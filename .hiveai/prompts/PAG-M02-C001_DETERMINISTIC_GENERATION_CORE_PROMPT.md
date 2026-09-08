# PAG-M02-C001 — Deterministic Generation Core

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M01-C001_CANONICAL_SCRUBBOTS_CONTRACTS_STRICT_AUDIT.md`

## 1. Objective

Implement and prove **PAG-M02 — Deterministic Generation Core** only.

M02 establishes:

1. immutable/versioned `GenerationRequest`;
2. canonical request serialization;
3. one project-owned deterministic RNG abstraction;
4. deterministic stage sub-seeds and retry seeds;
5. common generator interface;
6. immutable validated `GenerationResult`;
7. explicit failure semantics;
8. deterministic core/golden fixtures proving reproducibility.

Do not begin PAG-M03, PAG-M04, PAG-M05, PAG-M06, PAG-M07, PAG-M08, or PAG-M09.

Do not implement a production MASK, RULES, WFC, HYBRID, AUTO router, CLI, PNG writer, artifact exporter, quality filter, or Godot integration.

## 2. Authority and repository boundary

GitHub is the sole task/prompt/audit authority.

Implementation repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

The main `Sekiph82/Scrubbots` repository is read-only contract reference only if a current M01 contract question requires comparison. Do not modify it.

Do not discover work by searching local sibling folders.

If running on the owner's Windows machine, synchronize only the authorized Level Factory mirror using safe fetch + fast-forward. Preserve unrelated local edits.

## 3. Mandatory control-plane read order

Before product edits, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. M01 C001 strict audit
9. current M01 contract source under `src/scrubbots_pixel_factory/contracts/`
10. current M00 offline source/tests
11. this prompt

## 4. Mandatory Codex log

Create **before the first source/product edit**:

`.hiveai/codex-logs/PAG-M02-C001_DETERMINISTIC_GENERATION_CORE_CODEX_LOG.md`

Exact H1:

`# PAG-M02-C001 — Deterministic Generation Core`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- authority URL;
- starting branch, HEAD, origin, ahead/behind, status;
- synchronization;
- mandatory documents read;
- architecture decisions;
- exact source/data/test files changed;
- every material command;
- failed commands/tests and corrections;
- deterministic/property/golden evidence;
- full regression evidence;
- security/offline evidence;
- implementation commit SHA(s);
- implementation push result;
- observed local/remote equality checkpoint;
- final source/log diff summary.

### Important correction to prior log protocol

Do **not** attempt to make the log contain its own final log-file commit SHA.

That requirement is self-referential because adding a commit SHA to the log changes the commit SHA again.

Instead:

- record all implementation/product commit SHA(s) in the log;
- record push/equality checkpoints available before the log publication commit;
- publish the completed log in one final log commit;
- stop;
- ChatGPT/H!veAI will independently record the terminal repository HEAD after publication.

Do not create an extra commit merely to write the previous log commit SHA into the log.

## 5. Builder-only boundary

Codex must not:

- audit its own work;
- declare M02 PASS/CLOSED;
- edit task checkbox/state in `tasks.md`;
- edit `.hiveai/HANDOFF.md`;
- edit `.hiveai/CYCLE_INDEX.md`;
- edit `.hiveai/STATE.json`;
- append acceptance events to `.hiveai/EVENTS.jsonl`;
- create/edit `.hiveai/audits/**`;
- rewrite prior prompt/log/audit history.

ChatGPT owns acceptance and tracker transitions.

## 6. PAG-S02.1 — GenerationRequest

Implement tasks `PAG-0201..PAG-0211`.

Expected module:

`src/scrubbots_pixel_factory/core/request.py`

Exact module layout may vary if cleaner, but keep M02 core separate from M01 contracts and later generator families.

### Required request properties

`GenerationRequest` must be:

- immutable;
- versioned;
- deeply immutable, not merely a frozen dataclass containing mutable dict/list objects;
- generator-independent;
- validated on construction;
- canonical-serialization safe.

Required information:

- request schema/version;
- `difficulty`;
- optional explicit `width`;
- optional explicit `height`;
- master `seed`;
- `generator_mode`;
- optional style/theme information;
- optional requested canonical palette subset;
- generator-specific options in an explicitly versioned namespace.

