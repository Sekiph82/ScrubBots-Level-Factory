# Factory Studio Three-Module Owner UI V02

Status: OWNER-APPROVED / SUPERSEDES V01 EIGHT-PAGE NAVIGATION
Date: 2026-10-08
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Approved visual master

The owner approved the following repository image as the **canonical visual master** for the Factory Studio redesign:

`docs/product/visual-masters/FACTORY_STUDIO_THREE_MODULE_MASTER_V01.webp`

This image is the visual authority for layout, proportions, density, spacing, hierarchy, dark theme, panel placement, Visual Review Canvas size, bottom thumbnail strip, right-side details/actions, left-side generation/batch controls, header composition and overall visual character.

**Do not reinterpret it. Do not redesign it. Match it as closely as the Godot runtime permits.**

Important header detail, explicitly owner-locked:

- first module button text is **`1 PIXEL ART`**;
- second is **`LEVEL FACTORY`**;
- third is **`RELEASE POOL`**.

The leading numeral **`1`** before `PIXEL ART` is intentional in this approved master and must be preserved.

Where this written contract and the visual master differ in ordinary composition detail, the visual master wins. Safety, canonical authority and functional truth rules in this contract still win over purely decorative mockup content.


## Owner decision

Factory Studio must behave like the owner's earlier simple Level Factory executable.

The owner does **not** want eight primary pages.

The owner wants exactly **three main production modules**:

1. `PIXEL ART`
2. `LEVEL FACTORY`
3. `RELEASE POOL`

Settings is not a fourth main module. It is a small gear/button opening a secondary settings panel.

No HOME page.

No standalone CREATE, BATCH, SOLVE, REVIEW, LIBRARY or PUBLISH primary pages.

Those capabilities are composed inside the three modules.

## Permanent visual-review rule

The large central artwork-review area shown in the owner-provided Factory Studio screenshot is **mandatory**.

Call it:

`Visual Review Canvas`

This is not a separate navigation page.

It is the main visual workspace used to inspect the currently selected artwork or level.

### Visual Review Canvas requirements

- large central canvas occupying most available application space;
- preserves pixel-art nearest-neighbor rendering;
- background follows current game/VOID preview contract;
- centered selected artwork/level;
- supports single and batch workflows;
- when a batch item is selected, the canvas immediately shows that item;
- should not be buried under technical text;
- no engineering logs inside the canvas;
- concise status/action strip around the canvas is allowed;
- technical details remain collapsed/secondary.

The canvas must appear at minimum in:
- PIXEL ART;
- LEVEL FACTORY.

RELEASE POOL must also provide a selected-level visual preview, using the same component or a size-appropriate instance of it.

## Main navigation

Top-level navigation is exactly:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

A small Settings gear may sit in the header.

Do not expose backend architecture as primary navigation.

---

# Module 1 — PIXEL ART

Purpose:

**Create artwork, one-by-one or in CSV/batch mode.**

The owner should not need to think about solver, supply, release, provenance or canonical records here.

## Modes

### Single

Owner can:

- enter/select the artwork request;
- choose/import the source/provider inputs supported by the current system;
- generate one pixel artwork;
- inspect it in the large Visual Review Canvas;
- regenerate/retry if needed;
- accept the artwork into the Level Factory workflow.

### Batch / CSV

Owner can:

- choose/import CSV batch input;
- start generation for multiple artworks;
- see progress;
- see thumbnail/card results;
- select any item to inspect it in the Visual Review Canvas;
- retry failed items;
- accept selected/all valid artwork into LEVEL FACTORY.

## Default UI

Keep visible:

- Single / Batch toggle;
- prompt/source/CSV controls;
- generation progress;
- thumbnail strip/grid for batch;
- Visual Review Canvas;
- concise state;
- Generate / Regenerate / Retry;
- Send to Level Factory.

Technical provider details belong in Settings/Advanced.

---

# Module 2 — LEVEL FACTORY

Purpose:

**Turn one artwork or a batch into playable levels.**

This module combines the current supply, solve, difficulty, review and level-number work.

No separate SOLVE or REVIEW page.

## Single mode

For the selected artwork show:

- Visual Review Canvas;
- artwork identity;
- transparent/VOID-aware preview;
- supply columns: 3 / 4 / 5;
- Run Supply;
- Run Solver / Re-solve;
- replay result;
- official Difficulty V1;
- readiness;
- Level Number;
- Accept / Reject;
- Send READY level to Release Pool.

## Batch / CSV mode

Owner can process many artworks from a CSV/batch.

Use a compact table/list such as:

| Artwork | Level | Columns | Solver | Difficulty | Status |
|---|---:|---:|---|---|---|
| Owl | 11 | 3 | SOLVED | Easy 34 | READY |
| Fox | 12 | 4 | SOLVED | Medium 48 | READY |
| Fish | 13 | 5 | FAILED | - | RETRY |

Owner can:

- assign/adjust level numbers;
- set supply columns individually or in batch;
- Run Selected;
- Run All;
- Retry failures;
- select any row and inspect it in the Visual Review Canvas;
- Accept/Reject;
- Send READY levels to Release Pool.

## Canonical boundaries

Existing current-game loader/validator/supply/solver/replay/Difficulty V1 remain authoritative.

No local fake solver/difficulty/readiness state.

Review Accept/Reject delegates to canonical owner-review authority.

---

# Module 3 — RELEASE POOL

Purpose:

**Hold fully prepared levels and publish them when the owner says Upload/Publish.**

Only READY / accepted levels belong here.

## Required view

Show a compact visual list/grid/table containing:

- thumbnail;
- level number;
- identity/name;
- Difficulty V1;
- supply columns;
- READY state;
- publish/order state.

Selecting a level shows a visual preview.

## Owner actions

Primary flow:

1. review pool/order;
2. PRECHECK;
3. UPLOAD / PUBLISH.

The application may perform the internal safe pipeline:

`Release Pool -> pack -> STAGING -> verification -> exact production approval -> Production/R2`

but the normal owner UI should not expose a dozen backend pages.

## Safety

The UI must still preserve the real underlying publication gates.

If production cannot proceed because credentials, STAGING receipt, approval identity or another required gate is missing:

- fail closed;
- show one concise blocker;
- do not fabricate completion.

Production approval remains explicit in trusted logic, even if the owner-facing flow is intentionally simple.

Technical release details belong under Advanced/Details.

---

# Settings

Small header gear, not a main module.

Contains:

- provider configuration/status;
- generation model/provider settings;
- paths/runtime;
- R2/publisher environment status;
- cost/credit information when available;
- diagnostics;
- recovery;
- advanced technical details.

Unknown values remain unknown.

---

# Removed primary navigation

The following must not be primary owner navigation:

- HOME
- CREATE
- BATCH
- SOLVE
- REVIEW
- LIBRARY
- PUBLISH
- Import Validation
- Pipeline
- Candidates
- Comparison
- Similarity
- Readiness
- QA
- Revisions
- Failures
- Session Recovery
- Providers
- Cost Center
- Outputs

Their capabilities remain contextual inside the three modules or Settings/Advanced.

---

# Owner workflow

Normal end-to-end workflow:

`PIXEL ART -> LEVEL FACTORY -> RELEASE POOL -> PUBLISH`

Example batch workflow:

`CSV -> 40 artworks -> visual review -> supply/solve/difficulty/level number -> READY -> Release Pool -> Upload`

No other primary navigation is required.

---

# Visual density

The owner UI must resemble the simplicity of the previously supplied EXE:

- very few main pages;
- visual workspace first;
- concise labels;
- few large actions;
- no walls of explanatory text;
- no repeated canonical/provenance/authority prose;
- no giant matrix of NOT AVAILABLE values;
- technical detail collapsed by default.

The backend can remain complex.

The owner cockpit must remain simple.
