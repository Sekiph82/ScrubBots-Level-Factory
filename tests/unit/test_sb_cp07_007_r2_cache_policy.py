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


def test_pack_metadata_is_immutable_and_manifest_is_revalidated_json():
    s3 = FakeS3()
    provider = CloudflareR2Provider(client=s3, environ=FAKE_ENV)
    pack = b"pack"
    pack_digest = hashlib.sha256(pack).hexdigest()
    pack_result = provider.write_object_bytes(
        Environment.STAGING, "packs/immutable.scrubpack", pack_digest, pack, if_absent=True,
    )
    manifest = b'{"content_version":1}\n'
    manifest_digest = hashlib.sha256(manifest).hexdigest()
    manifest_result = provider.write_manifest_conditionally(
        Environment.STAGING, "staging:default", "manifests/current.json",
        manifest_digest, manifest, expected_prior_sha256=None,
    )
    pack_meta = s3.objects[(R2_BUCKET, "staging/packs/immutable.scrubpack")][2:]
    manifest_meta = s3.objects[(R2_BUCKET, "staging/manifests/current.json")][2:]
    assert pack_result.category is ProviderResultCategory.SUCCESS
    assert manifest_result.category is ProviderResultCategory.SUCCESS
    assert pack_meta == ("application/octet-stream", "public, max-age=31536000, immutable")
    assert manifest_meta == ("application/json", "no-cache")
