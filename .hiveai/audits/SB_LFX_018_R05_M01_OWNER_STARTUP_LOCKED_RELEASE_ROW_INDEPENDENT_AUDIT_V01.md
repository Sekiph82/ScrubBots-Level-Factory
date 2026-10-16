# SB-LFX-018 R05 M01 | Independent GPT owner-native startup audit: locked Release candidate Button | V01

Date: 2026-10-16 Europe/Istanbul
GitHub main reviewed: `6e4cbe46aee1b9dfdcbead679f7b1b2fc15ef7eb`.
Verdict: **Owner-installed Factory Studio launches and tabs render; former Nil-to-Dictionary crash NOT OBSERVED in supplied console screenshot. NEW genuine Release Pool BUTTON LIFETIME runtime fault P1 OPEN. M01 CLEAN STARTUP PASS DENIED pending focused correction and real owner recheck. Previously accepted G02 Release Pool geometry remains PASS, and parent R05 current-game production remains OPEN.**

## Authentic owner Windows screenshot evidence
Owner provided three new Windows 1536x960 screenshots at approximately 18:02:
- Terminal window in front of Factory Studio shows Godot Engine v4.7.2 Compatibility and **both** errors:
  `ERROR: Object is locked and can't be freed. at: core/object/object.cpp:787`
  `SCRIPT ERROR: Attempted to free a locked object (calling or emitting).`
  Two identical GDScript stack paths, one underlying trigger:
  `[0] _refresh_release_candidate_rows (res://scripts/factory_studio_exact_ui.gd:3753)`
  `[1] _select_release_candidate_id (res://scripts/factory_studio_exact_ui.gd:3799)`.
- LEVEL FACTORY screen shows frog source 002 large render, five bottom thumbnails, READY/Replay WIN and saved last result indicators. This is user-observed UI state, NOT a fresh solver, replay WIN or saved record checksum proof.
- RELEASE POOL screen shows large frog candidate preview, eight aligned equal right action/help buttons, Activity beneath final row with **CANDIDATE PREVIEW / READ ONLY** events, right summary READY 9, Visible 9, Selected 0, STAGING, Preflight Not run. A preview-only click caused a visible event, not a production publish. Left list in this image displays fewer rows in viewport than the summary; cannot infer actual records were deleted. Pixel Art also opens per owner. User experiences functioning UI despite terminal errors.

**Important:** prior `Nil` typed Dictionary assignment at startup is absent from the shown terminal, but an error-free full boot cannot be attested while this separate GDScript error exists. Owner's earlier `release pool sayfasi ok` visual geometry approval is still valid. Do NOT claim M01 entire startup PASS/CLOSED yet or delete its rollback files.

## Independently verified precise code cause
GPT fetched canonical `level_factory/scripts/factory_studio_exact_ui.gd` at GitHub main:
- `_refresh_release_candidate_rows()` lines ~3749-3753 iterates current buttons, `_release_candidate_rows.remove_child(child)`, then `child.free()` synchronously.
- Each new candidate `Button` registers `row.pressed.connect(_select_release_candidate_id.bind(candidate_id))`.
- `_select_release_candidate_id()` updates current preview, clears signature, and **synchronously calls** `_refresh_release_candidate_rows()` line ~3799.
A candidate button therefore invokes its own parent list's synchronous rebuild *from within its `pressed` signal emission*. The list immediately calls `free()` on the same currently calling/emitting button, which Godot correctly rejects as a **locked object**. The shown engine backtrace matches this exact reachable mechanism. The error can interrupt list rebuild after a subset has been removed; that explains UI looking functional yet partially stale. The status count and bytes of stored 9 READY are not shown to have changed.

There is **one** direct `child.free()` call in the inspected Studio script and it is at this row rebuild. This is a UI lifecycle/reentrancy bug, not a GPU/OpenGL, memory-capacity or external Claude Godot-editor issue. Avoid uninstall/reinstall, source/Pool corruption accusations or deleting 140 source PNGs.

## Corrective scope within the SAME M01 MILESTONE MASTER
- Do not undo or rework accepted Release Pool geometry. Fix only candidate Button destruction and rebuild scheduling, preferably `queue_free()` deferred deletion rather than synchronous `free()` on a signal-emitting object, combined with safe detachment/reentrancy protection as needed. If making selection handler deferred, keep selection/preview/selection-mode semantics and ensure idempotency under rapid repeated taps.
- Focused actual Godot 4.7.2 test must **trigger a real `pressed` signal from a current candidate button** (not merely direct `_select_release_candidate_id` function call), then verify after frame that candidate row count equals filtered IDs, nine READY remain, selected preview/current ID and activity event are correct, no free/locked-object SCRIPT ERROR or duplicate/stale button, and Manage Selection/Select All/Clear still function. Repeat selection and tab/resize transition. Check old regression/source-bound test remains true, no acceptance/upload/Preflight/Batch/solver/provider operation. A headless process `exit 0` is insufficient without actual suite PASS marker and zero stderr SCRIPT ERROR.
- Same existing M01 source/fixture/updater and original one-controller follow-on update pathway only; code+focused local tests then owner-normal-close/current installed-process check, manifest-preserving and rollback-bounded install. Studio is visibly OPEN in owner screenshot, so **NO hot patch or forced close**. Old R04/M01 four small recoveries total 1,302,594 B remain intact until a clean real-owner startup and UI selection recheck.
- Protect existing 2,968 historical untracked, two M01 backup copies, 16 previously deletion-denied scratch paths, owner 140 original PNG, accepted 002, saved nine READY 4/4/1, launcher, shortcut, historical Godot cache. Zero Actions/CI/workflow edits, no OS TEMP/worktree/clone, no full installer or solver/CPX-002/R2/production.
