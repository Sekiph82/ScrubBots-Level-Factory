from __future__ import annotations

from dataclasses import dataclass
import hashlib

from scrubbots_pixel_factory.output.png import decode_logical_png, encode_logical_png
from scrubbots_pixel_factory.qa import (
    AuthorityIdentity,
    M09RoundTripReceipt,
    StageDisposition,
    evaluate_m09_round_trip,
)


AUTHORITY = AuthorityIdentity(
    "https://github.com/Sekiph82/Scrubbots",
    "b" * 40,
    "scripts/level_art/m09_importer.gd",
    "M09_EXACT_PIXEL_ROUND_TRIP_V1",
)


@dataclass(frozen=True)
class Provider:
    mutate: bool = False

    def round_trip(self, source_png: bytes) -> M09RoundTripReceipt:
        decoded = decode_logical_png(source_png)
        cells = decoded.cells[:-1] + ("C04",) if self.mutate else decoded.cells
        return M09RoundTripReceipt(
            StageDisposition.PASS,
            AUTHORITY,
            hashlib.sha256(source_png).hexdigest(),
            hashlib.sha256(encode_logical_png(decoded.width, decoded.height, cells)).hexdigest(),
            decoded.width,
            decoded.height,
            decoded.cells,
            cells,
            "1" * 64,
            "exact M09 row-major round-trip receipt",
        )


def _png() -> bytes:
    cells = tuple(("C01", "C02", "C03", "C01")[index % 4] for index in range(20 * 59))
    return encode_logical_png(20, 59, cells)


def test_exact_rectangular_round_trip_preserves_repeated_palette_order_and_bytes() -> None:
    source = _png()
    before = bytes(source)
    report = evaluate_m09_round_trip(source, provider=Provider(), main_game_authority=AUTHORITY)
    assert report.disposition is StageDisposition.PASS
    assert report.width == 20 and report.height == 59
    assert report.source_grid_digest == report.reconstructed_grid_digest
    assert source == before
    assert report.digest() == report.digest()


def test_authority_drift_and_cell_mutation_fail_closed() -> None:
    drifted = AuthorityIdentity(AUTHORITY.repository, "c" * 40, AUTHORITY.source_path, AUTHORITY.contract_version)

    class DriftedProvider(Provider):
        def round_trip(self, source_png: bytes) -> M09RoundTripReceipt:
            receipt = super().round_trip(source_png)
            return M09RoundTripReceipt(receipt.disposition, drifted, receipt.source_png_sha256, receipt.reconstructed_png_sha256, receipt.width, receipt.height, receipt.source_cells, receipt.reconstructed_cells, receipt.evidence_digest, receipt.reason)

    report = evaluate_m09_round_trip(_png(), provider=DriftedProvider(), main_game_authority=AUTHORITY)
    assert report.disposition is StageDisposition.ERROR
    changed = evaluate_m09_round_trip(_png(), provider=Provider(mutate=True), main_game_authority=AUTHORITY)
    assert changed.disposition is StageDisposition.FAIL


def test_missing_main_game_capability_is_unavailable_not_a_factory_reimplementation() -> None:
    report = evaluate_m09_round_trip(_png(), provider=None, main_game_authority=AUTHORITY)
    assert report.disposition is StageDisposition.UNAVAILABLE
    assert report.reconstructed_png_sha256 is None
