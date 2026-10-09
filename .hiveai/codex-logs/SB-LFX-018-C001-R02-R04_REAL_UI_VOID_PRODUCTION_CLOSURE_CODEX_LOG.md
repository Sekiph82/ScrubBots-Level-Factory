# SB-LFX-018-C001-R02-R04 — Preserve R03, Build Real Three-Screen UI, Fix VOID Authority, Wire Production Publish
Document role: CODEX BUILDER LOG

## Session start and safe synchronization

- Starting timestamp: 2026-10-09T11:40:33.672+03:00 (Europe/Istanbul).
- Canonical repository: Sekiph82/ScrubBots-Level-Factory; persistent root C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator; origin https://github.com/Sekiph82/ScrubBots-Level-Factory.git; branch main.
- Persistent checkout began at b9b1daeca55fa2a222d0bbd522b8b41d59025f04, 0 ahead / 34 behind origin/main before fetch. It had 2,897 untracked owner/runtime files and no tracked modifications. Compared all 53 incoming changed paths to the untracked paths; no collisions. git merge --ff-only origin/main safely advanced it to ecbb364401ef2473c0f33090fe6392c2f015cbb4; all untracked files remain present and unstaged.
- Stashes were inventoried and left unchanged. Existing registered worktrees were inspected. The execution worktree is C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LFX-018-C001-R02-EXACT-THREE-MASTER, verified canonical origin, initially clean at R03 evidence head 8ec602beee3cd867d0092a4806863f6a2fcec347, then fast-forwarded to exact current Factory origin/main ecbb364401ef2473c0f33090fe6392c2f015cbb4, 0/0 and clean. No reset, rebase, clean, stash, forced checkout, or force push.
- Active task state is R04 authorized; root TASKS.md is unchanged. Current final authority remains ChatGPT independent audit/owner visual review. This log does not claim audit acceptance.

## KEEP / ADAPT / ADD matrix (completed before product edits)

| Disposition | R04 implementation decision |
|---|---|
| KEEP | R03 Alpix adapter and CSV-SHA resumable job state, LIMIT/resume, Claude credential boundary, Magnific/PixelLab routing, READY auto-pool, Reject exclusion/Accept restore, Release installer/shortcut, exact three owner masters, and useful R03 tests. |
| ADAPT | Replace MasterCanvas.texture plus transparent hotspots with actual Godot Controls and live bindings at the same three-master geometry; fix void_capability so a shallow/missing ancestor is reported as incomplete history and exact-current complete authority proves audited VOID; extend the existing publisher handoff to connect the audited verified-STAGING/current-main-replay/owner-approval/CP03-008/CP03-009 APIs; add the missing external-PNG identity/order and adversarial production coverage. |
| ADD | Permanent real-control dynamic-state coverage and exact 1536x1024 screenshots from the durable runtime; full-history exact-current game authority setup for LF19; transient exact manifest/version/PRODUCTION owner confirmation through canonical approval; end-to-end source-order/identity rejection tests. |

## Authority read before implementation

- Active R04 prompt URL and full tracked prompt; root TASKS.md; AGENTS.md; GOVERNANCE.md; previous R03 strict re-audit; R04 audit criteria; docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md.
- docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md; docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md; docs/product/FACTORY_STUDIO_LEGACY_EXE_PIXEL_ART_BEHAVIOR_V01.md; docs/product/FACTORY_STUDIO_EXACT_THREE_MASTER_UI_V03.md; visual master index; owner Alpix/auto-pool decision.
- Current main identifies blockers: screenshot-backed UI, shallow-history VOID false negative, missing production publish chain, external PNG identity/order test gaps, and R03 final screenshots absent. Local Alpix smoke remains conditional on current local plugin availability.

## Baseline and next actions

- R03 retained product baseline: 5b975a92532b9df1e781c96cb1de37dbba73aa6e; current evidence main at session start: 8ec602beee3cd867d0092a4806863f6a2fcec347.
- Product edits have not started. Next inspect the exact audited production API contracts, the real UI/control architecture, current game authority history, and current Claude Alpix configuration; then implement only the authorized R04 delta.

- Log creation correction: the first PowerShell here-string write contained four control characters caused by JavaScript string escaping in the shell command. Corrected them before product edits and scanned the file; no control characters remain.

## Implementation and verification progress (2026-10-09, Europe/Istanbul)

