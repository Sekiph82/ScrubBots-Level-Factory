# PAG-SP03-C001 — Raw Capture & Deterministic 24x24 Normalization Foundation
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**FAIL**

SP03-C001 establishes a useful normalization foundation, but it does not yet satisfy the required security/immutability/provenance contract.

Severity summary:

- BLOCKER: 0
- MAJOR: 3
- MINOR: 1
- NOTE: 2

No provider credits were spent during the builder cycle. SP04/M11 must remain blocked.

## 2. CONTRACT RECOVERY

Audited against:

1. root `TASKS.md` as current status authority;
2. `.hiveai/prompts/PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_PROMPT.md`;
3. `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`;
4. accepted SP01/SP02 semantic/provider contracts;
5. SP02-C003 strict audit;
6. M07/M08/M09 deterministic provenance/export boundaries;
7. current SP03 implementation, tests and CLI.

Required C001 properties include immutable raw capture, deterministic local decode, bounded malformed/decompression behavior, exact-size no-resize path, deterministic large-raster downsample, explicit alpha/background and palette policy, immutable normalized identity, exact raw-to-normalized provenance, and fail-closed LEVEL_ART handling.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start HEAD: `03ea6dd28dc44dad752a1d71e040db4868fe7fc8`.

Implementation commit: `448b88a7562e55d3b8dd32b5eac0b06f8b26c9a7`.

Terminal builder-log commit on GitHub `main`: `d5d8e5265735440083128d5547ec350c53f6c9b8`.

Compare start..terminal is ahead by 2 commits. Changed paths are limited to:

- matching builder log;
- semantic normalization package/exports/docs;
- CLI normalization path;
- SP03 focused tests.

No root tracker edit by Codex, no M00-M10 production algorithm edit, no provider execution, no SP04/M11 implementation.

Scope discipline: **PASS**.

## 4. ACCEPTANCE CRITERIA MATRIX

| Area | Result | Audit assessment |
|---|---|---|
| Raw bytes/hash capture | PASS | successful candidate bytes/hash are retained immutably as `bytes` |
| Exact 24x24 path | PASS | no resize/resample and decoded RGBA pixels are preserved subject to explicit alpha policy |
| 2048 -> 24 deterministic baseline | PASS | deterministic integer area resampling + explicit fit-center letterbox |
| Repeated normalization identity | PARTIAL | normalizer output is deterministic at construction time, but report nested state is mutable after construction |
| Alpha/background policy | PASS | `PRESERVE_ALPHA` and `OPAQUE_AS_IS` explicit |
| ASSET palette boundary | PASS | `PRESERVE_SOURCE_RGBA`, no LEVEL_ART color bands |
| LEVEL_ART final emission | PASS | C001 refuses final LEVEL_ART normalization |
| LEVEL_ART request legality | FAIL | normalization request does not preserve existing difficulty/dimension legality |
| Bounded malformed/decompression behavior | FAIL | zlib output cap is bypassed by unbounded `flush()` |
| Raw -> normalized provenance | PARTIAL/FAIL | source digest exists, but duplicated provider provenance in normalized artifact is not checked against source artifact |
| No raw overwrite | PASS | CLI test preserves source and rejects identical output path |
| No provider/network calls | PASS | normalization implementation is local/offline |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claims 10 focused SP03 tests, 74 SP01-SP03 focused tests and 455 full repository tests passing. The repository tests support those covered cases.

However, the current focused suite does not exercise:

- a compressed PNG whose expansion exceeds the expected scanline budget;
- mutation of `SemanticNormalizationReport.crop_pad` after construction;
- coordinated tampering of normalized provider provenance while retaining the same raw-artifact digest;
- illegal LEVEL_ART normalization dimensions with the future palette-policy identifier supplied.

Therefore green tests do not close the escaped contracts below.

## 6. FILE / SYMBOL EVIDENCE

Primary evidence:

- `src/scrubbots_pixel_factory/semantic/normalization/core.py`
  - `_decode_png_rgba()`
  - `SemanticNormalizationRequest.__post_init__()`
  - `SemanticNormalizationReport.__post_init__()`
  - `SemanticNormalizedArtifact.__post_init__()`
  - `normalize_semantic_artifact()`
- `tests/unit/test_sp03_normalization.py`
- `src/scrubbots_pixel_factory/cli/main.py`

## 7. FOCUSED TEST EVIDENCE

