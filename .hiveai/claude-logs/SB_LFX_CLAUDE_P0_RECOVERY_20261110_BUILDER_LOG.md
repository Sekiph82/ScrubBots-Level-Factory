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

## 2026-11-14 — frozen "8/903 done" screen; batch be7ea390 COMPLETE

- Batch be7ea390 (903 PNGs, started 00:05 by the owner): COMPLETE 09:38, 900 READY / 3 FAILED (LF-001309, LF-001370,
  LF-001414: REAL_PLAY_NO_WINNING_PLAN after 10-12 plans), ~94.5 READY/h over 9.55 h. Previous job ab2918ae stopped at
  20:00 with four PNGs mid-solve when the Studio closed; its rest was carried into be7ea390.
- Owner saw "Running · 8/903" for ~10 min at 00:19 while the job file said 21 READY. Cause: Studio reads run one at a time;
  each click on a thumbnail queued a `restore-source-run-readonly` read that took 87-137 s, and the 2.5 s batch progress
  read waited behind them. Profile: restore_source_run called list_candidates() three times (each re-validates all
  ~1500 bundles, because every Studio read is a fresh process and the row cache is per process) plus an unfiltered
  Release Pool scan.
- Fix: `find_candidate(id)` reads only `Workspace/Candidates/<id>` (full scan stays as fallback); restore_source_run and
  _latest_review use it; the Release Pool lookup there is filtered by candidate id. UI: a newer selection read replaces
  queued ones; batch progress reads go to the front of the queue.
- Tests: `test_claude_find_candidate_no_full_scan.py` 2 failed on old code, 2 pass; gallery suite queue check failed on the
  old UI (3 stale selection reads ahead of batch-latest), passes; 6 related Godot suites PASS; full unit suite 2156 passed,
  15 skipped, 0 failed.
- Owner decision 2026-11-14: keep the grey/white background of atlas LF-001297..001312 as it is (a flood-fill clean was
  prepared in the scratchpad only; preview `docs/evidence/claude-arctic-background-20261114/before_after_preview.png`).
- 10:09 the owner generated one PixelLab Pro 4x4 in the Studio (operation 1794640153-36642104599, provider job
  a4334c55…, 10 credits). The record ended STUDIO_SHUTDOWN_CANCELLED ("Factory Studio closed; cancel_job sent"):
  the Studio process ended before the result was downloaded, so nothing reached Final. PixelLab had completed it
  (gallery 1b5647ad… "ELEMENTAL - desert", 16 frames). Fetched the sheet read-only (no new generation) and imported it
  with the installed pixellab-pro-4x4-import: 16/16 PASS, PX-ATLAS-000095, Final 1488 -> 1504 (LF-001505..LF-001520).
  c97f8b8d deployed (backup pre-c97f8b8d) and the Studio relaunched 10:12 for the owner. Note: my headless Godot test
  runs share the Studio's app_userdata log folder; they rotated the owner's session logs, so why the Studio ended at
  ~10:10 is not visible.
- Owner request: a Studio button that checks the newest 10 PixelLab productions and imports the missing ones.
  PIXEL ART now has "Get Missing from PixelLab" (startup-gated). Backend `pixellab-gallery-sync`: list_images + get_image
  only (allowlist PIXELLAB_GALLERY_SYNC_TOOLS; never generates), download via the existing validated sheet fetch, a sheet
  is known when Transactions has pixellab-atlas-<sha256>.json (verified on the last 12 gallery sheets: 11 matched; the
  one miss is real), unknown 4x4 sheets go through the existing pixellab-pro-4x4-import, then the Studio rescans Final.
  Found while verifying: gallery dd88e4b0 "ELEMENTAL - skyborne" (2026-11-12) is not in the Factory.
  Tests: test_claude_pixellab_gallery_sync.py 2 passed; gallery UI suite PASS; PixelLab/launcher subset 131 passed.
  Startup at 10:12 took >11 min: release-pool read 150 s, candidate-inbox 85 s, library-refresh >7 min (Release Pool now
  ~1400 READY; every startup re-validates all bundles/entries in fresh processes). Not deployed yet: the owner needs
  the running Studio for PixelLab work.
- 11:07:23-11:07:35 PixelLab CSV batch row 22/100 ("BIRD - volcanic") ended PRE_SUBMISSION_ERROR / MCP_NETWORK_ERROR after
  2 MCP requests (initialize + notifications/initialized), no job id, paid_submission_possible false (no credit used).
  The UI batch rule then stopped with 78 rows unsent. Root cause of the stop: `_mcp_http_request` had no retry for
  free pre-submission requests (the existing 8-retry rule covers only polling/downloading an accepted job) and replaced
  every URLError/TimeoutError by a generic text (`from None`), so the actual Windows/TLS reason was not recorded; it
  failed after 12 s, i.e. a dropped/refused connection, not the 30 s timeout. A free read at 11:09 worked in 1.1 s.
  Fix: free MCP requests retry 3 times (2 s, 4 s back-off); create_image_pro is still sent once (SUBMISSION_UNKNOWN);
  the error text now carries the method and the exception, e.g. "ConnectionResetError: [WinError 10054] ...".
  Tests: test_claude_mcp_network_retry.py 3 passed; PixelLab/MCP/launcher subset 134 passed.
  598e4d89 (gallery button) was deployed at 11:10 by the close watcher; the Studio was relaunched for the owner.
