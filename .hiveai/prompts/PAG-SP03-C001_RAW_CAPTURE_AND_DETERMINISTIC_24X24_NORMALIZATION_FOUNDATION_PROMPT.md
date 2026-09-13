# PAG-SP03-C001 — Raw Capture & Deterministic 24x24 Normalization Foundation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`

## Authority

Read from GitHub before coding:

1. root `TASKS.md` — ONLY current project-status tracker;
2. `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`;
3. `.hiveai/audits/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_STRICT_AUDIT.md`;
4. `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`;
5. `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`;
6. accepted SP01 semantic contracts and SP02 provider bridges;
7. current M07/M08/M09 deterministic quality/export/provenance contracts;
8. `AGENTS.md`, `GOVERNANCE.md`, `CLAUDE.md`.

Do not use hidden legacy `.hiveai` trackers as current status authority.

## Owner-locked decisions entering SP03

The owner has explicitly accepted:

- the live Magnific wizard visual direction;
- `24x24 px` as the first owner-approved `ASSET_ART` baseline target;
- `recraft-v4-1` as a valid semantic smoke provider/model direction for this evidence;
- provider-neutral architecture remains mandatory.

This **does not** change LEVEL_ART contracts:

- EASY 20–29 each axis;
- MEDIUM 30–39;
- HARD 40–49;
- VERY_HARD 50–59;
- C01..C16 logical palette;
- existing difficulty color bands;
- one logical pixel = one gameplay cell.

Do not reinterpret 24x24 as a LEVEL_ART board size.

## Mission

Implement **SP03-C001 only**.

Build the first deterministic normalization foundation that can safely accept raw semantic-provider image bytes, preserve them immutably, decode them deterministically, produce an explicit normalized `ASSET_ART` result at the requested target size, and retain exact raw-to-normalized provenance.

The primary owner-approved target for this cycle is **24x24 ASSET_ART**.

Do not begin provider/model qualification (SP04), LEVEL_ART semantic integration (SP05), semantic scoring (SP06), Studio UI, weekly batch, or M11.

Do not spend Magnific or PixelLab credits.

Do not call external providers.

Do not edit root `TASKS.md`.

---

# 1. New normalization boundary

Introduce a small explicit normalization package under the semantic subsystem, for example:

`src/scrubbots_pixel_factory/semantic/normalization/`

Exact filenames may differ if architecture is cleaner, but the public contract must include equivalent concepts:

- `SemanticRawArtifact`
- `SemanticNormalizationRequest`
- `SemanticNormalizedArtifact`
- `SemanticNormalizationReport`
- one deterministic normalizer entry point

Do not overload `SemanticImageCandidate` into being the normalized object.

Raw provider candidate and normalized artwork are different lifecycle states.

## 1.1 SemanticRawArtifact

Must preserve at minimum:

- exact immutable raw bytes;
- raw SHA-256;
- provider candidate digest;
- provider id/version/workflow/model;
- request digest;
- requested logical dimensions;
- returned provider raster dimensions;
- media type;
- source status must be SUCCESS;
- input provenance/reference hashes already carried by SP01/SP02;
- no filesystem path in deterministic identity.

Construction from a successful `SemanticImageCandidate` must validate:

- bytes hash;
- candidate success;
- dimensions;
- request/provider provenance already present in candidate;
- no mutation/copy ambiguity.

The raw artifact must expose its own deterministic digest.

## 1.2 Raw immutability

Normalization must never overwrite or mutate raw provider bytes.

Tests must prove the SHA-256 and raw byte sequence are identical before and after normalization.

---

# 2. SemanticNormalizationRequest

Define an immutable/versioned request that binds:

- source raw artifact digest;
- output class;
- target width/height;
- normalization policy version;
- background/transparency policy;
- resize policy;
- crop/pad policy;
- palette policy identifier;
- optional source-region/alpha decisions if needed.

For C001:

### ASSET_ART

- 24x24 must be fully supported and first-class;
- retain existing ability to represent other accepted ASSET_ART sizes, but do not expand scope into a full asset policy redesign;
- ASSET_ART must **not** inherit LEVEL_ART difficulty/color-band validation;
- no forced C01..C16 mapping in C001 unless explicitly selected by a future palette policy;
- preserve RGBA where appropriate.

### LEVEL_ART

- request legality must continue to use existing LEVEL_ART dimension contracts;
- do not implement final LEVEL_ART palette quantization/color-band enforcement in C001;
- if normalization is asked to emit final LEVEL_ART without the future required palette policy, fail closed with an explicit typed error rather than silently producing non-canonical LevelData.

