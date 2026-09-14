# Content Lifecycle Workspace

This directory defines repository-visible boundaries for content lifecycle artifacts.

Recommended lifecycle:

```text
candidate -> validated -> owner/review accepted -> campaign-selected -> packaged -> staged -> production
```

Generated high-volume candidate/rejected/temp content should remain in ignored local paths unless a prompt explicitly authorizes evidence fixtures.

Canonical source/provenance, approved golden fixtures and small audit evidence may be committed when required.

Do not place publishing credentials, user-local databases or runtime cache state here.
