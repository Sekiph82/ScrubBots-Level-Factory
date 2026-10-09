# SB-LFX-018-C001-R02-R03 — Preserve R02-R02 Work, Add Alpix Production + READY Auto Pool
Document role: CODEX BUILDER LOG

## 2026-10-09 — continuation preflight

- Starting execution root: `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\SB-LFX-018-C001-R02-EXACT-THREE-MASTER`.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`; origin is `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; execution branch is detached HEAD.
- Before the R03 authority fetch, execution HEAD was `b396a8fafa454ba6670a318ca761f17d1efad1ea`, following the R02 remote advancement and normal merge. `git fetch --prune origin` advanced `origin/main` from `0387916e7ab6907919e9351ab57a8a654660e9d0` to `cdf8dba0998fadf667140a8b08c47a3bb419b53b` (nine commits). No reset, rebase, auto-stash, or clean was used.
- Persistent Desktop `main` and all other registered TEMP worktrees were inspected and left untouched. Existing named stashes were inventoried and left untouched.
- R02 in-progress status before R03: modified `factory_core_gateway.gd`, `factory_core_launcher.py`, `factory_studio_exact_ui.gd`, `scrubbots_publish_handoff.py`, two R02 test files; new R02 binding test and R02 builder log; Godot-generated untracked `.gd.uid` files; Godot changed the unrelated icon `.import` descriptor's line endings. These are preserved pending a safe checkpoint/reconciliation.
- R03 starts from the existing R02 implementation, not a rewrite. No R03 product changes have started.

## KEEP / ADAPT / ADD matrix

| Disposition | Existing or required work |
|---|---|
| KEEP | Commit `8b2f7eb95e804a739d631dd3c2f052f4b51983d9` exact three-master UI, owner visual lock, runtime master assets, launch/install path and exact screenshot harness. |
| KEEP | Useful R02 uncommitted canonical control bindings and tests; preserve and reconcile before continuing. |
| ADAPT | Provider selector and single/CSV generation to owner prompt/size/provider requests; add truthful ALPIX (Claude subscription + installed Alpix plugin) and MAGNIFIC routing; retain PixelLab only through its real configured adapter. |
| ADAPT | Existing CSV and per-row workflow to preserve legacy request semantics, hash job identity, durable row states, LIMIT pause and resume from first incomplete row. |
| ADAPT | Single/multiple/external PNG intake to use one canonical pipeline with exact per-source artifact identity and automatic-order rules. |
| ADAPT | READY pool eligibility: READY auto-includes; Accept restores/includes; Reject excludes/quarantines; Publish stays the explicit final human gate. |
| ADD | Alpix capability discovery from the actual local Claude configuration/CLI without guessed tool names or API-key/web-UI fallback. |
| ADD | Focused permanent R03 tests for provider routing, resumable CSV/job state, external multi-PNG binding, ordering, READY inclusion/exclusion, and no automatic publish. |

## Read set and work notes

- Active prompt: `.hiveai/prompts/SB-LFX-018-C001-R02-R03_ALPIX_AUTO_POOL_CONTINUATION_PROMPT.md`.
- Required live task authority and contracts: root `TASKS.md`; `AGENTS.md`; `GOVERNANCE.md`; `.hiveai/audit-criteria/SB-LFX-018-C001-R02-R03_ALPIX_AUTO_POOL_CONTINUATION_AUDIT_CRITERIA.md`; `docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md`; `docs/decisions/OWNER_PIXEL_ART_ALPIX_READY_AUTO_POOL_V01.md`; `docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`; `docs/product/FACTORY_STUDIO_LEGACY_EXE_PIXEL_ART_BEHAVIOR_V01.md`; prior R02 strict audit and visual-master/index contracts; `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`.
- All implementation, focused/full tests, runtime verification, exact screenshots, install/shortcut proof, commits, and publication will be appended chronologically below. Builder evidence is not independent acceptance.

### R03 authority reconciliation and local capability discovery

- R02 local implementation checkpoint: `ea1550c` (`checkpoint: preserve R02 exact UI control bindings`). This preserves the six tracked source/test changes plus the new R02 control-binding test before synchronization.
- Reconciled with current fetched `origin/main` by normal merge `7a82d549711946f597dc748897f45725e56a026a`; no conflict, reset, rebase, or stash. Remote `origin/main` at merge time: `cdf8dba0998fadf667140a8b08c47a3bb419b53b`.
- Read the full R03 prompt, audit criteria, owner workflow V04, owner decision, bindings V02, legacy EXE behavior reference, current TASKS, AGENTS, GOVERNANCE, visual-master contracts, and sync/publish standard. V02 supersedes prior V01 runtime bindings.
- Claude Code CLI discovery: installed at `C:\Users\sekip\.local\bin\claude.exe`, version `2.1.287`. The local `.claude/settings.json` enabled plugin IDs and `.claude/plugins/installed_plugins.json` installed plugin IDs contain no Alpix plugin. No Anthropic credential files were read. The implementation will keep ALPIX selectable but report unavailable, preserve pending job rows, and never use API-key or alternate-provider fallback.
- R03 implementation is in progress; no audit or acceptance claim is made.

