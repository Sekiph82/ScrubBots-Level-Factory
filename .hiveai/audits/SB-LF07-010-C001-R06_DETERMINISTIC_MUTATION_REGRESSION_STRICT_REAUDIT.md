# SB-LF07-010-C001-R06 — Strict Re-Audit

## Result
CHANGES_REQUIRED / FINAL REGRESSION INHERITS SB-LF07-008 SELF-ASSERTED PARENT PROVENANCE

## Closed in R06
- Seed-A / workload-seed-B false MATCHED regression is covered.
- Parent-bound same-seed config mismatch is covered.
- Missing parent provenance remains UNAVAILABLE.
- Full repository pytest is green: 1039 passed, 2 accepted capability skips.
- compileall, Godot headless, diff and protected-file gates are green.
- Previously closed M07 provenance/source/safety/accounting/governance/Palette V3 regressions remain retained.

## Remaining blocker
The positive MATCHED regression creates its “parent generation provenance” by directly injecting `generation_request.digest()` into a MutationCandidate payload. It does not prove that the parent candidate was actually produced by an accepted generation result/producer.

As a result, the final regression proves internal digest consistency, but not producer provenance authenticity.

## R07 requirement
After SB-LF07-008 introduces sealed producer-derived parent generation provenance:
- rebuild the aligned MATCHED regression through that accepted provenance constructor;
- add a forged raw payload SHA negative proving it stays UNAVAILABLE/non-MATCHED;
- retain seed mismatch, config mismatch, missing provenance and all previously closed regression gates;
- rerun full green gates.

## Disposition
OPEN / R07 REQUIRED; M07 remains ACTIVE.
