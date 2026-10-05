# SB-CP01-009-C001 — Deterministic .scrubpack Bytes

Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-10-05 12:33:56 +03:00 (Europe/Istanbul).
- Canonical Desktop repository identity confirmed at `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`: `Sekiph82/ScrubBots-Level-Factory`, branch `main`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`, HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`.
- Mandatory Desktop `git fetch --prune origin` completed. Desktop `main` is 0 ahead / 173 behind; 176 status entries include owner-local modifications/untracked files, 18 stashes, and 17 registered worktrees. Safe fast-forward/reconciliation is not possible without altering or conflicting with owner work. Desktop is unchanged. The already-authorized single M12 worktree under `%TEMP%\ScrubBots-Level-Factory\M12-CP01-001-010-CPX001-MASTER` is reused.
- Execution worktree root verified, origin exact, detached HEAD `8547a654c9cd11ad784a3f78cc05237b7023c8f1`, equal to fetched `origin/main` (0/0), clean; 18 shared stashes and 17 registered worktrees inspected.
- Live `origin/main:TASKS.md` confirms `M12_MASTER_BATCH_AUTHORIZED` and child order through `SB-CP01-009`.
- Read master prompt and Child 9 prompt/criteria before implementation. Child 9 exact H1 is `# SB-CP01-009-C001 — Deterministic .scrubpack Bytes`.

## Contract set read

- `.hiveai/prompts/M12_CP01_001_010_CPX001_MASTER_IMPLEMENTATION_PROMPT.md`.
- `.hiveai/prompts/SB-CP01-009-C001_DETERMINISTIC_SCRUBPACK_BYTES_PROMPT.md`.
- `.hiveai/audit-criteria/SB-CP01-009-C001_DETERMINISTIC_SCRUBPACK_BYTES_AUDIT_CRITERIA.md`.
- Root `AGENTS.md`, live `origin/main:TASKS.md`, `GOVERNANCE.md`, and relevant M11/M12 builder logs, prompts, and contracts for manifest canonicalization, ordering, payload validation, and deterministic build behavior.

## Implementation and verification

Work has not started. Record implementation decisions, commands, failures/corrections, focused and full regression results, changed files, commit/push evidence, and final parity chronologically below.

### Implementation and regression results

- Implementation commit `6f018438ec692003a4770f6b30ae1353852f4721` fixes all writer-controlled ZIP metadata through explicit `ZipInfo` values: fixed DOS epoch timestamp, ASCII names, ZIP_STORED/no compression (there is no compression level for stored entries), Unix creator and version values, regular 0644 mode, zero flags/volume/internal attributes, empty comments/extras, no ZIP64, and stable member order. Archive SHA-256 remains external.
- Added tests asserting the exact ZIP fields and launching two independent Python processes in separate build directories with identical explicit payloads; both archive bytes and final hashes must match.
- Updated `docs/content_platform/SCRUBPACK_V1_SPEC.md` with the byte-level ZIP policy. Documentation commit: `e55fabe03dea56c092e6768167b8eeb0ba39b5c0`.
- `python -m pytest -q tests/unit/test_sb_cp01_002_scrubpack_builder.py` -> 33 passed. Combined Child 1/2/8 pack tests -> 69 passed. Cumulative CP00/M11 + prior M12 pack regressions: 232 passed. Governance pair -> 13 passed.
- Required full `python -m pytest -q` -> `1401 passed, 3 skipped in 1123.79s (0:18:43)`. Skips were the configured slow supply pipeline test and two canonical-game-capability-gated tests.
- After the spec documentation update, pack plus governance focused tests -> 82 passed in 1.99s. `python -m compileall -q content_pipeline/src tests` and `git diff --check` passed.
- Initial inspection commands used two nonexistent test/spec paths and emitted path-not-found diagnostics; corrected using `rg --files`, the actual `tests/unit/test_sb_cp01_002_scrubpack_builder.py`, and `docs/content_platform/SCRUBPACK_V1_SPEC.md`. No implementation or tests were affected by those read-only path errors.
- Source changes add no dependencies, licenses, network/provider/runtime calls, credentials, production-game mutations, tracker changes, or audit edits. Focused and full tests pass.
- Implementation push and post-push equality check are pending.
- Implementation publication: pre-push fetch reported 2/0; normal git push origin HEAD:main succeeded. Post-push fetch confirmed local HEAD and origin/main both 55fabe03dea56c092e6768167b8eeb0ba39b5c0, 0/0. Separate child-log publication follows.
