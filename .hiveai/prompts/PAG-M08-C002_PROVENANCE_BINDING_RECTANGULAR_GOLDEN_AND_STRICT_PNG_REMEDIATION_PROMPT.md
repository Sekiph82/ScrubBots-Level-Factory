# PAG-M08-C002 — Provenance Binding, Rectangular Golden & Strict PNG Remediation
Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous strict audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M08-C001_OUTPUT_EXPORT_CONTRACT_STRICT_AUDIT.md`

Previous builder log:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/codex-logs/PAG-M08-C001_OUTPUT_EXPORT_CONTRACT_CODEX_LOG.md`

Current tracker:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/TASKS.md`

## 1. Mission

Close only these three C001 findings:

- `F-PAG-M08-C001-001` — generator-specific WFC/HYBRID/AUTO provenance can be silently omitted and is not sufficiently cross-bound on read;
- `F-PAG-M08-C001-002` — direct rectangular row-major evidence and committed rectangular JSON/PNG golden evidence are missing;
- `F-PAG-M08-C001-003` — strict PNG decoder does not reject a non-empty IEND payload.

Preserve all accepted C001 architecture:

- immutable artwork JSON separate from quality state;
- exact one-cell = one-pixel logical PNG;
- canonical C01..C16 RGB only;
- deterministic filter-0 standard-library PNG encoding;
- preview as integer presentation replication only;
- deterministic filesystem bundle writes/conflict handling;
- current M07 quality binding;
- current GenerationResult/request/RNG binding;
- zero runtime dependencies;
- all accepted M00-M07 behavior.

Do not begin PAG-M09+.

## 2. GitHub-first authority

Before editing, read completely from GitHub `main`:

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. v3 machine block/current state in `.hiveai/TASKS.md`
4. `.hiveai/EVENTS.jsonl`
5. `tasks.md`
6. `.hiveai/CYCLE_INDEX.md`
7. `AGENTS.md`
8. `GOVERNANCE.md`
9. M08 C001 authoritative prompt
10. M08 C001 builder log
11. M08 C001 strict audit
12. current `src/scrubbots_pixel_factory/output/`
13. current M08 tests/goldens
14. WFC candidate/result contracts
15. HYBRID candidate/stage metadata contracts
16. AUTO candidate/attempt metadata contracts
17. M02 GenerationResult/request/RNG contracts
18. M07 quality contracts
19. this C002 prompt

GitHub `main` is current-state authority.

Authorized local workspace only:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Never modify or substitute:
`C:\Users\sekip\Desktop\ScrubBots`

Use non-destructive synchronization only. No hard reset, force push, blanket clean/restore, or silent rebase.

## 3. Matching builder log

Before the first C002 source/test/golden edit create:

`.hiveai/codex-logs/PAG-M08-C002_PROVENANCE_BINDING_RECTANGULAR_GOLDEN_AND_STRICT_PNG_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M08-C002 — Provenance Binding, Rectangular Golden & Strict PNG Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically and truthfully:

- timestamp/repository/branch/origin/starting HEAD;
- GitHub-first reads;
- preserved local pre-existing changes;
- exact remediation edits;
- focused failures and corrections;
- golden creation/regeneration;
- verification commands/results;
- final diff/status;
- implementation/evidence commit;
- push result;
- post-log-publication local HEAD == origin/main checkpoint.

Do not edit ChatGPT-owned tracker/audit/task acceptance state and do not self-audit.

## 4. Fix F-PAG-M08-C001-001: fail-closed rich generator provenance

The M08 output layer must never silently imply complete provenance while discarding generator-specific metadata that is owned outside `GenerationResult`.

### 4.1 Raw GenerationResult policy

Current public `export_result()` / `build_export_bundle()` accepts raw results from every mode. For WFC/HYBRID/AUTO, richer exemplar/stage/router evidence lives on candidate wrappers and can therefore be lost.

Choose a narrow, explicit contract. Preferred behavior:

- raw MASK/RULES successful `GenerationResult` export may remain supported when no required external candidate metadata exists;
- raw WFC/HYBRID/AUTO successful results must fail closed unless the caller explicitly supplies the authoritative generator metadata through a dedicated argument/API;
- alternatively, make the public rich-mode path require the candidate wrapper and document that contract clearly;
- do not fabricate missing metadata from incomplete fields;
- do not widen or weaken M02 `GenerationResult` merely to solve M08.