- Owner layout 2026-11-14 (after a drawn mockup, docs/evidence/claude-pixel-art-layout-20261114/): PIXEL ART left nav in
  two-column rows Single|Batch, Size|Get Missing, Prompt|Generate (CSV file|Run Batch in batch mode), then a PixelLab
  credits panel and the activity log. Size is one button showing "Size · W × H / 4×4 / 16 · max N colours" and opens the
  existing size popup; default size 56×56 (was 32×32, which PixelLab 4×4 rejects); the fixed-provider button and the
  separate Selected Size box are removed. Credits: new `pixellab-balance` (free get_balance) read at STARTUP_READY and
  after every PixelLab result; live value 790 / 2000 generations, reset 2026-11-20. Every popup Window gets one dark
  theme (18 px text, 20 px titles, framed buttons/inputs) through a node_added hook. The earlier right-side placement of
  "Get Missing" overlapped Edit Prompt because _layout_pixellab_details_artwork_gap moves only the three action buttons.
  Test runner now gives Godot test processes their own APPDATA so they no longer rotate the live Studio's logs.
  Tests: old left-layout contract test updated to the owner layout; gallery suite checks credits panel, size caption,
  popup theme (PASS); 3 left-layout Godot suites PASS; full unit suite 2162 passed, 15 skipped, 0 failed.
- Startup speed (owner: "Yes, speed it up"). Profiles on real data: release-pool read 399 s (296 s in list_candidates),
  candidate-inbox 296 s (295 s in list_candidates): every Studio read is a fresh process, so all 1486 candidate bundles
  were re-validated (read_bundle) on every startup. Fix: validated candidate rows persist in
  `Workspace/Studio Extensions/cache/candidate-rows-v1.json`, keyed by the stat stamps of every file validation reads
  (bundle files incl. preview, and the bound Imported owner-upload folder) plus a digest of the validation code;
  any change re-validates that bundle in full; the cache is only an accelerator (write failures are ignored).
  OWNER INSTRUCTION 2026-11-14 ("testlerini yapma ama kodu bitir, ben acinca kurulsun"): committed and installed
  WITHOUT running the test suites; only an import check was run. Tests and a real startup measurement are still owed.
  Also open: registering a new Final PNG in library-refresh takes ~4 min each (6 PNGs in 54 min today).

## 2026-11-15 — PixelLab atlases with a white background (118, 119, 120)

- Owner: the last three Studio productions had a white background. The Studio sent no_background=True; PixelLab drew a
  white card behind every frame anyway (also visible in the PixelLab gallery). Our intake had no background check
  (118: 16/16 PASS), so the frames entered Final as normal sources. Same pattern as the arctic atlas PX-ATLAS-000082.
- Owner-approved PixelLab remove_background (data URL of each 224x224 sheet; the gallery reference was refused because
  the gallery item has 16 frames, no charge): 3 calls, 3 generations (750 -> 747). Results: 118 16/16 PASS, 119 15/16
  (one USED_COLOR_COUNT, as in the original), 120 16/16; palette exact, no semi-alpha. Imported with the installed
  pixellab-pro-4x4-import as PX-ATLAS-000121/122/123 (LF-001921..LF-001968, 47 new sources).
- The 48 old frames got a REJECTED Release Pool status (reason: white background, replaced by 121-123); on the owner's
  instruction ("eski 48 kareyi sil") the 48 Final PNGs, their 45 Imported folders and atlases 118-120 were moved (not
  deleted) to data/output/Pixellab/Removed/2026-11-15-white-background-originals/ with a hash manifest; 0 mismatches.
- Fix: pixellab_pro_atlas measures each frame's light-background ratio (opaque #FFFFFF/#D4D7D9 connected to the frame
  edge); an atlas with >= 6 frames above 0.15 gets OPAQUE_BACKGROUND on all frames (intake REJECTED). Both atlas import
  paths give such slices a REJECTED Release Pool status so the Final scan never makes them Pending (all 16 slices
  still land in Final). Calibration: 122 atlases, flagged exactly 082 (arctic, owner kept it; already READY, not
  affected), 118, 119, 120. Tests: test_claude_pixellab_background_atlas.py 2 passed (detector failed on old code);
  PixelLab/atlas/launcher/release subset 141 passed.
- Owner confirmed permanent deletion ("Delete it"): the 141 files of
  data/output/Pixellab/Removed/2026-11-15-white-background-originals/ (48 Final PNGs, 45 Imported folders, 3 atlases)
  were deleted one by one after re-verifying each SHA-256 against the move manifest (no unlisted files); the empty
  folders were removed. The manifest with every path and hash is kept in
  docs/evidence/claude-atlas-background-20261115/deleted-originals-manifest.json. The 48 REJECTED Release Pool history
  records remain (append-only history).

## 2026-11-15 — Background-free prompts, 4 generations, startup time, EDGE_CLIPPED margin

- Prompt CSV (owner data, untracked): produced rows removed, every remaining prompt gets a no-backdrop / 3-px-margin
  suffix without commas (backups in docs/evidence/claude-prompt-csv-20261115/). Rows 0084/0085 removed after their GUI
  generation; 165 rows left.
- 4 owner-approved paid generations (40 generations): 124 BIRD volcanic (CLI, owner objected: must use the Studio),
  125 MAMMAL cavern (CLI), 126 MAMMAL oceanic and 127 MAMMAL skyborne (Studio GUI Single/Prompt/Generate, credits panel
  727 -> 717). Backgrounds all clean (light-background ratio <= 0.065). Passes 1/13/8/6 of 16; every rejection was
  EDGE_CLIPPED. Mistake on my side: 126/127 were run before the owner-requested EDGE_CLIPPED fix existed.
- Edge analysis 124-127: 36 of 64 frames touch the 1-px ring; only 15 of them with <= 8 px, so a pixel tolerance would
  not fix it and the margin wording in the prompt is ignored by PixelLab.
