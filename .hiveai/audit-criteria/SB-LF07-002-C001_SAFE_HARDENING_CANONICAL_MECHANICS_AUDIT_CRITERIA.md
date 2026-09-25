# SB-LF07-002-C001 — Safe Hardening Mutations / Canonical Mechanics — Strict Audit Criteria

Target: `SB-LF07-002`

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
Implement safe HARDEN mutation operators only where semantics can be tied to real canonical Scrubbots mechanics.

Required:
- Discover and record exact current-main authority for each hardening operator: repository, commit SHA, source path, mechanic/contract version.
- Closed operator registry; each operator declares preconditions, deterministic transform, invariants preserved, and authority.
- At least one real hardening operator must be bound to a canonical mechanic and exercised end-to-end; otherwise the task remains UNAVAILABLE and cannot PASS.
- No operator may use board dimensions, used-color count, visual fragmentation, arbitrary art edits, or descriptive difficulty class as a proxy for hardening.
- A hardening operator may only alter fields/state that the canonical mechanic authority proves are legal mutation surfaces.
- Every output remains a child candidate, not accepted content.
- Unsupported mechanic/operator request => INAPPLICABLE/UNAVAILABLE, not a guessed transform.
- Parent/owner sources and current-main checkout remain unchanged.

Tests:
real authoritative operator; deterministic replay; inapplicable precondition; wrong/stale authority; illegal field mutation; dimensions/color-count shortcut rejection; parent non-mutation; operator registry closure.

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
PASS requires at least one proven canonical hardening operator with exact authority and no invented gameplay semantics.
