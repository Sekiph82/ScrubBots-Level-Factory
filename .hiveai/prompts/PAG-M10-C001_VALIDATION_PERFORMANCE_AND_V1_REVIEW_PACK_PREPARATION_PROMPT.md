# PAG-M10-C001 — Validation, Performance & V1 Review Pack Preparation
Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`
Canonical current-state tracker: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md`

Previous closing audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M09-C003_DETERMINISTIC_CANDIDATE_IDENTITY_AND_ACCEPTANCE_MATRIX_CLOSURE_STRICT_AUDIT.md`

## 1. Mission

Begin PAG-M10 after the independent PASS/CLOSED result for M09.

This cycle prepares the machine-verifiable V1 acceptance evidence and the fixed 100-candidate owner review pack. It covers:

- PAG-S10.1 property/fuzz validation (`PAG-1001..PAG-1011`);
- PAG-S10.2 measured performance (`PAG-1012..PAG-1022`);
- PAG-S10.3 review-pack generation and reports (`PAG-1023..PAG-1032`);
- machine-verifiable evidence needed for PAG-S10.4 (`PAG-1035..PAG-1049`) where this cycle can prove it without owner judgment.

This cycle does NOT self-complete owner-only gates:

- `PAG-1033` owner manually reviews the 100-candidate pack;
- `PAG-1034` final owner-approved/rejected/tuning classification;
- `PAG-1050` owner accepts the visual V1 review pack.

Those remain owner/ChatGPT acceptance gates after the pack is published.

`PAG-0441` may only become eligible for closure after measured RULES 59x59 evidence exists and an explicit V1 performance budget is recorded from the measured laptop data.

Do not begin M11.

## 2. Current authority / boundaries

Root `TASKS.md` is the only current project-state tracker.

Codex is builder only. Do not edit root task checkboxes/status, do not author independent audits, and do not declare M10 or V1 accepted.

Authorized local mirror only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never use or modify the sibling main-game repository:
`C:\Users\sekip\Desktop\ScrubBots`

Preserve all independently accepted M00-M09 contracts.

No network/API/cloud runtime. No GPU requirement. No new runtime dependency merely for benchmarking/property tests/reporting.

## 3. GitHub-first start

Before edits read from GitHub `main`:

1. root `TASKS.md`;
2. `AGENTS.md`, `GOVERNANCE.md`, README and pyproject;
3. M09 C003 closing audit and builder log;
4. M01 dimension/palette/color-band contracts;
5. M02 request/RNG/result contracts;
6. M03 MASK generator and accepted family evidence;
7. M04 RULES generator and deferred `PAG-0441` context;
8. M05 WFC exemplar contract and tracked synthetic fixtures;
9. M06 HYBRID/AUTO router/replay contracts;
10. M07 quality/diversity/review contracts;
11. M08 export/bundle contracts;
12. M09 CLI/batch/reproduce contracts;
13. current property/performance/review test directories and any existing benchmark helpers.

Synchronize non-destructively. Preserve unrelated local dirt.

## 4. Matching builder log

Before first M10 source/test/report edit create:

`.hiveai/codex-logs/PAG-M10-C001_VALIDATION_PERFORMANCE_AND_V1_REVIEW_PACK_PREPARATION_CODEX_LOG.md`

Exact H1:

`# PAG-M10-C001 — Validation, Performance & V1 Review Pack Preparation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record:

- start HEAD/origin/divergence/status;
- authority reads;
- hardware/runtime facts actually observable on the owner's machine;
- every failing test/benchmark and correction;
- exact property corpus size and deterministic corpus identity;
- exact benchmark seed set/config identity;
- raw and summarized benchmark measurements;
- proposed measured budgets and derivation;
- review-pack generation counts/mode mix/rejections;
- test commands/counts;
- implementation/report commits and pushes;
- final post-publication `HEAD == origin/main`, divergence `0 0`.

Do not hide slow, failed, rejected, contradicted or exhausted attempts.

## 5. Property/fuzz corpus, PAG-1001..1011

Create a deterministic project-owned property/fuzz suite without adding a runtime dependency.

### 5.1 Deterministic corpus

