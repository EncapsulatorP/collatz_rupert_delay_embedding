import argparse
from src.collatz_polytope import orbit, vertices_from_orbit
from src.geometry import convex_hull, hull_stats, export_obj

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--N", type=int, default=300)
    ap.add_argument("--mode", type=str, default="normalized", choices=["raw","normalized","normalized_parity"])
    ap.add_argument("--out", type=str, default="examples/poly.obj")
    args = ap.parse_args()

    a = orbit(args.n, args.N)
    V = vertices_from_orbit(a, mode=args.mode)
    H = convex_hull(V)
    st = hull_stats(V, H)
    export_obj(V, H, args.out)
    print("wrote:", args.out)
    print("stats:", st)

if __name__ == "__main__":
    main()
