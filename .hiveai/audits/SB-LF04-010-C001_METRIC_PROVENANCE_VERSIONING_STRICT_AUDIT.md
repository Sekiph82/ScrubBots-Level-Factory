# SB-LF04-010-C001 — Metric Provenance / Versioning — Strict Audit

Document role: INDEPENDENT CHATGPT STRICT AUDIT

## VERDICT

**CHANGES_REQUIRED**

- BLOCKER: 0
- MAJOR: 2
- MINOR: 0

## Audited chain

- implementation: `cca1d5a3cadf065793d0408958da301b4225fe29`
- terminal builder-log commit: `367084bcfa4992e5dba6c1055b83b68f820728e3`
- M04 master builder publication: `a9e63bc272646eccb88bef7672752132f9d3fb0a`
- final builder full suite: `937 passed, 1 capability skip`
- compileall / Godot / diff-check / TASKS no-diff: PASS

Builder logs and green tests were treated as evidence, not acceptance.

## Independent finding

## MAJOR-001 — Missing producer provenance is silently fabricated with generic identities

`build_difficulty_analysis()` auto-fills producer identity for every populated metric when the caller omits it:
- core metrics => `solver-evidence / BOUND_PROVIDER_V1`;
- optional metrics => `canonical-provider / BOUND_PROVIDER_V1`.

That is not the exact producing provider/policy version required by the task. In particular, 004–007 results carry their own provider ids/versions, but those identities are discarded when values are copied into LevelMetrics and later replaced with generic provenance.

The contract says a metric value must not exist without its producing version/source identity.

## MAJOR-002 — The envelope/parser do not enforce a closed exact metric-provenance catalog

`DifficultyAnalysis.__post_init__()` accepts arbitrary string metric names in `metric_provenance` and `component_availability`. `from_dict()` likewise reconstructs arbitrary names.

It does not require provider identity exactly for every AVAILABLE populated component and no provider for unavailable components. Directly constructed envelopes can therefore claim unknown metrics or incomplete provenance.

## Global invariant review

No board-size/color-count difficulty inference, source-art mutation, runtime network/provider-credit use, gameplay-rule clone, or builder TASKS mutation was accepted.

## Final disposition

**CHANGES_REQUIRED / IMPLEMENTATION RETAINED**

## Required remediation

Stop synthesizing generic provenance. Require exact producer identities for every populated metric, with fixed accepted identities for 002/003 and exact provider result identity for any future canonical 004–007 metric. Reject missing/extra provenance. Restrict provenance and availability names to the closed MetricId catalog and enforce consistency between AVAILABLE components and producer identities. Preserve score/lane cross-lineage rejection.
