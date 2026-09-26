# SB-LF07-007-C001-R03 — Strict Re-Audit

## Result
CHANGES_REQUIRED / FINITE RUNNER GOOD, TRUST INPUTS AND ERROR SEALING STILL OPEN

## Closed in R03
- Finite attempt budget, seed bounds, deterministic terminal precedence and genuine EXHAUSTED behavior are implemented.
- Non-applied attempts retain AttemptProvenance.
- Applied attempts emit authentic typed provenance.
- Exact-limit/no-post-limit behavior is covered.

## Remaining blockers
1. The authentic runner accepts any public `TypedChallengeTarget`; because SB-LF07-006 safety truth is forgeable, the runner can still return TARGET_MATCH from fabricated load/risk/retention PASS. R03 tests do exactly this.
2. `select_authentic_target()` and `provenance_from_authentic_validation()` are outside the runner's MutationContractError guard. A validator may return an authentic-looking but mutation-unrelated candidate; selection/provenance failures can escape as exceptions instead of producing the required terminal ERROR report.
3. Source post-verification is not executed on every terminal path; this is also part of SB-LF07-009.

## R04 requirement
Consume only sealed SB-LF07-006 target authority, catch selection/provenance contract failures and convert them to deterministic ERROR attempt/report evidence, and integrate the corrected source lifecycle on all operation paths. Preserve all finite-budget semantics already accepted.

## Disposition
OPEN / R04 REQUIRED.