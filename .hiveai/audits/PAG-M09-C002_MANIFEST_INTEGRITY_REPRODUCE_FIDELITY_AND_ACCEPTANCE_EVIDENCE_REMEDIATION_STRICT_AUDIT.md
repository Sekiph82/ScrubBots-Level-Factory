# PAG-M09-C002 — Manifest Integrity, Reproduce Fidelity & Acceptance Evidence Remediation
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

FAIL

PAG-M09-C002 materially repairs three of the four C001 defect families and closes most of the fourth, but M09 cannot receive unconditional acceptance yet. Two MAJOR residual findings remain, both bounded to the M09 CLI/resume/evidence layer:

- deterministic batch candidate identity is generated from the batch identity but is not re-derived and enforced during resume validation, so coordinated candidate-ID/path rewriting can remain semantically self-consistent while no longer being the ID implied by the immutable batch contract;
- the authoritative C002 prompt requires direct evidence for every named reproduce/determinism/path case, and the committed test matrix still omits several explicit gates.

No M03-M08 production generator, quality, WFC, router, or output algorithm needs redesign.

## 2. CONTRACT RECOVERY

Authoritative remediation prompt:
`.hiveai/prompts/PAG-M09-C002_MANIFEST_INTEGRITY_REPRODUCE_FIDELITY_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_PROMPT.md`

Previous strict audit:
`.hiveai/audits/PAG-M09-C001_CLI_AND_LOCAL_BATCH_GENERATION_STRICT_AUDIT.md`

Current-state authority: root `TASKS.md`.

C002 was explicitly limited to four C001 findings:

1. semantic manifest-history integrity;
2. exact recorded M08 quality-policy reproduction;
3. complete immutable batch identity including exemplar provenance/persisted quality policy;
4. the mandatory strict reproduce/determinism/path acceptance matrix.

## 3. BUILDER BOUNDARY / COMMITS / DIFF

Repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`

Builder initially synchronized at:
`fe1a5e09a271c78e29703976cf78739ba7ccf72b`

ChatGPT authority/control-plane tip merged by the builder after its first push was rejected:
`91a3d85e76ee201efa026c8773db89db2770d538`

Implementation commit:
`e5d3c5b951ae4cd95198860a042e955912b6b030`

Non-destructive merge commit:
`a8045f0bafd17460e98058a6b6e3972e8f6ccb31`

Completed-log publication / terminal builder-era HEAD:
`cd23b5d3d7ec4663e7c2b65e7d2d1630a18ec9f3`

Independent compare from ChatGPT authority tip `91a3d85...` to terminal builder-era `cd23b5d...` reports three commits ahead, zero behind, and exactly four changed paths:

- `.hiveai/codex-logs/PAG-M09-C002_MANIFEST_INTEGRITY_REPRODUCE_FIDELITY_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`
- `README.md`
- `src/scrubbots_pixel_factory/cli/main.py`
- `tests/integration/test_m09_cli_integration.py`

No root tracker acceptance state, prior prompt/audit, M03-M08 production algorithm, or M10/M11 implementation was changed by Codex.

## 4. C001 FINDING CLOSURE MATRIX

### `F-PAG-M09-C001-001` — semantic resume-history integrity

PARTIALLY CLOSED.

C002 now validates exact attempt field sets, re-derives every typed attempt seed, validates status-specific field semantics, one-to-one accepted records, dimensions, terminal-state invariants, accepted bundle request/seed/policy bindings, and replays deterministic prior attempts before resume.

Residual: accepted candidate ID/path are only checked for portability, uniqueness and mutual manifest/bundle consistency. The deterministic candidate ID actually used by generation is not re-derived from `batch_id + attempt_index` during validation/replay.

### `F-PAG-M09-C001-002` — reproduce used current default quality policy

CLOSED.

`_reproduce()` now reads `metadata.quality.report.policy`, constructs the exact `QualityPolicy`, re-evaluates the reproduced grid with that recorded policy, requires the complete quality report/decision/codes to reproduce, and then byte-compares the rebuilt M08 bundle.

A committed positive non-default-policy reproduce test exists.

### `F-PAG-M09-C001-003` — batch identity omitted exemplar provenance/persisted policy

FUNCTIONALLY CLOSED FOR NEW BATCH GENERATION, WITH A RESUME IDENTITY RESIDUAL.

`_batch_id()` now hashes the request template, typed root seed, requested count, max attempts, ordered exemplar identities/provenance and exact persisted quality policy. Different exemplar environments therefore generate different batch IDs and generated candidate IDs.

Residual: resume does not enforce that an accepted candidate ID is the exact deterministic ID implied by the validated batch identity and attempt index.

### `F-PAG-M09-C001-004` — mandatory acceptance evidence incomplete

PARTIALLY CLOSED.

C002 adds substantial new evidence, including actual separate-process batch byte comparison under two `PYTHONHASHSEED` settings, non-default quality policy, exemplar-bound batch identity, autodimension/rectangular batch behavior, manifest corruption cases, metadata corruption cases, and MASK byte-exact reproduce.

However, several prompt-mandated direct gates remain absent. See sections 10 and 17.

## 5. ACCEPTANCE CRITERIA MATRIX

- Standard-library Windows CLI architecture: PASS.
- Zero runtime dependencies/offline boundary: PASS.
- C001 single generate behavior preserved: PASS.
- Exact recorded M08 quality-policy reproduction: PASS.
- Exact root/count/terminal manifest invariants: PASS.
- Attempt seed derivation validation: PASS.
- Attempt status-field semantic validation: PASS.
- Accepted-record one-to-one cross-binding: PASS.
- Accepted bundle ID/hash/dimensions/request-seed/policy cross-binding: PASS.
- Deterministic replay of prior attempts before resume: PASS.
- Complete batch identity includes exemplar identities + persisted policy: PASS.
- Generated candidate IDs differ across distinct batch identities: PASS.
- Resume enforces exact deterministic candidate ID from immutable batch identity: FAIL.
- Mandatory strict reproduce matrix: FAIL / INCOMPLETE.
- Mandatory section-20 deterministic matrix: FAIL / INCOMPLETE.
- Required path/corruption matrix: FAIL / INCOMPLETE.
- M08 preservation/full regression builder evidence: PASS as builder evidence.
- Independent runtime replay: UNVERIFIED due audit-container DNS failure.

## 6. MANIFEST ROOT / ATTEMPT SEMANTICS REVIEW

C002 substantially strengthens `_validate_manifest()`.

The implementation now requires:

- `0 <= next_attempt_index <= max_attempts`;
- `0 <= accepted_count <= requested_count`;
- exact manifest request-template shape/canonicalization;
- exact canonical persisted `QualityPolicy` matching request difficulty;
- exact exemplar-identity field sets;
- complete batch-ID re-derivation;
- `len(attempts) == next_attempt_index`;
- `len(accepted) == accepted_count`;
- exact attempt field set;
- exact typed retry seed for attempt index;
- recognized status enum;
- status-specific failure/quality/hash/path rules;
- accepted-record one-to-one ordering;
- unique accepted IDs/paths;
- exact COMPLETE / EXHAUSTED / IN_PROGRESS state derivation.

This closes the primary C001 state-machine defect.

## 7. ACCEPTED BUNDLE CROSS-BINDING REVIEW

`_accepted_grids()` now uses M08 `read_bundle()` and requires:

- artwork candidate ID == accepted record candidate ID;
- artwork grid hash == record grid hash;
- artwork width/height == accepted dimensions;
- embedded generation request == request reconstructed from manifest + attempt seed;
- embedded typed generation seed == accepted attempt seed;
- bundle quality policy == persisted batch policy.

M08 continues to independently validate artwork/metadata/quality/generator provenance consistency.

This is a strong improvement over C001.

## 8. PRIOR-HISTORY REPLAY REVIEW

`_validate_attempt_history()` deterministically rebuilds each recorded request from the root retry sequence, regenerates through the router, recomputes logical-grid hash and quality report, validates failure/rejection/duplicate/accepted classification, and cross-checks accepted bundle cells.

This makes prior seed/status/hash/rejection tampering fail closed in ordinary and coordinated manifest-only corruption cases.

Replay is bounded by the recorded finite attempt history and remains within the M09 orchestration layer.

## 9. REPRODUCE QUALITY-POLICY FIDELITY REVIEW

PASS.

C002 no longer substitutes `_quality_policy(request)` during reproduce.

The implementation:

1. obtains the already M08-validated quality binding;
2. reads `quality.report.policy`;
3. constructs the exact policy;
4. requires canonical policy data;
5. evaluates the reproduced logical grid using that policy;
6. compares the entire reproduced quality report to the recorded report;
7. compares decision/rejection codes;
8. rebuilds and byte-compares the full M08 bundle.

The committed test `test_reproduce_uses_non_default_recorded_quality_policy` directly proves the intended positive case.

`F-PAG-M09-C001-002` is closed.

## 10. BATCH IDENTITY / CANDIDATE ID REVIEW

The batch identity fix itself is correct: `_batch_id()` now canonically includes the complete immutable V1 batch environment required by C002.

Generation then creates accepted candidate IDs as:

`f"{manifest['batch_id']}-{index:06d}"`

However, resume validation does not recompute and require this exact value.

For an accepted attempt `_validate_manifest()` only requires a portable `candidate_id`, a path equal to `candidates/<candidate_id>`, uniqueness, and equality between accepted/attempt records. `_accepted_grids()` requires the bundle candidate ID to equal that manifest value. `_validate_attempt_history()` again checks the accepted-record/bundle candidate ID against the attempt record, but never checks the deterministic generation formula.

M08 validates candidate IDs for syntax and internal artwork/metadata/quality equality, not against M09's batch-ID derivation.

Therefore a coordinated rewrite of the accepted candidate ID/path in manifest and internally consistent bundle metadata can remain valid while no longer being the deterministic candidate identity implied by the immutable batch contract. Likewise, a changed immutable environment whose replayed logical output happens to remain identical is not forced to use candidate IDs derived from the newly re-derived batch ID.

This violates C002 sections 6.5 and 8: candidate ID/path are recomputable prior history and candidate identity must be deterministic/collision-resistant for the immutable batch environment.

## 11. TEST / EVIDENCE REVIEW

Builder reports:

- focused C002/M09: `36 passed`;
- M08 + M09 + offline focused command: `62 passed`;
- initial standalone `pytest -q`: collection failure caused by an unrelated installed `tests` package;
- corrected `python -m pytest -q`: `327 passed` in `3:43.78`;
- offline boundary: pass;
- no new runtime dependency/network/asset.

The builder log is transparent about the collection-path problem and the corrected invocation.

The committed C002 tests add valuable coverage, but the authoritative prompt required named direct evidence, not merely a larger full-suite count.

## 12. OFFLINE / SECURITY / PATH REVIEW

PASS for runtime network/dependency boundaries.

C002 adds no network client, telemetry, unsafe deserializer, shell execution, arbitrary eval/exec, dependency, interpolation/resizing or M03-M08 production change.

`_safe_relative_path()` rejects empty/non-string values, backslash paths, absolute paths and `..` path components. Explicit generate candidate-ID traversal is rejected through the M08 artwork contract.

Residual evidence gaps remain for several specific path/cross-binding tamper classes required by the prompt.

## 13. ARCHITECTURE CONSISTENCY

PASS.

C002 preserves the accepted architecture:

- argparse CLI;
- local JSON input;
- existing `GenerationRequest`/`GeneratorOptions`;
- `GeneratorRouter.generate_candidate()`;
- M07 quality engine;
- M08 bundle APIs;
- project deterministic RNG;
- local-only WFC registry;
- no generator or PNG duplication.

The required C003 correction should remain entirely in M09 CLI validation/tests/docs.

## 14. CI / INDEPENDENT RUNTIME STATUS

GitHub exposes no combined status checks and no workflow runs for the C002 implementation commit.

Independent runtime replay could not be started because the audit container cannot resolve `github.com`; `git ls-remote` failed at DNS resolution. This is recorded as UNVERIFIED and is not itself a product failure.

The verdict is based on committed source/test evidence and explicit prompt requirements.

## 15. LOG / GOVERNANCE / SCOPE TRUTHFULNESS

Builder log H1 and role are correct.

The builder truthfully records:

- its initial pre-authority HEAD;
- the first rejected push;
- the non-destructive merge with ChatGPT's authority commits;
- implementation commit;
- focused/full test commands;
- the initial `pytest` collection issue and correction;
- final publication SHA;
- final local HEAD == origin/main, divergence `0 0`.

Independent compare confirms Codex did not modify root tracker acceptance state, prior audits/prompts, accepted M03-M08 production algorithms, or M10/M11.

## 16. CROSS-MILESTONE STATE

`PAG-0441` remains blocked until M10 establishes the measured V1 performance budget.

M10+ remains blocked until M09 receives unconditional independent PASS.

No new M00-M08 regression finding is opened by this audit.

## 17. DEFECTS BY SEVERITY

### F-PAG-M09-C002-001 — MAJOR — Resume does not re-derive deterministic accepted candidate ID/path

Status: OPEN.

Generation deterministically defines an accepted batch candidate ID from the immutable `batch_id` and `attempt_index`, but validation/replay does not require the stored ID to equal that derived value.

Current checks prove only that the candidate ID is syntactically safe, unique, and repeated consistently through attempt record, accepted record, directory path and M08 bundle.

That is insufficient for immutable deterministic history. A coordinated manifest + bundle candidate-ID/path rewrite can remain internally consistent while no longer matching the candidate identity implied by the batch contract.

Required target:

- centralize the deterministic batch candidate-ID function;
- use it both for generation and validation;
- for every `ACCEPTED` attempt require `candidate_id == expected_candidate_id(batch_id, attempt_index, ...)`;
- require `relative_path == candidates/<expected_candidate_id>`;
- require accepted record and M08 bundle candidate ID to equal that expected value;
- add a corruption test that changes candidate ID/path coherently across manifest/bundle and proves resume still rejects it;
- retain uniqueness/collision safety across different immutable exemplar/policy environments.

### F-PAG-M09-C002-002 — MAJOR — Authoritative C002 acceptance matrix remains incomplete

Status: OPEN.

C002 adds many missing tests, but the prompt explicitly requires direct coverage for every named case. The committed suite still lacks direct evidence for several requirements, including at minimum:

1. malformed reproduce JSON;
2. unsupported M02 request schema version;
3. unsupported generator-options namespace/version;
4. changed generator version as a distinct metadata corruption case;
5. changed recorded original artwork grid hash as a direct bundle-level case;
6. a controlled successful regeneration whose logical grid differs from the recorded artifact;
7. two independent `generate` invocations of the same explicit request proving identical default candidate ID and byte-identical M08 bundle files;
8. a single-generation auto-dimension case proving legal bounds and recorded resolved dimensions;
9. invalid mode and malformed/unsupported options JSON with no traceback noise;
10. deliberate single-generation quality rejection returning the exact documented `QUALITY_REJECTED` exit code and stable rejection codes;
11. direct assertion that every recorded batch attempt seed equals `DeterministicRNG(root_seed).retry_seed(index)`;
12. direct deterministic/unique candidate-ID assertions for a multi-accepted batch;
13. two different root batch seeds producing demonstrably different accepted sets;
14. absolute/unsafe accepted-manifest path cases in addition to one `..` traversal mutation;
15. accepted-bundle grid-hash and embedded request-seed mismatch cases versus the manifest;
16. forged COMPLETE, EXHAUSTED and IN_PROGRESS states as explicit state cases, rather than only one terminal-state mutation;
17. duplicate accepted candidate ID and duplicate accepted relative-path rejection;
18. required post-C002 verification evidence for `python -m compileall -q src tests`, standalone package import and CLI `--help` is not recorded in the C002 builder log.

Some implementation gates are already indirectly enforced by M08/read_bundle or `_validate_manifest()`. The issue is evidence completeness: the authoritative remediation prompt explicitly required direct tests/verification for these acceptance cases.

## 18. REQUIRED BOUNDED REMEDIATION

Create only `PAG-M09-C003`.

C003 must:

1. enforce one canonical deterministic batch candidate-ID derivation in both generation and resume validation;
2. bind accepted relative paths and M08 bundle candidate IDs to that derived value;
3. add the remaining direct strict reproduce, deterministic, quality-rejection, path/corruption and seed/candidate-ID acceptance tests listed above;
4. run/log the required compileall/import/help and focused/full regression commands;
5. preserve C002's successful manifest replay, recorded-quality-policy, complete batch identity and offline architecture;
6. not begin M10/M11 or modify M03-M08 production algorithms.

## 19. TRACKER DISPOSITION

M09 remains active and unaccepted.

No `PAG-0901..PAG-0930` checkbox should be promoted to `[x]` on this failed cycle.

Next cycle:
`PAG-M09-C003 — Deterministic Candidate Identity & Acceptance Matrix Closure`

Required actor: CODEX.

M10+ remains blocked.

## 20. FINAL CONCLUSION

C002 is a substantial remediation and closes the most important C001 correctness defects: semantic attempt replay, historical quality-policy fidelity and complete batch-environment identity are now present.

M09 nevertheless does not yet satisfy its strict acceptance contract because deterministic candidate identity is not enforced on resume and the explicitly mandatory acceptance matrix remains incomplete.

Final verdict: FAIL.