Use a fixed project seed/config to construct at least 2,000 valid `GenerationRequest` cases across the four difficulties, legal explicit and auto dimensions, square and rectangular dimensions, legal palette subsets, styles/themes/options that are valid for the selected generator, and the supported generator modes that can run under available local fixture requirements.

The corpus definition must be deterministic and versioned so a future run executes the same cases unless its corpus version deliberately changes.

Do not use Python global random or Python `hash()` as corpus authority.

### 5.2 Successful-result invariants

For every successful generation exercised by the property suite directly assert:

- result width equals resolved/requested width;
- result height equals resolved/requested height;
- cell count equals width×height;
- every logical cell is C01..C16;
- distinct used-color count satisfies difficulty band;
- used palette equals the actually-used ascending canonical subset;
- BG01 is absent;
- repeated same request reproduces the same logical grid and canonical result where applicable.

Exercise all four difficulty bands and genuinely rectangular cases.

The suite must include explicit 59×59 cases where the selected difficulty permits them.

### 5.3 Invalid request/batch robustness

Add a deterministic invalid-input corpus covering dimensions, difficulty/mode/options/palette conflicts and malformed CLI/batch inputs.

Expected invalid inputs must return/raise accepted domain errors and must not crash the batch process with uncontrolled traceback/state corruption.

### 5.4 Practicality

Do not turn the normal fast unit suite into an accidental multi-hour benchmark. It is acceptable to mark the full thousands-case corpus as an explicit M10 validation/performance test command if documented and still run it during this cycle.

The committed tests must make corpus count and coverage machine-verifiable.

## 6. Measured performance harness, PAG-1012..1022

Create a deterministic stdlib-based benchmark harness under the existing test/tool architecture, preferably `tests/performance/` and/or a small project-owned script.

Do not add benchmark libraries solely for this milestone.

### 6.1 Modes

Measure each available generator mode separately rather than hiding it behind AUTO:

- MASK;
- RULES;
- WFC using only tracked legal synthetic fixtures for technical engine benchmarking unless an owner-approved production exemplar exists;
- HYBRID strategies, separated sufficiently to identify WFC-bearing vs non-WFC-bearing paths;
- AUTO may be reported additionally but never substitutes for explicit-mode measurements.

Synthetic WFC fixtures are technical benchmark evidence only. Do not relabel them as owner-approved visual production exemplars.

### 6.2 Difficulty/size coverage

For each relevant mode benchmark representative:

- EASY;
- MEDIUM;
- HARD;
- VERY_HARD;
- explicit 59×59 VERY_HARD.

Use fixed deterministic benchmark seeds/configs committed as a manifest or source constant.

Include square and at least one rectangular workload where meaningful.

### 6.3 Measurements

For every benchmark family record at minimum:

- mode / strategy;
- difficulty;
- width×height;
- benchmark seed/config identity;
- number of measured samples;
- successes;
- quality rejections;
- generator contradictions/failures/retry exhaustion as applicable;
- median generation time;
- p95 generation time using a documented deterministic percentile method;
- peak Python memory using a stdlib mechanism such as `tracemalloc` with clearly documented semantics;
- total/accepted attempt counts where quality filtering is included.

Separate raw generation timing from optional PNG/review rendering if both are measured. Do not disguise export time as generator time.

### 6.4 Warmup / measurement integrity

Use explicit warmup behavior if needed, then measure a fixed seed set. Do not cherry-pick only fast successful seeds after seeing results.

Do not use wall-clock timestamps as deterministic artifact identity.

### 6.5 V1 performance budget proposal

The owner locked rule is: establish budgets from measured laptop results, not invented targets.

Produce `review/m10/M10_PERFORMANCE_REPORT.md` and a machine-readable JSON companion that contain:

- observed hardware/runtime facts available locally;
- raw benchmark summary;
- per-mode/difficulty median and p95;
- 59×59 results;
- failure/rejection rates;
- an explicit proposed V1 budget for each relevant mode/strategy;
- the deterministic rule/headroom used to derive each proposal from measured data;
- whether each measured result is inside the proposed budget.

Do not silently set a budget equal to one observed sample simply to force PASS. Explain headroom and measurement variability.

