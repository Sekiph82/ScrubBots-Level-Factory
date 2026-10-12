# SB-LFX-018-C001-R02-R05-R04-R01 — Independent Technical Audit V01

**Date:** 2026-10-12  
**Repository:** `Sekiph82/ScrubBots-Level-Factory` / GitHub `main`  
**Verdict: TECHNICAL IMPLEMENTATION ACCEPTED / OWNER WINDOWS VISUAL ACCEPTANCE PENDING.**  
**Parent R04 remains CONDITIONALLY OPEN; parent R05 remains OPEN.**

## Independently inspected published evidence

- Read the actual `main` builder log `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md` (blob `ece911e0857d0778fcc2b51916ff208f4c5df8ed`), the changed controller `level_factory/scripts/factory_studio_exact_ui.gd` (blob `b5f146fafb1cefeb5812e9daf9e3d90939a9b5b4`), the entire added focused test `level_factory/tests/factory_studio_r04_r01_preview_scope_queue_suite.gd`, published implementation commit `54105bc831b7a2f1d8ce664f5d70b9b8382012ae`, and closing evidence commit `3976abf7b3f552ecff8a66d2973abbea564b2a96`.
- Actual product commit contains the targeted controller, the focused suite and ten small PNG fixtures. Closing `3976abf` is log-only. Published GitHub source matches the described implementation. No game repository or unrelated release/product change appears in the published product commit.
- Codex reports Desktop `HEAD == origin/main == 3976abf7b3f552ecff8a66d2973abbea564b2a96`, 0/0, no tracked dirty paths, 57 original untracked owner status roots preserved except the previously **expressly authorized** in-place Release file update/backups. GitHub cannot independently read the owner's local untracked Release or shortcut, so these last statements remain builder-local evidence.
- No code or tests have been re-executed by this independent audit. Existing earlier PASS results are reused without repetition.

## F01 — FIT / CLIPPED PREVIEW: TECHNICAL PASS, OWNER VISUAL PENDING

`VisualReviewClip` is now a dedicated clipped `Control` sized to the review interior (design rect x=401,y=160,w=780,h=640), containing `VisualReviewContent` and the `SelectedArtworkPreview` `TextureRect`. Source image is aspect-fitted and centered using its actual pixel width/height; nearest-neighbor rendering is retained. Zoom acts on the nested content while the outer host clips actual painting. Root responsive transform scales the outer host once rather than multiplying both the preview's dimension and transform. `Fit` restores zoom factor 1.0. The prior cross-panel giant preview cause is structurally remediated.

The new builder test reports a **real graphical OpenGL Compatibility Intel Iris Xe** SubViewport image readback, with a dedicated colored 20×59 probe: rendered pixel bounds inside clip at Fit and zoom, Fit aspect ratio within tolerance, and client geometry at 1536×1024, 1920×1080, 920×610. These actual rendered pixels are stronger evidence than old mock geometry. **Actual installed Windows screenshot of the corrected owner frog was not submitted yet.**

## F02 — TAB-SCOPED IMAGE: TECHNICAL PASS, OWNER VISUAL PENDING

Source now keeps separate `_preview_paths_by_screen` entries for PIXEL ART, LEVEL FACTORY and RELEASE POOL; switching tabs presents only selected-tab image, and 0-READY Release Pool is blank. Current LF source ID is not rewritten by tab transitions. The focused test exercises LF → PIXEL ART → empty Release Pool → LF and verifies that the chosen preview/source is restored. No misleading READY claim or implicit publish is present. Actual owner installed three-tab screenshots are still required.

## F03 — FOUR IMPORTS / THUMBNAIL SELECTION: TECHNICAL PASS, OWNER VISUAL PENDING

Imported `source_id`, original path, filename and disposition are retained in an in-session deduplicated `_imported_sources` queue; rejected files are tracked separately. Existing eight LF bottom buttons now render imported actual PNG thumbnail icons + filename and IMPORTED/REUSED label; tooltip contains the full filename and source ID. Clicking each chooses exact `_last_source_id` and preview path without calling `pipeline`. Ten-source queue paging is supported by the wheel over the existing strip. The new test exercises 4 accepted identities (2 reused, 2 imported), reimport dedupe, 10-source page 2, thumbnail/source binding and 0 solver calls until exactly one explicit Run Pipeline dispatch. The **recording gateway** is a mocked importer shaped like canonical responses, not a new real filesystem import acceptance. Prior owner screenshot had separately confirmed actual real 4-PNG Godot chooser/import path on the preceding code version. An imported PNG is **NOT** automatically a READY level.

## Test chronology and acceptance limitations

The builder log correctly records **three unsuccessful new-suite development invocations** before the final graphical PASS: test node path after reparenting, first headless Dummy renderer/no pixel readback plus wrong test tab context, and incorrect recording-double call order/wrapped text/color colliding with thumbnails. Codex then corrected the test and executed the final focused graphical suite (exit 0, marker `SB-LFX-018-C001-R02-R05-R04-R01 preview scope queue PASS`). No unchanged R04/R01/R02/M17 tests were repeated, and no broad LF pytest, 148 solves, R2/CP03 operations or 150-PNG run was performed. These failures are transparently reported, not hidden. The independent audit does not claim all intermediate attempts passed.

## Local Release and launcher (builder-reported)

After successful focused test, only existing `Release/ScrubBots Factory Studio/level_factory/scripts/factory_studio_exact_ui.gd` and `.factory-studio-install-manifest.json` were reportedly updated in place with scoped backups, not full Release replacement. Controller exact SHA-256 `46D83CB550F575030E2AC47AF6914BA7AAC1DD64958A5C64CB0D1AAF5C14A4BE`, manifest exact SHA-256 `6676F81C507499BAB51658D9E2B683073A22817D4BC5C82F033D3A8D4CE94408`. Existing desktop shortcut → original `launch_factory_studio.ps1` → existing Release remains unchanged and resolver reportedly exits 0. Actual owner GUI acceptance of **this updated installation** is STILL PENDING. A resolver check is not a screenshot.

## Next and stop conditions

**No new Codex remediation should be opened now** based solely on prior screenshots, because those screenshots predate this corrected Release installation. Owner should reopen the existing desktop shortcut, choose the same 4 small real PNGs on LEVEL FACTORY, dismiss popup, show centered/clipped frog and all four bottom thumbnails, click PNG #2 or #3 (observe preview change), visit PIXEL ART and RELEASE POOL (with 0 READY blank), then return to LF and observe restored selection. Request actual owner screenshot evidence for LF thumbnail/preview #1 and #2/3 and the PIXEL ART / RELEASE POOL tabs. If owner screenshots show a remaining defect, open one surgical owner-evidence remediation without retesting old suites.

Until that verification, the correct lifecycle state is `R04_R01_TECHNICAL_PASS_OWNER_VISUAL_PENDING`, NOT `OWNER_VISUAL_PASS`. **Full R05 milestone OPEN:** CP03/R2 live production and operator authority, authoritative full LF regression, other unrun 148 solver routes, and unrelated Alpix/Windows-native-OS chooser conditions remain as separately gated. No authorization for them is implied.
