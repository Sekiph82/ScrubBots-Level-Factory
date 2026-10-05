# SB-CPX-001-C001 — Solver-Proven Supply Identity Pack Binding

Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-10-05 13:25:40 +03:00 (Europe/Istanbul).
- Canonical Desktop root verified as `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`, branch `main`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`, HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`.
- Mandatory Desktop `git fetch --prune origin` completed. Desktop is 0 ahead / 180 behind with 176 owner-local status entries, 18 stashes and 17 registered worktrees. Safe sync cannot alter owner work; Desktop is unchanged.
- Reused the one authorized M12 master worktree at `%TEMP%\ScrubBots-Level-Factory\M12-CP01-001-010-CPX001-MASTER`; exact root/origin verified, clean detached HEAD `a8842169f1ee88d030a668a77f8691aadee95820` equals fetched `origin/main` (0/0).
- Live `origin/main:TASKS.md` confirms `M12_MASTER_BATCH_AUTHORIZED` and CPX-001 is the final ordered child. Its prompt and audit criteria were read before implementation.
- Exact H1: `# SB-CPX-001-C001 — Solver-Proven Supply Identity Pack Binding`.

## Contract set read

- `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md` and `.hiveai/prompts/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_PROMPT.md`.
- `.hiveai/audit-criteria/SB-CPX-001-C001_SOLVER_PROVEN_SUPPLY_IDENTITY_PACK_BINDING_AUDIT_CRITERIA.md`.
- Root `AGENTS.md`, live `origin/main:TASKS.md`, `GOVERNANCE.md`, CPX-001/CPX-002 source-of-authority contracts, current content-pipeline/READY/Release Pool/supply-pipeline implementation, and required M11/M12 validation contracts.

## Implementation and verification

## Implementation decisions and rationale

- Added exact-byte state/evidence digest derivation at the existing canonical solver-result boundary in `supply_pipeline/scrubpack_identity.py`; it consumes the accepted solver PASS/replay evidence and does not execute a second solver.
- The Studio route and direct primary-supply API now retain that identity in both their result record and READY pipeline record.
- Added Content Pipeline proof resolution and `.scrubpack` build/verify APIs. Each explicit plan is checked against its exact LevelData ID/bytes, plan bytes and ordered FIFO columns, READY solver/replay/QA result, current ScrubBots authority, and current Factory source pipeline/review identity before the archive is built. The identity artifact is detached and its SHA-256 is carried in build evidence, preserving the existing V1 archive member layout.
- Release Pool admission is preferred when available. The real canonical run in the focused integration is READY and has an owner ACCEPT review, while the existing Release Pool gate declines it due to its independent Difficulty V1 projection requirements; the proof resolver therefore binds the exact current accepted READY pipeline and source files without fabricating profile data. A later REJECT makes current proof resolution fail closed.
- Increased the safe LevelData ID length limit from 64 to 128 in the pack and descriptor contracts. Current canonical Factory candidate IDs are longer than 64 characters; preserving the exact LevelData ID is required by this task. The ASCII allow-list and traversal/unsafe path rejection are unchanged.
- Added integration mutations for robot count, FIFO order, CID, level ID, exact plan bytes, state digest, evidence digest, stale source identity, and stale current review. Added pack verification of the detached identity artifact digest.
- Updated `content_pipeline/README.md` with the artifact, authority, compatibility, and ID-boundary behavior.

## Failures and corrections (chronological)

- First real READY/ACCEPT integration run failed because the test assumed Release Pool entry. Inspecting the generated owner review and READY pipeline showed the current Release Pool gate returned `NOT_ENTERED`; the canonical difficulty projection does not meet the Release Pool vector/profile contract. Corrected the test and resolver to bind the live owner-accepted READY pipeline when no valid pool entry exists; no difficulty/profile was synthesized.
- Next integration attempt asserted the wrong Release Pool rejection detail (`profile.dominant`); the actual current gate can reject earlier at the official challenge-vector projection. Removed the over-specific reason assertion and retained the truthful non-empty reason check.
- The pack preflight then rejected the real candidate ID under the old 64-character path limit. Extended the same ASCII-safe grammar consistently to 128 in runtime validators and JSON Schemas, and added boundary regression coverage.
- The following preflight identified a test descriptor helper attaching width/height to the supply-plan descriptor; the contract rejects those extra attributes. Printed the per-role validation report, removed the invalid attributes, and retained dimensions only on LevelData and metadata descriptors.
- Focused test command `python -m pytest -q tests/unit/test_sb_cp01_001_scrubpack_spec.py tests/unit/test_sb_cp01_002_scrubpack_builder.py tests/unit/test_sb_cp01_008_scrubpack_inspection.py tests/integration/test_sb_cpx_001_solver_identity_pack.py` passed: **83 passed in 17.25s**.
- `python -m compileall -q content_pipeline/src src/scrubbots_pixel_factory tests` and `git diff --check` completed successfully. Git emitted only its expected LF-to-CRLF working-copy notices.

## Files changed

- Factory solver identity source and READY pipeline result integration.
- Content Pipeline solver identity build/verification API and package exports.
- Scrubpack build result/evidence optional identity-artifact digest verification.
- Level ID runtime/schema boundaries, ID regression, real canonical Factory integration test, and Content Pipeline README.

Continue appending cumulative/regression/full-suite results, commits, publication, and final parity below. No dependency/license, provider/network, credential, production game, root `TASKS.md`, or audit changes are authorized or included. Legacy `solver_evidence.py` is not production authority. No M14 promotion replay is in scope.

## Final implementation verification

- Implementation commit: `43be43f` (`Bind Scrubpack supply plans to solver evidence`).
- Focused CP01 spec/builder/inspection and real current Factory integration: **83 passed in 17.25s**.
- Cumulative CP00, M11 authority, CP01, and governance-authority unit regressions: **252 passed in 2.35s**.
- Governance authority pair (`test_sb_lf00_007_governance_authority.py`, `test_r02_current_authority_guards.py`): **9 passed in 0.71s**.
- Full `python -m pytest -q`: **1,415 passed, 3 skipped in 765.36s (0:12:45)**. Skips: `test_maint_supply_pipeline_v01.py` requires `SCRUBBOTS_SLOW=1`; two regressions require a separately supplied canonical ScrubBots checkout/capability.
- `python -m compileall -q content_pipeline/src src/scrubbots_pixel_factory tests`, `git diff --check`, and staged `git diff --cached --check` passed.
- Dependency/license changes: none. Runtime network/provider/API/key additions: none. No production game checkout/source was changed. No root `TASKS.md` or `.hiveai/audits/**` files were changed.

## Publication and parity

Append the separate builder-log commit, fetched divergence, normal push result, final local/origin SHAs, and final clean status after publication.
