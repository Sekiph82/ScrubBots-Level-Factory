# PAG-M00-C002 — Repository Bootstrap & Governance

Document role: CODEX IMPLEMENTATION PROMPT

Status: AUTHORITATIVE / READY_FOR_IMPLEMENTATION  
Builder: Codex  
Independent auditor / tracker owner: ChatGPT  
Canonical repository: `https://github.com/Sekiph82/ScrubBots-Level-Factory`  
Canonical branch: `main`

Previous independent audit:
`https://github.com/Sekiph82/ScrubBots-Level-Factory/blob/main/.hiveai/audits/RECOVERY-R001_REVERT_MISTAKEN_SCRUBBOTS_LOCAL_EDITS_STRICT_AUDIT.md`

Superseded cycle:
`PAG-M00-C001` was aborted before implementation because the initial handoff allowed wrong local-repository discovery. Do not use that cycle.

## 1. GitHub authority rule

The GitHub repository above is the sole task, prompt, audit, and implementation authority.

Do not discover the active project or task by searching local folders.

Do not substitute the sibling main-game repository:

`C:\Users\sekip\Desktop\ScrubBots`

That repository is OFF-LIMITS for this cycle.

## 2. Local mirror synchronization

If this run executes on the owner's Windows machine, the local Level Factory mirror is:

`C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

Before implementation:

1. verify that this folder is a checkout of `https://github.com/Sekiph82/ScrubBots-Level-Factory`;
2. fetch `origin main`;
3. inspect `HEAD...origin/main`;
4. fast-forward only if safe;
5. do not reset, rebase, clean, force-push, or discard local changes;
6. if the folder is not the correct repository, STOP instead of searching sibling folders.

The local folder is only a synchronized worktree mirror. It is not task authority.

## 3. Mandatory reads

Read from the authorized Level Factory repository:

- `AGENTS.md`
- `GOVERNANCE.md`
- `tasks.md`
- `.hiveai/PROJECT_DASHBOARD.md`
- `.hiveai/HANDOFF.md`
- `.hiveai/CYCLE_INDEX.md`
- `reference/audits/README.md`
- `reference/audits/scrubbots/coordination/AUDIT_POLICY.md`
- `reference/audits/scrubbots/coordination/sessions/META-C005/CHATGPT_AUDIT_V01.md`
- the previous recovery audit linked above
- this prompt

## 4. Objective

Implement **PAG-M00 — Repository Bootstrap & Governance** only.

Do not begin PAG-M01.

Do not implement:

- palette/difficulty contracts,
- MASK generation,
- RULES generation,
- WFC,
- HYBRID routing,
- PNG/JSON generation,
- gameplay logic,
- Godot integration,
- GUI/editor functionality,
- cloud/API generation.

## 5. Builder log

Create before product implementation:

`.hiveai/codex-logs/PAG-M00-C002_REPOSITORY_BOOTSTRAP_AND_GOVERNANCE_CODEX_LOG.md`

Exact H1:

`# PAG-M00-C002 — Repository Bootstrap & Governance`

Immediately below:

`Document role: CODEX BUILDER LOG`

The log must be chronological and immutable after submission. Record:

- timestamp;
- GitHub authority URL;
- local mirror synchronization evidence if applicable;
- branch, starting HEAD, origin and ahead/behind;
- starting status;
- files/contracts read;
- implementation decisions;
- materially relevant commands;
- all failures and corrections;
- dependency choices;
- third-party provenance verification;
- tests added;
- focused/full test results;
- offline-boundary checks;
- files changed;
- commit SHA(s);
- push result;
- final local HEAD and `origin/main` equality.

Do not record secrets.

## 6. Codex role boundary

Codex is builder only.

Do not:

- author an audit;
- declare final PASS/CLOSED;
- edit task checkbox/state in `tasks.md`;
- edit `.hiveai/HANDOFF.md`;
- edit `.hiveai/CYCLE_INDEX.md`;
- create/edit `.hiveai/audits/**`;
- rewrite this prompt after implementation begins;
- rewrite historical prompt/log/audit records.

ChatGPT alone closes tasks and tracker state after independent audit.

## 7. In-scope M00 tasks

### PAG-S00.1 — Project bootstrap

Implement:

- PAG-0001 Python package structure under `src/scrubbots_pixel_factory/`.
- PAG-0002 `pyproject.toml` with deliberate Python baseline and explicit dependencies.
- PAG-0003 Windows-friendly local setup command.
- PAG-0004 local test command.
- PAG-0005 `.gitignore` for venv, caches, generated PNG/JSON, logs, build/coverage output, temporary WFC caches.
- PAG-0006 `output/.gitkeep` while ignoring generated output.
- PAG-0007 root `README.md` describing Pixel Art Generator V1 scope.
- PAG-0008 explicit OFFLINE_ONLY policy.
- PAG-0009 rule forbidding runtime HTTP/API use in core generation.
- PAG-0010 meaningful test that fails if a protected production generation path attempts network access.

