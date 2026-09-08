---
hiveaiDashboardSchema: hiveai-project-dashboard/v1
projectKey: scrubbots-level-factory
repository: Sekiph82/ScrubBots-Level-Factory
branchPolicy: main
dashboardMode: source-map
refreshPolicy: watcher-driven source invalidation; no generated status commits
---

# H!veAI Project Dashboard Manifest

This file is a pointer map for H!veAI. It is not a task ledger and must not duplicate task checkboxes.

## Project identity

Project: ScrubBots Level Factory — Pixel Art Generator V1
Repository: `Sekiph82/ScrubBots-Level-Factory`
Default branch: `main`
Canonical local repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
Primary role: offline procedural pixel-art generation tooling for SCRUBBOTS.

## Source authorities

Canonical task source: `tasks.md`
Handoff/current-cycle source: `.hiveai/HANDOFF.md`
Roadmap source: `tasks.md`
Progress/history source: `.hiveai/CYCLE_INDEX.md`
Architecture/governance sources: `AGENTS.md`, `GOVERNANCE.md`, `tasks.md`
Decision source: `GOVERNANCE.md` plus accepted independent audits under `.hiveai/audits/`
Agent instruction source: `AGENTS.md`
Security/offline source: `GOVERNANCE.md` and `tasks.md`
Prompt source: `.hiveai/prompts/`
Builder log source: `.hiveai/codex-logs/`
Independent audit source: `.hiveai/audits/`
Historical SCRUBBOTS audit reference: `reference/audits/`
Build/test metadata: `pyproject.toml`, test configuration, CI configuration if later added.

## Authority notes

`tasks.md` is the sole canonical detailed task ledger. Only ChatGPT acting as the independent auditor/tracker owner may change task completion state or milestone/sprint closure state.

Codex builder logs are claims/evidence records, never acceptance authority.

Used prompts, Codex logs, and audits are immutable historical records. Remediation requires a new cycle ID rather than rewriting an earlier record.

The main SCRUBBOTS repository remains authoritative for owner-locked gameplay/palette/visual contracts when explicitly referenced by this project.

## Refresh model

H!veAI should derive live state from Registry/Git/watcher evidence plus the canonical sources above. This manifest remains pointer-only and must not be rewritten as a generated status snapshot.
