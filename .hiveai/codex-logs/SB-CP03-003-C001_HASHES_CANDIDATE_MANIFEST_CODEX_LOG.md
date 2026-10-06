# SB-CP03-003-C001 — Hashes + Candidate Manifest

Document role: CODEX BUILDER LOG

## Start and inherited M14 synchronization

- Starting timestamp: `2026-10-06T18:29:25+03:00`.
- Canonical repository is `Sekiph82/ScrubBots-Level-Factory` at `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Reusing authorized TEMP worktree `C:\Users\sekip\AppData\Local\Temp\ScrubBots-Level-Factory\M14-CP03-001-012-CPX002-MASTER`.
- CP03-002 final published HEAD/origin/main: `2ac994e0a5ef7a2096fbf2d6e3f311e26fb62003`; fetch confirmed 0/0 and clean before this child.
- Live root `TASKS.md` retains `M14_MASTER_BATCH_AUTHORIZED` and the exact ordered master prompt. A separately queued Factory Studio maintenance task is marked `QUEUED_AFTER_M14 / DO_NOT_RUN_CONCURRENTLY`; it does not change current M14 authority.

## Child authority and contracts read

- `.hiveai/prompts/SB-CP03-003-C001_HASHES_CANDIDATE_MANIFEST_PROMPT.md` and `.hiveai/audit-criteria/SB-CP03-003-C001_HASHES_CANDIDATE_MANIFEST_AUDIT_CRITERIA.md` from current execution HEAD.
- Exact child scope: deterministic local manifest from CP03-002 pack evidence; explicit positive content version and canonical minimum game version; exact pack IDs/versions/object keys/SHA-256/byte lengths; exact level-to-pack ownership; M13 optional disabled/schedule metadata contracts; strict serialize/parse; CP02-009 reference validation against exact M12 evidence; app/content compatibility against explicit capability/version; monotonic successor check when prior accepted authority is supplied; local immutable bytes/hash only, with no provider/network mutation.
- Implementation decisions, commands, failures/corrections, files, focused/cumulative tests, commits, push result, and parity will be appended chronologically before advancing to CP03-004.

## Implementation and verification

- Implemented pure local `candidate_manifest.py` with a frozen result carrying the exact manifest bytes, SHA-256, original immutable M12 pack build evidence, strict parse/serialize round-trip result, CP02-009 reference validation, explicit app/content compatibility result, optional monotonic-successor result, and a fail-closed `publishable` property.
- Pack identity/version and exact archive SHA-256/byte length derive from each supplied `ScrubpackBuildResult`; provider-neutral object keys must be explicit and exactly cover the pack set. Level-to-pack ownership derives from exact M12 evidence membership. Content version, canonical minimum game version, app current version, supported schema capability, and optional disabled/schedule data are explicit caller inputs. The API does not read a filesystem, clock, network, or provider.
- Exported the API from `scrubbots_content_pipeline`; added `tests/unit/test_sb_cp03_003_candidate_manifest.py` for deterministic bytes/hash, exact archive binding, ownership, M13 disabled/schedule contract references, bad pack evidence, compatibility failure, monotonic successor, and explicit object-key membership.
- Focused command `python -m pytest -q tests/unit/test_sb_cp03_003_candidate_manifest.py tests/unit/test_sb_cp02_009_manifest_references.py tests/unit/test_sb_cp02_011_compatibility.py tests/unit/test_sb_cp02_012_manifest_parser_corpus.py`: **48 passed in 0.92s**.
- Prior M14 and M11-M13 regression command `python -m pytest -q tests/unit tests/integration/test_sb_cpx_001_solver_identity_pack.py tests/integration/test_sb_cp03_002_factory_candidate_pack.py`: **1,390 passed, 4 skipped in 283.36s**. The four skips explicitly state canonical ScrubBots/Godot capability was not supplied.
- Required unfiltered `python -m pytest -q`: **1,587 passed, 19 skipped in 1,077.19s**. The 19 skips are existing explicit missing canonical ScrubBots/Godot authority cases; no owner Desktop game checkout was used.
- `python -m compileall -q content_pipeline/src src tests` passed; all 16 Content Pipeline JSON files parsed; `git diff --check` exited 0 (Git emitted only its LF-to-CRLF working-copy notice for the modified package export).
- Files changed: `content_pipeline/src/scrubbots_content_pipeline/candidate_manifest.py`, `content_pipeline/src/scrubbots_content_pipeline/__init__.py`, and `tests/unit/test_sb_cp03_003_candidate_manifest.py`. No dependency/license, provider/network, game-repository, tracker, audit, or prompt changes. No test failed during this child.
- Product implementation commit `6b05737ce4e395b88c4fb59f2d945f39500e71ee` was pushed normally to `main`; post-push fetch confirmed `HEAD == origin/main` at that SHA, 0/0.
- Separate child/master evidence-log commit SHA, normal push evidence and post-push parity will be appended before starting CP03-004.
