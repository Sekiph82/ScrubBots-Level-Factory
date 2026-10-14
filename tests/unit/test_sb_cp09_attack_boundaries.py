from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline import ContentDisposition, ReasonCode, classify_content  # noqa: E402
from scrubbots_content_pipeline.config import Environment  # noqa: E402
from scrubbots_content_pipeline.r2_provider import CloudflareR2Provider  # noqa: E402
from scrubbots_content_pipeline.release_state import (  # noqa: E402
    ReleaseState,
    make_release_event,
    replay_release_events,
)


def test_declarative_boundary_rejects_multiple_executable_injection_shapes() -> None:
    example = ROOT / "content_pipeline" / "schemas" / "v1" / "examples" / "level.json"
    base = json.loads(example.read_text(encoding="utf-8"))
    attacks = (
        ("script", "res://payload.gd"),
        ("display_name", "${__import__('os').system('id')}"),
        ("extension", {"module_path": "https://attacker.invalid/payload"}),
        ("display_name", "level.tscn"),
    )
    for key, value in attacks:
        descriptor = dict(base)
        descriptor["attributes"] = {**base["attributes"], key: value}
        result = classify_content(descriptor)
        assert result.disposition is not ContentDisposition.REMOTE_DECLARATIVE
        assert ReasonCode.EXECUTABLE_FIELD in result.reason_codes or ReasonCode.EXECUTABLE_REFERENCE in result.reason_codes


def test_r2_endpoint_allowlist_requires_exact_https_cloudflare_host() -> None:
    accepted = CloudflareR2Provider(environ={
        "R2_ENDPOINT_URL": "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com",
    })
    assert accepted._endpoint() == "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com"
    for endpoint in (
        "http://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com",
        "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com.attacker.invalid",
        "https://attacker.invalid/0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com",
        "https://0123456789abcdef0123456789abcdef.r2.cloudflarestorage.com/path",
    ):
        assert CloudflareR2Provider(environ={"R2_ENDPOINT_URL": endpoint})._endpoint() is None


def test_release_ledger_replay_rejects_tamper_and_old_event_replay() -> None:
    event = make_release_event(
        sequence=1, event_id="stage-001", transition_id="stage-001", record_id="staging-001",
        content_id="manifest-v1", content_digest="a" * 64, environment=Environment.STAGING,
        from_state=None, to_state=ReleaseState.DRAFT, expected_state=None,
        previous_event_digest="0" * 64,
    )
    assert replay_release_events((event,)).accepted
    tampered = replace(event, content_digest="b" * 64)
    assert not replay_release_events((tampered,)).accepted
    replayed = replace(event, event_id="stage-002", transition_id="stage-002")
    assert not replay_release_events((event, replayed)).accepted
