[CmdletBinding()]
param([switch]$Apply)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$expectedRepoRoot = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator'
$canonicalOrigin = 'https://github.com/Sekiph82/ScrubBots-Level-Factory.git'
$runtimeRoot = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio'
$manifestPath = Join-Path $runtimeRoot '.factory-studio-install-manifest.json'
Import-Module (Join-Path $PSScriptRoot 'scoped_overlay_transaction.psm1') -Force
$relativePaths = @(
	'level_factory/scripts/factory_core_launcher.py',
    'level_factory/scripts/factory_studio_exact_ui.gd',
	'scripts/launch_factory_studio.ps1',
	'level_factory/scripts/factory_studio_shell.gd',
	'level_factory/scripts/factory_studio_workspace_page.gd',
	'level_factory/scripts/factory_core_gateway.gd',
	'level_factory/project.godot',
    'src/scrubbots_pixel_factory/output/bundle.py',
    'src/scrubbots_pixel_factory/semantic/providers/registry.py',
    'src/scrubbots_pixel_factory/png_batch.py',
    'src/scrubbots_pixel_factory/studio_extensions.py',
    'src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py',
    'src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py',
    'src/scrubbots_pixel_factory/supply_pipeline/release_pool.py',
    'src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py',
    'src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py',
    'src/scrubbots_pixel_factory/supply_pipeline/verify.py',
    'src/scrubbots_pixel_factory/alpix_batch.py',
    'src/scrubbots_pixel_factory/pixellab_pro_atlas.py'
)
$authorizedOverlayAdditions = @(
	'level_factory/project.godot',
	'level_factory/scripts/factory_studio_shell.gd',
	'level_factory/scripts/factory_studio_workspace_page.gd',
	'level_factory/scripts/factory_core_gateway.gd',
    'src/scrubbots_pixel_factory/output/bundle.py',
    'src/scrubbots_pixel_factory/semantic/providers/registry.py',
    'src/scrubbots_pixel_factory/supply_pipeline/supply_exporter.py',
    'src/scrubbots_pixel_factory/supply_pipeline/verify.py',
    'src/scrubbots_pixel_factory/alpix_batch.py',
    'src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py',
    'src/scrubbots_pixel_factory/supply_pipeline/solver_budget.py',
    'src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py',
    'src/scrubbots_pixel_factory/pixellab_pro_atlas.py'
)
# One exact installed solver variant was verified to be missing the Studio
# cancel-marker/process-tree handling. Permit repairing only those measured
# bytes; any other manifest mismatch remains a hard stop.
$authorizedRepairHashes = @{
    'src/scrubbots_pixel_factory/supply_pipeline/scrubbots_solver.py' = '57b6cf7ae679bf3b8c16b4d9ff8d0c3eb23ff3f4039c8d630c89fe19e3df0169'
    # This exact installed variant differs from the published optimizer only
    # in retaining the old 90-second defaults; restore the approved 240 cap.
    'src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py' = '798fc4848b35bf1a866e900e5343a641ac9ad97f3100f53b09b743bfd18bc62b'
}
# The installed verify.py bytes are an exact CRLF checkout of published
# source commit 17643de6756ba3d9552351eb237db19bd8d0c269. The existing builder
# log records this pre-existing mismatch. The repair is authorized only after
# runtime reproduction below proves the exact raw Git blob and CRLF byte hash.
$knownProvenanceHashes = @{
    'src/scrubbots_pixel_factory/supply_pipeline/verify.py' = @{
        sha256 = '90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744'
        sourceCommit = '17643de6756ba3d9552351eb237db19bd8d0c269'
        disposition = 'EXACT_HISTORIC_SOURCE_AND_CRLF_REPRODUCTION_REQUIRED'
    }
}

