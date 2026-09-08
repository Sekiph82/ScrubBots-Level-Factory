# PAG-M00-C003 — Bootstrap Reliability & Offline Enforcement Remediation
Document role: CODEX BUILDER LOG

## Cycle scope and authority

- Authority repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`
- Authoritative remediation prompt, read directly from GitHub raw content:
  `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/prompts/PAG-M00-C003_BOOTSTRAP_RELIABILITY_AND_OFFLINE_ENFORCEMENT_REMEDIATION_PROMPT.md`
- Previous strict audit:
  `https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`
- Previous implementation/log: PAG-M00-C002; preserved and not rewritten.
- Superseded cycle: PAG-M00-C001; not used.
- Scope: exactly the two cited MAJOR findings. No PAG-M01 or generator-family work.
- Log creation timestamp: `2026-09-08T18:35:08.5223505+03:00`.

## Starting state and safe synchronization

Canonical mirror:
`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Repository identity was verified as `Sekiph82/ScrubBots-Level-Factory`; origin
was `https://github.com/Sekiph82/ScrubBots-Level-Factory.git`; branch was
`main`. Before synchronization, status was `## main...origin/main` with no
working-tree changes. The sibling `C:\Users\sekip\Desktop\ScrubBots`
repository was not inspected or used.

The required non-destructive sequence was executed:

1. `git fetch origin main` advanced `origin/main` from `a2bd3aa` to
   `7dbf578`; `git rev-list --left-right --count HEAD...origin/main` returned
   `0 5`.
2. `git merge --ff-only origin/main` fast-forwarded the mirror from
   `a2bd3aa93ead73140690c84536164ed431b75d7c` to
   `7dbf57869fac921be8032d326115f40e40a2717d`.
3. The post-sync branch was `main`, status was clean, and local HEAD equaled
   `origin/main` at `7dbf57869fac921be8032d326115f40e40a2717d`.

No reset, rebase, clean, force-push, or discard operation was used.

## Mandatory inputs read

Read completely from the authorized checkout:

- `AGENTS.md`
- `GOVERNANCE.md`
- `tasks.md`
- `.hiveai/HANDOFF.md`
- `.hiveai/CYCLE_INDEX.md`
- `.hiveai/audits/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_STRICT_AUDIT.md`
- `.hiveai/codex-logs/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_CODEX_LOG.md`
- the C003 remediation prompt directly from GitHub

The active prompt identified only `PAG-0003`, `PAG-0010`, and `PAG-0020` as
open remediation scope. No task, tracker, handoff, cycle-index, prompt, or
audit file was modified.

## Process correction before test/commit

The first product patch was applied before this matching C003 log was created,
which did not follow the prompt's required ordering. This was not concealed or
discarded; the issue is recorded here before finalization. The log was then
created before any further source changes, and all subsequent tests, evidence,
and commits are recorded chronologically below.

## Finding F-PAG-M00-C002-001 remediation: Windows setup

`scripts/setup.ps1` now:

- prefers `py.exe -3.12`;
- reports the selected runtime version and executable path;
- falls back to `python.exe` only after validating its actual version is 3.12;
- fails with an actionable Python 3.12 / `>=3.12,<3.13` message otherwise;
- creates or clears only the exact repository-local `.venv`;
- validates the created venv's Python version;
- installs `.[test]` into that venv;
- never changes PATH or global PowerShell policy;
- performs no deletion outside the repository-owned `.venv` handling.

