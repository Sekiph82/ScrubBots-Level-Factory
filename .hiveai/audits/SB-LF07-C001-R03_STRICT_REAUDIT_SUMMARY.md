# SB-LF07-001,004..010-C001-R03 — Strict Re-Audit Summary

## Result

PASS / CLOSED:
- SB-LF07-001
- SB-LF07-002
- SB-LF07-003

CHANGES_REQUIRED:
- SB-LF07-004
- SB-LF07-005
- SB-LF07-006
- SB-LF07-007
- SB-LF07-008
- SB-LF07-009
- SB-LF07-010

M07 remains ACTIVE.

## Principal R03 findings
- 001: true lower-level mutation substrate separation is accepted.
- 004: authentic adapters improved, but public legacy synthetic eligibility APIs can still manufacture ELIGIBLE; M05 authority sealing and one logged SHA typo remain.
- 005: authentic typed references are generated, but caller replacement/direct construction remains production-valid to the ledger.
- 006: default builder truthfully reports safety UNAVAILABLE, but public SafetyConstraintEvidence/TypedChallengeTarget allow caller-forged TRUE constraints; tests use that bypass.
- 007: bounded semantics are strong, but forged target authority and uncaught selection/provenance contract errors remain.
- 008: accounting truth is fixed, but workload config is only seed-matched and GenerationResult.SUCCESS is incorrectly treated as accepted without equivalent M03/M04/M05 validation.
- 009: successful applied path has real M05 pre/post verification, but non-applied/error/exception operation paths can skip post-check.
- 010: regression still encodes forged safety and does not cover remaining sealed-boundary negatives.

## R04
Only SB-LF07-004..010 are authorized for R04. SB-LF07-001..003 are frozen PASS/CLOSED.
