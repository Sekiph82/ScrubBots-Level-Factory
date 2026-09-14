# SCRUBBOTS Cross-Repository Content Contract V01

Status: CANONICAL CROSS-REPO BOUNDARY
Date: 2026-09-14

## Repositories

- Producer/control plane: `Sekiph82/ScrubBots-Level-Factory`
- Consumer/runtime: `Sekiph82/Scrubbots`

## One-way dependency law

The shipping game must never import, preload, package or execute Factory/Publisher source code.

The Factory may consume versioned contract snapshots and golden fixtures derived from the game's declarative schemas and owner-locked rules.

The legal direction is:

```text
Factory/Publisher -> declarative artifacts -> Game Runtime
```

Never:

```text
Game Runtime -> execute Factory code
```

## Canonical compatibility surfaces

The two repositories must converge on explicit versioned contracts for:

1. LevelData schema and row-major cell mapping.
2. Canonical C01..C16 palette identifiers/values.
3. Production used-color envelope and Difficulty V1 metadata.
4. Campaign/level identifiers and ordering metadata.
5. `.scrubpack` container schema.
6. Remote content manifest schema.
7. Hash/integrity rules.
8. Minimum game-version compatibility.
9. Disabled/scheduled content semantics.
10. Runtime content-registry state machine.

## Golden-vector rule

For every cross-repo schema, the platform owns deterministic golden vectors. The game must consume the same vectors in runtime contract tests.

A schema change is not complete until:

- producer serialization validates;
- consumer parsing validates;
- invalid/adversarial fixtures fail closed on both sides;
- backward/forward compatibility behavior is explicit;
- schema/version provenance is recorded.

## Task implementation ownership

The canonical 224-task tracker lives in `ScrubBots-Level-Factory/TASKS.md`.

Task metadata uses one of:

- `FACTORY`: implementation in `ScrubBots-Level-Factory`.
- `GAME_RUNTIME`: implementation in `Scrubbots`.
- `CROSS_REPO`: coordinated changes/tests in both repositories.
- `OWNER_DECISION`: cannot close without an explicit owner decision.

`CP04` and `CP05` are primarily `GAME_RUNTIME` implementation milestones even though program tracking remains in the Content Platform repository.

## Runtime package rules

Remote packages are declarative only and may not contain executable scripts, native code or plugin binaries.

Downloaded content installs only below the game's `user://` content area. It never writes into or replaces `res://` application code/assets at runtime.

## Activation law

The game activates new content only after:

1. manifest compatibility succeeds;
2. all required packs download completely;
3. pack hashes match;
4. pack/schema/level validation succeeds;
5. the previous known-good set remains recoverable.

Failed updates never destroy the last-known-good content set.

## Publication law

The publisher must:

1. validate locally/dry-run;
2. upload immutable/versioned pack objects;
3. verify remote object integrity;
4. publish to STAGING;
5. validate through a real staging download path;
6. explicitly promote to PRODUCTION;
7. emit an auditable report.

## Difficulty and content semantics

Current main-game Difficulty V1 rules outrank stale Factory historical assumptions.

In particular:

- board dimensions do not define difficulty class;
- distinct used-color count does not define difficulty class;
- production logical art normally uses 3..12 canonical colors;
- rectangular boards are supported;
- Challenge, Session Load and Frustration Risk remain separate;
- CampaignBuilder sequences accepted content without changing accepted logical cells.

## Change control

Breaking contract changes require:

- a new schema/model version;
- migration notes;
- cross-repo golden fixtures;
- producer and consumer regression evidence;
- independent audit before production publication.
