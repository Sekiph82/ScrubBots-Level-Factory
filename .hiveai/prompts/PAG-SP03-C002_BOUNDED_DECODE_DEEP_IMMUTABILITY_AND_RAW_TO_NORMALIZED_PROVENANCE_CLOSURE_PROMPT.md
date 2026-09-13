# PAG-SP03-C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure
Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before coding:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `.hiveai/audits/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_STRICT_AUDIT.md`;
3. `.hiveai/prompts/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_PROMPT.md`;
4. `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`;
5. accepted SP01/SP02 semantic/provider contracts;
6. current SP03 normalization implementation/tests/docs;
7. M07/M08/M09 deterministic provenance/export contracts;
8. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do not use hidden legacy `.hiveai` tracker/control-plane files as current status authority.

## Mission

Implement **SP03-C002 only** and close exactly:

- `F-PAG-SP03-C001-001` — decompression-bomb memory bound bypass;
- `F-PAG-SP03-C001-002` — mutable nested normalization report state;
- `F-PAG-SP03-C001-003` — incomplete raw-to-normalized provider/request provenance binding;
- `F-PAG-SP03-C001-004` — LEVEL_ART normalization request legality gap.

Preserve the accepted C001 direction:

- immutable raw bytes/hash;
- exact-size 24x24 no-resize path;
- deterministic `AREA_AVERAGE_V1` baseline;
- explicit fit-center letterbox;
- `PRESERVE_ALPHA` / `OPAQUE_AS_IS`;
- ASSET_ART `PRESERVE_SOURCE_RGBA`;
- no LEVEL_ART final emission in C002;
- no network/provider call;
- no provider credits;
- no SP04/M11.

Do not edit root `TASKS.md`.

---

# 1. Strict bounded PNG decompression

Current defect:

`_decode_png_rgba()` limits `decompress(..., expected_length + 1)` but then calls unrestricted `decompressor.flush()`, which can expand `unconsumed_tail` far beyond the expected raster budget before the final length check.

Required behavior:

- decompressed scanline output must never materially exceed `expected_length` plus at most one sentinel byte used to detect overflow;
- do not call any zlib operation that can emit unbounded remaining output;
- process compressed input incrementally or otherwise enforce a hard output budget across **all** decompression stages;
- reject truncated streams;
- reject trailing compressed members/data;
- reject streams that produce more than exact expected scanline bytes;
- reject streams that do not reach zlib EOF within the bounded process;
- preserve CRC/chunk/profile restrictions already accepted in C001 unless strictly required for the security fix;
- keep `RAW_ARTIFACT_MAX_BYTES`, raw raster bound and `MAX_DECODE_PIXELS` explicit;
- no dependency addition solely for this closure unless justified by a smaller/safer architecture and prompt authority.

## 1.1 Required bomb test

Add a compact synthetic PNG whose IHDR claims a tiny legal raster but whose compressed IDAT expands to a very large byte sequence.

The test must prove:

- decoder rejects with `SemanticDecodeError` or a specific typed normalization error;
- rejection occurs because decompressed output exceeds the exact budget;
- the test does **not** itself allocate a giant expanded Python bytes object merely to assert failure;
- normal valid PNG fixtures remain green.

Also add tests for:

- exactly expected decompressed length -> PASS;
- expected length + 1 -> fail closed;
- truncated zlib stream -> fail closed;
- trailing compressed/unused data -> fail closed.

---

# 2. Deep immutability of deterministic report state

Current defect:

`SemanticNormalizationReport` is frozen but stores `crop_pad` as a mutable mapping. Normalizer passes an ordinary `dict`, so callers can mutate report state after construction and thereby change `report.digest()` and `SemanticNormalizedArtifact.digest()`.

Required behavior:

- all values participating in deterministic report/artifact identity must be deeply immutable after construction;
- copy caller-owned mutable inputs before storing;
- freeze `crop_pad` into a canonical immutable representation;
- canonical serialization must remain stable and JSON-compatible;
- only supported primitive value types may enter deterministic crop/pad identity;
- caller mutation of the original input mapping after report construction must not affect report bytes/digest;
- direct mutation through the stored report field must be impossible through normal Python mapping mutation operations;
- repeated `canonical_bytes()`/`digest()` calls must remain byte-identical.

