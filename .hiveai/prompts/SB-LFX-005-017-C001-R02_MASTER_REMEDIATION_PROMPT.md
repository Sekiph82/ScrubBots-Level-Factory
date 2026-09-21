# SB-LFX C001-R02 — MASTER REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main
Canonical local mirror: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator

Execute the R02 remediation batch sequentially in one run:

SB-LFX-005 → 008 → 009 → 011 → 012 → 013 → 014 → 015 → 016 → 017.

Do not touch PASS/CLOSED SB-LFX-004, 006, 007, 010 except for strictly necessary compatibility regression fixes that do not change accepted semantics.

Read:
- root TASKS.md;
- .hiveai/prompts/SB-LFX-005-017-C001-R02_REMEDIATION_INDEX.md;
- each task's saved R01 strict audit;
- each task's original criteria;
- each task's exact R02 prompt.

For EACH R02 task:
1. sync main and confirm local == origin/main;
2. create that task's R02 builder log before edits;
3. implement only the findings in its R01 audit/R02 prompt;
4. run focused tests + required real Godot integration;
5. run retained dependent regressions;
6. run full pytest, compileall, Godot headless boot, diff-check, and prove TASKS diff empty;
7. commit non-log implementation/tests/docs and record FINAL R02 IMPLEMENTATION SHA;
8. push and confirm equality;
9. finalize only the task's R02 builder log;
10. make exactly one task-final LOG-ONLY commit and record its SHA;
11. continue to next task without waiting for audit.

Cross-task dependency order matters:
- 012 must complete before revision-backed 016 closes.
- validated 006 review truth must remain the authority used by 009/017.
- accepted 004 validation and 005 pipeline truth must remain intact.

Never:
- edit TASKS.md;
- fabricate M03/M04/M05/owner/export/provider truth;
- weaken immutable source/candidate/review contracts;
- spend provider credits or make network calls merely for tests.

If a task cannot be completed safely, leave main green, finalize its R02 log as BLOCKED with exact evidence, and continue only where later tasks remain truthful.

After SB-LFX-017-R02:
create
`.hiveai/codex-logs/SB-LFX-C001-R02_MASTER_REMEDIATION_CODEX_LOG.md`

with a table containing for each R02 task:
- builder-log URL;
- start SHA;
- final implementation SHA;
- terminal log-only SHA;
- status;
- focused/runtime result;
- full-suite result.

Commit the master remediation log alone in the final summary commit.

Return only:
- master R02 log URL;
- final summary SHA;
- compact list of the 10 per-task R02 log URLs.

STOP. ChatGPT performs independent re-audit after the full R02 batch.