- Fix: a 56x56 Factory frame is now requested from PixelLab as 52x52 (provider_frame_size) and export_atlas pads every
  cell with a centred 2-px transparent ring (pad_atlas_frames, deterministic; only when both frame sides are < 56, so
  59x52 manual imports are not cropped). Manifest records provider_atlas_sha256 / provider_frame_padding; Grid Files and
  Final keep 224x224 / 56x56. Gallery sync recognises a known sheet by the raw or the padded SHA. No job was in flight
  (172 job records, none POLLING), so no accepted 56-px job is resumed with the new size. Same PixelLab price.
- Tests: new test_claude_pixellab_edge_margin.py (3; fails on old code: pad_atlas_frames missing). Old transport/poll
  fixtures updated from 224 to the 208 provider sheet; the old 59x52 import test caught a cropping bug in the first
  padding version (fixed). Targeted PixelLab/atlas/launcher/batch suites: 229 passed, 0 failed.
- Startup measured 1468 s: restore-imported-sources 1095 s (new Final PNG registration ~4 min each), release-pool
  122 s + 105 s, candidate-inbox 48 s (296 s before the candidate cache). Registration slowness still open.

## 2026-11-15 — Owner-edited EDGE_CLIPPED frames into Final; rejected slices no longer become Pending

- Edge-margin build 1cb6646c installed (Studio closed via CloseMainWindow; deploy_release.py --apply; the 3 installed
  files are byte-identical to the HEAD blobs).
- Bug found: the Final inventory scan registers every Final PNG without a Release Pool status as PENDING ("New
  SHA-verified PixelLab Final source discovered during inventory reconciliation"). Only OPAQUE_BACKGROUND slices got a
  REJECTED status at atlas time, so all 18 EDGE_CLIPPED slices of atlases 124/125 were PENDING. Fix:
  _reject_background_atlas_frames now gives every intake-rejected slice (any reason) a REJECTED status in both atlas
  paths.
- Owner redrew the clipped frames in Downloads\1..33.png (7.png = LF-001978, already in the system, skipped by owner
  decision). 20 of 32 had editor leftovers: semi-transparent pixels (1-98), near-palette colours (6 files), edge contact
  (8 files). New pixellab_pro_atlas.clean_owner_edited_frame (alpha >=128 opaque else clear; nearest Palette V3 colour;
  square canvas <= 59 with an empty 1-px ring, clearing the thinner outer column/row only when the art is wider than
  57 px). New owner_art_storage.archive_owner_edited_sprite puts a strict sprite into Final under the next LF name with
  a name-map record "owner-edit:<sha>" naming the frame it replaces (idempotent by SHA).
- Result: LF-002033..LF-002064 (32 files, sizes 56/58/59) imported and PENDING; the 32 replaced slices REJECTED (18 were
  PENDING, 14 had no status); the 4 un-edited EDGE_CLIPPED slices of 127 (LF-002018/2021/2023/2026) REJECTED.
  Evidence: docs/evidence/claude-owner-edits-20261115/ (owner-edits-manifest.json with owner-file and new SHA-256,
  cleaned/, before-after.png, asset-name-manifest.before.json).
- Tests: test_claude_owner_edited_sprites.py 3 (cleaner rules, archive naming/refusal, EDGE_CLIPPED -> REJECTED; the
  old function returned 0 for EDGE_CLIPPED-only manifests). PixelLab/atlas/Final/Release Pool/batch suites: 158 passed, 0 failed.

## 2026-11-15 — Partial white cards (PX-ATLAS-000130) and poor arctic set (129)

- Owner: the latest two Studio batch atlases look bad. 129 (SB_ATLAS_0087 MAMMAL arctic): small outline-less white
  animals, 15/16 PASS. 130 (SB_ATLAS_0088 MAMMAL volcanic): partial white cards behind ~8 frames, 16/16 PASS. 128, 131,
  132 are clean with 16/16 PASS and the 52->56 margin (no edge contact).
- Why the background check missed 130: the cards stop a few pixels inside the frame, so the edge-connected light ratio
  stayed under 0.15 in all but 4 frames (threshold 6).
- Fix: unoutlined_light_pixels counts opaque white/#D4D7D9 pixels directly on the silhouette border (PixelLab animals
  have a dark outline). >= 5 frames with >= 40 such pixels -> OPAQUE_BACKGROUND on the atlas. Calibration over 132
  atlases: flags only 082 (owner-kept arctic set, not re-processed), 129, 130; the white-animal atlas 019 stays
  accepted. Test: partial card without outline rejected, same block with an outline accepted (fails on old code: the
  card is not edge-connected).
- Not deployed yet: the owner's Studio batch is running. 129/130 frames are imported but have no Release Pool status
  yet; their status and the prompt suffix are owner decisions.
- Owner chose to stop the batch and return to the original prompts. The PixelLab CSV batch has no stop control in the
  UI (the "Stop after current" button belongs to the PNG/Level Factory batch), so the Studio was closed with
  CloseMainWindow while row 0094 was POLLING: the shutdown path sent PixelLab cancel_job (job 104e6238...,
  STUDIO_SHUTDOWN_CANCELLED). cb44e4d1 installed afterwards (installed file == HEAD blob).
- Prompt CSV (owner data): rows with a produced or accepted job (0086-0093) removed; the other 157 rows restored to the
  owner's original text from the pre-suffix backup (byte check: every current prompt started with its original).
  Backup of the suffix version: docs/evidence/claude-prompt-csv-20261115/before-revert-to-original.csv.
