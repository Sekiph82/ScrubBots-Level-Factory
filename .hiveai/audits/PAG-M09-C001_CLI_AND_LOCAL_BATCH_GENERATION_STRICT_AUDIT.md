# PAG-M09-C001 — CLI & Local Batch Generation
Document role: CHATGPT INDEPENDENT STRICT AUDIT

## 1. VERDICT

FAIL

The M09 C001 implementation establishes a credible offline CLI foundation, but four MAJOR acceptance defects remain. The defects are bounded to M09 orchestration/state/evidence. No accepted M00-M08 generator/output algorithm needs to be redesigned.

## 2. CONTRACT RECOVERY

Authoritative prompt:
`.hiveai/prompts/PAG-M09-C001_CLI_AND_LOCAL_BATCH_GENERATION_PROMPT.md`

Current-state authority: root `TASKS.md`.

M09 covers `PAG-0901` through `PAG-0930`: Windows-friendly single generation, exact reproduction from M08 metadata, deterministic finite/resumable batch generation, duplicate handling, review output, and offline/provenance preservation.

The prompt explicitly requires fail-closed historical metadata parsing, immutable resumable batch history, collision-resistant deterministic identity, and the mandatory negative/determinism test matrix in sections 12 and 20.

## 3. BRANCH / HEAD / DIFF SCOPE

Repository: `Sekiph82/ScrubBots-Level-Factory`
Branch: `main`

Builder synchronized base: `ed5d2c307c2abab14088f6997365085481661ae8`
Implementation commit: `23f27f3e73dc4a6ef34338378139aac842f3fde6`
Completed-log publication commit: `5f1324dade158315dfc062a079d4dbde716fd409`
Terminal builder-era HEAD independently observed: `fe1a5e09a271c78e29703976cf78739ba7ccf72b`

Independent compare from base to terminal reports exactly three commits ahead and zero behind. Changed paths are limited to the M09 CLI package, M09 tests, README, `pyproject.toml`, and the matching builder log. No M00-M08 production generator/output/quality implementation and no M10+ implementation was changed.

## 4. ACCEPTANCE CRITERIA MATRIX

- Installed/module CLI surface: PASS.
- Standard-library / zero runtime dependency: PASS.
- Single generation through `generate_candidate()`, M07 quality and M08 export: PASS.
- Local-only exemplar loader: PASS.
- Basic MASK/RULES/WFC reproduce path: PASS.
- Exact recorded reproduce policy/config fidelity: FAIL.
- Finite deterministic batch attempt derivation: PASS for newly generated attempts.
- Resume prior-history semantic integrity: FAIL.
- Collision-resistant batch identity across immutable exemplar environments: FAIL.
- Exact duplicate detection for current run: PASS.
- Completed resume byte no-op in honest manifest case: PASS.
- Mandatory strict reproduce/determinism/path test matrix: FAIL / INCOMPLETE.
- Windows evidence: PASS as builder evidence.
- Independent runtime replay: UNVERIFIED due audit-container DNS failure.

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

The builder accurately reports the broad CLI architecture and the existence of deterministic batch/resume machinery. Repository inspection confirms `argparse`, the console entry point, OS-entropy boundary for omitted single seed, local exemplar parsing, candidate-wrapper routing, atomic manifest writes, exact duplicate comparison, and M08 bundle publication.

However, the builder claim that resume validates immutable history is stronger than the implementation. `_validate_manifest()` mostly validates root shape/counts and attempt index ordering. It does not re-bind the recorded prior attempt seeds/status/rejections/accepted relations to the deterministic batch contract.

The builder also claims exact reproduction from recorded metadata, but `_reproduce()` recalculates quality with the current default `QualityPolicy(difficulty=...)` rather than reconstructing the policy recorded in the M08 quality report.

## 6. FILE / SYMBOL EVIDENCE

Primary implementation: `src/scrubbots_pixel_factory/cli/main.py`.

Important accepted behavior:

- `_request_from_canonical()` requires the exact M02 request field set/schema version.
- `_generate()` uses `GeneratorRouter.generate_candidate()`, evaluates M07 quality, and exports through M08.
- `_atomic_manifest_write()` uses same-directory temp file + fsync + atomic replace.
- current-attempt seeds are derived as `DeterministicRNG(root_seed).retry_seed(index)`.
- exact duplicates require both matching grid hash and exact logical-grid equality.

Open defects are detailed in section 14.

## 7. FOCUSED TEST EVIDENCE

Committed M09 tests contain 4 unit tests and 10 integration tests.

They directly cover:

