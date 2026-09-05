"""Prepare or apply the reviewed presentation refresh; never regenerate a PCB.

The recorded before/ CAD snapshots are immutable inputs. Native KiCad XML is
compared before applying, including net names, pin membership, part properties,
population states, library identity and symbol paths.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE / "balun_slipring"))
import generate_pinmap_tbd_drafts as core
from readable_schematic import render_schematic

CLI = Path("C:/Program Files/KiCad/10.0/bin/kicad-cli.exe")
REVIEW = ROOT / "outputs/balun-schematic-refresh-20260903"
PROJECTS = {
    "rj45": HERE / "balun_eth_rj45/balun_eth_rj45",
    "molex": HERE / "balun_slipring/molex_end/balun_slipring_molex",
    "m12": HERE / "balun_slipring/m12_end/balun_slipring_m12",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args: object) -> None:
    subprocess.run([str(CLI), *(str(a) for a in args)], check=True)


def netlist_signature(path: Path) -> dict:
    root = ET.parse(path).getroot()
    parts = {}
    for component in root.findall("./components/comp"):
        parts[component.attrib["ref"]] = {
            "value": component.findtext("value"),
            "footprint": component.findtext("footprint"),
            "datasheet": component.findtext("datasheet"),
            "fields": {n.attrib["name"]: n.text or "" for n in component.findall("./fields/field")},
            "properties": {n.attrib["name"]: n.attrib.get("value", "") for n in component.findall("property")},
            "libsource": component.find("libsource").attrib,
            "sheetpath": component.find("sheetpath").attrib,
            "tstamps": component.findtext("tstamps"),
        }
    nets = {n.attrib["name"]: {
        "class": n.attrib.get("class"),
        "nodes": sorted(tuple(sorted(p.attrib.items())) for p in n.findall("node")),
    } for n in root.findall("./nets/net")}
    return {"components": parts, "nets": nets}


def symbol_signature(source: str) -> dict:
    result = {}
    for ref, block in core.find_symbol_instances(source).items():
        result[ref] = {
            "uuids": re.findall(r'\(uuid\s+"([^"]+)"', block),
            "lib_id": re.search(r'\(lib_id\s+"([^"]+)"', block).group(1),
            "properties": dict(re.findall(r'\(property\s+"([^"]+)"\s+"((?:[^"\\]|\\.)*)"', block)),
            "states": {name: re.search(rf'\({name}\s+([^\s)]+)', block).group(1)
                       for name in ("unit", "body_style", "exclude_from_sim", "in_bom", "on_board", "in_pos_files", "dnp")},
        }
    return result


def visible_schematic_colors(source: str) -> str:
    """Change only custom schematic-color alpha; retain all PCB/routing settings."""
    expected = copy.deepcopy(json.loads(source))
    changed = set()
    for netclass in expected["net_settings"]["classes"]:
        if netclass["name"] not in {"ETH100", "RF50"}:
            continue
        old = netclass["schematic_color"]
        new, count = re.subn(r",\s*0\.000\)$", ", 1.000)", old)
        assert count == 1, f"Unexpected baseline color: {netclass['name']} {old}"
        source, count = re.subn(r'("schematic_color"\s*:\s*")' + re.escape(old) + '"',
                                lambda m: m.group(1) + new + '"', source)
        assert count == 1, f"Ambiguous color replacement: {old}"
        netclass["schematic_color"] = new
        changed.add(netclass["name"])
    assert changed == {"ETH100", "RF50"}
    assert json.loads(source) == expected, "Non-display project settings changed"
    return source


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply all three validated layouts with concurrent-save protection")
    args = parser.parse_args()
    applied_file = REVIEW / "applied_hashes.json"
    applied = json.loads(applied_file.read_text(encoding="utf-8")) if applied_file.exists() else {}
    prepared, summaries, starting_hashes = {}, {}, {}
    for variant, project in PROJECTS.items():
        name, live = project.name, project.with_suffix(".kicad_sch")
        work = REVIEW / name
        original = work / "before" / live.name
        live_pro = project.with_suffix(".kicad_pro")
        for editable in (live, live_pro):
            starting_hashes[editable.name] = sha(editable)
            recorded = applied.get(editable.name, applied.get(name) if editable == live else None)
            assert starting_hashes[editable.name] in {sha(work / "before" / editable.name), recorded}, f"User changes since the reviewed baseline: {editable}"
        for suffix in (".kicad_pcb", ".kicad_dru"):
            assert sha(project.with_suffix(suffix)) == sha(work / "before" / (name + suffix)), f"Protected file changed: {project}{suffix}"
        before = original.read_text(encoding="utf-8")
        after = render_schematic(before, variant)
        assert symbol_signature(before) == symbol_signature(after), f"Component metadata changed: {variant}"
        assert re.search(r'\(uuid\s+"([^"]+)"', before).group(1) == re.search(r'\(uuid\s+"([^"]+)"', after).group(1)
        candidate_dir = work / "candidate"
        candidate_dir.mkdir(exist_ok=True)
        candidate = candidate_dir / live.name
        candidate.write_text(after, encoding="utf-8")
        candidate_pro = candidate_dir / live_pro.name
        candidate_pro.write_text(visible_schematic_colors((work / "before" / live_pro.name).read_text(encoding="utf-8")), encoding="utf-8")
        library_table = (project.parent / "fp-lib-table").read_text(encoding="utf-8")
        library_table = library_table.replace("${KIPRJMOD}", project.parent.as_posix())
        (candidate_dir / "fp-lib-table").write_text(library_table, encoding="utf-8")
        run("sch", "erc", "--severity-all", "--exit-code-violations", "-o", work / "after-erc.rpt", candidate)
        run("sch", "export", "netlist", "--format", "kicadxml", "-o", work / "after.xml", candidate)
        old, new = netlist_signature(work / "before.xml"), netlist_signature(work / "after.xml")
        assert old == new, f"Electrical / BOM / population / UUID regression: {variant}"
        output_pdf = ROOT / "output/pdf" / (name + "_schematic.pdf")
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        run("sch", "export", "pdf", "--no-background-color", "--exclude-pdf-property-popups", "-o", output_pdf, candidate)
        summaries[name] = {"components": len(new["components"]), "nets": len(new["nets"]),
                           "before_sha256": sha(original), "after_sha256": sha(candidate),
                           "native_erc": "0 errors, 0 warnings", "netlist_and_symbol_properties_identical": True,
                           "project_change": "ETH100/RF50 schematic_color alpha 0.000 -> 1.000 only",
                           "pcb_and_design_rules_identical": True,
                           "pdf": str(output_pdf), "applied": args.apply}
        prepared[name] = ((live, candidate), (live_pro, candidate_pro))
        print(f"PASS {name}: {len(new['components'])} parts, {len(new['nets'])} nets; exact connectivity/properties preserved")
    if args.apply:
        for files in prepared.values():
            for live, _ in files:
                assert sha(live) == starting_hashes[live.name], f"Concurrent CAD save: {live}"
        for files in prepared.values():
            for live, candidate in files:
                shutil.copyfile(candidate, live)
        applied_file.write_text(json.dumps({live.name: sha(live) for files in prepared.values() for live, _ in files}, indent=2) + "\n", encoding="utf-8")
    (REVIEW / "verification.json").write_text(json.dumps(summaries, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
