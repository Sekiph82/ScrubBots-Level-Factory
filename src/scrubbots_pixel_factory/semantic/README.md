# SP01 semantic contracts

SP01 adds a provider-neutral boundary for semantic image generation. It
defines immutable `SemanticGenerationRequest`, content-identified
`ImageInputDescriptor`, versioned `SemanticCapabilities`, and typed
`SemanticImageCandidate` results.

`LEVEL_ART` remains bound to ScrubBots difficulty dimensions and C01..C16
legality. `ASSET_ART` is separate from `LevelData` and supports explicit
logical assets such as 16x16, 24x24, 32x32, 48x48, 64x64 and rectangles.

Magnific is the owner-selected primary semantic provider for SP02 while
credits are available, but SP01 does not call Magnific, consume credits,
scrape its website or use undocumented private endpoints. PixelLab-like
controls are product/interface inspiration only; PixelLab proprietary
backend code is not copied. Provider-neutral contracts remain mandatory so
Magnific can be replaced later.

SP03 adds a separate deterministic normalization boundary under
`semantic.normalization`. `SemanticRawArtifact` preserves successful provider
bytes and provenance immutably; `SemanticNormalizationRequest` selects a
versioned local policy; and `SemanticNormalizedArtifact` carries canonical
RGBA8 pixels plus a typed report. C001 supports the strict standard-library
PNG profile only (8-bit non-interlaced grayscale, RGB, grayscale-alpha, or
RGBA, with no color-management/palette chunks). JPEG and WebP are rejected
until a future cycle explicitly adds and tests a deterministic decoder.

The baseline uses exact-size preservation or deterministic integer-weighted
box-area resampling with centered letterboxing. `PRESERVE_ALPHA` and
`OPAQUE_AS_IS` are explicit policies, and ASSET_ART uses
`PRESERVE_SOURCE_RGBA`. LEVEL_ART normalization fails closed until the future
C01..C16 palette/quality contract is implemented. Raw bytes are never replaced,
and normalized semantic art cannot masquerade as an M08 logical-artwork bundle.

Existing MASK/RULES/WFC/HYBRID/AUTO engines remain retained downstream/control
infrastructure.
