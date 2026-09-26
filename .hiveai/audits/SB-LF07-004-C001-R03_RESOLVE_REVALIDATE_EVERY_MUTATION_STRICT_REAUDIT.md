# SB-LF07-004-C001-R03 — Strict Re-Audit

## Result
CHANGES_REQUIRED / AUTHENTIC PATH IMPROVED, ELIGIBILITY BYPASS STILL PUBLIC

## Closed in R03
- Actual accepted M03/M04/M05 producer types are now cross-checked against child/source/request/state identities before authentic adapter creation.
- M04 is bound to the authentic M03 digest and Challenge Score source/policy.
- M05 requires exact LevelData bytes/identity and source/LevelData digests.
- A positive authentic chain and unrelated-authentic-object negatives now exist.

## Remaining blockers
1. **The legacy synthetic eligibility path is still a public production surface.** `evidence()`, `revalidate_mutation()`, self-asserted `M03SolverEvidenceReceipt/M04DifficultyEvidenceReceipt/M05QAEvidenceReceipt`, and `revalidate_mutation_from_typed_receipts()` remain exported from the package root and can still construct a `ValidationEnvelope(disposition=ELIGIBLE)` from caller-created evidence. Calling this “fixture-only” in comments does not enforce fixture-only behavior.
2. Therefore the task-level invariant “every applied mutation is forced through accepted M03/M04/M05 truth before eligibility” is still false at the public API boundary.
3. The R03 builder log/master log records implementation SHA `94d29ddf7a6df6d0f4ee9d005d52ebd2ddcb7c30`, but the actual published commit is `94d29dd0f94765cc374166398836b80830dcb965`. The exact audit trail must be corrected.
4. M05 stage-authority validation proves a shared non-UNAVAILABLE repository authority but does not currently require an exact accepted authority identity beyond that shared repository/commit-present condition. Stale/mismatched accepted QA authority must be explicitly rejected rather than relabelled with the mutation authority.

## R04 requirement
Remove legacy synthetic eligibility helpers from production/root exports or hard-gate them as explicit test-only fixtures that cannot yield production-eligible objects. The only production eligibility entry point must consume authentic adapters. Tighten M05 accepted authority identity verification and add stale-authority negatives. Correct the published SHA evidence.

## Disposition
OPEN / R04 REQUIRED.