### PAG-S00.2 — Third-party provenance

Implement:

- PAG-0011 `THIRD_PARTY_NOTICES.md`.
- PAG-0012 verify and record `ikarth/wfc_2019f` URL, license, immutable commit/tag.
- PAG-0013 verify and record `mxgmn/WaveFunctionCollapse` URL, license, immutable commit/tag.
- PAG-0014 verify and record `mxgmn/MarkovJunior` URL, license, immutable commit/tag.
- PAG-0015 verify and record `zfedoran/pixel-sprite-generator` URL, license, immutable commit/tag.
- PAG-0016 preserve MIT notice requirements for future copied/substantially adapted code.
- PAG-0017 copy no third-party artwork/assets in M00.
- PAG-0018 establish provenance-comment convention for future substantial adaptations.
- PAG-0019 document algorithm-reference vs copied/adapted-code status.

Prepare evidence for, but do not close:

- PAG-0020 clean checkout installs locally.
- PAG-0021 tests run without main ScrubBots repo.
- PAG-0022 package imports without network access.

## 8. Required minimal structure

Create at minimum:

```text
README.md
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

Narrow support files are allowed, for example:

- `scripts/setup.ps1`
- `scripts/test.ps1`
- `tests/conftest.py`
- `tests/unit/test_import.py`
- `tests/integration/test_offline_boundary.py`

Do not create later generator modules merely as placeholders.

## 9. Python baseline

Prefer Python 3.12 for V1.

Keep M00 dependencies minimal.

Do not add WFC/Markov/sprite-generator packages as runtime dependencies yet.

Do not vendor third-party algorithm implementations in M00.

## 10. Offline boundary

M00 must establish a reusable, production-connected network-denial boundary for future generator execution.

The test must prove that a deliberate network attempt through the protected production path fails.

Do not create a test-only fake disconnected from production package code.

Do not add a remote client merely to disable it.

Ordinary dependency installation during setup is allowed; runtime generation must remain offline.

## 11. README requirements

State clearly:

- standalone SCRUBBOTS Pixel Art Generator V1;
- not the complete Level Factory;
- offline/local tooling;
- Python V1 core;
- one logical pixel = one gameplay cell;
- no resize/resample/interpolation to fit boards;
- no cloud image generation/runtime API dependency;
- `tasks.md` is canonical task ledger;
- ChatGPT = independent auditor/tracker owner;
- Codex = builder only;
- Windows setup/test commands.

Do not duplicate the entire task ledger.

## 12. Third-party provenance

For each primary reference record:

- repository URL;
- license;
- exact immutable commit SHA/tag verified;
- relevant algorithmic role;
- whether code was copied.

Expected M00 copied-code status: **none**.

Do not infer asset licensing from software licensing.

If upstream truth cannot be verified, record it honestly as UNVERIFIED rather than inventing provenance.

## 13. Required tests

At minimum prove:

1. package imports;
2. import performs no accidental network initialization;
3. deliberate network attempt through the protected production path is denied;
4. ordinary local deterministic computation still works;
5. tests do not depend on the main ScrubBots checkout;
6. standalone repository operation works.

Also run:

- full `pytest`;
- package/build metadata validation supported by selected tooling;
- clean/fresh environment install-import-test smoke where practical.

Record exact commands/results in the Codex log.

## 14. Safety

Verify:

- no secrets;
- no committed `.env`;
- no telemetry package;
- no core HTTP client dependency;
- no arbitrary shell-execution product API;
- setup/test scripts do not delete user data;
- generated/cache/build outputs are ignored;
- `reference/audits/` remains unchanged;
- `C:\Users\sekip\Desktop\ScrubBots` remains untouched.

## 15. Prohibited shortcuts

Do not:

- mark M00 tasks complete;
- start M01;
- fabricate placeholder generators;
- fabricate provenance;
- copy third-party example art;
- add cloud/API generation;
- add resize/interpolation logic;
- add GUI/Godot integration;
- add WFC/Markov/sprite implementation code;
- create a fake offline test disconnected from production boundaries;
- rewrite historical evidence;
- hide failures after fixing them.

## 16. Builder exit

The run may end as **implementation complete / pending independent audit** only when:

- all in-scope M00 artifacts exist;
- standalone package installs/imports;
- required tests pass;
- offline-boundary test is meaningful;
- provenance is truthful;
- no later milestone work started;
- matching Codex log is complete;
- implementation/log are committed and pushed to `origin/main`;
- final HEAD equals remote `main`.

Do not declare M00 PASS/CLOSED.

ChatGPT will independently inspect source, diff, tests, security, provenance and tracker truth and will decide whether M00 closes or a remediation cycle is required.
