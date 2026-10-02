"""Owner-approved Route A release as a game-repository branch and PR."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
from typing import Any, Callable, Mapping

from .release_pool import ReleaseError, _json, approve_release_plan, validate_release_plan


class RouteAError(RuntimeError):
    pass


_GAME_REMOTE = "https://github.com/Sekiph82/Scrubbots.git"
_ALLOWED_FIXED = "data/levels/catalog/production_catalog_v1.json"
_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def _run(args: list[str], cwd: Path, *, check: bool = True, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode:
        raise RouteAError(f"command failed ({result.returncode}): {' '.join(args)}\n{(result.stdout + result.stderr)[-2000:]}")
    return result


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return _run(["git", *args], root, check=check)


def _normalize_remote(value: str) -> str:
    value = value.strip().removesuffix(".git").rstrip("/")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.removeprefix("git@github.com:")
    return value.casefold()


def _approved_prefix(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    if plan.get("schema") != "scrubbots-campaign-plan/v1" or not isinstance(plan.get("slots"), list):
        raise RouteAError("campaign_plan.json is malformed or unsupported")
    claimed = plan.get("plan_hash")
    body = {key: value for key, value in plan.items() if key not in {"plan_hash", "artifact_path", "pool_size"}}
    digest = hashlib.sha256((json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()).hexdigest()
    if claimed != digest:
        raise RouteAError("campaign plan hash is stale or does not match its contents")
    rows: list[dict[str, Any]] = []
    for row in plan["slots"]:
        if not isinstance(row, Mapping) or not row.get("chosen_id"):
            break
        rows.append(dict(row))
    if not rows:
        raise RouteAError("approved campaign plan has no contiguous publishable prefix")
    expected = list(range(int(rows[0]["n"]), int(rows[0]["n"]) + len(rows)))
    if [row.get("n") for row in rows] != expected:
        raise RouteAError("approved plan orders are not contiguous")
    return rows


def _check_allowlist(root: Path, original_catalog: bytes, expected_ids: list[str], expected_orders: list[int]) -> list[str]:
    status = _git(root, "status", "--porcelain", "-z", "--untracked-files=all").stdout
    changed: set[str] = set()
    # Porcelain -z is NUL-delimited; paths in this contract cannot contain tabs/newlines.
    records = status.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        name = record[3:]
        if record[:2] == "R " or record[:2] == " C" or record[:2] == "RC":
            if index < len(records): index += 1
            raise RouteAError("renamed/copy paths are outside the release allow-list")
        changed.add(name.replace("\\", "/"))
    allowed = {_ALLOWED_FIXED}
    for identity in expected_ids:
        if not _ID.fullmatch(identity):
            raise RouteAError(f"plan contains unsafe candidate identity: {identity!r}")
        allowed.update({f"data/levels/{identity}.json", f"data/levels/supply/{identity}_supply_v1.json", f"data/levels/metadata/{identity}.metadata.json", f"assets/art/levels/previews/{identity}.png"})
    if not changed.issubset(allowed):
        raise RouteAError("game diff contains paths outside the Route A allow-list: " + ", ".join(sorted(changed - allowed)))
    catalog_path = root / _ALLOWED_FIXED
    if catalog_path.read_bytes() == original_catalog:
        raise RouteAError("release did not append the approved campaign to the production catalog")
    before = json.loads(original_catalog)
    after = json.loads(catalog_path.read_bytes())
    if not isinstance(before, dict) or not isinstance(after, dict) or after.get("entries", [])[:len(before.get("entries", []))] != before.get("entries", []):
        raise RouteAError("production catalog changes are not append-only")
    appended = after.get("entries", [])[len(before.get("entries", [])):]
    if [entry.get("id") for entry in appended] != expected_ids:
        raise RouteAError("catalog appended entries do not match the approved plan identities")
    if [entry.get("order") for entry in appended] != expected_orders:
        raise RouteAError("catalog appended orders do not match the approved contiguous plan")
    return sorted(changed)


def _restore(root: Path, original_catalog: bytes, created_paths: set[str]) -> None:
    for rel in created_paths:
        path = root / PurePosixPath(rel)
        if path.is_file():
            path.unlink()
    catalog = root / _ALLOWED_FIXED
    catalog.write_bytes(original_catalog)
    # Remove only empty directories created inside the allow-list tree.
    for rel in ("data/levels/metadata", "data/levels/supply", "assets/art/levels/previews"):
        base = root / rel
        if base.is_dir():
            for directory, _dirs, _files in os.walk(base, topdown=False):
                candidate = Path(directory)
                if candidate != base:
                    try: candidate.rmdir()
                    except OSError: pass


def _verify_game(project: Path, plan_rows: list[dict[str, Any]], orders: list[int]) -> dict[str, Any]:
    """Run game-owned validators, solver/replay and official Difficulty V1 in Godot."""
    from .game_rules import find_godot
    godot = find_godot()
    if not godot:
        raise RouteAError("Godot is unavailable for current game verification")
    executable = Path(godot)
    if executable.name.casefold() == "godot.exe" and executable.with_name("godot_console.exe").is_file():
        godot = str(executable.with_name("godot_console.exe"))
    ids = [str(row["chosen_id"]) for row in plan_rows]
    runner = project / "tests/factory_route_a_verify.gd"
    runner.parent.mkdir(parents=True, exist_ok=True)
    # The script is ephemeral and removed before allow-list validation/commit.
    runner.write_text('''extends SceneTree
const Catalog = preload("res://scripts/data/level_catalog.gd")
const Loader = preload("res://scripts/data/level_loader.gd")
const Supply = preload("res://scripts/gameplay/supply/supply_plan_loader.gd")
const ProofState = preload("res://scripts/gameplay/solver/proof_state.gd")
const Solver = preload("res://scripts/gameplay/solver/solvability_solver.gd")
const Analyzer = preload("res://scripts/difficulty/level_difficulty_analyzer_v1.gd")
func _initialize():
	var ids = JSON.parse_string(OS.get_environment("FACTORY_ROUTE_IDS"))
	var orders = JSON.parse_string(OS.get_environment("FACTORY_ROUTE_ORDERS"))
	var catalog = Catalog.new()
	var loaded = catalog.load_manifest()
	if not loaded.ok: _fail("LevelCatalog.load_manifest: " + str(loaded.errors)); return
	var all_result = catalog.validate_all()
	if not all_result.ok: _fail("LevelCatalog.validate_all: " + all_result.summary()); return
	var analyzer = Analyzer.new()
	if not analyzer.is_ok(): _fail("Difficulty V1 analyzer: " + analyzer.get_error()); return
	var analysis = load("res://scripts/difficulty/difficulty_v1_catalog_check.gd").new()
	var catalog_difficulty = analysis.validate_catalog(catalog)
	if not catalog_difficulty.ok: _fail("Difficulty V1 catalog check: " + str(catalog_difficulty.errors)); return
	for i in ids.size():
		var id = str(ids[i])
		var entry = catalog.get_entry_by_id(id)
		if entry == null: _fail("catalog entry missing " + id); return
		var level_result = Loader.load_from_path(entry.level_path)
		if not level_result.is_ok(): _fail("LevelLoader " + id + ": " + str(level_result.errors)); return
		var level = level_result.level_data
		var plan_result = Supply.load_plan(entry.supply_plan_path)
		if not plan_result.get("ok", false): _fail("SupplyPlanLoader " + id + ": " + str(plan_result.get("error", "failed"))); return
		var built = Supply.build_engine(plan_result.plan, level)
		if not built.get("ok", false): _fail("SupplyPlanLoader engine " + id + ": " + str(built.get("error", "failed"))); return
		var state = ProofState.from_level_and_supply(level, built["engine"])
		if state == null: _fail("ProofState " + id); return
		var solver = Solver.new()
		var solved = solver.solve(state)
		if str(solved.get("status", "")) != "SOLVED": _fail("SolvabilitySolver " + id + ": " + str(solved)); return
		var replay = solver.replay(state, solved.trace)
		if not replay.get("ok", false) or not replay.get("solved", false): _fail("SolvabilitySolver replay " + id + ": " + str(replay)); return
		var columns: Array = []
		for action in solved.trace: columns.append(int(action["column"]))
		var measured = analyzer.measure(level, built["engine"], columns, solved.trace)
		if not measured.get("ok", false): _fail("Difficulty V1 measure " + id + ": " + str(measured.get("error", "failed"))); return
		var score = analyzer.score(measured, int(orders[i]))
		var metadata = JSON.parse_string(FileAccess.get_file_as_string(entry.metadata_path))
		var expected = float(metadata.get("challengeScore", -1.0))
		var actual = float(score.get("challengeScore", -2.0))
		if absf(actual - expected) > 0.000001: _fail("Difficulty V1 metadata parity " + id + ": expected " + str(expected) + " actual " + str(actual)); return
	print("FACTORY_ROUTE_A_VERIFY_PASS")
	quit(0)
func _fail(message: String):
	push_error(message)
	quit(1)
''', encoding="utf-8")
    env = os.environ.copy()
    env["FACTORY_ROUTE_IDS"] = json.dumps(ids)
    env["FACTORY_ROUTE_ORDERS"] = json.dumps(orders)
    try:
        result = subprocess.run([godot, "--headless", "--path", str(project), "--script", "res://tests/factory_route_a_verify.gd"], cwd=project, env=env, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as exc:
        raise RouteAError(f"current-game verification timed out: {exc}") from exc
    finally:
        runner.unlink(missing_ok=True)
    if result.returncode != 0 or "FACTORY_ROUTE_A_VERIFY_PASS" not in result.stdout:
        raise RouteAError("current-game verification failed: " + (result.stdout + "\n" + result.stderr)[-6000:])
    return {"state": "PASS", "summary": f"LevelCatalog, LevelLoader, SupplyPlanLoader, solver/replay and Difficulty V1 parity passed for {len(ids)} levels."}


def _campaign_table(rows: list[dict[str, Any]], entries: list[dict[str, Any]]) -> str:
    by_id = {str(entry.get("id")): entry for entry in entries}
    lines = ["| n | class | target | D | delta | tier | size | colours |", "|---:|---|---:|---:|---:|---:|---|---|"]
    for row in rows:
        entry = by_id.get(str(row["chosen_id"]), {})
        metadata_path = str(entry.get("metadata_path", "")).removeprefix("res://")
        size = ""
        colours = ""
        if metadata_path:
            try:
                metadata = json.loads((Path(entry.get("_root", ".")) / metadata_path).read_text(encoding="utf-8"))
                size = f"{metadata.get('width')}×{metadata.get('height')}"
                colours = str(len(metadata.get("paletteSet", metadata.get("palette", []))))
            except (OSError, ValueError, TypeError):
                pass
        lines.append(f"| {row['n']} | {row['class']} | {row['target']} | {row.get('D')} | {row.get('delta')} | {row.get('tier')} | {size} | {colours} |")
    return "\n".join(lines)


def _release_approved_campaign_impl(*, plan_hash: str, game_project: str | Path, factory_commit_sha: str | None, studio_approval: bool, command_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None, verifier: Callable[..., dict[str, Any]] | None = None, publisher: Callable[..., dict[str, Any]] | None = None, expected_remote: str = _GAME_REMOTE) -> dict[str, Any]:
    """Prepare, verify, commit, push and PR one owner-approved contiguous batch."""
    if not studio_approval:
        raise RouteAError("Route A requires the explicit CampaignBuilder APPROVE action")
    if factory_commit_sha is None:
        factory_root = Path(__file__).resolve().parents[3]
        factory_commit_sha = _git(factory_root, "rev-parse", "HEAD").stdout.strip()
    if not re.fullmatch(r"[0-9a-fA-F]{40,64}", factory_commit_sha):
        raise RouteAError("Level Factory commit SHA is required for PR provenance")
    root = Path(game_project).expanduser().resolve()
    def run(args: list[str], *, check: bool = True, timeout: int = 120):
        if command_runner is None:
            return _run(args, root, check=check, timeout=timeout)
        result = command_runner(args, cwd=root, check=check, timeout=timeout)
        if check and result.returncode:
            raise RouteAError(f"command failed ({result.returncode}): {' '.join(args)}\n{(result.stdout + result.stderr)[-2000:]}")
        return result
    plan_path = Path(__import__("scrubbots_pixel_factory.studio_extensions", fromlist=["extensions_root"]).extensions_root()) / "release/campaign_plan.json"
    plan = _json(plan_path)
    rows = _approved_prefix(plan)
    if plan.get("plan_hash") != plan_hash:
        raise RouteAError("CampaignBuilder plan hash is stale; rebuild and review the plan")
    # Fetch without touching working files, then require the exact owner target and clean main.
    remote = _git(root, "remote", "get-url", "origin").stdout.strip()
    if _normalize_remote(remote) != _normalize_remote(expected_remote):
        raise RouteAError("configured game origin is not Sekiph82/Scrubbots")
    branch = _git(root, "branch", "--show-current").stdout.strip()
    if branch != "main": raise RouteAError("game checkout must be on main before Route A preflight")
    if _git(root, "status", "--porcelain").stdout.strip(): raise RouteAError("game checkout must be clean before Route A preflight")
    _git(root, "fetch", "--prune", "origin")
    counts = _git(root, "rev-list", "--left-right", "--count", "HEAD...origin/main").stdout.split()
    if counts != ["0", "0"]: raise RouteAError("game main must exactly match origin/main after fetch")
    auth = run(["gh", "auth", "status"], check=False)
    if auth.returncode != 0: raise RouteAError("gh authentication preflight failed")
    initial_head = _git(root, "rev-parse", "HEAD").stdout.strip()
    original_catalog_path = root / _ALLOWED_FIXED
    original_catalog = original_catalog_path.read_bytes()
    start_order = int(rows[0]["n"]); end_order = int(rows[-1]["n"]); count = len(rows)
    branch_name = f"levels/release-{start_order}-{end_order}"
    if _git(root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}", check=False).returncode == 0:
        raise RouteAError("deterministic release branch already exists; this campaign was already attempted")
    if _git(root, "ls-remote", "--heads", "origin", branch_name).stdout.strip():
        raise RouteAError("deterministic release branch already exists on origin; this campaign was already attempted")
    ids = [str(row["chosen_id"]) for row in rows]
    # Rebuild the exact current inputs before creating even a local branch.
    try:
        validate_release_plan(plan_hash=plan_hash, game_project=root)
    except (ReleaseError, OSError, ValueError) as exc:
        raise RouteAError(f"approved campaign plan is stale or mismatched: {exc}") from exc
    created_paths = {f"data/levels/{identity}.json" for identity in ids} | {f"data/levels/supply/{identity}_supply_v1.json" for identity in ids} | {f"data/levels/metadata/{identity}.metadata.json" for identity in ids} | {f"assets/art/levels/previews/{identity}.png" for identity in ids}
    pushed = False
    pr_url = ""
    local_branch = False
    try:
        _git(root, "switch", "-c", branch_name); local_branch = True
        publish_call = publisher or approve_release_plan
        publish_result = publish_call(plan_hash=plan_hash, game_project=root)
        orders = publish_result.get("approved_orders", publish_result.get("orders", []))
        if list(orders) != list(range(start_order, end_order + 1)):
            raise RouteAError("P1 publisher did not publish the approved contiguous order sequence")
        verification = (verifier or _verify_game)(root, rows, list(orders))
        changed = _check_allowlist(root, original_catalog, ids, [int(row["n"]) for row in rows])
        # Preserve order from the approved plan; stage only verified allow-list paths.
        _git(root, "add", "--", *changed)
        staged = _git(root, "diff", "--cached", "--name-only").stdout.splitlines()
        if set(staged) != set(changed): raise RouteAError("staged diff differs from the verified allow-list")
        message = f"levels: release {start_order}..{end_order} ({count} levels)\n\nPlan-Hash: {plan_hash}"
        _git(root, "-c", "user.name=Level Factory", "-c", "user.email=level-factory@users.noreply.github.com", "commit", "-m", message)
        commit_sha = _git(root, "rev-parse", "HEAD").stdout.strip()
        _git(root, "push", "origin", branch_name); pushed = True
        entries_after = json.loads((root / _ALLOWED_FIXED).read_text(encoding="utf-8"))["entries"][-count:]
        for entry in entries_after: entry["_root"] = str(root)
        shortage_summary = json.dumps(plan.get("shortages", []), ensure_ascii=False, sort_keys=True)
        body = "\n".join(["## Approved campaign release", "", _campaign_table(rows, entries_after), "", "### Shortage summary", shortage_summary, "", "### Game verification", str(verification.get("summary", "PASS")), "", f"Plan hash: `{plan_hash}`", f"Level Factory commit: `{factory_commit_sha}`", f"Game commit: `{commit_sha}`", "", "The repository is public; unreleased levels in this branch are publicly visible."])
        pr = run(["gh", "pr", "create", "--base", "main", "--head", branch_name, "--title", f"levels: release {start_order}..{end_order} ({count} levels)", "--body", body], check=True)
        pr_url = pr.stdout.strip().splitlines()[-1]
        run(["gh", "pr", "edit", pr_url, "--add-label", "levels-release"], check=True)
        pushed = True
        digests = {rel: hashlib.sha256((root / rel).read_bytes()).hexdigest() for rel in changed}
        receipt = {"schema": "scrubbots-release-receipt/v1", "plan_hash": plan_hash, "branch": branch_name, "game_commit_sha": commit_sha, "pr_url": pr_url, "file_digests": digests}
        receipt_path = Path(__import__("scrubbots_pixel_factory.studio_extensions", fromlist=["extensions_root"]).extensions_root()) / "release/release_receipt.json"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        return {"disposition": "RELEASE_PR_OPENED", "warning": "Public repository: pushing the branch makes unreleased levels publicly visible.", "receipt_path": str(receipt_path), "receipt": receipt, "verification": verification, **receipt}
    except Exception as exc:
        # Only undo paths admitted by the fixed publication transaction; preserve any unexpected path as evidence.
        status = _git(root, "status", "--porcelain", "-z", "--untracked-files=all", check=False).stdout if local_branch else ""
        unexpected = set()
        for record in status.split("\0"):
            if record:
                rel = record[3:].replace("\\", "/")
                if rel != _ALLOWED_FIXED and not any(rel.endswith(suffix) for suffix in (".json", ".png")):
                    unexpected.add(rel)
        if local_branch:
            current_head = _git(root, "rev-parse", "HEAD", check=False).stdout.strip()
            # A committed release is ours: switch to untouched main first so its tree
            # restores exactly, then remove only the deterministic branch we created.
            if current_head and 'initial_head' in locals() and current_head != initial_head:
                try: _git(root, "switch", "main")
                except Exception: pass
            else:
                try: _restore(root, original_catalog, created_paths)
                except OSError: pass
                try: _git(root, "restore", "--staged", "--", _ALLOWED_FIXED, *sorted(created_paths), check=False)
                except Exception: pass
                try: _git(root, "switch", "main")
                except Exception: pass
        if pushed:
            try:
                if pr_url: run(["gh", "pr", "close", pr_url], check=False)
                _git(root, "push", "origin", "--delete", branch_name, check=False)
            except Exception: pass
        if local_branch:
            try:
                _git(root, "switch", "main")
                _git(root, "branch", "-D", branch_name)
            except Exception: pass
        if isinstance(exc, RouteAError): raise
        raise RouteAError(f"Route A failed and rollback was attempted: {exc}") from exc


def release_approved_campaign(*, plan_hash: str, game_project: str | Path, factory_commit_sha: str | None = None, studio_approval: bool, command_runner: Callable[..., subprocess.CompletedProcess[str]] | None = None, verifier: Callable[..., dict[str, Any]] | None = None, publisher: Callable[..., dict[str, Any]] | None = None, expected_remote: str = _GAME_REMOTE) -> dict[str, Any]:
    """Run Route A and persist factory-side evidence for every refusal or failure."""
    try:
        return _release_approved_campaign_impl(plan_hash=plan_hash, game_project=game_project, factory_commit_sha=factory_commit_sha, studio_approval=studio_approval, command_runner=command_runner, verifier=verifier, publisher=publisher, expected_remote=expected_remote)
    except Exception as exc:
        try:
            from .. import studio_extensions as studio
            import time
            evidence_root = studio.extensions_root() / "release/failures"
            evidence_root.mkdir(parents=True, exist_ok=True)
            suffix = str(time.time_ns())
            evidence = {"schema": "scrubbots-route-a-failure/v1", "plan_hash": plan_hash, "game_project": str(Path(game_project).expanduser().resolve()), "reason": str(exc), "state": "ROLLED_BACK_OR_PREFLIGHT_REFUSED"}
            (evidence_root / f"{plan_hash}-{suffix}.json").write_text(json.dumps(evidence, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        except Exception:
            pass
        if isinstance(exc, RouteAError): raise
        raise RouteAError(str(exc)) from exc


__all__ = ["RouteAError", "release_approved_campaign"]
