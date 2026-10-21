# SB-LFX-018 R05 M03 | EXECUTION UNBLOCK + REAL OWNER-002 NATIVE REPLAY | UNRESTRICTED ENGINEERING MASTER V02
Document role: GPT AUTHORIZED CODEX BUILDER PROMPT
Date: 2026-10-21 Europe/Istanbul
Task: **SB-LFX-018 R05 V13-C/D R05 — INSTALLER OUTCOME VISIBILITY INTEGRATION REMEDIATION**
Same active milestone/cycle; do not restart prior R01-R04 source work or 140 PNG batch.
Canonical GitHub repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Canonical local checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Single tracker: `TASKS.md` in root, GPT-owned.
Immediate independent R04 audit V19: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R04_TRANSACTION_OUTCOME_STRICT_AUDIT_V19.md
Current R04 source commit: `a6e1484154f47668d2ce63fe98478ac30acbc074`; log commit: `f709b45abe0f0c7c052c080b0ecdb3ec6fbc28a2`.

## Task 0, MANDATORY FIRST: safe GitHub to local synchronization

Read the full linked GitHub prompt, current root TASKS.md, AGENTS.md, GOVERNANCE.md, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, V19 audit and existing chronological R05-M03 builder log. Before *any* source edits: verify exact canonical root, origin, Git branch, HEAD, `origin/main`, git status, 3,002 owner-untracked paths (count may vary), stashes and worktrees. Fetch/prune then safely fast-forward the canonical Desktop checkout to current `origin/main` **ONLY when the tracked state and owner files make FF safe**. Preserve all owner bytes and stashes; no reset/clean/rebase/autostash/forced merge, no clones, TEMP/worktree, new Desktop copies or generated scratch. The R04 log admits a briefly created worktree before reading its prohibition; do not repeat. If safe FF is impossible, leave files intact, report exact blocker and proceed only with read-only evidence if feasible. GitHub main is task/prompt authority; do not discover another local repo.

## Owner safety/cost locks

ZERO GitHub Actions/CI/hosted runners, provider paid calls or quota probing, PixelLab credits, R2, staging, production, 140-image job retries/resume, owner PNG edits, installed Release file/manifest edits, native Godot project/cache writes, Windows active worker kills. Do not run installer `-Apply`. No broad installer, no shadow Release, no test-generated TEMP/cache/worktree. No change to GPT-owned TASKS.md, audits, used prompts, HANDOFF, workflow, or historical log sections. Existing 140 COMPLETE = 102 READY, 4 FAILED, 34 REJECTED, 0 pending; existing Pool 131 JSON is a count, not a READY claim.

## R05-F01 BLOCKER: actual production installer suppresses outcome output

V19 independently inspected real GitHub source. R04 added `ConvertTo-ScopedOverlayOutcome` and `Write-ScopedOverlayOutcome`, but real script `scripts/install_factory_studio_scoped_overlay.ps1` invokes output function with `[void](Write-ScopedOverlayOutcome ...)` at:
- no-op branch (around existing source line 177);
- completion branch (around line 203).
PowerShell `[void](...)` discards *all* stdout pipeline output. Thus production installer does NOT emit visible JSON, human text or object for `NO_OP`, `COMMITTED` or `COMMITTED_CLEANUP_PENDING`, despite R04 test exercising helper independently.

Make **minimal** production call-site change and, if necessary, narrow formatter improvements so actual installer exposes a single unambiguous machine-readable normalized status plus visible operator-friendly text for all three success/no-op cases. `COMMITTED_CLEANUP_PENDING` must include preserved evidence directory and error, without pretending install rolled back. Do not duplicate or corrupt JSON. Fail-closed exceptions must continue to have non-success exit semantics and never be normalized as COMMITTED. Do not weaken checks for manifest/source/installed hash, configured allowlist, receipt ownership, process snapshot or writer exclusion, and do not mark real installation ready.

## R05-F02: test **production integration**, not just helper

Extend existing `tests/unit/test_scoped_overlay_transaction.ps1` and/or the focused `tests/unit/test_scoped_overlay_manifest_drift_contract.py` to:
1. Assert that **both actual installer call sites** preserve output and cannot contain `[void](Write-ScopedOverlayOutcome ...)` (prefer PowerShell AST/call-site review if possible, source contract acceptable *in addition* to executable helper checks).
2. Capture function output for synthetic `COMMITTED`, `COMMITTED_CLEANUP_PENDING`, `NO_OP`; verify exact parseable JSON status, scoped paths/SHA values, protected evidence/reason and operator string; avoid generating owner disk files.
3. Verify unexpected/rollback failures still throw; `INSTALL_BLOCKED_MANIFEST_DRIFT` + `PROCESS_QUIESCENCE_UNPROVEN` continue refusing replacement. No new test fixtures touching Release/Owner assets.
4. Show unchanged R04 pre-replacement snapshot logic and 140 original batch/Pool boundaries.

Do bounded local non-cache PowerShell parser and in-memory harness, Python `-B` focused contract tests, and `git diff --check`. Report real failures and corrections chronologically. If live PowerShell cannot be executed, record NOT RUN, not PASS. Don't rerun unrelated full suite.

## R05 completion boundary and publication

Only source-level R04 output integration can close here. Keep `verify.py` exactly as-is: installed bytes still have no approved receipt; prospective R04 decision packet is **not** permission to apply, to forge historical receipts or auto-approve `90e560...`. Real owner exclusive writer lock absent, native Godot protected UID/import/cache risk OPEN, installed three-screen GUI OPEN, physical rollback UNVERIFIED. This task does **not** ask owner to authorize migration.

Append truthful new R05 section to existing:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`
with start/end HEAD, status, changes, test counts, no-write proof and open gates. Commit source/tests and append-only builder evidence separately if practical. Verify workflow manual-only, `git fetch --prune origin`, require nondivergent ancestor, **normal** `git push origin HEAD:main`, fetch again and verify `HEAD == origin/main`, 0/0, clean tracked state. Never force/rebase or stage 3,002 owner-untracked items.

Return compact coded result `R05_OUTPUT_VISIBILITY_SOURCE_PASS` or exact FAIL, `INSTALL_BLOCKED_MANIFEST_DRIFT`, `PROCESS_QUIESCENCE_UNPROVEN`, `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK`, `INSTALLED_GUI_OPEN`, commit SHAs and full existing GitHub builder-log URL. Codex must NOT edit TASKS.md/independent audit or pronounce milestone accepted; GPT will independently audit R05.
