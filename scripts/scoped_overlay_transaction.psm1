Set-StrictMode -Version Latest

function Get-ScopedInstallHashDisposition {
	[CmdletBinding()]
	param(
		[Parameter(Mandatory)][string]$RelativePath,
		[Parameter(Mandatory)][string]$ExpectedHash,
		[Parameter(Mandatory)][string]$InstalledHash,
		[Parameter(Mandatory)][hashtable]$AuthorizedRepairHashes
	)

	if ($InstalledHash -ceq $ExpectedHash) { return 'MATCH' }
	$authorized = [string]$AuthorizedRepairHashes[$RelativePath]
	if ($authorized -and $InstalledHash -ceq $authorized) { return 'AUTHORIZED_REPAIR' }
	return 'UNKNOWN_DRIFT'
}

function Assert-ScopedInstallApplyGates {
	[CmdletBinding()]
	param(
		[Parameter(Mandatory)][AllowEmptyCollection()][object[]]$ManifestDrift,
		[Parameter(Mandatory)][bool]$Apply,
	[AllowNull()][object]$ProcessState,
		[bool]$WriterExclusionEstablished = $false,
		[bool]$RequireWriterExclusion = $false
	)

	if ($ManifestDrift.Count -gt 0) { throw 'Installed managed bytes differ from manifest without an approved exact repair; no files were written.' }
	if ($Apply -and $null -eq $ProcessState) { throw 'PROCESS_INVENTORY_INCOMPLETE: apply requires the transaction final process snapshot.' }
	if ($Apply -and -not $ProcessState.complete) { throw "PROCESS_INVENTORY_INCOMPLETE: refusing apply because process identity/parent metadata is missing: $($ProcessState.problems -join ', ')" }
	if ($Apply -and @($ProcessState.active).Count -gt 0) {
		$ids = @($ProcessState.active | ForEach-Object { "$($_.ProcessId):$($_.Name)" }) -join ', '
		throw "Installed runtime is in use; no files were written. Active processes: $ids"
	}
	if ($Apply -and $RequireWriterExclusion -and -not $WriterExclusionEstablished) { throw 'PROCESS_QUIESCENCE_UNPROVEN: a process snapshot cannot prevent a new writer from starting before replacement.' }
	return [pscustomobject]@{ allowed = $true; apply = $Apply }
}

function Acquire-ScopedWriterExclusion {
	[CmdletBinding()]
	param(
		[Parameter(Mandatory)][AllowEmptyCollection()][string[]]$LivePaths,
		[Parameter(Mandatory)][AllowEmptyCollection()][string[]]$StagedPaths,
		[Parameter(Mandatory)][string]$ProbeScriptPath,
		[Parameter(Mandatory)][string]$PowerShellPath
	)

	$handles = [System.Collections.Generic.List[IDisposable]]::new()
	$lockedLive = [System.Collections.Generic.List[string]]::new()
	$absentLive = [System.Collections.Generic.List[string]]::new()
	try {
		foreach ($path in @($LivePaths | Select-Object -Unique)) {
			if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
				$absentLive.Add([string]$path)
				continue
			}
			$share = [IO.FileShare]::Read -bor [IO.FileShare]::Delete
			$handle = [IO.File]::Open($path, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, $share)
			$handles.Add($handle)
			$lockedLive.Add([string]$path)
		}
		foreach ($path in @($StagedPaths | Select-Object -Unique)) {
			if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Writer exclusion staging target is missing: $path" }
			$share = [IO.FileShare]::Read -bor [IO.FileShare]::Delete
			$handle = [IO.File]::Open($path, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, $share)
			$handles.Add($handle)
		}
		foreach ($path in $lockedLive) {
			$quotedProbe = '"{0}"' -f $ProbeScriptPath.Replace('"', '\"')
			$quotedTarget = '"{0}"' -f $path.Replace('"', '\"')
			$arguments = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File {0} -TargetPath {1} -ExpectBlocked' -f $quotedProbe, $quotedTarget
			$probe = Start-Process -FilePath $PowerShellPath -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
			if ($probe.ExitCode -ne 0) { throw "Concurrent writer-open probe was not blocked for: $path (exit=$($probe.ExitCode))" }
		}
		return @{
			established = $true
			method = Get-ScopedWriterExclusionMethod
			handles = $handles
			lockedPaths = @($lockedLive)
			absentPaths = @($absentLive)
			probeCount = $lockedLive.Count
		}
	} catch {
		for ($index = $handles.Count - 1; $index -ge 0; $index--) {
			try { $handles[$index].Dispose() } catch { }
		}
		throw "PROCESS_QUIESCENCE_UNPROVEN: exclusive target lock or independent writer probe failed: $($_.Exception.Message)"
	}
}

