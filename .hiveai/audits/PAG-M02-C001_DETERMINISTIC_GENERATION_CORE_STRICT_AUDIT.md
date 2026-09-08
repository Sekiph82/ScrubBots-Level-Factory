# PAG-M02-C001 — Deterministic Generation Core

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-08  
Auditor: ChatGPT  
Cycle: `PAG-M02-C001`  
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation boundary:
- cycle base: `71628ca822689be3d1305580a631981bac909c0c`
- implementation commit: `c30227e264e1cc9c09daa80273eb14613bbb7b6d`
- builder-log publication commit: `e5274894725209834849b59d43be9999b2f31f9a`

Current repository HEAD at audit time also contains later control-plane-only commit:
`03803ac106a3484b6b8d78c8ffae4b73d6705e7f`

That later commit is not attributed to the M02 builder implementation scope.

## 1. VERDICT

**FAIL**

M02 is substantially correct, but the core `GenerationResult` contract is not actually fail-closed.

Three findings remain:

- **F-PAG-M02-C001-001 — BLOCKER — public GenerationResult constructor bypasses all success/failure validation.**
- **F-PAG-M02-C001-002 — MAJOR — result provenance is shape-validated but not authenticated against the request seed/project RNG.**
- **F-PAG-M02-C001-003 — MINOR — M02 rejects the empty-string seed even though the M01 project seed domain accepts strings without that restriction.**

PAG-M03 must remain blocked.

A bounded `PAG-M02-C002` remediation is required.

## 2. CONTRACT RECOVERY

M02 was required to establish:

- immutable/versioned `GenerationRequest`;
- canonical request serialization;
- one project-owned deterministic RNG abstraction;
- deterministic stage and retry derivation;
- common generator interface;
- immutable **validated** `GenerationResult`;
- explicit success/failure semantics;
- no partially valid production output represented as success;
- deterministic canonical result bytes;
- golden fixtures for EASY/MEDIUM/HARD/VERY_HARD;
- reproducibility independent of Python hash randomization.

No production MASK/RULES/WFC/HYBRID engine was authorized.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub inspection confirms the builder's M02 scope is bounded to:

- `src/scrubbots_pixel_factory/core/request.py`
- `src/scrubbots_pixel_factory/core/rng.py`
- `src/scrubbots_pixel_factory/core/generator.py`
- `src/scrubbots_pixel_factory/core/result.py`
- `src/scrubbots_pixel_factory/core/__init__.py`
- package-root exports
- test-only deterministic probe
- focused M02 tests
- four golden fixtures
- matching builder log

No production M03+ generator implementation was introduced.

