# SB-LF07-008-C001-R07 — Remediation Prompt

Target: `SB-LF07-008`

Authoritative R06 re-audit:
`.hiveai/audits/SB-LF07-008-C001-R06_MUTATE_VS_REGENERATE_EFFICIENCY_STRICT_REAUDIT.md`

Original C001 strict criteria remain authoritative.

Frozen PASS/CLOSED:
SB-LF07-001,002,003,004,005,006,007,009

## Final provenance closure

Replace self-asserted parent payload generation digests with sealed producer-derived generation provenance.

Required:
- Introduce a typed/sealed parent generation provenance object or adapter derived from an actual accepted `GenerationResult` and its exact `GenerationRequest`.
- The binding must include at minimum:
  - exact GenerationRequest digest;
  - exact GenerationResult digest;
  - generator id/version/mode;
  - exact seed/config identity;
  - exact parent candidate identity it is bound to.
- The construction path must derive these values internally from the accepted GenerationResult. Caller-provided raw digest strings cannot establish authenticity.
- Mutation workload availability/MATCHED must require this sealed binding.
- Raw parent payload keys such as `generation_request_digest` or nested `generation_provenance` may be retained only as historical/untrusted metadata and must not establish AVAILABLE/MATCHED.
- Missing sealed provenance => workload UNAVAILABLE.
- Seed/config mismatch against the sealed binding => ERROR/UNAVAILABLE, never MATCHED.
- Use the existing accepted generator route only. Do not invent a generator.
- Preserve truthful regeneration validation, solver workload and accounting availability semantics.

Tests:
- actual GenerationResult -> sealed parent provenance -> aligned mutation/regeneration => MATCHED;
- forged raw 64-hex parent payload digest without sealed provenance => UNAVAILABLE/non-MATCHED;
- sealed binding for another parent => reject;
- tampered request/result digest => reject;
- seed A vs B and same-seed config mismatch remain rejected.

Run full affected M07 and repository gates. Do not edit TASKS.md or ChatGPT audits. Do not self-promote PASS/CLOSED.
