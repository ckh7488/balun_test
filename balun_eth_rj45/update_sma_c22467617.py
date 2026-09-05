"""Migrate the checked-in Rev-B fixture to the 1.6 mm JLC SMA.

This intentionally changes only J2-J5, their local edge launches, and the
default RSH1 assembly state.  Run with KiCad's bundled Python while KiCad is
closed.  The operation is idempotent and preserves the validated Ethernet
routing and stack-up.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import uuid

import pcbnew


HERE = Path(__file__).resolve().parent
BOARD = HERE / "balun_eth_rj45.kicad_pcb"
SCHEMATIC = HERE / "balun_eth_rj45.kicad_sch"
LOCAL_FP = HERE / "balun_eth_rj45.pretty"
SMA_NAME = "SMA_MyAntenna_A-SMA-KE-16.5A_EdgeMount"
SMA_FPID = f"balun_eth_rj45:{SMA_NAME}"
SMA_REFS = ("J2", "J3", "J4", "J5")
SMA_YS = {"J2": 29.0, "J3": 47.0, "J4": 65.0, "J5": 83.0}
DATASHEET = (
    "https://datasheet.lcsc.com/datasheet/pdf/"
    "92633ab2cf30de4413e1a152c04a3ed5.pdf?productCode=C22467617"
)


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(mm(x), mm(y))


def balanced_expression(text: str, start: int) -> tuple[str, int]:
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start:index + 1], index + 1
    raise RuntimeError("Unbalanced KiCad expression")


def update_symbol(block: str, reference: str) -> str:
    if reference in SMA_REFS:
        replacements = {
            "Footprint": SMA_FPID,
            "Datasheet": DATASHEET,
            "Manufacturer": "MyAntenna",
            "MPN": "A-SMA-KE-16.5A",
            "Assembly": "FIT; JLC C22467617; Standard PCBA / wave-solder review",
        }
        block = re.sub(r"\(in_pos_files (?:yes|no)\)", "(in_pos_files yes)", block, count=1)
        block = re.sub(r"\(dnp (?:yes|no)\)", "(dnp no)", block, count=1)
        lcsc = "C22467617"
    elif reference == "RSH1":
        replacements = {
            "Assembly": "DNP DEFAULT; hand-fit on Port-1 board only",
        }
        block = re.sub(r"\(in_pos_files (?:yes|no)\)", "(in_pos_files no)", block, count=1)
        block = re.sub(r"\(dnp (?:yes|no)\)", "(dnp yes)", block, count=1)
        lcsc = "C17477"
    else:
        return block

    for field, value in replacements.items():
        block, count = re.subn(
            rf'(\(property\s+"{re.escape(field)}"\s+")[^"]*(")',
            rf'\g<1>{value}\g<2>', block, count=1,
        )
        if count != 1:
            raise RuntimeError(f"Could not update {reference} {field}")

    if '(property "LCSC Part #"' in block:
        block = re.sub(
            r'(\(property\s+"LCSC Part #"\s+")[^"]*(")',
            rf'\g<1>{lcsc}\g<2>', block, count=1,
        )
    else:
        custom = f'''\t\t(property "LCSC Part #" "{lcsc}"
\t\t\t(at 0 0 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)'''
        block = block.replace('\t\t(pin "1"', custom + '\n\t\t(pin "1"', 1)
    return block


def render_updated_schematic() -> str:
    text = SCHEMATIC.read_text(encoding="utf-8")
    cursor = 0
    output: list[str] = []
    changed: set[str] = set()
    while True:
        start = text.find("\n\t(symbol\n", cursor)
        if start < 0:
            output.append(text[cursor:])
            break
        expr_start = start + 2
        block, end = balanced_expression(text, expr_start)
        output.append(text[cursor:expr_start])
        match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
        if match and match.group(1) in (*SMA_REFS, "RSH1"):
            reference = match.group(1)
            block = update_symbol(block, reference)
            changed.add(reference)
        output.append(block)
        cursor = end
    expected = {*SMA_REFS, "RSH1"}
    if changed != expected:
        raise RuntimeError(f"Expected {sorted(expected)}; updated {sorted(changed)}")
    return "".join(output)


def add_segment(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM,
                start: tuple[float, float], end: tuple[float, float],
                width: float, layer: int) -> None:
    segment = pcbnew.PCB_TRACK(board)
    segment.SetStart(point(*start))
    segment.SetEnd(point(*end))
    segment.SetWidth(mm(width))
    segment.SetLayer(layer)
    segment.SetNet(net)
    board.Add(segment)


def add_via(board: pcbnew.BOARD, net: pcbnew.NETINFO_ITEM,
            at: tuple[float, float]) -> None:
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(point(*at))
    via.SetWidth(mm(0.60))
    via.SetDrill(mm(0.30))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetNet(net)
    board.Add(via)


def load_sma() -> pcbnew.FOOTPRINT:
    footprint = pcbnew.PCB_IO_KICAD_SEXPR().FootprintLoad(str(LOCAL_FP), SMA_NAME, False)
    if footprint is None:
        raise RuntimeError(f"Could not load {SMA_FPID}")
    return footprint


def replace_sma(board: pcbnew.BOARD, old: pcbnew.FOOTPRINT) -> None:
    nets: dict[str, pcbnew.NETINFO_ITEM] = {}
    for pad in old.Pads():
        nets[pad.GetNumber()] = pad.GetNet()
    new = load_sma()
    new.SetReference(old.GetReference())
    new.SetValue(old.GetValue())
    new.SetFPIDAsString(SMA_FPID)
    new.SetPath(old.GetPath())
    new.SetPosition(point(97.75, SMA_YS[old.GetReference()]))
    new.SetOrientationDegrees(0)
    new.SetDNP(False)
    new.Value().SetVisible(False)
    properties = {
        "Manufacturer": "MyAntenna",
        "MPN": "A-SMA-KE-16.5A",
        "LCSC Part #": "C22467617",
        "Assembly": "FIT; JLC C22467617; Standard PCBA / wave-solder review",
        "Datasheet": DATASHEET,
    }
    for name, value in properties.items():
        new.SetField(name, value)
        new.GetField(name).SetVisible(False)
    for pad in new.Pads():
        pad.SetNet(nets[pad.GetNumber()])
    board.Remove(old)
    board.Add(new)


def migrate_launches(board: pcbnew.BOARD) -> None:
    gnd = board.FindNet("/GND")
    rf_anchors: dict[str, tuple[float, float]] = {}
    local_vias = {
        (93.8, y + delta) for y in SMA_YS.values() for delta in (-4.25, 4.25)
    } | {
        (92.2, y + delta) for y in SMA_YS.values() for delta in (-4.25, 4.25)
    } | {
        (94.2, y + delta) for y in SMA_YS.values() for delta in (-2.825, 2.825)
    } | {
        (92.6, y + delta) for y in SMA_YS.values() for delta in (-2.825, 2.825)
    }
    new_vias = {
        (x, y + delta)
        for y in SMA_YS.values()
        for x in (94.2, 92.6)
        for delta in (-2.825, 2.825)
    }
    old_vias = {
        (x, y + delta)
        for y in SMA_YS.values()
        for x in (93.8, 92.2)
        for delta in (-4.25, 4.25)
    }
    present_vias = {
        (round(pcbnew.ToMM(item.GetPosition().x), 3),
         round(pcbnew.ToMM(item.GetPosition().y), 3))
        for item in board.GetTracks()
        if isinstance(item, pcbnew.PCB_VIA) and item.GetNetname() == "/GND"
    }
    rf_at_pad = set()
    for item in board.GetTracks():
        if isinstance(item, pcbnew.PCB_VIA) or not item.GetNetname().startswith("Net-(J"):
            continue
        start = (round(pcbnew.ToMM(item.GetStart().x), 3),
                 round(pcbnew.ToMM(item.GetStart().y), 3))
        end = (round(pcbnew.ToMM(item.GetEnd().x), 3),
               round(pcbnew.ToMM(item.GetEnd().y), 3))
        for reference, y in SMA_YS.items():
            if ((97.75, y) in (start, end)
                    and abs(pcbnew.ToMM(item.GetWidth()) - 0.357) < 1e-9):
                rf_at_pad.add(reference)
    if rf_at_pad == set(SMA_REFS) and new_vias <= present_vias and not (old_vias & present_vias):
        return
    for item in list(board.GetTracks()):
        if isinstance(item, pcbnew.PCB_VIA):
            at = (round(pcbnew.ToMM(item.GetPosition().x), 3),
                  round(pcbnew.ToMM(item.GetPosition().y), 3))
            if item.GetNetname() == "/GND" and at in local_vias:
                board.Remove(item)
            continue
        start = (round(pcbnew.ToMM(item.GetStart().x), 3),
                 round(pcbnew.ToMM(item.GetStart().y), 3))
        end = (round(pcbnew.ToMM(item.GetEnd().x), 3),
               round(pcbnew.ToMM(item.GetEnd().y), 3))
        if item.GetNetname() == "/GND" and (
            (start[0] >= 93.0 or end[0] >= 93.0)
            and any(abs(start[1] - (y + d)) < 0.001 for y in SMA_YS.values() for d in (-4.25, 4.25, -2.825, 2.825))
        ):
            board.Remove(item)
        elif item.GetNetname().startswith("Net-(J") and max(start[0], end[0]) >= 95.0:
            anchor = min((start, end), key=lambda p: p[0])
            previous = rf_anchors.get(item.GetNetname())
            if previous is None or anchor[0] < previous[0]:
                rf_anchors[item.GetNetname()] = anchor
            board.Remove(item)

    for reference, y in SMA_YS.items():
        net_name = f"Net-({reference}-In)"
        net = board.FindNet(net_name)
        anchor = rf_anchors.get(net_name)
        if anchor is None:
            raise RuntimeError(f"Could not find the local RF launch for {reference}")
        add_segment(board, net, (97.75, y), (95.00, y), 0.357, pcbnew.F_Cu)
        add_segment(board, net, (95.00, y), anchor, 0.357, pcbnew.F_Cu)

    for y in SMA_YS.values():
        for sy in (y - 2.825, y + 2.825):
            add_segment(board, gnd, (97.75, sy), (94.20, sy), 0.80, pcbnew.F_Cu)
            add_segment(board, gnd, (97.75, sy), (94.20, sy), 0.80, pcbnew.B_Cu)
            add_via(board, gnd, (94.20, sy))
            add_via(board, gnd, (92.60, sy))


def update_board(destination: Path) -> None:
    board = pcbnew.LoadBoard(str(BOARD))
    if not all(board.FindFootprintByReference(ref) for ref in (*SMA_REFS, "RSH1")):
        raise RuntimeError("Missing expected SMA or RSH1 footprint")
    for reference in SMA_REFS:
        current = board.FindFootprintByReference(reference)
        if str(current.GetFPID().GetLibItemName()) != SMA_NAME:
            replace_sma(board, current)
    rsh = board.FindFootprintByReference("RSH1")
    rsh.SetDNP(True)
    rsh.SetAttributes(
        rsh.GetAttributes() | pcbnew.FP_DNP | pcbnew.FP_EXCLUDE_FROM_POS_FILES
    )
    rsh.SetField("Assembly", "DNP DEFAULT; hand-fit on Port-1 board only")
    rsh.SetField("LCSC Part #", "C17477")
    rsh.GetField("Assembly").SetVisible(False)
    rsh.GetField("LCSC Part #").SetVisible(False)
    migrate_launches(board)
    if not pcbnew.ZONE_FILLER(board).Fill(board.Zones()):
        raise RuntimeError("Could not refill PCB zones")
    if not pcbnew.SaveBoard(str(destination), board):
        raise RuntimeError(f"Could not save updated PCB: {destination}")


def _temporary_peer(path: Path, token: str, label: str) -> Path:
    return path.with_name(f".{path.stem}.{token}.{label}{path.suffix}")


def update_project_transactionally() -> None:
    """Prepare both outputs first and roll back if either atomic replace fails."""
    original = {
        SCHEMATIC: SCHEMATIC.read_bytes(),
        BOARD: BOARD.read_bytes(),
    }
    token = uuid.uuid4().hex
    schematic_temp = _temporary_peer(SCHEMATIC, token, "tmp")
    board_temp = _temporary_peer(BOARD, token, "tmp")
    board_project_temp = board_temp.with_suffix(".kicad_pro")
    replaced: list[Path] = []
    try:
        schematic_temp.write_text(render_updated_schematic(), encoding="utf-8")
        update_board(board_temp)
        # SaveBoard creates a same-basename project file for the temporary PCB.
        # Remove it before committing either real project artifact.
        board_project_temp.unlink(missing_ok=True)

        os.replace(schematic_temp, SCHEMATIC)
        replaced.append(SCHEMATIC)
        os.replace(board_temp, BOARD)
        replaced.append(BOARD)
    except BaseException as error:
        rollback_errors: list[str] = []
        for path in reversed(replaced):
            restore = _temporary_peer(path, token, "restore")
            try:
                restore.write_bytes(original[path])
                os.replace(restore, path)
            except OSError as rollback_error:
                rollback_errors.append(f"{path}: {rollback_error}")
            finally:
                restore.unlink(missing_ok=True)
        if rollback_errors:
            raise RuntimeError(
                "Migration failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            ) from error
        raise
    finally:
        schematic_temp.unlink(missing_ok=True)
        board_temp.unlink(missing_ok=True)
        board_project_temp.unlink(missing_ok=True)


def main() -> None:
    lock = HERE / "~balun_eth_rj45.kicad_pro.lck"
    if lock.exists():
        raise SystemExit(f"Close KiCad before migration: {lock}")
    update_project_transactionally()
    print("Updated RJ45 J2-J5 to C22467617 and made RSH1 DNP-by-default")


if __name__ == "__main__":
    main()
