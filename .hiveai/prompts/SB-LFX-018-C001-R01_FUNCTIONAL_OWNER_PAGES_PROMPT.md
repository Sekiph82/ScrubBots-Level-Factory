# SB-LFX-018-C001-R01 — Functional Simple Owner Pages

Document role: CODEX REMEDIATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Strict audit:
`.hiveai/audits/SB-LFX-018-C001_STRICT_AUDIT_V01.md`

Audit criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R01_FUNCTIONAL_OWNER_PAGES_AUDIT_CRITERIA.md`

Product contract:
`docs/product/FACTORY_STUDIO_SIMPLE_OWNER_UI_V01.md`

Standing sync/publish:
`docs/process/CODEX_SYNC_PUBLISH_STANDARD_V01.md`

## FIRST OPERATION

Follow the standing safe-sync/publish standard.

Use exact current `origin/main`.

Preserve the dirty persistent Desktop checkout. If unsafe, use:

`%TEMP%\ScrubBots-Level-Factory\SB-LFX-018-C001-R01`

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:

`.hiveai/codex-logs/SB-LFX-018-C001-R01_FUNCTIONAL_OWNER_PAGES_CODEX_LOG.md`

## RETAIN THE ACCEPTED VISUAL DIRECTION

Do not return to the old 20+ page UI.

Keep exactly:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

Retain:

- current header;
- simple dark layout;
- compact state cards;
- large preview region;
- dominant Next Step region;
- contextual tools;
- collapsed Technical details;
- compact footer;
- owner window title without DEBUG.

This is a functional composition remediation, not a visual reset.

## 1. Build read-only canonical owner projections

Create narrow presentation adapters/helpers only where needed.

They may aggregate existing canonical surface/service snapshots for display, but must not become new truth.

No owner acceptance, solver result, batch state, release state, content version or provider state may be invented or independently persisted.

Owner mutations continue to call the existing canonical authority.

## 2. HOME becomes the real production dashboard

When batch/candidate evidence exists, show on HOME:

- Imported
- Solved
- Needs Attention
- Reviewed
- Accepted
- compact progress
- a thumbnail/item grid or strip
- Continue Batch

Use the current/most-recent canonical batch/job evidence.

When none exists, preserve the truthful empty state.

Do not show generic static defaults when real canonical data exists.

## 3. CREATE remains simple but operational

Keep the simple composition and expose normal owner actions without requiring technical navigation:

- Choose one PNG
- Choose multiple PNGs / batch
- preview
- validation/preparation summary
- Generate / Start Batch when eligible

Recipes/advanced settings remain secondary.

Use the existing import/validation/pipeline authorities.

## 4. BATCH becomes a real batch operator page

On BATCH itself show:

- overall progress;
- imported/processing/success/needs-attention counts as supported by canonical evidence;
- per-item rows/cards with thumbnail or identity and status;
- Retry eligible failures;
- Resume/Recover;
- Continue pipeline.

Do not merely link to the old Failures/Session Recovery page as the normal experience.

Detailed engineering evidence can remain contextual.

## 5. SOLVE composes supply + solver + Difficulty V1

On SOLVE itself show:

- current artwork/board;
- supply column selection/status 3/4/5;
- supply-plan summary;
- solver status/result;
- replay result where available;
- official Difficulty V1 score/class;
- concise validation state;
- Solve / Re-solve.

Use existing canonical pipeline/solver evidence.

No local substitute solver/difficulty logic.

## 6. REVIEW becomes the explicit owner decision surface

On REVIEW itself show:

- large preview;
- candidate identity;
- supply summary;
- solver result;
- Difficulty V1;
- concise readiness;
- ACCEPT;
- REJECT;
- Compare secondary action.

The simple-page ACCEPT and REJECT controls must call the exact existing canonical owner-review methods.

Do not infer acceptance from QA/readiness.

Preserve review history.

## 7. LIBRARY becomes a usable visual catalog

On LIBRARY itself provide:

- search;
- compact filters;
- grid/list results;
- thumbnail/identity;
- status;
- open/details.

History/Revisions/Reproduce remain contextual for a selected item.

Use existing Library/Search canonical records.

Do not invent persisted collections.

## 8. PUBLISH exposes the safe release progression directly

On PUBLISH itself visibly show:

`Accepted Levels -> Campaign Order -> Preflight -> STAGING -> Production Approval`

Include:

- accepted selected levels;
- assigned order / level numbers;
- content version when authoritative;
- preflight state;
- Publish to STAGING;
- separate explicit production approval;
- receipt/status.

These simple-page actions must delegate to the existing CampaignRelease/Content Pipeline methods.

Do not duplicate R2/publisher logic in the UI.

Do not collapse STAGING and production approval into one action.

## 9. SETTINGS composition

Show compact common admin state/entry points for:

- provider;
- paths/runtime;
- cost/credits if known;
- diagnostics;
- recovery.

Unknown values must remain unknown.

Keep engineering detail under Advanced/Technical details.

## 10. Page-specific visual evidence

Update the screenshot/evidence harness to demonstrate meaningful page-specific states with deterministic, clearly labeled fixture/canonical data.

Capture eight durable Release screenshots.

At minimum evidence must visibly demonstrate:

- HOME: batch counts/progress + multiple items;
- CREATE: source/entry controls;
- BATCH: item statuses/progress;
- SOLVE: supply columns + solver + Difficulty V1;
- REVIEW: readiness + ACCEPT/REJECT;
- LIBRARY: multiple results;
- PUBLISH: release progression with STAGING and production approval distinct;
- SETTINGS: compact admin state.

Never label fixture/demo state as real owner acceptance or real production publication.

## 11. Regression closure

The C001 full pytest did not complete.

Run the exact stalled Route A integration separately:

`tests/integration/test_release_route_a_authentic_verifier.py::test_default_route_a_verifier_runs_against_full_isolated_current_game_archive`

Classify/fix any current-head issue without weakening the test.

Then complete every collected repository pytest node.

Monolithic full pytest is preferred.

If operationally necessary, deterministic shards are allowed only if:

- collect node IDs first;
- record the full node list/count;
- every node runs exactly once across shards;
- every shard has a final summary;
- union equals collection;
- no unresolved failure remains.

Also run:

- focused owner UI tests;
- Factory Studio runtime suite;
- durable launcher/runtime smoke;
- Godot editor parse/import;
- compileall;
- diff check;
- secret scan.

No permanent skip/xfail/assertion weakening to manufacture green.

## 12. Publication

Implementation/test commit first.

Builder log/evidence commit separately.

Normal fast-forward push only.

Final:

- HEAD == origin/main;
- 0 ahead / 0 behind;
- clean execution worktree.

Final builder state:

`AWAITING_GPT_SB_LFX_018_C001_R01_STRICT_REAUDIT`

Return only the GitHub builder-log URL.
