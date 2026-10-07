# SB-CPX-002-C001-R01 — TEMP-Only Authority Evidence Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent strict audit:
`.hiveai/audits/SB-CPX-002-C001_CURRENT_MAIN_SUPPLY_REPLAY_PROMOTION_GATE_STRICT_AUDIT.md`

Audit criteria:
`.hiveai/audit-criteria/SB-CPX-002-C001-R01_TEMP_ONLY_AUTHORITY_EVIDENCE_AUDIT_CRITERIA.md`

## Purpose

Close one evidence/process defect only: an early CPX-002 builder attempt omitted `SCRUBBOTS_PROJECT` and allowed an existing Factory bridge to select the owner Desktop ScrubBots checkout before the authority mismatch failed closed.

The final CPX-002 product semantics and later TEMP-only replay are retained. Do not redesign CPX-002 or reopen CP03-008..012 unless a direct regression requires it.

## FIRST OPERATION — sync safely

1. Verify the canonical Level Factory repository/origin.
2. Run `git fetch --prune origin`.
3. Read current `origin/main:TASKS.md`; require this R01/master as current authority.
4. Preserve the persistent Desktop Level Factory checkout exactly. Never reset/clean/stash/restore/rebase/force/discard owner work.
5. Use a clean isolated TEMP execution worktree at exact current `origin/main` if the persistent checkout is not safely synchronizable.
6. Require execution HEAD == origin/main and 0/0 before R01 work.
7. Do not edit root `TASKS.md` or `.hiveai/audits/**`.

## Mandatory game-authority setup BEFORE any Factory/solver/replay call

Create a fresh isolated game authority under:
`%TEMP%\ScrubBots-Level-Factory\CPX-002-R01-GAME-AUTHORITY`

Before any CPX-001 pack construction, Factory solver bridge or CPX-002 replay:
- clone/fetch only `https://github.com/Sekiph82/Scrubbots.git`;
- resolve exact current `origin/main`;
- detach at that SHA;
- require clean status and HEAD == origin/main;
- require the root is under `%TEMP%`;
- explicitly set `SCRUBBOTS_PROJECT` to this exact TEMP root;
- pass the same exact root explicitly to every adapter that accepts a project/game root.

**Do not access or select `C:\Users\sekip\Desktop\ScrubBots` or any other owner persistent game checkout.**

## Required remediation

Add the narrowest fail-closed guard/regression needed so the CPX-002 authentic integration cannot silently use a configured/default Desktop game checkout when explicit TEMP authority is absent.

Preferred boundary:
- CPX-002 integration/host authority setup must require an explicit game authority;
- missing, non-TEMP, wrong-remote, dirty, non-current or drifting authority must stop before Factory solver/current-main replay work.

Do not weaken existing authority checks.

## Fresh evidence

From scratch, using only the R01 TEMP game authority:
1. build the authentic owner-accepted/READY CPX-001 solver-proven fixture;
2. build and verify exact staged pack/manifest bytes;
3. replay every packaged plan through current main Godot authority;
4. require exact identity/conservation/FIFO binding;
5. require `SOLVED`, replay PASS, active 0, unresolved 0, supply exhausted;
6. fetch/re-resolve origin/main after replay and require unchanged SHA/source hashes.

Record:
- ScrubBots current-main SHA;
- Godot version;
- authority source hashes;
- exact TEMP authority path classification (TEMP only, do not publish private user path text beyond the bounded TEMP role);
- test results and drift-fence result.

## Regression

Run:
- CPX-002 focused tests including missing/non-TEMP authority negative cases;
- authentic CPX-002 current-main integration;
- cumulative M14/M11-M13/governance suite;
- safe unfiltered full pytest with no implicit Desktop game authority;
- compileall;
- all Content Pipeline JSON parses;
- git diff --check.

If product/test code changes, commit implementation separately from the builder log.

Publish normally to `main`, fetch again and require clean 0/0 parity.

## Builder log

Write:
`.hiveai/codex-logs/SB-CPX-002-C001-R01_TEMP_ONLY_AUTHORITY_EVIDENCE_CODEX_LOG.md`

Append a truthful R01 summary to:
`.hiveai/codex-logs/M14_CP03_001_012_CPX002_MASTER_CODEX_LOG.md`

Do not rewrite prior history.

## Stop condition

After publication and clean 0/0 parity, stop for independent ChatGPT re-audit. Do not start M15 or any queued maintenance task.
