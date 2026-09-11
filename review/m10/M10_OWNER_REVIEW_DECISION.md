# M10 V1 Owner Visual Review Decision

Date: 2026-09-11  
Decision: **REJECT**

This decision is bound to every entry in `review/m10/M10_REVIEW_MANIFEST.json` at Git blob `ddc73575977736694977ca3cde3b48252730c4fc`.

## Result

- Reviewed: 100 / 100
- Accepted: 0
- Rejected: 100
- `PAG-1033`: owner review completed
- `PAG-1034`: all current visual families/styles rejected for product acceptance; semantic generation needs transformation
- `PAG-1050`: **REJECTED**
- M11: **BLOCKED**

## Owner acceptance reason

The current review pack does not meet the intended product objective. The images do not reliably communicate a recognizable object, character, creature, scene, or event when viewed without their metadata labels. Passing structural, palette, dimension, determinism, export, and performance checks is not sufficient for owner visual acceptance.

The current MASK/RULES/HYBRID synthesis remains useful as deterministic geometry/control infrastructure, but it is not accepted as the primary visual synthesis engine for the intended PixelLab-like pixel-art generator.

## Clarified product requirement

The Factory must be able to produce **small but clearly recognizable semantic pixel art**, comparable in readability to PixelLab-style outputs. Owner-provided examples prove that recognizable characters are possible even around 16x16 logical-pixel scale.

For SCRUBBOTS level artwork, the existing board contract remains authoritative unless separately changed:

- EASY: 20-29 logical cells per axis
- MEDIUM: 30-39
- HARD: 40-49
- VERY_HARD: 50-59
- rectangular boards allowed
- canonical logical palette C01..C16
- difficulty distinct-used-color bands remain hard legality

The semantic generation stage must therefore create recognizable subject matter **before** the existing SCRUBBOTS normalization, palette, QA, solver, provenance, batch, and export stages are applied.

A second output class may later support standalone game assets such as characters, enemies, items, objects, and animation frames with asset-specific dimensions/palettes. That asset contract must remain separate from LevelData legality.

## Required direction

Do not discard the accepted deterministic infrastructure. Transform the existing project by adding a semantic AI pixel-art generation layer and reusing the current request/RNG, constraints, palette enforcement, quality checks, provenance, PNG/JSON export, batch/reproduce, benchmarking, and review systems around that layer.

Existing MASK/RULES/WFC/HYBRID/AUTO code is retained. Its role changes from being the primary owner-visible art source to supporting geometry, masks, region control, style/detail propagation, puzzle constraints, mutation, fallback, and post-processing around semantic artwork.

## Owner acceptance standard going forward

**Metadata-blind recognizability is mandatory.** When the candidate name/category/description is hidden, a human reviewer must be able to identify the intended subject at a useful confidence level.

Structural-quality `ACCEPT` is not equivalent to semantic-art `ACCEPT`.

No candidate in this 100-image pack may be promoted as owner-approved V1 artwork. The pack is retained as negative evidence and future regression material.
