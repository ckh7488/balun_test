"""Regression checks for the presentation refresh; never save or regenerate PCBs.

Run with KiCad's bundled Python after refresh_schematic_layouts.py --apply.
All generated test schematics stay under the dated review directory.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

import refresh_schematic_layouts as refresh

core = refresh.core


def copy_project_settings(project: Path, destination: Path) -> None:
    shutil.copy2(project.with_suffix(".kicad_pro"), destination / (project.name + ".kicad_pro"))
    table = (project.parent / "fp-lib-table").read_text(encoding="utf-8")
    (destination / "fp-lib-table").write_text(table.replace("${KIPRJMOD}", project.parent.as_posix()), encoding="utf-8")


def check(schematic: Path, baseline: Path, destination: Path) -> None:
    refresh.run("sch", "erc", "--severity-all", "--exit-code-violations", "-o", destination / "erc.rpt", schematic)
    exported = destination / "netlist.xml"
    refresh.run("sch", "export", "netlist", "--format", "kicadxml", "-o", exported, schematic)
    assert refresh.netlist_signature(exported) == refresh.netlist_signature(baseline), schematic


def main() -> None:
    llc = refresh.HERE / "balun_llc16/balun_llc16"
    protected = [p.with_suffix(s) for p in refresh.PROJECTS.values()
                 for s in (".kicad_sch", ".kicad_pro", ".kicad_pcb", ".kicad_dru")]
    protected += [llc.with_suffix(s) for s in (".kicad_sch", ".kicad_pro")]
    starting = {p: refresh.sha(p) for p in protected}
    results = {}
    for variant, project in refresh.PROJECTS.items():
        work = refresh.REVIEW / project.name
        before = work / "before"
        for suffix in (".kicad_pcb", ".kicad_dru"):
            assert refresh.sha(project.with_suffix(suffix)) == refresh.sha(before / (project.name + suffix))
        expected_project = refresh.visible_schematic_colors((before / (project.name + ".kicad_pro")).read_text(encoding="utf-8"))
        assert json.loads(project.with_suffix(".kicad_pro").read_text(encoding="utf-8")) == json.loads(expected_project)
        assert refresh.symbol_signature(project.with_suffix(".kicad_sch").read_text(encoding="utf-8")) == refresh.symbol_signature((before / (project.name + ".kicad_sch")).read_text(encoding="utf-8"))
        live_check = work / "live-validation"
        live_check.mkdir(exist_ok=True)
        check(project.with_suffix(".kicad_sch"), work / "before.xml", live_check)
        refresh.run("pcb", "drc", "--refill-zones", "--schematic-parity", "--severity-all", "--exit-code-violations",
                    "-o", live_check / "drc.rpt", project.with_suffix(".kicad_pcb"))
        results[project.name] = {"live_erc_drc_parity": "PASS", "exact_connectivity_parts_and_uuids": "PASS",
                                "pcb_and_dru_sha256_unchanged": True, "project_display_only": True}
        if variant in core.VARIANTS:
            regenerated = work / "regeneration"
            regenerated.mkdir(exist_ok=True)
            config = dict(core.VARIANTS[variant], directory=regenerated)
            core.write_schematic(config)
            core.write_project(config)
            copy_project_settings(project, regenerated)
            generated_sch = regenerated / (project.name + ".kicad_sch")
            check(generated_sch, work / "before.xml", regenerated)
            assert refresh.symbol_signature(generated_sch.read_text(encoding="utf-8")) == refresh.symbol_signature(project.with_suffix(".kicad_sch").read_text(encoding="utf-8"))
            results[project.name]["regeneration_after_rj45_relayout"] = "PASS"
    llc_check = refresh.REVIEW / "llc-regression"
    llc_check.mkdir(exist_ok=True)
    old_xml = llc_check / "live.xml"
    refresh.run("sch", "export", "netlist", "--format", "kicadxml", "-o", old_xml, llc.with_suffix(".kicad_sch"))
    llc_generated = llc_check / "balun_llc16.kicad_sch"
    args = [sys.executable, str(llc.parent / "generate_schematic.py"), "--output-directory", str(llc_check)]
    if llc_generated.exists():
        args += ["--replace-generated-sha256", refresh.sha(llc_generated)]
    subprocess.run(args, check=True)
    copy_project_settings(llc, llc_check)
    check(llc_generated, old_xml, llc_check)
    subprocess.run([sys.executable, str(llc.parent / "verify_schematic.py"), str(llc_check / "netlist.xml")], check=True)
    assert refresh.symbol_signature(llc_generated.read_text(encoding="utf-8")) == refresh.symbol_signature(llc.with_suffix(".kicad_sch").read_text(encoding="utf-8"))
    assert all(refresh.sha(path) == digest for path, digest in starting.items()), "Verification changed a live CAD file"
    results["balun_llc16"] = {"regeneration_after_rj45_relayout": "PASS", "all_live_cad_untouched": True}
    (refresh.REVIEW / "regression.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print("PASS: all three live schematics; PCB parity; both slipring regenerators; LLC regeneration and pinmap checks.")
    print("No live CAD file was modified by verification.")


if __name__ == "__main__":
    main()
