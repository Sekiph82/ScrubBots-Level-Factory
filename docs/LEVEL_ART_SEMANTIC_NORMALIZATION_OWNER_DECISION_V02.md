# LEVEL_ART Semantic Normalization Owner Decision V02

Status: OWNER-CONTRACT CONVERGENCE / CURRENT AUTHORITY
Date: 2026-09-14

## Purpose

This document reconciles the previously accepted LEVEL_ART hard-cell normalization direction with the newer owner-locked Difficulty V1 decision in `Sekiph82/Scrubbots` and the Content Platform consolidation authority.

It does **not** reopen the owner's visual decision about CELL_MAJORITY.

## Retained owner-locked art decisions

The following remain unchanged:

- semantic/provider image is the source candidate;
- high-resolution LEVEL_ART reduction uses deterministic `CELL_MAJORITY`;
- no averaging, interpolation, antialiasing or blended-cell colors;
- one logical artwork pixel = one logical gameplay cell;
- logical artwork uses canonical C01..C16 only;
- BG01 remains presentation/background-only;
- deterministic provenance is required;
- owner/provider raw source bytes and hashes remain immutable evidence.

## Difficulty V1 convergence

The main-game owner decision `coordination/OWNER_DIFFICULTY_PROGRESSION_DECISION_V01.md` supersedes older rules that made board dimensions or distinct-color count equal to difficulty class identity.

Therefore the canonical production LEVEL_ART compilation workflow is now:

```text
SEMANTIC RAW IMAGE
        ↓
CELL_MAJORITY_V1
        ↓
PALETTE_SNAP_V1
        ↓
ONE LOGICAL PIXEL = ONE GAMEPLAY CELL
        ↓
C01..C16 ONLY
        ↓
PRODUCTION DIMENSION ENVELOPE: each axis 20..59, rectangles legal
        ↓
PRODUCTION USED-COLOR ENVELOPE: 3..12, independent of EASY/MEDIUM/HARD/VERY_HARD
        ↓
IMMUTABLE LOGICAL ART + PROVENANCE
        ↓
DOWNSTREAM Difficulty V1 / Challenge / Session Load / Frustration / solver / QA evaluation
```

## What is superseded from V01

V01's statements that treated these as canonical production LEVEL_ART legality are superseded:

- EASY dimensions 20..29;
- MEDIUM dimensions 30..39;
- HARD dimensions 40..49;
- VERY_HARD dimensions 50..59;
- EASY 3..5 colors;
- MEDIUM 6..7 colors;
- HARD 8..9 colors;
- VERY_HARD 10..12 colors.

Those remain historical/runtime-compatibility evidence where older systems still require them. They are not the current production semantic compiler truth.

Concrete current examples:

- 24x24 VERY_HARD is dimension-legal;
- 38x38 EASY is dimension-legal;
- an EASY candidate may legally use 8 canonical colors;
- a VERY_HARD candidate may legally use 5 canonical colors;
- class/lane identity must not cause the hard-cell compiler to resize the board or reduce/increase the used-color count.

## Current production dimension envelope

For canonical production LEVEL_ART compilation V1:

- width: 20..59 inclusive;
- height: 20..59 inclusive;
- width and height are validated independently;
- rectangles are legal;
- dimensions are not derived from EASY/MEDIUM/HARD/VERY_HARD.

Legacy class-specific validators may remain available for historical reproduction/compatibility, but the new production semantic compiler must not use them.

## Current production color envelope

After C01..C16 palette snap:

- 3..12 distinct used canonical colors are legal for every class/lane;
- if 3..12 are already used, preserve the snapped logical grid unchanged;
- if fewer than 3 are used, fail closed rather than inventing colors;
- if more than 12 are used, deterministic color-envelope reduction may reduce to exactly 12 using an audited fidelity-preserving policy;
- color count/distribution remains an input to Difficulty V1 metrics, not class identity.

The exact weighted subset optimization developed in PAG-SP05-C001 is approved to be retained for the >12 reduction case, provided its trusted provenance/evidence construction is repaired and independently audited.

## Class/lane metadata

EASY/MEDIUM/HARD/VERY_HARD may still exist as requested campaign/difficulty-lane metadata, but it is not a dimension or color-count legality key inside the hard-cell compiler.

If lane metadata is carried by the compiler for provenance, changing lane alone must not change:

- CELL_MAJORITY pixels;
- palette-snapped cells;
- production-envelope reduction;
- final logical cells.

Downstream Difficulty V1 evaluation and CampaignBuilder decide whether the candidate fits a requested lane/level target.

## Trusted compilation evidence

The canonical public producer of a trusted semantic LEVEL_ART artifact must be the canonical compiler itself.

Trusted report/artifact construction must not permit callers to mint fabricated:

- raw SHA/source provenance;
- majority-grid digest;
- palette-snapped digest/used colors;
- retained subset;
- weighted reduction objective;
- final logical-grid digest.

Direct dataclass construction, `dataclasses.replace()`, or an externally callable checked-constructor path must not be able to seal false transformation evidence.

## Scope separation

This decision governs semantic LEVEL_ART art compilation.

It does not itself implement:

- Challenge Score;
- Session Load;
- Frustration Risk;
- solver/gameplay legality;
- M08/LevelData bridge;
- campaign sequencing;
- semantic recognizability scoring;
- provider selection.

Those remain downstream Content Platform tasks.

## Authority chain

Current precedence for this subject:

1. `Sekiph82/Scrubbots/coordination/OWNER_DIFFICULTY_PROGRESSION_DECISION_V01.md`;
2. `coordination/OWNER_CONTENT_PLATFORM_CONSOLIDATION_DECISION_V01.md`;
3. current root `TASKS.md` canonical program rules;
4. this V02 convergence document for LEVEL_ART normalization;
5. V01 only for retained CELL_MAJORITY/palette/provenance decisions not superseded above.
