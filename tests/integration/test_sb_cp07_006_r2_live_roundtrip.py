from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline.config import Environment
from scrubbots_content_pipeline.provider import ProviderResultCategory
from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider


def _live_credentials_present() -> bool:
    endpoint = os.environ.get("R2_ENDPOINT_URL") or os.environ.get("R2_ACCOUNT_ID")
    return bool(endpoint and os.environ.get("R2_ACCESS_KEY_ID") and os.environ.get("R2_SECRET_ACCESS_KEY"))


@pytest.mark.skipif(not _live_credentials_present(), reason="OWNER_R2_WRITE_CREDENTIAL_REQUIRED")
def test_live_r2_staging_round_trip_is_exact_and_idempotent():
    payload = b"ScrubBots R2 staging integration probe v1\n"
    digest = hashlib.sha256(payload).hexdigest()
    object_key = f"_integration/roundtrip/{digest}.bin"
    provider = CloudflareR2Provider()

    first = provider.write_object_bytes(Environment.STAGING, object_key, digest, payload, if_absent=True)
    assert first.category in {ProviderResultCategory.SUCCESS, ProviderResultCategory.CONFLICT_STALE_PRECONDITION}
    readback = provider.read_object_bytes(Environment.STAGING, object_key)
    assert readback.category is ProviderResultCategory.SUCCESS
    assert readback.content_bytes == payload
    assert len(readback.content_bytes) == len(payload)
    assert hashlib.sha256(readback.content_bytes).hexdigest() == digest
    assert provider.verify_object(Environment.STAGING, object_key, digest).category is ProviderResultCategory.SUCCESS
