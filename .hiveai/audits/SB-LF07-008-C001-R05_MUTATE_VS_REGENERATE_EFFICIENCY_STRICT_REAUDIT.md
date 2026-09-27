# SB-LF07-008-C001-R05 — Strict Re-Audit

## Result
CHANGES_REQUIRED / SHARED WORKLOAD EXISTS, MUTATION WORKLOAD IS NOT CROSS-BOUND TO ACTUAL EXECUTION SEED

## Closed in R05
- One shared `canonical_workload_identity()` now drives mutation and regeneration workload construction.
- The identity binds GenerationRequest digest, sealed target digest/policy and attempt budget.
- A deterministic MATCHED fixture now exists.
- Same-seed changes to width/height/mode/style/theme/palette/options are detected as unmatched.
- Raw regeneration SUCCESS remains produced/inconclusive without accepted M03/M04/M05 validation.
- Solver workload/accounting availability remains truthful.

## Remaining blocker
`run_authentic_bounded_mutations(..., base_seed=..., generation_request=...)` accepts any immutable GenerationRequest and records its digest as the mutation workload without proving it belongs to the actual mutation execution.

There is no check that:
- `generation_request.seed == base_seed`;
- the effective mutation request seed lineage derives from that same canonical generation seed/config; or
- the supplied GenerationRequest is otherwise bound to the parent candidate's accepted generation provenance.

Therefore a mutation can execute under base seed A while the caller supplies a GenerationRequest with seed B. Regeneration can then use the same B request and the two route objects compare as MATCHED, despite different actual mutation/regeneration seed workloads.

This violates the original task criterion requiring the **same canonical seed/config identity** and the acceptance criterion requiring an apples-to-apples, provenance-bound comparison.

## R06 requirement
At minimum, fail closed unless the supplied GenerationRequest seed/config identity is provably the mutation workload identity. Bind the workload context to the actual mutation run before any comparison:
- exact generation seed must agree with the mutation base-seed contract;
- if the parent carries generation provenance/config identity, it must equal the supplied GenerationRequest digest;
- if exact config provenance is unavailable, mutation route remains UNAVAILABLE rather than MATCHED.

Add an adversarial test where mutation executes with seed A but workload/regeneration use seed B and prove MATCHED is impossible.

## Disposition
OPEN / R06 REQUIRED.