Acceptable implementation examples:

- private copied dict wrapped by `MappingProxyType`, with deterministic thawing;
- sorted immutable tuple structure plus read-only mapping/property facade;
- shared canonical freeze/thaw helper already consistent with SP01 contracts.

Do not use a mutable dict merely because the dataclass is frozen.

Required tests:

1. construct report from caller dict, record report/artifact digest, mutate caller dict -> no identity change;
2. attempt `report.crop_pad["offset_x"] = ...` -> mutation impossible;
3. report/artifact digest stable before/after failed mutation attempt;
4. exact-size and letterbox reports remain canonical and deterministic.

---

# 3. Exact raw-to-normalized provenance binding

Current defect:

`SemanticNormalizedArtifact` contains:

- `source_raw_artifact_digest`, and
- duplicated `provider_id`, `provider_version`, `workflow_version`, `model_id`, `request_digest`.

Those duplicated fields are not validated against the raw artifact identified by the source digest. A forged/replaced normalized artifact can therefore retain source digest/report/pixels while changing convenience provenance fields.

Required behavior:

Choose one fail-closed design:

### Preferred design A — canonical immutable source-provenance snapshot

Create a small immutable value such as `SemanticSourceProvenance` containing the exact source identity fields required downstream and its own canonical digest. Build it only from `SemanticRawArtifact` and bind its digest into normalized artifact identity.

or

### Design B — checked normalized constructor requiring raw artifact

Hide/directly constrain free construction and expose a checked constructor that receives the exact `SemanticRawArtifact`, derives provider/request fields, and validates report/request/pixel binding.

or an equivalent architecture with the same security property.

Required invariants:

- normalized artifact source digest == exact raw artifact digest;
- provider id/version/workflow/model/request digest are derived from or cryptographically cross-checked against that same source artifact;
- normalization request digest is exact;
- report source/request/output hash/target dims/policies exactly match;
- coordinated tampering must fail even if every field is syntactically valid;
- no absolute source path, signed URL, secret, audit URL or provider credential enters deterministic identity.

Required tests:

- exact raw/request/report/output chain -> PASS;
- source A digest + provider fields from source B -> reject;
- same raw digest + forged provider id/version/workflow/model/request digest -> reject;
- report from request A + output/request B -> reject;
- successful normalizer output remains deterministic and unchanged in normal use.

---

# 4. LEVEL_ART normalization-request legality

Current defect:

`SemanticNormalizationRequest` uses only generic `1..1024` target checks. Supplying `output_class=LEVEL_ART` plus `SCRUBBOTS_C01_C16` can represent illegal board dimensions even though final normalization later fails.

C002 must preserve owner-locked LEVEL_ART legality.

Use one of these bounded approaches:

### Preferred

Add explicit `difficulty` to `SemanticNormalizationRequest` for LEVEL_ART and validate target width/height with the existing canonical difficulty dimension resolver/validator.

For ASSET_ART, `difficulty` must be absent/ignored only if the contract clearly rejects accidental LEVEL semantics.

### Acceptable minimal C002 alternative

Since final LEVEL_ART normalization is intentionally not implemented yet, refuse **all** `LEVEL_ART` `SemanticNormalizationRequest` construction with an explicit typed error saying final LEVEL_ART normalization is deferred until the canonical palette/difficulty policy cycle.

Do not accept a generic arbitrary LEVEL_ART target merely because final normalization would fail later.

If choosing the preferred path, required tests include:

- EASY 20x20 valid, 19x20 invalid, 30x20 invalid;
- MEDIUM 30x30 valid, 29x30 invalid;
- HARD 40x40 valid, 39x40 invalid;
- VERY_HARD 50x50 valid, 49x50 invalid;
- rectangular dimensions inside the same difficulty band valid;
- ASSET_ART 24x24 remains independent of difficulty.

If choosing minimal refusal, test that every C002 LEVEL_ART normalization request fails at construction with a stable typed error and ASSET_ART remains unaffected.

---

# 5. Preserve exact-size and downsample semantics

Do not regress:

