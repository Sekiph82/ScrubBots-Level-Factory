# SB-LF07-006-C001 — Challenge Score Range Targeting — Strict Audit Criteria

Target: `SB-LF07-006`

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
Implement deterministic mutation targeting toward an explicit Challenge Score interval while respecting accepted load/risk/retention constraints.

Required:
- Target request uses explicit numeric lower/upper Challenge Score bounds and exact accepted M04 policy/version.
- Candidate evaluation consumes real post-mutation M04 Challenge Score and lane evidence from SB-LF07-004, never metadata heuristics.
- Width/height/color-count/difficulty label are forbidden target proxies.
- Load/risk/retention constraints may only be evaluated from accepted available evidence. Missing required evidence => INCONCLUSIVE/UNAVAILABLE, not zero/default PASS.
- Selection policy is versioned and deterministic for equal evidence.
- Target match means score in requested range AND all required safety/load/risk/retention gates satisfied.
- This task defines targeting/selection semantics, not unbounded search; attempt budgeting belongs to SB-LF07-007.
- Never mutate owner source art to chase score.

Tests:
below/in/above range; equal-score deterministic tie; missing risk/load evidence; score-policy mismatch; stale difficulty digest; forbidden metadata proxy; no acceptable candidate; parent/source non-mutation.

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
PASS only when targeting is driven by accepted M04 evidence and safety constraints, not visual/size/color heuristics.
