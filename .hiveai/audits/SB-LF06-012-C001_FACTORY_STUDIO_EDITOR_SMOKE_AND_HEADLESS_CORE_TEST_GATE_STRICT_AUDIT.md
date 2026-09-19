# SB-LF06-012-C001 — Factory Studio Editor Smoke + Headless Core Test Gate — Strict Audit

Document role: CHATGPT INDEPENDENT STRICT AUDIT

## VERDICT

**PASS / CLOSED**

Severity:
- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 1

Target requirement:
`SB-LF06-012 — Editor smoke + headless core tests. [PARTIAL]`

## Audited publication chain

- Starting authoritative tracker HEAD: `6eeb61238c3beb29d95499efee424771fad2b2fe`
- Builder implementation: `79ad82b484804ca3a439a031f578a1064cd71d92`
- Terminal builder publication: `d71585e26219e328cdb850d950e2764be1adf791`
- Terminal publication is exactly one builder-log-only commit.

## Acceptance findings

### 1. Real headless Studio smoke — PASS

The focused LF06-012 gate invokes the committed real Godot suite:

`godot --headless --path level_factory --script res://tests/factory_studio_runtime_suite.gd`

It requires:
- exit code 0;
- stable committed PASS marker;
- no Parse Error;
- no SCRIPT ERROR;
- no missing-file error.

The reused runtime suite already covers real scene instantiation, navigation/workspace, Generate surface, target controls, independent dimensions and accepted Studio runtime contracts. No duplicate giant scenario was introduced.

### 2. Direct canonical Python Core smoke — PASS

The same focused test invokes the committed `factory_core_launcher.py` directly with no PYTHONPATH override and runs real canonical:
- Generate;
- MEDIUM;
- RULES;
- 20x21 rectangular dimensions;
- explicit integer seed 12012;
- bounded temporary output.

It then reads the generated canonical bundle, verifies the recorded request contract and typed seed, invokes real canonical Reproduce from the generated `metadata.json`, and requires successful MATCH.

### 3. Canonical identity / byte-level reproduce — PASS

The focused gate independently compares:
- `metadata_json`;
- `artwork_json`;
- `artwork_png`;
- preview bytes;
- complete generated/reproduced relative file set;
- every corresponding file byte-for-byte.

This is real canonical Generate/Reproduce authority, not a fabricated test stub.

### 4. Bounded cleanup / offline boundary — PASS

The Core smoke uses a unique OS temporary directory and removes it in `finally`, then asserts that the temporary root no longer exists.

The committed gate and runtime sources add no HTTP/provider/API-key/credential requirement. The builder also reports final `level_factory/output/` contains only tracked `.gitkeep`.

### 5. Verification documentation — PASS

`level_factory/README.md` no longer falsely describes Godot tests as future work. It now truthfully documents:
- committed Godot-local smoke/integration tests;
- canonical root Python Core authority;
- exact focused LF06-012 pytest command;
- headless Godot project boot command;
- full Python regression command;
- GUI/provider/network/credential-free smoke boundary.

No competing tracker or acceptance ledger was introduced.

### 6. Scope / governance — PASS

Implementation changes are exactly:
- LF06-012 builder log;
- `level_factory/README.md`;
- focused LF06-012 Python acceptance gate.

No root `TASKS.md`, canonical Core semantics, Studio product behavior, provider/network/dependency, M03/M04/M05, SB-LFX, Content Platform or main-game implementation changed.

## Builder verification evidence

Builder reports:
- focused LF06-012: **3 passed, 1 warning**;
- retained LF00/LF06 rerun: **94 passed, 1 warning**;
- full pytest: **734 passed, 1 warning**;
- direct committed Godot Studio runtime: exit 0 / PASS marker / no stderr;
- direct Godot project boot: exit 0 / empty stderr;
- compileall: PASS;
- `git diff --check`: PASS;
- `git diff -- TASKS.md`: empty.

The builder transparently recorded and corrected two test-harness assertion issues, an invalid PowerShell wildcard invocation, and generated `__pycache__` interference. None represented a product semantic defect.

These test counts are builder-reported. The independent audit inspected the committed focused test, README, exact implementation diff and terminal publication topology.

## NOTE

The focused Core smoke uses an explicit test candidate ID. This is appropriate for the direct canonical CLI smoke and does not alter the accepted Studio candidate-presentation identity boundary.

## Closure

`SB-LF06-012` is accepted as **PASS / CLOSED**.

All canonical `SB-LF06-001..012` Factory Studio requirements are now closed. The next M06 work is the separately counted owner-approved `SB-LFX` extension surface and must not be treated as part of the fixed 224-source denominator.
