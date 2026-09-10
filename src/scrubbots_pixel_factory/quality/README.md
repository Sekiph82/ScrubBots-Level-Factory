# M07 quality layer

The M07 analyzer is generator-independent and reads only exact logical board
dimensions plus row-major canonical `C01..C16` cells. It never reads MASK,
RULES, WFC, HYBRID, or private topology metadata.

Because logical cells have no universal empty token, M07 infers structural
negative space with a deterministic heuristic: count canonical colors on the
outer boundary, choose the greatest boundary count, break ties by greatest
whole-grid count, and break any remaining tie by ascending canonical C-ID.
The result includes the counts and rule in the serialized evidence. This is a
structural-analysis heuristic, not gameplay truth or semantic background truth.

All metric and rejection serialization is canonical JSON. Grid identity uses a
framed SHA-256 payload containing schema/version, width, height, and row-major
cells. Near-duplicate analysis compares equal dimensions only; it never resizes
or interpolates grids. Quality decisions and diversity evidence are separate.

## Directional symmetry conventions

`horizontal_symmetry_score` is left-right mirror equivalence: each logical
cell `(x, y)` is compared with `(width - 1 - x, y)`. Geometrically, this is
reflection across the vertical centerline.

`vertical_symmetry_score` is top-bottom mirror equivalence: each logical cell
`(x, y)` is compared with `(x, height - 1 - y)`. Geometrically, this is
reflection across the horizontal centerline.

Both scores are in the inclusive range `0..1`. A score of `1.0` means every
logical cell equals its reflected counterpart under that convention. Scores
use the complete logical grid, including the inferred-negative-space C-ID as
ordinary cell equality. These are structural grid metrics, not
semantic/artistic judgments.
