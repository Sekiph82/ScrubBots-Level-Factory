"""Production-owned runtime boundary for the offline generator.

The boundary temporarily intercepts standard-library socket construction and
connection helpers while protected production work runs. It does not mutate
the interpreter at import time and restores every intercepted symbol on exit.
"""

from collections.abc import Iterator
from contextlib import contextmanager
import socket
from typing import Any, NoReturn


class OfflinePolicyError(RuntimeError):
    """Raised whenever protected runtime code attempts a network operation."""


def _deny_network(*_args: Any, **_kwargs: Any) -> NoReturn:
    raise OfflinePolicyError(
        "SCRUBBOTS Pixel Art Generator V1 is offline-only; runtime network access is forbidden"
    )


@contextmanager
def offline_runtime() -> Iterator[None]:
    """Run a production operation inside a temporary offline-only boundary.

    Direct ``socket.socket.connect`` calls and ``socket.create_connection``
    resolve through the temporarily substituted module symbols and therefore
    fail before the original socket implementation can reach the OS. Local
    deterministic computation remains unaffected. The original symbols are
    restored even when the protected operation raises.
    """

    original_socket = socket.socket
    original_socket_type = getattr(socket, "SocketType", None)
    original_create_connection = socket.create_connection

    class OfflineSocket(original_socket):
        def connect(self, *_args: Any, **_kwargs: Any) -> NoReturn:
            _deny_network()

        def connect_ex(self, *_args: Any, **_kwargs: Any) -> NoReturn:
            _deny_network()

    socket.socket = OfflineSocket
    if original_socket_type is not None:
        socket.SocketType = OfflineSocket
    socket.create_connection = _deny_network
    try:
        yield
    finally:
        socket.socket = original_socket
        if original_socket_type is not None:
            socket.SocketType = original_socket_type
        socket.create_connection = original_create_connection


def guarded_network_request(*_args: object, **_kwargs: object) -> NoReturn:
    """Keep the original explicit request-denial contract for compatibility."""

    _deny_network()
