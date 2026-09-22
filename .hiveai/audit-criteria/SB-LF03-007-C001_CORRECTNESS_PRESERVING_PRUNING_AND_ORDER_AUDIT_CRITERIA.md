# SB-LF03-007-C001 - Correctness-Preserving Pruning and Order - Strict Audit Criteria

Target:
`SB-LF03-007 - Add correctness-preserving pruning/order only with tests.`

## Rule

No pruning or ordering optimization may change gameplay truth.

All policies must be:
- versioned;
- deterministic;
- opt-in or explicitly selected;
- compared against the accepted baseline search.

## Ordering

Stable move ordering may improve determinism/performance.

For exhaustive unbounded-by-policy fixtures, reordered traversal must preserve final verdict and solution existence.

Under bounded search, ordering can affect which solution is found before the bound. Therefore:
- ordering version must be recorded in evidence;
- bounded outcomes must remain truthful;
- no bounded miss may be called proven unsolvable.

## Pruning

Only proof-safe pruning is allowed.

Examples:
- already-visited canonical semantic states from SB-LF03-005;
- dominated/duplicate branches only when equivalence is formally justified and tested.

If no additional safe pruning can be proven, an explicit `NONE_V1` pruning policy is acceptable.

Do not invent heuristic pruning from colors, board size, artwork shape or difficulty.

## Required tests

Compare baseline vs optimized policy on fixtures:
- solved;
- unsolved/exhausted;
- branching alternate solution;
- repeated-equivalent states;
- bounded search.

Prove no false SOLVED/UNSOLVABLE classification.

## PASS

PASS when every optimization is versioned, deterministic, proof-safe, regression-tested against baseline, and truthful under bounds.
