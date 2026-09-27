# SB-LF08-006-C001 — Implementation Prompt

Build the immutable accepted batch-result artifact contract on top of SB-LF08-001 and accepted M03/M04/M05/M08/PAG-M09 components.

For each Factory-accepted candidate, bind exact:
- batch plan/lane/attempt/candidate identity;
- final LevelData V1 bytes/digest;
- canonical logical-art PNG / M08 bundle identity;
- preview digest or explicit absence;
- generation request/result/metadata digests;
- source provenance;
- M03 solver evidence;
- M04 DifficultyAnalysis/Challenge Score/lane;
- M05 MachineReadableQAReport canonical bytes/digest;
- M07 mutation provenance when applicable.

Create a deterministic versioned batch-result manifest with per-lane requested/attempted/accepted/statistics and accepted-entry digests in stable order.

Reuse canonical artifact bytes. Do not create a second solver/QA/compiler or silently re-encode accepted artifacts.

Fail closed on missing/stale/cross-lineage artifacts and unsafe paths.

Do not implement owner review or Content Pipeline handoff yet. Do not edit TASKS.md or ChatGPT audits.
