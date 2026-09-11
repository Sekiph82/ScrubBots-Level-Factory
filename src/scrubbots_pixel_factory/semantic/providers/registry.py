"""Deterministic explicit provider registry with lazy provider imports."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..contracts import SemanticProviderError


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    provider_id: str
    adapter_version: str
    config_version: str
    _factory: Callable[..., object]

    def create(self, **kwargs: Any) -> object:
        return self._factory(**kwargs)


def _magnific_factory(**kwargs: Any) -> object:
    from .magnific import MagnificProvider

    return MagnificProvider(**kwargs)


def _pixellab_factory(**kwargs: Any) -> object:
    from .pixellab import PixelLabProvider

    return PixelLabProvider(**kwargs)


_REGISTRY = {
    "MAGNIFIC": ProviderDescriptor("MAGNIFIC", "magnific-adapter-v1", "1", _magnific_factory),
    "PIXELLAB": ProviderDescriptor("PIXELLAB", "pixellab-adapter-v1", "1", _pixellab_factory),
}


def provider_registry() -> tuple[ProviderDescriptor, ...]:
    """Return registrations in a stable, non-alphabetically surprising order."""

    return tuple(_REGISTRY[key] for key in ("MAGNIFIC", "PIXELLAB"))


def available_provider_ids() -> tuple[str, ...]:
    return tuple(item.provider_id for item in provider_registry())


def get_provider_descriptor(provider_id: str) -> ProviderDescriptor:
    if type(provider_id) is not str or provider_id not in _REGISTRY:
        raise SemanticProviderError(f"unknown semantic provider: {provider_id!r}")
    return _REGISTRY[provider_id]


def create_provider(provider_id: str, **kwargs: Any) -> object:
    return get_provider_descriptor(provider_id).create(**kwargs)


resolve_provider = create_provider


__all__ = [
    "ProviderDescriptor",
    "available_provider_ids",
    "create_provider",
    "get_provider_descriptor",
    "provider_registry",
    "resolve_provider",
]
