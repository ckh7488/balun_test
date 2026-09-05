"""Build only the document-mapped LLC schematic; PCB generation is separate.

Run with KiCad 10's bundled Python. A user photo confirms a female cable end,
requiring a male PCB mate, unlike the slip-ring fixture. Its selected PCB MPN
and footprint follow manufacturer documents; sourcing and mechanical release remain
on HOLD. This command cannot produce a PCB or Gerbers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "balun_slipring"))
import generate_pinmap_tbd_drafts as core
import layout_schematic


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, default=HERE)
    parser.add_argument("--replace-generated-sha256", help="Replace an existing reviewed generated draft only if its exact SHA-256 still matches")
    args = parser.parse_args()
    directory = args.output_directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "balun_llc16.kicad_sch"
    if target.exists():
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if args.replace_generated_sha256 != digest:
            raise SystemExit(f"Refusing to overwrite existing schematic without its matching SHA-256: {target}")
    spec = json.loads((HERE / "fixture_spec.json").read_text(encoding="utf-8"))
    assert spec["status"] == "PCB_DRAFT_A_DO_NOT_ORDER"
    assert spec["connector_pcb_footprint"] == "balun_llc16:Finecables_MB12MBAFF08ST-3"
    assert spec["connector_pcb_required_gender"] == "male_pin"
    config = {
        "directory": directory,
        "project": "balun_llc16",
        "board_label": "ACTUATOR to RJ45",
        "connector_symbol": "Conn_01x08",
        "connector_value": "MB12MBAFF08ST-3 / M12 MALE",
        "connector_footprint": spec["connector_pcb_footprint"],
        "connector_datasheet": spec["connector_pcb_datasheet"],
        "connector_manufacturer": spec["connector_pcb_manufacturer"],
        "connector_mpn": spec["connector_pcb_mpn"],
        "connector_lcsc": "",
        "connector_dnp": False,
        "connector_description": "Male A-code 8P PG9; manufacturer PCB layout p415. DUT is female; B-side panel-supported mounting. Supplier / mechanical release pending.",
        "assembly": "FIT REQUIRED; MB12MBAFF08ST-3; B-SIDE; JLC SOURCING / PANEL SUPPORT HOLD; DO NOT ORDER",
        "pin_nets": {int(pin): net for pin, net in spec["pin_nets"].items()},
        "scope_note": "LLC-13M-1 PDF: M12 8/2 = TX+/- to RJ45 1/2; M12 3/4 = RX+/- to RJ45 3/6.",
        "power_note": "M12 1/7 = P24, 5/6 = N24: ALL NC ON FIXTURE. Disconnect power tails and all active devices.",
        "loads_note": "Use existing RJ45 A/B channels. Terminate all four unused coax ports, including RJ45 C and D.",
        "unused_pins_note": "J1.1 / 5 / 6 / 7 POWER: ALL NC",
        "rct_assembly": "DNP; CT-FLOAT baseline; no optional CT-GND population approved for this LLC draft",
        "schematic_title": "LLC-13M-1 / ACTUATOR to RJ45",
        "schematic_date": "2026-09-03",
        "core_note": "2-channel VNA fixture: 50 ohm / 100 ohm differential.",
        "source_note": "Source: LLC-13M-1, 2022-04-25. Verify actual cable.",
        "release_note": "PCB DRAFT A: supplier / panel mechanics / fabrication HOLD.",
    }
    with tempfile.TemporaryDirectory(prefix="llc16-schematic-") as name:
        scratch = Path(name).resolve()
        assert scratch.parent == Path(tempfile.gettempdir()).resolve()
        config["directory"] = scratch
        core.write_schematic(config)
        base = (scratch / target.name).read_text(encoding="utf-8")
        content = layout_schematic.render(base, spec)
    # Recheck before replacing, so a concurrent editor save is not discarded.
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != args.replace_generated_sha256:
        raise SystemExit("Target changed during generation; refusing to overwrite")
    target.write_text(content, encoding="utf-8")
    print(f"Created PCB DRAFT A schematic: {target}")
    print("This command generates only a schematic; no assembly or fabrication release is granted.")


if __name__ == "__main__":
    main()
