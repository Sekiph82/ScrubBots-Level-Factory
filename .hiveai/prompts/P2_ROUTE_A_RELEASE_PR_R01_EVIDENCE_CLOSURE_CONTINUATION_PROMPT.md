# P2-ROUTE-A-C001-R01 — Strict Closure Remediation

Document role: CODEX CONTINUATION PROMPT

Repository: `Sekiph82/ScrubBots-Level-Factory`

Parent remediation:
`.hiveai/prompts/P2_ROUTE_A_RELEASE_PR_R01_PROMPT.md`

Parent audit:
`.hiveai/audits/P2_ROUTE_A_RELEASE_PR_STRICT_AUDIT.md`

R01 criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_R01_AUDIT_CRITERIA.md`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

Before any implementation or testing:

1. Verify the persistent Level Factory checkout identity, branch, origin, current HEAD, dirty state, stashes/worktrees, and fetch current `origin/main`.
2. Do not modify or discard the owner's dirty persistent checkout.
3. Read current task authority from GitHub/`origin/main:TASKS.md`; require `SB-CPX-003 / P2-ROUTE-A-C001-R01`.
4. Reuse only the already authorized temp R01 worktree under `%TEMP%\ScrubBots-Level-Factory\P2-ROUTE-A-C001-R01`.
5. Preserve all existing uncommitted R01 work and builder-log chronology.
6. Compare the temp worktree base with current `origin/main`. If incoming GitHub commits are coordination-only and do not overlap R01 product/test files, synchronize non-destructively while preserving the implementation. If overlap or ambiguity exists, stop.
7. After synchronization, confirm the temp worktree contains current TASKS, prompt, criteria, AGENTS and GOVERNANCE before continuing.

No new clone/worktree. No changes to the persistent dirty checkout.

## Previous attempt state

Retain the already implemented work unless defective:
- exact checkout snapshot / rollback verification;
- removal of public `expected_remote` override;
- Route A rollback and remote-identity regressions;
- authentic verifier integration scaffold;
- existing R01 builder log.

Previous focused result: **43 passed**.

Previous broad result: **1145 passed, 3 skipped, 6 failed**:
- one protected tracker wording failure;
- five Factory Studio action failures.

The authentic verifier executed against a full current game archive, but no valid staged P1 publication row existed, so F03 remains open.

## Closure A — authentic verifier with a REAL staged P1 row

Do not weaken F03.

The integration must stage at least one valid representative level through the accepted P1 publication transaction into a full isolated current Scrubbots archive, then run the real Route A default verifier and require `FACTORY_ROUTE_A_VERIFY_PASS`.

Current order 11 authority from the previous attempt:
- target challenge ≈ 20.6828;
- live tolerance ±3.5;
- acceptable range ≈ 17.1828..24.1828.

The prior valid 20×20 fixtures scored ≥26.72; the ~20.325 sample was 3×1 and invalid.

Find or deterministically generate a **valid current-production** candidate that:
- satisfies production dimensions;
- matches order 11 class/target within live tolerance;
- passes canonical ZIP supply/solve;
- is accepted by the existing P1 batch publication path.

Allowed:
- inspect canonical candidate/release evidence;
- inspect valid current fixtures;
- run a bounded deterministic seed/size/color search through the existing canonical pipeline.

Forbidden:
- changing minimum dimensions;
- widening tolerance;
- changing progression target;
- faking metadata;
- bypassing P1 publication;
- hand-creating game files that did not pass P1;
- changing Scrubbots difficulty authority.

Record the exact selected candidate, score/class, dimensions, search evidence, P1 staging result, and authentic verifier PASS.

The verifier must execute real LevelCatalog, DifficultyV1CatalogCheck, LevelLoader, SupplyPlanLoader, ProofState, SolvabilitySolver solve/replay, LevelDifficultyAnalyzerV1, and metadata parity <=1e-6.

Do not modify the live Scrubbots checkout and do not open/push a real game PR.

## Closure B — five Factory Studio action failures

Run the five failing tests individually.

For each:
- record exact test and assertion;
- classify as R01 regression, stale accepted-contract fixture, sync artifact, or unrelated preexisting issue;
- fix only if justified.

Then require:
- all five pass;
- Factory Studio action integration suite PASS;
- Factory Studio committed runtime suite PASS.

Do not blanket-edit tests.

## Closure C — tracker wording failure

Codex must not edit root `TASKS.md`.

After synchronization rerun the exact tracker/governance failure.

If it passes, record that the earlier failure came from stale local authority.

If it still fails:
- record exact assertion and current GitHub tracker lines;
- stop before publication;
- leave tracker repair to ChatGPT.

## Reverify F01/F02

Require:
- exact rollback to preflight state for all injected failures;
- no operation-created residue in game checkout;
- no caller-controlled production remote override;
- production remote identity fixed to canonical `Sekiph82/Scrubbots`.

## Final verification

Run:
- P2-R01 focused tests;
- full Route A tests;
- authentic staged-row verifier integration;
- P1 CampaignBuilder/Release Pool regressions;
- R02 publisher/catalog regressions;
- the five Studio action tests;
- both Factory Studio Godot suites;
- governance/tracker tests;
- full pytest;
- compileall;
- git diff --check.

PASS requires full pytest green except truthful pre-capability skips, both Studio suites PASS, and staged-row authentic verifier PASS.

Do not publish an audit-incomplete implementation.

## Builder log

Continue:
`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md`

Append chronology only; do not rewrite earlier entries.

## Publication

Only after every R01 criterion passes:
- commit implementation and builder log separately;
- fetch current GitHub authority again;
- publish only if no unrelated overlapping remote change appeared;
- use a normal non-force update to Level Factory `main`;
- verify published HEAD equals current `origin/main`;
- leave the persistent dirty Desktop checkout untouched.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md
