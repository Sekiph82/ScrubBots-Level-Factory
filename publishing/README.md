# Content Publishing Control Plane

This directory is the target home for CP00-CP03 and CP06-CP09 development-time publishing code/configuration.

The publisher owns:

- dry-run validation;
- `.scrubpack` creation;
- manifest construction;
- staging publication;
- remote integrity verification;
- explicit production promotion;
- rollback/disable/scheduling control-plane actions;
- storage/CDN adapters;
- publish/incident evidence.

The shipping game runtime is not implemented here. CP04/CP05 runtime code belongs in `Sekiph82/Scrubbots`.

## Safety

- declarative content only;
- no arbitrary executable payloads;
- no credentials in Git;
- staging before production;
- versioned/auditable state transitions;
- preserve prior known-good versions for rollback.

Local publisher state/caches belong in ignored paths under `publishing/local/` or equivalent.
