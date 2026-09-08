# PAG-M02-C003 — Result Construction Boundary Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`

Previous independent strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M02-C002_RESULT_INTEGRITY_AND_PROVENANCE_REMEDIATION_STRICT_AUDIT.md`

Previous remediation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M02-C002_RESULT_INTEGRITY_AND_PROVENANCE_REMEDIATION_PROMPT.md`

## 1. Scope

This is the final bounded M02 remediation for exactly one remaining BLOCKER:

`F-PAG-M02-C002-001 — unchecked raw GenerationResult construction remains available through GenerationResult._from_validated_fields(...)`.

Do not rework already-validated Request, RNG, provenance authentication, empty-string seed behavior, golden fixtures, interface, or canonical serialization.

Do not begin PAG-M03.

Open M02 task IDs remain:

- `PAG-0222`
- `PAG-0223`
- `PAG-0224`
- `PAG-0225`
- `PAG-0226`
- `PAG-0227`
- `PAG-0228`

`PAG-0206` is already closed by C002.

## 2. GitHub authority

GitHub is the sole task/prompt/audit authority.

Repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Do not modify the main ScrubBots repository.

Do not discover tasks from sibling local folders.

## 3. Mandatory reads

Before the first product edit, read:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md`
7. `GOVERNANCE.md`
8. C002 builder log
9. C002 strict audit
10. current `core/result.py`
11. current M02 result/interface/golden tests
12. this prompt

## 4. Matching builder log

Create before the first source edit:

`.hiveai/codex-logs/PAG-M02-C003_RESULT_CONSTRUCTION_BOUNDARY_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M02-C003 — Result Construction Boundary Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- authority URLs;
- start HEAD/status;
- synchronization;
- files read;
- exact boundary design;
- source changes;
- material commands;
- failed attempts and corrections;
- adversarial construction tests;
- focused M02 tests;
- golden regression;
- full regression;
- implementation commit SHA;
- push/equality checkpoint;
- final changed-file summary.

Do not record the log file's own terminal commit SHA.

## 5. Remaining BLOCKER

### Current problem

C002 correctly removed raw `GenerationResult(...)` construction.

However, `GenerationResult._from_validated_fields(...)` remains a callable classmethod accepting every raw result field and assigning them with `object.__setattr__` without validation.

A leading underscore is not access control.

The C002 prompt explicitly prohibited relying on naming convention alone.

### Required target behavior

After C003, there must be no ordinary callable class/module API that accepts arbitrary raw result fields and returns a `GenerationResult` without enforcing the success/failure invariants.

The supported public construction API remains:

- `GenerationResult.success(...)`
- `GenerationResult.failure(...)`

Equivalent strict public factories are acceptable, but no unsafe/raw factory may be available as a normal callable API.

## 6. Acceptable architecture

Preferred simplest solution:

**Make construction itself validating.**

For example:

- keep the public factories;
- move common already-validated field assignment into a mechanism that cannot be called with arbitrary raw state without validation;
- or implement a constructor/new path that requires an internal non-forgeable capability and rejects ordinary direct invocation.

A module-level helper with a leading underscore is not enough if callers can import/call it with arbitrary raw fields.

A classmethod with a leading underscore is not enough.

A public `unsafe`, `raw`, `validate=False`, or test-only bypass is forbidden.

Do not depend only on documentation or naming.

## 7. Strong preferred design

The most reviewable design is one where **all result creation ultimately passes through one invariant validator**.

Possible pattern:

1. one internal validation function validates a complete candidate state;
2. success/failure factories prepare candidate state;
3. one constructor/allocation route validates or requires a capability created only after validation;
4. direct ordinary construction either:
   - is impossible, or
   - performs the same invariant validation.

The key acceptance property is behavioral, not naming.

## 8. Required adversarial tests

Add tests that enumerate every construction path found in production source.

At minimum prove:

1. `GenerationResult(...)` cannot create arbitrary raw state;
2. `GenerationResult._from_validated_fields(...)` no longer exists as a callable unchecked path, or cannot return invalid state;
3. any replacement internal helper cannot be called through a normal API to produce:
   - SUCCESS with `request=None`;
   - SUCCESS with C17;
   - SUCCESS with BG01;
   - SUCCESS with wrong grid length;
   - SUCCESS with wrong dimensions;
   - SUCCESS with missing generator version;
   - SUCCESS with wrong seed;
   - SUCCESS with fake provenance;
   - FAILURE with a grid;
   - FAILURE with dimensions;
   - FAILURE without a reason;
4. `success(...)` still accepts valid output;
5. `failure(...)` still accepts valid failure;
6. success/failure remain frozen/deeply immutable;
7. canonical bytes for valid existing fixtures remain unchanged.

## 9. Source-surface audit required from builder

Before completion, perform and log a source scan for:

- `GenerationResult(`
- `GenerationResult.`
- `object.__new__(GenerationResult`
- `object.__new__(cls`
- `object.__setattr__` inside result construction code
- any function/classmethod/module helper accepting all raw result fields

For each path, state why it cannot bypass invariants.

Do not self-audit the milestone; this is builder-side source-surface evidence only.

## 10. Preserve C002 fixes

Do not regress:

### Provenance

Keep exact request-seed authentication for:

- five stage seeds;
- optional retry seeds;
- RNG algorithm.

### Seed domain

Keep empty-string seed accepted and deterministic.

### Determinism

Keep:

- existing RNG known vector;
- existing four M02 golden fixtures;
- existing canonical result hashes;
- existing non-empty request canonical bytes.

If a golden/hash changes, stop and investigate. Do not regenerate fixtures merely to pass tests.

## 11. Regression verification

Run and log:

- new construction-boundary adversarial tests;
- all M02 result tests;
- all M02 request/RNG/interface tests;
- all M02 golden tests;
- cross-process determinism tests;
- full repository pytest regression;
- standalone import;
- `pip check`;
- no-network/no-global-random static checks;
- `git diff --check`.

Builder baselines before C003:

- C002 focused: 53 PASS
- C002 full: 113 PASS

The suite should grow by at least one adversarial construction test.

## 12. Safety and scope

Do not:

- add M03 production generators;
- touch main ScrubBots;
- alter palette/difficulty contracts;
- alter RNG algorithm/version;
- change golden fixtures without a justified deterministic contract correction;
- remove provenance checks;
- add public/raw/unsafe result construction hooks;
- modify ChatGPT-owned tracker/task/audit state;
- self-audit.

## 13. Builder exit criteria

The builder may stop as implementation complete / pending independent audit only when:

- no unchecked ordinary callable raw-result construction path remains;
- valid success/failure factories still work;
- provenance authentication remains green;
- empty-string seed remains green;
- all golden fixtures remain unchanged;
- full regression passes;
- no PAG-M03 code exists;
- matching C003 builder log is published;
- implementation commit and push/equality checkpoint are recorded.

Do not close M02. ChatGPT will independently re-audit and record terminal repository HEAD.