After the builder log commit, `03803ac...` changed only H!veAI control-plane files and does not alter M02 product code.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Task / criterion | Result | Independent conclusion |
| --- | --- | --- |
| PAG-0201 immutable/versioned GenerationRequest | PASS | Frozen/slotted request plus deep option freezing. |
| PAG-0202 schema version | PASS | v1 schema/version represented canonically. |
| PAG-0203 difficulty | PASS | Reuses strict M01 Difficulty. |
| PAG-0204 optional width | PASS | Explicit axis validated; omission supported. |
| PAG-0205 optional height | PASS | Explicit axis validated; omission supported. |
| PAG-0206 seed | PARTIAL | Int/string typed serialization works, but empty string is rejected contrary to M01's accepted string seed domain. |
| PAG-0207 generator mode | PASS | Strict MASK/RULES/WFC/HYBRID; AUTO absent. |
| PAG-0208 optional style/theme | PASS | Optional nonblank strings. |
| PAG-0209 requested palette subset | PASS | Reuses M01 validation and canonical ordering. |
| PAG-0210 versioned generator options | PASS | Deep immutable namespace/version/values structure. |
| PAG-0211 canonical request serialization | PASS | Compact UTF-8 sorted-key JSON, typed seeds, finite values. |
| PAG-0212 project-owned deterministic RNG | PASS | SHA-256 counter/domain-separated RNG. |
| PAG-0213 no uncontrolled global randomness | PASS | No production random usage found. |
| PAG-0214 deterministic stage sub-seeds | PASS | Five named stage seeds and streams derive deterministically. |
| PAG-0215 RNG algorithm/version metadata | PASS | `SCRUBBOTS_SHA256_COUNTER_V1` recorded. |
| PAG-0216 same seed/config same grid | PASS | Golden/probe behavior independently reproduced. |
| PAG-0217 byte-identical canonical JSON | PASS | Canonical result hash reproduced independently. |
| PAG-0218 different seeds can differ | PASS | Probe/test contract supports distinct output. |
| PAG-0219 deterministic retry seeds | PASS | Attempt-indexed derivation independent of consumption. |
| PAG-0220 hash-randomization independence | PASS | Serialization/algorithms avoid Python hash ordering; builder cross-process evidence is consistent with source. |
| PAG-0221 common PixelGenerator interface | PASS | Protocol exists with explicit project RNG parameter. |
| PAG-0222 GenerationResult | FAIL | Class can be directly constructed without validation. |
| PAG-0223 exact width×height grid required | FAIL | Factory enforces; public constructor does not. |
| PAG-0224 canonical C-ID cells required | FAIL | Factory enforces; public constructor can accept C17/BG01/arbitrary grid. |
| PAG-0225 generator mode/version required | FAIL | Factory enforces; public constructor bypasses. |
| PAG-0226 seed/provenance required | FAIL | Direct constructor bypasses; provenance authenticity also not verified. |
| PAG-0227 explicit failure reason | FAIL | Failure factory enforces, but public constructor can create invalid failure state. |
| PAG-0228 never partial/invalid success | FAIL | Direct constructor allows invalid SUCCESS state. |
| PAG-0229 four difficulty golden fixtures | PASS | All four golden vectors independently reproduced exactly. |
| PAG-0230 same-request reruns byte-identical | PASS | Deterministic algorithms/golden hashes independently confirmed. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: deterministic RNG known vector

Builder test expects:

`DeterministicRNG(123, "root").next_u64() == 801623960106958567`

Independent reimplementation from the committed algorithm produced exactly:

`801623960106958567`

Claim disposition: **VERIFIED**

### Claim: four golden fixtures are stable

The auditor independently reimplemented the committed M01 selection rules plus M02 SHA-256 counter RNG and the test-only probe algorithm.

For all four fixtures, the following independently matched the committed fixture:

- resolved dimensions;
- selected palette;
- all five stage seeds;
- grid SHA-256;
- canonical result SHA-256.

Results:

- EASY: 5/5 match
- MEDIUM: 5/5 match
- HARD: 5/5 match
- VERY_HARD: 5/5 match

Claim disposition: **VERIFIED**

### Claim: GenerationResult is validated

This claim is **not true for the public class contract**.

`GenerationResult.success(...)` and `GenerationResult.failure(...)` perform substantial validation.

However, `GenerationResult` defines a public custom `__init__` whose body only assigns fields with `object.__setattr__`.

That constructor does not validate:

- status;
- request type;
- dimensions;
- grid length;
- logical C-IDs;
- used-color band;
- generator mode;
- generator version;
- seed;
- RNG algorithm;
- provenance;
- failure code/reason;
- success/failure mutual exclusivity.

Therefore callers can bypass both validated factories.

Claim disposition: **REJECTED**

### Claim: provenance is reproducible/validated

`_validate_provenance()` requires exactly the five stage names and requires each value to look like a 64-character lowercase hex digest.

It does **not** compare those values to:

`DeterministicRNG(request.seed).stage_seeds()`

A valid successful grid can therefore be paired with arbitrary fake stage digests such as all-zero SHA-shaped strings and still pass provenance validation.

Claim disposition: **PARTIAL / NOT ACCEPTED AS AUTHENTIC PROVENANCE**

## 6. FILE / SYMBOL EVIDENCE

### `core/request.py`

Positive:

- frozen/slotted request;
- nested generator option mappings become mapping proxies;
- lists/tuples become immutable tuples;
- nonfinite floats rejected;
- non-string mapping keys rejected;
- typed seed representation distinguishes `1` and `"1"`;
- request canonical JSON uses `sort_keys=True`, compact separators, UTF-8, `allow_nan=False`;
- explicit dimensions fail closed;
- explicit palette subset reuses M01 legality.

