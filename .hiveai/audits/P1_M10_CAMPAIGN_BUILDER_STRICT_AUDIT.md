# PROMPT P1 — M10 CampaignBuilder — Strict Audit

Date: 2026-10-02
Auditor: ChatGPT
Verdict: **CHANGES_REQUIRED**

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/P1_M10_CAMPAIGN_BUILDER_CODEX_LOG.md`

Implementation commit:
`e935264a7ff5ae9b7eb3fe1538760b36c9d04fba`

Owner prompt:
`.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md`

Owner decision:
`docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md`

## Executive result

The main architecture is correct and must be preserved:

- owner ACCEPT now enters the Release Pool instead of publishing;
- owner REJECT does not enter the active pool;
- CampaignBuilder is deterministic;
- candidate-slot assignment uses a rectangular Hungarian global assignment;
- exact difficulty class and hard-tolerance eligibility are enforced;
- tolerance tiers are recorded;
- sequence violations are repaired by blocking the offending edge and globally reassigning;
- first empty slot truncates the publishable prefix;
- shortage reports are generated;
- plan inputs are content-digested and plan hash is deterministic;
- owner lock/swap is revalidated;
- Studio Release view exists;
- APPROVE revalidates the live plan/pool/catalog before publication;
- batch publication uses explicit contiguous level numbers and rollback on injected write failure;
- existing catalog entries are preserved;
- P2 branch/PR/store automation was correctly not invented;
- full repository suite is green: **1160 passed, 4 skipped**.

However, three P1 requirements are not yet closed.

## F01 — Required current-game LevelCatalog integration remains UNVERIFIED

P1 explicitly requires:
`catalog loads through the game's LevelCatalog after publish`.

The builder created a genuine current-game integration fixture using:
- a Git archive of current `Sekiph82/Scrubbots origin/main`;
- the real `scripts/data/level_catalog.gd`;
- a published batch fixture.

But the Godot call timed out at 15 seconds and the test converted this to:
`pytest.skip(... LevelCatalog headless load did not return within 15 seconds ...)`.

Builder log correctly says:
`The LevelCatalog runtime load is unverified, not a pass.`

Because this is an explicit P1 acceptance test, it cannot remain a capability skip when:
- Godot is present;
- the canonical game repository is present;
- the fixture was successfully constructed.

**Disposition: BLOCKER.**

### Required closure

Make the current-game LevelCatalog integration deterministically executable:
- use the repository's existing Godot executable discovery conventions;
- keep the game authority read-only;
- use an isolated archive/fixture;
- allow a bounded timeout appropriate to first-load script parsing/import rather than 15 seconds if needed;
- require actual `CAMPAIGN_LEVEL_CATALOG_PASS`;
- timeout is FAIL for this specific required integration when the capability exists, not SKIP.

Do not replace the real game LevelCatalog with a Python imitation.

## F02 — P1 says runtime rules are consumed, but CampaignBuilder re-types/falls back to policy values

Owner P1:
`Rules to consume (never re-type; read from the game config at run time)`.

Current `campaign_builder.py` still embeds fallback copies of current tolerance values:
- hard tolerance fallback `5.0`;
- preferred fallback `2.0`;
- default fallback `3.5`.

The same implementation also identifies recovery slots with the literal set:
`{4, 6, 9, 1}`
for B/U profile checks.

The current game authority already supplies:
- all three challengeTolerance values;
- recovery guards defining their target slots.

CampaignBuilder must fail closed if those required runtime fields are missing/malformed rather than silently use copied current values.

Recovery targets must be derived from the current `recoveryGuards` authority, not literal slot numbers.

**Disposition: MAJOR.**

### Required closure

- require `preferredWhenPoolIsLarge`, `defaultPlusMinus`, and `neverForceLabelOutsidePlusMinus`;
- validate them as finite nonnegative numeric values with preferred <= default <= hard;
- no copied numerical fallback;
- derive recovery target slots from current recoveryGuards, including `toNextCycleSlot`;
- malformed/missing authority => `CampaignError`, zero plan publication.

