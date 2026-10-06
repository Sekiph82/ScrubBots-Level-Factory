# M14-CONT-001 — Resume After Authoritative Tracker Format Fix

Document role: CODEX MASTER CONTINUATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Existing master:
`.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`

Continuation criteria:
`.hiveai/audit-criteria/M14-CONT-001_TRACKER_FORMAT_RESUME_AUDIT_CRITERIA.md`

Authoritative tracker fix:
`dd7c4379ae6a5443e26f3117eee80d643d8ef529`

## Context

CP03-001 product work is already implemented but remains uncommitted in:

`C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`

The prior master run stopped only because the authoritative root tracker used:

`- Current Task: SB-CP03-001 - M14 master batch entry point`

while the canonical governance parser requires:

`- Current Task: SB-CP03-001 — M14 master batch entry point`

ChatGPT, the sole tracker writer, corrected that authoritative line in commit:
`dd7c4379ae6a5443e26f3117eee80d643d8ef529`

Do not modify the governance test.

## FIRST OPERATION — preserve the existing dirty TEMP worktree

1. Reuse exactly:
   `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`
2. Record current HEAD, status, diff, untracked files and hashes of the uncommitted CP03-001 implementation/log files.
3. Verify there is no local modification to:
   - `TASKS.md`;
   - `.hiveai/audits/**`.
4. Do NOT reset, clean, restore, rebase, force, checkout-overwrite, auto-stash or discard anything.
5. Run `git fetch --prune origin`.
6. Verify `origin/main` contains commit `dd7c4379ae6a5443e26f3117eee80d643d8ef529`.
7. Inspect the upstream diff from the worktree's current HEAD to `origin/main`.
8. Confirm the authoritative new upstream change does not overwrite any current uncommitted CP03-001 implementation/log path.
9. Only if non-overlapping, fast-forward the worktree to current `origin/main` while preserving all uncommitted work.
10. Re-hash/re-diff the preserved CP03-001 local changes and prove they are unchanged.

If Git refuses the fast-forward because a local file would be overwritten, or if any overlap is ambiguous, STOP. Do not stash or discard.

## Re-run the exact blocker first

Run:

`python -m pytest -q tests/unit/test_sb_lf00_007_governance_authority.py`

The governance test must now pass from the authoritative tracker fix.

If it does not, stop and record the exact assertion. Do not edit `TASKS.md` or the governance test.

## Resume CP03-001 verification

Then rerun:
- the CP03-001 focused suite;
- prior M14/M13/M12/M11/governance regressions required by the child/master;
- safe unfiltered `python -m pytest -q`;
- compileall;
- all Content Pipeline JSON parse checks;
- `git diff --check`.

The full-suite environment must continue to respect the M13 scope guard: no implicit owner Desktop Scrubbots checkout authority.

## CP03-001 publication

If all gates pass:

1. Update the existing CP03-001 builder log with the tracker-fix continuation evidence.
2. Append a continuation section to the existing M14 master log.
3. Commit CP03-001 implementation.
4. Commit CP03-001 child log/master-log evidence separately as appropriate.
5. Fetch/prune.
6. Normal non-force push to `main`.
7. Fetch again and require HEAD == `origin/main`, divergence 0/0, clean worktree.

Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.

## Continue the M14 master

After CP03-001 publication succeeds, continue immediately under the existing master prompt at:

`SB-CP03-002-C001`

Then continue the already-authorized order:

`CP03-002 -> 003 -> 004 -> 005 -> 006 -> 007 -> CPX-002 -> CP03-008 -> 009 -> 010 -> 011 -> 012`

Do not stop between passing children.

## Final response

When the whole M14 master batch completes or reaches a true blocker, return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/M14_CP03_001_012_CPX002_MASTER_CODEX_LOG.md
