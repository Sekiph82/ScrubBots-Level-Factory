# PAG-M08-C001 — Output / Export Contract
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. Verdict

FAIL

PAG-M08-C001 establishes a substantial deterministic output/export layer, but the milestone cannot close yet. Two MAJOR contract/evidence gaps and one MINOR strict-PNG gap remain.

## 2. Scope audited

Audited PAG-0801 through PAG-0830 against the authoritative C001 prompt, with emphasis on:

- immutable logical artwork JSON;
- generation/provenance/quality metadata binding;
- exact logical-resolution PNG;
- strict project-profile PNG decoding;
- preview-only integer replication;
- cross-file integrity;
- deterministic filesystem bundle semantics;
- golden/rectangular/59x59/cross-process evidence;
- preservation of M00-M07 and M09+ isolation.

## 3. Authority baseline

Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`

Branch: `main`

ChatGPT-authorized C001 base: `8790113f55c4b43bfd4939dd3c37c4959f5fbd64`

Terminal builder-era HEAD independently observed: `88be1da62da458f63a987ad477ca676b6074118b`

## 4. Builder boundary

Independent compare reports exactly three commits ahead and zero behind from the authorized base.

The diff is limited to the matching builder log, the new `output/` package, package exports, M08 unit/integration/golden tests, and the committed M08 golden JSON/PNG pair.

No M09+ implementation, generator production rewrite, ChatGPT-owned tracker/audit state, dependency file, or sibling ScrubBots repository change is present.

## 5. Builder-log integrity

The builder log uses the required exact H1 and `Document role: CODEX BUILDER LOG`.

It records the synchronized starting HEAD, pre-existing local control-plane changes, implementation chronology, initial failures/corrections, focused/full test counts, publication commits, and local/origin equality checkpoints.

## 6. Core artwork JSON contract

PASS, except for the rectangular evidence issue recorded separately below.

`ArtworkArtifact` is versioned, fail-closed, uses explicit candidate identity, canonical difficulty/dimensions, actual ascending used palette, row-major cells, the M07 logical-grid hash, deterministic canonical JSON, and deliberately excludes quality state from immutable artwork truth.

## 7. Exact logical PNG encoder

PASS.

The logical encoder writes exact 8-bit RGB truecolor, no alpha/interlace/palette approximation, one source cell per PNG pixel, filter-0 rows, canonical C01..C16 RGB only, deterministic zlib construction, and no resize/interpolation step.

## 8. Preview contract

PASS.

Preview scaling is positive-integer replication only. Logical artwork bytes and dimensions are not modified.

## 9. Cross-file artwork/quality binding

PASS for the implemented artwork/result/quality fields.

The reader cross-checks artwork candidate identity, dimensions, palette, grid hash, GenerationResult logical grid/dimensions/digest, request, typed seed, generator identity, RNG/provenance, deterministic quality policy/report, decision/rejection codes, logical PNG cells, and preview replication.

## 10. F-PAG-M08-C001-001 — MAJOR — Generator-specific provenance can be silently lost or semantically tampered

OPEN.

The authoritative prompt requires source/exemplar and WFC/HYBRID/AUTO router/stage metadata to be preserved when relevant, and explicitly says metadata exposed outside `GenerationResult` must be passed into M08 rather than silently discarded.

Current behavior has two related defects:

1. `_candidate_payload()` returns an empty metadata payload whenever the input object is a raw `GenerationResult`. The public `export_result()` API therefore accepts any successful result, including WFC/HYBRID/AUTO results whose richer metadata lives only on candidate wrappers. Existing WFC and router `generate()` APIs intentionally return only `GenerationResult`. A caller can therefore export a successful WFC/HYBRID/AUTO result and receive `generator_metadata.present=false`, silently losing exemplar/stage/router provenance.
2. On read, `_validate_metadata()` validates only the generator-metadata wrapper schema/version/present/payload shape. It does not semantically bind the payload back to the GenerationResult/request/artwork. For example, a WFC payload's `exemplar_id`, target palette, output dimensions, request-derived config, or analogous HYBRID/AUTO fields can be altered while remaining a mapping and the bundle reader has no generator-specific rejection gate for that contradiction.

Required remediation:

- fail closed when a metadata-bearing mode is exported without its required external metadata, or add an explicit generator-metadata argument/API so the data cannot be silently dropped;
- preserve simple MASK/RULES raw-result export where no external candidate metadata is required;
- validate namespace/mode and deterministic cross-bindings for WFC/HYBRID/AUTO metadata against the request/result/artwork wherever the authoritative fields are reconstructible;
- add negative tests showing missing rich metadata and semantically tampered rich metadata are rejected.

## 11. Representative provenance integration

PARTIAL / FAIL because of F-PAG-M08-C001-001.

The integration suite correctly proves that a `WFCCandidate` wrapper exports WFC metadata and exemplar ID. The generic representative loop also exercises MASK/RULES/HYBRID/AUTO/WFC successful outputs. However, it does not prove that HYBRID/AUTO rich payloads are themselves cross-bound on read, nor that raw-result export cannot silently omit metadata for modes where the prompt requires it.

## 12. F-PAG-M08-C001-002 — MAJOR — Required rectangular row-major and committed golden evidence is incomplete

OPEN.

The C001 prompt explicitly requires the canonical row-major rule to be directly tested on a rectangular grid and requires committed M08 golden JSON/PNG evidence to include at least one rectangular case.

The unit test named `test_artwork_json_contract_and_rectangular_row_major_index` creates the public `ArtworkArtifact` as 20x20 and checks indices 0, 19 and 20. That is a square, not a rectangular board. Its unused local six-cell list does not provide contract evidence.

The only committed M08 golden pair is `golden-easy.json` + `golden-easy.png`, and the golden test explicitly asserts `(width, height) == (20, 20)`. The separate 20x27 integration round trip is useful regression coverage but does not satisfy the prompt's committed rectangular golden requirement or the direct rectangular row-major known-answer gate.

Required remediation:

- add a legal rectangular known-answer artwork, for example 20x21 or 20x27, with distinguishable cells across a row boundary;
- directly assert `index = y * width + x` using that rectangular fixture;
- commit and validate at least one rectangular golden JSON/PNG pair, either as an additional pair or by deliberately replacing the square-only golden if all other required golden properties remain covered;
- prove exact canonical bytes, dimensions, raw RGB and PNG->cells round trip for the rectangular golden.

## 13. F-PAG-M08-C001-003 — MINOR — Strict PNG decoder accepts non-empty IEND payload

OPEN.

The project decoder is intentionally a strict decoder for the exact profile emitted by this repository. `_parse_chunks()` requires IEND to be last and unique, but does not require the IEND chunk data to be empty. A non-empty IEND with a correct CRC is malformed PNG and is outside the project's emitted profile, yet the current parser would not reject it on that basis.

Required remediation:

- require `IEND` data length to be zero;
- add a focused negative test constructing a correct-CRC non-empty IEND and prove `PNGContractError`.

## 14. Other PNG corruption gates

PASS for the evidenced C001 scope.

Bad signature/chunk/CRC structure, unsupported profile, decompressed-length/termination mismatch, non-zero scanline filter, noncanonical RGB, logical-dimension bounds and truncated PNG paths are fail-closed in the implementation/tests reviewed.

## 15. Filesystem publication semantics

PASS for the primary C001 requirements.

Candidate directories use deterministic names, byte-identical rewrites are accepted, conflicting content is rejected, writes are staged in a temporary sibling directory before replacement, and final artifact names are deterministic.

NOTE: because this is Windows-first, future hardening may also reject Windows-reserved device names and trailing-dot/trailing-space candidate IDs. This note does not independently determine the current FAIL verdict.

## 16. Determinism and golden evidence

PARTIAL / FAIL only because of F-PAG-M08-C001-002.

The square committed pair is byte-checked both JSON->canonical bytes and JSON->PNG expected bytes. Cross-process/PYTHONHASHSEED stability and repeated bundle equality are present. Rectangular committed golden evidence remains missing.

## 17. Regression/runtime evidence

Builder reports:

- M08 focused: `12 passed, 1 warning`;
- full repository: `284 passed, 1 warning`;
- compileall and diff check pass;
- no new dependency;
- unchanged local pytest/pytest-asyncio environment mismatch from `pip check`.

GitHub has no associated workflow run or combined status evidence for the terminal builder-era HEAD.

An independent clean-clone pytest attempt from the audit environment failed before checkout because outbound DNS could not resolve `github.com`. Runtime test execution is therefore independently UNVERIFIED. This is not itself the reason for FAIL.

## 18. Preservation / scope isolation

PASS.

No M09-M11 implementation was introduced. Existing generator code, M07 quality mathematics, owner-locked palette/dimension rules and runtime dependency set were preserved.

## 19. Finding summary

- `F-PAG-M08-C001-001` — MAJOR — generator-specific provenance can be silently omitted and is not semantically cross-bound on read;
- `F-PAG-M08-C001-002` — MAJOR — rectangular row-major direct evidence and committed rectangular golden pair are missing;
- `F-PAG-M08-C001-003` — MINOR — strict PNG decoder does not reject non-empty IEND data.

No BLOCKER finding.

## 20. Final disposition

PAG-M08-C001 = FAIL.

Do not promote PAG-0801..PAG-0830 to complete yet. M09+ remains blocked.

Authorize a bounded PAG-M08-C002 remediation that preserves the accepted C001 architecture and closes only the three findings above. After C002, rerun focused M08, M01-M07 regressions and full repository tests, then return the matching builder log for independent strict re-audit.