Finding:

- empty string seed is rejected by M02 although M01's `validate_seed()` accepted any string.

Result: **PASS except F-003**

### `core/rng.py`

Positive:

- explicit immutable algorithm identity;
- SHA-256 counter stream;
- domain separation;
- no Python `random` or `hash()`;
- rejection-sampled `randbelow`;
- deterministic choice/shuffle;
- child/stage streams do not consume parent;
- deterministic stage/retry seed derivation;
- invalid bounds/attempts fail closed.

Independent known-vector and stage-seed checks matched exactly.

Result: **PASS**

### `core/generator.py`

Protocol is narrow and does not introduce production engines.

Result: **PASS**

### `core/result.py`

Positive factory behavior:

- `success()` checks request, dimensions, explicit-axis match, grid length, logical C-IDs through M01, used-color band, requested subset containment, RNG identity, mode match, generator identity/version, seed match, provenance shape.
- `failure()` uses stable codes and no grid.
- canonical result bytes are compact/sorted/finite JSON.
- factory-created provenance is deep-frozen.

Blocking design defect:

The public `GenerationResult.__init__` bypasses all of the above.

Example invalid states currently constructible through the public constructor include conceptually:

- SUCCESS + `request=None`
- SUCCESS + `logical_grid=("C17",)`
- SUCCESS + width/height not matching grid length
- SUCCESS + missing generator version
- SUCCESS + arbitrary provenance
- FAILURE + `failure_reason=None`
- FAILURE + partial grid

The class therefore does not satisfy “immutable validated GenerationResult” as a type-level invariant.

Result: **FAIL**

### Provenance authenticity

`_validate_provenance(value)` validates only shape/hex format.

It has no access to the request and cannot verify stage values against the master seed.

Result: **FAIL**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- focused M02: `39 passed`
- full repository: `99 passed`

The auditor treats these as builder evidence, not proof.

Independent verification completed:

- RNG known vector reproduced;
- all four golden fixture dimensions reproduced;
- all four golden palettes reproduced;
- all 20 committed stage-seed vectors reproduced;
- all four grid hashes reproduced;
- all four canonical result hashes reproduced.

Existing tests do not cover:

1. direct public `GenerationResult(...)` construction with invalid state;
2. valid success grid + fake but hex-shaped stage provenance;
3. M01/M02 empty-string seed-domain consistency.

Those missing adversarial tests correspond directly to the findings.

## 8. REGRESSION EVIDENCE

M00/M01 architecture remains intact:

- no runtime dependencies added;
- no network imports;
- no production generator family introduced;
- M01 palette/difficulty contracts reused;
- offline architecture untouched;
- no main-game runtime dependency.

Builder reports full suite `99 PASS`; direct source inspection found no M00/M01 regression.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- no network/API dependency;
- no global randomness;
- no shell execution in production core;
- no pickle/eval/exec;
- deterministic canonical serialization;
- no main-game runtime access.

Integrity risk:

A future production generator can instantiate `GenerationResult` directly and bypass fail-closed validation. This is a core trust-boundary issue, not merely style.

Result: **FAIL due result integrity**

## 10. ARCHITECTURE CONSISTENCY

Request/RNG/interface layering is clean and appropriately stops before M03.

The test-only probe is correctly under `tests/support/`.

The primary architecture inconsistency is that the validated result factories are optional rather than being the only construction path.

Result: **FAIL only at result construction boundary**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- matching log existed before product edits;
- previous process ordering defect is corrected;
- no self-audit;
- no task acceptance mutation;
- implementation commit and equality checkpoint are recorded;
- terminal log SHA is correctly left to independent Git/H!veAI rather than self-reference.

Independent GitHub truth:

- product commit = `c30227e264e1cc9c09daa80273eb14613bbb7b6d`
- builder-log commit = `e5274894725209834849b59d43be9999b2f31f9a`
- later control-plane-only commit = `03803ac106a3484b6b8d78c8ffae4b73d6705e7f`

Result: **PASS**

## 12. FINAL REPOSITORY STATE

