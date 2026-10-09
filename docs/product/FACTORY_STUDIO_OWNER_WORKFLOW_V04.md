# Factory Studio Owner Workflow V04

Status: OWNER-LOCKED / CURRENT FUNCTIONAL AUTHORITY
Date: 2026-10-09

Visual authority remains the three approved masters in:
`docs/product/visual-masters/FACTORY_STUDIO_VISUAL_MASTER_INDEX_V01.md`

Functional authority:
- `docs/decisions/OWNER_PIXEL_ART_ALPIX_READY_AUTO_POOL_V01.md`
- `docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`
- `docs/product/FACTORY_STUDIO_LEGACY_EXE_PIXEL_ART_BEHAVIOR_V01.md`

## Three-screen production flow

### 1. PIXEL ART

Sources:
- ALPIX (Claude)
- MAGNIFIC
- PIXELLAB
- external PNG import

Single:
owner prompt + size + provider -> one PNG.

ALPIX CSV:
owner-selected CSV -> sequential Claude+Alpix rows -> persistent resumable job -> PNG collection.

Usage limit pauses without losing completed rows; Resume continues.

### 2. LEVEL FACTORY

Input can be generated or external PNG(s).

Each PNG gets one immutable matched level bundle.

Batch uses the same canonical solver/difficulty pipeline as single.

Only true READY items proceed.

READY items automatically enter Release Pool.

### 3. RELEASE POOL

Contains READY non-excluded levels.

Owner can inspect real PNG/level details, select a batch and Publish.

Publish is the human approval gate.

No content reaches players merely because it became READY.

## Numbering

Successful READY order is deterministic.

Failed/unsolved items consume no final production level number.

Canonical campaign/release planning resolves contiguous final level numbers against current game history.

## Visual rule

Do not change the three master compositions for this functional change.

Use existing master-defined regions/controls.

Where pause/resume state is needed, reuse the existing batch primary action location and change its runtime state/text rather than adding a new production panel.
