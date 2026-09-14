# SCRUBBOTS Content Production Platform Architecture V01

Status: CANONICAL PROGRAM ARCHITECTURE
Date: 2026-09-14

## Mission

`ScrubBots-Level-Factory` is the development-time content production and publishing platform for the SCRUBBOTS mobile game.

It is not part of the shipping gameplay runtime. It produces, validates, sequences, packages and publishes declarative content consumed by `Sekiph82/Scrubbots`.

## System map

```text
TEXT / OWNER ART / REFERENCE / SEMANTIC PROVIDER
                    |
                    v
             ART INTELLIGENCE
                    |
                    v
     CANONICAL LOGICAL ART COMPILER
      CELL_MAJORITY / C01..C16 / provenance
                    |
                    v
            PUZZLE INTELLIGENCE
         simulation / solver / metrics
                    |
                    v
   Challenge / Session Load / Frustration
                    |
                    v
          FACTORY QA + OWNER REVIEW
                    |
                    v
             CAMPAIGN BUILDER
                    |
                    v
             ACCEPTED LEVELDATA
                    |
                    v
             .scrubpack PACKAGER
                    |
                    v
           VERSIONED REMOTE MANIFEST
                    |
                    v
        STAGING -> VERIFY -> PRODUCTION
                    |
                    v
               STORAGE / CDN
                    |
                    v
        SCRUBBOTS GODOT CLIENT RUNTIME
```

## Platform domains

### 1. Art Intelligence

Responsibilities:

- provider-neutral semantic requests;
- Magnific / PixelLab and future provider adapters;
- raw-source identity and provenance;
- deterministic normalization;
- CELL_MAJORITY for high-resolution LEVEL_ART reduction;
- palette snapping to canonical C01..C16;
- semantic/readability review;
- owner-original source preservation.

Historical MASK/RULES/WFC/HYBRID/AUTO systems remain usable as control, mutation, topology, procedural or experimental layers. They do not become owner-visible semantic truth merely because they are deterministic.

### 2. Puzzle Intelligence

Responsibilities:

- pure/headless simulation;
- canonical legal-move semantics;
- deterministic solver/search;
- UNSOLVABLE vs INCONCLUSIVE distinction;
- solution/dead-end/branching/dependency evidence;
- exact reproduction of solver failures by level/config/version.

The platform must reuse or contract-test against canonical gameplay reachability, target and routing laws. It must not silently invent a second game.

### 3. Difficulty Intelligence

Difficulty V1 is the authority.

The platform measures at least:

- Challenge Score;
- Session Load;
- Frustration Risk;
- novelty/similarity;
- challenge-vector diversity.

Board dimensions and distinct color count are inputs, not difficulty-class identity.

### 4. Campaign Intelligence

CampaignBuilder:

- consumes accepted immutable levels;
- follows the owner-locked repeating ten-level cadence;
- targets campaign-age-adjusted challenge windows;
- validates recovery/tension waves;
- avoids repetitive challenge vectors and visual similarity;
- records deterministic sequencing provenance;
- never rewrites accepted logical level cells.

### 5. Factory Studio

The Studio is a human/operator interface over canonical core services.

It may provide:

- provider/model selection;
- prompt/reference configuration;
- candidate generation;
- batch/resume;
- visual preview;
- solve/analyze/validate/reproduce;
- QA/review disposition;
- campaign preview;
- publish controls where authorized.

The Studio is never a second compiler. Core truth lives in reusable platform modules.

### 6. Content Packaging

`.scrubpack` is the versioned declarative content container.

A pack contains only approved data/artifacts such as:

- LevelData;
- previews/metadata where contract-authorized;
- campaign/content metadata;
- hashes and provenance.

It must never contain executable game code.

### 7. Publishing Control Plane

Responsibilities:

- pack validation;
- manifest construction;
- staging publication;
- remote integrity verification;
- explicit promotion to production;
- immutable/versioned object naming where practical;
- rollback;
- level disable;
- scheduled activation;
- publish reports;
- operational audit history.

Production publication never silently overwrites live truth.

## Cross-repo boundary

### Factory repository writes

`Sekiph82/ScrubBots-Level-Factory` implements development-time generation, packaging and publishing.

### Game repository writes

`Sekiph82/Scrubbots` implements shipping-runtime content consumption:

- `RemoteContentManager`;
- HTTPS manifest/pack download;
- SHA/integrity checks;
- `user://` registry/cache;
- atomic activation;
- last-known-good fallback;
- offline behavior;
- LevelCatalog integration.

These runtime tasks remain visible in this platform's 224-task tracker so the end-to-end content system has one program ledger, but each task declares the correct implementation repository.

## Contract packages

The platform will converge on versioned schemas under `schemas/` for:

- LevelData compatibility;
- Factory QA report;
- Campaign manifest;
- `.scrubpack`;
- remote content manifest;
- runtime content registry test vectors.

Cross-repo contract tests must use the same golden vectors in both repositories.

## Security boundary

Remote content is declarative only.

Forbidden in remote packages/manifests:

- GDScript or arbitrary script text intended for execution;
- native libraries;
- executable plugins;
- dynamic expression/eval payloads;
- publishing credentials;
- API secrets.

Publishing credentials live only in operator/publisher environments and follow least privilege.

## Program completion reporting

Always report separately:

- Game/client tracker completion;
- Content Platform completion out of 224;
- Combined SCRUBBOTS program completion.

Tracker migration alone does not create completion credit.
