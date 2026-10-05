# SB-CP02-001-C001 — Audit Criteria

PASS only if:
- a closed, versioned `scrubbots.content.manifest.v1` model/schema exists;
- `schema_version` is exactly integer 1;
- root structure is deterministic and declarative-only;
- pack/level collections have explicit model ownership rather than arbitrary mappings;
- unknown root fields and unsupported schema identity/version fail closed;
- docs + focused tests exist;
- no network/provider/runtime/game mutation is introduced;
- M11/M12 regressions remain green.
