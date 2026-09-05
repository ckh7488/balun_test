import json

import numpy as np
import pytest
import skrf as rf

from analysis.m12_cal import corrected, fit, load_cal, main, read_network, save_cal, standard_model
from analysis.synthetic_demo import generate


@pytest.mark.parametrize("nonideal,polarity", [(False, 1), (True, 1), (True, -1)])
def test_recover_independent_cascade_and_reuse(tmp_path, nonideal, polarity):
    folder = tmp_path / "synthetic"
    expected = generate(folder, nonideal, polarity)
    cal, metadata = fit(folder / "session.json")
    save_cal(folder / "cal.npz", cal, metadata)
    loaded, stored_meta = load_cal(folder / "cal.npz")
    result = corrected(loaded, read_network(folder / "dut.s2p", 2))
    np.testing.assert_allclose(result.s, expected.s, atol=2e-11, rtol=0)
    np.testing.assert_allclose(result.z0, 100)
    assert len(stored_meta["input_sha256"]) == 7


def test_load_100ohm_is_not_match_at_internal_50ohm_reference():
    f = rf.Frequency(1, 100, 5, unit="mhz")
    model = standard_model(f, "load", {"resistance_ohm": 100})
    np.testing.assert_allclose(model.s[:, 0, 0], 1 / 3)
    model.renormalize(100)
    np.testing.assert_allclose(model.s, 0, atol=1e-15)


def test_port2_s2p_uses_s22_and_rejects_bad_grid(tmp_path):
    folder = tmp_path / "synthetic"
    expected = generate(folder)
    cfg = json.loads((folder / "session.json").read_text())
    for kind in ("open", "short", "load"):
        n = rf.Network(str(folder / f"p2_{kind}.s1p"))
        s = np.zeros((len(n.f), 2, 2), complex)
        s[:, 0, 0] = .77  # deliberately unrelated S11
        s[:, 1, 1] = n.s[:, 0, 0]
        rf.Network(frequency=n.frequency, s=s, z0=50).write_touchstone(filename=f"p2_{kind}", dir=folder)
        cfg["standards"]["p2"][kind]["file"] = f"p2_{kind}.s2p"
    (folder / "session.json").write_text(json.dumps(cfg))
    cal, _ = fit(folder / "session.json")
    n = read_network(folder / "dut.s2p", 2)
    np.testing.assert_allclose(corrected(cal, n).s, expected.s, atol=2e-11)
    with pytest.raises(ValueError, match="grid"):
        corrected(cal, n[::2])
    n.renormalize(100)
    with pytest.raises(ValueError, match="50-ohm"):
        corrected(cal, n)


def test_cli_export_and_preserve_inputs(tmp_path):
    folder = tmp_path / "synthetic"
    generate(folder)
    raw = (folder / "dut.s2p").read_bytes()
    main(["calibrate", str(folder / "session.json"), "--out", str(folder / "cal.npz")])
    main(["apply", str(folder / "cal.npz"), str(folder / "dut.s2p"), "--out", str(folder / "results")])
    for suffix in ("s2p", "csv", "png", "json"):
        assert (folder / "results" / f"dut_m12.{suffix}").stat().st_size > 0
    assert (folder / "dut.s2p").read_bytes() == raw
    output = rf.Network(str(folder / "results" / "dut_m12.s2p"))
    np.testing.assert_allclose(output.z0, 100)


def test_wrong_stage_and_duplicate_files_fail(tmp_path):
    folder = tmp_path / "synthetic"
    generate(folder)
    path = folder / "session.json"
    cfg = json.loads(path.read_text())
    cfg["input_stage"] = "raw"
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError, match="SMA SOLT"):
        fit(path)
    cfg["input_stage"] = "full_two_port_sma_solt"
    cfg["standards"]["p2"]["open"]["file"] = "p1_open.s1p"
    path.write_text(json.dumps(cfg))
    with pytest.raises(ValueError, match="Duplicate"):
        fit(path)
