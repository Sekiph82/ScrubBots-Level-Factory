"""Independent M04 procedural RULES generation package."""

from .colorize import ColorizedRules, color_component_sizes, colorize_canvas
from .generator import RuleShapeGenerator, recipe_names
from .model import CompositionRecipe, RecipeStep, RuleCanvas, RuleCandidate, RuleContractError
from .operations import (
    OPERATION_NAMES,
    RewriteRule,
    bounded_repeat,
    constrained_connected_growth,
    connected_components,
    contour_extraction,
    controlled_fragmentation,
    dilation,
    erosion,
    hole_carving,
    local_rewrite,
    nested_region,
    seeded_frontier_growth,
)
from .primitives import (
    PRIMITIVE_NAMES,
    apply_primitive,
    blob,
    branch,
    chamber,
    corridor,
    island,
    pocket,
    radial,
    ring,
    snake,
    spiral,
    voronoi_like,
    wave,
)
from .recipes import RECIPES, RECIPE_NAMES, recipe_for, render_recipe

__all__ = [
    "ColorizedRules", "CompositionRecipe", "OPERATION_NAMES", "PRIMITIVE_NAMES", "RECIPES", "RECIPE_NAMES", "RecipeStep", "RewriteRule", "RuleCanvas", "RuleCandidate", "RuleContractError", "RuleShapeGenerator", "apply_primitive", "blob", "bounded_repeat", "branch", "chamber", "color_component_sizes", "colorize_canvas", "constrained_connected_growth", "connected_components", "contour_extraction", "controlled_fragmentation", "corridor", "dilation", "erosion", "hole_carving", "island", "local_rewrite", "nested_region", "pocket", "radial", "recipe_for", "recipe_names", "render_recipe", "ring", "seeded_frontier_growth", "snake", "spiral", "voronoi_like", "wave",
]
