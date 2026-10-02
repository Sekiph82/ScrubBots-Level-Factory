# MAINT-ZIP-CORE-V02-C001-R01 — Product Shell Closure — Strict Audit

Date: 2026-10-02
Auditor: ChatGPT
Verdict: **CHANGES_REQUIRED**

Repository:
`Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/MAINT-ZIP-CORE-V02-C001-R01_PRODUCT_SHELL_CLOSURE_CODEX_LOG.md`

Primary product commit:
`97e28109d967987a0a62fbdbc6d9d70697e0f0e2`

Final builder publication:
`51b398c32ac43cf025af185f8eab2202a585a520`

Current main after builder publication differs only by the final log-equality commit; no later product-code mutation was found.

Parent audit:
`.hiveai/audits/MAINT-ZIP-CORE-V02-C001-LF_ONLY_STRICT_AUDIT.md`

## Executive result

R01 closed most of the previous product-shell blockers.

### Independently verified as closed

- Current CLI `generate` / `batch` no longer expose `--difficulty`.
- Factory Studio no longer shows a requested-difficulty selector.
- Gateway no longer injects `--difficulty EASY`.
- BACKGROUND / TRANSPARENT intent exists on the current Studio/CLI request surface.
- Procedural TRANSPARENT requests fail truthfully rather than silently filling a background when the current generator cannot produce alpha.
- Solve and Analyze are no longer permanently hard-coded UNAVAILABLE; availability is gated on Python Core + ZIP/game/Godot capability and a generated candidate.
- Exact opaque OWNER_UPLOAD artwork can derive a canonical candidate while preserving immutable source lineage.
- Derived OWNER_UPLOAD candidates are discoverable by `list_candidates()`, therefore can participate in the normal owner-review chain.
- Canonical candidate/artwork routes execute shipping `verify_exported_supply` and require a READY load-check before publication eligibility.
- Owner ACCEPT invokes an actual configured-game publisher; owner REJECT performs no publication.
- Publisher requires READY ZIP evidence + READY load-check and writes level, supply, metadata, preview, and production catalog paths.
- Live 3/4/5-column solve/replay/Difficulty V1/export/load-check was revalidated against the current read-only game authority.
- Full builder regression is green: `1132 passed, 3 skipped`; compileall and Factory Studio headless runtime suite PASS.
- ZIP tuning was not retuned by this product commit.

The remaining failures are narrow but production-significant.

## F01 — Current GenerationRequest still exposes requested difficulty through the same public class

Owner/R01 contract required:
- the CURRENT production artwork request has no requested-difficulty field;
- historical difficulty-bearing artifacts remain only through a clearly isolated legacy compatibility path.

Current implementation still defines:

`GenerationRequest.difficulty: Difficulty | str | None = None`

and the same class:
- accepts `difficulty="EASY|MEDIUM|HARD|VERY_HARD"`;
- switches to legacy behavior based on whether difficulty is None;
- serializes difficulty when supplied.

This means the public current request type still accepts requested difficulty. The legacy behavior is not isolated behind a distinct adapter/type.

CLI and Studio are difficulty-free, which is good, but Python/API production callers can still construct a difficulty-bearing `GenerationRequest`.

**Disposition: BLOCKER.**

### Required correction

- Current `GenerationRequest` must have no `difficulty` constructor field.
- Current canonical schema is difficulty-free only.
- Historical v1/v2 metadata reproduction must go through an explicit private/legacy compatibility adapter/type.
- Legacy compatibility must never be accepted by new current Generate/Batch requests.

## F02 — Current width/height are still optional and auto-selected

R01 explicitly required new production generation to use explicit width and height so requested difficulty is not replaced by another hidden size selector.

Current:
- CLI `--width` and `--height` are optional;
- current `GenerationRequest` accepts width/height None;
- current request can call seed-based `resolve_current_dimensions(..., seed=...)`;
- builder evidence explicitly added auto-dimension support.

This is outside the approved R01 contract.

**Disposition: BLOCKER.**

### Required correction

For NEW production Generate/Batch:
- width required;
- height required;
- both validated against current production envelope;
- no automatic current dimension selection.

Historical metadata reproduction may preserve its recorded old behavior.

## F03 — Retired M03/M04 solver/difficulty architecture remains publicly exported

The files remain, and more importantly the package root `scrubbots_pixel_factory/__init__.py` still publicly imports/exports the legacy solver/difficulty stack, including:
- `simulation_boundary`;
- `compact_solver_state`;
- `legal_move_provider`;
- `baseline_search`;
- `visited_memoization`;
- `solver_evidence`;
- `search_policy`;
- `solution_analysis`;
- `solver_budget`;
- `level_metrics`;
- `difficulty_analysis`;
- `canonical_bridge`.

