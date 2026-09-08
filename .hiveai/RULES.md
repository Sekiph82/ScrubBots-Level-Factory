# H!veAI Project Control Rules v1

This repository follows the shared H!veAI control-plane schema while preserving project-specific governance.

## Read order

1. `.hiveai/PROJECT.json`
2. `.hiveai/RULES.md`
3. `.hiveai/STATE.json`
4. `.hiveai/HANDOFF.md`
5. `tasks.md`
6. `AGENTS.md` or provider-specific instructions
7. active prompt/audit artifacts required by the current cycle

## Authority

- `tasks.md` is the canonical task ledger.
- `.hiveai/STATE.json` is H!veAI's materialized current-state projection.
- `.hiveai/HANDOFF.md` is the resume pointer.
- `.hiveai/EVENTS.jsonl` is append-only lifecycle history.
- Builder logs are claims only.
- Independent audits are acceptance authority when project governance says so.

## Actor permissions

Existing repository governance remains authoritative:
- Codex may not mark task completion/closure.
- Codex may not rewrite HANDOFF or independent audit history unless an owner-approved prompt explicitly changes governance.
- ChatGPT, acting as independent auditor/tracker owner, may synchronize accepted task/HANDOFF state.
- H!veAI may materialize STATE.json from verified repository/app evidence without changing task acceptance truth.

## Live refresh

H!veAI watches tasks.md, PROJECT.json, STATE.json, HANDOFF.md, EVENTS.jsonl, Git HEAD/index/refs, active prompts/logs/audits, and project watcher events. Refresh is event-driven with debounce; 60-second reconciliation is fallback only.

Provider-specific files may add stricter constraints but may not redefine the shared state schema.
