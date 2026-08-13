"""Archived Rev-A generator for the four-pair RJ45 VNA fixture.

This file predates the validated JLCPCB Rev-B stack and routing.  It is kept
only as construction history.  Running it overwrites the current PCB.

To intentionally regenerate the obsolete Rev-A board, pass --force-rev-a.
"""

from pathlib import Path
import json
import sys

if "--force-rev-a" not in sys.argv:
    raise SystemExit(
        "REFUSED: generate_pcb.py is the archived Rev-A generator and would "
        "overwrite the validated Rev-B PCB.  Use the checked-in .kicad_pcb; "
        "pass --force-rev-a only when intentionally recreating Rev A."
    )

import pcbnew


HERE = Path(__file__).resolve().parent
OUT = HERE / "balun_eth_rj45.kicad_pcb"
PROJECT = HERE / "balun_eth_rj45.kicad_pro"
KICAD_FP = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")
LOCAL_FP = HERE / "balun_eth_rj45.pretty"


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
title_block = board.GetTitleBlock()
title_block.SetTitle("4-pair RJ45 VNA fixture, 50 ohm SE to 100 ohm differential")
title_block.SetRevision("A")
title_block.SetDate("2026-08-12")
title_block.SetComment(0, "Use two identical boards; unused SMA ports require 50 ohm loads.")
title_block.SetComment(1, "PASSIVE DUT ONLY - NO PoE / NO ACTIVE ETHERNET.")
title_block.SetComment(2, "Confirm 50/100 ohm geometry with the selected PCB fabricator.")
settings = board.GetDesignSettings()
settings.SetBoardThickness(mm(1.50))
settings.m_MinClearance = mm(0.20)
settings.m_TrackMinWidth = mm(0.20)
settings.m_ViasMinSize = mm(0.60)
settings.m_MinThroughDrill = mm(0.30)
settings.m_ViasMinAnnularWidth = mm(0.15)
settings.m_HoleToHoleMin = mm(0.25)
# Edge-launch SMA signal/ground pads intentionally reach the routed edge.
settings.m_CopperEdgeClearance = mm(0.00)
settings.m_SilkClearance = mm(0.15)


# Net names and numbers deliberately follow the schematic netlist.
net_names = [
    "/DA_N", "/DA_P", "/DB_N", "/DB_P",
    "/DC_N", "/DC_P", "/DD_N", "/DD_P",
    "/GND", "/SHIELD",
    "Net-(J2-In)", "Net-(J3-In)", "Net-(J4-In)", "Net-(J5-In)",
    "Net-(RCT1-Pad2)", "Net-(RCT2-Pad2)",
    "Net-(RCT3-Pad2)", "Net-(RCT4-Pad2)",
    "unconnected-(T1-Pad2)", "unconnected-(T2-Pad2)",
    "unconnected-(T3-Pad2)", "unconnected-(T4-Pad2)",
]
nets = {}
for name in net_names:
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    nets[name] = net


uuids = {
    "CSH1": "7cf4fcff-a207-4f12-bc92-15c4fe48e4b0",
    "J1": "c90a94df-e9ee-45f6-b1d7-4b74a33307ae",
    "J2": "8e378d3d-a99e-457d-9c59-3d43592cb06c",
    "J3": "25613112-a452-492a-8609-e1f92fc9c315",
    "J4": "b1b64237-bca9-41c2-82e8-19ec90b6aa86",
    "J5": "7eca8feb-7c14-4408-aa5e-29a4a440a94d",
    "RCT1": "ac3341d4-1abb-4680-b570-095e6910fe92",
    "RCT2": "fd97f624-74df-4217-ada2-078a1ac3e649",
    "RCT3": "e2362941-3367-4e3c-85ab-f564ddfd5b52",
    "RCT4": "cb431d9a-a979-485f-ae28-a61e95254633",
    "RSH1": "f5587d21-0f0e-4681-9d3f-ba08795220a9",
    "T1": "cd8bc015-c5d9-4064-a3bd-ecad8524d249",
    "T2": "eecb38d9-6984-45f0-b45d-cf8ac82a28a2",
    "T3": "f2b231db-9c40-4d7f-9fd5-0fa66307e7ae",
    "T4": "747097a2-6f30-4594-bbe8-5012f2aa7731",
    "TP1": "1d9fcd7c-1612-4458-b5c3-61bac8a1d533",
    "TP2": "a8c10948-89d6-4667-b279-f21b69766629",
}


