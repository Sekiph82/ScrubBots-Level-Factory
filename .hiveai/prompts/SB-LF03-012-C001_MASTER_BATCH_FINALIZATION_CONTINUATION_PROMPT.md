# SB-LF03-012-C001 + C001 Master Batch Finalization Continuation

Document role: CODEX CONTINUATION / MASTER FINALIZATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

## Authorization

Resume the already-started LF03 master batch from its current published state.

Do **not** reimplement or rewrite SB-LF03-003..011.

The only remaining implementation task is:

`SB-LF03-012 — Add regression fixtures.`

After SB-LF03-012 is published, complete the existing LF03 C001 master-batch final verification and master log.

Current observed `main` at prompt preparation:

`f157e33a11a2ffef0ddb3ca631980dde1038377a`

This is informational only. Resolve current `origin/main` again when execution begins and fast-forward safely if needed.

## Required canonical reads

Read before changes:

- root `TASKS.md`;
- `AGENTS.md`;
- `GOVERNANCE.md`;
- `.hiveai/prompts/SB-LF03-003-012-C001_MASTER_BATCH_IMPLEMENTATION_PROMPT.md`;
- `.hiveai/prompts/SB-LF03-003-012-C001_IMPLEMENTATION_AND_AUDIT_INDEX.md`;
- `.hiveai/audit-criteria/SB-LF03-003-012-C001_POST_BATCH_STRICT_AUDIT_PROTOCOL.md`;
- `.hiveai/prompts/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_PROMPT.md`;
- `.hiveai/audit-criteria/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_AUDIT_CRITERIA.md`;
- all published SB-LF03-003..011 builder logs;
- current accepted LF03 product code and tests.

Do not modify root `TASKS.md`.

## Part A — Complete SB-LF03-012 only

Create the required builder log **before product/test edits**:

`.hiveai/codex-logs/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_CODEX_LOG.md`

Implement exactly the existing SB-LF03-012 prompt and audit criteria.

Required fixture coverage includes at minimum:

- legal-move provider schema/availability;
- deterministic branching solved search;
- proven no-solution/exhausted search;
- repeated-state/memoization;
- bounded INCONCLUSIVE;
- 0/1/multiple-solution analysis;
- solver evidence metrics;
- reproduction MATCH/DIVERGED;
- authority/source tamper fail-closed;
- canonical bridge integration when the required checkout/runner capability is supplied;
- large/rectangular workload evidence where practical.

Keep fixture-only fake providers explicitly non-production.

Do not add machine-specific paths, timestamps, caches, provider secrets, or another gameplay rules engine.

Canonical gameplay authority remains:

https://github.com/Sekiph82/Scrubbots

Do not copy ProofState, ProofKernel, legal-move, routing, targeting, placement, clearing, completion/deadlock, or canonical-key semantics into Python.

If the real canonical checkout/runner capabilities are absent, the integration fixture may skip only with an explicit truthful reason. If capabilities are supplied, it must execute and cannot silently skip.

### SB-LF03-012 verification

Run:

- focused SB-LF03-012 regression tests;
- the complete retained LF03 test set;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- real canonical bridge regression if capability is supplied;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Record exact pass/fail/skip counts and every correction truthfully.

Publish:

1. SB-LF03-012 implementation/tests/docs + builder log commit;
2. push to `main`;
3. finalize the SB-LF03-012 builder log;
4. create/push its terminal log-only commit.

Do not touch prior SB-LF03-003..011 logs except to read them.

## Part B — Finalize the existing LF03 C001 master batch

Only after SB-LF03-012 publication is complete, create:

`.hiveai/codex-logs/SB-LF03-C001_MASTER_BATCH_CODEX_LOG.md`

The master log must cover all ten tasks:

`SB-LF03-003, 004, 005, 006, 007, 008, 009, 010, 011, 012`

For each task record:

- task ID;
- builder-log path;
- full GitHub builder-log URL;
- implementation commit SHA;
- terminal log-only commit SHA;
- focused test result;
- full-suite result reported at that task;
- every skip and exact reason;
- known limitation/blocker;
- confirmation that `TASKS.md` diff was zero.

Do not infer missing data. Read it from the actual published builder logs/commits.

Explicitly preserve the known canonical-bridge truth:
- SB-LF03-009 must not be described as real canonical execution if the required checkout/runner integration did not actually execute;
- unavailable/skipped canonical bridge evidence must remain visibly unavailable/skipped.

## Final batch-wide verification

From the final post-012 repository state run:

- all retained LF03 tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- real canonical bridge regression if configured;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Record:
- exact test counts;
- skips and reasons;
- warnings;
- current `main` SHA;
- canonical Scrubbots authority SHA used;
- any unresolved capability limitation;
- confirmation that builder did not edit `TASKS.md`.

## Publication order

After final verification:

1. create/finalize `.hiveai/codex-logs/SB-LF03-C001_MASTER_BATCH_CODEX_LOG.md`;
2. commit/push the master log as the final batch summary commit;
3. verify local HEAD == `origin/main`;
4. STOP.

Do not create independent audits.
Do not create remediation prompts.
Do not mark any task PASS/CLOSED.
Do not advance the tracker.

ChatGPT will independently audit SB-LF03-003..012 one by one after this master log is published.

## Final response

Return only:

1. full GitHub URL of `.hiveai/codex-logs/SB-LF03-C001_MASTER_BATCH_CODEX_LOG.md`;
2. final master-log commit SHA;
3. full GitHub URL of `.hiveai/codex-logs/SB-LF03-012-C001_SOLVER_REGRESSION_FIXTURE_SUITE_CODEX_LOG.md`;
4. SB-LF03-012 implementation commit SHA;
5. SB-LF03-012 terminal log-only commit SHA.

Then STOP.