function Get-HistoricBlobBytes([string]$Commit, [string]$RelativePath, [string]$ExpectedRawSha256 = '') {
    $blobId = (Invoke-Git @('rev-parse', "$Commit`:$RelativePath")).Trim()
    if ($blobId -notmatch '^[0-9a-f]{40}$') { throw 'Historical verify.py Git blob identity is invalid.' }
    $start = [Diagnostics.ProcessStartInfo]::new()
    $start.FileName = 'git'
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.Arguments = '-C "{0}" cat-file blob {1}' -f $repoRoot, $blobId
    $process = [Diagnostics.Process]::Start($start)
    $memory = [IO.MemoryStream]::new()
    try {
        $process.StandardOutput.BaseStream.CopyTo($memory)
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        if ($process.ExitCode -ne 0) { throw "git cat-file failed: $stderr" }
        $bytes = $memory.ToArray()
        if (-not [string]::IsNullOrWhiteSpace($ExpectedRawSha256) -and (Get-Sha256Bytes $bytes) -cne $ExpectedRawSha256) { throw 'Historical verify.py raw blob bytes differ from the independently recorded source hash.' }
        return ,$bytes
    } finally { $memory.Dispose(); $process.Dispose() }
}

function Get-Sha256Bytes([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}


function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-Git([string[]]$Arguments) {
    $output = & git -C $repoRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git $($Arguments -join ' ') failed: $($output -join ' ')" }
    return (($output | Out-String).Trim())
}

function Assert-NoReparsePath([string]$Path) {
    $root = [IO.Path]::GetFullPath($runtimeRoot).TrimEnd('\')
    $cursor = [IO.Path]::GetFullPath($Path)
    while ($cursor.Equals($root, [StringComparison]::OrdinalIgnoreCase) -or $cursor.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase)) {
        $item = Get-Item -LiteralPath $cursor -Force -ErrorAction SilentlyContinue
        if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to follow owner-created reparse point: $cursor"
        }
        if ($cursor.Equals($root, [StringComparison]::OrdinalIgnoreCase)) { break }
        $cursor = Split-Path -Parent $cursor
    }
}

if (-not [StringComparer]::OrdinalIgnoreCase.Equals($repoRoot, $expectedRepoRoot)) { throw "Unexpected repository root: $repoRoot" }
$origin = (Invoke-Git @('remote', 'get-url', 'origin')).TrimEnd('/')
if (-not [StringComparer]::OrdinalIgnoreCase.Equals($origin, $canonicalOrigin.TrimEnd('/'))) { throw 'Canonical origin mismatch.' }
$head = Invoke-Git @('rev-parse', 'HEAD')
$remoteHead = Invoke-Git @('rev-parse', 'origin/main')
if ($head -cne $remoteHead) { throw 'Published HEAD and origin/main differ; refusing installation.' }
foreach ($relative in $relativePaths) {
    [void](Invoke-Git @('ls-files', '--error-unmatch', '--', $relative))
}
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw "Installed manifest is missing: $manifestPath" }
Assert-NoReparsePath $manifestPath
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.formatVersion -ne 1 -or $manifest.installationMode -cne 'OWNER_APPROVED_SCOPED_OVERLAY') { throw 'Installed manifest is not the expected scoped-overlay format.' }