def load_footprint(library, name, reference, value, x, y, rotation=0,
                   flipped=False, board_only=False, dnp=False,
                   properties=None):
    if library == "balun_eth_rj45":
        path = LOCAL_FP
    else:
        path = KICAD_FP / f"{library}.pretty"
    footprint = pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(str(path), name, False)
    if footprint is None:
        raise RuntimeError(f"Could not load {library}:{name}")
    footprint.SetReference(reference)
    footprint.SetValue(value)
    footprint.SetFPIDAsString(f"{library}:{name}")
    if reference in uuids:
        footprint.SetPath(pcbnew.KIID_PATH("/" + uuids[reference]))
    footprint.SetPosition(point(x, y))
    footprint.SetOrientationDegrees(rotation)
    footprint.Value().SetVisible(False)
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
    return footprint


footprints = {}
footprints["J1"] = load_footprint(
    "balun_eth_rj45", "RJ45_Amphenol_RJE59-188-5401", "J1",
    "RJE591885401 CAT6 NO-MAGNETICS", 30.43, 57.00, 90,
    properties={
        "Manufacturer": "Amphenol Communications Solutions",
        "MPN": "RJE591885401", "LCSC Part #": "C5386678",
        "Assembly": "FIT",
        "Datasheet": "https://www.amphenol-cs.com/product/rje591885401.html",
        "Description": "",
    },
)

channel_y = [29.0, 47.0, 65.0, 83.0]
# Physical top-to-bottom order follows the RJ45 pin field.  This avoids
# crossing the long differential runs; reference designators still retain
# their electrical A/B/C/D identity.
channels = [
    ("A", "1-2", 1, "J2", "T1", "RCT1", 29.0),
    ("B", "3-6", 2, "J3", "T2", "RCT2", 47.0),
    ("C", "4-5", 3, "J4", "T3", "RCT3", 65.0),
    ("D", "7-8", 4, "J5", "T4", "RCT4", 83.0),
]
for label, _pair, index, jref, tref, rref, y in channels:
    footprints[jref] = load_footprint(
        "balun_eth_rj45", "SMA_MyAntenna_A-SMA-KE-16.5A_EdgeMount",
        jref, f"SMA_{label}", 97.75, y,
        properties={
            "Manufacturer": "MyAntenna", "MPN": "A-SMA-KE-16.5A",
            "LCSC Part #": "C22467617", "Assembly": "FIT; JLC C22467617; Standard PCBA / wave-solder review",
            "Datasheet": "https://datasheet.lcsc.com/datasheet/pdf/92633ab2cf30de4413e1a152c04a3ed5.pdf?productCode=C22467617",
        },
    )
    footprints[tref] = load_footprint(
        "RF_Mini-Circuits", "Mini-Circuits_CD542_H2.84mm",
        tref, "ADT2-1T+", 65.50, y, 180,
        properties={
            "Manufacturer": "Mini-Circuits", "MPN": "ADT2-1T+",
            "LCSC Part #": "C5223988", "Assembly": "FIT",
            "Datasheet": "https://www.minicircuits.com/pdfs/ADT2-1T+.pdf",
        },
    )
    footprints[rref] = load_footprint(
        "Resistor_SMD", "R_0805_2012Metric_Pad1.20x1.40mm_HandSolder",
        rref, "0R", 59.00, y, flipped=(index != 2), dnp=True,
        properties={
            "Manufacturer": "ANY", "MPN": "0 ohm 0805",
            "LCSC Part #": "C17477",
            "Assembly": "DNP DEFAULT; fit all eight only for CT-GND comparison",
        },
    )

