# PAG-SP05-C001 V02 — LEVEL_ART Hard-Cell Compiler + Difficulty V1 Convergence
Document role: CODEX BUILDER PROMPT

Repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`

## Supersession

This prompt supersedes the earlier `PAG-SP05-C001_LEVEL_ART_HARD_CELL_COMPILER_PALETTE_SNAP_AND_DIFFICULTY_BUDGET_PROMPT.md` before implementation because the main SCRUBBOTS Difficulty V1 contract has now been made authoritative for the consolidated Content Platform.

Do not rewrite/delete the old prompt; keep it as historical evidence.

## Required reading

Read from GitHub before editing:

1. root `TASKS.md`;
2. `coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md`;
3. `docs/CONTENT_PLATFORM_ARCHITECTURE_V01.md`;
4. `docs/CROSS_REPO_CONTRACT_V01.md`;
5. `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V01.md`;
6. `docs/LEVEL_ART_DIFFICULTY_V1_CONVERGENCE_DECISION_V01.md`;
7. current semantic raw-artifact/normalization code and tests;
8. `contracts/palette.py`, `contracts/color_usage.py`, `contracts/difficulty.py` as legacy/current evidence, not permission to extend obsolete class-band truth;
9. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do not edit root `TASKS.md`.

## Mission

Implement a typed, deterministic canonical LEVEL_ART hard-cell compiler through this boundary:

```text
SemanticRawArtifact
 -> CELL_MAJORITY_V1
 -> PALETTE_SNAP_V1 to C01..C16
 -> current global used-color envelope validation/remediation
 -> immutable SemanticLevelArtArtifact + provenance
```

The compiler must not determine difficulty class from board dimensions or class-specific used-color bands.

Spend zero Magnific/PixelLab/provider credits. No provider call is needed.

Do not begin solver, Difficulty Score implementation, CampaignBuilder, `.scrubpack`, publisher or Studio refactor in this cycle.

## Required contract

### Dimensions

- target width/height are independent;
- rectangular boards supported;
- current production envelope is 20..59 per axis for production LEVEL_ART;
- no `difficulty -> dimension band` legality in the new compiler;
- smaller synthetic dimensions may be used only in isolated algorithm unit tests, never emitted as production LEVEL_ART.

### CELL_MAJORITY_V1

For source `SW x SH`, target `TW x TH`, require `SW >= TW` and `SH >= TH` in V1.

For target `(tx, ty)`:

- `x0=floor(tx*SW/TW)`
- `x1=floor((tx+1)*SW/TW)`
- `y0=floor(ty*SH/TH)`
- `y1=floor((ty+1)*SH/TH)`

Count exact decoded RGBA values within that half-open footprint.

Winner:

1. highest count;
2. tie -> lexicographic RGBA ascending.

Requirements:

- exact-size source maps 1:1;
- no averaging/interpolation/antialiasing;
- winning alpha must be 255 or fail closed;
- record deterministic pre-snap majority-grid digest.

### PALETTE_SNAP_V1

Snap every majority RGB to exactly one canonical C01..C16 using integer squared RGB distance:

`d2=(R-Rc)^2+(G-Gc)^2+(B-Bc)^2`

Tie -> lower canonical C-ID/index.

BG01 is excluded. Output logical cells are C-ID values only.

Record pre-envelope snapped-grid digest and used C-IDs.

### Current used-color envelope

Current general production envelope is 3..12 used canonical colors.

- if used count is 3..12: preserve snapped grid exactly;
- if used count <3: fail closed with explicit typed reason; do not inject arbitrary colors/cells;
- if used count >12: either fail closed or apply one explicit deterministic versioned semantic-preserving reduction policy; if reduction is implemented in this cycle it must be provenance-bound and exhaustively tested;
- never reduce/expand colors merely because requested class is EASY/MEDIUM/HARD/VERY_HARD;
- color count/distribution is a future Difficulty V1 metric input, not class identity.

Prefer fail-closed for >12 unless the existing code already provides a clearly reusable deterministic fidelity-preserving reduction that can be safely adapted without broadening this cycle.

### Typed request/result

Add an explicit LEVEL_ART request/result boundary, e.g. equivalent to:

- `SemanticLevelArtRequest`
- `SemanticLevelArtReport`
- `SemanticLevelArtArtifact`
- `compile_semantic_level_art()`

Exact names may follow repo conventions.

Request/result must bind:

- exact `SemanticRawArtifact` identity/hash/provenance;
- target width/height;
- CELL_MAJORITY policy/version;
- palette-snap policy/version;
- used-color-envelope policy/version;
- majority-grid digest;
- snapped/final logical-grid digest;
- actual used C-IDs;
- source decoded dimensions;
- deterministic artifact/request identity.

Result is deeply immutable and must fail closed on coordinated provenance tampering. Do not convert to final M08/LevelData bundle in this cycle.

## Legacy contract handling

Do not delete historical `Difficulty` enum/helpers or old tests merely to make new tests pass.

Instead:

- isolate the new compiler from obsolete class-band legality;
- add deprecation/current-authority documentation where needed;
- preserve historical compatibility helpers until a separate bounded migration can remove/replace them safely;
- do not create another duplicate difficulty/color-band table.

## Required focused tests

Prove at minimum:

1. exact-size source maps one pixel per logical cell before snap;
2. 4x4 -> 2x2 majority selection;
3. non-divisible rectangular footprint math deterministic;
4. majority tie-break deterministic;
5. source smaller than target fails closed;
6. non-opaque winning cell fails closed;
7. no area-average/intermediate colors in hard-cell stage;
8. every final cell is C01..C16;
9. BG01 cannot appear;
10. exact palette RGB maps to exact C-ID;
11. nearest snap uses integer squared RGB distance;
12. equal-distance palette tie -> lower C-ID;
13. production rectangular examples within 20..59 compile independent of class label;
14. a 24x24 request may carry any external target-class metadata without compiler class-band rejection;
15. a 38x38 request is not automatically HARD/MEDIUM/EASY by the compiler;
16. 3 used colors accepted;
17. 12 used colors accepted;
18. <3 used colors rejects without fabrication;
19. >12 behavior is deterministic and explicit according to chosen V1 policy;
20. same raw artifact + request -> identical deterministic result/digest;
21. raw byte/provenance change affects identity;
22. request/policy change affects identity;
23. direct construction/replace cannot mint mismatched trusted artifact;
24. accepted existing ASSET_ART normalization behavior remains unchanged;
25. no new code path calls a provider/network.

Use synthetic committed fixtures. Do not commit owner-private provider images.

## Regression

Run and log:

- focused SP05 V02 tests;
- semantic normalization regressions;
- PNG compatibility regressions;
- palette/color-usage/difficulty legacy contract tests;
- full pytest suite;
- compileall/import smoke;
- CLI smoke;
- `git diff --check`;
- secret/network scan over changed code/tests.

If old class-band tests fail because the new compiler intentionally does not use them, do not delete those tests. The new compiler should coexist with legacy compatibility contracts until a later migration.

## Allowed files

Authorized:

- semantic LEVEL_ART compiler/request/report/artifact implementation;
- exports/imports required for the new API;
- focused/regression tests;
- narrowly relevant semantic docs;
- matching builder log.

Do not edit:

- root `TASKS.md`;
- historical audit verdicts;
- main game repository;
- Studio/publisher code;
- unrelated generator families.

## Handoff

Commit/push authorized work to `main` without force.

Return only:

`AWAITING_AUDIT`

and the direct GitHub URL to the matching builder log.
