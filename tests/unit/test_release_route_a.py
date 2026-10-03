from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import release_route_a as route


def _git(cwd: Path, *args: str, check: bool = True):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=check)


def _world(tmp_path: Path, monkeypatch):
    bare = tmp_path / "remote.git"
    work = tmp_path / "game"
    work.mkdir()
    _git(tmp_path, "init", "--bare", str(bare))
    monkeypatch.setattr(route, "_GAME_REMOTE", str(bare))
    _git(work, "init", "-b", "main")
    _git(work, "config", "user.name", "Route Test")
    _git(work, "config", "user.email", "route-test@example.invalid")
    _git(work, "remote", "add", "origin", str(bare))
    catalog = work / "data/levels/catalog/production_catalog_v1.json"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(json.dumps({"schema": "scrubbots.production_catalog.v1", "entries": []}) + "\n")
    (work / "project.godot").write_text("config_version=5\n")
    _git(work, "add", ".")
    _git(work, "commit", "-m", "initial")
    _git(work, "push", "-u", "origin", "main")
    ext = tmp_path / "factory"
    (ext / "release").mkdir(parents=True)
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: ext)
    monkeypatch.setattr(route, "validate_release_plan", lambda **_kwargs: {"plan": {}, "prefix": [], "items": [], "game_project": work})
    body = {"schema": "scrubbots-campaign-plan/v1", "inputs": {"catalog_digest": "x", "authority_digest": "y", "pool_digest": "z"}, "K": 2, "slots": [
        {"n": 1, "class": "EASY", "target": 50.0, "chosen_id": "release-one", "D": 50.0, "delta": 0.0, "tier": 0},
        {"n": 2, "class": "EASY", "target": 51.0, "chosen_id": "release-two", "D": 51.0, "delta": 0.0, "tier": 0},
    ], "shortages": [], "publishable_prefix": [1, 2], "warnings": []}
    digest = hashlib.sha256((json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()).hexdigest()
    plan = {**body, "plan_hash": digest}
    (ext / "release/campaign_plan.json").write_text(json.dumps(plan, sort_keys=True) + "\n")
    return bare, work, ext, digest


def _publish(**kwargs):
    root = Path(kwargs["game_project"])
    catalog_path = root / "data/levels/catalog/production_catalog_v1.json"
    catalog = json.loads(catalog_path.read_text())
    entries = []
    for number, identity in ((1, "release-one"), (2, "release-two")):
        entry = {"id": identity, "order": number, "level_path": f"res://data/levels/{identity}.json", "supply_plan_path": f"res://data/levels/supply/{identity}_supply_v1.json", "metadata_path": f"res://data/levels/metadata/{identity}.metadata.json", "preview_path": f"res://assets/art/levels/previews/{identity}.png"}
        for rel, data in ((f"data/levels/{identity}.json", b"level"), (f"data/levels/supply/{identity}_supply_v1.json", b"supply"), (f"data/levels/metadata/{identity}.metadata.json", b"metadata"), (f"assets/art/levels/previews/{identity}.png", b"preview")):
            path = root / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        entries.append(entry)
    catalog["entries"].extend(entries)
    catalog_path.write_text(json.dumps(catalog, sort_keys=True) + "\n")
    return {"orders": [1, 2], "approved_orders": [1, 2]}


def _gh(*, fail_create=False, fail_edit=False, calls=None):
    calls = calls if calls is not None else []
    def run(args, **kwargs):
        calls.append(args)
        if args[:3] == ["gh", "auth", "status"]:
            return subprocess.CompletedProcess(args, 0, "authenticated", "")
        if args[:3] == ["gh", "pr", "edit"] and fail_edit: return subprocess.CompletedProcess(args, 1, "", "injected PR label failure")
        if args[:3] == ["gh", "pr", "create"]:
            if fail_create: return subprocess.CompletedProcess(args, 1, "", "injected PR failure")
            return subprocess.CompletedProcess(args, 0, "https://github.com/Sekiph82/Scrubbots/pull/99\n", "")
        return subprocess.CompletedProcess(args, 0, "", "")
    return run


def _call(work, digest, **kwargs):
    return route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda root, rows, orders: {"state": "PASS", "summary": "stub verified"}, command_runner=_gh(), **kwargs)


