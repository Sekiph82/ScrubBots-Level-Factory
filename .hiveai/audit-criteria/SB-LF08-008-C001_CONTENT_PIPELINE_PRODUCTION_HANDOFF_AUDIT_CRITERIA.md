# SB-LF08-008-C001 — Production-Ready Handoff to Content Pipeline — Strict Audit Criteria

Target: `SB-LF08-008`

## Boundary

M11+ Content Pipeline is not yet implemented. This task creates the immutable Level Factory **handoff envelope**, not Content Pipeline internals, catalog publication or game release.

Do not implement future CP milestones here.

## Eligibility

A candidate is READY_FOR_CONTENT_PIPELINE_HANDOFF only when:
- it is a valid SB-LF08-006 Factory-accepted batch entry;
- latest valid SB-LF08-007 owner review is ACCEPT;
- all referenced final artifact/evidence digests still match immutable bytes;
- batch plan/result and candidate lineage identities are exact;
- no required artifact/evidence is missing or stale.

QA ACCEPT alone is insufficient. Owner ACCEPT alone is insufficient.

## Handoff envelope

Create a closed versioned immutable handoff contract binding at minimum:
- batch plan/result digest;
- lane/class and candidate identity;
- LevelData V1 digest/reference;
- logical-art PNG digest/reference;
- preview digest/reference or explicit absence;
- M08 generation metadata/bundle digest;
- source provenance digest;
- M03 solver evidence digest;
- M04 DifficultyAnalysis/score/lane digest;
- M05 QA report digest;
- M07 mutation provenance digest or NOT_APPLICABLE;
- owner-review record/chain digest;
- handoff schema/version and deterministic handoff digest.

Disposition vocabulary must distinguish READY, NOT_OWNER_ACCEPTED, NOT_FACTORY_ACCEPTED, UNAVAILABLE, ERROR.

## Export boundary

- Materialize only deterministic manifest/reference data and required immutable artifacts.
- Safe portable paths; no absolute workstation paths.
- No direct write into future Content Pipeline state/catalog.
- No mutation of accepted candidate/source/QA/review evidence.
- Rerunning the handoff on identical evidence produces byte-identical output/no meaningless diff.

## Negative tests

Factory reject; owner missing/reject; stale review; cross-candidate artifact; missing LevelData/QA; altered art bytes; wrong lane; batch-result tamper; path traversal; unknown schema; rerun idempotence.

## Required gates

Focused 008 + 006/007 + retained M08/PAG-M09/M05 handoff evidence; full M03–M07; full pytest/compileall/Godot/diff/protected-file gates.

## PASS rule

PASS only when the Level Factory emits a deterministic, complete, immutable, owner-approved handoff package that future Content Pipeline code can consume without trusting UI state or recomputing Factory truth.
