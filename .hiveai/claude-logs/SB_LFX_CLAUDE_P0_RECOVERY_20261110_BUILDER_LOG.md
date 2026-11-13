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
- `Batch mismatch` root cause (diagnosed with temporary console prints, since removed): the GD `loaded-png-batch-find` request (196 Pending + 320 active IDs) was passed as base64 on the command line (~64 KB > Windows 32 767-char limit); the process failed to launch, the gateway returned `ERROR`, and `_apply_loaded_png_batch_find` maps any non-OK disposition to `Batch mismatch`. Backend on the same data returns `RESUMABLE_PENDING_SUBSET`/`MATCHED`. Fix: requests > 24 000 base64 chars are staged under `data/Level Factory/Runtime/studio-requests/` and passed with `--request-file` (deleted after). Test `tests/unit/test_claude_gateway_large_request.py` (real Godot headless; fails on prior gateway with b64=64024 ERROR). After deploy the installed app shows `Resume Batch · 180 remaining`, `Batch 79/260 · QUEUED` (`15_after_fix_lf_batch_resume_ready.png`).

## Owner requests during session
- Removed LF `PixelLab Final · Auto` (`SelectArtwork`) button; widened LF Workspace controls to the full left column (`13_after_lf_layout.png`).

## Commit f95a9cab (pushed)
P0-A classifier, inbox O(n²) fix, Release Pool write guard + quarantine, gateway request-file, LF button removal/layout, TASKS P0 evidence.

## Resume Batch did nothing → installed runtime parity defect (commit e2fd2936, pushed)
- Clicking `Resume Batch` appended `BATCH · RUNNING` but no `png-batch-run` worker appeared and the job file stayed untouched. Replaying the installed launcher gate read-only: `CANONICAL_FINAL_INVENTORY_UNAVAILABLE: too many values to unpack (expected 2)`.
- Cause: `scrubbots_pixel_factory` is a pip **editable** install pointing at the Desktop working tree, so the installed Studio executed Codex's uncommitted 2026-11-09 `studio_extensions` (3-tuple) against the committed launcher (2-tuple). Codex's own launcher had the same unpack bug; its test stub returned two values and masked it.
- Fix: launcher inserts the `src/` shipped beside it first (Release → deployed committed copy); data still resolves to the Desktop `data/`. Test `tests/unit/test_claude_launcher_bundled_src.py` (fails on prior launcher). Gate unpack fixed and stub updated.
- Adopted and committed Codex's uncommitted LF/RP work (owner plan items 4–6: retry bound to Release Pool FAILED/REJECTED record without Final membership; run gate on exact Pending; single verification during startup reconciliation). Its regression file: 68 passed with the fix; remaining failures are pre-existing ALPIX/archive-layout tests.
- Release deploy: every tracked file under `src/`, `level_factory/scripts`, `level_factory/scenes` that differed was replaced from HEAD (5 files, backups in `Release/.claude-deploy-backup-20261110/pre-e2fd2936/`); `Release/ScrubBots Factory Studio/.claude-deployed-commit` = e2fd2936.

## Test runs
- Focused new tests: all pass (p0a ×2 incl. Godot headless, candidate inbox, write guard, gateway large request (Godot headless), launcher bundled src).
- Related suites (studio/candidate/release_pool/review/inbox/batch selection, 388 tests): 297 passed, 90 failed, 1 skipped; failing files re-run with the write guard: 0 guard hits → failures are pre-existing stale tests (removed `_legacy_root`, ALPIX retirement, Pending/Release-Pool architecture changes). `factory_studio_runtime_suite.gd` (no timeout) hung >30 min against real data and was stopped — NOT_RUN_WITH_REASON.

## Further fixes found by running the real installed app (all pushed)
- 2043fb51: with bundled src active, `pinned_game_source.repository_root()`, the palette path (palette SHA binds PixelLab request digests), Imported record refs and Route A commit lookup derived data paths from their own file location (→ `Release\…\data`). First resume ended `PROJECTION_ERROR: pinned Difficulty V1 class authority is unavailable` ("ScrubBots project not found: …\Release\…\Runtime\…"). All four now use `factory_repository_root()`; test `test_installed_src_copy_reads_owner_data_from_canonical_checkout`.
- 18b98803: retryable `PROJECTION_ERROR` jobs were not discoverable after restart (resume caption/state lists and `find_resumable_pending_batch` omitted it) → orphaned job. Added; parametrized test fails on prior code.
- b41e66bb: removed dead `alpix_batch.py` + retired ALPIX tests (owner plan F1).
- 161ab0c0: `test_sb_lfx_018_r09_r02_r04_r01_run_output.py` wrote fake-solver output into real `data/Release Pool/Pending/Pipelines/Work/candidate-same-source` (2026-11-10 10:10, during the orphaned runtime-suite run) → quarantined to `data/Level Factory/Quarantine/claude-20261110-test-leak-pipeline-work-candidate-same-source/` with MANIFEST; test isolated; conftest now reports any owner-data change during a test session.
- db5e72b7: "Retry Failed / Rejected (N)" overflowed the 94 px button and overlapped Accept → "Retry (N)" / "Retry PNG" + tooltip.
- 9ae2dfd4: `release_entries()` verified the attested runtime once per entry (116×); now once per listing per column count. Listing ~70 s → ~11 s.
- Operational note: a `TaskStop` of a backgrounded pytest left its python + Godot runtime-suite children alive (10:12–10:22) running against real data; they were killed. The startup at 10:09 that reported "0 active PixelLab PNGs / BATCH OUTCOME RECONCILE ERROR" overlapped with that run; a clean restart reported 320 active, 0 errors. Owner Final/Grid files verified unchanged (no mtime after 08:40), Release Pool changes limited to the 16 legitimate new Pending entries.

## Installed GUI evidence (docs/evidence/claude-gui-20261110/)
- 01 Pixel Art after restart (activity is in-memory only; the owner's STOPPED_AFTER_FAILURE window had already been closed by the owner — the "before" failure state exists only in the owner's own screenshots).
- 03/04/05 old build: LF startup inventory still running after 1:30, 3:05, 8:04 (No Pending PNGs / 0 Final PNGs).
- 10/11 fixed build: Final 320/320 scanned in ~2 s; 320 PNG gallery, `Batch 196 Pending · 116 READY …`, issues All 320 / FAILED 6 / REJECTED 2 (phantom 9 gone).
- 12 `Batch mismatch` reproduced before the CLI-limit fix; 13 new Workspace layout (no PixelLab Final · Auto button); 15 after fix: `Resume Batch · 180 remaining`.
- 18 restored READY evidence of LF-000001 (Solver READY, Replay WON_CANONICAL, Difficulty MEDIUM, Pool IN_RELEASE_POOL — prior run, no re-solve).
- 19/20 real batch resumed: `Running 81/260`, live canonical pipeline on LF-000097 (SOURCE/PALETTE/CANDIDATE PASS, ANALYZE/PLAN 48/48 screening-solvable, SOLVE running).

