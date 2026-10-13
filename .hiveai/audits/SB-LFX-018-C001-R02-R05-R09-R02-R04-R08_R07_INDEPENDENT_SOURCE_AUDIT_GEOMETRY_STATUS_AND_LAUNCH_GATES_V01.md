# SB-LFX-018-C001-R02-R05-R09-R02-R04-R08 | GPT strict independent R07 implementation audit

Date 2026-10-13. **Reviewed LF GitHub** final builder HEAD `814679da793f2f1115b9ddb6443654a18089c559`, product/test commit `4530d3a0768431fc2c9b119b31ecf598efac6091`, R05 historical builder log, full current `level_factory/scripts/factory_studio_exact_ui.gd`, current `scripts/launch_factory_studio.ps1` and R07 focused Godot suite. Verdict **R07 PARTIAL SOURCE PASS, DESIGN F01 FAIL, LIVE LAUNCHER GUARD PENDING, OWNER INSTALLED VISUAL PENDING**. No independently executed Windows test/installation/hash verification by GPT.

## Passed on code review (not owner UX closure)
- Five `LevelVariation1..5` cards, sliding `start=clamp(i-2,0,max(0,N-5))`, no previous 8-slot paging. Source-bound `_sync_verified_batch_follow` validates job index/source PNG and source-record SHA, attempt and assigned columns, and updates selected sprite, right rows and left activity; 9 transition fake test exercises many transitions. Source selected during active batch cannot hijack it.
- Release Pool now uses `ReleaseCandidateScroll/Rows` for all filtered IDs with a responsive 14–15 visible at test 1920×1080, bottom management, dock-relative selected-three + Add More row, 8 help buttons and truthful retained in-session activity with status-only operations explicitly labeled. Three affected Godot suites PASS **per builder**, with no actual native solver or R2/STAGING/PRODUCTION launched.
- Builder read-only existing **REAL first 9 PNG composite job** `png-batch-c898cfef80663a61e8246ea1e4da8e13.json` found `COMPLETE / 9 READY / 0 failed or rejected / 3,4,5 allocations = 4/4/1`. GPT cannot independently read those local bytes, so this is verified only by Codex local audit. Existing 002 Pool and output reported preserved.
- Scoped existing installed Release sourceRevision `4530d3a0768431fc2c9b119b31ecf598efac6091`, installed controller and manifest only, old shortcut+PowerShell SHA preserved; all 555 output files post-overlay hash stable according to builder.

## Confirmed F01 FAIL: owner requested a **taller dock and shorter image canvas**, but source does neither

- In current `_apply_responsive_layout`, **unchanged** `bottom_y = size.y - bottom_margin - 106.0 * scale_y`; `RuntimeBottomStrip.size.y=106.0*scale_y`; central canvas height set through bottom_y, `VisualReviewClip/_preview_host` still fitted to the same bottom_y. In `_layout_level_factory_thumbnail_dock`, only card count/width changes from 8 to 5 inside exactly the SAME previous-height dock. No screen-specific height allocation or enlarged five-card **height** exists. Thus requested reduction of oversized artwork vertical area and increase of five-card gallery vertical space is **not implemented**, even though 5-card count/width tests pass.
- R07 suite checks dock containment and count, **not requested preview-vs-dock geometry delta** relative to previous installed version or owner annotated bounds. Treat headless PASS as limited, not the entire owner design accepted.

## Confirmed F02 partial: five-card status displays import state, not current batch item state

- `_refresh_runtime_cards()` builds `status_caption` solely from `_gameplay_sources[*].disposition` (`IMPORTED` / `REUSED`), not `_batch_snapshot.items[*].status` and current attempt. While centered active item marker follows job, the five cards cannot distinguish live RUNNING, already READY, FAILED or REJECTED; owner requested useful process tracking in the enlarged cards. `_sync_verified_batch_follow` and right/left statuses are source-bound, but card state captions remain stale SOURCE_ONLY/import labels. Do not claim all five show processing status. Repair via snapshot-attested source_id and job item status, distinct from source import and prior READY.

## F03 launcher gate: installed app shows DEBUG window; unchanged PowerShell strict title check reports failure

- Builder read-only visual opened the Studio after scoped install, but same original `scripts/launch_factory_studio.ps1` expects `$studioProcess.MainWindowTitle -eq 'ScrubBots Factory Studio'`; Godot instance was named `ScrubBots Factory Studio (DEBUG)` after a `SetWindowText` attempt. The guard shows `Factory Studio window title did not match the owner-approved title`. The app may still be usable when manually viewed; this is **not proof of a source/UI crash**, but is an unclosed shortcut acceptance gate. Diagnose actual process handle, Godot title update timing, launcher .lnk and safe supported identity check; do not silently broaden matcher to arbitrary windows or mask real failures. Preserve exact .lnk and launcher unless a narrow, owner-safe verified change is necessary and specifically justified in evidence.

## Additional boundaries

Release Pool results and Help native screenshot were inspected by builder but **OWNER Windows photo not received**; no user-visible acceptance. R07 test covers mocked current_index transitions, not live running nine-solver recording. R05 full regression, CPX-002 shipping, R2/STAGING/PRODUCTION still OPEN.

## Audit ruling

**R07 not CLOSED** solely based on these three tests. All positive implemented changes should be retained. ONE small R08 remediation prompt `.hiveai/prompts/SB-LFX-018-C001-R02-R05-R09-R02-R04-R08_TALL_FIVE_CARD_DOCK_BATCH_CARD_STATUS_AND_LAUNCH_GUARD_MASTER_PROMPT.md` must deliver shorter LF canvas/taller five-card dock, source-bound real status captions, focused geometry/status regressions, and launch title diagnosis/fix without risk to working nine READY. Then independent GPT audit and one owner Windows screenshot per tab. Zero new native solver/publication.
