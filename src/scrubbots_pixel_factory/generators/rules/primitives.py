"""Project-owned integer-grid primitives used by the M04 RULES engine."""

from collections.abc import Iterable

from ...core import DeterministicRNG
from .model import RuleCanvas, RuleContractError


PRIMITIVE_NAMES = (
    "BLOB", "ISLAND", "RING", "CORRIDOR", "POCKET", "SNAKE", "BRANCH",
    "CHAMBER", "SPIRAL", "WAVE", "RADIAL", "VORONOI",
)


def _validate_size(width: int, height: int) -> None:
    if isinstance(width, bool) or isinstance(height, bool) or not isinstance(width, int) or not isinstance(height, int) or width < 3 or height < 3:
        raise RuleContractError("primitive dimensions must be integers of at least 3x3")


def _center(width: int, height: int, rng: DeterministicRNG, margin: int = 2) -> tuple[int, int]:
    return (
        margin + rng.randbelow(max(1, width - 2 * margin)),
        margin + rng.randbelow(max(1, height - 2 * margin)),
    )


def _neighbors(index: int, width: int, height: int) -> tuple[int, ...]:
    x, y = index % width, index // width
    values = []
    if x:
        values.append(index - 1)
    if x + 1 < width:
        values.append(index + 1)
    if y:
        values.append(index - width)
    if y + 1 < height:
        values.append(index + width)
    return tuple(values)


def _bounded_growth(seed: int, width: int, height: int, target: int, rng: DeterministicRNG, allowed: set[int] | None = None) -> set[int]:
    available = set(range(width * height)) if allowed is None else set(allowed)
    if seed not in available or target < 1:
        raise RuleContractError("primitive seed/target is invalid")
    region = {seed}
    for _ in range(max(0, target - 1)):
        frontier = sorted({neighbor for index in region for neighbor in _neighbors(index, width, height) if neighbor in available and neighbor not in region})
        if not frontier:
            break
        region.add(rng.choice(frontier))
    return region


