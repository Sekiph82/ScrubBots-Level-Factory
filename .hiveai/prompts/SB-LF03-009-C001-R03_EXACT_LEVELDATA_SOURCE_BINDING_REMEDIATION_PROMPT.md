# SB-LF03-009-C001-R03 — Exact LevelData Source Binding Remediation

Document role: CODEX REMEDIATION PROMPT

Target:
`SB-LF03-009 — Reuse canonical reachability/routing semantics rather than importing another game's rules.`

R02 re-audit:
`.hiveai/audits/SB-LF03-009-C001-R02_VERIFIED_REAL_CANONICAL_INVOKE_REMEDIATION_STRICT_REAUDIT.md`

Create first:
`.hiveai/codex-logs/SB-LF03-009-C001-R03_EXACT_LEVELDATA_SOURCE_BINDING_REMEDIATION_CODEX_LOG.md`

Do not edit `TASKS.md`.

## Retain accepted R02 behavior

Preserve:
- real canonical Godot execution from an independent clean exact-SHA checkout;
- pinned committed external runner path + SHA-256;
- runner outside canonical checkout;
- verified Godot executable;
- canonical legal_moves / apply_placement / solve operations;
- deterministic repeat;
- checkout immutability;
- no Python gameplay clone.

## Finding to close

Current bridge only proves:

`payload["level_data_source_sha256"] == request.level_data_source_sha256`

It does not recompute that SHA from the actual LevelData source used to create gameplay state.

A caller can therefore change width/height/palette/cells while keeping the same claimed hash in both places.

## Canonical Level Data V1 source contract

Do not invent a second serialization.

Use the exact canonical Level Data V1 source format from:
`Sekiph82/Scrubbots/docs/03_LEVEL_DATA_SPEC.md`

Required source JSON fields:
- version
- id
- name
- difficulty
- width
- height
- palette
- cells

The gameplay `LevelData` object must be reconstructed from the **same exact source bytes whose SHA-256 is verified**.

## Required request design

Preferred pattern:

1. Request payload carries exact immutable Level Data V1 source bytes, e.g. bounded base64-encoded UTF-8 JSON bytes.
2. `CanonicalBridgeRequest` or a dedicated request validator:
   - decodes those exact bytes;
   - computes SHA-256;
   - requires equality with `level_data_source_sha256`;
   - validates bounded size and valid UTF-8/JSON shape;
   - fails closed before invoking Godot on mismatch.
3. The external Godot runner independently recomputes the SHA-256 from those exact decoded bytes using Godot hashing facilities and compares it with the verified request field.
4. The runner parses the same bytes into Level Data V1 fields and constructs canonical `LevelData` from them.
5. Do not keep a second independently editable `level` dictionary whose content can diverge from the hashed source bytes.

Supply/solver configuration may remain separate declarative request data because it is not Level Data source identity.

## Field fidelity

Use canonical V1 field `name`, not an invented source field `display_name`.

The runner may pass the parsed `name` value to the constructor parameter/instance member named `display_name`; source schema still remains canonical V1.

## Tamper tests

Real integration must prove:
- exact valid source bytes => AVAILABLE;
- change one cell but retain old hash => fail closed;
- change width/palette/name but retain old hash => fail closed;
- change source bytes and update the correct hash => valid only if Level Data is structurally valid;
- malformed UTF-8/JSON => fail closed;
- unsupported version => fail closed;
- source field type/shape mismatch => fail closed;
- canonical checkout remains clean/immutable.

Run real legal_moves, apply_placement and solve using the newly source-bound request.

## No architecture drift

Do not:
- hash a reserialized object if the contract claims original source-byte identity;
- create a Factory-only gameplay LevelData schema;
- derive gameplay semantics in Python;
- weaken exact authority/source verification.

Run focused 009 + 012 bridge regressions, retained LF03, full pytest, compileall, Godot headless, diff-check, TASKS no-diff.

Publish R03 implementation + finalized task log + terminal log-only commit.
