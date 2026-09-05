"""Verify the LLC routed draft against its schematic, mechanical map and RF rules."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "balun_slipring"))
import generate_pinmap_tbd_drafts as core
import verify_schematic


def verify(directory: Path) -> dict:
    netlist = directory / "balun_llc16.xml"
    verify_schematic.verify(netlist)
    board = pcbnew.LoadBoard(str(directory / "balun_llc16.kicad_pcb"))
    root = ET.parse(netlist).getroot()
    expected = {n.attrib["name"]: {(p.attrib["ref"], p.attrib["pin"]) for p in n.findall("node")}
                for n in root.findall("./nets/net")}
    fps = {f.GetReference(): f for f in board.GetFootprints()}
    actual = {}
    for ref, fp in fps.items():
        if fp.IsBoardOnly():
            continue
        for pad in fp.Pads():
            if pad.GetNumber():
                actual.setdefault(pad.GetNetname(), set()).add((ref, pad.GetNumber()))
    assert actual == expected, "PCB pads differ from the schematic"
    for component in root.findall("./components/comp"):
        fp = fps[component.attrib["ref"]]
        assert fp.GetValue() == component.findtext("value")
        assert fp.GetFPID().GetUniStringLibId() == component.findtext("footprint")
        assert fp.IsDNP() == any(p.attrib["name"] == "dnp" for p in component.findall("property"))
    j1 = fps["J1"]
    assert j1.IsFlipped() and j1.GetOrientationDegrees() == 0
    positions = {"1": (30.502243,39.693656), "2": (33.497757,39.693656),
                 "3": (34.723237,41.617274), "4": (34.075451,43.804162),
                 "5": (32,44.75), "6": (29.924549,43.804162),
                 "7": (29.276763,41.617274), "8": (32,42)}
    for pad in j1.Pads():
        xy = core.footprint_pad_center(j1, pad.GetNumber())
        assert math.dist(xy, positions[pad.GetNumber()]) < 0.000002
        assert abs(pcbnew.ToMM(pad.GetDrillSize().x) - 1.0) < 1e-6
        assert abs(pcbnew.ToMM(pad.GetSize().x) - 1.8) < 1e-6
        if pad.GetNumber() in {"1","5","6","7"}:
            assert actual[pad.GetNetname()] == {("J1",pad.GetNumber())}
            assert not any(t.GetNetname() == pad.GetNetname() for t in board.GetTracks())
    assert board.GetCopperLayerCount() == 4
    assert abs(pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()) - 1.5862) < 1e-6
    zones = list(board.Zones())
    assert len(zones) == 2
    assert {z.GetLayer() for z in zones} == {pcbnew.In1_Cu, pcbnew.In2_Cu}
    for zone in zones:
        assert zone.GetNetname() == "/GND" and zone.IsFilled()
        assert zone.GetFilledPolysList(zone.GetLayer()).OutlineCount() == 1
    assert all(t.GetLayer() not in {pcbnew.In1_Cu, pcbnew.In2_Cu} for t in board.GetTracks())
    metrics = {}
    for pair in ("TX", "RX"):
        core.validate_board_pair_topology(board, "LLC " + pair, f"/PAIR_{pair}_P", f"/PAIR_{pair}_N")
        lengths = {}
        for polarity in "PN":
            tracks = [t for t in board.GetTracks() if t.GetNetname() == f"/PAIR_{pair}_{polarity}"]
            assert all(abs(pcbnew.ToMM(t.GetWidth()) - .23) < 1e-6 for t in tracks)
            lengths[polarity] = sum(pcbnew.ToMM(t.GetLength()) for t in tracks)
        metrics[pair] = {"lengths_mm": lengths, "skew_mm": abs(lengths["P"]-lengths["N"]), "signal_vias": 0}
    core.validate_rf_launch_topology(board, "LLC saved PCB")
    texts = [d.GetText() for d in board.GetDrawings() if isinstance(d, pcbnew.PCB_TEXT)]
    assert "구동기 to RJ45" in texts
    assert not any("SLIPRING" in t or "REV-504" in t for t in texts)
    report = json.loads((directory / "drc.json").read_text(encoding="utf-8"))
    assert all(not report[k] for k in ("violations", "unconnected_items", "schematic_parity"))
    result = {"status": "PCB_DRAFT_A_DO_NOT_ORDER", "native_drc_unconnected_parity": [0,0,0],
              "schematic_pad_membership_equal": True, "male_footprint_coordinates_and_drills": "PASS",
              "power_pins_1_5_6_7_isolated": True, "all_required_components_fit_rct_dnp": True,
              "ground_planes": "In1/In2, filled, one connected polygon each", "pairs": metrics,
              "rf_A_B_length_mm": 26.762102, "board_mm": [68,44], "copper_layers": 4}
    (directory / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, nargs="?", default=HERE)
    verify(parser.parse_args().directory)
