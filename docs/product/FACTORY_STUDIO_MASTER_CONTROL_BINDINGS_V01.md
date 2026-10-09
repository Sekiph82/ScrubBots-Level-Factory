# Factory Studio Master Control Bindings V01

Status: SUPERSEDED BY `docs/product/FACTORY_STUDIO_MASTER_CONTROL_BINDINGS_V02.md`
Date: 2026-10-09
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Supersession

V02 replaces the owner-review-gated Release Pool rule with owner-approved READY auto-pool behavior and adds Claude+Alpix resumable production. Historical references remain evidence only.

## Purpose

The three visual masters are not decorative screenshots.

Every visible interactive control in the masters must be functional.

Every control must either:

1. invoke an existing canonical Factory/Core/Game/Content-Pipeline authority; or
2. perform a bounded UI-only operation such as selection, zoom, filtering, carousel paging or opening a modal.

No visible primary action may be a placeholder, inert hotspot, fake success, static mock value, or "UNAVAILABLE" explanation when its configured prerequisite is actually available.

The UI must not duplicate solver, difficulty, release, provider or review truth.

## Shared header / canvas controls

### Header

| Visible control | Required behavior | Authority |
|---|---|---|
| PIXEL ART | Switch to PIXEL ART master screen. Preserve current selected artwork when possible. | UI-only screen state |
| LEVEL FACTORY | Switch to LEVEL FACTORY. Carry the selected artwork/candidate identity forward. | UI-only state + immutable candidate identity |
| RELEASE POOL | Switch to RELEASE POOL and refresh current READY owner-accepted entries. | `release_pool.release_entries()` through Studio extension |
| Gear | Open a compact Settings modal, not a fourth page. | Existing Factory Studio configuration only |
| Native minimize/maximize/close | Normal OS window behavior. | OS/Godot window |

### Visual Review Canvas

The same interaction law applies on all three screens:

| Control | Behavior |
|---|---|
| Zoom slider | Change preview zoom only; nearest-neighbor; never alter artwork bytes. |
| Zoom out / zoom in | Step preview zoom down/up. |
| 1:1 | Exact pixel 1:1 view. |
| Fit/full-canvas control | Fit selected artwork/level to available canvas. |
| Grid control | Toggle pixel grid overlay only. |
| Canvas | Always shows the currently selected artwork/level identity, never a decorative unrelated image. |

## PIXEL ART screen

Canonical generation boundaries:

- Godot UI boundary: `level_factory/scripts/factory_core_gateway.gd`
- canonical deterministic Factory Core action: `run_action("Generate", ...)`
- provider abstraction when semantic/provider generation is selected:
  `src/scrubbots_pixel_factory/semantic/provider.py`
  and `src/scrubbots_pixel_factory/semantic/providers/registry.py`
- immutable artwork/candidate output: canonical Factory Core output contracts.

### Single generation controls

| Visible control | Required behavior |
|---|---|
| Single | Select single-generation mode. |
| Batch / CSV | Select CSV batch mode without changing page. |
| Prompt editor | Edit the actual generation prompt used by the selected prompt-capable provider. It must not be ignored. |
| Small cube/random control beside Prompt | Generate a new deterministic seed for the same prompt/style/size/provider request. It must not replace the prompt with unrelated text. |
| Style dropdown | Bind the selected style/profile into the generation request. |
| Size dropdown | Bind requested width/height into the generation request. Board/art envelope validation remains canonical. |
| Provider dropdown | Select the real provider/execution adapter. Never display a provider name that is not actually executing. Provider choices come from the configured provider registry/available local adapter. |
| Generate | Execute one real generation request and create a new immutable candidate/artwork result. Use the selected prompt/style/size/provider/seed. |
| Regenerate | Re-run the same effective request with a newly generated seed, producing a new immutable candidate. Never overwrite the prior candidate. |
| Edit Prompt | Focus/open the existing Prompt editor and preserve the selected candidate until Generate/Regenerate is invoked. Do not display an "unavailable" essay. |
| Add to Level Factory | Carry the exact selected candidate/artwork identity into LEVEL FACTORY and switch screens. No re-generation or byte mutation. |

### CSV batch controls

| Visible control | Required behavior |
|---|---|
| CSV path field/folder control | Open CSV file picker and bind the selected file. |
| Run Batch | Execute each accepted CSV row through the same canonical generation path as Single mode. |
| Batch Progress | Live projection of real row states: completed/succeeded/failed/remaining. Read-only status, not invented counts. |

