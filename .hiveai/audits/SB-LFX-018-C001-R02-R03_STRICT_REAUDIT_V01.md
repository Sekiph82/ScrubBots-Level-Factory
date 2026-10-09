# SB-LFX-018-C001-R02-R03 — Alpix + READY Auto Pool — Strict Re-Audit V01

Date: 2026-10-09
Repository: `Sekiph82/ScrubBots-Level-Factory`

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R02-R03_ALPIX_AUTO_POOL_CONTINUATION_CODEX_LOG.md`

Implementation commit:
`5b975a92532b9df1e781c96cb1de37dbba73aa6e`

Final builder evidence publications:
- `da6442a1f6fa338122702d6a00c864fc8120d466`
- `14d8e662eb39bc9c985de59acb7f29a3ad67c91b`
- `8ec602beee3cd867d0092a4806863f6a2fcec347`

Prompt:
`.hiveai/prompts/SB-LFX-018-C001-R02-R03_ALPIX_AUTO_POOL_CONTINUATION_PROMPT.md`

Criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R03_ALPIX_AUTO_POOL_CONTINUATION_AUDIT_CRITERIA.md`

## VERDICT

**CHANGES_REQUIRED / R04**

R03 contains substantial useful implementation and must be preserved.

The following are independently accepted as useful baseline work:

- exact PIXEL ART V04 master authority;
- three-screen navigation shell;
- Claude Code / Alpix discovery adapter;
- CSV SHA-256 persistent job identity;
- LIMIT / resume preservation;
- ALPIX no-API-key child environment;
- Magnific / PixelLab routing boundaries;
- READY auto-entry to Release Pool;
- Reject excludes / Accept restores;
- durable Release installer and shortcut preservation;
- removal of hard-coded publication version from the visible STAGING path.

However R03 cannot close because the current runtime still does not satisfy the owner's functional application contract.

## A — Preserve prior work: PASS

The builder correctly preserved the earlier R02 implementation rather than restarting.

The R03 implementation is a delta over the existing three-master work.

Post-product commits after `5b975a9` are evidence/log-only.

## B — Legacy EXE resumable job architecture: PASS

Independent source review confirms `src/scrubbots_pixel_factory/alpix_batch.py` implements:

- CSV SHA-256 job identity;
- persisted row state;
- PENDING / DRAWN / VALIDATED / IMPORTED / FAILED;
- LIMIT as a resumable stop rather than row failure;
- restart continuation;
- completed-artifact preservation;
- no repeated draw of completed imported rows.

The focused R03 tests cover simulated limit/resume/restart behavior.

## C — ALPIX adapter: PARTIAL / LIVE CAPABILITY GATE OPEN

The adapter correctly:

- discovers Claude Code locally;
- reads only Claude plugin/config metadata;
- requires an enabled Alpix identity + MCP server;
- strips `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` from the child environment;
- does not silently fall back to another provider;
- validates exact PNG dimensions.

But the builder independently found that the user's local Claude Code installation currently has **no installed/enabled Alpix plugin/MCP**.

Therefore no real Claude + Alpix PNG was generated.

This is not permission to fake the feature. Closure requires either a real installed Alpix capability or an explicit external owner gate.

## D — READY automatic Release Pool: PASS

Independent source review confirms:

- canonical READY can enter Release Pool without ACCEPT;
- auto entry records `eligibility_source = READY_AUTO`;
- REJECT excludes the candidate;
- later ACCEPT restores/re-includes it;
- these pool actions do not themselves publish.

This matches the 2026-10-09 owner decision.

## E — Production UI implementation architecture: FAIL

The most important R03 defect is structural.

`factory_studio_exact_ui.gd` still renders each approved master as the full runtime `MasterCanvas.texture` and places transparent `Button` hotspots over the screenshot.

That means a large part of what the owner sees is still baked fixture text/art rather than live application state.

Examples of values that can remain visually baked into the master instead of being real controls/data include:

- prompt/provider/size text;
- batch counters;
- artwork details;
- Level Details;
- solver status;
- replay result;
- Difficulty V1;
- supply summary;
- Release Pool rows/counts;
- selected-for-release cards;
- release-stage indicators.

A real artwork preview is overlaid in one central region, but this does not convert the rest of the screen into a functional application.

