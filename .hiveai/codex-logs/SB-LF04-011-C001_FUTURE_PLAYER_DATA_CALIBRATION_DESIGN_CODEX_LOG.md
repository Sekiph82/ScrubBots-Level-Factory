# SB-LF04-011-C001 — Future Player-Data Calibration Design

Document role: CODEX BUILDER LOG

Starting timestamp: 2026-09-24 Europe/Istanbul.

Canonical root verification: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` maps to `Sekiph82/ScrubBots-Level-Factory` on `origin`.

Branch and starting HEAD: `main`, `367084bcfa4992e5dba6c1055b83b68f820728e3`.

Origin and divergence: `HEAD` was equal to `origin/main` before edits.

Initial Git status: tracked files clean; pre-existing untracked nested worktree artifacts and Godot `.uid` files preserved and excluded.

Authorized scope read: root `TASKS.md`, governing instructions, M03 closure, LF04-001 through LF04-010 contracts/evidence, the M04 index/continuation prompt, LF04-011 prompt, and LF04-011 audit criteria.

Implementation decisions and rationale: added a closed offline aggregate `CalibrationDataset` and immutable disabled `CalibrationPlan` with state `DISABLED_UNTIL_POLICY_APPROVED`. Identity/PII/raw-event fields are rejected, minimum samples are required, runtime collection/network flags are fixed false, and future policy changes must be explicit rather than mutating Difficulty V1. Added the required privacy/product/security/retention/consent design document.

Commands and test evidence: focused LF04-011 plus LF04-010/009 tests passed 26 tests. `python -m compileall -q src tests`, Godot 4.7.2 headless editor boot, `git diff --check`, and `git diff --exit-code -- TASKS.md` passed. Full `python -m pytest -q -p no:cacheprovider` passed 934 tests with 1 pre-existing canonical-bridge capability skip in 319.39 seconds; no failures or xfails were introduced.

Files changed: `src/scrubbots_pixel_factory/difficulty_analysis.py`, package exports, calibration design documentation, this builder log, and `tests/unit/test_sb_lf04_011_calibration.py`.

Final diff, status, commits, push, and `origin/main` equality: pending publication.
