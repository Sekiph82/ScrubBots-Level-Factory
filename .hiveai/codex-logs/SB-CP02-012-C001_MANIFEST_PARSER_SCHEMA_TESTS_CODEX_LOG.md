# SB-CP02-012-C001 — Manifest Parser / Schema Tests

Document role: CODEX BUILDER LOG

## Session start
- 2026-10-06T09:40:16Z (UTC); M13-CONT-001 master continuation.
- Canonical repository `Sekiph82/ScrubBots-Level-Factory`; origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; canonical Desktop checkout remains preserved. Execution worktree `%TEMP%\ScrubBots-Level-Factory\M13-CONT-001`.
- Fetched start HEAD and `origin/main`: `4d374e7d90da115548e5b180db908e02de5d9498`; clean status, 0/0 divergence.
- Live root `TASKS.md` read; M13 master plus M13-CONT-001 authorize this final ordered child.
- Prompt `.hiveai/prompts/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_PROMPT.md`; SHA-256 `1324D2CF7D568594CA0900852DF92211C0F423A6CEFA9F3CDCF969898CE049DC`.
- Criteria `.hiveai/audit-criteria/SB-CP02-012-C001_MANIFEST_PARSER_SCHEMA_TESTS_AUDIT_CRITERIA.md`; SHA-256 `A9B53E39C705B7873313FD390AE14DFB43BB2D82656A71F1A6B13AA729EDC210`.

## Scope
- Add an external strict bytes-to-immutable-model manifest parser; enforce UTF-8, duplicate/nonfinite rejection, bounded size/depth/collections/strings, exact schema and all closed nested model contracts.
- Add positive and adversarial corpus across CP02-001..011, including versioning, compatibility, history, references, ownership, locations/secrets and time windows.
- Preserve M11/M12 authority. No tracker/audit changes. Separate implementation/log commits; after this child run final M13 master verification and stop for ChatGPT independent audit.

## Contracts read
- CP02-012 prompt and audit criteria; live root `TASKS.md`; existing `ContentManifestV1.from_dict` closed model.
- CP02-001..011 APIs and child tests, including exact-byte history, compatibility, and reference validation.

## Implementation and verification
- In progress; no CP02-012 edits or tests yet.

## Implementation and verification
- Added `parse_content_manifest_v1(raw: bytes)` as the strict external boundary. It enforces bytes-only input, strict UTF-8, duplicate-key rejection, non-finite number rejection, 1 MiB maximum input, 32-level container nesting, 4,096 items per collection, 16,384 Unicode code points per string, exact root fields, V1 schema identity/version, all closed nested model fields, and immutable model construction after checks.
- Added deterministic parse reason codes and canonical serialize/parse/serialize tests. Existing `ContentManifestV1.from_dict` remains the internal closed model constructor; no M11 helper behavior was rewritten.
- Added corpus cases for noncontiguous level IDs, content-version gaps, too-old game compatibility, duplicate keys at root/nested levels, ownership collisions, unknown pack/disabled-level/schedule references handed to CP009 validation, invalid UTC windows, tampered M10 history, URL/secret-like locations, future schema/version, UTF-8/JSON/non-finite failures, and resource limits.
- Documented exact byte boundary and limits in `REMOTE_CONTENT_MANIFEST_V1.md`.
- Focused CP02-012 parser corpus: **16 passed in 0.14s**.
- Cumulative CP02-001..012 + CP01/M12 + CP00/M11 + governance focused set: **404 passed in 14.83s**.
- Unfiltered `python -m pytest -q`: **1,562 passed, 19 skipped in 748.58s**. Skips are existing explicit unavailable ScrubBots/Godot authority cases.
- `python -m compileall -q content_pipeline/src tests/unit/test_sb_cp02_012_manifest_corpus.py`: PASS.
- All **16** Content Pipeline JSON files parsed: PASS.
- `git diff --check` and staged diff check: PASS; only configured LF-to-CRLF warnings.
- No TASKS/audit edits, dependency/license changes, credentials, network/provider behavior, or game/runtime changes.
- Implementation commit: `743372bc15c368cb98a6097778859905ea50e34f` (`Add strict manifest bytes parser and corpus`).
- Files changed: strict parser module, package exports, CP02 corpus tests, and Content Platform manifest documentation.

## Publication
- Child log commit and normal push/fetch parity will be recorded after publication.
- Normal non-force push `git push origin HEAD:main` succeeded; remote advanced from `4d374e7d90da115548e5b180db908e02de5d9498` to `f6db349637308b77180089c5bb671dfc58ff4b8c`.
- Post-push `git fetch --prune origin` verified local HEAD == `origin/main` == `f6db349637308b77180089c5bb671dfc58ff4b8c`, 0/0 divergence, and clean status. Initial child log commit: `f6db349637308b77180089c5bb671dfc58ff4b8c`.

## Log errata
- The compileall command path above contains a filename typo (`test_sb_cp02_012_manifest_corpus.py`). The actual child command was `python -m compileall -q content_pipeline/src tests/unit/test_sb_cp02_012_manifest_parser_corpus.py`, which passed; final master verification also passed `python -m compileall -q content_pipeline/src tests`.
- The corpus description phrase `M10 history` should read `M13 CP02-010 manifest history`; the test verifies tampered CP02-010 manifest-history evidence.
