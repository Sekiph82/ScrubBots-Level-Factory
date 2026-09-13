# SP04 Q01/Q02 — Magnific Live Raw Compatibility Evidence — 2026-09-14

Document role: CHATGPT / OWNER LIVE QUALIFICATION EVIDENCE

Repository: `Sekiph82/ScrubBots-Level-Factory`

## Scope

This record captures the first byte-level local examination of the owner-supplied PNG associated with the already accepted Magnific wizard smoke. No new provider generation was performed and no additional provider credits were spent.

Private Magnific creation identifiers, signed CDN URLs and account-specific links are intentionally omitted from this public repository record.

## Source facts

Magnific creation metadata previously reported the smoke output as 2048x2048. The actual owner-downloaded/uploaded PNG examined locally on 2026-09-14 is:

- media type: `image/png`
- actual dimensions: **1024x1024**
- byte length: **265479**
- SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`
- PNG bit depth: `8`
- PNG color type: `2` / RGB
- compression method: `0`
- filter method: `0`
- interlace method: `0`

The metadata-vs-file dimension mismatch is therefore a live provider/download-path fact that must not be hidden. For local decode and byte identity, the actual supplied file bytes are authoritative. Exact equivalence to the provider's internal original 2048x2048 raster remains unproven.

## PNG chunk fingerprint

All observed chunk CRCs are valid.

| Order | Chunk | Length | Classification |
|---:|---|---:|---|
| 1 | `IHDR` | 13 | critical |
| 2 | `caBX` | 13234 | ancillary/private |
| 3 | `fdEC` | 5 | ancillary/private |
| 4 | `IDAT` | 252159 | critical |
| 5 | `IEND` | 0 | critical |

Both `caBX` and `fdEC` are ancillary chunks because their first chunk-type character is lowercase. They are not pixel payload required for PNG decoding.

## Q01 disposition

**PARTIAL PASS / LOCAL ARTIFACT CAPTURED**

The exact bytes supplied by the owner are locally captured and immutably fingerprinted by SHA-256. However, because Magnific metadata says 2048x2048 while the actual supplied file is 1024x1024, this evidence does **not** claim byte-for-byte equivalence with Magnific's internal original raster.

## Q02 disposition

**FAIL — CURRENT SP03 STRICT DECODER IS NOT LIVE-MAGNIFIC-COMPATIBLE**

Current `src/scrubbots_pixel_factory/semantic/normalization/core.py::_png_chunks()` rejects any PNG chunk outside `{IHDR, IDAT, IEND}` with:

`PNG contains an unsupported ancillary or palette chunk`

Therefore the real owner-supplied Magnific PNG fails the accepted SP03 local import/decode boundary solely because it contains valid ancillary/private chunks `caBX` and `fdEC`.

This is an evidence-driven compatibility finding. Do not preprocess or strip the source file merely to manufacture a PASS. Raw bytes and raw SHA-256 must remain immutable.

## Diagnostic-only 24x24 normalization observation

For visual diagnosis only, the decoded RGB pixels were fed through the same integer `AREA_AVERAGE_V1` mathematics used by SP03 for a square 1024→24 resize. This is **not** an accepted SP03 pipeline result because Q02 fails before normal normalization can execute.

Diagnostic facts:

- target: 24x24
- crop/pad: none; square source maps to square target
- diagnostic normalized RGBA byte SHA-256: `733503bd8e9a28443010d96e3c3b93668aaa3497526c15d673e1cc9c513a4c5e`
- diagnostic PNG SHA-256: `b7bf0475ed2064a9af1e60c8121f015ae2feb1132403462e8b25a500e281928c`
- distinct RGBA colors: **124**

The high color count comes from area averaging at hard source boundaries. The wizard remains recognizable, but this introduces blended edge tones. No normalization-policy change is authorized by this record alone; official Q03/Q04 owner review must occur after live import compatibility is restored.

## Required remediation

Open one bounded compatibility cycle only:

**PAG-SP04-C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import**

Required behavior:

1. keep raw provider bytes and raw SHA-256 unchanged;
2. continue validating PNG signature, chunk lengths and CRCs;
3. accept/ignore structurally valid ancillary chunks for decoding rather than blanket-rejecting them;
4. continue rejecting unsupported/unknown critical chunks fail-closed;
5. preserve bounded decompression, pixel-budget and non-interlaced/8-bit safety controls;
6. add a fixture reproducing `IHDR -> caBX -> fdEC -> IDAT -> IEND` without embedding the private live artifact itself;
7. prove the same pixel payload decodes identically with and without safe ancillary chunks;
8. do not alter resize/palette/provider qualification policy in this remediation cycle.

## Gate state after this evidence

- SP04-Q01: **PARTIAL PASS / LOCAL BYTES CAPTURED; exact provider-original equivalence unresolved**
- SP04-Q02: **FAIL / REMEDIATION REQUIRED**
- SP04-Q03: **BLOCKED** pending C005
- SP04-Q04: **BLOCKED** pending accepted official Q03 output
- PixelLab live qualification: unchanged / pending later authorization
- additional provider credit spend: **0**