- exact 24x24 decoded RGBA -> 24x24: no resample/interpolation;
- raw bytes/hash unchanged after normalization;
- 2048x2048 synthetic source -> deterministic 24x24 result;
- aspect mismatch uses explicit `FIT_CENTER_LETTERBOX_V1`;
- `PRESERVE_ALPHA` and `OPAQUE_AS_IS` remain explicit;
- `PRESERVE_SOURCE_RGBA` remains first ASSET_ART palette baseline;
- no C01..C16 forced onto ASSET_ART;
- `SemanticNormalizedArtifact.as_m08_artwork()` remains blocked;
- real Magnific visual acceptance does not imply owner acceptance of local resampler quality.

No visual-algorithm redesign in C002.

---

# 6. Real provider artifact boundary

Do not call Magnific or PixelLab in C002.

Do not use private signed URLs or identifiers in Git history.

If the owner-approved Magnific raw file is not locally available, continue using synthetic fixtures for implementation tests.

Document that real provider-byte ingestion remains a post-C002 verification step.

Do not broaden decoder capability to arbitrary PNG/JPEG/WebP merely to simulate provider compatibility.

---

# 7. CLI safety preservation

Preserve:

- local-file-only semantic normalization;
- source never overwritten;
- no network/provider SDK;
- deterministic JSON manifest/report;
- explicit output class and dimensions;
- no secrets/private URLs in output.

Add regression coverage if provenance/LEVEL request changes affect CLI behavior.

---

# 8. Required focused test matrix

At minimum prove:

## Bounded decode

1. valid strict-profile PNG decodes;
2. decompressed exact expected length passes;
3. expected+1 byte fails;
4. compact high-expansion bomb fails within hard output budget;
5. truncated stream fails;
6. trailing/unused compressed data fails.

## Deep immutability

7. caller crop-pad dict mutation cannot alter report/artifact digest;
8. stored crop-pad mutation is impossible;
9. report/artifact digest remains stable across repeated calls.

## Provenance binding

10. exact raw/request/report/output chain passes;
11. source A + provider/request provenance B rejects;
12. forged provider/version/workflow/model/request field rejects;
13. report/request cross-pairing rejects.

## LEVEL legality

14. chosen LEVEL_ART legality strategy is explicitly tested;
15. ASSET_ART 24x24 remains valid and difficulty-independent.

## Existing C001 behavior

16. exact 24x24 fast path pixel-identical;
17. 2048->24 deterministic baseline unchanged;
18. alpha policies unchanged;
19. raw hash unchanged after normalization;
20. ASSET_ART remains separate from M08 LEVEL_ART;
21. CLI source overwrite protection remains;
22. SP01/SP02 focused regression green;
23. full repository regression green.

---

# 9. Security requirements

- no network;
- no provider call;
- no provider SDK invocation;
- no browser automation;
- no secret/env credential required;
- no absolute path in deterministic identity;
- hard decompressed output budget enforced throughout zlib lifecycle;
- malformed PNG fail closed before unbounded allocation;
- deterministic identity state deeply immutable.

---

# 10. Scope exclusions

Do NOT:

- edit root `TASKS.md`;
- begin SP03-C003/SP04/SP05/SP06/M11;
- change M00-M10 algorithms;
- change provider bridges except a compile/import compatibility change strictly required by SP03 types;
- call providers or spend credits;
- add semantic recognizability scoring;
- build Studio UI;
- implement final C01..C16 LEVEL_ART quantization;
- change owner-approved 24x24 ASSET_ART baseline;
- claim owner acceptance of local downsampler quality;
- self-audit or mark SP03 accepted.

---

# 11. Builder log

Create BEFORE any C002 source/test/doc edit:

`.hiveai/codex-logs/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-SP03-C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure`

Role line:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- repository/branch/start HEAD/origin HEAD/divergence;
- preserved user dirt;
- authority files read from GitHub;
- exact security design for bounded zlib output;
- exact deep-freeze/provenance design;
- exact files changed;
- every focused test failure/correction;
- SP03 focused result;
- SP01/SP02/SP03 focused result;
- full repository regression;
- compile/import/CLI/network/secret checks;
- implementation commit/push;
- final local HEAD == origin/main and divergence `0 0`.

Builder must not write the independent audit.

---

# 12. Stop rule

After implementation and verification:

1. complete builder log;
2. commit/push `main`;
3. verify HEAD == origin/main and divergence `0 0`;
4. STOP for independent ChatGPT audit.

Do not begin later work.