This is not a completed decommission.

R01 allowed retaining historical/evidence modules only if they were explicitly non-production and unreachable as current solver/difficulty authority.

Current package root still presents them as first-class public APIs.

**Disposition: BLOCKER.**

### Required correction

Do not delete historical functionality that other retained evidence/research modules still need.

Instead:
- remove retired solver/difficulty authorities from the current package-root production API;
- mark retained files explicitly `LEGACY_NON_PRODUCTION` / evidence-only;
- update current product code so Studio/CLI/supply pipeline cannot import them as authority;
- add a static dependency guard proving the canonical production path imports only the ZIP supply/solve/difficulty backend;
- direct legacy tests/tools to explicit module imports or a clearly named legacy namespace.

ZIP remains the single production brain.

## F04 — Publisher does not run current game LevelCatalog validation on the proposed publication

R01 required validation of the proposed catalog using the current game catalog authority before publication commit.

Current `game_publisher.py`:
- parses the production catalog;
- checks identity collisions;
- calculates progression placement;
- stages files;
- atomically replaces files/catalog.

But it does not execute the current game:
- `LevelCatalog.load_manifest(...)`;
- `DifficultyV1CatalogCheck.validate_catalog(...)`;
against the proposed staged entry before committing production paths.

This matters because current game catalog validation enforces additional shipping rules beyond level/supply load-check, including current production-level validation and current shell constraints.

**Disposition: BLOCKER.**

### Required correction

Before production mutation:
- stage the exact candidate level/supply/metadata/preview and a proposed manifest in an isolated validation area;
- execute current Scrubbots LevelCatalog + DifficultyV1CatalogCheck against that proposed content using the current read-only game authority;
- require PASS;
- clean temporary validation material;
- only then commit the production transaction.

Builder tests must still use only temporary game fixtures.

## F05 — Difficulty-based publication can create catalog-order gaps that stop gameplay progression

This is a concrete current-game incompatibility.

Current production catalog ends with a contiguous max order.

Current publisher:
- sets `first_order = max(existing order) + 1`;
- then scans many later cadence positions;
- may choose, for example, order 13 because the official Difficulty V1 score fits slot 13 better than slot 11;
- appends that order directly to the production catalog.

Current game `GameplayLaunchResolver` resolves:
`AppState.progression.current_level()`
by finding a catalog entry whose explicit `order` equals that exact frontier number.

If the frontier becomes 11 but the next published entry is order 13, the game returns:
`CONTENT_MISSING`.

Therefore the current difficulty placement can publish a catalog that validates structurally yet stalls campaign progression.

**Disposition: BLOCKER.**

### Safe owner-consistent closure rule

Do not invent a new cadence and do not renumber existing immutable content.

For shipping publication:
1. compute the next contiguous catalog order: `max(existing order) + 1`;
2. evaluate that exact slot using current DifficultyProgressionV1 authority;
3. publish only if the new level's official Difficulty V1 score/class is compatible with that exact next slot under the current owner tolerance;
4. if it does not fit, return a fail-closed `PROGRESSION_SLOT_MISMATCH` / waiting-for-compatible-slot result and perform zero game writes;
5. optionally report future compatible slot suggestions as advisory only, never publish them while preceding orders are absent.

This preserves:
- difficulty-based placement;
- current owner cadence;
- contiguous game frontier;
- immutable IDs;
- no save-number renaming.

Owner ACCEPT remains the automatic publication trigger when all shipping gates, including the next contiguous difficulty slot, are satisfied.

## Retained PASS findings

The following must not be rewritten in R02:

- ZIP candidates = 300.
- original + maximum three mutations.
- screening budget = 3000.
- viability budget = 3000.
- game-default real-solver budget.
- SupplyScorer weights unchanged.
- mean-batch-size seed ranges unchanged.
- internal automatic ZIP complexity/search band unchanged.
- ScreeningSimulator ranking-only.
- real game solve/replay + ZIP SolutionVerifier acceptance.
- no ProductionGameplayHost acceptance gate.
- 3/4/5 supply columns.
- preview depth = 3.
- baseline five-slot generation.
- no global robots-per-batch cap.
- owner-upload immutable source lineage.
- load-check publication gate.
- dynamic Solve/Analyze capability.
- configured-game publisher architecture.
- full green regression baseline from R01.

## Final verdict

`MAINT-ZIP-CORE-V02-C001-R01 = CHANGES_REQUIRED`

R02 is a narrow closure:
1. isolate legacy difficulty request support from the current request type;
2. require explicit current width + height;
3. remove legacy solver/difficulty authority from the current public production API;
4. run real game catalog validation before publication;
5. prevent progression-order gaps.

No ZIP algorithm retuning is authorized.
