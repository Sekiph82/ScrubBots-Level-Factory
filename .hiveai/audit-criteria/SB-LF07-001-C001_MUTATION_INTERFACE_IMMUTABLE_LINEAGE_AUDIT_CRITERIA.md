# SB-LF07-001-C001 — Mutation Interface / Immutable Lineage — Strict Audit Criteria

Target: `SB-LF07-001`

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
Define the versioned mutation boundary before implementing hardening/easing policy.

Required:
- Closed typed mutation request/result/disposition model.
- Request binds exact parent candidate/LevelData identity, parent source/art identities where present, operator id + operator contract version, deterministic seed, requested intent, and exact canonical authority identity.
- Parent bytes/objects are read-only. Mutation returns a distinct child identity and payload; parent and child may never alias mutable state.
- Result records pre/post digests and an immutable parent->child lineage edge.
- Closed dispositions at minimum: APPLIED, NO_CHANGE, INAPPLICABLE, UNAVAILABLE, ERROR. Caller cannot self-declare acceptance.
- Canonical serialization/digest excludes timestamps, paths and wall-clock duration.
- Operator execution is interface/registry based; this task must not invent gameplay mechanics or difficulty heuristics.
- Deterministic replay of the same exact request produces the same child digest/disposition.

Negative tests:
mutable aliasing; parent mutation; malformed operator/version/seed; stale parent digest; wrong authority; unknown disposition/operator; non-deterministic replay; path/timestamp identity contamination.

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
PASS only when M07 has an immutable deterministic mutation substrate that cannot rewrite its parent or mint unsupported gameplay truth.
