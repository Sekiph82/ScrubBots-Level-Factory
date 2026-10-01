# MAINT-ZIP-CORE-V02-C001 — LEVEL FACTORY ONLY — Canonical ZIP Core Cutover

Document role: CODEX BUILDER LOG

## Start and governance

- Start date: 2026-10-01 (Europe/Istanbul client date).
- Repository: `Sekiph82/ScrubBots-Level-Factory`.
- Canonical local root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Active branch: `main`.
- Authoritative prompt: `.hiveai/prompts/MAINT-ZIP-CORE-V02-C001-LF_ONLY_CANONICAL_CUTOVER_PROMPT.md`.
- This log is created before product edits, tests, documentation edits, or governance edits, as required by the active prompt.
- Builder boundary: Level Factory only. The separate `Sekiph82/Scrubbots` repository and the superseded cross-repository prompt are out of scope.

## Synchronization preflight

- Initial local HEAD before preflight: `0ea2faafe3b5cce1b48bda31e430e2355dddf501`.
- Origin: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- `git fetch origin --prune`: success; `origin/main` advanced from `0ea2faafe3b5cce1b48bda31e430e2355dddf501` to `52462786254c2a24c52de9f46391870f7adf733a`.
- Initial divergence: local behind `origin/main` by 3 commits, with no tracked modifications.
- Existing owner material: 54 pre-existing untracked paths, including Godot `.uid` files and prior local folders; no incoming tracked-path collisions were found.
- Stashes and worktrees were inspected. Existing stashes and worktree records were preserved; no reset, rebase, stash, clean, force checkout, deletion, or sibling clone/worktree operation was performed.
- Safe reconciliation: `git merge --ff-only origin/main` succeeded.
- Synchronized HEAD after preflight: `52462786254c2a24c52de9f46391870f7adf733a`.
- Post-sync divergence: `0/0` against `origin/main`.
- Post-sync tracked status: clean; the same pre-existing untracked owner material remains untouched.

## Authorized source set read

- `AGENTS.md`.
- `GOVERNANCE.md`.
- Root `TASKS.md` as the sole current task-state authority; current status is `OWNER_V02_APPROVED / LF_ONLY_IMPLEMENT_THEN_AUDIT`.
- `.hiveai/prompts/MAINT-ZIP-CORE-V02-C001-LF_ONLY_CANONICAL_CUTOVER_PROMPT.md` from the authoritative GitHub URL.
- `.hiveai/audit-criteria/MAINT-ZIP-CORE-V02-C001-LF_ONLY_AUDIT_CRITERIA.md`.
- `docs/decisions/OWNER_PRIMARY_SUPPLY_PIPELINE_V02.md`.
- Prior supply-pipeline strict audit and retained historical contracts were read for authority boundaries; the superseded runtime-WON requirement is not implemented.

## Implementation

- No product implementation has started yet.
- Required locked behavior: owner ZIP parameters, ranking-only screening, real game solve/replay authority, official Difficulty V1, dynamic depth, uncapped batches, explicit 3/4/5 columns with default 3, preview depth 3, no requested difficulty, shared generated/uploaded artwork route, preserved transparency, automatic ACCEPT publish, and deterministic post-difficulty progression placement.

## Initial implementation and focused-test correction

- Added the shared ZIP contract for allowed column counts `3|4|5`, default `3`, visible preview depth `3`, and baseline five-slot generation.
- Generalized `GameRules`, `DifficultyModel`, `SolutionVerifier`, `SupplyOptimizer`, the Godot bridge request, export verification, and CLI/launcher supply arguments to use explicit `column_count`.
- Removed the requested-difficulty target override from the supply optimizer and `supply-optimize` CLI surface; the internal image-complexity/search-band heuristic remains the only generation-band selector.
- Added exact logical-grid execution through `SupplyOptimizer.run_grid()` so canonical bundles can enter the ZIP route without an image round-trip.
- First focused collection command: `python -m pytest -q tests/integration/test_maint_supply_pipeline_v01.py tests/unit/test_sb_lfx_005_pipeline.py tests/unit/test_sb_lfx_010_readiness.py`.
- Failed correction: test collection raised `RuntimeError: constant COLUMN_COUNT not found` because the current game source uses typed GDScript declarations (`const COLUMN_COUNT: int = 3`); `_gd_const()` was corrected to accept both typed `=` and untyped `:=` declarations.
- `python -m compileall -q src level_factory/scripts`: passed before the focused collection correction.

