# SB-CP02-006-C001 — disabled_levels

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation: `e94f2a7a23dc92e31a53f651aa40fd68b6c2408b`

## VERDICT

**CHANGES_REQUIRED / R01**

Most declarative disabled-level behavior is correct, but one logical-identity inconsistency remains.

## PASS surfaces

Verified:
- `disabled_levels` is declarative metadata only;
- valid path-safe level IDs required;
- deterministic ordering;
- duplicate and casefold-collision rejection;
- no pack/level deletion;
- no .scrubpack byte mutation;
- unknown references are intentionally deferred to CP02-009;
- helper is pure and has no runtime/network/global-state dependency.

## F01 — MAJOR — casefold identity semantics disagree with is_level_disabled()

The manifest treats level identity case-insensitively for collision/reference purposes:
- level IDs are casefold-unique;
- CP02-009 resolves disabled level references using `casefold()`.

But:
`is_level_disabled(manifest, level_id)`
uses exact Python membership:

`return level_id in manifest.disabled_levels`

Therefore this accepted logical state is inconsistent:

- declared level ID: `Level-A`
- disabled_levels: `level-a`

CP02-009 considers the disabled reference valid because both identities casefold to the same logical level, while:
`is_level_disabled(manifest, "Level-A")`
returns False.

That violates the child contract that the pure helper answer whether a declared level is disabled.

## Required remediation

Preserve exact spelling in serialized manifest data.

Make disabled-state lookup follow the same logical identity semantics already used by collision/reference validation.

At minimum:
- compare level IDs using the same casefold rule;
- add mixed-case declared/disabled/query regressions;
- preserve current duplicate/collision behavior;
- preserve unknown-reference deferral to CP02-009;
- do not force all existing level IDs to lowercase;
- do not modify pack bytes or runtime/game behavior.

Rerun CP006, CP009 and CP012 focused/cumulative coverage plus full suite.

## FINAL

`SB-CP02-006 = CHANGES_REQUIRED / R01`
