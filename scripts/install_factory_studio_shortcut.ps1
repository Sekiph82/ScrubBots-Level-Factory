[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$canonicalOrigin = 'https://github.com/Sekiph82/ScrubBots-Level-Factory.git'
$runtimeRoot = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\Release\ScrubBots Factory Studio'
$releaseRoot = Split-Path -Parent $runtimeRoot
$shortcutPath = Join-Path (Join-Path $env:USERPROFILE 'Desktop') 'ScrubBots Factory Studio.lnk'
$ownerIconPath = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\ScrubBots_Factory_Studio.ico'
$repositoryIconRelativePath = 'level_factory/assets/icons/ScrubBots_Factory_Studio.ico'
$manifestName = '.factory-studio-install-manifest.json'
$manifestPath = Join-Path $runtimeRoot $manifestName
$powerShellPath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

function Get-NormalizedPath {
    param([Parameter(Mandatory)][string]$Path)

    return [System.IO.Path]::GetFullPath($Path).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
}

function Test-PathWithin {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Parent
    )

    $normalizedPath = Get-NormalizedPath -Path $Path
    $normalizedParent = (Get-NormalizedPath -Path $Parent) + [System.IO.Path]::DirectorySeparatorChar
    return $normalizedPath.StartsWith($normalizedParent, [System.StringComparison]::OrdinalIgnoreCase)
}

function Assert-SafeRelativePath {
    param([Parameter(Mandatory)][string]$RelativePath)

    if ([string]::IsNullOrWhiteSpace($RelativePath) -or $RelativePath.Contains("`n") -or $RelativePath.Contains("`r")) {
        throw "Invalid managed path in source/manifest: $RelativePath"
    }
    $portablePath = $RelativePath.Replace('\', '/')
    if ($portablePath.StartsWith('/') -or $portablePath -match '^[A-Za-z]:' -or ($portablePath -split '/') -contains '..') {
        throw "Managed path escapes the runtime root: $RelativePath"
    }
    if ($portablePath -ieq $manifestName) {
        throw "Source repository reserves the local installer manifest path: $RelativePath"
    }
    return $portablePath
}

function Get-FileSha256 {
    param([Parameter(Mandatory)][string]$Path)

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-ManagedSource {
    param([Parameter(Mandatory)][string]$SourceRoot)

    $gitDirectory = Join-Path $SourceRoot '.git'
    if (Test-Path -LiteralPath $gitDirectory) {
        $originOutput = & git -C $SourceRoot remote get-url origin 2>$null
        $originExitCode = $LASTEXITCODE
        $origin = ($originOutput -join "`n").Trim()
        if ($originExitCode -ne 0 -or $origin.TrimEnd('/') -ine $canonicalOrigin.TrimEnd('/')) {
            throw "Source root is not the canonical Factory repository: $SourceRoot"
        }
        $revision = (& git -C $SourceRoot rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($revision)) {
            throw 'Could not resolve the source Git revision.'
        }
        $publishedRevision = (& git -C $SourceRoot rev-parse origin/main 2>$null).Trim()
        if ($LASTEXITCODE -ne 0 -or $publishedRevision -ine $revision) {
            throw "Source revision $revision is not the current fetched origin/main revision. Fetch and publish first."
        }
        $dirtyTrackedFiles = & git -C $SourceRoot status --porcelain=v1 --untracked-files=no
        if ($LASTEXITCODE -ne 0 -or $dirtyTrackedFiles) {
            throw 'Source repository has tracked modifications; install only a published clean revision.'
        }
        $trackedPaths = @(& git -C $SourceRoot ls-files --cached)
        if ($LASTEXITCODE -ne 0 -or $trackedPaths.Count -eq 0) {
            throw 'Could not enumerate tracked source files for the runtime installation.'
        }
    }
    else {
        $sourceManifestPath = Join-Path $SourceRoot $manifestName
        if (-not (Test-Path -LiteralPath $sourceManifestPath -PathType Leaf)) {
            throw "Source is not a Git checkout or a managed installed runtime: $SourceRoot"
        }
        $sourceManifest = Get-Content -LiteralPath $sourceManifestPath -Raw | ConvertFrom-Json
        if ($sourceManifest.formatVersion -ne 1 -or [string]::IsNullOrWhiteSpace([string]$sourceManifest.sourceRevision)) {
            throw "Installed runtime manifest is invalid: $sourceManifestPath"
        }
        $revision = [string]$sourceManifest.sourceRevision
        $trackedPaths = @($sourceManifest.managedFiles | ForEach-Object { [string]$_.path })
        if ($trackedPaths.Count -eq 0) {
            throw 'Installed runtime manifest contains no managed source files.'
        }
    }

    $files = @()
    foreach ($rawPath in $trackedPaths) {
        $relativePath = Assert-SafeRelativePath -RelativePath ([string]$rawPath)
        $sourcePath = Join-Path $SourceRoot ($relativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
            throw "Tracked runtime source is missing: $sourcePath"
        }
        $files += [PSCustomObject]@{
            Path = $relativePath
            SourcePath = $sourcePath
            Sha256 = Get-FileSha256 -Path $sourcePath
        }
    }
    return [PSCustomObject]@{ Revision = $revision; Files = $files }
}

function Get-PreviousManifest {
    if (-not (Test-Path -LiteralPath $runtimeRoot -PathType Container)) {
        return $null
    }
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Runtime destination already contains unknown owner data without an installer manifest; preserved it and stopped: $runtimeRoot"
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.formatVersion -ne 1 -or [string]::IsNullOrWhiteSpace([string]$manifest.sourceRevision) -or $null -eq $manifest.managedFiles) {
        throw "Runtime installer manifest is invalid; preserved destination and stopped: $manifestPath"
    }
    return $manifest
}

function Assert-NoReparsePoint {
    param([Parameter(Mandatory)][string]$Path)

    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Refusing to follow an owner-created reparse point: $Path"
    }
}

