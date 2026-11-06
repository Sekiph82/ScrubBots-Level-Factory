"""Offline PixelLab MCP transport tests; no provider request or file output."""

import base64
from io import BytesIO
from urllib.error import HTTPError

import pytest
from PIL import Image

from scrubbots_pixel_factory import studio_extensions as extensions
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.studio_extensions import (
    PixelLabProviderError,
    generate_pixellab_pro_4x4_atlas_mcp,
)


def _atlas_png(width: int = 224, height: int = 224) -> bytes:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    color = CANONICAL_PALETTE.colors[0].rgb + (255,)
    image.putpixel((0, 0), color)
    image.putpixel((width - 1, height - 1), color)
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _image_result(raw: bytes) -> dict[str, object]:
    return {"jsonrpc": "2.0", "id": 4, "result": {"content": [
        {"type": "image", "mimeType": "image/png", "data": base64.b64encode(raw).decode("ascii")},
    ]}}


def test_windows_credential_blob_decodes_utf8_and_utf16le_without_nuls() -> None:
    token = "pixl_test-token-012345"
    assert extensions._decode_windows_credential_blob(token.encode("utf-8")) == token
    assert extensions._decode_windows_credential_blob((token + "\x00").encode("utf-16-le")) == token
    assert extensions._decode_windows_credential_blob((token + "\x00").encode("utf-8")) == ""


def test_mcp_pro_generation_uses_locked_palette_and_fetches_inline_4x4_atlas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    atlas = _atlas_png()
    calls: list[dict[str, object]] = []
    events: list[str] = []

    def request_message(**kwargs: object):
        message = kwargs["message"]
        assert isinstance(message, dict)
        calls.append(message)
        if message.get("method") == "initialize":
            return {"jsonrpc": "2.0", "id": 1, "result": {
                "protocolVersion": "2025-11-25", "capabilities": {},
                "serverInfo": {"name": "PixelLab", "version": "test"},
            }}, {"MCP-Session-Id": "session-test"}
        if message.get("method") == "notifications/initialized":
            return {}, {"MCP-Session-Id": "session-test"}
        params = message["params"]
        if params["name"] == "create_image_pro":
            assert params["arguments"] == {
                "description": "a blue slime",
                "width": 56,
                "height": 56,
                "no_background": True,
                "palette": [color.hex.upper() for color in CANONICAL_PALETTE.colors],
                "palette_name": "ScrubBots Palette V3",
                "max_colors": 12,
                "seed": 20261106,
            }
            return {"jsonrpc": "2.0", "id": message["id"], "result": {
                "content": [{"type": "text", "text": "job_id: mcp-job-1"}],
            }}, {}
        assert params["name"] == "get_image"
        assert params["arguments"] == {"job_id": "mcp-job-1"}
        return {**_image_result(atlas), "id": message["id"]}, {}

    result = generate_pixellab_pro_4x4_atlas_mcp(
        description="a blue slime", width=56, height=56, max_colors=12, seed=20261106,
        request_message=request_message,
        on_submission_started=lambda: events.append("submission"),
        on_mcp_request_started=lambda count: events.append(f"request-{count}"),
    )

    assert result.atlas_png == atlas
    assert result.job_id == "mcp-job-1"
    assert result.mcp_request_count == 4
    assert [call.get("method") for call in calls] == [
        "initialize", "notifications/initialized", "tools/call", "tools/call",
    ]
    assert events.index("submission") < events.index("request-3")
    assert all(call.get("method") != "tools/list" for call in calls)


