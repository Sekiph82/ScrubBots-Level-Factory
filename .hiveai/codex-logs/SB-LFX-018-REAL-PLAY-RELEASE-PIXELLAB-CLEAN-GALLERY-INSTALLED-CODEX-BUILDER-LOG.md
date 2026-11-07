# SB-LFX OWNER GOAL | AUTONOMOUS OPEN-BACKLOG EXECUTION | 2026-10-31

Document role: CODEX BUILDER LOG

## Scope

Bring the installed Factory Studio Release up to the current published Level Factory / Release Pool solver, canonical FPS policy, PixelLab MCP atlas path, and Final-only gallery implementation; then open the installed application through its existing Desktop shortcut and inspect the owner-facing pages. No paid PixelLab generation is allowed. The owner initially prohibited access to both PixelLab PNG folders, then directly authorized their access on 2026-11-08. Final and Grid Files images may now be loaded for application use and inspection; the original image files must remain unchanged.

The ScrubBots game repository is read-only.

## Start record

- Starting timestamp: 2026-11-07.
- Factory root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Factory repo: `Sekiph82/ScrubBots-Level-Factory`, branch `codex/sb-lfx-018-r05-v13-cd-recovery-20261021`.
- Starting local HEAD and `origin/main`: `4b77bcc353a7b36ea936142c674178ec2d00efe5`, ahead/behind `0/0`.
- Task queue guard passed its exact prompt / task ledger authority checks and reports the existing legacy reset as externally blocked for the one missing source PNG, 20 `source.json` records, and eight OS-policy-blocked installed candidate directories. This task is the owner’s direct request to update and visually verify the installed application; it does not resolve or overwrite that separate cleanup state.
- Factory tracked worktree had no tracked changes. Existing untracked owner files remain untouched.
- Source implementation evidence already present in the current published tree: `real_play_gate.py` requires canonical v2 `WON_CANONICAL`; `release_pool.py` verifies exact canonical proof with `searched == false`; `studio_extensions.py` admits only current PixelLab Final sources and retains nonmatching imports as historical.
- ScrubBots game checkout was inspected read-only at HEAD `9f1ada33d59c21f93120326e252e70bfbf2a7c7c` (`Make real-play solver canonical at 60 Hz`). The relevant `tools/real_play_file.gd` and `scripts/gameplay/solver/real_play_driver.gd` have no working-tree changes. `RealPlayDriver` uses `ProductionGameplayHost`, fixed `1.0/60.0`, immediate five-slot fill, earliest-frame refill, bounded search, and exact fresh-host canonical verification.
- Installed Release at start contains the already updated PixelLab MCP `studio_extensions.py` and launcher, but has no `supply_pipeline/real_play_gate.py`; installed `release_pool.py`, `png_batch.py`, `factory_studio_exact_ui.gd`, and `factory_studio_pipeline.gd` differ from current source.
- A no-write import probe against the installed package successfully imports `studio_extensions`, `png_batch`, and `release_pool`, but importing `supply_pipeline.real_play_gate` fails because that module is absent. The real-play adapter also imports `studio_lifecycle.py`, which is absent. Current source/import inspection found `pipeline_activity.py` and several solver/backend modules stale in Release.
- The Desktop shortcut was previously confirmed to target the existing Release launcher. This turn will open it visibly only after the scoped install.
- Owner clarification received 2026-11-08: files in canonical `data/output/Pixellab/Final` may be loaded read-only into the app; do not load old PNGs except protected game levels that already exist in the game. This authorizes the current Final source scan/import and GUI gallery inspection, while the original Final bytes must remain unchanged. Grid Files remains unaccessed.
- Further owner clarification received 2026-11-08: the prior no-touch rule applied only as protection from the legacy cleanup. The owner now expressly permits access to both `Final` and `Grid Files`; this does not authorize deletion of current art or loading legacy art from other locations.

## Correction and install plan

The owner pointed to the already-published prior report and builder log. Correction: the canonical solver implementation and its game/Factory tests were already completed and published; this turn must not repeat that work or characterize the code as incomplete. The prior Factory solver/release commit is `24540ad3ba872c56faebc5308d4d4eba027a4069`; the game solver commit is `9f1ada33d59c21f93120326e252e70bfbf2a7c7c`. The new task is to bring the installed Release up to those existing source results and visually check the app.

The installed Release incorrectly derived the repository/data root from its own `Release/ScrubBots Factory Studio` path. That means its PixelLab Final scanner was not pointed at the canonical Desktop checkout. A bounded root resolver now walks ancestors for the checkout marker pair (`.git` and `TASKS.md`); `studio_extensions` and default owner-art path resolution share it. A no-write runtime probe confirms both the source module and installed Release module path resolve to the canonical Desktop root and that `Final` resolves to the owner-approved canonical directory.