## LF real solver result (installed app)
- LF-000097 (`owner-upload-…`, 4 columns, run `pipeline-710a80c04ac67f732b19aad0`, 07:31:56Z→07:38:13Z): SOURCE PASS, PALETTE/STRUCTURE PASS, CANDIDATE PASS, SOLVE PASS, REPLAY PASS (fresh host, 90 steps, divergedAt −1, solved), DIFFICULTY PASS (Difficulty V1 official analyzer, HARD 50.80), QA PASS; real play `WON_CANONICAL`, `canonical_60hz`, dt 1/60, `searched: false` → READY in `data/Release Pool/Ready`. Batch then PAUSED by explicit Pause-after-current (179 remaining). Screenshots 19–21.

## P0-A paid continuation (installed app, owner-authorized queue)
- CSV `data/input/pixellab_diverse_atlas_prompts_250.csv`: resume check skipped row 1 (`ALREADY_ATTEMPTED`), monthly 1/200; count set to 2 → "2 separate paid PixelLab Pro requests for CSV rows 2–3 … 20 credits" (screenshot 31).
- Row 2 (SB_ATLAS_0003 window-cleaning robots): PixelLab job `aa8c0040-daa2-4e0c-ae5b-bd73d260f2de`, 16/16 intake PASS, Grid `PX-ATLAS-000026.png`, Final `LF-000401..416`.
- Row 3 (SB_ATLAS_0004 mopping robots): job `51652192-ecf6-4dc3-9dee-cdd3211bb489`, 15/16 PASS (frame 07 MINIMUM_ARTWORK — the exact row-1 shape), Grid `PX-ATLAS-000027.png`, Final `LF-000417..432`; counted as success.
- UI: "Batch complete: 2 succeeded, 0 failed, 0 remaining. No automatic retry was attempted." (screenshot 34). Final now 352 = 320 + 32.

## Incidents caused during CLAUDE testing (truthful record)
1. `tests/unit/test_pixellab_pro_4x4_v02.py` IMPORTED_ATLAS fixtures exported 5 synthetic atlases (PX-ATLAS-000021..25) + 80 slices (LF-000321..400) + 5 transactions into the owner's real `data/output/Pixellab` at 10:39–10:45 (tests patched `launcher._repository_root` but not the owner-art root). Never imported or pooled. Moved to `data/Level Factory/Quarantine/claude-20261110-test-leak-pixellab-imported-atlases/` with MANIFEST/rollback; asset-name registry entries left so names are not reused; Final provenance scan afterwards: 352 PNGs, 351 ALREADY_IMPORTED + 1 ELIGIBLE (row-3 frame 07).
2. **Possible real paid PixelLab requests from tests.** Six pre-existing tests patch the retired `generate_pixellab_pro_4x4_frames` while the launcher calls `generate_pixellab_pro_4x4_atlas_mcp`, and fake "credentials configured". Once my sandbox fix let them run past setup, they could reach the real MCP endpoint with the stored token. Confirmed: the `-x` run at ≈10:58 returned 16 real frames (127 s) → ≥1 real generation. Probable additional ones during runs at ≈10:39–10:46 and ≈10:55. Their sandbox ledgers were temporary, so the exact count/billing cannot be proven locally — owner must check PixelLab account history. Upper bound estimate ≤ 8 atlases. Now impossible: conftest blocks every PixelLab `urlopen` in tests (suite 127 s → 7 s, 6 tests fail safely).
3. Between ≈09:58 and 10:09, ~300 `data/Level Factory/Imported` record folders disappeared during the first pytest run (exact deleter not identified; not the reset script, no test references it); my `library_refresh` at 10:11 rebuilt them byte-identically from Final (counts reconcile: 319 = 304 + 15 before; 336 = 320 + 16 after row 2). Owner-data watch now reports any change to Release Pool/Batches/Imported/Final/Grid during tests.
4. `Work/candidate-same-source` test leak (see above) quarantined.

## PixelLab gallery reconciliation and recovery (≈11:50–12:00, owner-approved spend)
- Read-only PixelLab MCP (`list_images`, `get_image`, `get_balance`; no create tool reachable): 20 Creator-gallery images dated 2026-11-10. Balance: 439/2000 generations used, resets 2026-11-20.
- In system at generation time: 3 (row 1 FLOOR SCRUBBER = PX-ATLAS-000020 / LF-000305…320; row 2 WINDOW CLEANING = 000026 / LF-000401…416; row 3 MOPPING = 000027 / LF-000417…432). Gallery-sheet SHA = stored atlas SHA for all three.
- Test-triggered: 17 (4 "offline source test", 13 "same paid intent", CREATURE style) — far more than my earlier ≤8 estimate. Their outputs went to deleted temp sandboxes, except 4 that tests had imported into real Final (which I had wrongly quarantined as "synthetic").
- Recovery: each signed 224×224 gallery sheet downloaded with the app's `_mcp_gallery_sheet_url`/`_download_mcp_gallery_sheet` and imported through the canonical `_semantic_import_pixellab_pro_4x4` → Grid + 16 Final slices + transaction + Imported sources. 17/17 imported: PX-ATLAS-000021, 023, 024, 025 (byte-identical to the quarantined copies, same names) and 000028…000040; Final LF-000321…336, 353…400, 433…640. 271/272 frames passed LF intake (86d0380f frame 13 USED_COLOR_COUNT, kept in Final). Final total 624, Grid Files 39. Report: `data/output/Pixellab/Generation Staging/gallery-recovery-20261110/recovery-report.json`.
- Only PX-ATLAS-000022 (8864c98a, 1086 bytes, not in gallery) is a genuine synthetic fixture and stays quarantined; correction note written beside the quarantine manifest.

## Legacy v1.3.6 uninstall
- Registry delete via tools was refused twice by the permission policy. Owner's Windows uninstall failed because the referenced `%LOCALAPPDATA%\ScrubBots Level Factory\Uninstall_ScrubBots_Level_Factory.ps1` no longer existed (terminal opened and closed). A minimal uninstaller was restored at that path: it removes only the HKCU `ScrubBotsLevelFactory` entry, the two Start Menu shortcuts and its own folder; the owner runs it from Programs and Features. Backup: `data/Level Factory/Quarantine/claude-20261110-legacy-install-v1.3.6-leftovers/ScrubBotsLevelFactory-uninstall-key.reg`.

## F3: Run must cover every Pending PNG (owner, 2026-11-10 ≈12:10)
- Owner observed the restored "Resume Batch · 179 remaining" ignored the newly added PixelLab PNGs. Commit d5902171: `find_resumable_pending_batch` offers Resume only when the saved job's unfinished rows cover every Pending PNG; otherwise the UI's existing "Run Pending Batch (N)" path builds one batch from all Pending (READY excluded) and `create_png_batch` marks older unfinished jobs whose remaining rows it fully covers as `SUPERSEDED` (finished rows/history kept; `run_png_batch` refuses them; `png_batch_latest` ignores them). Tests `tests/unit/test_claude_pending_batch_covers_new_pngs.py` (2 pass; both fail on prior code); batch suites unchanged (21 pre-existing failures before and after).
- Real data read-only: Pending 227 vs saved job 179 → discovery returns NO_MATCHING_COMPOSITE (Run all Pending). App restart registers the 272 recovered Final PNGs into Pending (~1/s).

