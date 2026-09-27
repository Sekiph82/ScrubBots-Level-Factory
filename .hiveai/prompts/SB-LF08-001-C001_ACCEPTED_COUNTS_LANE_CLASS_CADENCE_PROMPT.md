# SB-LF08-001-C001 — Implementation Prompt

Implement requested **Factory-accepted** counts by M04 lane/class cadence on top of the accepted PAG-M09 deterministic batch/resume foundation.

Read first:
- dedicated strict criteria for this task;
- PAG-M09 C003 strict audit;
- M03/M04/M05/M07 accepted contracts;
- current root TASKS.md.

Required implementation:
- create a versioned production-batch plan/service with deterministic ordered lane cadence and requested accepted count per lane;
- finite lane/overall budgets and deterministic seeds;
- reuse/factor existing PAG-M09 batch/resume mechanisms rather than duplicate them;
- count a candidate only when authentic M03 evidence, authentic M04 lane assignment, and M05 MachineReadableQAReport ACCEPT all bind to the exact candidate;
- if M07 mutation is used, require its accepted revalidation/provenance;
- keep generated/attempted, rejected, duplicate, unavailable/inconclusive and Factory-accepted counts separate;
- resume from exact plan digest without regenerating accepted work;
- do not implement owner review/publishing yet.

Do not infer lane from request labels, dimensions or color count. Do not weaken acceptance to meet quotas.

Create dedicated tests for multi-lane deterministic cadence, wrong-lane rejection, unavailable evidence, duplicate prevention, plan tamper and resume.

Do not edit TASKS.md or ChatGPT audits.
