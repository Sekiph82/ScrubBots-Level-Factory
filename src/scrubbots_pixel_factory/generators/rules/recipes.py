"""Immutable M04 recipe catalog and deterministic layered composition."""

from types import MappingProxyType

from ...core import DeterministicRNG
from .model import CompositionRecipe, RecipeStep, RuleCanvas, RuleContractError
from .operations import connected_components, contour_extraction, dilation, local_rewrite, RewriteRule
from .primitives import apply_primitive


RECIPE_NAMES = (
    "SYMMETRY", "ORGANIC", "CENTRAL_SUBJECT", "MULTI_ISLAND",
    "BORDER_FRAME_EMBLEM", "DENSE_FULL_BOARD", "SPARSE_NEGATIVE_SPACE",
)


def _step(operation: str, domain: str, **parameters: int | str | bool) -> RecipeStep:
    return RecipeStep(operation, tuple(parameters.items()), domain)


_RECIPES = {
    "SYMMETRY": CompositionRecipe("SYMMETRY", 1, (
        _step("RING", "geometry/ring", radius=0, thickness=1),
        _step("RADIAL", "geometry/radial", rays=8, length=0),
    ), 4, 70, 96),
    "ORGANIC": CompositionRecipe("ORGANIC", 1, (
        _step("BLOB", "geometry/blob", target=0),
        _step("BRANCH", "geometry/branch", depth=0, branch_count=3),
        _step("LOCAL_REWRITE", "operations/rewrite", rule="FILL_NOTCH"),
    ), 10, 80, 90),
    "CENTRAL_SUBJECT": CompositionRecipe("CENTRAL_SUBJECT", 1, (
        _step("CHAMBER", "geometry/chamber", chamber_width=0, chamber_height=0),
        _step("RING", "geometry/emblem-ring", radius=0, thickness=1),
        _step("POCKET", "geometry/emblem-pocket", size=2),
    ), 10, 78, 90),
    "MULTI_ISLAND": CompositionRecipe("MULTI_ISLAND", 1, (
        _step("ISLAND", "geometry/island/1", target=0),
        _step("ISLAND", "geometry/island/2", target=0),
        _step("ISLAND", "geometry/island/3", target=0),
    ), 6, 58, 94),
    "BORDER_FRAME_EMBLEM": CompositionRecipe("BORDER_FRAME_EMBLEM", 1, (
        _step("FRAME", "geometry/frame", thickness=1),
        _step("CHAMBER", "geometry/frame-emblem", chamber_width=0, chamber_height=0),
        _step("RING", "geometry/frame-ring", radius=0, thickness=1),
    ), 20, 82, 82),
    "DENSE_FULL_BOARD": CompositionRecipe("DENSE_FULL_BOARD", 1, (
        _step("WAVE", "geometry/wave", period=5, amplitude=2),
        _step("DILATE", "operations/dense-dilation", iterations=6),
        _step("RADIAL", "geometry/dense-radial", rays=8, length=0),
    ), 25, 92, 82),
    "SPARSE_NEGATIVE_SPACE": CompositionRecipe("SPARSE_NEGATIVE_SPACE", 1, (
        _step("CORRIDOR", "geometry/sparse-corridor", width_cells=1),
        _step("ISLAND", "geometry/sparse-island/1", target=0),
        _step("ISLAND", "geometry/sparse-island/2", target=0),
    ), 6, 48, 94),
}

RECIPES = MappingProxyType(_RECIPES)


def recipe_for(style: str | None, rng: DeterministicRNG) -> CompositionRecipe:
    if style is None:
        name = rng.child("recipe-selection").choice(RECIPE_NAMES)
        return RECIPES[name]
    if style not in RECIPES:
        raise RuleContractError("style must be one of the seven RULES recipes")
    return RECIPES[style]


def _frame(canvas: RuleCanvas, thickness: int = 1) -> set[int]:
    cells = set()
    for y in range(canvas.height):
        for x in range(canvas.width):
            if x < thickness or y < thickness or x >= canvas.width - thickness or y >= canvas.height - thickness:
                cells.add(y * canvas.width + x)
    canvas.mark_many(cells, "frame", protected=True)
    return cells