footprints["RSH1"] = load_footprint(
    "Resistor_SMD", "R_0805_2012Metric_Pad1.20x1.40mm_HandSolder",
    "RSH1", "0R", 31.00, 46.50, 270, dnp=True,
    properties={"Assembly": "DNP DEFAULT; hand-fit on Port-1 board only", "LCSC Part #": "C17477"},
)
footprints["CSH1"] = load_footprint(
    "Capacitor_SMD", "C_1206_3216Metric_Pad1.33x1.80mm_HandSolder",
    "CSH1", "1nF 2kV DNP", 31.00, 68.30, 90, dnp=True,
    properties={"Assembly": "DNP; fit only after removing RSH1"},
)
footprints["TP1"] = load_footprint(
    "TestPoint", "TestPoint_Loop_D2.50mm_Drill1.0mm",
    "TP1", "GND_RF", 43.00, 23.50,
    properties={"LCSC Part #": "C238122", "Assembly": "FIT"},
)
footprints["TP2"] = load_footprint(
    "TestPoint", "TestPoint_Loop_D2.50mm_Drill1.0mm",
    "TP2", "RJ45_SHIELD", 25.00, 72.00,
    properties={"LCSC Part #": "C238122", "Assembly": "FIT"},
)

for index, (x, y) in enumerate(((25, 25), (25, 89), (86, 23.5), (86, 90.5)), start=1):
    ref = f"H{index}"
    footprints[ref] = load_footprint(
        "MountingHole", "MountingHole_3.2mm_M3", ref, "M3", x, y,
        board_only=True,
    )
    footprints[ref].Reference().SetVisible(False)


# Assign every schematic pad to the corresponding net.
connections = {
    "/DA_N": (("J1", "2"), ("T1", "6")),
    "/DA_P": (("J1", "1"), ("T1", "4")),
    "/DB_N": (("J1", "6"), ("T2", "6")),
    "/DB_P": (("J1", "3"), ("T2", "4")),
    "/DC_N": (("J1", "5"), ("T3", "6")),
    "/DC_P": (("J1", "4"), ("T3", "4")),
    "/DD_N": (("J1", "8"), ("T4", "6")),
    "/DD_P": (("J1", "7"), ("T4", "4")),
    "/GND": (
        ("CSH1", "1"), ("J2", "2"), ("J3", "2"),
        ("J4", "2"), ("J5", "2"),
        ("RCT1", "1"), ("RCT2", "1"), ("RCT3", "1"), ("RCT4", "1"),
        ("RSH1", "1"),
        ("T1", "1"), ("T2", "1"), ("T3", "1"), ("T4", "1"),
        ("TP1", "1"),
    ),
    "/SHIELD": (("CSH1", "2"), ("J1", "SH"), ("RSH1", "2"), ("TP2", "1")),
    "Net-(J2-In)": (("J2", "1"), ("T1", "3")),
    "Net-(J3-In)": (("J3", "1"), ("T2", "3")),
    "Net-(J4-In)": (("J4", "1"), ("T3", "3")),
    "Net-(J5-In)": (("J5", "1"), ("T4", "3")),
    "Net-(RCT1-Pad2)": (("RCT1", "2"), ("T1", "5")),
    "Net-(RCT2-Pad2)": (("RCT2", "2"), ("T2", "5")),
    "Net-(RCT3-Pad2)": (("RCT3", "2"), ("T3", "5")),
    "Net-(RCT4-Pad2)": (("RCT4", "2"), ("T4", "5")),
    "unconnected-(T1-Pad2)": (("T1", "2"),),
    "unconnected-(T2-Pad2)": (("T2", "2"),),
    "unconnected-(T3-Pad2)": (("T3", "2"),),
    "unconnected-(T4-Pad2)": (("T4", "2"),),
}
for net_name, node_list in connections.items():
    for reference, pad_number in node_list:
        matching = [pad for pad in footprints[reference].Pads() if pad.GetNumber() == pad_number]
        if not matching:
            raise RuntimeError(f"Missing pad {reference}.{pad_number}")
        for pad in matching:
            pad.SetNet(nets[net_name])


def add_segment(start, end, width, layer, net_name):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(point(*start))
    track.SetEnd(point(*end))
    track.SetWidth(mm(width))
    track.SetLayer(layer)
    track.SetNet(nets[net_name])
    board.Add(track)
    return track


def add_polyline(vertices, width, layer, net_name):
    for start, end in zip(vertices, vertices[1:]):
        add_segment(start, end, width, layer, net_name)


