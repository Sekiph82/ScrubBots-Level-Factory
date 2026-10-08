# Factory Studio Exact Three-Master UI V03

Status: OWNER-LOCKED / CANONICAL UI AUTHORITY
Date: 2026-10-08
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Final owner decision

The Factory Studio owner UI has exactly three production screens and must visually match the three approved repository masters.

There is no alternative layout interpretation.

There are no additional owner production pages.

There are no explanatory paragraphs on the three production screens.

There are no extra panels, extra navigation entries, extra action groups, engineering dashboards, technical-detail links, provenance blocks, canonical-authority prose, or NOT AVAILABLE matrices on the three production screens.

Dynamic values may change. The visible structure may not.

## Canonical visual masters

### PIXEL ART

`docs/product/visual-masters/FACTORY_STUDIO_PIXEL_ART_MASTER_V03.webp`

### LEVEL FACTORY

`docs/product/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.svg`

### RELEASE POOL

`docs/product/visual-masters/FACTORY_STUDIO_RELEASE_POOL_MASTER_V01.svg`

These three files are the visual specification.

The application must match them as closely as the Godot runtime and platform font rasterization permit.

## Exact top navigation

Visible module labels are exactly:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

No leading numeral before PIXEL ART.

No HOME.

No CREATE.

No BATCH.

No SOLVE.

No REVIEW.

No LIBRARY.

No PUBLISH.

No fourth production tab.

A Settings gear is allowed only because it is present in the masters. It opens secondary settings and does not become a production page.

## Master-wins rule

For visible layout, the master image wins over older prose specifications.

For backend truth/safety, existing canonical pipeline, solver, review, publisher and production-approval authorities remain binding.

If an old UI document, old prompt, screenshot, placeholder or legacy workspace conflicts with these three masters, it is superseded for owner-facing layout.

## No-explanation rule

The three main screens show only:

- labels visible in the corresponding master;
- dynamic values/statuses occupying those master positions;
- artwork/level thumbnails and previews;
- master-defined actions.

Do not add help paragraphs.

Do not add workflow explanations.

Do not add "canonical", "authority", "lineage", "provenance", "derived evidence", "immutable", "technical details", "not available until..." or similar engineering prose.

If a real action is blocked:

- keep the master layout;
- disable the relevant existing master control when appropriate;
- show at most a short transient error/toast/modal after owner interaction;
- never add a persistent explanatory panel to the main screen.

## No-extra rule

Do not add any visible element to a production screen unless:

1. it exists in that screen's visual master; or
2. it replaces a master placeholder with the real dynamic data that placeholder represents.

No extra buttons.

No extra cards.

No extra sidebars.

No extra tabs.

No extra footers.

No extra legends.

No extra debug labels.

No DEBUG title.

## PIXEL ART screen

Must follow the PIXEL ART master.

The screen owns single and CSV/batch artwork generation.

The large central Visual Review Canvas is mandatory.

Batch thumbnails/selectable results stay in the master-defined area.

Normal owner work is performed without navigating to a technical page.

## LEVEL FACTORY screen

Must follow the LEVEL FACTORY master.

The central owl-style Visual Review Canvas placement is the visual authority.

The screen owns:

- artwork selection;
- level number;
- supply columns 3/4/5;
- pipeline execution;
- solver/replay;
- Difficulty V1;
- supply plan;
- Accept/Reject;
- level variations/batch work;
- handoff of READY accepted levels to Release Pool.

The backend remains canonical; the screen does not invent solver/difficulty/readiness truth.

## RELEASE POOL screen

Must follow the RELEASE POOL master.

The screen contains:

- READY level pool/list;
- filters/search exactly in the master structure;
- central Visual Review Canvas;
- selected-for-release strip;
- selected level details;
- release target/state controls;
- master-defined preflight/upload controls;
- release manifest preview action.

Only accepted/READY levels appear as releasable content.

Real publication remains fail-closed through existing pack/STAGING/production/R2 authorities.

The UI must not expose additional backend release pages.

## Scaling

Reference capture size is 1536 × 1024.

At other window sizes:

- preserve the same topology;
- preserve relative panel proportions;
- preserve action placement;
- preserve dominant central Visual Review Canvas;
- scale/reflow only as necessary to remain usable.

Do not transform the screen into another information architecture.

## Dynamic-content rule

The following may change without violating visual identity:

- filenames;
- level names/numbers;
- counts;
- thumbnails;
- selected items;
- solver state;
- difficulty score/class;
- supply counts;
- READY/failure state;
- release selection;
- environment state;
- upload/preflight status.

Their positions and component types remain the same as the master.

## Canonical backend preservation

The visual lock does not weaken:

- transparent VOID contract;
- current-game loaders/validators;
- supply conservation;
- official solver/replay;
- Difficulty V1;
- owner Accept/Reject;
- Release Pool readiness;
- STAGING vs production separation;
- exact production approval;
- R2 secret handling;
- declarative-only remote payload.

## Supersession

This V03 document supersedes all prior owner-facing Factory Studio layout contracts.

Historical prompts, logs and audits remain immutable evidence but are not current UI authority.

Current UI authority is this document plus the three visual masters listed above.
