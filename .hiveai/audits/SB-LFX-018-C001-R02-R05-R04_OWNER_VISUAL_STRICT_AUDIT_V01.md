# SB-LFX-018-C001-R02-R05-R04 — Independent Owner Visual Strict Audit V01

Date: 2026-10-12
Repository: `Sekiph82/ScrubBots-Level-Factory`, GitHub `main`.
Implementation commits: `a527041c43d7e9801281bbaf68d6bf3c53b4823d`, `7b34ac0cbf7f1455c58a2eee778c11ac8b5725fb`.
Builder publication checkpoint: `3454bd24952c82d63e8b195f9827c19c3ff85ce7`.
**Verdict: R04 CHANGES_REQUIRED (OWNER VISUAL FAILURE). R04 focused headless/mock test PASS remains valid but is NOT native acceptance; parent R05 OPEN.**

## Independently checked

Reviewed actual published single R05 builder log, `level_factory/scripts/factory_studio_exact_ui.gd` and exact R04 source/test commit diffs in GitHub. Owner supplied **three actual installed Factory Studio Windows screenshots** on 2026-10-12: LEVEL FACTORY with `PNG import · 4 selected` popup, RELEASE POOL, PIXEL ART. This is owner-runtime evidence, not hypothetical simulator screenshots. The images themselves are conversation attachments, not GitHub screenshots, and are not claimed to be committed in this report.

### Correctly completed within limited scope

- **Window maximization/responsive chrome: OWNER VISUAL PASS, bounded.** Three tabs/panels/controls are arranged in a scaled and centered window rather than the earlier tiny upper-left frame. Remaining blank aspect margins are acceptable for proportional artwork unless owner objects; do not reopen basic scaling from scratch.
- **Actual Godot visible FileDialog operation: OWNER VISUAL PASS for selecting/importing 4 actual PNG file paths.** Owner's results popup shows four different 32x32 names, two `ALREADY_IMPORTED`, two `IMPORTED`, and per-item `owner-upload-` source IDs. This supports real multi-file dispatch and de-duplication for those four files. It does NOT demonstrate Windows **OS-native** picker (current UI is Godot FileDialog), a 150-file batch, four solver runs or four READY levels.
- **No implicit solver:** LEVEL FACTORY right panel reads `Solver: Awaiting pipeline`; builder source dispatches only `batch-import`, not `pipeline`, on selection. Retain this behavior.
- Codex reports exact Release controller/manifest in-place update and correct unchanged PS1/shortcut, GitHub publication 0/0, all 57 untracked top-level entries preserved. These are builder-local claims supported by log, not independently checked on owner's filesystem.
- Small focused GDScript test reported PASS with a mocked canonical-response-shaped recording gateway. It **did not** exercise the real filesystem importer, actual popup clipping, tab state or on-screen four-artwork navigation. Do not rerun this unchanged PASS test.

### BLOCKING DEFECTS CONFIRMED BY OWNER SCREENSHOTS

**F01 — Preview overflows all review boundaries.** The imported 32x32 green frog is rendered as a huge image through most of center/bottom and overlaps the right DETAILS controls, bottom strip and UI. User expected art to fit **inside** VISUAL REVIEW CANVAS. This cannot be accepted. Published `_preview_rect` is a child of root MasterUI rather than a clipped, bounded preview host. `_capture_responsive_layout` records base control geometry; `_apply_responsive_layout` treats preview specially, multiplying both `size` AND `scale` by `_responsive_scale`, while `_update_live_chrome` also resets preview position/size and zoom uses scale, making the rendered bounds sensitive to interacting transforms. Regardless of exact pixel magnification mechanism, there is **no visible clipping/enforced image-fit**. Changing just text/status or the external file is insufficient.

**F02 — Preview leaks between unrelated tabs.** Exactly the same unsolved frog PNG remains prominently visible on LEVEL FACTORY, PIXEL ART and RELEASE POOL. `_show_screen` switches button visibility but never clears/hides `_preview_rect` on RELEASE POOL; on other tabs it may reload the global `_selected_art_path`. Level Factory import context must not automatically appear on PIXEL ART (which should show its own generated/selected artwork) or RELEASE POOL (which must display only selected, true READY release artwork). Screenshot RELEASE POOL shows **READY levels: 0**, yet huge frog remains: clear failure.

**F03 — Multi-import queue visible only as popup, not selectable artwork.** Four unique sources are acknowledged, but only the first PNG can be previewed. The LEVEL FACTORY bottom strip still displays eight `—` placeholders. In current code `_refresh_runtime_cards` builds LEVEL FACTORY variations from the **candidate inbox** (derived level candidates), not the newly `batch-import`-ed source items. `_import_pngs` stores only `last_import_summary` string lines and a single `preview_path/source_id`; it does not retain a selectable list of all imported source/path pairs. Thus remaining selected PNGs have no visible browse/select-to-Run-Pipeline route; popup alone is insufficient.

### Overall contract / gate result

- R04 G1 responsive positioning: **OWNER VISUAL PASS (narrow)**.
- R04 G2 single/multi dispatch with honest status/no auto solver: **PARTIAL PASS**. Actual multi path import acknowledged, but bounded preview, per-import navigation, cross-tab scoping **FAIL**. Native Windows OS picker remains NOT VERIFIED (Godot chooser operates); 150-solver batch and regression remain NOT RUN.
- R04 G3 local scoped Release/launcher publication: **BUILDER-REPORTED DONE, OWNER VISUAL NOT ACCEPTED** because three-screen UX is broken. Existing Release contains the defect.
- R04 G4 publication/57 owner-path preservation: **builder-reported PASS**. GitHub tracked evidence verified.
- **Do not award R04 PASS or R05 closure.** Open narrow same-task corrective `SB-LFX-018-C001-R02-R05-R04-R01`, rather than another R05 full-suite loop. Prior test passes remain accepted without repetition. After targeted correction and in-place owner-approved Release update, obtain owner screenshots for all three tabs plus selecting second/third imported PNG. No live R2, no solver batch, no disk cleanup.

### Mandatory remediation acceptance

1. A 32x32 PNG is drawn with nearest-neighbor aspect-correct zoom and visible geometry **fully inside a clipped Visual Review Canvas**. Pixel image never paints across DETAILS, header, buttons, or VARIATIONS strip. Zoom/fit remain bounded at existing supported sizes; avoid double responsive scaling and rendering-order regressions.
2. Level Factory imported PNG shown only in its own tab; Pixel Art shows only relevant Pixel Art artwork; Release Pool with 0 READY levels shows **no image**. Selecting READY level can show only its actual READY identity, not stale LF import.
3. After 4 distinct source imports, show 4 usable thumbnails/rows in the existing Level Factory bottom strip (the remaining slots may be empty). Selecting any row updates canvas preview, selected `source_id` and the single explicit `Run Pipeline` target. Preserve original order, de-dup, and statuses. No automatic solver from selection; do not silently promote IMPORTED => READY.
4. Narrow new visual/geometry/state/navigation test only ONCE for new fix. Existing mocked import suite, provider history tests, full suites, 148 pending solver cases MUST NOT be repeated. If Codex native GUI unavailable report `OWNER_VISUAL_PENDING` and let owner take actual Windows screenshots.
5. Update *only* changed controller/dependent files in existing owner-approved Release/manifest, after narrow check PASS, without replacing Release directory or rewriting unchanged shortcut. Preserve remaining 57 owner paths, no TEMP.
