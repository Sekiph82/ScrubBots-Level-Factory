# PAG-M00-C001 — Repository Bootstrap & Governance

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor and tracker owner: ChatGPT  
Repository: `Sekiph82/ScrubBots-Level-Factory`  
Branch: `main`  
Canonical local repository root: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## 1. Objective

Implement and verify **PAG-M00 — Repository Bootstrap & Governance** only.

This cycle establishes a clean, Windows-first, Python-based, offline-only project foundation for the SCRUBBOTS Procedural Pixel Art Generator V1.

Do **not** begin PAG-M01 palette/difficulty contract implementation.

Do **not** implement MASK, RULES, WFC, HYBRID, CLI generation, output generation, or gameplay logic in this cycle.

## 2. Mandatory preflight

Before changing product files:

1. Run:
   - `git fetch origin main`
   - `git rev-list --left-right --count HEAD...origin/main`
2. Fast-forward with `git merge --ff-only origin/main` only if safe.
3. Do not reset, auto-rebase, force-push, discard user changes, or clean untracked user files.
4. Verify and log:
   - `git rev-parse --show-toplevel`
   - `git branch --show-current`
   - `git rev-parse HEAD`
   - `git remote -v`
   - `git status --short`
   - `git stash list`
   - `git worktree list`
5. The resolved repository root must be the canonical local folder:
   `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`
   Windows separator/casing normalization is acceptable, but working from another clone is not.
6. The branch must be `main`.
7. The origin must resolve to `Sekiph82/ScrubBots-Level-Factory`.

If any preflight condition cannot be satisfied safely, stop before product implementation and record the exact reason in the matching Codex log.

## 3. Read completely before implementation

Read:

- `AGENTS.md`
- `GOVERNANCE.md`
- `tasks.md`
- `.hiveai/PROJECT_DASHBOARD.md`
- `.hiveai/HANDOFF.md`
- `.hiveai/CYCLE_INDEX.md`
- `reference/audits/README.md`
- `reference/audits/scrubbots/coordination/AUDIT_POLICY.md`
- `reference/audits/scrubbots/coordination/sessions/META-C005/CHATGPT_AUDIT_V01.md`
- this prompt

The historical audits are reference evidence only. Do not reinterpret them as current task authority.

## 4. Mandatory matching Codex log

Before product implementation, create:

`.hiveai/codex-logs/PAG-M00-C001_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_CODEX_LOG.md`

Its exact H1 must be:

`# PAG-M00-C001 — Repository Bootstrap & Governance`

Immediately below it write:

`Document role: CODEX BUILDER LOG`

Append chronologically. Do not erase failed attempts after correcting them.

The log must include:

- start timestamp,
- repository-root proof,
- branch/HEAD/origin proof,
- synchronization result,
- initial status/stash/worktree state,
- documents read,
- implementation decisions,
- every material command,
- failures and corrections,
- dependency decisions,
- third-party license/provenance verification,
- tests added,
- focused tests run,
- regression/full tests run,
- offline-boundary verification,
- files changed,
- final diff summary,
- commit SHA(s),
- push result,
- final local HEAD,
- final `origin/main` HEAD,
- equality/divergence statement.

Never record secrets.

## 5. Strict ownership boundary

Codex must not edit:

- task states or checkboxes in `tasks.md`,
- `.hiveai/HANDOFF.md`,
- `.hiveai/CYCLE_INDEX.md`,
- any file under `.hiveai/audits/`,
- this used prompt after implementation begins,
- any historical prompt/log/audit record.

Codex must not author an audit or declare final PASS/CLOSED.

Codex may state in its log which task IDs it believes are implemented, but ChatGPT alone decides closure.

## 6. In-scope task IDs

Implement the repository work required by:

### PAG-S00.1 — Project bootstrap

