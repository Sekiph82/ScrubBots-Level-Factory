# SB-LF07-009-C001-R02 — Strict Re-Audit

## Result
CHANGES_REQUIRED / M05 TYPE REUSED, ORCHESTRATION ORDER STILL WRONG

## Material improvement
`mutation_source.py` now imports the accepted M05 `OwnerSourceRecord`, `SourcePreservationReport`, and verifier directly.

## Remaining blockers
1. The legacy duplicate M07 `OwnerSourceRecord` and verifier still remain exported through `m07_services` / package compatibility surfaces, so the duplicate authority has not actually been removed.
2. `run_authentic_bounded_mutations()` requires `source_context.passed` **before** mutation begins. But `passed` requires both a before report and an after report. The caller therefore has to perform “after” verification before the mutation loop, which is not a real post-operation guard.
3. The runner never invokes `verify_after()` after mutation/validation/targeting. Source bytes could theoretically change during the operation after the pre-built PASS context and no post-operation check would catch it.
4. R02 tests only establish/verify the context itself; they do not execute an integrated source-linked hardening/easing/targeting run proving pre/post protection.

## R03 requirement
Make the orchestration own the lifecycle: establish M05 pre-check, run mutation/validation/targeting, then perform post-check before returning TARGET_MATCH/eligible success. Remove legacy duplicate M07 source authority from production exports. Add integrated byte-mutation/alias/stale-source failure tests.

## Disposition
OPEN / R03 REQUIRED.