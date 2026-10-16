# SB-LFX-018 R05 | MILESTONE MASTER M01 | Accepted owner GUI -> robust startup -> safe installed smoke -> full-game readiness

Date: 2026-10-16 Europe/Istanbul
Role: SINGLE CODEX MILESTONE MASTER PROMPT. **Execute all safe phases continuously under this ONE prompt. Do not create one micro-prompt per fix or repeatedly ask for the same approval. Stop only at a genuine owner-action or safety gate.**
Repo: Sekiph82/ScrubBots-Level-Factory, branch main.
ONLY Desktop development checkout: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator.

## MILESTONE M01 - Owner acceptance and target outcome

Read LIVE root `TASKS.md` (SOLE tracker), `AGENTS.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, and owner screenshot audit:
`.hiveai/audits/SB_LFX_018_R05_G02_OWNER_AFTER_RELEASE_POOL_PASS_AND_STARTUP_NIL_GAP_AUDIT_V01.md`.
R04 installer evidence audit is `.hiveai/audits/SB_LFX_018_R05_G02_R04_CLEANUP_AND_INSTALLED_UI_OVERLAY_INDEPENDENT_AUDIT_V01.md`.

**Owner accepted the ACTUAL installed RELEASE POOL layout:** AFTER screenshot `Screenshot 2026-10-16 104048.png` shows 9 READY candidates; eight uniform buttons with same-size aligned help icons; Activity immediately after Preview Manifest down to the right-panel bottom; bottom selected cards contained. The owner explicitly said "release pool sayfasi ok." **Close G02 owner visual F01/F02/F03 now. DO NOT rebuild/retest/alter accepted Release Pool geometry.** The screenshot is genuine Windows observation, not current game/CPX-002/production PASS.

**New critical startup error observed on the SAME installed app:**
`SCRIPT ERROR: Trying to assign value of type 'Nil' to a variable of type 'Dictionary'. at: _restore_loaded_png_batch_readonly (res://scripts/factory_studio_exact_ui.gd:1234)` called from `_restore_imported_sources`.
Current source uses `var composite: Dictionary = resolved.get("batch", {})` at line 1234, and `var job: Dictionary = latest.get("job", {})` around 1248. The backend intentionally returns present keys `batch: null` on NO_MATCHING_COMPOSITE / ambiguous / snapshot mismatch, and `job: null` on no matching job / mismatch. A default argument to Dictionary.get does not replace an explicitly present null. This is a confirmed source-contract defect, not evidence that owner PNG or saved nine READY records vanished.

**M01 done only when:** (A) accepted Release Pool GUI visual record saved and unchanged; (B) BOTH nullable batch/job startup cases plus neighboring affected optional Dictionary cases guarded without weakening lineage gates; (C) bounded focused Godot/static/contract evidence green with zero CI; (D) safely updated real installed controller via source-controlled manifest-preserving tiny overlay and truthful owner startup smoke or explicit owner-action BLOCKED; (E) disk hygiene/rollback plan recorded; (F) read-only real-game/CPX-002 next gate matrix produced. Full R05 native current-game integration remains OPEN unless separate real authoritative evidence justifies it. No fabricated blanket PASS.

## Standing owner safety and git controls

**Zero GitHub Actions, CI, workflow edits or dispatch, hosted test jobs or cost exposure.** No new temporary worktree/clone, OS TEMP copies, cache explosion, test/output PNG evidence archive, broad disk sweep, new heavy full installer, R2/provider calls, real solver/game replay/CPX002 run, batch 140, automatic Accept/Reject/Preflight/Upload or PRODUCTION publish. Do not use/update `scripts/install_factory_studio_shortcut.ps1` (would stage 2,331 files/rewrite shortcut). Preserve all 140 owner PNG, original 002 ACCEPT, nine READY 4/4/1 records, existing Factory Studio state/launcher/shortcut, R2 and unrelated game checkout. Prior deletion-policy-denied 16 scratch entries may NOT be retried/bypassed. Do not force-stop Claude/Godot game processes: they are unrelated to installed Factory Studio. Minimize CPU and laptop disk writes.

Use only canonical Desktop LF main, tracked clean and ancestor evidence, `git fetch --prune origin`, normal `git merge --ff-only origin/main` only if 0 local unpublished commits, no case-insensitive owner-untracked path collisions. On true divergence/dirty owner edits STOP, no second merge/rebase/reset/stash/force. Commit sources/tests before builder log; logs append ONLY to existing `.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`. DO NOT edit root TASKS.md or GPT-owned prompts/audits/criteria/HANDOFF/workflows; GPT independently audits and updates tracker.

## PHASE I | Source fix with conservative backend semantics

Edit ONLY `level_factory/scripts/factory_studio_exact_ui.gd` in the startup PNG batch restore/read-only path and nearest directly affected typed-optional retrievals. For keys `batch`, `job` (and if necessary counts), read into `Variant`, check `is Dictionary`, then safely use the typed value, or explicitly branch to empty/unverified. Never directly type-assign a potentially Nil `Dictionary.get`. Preserve `_gateway == null` and source checks.

Do not interpret absent saved composite or job as authenticated success. Preserve distinctions for `MATCHED`, `LEGACY_EXACT_MATCH`, `NO_MATCHING_COMPOSITE`, `LEGACY_COMPOSITE_AMBIGUOUS`, `SOURCE_SNAPSHOT_MISMATCH`, `BATCH_JOB_SOURCE_MISMATCH`, `NO_MATCHING_JOB`. If provenance mismatched/ambiguous, keep Resume/Retry BLOCKED; do not create new composite/job, mutate saved json, auto-run solver, force ACCEPT, or replace saved last good READY. A valid saved job should still show correct totals and resume status; missing/null job should not trigger Godot runtime error. Check other same restore call sites (not giant unrelated refactor) where nullable backend `job`/counts keys are type-assigned; fix only confirmed reachable cases. No changes to Python business rules necessary unless evidence proves backend violates its declared contract.

## PHASE II | Focused regression, no uncontrolled disk cost

Extend EXISTING focused Godot fixture suites `level_factory/tests/factory_studio_r05_r05_loaded_batch_ui_suite.gd` and/or `level_factory/tests/factory_studio_r09_r02_r04_r03_batch_ui_binding_suite.gd` in place. Synthetic, in-memory gateway responses must cover:
1. Present `batch=null` with `NO_MATCHING_COMPOSITE`: no Nil type error, no job starts, no mutation, proper empty/read-only state.
2. Present `batch=null` with ambiguous/mismatch disposition: no Nil error, provenance warning and resume/retry BLOCKED.
3. Valid composite with `job=null` for `NO_MATCHING_JOB`: no Nil error, no fake READY/job ID or background operation.
4. Valid composite and `job=null` for `BATCH_JOB_SOURCE_MISMATCH`: mismatch state authoritative and blocked.
5. Valid composite and valid saved job: previous preserved READY and counts/Resume behavior stays semantically identical.
6. Exactly targeted malformed nested optional payload where needed, and repeat fresh/open loaded restore. No full 140 PNG import, game solver, actual production, owner data read/write, CI.
Only run locally bounded existing Godot tests if they generate **no new unapproved persistent caches, TEMP folders or evidence files**. Otherwise static/source plus zero-disk test and mark actual Godot NOT RUN. Parser/build and `git diff --check` if safe. Do not revisit previously green eight-buttons/layout/full suite without a real regression.

## PHASE III | Publish and safe existing installed Release overlay

The installed R04 controller SHA is builder reported as `e0a44647f5e54d9b18ca76cf50d8582be41e36bacc6f5400229cc777bfd0b9c2`, manifest SHA `56c9f32518fe01b2354942600c8d19662cab0713a23b42551304fccfbc0493eb`; 2,316 managed files, nine overlayPaths and one provenance overlayReceipts record. Existing tracked `scripts/install_factory_studio_ui_overlay.ps1` is baseline-pinned and refuses second apply on this new manifest. **DO NOT rerun old -Apply or full 2,331-file installer.**

In this SAME milestone, carefully extend the EXISTING tracked tiny updater (no second installer) for exactly one new versioned UI controller update with:
- default read-only preflight, explicit one-controller/manifest apply, strict current R04 baseline controller+manifest hashes checked afresh, published source Git SHA/clean state and owner approved overlay entry, unchanged other 2,315 managed hashes, preserved old sourceRevision/baseRevision/installationMode/nine overlayPaths and first overlay receipt; APPEND the new source-provenance receipt, not erase/relabel old 2,315.
- Exact no-reparse/junction, installed process absent and non-ambiguous BEFORE EVERY write; do not ask the user to prove previous X-click again. As of the owner's AFTER screenshot Studio is RUNNING; **do not hot patch or force-close**. Continue all safe coding/testing/read-only game readiness while waiting. If still running when installation would begin, mark `INSTALL AWAITING OWNER NORMAL CLOSE` and stop **only installation**, handing user one concise request.
- Bounded exact two new prior-controller/manifest rollback copies for this second upgrade, no new backup folders or OS TEMP, no hidden heavy copies. R04 two rollback copies are still needed until new installed startup is safely accepted. Distinguish original R04 and new bounded recovery copies; preserve/verify before and after. No shortcut/launcher/project, owner PNG/job files/Pool or unrelated installed content write.
- Guard standalone `-Rollback` with fresh exact installed process and path/reparse/manifest checks BEFORE any write (known R04 audit finding); no automatic rollback or unrequested running-app writes. Fail closed on unexpected hash/policy denial. No third stage leftovers. **Only update Release if preflight AND tests PASS**, otherwise leave current visually accepted R04 installed page intact.
- After publishing source/updater and bounded tests to normal GitHub main, run read-only preflight, install via explicit supported apply **only if app is naturally closed and all provenance/hashes match**. Never launch Studio or simulate owner visual PASS. If installed, report exact old/new manifest SHA and source controller SHA and no unrelated changed files; owner manually reopens existing shortcut and shares actual startup console result and/or one screenshot. Release Pool layout acceptance should remain valid.

## PHASE IV | Post-install owner verification, housekeeping and R05 forward readiness

When owner genuine AFTER startup shows no Nil-to-Dictionary error and accepts app behavior, independently log runtime startup PASS/FAIL as owner evidence. No screenshot/console result means `OWNER STARTUP NOT VERIFIED`, NOT full milestone closure. **Do not create a separate prompt at each intermediate milestone checkpoint.**

Once successful current startup acceptance and hash/receipt proof exist, execute a *separately verified exact-path, no-policy-bypass cleanup* of ONLY now-unneeded R04 and new task-created rollback copies (each with logged SHA/path/bytes), if rollback no longer necessary; never delete earlier if latest startup still fails. No permanent generated test caches/stage clones, no broad clean, no retry of previously policy-denied scratch, measure disk delta. Report actual disk files kept/removed; avoid falsely asserting the old 3,220 untracked count was unchanged after authorized prior cleanup.

Using current source evidence **read-only**, produce concise honest next R05 real-game readiness matrix: pinned 232-file minimal game `aef60a616d4ac401e9dfac15df6fe56e671c0053` vs live `Sekiph82/Scrubbots` remote HEAD (look up freshly; builder prior local 74 vs GPT remote 75 commits delta may be stale), actual authoritative game rules, current 002 ACCEPT/Pool, nine saved READY 4/4/1, Difficulty/load-check/replay WIN, full CPX-002, installed Studio success, 19 deselections/19 skips/six ignored modules, creator provenance/NTFS race-free proof. Classify `SOURCE VERIFIED`, `SAVED HISTORICAL`, `PHYSICAL OWNER PASS`, `NOT RUN/BLOCKED`. Identify one bounded safe next full-game proof requiring any explicit owner approval, **but do not run production, new game solver, bulk batch or CPX-002 without owner authorization**.

## One milestone handoff
Post one chronological builder log and exact published commit/source SHA, table of completed phases, tests PASS/NOT RUN, genuine installed status, two-backup disposition, disk byte delta, owner-only action if any, and next full-game gate. Local HEAD/origin/main parity, tracked clean and owner untracked accounting required, no GitHub Actions/CI. Parent R05 GAME/PRODUCTION remains OPEN until real current game/native evidence and owner authority are obtained. The current user specifically requests a SINGLE milestone master covering this whole sequence. **Do not stop for artificial micro-task approvals or repeated prompts.**
