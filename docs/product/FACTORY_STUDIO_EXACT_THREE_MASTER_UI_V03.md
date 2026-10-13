# Factory Studio Exact Three-Master UI V03

Status: VISUAL AUTHORITY RETAINED / FUNCTIONAL WORKFLOW SUPERSEDED BY `docs/product/FACTORY_STUDIO_OWNER_WORKFLOW_V04.md`
Date: 2026-10-08
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Functional control authority

Every interactive control is governed by `docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`. The masters define appearance; that binding contract defines runtime behavior. A visually correct but non-functional control is non-compliant.

## Final owner decision

The Factory Studio owner UI has exactly three production screens and must visually match the three approved repository masters.

There is no alternative layout interpretation.

There are no additional owner production pages.

There are no explanatory paragraphs on the three production screens.

There are no extra panels, extra navigation entries, extra action groups, engineering dashboards, technical-detail links, provenance blocks, canonical-authority prose, or NOT AVAILABLE matrices on the three production screens.

Dynamic values may change. The visible structure may not.

## Canonical visual masters

### PIXEL ART

`docs/product/visual-masters/FACTORY_STUDIO_PIXEL_ART_MASTER_V04.png`

### LEVEL FACTORY

`docs/product/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.svg`

Godot uses the 1536 × 1024 PNG at `level_factory/assets/visual-masters/FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.png`, rasterized from the unchanged canonical SVG with CairoSVG 2.9.0 so its text labels render in the runtime. SHA-256: `310da9787a1d67ae47ce7c052f4938a9da6c6c4ac118052a3a431d86c7d96a25`.

### RELEASE POOL

`docs/product/visual-masters/FACTORY_STUDIO_RELEASE_POOL_MASTER_V01.svg`

Godot uses the 1536 × 1024 PNG at `level_factory/assets/visual-masters/FACTORY_STUDIO_RELEASE_POOL_MASTER_V01.png`, rasterized from the unchanged canonical SVG with CairoSVG 2.9.0 so its text labels render in the runtime. SHA-256: `2bb86b7816201e17d7a8f217902632cd10c6085c206aa000522b3ec4e449ce1f`.

These three files are the visual specification.

The application must match them as closely as the Godot runtime and platform font rasterization permit.

## Owner-approved R09-R02 in-workflow exception

The latest direct owner ruling (R09-R02-R01) SUPERSEDES earlier R09-R02 provisional geometry and moves existing LEVEL FACTORY controls WITHIN the same left workspace, in THIS EXACT VERTICAL ORDER: (1) Select PNG and settings SIDE-BY-SIDE at TOP, (2) Run Pipeline directly underneath BOTH, (3) large PIPELINE ACTIVITY BELOW Run, filling the remaining left-panel height. 1536×1024 reference: left workspace Rect2(18,116,354,814); Select PNG Rect2(42,165,95,100) unchanged; LevelNumber Rect2(172,165,190,38); supply columns 3/4/5 x172/238/304 y209 w56 h38; MaxRobotsAuto Rect2(172,253,190,38); BackgroundIntent Rect2(172,297,190,38); move the LevelNumber dynamic label to same top-right control; RunLevelPipeline Rect2(26,347,335,52); Pipeline Activity panel Rect2(27,412,334,498), with bounded scroll list. Modest padding-only adjustments may be made for no-overlap/responsive scale, never reorder the three blocks.

The earlier activity at Rect2(27,540,334,250), Run Pipeline at Rect2(26,803,335,52), and Level/Columns/Max/Background controls at y346..525 are historical/REJECTED and are NOT the current visual authority. The updated activity panel is only visible on LEVEL FACTORY and truthfully displays source, elapsed, timestamped hash-verified backend stage events and errors without invented percentages. No fourth screen, no change to central image, right details, bottom variation carousel or other two tabs. Owner explicitly requested that actual Desktop .lnk or .exe opens the updated installed Studio; Codex must verify real target, safely deploy required code and refresh actual link/binary only where necessary. This written update does NOT claim the user's installed UI is already updated.

The panel uses a compact PIPELINE ACTIVITY title/state chip, one selected filename + elapsed row, one current phase/reason row and a vertically scrollable chronological event list. Each event is timestamped from the backend's elapsed time, bounded to one or two concise lines, and retained up to 200 visible rows. Scroll follows new rows only when already at the bottom. The monitor never fabricates a percentage, native visit count, replay or QA result; while the backend is active without solver progress, it says it is waiting for the next backend event.

Activity receipts are append-only, SHA-256 chained, bounded to 256 KiB per run, and written only under the installed Release `level_factory/output/studio-pipeline-activity` directory. The reader retains a per-run byte offset, holds partial newline/UTF-8 tails until complete, and verifies run ID, source ID/SHA, sequence, prior hash, body digest and exact terminal backend disposition. Truncated, malformed or mismatched streams fail closed. The actual backend disposition and primary stop reason remain visible; a transport warning is secondary and cannot convert a blocked/unavailable result to READY. The run button stays disabled only while its worker is active and is restored on a structured or transport error.

On opening the existing screen, the UI calls the read-only canonical `library-refresh` and verifies each immutable PNG SHA before restoring the source-only thumbnail queue. Existing batch order is retained where batch records identify it; remaining verified sources follow the canonical library order. A source-only import is never relabeled READY by this presentation restore and no solver is started by screen navigation or restoration.

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

## Direct owner responsive override — 2026-10-13

The owner-approved decision `docs/decisions/OWNER_FACTORY_STUDIO_LEVEL_FACTORY_COMPACT_BATCH_20261013_V01.md` supersedes only the Level Factory screen's old fixed 1536×1024 letterboxed placement and the right-side Details / Replay / Supply layout. Level Factory must use the actual full client rectangle with adaptive left, Visual Review, and right regions; the thumbnail strip docks to the bottom. Details use at most five compact paired rows, followed by the existing two Replay/Supply actions, the existing three review/run actions, and one clipped, scrollable inline Results panel. Replay and Supply do not open modal windows.

The three production screen identities, navigation order, source/gallery interactions, artwork behavior, and PIXEL ART / RELEASE POOL compositions remain governed by their corresponding masters. The responsive override changes layout geometry and Level Factory results placement only; it does not introduce a fourth screen or alter backend evidence.

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
- READY auto-pool include/exclude controls;
- Release Pool readiness;
- STAGING vs production separation;
- exact production approval;
- R2 secret handling;
- declarative-only remote payload.

## Supersession

This V03 document supersedes all prior owner-facing Factory Studio layout contracts.

Historical prompts, logs and audits remain immutable evidence but are not current UI authority.

Current UI authority is this document plus the three visual masters listed above.