### R03 implementation delta and first focused run

- Added a local Claude Code Alpix adapter that reads only enabled plugin IDs, installed plugin manifests, and their MCP server names; removes `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` from child environment; validates exact PNG size; and reports usage limits distinctly. Real local configuration currently has no Alpix plugin, so no real image request was executed.
- Added CSV-SHA `ArtJob` persistence with legacy prompt/semicolon/named-column/size parsing, atomic state writes, PENDING/DRAWN/VALIDATED/IMPORTED/FAILED/LIMIT states, restart recovery and validated-artifact preservation. LIMIT and unavailable capability leave the current row resumable.
- Extended provider selection to ALPIX (Claude), MAGNIFIC and PIXELLAB. Magnific delegates to the existing prepare/import adapter and is clearly not reported as direct image generation. PixelLab continues through its existing direct provider registry/secret boundary.
- Changed canonical Release Pool eligibility so true READY pipelines auto-enter; append-only owner REJECT excludes; owner ACCEPT restores. No publish operation is called by inclusion/review.
- First focused command: `python -m pytest tests/unit/test_sb_lfx_018_r03_alpix_auto_pool.py tests/unit/test_sb_lfx_018_c001_r02_exact_three_master_ui.py tests/unit/test_sb_lfx_018_c001_r02_master_control_bindings.py tests/unit/test_sb_lfx_006_candidate_review.py tests/unit/test_sb_cpx_004_scrubbots_publish.py -q` -> `2 failed, 32 passed in 3.26s`. Failures: fixture discovery used global PATH ahead of explicit fixture home; static test incorrectly rejected the contract-permitted credential-availability label. Both are corrected; rerun pending.

### R03 follow-up corrections and complete regression

- Re-ran the focused R03/R02/Candidate Review/Publisher command after provider, UI and recovery changes: `python -m pytest tests/unit/test_sb_lfx_018_r03_alpix_auto_pool.py tests/unit/test_sb_lfx_018_c001_r02_exact_three_master_ui.py tests/unit/test_sb_lfx_018_c001_r02_master_control_bindings.py tests/unit/test_sb_lfx_006_candidate_review.py tests/unit/test_sb_cpx_004_scrubbots_publish.py -q` -> `36 passed`.
- Extended focused coverage for Magnific's existing prepare-only adapter, automatic numbering display, and fail-closed Production. The adapter needed an explicit registered model; the default transparent-background request remains rejected by the adapter as unsupported, while supported background requests return `PREPARED_FOR_EXTERNAL_EXECUTION`.
- The first complete regression without explicit `SCRUBBOTS_PROJECT`: `python -m pytest -q` -> `26 failed, 1722 passed, 20 skipped, 3 errors in 1221.55s`. Evidence found two code/test issues and one missing environment authority: GDScript declared both a variable and function named `_manage_release_selection`; the UI directly inspected PIXELLAB secret status; the runtime test's old broad launcher scans assumed no provider adapters. Corrected the variable name, removed secret-status inspection from the UI, and scoped static tests to the Godot local runtime and the exact dashboard read-only functions.
- The first Godot runtime-suite child stayed blocked after that parse error; after confirming it was `godot --headless --path level_factory --script res://tests/factory_studio_runtime_suite.gd` launched by this pytest process, stopped only that exact child so pytest could finish. No unrelated Godot process was stopped.
- Created a dedicated temporary current-game authority at `%TEMP%\ScrubBots-Level-Factory\SB-LFX-018-C001-R02-R03-GAME-AUTHORITY` because pytest deletes its per-test clone. Verified origin `https://github.com/Sekiph82/Scrubbots.git`, fetched shallow `main` at `44c53a6da0aea1172b1f900c095b7bf20852a541`, detached HEAD to `origin/main`, and verified clean status. Did not inspect or modify the Desktop game checkout.
- Exact capability probe: `GameRules(..., column_count=3).void_capability()` -> `CLOSED / UNAVAILABLE`, reason `Current ScrubBots main does not contain the audited VOID implementation.` The LF19 topology and READY-pipeline tests therefore remain unable to pass against the current canonical game authority. No alternate branch, fixture, or claimed READY result was substituted.
- Final complete regression with `SCRUBBOTS_PROJECT` set to that verified detached TEMP authority: `python -m pytest -q` -> `1758 passed, 7 failed, 6 skipped in 1264.99s`. The seven failures are exactly `tests/integration/test_sb_lfx_019_void_game_parity.py`: corridor screening; five topology cases (ring, enclosed-hole, border-touching, void-row-column, corridor); transparent owner fixture READY pipeline. All fail at the unavailable audited VOID game capability, not at the R03 Alpix/pool tests.
- Post-change focused UI/provider/security-boundary gates: `python -m pytest ... -q` -> `40 passed in 12.43s`; includes Alpix resume/job identity/API-key exclusion, Magnific contract, provider availability, auto-pool/reject/restore/no-publish, exact masters, R02 bindings, plus project-local no-network/no-credential-marker checks.
- Affected Godot owner UI integration group after the GDScript parser fix: `51 passed, 2 failed in 60.61s`; the two stale static assertions were narrowed to the actual offline Godot runtime and the read-only dashboard function boundaries. Final full run then reported only the seven current-game VOID capability failures.
- Final static/runtime commands: `python -m compileall -q src scripts level_factory/scripts` exit 0; `godot --headless --editor --path level_factory --quit` exit 0 on Godot 4.7.2; `godot --headless --path level_factory --quit-after 5` exit 0; `git diff --check` exit 0 (Git emitted only configured LF/CRLF working-copy warnings).
- Production promotion remains fail-closed in the UI because this repository's trusted exact verified-STAGING owner-approval promotion operation is not connected; staging remains through the existing publisher handoff. No UI action claims R2/PRODUCTION mutation. No Alpix plugin is installed locally, so no paid/API fallback or real provider image was attempted.
- No `TASKS.md`, `.hiveai/HANDOFF.md`, prompt, audit, or owner master was edited. No dependency/license files were changed.
- Remaining before publication: append final diff/status/commit/push/runtime-install evidence below. This builder log does not declare independent acceptance; current-game VOID authority remains an explicit audit blocker.

