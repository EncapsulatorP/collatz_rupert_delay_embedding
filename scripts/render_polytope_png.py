from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from src.collatz_polytope import orbit, vertices_from_orbit
from src.geometry import convex_hull


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a Collatz polytope hull as a PNG.")
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--N", type=int, default=500)
    ap.add_argument("--mode", type=str, default="normalized", choices=["raw", "normalized", "normalized_parity"])
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--elev", type=float, default=26.0)
    ap.add_argument("--azim", type=float, default=38.0)
    args = ap.parse_args()

    a = orbit(args.n, args.N)
    V = vertices_from_orbit(a, mode=args.mode)
    H = convex_hull(V)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(9, 7), dpi=200)
    ax = fig.add_subplot(111, projection="3d")
    fig.patch.set_facecolor("#faf7f1")
    ax.set_facecolor("#fff9f2")

    tris = [V[s] for s in H.simplices]
    hull = Poly3DCollection(
        tris,
        facecolor="#ff8a5b",
        edgecolor="#6e2a00",
        linewidths=0.25,
        alpha=0.38,
    )
    ax.add_collection3d(hull)

    ax.scatter(
        V[:, 0],
        V[:, 1],
        V[:, 2],
        s=7,
        c=np.linspace(0.0, 1.0, V.shape[0]),
        cmap="turbo",
        alpha=0.95,
        depthshade=False,
    )

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(f"Collatz Delay-Embedding Hull (n={args.n}, N={args.N}, mode={args.mode})", pad=12, fontweight="bold")
    ax.view_init(elev=args.elev, azim=args.azim)
    ax.set_xlim(V[:, 0].min(), V[:, 0].max())
    ax.set_ylim(V[:, 1].min(), V[:, 1].max())
    ax.set_zlim(V[:, 2].min(), V[:, 2].max())

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
