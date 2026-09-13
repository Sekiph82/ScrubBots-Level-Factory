# PAG-SP03-C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure
Document role: CODEX BUILDER LOG

## Start checkpoint

- Starting timestamp: 2026-09-13T09:52:13.4146057+03:00.
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`.
- Workspace: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD: `03ea6dd28dc44dad752a1d71e040db4868fe7fc8`.
- `origin/main`: `03ea6dd28dc44dad752a1d71e040db4868fe7fc8`.
- Starting divergence: `0 0`.
- Synchronization: fetched GitHub `origin` and fast-forwarded only; no reset, rebase, force-push, discard, or sibling-repository access.
- Preserved pre-existing dirt: `docs/migration/legacy-task-trackers/EVENTS.jsonl`, `docs/migration/legacy-task-trackers/PROJECT.json`, `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and `review/m10.zip`. These files are outside this cycle scope.

## Authority and scope

Read from GitHub before implementation:

- `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, the machine block in `.hiveai/TASKS.md`, `.hiveai/EVENTS.jsonl`, `tasks.md`, `.hiveai/CYCLE_INDEX.md`, `AGENTS.md`, and `GOVERNANCE.md`.
- Authoritative prompt: `PAG-SP03-C002 — Bounded Decode, Deep Immutability & Raw-to-Normalized Provenance Closure`.
- Previous strict audit: `PAG-SP03-C001_RAW_CAPTURE_AND_DETERMINISTIC_24X24_NORMALIZATION_FOUNDATION_STRICT_AUDIT.md`.

Scope is limited to SP03-C002 findings: bounded incremental PNG decode, immutable nested normalization report state, exact raw-to-normalized provider/request provenance binding, and fail-closed LEVEL_ART request legality. No Magnific or PixelLab calls, credits, network generation, SP04, M11, tracker edits, audit edits, or main ScrubBots repository access.

The required C002 log path was verified absent in the current workspace before this file was created. C002 source/test files were clean at that checkpoint; this log is created and verified before reapplying any C002 source or test edit.

## Planned implementation

1. Replace unrestricted PNG decompressor flushing with an incremental hard budget of exact scanline length plus one sentinel byte, rejecting overlength, truncation, trailing data, and missing EOF.
2. Deep-copy and freeze `SemanticNormalizationReport.crop_pad`.
3. Carry a checked immutable raw-source provenance snapshot and normalization-request snapshot into `SemanticNormalizedArtifact`, with an immutable construction fingerprint so coordinated field tampering fails closed.
4. Reject every LEVEL_ART normalization request at construction until the canonical palette and difficulty policy exists, using the permitted minimal alternative.

## Chronological implementation record

- Verified the required log path with `Test-Path` before reapplying C002 source/test edits. The earlier workspace note claiming the path existed was inconsistent with the filesystem; the discrepancy was corrected by restoring the C002-only edits, creating this log, verifying it, and then reapplying them. No unrelated dirty files were changed.
- Replaced the PNG decoder's unrestricted `decompress()` plus `flush()` path with incremental 65,536-byte compressed-input processing and an exact scanline-length-plus-one hard output budget. The decoder now rejects overlength output, truncated streams, trailing compressed/unused data, and missing zlib EOF without unbounded expansion.
- Added `SemanticSourceProvenance` as an immutable raw-artifact snapshot. `SemanticNormalizedArtifact.from_raw_artifact()` is the checked construction path and binds the exact raw digest, provider candidate/provider fields, request digest, normalization request policies/dimensions, report policies/input hash, output dimensions, and pixel hash. A construction fingerprint makes later coordinated field replacement fail closed.
- Made `SemanticNormalizationReport.crop_pad` a copied `MappingProxyType` and validated its scalar values, so caller mutation and stored mapping mutation cannot alter report state.
- Changed `SemanticNormalizationRequest` to reject all `LEVEL_ART` construction with a stable typed `SemanticNormalizationError`, the minimal permitted legality alternative until canonical palette/difficulty policy exists.
- Exported `SemanticSourceProvenance` through the normalization, semantic, and package public surfaces and documented the C002 boundary in `src/scrubbots_pixel_factory/semantic/README.md`.
- Added focused tests for compact decompression bombs without a giant expanded Python bytes object, exact expected-plus-one output, truncated/trailing zlib streams, deep report immutability, provenance/request/report tampering, and fail-closed LEVEL_ART request construction.

## Verification

- `python -m pytest -q tests/unit/test_sp03_normalization.py` — 14 passed, 1 pre-existing `PytestCacheWarning` (Windows access denied creating `.pytest_cache`).
- `python -m pytest -q tests/unit/test_sp01_semantic_contracts.py tests/unit/test_sp02_provider_bridges.py tests/unit/test_sp03_normalization.py` — 78 passed, same warning.
- `python -m pytest -q` — 459 passed, same warning, in 227.10 seconds.
- `python -m compileall -q src tests` — passed.
- Standalone package import including `SemanticSourceProvenance` — passed.
- `scrubbots-pixel --help` — passed; no provider API or network generation was invoked.
- `git diff --check` — passed.
- Source-policy check: C002 changes are limited to local standard-library PNG normalization, provenance contracts, tests, and documentation; no runtime dependency, provider call, network access, Magnific/PixelLab invocation, or third-party asset was added.

## Files changed in scope

- `src/scrubbots_pixel_factory/semantic/normalization/core.py`
- `src/scrubbots_pixel_factory/semantic/normalization/__init__.py`
- `src/scrubbots_pixel_factory/semantic/__init__.py`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/semantic/README.md`
- `tests/unit/test_sp03_normalization.py`
- `.hiveai/codex-logs/PAG-SP03-C002_BOUNDED_DECODE_DEEP_IMMUTABILITY_AND_RAW_TO_NORMALIZED_PROVENANCE_CLOSURE_CODEX_LOG.md`

