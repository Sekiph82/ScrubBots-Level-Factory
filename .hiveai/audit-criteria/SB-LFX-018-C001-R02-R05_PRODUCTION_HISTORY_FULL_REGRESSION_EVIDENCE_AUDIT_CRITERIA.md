# SB-LFX-018-C001-R02-R05 — Production History + Full Regression + Evidence Closure — Audit Criteria

Parent audit:
`.hiveai/audits/SB-LFX-018-C001-R02-R04_STRICT_REAUDIT_V01.md`

R04 implementation:
`a22b1c0acd0bc3d606005aef1a15ef8641694dab`

## A. Preserve R04

Do not rebuild the native UI.

Preserve:

- native three-screen real-control architecture;
- R03 Alpix/resume work;
- READY auto-pool;
- corrected VOID capability;
- production confirmation UI;
- durable installer/shortcut;
- passing focused tests.

## B. Canonical production history

Factory Studio PRODUCTION must support an existing production manifest/history.

Use existing canonical content-platform history authorities.

Do not:

- invent manifest history;
- start from `ManifestHistoryV1()` when prior production exists;
- bypass CP03-008/009;
- erase or rewrite prior history.

PASS requires exact prior history/precondition binding into the canonical publisher.

## C. Repeated production release

Permanent integration test must prove at least:

1. a prior production manifest/history exists;
2. a newer valid STAGING candidate exists;
3. exact owner approval binds manifest SHA/version/PRODUCTION target;
4. CP03-008 promotes exact packs;
5. CP03-009 activates the new versioned production manifest;
6. production readback and history are exact;
7. a later second successor publication also succeeds;
8. versions remain strictly monotonic;
9. no direct UI/R2 shortcut exists.

## D. Adversarial production tests

Require zero unsafe mutation for:

- missing approval;
- wrong manifest SHA;
- wrong content version;
- wrong target;
- stale current-game authority;
- stale STAGING receipt;
- stale production precondition;
- incomplete/tampered manifest history.

## E. External PNG end-to-end identity

Use real distinct PNG fixtures.

Prove for single and multi/CSV batch:

- source PNG SHA identity;
- LevelData binding;
- supply-plan binding;
- official solver/replay binding;
- Difficulty V1 binding;
- metadata/publication identity binding.

Deliberately cross-bind one candidate's derived artifact to another PNG and require rejection.

Static source-string inspection alone is not sufficient.

## F. Batch ordering

Using canonical CampaignBuilder/release ordering, prove:

- READY successes preserve source order;
- failed/unsolved middle input consumes no final production level number;
- resulting final production sequence is contiguous after current catalog/history tail;
- retry/resume does not reshuffle stable successful candidates.

No parallel number allocator.

## G. Full-suite bounded execution

Identify the exact prior full-suite hang.

Use existing canonical solver budget/timeout authority where appropriate.

Requirements:

- no infinite/unbounded test execution;
- no fake solver;
- no skip/xfail;
- no weakened SOLVED/replay checks;
- budget exhaustion fails closed;
- complete repository pytest terminates and reports zero failures/errors.

If a shipping code path was truly unbounded, fix it with an owner-compatible bounded contract.

If only the test harness omitted an existing required budget, fix the harness/configuration without changing shipping semantics.

## H. VOID

All LF19 current-game parity tests remain green.

Do not regress the R04 shallow-history fix.

## I. Final visual evidence publication

Commit exact copies of the final durable screenshots under:

`.hiveai/evidence/SB-LFX-018-C001-R02-R05/`

Required:

- `PIXEL_ART_FINAL.png`
- `LEVEL_FACTORY_FINAL.png`
- `RELEASE_POOL_FINAL.png`
- `SHA256SUMS.txt`

Each screenshot exactly 1536x1024.

Evidence must come from the final installed runtime after all R05 code changes.

## J. Godot shutdown diagnostics

Determine whether the RID/ObjectDB diagnostics are:

- R04/R05 UI leaks;
- test-harness cleanup artifacts;
- or pre-existing Godot/plugin diagnostics.

Fix task-introduced leaks.

If not task-introduced, record reproducible bounded evidence.

## K. Alpix

If Alpix plugin/MCP remains absent:

- do not fake;
- do not use paid API fallback;
- preserve resumable jobs;
- report `OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED`.

Absence of Alpix does not excuse other technical failures.

## L. Final verification

Require:

- production-history focused suite PASS;
- external-PNG identity/order suite PASS;
- all LF19 PASS;
- native UI/runtime PASS;
- launcher/install PASS;
- Godot parse/import PASS;
- complete repository pytest PASS with zero failures/errors;
- compileall PASS;
- diff check PASS;
- secret scan PASS.

Builder does not edit root `TASKS.md` or `.hiveai/audits/**`.

Implementation/tests commit separately from evidence/log.

Normal fast-forward push only.

## Outcome

If all technical gates pass but Alpix plugin is absent:

`TECHNICAL PASS / OWNER_CLAUDE_ALPIX_PLUGIN_REQUIRED / OWNER VISUAL REVIEW`

If Alpix is present and live smoke also passes:

`TECHNICAL PASS / OWNER VISUAL REVIEW`

Otherwise:

`CHANGES_REQUIRED`.
