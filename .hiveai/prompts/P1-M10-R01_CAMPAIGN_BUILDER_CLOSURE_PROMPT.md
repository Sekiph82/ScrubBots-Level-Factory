# P1-M10-R01 — CampaignBuilder Closure

Document role: CODEX REMEDIATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Original P1 owner prompt:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md

Parent strict audit:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/P1_M10_CAMPAIGN_BUILDER_STRICT_AUDIT.md

R01 audit criteria:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audit-criteria/P1-M10-R01_CAMPAIGN_BUILDER_CLOSURE_AUDIT_CRITERIA.md

Owner decision:
https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md

## Mandatory sync preflight

1. Work only in:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
2. Verify repository:
   `Sekiph82/ScrubBots-Level-Factory`
3. Verify branch `main`.
4. `git fetch origin --prune`.
5. Inspect HEAD/origin/status/ahead-behind/stashes/worktrees.
6. Fast-forward only when safe.
7. Preserve owner material non-destructively.
8. No reset/rebase/stash/clean/force/discard.
9. No new sibling Desktop clone/worktree.
10. Stop before edits if safe synchronization is impossible.

## Scope

P3 and P3-R01 are PASS/CLOSED.
Do not modify their product behavior or tests except unavoidable regression compatibility.

Preserve the existing P1 architecture.

Close ONLY P1-F01, F02 and F03.

Scrubbots remains READ-ONLY authority.

## R01.1 — Make the real current LevelCatalog integration PASS

Current test:
`tests/integration/test_release_batch_level_catalog.py`

The current skip after a 15-second timeout is not closure.

Use the canonical game checkout read-only and keep the test isolated.

Requirements:
- discover current Godot executable using existing repository conventions instead of assuming one spelling if necessary;
- archive/copy current `Sekiph82/Scrubbots origin/main` into a temp fixture;
- publish the test batch into that temp fixture;
- invoke the real current `scripts/data/level_catalog.gd`;
- require `load_manifest().is_ok()`;
- require `CAMPAIGN_LEVEL_CATALOG_PASS`;
- require exit code 0.

When Godot + canonical checkout exist:
- timeout must fail;
- use a larger but bounded timeout suitable for first parse/import if 15 seconds is insufficient;
- do not skip the required integration merely because it is slow.

If the real LevelCatalog rejects the published content:
- diagnose the actual current-game error;
- fix only the narrow Level Factory publication defect;
- do not weaken game validation;
- do not edit Scrubbots.

## R01.2 — Remove retyped tolerance/recovery policy

In `campaign_builder.py`:

REMOVE numerical policy fallbacks for:
- preferred tolerance;
- default tolerance;
- hard tolerance.

Require all exact current authority fields.

Validate:
```
0 <= preferred <= default <= hard
```
and every value finite numeric.

Missing/malformed => `CampaignError`.

No plan should be written or published from malformed authority.

Replace literal recovery-slot detection:
```
{1,4,6,9}
```
with values derived from current `recoveryGuards`:
- each `toSlot`;
- each `toNextCycleSlot`.

Use those derived targets for recovery B/U profile checks.

Do not retype current cadence/recovery positions.

## R01.3 — Correct W/B/U axis medians

Current bug:
one B-axis median is reused for W and U comparisons.

Fix with distinct deterministic medians:
- `median_w`;
- `median_b`;
- `median_u`.

Rules:
- repeated high-W compares W to median_w;
- high-B back-to-back compares B to median_b;
- recovery B compares B to median_b;
- recovery U compares U to median_u.

Do not invent a scalar F.
Keep the current truthful warning that high-F sequencing cannot be enforced because current game authority claims no supported scalar Frustration Risk.

Add focused tests where:
- W distribution differs sharply from B;
- U distribution differs sharply from B;
- the prior buggy B-median reuse would produce the opposite verdict.

## Required regression

Run:
- targeted LevelCatalog integration;
- CampaignBuilder authority-negative tests;
- W/B/U axis tests;
- complete CampaignBuilder unit suite;
- release pool tests;
- batch publication/rollback tests;
- plan approval tests;
- Studio Release headless runtime;
- P3 + P3-R01 focused tests;
- full pytest;
- compileall;
- git diff --check.

Full pytest must be green except unrelated truthful environment capability skips.
The required LevelCatalog integration itself may not be skipped when capability exists.

## Builder governance

Do not edit:
- root `TASKS.md`;
- original P1 prompt;
- P3/P3-R01 prompts;
- `.hiveai/audits/**`;
- prior logs.

Create before edits:
`.hiveai/codex-logs/P1-M10-R01_CAMPAIGN_BUILDER_CLOSURE_CODEX_LOG.md`

Commit implementation separately from final log publication.

Push Level Factory `main`.
Fetch again.
Prove local HEAD == origin/main and ahead/behind 0/0.

Stop for independent ChatGPT re-audit.

## Final response

Return only:

https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/P1-M10-R01_CAMPAIGN_BUILDER_CLOSURE_CODEX_LOG.md
