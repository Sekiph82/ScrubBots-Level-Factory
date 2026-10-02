# P1-M10-R01 — CampaignBuilder Closure Audit Criteria

Parent owner prompt:
`.hiveai/prompts/P1_M10_CAMPAIGN_BUILDER.md`

Parent strict audit:
`.hiveai/audits/P1_M10_CAMPAIGN_BUILDER_STRICT_AUDIT.md`

Owner decision:
`docs/decisions/OWNER_RELEASE_POOL_BATCH_PUBLICATION_V01.md`

## PASS rule

PASS only if P1-F01..F03 close while all already-passing P1 behavior remains unchanged.

## F01 — Current game LevelCatalog must actually PASS

Required authentic integration:
- current read-only `Sekiph82/Scrubbots origin/main`;
- isolated temporary authority fixture/archive;
- P1 batch publication into that fixture;
- real current `scripts/data/level_catalog.gd::load_manifest()`;
- actual success marker and zero exit code.

When Godot + canonical game checkout are present:
- timeout is FAIL, not SKIP;
- increase the bounded timeout or narrow fixture setup as needed;
- do not replace current LevelCatalog with a Python imitation;
- do not edit Scrubbots source.

The resulting batch catalog must validate with the exact current game loader.

## F02 — Runtime authority must be consumed fail-closed

CampaignBuilder must require from current progression authority:
- `challengeTolerance.preferredWhenPoolIsLarge`;
- `challengeTolerance.defaultPlusMinus`;
- `challengeTolerance.neverForceLabelOutsidePlusMinus`;
- current `recoveryGuards`.

No numerical fallback copies of current policy values.

Validation:
- finite numeric values;
- nonnegative;
- preferred <= default <= hard;
- malformed/missing authority => CampaignError and no plan artifact/publish.

Recovery target slots used for recovery B/U checks must derive from current `recoveryGuards`, including `toNextCycleSlot`.

No literal `{1,4,6,9}` policy set.

## F03 — Axis-specific profile comparisons

If pool-relative medians remain the operational interpretation for qualitative “high/low” rules:
- repeated high-W uses median(W);
- high-B uses median(B);
- recovery B uses median(B);
- recovery U uses median(U).

Add tests with intentionally different W/B/U distributions so using the wrong axis cannot accidentally pass.

Do not invent scalar F:
- current game authority says no supported scalar Frustration Risk is claimed;
- retain truthful warning/unavailable evidence for high-F sequencing.

## Retain existing PASS behavior

Do not redesign:
- Release Pool semantics;
- ACCEPT => Release Pool only;
- owner APPROVE boundary;
- Hungarian global assignment;
- stable deterministic tie behavior;
- hard tolerance/class eligibility;
- tier reporting;
- sequential repair;
- first-hole contiguous prefix;
- shortage reports;
- deterministic plan hash;
- owner lock/swap revalidation;
- batch all-or-nothing rollback;
- existing catalog preservation;
- Studio Release UI;
- K=100 synthetic example;
- P2 pending boundary.

## Regression

Required:
- F01 authentic LevelCatalog integration PASS;
- F02 missing/malformed authority negative tests;
- F03 distinct-axis median tests;
- all existing CampaignBuilder tests PASS;
- all Release Pool/publication tests PASS;
- P3/P3-R01 tests remain PASS;
- full pytest green except unrelated truthful capability skips;
- compileall PASS;
- Factory Studio headless/runtime PASS;
- git diff --check PASS.

Builder must not edit:
- root TASKS.md;
- original P1 prompt;
- P3/P3-R01 prompts;
- .hiveai/audits/**;
- prior logs.
