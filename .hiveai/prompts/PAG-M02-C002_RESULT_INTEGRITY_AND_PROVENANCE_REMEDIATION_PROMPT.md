# PAG-M02-C002 — Result Integrity & Provenance Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M02-C001_DETERMINISTIC_GENERATION_CORE_STRICT_AUDIT.md`

Previous implementation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M02-C001_DETERMINISTIC_GENERATION_CORE_PROMPT.md`

## 1. Scope

This is a **bounded PAG-M02 remediation cycle**.

Do not reimplement the already-validated request/RNG/golden core.

Do not begin PAG-M03 or any production generator family.

Open findings:

- `F-PAG-M02-C001-001` — BLOCKER — public `GenerationResult` constructor bypasses validation.
- `F-PAG-M02-C001-002` — MAJOR — provenance is shape-validated but not authenticated.
- `F-PAG-M02-C001-003` — MINOR — M02 silently narrowed the M01 string-seed domain.

Open task IDs:

- `PAG-0206`
- `PAG-0222`
- `PAG-0223`
- `PAG-0224`
- `PAG-0225`
- `PAG-0226`
- `PAG-0227`
- `PAG-0228`

All other M02 task IDs are already independently validated. Preserve them.

## 2. GitHub authority

GitHub is the sole task/prompt/audit authority.

Repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Do not discover work from sibling local folders.

Do not modify the main `Sekiph82/Scrubbots` repository.

If using the owner's Windows mirror, synchronize only the authorized Level Factory checkout with safe fetch + fast-forward and preserve unrelated local changes.

## 3. Mandatory reads

Before the first product edit, read completely:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. C001 implementation prompt
9. C001 builder log
10. C001 strict audit
11. current `core/request.py`
12. current `core/rng.py`
13. current `core/result.py`
14. current M02 result/golden/determinism tests
15. this prompt

## 4. Matching builder log

Create **before the first source/product edit**:

`.hiveai/codex-logs/PAG-M02-C002_RESULT_INTEGRITY_AND_PROVENANCE_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M02-C002 — Result Integrity & Provenance Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- start timestamp;
- authority/prompt/audit URLs;
- branch/start HEAD/origin/status;
- synchronization evidence;
- files/contracts read;
- exact remediation design;
- material commands;
- failed tests/commands and corrections;
- focused adversarial result tests;
- provenance-authentication tests;
- seed-domain tests;
- golden regression;
- full regression;
- implementation commit SHA(s);
- push result and local/remote equality checkpoint;
- final changed-file summary.

Do not try to record the log file's own terminal commit SHA.

## 5. Finding F-PAG-M02-C001-001 — BLOCKER

### Problem

`GenerationResult.success(...)` and `GenerationResult.failure(...)` validate correctly, but the class also exposes a public custom `__init__` that blindly assigns all fields.

A caller can therefore bypass the factories and construct invalid states such as:

- SUCCESS with `request=None`;
- SUCCESS with C17/BG01;
- SUCCESS with wrong grid length;
- SUCCESS with no generator version;
- SUCCESS with arbitrary seed/RNG/provenance;
- FAILURE with a partial grid;
- FAILURE without a reason.

This violates the M02 type-level guarantee that a `GenerationResult` is an immutable validated success/failure result.

### Required target behavior

There must be **no public construction path** that can produce an invalid `GenerationResult`.

The supported public creation API should remain:

- `GenerationResult.success(...)`
- `GenerationResult.failure(...)`

or an equivalently strict API.

### Preferred implementation direction

A safe design is:

- keep `@dataclass(frozen=True, slots=True, init=False)`;
- remove the public validating-bypass constructor;
- use a private/internal classmethod/helper that allocates via `object.__new__` and assigns already-validated frozen fields;
- have only the validated success/failure factories call that internal builder.

Equivalent designs are acceptable if direct `GenerationResult(...)` cannot create arbitrary state.

Do not rely on naming convention alone. A public constructor accepting raw fields is not acceptable.

### Required adversarial tests

Add tests proving:

1. direct public construction with raw result fields is impossible;
2. no invalid SUCCESS can be produced with:
   - wrong grid length;
   - C17;
   - BG01;
   - invalid dimensions;
   - missing request;
   - wrong mode;
   - wrong seed;
   - missing generator version;
3. no invalid FAILURE can carry:
   - logical grid;
   - dimensions;
   - fake used palette;
   - missing/blank reason;
4. success/failure factory outputs remain frozen/deeply immutable;
5. canonical success/failure serialization remains byte-stable.

Do not test only that the factories reject bad input; test that the class itself has no bypass route.

## 6. Finding F-PAG-M02-C001-002 — MAJOR

### Problem

Current provenance validation verifies only:

- provenance is a mapping;
- `stage_seeds` contains the five expected keys;
- each value matches a lowercase 64-hex format.

It does not verify that those values are the actual deterministic stage seeds for the request.

A valid grid can therefore be paired with five fabricated all-zero SHA-shaped strings and still be accepted.

### Required target behavior

For every successful result:

`provenance.stage_seeds`

