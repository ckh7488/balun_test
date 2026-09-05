"""Check the LLC draft's exported KiCad XML netlist against its reviewed spec."""

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent


def verify(path: Path) -> None:
    spec = json.loads((HERE / "fixture_spec.json").read_text(encoding="utf-8"))
    root = ET.parse(path).getroot()
    nets = {
        node.attrib["name"]: {(p.attrib["ref"], p.attrib["pin"]) for p in node.findall("node")}
        for node in root.findall("./nets/net")
    }
    assert len(nets) == 15, "Unexpected added or merged nets"
    targets = {
        "PAIR_TX_P": ("T1", "4"), "PAIR_TX_N": ("T1", "6"),
        "PAIR_RX_P": ("T2", "4"), "PAIR_RX_N": ("T2", "6"),
    }
    for pin, name in spec["pin_nets"].items():
        memberships = [nodes for nodes in nets.values() if ("J1", pin) in nodes]
        assert len(memberships) == 1, (pin, memberships)
        expected = {("J1", pin)} if name is None else {("J1", pin), targets[name]}
        assert memberships[0] == expected, (pin, expected, memberships[0])
        if name is not None:
            assert nets["/" + name] == expected
    assert nets["/RF_A_50"] == {("J2", "1"), ("T1", "3")}
    assert nets["/RF_B_50"] == {("J3", "1"), ("T2", "3")}
    assert nets["/GND"] == {("J2", "2"), ("J3", "2"), ("T1", "1"), ("T2", "1"), ("RCT1", "1"), ("RCT2", "1")}
    assert nets["/CT_A"] == {("T1", "5"), ("RCT1", "2")}
    assert nets["/CT_B"] == {("T2", "5"), ("RCT2", "2")}
    for transformer in ("T1", "T2"):
        memberships = [nodes for nodes in nets.values() if (transformer, "2") in nodes]
        assert memberships == [{(transformer, "2")}], "Balun pin 2 must stay NC"
    components = {c.attrib["ref"]: c for c in root.findall("./components/comp")}
    assert set(components) == {"J1", "J2", "J3", "T1", "T2", "RCT1", "RCT2"}
    assert components["J1"].findtext("footprint") == "balun_llc16:Finecables_MB12MBAFF08ST-3"
    assert components["J1"].findtext("value") == "MB12MBAFF08ST-3 / M12 MALE"
    j1_fields = {f.attrib["name"]: f.text or "" for f in components["J1"].findall("./fields/field")}
    assert j1_fields["MPN"] == spec["connector_pcb_mpn"] == "MB12MBAFF08ST-3"
    assert spec["status"] == "PCB_DRAFT_A_DO_NOT_ORDER"
    assert spec["connector_pcb_jlc_sourcing_confirmed"] is False
    assert spec["connector_dut_gender_confirmed"] == "female_socket"
    assert spec["connector_pcb_required_gender"] == "male_pin"
    assert spec["connector_same_as_slipring"] is False
    assert spec["pinmap_design_status"] == "ACCEPTED_FOR_CIRCUIT_AND_PCB_DESIGN"
    assert spec["continuity_required_before_pcb_design"] is False
    assert spec["actual_cable_continuity_verified"] is False
    assert components["T1"].findtext("value") == "ADT2-1T+"
    assert components["T2"].findtext("value") == "ADT2-1T+"
    assert spec["connector_population"] == "REQUIRED_FIT_SUPPLIER_APPROVAL_PENDING"
    for reference in ("RCT1", "RCT2"):
        properties = {p.attrib["name"] for p in components[reference].findall("property")}
        assert "dnp" in properties, (reference, properties)
    for reference in ("J1", "J2", "J3", "T1", "T2"):
        properties = {p.attrib["name"] for p in components[reference].findall("property")}
        assert "dnp" not in properties, (reference, "Required component incorrectly marked DNP")
    assert {(r["m12"], r["rj45"]) for r in spec["dut_continuity_expected"]} == {(8, 1), (2, 2), (3, 3), (4, 6)}
    assert set(spec["power_pins_nc_on_fixture"]) == {"1", "5", "6", "7"}
    assert spec["quantity"] == 2 and spec["total_requested_pcbas"] == 4 + 4 + 2
    assert spec["unused_coax_loads_for_llc_measurement"] == 2 + 4 - 2
    assert spec["shared_load_kit_quantity"] >= spec["unused_coax_loads_for_llc_measurement"]
    print("PASS: selected male-mate footprint, all eight M12 pins, both RF paths, power-pin isolation, DNP states, shared quantities and fabrication HOLD")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("netlist", type=Path)
    verify(parser.parse_args().netlist)
