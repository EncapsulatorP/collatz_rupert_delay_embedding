from __future__ import annotations
from typing import List, Literal
import numpy as np

Mode = Literal["raw", "normalized", "normalized_parity"]

def collatz_step(n: int) -> int:
    if n <= 0:
        raise ValueError("Collatz is defined here for positive integers.")
    return n // 2 if (n % 2 == 0) else 3 * n + 1

def orbit(n0: int, N: int) -> List[int]:
    """Return a_0..a_N (length N+1)."""
    if N < 0:
        raise ValueError("N must be >= 0")
    a = [int(n0)]
    n = int(n0)
    for _ in range(N):
        n = collatz_step(n)
        a.append(n)
    return a

def vertices_from_orbit(a: List[int], mode: Mode = "normalized") -> np.ndarray:
    """
    Build vertices v_k for k=0..len(a)-2.

    raw:
        v_k = (a_k, a_{k+1}, 1 - 1/(k+1))

    normalized (recommended):
        s_k = a_k + a_{k+1} + 1
        v_k = (a_k/s_k, a_{k+1}/s_k, k/N)

    normalized_parity:
        z_k = k/N + (a_k mod 2)/(2N)
    """
    if len(a) < 2:
        raise ValueError("Need at least 2 orbit values.")
    N = len(a) - 1
    M = N
    v = np.zeros((M, 3), dtype=np.float64)

    for k in range(M):
        ak, ak1 = a[k], a[k+1]
        if mode == "raw":
            v[k, 0] = float(ak)
            v[k, 1] = float(ak1)
            v[k, 2] = 1.0 - 1.0 / float(k + 1)
        else:
            s = float(ak + ak1 + 1)
            v[k, 0] = float(ak) / s
            v[k, 1] = float(ak1) / s
            z = float(k) / float(N)
            if mode == "normalized_parity":
                z += (ak % 2) / (2.0 * float(N))
            v[k, 2] = z

    return v
