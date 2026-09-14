# Factory Workspace and Exclusions

This is the repository-wide workspace policy for the offline Factory tooling.
It separates durable source and evidence from generated output, transient
candidates, caches, local logs, and local-only secrets. It does not create a
cleanup scheduler, task tracker, secret manager, or operational control plane.

| Class | Examples | Git treatment | Retention / cleanup |
| --- | --- | --- | --- |
| Tracked source | `src/`, root `tests/`, `docs/`, `level_factory/project.godot`, `level_factory/README.md`, `level_factory/GOVERNANCE.md`, `level_factory/docs/`, `level_factory/scenes/`, boundary markers, `TASKS.md` | Tracked and visible | Durable; change only through an authorized implementation or governance task |
| Durable audit/review/reference evidence | `review/`, `reference/`, `.hiveai/prompts/`, `.hiveai/codex-logs/`, `.hiveai/audits/` | Tracked and visible | Durable evidence; never treated as disposable generated output |
| Durable source/evidence assets | `data/`, `exemplars/` | Tracked and visible | Not disposable caches merely because they are machine-readable; cleanup requires a later authorized workflow |
| Generated output | Root `output/` and `level_factory/output/` | Contents ignored; intentional `.gitkeep` markers tracked | Retained locally as needed; cleanup only by an explicitly authorized later workflow. Existing output is not automatically accepted production content |
| Candidate/transient output | `output/candidates/` when produced by batch tooling | Covered by the generated-output boundary and ignored | Transient generation space, never a second durable evidence store; cleanup only when explicitly authorized |
| Cache/temp state | `.venv/`, bytecode, pytest/mypy/ruff caches, `build/`, `dist/`, coverage output, `level_factory/.godot/`, WFC caches, `tmp/`, `temp/` | Ignored and local | Eligible for cleanup only through an explicitly authorized later workflow; this policy performs no cleanup |
| Local runtime logs | `logs/` and ordinary `*.log` files | Ignored and local | Local diagnostics only; cleanup is not performed by this task |
| Tracked builder evidence | `.hiveai/codex-logs/` | Tracked despite ordinary runtime `logs/` being ignored | Durable process evidence; never hidden by the runtime-log rule |
| Local-only secrets | `.env` and `.env.*` local variants, `.secrets/`, `secrets/`, `level_factory/.secrets/`, `level_factory/secrets/` | Ignored and never committed; root `.env.example` is allowed as a future non-secret template | No credential is required to be stored in Git. This task creates no secret and does not inspect external credential stores |

`review/` is durable tracked evidence and is not equivalent to generated
`output/`. Likewise, `.hiveai/codex-logs/` is tracked builder evidence even
though ordinary runtime `logs/` is ignored. `data/` and `exemplars/` remain
source/evidence surfaces, not disposable caches.

`level_factory/output/` is a Godot-facing generated/export staging surface,
not canonical tracker truth. The root `TASKS.md` remains the sole live task
ledger. No API credential, token, OAuth refresh data, private key, local secret
store, or machine-specific credential material may be committed to this
repository.

This document defines boundaries only. It does not move the root output/batch
implementation, delete owner-generated files, or claim that broader retention,
cleanup, or secret-management work is complete.
