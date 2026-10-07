from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from scrubbots_content_pipeline.config import Environment
from scrubbots_content_pipeline.provider import ProviderResultCategory
from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider
from test_sb_cp07_003_r2_provider import FakeS3


def test_malformed_credentials_and_non_r2_endpoint_fail_before_remote_calls():
    fake = FakeS3()
    cases = (
        {"R2_ENDPOINT_URL": "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com", "R2_ACCESS_KEY_ID": "short", "R2_SECRET_ACCESS_KEY": "also-short"},
        {"R2_ENDPOINT_URL": "https://attacker.example", "R2_ACCESS_KEY_ID": "a" * 32, "R2_SECRET_ACCESS_KEY": "b" * 32},
        {"R2_ENDPOINT_URL": "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com", "R2_ACCESS_KEY_ID": "a" * 32, "R2_SECRET_ACCESS_KEY": "b" * 15 + "\n"},
    )
    for env in cases:
        provider = CloudflareR2Provider(client=fake, environ=env)
        result = provider.write_object_bytes(
            Environment.STAGING, "packs/a.scrubpack", hashlib.sha256(b"x").hexdigest(), b"x", if_absent=True,
        )
        assert result.category is ProviderResultCategory.UNAVAILABLE
    assert not fake.calls


def test_credentials_do_not_escape_repr_results_or_serialized_capabilities():
    access = "ACCESS_KEY_0123456789abcdef"
    secret = "SECRET_KEY_0123456789abcdef0123456789"
    env = {
        "R2_ENDPOINT_URL": "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com",
        "R2_ACCESS_KEY_ID": access,
        "R2_SECRET_ACCESS_KEY": secret,
    }
    provider = CloudflareR2Provider(client=FakeS3(), environ=env)
    payload = json.dumps(provider.capabilities.to_dict()) + repr(provider)
    assert access not in payload and secret not in payload
    assert "credentials=redacted" in repr(provider)


def test_provider_exceptions_are_normalized_without_raw_text():
    fake = FakeS3()
    fake.fail_get = True
    provider = CloudflareR2Provider(client=fake, environ={
        "R2_ENDPOINT_URL": "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com",
        "R2_ACCESS_KEY_ID": "ACCESS_KEY_0123456789abcdef",
        "R2_SECRET_ACCESS_KEY": "SECRET_KEY_0123456789abcdef0123456789",
    })
    result = provider.verify_object(Environment.STAGING, "packs/a", "0" * 64)
    assert result.category is ProviderResultCategory.TRANSIENT_FAILURE
    assert "sensitive credential sample" not in repr(result)
    assert "SECRET_KEY_" not in repr(result)
