# SB-LF07-005-C001 — Seed / Parent / Mutation Provenance — Strict Audit Criteria

Target: `SB-LF07-005`

Prerequisites:
- M03 Puzzle Intelligence = COMPLETE / VERIFIED.
- M04 Difficulty Intelligence = COMPLETE / VERIFIED.
- M05 Unified Factory Validation & Level QA = COMPLETE / VERIFIED.
- M06 Factory Studio + SB-LFX-001..017 = PASS/CLOSED.
- MAINT-PALETTE-V3-001 = PASS/CLOSED.

Global invariants:
- Root `TASKS.md` and `.hiveai/audits/**` are ChatGPT-owned; builder must not edit them.
- Canonical gameplay/mechanic authority remains current `Sekiph82/Scrubbots`; do not clone gameplay rules into Python.
- Palette authority is V3: C01..C16, BG01 presentation-only, production dimensions 20..59 per axis, used-color envelope 3..12, and difficulty is never inferred from board size or color count.
- Mutation never edits the parent candidate, accepted LevelData, owner source art, or canonical Scrubbots checkout in place. A mutation creates a new child candidate with new identity.
- Every mutation truth must be deterministic and provenance-bound to exact parent/request/seed/operator/version/authority identities.
- Missing canonical mechanic/evidence/capability is `UNAVAILABLE` or `INCONCLUSIVE`, never fabricated PASS.
- A mutated child is not production-accepted merely because mutation succeeded. M03/M04/M05 truth remains authoritative.
- Wall-clock timing is operational telemetry only, never canonical correctness/difficulty truth.
- No network/provider credits merely for tests; no new skip/xfail may hide failures.

Task contract:
Define complete immutable mutation provenance for every attempt and child.

Required provenance:
- mutation request id/digest;
- deterministic seed and seed derivation/version;
- parent candidate/LevelData/source/art digests;
- parent lineage root and immediate parent identity;
- operator id/version/intent and canonical mechanic authority digest;
- attempt ordinal where applicable;
- pre-state digest, post-state/child digest;
- post-mutation M03/M04/M05 evidence digests when available;
- disposition/reason code.

Rules:
- canonical provenance is deterministic and content-bound.
- no caller may overwrite derived parent/child/evidence digests.
- reject cycles, self-parenting, missing immediate parent, mixed lineage roots, stale authority, and duplicate child identity with conflicting provenance.
- timestamps/paths/wall-clock remain metadata only.
- lineage supports deterministic replay from recorded parent + request + seed + operator version.

Tests:
round-trip parser; tamper; cycle; cross-root mix; seed drift; operator drift; evidence drift; duplicate conflict; deterministic replay.

Required gates:
- Focused tests for this task and all earlier implemented M07 tasks.
- Retained M03/M04/M05/M06 and Palette V3 contract tests relevant to the changed surface.
- Full repository `python -m pytest -q -p no:cacheprovider` green except pre-existing explicitly capability-gated skips.
- `python -m compileall -q src tests` PASS.
- Level Factory Godot headless editor/test suites relevant to changed runtime/editor surfaces PASS.
- `git diff --check` PASS.
- `git diff --exit-code -- TASKS.md` PASS.
- If current-main canonical mechanic execution is required, use a clean exact-SHA Scrubbots checkout/read-only capability and prove non-mutation.

Acceptance:
PASS only when every mutation/attempt can be reconstructed and audited without trusting caller-supplied parallel identity claims.
