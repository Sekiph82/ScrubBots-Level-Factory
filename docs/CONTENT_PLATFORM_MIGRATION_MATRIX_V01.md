# SCRUBBOTS Content Platform Migration Matrix V01

Status: CANONICAL MIGRATION LEDGER
Date: 2026-09-14

## Purpose

This document maps the 224 Level Factory + Content Pipeline tasks originally planned in `Sekiph82/Scrubbots` into their new canonical program home: `Sekiph82/ScrubBots-Level-Factory`.

The task IDs do not change. Existing historical evidence is preserved. Migration does not itself close a task.

## Status vocabulary

- `MIGRATED_OPEN`: canonical task now lives in this repository but remains open.
- `EVIDENCE_CANDIDATE`: existing PAG/SP code/audit evidence may satisfy some or all of the task after strict mapping audit.
- `REQUIRES_CONVERGENCE`: existing implementation conflicts with newer main-game contracts and must be migrated before credit.
- `NEW_WORK`: no sufficient implementation exists yet.
- `GAME_RUNTIME`: tracked here, implemented primarily in `Sekiph82/Scrubbots`.
- `CROSS_REPO`: requires coordinated producer/consumer evidence.

## Program-level mapping

| Task range | Canonical implementation owner | Migration state | Existing foundation |
|---|---|---|---|
| SB-LF00-* | FACTORY | EVIDENCE_CANDIDATE | standalone repo, Python package, governance, tests, offline core |
| SB-LF01-* | FACTORY | EVIDENCE_CANDIDATE / CONVERGENCE | deterministic requests, RNG, reproduce, batch provenance |
| SB-LF02-* | FACTORY | EVIDENCE_CANDIDATE / CONVERGENCE | MASK/RULES/WFC/HYBRID/AUTO + semantic provider layer |
| SB-LF03-* | FACTORY/CROSS_REPO | NEW_WORK | no canonical gameplay-equivalent solver closure yet |
| SB-LF04-* | FACTORY | NEW_WORK / CONVERGENCE | structural metrics exist; Difficulty V1 intelligence not complete |
| SB-LF05-* | FACTORY/CROSS_REPO | EVIDENCE_CANDIDATE / CONVERGENCE | deterministic export/quality/provenance strong; solvability missing |
| SB-LF06-* | FACTORY | EVIDENCE_CANDIDATE / CONVERGENCE | owner-supplied Windows Studio is operator-UI candidate |
| SB-LF07-* | FACTORY | NEW_WORK | no audited safe difficulty-targeting mutation engine |
| SB-LF08-* | FACTORY | EVIDENCE_CANDIDATE | CLI batch/resume/review foundation already substantial |
| SB-LF09-* | FACTORY | EVIDENCE_CANDIDATE | WFC/semantic research/provider qualification exists |
| SB-LF10-* | FACTORY | NEW_WORK | CampaignBuilder not implemented |
| SB-CP00-* | FACTORY/CROSS_REPO | MIGRATED_OPEN | architecture/governance begins with consolidation V01 |
| SB-CP01-* | FACTORY | NEW_WORK with export foundation | deterministic bundle machinery can be reused but `.scrubpack` is new |
| SB-CP02-* | FACTORY/CROSS_REPO | NEW_WORK | versioned remote manifest not yet canonical |
| SB-CP03-* | FACTORY | NEW_WORK | publisher/staging/promotion control plane not yet built |
| SB-CP04-* | GAME_RUNTIME | MIGRATED_OPEN | implement in `Sekiph82/Scrubbots` when runtime integration opens |
| SB-CP05-* | GAME_RUNTIME | MIGRATED_OPEN | implement in `Sekiph82/Scrubbots` |
| SB-CP06-* | FACTORY + GAME_RUNTIME | NEW_WORK | control-plane operations + runtime behavior |
| SB-CP07-* | FACTORY | NEW_WORK / OWNER_DECISION | storage/CDN provider selection required |
| SB-CP08-* | FACTORY | NEW_WORK | operational reporting/health/DR not implemented |
| SB-CP09-* | CROSS_REPO / OWNER_DECISION | MIGRATED_OPEN | release-time policy/security gate |

