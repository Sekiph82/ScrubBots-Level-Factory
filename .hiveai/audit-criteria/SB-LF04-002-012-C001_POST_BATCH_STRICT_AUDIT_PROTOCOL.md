# SB-LF04-002..012-C001 — Post-Batch Strict Audit Protocol

Document role: CHATGPT INDEPENDENT AUDIT PROTOCOL

After the complete M04 builder batch and master log are published, ChatGPT independently audits SB-LF04-002 through SB-LF04-012 one by one.

Builder logs and green tests are evidence, not acceptance.

For every task inspect:
- exact prompt/criteria;
- implementation commits/diffs;
- current product code and tests;
- accepted M03 and LF04-001 contracts;
- any canonical ScrubBots gameplay evidence used;
- full-batch regression results;
- root TASKS builder no-diff.

Create one durable audit file per task and one M04 batch summary.

No cascading false closure: a later task is judged on its own semantics and dependency impact.

If any task is CHANGES_REQUIRED:
- close only independent PASS tasks;
- keep earliest failed dependency as sole active tracker task;
- create one remediation prompt per failed task;
- create one remediation index and one master remediation prompt for failed tasks only;
- require separate remediation logs + one master remediation log;
- independently re-audit after the whole remediation batch.

Truth invariants:
- no board-size/color-count difficulty inference;
- no gameplay-rule clone;
- optional canonical metrics remain UNAVAILABLE when semantics are unavailable;
- Challenge Score V1 uses only its fixed required core metrics and coefficients;
- no missing metric becomes zero;
- lane mapping never mutates board/art;
- player-data calibration remains disabled/design-only until policy approval;
- no operational wall-clock data in canonical difficulty identity;
- no source mutation.
