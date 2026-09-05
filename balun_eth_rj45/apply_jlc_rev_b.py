"""Upgrade the saved fixture PCB to the validated JLCPCB Rev-B layout.

This updater preserves placement and non-Ethernet routing, replaces the four
Ethernet routes, installs the JLC04161H-7628 stack/rules, and removes blanket
outer-layer GND zones.  Close KiCad before running it against the real project.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path


PROJECT_BASENAME = "balun_eth_rj45"
KICAD_PYTHON = Path(r"C:\Program Files\KiCad\10.0\bin\python.exe")
KICAD_CLI = KICAD_PYTHON.with_name("kicad-cli.exe")
ETH_NETS = {
    "/DA_P", "/DA_N", "/DB_P", "/DB_N",
    "/DC_P", "/DC_N", "/DD_P", "/DD_N",
}
RF_NETS = {
    "Net-(J2-In)", "Net-(J3-In)", "Net-(J4-In)", "Net-(J5-In)",
}
UUID_NAMESPACE = uuid.UUID("b8cd363d-7b5e-48f7-97f0-7a06a2f668a4")

# Pair-B changes reference from L3 to L2 at these two signal vias.  Move the
# four plane-stitching vias from the original conservative 2.468 mm spacing to
# a symmetric 1.355 mm signal-to-GND centre spacing.
PAIR_B_RETURN_VIA_MOVES = {
    (59.0, 42.5): (60.0, 43.2),
    (62.0, 42.5): (61.0, 43.2),
    (59.0, 51.5): (60.0, 50.8),
    (62.0, 51.5): (61.0, 50.8),
}
PAIR_B_RETURN_VIA_TARGETS = frozenset(PAIR_B_RETURN_VIA_MOVES.values())


DRU_TEXT = """(version 1)

# JLCPCB 4-layer standard impedance stack:
# JLC04161H-7628, order as 1.6 mm, finished stack nominal 1.5862 mm.
# Outer-layer structures are non-coplanar microstrip referenced to L2/L3.

(rule "Controlled traces isolated from other controlled signals"
    (condition "(A.Type == 'Track' || A.Type == 'Via') && (B.Type == 'Track' || B.Type == 'Via') && (A.hasNetclass('ETH100') || A.hasNetclass('RF50')) && (B.hasNetclass('ETH100') || B.hasNetclass('RF50')) && !AB.isCoupledDiffPair() && !A.intersectsCourtyard('J1') && !B.intersectsCourtyard('J1') && !A.intersectsCourtyard('T?') && !B.intersectsCourtyard('T?')")
    # 0.60 mm is over 2.5 trace widths and almost 3x the 0.2104 mm plane
    # spacing.  Keep more where placement permits, but do not force long
    # uncoupled detours at the RJ45 fanout.
    (constraint clearance (min 0.60mm))
)

(rule "Copper to board edge"
    (constraint edge_clearance (min 0.30mm))
)

(rule "No routing on solid inner GND planes"
    (layer inner)
    (constraint disallow track)
)

(rule "Only GND zones on inner copper"
    (layer inner)
    (condition "A.Type == 'Zone' && A.NetName != '/GND'")
    (constraint disallow zone)
)

(rule "JLC 50 ohm outer geometry"
    (layer outer)
    (condition "A.Type == 'Track' && A.hasNetclass('RF50')")
    (constraint track_width (min 0.356mm) (opt 0.357mm) (max 0.358mm))
)

(rule "JLC 100 ohm differential trace width"
    (layer outer)
    (condition "A.Type == 'Track' && A.hasNetclass('ETH100')")
    (constraint track_width (min 0.233mm) (opt 0.234mm) (max 0.235mm))
)

(rule "JLC 100 ohm differential coupled gap"
    (layer outer)
    (condition "A.Type == 'Track' && A.hasNetclass('ETH100') && !A.intersectsCourtyard('J1') && !A.intersectsCourtyard('T?')")
    # The pair intentionally opens at connector/transformer fanouts.  A
    # maximum here creates false errors after KiCad reclassifies those short
    # sections; the uncoupled-length rules below limit how far that can extend.
    (constraint diff_pair_gap (min 0.21mm) (opt 0.216mm))
)

(rule "Ethernet pair topology"
    (condition "A.hasNetclass('ETH100')")
    # Offset bends create about 0.52 mm of local inside/outside path delta;
    # the transformer-end compensation restores zero end-to-end pair skew.
    (constraint skew (max 0.55mm) (within_diff_pairs))
    (constraint via_count (max 1))
)

(rule "Ethernet ordinary-pair uncoupled allowance"
    (condition "A.hasNetclass('ETH100') && A.NetName != '/DB_P' && A.NetName != '/DB_N'")
    (constraint diff_pair_uncoupled (max 16.00mm))
)

# 1000BASE-T pair B uses split RJ45 pins 3 and 6, with pins 4/5 between them.
(rule "Ethernet split-pair B uncoupled allowance"
    (condition "A.NetName == '/DB_P' || A.NetName == '/DB_N'")
    (constraint diff_pair_uncoupled (max 16.50mm))
)

(rule "Ethernet signal via geometry"
    (condition "A.Type == 'Via' && A.hasNetclass('ETH100')")
    (constraint via_diameter (min 0.60mm) (opt 0.60mm) (max 0.60mm))
    (constraint hole_size (min 0.30mm) (opt 0.30mm) (max 0.30mm))
)

