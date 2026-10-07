# R2 Publisher Secret Boundary

The publisher uses only S3-compatible object operations against the fixed
`scrubbots-content-prod` bucket. The operator supplies `R2_ACCESS_KEY_ID`,
`R2_SECRET_ACCESS_KEY`, and either `R2_ENDPOINT_URL` or `R2_ACCOUNT_ID` through
the process environment or a secure launcher that injects those environment
values. The adapter accepts only HTTPS R2 endpoints and rejects blank,
malformed, or control-character credentials before constructing a client or
making a remote request.

Create an R2 API token with **Object Read & Write** permission scoped to this
bucket only. Cloudflare currently groups object read, write, and list in that
bucket-scoped permission; this implementation calls object GET and conditional
PUT operations only, and does not list buckets or objects. The API token must
not have Admin Read & Write, account administration, DNS, billing, Worker, or
bucket-configuration permissions. The service never calls delete, ACL, bucket
creation, or Cloudflare REST API operations.

`boto3` and its `botocore` dependency are used only by the opt-in remote
provider. Credentials are not accepted in `PipelineConfig`, command-line
arguments, repository files, `.env` files, job reports, export receipts,
exception text, or provider `repr`. Do not place real credentials in local
tracked or untracked project files. Missing or malformed values produce a
sanitized unavailable result before the SDK client can issue a request.

Official references:

- [Cloudflare R2 S3 API authentication](https://developers.cloudflare.com/r2/api/tokens/)
- [Cloudflare R2 S3-compatible client setup](https://developers.cloudflare.com/r2/get-started/s3/)
- [Cloudflare R2 conditional operations](https://developers.cloudflare.com/r2/api/s3/extensions/)
