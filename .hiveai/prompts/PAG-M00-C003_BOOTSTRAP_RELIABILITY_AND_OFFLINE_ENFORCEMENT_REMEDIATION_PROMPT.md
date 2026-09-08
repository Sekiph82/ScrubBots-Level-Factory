# PAG-M00-C003 — Bootstrap Reliability & Offline Enforcement Remediation

Document role: CODEX REMEDIATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`

Previous implementation prompt:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_PROMPT.md`

## 1. Scope

This is a **bounded remediation** for exactly two MAJOR findings from the independent PAG-M00-C002 strict audit.

Do not reimplement the 19 already validated M00 tasks.

Do not begin PAG-M01.

Do not add generator families, palette/difficulty logic, WFC, RULES, MASK, HYBRID, PNG/JSON output, Godot, GUI, or gameplay code.

The only open M00 task IDs are:

- `PAG-0003`
- `PAG-0010`
- `PAG-0020`

## 2. GitHub authority

GitHub is the sole task/prompt/audit authority.

Repository:

`https://github.com/Sekiph82/ScrubBots-Level-Factory`

Do not discover work by searching local sibling folders.

The main game repository:

`C:\Users\sekip\Desktop\ScrubBots`

is OFF-LIMITS for this cycle.

If working on the owner's Windows machine, only synchronize the Level Factory mirror:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

with the authorized GitHub repository, using fetch + safe fast-forward only.

## 3. Mandatory reads

Before coding, read:

- `AGENTS.md`
- `GOVERNANCE.md`
- `tasks.md`
- `.hiveai/HANDOFF.md`
- `.hiveai/CYCLE_INDEX.md`
- `.hiveai/audits/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`
- `.hiveai/codex-logs/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_CODEX_LOG.md`
- this prompt

## 4. Matching builder log

Create before implementation:

`.hiveai/codex-logs/PAG-M00-C003_BOOTSTRAP_RELIABILITY_AND_OFFLINE_ENFORCEMENT_REMEDIATION_CODEX_LOG.md`

Exact H1:

`# PAG-M00-C003 — Bootstrap Reliability & Offline Enforcement Remediation`

Immediately below:

`Document role: CODEX BUILDER LOG`

Record chronologically:

- GitHub authority URL;
- previous audit URL;
- starting branch/HEAD/origin/status;
- safe synchronization;
- exact source changes;
- failed attempts and corrections;
- focused remediation tests;
- full regression tests;
- clean Windows setup evidence;
- offline adversarial evidence;
- final diff;
- implementation commit SHA;
- final log commit SHA;
- push results;
- final local HEAD and `origin/main` equality.

Do not self-audit or declare final PASS/CLOSED.

## 5. Finding F-PAG-M00-C002-001 — MAJOR

### Problem

`scripts/setup.ps1` currently prefers any discovered `python.exe` before the Windows `py.exe -3.12` launcher and does not explicitly validate the interpreter version before venv creation.

The PAG-M00-C002 builder chronology itself showed:

- direct script invocation blocked by the owner's PowerShell execution policy;
- first setup attempt created a broken local venv/interpreter state;
- manual `python -m venv --clear .venv` repair was required;
- Python 3.12 PATH manipulation was required before setup succeeded.

Therefore clean-checkout setup acceptance did not actually close.

### Required target behavior

A clean checkout on the owner's Windows machine must have one documented and reproducible setup path that:

1. deliberately resolves a supported Python interpreter;
2. supports exactly the repository metadata range `>=3.12,<3.13`;
3. prefers the Windows launcher `py.exe -3.12` when available;
4. may fall back to `python.exe` only after verifying its actual runtime version is supported;
5. fails early with a clear actionable error when Python 3.12 is unavailable;
6. creates the repo-owned `.venv`;
7. installs `.[test]`;
8. requires no manual PATH modification;
9. requires no manual venv surgery;
10. does not delete user data.

### Required changes

Modify only the narrow setup/test/documentation surface needed.

At minimum:

- harden `scripts/setup.ps1` interpreter resolution and version validation;
- make the owner-facing README setup command truthful for the owner's PowerShell execution-policy environment;
- if a tiny wrapper such as `scripts/setup.cmd` is the safest way to provide a one-command Windows entrypoint, it is allowed, but do not add unrelated launcher infrastructure;
- keep any execution-policy bypass process-scoped only;
- do not change global Windows policy;
- do not delete arbitrary folders;
- if handling an existing repo-owned `.venv`, restrict any recreate/clear behavior to that exact ignored repository-local environment and log it explicitly.

### Required focused tests/evidence