### R03 product commit and pre-publication state

- Final implementation diff was reviewed and staged separately from evidence. `git diff --cached --stat`: 10 paths, 828 insertions, 92 deletions; `git diff --cached --check` passed. Product commit: `5b975a92532b9df1e781c96cb1de37dbba73aa6e` (`Implement Alpix continuation and READY auto-pool`).
- Final verification summary: focused provider/UI/security tests `40 passed`; full regression `1758 passed, 7 failed, 6 skipped`; the seven failures are exclusively LF19 VOID parity/READY cases blocked by canonical ScrubBots main at `44c53a6da0aea1172b1f900c095b7bf20852a541`, which reports `CLOSED / UNAVAILABLE` for audited VOID. `compileall`, Godot editor parse, Godot headless startup, and whitespace checks passed.
- Final tracked product diff contains the adapter, provider routing, READY Release Pool eligibility, UI bindings, and focused tests listed above. No dependency/license changes; no secrets or forbidden control-plane/audit/task-state paths changed. Local Alpix plugin is absent, and the Production promotion action remains fail-closed without its trusted verified-STAGING owner-approval operation.
- Pre-publication fetch: origin remains canonical. `origin/main` is `cdf8dba0998fadf667140a8b08c47a3bb419b53b`; detached HEAD `5b975a92532b9df1e781c96cb1de37dbba73aa6e` is five commits ahead, zero behind, and `origin/main` is an ancestor of HEAD. The five commits are the retained master-render fix, safe reconciliation/checkpoint commits, and this R03 product commit. No force, reset, rebase, clean, or stash was used.
- At this point only the two builder logs are untracked; no product files remain unstaged. The existing R02 builder log is preserved unchanged. Next: evidence-only commit, normal fast-forward push, guarded runtime installation, shortcut verification, and final publication/status evidence.

### Published runtime install and shortcut verification

- Normal fast-forward publication succeeded: `git push origin HEAD:main` advanced `main` from `cdf8dba0998fadf667140a8b08c47a3bb419b53b` to `da6442a1f6fa338122702d6a00c864fc8120d466`; six commits ahead at publication time. No force push.
- Ran `scripts/install_factory_studio_shortcut.ps1` from the clean published canonical checkout. It completed and installed 2,074 manifest-managed files to `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`. Manifest revision `da6442a1f6fa338122702d6a00c864fc8120d466`; SHA-256 checks for the Alpix adapter, exact UI script, and launcher all match their manifest entries.
- Verified `C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk` exists and targets Windows PowerShell with `-File` set to the installed `scripts\launch_factory_studio.ps1`; working directory and owner icon both point inside the installed runtime. The shortcut launches the stable launcher path directly.
- Installer changed no project checkout files. Preparing the final evidence-only update and will republish it separately, then rerun the guarded installer so the runtime manifest matches the final published HEAD. The prior R02 log remains unchanged.
