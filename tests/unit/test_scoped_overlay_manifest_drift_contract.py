from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install_factory_studio_scoped_overlay.ps1"
TRANSACTION = ROOT / "scripts" / "scoped_overlay_transaction.psm1"


def _installer() -> str:
    return INSTALLER.read_text(encoding="utf-8")


def _transaction() -> str:
    return TRANSACTION.read_text(encoding="utf-8")


def test_solver_dependencies_are_scoped_and_manifest_owned() -> None:
    source = _installer()
    relative_paths = source.split("$relativePaths = @(", 1)[1].split(")", 1)[0]
    overlay_paths = source.split("$authorizedOverlayAdditions = @(", 1)[1].split(")", 1)[0]
    for path in (
        "src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py",
        "src/scrubbots_pixel_factory/supply_pipeline/verify.py",
        "src/scrubbots_pixel_factory/alpix_batch.py",
        "src/scrubbots_pixel_factory/pixellab_pro_atlas.py",
    ):
        assert f"'{path}'" in relative_paths
        assert f"'{path}'" in overlay_paths
    assert "$isAtlasPath = $relative -ceq 'src/scrubbots_pixel_factory/pixellab_pro_atlas.py'" in source
    assert "$isNewManagedPath = $isAtlasPath -and -not $managed.ContainsKey($relative)" in source
    assert "if (-not $managed.ContainsKey($relative) -and -not $isNewManagedPath)" in source
    assert "NewManagedPaths @('src/scrubbots_pixel_factory/pixellab_pro_atlas.py')" in source
    assert "if ($relative -cnotin $authorizedOverlayAdditions) { throw \"Installed overlay allowlist does not include: $relative\" }" in source


def test_preflight_reports_hash_triples_and_reproduces_exact_historic_verify_bytes() -> None:
    source = _installer()
    transaction = _transaction()
    for key in ("manifestSha256", "installedSha256", "sourceSha256"):
        assert key in source
    assert "Get-HistoricBlobBytes" in source
    assert "892b02b69bb5d3d9b1aa26d7499bbda4f1017548658444dc4332e67a2515cc9a" in source
    assert "canonicalCrlfBytes" in source
    assert "$authorizedRepairHashes[$verifyPath] = $historicVerifyHash" in source
    assert "90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744" in source
    assert "a9776ce1dcb73df2ac9acab34f0e26ae97cdb4d7c7caee248af8eeb9eb5f6122" in source
    assert "395e2fc99fd437dda256f25c33f09a5b75f63c5429e1dacce8e01ec0c1c3dd82" in source
    assert "2c2d2d39183780efd44516f97784ee20994f3554e4d3c2eac09920058a4071f5" in source
    assert "fdd2d815aafbd81706572178825abadd24a42cbd95a0e06f46a2d15317c1d4a2" in source
    assert "d30651a2c1d89720fc73e070a72282cbedcfa366159004aea327ae7937d12507" in source
    assert "priorExpectedFileReceipt" in source
    assert "Repeat V05 install requires the exact previously published verified overlay receipt." in source
    assert "Prior V05 verify.py receipt does not reproduce exact source-at-install bytes." in source
    assert "$verifiedReceiptChain = $false" in source
    assert "$atlasAdditionReceipt = $false" in source
    assert "[bool]$fileReceipt.priorExists -eq $false" in source
    assert "Installed managed bytes differ from manifest without an approved exact repair; no files were written." in transaction
    assert "$manifestDrift.Count -gt 0" in source


def test_apply_is_blocked_by_manifest_drift_or_active_runtime() -> None:
    source = _installer()
    transaction = _transaction()
    gate = source.index("Assert-ScopedInstallApplyGates -ManifestDrift")
    transaction_start = source.index("Invoke-ScopedOverlayTransaction -Plan")
    assert gate < transaction_start
    assert "PROCESS_INVENTORY_INCOMPLETE" in transaction
    assert "ParentProcessId" in transaction
    assert "ExecutablePath" in transaction
    assert "CommandLine" in transaction
    assert "activeIds.Contains([int]$process.ParentProcessId)" in transaction
    assert "AcquireWriterExclusion = {" in source
    assert "-ExpectBlocked" in transaction
    assert "WriterExclusionEstablished:$true" not in source


def test_transaction_stages_every_payload_and_manifest_before_first_replace() -> None:
    source = _transaction()
    first_payload_write = source.index("$Operations.WriteBytes $stage")
    manifest_stage_write = source.index("$Operations.WriteText $manifestStage")
    first_payload_replace = source.index("$Operations.Replace $item.stage")
    manifest_replace = source.index("$Operations.Replace $manifestStage")
    assert first_payload_write < manifest_stage_write < first_payload_replace < manifest_replace
    assert "if (([string](& $Operations.Hash $stage)) -cne [string]$item.sha256)" in source
    assert "[array]::Reverse($reverseAttempted)" in source
    assert "TARGET_HASH_MISMATCH" in source
    assert "MANIFEST_HASH_MISMATCH" in source
    assert "priorExists" in source
    assert "writerExclusionMethod" in source
    assert "MoveNew" in source


def test_preflight_never_writes_the_protected_job_or_release_pool() -> None:
    source = _installer()
    assert "png-batch-875545d48a14a0d6b4d542f554919e8d" not in source
    assert "studio-extensions\\png-batches\\jobs" not in source
    assert "studio-extensions\\release-pool" not in source
    assert "if (-not $Apply" in source
