from __future__ import annotations

import hashlib
import io
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scrubbots_content_pipeline.config import Environment, PRODUCTION_TARGET
from scrubbots_content_pipeline.manifest_history import (
    ManifestHistoryV1, append_manifest_history,
)
from scrubbots_content_pipeline.production_promotion import ProductionManifestPrecondition
from scrubbots_content_pipeline.provider import ProviderResultCategory
from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider
from scrubbots_publish_handoff import _read_production_manifest_history
from test_sb_cp03_007_staging_download_verify import _candidate


class _MissingObject(Exception):
    response = {"Error": {"Code": "NoSuchKey"}, "ResponseMetadata": {"HTTPStatusCode": 404}}


class _ConditionalConflict(Exception):
    response = {"Error": {"Code": "PreconditionFailed"}, "ResponseMetadata": {"HTTPStatusCode": 412}}


class _MemoryR2:
    """Stateful S3-shaped fixture for provider CAS/readback; no files or network."""

    def __init__(self):
        self.objects: dict[str, tuple[bytes, str]] = {}

    def get_object(self, *, Key, **_kwargs):
        if Key not in self.objects:
            raise _MissingObject()
        body, etag = self.objects[Key]
        return {"Body": io.BytesIO(body), "ETag": f'"{etag}"'}

    def put_object(self, *, Key, Body, IfNoneMatch=None, IfMatch=None, **_kwargs):
        current = self.objects.get(Key)
        if IfNoneMatch == "*" and current is not None:
            raise _ConditionalConflict()
        if IfMatch is not None and (current is None or current[1] != IfMatch):
            raise _ConditionalConflict()
        etag = hashlib.sha256(Body).hexdigest()
        self.objects[Key] = (Body, etag)
        return {"ETag": f'"{etag}"'}


def _provider(client):
    return CloudflareR2Provider(client=client, environ={
        "R2_ENDPOINT_URL": "https://" + "a" * 32 + ".r2.cloudflarestorage.com",
        "R2_ACCESS_KEY_ID": "test-access-key-0001",
        "R2_SECRET_ACCESS_KEY": "test-secret-key-000000000001",
    })


def _recorded(history, manifest_bytes, second):
    return append_manifest_history(history, manifest_bytes,
                                   recorded_at_utc=f"2026-10-10T10:00:0{second}Z")


def test_production_manifest_history_handoff_reads_and_cas_persists_n_plus_one_and_n_plus_two():
    client = _MemoryR2()
    provider = _provider(client)
    base = _candidate().manifest

    manifest_n = replace(base, content_version=3).to_json_bytes()
    client.objects["production/manifests/current.json"] = (
        manifest_n, hashlib.sha256(manifest_n).hexdigest())
    history_n = _recorded(ManifestHistoryV1(), manifest_n, 0)
    result = provider.write_manifest_history(
        history_n, expected_prior_tip_sha256=None, current_manifest_bytes=manifest_n)
    assert result.category is ProviderResultCategory.SUCCESS
    assert provider.read_manifest_history() == history_n

    current_history = history_n
    for version, second in ((4, 1), (5, 2)):
        successor = replace(base, content_version=version).to_json_bytes()
        client.objects["production/manifests/current.json"] = (
            successor, hashlib.sha256(successor).hexdigest())
        next_history = _recorded(current_history, successor, second)
        result = provider.write_manifest_history(
            next_history, expected_prior_tip_sha256=current_history.tip_sha256,
            current_manifest_bytes=successor)
        assert result.category is ProviderResultCategory.SUCCESS
        current_history = provider.read_manifest_history()
        assert current_history == next_history
        precondition = ProductionManifestPrecondition(
            PRODUCTION_TARGET.logical_target_id, "manifests/current.json",
            hashlib.sha256(successor).hexdigest(), version, successor)
        assert _read_production_manifest_history(
            current_history, successor, precondition) == next_history

    assert [record.content_version for record in current_history.records] == [3, 4, 5]


def test_production_history_handoff_rejects_stale_tip_and_current_manifest_mismatch():
    client = _MemoryR2()
    provider = _provider(client)
    base = _candidate().manifest
    manifest = replace(base, content_version=3).to_json_bytes()
    client.objects["production/manifests/current.json"] = (
        manifest, hashlib.sha256(manifest).hexdigest())
    history = _recorded(ManifestHistoryV1(), manifest, 0)
    assert provider.write_manifest_history(
        history, expected_prior_tip_sha256="0" * 64,
        current_manifest_bytes=manifest).category is ProviderResultCategory.CONFLICT_STALE_PRECONDITION
    with pytest.raises(ValueError, match="exact M13 history tip"):
        _read_production_manifest_history(
            history, b"different-current-manifest", ProductionManifestPrecondition(
                PRODUCTION_TARGET.logical_target_id, "manifests/current.json",
                hashlib.sha256(manifest).hexdigest(), 3, manifest))


def test_lf_production_handoff_persists_exact_activation_receipt_history(monkeypatch):
    import scrubbots_publish_handoff as handoff
    from types import SimpleNamespace

    for name in ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(name, "test-only-configured")
    base = _candidate().manifest
    manifest_n = replace(base, content_version=3).to_json_bytes()
    prior = _recorded(ManifestHistoryV1(), manifest_n, 0)
    manifest_next = replace(base, content_version=4).to_json_bytes()
    successor = _recorded(prior, manifest_next, 1)
    reviewed = {"candidate_manifest_sha256": "a" * 64, "content_version": 4}
    confirmation = {"confirmed": True, "approval_id": "approval-fixture", "owner_id": "owner-fixture",
                    "manifest_sha256": "a" * 64, "content_version": 4, "target": "PRODUCTION"}
    fresh = {"state": "PREFLIGHT_READY", "reviewed_identity": reviewed,
             "candidate_manifest_sha256": "a" * 64, "content_version": 4}
    monkeypatch.setattr(handoff, "publish_preflight", lambda *_args, **_kwargs: fresh)
    typed = SimpleNamespace(production=SimpleNamespace(manifest_history=prior))
    assembled = []
    monkeypatch.setattr(handoff, "_assemble_staging_request",
                        lambda *_args, **kwargs: (assembled.append(kwargs["provider_factory"]()) or typed))

    class HistoryProvider:
        def __init__(self):
            self.written = None

        def write_manifest_history(self, history, *, expected_prior_tip_sha256, current_manifest_bytes):
            self.written = (history, expected_prior_tip_sha256, current_manifest_bytes)
            return SimpleNamespace(category=ProviderResultCategory.SUCCESS)

        def read_manifest_history(self):
            return self.written[0]

    provider = HistoryProvider()
    class PublisherReport:
        accepted = True
        production_activation = SimpleNamespace(receipt=SimpleNamespace(
            manifest_history=successor, manifest_bytes=manifest_next))
        def to_dict(self):
            return {"accepted": True, "candidate_manifest_sha256": "a" * 64}

    result = handoff.publish_to_production(
        {"reviewed_identity": reviewed, "candidate_ids": ["candidate-1"], "pack_id": "pack-1",
         "content_version": 4, "created_at_utc": "2026-10-10T10:00:00Z"},
        owner_confirmation=confirmation, provider_factory=lambda: provider,
        publisher_runner=lambda _request: PublisherReport())
    assert result["state"] == "PRODUCTION_ACTIVATED"
    assert result["manifest_history"] == "EXACT_READBACK"
    assert provider.written == (successor, prior.tip_sha256, manifest_next)
    assert assembled == [provider]
