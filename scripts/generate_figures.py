from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from src.collatz_polytope import orbit, vertices_from_orbit
from src.geometry import convex_hull


def read_scan_csv(path: Path) -> Dict[str, np.ndarray]:
    rows = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        raise ValueError(f"CSV has no rows: {path}")

    def col(name: str, cast=float):
        return np.array([cast(r[name]) for r in rows])

    return {
        "n": col("n", int),
        "hull_simplices": col("hull_simplices", int),
        "hull_volume": col("hull_volume", float),
        "hull_area": col("hull_area", float),
        "rupert_proxy_hit_rate": col("rupert_proxy_hit_rate", float),
    }


def moving_average(x: np.ndarray, window: int) -> np.ndarray:
    window = max(1, int(window))
    if window == 1:
        return x.copy()
    k = np.ones(window, dtype=float) / float(window)
    pad_left = window // 2
    pad_right = window - 1 - pad_left
    xp = np.pad(x, (pad_left, pad_right), mode="edge")
    return np.convolve(xp, k, mode="valid")


def set_theme() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#f6f0e7",
            "axes.facecolor": "#fff9f2",
            "axes.edgecolor": "#4c3d2f",
            "axes.labelcolor": "#2b2219",
            "xtick.color": "#3a2d20",
            "ytick.color": "#3a2d20",
            "grid.color": "#c6b59f",
            "text.color": "#2b2219",
            "font.size": 11,
            "axes.titleweight": "bold",
        }
    )


def add_gradient_background(ax, color_top: str = "#fff8ef", color_bottom: str = "#f2e8d8") -> None:
    cmap = LinearSegmentedColormap.from_list("bg_grad", [color_top, color_bottom])
    grad = np.linspace(0.0, 1.0, 256).reshape(256, 1)
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.imshow(
        grad,
        extent=(x0, x1, y0, y1),
        origin="lower",
        aspect="auto",
        cmap=cmap,
        alpha=0.9,
        zorder=0,
    )