def _safe_island_center(canvas: RuleCanvas, slot: int) -> tuple[int, int]:
    positions = (
        (canvas.width // 4, canvas.height // 4),
        (canvas.width * 3 // 4, canvas.height // 4),
        (canvas.width // 2, canvas.height * 3 // 4),
    )
    return positions[slot % len(positions)]


def render_recipe(recipe: CompositionRecipe, width: int, height: int, rng: DeterministicRNG) -> RuleCanvas:
    if not isinstance(rng, DeterministicRNG):
        raise RuleContractError("recipe rendering requires the project DeterministicRNG")
    canvas = RuleCanvas(width, height)
    for layer_index, step in enumerate(recipe.layers):
        stream = rng.child(step.domain)
        operation = step.operation
        params = dict(step.parameters)
        if operation == "FRAME":
            thickness = int(params["thickness"])
            if recipe.recipe_id == "BORDER_FRAME_EMBLEM":
                thickness = 1 + stream.randbelow(2)
            _frame(canvas, thickness)
        elif operation == "RING":
            radius = max(2, min(width, height) // 4) if int(params["radius"]) == 0 else int(params["radius"])
            if recipe.recipe_id in {"SYMMETRY", "CENTRAL_SUBJECT", "BORDER_FRAME_EMBLEM"}:
                radius = max(2, min(width, height) // 4 - 1 + stream.randbelow(3))
            apply_primitive(canvas, "RING", stream, radius=radius, thickness=int(params["thickness"]))
        elif operation == "RADIAL":
            length = max(2, min(width, height) // 3) if int(params["length"]) == 0 else int(params["length"])
            rays = int(params["rays"])
            if recipe.recipe_id in {"SYMMETRY", "DENSE_FULL_BOARD"}:
                rays = 6 + stream.randbelow(5)
            apply_primitive(canvas, "RADIAL", stream, rays=rays, length=length)
        elif operation == "BLOB":
            target = max(12, width * height // 7) if int(params["target"]) == 0 else int(params["target"])
            apply_primitive(canvas, "BLOB", stream, target=target)
        elif operation == "BRANCH":
            apply_primitive(canvas, "BRANCH", stream, depth=min(height - 2, max(3, int(params["depth"]) or height // 5)), branch_count=int(params["branch_count"]))
        elif operation == "CHAMBER":
            cw = max(5, width // 2) if int(params["chamber_width"]) == 0 else int(params["chamber_width"])
            ch = max(5, height // 2) if int(params["chamber_height"]) == 0 else int(params["chamber_height"])
            if recipe.recipe_id in {"CENTRAL_SUBJECT", "BORDER_FRAME_EMBLEM"}:
                cw = max(5, min(width - 2, width // 2 - 2 + stream.randbelow(5)))
                ch = max(5, min(height - 2, height // 2 - 2 + stream.randbelow(5)))
            apply_primitive(canvas, "CHAMBER", stream, chamber_width=cw, chamber_height=ch)
        elif operation == "POCKET":
            size = int(params["size"])
            if recipe.recipe_id == "CENTRAL_SUBJECT":
                size = 2 + stream.randbelow(3)
            apply_primitive(canvas, "POCKET", stream, size=size)
        elif operation == "ISLAND":
            slot = layer_index - 1 if recipe.recipe_id == "MULTI_ISLAND" else layer_index
            apply_primitive(canvas, "ISLAND", stream, target=max(6, width * height // 35), center=_safe_island_center(canvas, slot))
        elif operation == "CORRIDOR":
            apply_primitive(canvas, "CORRIDOR", stream, width_cells=int(params["width_cells"]))
        elif operation == "WAVE":
            period = int(params["period"])
            amplitude = int(params["amplitude"])
            if recipe.recipe_id == "DENSE_FULL_BOARD":
                period = 4 + stream.randbelow(4)
                amplitude = 1 + stream.randbelow(3)
            apply_primitive(canvas, "WAVE", stream, period=period, amplitude=amplitude)
        elif operation == "DILATE":
            iterations = int(params["iterations"])
            if recipe.recipe_id == "DENSE_FULL_BOARD":
                iterations = 4 + stream.randbelow(3)
            dilation(canvas, set(canvas.occupied), iterations, label="dense")
        elif operation == "LOCAL_REWRITE":
            local_rewrite(canvas, RewriteRule(str(params["rule"])), label="rewrite")
        else:
            raise RuleContractError(f"unknown recipe operation: {operation}")

    if recipe.recipe_id == "ORGANIC":
        # The blob and branch are independent layers; bridge their nearest
        # deterministic cells so the recipe's organic subject is one structure.
        components = connected_components(canvas.occupied, canvas)
        for component in components[1:]:
            start = min(components[0])
            end = min(component)
            sx, sy = canvas.coord(start)
            ex, ey = canvas.coord(end)
            for x in range(min(sx, ex), max(sx, ex) + 1):
                canvas.mark(canvas.index(x, sy), "organic-bridge")
            for y in range(min(sy, ey), max(sy, ey) + 1):
                canvas.mark(canvas.index(ex, y), "organic-bridge")

    # Exact geometry-to-color fidelity requires the negative-space base region
    # to obey the same minimum component contract as foreground regions. Seal
    # only unprotected one-cell negative islands; these cells are surrounded by
    # occupied geometry and therefore cannot change the recipe silhouette's
    # connected structure.
    for component in connected_components(canvas.negative, canvas):
        if len(component) == 1 and component[0] not in canvas.protected_negative:
            canvas.mark(component[0], "negative-seal")

    # Stable semantic labels are retained for review and coloring. Region labels
    # are deterministic and are never derived from unordered iteration.
    contour = contour_extraction(canvas, set(canvas.occupied))
    for index in sorted(contour):
        if index not in canvas.protected_occupied:
            canvas.set_region(index, "OUTLINE")
    for index in sorted(set(canvas.occupied) - contour):
        if index not in canvas.protected_occupied:
            canvas.set_region(index, "BODY")
    if recipe.recipe_id == "CENTRAL_SUBJECT":
        canvas.protect_occupied(set(canvas.occupied), "CENTRAL_SUBJECT")
    elif recipe.recipe_id == "BORDER_FRAME_EMBLEM":
        opening = min(canvas.negative)
        canvas.protect_negative({opening})
    return canvas
