# SB-LF07-007-C001 — Bounded Mutation Attempts — Strict Audit Criteria

Target: `SB-LF07-007`

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
Add deterministic finite budgets to mutation targeting/search.

Required:
- Versioned attempt budget with positive finite max attempts and any explicit per-operator/child bounds needed.
- No while/unbounded recursion/path can exceed the declared budget.
- Attempt ordinal is deterministic and bound into provenance.
- Budget exhaustion => explicit EXHAUSTED/INCONCLUSIVE-style outcome, never UNSOLVABLE and never target success.
- Wall-clock timeout may abort operationally but is not canonical budget identity.
- Replaying identical parent/request/seed/operator set/budget yields same attempt sequence and terminal canonical result.
- Invalid zero/negative/overflow/unreasonably unbounded budgets fail closed.
- Each attempt still uses SB-LF07-004 post-mutation M03/M04/M05 validation.

Tests:
success before limit; exact-limit exhaustion; one-attempt budget; invalid budget; deterministic sequence; operational timeout separation; no post-limit operator calls; provenance ordinals.

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
PASS only when mutation targeting is provably finite and deterministic with truthful exhaustion semantics.
