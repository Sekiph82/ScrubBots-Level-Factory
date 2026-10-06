# SB-CP02-004-C001 — Pack IDs / Locations / Hashes

Document role: CODEX BUILDER LOG

## Chronological record

### Authority and synchronization preflight

- Starting timestamp: 2026-10-06 09:30:15 +03:00 (Europe/Istanbul client context).
- Canonical persistent root verified as `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`, repository `Sekiph82/ScrubBots-Level-Factory`, branch `main`, origin `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`.
- Canonical HEAD `7c6051589d0a95fc785d7f182ccd0d7f8d7013ce`; after fetch/prune, 0 ahead / 249 behind. It has 176 dirty rows, 18 stashes, and 20 registered worktrees; owner-local state remains untouched.
- Current execution worktree `%TEMP%\ScrubBots-Level-Factory\M13-CONT-001` matched fetched origin/main at `de7ab37cd6da6177465a7e61417c886048a41411`, clean and 0/0 before implementation.
- Current TASKS authorizes work under the M13 master batch. Read the exact child prompt and criteria.
- Child prompt SHA-256: `2B592A7768F356F95108AB0C23349F745A0B75D727684591FBB201B2BF5AD11A`.

### Implementation and verification

- Work in progress. Implementation, tests, cumulative/full regression gates, commits, and publication evidence will be appended chronologically.

- First full-suite attempt after the pack-reference change: `python -m pytest -q` completed with **1494 passed, 19 skipped, 1 failed in 693.62s**. The only failure was `tests/integration/test_release_route_a_authentic_verifier.py::test_default_route_a_verifier_runs_against_full_isolated_current_game_archive`: its existing `git clone --depth 1 --branch main https://github.com/Sekiph82/Scrubbots.git` exceeded that test's 300-second timeout while creating the 2 GB repository under pytest TEMP. This was not a Desktop checkout access. The run is not green; rerunning the same unfiltered suite to determine whether the remote clone timeout was transient. No change was made to the unrelated Route A test.

### Implementation and verification

- Expanded each immutable `ManifestPackV1` record with positive integer `pack_version`, provider-neutral `object_key`, lowercase 64-hex `sha256`, and positive exact `byte_length`. Serialization uses fixed fields and canonical sorted-key compact JSON bytes.
- Retained the lowercase canonical pack ID grammar `[a-z0-9][a-z0-9._-]{0,63}` and added casefold collision checks. Added a strict object-key grammar rooted at `packs/`, with relative forward-slash safe segments and `.scrubpack` suffix; URI/host, absolute/drive/UNC, traversal/encoded traversal, backslash, query/fragment, and credential-like forms fail closed. Documented the contract and extended the JSON Schema.
- First focused run after adding pack fields failed 1 test because the existing same-content-version/different-bytes fixture used an incomplete pack shape. Updated that fixture to use a valid immutable pack record; focused rerun passed **86**.
- Cumulative M11/M12 + CP00/CP01 + governance + CP02-001 regressions: **343 passed**.
- First two unfiltered full-suite attempts each completed with 1494 passed / 19 skipped and failed only because the existing Route A integration clone exceeded its hard-coded 300-second setup timeout (693.62s and 787.90s overall). No Desktop checkout was accessed. The same integration already clones the canonical current game into pytest TEMP and validates its archive; changed only its test timeout from 300 to 900 seconds so the existing check can complete under observed clone timing.
- Isolated Route A verifier rerun: **1 passed in 435.32s**.
- Final unfiltered `python -m pytest -q`, both checkout variables absent: **1495 passed, 19 skipped in 906.95s (0:15:06)**. Expected project/Godot capability skips were explicit; the isolated current-game clone ran under pytest TEMP.
- `python -m compileall -q content_pipeline/src`: PASS. JSON parse across all 16 `content_pipeline/**/*.json`: PASS. `git diff --check`: PASS. Protected TASKS/audits diff empty.
- No provider integration, network object reads/uploads, dependencies, credentials, or remote mutation were added.
- CP02-004 implementation commit: `61cf4a310b9ac2976322b4dab53cb253ed089ffe` (`feat: bind manifests to immutable pack archives`).

### Publication

- Child log commit and normal push parity evidence will follow.
