# SB-LF07-001-C001-R01 — Remediation Prompt

Target: `SB-LF07-001`

Authoritative frozen finding:
`.hiveai/audits/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_STRICT_AUDIT.md`

Original strict criteria remain fully authoritative:
`.hiveai/audit-criteria/SB-LF07-001-C001_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_AUDIT_CRITERIA.md`

Do not weaken or reinterpret the original criteria. Close every frozen C001 finding below with minimal forward changes while preserving accepted useful implementation.

Remediate only the frozen findings from the C001 strict audit while retaining useful implementation.

Required corrections:
- Separate the base mutation substrate from later task semantics. The SB-LF07-001 layer must define identities, immutable parent->child mutation request/result contracts, lineage and a registry interface, but must not itself own hardening/easing policy, M03/M04/M05 evidence semantics, targeting, attempt budgeting, efficiency policy or OWNER_UPLOAD policy.
- Remove the global assumption that one hard-coded Scrubbots SHA is permanently “current”. Introduce a current-main authority resolution/binding seam that can return exact repo/SHA/source-blob/version or truthful UNAVAILABLE.
- Prove the mutation interface works with an empty/no-concrete-operator registry.
- Preserve deterministic request/result/lineage digests and deep parent immutability.
- Do not rewrite history or squash prior commits; remediate forward.

Add tests that fail if future-task semantics leak into the base substrate or if stale current-main identity is silently accepted.

## Required publication protocol
- Read the original strict criteria and C001 strict audit before edits.
- Create `.hiveai/codex-logs/SB-LF07-001-C001-R01_MUTATION_INTERFACE_IMMUTABLE_LINEAGE_CODEX_LOG.md` before product edits.
- Run focused R01 tests plus all earlier/later affected M07 tests and retained relevant M03/M04/M05/M06/Palette V3 gates.
- Run full pytest, compileall, Godot headless checks, git diff --check, and prove TASKS.md unchanged.
- Do not edit root TASKS.md or any ChatGPT audit file.
- Commit implementation separately, then terminal log-only publication separately.
- Do not self-promote PASS/CLOSED.
