# Factory Studio Simple Owner UI V01

Status: OWNER-APPROVED PRODUCT CONTRACT  
Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`

## Owner goal

Factory Studio must be as simple to operate as the owner's earlier ScrubBots Level Factory executable while preserving the current canonical backend, evidence, safety and publishing contracts.

The UI is an owner production tool, not an engineering/debug dashboard.

Primary rule:

**Show the owner the job to do, not the backend implementation vocabulary.**

Canonical evidence remains available behind compact Details/Advanced surfaces, but technical truth must not dominate the default screen.

## Primary navigation

Owner-facing navigation is limited to eight primary destinations:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

No other current technical surface may remain as a separate primary navigation item.

Existing internal routes/capabilities may remain for compatibility and tests, but they must be reached contextually or through `Technical details` / `Advanced` / item-history surfaces.

## Page contract

### HOME

Default production dashboard.

Show current or most recent batch using concise cards:

- imported count;
- solved count;
- needs-attention count;
- reviewed count;
- accepted count;
- compact pipeline progress;
- thumbnail grid when artifacts exist;
- one dominant `Continue Batch` action.

No canonical-manifest lecture, provenance paragraph or long capability matrix on the default view.

### CREATE

One job: bring artwork into the Factory and start production.

Provide:

- select one PNG;
- select multiple PNGs / drag-and-drop batch;
- artwork preview;
- source label/name where needed;
- optional compact recipe/settings;
- one dominant `Generate` / `Start Batch` action.

Import Validation and pipeline preparation are contextual status/details inside CREATE, not primary navigation pages.

### BATCH

One job: operate many artworks.

Show:

- overall progress;
- per-item thumbnail/status;
- success / processing / needs-attention counts;
- retry only failed/eligible items;
- resume/recovery when applicable;
- clear next action.

Failures and Session Recovery are contextual BATCH tools, not primary navigation pages.

### SOLVE

One job: understand and produce a playable level from one artwork.

Primary content:

- large artwork/board preview;
- selected supply columns (3/4/5);
- supply-plan summary;
- solver status;
- official Difficulty V1 result;
- concise validation result;
- clear `Solve` / `Re-solve` action.

Technical proof, hashes and detailed solver provenance live behind `Technical details`.

### REVIEW

One job: owner decision.

Primary content:

- large pixel-art preview;
- supply summary;
- solver result;
- difficulty;
- compact readiness card;
- `ACCEPT` and `REJECT` as clear owner actions;
- optional compare action.

Readiness default presentation should be compact, for example:

`Artwork Ready | Supply Ready | Solver Solved | Difficulty Medium | QA Passed`

Candidate inbox, Comparison, Similarity, QA and detailed Readiness become tabs/drawers/contextual actions inside REVIEW.

### LIBRARY

One job: find existing source/candidate/accepted level material.

Provide:

- search;
- thumbnail/grid or compact list;
- small filter controls;
- item status;
- open/details action.

Standalone Search disappears from primary navigation. Revisions/Reproduce live in selected-item History/Advanced details.

### PUBLISH

One job: release accepted levels safely.

Primary workflow:

`Accepted Levels -> Campaign Order -> Preflight -> STAGING -> Owner Production Approval`

Show:

- selected accepted levels;
- assigned order/level numbers;
- current content version;
- concise preflight state;
- `Publish to STAGING`;
- separate explicit production approval action;
- publish receipt/status.

Outputs/artifacts are contextual within PUBLISH. Provider implementation detail is not a primary page.

### SETTINGS

Administrative/rarely used surfaces:

- paths;
- provider configuration/status;
- advanced technical settings;
- diagnostics;
- cost/credit information where truthful;
- recovery/maintenance utilities not appropriate to the normal production flow.

Providers and Cost Center are not primary navigation pages.

## Technical details rule

Engineering terms including `canonical`, `authority`, `immutable lineage`, `derived evidence`, `solver provenance`, SHA identities, gate matrices and low-level reason codes are allowed in expandable details/diagnostics, logs and evidence.

They must not form the default page copy unless the owner is actively diagnosing a failure.

Default states use short human labels:

- Ready
- Processing
- Needs Attention
- Failed
- Solved
- Waiting for Review
- Accepted
- Published to Staging

Do not display ten repeated `NOT AVAILABLE` labels when one concise blocked state plus the next required action communicates the truth.

## Visual hierarchy

- Use available screen area for preview, cards and production state instead of top-left text walls plus empty canvas.
- Primary page title and one-sentence guidance only.
- One dominant primary action per page/state.
- Secondary actions remain visually subordinate.
- Use readable spacing and type at normal desktop scaling.
- Use thumbnails/previews wherever visual identity matters.
- Avoid long all-caps contract paragraphs in the owner surface.
- Preserve the existing owner icon identity.

## Compact system status

Remove the permanent long footer sentence such as:

`Canonical Core: AVAILABLE ... Generate=AVAILABLE ...`

Replace owner-facing default with a small status such as:

`System: Ready`

or a compact status indicator.

Full capability matrix remains available under Diagnostics/Technical details.

## Window identity

Owner-launched durable runtime must display:

`ScrubBots Factory Studio`

The owner production runtime must not show `(DEBUG)` in the window title.

Debug/dev execution may retain diagnostic markers only when explicitly running a debug/development mode and must not leak that title into the normal Desktop shortcut experience.

## Capability preservation map

The simplification must not delete backend capabilities.

Map current surfaces as follows:

- Dashboard -> HOME
- Generate + Import + Import Validation + Pipeline -> CREATE / BATCH contextual workflow
- Batches + Batch Import + Failures + Session Recovery -> BATCH
- solver-related generation/readiness -> SOLVE
- Candidates + Review + Comparison + Similarity + Readiness + QA -> REVIEW
- Library + Search + Presets + Revisions + Reproduce -> LIBRARY / selected-item details, with Presets also available contextually from CREATE
- Release + Outputs -> PUBLISH
- Providers + Cost Center + technical diagnostics -> SETTINGS
- placeholder-only Settings/QA/Providers/Outputs/Batches pages must not remain as empty primary destinations

## Non-negotiable truth boundaries

- No canonical backend logic is replaced by presentation shortcuts.
- No owner acceptance is inferred.
- No QA PASS implies owner acceptance.
- No readiness card bypasses real gates.
- No hidden transformation of artwork.
- No publish safety gate is removed.
- Detailed canonical evidence remains retrievable.
- Existing headless/core workflows remain functional.

## Owner batch target

The UI must make the owner's immediate workflow efficient:

`40 PNG -> validate -> generate supply -> solve -> review -> accept -> campaign order -> publish`

The owner must not need to navigate twenty-plus engineering pages to complete this flow.

## Visual acceptance

Builder must provide current-runtime screenshots for all eight primary destinations at owner desktop scale after implementation.

Independent audit checks contract/behavior. Final visual acceptance remains owner review.
