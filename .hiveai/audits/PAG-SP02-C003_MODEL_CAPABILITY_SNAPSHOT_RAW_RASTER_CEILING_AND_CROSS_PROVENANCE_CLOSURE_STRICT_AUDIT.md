# PAG-SP02-C003 — Model Capability Snapshot, Raw Raster Ceiling & Cross-Provenance Closure
Document role: CHATGPT STRICT AUDIT

## 1. VERDICT

**PASS**

SP02-C003 closes the four MAJOR residuals and one MINOR semantic-provenance issue carried from the C002 audit. The provider bridge is now technically smoke-ready.

Severity summary:

- BLOCKER: 0
- MAJOR: 0
- MINOR: 1
- NOTE: 2

The remaining MINOR is documentation-only and does not affect deterministic identity, provider execution, result import, or smoke readiness.

No live Magnific or PixelLab generation was performed during this code audit. Paid-provider execution becomes authorized only after this PASS according to the canonical tracker.

## 2. CONTRACT RECOVERY

Audited against:

1. root `TASKS.md` as the only current status tracker;
2. `.hiveai/prompts/PAG-SP02-C003_MODEL_CAPABILITY_SNAPSHOT_RAW_RASTER_CEILING_AND_CROSS_PROVENANCE_CLOSURE_PROMPT.md`;
3. `.hiveai/audits/PAG-SP02-C002_PROVIDER_CONTRACT_FIDELITY_RESULT_IDENTITY_AND_SMOKE_READINESS_REMEDIATION_STRICT_AUDIT.md`;
4. `.hiveai/audits/PAG-SP02-C001_MAGNIFIC_AND_PIXELLAB_PROVIDER_BRIDGES_STRICT_AUDIT.md`;
5. `docs/SEMANTIC_PROVIDER_AUTHORITY_V02.md`;
6. `docs/MAGNIFIC_PROVIDER_AUTHORITY_V01.md`;
7. accepted SP01 semantic contracts/provider boundary;
8. current SP02 provider code, fixtures and tests;
9. official public `pixellab-code/pixellab-python` SDK files;
10. current owner-authorized Magnific image-model catalog, read-only.

Required closure points recovered:

- raw returned-provider raster bound must be separate from logical/requested dimensions;
- Magnific jobs must use pinned truthful per-model capability snapshots and unknown models must fail closed before canonical job creation;
- result-manifest identity must exclude mutable diagnostic prose;
- Magnific request/job/manifest and PixelLab request/job/candidate/manifest chains must be checked as one provenance chain;
- Magnific failure actual-model provenance must be optional when not observed;
- no SP03 normalization or SP04 qualification may be started in C003;
- no provider credits may be spent during C003 builder work.

## 3. BRANCH / HEAD / DIFF SCOPE

Builder start HEAD: `dad806aa397a43aee7b99a437725658d1fe069ad`.

Implementation commit: `013d8a169ffa8f2ecd4c48052a10cdccbd92c53b`.

Terminal builder-log commit on GitHub `main`: `35b6720c995538674f599c2abf5dc757ad474f4d`.

Compare `dad806a..35b6720` is ahead by 2 commits. Changed paths are limited to:

- matching C003 builder log;
- semantic public exports/constants;
- semantic raw-candidate bound;
- Magnific provider bridge/export;
- PixelLab bridge;
- provider README;
- Magnific smoke fixture;
- focused SP02 tests.

No accepted M00-M10 generator algorithm, rejected M10 visual evidence, root tracker, SP03/SP04 implementation, or main ScrubBots repository code was modified by Codex.

Scope discipline: **PASS**.

## 4. ACCEPTANCE CRITERIA MATRIX

