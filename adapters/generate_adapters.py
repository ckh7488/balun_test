"""Generate three passive 100BASE-TX adapter designs with KiCad 10 pcbnew.

Creates a NEW output directory, never overwrites reviewed CAD. Reuses project
connector footprints and the RJ45 fixture stack-up. Run native DRC/ERC/parity
after generation; manufacturer mating/mechanics and impedance approval remain
separate from electrical CAD checks.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import shutil
import uuid

import pcbnew as pcb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RJ45 = "RJ45_Amphenol_RJE59-188-5401"
VARIANTS = {
    "m12_slipring": {"footprint": "Finecables_MB12FBAFF08ST-3", "mpn": "MB12FBAFF08ST-3", "pins": 8,
                     "map": {"4": "A_P", "3": "A_N", "2": "B_P", "1": "B_N"}, "rotation": 0,
                     "note": "M12 FEMALE / SLIPRING; 5-8 NC; VERIFY MATE", "gender": "female"},
    "m12_llc": {"footprint": "Finecables_MB12MBAFF08ST-3", "mpn": "MB12MBAFF08ST-3", "pins": 8,
                "map": {"8": "A_P", "2": "A_N", "3": "B_P", "4": "B_N"}, "rotation": 180,
                "note": "M12 MALE / LLC; 1,5,6,7 NC; VERIFY MATE", "gender": "male"},
    "molex_slipring": {"footprint": "Molex_5055680571", "mpn": "5055680571", "pins": 5,
                       "map": {"1": "A_P", "2": "A_N", "3": "B_P", "4": "B_N"}, "rotation": 90,
                       "note": "MOLEX 5P / SLIPRING; PIN 5 NC; VERIFY HOUSING", "gender": "male"},
}


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "balun-test/adapters/" + key))


def expression(text, start):
    depth = 0
    quoted = escaped = False
    for i in range(start, len(text)):
        c = text[i]
        if escaped:
            escaped = False
        elif c == "\\" and quoted:
            escaped = True
        elif c == '"':
            quoted = not quoted
        elif not quoted:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    raise ValueError("Unbalanced source CAD")


def point(x, y):
    return pcb.VECTOR2I(pcb.FromMM(x), pcb.FromMM(y))


def xy(obj):
    p = obj.GetPosition()
    return pcb.ToMM(p.x), pcb.ToMM(p.y)


def add_track(b, net, a, z, layer, width=.234):
    if math.dist(a, z) < 1e-8:
        return
    track = pcb.PCB_TRACK(b)
    track.SetStart(point(*a)); track.SetEnd(point(*z))
    track.SetWidth(pcb.FromMM(width)); track.SetLayer(layer); track.SetNet(net)
    b.Add(track)


def via(b, net, at):
    v = pcb.PCB_VIA(b)
    v.SetPosition(point(*at)); v.SetWidth(pcb.FromMM(.6)); v.SetDrill(pcb.FromMM(.3))
    v.SetViaType(pcb.VIATYPE_THROUGH); v.SetLayerPair(pcb.F_Cu, pcb.B_Cu); v.SetNet(net)
    b.Add(v)


def text(b, value, at, layer=pcb.F_SilkS, size=1):
    item = pcb.PCB_TEXT(b); item.SetText(value); item.SetPosition(point(*at))
    item.SetTextSize(point(size, size)); item.SetTextThickness(pcb.FromMM(.15)); item.SetLayer(layer)
    b.Add(item)


def footprint(b, name, ref, at, angle, nets, project):
    f = pcb.PCB_IO_KICAD_SEXPR().FootprintLoad(str(HERE / "adapter.pretty"), name)
    f.SetFPID(pcb.LIB_ID("adapter", name)); f.SetReference(ref); f.SetValue(name)
    f.SetPosition(point(*at)); f.SetOrientationDegrees(angle)
    f.SetPath(pcb.KIID_PATH("/" + uid(project) + "/" + uid(project + ref)))
    f.Value().SetVisible(False)
    f.Reference().SetTextSize(point(1, 1))
    f.Reference().SetTextThickness(pcb.FromMM(.15))
    for pad in f.Pads():
        if pad.GetNumber() in nets:
            pad.SetNet(nets[pad.GetNumber()])
        elif pad.GetNumber():
            isolated = pcb.NETINFO_ITEM(b, f"unconnected-({ref}-Pad{pad.GetNumber()})")
            b.Add(isolated); pad.SetNet(isolated)
    b.Add(f)
    return f


def symbol_definition(name, pins):
    pintext = []
    height = 2.54 * (len(pins) - 1)
    for i, pin in enumerate(pins):
        y = -2.54 * i
        pintext.append(f'(pin passive line (at -7.62 {y} 0) (length 5.08) (name "{pin}" (effects (font (size 1.27 1.27)))) (number "{pin}" (effects (font (size 1.27 1.27)))))')
    return f'''(symbol "Adapter:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
      (symbol "{name}_0_1" (rectangle (start -2.54 1.27) (end 2.54 {-height-1.27})
        (stroke (width .254) (type default)) (fill (type background))))
      (symbol "{name}_1_1" {''.join(pintext)}))'''


def schematic(path, name, cfg):
    definitions = symbol_definition("RJ45", [str(n) for n in range(1, 9)] + ["SH"])
    definitions += symbol_definition("DUT" + str(cfg["pins"]), [str(n) for n in range(1, cfg["pins"] + 1)])
    definitions += symbol_definition("Shield", ["1"])
    parts = []
    for ref, sym, x, count, fp, mapping in (
        ("J1", "RJ45", 71.12, 9, RJ45, {"1": "A_P", "2": "A_N", "3": "B_P", "6": "B_N", "SH": "SHIELD"}),
        ("J2", "DUT" + str(cfg["pins"]), 152.4, cfg["pins"], cfg["footprint"], cfg["map"]),
        ("TP1", "Shield", 111.76, 1, "Shield_SolderPoint", {"1": "SHIELD"}),
    ):
        fp_source = (HERE / "adapter.pretty" / (fp + ".kicad_mod")).read_text()
        match = re.search(r'\(property "Datasheet" "([^"]*)"', fp_source)
        datasheet = match.group(1) if match else ""
        match = re.search(r'\(property "Description" "([^"]*)"', fp_source)
        description = match.group(1) if match else ""
        value = "RJ45 RJE591885401" if ref == "J1" else cfg["mpn"] if ref == "J2" else "Shield_SolderPoint"
        parts.append(f'''(symbol (lib_id "Adapter:{sym}") (at {x} 63.5 0) (unit 1) (in_bom {'no' if ref == 'TP1' else 'yes'}) (on_board yes) (dnp no)
          (uuid "{uid(name+ref)}")
          (property "Reference" "{ref}" (at {x} 57.38 0) (effects (font (size 1.27 1.27))))
          (property "Value" "{value}" (at {x} 59.92 0) (effects (font (size 1.27 1.27))))
          (property "Footprint" "adapter:{fp}" (at {x} 65 0) (effects (font (size 1.27 1.27)) (hide yes)))
          (property "Datasheet" "{datasheet}" (at {x} 65 0) (effects (font (size 1.27 1.27)) (hide yes)))
          (property "Description" "{description}" (at {x} 65 0) (effects (font (size 1.27 1.27)) (hide yes)))
          (instances (project "{name}" (path "/{uid(name)}" (reference "{ref}") (unit 1)))))''')
        for i in range(count):
            pin = "SH" if i == 8 else str(i + 1)
            y = 63.5 + i * 2.54
            if pin in mapping:
                net = "SHIELD" if mapping[pin] == "SHIELD" else "PAIR_" + mapping[pin]
                parts.append(f'(wire (pts (xy {x-7.62} {y}) (xy {x-25.4} {y})) (stroke (width 0) (type default)) (uuid "{uid(name+ref+pin+"wire")}"))')
                parts.append(f'(label "{net}" (at {x-25.4} {y} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(name+ref+pin+"label")}"))')
            else:
                parts.append(f'(no_connect (at {x-7.62} {y}) (uuid "{uid(name+ref+pin+"nc")}"))')
    for i, note in enumerate((cfg["note"], "Passive two-pair adapter; no magnetics, no PoE, no active Ethernet.",
                              "100 ohm pair trunks; JLC04161H-7628; 4 layers; 1.6 mm nominal.",
                              "Inner SHIELD planes connect to RJ45 shield. M12 body bond is mechanical/external.",
                              "M12 mounting bracket and actual mating/pin numbering require sample verification.",
                              "Calibration reference plane: DUT connector mating plane after this adapter.")):
        parts.append(f'(text "{note}" (at 30 {112+i*6} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid(name+note)}"))')
    path.write_text(f'''(kicad_sch (version 20260306) (generator "eeschema") (generator_version "10.0")
      (uuid "{uid(name)}") (paper "A4")
      (title_block (title "{name} / passive Ethernet adapter") (date "2026-09-05") (rev "A-DRAFT")
        (comment 1 "ELECTRICAL CAD DRAFT; verify mating and JLC production stack before ordering"))
      (lib_symbols {definitions})
      {chr(10).join(parts)}
      (sheet_instances (path "/" (page "1"))) (embedded_fonts no))\n''', encoding="utf-8")


def board(directory, name, cfg):
    source = (ROOT / "balun_eth_rj45/balun_eth_rj45.kicad_pcb").read_text()
    blocks = [expression(source, source.index("(" + key)) for key in ("general", "layers", "setup")]
    path = directory / (name + ".kicad_pcb")
    path.write_text('(kicad_pcb (version 20260206) (generator "pcbnew") ' + "\n".join(blocks) + ')')
    b = pcb.LoadBoard(str(path))
    nets = {}
    for label in ("A_P", "A_N", "B_P", "B_N", "SHIELD"):
        n = pcb.NETINFO_ITEM(b, "/SHIELD" if label == "SHIELD" else "/PAIR_" + label)
        b.Add(n); nets[label] = n
    j1 = footprint(b, RJ45, "J1", (12, 20), 90,
                   {"1": nets["A_P"], "2": nets["A_N"], "3": nets["B_P"], "6": nets["B_N"], "SH": nets["SHIELD"]}, name)
    j2 = footprint(b, cfg["footprint"], "J2", (48, 20), cfg["rotation"],
                   {pin: nets[net] for pin, net in cfg["map"].items()}, name)
    j1.SetValue("RJ45 RJE591885401"); j2.SetValue(cfg["mpn"])
    tp = footprint(b, "Shield_SolderPoint", "TP1", (35, 28), 0, {"1": nets["SHIELD"]}, name)
    tp.Reference().SetPosition(point(35, 30.5))
    j1.Reference().SetPosition(point(12, 9)); j2.Reference().SetPosition(point(48, 9))
    starts = {"A_P": xy(j1.FindPadByNumber("1")), "A_N": xy(j1.FindPadByNumber("2")),
              "B_P": xy(j1.FindPadByNumber("3")), "B_N": xy(j1.FindPadByNumber("6"))}
    ends = {net: xy(j2.FindPadByNumber(pin)) for pin, net in cfg["map"].items()}
    if name == "m12_slipring":
        tails = {"A_P": [(42, 17.2), (44, 17.2)], "A_N": [(42, 17.65), (43.5, 19.8)],
                 "B_P": [(42, 22.7), (46.502243, 24)], "B_N": [(42, 23.15), (44, 24.45), (49.497757, 24.45)]}
        levels = {"A_P": 17.2, "A_N": 17.65, "B_P": 22.7, "B_N": 23.15}
    elif name == "m12_llc":
        tails = {"A_P": [(41, 14.55), (48, 14.55)], "A_N": [(41, 15), (46.502243, 15)],
                 "B_P": [(42, 20.0), (43.5, 19.5)], "B_N": [(42, 20.45), (43.5, 22.4)]}
        levels = {"A_P": 14.55, "A_N": 15, "B_P": 20.0, "B_N": 20.45}
    else:
        tails = {"A_P": [(42, 17.5), (44, 17.5)], "A_N": [(42, 17.95), (44, 18.75)],
                 "B_P": [(42, 20), (44, 20)], "B_N": [(42, 20.45), (44, 21.25)]}
        levels = {"A_P": 17.5, "A_N": 17.95, "B_P": 20, "B_N": 20.45}
    routes = {}
    for net, start in starts.items():
        ymid = (start[1] + levels[net]) / 2
        routes[net] = [start, (22, start[1]), (26, ymid), (30, levels[net])] + tails[net] + [ends[net]]
    length = lambda route: sum(math.dist(a, z) for a, z in zip(route, route[1:]))
    # Broad outward fanout adjustment, not a tightly packed serpentine.
    for pair in ("A", "B"):
        a, z = pair + "_P", pair + "_N"
        short = a if length(routes[a]) < length(routes[z]) else z
        target = max(length(routes[a]), length(routes[z]))
        base_y = routes[short][2][1]
        sign = -1 if short.endswith("P") else 1
        low, high = 0.0, 8.0
        for _ in range(55):
            mid = (low + high) / 2
            routes[short][2] = (26, base_y + sign * mid)
            if length(routes[short]) < target:
                low = mid
            else:
                high = mid
    # With the verified 0.234 mm width, extend this trunk by 50 um
    # before the fanout to retain the existing 0.20 mm clearance. The resulting
    # sub-0.01 mm pair skew is preferable to another long tuning detour.
    if name == "m12_slipring":
        routes["B_P"][-3] = (42.05, 22.7)
    for net, route in routes.items():
        layer = pcb.F_Cu if net.startswith("A") else pcb.B_Cu
        for i, (a, z) in enumerate(zip(route, route[1:])):
            # Molex B pair uses one symmetric signal via per conductor.
            if name == "molex_slipring" and net.startswith("B") and i == len(route) - 2:
                via(b, nets[net], a); layer = pcb.F_Cu
            add_track(b, nets[net], a, z, layer, .15 if i == 0 else .234)
    for at in ((4, 4), (62, 4), (62, 36), (4, 36)):
        hole = pcb.FOOTPRINT(b); hole.SetReference("H" + str(len(list(b.GetFootprints())) - 2))
        hole.SetAttributes(pcb.FP_BOARD_ONLY | pcb.FP_EXCLUDE_FROM_BOM | pcb.FP_EXCLUDE_FROM_POS_FILES)
        hole.SetPosition(point(*at)); hole.Reference().SetVisible(False); hole.Value().SetVisible(False)
        pad = pcb.PAD(hole); pad.SetAttribute(pcb.PAD_ATTRIB_NPTH); pad.SetShape(pcb.PAD_SHAPE_CIRCLE)
        pad.SetSize(point(3.2, 3.2)); pad.SetDrillSize(point(3.2, 3.2)); pad.SetLayerSet(pcb.LSET.AllCuMask())
        pad.SetPosition(point(*at)); hole.Add(pad)
        ring = pcb.PCB_SHAPE(hole); ring.SetShape(pcb.SHAPE_T_CIRCLE)
        ring.SetCenter(point(*at)); ring.SetEnd(point(at[0] + 3.8, at[1]))
        ring.SetLayer(pcb.F_CrtYd); ring.SetWidth(pcb.FromMM(.05)); hole.Add(ring)
        b.Add(hole)
        ring = pcb.PCB_SHAPE(); ring.SetShape(pcb.SHAPE_T_CIRCLE)
        ring.SetCenter(point(*at)); ring.SetEnd(point(at[0] + 1.9, at[1]))
        ring.SetLayer(pcb.F_SilkS); ring.SetWidth(pcb.FromMM(.12)); b.Add(ring)
    corners = [(0, 0), (66, 0), (66, 40), (0, 40), (0, 0)]
    for a, z in zip(corners, corners[1:]):
        edge = pcb.PCB_SHAPE(); edge.SetShape(pcb.SHAPE_T_SEGMENT); edge.SetStart(point(*a)); edge.SetEnd(point(*z))
        edge.SetLayer(pcb.Edge_Cuts); edge.SetWidth(pcb.FromMM(.05)); b.Add(edge)
    for layer in (pcb.In1_Cu, pcb.In2_Cu):
        zone = pcb.ZONE(b); zone.SetLayer(layer); zone.SetNet(nets["SHIELD"])
        zone.SetLocalClearance(pcb.FromMM(.25)); zone.SetMinThickness(pcb.FromMM(.2))
        zone.SetPadConnection(pcb.ZONE_CONNECTION_THERMAL)
        zone.SetThermalReliefGap(pcb.FromMM(.25)); zone.SetThermalReliefSpokeWidth(pcb.FromMM(.3))
        zone.Outline().NewOutline()
        for x, y in corners[:-1]: zone.Outline().Append(pcb.FromMM(x), pcb.FromMM(y))
        b.Add(zone)
    for at in ((9, 7), (20, 7), (35, 7), (57, 7), (6, 32), (20, 32), (35, 32), (57, 32), (43, 16), (43, 25)):
        via(b, nets["SHIELD"], at)
    if name == "molex_slipring":
        for at in ((43, 19.3), (43, 22.25)):
            via(b, nets["SHIELD"], at)
    text(b, name.upper().replace("_", " "), (33, 2), size=1.2)
    text(b, "100BASE-TX / PASSIVE ONLY", (33, 34), size=1)
    text(b, "A-DRAFT / VERIFY MATE + CAM", (33, 37), size=.8)
    title = b.GetTitleBlock(); title.SetTitle(name + " passive adapter"); title.SetRevision("A-DRAFT")
    title.SetDate("2026-09-05"); title.SetComment(0, cfg["note"])
    title.SetComment(1, "JLC04161H-7628 / 100R trunk W0.234 G0.216 / verify manufacturer mating")
    pcb.SaveBoard(str(path), b)
    return {k: {"length_mm": length(v), "signal_vias": int(name == "molex_slipring" and k.startswith("B")),
                "vertices_mm": v} for k, v in routes.items()}


def generate(output):
    output.mkdir(parents=True, exist_ok=False)
    project = json.loads((ROOT / "balun_eth_rj45/balun_eth_rj45.kicad_pro").read_text())
    project["net_settings"]["netclass_patterns"] = [{"netclass": "ETH100", "pattern": "/PAIR_*"}]
    project["board"]["design_settings"]["drc_exclusions"] = []
    for name, cfg in VARIANTS.items():
        directory = output / name; directory.mkdir()
        (directory / "fp-lib-table").write_text('(fp_lib_table (version 7) (lib (name "adapter")(type "KiCad")(uri "${KIPRJMOD}/../adapter.pretty")(options "")(descr "Project-local reviewed connector footprints")))\n')
        (directory / "sym-lib-table").write_text('(sym_lib_table (version 7) (lib (name "Adapter")(type "KiCad")(uri "${KIPRJMOD}/../adapter.kicad_sym")(options "")(descr "Passive adapter symbols")))\n')
        (directory / (name + ".kicad_pro")).write_text(json.dumps(project, indent=2) + "\n")
        schematic(directory / (name + ".kicad_sch"), name, cfg)
        metrics = board(directory, name, cfg)
        (directory / "design.json").write_text(json.dumps({"status": "ELECTRICAL_CAD_DRAFT", **cfg, "routing": metrics}, indent=2) + "\n")
        (directory / (name + ".kicad_dru")).write_text('''(version 1)
(rule "Board edge" (constraint edge_clearance (min 0.30mm)))
(rule "Inner planes only" (layer inner) (constraint disallow track))
(rule "Differential trace width" (layer outer) (condition "A.Type == 'Track' && A.hasNetclass('ETH100')") (constraint track_width (min 0.233mm) (opt 0.234mm) (max 0.235mm)))
(rule "RJ45 pin escape" (condition "A.Type == 'Track' && A.hasNetclass('ETH100') && A.intersectsCourtyard('J1')") (constraint track_width (min 0.14mm) (opt 0.15mm) (max 0.235mm)))
(rule "Signal vias" (condition "A.Type == 'Via' && A.hasNetclass('ETH100')") (constraint via_diameter (min 0.60mm)) (constraint hole_size (min 0.30mm)))
''')
    shutil.copytree(HERE / "adapter.pretty", output / "adapter.pretty")
    definitions = symbol_definition("RJ45", [str(n) for n in range(1, 9)] + ["SH"])
    definitions += symbol_definition("DUT8", [str(n) for n in range(1, 9)])
    definitions += symbol_definition("DUT5", [str(n) for n in range(1, 6)])
    definitions += symbol_definition("Shield", ["1"])
    (output / "adapter.kicad_sym").write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") ' + definitions.replace('"Adapter:', '"') + ')\n')
    print(f"Generated {output}; run native DRC/ERC/parity and inspect before fabrication.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    generate(parser.parse_args().output)
