# SB-LF03-012 Solver Regression Fixtures V1

The LF03 regression corpus lives at
`tests/fixtures/lf03_solver_regression_v1.json`.

The corpus is declarative and checksum-checked. Each fixture has a stable ID,
fixture family, `production: false` label for fake graph/key data, and a
payload SHA-256 computed from canonical JSON bytes.

The committed local fixtures cover:

- legal-move provider schema and availability transport,
- deterministic branching search with solved and proven-unsolvable paths,
- duplicate canonical-key memoization,
- deterministic state/depth bound exhaustion as `INCONCLUSIVE`,
- exact zero, one, and multiple solution-count observations,
- solver evidence metrics and deterministic canonical evidence bytes,
- reproduction `MATCH` and `DIVERGED`,
- authority/source tamper fail-closed behavior,
- rectangular workload evidence through a `3x2` fixture graph.

`LF03_CANONICAL_BRIDGE_CAPABILITY_V1` is capability-gated by
`SCRUBBOTS_CANONICAL_CHECKOUT` and `SCRUBBOTS_CANONICAL_BRIDGE_RUNNER`. When
those are absent, the test skips with an explicit reason. When both are present,
the fixture verifies the real canonical bridge capability without modifying the
canonical checkout.
