# PAG-M09-C003 — Deterministic Candidate Identity & Acceptance Matrix Closure
Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`
Canonical current-state tracker: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md`

Previous strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M09-C002_MANIFEST_INTEGRITY_REPRODUCE_FIDELITY_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

Previous C002 builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M09-C002_MANIFEST_INTEGRITY_REPRODUCE_FIDELITY_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

## 1. Mission

Close only the two residual C002 findings:

- `F-PAG-M09-C002-001` — resume does not re-derive deterministic accepted candidate ID/path;
- `F-PAG-M09-C002-002` — the authoritative strict reproduce/determinism/path acceptance matrix remains incomplete.

Preserve all C002 fixes already accepted by the independent audit:

- exact attempt seed derivation validation;
- strict attempt/status schema;
- accepted-record one-to-one binding;
- accepted-bundle request/seed/hash/dimensions/policy binding;
- deterministic prior-attempt replay before resume;
- exact recorded M08 quality-policy reproduce fidelity;
- complete batch identity including exemplar identities/provenance and persisted quality policy;
- local-only/offline/zero-runtime-dependency architecture.

Do not begin M10 or M11. Do not modify accepted M03-M08 production algorithms.

## 2. Current tracker authority

Root `TASKS.md` is the only current project-status tracker.

Codex is builder only. Do not mark `PAG-0901..PAG-0930` `[x]`, do not declare M09 accepted, and do not author an independent audit.

## 3. GitHub-first start

Before edits read from GitHub `main`:

1. root `TASKS.md`;
2. `AGENTS.md` and `GOVERNANCE.md`;
3. M09 C001 and C002 prompts/audits/logs;
4. current `src/scrubbots_pixel_factory/cli/main.py`;
5. current M09 tests;
6. accepted M08 artwork/bundle candidate-ID validation;
7. this C003 prompt.

Authorized local mirror only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never use or modify:
`C:\Users\sekip\Desktop\ScrubBots`

Synchronize non-destructively.

## 4. Matching builder log

Before the first C003 source/test/doc edit create:

`.hiveai/codex-logs/PAG-M09-C003_DETERMINISTIC_CANDIDATE_IDENTITY_AND_ACCEPTANCE_MATRIX_CLOSURE_CODEX_LOG.md`

Exact H1:

`# PAG-M09-C003 — Deterministic Candidate Identity & Acceptance Matrix Closure`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record start HEAD/origin/divergence/status, authority reads, every focused failure/correction, exact test commands/counts, implementation commit, push, completed-log publication and final post-publication `HEAD == origin/main`, divergence `0 0`.

## 5. Canonical deterministic batch candidate identity

The accepted C002 implementation generates new accepted candidate IDs as:

`<batch-id>-<zero-padded-attempt-index>`

You may preserve that exact format or centralize an equivalently deterministic format. Do not introduce random UUIDs, time, Python `hash()`, machine paths or mutable defaults.

Create one project-owned helper/function for the expected accepted batch candidate ID, for example:

`_batch_candidate_id(manifest_or_batch_id, attempt_index)`

Use the same helper in:

- new accepted candidate generation;
- `_validate_manifest()` accepted-attempt validation;
- accepted-record validation;
- accepted bundle/path validation as appropriate;
- prior-history replay as appropriate.

For every `ACCEPTED` attempt require:

- candidate ID equals exactly the deterministic value derived from the validated immutable batch ID and attempt index;
- accepted record candidate ID equals the same expected value;
- relative path equals exactly `candidates/<expected-candidate-id>`;
- M08 bundle candidate ID equals exactly the same expected value.

A coordinated rewrite of manifest attempt + accepted record + directory name + internally consistent M08 candidate-ID fields must still fail resume if the rewritten ID is not the deterministic candidate ID derived from the immutable batch contract.

Do not weaken M08 candidate ID/path safety.

## 6. Preserve complete batch-environment identity

Do not regress C002 `_batch_id()`.

Batch identity must continue to bind canonically:

- request template;
- typed root seed;
- requested accepted count;
- max attempts;
- exact ordered exemplar identities/provenance;
- exact persisted quality policy/version/data.

Changing exemplar identity/provenance or quality policy must continue to change the batch ID and therefore the derived accepted candidate IDs.

## 7. Finish the strict reproduce negative matrix

Add direct bundle-level tests for the C002 cases still not directly evidenced.

At minimum add explicit tests for:

1. malformed `metadata.json` JSON text;
2. unsupported M02 request `schema_version`;
3. unsupported generator-options namespace and/or version;
4. changed generator version as a distinct metadata corruption case;
5. changed recorded original artwork grid hash as a direct bundle-level case;
6. controlled successful regeneration whose logical-grid hash/cells differ from the recorded artifact and therefore returns reproduce mismatch.

Keep existing tests for wrong M08 metadata schema, missing request field, typed seed tamper, generator-mode tamper, WFC missing/wrong exemplar, non-default quality policy and positive MASK/RULES/WFC MATCH.

Every expected domain failure must be non-zero with no uncontrolled traceback.

