"""Presentation-only layouts for the three existing BALUN schematic designs.

Retain symbol/pin UUIDs, library definitions, component properties and net names.
Anonymous primary/CT nets stay wired directly; no new electrical labels are added.
"""

from __future__ import annotations

import re
import generate_pinmap_tbd_drafts as core


def quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


class Sheet:
    def __init__(self, source: str, project: str):
        self.source, self.project = source, project
        self.root = re.search(r'\(uuid\s+"([^"]+)"', source).group(1)
        self.instances = core.find_symbol_instances(source)
        lib_start = source.index("\t(lib_symbols") + 1
        self.library, _ = core.balanced_expression(source, lib_start)
        self.drawing: list[str] = []
        self.placed: dict[str, str] = {}

    def uid(self, key: str) -> str:
        return core.stable_uuid(self.project, "readable:" + key)

    def text(self, key: str, value: str, x: float, y: float, size: float = 1.27,
             *, left: bool = False, bold: bool = False, korean: bool = False):
        font = '(face "Malgun Gothic")' if korean else ""
        weight = "(bold yes)" if bold else ""
        justify = "(justify left)" if left else ""
        self.drawing.append(f'''\t(text "{quote(value)}" (exclude_from_sim no)
            (at {x:g} {y:g} 0)
            (effects (font {font} (size {size:g} {size:g}) {weight}) {justify})
            (uuid "{self.uid(key)}"))''')

    def line(self, key: str, x1: float, y1: float, x2: float, y2: float):
        self.drawing.append(f'''\t(polyline (pts (xy {x1:g} {y1:g}) (xy {x2:g} {y2:g}))
            (stroke (width 0.254) (type default)) (fill (type none))
            (uuid "{self.uid(key)}"))''')

    def wire(self, key: str, x1: float, y1: float, x2: float, y2: float):
        self.drawing.append(core.schematic_wire(self.project, "readable:" + key, x1, y1, x2, y2))

    def label(self, key: str, name: str, x: float, y: float, size: float = 1.27):
        self.drawing.append(f'''\t(label "{quote(name)}" (at {x:g} {y:g} 0)
            (effects (font (size {size:g} {size:g})) (justify left bottom))
            (uuid "{self.uid(key)}"))''')

    def nc(self, key: str, x: float, y: float):
        self.drawing.append(core.schematic_no_connect(self.project, "readable:" + key, x, y))

    @staticmethod
    def field(block: str, name: str, x: float, y: float, rotation: int, size: float) -> str:
        match = re.search(rf'\(property "{re.escape(name)}" "((?:[^"\\]|\\.)*)"', block)
        original, _ = core.balanced_expression(block, match.start())
        angle = 90 if rotation % 180 == 90 else 0
        new = f'''(property "{name}" "{match.group(1)}" (at {x:g} {y:g} {angle})
            (show_name no) (do_not_autoplace no)
            (effects (font (size {size:g} {size:g}))))'''
        return block.replace(original, new, 1)

    def place(self, ref: str, x: float, y: float, reference: tuple[float, float],
              value: tuple[float, float], *, rotation: int | None = None, size: float = 1.27):
        assert ref not in self.placed, ref
        block = self.instances[ref]
        old = re.search(r'\(at [-\d.]+ [-\d.]+ ([-\d.]+)\)', block)
        rotation = int(float(old.group(1))) if rotation is None else rotation
        block = re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)',
                       f"(at {x:g} {y:g} {rotation})", block, count=1)
        block = self.field(block, "Reference", *reference, rotation, size)
        block = self.field(block, "Value", *value, rotation, size)
        self.placed[ref] = block

    def channel(self, number: int, x: float, y: float, positive: str, negative: str,
                *, rf_label: str | None, heading: str, heading_y: float):
        """SMA -> primary; secondary -> existing pair labels; CT -> RCT.2 directly."""
        jref, tref, rref = f"J{number + 1}", f"T{number}", f"RCT{number}"
        self.text(f"{tref}:heading", heading, x - 81.28, heading_y, 1.35, left=True, bold=True)
        self.place(jref, x - 53.34, y - 5.08, (x - 58.42, y + 1.27), (x - 58.42, y + 5.08))
        self.place(tref, x, y, (x, y - 15.24), (x, y - 11.43))
        # Rotating a nonpolar resistor changes only drawing orientation.
        # At 270 degrees its left pad is pin 2 (CT) and right pad is pin 1 (GND).
        self.place(rref, x + 30.48, y, (x + 30.48, y - 15.24), (x + 30.48, y - 11.43), rotation=270)
        self.wire(f"{jref}:rf", x - 48.26, y - 5.08, x - 5.08, y - 5.08)
        if rf_label:
            self.label(f"{jref}:rf-name", rf_label, x - 35.56, y - 5.08)
        else:
            self.text(f"{jref}:rf-note", "50 ohm", x - 27.94, y - 7.62, 1.1)
        self.wire(f"{jref}:gnd", x - 53.34, y - 10.16, x - 53.34, y - 15.24)
        self.label(f"{jref}:gnd-name", "GND", x - 53.34, y - 15.24)
        self.wire(f"{tref}:gnd", x - 5.08, y + 5.08, x - 5.08, y + 12.7)
        self.label(f"{tref}:gnd-name", "GND", x - 5.08, y + 12.7)
        self.wire(f"{tref}:n", x + 5.08, y - 5.08, x + 20.32, y - 5.08)
        self.label(f"{tref}:n-name", negative, x + 20.32, y - 5.08, 1.1)
        self.wire(f"{tref}:p", x + 5.08, y + 5.08, x + 20.32, y + 5.08)
        self.label(f"{tref}:p-name", positive, x + 20.32, y + 5.08, 1.1)
        self.wire(f"{tref}:ct", x + 5.08, y, x + 26.67, y)
        self.wire(f"{rref}:gnd", x + 34.29, y, x + 48.26, y)
        self.label(f"{rref}:gnd-name", "GND", x + 48.26, y, 1.1)
        self.text(f"{rref}:population", "DNP / CT FLOAT", x + 33.02, y + 20.32, 1.27)
        self.text(f"{tref}:ratio", "1:2 impedance", x - 11.43, y + 20.32, 1.1)

    def finish(self, paper: str, title: str, comments: list[str]) -> str:
        assert set(self.instances) == set(self.placed), set(self.instances) - set(self.placed)
        rev = re.search(r'\(rev "([^"]*)"', self.source).group(1)
        items = "\n".join(f'        (comment {i} "{quote(v)}")' for i, v in enumerate(comments, 1))
        return f'''(kicad_sch
    (version 20260306) (generator "eeschema") (generator_version "10.0")
    (uuid "{self.root}") (paper "{paper}")
    (title_block (title "{quote(title)}") (date "2026-09-03") (rev "{rev}")
{items}
    )
{core.indent_block(self.library, 1)}
{chr(10).join(self.drawing)}
{chr(10).join(core.indent_block(self.placed[r], 1) for r in self.instances)}
    (sheet_instances (path "/" (page "1")))
    (embedded_fonts no)
)
'''


