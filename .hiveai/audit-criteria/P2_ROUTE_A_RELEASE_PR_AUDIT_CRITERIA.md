# P2 — Route A Release PR — Strict Audit Criteria

Owner prompt:
`.hiveai/prompts/P2_ROUTE_A_RELEASE_PR.md`

Tracker:
`SB-CPX-003` under M14 Route A subset.

## PASS rule

PASS only if the Level Factory can take an owner-approved P1 CampaignBuilder plan and safely prepare a reviewable Scrubbots game-repository branch + PR without ever pushing or mutating `main`, while preserving exact rollback and real game-side verification.

## A. Preconditions / authorization

- P1-M10 is PASS/CLOSED.
- Input is an owner-approved `campaign_plan.json`; unapproved/stale/mismatched plan is rejected.
- Preflight requires:
  - configured target repository is exactly `Sekiph82/Scrubbots`;
  - checkout is on `main`;
  - working tree is clean;
  - fetch has completed and local `main` is exactly in sync with `origin/main`;
  - `gh` is authenticated.
- Any failed preflight => zero game writes, zero branch push, zero PR.

## B. Git safety

- Never push directly to `main`.
- Never force-push.
- Never rewrite history.
- Release branch name is deterministic: `levels/release-<N+1>-<N+M>`.
- One release commit only, with message `levels: release N+1..N+M (<count> levels)` and plan hash evidence.
- Tests use a temporary local bare remote only and never touch the real remote.

## C. Allowed diff boundary

Only:
- `data/levels/<id>.json`;
- `data/levels/supply/<id>_supply_v1.json`;
- `data/levels/metadata/<id>.metadata.json`;
- `assets/art/levels/previews/<id>.png`;
- append-only `data/levels/catalog/production_catalog_v1.json`.

Any other game-repo diff => abort and restore preflight state.

## D. P1 transaction / exact order

- Uses the accepted P1 CampaignBuilder explicit contiguous orders.
- Existing catalog entries remain immutable.
- No gap or order scan-forward is introduced.
- Catalog collision / same plan twice fails closed.
- Owner ACCEPT alone does not invoke this route; Route A starts only after CampaignBuilder owner APPROVE.

## E. Real game-side verification

Before commit/push/PR:
- current game LevelCatalog loads and `validate_all` passes;
- every new level loads through current LevelLoader;
- every new supply plan loads through current SupplyPlanLoader;
- current SolvabilitySolver replay of recorded trace, or canonical solve when replay is unavailable by contract, ends SOLVED / WIN;
- current LevelDifficultyAnalyzerV1 score equals metadata score within 1e-6.

Any failure => no commit, no push, no PR.

## F. PR content / public-repo warning

PR body includes:
- campaign table: n, class, target, D, delta, tier, size, colours;
- shortage summary;
- game verification results;
- plan hash;
- Level Factory commit SHA.

PR gets label `levels-release`.

Studio must clearly warn that the Scrubbots repository is public and pushing the release branch makes unreleased levels publicly visible.

## G. Release receipt

After successful branch push + PR creation, Level Factory records `release_receipt.json` with at least:
- plan hash;
- branch;
- game commit SHA;
- PR URL;
- file digests.

Studio surfaces the receipt.

Receipt must be bound to the exact approved plan and game commit.

## H. Failure / rollback

At any failure point:
- restore target checkout byte-for-byte to its preflight state;
- remove the local release branch created by this operation;
- do not leave a partial pushed release/PR created by the failed operation;
- preserve failure evidence in Level Factory.

Focused tests must prove rollback after injected failures before commit, after local commit but before push, and during PR-open handling where safely simulatable with the local test remote/stubs.

## I. Regression

Required:
- dirty-tree refusal;
- wrong-branch refusal;
- behind/diverged refusal;
- wrong-remote refusal;
- unauthenticated-gh refusal;
- allow-list rejection;
- game verification failure abort;
- exact rollback;
- PR body generation;
- idempotent collision refusal;
- public-repo warning;
- release receipt;
- existing P1 Release Pool/CampaignBuilder tests remain green;
- full pytest green except truthful capability skips;
- compileall PASS;
- git diff --check PASS.