def save_trend_figure(data: Dict[str, np.ndarray], out_path: Path) -> None:
    n = data["n"]
    volume = data["hull_volume"]
    area = data["hull_area"]
    hit = data["rupert_proxy_hit_rate"]
    simplices = data["hull_simplices"]

    v_roll = moving_average(volume, 11)
    a_roll = moving_average(area, 11)

    fig, ax1 = plt.subplots(figsize=(13.5, 7.2), dpi=180)
    ax2 = ax1.twinx()

    ax1.set_xlim(n.min() - 1, n.max() + 1)
    ax1.set_ylim(volume.min() * 0.97, volume.max() * 1.02)
    add_gradient_background(ax1)

    sizes = 18.0 + 1.0 * simplices
    sc = ax1.scatter(
        n,
        volume,
        c=hit,
        s=sizes,
        cmap="cividis",
        alpha=0.85,
        linewidth=0.4,
        edgecolor="#2b2219",
        zorder=3,
    )
    ax1.plot(n, v_roll, color="#9f1f3f", linewidth=2.7, zorder=4, label="Rolling mean (volume)")
    ax2.plot(n, a_roll, color="#24527a", linewidth=2.2, alpha=0.85, zorder=4, label="Rolling mean (area)")

    idx_top = np.argsort(hit + (volume - volume.mean()) / volume.std())[-8:]
    for i in idx_top:
        ax1.text(
            n[i],
            volume[i] + 0.00025,
            str(int(n[i])),
            fontsize=8,
            ha="center",
            va="bottom",
            color="#1f1f1f",
            zorder=5,
        )

    ax1.grid(True, alpha=0.35, linestyle="--")
    ax1.set_xlabel("Seed n")
    ax1.set_ylabel("Convex hull volume")
    ax2.set_ylabel("Convex hull area")
    ax1.set_title("Collatz Delay-Embedding Geometry Across Seeds")
    fig.text(
        0.125,
        0.925,
        "Point color = Rupert-proxy hit rate, point size = hull simplices",
        fontsize=10,
        color="#4b3f32",
    )

    cb = fig.colorbar(sc, ax=[ax1, ax2], fraction=0.025, pad=0.02)
    cb.set_label("Rupert-proxy hit rate")

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def save_phase_map_figure(data: Dict[str, np.ndarray], out_path: Path) -> None:
    n = data["n"]
    volume = data["hull_volume"]
    area = data["hull_area"]
    hit = data["rupert_proxy_hit_rate"]
    simplices = data["hull_simplices"]

    fig = plt.figure(figsize=(14.0, 7.0), dpi=180)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.1], wspace=0.15)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    ax1.set_xlim(n.min() - 1, n.max() + 1)
    lv = np.log10(volume)
    pad = 0.02 * (lv.max() - lv.min() + 1e-9)
    ax1.set_ylim(lv.min() - pad, lv.max() + pad)
    add_gradient_background(ax1, color_top="#fff8f1", color_bottom="#f7ead6")
    hb = ax1.hexbin(n, lv, gridsize=28, cmap="YlOrBr", mincnt=1, linewidths=0.2, alpha=0.95)
    ax1.plot(n, moving_average(lv, 15), color="#512b58", linewidth=2.4, alpha=0.85)
    ax1.set_title("Seed vs log10(Volume) density")
    ax1.set_xlabel("Seed n")
    ax1.set_ylabel("log10(hull volume)")
    c1 = fig.colorbar(hb, ax=ax1, fraction=0.046, pad=0.03)
    c1.set_label("bin count")

    sizes = 14.0 + 1.8 * simplices
    sc = ax2.scatter(
        volume,
        area,
        c=hit,
        s=sizes,
        cmap="plasma",
        alpha=0.75,
        linewidth=0.4,
        edgecolor="#1c1c1c",
    )
    interesting = np.where(hit > np.percentile(hit, 90))[0]
    ax2.scatter(
        volume[interesting],
        area[interesting],
        s=(sizes[interesting] * 1.4),
        marker="*",
        c="#00a878",
        edgecolor="#0b3d2e",
        linewidth=0.9,
        zorder=6,
        label="Top 10% hit-rate",
    )

    ax2.grid(True, alpha=0.35, linestyle=":")
    ax2.set_title("Geometry phase map")
    ax2.set_xlabel("Hull volume")
    ax2.set_ylabel("Hull area")
    ax2.legend(loc="lower right", frameon=True, facecolor="#fffaf2")
    c2 = fig.colorbar(sc, ax=ax2, fraction=0.046, pad=0.03)
    c2.set_label("Rupert-proxy hit rate")

    fig.suptitle("Structure + Proxy Fit Signals", fontsize=17, fontweight="bold", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def save_spotlight_figure(data: Dict[str, np.ndarray], out_path: Path) -> np.ndarray:
    n = data["n"]
    volume = data["hull_volume"]
    area = data["hull_area"]
    hit = data["rupert_proxy_hit_rate"]
    simplices = data["hull_simplices"]

    z = lambda x: (x - x.mean()) / (x.std() + 1e-12)
    score = 1.2 * z(volume) + 0.9 * z(area) + 0.4 * z(simplices) + 4.0 * hit
    top_idx = np.argsort(score)[-15:][::-1]

    n_top = n[top_idx]
    score_top = score[top_idx]
    hit_top = hit[top_idx]

    fig, ax = plt.subplots(figsize=(12.5, 8.2), dpi=180)
    y = np.arange(len(top_idx))
    bars = ax.barh(y, score_top, color=plt.cm.viridis(0.2 + 0.7 * (hit_top / (hit_top.max() + 1e-12))))

    ax.set_yticks(y)
    ax.set_yticklabels([f"n={int(v)}" for v in n_top])
    ax.invert_yaxis()
    ax.set_xlabel("Composite interestingness score")
    ax.set_title("Spotlight Seeds: high geometry + proxy-fit signal")
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    for i, (bar, h) in enumerate(zip(bars, hit_top)):
        ax.text(
            bar.get_width() + 0.02,
            i,
            f"hit={h:.3f}",
            va="center",
            ha="left",
            fontsize=9,
            color="#1f1f1f",
        )

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return n_top[:3]


def save_hull_gallery(top_seeds: np.ndarray, N: int, mode: str, out_path: Path) -> None:
    fig = plt.figure(figsize=(15.0, 5.2), dpi=180)

    for idx, n in enumerate(top_seeds, start=1):
        ax = fig.add_subplot(1, len(top_seeds), idx, projection="3d")
        a = orbit(int(n), N)
        V = vertices_from_orbit(a, mode=mode)
        H = convex_hull(V)

        tris = [V[s] for s in H.simplices]
        poly = Poly3DCollection(
            tris,
            facecolor="#ff7f50",
            edgecolor="#5a1f00",
            linewidths=0.25,
            alpha=0.36,
        )
        ax.add_collection3d(poly)
        ax.scatter(
            V[:, 0],
            V[:, 1],
            V[:, 2],
            s=6,
            c=np.linspace(0.0, 1.0, len(V)),
            cmap="turbo",
            alpha=0.9,
            depthshade=False,
        )

        ax.set_title(f"n={int(n)}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.view_init(elev=26, azim=35 + idx * 40)
        ax.set_xlim(V[:, 0].min(), V[:, 0].max())
        ax.set_ylim(V[:, 1].min(), V[:, 1].max())
        ax.set_zlim(V[:, 2].min(), V[:, 2].max())

    fig.suptitle("3D Hull Gallery of Spotlight Seeds", fontsize=17, fontweight="bold", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, required=True, help="Input CSV from scripts/scan_batch.py")
    ap.add_argument("--outdir", type=str, default="examples/figures")
    ap.add_argument("--N", type=int, default=220, help="Orbit steps for 3D gallery")
    ap.add_argument("--mode", type=str, default="normalized", choices=["raw", "normalized", "normalized_parity"])
    args = ap.parse_args()

    set_theme()

    csv_path = Path(args.csv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    data = read_scan_csv(csv_path)

    p1 = outdir / "figure_01_trend.png"
    p2 = outdir / "figure_02_phase_map.png"
    p3 = outdir / "figure_03_spotlight.png"
    p4 = outdir / "figure_04_hull_gallery.png"

    save_trend_figure(data, p1)
    save_phase_map_figure(data, p2)
    top_seeds = save_spotlight_figure(data, p3)
    save_hull_gallery(top_seeds, N=args.N, mode=args.mode, out_path=p4)

    print(f"wrote {p1}")
    print(f"wrote {p2}")
    print(f"wrote {p3}")
    print(f"wrote {p4}")


if __name__ == "__main__":
    main()
