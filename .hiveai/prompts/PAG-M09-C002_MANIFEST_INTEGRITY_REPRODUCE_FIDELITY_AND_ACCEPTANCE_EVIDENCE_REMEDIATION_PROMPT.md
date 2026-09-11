# PAG-M09-C002 — Manifest Integrity, Reproduce Fidelity & Acceptance Evidence Remediation
Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION
Builder: Codex
Independent auditor / tracker owner: ChatGPT
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
Canonical branch: `main`
Canonical current-state tracker: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/TASKS.md`

Previous strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M09-C001_CLI_AND_LOCAL_BATCH_GENERATION_STRICT_AUDIT.md`

Previous builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M09-C001_CLI_AND_LOCAL_BATCH_GENERATION_CODEX_LOG.md`

## 1. Mission

Close only the four findings from the M09 C001 strict audit:

- `F-PAG-M09-C001-001` resume accepts semantically tampered batch history;
- `F-PAG-M09-C001-002` reproduce substitutes current default M07 quality policy for recorded policy;
- `F-PAG-M09-C001-003` batch identity omits immutable exemplar provenance;
- `F-PAG-M09-C001-004` mandatory reproduce/determinism/path acceptance evidence is incomplete.

Preserve the accepted C001 architecture: standard-library `argparse`, zero runtime dependencies, `generate_candidate()`, local-only exemplar loading, M07 quality, M08 bundle export/read, exact duplicate semantics, atomic local manifest writes and Windows-friendly CLI surface.

Do not begin M10 or M11. Do not modify accepted M03-M08 production generator/output/quality algorithms merely to satisfy M09.

## 2. Current tracker authority

Root `TASKS.md` is the only current project-status tracker. Hidden migrated tracker/control-plane files are historical only and must not be revived.

Codex is builder only. Do not mark `PAG-0901..PAG-0930` complete, do not declare M09 accepted, and do not author an independent audit.

## 3. GitHub-first start

Before edits read from GitHub `main`:

1. root `TASKS.md`;
2. `AGENTS.md` and `GOVERNANCE.md`;
3. M09 C001 prompt, builder log and strict audit;
4. current `src/scrubbots_pixel_factory/cli/main.py` and M09 tests;
5. M07 `QualityPolicy` / `QualityReport` contracts;
6. M08 artwork/bundle/quality-binding contracts;
7. M05 exemplar identity/provenance contracts;
8. M02 request/RNG/result contracts;
9. this C002 prompt.

Authorized local mirror only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never use or modify:
`C:\Users\sekip\Desktop\ScrubBots`

Synchronize non-destructively.

## 4. Matching builder log

Before the first C002 source/test/doc edit create:

`.hiveai/codex-logs/PAG-M09-C002_MANIFEST_INTEGRITY_REPRODUCE_FIDELITY_AND_ACCEPTANCE_EVIDENCE_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M09-C002 — Manifest Integrity, Reproduce Fidelity & Acceptance Evidence Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record start HEAD/origin/status, authority reads, every failing focused test and correction, exact test counts, implementation commit, push, completed-log publication and final post-completed-log `HEAD == origin/main`, divergence `0 0` checkpoint.

## 5. Preserve accepted C001 behavior

Do not weaken:

- `scrubbots-pixel` and `python -m scrubbots_pixel_factory.cli` entry points;
- generate/reproduce/batch command names and stable exit-code meanings;
- canonical explicit seed parsing;
- OS entropy only at omitted single-generation seed boundary;
- local JSON exemplar loading into accepted `Exemplar`/`ExemplarRegistry`;
- `GeneratorRouter.generate_candidate()` candidate-wrapper path;
- quality rejection before accepted single export;
- M08 bundle bytes/provenance rules;
- deterministic attempt seed derivation;
- exact hash + logical-cell duplicate collision safety;
- finite max-attempt behavior;
- same-directory atomic manifest write;
- zero runtime dependency and offline boundary.

## 6. Manifest semantic integrity

Strengthen `_validate_manifest()` and resume verification so a manifest is not accepted merely because list lengths and attempt indices look plausible.

### 6.1 Exact root/state invariants

Require at minimum:

- `0 <= next_attempt_index <= max_attempts`;
- `0 <= accepted_count <= requested_count`;
- `len(attempts) == next_attempt_index`;
- `len(accepted) == accepted_count`;
- `COMPLETE` iff `accepted_count == requested_count`;
- `EXHAUSTED` iff `accepted_count < requested_count` and `next_attempt_index == max_attempts`;
- `IN_PROGRESS` iff target is unmet and attempts remain;
- a completed target must not also claim exhausted/in-progress state.

