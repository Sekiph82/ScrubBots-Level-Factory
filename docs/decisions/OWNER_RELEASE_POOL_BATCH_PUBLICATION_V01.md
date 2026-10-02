# OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01

Status: OWNER APPROVED
Date: 2026-10-02

Source authority:
`.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md`

Source prompt SHA-256:
`09de3ed5f15edf47a56f0135299467abacda2560c1381ec9ec888ef2fbc0afe1`

## Decision

This decision supersedes the earlier product rule:
`owner ACCEPT auto-publishes`.

The new owner authority is:

- Owner ACCEPT moves a READY level into the Release Pool.
- ACCEPT does not publish immediately.
- ACCEPT does not choose a catalog order.
- Campaign publication happens per release batch.
- Default release batch size is K=100 and is configurable.
- CampaignBuilder assigns the pool into the next contiguous catalog range `N+1 ... N+K`.
- The owner reviews/approves the campaign plan.
- The approved batch is published as one all-or-nothing transaction.
- Existing catalog entries are never modified by CampaignBuilder.
- Distribution Route A (game repo branch + PR/store update) is governed by separate prompt P2.
- Distribution Route B (.scrubpack/CDN, M11-M20) remains future work.

## Interaction with current work

P3 / P3-R01 headless processing still stops at the owner Review Queue and never ACCEPTs or publishes.

MAINT-ZIP-CORE-V02-C001-R02 remains paused while P3-R01 + P1-M10 are active. Any older R02 wording that assumes ACCEPT immediately publishes is superseded by this decision and must be reconciled before R02 resumes.

## CampaignBuilder authority

CampaignBuilder consumes, but does not rewrite:
- accepted level artifacts;
- official Difficulty V1;
- challenge vector/profile/signature evidence;
- current game progression/cadence/tolerance/recovery rules;
- current production catalog.

CampaignBuilder never modifies level data to force a fit. Shortages request more generation upstream.
