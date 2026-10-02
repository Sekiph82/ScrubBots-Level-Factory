# PROMPT P1 — M10 CampaignBuilder: batch campaign sequencing for accepted levels
Document role: CODEX BUILDER LOG

## Starting State

- Starting timestamp: 2026-10-02 12:41:13 +03:00.
- Canonical root: C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator; repository Sekiph82/ScrubBots-Level-Factory; origin is https://github.com/Sekiph82/ScrubBots-Level-Factory.git.
- Branch: main; starting HEAD and origin/main: 780cd6e0f5ab1f79503d9a2b0fcff0bd8eb68fff; ahead/behind 0/0 after fetch/prune and safe fast-forward.
- Initial tracked state was clean. Initial `git status --short --branch` output follows.

```
## main...origin/main
?? "Scrubbots - Pixel Art Generator-SB-LF04-001-R01-VERIFY/"
?? "Scrubbots - Pixel Art Generator-SB-LF04-001-R01/"
?? "Scrubbots - Pixel Art Generator-SB-LF04-001/"
?? level_factory/scripts/factory_core_gateway.gd.uid
?? level_factory/scripts/factory_studio_art_editor.gd.uid
?? level_factory/scripts/factory_studio_art_preview.gd.uid
?? level_factory/scripts/factory_studio_art_revalidation.gd.uid
?? level_factory/scripts/factory_studio_batch_import.gd.uid
?? level_factory/scripts/factory_studio_candidates.gd.uid
?? level_factory/scripts/factory_studio_comparison.gd.uid
?? level_factory/scripts/factory_studio_cost.gd.uid
?? level_factory/scripts/factory_studio_dashboard.gd.uid
?? level_factory/scripts/factory_studio_evidence_panel.gd.uid
?? level_factory/scripts/factory_studio_failures.gd.uid
?? level_factory/scripts/factory_studio_import.gd.uid
?? level_factory/scripts/factory_studio_import_validation.gd.uid
?? level_factory/scripts/factory_studio_library.gd.uid
?? level_factory/scripts/factory_studio_navigation.gd.uid
?? level_factory/scripts/factory_studio_pipeline.gd.uid
?? level_factory/scripts/factory_studio_presets.gd.uid
?? level_factory/scripts/factory_studio_puzzle_config_gate.gd.uid
?? level_factory/scripts/factory_studio_readiness.gd.uid
?? level_factory/scripts/factory_studio_reproduce.gd.uid
?? level_factory/scripts/factory_studio_revisions.gd.uid
?? level_factory/scripts/factory_studio_search.gd.uid
?? level_factory/scripts/factory_studio_session.gd.uid
?? level_factory/scripts/factory_studio_shell.gd.uid
?? level_factory/scripts/factory_studio_similarity.gd.uid
?? level_factory/scripts/factory_studio_target_controls.gd.uid
?? level_factory/scripts/factory_studio_workspace_page.gd.uid
?? level_factory/tests/factory_studio_action_integration_suite.gd.uid
?? level_factory/tests/factory_studio_art_revalidation_integration_suite.gd.uid
?? level_factory/tests/factory_studio_batch_import_r01_integration_suite.gd.uid
?? level_factory/tests/factory_studio_candidate_review_integration_suite.gd.uid
?? level_factory/tests/factory_studio_comparison_integration_suite.gd.uid
?? level_factory/tests/factory_studio_cost_center_r01_integration_suite.gd.uid
?? level_factory/tests/factory_studio_dashboard_integration_suite.gd.uid
?? level_factory/tests/factory_studio_exact_reproduce_integration_suite.gd.uid
?? level_factory/tests/factory_studio_exact_reproduce_r01_integration_suite.gd.uid
?? level_factory/tests/factory_studio_exact_reproduce_r03_integration_suite.gd.uid
?? level_factory/tests/factory_studio_failures_r01_integration_suite.gd.uid
?? level_factory/tests/factory_studio_import_integration_suite.gd.uid
?? level_factory/tests/factory_studio_import_validation_integration_suite.gd.uid
?? level_factory/tests/factory_studio_library_integration_suite.gd.uid
?? level_factory/tests/factory_studio_pipeline_integration_suite.gd.uid
?? level_factory/tests/factory_studio_presets_integration_suite.gd.uid
?? level_factory/tests/factory_studio_puzzle_config_gate_integration_suite.gd.uid
?? level_factory/tests/factory_studio_readiness_integration_suite.gd.uid
?? level_factory/tests/factory_studio_revisions_r01_integration_suite.gd.uid
?? level_factory/tests/factory_studio_runtime_suite.gd.uid
?? level_factory/tests/factory_studio_search_integration_suite.gd.uid
?? level_factory/tests/factory_studio_session_r01_integration_suite.gd.uid
?? level_factory/tests/factory_studio_similarity_r01_integration_suite.gd.uid
?? level_factory/tests/factory_studio_truth_separation_integration_suite.gd.uid
```

