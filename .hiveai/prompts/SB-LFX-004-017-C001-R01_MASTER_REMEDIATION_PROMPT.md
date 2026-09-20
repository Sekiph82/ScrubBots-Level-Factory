# SB-LFX-004..017-C001-R01 — MASTER REMEDIATION PROMPT

Document role: CODEX MASTER REMEDIATION PROMPT
Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main
Canonical local mirror: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator

## Owner-authorized execution mode

Execute all required remediation tasks sequentially in ONE continuous run:
SB-LFX-004-R01 → 005-R01 → 006-R01 → 007-R01 → 008-R01 → 009-R01 → 010-R01 → 011-R01 → 012-R01 → 013-R01 → 014-R01 → 015-R01 → 016-R01 → 017-R01.

Do not wait for ChatGPT audit between remediations.

SB-LFX-003 is PASS/CLOSED and must be preserved.

Read before starting:
- root TASKS.md;
- .hiveai/prompts/SB-LFX-004-017-C001-R01_REMEDIATION_INDEX.md;
- every task's strict audit;
- every task's original audit criteria;
- every task's R01 remediation prompt.

## Governance

- GitHub main is canonical.
- TASKS.md is read-only for Codex.
- Do not edit audits, audit criteria, product specs or authoritative prompts.
- A remediation is not PASS merely because tests pass.
- Preserve accepted LF06, SB-LFX-001, SB-LFX-002 and SB-LFX-003 behavior.
- Preserve already-correct parts of SB-LFX-004..017; fix only audited findings and necessary compatibility boundaries.
- Earlier R01 tasks in this batch are implemented but unaudited dependencies until the post-remediation audit.
- No sibling repository work.
- No provider credit spending or network calls merely to satisfy tests/UI.

## Per-task R01 loop

For each task 004 through 017 in order:
1. Sync/fetch main and confirm local HEAD equals origin/main.
2. Read that task's strict audit, original criteria and exact R01 remediation prompt from the remediation index.
3. Create that task's exact R01 builder log BEFORE any product/test edit.
4. Record start SHA and all audited findings in the log.
5. Implement only the remediation needed to close those findings.
6. Run focused tests and the required real Godot integration.
7. Run retained dependent regressions. Pay special attention to cross-task dependencies such as:
   - 006 review validation feeding 007/009/010/017;
   - 004 validation feeding 005;
   - 005 pipeline evidence feeding 013/015;
   - 012 revision identity feeding 016.
8. Run full python -m pytest -q, compileall, Godot headless boot, git diff --check, and prove git diff -- TASKS.md is empty.
9. Commit all non-log remediation code/tests/docs and record one FINAL R01 IMPLEMENTATION SHA.
10. Push and confirm equality.
11. Finalize only that task's R01 builder log with changed files, test results, final implementation SHA, known limitations and publication topology.
12. Make exactly one R01 task-final commit changing ONLY that R01 builder log.
13. Push and record the R01 LOG-ONLY SHA.
14. Confirm the terminal task commit is log-only.
15. Continue immediately to the next R01 task.

## Failure handling

If a remediation cannot be completed safely:
- do not fake closure;
- do not leave main broken;
- retain truthful NOT_AVAILABLE/BLOCKED behavior where required;
- finalize that task's R01 log as REMEDIATION_INCOMPLETE/BLOCKED with exact evidence;
- continue only where later work can remain truthful.

Every task 004..017 must end with a separate R01 builder log even if blocked.

## Final remediation-batch log

After SB-LFX-017-R01 is published, create:
.hiveai/codex-logs/SB-LFX-004-017-C001-R01_MASTER_REMEDIATION_CODEX_LOG.md

The master log must contain for each task 004..017:
- R01 builder-log full GitHub URL;
- start SHA;
- final R01 implementation SHA;
- R01 terminal log-only SHA;
- builder status: REMEDIATED or REMEDIATION_INCOMPLETE/BLOCKED;
- focused/runtime result;
- full-suite result.

Commit/push the master remediation log as the only file in the final remediation-summary commit.

Then return only:
1. master remediation-log full GitHub URL;
2. final remediation-summary SHA;
3. compact list of the 14 per-task R01 builder-log URLs.

STOP. Do not create R01 audits. ChatGPT performs the independent re-audit task by task after the entire remediation batch.