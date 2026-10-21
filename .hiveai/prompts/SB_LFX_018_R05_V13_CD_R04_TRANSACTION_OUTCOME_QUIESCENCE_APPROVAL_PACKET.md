# SB-LFX-018 R05 M03 | EXECUTION UNBLOCK + REAL OWNER-002 NATIVE REPLAY | UNRESTRICTED ENGINEERING MASTER V02
Document role: GPT AUTHORIZED CODEX BUILDER PROMPT
Date: 2026-10-21 (Europe/Istanbul)
Scope: **R04 continuation only** of active R05 V13-C/D. Do not rerun prior V13-A/B/C/D implementation, R02/R03 tests unchanged, 140 batch, old installer work or previous prompts.
Canonical GitHub: https://github.com/Sekiph82/ScrubBots-Level-Factory
Canonical persistent checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Canonical task tracker: root `TASKS.md`.
Immediate independent audit V18: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R03_ROLLBACK_AND_INSTALL_AUTHORITY_STRICT_AUDIT_V18.md
Prior R03 source commit `e08f3fc8167baf8ba44d213ae9b0840698d2f33f`, final builder receipt `7b12ff2e12924396b1dd7701b5b4af94de5e03d7`.

## Critical boundaries

Before edits, read root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, V18 strict audit, R03 prompt, current installer/module/tests and existing M03 builder log. First confirm canonical GitHub branch, origin, fetch, HEAD parity, owner untracked files/stashes, safe fast-forward-only policy. Owner-restricted Desktop only: **no clone, new worktree, TEMP tree/scratch, extracted project, alternate user profile, broad install, forced sync, reset/clean, autostash or rebase**. If blocked, preserve files, perform read-only source/evidence work and record exact blocker; no fabricated exceptions.

**Zero Actions/CI/hosted runner/billable API/PixelLab/Claude quota probe/R2/staging/production/140 re-run or selective image retries.** No owner source PNGs, original COMPLETE job, Pool, Release application files, protected Godot .uid/.import/cache, or installed manifest mutations. Never stop/kill live Studio/worker. Do not edit root TASKS.md, GPT audits, used prompts, HANDOFF, workflow or prior builder log history. Append chronological content only to SAME M03 builder log; source/tests and log separately committed when practical. No new milestone.

## R04-A: cleanup-pending result must be observable (V18 R03-F05)

Inspect the already-published `scripts/scoped_overlay_transaction.psm1` and `scripts/install_factory_studio_scoped_overlay.ps1`; keep the R03 rollback module and exact SHA/receipt/allowlist guards intact.

The module may return `COMMITTED_CLEANUP_PENDING` if post-commit transaction-directory cleanup fails. The wrapper currently prints only `COMMITTED`; silent exit on pending cleanup is not acceptable.

Implement exact, machine-readable and human-visible propagation of:
- `COMMITTED` with exact installed scope and verified hashes;
- `COMMITTED_CLEANUP_PENDING` with exact transactionRoot, error reason, no automatic dangerous cleanup/rollback, explicit preserved evidence path and operator-safe next action;
- `NO_OP`, distinct from a changed install;
- fail-closed transaction exceptions including `TRANSACTION_FAILED_ROLLBACK_INCOMPLETE`; never downgrade errors into success.

Do not introduce a second installation entrypoint. Add focused unit tests that **execute** wrapper-outcome mapping with synthetic results, not just search for source strings; no writing to owner Release.

## R04-B: process-quiescence race and fail-closed handling (V18 R03-F06)

The R03 `Get-ScopedProcessInventoryState` helper gives a bounded preflight snapshot but cannot by itself prohibit a worker starting later. Define an honest, narrow policy for planned `-Apply`:
- immediately before first owner-target replacement, take a **fresh** bounded full process identity + executable/command-line/parent/descendants reading using the same module helper, and deny on any inaccessible/missing necessary fields or exact Release runtime writer;
- identify any potential TOCTOU period remaining after that recheck. Where exclusive-writer control cannot be established without owner-state mutation or unauthorized locking, report `PROCESS_QUIESCENCE_UNPROVEN` rather than claiming exclusive access;
- add synthetic process tests where a worker appears *between* plan/pre-stage and replacement, including child PID, CIM error, incomplete metadata and unchanged target proof. Do not start, terminate, suspend, attach to or probe live worker in R04.
- keep target prior SHA verification immediately before changes. Never rely only on stale PIDs or changed process names.

Any design needing an owner process lock, additional files in Release or privileged OS control must remain preview-only until explicitly authorized. **Do not run `-Apply`** in this task; `verify.py` manifest authority still blocks it.

## R04-C: explicit prospective manifest migration decision packet, no retroactive approval

Prepare a clear, bounded **read-only decision packet** stored as a new markdown source document in the existing repository `docs/process/` (not a new tracker). Include:
- installed `verify.py` manifest expected SHA `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2`;
- installed SHA `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744`;
- R03 source SHA `151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3`, rehash current source if head changes;
- original `verify.py` absence of exact overlay/receipt in six manifests is **builder-reported**; exact local observations to be revalidated read-only, no silently trusted stale numbers;
- eight previously planned changes, three overlay additions, code/source ABI/dependency closure and exact file+SHA matrix. Enumerate from a fresh read-only preflight, not assumptions;
- rollback evidence (in-memory tested, physical NOT verified), active process boundary, Godot cache/UID mutation risk, owner job/Pool baselines and three-screen acceptance proof;
- two distinct owner choices: keep existing install unchanged and accept continued block, or **prospectively** authorize an exact controlled manifest migration after explicit review of scope/safety. A prospective approval must never be presented as an old receipt, and does not alone waive mandatory native/process gates.

No manifest rewrite, hash auto-trust, file copy, new release approval, native execution or receipt fabrication. Do not solicit provider credentials or source PNG uploads.

## R04-D: native Godot and installed GUI

Read-only identify any viable owner-safe Godot 4.7.2 parser/test path with no writes to original project, `.godot`, `.uid`, `.import`, AppData or owner Release. The standing no-TEMP/no-clone rule is binding. If impossible, record `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK` plus exact blocked options. Do not launch native test, install or open GUI to force completion. Real 240→480 PID/child and 3-screen screenshot acceptance remain OPEN. No fictional smoke PASS.

## R04-E: tests, evidence and publication

Focused bounded local tests only, using canonical Desktop source and `pwsh -NoProfile` in-memory adapter without filesystem fixture; Python `-B`, `-p no:cacheprovider`, no Actions. PowerShell AST parse; `git diff --check`; state test counts and any failed retries. Check dependency scope, zero immutable job/Pool changes, and report explicit limitations. If no new safe production fix is justified, publish packet/evidence only, not an artificial code diff.

Normal fast-forward-only push after verifying manual-only workflow, remote ancestry and clean scoped tracked status. No rebase/force/merge or staging owner untracked Release. Re-fetch and report final remote SHA and 0 ahead/behind. Publish log in existing `.hiveai/codex-logs/SB-LFX-018-R05-M03_NATIVE_002_REPLAY_COMPLETE_V02_CODEX_BUILDER_LOG.md`.

Return `R04_SOURCE_READY` / `R04_BLOCKED`, `CLEANUP_PENDING_REPORTED` or exact reason, `PROCESS_QUIESCENCE_PROVEN` or `PROCESS_QUIESCENCE_UNPROVEN`, `INSTALL_BLOCKED_MANIFEST_DRIFT`, `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK`, `INSTALLED_GUI_OPEN`, real published commit(s), existing log URL and prospective owner decision packet URL. Do not claim full V13 acceptance. GPT will conduct independent R04 audit and update `TASKS.md`.
