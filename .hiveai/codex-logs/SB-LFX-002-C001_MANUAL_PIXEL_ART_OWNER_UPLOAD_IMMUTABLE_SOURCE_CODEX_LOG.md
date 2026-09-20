# SB-LFX-002-C001 — Manual Pixel Art OWNER_UPLOAD Immutable Source Import
Document role: CODEX BUILDER LOG

## Start and scope

- Starting timestamp: 2026-09-20 Europe/Istanbul.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical branch: `main`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Active task: `SB-LFX-002-C001` only.
- Scope: source-ingestion only for explicit local OWNER_UPLOAD input; no normalization, palette/structural validation, candidate creation, solver, difficulty, QA, owner acceptance, promotion, Source Art Library, batch import, provider, Content Platform, or main-game work.
- Root `TASKS.md` is read-only and remains the sole task ledger.

## Synchronization and initial state

- Verified repository identity, `origin`, branch `main`, and canonical mirror.
- Starting local HEAD before sync: `b5463a7a3627c7289272bf4616b914040f34ec4f`.
- Ran `git fetch origin main --prune`; remote `main` was four commits ahead.
- Fast-forwarded only with `git merge --ff-only origin/main` to `ccf4536700c9c62c1717ace05f543962e7d955f2`.
- Post-sync local `main` equals `origin/main`.
- Initial status contains only the ten pre-existing owner-local Godot UID files; they remain untracked, preserved, and outside this task:
  `level_factory/scripts/factory_core_gateway.gd.uid`, `factory_studio_art_editor.gd.uid`, `factory_studio_art_preview.gd.uid`, `factory_studio_evidence_panel.gd.uid`, `factory_studio_navigation.gd.uid`, `factory_studio_shell.gd.uid`, `factory_studio_target_controls.gd.uid`, `factory_studio_workspace_page.gd.uid`, `level_factory/tests/factory_studio_action_integration_suite.gd.uid`, and `factory_studio_runtime_suite.gd.uid`.
- Inspected existing stashes and worktrees without modifying them.

## Required reads

Read completely before implementation:

- root `TASKS.md`, confirming `SB-LFX-002-C001` is `READY_FOR_IMPLEMENTATION` and no tracker edit is authorized;
- `AGENTS.md` and `GOVERNANCE.md`;
- previous strict audit `.hiveai/audits/SB-LFX-001-C001_FACTORY_OPERATIONS_DASHBOARD_CANONICAL_DERIVED_VIEW_STRICT_AUDIT.md`;
- `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`;
- `.hiveai/audit-criteria/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_AUDIT_CRITERIA.md`;
- `.hiveai/prompts/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_PROMPT.md`;
- current Factory Studio Import navigation/workspace/gateway/shell and project scene;
- semantic normalization raw-artifact contracts, `SemanticRawArtifact.from_local_file()`, strict PNG decoder boundary, LEVEL_ART compiler, and locked `CELL_MAJORITY_V1` / `PALETTE_SNAP_V1` policies;
- output/export, generated-output governance, project-boundary, clean-checkout, and existing semantic normalization/LEVEL_ART tests.

## Initial implementation decisions

- Add a separate canonical owner-upload source contract rather than relabeling `LOCAL_FILE` provenance.
- Accept only the existing strict PNG profile and preserve exact selected bytes under `level_factory/output/owner-uploads/<owner-upload-sha256>/`.
- Verify existing content-addressed record and stored bytes before returning `ALREADY_IMPORTED`; divergent or corrupt destinations fail closed.
- Keep the source record explicitly `OWNER_UPLOAD`, `SOURCE_ONLY`, and `UNVALIDATED`; do not call normalization, palette snap, LEVEL_ART compilation, quality policy, or any downstream gate.
- Use a fixed shell-free launcher operation and a real Import surface with a FileDialog plus headless path setter.

## Chronology

Implementation, tests, regressions, offline/security checks, final diff, commits, pushes, and equality checkpoints will be appended chronologically below. No product or test edit occurred before this log was created.

## Implementation and focused verification chronology

- Added `src/scrubbots_pixel_factory/owner_upload.py` as a separate canonical source-ingestion contract. It derives `owner-upload-<sha256>`, stores exact `source.png` bytes plus canonical `source.json` under `level_factory/output/owner-uploads/`, verifies the record/bytes binding before `ALREADY_IMPORTED`, and fails closed for divergent or incomplete destinations.
- Reused only the existing strict PNG decoder boundary through a transient `SemanticRawArtifact.from_local_file()` decode. The transient legacy `LOCAL_FILE` provenance is never persisted or relabeled; the persisted record explicitly uses `OWNER_UPLOAD`, `SOURCE_ONLY`, and `UNVALIDATED`.
- Added the launcher `owner-upload` operation and the existing Gateway's shell-free `run_owner_import` bridge with stderr capture and structured result parsing. The selected local source path is passed as one bounded process argument; no shell, URL, provider, credential, normalization, palette, LEVEL_ART, QA, solver, difficulty, or promotion operation is invoked.
- Replaced only the inert Factory Studio Import surface with `FactoryStudioImport`: FileDialog-based local PNG selection, a headless/programmatic source-path setter, Import action, EMPTY/IMPORTING/IMPORTED/ALREADY_IMPORTED/ERROR states, source identity/provenance/hash/dimensions/path display, and the required source-only notice.
- Added the real Godot import integration. It creates two deterministic valid PNG fixtures outside the governed destination with the same display filename, imports both through the real scene/navigation/Gateway/Python boundary, verifies exact bytes and external immutability, proves same-byte idempotence, proves same-name different-byte identity separation, corrupts and restores an existing target record to prove fail-closed behavior, rejects a corrupt source without a trusted record, and cleans bounded artifacts.
- Added focused Python tests and extended the existing project-local Godot allowlist for the Import script and integration suite.
- Focused command: `python -m pytest -q tests/unit/test_sb_lfx_002_owner_upload.py -x` — 4 passed (one environment pytest-cache permission warning; no test failure).
- Syntax command: `python -m py_compile src/scrubbots_pixel_factory/owner_upload.py level_factory/scripts/factory_core_launcher.py` — passed.
- Real integration command: `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_import_integration_suite.gd` — exit code 0 and `SB-LFX-002-C001 OWNER_UPLOAD import integration PASS`.
- Post-integration output check confirmed the bounded `level_factory/output/owner-uploads` destination and temporary fixture root were cleaned.

