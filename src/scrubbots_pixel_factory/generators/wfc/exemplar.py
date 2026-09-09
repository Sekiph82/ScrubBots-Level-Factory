"""Validated exemplar and palette-mapping helpers for the WFC engine."""

from collections.abc import Mapping

from ...contracts import CANONICAL_PALETTE
from .model import Exemplar, WFCConfig, WFCContractError


def _ordered_palette(values: set[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(values, key=lambda value: int(value[1:])))


def canonical_palette_mapping(
    exemplar: Exemplar,
    target_palette: tuple[str, ...],
    explicit: tuple[tuple[str, str], ...] = (),
) -> tuple[tuple[str, str], ...]:
    """Return a complete, deterministic one-to-one source-to-target mapping."""

    source = exemplar.source_palette
    target = tuple(target_palette)
    if len(source) != len(target):
        raise WFCContractError("source and target palettes must have equal cardinality")
    if explicit:
        pairs = tuple(explicit)
        if len(pairs) != len(source):
            raise WFCContractError("explicit palette mapping must cover every source color exactly once")
        keys = tuple(pair[0] for pair in pairs)
        values = tuple(pair[1] for pair in pairs)
        if set(keys) != set(source) or len(set(keys)) != len(keys):
            raise WFCContractError("explicit palette mapping source IDs must match the exemplar exactly")
        if set(values) != set(target) or len(set(values)) != len(values):
            raise WFCContractError("explicit palette mapping target IDs must match the request exactly")
    else:
        pairs = tuple(zip(source, target, strict=True))
    for source_id, target_id in pairs:
        CANONICAL_PALETTE.validate_logical_id(source_id)
        CANONICAL_PALETTE.validate_logical_id(target_id)
    return tuple(sorted(pairs, key=lambda pair: int(pair[0][1:])))


def map_exemplar_pixels(
    exemplar: Exemplar,
    target_palette: tuple[str, ...],
    config: WFCConfig,
) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
    mapping = canonical_palette_mapping(exemplar, target_palette, config.palette_mapping)
    lookup = dict(mapping)
    try:
        mapped = tuple(lookup[cell] for cell in exemplar.pixels)
    except KeyError as exc:
        raise WFCContractError("exemplar contains a color outside the complete palette mapping") from exc
    return mapped, mapping