## Existing PAG/SP evidence mapping

Historical accepted work is retained as migration evidence:

### PAG M00-M02
Candidate evidence for:

- `SB-LF00-*` repository/bootstrap/testing boundaries;
- `SB-LF01-001..004`, `SB-LF01-008..009` deterministic config/seed/provenance concepts.

### PAG M03-M06
Candidate evidence for:

- `SB-LF02-005..006`, `SB-LF02-011..012` procedural/topology/provenance/testing;
- `SB-LF09-003`, `SB-LF09-006..007` experimental procedural-generation research.

### PAG M07
Candidate evidence for:

- portions of `SB-LF05-006..009` structural/quality/readability reporting;
- `SB-LF08-003` rejection statistics foundation.

The M10 owner rejection of 100/100 generated artworks remains binding negative evidence: structural acceptance is not semantic acceptance.

### PAG M08
Candidate evidence for:

- `SB-LF05-002..003`, `SB-LF05-007..008` deterministic output/round-trip/provenance;
- portions of `SB-LF08-006` batch output artifacts;
- reusable machinery for future `SB-CP01-*` packaging, but not completion of `.scrubpack` itself.

### PAG M09-M10
Candidate evidence for:

- `SB-LF08-002..005`, `SB-LF08-009..010` CLI batch/reproduce/resume/acceptance evidence;
- Factory performance/property testing patterns.

### PAG-SP00-SP04
Candidate evidence for:

- `SB-LF02-004`, `SB-LF02-008`, `SB-LF02-011..012` semantic ART_FIRST/provider/provenance paths;
- `SB-LF05-008..009` source preservation + semantic quality boundary;
- `SB-LF09-003`, `SB-LF09-006..008` semantic-provider research.

## Mandatory convergence before migration credit

The following legacy assumptions are superseded and must not receive canonical task credit until corrected:

1. Difficulty class derived from board dimensions.
2. Difficulty class derived from fixed color-count bands.
3. Any LEVEL_ART pipeline that treats `AREA_AVERAGE_V1` as canonical logical-cell reduction.
4. Any square-only assumption.
5. Any compiler that fabricates additional used colors merely to satisfy old class bands.
6. Any duplicate compiler inside the Windows Studio that can diverge from canonical Factory Core.

Current authority is the main-game Difficulty V1 contract plus owner-locked CELL_MAJORITY semantic reduction direction.

## Runtime-task migration rule

`CP04` and `CP05` remain in this 224-task ledger because they are required to complete the end-to-end Content Platform, but their implementation occurs in `Sekiph82/Scrubbots`.

Closing one of these tasks requires evidence from both repositories:

- Factory schema/golden fixture/published artifact truth;
- Game runtime implementation and tests consuming the same truth.

## Factory Studio migration

Owner-supplied `ScrubBots Level Factory v1.3.6` is treated as an evidence/source candidate for LF06/LF08 and provider-operation tasks.

Retain/migrate only source and useful operator assets. Do not import:

- virtual environments;
- PyInstaller build trees;
- generated EXEs/installers as source authority;
- caches;
- local secrets/tokens.

Studio compiler/validator logic must be progressively replaced by calls into canonical Factory Core.

## First migration audit order

1. LF00 repository/platform bootstrap evidence.
2. LF01 deterministic generation evidence.
3. Difficulty V1 contract convergence.
4. Semantic CELL_MAJORITY compiler convergence.
5. Studio source extraction and core-adapter boundary.
6. LF02/LF05/LF08 existing-evidence mapping.
7. Solver/difficulty/campaign new work.
8. CP00-CP03 packaging/publisher foundation.
9. CP04-CP05 game-runtime integration.
10. CP06-CP09 operations/release hardening.
