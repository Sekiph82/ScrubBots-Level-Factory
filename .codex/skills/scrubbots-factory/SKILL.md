---
name: scrubbots-factory
description: Continue one explicitly authorized ScrubBots Level Factory task at a time without using a dashboard.
---

# ScrubBots Factory

Use this workflow only in `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator` for `Sekiph82/ScrubBots-Level-Factory`.

1. Run `python -B scripts/codex/scrubbots_task_queue.py --json`. It is a read-only guard, not a task claimant. If it fails, stop and explain the exact mismatch in this chat.
2. Read only the exact prompt returned by the guard, the named previous audit/contracts, root `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, and the sync/publish standard. Treat the current prompt as the boundary for that task.
3. Do not infer the next task from unchecked rows. Work only on the explicit current task. Never use a dashboard, dashboard inbox, or another task ledger. Ask the owner questions in the active chat and wait when work depends on an answer.
4. Preserve owner files, Release data, PNGs, jobs, Pool records, installed data, and all untracked files. Never reset, clean, stash, rebase, force-push, use TEMP/worktrees/clones, or run CI/Actions. Do not run paid providers or `Release -Apply` unless a later task explicitly authorizes the exact operation.
5. Make only changes in the active task scope. Run only its bounded local checks, with Python bytecode and pytest caches disabled. Record failures and unrun gates truthfully.
6. Do not claim independent audit, owner visual/native acceptance, or release acceptance. Do not advance task state beyond the evidence allowed by the current task. The owner may authorize task-state edits in chat, but any active prompt prohibition still requires explicit owner direction for that exact exception.
7. Continue into another task only when the owner or current authoritative task explicitly directs that sequence. No background polling or self-triggered process loop.

The queue guard prints no dashboard links and never writes `TASKS.md`; chat is the owner-question and answer channel.