$managed = @{}
foreach ($entry in @($manifest.managedFiles)) {
    if ($managed.ContainsKey([string]$entry.path)) { throw "Duplicate managed path: $($entry.path)" }
    $managed[[string]$entry.path] = $entry
}
$verifyPath = 'src/scrubbots_pixel_factory/supply_pipeline/verify.py'
$verifyEntries = @($manifest.managedFiles | Where-Object path -ceq $verifyPath)
if ($verifyEntries.Count -ne 1) { throw 'Historical verify.py repair requires exactly one managed manifest entry.' }
$manifestSha256 = Get-Sha256 $manifestPath
$historicVerifyHash = $knownProvenanceHashes[$verifyPath].sha256
$verifyRepairAuthorized = $false
if (([string]$verifyEntries[0].sha256).ToLowerInvariant() -ceq '0f4b7f0319d68278934863fd448db63acdeb418776cddcbca4685815d3317ca2') {
    $historicLfBytes = [byte[]](Get-HistoricBlobBytes -Commit $knownProvenanceHashes[$verifyPath].sourceCommit -RelativePath $verifyPath -ExpectedRawSha256 '892b02b69bb5d3d9b1aa26d7499bbda4f1017548658444dc4332e67a2515cc9a')
    $lfText = [Text.UTF8Encoding]::new($false, $true).GetString($historicLfBytes)
    $canonicalLf = $lfText.Replace("`r`n", "`n")
    $canonicalCrlfBytes = [Text.UTF8Encoding]::new($false).GetBytes($canonicalLf.Replace("`n", "`r`n"))
    if ((Get-Sha256Bytes $canonicalCrlfBytes) -cne $historicVerifyHash) { throw 'Historical verify.py LF-to-CRLF provenance did not reproduce the exact installed hash.' }
    $verifyRepairAuthorized = $true
}
elseif ($manifestSha256 -cin @(
    'a9776ce1dcb73df2ac9acab34f0e26ae97cdb4d7c7caee248af8eeb9eb5f6122',
    '395e2fc99fd437dda256f25c33f09a5b75f63c5429e1dacce8e01ec0c1c3dd82'
)) {
    # These two exact manifests are prior successful V05 overlays. Permit a
    # repeat only when the latest UI receipt and the historic verify.py plus
    # atlas-addition receipts prove the exact chain and writer exclusion.
    $priorReceipt = @($manifest.overlayReceipts)[-1]
    $atlasPath = 'src/scrubbots_pixel_factory/pixellab_pro_atlas.py'
    $priorReceiptHead = if ($manifestSha256 -ceq 'a9776ce1dcb73df2ac9acab34f0e26ae97cdb4d7c7caee248af8eeb9eb5f6122') { 'ee51d899df149cb559184f4617537e1e6cb7dc6e' } else { '1a8e7d435eb55601b2eaa37371109e753f4852fd' }
    $priorUiHash = if ($priorReceiptHead -ceq 'ee51d899df149cb559184f4617537e1e6cb7dc6e') { 'ebe91efa47224520c3de97139638916c492b68b94db7612c76bdfa023c5208d2' } else { 'f39f0324e704d636e21d4aab9d83b527b790f2a0c2b0eab7861472b745653e66' }
    $priorUiReceipt = @($priorReceipt.files | Where-Object { $_.path -ceq 'level_factory/scripts/factory_studio_exact_ui.gd' -and $_.sha256 -ceq $priorUiHash })
    if ($priorReceipt.taskId -cne 'SB-LFX-018-R05-M03' -or
        $priorReceipt.sourceCommit -cne $priorReceiptHead -or
        $priorReceipt.sourceHead -cne $priorReceiptHead -or
        [string]$priorReceipt.writerExclusionMethod -cnotlike 'Windows FileStream deny-write handles on every existing replacement target and install manifest;*' -or
        $priorUiReceipt.Count -ne 1) {
        throw 'Repeat V05 install requires the exact previously published verified overlay receipt.'
    }
    $verifiedReceiptChain = $false
    $atlasAdditionReceipt = $false
    foreach ($receipt in @($manifest.overlayReceipts)) {
        if ([string]$receipt.sourceHead -cne 'ee51d899df149cb559184f4617537e1e6cb7dc6e' -or [string]$receipt.sourceCommit -cne 'ee51d899df149cb559184f4617537e1e6cb7dc6e') { continue }
        foreach ($fileReceipt in @($receipt.files)) {
            if ([string]$fileReceipt.path -ceq $verifyPath -and
                [string]$fileReceipt.priorSha256 -ceq $historicVerifyHash -and
                [string]$fileReceipt.sha256 -ceq '151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3' -and
                [string]$receipt.writerExclusionMethod -clike 'Windows FileStream deny-write handles on every existing replacement target and install manifest;*') { $verifiedReceiptChain = $true }
            if ([string]$fileReceipt.path -ceq $atlasPath -and
                [bool]$fileReceipt.priorExists -eq $false -and
                [string]$fileReceipt.sha256 -ceq 'afe51ffcc48b94ca9e81b4fbdfc54ab5d6c4e434213874573cf9e7d50c595497' -and
                [string]$receipt.writerExclusionMethod -clike 'Windows FileStream deny-write handles on every existing replacement target and install manifest;*') { $atlasAdditionReceipt = $true }
        }
    }
    if (-not $verifiedReceiptChain -or -not $atlasAdditionReceipt -or
        ([string]$verifyEntries[0].sha256).ToLowerInvariant() -cne '151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3') {
        throw 'Prior V05 verify.py or atlas addition receipts are missing or inconsistent.'
    }
    $priorSourceBytes = [byte[]](Get-HistoricBlobBytes -Commit 'ee51d899df149cb559184f4617537e1e6cb7dc6e' -RelativePath $verifyPath)
    $priorSourceText = [Text.UTF8Encoding]::new($false, $true).GetString($priorSourceBytes)
    $priorCanonicalLf = $priorSourceText.Replace("`r`n", "`n")
    $priorCanonicalCrlf = [Text.UTF8Encoding]::new($false).GetBytes($priorCanonicalLf.Replace("`n", "`r`n"))
    if ((Get-Sha256Bytes $priorCanonicalCrlf) -cne '151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3') { throw 'Prior V05 verify.py receipt does not reproduce exact source-at-install bytes.' }
    if ((Get-Sha256 (Join-Path $runtimeRoot ($verifyPath.Replace('/', [IO.Path]::DirectorySeparatorChar)))) -cne '151a95682b83ffdc9fe44368ab7ddf04c5dd89923e8a4192297019b02fc525a3') { throw 'Installed verify.py no longer matches its prior successful V05 receipt.' }
    $verifyRepairAuthorized = $true
}
else { throw 'Historical verify.py repair requires the exact legacy manifest or the exact prior V05 receipt manifest.' }
if ($verifyRepairAuthorized) { $authorizedRepairHashes[$verifyPath] = $historicVerifyHash }
$overlayAdditions = @()
$plan = @()
$manifestDrift = @()
foreach ($relative in $relativePaths) {
    $isAtlasPath = $relative -ceq 'src/scrubbots_pixel_factory/pixellab_pro_atlas.py'
    $isNewManagedPath = $isAtlasPath -and -not $managed.ContainsKey($relative)
    if (-not $managed.ContainsKey($relative) -and -not $isNewManagedPath) { throw "Manifest does not own the managed target: $relative" }
    if (@($manifest.overlayPaths) -cnotcontains $relative) {
        if ($relative -cnotin $authorizedOverlayAdditions) { throw "Installed overlay allowlist does not include: $relative" }
        $overlayAdditions += $relative
    }
    $source = Join-Path $repoRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
    $target = Join-Path $runtimeRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Source file is missing: $relative" }
    $targetExists = Test-Path -LiteralPath $target -PathType Leaf
    if ($targetExists) { Assert-NoReparsePath $target }
    elseif (-not $isNewManagedPath) { throw "Installed managed target is missing: $relative" }
    elseif (Test-Path -LiteralPath $target) { throw "New managed target path is occupied by a non-file owner object: $relative" }
    $installedHash = if ($targetExists) { Get-Sha256 $target } else { $null }
    $expectedInstalledHash = if ($managed.ContainsKey($relative)) { ([string]$managed[$relative].sha256).ToLowerInvariant() } else { $null }
    $pathReceipts = @($manifest.overlayReceipts | ForEach-Object {
        if ($_.PSObject.Properties.Name -contains 'files') { $_.files }
    } | Where-Object { $_.path -ceq $relative })
    $hasOverlayPath = $relative -cin @($manifest.overlayPaths)
    $hashDisposition = if ($targetExists) { Get-ScopedInstallHashDisposition -RelativePath $relative -ExpectedHash $expectedInstalledHash -InstalledHash $installedHash -AuthorizedRepairHashes $authorizedRepairHashes } else { 'AUTHORIZED_NEW' }
    if ($hashDisposition -eq 'UNKNOWN_DRIFT') {
            $known = $knownProvenanceHashes[$relative]
            $reason = if ($known -and $installedHash -ceq $known.sha256) { $known.disposition } else { 'UNRECOGNIZED_INSTALLED_BYTES' }
            $manifestDrift += [pscustomobject]@{
                path = $relative
                manifestSha256 = $expectedInstalledHash
                installedSha256 = $installedHash
                sourceSha256 = Get-Sha256 $source
                overlayPath = $hasOverlayPath
                overlayReceiptCount = $pathReceipts.Count
                provenance = $reason
                sourceCommit = if ($known) { $known.sourceCommit } else { $null }
            }
            continue
    }
    $sourceHash = Get-Sha256 $source
    if ($targetExists -and $installedHash -ceq $sourceHash) { continue }
    $plan += [pscustomobject]@{ path = $relative; source = $source; target = $target; manifestSha256 = $expectedInstalledHash; installedSha256 = $installedHash; sourceSha256 = $sourceHash; overlayPath = $hasOverlayPath; overlayReceiptCount = $pathReceipts.Count; priorSha256 = $installedHash; priorExists = $targetExists; sha256 = $sourceHash; bytes = (Get-Item -LiteralPath $source).Length }
}
$plannedPaths = @($plan | ForEach-Object { [string]$_.path })
$driftPaths = @($manifestDrift | ForEach-Object { [string]$_.path })

