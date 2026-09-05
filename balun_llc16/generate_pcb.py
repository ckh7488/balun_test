"""Create the LLC-specific routed PCB from its native schematic netlist.

Reuse only the reviewed slip-ring RF launches, ground geometry, stack and outline.
Replace J1 and all four pair routes; assign ALL pad nets from the LLC schematic.
Output defaults to a review staging directory. Never overwrite a PCB silently.
First run generate_schematic.py into the same staging directory. Run with KiCad
10 Python; native CLI zone refill / ERC / DRC / parity are performed automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "balun_slipring"))
import generate_pinmap_tbd_drafts as core
import verify_schematic

PROJECT = "balun_llc16"
SOURCE = HERE.parent / "balun_slipring/m12_end/balun_slipring_m12"
DEFAULT = HERE.parents[1] / "outputs/balun-llc16-pcb-20260903/stage"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def settings(directory: Path) -> None:
    data = json.loads(SOURCE.with_suffix(".kicad_pro").read_text(encoding="utf-8"))
    data = core.recursively_replace(data, "balun_slipring_m12", PROJECT)
    data["text_variables"] = {"FIXTURE_USE": "구동기 to RJ45", "RELEASE_STATUS": "PCB DRAFT A - DO NOT ORDER"}
    (directory / f"{PROJECT}.kicad_pro").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rules = SOURCE.with_suffix(".kicad_dru").read_text(encoding="utf-8")
    rules = re.sub(r"# Document-mapped DRAFT 1\..*?# connector mechanics remain fabrication blockers\.",
                   "# LLC PCB DRAFT A. Source: LLC-13M-1 numeric pin map.\n# JLC04161H-7628; male M12 panel support / sourcing / SMA thickness HOLD.", rules, flags=re.S)
    (directory / f"{PROJECT}.kicad_dru").write_text(rules, encoding="utf-8")
    # Staging references actual local libraries, never a guessed relative path.
    table = (HERE / "fp-lib-table").read_text(encoding="utf-8").replace("${KIPRJMOD}", HERE.as_posix())
    (directory / "fp-lib-table").write_text(table, encoding="utf-8")


def solve_pair(board, nets, label, start_p, start_n, end_p, end_n):
    """Balance full P/N lengths with a smooth shared fan-out, not a meander."""
    def paths(tuning):
        if label == "TX":
            center = [(32.225, 38.3), (32.225, 37.2), (34.5, 34.8), (40, 31.5), (45, 31), (49.4, tuning), (50, tuning)]
            lead_p, lead_n = [], []
            fan_p, fan_n = [(52.8, 28.46)], [(52.8, 33.54)]
        else:
            center = [(36.3, 44.5), (38.0, 47.0), (42, 50.5), (46, 53), (48, tuning)]
            lead_p, lead_n = [], []
            fan_p, fan_n = [(49, 51.9), (52.8, 50.46)], [(49, 54.1), (52.8, 55.54)]
        p_trunk, n_trunk = core.offset_polyline(center, -1), core.offset_polyline(center, 1)
        p_path = [start_p, *lead_p, *p_trunk, *fan_p, end_p]
        n_path = [start_n, *lead_n, *n_trunk, *fan_n, end_n]
        return p_path, n_path, p_trunk, n_trunk

    def mismatch(tuning):
        p, n, _, _ = paths(tuning)
        return core.path_length(p) - core.path_length(n)

    mid = 31 if label == "TX" else 53
    probes = [mid - 5 + 0.1 * i for i in range(101)]
    brackets = [(a, b) for a, b in zip(probes, probes[1:]) if mismatch(a) * mismatch(b) <= 0]
    if not brackets:
        raise RuntimeError(f"Cannot balance {label}: " + str([(v, mismatch(v)) for v in (mid-5, mid, mid+5)]))
    low, high = min(brackets, key=lambda pair: abs(sum(pair)/2 - mid))
    for _ in range(50):
        middle = (low + high) / 2
        if mismatch(low) * mismatch(middle) <= 0:
            high = middle
        else:
            low = middle
    tuning = (low + high)/2
    p, n, pt, nt = paths(tuning)
    lp, ln = core.path_length(p), core.path_length(n)
    stats = {"p_mm": lp, "n_mm": ln, "skew_mm": abs(lp-ln),
             "coupled_min_mm": min(core.path_length(pt),core.path_length(nt)),
             "fanout_max_mm": max(lp-core.path_length(pt), ln-core.path_length(nt)),
             "tuning_y": tuning, "signal_vias": 0, "width_mm": 0.23, "gap_mm": 0.22,
             "p_path": p, "n_path": n}
    assert stats["skew_mm"] < 0.001
    assert stats["fanout_max_mm"] < 11.0
    assert stats["coupled_min_mm"] > (20.0 if label == "TX" else 14.0)
    for suffix, vertices in (("P", p), ("N", n)):
        core.add_polyline(board, nets, vertices, 0.23, pcbnew.F_Cu, f"/PAIR_{label}_{suffix}")
    print(label, json.dumps(stats))
    return stats


def build(directory: Path) -> dict:
    exported = ET.parse(directory / f"{PROJECT}.xml").getroot()
    components = {c.attrib["ref"]: c for c in exported.findall("./components/comp")}
    assert components["J1"].findtext("footprint") == "balun_llc16:Finecables_MB12MBAFF08ST-3"
    board = pcbnew.LoadBoard(str(SOURCE.with_suffix(".kicad_pcb")))
    # Remove every inherited signal-pair route and the old FEMALE connector.
    for track in list(board.GetTracks()):
        if track.GetNetname().startswith("/PAIR_"):
            board.Delete(track)
    old_connector = next(f for f in board.GetFootprints() if f.GetReference() == "J1")
    board.Delete(old_connector)
    for drawing in list(board.GetDrawings()):
        if drawing.GetLayer() != pcbnew.Edge_Cuts:
            board.Delete(drawing)
    j1 = pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(str(HERE / "llc16.pretty"), "Finecables_MB12MBAFF08ST-3", False)
    assert j1
    j1.SetReference("J1")
    j1.SetFPIDAsString("balun_llc16:Finecables_MB12MBAFF08ST-3")
    j1.SetPosition(core.point(32, 42))
    board.Add(j1)
    j1.Flip(j1.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    j1.SetOrientationDegrees(0)
    footprints = {f.GetReference(): f for f in board.GetFootprints()}
    for ref, component in components.items():
        fp = footprints[ref]
        fp.SetValue(component.findtext("value"))
        fp.SetPath(pcbnew.KIID_PATH("/" + component.findtext("tstamps")))
        for name, value in [("Datasheet", component.findtext("datasheet") or ""),
                            *((field.attrib["name"], field.text or "") for field in component.findall("./fields/field"))]:
            fp.SetField(name, value)
            fp.GetField(name).SetVisible(False)
        is_dnp = any(p.attrib["name"] == "dnp" for p in component.findall("property"))
        fp.SetDNP(is_dnp)
        fp.SetAttributes((fp.GetAttributes() | pcbnew.FP_DNP | pcbnew.FP_EXCLUDE_FROM_POS_FILES) if is_dnp
                         else (fp.GetAttributes() & ~pcbnew.FP_DNP & ~pcbnew.FP_EXCLUDE_FROM_POS_FILES))
    nets = dict(board.GetNetsByName())
    for net in exported.findall("./nets/net"):
        name = net.attrib["name"]
        if name not in nets:
            nets[name] = pcbnew.NETINFO_ITEM(board, name)
            board.Add(nets[name])
        for node in net.findall("node"):
            pads = [p for p in footprints[node.attrib["ref"]].Pads() if p.GetNumber() == node.attrib["pin"]]
            assert pads, node.attrib
            for pad in pads:
                pad.SetNet(nets[name])
    for track in board.GetTracks():
        translated = {"Net-(RCT1-Pad2)": "/CT_A", "Net-(RCT2-Pad2)": "/CT_B"}.get(track.GetNetname())
        if translated:
            track.SetNet(nets[translated])
    metrics = {}
    for pair, t, pp, np in (("TX", "T1", "8", "2"), ("RX", "T2", "3", "4")):
        metrics[pair] = solve_pair(board, nets, pair, core.footprint_pad_center(j1, pp), core.footprint_pad_center(j1, np),
                                   core.footprint_pad_center(footprints[t], "4"), core.footprint_pad_center(footprints[t], "6"))
        core.validate_board_pair_topology(board, "LLC " + pair, f"/PAIR_{pair}_P", f"/PAIR_{pair}_N")
    core.validate_rf_launch_topology(board, "LLC")
    title = board.GetTitleBlock()
    title.SetTitle("LLC-13M-1 / ACTUATOR to RJ45 / VNA fixture")
    title.SetRevision("A-PCB")
    title.SetDate("2026-09-03")
    title.SetComment(0, "M12 MALE: TX 8/2; RX 3/4; power pins 1/5/6/7 NC.")
    title.SetComment(1, "DO NOT ORDER: JLC sourcing / panel support / mechanical approval pending.")
    title.SetComment(2, "JLC04161H-7628: 50R W0.35; 100R W0.23/G0.22; L2/L3 GND.")
    title.SetComment(3, "J1 B-side straight male, PG9; no shield pin. CT resistors DNP.")
    use = core.add_board_text(board, "구동기 to RJ45", 53, 22.1, size=1.15, thickness=0.18)
    use.SetFontProp("Malgun Gothic")
    core.add_board_text(board, "LLC-13M-1 / M12 MALE", 32, 28.8, size=0.85, thickness=0.14)
    core.add_board_text(board, "TX 8/2  RX 3/4", 32, 54.7, size=0.8, thickness=0.13)
    core.add_board_text(board, "1/5/6/7 NC - NO POWER", 32, 56.5, size=0.8, thickness=0.13)
    core.add_board_text(board, "PCB DRAFT A - DO NOT ORDER", 52, 62, size=0.9, thickness=0.15)
    core.add_board_text(board, "TX", 78.5, 33.8, size=1)
    core.add_board_text(board, "RX", 78.5, 55.8, size=1)
    for value, x, y, size in (("LLC / ACTUATOR to RJ45", 54, 22.1, 1),
                               ("M12 MALE - PANEL SUPPORT", 32, 30.4, .8),
                               ("CT FLOAT / RCT1,RCT2 DNP", 53, 42, .9),
                               ("LLC ID: ____", 69, 62, .8)):
        core.add_board_text(board, value, x, y, pcbnew.B_SilkS, size, 0.13)
    j1.Reference().SetPosition(core.point(32, 53.5))
    j1.Reference().SetTextAngleDegrees(0)
    j1.Reference().SetTextSize(core.point(.85,.85))
    j1.Reference().SetTextThickness(core.mm(.14))
    for ref in ("RCT1", "RCT2"):
        footprints[ref].GetField("Assembly").SetVisible(False)
    settings(directory)
    pcbnew.SaveBoard(str(directory / f"{PROJECT}.kicad_pcb"), board)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=DEFAULT)
    parser.add_argument("--replace-generated-sha256")
    args = parser.parse_args()
    directory = args.output_directory.resolve()
    if directory == HERE:
        raise SystemExit("Generate into staging, validate and explicitly apply; never overwrite the live project here")
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{PROJECT}.kicad_pcb"
    if target.exists() and digest(target) != args.replace_generated_sha256:
        raise SystemExit("Refusing to overwrite existing PCB without its matching SHA-256")
    if not (directory / f"{PROJECT}.kicad_sch").is_file():
        raise SystemExit("Generate or copy the reviewed LLC schematic into this staging directory first")
    settings(directory)
    subprocess.run([str(core.KICAD_CLI), "sch", "export", "netlist", "--format", "kicadxml", "-o",
                    str(directory / f"{PROJECT}.xml"), str(directory / f"{PROJECT}.kicad_sch")], check=True)
    verify_schematic.verify(directory / f"{PROJECT}.xml")
    subprocess.run([str(core.KICAD_CLI), "sch", "erc", "--severity-all", "--exit-code-violations", "-o",
                    str(directory / "erc.rpt"), str(directory / f"{PROJECT}.kicad_sch")], check=True)
    source_hashes = {p: digest(p) for p in (SOURCE.with_suffix(".kicad_pcb"), SOURCE.with_suffix(".kicad_sch"))}
    metrics = build(directory)
    assert all(digest(p) == h for p, h in source_hashes.items())
    subprocess.run([str(core.KICAD_CLI), "pcb", "drc", "--refill-zones", "--save-board", "--schematic-parity",
                    "--severity-all", "--exit-code-violations", "--format", "json", "-o", str(directory / "drc.json"), str(target)], check=True)
    (directory / "routing_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print("Created routed LLC candidate; native ERC / saved zone refill / DRC / parity all passed. Fabrication remains HOLD.")


if __name__ == "__main__":
    main()
