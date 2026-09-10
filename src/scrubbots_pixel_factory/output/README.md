# M08 output / export contract

The output package preserves immutable logical artwork separately from
generation metadata and M07 quality state. `artwork.json` contains only
versioned logical truth: explicit caller-supplied candidate identity,
difficulty, exact dimensions, the ascending actual-used canonical palette,
row-major cells, and the existing M07 logical-grid hash.

The row-major index is exactly `index = y * width + x`. `artwork.png` is a
strict project-owned 8-bit RGB PNG: one logical cell is one PNG pixel, rows use
filter 0, RGB values come only from canonical C01..C16, and the file contains
no BG01, alpha, palette approximation, interpolation, resampling, grid lines,
timestamps, or text metadata. The standard-library encoder/decoder is limited
to this profile and fails closed on malformed or unsupported input.

An optional preview uses only a validated positive integer nearest-neighbor
replication scale. It is a presentation artifact; the logical JSON/PNG truth
is never changed. `metadata.json` binds candidate identity, dimensions,
palette, grid hash, successful GenerationResult digest/request/RNG provenance,
supplied WFC/HYBRID/AUTO metadata, and the exact M07 quality report. Quality
ACCEPT/REJECT and rejection codes never become artwork truth.

Raw successful MASK/RULES results may be exported directly. Raw successful
WFC, HYBRID, and AUTO results are rejected unless their candidate wrapper is
passed through, or the caller supplies authoritative mode-specific metadata
via `generator_metadata=`. The explicit metadata may be the raw mode mapping
or the canonical `{"namespace": ..., "data": ...}` envelope. The reader
verifies the namespace and reconstructible exemplar, palette, option, stage,
attempt, digest, and seed bindings; it never relabels or silently repairs
rich provenance.
