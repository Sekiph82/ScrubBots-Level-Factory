# P1-M10-R01 — CampaignBuilder Strict Closure — Audit Criteria

Parent owner prompt:
`.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md`

Parent strict audit:
`.hiveai/audits/P1_M10_CAMPAIGN_BUILDER_STRICT_AUDIT.md`

Owner decision:
`docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md`

## PASS rule

PASS only if F01..F04 from the parent audit close without redesigning the accepted Release Pool / CampaignBuilder architecture.

## A. Current-game LevelCatalog proof

When Godot + canonical read-only Scrubbots authority are present:
- post-publish temp fixture MUST load through the real current game `LevelCatalog`;
- actual PASS marker required;
- timeout is failure, not skip;
- no Python imitation substitutes for LevelCatalog.

Use an isolated archive/temp game copy only.

A truthful capability skip is allowed only if Godot or canonical game authority is genuinely unavailable before the test starts.

## B. Runtime policy consumption

CampaignBuilder must require runtime authority fields:
- preferredWhenPoolIsLarge;
- defaultPlusMinus;
- neverForceLabelOutsidePlusMinus;
- recoveryGuards.

No copied fallback values.

Validate:
- finite/nonnegative;
- preferred <= default <= hard.

Recovery target slots must be derived from `recoveryGuards`, including cross-cycle `toNextCycleSlot`.

No literal recovery-slot set.

Malformed/missing authority => fail closed.

## C. Correct axis comparisons

If pool-relative medians remain the operationalization of qualitative docs:
- repeated high-W compares W against median(W);
- high-B compares B against median(B);
- recovery U compares U against median(U);
- recovery B compares B against median(B).

Tests must use deliberately different W/U/B medians.

No scalar F may be invented.

## D. Official profile authority

For new Release Pool entries:
- consume current official Difficulty V1 `profile.dominant` when available;
- do not recompute the current game profile formula as Level Factory authority.

If official profile is absent/malformed:
- fail closed for CampaignBuilder eligibility or explicitly mark profile unavailable;
- do not silently manufacture a production profile.

## E. Existing catalog tail history

Campaign sequence checks must include enough existing production history to enforce cross-boundary constraints.

At minimum:
- last two existing catalog levels for dominant-profile run limit;
- last existing level for adjacency/recovery/similarity checks.

Authority order:
1. current official metadata/evidence if present;
2. otherwise read-only current game Difficulty V1 analysis for the required existing catalog levels;
3. otherwise fail closed with explicit boundary-evidence-unavailable status.

Do not silently default prior production profiles to BALANCED.

Required regression:
- existing order N-1 FLOW;
- existing order N FLOW;
- new N+1 FLOW candidate;
- N+1 FLOW must be rejected/reassigned.

## F. Preserve accepted P1 behavior

Do not change:
- ACCEPT -> Release Pool only;
- deterministic Hungarian global assignment;
- exact class + hard tolerance eligibility;
- first-hole contiguous prefix;
- shortage report;
- owner lock/swap revalidation;
- deterministic plan hash;
- APPROVE boundary;
- all-or-nothing batch transaction;
- existing catalog entries immutable;
- P2 remains pending/uninvented.

## G. Regression

Required:
- focused F01..F04 tests;
- current game LevelCatalog real PASS;
- brute-force assignment test;
- tolerance tier tests;
- all recovery guards;
- profile run;
- novelty/similarity;
- K=100 example determinism;
- batch rollback;
- Release Pool admission;
- Studio Release runtime;
- full pytest green except truthful pre-capability skips;
- compileall PASS;
- git diff --check PASS.

Builder must not edit root TASKS.md, original P1 prompt, prior audits, or prior logs.
