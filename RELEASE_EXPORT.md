# JLCPCB release export

> **Latest procurement override, 2026-09-03:** The user subsequently chose bare PCB fabrication plus separately purchased components and in-house hand soldering. See [`HAND_ASSEMBLY_PURCHASE_2026-09-03.md`](HAND_ASSEMBLY_PURCHASE_2026-09-03.md). The older PCBA delivery assumptions below are historical. This changes procurement only: ten intended assembled boards, electrical FIT/DNP variants, connector/mechanical HOLDs, release checks and the exporter's lack of LLC fabrication support remain unchanged. Do not treat this decision as fabrication approval.

> **2026-09-03 purchase-scope update:** The planned delivery is now ten PCBAs: four slip-ring, four RJ45 (two SHIELD-BONDED and two SHIELD-FLOAT), and two new LLC M12 endpoints sharing the RJ45 boards. No default user soldering step is assumed. See [`PCBA_PURCHASE_SCOPE_2026-09-03.md`](PCBA_PURCHASE_SCOPE_2026-09-03.md). The current exporter still produces the common RSH1-DNP candidate, not both assembly variants. Do not use its RJ45 BOM/CPL unchanged for the SHIELD-BONDED boards. Supplier approval and validated variant-specific outputs are required; slip-ring HOLD status is unchanged. **The [LLC design](balun_llc16/README.md) now has a routed PCB DRAFT A with clean native ERC/DRC/parity, but no fabrication Gerber/BOM/CPL and is still not covered by this exporter.** Its male M12 MB12MBAFF08ST-3 footprint follows the manufacturer's male PCB layout and the cable drawing's numeric pin map. JLC sourcing/assembly, actual mating and panel support, manufacturing stack/impedance/CAM and release approval remain outstanding. Cable continuity and no-power checks belong before the first VNA connection, not as prerequisites to starting PCB design.

`export_jlc_release.ps1` creates reproducible JLCPCB fabrication outputs without saving or editing the live KiCad projects. Each project is copied to a separate temporary staging directory before KiCad refills and saves zones, runs DRC with schematic parity, and runs ERC.

## Default release-candidate export

Run from PowerShell in the repository root:

```powershell
.\export_jlc_release.ps1
```

The default output directory is `release_jlc/<timestamp>/`. The script validates all three projects, but creates fabrication files and a Gerber ZIP only for `balun_eth_rj45`.

- `balun_eth_rj45`: `RELEASE_CANDIDATE`
- `balun_slipring_molex`: `HOLD_DO_NOT_ORDER`
- `balun_slipring_m12`: `HOLD_DO_NOT_ORDER`

The two slip-ring boards remain blocked by connector, pin-map, mechanical, and final impedance-release checks. Their default output directories contain validation reports and an explicit HOLD notice, but no fabrication ZIP.

## Explicit engineering export of HOLD boards

```powershell
.\export_jlc_release.ps1 -IncludeHoldBoards
```

This creates engineering-review Gerbers for the two HOLD boards. Their ZIP filenames contain `HOLD_DO_NOT_ORDER`. This switch does not approve them for fabrication or ordering.

An alternate empty output directory and an explicit KiCad 10 CLI may be supplied:

```powershell
.\export_jlc_release.ps1 `
  -OutputDirectory 'C:\release\balun-review' `
  -KiCadCli 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe'
```

The script refuses to write into a non-empty output directory.

## Output structure

For an exported project:

```text
<project>/
  fabrication/     RS-274X Gerbers, separate PTH/NPTH Excellon, drill maps, IPC-D-356 netlist
  assembly/        DNP-excluded JLCPCB-format BOM and CPL CSV
  reports/         DRC, ERC, and drill reports
  README.txt       status and order warnings
  *-JLCPCB_GERBER.zip
```

The Gerber ZIP contains only the files in `fabrication/` and is the PCB-fabrication upload. The component position CSV is deliberately outside that ZIP. `SHA256SUMS.txt` covers all generated files and ZIPs.

## Assembly BOM/CPL

The script exports a project-specific BOM with `Comment`, `Designator`, `Footprint`, and `LCSC Part #`, and a CPL with `Designator`, `Mid X`, `Mid Y`, `Rotation`, and `Layer`. Both exclude schematic/PCB items marked DNP. The repository-wide combined BOM is not a valid per-project JLCPCB assembly BOM and must not be uploaded.

The generated files are upload-format candidates, not automatic placement approval. In particular, JLC's own KiCad guidance requires checking component translations and rotations in the placement preview.

Before paying for any PCBA order, manually verify all of the following:

1. project-specific BOM fields, LCSC numbers, FIT/DNP state, and assembly quantities;
2. the DNP-excluded position CSV side, rotation, origin, and JLC placement preview;
3. SMA and connector orientation in the JLC 2D/3D viewer;
4. current JLC stack-up selection and impedance-calculator result;
5. Gerber CAM, inner-plane fill, PTH/NPTH drills, and board outline;
6. the project status in `RELEASE_README.txt` and each project `README.txt`.

`RELEASE_CANDIDATE` means the automated CAD checks passed. It does not replace controlled-impedance approval, BOM/CPL review, mechanical validation, or an engineering decision to order.
