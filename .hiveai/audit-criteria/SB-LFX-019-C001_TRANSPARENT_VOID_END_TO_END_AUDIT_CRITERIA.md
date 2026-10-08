# SB-LFX-019-C001 — Transparent Artwork -> VOID End-to-End — Audit Criteria

## Gate

Do not implement unless exact current `Sekiph82/Scrubbots:main` positively exposes the owner-approved VOID LevelData contract.

Current pre-gate behavior must remain fail-closed.

## A. Game capability authority

PASS only if builder records:

- exact current game commit;
- canonical remote/main authority;
- authoritative VOID ADR/spec;
- exact LevelData version/VOID encoding;
- owner decisions inherited for presentation and minimum artwork.

No copied/stale local assumption.

## B. Import and QA

Require:

- alpha values only 0 or 255;
- semi-alpha rejection;
- alpha 0 -> VOID;
- non-VOID colors only count toward 3..12 color rule;
- game ADR minimum-artwork rule applied to non-VOID artwork;
- no transparent->colour fill fallback.

## C. Solver/supply parity

Require:

- VOID excluded from color totals and supply conservation;
- screening treats VOID according to official game initial/open semantics;
- solver bridge constructs official game-supported VOID LevelData;
- no fake colour 0 + manually forced cleared workaround;
- official game solver/replay proves SOLVED/WIN;
- official Difficulty V1 analyzes VOID levels;
- supply columns 3/4/5 supported under normal production rules.

## D. Export/identity/publish

Require:

- official new LevelData version and `-1` VOID cells;
- SupplyPlanLoader and LevelLoader pass in exact current game authority;
- hashes/identity bind VOID layout;
- metadata records `artworkCellCount` and `voidCellCount`;
- TRANSPARENT intent publishable only while capability gate is open;
- campaign/release uses official score without special-cased difficulty fiction.

## E. Preview

Factory Studio preview must render VOID exactly according to the game ADR/current gameplay presentation.

No LF-specific competing visual semantics.

## F. Required fixtures

Permanent tests:

- ring;
- enclosed hole;
- border-touching VOID;
- VOID-only row/column where game contract permits;
- legal corridor/reachability case from game fixtures;
- capability gate closed;
- semi-alpha rejection;
- minimum-artwork boundary;
- color count ignoring VOID;
- full-canvas opaque regression;
- owner-real 32x32 sprite with approximately 550 transparent pixels at supply columns 3, 4 and 5.

Every accepted transparent fixture must export, load in the game, replay WIN and produce official Difficulty V1 evidence.

## G. Full-canvas compatibility

Opaque legacy input must preserve previous output/hashes/behavior wherever the game format remains V1-compatible.

VOID support must not silently upgrade or mutate legacy opaque content without contract need.

## H. Regression

Require focused tests, current-game parity tests, safe full LF suite, compile/schema/diff/secret checks.

No builder edit to root `TASKS.md` or `.hiveai/audits/**`.
