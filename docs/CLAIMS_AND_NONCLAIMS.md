# Claims / Non-claims (read this first)

## A clean, correct statement
If we build an **infinite-horizon** hull

    $P_n = Conv({v_k}_{k>=0})$

with $v_k = (a_k, a_{k+1}, 1 - 1/(k+1))$,

and the Collatz orbit has unbounded limsup (its values are unbounded),
then {$v_k$} is unbounded in $R^3 (x/y grow)$, hence $P_n$ is an unbounded convex set.

Rupert’s property is defined for compact (bounded) bodies/polyhedra.
So $Rupert(P_n)$ is not in-domain (or is false by convention).

## Everything else is hypothesis unless proved
- “Convergence ⇒ $Rupert(P(n,N))$” is NOT proved here.
- “Cycle ⇒ non-Rupert” is NOT proved here.
- “Noperthedron implies high-complexity hulls are non-Rupert” is NOT a theorem.

This repo exists to explore correlations and prototype constructions that could support future lemmas.
