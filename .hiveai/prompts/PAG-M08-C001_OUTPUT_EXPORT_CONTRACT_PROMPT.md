# PAG-M08-C001 — Output / Export Contract
Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous closing audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M07-C003_REVIEW_EVIDENCE_AND_SYMMETRY_CONTRACT_CLOSURE_STRICT_AUDIT.md`

Current tracker:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/TASKS.md`

## 1. Mission

Implement and prove the complete `PAG-M08 — Output / Export Contract` scope, tasks `PAG-0801` through `PAG-0830`.

M08 turns an already-generated, immutable logical grid plus its generation/quality evidence into deterministic local artifacts suitable for later CLI and Level Factory consumption.

Expected bundle conceptually:

```text
candidate_id/
  artwork.json
  metadata.json
  artwork.png
  artwork.preview.png   # optional presentation-only artifact
```

M08 does not implement the M09 CLI or batch orchestration.

## 2. GitHub-first authority

Before editing, read completely from GitHub `main`:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. v3 machine block and current state in `.hiveai/TASKS.md`
4. `.hiveai/EVENTS.jsonl`
5. `tasks.md`, especially all M08 tasks and global Definition of Done
6. `.hiveai/CYCLE_INDEX.md`
7. `AGENTS.md`
8. `GOVERNANCE.md`
9. M07 C003 strict audit
10. M02 request/result/RNG contracts and tests
11. M01 palette/difficulty contracts and tests
12. M03-M06 representative generator/router outputs and metadata
13. M07 quality report/hash APIs and tests
14. `pyproject.toml`, `.gitignore`, package exports and offline guard
15. this prompt

GitHub `main` is current-state authority.

Authorized local workspace only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never substitute or modify:
`C:\Users\sekip\Desktop\ScrubBots`

Use only non-destructive synchronization. No hard reset, force push, blanket restore/clean or silent auto-rebase.

## 3. Matching builder log

Before the first M08 implementation/test/golden edit, create:

`.hiveai/codex-logs/PAG-M08-C001_OUTPUT_EXPORT_CONTRACT_CODEX_LOG.md`

Exact H1:

`# PAG-M08-C001 — Output / Export Contract`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- timestamp, repository, branch, origin and starting HEAD/status;
- GitHub-first reads;
- preserved pre-existing local changes;
- architecture decisions;
- implementation edits;
- focused failures/corrections;
- golden creation/regeneration;
- test commands/results;
- offline/no-resize/static checks;
- final changed paths;
- implementation/evidence commit SHA;
- push result;
- final post-log-publication local HEAD and `origin/main` equality.

Do not edit ChatGPT-owned tracker/audit/task acceptance state and do not self-audit.

## 4. Preserve accepted M00-M07 contracts

M08 must consume existing authoritative contracts rather than fork them.

Preserve exactly:

- difficulty dimension bands and rectangular support;
- canonical C01..C16 RGB mapping;
- used-palette ascending actual-use semantics;
- BG01 presentation-only rule;
- `GenerationRequest` canonical serialization;
- immutable successful `GenerationResult` and its digest/provenance contract;
- deterministic RNG/stage-seed provenance;
- M03-M06 generator behavior and metadata;
- M07 logical-grid hash and quality/diversity semantics;
- fully offline runtime;
- one logical pixel = one gameplay cell.

Do not mutate a generated grid during export. Reject contradictory export inputs rather than fixing/recoloring/resizing them.

## 5. Output package boundary

Create a focused project-owned output/export package, preferably under:

`src/scrubbots_pixel_factory/output/`

Exact module names are implementation-detail choices, but responsibilities must stay separated and testable:

- logical artifact schema/validation/canonical serialization;
- metadata/provenance/quality serialization;
- exact logical PNG encoder/decoder for the project's own PNG profile;
- optional preview encoder;
- filesystem bundle writer/reader/round-trip validator.

Expose only the minimum stable API required by later M09 work.

Do not put CLI argument parsing or batch orchestration into M08.

## 6. Logical artwork JSON contract — PAG-0801..0807

Define a versioned, fail-closed logical-artwork artifact schema.

At minimum `artwork.json` must bind:

- schema name and integer schema version;
- explicit caller-supplied `candidate_id`;
- canonical difficulty;
- exact width and height;
- actual local palette as ascending canonical C-IDs;
- row-major logical cells;
- logical-grid identity/hash using the existing M07 project-owned hash where appropriate.

