# SB-LF07-010-C001 — Deterministic Mutation Regression Closure — Strict Audit Criteria

Target: `SB-LF07-010`

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
Close M07 with an executable versioned regression corpus proving SB-LF07-001..009 together.

Corpus must cover:
- immutable interface/lineage and deterministic request/result identity;
- at least one real canonical hardening operator;
- at least one real canonical easing operator;
- mandatory post-mutation M03/M04/M05 chain;
- provenance/tamper/cycle/cross-lineage rejection;
- Challenge Score range targeting and missing constraint evidence;
- exact attempt budgets/exhaustion;
- mutate-vs-regenerate matched evidence;
- owner source byte preservation;
- Palette V3 and no size/color difficulty shortcuts.

Required:
- Declarative/versioned/checksummed fixtures where practical.
- Repeated clean runs produce identical canonical result digests and attempt sequences.
- Negative corpus must actually fail when trust/identity/authority/evidence is tampered.
- Representative parent LevelData/art/source bytes are unchanged before/after.
- No hidden skips/xfails or network/provider spend.
- Full M03/M04/M05/M06/M07 + Palette V3 regression remains green.

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
PASS only when M07 has a deterministic executable regression closure with no unresolved task-specific gap; only independent ChatGPT audit may declare M07 COMPLETE.
