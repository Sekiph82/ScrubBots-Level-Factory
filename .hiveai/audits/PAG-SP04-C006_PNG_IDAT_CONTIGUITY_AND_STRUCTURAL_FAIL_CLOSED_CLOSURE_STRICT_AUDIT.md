# PAG-SP04-C006 — PNG IDAT Contiguity & Structural Fail-Closed Closure
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**PASS**

Severity summary:

- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 2

C006 closes the sole technical residual from C005. The PNG decoder now enforces one contiguous IDAT run while preserving the real Magnific-shaped `IHDR -> caBX -> fdEC -> IDAT -> IEND` compatibility, raw-byte identity, CRC/type/critical-chunk protections, bounded decode behavior and unchanged normalization policy.

No C007 remediation cycle is required.

## 2. CONTRACT RECOVERY

Authoritative C006 contract recovered from:

- root `TASKS.md`;
- `.hiveai/prompts/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_PROMPT.md`;
- `.hiveai/audits/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_STRICT_AUDIT.md`;
- `review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md`;
- current SP03 normalization source/tests and SP04 qualification tests.

Required closure was narrow: one contiguous IDAT run, preserved ancillary compatibility, no provider/palette/resize-policy changes and zero provider spend.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start HEAD/origin/main: `862f801091dd32cf236af02d148d344d45b32ed9`.

Implementation commit: `e4a4155e6c022f1647b2010506f46693905c2de9`.

Terminal GitHub `main` at audit time: `6f3500955de2b39ded978cd39fc30fcafed79059`.

GitHub compare from builder start to terminal `main` shows exactly three changed paths:

- `src/scrubbots_pixel_factory/semantic/normalization/core.py`;
- `tests/unit/test_sp04_c006_idat_contiguity.py`;
- matching C006 builder log.

No root `TASKS.md`, provider bridge, palette policy, resize policy, qualification model or separate ScrubBots repository change occurred in builder scope.

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Audit result |
|---|---|
| live-shaped `caBX/fdEC` PNG remains accepted | PASS |
| single IDAT accepted | PASS |
| multiple consecutive IDAT accepted | PASS |
| non-IDAT splitting IDAT run rejected | PASS |
| legal post-IDAT ancillary accepted | PASS |
| critical/type/reserved-bit/CRC protections intact | PASS |
| bounded decode/decompression protections intact | PASS by unchanged scoped code + regression evidence |
| immutable raw bytes/SHA/provenance intact | PASS |
| normalization pixels/policy unchanged | PASS |
| no provider/palette/qualification policy change | PASS |
| zero provider calls/credits | PASS |
| root TASKS untouched by builder | PASS |
| no legacy hidden tracker/control-plane authority reads | PASS by builder log |
| focused/full tests green | PASS by builder evidence |
| terminal publication evidence truthful | PASS with explicit publication limitation |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

Builder reports 28 C006+C005+SP03 tests, 26 SP04 tests, 118 combined SP01-SP04 focused tests and 499 full repository tests passing. Repository diff matches the claimed narrow implementation: explicit IDAT-run state plus focused regression tests.

Builder states no Magnific/PixelLab call or credit spend occurred; changed code contains no provider/network execution path.

## 6. FILE / SYMBOL EVIDENCE

`_png_chunks()` now initializes `idat_started=False` and `idat_run_closed=False`.

- First/consecutive `IDAT` keeps the run open.
- First non-IDAT after IDAT closes the run.
- Any later `IDAT` raises `PNG IDAT chunks must form one contiguous run`.

Existing chunk-type, reserved-bit, CRC, boundary, critical-chunk and required-IDAT validation remains present.

`tests/unit/test_sp04_c006_idat_contiguity.py` covers single/consecutive IDAT, live-shaped pre-IDAT ancillary chunks, legal post-IDAT ancillary data, generic interleaving rejection, critical/type/CRC/reserved-bit failures and provenance/normalized-pixel stability.

## 7. FOCUSED TEST EVIDENCE

Builder-reported:

