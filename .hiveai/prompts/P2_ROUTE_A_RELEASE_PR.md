# PROMPT P2 — Route A release: publish an approved campaign batch as a game-repo PR

Repository: `Sekiph82/ScrubBots-Level-Factory`. Target: the local checkout of
`Sekiph82/Scrubbots` (configured game project path). Depends on P1 (approved `campaign_plan.json`).
Follow GOVERNANCE.md / AGENTS.md / CLAUDE.md. Track it under M14 (Route A subset) or a new
owner-approved extension ID chosen by the tracker owner.

## Goal

After the owner approves a campaign plan, produce a reviewable pull request in the game repo that
adds the batch (levels N+1 … N+M). Players receive it through the next store build (owner builds
and submits; out of scope here).

## Hard rules

- Never push to `main`; never force-push; never rewrite history. Branch + PR only.
- Preflight must pass or nothing is written: game checkout on `main`, clean working tree, in sync
  with `origin/main` (fetch first), configured remote is `Sekiph82/Scrubbots`, `gh` authenticated.
- Only these paths may change: `data/levels/<id>.json`, `data/levels/supply/<id>_supply_v1.json`,
  `data/levels/metadata/<id>.metadata.json`, `assets/art/levels/previews/<id>.png`,
  `data/levels/catalog/production_catalog_v1.json` (append-only entries). Any other diff = abort.
- The game repo is PUBLIC: warn the owner in the UI that unreleased levels become publicly visible
  once pushed (owner may switch the repo to private or use a private staging repo).

## Steps

1. Preflight (above). Branch `levels/release-<N+1>-<N+M>`.
2. Batch publish into the checkout (P1 transaction).
3. Game-side verification headless with the game's own code, all must pass:
   LevelCatalog load + validate_all; for every new level: LevelLoader + SupplyPlanLoader load,
   SolvabilitySolver.replay of the recorded solution trace (or solve) = SOLVED / WIN, official
   LevelDifficultyAnalyzerV1 score equals the score in metadata (tolerance 1e-6).
4. Commit (one commit, message `levels: release N+1..N+M (<count> levels)` + plan hash).
5. Push the branch; open the PR with `gh pr create`: body = campaign table (n, class, target, D,
   delta, tier, size, colours), shortage summary, verification results, plan hash, Level Factory
   commit SHA. Label `levels-release`.
6. Record a release receipt (`release_receipt.json`: plan hash, branch, commit SHA, PR URL, file
   digests) in Level Factory output; Studio shows it.
7. Failure at any step: delete the local branch, restore the checkout to the preflight state,
   keep evidence; no partial PR.

## Tests

Preflight refusals (dirty tree, wrong branch, behind origin, wrong remote, gh not authed), path
allow-list enforcement, verification failure aborts before commit, rollback restores the checkout
byte-for-byte, PR body generation, idempotency (same plan twice → refuses: catalog collision).
Use a temporary local bare remote in tests; never touch the real remote in tests.