The canonical index rule is exactly:

`index = y * width + x`

Document and directly test this rule on rectangular grids.

`artwork.json` represents immutable logical artwork truth. It must not contain mutable human-review state or a field whose change would imply the cells changed when they did not.

Canonical JSON must be deterministic:

- UTF-8;
- no timestamps;
- no random UUIDs;
- no local absolute paths;
- stable keys/list ordering;
- no NaN/Infinity;
- same logical artifact input => byte-identical JSON.

## 7. Candidate identity

M08 must not invent a time-based candidate identity.

The exporter should require an explicit deterministic `candidate_id` from its caller. M09 can later define user-facing naming policy.

If `candidate_id` becomes a filesystem directory name, validate it conservatively and reject path traversal, separators, absolute-path semantics, empty strings, `.` and `..`. Do not silently sanitize two distinct IDs into the same path.

The same candidate ID must be bound consistently across `artwork.json` and `metadata.json`.

## 8. Metadata JSON contract — PAG-0808..0814

Keep generation/quality state separate from immutable `artwork.json`.

At minimum `metadata.json` must deterministically record and bind to the exact artwork:

- schema name/version;
- candidate ID;
- artwork schema/version and logical-grid hash/digest binding;
- canonical difficulty and resolved dimensions as needed for cross-checking;
- generator mode;
- actual generator ID/version;
- master seed using the existing typed/canonical semantics;
- deterministic stage sub-seeds/provenance already owned by M02;
- canonical GenerationRequest/generation config and versioned generator options;
- successful `GenerationResult` digest;
- source/exemplar provenance where it genuinely exists;
- generator/router/hybrid metadata where relevant and supplied by the authoritative generating layer;
- M07 quality policy/metrics;
- M07 quality decision and stable rejection codes.

Do not fabricate exemplar/source provenance for MASK/RULES or any path that did not use one.

Do not silently discard WFC/HYBRID/AUTO provenance merely because it does not fit a flat schema. Preserve supplied JSON-compatible generator metadata canonically under an explicit versioned namespace/binding.

Quality acceptance/rejection state must be separate from immutable grid truth. A structurally quality-rejected but otherwise valid successful `GenerationResult` may still be represented as the same immutable artwork plus a REJECT quality decision. Export must never recolor/regenerate/mutate it to make quality pass.

A failed `GenerationResult` has no complete logical artwork and must not be exported as a successful artwork bundle.

## 9. Cross-file integrity

Add explicit validation that `artwork.json`, `metadata.json`, and `artwork.png` describe the same candidate.

At minimum verify:

- candidate IDs agree between JSON artifacts;
- width/height agree;
- palette equals actual used C-ID subset;
- cell count equals width*height;
- logical-grid hash agrees;
- metadata's GenerationResult/artwork binding agrees;
- quality analysis, if supplied, is for the exact same dimensions/cells rather than a different grid;
- PNG decoded cells exactly equal `artwork.json` cells.

A mismatched file or mismatched quality report must fail closed with a stable project-owned error/exception type.

## 10. Deterministic logical PNG profile — PAG-0815..0819

The repository currently has zero runtime dependencies. Preserve that property unless an independently necessary reason is proven. For M08, prefer a small project-owned standard-library PNG codec for the exact format the project itself emits rather than introducing Pillow or another general imaging runtime.

Use a deliberately narrow deterministic logical PNG profile:

- PNG signature;
- IHDR width/height exactly equal logical width/height;
- 8-bit RGB truecolor is preferred;
- no palette approximation;
- no alpha needed for logical art;
- no interlace;
- exact canonical RGB per C-ID;
- one output pixel per logical cell;
- no presentation grid lines;
- no antialiasing;
- no resizing/interpolation;
- no time/text/profile metadata that changes bytes between runs;
- deterministic scanline/filter policy, preferably filter type 0 for every row;
- deterministic IDAT construction/compression under the supported environment;
- valid CRCs.

If a different equally strict profile is chosen, document why and prove every invariant above.

The logical PNG encoder must consume logical cells directly. It must never render a larger image then shrink it.

## 11. Strict decoder for the generator's own PNG — PAG-0822..0828

Implement only enough PNG decoding to validate/reconstruct PNGs produced by this project-owned logical PNG profile. M08 does not need a general-purpose image library.