- Implemented the R04 native three-screen UI in `level_factory/scripts/factory_studio_exact_ui.gd`: the owner screenshots are now hidden references, and the screens render with actual Godot panels, buttons, live status, candidate/release thumbnails, a selectable artwork preview, mode-aware single/batch controls, external PNG and CSV selection, level settings, solver/replay/supply/review actions, release pool selection, STAGING/PRODUCTION controls, and exact owner-confirmed production promotion.
- Repositioned runtime controls after visual inspection of generated screenshots to remove overlapping labels/cards/actions. The final preview evidence currently exists in TEMP only; durable-runtime captures remain pending installation.
- Fixed the R04 VOID authority classifier: shallow history with an absent audited object now returns `INCOMPLETE_GIT_HISTORY`; complete history with an absent audited ancestor returns `AUDITED_VOID_ANCESTOR_MISSING`. Both states carry explicit reason codes.
- Extended the publish adapter to bind a candidate manifest SHA-256 into preflight identity and require current exact manifest/version/target owner approval before invoking the canonical production publisher. The UI has no direct R2 credentials. Production fail-closes when the remote manifest-history API is not available for an existing production manifest.
- Added/updated publisher, VOID, UI binding, R03 auto-pool, runtime, and owner screenshot tests. Retained R03 provider/CSV/resume/credential behavior and existing release pipeline.
- The installed Claude configuration has no Alpix plugin; did not add a third-party plugin or credentials. Owner Alpix live-provider smoke remains unavailable for that reason.
- Focused publisher/UI/VOID/release batch tests: `59 passed in 1.84s`. Earlier VOID source/game parity suite: `20 passed in 516.26s`, including the seven required LF19 cases. Earlier R03/UI/publisher subset: `41 passed` before the final layout-only change.
- Godot runtime suite with Godot 4.7.2 console binary: `SB-LF06-002-C001-R01 committed runtime suite PASS`, exit code 0. Godot still reports shutdown RID/ObjectDB allocations (4 dummy textures, 216 shaped-text records, 1 font, 2 CanvasItem RIDs, 24 ObjectDB instances); this is recorded as a builder diagnostic, not clean-shutdown evidence.
- Real-renderer visual suite captured `PIXEL_ART_FINAL.png`, `LEVEL_FACTORY_FINAL.png`, and `RELEASE_POOL_FINAL.png`, each exactly 1536x1024. The screenshots were visually inspected and the screen controls repositioned; one later screenshot refresh is required after the final Release Pool card spacing adjustment. The real-renderer suite also reports shutdown texture/RID/ObjectDB leak warnings despite exit 0.
- Godot invocation correction: invoking the GUI `godot.exe` in headless mode concealed parse/runtime diagnostics. Switched to `godot_console.exe`. It exposed and corrected an `elif` placement parse error, `String.is_absolute()` (changed to `is_absolute_path()`), and unsupported `Button.icon_max_width` assignment. A dummy-renderer screenshot attempt failed because headless mode has no 1536x1024 render texture; the real renderer then captured all three sizes successfully. These failures and corrections are retained here.
- `python -m compileall -q src tests scripts level_factory/scripts` and `git diff --check` passed. The full `python -m pytest -q` regression is currently running; its final result will be appended after completion.
- Durable install preflight observation: the authorized runtime root already exists and has an install manifest at source revision `8ec602beee3cd867d0092a4806863f6a2fcec347` with 2,074 managed files. The R04 installer will only run after publication; exact manifest-to-file hashes and new-path conflicts must be checked before invoking the installer. Existing desktop shortcut also exists and will be preserved/updated only via the safety-managed installer.

- Read-only installer preflight completed: all 2,074 previously managed runtime files exist and match their recorded SHA-256; no tracked source path absent from the old manifest collides with an unmanaged existing runtime path. The script remains deferred until R04 tracked changes are committed and published at current origin/main.

- Final layout refresh of the three TEMP screenshots completed after the Release Pool selected-card spacing update; all three remain 1536x1024 and visually inspected. The real-renderer Godot process reports the same shutdown RID/ObjectDB warnings; no SCRIPT ERROR was present.

- Full-suite attempt 1 (environment correction required): python -m pytest -q -> 1,741 passed, 20 skipped, 10 failed, 3 errors in 526.55s. This invocation omitted SCRUBBOTS_PROJECT; failures/errors were canonical replay/VOID/pipeline tests that therefore reported unavailable without game authority. No product test failure was hidden. Rerunning the entire suite with verified full-history exact-current game authority at C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LFX-018-C001-R02-R03-GAME-AUTHORITY.

## Regression run outcome and bounded closeout decision (2026-10-09)