On the owner's Windows machine, log evidence for:

A. supported-interpreter resolution;
B. explicit reported Python version;
C. clean setup from no usable `.venv`;
D. no manual PATH manipulation;
E. no manual `venv --clear` command outside the setup path;
F. setup installs the package/test extra successfully;
G. the documented owner-facing command works under the current execution-policy environment;
H. unsupported interpreter detection fails clearly when exercised in a safe simulated/testable way where practical.

The final setup proof must not be summarized as “fresh” if manual recovery was necessary.

## 6. Finding F-PAG-M00-C002-002 — MAJOR

### Problem

`guarded_network_request(...)` currently raises only when production code explicitly chooses to call it.

The independent auditor imported the package and then performed a direct standard-library socket operation. That operation reached the OS rather than being rejected by `OfflinePolicyError`.

The existing PAG-0010 test therefore proves the explicit guard function raises; it does not prove a production execution boundary contains direct network access.

### Required target behavior

M00 must expose a **small project-owned offline execution boundary** that future generator entry points can execute inside.

A deliberate direct standard-library network operation inside that protected path must fail closed with a project-owned `OfflinePolicyError` before external networking occurs.

The boundary must:

- be production code, not test-only;
- be dependency-free;
- avoid permanent unsafe global state where possible;
- restore temporary interception state after use;
- work for ordinary local deterministic computation;
- be suitable for future generator-router/CLI entry points;
- not initialize network services at import time.

### Acceptable implementation direction

A narrow context manager / execution wrapper is preferred, for example conceptually:

```python
with offline_runtime():
    generate_locally(...)
```

or:

```python
run_offline(generate_locally, ...)
```

The exact API may differ.

It may temporarily intercept the relevant Python standard-library network boundaries such as socket connection creation while the protected execution is active, then restore them.

Do not globally poison the interpreter at package import.

Do not add `requests`, `httpx`, or any remote client.

### Required focused tests

Add tests proving at minimum:

1. direct `socket.socket.connect` or equivalent connection attempt inside the production offline boundary raises `OfflinePolicyError`;
2. `socket.create_connection` or another separate standard-library network path inside the boundary also fails closed where technically appropriate;
3. the same socket primitive is restored after leaving the boundary;
4. ordinary deterministic local computation runs successfully inside the boundary;
5. package import still performs no network initialization;
6. the existing explicit `guarded_network_request` contract remains compatible or is cleanly superseded with documented rationale;
7. a durable test or narrowly scoped source-policy check prevents accidental forbidden runtime networking code from appearing outside the dedicated offline-boundary implementation, if practical without brittle false positives.

Do not make a test pass merely by calling a function whose body immediately raises without actually attempting a direct network primitive inside the protected execution boundary.

## 7. Regression requirements

Run all pre-existing tests plus the new remediation tests.

Minimum expected regression baseline:

- original 5 tests remain green;
- new setup/offline-focused tests are green;
- package import still works standalone;
- deterministic digest behavior remains unchanged;
- no main ScrubBots checkout dependency;
- no runtime dependencies added;
- no third-party provenance changes unless directly necessary;
- `reference/audits/` remains unchanged;
- no later milestone files appear.

## 8. Clean-install acceptance

Re-prove PAG-0020 truthfully.

The final evidence must show that the documented Windows setup path itself performs the clean setup.

Do not count a run that required manual environment repair as closure.

After setup:

- run the documented test command;
- run package import;
- run the offline adversarial checks;
- run `pip check`;
- record exact Python version and executable path.

## 9. Safety / prohibited shortcuts

Do not:

- touch the main `ScrubBots` repo;
- edit `tasks.md`;
- edit `.hiveai/HANDOFF.md`;
- edit `.hiveai/CYCLE_INDEX.md`;
- author/edit audit files;
- rewrite the C002 prompt/log/audit;
- start PAG-M01;
- add runtime network dependencies;
- modify global PowerShell execution policy;
- add broad shell/process execution APIs;
- delete user files;
- hide failed setup/test attempts;
- declare final M00 acceptance.

## 10. Closure criteria for builder handoff

Codex may end the run as **implementation complete / pending independent audit** only when:

- F-PAG-M00-C002-001 is implemented with repeatable clean Windows setup evidence;
- F-PAG-M00-C002-002 is implemented with direct adversarial network-block evidence;
- all regression tests pass;
- the matching C003 log is complete;
- implementation and final log are committed and pushed;
- final HEAD equals `origin/main`;
- no protected tracker/audit/task files were modified.

ChatGPT will independently re-audit the repository and decide whether PAG-M00 closes and PAG-M01 unlocks.
