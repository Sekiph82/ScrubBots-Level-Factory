# SB-LFX-018-C001-R02-R05-R09-R02-R04-R07 | Independent strict owner UI acceptance

Scope/authority: `docs/decisions/SB-LFX-018-C001-R02-R05-R09-R02-R04-R07_FIVE_SLOT_FOLLOW_ACTIVE_PNG_AND_RELEASE_POOL_OWNER_DECISION_V01.md`, `.hiveai/prompts/SB-LFX-018-C001-R02-R05-R09-R02-R04-R07_FIVE_SLOT_LIVE_BATCH_FOLLOWER_AND_RELEASE_POOL_DASHBOARD_MASTER_PROMPT.md`. Source/design changes only until owner completes currently active nine PNG job and closes installed app normally.

## Level Factory gates
- **LF1 Exactly five:** After N>=5 loaded, precisely 5 visible interactive PNG cards and zero hidden extra click targets. 005 active: 003,004,**005**,006,007. At boundaries start/end clamp, retain five; 009/010 last five, no sixth card. N<5 no fabricated clickable PNG.
- **LF2 Full UI sync:** Each authenticated batch `job_id/current_index/source SHA` transition updates together (1) big displayed PNG, (2) active five-strip highlight/window, (3) right Details run/columns/status/Pool, (4) left Pipeline Activity source and stage; no 002 data attached to 006. Rapid DONE/REUSED/FAILED transitions, source preview during RUNNING, Paused/Interrupted/Complete and restart correct.
- **LF3 Geometry:** Big central image area reduced vertically per owner's white marks, thumbnail dock visibly enlarged under it. Art undistorted and wholly inside, nearest neighbor/zoom/grid/fit intact, five large readable thumbnail cards, dock not overlapping source art. Test native maximized 1536×~864, 1536×1024, 1920×1080, minimum/window resizing.
- **LF4 Security:** Selected PNG and background refresh are strictly read-only; no unsolicited pipeline, no losing original immutable 002 or 003/004... records, no source/run/Pool mismatch; batch planner/4-4-1 quota/serial/native 25k/90s limit unchanged.

## Release Pool gates
- **RP1 Candidate list:** At actual owner maximized display ~14–15 visible compact candidates when count >=15, rest scrollable; no fixed 8 limit; tests 0/5/15/25/150 entries. Search and filters apply across ALL, selections keyed by exact candidate ID not visual index.
- **RP2 Bottom management:** Manage Selection pinned to bottom, Select All and Clear below side by side; all remain visible when scrolling/resizing, selected state correct for filtered results.
- **RP3 Bottom selected:** Three selected candidate cards (+ own X) and Add More Levels are a single 4-box row fully INSIDE lower central dock, below big art, no floating over crab, no hidden hitboxes. Selection 0/1/3, image fit and tab switches correct.
- **RP4 Help:** ⓘ adjacent to each of the eight actual right-hand controls, keyboard/accessibility/focus, concise truthful descriptions/prerequisites; a status-only backend action is described as status-only.
- **RP5 Real activity:** persistent right-hand scroll region shows exact actual selected target/source and timestamped invoked operation, true backend result, error/status/proof; never simulated successes/progress. Disabled/blocked operations, errors, no selection/preflight, valid readbacks tested. Only real operation events may claim stage PASS. No auto-publish via Help or target selection.

## Test, release and handoff boundaries
- **T1 Red→Green** focused UI automated tests actually fail old layout and pass new; validate global rects and visible controls rather than only static source strings. Fake canonical job current_index and fake pool events; zero native solver/replay/load-check or R2/STAGING/PRODUCTION. Owner original nine job artifact set and pool unchanged, no archive/base-temp cleanup.
- **T2 Process and installed Release:** If Studio active (especially nine-PNG job), no install/hotpatch, no force close. Implement/tracked git commit allowed; install only on owner-safe normal close. Back up only changed modules with hashes, preserve desktop shortcut/launcher, report exact product vs final log commit, original file parity.
- **T3 GPT audit and owner visual:** GPT independently review source and Codex focused test evidence, then owner screenshots for LEVEL FACTORY real active tracking (or mocked read-only playback if actual job already finished) and RELEASE POOL 15-row list/four bottom boxes and right Help/Activity. UI technical PASS is not real 9/9 solver PASS, publishing remains gated.

**Automatic FAIL:** six images displayed, active 005 not third when N>=7, stale 002 shown while 006 active, central candidate bar floating over art, pool limited to 8, Release help publishing, fabricated stage logs, modified running Studio Release or any native run initiated by Codex.