If an explicit `generator_metadata` argument is added, validate/canonicalize it with the same contract used for candidate-wrapper metadata and prove wrapper vs explicit-metadata export is deterministic and equivalent where appropriate.

### 4.2 Namespace/mode binding

Generator metadata namespace must agree with the outer generating mode:

- WFC result -> WFC metadata where required;
- HYBRID result -> HYBRID metadata;
- AUTO result -> AUTO metadata;
- simple MASK/RULES may have no external rich metadata unless a documented authoritative wrapper genuinely supplies it.

Do not allow a WFC payload to be relabeled as AUTO/HYBRID or vice versa.

### 4.3 Semantic cross-binding on read

Strengthen `_validate_metadata()` so reconstructible authoritative fields inside rich metadata are checked against the exact GenerationResult/request/artwork.

At minimum for WFC validate available bindings such as:

- metadata schema/version;
- `exemplar_id` agrees with the request's selected exemplar/style when the request records it;
- target palette agrees with the output/request palette truth;
- output dimensions agree with artwork dimensions;
- request-owned WFC options such as pattern size/periodicity/rotation/reflection/max attempts agree where present;
- attempt index is valid relative to recorded retry provenance/max attempts;
- do not invent provenance fields that the WFC candidate did not record.

At minimum for HYBRID validate available bindings such as:

- metadata schema/version and strategy agrees with outer hybrid request config;
- final dimensions/palette/grid/result digest evidence agrees where recorded;
- stage records remain in deterministic order and their request/result/digest bindings are not contradictory to the exported result/artwork where directly reconstructible.

At minimum for AUTO validate available bindings such as:

- metadata schema/version;
- configured candidate order/fallback semantics agree with the AUTO request;
- selected engine ID/version agrees with the successful outer result;
- attempt records are deterministic/ordered and the successful selected attempt agrees with the exported result where recorded.

Do not duplicate the full M05/M06 replay engines inside M08. Cross-bind the fields that M08 can authoritatively verify from exported request/result/artwork plus the accepted candidate metadata contract.

### 4.4 Mandatory provenance negative tests

Add tests that fail before the fix and pass after it:

1. raw successful WFC result exported without required rich metadata is rejected;
2. raw HYBRID result without required rich metadata is rejected;
3. raw AUTO result without required rich metadata is rejected;
4. rich candidate-wrapper exports remain accepted;
5. WFC `exemplar_id` tampered to an unrelated value is rejected by `read_bundle`;
6. WFC target palette/output dimensions or another deterministic request/artwork binding tampered is rejected;
7. HYBRID strategy/stage/final binding tamper is rejected;
8. AUTO selected-engine/attempt/config binding tamper is rejected;
9. wrong rich metadata namespace for the generating mode is rejected;
10. MASK/RULES raw-result export remains supported if that is the documented simple-mode contract.

Use stable project-owned `OutputContractError` failures. Do not silently repair metadata.

## 5. Fix F-PAG-M08-C001-002: real rectangular row-major evidence

The current unit test named as rectangular uses 20x20. Replace or supplement it with a genuinely rectangular legal artifact.

Use a deterministic project-owned fixture such as 20x21, 20x27, 21x20, or another legal rectangular board.

The logical cells must make row boundaries distinguishable so the test can directly prove:

`index = y * width + x`

At minimum assert known cells at:

- `(0,0)` -> index 0;
- `(width-1,0)` -> index `width-1`;
- `(0,1)` -> index `width`;
- at least one later `(x,y)` -> `y*width+x`.

Do not leave an unused tiny non-contract list pretending to be rectangular evidence.

## 6. Rectangular committed golden pair

Commit at least one deterministic rectangular M08 JSON/PNG golden pair under `tests/golden/fixtures/m08/`.

You may keep the existing square pair and add a rectangular pair, or deliberately replace the existing pair if the full golden requirements remain covered.

The rectangular golden test must prove:

- JSON canonical bytes equal committed bytes;
- width != height and both dimensions legal for the recorded difficulty;
- multiple canonical colors;
- local palette equals actual ascending used set;
- PNG dimensions exactly equal JSON logical dimensions;
- `encode_logical_png(...)` equals committed PNG bytes;
- decoded PNG cells equal JSON cells;
- raw RGB bytes equal canonical row-major JSON-derived RGB;
- row boundary/index behavior is consistent with `y*width+x`;
- no third-party artwork/provenance is introduced.

