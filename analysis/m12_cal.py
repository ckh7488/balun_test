"""SMA-SOLT-corrected measurements -> saved UnknownThru -> balanced DUT.

Run from the repository root: python -m analysis.m12_cal --help
All numerical calibration standards are referenced to 50 ohms. The corrected
balanced result is THEN renormalized to 100 ohms. Input S values are never
relabelled or pre-renormalized to pretend that the SMA is a balanced port.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import skrf as rf
from skrf.calibration import EightTerm, UnknownThru

SCHEMA = 1
INPUT_Z0 = 50.0
OUTPUT_Z0 = 100.0
NAMES = ("open", "short", "load")


def template():
    return {
        "schema": SCHEMA,
        "input_stage": "full_two_port_sma_solt",
        "setup_id": "M12_PAIR_A_CTFLOAT_RUN01",
        "reference_planes": ["left adapter M12 mating plane", "right adapter M12 mating plane"],
        "notes": "Ideal OSL is an initial approximation, not a measured standard model. Record pin map, board/adapter/load IDs, shield, sweep, SMA calibration ID and photos.",
        "standards": {
            port: {
                name: {
                    "file": f"{port}_{name}.s1p",
                    "model": {"capacitance_pf": 0.0} if name == "open" else
                    {"resistance_ohm": 0.0, "inductance_nh": 0.0} if name == "short" else
                    {"resistance_ohm": 100.0, "inductance_nh": 0.0, "capacitance_pf": 0.0},
                }
                for name in NAMES
            } for port in ("p1", "p2")
        },
        "thru": {"file": "thru.s2p", "delay_ns": 0.0, "polarity": 1,
                 "notes": "Reciprocal short connection; estimate delay and verify pair polarity. This is NOT a measured thru model."},
    }


def number(obj, key, default=0.0, positive=False):
    value = float(obj.get(key, default))
    if not np.isfinite(value) or value < 0 or (positive and value <= 0):
        raise ValueError(f"{key} must be finite and {'positive' if positive else 'nonnegative'}")
    return value


def read_network(path, nports=None, frequencies=None):
    n = rf.Network(str(path))
    if nports is not None and n.nports != nports:
        raise ValueError(f"{path}: expected {nports} ports, got {n.nports}")
    if len(n.f) < 3 or not np.all(np.isfinite(n.f)) or n.f[0] <= 0 or np.any(np.diff(n.f) <= 0):
        raise ValueError(f"{path}: need at least 3 positive, strictly increasing frequencies")
    if not np.all(np.isfinite(n.s)) or not np.allclose(n.z0, INPUT_Z0, rtol=0, atol=1e-9):
        raise ValueError(f"{path}: need finite S data with 50-ohm SMA reference")
    if frequencies is not None and not np.array_equal(n.f, frequencies):
        raise ValueError(f"{path}: frequency grid differs; remeasure on the calibration grid")
    return n


def standard_model(frequency, kind, model):
    """Lumped termination behind an optional lossless offset line; output z0=50.

    O: shunt C. S: series R+L. L: (R+L) shunted by C.
    offset_delay_ns is ONE-WAY delay, offset_z0_ohm defaults to 100.
    These parameters must come from construction/model evidence, not fitting
    the same standards until they look ideal after calibration.
    """
    allowed = {"capacitance_pf", "resistance_ohm", "inductance_nh", "offset_delay_ns", "offset_z0_ohm"}
    if set(model) - allowed:
        raise ValueError(f"Unknown standard model fields: {set(model) - allowed}")
    w = 2 * np.pi * frequency.f
    zline = number(model, "offset_z0_ohm", 100, positive=True)
    c = number(model, "capacitance_pf") * 1e-12
    if kind == "open":
        if model.get("resistance_ohm", 0) or model.get("inductance_nh", 0):
            raise ValueError("Open model supports capacitance and offset only")
        gamma = (1 - 1j * w * c * zline) / (1 + 1j * w * c * zline)
    else:
        r = number(model, "resistance_ohm", 100 if kind == "load" else 0, positive=kind == "load")
        z = r + 1j * w * number(model, "inductance_nh") * 1e-9
        if kind == "short" and c:
            raise ValueError("Short model supports series R/L and offset only")
        z = z / (1 + 1j * w * c * z)
        gamma = (z - zline) / (z + zline)
    gamma *= np.exp(-2j * w * number(model, "offset_delay_ns") * 1e-9)
    # Bilinear change of reflection reference, including exact O/S endpoints.
    mismatch = (zline - INPUT_Z0) / (zline + INPUT_Z0)
    gamma = (mismatch + gamma) / (1 + mismatch * gamma)
    return rf.Network(frequency=frequency, s=gamma[:, None, None], z0=INPUT_Z0, name=kind)


def two_reflects(left, right):
    s = np.zeros((len(left.f), 2, 2), complex)
    s[:, 0, 0], s[:, 1, 1] = left.s[:, 0, 0], right.s[:, 0, 0]
    return rf.Network(frequency=left.frequency, s=s, z0=INPUT_Z0)


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fit(config_path):
    path = Path(config_path).resolve()
    cfg = json.loads(path.read_text(encoding="utf-8"))
    if cfg.get("schema") != SCHEMA or cfg.get("input_stage") != "full_two_port_sma_solt":
        raise ValueError("Only full two-port SMA SOLT corrected exports are supported")
    if not cfg.get("setup_id") or len(cfg.get("reference_planes", [])) != 2:
        raise ValueError("Record setup_id and the two reference_planes")
    tcfg = cfg["thru"]
    thru_path = path.parent / tcfg["file"]
    thru = read_network(thru_path, 2)
    if np.any(np.abs(thru.s[:, 1, 0]) < 1e-5) or np.any(np.abs(thru.s[:, 0, 1]) < 1e-5):
        raise ValueError("Thru has a near-zero transmission; check wiring/balun band")
    files = {str(thru_path.resolve()): hash_file(thru_path)}
    data, ideals = {}, {}
    for port_index, port in enumerate(("p1", "p2")):
        data[port], ideals[port] = {}, {}
        for kind in NAMES:
            item = cfg["standards"][port][kind]
            src = (path.parent / item["file"]).resolve()
            if str(src) in files:
                raise ValueError(f"Duplicate calibration input: {src}")
            n = read_network(src, frequencies=thru.f)
            if n.nports == 2:
                n = n.s11 if port_index == 0 else n.s22
            elif n.nports != 1:
                raise ValueError(f"{src}: expected .s1p or .s2p")
            data[port][kind] = n
            ideals[port][kind] = standard_model(thru.frequency, kind, item["model"])
            files[str(src)] = hash_file(src)
    measured = [two_reflects(data["p1"][k], data["p2"][k]) for k in NAMES]
    known = [two_reflects(ideals["p1"][k], ideals["p2"][k]) for k in NAMES]
    polarity = tcfg["polarity"]
    if polarity not in (-1, 1):
        raise ValueError("thru.polarity must be +1 or -1 from the pair wiring")
    t = polarity * np.exp(-2j * np.pi * thru.f * number(tcfg, "delay_ns") * 1e-9)
    approx = rf.Network(frequency=thru.frequency, s=np.zeros_like(thru.s), z0=OUTPUT_Z0)
    approx.s[:, 1, 0] = approx.s[:, 0, 1] = t
    approx.renormalize(INPUT_Z0)
    zero = rf.Network(frequency=thru.frequency, s=np.zeros((len(thru.f), 1, 1)), z0=INPUT_Z0)
    # Initial FULL SMA SOLT removes instrument switch errors to its accuracy.
    # The second stage models only fixed fixture error boxes, with zero switch
    # terms and zero additive leakage. This is NOT valid for raw VNA exports.
    cal = UnknownThru(measured=measured + [thru], ideals=known + [approx], switch_terms=(zero, zero))
    cal.run()
    if any(not np.all(np.isfinite(v)) for v in cal.coefs.values()):
        raise ValueError("Non-finite correction coefficients; check standards and frequency range")
    for key in ("forward reflection tracking", "reverse reflection tracking", "k"):
        if np.any(np.abs(cal.coefs[key]) < 1e-12):
            raise ValueError(f"Degenerate calibration: {key}")
    metadata = {
        "schema": SCHEMA, "algorithm": "UnknownThru", "skrf_version": rf.__version__,
        "input_z0_ohm": INPUT_Z0, "calibration_z0_ohm": INPUT_Z0, "output_z0_ohm": OUTPUT_Z0,
        "config": cfg, "input_sha256": files,
        "limitations": ["OSL model accuracy not established by this fit", "thru reciprocity and phase/polarity assumed",
                        "fixed two-error-box approximation; no mixed-mode or cross-pair leakage correction",
                        "synthetic verification is not hardware validation"],
    }
    return cal, metadata


def save_cal(path, cal, metadata):
    path = Path(path)
    if path.suffix != ".npz":
        raise ValueError("Calibration output must end in .npz")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as f:
        np.savez_compressed(f, frequency_hz=cal.frequency.f, metadata=json.dumps(metadata), **cal.coefs)


def load_cal(path):
    with np.load(path, allow_pickle=False) as archive:
        meta = json.loads(str(archive["metadata"]))
        if meta.get("schema") != SCHEMA or meta.get("algorithm") != "UnknownThru":
            raise ValueError("Unsupported calibration archive")
        f = rf.Frequency.from_f(archive["frequency_hz"], unit="hz")
        coefs = {k: archive[k].copy() for k in archive.files if k not in ("frequency_hz", "metadata")}
    return EightTerm.from_coefs(f, coefs), meta


def corrected(cal, measured):
    if measured.nports != 2 or not np.array_equal(measured.f, cal.frequency.f):
        raise ValueError("DUT must be two-port and use exactly the calibration frequency grid")
    if not np.allclose(measured.z0, INPUT_Z0, rtol=0, atol=1e-9):
        raise ValueError("DUT must retain the 50-ohm SMA reference")
    n = cal.apply_cal(measured)
    if not np.all(np.isfinite(n.s)):
        raise ValueError("Correction produced non-finite values")
    # Actual wave-reference transformation at the already corrected DUT plane.
    n.renormalize(OUTPUT_Z0)
    return n


def metrics(n):
    tiny = np.finfo(float).tiny
    loss = -20 * np.log10(np.maximum(np.abs(n.s), tiny))
    phase = np.unwrap(np.angle(n.s), axis=0)
    gd = -np.gradient(phase, n.f, axis=0) / (2 * np.pi) * 1e9
    return np.column_stack((n.f, loss[:, 0, 0], loss[:, 1, 1], loss[:, 1, 0], loss[:, 0, 1],
                            np.rad2deg(phase[:, 1, 0]), np.rad2deg(phase[:, 0, 1]), gd[:, 1, 0], gd[:, 0, 1],
                            np.abs(n.s[:, 1, 0] - n.s[:, 0, 1])))


def export_result(n, out_dir, label, metadata):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("s2p", "csv", "png", "json"):
        if (out / f"{label}.{ext}").exists():
            raise FileExistsError(f"Refusing to overwrite {out / label}; choose a new output folder")
    n.name = label
    n.comments = "M12/adapter-end correction; 100-ohm balanced effective two-port. Not full mixed-mode."
    n.write_touchstone(filename=label, dir=out, form="ri")
    values = metrics(n)
    np.savetxt(out / f"{label}.csv", values, delimiter=",", comments="", header=
               "frequency_hz,rl1_db,rl2_db,il21_db,il12_db,phase21_deg,phase12_deg,group_delay21_ns,group_delay12_ns,reciprocity_abs")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    x = n.f / 1e6
    for ax, cols, labels, ylabel in (
        (axes[0, 0], (1, 2), ("RL1", "RL2"), "Return loss (dB)"),
        (axes[0, 1], (3, 4), ("IL21", "IL12"), "Insertion loss (dB)"),
        (axes[1, 0], (5, 6), ("S21", "S12"), "Unwrapped phase (deg)"),
        (axes[1, 1], (7, 8), ("S21", "S12"), "Group delay (ns)"),
    ):
        for col, legend in zip(cols, labels):
            ax.plot(x, values[:, col], label=legend)
        ax.set(xlabel="Frequency (MHz)", ylabel=ylabel)
        ax.grid(True, alpha=.3)
        ax.legend()
    fig.suptitle(f"{label} — 100 ohm balanced; model-dependent correction")
    fig.savefig(out / f"{label}.png", dpi=160)
    plt.close(fig)
    metadata = dict(metadata)
    metadata["max_singular_value"] = float(np.max(np.linalg.svd(n.s, compute_uv=False)))
    metadata["max_reciprocity_abs"] = float(np.max(values[:, 9]))
    metadata["decision"] = "No automatic industrial-use PASS/FAIL; apply validated limits and uncertainty."
    (out / f"{label}.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="write an editable session template beside measurement files")
    init.add_argument("config", type=Path)
    fit_parser = sub.add_parser("calibrate", help="fit 3+3+1 standard files; save reusable coefficients")
    fit_parser.add_argument("config", type=Path)
    fit_parser.add_argument("--out", required=True, type=Path)
    apply_parser = sub.add_parser("apply", help="correct one or more SMA-calibrated DUT .s2p files")
    apply_parser.add_argument("calibration", type=Path)
    apply_parser.add_argument("dut", nargs="+", type=Path)
    apply_parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            args.config.parent.mkdir(parents=True, exist_ok=True)
            with args.config.open("x", encoding="utf-8") as f:
                json.dump(template(), f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"Created {args.config}; edit models, pin polarity and setup notes before calibrating.")
        elif args.command == "calibrate":
            cal, metadata = fit(args.config)
            save_cal(args.out, cal, metadata)
            print(f"Saved {args.out}. OSL model and thru phase assumptions still require independent checks.")
        else:
            cal, meta = load_cal(args.calibration)
            for dut in args.dut:
                measured = read_network(dut, 2, cal.frequency.f)
                n = corrected(cal, measured)
                provenance = {**meta, "dut_sha256": hash_file(dut), "calibration_sha256": hash_file(args.calibration)}
                export_result(n, args.out, dut.stem + "_m12", provenance)
                print(f"Saved {dut.stem}_m12: .s2p, .csv, .png, .json in {args.out}")
    except (ValueError, KeyError, OSError, np.linalg.LinAlgError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
