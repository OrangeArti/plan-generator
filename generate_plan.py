"""
Deterministic backtracking planner for the exhibition hall.
Key rules encoded:
- Hall 80x40, main corridors at x=48-52, y=33-37, y=3-7 (4 m width).
- Secondary vertical spurs in A/B to increase frontage.
- One tertiary horizontal corridor across A/B to increase frontage.
- Outer strips C/D/E/F (depth 3 m) accept only <=36 m² booths; we place all small booths there.
- Inner zones A/B host the remaining inventory; every booth must touch a corridor on a full side.
- Grid alignment 0.25 m, aspect ratio <= 4:1.
Inventory (total 48 booths, 2,232 m²):
 2×200, 3×100, 2×90, 3×80, 4×60, 5×48, 4×40, 5×30, 5×20, 5×18, 4×15, 6×12.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import math

GRID = 0.25
STEP = 1.0  # search step along edges
HALL_W, HALL_H = 80.0, 40.0

def snap(v: float) -> float:
    return round(v / GRID) * GRID

def rects_overlap(r1, r2) -> bool:
    return not (
        r1.x + r1.w <= r2.x or
        r2.x + r2.w <= r1.x or
        r1.y + r1.h <= r2.y or
        r2.y + r2.h <= r1.y
    )

@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float
    label: str = ""
    zone: str = ""

    def copy(self, **kwargs):
        return Rect(
            x=kwargs.get("x", self.x),
            y=kwargs.get("y", self.y),
            w=kwargs.get("w", self.w),
            h=kwargs.get("h", self.h),
            label=kwargs.get("label", self.label),
            zone=kwargs.get("zone", self.zone),
        )

def touches_corridor(r: Rect, corridors: List[Rect]) -> bool:
    for c in corridors:
        # Check left/right contact
        if math.isclose(r.x + r.w, c.x, abs_tol=1e-6) or math.isclose(c.x + c.w, r.x, abs_tol=1e-6):
            if not (r.y >= c.y + c.h or r.y + r.h <= c.y):
                return True
        # Check top/bottom contact
        if math.isclose(r.y + r.h, c.y, abs_tol=1e-6) or math.isclose(c.y + c.h, r.y, abs_tol=1e-6):
            if not (r.x >= c.x + c.w or r.x + r.w <= c.x):
                return True
    return False

def inside_zone(r: Rect, zone_bounds: Dict[str, float]) -> bool:
    return (
        r.x >= zone_bounds["x0"] - 1e-6 and
        r.x + r.w <= zone_bounds["x1"] + 1e-6 and
        r.y >= zone_bounds["y0"] - 1e-6 and
        r.y + r.h <= zone_bounds["y1"] + 1e-6
    )

# Zones
ZONE_A = {"x0": 0.0, "x1": 48.0, "y0": 7.0, "y1": 33.0}
ZONE_B = {"x0": 52.0, "x1": 80.0, "y0": 7.0, "y1": 33.0}

# Corridors
MAIN_CORRIDORS = [
    Rect(48.0, 0.0, 4.0, 40.0, label="main_vertical"),
    Rect(0.0, 33.0, 80.0, 4.0, label="main_upper"),
    Rect(0.0, 3.0, 80.0, 4.0, label="main_lower"),
]

SECONDARY_CORRIDORS = [
    Rect(22.5, 7.0, 3.0, 26.0, label="spur_A"),
    Rect(62.5, 7.0, 3.0, 26.0, label="spur_B"),
]

TERTIARY_CORRIDORS = [
    Rect(0.0, 19.0, 80.0, 3.0, label="tertiary_mid"),  # allowed inside A/B; corridors occupy space, so booths won't overlap
]

CORRIDORS = MAIN_CORRIDORS + SECONDARY_CORRIDORS + TERTIARY_CORRIDORS

# Inventory
INVENTORY = {
    200: 2, 100: 3, 90: 2, 80: 3, 60: 4, 48: 5, 40: 4,
    30: 5, 20: 5, 18: 5, 15: 4, 12: 6
}

# Shape options (w,h) within 4:1 aspect; allow rotation
SHAPES = {
    200: [(20.0, 10.0), (10.0, 20.0)],
    100: [(10.0, 10.0)],
    90:  [(9.0, 10.0), (10.0, 9.0)],
    80:  [(8.0, 10.0), (10.0, 8.0)],
    60:  [(10.0, 6.0), (6.0, 10.0)],
    48:  [(8.0, 6.0), (6.0, 8.0)],
    40:  [(8.0, 5.0), (5.0, 8.0)],
    30:  [(10.0, 3.0), (6.0, 5.0), (5.0, 6.0)],  # 10x3 for strips, 6x5 for inner
    20:  [(5.0, 4.0), (4.0, 5.0)],
    18:  [(6.0, 3.0), (4.5, 4.0), (4.0, 4.5)],
    15:  [(5.0, 3.0), (3.75, 4.0), (4.0, 3.75)],
    12:  [(4.0, 3.0), (3.0, 4.0)],
}

# Visual palette
CATEGORY_COLORS = {
    "xl": "#f7c266",  # 200s and 100s
    "lg": "#8bd3e6",  # 90/80/60
    "md": "#b2d39f",  # 48/40/30
    "sm": "#f2a4b7",  # 20/18/15/12
}
CORRIDOR_MAIN_FILL = "#d5e5ff"
CORRIDOR_SECONDARY_FILL = "#e8f2ff"
HALL_BORDER_COLOR = "#1f2933"
ZONE_OUTLINE_COLOR = "#9ca3af"
BOOTH_STROKE_COLOR = "#2e2e2e"
BOOTH_STROKE_WIDTH = 0.12
HALL_STROKE_WIDTH = 0.18
ZONE_STROKE_WIDTH = 0.12

def layout_outer_strips(blocking: List[Rect]) -> Tuple[List[Rect], Dict[int, int]]:
    """Place small booths in C/D/E/F (depth 3 m)."""
    placed = []
    used = {30: 0, 18: 0, 15: 0, 12: 0}
    bid = 1

    def add(area, x, y, w, h, zone):
        nonlocal bid
        r = Rect(snap(x), snap(y), snap(w), snap(h), label=f"{zone}_{bid}", zone=zone)
        for b in blocking + placed:
            if rects_overlap(r, b):
                raise RuntimeError(f"Overlap placing {r}")
        if not touches_corridor(r, MAIN_CORRIDORS):
            # outer strips must touch main upper/lower
            raise RuntimeError(f"No corridor contact for outer {r}")
        placed.append(r)
        used[area] = used.get(area, 0) + 1
        bid += 1

    # Zone C: y=37..40, x=0..48 => 3×30 + 3×18 (fills 48 m)
    x = 0.0; y = 37.0
    for _ in range(3):
        add(30, x, y, 10.0, 3.0, "C"); x += 10.0
    for _ in range(3):
        add(18, x, y, 6.0, 3.0, "C"); x += 6.0

    # Zone D: y=37..40, x=52..80 => 1×30 + 2×15 + 2×12
    x = 52.0; y = 37.0
    add(30, x, y, 10.0, 3.0, "D"); x += 10.0
    for _ in range(2):
        add(15, x, y, 5.0, 3.0, "D"); x += 5.0
    for _ in range(2):
        add(12, x, y, 4.0, 3.0, "D"); x += 4.0

    # Zone E: y=0..3, x=0..48 => 1×30 + 2×18 + 2×15 + 3×12
    x = 0.0; y = 0.0
    add(30, x, y, 10.0, 3.0, "E"); x += 10.0
    for _ in range(2):
        add(18, x, y, 6.0, 3.0, "E"); x += 6.0
    for _ in range(2):
        add(15, x, y, 5.0, 3.0, "E"); x += 5.0
    for _ in range(3):
        add(12, x, y, 4.0, 3.0, "E"); x += 4.0

    # Zone F: y=0..3, x=52..80 => 1×12, rest buffer
    add(12, 52.0, 0.0, 4.0, 3.0, "F")

    return placed, used

def corridor_edges_for_zone(zone: str) -> List[Dict]:
    zb = ZONE_A if zone == "A" else ZONE_B
    edges = []
    for c in CORRIDORS:
        x0, x1 = c.x, c.x + c.w
        y0, y1 = c.y, c.y + c.h
        # vertical edges
        # Main vertical: only one side per zone
        if c.label == "main_vertical":
            if zone == "A":
                edges.append({"type": "v", "side": "right", "x": x0, "y0": zb["y0"], "y1": zb["y1"]})
            else:
                edges.append({"type": "v", "side": "left", "x": x1, "y0": zb["y0"], "y1": zb["y1"]})
            continue
        # Secondary spurs: only in their zones
        if c.label == "spur_A" and zone == "A":
            edges.append({"type": "v", "side": "right", "x": x0, "y0": max(y0, zb["y0"]), "y1": min(y1, zb["y1"])})
            edges.append({"type": "v", "side": "left", "x": x1, "y0": max(y0, zb["y0"]), "y1": min(y1, zb["y1"])})
            continue
        if c.label == "spur_B" and zone == "B":
            edges.append({"type": "v", "side": "right", "x": x0, "y0": max(y0, zb["y0"]), "y1": min(y1, zb["y1"])})
            edges.append({"type": "v", "side": "left", "x": x1, "y0": max(y0, zb["y0"]), "y1": min(y1, zb["y1"])})
            continue
        # horizontal edges
        if c.label == "main_upper":
            edges.append({"type": "h", "side": "top", "y": y0, "x0": max(x0, zb["x0"]), "x1": min(x1, zb["x1"])})
            continue
        if c.label == "main_lower":
            edges.append({"type": "h", "side": "bottom", "y": y1, "x0": max(x0, zb["x0"]), "x1": min(x1, zb["x1"])})
            continue
        # tertiary corridor: allow both sides within zone
        if c.label == "tertiary_mid":
            edges.append({"type": "h", "side": "top", "y": y0, "x0": max(x0, zb["x0"]), "x1": min(x1, zb["x1"])})
            edges.append({"type": "h", "side": "bottom", "y": y1, "x0": max(x0, zb["x0"]), "x1": min(x1, zb["x1"])})
    return edges

def generate_candidates(area: int, zone: str) -> List[Rect]:
    """Generate candidate placements for a booth area in a zone, snapped to grid."""
    shapes = SHAPES[area]
    zb = ZONE_A if zone == "A" else ZONE_B
    edges = corridor_edges_for_zone(zone)
    candidates: List[Rect] = []

    for (w0, h0) in shapes:
        w, h = snap(w0), snap(h0)
        # enforce aspect <=4
        if max(w, h) / min(w, h) > 4.0001:
            continue
        for e in edges:
            if e["type"] == "v":
                x = e["x"] - w if e["side"] == "right" else e["x"]
                y_start = e["y0"]
                y_end = e["y1"] - h
                y = y_start
                while y <= y_end + 1e-6:
                    r = Rect(snap(x), snap(y), w, h, zone=zone)
                    if inside_zone(r, zb):
                        candidates.append(r)
                    y += STEP
            else:  # horizontal
                y = e["y"] - h if e["side"] == "top" else e["y"]
                x_start = e["x0"]
                x_end = e["x1"] - w
                x = x_start
                while x <= x_end + 1e-6:
                    r = Rect(snap(x), snap(y), w, h, zone=zone)
                    if inside_zone(r, zb):
                        candidates.append(r)
                    x += STEP
    # Deduplicate candidates and cap to keep search tractable
    uniq = {}
    for r in candidates:
        key = (r.x, r.y, r.w, r.h)
        uniq[key] = r
    # sort by distance to main entrance (50,40) for heuristic
    def dist(r: Rect):
        cx = r.x + r.w / 2
        cy = r.y + r.h / 2
        return (cx - 50.0) ** 2 + (cy - 40.0) ** 2
    cand_list = sorted(uniq.values(), key=dist)
    return cand_list[:400]  # cap a bit higher

def greedy_place_with_skips(place_order: List[int], candidates_cache: Dict[Tuple[int, str], List[Rect]],
                            blocking: List[Rect]) -> Tuple[List[Rect], List[int]]:
    placed: List[Rect] = []
    skipped: List[int] = []
    for area in place_order:
        placed_flag = False
        for zone in ["A", "B"]:
            for cand in candidates_cache[(area, zone)]:
                if any(rects_overlap(cand, b) for b in placed + blocking):
                    continue
                if not touches_corridor(cand, CORRIDORS):
                    continue
                placed.append(cand.copy(label=f"{zone}_{len([p for p in placed if p.zone==zone])+1}", zone=zone))
                placed_flag = True
                break
            if placed_flag:
                break
        if not placed_flag:
            skipped.append(area)
    return placed, skipped

def booth_category(area: int) -> str:
    """Map booth area to one of four visual categories."""
    if area >= 150:
        return "xl"
    if area >= 80:
        return "lg"
    if area >= 40:
        return "md"
    return "sm"

def main():
    # Build blocking rects = corridors
    blocking = CORRIDORS.copy()
    # Place outer strips
    outer_booths, used_outer = layout_outer_strips(blocking)
    blocking += outer_booths  # treat outer booths as blocking for inner placements

    # Remaining inventory for inner zones
    remaining = INVENTORY.copy()
    for a, c in used_outer.items():
        remaining[a] -= c

    # Build placement order (descending area, priority)
    place_order: List[int] = []
    for a, c in sorted(remaining.items(), key=lambda kv: kv[0], reverse=True):
        place_order += [a] * c

    # Precompute candidates for each area/zone
    candidates_cache: Dict[Tuple[int, str], List[Rect]] = {}
    for a in set(place_order):
        for z in ["A", "B"]:
            candidates_cache[(a, z)] = generate_candidates(a, z)
            if not candidates_cache[(a, z)]:
                raise RuntimeError(f"No candidates for area {a} in zone {z}")

    placed_inner, skipped = greedy_place_with_skips(place_order, candidates_cache, blocking)

    all_booths = outer_booths + placed_inner
    # Validation: counts and area
    counts = {}
    total_area = 0
    for b in all_booths:
        counts[b.w * b.h] = counts.get(b.w * b.h, 0) + 1  # not ideal; area by dimensions
        total_area += b.w * b.h

    # SVG
    svg_parts = []
    svg_parts.append(
        "<style>"
        f".hall-border{{stroke:{HALL_BORDER_COLOR};stroke-width:{HALL_STROKE_WIDTH};fill:none;}}"
        f".zone-outline{{stroke:{ZONE_OUTLINE_COLOR};stroke-width:{ZONE_STROKE_WIDTH};stroke-dasharray:0.6 0.6;fill:none;}}"
        f".booth{{stroke:{BOOTH_STROKE_COLOR};stroke-width:{BOOTH_STROKE_WIDTH};}}"
        ".booth-text{font-size:1.2px;font-family:Arial,sans-serif;fill:#1f2933;}"
        ".corridor-main{stroke:none;}"
        ".corridor-secondary{stroke:none;}"
        "</style>"
    )

    def svg_rect(r: Rect, cls: str, fill: str, stroke: str = "none", stroke_width: float = 0.0, text: str = None):
        svg_y = HALL_H - r.y - r.h
        txt = ""
        if text:
            tx = r.x + r.w / 2
            ty = svg_y + r.h / 2
            txt = (
                f'<text x="{tx}" y="{ty}" class="booth-text" text-anchor="middle" '
                f'dominant-baseline="middle">{text}</text>'
            )
        return (
            f'<rect x="{r.x}" y="{svg_y}" width="{r.w}" height="{r.h}" class="{cls}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}" fill="{fill}" />{txt}'
        )

    # Hall boundary
    svg_parts.append(
        svg_rect(
            Rect(0.0, 0.0, HALL_W, HALL_H),
            cls="hall-border",
            fill="none",
            stroke=HALL_BORDER_COLOR,
            stroke_width=HALL_STROKE_WIDTH,
        )
    )

    # Corridors with differentiated colors
    for c in CORRIDORS:
        is_main = c.label in {"main_vertical", "main_upper", "main_lower"}
        fill = CORRIDOR_MAIN_FILL if is_main else CORRIDOR_SECONDARY_FILL
        cls = "corridor-main" if is_main else "corridor-secondary"
        svg_parts.append(svg_rect(c, cls=cls, fill=fill))

    # Booths by category color
    for b in all_booths:
        area = int(round(b.w * b.h))
        label = f"{area} m2"
        category = booth_category(area)
        fill = CATEGORY_COLORS[category]
        svg_parts.append(
            svg_rect(
                b,
                cls="booth",
                fill=fill,
                stroke=BOOTH_STROKE_COLOR,
                stroke_width=BOOTH_STROKE_WIDTH,
                text=label,
            )
        )

    # Zone outlines for readability (do not affect geometry)
    zone_outlines = [
        Rect(0.0, 7.0, 48.0, 26.0, label="A"),
        Rect(52.0, 7.0, 28.0, 26.0, label="B"),
        Rect(0.0, 37.0, 48.0, 3.0, label="C"),
        Rect(52.0, 37.0, 28.0, 3.0, label="D"),
        Rect(0.0, 0.0, 48.0, 3.0, label="E"),
        Rect(52.0, 0.0, 28.0, 3.0, label="F"),
    ]
    for z in zone_outlines:
        svg_parts.append(
            svg_rect(
                z,
                cls="zone-outline",
                fill="none",
                stroke=ZONE_OUTLINE_COLOR,
                stroke_width=ZONE_STROKE_WIDTH,
            )
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{HALL_W*10}" height="{HALL_H*10}" '
        f'viewBox="0 0 {HALL_W} {HALL_H}">\n' + "\n".join(svg_parts) + "\n</svg>"
    )
    with open("new_plan.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Generated new_plan.svg with", len(all_booths), "booths")
    placed_counts = {}
    for b in all_booths:
        placed_counts[b.label] = placed_counts.get(b.label, 0) + 1
    print("Skipped (unplaced) booth areas:", skipped)
    print("Total booth area placed:", total_area)

if __name__ == "__main__":
    main()
