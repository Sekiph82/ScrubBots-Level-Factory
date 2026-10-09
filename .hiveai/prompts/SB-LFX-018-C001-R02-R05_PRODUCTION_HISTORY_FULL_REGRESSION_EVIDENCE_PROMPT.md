# SB-LFX-018-C001-R02-R05 — Preserve R04; Close Production History, Full Regression and Evidence

Document role: CODEX REMEDIATION / CONTINUATION PROMPT

Repository:
`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Parent audit:
`.hiveai/audits/SB-LFX-018-C001-R02-R04_STRICT_REAUDIT_V01.md`

Criteria:
`.hiveai/audit-criteria/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_AUDIT_CRITERIA.md`

Baseline to preserve:
`a22b1c0acd0bc3d606005aef1a15ef8641694dab`

## DO NOT REDO R04

R04 successfully replaced the screenshot/hotspot application with native Godot controls.

Keep that work.

Also keep:

- Alpix adapter / CSV resume;
- READY auto-pool;
- Reject/Accept pool semantics;
- VOID shallow-history correction;
- production confirmation dialog;
- durable installer and shortcut;
- focused passing suites.

Before mutation, log KEEP / ADAPT / ADD.

Never edit root `TASKS.md`.

Never write `.hiveai/audits/**`.

Builder log:
`.hiveai/codex-logs/SB-LFX-018-C001-R02-R05_PRODUCTION_HISTORY_FULL_REGRESSION_EVIDENCE_CODEX_LOG.md`

## 1. FIX ONGOING PRODUCTION PUBLISH

Current R04 code intentionally fails whenever a production manifest already exists because it cannot supply canonical manifest history and creates an empty `ManifestHistoryV1()`.

That only permits the first production release.

This must be fixed.

Read and reuse the already-audited content-platform authorities for:

- manifest history;
- provider release/history storage;
- CP03-007 STAGING verification;
- CPX-002 replay;
- CP03-008 pack promotion;
- CP03-009 versioned production activation.

Do not invent a second history model.

Do not rebuild CP03-008/009.

Do not discard existing production history.

Factory Studio must be able to publish version N+1 when production version N already exists.

## 2. ADD REAL REPEATED-PRODUCTION TEST

Build a permanent integration fixture through the Factory Studio handoff proving:

- existing production manifest/history;
- valid next STAGING manifest;
- exact owner confirmation;
- CP03-008 promotion;
- CP03-009 activation;
- exact production readback/history;
- then another later valid successor publication.

Prove strict version monotonicity.

Add wrong SHA/version/target/stale history/stale authority negatives.

Do not mock away the CP03-008/009 boundaries being audited.

## 3. COMPLETE EXTERNAL PNG IDENTITY / ORDER TESTS

The R04 static dispatch test is not enough.

Create distinct PNG fixtures and run real canonical import/pipeline evidence far enough to prove each source stays bound to its own:

- source SHA;
- LevelData;
- supply plan;
- solver proof;
- replay;
- Difficulty V1;
- metadata/publication identity.

Deliberately cross-bind one derived artifact from PNG A to PNG B and require fail-closed rejection.

For a batch such as:

`A READY -> B FAILED/UNSOLVED -> C READY`

prove canonical CampaignBuilder/release planning yields contiguous final publication order for A/C with no gap consumed by B.

Retry/resume must preserve stable successful order.

Reuse existing canonical order authority.

## 4. CLOSE THE FULL-SUITE HANG

The R04 authority-enabled full pytest never completed.

The log indicates canonical solver calls with:

- analyze=true;
- no max_visited;
- no bounded completion contract.

First identify the exact hanging test(s).

Do not immediately change shipping solver behavior.

Determine whether:

A. the test harness omitted an existing canonical budget, or  
B. a production path truly lacks a required bound.

If A:
- configure the existing canonical budget in that test/fixture path.

If B:
- add an owner-compatible fail-closed visit/time bound using existing solver-budget concepts.

Hard rules:

- no skip;
- no xfail;
- no fake SOLVED;
- no removing replay verification;
- no arbitrary tiny timeout that causes false failures;
- budget exhaustion must return a truthful bounded failure, never hang forever.

Then run the complete repository pytest until it terminates with **0 failures / 0 errors**.

## 5. KEEP VOID GREEN

Run all LF19 current-game tests again against history-complete exact-current ScrubBots authority.

The seven R03 failures must remain closed.

## 6. PUBLISH FINAL SCREENSHOT EVIDENCE

After final R05 code is installed to the durable Release runtime, capture:

- PIXEL_ART_FINAL.png
- LEVEL_FACTORY_FINAL.png
- RELEASE_POOL_FINAL.png

exactly 1536x1024.

Copy the exact final files into:

`.hiveai/evidence/SB-LFX-018-C001-R02-R05/`

also add:

`SHA256SUMS.txt`

Do not regenerate different screenshots merely for GitHub.

These must be byte-identical copies of the final durable-runtime captures.

## 7. CLASSIFY GODOT SHUTDOWN LEAKS

Re-run native runtime/screenshot tests.

If the RID/ObjectDB diagnostics are caused by R04/R05-created nodes/resources, close them.

If they are test-harness cleanup or pre-existing engine/plugin noise, record exact reproduction and bounded disposition.

Do not claim clean shutdown if warnings remain.

## 8. ALPIX EXTERNAL GATE

Recheck installed Claude plugins.

If real Alpix is still absent:

- do not install an ambiguous plugin;
- do not use Anthropic API billing;
- do not fake the smoke;
- finish every other closure;
- report `OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`.

## 9. FINAL VERIFICATION

Run focused suites during development.

After stable implementation, run exactly one final complete regression with correct exact-current game authority.

Final evidence must include:

- full pytest zero failures/errors;
- LF19 PASS;
- production history/successor PASS;
- external PNG identity/order PASS;
- native runtime PASS;
- launcher/install PASS;
- Godot parse/import PASS;
- compileall PASS;
- git diff --check PASS;
- secret scan PASS.

## 10. PUBLICATION

Implementation/tests commit first.

Evidence/log commit separately.

Normal fast-forward push only.

Final execution checkout clean and 0/0.

Final state if Alpix absent but everything else is green:

`AWAITING_GPT_SB_LFX_018_C001_R02_R05_STRICT_REAUDIT / OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`

Final response:
return only the GitHub builder-log URL.
