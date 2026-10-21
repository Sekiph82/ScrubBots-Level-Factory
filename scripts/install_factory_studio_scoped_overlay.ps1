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
    $hashDisposition = Get-ScopedInstallHashDisposition -RelativePath $relative -ExpectedHash $expectedInstalledHash -InstalledHash $installedHash -AuthorizedRepairHashes $authorizedRepairHashes
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
    if ($installedHash -ceq $sourceHash) { continue }
    $plan += [pscustomobject]@{ path = $relative; source = $source; target = $target; manifestSha256 = $expectedInstalledHash; installedSha256 = $installedHash; sourceSha256 = $sourceHash; overlayPath = $hasOverlayPath; overlayReceiptCount = $pathReceipts.Count; priorSha256 = $installedHash; sha256 = $sourceHash; bytes = (Get-Item -LiteralPath $source).Length }
}

$processQueryError = $null
try { $processInventory = @(Get-CimInstance Win32_Process -ErrorAction Stop) }
catch { $processInventory = @(); $processQueryError = $_.Exception.Message }
$processState = if ($processQueryError) {
    [pscustomobject]@{ complete = $false; status = 'PROCESS_INVENTORY_INCOMPLETE'; problems = @("CIM_QUERY_FAILED:$processQueryError"); active = @() }
} else {
    Get-ScopedProcessInventoryState -Processes $processInventory -RuntimeRoot $runtimeRoot -CurrentPid $PID
}
$active = @($processState.active)

[pscustomobject]@{
    state = if ($manifestDrift.Count -gt 0) { 'BLOCKED_MANIFEST_DRIFT' } elseif ($Apply) { 'APPLY_READY' } else { 'PREFLIGHT_ONLY' }
    sourceHead = $head
    runtimeRoot = $runtimeRoot
    processInventoryStatus = $processState.status
    processInventoryProblems = $processState.problems
    activeRuntimeProcesses = @($active | ForEach-Object { [pscustomobject]@{ pid = $_.ProcessId; name = $_.Name; executablePath = $_.ExecutablePath; parentPid = $_.ParentProcessId; commandLine = $_.CommandLine } })
    overlayAllowlistAdditions = $overlayAdditions
    plannedFiles = $plan
    manifestDrift = $manifestDrift
    unchangedFiles = @($relativePaths | Where-Object { $_ -notin @($plan.path) -and $_ -notin @($manifestDrift.path) })
} | ConvertTo-Json -Depth 8

$gateResult = Assert-ScopedInstallApplyGates -ManifestDrift $manifestDrift -Apply:$Apply -ProcessState $processState
if (-not $Apply -or ($plan.Count -eq 0 -and $overlayAdditions.Count -eq 0)) { return }

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
}
$result = Invoke-ScopedOverlayTransaction -Plan $plan -Manifest $manifest -ManifestPath $manifestPath -TransactionRoot $transactionRoot -SourceHead $head -OverlayAdditions $overlayAdditions -Operations $fileOperations
if ($result.status -eq 'COMMITTED') { 'OWNER_DESKTOP_STUDIO_SCOPED_OVERLAY_UPDATED' }
