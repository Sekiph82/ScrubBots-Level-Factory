# SB-LF01-005-C001-R01 — Manifest Version Gate & Workload Guidance Remediation
Document role: CHATGPT STRICT AUDIT

Audit date: 2026-09-15
Repository: `Sekiph82/ScrubBots-Level-Factory`
Authoritative prompt: `.hiveai/prompts/SB-LF01-005-C001-R01_MANIFEST_VERSION_GATE_AND_WORKLOAD_GUIDANCE_REMEDIATION_PROMPT.md`
Starting tracker/base commit: `aa957110269ab1449e0922829b1b4bf35c36b434`
Retained C001 implementation commit: `739e100c4a5a188f6aa3d311e87069924c8ef3c8`
R01 remediation implementation commit: `c84f182ac07813dda6095ff6db5ad58dd210627d`
Observed terminal builder publication commit: `9c0aedf2283b0e20aa825897505c2067d1d14b7d`
Builder log: `.hiveai/codex-logs/SB-LF01-005-C001-R01_MANIFEST_VERSION_GATE_AND_WORKLOAD_GUIDANCE_REMEDIATION_CODEX_LOG.md`

## 1. VERDICT

**PASS / CLOSED**

R01 closes all findings from the C001 strict audit without reopening the accepted independent-dimension architecture.

Finding summary:

- BLOCKER: 0
- MAJOR: 0
- MINOR: 0
- NOTE: 1

`SB-LF01-005` is eligible for tracker closure.

## 2. ACCEPTED ARCHITECTURE RETAINED

The accepted C001 migration remains intact:

- current request/dimension schema v2 uses one canonical independent production envelope of width `20..59` and height `20..59`;
- rectangles remain legal;
- current dimension legality and automatic selection are not difficulty-banded;
- historical request schema v1 retains its legacy difficulty-band semantics only for explicitly versioned replay;
- valid historical v1 bundle/batch replay remains supported;
- current automatic width and height resolution remains deterministic and uses separate axis domains.

R01 did not alter the dimension contracts, request schema architecture, generator behavior, Factory Studio product code, provider code, solver code, Content Platform, main-game code, or root tracker.

## 3. FINDING CLOSURE

### F-SB-LF01-005-MAJOR-001 — CLOSED

The batch-manifest version boundary is now fail-closed.

`_validate_manifest()` reads `manifest_version = value.get("version")` and requires:

`type(manifest_version) is int`

before checking membership in the supported integer versions. This prevents JSON booleans from entering the v1 branch despite Python's `True == 1` behavior.

Focused regression coverage explicitly rejects:

- `true`;
- `false`;
- `1.0`;
- `"1"`;
- `null`;
- unsupported integer `3`;
- unsupported integer `99`.

Separate integration evidence preserves valid current v2 create/resume and the pre-existing valid v1 historical replay path.

### F-SB-LF01-005-MINOR-002 — CLOSED

The repository README now contains an explicit `Dimension and workload guidance` section that states:

- production width and height are independently legal in `20..59`;
- every rectangle in the envelope remains legal regardless of difficulty label;
- larger board area may require more processing/resources;
- the guidance is advisory only;
- it never changes legality;
- it is not difficulty and must not be used to infer or assign difficulty.

No invented timing, RAM, CPU, size-tier, difficulty-band, or benchmark thresholds were introduced.

The accompanying regression assertion derives the numeric envelope from `PRODUCTION_DIMENSION_ENVELOPE`, avoiding a second executable dimension policy.

### F-SB-LF01-005-MINOR-003 — CLOSED

Publication discipline is now truthful and non-self-referential.

The builder log distinguishes:

1. implementation commit `c84f182ac07813dda6095ff6db5ad58dd210627d`;
2. pushed implementation equality checkpoint at that same SHA;
3. a planned final log-only publication.

GitHub chronology independently shows the actual terminal builder commit is `9c0aedf2283b0e20aa825897505c2067d1d14b7d` (`Publish R01 remediation builder log`).

The compare from implementation to terminal publication changes only the matching R01 builder log, so the product/test/documentation tree is frozen at `c84f182...`.

## 4. REGRESSION AND SCOPE EVIDENCE

Builder evidence records:

- focused R01/C001 compatibility suite: `56 passed, 1 warning`;
- affected regression suite: `175 passed, 1 warning`;
- full suite: `685 passed, 1 warning`;
- `python -m compileall -q src tests`: PASS;
- package import/router smoke: PASS;
- module CLI and installed CLI help: PASS;
- explicit `23x47` generation and reproduce: PASS / `MATCH`;
- deterministic omitted-axis current generation: same seed resolved identically;
- `git diff --check`: PASS.

The only changed product/test/documentation files between the ChatGPT R01 routing commit and the remediation implementation are:

- `README.md`;
- `src/scrubbots_pixel_factory/cli/main.py`;
- `tests/integration/test_m09_cli_integration.py`;
- `tests/unit/test_sb_lf01_005_dimension_envelope.py`.

The final builder publication adds only the matching builder log. Root `TASKS.md` was not modified by the builder.

## 5. NOTE

The test commands and runtime smokes above are builder-executed evidence. This strict audit independently verified the committed source, tests, commit boundaries, changed-file scope, and publication chronology through GitHub, but did not independently rerun the Windows local test suite.

No defect found in the committed R01 changes that warrants additional remediation.

## 6. CLOSURE DECISION

`SB-LF01-005` is **PASS / CLOSED**.

The temporary M01 dependency detour is complete. The execution frontier may return to M06 Factory Studio at `SB-LF06-002 — Target difficulty/dimensions/seed/mode/candidate controls`.

The next Studio cycle must preserve the canonical-Core rule: presentation controls may collect operator intent, but must not create a second compiler, second dimension policy, second difficulty policy, or false successful Core state when the canonical Core boundary is unavailable.