## Publication checkpoint

- Final verification timestamp before commit: 2026-09-13T12:42:28.8265939+03:00.
- Implementation/merge publication commit: `e0059176ec2a599a80c80d945de73ec2a2beec03`.
- Builder-log publication commit: `ff7395e8e03db757e6eaf61838274dc61a4d7780`.
- Verified after `git fetch origin` at the final pre-log-update checkpoint: local HEAD `ff7395e8e03db757e6eaf61838274dc61a4d7780` equals `origin/main` `ff7395e8e03db757e6eaf61838274dc61a4d7780`; divergence `0 0`.
- Final scoped status: no staged or unstaged C002 files. Preserved unrelated dirt remains exactly as listed in the start checkpoint.

## Push correction and final publication

- First implementation push attempt: `git push origin main` was rejected because GitHub `origin/main` advanced from the starting checkpoint to `b28b55bb04223574ecf9137d93d98963059cd169` with the current C002 prompt, tracker, and independent audit. No force-push or reset was used.
- Fetched `origin`, confirmed local `HEAD...origin/main` was `1 3`, and merged `origin/main` with the non-destructive `ort` strategy. The merge brought in only the GitHub-authoritative C002 prompt/audit and tracker changes; no local product or preserved dirty file was discarded.
- Merge checkpoint timestamp: 2026-09-13T12:43:27.8252301+03:00. Merge HEAD: `e0059176ec2a599a80c80d945de73ec2a2beec03`; `origin/main`: `b28b55bb04223574ecf9137d93d98963059cd169`; pre-publication divergence: `2 0`.
- The final log update and publication commit are being created after the implementation and merge chronology above; this is the final log-only publication step.

The final log-only publication update itself is intentionally not self-recorded by SHA inside this file. After its push, `git fetch origin` and equality verification are required to complete the terminal checkpoint without creating a further self-referential commit.
