"""Original deterministic MASK / sprite generation for SCRUBBOTS."""

from .colorize import colorize_mask
from .engine import MaskContractError, resolve_mask
from .engine import classify_coordinates, symmetry_orbits
from .model import MaskCellState, MaskConfig, MaskDefinition, ResolvedMask, SymmetryMode
from .templates import FAMILY_NAMES, TemplateFamily, template_for
from .generator import MaskSpriteGenerator
from .generator import MaskCandidate

__all__ = [
    "FAMILY_NAMES",
    "MaskCellState",
    "MaskConfig",
    "MaskContractError",
    "MaskDefinition",
    "MaskCandidate",
    "MaskSpriteGenerator",
    "ResolvedMask",
    "SymmetryMode",
    "TemplateFamily",
    "classify_coordinates",
    "colorize_mask",
    "resolve_mask",
    "symmetry_orbits",
    "template_for",
]
