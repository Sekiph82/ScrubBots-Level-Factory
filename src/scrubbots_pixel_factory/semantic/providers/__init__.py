"""Explicit, isolated SP02 provider bridges.

The package intentionally does not import optional SDKs.  Provider modules are
selected by the registry only when a caller explicitly requests that provider.
"""

from .registry import (
    ProviderDescriptor,
    available_provider_ids,
    create_provider,
    get_provider_descriptor,
    provider_registry,
)

__all__ = [
    "ProviderDescriptor",
    "available_provider_ids",
    "create_provider",
    "get_provider_descriptor",
    "provider_registry",
]
