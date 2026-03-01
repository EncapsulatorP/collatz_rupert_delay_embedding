from __future__ import annotations
import numpy as np
from typing import Tuple

def random_rotation_matrix(rng: np.random.Generator) -> np.ndarray:
    """Uniform random rotation via quaternion."""
    u1, u2, u3 = rng.random(3)
    q1 = np.sqrt(1-u1) * np.sin(2*np.pi*u2)
    q2 = np.sqrt(1-u1) * np.cos(2*np.pi*u2)
    q3 = np.sqrt(u1) * np.sin(2*np.pi*u3)
    q4 = np.sqrt(u1) * np.cos(2*np.pi*u3)
    x, y, z, w = q1, q2, q3, q4
    return np.array([
        [1-2*(y*y+z*z), 2*(x*y - z*w), 2*(x*z + y*w)],
        [2*(x*y + z*w), 1-2*(x*x+z*z), 2*(y*z - x*w)],
        [2*(x*z - y*w), 2*(y*z + x*w), 1-2*(x*x+y*y)]
    ], dtype=np.float64)

def project_points(P: np.ndarray, R: np.ndarray, plane: Tuple[int,int] = (0,1)) -> np.ndarray:
    """Rotate 3D points and project to 2D by selecting coordinates."""
    Q = (P @ R.T)
    return Q[:, [plane[0], plane[1]]]

def convex_hull_2d(points: np.ndarray) -> np.ndarray:
    """2D convex hull in CCW order using monotone chain."""
    pts = np.unique(points, axis=0)
    if pts.shape[0] <= 2:
        return pts
    pts = pts[np.lexsort((pts[:,1], pts[:,0]))]

    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in pts[::-1]:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.vstack((lower[:-1], upper[:-1]))

def point_in_convex_polygon(poly: np.ndarray, p: np.ndarray) -> bool:
    """O(H) inside test for CCW convex polygon."""
    H = poly.shape[0]
    for i in range(H):
        a = poly[i]
        b = poly[(i+1) % H]
        if (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0]) < -1e-12:
            return False
    return True

def polygon_contains_all(poly: np.ndarray, pts: np.ndarray) -> bool:
    return all(point_in_convex_polygon(poly, p) for p in pts)

def try_fit_by_translation(outer: np.ndarray, inner: np.ndarray, rng: np.random.Generator, trials: int = 2000) -> bool:
    """
    Heuristic translation-only fit test:
    sample translations within outer bbox and check if all inner vertices land inside outer.
    """
    if outer.shape[0] < 3 or inner.shape[0] < 3:
        return False
    omin = outer.min(axis=0); omax = outer.max(axis=0)
    oc = outer.mean(axis=0)
    for _ in range(trials):
        lam = rng.random()
        t = lam*oc + (1-lam)*(omin + (omax-omin)*rng.random(2))
        shifted = inner + t
        if polygon_contains_all(outer, shifted):
            return True
    return False

def rupert_proxy(P: np.ndarray, rng: np.random.Generator, trials: int = 200, angles: int = 36) -> dict:
    """
    Proxy test:
      - sample random orientations A and B
      - project both to 2D, compute convex hull polygons
      - try to fit hull(B) inside hull(A) by scanning in-plane rotations + random translations
    """
    hits = 0
    for _ in range(trials):
        RA = random_rotation_matrix(rng)
        RB = random_rotation_matrix(rng)
        A = convex_hull_2d(project_points(P, RA))
        B0 = convex_hull_2d(project_points(P, RB))
        ok = False
        for j in range(angles):
            ang = 2*np.pi*j/angles
            R2 = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]], dtype=np.float64)
            B = B0 @ R2.T
            if try_fit_by_translation(A, B, rng, trials=500):
                ok = True
                break
        if ok:
            hits += 1
    return {"trials": int(trials), "hits": int(hits), "hit_rate": float(hits)/float(trials)}