CSV rows must support the same effective generation inputs as Single mode. Minimum supported logical schema:

`prompt,style,width,height,provider,seed,background_intent`

A documented alias for a single `size` column is allowed if normalized to width/height before execution.

Batch must not use a weaker alternate generator.

### Artwork selection

| Control | Behavior |
|---|---|
| Preview Variations thumbnails | Select that immutable candidate; update canvas + Artwork Details. |
| Bottom artwork thumbnails | Select artwork; update canvas + Artwork Details + current candidate identity. |
| Left/right carousel arrows | Page/scroll current artwork collection only. |

Artwork Details values are derived from the selected actual image/artifact, including dimensions, used colors, transparent/VOID pixels and format.

## LEVEL FACTORY screen

Canonical pipeline authorities:

- Studio extension operation `pipeline`;
- `src/scrubbots_pixel_factory/supply_pipeline/primary.py::run_primary_supply_pipeline`;
- `supply_optimizer.py`;
- `supply_exporter.py`;
- official current ScrubBots solver/replay through the canonical Godot bridge;
- official Difficulty V1;
- Studio extension `owner-review`;
- canonical Release Pool entry on owner ACCEPT only.

### Artwork / batch input

| Visible control | Required behavior |
|---|---|
| Artwork thumbnail | Select exact artwork/candidate and update canvas/details. |
| Artwork left/right arrows | Page current candidate/artwork queue. |
| Select Artwork region interaction | Permit single PNG/current generated candidate selection. It may also accept multi-PNG/CSV batch input without adding a new visible page or panel. |
| Batch input loaded through the existing region | Each batch row/item uses the same canonical pipeline as single mode. No alternate solver. |

For LEVEL FACTORY CSV/batch, each item must be able to bind:
`artwork identity/path, level_number, supply_columns, background_intent`.
Target difficulty may be present only as reporting/planning metadata and must never become a hard acceptance filter.

### Level Settings

| Visible control | Required behavior |
|---|---|
| Level Number | Pass the chosen level number/order into the canonical pipeline/release identity. No static display-only field. |
| Supply Columns 3 / 4 / 5 | Set exact `column_count` passed to the canonical primary supply pipeline. |
| Max Robots = Auto | Owner rule is no global robot cap. "Auto" means canonical no-cap behavior; do not invent a hidden cap. |
| Background | Bind background intent. TRANSPARENT keeps alpha/VOID semantics; fill behavior only when explicitly selected. |
| Target Difficulty = Auto (V1) | Display/plan against official Difficulty V1. Any user-selected target is advisory/reporting only, never a solver/pipeline hard filter. |

### Pipeline and actions

| Visible control | Required behavior |
|---|---|
| Run Pipeline | Execute artwork validation -> supply generation -> official game solve -> replay verification -> Difficulty V1 -> READY preparation through one canonical pipeline request. |
| Pipeline step indicators | Read-only projection of real stage states. They are never manually checked. |
| Supply Plan chevron | UI-only expand/collapse of the real canonical supply plan. |
| Solve Again | Re-run the canonical pipeline/solver route for the same selected artwork and current settings; do not call a shadow solver. |
| Preview Replay | Open a modal/overlay replay preview driven by the canonical solver proof/replay trace. It must not merely show the word WIN. |
| Accept Level | Call append-only `owner-review` with ACCEPT. Enabled only after canonical READY: supply + SOLVED + replay WIN + Difficulty V1 + required QA. Successful ACCEPT enters canonical Release Pool. |
| Reject | Call append-only `owner-review` with REJECT. Never enters Release Pool. |

### Level Variations

| Control | Behavior |
|---|---|
| Variation thumbnail/card | Select that exact candidate/variation and update canvas, solver/difficulty and supply details. |
| Left/right arrows | Page variations only. |

## RELEASE POOL screen

Canonical release authorities:

- `src/scrubbots_pixel_factory/supply_pipeline/release_pool.py`;
- campaign/release ordering authority where required:
  `campaign_builder.py` / `release_route_a.py`;
- trusted Studio publish handoff:
  `scripts/scrubbots_publish_handoff.py`;
- `content_pipeline/src/scrubbots_content_pipeline/one_command_publisher.py`;
- STAGING verification/current-main replay;
- production authority:
  `production_promotion.py` plus versioned production manifest activation;
