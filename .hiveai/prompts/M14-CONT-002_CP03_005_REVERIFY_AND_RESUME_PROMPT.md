# M14-CONT-002 — Reverify CP03-005 After Tracker Denominator Fix and Resume

Document role: CODEX MASTER CONTINUATION PROMPT

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent interim audit:
`.hiveai/audits/M14_CP03_001_012_CPX002_MASTER_INTERIM_STRICT_AUDIT.md`

CP03-005 audit:
`.hiveai/audits/SB-CP03-005-C001_VERIFY_REMOTE_OBJECT_INTEGRITY_STRICT_AUDIT.md`

Continuation criteria:
`.hiveai/audit-criteria/M14-CONT-002_CP03_005_REVERIFY_AND_RESUME_AUDIT_CRITERIA.md`

Authoritative tracker correction:
`67807bd54d6a31d29ddc8f672ca3f23a7f754a6a`

Existing M14 master:
`.hiveai/prompts/M14_CP03_001_012_CPX002_MASTER_IMPLEMENTATION_PROMPT.md`

## FIRST OPERATION — mandatory GitHub ↔ Desktop synchronization

1. Verify canonical Level Factory repository identity and origin.
2. Reuse the existing authorized M14 TEMP worktree if it still exists and is safe.
3. Run `git fetch --prune origin`.
4. Read current `origin/main:TASKS.md`; require this continuation as Current Prompt/authority.
5. Verify `origin/main` contains commit `67807bd54d6a31d29ddc8f672ca3f23a7f754a6a`.
6. Preserve owner-local work. Never reset, clean, auto-stash, rebase, force, restore, overwrite or discard.
7. If the old TEMP worktree is gone, create only:
   `%TEMP%\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`
   from exact current origin/main.
8. Require execution HEAD clean and 0/0 before verification.

Create/update continuation evidence in:
`.hiveai/codex-logs/M14_CP03_001_012_CPX002_MASTER_CODEX_LOG.md`

Do not rewrite prior log history.

## Current accepted state

Independent ChatGPT audit has closed:
- CP03-001 PASS/CLOSED
- CP03-002 PASS/CLOSED
- CP03-003 PASS/CLOSED
- CP03-004 PASS/CLOSED

CP03-005 product semantics passed independent source audit but remained conditional only because the full suite was blocked by the ChatGPT-owned denominator mismatch.

Do not reimplement CP03-001..004.

## Step 1 — verify tracker correction first

Run:

`python -m pytest -q tests/unit/test_sb_lf00_007_governance_authority.py`

Require all tests PASS.

If denominator still fails:
- stop;
- do not edit TASKS.md;
- do not edit the governance test.

## Step 2 — reverify CP03-005 unchanged

Verify current implementation still contains commit:
`88d2d09e28e73e4d4f8c5d555efab2e60a809704`

Rerun:
- CP03-005 focused byte-integrity tests;
- CP03-003/004 regressions;
- cumulative M14/M13/M12/M11/governance tests;
- safe unfiltered `python -m pytest -q`;
- compileall;
- all Content Pipeline JSON parse checks;
- `git diff --check`.

Expected product behavior remains:
- exact provider byte readback;
- local length/SHA/byte equality;
- M12 inspect_scrubpack on readback bytes;
- provider SUCCESS alone insufficient;
- truncation/mutation/swap/wrong-key/stale digest fail closed.

Do not edit CP03-005 product code merely to create a new commit if all tests are green.

Append reverify evidence to:
- CP03-005 child log;
- M14 master log.

Commit only evidence-log changes if product code remains unchanged.

Publish normally to main and require 0/0 clean parity.

## Step 3 — resume original M14 master

If CP03-005 is green, continue immediately under the existing child prompts:

`CP03-006 -> CP03-007 -> CPX-002 -> CP03-008 -> CP03-009 -> CP03-010 -> CP03-011 -> CP03-012`

For every child:
- use its existing prompt + audit criteria;
- one distinct builder log;
- implementation/log commits separate;
- fetch before push;
- normal non-force main push;
- fetch after push;
- require 0/0 parity;
- continue without owner/ChatGPT handoff between passing children.

Preserve all original M14 provider/security/current-main rules.

## Protected boundaries

- Do not edit root TASKS.md.
- Do not edit .hiveai/audits/**.
- Do not run queued Factory Studio launcher maintenance concurrently.
- Do not select or integrate a real cloud vendor before M18.
- CPX-002 authentic current Scrubbots main Godot replay remains mandatory before production promotion.

## Final response

When M14 completes or reaches a new true blocker, return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/M14_CP03_001_012_CPX002_MASTER_CODEX_LOG.md
