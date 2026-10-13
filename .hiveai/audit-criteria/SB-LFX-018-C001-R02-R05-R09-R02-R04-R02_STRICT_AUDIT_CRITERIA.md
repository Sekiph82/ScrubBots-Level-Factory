# SB-LFX-018-C001-R02-R05-R09-R02-R04-R02 — GPT Independent STRICT Audit Criteria

**Scope:** Owner-screen visual layout change and first-class persistent sequential Level Factory PNG batch. This is a new direct-owner modification, not permission for the builder to actually solve all imported PNGs.

**Authoritative:** `docs/decisions/OWNER_FACTORY_STUDIO_LEVEL_FACTORY_COMPACT_BATCH_20261013_V01.md` and `.hiveai/prompts/SB-LFX-018-C001-R02-R05-R09-R02-R04-R02_FULL_WINDOW_DETAILS_INLINE_RESULTS_AND_SEQUENTIAL_BATCH_MASTER_PROMPT.md`.

## Owner UI / source boundaries

| Gate | PASS only if |
| --- | --- |
| V01 Full-screen client | At client 1536×864/1024, 1920×1080 and minimum target, application content extends to all four actual **client** edges (normal padding acceptable) with no 110px side bands and no bottom unused wide stripe. Native taskbar/titlebar not painted over, no clipping/overlap. Existing root uniform-letterbox policy removed or overridden responsibly. |
| V02 3 tab independence | PIXEL ART / LEVEL FACTORY / RELEASE POOL still fully functional; responsive resize doesn't disturb other two screens' important controls. No fourth screen/extra overlay/nav. |
| V03 Details compact | Up to **five rows**, 2 true fields each, source SHA and `Source:` absent from visual Details; full provenance unchanged in artifact and tooltips/logs, no secretly omitted necessary level result. Correct current source, run, columns, RUNNING, review and Pool states. |
| V04 Actions | Immediately after details EXACT two buttons side-by-side `Preview Replay | Supply Plan` and next line EXACT three `Solve Again | Accept | Reject` with legible captions, keyboard/tab/press handlers. |
| V05 Inline one-panel scroll | Below action rows, scrollable in-card live Results fills remainder. No external giant gray dialogs for Replay/Supply. Current original 002 4-col true values and 51 steps show legibly, one content mode at a time, scroll behavior actually tested, errors remain truthful. Preview trace not represented as a fake full game simulation. |
| V06 Art contract | Nearest pixel filtering, undistorted square pixels, zoom/grid/fit, source switching and gallery intact, no source byte mutations; source/run proof bound to correct selected preview. |

## Batch engine / storage boundaries

| Gate | PASS only if |
| --- | --- |
| B01 Explicit trigger | Multiple imported/ready-to-queue PNGs offer `Run Entire Batch (N)` or `Resume Batch` via **existing Level Factory Run action**; one click initiates sequential job; NONE on import, PNG select, tab, startup or test. Single Run Pipeline and manual columns remain working. |
| B02 Canonical source truth | Each item reuses authentic source SHA and existing 20..59 logical/art palette/VOID/derivation verification, no silent resizing or fake playable items; selected source maps to own immutable candidate/run. |
| B03 45/40/15 exact deterministic | 3-col quota 45%, 4-col 40%, 5-col 15%, largest remainders tie 3→4→5. Examples 9=4/4/1; 40=18/16/6; 100=45/40/15; 150=68/60/22. Generated assignments stable across restarts, interleaved, persisted; per-source assigned column reaches **real backend request and canonical supply**, not just button state. Planned vs actually READY mix separately truthful if failures. |
| B04 Sequential total batch | At least 150 distinct inputs handled in fake-runtime integration, concurrency max 1. Correct success/failure/rejection states and continuing after an individual failure, full stage schema, official solver, replay, Difficulty V1, QA, true READY_AUTO pool readback, no extra ACCEPT required. Existing single 002 remains eligible, 003 never inherits false READY. |
| B05 Durable / exactly-once-on-success | Atomic per-transition persisted job with source digest, ordered IDs, assigned column, unique activity run, proof and per-item state. Interrupt at before/after READY and pool insertion, restart/resume, duplicate click and paused processing skip verified-complete without expensive repeat; recover unverified partial honestly. No stale run aliasing or file overwrite. |
| B06 Campaign numbering / publish | Only READY consume *relative publish order*, failed and duplicate don't consume a permanent level number. CampaignBuilder later assigns actual contiguous N+1.. only on separate owner-approved publication. No R2/STAGING/PRODUCTION or current Scrubbots full-game replay gate bypass. |
| B07 Owner controls and progress | Owner sees per-item index, source file, 3/4/5 selection, stage, elapsed, completed/failed/skipped/remaining, Pause/Resume. Native 25k visited/90 seconds per invocation preserved; backend never swallows error nor permits 2 simultaneous jobs. |
| B08 Source identity and disk | Existing original PNG/record, historical 002 run, supplements, pool entry, pinned 232-file mini-runtime hashes unchanged; per-run new outputs distinct; tests bounded in count, generated file bytes/disk tracked, never reuse protected `.m17` basetemp. |

## Tests and delivery

- **Zero Codex native Scrubbots solver, replay-run, load-check.** All initial tests fake/spy. A new real batch requires explicit owner UI click AFTER install/independent audit, not a builder qualification.
- Fresh focused unit and Godot UI/integration tests must **prove** widget positions/scrollability/current source + actual backend arguments, not source-string assertions alone; include 150-item fake stress and interrupted/resumed job.
- No full old regression repeat, 148 native batch, game repo write, cloud/R2, publication, destructive clean, unexpected user disk edits.
- Builder safety install: check running application; if running stop `OWNER_CLOSE_STUDIO_TO_INSTALL`, not forced exit; backup only small changed installed overlay; SHA manifest and true Desktop `.lnk`/PS1 unchanged.
- Check actual GitHub SHA/diff, builder log, tests and provenance. GPT writes root TASKS/audit; Codex never does. Owner Windows screenshots required for visual full PASS. If batch engine implemented/tested but no owner-initiated real batch yet, record `BATCH_TECHNICAL_PASS / OWNER_LIVE_RUN_PENDING`, not a fabricated native READY population.
- User supplied R04-R01 screenshots confirm earlier 002 Replay data opens but is unreadable; supply content is real but non-scrollable. These count as **GUI REWORK REQUIRED**, not passing the new compact inline UI scope.

**Verdict:** Anything that starts batch without explicit click, reruns completed batch source, submits/claims unsolved as READY, assigns final level number to failure, leaves letterbox strips, retains overlap, or falsely claims cloud publish = FAIL. Only close R04-R02 after all UI and batch gates, source and builder checks, and owner visually validates installed UI.
