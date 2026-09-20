# SB-LFX-002-C001 — Manual Pixel Art OWNER_UPLOAD Immutable Source Import

Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on:

`SB-LFX-002 — Support manual Pixel Art import with explicit OWNER_UPLOAD provenance and immutable original bytes. [EXTENSION]`

This task implements SOURCE INGESTION ONLY.

Create the builder log BEFORE any product/test edit:

`.hiveai/codex-logs/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_CODEX_LOG.md`

Do not modify root `TASKS.md`.

## Required reads

Read fully before edits:
- root `TASKS.md`;
- SB-LFX-001 closing strict audit;
- `docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`;
- `.hiveai/audit-criteria/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_AUDIT_CRITERIA.md`;
- current Factory Studio Import placeholder/navigation/workspace/gateway;
- semantic normalization raw-artifact contracts;
- `SemanticRawArtifact.from_local_file()`;
- LEVEL_ART compiler and locked CELL_MAJORITY_V1 / PALETTE_SNAP_V1 policies;
- generated/output governance and clean-checkout tests.

## 1. Create an explicit OWNER_UPLOAD source contract

Do NOT relabel existing `LOCAL_FILE` provenance.

Add a narrow canonical Python owner-upload ingestion contract with explicit:

`origin = OWNER_UPLOAD`

Persist imported sources under governed Factory output, preferably content-addressed:

`level_factory/output/owner-uploads/<source_id>/`

Store:
- exact original bytes;
- canonical source record JSON.

Use deterministic content identity derived from SHA-256.

The source record must bind:
- schema/version;
- source_id;
- OWNER_UPLOAD;
- source SHA-256;
- byte length;
- supported media type;
- original filename as display metadata only;
- decoded original dimensions;
- relative immutable source path;
- SOURCE_ONLY / UNVALIDATED status.

## 2. Preserve owner bytes exactly

The imported stored image must be byte-for-byte identical to the selected file.

Do NOT:
- recompress;
- resize;
- crop;
- quantize;
- palette snap;
- alter alpha;
- compile LEVEL_ART.

Do not modify/delete the owner's external original.

## 3. C001 format boundary

Use the existing deterministic image boundary.

Supporting strict PNG only is correct if that is the current authoritative decoder.

Unsupported/corrupt formats fail closed.

No new imaging dependency unless absolutely required by an existing canonical contract.

## 4. Idempotence and collision safety

Same bytes twice:
- same source ID;
- verify existing record + bytes;
- return ALREADY_IMPORTED/SAME_SOURCE without destructive rewrite.

Same filename, different bytes:
- distinct source IDs;
- never overwrite.

Existing content-addressed destination with mismatched/corrupt record or bytes:
- ERROR;
- never silently repair/replace.

## 5. Make the Import Studio surface real

Replace only the current Import placeholder with the bounded owner-upload UI.

Provide:
- FileDialog or equivalent explicit local-file selector;
- Import button;
- a test/programmatic source-path setter;
- status;
- source ID;
- OWNER_UPLOAD origin;
- SHA;
- original filename/dimensions;
- immutable stored path.

Display prominently:

`SOURCE ONLY — validation/candidate creation pending SB-LFX-004`

No validation, candidate promotion, review, solver, difficulty or QA controls in this task.

## 6. Canonical process boundary

Use a shell-free Studio -> Python operation.

The canonical Python ingestion operation may accept an owner-selected absolute local source path because this is an explicit import action.

It must reject URLs, missing files/directories, malformed input and unsupported formats.

The destination remains bounded to the governed Factory owner-upload area.

## 7. Real integration required

Add focused tests and one committed real Godot integration proving:

- valid external PNG import;
- explicit OWNER_UPLOAD;
- byte-identical stored source;
- external original unchanged;
- canonical source-record binding;
- SOURCE_ONLY / UNVALIDATED truth;
- same-byte re-import idempotence;
- same filename + different bytes => distinct source identity;
- corrupted existing destination fails closed;
- corrupt/unsupported source leaves no trusted import;
- no downstream validation/promotion claims;
- bounded cleanup.

## 8. Preserve accepted work

Keep SB-LFX-001 and LF06-001..012 green.

Do not refactor Dashboard/Generate/editor/revalidation/reproduce for style.

## 9. Forbidden scope

Do not start:
- SB-LFX-003+;
- Source Art Library;
- Import Validation Wizard;
- candidate/review workflow;
- batch import;
- revision history;
- providers;
- M03/M04/M05;
- Content Platform;
- main game.

Do not modify `TASKS.md`.

## Verification

Run and record:
- focused LFX-002 tests;
- real Godot Import integration;
- LFX-001 retained tests;
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
1. full GitHub URL of `.hiveai/codex-logs/SB-LFX-002-C001_MANUAL_PIXEL_ART_OWNER_UPLOAD_IMMUTABLE_SOURCE_CODEX_LOG.md`;
2. final implementation commit SHA;
3. terminal log-only publication commit SHA.
