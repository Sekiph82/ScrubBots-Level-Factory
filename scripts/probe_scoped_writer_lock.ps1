[CmdletBinding()]
param(
	[Parameter(Mandatory)][string]$TargetPath,
	[switch]$ExpectBlocked
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $TargetPath -PathType Leaf)) { exit 92 }

try {
	$stream = [IO.File]::Open($TargetPath, [IO.FileMode]::Open, [IO.FileAccess]::Write, [IO.FileShare]::None)
	$stream.Dispose()
	if ($ExpectBlocked) { exit 91 }
	exit 0
}
catch [IO.IOException] {
	if ($ExpectBlocked) { exit 0 }
	exit 93
}
catch {
	exit 94
}