- PAG-0001 Create Python package structure under `src/scrubbots_pixel_factory/`.
- PAG-0002 Add `pyproject.toml` with supported Python and explicit dependencies.
- PAG-0003 Add a Windows-friendly local setup command.
- PAG-0004 Add a local test command.
- PAG-0005 Add `.gitignore` entries for virtualenv, Python caches, generated PNG/JSON, logs, build/coverage artifacts, and temporary WFC caches.
- PAG-0006 Add `output/.gitkeep` while ignoring generated output contents.
- PAG-0007 Add a minimal root `README.md` explaining Pixel Art Generator V1 scope.
- PAG-0008 Add an explicit OFFLINE_ONLY policy to project documentation.
- PAG-0009 Encode the rule that runtime HTTP/API calls are forbidden for core generation.
- PAG-0010 Add a test that would fail if a production generation path attempts network access.

### PAG-S00.2 — Third-party provenance

- PAG-0011 Create `THIRD_PARTY_NOTICES.md`.
- PAG-0012 Record `ikarth/wfc_2019f` URL, license, and exact upstream commit/tag verified during this cycle.
- PAG-0013 Record `mxgmn/WaveFunctionCollapse` URL, license, and exact upstream commit/tag verified during this cycle.
- PAG-0014 Record `mxgmn/MarkovJunior` URL, license, and exact upstream commit/tag verified during this cycle.
- PAG-0015 Record `zfedoran/pixel-sprite-generator` URL, license, and exact upstream commit/tag verified during this cycle.
- PAG-0016 Preserve required MIT notices for any code copied or substantially adapted during this cycle. Prefer copying no third-party algorithm code in M00.
- PAG-0017 Do not copy third-party example artwork/assets unless independently licensed. For M00, copy none.
- PAG-0018 Establish a provenance-comment convention for future substantially adapted modules.
- PAG-0019 Document which sources are algorithm references versus future possible adapted-code sources.

### M00 acceptance evidence

Prepare evidence relevant to:

- PAG-0020 Clean checkout installs locally.
- PAG-0021 Tests run locally without requiring the main Scrubbots repo.
- PAG-0022 Generator package imports without network access.

Do not mark these tasks complete yourself.

## 7. Required project skeleton

Create at minimum:

```text
README.md
AGENTS.md                         # already ChatGPT-owned; do not modify unless absolutely required and authorized
GOVERNANCE.md                     # already ChatGPT-owned; do not modify
pyproject.toml
.gitignore
THIRD_PARTY_NOTICES.md

src/
  scrubbots_pixel_factory/
    __init__.py

output/
  .gitkeep

tests/
  unit/
  integration/
```

You may add narrowly justified bootstrap support files such as:

- `scripts/setup.ps1`
- `scripts/test.ps1`
- `tests/conftest.py`
- `tests/unit/test_import.py`
- `tests/integration/test_offline_boundary.py`

Do not create the later generator architecture modules merely to fill folders.

## 8. Python baseline

Use Python 3.12 as the preferred V1 baseline unless the local environment proves it unavailable or a dependency incompatibility is directly demonstrated.

If the machine has a different usable Python version, do not silently change the repository baseline. Record the environment fact in the log and keep the declared project baseline deliberate.

Keep M00 dependencies minimal.

Do not add WFC/Markov/sprite-generator as runtime dependencies in this cycle.

Do not vendor third-party algorithm source in this cycle.

## 9. Windows setup and test UX

Provide simple PowerShell entry points or equivalent documented commands so the owner can use the project from the canonical local folder.

Preferred conceptual UX:

```powershell
./scripts/setup.ps1
./scripts/test.ps1
```

Requirements:

- setup creates/uses a local virtual environment rather than global install where practical;
- setup must fail clearly on unsupported Python;
- test command must run the repository test suite;
- scripts must use safe argument/process invocation;
- scripts must not download runtime assets or call cloud APIs beyond ordinary package installation required for environment setup;
- generation/runtime tests themselves must not require network.

Package installation during development/setup is not the same as runtime generation. The offline invariant applies to the generator's operational runtime.

## 10. Offline boundary design

