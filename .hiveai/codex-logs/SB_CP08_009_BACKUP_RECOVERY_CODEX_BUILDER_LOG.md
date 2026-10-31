# SB-CP08-009 — Disaster Recovery from Backups

Document role: CODEX BUILDER LOG

## Start and authority

- Started: 2026-10-31 UTC.
- Canonical Desktop root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; repository `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; execution branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting `HEAD == origin/main == 297c2e5a96864e9b2010cc5697dd4f56cc9f7fb1`, 0 ahead / 0 behind. Read-only queue guard selected existing `SB-CP08-009`; owner prompt blob `3cafdbd2168ff4cbdea1d7ceed2b91f11d08a648`.
- Read root `TASKS.md`, repository builder instructions and the autonomous backlog contract. Existing backup helpers are in `content_pipeline/src/scrubbots_content_pipeline/operations.py`; existing test is `tests/unit/test_sb_cp08_operations_evidence.py`.
- Confirmed prior in-memory export/restore roundtrip and payload-tamper/path-escape coverage already exists. New narrow question: does restore enforce a strict JSON integer type for `schema_version`, rather than accepting boolean `true` through Python's `True == 1` equality?
- Scope is only bounded in-memory validation and a regression test. No filesystem restoration, provider reads/writes, R2/Production, CI/Actions, GUI, Release Apply, owner data, original PNG/Pool, game repository, clone/worktree or TEMP path operation.

## Planned implementation

- Add a synthetic integrity-valid recovery bundle with `schema_version: true` and assert rejection.
- If reproduced, require the schema version to be exactly an integer `1`, without changing valid version-1 bundle output or restore behavior.
- Run only the changed focused in-memory test(s) with Python bytecode/pytest caches and tmpdir plugin disabled; record live restore and clean-machine gates as NOT_RUN.

## Implementation and verification

- Before the source fix, the new in-memory regression failed as intended: `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py::test_backup_restore_rejects_boolean_schema_version_even_with_valid_bundle_hash` -> 1 failed because `restore_recovery_bundle` accepted `schema_version: true` after the synthetic bundle digest was recomputed. No filesystem/temp fixture was used.
- Narrow source fix: recovery restore now requires `type(schema_version) is int` and value `1`; valid version-1 exports and all later object/hash checks are unchanged.
- Added the negative in-memory regression using a synthetic export whose bundle hash is valid for the boolean schema field.
- Corrected focused command: `python -B -m pytest -p no:cacheprovider -p no:tmpdir -q tests/unit/test_sb_cp08_operations_evidence.py::test_backup_export_verifies_all_bytes_before_returning_recovered_objects tests/unit/test_sb_cp08_operations_evidence.py::test_backup_restore_rejects_boolean_schema_version_even_with_valid_bundle_hash` -> **2 passed in 0.26s**.
- `git diff --check` passed. No provider, filesystem restore, remote R2, Staging/Production, CI/Actions, GUI, Release Apply, game repository, owner data, original PNG/Pool or external deployment was accessed or modified.
- **NOT RUN:** clean-machine disaster recovery, restoration of actual provider/Production backups, or operational failover. This evidence is bounded builder-level in-memory validation and does not prove backup authenticity or a live restore.
- Files changed: `content_pipeline/src/scrubbots_content_pipeline/operations.py` and `tests/unit/test_sb_cp08_operations_evidence.py`. No dependencies or schemas were changed; no generated cache/scratch was created.
- The initial failing test attempt is retained above as truthful RED evidence; it was followed by the strict type fix and 2/2 passing targeted checks.
