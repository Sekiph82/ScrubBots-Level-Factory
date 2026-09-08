$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
$pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue

if ($null -ne $pythonCommand) {
    & $pythonCommand.Source -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Python could not create the local .venv."
    }
} elseif ($null -ne $pyLauncher) {
    & $pyLauncher.Source -3.12 -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.12 was not available through the Windows py launcher."
    }
} else {
    throw "Neither python.exe nor the Windows py launcher was found."
}

$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "The local .venv was not created successfully."
}
& $venvPython -m pip install -e ".[test]"
if ($LASTEXITCODE -ne 0) {
    throw "Editable package/test installation failed."
}

Write-Output "Environment ready: $venvPython"
