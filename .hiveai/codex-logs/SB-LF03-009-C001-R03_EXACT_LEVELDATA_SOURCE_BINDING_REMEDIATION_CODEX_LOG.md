# SB-LF03-009-C001-R03 — Exact LevelData Source Binding Remediation

Document role: CODEX BUILDER LOG

## Chronology

- Start: 2026-09-23 Europe/Istanbul.
- Repository and branch: `Sekiph82/ScrubBots-Level-Factory`, `main`.
- Starting HEAD after safe fast-forward: `804c6e8`; `origin/main` matched; initial status contained only preserved untracked `level_factory/**/*.uid` files.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, the R03 master prompt, R03 index, R02 re-audit, and exact task prompt were read before implementation. `TASKS.md` is untouched.
- The owner ScrubBots checkout remains read-only; real bridge tests use an independent temporary clean checkout at the exact canonical SHA.

## Work log

Implementation and verification entries will be appended chronologically.

- Read canonical `docs/03_LEVEL_DATA_SPEC.md`, the existing bridge/runner, and the R02 real-invoke tests. The prior request carried only a caller-claimed hash alongside a separate level dictionary.
- Added a bounded exact UTF-8 JSON source-byte contract for Level Data V1: exact fields `version,id,name,difficulty,width,height,palette,cells`, duplicate-key rejection, structural validation, and SHA-256 computed over the original bytes. The request now carries those bytes as base64 and rejects stale/tampered/malformed/unsupported sources before Godot execution.
- Updated the external runner to independently decode and hash the same bytes with Godot `HashingContext`, parse the same canonical fields, and construct `LevelData` from `name` and those parsed values. Removed the divergent `level` dictionary path.
- Added tamper coverage for cells, width, palette, name, malformed JSON, and unsupported version, plus valid changed-source binding. Real legal-move execution remains covered from a temporary exact-SHA clean checkout.
- Focused command: `python -m pytest -q tests/unit/test_sb_lf03_009_canonical_bridge.py tests/unit/test_sb_lf03_005_visited_memoization.py` -> `13 passed, 1 warning`.
- A first real Godot attempt returned the generic malformed-source error because Godot JSON numbers are parsed as floats; the runner was corrected to accept only integer-valued JSON numbers, debug prints were removed, and the focused suite then passed.
- Implementation commit: `f954171`; pushed successfully to `origin/main`. `TASKS.md` remained unchanged and preserved `.uid` files were not staged.
- Task terminal finalization: focused 009 plus retained 005 tests passed; exact source-byte hash, stale-hash tamper rejection, valid updated source, malformed UTF-8/JSON, unsupported version, runner identity, real Godot invocation, and checkout immutability were exercised. This append is the required terminal log-only publication.
