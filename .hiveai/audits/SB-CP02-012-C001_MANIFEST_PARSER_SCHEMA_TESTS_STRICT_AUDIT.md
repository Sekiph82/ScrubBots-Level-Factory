# SB-CP02-012-C001 — Manifest Parser / Schema Tests

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation: `743372bc15c368cb98a6097778859905ea50e34f`

## VERDICT

**CONDITIONAL / REAUDIT_AFTER_CP006_R01**

Own parser implementation is strong and passes its direct criteria:
- bytes-only external boundary;
- strict UTF-8;
- duplicate-key rejection at nested levels;
- NaN/Infinity rejection;
- 1 MiB input limit;
- nesting, collection and string limits;
- root object requirement;
- exact closed V1 root;
- future/unsupported schema rejection;
- nested model validation;
- immutable ContentManifestV1 output;
- canonical serialize/parse/serialize round-trip;
- adversarial corpus for versioning, ownership, references, schedule, history and object-key behavior.

However the criterion requires the corpus to cover CP02-001..011 semantics. It currently does not catch the CP006 mixed-case disabled-level logical-identity inconsistency found by independent audit.

No separate parser product defect is opened.

After CP006-R01:
- add/update the corpus regression for mixed-case logical disabled identity;
- rerun CP012 focused/cumulative/full suite;
- re-audit this child.

`SB-CP02-012 = CONDITIONAL / REAUDIT_AFTER_CP006_R01`
