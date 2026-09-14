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

SP06-C002 adds deterministic durable quality evidence. Export is available
only from an intact C001 assessment. Reload validates the exact trusted
LEVEL_ART artifact and recomputes structural diagnostics instead of trusting
serialized claims, then reconstructs and cross-checks the review and all
canonical identities. Only an explicit `ACCEPT` passes the narrow acceptance
gate; `UNREVIEWED` and `REJECT` do not. This is an auditable evidence gate, not
computer vision or an inference of recognizability, and it calls no provider or
vision model.
## SP07-C001 reference/style generation planning

SP07-C001 adds an offline, provider-neutral planning boundary under
`semantic.generation`. A plan is bound to the exact canonical
`SemanticGenerationRequest`, preserves role-correct REFERENCE, STYLE, INIT and
COLOR_REFERENCE descriptors by content identity, and derives deterministic
candidate variants from the project RNG. Local filesystem paths are excluded
by the existing descriptor identity contract. The plan is execution intent,
not generated imagery; C001 calls no provider and performs no image
generation. Later provider execution requires its own explicitly authorized
and audited cycle. SP05 compilation and SP06 quality/evidence gates remain
downstream and unchanged.
