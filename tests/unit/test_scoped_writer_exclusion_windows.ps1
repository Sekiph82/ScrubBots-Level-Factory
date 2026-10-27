$ErrorActionPreference = 'Stop'
$modulePath = Join-Path $PSScriptRoot '..\..\scripts\scoped_overlay_transaction.psm1'
$probePath = Join-Path $PSScriptRoot '..\..\scripts\probe_scoped_writer_lock.ps1'
Import-Module $modulePath -Force

$fixtureRoot = Join-Path $PSScriptRoot '.r10-v05-writer-exclusion-test'
if (Test-Path -LiteralPath $fixtureRoot) { throw "Refusing to reuse pre-existing writer exclusion fixture: $fixtureRoot" }
$resolvedUnitRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path.TrimEnd('\')
$resolvedFixture = [IO.Path]::GetFullPath($fixtureRoot)
if (-not $resolvedFixture.StartsWith($resolvedUnitRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Writer exclusion fixture escaped its test-owned unit directory.' }

$createdFixture = $false
$lease = $null
try {
	[void][IO.Directory]::CreateDirectory($fixtureRoot)
	$createdFixture = $true
	$target = Join-Path $fixtureRoot 'live-target.bin'
	$stage = Join-Path $fixtureRoot 'staged-target.bin'
	[IO.File]::WriteAllBytes($target, [Text.Encoding]::UTF8.GetBytes('before'))
	[IO.File]::WriteAllBytes($stage, [Text.Encoding]::UTF8.GetBytes('replacement'))
	$powerShellPath = (Get-Process -Id $PID).Path
	$unlocked = Start-Process -FilePath $powerShellPath -ArgumentList @('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',('"{0}"' -f $probePath),'-TargetPath',('"{0}"' -f $target)) -Wait -PassThru -WindowStyle Hidden
	if ($unlocked.ExitCode -ne 0) { throw "Unlocked control write-open failed unexpectedly: $($unlocked.ExitCode)" }
	$lease = Acquire-ScopedWriterExclusion -LivePaths @($target) -StagedPaths @($stage) -ProbeScriptPath $probePath -PowerShellPath $powerShellPath
	if (-not $lease.established -or $lease.probeCount -ne 1) { throw 'Writer exclusion lease did not report the exact live target probe.' }
	'WINDOWS_SCOPED_WRITER_EXCLUSION_TEST_PASS'
}
finally {
	if ($lease) { Release-ScopedWriterExclusion -Lease $lease }
	if ($createdFixture -and (Test-Path -LiteralPath $fixtureRoot -PathType Container)) {
		if ((Test-Path -LiteralPath (Join-Path $fixtureRoot 'live-target.bin')) -and [Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes((Join-Path $fixtureRoot 'live-target.bin'))) -cne 'before') { throw 'Blocked child probe changed live fixture bytes.' }
		$fixtureItem = Get-Item -LiteralPath $fixtureRoot -Force
		if (($fixtureItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Refusing to remove a reparse-point test fixture.' }
		Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
	}
}
