# PAG-SP04-C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**FAIL**

Severity summary:

- BLOCKER: 0
- MAJOR: 1
- MINOR: 2
- NOTE: 2

C005 achieves the primary live compatibility target for the owner-supplied Magnific PNG shape, preserves raw-byte identity, keeps unknown critical chunks fail-closed, and leaves normalization/provider policy unchanged. However, the generic ancillary relaxation introduces a new PNG structural acceptance hole: ancillary chunks may now split the IDAT run, and `_decode_png_rgba()` silently concatenates the separated IDAT payloads and accepts the malformed structure. C005 therefore does not satisfy the prompt's requirement that only structurally valid ancillary chunks be ignored while the parser remains fail-closed.

A bounded C006 remediation is required. No provider call or credit spend is needed.

## 2. CONTRACT RECOVERY

Authoritative C005 contract recovered from:

- root `TASKS.md`;
- `.hiveai/prompts/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_PROMPT.md`;
- `review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md`;
- accepted SP03 normalization foundation;
- accepted SP04-C004 qualification foundation.

Key C005 obligations:

1. preserve exact immutable raw bytes/SHA;
2. accept structurally valid ancillary chunks generically;
3. reject malformed types and unsupported/unknown critical chunks fail-closed;
4. preserve CRC, truncation, bounded decode and decompression protections;
5. cover live-shaped `caBX` + `fdEC` synthetic regression;
6. preserve deterministic normalized pixels while keeping byte-distinct source provenance distinct;
7. do not change `AREA_AVERAGE_V1`, crop/pad, palette or provider policy;
8. do not spend provider credits;
9. keep root `TASKS.md` untouched by builder;
10. publish truthful terminal repository evidence.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start HEAD/origin/main: `9fcaaf297e0a4972dfc77bedf75244878cc5cffe`.

Implementation commit: `03825dae00e25e34e7928c9ee513e1b7ce14e1ec`.

Current GitHub `main` at audit time: `20102e24d2ae68f686433d123d7c3825283ab321`.

GitHub compare from builder start to current `main` shows exactly three changed paths:

- `.hiveai/codex-logs/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_CODEX_LOG.md`;
- `src/scrubbots_pixel_factory/semantic/normalization/core.py`;
- `tests/unit/test_sp04_c005_ancillary_png.py`.

No root `TASKS.md`, provider bridge, palette, resize policy, benchmark corpus or separate ScrubBots repository change appears in the C005 diff scope.

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Audit result |
|---|---|
| valid live-shaped ancillary chunks no longer blanket-rejected | PASS |
| unknown/unsupported critical chunks fail closed | PASS |
| `caBX` + `fdEC` synthetic regression | PASS |
| ancillary/baseline decode to identical RGBA | PASS |
| raw bytes/SHA remain byte-sensitive and immutable | PASS |
| local raw artifact import accepts ancillary synthetic | PASS |
| normalized RGBA remains deterministic/pixel-equivalent | PASS |
| source provenance remains distinct for byte-distinct sources | PASS |
| CRC/truncation/malformed type fail closed | PASS |
| bounded decompression protections preserved | PASS by scoped diff + builder regression evidence |
| no normalization/provider/palette expansion | PASS |
| no provider call / zero credit spend | PASS by builder evidence and scoped code review |
| root TASKS untouched by builder | PASS |
| builder log created before implementation edits | BUILDER-CLAIMED / not independently timestamp-provable |
| final terminal HEAD == origin/main `0 0` recorded in builder log | PARTIAL / process finding |
| only structurally valid ancillary placement accepted | **FAIL** |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder claims the parser validates ASCII chunk types, reserved-bit semantics and CRCs, ignores valid ancillary chunks, rejects unsupported critical chunks, and preserves all existing decode bounds. Repository diff confirms these changes.

Builder claims 22 focused SP03+C005 tests, 26 SP04 tests, 112 combined SP01-SP04 tests, and 493 full repository tests passed. These are builder-reported results, not independently replayed by ChatGPT in a clean checkout.

The builder's statement that the parser remains fail-closed at the PNG chunk boundary is incomplete: current code does not enforce that all IDAT chunks form one consecutive run once ancillary chunks are permitted.

## 6. FILE / SYMBOL EVIDENCE

`src/scrubbots_pixel_factory/semantic/normalization/core.py`:

- `_png_chunks()` now rejects non-letter chunk type codes;
- third chunk-type byte must remain uppercase, preserving the PNG reserved bit;
- CRC remains verified before classification;
- unsupported critical chunks are rejected based on first-byte criticality;
- generic ancillary chunks are retained but ignored by pixel decode;
- existing first-IHDR / last-IEND / required-IDAT checks remain;
- **no check requires IDAT chunks to be consecutive**.

