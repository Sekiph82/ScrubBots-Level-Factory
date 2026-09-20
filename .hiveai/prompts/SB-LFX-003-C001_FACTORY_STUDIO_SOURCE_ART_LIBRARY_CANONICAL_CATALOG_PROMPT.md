# SB-LFX-003-C001 — Factory Studio Source Art Library Canonical Catalog

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LFX-003 — Build searchable Source Art Library/index with immutable source identity, provenance, tags, review state and usage references. [EXTENSION]`

Create the builder log BEFORE any product/test edit:

`.hiveai/codex-logs/SB-LFX-003-C001_SOURCE_ART_LIBRARY_CANONICAL_CATALOG_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read fully before edits:
- root `TASKS.md`;
- SB-LFX-002 closing strict audit;
- `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`;
- `.hiveai/audit-criteria/SB-LFX-003-C001_SOURCE_ART_LIBRARY_CANONICAL_CATALOG_AUDIT_CRITERIA.md`;
- accepted OWNER_UPLOAD source contract;
- current Import/Dashboard/navigation/workspace/Gateway code;
- clean-checkout/project-boundary tests.

## 1. Source truth stays canonical

Build Library C001 over real retained OWNER_UPLOAD sources only.

Do not invent persisted provider/procedural source records.

Every refresh must verify source.json + source.png binding before presenting a source as valid.

Refactor/reuse a narrow public canonical Python read/verify function from the accepted owner-upload contract if needed. Do not reimplement source verification permissively in GDScript.

## 2. Derived Library view, not a second source database

Do not create a master index containing copied source truth that becomes authoritative.

Build the source list fresh from verified canonical source directories.

It is acceptable to persist only operator catalog metadata for:
- label;
- tags.

Keep that metadata in a separately governed versioned sidecar area such as:

`level_factory/output/source-library/metadata/<source_id>.json`

The sidecar must bind source_id and contain no source-authority, QA, solver, difficulty, review-acceptance or production truth.

## 3. Label/tag metadata

Implement bounded catalog metadata:
- optional human label;
- deterministic tags;
- trimmed/bounded strings;
- unique tags;
- stable canonical JSON;
- source-ID binding.

Editing label/tags must never modify source.png or source.json.

Corrupt catalog metadata must fail closed for that metadata rather than rewriting source truth.

## 4. Truthful unavailable domains

For C001 expose:
- owner review state;
- derived logical dimensions;
- palette facts;
- candidate/level usage references.

If no canonical source exists for those domains, show explicit NOT AVAILABLE with reason.

Do not infer:
- owner review;
- zero usage;
- C01..C16 validity;
- candidate acceptance;
- production readiness.

## 5. Make Library surface real

Replace only the current Library placeholder.

Provide:
- Refresh;
- basic search;
- deterministic source list;
- selected source detail;
- source ID/origin/hash/original filename/dimensions/state;
- label/tags;
- unavailable review/palette/derived-dimension/usages;
- immutable source path;
- edit/save label/tags.

Display clearly:

`ASSET CATALOG ONLY — source art is not training data and Library membership is not owner acceptance.`

Do not add candidate/review/QA/promotion controls.

## 6. Basic search only

Search across:
- source ID;
- original filename;
- label;
- tags;
- origin.

Keep search read-only and deterministic.

Do not implement LFX-009 smart collections or saved advanced filters.

## 7. Corruption behavior

A bad source record or mismatched source bytes must never render as valid Library content.

Either fail refresh closed or explicitly quarantine/exclude the bad source with truthful error evidence.

Never silently repair source truth.

## 8. Real integration required

Add focused tests plus one real Godot Library integration that:
- creates/imports two OWNER_UPLOAD fixtures;
- opens real Library;
- refreshes canonical sources;
- verifies source truth against bytes/records;
- saves label/tags on one source;
- proves source.png/source.json unchanged;
- refreshes and proves metadata persistence;
- searches by ID, filename, label and tag;
- proves review/palette/derived dimensions/usages are NOT AVAILABLE;
- corrupts a bounded source/record and proves it is not trusted;
- proves no candidate/QA/acceptance/promotion action;
- cleans bounded source/catalog metadata artifacts.

## 9. Preserve accepted work

Keep SB-LFX-001/002 and LF06-001..012 green.

Do not refactor existing Dashboard/Import/Generate/editor/revalidation/reproduce for style.

## 10. Forbidden scope

Do not start:
- SB-LFX-004+;
- Import Validation Wizard;
- Candidate Inbox/Review;
- owner acceptance;
- smart collections;
- readiness card;
- batch import;
- revision history;
- provider work;
- M03/M04/M05;
- Content Platform;
- main game.

Do not modify `TASKS.md`.

## Verification

Run and record:
- focused LFX-003 tests;
- real Godot Library integration;
- retained LFX-002 import tests;
- retained LFX-001 Dashboard tests;
- relevant LF06 tests;
- full pytest;
- compileall;
- Godot headless boot;
- diff check;
- TASKS diff empty;
- exact changed-file review.

Publication:
1. implementation/tests/docs commit(s);
2. push/equality checkpoint;
3. exactly one terminal builder-log-only publication commit;
4. stop.

At completion give only:
1. full GitHub URL of `.hiveai/codex-logs/SB-LFX-003-C001_SOURCE_ART_LIBRARY_CANONICAL_CATALOG_CODEX_LOG.md`;
2. final implementation commit SHA;
3. terminal log-only publication commit SHA.