M00 does not yet have real generator implementations, so do not fabricate a fake production generator just to satisfy PAG-0010.

Instead establish a reusable production network-denial boundary appropriate for later generator modules.

Acceptable patterns include:

- a small project-owned offline guard/context used by generation entry points later,
- test instrumentation that blocks Python socket/network primitives for modules under the production package,
- an explicit architecture hook that future generator entry points must execute under.

The test must be meaningful enough that a deliberately introduced network attempt through the protected production path would fail.

Do not monkeypatch a test-only fake function that production code never uses.

Do not add a remote service client and then “disable” it.

## 11. README requirements

The root README must clearly state:

- this repo is the standalone SCRUBBOTS Pixel Art Generator V1;
- it is not the complete Level Factory;
- it is offline/local-laptop tooling;
- Python is the V1 core;
- one generated logical pixel equals one SCRUBBOTS gameplay cell;
- logical source art must not be resized/resampled to fit boards;
- cloud image generation and runtime APIs are out of scope;
- `tasks.md` is the canonical task ledger;
- ChatGPT is independent auditor/tracker owner;
- Codex is builder only;
- basic Windows setup/test commands.

Do not duplicate the full task ledger into README.

## 12. Third-party provenance requirements

For each of the four primary references, verify from the upstream repository:

- repository URL,
- license name,
- exact commit SHA or immutable tag checked,
- what concept/module is relevant to SCRUBBOTS,
- whether code is copied in this cycle.

For M00 the expected “code copied” result is **none**.

Do not claim an asset license from a software LICENSE unless separately supported.

If an upstream repository cannot be verified, record it as UNVERIFIED in the Codex log and keep THIRD_PARTY_NOTICES truthful. Do not invent a SHA/license.

## 13. Tests required

At minimum add and run tests proving:

1. package imports successfully;
2. bootstrap package exposes no accidental network initialization;
3. offline/network denial boundary rejects a deliberate network attempt on the protected production path;
4. offline boundary does not break ordinary local deterministic computation;
5. tests do not require the main `Sekiph82/Scrubbots` checkout;
6. project can run from the canonical standalone repo.

Also run:

- full `pytest` suite,
- package/build metadata validation supported by the chosen tooling,
- a clean or fresh-venv install/import/test smoke where practical.

Record exact commands and outputs in the Codex log.

## 14. Security/safety checks

Verify:

- no secrets or credentials are added;
- no `.env` values are committed;
- no telemetry package is introduced;
- no HTTP client is introduced as a core runtime dependency;
- no arbitrary shell execution API is added to Python product code;
- setup/test scripts do not delete user files;
- generated/cache/build outputs are ignored appropriately;
- `reference/audits/` remains unmodified.

## 15. Prohibited shortcuts

Do not:

- mark M00 tasks complete in `tasks.md`;
- start PAG-M01;
- add placeholder generator implementations;
- fabricate third-party provenance;
- copy third-party sample images;
- add cloud/API generation;
- use interpolation/resizing logic;
- add a GUI;
- add Godot integration;
- add WFC implementation code;
- add MarkovJunior implementation code;
- add sprite-generator implementation code;
- create a fake passing offline test disconnected from production package boundaries;
- delete or rewrite historical audit references;
- hide failing commands after fixing them.

## 16. Exit criteria for the builder run

The builder run may be reported as implementation-complete/pending-audit only if:

- all in-scope M00 repository artifacts exist;
- the standalone package installs/imports;
- required tests pass from the standalone repo;
- offline-boundary test is meaningful;
- third-party provenance is truthful and immutable-reference based;
- no later milestone implementation was started;
- matching Codex log is complete;
- implementation and log are committed;
- commits are pushed to `origin/main`;
- final local HEAD and `origin/main` are verified.

Even then, do not declare M00 PASS/CLOSED.

ChatGPT will independently audit the actual repository, rerun/reproduce tests where possible, inspect source/diff/security/provenance, and decide whether PAG-M00 can close or requires PAG-M00-C002 remediation.
