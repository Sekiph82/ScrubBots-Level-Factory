# SB-LF08-008-C001 — Implementation Prompt

Implement only the Level Factory boundary envelope for production-ready Content Pipeline handoff. Do not implement future M11+ Content Pipeline internals.

A handoff is READY only when the exact SB-LF08-006 accepted entry has latest valid SB-LF08-007 owner ACCEPT and all referenced immutable artifact/evidence digests still match.

Create a closed versioned deterministic handoff contract binding:
- batch plan/result;
- lane/class/candidate;
- LevelData;
- logical art and preview;
- M08 bundle/generation metadata;
- source provenance;
- M03 solver;
- M04 difficulty/score/lane;
- M05 QA;
- M07 mutation provenance or NOT_APPLICABLE;
- owner review chain/latest accepted record.

Use explicit READY / NOT_OWNER_ACCEPTED / NOT_FACTORY_ACCEPTED / UNAVAILABLE / ERROR dispositions.

Materialize only safe deterministic manifest/reference data and required immutable artifacts. No absolute workstation paths, no direct Content Pipeline catalog writes, no main-game release claim.

Rerun with identical evidence must be byte-identical/no-op.

Do not edit TASKS.md or ChatGPT audits.
