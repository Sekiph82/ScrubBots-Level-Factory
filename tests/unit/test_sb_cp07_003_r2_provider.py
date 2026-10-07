from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline.config import Environment
from scrubbots_content_pipeline.provider import ProviderFeature, ProviderResultCategory
from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider, R2_BUCKET, physical_object_key
from scrubbots_content_pipeline.release_state import ReleaseState, make_release_event

FAKE_ENV = {
    "R2_ENDPOINT_URL": "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com",
    "R2_ACCESS_KEY_ID": "test-access-key-01",
    "R2_SECRET_ACCESS_KEY": "test-secret-key-01",
}


class FakeS3:
    def __init__(self):
        self.objects: dict[tuple[str, str], tuple[bytes, str, str, str]] = {}
        self.calls: list[tuple[str, str]] = []
        self.fail_get = False
        self.fail_production_put = False
        self.corrupt_read = False

    def put_object(self, **kwargs):
        key = (kwargs["Bucket"], kwargs["Key"])
        self.calls.append(("put", kwargs["Key"]))
        if self.fail_production_put and kwargs["Key"].startswith("production/"):
            raise RuntimeError("secret-like production write failure")
        current = self.objects.get(key)
        if kwargs.get("IfNoneMatch") == "*" and current is not None:
            raise PreconditionError()
        if kwargs.get("IfMatch") is not None and (current is None or current[1] != kwargs["IfMatch"]):
            raise PreconditionError()
        body = bytes(kwargs["Body"])
        etag = hashlib.md5(body, usedforsecurity=False).hexdigest()
        self.objects[key] = (body, etag, kwargs.get("ContentType", ""), kwargs.get("CacheControl", ""))
        return {"ETag": f'"{etag}"'}

    def get_object(self, *, Bucket, Key):
        self.calls.append(("get", Key))
        if self.fail_get:
            raise RuntimeError("sensitive credential sample")
        item = self.objects.get((Bucket, Key))
        if item is None:
            error = RuntimeError("missing")
            error.response = {"Error": {"Code": "NoSuchKey"}, "ResponseMetadata": {"HTTPStatusCode": 404}}
            raise error
        body = item[0][:-1] + b"x" if self.corrupt_read and item[0] else item[0]
        return {"Body": MemoryBody(body), "ETag": f'"{item[1]}"'}

    def copy_object(self, **kwargs):
        self.calls.append(("copy", kwargs["Key"]))
        if self.fail_copy:
            raise RuntimeError("secret-like provider detail")
        source = kwargs["CopySource"]["Key"]
        value = self.objects[(kwargs["Bucket"], source)]
        return self.put_object(Bucket=kwargs["Bucket"], Key=kwargs["Key"], Body=value[0],
                               ContentType=value[2], CacheControl=value[3],
                               IfNoneMatch=kwargs.get("IfNoneMatch"))


class MemoryBody:
    def __init__(self, value: bytes):
        self.value = value

    def read(self):
        return self.value


class PreconditionError(Exception):
    response = {"Error": {"Code": "PreconditionFailed"}, "ResponseMetadata": {"HTTPStatusCode": 412}}


def test_physical_namespace_is_disjoint_and_keys_stay_neutral():
    assert physical_object_key(Environment.STAGING, "packs/p1.scrubpack") == "staging/packs/p1.scrubpack"
    assert physical_object_key(Environment.PRODUCTION, "packs/p1.scrubpack") == "production/packs/p1.scrubpack"
    assert physical_object_key(Environment.STAGING, "packs/p1.scrubpack") != physical_object_key(Environment.PRODUCTION, "packs/p1.scrubpack")
    for key in ("../secret", "_control/current.json", "production/packs/a", "staging/packs/a"):
        try:
            physical_object_key(Environment.STAGING, key)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted reserved or unsafe logical key: {key}")


def test_exact_byte_upload_read_verify_is_idempotent_and_never_overwrites():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b"scrubpack-exact-bytes"
    digest = hashlib.sha256(raw).hexdigest()
    first = provider.write_object_bytes(Environment.STAGING, "packs/a.scrubpack", digest, raw, if_absent=True)
    second = provider.write_object_bytes(Environment.STAGING, "packs/a.scrubpack", digest, raw, if_absent=True)
    conflict = provider.write_object_bytes(Environment.STAGING, "packs/a.scrubpack", hashlib.sha256(b"different").hexdigest(), b"different", if_absent=True)
    assert first.category is ProviderResultCategory.SUCCESS
    assert second.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
    assert conflict.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
    assert provider.read_object_bytes(Environment.STAGING, "packs/a.scrubpack").content_bytes == raw
    assert provider.verify_object(Environment.STAGING, "packs/a.scrubpack", digest).category is ProviderResultCategory.SUCCESS
    assert s3.objects[(R2_BUCKET, "staging/packs/a.scrubpack")][0] == raw
    assert len(s3.objects) == 1
    assert s3.objects[(R2_BUCKET, "staging/packs/a.scrubpack")][2:] == (
        "application/octet-stream", "public, max-age=31536000, immutable")


