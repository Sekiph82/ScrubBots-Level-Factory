# SB-LFX-018 R05 | Independent owner AFTER Release Pool visual audit + startup nil runtime gap V01

Date: 2026-10-16 Europe/Istanbul
GitHub source baseline: `b068aec77f33e14d8ec95fd968d66cc723c62a37`.
**Owner visual verdict: RELEASE POOL LAYOUT PASS / OWNER ACCEPTED. Runtime startup restoration FAIL/OPEN. Full current-game R05 production and CPX-002 OPEN.**

## Direct owner BEFORE/AFTER comparison
Owner provided real Windows BEFORE screenshots `Screenshot 2026-10-16 025715.png` (Release Pool), `025640.png` (Level Factory) and `025610.png` (Pixel Art), and genuine AFTER Windows screenshot `Screenshot 2026-10-16 104048.png` showing installed `ScrubBots Factory Studio (DEBUG)` at 1536x960 screen capture. Owner explicitly stated **'release pool sayfasi ok'**, approving the new Release Pool layout. GPT inspected the actual shared image directly; the screenshot itself was not copied to GitHub.

AFTER screenshot visual facts:
1. Right Details panel shows exactly eight action rows `STAGING, PRODUCTION, Preflight, Validate Assets, Build Scrubpack, Upload Status, Upload Selected, Preview Manifest` using visibly equal width/height and same-size aligned ⓘ help controls.
2. Activity heading `RELEASE POOL ACTIVITY` starts immediately after the Preview Manifest row (~y499 after button bottom ~y497); its content begins below heading and the remaining right-side panel extends to the inner bottom. The earlier approximately 200px blank gap and unequal buttons are resolved.
3. Left candidate list shows **nine** READY rows, right summary `READY levels: 9; Visible: 9; Selected: 0; Target: STAGING; Preflight: Not run`. Lower `SELECTED FOR RELEASE` strip shows three `Empty selection` cards and one `Add More Levels`, all visually within strip at this viewport. This is screen observation only, not proof of live game solve or Pool publication/asset checksum.
4. The `(DEBUG)` Windows title was already allowed by tracked launcher. No evidence of a present launch-window-title block. The user approved page layout, not startup-error-free product operation.

**G02 Release Pool F01/F02/F03 owner GUI visual gate CLOSED/PASS for provided real AFTER viewport.** Other screens were not re-shot after the update, but their source layout is unchanged from previous owner screenshots. G02 visual closure must **not** be inflated to end-to-end startup or R05 game-production PASS.

## New separate P0: read-only startup restoration throws Nil-to-Dictionary
Owner separately supplied Godot 4.7.2 Compatibility console trace:
`SCRIPT ERROR: Trying to assign value of type 'Nil' to a variable of type 'Dictionary'. at: _restore_loaded_png_batch_readonly (res://scripts/factory_studio_exact_ui.gd:1234)`
called by `_restore_imported_sources` at ~1220. Independently read the exact GitHub controller source:
`var composite: Dictionary = resolved.get("batch", {})` at 1234,
`var job: Dictionary = latest.get("job", {})` at 1248.

The Python extension `src/scrubbots_pixel_factory/studio_extensions.py::find_loaded_png_batch` intentionally returns `{"disposition": "NO_MATCHING_COMPOSITE", "batch": None}`, and also returns `batch=None` for some unverified/mismatched/ambiguous cases. `src/scrubbots_pixel_factory/png_batch.py::png_batch_latest` intentionally returns `job=None` for no matching job / mismatch. Godot's Dictionary.get(key, {}) default **does not apply when the key exists with Nil value**, so a typed Dictionary assignment errors before the intended `NO_MATCHING_COMPOSITE`/mismatch guard can run. The exact source and backend contracts establish a **real, reachable null-type bug**.

Secondary `job` assignment on line 1248 is the same latent failure mode, even after fixing line 1234. Review only other directly relevant typed Dictionary retrievals from optional extension data (e.g., `counts`) for safely typed defaults. Never convert a mismatch into APPROVED/MATCHED, never fabricate restored jobs or rerun solver. Validate Variant `is Dictionary`, then assign the typed dictionary or literal empty dictionary. Keep existing dispositions `NO_MATCHING_COMPOSITE`, `LEGACY_COMPOSITE_AMBIGUOUS`, `SOURCE_SNAPSHOT_MISMATCH`, `BATCH_JOB_SOURCE_MISMATCH` conservative and non-mutating. Missing saved composite is not itself data loss: the original 140 PNG or persisted nine READY records have not been shown missing. Actual startup error must be fixed and user rechecked.

## Installer and disk conditions
Prior R04 builder reported installed UI/controller SHA256 `e0a44647f5e54d9b18ca76cf50d8582be41e36bacc6f5400229cc777bfd0b9c2`, installed manifest SHA256 `56c9f32518fe01b2354942600c8d19662cab0713a23b42551304fccfbc0493eb`; 2,316 managed entries + nine allowed overlay paths + one R04 overlay receipt; UI restored visually in AFTER screenshot. The standalone `scripts/install_factory_studio_ui_overlay.ps1` is **pinned to the OLD baseline**, not a generic second-release updater: do not rerun `-Apply` on an already updated manifest. Two R04 rollback files (195,392 + 454,775 bytes) remain and are justified until startup fix reinstallation validated. The script's `-Rollback` path lacks fresh running-Studio/reparse guard; do not invoke it while Studio open.

User has repeatedly forbidden expensive CI, TEMP worktrees/clones, disk-residue. R04 cleanup 254 generated files (+901,120 bytes C: free) builder-reported. Preserve previously policy-denied 16 scratch files, original PNG sources, owner-accepted 002, historical nine READY, Release Pool and desktop launcher. No mass cleanup or installer bundle regeneration.

## Decision / master milestone
Accept owner's release-page visual approval immediately. Next one **integrated MILESTONE MASTER** must (in one Codex instruction, not repeated micro-task prompts) complete source null/typed-contract fixes, bounded zero-disk startup tests, safe follow-on one-controller manifest-preserving overlay (including R04 receipt chain, small bounded recovery, no full installer), truthful owner startup smoke gate, leftover safe backup cleanup after verified acceptance, and read-only next R05 real-game/CPX-002 readiness inventory. Do not run actual solver/production/140-item batch, R2 or CI. Parent R05 full game-production gate remains OPEN.