def test_mcp_rejects_wrong_atlas_size_without_resubmitting(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    creates = 0

    def request_message(**kwargs: object):
        nonlocal creates
        message = kwargs["message"]
        if message.get("method") == "initialize":
            return {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25"}}, {}
        if message.get("method") == "notifications/initialized":
            return {}, {}
        if message["params"]["name"] == "create_image_pro":
            creates += 1
            return {"jsonrpc": "2.0", "id": message["id"], "result": {
                "content": [{"type": "text", "text": "job_id: mcp-job-2"}],
            }}, {}
        return {**_image_result(_atlas_png(56, 56)), "id": message["id"]}, {}

    with pytest.raises(PixelLabProviderError, match="exact 4x4 size"):
        generate_pixellab_pro_4x4_atlas_mcp(
            description="wrong dimensions", width=56, height=56, seed=2,
            request_message=request_message,
        )
    assert creates == 1


def test_mcp_credential_preflight_is_free_and_sends_no_request(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "")
    requests: list[object] = []
    with pytest.raises(PixelLabProviderError, match="PIXELLAB_API_TOKEN_NOT_CONFIGURED"):
        generate_pixellab_pro_4x4_atlas_mcp(
            description="preflight", width=56, height=56, seed=1,
            request_message=lambda **kwargs: requests.append(kwargs),
        )
    assert requests == []


def test_mcp_unknown_paid_submission_is_never_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    creates = 0
    started: list[bool] = []

    def request_message(**kwargs: object):
        nonlocal creates
        message = kwargs["message"]
        if message.get("method") == "initialize":
            return {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2025-11-25"}}, {}
        if message.get("method") == "notifications/initialized":
            return {}, {}
        creates += 1
        raise PixelLabProviderError("SUBMISSION_UNKNOWN", "No automatic retry.")

    with pytest.raises(PixelLabProviderError, match="No automatic retry"):
        generate_pixellab_pro_4x4_atlas_mcp(
            description="ambiguous", width=56, height=56, seed=1,
            request_message=request_message,
            on_submission_started=lambda: started.append(True),
        )
    assert started == [True]
    assert creates == 1


def test_mcp_shutdown_cancels_accepted_job_and_keeps_job_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    shutting_down = False
    calls: list[str] = []

    def shutdown_requested() -> bool:
        return shutting_down

    monkeypatch.setattr("scrubbots_pixel_factory.studio_lifecycle.studio_shutdown_requested", shutdown_requested)

    def request_message(**kwargs: object):
        nonlocal shutting_down
        message = kwargs["message"]
        method = str(message.get("method", ""))
        if method == "initialize":
            calls.append("initialize")
            return {"jsonrpc": "2.0", "id": message["id"], "result": {"protocolVersion": "2025-11-25"}}, {}
        if method == "notifications/initialized":
            calls.append("initialized")
            return {}, {}
        name = str(message["params"]["name"])
        calls.append(name)
        if name == "create_image_pro":
            return {"jsonrpc": "2.0", "id": message["id"], "result": {
                "content": [{"type": "text", "text": "job_id: mcp-shutdown-job"}],
            }}, {}
        if name == "cancel_job":
            return {"jsonrpc": "2.0", "id": message["id"], "result": {
                "content": [{"type": "text", "text": "cancelled"}],
            }}, {}
        raise AssertionError(f"unexpected MCP tool request: {name}")

    def accepted(_job_id: str) -> None:
        nonlocal shutting_down
        shutting_down = True

    with pytest.raises(PixelLabProviderError) as caught:
        generate_pixellab_pro_4x4_atlas_mcp(
            description="a blue slime", width=56, height=56, seed=17,
            request_message=request_message, on_job_accepted=accepted,
        )

    assert caught.value.code == "STUDIO_SHUTDOWN_CANCELLED"
    assert caught.value.job_id == "mcp-shutdown-job"
    assert calls == ["initialize", "initialized", "create_image_pro", "cancel_job"]


@pytest.mark.parametrize(
    ("status", "expected_code"),
    [(401, "MCP_AUTHENTICATION_FAILED"), (402, "INSUFFICIENT_CREDITS"), (429, "RATE_LIMITED")],
)
def test_mcp_http_failures_are_classified_without_exposing_response_body(
    monkeypatch: pytest.MonkeyPatch, status: int, expected_code: str
) -> None:
    def reject_request(*args: object, **kwargs: object) -> None:
        raise HTTPError("https://api.pixellab.ai/mcp", status, "failure", {}, BytesIO(b"private-body"))

    monkeypatch.setattr(extensions, "urlopen", reject_request)
    with pytest.raises(PixelLabProviderError) as caught:
        extensions._mcp_http_request(
            secret="test-token", message={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            session_id=None, protocol_version=None,
        )
    assert caught.value.code == expected_code
    assert "private-body" not in str(caught.value)
