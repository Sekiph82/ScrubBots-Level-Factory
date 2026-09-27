# SB-LF07-008-C001-R04 — Strict Re-Audit

## Result
CHANGES_REQUIRED / TRUTHFUL UNAVAILABLE, BUT NO ACTUAL MATCHED WORKLOAD PATH

## Closed in R04
- Seed-only workload is no longer claimed as full configuration.
- Same-seed/different GenerationRequest configurations produce different regeneration config digests.
- Raw GenerationResult SUCCESS is not counted as accepted; it is inconclusive without accepted M03/M04/M05 validation.
- Provider accounting remains unavailable/None.
- Solver workload availability is explicit rather than silently authoritative zero.

## Remaining blockers
1. Mutation workload and regeneration workload are derived from different canonical structures:
   - mutation: hash of `parent.payload["generation_request"]` requiring additional target/validation/budget keys;
   - regeneration: `GenerationRequest.digest()`.
   These cannot represent the same canonical workload identity. The authentic comparison therefore has no demonstrated path to `MATCHED`; R04 tests only prove `UNAVAILABLE`.
2. No shared workload-identity constructor is consumed by both mutation and regeneration routes.
3. There is no optional authenticated regeneration-validation adapter path. A raw generated result is correctly inconclusive, but 008 still cannot compare accepted/eligible regeneration evidence when such validation is available.

## R05 requirement
Introduce one shared canonical matched-workload identity, preferably bound to the exact GenerationRequest digest plus target/validation/budget identity, and have both routes consume that same identity. Demonstrate at least one actual MATCHED deterministic fixture. If accepted regeneration M03/M04/M05 evidence can be supplied, bind and count it; otherwise keep regeneration acceptance explicitly unavailable/inconclusive without fabricating it.

## Disposition
OPEN / R05 REQUIRED.