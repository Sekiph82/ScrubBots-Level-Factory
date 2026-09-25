# SB-LF07-008-C001 — Mutate vs Regenerate Efficiency Comparison — Strict Audit Criteria

Target: `SB-LF07-008`

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
Provide a reproducible evidence comparison between mutation targeting and regeneration without turning a benchmark into production truth.

Required:
- Compare matched workloads: same target policy/range, canonical seed/config identity, validation requirements and declared budgets.
- Mutation path uses M07; regeneration path uses an already accepted generator route only. Do not invent a new generator.
- Record deterministic/canonical counters where meaningful: attempts/candidates produced, accepted/eligible count, rejection/inconclusive counts, solver states/evidence workload where available, and provider cost/credits only from trusted existing accounting evidence.
- Wall-clock duration and machine-specific resource usage may be recorded only as non-canonical telemetry.
- Do not declare mutate or regenerate globally superior; return evidence for the matched case.
- Preserve exact lineage and separate the two paths.
- No provider spending merely to make tests pass; use deterministic fixtures/mocks for cost boundaries.

Tests:
matched-case comparison; mismatched target/budget rejection; zero accepted; inconclusive outcomes; trusted/untrusted cost evidence; deterministic counters; telemetry exclusion from digest.

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
PASS only when the comparison is apples-to-apples, provenance-bound and does not convert incidental runtime timing into canonical strategy truth.
