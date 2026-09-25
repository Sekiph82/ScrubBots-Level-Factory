# SB-LF07-004-C001 — Re-solve / Revalidate Every Mutation — Strict Audit Criteria

Target: `SB-LF07-004`

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
Make every applied mutation pass through authoritative post-mutation evidence before it can become an eligible candidate.

Required post-mutation chain:
1. exact child identity / LevelData binding;
2. M03 authoritative solver evidence;
3. M04 DifficultyAnalysis + Challenge Score/lane evidence;
4. M05 structural/production/solver/semantic QA as applicable;
5. derived child disposition from those stages.

Rules:
- PROVEN_UNSOLVABLE => reject child.
- INCONCLUSIVE/UNKNOWN_BOUND => review/retry/inconclusive, never unsolvable.
- validator/authority/evidence mismatch => ERROR/fail closed.
- missing capability => UNAVAILABLE, never PASS.
- no mutation result may bypass re-solve/revalidation based on parent acceptance.
- post-mutation evidence digests bind the exact child, operator request and parent lineage.
- QA/analysis must not mutate parent or child during evaluation.

Tests:
solved+valid child; proven-unsolvable child; inconclusive solver; structural reject; stale parent evidence replay; child hash mismatch; unavailable current-main capability; deterministic evidence envelope; non-mutation.

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
PASS only when every applied mutation is forced through the accepted M03/M04/M05 truth chain before eligibility.
