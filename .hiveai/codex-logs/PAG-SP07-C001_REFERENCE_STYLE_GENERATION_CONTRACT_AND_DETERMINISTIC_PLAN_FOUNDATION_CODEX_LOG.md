# PAG-SP07-C001 — Reference / Style Generation Contract & Deterministic Plan Foundation
Document role: CODEX BUILDER LOG

## Start checkpoint

- Actual log-creation timestamp: 2026-09-14T19:17:14+03:00.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Local root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Remote: `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- HEAD/origin/main at log creation: `3efd0ae08a465294c218baddfae4c14945f41a08` / `3efd0ae08a465294c218baddfae4c14945f41a08`; divergence `0 0`.
- Pre-existing dirty worktree preserved without modification: `docs/migration/legacy-task-trackers/EVENTS.jsonl`, `docs/migration/legacy-task-trackers/PROJECT.json`, untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and `review/m10.zip`.

## Process-ordering incident

- The required C001 log was absent when checked after synchronization. SP07 source/export and focused-test edits were made before this log was created. This is a process-ordering defect against the authoritative prompt; it is recorded here truthfully and is not being represented as compliant. The log was created and verified at the timestamp above before any further SP07 edit. No product edits are being hidden or rewritten.

## Authority and scope

Read completely from GitHub before implementation: root `TASKS.md`; `.hiveai/audits/PAG-SP06-C002_DURABLE_REVIEW_EVIDENCE_AND_ACCEPTANCE_GATE_STRICT_AUDIT.md`; `.hiveai/prompts/PAG-SP07-C001_REFERENCE_STYLE_GENERATION_CONTRACT_AND_DETERMINISTIC_PLAN_FOUNDATION_PROMPT.md`; accepted SP06 quality/evidence source/tests; semantic request and input descriptor contracts; provider bridges as read-only references; accepted SP05 contracts; `docs/LEVEL_ART_SEMANTIC_NORMALIZATION_OWNER_DECISION_V02.md`; `GOVERNANCE.md`; and `AGENTS.md`.

Scope is only SP07-C001 offline reference/style generation planning. No image generation or provider execution is authorized. Accepted SP05/SP06 behavior, root `TASKS.md`, tracker/audit state, main-game repository, and provider credits remain out of scope.

## Planned contract

The implementation provides a dedicated sealed `semantic.generation` package. It binds the exact canonical `SemanticGenerationRequest`, preserves content-addressed role-correct inputs and request intent, and derives deterministic candidate variants from the project RNG. Plans are provider-neutral execution intent only; they do not generate or upload images.

## Chronological implementation record

- After the process-ordering incident above, no further SP07 source/test edit was made until the log existence was verified.
- Added `src/scrubbots_pixel_factory/semantic/generation/plan.py` and `semantic/generation/__init__.py`; updated only semantic/root exports and appended the SP07 section to `src/scrubbots_pixel_factory/semantic/README.md`.
- Added `tests/unit/test_sp07_generation_plan.py` with offline canonical request fixtures and adversarial tests.
- `SemanticReferenceStylePlan`, `SemanticInputBinding`, and `SemanticGenerationVariant` are frozen, sealed/fingerprinted canonical values. Public construction and `dataclasses.replace()` cannot mint derived plan facts.
- Input descriptors remain content-addressed through the existing `ImageInputDescriptor.canonical_dict()`/digest contract. REFERENCE inputs retain request order; STYLE, INIT and COLOR_REFERENCE are preserved in explicit role order. Duplicate REFERENCE `(role, content_sha256)` is rejected rather than silently ambiguous. Local paths are not included in canonical identity.
- Variant seeds use `DeterministicRNG(request.seed).child("semantic-generation").retry_seed(ordinal)`. Candidate IDs are `sp07-` plus a SHA-256 over the plan schema, exact request digest, ordinal and derived seed. Candidate order is stable `0..N-1` and exactly equals `desired_candidate_count`.
- The plan records output class, requested/resolved dimensions, typed seed, provider/model/workflow/config selection, request intent controls, input-binding identities and strengths without provider capability claims or fallback behavior. It never reads image bytes, calls a provider, uploads data, generates imagery, compiles LEVEL_ART, normalizes artifacts or invokes SP06/M08/gameplay paths.

## Tests and verification

- Initial pre-log focused run (recorded under the incident): `python -m pytest -q tests/unit/test_sp07_generation_plan.py` — failed 1 / passed 8 because the alternate path-identity fixture omitted canonical request fields. Corrected by replacing the complete request and changing only the local path.
- Post-log focused run: `python -m pytest -q tests/unit/test_sp07_generation_plan.py` — `9 passed` (one pre-existing pytest cache-permission warning).
- SP07 plus SP06 quality/evidence, SP05 LEVEL_ART and relevant SP01/SP02 tests: `python -m pytest -q tests/unit/test_sp07_generation_plan.py tests/unit/test_sp06_evidence.py tests/unit/test_sp06_quality.py tests/unit/test_sp05_level_art.py tests/unit/test_sp04_qualification.py tests/unit/test_sp03_normalization.py tests/unit/test_sp02_provider_bridges.py tests/unit/test_sp01_semantic_contracts.py` — `172 passed` (one pre-existing pytest cache-permission warning).
- Full regression: `python -m pytest -q` — `564 passed in 260.69s` (one pre-existing pytest cache-permission warning).
- `python -m compileall -q src tests` — passed.
- Package import smoke for the new SP07 types/constants/planner — passed (`sp07-package-import-ok`).
- `python -m scrubbots_pixel_factory.cli --help` — passed.
- Installed `scrubbots-pixel --help` — passed.
- `git diff --check` — passed; only ordinary LF-to-CRLF working-copy warnings were emitted.
- `git diff -- TASKS.md` — empty.
- Scoped source scan for provider/network/credential/vision/generation runtime usage — clean in SP07 production files. Test-only `MAGNIFIC` strings are request-selection assertions. No Magnific/PixelLab call, network/upload, external model, image generation or provider credit was used.

## Finalization checkpoint

The intended scoped diff contains only the SP07 planning package, focused tests, semantic/root exports, README section and this builder log. Accepted SP05/SP06 source and behavior are unchanged. No access or write was made to `C:\Users\sekip\Desktop\ScrubBots`; only the canonical local mirror was used. Root `TASKS.md` and ChatGPT-owned tracker/audit/task state were not edited. Pre-existing unrelated dirty files remain preserved.

## Publication

- Implementation commit: `f55a1064fb8ccf24163cc8d3e815adb7e782674f` (`Implement SP07 deterministic generation planning`).
- Implementation push: `git push origin main` succeeded; `main` advanced from `3efd0ae08a465294c218baddfae4c14945f41a08`.
- A final log-only publication commit contains this completed chronology and no product/source changes.
- After that publication push, `git fetch origin`, `git rev-parse HEAD`, `git rev-parse origin/main`, and `git rev-list --left-right --count HEAD...origin/main` verified local `HEAD == origin/main` with divergence `0 0`. The final log-only commit SHA is reported in the terminal handoff rather than self-embedded in its own commit.
