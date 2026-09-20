# SB-LFX-002-C001 — Manual Pixel Art OWNER_UPLOAD Immutable Source — Strict Audit Criteria

Document role: INDEPENDENT CHATGPT AUDIT CRITERIA

Target extension:

`SB-LFX-002 — Support manual Pixel Art import with explicit OWNER_UPLOAD provenance and immutable original bytes. [EXTENSION]`

Authoritative product contract:
`docs/product/FACTORY_STUDIO_OWNER_OPERATIONS_EXTENSIONS_V01.md`

## 1. Purpose

Implement the first manual owner-upload ingestion boundary in Factory Studio.

This task creates an immutable source artifact only.

It does NOT perform the later Import Validation Wizard, palette correction, structural QA, candidate promotion, Source Art Library indexing, owner acceptance, or production promotion.

A successfully imported source must remain distinguishable from:
- provider imagery;
- procedural generation;
- generic legacy LOCAL_FILE normalization;
- canonical candidate/level output.

Its explicit origin is:

`OWNER_UPLOAD`

## 2. Existing architecture that must remain truthful

The repository already has deterministic semantic raw/normalization and LEVEL_ART compilation contracts.

Important:
- `SemanticRawArtifact.from_local_file()` currently records `LOCAL_FILE`;
- this must NOT be relabeled or misrepresented as OWNER_UPLOAD;
- existing `CELL_MAJORITY_V1` and `PALETTE_SNAP_V1` remain downstream transformation policies;
- LFX-002 must not silently invoke those policies.

If later tasks derive canonical logical art from an owner upload, the imported original remains immutable and the derived artifact gets its own identity/lineage.

## 3. Severity model

### BLOCKER

Automatic FAIL if:
- imported owner bytes are modified, resized, quantized, recompressed or overwritten;
- provenance does not explicitly distinguish `OWNER_UPLOAD`;
- legacy `LOCAL_FILE` is simply renamed/presented as OWNER_UPLOAD without a real source contract;
- imported source is presented as validated candidate, QA PASS, owner accepted or production-ready;
- import silently runs palette snap, CELL_MAJORITY, structural QA, solver, difficulty or promotion;
- source record becomes a second project/task tracker;
- builder modifies root `TASKS.md`;
- network/provider/credential access is introduced.

### MAJOR

Examples:
- source SHA-256 does not bind exact stored bytes;
- re-import can silently overwrite a different source;
- same filename with different bytes collides;
- source record can point to missing/mismatched original bytes;
- successful import does not preserve the owner-selected original file byte-for-byte;
- invalid/unsupported input leaves a trusted imported-source record behind;
- arbitrary URL input is accepted;
- imported source files are stored outside the governed Factory output/source area;
- no real Godot Import-surface integration proves the workflow.

### MINOR

Examples:
- correct immutable source/provenance but weak display metadata;
- file chooser ergonomics are basic while import truth is correct.

## 4. Canonical owner-upload source contract

Add a narrow canonical Python contract for imported owner source art.

Preferred durable structure under the governed Factory output area:

`level_factory/output/owner-uploads/<source_id>/`

with at minimum:
- exact original source bytes, using a stable internal filename;
- canonical source record JSON.

Recommended deterministic source identity:

`owner-upload-<sha256>`

or an equivalently collision-resistant content-derived identity.

The canonical source record must include at least:
- schema + version;
- source_id;
- origin exactly `OWNER_UPLOAD`;
- source_sha256;
- byte_length;
- media_type;
- original filename as display metadata only;
- decoded original width/height where supported;
- immutable original relative path;
- status that makes clear this is an imported SOURCE, not a validated candidate.

Do not include filesystem path as identity.

## 5. Supported input for C001

Use the repository's already deterministic supported raster profile rather than adding image libraries casually.

C001 may support only canonical strict PNG input (`image/png`) if that is the only currently authoritative deterministic decoder.

Unsupported/corrupt formats fail closed.

Do not claim JPEG/WebP support unless it is actually added to the canonical decoder and independently tested within authorized scope.

## 6. Owner-selected local file boundary

Import must accept an explicitly operator-selected local file.

Reject:
- HTTP/HTTPS or URL-like inputs;
- NUL/malformed paths;
- directories;
- missing files;
- unsupported media;
- inputs exceeding the existing bounded raw-artifact size policy.

Do not mutate or delete the original external file.

