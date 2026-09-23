# SB-LF04-001-C001 — Versioned LevelMetrics Contract — Audit Criteria

Document role: CHATGPT STRICT AUDIT CRITERIA

## Task

`SB-LF04-001 — Define versioned LevelMetrics.`

## Purpose

Create the canonical Factory-side versioned LevelMetrics data contract that later M04 tasks populate from accepted M03 solver evidence.

This task defines the envelope, identity, provenance, availability semantics and deterministic serialization.

It does **not** define Difficulty V1 Challenge Score and does not invent new gameplay-derived metrics.

## Accepted upstream truth

M03 is COMPLETE / VERIFIED.

Accepted source contracts include:
- `SolverEvidenceReport` / `SolverMetrics`;
- `BudgetedSolverResult`;
- `SolutionCountResult`;
- exact Level Data V1 source identity;
- canonical gameplay authority identity;
- operational timeout excluded from canonical solver truth.

Historical production contracts also require:
- width/height independently legal in 20..59;
- difficulty class is classification metadata, not board-size truth;
- used-color count does not define difficulty;
- lane/class must not transform the art or solver evidence.

## Required LevelMetrics V1 envelope

The implementation must define a closed, immutable, versioned LevelMetrics contract with at least:

1. schema identifier + integer schema version;
2. exact LevelData/source identity, using a strict SHA-256 field already accepted by Factory contracts;
3. canonical gameplay authority identity;
4. exact solver-evidence identity:
   - accepted solver evidence schema/version;
   - solver evidence digest;
5. analysis disposition/status that distinguishes at minimum:
   - AVAILABLE;
   - INCONCLUSIVE;
   - UNAVAILABLE;
   - ERROR;
6. deterministic metric-contract identity/version;
7. deterministic canonical serialization + SHA-256 digest;
8. optional/nullable metric slots may be reserved only for metrics explicitly scheduled in M04, but this task must not calculate them.

## Metric-slot scope

It is acceptable for V1 to define typed optional slots that later tasks populate, including planned M04 families such as:
- solution depth / move count;
- states visited;
- dead ends;
- branching;
- forced moves;
- dependency depth;
- slot pressure;
- bait/deadlock;
- volatility;
- solution count/entropy references;
- future Challenge Score result/reference.

But SB-LF04-001 itself must not derive or calculate those values.

Unset metrics must remain explicitly absent, not fabricated zero.

Do not create free-form arbitrary metric names that can silently become a second truth system. Prefer closed typed fields or a closed versioned metric-id enum/catalog.

## Provenance requirements

Every AVAILABLE LevelMetrics object must be bound to:
- one exact LevelData/source identity;
- one exact canonical gameplay authority;
- one exact canonical solver-evidence digest/version.

If evidence is unavailable/inconclusive/error, the envelope must preserve that truth and must not fabricate measurements.

Operational telemetry such as elapsed wall-clock time or timeout seconds must never enter canonical LevelMetrics bytes/digest.

## Difficulty separation

LevelMetrics must not:
- infer EASY/MEDIUM/HARD/VERY_HARD from width or height;
- infer difficulty from used-color count;
- map a board to a difficulty class;
- define Challenge Score coefficients;
- implement campaign/lane rhythm;
- use historical class-specific dimension bands as current production truth.

If difficulty metadata is carried for lineage, it must be descriptive input metadata only and must not change metric values or canonical evidence identity.

## Closed schema / validation

Fail closed on:
- unknown schema/version;
- malformed SHA-256;
- malformed authority;
- invalid evidence schema/version/digest;
- unknown top-level fields in parsing/import;
- illegal metric types/ranges;
- metric values present when disposition forbids them;
- NaN/Infinity if any float field is introduced;
- arbitrary unversioned extension metrics.

Input mutable mappings/lists must be copied/frozen.

## Determinism

Same semantic input must produce byte-identical canonical serialization and digest.

Dictionary insertion order, runtime timestamps, absolute paths, object IDs and elapsed time must not affect canonical bytes.

## Architecture constraints

Do not:
- modify canonical gameplay logic;
- call ProofKernel/SolvabilitySolver directly merely to compute M04 metrics in this task;
- implement SB-LF04-002..009;
- implement Challenge Score;
- modify art source;
- modify LevelData source;
- modify root TASKS.md as builder;
- use WFC metrics as gameplay difficulty truth;
- use provider/network calls or credits for tests.

## Required tests

At minimum:

1. deterministic canonical bytes/digest;
2. exact LevelData identity binding;
3. exact authority binding;
4. exact solver evidence identity binding;
5. AVAILABLE with all metric slots absent is legal if this task only defines the contract;
6. unavailable/inconclusive/error cannot carry fabricated measurements;
7. unknown fields/version fail closed;
8. malformed hashes/types fail closed;
9. mutable input cannot mutate accepted object after construction;
10. elapsed time/operational timeout cannot enter canonical serialization;
11. same source/evidence under different descriptive difficulty class metadata does not alter solver-derived measurement content;
12. dimensions/used-color count are not interpreted as difficulty;
13. retained M03 regression suite stays green;
14. full repository pytest green;
15. compileall PASS;
16. Godot headless editor boot PASS;
17. `git diff --check` PASS;
18. `git diff --exit-code -- TASKS.md` PASS.

## Audit blockers

BLOCKER examples:
- LevelMetrics becomes an independent gameplay truth source;
- fabricated metrics on unavailable/inconclusive evidence;
- current difficulty inferred from dimensions/color count;
- operational timeout enters canonical metrics identity;
- gameplay source mutation.

MAJOR examples:
- incomplete evidence/source binding;
- open/free-form unversioned metrics;
- nondeterministic canonical bytes;
- parser accepts unknown fields;
- mutable input aliases retained.

## Acceptance

PASS only when LevelMetrics V1 is a deterministic, provenance-bound data contract ready for later M04 population tasks without preempting their semantics.