- New detector on atlases 128-135: 129 and 130 rejected (OPAQUE_BACKGROUND), the other six 16/16 PASS.
- Owner screenshot: PixelLab gallery sheet of row 0094 (REPTILE oceanic) with white cards behind frames 1 and 12.
  PixelLab finished it although the shutdown sent cancel_job; it is not in the Factory (Grid Files end at 135 =
  REPTILE row 0093; 133-135 are clean). The atlas rule (>= 5 frames) would have let it pass. Added a per-frame rule:
  light_card_edge = longest straight outline-less white border; >= 20 px rejects that frame (OPAQUE_BACKGROUND).
  Calibration over 132 atlases: 130 card frames 20-46, 117 white blocks 27, legit smoke/wind/spirit art <= 18, one
  flat-cut bust in 122 = 28 (accepted cost). Test: card behind frames 1 and 12 rejects exactly those (old code: none).
- Owner decisions: all 32 slices of 129/130 REJECTED (31 transitions + 1 already rejected). Gallery sheet of row 0094
  imported via the free gallery path (pixellab_recent_gallery_sheets(1) + _pixellab_gallery_sync) as PX-ATLAS-000136:
  14 PASS, frames 1 and 12 auto-rejected by the new card rule; frame 4 REJECTED by the owner. On the owner's request
  the white card was removed from 1, 4, 12 (flood from the frame border through transparent/light pixels + specks
  <= 6 px) and added as owner edits LF-002209/2210 (PENDING) and LF-002211 (gecko; owner rejected the result ->
  REJECTED). Evidence: docs/evidence/claude-atlas136-clean-20261115/. Same cleaning previewed for all 16 frames of
  130 in docs/evidence/claude-atlas130-clean-20261115/ (not imported; waiting for the owner).
- Owner approved the cleaned 130 set: 14 frames added as LF-002212..002225; squirrel (LF-002101) and deer (LF-002108)
  additionally had enclosed white pixels removed on request (31 and 5 px) and were added after owner approval. All 16
  PENDING; the 130 originals stay REJECTED. Manifest: docs/evidence/claude-atlas130-clean-20261115/manifest.json.

## 2026-11-15 — Rejected art is deleted, not kept

- Owner: "rejected olan ... pngleri sistemde tutmak icin israr ediyorsun ... rejected is sil. sistemde yer kaplamasin".
- Why a plain file delete was not enough: reconcile_status_projections rebuilds Release Pool projections from
  .history, and the Final scan marks every slice of an atlas invalid when one listed slice is missing.
- Code: owner_folder_batch accepts a transaction "purged_slices" list (other slices stay a valid group; a fully purged
  atlas no longer needs its Grid Files PNG); owner_art_storage.purge_final_slice; owner_release_library.
  purge_rejected_source (REJECTED only: projection, artwork copy, .objects blob, history); launcher
  _purge_rejected_sources (also Imported folder and Level Factory candidate, emptied file by file, no recursion).
  Atlas intake now purges its rejected slices right after marking them REJECTED.
- Run: 122 REJECTED sources purged (624 files hashed beforehand in
  docs/evidence/claude-purge-rejected-20261115/pre-purge-manifest.json; 941 deleted paths in purge-result.json), atlases
  129/130 removed. After: REJECTED 0, Release Pool/Rejected empty, transaction index 1752 entries / 0 invalid groups,
  reconciliation repaired 0. Tests: test_claude_purge_rejected.py 3; PixelLab/atlas/Final/Release Pool suites 215
  passed, 3 skipped, 0 failed.

## 2026-11-15 — Style image and richer prompts

- Batch with the original short prompts (rows 0094-0100): 14, 0, 16, 15, 16, 0, 0 of 16 passed; three whole atlases
  were white cards, so the card problem is PixelLab-side, not caused by the earlier suffix. Owner liked the arctic
  (PX-ATLAS-000140) and volcanic (141) sets and found desert (139) plain; owner stopped the batch.
- PixelLab MCP create_image_pro (tools/list, free) accepts style_image_url/base64 + style_copy and reference_images.
  generate_pixellab_pro_4x4_atlas_mcp takes style_image_png; when data/input/pixellab_style_reference.png exists the
  launcher sends it with style_copy outline/detail/shading (Palette V3 stays locked) and records style_image_sha256 in
  the job. Style image = atlas 140 with its rejected card cell (frame 3) cleared.
- Prompt CSV (owner data): produced rows 0094-0100 removed (150 left); each prompt gets "Charming characterful
  creatures with expressive faces and distinctive outfits or accessories with rich detail and shading. Each creature
  is an isolated sprite on a transparent background." (no commas: the Studio CSV reader splits on them; no
  white/card wording). Copies in docs/evidence/claude-prompt-csv-20261115/.
- Tests: test_claude_pixellab_style_image.py 2 (sent only when configured); PixelLab transport/poll/recovery 66 passed.
- Owner-approved cleaning of four batch atlases (sources from Generation Staging, same flood-clean as 130/136):
  oceanic frames 4/6/8/9/10/12, skyborne 13 frames (2, 9, 11 excluded: the clean removed light body parts), the two
  later 0/16 atlases (marshland and the dragon/lizard-warrior set) 16 + 16 frames. Row-7 frame 2 (naga mage):
  enclosed white removed (27 px) and on request the staff joined (3 grey -> brown, 3 outline pixels).
  51 sprites added as owner edits LF-002340..LF-002390 (PENDING); oceanic originals LF-002231/2235/2237/2239 (no
  status yet) set REJECTED and purged. Evidence: docs/evidence/claude-batch-clean-20261115/.
- Skyborne 2/9/11 fixed by hand on request: the card is pure #FFFFFF while the animals' light parts are #D4D7D9, so
  only border-reachable pure white was removed (2-7 enclosed white highlight pixels kept). Owner approved; added as
  owner edits (PENDING). All 64 frames of the four atlases are now in Final (10 untouched oceanic + 54 cleaned).