The decoder/validator must fail closed on malformed or unsupported project PNGs, including where applicable:

- bad PNG signature;
- malformed chunk lengths;
- CRC failure;
- missing/duplicate/invalid IHDR;
- unsupported bit depth/color type/interlace;
- decompressed payload length mismatch;
- unsupported scanline filter if the project profile permits only filter 0;
- extra/truncated logical pixel data;
- RGB not mapping exactly to one canonical C01..C16 value;
- impossible/invalid dimensions.

Because the canonical palette mapping is one-to-one, exact RGB can map back to canonical C-IDs.

Do not claim that candidate ID, difficulty or generation provenance are recoverable from PNG pixels alone. PNG round-trip recovery is authoritative for exact dimensions/RGB/cells/local palette. Non-pixel identity/provenance comes from the JSON artifacts and must be cross-bound there.

## 12. Raw RGB byte truth — PAG-0824

Define a simple deterministic raw logical RGB byte representation in row-major order:

```text
R,G,B for cell[0]
R,G,B for cell[1]
...
```

Directly prove:

- expected length = `width * height * 3`;
- bytes derive only from exact canonical C-ID mapping;
- decoded PNG raw RGB bytes are byte-identical to bytes derived from logical JSON;
- rectangular row boundaries are correct.

## 13. Optional preview PNG — PAG-0820..0821

Implement an optional presentation-only enlarged preview.

For V1 C001, the simplest accepted preview is exact integer nearest-neighbor replication:

- scale is an explicitly validated positive integer;
- every logical source pixel becomes exactly a `scale x scale` solid block;
- no interpolation/resampling algorithm is used;
- no source logical dimension/cell/palette is changed.

BG01 and presentation grid lines may be supported only in the preview layer, never in `artwork.png` or logical JSON. They are optional. Do not add them merely to satisfy the task wording.

If grid lines are implemented, tests must prove they are presentation-only and do not affect round-trip logical truth.

## 14. Bundle write semantics

Create deterministic local bundle-writing behavior suitable for M09 to call later.

Requirements:

- explicit destination directory;
- deterministic file names;
- create only the intended candidate directory/files;
- no current-time suffixes;
- no network calls;
- no global mutable state;
- no silent overwrite with conflicting content;
- re-writing byte-identical content is allowed and must not produce different bytes;
- conflicting existing candidate content must fail clearly unless an explicit overwrite policy is deliberately designed and tested.

Avoid leaving partially valid successful bundles after an error. A small write-to-temporary-then-replace strategy inside the chosen destination is acceptable if deterministic final artifacts are preserved and cleanup is tested.

## 15. Golden PNG/JSON round-trip — PAG-0829

Commit deterministic project-owned M08 golden evidence under `tests/golden/` or an equally clear test path.

At minimum include golden logical JSON/PNG pairs that prove:

- one canonical legal difficulty case;
- at least one rectangular case;
- multiple canonical colors;
- exact logical-resolution PNG dimensions;
- exact byte-level RGB round trip;
- PNG -> decoded cells == JSON cells;
- JSON -> PNG bytes == committed expected PNG bytes for the supported environment/profile;
- local palette equals actual ascending used C-ID set.

Do not use third-party artwork. Golden logical patterns must be synthetic/project-owned test fixtures or deterministic outputs already owned by this repository.

Exercise all four difficulty bands in tests, including a 59x59 VERY_HARD export/round-trip workload. Not every band needs a committed binary golden if focused deterministic tests provide equivalent evidence.

## 16. No-meaningless-diff reproducibility — PAG-0830

Directly prove that re-exporting the same candidate from the same successful result + same generator metadata + same quality report produces byte-identical deterministic artifacts.

Test at least:

- `artwork.json` bytes identical;
- `metadata.json` bytes identical;
- `artwork.png` bytes identical;
- preview PNG bytes identical when enabled;
- exact file set unchanged;
- no timestamps or machine paths enter deterministic file content.

Also prove that a meaningful logical-grid change changes the appropriate artwork hash/PNG/JSON rather than being hidden by stale metadata.

## 17. Representative generator provenance integration

Exercise export from representative accepted outputs of existing families without modifying those generators:

- MASK;
- RULES;
- HYBRID;
- AUTO;
- synthetic-test-only WFC where available.

