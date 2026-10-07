from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "content_pipeline" / "schemas" / "v1"

NEUTRAL_CONTRACTS = (
    SCHEMAS / "content-manifest.schema.json",
    SCHEMAS / "scrubpack-manifest.schema.json",
    SCHEMAS / "examples" / "level.json",
    SCHEMAS / "examples" / "supply-plan.json",
    SCHEMAS / "examples" / "approved-metadata.json",
)
PROVIDER_TERMS = re.compile(
    r"cloudflare|r2\.dev|cloudflarestorage|r2_(?:bucket|account|endpoint|access|secret)|"
    r"(?:access|secret)_key|api_token|account_id|\bbucket\b",
    re.IGNORECASE,
)


def _keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from _keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _keys(nested)


def test_neutral_manifest_scrubpack_level_supply_and_metadata_have_no_r2_fields():
    for path in NEUTRAL_CONTRACTS:
        raw = path.read_text(encoding="utf-8")
        assert PROVIDER_TERMS.search(raw) is None, path.relative_to(ROOT)
        parsed = json.loads(raw)
        assert all(PROVIDER_TERMS.search(str(key)) is None for key in _keys(parsed)), path.relative_to(ROOT)


def test_r2_specific_imports_and_client_dependencies_stay_in_adapter_boundary():
    neutral_sources = (
        ROOT / "content_pipeline/src/scrubbots_content_pipeline/provider.py",
        ROOT / "content_pipeline/src/scrubbots_content_pipeline/config.py",
        ROOT / "content_pipeline/src/scrubbots_content_pipeline/manifest_v1.py",
        ROOT / "content_pipeline/src/scrubbots_content_pipeline/scrubpack_spec.py",
        ROOT / "content_pipeline/src/scrubbots_content_pipeline/payload_validation.py",
    )
    for path in neutral_sources:
        content = path.read_text(encoding="utf-8").lower()
        assert "r2_provider" not in content and "import boto3" not in content
    adapter = (ROOT / "content_pipeline/src/scrubbots_content_pipeline/r2_provider.py").read_text(encoding="utf-8")
    assert "import boto3" in adapter
