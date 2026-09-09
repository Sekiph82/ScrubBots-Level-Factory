"""Original deterministic MASK / sprite generation for SCRUBBOTS."""

from .colorize import (
    ColorRole,
    ColorRoleAssignment,
    ColorizedMask,
    color_component_sizes,
    colorize_mask,
    colorize_with_roles,
)
from .engine import MaskContractError, resolve_mask
from .engine import classify_coordinates, symmetry_orbits
from .model import MaskCellState, MaskConfig, MaskDefinition, ResolvedMask, SymmetryMode
from .templates import FAMILY_NAMES, TemplateFamily, preferred_symmetry, template_for
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
    "ColorRole",
    "ColorRoleAssignment",
    "ColorizedMask",
    "color_component_sizes",
    "classify_coordinates",
    "colorize_mask",
    "colorize_with_roles",
    "preferred_symmetry",
    "resolve_mask",
    "symmetry_orbits",
    "template_for",
]