For each represented family, assert the export preserves the successful GenerationResult's exact grid/dimensions/palette/seed/generator identity.

For WFC/HYBRID/AUTO, also bind relevant available source/exemplar/stage/router metadata. If an API boundary exposes metadata outside `GenerationResult`, pass it explicitly into M08 rather than widening or weakening the M02 result contract without necessity.

## 18. Negative/corruption tests

Add focused negative tests that would catch plausible false-green export implementations.

At minimum cover:

- off-palette RGB/cell;
- width*height mismatch;
- incorrect/non-ascending or unused local palette;
- artwork/metadata candidate-ID mismatch;
- quality report bound to a different logical grid;
- corrupted PNG CRC;
- PNG RGB changed to a noncanonical value;
- truncated PNG/decompressed payload;
- illegal preview scale;
- path traversal candidate ID;
- failed GenerationResult passed to successful exporter;
- tampered artwork hash/digest;
- unsupported artifact schema/version on read.

Round-trip readers must not silently accept or repair these cases.

## 19. Required tests and evidence

Create dedicated M08 tests, preferably separated into unit/integration/golden concerns.

At minimum run and log:

1. all M08 unit tests;
2. M08 golden PNG/JSON tests;
3. M08 corruption/negative tests;
4. M08 representative generator integration tests;
5. rectangular export/round-trip;
6. 59x59 export/round-trip;
7. deterministic repeated export in-process;
8. cross-process/PYTHONHASHSEED deterministic JSON and PNG evidence;
9. M01/M02 contract regressions;
10. M03 MASK regressions;
11. M04 RULES regressions;
12. M05 WFC regressions;
13. M06 router/hybrid/replay/AUTO regressions;
14. all M07 quality/diversity regressions;
15. full repository pytest;
16. standalone package import.

Report exact commands and counts. Do not hide initially failing tests; record the defect/correction chronology in the builder log.

## 20. Static/offline/source checks

Run and log checks proving:

- no runtime network/API/cloud path was added;
- no `requests`, HTTP client, socket use outside the existing offline guard, or remote URL fetch exists in output runtime;
- no resize/resample/interpolation call exists in logical PNG path;
- preview uses only exact integer replication;
- no BG01 enters logical JSON or logical PNG;
- no C17+ or arbitrary RGB is accepted;
- no timestamps/absolute local paths enter committed goldens or deterministic artifacts;
- no built-in randomized `hash()` is used for artifact identity;
- no M09+ implementation was introduced;
- `git diff --check` passes;
- `python -m pip check` result is recorded truthfully.

Do not change dependencies merely to silence an unrelated local environment warning.

## 21. Expected source scope

Expected additions/changes are primarily:

- `src/scrubbots_pixel_factory/output/**`;
- package export surfaces only where needed;
- `tests/unit/test_m08_*`;
- `tests/integration/test_m08_*`;
- `tests/golden/test_m08_*` plus small deterministic project-owned golden artifacts;
- focused M08 documentation if useful;
- matching C001 builder log.

Minimal changes to existing M01-M07 production files are allowed only when a focused M08 integration test proves an actual missing public boundary. Explain such changes in the log.

Do not edit:

- `.hiveai/TASKS.md`;
- `.hiveai/EVENTS.jsonl`;
- `tasks.md` acceptance/checkbox state;
- `.hiveai/CYCLE_INDEX.md`;
- `.hiveai/audits/**`;
- historical used prompts/logs/audits.

Do not begin M09, M10 or M11.

## 22. Acceptance mapping

The builder log must include a compact mapping from every M08 task ID to implementation/test evidence:

- PAG-0801..0814 JSON/metadata contract;
- PAG-0815..0821 logical/preview PNG;
- PAG-0822..0828 round-trip validation;
- PAG-0829 committed golden pair evidence;
- PAG-0830 byte-stable no-meaningless-diff evidence.

Do not mark tracker checkboxes yourself. The map is evidence for ChatGPT audit.

## 23. Audit gate

Stop after implementation, evidence, commit, push and final equality verification.

Return the matching builder log for independent ChatGPT strict audit.

Only ChatGPT may issue PASS / CONDITIONAL / FAIL or advance M08 task/tracker state.

A green pytest aggregate is necessary but not sufficient. The audit will independently inspect artifact semantics, PNG bytes/profile, corruption gates, cross-file bindings, provenance preservation, deterministic goldens and diff scope.