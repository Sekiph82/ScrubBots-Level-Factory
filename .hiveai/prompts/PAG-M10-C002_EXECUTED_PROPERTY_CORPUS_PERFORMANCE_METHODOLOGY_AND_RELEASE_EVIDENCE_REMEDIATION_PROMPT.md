# PAG-M10-C002 — Executed Property Corpus, Performance Methodology & Release Evidence Remediation
Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`
Canonical current-state tracker: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md`

Previous strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M10-C001_VALIDATION_PERFORMANCE_AND_V1_REVIEW_PACK_PREPARATION_STRICT_AUDIT.md`

Previous builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M10-C001_VALIDATION_PERFORMANCE_AND_V1_REVIEW_PACK_PREPARATION_CODEX_LOG.md`

## 1. Mission

Close only the five C001 findings:

- `F-PAG-M10-C001-001` — the >=2,000 request corpus is serialized but not actually executed as a property-validation corpus;
- `F-PAG-M10-C001-002` — performance p95/budgets use repeated identical requests instead of a fixed distinct deterministic seed/config set;
- `F-PAG-M10-C001-003` — owner-review attempt/diversity/metrics/selection evidence is incomplete;
- `F-PAG-M10-C001-004` — V1 gate matrix omits PAG-1035..PAG-1049;
- `F-PAG-M10-C001-005` — C001 builder-log creation/start chronology was not reliable.

Preserve every accepted M00-M09 contract and preserve the useful C001 M10 foundation.

Do not begin M11. Do not ask the owner to visually approve the 100-candidate pack in this cycle. PAG-1033, PAG-1034 and PAG-1050 remain owner/ChatGPT gates after independent technical PASS.

## 2. Current authority / builder boundary

Root `TASKS.md` is the only current project-state authority.

Codex is builder only. Do not edit root task checkboxes/status. Do not author an independent audit. Do not mark PAG-0441, PAG-1048 or any owner-only gate accepted.

Authorized local mirror only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never use or modify:
`C:\Users\sekip\Desktop\ScrubBots`

Synchronize non-destructively from GitHub `main` before edits.

## 3. Matching builder log is a hard pre-edit gate

Before the FIRST C002 source/test/report edit create:

`.hiveai/codex-logs/PAG-M10-C002_EXECUTED_PROPERTY_CORPUS_PERFORMANCE_METHODOLOGY_AND_RELEASE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M10-C002 — Executed Property Corpus, Performance Methodology & Release Evidence Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

The log must truthfully record the actual current GitHub authority tip, local HEAD, origin/main, divergence, timestamp and local dirt. Do not copy a prior cycle timestamp/base. Confirm the file exists before any C002 source/test/report edit.

Record commands/results chronologically, including slow/failing benchmark cases.

## 4. Preserve C001 review pack foundation where possible

Preserve unless an evidence correction requires change:

- exactly 100 accepted owner-review candidates;
- exactly 25 EASY, 25 MEDIUM, 25 HARD, 25 VERY_HARD;
- all owner statuses `PENDING_OWNER_REVIEW`;
- MASK/RULES/non-WFC HYBRID visual coverage;
- `WFC_VISUAL_PACK_SKIPPED_NO_APPROVED_EXEMPLAR`;
- zero exact duplicates;
- offline/self-contained HTML;
- no production generator modification.

Do not silently change logical review grids merely to make a report easier.

## 5. Execute the property corpus, do not only serialize it

Create/version a deterministic valid request corpus with at least 2,000 requests.

The committed M10 validation command must actually execute every request in the advertised executed corpus through the accepted generation surface. The corpus may be revised from C001 to keep runtime practical, but the report and tests must truthfully distinguish:

- corpus definitions;
- executed generation cases;
- successful results;
- accepted domain failures/retry exhaustions where valid generator requests can legitimately fail;
- mode/difficulty counts.

For every successful result directly validate:

- resolved/requested width/height;
- exact width*height cell count;
- every cell C01..C16;
- difficulty distinct-color band;
- actual used palette equals ascending used C-ID subset;
- no BG01 logical cell;
- same request reproducibility for the exercised deterministic contract.

Required coverage:

- all four difficulties;
- explicit square and rectangular dimensions;
- auto dimensions;
- MASK, RULES, HYBRID, AUTO and technical synthetic-fixture WFC coverage;
- explicit valid 59x59 generation cases;
- deterministic request/corpus identity.

Do not make all 2,000 cases expensive WFC/HYBRID cases merely to satisfy a count. It is acceptable to weight the large corpus toward faster valid generator paths while keeping direct bounded representative coverage for all slower modes. The machine report must state the distribution honestly.

### Invalid corpus

Actually execute the committed invalid cases, including at minimum:

- invalid dimension boundaries;
- unsupported difficulty;
- unsupported mode;
- bool/invalid seed;
- malformed/unsupported options;
- palette/difficulty conflicts;
- malformed CLI/batch configuration;
- bounded batch invalid-input behavior with no uncontrolled traceback/state corruption.

## 6. Replace repeated-request timing with a fixed distinct benchmark set

C001 raw performance data remains historical evidence. Create a new benchmark version for C002.

Define a committed/versioned deterministic benchmark manifest containing distinct seed/config identities. Do not compute p95 from repeated runs of one identical request and call it seed-set p95.

### 6.1 Core mode/difficulty seed-set measurements

For MASK, RULES and each non-WFC HYBRID strategy used in production review, measure a fixed set of at least 20 DISTINCT deterministic seed/config cases per difficulty for the representative workload.

Each sample must retain:

- seed;
- request digest/config identity;
- dimensions;
- status/failure;
- quality decision/codes;
- elapsed generation time;
- peak tracemalloc memory;
- attempts/retries where applicable;
- grid hash on success.

Compute median and nearest-rank p95 across the distinct measured sample set.

Warmup runs may occur, but warmups are not measured samples and must not replace distinct cases.

### 6.2 WFC and WFC-bearing HYBRID

Use only tracked synthetic fixtures for technical performance evidence.

Measure bounded DISTINCT deterministic cases across all four difficulties for WFC. Use a practical fixed set of at least 10 distinct cases per difficulty unless the existing accepted WFC bound makes that prohibitively slow; if a smaller set is objectively necessary, document the reason and do not overstate p95 confidence.

Measure both WFC-bearing HYBRID strategies beyond EASY. At minimum include each strategy at representative EASY, MEDIUM, HARD and VERY_HARD with distinct bounded cases sufficient to expose contradiction/failure rate and timing.

Do not hide RETRY_EXHAUSTED or contradictions. Report them in the denominator.

### 6.3 RULES 59x59 / PAG-0441

This is a hard dedicated dataset.

Measure at least 20 DISTINCT deterministic RULES 59x59 seed/config cases. Use a precommitted/versioned seed/config set, not seeds selected after seeing speed.

Record:

- each raw sample;
- success/failure;
- recipe/style/config identity;
- median;
- nearest-rank p95;
- peak memory;
- quality rejection rate;
- proposed V1 RULES 59x59 budget;
- explicit derivation/headroom.

PAG-0441 remains pending independent audit even if all samples fit the proposed budget.

## 7. Budget methodology

Do not make the pass test tautological.

A proposed budget may use a documented measured-data rule such as p95 plus explicit headroom, but:

- calculate p95 over distinct deterministic cases;
- state sample count and coverage;
- keep measured maximum visible;
- explain why the headroom is suitable for the offline factory workflow;
- do not label the proposal owner-approved;
- do not set `inside_budget=true` merely because the budget was mathematically derived from the same maximum without explaining what the flag means.

Publish raw samples and summaries in `M10_PERFORMANCE_REPORT.json` and a useful Markdown report.

## 8. Repair owner-review metrics and selection authority

Publish exactly:

- `review/m10/M10_METRICS_REPORT.json`
- `review/m10/M10_METRICS_REPORT.md`

These reports must include:

- total generation attempts used to build the fixed 100 pack;
- ACCEPT count;
- rejection count/rate;
- ordered rejection-code distribution;
- exact duplicate count/rate;
- duplicate relations if any;
- mode/difficulty counts;
- family/recipe/strategy counts where applicable;
- aggregate structural M07 quality metrics;
- deterministic near-duplicate evidence using M07 occupancy similarity and color-layout similarity separately;
- nearest-neighbor or equivalent diversity summary sufficient to detect an overly repetitive pack;
- zero-grid-mutation statement.

If every review slot succeeds on its first deterministic request, still publish an explicit 100-attempt ledger with empty rejection/duplicate relations rather than implying the selection process did not exist.

### Root seed / selection rules

The review manifest must truthfully define root seed/config/version and selection rules.

You may preserve all current logical grids by correcting the declared seed authority if the existing per-slot seed formula can be truthfully derived from a documented root namespace. Do not claim a root seed that is not actually used.

Record the exact deterministic formula mapping review root/version/difficulty/slot to request seed/config and candidate ID.

## 9. Improve owner review HTML only as needed

Keep it offline and self-contained.

Make the owner-facing index clearly navigable/grouped by difficulty and mode/family/strategy. Every card must display enough local information for review:

- candidate ID;
- difficulty;
- mode;
- family/recipe/strategy where relevant;
- seed;
- dimensions;
- grid hash;
- PENDING_OWNER_REVIEW state.

Do not use CDN/network/external fonts/images/CSS.

## 10. Build the actual PAG-1035..1049 release-gate matrix

`M10_V1_GATE_MATRIX.json` and `.md` must enumerate every release gate PAG-1035 through PAG-1049 individually.

For each include:

- task ID/name;
- machine evidence status such as `EVIDENCE_READY`, `PENDING_INDEPENDENT_ACCEPTANCE`, or an explicit technical blocker;
- exact evidence files/tests/metrics supporting the gate;
- notes where synthetic WFC technical evidence substitutes for an unavailable approved production exemplar as allowed by PAG-1044.

Required special handling:

- PAG-1048 must remain `PENDING_INDEPENDENT_ACCEPTANCE` until the repaired multi-seed 59x59 performance dataset receives ChatGPT/owner acceptance;
- PAG-1049 must bind to concrete THIRD_PARTY_NOTICES/LICENSES/adapted-source-comment evidence;
- owner-only PAG-1033/PAG-1034/PAG-1050 remain separately `PENDING_OWNER_REVIEW` and must not be mixed with machine PASS.

## 11. Third-party attribution reaudit depth

Preserve the no-new-dependency/no-copied-artwork boundary.

Strengthen `M10_THIRD_PARTY_ATTRIBUTION_REAUDIT.json` to explicitly record for each referenced upstream project:

- expected pinned source URL/commit;
- notice/license presence;
- whether current production contains copied/substantially adapted source requiring notice;
- adapted-source comment evidence where applicable;
- stale/missing/extra finding list.

Do not browse/download new third-party assets.

## 12. Tests / verification required

Run and record at minimum:

- full executed >=2,000 valid property corpus command with actual executed count;
- property invariant summary by mode/difficulty;
- invalid corpus execution and batch robustness;
- distinct multi-seed benchmark generation;
- per-mode/per-difficulty performance validation;
- WFC/WFC-bearing HYBRID failure-rate evidence;
- 20+ distinct RULES 59x59 dataset;
- benchmark aggregation known-answer tests;
- required M10 metrics report tests;
- exact 100 candidate / 25-25-25-25 / pending-owner / no-exact-duplicate checks;
- M07 near-duplicate/diversity report checks;
- review manifest root/selection reproducibility check;
- review HTML offline/grouping/card-local evidence tests;
- PAG-1035..1049 gate matrix completeness check;
- third-party reaudit completeness check;
- deterministic regeneration byte comparison for deterministic logical review artifacts;
- relevant M07/M08/M09 regressions;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- package import;
- module and installed CLI help;
- offline/dependency/source scan;
- `git diff --check`;
- final scoped diff/status.

Performance artifacts are naturally machine-dependent; do not require byte-identical timing values across reruns. Their benchmark definition/seed manifest must be deterministic, while observed times are evidence from the owner's laptop.

## 13. Scope boundary

Expected changes are limited to:

- M10 tool/validation code;
- tests/property/**, tests/performance/** and M10 integration tests;
- review/m10/**;
- focused M10 README docs;
- matching C002 builder log.

Do not modify M03-M09 production algorithms unless a newly executed property corpus reveals a real accepted-contract defect. If such a defect appears, STOP and report it for a separate bounded remediation rather than silently fixing production algorithms inside C002.

Do not begin M11.

## 14. Stop conditions

Stop and report rather than hiding evidence if:

- the executed property corpus exposes an M00-M09 contract violation;
- a benchmark family is unbounded/hanging;
- measured performance makes the offline workflow clearly impractical;
- the 100-candidate pack cannot be reproduced without changing logical grids;
- attribution evidence is genuinely missing.

## 15. Completion / publication

Commit and push C002 normally to `main`.

Publish the completed matching builder log.

After publication fetch origin and verify/record:

- local HEAD;
- origin/main;
- exact equality;
- divergence `0 0`.

Do not edit root `TASKS.md` acceptance state.
Do not self-audit.
Do not mark owner gates complete.

Stop after publication and return the C002 builder log for independent ChatGPT strict audit.
