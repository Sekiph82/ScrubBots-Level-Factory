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
    new_managed_paths = source.split("$authorizedNewManagedPaths = @(", 1)[1].split(")", 1)[0]
    for path in (
        "src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py",
        "src/scrubbots_pixel_factory/supply_pipeline/verify.py",
        "src/scrubbots_pixel_factory/alpix_batch.py",
        "src/scrubbots_pixel_factory/owner_art_storage.py",
        "src/scrubbots_pixel_factory/owner_folder_batch.py",
        "src/scrubbots_pixel_factory/owner_release_library.py",
        "src/scrubbots_pixel_factory/pixellab_pro_atlas.py",
    ):
        assert f"'{path}'" in relative_paths
        assert f"'{path}'" in overlay_paths
    for path in (
        "src/scrubbots_pixel_factory/owner_art_storage.py",
        "src/scrubbots_pixel_factory/owner_folder_batch.py",
        "src/scrubbots_pixel_factory/owner_release_library.py",
    ):
        assert f"'{path}'" in new_managed_paths
    assert "$isNewManagedPath = $relative -cin $authorizedNewManagedPaths -and -not $managed.ContainsKey($relative)" in source
    assert "if (-not $managed.ContainsKey($relative) -and -not $isNewManagedPath)" in source
    assert "NewManagedPaths $authorizedNewManagedPaths" in source
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


def test_repeat_v06_install_requires_exact_manifest_receipt_and_verify_hashes() -> None:
    source = _installer()
    assert "53d2305a67685e6a782b8273ca9f3d1024a5b7d9dd9a9ba14453c64b0be43367" in source
    assert "a91f6627d24f48df953a3baf956db76f6a2fef12" in source
    assert "Repeat R10 V06 install requires the exact published seven-file receipt" in source
    assert "R10 V06 prior install receipt differs from its exact recorded bytes" in source
    assert "R10 V06 manifest does not retain the exact published verify.py receipt" in source
    assert "Installed verify.py differs from the exact R10 V06 manifest receipt" in source
    for sha256 in (
        "7d383e204588c8c4374ce06660087171de5b16f87ca8f71d8f027f632b9dee9b",
        "5f08fe2a4884c3804964e5ee45f56081acc71887cddb0b741bb5e2fa01a324e1",
        "3a7d046a35dacb6ea516179d6004e388c0962d195dc43d711981e8e14e86d27f",
        "5f874c1b4b8de5227c7eb701c98f1e201ced3e0a78523fb918c446882d6163ac",
        "74a11709f16caaca7ae21d5ed53331003e2754f3a33241ed83ee9d5e492a2a37",
        "0a6ed1123ed6e1ce5204972ffe489e67e682a198e1c462006aea32c251d63b97",
        "f93289e84276529b1404c64bf6b435c3c50a636db9c4d19cbaef941a2f4c8540",
    ):
        assert sha256 in source


def test_missing_cim_process_fields_use_native_query_without_bypassing_gate() -> None:
    source = _installer()
    assert "OpenProcess(0x1000" in source
    assert "QueryFullProcessImageName" in source
    assert "NtQueryInformationProcess" in source
    assert "function Complete-ScopedProcessMetadata" in source
    assert "return @($completed)" in source
    assert "return ,@($completed)" not in source
    assert "$completeInventory = @(Complete-ScopedProcessMetadata -Processes $freshInventory)" in source
    assert "Get-ScopedProcessInventoryState -Processes $completeInventory" in source
    assert "PROCESS_INVENTORY_INCOMPLETE" in _transaction()
