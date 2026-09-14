# LF / CP Requirement Mapping V01

This is the cross-repository migration ledger for the 224 canonical SCRUBBOTS Level Factory + Content Pipeline source requirements. It is evidence/reference only. Root `TASKS.md` remains the live state authority.

Status vocabulary: `VERIFIED`, `PARTIAL`, `MIGRATION`, `NEW`, `GAME_RUNTIME`.

## Level Factory, 112 requirements

### LF00 -> Unified M00
- VERIFIED: `SB-LF00-003`, `004`, `005`
- PARTIAL: `SB-LF00-006`
- MIGRATION: `SB-LF00-001`, `002`, `007`, `008`

### LF01 -> Unified M01
- VERIFIED: `SB-LF01-001`, `002`, `003`, `004`, `006`, `007`, `008`
- PARTIAL: `SB-LF01-009`
- MIGRATION: `SB-LF01-005`, `010`

### LF02 -> Unified M02
- VERIFIED: `SB-LF02-005`, `006`, `007`, `011`, `012`
- PARTIAL: `SB-LF02-001`, `004`, `008`
- NEW: `SB-LF02-002`, `003`, `009`, `010`

### LF03 -> Unified M03
- NEW: `SB-LF03-001..012`
- Note: existing WFC solver is constraint-generation infrastructure, not the SCRUBBOTS gameplay solver.

### LF04 -> Unified M04
- PARTIAL: `SB-LF04-001`, `010`, `012`
- NEW: `SB-LF04-002..009`, `011`

### LF05 -> Unified M05
- VERIFIED: `SB-LF05-006`, `009`
- PARTIAL: `SB-LF05-001`, `002`, `003`, `007`, `008`
- NEW: `SB-LF05-004`, `005`, `010`
- Note: `SB-LF05-009` became VERIFIED after accepted PAG-SP06-C001/C002 recognizability/evidence-gate closure.

### LF06 -> Unified M06
- VERIFIED: `SB-LF06-009`
- PARTIAL: `SB-LF06-002`, `003`, `008`, `010`, `011`, `012`
- MIGRATION: `SB-LF06-001`
- NEW: `SB-LF06-004`, `005`, `006`, `007`
- Studio migration source: Windows ScrubBots Level Factory v1.3.6.

### LF07 -> Unified M07
- NEW: `SB-LF07-001..010`

### LF08 -> Unified M08
- VERIFIED: `SB-LF08-002`, `003`, `004`, `005`, `010`
- PARTIAL: `SB-LF08-001`, `006`, `007`, `009`
- NEW: `SB-LF08-008`

### LF09 -> Unified M09
- VERIFIED: `SB-LF09-005`, `006`, `008`
- PARTIAL: `SB-LF09-002`, `003`, `007`
- NEW: `SB-LF09-001`, `004`
- Active mapping: `PAG-SP07-C001-R01 -> SB-LF09-003`.

### LF10 -> Unified M10
- NEW: `SB-LF10-001..008`

## Content Pipeline, 112 requirements

### CP00 -> Unified M11
- PARTIAL: `SB-CP00-002`, `003`, `006`, `008`
- MIGRATION: `SB-CP00-001`, `009`
- NEW: `SB-CP00-004`, `005`, `007`, `010`

### CP01 -> Unified M12
- PARTIAL: `SB-CP01-002..007`, `009`, `010`
- NEW: `SB-CP01-001`, `008`
- Note: PAG deterministic bundles are foundation/evidence, not a completed `.scrubpack` contract.

### CP02 -> Unified M13
- NEW: `SB-CP02-001..012`

### CP03 -> Unified M14
- PARTIAL: `SB-CP03-002`, `003`
- NEW: `SB-CP03-001`, `004..012`

### CP04 -> Unified M15
- GAME_RUNTIME: `SB-CP04-001..014`
- Implementation repository: `Sekiph82/Scrubbots`.

### CP05 -> Unified M16
- GAME_RUNTIME: `SB-CP05-001..012`
- Implementation repository: `Sekiph82/Scrubbots`.

### CP06 -> Unified M17
- PARTIAL: `SB-CP06-006`, `007`, `009`
- GAME_RUNTIME: `SB-CP06-004`, `010`
- NEW: `SB-CP06-001`, `002`, `003`, `005`, `008`, `011`, `012`

### CP07 -> Unified M18
- PARTIAL: `SB-CP07-003`, `010`
- NEW: `SB-CP07-001`, `002`, `004..009`

### CP08 -> Unified M19
- PARTIAL: `SB-CP08-001`, `003`, `006`, `008`, `010`
- NEW: `SB-CP08-002`, `004`, `005`, `007`, `009`

### CP09 -> Unified M20
- PARTIAL: `SB-CP09-003`, `004`, `008`
- NEW: `SB-CP09-001`, `002`, `005`, `006`, `007`, `009`, `010`

## Count reconciliation

Canonical source-requirement total: 224.

- VERIFIED: 26
- PARTIAL: 53
- MIGRATION: 9
- NEW: 108
- GAME_RUNTIME: 28

`26 + 53 + 9 + 108 + 28 = 224`.

Engineering/migration coverage: `26 + 53 + 9 = 88 / 224 = 39.29%`.

## Unique extension tasks outside the 224

These remain live under unified M09 because their complete capabilities are not represented by the 224 source requirements:

- `PAG-SP11` — ASSET_ART Production
- `PAG-SP12` — Direction / Rotation Variants
- `PAG-SP13` — Animation

`PAG-SP14` remains an integration/closure alias and does not add another denominator task.

## Historical evidence families

- PAG-M00/M01 -> primarily M00/M01
- PAG-M02 -> M01
- PAG-M03..M06 -> M02/M09
- PAG-M07 -> M05
- PAG-M08 -> M05/M08/M12 foundation
- PAG-M09 -> M08/M12 foundation
- PAG-M10 -> M05 technical evidence + negative visual corpus
- PAG-SP01/SP02 -> M02/M09
- PAG-SP03 -> M02/M05
- PAG-SP04 -> M05/M09
- PAG-SP05 -> M02/M05
- PAG-SP06 -> M05
- PAG-SP07 -> M09
- PAG-SP08 -> M09/M06
- PAG-SP09 -> M06
- PAG-SP10 -> M08

Historical acceptance/failure/remediation state is never rewritten merely because the capability is mapped into the unified roadmap.