## 8. Finish the section-20 deterministic acceptance matrix

Add direct bounded evidence for the remaining named acceptance cases.

### 8.1 Same explicit single request

Run the same explicit single-generation request into two separate temporary output roots/processes.

Assert:

- both succeed;
- default candidate IDs are identical;
- file sets are identical;
- every M08 bundle file is byte-identical.

### 8.2 Single auto-dimension generation

Run `generate` with difficulty + mode + explicit seed but omitted width/height.

Assert:

- success;
- resolved dimensions are inside the correct difficulty band;
- metadata/result/artwork store those exact resolved dimensions;
- no resize is introduced.

### 8.3 Invalid mode/options evidence

Add direct CLI tests for:

- unsupported mode via argparse surface;
- malformed/unsupported generator options JSON;
- stable non-zero exit behavior;
- no traceback noise.

### 8.4 Single quality rejection exit code

Use a canonical local non-default quality policy that deliberately rejects an otherwise valid generated grid.

Assert:

- `generate` returns the documented `ExitCode.QUALITY_REJECTED` value (`5`);
- stderr contains `QUALITY_REJECTED` and stable ordered rejection code(s);
- no accepted bundle is exported as success.

### 8.5 Every attempted seed

For a batch with multiple attempts, assert for every attempt index N:

`attempt_seed == typed(DeterministicRNG(root_seed).retry_seed(N))`

Do not only test one corrupted seed.

### 8.6 Deterministic unique candidate IDs

For a batch that accepts more than one candidate, assert:

- IDs are unique;
- each ID equals the canonical helper derivation for its attempt;
- rerunning the same immutable batch environment produces identical IDs.

### 8.7 Different batch root seeds

Use two known bounded root seeds/configurations whose accepted logical-grid hashes differ.

Assert the accepted set differs. Do not use a probabilistic assertion whose result may occasionally collide.

Retain C002's actual separate-process two-`PYTHONHASHSEED` byte-equality test.

## 9. Finish path and corruption evidence

Add direct negative tests for:

- absolute accepted manifest relative path;
- unsafe/backslash or equivalent non-portable accepted path as relevant to the V1 format;
- accepted-bundle grid hash mismatch versus manifest;
- accepted-bundle embedded request seed mismatch versus manifest;
- forged COMPLETE state;
- forged EXHAUSTED state;
- forged IN_PROGRESS state;
- duplicate accepted candidate ID;
- duplicate accepted relative path;
- coordinated manifest + accepted record + M08 bundle candidate-ID/path rewrite that is internally consistent but differs from the deterministic expected candidate ID.

For the coordinated bundle rewrite, mutate all M08 candidate-ID bindings needed to keep `read_bundle()` internally valid, rename the bundle directory consistently, then prove M09 resume still rejects because the candidate ID no longer matches the deterministic batch candidate-ID formula.

Do not weaken M08 to make this test easy.

## 10. Evidence quality

Directly assert the intended property. Avoid one generic corruption test standing in for several semantically different gates when the prompt names those gates separately.

The existing full suite passing is supporting regression evidence, not a replacement for this acceptance matrix.

## 11. Required focused verification

Run and record at minimum:

- C003 deterministic candidate-ID validation tests;
- coordinated manifest/bundle candidate-ID tamper test;
- all remaining strict reproduce negatives;
- same-explicit-single-request byte-equality test;
- single auto-dimension test;
- invalid mode/options tests;
- exact single quality-rejection exit-code test;
- every-attempt seed derivation test;
- deterministic/unique candidate-ID test;
- different-root-seed accepted-set test;
- all required state/path/bundle mismatch tests;
- C002 manifest integrity/replay tests;
- C002 recorded-quality-policy reproduce test;
- actual two-`PYTHONHASHSEED` separate-process batch determinism test;
- network-blocked generation test;
- relevant M08 output tests;
- representative M03-M07 regression tests;
- full `python -m pytest -q`.

Also explicitly run and record after final edits:

- `python -m compileall -q src tests`;
- standalone package import;
- `python -m scrubbots_pixel_factory.cli --help`;
- installed `scrubbots-pixel --help` where the existing local editable-install workflow permits;
- `git diff --check`;
- final scoped diff/status.

## 12. Scope boundary

Production edits should remain in:

- `src/scrubbots_pixel_factory/cli/**`;
- M09 tests;
- M09 CLI README/documentation only if needed.

Do not change root `TASKS.md` acceptance/checkbox state.
Do not revive legacy hidden tracker files.
Do not rewrite historical prompts/logs/audits.
Do not change M03-M08 production algorithms.
Do not begin M10 or M11.

## 13. Completion handoff

After all required evidence passes:

1. commit focused C003 changes;
2. push `main` normally, never force-push;
3. complete the matching C003 builder log truthfully;
4. publish the completed builder log;
5. fetch origin and verify local `HEAD == origin/main` and divergence `0 0`;
6. record that checkpoint in the log;
7. return the C003 builder log for independent ChatGPT strict audit.

Do not self-audit or declare M09 accepted.
