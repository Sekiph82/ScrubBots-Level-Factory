# PAG-SP04-C005 — Safe Ancillary PNG Compatibility for Live Magnific Raw Import
Document role: CODEX BUILDER LOG

## Start checkpoint

- Starting timestamp: 2026-09-14T00:53:25.5164878+03:00
- Canonical repository: `Sekiph82/ScrubBots-Level-Factory`
- Canonical root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
- Branch: `main`
- Starting `HEAD`: `9fcaaf297e0a4972dfc77bedf75244878cc5cffe`
- Starting `origin/main`: `9fcaaf297e0a4972dfc77bedf75244878cc5cffe`
- Starting divergence (`git rev-list --left-right --count HEAD...origin/main`): `0 0`
- Starting status: pre-existing dirt preserved: modified `docs/migration/legacy-task-trackers/EVENTS.jsonl`, modified `docs/migration/legacy-task-trackers/PROJECT.json`, untracked `.hiveai/EVENT_INDEX.json`, `.hiveai/HANDOFF.md`, `.hiveai/STATE.json`, and `review/m10.zip`.
- Synchronization: `git fetch origin` followed by non-destructive `git merge --ff-only origin/main`; fast-forwarded from `fab2860e1e6c811e5ddd2a1291a88b5282503fb2` to `9fcaaf297e0a4972dfc77bedf75244878cc5cffe`.
- No provider call or credit spend occurred.

## Authority and contracts read

- GitHub authoritative prompt: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_PROMPT.md`
- GitHub trigger evidence: `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/review/sp04/SP04_Q01_Q02_MAGNIFIC_LIVE_RAW_COMPATIBILITY_2026-09-14.md`
- `AGENTS.md`
- `GOVERNANCE.md`
- `CLAUDE.md`
- Root `TASKS.md` (current tracker; not modified)
- `.hiveai/PROJECT.json`, `.hiveai/RULES.md`, `.hiveai/TASKS.md`, and `.hiveai/EVENTS.jsonl` are not present in this current GitHub checkout; no legacy hidden tracker was used as authority.
- `tasks.md` and `.hiveai/CYCLE_INDEX.md` were read as historical/project records and were not modified.
- Accepted SP03 normalization source/tests and accepted SP04 qualification source/tests were read before implementation.

## Scope

Implement only safe generic PNG ancillary-chunk compatibility for SP04-C005. Preserve immutable raw bytes and hashes, bounded decoding, critical-chunk fail-closed behavior, normalization policy, provider policy, and all M00–SP04 accepted contracts. The owner-supplied private PNG is not committed.

## Implementation and verification record

- Implementation edit: `src/scrubbots_pixel_factory/semantic/normalization/core.py` now validates four-letter ASCII PNG chunk type codes, rejects an invalid reserved bit, validates every chunk CRC before any classification, ignores structurally valid ancillary chunks generically, and rejects unsupported critical chunks. Existing IHDR/IDAT/IEND structure, IEND emptiness, decompression, raster, filter, color-type, and media bounds remain unchanged.
- Test edit: added `tests/unit/test_sp04_c005_ancillary_png.py` with deterministic synthetic `IHDR -> caBX -> fdEC -> IDAT -> IEND` fixtures and negative tests for unknown critical chunks, corrupt ancillary CRC, malformed type, and truncation. Tests also prove exact decoded RGBA equality, distinct raw SHA/artifact provenance, local-file import, and identical normalized RGBA/hash.
- Owner private/live PNG was not added. No provider policy, `AREA_AVERAGE_V1`, palette policy, or dimension-reconciliation behavior was changed.
- `python -m pytest -q tests/unit/test_sp04_c005_ancillary_png.py tests/unit/test_sp03_normalization.py` — **22 passed**, 1 pre-existing Windows pytest-cache permission warning.
- `python -m pytest -q tests/unit/test_sp04_qualification.py` — **26 passed**, 1 pre-existing Windows pytest-cache permission warning.
- `python -m pytest -q tests/unit/test_sp01_semantic_contracts.py tests/unit/test_sp02_provider_bridges.py tests/unit/test_sp03_normalization.py tests/unit/test_sp04_qualification.py tests/unit/test_sp04_c005_ancillary_png.py` — **112 passed**, 1 pre-existing Windows pytest-cache permission warning.
- `python -m pytest -q` — **493 passed**, 1 pre-existing Windows pytest-cache permission warning, completed in 297.12 seconds.
- `python -m compileall -q src tests` — passed.
- `python -c "import scrubbots_pixel_factory as package; print(package.__name__)"` — passed; printed `scrubbots_pixel_factory`.
- `python -m scrubbots_pixel_factory.cli --help` — passed; offline `generate`, `reproduce`, `batch`, and `semantic-normalize` commands listed.
- installed `scrubbots-pixel --help` — passed with the same offline command surface.
- `git diff --check` — passed.
- Scoped offline/network/credential scan over changed source/test files — passed; no runtime network import/call, provider call, credential, or telemetry reference found.
- No Magnific or PixelLab call was made and no provider credits were spent.
- No changes were made to root `TASKS.md`, accepted generator algorithms outside the scoped decoder, provider/palette policy, legacy tracker files, or the separate main ScrubBots repository.

### Changes and rationale

The parser remains fail-closed at the PNG chunk boundary: malformed type codes and invalid reserved-bit semantics are rejected; every chunk's CRC is checked; known critical chunks continue through the existing decoder; valid ancillary chunks are retained in the parsed sequence but never interpreted as pixel data; and unknown critical chunks are rejected. This accepts generic valid private chunks such as the live-shaped `caBX` and `fdEC` while preserving immutable source bytes and all existing bounded decode protections.

Files changed in this cycle:

- `src/scrubbots_pixel_factory/semantic/normalization/core.py`
- `tests/unit/test_sp04_c005_ancillary_png.py`
- `.hiveai/codex-logs/PAG-SP04-C005_SAFE_ANCILLARY_PNG_COMPATIBILITY_FOR_LIVE_MAGNIFIC_RAW_IMPORT_CODEX_LOG.md`

## Publication checkpoint

- Implementation commit: `03825da` (`Implement SP04-C005 ancillary PNG compatibility`).
- Implementation commit push: succeeded with `git push origin main` (`9fcaaf2..03825da main -> main`).
- The completed log is being published in a separate evidence-only commit so its publication checkpoint can contain the real implementation SHA and final repository equality; no source or policy changes are included in that publication commit.
- Final fetch/equality checkpoint for the completed-log publication: immediately after `git push origin main` and `git fetch origin`, `git rev-parse HEAD` and `git rev-parse origin/main` both returned `85832a57c035eeae083b2b7e3e274e6564f5f2dc`, and `git rev-list --left-right --count HEAD...origin/main` returned `0 0`.
- The only subsequent publication operation is this evidence-only log checkpoint commit; the final handoff independently records the terminal commit and repeats the equality check. No product, test, provider, palette, or tracker files are changed after the implementation commit.
