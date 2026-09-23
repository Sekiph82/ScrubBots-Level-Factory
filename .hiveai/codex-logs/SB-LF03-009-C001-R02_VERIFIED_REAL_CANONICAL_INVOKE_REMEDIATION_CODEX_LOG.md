# SB-LF03-009-C001-R02 — Verified Real Canonical Invoke Remediation

Document role: CODEX BUILDER LOG

## Chronology

- Start: 2026-09-23 Europe/Istanbul.
- Repository: `Sekiph82/ScrubBots-Level-Factory`, branch `main`.
- Starting HEAD: `85f4b18cdea856948659ee31f9bad3aacea01ef6`; safe synchronization completed; `TASKS.md` untouched.
- Canonical primary checkout is read-only and will not be cleaned, reset, stashed, or modified. Pre-existing Level Factory `.uid` files remain unstaged.

## Work log

R02 implementation and verification entries will be appended chronologically.

- Read the canonical bridge contract, runner, ScrubBots authority verification, and LF03-009 regression test. The owner checkout is dirty, so a temporary local Git clone is the only permitted execution checkout.
- Hardened capability/invoke gating to the committed Level Factory runner path and SHA, verified Godot availability, and enforced that the runner remains outside the canonical checkout.
- Added runner-side LevelData source-identity matching against the verified request envelope. The runner remains a transport adapter and delegates `legal_moves`, `apply_placement`, and `solve` to canonical preloaded scripts.
- Updated the integration test to clone the owner repository into a temporary clean checkout at `1144704e6c3647ed1cf76c610be5bd675585734a` with `core.autocrlf=false`, verify clean status/source bytes, and execute a real Godot `legal_moves` request. Result: `5 passed`.
