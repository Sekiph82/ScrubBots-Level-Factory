# SB-CPX-002-C001-R01 — TEMP-Only Authority Evidence Closure — Audit Criteria

## PASS rule

PASS only if CPX-002 can no longer silently fall back to an owner Desktop ScrubBots checkout, and a fresh authentic current-main Godot replay is produced using only an explicitly resolved isolated TEMP authority.

## A. Sync and owner-local preservation

Require:
- fetch/prune Level Factory origin before work;
- preserve all owner-local Desktop Level Factory files non-destructively;
- never reset, clean, auto-stash, restore, rebase, force or discard owner work;
- use a clean isolated Level Factory execution worktree if the persistent checkout is unsafe.

## B. No Desktop game fallback

Before any Factory bridge, solver, CPX-001 pack construction or CPX-002 replay:
- create/resolve a fresh ScrubBots authority under `%TEMP%`;
- require exact remote `https://github.com/Sekiph82/Scrubbots.git`;
- fetch current `origin/main`, detach at that exact SHA and require clean 0/0 authority;
- explicitly bind `SCRUBBOTS_PROJECT` and every equivalent project/root argument to that TEMP path;
- add a fail-closed regression/guard so the CPX-002 integration path rejects missing or non-TEMP authority rather than using a configured/default Desktop checkout.

No command in the R01 execution may select `C:\Users\sekip\Desktop\ScrubBots` or another persistent owner game checkout as game authority.

## C. Authentic current-main replay

Require fresh evidence for:
- exact current ScrubBots `origin/main` SHA;
- exact authority source hashes;
- actual Godot availability/version;
- exact staged manifest/pack bytes;
- exact CPX-001 LevelData/supply-plan/FIFO/digest binding;
- SupplyPlanLoader acceptance and conservation;
- canonical solver `SOLVED`;
- replay PASS, zero active/unresolved remainder, exhausted supply;
- final origin/main and authority-source drift recheck.

## D. Product scope

Retain the accepted CPX-002 product semantics unless the new fail-closed authority guard requires a narrow integration/adapter change.

Do not modify CP03-008..012 merely to create new commits. Their PASS audits remain valid unless direct semantic regression is found.

## E. Regression/publication

Require:
- focused CPX-002 and authority-boundary tests PASS;
- authentic current-main/Godot integration PASS;
- cumulative M14/M11-M13/governance tests PASS;
- safe unfiltered full pytest PASS;
- compileall, JSON parse and diff-check PASS;
- implementation and evidence-log commits separate when implementation changes;
- normal non-force publication and clean 0/0 parity.

Root `TASKS.md` and `.hiveai/audits/**` remain ChatGPT-owned and must not be edited by Codex.
