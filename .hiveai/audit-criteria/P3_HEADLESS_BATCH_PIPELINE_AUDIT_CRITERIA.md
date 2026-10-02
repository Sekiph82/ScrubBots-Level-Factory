# PROMPT P3 — Headless, resumable batch processing of imported art (unattended runs)

Document role: CHATGPT AUDIT CRITERIA

Authoritative owner prompt:
`.hiveai/prompts/P3_HEADLESS_BATCH_PIPELINE.md`

Exact owner prompt SHA-256:
`c310b033152ddc079d3261f12cc07d4036e5c4e921371e1bd930d8749fe8042f`

## Scope

Audit only the behavior required by the authoritative owner prompt.

Do not require:
- a second compiler;
- a simplified headless-only pipeline;
- owner ACCEPT;
- automatic publish;
- network/cloud behavior;
- concurrency greater than the bounded default.

## PASS criteria

### A. Exact Studio parity

The CLI headless path must invoke the SAME canonical orchestration/stages/gates used by Factory Studio for imported OWNER_UPLOAD sources.

Required canonical chain:

`Import → Normalize → Validate → Candidate → ZIP supply/solve/Difficulty V1 → QA → Review`

No duplicated or simplified compiler/solver/difficulty implementation is accepted.

For the same source identity + job settings:
- Studio and CLI must produce identical canonical source/candidate/pipeline/review-queue records;
- identities/digests must match;
- READY/REJECTED disposition and reason must match.

### B. CLI contract

Required commands:

`scrubbots-pixel pipeline run --job <producer_job.json>`

`scrubbots-pixel pipeline status --job <producer_job.json>`

The producer job manifest is read-only.

It binds the imported sources by source ID/SHA-256 and carries the requested per-source job metadata described by the owner prompt.

CLI results must be written only to existing canonical Level Factory stores/evidence locations.

### C. Review boundary

Headless processing stops at the owner Review Queue.

It must never:
- create owner ACCEPT evidence;
- create owner REJECT evidence on behalf of the owner;
- trigger automatic publication;
- mutate the configured Scrubbots game project as a consequence of the unattended run.

READY candidates must appear in Studio's Review Queue exactly as equivalent Studio-created candidates do.

### D. Durable resumability

Resume semantics must honor the accepted SB-LFX-015 durable-resume contract.

Per source:
- completed stage evidence is durable;
- completed stages are not rerun on restart;
- an interrupted stage is the only stage rerun for that source;
- no duplicate source/candidate/pipeline identity is created;
- a repeated resume/re-run is idempotent;
- evidence never falsely claims RESUMED unless canonical work actually advances.

### E. Interruption coverage

Focused tests interrupt at every canonical stage boundary and prove:
- restart reads durable state;
- prior completed stages are reused;
- interrupted stage re-executes exactly once;
- subsequent stages execute normally;
- final canonical records equal uninterrupted execution.

### F. Job-level resumability

For a multi-source producer job:
- one source failure/interruption must not corrupt completed source records;
- restart resumes from per-source durable state;
- completed sources are skipped without mutation;
- remaining sources continue deterministically.

### G. Bounded concurrency

Default concurrency is exactly 1.

If any optional concurrency control exists:
- it must remain bounded;
- default stays 1;
- no test may require parallel solver execution.

### H. Machine-readable progress

Run emits machine-readable progress records sufficient to identify:
- job;
- source/CSV row identity;
- current stage;
- stage disposition;
- READY / REJECTED / FAILED terminal state;
- rejection/failure reason where applicable.

Final summary reports:
- READY;
- REJECTED with preserved reasons;
- FAILED.

`pipeline status` reads durable job/source state without rerunning canonical work.

### I. Rejection truth

Canonical validation/QA rejection reasons are preserved byte-for-byte or semantically identical through:
- durable records;
- status output;
- final summary;
- Studio Review Queue / candidate surfaces where applicable.

The CLI must not convert a canonical rejection into generic FAILED when the canonical system has a specific rejection disposition.

### J. Offline invariant

The new CLI/orchestrator adds no network dependency.

Core processing remains offline:
- no runtime HTTP;
- no cloud API;
- no telemetry requirement;
- no API key requirement.

The external producer is outside this core execution boundary.

### K. Idempotency

Running the same completed job again:
- creates no duplicate immutable OWNER_UPLOAD source;
- creates no duplicate canonical candidate;
- creates no duplicate successful stage evidence;
- creates no duplicate Review Queue item;
- returns the same canonical terminal identities/dispositions.

### L. Regression

Required builder evidence:
- focused P3 parity tests;
- every-stage interruption/resume tests;
- idempotent rerun tests;
- rejection-reason preservation tests;
- offline/network-boundary tests;
- relevant SB-LFX-005 pipeline tests;
- relevant SB-LFX-015 recovery tests;
- owner-upload tests;
- full pytest green except truthful environment capability skips;
- compileall PASS;
- Factory Studio headless/runtime contract PASS;
- git diff --check PASS.

## Governance

Builder must:
- follow root GOVERNANCE.md / AGENTS.md / CLAUDE.md;
- create `.hiveai/codex-logs/P3_HEADLESS_BATCH_PIPELINE_CODEX_LOG.md` before product edits;
- not edit root `TASKS.md`;
- not edit `.hiveai/audits/**`;
- preserve the authoritative owner prompt unchanged;
- stop for independent ChatGPT audit after push.
