# SB-LF07-003-C001 — Safe Easing Mutations / Canonical Mechanics — Strict Audit Criteria

Target: `SB-LF07-003`

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
Implement safe EASE mutation operators only where semantics can be tied to real canonical Scrubbots mechanics.

Required:
- Same authority discipline as SB-LF07-002: exact current-main repo/SHA/source path/version per operator.
- At least one real easing operator bound to a canonical mechanic and exercised end-to-end; otherwise no PASS.
- Closed deterministic operator registry with preconditions and preserved invariants.
- Easing must not mean resize smaller, reduce colors, recolor art, or assign an easier class.
- Do not delete/disable canonical mechanics unless the canonical contract explicitly defines that field/state as a legal mutation surface.
- Unsupported requests fail closed.
- Every output is a new child candidate; parent/source/current-main checkout remain immutable.

Tests:
real easing operator; deterministic replay; inapplicable state; stale authority; illegal mechanic deletion; size/color proxy rejection; parent non-mutation; registry closure.

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
PASS requires at least one real authority-bound easing operator with no heuristic or fabricated mechanic semantics.