---

# 3. Deterministic decode

Use a deterministic, local image decoding path.

Requirements:

- PNG/JPEG/WebP decoding only if explicitly supported and tested;
- normalize decoded pixels to one documented working mode, preferably RGBA8;
- reject corrupt/unsupported image data with typed error;
- decoder must not use network;
- decoded width/height must match provider candidate returned dimensions;
- EXIF/orientation behavior must be explicit and deterministic;
- do not silently color-manage differently across machines if avoidable;
- document Pillow/version dependency if Pillow is used.

If adding Pillow to project dependencies, pin a compatible bounded version and document why it is now core normalization infrastructure.

---

# 4. Exact-size fast path

If decoded raw artwork already exactly matches the normalization target dimensions:

- do **not** resize;
- do **not** resample;
- do **not** interpolate;
- pixel bytes after canonical decode should be preserved as the normalized pixel matrix, subject only to the explicitly selected background/alpha policy;
- report `resize_applied = false` or equivalent;
- record exact-size path in deterministic provenance.

This is essential for future PixelLab exact-size 24x24/other native outputs.

Required test:

- exact 24x24 RGBA source -> normalized 24x24 uses no resampling and preserves all pixels exactly.

---

# 5. Large-raster -> 24x24 policy for C001

Magnific may provide a large raw raster such as 2048x2048 for a 24x24 target.

C001 must implement a deterministic baseline downsampling policy but must **not** pretend this policy is already owner-qualified for all semantic art.

Required baseline:

- output target dimensions exact 24x24;
- square 1:1 source to square target requires no aspect crop;
- for aspect mismatch, deterministic fit policy must be explicit and versioned, not guessed;
- use one documented resampler selected for pixel-art semantic preservation;
- do not use hidden AI, network, provider resize, or random operations;
- record source dimensions, target dimensions, resampler, crop/pad, alpha/background policy in report and normalized digest;
- repeated normalization of identical bytes + identical request must be byte-identical.

Important:

The owner accepted the **Magnific-produced 24x24 derivative**, but that does not prove any specific local resampler matches its quality. Therefore C001 may establish the deterministic local baseline, but visual equivalence/quality remains a later qualification question.

Do not claim owner acceptance of the local resampler unless the owner reviews its output later.

---

# 6. Background and transparency policy

Create explicit, versioned behavior.

At minimum support:

- `PRESERVE_ALPHA`
- `OPAQUE_AS_IS`

If source has no alpha, do not fabricate transparency from color similarity in C001.

Background removal/segmentation is a future operation unless a deterministic explicit mask exists.

No heuristic flood-fill/background deletion in C001.

---

# 7. ASSET_ART palette policy boundary

C001 must define a palette-policy interface/identifier without forcing a final asset palette decision.

At minimum include:

- `PRESERVE_SOURCE_RGBA` for ASSET_ART baseline;
- future-compatible place for `SCRUBBOTS_C01_C16` but do **not** silently enable it for ASSET_ART;
- normalized artifact records the selected palette policy.

For the first 24x24 ASSET_ART baseline, use `PRESERVE_SOURCE_RGBA`.

Do not apply LEVEL_ART color-band rules to ASSET_ART.

---

# 8. SemanticNormalizedArtifact

Must include at minimum:

- schema/version;
- source raw artifact digest;
- normalization request digest;
- output class;
- target width/height;
- canonical RGBA pixel bytes or equivalent immutable pixel representation;
- normalized pixel SHA-256;
- deterministic artifact digest;
- normalization report digest;
- palette policy;
- explicit provenance back to raw candidate/request/provider.

It must not contain provider secrets or private signed URLs.

It must not masquerade as M08 LEVEL_ART unless all later LEVEL_ART canonical constraints are satisfied.

For `ASSET_ART`, a separate explicit export/read path may exist, but do not wire production asset export yet.

---

# 9. SemanticNormalizationReport

Record deterministic facts, not mutable UI prose, including:

- policy/schema version;
- raw dimensions;
- target dimensions;
- exact-size fast path yes/no;
- resize applied yes/no;
- resampler identifier;
- crop/pad operation and parameters;
- alpha/background policy;
- palette policy;
- input/output hashes;
- warnings/status as typed/versioned values.

Keep free-text diagnostics out of deterministic identity where wording may change.

---

# 10. Real smoke artifact boundary