- Style-image test (owner-approved 5 generations, Studio GUI: 3 Single + 2 via a 2-row batch CSV
  data/input/pixellab_batch_test_2_rows.csv): AMPHIBIAN natural variety / woodland / cavern / oceanic / skyborne.
  Design matched the arctic style in all five. Cavern, oceanic, skyborne 16/16 PASS; natural variety and woodland came
  as full white-card atlases (0/16) and were cleaned removing only border-reachable pure #FFFFFF; owner approved and
  the 32 cleaned sprites were added as LF-002474..LF-002505 (PENDING). Rows 0101-0105 removed from the prompt CSV
  (146 left). Studio startup this time: 1109 s. Evidence: docs/evidence/claude-style-test-20261115/.

## 2026-11-15 — Owner 48-row PixelLab batch review and cleanup

- Owner ran 48 CSV rows in Studio (14:33–15:55 UTC). 35 atlases passed intake (560 frames PENDING); 13 came back with white cards (FRAMES_REJECTED).
- Watcher cleaned all 208 frames of the 13 card atlases (pure-#FFFFFF flood from frame border + <=6 px speck removal), archived them as owner edits, imported and set PENDING; 0 archive failures. Rejected originals were auto-purged.
- Scan of all 768 final frames: 25 passing frames contain border-reachable white, all reviewed visually as art pixels (snow, sparkles, bones, highlights) — no card fragments. Sheet: `docs/evidence/claude-batch48-20261115/residual-white-review.png`.
- Detached-component scan of cleaned frames found 5 grey card-edge strips left by the first cleanup (LF-002569, LF-002678, LF-002681, LF-002854, LF-003198). Stripped, re-archived as LF-003482..003486 PENDING; superseded versions set REJECTED and purged. 3 detached sparkles kept as art. Sheet: `cleaned-detached-review.png`, mapping `refix-v2.json`.
- Release Pool after: 2440 records — READY 1483, PENDING 955, FAILED 2, REJECTED 0. Final: 3048 PNGs.

## 2026-11-15 — Owner-approved fixes after full Final white scan

- Full scan of Final (3048 PNG) for border-reachable pure white: 29 hits, 26 are art (snow, waves, white bodies). 3 real card fragments cleaned: LF-001864 -> LF-003487, LF-001869 -> LF-003488, LF-002289 -> LF-003489 (old versions REJECTED and purged). Sheet: `final-white-scan.png`.
- 9 frames rejected earlier today were never in the system (`earlier-rejected-not-in-system.png`). Owner approved adding 5: four EDGE_CLIPPED frames (LF-002018/2021/2023/2026) got a 1-px transparent border (58x58) and detached 1-2 px specks removed -> LF-003495..003498; dragon LF-002278 had its white bottom line flood-cleaned -> LF-003494. Badger, raccoon, beaver and tiny chick stay out.
- Release Pool: READY 1483, PENDING 960, FAILED 2, REJECTED 0. Evidence: `docs/evidence/claude-batch48-20261115/fix8/`.

## 2026-11-16 — Startup hang: per-source full Release Pool rescan

- Symptom: Studio buttons stayed disabled for hours; worker `library-refresh` read 54 GB from disk.
- Root cause: `_sync_current_pixellab_final_sources` called `list_records()` (reads and re-verifies every projection + history, ~2,500 rows) once per Final PNG without a status. ~600 PNGs lacked status (passing slices of the 48-row batch), ~18 s each.
- Fix (commit 03cd8ed6): `list_records(source_id=...)` globs only that source's projections; inventory uses it. Test `tests/unit/test_claude_inventory_single_source_lookup.py`; full unit suite 2179 passed, 15 skipped, 0 failed. Deployed to Release.
- Real app relaunch 23:42 local: inventory complete in 333 s (3053 active PNGs, 1 invalid), buttons active. An orphaned worker from the previous Studio window (PID 3412, old code) kept running after close; owner ended it manually.

## 2026-11-17 — re-pin solver runtime to game 28741ed1 (game agent note)

**Note received (via owner).** The game agent said the Factory real-play precheck is pinned to game ec1e57a7
and robot routes changed with the new gameplay shell, so it suggested moving to latest CI-green main 28741ed1.

**What is actually pinned.** Only the attested solver runtime (`pinned_game_source.PINNED_MAIN_SHA`,
`data/Level Factory/Runtime/<commit>`). Real-play (`real_play_gate.ensure_real_play_gate`, precheck and
final gate) runs `tools/real_play_file.gd` in the live game checkout `C:\Users\sekip\Desktop\ScrubBots`,
whatever its HEAD is; no setting overrides it. The newest run (candidate e4709c39…, 07:58 today) already
recorded `gameCommit` 28741ed1 in both prechecks and the final gate.
`git diff ec1e57a7 28741ed1 -- scripts/gameplay scripts/data tools` is empty: solver/ProofKernel output
cannot change. The shell change (bf997e10, CI fix 37f08b70 `gameplay_shell_geometry.gd`, which re-ordered
game L30 real-play clicks) reaches real play through `production_gameplay_host.gd -> gameplay_screen.gd`.

**Change.** Built runtime 28741ed1 with `scripts/build_pinned_game_runtime.py 28741ed1 0b6dfc35 --apply`
(284 files, 2,618,857 bytes, tree 666d9641, attestation 875cded7…; new file data/config/events_v02_catalog.json).
Added it to `ATTESTED_RUNTIMES`, set `PINNED_MAIN_SHA`; older runtimes stay attested for their runs.
UI const and 3 Godot suites + 3 pytest files updated. Game CI for 28741ed1: "Android Family First10 APK" success.

**Residual (not done).** Final real-play results under data/Release Pool by gameCommit (all runs, incl. repeats):
87b11906 1117, 28741ed1 237, 9f1ada33 162(+15 LOST, 1 SEARCH_BUDGET), f60cfa94 152, 26d15718 53,
4cd72401 27, 4bb2b0bd 13, 1ba76a00 3. Everything before 37f08b70 was played with the old shell geometry, so
existing READY levels are not proven on the current game. Re-verifying them is an owner decision (CPU time).

## 2026-11-17 — P0-P factory database (S0–S2) and P0-O replay

**Owner request.** Write the redesign (one SQLite store, verify on write, fast startup, persistent backend,
LF↔RP one table) into TASKS.md as a detailed plan and work on it (TASKS › P0-P, S0..S5).

**S0 baseline** (`docs/evidence/claude-factory-db-20261117/baseline.md`): startup 333.1 s, of which
sync + READY reconcile 269.9 s; batch prep READY check 432 s → 10.1 s (ea57f002).

**S1** (d382e2a1): `src/scrubbots_pixel_factory/factory_db.py`. Tables images, sources, status_events
(exact owner-release-library event bytes), status (trigger-maintained), candidates, release_entries,
batch_records. Triggers: inserts must extend the chain, no updates, history deletable only when REJECTED,
status changes only through an event. Real import 192.5 s; parity 0 differences (3053/3053/3053, 6763
events, 1764 entries, 2437 batch records, 1766 candidates, 0 chain errors).

**S2** (d5833243, 2ad92d70, d86223e4; installed and launched via the Desktop LNK):
- Startup inventory from the DB: 0.3 s drift check (per-source event counts) heals missed events; Final by
  name/size/mtime, only new/changed files validated. Installed app: 2.0 s (was 333.1 s).
- `list_records` / `release_entries` answer from the DB; `verify=True` keeps the full read check on READY
  transition, pool entry, production plan and scrubpack identity. Release listing identical (1764 = 1764).
- Writes mirrored: transition/purge (status), import/alignment (source row), enter_release_pool (entry). Each
  mirror finds the DB beside its own data root. Found while testing: with a default-root mirror the unit suite
  wrote 17 tmp source rows into the owner's DB (rows only, no files); removed, parity PASS again; regression
  test watched failing on the old code.
- Found in the real app: after the fast backend the Studio froze ~1 min parsing 250 MB of full Release Pool
  entries (7.8 GB RAM). Studio list now gets slim rows built in SQLite (7.2 MB, 1.6 s). First slim version
  showed '<null>' titles (GDScript get() on present null keys); fixed and re-checked in the app.
- Not met: buttons usable ~106 s after launch. Remaining: Godot main-thread gallery work (~35 s frozen) and
  serial one-process-per-read ops (candidate-inbox ~15 s, restore-source-run ~12 s, loaded-png-batch-find
  ~12 s). That is S4 (persistent backend, async UI).

**Tests.** Full suite on the S2 code: 2430 passed / 12 failed; the 12 were 2 Godot suites needing the full
inbox (fixed: slim only on request), 7 tests whose patched release_entries lacked the new keyword (fixed),
1 legacy-scan test (now verify=True), 2 TASKS.md-dirty checks (clear after commit). After fixes: all 36
Godot suites pass; focused DB/pool tests pass.

**P0-O replay** (owner "Evet, oynat"): every READY level whose real play predated game 37f08b70 replayed on
the live game (head 40b38a5f, CI green, gameplay identical to 28741ed1): 1479/1479 WON_CANONICAL, 0 lost.
44 READY rows whose entry has no run id are replayed in a second pass (results.jsonl under
`data/Level Factory/Workspace/Revalidation/40b38a5f…`).

## 2026-11-17 afternoon — P0-P S4 and re-pin to game 1de7a7f6

**S4 service** (9af80a35, installed): `factory_core_launcher.py serve`; gateway routes 11 read-only operations to
≤3 long-lived processes; writers/solvers/paid providers keep one process each. After closing the Studio no service
process remained. Per-operation timings now go to `data/Level Factory/Runtime/studio-service.log`.

**Measured in the installed app** (Godot "Responding" sampled every second; service log):
- after 9af80a35: buttons ~85 s; Godot busy ~16 s after the Release Pool list and ~12 s after the source catalog.
- causes fixed in e94c3793 (installed): O(n²) `_release_entry_for_id` (1764×1764), 1764 synchronous icon loads,
  per-source linear upsert + source.json re-read for 3053 sources, Array `in` membership. Next launch: 0 frozen
  samples; STARTUP_READY 51.9 s (gate waits for loaded-png-batch-find 7.9 s, restore-source-run 3.6 s).
- candidate cache digest hashed CRLF (checkout) vs LF (Release) bytes → each side discarded the other's 1766-row
  cache (~2.5 min); normalized (89b539bf, installed).

**Owner batch (14:04)**: Run Pending Batch froze the window ~22 min (owner could not minimize it to reach the
Desktop) while png-batch-create validated 1286 PNGs on Godot's main thread. Cause: `verify_attested_runtime`
re-hashed the 284 runtime files per PNG (0.71 s each). Fixed (950812de): verified once per process, re-checked when
a file's size/mtime or the file set changes (stamp re-taken ≤ every 30 s); 40 PNGs 35 s → 6.6 s. Composite lookup
no longer loads ~2400 v1 import files. Planning calls moved off the main thread (fa0d42c0). Both not installed
while the batch runs. Batch at 15:05: 23 READY, 0 failed, 5 running, 1256 queued.

**Re-pin** (game agent via owner): game 1de7a7f6 attested runtime (284 files, 2,620,577 B). vs 28741ed1 only Home
screen/UI text changed; gameplay, gameplay shell and tools/real_play_file.gd identical; real play already ran on the
live checkout at 1de7a7f6. CI "Android Family First10 APK" success. Committed in 950812de.

**Tests**: all 37 Godot suites pass on fa0d42c0; focused unit tests pass. Full unit suite not re-run this round.

## 2026-11-18 — cleaned atlases saved to Grid Files; 18 Pending vs 16 solved

**Owner gallery check.** The owner sent 20 PixelLab gallery sheets. Matching only against Grid Files found 2 (136, 137)
and I wrongly said 18 were missing. Matching against Generation Staging originals and Final frames: all 20 are in
the system (316/320 frames in Final, almost all READY; 4 frames were owner-rejected and purged). 18 originals had
been purged as rejected art after their frames were cleaned (2026-11-15), so only loose LF PNGs remained.
**New owner rule:** after cleaning, always save the clean 4x4 atlas in Grid Files. Applied to the 18: assembled from
their current Final frames (58 px edge-padded frames cropped back to 56 after checking the empty ring; purged
frames left empty) as PX-ATLAS-000198..000215, registered in asset-name-manifest.json so new atlas numbers do not
collide. Evidence: docs/evidence/claude-clean-atlases-to-grid-20261118/ (manifest.json, before-after-1..3.png).

**18 Pending, 16 solved.** LF-000581 and LF-001785 had a verified READY pipeline and Release Pool entry but stayed
PENDING ("Solver attempt started") because their batches were interrupted before the outcome was recorded. Planning
skipped them as already READY but never fixed the status. create_png_batch now records READY for such sources via
transition_pipeline (test_claude_ready_excluded_status.py); the two were recorded the same way (PENDING 18 -> 16).
Not installed yet (batch running).

## 2026-11-22 — Owner Release Pool review: arctic atlas + tornado purged; deploy 7f8f631f/9f36b287
- Owner reversed the 2026-11-14 keep decision: 16 opaque white-background frames LF-001297..001312 (only opaque READY frames in a 3060 scan) and tornado LF-001213 set REJECTED and purged (279 paths; arctic Grid Files atlas removed with its last slice). Evidence: docs/evidence/claude-reject-arctic-tornado-20261122/.
- Deployed launcher + exact UI (new slices Pending at slicing; balance-based CSV limit). Relaunch counts: READY 3043, PENDING 736, FAILED 4, REJECTED 5.

## 2026-11-22 — Release Pool still listed the 17 purged levels (fixed bfdf7cf2)
- Root cause: _purge_rejected_sources removed status/history, Final, Imported and candidate folders but not Release Pool Ready entry files nor factory.db release_entries rows; the Release Pool list reads those. Never surfaced before because earlier purged sources were never READY.
- Fix: release_pool.purge_candidate_entries, called by the purge. Regression test tests/unit/test_claude_purge_release_entries.py (function absent at HEAD before the fix).
- Cleanup: 17 stale entries removed (docs/evidence/claude-reject-arctic-tornado-20261122/release-entries-purge.json). Deployed; relaunch: Release Pool 3043, READY 3043, PENDING 1550 (owner's new PixelLab output), FAILED 4, REJECTED 5.

## 2026-11-23 — Batch rate 57 PNG/h traced to memory paging; worker recycling deployed (783497dc)
- Per-PNG time unchanged vs 2026-11-17/18 (mean 335 s vs 313 s; real-play LOST retries ~2/PNG in both). Sustained rate then was 60-67/h; earlier "100-135/h" figures were short peaks.
- Machine: CPU 22-27% of 16 threads, 0.2 GB of 15.7 GB RAM free, commit 43 GB, ~115k pages/s. Each long-lived ProcessPool child held ~3.7 GB private (an idle one 3.8 GB private / 94 MB working set); Studio UI 4.1 GB private.
- Fix: ProcessPoolExecutor(max_tasks_per_child=PNGS_PER_WORKER_PROCESS=4); regression test seen failing before the fix; 13/13 tests in test_claude_parallel_png_batch.py pass.
- Batch stopped with "Stop after current" (no in-flight loss), deployed, relaunched: 6.0 GB free at idle; READY 3489, PENDING 2158, FAILED 9, REJECTED 5. Rate gain not yet measured. Studio UI 4.1 GB not investigated.

## 2026-11-23 — Real cause of batch slowdown found and measured; 10 workers (08381ed7, c8225225)
- 783497dc (worker recycling) was a wrong diagnosis: first post-deploy hour measured 46 PNG/h. Per-child memory stayed at ~525 MB through 8 real-play pre-checks and jumped to ~4 GB only in the READY finish (QA -> "pipeline completed READY", ~150 s).
- Read-only measurements on real data, fresh process each: list_candidates() lookup 57.3 s / +3.5 GB; full pipeline scan 5.4 s; find_candidate() 7.2 s / +2.1 GB (it loaded the whole 232 MB candidate-rows cache, which every child then kept); release_entries(verify) x2 16.3 s / +2.1 GB.
- Fix: READY finish uses find_candidate(); _enter_candidate_release_pool uses the passed READY pipeline; find_candidate validates the one bundle without the disk cache (0.05 s). After fix: lookup 0.1 s / +4 MB, verify x2 9.5 s / +13 MB. Recycling reverted.
- Owner: default 10 parallel workers, upper bound 12. Tests: 124 passed, 4 skipped (removed 2026-11-07 evidence) + 13/13 batch tests. Deployed; Studio relaunched; Resume Batch (1967 remaining) started by Claude via GUI; 10 workers confirmed, 4.1 GB free at start. Rate measurement scheduled after one hour.
- One-hour measurement after deploy (09:07-10:04 UTC): 136 terminal results, 143 PNG/h (before: 46-57/h). 10 workers at ~550 MB private each, 3.5 GB free, 8 pages/s (was ~200k), CPU 68%. Counts: READY 3814, PENDING 1831, FAILED 11, REJECTED 5.
- 12 workers (14063498) deployed via Stop-after-current, relaunch and Resume Batch (1799 remaining). One hour (10:25-11:23 UTC): 160 terminal results, 164.9 PNG/h; 28 pages/s, CPU 67%, 2.7 GB free; no new FAILED. Counts: READY 4006, PENDING 1639, FAILED 11, REJECTED 5.

## 2026-11-23 — FAILED cause analysis and owner's supply-repair idea (experiment only)
- All REAL_PLAY_NO_WINNING_PLAN failures are slot jams: in every lost plan (291 total) all 5 slots hold WAITING batches of 1-3 colors whose targets are covered; supply never exhausted; 700-1400 px left. LF-003674 failed screening (no real-play run).
- Owner idea: at the jam, shrink the jamming batch and move its excess later. Shrinking only the largest waiting batch: LF-005285 stuck 43->50 over 8 rounds, still LOST (each waiting batch holds a slot even with 1 robot). Shrinking every WAITING slot batch to its used part and appending the rest to its column end (+1 click each): LF-005285 WON_CANONICAL in round 1.
- Same repair on the first lost plan of each FAILED level (max 6 rounds): 16/21 WON_CANONICAL (LF-002850, 002773, 002697, 003715, 003960, 004033, 004196, 004627, 004693, 004981, 005004, 005063, 005090, 005282, 005285, 005409); 5 still LOST (LF-002494, 003524, 003870, 004724, 005185). Experiment files: data/Level Factory/Workspace/claude-supply-repair-experiment/. Not wired into the pipeline; repaired plans have not been through solver proof, Difficulty V1 or READY.
- Slot-jam repair wired into the real-play alternatives loop (2c8ca6ce): on a LOST pre-check every WAITING slot batch keeps its used robots, the rest go to its column end (+1 click); the exact order is replayed by the screening kernel, proven by solver KERNEL_REPLAY, verified and real-played again (max 6 rounds); a won repair continues through the unchanged Difficulty V1 / final export / authoritative real-play path. Tests: 3 new unit tests (seen failing before the helpers existed) + loop integration test; 8/8 real-play alternative tests, 33 passed + 28 subtests in supply-optimizer suites. Main batch finished 2026-11-23 22:27 UTC (READY 5626, FAILED 30, REJECTED 5, PENDING 0); deployed while Studio was closed. FAILED levels not yet retried: Studio "Retry (N)" also re-solves the 5 REJECTED sources, so the owner is asked first.
- Retry of only the 30 FAILED sources (job png-batch-37a753b68c979ebde75938f91e08771d via png-batch-retry-release-sources with the 30 FAILED ids; 5 REJECTED untouched), started by Claude via Studio Resume Batch at 06:36 local, finished 06:56: 29 READY, 1 FAILED (LF-003674, screening: no candidate after 432 attempts). 28 of the 29 were won by the slot-jam repair (1-3 rounds); LF-005982 won without repair. Counts: READY 5655, FAILED 1, REJECTED 5, PENDING 0.

## 2026-11-24 — Campaign label rule, Pixel Art Pause/Stop, VERY_HARD prompts, game metadata
- Campaign eligibility by score within hard tolerance of the slot's own target; published class = slot cadence class (e70816b3). Game catalog check only requires a valid class token. 87 passed + 8 subtests (campaign/publisher suites).
- Game repo 081f98a6 (separate session): official Difficulty V1 added to 160 of 170 L31-L200 metadata (10 skipped, owner decision pending); Factory `_game_authority` now returns catalog tail [199, 200].
- Pixel Art CSV batch Pause after current / Stop after current (b4e4d6de); 13 Python tests + Godot batch CSV UI suite pass.
- PixelLab create_image_pro schema (read-only tools/list): no minimum-colour option; only max_colors (2..64), palette, style image, reference images.
- Pool analysis: official challenge ~+1 per used colour (3 colours avg 43.6 -> 12 colours avg 57.2, max 62.6); hardest 300 mostly COLOR profile. VERY_HARD prompt CSV added (data/input/very_hard_atlas_prompts_30.csv).
- Owner asked to stop PixelLab production: Studio closed at 08:02; row 12/33 (POWER-UP) had already been submitted (balance 220 -> 210) and finished on PixelLab at 08:03; recovered with Get Missing from PixelLab after relaunch (16/16 imported, no new paid request). Deployed e70816b3, b4e4d6de.
- Campaign score bands 201-1200 (b75c84fd) and UI header/zoom/size alignment (c29e0a0d) committed; 3 band tests, 30 UI tests, 2 Godot UI suites pass; not yet deployed (Studio open).
- VERY_HARD trial (row 1, LF-006379..006394) solved alone via pending-png-batch-create / png-batch-create / png-batch-run with the installed backend: 16/16 READY, official scores 35.1-55.2 (mean 46.1); none reaches the VERY_HARD band (>=57.9). Owls 48.0-55.2, foxes 45.3-52.4, stags 35.1-41.5 (FLOW). Prompt v2 written (rows 2-30, row 1 unchanged).
- VERY_HARD trial 2 (prompt v2 row 2, LF-006395..006410): 16/16 READY, mean 53.2 (trial 1: 46.1, pool ~50), max 61.1; 2 in VERY_HARD band >=57.9 (LF-006406 61.1, LF-006409 58.9, both curled foxes), 7 HARD (52.4-57.9), LF-006401 57.7. Coverage 50% vs 36%; colour count unchanged (6.2).
- VERY_HARD trial 3 (row 3 dressed characters, LF-006411..006426): 16/16 READY, mean 53.8, max 58.0; 1 VERY_HARD (LF-006415 58.0), 11 HARD (52.4-57.9), 3 MEDIUM, 1 EASY-band (44.6). Colours 7.7 (6-9), coverage 49%, regions 130.