def slipring(source: str, variant: str) -> str:
    is_m12 = variant == "m12"
    project = "balun_slipring_" + variant
    s = Sheet(source, project)
    endpoint = "M12 END" if is_m12 else "MOLEX END"
    s.text("heading", "SLIPRING / " + endpoint, 148.59, 18.0, 2.2, bold=True)
    s.text("subtitle", "슬립링 측정 지그  |  " + endpoint, 148.59, 25.4, 1.6, korean=True)
    s.line("heading-rule", 17.78, 31.75, 279.4, 31.75)
    s.line("column-rule", 180.34, 36.83, 180.34, 146.05)
    for i, pair in ((1, "TX"), (2, "RX")):
        s.channel(i, 101.6, 63.5 + (i - 1) * 55.88, f"PAIR_{pair}_P", f"PAIR_{pair}_N",
                  rf_label=f"RF_{'AB'[i - 1]}_50", heading=f"{'AB'[i - 1]} / {pair} PAIR  -  50 ohm SMA to 100 ohm differential",
                  heading_y=39.37 + (i - 1) * 55.88)
    s.text("connector-heading", endpoint + " / J1", 232.41, 39.37, 1.5, bold=True)
    s.text("connector-state", "FEMALE PCB mate / candidate on HOLD" if is_m12 else "505565 cable mate candidate / HOLD",
           232.41, 45.72, 1.15)
    s.place("J1", 248.92, 76.2, (248.92, 58.42), (232.41, 96.52), size=1.15)
    pin_map = ({1: "PAIR_RX_N", 2: "PAIR_RX_P", 3: "PAIR_TX_N", 4: "PAIR_TX_P", 5: None, 6: None, 7: None, 8: None}
               if is_m12 else {1: "PAIR_TX_P", 2: "PAIR_TX_N", 3: "PAIR_RX_P", 4: "PAIR_RX_N", 5: None})
    descriptions = ({1: "RX-", 2: "RX+", 3: "TX-", 4: "TX+", 5: "GPS RX / NC", 6: "1PPS / NC", 7: "+24V / NC", 8: "24V RTN / NC"}
                    if is_m12 else {1: "TX+", 2: "TX-", 3: "RX+", 4: "RX-", 5: "UNUSED / NC"})
    first_y = 68.58 if is_m12 else 71.12
    for pin, net in pin_map.items():
        y = first_y + (pin - 1) * 2.54
        if net:
            s.wire(f"J1:{pin}:wire", 204.47, y, 243.84, y)
            s.label(f"J1:{pin}:net", net, 204.47, y, 1.1)
        else:
            s.nc(f"J1:{pin}:nc", 243.84, y)
        s.text(f"J1:{pin}:function", descriptions[pin], 252.73, y, 1.05, left=True)
    s.text("map-heading", "SLIPRING MAP / PALA720 SLIDE 14", 232.41, 107.95, 1.25, bold=True)
    for key, value, x in (("signal", "SIGNAL", 201.93), ("molex", "MOLEX", 232.41), ("m12", "M12", 264.16)):
        s.text("map:" + key, value, x, 114.3, 1.1, bold=True)
    s.line("map-rule", 190.5, 116.84, 276.86, 116.84)
    for i, row in enumerate((("TX+", "1", "4"), ("TX-", "2", "3"), ("RX+", "3", "2"), ("RX-", "4", "1"))):
        for j, x in enumerate((201.93, 232.41, 264.16)):
            s.text(f"map:{i}:{j}", row[j], x, 122.555 + i * 6.35)
    s.text("pin-view", "Logical pin numbers; verify mating-face / PCB view.", 232.41, 153.67, 1.0)
    s.text("not-llc", "NOT interchangeable with the LLC / actuator M12 fixture.", 232.41, 158.75, 1.0)
    s.line("notes-rule", 17.78, 151.13, 172.72, 151.13)
    s.text("notes-heading", "ASSEMBLY / MEASUREMENT NOTES", 20.32, 156.21, 1.3, left=True, bold=True)
    notes = [
        "1. REVIEW ONLY - DO NOT FABRICATE. Connector fit / mechanics remain on HOLD.",
        "2. Existing J1 DNP is retained as a candidate HOLD; not a connectorless order.",
        "3. RCT1/RCT2 DNP: CT-FLOAT baseline. No on-board 100 ohm load.",
        "4. M12 pins 5/6/7/8 are NC; disconnect power and all active equipment.",
        "5. Two-board tests: terminate the two unused SMA ports with 50 ohm loads.",
        "6. Coax O/S/L + THRU does not remove the balun / PCB / connector response.",
    ]
    for i, note in enumerate(notes):
        s.text(f"note:{i}", note, 20.32, 162.56 + i * 5.08, 1.35, left=True)
    return s.finish("A4", "SLIPRING / " + endpoint, [
        "50 ohm coax / 100 ohm differential; CT-FLOAT baseline.",
        "Source: PALA720 slide 14; layout-only refresh.",
        "HOLD / DO NOT FABRICATE: endpoint fit and mechanics.",
    ])


