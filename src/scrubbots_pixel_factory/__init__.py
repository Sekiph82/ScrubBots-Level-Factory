"""Offline-only SCRUBBOTS Pixel Art Generator V1 foundation.

M00 intentionally exposes policy and local smoke utilities only. Generator
families and SCRUBBOTS contract modules belong to later milestones.
"""

from .offline import OfflinePolicyError, guarded_network_request
from .local import deterministic_digest

__all__ = [
    "OfflinePolicyError",
    "guarded_network_request",
    "deterministic_digest",
]

__version__ = "0.1.0"
OFFLINE_ONLY = True
