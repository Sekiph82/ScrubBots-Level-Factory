# SB-LF04-010-C001 — Metric Provenance / Versioning

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-24 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `42c19a8dc0ae9a6fe525d424fcbcd03c2614c663`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked nested worktree artifacts and Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing instructions, M03 closure, LF04-001 through LF04-009 contracts/evidence, the M04 index/continuation prompt, LF04-010 prompt, and LF04-010 audit criteria.

Implementation decisions and rationale: added a closed immutable `DifficultyAnalysis` envelope and provider identities. It binds LevelData SHA, canonical authority, solver evidence, LevelMetrics schema/version/digest, metric providers, Challenge Score, lane mapping, component availability, and disposition. Cross-lineage score/lane results are rejected; operational telemetry is excluded.

Commands and test evidence: focused LF04-010 plus LF04-009/008 tests passed 20 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Full `python -m pytest -q -p no:cacheprovider` passed 924 tests with 1 pre-existing canonical-bridge capability skip in 342.45 seconds; no failures or xfails were introduced.

Files changed: `src/scrubbots_pixel_factory/difficulty_analysis.py`, package exports, this builder log, and `tests/unit/test_sb_lf04_010_provenance.py`.

Implementation commit: `cca1d5a3cadf065793d0408958da301b4225fe29`, pushed successfully. Final tracked status was clean; pre-existing untracked nested worktree artifacts and Godot `.uid` files remained preserved and unstaged. `TASKS.md` had zero diff. Terminal log-only commit: pending.
