# SB-CP02-004-C001 — Pack IDs / Locations / Hashes

Document role: CHATGPT INDEPENDENT STRICT AUDIT

Implementation: `61cf4a310b9ac2976322b4dab53cb253ed089ffe`

## VERDICT

**PASS / CLOSED**

Verified pack references bind:
- canonical lowercase pack ID;
- positive pack version;
- provider-neutral relative logical object key;
- lowercase 64-hex archive SHA-256;
- positive exact archive byte length.

Object-key grammar rejects:
- HTTP/HTTPS URLs and host-style paths;
- absolute/drive/UNC paths;
- traversal and percent traversal forms;
- backslashes;
- query/fragment forms;
- credential-like colon/@ forms;
- non-.scrubpack suffixes.

Pack identity is case-safe and no provider/network I/O is introduced.

`SB-CP02-004 = PASS / CLOSED`
