# SB-LF09-001-C001 — Experimental Evolutionary Selection

Document role: CODEX BUILDER LOG

## Starting record

- Starting timestamp: 2026-09-27T22:01:52.1598707+03:00
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
- Canonical checkout verified: isolated worktree at `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LF09-001-C001-20260927`; owner mirror preserved at `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Source branch: `main`; isolated worktree is detached at the fetched `origin/main` commit as required by the safe-worktree procedure.
- Starting local HEAD: `4ee246a8391c97123ebfdde7c319b4500d864866`
- Starting `origin/main`: `4ee246a8391c97123ebfdde7c319b4500d864866`
- Starting canonical-owner checkout state: dirty and 31 commits behind before fetch; owner changes were preserved and were not reset, cleaned, stashed, rebased, overwritten, or synchronized in place.
- Synchronization result: `git fetch origin --prune` completed; safe isolated worktree created from the fetched `origin/main`. No fast-forward was applied to the dirty owner mirror.
- Required actor/task authorization: live `origin/main:TASKS.md` authorizes `SB-LF09-001`, status `READY_FOR_IMPLEMENTATION / M09-001_AUTHORIZED`, Required Actor `CODEX`.

## Authority and contracts read

- `TASKS.md` from live `origin/main`.
- `AGENTS.md`, `README.md`, `GOVERNANCE.md`, `CLAUDE.md`, and `THIRD_PARTY_NOTICES.md` from live `origin/main`.
- `.hiveai/prompts/SB-LF09-001-C001_EXPERIMENTAL_EVOLUTIONARY_SELECTION_PROMPT.md` from live `origin/main`.
- `.hiveai/audit-criteria/SB-LF09-001-C001_EXPERIMENTAL_EVOLUTIONARY_SELECTION_AUDIT_CRITERIA.md` from live `origin/main`.
- `.hiveai/audits/SB-LF08-C001-R01_STRICT_AUDIT_SUMMARY.md` from live `origin/main`.
- Canonical accepted-candidate/evidence contracts in `m08_batch.py` and M07 lineage/provenance contracts in `mutation_base.py` / `m07_services.py`.

## Authorized scope and implementation plan

Implement only the offline, deterministic, bounded, explicitly opt-in experimental evolutionary-selection prototype for accepted M08 candidate evidence. Preserve exact candidate/source lineage and immutable evidence references; reject missing, unavailable, invalid, duplicate, or cross-candidate identities; do not alter production generation, publication, M03/M04/M05/M07 gates, source-art bytes, or add network/provider/telemetry/API-key/runtime HTTP behavior. Add focused contract tests and run the required retained and repository gates. Builder evidence remains subject to independent ChatGPT audit.

Further entries will be appended chronologically as implementation, verification, and publication occur.

## Chronological implementation and verification

- Implementation files changed: `src/scrubbots_pixel_factory/evolutionary_selection.py`, package exports in `src/scrubbots_pixel_factory/__init__.py`, and `tests/unit/test_sb_lf09_001_evolutionary_selection.py`.
- The prototype accepts only canonical M08 `CandidateEvidence`, requires `EXPERIMENTAL_EVOLUTIONARY_SELECTION_V1`, validates unique candidate/lineage/bundle/generation identities, ranks existing immutable evidence deterministically by versioned policy and seed, records immutable selection provenance, and fails closed for unavailable/invalid evidence, insufficient population, and insufficient budget.
- The experimental module has no generator-router, CLI, publication, provider, telemetry, API-key, or runtime HTTP integration; it never changes source-art or accepted evidence bytes.
- First focused command: `python -m pytest -q tests/unit/test_sb_lf09_001_evolutionary_selection.py`; initial result `6 failed, 2 passed` because the new test fixture passed constructor fields both positionally and by keyword. This was a test-only fixture error; it was corrected immediately and the rerun passed `8 passed`.
- Retained M08/M07 command: `python -m pytest -q tests/unit/test_m08_batch.py tests/unit/test_m08_output.py tests/unit/test_sb_lf07_*.py`; result `26 passed`.
- Corrected focused command: `python -m pytest -q tests/unit/test_sb_lf09_001_evolutionary_selection.py`; result `9 passed` after adding the forged-lineage constructor regression.
- First full command: `python -m pytest -q`; result `1073 passed, 2 skipped in 543.11s`. Skips were the pre-existing unavailable canonical ScrubBots checkout capability in `test_sb_lf03_002_compact_solver_state.py` and `test_sb_lf04_012_regression.py`; no skip/xfail was added by this task.
- Final full command after the final focused test addition: `python -m pytest -q`; result `1074 passed, 2 skipped in 528.85s (0:08:48)`, with the same two truthful capability skips.
- Compile gate: `python -m compileall -q src tests`; `PASS`.
- Godot gate: `godot_console.exe --headless --editor --path . --quit`; Godot `4.7.2.stable.official.ed1daf0bf`, exit `0`.
- Protected-file and hygiene gates: `git diff --check` `PASS`; `git diff --exit-code -- TASKS.md` `PASS`; active prompt and `.hiveai/audits/**` diff checks `PASS`.
- Offline/security review: only Python standard-library hashing/JSON/dataclass/enum logic was added; no dependency, license, network, provider, telemetry, API-key, or runtime HTTP changes were made. The core offline invariant remains intact.
- Evidence URLs: repository `https://github.com/Sekiph82/ScrubBots-Level-Factory`; prompt `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/4ee246a8391c97123ebfdde7c319b4500d864866/.hiveai/prompts/SB-LF09-001-C001_EXPERIMENTAL_EVOLUTIONARY_SELECTION_PROMPT.md`; audit criteria `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/4ee246a8391c97123ebfdde7c319b4500d864866/.hiveai/audit-criteria/SB-LF09-001-C001_EXPERIMENTAL_EVOLUTIONARY_SELECTION_AUDIT_CRITERIA.md`; previous audit `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/4ee246a8391c97123ebfdde7c319b4500d864866/.hiveai/audits/SB-LF08-C001-R01_STRICT_AUDIT_SUMMARY.md`.

## Pre-publication state

- Timestamp: 2026-09-27T22:24:40.4454579+03:00
- Final pre-commit paths: only the three authorized implementation/test paths plus this matching builder log.
- `TASKS.md`, `.hiveai/audits/**`, and the active prompt are unchanged.
- Implementation commit and the separate log-publication commit are still pending; no acceptance is claimed.

## Publication record

- Implementation commit: `6e1097bfb49801c6e89fc54d6db7fa9e8d7ebb15` (`Implement experimental evolutionary selection`).
- Implementation commit contains only the authorized module, package export, and focused tests; this log remains separate and unpublished until the terminal log commit.
- Local state after implementation commit: detached `HEAD` at `6e1097bfb49801c6e89fc54d6db7fa9e8d7ebb15`, one commit ahead of fetched `origin/main`; only this new log is untracked.
