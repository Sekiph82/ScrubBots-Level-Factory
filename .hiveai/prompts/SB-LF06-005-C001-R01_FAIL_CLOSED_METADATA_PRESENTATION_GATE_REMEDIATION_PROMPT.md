# SB-LF06-005-C001-R01 — Fail-Closed Metadata Presentation Gate Remediation

Document role: CODEX REMEDIATION PROMPT

Repository: https://github.com/Sekiph82/ScrubBots-Level-Factory
Branch: `main`
Canonical local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`

## Mission

Work only on `SB-LF06-005-C001-R01`.

Read first:
- root `TASKS.md`;
- `.hiveai/audits/SB-LF06-005-C001_FACTORY_STUDIO_CANONICAL_EVIDENCE_METRICS_PANEL_STRICT_AUDIT.md`;
- original LF06-005 prompt;
- current evidence panel, integration tests, `bundle.py`, and `core/request.py`.

Create the matching R01 builder log before product edits.

Retain the accepted LF06-005 architecture. Fix only the presentation reader's missing fail-closed checks.

## Required fixes

1. Before panel `READY`, require candidate identity agreement between:
   - successful action `candidate_id`;
   - root `metadata.candidate_id`;
   - `metadata.artwork.candidate_id`.

2. Before panel `READY`, require `generation.request.schema` and `generation.request.schema_version` to match canonical Python request contracts:
   - `GENERATION_REQUEST_SCHEMA`;
   - `SUPPORTED_GENERATION_REQUEST_SCHEMA_VERSIONS`.
   Add a narrow Python cross-language test proving any Studio literals/version list exactly match those Python constants. Do not silently coerce malformed version types.

3. Type-check consumed presentation fields before type-specific operations. At minimum, `quality.rejection_codes` must be an array/list-compatible value before duplication/use. Invalid consumed-field types must produce panel `ERROR`, not a Godot runtime error.

4. Preserve previous successful evidence when a newer successful action points to unsupported/mismatched/unreadable evidence. Keep action result, preview state and evidence-panel state separate.

Do not duplicate the full Python bundle validator and do not recompute quality in GDScript.

## Required real integration evidence

Using real Generate/Reproduce output as the base test fixture, prove:
- valid Generate still reaches `READY`;
- root metadata candidate mismatch yields `ERROR`;
- unsupported request schema yields `ERROR`;
- unsupported request version yields `ERROR`;
- wrong request-version type is rejected;
- wrong `quality.rejection_codes` type yields `ERROR` without aborting the Godot suite;
- previous successful evidence remains retained/stale after each attempted invalid newer evidence;
- restored canonical metadata allows real Reproduce MATCH to reach `READY` from its own metadata source;
- accepted crisp preview/action behavior remains green;
- test outputs are restored/cleaned.

## Preserve locked semantics

- Structural QA comes only from canonical metadata.
- Request difficulty is target/request context only.
- Solution remains unavailable pending M03.
- Difficulty analysis remains unavailable pending M04.
- Load/risk remains unavailable without canonical models.
- `Structural QA ACCEPT != OWNER ACCEPT` remains explicit.
- No provider/network dependency or second persistent evidence store.

## Forbidden scope

Do not modify canonical Python Core semantics.
Do not implement solver, Difficulty V1, load/risk scoring, editing, Dashboard, Import, Library, providers, Content Platform or main-game work.
Do not start `SB-LF06-006+`.
Do not modify root `TASKS.md`.

## Verification

Run focused R01/LF06-005 tests, retained LF06-001..004 and LF01 regressions, canonical output/bundle/quality tests, real Godot integration, full pytest, compileall, Godot headless boot and `git diff --check`. Record failures/corrections truthfully.

## Publication

Use implementation commit(s), push/equality checkpoint, then exactly one final log-only publication commit. At completion give only:
1. finalized R01 builder-log GitHub URL;
2. final remediation implementation SHA;
3. actual terminal publication SHA.

Then stop for independent ChatGPT strict audit.