# J1 uses 1.30/0.90 mm PTH pads (0.20 mm annular ring).  The short 0.15 mm
# pin-field escape keeps at least 0.295 mm copper clearance to adjacent PTHs.
(rule "RJ45 pin-field neckdown"
    (condition "A.Type == 'Track' && A.hasNetclass('ETH100') && A.intersectsCourtyard('J1')")
    (constraint track_width (min 0.14mm) (opt 0.15mm) (max 0.235mm))
)

(rule "RJ45 PTH to signal escape clearance"
    (condition "A.memberOfFootprint('J1') && A.Type == 'Pad' && B.hasNetclass('ETH100') && A.Net != B.Net")
    (constraint clearance (min 0.28mm))
)

(rule "RJ45 local signal fanout clearance"
    (condition "A.Type == 'Track' && B.Type == 'Track' && A.hasNetclass('ETH100') && B.hasNetclass('ETH100') && A.intersectsCourtyard('J1') && B.intersectsCourtyard('J1')")
    (constraint clearance (min 0.18mm))
)

# Edge-launch pads intentionally meet the routed edge.  This exception must be
# after the general edge rule because KiCad evaluates matching rules last-first.
(rule "SMA edge-launch exception"
    (condition "A.memberOfFootprint('J2') || A.memberOfFootprint('J3') || A.memberOfFootprint('J4') || A.memberOfFootprint('J5')")
    (constraint edge_clearance (min -0.10mm))
)
"""


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}; found {count}")
    return text.replace(old, new, 1)


def _root_child_spans(text: str) -> list[tuple[int, int]]:
    """Return byte-index-like character spans for root-level s-expressions."""
    spans: list[tuple[int, int]] = []
    depth = 0
    start: int | None = None
    in_string = False
    escaped = False
    for index, char in enumerate(text):
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
            if depth == 2:
                start = index
        elif char == ")":
            if depth == 2 and start is not None:
                spans.append((start, index + 1))
                start = None
            depth -= 1
            if depth < 0:
                raise RuntimeError("Unbalanced closing parenthesis in PCB")
    if depth != 0 or in_string:
        raise RuntimeError("Unbalanced PCB s-expression")
    return spans


def _strip_zone_fill_cache(zone: str) -> str:
    """Remove stale cached fill so new signal vias cannot overlap old GND fill."""
    output: list[str] = []
    cursor = 0
    for start, end in _root_child_spans(zone):
        child = zone[start:end]
        output.append(zone[cursor:start])
        if not child.startswith("(filled_polygon") and not child.startswith("(fill_segments"):
            output.append(child)
        cursor = end
    output.append(zone[cursor:])
    return "".join(output)


def _stable_uuid(name: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, name))


def _find_kicad_cli() -> Path:
    """Return the KiCad CLI paired with the configured pcbnew runtime."""
    if KICAD_CLI.exists():
        return KICAD_CLI
    discovered = shutil.which("kicad-cli")
    if discovered:
        return Path(discovered)
    raise RuntimeError(f"KiCad CLI is missing: {KICAD_CLI}")


def _assert_saved_inner_plane_fills(board_path: Path) -> None:
    """Require one saved, filled /GND zone on each inner copper layer."""
    text = board_path.read_text(encoding="utf-8")
    plane_fills: dict[str, int] = {"In1.Cu": 0, "In2.Cu": 0}
    for start, end in _root_child_spans(text):
        block = text[start:end]
        if not block.startswith("(zone") or '(net "/GND")' not in block:
            continue
        for layer in plane_fills:
            if f'(layer "{layer}")' in block:
                if "(filled_polygon" not in block and "(fill_segments" not in block:
                    raise RuntimeError(f"Saved {layer} /GND zone has no fill cache")
                plane_fills[layer] += 1

    invalid = {layer: count for layer, count in plane_fills.items() if count != 1}
    if invalid:
        raise RuntimeError(
            "Expected exactly one saved, filled /GND zone on each inner layer; "
            f"found {invalid}"
        )


def refill_and_validate_project(project_dir: Path) -> None:
    """Refill/save zones, then require a clean DRC and schematic parity check."""
    board_path = project_dir / f"{PROJECT_BASENAME}.kicad_pcb"
    cli = _find_kicad_cli()
    with tempfile.TemporaryDirectory(prefix="balun_rev_b_drc_") as report_dir:
        report_path = Path(report_dir) / f"{PROJECT_BASENAME}_post_migration_drc.rpt"
        result = subprocess.run(
            [
                str(cli),
                "pcb",
                "drc",
                "--output",
                str(report_path),
                "--format",
                "report",
                "--all-track-errors",
                "--schematic-parity",
                "--units",
                "mm",
                "--severity-all",
                "--exit-code-violations",
                "--refill-zones",
                "--save-board",
                str(board_path),
            ],
            cwd=project_dir,
            check=False,
        )
        if result.returncode:
            if report_path.exists():
                report = report_path.read_text(encoding="utf-8", errors="replace")
            else:
                report = "DRC report was not created."
            raise RuntimeError(
                f"Post-migration KiCad DRC/parity failed with exit "
                f"{result.returncode}:\n{report}"
            )
    _assert_saved_inner_plane_fills(board_path)
    print("Post-migration zone refill/save, DRC, and schematic parity: PASS")


def _migrate_pair_b_return_via(
    block: str,
) -> tuple[str, tuple[float, float] | None]:
    """Move or recognize one of the four symmetric pair-B return vias."""
    at_match = re.search(r'\(at (-?[0-9.]+) (-?[0-9.]+)\)', block)
    if not at_match:
        return block, None
    at = (float(at_match.group(1)), float(at_match.group(2)))
    target = PAIR_B_RETURN_VIA_MOVES.get(at)
    if target is None:
        if at not in PAIR_B_RETURN_VIA_TARGETS:
            return block, None
        target = at
    replacement = f"(at {target[0]:g} {target[1]:g})"
    block, count = re.subn(r'\(at -?[0-9.]+ -?[0-9.]+\)', replacement, block, count=1)
    if count != 1:
        raise RuntimeError(f"Could not update pair-B return via at {at}")
    return block, target


def _local_ground_objects(newline: str) -> str:
    objects: list[str] = []

    # Retain short L2/L3 connections for the optional bottom-side centre-tap
    # grounding resistors after blanket B.Cu is removed.  RCT1-RCT4 remain
    # DNP for the CT-FLOAT baseline; populate all eight parts across both
    # fixture boards only for a controlled CT-GND comparison.
    for ref, x, y, via_x, via_y in (
        # Keep the through-via outside pair A's top-layer fanout corridor.
        ("RCT1", 58.0, 29.0, 58.0, 24.0),
        # Pair C runs across y=64.775/65.225 on F.Cu, so put the through-via
        # below that corridor instead of punching through the differential pair.
        ("RCT3", 58.0, 65.0, 58.0, 68.0),
        # Keep the T4 centre-tap reference compact without crowding DD_P/N.
        ("RCT4", 58.0, 83.0, 57.5, 84.2),
    ):
        x_text = f"{x:g}"
        y_text = f"{y:g}"
        via_x_text = f"{via_x:g}"
        via_y_text = f"{via_y:g}"
        objects.append(
            f"(segment{newline}"
            f"\t\t(start {x_text} {y_text}){newline}"
            f"\t\t(end {via_x_text} {via_y_text}){newline}"
            f"\t\t(width 0.5){newline}"
            f"\t\t(layer \"B.Cu\"){newline}"
            f"\t\t(net \"/GND\"){newline}"
            f"\t\t(uuid \"{_stable_uuid(ref + '-gnd-track')}\"){newline}"
            f"\t)"
        )
        objects.append(
            f"(via{newline}"
            f"\t\t(at {via_x_text} {via_y_text}){newline}"
            f"\t\t(size 0.6){newline}"
            f"\t\t(drill 0.3){newline}"
            f"\t\t(layers \"F.Cu\" \"B.Cu\"){newline}"
            f"\t\t(net \"/GND\"){newline}"
            f"\t\t(uuid \"{_stable_uuid(ref + '-gnd-via')}\"){newline}"
            f"\t)"
        )

    # The selected C22467617 edge SMA has separate top and bottom ground
    # paddles at +/-2.825 mm.  The dedicated migration below replaces these
    # provisional objects with the exact idempotent local launch.
    for ref, y in (
        ("J2A", 26.175), ("J2B", 31.825),
        ("J3A", 44.175), ("J3B", 49.825),
        ("J4A", 62.175), ("J4B", 67.825),
        ("J5A", 80.175), ("J5B", 85.825),
    ):
        y_text = f"{y:g}"
        objects.append(
            f"(segment{newline}"
            f"\t\t(start 97.75 {y_text}){newline}"
            f"\t\t(end 94.2 {y_text}){newline}"
            f"\t\t(width 0.8){newline}"
            f"\t\t(layer \"B.Cu\"){newline}"
            f"\t\t(net \"/GND\"){newline}"
            f"\t\t(uuid \"{_stable_uuid(ref + '-bottom-gnd-track')}\"){newline}"
            f"\t)"
        )

    return (newline + "\t").join(objects)


def _coordinate(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _segment_object(
    newline: str,
    name: str,
    net: str,
    layer: str,
    start: tuple[float, float],
    end: tuple[float, float],
    width: float = 0.234,
) -> str:
    return (
        f"(segment{newline}"
        f"\t\t(start {_coordinate(start[0])} {_coordinate(start[1])}){newline}"
        f"\t\t(end {_coordinate(end[0])} {_coordinate(end[1])}){newline}"
        f"\t\t(width {_coordinate(width)}){newline}"
        f"\t\t(layer \"{layer}\"){newline}"
        f"\t\t(net \"{net}\"){newline}"
        f"\t\t(uuid \"{_stable_uuid('rev-b-route-' + name)}\"){newline}"
        f"\t)"
    )


def _via_object(newline: str, name: str, net: str, at: tuple[float, float]) -> str:
    return (
        f"(via{newline}"
        f"\t\t(at {_coordinate(at[0])} {_coordinate(at[1])}){newline}"
        f"\t\t(size 0.6){newline}"
        f"\t\t(drill 0.3){newline}"
        f"\t\t(layers \"F.Cu\" \"B.Cu\"){newline}"
        f"\t\t(net \"{net}\"){newline}"
        f"\t\t(uuid \"{_stable_uuid('rev-b-route-' + name)}\"){newline}"
        f"\t)"
    )


def _parallel_trunk(
    center_start: tuple[float, float], center_end: tuple[float, float]
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Return P-start, P-end, N-start, N-end at 0.45 mm center spacing."""
    dx = center_end[0] - center_start[0]
    dy = center_end[1] - center_start[1]
    length = math.hypot(dx, dy)
    normal = (-dy / length, dx / length)
    offset = (normal[0] * 0.225, normal[1] * 0.225)
    plus_start = (center_start[0] + offset[0], center_start[1] + offset[1])
    plus_end = (center_end[0] + offset[0], center_end[1] + offset[1])
    minus_start = (center_start[0] - offset[0], center_start[1] - offset[1])
    minus_end = (center_end[0] - offset[0], center_end[1] - offset[1])
    if plus_start[1] < minus_start[1]:
        return plus_start, plus_end, minus_start, minus_end
    return minus_start, minus_end, plus_start, plus_end


