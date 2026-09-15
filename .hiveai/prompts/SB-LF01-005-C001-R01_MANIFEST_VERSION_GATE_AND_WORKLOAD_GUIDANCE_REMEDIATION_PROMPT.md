# SB-LF01-005-C001-R01 — Manifest Version Gate & Workload Guidance Remediation
Document role: CODEX IMPLEMENTATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Remediate only the strict-audit findings for:

`SB-LF01-005 — Support width/height selection within current engine/content envelope and workload guidance. [MIGRATION]`

Source audit:

`.hiveai/audits/SB-LF01-005-C001_INDEPENDENT_DIMENSION_ENVELOPE_MIGRATION_STRICT_AUDIT.md`

The central C001 dimension architecture is accepted and must be retained:

- current production request schema v2 uses independent width/height `20..59`;
- rectangles are legal;
- difficulty does not band current dimension legality or automatic selection;
- one canonical `PRODUCTION_DIMENSION_ENVELOPE` remains the legality source;
- request schema v1 retains historical difficulty-band dimension semantics only for explicitly versioned historical replay;
- current automatic width/height use separate deterministic domains;
- historical v1 bundle/batch compatibility remains supported.

Do not redesign or reopen those accepted decisions.

Do not begin `SB-LF06-002`, any `SB-LFX-*` task, Dashboard, Import, Library, solver, provider, Content Platform, or main-game work.

## Required reads before edits

Read completely from GitHub:

1. root `TASKS.md`;
2. this R01 prompt;
3. `.hiveai/audits/SB-LF01-005-C001_INDEPENDENT_DIMENSION_ENVELOPE_MIGRATION_STRICT_AUDIT.md`;
4. original C001 prompt and finalized builder log;
5. `src/scrubbots_pixel_factory/cli/main.py` batch manifest parsing/resume paths;
6. `src/scrubbots_pixel_factory/contracts/dimensions.py`;
7. `src/scrubbots_pixel_factory/contracts/difficulty.py`;
8. `src/scrubbots_pixel_factory/contracts/production.py`;
9. relevant C001 focused tests and M09 CLI integration tests;
10. current user-facing/core documentation or CLI help surfaces where advisory dimension workload guidance fits without creating a second policy.

Before implementation create and verify:

`.hiveai/codex-logs/SB-LF01-005-C001-R01_MANIFEST_VERSION_GATE_AND_WORKLOAD_GUIDANCE_REMEDIATION_CODEX_LOG.md`

Do not edit root `TASKS.md`.
Do not rewrite the original C001 builder log.

## F-SB-LF01-005-MAJOR-001 — Strict batch manifest version typing

Current manifest validation uses membership against supported integer versions without first enforcing exact integer type. In Python, `True == 1`, so malformed JSON `"version": true` can be interpreted as legacy manifest version 1.

Repair the version gate so:

- manifest `version` must be exact `int` type;
- booleans are rejected;
- only integer `1` and current integer `2` are accepted;
- valid v1 manifests retain byte/replay compatibility;
- valid v2 manifests retain current independent-dimension behavior;
- no malformed version value can silently select a compatibility branch.

Add explicit automated cases for at least:

- `true` -> reject;
- `false` -> reject;
- `1.0` -> reject;
- `"1"` -> reject;
- `null` -> reject;
- unsupported integer such as `3` or `99` -> reject;
- valid integer `1` -> legacy path remains accepted/replayable;
- valid integer `2` -> current path remains accepted/replayable.

Use fail-closed errors without traceback leakage through normal CLI usage.

Do not change the meaning or bytes of valid historical v1 request templates merely to implement stricter typing.

## F-SB-LF01-005-MINOR-002 — Implement non-binding workload guidance

Complete the task's explicit workload-guidance requirement without creating a new legality or difficulty policy.

Add concise user/developer-facing guidance in an appropriate existing or narrowly scoped documentation/help surface. It must state all of the following truthfully:

- production width and height are independently legal from `20..59` inclusive;
- every rectangle inside that envelope remains legal regardless of difficulty label;
- larger board area may require more processing/resources than smaller board area;
- workload guidance is advisory only;
- workload guidance never changes legality;
- workload guidance is not difficulty and must not be used to infer or assign difficulty.

Do **not** invent timing, RAM, CPU, cell-per-second, threshold, tier, or benchmark numbers that are not measured and accepted.

Do **not** create EASY/MEDIUM/HARD workload size bands, hidden size tiers, or any replacement mapping from difficulty to dimensions.

Prefer documentation/help text over a speculative workload-scoring API.

Add a narrow test/assertion that protects the guidance's key separation from difficulty and points to the canonical production envelope rather than duplicating a second numeric truth where practical.

## F-SB-LF01-005-MINOR-003 — Truthful R01 publication discipline

The original C001 log incorrectly made an equality record that required another commit to publish it.

For R01:

- keep log entries chronological;
- clearly distinguish implementation commit, pushed equality checkpoint, and final log publication;
- do not claim a commit is terminal if another builder commit is planned;
- do not attempt to embed a self-referential final SHA into the same commit;
- at handoff provide the actual implementation SHA and actual final publication SHA after push;
- if the final log cannot contain its own SHA, say so truthfully and let the handoff carry the actual final publication SHA.

No need to rewrite C001 history.

## Required regression

Run and record at minimum:

1. focused strict manifest-version tests including boolean/float/string/null/unsupported integer;
2. historical valid v1 bundle reproduce;
3. historical valid v1 batch resume/replay;
4. current valid v2 batch create/resume/replay;
5. C001 dimension-envelope focused suite;
6. affected request/difficulty/core/router tests;
7. full `python -m pytest -q`;
8. `python -m compileall -q src tests`;
9. package import smoke;
10. CLI/module help smoke;
11. representative explicit rectangle current generation/reproduce;
12. representative current omitted-axis deterministic generation;
13. `git diff --check`;
14. changed-file review proving no root `TASKS.md`, Factory Studio feature, provider, Content Platform, solver, or main-game change.

Record all failed commands and corrections truthfully.

## Allowed scope

Allowed only as required by the audit:

- `src/scrubbots_pixel_factory/cli/main.py` for strict manifest version typing if that remains the appropriate boundary;
- tests directly proving the corrected batch version gate;
- narrow existing/new documentation or CLI help text for advisory workload guidance;
- narrow test guarding the guidance contract;
- matching R01 builder log.

Do not modify core dimension semantics unless a direct remediation blocker proves it necessary. Any such blocker must be recorded rather than silently broadening scope.

## Acceptance criteria

PASS eligibility requires all of the following:

- [ ] manifest version accepts only exact integer 1 or 2;
- [ ] bool/float/string/null/unsupported versions fail closed;
- [ ] historical valid v1 request/batch replay remains intact;
- [ ] current v2 dimension behavior remains independent `20..59`;
- [ ] workload guidance exists and is explicitly advisory;
- [ ] workload guidance never changes legality and is not difficulty;
- [ ] no unmeasured performance thresholds or new size bands are invented;
- [ ] all accepted C001 dimension/schema architecture remains unchanged;
- [ ] root `TASKS.md` unchanged;
- [ ] no Studio/LFX/provider/solver/Content Platform/main-game work;
- [ ] focused and full regression pass;
- [ ] R01 builder log is published truthfully;
- [ ] builder stops for independent ChatGPT strict audit.

## GitHub handoff

Push remediation/tests/guidance/finalized R01 builder log to `main`.

At completion give the user only:

1. full GitHub URL of the finalized R01 builder log;
2. remediation implementation commit SHA;
3. actual final publication commit SHA.

Then stop for independent ChatGPT strict audit.