README now documents:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1`

and the corresponding test command. The bypass is process-scoped and does not
change global execution policy.

The first run of the revised setup script failed because a PowerShell native
output pipeline overwrote `$LASTEXITCODE` with `-1`, falsely rejecting valid
`3.12.10`. The script was corrected to capture probe output and exit code
before pipeline processing. The same documented command then succeeded using
`py.exe -3.12`, printed Python `3.12.10` at
`C:\Users\sekip\AppData\Local\Programs\Python\Python312\python.exe`,
cleared only the repository-local `.venv`, reported the created venv path, and
installed the package/test extra. No manual PATH modification or external
`venv --clear` repair was used in this remediation run.

## Finding F-PAG-M00-C002-002 remediation: offline execution boundary

`src/scrubbots_pixel_factory/offline.py` now provides the production
`offline_runtime()` context manager. While active, it temporarily substitutes
the standard-library `socket.socket` class with a project-owned subclass whose
`connect` and `connect_ex` fail with `OfflinePolicyError`, and substitutes
`socket.create_connection` with the same denial. The original symbols are
restored in `finally`, including when protected work raises. Import remains
side-effect free; no HTTP client, socket connection, or remote service is
initialized at import time.

The existing `guarded_network_request()` contract remains available and now
shares the same project-owned denial. `offline_runtime` is exported from the
package root for future generator entry points.

Focused tests cover direct `socket.socket.connect`, `socket.create_connection`,
temporary interception restoration, deterministic local work inside the
boundary, import-time network initialization, the explicit guard contract,
standalone import, and a narrow source-policy scan that excludes only the
dedicated boundary module from standard-library/network import checks.

## Test and evidence chronology

All commands ran in the authorized Level Factory mirror.

1. Focused offline remediation tests after the first product patch:
   `7 passed in 0.23s`.
2. First documented setup run failed at the new venv-version check because of
   the `$LASTEXITCODE` pipeline bug described above. The script was corrected.
3. Rerun of the exact documented owner-facing setup command succeeded. It
   selected `py.exe -3.12`, reported Python `3.12.10`, recreated only the
   repository `.venv`, installed `scrubbots-pixel-factory==0.1.0` and pytest
   test dependencies, and finished with `Environment ready`.
4. Rerun of the documented process-scoped test command passed all tests:
   `9 passed in 0.18s` on Windows Python `3.12.10`, pytest `9.1.1`.
5. Post-setup package import passed and resolved from this checkout's `src`.
   `pip check` reported `No broken requirements found`.
6. A deliberate direct `socket.socket().connect(('203.0.113.1', 9))` inside
   `offline_runtime()` failed with project-owned `OfflinePolicyError` before
   OS networking; the process exit was `1`. The focused suite separately
   proves `socket.create_connection` is denied and symbols are restored.
7. Setup contract checks passed for launcher priority, fallback version
   validation, explicit venv scope, and absence of PATH mutation.
8. `py -3.12 -m pip install --dry-run --no-deps --no-build-isolation .`
   reported `Would install scrubbots-pixel-factory-0.1.0`.
9. `git diff --check` passed after the implementation edits.

Unsupported-interpreter handling was exercised by source-contract assertions:
the setup script requires exact Python 3.12 for both launcher selection and
validated fallback, and contains an actionable failure message. The owner's
available `py.exe -3.12` path was used for the actual clean setup.

## Files changed in this remediation

- `scripts/setup.ps1`
- `README.md`
- `src/scrubbots_pixel_factory/__init__.py`
- `src/scrubbots_pixel_factory/offline.py`
- `tests/integration/test_offline_boundary.py`
- this matching C003 builder log

No runtime dependencies, third-party provenance, generated output, later
milestone files, `reference/audits/`, task state, tracker state, handoff,
cycle index, prior C002 log, prompt, or audit was changed.

## Finalization

The implementation diff is limited to the two audited MAJOR findings and the
owner-facing documentation/tests required to prove them. No audit was
performed or authored. Builder status is implementation complete / pending
independent audit; this record does not declare `PASS` or `CLOSED`.

The implementation commit SHA, final log commit SHA, push results, final
status, and local/remote equality will be appended after the commits execute.

Implementation commit: `42ecae4f7408191b3c9f23918cb60627ff76dae6`
(`fix: harden bootstrap and offline boundary`). The implementation commit was
pushed successfully with `git push origin main`, advancing GitHub `main` from
`7dbf57869fac921be8032d326115f40e40a2717d` to that SHA. The tree was clean
before the log-only completion append.
