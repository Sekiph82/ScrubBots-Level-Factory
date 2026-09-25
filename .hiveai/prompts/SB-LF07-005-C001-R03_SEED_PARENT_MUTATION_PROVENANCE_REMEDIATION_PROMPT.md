# SB-LF07-005-C001-R03 — Remediation Prompt

Target: `SB-LF07-005`

Authoritative R02 re-audit:
`.hiveai/audits/SB-LF07-005-C001-R02_SEED_PARENT_MUTATION_PROVENANCE_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Accepted and frozen closed tasks:
- SB-LF07-002 = PASS/CLOSED
- SB-LF07-003 = PASS/CLOSED

Do not modify accepted 002/003 behavior except strictly necessary compatibility wiring, and any such wiring must preserve their tests/authority semantics.

Integrate typed evidence provenance into production.

Required:
- Add an authentic provenance constructor that consumes exact SB-LF07-004 authentic adapters/validation envelope and derives one typed evidence reference per applicable stage.
- Production mutation provenance after validation must require unique M03_SOLVER, M04_DIFFICULTY and M05_QA references with authentic producer digests.
- Stop using anonymous-only evidence_digests as the production path; retain only for historical compatibility if necessary.
- The bounded authentic runner must emit these typed references automatically.
- Add missing-stage, stage-swap, producer-digest drift and replay tests on the actual runner/provenance path.
- Preserve explicit root registration and cycle/missing-parent protections.

## Publication protocol
- Read C001 criteria, C001 audit, R01/R02 prompts/logs/re-audits before edits.
- Create `.hiveai/codex-logs/SB-LF07-005-C001-R03_SEED_PARENT_MUTATION_PROVENANCE_CODEX_LOG.md` before product edits.
- Add adversarial tests that fail R02 behavior.
- Run focused tests plus all affected M07 and retained M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless, git diff --check and TASKS no-diff proof.
- Never edit root TASKS.md or .hiveai/audits/**.
- Do not weaken criteria or self-promote PASS/CLOSED.
- Commit implementation separately, then terminal log-only publication.
