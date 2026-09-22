# SB-LF03-011 Deterministic Budgets and Inconclusive V1

`SolverBudgetPolicy` is the versioned proof-budget contract for LF03 solver
evidence and reproduction bundles. It records deterministic limits for visited
states, depth, and counted solutions. These limits are part of canonical replay
identity.

`operational_timeout_seconds` is an optional monotonic wall-clock kill switch.
It is recorded separately as operational evidence and always maps to
`INCONCLUSIVE`; it cannot prove unsolvability.

`BudgetedSolverResult` maps provider/search/count observations into five
explicit outcomes:

- `SOLVED`
- `PROVEN_UNSOLVABLE`
- `INCONCLUSIVE`
- `UNAVAILABLE`
- `ERROR`

Budget exhaustion, `UNKNOWN_BOUND`, lower-bound solution counting, provider
interruption, and timeout are all `INCONCLUSIVE`. Exhaustive provider proof or
exact zero-solution enumeration is required for `PROVEN_UNSOLVABLE`.

The contract intentionally does not define an ambiguous `UNSOLVED` terminal
truth. Any UI may display "unsolved" only as a label backed by one of the
explicit dispositions above.