def _legacy_rev_a_route_objects(newline: str) -> list[str]:
    """Restore the validated, length-matched Rev-A topology at JLC widths."""
    objects: list[str] = []

    def add_polyline(name: str, net: str, layer: str, points: list[tuple[float, float]], neck: bool = False) -> None:
        for index, (start, end) in enumerate(zip(points, points[1:])):
            width = 0.20 if neck and index == 0 else 0.234
            objects.append(_segment_object(newline, f"{name}-{index}", net, layer, start, end, width))

    add_polyline("A-P", "/DA_P", "F.Cu", [
        (35.43, 53.39), (36.50, 52.32), (38.50, 52.32), (41.50, 50.39),
        (51.50, 28.775), (56.00, 28.775), (59.00, 26.46), (62.96, 26.46),
    ], neck=True)
    add_polyline("A-N", "/DA_N", "F.Cu", [
        (37.46, 54.41), (39.50, 54.41), (42.50, 51.41),
        (52.50, 29.225), (53.00, 29.225), (53.00, 29.86465),
        (54.00, 29.86465), (54.00, 29.225), (56.00, 29.225),
        (59.00, 31.54), (62.96, 31.54),
    ], neck=True)

    add_polyline("B-P", "/DB_P", "B.Cu", [
        (35.43, 55.43), (33.00, 55.43), (33.00, 52.00), (42.00, 52.00),
        (48.00, 46.775), (58.00, 46.775), (60.50, 44.46),
    ], neck=True)
    add_polyline("B-N", "/DB_N", "B.Cu", [
        (37.46, 58.49), (40.50, 58.49), (44.00, 55.00),
        (49.00, 47.225), (51.00, 47.225), (51.00, 50.51975),
        (53.00, 50.51975), (53.00, 47.225), (58.00, 47.225),
        (60.50, 49.54),
    ], neck=True)
    for polarity, net, point in (
        ("P", "/DB_P", (60.50, 44.46)),
        ("N", "/DB_N", (60.50, 49.54)),
    ):
        objects.append(_via_object(newline, f"B-{polarity}-via", net, point))
        objects.append(_segment_object(newline, f"B-{polarity}-top", net, "F.Cu", point, (62.96, point[1])))

    add_polyline("C-P-bottom", "/DC_P", "B.Cu", [(37.46, 56.45), (39.50, 56.45)], neck=True)
    objects.append(_via_object(newline, "C-P-via", "/DC_P", (39.50, 56.45)))
    add_polyline("C-P-top", "/DC_P", "F.Cu", [
        (39.50, 56.45), (42.50, 59.45), (50.50, 64.775), (50.80, 64.775),
        (50.80, 62.57547), (51.50, 62.57547), (51.50, 64.775),
        (52.00, 64.775), (52.00, 62.57547), (52.70, 62.57547),
        (52.70, 64.775), (53.20, 64.775), (53.20, 62.57547),
        (53.90, 62.57547), (53.90, 64.775), (56.00, 64.775),
        (59.00, 62.46), (62.96, 62.46),
    ])
    add_polyline("C-N-bottom", "/DC_N", "B.Cu", [
        (35.43, 57.47), (32.70, 57.47), (32.70, 66.00),
    ], neck=True)
    objects.append(_via_object(newline, "C-N-via", "/DC_N", (32.70, 66.00)))
    add_polyline("C-N-top", "/DC_N", "F.Cu", [
        (32.70, 66.00), (40.00, 66.00), (50.00, 65.225), (56.00, 65.225),
        (59.00, 67.54), (62.96, 67.54),
    ])

    add_polyline("D-P-bottom", "/DD_P", "B.Cu", [
        (35.43, 59.51), (34.00, 59.51), (34.00, 70.50), (43.00, 70.50),
    ], neck=True)
    objects.append(_via_object(newline, "D-P-via", "/DD_P", (43.00, 70.50)))
    add_polyline("D-P-top", "/DD_P", "F.Cu", [
        (43.00, 70.50), (49.00, 76.50), (56.00, 82.775),
        (59.00, 80.46), (62.96, 80.46),
    ])
    add_polyline("D-N-bottom", "/DD_N", "B.Cu", [
        (37.46, 60.53), (40.00, 60.53), (46.00, 64.50), (46.00, 74.50),
    ], neck=True)
    objects.append(_via_object(newline, "D-N-via", "/DD_N", (46.00, 74.50)))
    add_polyline("D-N-top", "/DD_N", "F.Cu", [
        (46.00, 74.50), (51.00, 79.50), (56.00, 84.00),
        (59.00, 85.54), (59.50, 85.54), (59.50, 88.63545),
        (61.00, 88.63545), (61.00, 85.54), (62.96, 85.54),
    ])

    return objects


