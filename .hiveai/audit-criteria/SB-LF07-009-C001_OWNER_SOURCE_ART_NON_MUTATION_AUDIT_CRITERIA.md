# SB-LF07-009-C001 — Owner Source Art Non-Mutation — Strict Audit Criteria

Target: `SB-LF07-009`

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
Enforce the M05 immutable OWNER_UPLOAD/source-library boundary throughout all M07 paths.

Required:
- Mutation target must be candidate/LevelData/gameplay-config state, never immutable owner source bytes.
- Before/after any M07 operation that has access to source records, verify exact source SHA/length/dimensions/record identity.
- Any derived preview/art/revision/output path must not alias source path/content identity.
- If a future explicitly authorized visual mutation exists, it must create a new derived artifact/revision with explicit lineage; it still may not overwrite or masquerade as OWNER_UPLOAD.
- Stale/corrupt/missing source record fails closed.
- Hardening/easing/targeting cannot silently recolor, resize, quantize, normalize or rewrite owner art to reach difficulty.
- Repeated mutation/targeting is idempotent with respect to owner source bytes.

Tests:
source alias; source byte mutation; corrupt record; derived-path collision; silent recolor/resize attempt; repeated run; path metadata trick; valid candidate-only mutation with source unchanged.

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
PASS only when every M07 code path proves owner source art is immutable and difficulty targeting cannot silently alter it.
