# PAG-SP03-C003 — Provenance Seal & Construction Integrity Closure
Document role: CODEX BUILDER LOG

## Start checkpoint

- Starting timestamp: 2026-09-13T14:09:00.2483124+03:00.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Workspace: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Fetched GitHub `origin/main` and fast-forwarded local `main` non-destructively.
- Starting HEAD: `ae9537f644765a89268be950bdb1f1e9a5e1b60c`.
- `origin/main`: `ae9537f644765a89268be950bdb1f1e9a5e1b60c`.
- Starting divergence: `0 0`.
- Preserved pre-existing dirt: `docs/migration/legacy-task-trackers/EVENTS.jsonl`, `docs/migration/legacy-task-trackers/PROJECT.json`, `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and `review/m10.zip`. These files are outside C003 scope and remain untouched.

## Authority and scope

Read directly from GitHub before coding:

- Root `TASKS.md`, the only current project-status tracker.
- The authoritative SP03-C003 prompt and the SP03-C002 strict audit.
- Accepted SP01/SP02 contracts, SP03 C001/C002 implementation, `review/sp02/SP02_MAGNIFIC_LIVE_SMOKE_2026-09-13.md`, M07/M08/M09 provenance/export contracts, `AGENTS.md`, `GOVERNANCE.md`, and `CLAUDE.md`.

Legacy hidden `.hiveai` tracker/control-plane projections are not used as current task authority. This cycle implements only `F-PAG-SP03-C002-001` provenance construction sealing and `F-PAG-SP03-C002-002` builder authority/process correction. No TASKS.md edit, provider call, provider credit, SP04/M11 work, provider-bridge change, visual algorithm change, or main ScrubBots repository access is permitted.

## Planned construction-seal design

- `SemanticSourceProvenance` will use an `init=False` internal construction token and fingerprint. Normal creation will manually install the token only through `from_raw_artifact(raw)`; ordinary direct construction and `dataclasses.replace()` will fail closed. Serialization/digest paths will assert the source seal.
- `SemanticNormalizedArtifact` will make its token and fingerprint `init=False`. Its checked factory will install them internally, derive the fingerprint unconditionally from accepted source/request/report/output inputs, and assert integrity on construction and deterministic serialization/digest. Callers cannot pass or reset either seal through normal dataclass APIs.
- Add explicit sensitivity tests for provider/version/workflow/model/request tampering, the coordinated source-A-digest attack, seal reset attempts, reference provenance retention, and stable valid-object digest/bytes.

## Chronological implementation record

- Replaced public seal fields on `SemanticSourceProvenance` with `init=False` construction token/fingerprint state. `from_raw_artifact(raw)` now allocates and initializes the sealed snapshot internally, validates fields, installs the fingerprint, and asserts integrity. Direct construction and `dataclasses.replace()` replacement of source fields cannot produce an accepted snapshot.
- Replaced public `init=True` token/fingerprint fields on `SemanticNormalizedArtifact` with `init=False` state. The checked factory installs the token, validates all source/request/report/output bindings, derives the fingerprint unconditionally, and the artifact asserts both its own and the source snapshot's integrity from `identity_dict()`, `canonical_dict()`, and `digest()` paths.
- Added direct constructor and `dataclasses.replace()` tests for provider id/version, workflow, model and request-digest changes; reference-input preservation; coordinated source-A-digest/provider replacement with attempted fingerprint reset; internal seal reset attempts; unavailable internal fields in the public signature; and stable canonical bytes/digest.
- Focused correction 1: the first focused run failed one existing provider-tamper assertion because the new fail-closed path reports `checked construction`; widened only that test's expected typed-error wording.
- Focused correction 2: the same existing request-digest assertion required the new fail-closed wording; updated its expected error alternatives.
- Focused correction 3: the existing foreign-source replacement assertion required the new fail-closed wording; updated its expected error alternatives.
- Focused correction 4: the existing report-tamper assertion required the new fail-closed wording; updated its expected error alternatives.
- No production algorithm, decoder, palette, alpha, resize, provider bridge, tracker, review, or task-state changes were made.

## Verification

- `python -m pytest -q tests/unit/test_sp03_normalization.py` — 17 passed, 1 pre-existing `PytestCacheWarning`.
- `python -m pytest -q tests/unit/test_sp01_semantic_contracts.py tests/unit/test_sp02_provider_bridges.py tests/unit/test_sp03_normalization.py` — 81 passed, same warning.
- `python -m pytest -q` — 462 passed, same warning, in 226.30 seconds.
- `python -m compileall -q src tests` — passed.
- Standalone package import including `SemanticSourceProvenance` and public seal-signature assertions — passed.
- `scrubbots-pixel --help` — passed; no provider API or network generation was invoked.
- `git diff --check` — passed.
- Scoped diff network/provider/secret scan — no matches.
- Source-policy check: C003 changes are limited to local standard-library provenance construction sealing and tests; no runtime dependency, provider call, network access, Magnific/PixelLab invocation, third-party asset, or visual algorithm change was added.

## Changed paths

- `src/scrubbots_pixel_factory/semantic/normalization/core.py` — production construction-seal implementation.
- `tests/unit/test_sp03_normalization.py` — coordinated-tamper and construction-integrity evidence.
- `.hiveai/codex-logs/PAG-SP03-C003_PROVENANCE_SEAL_AND_CONSTRUCTION_INTEGRITY_CLOSURE_CODEX_LOG.md` — this builder log.

## Publication checkpoint

- Final verification timestamp before commit: 2026-09-13T14:18:34.2620306+03:00.
- Pre-commit local HEAD: `ae9537f644765a89268be950bdb1f1e9a5e1b60c`.
- Pre-commit `origin/main`: `ae9537f644765a89268be950bdb1f1e9a5e1b60c`.
- Pre-commit divergence: `0 0`.
- Implementation commit: `f4e1594c89fd731da80149c268a63760e7a20eaa`.
- `git push origin main` — passed.
- Verified after `git fetch origin` at 2026-09-13T14:19:54.4682108+03:00: local HEAD `f4e1594c89fd731da80149c268a63760e7a20eaa` equals `origin/main` `f4e1594c89fd731da80149c268a63760e7a20eaa`; divergence `0 0`.
- Final scoped status before this terminal log publication: no staged or unstaged C003 source/test files. Preserved unrelated dirt remains exactly as listed in the start checkpoint.
- This final log update will be published as a log-only commit; a post-push fetch/equality check will complete the terminal checkpoint without writing a self-referential commit SHA into this file.
