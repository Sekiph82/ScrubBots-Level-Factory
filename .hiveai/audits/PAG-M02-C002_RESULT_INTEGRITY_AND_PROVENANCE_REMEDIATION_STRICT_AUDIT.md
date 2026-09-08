# PAG-M02-C002 — Result Integrity & Provenance Remediation

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Date: 2026-09-09
Auditor: ChatGPT
Cycle: `PAG-M02-C002`
Repository: `Sekiph82/ScrubBots-Level-Factory`

Audited implementation boundary:
- cycle base: `726b84ebaca39f0f32f3e970f635ab03e7925f50`
- implementation commit: `c15ea0cf1d8954fbfc12d30d3e185dffe82e5c74`
- builder-log publication commit: `7ccbc1ad3209d0e2d3f4e03d4c19127a69b33ce6`

## 1. VERDICT

**FAIL**

Two of the three C001 findings are closed:

- `F-PAG-M02-C001-002` provenance authentication: **CLOSED**
- `F-PAG-M02-C001-003` empty-string seed compatibility: **CLOSED**

One BLOCKER remains:

- **F-PAG-M02-C002-001 — BLOCKER — raw invalid GenerationResult state remains constructible through the callable `_from_validated_fields(...)` classmethod.**

The remediation removed the public raw-field `__init__`, but replaced it with a classmethod that performs the same unchecked raw field assignment. A leading underscore is a naming convention, not an integrity boundary.

M02 must not close and PAG-M03 remains blocked.

A narrowly bounded `PAG-M02-C003` remediation is required.

## 2. CONTRACT RECOVERY

C002 was authorized to remediate only:

1. invalid direct `GenerationResult` construction;
2. unauthenticated result provenance;
3. M01/M02 empty-string seed-domain inconsistency.

The target result invariant was stronger than “normal constructor raises”:

> There must be no public construction path that can produce an invalid `GenerationResult`.

The prompt also explicitly stated:

> Do not rely on naming convention alone.

and:

> If an internal private builder exists, it must not accept unvalidated external state through a normal public API.

Therefore removing `__init__` is necessary but not sufficient if another callable class API still accepts arbitrary raw fields without validation.

## 3. BRANCH / HEAD / DIFF SCOPE

Independent GitHub comparison from `726b84e...` shows exactly two C002 commits:

1. `c15ea0cf1d8954fbfc12d30d3e185dffe82e5c74` — remediation implementation
2. `7ccbc1ad3209d0e2d3f4e03d4c19127a69b33ce6` — matching builder log

Changed product/test scope is bounded to:

- `src/scrubbots_pixel_factory/core/request.py`
- `src/scrubbots_pixel_factory/core/rng.py`
- `src/scrubbots_pixel_factory/core/result.py`
- M02 request/RNG/result/determinism tests
- matching C002 builder log

No PAG-M03 implementation was introduced.

Scope result: **PASS**

## 4. ACCEPTANCE CRITERIA MATRIX

| Criterion | Result | Independent conclusion |
| --- | --- | --- |
| Empty-string GenerationRequest accepted | PASS | M02-only rejection removed. |
| Empty-string RNG deterministic | PASS | RNG typed-seed encoding supports empty string deterministically. |
| Empty string remains distinct from 0 / "0" | PASS | Seed encoding preserves type and length. |
| Stage provenance authenticated to request seed | PASS | Exact equality checked against `DeterministicRNG(request.seed).stage_seeds()`. |
| Fake well-formed stage digests rejected | PASS | Shape-only acceptance removed. |
| Missing/extra/wrong-seed stage provenance rejected | PASS | Exact stage-key/value equality enforced. |
| Retry provenance authenticated | PASS | Canonical attempt keys and deterministic retry digests validated. |
| Wrong RNG algorithm rejected | PASS | Success factory still requires exact project RNG identity. |
| Public raw `GenerationResult(...)` construction blocked | PASS | Dataclass `init=False` removes raw constructor. |
| No alternative raw-state construction API | **FAIL** | `GenerationResult._from_validated_fields(...)` is callable and performs unchecked raw assignment. |
| Success/failure type-level invariants cannot be bypassed | **FAIL** | The callable internal builder bypasses all invariants. |
| Existing golden vectors unchanged | PASS | Builder reports unchanged fixtures; remediation does not alter non-empty seed derivation. |
| No M03 work | PASS | Scope remains M02-only. |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

