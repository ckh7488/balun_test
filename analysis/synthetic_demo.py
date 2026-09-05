"""Create reproducible, explicitly SYNTHETIC data to exercise the full CLI.

Independent network cascade with unequal lossy fixtures, impedance-transforming
baluns, nonideal OSL and an unknown mismatched reciprocal thru. No hardware
accuracy claim follows from this example.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import skrf as rf

from .m12_cal import template


def line(f, z=100, delay_ns=1.0, loss_db=.1):
    media = rf.media.DefinedGammaZ0(f, z0=z, z0_port=100,
                                  gamma=loss_db / 8.686 + 2j * np.pi * f.f * delay_ns * 1e-9)
    return media.line(1, unit="m")


def generate(directory, nonideal=True, polarity=1):
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=False)
    f = rf.Frequency(1, 200, 401, unit="mhz")
    balun = line(f, delay_ns=.2, loss_db=.4)
    # An ideal turns-ratio transformation expressed by matched mixed z0 ports.
    # This is deliberate physics in the synthetic fixture, not data relabelling.
    balun.z0 = np.tile([50, 100], (len(f), 1))
    left = balun ** line(f, z=87, delay_ns=1.4, loss_db=.2)
    right = line(f, z=116, delay_ns=2.1, loss_db=.3) ** balun.flipped()
    cfg = template()
    cfg["setup_id"] = "SYNTHETIC_NOT_HARDWARE"
    cfg["thru"].update(delay_ns=.7, polarity=polarity)
    for port, fixture in (("p1", left), ("p2", right.flipped())):
        w = 2 * np.pi * f.f
        scale = 1 if port == "p1" else 1.3
        capacitance = .8 * scale if nonideal else 0
        inductance = 7 * scale if nonideal else 0
        resistance = 100 + scale if nonideal else 100
        # Independently form physical impedances/admittances at 100 ohms.
        yo = 1j * w * capacitance * 1e-12
        zs = 1j * w * inductance * 1e-9
        zl = resistance + 1j * w * inductance * 1e-9
        gammas = {"open": (1 - 100 * yo) / (1 + 100 * yo),
                  "short": (zs - 100) / (zs + 100), "load": (zl - 100) / (zl + 100)}
        cfg["standards"][port]["open"]["model"] = {"capacitance_pf": capacitance}
        cfg["standards"][port]["short"]["model"] = {"inductance_nh": inductance}
        cfg["standards"][port]["load"]["model"] = {"resistance_ohm": resistance, "inductance_nh": inductance}
        for kind, gamma in gammas.items():
            std = rf.Network(frequency=f, s=gamma[:, None, None], z0=100)
            m = fixture ** std
            m.write_touchstone(filename=f"{port}_{kind}", dir=out, form="ri")
    thru = line(f, z=112, delay_ns=.7, loss_db=.15)
    thru.s[:, 1, 0] *= polarity
    thru.s[:, 0, 1] *= polarity
    dut = line(f, z=93, delay_ns=17, loss_db=1.2) ** line(f, z=108, delay_ns=3, loss_db=.2)
    (left ** thru ** right).write_touchstone(filename="thru", dir=out, form="ri")
    (left ** dut ** right).write_touchstone(filename="dut", dir=out, form="ri")
    dut.write_touchstone(filename="expected_dut_100ohm", dir=out, form="ri")
    (out / "session.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return dut


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    generate(args.directory)
    print(f"Created SYNTHETIC measurements in {args.directory}")
