# P1-M10-R01 — CampaignBuilder Strict Closure — Independent Audit

Date: 2026-10-02
Auditor: ChatGPT
Verdict: **PASS / CLOSED**

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/P1_M10_CAMPAIGN_BUILDER_STRICT_AUDIT.md`

R01 audit criteria:
`.hiveai/audit-criteria/P1_M10_CAMPAIGN_BUILDER_R01_AUDIT_CRITERIA.md`

Builder log:
`.hiveai/codex-logs/P1_M10_CAMPAIGN_BUILDER_R01_CODEX_LOG.md`

Implementation commit:
`b6c904cdc6693f6adbc4def570334a0f081bdc63`

Builder-log publication commit:
`f831f38772bffbe15b8f50d4149de3379126b9dc`

## Executive result

All four findings F01..F04 from the parent P1 audit are closed without redesigning the accepted Release Pool / CampaignBuilder architecture.

The accepted owner flow remains:
- owner ACCEPT moves a READY level into the Release Pool only;
- CampaignBuilder assigns accepted production candidates to the next contiguous catalog slots;
- owner APPROVE authorizes publication of the contiguous publishable prefix;
- publication is an all-or-nothing batch transaction;
- P2 remains pending and was not invented.

## F01 — Real current-game LevelCatalog proof — PASS

The integration test now:
- uses the repository Godot discovery convention;
- creates a full isolated archive of current `Sekiph82/Scrubbots origin/main`;
- publishes the proposed batch only inside the temporary game fixture;
- invokes the real current-game `LevelCatalog.load_manifest()`;
- requires explicit `CAMPAIGN_LEVEL_CATALOG_PASS`;
- treats timeout/nonzero as failure when Godot + game authority exist.

Final focused evidence:
`tests/integration/test_release_batch_level_catalog.py = 1 passed` in 13.80s against Scrubbots authority `df59ea2553d5b2842a9f8d191cc6482a127f5c9b`.

Earlier timeout/API/indentation failures are retained in the builder chronology and were not counted as PASS.

## F02 — Runtime tolerance/recovery authority — PASS

`campaign_builder.py` now:
- requires `challengeTolerance`;
- requires `preferredWhenPoolIsLarge`, `defaultPlusMinus`, and `neverForceLabelOutsidePlusMinus`;
- validates finite, nonnegative numeric values and `preferred <= default <= hard`;
- raises `CampaignError` on missing/malformed authority;
- derives recovery targets from configured `recoveryGuards` `toSlot` and `toNextCycleSlot`;
- contains no literal `{4, 6, 9, 1}` recovery set.

No copied CampaignBuilder tolerance fallback remains.

## F03 — W/U/B axis-correct comparisons — PASS

CampaignBuilder now computes independent pool medians:
- W from vector index 0;
- U from vector index 3;
- B from vector index 4.

The sequence logic uses:
- W median for repeated high-W;
- U median for recovery low-U;
- B median for recovery low-B;
- B median for high-B adjacency.

Focused tests deliberately separate W/U/B medians and prove the former shared-B-median defect is closed.

No unsupported scalar F was invented.

## F04 — Official Difficulty V1 profile + catalog-boundary history — PASS

Release Pool admission now:
- consumes nested `official_difficulty_v1.profile.dominant`;
- binds the complete official profile to immutable Release Pool evidence;
- validates official challenge score/vector/profile;
- fails closed when official profile evidence is missing/malformed;
- does not recompute the current game dominant-profile formula as production authority.

Current game authority now retains the final two production-catalog entries.

Authority resolution is:
1. official catalog metadata when hash-bound official Difficulty V1 evidence exists;
2. otherwise hash-bound current-game M53 Difficulty V1 evidence;
3. otherwise `CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE`.

The profile-run rule is evaluated across the existing-catalog/new-batch boundary. Regression coverage includes:
- FLOW, FLOW, then FLOW => blocked/reassigned;
- FLOW, COLOR, then FLOW => not rejected merely because FLOW occurred two positions back.

## Preserved P1 architecture — PASS

Independent inspection confirms the remediation did not replace:
- deterministic Hungarian global assignment;
- exact class + hard-tolerance eligibility;
- first-hole contiguous prefix;
- shortage reporting;
- owner lock/swap revalidation;
- deterministic plan hash;
- APPROVE boundary;
- transactional batch publication/rollback;
- immutable existing catalog entries;
- P2 pending boundary.

Implementation diff is scoped to nine P1-R01 files plus the deterministic K=100 evidence refresh.

## Regression evidence

Builder evidence:
- R01 focused combined set: **31 passed**;
- real current-game LevelCatalog integration: **PASS**;
- Factory Studio committed runtime suite marker: **PASS**;
- full pytest: **1176 passed, 3 skipped, 1 warning**;
- compileall: **PASS**;
- `git diff --check`: **PASS**.

The three skips are capability/opt-in scoped and do not include the required LevelCatalog acceptance test.

## Audit note for resumed final-cutover work

The preserved `MAINT-ZIP-CORE-V02-C001-R02` prompt predates the owner Release Pool decision and still contains old `owner ACCEPT auto-publishes` wording.

Before R02 execution, its prompt/criteria must be reconciled so that:
- ACCEPT performs zero game writes and enters Release Pool only;
- CampaignBuilder owner APPROVE is the publication authorization;
- the publication batch starts at the next catalog order and remains contiguous;
- proposed-batch LevelCatalog + DifficultyV1CatalogCheck validation occurs before production writes;
- publication uses current runtime tolerance authority fail-closed, without numeric fallback.

## Final disposition

`P1-M10-R01 = PASS / CLOSED`

`P1-M10 = PASS / CLOSED`

Tracker IDs `SB-LF10-001..SB-LF10-008` are satisfied by the accepted P1 implementation + R01 closure and may be marked PASS/CLOSED.

Next authorized action:
resume `MAINT-ZIP-CORE-V02-C001-R02` only after reconciling its paused prompt/audit criteria with `OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01`.