The official scoped overlay will update exactly the current source versions of `scripts/launch_factory_studio.ps1`, `level_factory/scripts/factory_studio_exact_ui.gd`, `level_factory/scripts/factory_studio_pipeline.gd`, `src/scrubbots_pixel_factory/output/bundle.py`, `src/scrubbots_pixel_factory/png_batch.py`, `src/scrubbots_pixel_factory/pipeline_activity.py`, `src/scrubbots_pixel_factory/studio_extensions.py`, `src/scrubbots_pixel_factory/owner_art_storage.py`, `src/scrubbots_pixel_factory/owner_folder_batch.py`, `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py`, `src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py`, plus add the absent tracked `src/scrubbots_pixel_factory/supply_pipeline/real_play_gate.py` and `src/scrubbots_pixel_factory/studio_lifecycle.py` as new managed paths. This brings in the exact proof gate and its child-process lifecycle dependency, the READY/Pool gate, active Final-only gallery filtering, PixelLab MCP routing, and current visible page.

## Safety and verification boundary

Do not run any PixelLab/ALPIX generation action. The owner permits the app to load/display current `Final` and `Grid Files` images, but original image bytes are preserved. Do not load old Factory PNGs from any other location into the active Level Factory or Release Pool pages. No physical legacy-file deletion or ACL workaround is in scope. GUI inspection must be read-only and avoid all generation, solve/batch, retry, delete, release, or paid-provider controls. The game repository is read-only. Do not claim native solver runtime acceptance from source/test results alone.

## Focused verification already attempted

- `python -B -m pytest -q -p no:cacheprovider tests/unit/test_sb_studio_real_play_gate_081.py tests/unit/test_sb_lfx_018_r09_r02_r04_r03_batch_binding.py` — **43 passed, 1 failed**. The failure is `test_real_producer_shape_persists_owner_binding_before_immutable_write` at `_verify_column_artifacts(result, 3)`. The captured test output alone does not isolate which persisted-artifact/hash/identity predicate failed; no cause is claimed and no remediation is asserted. Both files use pytest `tmp_path`; no further temp-backed tests will be run in this task. This run created pytest temp output under `%LOCALAPPDATA%\Temp`; it is left untouched.
- The current source-level contract requires `WON_CANONICAL`/`canonical_60hz` result evidence, and the current game checkout’s file-mode/driver are clean at commit `9f1ada33d59c21f93120326e252e70bfbf2a7c7c`. No production level was solved and no solver runtime WIN is claimed.
- The first run of the installer/root static contract test had 12 pass and one assertion failure because the new test expected a standalone `return factory_repository_root()` expression, while the actual `owner_art_paths` uses `else factory_repository_root()`. Corrected the assertion. Retest: `python -B -m pytest -q -p no:cacheprovider tests/unit/test_scoped_overlay_manifest_drift_contract.py` — **13 passed** in 0.18s. No pytest temp paths are used by this static-only file.
- `ast.parse` over nine in-scope Python source files — **PASS**; PowerShell parser over `scripts/install_factory_studio_scoped_overlay.ps1` — **PASS**; `git diff --check` — **PASS**.
- No-write canonical root probe using both the source file path and installed Release `studio_extensions.py` path — **PASS**, both resolve to `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`; the resolved PixelLab source path is exactly canonical `data/output/Pixellab/Final`.

## 2026-11-08 continuation: canonical app data paths and owner prompt

The owner supplied the exact PixelLab CSV prompt to use: `Pixel art style: CLEANING ROBOT - assorted cute compact floor-cleaning designs.` The source CSV is `data/input/pixellab_diverse_atlas_prompts_250.csv`, SHA-256 `6d94a33b45e2fe8011f290ccd3fcc90bc3f011de997a1e5862aa498126e5ad41`, with 250 rows. Row 1 ID is `SB_ATLAS_0001` and its prompt matches exactly.

The current GUI task exposed another installed Release path error. `factory_studio_exact_ui.gd` resolved CSV, PixelLab/ALPIX/Owner Suggestions, and Palette V3 from `res://../data`, which points under `Release/ScrubBots Factory Studio/data` for the installed app. Added a fail-closed repository-root walk that requires both `.git` and `TASKS.md`, then routes these resources through the canonical repository `data` directory. Added a focused static contract check; no fallback Release data tree is accepted.

Verification: three direct focused UI/source checks passed; Godot 4.7.2 `--headless --editor --quit` parsed/opened the source project successfully; `git diff --check` passed. Commit `404f6bf3000ecca17c3c7ddbc54674bbb8999312` was pushed normally to `main`. A scoped-overlay preflight found no manifest drift; the official installer applied only `level_factory/scripts/factory_studio_exact_ui.gd`, state `COMMITTED`, installed SHA-256 `31f852de7570bc63d66f919481b32a87ddb30ec682a74f53844d65f415b1fadf`.

Read-only PixelLab CSV preflight against the durable local job ledger returned `READY`, `0` paid requests recorded for the current UTC month, and row 1 `NEW`. No PixelLab PNG was written or changed in this stage. The canonical folders currently contain 18 PNG atlases in `Grid Files` and 288 individual PNGs in `Final`; this task did not mutate either folder.

Scope correction: the earlier prohibition on paid PixelLab generation is superseded by the owner's direct chat authorization on 2026-11-08, allowing paid requests until one successful production, and the owner selected the first CSV prompt above. Computer Use initialization then returned: `Computer Use was stopped by the user with the physical Escape key. Stop your work, do not call further Computer Use tools in this turn`. The LNK was therefore not launched in this continuation, no UI confirmation was submitted, and no paid provider request was sent. GUI startup, CSV picker runtime, atlas retrieval, slicing, and paid-success verification remain NOT RUN in this turn.
