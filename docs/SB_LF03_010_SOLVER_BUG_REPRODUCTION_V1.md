# SB-LF03-010 Solver Bug Reproduction V1

`ReproductionManifest` is a closed, deterministic identity contract for
replaying solver observations that were produced by the already accepted LF03
provider, bridge, search, memoization, ordering, and evidence layers.

The manifest binds:

- candidate source SHA-256 and LevelData source SHA-256,
- seed, normalized JSON-compatible configuration, and generator version,
- the locked canonical `Sekiph82/Scrubbots` authority and ProofState source
  contract,
- legal-move provider, canonical bridge, search, memo provider, ordering, and
  pruning versions,
- deterministic solution-analysis budgets,
- operation, goal, expected disposition, observed evidence digest, and observed
  path.

`ReproductionBundle` stores the manifest and its canonical digest. A bundle is
accepted only when the digest exactly matches the manifest bytes. Any authority
or source-contract drift fails closed during construction.

`ReproductionReplay` compares a supplied observation from existing solver
layers with the immutable bundle. It returns `MATCH`, `DIVERGED`,
`UNAVAILABLE`, or `ERROR`. It does not regenerate source artifacts, discover
new legal moves, apply placements, compute canonical keys, invoke WFC, or
reimplement gameplay semantics.

Normalized configuration intentionally rejects secrets and absolute machine
paths, so reproduction artifacts remain durable and shareable without binding
to private local state.
