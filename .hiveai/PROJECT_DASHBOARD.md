hiveaiDashboardSchema: hiveai-project-dashboard/v1
projectKey: scrubbots-level-factory
repository: Sekiph82/ScrubBots-Level-Factory
branchPolicy: main
dashboardMode: source-map
trackingMode: canonical-control-plane-v1
refreshPolicy: watcher-first-500ms-plus-60s-reconcile

## Source authorities

Canonical task source: `tasks.md`
Handoff source: `.hiveai/HANDOFF.md`
Progress/history source: `.hiveai/EVENTS.jsonl`
Architecture source: `.hiveai/PROJECT.json`
Decision/governance source: `.hiveai/RULES.md`
Agent instruction source: `AGENTS.md`
Independent audit source: `.hiveai/audits/`

## Contract

Pointer-only compatibility manifest. Current state must come from STATE.json + canonical task/HANDOFF/Git evidence, not historical prose in this file.
