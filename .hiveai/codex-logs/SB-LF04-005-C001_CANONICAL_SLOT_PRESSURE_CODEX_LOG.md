# SB-LF04-005-C001 — Canonical Slot Pressure

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-23 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `b66af0867bbc91c16e7eca90f3bce2d64ec2dfee`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing instructions, M03 closure, LF04-001 through LF04-004 contracts/evidence, the M04 index/master prompt, LF04-005 prompt, and LF04-005 audit criteria.

Implementation decisions and rationale: added immutable canonical `SlotSnapshot` values and a versioned `SlotPressureResult`. Slot pressure is the maximum occupied-slots/capacity ratio over an authority-bound trace, bounded to [0,1]. No art or color inference is used; absent trace evidence remains UNAVAILABLE.

Commands and test evidence: Initial focused run had one fixture assertion error (expected 0.25 instead of the correct maximum 0.375); corrected the expectation. Focused LF04-005 plus LF04-004/003 tests then passed 18 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Full `python -m pytest -q -p no:cacheprovider` passed 894 tests with 1 pre-existing canonical-bridge capability skip in 189.94 seconds; no failures or xfails were introduced.

Files changed: `src/scrubbots_pixel_factory/difficulty_analysis.py`, package exports, this builder log, and `tests/unit/test_sb_lf04_005_slot_pressure.py`.

Final diff, status, commits, push, and `origin/main` equality: pending publication.
