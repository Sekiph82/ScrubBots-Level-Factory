# LEVEL_ART Difficulty V1 Convergence Decision V01

Status: **OWNER-INSTRUCTION-DERIVED / CANONICAL MIGRATION AUTHORITY**
Date: 2026-09-14

## Purpose

This addendum reconciles the earlier LEVEL_ART semantic normalization decision with the newer owner-locked Difficulty V1 rules in `Sekiph82/Scrubbots`.

It preserves CELL_MAJORITY and C01..C16 palette snap while superseding the old use of class-specific dimension and used-color bands as current player-facing difficulty legality.

## Preserved rules

The canonical LEVEL_ART semantic pipeline remains:

```text
SEMANTIC IMAGE
 -> CELL_MAJORITY
 -> PALETTE SNAP
 -> ONE LOGICAL PIXEL = ONE GAMEPLAY CELL
 -> C01..C16
 -> CURRENT STRUCTURAL / DIFFICULTY / QA EVALUATION
 -> VALIDATION / EXPORT
```

Preserved:

- CELL_MAJORITY deterministic hard-cell reduction;
- no area averaging/interpolation/antialiasing for canonical LEVEL_ART logical cells;
- deterministic tie-breaks/versioned policy;
- immutable raw provider/source bytes and hashes;
- deterministic snap to C01..C16;
- BG01 presentation-only;
- rectangular boards supported;
- one logical cell = one gameplay cell.

## Superseded rules

The following older statements are historical compatibility rules and are no longer current Difficulty V1 identity/legality:

- EASY must be 20..29 per axis;
- MEDIUM must be 30..39;
- HARD must be 40..49;
- VERY_HARD must be 50..59;
- EASY must use 3..5 colors;
- MEDIUM must use 6..7;
- HARD must use 8..9;
- VERY_HARD must use 10..12.

Current production-capable board envelope remains 20..59 per dimension with rectangular boards allowed, but class is not inferred from dimensions.

Current general production LEVEL_ART used-color envelope is 3..12 canonical C01..C16 colors unless a newer audited content-family rule narrows it.

## Color-budget behavior

The compiler may enforce the global current 3..12 production envelope, but it must not mutate artwork solely to hit a difficulty-class color count.

Rules:

- 3..12 used colors: legal for the color-envelope stage, subject to later semantic/QA/difficulty evaluation.
- >12 used colors after snap: deterministic semantic-preserving reduction may be used only under an explicit versioned policy with provenance and tests, or the candidate may be rejected.
- <3 used colors: reject or route to an explicit remediation/generation policy; do not inject arbitrary accent cells merely to fabricate compliance.
- color count/distribution feeds Difficulty V1 Color Complexity; it is not class identity.

## Dimension behavior

The semantic compiler validates dimensions against the current engine/content envelope and requested generation contract, not a difficulty-class dimension band.

Board size contributes to workload/session-load evaluation.

## Difficulty evaluation boundary

The semantic hard-cell compiler does not need to decide final EASY/MEDIUM/HARD/VERY_HARD class from pixels alone.

Final production candidate acceptance is evaluator-guided and ultimately considers:

- Challenge Score;
- Session Load;
- Frustration Risk;
- visual/readability quality;
- solver evidence when available;
- campaign target/cadence.

## Legacy implementation migration

Existing `contracts/difficulty.py` and `contracts/color_usage.py` may retain historical compatibility helpers until a bounded migration replaces them. New code must not create additional duplicate class-band truth.

Where the old SP05 prompt conflicts with this decision, this decision wins.

## Audit rule

A hard-cell compiler can receive canonical migration credit for CELL_MAJORITY, palette snap, provenance and global-envelope correctness even if historical compatibility helpers remain elsewhere, provided the new compiler does not enforce stale class bands as current production truth.
