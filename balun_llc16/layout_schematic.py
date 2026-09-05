"""Lay out the LLC schematic without changing the shared slip-ring generator."""

from __future__ import annotations

import re
import generate_pinmap_tbd_drafts as core

PROJECT = "balun_llc16"


def quoted(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def text(key: str, value: str, x: float, y: float, size: float = 1.27,
         *, left: bool = False, bold: bool = False, korean: bool = False) -> str:
    face = '(face "Malgun Gothic")' if korean else ""
    weight = "(bold yes)" if bold else ""
    justify = "(justify left)" if left else ""
    return f'''\t(text "{quoted(value)}"
        (exclude_from_sim no) (at {x:g} {y:g} 0)
        (effects (font {face} (size {size:g} {size:g}) {weight}) {justify})
        (uuid "{core.stable_uuid(PROJECT, key)}")
    )'''


def line(key: str, x1: float, y1: float, x2: float, y2: float) -> str:
    return f'''\t(polyline (pts (xy {x1:g} {y1:g}) (xy {x2:g} {y2:g}))
        (stroke (width 0.254) (type default)) (fill (type none))
        (uuid "{core.stable_uuid(PROJECT, key)}")
    )'''


def wire(key: str, x1: float, y1: float, x2: float, y2: float) -> str:
    return core.schematic_wire(PROJECT, key, x1, y1, x2, y2)


def label(key: str, value: str, x: float, y: float, size: float = 1.27) -> str:
    return f'''\t(label "{quoted(value)}" (at {x:g} {y:g} 0)
        (effects (font (size {size:g} {size:g})) (justify left bottom))
        (uuid "{core.stable_uuid(PROJECT, key)}")
    )'''


def field(block: str, name: str, x: float, y: float, size: float = 1.27, angle: int = 0) -> str:
    match = re.search(rf'\(property "{re.escape(name)}" "([^"]*)"', block)
    if match is None:
        raise ValueError(f"Missing property: {name}")
    original, _ = core.balanced_expression(block, match.start())
    replacement = f'''(property "{name}" "{match.group(1)}"
        (at {x:g} {y:g} {angle}) (show_name no) (do_not_autoplace no)
        (effects (font (size {size:g} {size:g}))))'''
    return block.replace(original, replacement, 1)


def position(block: str, x: float, y: float,
             reference: tuple[float, float], value: tuple[float, float]) -> str:
    rotation = float(re.search(r'\(at [-\d.]+ [-\d.]+ ([-\d.]+)\)', block).group(1))
    block, count = re.subn(r'\(at [-\d.]+ [-\d.]+ ([-\d.]+)\)',
                          lambda m: f"(at {x:g} {y:g} {m.group(1)})", block, count=1)
    assert count == 1
    field_angle = 90 if rotation % 180 == 90 else 0
    return field(field(block, "Reference", *reference, angle=field_angle), "Value", *value, angle=field_angle)


def render(base: str, spec: dict) -> str:
    """Return an A4 review schematic with the original component UUIDs/pin IDs."""
    start = base.index("\t(lib_symbols") + 1
    library, _ = core.balanced_expression(base, start)
    instances = core.find_symbol_instances(base)
    drawing = [
        text("heading", "LLC-13M-1 / ACTUATOR to RJ45", 148.59, 18.0, 2.2, bold=True),
        text("purpose", "구동기 to RJ45  |  2-channel VNA fixture", 148.59, 25.4, 1.6, korean=True),
        line("heading-rule", 17.78, 31.75, 279.4, 31.75),
        text("j1-heading", "M12 TO LLC CABLE", 232.41, 39.37, 1.5, bold=True),
        text("j1-required", "Required 8-pin MALE / cable is FEMALE", 232.41, 45.72, 1.1),
        line("column-rule", 180.34, 36.83, 180.34, 146.05),
    ]
    placed = []
    for channel, offset, pair in ((1, 0.0, "TX"), (2, 55.88, "RX")):
        letter = "A" if channel == 1 else "B"
        jref, tref, rref = f"J{channel + 1}", f"T{channel}", f"RCT{channel}"
        y = 63.5 + offset
        drawing.append(text(f"heading:{channel}", f"{letter} / {pair} PAIR  -  50 ohm SMA to 100 ohm differential",
                            20.32, 39.37 + offset, 1.35, left=True, bold=True))
        placed.append(position(instances[jref], 48.26, y - 5.08,
                               (43.18, y + 1.27), (43.18, y + 5.08)))
        placed.append(position(instances[tref], 101.6, y,
                               (101.6, y - 15.24), (101.6, y - 11.43)))
        placed.append(position(instances[rref], 137.16, y + 20.32,
                               (137.16, y + 15.24), (137.16, y + 25.4)))
        drawing.extend([
            wire(f"{jref}:rf", 53.34, y - 5.08, 96.52, y - 5.08),
            label(f"{jref}:rf-name", f"RF_{letter}_50", 66.04, y - 5.08),
            wire(f"{jref}:ground", 48.26, y - 10.16, 48.26, y - 15.24),
            label(f"{jref}:ground-name", "GND", 48.26, y - 15.24),
            wire(f"{tref}:ground", 96.52, y + 5.08, 96.52, y + 12.7),
            label(f"{tref}:ground-name", "GND", 96.52, y + 12.7),
            wire(f"{tref}:negative", 106.68, y - 5.08, 132.08, y - 5.08),
            label(f"{tref}:negative-name", f"PAIR_{pair}_N", 132.08, y - 5.08),
            wire(f"{tref}:positive", 106.68, y + 5.08, 132.08, y + 5.08),
            label(f"{tref}:positive-name", f"PAIR_{pair}_P", 132.08, y + 5.08),
            wire(f"{tref}:ct", 106.68, y, 116.84, y),
            label(f"{tref}:ct-name", f"CT_{letter}", 116.84, y, 1.0),
            wire(f"{rref}:ct", 140.97, y + 20.32, 154.94, y + 20.32),
            label(f"{rref}:ct-name", f"CT_{letter}", 154.94, y + 20.32, 1.0),
            wire(f"{rref}:ground", 133.35, y + 20.32, 125.73, y + 20.32),
            label(f"{rref}:ground-name", "GND", 125.73, y + 20.32, 1.0),
            text(f"{rref}:dnp", "DNP / CT FLOAT", 153.67, y + 25.4, 1.27),
            text(f"{tref}:ratio", "1:2 impedance", 90.17, y + 20.32, 1.0),
        ])
    placed.append(position(instances["J1"], 248.92, 76.2,
                           (248.92, 58.42), (238.76, 96.52)))
    pin_notes = {1: "P24 / NC", 2: "TX-", 3: "RX+", 4: "RX-",
                 5: "N24 / NC", 6: "N24 / NC", 7: "P24 / NC", 8: "TX+"}
    for pin in range(1, 9):
        y = 68.58 + (pin - 1) * 2.54
        net = spec["pin_nets"][str(pin)]
        if net is None:
            drawing.append(core.schematic_no_connect(PROJECT, f"J1:nc:{pin}", 243.84, y))
        else:
            drawing.extend([
                wire(f"J1:wire:{pin}", 204.47, y, 243.84, y),
                label(f"J1:label:{pin}", net, 204.47, y, 1.1),
            ])
        drawing.append(text(f"J1:function:{pin}", pin_notes[pin], 252.73, y, 1.27, left=True))

    drawing.extend([
        text("map-heading", "CABLE MAP / NUMERIC PINS", 232.41, 107.95, 1.3, bold=True),
        text("map-col1", "SIGNAL", 201.93, 114.3, 1.1, bold=True),
        text("map-col2", "M12 J1", 232.41, 114.3, 1.1, bold=True),
        text("map-col3", "RJ45 DUT", 264.16, 114.3, 1.1, bold=True),
        line("map-rule", 190.5, 116.84, 276.86, 116.84),
        text("j1-view-note", "J1 symbol shows logical pin numbers only.", 232.41, 153.67, 1.05),
        text("j1-view-note2", "Not a mechanical mating-face drawing.", 232.41, 158.75, 1.05),
        line("notes-rule", 17.78, 151.13, 172.72, 151.13),
        text("notes-heading", "ASSEMBLY / MEASUREMENT NOTES", 20.32, 156.21, 1.3, left=True, bold=True),
    ])
    for index, row in enumerate(spec["dut_continuity_expected"]):
        y = 122.555 + index * 6.35
        for column, value, x in ((1, row["signal"], 201.93), (2, str(row["m12"]), 232.41),
                                 (3, str(row["rj45"]), 264.16)):
            drawing.append(text(f"map:{index}:{column}", value, x, y, 1.27))
    notes = [
        "1. J1: MB12MBAFF08ST-3, male, B-side. Sourcing / panel support on HOLD.",
        "2. J1.1/5/6/7 are NC. Never connect cable N24 to VNA GND.",
        "3. RCT1/RCT2: 0R, DNP. Keep both CTs floating. No on-board 100 ohm load.",
        "4. Use existing RJ45 A/B fixture; terminate all four unused SMA ports.",
        "5. Coax O/S/L + THRU calibration does not remove the baluns or PCB.",
        "6. Unpowered DUT only. Check cable wiring before first VNA connection.",
    ]
    for index, note in enumerate(notes):
        drawing.append(text(f"note:{index}", note, 20.32, 162.56 + index * 5.08, 1.5, left=True))
    root = core.stable_uuid(PROJECT, "root")
    return f'''(kicad_sch
    (version 20260306) (generator "eeschema") (generator_version "10.0")
    (uuid "{root}") (paper "A4")
    (title_block
        (title "LLC-13M-1 / ACTUATOR to RJ45")
        (date "2026-09-03") (rev "{spec['schematic_revision']}")
        (comment 1 "50 ohm coax / 100 ohm differential; CT-FLOAT baseline.")
        (comment 2 "Source: LLC-13M-1 drawing, 2022-04-25, page 1.")
        (comment 3 "PCB DRAFT A: JLC sourcing / panel mechanics HOLD.")
    )
{core.indent_block(library, 1)}
{chr(10).join(drawing)}
{chr(10).join(core.indent_block(block, 1) for block in placed)}
    (sheet_instances (path "/" (page "1")))
    (embedded_fonts no)
)
'''
