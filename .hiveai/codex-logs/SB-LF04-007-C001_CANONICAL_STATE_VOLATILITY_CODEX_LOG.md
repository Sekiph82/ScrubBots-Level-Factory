# SB-LF04-007-C001 — Canonical State Volatility

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-23 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `6d6561da7a16d188bfd618c2f5a915c6b7c96451`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing instructions, M03 closure, LF04-001 through LF04-006 contracts/evidence, the M04 index/master prompt, LF04-007 prompt, and LF04-007 audit criteria.

Implementation decisions and rationale: added immutable `VolatilitySnapshot` values and a versioned `VolatilityResult`. Volatility is the mean transition delta of the normalized remaining-active-cell, remaining-supply, and occupied-slot signature over an ordered canonical trace. No art fragmentation or timing data is used; unavailable trace data remains UNAVAILABLE.

Commands and test evidence: focused LF04-007 plus LF04-006/005 tests passed 18 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Full `python -m pytest -q -p no:cacheprovider` passed 904 tests with 1 pre-existing canonical-bridge capability skip in 607.81 seconds; no failures or xfails were introduced.

Files changed: `src/scrubbots_pixel_factory/difficulty_analysis.py`, package exports, this builder log, and `tests/unit/test_sb_lf04_007_volatility.py`.

Final diff, status, commits, push, and `origin/main` equality: pending publication.
