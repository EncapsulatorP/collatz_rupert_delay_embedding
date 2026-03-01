import argparse
import numpy as np
from src.collatz_polytope import orbit, vertices_from_orbit
from src.projection import rupert_proxy

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--N", type=int, default=300)
    ap.add_argument("--mode", type=str, default="normalized", choices=["raw","normalized","normalized_parity"])
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--angles", type=int, default=36)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    a = orbit(args.n, args.N)
    V = vertices_from_orbit(a, mode=args.mode)
    res = rupert_proxy(V, rng=rng, trials=args.trials, angles=args.angles)
    print(res)

if __name__ == "__main__":
    main()
