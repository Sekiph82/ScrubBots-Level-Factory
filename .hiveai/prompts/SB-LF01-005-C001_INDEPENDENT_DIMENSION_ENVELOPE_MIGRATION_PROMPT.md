# SB-LF01-005-C001 — Independent Dimension Envelope Migration
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Implement only:

`SB-LF01-005 — Support width/height selection within current engine/content envelope and workload guidance. [MIGRATION]`

This task is opened as a dependency before `SB-LF06-002` because the canonical Python Factory Core currently ties legal/automatic board dimensions to difficulty bands, while the owner-locked production contract says:

- width is `20..59` inclusive;
- height is `20..59` inclusive;
- width and height are independently validated;
- rectangles are legal;
- difficulty is not derived from board size;
- board size is not a difficulty rule.

Factory Studio must consume canonical Core truth, so the Studio controls must not be built on top of the stale difficulty-band dimension contract.

Do not begin `SB-LF06-002`, any `SB-LFX-*` task, solver, Dashboard, Import, provider, Content Platform, or main-game work in this cycle.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this prompt;
3. previous strict PASS audit:
   `.hiveai/audits/SB-LF06-001-C001-R01_FACTORY_STUDIO_RUNTIME_NODE_CONTRACT_REMEDIATION_STRICT_AUDIT.md`;
4. `src/scrubbots_pixel_factory/core/request.py`;
5. `src/scrubbots_pixel_factory/contracts/difficulty.py`;
6. `src/scrubbots_pixel_factory/contracts/production.py`;
7. `src/scrubbots_pixel_factory/contracts/__init__.py`;
8. all generator/router code that consumes resolved width/height;
9. CLI generate/reproduce/batch paths and metadata/request deserialization paths;
10. output/provenance code that records generation requests or resolved dimensions;
11. all tests referencing difficulty bands, dimension selection, explicit dimensions, request serialization, reproduction, batch resume, or historical metadata;
12. relevant retained PAG-M01/M02/M08/M09 audits/evidence inside this repository.

Before any implementation edit create and verify:

