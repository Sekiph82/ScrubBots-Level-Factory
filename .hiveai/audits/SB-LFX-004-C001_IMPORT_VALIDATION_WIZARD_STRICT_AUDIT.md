# SB-LFX-004-C001 — Import Validation Wizard — Strict Audit

## VERDICT

**CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Severity:
- BLOCKER: 0
- MAJOR: 1
- MINOR: 0
- NOTE: 1

## Audited chain

- Start: `c683e240218414a0010b0ba79a6f6ef11e3c0f0e`
- Implementation: `ef115dcd09e992ca00a934c952b2bdb765558355`
- Task-final log-only: `a6b87e6cd22a9553e0e0347654f6c4c1e16d5b95`
- Final shared hardening: `f4001e3060c83b6a2cf9f51b72cc8f974110cba8`

## Accepted implementation semantics

The product implementation is substantially correct:
- validation starts by re-verifying exact OWNER_UPLOAD source truth;
- exact source pixels are interpreted read-only;
- 20..59 independent dimensions are checked;
- canonical palette membership, foreign-color count, transparent/semi-alpha counts and used C-IDs are derived in Python;
- exact logical sources use canonical `evaluate_grid(..., QualityPolicy())`;
- non-exact sources report `DERIVED_ARTIFACT_REQUIRED` / structural NOT APPLICABLE and identify CELL_MAJORITY_V1 / PALETTE_SNAP_V1 without applying them;
- evidence is separately persisted with source ID/hash/record identity and immutable write semantics;
- source bytes/record are not mutated;
- solver/difficulty/owner acceptance remain unavailable.

No product-semantics blocker was found.

## MAJOR-001 — required real-runtime acceptance matrix is incomplete

The audit criteria explicitly require committed real integration evidence for:
1. semi-alpha or canonical alpha-invalid input;
2. tampered source/evidence fail-closed behavior.

The committed Godot integration exercises only:
- one exact-valid 20x20 canonical RGB source; and
- one 19x20 foreign-color source.

The focused Python tests similarly cover exact-valid and foreign/illegal-dimension cases, but do not cover semi-alpha and do not tamper the source/evidence contract.

Therefore required runtime proof is missing even though the implementation contains code paths for these conditions.

### Required remediation

Add committed acceptance coverage that:
- imports/constructs a supported PNG containing semi-alpha or another canonical alpha-invalid case and proves `ALPHA_CONTRACT` / derived-artifact-required truth;
- tampers a bounded OWNER_UPLOAD source record/bytes and proves validation fails closed with no trusted report;
- tampers or conflicts with existing immutable validation evidence and proves it is not silently overwritten/trusted;
- proves source bytes remain unchanged across these failure paths.

Prefer adding these to the real Godot integration, with focused Python coverage as supplemental evidence.

## Publication / regression

The task-final publication is log-only. Builder reports focused tests and real validation integration PASS. Per-task full pytest was not recorded, but the completed batch later reports 759 passed, 1 warning.

## NOTE

The final batch hardening changes only shared transport/static-regression syntax for this task and does not resolve MAJOR-001.

## Disposition

Implementation remains retained. `SB-LFX-004` is **not closed** until MAJOR-001 is remediated and re-audited.