def rj45(source: str) -> str:
    s = Sheet(source, "balun_eth_rj45")
    s.text("heading", "RJ45 / FOUR-PAIR VNA FIXTURE", 210.0, 18.0, 2.6, bold=True)
    s.text("subtitle", "RJ45 이더넷 케이블 측정 지그  |  4-channel VNA fixture", 210.0, 25.4, 1.8, korean=True)
    s.line("heading-rule", 17.78, 31.75, 402.59, 31.75)
    s.line("column-rule", 308.61, 36.83, 308.61, 246.38)
    for i, pair in enumerate(((1, 2), (3, 6), (4, 5), (7, 8)), 1):
        letter = "ABCD"[i - 1]
        x, y = (93.98 if i % 2 else 246.38), (66.04 if i < 3 else 139.7)
        s.channel(i, x, y, f"D{letter}_P", f"D{letter}_N", rf_label=None,
                  heading=f"{letter} / RJ45 {pair[0]}(+) - {pair[1]}(-)", heading_y=y - 26.67)
    s.text("connector-heading", "RJ45 / NO MAGNETICS", 355.6, 39.37, 1.6, bold=True)
    s.place("J1", 337.82, 69.85, (337.82, 46.99), (355.6, 104.14), size=1.15)
    pins = {1: "DA_P", 2: "DA_N", 3: "DB_P", 4: "DC_P", 5: "DC_N", 6: "DB_N", 7: "DD_P", 8: "DD_N"}
    for pin, net in pins.items():
        y = 77.47 - (pin - 1) * 2.54
        s.wire(f"J1:{pin}:wire", 347.98, y, 368.3, y)
        s.label(f"J1:{pin}:label", net, 368.3, y)
    s.wire("J1:shield-wire", 337.82, 82.55, 337.82, 92.71)
    s.label("J1:shield-label", "SHIELD", 337.82, 92.71)
    s.text("connector-note", "Component pin numbers, not a mating-face drawing.", 355.6, 112.395, 1.0)
    s.text("shield-heading", "SHIELD OPTIONS / TEST POINTS", 355.6, 129.54, 1.45, bold=True)
    for ref, y in (("RSH1", 151.13), ("CSH1", 176.53)):
        s.place(ref, 355.6, y, (355.6, y - 10.16), (355.6, y - 6.35), rotation=270)
        s.wire(f"{ref}:shield-wire", 330.2, y, 351.79, y)
        s.label(f"{ref}:shield-label", "SHIELD", 330.2, y)
        s.wire(f"{ref}:ground-wire", 359.41, y, 381, y)
        s.label(f"{ref}:ground-label", "GND", 381, y)
        s.text(f"{ref}:dnp", "DNP IN COMMON CAD" if ref == "RSH1" else "OPTIONAL AC BOND / DNP", 355.6, y + 7.62, 1.1)
    for ref, x, net in (("TP1", 332.74, "GND"), ("TP2", 375.92, "SHIELD")):
        s.place(ref, x, 209.55, (x + 10.16, 201.93), (x + 10.16, 205.74), size=1.1)
        s.wire(ref + ":wire", x, 209.55, x, 217.17)
        s.label(ref + ":net", net, x, 217.17, 1.1)
    s.text("variant-note", "PCBA: SHIELD-BONDED / SHIELD-FLOAT variants.", 355.6, 233.68, 1.15)
    s.text("variant-note2", "Supplier fits RSH1 only on the BONDED boards.", 355.6, 239.395, 1.15)
    s.line("notes-rule", 17.78, 190.5, 299.72, 190.5)
    s.text("notes-heading", "ASSEMBLY / MEASUREMENT NOTES", 20.32, 196.215, 1.6, left=True, bold=True)
    notes = [
        "1. Passive DUT only. Disconnect PoE and all active Ethernet equipment before connecting the VNA.",
        "2. Two identical PCB artworks; measure one path at a time and terminate all six unused SMA ports with 50 ohm loads.",
        "3. RCT1..RCT4 are DNP on this board. The default comparison condition is CT-FLOAT on both endpoint boards.",
        "4. CT-GND is a separate controlled comparison: fit all eight RCTs across two boards; do not mix CT states.",
        "5. This common CAD keeps RSH1 and CSH1 DNP. Final PCBA variants follow PCBA_PURCHASE_SCOPE_2026-09-03.md.",
        "6. RSH1 fitted = direct shield bond; CSH1 alone = optional AC bond; both DNP = floating. Never fit both together.",
        "7. Final shield variants are assembled by the supplier; legacy hand-fit property text is not a user soldering instruction.",
        "8. Coax O/S/L + THRU calibration leaves the PCB / balun response embedded. Keep REF/DUT fixture conditions fixed.",
        "9. Secondary convention P=pin 4, N=pin 6 is unchanged. Account for single-fixture polarity in phase/de-embedding work.",
        "10. No TVS, common-mode choke, MagJack, series capacitors or on-board 50 ohm loads are added to the signal paths.",
    ]
    for i, note in enumerate(notes):
        s.text(f"note:{i}", note, 20.32, 203.2 + i * 5.08, 1.45, left=True)
    return s.finish("A3", "RJ45 / FOUR-PAIR VNA FIXTURE", [
        "50 ohm coax / 100 ohm differential; CT-FLOAT baseline.",
        "Layout-only refresh; circuit / PCB / DNP states unchanged.",
        "Common CAD is not both PCBA shield assembly variants.",
    ])


def render_schematic(source: str, variant: str) -> str:
    if variant == "rj45":
        return rj45(source)
    if variant in ("molex", "m12"):
        return slipring(source, variant)
    raise ValueError(variant)
