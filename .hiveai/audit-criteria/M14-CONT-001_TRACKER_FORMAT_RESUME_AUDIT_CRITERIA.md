# M14-CONT-001 — Tracker Format Fix Resume — Audit Criteria

## PASS rule

PASS only if the existing M14 TEMP worktree resumes without losing or rewriting the uncommitted CP03-001 implementation/log work, incorporates the authoritative tracker-only fix, reruns the blocked governance/full-suite gates successfully, publishes CP03-001 normally, and then continues the already-authorized M14 master batch.

## A. Preserve existing work

Require:
- exact existing TEMP worktree is reused:
  `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`;
- current uncommitted CP03-001 implementation and its two builder logs are preserved byte-for-byte before upstream synchronization;
- no reset, clean, restore, rebase, force, checkout-overwrite, auto-stash or discard;
- root `TASKS.md` and `.hiveai/audits/**` remain unmodified locally by Codex.

## B. Incorporate authoritative tracker fix

Require:
- fetch/prune origin;
- verify authoritative tracker format-fix commit `dd7c4379ae6a5443e26f3117eee80d643d8ef529` is contained in current `origin/main`;
- verify upstream changes since the CP03-001 start do not overlap the uncommitted CP03-001 implementation/log paths except the expected tracker-only governance correction;
- safely fast-forward to current `origin/main` only if Git confirms local modifications will not be overwritten;
- if any overlap/ambiguity exists, stop rather than stash/reset/discard.

## C. Re-run blocked gates

Before any commit:
- run `tests/unit/test_sb_lf00_007_governance_authority.py`;
- require the current-task em-dash contract PASS;
- rerun CP03-001 focused regressions;
- rerun safe unfiltered full pytest;
- compileall PASS;
- all Content Pipeline JSON parse checks PASS;
- `git diff --check` PASS.

## D. Continue original master batch

If gates pass:
- finish CP03-001 publication with implementation commit and separate child-log commit;
- append a truthful continuation section to the existing M14 master log;
- normal non-force push to main;
- fetch and require 0/0 clean parity;
- continue immediately with CP03-002 and the existing M14 master execution order;
- do not request another owner/ChatGPT handoff between passing children.

## E. No scope expansion

Do not change the governance test to accept the wrong separator.
Do not weaken tracker parsing.
Do not redesign CP03-001.
Do not edit root `TASKS.md`.
Do not edit `.hiveai/audits/**`.