Builder log reports:

- SP03 focused: 10 passed;
- SP01+SP02+SP03 focused: 74 passed;
- full repository: 455 passed;
- compile/import/CLI/offline/credential scans passed.

These are useful regression signals but insufficient for the residual security and immutability cases.

## 8. REGRESSION EVIDENCE

No accepted M00-M10 generator logic or SP01/SP02 provider bridge was modified by the builder.

Independent clean-clone replay was attempted by the auditor but the audit container could not resolve `github.com`, so runtime replay is **UNVERIFIED**, not failed.

No GitHub commit statuses or workflow runs are associated with terminal HEAD.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

**FAIL** because bounded decompression is not actually enforced.

`_decode_png_rgba()` calls:

`decompressor.decompress(compressed, expected_length + 1)`

but then appends:

`decompressor.flush()`

without any output limit. Python zlib can retain a large `unconsumed_tail` after the capped `decompress()` call; unrestricted `flush()` then expands the remainder. A small compressed input can therefore allocate output far beyond the declared scanline/pixel budget before the later length check rejects it.

This violates the explicit C001 decompression-bomb / bounded-memory requirement.

Offline/network isolation otherwise remains correct.

## 10. ARCHITECTURE CONSISTENCY

Overall architecture is sound:

`SemanticImageCandidate -> SemanticRawArtifact -> SemanticNormalizationRequest -> SemanticNormalizedArtifact`.

The exact-size path and raw/normalized lifecycle separation are correct.

Residual architecture defects are bounded and do not require redesign.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder log was created before source edits and remained within scope.

Root `TASKS.md` was not modified by Codex.

Builder documentation truthfully says only a strict PNG subset is supported. Real Magnific raw-byte ingestion remains unverified because the live image bytes were not present in the builder worktree.

## 12. FINAL REPOSITORY STATE

Terminal GitHub `main` for builder work: `d5d8e5265735440083128d5547ec350c53f6c9b8` before this audit publication.

Builder implementation/log publication is complete. C001 acceptance is withheld by this audit.

## 13. OPEN CROSS-MILESTONE FINDINGS

- Real accepted Magnific PNG ingestion remains unverified and should be exercised after decoder safety closure.
- SP04 provider/model qualification remains blocked.
- M11 remains blocked.
- PixelLab live smoke remains optional and separate.

## 14. DEFECTS BY SEVERITY

### MAJOR — F-PAG-SP03-C001-001 — Decompression-bomb memory bound is bypassable through unbounded zlib flush

The decoder limits the first decompression call to `expected_length + 1`, but immediately calls unrestricted `decompressor.flush()` and concatenates the result.

This means malformed or adversarial compressed data can expand vastly beyond the expected raster budget before the final length check executes.

Impact:

- local/provider-supplied image can cause excessive memory consumption or process termination;
- `MAX_DECODE_PIXELS` and `RAW_ARTIFACT_MAX_BYTES` do not by themselves prevent decompression amplification;
- prompt section 13 is not satisfied.

Required closure:

- never perform an unbounded final decompression expansion;
- enforce an exact maximum decompressed byte budget throughout streaming decode;
- reject if more than the expected scanline length exists;
- add a compact high-compression bomb fixture proving bounded rejection without material memory expansion.

### MAJOR — F-PAG-SP03-C001-002 — Normalization report is not deeply immutable and artifact identity can change after construction

`SemanticNormalizationReport` is a frozen dataclass, but `crop_pad` remains the caller-supplied mutable mapping. `__post_init__()` validates it but does not freeze/copy it into an immutable representation.

The normalizer itself supplies a normal `dict`.

A caller can therefore mutate `normalized.report.crop_pad` after construction. Because report digest is calculated dynamically from that mapping and normalized-artifact identity includes `report_digest`, the normalized artifact's deterministic digest can change after construction.

Impact:

- violates immutable deterministic artifact semantics;
- provenance identity is not stable over object lifetime;
- frozen dataclass gives a false immutability guarantee.

Required closure:

- deep-freeze report mappings, e.g. immutable sorted tuple or `MappingProxyType` over a private copied dict with canonical thawing;
- validate only canonical primitive values;
- add a test proving caller-owned source dict mutation and attempted report mapping mutation cannot change report/artifact bytes or digest.

### MAJOR — F-PAG-SP03-C001-003 — Duplicated provider provenance in normalized artifact is not cross-bound to the raw artifact

