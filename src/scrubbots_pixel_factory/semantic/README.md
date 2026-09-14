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

SP03-C002 keeps PNG zlib decoding incrementally bounded to the exact scanline
length plus one sentinel byte. It never performs an unrestricted decompressor
flush and rejects truncation, trailing bytes, missing EOF, and overlength
streams. Normalization reports copy their nested crop/pad facts into an
immutable mapping. A normalized artifact is only created through its checked
raw-artifact constructor, which snapshots and cross-binds the provider/source
provenance, exact normalization request, report policies, dimensions, and
output hash.

The baseline uses exact-size preservation or deterministic integer-weighted
box-area resampling with centered letterboxing. `PRESERVE_ALPHA` and
`OPAQUE_AS_IS` are explicit policies, and ASSET_ART uses
`PRESERVE_SOURCE_RGBA`. LEVEL_ART normalization fails closed until the future
C01..C16 palette/quality contract is implemented. Raw bytes are never replaced,
and normalized semantic art cannot masquerade as an M08 logical-artwork bundle.

Existing MASK/RULES/WFC/HYBRID/AUTO engines remain retained downstream/control
infrastructure.

## SP06 semantic-quality foundation

SP06-C001 adds an offline `semantic.quality` boundary. Structural diagnostics
are deterministic facts computed from the sealed LEVEL_ART logical C-ID grid:
transitions, adjacency density, connected components, singleton components,
per-ID cell counts, and largest-component ratios. They are evidence about grid
structure only; they do not claim to recognize the depicted subject.

Recognizability is therefore an explicit `UNREVIEWED`, `ACCEPT`, or `REJECT`
review disposition bound to the exact assessment and trusted artifact. ACCEPT
and REJECT require reviewer/reason evidence, and an unreviewed assessment never
passes. The gate calls no provider or vision model and does not modify the
accepted SP05 compiler output.