| Area | Result | Audit assessment |
|---|---|---|
| Raw returned-raster ceiling | PASS | `SEMANTIC_RAW_RASTER_MAX_DIMENSION = 8192`; requested dimensions remain at existing 1024 request contract |
| 2k/4k Magnific raw candidates | PASS | focused tests cover 2048, 4096 and 8192; raw candidate remains blocked from M08 artwork |
| Magnific pinned model snapshots | PASS | immutable model-specific snapshot type and fail-closed lookup introduced |
| `recraft-v4-1` truth | PASS | 11 ratios, no `21:9`, STYLE-only reference role; matches current connected catalog |
| `seedream-5-pro` truth | PASS | exact 8 ratios, REFERENCE/STYLE, `1.5k`/`2k`; matches current connected catalog |
| `imagen-nano-banana-2-lite` truth | PASS | exact 10 ratios, REFERENCE/STYLE; matches current connected catalog |
| Unknown model | PASS | absent model fails through pinned snapshot lookup before canonical job creation |
| Resolution/quality override validation | PASS | explicit values checked against selected pinned model snapshot |
| Smoke fixture snapshot | PASS | canonical `recraft-v4-1` fixture contains exact pinned ratio/role/options snapshot |
| Failure diagnostic identity | PASS | `failure_reason` removed from Magnific and PixelLab result-manifest identity while retained in full serialization |
| Magnific request/job/manifest binding | PASS | request digest, job digest, provider/config/version, model, dimensions, seed, count, ratio, prompt, roles and snapshot checked |
| PixelLab request/job/candidate binding | PASS | checked construction validates provider/version/config/engine/workflow/seed/dimensions/controls/input provenance and output dimensions |
| Magnific failure actual model | PASS | non-success may omit observed actual model; reported drift fails closed |
| C002 PixelLab behavior | PASS | exact dimensions, deterministic provider seed, secret isolation and BitForge style strength preserved |
| No early normalization | PASS | raw provider candidate still raises `SemanticNormalizationRequiredError` for M08 artwork |
| Full regression | BUILDER PASS / AUDITOR UNVERIFIED | builder: 445 passed; audit clean clone blocked by DNS |
| Paid/live calls | PASS | none performed by builder or this code audit |

## 5. BUILDER CLAIMS VS REPOSITORY TRUTH

The builder claims are materially supported by current repository state.

Confirmed:

- request/logical dimensions remain separately bounded from returned raw raster dimensions;
- returned raw dimensions through 8192 are representable;
- model-specific Magnific snapshot data is carried in canonical job identity;
- unknown models no longer inherit a permissive global model snapshot;
- `recraft-v4-1` generic REFERENCE is rejected during job preparation while STYLE remains supported;
- explicit unsupported Magnific resolution/quality values fail closed;
- result-manifest digest no longer changes when only failure prose changes;
- coordinated Magnific request-A/job-B pairing is rejected;
- coordinated PixelLab candidate/request/job mismatches are rejected;
- Magnific failure constructors no longer fabricate an observed actual model.

Builder reports 26 focused SP02 tests, 64 combined SP01+SP02 tests after final mismatch cases, and 445 full repository tests passing.

## 6. FILE / SYMBOL EVIDENCE

Primary inspected implementation:

- `src/scrubbots_pixel_factory/semantic/contracts.py`
  - `SEMANTIC_RAW_RASTER_MAX_DIMENSION`
  - `SemanticImageCandidate.__post_init__()`
- `src/scrubbots_pixel_factory/semantic/providers/magnific/bridge.py`
  - `MagnificModelCapabilitySnapshot`
  - `MAGNIFIC_MODEL_CAPABILITY_SNAPSHOTS`
  - `get_magnific_model_snapshot()`
  - `MagnificJobSpec.from_request()`
  - `MagnificResultManifest.identity_dict()`
  - `MagnificResultManifest.import_result()`
- `src/scrubbots_pixel_factory/semantic/providers/pixellab/bridge.py`
  - `_validate_candidate_binding()`
  - `PixelLabResultManifest.from_candidate()`
  - `PixelLabResultManifest.identity_dict()`
  - `PixelLabProvider.manifest_for()`
- `tests/fixtures/sp02/magnific_smoke_job.json`
- `tests/unit/test_sp02_provider_bridges.py`
- `src/scrubbots_pixel_factory/semantic/providers/README.md`

Official PixelLab SDK re-check:

- `pixellab/__init__.py` exports `PixelLabClient as Client`, matching the adapter's lazy `pixellab.Client` lookup;
- `PixelLabClient` accepts `secret` and `base_url`, matching adapter construction;
- official `Base64Image` exposes `pil_image()`, matching the adapter's lossless PNG import fallback.

## 7. FOCUSED TEST EVIDENCE

C003 focused tests cover the escaped C002 findings directly:

