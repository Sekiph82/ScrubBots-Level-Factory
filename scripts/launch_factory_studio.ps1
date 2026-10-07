[CmdletBinding()]
param(
    [switch]$ResolveOnly
)

$ErrorActionPreference = 'Stop'

function Test-Godot4Executable {
    param([Parameter(Mandatory)][string]$Candidate)

    if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf) -or [IO.Path]::GetExtension($Candidate) -ine '.exe') {
        return $false
    }
    $versionInfo = (Get-Item -LiteralPath $Candidate).VersionInfo
    return ($versionInfo.FileDescription -match '^Godot Engine' -and $versionInfo.ProductVersion -match '^4(?:\.|$)')
}

function Resolve-GodotExecutable {
    $override = [Environment]::GetEnvironmentVariable('SCRUBBOTS_FACTORY_GODOT')
    if (-not [string]::IsNullOrWhiteSpace($override)) {
        if (-not (Test-Path -LiteralPath $override -PathType Leaf)) {
            throw "SCRUBBOTS_FACTORY_GODOT does not point to a file: $override"
        }
        $candidate = (Resolve-Path -LiteralPath $override).Path
        if (-not (Test-Godot4Executable -Candidate $candidate)) {
            throw "SCRUBBOTS_FACTORY_GODOT must point to a working Godot 4 executable: $candidate"
        }
        return $candidate
    }

    foreach ($commandName in @('godot.exe', 'godot')) {
        $commands = Get-Command -Name $commandName -CommandType Application -All -ErrorAction SilentlyContinue
        foreach ($command in $commands) {
            $candidate = $command.Source
            if ($candidate -and (Test-Godot4Executable -Candidate $candidate)) {
                return (Resolve-Path -LiteralPath $candidate).Path
            }
        }
    }

    $knownLocations = @(
        (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links\godot.exe'),
        (Join-Path $env:ProgramFiles 'Godot\godot.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Godot\godot.exe')
    )
    foreach ($candidate in $knownLocations) {
        if (Test-Godot4Executable -Candidate $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw 'Godot 4 was not found. Install Godot 4 or set SCRUBBOTS_FACTORY_GODOT to its godot.exe path, then retry.'
}

try {
    $repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    $projectPath = Join-Path $repoRoot 'level_factory'
    if (-not (Test-Path -LiteralPath (Join-Path $projectPath 'project.godot') -PathType Leaf)) {
        throw "Factory Studio project.godot is missing: $projectPath"
    }

    $godotPath = Resolve-GodotExecutable
    if ($ResolveOnly) {
        Write-Output $godotPath
        return
    }

    $quotedProjectPath = '"{0}"' -f $projectPath
    Start-Process -FilePath $godotPath -ArgumentList @('--path', $quotedProjectPath) -WorkingDirectory $repoRoot | Out-Null
}
catch {
    $message = "ScrubBots Factory Studio could not start.`r`n`r`n$($_.Exception.Message)"
    if ($ResolveOnly) {
        Write-Error $message
        exit 1
    }
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        [void][System.Windows.Forms.MessageBox]::Show($message, 'ScrubBots Factory Studio', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    }
    catch {
        Write-Error $message
    }
    exit 1
}