def add_via(x, y, net_name, diameter=0.60, drill=0.30):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(x, y))
    via.SetWidth(mm(diameter))
    via.SetDrill(mm(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(nets[net_name])
    board.Add(via)
    return via


def add_shape(start, end, layer=pcbnew.Edge_Cuts, width=0.05):
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetStart(point(*start))
    shape.SetEnd(point(*end))
    shape.SetLayer(layer)
    shape.SetWidth(mm(width))
    board.Add(shape)


def add_text(text_value, x, y, layer=pcbnew.F_SilkS, size=1.10,
             thickness=0.18, angle=0):
    text_item = pcbnew.PCB_TEXT(board)
    text_item.SetText(text_value)
    text_item.SetPosition(point(x, y))
    text_item.SetLayer(layer)
    text_item.SetTextSize(point(size, size))
    text_item.SetTextThickness(mm(thickness))
    text_item.SetTextAngleDegrees(angle)
    if layer in (pcbnew.B_SilkS, pcbnew.B_Fab):
        text_item.SetMirrored(True)
    board.Add(text_item)
    return text_item


# 80 x 74 mm outline with 2 mm chamfers.  The RJ45 mating face and SMA
# launch reference planes lie exactly on the left and right board edges.
outline = [
    (22, 20), (98, 20), (100, 22), (100, 92),
    (98, 94), (22, 94), (20, 92), (20, 22), (22, 20),
]
for start, end in zip(outline, outline[1:]):
    add_shape(start, end)


# 100 ohm differential-side routes.  A/C/D stay on F.Cu.  Pair B is kept
# together on B.Cu through the RJ45 3-6 / 4-5 escape and returns to F.Cu
# immediately before T2.  Nominal P/N centreline lengths are matched.
diff_routes = {
    "/DA_P": (pcbnew.F_Cu, [
        (35.43, 53.39), (36.50, 52.32), (38.50, 52.32), (41.50, 50.39),
        (51.50, 28.775), (56.00, 28.775), (59.00, 26.46), (62.96, 26.46),
    ]),
    "/DA_N": (pcbnew.F_Cu, [
        (37.46, 54.41), (39.50, 54.41), (42.50, 51.41),
        (52.50, 29.225), (53.00, 29.225), (53.00, 29.86465),
        (54.00, 29.86465), (54.00, 29.225), (56.00, 29.225),
        (59.00, 31.54), (62.96, 31.54),
    ]),
    "/DB_P": (pcbnew.B_Cu, [
        (35.43, 55.43), (33.00, 55.43), (33.00, 52.00), (42.00, 52.00),
        (48.00, 46.775), (58.00, 46.775), (60.50, 44.46),
    ]),
    "/DB_N": (pcbnew.B_Cu, [
        (37.46, 58.49), (40.50, 58.49), (44.00, 55.00),
        (49.00, 47.225), (51.00, 47.225), (51.00, 50.51975),
        (53.00, 50.51975), (53.00, 47.225), (58.00, 47.225),
        (60.50, 49.54),
    ]),
    "/DC_P": (pcbnew.B_Cu, [
        (37.46, 56.45), (39.50, 56.45),
    ]),
    "/DC_N": (pcbnew.B_Cu, [
        (35.43, 57.47), (32.70, 57.47), (32.70, 66.00),
    ]),
    "/DD_P": (pcbnew.B_Cu, [
        (35.43, 59.51), (34.00, 59.51), (34.00, 70.50), (43.00, 70.50),
    ]),
    "/DD_N": (pcbnew.B_Cu, [
        (37.46, 60.53), (40.00, 60.53), (46.00, 64.50), (46.00, 74.50),
    ]),
}
for net_name, (layer, vertices) in diff_routes.items():
    # A 0.20 mm neck at the staggered RJ45 pin field preserves the 0.20 mm
    # clearance between 1.60 mm PTH pads; the controlled section is 0.25 mm.
    add_segment(vertices[0], vertices[1], 0.20, layer, net_name)
    add_polyline(vertices[1:], 0.25, layer, net_name)

# Return the C/D escape traces to F.Cu as matched via pairs.
add_via(39.50, 56.45, "/DC_P")
add_polyline([
    (39.50, 56.45), (42.50, 59.45), (50.50, 64.775), (50.80, 64.775),
    (50.80, 62.57547), (51.50, 62.57547), (51.50, 64.775),
    (52.00, 64.775), (52.00, 62.57547), (52.70, 62.57547),
    (52.70, 64.775), (53.20, 64.775), (53.20, 62.57547),
    (53.90, 62.57547), (53.90, 64.775), (56.00, 64.775),
    (59.00, 62.46), (62.96, 62.46),
], 0.25, pcbnew.F_Cu, "/DC_P")
add_via(32.70, 66.00, "/DC_N")
add_polyline([
    (32.70, 66.00), (40.00, 66.00), (50.00, 65.225), (56.00, 65.225),
    (59.00, 67.54), (62.96, 67.54),
], 0.25, pcbnew.F_Cu, "/DC_N")
add_via(43.00, 70.50, "/DD_P")
add_polyline([
    (43.00, 70.50), (49.00, 76.50), (56.00, 82.775),
    (59.00, 80.46), (62.96, 80.46),
], 0.25, pcbnew.F_Cu, "/DD_P")
add_via(46.00, 74.50, "/DD_N")
add_polyline([
    (46.00, 74.50), (51.00, 79.50), (56.00, 84.00),
    (59.00, 85.54), (59.50, 85.54), (59.50, 88.63545),
    (61.00, 88.63545), (61.00, 85.54), (62.96, 85.54),
], 0.25, pcbnew.F_Cu, "/DD_N")

# Pair B layer changes are symmetrical and tightly surrounded by return vias.
for net_name, y in (("/DB_P", 44.46), ("/DB_N", 49.54)):
    add_via(60.50, y, net_name)
    add_segment((60.50, y), (62.96, y), 0.25, pcbnew.F_Cu, net_name)


# 50 ohm single-ended launches.  The narrow middle section is the nominal
# 0.35 mm controlled-impedance line; widths broaden only at large pads.
for _label, _pair, index, jref, _tref, _rref, y in channels:
    net_name = f"Net-({jref}-In)"
    add_segment((97.75, y), (95.00, y), 0.35, pcbnew.F_Cu, net_name)
    add_segment((95.00, y), (94.00, y), 0.35, pcbnew.F_Cu, net_name)
    add_segment((94.00, y), (91.46, y - 2.54), 0.35, pcbnew.F_Cu, net_name)
    add_segment((91.46, y - 2.54), (69.54, y - 2.54), 0.35, pcbnew.F_Cu, net_name)
    add_segment((69.54, y - 2.54), (68.04, y - 2.54), 0.55, pcbnew.F_Cu, net_name)


# Optional centre-tap grounding paths are retained even though RCT1-RCT4 are
# DNP by default.  Three are on B.Cu to leave the matched pairs undisturbed;
# T2/RCT2 stays on F.Cu because pair B is below it.  Populate all eight RCTs
# across both fixture boards only for a controlled CT-GND comparison.
for _label, _pair, index, _jref, _tref, rref, y in channels:
    net_name = f"Net-({rref}-Pad2)"
    if index == 2:
        add_segment((62.96, y), (60.00, y), 0.30, pcbnew.F_Cu, net_name)
    else:
        add_segment((62.96, y), (61.00, y), 0.30, pcbnew.F_Cu, net_name)
        add_via(61.00, y, net_name)
        add_segment((61.00, y), (60.00, y), 0.30, pcbnew.B_Cu, net_name)


# RJ45 shield is intentionally distinct from RF GND and joined by RSH1.
shield_routes = [
    [(26.97, 49.06), (23.50, 49.06), (23.50, 64.94), (26.97, 64.94)],
    [(26.97, 49.06), (29.00, 49.06), (31.00, 47.50)],
    [(26.97, 64.94), (29.00, 64.94), (31.00, 66.7375)],
    [(23.50, 64.94), (23.50, 72.00), (25.00, 72.00)],
]
for vertices in shield_routes:
    add_polyline(vertices, 0.80, pcbnew.F_Cu, "/SHIELD")


# Explicit local GND ties plus stitching vias; the four copper pours provide
# the remaining ground connections.
add_segment((31.00, 45.50), (31.00, 43.50), 0.80, pcbnew.F_Cu, "/GND")
add_via(31.00, 43.50, "/GND")
add_segment((31.00, 69.8625), (31.00, 72.00), 0.80, pcbnew.F_Cu, "/GND")
add_via(31.00, 72.00, "/GND")
# If optional RCT2 is populated, its ground end needs an unambiguous local
# plane connection instead of the small F.Cu island enclosed by pair B.
add_segment((58.00, 47.00), (57.00, 44.00), 0.50, pcbnew.F_Cu, "/GND")
add_via(57.00, 44.00, "/GND")

for y in channel_y:
    # Transformer primary-return vias.
    add_segment((68.04, y + 2.54), (70.20, y + 2.54), 0.80, pcbnew.F_Cu, "/GND")
    add_via(70.20, y + 2.54, "/GND")
    add_via(68.04, y + 4.40, "/GND")
    # SMA ground paddle stitching at both sides of each launch.
    for sy in (y - 2.825, y + 2.825):
        add_segment((97.75, sy), (94.20, sy), 0.80, pcbnew.F_Cu, "/GND")
        add_segment((97.75, sy), (94.20, sy), 0.80, pcbnew.B_Cu, "/GND")
        add_via(94.20, sy, "/GND")
        add_via(92.60, sy, "/GND")

# Pair-B transition return vias.  Each GND via is 1.355 mm centre-to-centre
# from its associated signal via, mirrored about x=60.5 and y=47.0.  Keep the
# GND vias outside the P/N gap so the differential field is not split.
for x, y in ((60.0, 43.2), (61.0, 43.2), (60.0, 50.8), (61.0, 50.8)):
    add_via(x, y, "/GND")

# Return-current stitching for the C/D layer transitions.
for x, y in ((40.5, 54.8), (35.5, 68.5), (42.0, 73.5), (47.5, 72.0)):
    add_via(x, y, "/GND")

# General stitching along the board perimeter and between SMA channels.
stitch_points = []
for x in (30, 38, 46, 54, 62, 72, 80, 90):
    stitch_points.extend(((x, 22.5), (x, 91.5)))
for y in (29, 38, 47, 56, 65, 74, 83):
    stitch_points.append((22.5, y))
for y in (38, 56, 74):
    for x in (73, 77, 81, 85, 89):
        stitch_points.append((x, y))
for x, y in stitch_points:
    add_via(x, y, "/GND")


def add_ground_zone(layer):
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(nets["/GND"])
    zone.SetLocalClearance(mm(0.25))
    zone.SetMinThickness(mm(0.20))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    zone.SetMinIslandArea(mm(2.0) * mm(2.0))
    vertices = [
        (22.10, 20.30), (97.90, 20.30), (99.70, 22.10), (99.70, 91.90),
        (97.90, 93.70), (22.10, 93.70), (20.30, 91.90), (20.30, 22.10),
    ]
    for x, y in vertices:
        zone.AppendCorner(point(x, y), -1)
    board.Add(zone)
    return zone


for copper_layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
    add_ground_zone(copper_layer)


# Keep the fabrication/usage constraints visible on the physical fixture.
add_text("BALUN ETH RJ45  REV A", 61.0, 22.1, size=1.20, thickness=0.20)
add_text("PASSIVE DUT ONLY - NO PoE", 54.0, 91.8, size=1.00, thickness=0.17)
add_text("UNUSED SMA -> 50R LOAD", 74.0, 93.0, pcbnew.B_SilkS, 0.90, 0.15)
add_text("SH", 27.5, 69.7, size=0.90, thickness=0.15)
add_text("GND", 40.0, 27.0, size=0.90, thickness=0.15)
for label, pair_name, _index, _jref, _tref, _rref, y in channels:
    add_text(f"{label} {pair_name}", 88.5, y + 3.1, size=0.95, thickness=0.16)

# Assembly notes live on User.Comments so they do not print on the PCB.
add_text("STACKUP: 1.50 mm 4L; outer dielectric 0.20 mm nominal",
         55.0, 97.0, pcbnew.Cmts_User, 1.00, 0.15)
add_text("VERIFY 50R/100R WIDTHS WITH FAB STACKUP BEFORE ORDER",
         55.0, 99.0, pcbnew.Cmts_User, 1.00, 0.15)


# Make references compact and readable; values remain on fabrication layers.
reference_positions = {
    "J1": (42.5, 57.0, 90),
    "J2": (91.5, 23.8, 0), "J3": (91.5, 41.8, 0),
    "J4": (91.5, 59.8, 0), "J5": (91.5, 77.8, 0),
    "T1": (65.5, 23.7, 0), "T2": (65.5, 41.7, 0),
    "T3": (65.5, 59.7, 0), "T4": (65.5, 77.7, 0),
    "RCT1": (58.5, 32.0, 0), "RCT2": (58.5, 50.0, 0),
    "RCT3": (58.5, 68.0, 0), "RCT4": (58.5, 86.0, 0),
    "RSH1": (34.5, 45.7, 0), "CSH1": (35.0, 69.0, 0),
    "TP1": (44.5, 25.8, 0), "TP2": (25.0, 74.5, 0),
}
for reference, (x, y, angle) in reference_positions.items():
    ref_text = footprints[reference].Reference()
    ref_text.SetPosition(point(x, y))
    ref_text.SetTextAngleDegrees(angle)
    ref_text.SetTextSize(point(0.90, 0.90))
    ref_text.SetTextThickness(mm(0.15))


pcbnew.SaveBoard(str(OUT), board)

# pcbnew's Python bindings do not currently expose the full physical stack-up
# editor.  Insert the KiCad-native stack-up block after serializing the board.
stackup = """\
\t\t(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen") (color "White"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "prepreg") (thickness 0.2)
\t\t\t\t(material "FR4") (epsilon_r 4.2) (loss_tangent 0.02))
\t\t\t(layer "In1.Cu" (type "copper") (thickness 0.018))
\t\t\t(layer "dielectric 2" (type "core") (thickness 0.994)
\t\t\t\t(material "FR4") (epsilon_r 4.2) (loss_tangent 0.02))
\t\t\t(layer "In2.Cu" (type "copper") (thickness 0.018))
\t\t\t(layer "dielectric 3" (type "prepreg") (thickness 0.2)
\t\t\t\t(material "FR4") (epsilon_r 4.2) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
\t\t\t(copper_finish "ENIG")
\t\t\t(dielectric_constraints yes)
\t\t)
"""
board_text = OUT.read_text(encoding="utf-8")
setup_marker = "\t(setup\n"
if setup_marker not in board_text:
    raise RuntimeError("Could not locate the KiCad setup block for stack-up insertion")
OUT.write_text(board_text.replace(setup_marker, setup_marker + stackup, 1), encoding="utf-8")

# Keep the editor defaults synchronized with the routed geometry.  KiCad can
# rewrite project settings when an older PCB Editor window is still open, so
# the generator deliberately restores these values after writing the board.
project_data = json.loads(PROJECT.read_text(encoding="utf-8"))
design_settings = project_data["board"]["design_settings"]
design_settings["diff_pair_dimensions"] = [
    {"gap": 0.2, "via_gap": 0.25, "width": 0.25}
]
design_settings["track_widths"] = [0.25, 0.35, 0.55, 0.8]

net_settings = project_data["net_settings"]
default_class = next(c for c in net_settings["classes"] if c["name"] == "Default")

def project_netclass(name, track_width, clearance, priority, color):
    result = dict(default_class)
    result.update({
        "name": name,
        "track_width": track_width,
        "clearance": clearance,
        "diff_pair_width": 0.25,
        "diff_pair_gap": 0.2,
        "diff_pair_via_gap": 0.25,
        "priority": priority,
        "pcb_color": color,
        "schematic_color": color,
    })
    return result

net_settings["classes"] = [
    default_class,
    project_netclass("ETH100", 0.25, 0.20, 1, "rgba(0, 102, 204, 0.000)"),
    project_netclass("RF50", 0.35, 0.25, 2, "rgba(204, 51, 0, 0.000)"),
]
net_settings["netclass_patterns"] = [
    *({"netclass": "ETH100", "pattern": f"/D{pair}_{pol}"}
      for pair in "ABCD" for pol in "PN"),
    *({"netclass": "RF50", "pattern": f"Net-(J{ref}-In)"}
      for ref in range(2, 6)),
]
PROJECT.write_text(json.dumps(project_data, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")

print(f"Generated {OUT}")
print(f"Footprints: {len(board.GetFootprints())}")
print(f"Tracks/vias: {len(board.GetTracks())}")
print(f"Zones: {len(board.Zones())}")