This directly conflicts with the owner's instruction that the masters define the appearance while the application itself must work.

The visual masters may remain reference/evidence assets, but they may not be the production UI background carrying fake state.

## F — Master controls / production publication: FAIL

The R03 UI deliberately leaves PRODUCTION publication unwired:

`_upload_selected()` reports:

`PRODUCTION is unavailable: ... promotion handoff ... not connected.`

The permanent R03 test explicitly asserts that `"production-promotion"` is absent.

That is contrary to the owner's rule that the master controls must actually perform their jobs.

The repository already contains audited canonical authorities:

- CP03-007 verified STAGING download;
- CPX-002 current-main replay;
- CP03-008 production pack promotion;
- CP03-009 production manifest activation.

The UI must connect to those authorities. It must not invent another production route.

## G — Current-game VOID full regression: FAIL, builder diagnosis is incorrect

Builder final full pytest:

**1758 passed, 7 failed, 6 skipped**

All seven failures are LF19 current-game VOID tests.

The builder log states current ScrubBots `main` at:

`44c53a6da0aea1172b1f900c095b7bf20852a541`

does not contain the audited VOID implementation.

Independent GitHub verification disproves that conclusion.

Current ScrubBots `main` includes:

`7d0d148b8609ec04852fdee02f6b8ef37598c616`
`feat(level-data): VOID cells for transparent artwork pixels (ADR-030)`

and current `scripts/data/level_data.gd` contains:

- `FORMAT_VERSION_VOID := 2`;
- `VOID_CELL := -1`;
- artwork/VOID helpers.

Current game also still contains `tests/void_cells_c001.gd`.

The false CLOSED result comes from the LF capability proof relying on:

`git merge-base --is-ancestor 7d0d148... HEAD`

while the builder intentionally created a **shallow** current-game checkout. A shallow checkout can lack the ancestor object even though remote current main contains that commit.

Therefore this is a Factory authority/provisioning defect, not a missing-game-feature external blocker.

R04 must fix this without weakening the VOID tests.

## H — Required R03 test matrix: FAIL / INCOMPLETE

The R03 prompt required permanent coverage for, among other things:

- provider selector -> actual executor;
- external multi-PNG intake;
- immutable PNG-to-derived-artifact matching;
- failed/unsolved PNG consumes no final production order;
- final contiguous release numbering;
- no auto-publish;
- visual three-master runtime fidelity.

The new R03 focused test file contains useful provider/resume/auto-pool coverage, but it does **not** close the complete required matrix.

In particular there is no complete permanent R03 proof for:

- multi-PNG end-to-end pipeline;
- wrong-PNG/wrong-derived-artifact cross-binding rejection;
- failed-item numbering gap prevention;
- final contiguous order through CampaignBuilder;
- real three-screen dynamic-state rendering.

## I — Durable runtime installation: PASS as installation evidence

The durable runtime installation and Desktop shortcut were refreshed.

The stable path remains:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio`

This installer work should be retained.

## J — Final visual evidence: INCOMPLETE

No R03-specific final three-screen screenshot artifacts are published in the repository.

Because R04 must replace screenshot-backed fake state with real live controls, final owner screenshots must be captured again after the functional rebuild.

## Required R04 closure

1. Preserve the exact-master assets, styling geometry, backend adapters, job/resume code, auto-pool work, installer and useful tests.
2. Replace the runtime screenshot+transparent-hotspot architecture with real Godot controls whose geometry/style matches the masters.
3. Bind every visible dynamic field to real state.
4. Keep the real selected PNG in the Visual Review Canvas.
5. Connect PRODUCTION Publish to the already-audited CP03-007/CPX-002/CP03-008/CP03-009 chain with exact owner approval.
6. Fix shallow-history current-game VOID authority so current `main` opens the already-audited VOID capability.
7. Make the seven LF19 tests pass without weakening/skipping them.
8. Add the missing external multi-PNG / identity / ordering / no-gap / dynamic-UI tests.
9. If real Alpix plugin is present, run one real Claude-subscription Alpix PNG smoke. If absent, stop at an explicit owner capability gate after all other technical work is complete.
10. Capture all three final 1536x1024 durable-runtime screenshots.
11. Run final full regression with zero unresolved code/test failures.

## FINAL STATE

`CHANGES_REQUIRED / R04_AUTHORIZED`
