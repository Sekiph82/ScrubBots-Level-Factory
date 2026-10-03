# P2-ROUTE-A-C001-R01 — Strict Closure Audit Criteria

Parent audit:
`.hiveai/audits/P2_ROUTE_A_RELEASE_PR_STRICT_AUDIT.md`

## PASS rule

PASS only if P2 F01..F03 close while preserving the accepted Route A architecture.

## A. Exact rollback

For every injected failure after preflight:
- final branch equals preflight branch;
- final HEAD equals preflight HEAD;
- final tracked/index/worktree state equals preflight;
- final untracked-path set equals preflight;
- operation-created allow-list and non-allow-list paths are absent;
- local release branch is absent;
- pushed release branch is removed;
- created PR is closed when a later step fails;
- failure evidence is retained outside the game checkout.

Required tests:
- allow-list violation;
- verifier failure;
- local-commit/pre-push failure;
- push/PR-create failure;
- post-PR label/edit failure.

No test may expect post-preflight game-repo residue to survive.

## B. Canonical remote identity

Production Route A:
- has no caller-controlled `expected_remote` or equivalent authorization override;
- compares `origin` to the fixed canonical `Sekiph82/Scrubbots` identity;
- Studio request cannot override target identity.

Tests may replace a private/internal authority seam only.

Regression must prove an arbitrary production origin is refused and cannot be authorized by function/request arguments.

## C. Authentic current-game verifier execution

An integration test must execute the real default verifier against a full isolated current Scrubbots archive/temp project with a **non-empty real current-game production row**.

This verifier proof is intentionally separated from CampaignBuilder frontier eligibility. Current Scrubbots Difficulty V1 evidence shows the existing production EASY population is materially above early progression targets, so requiring a newly generated Order-11 row inside the current live tolerance would conflate verifier integration with a separate calibration/content-availability problem.

Required verifier input:
- use at least one existing canonical production-catalog row from current Scrubbots authority, or an exact isolated copy of such a row bound to its real level/supply/metadata files;
- the row set must be non-empty;
- do not use an empty plan;
- do not fake metadata or analyzer output.

Require authentic execution of:
- LevelCatalog load + validate_all;
- DifficultyV1CatalogCheck;
- LevelLoader;
- SupplyPlanLoader;
- ProofState;
- SolvabilitySolver solve + replay;
- LevelDifficultyAnalyzerV1 measurement/score;
- metadata score parity <= 1e-6 where the current row carries official Difficulty V1 metadata;
- explicit `FACTORY_ROUTE_A_VERIFY_PASS`.

The accepted P1/R02 publication transaction remains independently required by section D/E regressions. This verifier integration test does not need to invent a currently unavailable Order-11 candidate merely to exercise the real game verifier.

If Godot + canonical game authority exist, timeout/nonzero/API mismatch/missing marker is failure, not skip.

No live game checkout mutation and no real remote push/PR.

## D. Preserve accepted behavior

Retain:
- CampaignBuilder APPROVE;
- stale/current-input plan revalidation;
- deterministic release branch;
- exact contiguous P1 transaction;
- normal allow-list;
- one release commit with plan hash;
- branch-only push;
- PR content + label;
- public-repo warning;
- release receipt;
- collision/idempotency refusal.

## E. Regression

Required:
- P2-R01 focused suite green;
- prior Route A suite green;
- authentic verifier integration PASS when capability exists;
- P1 regression green;
- R02 publication regression green;
- governance tests green;
- full pytest green except truthful pre-capability skips;
- compileall PASS;
- git diff --check PASS;
- Factory Studio runtime/action integration PASS.

Builder must not edit root TASKS.md, audits, prior logs, or active prompt/criteria.