def _detour_midpoint(
    start: tuple[float, float],
    end: tuple[float, float],
    extra_length: float,
    normal_sign: float,
) -> tuple[float, float]:
    """Return a midpoint that adds exactly extra_length to a two-leg path."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    direct = math.hypot(dx, dy)
    offset = 0.5 * math.sqrt((direct + extra_length) ** 2 - direct ** 2)
    normal = (-dy / direct, dx / direct)
    return (
        (start[0] + end[0]) / 2 + normal_sign * offset * normal[0],
        (start[1] + end[1]) / 2 + normal_sign * offset * normal[1],
    )


def _offset_polyline(
    centerline: list[tuple[float, float]], side: float, distance: float = 0.225
) -> list[tuple[float, float]]:
    """Offset a polyline with mitered corners for a constant pair gap."""
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for start, end in zip(centerline, centerline[1:]):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        unit = (dx / length, dy / length)
        normal = (-unit[1], unit[0])
        segments.append((unit, normal))

    result = [(
        centerline[0][0] + side * distance * segments[0][1][0],
        centerline[0][1] + side * distance * segments[0][1][1],
    )]

    def cross(a: tuple[float, float], b: tuple[float, float]) -> float:
        return a[0] * b[1] - a[1] * b[0]

    for index, vertex in enumerate(centerline[1:-1], 1):
        previous_unit, previous_normal = segments[index - 1]
        next_unit, next_normal = segments[index]
        previous_point = (
            vertex[0] + side * distance * previous_normal[0],
            vertex[1] + side * distance * previous_normal[1],
        )
        next_point = (
            vertex[0] + side * distance * next_normal[0],
            vertex[1] + side * distance * next_normal[1],
        )
        denominator = cross(previous_unit, next_unit)
        if abs(denominator) < 1e-12:
            intersection = (
                (previous_point[0] + next_point[0]) / 2,
                (previous_point[1] + next_point[1]) / 2,
            )
        else:
            delta = (next_point[0] - previous_point[0], next_point[1] - previous_point[1])
            scale = cross(delta, next_unit) / denominator
            intersection = (
                previous_point[0] + scale * previous_unit[0],
                previous_point[1] + scale * previous_unit[1],
            )
        result.append(intersection)

    result.append((
        centerline[-1][0] + side * distance * segments[-1][1][0],
        centerline[-1][1] + side * distance * segments[-1][1][1],
    ))
    return result


def _routed_pair_objects(newline: str) -> list[str]:
    """Create smooth, length-balanced fanouts and constant-gap coupled trunks."""
    objects: list[str] = []

    def add_path(
        name: str,
        net: str,
        layer: str,
        points: list[tuple[float, float]],
        width: float = 0.234,
    ) -> None:
        for index, (start, end) in enumerate(zip(points, points[1:])):
            objects.append(_segment_object(newline, f"{name}-{index}", net, layer, start, end, width))

    def neck_path(pad: tuple[float, float]) -> list[tuple[float, float]]:
        # The pin field is deliberately kept simple.  Length compensation is
        # placed at the transformer end, where there is much more room.
        return [pad, (40.5, pad[1])]

    pair_data = (
        # The final centreline vertices compensate the 2.03 mm RJ45 pin-column
        # stagger through ordinary fanout geometry.  This avoids a one-sided
        # U-turn while retaining end-to-end P/N length balance.
        ("A", "F.Cu", "/DA_P", "/DA_N", (35.43, 53.39), (37.46, 54.41),
         [(44.0, 53.9), (46.0, 53.9), (56.0, 29.0), (58.0, 27.7214)],
         (62.96, 26.46), (62.96, 31.54)),
        ("B", "B.Cu", "/DB_P", "/DB_N", (35.43, 55.43), (37.46, 58.49),
         [(44.0, 56.96), (46.0, 56.96), (54.0, 47.0), (58.0, 45.47996)],
         (62.96, 44.46), (62.96, 49.54)),
        ("C", "F.Cu", "/DC_P", "/DC_N", (37.46, 56.45), (35.43, 57.47),
         [(44.0, 56.96), (46.0, 56.96), (50.0, 65.0), (58.0, 66.36969)],
         (62.96, 62.46), (62.96, 67.54)),
        ("D", "F.Cu", "/DD_P", "/DD_N", (35.43, 59.51), (37.46, 60.53),
         [(44.0, 60.02), (46.0, 60.02), (55.0, 83.0), (58.0, 81.74104)],
         (62.96, 80.46), (62.96, 85.54)),
    )

    for pair, layer, p_net, n_net, p_pad, n_pad, centerline, p_dest, n_dest in pair_data:
        p_trunk = _offset_polyline(centerline, -1.0)
        n_trunk = _offset_polyline(centerline, 1.0)
        p_neck = neck_path(p_pad)
        n_neck = neck_path(n_pad)
        add_path(f"{pair}-P-neck", p_net, layer, p_neck, 0.15)
        add_path(f"{pair}-N-neck", n_net, layer, n_neck, 0.15)
        objects.append(_segment_object(newline, f"{pair}-P-fan-in", p_net, layer, p_neck[-1], p_trunk[0]))
        objects.append(_segment_object(newline, f"{pair}-N-fan-in", n_net, layer, n_neck[-1], n_trunk[0]))
        add_path(f"{pair}-P-trunk", p_net, layer, p_trunk)
        add_path(f"{pair}-N-trunk", n_net, layer, n_trunk)

        if pair == "B":
            p_transition = (60.5, p_dest[1])
            n_transition = (60.5, n_dest[1])
            objects.append(_segment_object(newline, "B-P-fan-out", p_net, layer, p_trunk[-1], p_transition))
            objects.append(_segment_object(newline, "B-N-fan-out", n_net, layer, n_trunk[-1], n_transition))
            objects.append(_via_object(newline, "B-P-via", p_net, p_transition))
            objects.append(_via_object(newline, "B-N-via", n_net, n_transition))
            add_path("B-P-top", p_net, "F.Cu", [p_transition, p_dest])
            add_path("B-N-top", n_net, "F.Cu", [n_transition, n_dest])
        else:
            p_prepad = (60.0, p_dest[1])
            n_prepad = (60.0, n_dest[1])
            objects.append(_segment_object(newline, f"{pair}-P-fan-out", p_net, layer, p_trunk[-1], p_prepad))
            objects.append(_segment_object(newline, f"{pair}-N-fan-out", n_net, layer, n_trunk[-1], n_prepad))
            add_path(f"{pair}-P-pad", p_net, layer, [p_prepad, p_dest])
            add_path(f"{pair}-N-pad", n_net, layer, [n_prepad, n_dest])

    return objects


def update_board(board_path: Path) -> dict[str, int]:
    raw = board_path.read_bytes()
    text = raw.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"

    text = _replace_once(text, "\t\t(thickness 1.5)", "\t\t(thickness 1.5862)", "board thickness")
    text = _replace_once(text, '\t\t(rev "A")', '\t\t(rev "B")', "revision")
    text = _replace_once(
        text,
        '\t\t(comment 3 "Confirm 50/100 ohm geometry with the selected PCB fabricator.")',
        '\t\t(comment 3 "JLC04161H-7628: 50R W0.357; 100R W0.234/G0.216; L2/L3 GND.")',
        "title-block impedance note",
    )
    text = _replace_once(text, '\t\t(4 "In1.Cu" signal)', '\t\t(4 "In1.Cu" power)', "In1 layer type")
    text = _replace_once(text, '\t\t(6 "In2.Cu" signal)', '\t\t(6 "In2.Cu" power)', "In2 layer type")

    text = _replace_once(text, '\t\t\t\t(thickness 0.994)', '\t\t\t\t(thickness 1.065)', "core thickness")
    for dielectric_name in ("dielectric 1", "dielectric 3"):
        prepreg_pattern = re.compile(
            rf'(\(layer "{dielectric_name}".*?\(thickness )0\.2(\))',
            re.DOTALL,
        )
        text, count = prepreg_pattern.subn(r'\g<1>0.2104\g<2>', text, count=1)
        if count != 1:
            raise RuntimeError(f"Expected a 0.2 mm thickness in {dielectric_name}")
    if text.count('\t\t\t\t(thickness 0.018)') != 2:
        raise RuntimeError("Expected two 0.018 mm inner copper layers")
    text = text.replace('\t\t\t\t(thickness 0.018)', '\t\t\t\t(thickness 0.0152)')

    # Replace dielectric material/Dk fields in stack order: PP, core, PP.
    dielectric_pattern = re.compile(
        r'(\(layer "dielectric [123]".*?\(material )"FR4"(\).*?\(epsilon_r )4\.2(\))',
        re.DOTALL,
    )
    dielectric_index = 0

    def dielectric_replacement(match: re.Match[str]) -> str:
        nonlocal dielectric_index
        dielectric_index += 1
        dk = "4.36" if dielectric_index == 2 else "4.4"
        return f'{match.group(1)}"Nan Ya NP-155F"{match.group(2)}{dk}{match.group(3)}'

    text, dielectric_count = dielectric_pattern.subn(dielectric_replacement, text)
    if dielectric_count != 3:
        raise RuntimeError(f"Expected three dielectric definitions; found {dielectric_count}")

    text = _replace_once(text, "BALUN ETH RJ45  REV A", "BALUN ETH RJ45  REV B", "silkscreen revision")
    text = _replace_once(
        text,
        "STACKUP: 1.50 mm 4L; outer dielectric 0.20 mm nominal",
        "JLC04161H-7628: ORDER 1.6 mm; STACK 1.5862 mm",
        "stackup drawing note",
    )
    text = _replace_once(
        text,
        "VERIFY 50R/100R WIDTHS WITH FAB STACKUP BEFORE ORDER",
        "NON-COPLANAR: 50R W0.357 / 100R W0.234 G0.216",
        "impedance drawing note",
    )

    spans = _root_child_spans(text)
    output: list[str] = []
    cursor = 0
    inserted_ground = False
    removed_outer_zones = 0
    eth_segments = 0
    rf_segments = 0
    route_objects = _routed_pair_objects(newline)
    inserted_objects = (newline + "\t").join(
        [*route_objects, _local_ground_objects(newline)]
    )
    removed_eth_segments = 0
    removed_eth_vias = 0
    removed_obsolete_ground_vias = 0
    seen_pair_b_return_vias: set[tuple[float, float]] = set()
    obsolete_ground_vias = {(40.5, 54.8), (35.5, 68.5), (42.0, 73.5), (47.5, 72.0)}

    for start, end in spans:
        block = text[start:end]
        output.append(text[cursor:start])
        if block.startswith("(zone") and not inserted_ground:
            output.append(inserted_objects + newline + "\t")
            inserted_ground = True

        if block.startswith("(footprint") and '(property "Reference" "J1"' in block:
            if block.count("(size 1.6 1.6)") != 8:
                raise RuntimeError("Expected eight 1.60 mm signal pads in J1")
            output.append(block.replace("(size 1.6 1.6)", "(size 1.3 1.3)"))
        elif block.startswith("(zone") and ('(layer "F.Cu")' in block or '(layer "B.Cu")' in block):
            if '(net "/GND")' not in block:
                raise RuntimeError("Refusing to remove a non-GND outer zone")
            removed_outer_zones += 1
        elif block.startswith("(zone"):
            output.append(_strip_zone_fill_cache(block))
        elif block.startswith("(segment"):
            net_match = re.search(r'\(net "([^"]+)"\)', block)
            net_name = net_match.group(1) if net_match else ""
            if net_name in ETH_NETS:
                eth_segments += 1
                removed_eth_segments += 1
            elif net_name in RF_NETS:
                block, count = re.subn(r'\(width [0-9.]+\)', '(width 0.357)', block, count=1)
                if count != 1:
                    raise RuntimeError(f"Missing width in RF segment on {net_name}")
                rf_segments += 1
                output.append(block)
            else:
                output.append(block)
        elif block.startswith("(via"):
            net_match = re.search(r'\(net "([^"]+)"\)', block)
            net_name = net_match.group(1) if net_match else ""
            if net_name in ETH_NETS:
                removed_eth_vias += 1
            elif net_name == "/GND":
                at_match = re.search(r'\(at ([0-9.]+) ([0-9.]+)\)', block)
                at = (float(at_match.group(1)), float(at_match.group(2))) if at_match else None
                if at in obsolete_ground_vias:
                    removed_obsolete_ground_vias += 1
                else:
                    block, target = _migrate_pair_b_return_via(block)
                    if target is not None:
                        seen_pair_b_return_vias.add(target)
                    output.append(block)
            else:
                output.append(block)
        else:
            output.append(block)
        cursor = end

    output.append(text[cursor:])
    if not inserted_ground:
        raise RuntimeError("No zone insertion point found")
    if removed_outer_zones != 2:
        raise RuntimeError(f"Expected two outer GND zones; removed {removed_outer_zones}")
    if seen_pair_b_return_vias != PAIR_B_RETURN_VIA_TARGETS:
        raise RuntimeError(
            "Expected all four pair-B return vias; found "
            f"{sorted(seen_pair_b_return_vias)}"
        )

    board_path.write_bytes("".join(output).encode("utf-8"))
    return {
        "removed_outer_zones": removed_outer_zones,
        "removed_ethernet_segments": removed_eth_segments,
        "removed_ethernet_vias": removed_eth_vias,
        "added_ethernet_segments": sum(item.startswith("(segment") for item in route_objects),
        "added_ethernet_vias": sum(item.startswith("(via") for item in route_objects),
        "removed_obsolete_ground_vias": removed_obsolete_ground_vias,
        "updated_pair_b_return_vias": len(seen_pair_b_return_vias),
        "rf_segments": rf_segments,
        "added_ground_segments": 11,
        "added_ground_vias": 3,
    }


def update_routing_only(board_path: Path) -> dict[str, int]:
    """Replace only Ethernet routing and compact optional RCT4's GND path.

    This is the safe migration path for a board that is already at Rev B.  It
    deliberately leaves footprints, stack-up, RF routes, zones, and project
    settings untouched.
    """
    raw = board_path.read_bytes()
    text = raw.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"

    route_objects = _routed_pair_objects(newline)
    inserted_objects = (newline + "\t").join(route_objects)
    rct4_track_uuid = _stable_uuid("RCT4-gnd-track")
    rct4_via_uuid = _stable_uuid("RCT4-gnd-via")

    output: list[str] = []
    cursor = 0
    inserted_routes = False
    removed_segments = 0
    removed_vias = 0
    updated_rct4_tracks = 0
    updated_rct4_vias = 0
    seen_pair_b_return_vias: set[tuple[float, float]] = set()

    for start, end in _root_child_spans(text):
        block = text[start:end]
        output.append(text[cursor:start])

        if block.startswith("(zone") and not inserted_routes:
            output.append(inserted_objects + newline + "\t")
            inserted_routes = True

        if block.startswith("(zone"):
            output.append(_strip_zone_fill_cache(block))
        elif block.startswith("(segment"):
            net_match = re.search(r'\(net "([^"]+)"\)', block)
            net_name = net_match.group(1) if net_match else ""
            if net_name in ETH_NETS:
                removed_segments += 1
            elif f'(uuid "{rct4_track_uuid}")' in block:
                if "(start 58 83)" not in block:
                    raise RuntimeError("Unexpected RCT4 GND-track start point")
                block, count = re.subn(
                    r'\(end (?:55 84\.5|57\.5 84\.2)\)',
                    '(end 57.5 84.2)',
                    block,
                    count=1,
                )
                if count != 1:
                    raise RuntimeError("Unexpected RCT4 GND-track endpoint")
                output.append(block)
                updated_rct4_tracks += 1
            else:
                output.append(block)
        elif block.startswith("(via"):
            net_match = re.search(r'\(net "([^"]+)"\)', block)
            net_name = net_match.group(1) if net_match else ""
            if net_name in ETH_NETS:
                removed_vias += 1
            elif net_name == "/GND":
                block, target = _migrate_pair_b_return_via(block)
                if target is not None:
                    output.append(block)
                    seen_pair_b_return_vias.add(target)
                elif f'(uuid "{rct4_via_uuid}")' in block:
                    block, count = re.subn(
                        r'\(at (?:55 84\.5|57\.5 84\.2)\)',
                        '(at 57.5 84.2)',
                        block,
                        count=1,
                    )
                    if count != 1:
                        raise RuntimeError("Unexpected RCT4 GND-via location")
                    output.append(block)
                    updated_rct4_vias += 1
                else:
                    output.append(block)
            else:
                output.append(block)
        else:
            output.append(block)
        cursor = end

    output.append(text[cursor:])
    if not inserted_routes:
        raise RuntimeError("No zone insertion point found")
    if removed_segments == 0 or removed_vias != 2:
        raise RuntimeError(
            f"Unexpected existing Ethernet routing: {removed_segments} segments, "
            f"{removed_vias} vias"
        )
    if updated_rct4_tracks != 1 or updated_rct4_vias != 1:
        raise RuntimeError(
            f"Expected one RCT4 GND track/via; found "
            f"{updated_rct4_tracks}/{updated_rct4_vias}"
        )
    if seen_pair_b_return_vias != PAIR_B_RETURN_VIA_TARGETS:
        raise RuntimeError(
            "Expected all four pair-B return vias; found "
            f"{sorted(seen_pair_b_return_vias)}"
        )

    board_path.write_bytes("".join(output).encode("utf-8"))
    return {
        "removed_ethernet_segments": removed_segments,
        "removed_ethernet_vias": removed_vias,
        "added_ethernet_segments": sum(item.startswith("(segment") for item in route_objects),
        "added_ethernet_vias": sum(item.startswith("(via") for item in route_objects),
        "updated_rct4_ground_track": updated_rct4_tracks,
        "updated_rct4_ground_via": updated_rct4_vias,
        "updated_pair_b_return_vias": len(seen_pair_b_return_vias),
    }


def update_project(project_path: Path) -> None:
    raw = project_path.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    project = json.loads(raw.decode("utf-8"))
    design = project["board"]["design_settings"]
    design["defaults"]["zones"]["min_clearance"] = 0.25
    design["diff_pair_dimensions"] = [{"gap": 0.216, "via_gap": 0.30, "width": 0.234}]
    design["track_widths"] = [0.234, 0.25, 0.357, 0.5, 0.8]
    design["via_dimensions"] = [{"diameter": 0.6, "drill": 0.3}]

    # Keep the global edge value at zero: the custom rule enforces 0.30 mm and
    # the later SMA rule can then legally override it at the edge launch.
    design["rules"]["min_copper_edge_clearance"] = 0.0
    design["rules"]["min_track_width"] = 0.15

    classes = {item["name"]: item for item in project["net_settings"]["classes"]}
    default = classes["Default"]
    default["track_width"] = 0.25
    default["via_diameter"] = 0.6
    default["via_drill"] = 0.3

    eth = classes["ETH100"]
    eth.update({
        "clearance": 0.20,
        "track_width": 0.234,
        "diff_pair_width": 0.234,
        "diff_pair_gap": 0.216,
        "diff_pair_via_gap": 0.30,
        "via_diameter": 0.6,
        "via_drill": 0.3,
    })

    rf = classes["RF50"]
    rf.update({
        "clearance": 0.25,
        "track_width": 0.357,
        "via_diameter": 0.6,
        "via_drill": 0.3,
    })

    encoded = json.dumps(project, ensure_ascii=False, indent=2) + newline
    if newline == "\r\n":
        encoded = encoded.replace("\n", "\r\n")
    project_path.write_bytes(encoded.encode("utf-8"))


def make_backup(project_dir: Path, label: str = "pre_jlc_rev_b") -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = project_dir / f"backup_{label}_{stamp}"
    destination.mkdir()
    for suffix in (".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_dru"):
        source = project_dir / f"{PROJECT_BASENAME}{suffix}"
        shutil.copy2(source, destination / source.name)
    footprint_library = project_dir / "balun_eth_rj45.pretty"
    if footprint_library.exists():
        shutil.copytree(footprint_library, destination / footprint_library.name)
    return destination


def update_local_footprint(project_dir: Path) -> None:
    footprint = project_dir / "balun_eth_rj45.pretty" / "RJ45_Amphenol_RJE59-188-5401.kicad_mod"
    if not footprint.exists():
        return
    text = footprint.read_text(encoding="utf-8")
    if text.count("(size 1.6 1.6)") != 8:
        raise RuntimeError("Expected eight 1.60 mm pads in the local RJ45 footprint")
    footprint.write_text(text.replace("(size 1.6 1.6)", "(size 1.3 1.3)"), encoding="utf-8")


def run_sma_migration(project_dir: Path) -> None:
    """Finish either Rev-B path with the exact C22467617 footprint/launch."""
    updater = project_dir / "update_sma_c22467617.py"
    if not KICAD_PYTHON.exists() or not updater.exists():
        raise RuntimeError("KiCad Python or update_sma_c22467617.py is missing")
    subprocess.run([str(KICAD_PYTHON), str(updater)], cwd=project_dir, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--no-backup", action="store_true", help="Only for disposable test copies")
    parser.add_argument(
        "--routing-only",
        action="store_true",
        help="Update an existing Rev-B board to the smooth fanout geometry",
    )
    args = parser.parse_args()
    project_dir = args.project_dir.resolve()

    lock = project_dir / f"~{PROJECT_BASENAME}.kicad_pro.lck"
    if lock.exists():
        print(f"Refusing to edit while KiCad lock exists: {lock}", file=sys.stderr)
        return 2

    board_path = project_dir / f"{PROJECT_BASENAME}.kicad_pcb"
    schematic_path = project_dir / f"{PROJECT_BASENAME}.kicad_sch"
    project_path = project_dir / f"{PROJECT_BASENAME}.kicad_pro"
    rules_path = project_dir / f"{PROJECT_BASENAME}.kicad_dru"
    for path in (board_path, schematic_path, project_path, rules_path):
        if not path.exists():
            raise FileNotFoundError(path)

    if args.routing_only:
        backup = None if args.no_backup else make_backup(project_dir, "pre_smooth_fanout")
        stats = update_routing_only(board_path)
        if backup:
            print(f"Backup: {backup}")
        for key, value in stats.items():
            print(f"{key}: {value}")
        run_sma_migration(project_dir)
        refill_and_validate_project(project_dir)
        return 0

    backup = None if args.no_backup else make_backup(project_dir)
    stats = update_board(board_path)
    update_project(project_path)
    update_local_footprint(project_dir)
    rules_path.write_text(DRU_TEXT, encoding="utf-8", newline="\n")

    if backup:
        print(f"Backup: {backup}")
    for key, value in stats.items():
        print(f"{key}: {value}")
    run_sma_migration(project_dir)
    refill_and_validate_project(project_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
