# SB-LF03-003..012-C001-R01 — Master Remediation Prompt

Document role: CODEX MASTER REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

## Authorization

Remediate only the tasks that failed the C001 independent audit:

`SB-LF03-003 -> 004 -> 005 -> 006 -> 008 -> 009 -> 010 -> 011 -> 012`

Do not reopen SB-LF03-007. It is PASS/CLOSED.

Canonical R01 index:
`.hiveai/prompts/SB-LF03-003-012-C001-R01_REMEDIATION_INDEX.md`

C001 audit summary:
`.hiveai/audits/SB-LF03-003-012-C001_STRICT_AUDIT_SUMMARY.md`

## Governance

- Root `TASKS.md` is ChatGPT-owned. Do not edit it.
- Do not create or edit files under `.hiveai/audits/`.
- Do not rewrite C001 prompts/logs/audits.
- Every R01 task gets its own new builder log, implementation commit and terminal log-only commit.
- Preserve accepted C001 behavior not implicated by the corresponding audit.
- No force push/reset/clean/discard/rebase of unrelated user work.
- No provider credits or runtime network calls merely for tests.
- No Python clone of canonical ScrubBots gameplay mechanics.

## Canonical gameplay authority

Canonical truth remains:
https://github.com/Sekiph82/Scrubbots

Resolve current `main` SHA at execution time.

For SB-LF03-009/012, the owner's local main-game checkout may be used only as a **read-only canonical execution target** if present and if exact HEAD/source verification succeeds.

Expected owner checkout location may be:
`C:\Users\sekip\Desktop\ScrubBots`

Do not modify that checkout. Do not create bridge files inside it. Do not clean/reset/stash it. If it is dirty, authority verification must fail closed unless the exact required canonical source bytes and allowed immutability contract can still be proven under the existing verifier.

The external canonical bridge runner must live in the Level Factory repository or another location outside the canonical checkout.

## Execution order

For each task in this exact order:

1. synchronize Level Factory safely with current `origin/main`;
2. read its C001 audit and exact R01 prompt from the remediation index;
3. create its R01 builder log before product/test edits;
4. remediate only the findings;
5. run focused tests plus affected dependent LF03 tests;
6. run the requested retained/full gates;
7. verify `git diff --exit-code -- TASKS.md`;
8. commit/push product + tests/docs + task log;
9. finalize task log;
10. make/push terminal log-only commit;
11. continue without waiting for ChatGPT audit.

## Shared binding remediation

003/004/005/008 are related but remain separate audited tasks.

Prefer shared reusable validators rather than duplicated checks:
- legal result ↔ exact query/state;
- key result ↔ exact requested state;
- transition child ↔ parent canonical authority.

Do not weaken schemas to make tests pass.

## Frontier metric

006 must report actual frontier truth or remove/rename the claim. Do not keep `depth + 1` under the name `frontier_peak`.

## Real canonical bridge

009 is the critical remediation.

C001 did not satisfy acceptance because no real canonical gameplay operation executed.

R01 must establish a real read-only Godot bridge and actually call `invoke()` against canonical ScrubBots gameplay authority.

The runner may orchestrate:
- ProofState;
- ProofKernel;
- SolvabilitySolver;
- required canonical LevelData/supply components.

It may not reimplement those mechanics.

Prove real legal/transition/solver behavior, deterministic repeat, mismatch/error handling and checkout immutability.

`capability()` must not claim AVAILABLE merely because a runner file exists.

If a truly unavoidable environment blocker prevents real execution, record it truthfully. Do not fabricate PASS.

## Replay identity

010 must revalidate current source/execution identity before MATCH.

## Budgets / timeout

011 must enforce visited-state budget during traversal and keep wall-clock timeout occurrence/policy outside canonical deterministic evidence identity.

## Regression lock

012 runs last and must add regression fixtures for every R01 defect plus real canonical invoke coverage.

## R01 master log

After all nine task attempts create:

`.hiveai/codex-logs/SB-LF03-C001-R01_MASTER_REMEDIATION_CODEX_LOG.md`

For each task record:
- task ID;
- R01 builder-log full URL;
- implementation SHA;
- terminal log-only SHA;
- focused tests;
- retained/full regression results;
- skips and exact reasons;
- known blocker/limitation;
- TASKS zero-diff confirmation.

Then run final batch-wide:
- all retained LF03 tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- real canonical bridge/invoke regression;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Commit/push the master remediation log as the final R01 summary commit.

## Final response

Return only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LF03-C001-R01_MASTER_REMEDIATION_CODEX_LOG.md`;
2. final master-log commit SHA;
3. the nine R01 task builder-log GitHub URLs.

Then STOP for independent ChatGPT re-audit.