`SemanticNormalizedArtifact` stores both `source_raw_artifact_digest` and duplicated provider/request fields (`provider_id`, `provider_version`, `workflow_version`, `model_id`, `request_digest`).

Its `__post_init__()` validates those fields syntactically and binds the report/pixel hashes, but it does not prove that the duplicated provider/request fields correspond to the raw artifact identified by `source_raw_artifact_digest`.

A directly constructed/replaced normalized artifact can therefore retain the original source digest/report/pixels while changing provider provenance to another non-empty value and still pass construction.

Impact:

- internally contradictory provenance artifact can be created;
- consumers reading the convenience provider fields can receive false provenance even though the source digest points elsewhere.

Required closure:

- make source provenance non-duplicated/derived where possible, or include an immutable source-provenance snapshot/digest and validate exact correspondence at construction;
- checked constructor should require the actual `SemanticRawArtifact` or a canonical immutable source-provenance value;
- add coordinated tampering tests.

### MINOR — F-PAG-SP03-C001-004 — LEVEL_ART normalization-request legality does not preserve existing difficulty/dimension contract

`SemanticNormalizationRequest.__post_init__()` applies only generic `1..1024` target dimension checks. If caller supplies `output_class=LEVEL_ART` with `palette_policy=SCRUBBOTS_C01_C16`, an otherwise illegal target such as 1x1 can be represented as a valid normalization request.

Final normalization still fails closed in C001, so invalid LevelData does not escape. However prompt section 2 explicitly requires LEVEL_ART request legality to continue using the existing LEVEL_ART dimension contracts.

Required closure:

- add sufficient difficulty/context to validate LEVEL_ART target dimensions through the existing canonical resolver/validator, or refuse constructing LEVEL_ART normalization requests in C001 until that context exists;
- tests must cover illegal and legal per-difficulty dimensions.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

- Real provider PNG compatibility should be tested after safety closure; the current strict decoder intentionally rejects ancillary/color-management chunks.
- Consider premultiplied-alpha aware downsampling in later visual qualification. Current straight-RGBA area averaging is deterministic but may create edge-color fringes on transparent art.
- Keep local 24x24 resampler quality separate from owner acceptance of Magnific's own 24x24 derivative.

## 16. UNVERIFIED ITEMS

- Independent builder test replay: UNVERIFIED due audit-container GitHub DNS failure.
- Real accepted Magnific raw PNG through local decoder: UNVERIFIED.
- Visual owner acceptance of local `AREA_AVERAGE_V1` output: NOT REQUESTED / NOT CLAIMED.
- JPEG/WebP: intentionally unsupported in C001.

## 17. REGRESSION RISK

Current risk if C001 were accepted unchanged: **MEDIUM-HIGH**.

Functional normal normalization is deterministic, but an untrusted compressed PNG can bypass the memory bound, and post-construction report/provenance integrity is not fully immutable/fail-closed.

## 18. AUDIT CONFIDENCE

**HIGH** for static defects. The zlib issue follows directly from the implementation and Python `decompressobj` semantics; report/provenance mutation paths are visible directly in constructors.

**MEDIUM** for runtime regression because clean checkout could not run in the auditor container.

## 19. FINAL VERDICT

**FAIL**

SP03-C001 is a strong foundation but is not acceptance-ready. Do not begin SP04/M11.

Disposition:

- exact 24x24 no-resize foundation: ACCEPTED as implementation direction;
- deterministic 2048->24 local baseline: ACCEPTED as unqualified technical baseline;
- raw/provider lifecycle separation: ACCEPTED;
- security/immutability/provenance closure: C002 REQUIRED;
- SP03 overall: ACTIVE / NOT CLOSED.

## 20. REQUIRED REMEDIATION

Create one bounded cycle:

`PAG-SP03-C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure`

C002 must only:

1. make PNG decompression strictly output-bounded for all stages and add bomb tests;
2. deep-freeze deterministic report state and prove digest stability against mutation;
3. cross-bind normalized provider/request provenance exactly to the source raw artifact;
4. preserve/enforce LEVEL_ART request dimension legality or refuse such requests until sufficient difficulty context exists;
5. preserve all accepted C001 exact-size/downsample/alpha/palette/offline behavior;
6. run focused + SP01/SP02 + full regression and stop for independent audit.
