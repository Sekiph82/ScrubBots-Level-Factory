"""Production-owned runtime network boundary for the offline generator.

There is deliberately no HTTP client or socket initialization here. Future
generation code must call this boundary for any operation that could leave the
local process; M00 denies it explicitly and synchronously.
"""


class OfflinePolicyError(RuntimeError):
    """Raised whenever runtime code attempts a network operation."""


def guarded_network_request(*_args: object, **_kwargs: object) -> None:
    """Deny a runtime network request under the V1 offline-only contract."""

    raise OfflinePolicyError(
        "SCRUBBOTS Pixel Art Generator V1 is offline-only; runtime network access is forbidden"
    )