must equal the project-owned deterministic derivation for the exact request seed and the recorded project RNG algorithm.

At minimum compare against:

`DeterministicRNG(request.seed).stage_seeds()`

using the exact M02 algorithm/version.

If provenance supplies retry metadata, validate it deterministically too.

### Provenance contract

Keep the contract bounded to M02.

Required:

- `stage_seeds` exactly five M02 stage keys;
- each stage value exactly equals expected deterministic value;
- extra/missing/incorrect stage values rejected;
- project RNG algorithm must equal the supported M02 algorithm;
- if `retry_seeds` is present:
  - it must be a deterministic mapping;
  - attempt keys must represent non-negative integer attempts canonically;
  - values must equal `DeterministicRNG(request.seed).retry_seed(attempt)`;
  - malformed/duplicate-equivalent attempt keys fail closed.

Do not invent WFC/MASK/RULES-specific provenance yet.

### Required adversarial tests

Add tests proving rejection of:

- all-zero but well-formed stage digests;
- one altered stage digest;
- missing stage;
- extra stage;
- stage seeds from a different request seed;
- wrong RNG algorithm;
- malformed retry attempt key;
- retry seed from the wrong attempt;
- retry seed derived from another master seed.

Also prove correct stage/retry provenance remains accepted and canonical.

## 7. Finding F-PAG-M02-C001-003 — MINOR

### Problem

M01 defines project selection seeds as:

- integer excluding bool;
- string.

M01 does not reject the empty string.

M02 currently rejects `""` in both:

- `GenerationRequest`;
- `DeterministicRNG`.

That silently narrows an already accepted project contract.

### Required target behavior

For this remediation, preserve M01 compatibility:

- accept `""` as a valid string seed;
- keep integer/string type distinction;
- continue rejecting bool and non-int/non-string types;
- canonical typed seed serialization must encode empty string unambiguously;
- M02 RNG must derive a deterministic stable stream from empty string.

Do not change M01 in this cycle.

### Required tests

Prove:

- empty-string GenerationRequest constructs;
- empty-string canonical seed is `{"type":"string","value":""}`;
- empty-string RNG is deterministic;
- empty string differs from integer `0`, string `"0"`, and other seeds;
- cross-process/hash-seed behavior remains stable.

## 8. Golden compatibility

The C001 independent audit reproduced all four golden fixtures exactly.

The remediation should not change valid deterministic outputs unless a genuine contract correction makes change unavoidable.

Expected outcome:

- existing four M02 golden fixtures remain unchanged;
- existing RNG known vector remains unchanged;
- existing valid request canonical bytes remain unchanged;
- existing valid result canonical hashes remain unchanged.

If any golden changes, explain precisely why and do not silently regenerate fixtures to make tests green.

## 9. Required result-construction architecture checks

Before handoff, explicitly inspect and log:

- `GenerationResult.__init__` public signature/behavior;
- all internal call sites constructing `GenerationResult`;
- all production source references to `GenerationResult(`;
- all test/support references.

A source scan should prove no product/test generator bypasses the validated public factories.

If an internal private builder exists, it must not accept unvalidated external state through a normal public API.

## 10. Regression requirements

Run:

- focused result integrity tests;
- focused provenance tests;
- focused request/seed tests;
- all M02 request/RNG/result/interface tests;
- all four golden fixture tests;
- cross-process/hash-randomization tests;
- full repository pytest regression;
- standalone import;
- `pip check`;
- no-network/no-global-random static policy checks;
- `git diff --check`.

The previous builder baseline was:

- M02 focused: 39 PASS
- full repository: 99 PASS

The new suite should grow because adversarial tests are being added.

## 11. Security / safety

Preserve:

- zero runtime dependencies;
- offline-only runtime;
- no network imports in M02 core;
- no global `random`;
- no `hash()` determinism;
- no shell execution;
- no arbitrary executable deserialization;
- no main ScrubBots runtime dependency.

The result integrity fix must reduce, not widen, the trusted construction surface.

## 12. Prohibited shortcuts

Do not:

- simply rename `__init__` parameters and leave bypass possible;
- leave a public `unsafe=True` or `validate=False` path;
- accept fake provenance because it has correct length/hex format;
- remove provenance from results to avoid validating it;
- regenerate golden fixtures without explaining a legitimate deterministic contract change;
- begin PAG-M03;
- add production generator implementations;
- modify ChatGPT-owned task/tracker/audit state;
- self-audit.

## 13. Builder exit criteria

Builder may stop as **implementation complete / pending independent audit** only when:

- direct invalid `GenerationResult` construction is impossible;
- success/failure invariants are type-level enforced;
- provenance stage seeds are authenticated against request/RNG;
- supplied retry provenance is authenticated;
- empty-string seed is M01-compatible and deterministic;
- all existing golden vectors remain valid unless explicitly justified;
- full regression passes;
- no M03+ implementation exists;
- matching C002 builder log is published;
- implementation commit(s), push result, and equality checkpoint are recorded.

Do not close M02. ChatGPT will independently re-audit and record terminal repository HEAD.
