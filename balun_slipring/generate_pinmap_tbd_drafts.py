"""Generate the two pre-pin-map KiCad 10 endpoint drafts.

The generated boards intentionally stop at the mapping boundary.  They are
layout-review artifacts, not fabrication outputs.  Re-run only while the
project is still in PINMAP-TBD state; once the pin map is known, edit the
KiCad projects normally and retire this generator.

Run this with KiCad's bundled Python, which provides the pcbnew module.  A
forced regeneration is permitted only while every existing board and
schematic still carries the DRAFT 0 / DO NOT FABRICATE markers.  Any saved
DRC/ERC report is removed after generation because it no longer describes the
new files; run kicad-cli again before trusting or committing fresh reports.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import textwrap
import uuid

import pcbnew


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SOURCE = REPO / "balun_eth_rj45"
SOURCE_SCH = SOURCE / "balun_eth_rj45.kicad_sch"
SOURCE_PRO = SOURCE / "balun_eth_rj45.kicad_pro"
KICAD_FP = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
KICAD_SYM = Path(r"C:\Program Files\KiCad\10.0\share\kicad\symbols")
COMMON_FP = HERE / "common.pretty"

DRAFT_REVISION_MARKER = '(rev "DRAFT 0")'
DRAFT_WARNING_MARKER = "DO NOT FABRICATE"

OLD_PROJECT = "balun_eth_rj45"
UUID_NAMESPACE = uuid.UUID("0d56d9bc-fc17-4b6b-a8b1-191592ab77c9")

VARIANTS = {
    "molex": {
        "directory": HERE / "molex_end",
        "project": "balun_slipring_molex",
        "connector_symbol": "Conn_01x04",
        "connector_value": "5055680471 / PINMAP TBD",
        "connector_footprint": "balun_slipring_common:Molex_5055680471",
        "connector_datasheet": (
            "https://www.molex.com/content/dam/molex/molex-dot-com/products/"
            "automated/en-us/2ddrawingdxfadobe2d/505/505568/"
            "5055680471.pdf?inline="
        ),
        "connector_manufacturer": "Molex",
        "connector_mpn": "5055680471",
        "raw_prefix": "MOL_RAW",
        "raw_count": 4,
        "connector_dnp": False,
        "board_label": "MOLEX END",
    },
    "m12": {
        "directory": HERE / "m12_end",
        "project": "balun_slipring_m12",
        "connector_symbol": "Conn_01x08",
        "connector_value": "M12 A-8 FEMALE / EXACT MPN TBD",
        "connector_footprint": "",
        "connector_datasheet": (
            "https://finecables.com/uploadfiles/2022/06/"
            "259%20M12%20A_coding%20Straight%20Connector%2C%20Panel%20Mount"
            "%2C%20PCB%20Type%2C%20Front%20fastened.pdf"
        ),
        "connector_manufacturer": "Finecables (candidate family)",
        "connector_mpn": "Female mate for MB12MBAFF08ST-0; suffix TBD",
        "raw_prefix": "M12_RAW",
        "raw_count": 8,
        "connector_dnp": True,
        "board_label": "M12 END",
    },
}


def stable_uuid(project: str, key: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, f"{project}:{key}"))


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def balanced_expression(text: str, start: int) -> tuple[str, int]:
    if text[start] != "(":
        raise ValueError("balanced_expression must start on '('")
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1], index + 1
    raise ValueError("unterminated S-expression")


def find_named_symbol(text: str, name: str) -> str:
    match = re.search(rf'\(symbol\s+"{re.escape(name)}"', text)
    if not match:
        raise RuntimeError(f"Could not find symbol definition {name}")
    return balanced_expression(text, match.start())[0]


def find_symbol_instances(schematic_text: str) -> dict[str, str]:
    lib_start = schematic_text.index("\t(lib_symbols")
    _, after_lib = balanced_expression(schematic_text, lib_start + 1)
    instances: dict[str, str] = {}
    cursor = after_lib
    marker = "\n\t(symbol\n"
    while True:
        found = schematic_text.find(marker, cursor)
        if found < 0:
            break
        start = found + 2
        block, cursor = balanced_expression(schematic_text, start)
        ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        if ref_match:
            instances[ref_match.group(1)] = block
    return instances


def indent_block(block: str, tabs: int) -> str:
    clean = textwrap.dedent(block).strip()
    prefix = "\t" * tabs
    return "\n".join(prefix + line if line else line for line in clean.splitlines())


def schematic_text_item(project: str, key: str, value: str, x: float, y: float,
                        size: float = 1.0, bold: bool = False) -> str:
    bold_line = "\n\t\t\t\t(bold yes)" if bold else ""
    return f'''\t(text "{value}"
\t\t(exclude_from_sim no)
\t\t(at {x:g} {y:g} 0)
\t\t(effects
\t\t\t(font
\t\t\t\t(size {size:g} {size:g}){bold_line}
\t\t\t)
\t\t)
\t\t(uuid "{stable_uuid(project, key)}")
\t)'''


def schematic_wire(project: str, key: str, x1: float, y1: float,
                   x2: float, y2: float) -> str:
    return f'''\t(wire
\t\t(pts
\t\t\t(xy {x1:g} {y1:g}) (xy {x2:g} {y2:g})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{stable_uuid(project, key)}")
\t)'''


def schematic_label(project: str, key: str, value: str, x: float, y: float,
                    angle: int = 0) -> str:
    return f'''\t(label "{value}"
\t\t(at {x:g} {y:g} {angle})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t)
\t\t)
\t\t(uuid "{stable_uuid(project, key)}")
\t)'''


def schematic_no_connect(project: str, key: str, x: float, y: float) -> str:
    return f'''\t(no_connect
\t\t(at {x:g} {y:g})
\t\t(uuid "{stable_uuid(project, key)}")
\t)'''


def connector_instance(config: dict[str, object], root_uuid: str) -> tuple[str, str]:
    project = str(config["project"])
    count = int(config["raw_count"])
    symbol_uuid = stable_uuid(project, "symbol:J1")
    pin_blocks = "\n".join(
        f'''\t\t(pin "{pin}"
\t\t\t(uuid "{stable_uuid(project, f"symbol:J1:pin:{pin}")}")
\t\t)'''
        for pin in range(1, count + 1)
    )
    dnp = "yes" if bool(config["connector_dnp"]) else "no"
    on_board = "no" if dnp == "yes" else "yes"
    in_pos_files = "no" if dnp == "yes" else "yes"
    assembly = (
        "TBD / DO NOT ORDER OR FABRICATE"
        if dnp == "yes"
        else "FOOTPRINT PLACED; SIGNAL PINMAP TBD / DO NOT FABRICATE"
    )
    block = f'''\t(symbol
\t\t(lib_id "Connector_Generic:{config['connector_symbol']}")
\t\t(at 55.88 90.17 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board {on_board})
\t\t(in_pos_files {in_pos_files})
\t\t(dnp {dnp})
\t\t(uuid "{symbol_uuid}")
\t\t(property "Reference" "J1"
\t\t\t(at 55.88 75 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "{config['connector_value']}"
\t\t\t(at 55.88 105 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "{config['connector_footprint']}"
\t\t\t(at 55.88 90.17 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "{config['connector_datasheet']}"
\t\t\t(at 55.88 90.17 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "Connector-side raw pins; intentionally isolated from balun pairs until continuity mapping is verified"
\t\t\t(at 55.88 90.17 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Manufacturer" "{config['connector_manufacturer']}"
\t\t\t(at 55.88 90.17 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "MPN" "{config['connector_mpn']}"
\t\t\t(at 55.88 90.17 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Assembly" "{assembly}"
\t\t\t(at 55.88 90.17 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
{pin_blocks}
\t\t(instances
\t\t\t(project "{project}"
\t\t\t\t(path "/{root_uuid}"
\t\t\t\t\t(reference "J1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''
    return block, symbol_uuid


def write_schematic(config: dict[str, object]) -> dict[str, str]:
    project = str(config["project"])
    output_dir = Path(config["directory"])
    source_text = SOURCE_SCH.read_text(encoding="utf-8")
    old_root = re.search(r'\(uuid\s+"([^"]+)"\)', source_text).group(1)
    root_uuid = stable_uuid(project, "root")

    embedded_names = [
        "Connector:Conn_Coaxial",
        "Device:R",
        "Transformer:ADT2-1T",
    ]
    embedded = [find_named_symbol(source_text, name) for name in embedded_names]
    generic_name = str(config["connector_symbol"])
    generic_source = (KICAD_SYM / "Connector_Generic.kicad_sym").read_text(
        encoding="utf-8"
    )
    generic = find_named_symbol(generic_source, generic_name)
    generic = generic.replace(
        f'(symbol "{generic_name}"',
        f'(symbol "Connector_Generic:{generic_name}"',
        1,
    )
    embedded.append(generic)

    source_instances = find_symbol_instances(source_text)
    retained_refs = ("J2", "J3", "T1", "T2", "RCT1", "RCT2")
    instances: list[str] = []
    symbol_uuids: dict[str, str] = {}
    for ref in retained_refs:
        block = source_instances[ref]
        block = block.replace(OLD_PROJECT, project)
        block = block.replace(old_root, root_uuid)
        if ref in ("J2", "J3"):
            block = re.sub(
                r'(\(property\s+"Assembly"\s+")[^"]*(")',
                r'\1DNP UNTIL STACK/CONNECTOR DECISION\2',
                block,
                count=1,
            )
        instances.append(indent_block(block, 1))
        symbol_uuids[ref] = re.search(r'\(uuid\s+"([^"]+)"\)', block).group(1)

    j1_block, j1_uuid = connector_instance(config, root_uuid)
    instances.append(j1_block)
    symbol_uuids["J1"] = j1_uuid

    drawing: list[str] = []
    drawing.extend([
        schematic_text_item(
            project, "text:warning",
            "PINMAP TBD - REVIEW ONLY - DO NOT FABRICATE",
            145, 25, 1.6, True,
        ),
        schematic_text_item(
            project, "text:scope",
            "Common SMA/balun core is fixed; connector RAW nets are deliberately isolated.",
            145, 31, 1.0, False,
        ),
        schematic_text_item(
            project, "text:map",
            "After continuity test: replace RAW-to-PAIR boundary with four short symmetric direct routes.",
            145, 35, 1.0, False,
        ),
        schematic_text_item(
            project, "text:loads",
            "Unused channel SMA requires an external 50 ohm termination during crosstalk tests.",
            145, 39, 1.0, False,
        ),
        schematic_text_item(project, "text:j2", "J2 / PAIR A", 82.5, 60, 1.0, True),
        schematic_text_item(project, "text:j3", "J3 / PAIR B", 82.5, 89, 1.0, True),
        schematic_text_item(project, "text:j1", "J1 / RAW PINS", 55, 70, 1.0, True),
    ])

    # Common RF core copied from the validated RJ45 fixture.  Transformer pin
    # 2 remains NC; the two secondary pins stop at named mapping-boundary nets.
    drawing.extend([
        schematic_wire(project, "wire:j2_t1", 87.63, 67.31, 111.76, 67.31),
        schematic_wire(project, "wire:t1_rct1", 121.92, 72.39, 143.51, 72.39),
        schematic_wire(project, "wire:j3_t2", 87.63, 96.52, 111.76, 96.52),
        schematic_wire(project, "wire:t2_rct2", 121.92, 101.6, 143.51, 101.6),
        schematic_label(project, "label:j2:gnd", "GND", 82.55, 62.23, 90),
        schematic_label(project, "label:j2:rf", "RF_A_50", 99.06, 67.31, 0),
        schematic_label(project, "label:t1:gnd", "GND", 111.76, 77.47, 0),
        schematic_label(project, "label:rct1:gnd", "GND", 135.89, 72.39, 180),
        schematic_label(project, "label:t1:n", "PAIR_A_N_TBD", 121.92, 67.31, 180),
        schematic_label(project, "label:t1:p", "PAIR_A_P_TBD", 121.92, 77.47, 180),
        schematic_label(project, "label:j3:gnd", "GND", 82.55, 91.44, 90),
        schematic_label(project, "label:j3:rf", "RF_B_50", 99.06, 96.52, 0),
        schematic_label(project, "label:t2:gnd", "GND", 111.76, 106.68, 0),
        schematic_label(project, "label:rct2:gnd", "GND", 135.89, 101.6, 180),
        schematic_label(project, "label:t2:n", "PAIR_B_N_TBD", 121.92, 96.52, 180),
        schematic_label(project, "label:t2:p", "PAIR_B_P_TBD", 121.92, 106.68, 180),
    ])

    if int(config["raw_count"]) == 4:
        pin_ys = (87.63, 90.17, 92.71, 95.25)
    else:
        pin_ys = (82.55, 85.09, 87.63, 90.17, 92.71, 95.25, 97.79, 100.33)
    for pin, y in enumerate(pin_ys, start=1):
        drawing.append(schematic_label(
            project,
            f"label:j1:{pin}",
            f"{config['raw_prefix']}{pin}",
            50.80,
            y,
            180,
        ))

    lib_text = "\n".join(indent_block(block, 2) for block in embedded)
    content = f'''(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{root_uuid}")
\t(paper "A4")
\t(title_block
\t\t(title "100BASE-TX slip-ring VNA fixture - {config['board_label']} - PINMAP TBD")
\t\t(date "2026-08-13")
\t\t(rev "DRAFT 0")
\t\t(comment 1 "Two-channel 50 ohm single-ended to 100 ohm differential fixture core.")
\t\t(comment 2 "Connector RAW pins intentionally not mapped to balun pairs.")
\t\t(comment 3 "REVIEW ONLY - DO NOT FABRICATE UNTIL PINMAP AND CONNECTOR MECHANICS ARE VERIFIED.")
\t)
\t(lib_symbols
{lib_text}
\t)
{chr(10).join(drawing)}
{chr(10).join(instances)}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
'''
    sch_path = output_dir / f"{project}.kicad_sch"
    sch_path.write_text(content, encoding="utf-8")
    return symbol_uuids


def recursively_replace(value: object, old: str, new: str) -> object:
    if isinstance(value, str):
        return value.replace(old, new)
    if isinstance(value, list):
        return [recursively_replace(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: recursively_replace(item, old, new) for key, item in value.items()}
    return value


def write_project(config: dict[str, object]) -> None:
    project = str(config["project"])
    output_dir = Path(config["directory"])
    data = json.loads(SOURCE_PRO.read_text(encoding="utf-8"))
    data = recursively_replace(data, OLD_PROJECT, project)
    design = data["board"]["design_settings"]
    design["diff_pair_dimensions"] = [
        {"gap": 0.22, "via_gap": 0.30, "width": 0.23}
    ]
    design["track_widths"] = [0.23, 0.35, 0.55, 0.80]
    net_settings = data["net_settings"]
    net_settings["netclass_patterns"] = [
        *(
            {"netclass": "ETH100", "pattern": f"/PAIR_{pair}_{pol}_TBD"}
            for pair in "AB" for pol in "PN"
        ),
        {"netclass": "RF50", "pattern": "/RF_A_50"},
        {"netclass": "RF50", "pattern": "/RF_B_50"},
    ]
    pro_path = output_dir / f"{project}.kicad_pro"
    pro_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fp_table = '''(fp_lib_table
  (lib (name "balun_slipring_common")(type "KiCad")(uri "${KIPRJMOD}/../common.pretty")(options "")(descr "Shared connector footprints for balun_slipring"))
)\n'''
    (output_dir / "fp-lib-table").write_text(fp_table, encoding="utf-8")

    dru = '''(version 1)

# PINMAP-TBD draft.  Geometry follows the same JLC04161H-7628 stack used by
# balun_eth_rj45 Rev B.  Connector-specific escape rules are intentionally
# absent until the exact pin map and M12 female footprint are fixed.

(rule "Controlled traces isolated from other controlled signals"
    (condition "(A.Type == 'Track' || A.Type == 'Via') && (B.Type == 'Track' || B.Type == 'Via') && (A.hasNetclass('ETH100') || A.hasNetclass('RF50')) && (B.hasNetclass('ETH100') || B.hasNetclass('RF50')) && !AB.isCoupledDiffPair() && !A.intersectsCourtyard('T?') && !B.intersectsCourtyard('T?')")
    (constraint clearance (min 0.60mm))
)

(rule "Copper to board edge"
    (constraint edge_clearance (min 0.30mm))
)

(rule "No routing on solid inner GND planes"
    (layer inner)
    (constraint disallow track)
)

(rule "Only GND zones on inner copper"
    (layer inner)
    (condition "A.Type == 'Zone' && A.NetName != '/GND'")
    (constraint disallow zone)
)

(rule "JLC 50 ohm outer geometry"
    (layer outer)
    # Short 0.55/0.80 mm flares inside the transformer/SMA courtyards match
    # their large pads.  The uniform line between those launch regions is
    # the controlled 0.35 mm section.
    (condition "A.Type == 'Track' && A.hasNetclass('RF50') && !A.intersectsCourtyard('J2') && !A.intersectsCourtyard('J3') && !A.intersectsCourtyard('T?')")
    (constraint track_width (min 0.34mm) (opt 0.35mm) (max 0.36mm))
)

(rule "JLC 100 ohm differential trace width"
    (layer outer)
    (condition "A.Type == 'Track' && A.hasNetclass('ETH100')")
    (constraint track_width (min 0.22mm) (opt 0.23mm) (max 0.24mm))
)

(rule "JLC 100 ohm differential coupled gap"
    (layer outer)
    (condition "A.Type == 'Track' && A.hasNetclass('ETH100') && !A.intersectsCourtyard('T?')")
    # The pair is allowed to open only in the short connector/transformer
    # fan-outs.  The uncoupled-length rule below bounds those exceptions.
    (constraint diff_pair_gap (min 0.21mm) (opt 0.22mm))
)

(rule "Ethernet pair topology"
    (condition "A.hasNetclass('ETH100')")
    (constraint skew (max 0.55mm) (within_diff_pairs))
    (constraint via_count (max 1))
    (constraint diff_pair_uncoupled (max 16.00mm))
)

(rule "SMA edge-launch exception"
    (condition "A.memberOfFootprint('J2') || A.memberOfFootprint('J3')")
    (constraint edge_clearance (min -0.10mm))
)
'''
    (output_dir / f"{project}.kicad_dru").write_text(dru, encoding="utf-8")


def load_footprint(board: pcbnew.BOARD, library: str, name: str,
                   reference: str, value: str, x: float, y: float,
                   rotation: float = 0, board_only: bool = False,
                   dnp: bool = False, symbol_uuid: str | None = None,
                   properties: dict[str, str] | None = None) -> pcbnew.FOOTPRINT:
    library_path = COMMON_FP if library == "balun_slipring_common" else KICAD_FP / f"{library}.pretty"
    footprint = pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(str(library_path), name, False)
    if footprint is None:
        raise RuntimeError(f"Could not load {library}:{name}")
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetFPIDAsString(f"{library}:{name}")
    footprint.SetPosition(point(x, y))
    footprint.SetOrientationDegrees(rotation)
    if symbol_uuid:
        footprint.SetPath(pcbnew.KIID_PATH("/" + symbol_uuid))
    for field_name, field_value in (properties or {}).items():
        footprint.SetField(field_name, field_value)
        footprint.GetField(field_name).SetVisible(False)
    if board_only:
        footprint.SetBoardOnly(True)
        footprint.SetAttributes(
            footprint.GetAttributes()
            | pcbnew.FP_BOARD_ONLY
            | pcbnew.FP_EXCLUDE_FROM_BOM
            | pcbnew.FP_EXCLUDE_FROM_POS_FILES
        )
    if dnp:
        footprint.SetDNP(True)
        footprint.SetAttributes(footprint.GetAttributes() | pcbnew.FP_DNP)
    board.Add(footprint)
    return footprint


def add_segment(board: pcbnew.BOARD, nets: dict[str, pcbnew.NETINFO_ITEM],
                start: tuple[float, float], end: tuple[float, float],
                width: float, layer: int, net_name: str) -> pcbnew.PCB_TRACK:
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(*start))
    track.SetEnd(point(*end))
    track.SetWidth(mm(width))
    track.SetLayer(layer)
    track.SetNet(nets[net_name])
    board.Add(track)
    return track


def add_polyline(board: pcbnew.BOARD, nets: dict[str, pcbnew.NETINFO_ITEM],
                 vertices: list[tuple[float, float]], width: float,
                 layer: int, net_name: str) -> None:
    for start, end in zip(vertices, vertices[1:]):
        add_segment(board, nets, start, end, width, layer, net_name)


def add_via(board: pcbnew.BOARD, nets: dict[str, pcbnew.NETINFO_ITEM],
            x: float, y: float, net_name: str,
            diameter: float = 0.60, drill: float = 0.30) -> pcbnew.PCB_VIA:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(x, y))
    via.SetWidth(mm(diameter))
    via.SetDrill(mm(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(nets[net_name])
    board.Add(via)
    return via


def add_line(board: pcbnew.BOARD, start: tuple[float, float],
             end: tuple[float, float], layer: int = pcbnew.Edge_Cuts,
             width: float = 0.05) -> pcbnew.PCB_SHAPE:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetStart(point(*start))
    shape.SetEnd(point(*end))
    shape.SetLayer(layer)
    shape.SetWidth(mm(width))
    board.Add(shape)
    return shape


def add_circle(board: pcbnew.BOARD, center: tuple[float, float], radius: float,
               layer: int, width: float = 0.2) -> pcbnew.PCB_SHAPE:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_CIRCLE)
    shape.SetCenter(point(*center))
    shape.SetEnd(point(center[0] + radius, center[1]))
    shape.SetLayer(layer)
    shape.SetWidth(mm(width))
    board.Add(shape)
    return shape


def add_board_text(board: pcbnew.BOARD, value: str, x: float, y: float,
                   layer: int = pcbnew.F_SilkS, size: float = 1.0,
                   thickness: float = 0.16, angle: float = 0) -> pcbnew.PCB_TEXT:
    text = pcbnew.PCB_TEXT(board)
    text.SetText(value)
    text.SetPosition(point(x, y))
    text.SetLayer(layer)
    text.SetTextSize(point(size, size))
    text.SetTextThickness(mm(thickness))
    text.SetTextAngleDegrees(angle)
    if layer in (pcbnew.B_SilkS, pcbnew.B_Fab):
        text.SetMirrored(True)
    board.Add(text)
    return text


def add_ground_zone(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM,
                    layer: int) -> pcbnew.ZONE:
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(net)
    zone.SetLocalClearance(mm(0.25))
    zone.SetMinThickness(mm(0.20))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    zone.SetMinIslandArea(mm(2.0) * mm(2.0))
    vertices = [
        (22.1, 20.3), (85.9, 20.3), (87.7, 22.1), (87.7, 61.9),
        (85.9, 63.7), (22.1, 63.7), (20.3, 61.9), (20.3, 22.1),
    ]
    for x, y in vertices:
        zone.AppendCorner(point(x, y), -1)
    board.Add(zone)
    return zone


STACKUP = '''\t\t(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen") (color "White"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "prepreg") (thickness 0.2104)
\t\t\t\t(material "Nan Ya NP-155F") (epsilon_r 4.4) (loss_tangent 0.02))
\t\t\t(layer "In1.Cu" (type "copper") (thickness 0.0152))
\t\t\t(layer "dielectric 2" (type "core") (thickness 1.065)
\t\t\t\t(material "Nan Ya NP-155F") (epsilon_r 4.38) (loss_tangent 0.02))
\t\t\t(layer "In2.Cu" (type "copper") (thickness 0.0152))
\t\t\t(layer "dielectric 3" (type "prepreg") (thickness 0.2104)
\t\t\t\t(material "Nan Ya NP-155F") (epsilon_r 4.4) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
\t\t\t(copper_finish "ENIG")
\t\t\t(dielectric_constraints yes)
\t\t)
'''


def write_board(config: dict[str, object], symbol_uuids: dict[str, str]) -> None:
    project = str(config["project"])
    output_dir = Path(config["directory"])
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    board.GetDesignSettings().SetBoardThickness(mm(1.5862))
    settings = board.GetDesignSettings()
    settings.m_MinClearance = mm(0.20)
    settings.m_TrackMinWidth = mm(0.20)
    settings.m_ViasMinSize = mm(0.60)
    settings.m_MinThroughDrill = mm(0.30)
    settings.m_ViasMinAnnularWidth = mm(0.15)
    settings.m_HoleToHoleMin = mm(0.25)
    settings.m_CopperEdgeClearance = mm(0.00)

    title = board.GetTitleBlock()
    title.SetTitle(f"100BASE-TX slip-ring VNA fixture - {config['board_label']} - PINMAP TBD")
    title.SetRevision("DRAFT 0")
    title.SetDate("2026-08-13")
    title.SetComment(0, "Common 2-channel RF core only; connector mapping is intentionally open.")
    title.SetComment(1, "REVIEW ONLY - DO NOT FABRICATE.")
    title.SetComment(2, "JLC04161H-7628: 50R W0.35; future 100R W0.23/G0.22; L2/L3 GND.")

    net_names = [
        "/GND",
        "/PAIR_A_P_TBD", "/PAIR_A_N_TBD",
        "/PAIR_B_P_TBD", "/PAIR_B_N_TBD",
        "/RF_A_50", "/RF_B_50",
        "Net-(RCT1-Pad2)", "Net-(RCT2-Pad2)",
        "unconnected-(T1-Pad2)", "unconnected-(T2-Pad2)",
    ]
    if config["raw_prefix"] == "MOL_RAW":
        net_names.extend(f"/MOL_RAW{pin}" for pin in range(1, 5))
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for net_name in net_names:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
        nets[net_name] = net

    footprints: dict[str, pcbnew.FOOTPRINT] = {}
    channels = (("A", "J2", "T1", "RCT1", 31.0), ("B", "J3", "T2", "RCT2", 53.0))
    for label, jref, tref, rref, y in channels:
        footprints[jref] = load_footprint(
            board, "Connector_Coaxial", "SMA_Amphenol_132289_EdgeMount",
            jref, f"SMA_{label}", 85.45, y,
            symbol_uuid=symbol_uuids[jref],
            properties={
                "Manufacturer": "Amphenol RF", "MPN": "132289",
                "Assembly": "DNP UNTIL STACK/CONNECTOR DECISION",
                "Datasheet": "https://www.amphenolrf.com/132289.html",
            },
        )
        footprints[tref] = load_footprint(
            board, "RF_Mini-Circuits", "Mini-Circuits_CD542_H2.84mm",
            tref, "ADT2-1T+", 57.50, y, 180,
            symbol_uuid=symbol_uuids[tref],
            properties={
                "Manufacturer": "Mini-Circuits", "MPN": "ADT2-1T+", "Assembly": "FIT",
                "Datasheet": "https://www.minicircuits.com/pdfs/ADT2-1T+.pdf",
            },
        )
        footprints[rref] = load_footprint(
            board, "Resistor_SMD", "R_0805_2012Metric_Pad1.20x1.40mm_HandSolder",
            rref, "0R", 50.80, y,
            symbol_uuid=symbol_uuids[rref],
            properties={
                "Manufacturer": "ANY", "MPN": "0 ohm 0805",
                "Assembly": "FIT; remove for floating-CT comparison",
            },
        )

    if config["raw_prefix"] == "MOL_RAW":
        footprints["J1"] = load_footprint(
            board, "balun_slipring_common", "Molex_5055680471",
            "J1", "5055680471 / PINMAP TBD", 29.0, 42.0, 90,
            symbol_uuid=symbol_uuids["J1"],
            properties={
                "Manufacturer": "Molex", "MPN": "5055680471",
                "Assembly": "FOOTPRINT PLACED; SIGNAL PINMAP TBD / DO NOT FABRICATE",
                "Datasheet": str(config["connector_datasheet"]),
                "Description": "Connector-side raw pins; intentionally isolated from balun pairs until continuity mapping is verified",
            },
        )

    for index, (x, y) in enumerate(((25, 25), (25, 59), (74, 25), (74, 59)), start=1):
        reference = f"H{index}"
        footprints[reference] = load_footprint(
            board, "MountingHole", "MountingHole_3.2mm_M3",
            reference, "M3 / PROVISIONAL", x, y, board_only=True,
        )
        footprints[reference].Reference().SetVisible(False)

    connections: dict[str, tuple[tuple[str, str], ...]] = {
        "/GND": (
            ("J2", "2"), ("J3", "2"),
            ("T1", "1"), ("T2", "1"),
            ("RCT1", "1"), ("RCT2", "1"),
        ),
        "/PAIR_A_P_TBD": (("T1", "4"),),
        "/PAIR_A_N_TBD": (("T1", "6"),),
        "/PAIR_B_P_TBD": (("T2", "4"),),
        "/PAIR_B_N_TBD": (("T2", "6"),),
        "/RF_A_50": (("J2", "1"), ("T1", "3")),
        "/RF_B_50": (("J3", "1"), ("T2", "3")),
        "Net-(RCT1-Pad2)": (("RCT1", "2"), ("T1", "5")),
        "Net-(RCT2-Pad2)": (("RCT2", "2"), ("T2", "5")),
        "unconnected-(T1-Pad2)": (("T1", "2"),),
        "unconnected-(T2-Pad2)": (("T2", "2"),),
    }
    if "J1" in footprints:
        for pin in range(1, 5):
            connections[f"/MOL_RAW{pin}"] = (("J1", str(pin)),)

    for net_name, nodes in connections.items():
        for reference, pad_number in nodes:
            pads = [pad for pad in footprints[reference].Pads() if pad.GetNumber() == pad_number]
            if not pads:
                raise RuntimeError(f"Missing pad {reference}.{pad_number}")
            for pad in pads:
                pad.SetNet(nets[net_name])

    outline = [
        (22, 20), (86, 20), (88, 22), (88, 62),
        (86, 64), (22, 64), (20, 62), (20, 22), (22, 20),
    ]
    for start, end in zip(outline, outline[1:]):
        add_line(board, start, end)

    # The only controlled routes committed before pin mapping are the two
    # identical 50-ohm single-ended paths.  Differential pads stop at T1/T2.
    for _label, jref, _tref, rref, y in channels:
        input_net = f"/RF_{label}_50"
        add_segment(board, nets, (85.45, y), (83.40, y), 0.80, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (83.40, y), (82.00, y), 0.55, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (82.00, y), (79.46, y - 2.54), 0.35, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (79.46, y - 2.54), (61.54, y - 2.54), 0.35, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (61.54, y - 2.54), (60.04, y - 2.54), 0.55, pcbnew.F_Cu, input_net)

        ct_net = f"Net-({rref}-Pad2)"
        add_segment(board, nets, (54.96, y), (51.80, y), 0.30, pcbnew.F_Cu, ct_net)
        add_segment(board, nets, (49.80, y), (48.30, y), 0.50, pcbnew.F_Cu, "/GND")
        add_via(board, nets, 48.30, y, "/GND")

        add_segment(board, nets, (60.04, y + 2.54), (62.00, y + 2.54), 0.80, pcbnew.F_Cu, "/GND")
        add_via(board, nets, 62.00, y + 2.54, "/GND")
        add_via(board, nets, 60.04, y + 4.35, "/GND")

        for sy in (y - 4.25, y + 4.25):
            add_segment(board, nets, (85.45, sy), (83.70, sy), 0.80, pcbnew.F_Cu, "/GND")
            add_via(board, nets, 83.70, sy, "/GND")
            add_via(board, nets, 81.90, sy, "/GND")

    # Ground stitching only; there are deliberately no F/B blanket pours.
    stitch_points = [
        (34, 23.0), (42, 23.0), (50, 23.0), (58, 23.0), (66, 23.0), (78, 23.0),
        (34, 59.5), (42, 59.5), (50, 59.5), (58, 59.5), (66, 59.5), (78, 59.5),
        (22.5, 33), (22.5, 42), (22.5, 51),
        (71, 42), (76, 42), (81, 42),
    ]
    for x, y in stitch_points:
        add_via(board, nets, x, y, "/GND")

    for layer in (pcbnew.In1_Cu, pcbnew.In2_Cu):
        add_ground_zone(board, nets["/GND"], layer)

    add_board_text(board, f"SLIPRING {config['board_label']} / PINMAP TBD", 54, 22.1, size=1.05, thickness=0.18)
    add_board_text(board, "DRAFT - DO NOT FAB", 53, 62.0, size=1.05, thickness=0.18)
    add_board_text(board, "A", 78.5, 33.8, size=1.0, thickness=0.16)
    add_board_text(board, "B", 78.5, 55.8, size=1.0, thickness=0.16)
    add_board_text(board, "UNUSED SMA -> 50R", 71.5, 62.0, pcbnew.B_SilkS, 0.8, 0.13)
    add_board_text(board, "PINMAP TBD", 43.5, 42.0, pcbnew.Cmts_User, 1.2, 0.18, 90)
    add_board_text(board, "NO ROUTING IN THIS GAP UNTIL CONTINUITY MAP IS VERIFIED", 45.5, 66.5, pcbnew.Cmts_User, 0.9, 0.14)

    # Mapping boundary / connector-mechanics reservation on user layers.
    for start, end in zip(
        ((36, 24), (53.5, 24), (53.5, 60), (36, 60)),
        ((53.5, 24), (53.5, 60), (36, 60), (36, 24)),
    ):
        add_line(board, start, end, pcbnew.Cmts_User, 0.15)

    if "J1" in footprints:
        add_board_text(board, "J1 PIN 1", 29.0, 35.5, size=0.80, thickness=0.13)
        add_board_text(board, "5055680471", 29.0, 49.0, size=0.80, thickness=0.13)
    else:
        add_circle(board, (29.0, 42.0), 8.5, pcbnew.F_SilkS, 0.2)
        add_board_text(board, "M12 AREA TBD", 29.0, 42.0, size=0.80, thickness=0.13)
        add_circle(board, (29.0, 42.0), 11.5, pcbnew.Cmts_User, 0.2)
        add_circle(board, (29.0, 42.0), 8.0, pcbnew.Cmts_User, 0.15)
        add_board_text(board, "M12 FEMALE", 29.0, 39.8, pcbnew.Cmts_User, 0.9, 0.14)
        add_board_text(board, "FOOTPRINT TBD", 29.0, 42.2, pcbnew.Cmts_User, 0.9, 0.14)
        add_board_text(board, "MECHANICS TBD", 29.0, 44.6, pcbnew.Cmts_User, 0.9, 0.14)

    reference_positions = {
        "J2": (80.0, 24.2, 0), "J3": (80.0, 46.2, 0),
        "T1": (57.5, 25.5, 0), "T2": (57.5, 47.5, 0),
        "RCT1": (49.8, 34.0, 0), "RCT2": (49.8, 56.0, 0),
        "J1": (29.0, 33.5, 0),
    }
    for reference, (x, y, angle) in reference_positions.items():
        if reference not in footprints:
            continue
        ref_text = footprints[reference].Reference()
        ref_text.SetPosition(point(x, y))
        ref_text.SetTextAngleDegrees(angle)
        ref_text.SetTextSize(point(0.85, 0.85))
        ref_text.SetTextThickness(mm(0.14))

    # Zone filling through the Windows pcbnew Python binding is unstable in
    # KiCad 10.0.0.  Save the geometry here; verification uses kicad-cli
    # --refill-zones, which runs the native board engine out of process.
    output = output_dir / f"{project}.kicad_pcb"
    pcbnew.SaveBoard(str(output), board)

    board_text = output.read_text(encoding="utf-8")
    setup_marker = "\t(setup\n"
    if setup_marker not in board_text:
        raise RuntimeError("Could not locate setup block for stack-up insertion")
    board_text = board_text.replace(setup_marker, setup_marker + STACKUP, 1)
    output.write_text(board_text, encoding="utf-8")


def verify_overwrite_policy(force: bool) -> None:
    outputs: list[Path] = []
    for config in VARIANTS.values():
        directory = Path(config["directory"])
        project = str(config["project"])
        outputs.extend(directory / f"{project}.{suffix}" for suffix in ("kicad_sch", "kicad_pcb", "kicad_pro", "kicad_dru"))
    existing = [path for path in outputs if path.exists()]
    if existing and not force:
        formatted = "\n".join(f"  {path.relative_to(HERE)}" for path in existing)
        raise SystemExit(
            "REFUSED: draft outputs already exist.  This generator can overwrite manual edits.\n"
            f"{formatted}\n"
            "Use --force only while intentionally regenerating the PINMAP-TBD drafts."
        )

    if force:
        protected = []
        for path in existing:
            if path.suffix not in (".kicad_sch", ".kicad_pcb"):
                continue
            content = path.read_text(encoding="utf-8")
            if (
                DRAFT_REVISION_MARKER not in content
                or DRAFT_WARNING_MARKER not in content
            ):
                protected.append(path)
        if protected:
            formatted = "\n".join(f"  {path.relative_to(HERE)}" for path in protected)
            raise SystemExit(
                "REFUSED: at least one design no longer has both DRAFT 0 and "
                "DO NOT FABRICATE markers.\n"
                f"{formatted}\n"
                "The project may contain manual post-pin-map work; retire this generator."
            )


def invalidate_reports(config: dict[str, object]) -> None:
    directory = Path(config["directory"])
    project = str(config["project"])
    for report_type in ("drc", "erc"):
        report = directory / f"{project}_{report_type}.rpt"
        if report.exists():
            report.unlink()
            print(f"Removed stale verification report {report.relative_to(HERE)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing draft outputs")
    args = parser.parse_args()
    verify_overwrite_policy(args.force)
    for config in VARIANTS.values():
        Path(config["directory"]).mkdir(parents=True, exist_ok=True)
        symbol_uuids = write_schematic(config)
        write_board(config, symbol_uuids)
        # pcbnew.SaveBoard creates a minimal sibling .kicad_pro on Windows.
        # Restore the intended impedance/netclass settings after board save.
        write_project(config)
        invalidate_reports(config)
        print(f"Generated {config['project']} in {Path(config['directory']).relative_to(HERE)}")


if __name__ == "__main__":
    main()