def test_route_a_success_builds_only_release_branch_commit_pr_body_label_and_receipt(tmp_path, monkeypatch):
    bare, work, ext, digest = _world(tmp_path, monkeypatch)
    calls = []
    result = route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS", "summary": "game verified"}, command_runner=_gh(calls=calls))
    assert result["disposition"] == "RELEASE_PR_OPENED"
    assert result["branch"] == "levels/release-1-2"
    assert result["warning"].startswith("Public repository")
    assert Path(result["receipt_path"]).is_file()
    assert _git(work, "branch", "--show-current").stdout.strip() == "levels/release-1-2"
    assert _git(bare, "show-ref", "--verify", "refs/heads/levels/release-1-2").returncode == 0
    message = _git(work, "log", "-1", "--format=%B").stdout
    assert "levels: release 1..2 (2 levels)" in message and digest in message
    create = next(call for call in calls if call[:3] == ["gh", "pr", "create"])
    body = create[create.index("--body") + 1]
    for marker in ("| n | class | target | D | delta | tier | size | colours |", "Shortage summary", "game verified", digest, "a" * 40):
        assert marker in body
    assert any(call[:4] == ["gh", "pr", "edit", "https://github.com/Sekiph82/Scrubbots/pull/99"] for call in calls)


@pytest.mark.parametrize("refusal", ["dirty", "wrong_branch", "behind", "wrong_remote", "unauthenticated"])
def test_preflight_refusals_make_no_release_files_or_branch(tmp_path, monkeypatch, refusal):
    bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    if refusal == "dirty": (work / "owner.txt").write_text("preserve")
    if refusal == "wrong_branch": _git(work, "switch", "-c", "owner")
    if refusal == "behind":
        other = tmp_path / "other"; _git(tmp_path, "clone", "-b", "main", str(bare), str(other)); _git(other, "config", "user.name", "Other"); _git(other, "config", "user.email", "other@example.invalid"); (other / "remote.txt").write_text("new"); _git(other, "add", "."); _git(other, "commit", "-m", "advance"); _git(other, "push", "origin", "main"); _git(work, "fetch", "origin")
    if refusal == "wrong_remote": _git(work, "remote", "set-url", "origin", "https://example.invalid/Scrubbots.git")
    gh = _gh()
    if refusal == "unauthenticated":
        def gh(args, **kwargs): return subprocess.CompletedProcess(args, 1, "", "not authenticated")
    with pytest.raises(route.RouteAError):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS"}, command_runner=gh)
    assert _git(work, "branch", "--list", "levels/release-*").stdout.strip() == ""
    assert not (work / "data/levels/release-one.json").exists()
    if refusal == "dirty": assert (work / "owner.txt").read_text() == "preserve"
    assert _git(bare, "show-ref", "--verify", "refs/heads/levels/release-1-2", check=False).returncode != 0


def test_verification_failure_restores_checkout_and_removes_branch(tmp_path, monkeypatch):
    _bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    before = {p.relative_to(work).as_posix(): p.read_bytes() for p in work.rglob("*") if p.is_file() and ".git" not in p.parts}
    with pytest.raises(route.RouteAError, match="injected verification"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: (_ for _ in ()).throw(route.RouteAError("injected verification")), command_runner=_gh())
    after = {p.relative_to(work).as_posix(): p.read_bytes() for p in work.rglob("*") if p.is_file() and ".git" not in p.parts}
    assert after == before
    assert _git(work, "branch", "--show-current").stdout.strip() == "main"
    assert _git(work, "branch", "--list", "levels/release-*").stdout.strip() == ""


