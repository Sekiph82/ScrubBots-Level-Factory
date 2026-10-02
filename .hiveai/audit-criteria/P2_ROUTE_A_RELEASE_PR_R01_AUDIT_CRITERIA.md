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

An integration test must execute the real default verifier against a full isolated current Scrubbots archive/temp project.

Require authentic execution of:
- LevelCatalog load + validate_all;
- DifficultyV1CatalogCheck;
- LevelLoader;
- SupplyPlanLoader;
- ProofState;
- SolvabilitySolver solve + replay;
- LevelDifficultyAnalyzerV1 measurement/score;
- metadata score parity <= 1e-6;
- explicit `FACTORY_ROUTE_A_VERIFY_PASS`.

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