The selected source may live outside the repository because manual import is intentionally an owner-selected local-file operation.

Use shell-free bounded process invocation.

## 7. Immutable byte preservation

PASS requires proof that:
- SHA-256 is computed from exact selected source bytes;
- stored source bytes equal selected source bytes byte-for-byte;
- external original bytes remain unchanged;
- source record hash matches stored bytes;
- a subsequent read verifies the record/bytes binding.

No import step may recompress the PNG.

## 8. Collision / idempotence rules

Same bytes imported twice:
- must resolve to the same content identity;
- may return an explicit ALREADY_IMPORTED / SAME_SOURCE disposition;
- must verify existing stored bytes and record before trusting them;
- must not rewrite with divergent metadata.

Same filename with different bytes:
- must produce distinct source identities;
- must never overwrite the first source.

Existing corrupted/mismatched content-addressed source:
- must fail closed, not repair silently.

## 9. Factory Studio Import surface

Make the existing `Import` navigation surface real for this bounded task.

Provide:
- file selection using a suitable Godot FileDialog or equivalent operator-select mechanism;
- optional programmatic/test path setter for headless integration;
- Import action;
- state: EMPTY / IMPORTING / IMPORTED / ALREADY_IMPORTED / ERROR;
- source ID;
- origin OWNER_UPLOAD;
- SHA-256;
- original filename;
- original dimensions if available;
- stored immutable source path.

The UI must explicitly state:

`SOURCE ONLY — validation/candidate creation pending SB-LFX-004`

or equivalent truthful wording.

Do not add palette/QA/solver/accept/reject controls.

## 10. No transformation in LFX-002

The import workflow must not:
- resize;
- crop/pad;
- palette snap;
- change alpha;
- reduce colors;
- compile LEVEL_ART;
- create a production candidate bundle;
- run quality policy;
- infer difficulty.

Any future transformation must create a separate derived artifact and belongs to later audited work.

## 11. Required real runtime integration

PASS requires a committed real Godot integration using the actual Factory Studio scene.

Minimum scenario:

1. create a deterministic valid PNG fixture outside the governed import destination;
2. record its exact bytes/SHA;
3. navigate to real Import surface;
4. import it through the actual Studio -> canonical Python boundary;
5. prove IMPORTED with origin OWNER_UPLOAD;
6. verify stored source bytes exactly equal fixture bytes;
7. verify external fixture remains byte-identical;
8. verify source record binds source ID/SHA/dimensions/path/origin;
9. prove no candidate/QA/solver/difficulty/owner-acceptance claim;
10. re-import same bytes and prove idempotent same identity/no destructive rewrite;
11. import a different-byte PNG with the same display filename and prove distinct source identity/no overwrite;
12. corrupt a copied/target record or stored source in a bounded test destination and prove fail-closed behavior rather than silent repair;
13. try unsupported/corrupt input and prove no trusted source artifact remains;
14. clean all bounded test artifacts.

## 12. Static/security guards

Focused tests must guard:
- literal OWNER_UPLOAD contract;
- no TASKS read/import;
- no provider/network/credential code;
- no normalization/palette/LEVEL_ART calls in the LFX-002 import operation;
- no overwrite of an existing divergent content-addressed source;
- no external-source mutation/delete;
- source-record verification before ALREADY_IMPORTED success.

## 13. Retained regressions / publication

Builder records:
- focused SB-LFX-002 tests;
- real Godot Import integration;
- SB-LFX-001 Dashboard regression;
- relevant LF06-001..012 regressions;
- full pytest;
- compileall;
- Godot headless boot;
- `git diff --check`;
- `git diff -- TASKS.md` empty;
- exact changed-file review;
- exactly one terminal builder-log-only publication commit.

## 14. Scope limits

Do not implement:
- SB-LFX-003 Source Art Library;
- SB-LFX-004 Import Validation Wizard;
- palette/structural validation UI;
- candidate inbox/review;
- batch import;
- revision history;
- provider integration;
- M03/M04/M05;
- production promotion;
- Content Platform or main-game work.

## PASS closure rule

`SB-LFX-002` may close when Factory Studio can ingest an owner-selected supported pixel-art file into a canonical content-addressed immutable source record with explicit OWNER_UPLOAD provenance, preserve original bytes exactly, behave safely under re-import/collision/corruption, make no validation/promotion claims, and prove the flow through real runtime integration.