- omitted seed control/recording;
- seed token parsing;
- local-path rejection for options/exemplar input;
- module help;
- rectangular RULES single generation + reproduce;
- one tampered request seed;
- WFC matching/missing/wrong exemplar;
- identical honest batch reruns and completed-resume no-op;
- interrupted/resumed convergence;
- finite batch configuration;
- bounded WFC generator failure;
- exact duplicate record;
- cross-process help text under two hash-seed settings;
- one network-blocked MASK generation.

This is useful evidence, but it does not satisfy the authoritative prompt's full mandatory matrix.

## 8. REGRESSION EVIDENCE

Builder reports:

- focused M09: `14 passed, 1 warning`;
- combined M09/M08: `32 passed, 1 warning`;
- full repository: `305 passed, 1 warning in 233.88s`;
- compileall/import/diff/static scans: pass;
- installed PowerShell/module CLI smoke: pass;
- only the pre-existing pytest-asyncio/pytest environment mismatch in `pip check`.

GitHub exposes no combined commit status checks or workflow runs for terminal builder HEAD.

Independent runtime execution could not start because the audit container cannot resolve `github.com`. Runtime replay is therefore UNVERIFIED, not failed.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

PASS for network/dependency boundaries.

No runtime network client, telemetry, unsafe deserialization, `eval`/`exec`, interpolation/resizing, or new dependency was introduced.

Path safety is partially strong: M08 candidate IDs reject separators/absolute semantics and manifest accepted paths are checked as portable relative paths. The prompt-required dedicated M09 path-tamper evidence is nevertheless incomplete and is included in the acceptance-evidence finding.

## 10. ARCHITECTURE CONSISTENCY

PASS with bounded M09 corrections required.

The CLI correctly orchestrates accepted M02/M05/M06/M07/M08 layers instead of duplicating generator or PNG logic. C002 should preserve this architecture and modify only M09 parsing/identity/state verification/tests/docs as necessary.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder log H1/role are correct. It truthfully records initial test harness failures, test counts, implementation commit, push, completed-log publication and the equality checkpoint after the completed-log commit.

Terminal `fe1a5e...` is an evidence-only follow-up that records the equality result for `5f1324d...`. This self-referential final publication pattern is NOTE only and does not cause the product FAIL.

Root `TASKS.md` remains the sole current-state tracker. No M09 checkbox may be completed after this failed audit.

## 12. FINAL REPOSITORY STATE

Terminal builder-era HEAD: `fe1a5e09a271c78e29703976cf78739ba7ccf72b`.

C001 implementation scope is bounded to M09 and leaves M10/M11 untouched.

## 13. OPEN CROSS-MILESTONE FINDINGS

`PAG-0441` remains blocked until M10 establishes the measured V1 performance budget.

M10+ remains blocked until M09 receives unconditional independent PASS.

No new M00-M08 regression finding was identified.

## 14. DEFECTS BY SEVERITY

### F-PAG-M09-C001-001 — MAJOR — Resume accepts semantically tampered batch history

Status: OPEN.

`_validate_manifest()` checks schema/root fields, count types, batch ID, request-template validity, `len(attempts) == next_attempt_index`, accepted length, attempt index ordering and accepted relative-path shape. It does not prove that prior history is the history deterministically implied by the root seed and manifest state.

Concrete gaps:

1. each recorded `attempt_seed` is not rederived and compared to `DeterministicRNG(root_seed).retry_seed(attempt_index)`;
2. attempt record exact field set/types/status semantics are not validated;
3. accepted records are not required to correspond one-to-one to `ACCEPTED` attempt records with identical seed/candidate/hash/path/dimensions;
4. accepted bundles are checked only against recorded grid hash, not against recorded candidate ID, dimensions and attempt seed/request provenance;
5. `COMPLETE` is not required to mean `accepted_count == requested_count`;
6. `EXHAUSTED` is not required to mean `next_attempt_index == max_attempts` with target unmet;
7. `IN_PROGRESS`, `next_attempt_index`, accepted count and max-attempt relationships are not semantically cross-bound.

A manifest can therefore preserve its array lengths/index ordering while changing prior attempt seeds/status/rejection history, or even lie about terminal state, and still pass resume validation.

Required target: resume must fail closed on any prior-history mutation that would make the manifest differ from the deterministic uninterrupted state machine.

### F-PAG-M09-C001-002 — MAJOR — Reproduce substitutes current default M07 quality policy for the recorded M08 policy

Status: OPEN.

M08 metadata stores the full quality report, including `report.policy`.

`_reproduce()` regenerates the logical grid correctly, but then calls `_quality_policy(request)`, which constructs the current default `QualityPolicy(difficulty=request.difficulty)`. It uses that new report to rebuild and byte-compare the bundle.

