# SB-LF04-004-C001 — Canonical Dependency Depth

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-23 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `54f3a56b7759ffad21c8b9c1307df0506b1c26ff`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing repository instructions, M03 closure, LF04-001 through LF04-003 contracts/evidence, the M04 index/master prompt, LF04-004 prompt, and LF04-004 audit criteria.

Implementation decisions and rationale: added a versioned `DependencyDepthResult` requiring an explicit provider binding to canonical authority, level source, state, and solver evidence. No M03 path depth, art, color, dimension, or heuristic inference is used. The production helper remains UNAVAILABLE when canonical dependency semantics are not executable; fixture results can validate the contract but do not provide production authority.

Commands and test evidence: Initial focused run failed 5 tests because the new provider result referenced `AnalysisDisposition` without importing it; imported the enum and reran successfully. Corrected focused LF04-004 plus LF04-002/003 tests passed 18 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Full `python -m pytest -q -p no:cacheprovider` passed 886 tests with 1 pre-existing canonical-bridge capability skip in 288.14 seconds; no failures or xfails were introduced.

Files changed: `src/scrubbots_pixel_factory/difficulty_analysis.py`, package exports, this builder log, and `tests/unit/test_sb_lf04_004_dependency_depth.py`.

Final diff, status, commits, push, and `origin/main` equality: pending publication.
