from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from scrubbots_content_pipeline.config import Environment
from scrubbots_content_pipeline.provider import ProviderResultCategory
from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider, R2_BUCKET
from test_sb_cp07_003_r2_provider import FAKE_ENV, FakeS3


def _seed(s3: FakeS3, key: str, raw: bytes) -> None:
    etag = hashlib.md5(raw, usedforsecurity=False).hexdigest()
    s3.objects[(R2_BUCKET, key)] = (raw, etag, "application/json", "no-cache")


def test_production_packs_are_copy_if_absent_and_never_replace_existing_bytes():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b"immutable-pack"
    digest = hashlib.sha256(raw).hexdigest()
    provider.write_object_bytes(Environment.STAGING, "packs/v1.scrubpack", digest, raw, if_absent=True)
    _seed(s3, "production/packs/v1.scrubpack", b"preexisting-different")
    result = provider.promote_object(
        Environment.STAGING, "packs/v1.scrubpack", Environment.PRODUCTION,
        "packs/v1.scrubpack", digest,
    )
    assert result.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
    assert s3.objects[(R2_BUCKET, "production/packs/v1.scrubpack")][0] == b"preexisting-different"


def test_exact_existing_production_bytes_are_idempotent_without_rewrite():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b"immutable-pack"
    digest = hashlib.sha256(raw).hexdigest()
    provider.write_object_bytes(Environment.STAGING, "packs/v1.scrubpack", digest, raw, if_absent=True)
    _seed(s3, "production/packs/v1.scrubpack", raw)
    write_count = sum(call[0] == "put" for call in s3.calls)
    result = provider.promote_object(Environment.STAGING, "packs/v1.scrubpack", Environment.PRODUCTION,
                                     "packs/v1.scrubpack", digest)
    assert result.category is ProviderResultCategory.SUCCESS
    assert result.content_digest == digest
    assert sum(call[0] == "put" for call in s3.calls) == write_count


def test_uncertain_target_read_fails_without_mutation():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b"immutable-pack"
    digest = hashlib.sha256(raw).hexdigest()
    provider.write_object_bytes(Environment.STAGING, "packs/v1.scrubpack", digest, raw, if_absent=True)
    before = len([call for call in s3.calls if call[0] == "put"])
    s3.fail_get = True
    result = provider.promote_object(Environment.STAGING, "packs/v1.scrubpack", Environment.PRODUCTION,
                                     "packs/v1.scrubpack", digest)
    assert result.category is ProviderResultCategory.TRANSIENT_FAILURE
    assert sum(call[0] == "put" for call in s3.calls) == before
    assert (R2_BUCKET, "production/packs/v1.scrubpack") not in s3.objects


def test_production_manifest_requires_exact_prior_digest_version_and_monotonic_successor():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    previous = b'{"content_version":5}\n'
    prior_sha = hashlib.sha256(previous).hexdigest()
    _seed(s3, "production/manifests/current.json", previous)
    candidate = b'{"content_version":6}\n'
    candidate_sha = hashlib.sha256(candidate).hexdigest()
    wrong_version = provider.write_manifest_conditionally(
        Environment.PRODUCTION, "production:default", "manifests/current.json",
        candidate_sha, candidate, expected_prior_sha256=prior_sha,
        expected_prior_content_version=4,
    )
    non_successor = provider.write_manifest_conditionally(
        Environment.PRODUCTION, "production:default", "manifests/current.json",
        prior_sha, previous, expected_prior_sha256=prior_sha,
        expected_prior_content_version=5,
    )
    assert wrong_version.category is ProviderResultCategory.INVALID_REQUEST
    assert non_successor.category is ProviderResultCategory.INVALID_REQUEST
    assert s3.objects[(R2_BUCKET, "production/manifests/current.json")][0] == previous


def test_current_manifest_bytes_are_preserved_without_provider_mutation():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b'{"content_version":1}\n'
    result = provider.write_manifest_conditionally(
        Environment.STAGING, "staging:default", "manifests/current.json",
        hashlib.sha256(raw).hexdigest(), raw, expected_prior_sha256=None,
    )
    assert result.category is ProviderResultCategory.SUCCESS
    assert s3.objects[(R2_BUCKET, "staging/manifests/current.json")][0] == raw
