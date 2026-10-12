# R05-R09 Strict Independent Audit Criteria

Master: .hiveai/prompts/SB-LFX-018-C001-R02-R05-R09_SIX_CAPPED_SINGLE_CANDIDATE_SOLVER_ATTEMPTS_MASTER_PROMPT.md
Repo and implementation: Sekiph82/ScrubBots-Level-Factory only. Codex builds/logs; ChatGPT alone changes LF root TASKS.md and publishes strict audits.
Owner authorization 2026-10-12: one 90s fresh initial native attempt plus up to FIVE distinct retries; **maximum SIX primary real native candidate solves**, plus at most ONE separately capped shipping load-check for the single winner. Do not confuse processes with calls to native SolvabilitySolver.solve.

## Acceptance criteria

A. Original, game provenance. The current frozen R08 232-file/1,977,597-byte pinned native LF-only Godot runtime and VOID V2 proof are reused and reattested as needed, not redownloaded/rebuilt unnecessarily. Original installed Release 002_32x32px.png and its immutable source.json hashes unchanged, 736 artwork + 288 VOID, no image recolor. Separate Scrubbots checkout absolutely untouched (no git commands/work), and CPX-002 full-game replay remains separate.

B. Four-in-one defect corrected before any new native solver call. Each Godot request has EXACTLY one distinct sha-bound candidate plan and one native solve invocation, explicit stop_after=1, per-source global budget accounting. The R08 prior 4-candidate/one-process attempt is historical with unknown internal count; never rewrite that history. A response with absent native results never claims a successful solve or known visit count.

C. Deterministic nonwasteful retries. Attempt 1 = top eligible ranked supply plan. Up to attempts 2,3,4,5,6 = next DISTINCT candidate, and no retry of identical candidate hash under identical deterministic seed and bounds. Preserve original source art. Existing saved R08 ranked candidates used if trustworthy; maximum enough bounded OFFLINE screening to fill six, never >6 native primary calls. Every attempt <=90s hard wall-clock, explicit <=25,000 max visited/candidate, child process stopped/reaped on timeout. No parallel runaway or new background solvers. Total primary worst-case native time <=540s; optional successful load-check <=90s. Stop immediately upon first genuinely accepted winning candidate.

D. Truthful statuses. Capture small per-attempt durable receipts with source SHA, candidate plan SHA, game SHA, wall-time, native start/end identity, actual returned statuses and timeout reason, bounded output. TIMEOUT, UNKNOWN_BOUND and DEADLOCK are distinct; TIMEOUT/UNKNOWN_BOUND must never imply mathematical proof of failure. If attempts exhausted (or unique candidate pool exhausted earlier), owner-facing EXACT status **UNSOLVED** with attempts_run, retries_run, per-status counts and proof_of_global_unsolvability:false. UNSOLVED here is an OPERATIONAL retry-budget decision, not a canonical Solver status or an assertion that all configurations are impossible. Fatal safety/authority/IO issues stop BLOCKED, not forced UNSOLVED.

E. Genuine winner only. Real LevelData V2, 3/4/5 FIFO supply columns, replay WIN fresh state, official Difficulty V1, color/plan conservation, QA, shipping load-check for SAME winner under independent <=90s cap, correct source/pipeline/Release Pool identity are individually proven. Any missing proof => NOT_READY, no fake READY_AUTO. Even offline technical SOLVED does not bypass CPX-002 full-game current-source replay, R2 STAGING/PRODUCTION owner consent or Family APK deployment.

F. Tests only new affected work. New small focused tests cover 4-in-one regression protection, uniqueness and six-call maximum, TIMEOUT vs DEADLOCK/UNKNOWN_BOUND, early stop on valid SOLVED, max one capped optional load-check, corrupted authority fail-closed and original source SHA protection. Old R08 4+1, R04, R05-R05, M14/M18 and full regression NOT rerun. Do not run actual native performance stress as a unit test.

G. Resource and repository safety. LF original Desktop only, safe sync and normal FF commit to GitHub main, no new clone, TEMP worktree, OS TEMP scratch or cleanup. All 57 preexisting owner-local paths preserved, installed Release app, launcher and game checkout untouched. Jobs and summary are small, confined to ignored existing LF output. No R2 calls/credentials or publication.

H. Builder delivery. Append single concise R09 section to existing R05 builder log, including precise number of primary native calls and optional load-check, attempts indexes, 90s cap, original SHA, technical statuses, proof filenames and overall UNSOLVED or authentic single-source outcome. Code/tests + log published to LF main, GitHub parity 0 ahead/0 behind. Codex leaves root TASKS.md/audits untouched; independent audit comes after log.

## Verdicts

- SINGLE_SOURCE_OFFLINE_SOLVED_SHIPPING_PENDING: verified true offline native SOLVED/WIN/Difficulty V1/QA and bounded load-check plus honest still-open CPX-002 and owner release gates.
- UNSOLVED_RETRY_BUDGET_EXHAUSTED: six DISTINCT bounded primary attempts unsuccessful, no false READY.
- UNSOLVED_CANDIDATE_POOL_EXHAUSTED: fewer than six distinct valid candidates remain; no more native calls, truthful attempts count.
- BLOCKED_PRECONDITION: authority, code, process/OS, schema, file integrity or safety fault. Stop before wasting retries.
- CHANGES_REQUIRED: >6 calls, any four-in-one bridge call, >90s/call, hidden retry of same plan, false mathematically proven UNSOLVED, original art/game repo modification, old test reruns, cloud writes, destructive cleanup or fabricated READY.

Parent R05 and final Family APK shipment remain OPEN.
