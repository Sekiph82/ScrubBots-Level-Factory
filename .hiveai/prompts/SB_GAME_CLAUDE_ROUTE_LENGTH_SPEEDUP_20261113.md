# ScrubBots game — make the route-length measurement faster, with identical output

Written 2026-11-13 by the Factory Claude for the Claude working in
`C:\Users\sekip\Desktop\Scrubbots` (`Sekiph82/Scrubbots`). The owner explicitly asks for this game
change. Follow the game repo's own CLAUDE.md, TASKS.md and test rules for everything not stated
here. It continues your job 156 (`6534537c`, "verdict-only target access for ProofKernel + Difficulty
V1 analyzer").

## Why

The Factory now solves PixelLab PNGs with your `6534537c` runtime. The first real batch on the
owner's laptop (6 PNGs at once, 21 PNGs measured 2026-11-13 12:43–13:03) went from a median of
17.6 to 4.3 minutes per level, about 63 levels per hour. Thank you.

At the end of job 156 you wrote that most of the remaining time now comes from the route-length
measurement, which computes a full route for every robot. In the Factory, the per-level game-side time
is now:

| Game call | Median | Range | What runs |
|---|---|---|---|
| Official Difficulty V1 on the winning plan (`analyze_trace`) | 51 s | 28–70 s | `LevelDifficultyAnalyzerV1.measure()` / `score()` |
| Real-play pre-check per plan (`real_play_v1`, `canonical_60hz`) | ~22 s | 6–68 s | real-play driver on the production host |
| Kernel replay of a plan (`verify_trace`) | ~8–13 s incl. Godot start | | `ProofKernel.apply_placement()` per step |

A level with several candidate plans runs the replay and the real-play pre-check once per plan
(up to 8 plans in this batch). Faster route measurement helps the analysis and every replay.

## Goal

Make the route-length measurement faster: the full per-robot route computation used by the
Difficulty V1 analyzer and, if it is the same code, by `ProofKernel`. Typical candidates, decided by your
own profiling:

- Compute only the route length the measurement needs, not the full route objects.
- Reuse routes between steps when the board around them did not change; recompute incrementally.
- Precompute per-board routing data (neighbours, access, entry points) once per level.
- One BFS/flood per source instead of one per robot where the result is shared.
- Packed arrays, no Dictionary/Array allocation in hot loops.

Target: `measure()` on the two levels below at least 2x faster than on `6534537c`, and a faster
`apply_placement()` if the same code is involved. Report old and new seconds per part.

## Hard requirement: identical results

The output must stay byte-identical, exactly as in job 156:

- every field `measure()` and `score()` return;
- every `ProofKernel` result (`clears`, `active_after`, `placed`), trace hash and solver status;
- real-play outcomes.

More than 250 Factory levels and all campaign levels already carry Difficulty V1 scores.

- Reuse and extend your job-156 identical-output regression: the 30 campaign levels, the difficulty
  anchor fixtures, and at least the two Factory levels below.
- Watch it fail when you deliberately change one value.
- If an exact match is impossible somewhere, drop that speed-up and tell the owner; never change a
  score silently.

## Real Factory inputs (read-only owner data; copy them, never write here)

Folder: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\data\Release Pool\Pending\Pipelines\Work\`

1. LF-000147: `candidate-owner-3e3054a9b3ad260fc2df5807b2dabe54dad7340b1a2176fd\9a32f00dda745d2086f3\`
   - challengeScore 52.1888, HARD.
2. LF-000148: `candidate-owner-746d44ed04341a8b20bd5fe042b917368c392ecb687b4c16\31c77e600be5bb42d56b\`
   - challengeScore 43.8423, MEDIUM.

Both use the same file pattern as in job 156: the level `.json`, the plan `_supply_v1.json` and the
saved Factory result `_supply_result.json` (`solver_metrics.official_difficulty_v1`, `solution_trace`).

On `6534537c` the Factory re-verified both: a full solve plus official analysis took 35 s and 37 s.
The Difficulty V1 JSON was byte-identical to the saved results.

## Must not change

- Game rules, ProofKernel semantics, Difficulty V1 formulas, constants and anchors.
- Released or campaign level data.
- The real-play "refill slots at once" rule and the slot pop hold (`628ab240`).

## Done when

- `measure()` on the two levels is at least 2x faster than on `6534537c`. Report:
  - old and new seconds per part, with the route-length part separate;
  - the `apply_placement()` mean.
- The identical-output regression passes on campaign levels, anchors and these Factory levels.
- The full headless suite passes. Report the exact counts, including any failures.
- One code commit is pushed to the game's main branch and CI is green. Tell the owner the commit hash;
  the Factory Claude then re-pins its runtime to it and re-measures.
