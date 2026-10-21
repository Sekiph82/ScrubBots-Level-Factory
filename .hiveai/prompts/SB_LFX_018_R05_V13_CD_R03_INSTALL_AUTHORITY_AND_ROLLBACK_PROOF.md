# SB-LFX-018 R05 M03 | EXECUTION UNBLOCK + REAL OWNER-002 NATIVE REPLAY | UNRESTRICTED ENGINEERING MASTER V02
Document role: GPT AUTHORIZED CODEX BUILDER PROMPT
Date: 2026-10-21 Europe/Istanbul
Cycle scope: R03 focused continuation of the same active SB-LFX-018 R05 V13-C/D. **Do not restart/rebuild R02, V13-A/B, V13-D solver or the 140-source batch.**
Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Canonical desktop checkout: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Tracker: root `TASKS.md`
Required independent audit V17: https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/SB_LFX_018_R05_V13_CD_R02_MANIFEST_DRIFT_STRICT_AUDIT_V17.md
Previous R02 source/test published commit: `c9fef3a9ce1165f15352be34cd3ef673da0ae2ad`; R02 builder receipts `a32c51a`, `7b869cd`.

## Hard authority boundaries

Read `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`, V16/V17 independent audits, the preceding R02 prompt, current source installer/tests and existing chronological M03 builder log. Follow strongest current owner instruction: **Desktop only, no new clone, worktree, TEMP scratch, extracted project/copy, blind Release install, forced sync, reset/clean/rebase/autostash.** Preserve owner-untracked Release, `.uid`, `.import`, `.godot`, fixtures, images and stashes. The current task state and prompt precedence come from GitHub. Normal fast-forward-only publication; no force. If checkout unsafe, preserve and report, do not invent a new workspace.

**ZERO GitHub Actions/CI/hosted runners, paid APIs/providers, R2/staging/production calls, Claude quota probing, PixelLab credit spending, 140 retry/resume/repaint, owner PNG/Pool/job changes, or process kills.** Do not touch used prompts, independent audits, tracker, HANDOFF, workflow files or historical logs. Append only to existing M03 CODEX BUILDER LOG with chronological truthful records. No new approval is implied by this prompt.

## Goal A: narrow approved-manifest provenance decision (R02-F01)

Start with bounded read-only local verification of `HEAD`, `origin/main`, branch, tracked status, exact paths, 2,318-item installed manifest and exact target hashes. Do not edit `Release`.

Reconfirm:
- manifest `verify.py` SHA `0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2`;
- installed `verify.py` SHA `90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744`;
- manifest baseline corresponds to source `51c7db1`; installed CRLF bytes correspond to source `17643de`;
- installed overlay path absent, per-file receipt count zero, while R02 preflight plans eight other managed replacements and three overlay additions.

**Find actual authority, not just source equivalence**: within already-owned installation metadata and approved prior receipts, inspect exact original installation/upgrade provenance, dated manifest backups if already present, explicitly authorized prior transitions, and hash-bound repair receipts. Only bounded read-only inspection, never broad disk search. Distinguish an authentic contemporaneous approved install receipt from a newly inferred historical claim. If no authentic approval is found, record `INSTALL_BLOCKED_MANIFEST_DRIFT`, refuse `-Apply`, and produce a small owner decision packet: exact current/expected/new source hashes, file-path scope, backup/rollback plan, tests and what narrowly scoped approval would be required. **Do not silently fix/rebase hash, rewrite manifest, install the old source version, or present an inferred receipt as fact.** If provenance is indeterminate this is an accepted safe *diagnostic* end state, not permission to deploy.

## Goal B: finish fail-closed transactional proof (R02-F02/F03)

Inspect real source in `scripts/install_factory_studio_scoped_overlay.ps1`. Retain exact allowlist and managed-file checks. Add **bounded, offline, no-cache focused tests** of:
1. manifest drift rejects before target replacement;
2. staging failure with zero live replacements;
3. replacement failure after the first/second payload: reverse restore of exact hashes;
4. manifest replacement or final verification failure: manifest plus all earlier live bytes restored; explicit failure if rollback incomplete;
5. process inventory denies apply when a matching writer/child exists, or when needed process executable/command-line/parent metadata is inaccessible/incomplete;
6. no-op and authorized legacy repair vs unknown installed-byte drift;
7. unchanged original job/Pool/PNG isolation.

Tests must actually exercise behavior where feasible, **not only inspect PowerShell source strings**. Use a synthetic in-memory adapter for pure logic or narrowly bounded existing repo-local test fixtures only if permitted by owner's Desktop-only/no-TEMP policy. Never create/modify an imitation Release installation in owner protected data. If actual file fault-injection is not safely possible under owner policy, say `UNVERIFIED`; source-only/test-double tests are not physical rollback acceptance. Avoid mass suite reruns and any cache-producing default.

Add narrowly justified source improvements only for confirmed failures. In particular, on failed rollback do not print an unconditional restored-state claim; re-hash targets/manifest to prove recovery where feasible and preserve error/evidence if not. Make process-observation quality explicit rather than treating inaccessible fields as proof that no writer exists. Record focused failed attempts and fixes, syntax checks, Python tests, `git diff --check`.

## Goal C: native/installed boundary (R02-F04)

Read-only inspection of actual Godot 4.7.2 CLI options and current import/cache write paths is allowed, but **do not open the protected project** if write-free execution cannot be proven. No TEMP clone, staging copy, alternate Godot user profile, new scratch, owner UID/import/cache deletion, filesystem overlay or implicit cache baseline write. If truly read-only native route is demonstrated, explicitly hash every protected path before/after and run only bounded focused native checks; otherwise `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK` remains OPEN. Do not promote 240→480 same-PID, child-kill, native GUI or three-screen screenshot status without genuine Windows evidence. Actual `-Apply` remains forbidden until manifest approval AND mandatory native/process/install gates are met.

## Goal D: publication and handoff

Do all remaining safe source/test improvements without asking routine questions, even if deployment is blocked. If no additional justified code changes are possible, publish a concise new chronological builder-log continuation only, including exact reason no source changed. Use separate source/test and log commits if practical, normal fast-forward-safe `git push origin HEAD:main`, no workflow dispatch; verify fetched post-push GitHub parity and tracked clean state. Return short status with:
`R03_PROVENANCE_FOUND` or `INSTALL_BLOCKED_MANIFEST_DRIFT`;
`ROLLBACK_TESTED` / `ROLLBACK_SOURCE_ONLY` / `ROLLBACK_UNVERIFIED`;
`PROCESS_INVENTORY_FAIL_CLOSED` or exact remaining blocker;
`NATIVE_GODOT_PASS` or `NATIVE_GODOT_OWNER_CACHE_WRITE_RISK`;
`INSTALLED_GUI_PASS` or `INSTALLED_GUI_OPEN`;
protected 140 = 102 READY + 4 FAILED + 34 REJECTED, Pool 131 JSON entries only as builder-verified; source commit(s), builder-log commit, full log URL.

**Builder never edits `TASKS.md` or independent audits, never declares whole milestone accepted.** GPT conducts independent R03 review and controls next task state.
