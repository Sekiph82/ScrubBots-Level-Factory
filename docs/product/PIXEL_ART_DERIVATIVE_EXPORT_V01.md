# Pixel Art Derivative Export V01

The `scrubbots-pixel asset-export` command creates local, deterministic PNG
rotation variants and an animation strip from an explicitly selected source.
It reads source files only; it never runs the level solver, calls an image
provider, or publishes content.

Example:

```text
scrubbots-pixel asset-export artwork.png --output-dir derived/artwork --direction N --direction E --direction S --direction W --frame walk-00.png --frame walk-01.png --frame-duration-ms 100
```

`--direction` may be repeated with N/NE/E/SE/S/SW/W/NW. The input is assumed
to face north. Cardinal outputs are pixel rotations, mechanically described
in the manifest and not semantically validated facing art. Diagonal directions
require explicit direction PNGs, for example
`--direction NE --direction-file NE=artwork-ne.png`; the exporter never
fabricates a diagonal with interpolation. All direction outputs retain owner
review markers. The input image bytes are hashed into the manifest and never
overwritten. Logical pixel dimensions stay unchanged per frame and no scaling,
resampling, interpolation, or antialiasing is performed. Alpha is retained.

`--frame` may be repeated in playback order. Every frame must have identical
dimensions and the same set of RGBA colors. The command writes individual frame PNGs, a horizontal sprite
sheet, and a deterministic JSON manifest containing source/output hashes,
dimensions, frame order, and duration. It refuses to use an output directory
that already exists, including a directory with owner files. Choose a new,
task-specific output directory; review the generated derivatives before any
art-style or production approval.

This feature supplies local assets and manifests only. It does not decide
copyright or ownership, deem generated art owner-approved, change canonical
level data, or satisfy any game-side animation importer contract.