The accepted live Magnific smoke evidence is:

`review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`

Do not invent or reconstruct the private Magnific image from metadata.

If the live raw/24x24 PNG is not available as an actual local file in the Codex worktree, do not fabricate it and do not call Magnific.

Instead:

- build a clear local ingestion command/function that can ingest an owner-supplied file later;
- tests use committed synthetic lossless fixtures;
- document exactly where/how the owner-approved real file will be captured in a later verification step;
- no private Magnific identifiers or signed URLs enter Git history.

If an actual approved local file is already present in the worktree and clearly owner-provided, it may be used only as read-only evidence; do not commit it unless the repository already contains an explicit owner-authorized fixture policy.

---

# 11. CLI / tooling boundary

Add a minimal explicit normalization tooling path only if it fits current CLI architecture.

Acceptable example:

`python -m scrubbots_pixel_factory.cli semantic-normalize ...`

or a focused tool module.

It must:

- accept a local input file;
- require explicit output class and target dimensions;
- default ASSET_ART 24x24 only when explicitly invoked in an ASSET_ART-specific path;
- print/save deterministic manifest/report;
- never perform network calls;
- never invoke Magnific/PixelLab;
- never overwrite the raw source file.

Do not build Studio UI in C001.

---

# 12. Required tests

At minimum add tests proving:

1. successful provider candidate -> immutable raw artifact;
2. raw SHA-256 remains unchanged after normalization;
3. corrupt image rejects cleanly;
4. decoded dimensions must match candidate returned dimensions;
5. exact 24x24 RGBA -> 24x24 is pixel-identical and reports no resize;
6. 2048x2048 synthetic image -> deterministic 24x24 result;
7. repeated normalization -> byte-identical pixels, report and digest;
8. aspect mismatch uses explicit deterministic crop/pad/fit policy;
9. ASSET_ART `PRESERVE_SOURCE_RGBA` does not invoke LEVEL_ART color bands;
10. LEVEL_ART cannot silently bypass future C01..C16 canonicalization requirements;
11. source path is excluded from identity;
12. raw bytes are never overwritten;
13. no provider secret/signed URL enters manifest/report;
14. normalized raw semantic result still cannot silently masquerade as canonical M08 LEVEL_ART;
15. historical SP01/SP02 tests remain green;
16. full repository regression remains green.

---

# 13. Security / offline requirements

- no network in normalization code;
- no provider SDK invocation;
- no browser automation;
- no secret/environment credential read required for normalization;
- no absolute path in deterministic identity;
- bound memory behavior for maximum accepted raw raster;
- malformed image must fail closed;
- decompression-bomb protections must be explicit if Pillow is used;
- never deserialize executable metadata from images.

---

# 14. Scope exclusions

Do NOT:

- change M00-M10 algorithms;
- change LEVEL_ART size/color-band contracts;
- force 24x24 on LEVEL_ART;
- claim 24x24 is the only future ASSET_ART size;
- implement semantic recognizability scoring;
- implement provider qualification;
- call Magnific/PixelLab;
- spend credits;
- scrape provider sites;
- implement reference/style generation;
- implement inpaint/animation/rotation;
- build Studio UI;
- begin M11;
- edit root `TASKS.md`;
- self-audit or mark SP03 accepted.

---

# 15. Builder log

Create BEFORE any scoped source/test/doc edit:

`.hiveai/codex-logs/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_CODEX_LOG.md`

Exact H1:

`# PAG-SP03-C001 — Raw Capture & Deterministic 24x24 Normalization Foundation`

Role line:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- repository/branch;
- starting local HEAD and fetched `origin/main`;
- divergence `0 0`;
- preserved user-owned dirt;
- authority files read from GitHub;
- files/symbols changed;
- dependency changes and rationale;
- every focused test failure/correction;
- focused SP03 results;
- SP01+SP02 regression results;
- full repository regression;
- compile/import/CLI checks;
- network/secret scans;
- exact changed paths;
- implementation commit;
- push result;
- final local HEAD == origin/main and divergence `0 0`.

Builder must not write the independent audit.

---

# 16. Stop rule

After implementation:

1. run required focused tests;
2. run SP01+SP02 regression tests;
3. run full repository regression;
4. run compile/import/CLI/offline/secret checks;
5. complete builder log;
6. commit and push `main`;
7. verify local HEAD == origin/main and divergence `0 0`;
8. STOP for independent ChatGPT audit.

Do not begin SP03-C002, SP04, or later milestones.