Do not retype the owner cadence/tolerance/recovery policy in Level Factory.

## F03 — W and U profile comparisons use the B-axis median

Current sequence logic computes:

`median = median(B)`

then uses that same scalar for:
- recovery B check — appropriate for B;
- recovery U check — wrong axis;
- repeated high-W check — wrong axis.

Later high-B back-to-back correctly uses a B-specific median.

Therefore current profile repair can misclassify:
- high-W adjacency;
- recovery U suitability.

This is a real logic defect independent of the chosen pool-relative median interpretation.

**Disposition: MAJOR.**

### Required closure

If the current implementation continues using pool-relative medians to operationalize the qualitative docs:
- W must compare against median(W);
- B must compare against median(B);
- U must compare against median(U).

Add targeted fixtures where W/B/U medians differ and prove the correct axis is used.

Do not invent a scalar F. Current game `level_difficulty_analysis_v1.json` explicitly states no supported scalar Frustration Risk is claimed. The existing warning for unavailable high-F sequencing is truthful and may remain.

## Independently accepted P1 behavior

### Release Pool — PASS

`record_owner_review(..., ACCEPT)` no longer calls immediate game publication.

It invokes Release Pool admission only when:
- latest owner review is ACCEPT;
- canonical pipeline is READY;
- official Difficulty V1 evidence is available.

Release Pool evidence binds:
- candidate/artwork/grid identity;
- official score/vector/profile;
- canonical files + SHA-256;
- pipeline identity/digest;
- owner review identity.

Pool reads revalidate those identities.

### Global assignment — PASS

The Hungarian implementation is deterministic and the focused test compares its minimum assignment cost with brute-force permutations.

Actual candidate-slot eligibility enforces:
- current class label;
- hard tolerance;
- production dimension/color envelope.

### Contiguity / shortage — PASS

At first unfilled slot:
- publishable prefix stops;
- later slots are not publishable;
- shortage records contain slot/class/target/range/nearby unused candidate reasons.

### Recovery guards — PASS structurally, pending F02/F03 correction

Configured recoveryGuards are evaluated on adjacent actual official challenge scores.

No hard-tolerance violation is introduced by repair.

### Similarity / novelty — PASS under current game authority

Current game `level_difficulty_analysis_v1.json` operationally defines combined similarity from:
- challenge-vector similarity;
- palette Jaccard;
- dimension similarity.

The implementation matches those three current operational fields.

The current game does not provide a configured `maxConsecutiveSimilarity` threshold. The builder correctly reports this as unavailable instead of inventing a threshold.

Slot `noveltyTarget` is still applied.

### High-F — truthful limitation

Current game authority explicitly says:
- only provisional choice-opacity pieces exist;
- no supported scalar F is claimed.

The builder reports high-F adjacency as unavailable rather than manufacturing a number.

This is acceptable under P1 section 6: report rules that could not be applied with evidence.

### Batch transaction — PASS at unit level

Verified focused tests:
- contiguous explicit orders;
- existing catalog entries preserved;
- injected write failure removes new files and restores original catalog bytes.

F01 still requires authentic current-game LevelCatalog load proof.

### K=100 example — PASS

A deterministic synthetic K=100 example artifact is generated and explicitly documented as synthetic/non-production.

## Regression evidence

Builder final:
- focused campaign/publication/release tests: PASS;
- P3/P1 focused set: PASS;
- boundary checks: PASS;
- full pytest: **1160 passed, 4 skipped**;
- compileall: PASS;
- git diff --check: PASS;
- Studio Release headless runtime: PASS.

Three environment/capability skips unrelated to P1 acceptance may remain truthful.

The current-game LevelCatalog timeout skip is NOT accepted for P1 because it is an explicit owner-required integration test and the capability existed.

## Final disposition

`P1-M10 = CHANGES_REQUIRED`

Preserve the implementation and remediate only:
1. real current-game LevelCatalog PASS evidence;
2. fail-closed runtime tolerance/recovery authority consumption;
3. correct W/B/U axis-specific profile comparisons.

No CampaignBuilder redesign is authorized.