### Claim: direct public constructor bypass is removed

Repository truth confirms:

- `@dataclass(..., init=False)`
- no custom `__init__`
- `GenerationResult(...)` with raw fields raises `TypeError`.

This part is correct.

Disposition: **VERIFIED BUT INCOMPLETE**

### Claim: “GenerationResult will have no public raw-field construction path”

Repository truth contradicts the stronger claim.

Current source exposes:

`GenerationResult._from_validated_fields(...)`

as a classmethod.

It accepts all result-state fields:

- status
- request
- width
- height
- logical_grid
- used_palette
- generator_mode
- generator_id
- generator_version
- seed
- rng_algorithm
- provenance
- failure_code
- failure_reason

and assigns them directly with `object.__setattr__`.

It performs **zero validation**.

A normal Python caller can invoke that classmethod directly. No capability token, sentinel, validation proof object, inaccessible closure, or validating constructor prevents it.

Disposition: **REJECTED**

### Claim: provenance is authenticated

Repository truth confirms:

- only `stage_seeds` and optional `retry_seeds` are accepted;
- exact five stage keys required;
- stage values compared to `DeterministicRNG(request.seed).stage_seeds()`;
- retry keys must be canonical non-negative decimal strings;
- retry values compared to exact deterministic retry derivation.

Disposition: **VERIFIED**

### Claim: M01 seed domain restored

Repository truth confirms empty-string rejection was removed from both request and RNG.

Typed RNG material encodes:

`string:0:`

for empty string, remaining distinct from integer/string-zero forms.

Disposition: **VERIFIED**

## 6. FILE / SYMBOL EVIDENCE

### `core/request.py`

The empty-string prohibition is removed.

The request still rejects bool and non-int/non-string seeds.

Canonical typed serialization remains unambiguous.

Result: **PASS**

### `core/rng.py`

Empty string is accepted and deterministically encoded.

Existing non-empty seed/RNG behavior is preserved.

Retry derivation remains deterministic and now safely encodes attempts beyond 128-bit range without altering normal existing vectors.

Result: **PASS**

### `core/result.py::_validate_provenance`

Significantly improved.

It now validates:

- supported provenance field set;
- exact stage names;
- digest shape;
- exact deterministic stage values for request seed;
- optional canonical retry attempt keys;
- exact deterministic retry values.

Result: **PASS**

### `core/result.py::GenerationResult`

The raw `__init__` bypass is removed.

However:

`GenerationResult._from_validated_fields(...)`

remains a directly callable classmethod and blindly constructs state.

Conceptually, a caller can still execute:

```python
GenerationResult._from_validated_fields(
    status=ResultStatus.SUCCESS,
    request=None,
    width=1,
    height=1,
    logical_grid=("C17",),
    used_palette=(),
    generator_mode="MASK",
    generator_id=None,
    generator_version=None,
    seed=1,
    rng_algorithm=None,
    provenance=None,
    failure_code=None,
    failure_reason=None,
)
```

The method will allocate and return that invalid object because its body contains assignment only.

The leading underscore does not enforce access control in Python.

Result: **FAIL**

## 7. FOCUSED TEST EVIDENCE

Builder reports:

- focused remediation/M02 suite: `53 passed`
- full repository regression: `113 passed`

These are builder evidence, not final proof.

The added tests correctly cover:

- raw `GenerationResult(...)` constructor rejection;
- stage provenance tampering;
- missing/extra/wrong-seed stage provenance;
- retry provenance tampering;
- empty-string request/RNG behavior;
- cross-process empty-string stability.

Critical missing adversarial test:

- direct call to `GenerationResult._from_validated_fields(...)` with invalid raw state.

The source itself proves that such a call remains possible.

Passing tests cannot override this direct contract violation.

## 8. REGRESSION EVIDENCE

No regression was found in already-validated M02 Request/RNG/golden behavior.

Builder reports existing golden fixtures unchanged.

