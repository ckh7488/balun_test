"""Generate the two document-mapped KiCad 10 endpoint drafts.

The electrical mapping comes from slide 14 of ``Docs/[인수인계] PALA720.pptx``.
The generated boards include the fixed 100BASE-TX fan-outs and the selected
1.6 mm MyAntenna edge-launch SMA, but remain review artifacts rather than
fabrication outputs until the endpoint connector mechanics are verified.

Run this with KiCad's bundled Python, which provides the pcbnew module.  A
forced regeneration is permitted only while every existing board and
schematic still carries a recognized draft revision / DO NOT FABRICATE marker.
Each selected variant is built in a sibling staging directory before any live
design file is replaced.  Saved DRC/ERC reports are then removed because they
no longer describe the new files; run kicad-cli again before trusting or
committing fresh reports.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
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
KICAD_CLI = Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe")
COMMON_FP = HERE / "common.pretty"

DRAFT_REVISION_MARKERS = ('(rev "DRAFT 0")', '(rev "DRAFT 1")')
DRAFT_WARNING_MARKER = "DO NOT FABRICATE"

OLD_PROJECT = "balun_eth_rj45"
UUID_NAMESPACE = uuid.UUID("0d56d9bc-fc17-4b6b-a8b1-191592ab77c9")

VARIANTS = {
    "molex": {
        "directory": HERE / "molex_end",
        "project": "balun_slipring_molex",
        "connector_symbol": "Conn_01x05",
        "connector_value": "5055680571 / 505565 SERIES MATE CAND",
        "connector_footprint": "balun_slipring_common:Molex_5055680571",
        "connector_datasheet": (
            "https://www.molex.com/en-us/products/part-detail/5055680571"
        ),
        "connector_manufacturer": "Molex",
        "connector_mpn": "5055680571",
        "connector_lcsc": "C585386",
        "pin_nets": {
            1: "PAIR_TX_P",
            2: "PAIR_TX_N",
            3: "PAIR_RX_P",
            4: "PAIR_RX_N",
            5: None,
        },
        "connector_dnp": True,
        "assembly": (
            "DNP UNTIL PHYSICAL MATING, KEY/PIN-1 ORIENTATION AND LAND PATTERN "
            "ARE VERIFIED AGAINST REV-504"
        ),
        "connector_description": (
            "Five-circuit PCB-side candidate for the 5055650501 cable housing; "
            "the housing identity is a cross-slide inference and circuit 5 is NC"
        ),
        "connector_position": (29.0, 42.0, 90.0),
        "connector_flipped": False,
        "board_label": "MOLEX END",
    },
    "m12": {
        "directory": HERE / "m12_end",
        "project": "balun_slipring_m12",
        "connector_symbol": "Conn_01x08",
        "connector_value": "MB12FBAFF08ST-3 / VERIFY MECHANICS",
        "connector_footprint": "balun_slipring_common:Finecables_MB12FBAFF08ST-3",
        "connector_datasheet": (
            "https://finecables.com/uploadfiles/2022/06/"
            "259%20M12%20A_coding%20Straight%20Connector%2C%20Panel%20Mount"
            "%2C%20PCB%20Type%2C%20Front%20fastened.pdf"
        ),
        "connector_manufacturer": "Finecables",
        "connector_mpn": "MB12FBAFF08ST-3 (candidate; verify mechanics)",
        "connector_lcsc": "C22378785",
        "pin_nets": {
            1: "PAIR_RX_N",
            2: "PAIR_RX_P",
            3: "PAIR_TX_N",
            4: "PAIR_TX_P",
            5: None,
            6: None,
            7: None,
            8: None,
        },
        "connector_dnp": True,
        "assembly": (
            "PCB B-SIDE ELECTRICAL CANDIDATE; DNP UNTIL MATING, KEY/PIN-1, "
            "FRONT-FASTENED PANEL SUPPORT AND AVAILABILITY ARE VERIFIED"
        ),
        "connector_description": (
            "M12 A-coded eight-pin female candidate using the manufacturer "
            "female PCB layout; pins 1-4 are mapped from the handoff document "
            "and pins 5-8 are intentionally NC"
        ),
        # Back-side mounting puts the four Ethernet pads toward the baluns,
        # so both members of both pairs can remain on F.Cu with zero vias.
        # This is an electrical-layout candidate only: the real A-key,
        # mating-face pin view and panel access remain fabrication blockers.
        "connector_position": (30.0, 42.0, 225.0),
        "connector_flipped": True,
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
    count = len(config["pin_nets"])
    symbol_uuid = stable_uuid(project, "symbol:J1")
    pin_blocks = "\n".join(
        f'''\t\t(pin "{pin}"
\t\t\t(uuid "{stable_uuid(project, f"symbol:J1:pin:{pin}")}")
\t\t)'''
        for pin in range(1, count + 1)
    )
    dnp = "yes" if bool(config["connector_dnp"]) else "no"
    # Keep a DNP candidate on the PCB so parity and the document-mapped escape
    # routing can still be checked before its mechanical/procurement release.
    on_board = "yes"
    in_pos_files = "no" if dnp == "yes" else "yes"
    assembly = str(config["assembly"])
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
\t\t(property "Description" "{config['connector_description']}"
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
\t\t(property "LCSC Part #" "{config['connector_lcsc']}"
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
        # Source RJ45 symbols may have been moved for documentation.  The RF
        # core's construction coordinates/orientations must not depend on that
        # presentation; the endpoint-specific layout is applied after wiring.
        construction_at = {
            "J2": "82.55 67.31 180", "J3": "82.55 96.52 180",
            "T1": "116.84 72.39 0", "T2": "116.84 101.6 0",
            "RCT1": "139.7 72.39 90", "RCT2": "139.7 101.6 90",
        }[ref]
        block = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)', f"(at {construction_at})", block, count=1)
        block = block.replace(OLD_PROJECT, project)
        block = block.replace(old_root, root_uuid)
        if ref in ("J2", "J3"):
            replacements = {
                "Footprint": "balun_slipring_common:SMA_MyAntenna_A-SMA-KE-16.5A_EdgeMount",
                "Datasheet": "https://datasheet.lcsc.com/datasheet/pdf/92633ab2cf30de4413e1a152c04a3ed5.pdf?productCode=C22467617",
                "Manufacturer": "MyAntenna",
                "MPN": "A-SMA-KE-16.5A",
                "Assembly": "FIT; JLC C22467617; Standard PCBA / wave-solder review",
            }
            for field, value in replacements.items():
                block, count = re.subn(
                    rf'(\(property\s+"{field}"\s+")[^"]*(")',
                    rf'\g<1>{value}\g<2>', block, count=1,
                )
                if count != 1:
                    raise RuntimeError(f"Could not update {ref} {field}")
            lcsc_property = '''\t\t(property "LCSC Part #" "C22467617"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)'''
            if '(property "LCSC Part #"' not in block:
                block = block.replace('\t\t(pin "1"', lcsc_property + '\n\t\t(pin "1"', 1)
        elif ref in ("RCT1", "RCT2"):
            # The balanced winding is floating by default.  Keep the 0-ohm
            # link as an explicit all-four-links CT-GND comparison option.
            block, assembly_count = re.subn(
                r'(\(property\s+"Assembly"\s+")[^"]*(")',
                lambda m: m.group(1) + str(config.get(
                    "rct_assembly", "DNP; fit all four RCTs only for controlled CT-GND comparison"
                )) + m.group(2),
                block,
                count=1,
            )
            if assembly_count != 1:
                raise RuntimeError(f"Could not set {ref} DNP assembly property")
            block, position_count = re.subn(
                r'\(in_pos_files (?:yes|no)\)', "(in_pos_files no)", block, count=1
            )
            block, dnp_count = re.subn(
                r'\(dnp (?:yes|no)\)', "(dnp yes)", block, count=1
            )
            if position_count != 1 or dnp_count != 1:
                raise RuntimeError(f"Could not set {ref} native DNP flags")
            for field, value in {
                "Manufacturer": "UNI-ROYAL",
                "MPN": "0805W8F0000T5E",
            }.items():
                block, count = re.subn(
                    rf'(\(property\s+"{field}"\s+")[^"]*(")',
                    rf'\g<1>{value}\g<2>', block, count=1,
                )
                if count != 1:
                    raise RuntimeError(f"Could not update {ref} {field}")

        lcsc_code = {
            "J2": "C22467617", "J3": "C22467617",
            "T1": "C5223988", "T2": "C5223988",
            "RCT1": "C17477", "RCT2": "C17477",
        }[ref]
        lcsc_pattern = r'(\(property\s+"LCSC Part #"\s+")[^"]*(")'
        if re.search(lcsc_pattern, block):
            block = re.sub(
                lcsc_pattern, rf'\g<1>{lcsc_code}\g<2>', block, count=1
            )
        else:
            lcsc_property = f'''\t\t(property "LCSC Part #" "{lcsc_code}"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)'''
            block = block.replace(
                '\t\t(pin "1"', lcsc_property + '\n\t\t(pin "1"', 1
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
            "DOC PINMAP APPLIED - REVIEW ONLY - DO NOT FABRICATE",
            145, 25, 1.6, True,
        ),
        schematic_text_item(
            project, "text:scope",
            str(config.get("scope_note", "PALA720 slide 14: Molex 1/2 = TX+/-; 3/4 = RX+/-. M12 4/3 = TX+/-; 2/1 = RX+/-.")),
            145, 31, 1.0, False,
        ),
        schematic_text_item(
            project, "text:map",
            str(config.get("power_note", "M12 5 GPS_RX, 6 GPS_1PPS, 7 +24V and 8 24V_GND are intentionally NC on this fixture.")),
            145, 35, 1.0, False,
        ),
        schematic_text_item(
            project, "text:loads",
            str(config.get("loads_note", "Unused channel SMA requires an external 50 ohm termination during crosstalk tests.")),
            145, 39, 1.0, False,
        ),
        schematic_text_item(project, "text:j2", "J2 / TX PAIR", 82.5, 60, 1.0, True),
        schematic_text_item(project, "text:j3", "J3 / RX PAIR", 82.5, 89, 1.0, True),
        schematic_text_item(project, "text:j1", "J1 / DOC-MAPPED PINS", 55, 70, 1.0, True),
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
        schematic_label(project, "label:t1:n", "PAIR_TX_N", 121.92, 67.31, 180),
        schematic_label(project, "label:t1:p", "PAIR_TX_P", 121.92, 77.47, 180),
        schematic_label(project, "label:j3:gnd", "GND", 82.55, 91.44, 90),
        schematic_label(project, "label:j3:rf", "RF_B_50", 99.06, 96.52, 0),
        schematic_label(project, "label:t2:gnd", "GND", 111.76, 106.68, 0),
        schematic_label(project, "label:rct2:gnd", "GND", 135.89, 101.6, 180),
        schematic_label(project, "label:t2:n", "PAIR_RX_N", 121.92, 96.52, 180),
        schematic_label(project, "label:t2:p", "PAIR_RX_P", 121.92, 106.68, 180),
    ])

    count = len(config["pin_nets"])
    if count == 5:
        pin_ys = (85.09, 87.63, 90.17, 92.71, 95.25)
    elif count == 8:
        pin_ys = (82.55, 85.09, 87.63, 90.17, 92.71, 95.25, 97.79, 100.33)
    else:
        raise ValueError(f"Unsupported connector pin count: {count}")
    for pin, y in enumerate(pin_ys, start=1):
        net_name = config["pin_nets"][pin]
        if net_name is None:
            drawing.append(schematic_no_connect(
                project, f"no_connect:j1:{pin}", 50.80, y
            ))
        else:
            drawing.append(schematic_label(
                project, f"label:j1:{pin}", str(net_name), 50.80, y, 180
            ))

    if count == 5:
        drawing.append(schematic_text_item(
            project, "text:j1-unused", "J1.5 = NC (unused housing circuit)",
            34, 104, 0.9, False,
        ))
    else:
        drawing.append(schematic_text_item(
            project, "text:j1-unused",
            str(config.get("unused_pins_note", "J1.5 GPS_RX / 6 GPS_1PPS / 7 +24V / 8 24V_GND: ALL NC ON FIXTURE")),
            38, 107, 0.9, True,
        ))

    lib_text = "\n".join(indent_block(block, 2) for block in embedded)
    content = f'''(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{root_uuid}")
\t(paper "A4")
\t(title_block
\t\t(title "{config.get('schematic_title', f'100BASE-TX slip-ring VNA fixture - {config["board_label"]} - DOC PINMAP')}")
\t\t(date "{config.get('schematic_date', '2026-08-31')}")
\t\t(rev "DRAFT 1")
\t\t(comment 1 "{config.get('core_note', 'Two-channel 50 ohm single-ended to 100 ohm differential fixture core.')}")
\t\t(comment 2 "{config.get('source_note', 'Electrical map from PALA720 slide 14; TX and RX fan-outs are connected.')}")
\t\t(comment 3 "{config.get('release_note', 'REVIEW ONLY - DO NOT FABRICATE UNTIL CONTINUITY AND ENDPOINT CONNECTOR MECHANICS ARE VERIFIED.')}")
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
    readable_variant = {
        "balun_slipring_molex": "molex", "balun_slipring_m12": "m12",
    }.get(project)
    if readable_variant:
        from readable_schematic import render_schematic
        content = render_schematic(content, readable_variant)
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
            {"netclass": "ETH100", "pattern": f"/PAIR_{pair}_{pol}"}
            for pair in ("TX", "RX") for pol in "PN"
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

# Document-mapped DRAFT 1.  Electrical connectivity follows PALA720 slide 14.
# Geometry follows the same JLC04161H-7628 stack used by the balun_eth_rj45
# reference.  The selected C22467617 SMA accepts 1.6+/-0.05 mm PCB; endpoint
# connector mechanics remain fabrication blockers.

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
    # The short 0.55 mm transformer-side signal flare matches the large RF
    # pad.  Separate 0.80 mm tracks at the transformer are GND launches, not
    # RF50 flares.  The uniform RF line outside the launch courtyard is the
    # controlled 0.35 mm section.
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
    (condition "A.Type == 'Track' && A.hasNetclass('ETH100') && !A.intersectsCourtyard('T?') && !A.intersectsCourtyard('J1')")
    # The pair is allowed to open only in the short connector/transformer
    # fan-outs.  The uncoupled-length rule below bounds those exceptions.
    (constraint diff_pair_gap (min 0.21mm) (opt 0.22mm) (max 0.23mm))
)

(rule "Ethernet pair topology"
    (condition "A.hasNetclass('ETH100')")
    (constraint skew (max 0.10mm) (within_diff_pairs))
    (constraint via_count (max 0))
    (constraint diff_pair_uncoupled (max 11.20mm))
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
                   dnp: bool = False, flipped: bool = False,
                   symbol_uuid: str | None = None,
                   properties: dict[str, str] | None = None) -> pcbnew.FOOTPRINT:
    library_path = COMMON_FP if library == "balun_slipring_common" else KICAD_FP / f"{library}.pretty"
    footprint = pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(str(library_path), name, False)
    if footprint is None:
        raise RuntimeError(f"Could not load {library}:{name}")
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetFPIDAsString(f"{library}:{name}")
    footprint.SetPosition(point(x, y))
    if not flipped:
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
        footprint.SetAttributes(
            footprint.GetAttributes()
            | pcbnew.FP_DNP
            | pcbnew.FP_EXCLUDE_FROM_POS_FILES
        )
    board.Add(footprint)
    if flipped:
        footprint.Flip(footprint.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        footprint.SetOrientationDegrees(rotation)
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


def path_length(vertices: list[tuple[float, float]]) -> float:
    return sum(math.dist(start, end) for start, end in zip(vertices, vertices[1:]))


def offset_polyline(
    centerline: list[tuple[float, float]], side: float,
    distance: float = 0.225,
) -> list[tuple[float, float]]:
    """Miter-offset a shared centerline to preserve 0.45 mm pair spacing."""
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for start, end in zip(centerline, centerline[1:]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length <= 0:
            raise RuntimeError("Differential centerline contains a zero-length segment")
        unit = (dx / length, dy / length)
        normal = (-unit[1], unit[0])
        segments.append((unit, normal))

    result = [(
        centerline[0][0] + side * distance * segments[0][1][0],
        centerline[0][1] + side * distance * segments[0][1][1],
    )]

    def cross(a: tuple[float, float], b: tuple[float, float]) -> float:
        return a[0] * b[1] - a[1] * b[0]

    for index, vertex in enumerate(centerline[1:-1], 1):
        previous_unit, previous_normal = segments[index - 1]
        next_unit, next_normal = segments[index]
        previous_point = (
            vertex[0] + side * distance * previous_normal[0],
            vertex[1] + side * distance * previous_normal[1],
        )
        next_point = (
            vertex[0] + side * distance * next_normal[0],
            vertex[1] + side * distance * next_normal[1],
        )
        denominator = cross(previous_unit, next_unit)
        if abs(denominator) < 1e-12:
            intersection = (
                (previous_point[0] + next_point[0]) / 2,
                (previous_point[1] + next_point[1]) / 2,
            )
        else:
            delta = (
                next_point[0] - previous_point[0],
                next_point[1] - previous_point[1],
            )
            scale = cross(delta, next_unit) / denominator
            intersection = (
                previous_point[0] + scale * previous_unit[0],
                previous_point[1] + scale * previous_unit[1],
            )
        result.append(intersection)

    result.append((
        centerline[-1][0] + side * distance * segments[-1][1][0],
        centerline[-1][1] + side * distance * segments[-1][1][1],
    ))
    return result


def route_controlled_pair(
    board: pcbnew.BOARD,
    nets: dict[str, pcbnew.NETINFO_ITEM],
    pair_name: str,
    p_net: str,
    n_net: str,
    p_start: tuple[float, float],
    n_start: tuple[float, float],
    centerline: list[tuple[float, float]],
    p_end: tuple[float, float],
    n_end: tuple[float, float],
    p_fanout: list[tuple[float, float]] | None = None,
    n_fanout: list[tuple[float, float]] | None = None,
) -> dict[str, float]:
    """Route and reject a pair unless coupling, skew and topology are sound."""
    p_trunk = offset_polyline(centerline, -1.0)
    n_trunk = offset_polyline(centerline, 1.0)
    p_path = [p_start, *p_trunk, *(p_fanout or []), p_end]
    n_path = [n_start, *n_trunk, *(n_fanout or []), n_end]

    p_length = path_length(p_path)
    n_length = path_length(n_path)
    p_coupled = path_length(p_trunk)
    n_coupled = path_length(n_trunk)
    skew = abs(p_length - n_length)
    coupled = min(p_coupled, n_coupled)
    uncoupled = max(p_length - p_coupled, n_length - n_coupled)

    if skew > 0.01:
        raise RuntimeError(f"{pair_name}: generated P/N skew {skew:.6f} mm exceeds 0.01 mm")
    if coupled < 16.00:
        raise RuntimeError(f"{pair_name}: coupled trunk {coupled:.6f} mm is below 16 mm")
    if uncoupled > 11.00:
        raise RuntimeError(f"{pair_name}: fan-in/out {uncoupled:.6f} mm exceeds 11 mm")

    add_polyline(board, nets, p_path, 0.23, pcbnew.F_Cu, p_net)
    add_polyline(board, nets, n_path, 0.23, pcbnew.F_Cu, n_net)
    print(
        f"  {pair_name}: P={p_length:.6f} mm N={n_length:.6f} mm "
        f"skew={skew:.6f} mm coupled>={coupled:.6f} mm "
        f"fanout<={uncoupled:.6f} mm vias=0/0"
    )
    return {
        "p_length": p_length,
        "n_length": n_length,
        "skew": skew,
        "coupled": coupled,
        "uncoupled": uncoupled,
    }


def validate_board_pair_topology(
    board: pcbnew.BOARD, pair_name: str, p_net: str, n_net: str,
) -> None:
    """Validate the quantized KiCad objects, not only source coordinates."""
    metrics: dict[str, tuple[float, int, set[int]]] = {}
    for net_name in (p_net, n_net):
        items = [item for item in board.GetTracks() if item.GetNetname() == net_name]
        vias = sum(isinstance(item, pcbnew.PCB_VIA) for item in items)
        layers = {
            item.GetLayer() for item in items
            if not isinstance(item, pcbnew.PCB_VIA)
        }
        length = sum(
            pcbnew.ToMM(item.GetLength()) for item in items
            if not isinstance(item, pcbnew.PCB_VIA)
        )
        metrics[net_name] = (length, vias, layers)

    p_length, p_vias, p_layers = metrics[p_net]
    n_length, n_vias, n_layers = metrics[n_net]
    skew = abs(p_length - n_length)
    if skew > 0.01:
        raise RuntimeError(f"{pair_name}: PCB-object skew {skew:.6f} mm exceeds 0.01 mm")
    if p_vias != n_vias or p_vias != 0:
        raise RuntimeError(f"{pair_name}: asymmetric/nonzero signal vias {p_vias}/{n_vias}")
    if p_layers != n_layers or p_layers != {pcbnew.F_Cu}:
        raise RuntimeError(
            f"{pair_name}: P/N layer sequences differ or are not F.Cu-only: "
            f"{p_layers}/{n_layers}"
        )


def validate_rf_launch_topology(board: pcbnew.BOARD, board_name: str) -> None:
    """Reject any drift from the symmetric, hardware-clear RF launch geometry."""

    def signature(
        start: tuple[float, float],
        end: tuple[float, float],
        width: float,
    ) -> tuple[tuple[float, float], tuple[float, float], float]:
        endpoints = tuple(sorted((
            tuple(round(value, 6) for value in start),
            tuple(round(value, 6) for value in end),
        )))
        return endpoints[0], endpoints[1], round(width, 6)

    footprints = {item.GetReference(): item for item in board.GetFootprints()}
    lengths: dict[str, float] = {}
    hole_clearances: dict[str, float] = {}
    for label, y in (("A", 31.0), ("B", 53.0)):
        low_y = y - 2.54
        expected = sorted((
            signature((85.75, y), (83.00, y), 0.35),
            signature((83.00, y), (65.08, y), 0.35),
            signature((65.08, y), (62.54, low_y), 0.35),
            signature((62.54, low_y), (61.54, low_y), 0.35),
            signature((61.54, low_y), (60.04, low_y), 0.55),
        ))
        items = [
            item for item in board.GetTracks()
            if item.GetNetname() == f"/RF_{label}_50"
        ]
        if any(isinstance(item, pcbnew.PCB_VIA) for item in items):
            raise RuntimeError(f"{board_name} RF {label}: signal via is not permitted")
        if any(item.GetLayer() != pcbnew.F_Cu for item in items):
            raise RuntimeError(f"{board_name} RF {label}: route is not F.Cu-only")

        actual = sorted(
            signature(
                (
                    pcbnew.ToMM(item.GetStart().x),
                    pcbnew.ToMM(item.GetStart().y),
                ),
                (
                    pcbnew.ToMM(item.GetEnd().x),
                    pcbnew.ToMM(item.GetEnd().y),
                ),
                pcbnew.ToMM(item.GetWidth()),
            )
            for item in items
        )
        if actual != expected:
            raise RuntimeError(
                f"{board_name} RF {label}: launch geometry drifted from the "
                "approved early-jog route"
            )

        length = sum(pcbnew.ToMM(item.GetLength()) for item in items)
        if not math.isclose(length, 26.762102, abs_tol=0.000001):
            raise RuntimeError(
                f"{board_name} RF {label}: length {length:.6f} mm does not "
                "match 26.762102 mm"
            )
        lengths[label] = length

        hole_reference = "H3" if label == "A" else "H4"
        expected_hole = (74.0, 25.0 if label == "A" else 59.0)
        if hole_reference not in footprints:
            raise RuntimeError(f"{board_name}: missing mounting hole {hole_reference}")
        hole_position = footprints[hole_reference].GetPosition()
        actual_hole = (
            pcbnew.ToMM(hole_position.x),
            pcbnew.ToMM(hole_position.y),
        )
        if not all(
            math.isclose(actual, expected, abs_tol=0.000001)
            for actual, expected in zip(actual_hole, expected_hole)
        ):
            raise RuntimeError(
                f"{board_name}: {hole_reference} moved from "
                f"{expected_hole} to {actual_hole}"
            )
        hole_clearance = abs(actual_hole[1] - y)
        if not math.isclose(hole_clearance, 6.0, abs_tol=0.000001):
            raise RuntimeError(
                f"{board_name}: RF {label} centerline to {hole_reference} "
                f"center is {hole_clearance:.6f} mm, not 6.000000 mm"
            )
        hole_clearances[label] = hole_clearance

    if not math.isclose(lengths["A"], lengths["B"], abs_tol=0.000001):
        raise RuntimeError(
            f"{board_name}: RF A/B lengths differ: "
            f"{lengths['A']:.6f}/{lengths['B']:.6f} mm"
        )
    print(
        f"  {board_name} RF: A={lengths['A']:.6f} mm "
        f"B={lengths['B']:.6f} mm H3/H4 center clearance="
        f"{hole_clearances['A']:.6f}/{hole_clearances['B']:.6f} mm"
    )


def footprint_pad_center(footprint: pcbnew.FOOTPRINT,
                         pad_number: str) -> tuple[float, float]:
    pads = [pad for pad in footprint.Pads() if pad.GetNumber() == pad_number]
    if len(pads) != 1:
        raise RuntimeError(
            f"Expected one pad {footprint.GetReference()}.{pad_number}; "
            f"found {len(pads)}"
        )
    position = pads[0].GetPosition()
    return pcbnew.ToMM(position.x), pcbnew.ToMM(position.y)


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
\t\t\t\t(material "Nan Ya NP-155F") (epsilon_r 4.36) (loss_tangent 0.02))
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
    title.SetTitle(f"100BASE-TX slip-ring VNA fixture - {config['board_label']} - DOC PINMAP")
    title.SetRevision("DRAFT 1")
    title.SetDate("2026-08-31")
    title.SetComment(0, "Electrical map from PALA720 slide 14; TX and RX pairs are routed.")
    title.SetComment(1, "REVIEW ONLY - DO NOT FABRICATE; verify continuity and endpoint connectors.")
    title.SetComment(2, "JLC04161H-7628 draft: 50R W0.35; 100R W0.23/G0.22; L2/L3 GND.")
    if bool(config["connector_flipped"]):
        title.SetComment(3, "J1 PCB B-SIDE CANDIDATE; verify front-fastened panel, A-key and pin 1.")

    net_names = [
        "/GND",
        "/PAIR_TX_P", "/PAIR_TX_N",
        "/PAIR_RX_P", "/PAIR_RX_N",
        "/RF_A_50", "/RF_B_50",
        "Net-(RCT1-Pad2)", "Net-(RCT2-Pad2)",
        "unconnected-(T1-Pad2)", "unconnected-(T2-Pad2)",
    ]
    net_names.extend(
        f"unconnected-(J1-Pin_{pin}-Pad{pin})"
        for pin, net_name in config["pin_nets"].items()
        if net_name is None
    )
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for net_name in net_names:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
        nets[net_name] = net

    footprints: dict[str, pcbnew.FOOTPRINT] = {}
    channels = (("A", "J2", "T1", "RCT1", 31.0), ("B", "J3", "T2", "RCT2", 53.0))
    for label, jref, tref, rref, y in channels:
        footprints[jref] = load_footprint(
            board, "balun_slipring_common", "SMA_MyAntenna_A-SMA-KE-16.5A_EdgeMount",
            jref, f"SMA_{label}", 85.75, y,
            symbol_uuid=symbol_uuids[jref],
            properties={
                "Manufacturer": "MyAntenna", "MPN": "A-SMA-KE-16.5A",
                "LCSC Part #": "C22467617",
                "Assembly": "FIT; JLC C22467617; Standard PCBA / wave-solder review",
                "Datasheet": "https://datasheet.lcsc.com/datasheet/pdf/92633ab2cf30de4413e1a152c04a3ed5.pdf?productCode=C22467617",
            },
        )
        footprints[tref] = load_footprint(
            board, "RF_Mini-Circuits", "Mini-Circuits_CD542_H2.84mm",
            tref, "ADT2-1T+", 57.50, y, 180,
            symbol_uuid=symbol_uuids[tref],
            properties={
                "Manufacturer": "Mini-Circuits", "MPN": "ADT2-1T+",
                "LCSC Part #": "C5223988", "Assembly": "FIT",
                "Datasheet": "https://www.minicircuits.com/pdfs/ADT2-1T+.pdf",
            },
        )
        footprints[rref] = load_footprint(
            board, "Resistor_SMD", "R_0805_2012Metric_Pad1.20x1.40mm_HandSolder",
            rref, "0R", 50.80, y,
            dnp=True,
            flipped=True,
            symbol_uuid=symbol_uuids[rref],
            properties={
                "Manufacturer": "UNI-ROYAL", "MPN": "0805W8F0000T5E",
                "LCSC Part #": "C17477",
                "Assembly": "DNP; fit all four RCTs only for controlled CT-GND comparison",
            },
        )

    connector_x, connector_y, connector_rotation = config["connector_position"]
    footprint_name = str(config["connector_footprint"]).split(":", 1)[1]
    footprints["J1"] = load_footprint(
        board, "balun_slipring_common", footprint_name,
        "J1", str(config["connector_value"]),
        float(connector_x), float(connector_y), float(connector_rotation),
        dnp=bool(config["connector_dnp"]),
        flipped=bool(config["connector_flipped"]),
        symbol_uuid=symbol_uuids["J1"],
        properties={
            "Manufacturer": str(config["connector_manufacturer"]),
            "MPN": str(config["connector_mpn"]),
            "LCSC Part #": str(config["connector_lcsc"]),
            "Assembly": str(config["assembly"]),
            "Datasheet": str(config["connector_datasheet"]),
            "Description": str(config["connector_description"]),
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
        "/RF_A_50": (("J2", "1"), ("T1", "3")),
        "/RF_B_50": (("J3", "1"), ("T2", "3")),
        "Net-(RCT1-Pad2)": (("RCT1", "2"), ("T1", "5")),
        "Net-(RCT2-Pad2)": (("RCT2", "2"), ("T2", "5")),
        "unconnected-(T1-Pad2)": (("T1", "2"),),
        "unconnected-(T2-Pad2)": (("T2", "2"),),
    }
    transformer_nodes = {
        "PAIR_TX_P": ("T1", "4"),
        "PAIR_TX_N": ("T1", "6"),
        "PAIR_RX_P": ("T2", "4"),
        "PAIR_RX_N": ("T2", "6"),
    }
    for pin, mapped_net in config["pin_nets"].items():
        if mapped_net is None:
            connections[f"unconnected-(J1-Pin_{pin}-Pad{pin})"] = (("J1", str(pin)),)
            continue
        net_name = f"/{mapped_net}"
        connections[net_name] = (
            transformer_nodes[str(mapped_net)],
            ("J1", str(pin)),
        )

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

    # Keep both 50-ohm launches as exact 22 mm translations of each other.
    # Route the long section on the SMA centerline so the edge launch has a
    # straight approach and both traces remain 6 mm from the adjacent M3-hole
    # centers.  After the short 0.55 mm transformer-pad flare, retain 1.0 mm
    # of 0.35 mm straight trace before the 2.54 x 2.54 mm 45-degree jog.  This
    # separates the width step from the bend without changing the inherited
    # 26.762102 mm total centerline length.
    # Document-mapped differential routes are added below and kept on F.Cu
    # over the solid inner GND planes.
    for _label, jref, _tref, rref, y in channels:
        input_net = f"/RF_{_label}_50"
        add_segment(board, nets, (85.75, y), (83.00, y), 0.35, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (83.00, y), (65.08, y), 0.35, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (65.08, y), (62.54, y - 2.54), 0.35, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (62.54, y - 2.54), (61.54, y - 2.54), 0.35, pcbnew.F_Cu, input_net)
        add_segment(board, nets, (61.54, y - 2.54), (60.04, y - 2.54), 0.55, pcbnew.F_Cu, input_net)

        # Preserve an optional CT-GND test path below the differential pair.
        # The transformer CT reaches B.Cu through one central via, then the
        # DNP-by-default back-side 0-ohm link reaches a remote GND return via.
        # Populate all four RCT links across both fixture boards together only
        # for a controlled grounded-center-tap comparison.
        ct_net = f"Net-({rref}-Pad2)"
        add_segment(board, nets, (54.96, y), (52.80, y), 0.30, pcbnew.F_Cu, ct_net)
        add_via(board, nets, 52.80, y, ct_net)
        add_segment(board, nets, (52.80, y), (51.80, y), 0.30, pcbnew.B_Cu, ct_net)
        ground_via_y = 24.0 if y < 42.0 else 60.0
        add_segment(board, nets, (49.80, y), (49.00, ground_via_y), 0.50, pcbnew.B_Cu, "/GND")
        add_via(board, nets, 49.00, ground_via_y, "/GND")

        add_segment(board, nets, (60.04, y + 2.54), (62.00, y + 2.54), 0.80, pcbnew.F_Cu, "/GND")
        add_via(board, nets, 62.00, y + 2.54, "/GND")
        add_via(board, nets, 60.04, y + 4.35, "/GND")

        for sy in (y - 2.825, y + 2.825):
            add_segment(board, nets, (85.75, sy), (82.20, sy), 0.80, pcbnew.F_Cu, "/GND")
            add_segment(board, nets, (85.75, sy), (82.20, sy), 0.80, pcbnew.B_Cu, "/GND")
            add_via(board, nets, 82.20, sy, "/GND")
            add_via(board, nets, 80.60, sy, "/GND")

    mapped_pin = {
        str(net_name): str(pin)
        for pin, net_name in config["pin_nets"].items()
        if net_name is not None
    }
    route_ends = {
        "PAIR_TX_P": footprint_pad_center(footprints["T1"], "4"),
        "PAIR_TX_N": footprint_pad_center(footprints["T1"], "6"),
        "PAIR_RX_P": footprint_pad_center(footprints["T2"], "4"),
        "PAIR_RX_N": footprint_pad_center(footprints["T2"], "6"),
    }
    route_starts = {
        net_name: footprint_pad_center(footprints["J1"], pin)
        for net_name, pin in mapped_pin.items()
    }

    # Each pair is derived from one shared centerline.  Offsetting it by
    # +/-0.225 mm creates W=0.23 mm traces at 0.45 mm center spacing, hence a
    # 0.22 mm edge gap.  Only the short connector/transformer fan-in/out is
    # opened.  The generator rejects skew above 0.01 mm, coupled trunk below
    # 16 mm, or total fan-in/out above 11 mm.
    if len(config["pin_nets"]) == 5:
        route_controlled_pair(
            board, nets, "Molex TX", "/PAIR_TX_P", "/PAIR_TX_N",
            route_starts["PAIR_TX_P"], route_starts["PAIR_TX_N"],
            [(34.0, 40.125), (38.0, 40.125), (49.0, 31.0), (51.0, 31.0)],
            route_ends["PAIR_TX_P"], route_ends["PAIR_TX_N"],
        )
        route_controlled_pair(
            board, nets, "Molex RX", "/PAIR_RX_P", "/PAIR_RX_N",
            route_starts["PAIR_RX_P"], route_starts["PAIR_RX_N"],
            [(34.0, 42.625), (38.0, 42.625), (49.0, 53.0), (51.0, 53.0)],
            route_ends["PAIR_RX_P"], route_ends["PAIR_RX_N"],
        )
    else:
        # J1 is a back-side electrical-layout candidate at 225 degrees.  Its
        # PTH signal pads 1-4 then face the baluns while NC pads 5-8 face away,
        # allowing both complete pairs to stay on F.Cu with zero signal vias.
        # The slight final centerline angles provide smooth length correction;
        # there are no one-sided U-turns or polarity-specific layer changes.
        route_controlled_pair(
            board, nets, "M12 TX", "/PAIR_TX_P", "/PAIR_TX_N",
            route_starts["PAIR_TX_P"], route_starts["PAIR_TX_N"],
            [
                (31.766629161, 38.746273545),
                (33.102674036, 36.285585818),
                (36.0, 34.0), (46.0, 31.0),
                (48.0, 30.638185215),
            ],
            route_ends["PAIR_TX_P"], route_ends["PAIR_TX_N"],
            [(49.0, 29.9), (52.8, 28.46)],
            [(49.0, 32.1), (52.8, 33.54)],
        )
        route_controlled_pair(
            board, nets, "M12 RX", "/PAIR_RX_P", "/PAIR_RX_N",
            route_starts["PAIR_RX_P"], route_starts["PAIR_RX_N"],
            [
                (32.479359637, 44.479359637),
                (34.459258625, 46.459258625),
                (37.0, 49.0), (46.0, 53.0),
                (48.0, 53.262015126),
            ],
            route_ends["PAIR_RX_P"], route_ends["PAIR_RX_N"],
            [(49.0, 51.9), (52.8, 50.46)],
            [(49.0, 54.1), (52.8, 55.54)],
        )

    validate_board_pair_topology(
        board, f"{config['board_label']} TX", "/PAIR_TX_P", "/PAIR_TX_N"
    )
    validate_board_pair_topology(
        board, f"{config['board_label']} RX", "/PAIR_RX_P", "/PAIR_RX_N"
    )
    validate_rf_launch_topology(board, str(config["board_label"]))

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

    if str(config["board_label"]) == "M12 END":
        usage_label = add_board_text(board, "슬립링 / SLIPRING", 54, 22.1, size=1.05, thickness=0.18)
        usage_label.SetUnresolvedFontName("Malgun Gothic")
    else:
        add_board_text(board, f"SLIPRING {config['board_label']} / DOC MAP", 54, 22.1, size=1.05, thickness=0.18)
    add_board_text(board, "DRAFT 1 - DO NOT FAB", 53, 62.0, size=1.05, thickness=0.18)
    add_board_text(board, "TX", 78.5, 33.8, size=1.0, thickness=0.16)
    add_board_text(board, "RX", 78.5, 55.8, size=1.0, thickness=0.16)
    add_board_text(board, "UNUSED SMA -> 50R", 71.5, 62.0, pcbnew.B_SilkS, 0.8, 0.13)
    add_board_text(board, "DOC MAP: TX / RX", 43.5, 42.0, pcbnew.Cmts_User, 1.2, 0.18, 90)
    add_board_text(board, "VERIFY REV-504 CONTINUITY + J1 PIN 1 / KEY BEFORE FAB", 52.0, 66.5, pcbnew.Cmts_User, 0.9, 0.14)

    # Mapping boundary / connector-mechanics reservation on user layers.
    for start, end in zip(
        ((36, 24), (53.5, 24), (53.5, 60), (36, 60)),
        ((53.5, 24), (53.5, 60), (36, 60), (36, 24)),
    ):
        add_line(board, start, end, pcbnew.Cmts_User, 0.15)

    if len(config["pin_nets"]) == 5:
        add_board_text(board, "J1 PIN 1", 29.0, 36.0, size=0.80, thickness=0.13)
        add_board_text(board, "5055680571 CAND", 29.0, 49.0, size=0.80, thickness=0.13)
    else:
        add_board_text(board, "M12 J1 / B-SIDE CAND", 30.0, 30.0, size=0.80, thickness=0.13)
        add_board_text(board, "PIN 1 / A-KEY VERIFY", 30.0, 52.8, pcbnew.Cmts_User, 0.8, 0.13)
        add_board_text(board, "VERIFY MATING FACE / PANEL ACCESS", 30.0, 32.0, pcbnew.Cmts_User, 0.7, 0.12)
        add_board_text(board, "PINS 5-8: NC", 30.0, 55.0, pcbnew.Cmts_User, 0.8, 0.13)

    reference_positions = {
        "J2": (80.0, 24.2, 0), "J3": (80.0, 46.2, 0),
        "T1": (57.5, 25.5, 0), "T2": (57.5, 47.5, 0),
        "RCT1": (49.8, 34.0, 0), "RCT2": (49.8, 56.0, 0),
        "J1": (29.0, 34.0, 0) if len(config["pin_nets"]) == 5 else (30.0, 31.8, 0),
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


def verify_overwrite_policy(force: bool, variants: list[dict[str, object]]) -> None:
    outputs: list[Path] = []
    for config in variants:
        directory = Path(config["directory"])
        project = str(config["project"])
        outputs.extend(directory / f"{project}.{suffix}" for suffix in ("kicad_sch", "kicad_pcb", "kicad_pro", "kicad_dru"))
    existing = [path for path in outputs if path.exists()]
    if existing and not force:
        formatted = "\n".join(f"  {path.relative_to(HERE)}" for path in existing)
        raise SystemExit(
            "REFUSED: draft outputs already exist.  This generator can overwrite manual edits.\n"
            f"{formatted}\n"
            "Use --force only while intentionally regenerating the document-mapped drafts."
        )

    if force:
        protected = []
        for path in existing:
            if path.suffix not in (".kicad_sch", ".kicad_pcb"):
                continue
            content = path.read_text(encoding="utf-8")
            if (
                not any(marker in content for marker in DRAFT_REVISION_MARKERS)
                or DRAFT_WARNING_MARKER not in content
            ):
                protected.append(path)
        if protected:
            formatted = "\n".join(f"  {path.relative_to(HERE)}" for path in protected)
            raise SystemExit(
                "REFUSED: at least one design no longer has a recognized draft revision and "
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


def refill_and_validate_staged_board(config: dict[str, object]) -> None:
    """Persist zone fills and reject a staged PCB with DRC/parity violations."""
    directory = Path(config["directory"])
    project = str(config["project"])
    board = directory / f"{project}.kicad_pcb"
    report = directory / f"{project}_staged_drc.rpt"
    if not KICAD_CLI.is_file():
        raise RuntimeError(f"KiCad CLI not found: {KICAD_CLI}")
    result = subprocess.run(
        [
            str(KICAD_CLI), "pcb", "drc",
            "--refill-zones", "--save-board",
            "--schematic-parity", "--all-track-errors",
            "--severity-all", "--severity-exclusions",
            "--exit-code-violations",
            "-o", str(report), str(board),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        report_text = report.read_text(encoding="utf-8", errors="replace") if report.exists() else ""
        details = "\n".join(
            part for part in (result.stdout, result.stderr, report_text) if part
        )
        raise RuntimeError(
            f"Staged {project} DRC/parity/refill failed with exit "
            f"{result.returncode}:\n{details}"
        )


def generate_variant_transactionally(config: dict[str, object]) -> None:
    """Build a complete variant off-line, then replace the live draft files."""
    target_dir = Path(config["directory"])
    project = str(config["project"])
    target_dir.mkdir(parents=True, exist_ok=True)
    filenames = [
        f"{project}.kicad_sch",
        f"{project}.kicad_pcb",
        f"{project}.kicad_pro",
        f"{project}.kicad_dru",
        "fp-lib-table",
    ]

    # A sibling of the output directories preserves the
    # ${KIPRJMOD}/../common.pretty relationship in fp-lib-table.
    with tempfile.TemporaryDirectory(prefix=f".{project}-stage-", dir=HERE) as temp:
        stage_dir = Path(temp)
        stage_config = dict(config)
        stage_config["directory"] = stage_dir
        symbol_uuids = write_schematic(stage_config)
        write_board(stage_config, symbol_uuids)
        # pcbnew.SaveBoard creates a minimal sibling .kicad_pro on Windows.
        # Restore the intended impedance/netclass settings after board save.
        write_project(stage_config)
        refill_and_validate_staged_board(stage_config)

        missing = [name for name in filenames if not (stage_dir / name).is_file()]
        if missing:
            raise RuntimeError(f"Staged generation did not create: {', '.join(missing)}")

        backup_dir = stage_dir / "backup"
        backup_dir.mkdir()
        originally_present: set[str] = set()
        for name in filenames:
            target = target_dir / name
            if target.exists():
                shutil.copy2(target, backup_dir / name)
                originally_present.add(name)

        replaced: list[str] = []
        try:
            for name in filenames:
                os.replace(stage_dir / name, target_dir / name)
                replaced.append(name)
            invalidate_reports(config)
        except Exception:
            # Never leave a schematic from one generation paired with a
            # PCB/project from another after a failed live-file replacement.
            for name in reversed(replaced):
                target = target_dir / name
                if name in originally_present:
                    os.replace(backup_dir / name, target)
                elif target.exists():
                    target.unlink()
            raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="overwrite existing draft outputs")
    parser.add_argument(
        "--variant",
        action="append",
        choices=tuple(VARIANTS),
        help="regenerate only the selected endpoint; may be supplied more than once",
    )
    args = parser.parse_args()
    selected = [VARIANTS[name] for name in (args.variant or tuple(VARIANTS))]
    verify_overwrite_policy(args.force, selected)
    for config in selected:
        generate_variant_transactionally(config)
        print(f"Generated {config['project']} in {Path(config['directory']).relative_to(HERE)}")


if __name__ == "__main__":
    main()