`_decode_png_rgba()` continues to construct the compressed stream with the equivalent of:

`b"".join(data for kind, data in chunks if kind == b"IDAT")`

Therefore an ancillary chunk inserted between two IDAT chunks is erased structurally and the two IDAT byte sequences are recombined for decompression.

`tests/unit/test_sp04_c005_ancillary_png.py` covers the intended live shape before IDAT and several negative cases, but does not test an ancillary chunk interleaved between split IDAT chunks.

## 7. FOCUSED TEST EVIDENCE

Builder-reported:

- `tests/unit/test_sp04_c005_ancillary_png.py` + SP03 normalization: 22 passed;
- SP04 qualification: 26 passed;
- combined SP01-SP04 focused: 112 passed.

Independent audit probe against the current C005 parsing logic:

- owner-supplied real PNG shape `IHDR -> caBX -> fdEC -> IDAT -> IEND` parses successfully;
- actual local file remains 1024x1024, 265479 bytes, SHA-256 `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
- a synthetic malformed sequence `IHDR -> IDAT(part1) -> caBX -> IDAT(part2) -> IEND` is also accepted and decoded successfully by the current logic.

That second probe exposes F-PAG-SP04-C005-001.

## 8. REGRESSION EVIDENCE

Builder reports full repository `493 passed` in 297.12 seconds and `compileall`, package import, CLI help and diff checks passed.

No source diff touches `AREA_AVERAGE_V1`, crop/pad behavior, palette policy, provider selection or qualification scoring.

The discovered regression is localized to PNG structural validation introduced by making ancillary chunks permissible.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive findings:

- ancillary payloads are not executed or interpreted as URLs/files/network instructions;
- CRC remains mandatory;
- malformed chunk types and invalid reserved-bit codes fail closed;
- unknown critical chunks fail closed;
- existing raw byte limit, raster dimension/pixel limits and bounded zlib code were not modified;
- no provider network call or credential path was added.

Residual safety/integrity concern:

- accepting non-consecutive IDAT runs weakens parser structural strictness and violates the intended fail-closed PNG boundary, even though no direct code-execution vector was identified.

## 10. ARCHITECTURE CONSISTENCY

Provider-neutral architecture remains intact.

Raw artifacts remain immutable evidence; ancillary chunks are ignored only for pixel interpretation and are not stripped from `SemanticRawArtifact.raw_bytes`.

SP03 normalization policy and SP04 qualification architecture remain untouched.

C005 is architecturally aligned except for the IDAT structural-validation gap.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Root `TASKS.md` was not changed by Codex, as required.

Builder log truthfully records pre-existing local dirt and reports no provider spend.

Process finding F-PAG-SP04-C005-002: builder says `.hiveai/CYCLE_INDEX.md` was read as a historical/project record even though the C005 prompt explicitly prohibited reading legacy hidden `.hiveai` tracker/control-plane files to reconstruct current state. It was not used as current authority, so this is MINOR and does not drive the technical verdict.

Process finding F-PAG-SP04-C005-003: the builder log's recorded equality checkpoint is for `85832a57...`, while two later log-only commits (`930180df...` and terminal `20102e24...`) exist on `main`. GitHub proves the terminal commits were pushed, but the builder log does not actually record terminal `20102e24... == origin/main` with divergence `0 0` after all publication commits as requested. MINOR process evidence gap.

## 12. FINAL REPOSITORY STATE

GitHub `main` at audit time:

`20102e24d2ae68f686433d123d7c3825283ab321`

Branch is publicly reachable and contains the C005 implementation plus builder-log publication commits.

No GitHub commit statuses are present for terminal `main`; repository CI evidence remains absent.

## 13. OPEN CROSS-MILESTONE FINDINGS

- Provider metadata reported 2048x2048 while the owner-downloaded artifact is 1024x1024. This mismatch remains visible and unresolved by design; C005 was not authorized to reconcile it.
- Q03/Q04 remain blocked until decoder compatibility is strictly accepted.
- Diagnostic 1024→24 `AREA_AVERAGE_V1` output has 124 RGBA colors; this remains a later owner-review observation, not authorization for resize-policy change.
- PixelLab live qualification remains pending later owner authorization and runtime secret conditions.

## 14. DEFECTS BY SEVERITY

### MAJOR — F-PAG-SP04-C005-001 — Ancillary relaxation permits non-consecutive IDAT runs

**Evidence:** `_png_chunks()` permits generic ancillary chunks anywhere between IHDR and IEND, while `_decode_png_rgba()` concatenates all IDAT payloads regardless of intervening chunks. Independent synthetic probe `IHDR -> IDAT(part1) -> caBX -> IDAT(part2) -> IEND` is accepted and decoded.

**Impact:** PNG requires IDAT chunks to form a consecutive run. C005 therefore accepts a structurally invalid PNG that should fail closed. This directly conflicts with the prompt's requirement to ignore only structurally valid ancillary chunks while preserving strict structural validation.

**Required remediation:** explicitly enforce one contiguous IDAT run. Unknown ancillary chunks may be allowed before the first IDAT or after the final IDAT, but no non-IDAT chunk may appear between IDAT chunks. Add positive consecutive-multi-IDAT and negative interleaved-ancillary regression tests.

### MINOR — F-PAG-SP04-C005-002 — Legacy hidden CYCLE_INDEX read despite prompt prohibition

No technical acceptance impact. Future builder must read only the explicit current authorities.

### MINOR — F-PAG-SP04-C005-003 — Final equality evidence is not terminal

The logged `0 0` checkpoint is at `85832a57...`; terminal GitHub `main` is `20102e24...`. GitHub proves publication, but the exact required final local-vs-origin evidence was not captured after the terminal publication commit.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking future opportunities:

- add CI to independently run SP01-SP04 focused and full tests on pushed commits;
- add a compact PNG structural-state parser rather than accumulating independent post-hoc checks if future PNG support expands;
- retain live provider-shape fixtures as synthetic data rather than committing private downloaded artifacts.

Do not change resize policy during C006.

## 16. UNVERIFIED ITEMS

- Full builder test suite was not independently replayed because the audit container could not resolve `github.com` for a clean clone.
- Builder chronology claim that the log file existed before the first source/test edit cannot be independently proven from Git history because log + implementation first appear in the same implementation commit.
- Exact provider-internal equivalence between Magnific metadata-reported 2048x2048 and owner-downloaded 1024x1024 remains unverified and intentionally out of C005 scope.

## 17. REGRESSION RISK

Overall remediation risk for C006 is LOW if kept narrow.

Required code change is a small chunk-order state invariant around existing `_png_chunks()` output. It should not touch decompression, raster conversion, raw artifact identity, normalization or provider bridges.

Primary regression risks to test:

- valid single IDAT remains accepted;
- valid multiple consecutive IDAT chunks remain accepted;
- valid ancillary chunks before/after the IDAT run remain accepted;
- ancillary/other chunks inside the IDAT run are rejected;
- live `caBX/fdEC` pre-IDAT shape remains accepted;
- unknown critical chunks remain rejected.

## 18. AUDIT CONFIDENCE

**HIGH** for the identified MAJOR finding.

Reason: the exact source condition is visible in the GitHub diff and the malformed split-IDAT/interleaved-ancillary sequence was independently reproduced against the current C005 parsing logic.

**MEDIUM** for full-suite regression status because independent clean-checkout test replay was blocked by audit-environment DNS.

## 19. FINAL VERDICT

**FAIL**

C005 successfully proves that the actual Magnific `caBX/fdEC` shape can be supported without rewriting raw bytes and closes the original blanket-ancillary rejection in substance. It cannot be accepted yet because the implementation also admits structurally invalid non-consecutive IDAT streams.

Only a bounded IDAT-contiguity closure is required. No provider regeneration, provider call, credit spend, normalization-policy change or architecture rewrite is justified.

## 20. REQUIRED REMEDIATION

Open exactly one bounded cycle:

**PAG-SP04-C006 — PNG IDAT Contiguity & Structural Fail-Closed Closure**

C006 must:

1. enforce one contiguous IDAT run;
2. accept one IDAT and multiple consecutive IDAT chunks;
3. reject any ancillary or other chunk inserted between IDAT chunks;
4. preserve live `IHDR -> caBX -> fdEC -> IDAT -> IEND` compatibility;
5. preserve CRC/type/reserved-bit/criticality validation;
6. preserve immutable raw bytes/SHA and provenance;
7. preserve all decompression/raster safety limits;
8. leave `AREA_AVERAGE_V1`, palette/provider/qualification policy untouched;
9. spend zero provider credits;
10. run focused + full regression tests;
11. avoid legacy hidden tracker/control-plane reads;
12. record the true terminal HEAD/origin/main equality after the final publication commit.

After C006 PASS, return immediately to the owner-supplied 1024x1024 artifact for official SP04-Q02 acceptance and Q03/Q04 execution.