### 6.2 Exact attempt record schema

Define one exact version-1 attempt-record field set and validate type/meaning for every field.

For each `attempt_index = N`:

- recorded `attempt_seed` must equal exactly `DeterministicRNG(root_seed).retry_seed(N)` with correct typed-seed representation;
- status must be one accepted enum/value such as `GENERATOR_FAILURE`, `QUALITY_REJECTED`, `DUPLICATE`, `ACCEPTED`;
- generator failure must have a failure code and must not pretend to have a quality decision/grid hash;
- successful generated grids must have dimensions, grid hash and quality decision;
- quality rejection must have `REJECT` + ordered rejection codes and no accepted path/candidate ID;
- duplicate must have `ACCEPT`, grid hash and valid `duplicate_of`, but no accepted bundle path of its own;
- accepted must have `ACCEPT`, grid hash, candidate ID and safe relative path;
- reject impossible mixed states.

Do not silently repair malformed historical records.

### 6.3 Accepted-record cross-binding

Require accepted history to correspond one-to-one, in deterministic order, with attempt records whose status is `ACCEPTED`.

For every accepted entry, cross-bind:

- attempt index;
- exact typed attempt seed;
- candidate ID;
- grid hash;
- relative path;
- width/height.

No duplicate accepted candidate IDs or relative paths are permitted.

### 6.4 Accepted bundle cross-binding

During resume verification, `read_bundle()` each accepted relative path and require at minimum:

- bundle candidate ID == manifest accepted candidate ID;
- bundle artwork width/height == manifest accepted width/height;
- bundle artwork grid hash == manifest accepted grid hash;
- embedded M02 request typed seed == manifest accepted attempt seed;
- embedded request template fields match immutable manifest request template except per-attempt seed/resolved dimensions owned by accepted upstream contracts;
- generator mode/config/provenance remain valid under M08.

Do not trust a manifest value merely because the bundle itself is valid.

### 6.5 Prior rejection/history immutability

Resume must reject tampering of prior:

- attempt seed;
- status;
- failure code;
- quality decision;
- rejection codes;
- grid hash;
- duplicate relation;
- candidate ID/path;
- dimensions;
- accepted record relation;
- terminal state/count/index.

Where a field can be recomputed from an existing accepted bundle or deterministic batch contract, recompute and compare. Do not replay every rejected generator attempt solely to validate non-reconstructible result details unless necessary; validate all directly reconstructible identity/state relations.

## 7. Exact reproduce quality-policy fidelity

M08 stores the complete quality report under the quality binding, including the policy used to make the decision.

`reproduce` must not call the current default policy and then hope the bytes match.

Implement a strict parser/reconstructor for the recorded M08 quality policy:

- require the accepted quality-binding/report schema/version/field shape already guaranteed or exposed by M08;
- read the exact recorded `quality.report.policy` data;
- construct `QualityPolicy` from exactly that recorded policy;
- reject unsupported/malformed policy version/data;
- reevaluate the reproduced grid using that recorded policy;
- require decision/rejection codes/report and rebuilt M08 metadata bytes to match the original;
- never substitute today's defaults for missing historical policy fields.

Add a positive known-answer test using a supported non-default policy whose bundle reproduces byte-identically.

Add negative policy tamper/schema/version tests where applicable.

Do not change M07 policy semantics or M08 quality binding.

## 8. Batch identity must bind the complete immutable environment

Current C001 batch identity excludes `exemplar_identities` even though the registry determines WFC-bearing output.

Build batch identity from the complete immutable V1 batch environment, including at minimum:

- request template;
- typed root seed;
- requested accepted count;
- max attempts;
- exact ordered exemplar identities/provenance used by the registry;
- exact persisted M07 quality policy/version/data.

The identity serialization must be canonical and machine-independent.

The same complete immutable environment must yield the same batch ID. Changing exemplar content/provenance or persisted policy must yield a different batch ID.

Update manifest validation to rederive this complete identity.

### Candidate IDs

Candidate IDs must remain deterministic and collision-resistant. They must not collide for distinct immutable batch environments. A strong design is:

`<batch-id>-<attempt-index>-<request-or-grid-digest-prefix>`

Exact formatting is your implementation choice, but it must be filesystem-safe and tested. Never use Python `hash()`, time or UUID.

No accepted candidate ID may repeat within a manifest.

## 9. Restore the authoritative reproduce negative matrix

Add direct tests for every C001 prompt section-12 mandatory case, including:

1. malformed metadata JSON;
2. wrong M08 metadata schema/version;
3. unsupported M02 request schema version;
4. unsupported generator-options version/namespace;
5. missing required request field;
6. changed typed seed;
7. changed generator mode/version;
8. changed recorded original grid hash;
9. missing required WFC exemplar;
10. wrong exemplar ID/content/provenance where reconstructibly detectable;
11. successful regeneration whose logical-grid hash differs from the recorded artifact.

Use real bundle-level tests. Do not satisfy several cases with one generic assertion if it does not prove the intended gate.

Retain positive MATCH evidence for at least accepted MASK and RULES artifacts and rich WFC with matching local synthetic exemplar.

## 10. Restore the section-20 deterministic acceptance matrix

Add direct bounded evidence for every authoritative M09 C001 prompt section-20 item. In particular, current C001 evidence must be strengthened to include:

- same explicit single request => same deterministic candidate ID and byte-identical M08 files;
- omitted seed exact print/metadata binding;
- auto-dimension CLI bounds + recorded resolved dimensions;
- rectangular single generation;
- invalid dimension/mode/options no traceback;
- deliberate quality rejection returns exact quality-reject exit code and stable codes;
- positive MASK and RULES reproduce MATCH;
- request/hash/version tamper detection;
- rich reproduce matching/missing/wrong exemplar;
- deliberate reject/duplicate scenario where attempt count differs from accepted count;
- every attempted seed equals the deterministic derivation;
- max-attempt exhaustion;
- exact duplicate detection without mutation;
- deterministic unique candidate IDs;
- interrupted/resumed output byte equality with uninterrupted output;
- completed resume byte no-op;
- same batch config/root seed produces identical manifest and accepted bundle bytes in separate processes under at least two different `PYTHONHASHSEED` settings;
- different root batch seeds can produce different accepted sets;
- genuinely rectangular batch path;
- generation succeeds inside a network-blocked boundary.

Do not replace actual batch cross-process/hash-seed evidence with `--help` text comparison.

## 11. Path and corruption negative evidence

Add M09-specific negative tests for:

- traversal/absolute/unsafe accepted manifest relative paths;
- candidate-ID traversal through the CLI surface where explicit IDs are accepted;
- accepted bundle candidate ID mismatch versus manifest;
- accepted bundle dimensions/hash/request-seed mismatch versus manifest;
- tampered prior attempt seed;
- tampered status/rejection code relation;
- forged COMPLETE/EXHAUSTED/IN_PROGRESS state;
- accepted record not matching an ACCEPTED attempt;
- duplicate accepted candidate ID/path.

Expected domain failures must return a stable non-zero CLI code without traceback noise.

## 12. Batch review evidence

Preserve the deterministic batch report and M07 review pack.

Ensure the human-readable report remains sufficient to trace each generated-grid attempt status (`ACCEPTED`, `QUALITY_REJECTED`, `DUPLICATE`) back to attempt index, typed seed, hash and relation. If the existing report already satisfies this after the state schema is tightened, do not redesign the review layer.

## 13. Scope boundary

Production changes should normally remain within:

- `src/scrubbots_pixel_factory/cli/**`;
- M09 tests;
- M09 CLI documentation/entrypoint only if required.

Do not modify M03-M08 production algorithms. Do not add dependencies. Do not begin M10/M11.

## 14. Required verification

Run and record at minimum:

- all new C002 focused manifest integrity tests;
- all strict reproduce negative tests;
- non-default recorded quality-policy reproduce test;
- complete section-20 deterministic acceptance matrix;
- batch identity/exemplar collision tests;
- path/corruption tests;
- Windows module/installed command smoke;
- actual separate-process batch determinism under at least two `PYTHONHASHSEED` values;
- network-blocked generation test;
- relevant M08 output tests;
- representative M03-M07 regressions;
- full `python -m pytest -q`;
- `python -m compileall -q src tests`;
- standalone package import;
- `python -m scrubbots_pixel_factory.cli --help`;
- installed `scrubbots-pixel --help` if editable-install evidence is available;
- `git diff --check`;
- offline/no-resize/no-new-dependency static scans.

Record exact commands/counts and all material failures/corrections.

## 15. Publication gate

Exit only when:

1. all four C001 findings are closed;
2. all focused/full regressions pass;
3. no M10/M11 or accepted M03-M08 production algorithm change exists;
4. implementation and matching C002 builder log are committed and pushed to `main`;
5. after completed-log publication, `git fetch origin main` proves local `HEAD == origin/main` and `git rev-list --left-right --count HEAD...origin/main` returns `0 0`, recorded in the log.

Then stop and return the C002 builder log for independent ChatGPT strict audit.
