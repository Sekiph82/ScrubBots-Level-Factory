# SB-LFX-018-C001-R02 — Final Owner UI Closure — Audit Criteria

## Retain

Retain all R01 accepted architecture:

- exact eight owner destinations;
- current simple shell;
- read-only canonical owner projection;
- canonical mutation delegation;
- direct review ACCEPT/REJECT;
- 3/4/5 solve control;
- compact footer/title;
- contextual legacy tools;
- no shadow truth.

## A. HOME visual production list

When canonical items exist, HOME must show:

- imported / solved / needs-attention / reviewed / accepted counts;
- compact progress;
- multiple visual item cards/rows;
- thumbnail where an artwork/source preview exists;
- identity/status;
- Continue Batch.

No contradiction between summary, cards and next action.

## B. BATCH visual operation

Show:

- progress/counts;
- multiple per-item rows/cards;
- thumbnail when available;
- item identity/status;
- Retry eligible failures;
- Resume/Recover;
- Continue Batch/Pipeline.

No fake success.

## C. LIBRARY visual catalog

Show:

- search;
- filter;
- canonical result rows/cards;
- thumbnail when available;
- identity/type/status;
- open/details route.

History/Revisions/Reproduce remain contextual.

## D. PUBLISH direct safe controls

On the simple PUBLISH page expose separately:

- Campaign Order / accepted selection;
- Preflight;
- Publish to STAGING;
- Production Approval.

Require visible state for:

- accepted levels/order;
- current content version when authoritative;
- preflight;
- staging;
- production approval;
- receipt/status where present.

STAGING and Production Approval must remain distinct.

Production Approval must be disabled/blocked until the canonical required evidence exists.

Do not treat Route A PR approval as remote-content Production Approval.

All real publication/promotion mutations delegate to trusted existing Python/content-pipeline authority.

No R2 credentials in GDScript/UI state/logs.

## E. SETTINGS

Show compact:

- provider state;
- durable runtime/project path or resolved path status;
- local core/runtime status;
- cost/credits when known;
- recovery;
- diagnostics.

Unknown stays unknown.

## F. Coherent visual fixture

The durable eight-page evidence fixture must drive one coherent presentation state per page.

A fixture page must not say SOLVED/4 columns in one region and Not run/3 columns in another.

Require consistency across:

- state cards;
- selected controls;
- item lists;
- preview;
- next-step message;
- button enablement;
- fixture label.

Fixture remains display-only and must never persist owner review, release or production truth.

## G. Current-game authority for VOID regression

Use exact canonical `Sekiph82/Scrubbots main`.

The regression checkout must have enough Git history to prove the already-audited VOID commit ancestry.

Accepted methods include:

- non-shallow clone; or
- explicit deepen/fetch sufficient to make `git merge-base --is-ancestor 7d0d148b... HEAD` authoritative.

Do not weaken `void_capability.py` solely because a shallow clone lacks the ancestor object.

Prove:

- authority clean;
- HEAD == origin/main;
- canonical origin;
- audited VOID ancestor present;
- `FORMAT_VERSION_VOID == 2`;
- `VOID_CELL == -1`.

## H. Regression

After final R02 implementation:

- focused R02 owner UI tests PASS;
- all seven `test_sb_lfx_019_void_game_parity.py` cases PASS against history-complete exact-current game authority;
- exact Route A authentic verifier PASS;
- Factory Studio runtime suite PASS;
- durable launcher/runtime smoke PASS;
- Godot parse/import PASS;
- complete repository pytest PASS with zero failures;
- compileall PASS;
- diff check PASS;
- secret scan PASS.

No skip/xfail/assertion weakening to hide failures.

## I. Governance/publication

Builder must not edit root `TASKS.md` or `.hiveai/audits/**`.

Implementation/test commit first.

Evidence/log commit separately.

Normal fast-forward push only.

Final clean 0/0 parity.

## Outcome

If A-I pass:

`TECHNICAL PASS / OWNER VISUAL REVIEW`

ChatGPT then inspects the final screenshots.

Only owner visual acceptance closes:

`PASS / CLOSED`

and opens M17.
