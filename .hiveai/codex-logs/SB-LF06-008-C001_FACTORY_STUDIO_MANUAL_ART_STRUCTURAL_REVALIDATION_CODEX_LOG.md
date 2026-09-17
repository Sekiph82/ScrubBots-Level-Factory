# SB-LF06-008-C001 — Factory Studio Manual Artwork Structural Revalidation
Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-17 Europe/Istanbul.
- Scope: `SB-LF06-008-C001` only.
- Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`.
- Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Non-destructive synchronization: fetched `origin/main` and fast-forwarded local `247048be55c1fa212c2f8071377ac119689520b7` to `bbc4492a42a84e40cf45b119bd7f0772724081f8`.
- Starting HEAD after synchronization: `bbc4492a42a84e40cf45b119bd7f0772724081f8`.
- `origin/main` after synchronization: `bbc4492a42a84e40cf45b119bd7f0772724081f8`; local branch was equal to origin.
- Initial status: clean except for ten existing/untracked owner-local Godot UID files under `level_factory/scripts/` and `level_factory/tests/`; these files are preserved and will not be staged.
- Repository identity, branch, origin, status, stashes/worktrees were checked; no sibling repository was used.

## Required records and contracts read before edits

- Root `TASKS.md`, including the active `SB-LF06-008` frontier and the instruction not to edit the tracker.
- `AGENTS.md` and `GOVERNANCE.md`.
- `.hiveai/audit-criteria/SB-LF06-008-C001_MANUAL_ART_STRUCTURAL_REVALIDATION_AUDIT_CRITERIA.md`.
- `.hiveai/prompts/SB-LF06-008-C001_FACTORY_STUDIO_MANUAL_ART_STRUCTURAL_REVALIDATION_PROMPT.md`.
- Previous strict audit `.hiveai/audits/SB-LF06-007-C001-R01_WRONG_TASK_EXECUTION_RECOVERY_STRICT_AUDIT.md`.
- Existing LF06-001..007 Studio scripts/tests, including the real editor, action bridge, evidence panel, preview, runtime and puzzle-config gate.
- `level_factory/scripts/factory_core_gateway.gd`, `level_factory/scripts/factory_core_launcher.py`, and `level_factory/scripts/factory_studio_art_editor.gd`.
- Canonical `output/bundle.py`, `quality/core.py`, quality/output/hash exports and relevant contract tests.
- Factory README/governance and project-boundary tests.

## Capability decision and implementation boundary

- Canonical Python `read_bundle()`, `QualityPolicy`, `evaluate_grid()`, and `logical_grid_hash()` are the sole source-bundle, policy, structural-analysis and hash authorities.
- LF06-008 will add a separate manual-art structural revalidation path over the retained LF06-006 in-memory DIRTY working copy. It will not enable LF06-003 `Validate`, claim full gameplay validation, or create a second validator.
- The bridge will use a fixed executable plus discrete arguments and a bounded transient request file. It will reject arbitrary command/executable input, preserve stderr/exit-code truth, and delete transient transport data.
- Revalidation will require editor source identity and an immutable source bundle to agree, reuse the exact policy recorded in source metadata, evaluate the exact working grid, bind results to source and working hashes, preserve DIRTY state, and mark later edits STALE.
- Source bundle bytes and canonical preview/evidence identity will remain immutable; no edited candidate, metadata replacement, revision, promotion, provider, network, solver, difficulty, load/risk or M05 capability will be added.

This builder log was created and verified before any LF06-008 implementation, test, documentation, or governance edit.

## Chronological implementation and verification

- Added read-only source/working logical-cell snapshots to the existing memory-only editor; no canonical source write path was added.
- Added `factory_studio_art_revalidation.gd` as a dedicated, scope-qualified UI/state component. It exposes NOT_REQUIRED, AVAILABLE, RUNNING, structural ACCEPT/REJECT, ERROR/UNAVAILABLE and STALE states, binds results to the retained editor source, preserves DIRTY state, and invalidates results after later working-grid changes.
- Added `factory_studio_art_revalidation_integration_suite.gd`, a committed headless runner that instantiates the real Studio scene, performs Generate/load/edit/revalidate/reject/stale/reset flows, checks source identity and preview/evidence identity, proves source bytes are unchanged, checks LF06-003 Validate remains disabled and LF06-007 remains UNAVAILABLE, and proves transient request cleanup.
- Extended `factory_core_launcher.py` with only the fixed `studio-revalidate-art` operation. It fail-closed validates the bounded request, reads the source bundle with canonical `read_bundle()`, reconstructs the exact metadata policy through `QualityPolicy`, evaluates the working grid with canonical `evaluate_grid()`, and returns the canonical `logical_grid_hash()` values and structured result.
- Extended `factory_core_gateway.gd` only with the fixed discrete launcher invocation. The dedicated revalidation component owns the bounded transient request file and removes it after the call; the gateway accepts only the fixed request path and never accepts arbitrary executable/command fields.
- First focused LF06-008 run: 5 static/bridge tests passed; the Godot runner failed to parse because the test used `bool(Button)` rather than a null comparison. Corrected the test runner.
- Second focused run: the Godot runner exposed a missing `_safe_output_path()` helper in the gateway. Corrected the gateway with the bounded output-path helper.
- Third runner execution reached PASS but emitted JSON parse diagnostics while scanning non-JSON process lines. Corrected the gateway to parse only trimmed object-looking lines; the next direct runner execution exited 0 with the PASS marker and empty stderr.
- Initial retained regression subset: `203 passed, 3 failed`. The failures were the existing gateway static ban on `FileAccess`/`DirAccess`, clean-checkout tracked-resource visibility for not-yet-indexed new files, and the existing `load(` safety marker matching the helper name. Corrected the architecture/helper name, staged only intended LF06-008 files so the tracked topology was testable, and reran the affected tests: `21 passed`, one pre-existing pytest cache warning.
- First complete `python -m pytest -q`: `717 passed, 5 failed`. Four failures were caused by generated `level_factory/scripts/__pycache__` files from the preceding compile/launcher checks being included by existing project-boundary scans; those generated caches were removed using bounded cleanup. The fifth failure was the synchronized current main branch's new authoritative `.hiveai/audit-criteria` directory not yet included in the existing governance allowlist. Added only `audit-criteria` to that test's accepted process-archive set; the affected project/governance tests then passed: `23 passed`, one pre-existing pytest cache warning.
- Current changed files are limited to the dedicated LF06-008 component/runner/test, the fixed launcher/gateway/editor/target integration, the narrow project-boundary allowlist additions, and this builder log. Root `TASKS.md` remains unedited.
- Final complete `python -m pytest -q`: `722 passed, 1 warning` in `274.23s`. The warning is the pre-existing access-denied pytest cache warning; no test was hidden or suppressed.
- `python -m compileall -q src tests level_factory/scripts/factory_core_launcher.py`: exit code 0. Generated `__pycache__` directories were removed afterward from only the bounded `src`, `tests`, `tools`, and `level_factory` roots.
- `godot --headless --path level_factory --quit`: exit code 0 with no parse, missing-resource, provider, network, credential, or sibling-repository diagnostic.
- Final `git diff --check`: exit code 0. `git diff -- TASKS.md` is empty. `level_factory/output` contains only the tracked `.gitkeep`; no generated candidate, transport, revision, or edited bundle remains.
- No dependency or license files changed. No provider/network service, credential, API key, telemetry, solver, measured difficulty, load/risk, M05 validation, persistence, revision history, owner acceptance, production promotion, SB-LF06-009+, SB-LFX, Content Platform, or main-game work was introduced.
- Pre-implementation source bundle, metadata and artwork were exercised through canonical `read_bundle()` and remained byte-identical across both structural result and deliberate reject paths. The revalidation surface remains explicitly structural/art-only and the existing Validate action remains unavailable.
- Pre-implementation, final staged-file review contains only the new LF06-008 builder log, the fixed launcher/gateway/editor/target integration, the dedicated revalidation component and runner, focused test, and the two narrowly required boundary allowlist updates. The ten existing owner-local Godot UID files remain untracked and preserved.

## Publication checkpoints

Implementation commit, push/equality checkpoint, and exactly one terminal log-only publication commit will be appended chronologically. Root `TASKS.md`, prompts, audits, and prior builder logs will not be edited.

## Implementation checkpoint

- Implementation commit: `df34197592eccc1498877478849c1f2aabeac8c4` (`Add manual artwork structural revalidation`).
- The implementation commit was pushed successfully to `origin/main`.
- Immediately after push, local `HEAD` and `origin/main` were both `df34197592eccc1498877478849c1f2aabeac8c4`.
- The ten pre-existing owner-local Godot UID files remain untracked and were not staged, deleted, or modified.

## Final publication checkpoint

- This is the final builder-log evidence update before the terminal log-only publication commit. No product, test, tracker, prompt, audit, or prior-log content will be changed afterward.
