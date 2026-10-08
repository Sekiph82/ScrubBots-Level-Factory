# SB-LFX-018-C001 — ChatGPT Strict Audit V01

Date: 2026-10-08  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation:
`b4551d6bfddb3d029e46fc95250fc4985a8190bd`

Builder evidence:
- `779b0449f9bdd9f82ccce6289aa4932ab339d2da`
- `6cd8ba87ea1a510a486ab00a58533287f09a842b`

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001_SIMPLE_OWNER_UI_CODEX_LOG.md`

Criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001_SIMPLE_OWNER_UI_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R01**

The visual direction and navigation simplification are accepted and must be retained.

The task is not yet complete because the eight owner pages are currently mostly a simplified shell around legacy technical tools. Several product-contract page responsibilities are not yet represented by live canonical data and owner controls on the owner page itself.

Full repository regression is also incomplete.

## A — Primary navigation: PASS / RETAIN

The owner-facing navigation is now exactly:

`HOME | CREATE | BATCH | SOLVE | REVIEW | LIBRARY | PUBLISH | SETTINGS`

Legacy technical pages no longer appear as primary navigation destinations.

Runtime/static tests verify the exact list and order.

Retain this architecture.

## B — Window identity and compact shell: PASS / RETAIN

Accepted:

- native owner window title is `ScrubBots Factory Studio`;
- normal runtime no longer displays `(DEBUG)`;
- header copy is concise;
- long canonical-core footer was replaced by compact `System: Ready` / `System: Needs setup`;
- full capability detail remains available by tooltip / Technical details;
- default pages no longer expose the prior engineering text walls.

Retain.

## C — Visual direction: PASS / RETAIN

Independent review of all eight committed screenshots confirms a substantial simplification over the prior 20+ page engineering UI.

Accepted visual direction:

- clear eight-item left navigation;
- large owner page title;
- one-line guidance;
- compact state cards;
- large artwork-preview area;
- one dominant Next Step area;
- contextual secondary actions;
- collapsed Technical details;
- strong use of available screen space;
- compact footer.

The screenshots are technically valid evidence from the durable Release runtime.

However they also reveal that every page currently shares nearly the same generic shell and preview-only owl. That is acceptable as a first visual composition but not sufficient for each page's functional product contract.

## D — Technical capability preservation: PASS / RETAIN

Source and runtime tests confirm legacy tools remain reachable contextually:

- validation / pipeline preparation;
- batch import / failure retry / session recovery;
- comparison / similarity / QA;
- search / revisions / reproduce;
- release / outputs;
- providers / cost;
- explicit ACCEPT / REJECT;
- STAGING;
- separate production approval.

The legacy surfaces are parked and opened contextually rather than deleted.

No acceptance or publish gate was removed.

Retain.

## E01 — BLOCKING: HOME is not yet a live production dashboard

Product contract requires HOME, when batch data exists, to show current/most-recent batch information such as:

- imported count;
- solved count;
- needs-attention count;
- reviewed count;
- accepted count;
- compact pipeline progress;
- thumbnail grid;
- Continue Batch.

Current HOME owner state is hard-coded:

`No batch selected / Choose artwork or continue a saved batch`

and its five state cards come from static defaults.

There is no canonical batch-summary projection or thumbnail grid on HOME.

R01 must bind HOME read-only to existing canonical batch/job/candidate evidence. It must remain truthful when no batch exists.

## E02 — BLOCKING: BATCH lacks the required live per-item production view

Product contract requires BATCH to show:

- overall progress;
- per-item thumbnail/status;
- success / processing / needs-attention counts;
- eligible retry;
- recovery/resume;
- clear next action.

Current BATCH page shows only generic static cards and links into legacy Pipeline / Failures / Session Recovery.

R01 must compose those existing authorities into a simple live BATCH page rather than requiring the owner to operate the old technical surfaces for normal batch work.

Legacy details may remain available behind contextual actions.

## E03 — BLOCKING: SOLVE does not present the solve contract on the owner page

Product contract requires SOLVE to present together:

- artwork/board preview;
- selected supply columns 3/4/5;
- supply-plan summary;
- solver state/result;
- official Difficulty V1;
- concise validation state;
- Solve / Re-solve action.

Current SOLVE owner page contains a generic five-card summary and opens the old Generate workspace.

R01 must project the real canonical solve/supply/difficulty evidence onto the owner page and expose the relevant owner controls there without creating shadow truth.

## E04 — BLOCKING: REVIEW does not yet function as the owner decision page

Product contract requires REVIEW itself to expose:

- large preview;
- supply summary;
- solver result;
- Difficulty V1;
- compact readiness;
- explicit ACCEPT and REJECT owner actions;
- optional compare.

Current owner REVIEW page links to `Open review queue`; ACCEPT/REJECT only appear after entering the legacy contextual surface.

Capability preservation is PASS, but page responsibility is not.

R01 must make explicit ACCEPT/REJECT and the decision evidence directly available in the simple REVIEW composition while delegating mutations to the existing canonical review authority.

## E05 — BLOCKING: LIBRARY is not yet a usable simple library page

Product contract requires LIBRARY to provide:

- search;
- thumbnail/grid or compact list;
- small filters;
- item status;
- open/details;
- history/revision/reproduce contextually.

Current LIBRARY page shows the generic preview shell plus buttons to old Search / Presets / Revisions / Reproduce.

R01 must compose a real read-only library/search result view on the owner page, preserving canonical source/candidate identity.

## E06 — BLOCKING: PUBLISH does not yet expose the safe release workflow on the owner page

Product contract requires PUBLISH to visibly present:

`Accepted Levels -> Campaign Order -> Preflight -> STAGING -> Owner Production Approval`

including:

- selected accepted levels;
- assigned order / level numbers;
- current content version;
- concise preflight;
- Publish to STAGING;
- separate production approval;
- receipt/status.

Current PUBLISH owner page only shows generic cards, `Open campaign order`, `Release pool`, and `Outputs`.

The canonical release surface still contains STAGING and approval, so safety capability is preserved, but the simplified owner page has not yet absorbed the workflow.

R01 must expose it directly while delegating all actual mutations to the existing release/publisher authority.

## E07 — SETTINGS: partial, needs composition closure

SETTINGS correctly routes to Providers, Cost and credits, Session recovery and Technical details.

R01 should complete the simple administrative composition enough that common provider/path/status configuration does not require hunting through an engineering placeholder.

Do not fabricate unavailable provider values.

## F — Canonical-state projection boundary

Current owner state cards are largely static defaults.

The only live owner-page projection today is limited mainly to:

- system status;
- last successful artwork indication;
- canonical artwork preview.

R01 must introduce read-only presentation projections/adapters over existing canonical surfaces/services for HOME/BATCH/SOLVE/REVIEW/LIBRARY/PUBLISH.

Do not create a new authoritative database, tracker, acceptance state or publish state.

Owner-page controls must call the existing canonical mutation methods.

## G — Evidence quality: TECHNICAL PASS, owner visual review still pending

All eight screenshots exist and were independently inspected.

They prove the new shell renders at 1280x800.

They do not yet prove page-specific production states because the same preview-only sample and mostly generic states are shown on every page.

R01 screenshots must include page-appropriate deterministic/canonical fixture states so visual audit can verify the actual contract:

- HOME with batch counts/progress/grid;
- BATCH with multiple item statuses;
- SOLVE with supply columns/solver/difficulty;
- REVIEW with decision controls/readiness;
- LIBRARY with result grid/list;
- PUBLISH with release/preflight/staging/approval state;
- SETTINGS with compact admin state.

Fixture/demo truth must be explicitly labeled and must not fabricate owner acceptance or production publication.

## H — BLOCKING: full repository regression incomplete

Builder started `python -m pytest -q` but interrupted it while:

`tests/integration/test_release_route_a_authentic_verifier.py::test_default_route_a_verifier_runs_against_full_isolated_current_game_archive`

stopped producing progress.

No final full-suite summary exists.

The criteria explicitly require a safe full repository regression.

R01 must classify that exact integration case and complete all collected pytest nodes, either in one run or deterministic complete shards.

No skip/xfail/assertion weakening merely to obtain green output.

## I — Focused regression: PASS / RETAIN

Accepted evidence:

- focused UI/launcher tests: **26 passed**;
- Factory Studio runtime suite: PASS;
- Godot editor import/parse: PASS;
- `git diff --check`: PASS;
- durable Release runtime screenshots: PASS;
- normal fast-forward publication: PASS;
- builder did not edit TASKS/audits.

## R01 scope

R01 is not a visual reset.

Retain the accepted shell and eight-page navigation.

R01 closes:

1. live canonical HOME dashboard composition;
2. live BATCH composition;
3. live SOLVE composition;
4. direct REVIEW decision composition;
5. usable LIBRARY composition;
6. direct safe PUBLISH workflow composition;
7. compact SETTINGS composition;
8. page-specific screenshot evidence;
9. complete regression, including classification of the previously stalled Route A integration.

## FINAL

**CHANGES_REQUIRED / R01**

Do not begin M17.
