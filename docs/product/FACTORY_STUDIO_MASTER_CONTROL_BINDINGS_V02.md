# Factory Studio Master Control Bindings V02

Status: OWNER-FUNCTIONAL / CANONICAL UI ACTION CONTRACT
Date: 2026-10-09

Owner decision:
`docs/decisions/OWNER_PIXEL_ART_ALPIX_READY_AUTO_POOL_V01.md`

Legacy EXE behavior:
`docs/product/FACTORY_STUDIO_LEGACY_EXE_PIXEL_ART_BEHAVIOR_V01.md`

V02 supersedes V01 for runtime behavior. The three visual masters remain unchanged.

## Shared

Header remains exactly:

`PIXEL ART | LEVEL FACTORY | RELEASE POOL`

Visual Review Canvas always shows the actually selected/generated/imported PNG or level artwork.

Master owl imagery is a fixture/example only, never a forced production image.

Zoom/grid/1:1/fit/carousel controls are presentation-only and never mutate canonical bytes.

## PIXEL ART

### Provider

**Effective active Pixel Art provider choices, owner override 2026-10-20:**

- `ALPIX (Claude)`
- `PIXELLAB` (real `PRO_FLASH` engine)

`MAGNIFIC` is retired from the visible Provider options and all active Pixel Art Generate/Regenerate/CSV selection paths because the owner's subscription and credits expired. Preserve historical MAGNIFIC artwork/jobs and provenance without mutating the owner's data. This newer decision supersedes the earlier V02 minimum-provider list without changing three-screen layout or other page functionality.

The selected option must control the actual execution path.

### Single

The owner types prompt, chooses size and provider, then Generate creates one PNG.

Do not generate a hidden prompt plan or batch list.

`ALPIX (Claude)`:
- use local Claude Code subscription authentication;
- discover and call installed Alpix plugin/MCP/tool;
- no Anthropic API key / paid API fallback;
- output one PNG at requested size.

`PIXELLAB` (Pro Flash):
- implement the actual official provider invocation, not a label-only change or PIXFLUX fallback;
- use canonical `data/palette/scrubbots_palette_v3.json` for the 16-color output validator;
- do not duplicate provider logic;
- fail closed if the Pro Flash API/token is unavailable;
- preserve existing secret-handling rules.

Historical `MAGNIFIC` is read-only provenance, not a selectable active Pixel Art provider; retired jobs/CSV rows fail closed without paid calls or implicit conversion.

### Batch / CSV

The selected CSV is the batch definition.

Factory Studio reads it; it does not author it.

When Provider = ALPIX:
- use the legacy EXE `ArtJob` / `ArtProducer` semantics;
- CSV SHA-256 identifies the persistent job;
- process rows sequentially;
- persist after every transition;
- valid completed rows are never repeated;
- usage limit -> `LIMIT` and clean stop;
- master-defined primary batch action becomes Resume when resumable;
- Resume continues first incomplete row;
- app restart must retain resumability.

CSV parsing should port legacy `read_rows()` compatibility instead of inventing an incompatible format.

### Artwork collection

Every generated/imported PNG appears in the real artwork collection/thumbnails.

Selecting it updates:
- Visual Review Canvas;
- dimensions;
- palette/color count;
- transparent/VOID counts;
- format;
- immutable identity.

`Add to Level Factory` transfers exact identity, not a re-generated image.

## LEVEL FACTORY

Inputs:
- selected PIXEL ART result;
- one external PNG;
- multi-PNG selection;
- existing external PNG CSV/batch.

All use the same canonical pipeline.

For every source:
PNG -> alpha/VOID validation -> supply -> official solver -> replay -> Difficulty V1 -> load/QA -> immutable artifact bundle.

### Level Number

Default behavior is Auto.

For batch, do not require manual numbering per PNG.

Reuse canonical campaign/release ordering:
- only successful READY items receive publish order;
- failed/unsolved items consume no final level number;
- relative successful order follows input order;
- final publication plan is contiguous against current catalog/history.

Manual single-level number override may remain only where already safely supported.

### Supply columns

3/4/5 must reach the canonical primary supply pipeline.

### Run Pipeline

Must execute canonical:
validation -> supply -> official game solve -> replay -> Difficulty V1 -> QA/load checks.

No shadow solver or scorer.

### Automatic Release Pool

A candidate that reaches canonical READY is automatically included in Release Pool.

No owner ACCEPT is required for pool eligibility.

`Accept Level`:
- idempotently include/restore READY candidate in pool.

`Reject`:
- exclude/quarantine candidate from pool.

Reject must not publish and must not corrupt source/derived artifacts.

## RELEASE POOL

Release Pool shows canonical READY, non-excluded candidates.

Each row/card/preview comes from the candidate's real source PNG and immutable bundle.

Search/filter/select work on this canonical pool.

The selected-for-release list is a publication selection, not a generation step.

### Publish

Nothing publishes automatically.

Owner-triggered Upload/Publish is the final human gate.

STAGING:
Release Pool -> deterministic pack -> preflight -> STAGING -> verification.

PRODUCTION:
requires exact owner approval bound to manifest SHA + content version + PRODUCTION target, then canonical promotion/R2 activation.

No direct UI-to-R2 bypass.

No hard-coded content version.

## Functional test rule

Every visible interactive control must have:
- one explicit handler;
- either a canonical backend binding or documented presentation-only purpose;
- permanent test.

A visually correct but inert control is FAIL.

## 2026-10-20 Owner Override Scope

The 2026-10-20 owner instruction removes MAGNIFIC only from active PIXEL ART provider choices. It does not authorize deleting stored MAGNIFIC source assets/jobs or the historical adapter, changing LEVEL FACTORY/RELEASE POOL, resetting the 140-PNG job, running provider calls, or reinstalling the owner-repaired Studio. V12 Pro Flash palette master is the current implementation authority for this specific provider change.
