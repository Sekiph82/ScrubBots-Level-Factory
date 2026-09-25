# SB-LF05-008-C001 — Owner Source Byte Preservation QA
Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-09-25T03:10:30+03:00 (Europe/Istanbul)
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Repository identity: `Sekiph82/ScrubBots-Level-Factory`
- Branch: `main`
- Starting HEAD and `origin/main`: `8f2eb741725ebb37ad64ded81ca050e39c4b839f`
- Starting divergence: `HEAD...origin/main = 0 0`
- Initial status: clean tracked tree; preserved pre-existing untracked detached-worktree folders and Godot `.uid` files
- Protected tracker check: `git diff --exit-code -- TASKS.md` passed before implementation
- Authoritative prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/SB-LF05-008-C001_OWNER_SOURCE_BYTE_PRESERVATION_QA_PROMPT.md`
- Audit criteria: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/SB-LF05-008-C001_OWNER_SOURCE_BYTE_PRESERVATION_QA_AUDIT_CRITERIA.md`

## Authority and contracts read

- Root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, M05 master prompt/index/protocol, M03 and M04 closure summaries.
- SB-LF05-008 prompt and audit criteria, plus published SB-LF05-001..005/007 implementation and builder logs.
- Existing `owner_upload.py`, `studio_extensions.verify_owner_source`, source-library, and immutable evidence contracts.

## Scope and implementation boundary

This log covers only SB-LF05-008. The implementation will fail closed on source-record/byte drift, preserve exact bytes and SHA/length identity across analysis, and keep derived artifact references separate. It will not create a second source store, edit `TASKS.md`, create audit files, or claim acceptance.

## Chronological implementation record

- Builder log created before product or test edits.
- Added `src/scrubbots_pixel_factory/qa/source_preservation.py` and package exports. The helper binds recorded source SHA/length, verifies bytes before and after bounded analysis, detects source mutation/corruption, and carries derived artifact references separately.
- Added `tests/unit/test_sb_lf05_008_source_preservation.py` covering unchanged owner bytes with derived output, corrupt source identity, and analysis mutation fail-closed behavior.
- Focused command: `$env:PYTHONPATH='src'; python -m pytest -q tests/unit/test_sb_lf05_008_source_preservation.py -p no:cacheprovider` -> `2 passed`.

## Final handoff

Pending implementation and independent ChatGPT audit. Builder evidence is not acceptance.