- C006+C005+SP03: 28 passed;
- SP04 qualification: 26 passed;
- combined SP01-SP04: 118 passed;
- full repository: 499 passed.

Independent ChatGPT probes against current C006 logic:

1. owner-supplied real PNG `IHDR -> caBX -> fdEC -> IDAT -> IEND` is accepted;
2. actual file remains 1024x1024, 265479 bytes, SHA-256 `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
3. a synthetic consecutive two-IDAT stream is accepted;
4. synthetic `IDAT -> caBX -> IDAT` is rejected fail-closed.

## 8. REGRESSION EVIDENCE

No change touches `_area_resize`, `_fit_center`, alpha policy, ASSET_ART palette policy, provider bridges, benchmark corpus or qualification scoring.

Builder reports full repository 499 PASS plus compile/import/CLI/diff checks.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

C005 safety remains intact:

- ancillary payloads are never executed or interpreted as network/filesystem instructions;
- CRC is validated before classification;
- malformed type and invalid reserved-bit semantics fail closed;
- unsupported critical chunks fail closed;
- raw-size/raster/pixel/zlib limits are unchanged;
- IDAT structural strictness is now stronger than C005.

## 10. ARCHITECTURE CONSISTENCY

Provider-neutral architecture and immutable raw-evidence boundary remain intact. C006 is a parser structural invariant only and does not cross into provider selection, semantic generation, normalization policy or LEVEL_ART integration.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder did not edit root `TASKS.md` and explicitly states legacy hidden tracker/control-plane files were not read as authority.

The builder log truthfully explains that embedding a commit's own final SHA inside that same commit is self-referential. It does not manufacture a terminal equality checkpoint. GitHub independently confirms terminal `main` is publicly reachable at `6f3500955de2b39ded978cd39fc30fcafed79059`.

## 12. FINAL REPOSITORY STATE

Terminal GitHub `main` at audit time:

`6f3500955de2b39ded978cd39fc30fcafed79059`

No GitHub commit statuses are present for the terminal commit.

## 13. OPEN CROSS-MILESTONE FINDINGS

- Magnific provider metadata reported 2048x2048 while the owner-downloaded artifact is 1024x1024. This mismatch remains visible evidence and is not silently reconciled.
- PixelLab live qualification remains pending owner-authorized API conditions.
- The accepted `AREA_AVERAGE_V1` 1024→24 result contains 124 RGBA colors; visual suitability remains an owner-review question, not a C006 parser defect.

## 14. DEFECTS BY SEVERITY

No BLOCKER, MAJOR or MINOR defects remain in C006 scope.

NOTE-001: full builder suite was not independently replayed from a clean checkout; independent focused parser/live-file probes were executed instead.

NOTE-002: no CI/status checks exist for terminal `main`.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Future non-blocking improvements:

- add CI for focused/full regression replay;
- if PNG support expands further, consider a small explicit chunk-order state machine for all supported structural ordering rules;
- keep private provider artifacts out of Git and retain only hashes/typed evidence.

## 16. UNVERIFIED ITEMS

- Exact provider-internal relationship between Magnific metadata 2048x2048 and downloaded 1024x1024 bytes remains unverified and outside C006 scope.
- Builder full-suite results remain builder evidence rather than independently replayed CI evidence.

## 17. REGRESSION RISK

LOW. C006 adds eight scoped lines to the chunk parser and a focused test file. No resize, palette, provider or qualification behavior changed.

## 18. AUDIT CONFIDENCE

**HIGH** for C006 technical closure because the exact C005 failure sequence and the real owner-supplied Magnific chunk sequence were independently replayed against the current logic.

## 19. FINAL VERDICT

**PASS**

C006 closes the C005 IDAT-contiguity residual without weakening live ancillary compatibility or accepted safety/provenance boundaries.

## 20. REQUIRED REMEDIATION

None.

Return immediately to SP04 live qualification:

- mark Q02 decoder compatibility PASS for the owner-supplied 1024x1024 artifact;
- run official Q03 local deterministic normalization to 24x24;
- present Q04 metadata-blind owner visual review;
- do not open another Codex decoder cycle unless new evidence requires it.
