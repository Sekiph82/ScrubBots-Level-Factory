# SB-CP02-012-C001 — Audit Criteria

PASS only if an external bytes-to-model parser enforces strict UTF-8 JSON, duplicate/nonfinite/resource-limit rejection, exact closed V1 schema, unsupported-version rejection and immutable validated output; accepted manifests round-trip canonically; and the regression corpus covers all CP02-001..011 positive and adversarial semantics. M11/M12 behavior must remain green.