`.hiveai/codex-logs/SB-LF01-005-C001_INDEPENDENT_DIMENSION_ENVELOPE_MIGRATION_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## 1. Canonical target dimension contract

The post-migration production contract must have one canonical dimension envelope:

- minimum width = 20;
- maximum width = 59;
- minimum height = 20;
- maximum height = 59;
- each axis validated independently;
- all legal rectangles inside that envelope are allowed;
- difficulty value must not make an otherwise legal dimension illegal;
- used-color count must not determine board dimensions;
- no square-only assumption.

Examples that MUST be legal after migration for every production difficulty label:

- `20x20`;
- `20x59`;
- `59x20`;
- `59x59`;
- representative interior rectangles such as `23x47` and `52x31`.

Values below 20 or above 59 must remain invalid.

Do not encode the envelope independently in multiple production modules. Establish one canonical source of dimension-envelope truth and have request/generation paths consume it.

## 2. Remove difficulty-band dimension semantics

Current `contracts/difficulty.py` contains `DIFFICULTY_BANDS` where EASY/MEDIUM/HARD/VERY_HARD select separate board-size bands. That is obsolete production semantics.

Migrate production behavior so:

- difficulty remains a valid independent semantic/classification input where used elsewhere;
- dimension validation does not inspect difficulty to decide whether width/height are legal;
- automatic selection of omitted width/height does not use difficulty to choose a size band;
- the same dimension-selection seed/domain inputs must not silently produce different ranges merely because difficulty changed;
- no replacement difficulty-to-size mapping is introduced under another name.

Keep deterministic selection. Width and height must use separate deterministic domains so rectangles remain naturally possible.

## 3. GenerationRequest and canonical serialization

`GenerationRequest` must reflect the migrated contract.

Required behavior:

- explicit width/height are validated against the global 20..59 envelope independently of difficulty;
- if one or both axes are omitted, deterministic resolution uses the global envelope;
- difficulty remains serialized independently;
- width and height request fields retain their explicit/omitted meaning;
- canonical serialization remains stable and deterministic for a given schema/version;
- no UI-only rule is introduced as a substitute for Core validation.

## 4. Historical reproducibility and semantic versioning gate

This migration changes a historically serialized semantic when width or height can be omitted. Do **not** silently change the meaning of an already-versioned serialized request if that would make accepted historical artifacts unreproducible.

Before choosing implementation strategy, inventory and record in the builder log:

- request schema/version behavior;
- how historical metadata reconstructs requests;
- whether accepted bundles persist explicit resolved dimensions or omitted axes;
- reproduce/resume behavior for historical artifacts;
- generator-version/provenance fields that may already protect replay.

Then implement one auditable strategy:

A. preserve legacy request semantics only for explicitly identifiable historical schema/version data while making the new/current production schema use independent 20..59 dimensions; or

B. if repository evidence proves historical accepted reproduction is unaffected because resolved dimensions are persisted and replay does not re-resolve the stale band, document and test that proof before changing semantics in place.

Do not perform an unversioned semantic mutation that causes old persisted accepted artifacts to regenerate differently without detection.

If a schema/version bump is required, implement backward-compatible parsing/reproduction for supported historical data and add corruption/unsupported-version tests. Do not invent a migration shortcut just to avoid test updates.

## 5. Workload guidance

`SB-LF01-005` includes workload guidance, but workload guidance must remain separate from legality and difficulty.

It is acceptable to expose/document non-binding cost guidance such as larger boards requiring more compute, provided:

- it never makes a legal 20..59 dimension illegal;
- it is not called difficulty;
- it does not map difficulty labels to sizes;
- 59x59 remains an explicitly tested supported production boundary.

Do not invent performance numbers that were not measured.

## 6. Downstream migration

Inspect and update all in-repository callers/tests that rely on the obsolete band semantics.

Pay special attention to:

- generators that ask for resolved dimensions;
- AUTO/HYBRID routing if dimensions affect routing;
- deterministic provenance/digest behavior;
- accepted bundle metadata;
- reproduce;
- batch/resume;
- quality tests whose fixtures assume EASY=20..29 etc;
- docs/help text.

Do not change unrelated generation quality, palette, provider, solver, or gameplay rules.

## 7. Required focused tests

Add/adjust tests proving at minimum:

1. global width envelope is exactly 20..59;
2. global height envelope is exactly 20..59;
3. width and height validate independently;
4. rectangles are legal;
5. each production difficulty accepts `20x20`, `20x59`, `59x20`, `59x59`, and representative interior rectangles;
6. 19 and 60 are rejected on either axis;
7. automatic width/height selection remains deterministic;
8. width and height use separate stable selection domains;
9. automatic dimension resolution is not difficulty-banded;
10. `GenerationRequest` canonical serialization/digest remain deterministic for the applicable schema/version;
11. historical reproduction/version behavior is explicitly covered according to the chosen migration strategy;
12. 59x59 generation/relevant cost-scaled path remains exercised;
13. no difficulty or used-color rule is derived from dimensions;
14. existing rectangular-board evidence remains green.

Tests must verify behavior, not merely grep constants.

## 8. Required regression and verification

Run and record at minimum:

1. new focused SB-LF01-005 tests;
2. existing request/core/difficulty/dimension tests;
3. generator/router tests affected by resolved dimensions;
4. reproduce and batch/resume tests affected by request semantics;
5. prior LF01 deterministic/provenance/rectangle/59x59 suites;
6. full `python -m pytest -q`;
7. `python -m compileall -q src tests`;
8. package import smoke;
9. module CLI help and installed CLI help if available;
10. representative CLI generation with explicit rectangular dimensions;
11. representative deterministic omitted-axis resolution/reproduction according to the migrated version contract;
12. `git diff --check`;
13. changed-file inspection proving no root `TASKS.md`, Studio feature, provider, Content Platform, or main-game scope creep.

Record failed commands and corrections truthfully.

## Allowed scope

Allowed only where required to migrate the dimension contract:

- `src/scrubbots_pixel_factory/contracts/**`;
- `src/scrubbots_pixel_factory/core/**`;
- generator/router code directly affected by dimension resolution;
- CLI/reproduction/output/provenance code directly affected by request schema/version compatibility;
- tests/fixtures/docs directly affected by the migration;
- matching builder log.

Do not modify `level_factory/` Studio product functionality in this cycle unless a documentation cross-reference must be corrected. Do not edit root `TASKS.md`.

## Forbidden scope

Do not implement:

- `SB-LF06-002` controls;
- any Dashboard/Import/Library/LFX behavior;
- gameplay solver semantics;
- provider/API/network integration;
- Content Platform work;
- main-game code;
- new difficulty formulas;
- new color-count/difficulty coupling.

No self-audit or tracker state changes.

## Builder log requirements

H1 exactly:

`# SB-LF01-005-C001 — Independent Dimension Envelope Migration`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp/repo/branch/origin/status/worktrees;
- required reads;
- pre-edit dimension-contract inventory;
- exact historical reproduction/version analysis;
- selected migration/version strategy and why;
- changed symbols/callers;
- failed tests/commands and corrections;
- focused results;
- reproduction/batch compatibility results;
- 59x59 evidence;
- full regression/toolchain results;
- TASKS no-change proof;
- no Studio/provider/main-game/Content Platform scope creep;
- implementation commit/push;
- final log publication/equality evidence without false self-referential claims.

Keep timestamps monotonic and truthful. Never record secrets.

## Acceptance criteria

PASS eligibility requires all of the following:

- [ ] canonical production dimensions are independent 20..59 width and 20..59 height;
- [ ] rectangles remain legal;
- [ ] difficulty does not control dimension legality or selection bands;
- [ ] automatic dimension selection remains deterministic with separate axis domains;
- [ ] one canonical envelope source exists;
- [ ] GenerationRequest uses canonical migrated behavior;
- [ ] historical accepted reproduction/version semantics are preserved or explicitly version-migrated with tests;
- [ ] 59x59 remains supported and tested;
- [ ] workload guidance is advisory and separate from legality/difficulty;
- [ ] no unrelated generation/palette/solver/provider behavior changes;
- [ ] no Studio feature implementation;
- [ ] root `TASKS.md` unchanged by builder;
- [ ] focused and affected regression suites pass;
- [ ] full regression passes;
- [ ] compile/import/CLI checks pass;
- [ ] builder log finalized/pushed truthfully;
- [ ] builder stops for independent ChatGPT audit.

## GitHub handoff

Push implementation, tests, compatibility evidence, and finalized builder log to `main`.

At completion provide only:

1. full GitHub URL of the finalized builder log;
2. implementation commit SHA;
3. final publication/equality checkpoint SHA described truthfully.

Then stop for independent ChatGPT strict audit.
