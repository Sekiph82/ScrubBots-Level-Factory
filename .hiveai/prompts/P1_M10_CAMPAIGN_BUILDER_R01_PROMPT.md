# P1-M10-R01 — CampaignBuilder Strict Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Parent owner prompt:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md

Parent strict audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/P1_M10_CAMPAIGN_BUILDER_STRICT_AUDIT.md

R01 audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/P1_M10_CAMPAIGN_BUILDER_R01_AUDIT_CRITERIA.md

Owner decision:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md

## Scope

Modify ONLY:
`Sekiph82/ScrubBots-Level-Factory`.

Scrubbots remains READ-ONLY authority.

Do NOT redesign CampaignBuilder.
Do NOT change the original P1 prompt.
Do NOT change P3, which is PASS/CLOSED.
Do NOT invent P2 behavior.

Close only F01..F04 from the parent P1 audit.

## Mandatory sync preflight

1. Work only in `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
2. Verify repository `Sekiph82/ScrubBots-Level-Factory`, branch `main`.
3. Fetch/prune.
4. Inspect HEAD/origin/status/ahead-behind/stashes/worktrees.
5. Fast-forward when safe.
6. Preserve owner material.
7. No reset/rebase/stash/clean/force/discard.
8. No sibling clone/worktree.
9. Stop if safe sync is impossible.

# R01.1 — Make real current-game LevelCatalog validation PASS

Current test currently times out at 15s and skips.

Fix the integration proof, not by weakening it.

Use the canonical read-only Scrubbots checkout:
`C:\Users\sekip\Desktop\Scrubbots`
when available, or equivalent authorized Git authority.

Recommended:
- create a FULL isolated `git archive origin/main` temp game fixture rather than a partial scripts/data extraction;
- publish the candidate batch into that temp copy;
- run current game LevelCatalog against the resulting catalog;
- preferably reuse the game’s current `tests/m35_level_catalog.gd` seam or a tiny script that invokes the same `LevelCatalog.load_manifest()`;
- use the repository’s Godot discovery convention;
- allow a bounded first-load timeout sufficient for actual headless startup/import.

When Godot + game authority exist:
- timeout = FAIL;
- nonzero = FAIL;
- require explicit PASS output.

Only a true missing pre-capability may skip.

Never mutate the owner’s live game checkout.

# R01.2 — Remove copied runtime policy defaults

In `campaign_builder.py`:

REMOVE fallback copies for:
- 5.0 hard tolerance;
- 3.5 default tolerance;
- 2.0 preferred tolerance.

Require the current authority’s `challengeTolerance` object.

Validate all three values:
- exact numeric finite;
- >= 0;
- preferred <= default <= hard.

If missing/malformed:
`CampaignError`.

Do not build a plan.

REMOVE the literal recovery set:
`{4, 6, 9, 1}`.

Derive recovery target slots from current `recoveryGuards`:
- each `toSlot`;
- each `toNextCycleSlot`.

Use those derived targets for recovery low-B/U checks.

Do not retype cadence/recovery policy.

# R01.3 — Fix W/U/B axis-specific thresholds

Current code uses B median for W and U.

Keep the existing pool-relative median interpretation only if you preserve it consistently.

Compute separate:
- W median from vector index 0;
- U median from vector index 3;
- B median from vector index 4.

Use:
- repeated high-W => W vs W median;
- recovery low-U => U vs U median;
- recovery low-B => B vs B median;
- high-B back-to-back => B vs B median.

Add a fixture where medians differ dramatically and prove each rule uses its own axis.

Do not invent a scalar F. Keep the truthful high-F-unavailable warning.

# R01.4 — Consume official profile authority

Current game `LevelDifficultyAnalyzerV1` already emits:

`profile: { dominant, scores, runnerUp }`

inside `official_difficulty_v1`.

In Release Pool admission:
- consume `official_difficulty_v1.profile.dominant`;
- bind it into immutable Release Pool evidence;
- do not recompute FLOW/COLOR/FORTRESS/ROUTE/MARATHON formulas in Level Factory for new production evidence.

If official profile evidence is missing/malformed:
- fail Release Pool/CampaignBuilder eligibility truthfully;
- do not silently default/recompute.

Keep historical/research compatibility separate if needed.

# R01.5 — Enforce profile history across catalog boundary

Current `_game_authority()` retains only one prior catalog level.

That is insufficient for:
`no same dominant profile more than 2 consecutive`.

Load sufficient current existing-catalog context.

Minimum:
- N-1 and N profiles for the profile-run rule;
- N challenge/vector/signature for adjacency/recovery/similarity.

Important: current First-10 metadata may not contain Challenge V1 profile/vector fields.

Therefore resolve boundary evidence in this order:

1. use current official metadata/evidence if it actually contains official Difficulty V1 profile/vector/signature;
2. otherwise obtain current official Difficulty V1 analysis read-only for the required catalog levels using current game authority;
3. if that cannot be obtained, fail campaign planning closed with a clear `CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE` or equivalent.

Do NOT:
- default missing prior profile to BALANCED;
- recompute a fake prior profile from old class/dimensions;
- ignore missing history.

Regression:
- N-1 FLOW;
- N FLOW;
- candidate for N+1 FLOW;
- plan must reject/reassign N+1 FLOW.

Also test:
- N-1 FLOW;
- N COLOR;
- N+1 FLOW is not rejected merely because FLOW appeared two positions back.

# R01.6 — Preserve existing P1 architecture

Do not alter accepted:
- ACCEPT -> Release Pool only;
- Hungarian assignment;
- class/tolerance eligibility;
- shortage generation;
- first-hole contiguity;
- plan hash;
- owner locks/swaps;
- APPROVE;
- publish_batch transaction;
- rollback;
- P2 pending boundary.

# Required tests

Run:
- P1-R01 focused tests;
- existing CampaignBuilder tests;
- Release Pool tests;
- batch publication/rollback;
- real LevelCatalog integration;
- K=100 deterministic example;
- Studio Release headless runtime;
- full pytest;
- compileall;
- git diff --check.

Full pytest must be green except truthful skips where capability is missing BEFORE the test starts.

If Godot + game authority exist, LevelCatalog integration may not skip on timeout.

## Builder governance

Do not edit:
- root `TASKS.md`;
- original P1 prompt;
- `.hiveai/audits/**`;
- prior logs;
- P3 PASS artifacts.

Create before product edits:
`.hiveai/codex-logs/P1_M10_CAMPAIGN_BUILDER_R01_CODEX_LOG.md`

Commit implementation separately from final log publication.

Push Level Factory `main`.
Fetch again.
Prove local/origin 0/0.

STOP for independent ChatGPT re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P1_M10_CAMPAIGN_BUILDER_R01_CODEX_LOG.md