function Assert-NoRuntimeReparsePath {
    param([Parameter(Mandatory)][string]$Path)

    $normalizedPath = Get-NormalizedPath -Path $Path
    $normalizedRoot = Get-NormalizedPath -Path $runtimeRoot
    $cursor = $normalizedPath
    while ($cursor -and ($cursor.Equals($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase) -or (Test-PathWithin -Path $cursor -Parent $normalizedRoot))) {
        Assert-NoReparsePoint -Path $cursor
        if ($cursor.Equals($normalizedRoot, [System.StringComparison]::OrdinalIgnoreCase)) { break }
        $cursor = Split-Path -Parent $cursor
    }
}

function Get-ManifestFileMap {
    param([Parameter()][object]$Manifest)

    $map = @{}
    if ($null -eq $Manifest) { return $map }
    foreach ($entry in $Manifest.managedFiles) {
        $relativePath = Assert-SafeRelativePath -RelativePath ([string]$entry.path)
        $sha256 = [string]$entry.sha256
        if ($sha256 -notmatch '^[0-9a-fA-F]{64}$' -or $map.ContainsKey($relativePath)) {
            throw "Runtime manifest has an invalid or duplicate managed file: $relativePath"
        }
        $map[$relativePath] = $sha256.ToLowerInvariant()
    }
    return $map
}

function Get-RuntimePath {
    param([Parameter(Mandatory)][string]$RelativePath)

    $relativePath = Assert-SafeRelativePath -RelativePath $RelativePath
    $targetPath = Join-Path $runtimeRoot ($relativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
    if (-not (Test-PathWithin -Path $targetPath -Parent $runtimeRoot)) {
        throw "Target path escapes the runtime root: $RelativePath"
    }
    return $targetPath
}

if (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'scripts\launch_factory_studio.ps1') -PathType Leaf)) {
    throw "Committed launcher script is missing: $repoRoot"
}
if (-not (Test-Path -LiteralPath $powerShellPath -PathType Leaf)) {
    throw "Windows PowerShell executable is missing: $powerShellPath"
}
$tempRoot = Get-NormalizedPath -Path $env:TEMP
if (Test-PathWithin -Path $runtimeRoot -Parent $tempRoot) {
    throw "Factory Studio runtime may not be installed under TEMP: $runtimeRoot"
}
Assert-NoReparsePoint -Path $releaseRoot
Assert-NoReparsePoint -Path $runtimeRoot

