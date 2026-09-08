$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$pythonCommand = $null
$pythonPrefixArgs = @()
$pythonVersion = $null
$pythonExecutable = $null
$versionProbe = "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'); print(sys.executable)"

$pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
if ($null -ne $pyLauncher) {
    $launcherProbe = @(& $pyLauncher.Source -3.12 -c $versionProbe 2>&1)
    $launcherExitCode = $LASTEXITCODE
    if ($launcherExitCode -eq 0 -and $launcherProbe.Count -ge 2) {
        $pythonCommand = $pyLauncher.Source
        $pythonPrefixArgs = @("-3.12")
        $pythonVersion = [string]$launcherProbe[0]
        $pythonExecutable = [string]$launcherProbe[1]
        Write-Output "Selected Python via py.exe -3.12: $pythonVersion ($pythonExecutable)"
    } else {
        Write-Output "py.exe -3.12 was unavailable; checking python.exe after version validation."
    }
}

if ($null -eq $pythonCommand) {
    $pythonCommandInfo = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($null -ne $pythonCommandInfo) {
        $pythonProbe = @(& $pythonCommandInfo.Source -c $versionProbe 2>&1)
        $pythonExitCode = $LASTEXITCODE
        if ($pythonExitCode -eq 0 -and $pythonProbe.Count -ge 2) {
            $candidateVersion = [string]$pythonProbe[0]
            $candidateParts = $candidateVersion.Split(".")
            if ($candidateParts.Count -eq 3 -and $candidateParts[0] -eq "3" -and $candidateParts[1] -eq "12") {
                $pythonCommand = $pythonCommandInfo.Source
                $pythonVersion = $candidateVersion
                $pythonExecutable = [string]$pythonProbe[1]
                Write-Output "Selected validated python.exe: $pythonVersion ($pythonExecutable)"
            } else {
                Write-Output "python.exe reported unsupported Python $candidateVersion; Python 3.12 is required."
            }
        } else {
            Write-Output "python.exe could not report a usable runtime version; Python 3.12 is required."
        }
    }
}

if ($null -eq $pythonCommand) {
    throw "Python 3.12 is required (metadata supports >=3.12,<3.13). Install Python 3.12 or enable the py.exe -3.12 launcher, then rerun this command."
}

$venvPath = Join-Path $repoRoot ".venv"
if (Test-Path -LiteralPath $venvPath) {
    Write-Output "Clearing repository-local .venv only: $venvPath"
}

& $pythonCommand @pythonPrefixArgs -m venv --clear $venvPath
if ($LASTEXITCODE -ne 0) {
    throw "Python $pythonVersion could not create the repository-local .venv at $venvPath."
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "The repository-local .venv was not created successfully at $venvPath."
}

$venvProbe = @(& $venvPython -c $versionProbe 2>&1)
$venvExitCode = $LASTEXITCODE
$venvVersion = [string]$venvProbe[0]
if ($venvExitCode -ne 0 -or $venvVersion -notmatch '^3\.12\.') {
    throw "The created .venv reported unsupported Python $venvVersion; Python 3.12 is required."
}
Write-Output "Repository .venv Python: $venvVersion ($venvPython)"

& $venvPython -m pip install -e ".[test]"
if ($LASTEXITCODE -ne 0) {
    throw "Editable package/test installation failed in the repository-local .venv."
}

Write-Output "Environment ready: $venvPython"
