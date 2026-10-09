# SB-LFX-018-C001-R02-R05-B01-R02 — Disk Footprint Optimization Strict Audit

The original R05 and B01 safety/audit criteria remain binding, with the explicit R02 owner correction superseding the earlier blanket "do not delete" assumption. No R05 PASS without original R05 technical gates.

## Owner decision / authority
- R02 explicitly records owner rejection of 65 GB-scale test duplication, not a blanket instruction to keep test fixtures.
- No deletion command was executed on the two prior fixtures, and the automated policy blocked the earlier exact-path request. Neither Codex nor a prompt may bypass that gate.
- No owner project data, protected temp contents, Git objects, local worktree changes, or existing builder evidence are deleted/overwritten without legitimate authorization.
- Current baseline and incremental peak storage consumption are measured. No individual new test >4 GiB projected; no >8 GiB cumulative added storage under continuation. Never treat free space as authorization for oversized tests.

## Engineering efficiency
- Route A no longer needlessly holds the 4.718 GB additional clone AND 2.526 GB on-disk archive AND 2.201 GB extracted project simultaneously when an exact canonical verified authority exists.
- Batch catalog integration no longer retains both the 2.526 GB tar and 2.522 GB extracted tree.
- Genuinely stream archive contents or demonstrate a measurably equivalent safe low-disk mechanism, preserving exact-current SHA, complete real-game contents, full Git authority/VOID, source immutability, truly isolated mutations, Godot script execution and authentic negative checks.
- No unsafe mutable hardlinks, leakage into owner checkout, fake verifier/game, permanent skip/xfail or loss of identity/solver/replay assertions.
- Remaining large tests and fixture retention audited before full run. Original pytest-2308 paths remain untouched by fresh tests, including implicit tmp pruning.

## Correctness gates
- Prior 84% test failures/errors reproduced/classified and resolved individually, headless real import test completes under truthful bound.
- External distinct PNG A READY / B FAILED / C READY canonical identity/order and negative cross-binding tests genuinely PASS.
- Existing production history N->N+1->N+2 / CP03-008/009 adversarial tests genuinely PASS.
- Full correctly configured authority-enabled pytest completes 0 fail / 0 error. Original R05 LF19/VOID, native three-master UI, Godot parse/runtime, release installation, screenshots from installed code and hash publication, compileall, diff check and secret scan still pass.
- Publication remains blocked until full original R05 PASS evidence, GPT independent audit still required, root `TASKS.md` only maintained by GPT.

Outcome before all gates: `R05_UNVERIFIED / NO_INSTALL_NO_PUBLICATION`.