function Get-ScopedWriterExclusionMethod {
	return 'Windows FileStream deny-write handles on every existing replacement target, staged replacement, and install manifest; independent PowerShell write-open probe denied on each existing live target; absent additions use no-overwrite move.'
}

function Release-ScopedWriterExclusion {
	[CmdletBinding()]
	param([AllowNull()][hashtable]$Lease)
	if (-not $Lease) { return }
	$handles = @($Lease.handles)
	for ($index = $handles.Count - 1; $index -ge 0; $index--) {
		try { $handles[$index].Dispose() } catch { }
	}
	$Lease.established = $false
}

function ConvertTo-ScopedOverlayOutcome {
	[CmdletBinding()]
	param([Parameter(Mandatory)][object]$Result)

	$status = [string]$Result.status
	switch ($status) {
		'COMMITTED' {
			$paths = @($Result.changedPaths | ForEach-Object { [string]$_ })
			$hashes = @($Result.verifiedHashes)
			if ($paths.Count -eq 0 -or $hashes.Count -ne $paths.Count) { throw 'Invalid COMMITTED result: exact changed paths and verified hashes are required.' }
			return [pscustomobject]@{ status = $status; changedPaths = $paths; verifiedHashes = $hashes }
		}
		'COMMITTED_CLEANUP_PENDING' {
			$root = [string]$Result.transactionRoot
			$errorReason = [string]$Result.cleanupError
			$paths = @($Result.changedPaths | ForEach-Object { [string]$_ })
			$hashes = @($Result.verifiedHashes)
			if ([string]::IsNullOrWhiteSpace($root) -or [string]::IsNullOrWhiteSpace($errorReason)) { throw 'Invalid COMMITTED_CLEANUP_PENDING result: transaction evidence path and cleanup error are required.' }
			if ($paths.Count -eq 0 -or $hashes.Count -ne $paths.Count) { throw 'Invalid COMMITTED_CLEANUP_PENDING result: exact changed paths and verified hashes are required.' }
			return [pscustomobject]@{
				status = $status
				changedPaths = $paths
				verifiedHashes = $hashes
				transactionRoot = $root
				errorReason = $errorReason
				evidencePath = $root
				nextAction = 'Preserve the transaction directory; inspect its evidence and request operator review before any cleanup.'
			}
		}
		'NO_OP' { return [pscustomobject]@{ status = $status; changedPaths = @(); verifiedHashes = @() } }
		default { throw "Unknown transaction outcome '$status'; failing closed." }
	}
}

function Write-ScopedOverlayOutcome {
	[CmdletBinding()]
	param([Parameter(Mandatory)][object]$Result)

	$outcome = ConvertTo-ScopedOverlayOutcome -Result $Result
	$outcome | ConvertTo-Json -Depth 8 -Compress
	switch ([string]$outcome.status) {
		'COMMITTED' { 'OWNER_DESKTOP_STUDIO_SCOPED_OVERLAY_UPDATED' }
		'COMMITTED_CLEANUP_PENDING' { "COMMITTED_CLEANUP_PENDING: installed files are verified; preserve evidence at $($outcome.evidencePath). Reason: $($outcome.errorReason) Next action: $($outcome.nextAction)" }
		'NO_OP' { 'NO_OP: no installed files changed.' }
	}
}

