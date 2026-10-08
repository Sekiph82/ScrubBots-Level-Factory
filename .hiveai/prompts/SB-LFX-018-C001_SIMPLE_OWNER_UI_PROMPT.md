# SB-LFX-018-C001 — Simple Owner UI

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Product contract:
`docs/product/FACTORY_STUDIO_SIMPLE_OWNER_UI_V01.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001_SIMPLE_OWNER_UI_AUDIT_CRITERIA.md`

Standing sync/publish:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## EXECUTION GATE

Run only after `MAINT-FACTORY-STUDIO-LAUNCHER-C001-R01` and `SB-LFX-019-C001` are independently PASS/CLOSED and root `TASKS.md` makes `SB-LFX-018-C001` Current Task. VOID is implemented first so CREATE/SOLVE/REVIEW previews and status surfaces are simplified once against the final transparent-art contract.

Do not begin M17 concurrently.

## FIRST OPERATION — standing safe sync

Apply `docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`.

Use exact current `origin/main`. Preserve the dirty owner Desktop checkout. If it is not clean fast-forward-safe, use one clean task worktree:

`%TEMP%\ScrubBots-Level-Factory\SB-LFX-018-C001`

Never edit root `TASKS.md` or `.hiveai/audits/**`.

Builder log:

`.hiveai/codex-logs/SB-LFX-018-C001_SIMPLE_OWNER_UI_CODEX_LOG.md`

## OWNER UX TARGET

The current Factory Studio is functionally rich but owner-hostile: too many top-level pages, engineering vocabulary, repeated unavailable matrices, small text blocks and unused canvas.

Keep the engine. Redesign the cockpit.

Do not remove canonical capabilities. Recompose them.

## 1. Replace primary navigation

Owner-facing primary navigation must become exactly:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

Preserve stable internal route/service IDs where useful for tests/backward compatibility, but technical routes must no longer appear as primary menu items.

Map all existing functions according to `FACTORY_STUDIO_SIMPLE_OWNER_UI_V01.md`.

## 2. Build simple production pages

Implement the eight page contracts from the product spec.

High priority owner workflow:

`40 PNG -> validate -> generate supply -> solve -> review -> accept -> campaign order -> publish`

The owner should normally progress through this flow without opening diagnostics.

## 3. Remove technical text walls from default surfaces

Default owner pages must not display long paragraphs explaining canonical/immutable/authority/provenance architecture.

Replace them with:

- short state;
- short reason if blocked;
- next action.

Keep exact technical truth under expandable `Technical details`, `Advanced`, Diagnostics or selected-item History.

Do not delete evidence fields from the underlying data/service contract.

## 4. Compact readiness/status

Replace multi-line repeated `NOT AVAILABLE` matrices with concise owner-readable state.

Example visual contract:

`Artwork Ready`
`Supply Ready`
`Solver Solved`
`Difficulty Medium`
`QA Passed`

with:

`Technical details >`

When blocked, show the first actionable blocker and the next required action. Do not fabricate readiness.

## 5. Use the screen for visual production work

Artwork preview and thumbnail grids must become first-class.

Avoid layouts where all controls/text occupy the top-left while most of the screen is unused.

Create clear hierarchy:

- page title;
- one-line guidance;
- primary visual/state content;
- one dominant action;
- secondary/advanced detail below or collapsed.

## 6. Owner runtime identity

Normal Desktop shortcut runtime title:

`ScrubBots Factory Studio`

Do not show `(DEBUG)` in the normal owner runtime.

Replace the permanent long canonical-core footer with a compact status such as `System: Ready`. Full capability matrix remains in Diagnostics.

## 7. Preserve all real capabilities

Do not remove or weaken:

- manual import;
- batch import;
- validation;
- canonical pipeline;
- supply/solver;
- Difficulty V1;
- QA;
- owner review;
- comparison;
- similarity;
- revisions;
- reproduce;
- failure retry;
- session recovery;
- presets;
- provider accounting;
- publish preflight/STAGING/production approval.

Move them into the correct contextual owner page.

Do not replace backend truth with UI-local shadow state.

## 8. Visual evidence

Run the durable owner runtime and capture screenshots for:

1. HOME
2. CREATE
3. BATCH
4. SOLVE
5. REVIEW
6. LIBRARY
7. PUBLISH
8. SETTINGS

Use realistic fixture/canonical data where safe so the screens demonstrate layout. Do not fabricate PASS truth.

Record screenshot paths and state in the builder log.

## 9. Tests

Add focused tests proving:

- primary nav is exactly eight entries;
- old technical pages are absent from primary nav;
- internal capabilities remain reachable contextually;
- compact footer/status;
- normal owner runtime title excludes DEBUG;
- major page nodes/actions exist;
- no publish/review truth boundary changed.

Run Factory Studio runtime suite and safe full repository pytest.

## 10. Publication

Use the mandatory finish section of `CODEX_SYNC_PUBLISH_STANDARD_V01.md`.

Implementation/test commit first, builder-log/evidence commit second, normal push to `main`, final 0/0 clean parity.

Final response:
return only the GitHub builder log URL.
