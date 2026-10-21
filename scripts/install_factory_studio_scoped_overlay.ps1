[CmdletBinding()]
param([switch]$Apply)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\')
$expectedRepoRoot = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator'
$canonicalOrigin = 'https://github.com/Sekiph82/ScrubBots-Level-Factory.git'
$runtimeRoot = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio'
$manifestPath = Join-Path $runtimeRoot '.factory-studio-install-manifest.json'
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
    'src/scrubbots_pixel_factory/alpix_batch.py'
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
    'src/scrubbots_pixel_factory/supply_pipeline/supply_optimizer.py'
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
# log records that this mismatch predated scoped installs, and no per-file
# overlay receipt proves an approved transaction. Report this provenance, but
# deliberately do not authorize it as a repair hash.
$knownProvenanceHashes = @{
    'src/scrubbots_pixel_factory/supply_pipeline/verify.py' = @{
        sha256 = '90e560824678fd07055225e5d500a956e7a82f9734263f22d2cc4a7afa190744'
        sourceCommit = '17643de6756ba3d9552351eb237db19bd8d0c269'
        disposition = 'KNOWN_SOURCE_VERSION_APPROVAL_UNPROVEN'
    }
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
$overlayAdditions = @()
$plan = @()
$manifestDrift = @()
foreach ($relative in $relativePaths) {
    if (-not $managed.ContainsKey($relative)) { throw "Manifest does not own the managed target: $relative" }
    if (@($manifest.overlayPaths) -cnotcontains $relative) {
        if ($relative -cnotin $authorizedOverlayAdditions) { throw "Installed overlay allowlist does not include: $relative" }
        $overlayAdditions += $relative
    }
    $source = Join-Path $repoRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
    $target = Join-Path $runtimeRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
    if (-not (Test-Path -LiteralPath $source -PathType Leaf) -or -not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Source or installed target is missing: $relative" }
    Assert-NoReparsePath $target
    $installedHash = Get-Sha256 $target
    $expectedInstalledHash = ([string]$managed[$relative].sha256).ToLowerInvariant()
    $pathReceipts = @($manifest.overlayReceipts | ForEach-Object {
        if ($_.PSObject.Properties.Name -contains 'files') { $_.files }
    } | Where-Object { $_.path -ceq $relative })
    $hasOverlayPath = $relative -cin @($manifest.overlayPaths)
    if ($installedHash -cne $expectedInstalledHash) {
        $authorizedHash = [string]$authorizedRepairHashes[$relative]
        if (-not $authorizedHash -or $installedHash -cne $authorizedHash) {
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
    }
    $sourceHash = Get-Sha256 $source
    if ($installedHash -ceq $sourceHash) { continue }
    $plan += [pscustomobject]@{ path = $relative; source = $source; target = $target; manifestSha256 = $expectedInstalledHash; installedSha256 = $installedHash; sourceSha256 = $sourceHash; overlayPath = $hasOverlayPath; overlayReceiptCount = $pathReceipts.Count; priorSha256 = $installedHash; sha256 = $sourceHash; bytes = (Get-Item -LiteralPath $source).Length }
}

$processInventory = @(Get-CimInstance Win32_Process)
$activeProcessIds = [Collections.Generic.HashSet[uint32]]::new()
$runtimeNeedle = $runtimeRoot.TrimEnd('\')
foreach ($process in $processInventory) {
    $commandLine = [string]$process.CommandLine
    $usesRuntime = $commandLine.IndexOf($runtimeNeedle, [StringComparison]::OrdinalIgnoreCase) -ge 0
    $isStudioOrWriter = $process.Name -like 'Godot*' -or
        $commandLine -match 'factory_core_launcher\.py|png_batch\.py'
    if ($process.ProcessId -ne $PID -and $usesRuntime -and $isStudioOrWriter) {
        [void]$activeProcessIds.Add([uint32]$process.ProcessId)
    }
}
# Include descendants such as Python workers and console hosts even when their
# own command line does not repeat the runtime path.
do {
    $addedProcess = $false
    foreach ($process in $processInventory) {
        if ($process.ProcessId -ne $PID -and $activeProcessIds.Contains([uint32]$process.ParentProcessId)) {
            if ($activeProcessIds.Add([uint32]$process.ProcessId)) { $addedProcess = $true }
        }
    }
} while ($addedProcess)
$active = @($processInventory | Where-Object { $activeProcessIds.Contains([uint32]$_.ProcessId) })
if ($Apply -and $active.Count -gt 0) {
    $ids = ($active | ForEach-Object { "$($_.ProcessId):$($_.Name)" }) -join ', '
    throw "Installed runtime is in use; no files were written. Active processes: $ids"
}

[pscustomobject]@{
    state = if ($manifestDrift.Count -gt 0) { 'BLOCKED_MANIFEST_DRIFT' } elseif ($Apply) { 'APPLY_READY' } else { 'PREFLIGHT_ONLY' }
    sourceHead = $head
    runtimeRoot = $runtimeRoot
    activeRuntimeProcesses = @($active | ForEach-Object { [pscustomobject]@{ pid = $_.ProcessId; name = $_.Name; executablePath = $_.ExecutablePath; parentPid = $_.ParentProcessId; commandLine = $_.CommandLine } })
    overlayAllowlistAdditions = $overlayAdditions
    plannedFiles = $plan
    manifestDrift = $manifestDrift
    unchangedFiles = @($relativePaths | Where-Object { $_ -notin @($plan.path) -and $_ -notin @($manifestDrift.path) })
} | ConvertTo-Json -Depth 8

if ($manifestDrift.Count -gt 0) { throw 'Installed managed bytes differ from manifest without an approved exact repair; no files were written.' }
if (-not $Apply -or ($plan.Count -eq 0 -and $overlayAdditions.Count -eq 0)) { return }

$transactionRoot = Join-Path $runtimeRoot ('.lf-scoped-overlay-' + [Guid]::NewGuid().ToString('N'))
if (-not $transactionRoot.StartsWith($runtimeRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Transaction path escaped the installed runtime.' }
$replaced = @()
$manifestOriginal = [IO.File]::ReadAllBytes($manifestPath)
$manifestReplaced = $false
try {
    [void][IO.Directory]::CreateDirectory($transactionRoot)
    $receiptFiles = @()
    $stagedFiles = @()
    foreach ($item in $plan) {
        $relativeStage = $item.path.Replace('/', [IO.Path]::DirectorySeparatorChar)
        $stage = Join-Path (Join-Path $transactionRoot 'stage') $relativeStage
        $backup = Join-Path (Join-Path $transactionRoot 'backup') $relativeStage
        [void][IO.Directory]::CreateDirectory((Split-Path -Parent $stage))
        [void][IO.Directory]::CreateDirectory((Split-Path -Parent $backup))
        [IO.File]::WriteAllBytes($stage, [IO.File]::ReadAllBytes($item.source))
        if ((Get-Sha256 $stage) -cne $item.sha256) { throw "Staged source hash mismatch: $($item.path)" }
        $stagedFiles += [pscustomobject]@{ stage = $stage; target = $item.target; backup = $backup; relative = $item.path; expected = $item.sha256 }
        $managedEntry = @($manifest.managedFiles | Where-Object path -ceq $item.path)
        $managedEntry[0].sha256 = $item.sha256
        $receiptFiles += [pscustomobject]@{ path = $item.path; priorSha256 = $item.priorSha256; sha256 = $item.sha256; bytes = $item.bytes }
    }
    $receipt = [pscustomobject]@{
        taskId = 'SB-LFX-018-R05-M03'
        sourceCommit = $head
        sourceHead = $head
        files = $receiptFiles
        installedAtUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    }
    $manifest.overlayPaths = @($manifest.overlayPaths) + @($overlayAdditions)
    $manifest.overlayReceipts = @($manifest.overlayReceipts) + @($receipt)
    $manifestStage = Join-Path $transactionRoot '.factory-studio-install-manifest.json'
    $manifestBackup = Join-Path $transactionRoot 'backup-manifest.json'
    [IO.File]::WriteAllText($manifestStage, ($manifest | ConvertTo-Json -Depth 100) + "`n", [Text.UTF8Encoding]::new($false))

    # Stage and verify every payload and the updated manifest before the first
    # owner target is replaced. A staging failure therefore has no live writes.
    foreach ($item in $stagedFiles) {
        [IO.File]::Replace($item.stage, $item.target, $item.backup)
        $replaced += [pscustomobject]@{ target = $item.target; backup = $item.backup; relative = $item.relative; expected = $item.expected }
        if ((Get-Sha256 $item.target) -cne $item.expected) { throw "Installed file hash mismatch after replacement: $($item.relative)" }
    }
    [IO.File]::Replace($manifestStage, $manifestPath, $manifestBackup)
    $manifestReplaced = $true
    $installedManifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($installedManifest.overlayReceipts[-1].sourceHead -cne $head) { throw 'Installed overlay receipt did not verify.' }
    foreach ($item in $plan) {
        if ((Get-Sha256 $item.target) -cne $item.sha256) { throw "Final installed hash mismatch: $($item.path)" }
    }
    Remove-Item -LiteralPath $transactionRoot -Recurse -Force
    'OWNER_DESKTOP_STUDIO_SCOPED_OVERLAY_UPDATED'
}
catch {
    $failure = $_
    if ($manifestReplaced -and (Test-Path -LiteralPath (Join-Path $transactionRoot 'backup-manifest.json'))) {
        [IO.File]::Replace((Join-Path $transactionRoot 'backup-manifest.json'), $manifestPath, $null)
    }
    foreach ($entry in @($replaced | Select-Object -Reverse)) {
        if (Test-Path -LiteralPath $entry.backup) { [IO.File]::Replace($entry.backup, $entry.target, $null) }
    }
    if ($replaced.Count -eq 0 -or @($replaced | Where-Object { Test-Path -LiteralPath $_.backup }).Count -eq 0) {
        Remove-Item -LiteralPath $transactionRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    throw "Scoped overlay update failed and rollback was attempted: $failure"
}
