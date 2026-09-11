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

This layer ends at immutable raw image bytes and provenance. A semantic
candidate cannot masquerade as an M08 logical-artwork bundle; deterministic
normalization belongs to SP03. Existing MASK/RULES/WFC/HYBRID/AUTO engines
remain retained downstream/control infrastructure.