function Get-ScopedProcessInventoryState {
	[CmdletBinding()]
	param(
		[Parameter(Mandatory)][AllowEmptyCollection()][object[]]$Processes,
		[Parameter(Mandatory)][string]$RuntimeRoot,
		[Parameter(Mandatory)][int]$CurrentPid
	)

	$problems = [System.Collections.Generic.List[string]]::new()
	$byPid = @{}
	$runtimeNeedle = $RuntimeRoot.TrimEnd('\')
	$writerNamePattern = '^(Godot.*|python(?:w)?\.exe|pwsh\.exe|powershell\.exe|cmd\.exe)$'
	if ($Processes.Count -eq 0) { $problems.Add('PROCESS_INVENTORY_EMPTY') }

	foreach ($process in $Processes) {
		$pidProperty = $process.PSObject.Properties['ProcessId']
		$parentProperty = $process.PSObject.Properties['ParentProcessId']
		$nameProperty = $process.PSObject.Properties['Name']
		if (-not $pidProperty -or $null -eq $pidProperty.Value -or -not $parentProperty -or $null -eq $parentProperty.Value -or -not $nameProperty -or [string]::IsNullOrWhiteSpace([string]$nameProperty.Value)) {
			$problems.Add('PROCESS_ID_PARENT_OR_NAME_MISSING')
			continue
		}
		try {
			$id = [int]$pidProperty.Value
			$parentId = [int]$parentProperty.Value
		} catch {
			$problems.Add('PROCESS_ID_OR_PARENT_INVALID')
			continue
		}
		if ($byPid.ContainsKey($id)) { $problems.Add("DUPLICATE_PROCESS_ID:$id"); continue }
		$byPid[$id] = $process
		if ($id -eq $CurrentPid) { continue }

		$name = [string]$nameProperty.Value
		$commandProperty = $process.PSObject.Properties['CommandLine']
		$executableProperty = $process.PSObject.Properties['ExecutablePath']
		if ($name -match $writerNamePattern) {
			if (-not $commandProperty -or [string]::IsNullOrWhiteSpace([string]$commandProperty.Value)) { $problems.Add("COMMAND_LINE_UNAVAILABLE:$id") }
			if (-not $executableProperty -or [string]::IsNullOrWhiteSpace([string]$executableProperty.Value)) { $problems.Add("EXECUTABLE_PATH_UNAVAILABLE:$id") }
		}
	}

	$activeIds = [System.Collections.Generic.HashSet[int]]::new()
	if ($problems.Count -eq 0) {
		foreach ($process in $Processes) {
			if ([int]$process.ProcessId -eq $CurrentPid) { continue }
			$name = [string]$process.Name
			$commandProperty = $process.PSObject.Properties['CommandLine']
			$executableProperty = $process.PSObject.Properties['ExecutablePath']
			$commandLine = if ($commandProperty) { [string]$commandProperty.Value } else { '' }
			$executablePath = if ($executableProperty) { [string]$executableProperty.Value } else { '' }
			$usesRuntime = (($commandLine.IndexOf($runtimeNeedle, [StringComparison]::OrdinalIgnoreCase) -ge 0) -or ($executablePath.IndexOf($runtimeNeedle, [StringComparison]::OrdinalIgnoreCase) -ge 0))
			$isStudioOrWriter = ($name -like 'Godot*') -or ($commandLine -match 'factory_core_launcher\.py|png_batch\.py')
			if ($usesRuntime -and $isStudioOrWriter) { [void]$activeIds.Add([int]$process.ProcessId) }
		}
	}

	if ($problems.Count -eq 0) {
		$added = $true
		while ($added) {
			$added = $false
			foreach ($process in $Processes) {
				if ($null -eq $process.ProcessId -or [int]$process.ProcessId -eq $CurrentPid) { continue }
				if ($activeIds.Contains([int]$process.ParentProcessId) -and $activeIds.Add([int]$process.ProcessId)) { $added = $true }
			}
		}
	}

	$active = @($Processes | Where-Object { $null -ne $_.ProcessId -and $activeIds.Contains([int]$_.ProcessId) })
	return [pscustomobject]@{
		complete = ($problems.Count -eq 0)
		status = if ($problems.Count -eq 0) { 'COMPLETE' } else { 'PROCESS_INVENTORY_INCOMPLETE' }
		problems = @($problems)
		active = $active
	}
}

function Invoke-ScopedOverlayTransaction {
	[CmdletBinding()]
	param(
		[Parameter(Mandatory)][AllowEmptyCollection()][object[]]$Plan,
		[Parameter(Mandatory)][object]$Manifest,
		[Parameter(Mandatory)][string]$ManifestPath,
		[Parameter(Mandatory)][string]$TransactionRoot,
		[Parameter(Mandatory)][string]$SourceHead,
		[Parameter(Mandatory)][AllowEmptyCollection()][string[]]$OverlayAdditions,
		[Parameter(Mandatory)][hashtable]$Operations,
		[AllowEmptyCollection()][string[]]$NewManagedPaths = @()
	)

	if ($Plan.Count -eq 0 -and $OverlayAdditions.Count -eq 0) {
		return [pscustomobject]@{ status = 'NO_OP'; changedPaths = @() }
	}
	foreach ($operationName in @('CreateDirectory','ReadBytes','WriteBytes','WriteText','ReadText','Hash','Exists','Replace','MoveNew','DeleteFile','RemoveTree','GetProcessSnapshot','AcquireWriterExclusion','ReleaseWriterExclusion')) {
		if (-not $Operations.ContainsKey($operationName) -or $Operations[$operationName] -isnot [scriptblock]) { throw "Missing transaction operation: $operationName" }
	}

	$originalManifestBytes = [byte[]](& $Operations.ReadBytes $ManifestPath)
	$originalManifestHash = [string](& $Operations.Hash $ManifestPath)
	$originals = @{}
	$stagedFiles = @()
	$attempted = @()
	$manifestStage = Join-Path $TransactionRoot '.factory-studio-install-manifest.json'
	$manifestBackup = Join-Path $TransactionRoot 'backup-manifest.json'
	$manifestReplaceAttempted = $false
	$transactionFailure = $null
	$writerLease = $null

	try {
		[void](& $Operations.CreateDirectory $TransactionRoot)
		$receiptFiles = @()
		foreach ($item in $Plan) {
			$relativeStage = ([string]$item.path).Replace('/', [IO.Path]::DirectorySeparatorChar)
			$stage = Join-Path (Join-Path $TransactionRoot 'stage') $relativeStage
			$backup = Join-Path (Join-Path $TransactionRoot 'backup') $relativeStage
			[void](& $Operations.CreateDirectory (Split-Path -Parent $stage))
			[void](& $Operations.CreateDirectory (Split-Path -Parent $backup))
			$targetExists = [bool](& $Operations.Exists $item.target)
			if ([bool]$item.priorExists -ne $targetExists) { throw "Pre-transaction target existence changed: $($item.path)" }
			$originalBytes = if ($targetExists) { [byte[]](& $Operations.ReadBytes $item.target) } else { [byte[]]@() }
			$originalHash = if ($targetExists) { [string](& $Operations.Hash $item.target) } else { $null }
			if ($targetExists -and $item.priorSha256 -and $originalHash -cne [string]$item.priorSha256) { throw "Pre-transaction target changed: $($item.path)" }
			$sourceBytes = [byte[]](& $Operations.ReadBytes $item.source)
			[void](& $Operations.WriteBytes $stage $sourceBytes)
			if (([string](& $Operations.Hash $stage)) -cne [string]$item.sha256) { throw "Staged source hash mismatch: $($item.path)" }
			$originals[[string]$item.path] = [pscustomobject]@{ existed = $targetExists; bytes = $originalBytes; sha256 = $originalHash; target = [string]$item.target; restoreStage = (Join-Path (Join-Path $TransactionRoot 'restore') $relativeStage) }
			$stagedFiles += [pscustomobject]@{ stage = $stage; target = [string]$item.target; backup = $backup; relative = [string]$item.path; expected = [string]$item.sha256; priorExists = $targetExists }
			$managedEntry = @($Manifest.managedFiles | Where-Object path -ceq $item.path)
			if ($managedEntry.Count -eq 1) {
				$managedEntry[0].sha256 = [string]$item.sha256
			} elseif ($managedEntry.Count -eq 0 -and -not $targetExists -and $item.path -cin $NewManagedPaths) {
				$Manifest.managedFiles = @($Manifest.managedFiles) + @([pscustomobject]@{ path = [string]$item.path; sha256 = [string]$item.sha256 })
			} else { throw "Manifest must contain exactly one managed entry or an authorized absent addition: $($item.path)" }
			$receiptFiles += [pscustomobject]@{ path = [string]$item.path; priorExists = $targetExists; priorSha256 = $originalHash; sha256 = [string]$item.sha256; bytes = [long]$item.bytes }
		}

		$receipt = [pscustomobject]@{
			taskId = 'SB-LFX-018-R05-M03'
			sourceCommit = $SourceHead
			sourceHead = $SourceHead
			files = $receiptFiles
			writerExclusionMethod = Get-ScopedWriterExclusionMethod
			installedAtUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
		}
		$Manifest.overlayPaths = @(@($Manifest.overlayPaths) + @($OverlayAdditions) | Select-Object -Unique)
		$Manifest.overlayReceipts = @($Manifest.overlayReceipts) + @($receipt)
		[void](& $Operations.WriteBytes (Join-Path $TransactionRoot 'restore-manifest.bin') $originalManifestBytes)
		[void](& $Operations.WriteText $manifestStage (($Manifest | ConvertTo-Json -Depth 100) + "`n"))
		$livePaths = @($Plan | Where-Object { $_.priorExists } | ForEach-Object { [string]$_.target }) + @($ManifestPath)
		$stagePaths = @($stagedFiles | ForEach-Object { [string]$_.stage }) + @($manifestStage)
		$writerLease = & $Operations.AcquireWriterExclusion $livePaths $stagePaths
		if (-not $writerLease -or $writerLease.established -ne $true -or [string]::IsNullOrWhiteSpace([string]$writerLease.method)) {
			throw 'PROCESS_QUIESCENCE_UNPROVEN: writer exclusion did not provide a verified lease.'
		}
		if ([string](& $Operations.Hash $ManifestPath) -cne $originalManifestHash) { throw 'Pre-transaction manifest changed before exclusive lock acquisition.' }
		foreach ($item in $Plan) {
			$existsNow = [bool](& $Operations.Exists $item.target)
			if ([bool]$item.priorExists -ne $existsNow) { throw "Pre-transaction target existence changed after exclusive lock: $($item.path)" }
			if ($existsNow -and [string](& $Operations.Hash $item.target) -cne [string]$originals[[string]$item.path].sha256) {
				throw "Pre-transaction target changed after exclusive lock: $($item.path)"
			}
		}

		# This is the last bounded process snapshot before any live replacement.
		# Target handles block new write opens; this snapshot detects any legacy
		# process that was already active before the handles were acquired.
		$freshProcessState = & $Operations.GetProcessSnapshot
		[void](Assert-ScopedInstallApplyGates -ManifestDrift @() -Apply:$true -ProcessState $freshProcessState -WriterExclusionEstablished:$writerLease.established -RequireWriterExclusion:$true)
		foreach ($item in $stagedFiles) {
			$original = $originals[[string]$item.relative]
			$immediateExists = [bool](& $Operations.Exists $item.target)
			if ($original.existed) {
				$immediatePriorHash = [string](& $Operations.Hash $item.target)
				if (-not $immediateExists -or $immediatePriorHash -cne [string]$original.sha256) { throw "Pre-replacement target changed: $($item.relative)" }
			} elseif ($immediateExists) { throw "Pre-replacement addition target unexpectedly exists: $($item.relative)" }
			$attempted += $item
			if ($original.existed) { [void](& $Operations.Replace $item.stage $item.target $item.backup) }
			else { [void](& $Operations.MoveNew $item.stage $item.target) }
			if (([string](& $Operations.Hash $item.target)) -cne $item.expected) { throw "Installed file hash mismatch after replacement: $($item.relative)" }
		}
		$manifestReplaceAttempted = $true
		[void](& $Operations.Replace $manifestStage $ManifestPath $manifestBackup)
		$installedManifest = (& $Operations.ReadText $ManifestPath) | ConvertFrom-Json
		if (@($installedManifest.overlayReceipts).Count -eq 0 -or $installedManifest.overlayReceipts[-1].sourceHead -cne $SourceHead) { throw 'Installed overlay receipt did not verify.' }
		foreach ($item in $stagedFiles) {
			if (([string](& $Operations.Hash $item.target)) -cne $item.expected) { throw "Final installed hash mismatch: $($item.relative)" }
		}
		try {
			[void](& $Operations.ReleaseWriterExclusion $writerLease)
			$writerLease = $null
			[void](& $Operations.RemoveTree $TransactionRoot)
			$successResult = [pscustomobject]@{ status = 'COMMITTED'; changedPaths = @($stagedFiles.relative); verifiedHashes = @($stagedFiles | ForEach-Object { [pscustomobject]@{ path = $_.relative; sha256 = $_.expected } }); transactionRoot = $TransactionRoot }
		} catch {
			$successResult = [pscustomobject]@{ status = 'COMMITTED_CLEANUP_PENDING'; changedPaths = @($stagedFiles.relative); verifiedHashes = @($stagedFiles | ForEach-Object { [pscustomobject]@{ path = $_.relative; sha256 = $_.expected } }); transactionRoot = $TransactionRoot; cleanupError = $_.Exception.Message }
		}
		[void](& $Operations.ReleaseWriterExclusion $writerLease)
		$writerLease = $null
		return $successResult
	} catch {
		$transactionFailure = $_.Exception.Message
	}
	if ($attempted.Count -eq 0 -and -not $manifestReplaceAttempted -and $transactionFailure -match '^(PROCESS_INVENTORY_INCOMPLETE|PROCESS_QUIESCENCE_UNPROVEN|Installed runtime is in use|Pre-replacement target changed)') {
		[void](& $Operations.ReleaseWriterExclusion $writerLease)
		$writerLease = $null
		try { [void](& $Operations.RemoveTree $TransactionRoot) } catch { throw "TRANSACTION_FAILED_ROLLBACK_INCOMPLETE: $transactionFailure; no target replacement occurred; staged evidence cleanup failed: $($_.Exception.Message); evidence=$TransactionRoot" }
		throw $transactionFailure
	}

	$rollbackProblems = [System.Collections.Generic.List[string]]::new()
	$reverseAttempted = @($attempted)
	[array]::Reverse($reverseAttempted)
	if ($manifestReplaceAttempted) {
		try {
			$currentManifestHash = [string](& $Operations.Hash $ManifestPath)
			if ($currentManifestHash -cne $originalManifestHash) {
				if (& $Operations.Exists $manifestBackup) {
					[void](& $Operations.Replace $manifestBackup $ManifestPath $null)
				} else {
					$restoreManifest = Join-Path $TransactionRoot 'restore-manifest.bin'
					[void](& $Operations.WriteBytes $restoreManifest $originalManifestBytes)
					[void](& $Operations.Replace $restoreManifest $ManifestPath $null)
				}
			}
		} catch { $rollbackProblems.Add("MANIFEST_RESTORE_ERROR:$($_.Exception.Message)") }
	}

	foreach ($item in $reverseAttempted) {
		try {
			$original = $originals[[string]$item.relative]
			$targetExists = [bool](& $Operations.Exists $item.target)
			if (-not $original.existed) {
				if ($targetExists) {
					$currentHash = [string](& $Operations.Hash $item.target)
					if ($currentHash -cne [string]$item.expected) { throw 'New target changed after transaction write; refusing to delete unrelated bytes.' }
					[void](& $Operations.DeleteFile $item.target)
				}
			} elseif (-not $targetExists -or [string](& $Operations.Hash $item.target) -cne [string]$original.sha256) {
				if (& $Operations.Exists $item.backup) { [void](& $Operations.Replace $item.backup $item.target $null) }
				else {
					[void](& $Operations.WriteBytes $original.restoreStage ([byte[]]$original.bytes))
					[void](& $Operations.Replace $original.restoreStage $item.target $null)
				}
			}
		} catch { $rollbackProblems.Add("TARGET_RESTORE_ERROR:$($item.relative):$($_.Exception.Message)") }
	}

	$recoveryHashes = @()
	if ($manifestReplaceAttempted -or $transactionFailure) {
		try {
			$actualManifestHash = [string](& $Operations.Hash $ManifestPath)
			$recoveryHashes += [pscustomobject]@{ path = $ManifestPath; expected = $originalManifestHash; actual = $actualManifestHash }
			if ($actualManifestHash -cne $originalManifestHash) { $rollbackProblems.Add("MANIFEST_HASH_MISMATCH:$actualManifestHash") }
		} catch { $rollbackProblems.Add("MANIFEST_HASH_UNAVAILABLE:$($_.Exception.Message)") }
	}
	foreach ($item in $reverseAttempted) {
		try {
			$original = $originals[[string]$item.relative]
			$actualExists = [bool](& $Operations.Exists $item.target)
			$actual = if ($actualExists) { [string](& $Operations.Hash $item.target) } else { 'MISSING' }
			$expected = if ($original.existed) { [string]$original.sha256 } else { 'MISSING' }
			$recoveryHashes += [pscustomobject]@{ path = $item.target; expected = $expected; actual = $actual }
			if ($actual -cne $expected) { $rollbackProblems.Add("TARGET_HASH_MISMATCH:$($item.relative):$actual") }
		} catch { $rollbackProblems.Add("TARGET_HASH_UNAVAILABLE:$($item.relative):$($_.Exception.Message)") }
	}

	if ($rollbackProblems.Count -eq 0) {
		[void](& $Operations.ReleaseWriterExclusion $writerLease)
		$writerLease = $null
		try { [void](& $Operations.RemoveTree $TransactionRoot) } catch { $rollbackProblems.Add("TRANSACTION_EVIDENCE_CLEANUP_FAILED:$($_.Exception.Message)") }
	}
	if ($rollbackProblems.Count -gt 0) {
		[void](& $Operations.ReleaseWriterExclusion $writerLease)
		$writerLease = $null
		throw "TRANSACTION_FAILED_ROLLBACK_INCOMPLETE: $transactionFailure; problems=$($rollbackProblems -join '; '); recoveryHashes=$($recoveryHashes | ConvertTo-Json -Compress -Depth 4); evidence=$TransactionRoot"
	}
	throw "TRANSACTION_FAILED_ROLLBACK_VERIFIED: $transactionFailure; original manifest and $($attempted.Count) attempted payload target(s) re-hashed to their pre-transaction values."
}

Export-ModuleMember -Function Get-ScopedInstallHashDisposition, Assert-ScopedInstallApplyGates, Get-ScopedWriterExclusionMethod, Acquire-ScopedWriterExclusion, Release-ScopedWriterExclusion, Get-ScopedProcessInventoryState, ConvertTo-ScopedOverlayOutcome, Write-ScopedOverlayOutcome, Invoke-ScopedOverlayTransaction