- 2048x2048, 4096x4096 and 8192x8192 raw returned rasters;
- >8192 rejection;
- raw candidate cannot masquerade as M08 artwork;
- exact `recraft-v4-1` and `seedream-5-pro` snapshot data;
- unknown model rejection;
- unsupported explicit resolution rejection;
- `recraft-v4-1` generic REFERENCE rejection;
- exact fixture equality with canonical job;
- Magnific failure reason A/B digest invariance;
- PixelLab failure reason A/B digest invariance;
- request-A/job-B Magnific mismatch rejection;
- PixelLab candidate/request/job mismatch and tampered provider/job/output rejection;
- BitForge style-strength regression preservation.

Builder chronology records one test-construction mistake during implementation, corrected before final runs. That is healthy evidence rather than a hidden failure.

## 8. REGRESSION EVIDENCE

Builder reports:

- final SP02 focused suite: 26 passed;
- final SP01 + SP02 combined suite: 64 passed;
- full repository suite: 445 passed in 231.73 seconds;
- `compileall`: PASS;
- package/provider imports: PASS;
- module and installed CLI help: PASS;
- scoped provider-network scan: PASS;
- credential-pattern scan: PASS;
- `git diff --check`: PASS.

Independent auditor clean-clone replay was attempted from GitHub but audit-container DNS could not resolve `github.com`. Runtime replay is therefore **UNVERIFIED**, not failed.

GitHub terminal HEAD has no commit-status checks and no associated workflow runs.

## 9. SECURITY / SAFETY / OFFLINE REVIEW

**PASS**.

- Magnific remains an offline local job/result bridge; no scraping/browser/private endpoint code introduced.
- PixelLab SDK remains optional/lazy and networked only on deliberate provider execution.
- PixelLab secret remains runtime-only and excluded from canonical identity/logging paths inspected.
- no credentials appear in C003 scope;
- no provider credits were consumed by Codex;
- diagnostic/audit/cost metadata does not contaminate deterministic provider-result identity.

## 10. ARCHITECTURE CONSISTENCY

**PASS**.

The intended architecture is now internally consistent:

`SemanticGenerationRequest -> explicit provider/model job -> raw provider raster -> provenance-bound SemanticImageCandidate -> SP03 normalization`.

Logical artwork limits and provider raster limits are distinct.

Provider capability truth is pinned at the explicit Magnific model level without making ordinary jobs depend on mutable live catalog queries.

PixelLab remains a direct official-SDK provider behind the same provider-neutral SP01 boundary.

No architecture restart occurred.

## 11. TRACKER / LOG / DOCUMENTATION TRUTHFULNESS

Builder correctly used root `TASKS.md` as current status authority and explicitly ignored local/legacy hidden tracker debris.

The builder log was created before C003 implementation edits.

One documentation-only inconsistency remains:

- the pinned snapshot objects store `observation_date="2026-09-11"`;
- provider README states the current smoke snapshot was observed on `2026-09-12`.

The observation date is explicitly non-identity metadata and does not alter job digest, capability values, or smoke execution. Current live catalog inspection during this audit confirms the pinned capability values themselves remain correct.

Classification: **MINOR**, non-blocking.

A second process note: the builder log records `0 0` divergence immediately before its final log-only commit and states the post-commit equality was verified, but it does not print the final `35b6720...` local/origin hashes and numeric divergence in the file. GitHub proves the terminal log-only commit exists on `main`; local terminal equality remains builder-asserted rather than independently observable.

Classification: **NOTE**.

## 12. FINAL REPOSITORY STATE

GitHub `main` terminal inspected HEAD: `35b6720c995538674f599c2abf5dc757ad474f4d`.

Implementation commit: `013d8a169ffa8f2ecd4c48052a10cdccbd92c53b`.

Final commit changes only the matching C003 builder log.

No GitHub commit statuses are present on terminal HEAD.

No GitHub Actions workflow runs are associated with terminal HEAD.

Repository state is technically acceptable for the first owner-authorized provider smoke.

## 13. OPEN CROSS-MILESTONE FINDINGS

- Live Magnific smoke has not yet been run.
- Live PixelLab smoke has not yet been run and additionally requires locally available `PIXELLAB_SECRET` plus explicit live-run authorization.
- SP03 normalization has not begun.
- SP04 model/workflow qualification has not begun.
- M11 remains blocked until later semantic artwork receives owner visual acceptance.
- M10 rejected 100-pack remains permanent negative semantic regression evidence.

