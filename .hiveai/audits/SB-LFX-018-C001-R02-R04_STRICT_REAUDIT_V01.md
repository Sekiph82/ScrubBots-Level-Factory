# SB-LFX-018-C001-R02-R04 — Real UI + VOID + Production Publish — Strict Re-Audit V01

Date: 2026-10-09
Repository: `Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R02-R04_REAL_UI_VOID_PRODUCTION_CLOSURE_CODEX_LOG.md`

Implementation:
`a22b1c0acd0bc3d606005aef1a15ef8641694dab`

Evidence publication:
`694d6c56c96968fb7c7d790c5b407de219da74d9`

Prompt:
`.hiveai/prompts/SB-LFX-018-C001-R02-R04_REAL_UI_VOID_PRODUCTION_CLOSURE_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R04_REAL_UI_VOID_PRODUCTION_CLOSURE_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R05**

R04 is a large and useful improvement. Preserve it.

The native three-screen UI conversion, corrected VOID-authority diagnosis, durable installation, READY auto-pool behavior, and production-confirmation surface are accepted as baseline work.

R04 does not close because four hard gates remain:

1. complete unfiltered regression never finished;
2. production publication is not actually usable for ongoing production once a production manifest already exists;
3. required external-PNG identity/order coverage is still mostly static dispatch inspection rather than end-to-end proof;
4. final three screenshots are not published as auditable repository evidence.

The Claude/Alpix live smoke remains an external owner capability gate because no installed/enabled Alpix plugin/MCP was present locally.

## A — Prior work preservation: PASS

Builder preserved the useful R02/R03 implementation.

No destructive cleanup/reset/force behavior is evidenced.

R04 product commit is cleanly separated from builder evidence.

## B — Real native UI architecture: PASS

Independent source review confirms the previous screenshot-plus-transparent-hotspot production architecture was removed.

`factory_studio_exact_ui.gd` now:

- clears `MasterCanvas.texture`;
- hides `MasterCanvas`;
- creates real Panels/Labels/Buttons;
- binds real handlers;
- projects candidate/release data into real controls;
- renders actual artwork images through runtime textures.

The visual masters remain reference authority rather than live baked-state backgrounds.

This closes the main architectural defect from R03.

## C — PIXEL ART / LEVEL FACTORY / RELEASE POOL dynamic controls: PASS WITH OWNER VISUAL REVIEW STILL REQUIRED

The three production screens now contain real runtime controls and live state.

R04 also preserves:

- ALPIX / MAGNIFIC / PIXELLAB selection;
- resumable ALPIX batch state;
- generated/imported artwork preview;
- LEVEL FACTORY pipeline controls;
- READY Release Pool projection;
- STAGING and PRODUCTION selection;
- exact production-confirmation dialog.

Independent owner visual acceptance of the actual durable screenshots is still required before final UI closure.

## D — VOID authority correction: PASS

The prior shallow-history false negative was correctly fixed.

`void_capability.py` now distinguishes:

- `INCOMPLETE_GIT_HISTORY`;
- `AUDITED_VOID_ANCESTOR_MISSING`.

Builder then used history-complete exact-current ScrubBots authority and reports:

- focused VOID/source/game parity: **20 passed**;
- all seven previously failing LF19 cases are included in that passing set.

This is consistent with the already-audited game VOID implementation.

## E — Production confirmation UI: PASS

The UI now has a real transient production confirmation bound to:

- exact manifest SHA-256;
- exact content version;
- target = PRODUCTION.

The publisher handoff rejects wrong confirmation before production assembly.

No direct UI -> R2 credential path was introduced.

## F — Ongoing PRODUCTION publication: FAIL

The new production adapter is not complete for normal ongoing publication.

Inside `scripts/scrubbots_publish_handoff.py`, production assembly does:

`current_production = provider.read_object_bytes(Environment.PRODUCTION, _MANIFEST_KEY).content_bytes`

and if a production manifest already exists:

`raise ValueError("production manifest history is not available from the provider contract")`

It then creates:

`ManifestHistoryV1()`

only for the empty-history case.

Therefore the UI production flow can only proceed when there is no prior production manifest. After the first production release, subsequent legitimate production publication is intentionally blocked.

That violates the owner workflow and R04 criteria, which require repeated versioned production releases through the existing audited CP03-008/CP03-009 history/CAS chain.

R05 must bind the real canonical manifest-history authority. It must not fabricate history and must not weaken CP03-009.

## G — Production-chain test quality: PARTIAL / FAIL

The new focused production test proves exact confirmation reaches a mocked typed publisher request.

It does not independently prove an actual non-empty-history CP03-008 + CP03-009 successor activation through the Factory Studio handoff.

Required permanent coverage must include:

- existing production manifest/history;
- next valid content version;
- exact owner approval;
- CP03-008 pack promotion;
- CP03-009 manifest activation;
- exact readback/history;
- second/subsequent production publication;
- wrong hash/version/target and stale history fail closed before unsafe mutation.

## H — External PNG intake: PARTIAL

R04 adds useful dispatch coverage proving single, multi-select and CSV routes call `batch-import` then `pipeline`.

However the new test is static source inspection.

It does not satisfy the stronger R04 identity/order criteria requiring actual end-to-end evidence that:

- multiple different PNG byte identities remain bound to their own derived LevelData/supply/solver/replay/Difficulty metadata;
- deliberate cross-binding rejects;
- a failed/unsolved middle item consumes no final production order;
- CampaignBuilder produces a contiguous final sequence;
- retry/resume preserves stable successful order.

R05 must add real fixture-based integration coverage.

## I — Full regression: FAIL

R04 criteria require a complete repository pytest run with zero unresolved code/test failures.

That evidence does not exist.

Builder records:

- no-authority run: **1741 passed, 20 skipped, 10 failed, 3 errors**;
- authority-enabled run: no final summary because canonical solver execution hung for more than 30 minutes and was manually stopped.

Focused suites are useful, including:

- 60 focused PASS;
- 20 VOID/source-game parity PASS;
- Godot runtime assertions PASS.

But focused success cannot replace the required complete regression.

R05 must identify the exact unbounded/hanging test path and close it without weakening shipping solver semantics or skipping the test.

## J — Solver/full-suite hang: OPEN DEFECT

Builder notes the authority-enabled full suite entered canonical solver requests with:

- `analyze=true`;
- no `max_visited`;
- no bounded timeout/result.

This is now a reproducible test/execution closure issue.

R05 must:

1. identify the exact hanging test(s);
2. distinguish test-harness configuration from shipping solver semantics;
3. use an existing canonical bounded solver budget/timeout authority where appropriate;
4. fail closed on budget exhaustion rather than hang forever;
5. preserve real solver/replay verification;
6. finish the entire suite.

No skip/xfail or fake solver result is acceptable.

## K — Godot shutdown leak diagnostics: CONDITIONAL

R04 runtime/editor/screenshot commands exit 0 and no script/resource-load error remains.

Godot still reports RID/ObjectDB allocations at shutdown.

This is not independently proven to affect normal app use, so it is not by itself an R04 rejection.

R05 should classify the leak source. If introduced by the R04 UI, close it. If it is test/editor shutdown-only or pre-existing engine/plugin noise, publish bounded evidence and do not hold the milestone for unrelated engine diagnostics.

## L — Durable install: PASS

Installed runtime:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

Builder reports:

- installer exit 0;
- 2,077 managed files;
- 0 missing/mismatched managed files;
- Desktop shortcut preserved;
- local Desktop repo synchronized 0/0 while owner-untracked files remained untouched.

## M — Final screenshot evidence: INCOMPLETE

Builder reports three final durable captures, each 1536x1024, with SHA-256 values.

Those images are stored only under the user's installed runtime path and are not committed/published with the builder evidence.

Independent audit cannot inspect them from GitHub.

R05 must copy the final three screenshots into a bounded repository evidence folder and publish them unchanged, together with SHA-256 values.

This is evidence publication only, not a redesign request.

## N — Claude + Alpix live smoke: OWNER EXTERNAL GATE

Builder rechecked local Claude configuration and found no installed/enabled Alpix plugin/MCP.

Correct behavior:

- no fake Alpix success;
- no Anthropic paid API fallback;
- no ambiguous third-party install.

This remains:

`OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`

after all code/runtime gates are green.

## R05 required closure

Preserve R04.

Do only the remaining closure work:

1. bind canonical persisted production manifest history so second/subsequent production releases work through CP03-008/009;
2. add real successor-production tests;
3. add real external multi-PNG immutable-identity / cross-binding / contiguous-order integration tests;
4. bound/fix the full-suite solver hang without weakening real solver verification;
5. complete full pytest with zero unresolved failures;
6. publish the three final 1536x1024 screenshots as auditable evidence;
7. classify/fix R04-introduced Godot shutdown leaks if any;
8. keep Alpix as an external owner plugin gate if still absent.

## FINAL STATE

`CHANGES_REQUIRED / R05_AUTHORIZED / OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`
