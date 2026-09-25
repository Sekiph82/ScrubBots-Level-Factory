# SB-LF07-008-C001-R03 — Remediation Prompt

Document role: CODEX BUILDER LOG

## Start

- Starting timestamp: 2026-09-25 Europe/Istanbul.
- Scope: SB-LF07-008-C001-R03 actual-route workload matching and unavailable accounting truth.
- Canonical repository verified as `Sekiph82/ScrubBots-Level-Factory`.
- Local mirror: `C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator`.
- Branch: `main`.
- Starting HEAD and `origin/main`: `4e6f5934856bc3800589578c6d77b44db495dc5e`; tracked tree clean before this log; owner-untracked files preserved.
- Frozen SB-LF07-002/003 behavior and tests remain unchanged except compatibility wiring.

## Contracts read before edits

- R03 master/index, original SB-LF07-008 criteria/C001 audit, R01/R02 prompts/logs and strict re-audits.
- `TASKS.md`, `AGENTS.md`, `GOVERNANCE.md`, actual AttemptReport/GenerationRequest/GenerationResult contracts, accepted SB-LFX-017 accounting truth, and retained M03/M04/M05/M06/Palette V3 tests.

## Frozen finding and R03 boundary

- R02 accepted arbitrary caller workload/config digests and a caller-created CostUsageRecord as route evidence.
- R03 must derive matched workload identity from actual route contracts, preserve truthful counters, and report cost/credit accounting as unavailable because no authoritative provider exists.

## Chronological implementation and verification

- Added actual-route workload derivation. Authentic mutation route identity now comes from the `AttemptReport` target digest, runner-derived seed/config digest, target validation-policy identity, and actual `AttemptBudget` digest. Authentic regeneration route identity now comes from the actual `GenerationResult.request`, supplied typed target, and actual budget; caller workload/config digests are rejected when they do not match or are supplied as authority.
- Preserved exact generator ID/version, request digest, seed, dimensions, and request configuration by retaining the accepted `GenerationResult` and deriving the route request identity from its exact request.
- Corrected route counters to count applied, accepted, inconclusive/unavailable, and rejected/error attempts from actual attempt records rather than caller DTOs.
- Enforced accepted SB-LFX-017 truth: no authoritative provider/job accounting producer exists. `TrustedAccountingEvidence.from_cost_usage` rejects caller-created `CostUsageRecord`, regeneration routes reject caller accounting/config evidence, and route comparisons always leave cost/credits as `None`.
- Added matched actual mutation/regeneration route coverage plus forged workload, forged config, forged accounting, and exact request/result requirements.
- First focused run exposed the intended old test’s caller-created accounting path; converted that test to the actual route and explicit unavailable accounting assertion.
- Second focused run exposed use of `TypedChallengeTarget.canonical_dict()` even though the accepted typed target exposes only its authenticated `digest()`; corrected workload derivation to use the target digest.
- Third focused run exposed use of the legacy route comparator instead of the authentic route comparator; corrected the test to call `compare_efficiency_from_authentic_routes`.
- Focused result: `python -m pytest -q -p no:cacheprovider tests/unit/test_sb_lf07_008_efficiency.py` — 9 passed.
- Affected M07 run: 71 tests passed; one retained SB-LF07-010 R02 regression test still exercises the now-forbidden caller-created accounting/config path and is intentionally left for the ordered SB-LF07-010 regression remediation.
- Offline/network boundary: route identity and counters are derived locally from accepted immutable contracts; no runtime network, telemetry, or provider accounting dependency added.
- Dependency/license/security: no dependency or license changes; arbitrary financial evidence is rejected and unavailable cost truth cannot become trusted through a caller DTO.
- Changed files: `src/scrubbots_pixel_factory/m07_services.py`, `src/scrubbots_pixel_factory/mutation_attempts.py`, `src/scrubbots_pixel_factory/mutation_efficiency.py`, `tests/unit/test_sb_lf07_008_efficiency.py`, and this builder log.

## Publication checkpoints

- Implementation commit: `aef37cdef19153360fa1df412e2d00978a75bdc1` (`Remediate SB-LF07-008 actual route efficiency`), pushed to `origin/main`.
- Terminal log-only commit: `2e20cf9dffac048f15e19955ba6ef9e9e750fc73`, pushed successfully.
- Final local HEAD and `origin/main` equality at the task checkpoint: `2e20cf9dffac048f15e19955ba6ef9e9e750fc73`.
