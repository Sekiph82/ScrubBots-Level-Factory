# SB-LF07-001-C001-R03 — Remediation Prompt

Target: `SB-LF07-001`

Authoritative R02 re-audit:
`.hiveai/audits/SB-LF07-001-C001-R02_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Accepted and frozen closed tasks:
- SB-LF07-002 = PASS/CLOSED
- SB-LF07-003 = PASS/CLOSED

Do not modify accepted 002/003 behavior except strictly necessary compatibility wiring, and any such wiring must preserve their tests/authority semantics.

Close the remaining R02 architecture finding.

Required:
- Make the base substrate physically real: move the actual implementations of authority identity/resolution, candidate/request/result/lineage identities, registry and engine into mutation_base.py or another true lower-level substrate module.
- Higher-level services may import the base. The base must not import m07_services or any higher M07 service.
- Convert m07_services into a compatibility/re-export layer over lower-level modules, not the implementation owner.
- Remove duplicate base implementations from m07_services.
- Keep all canonical digest behavior stable or provide deterministic migration tests proving equivalent identity.
- Base tests must run with no imports of evidence/targeting/attempt/efficiency/source modules.

## Publication protocol
- Read C001 criteria, C001 audit, R01/R02 prompts/logs/re-audits before edits.
- Create `.hiveai/codex-logs/SB-LF07-001-C001-R03_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail R02 behavior.
- Run focused tests plus all affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and TASKS no-diff proof.
- Never edit root TASKS.md or .hiveai/audits/**.
- Do not weaken criteria or self-promote PASS/CLOSED.
- Commit implementation separately, then terminal log-only publication.
