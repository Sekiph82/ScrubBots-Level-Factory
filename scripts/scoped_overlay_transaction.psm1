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
		[Parameter(Mandatory)][object]$ProcessState
	)

	if ($ManifestDrift.Count -gt 0) { throw 'Installed managed bytes differ from manifest without an approved exact repair; no files were written.' }
	if ($Apply -and -not $ProcessState.complete) { throw "PROCESS_INVENTORY_INCOMPLETE: refusing apply because process identity/parent metadata is missing: $($ProcessState.problems -join ', ')" }
	if ($Apply -and @($ProcessState.active).Count -gt 0) {
		$ids = @($ProcessState.active | ForEach-Object { "$($_.ProcessId):$($_.Name)" }) -join ', '
		throw "Installed runtime is in use; no files were written. Active processes: $ids"
	}
	return [pscustomobject]@{ allowed = $true; apply = $Apply }
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
		[Parameter(Mandatory)][hashtable]$Operations
	)

	if ($Plan.Count -eq 0 -and $OverlayAdditions.Count -eq 0) {
		return [pscustomobject]@{ status = 'NO_OP'; changedPaths = @() }
	}
	foreach ($operationName in @('CreateDirectory','ReadBytes','WriteBytes','WriteText','ReadText','Hash','Exists','Replace','RemoveTree')) {
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

	try {
		[void](& $Operations.CreateDirectory $TransactionRoot)
		$receiptFiles = @()
		foreach ($item in $Plan) {
			$relativeStage = ([string]$item.path).Replace('/', [IO.Path]::DirectorySeparatorChar)
			$stage = Join-Path (Join-Path $TransactionRoot 'stage') $relativeStage
			$backup = Join-Path (Join-Path $TransactionRoot 'backup') $relativeStage
			[void](& $Operations.CreateDirectory (Split-Path -Parent $stage))
			[void](& $Operations.CreateDirectory (Split-Path -Parent $backup))
			$originalBytes = [byte[]](& $Operations.ReadBytes $item.target)
			$originalHash = [string](& $Operations.Hash $item.target)
			if ($item.priorSha256 -and $originalHash -cne [string]$item.priorSha256) { throw "Pre-transaction target changed: $($item.path)" }
			$sourceBytes = [byte[]](& $Operations.ReadBytes $item.source)
			[void](& $Operations.WriteBytes $stage $sourceBytes)
			if (([string](& $Operations.Hash $stage)) -cne [string]$item.sha256) { throw "Staged source hash mismatch: $($item.path)" }
			$originals[[string]$item.path] = [pscustomobject]@{ bytes = $originalBytes; sha256 = $originalHash; target = [string]$item.target; restoreStage = (Join-Path (Join-Path $TransactionRoot 'restore') $relativeStage) }
			$stagedFiles += [pscustomobject]@{ stage = $stage; target = [string]$item.target; backup = $backup; relative = [string]$item.path; expected = [string]$item.sha256 }
			$managedEntry = @($Manifest.managedFiles | Where-Object path -ceq $item.path)
			if ($managedEntry.Count -ne 1) { throw "Manifest must contain exactly one managed entry: $($item.path)" }
			$managedEntry[0].sha256 = [string]$item.sha256
			$receiptFiles += [pscustomobject]@{ path = [string]$item.path; priorSha256 = $originalHash; sha256 = [string]$item.sha256; bytes = [long]$item.bytes }
		}

		$receipt = [pscustomobject]@{
			taskId = 'SB-LFX-018-R05-M03'
			sourceCommit = $SourceHead
			sourceHead = $SourceHead
			files = $receiptFiles
			installedAtUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
		}
		$Manifest.overlayPaths = @($Manifest.overlayPaths) + @($OverlayAdditions)
		$Manifest.overlayReceipts = @($Manifest.overlayReceipts) + @($receipt)
		[void](& $Operations.WriteBytes (Join-Path $TransactionRoot 'restore-manifest.bin') $originalManifestBytes)
		[void](& $Operations.WriteText $manifestStage (($Manifest | ConvertTo-Json -Depth 100) + "`n"))

		foreach ($item in $stagedFiles) {
			$attempted += $item
			[void](& $Operations.Replace $item.stage $item.target $item.backup)
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
			[void](& $Operations.RemoveTree $TransactionRoot)
			return [pscustomobject]@{ status = 'COMMITTED'; changedPaths = @($stagedFiles.relative); transactionRoot = $TransactionRoot }
		} catch {
			return [pscustomobject]@{ status = 'COMMITTED_CLEANUP_PENDING'; changedPaths = @($stagedFiles.relative); transactionRoot = $TransactionRoot; cleanupError = $_.Exception.Message }
		}
	} catch {
		$transactionFailure = $_.Exception.Message
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
			$currentHash = [string](& $Operations.Hash $item.target)
			if ($currentHash -cne [string]$original.sha256) {
				if (& $Operations.Exists $item.backup) {
					[void](& $Operations.Replace $item.backup $item.target $null)
				} else {
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
			$actual = [string](& $Operations.Hash $item.target)
			$recoveryHashes += [pscustomobject]@{ path = $item.target; expected = [string]$original.sha256; actual = $actual }
			if ($actual -cne [string]$original.sha256) { $rollbackProblems.Add("TARGET_HASH_MISMATCH:$($item.relative):$actual") }
		} catch { $rollbackProblems.Add("TARGET_HASH_UNAVAILABLE:$($item.relative):$($_.Exception.Message)") }
	}

	if ($rollbackProblems.Count -eq 0) {
		try { [void](& $Operations.RemoveTree $TransactionRoot) } catch { $rollbackProblems.Add("TRANSACTION_EVIDENCE_CLEANUP_FAILED:$($_.Exception.Message)") }
	}
	if ($rollbackProblems.Count -gt 0) {
		throw "TRANSACTION_FAILED_ROLLBACK_INCOMPLETE: $transactionFailure; problems=$($rollbackProblems -join '; '); recoveryHashes=$($recoveryHashes | ConvertTo-Json -Compress -Depth 4); evidence=$TransactionRoot"
	}
	throw "TRANSACTION_FAILED_ROLLBACK_VERIFIED: $transactionFailure; original manifest and $($attempted.Count) attempted payload target(s) re-hashed to their pre-transaction values."
}

Export-ModuleMember -Function Get-ScopedInstallHashDisposition, Assert-ScopedInstallApplyGates, Get-ScopedProcessInventoryState, Invoke-ScopedOverlayTransaction
