"""Native KiCad DRC/ERC/parity, independent pin-map checks and SVG exports.

Usage: python adapters/verify_adapters.py --kicad-cli /path/to/kicad-cli
Zone refill updates the saved boards before their hashes are recorded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
EXPECTED = {
    "m12_slipring": {"1": "4", "2": "3", "3": "2", "6": "1"},
    "m12_llc": {"1": "8", "2": "2", "3": "3", "6": "4"},
    "molex_slipring": {"1": "1", "2": "2", "3": "3", "6": "4"},
}


def run(cli, *args):
    result = subprocess.run([cli, *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kicad-cli", default="kicad-cli")
    args = parser.parse_args()
    summary = {"kicad_version": run(args.kicad_cli, "version"), "boards": {}}
    for name, pinmap in EXPECTED.items():
        d = HERE / name
        pcb, sch = d / f"{name}.kicad_pcb", d / f"{name}.kicad_sch"
        run(args.kicad_cli, "pcb", "drc", "--refill-zones", "--save-board", "--schematic-parity",
            "--exit-code-violations", "--format", "json", "--output", d / "drc.json", pcb)
        run(args.kicad_cli, "sch", "erc", "--exit-code-violations", "--format", "json", "--output", d / "erc.json", sch)
        run(args.kicad_cli, "sch", "export", "netlist", "--format", "kicadxml", "--output", d / "netlist.xml", sch)
        nets = [set((n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node"))
                for net in ET.parse(d / "netlist.xml").findall("./nets/net")]
        for source, target in pinmap.items():
            expected = {("J1", source), ("J2", target)}
            if expected not in nets:
                raise ValueError(f"{name}: missing exact pair net {expected}")
        if name != "molex_slipring" and {("J1", "SH"), ("TP1", "1")} not in nets:
            raise ValueError(f"{name}: missing shield solder-point connection")
        for net in nets:
            for ref, pin in net:
                if (ref == "J1" and pin not in {*pinmap, "SH"}) or (ref == "J2" and pin not in pinmap.values()):
                    if len(net) != 1:
                        raise ValueError(f"{name}: NC/power pin unexpectedly connected: {net}")
        for label, layers in (("layout", "F.Cu,B.Cu,F.SilkS,Edge.Cuts"), ("planes", "In1.Cu,In2.Cu,Edge.Cuts")):
            run(args.kicad_cli, "pcb", "export", "svg", "--layers", layers, "--mode-single", "--fit-page-to-board",
                "--exclude-drawing-sheet", "--output", d / f"{label}.svg", pcb)
            svg = d / f"{label}.svg"
            content = svg.read_text().replace('</desc>', '</desc>\n<rect width="100%" height="100%" fill="#111827"/>', 1)
            svg.write_text("\n".join(line.rstrip() for line in content.splitlines()) + "\n")
        run(args.kicad_cli, "sch", "export", "svg", "--output", str(d / "schematic_svg") + "/", sch)
        counts = {}
        for kind in ("drc", "erc"):
            p = d / f"{kind}.json"
            data = json.loads(p.read_text())
            groups = [data.get(k, []) for k in ("violations", "unconnected_items", "schematic_parity")]
            groups += [s.get("violations", []) for s in data.get("sheets", [])]
            counts[kind] = sum(map(len, groups))
            if counts[kind]:
                raise ValueError(f"{name}: {kind} still has violations")
            # Make review reports portable without changing their findings.
            p.write_text(json.dumps(data, indent=2).replace(str(HERE.parent) + "/", "") + "\n")
        # The generated netlist is an intermediate; native parity and explicit
        # assertions above are retained in the signed-by-hash verification file.
        (d / "netlist.xml").unlink()
        hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (pcb, sch, d / f"{name}.kicad_pro", d / f"{name}.kicad_dru")}
        summary["boards"][name] = {**counts, "exact_pinmap_verified": pinmap, "sha256": hashes}
        print(f"{name}: DRC/ERC/parity 0; pinmap and isolated NC pins verified")
    summary["not_verified"] = ["Actual DUT connector mating and continuity", "Mechanical panel fit",
                               "Manufacturer-controlled impedance", "RF performance and calibration accuracy"]
    (HERE / "verification.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