Therefore a valid existing M08 bundle produced with a supported non-default M07 policy can be falsely reported as MISMATCH even though generation/artwork/provenance reproduce exactly. This violates the M09 rule to reproduce recorded historical state without substituting current defaults.

Required target: strictly parse/reconstruct the exact recorded M08 quality policy/report contract, reevaluate using that recorded policy, and require the regenerated quality binding to match the original.

### F-PAG-M09-C001-003 — MAJOR — Batch identity/candidate identity omits immutable exemplar provenance

Status: OPEN.

`_batch_config(args, seed, registry)` accepts `registry` but does not include it in the returned config. `_batch_id()` hashes only request template + root seed + requested count + max attempts.

`exemplar_identities` and the persisted quality policy are stored separately in the manifest but are not part of the batch identity. Accepted candidate IDs are only `batch_id + attempt_index`.

Consequently two WFC-bearing batches with the same request/root/count/bound but different local exemplar content/provenance can receive the same batch ID and same per-attempt candidate IDs while producing different artifacts. This is not collision-resistant identity for the immutable generation environment.

Required target: bind the deterministic batch identity to the complete immutable batch environment, including exact exemplar identities/provenance and exact persisted quality policy. Candidate IDs must remain deterministic and collision-resistant for distinct immutable batch environments; adding request/grid digest material is acceptable if documented.

### F-PAG-M09-C001-004 — MAJOR — Mandatory reproduce/determinism/path acceptance evidence is incomplete

Status: OPEN.

The authoritative prompt explicitly requires the strict negative list in section 12 and the 20-item determinism/cross-process acceptance list in section 20. The committed 14 M09 tests do not directly prove several required gates.

Missing or materially incomplete direct evidence includes at least:

- malformed reproduce JSON;
- wrong M08 metadata schema/version;
- unsupported request schema version;
- unsupported generator-options version/namespace;
- missing request field;
- changed generator mode/version;
- changed recorded grid hash;
- successful regeneration whose hash differs;
- positive accepted MASK reproduce in addition to RULES;
- same explicit single request => same candidate ID + byte-identical M08 bundle;
- auto-dimension CLI request bounds/resolved-dimension evidence;
- explicit quality-rejection exit code + stable codes;
- every batch attempt seed checked against deterministic derivation;
- candidate-ID uniqueness/determinism evidence;
- actual batch outputs/manifests across separate processes and at least two `PYTHONHASHSEED` settings (current cross-process test checks only `--help` text);
- different root batch seeds producing different accepted sets;
- rectangular batch path;
- M09 manifest/candidate traversal tamper rejection;
- the terminal/history corruption cases required by F-001 remediation.

Passing the full repository suite does not replace explicit acceptance evidence required by the authoritative prompt.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

NOTE only: `_batch_config()` currently receives `registry` but does not use it; C002 should remove the misleading parameter only if the complete immutable identity is instead built cleanly elsewhere.

No CLI framework or new dependency is justified by this remediation.

## 16. UNVERIFIED ITEMS

Independent pytest replay is UNVERIFIED because the audit container cannot resolve GitHub for a clean checkout.

Builder-reported `305 passed` remains builder evidence.

## 17. REGRESSION RISK

Moderate if remediation is kept within M09 state validation/identity/reproduce parsing/tests. Do not touch M03-M08 generation algorithms or M08 PNG/export contracts.

## 18. AUDIT CONFIDENCE

HIGH for the four findings because they follow directly from the authoritative prompt and static control flow/data identity in the committed implementation.

MEDIUM-HIGH for overall runtime health because broad builder regression evidence exists but independent execution was unavailable.

## 19. FINAL VERDICT

FAIL

Open findings:

- `F-PAG-M09-C001-001`
- `F-PAG-M09-C001-002`
- `F-PAG-M09-C001-003`
- `F-PAG-M09-C001-004`

PAG-M09 remains OPEN. `PAG-0901..PAG-0930` remain unchecked. PAG-M10+ remains blocked.

## 20. REQUIRED REMEDIATION

Create bounded `PAG-M09-C002 — Manifest Integrity, Reproduce Fidelity & Acceptance Evidence Remediation`.

C002 must:

1. fail closed on any semantic mutation of recorded batch history/terminal state and cross-bind accepted records to exact accepted bundles;
2. reproduce with the exact recorded M08 quality policy instead of current defaults;
3. bind batch/candidate identity to the complete immutable exemplar/provenance + policy environment;
4. add the missing authoritative reproduce, determinism, cross-process, quality, rectangular, path-safety and corruption evidence;
5. preserve the accepted C001 CLI architecture, zero runtime dependencies, local-only behavior, M08 provenance and all M00-M08 contracts.
