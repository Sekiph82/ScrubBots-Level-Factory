from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install_factory_studio_scoped_overlay.ps1"


def _installer() -> str:
    return INSTALLER.read_text(encoding="utf-8")


def test_solver_dependencies_are_scoped_and_manifest_owned() -> None:
    source = _installer()
    relative_paths = source.split("$relativePaths = @(", 1)[1].split(")", 1)[0]
    overlay_paths = source.split("$authorizedOverlayAdditions = @(", 1)[1].split(")", 1)[0]
    for path in (
        "src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py",
        "src/scrubbots_pixel_factory/supply_pipeline/verify.py",
        "src/scrubbots_pixel_factory/alpix_batch.py",
    ):
        assert f"'{path}'" in relative_paths
        assert f"'{path}'" in overlay_paths
    assert "if (-not $managed.ContainsKey($relative)) { throw \"Manifest does not own the managed target: $relative\" }" in source
    assert "if ($relative -cnotin $authorizedOverlayAdditions) { throw \"Installed overlay allowlist does not include: $relative\" }" in source


def test_preflight_reports_hash_triples_and_keeps_unproven_verify_drift_blocked() -> None:
    source = _installer()
    for key in ("manifestSha256", "installedSha256", "sourceSha256"):
        assert key in source
    assert "KNOWN_SOURCE_VERSION_APPROVAL_UNPROVEN" in source
    assert "90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744" in source
    assert "Installed managed bytes differ from manifest without an approved exact repair; no files were written." in source
    assert "$manifestDrift.Count -gt 0" in source


def test_apply_is_blocked_by_manifest_drift_or_active_runtime() -> None:
    source = _installer()
    drift_gate = source.index("if ($manifestDrift.Count -gt 0) { throw")
    transaction_start = source.index("$transactionRoot = Join-Path")
    active_gate = source.index("if ($Apply -and $active.Count -gt 0)")
    assert drift_gate < transaction_start
    assert active_gate < transaction_start
    assert "$process.ProcessId -ne $PID" in source
    assert "$process.ParentProcessId" in source
    assert "activeProcessIds.Contains([uint32]$process.ParentProcessId)" in source
    assert "executablePath = $_.ExecutablePath" in source
    assert "commandLine = $_.CommandLine" in source
    assert "$process.ParentProcessId" in source
    assert "activeProcessIds.Contains([uint32]$process.ParentProcessId)" in source
    assert "executablePath = $_.ExecutablePath" in source
    assert "commandLine = $_.CommandLine" in source


def test_transaction_stages_every_payload_and_manifest_before_first_replace() -> None:
    source = _installer()
    first_payload_write = source.index("[IO.File]::WriteAllBytes($stage")
    manifest_stage_write = source.index("[IO.File]::WriteAllText($manifestStage")
    first_payload_replace = source.index("[IO.File]::Replace($item.stage")
    manifest_replace = source.index("[IO.File]::Replace($manifestStage")
    assert first_payload_write < manifest_stage_write < first_payload_replace < manifest_replace
    assert "if ((Get-Sha256 $stage) -cne $item.sha256)" in source
    assert "foreach ($entry in @($replaced | Select-Object -Reverse))" in source
    assert "if ((Get-Sha256 $item.target) -cne $item.expected)" in source


def test_preflight_never_writes_the_protected_job_or_release_pool() -> None:
    source = _installer()
    assert "png-batch-875545d48a14a0d6b4d542f554919e8d" not in source
    assert "studio-extensions\\png-batches\\jobs" not in source
    assert "studio-extensions\\release-pool" not in source
    assert "if (-not $Apply" in source