def blob(width: int, height: int, rng: DeterministicRNG, *, target: int | None = None) -> set[int]:
    _validate_size(width, height)
    center = rng.child("center")
    x, y = _center(width, height, center)
    maximum = max(6, min(width * height // 3, (width + height) * 2))
    size = target if target is not None else 8 + rng.randbelow(maximum - 7)
    return _bounded_growth(y * width + x, width, height, max(2, min(size, width * height)), rng.child("growth"))


def island(width: int, height: int, rng: DeterministicRNG, *, target: int | None = None, center: tuple[int, int] | None = None) -> set[int]:
    _validate_size(width, height)
    x, y = center or _center(width, height, rng.child("center"), margin=2)
    size = max(2, min(target if target is not None else 10 + rng.randbelow(12), width * height // 4))
    return _bounded_growth(y * width + x, width, height, size, rng.child("growth"))


def ring(width: int, height: int, rng: DeterministicRNG, *, radius: int | None = None, thickness: int = 1) -> set[int]:
    _validate_size(width, height)
    if isinstance(thickness, bool) or not isinstance(thickness, int) or not 1 <= thickness <= 3:
        raise RuleContractError("ring thickness must be 1..3")
    cx, cy = width // 2, height // 2
    limit = max(2, min(width, height) // 3)
    outer = radius if radius is not None else max(2, limit - 1)
    if not 2 <= outer <= limit:
        raise RuleContractError("ring radius is out of bounds")
    cells = set()
    for layer in range(thickness):
        distance = outer - layer
        left, right = cx - distance, cx + distance
        top, bottom = cy - distance, cy + distance
        for x in range(left, right + 1):
            if 0 <= x < width:
                if 0 <= top < height: cells.add(top * width + x)
                if 0 <= bottom < height: cells.add(bottom * width + x)
        for y in range(top, bottom + 1):
            if 0 <= y < height:
                if 0 <= left < width: cells.add(y * width + left)
                if 0 <= right < width: cells.add(y * width + right)
    return cells


def corridor(width: int, height: int, rng: DeterministicRNG, *, start: tuple[int, int] | None = None, end: tuple[int, int] | None = None, width_cells: int = 1) -> set[int]:
    _validate_size(width, height)
    if not 1 <= width_cells <= 3:
        raise RuleContractError("corridor width must be 1..3")
    start = start or (1, height // 2)
    end = end or (width - 2, height // 2)
    if not all(0 <= x < width and 0 <= y < height for x, y in (start, end)):
        raise RuleContractError("corridor endpoints must be in bounds")
    x, y = start
    cells: set[int] = set()
    steps = width * height
    for _ in range(steps):
        for dy in range(-(width_cells // 2), width_cells // 2 + 1):
            for dx in range(-(width_cells // 2), width_cells // 2 + 1):
                if abs(dx) + abs(dy) <= width_cells // 2:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        cells.add(ny * width + nx)
        if (x, y) == end:
            break
        choices = []
        if x < end[0]: choices.append((x + 1, y))
        elif x > end[0]: choices.append((x - 1, y))
        if y < end[1]: choices.append((x, y + 1))
        elif y > end[1]: choices.append((x, y - 1))
        if x != end[0] and rng.randbelow(3) == 0:
            vertical = (x, y + (1 if rng.randbelow(2) else -1))
            if 0 <= vertical[1] < height:
                choices.append(vertical)
        if not choices:
            break
        x, y = rng.choice(choices)
    if (end[1] * width + end[0]) not in cells:
        raise RuleContractError("corridor could not reach endpoint within bound")
    return cells


def pocket(width: int, height: int, rng: DeterministicRNG, *, size: int = 2) -> set[int]:
    _validate_size(width, height)
    if not 2 <= size <= min(width, height) - 2:
        raise RuleContractError("pocket size is out of bounds")
    cx, cy = width // 2, height // 2
    x0, y0 = max(1, cx - size // 2), max(1, cy - size // 2)
    return {y * width + x for y in range(y0, min(height - 1, y0 + size)) for x in range(x0, min(width - 1, x0 + size))}


def snake(width: int, height: int, rng: DeterministicRNG, *, max_steps: int = 24) -> set[int]:
    _validate_size(width, height)
    if isinstance(max_steps, bool) or not isinstance(max_steps, int) or not 2 <= max_steps <= width * height:
        raise RuleContractError("snake max_steps is out of bounds")
    x, y = _center(width, height, rng.child("center"), margin=1)
    current = y * width + x
    path = {current}
    for _ in range(max_steps - 1):
        choices = [neighbor for neighbor in rng.shuffle(list(_neighbors(current, width, height))) if neighbor not in path]
        if not choices:
            break
        current = choices[0]
        path.add(current)
    return path


def branch(width: int, height: int, rng: DeterministicRNG, *, depth: int = 6, branch_count: int = 3) -> set[int]:
    _validate_size(width, height)
    if not 1 <= depth <= min(width, height) or not 1 <= branch_count <= 6:
        raise RuleContractError("branch depth/count is out of bounds")
    cx, cy = width // 2, height - 2
    cells = {cy * width + cx}
    for step in range(depth):
        cells.add(max(0, cy - step - 1) * width + cx)
    for arm in range(branch_count):
        direction = -1 if arm % 2 == 0 else 1
        y = height - 3 - (arm * max(1, depth // branch_count))
        for step in range(max(1, depth // 2)):
            x = cx + direction * step
            if 0 <= x < width and 0 <= y < height:
                cells.add(y * width + x)
                for rise in range(step + 1):
                    if y - rise >= 0:
                        cells.add((y - rise) * width + x)
    return cells


def chamber(width: int, height: int, rng: DeterministicRNG, *, chamber_width: int | None = None, chamber_height: int | None = None) -> set[int]:
    _validate_size(width, height)
    cw = chamber_width or max(4, width // 3)
    ch = chamber_height or max(4, height // 3)
    if not 3 <= cw <= width - 2 or not 3 <= ch <= height - 2:
        raise RuleContractError("chamber dimensions are out of bounds")
    x0, y0 = (width - cw) // 2, (height - ch) // 2
    cells = {y * width + x for y in range(y0, y0 + ch) for x in range(x0, x0 + cw)}
    return cells


def spiral(width: int, height: int, rng: DeterministicRNG, *, turns: int = 2) -> set[int]:
    _validate_size(width, height)
    if not 1 <= turns <= min(width, height) // 2:
        raise RuleContractError("spiral turns are out of bounds")
    cells: set[int] = set()
    left, right, top, bottom = 1, width - 2, 1, height - 2
    for turn in range(turns):
        old_right, old_top = right, top
        for x in range(left, right + 1): cells.add(top * width + x)
        for y in range(top, bottom + 1): cells.add(y * width + right)
        if top < bottom:
            for x in range(right, left - 1, -1): cells.add(bottom * width + x)
        if left < right:
            for y in range(bottom, top, -1): cells.add(y * width + left)
        left += 2; right -= 2; top += 2; bottom -= 2
        if left > right or top > bottom: break
        # A two-cell stair connector turns the nested perimeter into one
        # continuous 4-neighbor spiral rather than disconnected rings.
        for x in range(right, old_right):
            cells.add((old_top + 1) * width + x)
        cells.add((top - 1) * width + right)
    return cells


def wave(width: int, height: int, rng: DeterministicRNG, *, period: int = 5, amplitude: int = 2) -> set[int]:
    _validate_size(width, height)
    if not 2 <= period <= width or not 1 <= amplitude <= max(1, height // 4):
        raise RuleContractError("wave period/amplitude is out of bounds")
    cells: set[int] = set()
    center = height // 2
    previous = center
    for x in range(width):
        offset = ((x % period) * amplitude * 2 // period) - amplitude
        current = center + offset
        for y in range(min(previous, current) - 1, max(previous, current) + 2):
            if 0 <= y < height: cells.add(y * width + x)
        previous = current
    return cells


def radial(width: int, height: int, rng: DeterministicRNG, *, rays: int = 6, length: int | None = None) -> set[int]:
    _validate_size(width, height)
    if not 2 <= rays <= 12:
        raise RuleContractError("radial ray count is out of bounds")
    span = length or max(2, min(width, height) // 3)
    if not 2 <= span <= max(width, height):
        raise RuleContractError("radial length is out of bounds")
    cx, cy = width // 2, height // 2
    cells = {cy * width + cx}
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
    for ray in range(rays):
        dx, dy = directions[ray % len(directions)]
        for step in range(1, span + 1):
            x, y = cx + dx * step, cy + dy * step
            if 0 <= x < width and 0 <= y < height:
                cells.add(y * width + x)
                if dx and dy:
                    if 0 <= x - dx < width and 0 <= y < height: cells.add(y * width + x - dx)
                    if 0 <= x < width and 0 <= y - dy < height: cells.add((y - dy) * width + x)
    return cells


def voronoi_like(width: int, height: int, rng: DeterministicRNG, *, regions: int = 3) -> dict[str, set[int]]:
    _validate_size(width, height)
    if not 2 <= regions <= 8:
        raise RuleContractError("Voronoi region count is out of bounds")
    points = []
    available = list(range(width * height))
    for index in range(regions):
        point = available.pop(rng.randbelow(len(available)))
        points.append(point)
    output = {f"V{index + 1}": set() for index in range(regions)}
    for cell in range(width * height):
        cx, cy = cell % width, cell // width
        winner = min(range(regions), key=lambda index: (abs(cx - points[index] % width) + abs(cy - points[index] // width), points[index], index))
        output[f"V{winner + 1}"].add(cell)
    return output


def apply_primitive(canvas: RuleCanvas, primitive: str, rng: DeterministicRNG, **parameters: int | tuple[int, int]) -> set[int] | dict[str, set[int]]:
    """Render one primitive onto a canvas, respecting protected semantics."""
    if not isinstance(canvas, RuleCanvas) or not isinstance(rng, DeterministicRNG):
        raise RuleContractError("primitive application requires RuleCanvas and DeterministicRNG")
    functions = {
        "BLOB": blob, "ISLAND": island, "RING": ring, "CORRIDOR": corridor,
        "POCKET": pocket, "SNAKE": snake, "BRANCH": branch, "CHAMBER": chamber,
        "SPIRAL": spiral, "WAVE": wave, "RADIAL": radial, "VORONOI": voronoi_like,
    }
    try:
        geometry = functions[primitive](canvas.width, canvas.height, rng, **parameters)
    except KeyError as exc:
        raise RuleContractError(f"unknown primitive: {primitive}") from exc
    if isinstance(geometry, dict):
        for label, cells in geometry.items():
            canvas.mark_many(set(cells) - set(canvas.protected_negative), label)
        return geometry
    safe = set(geometry) - set(canvas.protected_negative)
    canvas.mark_many(safe, primitive)
    return safe