$source = Get-ManagedSource -SourceRoot $repoRoot
$previousManifest = Get-PreviousManifest
$previousFiles = Get-ManifestFileMap -Manifest $previousManifest
$sourcePaths = @{}
foreach ($file in $source.Files) { $sourcePaths[$file.Path] = $file }

$ownerIconSource = Join-Path $repoRoot $repositoryIconRelativePath
if (-not (Test-Path -LiteralPath $ownerIconPath -PathType Leaf)) {
    throw "Owner-authoritative ICO is missing: $ownerIconPath"
}
if (-not (Test-Path -LiteralPath $ownerIconSource -PathType Leaf) -or (Get-FileSha256 -Path $ownerIconSource) -ne (Get-FileSha256 -Path $ownerIconPath)) {
    throw 'Committed runtime ICO does not match the owner-authoritative ICO; preserved existing shortcut and stopped.'
}
$stableIconPath = Get-RuntimePath -RelativePath $repositoryIconRelativePath

# Preflight all existing managed files and path collisions before writing anything.
foreach ($relativePath in $previousFiles.Keys) {
    $path = Get-RuntimePath -RelativePath $relativePath
    Assert-NoRuntimeReparsePath -Path $path
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Previously managed runtime file is missing; preserved destination and stopped: $path"
    }
    Assert-NoReparsePoint -Path $path
    if ((Get-FileSha256 -Path $path) -ne $previousFiles[$relativePath]) {
        throw "Previously managed runtime file was modified; preserved owner data and stopped: $path"
    }
}
foreach ($relativePath in $sourcePaths.Keys) {
    $path = Get-RuntimePath -RelativePath $relativePath
    Assert-NoRuntimeReparsePath -Path $path
    if (Test-Path -LiteralPath $path) {
        Assert-NoReparsePoint -Path $path
        if (-not $previousFiles.ContainsKey($relativePath)) {
            throw "Unmanaged owner file conflicts with a new runtime file; preserved destination and stopped: $path"
        }
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "A directory conflicts with a runtime file; preserved destination and stopped: $path"
        }
    }
}
if ((Test-Path -LiteralPath $runtimeRoot) -and (Test-Path -LiteralPath $manifestPath) -and -not $previousManifest) {
    throw "Runtime manifest collision; preserved destination and stopped: $manifestPath"
}

if (-not (Test-Path -LiteralPath $releaseRoot -PathType Container)) {
    New-Item -ItemType Directory -Path $releaseRoot -Force | Out-Null
}
if (-not (Test-Path -LiteralPath $runtimeRoot -PathType Container)) {
    New-Item -ItemType Directory -Path $runtimeRoot | Out-Null
}

