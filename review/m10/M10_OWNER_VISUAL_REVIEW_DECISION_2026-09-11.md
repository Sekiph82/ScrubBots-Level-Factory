# M10 Owner Visual Review Decision — 2026-09-11

Document role: OWNER VISUAL ACCEPTANCE RECORD

## Decision

**REJECT — ALL 100 CANDIDATES**

The owner manually reviewed the deterministic M10 V1 review pack and rejects all 100 candidates.

- EASY: 25 / 25 rejected
- MEDIUM: 25 / 25 rejected
- HARD: 25 / 25 rejected
- VERY_HARD: 25 / 25 rejected
- Total: **100 / 100 rejected**
- Owner acceptance count: **0 / 100**

## Owner reason

The images are structurally valid procedural pixel patterns, but they do not meet the product requirement for recognizable semantic pixel art. In the owner's judgment, the pack does not provide reliably identifiable objects, characters, events or scenes when viewed without relying on metadata labels.

The product requirement is now explicitly clarified as:

> The generation system must be capable of producing recognizable semantic pixel art comparable in readability to low-resolution PixelLab examples, including clearly identifiable characters and objects even at very small logical resolutions.

Examples shown by the owner include recognizable wizard, dwarf and elf character sprites, including a very small wizard example demonstrating that low logical resolution itself is not a sufficient explanation for the rejected pack.

## Technical interpretation

This owner rejection does **not** invalidate the accepted deterministic infrastructure built in M00–M10:

- canonical ScrubBots palette/dimension contracts,
- deterministic request/RNG/provenance,
- MASK/RULES/WFC/HYBRID structural generators,
- quality/diversity metrics,
- exact PNG/JSON export,
- reproduce/batch orchestration,
- performance/property evidence.

It invalidates the previous product assumption that procedural geometry alone is sufficient as the primary semantic-art source.

MASK/RULES/WFC/HYBRID are therefore retained and repurposed as structural, post-processing, augmentation, topology, palette and exemplar-detail engines around a new semantic pixel-art generation layer.

## Gate disposition

- `PAG-1033` Owner manually reviews the 100-candidate pack: **EXECUTED**
- `PAG-1034` Record approved/rejected/tuning result: **100 REJECTED / SEMANTIC PIVOT REQUIRED**
- `PAG-1050` Owner accepts visual V1 pack: **FAIL / NOT ACCEPTED**
- M11 legacy handoff gate: **BLOCKED / SUPERSEDED BEFORE START**

The next authorized work is the Semantic Pixel Studio conversion plan documented in:

`docs/PAG_V2_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN.md`

No rejected M10 candidate may be promoted as owner-approved production artwork.