# SB-LF05-001-C001 — Strict Audit

**VERDICT: CHANGES_REQUIRED / PRODUCT IMPLEMENTATION RETAINED**

Accepted: stage model, current rectangular/envelope truth, no Python validator clone, truthful capability absence.

Blocker: exact LevelData payload is not carried to the main-game provider. Mapping hash and id/width/height can disagree; provider receives no exact LevelData bytes to run current LevelValidator/ProductionLevelValidator, and receipts are not bound to that exact digest/source.

R01: carry exact immutable LevelData bytes/mapping; derive its fields from payload; bind structural/production receipts to LevelData digest/source and exact main-game SHA/provider/version; add malformed/version/TEST/unknown/rectangular/M04-mismatch/capability/drift tests.
