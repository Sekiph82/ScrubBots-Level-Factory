# SB-LF08-009-C001 — Implementation Prompt

Add deterministic offline stress coverage and any minimal production hardening needed for high-rejection M08 batch operation.

Cover:
- 100% reject to finite exhaustion;
- mostly reject then late acceptance;
- duplicates;
- unavailable/inconclusive M03/M04/M05;
- one lane exhausts while another completes;
- interruption/resume after long rejection history;
- rerun COMPLETE/EXHAUSTED;
- source preservation where applicable.

Required invariants:
- finite explicit budgets;
- no retry recursion/unbounded loops;
- no threshold/range/QA relaxation to satisfy quotas;
- rejected/unavailable/duplicate candidates never increment Factory accepted count;
- statistics reconcile exactly with history;
- accepted IDs/artifacts unique;
- resume deterministic and no redoing accepted work;
- terminal states truthful;
- no provider/network spend in tests;
- no wall-clock/resource telemetry in canonical truth.

Reuse PAG-M09 corruption/resume semantics and M08 001/006/007/008 contracts. Do not create a new batch engine.

Do not edit TASKS.md or ChatGPT audits.
