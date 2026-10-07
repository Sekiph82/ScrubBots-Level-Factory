from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from scrubbots_content_pipeline.config import Environment
from scrubbots_content_pipeline.provider import ProviderIdentity, ProviderObjectBytesResult, ProviderResultCategory
from scrubbots_content_pipeline.r2_export import ExportReason, export_current_production
from test_sb_cp03_007_staging_download_verify import _candidate, MANIFEST_KEY


class ProductionReader:
    identity = ProviderIdentity("test-reader", "1.0")

    def __init__(self):
        candidate = _candidate()
        self.objects = {MANIFEST_KEY: candidate.manifest_bytes}
        self.objects.update({pack.object_key: build.archive_bytes
                             for pack, build in zip(candidate.manifest.packs, candidate.pack_builds)})
        self.calls: list[tuple[Environment, str]] = []
        self.missing: set[str] = set()
        self.corrupt: set[str] = set()

    def read_object_bytes(self, environment, object_key):
        self.calls.append((environment, object_key))
        if environment is not Environment.PRODUCTION or object_key in self.missing:
            return ProviderObjectBytesResult("1.0", ProviderResultCategory.UNAVAILABLE,
                                             self.identity.provider_id, environment, object_key, None)
        raw = self.objects.get(object_key)
        if raw is not None and object_key in self.corrupt:
            raw = raw + b"corrupt"
        if raw is None:
            return ProviderObjectBytesResult("1.0", ProviderResultCategory.UNAVAILABLE,
                                             self.identity.provider_id, environment, object_key, None)
        return ProviderObjectBytesResult("1.0", ProviderResultCategory.SUCCESS,
                                         self.identity.provider_id, environment, object_key, raw)


def test_export_downloads_exact_manifest_and_every_pack_with_deterministic_receipt(tmp_path):
    provider = ProductionReader()
    first = export_current_production(provider, tmp_path / "first")
    second = export_current_production(provider, tmp_path / "second")
    assert first.accepted and first.reason_code is ExportReason.EXPORTED
    assert second.accepted and first.receipt_bytes == second.receipt_bytes
    assert (tmp_path / "first" / MANIFEST_KEY).read_bytes() == provider.objects[MANIFEST_KEY]
    receipt = json.loads(first.receipt_bytes)
    assert hashlib.sha256(provider.objects[MANIFEST_KEY]).hexdigest() == receipt["manifest"]["sha256"]
    for pack in receipt["packs"]:
        raw = provider.objects[pack["object_key"]]
        assert (tmp_path / "first" / pack["object_key"]).read_bytes() == raw
        assert len(raw) == pack["byte_length"]
        assert hashlib.sha256(raw).hexdigest() == pack["sha256"]
    assert all(environment is Environment.PRODUCTION for environment, _ in provider.calls)


def test_missing_or_corrupt_pack_fails_before_creating_destination(tmp_path):
    provider = ProductionReader()
    pack_key = next(key for key in provider.objects if key != MANIFEST_KEY)
    provider.corrupt.add(pack_key)
    destination = tmp_path / "corrupt"
    result = export_current_production(provider, destination)
    assert not result.accepted and result.reason_code is ExportReason.PACK_INTEGRITY_MISMATCH
    assert not destination.exists()
    provider.corrupt.clear()
    provider.missing.add(pack_key)
    missing = export_current_production(provider, destination)
    assert not missing.accepted and missing.reason_code is ExportReason.PACK_UNAVAILABLE
    assert not destination.exists()


def test_export_refuses_existing_files_without_overwriting(tmp_path):
    provider = ProductionReader()
    destination = tmp_path / "existing"
    destination.mkdir()
    target = destination / MANIFEST_KEY
    target.parent.mkdir()
    target.write_bytes(b"owner data")
    result = export_current_production(provider, destination)
    assert result.reason_code is ExportReason.DESTINATION_CONFLICT
    assert target.read_bytes() == b"owner data"
