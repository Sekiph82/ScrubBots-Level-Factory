# SB-LFX-002-C001 — Manual Pixel Art OWNER_UPLOAD Immutable Source — Strict Audit

Document role: CHATGPT INDEPENDENT STRICT AUDIT

## VERDICT

**PASS / CLOSED**

Severity:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 1

Target extension:
`SB-LFX-002 — Support manual Pixel Art import with explicit OWNER_UPLOAD provenance and immutable original bytes. [EXTENSION]`

## Audited publication chain

- Starting authoritative tracker HEAD: `ccf4536700c9c62c1717ace05f543962e7d955f2`
- Builder implementation: `7e6ad79a5436b013e787509e9b2ab374ed90c78d`
- Terminal builder publication: `adf1edaf8bc4ee78ce9028a084c819fcba3a46b8`
- Terminal publication is exactly one builder-log-only commit.
- Builder log existed before product/test edits, satisfying the corrected log-first governance rule.

## Acceptance findings

### 1. Explicit OWNER_UPLOAD provenance — PASS

A new canonical Python source-ingestion contract exists in `src/scrubbots_pixel_factory/owner_upload.py`.

Persisted source records explicitly bind:
- schema/version;
- content-derived source ID;
- `origin = OWNER_UPLOAD`;
- SHA-256;
- byte length;
- media type;
- original filename as display metadata;
- original dimensions;
- immutable stored relative path;
- source-record path;
- `SOURCE_ONLY`;
- `UNVALIDATED`.

The existing transient `SemanticRawArtifact.from_local_file()` path remains `LOCAL_FILE` and is used only for strict deterministic PNG decoding/dimension verification. It is not persisted or relabeled as OWNER_UPLOAD.

### 2. Exact immutable byte preservation — PASS

Source identity is `owner-upload-<sha256>`, derived from the exact selected bytes.

The import path stores those exact bytes as `source.png` without:
- recompression;
- resizing;
- crop/pad;
- palette snapping;
- alpha changes;
- LEVEL_ART compilation.

The real Godot integration proves:
- stored bytes equal selected bytes;
- the external selected source remains byte-identical;
- the source record hash binds the stored bytes.

### 3. Source-only truth boundary — PASS

The operation returns explicit:
- `SOURCE_ONLY`;
- `UNVALIDATED`;
- source-only notice that validation/candidate creation is pending SB-LFX-004.

Candidate, quality, solver, measured difficulty and owner acceptance are all explicitly unavailable.

No normalization, palette snap, `CELL_MAJORITY`, LEVEL_ART compilation, QA, solver, difficulty or promotion operation is called by the LFX-002 ingestion path.

### 4. Strict supported-format boundary — PASS

C001 reuses the existing deterministic strict PNG decoder.

Corrupt/unsupported input fails closed before a trusted owner-upload source record is created.

No JPEG/WebP support or new image-library dependency is claimed.

### 5. Idempotence / collision safety — PASS

Same exact bytes:
- resolve to the same source ID;
- verify existing stored bytes and record;
- return `ALREADY_IMPORTED`;
- do not rewrite the canonical record.

Same display filename with different bytes:
- produces distinct content identities;
- preserves both sources;
- never overwrites the first source.

Existing malformed/incomplete/divergent content-addressed destinations fail closed rather than being silently repaired or replaced.

The original filename is intentionally display-only and therefore is not part of the content identity.

### 6. Local-file / process security boundary — PASS

The source must be an existing local file.

The canonical ingestion rejects URL-like input, NUL/malformed paths, directories/missing files, oversized input and unsupported raster content.

Studio invokes the Python launcher through the existing shell-free bounded process bridge.

No HTTP/provider/API-key/credential/telemetry dependency was introduced.

### 7. Real Factory Studio Import surface — PASS

The prior inert Import surface is now a bounded real UI with:
- FileDialog selection;
- programmatic/headless path setter;
- Import action;
- EMPTY / IMPORTING / IMPORTED / ALREADY_IMPORTED / ERROR states;
- source ID;
- OWNER_UPLOAD provenance;
- hash/bytes/media/filename;
- original dimensions;
- immutable stored source/record paths;
- explicit source-only notice.

No palette/QA/solver/difficulty/accept/reject/promotion controls were added.

### 8. Real runtime integration — PASS

The committed real Godot integration:
- loads the actual Factory Studio scene;
- navigates to real Import;
- creates two external valid PNG fixtures using the same filename;
- imports through Studio -> Gateway -> canonical Python;
- checks exact source bytes and external immutability;
- checks OWNER_UPLOAD / SOURCE_ONLY / UNVALIDATED;
- checks canonical source record bindings;
- proves same-byte idempotence;
- proves same-name/different-byte identity separation;
- corrupts an existing target record and proves fail-closed ERROR;
- rejects corrupt input without trusted identity;
- restores/cleans bounded test artifacts.

Builder reports the integration exits 0 with the committed PASS marker.

### 9. Scope / regression / publication — PASS

Implementation scope is limited to:
- canonical owner-upload source contract;
- launcher operation;
- Gateway bridge;
- Factory Studio Import surface;
- Workspace hookup;
- real Import integration suite;
- focused tests;
- project-boundary allowlist;
- builder log.

No root `TASKS.md`, prompts/audits, provider integration, Source Art Library, Import Validation Wizard, candidate/review workflow, M03/M04/M05, Content Platform or main-game implementation changed.

Builder reports:
- focused LFX-002: **4 passed**;
- retained bounded regression: **35 passed**;
- full pytest: **742 passed, 1 warning**;
- real Godot Import integration: exit 0 / PASS marker;
- compileall: PASS;
- Godot headless boot: PASS;
- staged diff check: PASS;
- `TASKS.md` untouched.

These counts are builder-reported. Independent audit additionally inspected the committed source contract, UI/process bridge, real integration, exact implementation diff and terminal publication topology.

## NOTE

The focused Python unit test contains one tautological byte comparison when checking the source record after renamed same-byte re-import. This does not weaken acceptance because the committed real Godot integration separately snapshots the record bytes before re-import and proves they remain exactly unchanged afterward.

## Closure

`SB-LFX-002` is accepted as **PASS / CLOSED**.

Factory Studio now has a real manual owner-upload source-ingestion boundary with explicit OWNER_UPLOAD provenance, content-addressed immutable identity, byte-exact preservation, fail-closed re-import/corruption behavior and no premature validation or candidate claims.
