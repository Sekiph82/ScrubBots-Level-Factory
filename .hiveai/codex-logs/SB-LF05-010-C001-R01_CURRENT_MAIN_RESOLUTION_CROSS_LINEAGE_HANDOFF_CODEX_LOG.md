# SB-LF05-010-C001-R01 — Current-Main/Cross-Lineage Handoff Remediation
Document role: CODEX BUILDER LOG

## Chronology

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Canonical repository/root, `main`, origin, and starting HEAD `f03989978ecbb1e23593a54a3e8082ac04e6819c` were verified.
- R01 prompt/audit and predecessor handoff contracts were read before edits; owner untracked files were preserved.

## Scope and evidence

Resolve current `Sekiph82/Scrubbots@main`, bind all cross-lineage identities, require exact validator/M09 clean-checkout evidence, derive M30 only from eligibility, and keep M47/M48 pending. `TASKS.md` and `.hiveai/audits/**` remain protected.

## Commands/results

Focused/regression tests, compileall, Godot headless, diff-check, protected-tracker check, commits, push, and final SHA verification will be appended chronologically.

- Added read-only `CurrentMainResolution` boundary; eligible handoff requires canonical `https://github.com/Sekiph82/Scrubbots@main`, a pinned non-UNAVAILABLE SHA, clean checkout, exact LevelValidator and ProductionLevelValidator proofs, applicable M09 proof, and non-mutation proof.
- Handoff now cross-binds QA source/LevelData/logical-art plus solver/difficulty/semantic digests, derives M30 compatibility only from eligibility, and keeps M47 Android/M48 iOS PENDING.
- Validator/M09 rejection, stale/wrong authority, mixed hashes, absent resolver/provider, and missing proof tests are covered. Focused M05/R01 suite: `34 passed`; full corrected regression: `985 passed, 2 skipped`.
- No canonical `Sekiph82/Scrubbots` checkout was supplied to this builder session; exact native validator/M09 execution is therefore represented as `UNAVAILABLE`, never fabricated. Mocked tests use no provider credits/network calls and do not mutate a main-game checkout/catalog.
- `python -m compileall -q src tests`: PASS; Godot headless editor quit: PASS; `git diff --check`: PASS; `git diff --exit-code -- TASKS.md`: PASS.
