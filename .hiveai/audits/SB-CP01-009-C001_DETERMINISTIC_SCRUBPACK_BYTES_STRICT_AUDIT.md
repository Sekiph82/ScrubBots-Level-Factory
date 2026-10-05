# SB-CP01-009-C001 — Deterministic .scrubpack Bytes

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation:
- `6f018438ec692003a4770f6b30ae1353852f4721`
- `e55fabe03dea56c092e6768167b8eeb0ba39b5c0`

## VERDICT

**PASS / CLOSED**

ZIP output explicitly normalizes builder-controlled metadata:
- fixed 1980 timestamp;
- ZIP_STORED compression;
- canonical member order;
- ASCII names;
- fixed create/extract version;
- fixed mode/attributes/flags;
- no comments/extras;
- fixed ZIP64 behavior.

Separate-process/separate-directory builds from identical semantic inputs produce identical archive bytes and SHA-256.

Builder evidence:
- focused: 69 passed;
- cumulative: 232 passed;
- full pytest: 1401 passed, 3 skips;
- compileall/diff check PASS.

`SB-CP01-009 = PASS / CLOSED`