Current GitHub HEAD at audit time:

`03803ac106a3484b6b8d78c8ffae4b73d6705e7f`

The later HEAD changes only H!veAI project-control files and does not remediate the M02 result defects.

M02 product implementation remains at:

`c30227e264e1cc9c09daa80273eb14613bbb7b6d`

Result: **PUBLISHED, NOT ACCEPTED**

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M02-C001-001 — BLOCKER

**Public GenerationResult construction bypasses every result invariant.**

Affected:

`src/scrubbots_pixel_factory/core/result.py::GenerationResult.__init__`

Current incorrect behavior:

The constructor blindly assigns caller values.

Target behavior:

Every externally constructible `GenerationResult` instance must satisfy the success/failure invariants. The only practical public creation paths should be validated success/failure factories or an equally strict constructor.

### F-PAG-M02-C001-002 — MAJOR

**Provenance stage digests are not verified against the request seed/RNG algorithm.**

Affected:

`src/scrubbots_pixel_factory/core/result.py::_validate_provenance`

Current incorrect behavior:

Any five correctly named 64-character lowercase hex strings are accepted.

Target behavior:

For a successful result, stage provenance must match the deterministic stage derivation for the exact request seed and project RNG algorithm.

If retry provenance is supplied, it must also be structurally and deterministically validated.

### F-PAG-M02-C001-003 — MINOR

**M02 seed domain is stricter than M01 without an owner-approved contract change.**

Affected:

- `core/request.py`
- `core/rng.py`

Current behavior:

empty string seed is rejected.

M01 project contract accepts `int | str` and does not reject `""`.

Target behavior:

Either restore M01-compatible string seed acceptance or, if empty strings are intentionally prohibited, first make that an explicit owner-approved contract change rather than silently narrowing the domain in M02.

For this remediation, preserve the existing owner-approved M01 domain and accept empty string deterministically.

## 14. DEFECTS BY SEVERITY

### BLOCKER

- F-PAG-M02-C001-001

### MAJOR

- F-PAG-M02-C001-002

### MINOR

- F-PAG-M02-C001-003

### NOTE

The exact builder `99 passed` command was not independently rerun in the auditor container because the repository cannot be cloned there due outbound GitHub DNS restrictions. Deterministic core/golden outputs were independently reproduced from repository source instead.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking after remediation:

- consider a private internal result builder helper to avoid repeating field assignment;
- provenance can be formalized into a small immutable typed structure rather than an open mapping in a later bounded core cleanup;
- M03+ generators should never call `GenerationResult` internals directly.

## 16. UNVERIFIED ITEMS

Exact Windows full-suite execution is builder evidence only.

No golden deterministic vector remains unverified.

## 17. REGRESSION RISK

**MEDIUM**

Fixing the result construction boundary is foundational and must preserve canonical bytes/golden fixtures where valid behavior is unchanged.

## 18. AUDIT CONFIDENCE

**HIGH**

Evidence includes:

- direct GitHub source/diff inspection;
- exact commit-scope inspection;
- independent RNG known-vector reproduction;
- independent reproduction of all four golden fixture dimensions/palettes/stage seeds/grid hashes/result hashes;
- direct type-construction and provenance-validation source analysis;
- tracker/control-plane inspection.

## 19. FINAL VERDICT

**FAIL**

`PAG-M02-C001` is not accepted.

M02 remains active in remediation state.

Validated Request/RNG/determinism work should be preserved.

PAG-M03 remains blocked.

## 20. REQUIRED REMEDIATION

Create bounded cycle:

`PAG-M02-C002 — Result Integrity & Provenance Remediation`

Required work only:

1. make invalid direct `GenerationResult` construction impossible or equally validated;
2. authenticate provenance against request seed/project RNG;
3. validate retry provenance when supplied;
4. restore M01-compatible empty-string seed behavior;
5. add direct-constructor bypass tests;
6. add fake-provenance rejection tests;
7. add empty-string seed deterministic request/RNG tests;
8. rerun all M02 golden/canonical hashes and full regression;
9. do not change valid golden outputs unless a genuine invariant correction requires it;
10. do not begin PAG-M03.
