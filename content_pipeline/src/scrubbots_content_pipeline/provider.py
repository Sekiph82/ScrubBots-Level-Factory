"""Provider boundary declarations; no provider implementation is shipped."""

from __future__ import annotations

from typing import Protocol

from .config import Environment
from .validation import DryRunReport


class ProviderAdapter(Protocol):
    """Future provider operations, intentionally interface-only in this task."""

    def validate(self, environment: Environment) -> DryRunReport:
        """Describe provider-side validation without changing remote state."""
        ...

    def publish(self, report: DryRunReport) -> None:
        """Reserved interface; no implementation is available in this milestone."""
        ...

    def promote(self, report: DryRunReport) -> None:
        """Reserved interface; no implementation is available in this milestone."""
        ...

    def rollback(self, report: DryRunReport) -> None:
        """Reserved interface; no implementation is available in this milestone."""
        ...