The independent auditor/owner will decide whether the proposed budget is acceptable for the offline factory workflow. Codex does not self-approve `PAG-0441` or `PAG-1048`.

### 6.6 Optimization boundary

`PAG-1022` means optimize only a measured bottleneck.

Do not proactively rewrite accepted generators for speed. If all modes are practically acceptable, record `NO_OPTIMIZATION_REQUIRED` with evidence.

If a measured bottleneck appears severe enough to require product changes, stop before broad algorithm redesign, document the measured bottleneck and propose a bounded follow-up remediation. Do not weaken determinism/quality to win a benchmark.

## 7. Fixed 100-candidate V1 owner review pack, PAG-1023..1032

Generate exactly 100 accepted review candidates:

- 25 EASY;
- 25 MEDIUM;
- 25 HARD;
- 25 VERY_HARD.

Use a committed deterministic review-pack manifest defining root seed/config/version and selection rules. Re-running the same pack definition must reproduce the same accepted candidate IDs/logical grids/review artifacts.

### 7.1 Mode mix

The review set must include meaningful MASK and RULES examples across difficulties.

M06 is accepted, so include HYBRID examples using strategies that are valid with available inputs.

For WFC:

- include WFC visual-review candidates only if an owner-approved exemplar is actually available under the accepted M05 contract;
- if no approved exemplar exists, explicitly record `WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR` and do not fabricate/upgrade a synthetic fixture into owner art;
- technical WFC engine/property/performance evidence may still use tracked synthetic fixtures.

AUTO may be included as additional routing evidence but does not replace the explicit mode families above.

### 7.2 Acceptance and duplicate rules

Only M07 `ACCEPT` candidates enter the 100-candidate pack.

Record every generation attempt, seed, rejection code, duplicate relation and accepted ID needed to reproduce selection.

Do not mutate accepted grids to improve diversity. Regenerate using recorded deterministic seeds.

Exact duplicates must not occupy multiple review slots. Record near-duplicate metrics separately rather than silently mutating output.

### 7.3 Review artifacts

Publish deterministic owner-review artifacts under `review/m10/`.

At minimum:

- `M10_REVIEW_MANIFEST.json` containing the 100 accepted candidate identities, difficulty/mode/style/family/seed/dimensions/grid hash and review state;
- `M10_REVIEW_INDEX.html`, fully offline/self-contained, with clear grouping by difficulty and mode/family and integer-nearest-neighbor visual previews;
- `M10_METRICS_REPORT.json`;
- `M10_METRICS_REPORT.md` summarizing attempts, acceptance/rejection/duplicate rates, structural quality/diversity metrics and mode/difficulty counts;
- `M10_PERFORMANCE_REPORT.json`;
- `M10_PERFORMANCE_REPORT.md`.

The HTML must not depend on CDN/network JavaScript, external fonts, remote images or remote CSS.

Do not commit hundreds of redundant heavyweight candidate directories if the same owner-review evidence can be represented compactly by deterministic logical data + self-contained review HTML. If source candidate bundles are needed for audit, store them in a clearly bounded review/evidence area and justify size.

### 7.4 Owner review fields

Every review candidate needs a stable owner-review slot/status such as:

- `PENDING_OWNER_REVIEW` initially;
- later `APPROVED`;
- `REJECTED`;
- `NEEDS_TUNING`.

C001 must initialize all 100 to `PENDING_OWNER_REVIEW` and must not impersonate the owner by approving them.

Provide fields for owner notes and style/family classification without changing immutable grid truth.

## 8. Machine-verifiable release-gate matrix, PAG-1035..1049

Create `review/m10/M10_V1_GATE_MATRIX.md` and machine-readable JSON companion mapping every release-gate task to concrete evidence.

This cycle should gather/verify evidence for:

- fully offline engine;
- no GPU requirement;
- all four dimension bands;
- rectangular boards;
- seed reproduction;
- C01..C16 enforcement;
- difficulty color-band enforcement;
- MASK pass;
- RULES pass;
- WFC engine pass or explicit approved-exemplar availability status per `PAG-1044`;
- PNG/JSON round trip;
- batch generation;
- duplicate detection;
- measured 59×59 performance;
- third-party attribution audit.

