# Factory Studio

This directory is the target home for the owner-facing Windows/operator application.

Authority: `docs/STUDIO_INTEGRATION_PLAN_V01.md`.

## Dependency rule

`Studio -> canonical Factory Core`

The Studio may orchestrate providers, batch jobs, resume, previews, review and publishing UX. It must not own a second independent LevelData compiler, palette authority, Difficulty V1 implementation, solver truth or packaging schema.

## v1.3.6 source candidate

The owner-supplied `ScrubBots Level Factory v1.3.6` ZIP is a migration source candidate. Import only real source/operator assets in a bounded audited cycle.

Do not import virtual environments, build trees, caches, local databases containing owner state, credentials, generated installers or EXEs as source authority.

## Planned layout

```text
studio/
  src/
  adapters/
  assets/
  packaging/
  tests/
```

Credential and user-local state must remain outside Git.
