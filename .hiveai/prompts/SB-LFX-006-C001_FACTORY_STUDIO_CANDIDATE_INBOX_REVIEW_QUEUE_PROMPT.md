# SB-LFX-006-C001 — Factory Studio Candidate Inbox + Owner Review Queue

Builder log:
`.hiveai/codex-logs/SB-LFX-006-C001_CANDIDATE_INBOX_REVIEW_QUEUE_CODEX_LOG.md`

Create log first. Work only on LFX-006.

Read criteria, product spec, current candidate/bundle/pipeline contracts from committed LFX-005 and earlier code.

Build:
1. a derived Candidate Inbox over real canonical candidate artifacts only;
2. append-only owner-review evidence bound to exact candidate/artwork identity;
3. Review Queue derived from latest valid review evidence.

Provide ACCEPT and REJECT with reason/note. A second decision creates a new review record and preserves prior history.

Never equate QA with owner acceptance. Never mutate source/candidate bytes. Unsupported origins or missing solver/difficulty remain NOT AVAILABLE.

Real Godot integration must create/obtain real candidates, review them, prove history and identity binding, reload queue, corrupt review evidence and fail closed, and prove underlying bytes unchanged.

Do not implement comparison/LFX-007+, promotion or Content Platform. Do not edit TASKS.

Commit/push implementation, then exactly one task-final builder-log-only commit; continue only under the batch master.
