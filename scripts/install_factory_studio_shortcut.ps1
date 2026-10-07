[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$launcherPath = Join-Path $repoRoot 'scripts\launch_factory_studio.ps1'
$shortcutPath = Join-Path (Join-Path $env:USERPROFILE 'Desktop') 'ScrubBots Factory Studio.lnk'
$ownerIconPath = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\ScrubBots_Factory_Studio.ico'
$repositoryIconPath = Join-Path $repoRoot 'level_factory\assets\icons\ScrubBots_Factory_Studio.ico'
$powerShellPath = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'

if (-not (Test-Path -LiteralPath $launcherPath -PathType Leaf)) {
    throw "Committed launcher script is missing: $launcherPath"
}
if (-not (Test-Path -LiteralPath $powerShellPath -PathType Leaf)) {
    throw "Windows PowerShell executable is missing: $powerShellPath"
}

$iconPath = $ownerIconPath
if (-not (Test-Path -LiteralPath $iconPath -PathType Leaf)) {
    if (-not (Test-Path -LiteralPath $repositoryIconPath -PathType Leaf)) {
        throw "The owner ICO and committed fallback ICO are both missing: $ownerIconPath ; $repositoryIconPath"
    }
    $iconPath = $repositoryIconPath
}

$desktopPath = Split-Path -Parent $shortcutPath
if (-not (Test-Path -LiteralPath $desktopPath -PathType Container)) {
    New-Item -ItemType Directory -Path $desktopPath -Force | Out-Null
}

$quotedLauncherPath = '"{0}"' -f $launcherPath
$arguments = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File {0}' -f $quotedLauncherPath
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $powerShellPath
$shortcut.Arguments = $arguments
$shortcut.WorkingDirectory = $repoRoot
$shortcut.Description = 'ScrubBots Factory Studio'
$shortcut.IconLocation = '{0},0' -f $iconPath
$shortcut.Save()

Write-Output $shortcutPath
