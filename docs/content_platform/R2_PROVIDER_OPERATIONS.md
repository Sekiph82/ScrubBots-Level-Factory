# Cloudflare R2 Content Provider Operations

The M18 provider stores provider-neutral object keys under separate physical
prefixes in the owner-provisioned `scrubbots-content-prod` bucket:

- staging content: `staging/<object_key>`
- production content: `production/<object_key>`
- release-control state: `_control/<control_key>`

Manifests continue to contain provider-neutral keys such as
`packs/<pack-id>.scrubpack`. The provider adds the environment prefix when it
addresses R2. The stable current production manifest key is
`production/manifests/current.json`.

`.scrubpack` objects are created conditionally and receive
`application/octet-stream` with `public, max-age=31536000, immutable`.
Manifest objects receive `application/json` and `no-cache`, so clients
revalidate the stable current pointer. Provider control objects remain under
`_control/` and cannot be used as game content keys.

The owner-provisioned `r2.dev` URL is the Family Test read-delivery endpoint.
Its availability and caching behavior do not establish final custom-domain
CDN configuration. A later delivery host can change the public base URL while
provider-neutral object keys remain stable.

The provider requires an operator process environment with `R2_ACCESS_KEY_ID`,
`R2_SECRET_ACCESS_KEY`, and either a valid `R2_ENDPOINT_URL` or `R2_ACCOUNT_ID`.
Credentials are read at client initialization and are never part of pipeline
configuration, reports, receipts, or logs. The actual required permission scope
is documented separately in `R2_PUBLISHER_SECRET_BOUNDARY.md`.
