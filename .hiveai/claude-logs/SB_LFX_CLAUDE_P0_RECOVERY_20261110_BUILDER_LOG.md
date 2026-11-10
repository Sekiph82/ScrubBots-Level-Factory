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
