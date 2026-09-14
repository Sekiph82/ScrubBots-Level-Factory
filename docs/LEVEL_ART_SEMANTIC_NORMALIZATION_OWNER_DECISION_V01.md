# LEVEL_ART Semantic Normalization Owner Decision V01

Status: OWNER-LOCKED
Date: 2026-09-14

## Purpose

This decision removes ambiguity between the previously accepted LEVEL_ART contract and the temporary SP03/SP04 ASSET_ART `AREA_AVERAGE_V1` qualification baseline.

The core LEVEL_ART direction was already owner-approved in `docs/PAG_SEMANTIC_PIXEL_STUDIO_CONVERSION_PLAN_V01.md`: semantic provider output must become a deterministic logical grid, use only C01..C16, preserve one logical artwork pixel as one gameplay cell, and obey difficulty used-color legality.

What had not previously been owner-locked by exact algorithm name was the high-resolution semantic-image to logical-cell reduction step. The owner has now reviewed the live Magnific 1024x1024 -> 24x24 experiments and selected deterministic CELL_MAJORITY.

## Owner-locked LEVEL_ART workflow

```text
SEMANTIC IMAGE
    ↓
CELL_MAJORITY
    ↓
PALETTE SNAP
    ↓
ONE LOGICAL PIXEL = ONE GAMEPLAY CELL
    ↓
C01..C16 ONLY
    ↓
DIFFICULTY USED-COLOR BUDGET
    ↓
STRUCTURAL / SEMANTIC / GAMEPLAY VALIDATION
    ↓
DETERMINISTIC EXPORT
```

This is the canonical LEVEL_ART normalization direction.

## CELL_MAJORITY requirements

For each requested logical output cell:

- determine the exact deterministic source-region footprint corresponding to that target cell;
- count source pixel colors within that footprint using a versioned deterministic color representation;
- select exactly one winning color for the cell;
- use an explicit deterministic tie-break rule;
- emit one flat color for the target cell;
- never average/blend colors;
- never introduce antialiasing or interpolation colors;
- preserve the immutable original provider bytes/hash separately from normalized output.

The implementation must be versioned and reproducible.

## Palette snap

After CELL_MAJORITY, every LEVEL_ART logical cell must be mapped deterministically to the legal ScrubBots logical palette C01..C16.

- No arbitrary provider color may survive into canonical LEVEL_ART.
- BG01 remains presentation/background only and is not a logical artwork color.
- Palette mapping must be deterministic, versioned, provenance-bound and reproducible.

## Difficulty used-color legality

Canonical LEVEL_ART remains:

- EASY: 20-29 cells per axis; 3-5 distinct used C01..C16 colors;
- MEDIUM: 30-39; 6-7 colors;
- HARD: 40-49; 8-9 colors;
- VERY_HARD: 50-59; 10-12 colors;
- rectangular boards allowed.

The difficulty color budget is a hard legality rule for LEVEL_ART.

If palette snap initially yields too many legal colors, deterministic color-budget reduction must reduce to the requested difficulty band without introducing non-C01..C16 colors. If it yields too few, the candidate must not be silently fabricated into compliance; use an explicit deterministic remediation/rejection policy.

## AREA_AVERAGE_V1 disposition

`AREA_AVERAGE_V1` is OWNER REJECTED for LEVEL_ART because it creates blended/intermediate colors and antialiased-looking edges.

It may remain historical/technical evidence for prior ASSET_ART qualification, but it is not an acceptable LEVEL_ART logical-grid reduction policy.

## Live evidence

Owner-reviewed Magnific wizard evidence:

- actual downloaded source: 1024x1024 PNG;
- source SHA-256: `58c667c848323727392ecbd663f1ebaa8f4b19471b1946f9325ab8d419eb63e9`;
- `AREA_AVERAGE_V1` 24x24 result: OWNER REJECTED for blended edge colors;
- nearest-neighbor diagnostic: not selected;
- CELL_MAJORITY diagnostic: OWNER ACCEPTED as the logical-cell reduction direction.

The CELL_MAJORITY diagnostic itself is not yet canonical LEVEL_ART because C01..C16 palette snap and difficulty color-budget enforcement still need implementation and strict audit.

## Scope distinction

This decision is specifically authoritative for LEVEL_ART.

ASSET_ART remains a separate output class and may use different palette and normalization policies when explicitly specified. ASSET_ART policy must never weaken or replace this LEVEL_ART contract.