Do not mark owner visual acceptance (`PAG-1050`) PASS in this cycle.

### Third-party attribution audit

Recheck `THIRD_PARTY_NOTICES.md`, `LICENSES/` and adapted-source comments against actual current production source. Report missing/extra/stale attribution facts. Do not browse/download new third-party assets as part of this review.

## 9. M04 deferred performance gate

Explicitly measure RULES at 59×59 under the fixed benchmark set.

The performance report must contain a dedicated `PAG-0441` row with:

- measured RULES 59×59 median;
- measured RULES 59×59 p95;
- peak memory;
- sample count;
- proposed RULES V1 budget and derivation;
- pass/fail against the proposed budget;
- note that final independent acceptance is owned by ChatGPT/owner, not Codex.

Do not edit the M04 tracker checkbox.

## 10. Reproducibility of reports

Machine-readable manifests/reports must use canonical deterministic serialization where practical.

Do not embed runtime timestamps, absolute local paths, random UUIDs or machine-specific temp paths in deterministic review-pack identity.

Hardware/performance reports may record human-readable environment facts separately; those environment facts must not change logical candidate identity.

Re-running review-pack generation from the same canonical definition must not create meaningless diffs.

## 11. Tests / verification required

Run and record at minimum:

- full deterministic property/fuzz corpus with explicit case count;
- all property invariant tests;
- invalid-request/batch robustness corpus;
- benchmark harness self-tests/known-answer aggregation tests;
- actual full benchmark run on the owner's current laptop;
- explicit 59×59 RULES benchmark;
- review-pack generator tests;
- actual deterministic 100-candidate review-pack generation;
- exact 25/25/25/25 difficulty-count assertion;
- review pack no-exact-duplicate assertion;
- review artifact deterministic regeneration/hash comparison;
- offline self-contained HTML/source scans;
- M10 gate-matrix generation/validation;
- relevant M07/M08/M09 regression suites;
- full `python -m pytest -q` after final edits;
- `python -m compileall -q src tests`;
- standalone package import;
- `python -m scrubbots_pixel_factory.cli --help`;
- `scrubbots-pixel --help` where installed;
- `git diff --check`;
- dependency/offline source scan;
- final scoped diff/status.

If the full property/benchmark/review generation takes longer than the normal suite, run it explicitly and record its command/result separately. Do not skip it merely because the fast suite passes.

## 12. Expected implementation/report scope

Expected changes may include:

- `tests/property/**`;
- `tests/performance/**`;
- a small project-owned `validation/` or `tools/` module if needed to share deterministic corpus/benchmark/review-pack logic;
- `review/m10/**` deterministic reports/review artifacts;
- focused README documentation;
- M10 tests;
- matching C001 builder log.

Changes to M03-M09 production algorithms are NOT expected unless a directly measured defect requires a narrowly justified correction. Broad generator tuning belongs in a separate audited remediation if necessary.

No M11 work.

## 13. Required stop conditions

Stop and report rather than hiding the result if:

- a generator violates an accepted M00-M09 logical contract under the property corpus;
- 59×59 causes an unbounded/hanging path;
- performance is so poor that the offline factory workflow is plainly impractical;
- the 100 accepted pack cannot be completed within an explicit finite attempt bound;
- a required review-pack family cannot run without inventing an exemplar;
- third-party attribution is materially incomplete;
- a proposed optimization would change accepted deterministic output without a bounded remediation plan.

A truthful FAIL/exhaustion report is better than silently relaxing quality or determinism.

## 14. Publication

Commit and push C001 implementation/tests/reports to `main` normally.

Publish the completed matching builder log.

After the final builder-log publication commit:

- `git fetch origin`;
- record local `HEAD`;
- record `origin/main`;
- record `git rev-list --left-right --count HEAD...origin/main`;
- require divergence `0 0` before stopping.

Do not edit root `TASKS.md` task acceptance state.

Do not begin owner classification on the owner's behalf.

Do not begin M11.

Stop after publication and return the C001 builder log for independent ChatGPT audit and owner-review preparation.