## Run Pending Batch fixes and one-name rule (≈12:40–13:05)
- Owner: "Run Pending Batch (499)" did nothing. Installed launcher `pending-png-batch-create` → `Pending source identity changed before batch creation`: 31 records had matching SHA but different display names (row 1: Pending sprite-NN vs Imported LF-; row 2: Pending LF- vs Imported sprite-NN). ac943526: identity = SHA; rejected Run logged in Pipeline Activity ("BATCH NOT STARTED"); LF thumbnails fall back to Release Pool status (were SOURCE_ONLY).
- Owner: names must not change between folders. 4afee0be: startup sync aligns Imported copy/source.json and Pending records to the Final filename. Real data after one installed sync: 624 sources, 0 invalid, 0 sprite-names in Pending/Imported, 0 Final/Imported/Release Pool mismatches; installed `pending-png-batch-create` verifies 499/499.
- Test runs: new tests pass and fail on prior code; owner-upload/library suites show the same 3 pre-existing failures before/after; a hanging Godot import suite (uses legacy res://output/owner-uploads, not data/) was stopped.

## 2026-11-10 ~16:00–17:00 — P0-H PixelLab network drop, recovery, install (CLAUDE)

Owner report: last 10–15 PixelLab rows showed errors; batch stopped after the first error, re-run stopped again. App closed by owner before deploy.

Evidence (job ledger `data/Level Factory/Workspace/Studio Extensions/pixellab-jobs`, 47 records since baseline):
- 45 rows completed (44 `SOURCES_IMPORTED_NOT_READY`, 1 `FRAMES_REJECTED` op 1794313558: 16/16 frames `EDGE_CLIPPED`, art touches the 56x56 cell edge — intake rule, not a provider error).
- 2 rows `MCP_NETWORK_ERROR`: op 1794310665-5239981661 (job 27caa485-8f48-48f9-8b98-c45bce5a1af5, 17 MCP requests, 14:37:45→14:39:59) and op 1794314047-8621544354 (job 5d43bbd4-76a8-4cbe-8352-c805d0b7d38b, 4 requests, 15:34:07→15:34:19). Both had a provider job ID ⇒ create_image_pro accepted. Read-only `get_image`: both `status: completed`, `asset_status: saved`, `charged: 10 generations`.
- Root cause: `_mcp_http_request` maps `URLError`/`TimeoutError` to `MCP_NETWORK_ERROR`; the poll loop re-raised on the first failed free `get_image`, so one dropped connection failed a paid row and stopped the batch. CLAUDE's own read-only gallery scan hit the same drop twice (retried OK) ⇒ transient provider/network side.
- Fix 51a371dc: transient read-only faults retried (≤8, MCP session reopened); `resume_job_id` polls without create; Run Batch inspection first runs `_recover_accepted_pixellab_jobs` (job ID present, no atlas, network/poll state, POLLING only if >15 min old) and the UI logs `PIXELLAB RECOVERY`.
- Recovery with the new code on real data (free reads only): 27caa485 → Grid PX-ATLAS-000086, 5d43bbd4 → PX-ATLAS-000087, 16/16 intake PASS each; records now `SOURCES_IMPORTED_NOT_READY` with `recovered_from_state`.
- Gallery audit (list_images 163 items; 86 are 56x56 4x4 sheets; sheets downloaded to `data/output/Pixellab/Generation Staging/gallery-recovery-20261110/`): 66 already transacted; 2 = the rows above (now recovered); 8 older (2026-10-27, 11-05, 11-06) byte-identical in Grid Files PX-ATLAS-000003/004/007/008/011/012/014/018; 10 of 2026-11-07 (CREATURE ×9, CLEANING BUCKET) have 13–16/16 cells pixel-identical to existing Final singles — not re-imported (would duplicate PNGs). Note: the first gallery check run overwrote `recovery-report.json` from the earlier 17-atlas recovery; later reports are timestamped.
- Name check (`docs/evidence/claude-name-check-20261110/check_names.py`): 47 new jobs, 752 new Final PNG, 0 duplicate names, 0 `sprite-*` names, 0 Imported/Final name mismatches; only open item was Release Pool sync of new PNGs, run by CLAUDE with the app closed.
- Tests: new 3 + 2 pass (the 3 retry tests fail on 2bd5cffb source); MCP transport 12 pass; Godot UI 10 pass; `test_pixellab_pro_4x4_v02.py` 16 failed both on clean HEAD worktree and after the change (pre-existing P0-G item).
- Install: Release files `factory_core_launcher.py`, `factory_studio_exact_ui.gd` (also carries startup gate 2bd5cffb), `studio_extensions.py` replaced (content == HEAD 51a371dc ignoring CRLF); backups in CLAUDE scratchpad `release-backup-51a371dc`; `.claude-deployed-commit` = 51a371dc. LNK unchanged.
- Release Pool sync (`_sync_current_pixellab_final_sources`, app closed): 1376 active Final sources, 0 invalid, 15 min 54 s wall time (F7 slowness confirmed). Pending PNG 499 → 1251 (= 499 + 752). Name check re-run: 47 jobs, 752 new Final PNG, rows_with_issues 0, duplicates 0, sprite names 0. Installed GUI not relaunched by CLAUDE (owner to open the LNK); startup gate and `PIXELLAB RECOVERY` log line are verified by Godot headless tests only.

## 2026-11-10 ~18:40 → 11-11 ~02:30 — P0-I unit-suite triage, owner-data incident, test isolation (CLAUDE)

Full unit run (`tests/unit`, 18:43→22:05) stalled 3 h 12 min on `factory_studio_import_integration_suite.gd` (headless Godot, no timeout; also hangs on clean HEAD). Result after kill: 148 failed / 1903 passed. Baseline with HEAD `src` against the real data root: 141 of the 143 failing ids also fail → pre-existing; the 2 regressions were mine (`os` shadowed by a local `import os` in `_studio_extension_main` → every studio-extension op errored; fixed) and one that passed again after re-run.

Owner-data incident (found during triage):
- `data/Level Factory/Imported` was empty (dir mtime 22:39, during the baseline run). Cause: `tests/unit/test_sb_lfx_014_batch_import.py` imported into the real store and its `finally` unlinked **every** `owner-upload-*` folder under the real `owner_upload_root()` — the long-unexplained "deleter of ~300 Imported records".
- Restored additively with the app's own `import_owner_upload()` from PixelLab Final (`docs/evidence/claude-imported-restore-20261110/`): 0 → 1376 records, 0 byte mismatches, every Release Pool record (1251 PENDING / 117 READY / 6 FAILED / 2 REJECTED, unchanged) has its Imported record. Name check: 0 issues.
- 84 synthetic `same.png` batch-import ledgers written by unisolated tests into `data/Level Factory/Batches/Imports` were deleted on the owner's explicit instruction ("arşivlemene gerek yok … sil"), manifest first (`docs/evidence/claude-test-ledger-cleanup-20261110/`); 1007 real ledgers remain.
- `Studio Extensions/failures` is empty and `retries` absent: `test_sb_lfx_013_failures.py` deleted every JSON there on each run; not recoverable.
- Guard: `tests/conftest.py` audit hook fails any test that deletes, renames or writes under the real checkout's `data/`; regression `tests/unit/test_claude_owner_data_guard.py`. A guarded sweep reported 0 owner-data changes. Godot children of tests are not covered by this hook (separate process).
- Godot subprocesses started by tests without a timeout are now bounded to 900 s (conftest wrapper).

Product fixes found by the triage (each with a test that failed before):
- `operations.verify_content_health`: observed object keys (`../outside`, non-string) were validated only after a successful manifest parse; an invalid manifest skipped the check. Now validated first. Old code verified to return FAIL without raising.
- `scripts/codex/scrubbots_task_queue.py`: `git status --porcelain` output was `.strip()`ped, turning the first line's " M" into "M".
- `current_game_contract.py` (Factory Core) imported the content pipeline through a `sys.path` hack (boundary violation since 4368559e); the integration-layer adapter `scripts/cpx002_current_main_replay_adapter.py` now owns that path, core only loads the adapter.
- `factory_studio_exact_ui.gd`: compiled-in `C:/Users/sekip/...` defaults for the game checkout and Godot executable replaced by paths derived from the repository root / running Godot.
- `factory_studio_target_controls.gd`: generator modes lacked `ART_FIRST` (added to core 6364d1a5).
- `owner_upload_root()` cache (startup speed-up) re-checks reparse points every call; only path resolution is cached.

Stale tests updated to current, deliberate product contracts (each change commented in the test): canonical data layout (`data/Level Factory/...` since c0d940f5), original-filename storage, 900 s solver budget (c0d940f5), PixelLab-only Pixel Art (e48443c2), MCP transport (`generate_pixellab_pro_4x4_atlas_mcp`), Release-Pool-Pending-only job creation, semantic request schema v2 digests (45b19569), approved `factory_data_paths.gd` preload and staged-request `FileAccess` write (f95a9cab). Tests depending on the owner's 002/003/R09 evidence removed by the 2026-11-07 cleanup now skip with that reason (11 skips) instead of fabricating evidence. A fake-PID test could reach real `taskkill /PID 12345 /T /F`; termination is now stubbed there.

Results: non-Godot unit suite 1752 passed, 11 skipped, 7 failed → the 7 then fixed (solver budget contract) except `cp00_010`/secret-literal checks that only fail while TASKS.md/launcher are uncommitted. PixelLab v02: 47/47. NOT DONE: 22 GDScript integration suites still target legacy `res://output` and the real data root; they need an isolated project copy + path migration (next task). Startup re-measurement, arctic background import and Release deploy are still pending.

## 2026-11-12 — P0-J Godot integration suites isolated, cross-layer path/contract bugs fixed (CLAUDE)

Isolation: `tests/conftest.py` `build_isolated_factory_copy()` + `run_isolated_godot_suite` fixture copy `level_factory` (minus legacy `output/`), `src`, `scripts`, `content_pipeline`, `TASKS.md`, Palette V2/V3 and a `.git` marker into a pytest temp dir, so FactoryDataPaths/owner_art_storage resolve every mutable path to `<copy>/data`. All 12 pytest wrappers of headless Studio suites now use it. `level_factory/tests/factory_test_paths.gd` maps the suites' former `res://output/...` paths to the canonical layout and refuses (push_error + user:// redirect) when the repository root is the owner's real checkout. Owner `data/` + `level_factory/output` file listing (18,129 files, size+mtime) identical before/after every full run.

Product bugs found by the suites (each fixed; the failing suite is the regression):
- Studio Generate writes bundles to `data/output` (gateway's only approved area) but art preview, pixel editor, evidence panel, launcher revalidation and the candidate inbox accepted only `data/Level Factory/Workspace` (since c0d940f5): generated art could not be edited/revalidated and never reached review/pipeline. One rule: `FactoryDataPaths.is_studio_bundle_path()` (GD) and both roots in `_candidate_roots()`/`_run_studio_revalidation()` (Python); PixelLab art excluded.
- Release Pool readable artwork names collided for two different sources with the same basename (`a/same.png`, `b/same.png`): the whole batch import failed ("projection collides with an unverified status record") and a later move of one source could unlink the other's readable PNG. Second source now uses `<stem>--<id12>.png`; other sources' files are never claimed, verified or unlinked. Regression `tests/unit/test_claude_release_pool_same_name_sources.py` (failed before, passes after).
- `factory_studio_exact_ui.gd` destroyed live worker Threads when freed without a window-close request → Godot 0xC0000005. `_exit_tree()` now signals the cancel marker and joins the threads.
- Missing `data/output/Pixellab/Final` produced a raw `[WinError 3]` pipeline block; now an empty Final inventory (clear PIXELLAB_FINAL_ONLY result).
- Failure Inbox ignored the current pipeline's `UNAVAILABLE` stage disposition (only legacy `NOT_AVAILABLE`), hiding unavailable solver stages; now listed, non-retryable.
- Candidate pipelines silently ignored an explicit `interrupt_after` boundary (ZIP route ran to the end), so durable recovery could never resume; the boundary is honoured.
- Network imports were spread through `studio_extensions.py`; moved to `provider_http.py`, the only boundary allowed besides `offline.py`.
- Integration tests `test_sb_cp03_002`, `cpx_001`, `cpx_002`, `lfx_019`, `p3_headless`, `maint_supply_pipeline_v01` let the solver write job plans into the owner's real `data/Release Pool` (blocked by the conftest guard during this run; nothing written). Fixed by also isolating `owner_art_storage.factory_repository_root`.

Stale suite expectations updated to deliberate contracts (comment in each): original-filename Imported storage, `NOT_AVAILABLE` solver spelling (8bf28292), corrupt PNG = REJECTED (2483a3a0), newest-first activity rows (f3003d98), single 900 s solver budget, background_intent required / difficulty removed from presets, "No HOME" + ART_FIRST mode, Final-only (51–59 px) Level Factory input, Workspace/Reproductions, Runtime root `data/Level Factory/Runtime/<sha>`, `source_authority` preflight binding, CLAUDE actor message, earlier read_bundle rejection of forged candidate identity. Env-dependent integration tests now skip with a reason when `SCRUBBOTS_PROJECT` is unset (the implicit Desktop fallback is disabled by design).

Godot suites: final isolated run 29 PASS of 43 scripts (was 6 at the start of this pass); the 14 others are listed below. Not tests: `factory_studio_owner_visual_evidence_suite.gd` (screenshot tool, needs a display + env), `factory_studio_r09_r02_r04_r01_profile_derivation_suite.gd` (game-runtime helper; its preload exists only in the game project). Remaining 12 legacy UI suites (R04-R04, R04-R01, R04 responsive, R05-R05, R06, R07, R09-R02 activity/monitor, R09-R02-R04 R02/R03/R09/source-UI) target removed controls (`SelectArtwork` f95a9cab, `PipelineActivityText` 581003a5), the pre-Pending synchronous batch flow, or 002/003 owner evidence deleted 2026-11-07 — owner decision requested (retire vs rewrite).

Real game run (`SCRUBBOTS_PROJECT` = temp clean clone of Sekiph82/Scrubbots origin/main c58256c5, game repo untouched): remaining failures only these two; two cross-repo findings need an owner decision:
1. `AUDITED_VOID_COMMIT 7d0d148b…` (void_capability.py, pinned_game_source.py) and pinned runtime commit `aef60a61…` no longer exist in the game history (rewritten after 2026-10-08; VOID work is now f4c10170 / audit 0b6dfc35, no identical tree). VOID capability against current game main is permanently CLOSED (`AUDITED_VOID_ANCESTOR_MISSING`); the pinned runtime snapshot is unaffected.
2. `SupplyExporter` adds `source_sha256` to level JSON (7bf85b28) but the game Level Data Spec and content pipeline allow only 8 fields → `build_solver_proven_scrubpack` fails `UNKNOWN_PAYLOAD_FIELD` for every Factory READY level (owner's 117 READY levels carry the field, bound by SHA).

Full `pytest tests` (no SCRUBBOTS_PROJECT): 2254 passed, 45 skipped, 2 failed — both are "TASKS.md must equal HEAD" checks that pass once this entry is committed. Owner `data/` + `level_factory/output` unchanged (18,129-file size/mtime listing identical before/after).

## 2026-11-12 (later) — P0-J follow-up: 12 legacy Studio UI suites rewritten (owner chose "Rewrite") (CLAUDE)

Rewritten against the current product, keeping each suite's intent (commits 6ddf16e7, aea850e5 and this entry's commit):
- R09-R02 activity / R09-R02-R01 monitor: panel at Rect2(27,412,334,…) now filling the left workspace; title/state/source/phase/rows structure; hash-chained incremental JSONL stream, UTF-8 split, tamper fail-closed, slow worker; startup inventory + startup gate settled like the real reads; source-scoped results; per-row Details (stop reason in the Pipeline row tooltip); Run disabled only while a worker runs or nothing is Pending.
- R05-R05, R06, R09-R02-R04-R03: Pending-only snapshots ("pending-png-batch-create") bound to the pinned Runtime and the 900 s budget; saved-batch restore through the real background reader; RUNNING→INTERRUPTED, PAUSED, explicit Resume; verified retry lineage; nullable restore contract; mismatched jobs never resume.
- R04 responsive, R04-R01, R04-R04: region-based responsive geometry with the declared 1100×720 minimum (every master control inside 1100×720…2560×1440); single file = PixelLab Pro 4×4 import, multi-file intake statuses; sliding five-slot window; no per-source pipeline from Run.
- R07, R09-R02-R04 source UI / R02 inline / R09 activity scope: deleted owner 002/003 data replaced by committed PNG fixtures, canonical Imported records (PNG + source.json) and a hash-bound READY pipeline (`level_factory/tests/factory_test_ready_fixture.gd`) written inside the isolated copy; inline results panel; follow-the-queue hand-off to the next source.

Product fix found here: LEVEL FACTORY Details cut the solver state to 10 characters ("UNAVAILABL"); now 11 (the R09-R02-R01 suite checks it; seen failing first).

Godot: all 41 Studio suites pass in isolation (41/43 scripts; the 2 non-suites are the screenshot tool and the game-runtime profile helper). New `tests/integration/test_claude_studio_godot_suites.py` runs the 33 suites without a dedicated wrapper so they cannot silently drift again (only 8 of 41 had wrappers).

## 2026-11-12 (evening) — P0-K: real-app run, 200-cell rule, parallel PNG batch (CLAUDE)

Real installed app (owner present, Desktop LNK, Release = f58f5eec):
- Run Batch works but the click froze the UI ~8.5 min: `png-batch-create` runs on the main thread and re-validates all 1299 Pending sources (`_verify_sources`). Not fixed yet (async/cached plan creation is open).
- Batch LF-000099 reached READY in ~777 s: screening 50 plans ~25 s, solver Godot process 650 s, 1/60 replay + load check ~91 s, review ~11 s. The owner stopped the worker with Stop after current; job STOPPED cleanly (ready 1, rejected 23, remaining 1275).
- Bottom gallery stayed on LF-000001..005 while LF-000099 solved: the five-slot window was positioned with the Pending-batch index (1299 items), not the rendered gallery index (1424 Final PNGs). Fixed with `_gallery_window_start_for()`; regression suite seen failing first.
- 22 of 23 plan-time rejections were MINIMUM_ARTWORK (462..778 artwork cells < 25% of 3136). Owner decision: drop the ratio, keep >= 200 cells. Changed in studio_extensions, supply_optimizer, art_first router, transparent_negative_space, pixellab_pro_atlas (game-doc reporters void_capability/current_game_contract untouched). Commit 638d6208. LF-000397 (2 colours) stays rejected.

Solver timing (temp copy of the pinned runtime + one real plan, game repo untouched): analyze OFF wall 99 s (native solve 66 s); analyze ON wall 513 s (solve 73 s). The official Difficulty V1 analyzer costs ~414 s per level. The screening simulator matched the engine on the solver trace (`screening_diverged_steps = 0`).

Owner chose "Parallel batch first":
- `png_batch.run_png_batch` keeps up to `parallel_workers(settings)` canonical pipelines in flight (ThreadPoolExecutor; setting `parallel_workers`, env `SCRUBBOTS_FACTORY_BATCH_WORKERS`, default `cpu_count // 4` capped at 4, hard cap 8). Preparation, revalidation, reuse checks and every job-state/Release Pool projection write stay on the orchestrating thread. Per-item solver job dirs, run output dirs, activity streams and Release Pool entry files were already unique. Pause/Stop after current: no new item starts; running ones finish and are recorded. CANCEL_NOW: solvers abort through the existing control file; unfinished items stay RUNNING for `_recover_attempt`. `current_index` = lowest running item (gallery/Details follow it).
- Found while reviewing thread safety: `release_pool.release_entries` kept its per-listing pinned-rules cache in a module global; two overlapping listings left a stale dict installed forever. Now thread-local; regression `test_parallel_listings_do_not_leak_a_scope_into_later_calls` fails on the old code (`[{}] == [None]`).
- UI: Run button and activity header show `· N parallel` when more than one item is RUNNING (gallery suite asserts `Running 5/8 · 2 parallel`).
- Tests: `tests/unit/test_claude_parallel_png_batch.py` (peak concurrency = workers, Pause finishes in-flight and starts none, one worker crash fails only its item, worker bounds) — 8 of 9 fail on the old code. The old sequential pause test pins 1 worker. Existing batch suites: 81/81 with 1 worker.
- Real benchmark: 4 concurrent solver+analysis Godot processes on the same plan: 537–544 s each, total 544 s vs 513 s alone → ~3.8x throughput on 16 cores; all SOLVED, results identical to the single run except `elapsedMs` (another session's Godot perf tests ran at the same time).

## 2026-11-12 (night) — P0-K real-app verification of the parallel batch (CLAUDE)

Installed app (Release = 335705a6, Desktop LNK, owner watching):
- Retry (Release Pool FAILED/REJECTED, 31 PNGs) ran with 2-3 parallel workers; result 0 READY / 29 FAILED / 2 REJECTED.
  - 21 ratio PNGs: the GAME's `scripts/data/production_level_validator.gd:64` (ADR-030 D2) still enforces ">= 1/4 of the board" inside the solver bridge ("got 719 of 3136"). My earlier statement that the game did not enforce the ratio in code was WRONG; it is enforced in the game validator and in the pinned runtime copy. Owner asked for a handoff prompt: `.hiveai/prompts/SB_GAME_CLAUDE_D2_DROP_ARTWORK_RATIO_20261112.md` (game change + Factory runtime re-pin afterwards).
  - 8 previously FAILED PNGs: "immutable evidence already exists with different content" — regression from 638d6208: the persisted validation report changed only in `minimum_rule`, the evidence path did not. Fixed in f7874352 (non-legacy rule enters the path context; legacy files keep their paths); regression test fails on the old code.
  - Batch rows showed a bare "UNAVAILABLE"; now carry the solver reason (b2ce8cae).
- Run Pending Batch (1279): plan creation froze the UI ~6 min (19:28 → 19:34; open item). Then 4 items RUNNING at once ("Running 4/1275 · 4 parallel", gallery marks the active PNG). First 4 READY: LF-000102 (10.4 min), LF-000100 (12.4), LF-000104 (14.3), LF-000103 (16.1) — 4 levels in 16.5 min wall vs ~52 min sequential. Screenshots: `docs/evidence/claude-gui-20261112-parallel/` (owner-local, not committed).
- Profile of one Difficulty V1 measure (91 steps, temp runtime copy): 382 s = per-step decision states ~270 s (independent per step, parallelisable within one PNG) + 91 sequential placements ~74 s + peel ~35 s; score 2 ms.
- Not yet deployed (app running): b2ce8cae, f7874352.
- Stop after current (owner + Claude, 20:50): job png-batch-c3bbc2dc STOPPED with 20 READY / 0 FAILED in 83 min wall (19:34:44 → 20:57:37), ~4.2 min per level (~345/day) vs ~13 min sequential. Window close then showed "Not Responding" ~1 min before the process exited by itself (open item). Release deployed to 5a851fa3 (b2ce8cae, f7874352; backups in `Release/.claude-deploy-backup-20261112/pre-5a851fa3`); relaunched app loads.
- Game Claude reports `dd54007a` (ADR-030 D2 ratio dropped, 92/92 local suites). Re-pin is NOT a drop-in swap: `pinned_game_source.py` hard-codes `aef60a61` (absent from current game history), its tree/attestation/project digests, 232 files and the audited VOID ancestor `7d0d148b` (also absent). dd54007a vs the pinned runtime: 89 of the 230 shared runtime files changed (solver 67 lines, proof kernel 53, analyzer 8, challenge score model 10, target access 14, five-slot engine 2), 53 added, 2 removed. Re-pinning therefore changes solver/difficulty behaviour for new levels and needs an owner decision on the new VOID audit anchor; no change made.

## 2026-11-12 (late night) — P0-L: re-pin new solves to game main dd54007a (owner decision) (CLAUDE)

Owner: "Yes, re-pin to dd54007a" after the game Claude dropped the ADR-030 D2 ratio (dd54007a, 92/92 local game suites).
- Runtime built read-only from the local game clone (`scripts/build_pinned_game_runtime.py dd54007a 0b6dfc35`): `data/Level Factory/Runtime/dd54007abb59863bc753c1a029b9db227fb4f89f`, 283 files / 2,535,120 bytes, tree 38c3a7c9, attestation sha256 3d681351…; dd54007a is on game origin/main; VOID anchor 0b6dfc35 "audit(void): close SB-VOID-C001" (7d0d148b no longer exists). Old runtime folder untouched.
- `pinned_game_source.ATTESTED_RUNTIMES` registry (aef60a61 + dd54007a). New solves use dd54007a; Release Pool verification, historical profile supplements and class authority use `runtime_root_for_run(primary)` (the run's recorded git_head). Real data, read-only: 138/138 Release Pool entries still valid (all aef60a61). void_capability reports each runtime's own D2 rule; full-checkout ADR regex accepts the amended text. r09 campaign tooling stays on aef60a61. UI `_PINNED_GAME_COMMIT` = dd54007a.
- Same real plan (LF-000099 candidate, 56x56) solved with both runtimes: identical 91-step trace, identical Difficulty V1 (challengeScore 52.4495, B/S/U identical); 510 s.
- Tests: full unit 2051 passed / 4 failed before the test updates (old 232-file / aef assertions) → updated to the registry contract; new `test_claude_multi_runtime_repin.py`; three Godot suites with a hard-coded pin updated and PASS.
- Found: the STOPPED batch c3bbc2dc (1255 remaining) carries the aef60a61 runtime in its settings; Resume would have solved with the old rules. Resume now rebinds remaining items to the current pin (02460a66; regression fails on old code).
- Real app (Release = 38501acf): Retry 31 → job png-batch-f2a7c619 bound to dd54007a. LF-000056 (previously "immutable evidence" failure) READY in 17.5 min, authority dd54007a, score 50.90 HARD, Release Pool read-back verified. LF-000270 and LF-000397 rejected at planning (unchanged).
- Timeout investigation (owner: "Yes, investigate"):
  - LF-000047 solver TIMEOUT_900: native search SOLVED with visited=1912 (typical ~135) at ~899 s of the 900 s canonical budget, which also covers Godot start and Difficulty V1 analysis; killed before analysis. Genuinely hard level; changing the 900 s budget is an owner policy decision (not changed).
  - LF-000009 / LF-000037 real_play_v1 900 s timeouts: the solver-proven order (equals intendedColumnClicks, replay ok, divergedAt -1) deadlocks in real 60 Hz play at click 27 / 26 with all five slots WAITING and 0 active robots, then real-play `--search` exceeds 900 s. Reproduced in 11 s on a clean dd54007a clone after `--import` (no script errors) with the identical click/frame as on the Desktop checkout 9f1ada33, so it is a game proof-kernel vs production-host divergence, not a version or parallel-load effect. Hand-off prompt: `.hiveai/prompts/SB_GAME_CLAUDE_PROOF_KERNEL_REAL_PLAY_DIVERGENCE_20261112.md`.
  - Also found: real-play runs the owner's Desktop game checkout (HEAD 9f1ada33, 145 commits behind dd54007a, uncommitted project.godot/main.tscn edits) while the solver uses dd54007a. Not the cause here, but solver and real-play should use one game commit; needs an owner decision (update that checkout or give the Factory its own clean clone at the pin).

## 2026-11-13 (night) — P0-M: real-play alternatives, batch choice UI, overnight run (CLAUDE)

Owner chose option A from the game investigation (job 155): a level ships only if real 60 Hz play wins it with slots refilled at once; no game change. Desktop game checkout updated by the game Claude to main 26d15718 (owner's 4 uncommitted files kept); the solver stays on dd54007a.
- 1b958875: each quality-ranked plan is solved without the official analysis, pre-checked with one canonical real-play run (~11 s, no order search); only the first plan the game wins gets Difficulty V1 via a new bridge `analyze_trace` mode (verified identical to the full run, challengeScore 52.4495). At most 12 plans or 30 min per PNG; one solver timeout no longer ends the search.
  Real app retry (job 80ab5e4a): LF-000037 READY (plan 2 won after plan 1 deadlocked at click 26), LF-000009 READY (plan 6 won after deadlocks at clicks 47/51/19/12/49), LF-000093 READY (plan 2), LF-000088 FAILED REAL_PLAY_NO_WINNING_PLAN (5 plans). Final gates: WON_CANONICAL, searched=false.
- 2319fb86: PIXEL ART candidate cards (Button grew with long captions) and the activity table (never laid out responsively, fixed 334x924) overflowed in small windows; verified fixed in the installed app.
- 16ffd813: "Batch mismatch" locked Run: two 8 November jobs whose Pending rows were partly finished elsewhere were never superseded, making discovery ambiguous. Supersede now considers only still-Pending rows; ambiguity offers Run Pending Batch. Verified: the new batch superseded c3bbc2dc, c9edaac7, 279b7fef, b89087a9.
- 6338ac18: "Resume saved batch · k remaining" offered next to Run Pending Batch when a stopped job does not cover every Pending PNG; a running retry's progress is followed even when the gallery cannot re-derive it (screen stayed "Running 2/6 · QUEUED").
- 6e496795 / ec22a77b: default batch workers 6, then 8 (owner decision for the overnight run; i7-1260P 16 threads, 15.7 GB).
- Release = ec22a77b. Run Pending Batch (1256) started 00:58 on 2026-11-13 in the installed app (job png-batch-6cc4887a, dd54007a runtime, 8 workers); left running overnight by owner request.

## 2026-11-13 — Live Release status during a batch (Claude)

- Owner report: counter showed 180 R / 2 F while Release Pool held 208 READY / 6 FAILED; Batch Issues kept finished PNGs as "PENDING · Solver attempt started".
- Root cause: the owner Release Pool archive (source of the status counter and Batch Issues) was re-read only when the whole batch ended.
- Fix: `_apply_batch_progress_result` re-reads the archive whenever the batch finished total (ready+failed+rejected+skipped) changes; loaded flag kept, old view stays until the new read lands.
- Regression in `factory_studio_gallery_follows_active_source_suite.gd`; watched fail on unfixed code ("a PNG finished during the batch but the Release Pool was not re-read"), then PASS. Related Godot suites PASS (monitor, activity, pinned authority, pixel cards, r05 loaded batch, batch UI binding, batch CSV). Python UI tests 164 passed.
- 30-PNG measurement on installed c8c32430: 26 READY / 4 FAILED (PNG_TIME_LIMIT after a won plan), READY median 17.6 min, analysis median 594 s, 94/94 kernel replay SOLVED, 14.1 READY/h. Not yet installed: a9778a46, f08dcae1, this fix.

## 2026-11-13 — LEVEL FACTORY screen defects (Claude)

Seen in the installed app (d31ad0ab) during the running batch, all fixed in `factory_studio_exact_ui.gd`:
- Retry/Accept/Reject overlapped the Batch Issues heading and tabs: the Studio opens on PIXEL ART with these buttons hidden, so the panel kept its unscaled default top; `_show_screen` now lays the panel out again.
- Run button "61/1256", Details "56/1256", activity "Starting next verified PNG": one shared `N/total done` text (`_batch_progress_text`); with parallel workers (no current_index) the activity header names the followed PNG; P/R/F/X no longer repeated in the activity header (counter shows them).
- Preview Replay / Supply Plan opened "Results unavailable … SOURCE_RUN_MISMATCH" for a PNG without a READY result: now disabled with a tooltip.
- Owner request: Batch Issues lists the PNGs being solved first, in filename order, marked RUNNING (no duplicate Pending row); refreshed when the running set changes.
- Regressions in `factory_studio_gallery_follows_active_source_suite.gd`; all new checks watched fail against d31ad0ab, then PASS. 18 related Godot suites PASS; `profile_derivation` suite not run (missing game analyzer file in the isolated copy, unrelated). Python UI tests 164 passed.

## 2026-11-13 — Re-pin to game 6534537c (faster ProofKernel / Difficulty V1) (Claude)

- Game Claude job 156: `6534537c` "perf: verdict-only target access for ProofKernel + Difficulty V1 analyzer, identical-output regression" (game CI run 43393264103 passed; game Desktop at f60cfa94).
- Runtime built read-only with `scripts/build_pinned_game_runtime.py 6534537c 0b6dfc35 --apply`: 283 files, 2,540,029 bytes, tree 96a9806e, attestation sha256 1e41805d…, same VOID anchor 0b6dfc35. Registered in `ATTESTED_RUNTIMES`; dd54007a and aef60a61 stay attested for their existing runs.
- Also carries game 628ab240 (finished slot takes no pick until its pop ends), which real play already used since 26d15718.
- Real check on the new runtime (copies of LF-000147 / LF-000148 plans, `verify_exported_supply`, full native solve + official analysis): 35 s and 37 s; Difficulty V1 JSON byte-identical to the saved results (challengeScore 52.1888 / 43.8423).
- Tests: re-pin unit tests 10 passed / 4 skipped; pin-bound Godot suites (r05 loaded batch, pinned authority, batch UI binding, gallery follow) PASS.

## 2026-11-13 — First real batch measurement on runtime 6534537c (Claude)

- Installed 10e429df; owner approved resume 12:43 local. 21 PNGs finished 12:43–13:03: 21 READY / 0 FAILED.
- READY median 4.3 min (was 17.6 min on dd54007a); stages median: screening 58 s, official analysis 58 s (was 594 s), tail 57 s. 49/49 kernel replays SOLVED, 0 native searches.
- ~63 READY/h with 6 workers (was 14.1/h); CPU ~50 %, frequency ~71 %, free RAM 3.1–4.3 GB.

## 2026-11-13 15:15–15:45 local — batch stall at 211 READY; re-pin to game ec1e57a7

**Studio check.** Batch job `png-batch-6cc4887a…` stood at 211 READY / 5 FAILED / 6 RUNNING / 1034 QUEUED.
The job file was last written 14:47:01 and was 1,048,170 bytes. All six RUNNING PNGs (LF-000379..384)
logged "Backend pipeline completed with disposition READY" between 14:47:31 and 14:51:04, but the job never
recorded them. The Studio kept polling `batch-latest` until it closed at 15:14:38 (no error in godot.log).

**Root cause.** `png_batch.MAX_JOB_BYTES = 1 MiB`. A READY item carries ~2 KB of proof refs
(artifact_refs, release_pool). The first finish after 14:47:01 made `_write_job` exceed the cap; it raised
`ValueError("PNG batch job exceeds the bounded one-megabyte state limit")` inside the coordinator, which
stopped the whole batch. A full 1256-item batch needs ~3 MB.

**Fix.** Cap raised to 8 MiB (~3500 items). Regression `tests/unit/test_claude_png_batch_job_size.py` writes
and reads back a 1256-READY-item job; it failed on the old cap and passes now. Existing batch suite: 25/25.
On resume, `_recover_attempt` marks the six finished PNGs READY from their complete canonical runs.

**Re-pin to game ec1e57a7** (job 157: faster route-length measurement, byte-identical output, game CI green).
- Runtime built read-only: tree c986e5b5, 283 files, 2,547,273 bytes, attestation sha256 f351d37c….
- Registry entry added; PINNED_MAIN_SHA, UI const and 3 Godot suites set to ec1e57a7; 6534537c kept for old runs.
- Probe on read-only copies: LF-000147 and LF-000148 Difficulty V1 JSON identical to the saved results
  (52.1888 / 43.8423); full solve plus official analysis 20 s each (6534537c: 35–37 s).
- Pin unit tests 8 passed / 4 skipped (pre-existing missing 002 source). Godot suites PASS: r05_r05 loaded batch UI,
  r09_r02_r02 pinned authority, r09_r02_r04_r03 batch UI binding, gallery follows active source.

## 2026-11-13 ~15:30–15:50 local — installed app on 9a622485; job items keep only the pool summary

- Deployed 9a622485 to Release (3 files; backup `Release\.claude-deploy-backup-20261112\pre-9a622485`), launched via the
  Desktop LNK (STARTUP_READY 200 s), LEVEL FACTORY showed "Resume Batch · 1040 remaining"; owner-requested Resume pressed.
- The job file crossed 1 MiB (1,205,501 bytes) and was written normally; LF-000379 was recovered READY from its finished run.
- Found: a recovery of an ALREADY_IN_RELEASE_POOL item stored the full pool row (candidate + pipeline, 175 KB) in the job,
  while normal finishes store a 7-field summary. `_pool_summary` now keeps only candidate_id, disposition, entry_digest,
  pipeline_run_id, pool_size, publication, readback_verified and reason for finish, recovery and reuse paths.
  Regression `test_recovered_ready_item_keeps_only_the_release_pool_summary` failed on the old code, passes now.
- Full Python unit suite on 9a622485: 2070 passed, 15 skipped (2026-11-07 cleanup evidence), 0 failed.
  Batch/pool subset after the summary change: 177 passed.
- Seen on screen 15:37: a PNG that just finished left the RUNNING rows of Batch Issues and showed
  "PENDING · Solver attempt started" for a few seconds until the Release Pool re-read landed (LF-000395, LF-000398;
  both READY on disk). Batch Issues now shows the batch outcome for a Pending archive row whose loaded-batch item is
  READY/FAILED/REJECTED. Gallery suite check failed on the old code (LF-000005..007 "PENDING"), passes now; 10 Godot
  suites touching the batch/archive panel PASS.
- Stop after current at 15:37: job STOPPED at 232 READY / 5 FAILED, but the Studio kept "Running · 237/1256 done" and
  the batch launcher (factory_core_launcher png-batch-run) stayed at one busy core for 6+ minutes. Cause: after
  run_png_batch returns, the launcher calls record_batch_outcomes over every terminal item; each transition_pipeline
  rescans all 1424 Release Pool records (list_records), although every item was already recorded when it finished.
  Calls are idempotent (no new .history events after 15:41), only slow. record_batch_outcomes now skips items whose
  owner_release_projection is RECORDED with the same status. Regression failed on the old code, passes now;
  owner-release/batch subset 156 passed.
- Old launcher finished its re-projection at 16:02:42 (25 min after Stop). Studio closed with CloseMainWindow, c2d547dd
  deployed (backup `Release\.claude-deploy-backup-20261112\pre-c2d547dd`), relaunched via the Desktop LNK
  (STARTUP_READY 195 s), Resume pressed at 16:06. First finishes LF-000403/404/405 READY within 5 min; job item
  release_pool 344 bytes; Batch Issues on screen: 5 RUNNING rows first, then READY LF-000403/405/404, no stale Pending.

## 2026-11-13 ~17:00–17:45 local — Factory screening 5–9x faster, identical plans (owner: "Yes, speed it up")

- Batch on ec1e57a7 (39 PNGs): median 4.2 min; screening median 61 s but 3–10 min on hard images
  (LF-000408 56x56 VERY_HARD: 384 attempts, 616 s in the real run).
- Benchmark `screen_bench.py` (scratchpad) reproduces SupplyOptimizer screening + scoring exactly
  (best scores equal the real activity log for LF-000410 and LF-000408).
- cProfile LF-000408: 933 of 1007 s in ScreeningSimulator.quiesce; 55 M small numpy calls (per lane per wave a scan of
  every cell of that colour for active & reachable).
- Rewrite: state arrays are bytearrays; per colour the reachable ACTIVE cells are a sorted list of TargetSelector ranks,
  updated when a cell clears (remove) or becomes reachable (insort). Same claim order, same quiescence.
- Identical: frozen previous class `tests/unit/_screening_reference_v1.py`; `test_claude_screening_identical.py`
  compares solve/replay/peel/key on 80 random boards (72 SOLVED / 7 BOUND / 1 DEADLOCK) plus a forced DEADLOCK case;
  a deliberate target-order change made 49 of them fail. Real levels: pool+scores digest identical
  (LF-000410 60975357…, LF-000408 3a1c6c24…).
- Time (screening + scoring, machine busy with the 6-worker batch): LF-000410 22 s -> 10 s;
  LF-000408 107 s total vs 616 s screening in the real run.
- Supply/screening/scorer/optimizer/r09/campaign unit subset: 203 passed, 10 skipped.
- 17:20–18:17 local: b1075c4e deployed (backup pre-b1075c4e). Owner asked to bring in the PixelLab images made in the last
  hour. Read-only PixelLab MCP (Studio credential, never printed): list_images showed 4 new 2026-11-13 gallery sheets
  (1794578452172 cleaning liquids, 1794578538889 and 1794578714320 demon slayer characters, 1794578858079 football players),
  each 224x224 4x4. Downloaded with the Studio's own validated sheet fetch (no generation, no paid call), imported with the
  installed `pixellab-pro-4x4-import` operation: 4 x 16/16 PASS and imported (PX-ATLAS-000091..094, Final 1424 -> 1488).
  Studio restart took 909 s (restore-imported-sources 575 s for the first validation of 64 new PNGs). LEVEL FACTORY showed
  "Run Pending Batch (1013)" = 949 remaining + 64 new; pressed at 18:10; plan creation ~6.5 min; new job
  png-batch-ab2918ae (1013 items, runtime ec1e57a7) RUNNING at 18:17 with 6 workers.

## 2026-11-13 18:36–19:10 local — batch coordinator died on a Windows file-sharing race

- Job png-batch-ab2918ae: 27 READY in 20 min (median 3.0 min/PNG, screening median 10.5 s, ~88 READY/h). At 18:36 the
  coordinator process (png-batch-run) was gone while six PNGs (LF-000499..504) logged "Backend pipeline completed with
  disposition READY" at 18:36–18:38; job file last written 18:36:22, state RUNNING, 0.45 MB (not the size cap).
  The Studio showed "INTERRUPTED · Previous batch worker stopped with the application" (the app had not stopped).
- Cause: on Windows os.replace onto a file another process has open fails with PermissionError [WinError 5]
  (reproduced in the scratchpad). The Studio reads the job file every 2.5 s (png-batch-latest) and the Release Pool status
  projections while the batch writes them; my 60 s watch script also read the job file. One collision kills the run.
- Fix: `fs_atomic.replace` retries os.replace on PermissionError for up to ~18 s; used for the batch job file, owner release
  status projections, studio_extensions JSON evidence and owner_art_storage manifests. Regression
  `test_claude_job_write_tolerates_reader.py` (reader holds the job file 0.4 s) failed with WinError 5 on the old code, passes.
- UI: a batch worker that returned state ERROR was shown as "BATCH READY", then "stopped with the application". It now
  shows "Batch worker stopped: <error> · Finished PNGs are kept; press Resume Batch." and logs BATCH_WORKER_ERROR to godot.log.
  Gallery suite check failed on the old code ("BATCH READY · 1/3 READY"), passes; 4 batch UI suites PASS.
- Full unit suite: 2154 passed, 15 skipped, 0 failed.
