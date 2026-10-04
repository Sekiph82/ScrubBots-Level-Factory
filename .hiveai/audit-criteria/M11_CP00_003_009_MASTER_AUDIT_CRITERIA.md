# M11 Master - SB-CP00-003..009 - Audit Wrapper

This file is a milestone wrapper only. It does not replace any child audit criteria.

## Master PASS rule

M11 remaining batch may close only after ChatGPT independently audits every child below against its own criteria and every child is PASS/CLOSED:

1. SB-CP00-003-C001
2. SB-CP00-004-C001
3. SB-CP00-005-C001
4. SB-CP00-006-C001
5. SB-CP00-007-C001
6. SB-CP00-008-C001
7. SB-CP00-009-C001

## Required audit behavior

ChatGPT must:
- fetch live GitHub implementation/log evidence;
- audit each child independently;
- publish one strict audit file per child;
- never accept Codex self-claims without repository verification;
- if any child is CHANGES_REQUIRED, create a focused remediation prompt/criteria for that child and keep M11 open;
- do not open the next milestone until every child audit is PASS/CLOSED.

## Master evidence

Require:
- seven distinct child logs;
- implementation/log commit separation per child;
- no Codex edit to root TASKS.md;
- no Codex edit to audit files;
- master synchronization evidence;
- final main parity 0/0;
- no live provider/network/runtime mutation during M11.

The master wrapper is not a second tracker. Root `TASKS.md` remains sole lifecycle authority.