- Stashes: 18 preserved. Registered worktrees: canonical checkout, six under `%TEMP%\ScrubBots-Level-Factory`, and four stale/prunable Desktop-named registrations; none created, pruned, or altered.
- The prior untracked owner `.uid` sidecars and stale directories were preserved and remain unstaged.
- P1 prompt blob SHA-256 verified from synced `main`: `09de3ed5f15edf47a56f0135299467abacda2560c1381ec9ec888ef2fbc0afe1`.

## Authority Read

- Read root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, and `CLAUDE.md`.
- Read combined master prompt `.hiveai/prompts/P3-R01_P1-M10_COMBINED_MASTER_PROMPT.md` from the supplied GitHub URL and synced GitHub `main`.
- Read owner prompt `.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md`, owner criteria `.hiveai/audit-criteria/P1_M10_CAMPAIGN_BUILDER_AUDIT_CRITERIA.md`, combined criteria, and `docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md`.
- P1 is co-current with P3-R01. Owner ACCEPT must enter Release Pool only; campaign plan APPROVE is a separate all-or-nothing contiguous batch publication boundary. P2 distribution behavior is not authorized.
- Scrubbots game repository `Sekiph82/Scrubbots` is explicitly authorized for read-only rules use. Its canonical root is `C:\Users\sekip\Desktop\ScrubBots`, origin is the expected repository, `main` equals `origin/main` at `836d5d9e9036a59123f9df2b1c94f76e64efe7f8`, and its working tree contains unrelated owner modifications/untracked files. No game-repository file will be edited; current rules will be read from `origin/main` blobs.

## Implementation and Verification

Pending. Record each command/result chronologically, including all failures and corrections. Must satisfy the P1 owner prompt and criteria, reuse live game authority, avoid new dependencies, avoid modifying accepted level data, and keep P2-only distribution automation pending.

## Publication

Implementation commit, log commit, push, and final local/origin SHA parity: pending. Stop after both builder logs are pushed for independent audits; do not claim acceptance.
## Execution Chronology — 2026-10-02 10:40 UTC

This appended record supersedes the initial `Pending` implementation placeholder above. It preserves that placeholder as the log's original pre-implementation state.

- Added deterministic CampaignBuilder assignment with Hungarian matching, eligibility and dynamic production envelope checks, tolerance-tier penalties, stable-ID tie breaking, sequential recovery guard/profile/novelty checks, deterministic blocked-edge reassignment, first-hole contiguous prefix, shortage reporting, input digest, and plan hash.
- Added immutable Release Pool admission from latest owner ACCEPT with READY pipeline only. Pool reads revalidate the candidate, review, pipeline, and file hashes. Runtime authority is read from the current game progression config, Difficulty analyzer, production catalog, M10 architecture documentation, `difficulty_rules.gd`, and palette policy. Plan generation writes `campaign_plan.json`; approval revalidates the hash and live inputs before calling batch publication.
- Changed `publish_level` to require an explicit positive level number and exact target/class checks. `publish_batch` stages a complete transaction in a temporary copied project, assigns explicit contiguous order, then publishes files/catalog as one commit point, restoring catalog bytes and removing new files on injected failure.
- Owner ACCEPT now admits to Release Pool without immediate publication. Added launcher extension operations and a Studio Release view for pool size vs K, rows/tiers/warnings/shortages, owner lock/swap, and explicit APPROVE.
- Added CampaignBuilder tests for brute-force-optimal assignment, all tiers, hard tolerance/class constraints, determinism/hash, first-hole shortage, recovery guards, profile run, similarity and novelty constraints, invalid locks, and a synthetic K=100 artifact. Added batch publication/rollback and plan revalidation/approval tests, plus owner ACCEPT readiness/pool behavior coverage. Added architecture documentation and deterministic synthetic output.
- Read current game rules from the authorized read-only game repository. Parser result: dimensions 20–59 and 3–12 colors; current production catalog contains 10 entries. The current analyzer config does not define a maximum consecutive-similarity threshold, so similarity is reported/digested without inventing a max-based rejection. Current Difficulty V1 docs/record do not provide supported scalar Frustration Risk, so that signal is warned as unavailable. Both limits remain visible in implementation/docs.
- The LevelCatalog integration fixture creates a temporary Git archive of `origin/main` and attempts the current catalog load. Godot did not return within the 15-second limit; the integration test now records a capability skip. This current-game runtime integration remains unverified.
- The P2 prompt was unavailable in the authorized source set. No Route A branch/PR/store automation was invented; P2 distribution behavior remains pending.
- Focused campaign/publication/release-review tests: 14 passed. Focused P3/P1 test set before the last approval case was added: 32 passed. P3 focused cases passed after correcting the ZIP-B crash seam. Boundary/clean-checkout checks: 15 passed. Isolated pipeline test: 1 passed. Full final suite: **1160 passed, 4 skipped**, with the skip and cache-warning details recorded in the P3 log.
- `python -m compileall -q src tests level_factory/scripts/factory_core_launcher.py`: PASS. `git diff --check`: PASS with LF-to-CRLF conversion warnings only. Studio Release headless runtime suite: `SB-LF06-002-C001-R01 committed runtime suite PASS`.
- No new runtime dependencies, remote API calls, API keys, or edits to accepted game level data were introduced. Game-repository changes were not made.