The C002 code does not introduce M03+ architecture.

Result: **PASS**

## 9. SECURITY / SAFETY / OFFLINE REVIEW

Positive:

- zero runtime network dependency preserved;
- no global randomness introduced;
- no shell execution introduced;
- provenance trust is materially stronger.

Integrity issue:

A future generator or caller can bypass the core result trust boundary through the unchecked classmethod.

This remains a core integrity/security-of-state issue.

Result: **FAIL**

## 10. ARCHITECTURE CONSISTENCY

The remediation is narrow and otherwise architecturally correct.

The remaining issue is specifically the construction boundary: validated factories are still not the exclusive practical path to a result object.

Result: **FAIL at result construction boundary only**

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Positive:

- C002 log was created before source edits;
- failures/corrections were preserved;
- no self-audit;
- no task acceptance files modified by Codex;
- implementation commit and equality checkpoint recorded;
- no self-referential terminal log SHA behavior.

One process note:

The builder used a temporary stash to preserve pre-existing control-plane edits despite earlier governance guidance strongly preferring no stash operations. The log records this transparently and reports that the stash remains for recovery. This did not affect product scope and is not an M02 acceptance blocker.

Result: **PASS with NOTE**

## 12. FINAL REPOSITORY STATE

C002 implementation commit:

`c15ea0cf1d8954fbfc12d30d3e185dffe82e5c74`

C002 builder-log commit:

`7ccbc1ad3209d0e2d3f4e03d4c19127a69b33ce6`

The remediation is published but not accepted as M02 closure.

## 13. OPEN CROSS-MILESTONE FINDINGS

### F-PAG-M02-C002-001 — BLOCKER

**Unchecked raw result construction remains available through `GenerationResult._from_validated_fields(...)`.**

Affected:

`src/scrubbots_pixel_factory/core/result.py`

Current incorrect behavior:

An externally callable classmethod accepts every raw result field and assigns them without validation.

Target behavior:

No ordinary callable API on `GenerationResult` may accept arbitrary unvalidated raw result state.

Validated success/failure construction must be the only supported executable construction path.

A private helper must not be “private” only by underscore naming while remaining a raw public classmethod.

## 14. DEFECTS BY SEVERITY

### BLOCKER

- F-PAG-M02-C002-001

### MAJOR

None.

### MINOR

None.

### NOTE

- C001 provenance finding is closed.
- C001 seed-domain finding is closed.
- Builder used a reversible stash to preserve unrelated local control-plane edits; no product impact observed.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

A clean fix can be very small.

Preferred options include:

- module-private closure/helper not exposed as a class attribute, with construction gated by an unforgeable module-private capability checked by `__new__`/`__init__`; or
- a validating constructor used by factories, so even direct calls cannot create invalid state; or
- another design where all externally reachable creation routes enforce the same invariants.

The next cycle must not broaden M02 architecture.

## 16. UNVERIFIED ITEMS

Exact builder Windows `113 passed` command was not independently rerun.

The remaining BLOCKER does not depend on test-environment uncertainty; it is directly visible in committed source.

## 17. REGRESSION RISK

**LOW**

Only a narrow construction-boundary fix remains.

## 18. AUDIT CONFIDENCE

**HIGH**

The remaining defect is a direct source-level bypass, not an inference from builder logs.

## 19. FINAL VERDICT

**FAIL**

`PAG-M02-C002` is not accepted.

Closed findings:

- `F-PAG-M02-C001-002`
- `F-PAG-M02-C001-003`

Remaining finding:

- `F-PAG-M02-C002-001` — BLOCKER

PAG-M03 remains blocked.

## 20. REQUIRED REMEDIATION

Create one final bounded cycle:

`PAG-M02-C003 — Result Construction Boundary Remediation`

Required work only:

1. remove the externally callable unchecked raw-state builder;
2. ensure every ordinary executable `GenerationResult` construction path enforces invariants or is inaccessible without a true internal capability;
3. add an adversarial test specifically targeting every internal/raw construction path;
4. preserve authenticated provenance and empty-string seed fixes;
5. preserve all golden hashes/RNG vectors;
6. rerun focused M02 + full regression;
7. do not begin PAG-M03.
