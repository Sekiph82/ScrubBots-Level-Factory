"""2026-11-14 11:07: PixelLab batch row 22/100 stopped on one dropped connection while
opening the MCP session (no paid request), and the real cause was thrown away."""
import io
from urllib.error import URLError

import pytest

from scrubbots_pixel_factory import studio_extensions as se


class _Response(io.BytesIO):
    headers = {"Content-Type": "application/json"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _patch(monkeypatch, failures):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request)
        if len(calls) <= failures:
            raise URLError(ConnectionResetError(10054, "An existing connection was forcibly closed by the remote host"))
        return _Response(b'{"jsonrpc":"2.0","id":1,"result":{}}')

    monkeypatch.setattr(se, "urlopen", fake_urlopen)
    monkeypatch.setattr(se.time, "sleep", lambda _s: None)
    return calls


def test_free_request_survives_one_dropped_connection(monkeypatch):
    calls = _patch(monkeypatch, failures=1)
    response, _ = se._mcp_http_request(secret="x", message={"jsonrpc": "2.0", "id": 1, "method": "initialize"}, session_id=None, protocol_version=None)
    assert response["result"] == {} and len(calls) == 2


def test_persistent_failure_keeps_the_real_cause(monkeypatch):
    calls = _patch(monkeypatch, failures=99)
    with pytest.raises(se.PixelLabProviderError) as error:
        se._mcp_http_request(secret="x", message={"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id="s", protocol_version="v")
    assert error.value.code == "MCP_NETWORK_ERROR" and len(calls) == 3
    assert "ConnectionResetError" in str(error.value) and "notifications/initialized" in str(error.value)


def test_paid_submission_is_never_resent(monkeypatch):
    calls = _patch(monkeypatch, failures=99)
    message = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "create_image_pro", "arguments": {}}}
    with pytest.raises(se.PixelLabProviderError) as error:
        se._mcp_http_request(secret="x", message=message, session_id="s", protocol_version="v")
    assert error.value.code == "SUBMISSION_UNKNOWN" and len(calls) == 1
