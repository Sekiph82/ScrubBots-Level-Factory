"""Owner 2026-11-10: two batch rows stopped with MCP_NETWORK_ERROR after PixelLab had
accepted and charged them (rows 10 of two runs). The failure was one dropped free
get_image status read. Polling must retry read-only calls and never resubmit."""
import base64
from io import BytesIO

import pytest
from PIL import Image

from scrubbots_pixel_factory import studio_extensions as extensions
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE
from scrubbots_pixel_factory.studio_extensions import PixelLabProviderError, generate_pixellab_pro_4x4_atlas_mcp


def _atlas_png() -> bytes:
    image = Image.new("RGBA", (224, 224), (0, 0, 0, 0))
    image.putpixel((0, 0), CANONICAL_PALETTE.colors[0].rgb + (255,))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _provider(atlas: bytes, *, drops: int, calls: list[str]):
    remaining = {"drops": drops}

    def request_message(**kwargs: object):
        message = kwargs["message"]
        method = message.get("method")
        if method == "initialize":
            calls.append("initialize")
            return {"jsonrpc": "2.0", "id": message["id"], "result": {"protocolVersion": "2025-11-25"}}, {"MCP-Session-Id": "s"}
        if method == "notifications/initialized":
            return {}, {}
        name = message["params"]["name"]
        calls.append(name)
        if name == "create_image_pro":
            return {"jsonrpc": "2.0", "id": message["id"], "result": {
                "content": [{"type": "text", "text": "job_id: job-accepted"}]}}, {}
        assert name == "get_image" and message["params"]["arguments"] == {"job_id": "job-accepted"}
        if remaining["drops"]:
            remaining["drops"] -= 1
            raise PixelLabProviderError("MCP_NETWORK_ERROR", "Could not complete the PixelLab MCP request.")
        return {"jsonrpc": "2.0", "id": message["id"], "result": {"content": [
            {"type": "image", "mimeType": "image/png", "data": base64.b64encode(atlas).decode("ascii")}]}}, {}

    return request_message


def test_dropped_status_read_is_retried_without_resubmitting(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    atlas, calls = _atlas_png(), []

    result = generate_pixellab_pro_4x4_atlas_mcp(
        description="forest spirit", width=56, height=56, seed=7,
        request_message=_provider(atlas, drops=2, calls=calls), sleep=lambda _s: None,
    )

    assert result.atlas_png == atlas and result.job_id == "job-accepted"
    assert calls.count("create_image_pro") == 1
    assert calls.count("initialize") == 3            # session reopened after each dropped read


def test_persistent_network_failure_keeps_job_id_and_never_resubmits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    calls: list[str] = []

    with pytest.raises(PixelLabProviderError) as caught:
        generate_pixellab_pro_4x4_atlas_mcp(
            description="forest spirit", width=56, height=56, seed=7,
            request_message=_provider(_atlas_png(), drops=99, calls=calls), sleep=lambda _s: None,
        )

    assert caught.value.code == "MCP_NETWORK_ERROR" and caught.value.job_id == "job-accepted"
    assert calls.count("create_image_pro") == 1


def test_resume_polls_accepted_job_without_create(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    atlas, calls = _atlas_png(), []

    result = generate_pixellab_pro_4x4_atlas_mcp(
        description="forest spirit", width=56, height=56, seed=7, resume_job_id="job-accepted",
        request_message=_provider(atlas, drops=1, calls=calls), sleep=lambda _s: None,
        on_submission_started=lambda: pytest.fail("resume must not start a paid submission"),
    )

    assert result.atlas_png == atlas
    assert "create_image_pro" not in calls