### Generator modes

Define a core enum for explicit future modes:

- `MASK`
- `RULES`
- `WFC`
- `HYBRID`

Do not implement `AUTO` yet. M06 owns AUTO after explicit modes are stable.

Do not implement the generator engines behind these names.

### Difficulty / dimensions

Reuse M01:

- `Difficulty`;
- dimension validation;
- explicit requested palette-subset validation.

If explicit width or height is supplied, validate that axis immediately against difficulty.

An omitted axis may remain unresolved in the immutable request and be deterministically resolved later by core stage resolution.

Do not silently clamp an illegal dimension.

### Seed contract

Accept the same deliberate seed domain used by project contracts:

- integer excluding bool;
- string.

Preserve the distinction between integer `1` and string `"1"`.

Reject other seed types.

### Style / theme

Use explicit optional immutable string fields or one clearly documented immutable style/theme structure.

Reject empty/whitespace-only identifiers if present.

Do not add an art-style catalog yet; that belongs to later generator milestones.

### Requested palette subset

If supplied:

- validate through M01 canonical subset rules for the request difficulty;
- store as immutable canonical ascending tuple;
- reject BG01, duplicates, off-palette IDs, and incompatible sizes.

Do not auto-fix an illegal requested subset.

### Versioned generator options

Define a narrow immutable structure such as `GeneratorOptions` containing:

- namespace;
- schema/version;
- canonical values.

Values must be deeply immutable/canonicalizable.

Allowed nested values should be deliberately bounded to deterministic JSON-compatible types.

If floats are allowed:

- reject NaN and infinities;
- canonicalization must remain byte-stable on supported Python 3.12.

Reject:

- sets;
- arbitrary objects;
- bytes unless explicitly encoded by a documented stable format;
- mappings with non-string keys;
- mutable objects escaping into the stored request.

### Canonical request serialization

Provide canonical request object/bytes/JSON.

Requirements:

- UTF-8;
- deterministic field representation;
- deterministic mapping-key order;
- no incidental whitespace;
- no Python object repr;
- seed type encoded so int/string seeds cannot collide semantically;
- generator options with different input dictionary key order serialize identically;
- canonical palette subset order;
- same logical request = byte-identical canonical request JSON;
- illegal/non-canonical values fail rather than serialize ambiguously.

A stable request digest/hash may be added if narrowly useful.

Do not define the M08 final generator artifact schema here.

## 7. PAG-S02.2 — Project deterministic RNG

Implement tasks `PAG-0212..PAG-0220`.

Expected module:

`src/scrubbots_pixel_factory/core/rng.py`

### Algorithm

Use one project-owned deterministic algorithm with an explicit immutable identity/version.

Preferred architecture:

**SHA-256 counter/domain-separated RNG**, not Python module-global `random`.

Example identity:

`SCRUBBOTS_SHA256_COUNTER_V1`

The exact name may differ, but must be persisted in metadata/tests.

Do not rely on:

- global `random`;
- Python `hash()`;
- set/dict iteration order;
- OS entropy;
- timestamps;
- UUID randomness;
- process IDs;
- network state.

### Required RNG API

Provide a minimal, testable abstraction suitable for future generators.

At minimum support deterministic equivalents of:

- next fixed-width unsigned value or bytes;
- `randbelow(n)` with valid positive bound;
- deterministic choice from an ordered sequence;
- deterministic shuffle/permutation of an ordered sequence;
- derived child stream/domain;
- stable stage sub-seed derivation;
- stable retry-seed derivation.

If `randbelow` is implemented from digest integers, use rejection sampling or another unbiased documented method rather than obvious modulo bias.

### Named stage domains

Derive deterministic, distinct stage seeds/streams for at least:

- `dimension`
- `palette`
- `geometry`
- `colorization`
- `post_processing`

Stage derivation must be:

- deterministic;
- domain-separated;
- independent of call order between unrelated stages;
- recorded in metadata/provenance used by core results.

### Retry derivation

Provide explicit deterministic retry derivation by attempt index.

Requirements:

- retry 0/1/2... produce stable distinct retry seeds/streams;
- same request + attempt = same retry seed;
- no dependence on prior failed RNG consumption;
- no dependence on Python hash randomization.

