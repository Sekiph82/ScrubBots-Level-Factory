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
	$replaceTarget = Join-Path $fixtureRoot 'replace-target.bin'
	$replaceStage = Join-Path $fixtureRoot 'replace-stage.bin'
	$replaceBackup = Join-Path $fixtureRoot 'replace-backup.bin'
	[IO.File]::WriteAllBytes($target, [Text.Encoding]::UTF8.GetBytes('before'))
	[IO.File]::WriteAllBytes($stage, [Text.Encoding]::UTF8.GetBytes('replacement'))
	[IO.File]::WriteAllBytes($replaceTarget, [Text.Encoding]::UTF8.GetBytes('old-transaction-bytes'))
	[IO.File]::WriteAllBytes($replaceStage, [Text.Encoding]::UTF8.GetBytes('new-transaction-bytes'))
	$powerShellPath = (Get-Process -Id $PID).Path
	$unlocked = Start-Process -FilePath $powerShellPath -ArgumentList @('-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',('"{0}"' -f $probePath),'-TargetPath',('"{0}"' -f $target)) -Wait -PassThru -WindowStyle Hidden
	if ($unlocked.ExitCode -ne 0) { throw "Unlocked control write-open failed unexpectedly: $($unlocked.ExitCode)" }
	$lease = Acquire-ScopedWriterExclusion -LivePaths @($target,$replaceTarget) -StagedPaths @() -ProbeScriptPath $probePath -PowerShellPath $powerShellPath
	if (-not $lease.established -or $lease.probeCount -ne 2) { throw 'Writer exclusion lease did not report the exact live target probes.' }
	$lockedHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
	$sha256 = [Security.Cryptography.SHA256]::Create()
	try { $expectedHash = ([BitConverter]::ToString($sha256.ComputeHash([Text.Encoding]::UTF8.GetBytes('before')))).Replace('-', '').ToLowerInvariant() }
	finally { $sha256.Dispose() }
	if ($lockedHash -cne $expectedHash) { throw 'Read-only hash verification failed while the deny-write lease was held.' }
	[IO.File]::Replace($replaceStage,$replaceTarget,$replaceBackup)
	if ([Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($replaceTarget)) -cne 'new-transaction-bytes') { throw 'Atomic replacement did not retain the staged bytes while the writer lease was held.' }
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
