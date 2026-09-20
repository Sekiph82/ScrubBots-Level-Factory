# SB-LFX-003..017-C001 — MASTER BATCH IMPLEMENTATION PROMPT

Document role: CODEX MASTER IMPLEMENTATION PROMPT
Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: main
Canonical local mirror: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator

## Owner-authorized execution mode

Implement the remaining SB-LFX tasks sequentially in ONE continuous builder run:

SB-LFX-003 → 004 → 005 → 006 → 007 → 008 → 009 → 010 → 011 → 012 → 013 → 014 → 015 → 016 → 017.

Do NOT wait for ChatGPT audit between tasks.

SB-LFX-001 and SB-LFX-002 are already independently audited PASS/CLOSED baselines. Preserve them and do not reimplement them unless a later task requires a strictly additive compatible integration.

Read:
- root TASKS.md;
- docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md;
- .hiveai/prompts/SB-LFX-001-017_IMPLEMENTATION_AND_AUDIT_INDEX.md;
- .hiveai/audit-criteria/SB-LFX-003-017_POST_BATCH_STRICT_AUDIT_PROTOCOL.md.

## Critical governance

- GitHub main is canonical.
- Root TASKS.md is READ ONLY for Codex.
- Do not edit any audit criteria, authoritative prompt, strict audit or product-plan file.
- Builder logs are claims, not acceptance.
- A passing test suite does NOT mean a task is PASS/CLOSED.
- Previous tasks in this batch are IMPLEMENTED BUT UNAUDITED. Use their committed APIs as implementation dependencies, but never describe them as independently accepted.
- Preserve SB-LFX-001/002 and all accepted LF06 behavior.
- No sibling repo work.
- No secrets or provider credit spending unless a task explicitly has an already-authorized reliable local contract. LFX-017 must not spend credits merely to populate accounting.

## Task loop

For EACH task N from 003 through 017:

1. Sync/fetch GitHub main and confirm local HEAD == origin/main before starting the task.
2. Read that task's exact audit criteria and exact implementation prompt from the index.
3. Create that task's exact builder log path from the index BEFORE any product/test edit.
4. In the log record:
   - starting HEAD;
   - scope;
   - required reads;
   - implementation decisions;
   - chronology.
5. Implement ONLY that task's authorized scope.
6. Do not opportunistically implement the next task.
7. Run the task's focused tests and real Godot integration.
8. Run the retained regressions required by the task prompt/criteria.
9. Run full `python -m pytest -q`, compileall, Godot headless boot, `git diff --check`, and prove `git diff -- TASKS.md` is empty.
10. Keep the repository green before advancing.
11. Commit task implementation/tests/docs. One or more implementation commits are allowed, but identify one FINAL IMPLEMENTATION SHA that contains all non-log work for that task.
12. Push main and confirm local/remote equality.
13. Finalize ONLY that task's builder log with:
    - changed files;
    - test commands/results;
    - known limitations;
    - final implementation SHA;
    - publication topology.
14. Make exactly one task-final commit that changes ONLY that task's builder log.
15. Push and record that task-final LOG-ONLY SHA.
16. Confirm the task-final commit is log-only.
17. Immediately proceed to the next task without waiting for audit.

## Failure/blocker handling

Do not fake completion to keep the batch moving.

If a task encounters a genuine missing canonical dependency:
- implement the truthful NOT_AVAILABLE/BLOCKED behavior required by its criteria where that satisfies the product contract;
- keep the repo green;
- state the limitation explicitly in the task log.

If a task cannot be completed safely and its own required tests cannot be made green:
- do not leave main broken;
- revert only the broken task edits if necessary;
- finalize that task log as `IMPLEMENTATION_INCOMPLETE / BLOCKED` with exact reason and evidence;
- create the task-final log-only commit;
- continue to later tasks ONLY where they can be implemented truthfully without pretending the blocked dependency exists.
- if a later task depends on the blocked capability, implement only truthful unavailable behavior or record that later task BLOCKED too.

Every task 003..017 must end with its own builder log, even if BLOCKED.

## Non-negotiable truth rules

- Owner source bytes are immutable.
- Transformations create separate derived identities.
- C01..C16 / dimensions / alpha / structural facts come from canonical code, not UI guesses.
- WFC is not the ScrubBots gameplay solver.
- Target difficulty is not measured Difficulty V1.
- QA PASS is not owner acceptance.
- Library/search/dashboard/readiness/comparison views are derived, not new truth stores.
- Review evidence is explicit and auditable.
- Exact Reproduce is enabled only for real reproducible paths.
- Similarity is advisory, never auto-reject.
- Provider accounting shows UNKNOWN/NOT AVAILABLE instead of invented precision.
- Imported/source art is provenance-bearing content, never training data.
- No task may silently promote content to production.

## Final batch output

After SB-LFX-017 task-final log-only commit is pushed:

1. Create:
   `.hiveai/codex-logs/SB-LFX-003-017-C001_MASTER_BATCH_IMPLEMENTATION_CODEX_LOG.md`

2. This master log must contain a table for every task 003..017:
   - task ID;
   - task builder-log full GitHub URL;
   - start SHA;
   - final implementation SHA;
   - task-final log-only SHA;
   - builder status: IMPLEMENTED or IMPLEMENTATION_INCOMPLETE/BLOCKED;
   - focused test result;
   - full-suite result.

3. Commit/push this master batch log as the only file in the final batch-summary commit.

4. Return to the user ONLY:
   - master batch-log full GitHub URL;
   - final batch-summary SHA;
   - a compact list of the 15 per-task builder-log URLs.

Then STOP. Do not create audits. Do not create remediation prompts. ChatGPT performs those only after the complete coding batch.
