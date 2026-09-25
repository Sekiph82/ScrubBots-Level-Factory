"""Receipt-bound M09 exact logical-art round-trip verification.

The importer remains an external main-game authority.  Factory code verifies
the receipt's identity and exact row-major result; it does not import or
reimplement main-game conversion semantics.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from typing import Protocol, runtime_checkable

from ..contracts import CANONICAL_PALETTE
from .unified import AuthorityIdentity, LevelDataIdentity, QAContractError, StageDisposition, _canonical_bytes, _digest, _sha


M09_ROUND_TRIP_SCHEMA = "scrubbots-m09-logical-art-round-trip"
M09_ROUND_TRIP_VERSION = 1


def _text(value: object, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise QAContractError(f"{label} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class M09RoundTripReceipt:
    """Typed evidence returned by an exact main-game M09 provider."""

    disposition: StageDisposition
    authority: AuthorityIdentity
    source_png_sha256: str
    reconstructed_png_sha256: str
    width: int
    height: int
    source_cells: tuple[str, ...]
    reconstructed_cells: tuple[str, ...]
    evidence_digest: str
    reason: str
    importer_id: str = "main-game-m09-importer"
    importer_version: str = "M09_EXACT_PIXEL_ROUND_TRIP_V1"
    level_data_bytes: bytes | None = None
    level_data_sha256: str | None = None
    first_seen_palette: tuple[str, ...] | None = None
    source_cell_indices: tuple[int, ...] | None = None
    reconstructed_cell_indices: tuple[int, ...] | None = None
    reconstructed_logical_pixels: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, StageDisposition):
            raise QAContractError("M09 round-trip disposition is malformed")
        if not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("M09 round-trip authority is malformed")
        _sha(self.source_png_sha256, "M09 source PNG SHA-256")
        _sha(self.reconstructed_png_sha256, "M09 reconstructed PNG SHA-256")
        _sha(self.evidence_digest, "M09 evidence digest")
        if type(self.width) is not int or type(self.height) is not int or self.width < 1 or self.height < 1:
            raise QAContractError("M09 round-trip dimensions must be positive integers")
        if type(self.source_cells) is not tuple or type(self.reconstructed_cells) is not tuple:
            raise QAContractError("M09 round-trip cells must be immutable tuples")
        if len(self.source_cells) != self.width * self.height or len(self.reconstructed_cells) != self.width * self.height:
            raise QAContractError("M09 round-trip cell count does not match dimensions")
        try:
            CANONICAL_PALETTE.used_ids(self.source_cells)
            CANONICAL_PALETTE.used_ids(self.reconstructed_cells)
        except (TypeError, ValueError) as exc:
            raise QAContractError("M09 round-trip cells must be canonical C01..C16 IDs") from exc
        _text(self.reason, "M09 round-trip reason")
        _text(self.importer_id, "M09 importer_id")
        _text(self.importer_version, "M09 importer_version")
        if self.level_data_bytes is not None and type(self.level_data_bytes) is not bytes:
            raise QAContractError("M09 LevelData bytes must be immutable bytes")
        if self.level_data_sha256 is not None:
            _sha(self.level_data_sha256, "M09 LevelData SHA-256")
            if self.level_data_bytes is not None and hashlib.sha256(self.level_data_bytes).hexdigest() != self.level_data_sha256:
                raise QAContractError("M09 LevelData hash does not match exact bytes")
        for values, label in ((self.first_seen_palette, "M09 first-seen palette"), (self.source_cell_indices, "M09 source cell indices"), (self.reconstructed_cell_indices, "M09 reconstructed cell indices"), (self.reconstructed_logical_pixels, "M09 reconstructed logical pixels")):
            if values is not None and type(values) is not tuple:
                raise QAContractError(f"{label} must be an immutable tuple")
        if self.first_seen_palette is not None:
            if tuple(dict.fromkeys(self.first_seen_palette)) != self.first_seen_palette:
                raise QAContractError("M09 first-seen palette contains duplicates")
            if any(cell not in CANONICAL_PALETTE.ids for cell in self.first_seen_palette):
                raise QAContractError("M09 first-seen palette contains a foreign cell ID")
        for values, label in ((self.source_cell_indices, "M09 source cell indices"), (self.reconstructed_cell_indices, "M09 reconstructed cell indices")):
            if values is not None and (len(values) != self.width * self.height or any(type(index) is not int or index < 0 for index in values)):
                raise QAContractError(f"{label} are malformed")
        if self.reconstructed_logical_pixels is not None and len(self.reconstructed_logical_pixels) != self.width * self.height:
            raise QAContractError("M09 reconstructed logical pixels do not match dimensions")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": M09_ROUND_TRIP_SCHEMA,
            "version": M09_ROUND_TRIP_VERSION,
            "disposition": self.disposition.value,
            "authority": self.authority.canonical_dict(),
            "source_png_sha256": self.source_png_sha256,
            "reconstructed_png_sha256": self.reconstructed_png_sha256,
            "dimensions": {"width": self.width, "height": self.height},
            "source_cells": list(self.source_cells),
            "reconstructed_cells": list(self.reconstructed_cells),
            "evidence_digest": self.evidence_digest,
            "reason": self.reason,
            "importer_id": self.importer_id,
            "importer_version": self.importer_version,
            "level_data_sha256": self.level_data_sha256,
            "first_seen_palette": None if self.first_seen_palette is None else list(self.first_seen_palette),
            "source_cell_indices": None if self.source_cell_indices is None else list(self.source_cell_indices),
            "reconstructed_cell_indices": None if self.reconstructed_cell_indices is None else list(self.reconstructed_cell_indices),
            "reconstructed_logical_pixels": None if self.reconstructed_logical_pixels is None else list(self.reconstructed_logical_pixels),
        }


@runtime_checkable
class MainGameM09RoundTripProvider(Protocol):
    def round_trip(self, source_png: bytes) -> M09RoundTripReceipt:
        """Return exact-source M09 importer/exporter evidence."""


@dataclass(frozen=True, slots=True)
class M09RoundTripReport:
    disposition: StageDisposition
    authority: AuthorityIdentity
    source_png_sha256: str
    reconstructed_png_sha256: str | None
    width: int | None
    height: int | None
    source_grid_digest: str | None
    reconstructed_grid_digest: str | None
    evidence_digest: str
    reason: str
    schema: str = M09_ROUND_TRIP_SCHEMA
    version: int = M09_ROUND_TRIP_VERSION
    level_data_sha256: str | None = None
    first_seen_palette_digest: str | None = None
    source_cell_indices_digest: str | None = None
    reconstructed_cell_indices_digest: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.disposition, StageDisposition) or not isinstance(self.authority, AuthorityIdentity):
            raise QAContractError("M09 report identity is malformed")
        _sha(self.source_png_sha256, "M09 report source PNG SHA-256")
        _sha(self.evidence_digest, "M09 report evidence digest")
        for value, label in ((self.reconstructed_png_sha256, "reconstructed PNG SHA-256"), (self.source_grid_digest, "source grid digest"), (self.reconstructed_grid_digest, "reconstructed grid digest")):
            if value is not None:
                _sha(value, f"M09 report {label}")
        for value, label in ((self.level_data_sha256, "LevelData SHA-256"), (self.first_seen_palette_digest, "first-seen palette digest"), (self.source_cell_indices_digest, "source cell-indices digest"), (self.reconstructed_cell_indices_digest, "reconstructed cell-indices digest")):
            if value is not None:
                _sha(value, f"M09 report {label}")
        if self.schema != M09_ROUND_TRIP_SCHEMA or self.version != M09_ROUND_TRIP_VERSION:
            raise QAContractError("unsupported M09 round-trip schema/version")
        _text(self.reason, "M09 report reason")

    def canonical_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "version": self.version,
            "disposition": self.disposition.value,
            "authority": self.authority.canonical_dict(),
            "source_png_sha256": self.source_png_sha256,
            "reconstructed_png_sha256": self.reconstructed_png_sha256,
            "dimensions": None if self.width is None or self.height is None else {"width": self.width, "height": self.height},
            "source_grid_digest": self.source_grid_digest,
            "reconstructed_grid_digest": self.reconstructed_grid_digest,
            "evidence_digest": self.evidence_digest,
            "reason": self.reason,
            "level_data_sha256": self.level_data_sha256,
            "first_seen_palette_digest": self.first_seen_palette_digest,
            "source_cell_indices_digest": self.source_cell_indices_digest,
            "reconstructed_cell_indices_digest": self.reconstructed_cell_indices_digest,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _unavailable(source_sha256: str, authority: AuthorityIdentity | None, reason: str) -> M09RoundTripReport:
    selected = authority or AuthorityIdentity("Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/M09", "UNAVAILABLE")
    evidence = _digest({"stage": "M09_ROUND_TRIP", "source_png_sha256": source_sha256, "authority": selected.canonical_dict(), "reason": reason})
    return M09RoundTripReport(StageDisposition.UNAVAILABLE, selected, source_sha256, None, None, None, None, None, evidence, reason)


def evaluate_m09_round_trip(
    source_png: bytes,
    *,
    provider: MainGameM09RoundTripProvider | object | None,
    main_game_authority: AuthorityIdentity | None,
    level_data: LevelDataIdentity | None = None,
) -> M09RoundTripReport:
    """Verify a provider receipt's exact pixel/cell identity without mutation."""

    if not isinstance(source_png, bytes):
        raise QAContractError("source logical PNG must be immutable bytes")
    source_sha256 = hashlib.sha256(source_png).hexdigest()
    if provider is None:
        return _unavailable(source_sha256, main_game_authority, "exact main-game M09 round-trip capability is unavailable")
    try:
        method = getattr(provider, "round_trip", None)
        if not callable(method):
            raise QAContractError("M09 provider must expose round_trip")
        receipt = method(source_png)
        if not isinstance(receipt, M09RoundTripReceipt):
            raise QAContractError("M09 provider returned an untyped receipt")
        if main_game_authority is not None and receipt.authority != main_game_authority:
            return M09RoundTripReport(StageDisposition.ERROR, main_game_authority, source_sha256, None, None, None, None, None, _digest({"error": "AUTHORITY_DRIFT", "receipt": receipt.canonical_dict()}), "M09 provider authority does not match the requested exact main-game authority")
        if receipt.source_png_sha256 != source_sha256:
            return M09RoundTripReport(StageDisposition.ERROR, receipt.authority, source_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, None, None, _digest({"error": "SOURCE_HASH_MISMATCH", "receipt": receipt.canonical_dict()}), "M09 receipt is bound to different source PNG bytes")
        if level_data is not None:
            if receipt.level_data_bytes is None or receipt.level_data_sha256 is None or receipt.level_data_sha256 != level_data.level_data_sha256 or receipt.level_data_bytes != level_data.level_data_bytes:
                return M09RoundTripReport(StageDisposition.ERROR, receipt.authority, source_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, None, None, _digest({"error": "LEVELDATA_IDENTITY_DRIFT", "receipt": receipt.canonical_dict()}), "M09 receipt is not bound to the exact generated LevelData bytes")
            expected_palette = tuple(dict.fromkeys(receipt.source_cells))
            if receipt.first_seen_palette is None or receipt.first_seen_palette != expected_palette:
                return M09RoundTripReport(StageDisposition.ERROR, receipt.authority, source_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, None, None, _digest({"error": "PALETTE_ORDER_DRIFT", "receipt": receipt.canonical_dict()}), "M09 receipt does not bind first-seen palette order")
            if receipt.source_cell_indices is None or receipt.reconstructed_cell_indices is None:
                return M09RoundTripReport(StageDisposition.ERROR, receipt.authority, source_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, None, None, _digest({"error": "CELL_INDEX_IDENTITY_UNAVAILABLE", "receipt": receipt.canonical_dict()}), "M09 receipt does not bind row-major LevelData cell indices")
            expected_source_indices = tuple(receipt.first_seen_palette.index(cell) for cell in receipt.source_cells)
            expected_reconstructed_indices = tuple(receipt.first_seen_palette.index(cell) for cell in receipt.reconstructed_cells)
            if receipt.source_cell_indices != expected_source_indices or receipt.reconstructed_cell_indices != expected_reconstructed_indices:
                return M09RoundTripReport(StageDisposition.ERROR, receipt.authority, source_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, None, None, _digest({"error": "CELL_INDEX_DRIFT", "receipt": receipt.canonical_dict()}), "M09 receipt cell indices are inconsistent with first-seen palette order")
            if receipt.reconstructed_logical_pixels is None or receipt.reconstructed_logical_pixels != receipt.reconstructed_cells:
                return M09RoundTripReport(StageDisposition.ERROR, receipt.authority, source_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, None, None, _digest({"error": "RECONSTRUCTED_PIXEL_DRIFT", "receipt": receipt.canonical_dict()}), "M09 reconstructed logical pixels are not cross-bound to reconstructed cells")
        source_grid_digest = _digest({"width": receipt.width, "height": receipt.height, "row_major_cells": list(receipt.source_cells)})
        reconstructed_grid_digest = _digest({"width": receipt.width, "height": receipt.height, "row_major_cells": list(receipt.reconstructed_cells)})
        exact = receipt.source_cells == receipt.reconstructed_cells
        disposition = receipt.disposition if exact else StageDisposition.FAIL
        reason = receipt.reason if exact else "M09 round-trip row-major logical cell identity changed"
        palette_digest = _digest(list(receipt.first_seen_palette)) if receipt.first_seen_palette is not None else None
        source_index_digest = _digest(list(receipt.source_cell_indices)) if receipt.source_cell_indices is not None else None
        reconstructed_index_digest = _digest(list(receipt.reconstructed_cell_indices)) if receipt.reconstructed_cell_indices is not None else None
        return M09RoundTripReport(disposition, receipt.authority, source_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, source_grid_digest, reconstructed_grid_digest, receipt.evidence_digest, reason, level_data_sha256=receipt.level_data_sha256, first_seen_palette_digest=palette_digest, source_cell_indices_digest=source_index_digest, reconstructed_cell_indices_digest=reconstructed_index_digest)
    except Exception as exc:
        authority = main_game_authority or AuthorityIdentity("Sekiph82/Scrubbots", "UNAVAILABLE", "main-game/M09", "UNAVAILABLE")
        return M09RoundTripReport(StageDisposition.ERROR, authority, source_sha256, None, None, None, None, None, _digest({"error": str(exc), "source_png_sha256": source_sha256}), f"M09 round-trip provider error: {exc}")


__all__ = [
    "M09_ROUND_TRIP_SCHEMA",
    "M09_ROUND_TRIP_VERSION",
    "M09RoundTripReceipt",
    "M09RoundTripReport",
    "MainGameM09RoundTripProvider",
    "evaluate_m09_round_trip",
]