### M01 transition

Do not delete or broadly rewrite M01 `_stable_select.py` in this milestone unless required for a narrow compatibility adjustment.

M02 RNG becomes the future core randomness authority.

For deterministic request resolution/probe tests, stage sub-seeds may be supplied into M01 dimension/palette resolution helpers, or equivalent M02 core resolution may reuse M01 validators.

Avoid maintaining two competing production RNG systems after M02.

Document which helper is transitional.

## 8. PAG-S02.3 — Common generator interface

Implement tasks `PAG-0221..PAG-0228`.

Expected modules may include:

`src/scrubbots_pixel_factory/core/generator.py`  
`src/scrubbots_pixel_factory/core/result.py`

### PixelGenerator interface

Define a clear common interface/protocol/ABC for future generator engines.

It must not contain actual MASK/RULES/WFC logic.

The contract must make deterministic RNG ownership explicit.

A future engine must not be able to silently create uncontrolled global randomness.

For example, the interface may receive:

- immutable `GenerationRequest`;
- project-owned RNG/context.

Exact signature is architectural, but document it.

### GenerationResult

Define an immutable result contract.

A successful result must require:

- success state;
- request/core schema version as appropriate;
- resolved width and height;
- exact `width * height` row-major logical grid;
- only canonical C01..C16 logical IDs;
- legal actual-used-color count for difficulty;
- actual used palette in ascending canonical order;
- generator mode;
- generator implementation/version identifier;
- original master seed;
- deterministic RNG algorithm/version metadata;
- deterministic provenance sufficient for M02 reproduction;
- no BG01 logical cells.

A failed result must require:

- explicit stable failure code/reason;
- no successful logical grid;
- no partially valid production output represented as success.

Do not let failure objects carry a misleading partial production grid.

### Success validation

The core success constructor/factory must fail closed on:

- wrong grid length;
- illegal C-ID;
- BG01;
- used-color count outside difficulty band;
- illegal dimensions;
- request/result mode mismatch;
- missing generator version;
- malformed provenance/RNG metadata.

Do not trust a future generator implementation to self-certify its own result.

### Failure semantics

Define stable generic failure codes appropriate to the core, for example:

- invalid request;
- generation failed;
- contract violation;
- retry exhausted.

Do not invent detailed WFC/MASK/RULES-specific failure enums yet.

A deterministic detail/message may exist, but canonical behavior must not depend on nondeterministic exception reprs.

## 9. Canonical core result representation

Tasks `PAG-0216` and `PAG-0217` require deterministic grid and canonical JSON evidence.

Define a **core deterministic result serialization** for testing/reproduction.

This is not the final M08 artifact/export schema.

Requirements:

- success/failure canonical representation;
- deterministic mapping order;
- row-major cell order;
- typed seed representation;
- RNG algorithm/version;
- stable provenance fields;
- same result = byte-identical JSON;
- request/options input key-order cannot affect result bytes.

Name/document it clearly as M02 core canonical serialization so M08 remains free to define the production artifact schema later.

## 10. Test-only deterministic contract probe

M02 acceptance requires deterministic grid/golden evidence before real generator families exist.

Create a **test-only** generator under `tests/support/` or equivalent.

Example:

`DeterministicContractProbeGenerator`

Rules:

- test/support only;
- never exported as production generator;
- never described as MASK/RULES/WFC;
- must implement the common `PixelGenerator` interface;
- must use only project-owned RNG/stage streams;
- must resolve legal dimensions/palette using the request + M01/M02 contracts;
- must produce a simple deterministic legal row-major grid;
- must ensure every selected used color actually appears;
- must not resize/interpolate/image-process anything;
- must not call network/global random;
- must not become a production fallback.

Its purpose is only to prove M02 core determinism and interface/result contracts.

## 11. Golden deterministic fixtures — PAG-0229

Create at least one fixed golden fixture for each:

- EASY
- MEDIUM
- HARD
- VERY_HARD

Fixtures should be compact and reviewable.

Preferred contents:

- canonical request JSON/object;
- expected resolved dimensions;
- expected actual palette;
- expected RNG algorithm/version;
- expected stage-seed identifiers/digests as appropriate;
- expected logical-grid SHA-256;
- expected canonical core-result SHA-256.

