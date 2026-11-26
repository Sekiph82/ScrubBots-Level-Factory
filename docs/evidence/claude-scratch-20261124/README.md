# Claude scratch archive (2026-11-12 .. 2026-11-25)

Files that lived in Claude Code's session temp scratchpad, archived on owner request before
that folder was deleted. Nothing here is imported by Studio.

- `apply_*.py`, `wire_*.py`, `fix_*.py`, `backfill_real_play.py`: one-off patchers; their
  changes are already committed (see the builder log).
- `exp_*.jsonl`, `seed_noise.jsonl`, `pxl_*`, `vh_trial*_sheet.png`, `solve_vh_trial*.py`,
  `supply_difficulty_experiment.py`, `score_png.py`: VERY_HARD / supply / seed-noise
  difficulty experiments (2026-11-23..24).
- `pxl-trial/`: claude-pxl drawing trials (images and their scores).
- `*.log`: local game CI runs for the 1000-level release.

Reusable tools were copied to `scripts/claude/`: `deploy_release.py` (bounded Studio
deploy), `score_png.py`, `run_easy_until.py`, `dry_run_game_release.py`, `real_play_shards.py`.
Not archived: the game clones used for test runs (copies of the game repo) and `claude-pxl`
(a third-party GitHub repository, https://github.com/crsolver/claude-pxl).
