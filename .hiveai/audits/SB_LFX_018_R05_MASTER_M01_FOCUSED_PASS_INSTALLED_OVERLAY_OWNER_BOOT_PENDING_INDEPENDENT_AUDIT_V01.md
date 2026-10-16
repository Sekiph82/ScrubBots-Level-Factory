# SB-LFX-018 R05 | M01 GPT independent focused regression and installed-overlay evidence audit V01

Date: 2026-10-16 Europe/Istanbul
Repo: `Sekiph82/ScrubBots-Level-Factory`
Builder published GitHub main: `f0e3198f7e6529cdf99842ac2ef582b04e757d09`
Previous GPT commit `89ee6b1ab7a536d525c7daf6c7ba2bd470963f59`
Test-only commit `e67846e2c485a5b0e17b3de513f413d9921778c5`
**VERDICT: M01 FOCUSED GODOT RED->GREEN SOURCE/BUILDER EVIDENCE PASS; SCOPED UI INSTALL BUILDER HASH-VERIFIED; OWNER INSTALLED STARTUP SMOKE OPEN; FULL M01 OWNER GATE/PARENT R05 GAME-PRODUCTION NOT CLOSED.**

## Independent GitHub source and history audit
GPT fetched actual `main` and compared `89ee6b1a..f0e3198f`. Exactly three normal descendant commits: focused fixture change `e67846e2`, builder log `efcf9296`, final log receipt `f0e3198f`. Only **one existing test file** `level_factory/tests/factory_studio_r05_r05_loaded_batch_ui_suite.gd` and the established chronological builder log changed. Product `level_factory/scripts/factory_studio_exact_ui.gd` and narrow `scripts/install_factory_studio_ui_overlay.ps1` were **unchanged** in this turn. GitHub `.github/workflows` zero modifications; NO CI/Actions. No new user art or game files in the remote diff.

The updated test builds nine synthetic owner-upload identifiers (bounded signed int formatting), supplies source and record SHA fields matching the in-memory loaded/composite/job records, and preserves `planned_quotas={3:4,4:4,5:1}`. It explicitly sets selected `_activity_source_id` to the ninth source and confirms `_batch_job_matches_loaded_sources()`. It asserts only selected `BatchResult_008` is displayed with source-bound FAILED status, attempt/reason, source SHA and record SHA, and eight unselected result rows do **not** leak into the selected-source activity panel. It mutates either SHA in the synthetic copied job to `"0".repeat(64)` and requires fail-closed: no verified source match, no activity row. The preexisting nullable `batch/job`, ambiguous/lineage refusal, valid paused job and five-card/resize checks remain. This aligns with the independently inspected real controller `_render_batch_item_results` selected-source/explicit-forced behavior. Crucially, no production SHA/provenance validation was relaxed to green the test.

Builder reports the following local test history:
- Known-good unchanged Godot R07 control suite PASS using **actual absolute Godot 4.7.2 executable**, bounded asynchronous in-memory stdout and stderr.
- Previous R05 suite RED with nine outdated expected rows/global quota tooltip; corrected test briefly RED twice due synthetic ID formatting and mock source-scope capture, then fixed.
- Final actual focused R05 run: exit **0**, elapsed **470 ms**, final literal suite-printed `SB-LFX-018-C001-R02-R05-R09-R02-R04-R05 loaded PNG batch UI PASS`; stderr empty, no Godot SCRIPT ERROR. Actual Git blob `eedc12cfc8a142d9cc848b440fc7e5539a04a3d6`. **GPT inspected the code and original builder log, did not personally execute local Windows Godot.**

## Safe installed controller evidence, not owner boot
Builder used the already published existing updater after genuine focused suite green. Windows PowerShell **5.1** read-only launch was not compatible with its inline C# process-check expression syntax and generated a transient compiler scratch `...Temp/...cs`; builder reported scratch absent on later check. The same existing updater **PowerShell 7.6.5** read-only preflight passed. Future runs should use supported PowerShell 7 rather than repeatedly creating compiler scratch with 5.1. No CI/cloud.

After explicit `-Apply`, builder reported:
- Installed UI controller SHA256 **`11d3f59f3340df98c566d30fbf9d9ec304fbc18929c8695f9a89a37c823669da`**, equal to published source (startup nullable fix).
- Updated installed manifest SHA256 **`94c6f6b51dc28e1c1208e04146f0573760ca6af03114657cff0e7b0b9a7a6ec7`**; all **2,316** managed files retained, **nine** authorized overlay paths, **two** append-only receipts (old R04 + current M01). Unchanged original `baseRevision/sourceRevision/installationMode`, unchanged **other 2,315** managed path/SHA values; no shortcut/launcher/project/icon edits.
- Fresh exact installed Studio process check returned zero before updates; unrelated Godot headless process was not stopped. Source/app installed paths and old PNG/READY review objects unchanged per builder evidence. **GPT cannot directly hash the owner's Windows installed files or prove process state through GitHub.**
- Four recovery files retained until owner startup smoke success: R04 controller **195,392 B** + manifest **454,775 B**; M01 controller **197,118 B** + manifest **455,309 B**, **1,302,594 B total (~1.30 MB)**. Their original hashes and names were logged; do not delete/rollback automatically while boot is unverified.
- Local Git clean synced state `HEAD=origin/main=f0e3198f...` 0/0 and 2,968 preexisting + **two newly untracked M01 recovery paths** (2,970 total) are builder-reported. Existing 16 previously policy-deletion-blocked scratch files remain protected. `level_factory/.godot` cache remained 273 files/1,976,086 bytes; no new persistent test artifact claimed.

## Read-only game gate
Builder refreshed remote `Sekiph82/Scrubbots` HEAD at `f96e7cd39928d1fbc9981559c613b2d6cc1cd8f3` while pinned minimal runtime remains `aef60a616d4ac401e9dfac15df6fe56e671c0053`. Live full game/CPX-002, current-main solve/replay WIN/Difficulty/load-check, owner source bytes, R2/PRODUCTION are **NOT RUN**, irrespective of historical saved 002 ACCEPT and nine READY 4/4/1; 19 historical deselections, 19 skips, six ignored modules remain unwaived. Authentic upstream AI artist and real native NTFS handle/race proof remain OPEN.

## Exact gate now due
**Do not create another coding micro-task for a green test.** Owner must manually open **existing Desktop ScrubBots Factory Studio shortcut**, observe full startup and report whether the prior `SCRIPT ERROR Trying to assign value of type 'Nil' to a variable of type 'Dictionary'` (previously line 1234) is absent, and whether the three tabs/display continue functioning. Capture terminal error text/screenshot if any; no solver, Run Entire Loaded Batch (140), acceptance, release/upload/preflight or publication. **This owner visual/native startup acceptance is genuinely unresolved until user replies.** On a clean report, close M01 owner's startup gate and only then plan exact-path safely authorized cleanup of four R04/M01 recoveries with file-identity/hash/process checks, not an unrestricted disk clean or policy workaround. Further R05 current-game proof needs separate explicit resource authorization. If startup fails, retain all four recoveries and continue SAME master with exact error evidence.
