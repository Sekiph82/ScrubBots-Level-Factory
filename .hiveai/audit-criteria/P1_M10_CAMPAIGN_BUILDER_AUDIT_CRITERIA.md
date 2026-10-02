# PROMPT P1 — M10 CampaignBuilder: batch campaign sequencing for accepted levels

Document role: CHATGPT AUDIT CRITERIA

Authoritative owner prompt:
`.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md`

Exact owner prompt SHA-256:
`09de3ed5f15edf47a56f0135299467abacda2560c1381ec9ec888ef2fbc0afe1`

Owner decision:
`docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md`

Tracker scope:
`SB-LF10-001 ... SB-LF10-008`

## PASS rule

PASS only if the implementation satisfies the owner P1 prompt without modifying accepted level data to force campaign fit and without retyping stale game-policy constants as Level Factory authority.

## A. Release Pool boundary

- Owner ACCEPT moves a READY accepted level into the Release Pool.
- ACCEPT does not immediately publish.
- ACCEPT does not choose its own catalog order.
- owner REJECT does not enter Release Pool.
- pool entries bind candidate/level identity, official Difficulty V1 score, challenge vector, profile, novelty/signature evidence, session load, files and digests.

## B. Runtime game authority

CampaignBuilder must read the current game authority at runtime/read-only:
- progression/cadence config;
- tolerance ladder;
- recovery guards;
- production catalog;
- profile diversity / novelty rules from current game architecture docs/config.

Do not duplicate those values as independent Level Factory policy constants.

Tests may use exact isolated fixtures.

## C. Deterministic slots and eligibility

For current catalog size N and requested K:
- consider slots N+1...N+K;
- derive target/class/role/novelty from current progression authority;
- candidate eligibility requires score within the current hard tolerance and class compatibility;
- cost uses absolute target delta plus the requested tier penalties;
- stable ID order resolves exact ties.

Never assign outside the current hard tolerance.

## D. Global assignment

Use deterministic global minimum-cost assignment over the eligible candidate/slot graph.

Allowed implementation:
- Hungarian;
- min-cost flow;
- deterministic equivalent;
- numpy only / existing dependencies.

No greedy first-fit may remain as campaign sequencing authority.

Small-pool tests must compare against brute-force optimal cost.

## E. Sequential repair

After global assignment:
- evaluate current recovery guards;
- evaluate profile-run rules;
- evaluate high-W/high-B/high-F/recovery constraints;
- evaluate configured multi-field similarity/novelty constraints;
- repair only through deterministic swaps/reassignment from unused pool;
- never violate the hard difficulty tolerance;
- CampaignBuilder never edits a level/art/supply to make it fit.

## F. Contiguity

Publication plan is a contiguous prefix only.

If N+j cannot be filled:
- publishable prefix ends at N+j-1;
- no later slot is published;
- remaining requested positions are shortage;
- catalog order contains no hole.

## G. Shortage report

Each shortage includes:
- catalog number;
- class;
- target;
- allowed range;
- nearest unused candidates;
- deterministic failure reasons.

The report is upstream generation input only.
CampaignBuilder itself does not regenerate or mutate levels.

## H. Campaign plan artifact

Write deterministic:
`campaign_plan.json`

Schema:
`scrubbots-campaign-plan/v1`

Must bind:
- catalog digest;
- progression/authority digest;
- Release Pool identities/digests;
- requested K;
- per-slot target/class/role/chosen identity/score/delta/tier;
- guard/profile/similarity checks;
- shortages;
- deterministic plan hash.

Same inputs => identical semantic plan + identical plan hash.

Rebuild does not regenerate levels.

## I. Studio Release view

Studio exposes:
- Release Pool size vs K;
- plan rows;
- target vs actual difficulty;
- tiers;
- warnings/shortages;
- owner lock/swap;
- APPROVE.

Owner lock/swap is revalidated against all eligibility/guard/similarity/contiguity rules.

Invalid manual swaps fail closed.

## J. Batch publication

APPROVE publishes the chosen contiguous prefix as ONE transaction.

Requirements:
- explicit level_number per item;
- all-or-nothing staging/commit;
- injected failure => rollback/no partial catalog;
- existing catalog entries unchanged;
- exact new orders contiguous;
- resulting catalog loads through current game LevelCatalog.

Owner ACCEPT alone must not publish.

## K. P2 boundary

Prompt P2 is not currently present in this repository.

Do not invent branch/PR/store-update behavior not supplied by P2.

P1 may implement the local batch publication transaction and Release Pool/CampaignBuilder boundary.
Any P2-only distribution automation must be reported as pending with evidence.

## L. Tests

Required:
- assignment optimality vs brute force;
- hard tolerance never exceeded;
- tier behavior;
- class compatibility;
- first-hole contiguous stop;
- every recovery guard;
- profile run limit;
- similarity limit;
- shortage content;
- deterministic tie-breaking;
- deterministic plan hash;
- rebuild without regeneration;
- owner lock/swap revalidation;
- ACCEPT => Release Pool only;
- APPROVE => one batch transaction;
- rollback on injected failure;
- existing catalog entries unchanged;
- current game LevelCatalog accepts published fixture;
- K=100 synthetic pool example artifact/report;
- no level-data mutation by CampaignBuilder;
- full pytest green except truthful capability skips;
- compileall PASS;
- Factory Studio headless/runtime PASS;
- git diff --check PASS.

## Governance

Builder must not edit root TASKS.md or .hiveai/audits/**.

P1 owner prompt remains immutable.
