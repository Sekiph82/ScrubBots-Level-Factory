# SB-CP01-010-C001 — Reject Unsupported Pack Versions Safely

Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-10-05 12:58:39 +03:00 (Europe/Istanbul).
- Canonical Desktop root verified as `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`, branch `main`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`, HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`.
- Mandatory Desktop `git fetch --prune origin` completed. Desktop `main` is 0 ahead / 177 behind with 176 dirty status entries, 18 stashes, and 17 registered worktrees. Owner-local work makes synchronization unsafe; Desktop remains unchanged.
- Reused the authorized M12 master worktree under `%TEMP%\ScrubBots-Level-Factory\M12-CP01-001-010-CPX001-MASTER`; root/origin verified, clean detached HEAD `159270ca785f81665a111f900c7e29ffeaa55be4`, equal to fetched `origin/main` (0/0). Shared stashes/worktrees inspected.
- Live `origin/main:TASKS.md` confirms `M12_MASTER_BATCH_AUTHORIZED` and Child 10 is next. Child 10 prompt and criteria were read before edits.
- Exact H1: `# SB-CP01-010-C001 — Reject Unsupported Pack Versions Safely`.

## Contract set read

- `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
- `.hiveai/prompts/SB-CP01-010-C001_UNSUPPORTED_PACK_VERSION_REJECTION_PROMPT.md`.
- `.hiveai/audit-criteria/SB-CP01-010-C001_UNSUPPORTED_PACK_VERSION_REJECTION_AUDIT_CRITERIA.md`.
- Root `AGENTS.md`, live `origin/main:TASKS.md`, `GOVERNANCE.md`, Child 1/2/7/8/9 contracts, and current builder/spec/inspector implementation.

## Implementation and verification

Work has not started. Append implementation decisions, test cases and outcomes, any failures/corrections, changed files, commit/push evidence, and final parity chronologically below.

### Implementation and regression results

- Implementation commit `3f51c51aaaca8405283fceed8ad89157da474897` adds the explicit `SUPPORTED_SCRUBPACK_VERSIONS = {1}` set and uses it in the strict manifest model. The builder always emits manifest V1 and its existing M11 validators reject non-V1 payload contracts before archive creation.
- The inspector now deterministically classifies missing/malformed manifest versions as `INVALID_MANIFEST`, unsupported manifest schema/version as `UNSUPPORTED_VERSION`, malformed member version markers as `INVALID_MEMBER_VERSION`, and future/mixed member schema/version contracts as `UNSUPPORTED_VERSION`. It verifies member digests and all version/schema markers before extraction creates its temporary or final destination. Human and machine reports share the fixed reason codes.
- Added tests for missing manifest schema/version, booleans, strings, zero, negative and future values, unknown manifest schema, mixed level/supply/metadata versions, and source/destination preservation for inspect/extract rejection. The V1-only supported set is asserted. Updated `.hiveai` V1 spec docs with the version gate and reason codes.
- First focused run failed 11 new cases with `NameError: PACK_MANIFEST_PATH is not defined` in the test module. Added the missing test import; rerun `python -m pytest -q tests/unit/test_sb_cp01_001_scrubpack_spec.py tests/unit/test_sb_cp01_002_scrubpack_builder.py tests/unit/test_sb_cp01_008_scrubpack_inspection.py` passed `81 passed in 24.79s`; the post-commit rerun passed `81 passed in 0.70s`.
- Cumulative CP00/M11 + prior M12 pack suite: `244 passed in 2.18s`. Governance pair: `13 passed in 1.03s`.
- Required full `python -m pytest -q`: `1413 passed, 3 skipped in 1132.21s (0:18:52)`. Skips were the configured slow supply pipeline test and two canonical-game-capability-gated tests.
- `python -m compileall -q content_pipeline/src tests` and `git diff --check` passed. Rejected version inspection/extraction tests assert source bytes remain identical and no destination is created.
- Initial grouped source patch did not apply because import context differed; it was split into smaller scoped patches. No files changed from that failed patch attempt. An initial documentation-path read used a nonexistent location; `rg --files` identified `docs/content_platform/SCRUBPACK_V1_SPEC.md`.
- No dependencies/licenses, network/provider/runtime calls, credentials, production-game changes, root tracker, or audit changes. Implementation push and separate log publication are pending.
- Implementation publication: pre-push fetch showed 1/0; normal git push origin HEAD:main succeeded. Post-push fetch confirmed local HEAD and origin/main both 3f51c51aaaca8405283fceed8ad89157da474897, 0/0. Separate builder-log publication follows.