## Regression and correction chronology

- First bounded regression command: `python -m pytest -q tests/unit/test_sb_lfx_002_owner_upload.py tests/unit/test_sb_lfx_001_factory_operations_dashboard.py tests/unit/test_sb_lf06_001_factory_studio_workspace.py tests/unit/test_sb_lf06_012_factory_studio_editor_smoke_and_headless_core_test_gate.py tests/unit/test_sb_lf00_002_project_boundaries.py tests/unit/test_sb_lf00_008_clean_checkout_contract.py -x` — 25 passed, then the project-boundary UTF-8 read failed on generated `level_factory/scripts/__pycache__` bytecode. Removed only that generated cache directory.
- The same bounded regression rerun reached the clean-checkout tracked-resource assertion and failed because the newly added Import script was not staged yet. Staged only the nine authorized task files; the ten owner-local UID files remained untracked and untouched.
- The next rerun found a legacy substring guard treating the new method name `run_owner_upload(` as forbidden `load(`. Renamed only the Godot-facing method to `run_owner_import` and updated its Import caller and focused contract assertion; the launcher operation remains `owner-upload`.
- Corrected bounded regression command rerun: `python -m pytest -q tests/unit/test_sb_lfx_002_owner_upload.py tests/unit/test_sb_lfx_001_factory_operations_dashboard.py tests/unit/test_sb_lf06_001_factory_studio_workspace.py tests/unit/test_sb_lf06_012_factory_studio_editor_smoke_and_headless_core_test_gate.py tests/unit/test_sb_lf00_002_project_boundaries.py tests/unit/test_sb_lf00_008_clean_checkout_contract.py -x` — 35 passed (one environment pytest-cache permission warning).
- Full regression command: `python -m pytest -q` — 742 passed (one environment pytest-cache permission warning), exit code 0.
- Compile and cache hygiene: `python -m compileall -q src level_factory/scripts/factory_core_launcher.py` — exit code 0; removed only generated `level_factory/scripts/__pycache__` afterward.
- Headless project boot: `godot_console.exe --headless --path level_factory --quit` — exit code 0.
- Re-ran the real integration after the Gateway method-name correction: `godot_console.exe --headless --path level_factory --script res://tests/factory_studio_import_integration_suite.gd` — exit code 0 with `SB-LFX-002-C001 OWNER_UPLOAD import integration PASS`. The test left only an empty generated `level_factory/output/owner-uploads` directory; verified it contained zero entries and removed that exact empty generated directory. No generated source or record contents remain.

## Offline, security, and dependency boundary

- No network/provider call, HTTP client, credential, API-key, token, telemetry, or runtime dependency was added. The owner-upload path accepts only a local filesystem path and uses no shell execution.
- No dependency or license files changed. Existing Python Factory Core remains authoritative; the nested Godot project contains only the launcher bridge, not a second compiler or Core implementation.
- Source bytes are written only to the content-addressed owner-upload destination; external selected files are read-only from this feature's perspective. Existing destination identity/bytes are verified before idempotent reuse; corruption and malformed input fail closed.
- No `TASKS.md`, prompt, audit, sibling repository, or owner-local UID file was modified.

## Implementation publication and terminal log checkpoint

- Final implementation diff was limited to the nine staged files listed in the implementation commit; `git diff --cached --check` passed and staged `TASKS.md` diff was empty.
- Implementation commit: `7e6ad79a5436b013e787509e9b2ab374ed90c78d` (`Implement OWNER_UPLOAD immutable source import`).
- Ran `git push origin main`; GitHub accepted `main` from `ccf4536700c9c62c1717ace05f543962e7d955f2` to `7e6ad79a5436b013e787509e9b2ab374ed90c78d`.
- Ran `git fetch origin main --prune`; local `HEAD` and `origin/main` both equal `7e6ad79a5436b013e787509e9b2ab374ed90c78d`.
- Final working-tree state after implementation publication contains only the ten pre-existing owner-local Godot UID files as untracked; they were preserved and are not part of this task.
- The remaining publication step is a separate terminal commit containing only this finalized builder log; no product or test file will be included in that checkpoint.
