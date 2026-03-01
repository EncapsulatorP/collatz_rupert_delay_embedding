from __future__ import annotations

import argparse
from typing import Dict, Tuple

import numpy as np

from src.collatz_polytope import orbit, vertices_from_orbit
from src.projection import convex_hull_2d, project_points, random_rotation_matrix


def polygon_area(poly: np.ndarray) -> float:
    if poly.shape[0] < 3:
        return 0.0
    x = poly[:, 0]
    y = poly[:, 1]
    return 0.5 * float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n <= 1e-15:
        return np.zeros_like(v)
    return v / n


def projected_width(points: np.ndarray, direction: np.ndarray) -> float:
    d = normalize(direction)
    proj = points @ d
    return float(np.max(proj) - np.min(proj))


def min_width_direction(poly: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Return an approximate minimum-width direction for a convex polygon.
    Uses edge normals as candidate directions.
    """
    h = poly.shape[0]
    if h < 2:
        return np.array([1.0, 0.0], dtype=np.float64), 0.0
    if h == 2:
        edge = poly[1] - poly[0]
        normal = np.array([-edge[1], edge[0]], dtype=np.float64)
        d = normalize(normal)
        if np.linalg.norm(d) <= 1e-15:
            d = np.array([1.0, 0.0], dtype=np.float64)
        return d, projected_width(poly, d)

    best_dir = np.array([1.0, 0.0], dtype=np.float64)
    best_width = float("inf")
    for i in range(h):
        edge = poly[(i + 1) % h] - poly[i]
        normal = np.array([-edge[1], edge[0]], dtype=np.float64)
        d = normalize(normal)
        if np.linalg.norm(d) <= 1e-15:
            continue
        w = projected_width(poly, d)
        if w < best_width:
            best_width = w
            best_dir = d

    if not np.isfinite(best_width):
        best_width = projected_width(poly, best_dir)
    return best_dir, float(best_width)


def rotate_2d(points: np.ndarray, angle_rad: float) -> np.ndarray:
    c = float(np.cos(angle_rad))
    s = float(np.sin(angle_rad))
    r = np.array([[c, -s], [s, c]], dtype=np.float64)
    return points @ r.T


def containment_proxy_min_width(
    outer_hull: np.ndarray, inner_hull: np.ndarray, angles: int = 180, tol: float = 1e-12
) -> Dict[str, float]:
    """
    Necessary-condition proxy for containment with in-plane rotation:
    - Compute min-width direction of outer hull.
    - Rotate inner hull and check width(inner_rot) <= width_min(outer) in that direction.
    """
    if outer_hull.shape[0] < 3 or inner_hull.shape[0] < 3:
        return {
            "feasible": False,
            "best_angle_deg": 0.0,
            "best_ratio": float("inf"),
            "outer_min_width": 0.0,
            "inner_best_width": 0.0,
        }

    dmin, outer_min_width = min_width_direction(outer_hull)
    best_ratio = float("inf")
    best_angle = 0.0
    inner_best_width = 0.0
    feasible = False

    for j in range(max(1, int(angles))):
        angle = 2.0 * np.pi * float(j) / float(max(1, int(angles)))
        inner_rot = rotate_2d(inner_hull, angle)
        w_inner = projected_width(inner_rot, dmin)
        ratio = w_inner / max(outer_min_width, 1e-15)

        if ratio < best_ratio:
            best_ratio = ratio
            best_angle = angle
            inner_best_width = w_inner
        if w_inner <= outer_min_width + tol:
            feasible = True

    return {
        "feasible": bool(feasible),
        "best_angle_deg": float(np.degrees(best_angle)),
        "best_ratio": float(best_ratio),
        "outer_min_width": float(outer_min_width),
        "inner_best_width": float(inner_best_width),
    }


def sample_proxy_hit_rate(
    points_3d: np.ndarray, trials: int, angles: int, rng: np.random.Generator
) -> Dict[str, float]:
    hits = 0
    for _ in range(max(1, int(trials))):
        r_outer = random_rotation_matrix(rng)
        r_inner = random_rotation_matrix(rng)

        outer_2d = convex_hull_2d(project_points(points_3d, r_outer))
        inner_2d = convex_hull_2d(project_points(points_3d, r_inner))
        res = containment_proxy_min_width(outer_2d, inner_2d, angles=angles)
        hits += int(res["feasible"])

    t = max(1, int(trials))
    return {"trials": t, "hits": int(hits), "hit_rate": float(hits) / float(t)}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Convex hull + min-width containment proxy for Collatz delay-embedded points."
    )
    ap.add_argument("--n", type=int, required=True, help="Initial Collatz seed.")
    ap.add_argument("--N", type=int, default=300, help="Number of Collatz steps.")
    ap.add_argument(
        "--mode",
        type=str,
        default="normalized",
        choices=["raw", "normalized", "normalized_parity"],
        help="Embedding mode for vertices_from_orbit.",
    )
    ap.add_argument("--angles", type=int, default=180, help="In-plane rotation samples for proxy.")
    ap.add_argument("--trials", type=int, default=120, help="Random orientation pair trials.")
    ap.add_argument("--seed", type=int, default=0, help="RNG seed.")
    args = ap.parse_args()

    a = orbit(args.n, args.N)
    points_3d = vertices_from_orbit(a, mode=args.mode)
    hull_2d = convex_hull_2d(points_3d[:, :2])

    dmin, wmin = min_width_direction(hull_2d)
    area = polygon_area(hull_2d)
    proxy = sample_proxy_hit_rate(
        points_3d=points_3d, trials=args.trials, angles=args.angles, rng=np.random.default_rng(args.seed)
    )

    print(f"n={args.n} N={args.N} mode={args.mode}")
    print(f"hull_vertices_2d={int(hull_2d.shape[0])} area_2d={area:.10g}")
    print(f"outer_min_width={wmin:.10g} min_width_dir=({dmin[0]:.6f}, {dmin[1]:.6f})")
    print(proxy)


if __name__ == "__main__":
    main()