Keep golden generation deterministic with no timestamps, local paths or random UUIDs.

## 7. Fix F-PAG-M08-C001-003: strict IEND validation

The project encoder emits an empty IEND payload. The strict project-profile decoder must reject malformed IEND data.

Implement a direct parser gate requiring:

- exactly one IEND;
- IEND is final;
- IEND data length is exactly zero.

The first two already exist and must be preserved.

Add a focused negative test that constructs a PNG with:

- otherwise-valid project profile;
- non-empty IEND data;
- correct IEND CRC;

and proves `decode_logical_png()` raises `PNGContractError`.

Do not weaken CRC or chunk-order validation.

## 8. Preserve accepted C001 behavior

Do not redesign unless a focused failing test proves a new contradiction:

- artwork schema/key set/hash;
- canonical JSON byte policy;
- quality report binding;
- logical RGB mapping;
- filter-0 encoder;
- preview block replication;
- bundle conflict semantics;
- 59x59 support;
- cross-process determinism;
- zero dependencies.

Do not modify M03-M07 generation/quality production code to make M08 tests pass.

## 9. Optional Windows candidate-ID hardening

The C001 audit notes, but does not make acceptance depend on, Windows-specific filesystem names.

If touching candidate-ID validation, it is acceptable to strengthen it conservatively for Windows-first operation by rejecting trailing spaces/dots, Windows reserved device names and invalid path characters. If implemented, add tests and ensure no two accepted IDs can collapse to one normal Windows candidate path.

Do not turn this optional hardening into a large naming subsystem.

## 10. Required focused verification

At minimum run and record:

1. `tests/unit/test_m08_output.py`;
2. `tests/integration/test_m08_export_integration.py`;
3. `tests/golden/test_m08_export.py`;
4. all new rich-provenance negative tests;
5. direct rectangular row-major known-answer test;
6. rectangular committed golden test;
7. non-empty-IEND negative test;
8. rectangular bundle/preview round trip;
9. all four difficulty bands and 59x59;
10. repeated export determinism;
11. cross-process/PYTHONHASHSEED JSON+PNG determinism.

## 11. Regression verification

Run and log:

- M01/M02 contract tests;
- M03 MASK tests;
- M04 RULES tests;
- M05 WFC tests;
- M06 router/hybrid/replay/AUTO tests;
- all M07 quality/diversity tests;
- all M08 tests;
- full repository pytest;
- standalone package import.

Do not reduce or delete accepted regression coverage simply to get green counts.

## 12. Static/offline checks

Run and log checks proving:

- no runtime network/API/cloud path;
- no new dependency;
- no logical resize/resample/interpolation;
- preview remains integer replication only;
- no BG01/C17+/arbitrary RGB enters logical artwork;
- no M09+ implementation;
- no timestamps/absolute paths in deterministic goldens;
- `git diff --check` clean;
- final diff contains only bounded C002 files.

`pip check` may continue to show the previously documented local pytest/pytest-asyncio mismatch; record it truthfully and do not change unrelated dependencies merely to silence it.

## 13. Expected bounded source scope

Expected edits should primarily stay within:

- `src/scrubbots_pixel_factory/output/bundle.py`;
- `src/scrubbots_pixel_factory/output/png.py`;
- `src/scrubbots_pixel_factory/output/artwork.py` only if necessary for bounded candidate-ID hardening;
- `src/scrubbots_pixel_factory/output/README.md`;
- M08 unit/integration/golden tests;
- M08 golden fixtures;
- matching C002 builder log.

Do not edit `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `tasks.md`, `.hiveai/CYCLE_INDEX.md`, `.hiveai/audits/**`, historical prompts/logs, or M09+ files.

## 14. Stop condition

After implementation and verification:

1. commit focused C002 implementation/evidence;
2. push to `main`;
3. publish the completed matching builder log;
4. fetch origin;
5. record exact local HEAD, origin/main and divergence;
6. verify local HEAD == origin/main;
7. stop;
8. return the C002 builder-log GitHub link for independent ChatGPT strict audit.

Do not mark PAG-0801..PAG-0830 complete yourself. Only independent ChatGPT audit may close M08 and unblock M09.
