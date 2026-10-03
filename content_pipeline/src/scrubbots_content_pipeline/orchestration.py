"""Interface-only publish, promote, rollback, and evidence boundaries."""

from __future__ import annotations

from typing import Protocol

from .validation import DryRunReport


class PublishOrchestrator(Protocol):
    """Future coordinator contract; no live publishing implementation exists."""

    def publish(self, report: DryRunReport) -> DryRunReport:
        ...


class PromotionOrchestrator(Protocol):
    """Future promotion coordinator contract; interface only in this milestone."""

    def promote(self, report: DryRunReport) -> DryRunReport:
        ...


class RollbackOrchestrator(Protocol):
    """Future rollback coordinator contract; interface only in this milestone."""

    def rollback(self, report: DryRunReport) -> DryRunReport:
        ...


class EvidenceSink(Protocol):
    """Boundary for a later local or externally managed evidence destination."""

    def write_report(self, report: DryRunReport) -> None:
        ...
