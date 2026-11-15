"""Owner 2026-11-15: every generation carries the liked arctic atlas as style image."""
import base64
from io import BytesIO

import pytest
from PIL import Image

from scrubbots_pixel_factory import studio_extensions as extensions
from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE


def _png(size: int) -> bytes:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    image.putpixel((0, 0), CANONICAL_PALETTE.colors[0].rgb + (255,))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _provider(atlas: bytes, created: list[dict]):
    def request_message(**kwargs):
        message = kwargs["message"]
        if message.get("method") == "initialize":
            return {"jsonrpc": "2.0", "id": message["id"], "result": {"protocolVersion": "2025-11-25"}}, {"MCP-Session-Id": "s"}
        if message.get("method") == "notifications/initialized":
            return {}, {}
        name = message["params"]["name"]
        if name == "create_image_pro":
            created.append(message["params"]["arguments"])
            return {"jsonrpc": "2.0", "id": message["id"], "result": {"content": [{"type": "text", "text": "job_id: job-1"}]}}, {}
        return {"jsonrpc": "2.0", "id": message["id"], "result": {"content": [
            {"type": "image", "mimeType": "image/png", "data": base64.b64encode(atlas).decode("ascii")}]}}, {}
    return request_message


@pytest.mark.parametrize("style", [None, b"style"])
def test_style_image_is_sent_only_when_configured(monkeypatch, style):
    monkeypatch.setattr(extensions, "get_pixellab_secret", lambda: "test-token")
    created: list[dict] = []
    extensions.generate_pixellab_pro_4x4_atlas_mcp(
        description="desert reptiles", width=56, height=56, seed=7, sleep=lambda _s: None,
        request_message=_provider(_png(208), created), style_image_png=style and _png(224),
    )
    arguments = created[0]
    if style is None:
        assert "style_image_url" not in arguments and "style_copy" not in arguments
    else:
        assert arguments["style_image_url"] == "data:image/png;base64," + base64.b64encode(_png(224)).decode("ascii")
        assert arguments["style_copy"] == ["outline", "detail", "shading"]
        assert arguments["palette_name"] == "ScrubBots Palette V3"
