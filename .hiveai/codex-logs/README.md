# Codex Builder Logs

This directory stores immutable builder execution logs.

Builder logs are claims and execution evidence only. They are not independent audits and never close tasks.

For every cycle, the matching log must use the exact same H1 as its prompt and audit.

Example:

`# PAG-M00-C001 — Repository Bootstrap & Governance`

Immediately below the H1:

`Document role: CODEX BUILDER LOG`

Codex may create the log for the active cycle and append to it during that run. Once submitted/pushed for audit, it becomes historical evidence and must not be rewritten to hide failures.
