# SB-LFX-018-R05-G02 | GPT OWNER WINDOWS VISUAL AUDIT V01 | ACTION AREA LAYOUT FAIL

Date: 2026-10-16 Europe/Istanbul
Scope: user-provided Windows screenshots: Screenshot 2026-10-16 025610.png (PIXEL ART), 025640.png (LEVEL FACTORY), 025715.png (RELEASE POOL). The uploaded images were not copied into the repository or modified.
**Verdict: LIVE THREE-TAB VISUAL PRESENCE PASS; G02 OWNER VISUAL ACCEPTANCE CHANGES REQUIRED, G02-R01 F01/F02 OPEN. Full R05 game/production OPEN.**

## Direct screenshot observations
- Windows title bar all three: ScrubBots Factory Studio (DEBUG). PIXEL ART, LEVEL FACTORY, RELEASE POOL tabs truly render. No title-error popup visible. DEBUG alone is not a failure: tracked scripts/launch_factory_studio.ps1 explicitly allows both normal and DEBUG exact titles. Screenshot does not prove shortcut launcher executable/process hash or exact current installed source revision.
- PIXEL ART: left prompt controls, bottom VARIATIONS / RECENT ITEMS · 140 PNG. Not a production provider or generated-art acceptance.
- LEVEL FACTORY: existing 002 frog central artwork fully bounded, exactly five bottom thumbnail cards 002..006, current SOURCE_ONLY, button Run Entire Loaded Batch (140). This count is not the historic nine READY; absolutely DO NOT invoke that action in a layout test.
- RELEASE POOL: nine visible candidate READY rows at left; right shows READY levels: 9, Visible: 9, Selected: 0, Target STAGING, Preflight Not run. Empty selection is consistent with zero selected; no new preflight or publication.

## F01 Release Pool ACTIVITY wrongly bottom-anchored
Owner explicitly requires RELEASE POOL ACTIVITY **immediately beneath the last right-hand action button and continuing to the right panel's inner bottom**. Screenshot last Preview Manifest button ends around y=540 while ACTIVITY label is near y=745, leaving roughly 200px unused. The small bottom stub is unacceptable. Current tracked level_factory/scripts/factory_studio_exact_ui.gd function _layout_release_pool_dashboard calculates min_top from final action, then uses maxf(min_top, panel_bottom - 220.0 * scale_y), forcing a bottom-anchored top and creating this gap. The construction also hard-codes activity geometry (774, 796, 128).
**Required:** actual last action/ⓘ bottom + 6–10 scale-adjusted px = activity header top; scroll immediately below header, filling to right RuntimeDetailsPanel bottom padding, without clipping or overlap. Preserve honest timestamped action events, empty-state, scrolling and tail-follow.

## F02 Right-side action/info controls have unequal sizes
Screenshot shows STAGING/PRODUCTION/Preflight etc smaller, while Upload Selected and Preview Manifest are taller. All **eight rows** (STAGING, PRODUCTION, Preflight, Validate Assets, Build Scrubpack, Upload Status, Upload Selected, Preview Manifest) must have identical action width, action height, left alignment, consistent row gaps and same-size matching ⓘ help icons.
Canonical source constructs disparate Rect2 action geometries at lines ~1470–1485, including starting x=1215 vs 1207, heights 36, 40, 54, 50, different help sizes. _layout_release_pool_dashboard then shrinks individual action width and positions help icons from those varied bases.
**Required:** one computed right-column responsive grid based on actual RuntimeDetailsPanel/geometry; constant uniform row height and gap, identical icon width/height, with safe client-bottom and activity allocations. No repeated-resize cumulative width shrinking. Preserve ALL labels, tooltips/help semantics, enabled states, STAGING/PRODUCTION target setting, Preflight/Status-only distinction, and real publication guardrails.

## Evidence gate and safety
Current installed Release sourceRevision (builder-reported) 89d74c9fe758ad0766f7ff5290154a1f56548b14 is NOT assumed identical to GitHub current tracked source; Codex must inspect installed controller hash/manifest and compare it before remediation.
Actual live app window evidence passes three-tab presence. Owner **explicitly reports two Release Pool visual failures**, so G02 native visual final PASS is denied pending real updated screenshot/user approval. No Pixel Art/Level Factory content, five-card dock, gameplay or Release/Pool product behavior changes authorized.
No 140-item batch, actual solver, owner ACCEPT/REJECT, preflight, upload, R2, production, owner PNG, installed shortcut mutation without safe scoped install, CI/Actions/workflow edits, OS TEMP, new worktree/clone, cleanup or 16 policy-blocked scratch deletion. Protect 3,220 existing untracked paths, accepted 002 and historic 9 READY.
A scoped installed Release UI overlay is allowed only when current Studio is confirmed naturally closed, present manifest/backup match and exact safe install authority still permits it; otherwise publish source/tests and report INSTALL BLOCKED instead of patching live process.
Authentic AI creator provenance, full-game current CPX-002, native NTFS ART_FIRST guard/race-free handles and complete R05 remain OPEN.

## Basis
GPT independently fetched Github main 177902c6d7d12f33f3a86ed3f389cd3c8c62863d, actual factory_studio_exact_ui.gd geometry and tracked PS1 title allowlist, and examined the supplied screenshots. Screenshot descriptions are observational, not claims of running native game tests.