- Authority-enabled full-suite attempt used `SCRUBBOTS_PROJECT=C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LFX-018-C001-R02-R03-GAME-AUTHORITY`. It entered exact-current 20x20 and then 32x32 canonical solver bridge requests with `analyze=true`, no `max_visited`, no timeout in `ScrubBotsSolver.run()`, and no `res.json` result after more than 30 minutes on the first request. The second request showed the same unbounded pattern. I stopped only the exact test Godot process and pytest process so the task could proceed; this run has no final pytest summary and is not a pass.
- A first Stop-Process attempt specified the already-exited PID 33224 and returned “Cannot find a process”; verified that PID had exited, then stopped the still-running pytest PID 28236. No other processes were targeted.
- Result boundaries remain: focused publisher/UI/VOID/release batch tests `59 passed`; focused LF19 source/game parity `20 passed in 516.26s`; Godot runtime suite passed its assertions with shutdown leak diagnostics; real-renderer screenshots are captured at 1536x1024 but Godot reports RID/ObjectDB leak diagnostics on exit. Full suite under no authority was separately recorded above (1,741 passed, 20 skipped, 10 failed, 3 errors) and is not final evidence.
- The full run did not collect the late-added external-PNG dispatch contract assertion; that test will be run explicitly before the product commit.

## Final scoped verification before publication

- Added external PNG dispatch coverage: single PNG import, multi-select, and CSV rows each route through `batch-import`, then the same canonical `pipeline(source_id, request)` in input order; columns 3/4/5 and background intent are forwarded. Focused suite including this test: `60 passed in 2.26s`.
- `python -m compileall -q src tests scripts level_factory/scripts`: exit 0. `git diff --check`: exit 0. Protected task-state/handoff/audit/prompt diff check: exit 0.
- Godot 4.7.2 editor import/parse: exit 0 with no script parse errors. Headless app boot: exit 0. Both and runtime/screenshot suites report RID/ObjectDB leak diagnostics on shutdown; these are retained as open builder diagnostics.
- Production approval coverage verifies exact reviewed manifest SHA, content version and PRODUCTION target. No R2 credentials were read or logged. Alpix is still absent from Claude's installed plugin configuration; the owner-provider smoke is not claimable.

## Durable runtime installation and visual evidence

- Product implementation commit `a22b1c0acd0bc3d606005aef1a15ef8641694dab` was pushed normally to `origin/main` (`ecbb364..a22b1c0`).
- The safety-managed installer completed with exit 0 and updated `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`; the desktop shortcut path was reported as `C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk`.
- Installed runtime manifest source revision is `a22b1c0acd0bc3d606005aef1a15ef8641694dab`, with 2,077 managed files. Rechecked every managed file against its manifest SHA-256 after installation: 0 missing or mismatched files. The prior 2,074-file owner manifest was intact before install, with 0 pre-existing managed hash conflicts and 0 unmanaged new-path conflicts.
- Durable-runtime screenshot suite was first invoked before Godot asset import and reported missing generated `.godot/imported` caches; tracked PNG/SVG source assets were present. Ran Godot editor import successfully (exit 0), then reran the real-renderer screenshot suite. Final captures have no script or resource-load errors and each is exactly 1536x1024:
  - `Release/ScrubBots Factory Studio/owner-visual-evidence/SB-LFX-018-C001-R02-R04/PIXEL_ART_FINAL.png` SHA-256 `9bb7c3cb2612c707fe2a96af29e707f232fd33324330d5b0d367b397d3d86039`.
  - `Release/ScrubBots Factory Studio/owner-visual-evidence/SB-LFX-018-C001-R02-R04/LEVEL_FACTORY_FINAL.png` SHA-256 `0bd686369bcd13d112a0485468b03338c20ab0fe6feaeba2c1524cfae6cc6dd`.
  - `Release/ScrubBots Factory Studio/owner-visual-evidence/SB-LFX-018-C001-R02-R04/RELEASE_POOL_FINAL.png` SHA-256 `fa0a287d079c2e2d13a0b1b7a05941d8e329c3980f6bd6a2a453550634603d6e`.
- Both editor import and screenshot/runtime shutdown continue to report Godot RID/ObjectDB leak diagnostics despite exit 0. This remains an open builder diagnostic, not acceptance evidence.
- Handoff state: `AWAITING_GPT_SB_LFX_018_C001_R02_R04_STRICT_REAUDIT / OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`. Claude has no installed Alpix plugin, so live owner-provider generation could not be exercised. The builder has not claimed audit or milestone acceptance.

- Persistent canonical Desktop mirror was fetched after product publication. It was clean in tracked files, 10 incoming tracked paths had 0 collisions with 2,903 untracked owner paths, and it fast-forwarded cbb364..a22b1c0; final local main == origin/main == a22b1c0acd0bc3d606005aef1a15ef8641694dab, 0/0, tracked-clean. All 2,903 untracked owner files were left untouched.
