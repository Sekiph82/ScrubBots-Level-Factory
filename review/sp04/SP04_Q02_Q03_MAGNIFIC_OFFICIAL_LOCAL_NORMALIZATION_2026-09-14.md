# SP04-Q02/Q03 — Magnific Official Local Decoder + 24x24 Normalization Evidence — 2026-09-14

Document role: LIVE QUALIFICATION EVIDENCE

## Scope

This record captures the first official post-C006 local decode and deterministic 24x24 normalization of the owner-supplied Magnific wizard artifact. The private PNG itself is not committed.

No Magnific or PixelLab generation/API call was made during this evidence run and no provider credits were spent.

## Source artifact

- source: owner-supplied downloaded Magnific wizard PNG associated with the accepted `recraft-v4-1` smoke direction;
- local file dimensions: **1024x1024**;
- byte length: **265479**;
- exact source SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
- decoded profile: 8-bit RGB, non-interlaced;
- chunk sequence: `IHDR -> caBX -> fdEC -> IDAT -> IEND`;
- provider creation metadata had previously reported 2048x2048. That metadata-vs-downloaded-file mismatch remains explicitly unresolved and is not rewritten here.

## Q02 — Decoder compatibility

**PASS**

Post-C006 parser behavior was independently replayed against the exact owner-supplied bytes:

- valid live-shaped ancillary `caBX` and `fdEC` chunks are accepted without stripping or transcoding the raw file;
- all observed chunk CRCs validate;
- exact source SHA remains unchanged;
- synthetic consecutive multi-IDAT remains accepted;
- synthetic `IDAT -> caBX -> IDAT` is rejected fail-closed.

C006 strict audit:
`.hiveai/audits/PAG-SP04-C006_PNG_IDAT_CONTIGUITY_AND_STRUCTURAL_FAIL_CLOSED_CLOSURE_STRICT_AUDIT.md`

## Q03 — Official local deterministic normalization

**PASS**

Policy:

- output class: `ASSET_ART`;
- target: **24x24**;
- alpha policy: `PRESERVE_ALPHA`;
- resize policy: `AREA_AVERAGE_V1`;
- crop/pad policy: `FIT_CENTER_LETTERBOX_V1`;
- palette policy: `PRESERVE_SOURCE_RGBA`;
- source and target are square, so fitted dimensions are 24x24 with offsets 0,0.

Deterministic identity/provenance values reconstructed from the accepted SP03 canonical contracts:

- local input request digest: `434d30d239f3a9054fe6a172c328b4f210bda9428f90ef193c45010cf595af6a`;
- local candidate digest: `ba9e2392f3f0ae1108a82fd25719155e610e534a5c4a717e3fbc9410dc0bbf9b`;
- raw artifact digest: `136334fc4c967c0788667663a90c6999bbd5d21a21e47027e13eba6133b02957`;
- normalization request digest: `de20b17c8e3e1d7264bae9c1fd9101e3367e80e89f7241a68091ed07b9b3fcf5`;
- normalized RGBA SHA-256: `733503bd8e9a28443010d96e3c3b93668aaa3497526c15d673e1cc9c513a4c5e`;
- normalization report digest: `77d17de9c187b92b1e355d090e7922658204508f04449aa61bcc6d30981389af`;
- source provenance digest: `cfae1353f7c25f23a3959c76260bfd65545bdcba95da18d00e661b7a5c3d8e13`;
- normalized artifact digest: `b69312f889f41c7d78495c7e4433f5a186c0e3d30e5fe764b6034289c9430f7f`.

The official 24x24 normalized output contains **124 distinct RGBA colors**. This is deterministic behavior of `AREA_AVERAGE_V1` over the supplied 1024x1024 hard-edged source.

## Q04 — Owner visual review

**PENDING OWNER DISPOSITION**

The 24x24 result has been exported to the conversation for metadata-blind visual inspection, together with a nearest-neighbor enlarged review view. Those exported PNG files are not committed to this public repository.

Decision question:

Does the official local `AREA_AVERAGE_V1` 24x24 wizard preserve the intended crisp/readable Colony-Flow-style pixel-art appearance sufficiently for production, or do the 124 blended RGBA edge tones justify an evidence-driven alternative pixel-art downsampling policy?

No resize-policy change is authorized until owner disposition is recorded.