These are downstream gates, not C003 implementation failures.

## 14. DEFECTS BY SEVERITY

### BLOCKER

None.

### MAJOR

None.

### MINOR — F-PAG-SP02-C003-001 — Snapshot observation-date documentation differs by one day

Code stores the pinned model observation date as `2026-09-11`, while provider README documents `2026-09-12` for the smoke snapshot.

Impact: documentation traceability only. Observation date is excluded from deterministic job identity, and current catalog values match the pinned snapshot.

Disposition: may be corrected during the next documentation touch; no C004 remediation cycle is required solely for this issue.

### NOTE — N-PAG-SP02-C003-001 — Independent test replay unavailable

Audit clean clone failed because the audit container could not resolve `github.com`. Builder's 445-test report remains the available runtime evidence.

### NOTE — N-PAG-SP02-C003-002 — Final local/origin equality after log-only commit is not printed

Builder prints equality before the final log-only commit and claims final equality after push, but omits the final numeric/hash line. GitHub terminal state confirms the pushed commit, but local equality cannot be independently observed.

## 15. TECHNICAL DEBT / UPGRADE OPPORTUNITIES

Non-blocking future hardening:

- model-specific capability narrowing could also be surfaced directly through a model-aware provider capability view for future SP09 UI, rather than relying on provider-level union plus `prepare_job()` validation;
- Magnific import could defensively revalidate all optional job-only execution options even for manually reconstructed dataclass instances, although the canonical `from_request()` path already validates them and job digest binds them;
- PixelLab provenance documentation should eventually distinguish provider wire encoding from project-owned lossless PNG bytes when the SDK supplies only decoded `Base64Image`/PIL access;
- add CI to remove reliance on builder-local pytest evidence.

None of these blocks the bounded SP02 smoke contract.

## 16. UNVERIFIED ITEMS

- independent replay of 445 tests: UNVERIFIED due audit-container DNS;
- live Magnific generation/result import: NOT RUN yet;
- live PixelLab generation: NOT RUN yet;
- PixelLab server-side acceptance of the exact smoke request: not proven until owner-authorized live call;
- long-term cloud-model byte determinism across provider revisions: explicitly outside project guarantee.

## 17. REGRESSION RISK

Current technical regression risk for proceeding to a **single controlled smoke**: **LOW-MEDIUM**.

The previously high-risk defects at the raw-raster, model-capability, result-identity and coordinated-provenance boundaries have direct code and focused-test closure.

Risk remains provider-runtime-specific rather than architecture-specific, which is exactly what the smoke step is intended to measure.

## 18. AUDIT CONFIDENCE

**HIGH** for static contract closure and current Magnific catalog truth.

**MEDIUM-HIGH** overall because independent pytest replay was unavailable.

Confidence is sufficient for a controlled one-candidate live smoke, not for declaring cloud-provider behavior permanently deterministic.

## 19. FINAL VERDICT

**PASS**

Disposition:

- `F-PAG-SP02-C002-001`: CLOSED;
- `F-PAG-SP02-C002-002`: CLOSED;
- `F-PAG-SP02-C002-003`: CLOSED;
- `F-PAG-SP02-C002-004`: CLOSED;
- `F-PAG-SP02-C002-005`: CLOSED;
- PAG-SP02-C003: **PASS / CLOSED**;
- PAG-SP02 provider bridge: **TECHNICAL PASS / LIVE SMOKE AUTHORIZED**;
- SP03/SP04 implementation should not be treated as dependent on unproven visual quality; first controlled provider smoke should be captured before provider qualification decisions.

## 20. REQUIRED REMEDIATION

No C004 code-remediation cycle is required.

Next action is not another Codex repair prompt.

Run one owner-authorized controlled Magnific smoke using the committed `recraft-v4-1`, 1:1, count-1 wizard fixture. Capture:

- exact provider/model;
- creation identifier;
- requested aspect ratio;
- returned image dimensions/format;
- immutable raw/result hash where available;
- bridge manifest/import evidence;
- credit/cost metadata when surfaced, outside deterministic identity.

PixelLab live smoke remains optional/pending until `PIXELLAB_SECRET` is available in the authorized execution environment and the owner explicitly authorizes that live API spend.