def test_no_credentials_or_invalid_endpoint_fail_before_mutation():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ={})
    result = provider.write_object_bytes(Environment.STAGING, "packs/a.scrubpack", hashlib.sha256(b"x").hexdigest(), b"x", if_absent=True)
    assert result.category is ProviderResultCategory.UNAVAILABLE
    assert not s3.calls
    provider = CloudflareR2Provider(environ={"R2_ENDPOINT_URL": "http://bad.example", "R2_ACCESS_KEY_ID": "x", "R2_SECRET_ACCESS_KEY": "y"})
    assert provider.write_object_bytes(Environment.STAGING, "packs/a", hashlib.sha256(b"x").hexdigest(), b"x", if_absent=True).category is ProviderResultCategory.UNAVAILABLE


def test_direct_production_write_and_hash_mismatch_fail_closed():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b"x"
    assert provider.write_object_bytes(Environment.PRODUCTION, "packs/a", hashlib.sha256(raw).hexdigest(), raw, if_absent=True).category is ProviderResultCategory.INVALID_REQUEST
    assert provider.write_object_bytes(Environment.STAGING, "packs/a", "0" * 64, raw, if_absent=True).category is ProviderResultCategory.INVALID_REQUEST
    assert not s3.calls


def test_provider_exception_text_is_not_returned_or_in_repr():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    s3.fail_get = True
    read = provider.read_object_bytes(Environment.STAGING, "packs/a")
    result = provider.verify_object(Environment.STAGING, "packs/a", "0" * 64)
    assert read.category is ProviderResultCategory.TRANSIENT_FAILURE
    assert result.category is ProviderResultCategory.TRANSIENT_FAILURE
    assert "sensitive credential sample" not in repr(provider)


def test_failed_copy_is_normalized_and_cross_environment_copy_is_denied():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b"copy"
    digest = hashlib.sha256(raw).hexdigest()
    provider.write_object_bytes(Environment.STAGING, "packs/a", digest, raw, if_absent=True)
    s3.fail_production_put = True
    failed = provider.promote_object(Environment.STAGING, "packs/a", Environment.PRODUCTION, "packs/a", digest)
    denied = provider.promote_object(Environment.PRODUCTION, "packs/a", Environment.STAGING, "packs/a", digest)
    assert failed.category is ProviderResultCategory.TRANSIENT_FAILURE
    assert denied.category is ProviderResultCategory.UNAUTHORIZED_REFERENCE
    assert ProviderFeature.OBJECT_DELETE not in provider.capabilities.features


def test_corrupt_readback_is_reported_as_integrity_failure():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b"exact bytes"
    digest = hashlib.sha256(raw).hexdigest()
    provider.write_object_bytes(Environment.STAGING, "packs/a", digest, raw, if_absent=True)
    s3.corrupt_read = True
    assert provider.verify_object(Environment.STAGING, "packs/a", digest).category is ProviderResultCategory.INTEGRITY_MISMATCH


def test_release_event_append_is_content_addressed_and_stale_tip_is_rejected():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    event = make_release_event(
        sequence=1, event_id="stage-1", transition_id="stage-1", record_id="staging-1",
        content_id="manifest-v1", content_digest="a" * 64, environment=Environment.STAGING,
        from_state=None, to_state=ReleaseState.DRAFT, expected_state=None,
        previous_event_digest="0" * 64,
    )
    stale = provider.append_release_event(event, expected_prior_sequence=2, expected_prior_event_digest="b" * 64)
    accepted = provider.append_release_event(event, expected_prior_sequence=0, expected_prior_event_digest="0" * 64)
    assert stale.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
    assert accepted.category is ProviderResultCategory.SUCCESS
    assert provider.read_release_events() == (event,)
    assert (R2_BUCKET, "_control/release-events/current.json") in s3.objects


def test_staging_manifest_is_conditional_no_cache_json_and_preserves_neutral_key():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    raw = b'{"content_version":1}\n'
    digest = hashlib.sha256(raw).hexdigest()
    first = provider.write_manifest_conditionally(
        Environment.STAGING, "staging:default", "manifests/current.json", digest, raw,
        expected_prior_sha256=None,
    )
    second = provider.write_manifest_conditionally(
        Environment.STAGING, "staging:default", "manifests/current.json", digest, raw,
        expected_prior_sha256=None,
    )
    stored = s3.objects[(R2_BUCKET, "staging/manifests/current.json")]
    assert first.category is ProviderResultCategory.SUCCESS
    assert second.category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
    assert stored[0] == raw and stored[2:] == ("application/json", "no-cache")