You do not need to commit enormous full-grid JSON fixtures if stable hashes plus deterministic fixture requests provide stronger, smaller golden evidence.

Golden fixtures must fail if deterministic core behavior drifts unexpectedly.

## 12. Determinism and hash-randomization tests

Required focused tests include:

### Request
- deeply immutable;
- nested caller-owned mapping/list mutation after construction cannot alter request;
- canonical JSON identical for differently ordered input mappings;
- int seed 1 differs from string seed "1";
- invalid NaN/inf/noncanonical option values rejected if relevant;
- explicit illegal dimensions rejected;
- explicit illegal palette rejected;
- strict mode validation;
- schema/version included.

### RNG
- same seed/domain = same sequence;
- different seeds can differ;
- different domains differ;
- fixed known-answer vectors for algorithm/version;
- `randbelow` bounds;
- deterministic choice;
- deterministic shuffle;
- named stage sub-seeds stable/distinct;
- retry seeds stable/distinct;
- invalid bounds fail closed.

### Result
- valid success accepted;
- wrong grid length rejected;
- C17/BG01/off-palette rejected;
- illegal used-color count rejected;
- mode mismatch rejected;
- failure requires reason;
- failure has no partial production grid;
- result deeply immutable;
- canonical result JSON byte-stable.

### Cross-process
Run fixed deterministic probe requests in fresh subprocesses with different `PYTHONHASHSEED` values and compare exact canonical bytes/digests.

Same request must remain byte-identical.

### Different seeds
At least one fixed probe request pair with different seeds must produce distinct logical output/core-result hash.

Do not assert every pair of arbitrary seeds must differ.

## 13. Offline/security regression

All M00 and M01 tests must remain green.

M02 code must:

- operate offline;
- introduce no runtime network dependency;
- not import network libraries;
- not use global random;
- not access main ScrubBots checkout at runtime;
- not execute shell commands from production code;
- not deserialize arbitrary executable objects;
- not allow mutable request/result state to leak.

Run the existing source-policy/offline tests against all new production modules.

## 14. Canonical serialization safety

For any JSON serialization:

- use `allow_nan=False`;
- canonical separators/order;
- UTF-8;
- no locale dependence;
- no timestamp;
- no machine path;
- no memory address;
- no unordered set representation;
- no exception repr as canonical state.

Tests must prove options mapping insertion order cannot alter canonical bytes.

## 15. Prohibited shortcuts

Do not:

- start MASK/RULES/WFC implementation;
- create AUTO mode;
- create production fake generator;
- use module-global `random`;
- use Python `hash()` for deterministic output;
- use timestamps/UUID entropy;
- make a frozen dataclass that still exposes mutable nested dict/list state;
- accept partial success;
- silently repair illegal generated grids;
- resize/interpolate source art;
- define M08 final export/artifact schema;
- update ChatGPT-owned task/tracker/audit state;
- self-audit.

## 16. Required verification

Before handoff, run and log:

- focused request tests;
- focused RNG tests;
- focused result/interface tests;
- golden fixture tests;
- cross-process/hash-randomization tests;
- full repository pytest regression;
- standalone package import;
- `pip check`;
- package metadata/build dry run;
- no-network source-policy regression;
- no-global-random static check for production generator/core modules;
- `git diff --check`.

Record exact totals and failures/corrections.

## 17. M02 acceptance

M02 may be handed to ChatGPT as implementation complete / pending independent audit only when:

- `PAG-0201..PAG-0230` all have implementation/test evidence;
- four difficulty golden fixtures exist;
- same request reruns are byte-identical on supported environment;
- cross-process `PYTHONHASHSEED` variation does not change canonical bytes;
- different seed evidence demonstrates distinct output;
- retries are deterministic and call-order independent;
- result success/failure invariants fail closed;
- M00/M01 regressions remain green;
- no M03+ production generator implementation exists;
- matching builder log is published;
- implementation commit(s), push result, and equality checkpoint are logged.

Do not mark tasks complete. Do not mutate H!veAI acceptance state. ChatGPT will perform the independent strict audit and record the terminal repository HEAD.
