# PAG-M09-C003 — Deterministic Candidate Identity & Acceptance Matrix Closure
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

PASS

PAG-M09-C003 closes both residual M09 findings. No BLOCKER, MAJOR or MINOR finding remains in the M09 CLI / reproduce / deterministic batch / resume contract.

M09 is eligible for PASS / CLOSED and `PAG-0901..PAG-0930` are eligible for independent tracker completion.

## 2. CONTRACT RECOVERY

Authoritative prompt:
`.hiveai/prompts/PAG-M09-C003_DETERMINISTIC_CANDIDATE_IDENTITY_AND_ACCEPTANCE_MATRIX_CLOSURE_PROMPT.md`

Previous strict audit:
`.hiveai/audits/PAG-M09-C002_MANIFEST_INTEGRITY_REPRODUCE_FIDELITY_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_STRICT_AUDIT.md`

Current-state authority at audit start: root `TASKS.md`.

C003 was explicitly limited to two residuals:

- `F-PAG-M09-C002-001`: deterministic accepted candidate ID/path was generated but not re-derived during resume;
- `F-PAG-M09-C002-002`: direct strict reproduce/determinism/path acceptance evidence remained incomplete.

## 3. BUILDER BOUNDARY / COMMITS / DIFF

Repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`

Builder synchronized base:
`a10c77232f577a1d8c3f05d7855e318e5f0829e3`

Implementation commit:
`9d29c46ffad083158e33ae227191a72920445a86`

Publication-checkpoint commit / terminal builder-era HEAD:
`be0aa3d1efb108a200a261a3f02e677cee399960`

Independent compare from base to terminal reports exactly two commits ahead and zero behind. Changed paths are limited to:

- `.hiveai/codex-logs/PAG-M09-C003_DETERMINISTIC_CANDIDATE_IDENTITY_AND_ACCEPTANCE_MATRIX_CLOSURE_CODEX_LOG.md`;
- `README.md`;
- `src/scrubbots_pixel_factory/cli/main.py`;
- `tests/integration/test_m09_cli_integration.py`.

No root task acceptance state, prior audit/prompt/log, M03-M08 production algorithm, M10 implementation, M11 implementation or main ScrubBots repository was modified by Codex.

## 4. RESIDUAL FINDING CLOSURE MATRIX

### `F-PAG-M09-C002-001` — deterministic candidate-ID/path binding

CLOSED.

C003 adds one canonical `_batch_candidate_id()` helper using the accepted `<batch-id>-<zero-padded-attempt-index>` formula.

The same helper is now used for:

- new accepted candidate generation;
- accepted-attempt validation;
- accepted-record validation;
- accepted bundle candidate-ID/path binding;
- deterministic prior-history replay.

An accepted manifest record must now equal the candidate ID implied by the already-validated immutable batch identity and attempt index. Relative path must equal `candidates/<expected-candidate-id>`.

### `F-PAG-M09-C002-002` — acceptance evidence completeness

CLOSED.

C003 adds direct tests for the remaining named reproduce, identity, deterministic, quality-rejection, state, bundle-cross-binding and path cases while retaining the accepted C002 real separate-process two-`PYTHONHASHSEED` batch-byte test.

## 5. DETERMINISTIC CANDIDATE ID REVIEW

`_batch_candidate_id(manifest_or_batch_id, attempt_index)` rejects malformed inputs and returns only a function of validated batch identity plus non-negative integer attempt index.

No UUID, wall clock, Python `hash()`, machine path or mutable current default contributes to the identity.

`_validate_manifest()` now re-derives the expected candidate ID for every `ACCEPTED` attempt and requires the exact canonical relative path.

Accepted history independently performs the same derivation from its linked attempt index.

## 6. ACCEPTED BUNDLE / PATH CROSS-BINDING

`_accepted_grids()` now re-derives the expected candidate ID from the validated manifest and accepted attempt index.

It requires:

- M08 bundle candidate ID == manifest candidate ID;
- M08 bundle candidate ID == deterministic M09 expected candidate ID;
- relative path == `candidates/<expected-candidate-id>`;
- existing C002 hash/dimension/request-seed/policy bindings remain intact.

This closes the prior coordinated-rewrite gap.

## 7. COORDINATED REWRITE NEGATIVE EVIDENCE

The committed C003 test generates a valid batch, changes the candidate ID consistently in `artwork.json`, all required M08 metadata candidate-ID bindings, manifest attempt, manifest accepted record and directory name, and proves `read_bundle()` still accepts the rewritten M08 bundle internally.

M09 resume nevertheless rejects it because the new ID is not the value derived from immutable batch identity + attempt index.

This is the exact adversarial case required by the C003 prompt and directly proves the M09-level deterministic identity gate rather than relying on M08 to reject the bundle first.

## 8. STRICT REPRODUCE MATRIX

Direct committed evidence now covers the remaining C003 cases:

- malformed `metadata.json` JSON;
- unsupported M02 request schema version;
- unsupported generator-options namespace;
- unsupported generator-options version;
- changed generator version;
- changed original artwork grid hash;
- controlled successful regeneration with different logical cells/hash returning reproduce mismatch.

Existing retained C001/C002 tests continue to cover wrong M08 metadata schema, missing required request field, typed seed tamper, generator-mode tamper, non-default recorded quality policy, WFC matching/missing/wrong exemplar and positive MASK/RULES/WFC reproduction paths.

## 9. SINGLE-GENERATION DETERMINISM / AUTO DIMENSIONS

C003 directly runs the same explicit RULES request in two independent processes under different `PYTHONHASHSEED` settings and verifies identical default candidate IDs, identical file sets and byte-identical M08 files.

Auto-dimension single generation is directly tested with omitted width/height. The recorded request retains `None` for explicit dimensions while the resolved result/artwork dimensions are equal and inside the EASY 20–29 band.

## 10. INVALID INPUT / QUALITY EXIT REVIEW

Direct CLI evidence covers unsupported mode, malformed options JSON and unsupported options namespace/version with stable non-zero behavior and no traceback.

A deliberate valid generation under a canonical rejecting M07 policy returns exact documented exit code `5`, emits `QUALITY_REJECTED` plus a stable rejection code, and does not export an accepted bundle.

## 11. BATCH DETERMINISM REVIEW

A multi-accepted batch directly verifies every recorded attempt seed against `DeterministicRNG(root_seed).retry_seed(index)`.

Every accepted candidate ID is checked against the canonical helper and accepted IDs are unique.

Existing byte-stable same-batch rerun and completed-resume no-op evidence remains intact.

C003 also adds two known root seeds whose accepted grid-hash sets differ, avoiding a merely probabilistic 'different seeds may differ' assertion.

## 12. RESUME STATE / PATH / BUNDLE CORRUPTION REVIEW

Direct negative evidence now includes:

- absolute accepted path;
- backslash/non-portable accepted path;
- accepted bundle grid-hash corruption;
- accepted bundle embedded request-seed corruption;
- forged COMPLETE;
- forged EXHAUSTED;
- forged IN_PROGRESS;
- duplicate accepted candidate ID;
- duplicate accepted relative path;
- coordinated internally-valid candidate-ID/path rewrite.

C002's prior attempt-seed/status/hash/rejection/count/index corruption matrix remains retained.

## 13. CROSS-PROCESS / OFFLINE REVIEW

The accepted C002 test that generates full batch artifacts in separate processes under two different `PYTHONHASHSEED` values remains present and compares complete file sets and bytes, not merely CLI help text.

The network-blocked generation test remains present.

Runtime dependency list remains empty. No network client, telemetry path, remote exemplar lookup or online fallback was introduced.

## 14. BUILDER TEST / TOOLING EVIDENCE

Builder reports:

- focused M09 C003/C002 suite: `56 passed`;
- representative M03-M09 + offline/M08 suite: `128 passed`;
- full repository: `347 passed in 3:34.10` with the existing pytest cache warning;
- `python -m compileall -q src tests`: PASS;
- standalone package import: PASS;
- `python -m scrubbots_pixel_factory.cli --help`: PASS;
- installed `scrubbots-pixel --help`: PASS;
- `git diff --check`: PASS apart from expected line-ending conversion warnings.

The builder truthfully recorded three initial fixture/test-construction failures and their test-only corrections before the final focused PASS.

## 15. INDEPENDENT RUNTIME / CI STATUS

GitHub exposes no combined commit status entries and no workflow runs for terminal builder-era HEAD `be0aa3d...`.

The audit environment therefore has no independent CI runtime result to substitute for the builder's local `347 passed` evidence.

Independent acceptance is based on repository diff inspection, direct source-contract comparison, committed direct tests and prior accepted M00-M08 contracts. Lack of CI is NOTE only and is not a product defect.

## 16. ARCHITECTURE / REGRESSION REVIEW

PASS.

C003 changes only the M09 orchestration/validation layer and tests. It does not reopen or duplicate M03-M08 generator, quality, WFC, router or output algorithms.

C002's exact recorded quality-policy fidelity and complete batch-environment identity remain unchanged.

## 17. TRACKER / GOVERNANCE REVIEW

PASS.

Codex did not alter root `TASKS.md`, acceptance checkboxes, prior audits/prompts/logs or the historical cycle index.

Root `TASKS.md` remains the only current project-state authority.

The final `be0aa3d...` commit is evidence-only and records the post-implementation push equality checkpoint. It does not modify product code.

## 18. M09 TASK ELIGIBILITY

With C003 PASS, the complete M09 contract is independently supported:

- single-generation CLI and Windows/module entry surface;
- explicit/omitted seed behavior;
- legal auto/explicit dimensions;
- M07 quality gate and stable domain exits;
- exact recorded M08 reproduce behavior;
- local-only rich exemplar reproduction;
- finite deterministic batch orchestration;
- attempts vs accepted separation;
- deterministic attempted seeds;
- strict resumable manifest/history validation;
- collision-resistant deterministic batch/candidate identity;
- exact duplicate detection without mutation;
- deterministic review/report output;
- offline operation and provenance preservation.

`PAG-0901..PAG-0930` are eligible for `[x]` by the independent tracker owner.

## 19. OPEN CROSS-MILESTONE ITEMS

No M09 finding remains.

`PAG-0441` remains blocked until M10 establishes the measured V1 performance budget.

M10 may now begin. M11 remains gated on M10 V1 acceptance.

## 20. FINAL DISPOSITION

PASS

Severity count:

- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 1 — no GitHub CI/status runtime exists for the terminal builder HEAD; builder local full-suite evidence is `347 passed`.

Closed by this audit:

- `F-PAG-M09-C002-001`;
- `F-PAG-M09-C002-002`;
- remaining residual scope from `F-PAG-M09-C001-001` and `F-PAG-M09-C001-004`.

Previously closed in C002 and preserved:

- `F-PAG-M09-C001-002`;
- `F-PAG-M09-C001-003`.

Milestone disposition:

`PAG-M09 — CLI & Local Batch Generation: PASS / CLOSED`.