def test_pr_failure_after_push_deletes_remote_branch_and_restores_checkout(tmp_path, monkeypatch):
    bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    with pytest.raises(route.RouteAError, match="injected PR failure"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS", "summary": "verified"}, command_runner=_gh(fail_create=True))
    assert _git(work, "branch", "--show-current").stdout.strip() == "main"
    assert _git(work, "branch", "--list", "levels/release-*").stdout.strip() == ""
    assert _git(bare, "show-ref", "--verify", "refs/heads/levels/release-1-2", check=False).returncode != 0
    assert not (work / "data/levels/release-one.json").exists()


def test_plan_replay_or_collision_is_idempotently_refused(tmp_path, monkeypatch):
    bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    kwargs = dict(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS", "summary": "verified"}, command_runner=_gh())
    route.release_approved_campaign(**kwargs)
    _git(work, "switch", "main")
    catalog = (work / "data/levels/catalog/production_catalog_v1.json").read_bytes()
    with pytest.raises(route.RouteAError, match="branch already exists"):
        route.release_approved_campaign(**kwargs)
    assert (work / "data/levels/catalog/production_catalog_v1.json").read_bytes() == catalog


def test_allowlist_violation_removes_unexpected_file_and_directory_and_restores_preflight_snapshot(tmp_path, monkeypatch):
    _bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    snapshot = route._snapshot_checkout(work)
    created_path = work / "unexpected/nested/payload.bin"
    def bad_publish(**kwargs):
        result = _publish(**kwargs)
        created_path.parent.mkdir(parents=True)
        created_path.write_bytes(b"created by failed Route A attempt")
        return result
    with pytest.raises(route.RouteAError, match="outside the Route A allow-list"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=bad_publish, verifier=lambda *_: {"state": "PASS"}, command_runner=_gh())
    assert not created_path.exists()
    assert not (work / "unexpected").exists()
    assert _git(work, "branch", "--list", "levels/release-*").stdout.strip() == ""
    assert route._verify_checkout_snapshot(work, snapshot) == []


def test_public_route_api_cannot_override_canonical_remote(tmp_path, monkeypatch):
    _bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    monkeypatch.setattr(route, "_GAME_REMOTE", "https://github.com/Sekiph82/Scrubbots.git")
    _git(work, "remote", "set-url", "origin", "https://example.invalid/arbitrary.git")
    with pytest.raises(route.RouteAError, match="not Sekiph82/Scrubbots"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS"}, command_runner=_gh())
    with pytest.raises(TypeError, match="expected_remote"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, expected_remote="https://example.invalid/arbitrary.git")


def test_post_pr_label_failure_closes_pr_and_restores_preflight_snapshot(tmp_path, monkeypatch):
    bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    snapshot = route._snapshot_checkout(work)
    calls: list[list[str]] = []
    with pytest.raises(route.RouteAError, match="injected PR label failure"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS", "summary": "verified"}, command_runner=_gh(fail_edit=True, calls=calls))
    assert any(call[:3] == ["gh", "pr", "close"] for call in calls)
    assert _git(bare, "show-ref", "--verify", "refs/heads/levels/release-1-2", check=False).returncode != 0
    assert route._verify_checkout_snapshot(work, snapshot) == []


def test_rollback_cleanup_failure_is_reported_and_evidence_is_not_rolled_back(tmp_path, monkeypatch):
    _bare, work, ext, digest = _world(tmp_path, monkeypatch)
    original_git = route._git
    def fail_return_to_main(root, *args, **kwargs):
        if args[:2] == ("switch", "--force"):
            return subprocess.CompletedProcess(["git", *args], 1, "", "injected cleanup failure")
        return original_git(root, *args, **kwargs)
    monkeypatch.setattr(route, "_git", fail_return_to_main)
    def bad_publish(**kwargs):
        result = _publish(**kwargs)
        (work / "unexpected.bin").write_bytes(b"unexpected")
        return result
    with pytest.raises(route.RouteARollbackError, match="rollback could not be verified"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=bad_publish, verifier=lambda *_: {"state": "PASS"}, command_runner=_gh())
    evidence = list((ext / "release/failures").glob("*.json"))
    assert evidence
    assert json.loads(evidence[-1].read_text())["state"] == "ROLLBACK_FAILED"


def test_local_commit_failure_before_push_rolls_back_and_deletes_branch(tmp_path, monkeypatch):
    bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    original_git = route._git
    injected = False
    def fail_push(root, *args, **kwargs):
        nonlocal injected
        if args[:3] == ("push", "origin", "levels/release-1-2") and not injected:
            injected = True
            raise route.RouteAError("injected push failure after local commit")
        return original_git(root, *args, **kwargs)
    monkeypatch.setattr(route, "_git", fail_push)
    with pytest.raises(route.RouteAError, match="injected push failure"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS"}, command_runner=_gh())
    assert injected
    assert _git(work, "branch", "--show-current").stdout.strip() == "main"
    assert _git(work, "branch", "--list", "levels/release-*").stdout.strip() == ""
    assert _git(bare, "show-ref", "--verify", "refs/heads/levels/release-1-2", check=False).returncode != 0
    assert not (work / "data/levels/release-one.json").exists()


def test_stale_plan_refusal_happens_before_local_branch_creation(tmp_path, monkeypatch):
    bare, work, _ext, digest = _world(tmp_path, monkeypatch)
    def stale(**_kwargs): raise route.ReleaseError("campaign inputs or locked sequence changed")
    monkeypatch.setattr(route, "validate_release_plan", stale)
    with pytest.raises(route.RouteAError, match="stale or mismatched"):
        route.release_approved_campaign(plan_hash=digest, game_project=work, factory_commit_sha="a" * 40, studio_approval=True, publisher=_publish, verifier=lambda *_: {"state": "PASS"}, command_runner=_gh())
    assert _git(work, "branch", "--list", "levels/release-*").stdout.strip() == ""
    assert not (work / "data/levels/release-one.json").exists()
