# M13 — Remote Manifest & Content Versioning — Interim Master Audit

Document role: CHATGPT INDEPENDENT MASTER INTERIM AUDIT

## VERDICT

**CONTINUATION_REQUIRED / M13 REMAINS OPEN**

Current child state:
- SB-CP02-001: PASS / CLOSED
- SB-CP02-002..012: NOT STARTED

No product defect is opened against child 001.

## Blocker

The M13 master requires an unfiltered full pytest gate before continuing.

During child 001, full pytest reached:
`tests/integration/test_release_batch_level_catalog.py`

That test implements implicit authority discovery:

`SCRUBBOTS_PROJECT` if configured, otherwise `Path.home() / "Desktop" / "ScrubBots"`.

On the owner's machine this silently treats a separate Desktop Scrubbots checkout as an available capability and launches Godot against an archive derived from it.

The M13 task did not authorize implicit access to that owner checkout.

The batch correctly stopped rather than silently consuming the unrelated working repository.

## Harness finding H01

**MAJOR / CONTINUATION BLOCKER**

Historical integration capability must be explicit, not inferred from a user's Desktop.

Required:
- no automatic `~/Desktop/ScrubBots` / `~/Desktop/Scrubbots` discovery;
- use `SCRUBBOTS_PROJECT` only when explicitly supplied for that run, or skip truthfully when absent;
- an explicitly supplied checkout must be verified as `Sekiph82/Scrubbots` and treated read-only;
- test mutation must remain confined to its extracted TEMP archive;
- full pytest for M13 must not touch owner Desktop game checkout unless the prompt explicitly authorizes it.

## Harness finding H02

**MAJOR / BATCH-DURABILITY**

Child 001 modified the historical CP010 source guard to whitelist only:
- `content_pipeline/src/scrubbots_content_pipeline/__init__.py`;
- `content_pipeline/src/scrubbots_content_pipeline/manifest_v1.py`.

That exact changed-path whitelist will become stale as CP02-002..012 legitimately add Content Platform source files.

The security intent must remain, but the guard should validate behavior/architecture rather than force per-child source-path whitelist maintenance.

Required:
- keep root tracker protection;
- keep package-wide forbidden network/provider/runtime import checks;
- make those checks recursive across the Content Pipeline Python package;
- do not require every future declarative M13 source file to be manually added to a historical exact-path allowlist.

## Continuation

A single M13 continuation is authorized to:
1. repair H01/H02 test-harness behavior;
2. complete an unfiltered safe full pytest gate;
3. resume the existing M13 master at SB-CP02-002;
4. execute SB-CP02-002..012 continuously under their already-published prompts/criteria;
5. keep SB-CP02-001 closed.

M13 is not eligible for milestone closure until all remaining 11 children receive independent audits.