$stageRoot = Join-Path $runtimeRoot ('.factory-studio-stage-' + [guid]::NewGuid().ToString('N'))
if (Test-Path -LiteralPath $stageRoot) { throw "Unexpected staging path collision: $stageRoot" }
New-Item -ItemType Directory -Path $stageRoot | Out-Null
$stagedSource = Join-Path $stageRoot 'source'
$backupRoot = Join-Path $stageRoot 'backup'
New-Item -ItemType Directory -Path $stagedSource | Out-Null
New-Item -ItemType Directory -Path $backupRoot | Out-Null
$changedPaths = [System.Collections.Generic.List[string]]::new()
$markerBackedUp = $false
$markerPreviouslyExisted = Test-Path -LiteralPath $manifestPath -PathType Leaf
try {
    foreach ($file in $source.Files) {
        $stagePath = Join-Path $stagedSource ($file.Path.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
        New-Item -ItemType Directory -Path (Split-Path -Parent $stagePath) -Force | Out-Null
        Copy-Item -LiteralPath $file.SourcePath -Destination $stagePath
        if ((Get-FileSha256 -Path $stagePath) -ne $file.Sha256) { throw "Staged source hash mismatch: $($file.Path)" }
    }
    if ($markerPreviouslyExisted) {
        Copy-Item -LiteralPath $manifestPath -Destination (Join-Path $backupRoot $manifestName)
        $markerBackedUp = $true
    }
    foreach ($file in $source.Files) {
        if ($previousFiles.ContainsKey($file.Path) -and $previousFiles[$file.Path] -eq $file.Sha256) {
            continue
        }
        $targetPath = Get-RuntimePath -RelativePath $file.Path
        New-Item -ItemType Directory -Path (Split-Path -Parent $targetPath) -Force | Out-Null
        if (Test-Path -LiteralPath $targetPath -PathType Leaf) {
            $backupPath = Join-Path $backupRoot ($file.Path.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
            New-Item -ItemType Directory -Path (Split-Path -Parent $backupPath) -Force | Out-Null
            Copy-Item -LiteralPath $targetPath -Destination $backupPath
        }
        $changedPaths.Add($file.Path)
        Copy-Item -LiteralPath (Join-Path $stagedSource ($file.Path.Replace('/', [System.IO.Path]::DirectorySeparatorChar))) -Destination $targetPath -Force
    }
    foreach ($relativePath in $previousFiles.Keys) {
        if (-not $sourcePaths.ContainsKey($relativePath)) {
            $targetPath = Get-RuntimePath -RelativePath $relativePath
            $backupPath = Join-Path $backupRoot ($relativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
            New-Item -ItemType Directory -Path (Split-Path -Parent $backupPath) -Force | Out-Null
            Copy-Item -LiteralPath $targetPath -Destination $backupPath
            Remove-Item -LiteralPath $targetPath -Force
            $changedPaths.Add($relativePath)
        }
    }
    $newManifest = [ordered]@{
        formatVersion = 1
        sourceRevision = $source.Revision
        managedFiles = @($source.Files | ForEach-Object { [ordered]@{ path = $_.Path; sha256 = $_.Sha256 } })
    }
    $stagedManifest = Join-Path $stageRoot $manifestName
    $newManifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $stagedManifest -Encoding utf8
    Move-Item -LiteralPath $stagedManifest -Destination $manifestPath -Force
}
catch {
    foreach ($relativePath in @($changedPaths.ToArray()) | Select-Object -Reverse) {
        $targetPath = Get-RuntimePath -RelativePath $relativePath
        $backupPath = Join-Path $backupRoot ($relativePath.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
        if (Test-Path -LiteralPath $backupPath -PathType Leaf) {
            Copy-Item -LiteralPath $backupPath -Destination $targetPath -Force
        }
        elseif (Test-Path -LiteralPath $targetPath -PathType Leaf) {
            Remove-Item -LiteralPath $targetPath -Force
        }
    }
    if ($markerBackedUp) {
        Copy-Item -LiteralPath (Join-Path $backupRoot $manifestName) -Destination $manifestPath -Force
    }
    elseif (-not $markerPreviouslyExisted -and (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        Remove-Item -LiteralPath $manifestPath -Force
    }
    throw
}
finally {
    $normalizedStage = Get-NormalizedPath -Path $stageRoot
    if ((Test-PathWithin -Path $normalizedStage -Parent $runtimeRoot) -and (Test-Path -LiteralPath $stageRoot -PathType Container)) {
        Remove-Item -LiteralPath $stageRoot -Recurse -Force
    }
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $powerShellPath
$quotedLauncherPath = '"{0}"' -f (Join-Path $runtimeRoot 'scripts\launch_factory_studio.ps1')
$arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File {0}' -f $quotedLauncherPath
$shortcut.Arguments = $arguments
$shortcut.WorkingDirectory = $runtimeRoot
$shortcut.Description = 'ScrubBots Factory Studio'
$shortcut.IconLocation = '{0},0' -f $stableIconPath
$shortcut.Save()

Write-Output $shortcutPath
