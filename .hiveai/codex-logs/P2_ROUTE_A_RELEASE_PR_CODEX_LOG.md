# PROMPT P2 — Route A release: publish an approved campaign batch as a game-repo PR
Document role: CODEX BUILDER LOG

## Session start — 2026-10-02 16:08 +03:00 (Europe/Istanbul)

- Canonical implementation repository: `Sekiph82/ScrubBots-Level-Factory`, root `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, branch `main`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Initial local HEAD was `f831f38772bffbe15b8f50d4149de3379126b9dc`; initial tracked state was clean. Fetch found `origin/main` nine commits ahead at `7a4b2e887ae8fbc6e4c0db87b9f9990dc69d9d7a`; reviewed and fast-forwarded safely. Pre-edit local HEAD equals `origin/main`, divergence `0/0`.
- Preserved preexisting untracked SB-LF04 directories and Godot `.uid` sidecars. Inspected stashes/worktrees without changing them.
- Read `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`, current P2 prompt and audit criteria, reconciled R02 prompt and audit criteria, R02 parent audit, P1-M10-R01 audit, and owner V02/Release Pool decisions.
- P2 is co-current under `SB-CPX-003`. This work implements and tests Route A capability only; no actual approved `campaign_plan.json` was supplied. Tests must use only a temporary local bare remote. No push/PR to `Sekiph82/Scrubbots`, no game `main` mutation, and no real release operation will be performed in this implementation cycle.
- No product code or tests were changed or run before creating this log.

## Scope and execution

Pending. Append P2-only design, commands, failures/corrections, tests, and publication evidence. Keep Route A implementation and evidence distinct from R02.

## P2 Route A implementation and validation chronology — 2026-10-02

- Implemented a dedicated `release_route_a.py` service and wired CampaignBuilder APPROVE to it. Route A requires explicit Studio approval, revalidates the exact stored campaign-plan hash and current source inputs before branch creation, checks canonical remote / clean exact `main` / `origin/main` equality and `gh` authentication, and uses a deterministic `levels/release-N-M` branch.
- Route A calls the existing P1 transaction for exact contiguous assigned orders, validates current game catalog/level/supply/solver/replay/Difficulty V1 parity, enforces the file allow-list and append-only catalog, creates one provenance-rich commit, pushes only the release branch, opens/labeled the PR, and persists a hash-bound receipt. Refusal/failure handling attempts scoped rollback and records factory-side failure evidence. Launcher remains a thin dispatcher; it invokes the route service without embedding subprocess operations.
- Studio now names the action “APPROVE and Open Release PR”, displays the public-repository exposure warning, and surfaces PR/branch/game commit/receipt details. Public visibility warning is included in the PR body and receipt response.
- Route tests use only temporary local game repositories and local bare remotes with stubbed `gh`, publisher, and verifier. They cover success, preflight refusals, stale plan before branch creation, allow-list rejection, verifier rollback, push failure after local commit, PR creation failure after push cleanup, and idempotency/collision.
- Early Route A focused run caught the test's expected branch being `release-1-2` instead of the deterministic `levels/release-1-2`; corrected the fixture expectation. Subsequent route/publisher runs passed. Full R02/P2 suite initially had 14 failures; fixes are detailed in the R02 log, including legacy M07 compatibility, the catalog pass marker, and thin-launcher subprocess constraint.
- Final focused/static verification: R02 authority, M02 interface/request, dimension envelope, batch publisher, Route A, game catalog load, and M09 CLI tests -> 119 passed; Python compileall and `git diff --check` passed (Git emitted only LF-to-CRLF normalization notices).
- The Route A and related M07/catalog/launcher focused regression set -> 39 passed. Full repository regression -> 1,163 passed, 3 skipped, 2 owner-tracker failures from the live protected `TASKS.md` (246 declared / 247 parsed and current-task parser mismatch); no tracker edits were made.
- Godot runtime suite exited 0. Action integration suite exited 0 with its deliberate missing-artwork diagnostics at the corruption/recovery probe, followed by all expected integration PASS markers.
- No real `campaign_plan.json` was supplied. Therefore there was no mutation of the actual Sekiph82/Scrubbots checkout, no push to that repository, and no real pull request. No dependency/license changes or runtime network access were added.
- Exact final diff, implementation commit, final log commit, and factory branch publication evidence will be appended when complete.

## Scoped commit and pre-push evidence — 2026-10-02

- The distinct R02 implementation commit is `5f4e30a...`; the distinct Route A implementation commit is `0ac1bc7...`. No tracker, active prompt, handoff, or audit path is part of either implementation commit.
- Final fetch/prune preflight confirmed canonical repository root and exact origin, branch `main`, current HEAD `0ac1bc70606bf2b74c87147d18c254a52f3dfc10`, `origin/main` `7a4b2e887ae8fbc6e4c0db87b9f9990dc69d9d7a`, divergence 2 ahead / 0 behind. Existing 18 stashes and worktrees were inspected and left unchanged.
- Preserved the preexisting untracked SB-LF04 directories and Godot `.uid` sidecars; none are included in the Route A or R02 commits. Git reported line-ending-related modified status markers for committed test fixtures while `git diff` showed no content diff and their hashes matched HEAD; these were not re-staged or overwritten.
- The final publication work is limited to the Level Factory `main` branch. Route A was tested against temporary local repos only; it did not push to Scrubbots or open a game PR.

## Publication result — 2026-10-02

- `git push origin main` succeeded after final fetch/prune and exact branch/origin/divergence checks. Published range: `7a4b2e887ae8fbc6e4c0db87b9f9990dc69d9d7a..59294b4b6a9ad37cdcd3f81c4b4b25e27ff73a46`, including both implementation commits and the first combined builder-log commit.
- Immediately after publication, local `main` and `origin/main` both resolved to `59294b4b6a9ad37cdcd3f81c4b4b25e27ff73a46`. This log-only publication note will itself be pushed as a final append; exact equality will be checked again.
- There was no supplied live campaign plan, so no actual Scrubbots branch, commit, push, or PR was created. Route A remains implemented and locally verified with a temporary remote.
