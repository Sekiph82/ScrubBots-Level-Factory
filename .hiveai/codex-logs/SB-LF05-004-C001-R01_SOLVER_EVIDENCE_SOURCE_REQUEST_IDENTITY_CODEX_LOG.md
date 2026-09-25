# SB-LF05-004-C001-R01 — Solver Source/Request Identity Remediation
Document role: CODEX BUILDER LOG

## Chronology

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Canonical repository/root, `main`, origin, and starting HEAD `f03989978ecbb1e23593a54a3e8082ac04e6819c` were verified.
- R01 prompt/audit and M03 solver contracts were read before edits; owner untracked files were preserved.

## Scope and evidence

Bind solver QA to exact level/source/state/request, authority/provider/version, evidence digest, and deterministic budget identity. No second solver or synthetic relabeling. `TASKS.md` and `.hiveai/audits/**` remain protected; builder evidence is not acceptance.

## Commands/results

Focused/regression tests, compileall, Godot headless, diff-check, protected-tracker check, commits, push, and final SHA verification will be appended chronologically.

- Added provenance-bearing M03 solver envelope support for exact level/source/request, authority, provider/version, evidence digest, state digest, and deterministic budget digest.
- Solver gate now rejects cross-level, cross-request, authority, provider, state, budget, and receipt-digest replay as `ERROR`; only matching authoritative `PROVEN_UNSOLVABLE` rejects, while timeout/inconclusive/unavailable remain distinct.
- Added replay and digest-adversarial tests. Focused M05/R01 suite: `34 passed`; full corrected regression: `985 passed, 2 skipped`.
- `python -m compileall -q src tests`: PASS; Godot headless editor quit: PASS; `git diff --check`: PASS; `git diff --exit-code -- TASKS.md`: PASS. No second solver or provider credits/network calls were used.

## Publication closure

- Implementation commit: `159a7c08d7963650fdecce1ce3e5a8f0318abf8a`.
- Terminal log-only commit: pending in this append.
- Builder handoff remains `AWAITING_AUDIT`; no PASS/CLOSED claim is made.
