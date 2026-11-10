# CLAUDE builder log — P0 recovery 2026-11-10

Document role: CLAUDE BUILDER EVIDENCE (append-only; self-review, not an independent audit)
Active contract: `.hiveai/prompts/SB_LFX_OWNER_CLAUDE_AUTONOMOUS_RECOVERY_PIXEL_ART_BATCH_MISMATCH_20261110.md`

## Starting state
- Desktop checkout fast-forwarded to `origin/main` 6f8a8708 (0/0). Codex's uncommitted 2026-11-09 LF/RP consolidation diff (7 tracked files) preserved unstaged; only CLAUDE hunks are staged per commit.
- Desktop LNK `ScrubBots Factory Studio.lnk` → `Godot_v4.7.2-stable_win64.exe --path "<repo>\Release\ScrubBots Factory Studio\level_factory"`.
- Installed parity: Release `factory_studio_exact_ui.gd` predated `c3545185`/`631d76db`; all other Release `.gd`/`.py` equal source. Data root: GD `factory_data_paths.gd` and Python `factory_repository_root` both resolve upward to the Desktop checkout `data/`. The launcher also prepends the Desktop working-tree `src/` to `sys.path`, so installed Python == live working tree.

## P0-A Pixel Art first-row stop
- Evidence: `data/Level Factory/Workspace/Studio Extensions/pixellab-jobs/1794288845-1335910230.json` (+ digest claim). State `SOURCES_IMPORTED_NOT_READY`, PixelLab job `be9a6ab5-55b0-4ec2-883c-96c3847b0698`, atlas sha `ce56a644…`, 16 frames sliced (`slice_pixel_match` true), frame 07 `REJECTED [MINIMUM_ARTWORK]` (701 opaque px), `pass_count` 15, 15 sources imported. Final `LF-000305..LF-000320.png`, Grid `PX-ATLAS-000020.png`, transaction `pixellab-atlas-ce56a644….json` all written 2026-11-10 08:35.
- Root cause: `_poll_pixel_art_worker` treated a row as successful only when `pass_count == 16`; a billed, fully persisted atlas with one LF-intake-rejected frame was counted FAILED, the fail-fast policy stopped the batch, and the activity row printed the fallback `Provider returned no detailed reason.` because success-shaped results carry no `error`.
- Fix: `_pixellab_atlas_generated()` (atlas path + 16 frame statuses) defines row success; `_pixellab_result_detail()` reports `N/16 passed …; intake-rejected: 07 MINIMUM_ARTWORK`. Provider/transport errors still stop with no retry.
- Billing safety: read-only `_inspect_pixellab_batch` on `data/input/pixellab_diverse_atlas_prompts_250.csv` → row 1 `ALREADY_ATTEMPTED`, rows 2..249 `NEW`, Factory-recorded month usage 1/200. No paid request was sent by CLAUDE during diagnosis.
- Tests: `tests/unit/test_claude_p0a_pixellab_row_classification.py` — source contract (fails on prior HEAD) + real Godot 4.7.2 headless execution: `P0A_CHECK PASS Atlas generated; 16/16 frames saved; 15/16 passed Level Factory intake; intake-rejected: 07 MINIMUM_ARTWORK.`

## P0-B Level Factory
- Startup stall: `candidate_inbox()` → `_latest_review()` → `list_candidates()` per candidate re-validated all 125 bundles (O(n²)); old build still `Startup inventory: comparing…` after 8 min (`docs/evidence/claude-gui-20261110/05_before_lf_15min.png`). Fixed with a stat-keyed per-process row cache in `list_candidates()` and chain reuse in `candidate_inbox()`; inbox 6.2 s. Test `tests/unit/test_claude_candidate_inbox_linear.py`.
- Phantom FAILED issues: 9 synthetic `owner-upload-000…0001..0009` records (provider OWNER_UPLOAD, batch null, `batch item source path could not be resolved for Pending projection`, 2026-11-09T12:11Z) leaked from a unit test into the real Release Pool. 27 files moved to `data/Level Factory/Quarantine/claude-20261110-synthetic-test-release-pool-records/` with hash MANIFEST and rollback. `tests/conftest.py` now refuses real-checkout `owner_release_library.transition` writes (`tests/unit/test_claude_release_pool_write_guard.py`).
- After fix (installed app): `All (320) · FAILED (6) · REJECTED (2)`, `Batch 196 Pending · 116 READY …` (= 180 STOPPED-job rows + 16 new Final PNGs) — `11_after_lf_loaded.png`.
- `Batch mismatch` still reproduced after restore (`12_after_lf_batch_restore.png`); backend `find_loaded_png_batch` → `RESUMABLE_PENDING_SUBSET` (job `png-batch-464ea07d…`) and `png_batch_latest` → `MATCHED`, so the flag is set GD-side. Investigation continuing.

## Owner requests during session
- Removed LF `PixelLab Final · Auto` (`SelectArtwork`) button; widened LF Workspace controls to the full left column (`13_after_lf_layout.png`).
