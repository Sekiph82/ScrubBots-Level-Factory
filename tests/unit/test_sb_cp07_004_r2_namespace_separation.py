from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline.config import Environment
from scrubbots_content_pipeline.provider import ProviderResultCategory
from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider, physical_object_key


def test_identical_neutral_key_has_disjoint_physical_environment_namespaces():
    logical_key = "packs/pack-001.scrubpack"
    staging = physical_object_key(Environment.STAGING, logical_key)
    production = physical_object_key(Environment.PRODUCTION, logical_key)
    assert staging == "staging/" + logical_key
    assert production == "production/" + logical_key
    assert staging != production
    assert not staging.startswith("production/")
    assert not production.startswith("staging/")


def test_control_namespace_cannot_be_referenced_as_game_content():
    for key in ("_control/release-events/current.json", "_control/manifest-history/one.json"):
        try:
            physical_object_key(Environment.STAGING, key)
        except ValueError:
            continue
        raise AssertionError("provider control key was accepted as content")


def test_staging_writer_and_manifest_surface_reject_production_and_control_keys():
    provider = CloudflareR2Provider(environ={})
    digest = hashlib.sha256(b"x").hexdigest()
    direct_production = provider.write_object_bytes(
        Environment.PRODUCTION, "packs/a.scrubpack", digest, b"x", if_absent=True,
    )
    control_manifest = provider.write_manifest_conditionally(
        Environment.STAGING, "staging:default", "_control/current.json", digest,
        b"x", expected_prior_sha256=None,
    )
    assert direct_production.category is ProviderResultCategory.INVALID_REQUEST
    assert control_manifest.category is ProviderResultCategory.INVALID_REQUEST
