# SB-LF04-001-C001 — Define Versioned LevelMetrics

Document role: CODEX IMPLEMENTATION PROMPT

Repository:
https://github.com/Sekiph82/ScrubBots-Level-Factory

Branch:
`main`

Task:
`SB-LF04-001 — Define versioned LevelMetrics.`

Audit criteria:
`.hiveai/audit-criteria/SB-LF04-001-C001_VERSIONED_LEVEL_METRICS_CONTRACT_AUDIT_CRITERIA.md`

Expected builder log:
`.hiveai/codex-logs/SB-LF04-001-C001_VERSIONED_LEVEL_METRICS_CONTRACT_CODEX_LOG.md`

Do not edit root `TASKS.md`.

## Read before implementation

- root `TASKS.md`;
- `AGENTS.md`;
- `GOVERNANCE.md`;
- M03 final closure summary:
  `.hiveai/audits/SB-LF03-M03_FINAL_CLOSURE_SUMMARY.md`;
- accepted:
  - `src/scrubbots_pixel_factory/solver_evidence.py`;
  - `src/scrubbots_pixel_factory/solver_budget.py`;
  - `src/scrubbots_pixel_factory/solution_analysis.py`;
  - `src/scrubbots_pixel_factory/compact_solver_state.py`;
  - exact Level Data / canonical bridge contracts;
- current production difficulty/dimension contracts:
  - `src/scrubbots_pixel_factory/contracts/difficulty.py`;
  - `src/scrubbots_pixel_factory/contracts/production.py`;
- migration mapping showing SB-LF04-001 is PARTIAL historical evidence, not already closed.

## Mission

Create a dedicated Factory-side versioned LevelMetrics V1 contract.

This is a **data-contract task**, not a scoring task.

The contract must be ready for SB-LF04-002..012 without calculating those later metrics now.

## Recommended module

Create a dedicated module such as:

`src/scrubbots_pixel_factory/level_metrics.py`

Do not bury the contract inside Studio UI or generator code.

## Contract design

Define:
- explicit schema string;
- integer schema version;
- immutable/frozen structures;
- exact LevelData source SHA-256;
- exact canonical `SolverStateAuthority` or accepted equivalent authority structure;
- solver evidence schema/version + digest;
- metrics contract/version identity;
- analysis disposition enum;
- deterministic canonical_dict / canonical_bytes / digest.

Use closed parsing/import validation if a parser is exposed.

### Metric fields

You may define typed optional fields/catalog entries for metrics explicitly listed in M04 tasks, but leave them `None`/absent in SB-LF04-001 unless supplied by tests as already-observed values.

Do not calculate:
- solution depth;
- move count;
- forced moves;
- dependency depth;
- slot pressure;
- bait/deadlock;
- volatility;
- Challenge Score.

Those belong to later tasks.

Do not introduce an unrestricted `dict[str, float]` metrics bag.

If a generic representation is necessary, use a closed versioned MetricId enum/catalog restricted to canonical M04-planned IDs with strict value types.

## Analysis dispositions

Represent at least:
- AVAILABLE;
- INCONCLUSIVE;
- UNAVAILABLE;
- ERROR.

Rules:
- unavailable/error/inconclusive cannot silently become zero metrics;
- missing metric is not zero;
- Challenge Score is not available merely because LevelMetrics exists.

## Evidence binding

For AVAILABLE metrics require exact:
- LevelData source hash;
- gameplay authority;
- solver evidence schema/version/digest.

No caller-supplied “verified=true” boolean is sufficient by itself.

This task does not need to invoke gameplay. It consumes/records accepted identity values from already-produced M03 evidence.

## Difficulty and production invariants

Preserve:
- production width/height 20..59 independently;
- rectangular boards legal;
- difficulty class independent from board size;
- used colors 3..12 production legality independent from difficulty;
- no class-band resurrection.

If LevelMetrics carries descriptive difficulty metadata, prove changing only that metadata does not transform solver-derived measurements.

## Canonical exclusions

Never serialize into canonical LevelMetrics identity:
- elapsed seconds;
- wall-clock timestamps;
- operational timeout seconds/occurrence;
- absolute filesystem paths;
- process/object IDs;
- UI state.

## Tests

Create focused SB-LF04-001 tests covering every audit criterion.

Include explicit negative cases:
- wrong evidence digest format;
- unknown schema/version;
- unknown metric ID/field;
- measurement attached to forbidden disposition;
- NaN/Infinity if floats exist;
- mutable-input alias attempt;
- difficulty metadata changed while same evidence stays identical in measurement content;
- width/color count not used as difficulty inference.

Run:
- focused SB-LF04-001;
- retained M03 tests;
- relevant existing difficulty/production contract tests;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- Level Factory Godot headless editor boot;
- `git diff --check`;
- `git diff --exit-code -- TASKS.md`.

Record exact counts/skips/warnings.

## Publication

1. Create builder log before product edits.
2. Implement product/tests/docs.
3. Run gates.
4. Commit/push implementation + builder log.
5. Finalize builder log with implementation SHA and results.
6. Publish terminal log-only commit.
7. STOP for independent ChatGPT audit.

Do not create audit files or remediation prompts.
