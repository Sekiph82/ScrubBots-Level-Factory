# SB-LFX-018-C001 — Simple Owner UI — Audit Criteria

## PASS rule

PASS only if Factory Studio becomes a simple owner production application without deleting or weakening canonical backend capabilities.

## A. Primary navigation

Require exactly these owner-facing primary destinations:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

No Import Validation, Pipeline, Candidates, Comparison, Presets, Search, Readiness, Reproduce, Revisions, Failures, Batch Import, Session Recovery, Similarity, Cost Center, Release, QA, Providers or Outputs as separate primary navigation items.

Underlying routes may remain for compatibility but must be contextual/advanced only.

## B. Page responsibilities

Verify the contract in `docs/product/FACTORY_STUDIO_SIMPLE_OWNER_UI_V01.md`.

Each page must have one dominant user job and one dominant action appropriate to current state.

HOME must support the 40-art batch summary/continue pattern when data exists.

CREATE must support single and multi-PNG entry.

BATCH must show per-item progress/retry/recovery without separate failure/recovery pages.

SOLVE must present artwork + supply + solver + Difficulty V1 together.

REVIEW must expose large preview, compact readiness and explicit ACCEPT/REJECT.

LIBRARY must include search/discovery and selected-item history/details.

PUBLISH must expose accepted levels/order/preflight/STAGING/separate production approval.

SETTINGS must absorb provider/cost/advanced/diagnostic surfaces.

## C. Text density and technical-detail containment

Require:

- no default page dominated by contract paragraphs;
- no repeated wall of `NOT AVAILABLE` statuses;
- compact human state + next action by default;
- canonical hashes/provenance/authority/lineage/reason matrices remain accessible under `Technical details`, `Advanced`, Diagnostics or item history;
- technical truth is not deleted.

## D. Visual hierarchy

Require:

- previews/thumbnails/cards use available desktop space;
- owner runtime no longer looks like top-left text over a mostly empty canvas;
- primary actions visually distinct;
- readable desktop-scale text;
- compact system status replaces the long permanent canonical-core footer;
- owner Desktop launch window title is exactly `ScrubBots Factory Studio`, with no `(DEBUG)`.

## E. Capability preservation

Regression proof must show:

- canonical Factory Core interfaces unchanged unless presentation adapter changes are required;
- import, validation, pipeline, solver, difficulty, QA, review, revision, recovery, similarity, provider accounting and publish capabilities remain reachable through their new contextual locations;
- no owner acceptance or publish gate is inferred/bypassed;
- headless/batch/core workflows remain functional.

## F. Evidence

Require builder screenshots of all eight primary pages from the durable owner runtime at desktop scale.

Require focused navigation/page tests plus safe full repository regression.

Final visual disposition may be `TECHNICAL PASS / OWNER VISUAL REVIEW` until the owner approves the screenshots.
