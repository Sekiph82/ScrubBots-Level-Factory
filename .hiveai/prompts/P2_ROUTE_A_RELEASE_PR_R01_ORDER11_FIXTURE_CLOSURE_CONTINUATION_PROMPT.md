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

Before any implementation or test work:

1. Verify the persistent Level Factory checkout identity, branch, origin, HEAD, dirty state, stashes/worktrees, and fetch current `origin/main`.
2. Do not modify or discard the owner's dirty persistent checkout.
3. Read task authority from GitHub/`origin/main:TASKS.md`; require `SB-CPX-003 / P2-ROUTE-A-C001-R01`.
4. Reuse only the already authorized temp worktree under `%TEMP%\ScrubBots-Level-Factory\P2-ROUTE-A-C001-R01`.
5. Preserve the existing R01 implementation and append-only builder log.
6. Synchronize the temp worktree non-destructively with current `origin/main` only if incoming changes are non-overlapping coordination/governance changes.
7. If product/test overlap or ambiguity exists, stop before edits.

No new clone/worktree. No changes to the persistent dirty checkout.

## Current state

Retain the already completed R01 work:
- exact rollback snapshot/verification;
- canonical remote override removal;
- rollback/remote regressions;
- Solve/Analyze unavailable-reason fix;
- five Factory Studio action checks PASS;
- Factory Studio committed runtime suite PASS;
- Route A focused suite PASS;
- P1/R02 regression set PASS.

Tracker wording has been repaired by ChatGPT in GitHub. Codex must not edit `TASKS.md`.

The only remaining R01 blocker is F03:
**authentic Route A verifier must run on at least one valid P1-staged production row.**

## Targeted order-11 fixture strategy

Do not continue blind/random search first.

Current Scrubbots authority:
- next catalog order: 11;
- class: EASY;
- target challenge ≈ 20.6828;
- hard publication tolerance for the accepted P1 transaction: use current runtime authority exactly;
- production minimum board dimensions: 20×20.

Use current Scrubbots M53 calibration evidence as a STRUCTURAL STARTING POINT only, not as production difficulty authority.

Promising source fixture:
`coordination/sessions/M53-C002/evidence/corpus_raw/access_band3_24_raw.json`

Reason:
- it is a low-complexity border-access pattern;
- a V1-equivalent proxy from its current raw gameplay evidence is approximately 25.55;
- reducing the same structural pattern from 24×24 to 20×20 removes the positive workload contribution associated with 576 vs 400 cells, putting the design near the order-11 hard boundary before any further entropy/access simplification.

This numeric estimate is a search heuristic only. Final acceptance comes exclusively from the current production V1 analyzer and P1 transaction.

## Required candidate construction

Build a deterministic **20×20 production-valid derivative** of the access-band concept.

Requirements:
- 20×20 exactly for the first targeted attempt;
- 3 canonical colors minimum;
- valid current production color rules;
- all geometry/art must be legitimate logical-cell data;
- no resizing/resampling of production source art;
- create the fixture deterministically through test/helper generation, not by patching Difficulty metadata.

Start with:
1. three broad border-touching bands / regions;
2. low unlock depth;
3. high immediate accessibility;
4. low bottleneck pressure;
5. low slot-color pressure;
6. deliberately skewed but valid 3-color distribution if needed to reduce C while keeping 3 distinct colors.

Run current canonical ZIP supply generation/solve and current production Difficulty V1.

If the first 20×20 access-band candidate is still above the live hard window:
- keep 20×20;
- vary only deterministic structural parameters that can legitimately lower A/B/R/S/C;
- prefer fewer forced states, broader early access, less route detour, lower entropy while retaining 3 colors;
- run a bounded targeted family search around this structure.

Do NOT:
- change progression target;
- widen tolerance;
- lower production minimum dimensions;
- fake challengeScore/class/profile;
- patch Scrubbots authority;
- bypass canonical ZIP solve;
- bypass accepted P1 publication.

## Required success condition

Select one candidate only when current production evidence proves:
- dimensions valid;
- official Difficulty V1 class = required order-11 class;
- official score is inside the live P1 hard tolerance for exact order 11;
- canonical ZIP pipeline READY/SOLVED;
- official profile/evidence complete enough for Release Pool/P1 publication;
- accepted P1 transaction stages it into the isolated full current Scrubbots archive at order 11.

Then run the real default Route A verifier on that staged isolated archive.

Require:
`FACTORY_ROUTE_A_VERIFY_PASS`

The verifier must authentically execute:
- LevelCatalog load + validate_all;
- DifficultyV1CatalogCheck;
- LevelLoader;
- SupplyPlanLoader;
- ProofState;
- SolvabilitySolver solve + replay;
- LevelDifficultyAnalyzerV1;
- metadata challenge-score parity <= 1e-6.

No live Scrubbots mutation. No real branch push/PR.

## Search evidence

Record in the builder log:
- fixture family;
- dimensions;
- exact deterministic parameters/seeds;
- number of candidates attempted;
- each candidate's official V1 D/class;
- selected candidate vector/profile;
- ZIP solve result;
- P1 stage result;
- verifier result.

Stop the targeted family search once a valid candidate is found.

## Tracker recheck

After synchronization rerun the governance/tracker test that previously failed.

GitHub tracker has been repaired by ChatGPT. It must now PASS.

If it still fails, record the exact assertion and stop. Do not edit `TASKS.md`.

## Final verification

Run:
- targeted order-11 authentic verifier integration;
- all P2-R01 focused tests;
- full Route A tests;
- P1 CampaignBuilder/Release Pool regressions;
- R02 publisher/catalog regressions;
- Factory Studio action integration suite;
- Factory Studio committed runtime suite;
- governance/tracker tests;
- full pytest;
- compileall;
- git diff --check.

PASS requires:
- authentic staged order-11 row verifier PASS;
- full pytest green except truthful pre-capability skips;
- tracker guard PASS;
- both Studio suites PASS.

## Publication

Only after all R01 criteria pass:
- commit implementation and builder log separately;
- fetch current GitHub authority again;
- publish only if no overlapping unrelated remote change exists;
- normal non-force update to Level Factory `main`;
- verify published HEAD equals `origin/main`;
- leave the persistent dirty Desktop checkout untouched.

## Builder log

Continue:
`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md`

Append chronology only.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md