## Verification and publication ledger

- Tests run: none yet.
- Files changed: this builder log only at this point.
- Product files changed: none yet.
- Root `TASKS.md`: not modified.
- `.hiveai/audits/**`: not modified.
- Dependency/license changes: none.
- Network/provider/runtime-boundary changes: none.
- Security/safety observations: no secrets recorded; offline-only core-generation boundary remains in force.

## Final handoff

- This log will be appended chronologically during implementation, tests, commits, and publication.
- Builder evidence will remain distinct from independent ChatGPT audit and will not declare audit acceptance.

## Continued implementation evidence

- The rerun after the first correction collected successfully but failed five integration cases because the current game loader is already range-based (`MIN_COLUMNS`/`MAX_COLUMNS`) and the local bridge still referenced removed `SupplyPlanLoader.COLUMN_COUNT` members.
- Corrected the Level Factory-side authority reader to accept the current dynamic game range and corrected the bridge to use its own validated 3..5 request contract, without editing the separate game checkout.
- Focused rerun passed: `14 passed, 1 skipped` in `120.94s`; the skip is the existing opt-in `SCRUBBOTS_SLOW=1` case. Pytest emitted one pre-existing cache-permission warning for `.pytest_cache`; no product failure.
- Added the shared Studio canonical-artwork route: exact OWNER_UPLOAD grids and generated candidate bundle cells map directly to compact palette indices and execute through the same `SupplyOptimizer.run_grid()` / real-game solve-replay / official Difficulty V1 / export path.
- Added ACCEPT-only automatic isolated publication and deterministic progression ordering by official difficulty score, then immutable level ID. REJECT is explicitly not published; ACCEPT without a READY ZIP run remains not published.
- Removed requested difficulty from new Studio draft/preset settings and replaced owner-facing M03/M04 pending copy with truthful canonical ZIP/official Difficulty V1 availability language. Historical generator contracts remain compatibility-only.
- Added LF-only regression coverage for 3/4/5 columns, target-option removal, difficulty-free new presets, and progression tie-breaking.
- `python -m compileall -q src level_factory/scripts`: passed.
- `godot --headless --path level_factory --quit`: passed. The pre-existing Studio runtime suite still asserts the retired Difficulty control and therefore exits before its old PASS marker; this is a stale legacy test expectation, not a product parse error.
- CLI dynamic-column verification: `supply-optimize` with `--column-count 4` and `--column-count 5` both returned `READY`, `SOLVED`, `WIN`, official Difficulty V1 evidence, and conservation checks with selected-column validation true. Output was isolated under `%TEMP%`.
- New/related focused suite passed: `15 passed` covering the LF-only contract plus review/comparison/readiness/preset compatibility tests; one pre-existing `.pytest_cache` permission warning remained.
- Export verification command on the 4-column plan returned `READY`, real solver `SOLVED`, replay `WIN`, official Difficulty V1 `ok: true`, and all conservation/selected-column checks true.
- Full suite command: `python -m pytest -q` completed `1117 passed, 3 skipped, 15 failed` in `459.48s`. The failures are the old Studio/runtime/static tests that require the removed owner-facing Difficulty control or retired M03/M04 wording, the owner-controlled current-task parser mismatch already present in synchronized TASKS state, and stateful legacy source/pipeline expectations. Root `TASKS.md` and legacy tests were not rewritten to conceal these superseded expectations.
- Added the explicit Studio ZIP column selector with exactly 3/4/5 choices and preview depth fixed at 3; source, candidate, and primary-image Studio requests now carry the selected column count.
- Post-change smoke: `godot --headless --path level_factory --quit`, `python -m compileall -q src level_factory/scripts`, and the LF-only/review/preset focused suite passed (`15 passed`, one pre-existing cache-permission warning).
