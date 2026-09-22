# SB-LF03-003..012-C001 - Post-Batch Strict Audit Protocol

Document role: CHATGPT INDEPENDENT AUDIT PROTOCOL

## Timing

Do not audit individual task completion from builder claims during the implementation run.

Wait until the complete SB-LF03-003..012 builder batch and master builder log are published.

Then independently audit every task:

`003, 004, 005, 006, 007, 008, 009, 010, 011, 012`

one by one.

## Evidence hierarchy

For each task inspect:
1. its exact implementation prompt;
2. its exact audit criteria;
3. builder log;
4. implementation commits/diffs;
5. current product code;
6. committed tests;
7. retained predecessor contracts;
8. canonical `Sekiph82/Scrubbots` authority when relevant;
9. full-batch regression evidence;
10. root `TASKS.md` no-builder-diff requirement.

Builder logs are claims, not acceptance.

## Audit output

Create one durable audit file per task under:
`.hiveai/audits/`

Each must contain:
- PASS/CLOSED or CHANGES_REQUIRED;
- BLOCKER/MAJOR/MINOR counts;
- exact implementation/log SHAs;
- findings;
- preserved accepted behavior;
- required remediation if any.

Also create:
`.hiveai/audits/SB-LF03-003-012-C001_STRICT_AUDIT_SUMMARY.md`

## No cascading false closure

A later task can be implemented on top of an earlier task that eventually fails audit.

Do not automatically fail the later task solely because the earlier one failed.

Instead determine whether:
- the later task's own implementation is independently sound but dependency-gated;
- or it materially relies on incorrect semantics and therefore also requires remediation.

## Remediation protocol

If any tasks fail:

1. Close only tasks that independently PASS.
2. Keep the earliest failed task as the sole active `[~]` unless a stricter dependency order is required.
3. Create a distinct R01 remediation prompt for every failed task.
4. Preserve every accepted behavior from the C001 audit.
5. Create:
   `.hiveai/prompts/SB-LF03-<failed-range>-C001-R01_REMEDIATION_INDEX.md`
6. Create:
   `.hiveai/prompts/SB-LF03-<failed-range>-C001-R01_MASTER_REMEDIATION_PROMPT.md`
7. Master remediation executes failed tasks only, in ascending dependency order.
8. Each failed task gets its own R01 builder log.
9. The batch gets:
   `.hiveai/codex-logs/SB-LF03-C001-R01_MASTER_REMEDIATION_CODEX_LOG.md`
10. ChatGPT independently re-audits every remediated task after the whole remediation batch.

Repeat R02/R03 only for still-open findings. Never reopen PASS/CLOSED tasks without a new independently demonstrated defect.

## Truth constraints

Across audits/remediation:
- no Python clone of canonical gameplay mechanics;
- WFC is never gameplay solver authority;
- UNKNOWN_BOUND/budget exhaustion is never PROVEN_UNSOLVABLE;
- provider unavailable is never a solved/unsolved verdict;
- timing is never canonical deterministic evidence;
- fixture providers never become production authority;
- main-game checkout/source identity must fail closed on drift;
- root TASKS remains ChatGPT-owned.
