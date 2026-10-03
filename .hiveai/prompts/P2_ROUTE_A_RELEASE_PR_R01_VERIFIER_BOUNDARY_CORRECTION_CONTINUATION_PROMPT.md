# P2-ROUTE-A-C001-R01 — Strict Closure Remediation

Document role: CODEX CONTINUATION PROMPT

Repository: `Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/P2_ROUTE_A_RELEASE_PR_STRICT_AUDIT.md`

Corrected R01 criteria:
`.hiveai/audit-criteria/P2_ROUTE_A_RELEASE_PR_R01_AUDIT_CRITERIA.md`

## FIRST OPERATION — mandatory local ↔ GitHub synchronization

Before any implementation or testing:

1. Verify the persistent Level Factory checkout identity, branch, origin, HEAD, dirty state, stashes/worktrees, then fetch current `origin/main`.
2. Do not modify or discard the owner's dirty persistent checkout.
3. Read current task authority from GitHub/`origin/main:TASKS.md`; require `SB-CPX-003 / P2-ROUTE-A-C001-R01`.
4. Reuse only the already authorized temp R01 worktree.
5. Preserve all existing R01 implementation and append-only builder-log history.
6. Synchronize the temp worktree non-destructively with current `origin/main` only when incoming changes are non-overlapping coordination/governance changes.
7. Stop if safe preservation/synchronization is ambiguous.

No new clone/worktree. No persistent-checkout edits.

## Why the verifier criterion changed

Do not continue searching for an Order-11 candidate.

Current Scrubbots evidence shows that early Difficulty V1 progression targets are not calibrated to the existing production population:
- production Level 1 is 20×20 and has official D1 ≈ 46.03 against target 20;
- existing EASY production levels are approximately 45–51;
- eight targeted valid 20×20 R01 candidates still bottomed out at D1 ≈ 29.47, above the Order-11 hard ceiling ≈ 24.18.

Therefore Order-11 candidate availability is a separate calibration/content-availability issue. It must not block proof that Route A's real default verifier actually executes against current game authority.

Do not alter progression, tolerance, Difficulty V1, production dimensions, or P1 publication rules.

## F03 corrected closure

Replace the empty-row verifier proof with a **non-empty canonical current-game production row**.

Use a full isolated current Scrubbots archive/temp project and at least one existing production-catalog row with its real current files.

Preferred:
- choose a current catalog row that has a valid supply plan and canonical solver evidence;
- keep the row byte-identical to current Scrubbots authority;
- do not fabricate challenge metadata.

Invoke the REAL default Route A verifier, not an injected stub.

Require:
`FACTORY_ROUTE_A_VERIFY_PASS`

Authentically execute:
- LevelCatalog load + validate_all;
- DifficultyV1CatalogCheck;
- LevelLoader;
- SupplyPlanLoader;
- ProofState;
- SolvabilitySolver solve + replay;
- LevelDifficultyAnalyzerV1 measurement/score;
- metadata parity checks supported by the current row.

The plan/row set must be non-empty.

No live Scrubbots mutation.
No real branch push or PR.

## Preserve independent P1 publication evidence

Do not remove or weaken:
- P1 CampaignBuilder/Release Pool regression tests;
- R02 exact contiguous publication/catalog tests;
- rollback tests;
- canonical remote tests.

Those tests remain the publication-transaction proof. F03 is the authentic real-game verifier proof.

## Tracker

ChatGPT has repaired the protected tracker wording. Codex must not edit `TASKS.md`.

Rerun the governance/tracker guard after synchronization. It must pass.

## Final verification

Run:
- non-empty authentic verifier integration;
- all P2-R01 focused tests;
- full Route A tests;
- P1 CampaignBuilder/Release Pool regressions;
- R02 publisher/catalog regressions;
- Factory Studio action suite;
- Factory Studio committed runtime suite;
- governance/tracker tests;
- full pytest;
- compileall;
- git diff --check.

PASS requires:
- non-empty authentic verifier PASS;
- P1/R02 publication regressions PASS;
- tracker guard PASS;
- both Studio suites PASS;
- full pytest green except truthful pre-capability skips.

## Publication

Only after all R01 criteria pass:
- commit implementation and builder log separately;
- fetch current GitHub authority again;
- publish only if no overlapping unrelated remote changes appeared;
- normal non-force update to Level Factory `main`;
- verify published HEAD equals `origin/main`;
- leave the persistent dirty Desktop checkout untouched.

## Builder log

Continue:
`.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md`

Append chronology only. Record the abandoned Order-11 search as retained negative evidence and explicitly note the corrected verifier boundary.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P2_ROUTE_A_RELEASE_PR_R01_CODEX_LOG.md
