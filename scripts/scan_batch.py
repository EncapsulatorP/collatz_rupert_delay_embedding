import argparse
import csv
import numpy as np
from src.collatz_polytope import orbit, vertices_from_orbit
from src.geometry import convex_hull, hull_stats
from src.projection import rupert_proxy

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmin", type=int, default=2)
    ap.add_argument("--nmax", type=int, default=200)
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--mode", type=str, default="normalized", choices=["raw","normalized","normalized_parity"])
    ap.add_argument("--trials", type=int, default=120)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str, default="examples/scan.csv")
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    rows = []
    for n in range(args.nmin, args.nmax + 1):
        a = orbit(n, args.N)
        V = vertices_from_orbit(a, mode=args.mode)
        H = convex_hull(V)
        st = hull_stats(V, H)
        rp = rupert_proxy(V, rng=rng, trials=args.trials, angles=24)
        rows.append({
            "n": n,
            "N": args.N,
            "mode": args.mode,
            "hull_simplices": st.n_hull_simplices,
            "hull_volume": st.volume,
            "hull_area": st.area,
            "rupert_proxy_hit_rate": rp["hit_rate"],
        })
        if n % 25 == 0:
            print("done", n)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("wrote", args.out)

if __name__ == "__main__":
    main()