- Cloudflare R2 provider only through the content pipeline. UI never receives R2 secrets.

### Pool selection / filtering

| Visible control | Required behavior |
|---|---|
| Search Levels | Filter current canonical Release Pool entries by level/name/identity. |
| All Difficulties filter | Filter current pool projection only. |
| All Columns filter | Filter current pool projection only. |
| Ready-level row | Select/highlight exact entry and update Visual Review Canvas + Level Details. |
| Manage Selection (N) | Enter/commit multi-selection behavior for READY entries in the current filtered pool. |
| Select All | Select all currently filtered eligible READY entries. |
| Clear | Clear release selection. |
| Selected-for-Release card | Select card and update preview/details. |
| X on selected card | Remove only that entry from current release selection. |
| Add More Levels | Return focus to Ready Levels selection, retaining already selected entries. |

Only canonical owner-accepted READY entries may appear as releasable items.

### Target / publication controls

| Visible control | Required behavior |
|---|---|
| STAGING (Family Test) | Set target to STAGING. |
| PRODUCTION | Set target to PRODUCTION, but does not itself authorize mutation. Production still requires exact owner approval bound to manifest SHA + content_version + production target. |
| Run Preflight Checks indicator | Read-only real stage state. Cannot be unchecked to bypass a gate. |
| Validate Assets & Data indicator | Read-only real stage state. |
| Build ScrubPack indicator | Read-only real stage state. |
| Upload to R2 indicator | Read-only real stage state. |
| Upload Selected (N) | Execute the canonical publication chain for the selected target and selected exact identities. |
| Preview Release Manifest | Run/build read-only preflight data and open the exact candidate/release manifest in a modal/overlay. No mutation. |

### Upload Selected behavior

If target is STAGING:

1. revalidate current Release Pool membership;
2. resolve exact current ScrubBots game authority;
3. build deterministic ScrubPack(s);
4. run publisher preflight;
5. require secure writer credentials in process environment;
6. invoke the canonical one-command STAGING publisher;
7. surface real receipt/state.

If target is PRODUCTION:

1. require an exact verified STAGING manifest/download for the selected content;
2. require current-main replay verification;
3. present a transient exact approval confirmation containing at least:
   - manifest SHA-256,
   - content version,
   - target = PRODUCTION;
4. only the owner's explicit confirmation creates/uses the exact `OwnerPromotionApproval`;
5. call canonical production promotion and manifest activation;
6. fail closed if approval, authority, history, hashes or provider capabilities differ.

No direct UI -> R2 write is allowed.

No hard-coded content version such as `2` is acceptable for ongoing publication. Derive/validate the next version against current release history/manifest authority.

## Settings gear

Settings is a modal/secondary surface only.

It may configure/bind:
- Factory Python executable/path;
- exact ScrubBots project/authority location;
- available artwork provider adapter selection/config references;
- release/runtime paths;
- credential **availability**.

It must never display, persist or log secret credential values.

## Mandatory implementation rule

The masters are not allowed to be implemented as a background image with a few transparent hotspots.

Every visible interactive control must be a real Godot control or an exact overlay with:

- explicit handler;
- explicit state;
- explicit canonical binding or documented UI-only purpose;
- permanent focused test.

Every master-defined primary action must be usable when its prerequisites are configured.

A handler whose normal behavior is only to report "unavailable", "not implemented", or explanatory text is a FAIL.

## Mandatory binding tests

Permanent tests must prove at least:

1. every visible interactive master control has exactly one intended handler;
2. every backend action handler invokes the correct canonical boundary;
3. changing Prompt/Style/Size/Provider changes the actual generation request;
4. CSV Batch uses the same generator path as Single;
5. Level Number and Supply Columns reach the primary pipeline request;
6. Run Pipeline reaches the official solve/replay/Difficulty V1 route;
7. Preview Replay consumes canonical replay proof;
8. ACCEPT alone creates Release Pool eligibility;
9. REJECT never creates eligibility;
10. release search/filter/select actions operate on canonical Release Pool projection;
11. STAGING Upload Selected uses trusted publish handoff;
12. PRODUCTION Upload Selected requires exact manifest/version/target owner approval and canonical production promotion;
13. R2 secrets never enter UI state/log/artifacts;
14. no hard-coded content version controls real publication;
15. zoom/grid/carousel controls mutate presentation only, never canonical data.