[pscustomobject]@{
    state = if ($manifestDrift.Count -gt 0) { 'BLOCKED_MANIFEST_DRIFT' } elseif ($Apply) { 'APPLY_TRANSACTION_GATED' } else { 'PREFLIGHT_ONLY' }
    sourceHead = $head
    runtimeRoot = $runtimeRoot
    processInventoryStatus = if ($Apply) { 'DEFERRED_TO_LOCKED_TRANSACTION_GATE' } else { 'NOT_QUERIED' }
    overlayAllowlistAdditions = $overlayAdditions
    plannedFiles = $plan
    manifestDrift = $manifestDrift
    unchangedFiles = @($relativePaths | Where-Object { $_ -notin $plannedPaths -and $_ -notin $driftPaths })
} | ConvertTo-Json -Depth 8

$gateResult = Assert-ScopedInstallApplyGates -ManifestDrift $manifestDrift -Apply:$false -ProcessState $null
if (-not $Apply) { return }
if ($plan.Count -eq 0 -and $overlayAdditions.Count -eq 0) {
	Write-ScopedOverlayOutcome -Result ([pscustomobject]@{ status = 'NO_OP'; changedPaths = @() })
	return
}

$transactionRoot = Join-Path $runtimeRoot ('.lf-scoped-overlay-' + [Guid]::NewGuid().ToString('N'))
if (-not $transactionRoot.StartsWith($runtimeRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Transaction path escaped the installed runtime.' }
$fileOperations = @{
    CreateDirectory = { param($path) [IO.Directory]::CreateDirectory($path) }
    ReadBytes = { param($path) [IO.File]::ReadAllBytes($path) }
    WriteBytes = { param($path,$bytes) [IO.File]::WriteAllBytes($path,[byte[]]$bytes) }
    WriteText = { param($path,$value) [IO.File]::WriteAllText($path,[string]$value,[Text.UTF8Encoding]::new($false)) }
    ReadText = { param($path) Get-Content -LiteralPath $path -Raw }
    Hash = { param($path) Get-Sha256 $path }
    Exists = { param($path) Test-Path -LiteralPath $path -PathType Leaf }
    Replace = { param($stage,$target,$backup) [IO.File]::Replace($stage,$target,$backup) }
    RemoveTree = { param($path) Remove-Item -LiteralPath $path -Recurse -Force }
    MoveNew = { param($stage,$target) [IO.File]::Move($stage,$target) }
    DeleteFile = { param($path) [IO.File]::Delete($path) }
    AcquireWriterExclusion = { param($livePaths,$stagePaths) Acquire-ScopedWriterExclusion -LivePaths $livePaths -StagedPaths $stagePaths -ProbeScriptPath (Join-Path $PSScriptRoot 'probe_scoped_writer_lock.ps1') -PowerShellPath (Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe') }
    ReleaseWriterExclusion = { param($lease) Release-ScopedWriterExclusion -Lease $lease }
    GetProcessSnapshot = {
        try {
            $freshInventory = @(Get-CimInstance Win32_Process -ErrorAction Stop)
            Get-ScopedProcessInventoryState -Processes $freshInventory -RuntimeRoot $runtimeRoot -CurrentPid $PID
        } catch {
            [pscustomobject]@{ complete = $false; status = 'PROCESS_INVENTORY_INCOMPLETE'; problems = @("CIM_QUERY_FAILED:$($_.Exception.Message)"); active = @() }
        }
    }
}
$result = Invoke-ScopedOverlayTransaction -Plan $plan -Manifest $manifest -ManifestPath $manifestPath -TransactionRoot $transactionRoot -SourceHead $head -OverlayAdditions $overlayAdditions -Operations $fileOperations -NewManagedPaths @('src/scrubbots_pixel_factory/pixellab_pro_atlas.py')
Write-ScopedOverlayOutcome -Result $result
