[CmdletBinding()]
param(
    [switch]$ResolveOnly
)

$ErrorActionPreference = 'Stop'

function Get-FullPathForIdentity {
    param([Parameter(Mandatory)][string]$Path)
    return [IO.Path]::GetFullPath($Path).TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
}

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

    $godotSha256 = (Get-FileHash -LiteralPath $godotPath -Algorithm SHA256).Hash
    $quotedProjectPath = '"{0}"' -f $projectPath
    $studioProcess = Start-Process -FilePath $godotPath -ArgumentList @('--path', $quotedProjectPath) -WorkingDirectory $repoRoot -PassThru
    $studioProcessId = $studioProcess.Id
    $windowTitle = 'ScrubBots Factory Studio'
    $allowedWindowTitles = @($windowTitle, "$windowTitle (DEBUG)")
    if (-not ('FactoryStudioNativeWindowTitle' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class FactoryStudioNativeWindowTitle {
    [DllImport("user32.dll", CharSet = CharSet.Unicode, EntryPoint = "SetWindowTextW", SetLastError = true)]
    public static extern bool SetWindowText(IntPtr windowHandle, string windowTitle);
    [DllImport("user32.dll", EntryPoint = "GetWindowThreadProcessId", SetLastError = true)]
    public static extern uint GetWindowThreadProcessId(IntPtr windowHandle, out uint processId);
}
'@
    }

    $windowHandle = [IntPtr]::Zero
    $titleVerified = $false
    $titleSetAttempted = $false
    $lastWindowTitle = ''
    $processIdentityVerified = $false
    $expectedProjectPath = Get-FullPathForIdentity $projectPath
    $projectArgumentPattern = '(?i)(?:^|\s)--path\s+"' + [regex]::Escape($expectedProjectPath) + '"(?:\s|$)'
    for ($attempt = 0; $attempt -lt 80; $attempt++) {
        $studioProcess = Get-Process -Id $studioProcessId -ErrorAction Stop
        if ($studioProcess.HasExited) {
            throw 'Godot exited before the Studio window was ready.'
        }
        if (-not $processIdentityVerified) {
            $processIdentity = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = $studioProcessId" -ErrorAction Stop
            if ($null -eq $processIdentity -or -not (Test-Path -LiteralPath $processIdentity.ExecutablePath -PathType Leaf)) {
                throw 'Factory Studio process executable identity could not be read.'
            }
            if (-not (Test-Godot4Executable -Candidate $processIdentity.ExecutablePath) -or
                    (Get-FileHash -LiteralPath $processIdentity.ExecutablePath -Algorithm SHA256).Hash -ne $godotSha256) {
                throw 'Factory Studio process did not start from the exact approved Godot 4 executable.'
            }
            if ($processIdentity.CommandLine -notmatch $projectArgumentPattern) {
                throw 'Factory Studio process was not launched with the exact approved Release project path.'
            }
            $processIdentityVerified = $true
        }
        $windowHandle = $studioProcess.MainWindowHandle
        if ($windowHandle -ne [IntPtr]::Zero) {
            [uint32]$windowProcessId = 0
            [void][FactoryStudioNativeWindowTitle]::GetWindowThreadProcessId($windowHandle, [ref]$windowProcessId)
            if ([int]$windowProcessId -ne $studioProcessId) {
                throw 'Factory Studio main window handle belongs to a different process.'
            }
            $studioProcess.Refresh()
            $lastWindowTitle = $studioProcess.MainWindowTitle
            if ($allowedWindowTitles -ccontains $lastWindowTitle) {
                $titleVerified = $true
                break
            }
            if (-not $titleSetAttempted) {
                [void][FactoryStudioNativeWindowTitle]::SetWindowText($windowHandle, $windowTitle)
                $titleSetAttempted = $true
            }
        }
        Start-Sleep -Milliseconds 125
    }
    if ($windowHandle -eq [IntPtr]::Zero) {
        throw 'Factory Studio did not create a main window within 10 seconds.'
    }
    if (-not $titleVerified) {
        throw "Factory Studio window title was not an approved exact title. Last title: '$lastWindowTitle'."
    }
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
