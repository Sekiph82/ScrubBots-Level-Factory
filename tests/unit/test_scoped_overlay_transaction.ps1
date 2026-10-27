$ErrorActionPreference = 'Stop'
Import-Module (Join-Path $PSScriptRoot '..\..\scripts\scoped_overlay_transaction.psm1') -Force

$script:fakeFiles = @{}
$script:replaceCalls = 0
$script:stageWriteCalls = 0
$script:hashCalls = @{}
$script:failStageWriteAt = 0
$script:failReplaceBeforeAt = 0
$script:failReplaceAfterAt = 0
$script:failRollbackTarget = ''
$script:failFinalVerification = $false
$script:failRemoveTree = $false
$script:freshProcessState = $null
$script:writerLeaseEstablished = $true

function Assert-True([bool]$Condition, [string]$Message) {
	if (-not $Condition) { throw "ASSERTION_FAILED: $Message" }
}

# Inspect the real production caller: both status paths must preserve the helper's output.
$installerPath=Join-Path $PSScriptRoot '..\..\scripts\install_factory_studio_scoped_overlay.ps1'
$installerSource=Get-Content -LiteralPath $installerPath -Raw
$visibleCallCount=[regex]::Matches($installerSource,'(?m)^\s*Write-ScopedOverlayOutcome\s+-Result').Count
$suppressedCallCount=[regex]::Matches($installerSource,'(?im)^\s*\[void\]\s*\(\s*Write-ScopedOverlayOutcome').Count
Assert-True ($visibleCallCount -eq 2 -and $suppressedCallCount -eq 0) 'both actual installer outcome call sites preserve pipeline output'
Assert-True ($installerSource -match '(?s)GetProcessSnapshot\s*=\s*\{.*?Get-ScopedProcessInventoryState' -and $installerSource -match 'AcquireWriterExclusion\s*=\s*\{' -and $installerSource -notmatch 'WriterExclusionEstablished:\$true|WriterExclusionEstablished:\$false') 'installer proves writer exclusion through transaction operation without caller-supplied assertion'

function ConvertTo-FakeBytes([string]$Text) { return ,([Text.Encoding]::UTF8.GetBytes($Text)) }
function Get-FakeHash([byte[]]$Bytes) {
	$sha = [Security.Cryptography.SHA256]::Create()
	try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant() }
	finally { $sha.Dispose() }
}
function Put-FakeText([string]$Path, [string]$Text) { $script:fakeFiles[$Path] = ConvertTo-FakeBytes $Text }
function Get-FakeText([string]$Path) { return [Text.Encoding]::UTF8.GetString([byte[]]$script:fakeFiles[$Path]) }
function Reset-FakeFileSystem {
	$script:fakeFiles = @{}
	$script:replaceCalls = 0
	$script:stageWriteCalls = 0
	$script:hashCalls = @{}
	$script:failStageWriteAt = 0
	$script:failReplaceBeforeAt = 0
	$script:failReplaceAfterAt = 0
	$script:failRollbackTarget = ''
	$script:failFinalVerification = $false
	$script:failRemoveTree = $false
	$script:freshProcessState = [pscustomobject]@{ complete = $true; status = 'COMPLETE'; problems = @(); active = @() }
	$script:writerLeaseEstablished = $true
	Put-FakeText 'source-one' 'new-one'
	Put-FakeText 'source-two' 'new-two'
	Put-FakeText 'target-one' 'old-one'
	Put-FakeText 'target-two' 'old-two'
	Put-FakeText 'png-batch-protected' 'immutable-job-bytes'
	Put-FakeText 'release-pool-protected' 'immutable-pool-bytes'
	Put-FakeText 'owner-png-protected' 'immutable-png-bytes'
	$initialManifest = [pscustomobject]@{
		managedFiles = @(
			[pscustomobject]@{ path = 'one.py'; sha256 = (Get-FakeHash (ConvertTo-FakeBytes 'old-one')) },
			[pscustomobject]@{ path = 'two.py'; sha256 = (Get-FakeHash (ConvertTo-FakeBytes 'old-two')) }
		)
		overlayPaths = @()
		overlayReceipts = @()
	}
	Put-FakeText 'manifest' (($initialManifest | ConvertTo-Json -Depth 10) + "`n")
}

$script:fakeOperations = @{
	CreateDirectory = { param($path) }
	ReadBytes = { param($path) if (-not $script:fakeFiles.ContainsKey([string]$path)) { throw "fake file missing: $path" }; return ,([byte[]]$script:fakeFiles[[string]$path]) }
	WriteBytes = { param($path,$bytes) if ([string]$path -match '[\\/]stage[\\/]') { $script:stageWriteCalls++; if ($script:failStageWriteAt -eq $script:stageWriteCalls) { throw 'injected staging failure' } }; $script:fakeFiles[[string]$path] = [byte[]]$bytes }
	WriteText = { param($path,$value) $script:fakeFiles[[string]$path] = [Text.Encoding]::UTF8.GetBytes([string]$value) }
	ReadText = { param($path) [Text.Encoding]::UTF8.GetString([byte[]]$script:fakeFiles[[string]$path]) }
	Hash = { param($path) $key=[string]$path; if (-not $script:hashCalls.ContainsKey($key)) { $script:hashCalls[$key]=0 }; $script:hashCalls[$key]++; if ($script:failFinalVerification -and $key -eq 'target-one' -and $script:hashCalls[$key] -eq 3) { $script:failFinalVerification=$false; throw 'injected final verification failure' }; Get-FakeHash ([byte[]]$script:fakeFiles[$key]) }
	Exists = { param($path) $script:fakeFiles.ContainsKey([string]$path) }
	Replace = {
		param($stage,$target,$backup)
		$script:replaceCalls++
		if ($script:failRollbackTarget -and [string]$target -eq $script:failRollbackTarget -and [string]$stage -match '[\\/]backup[\\/]') { throw 'injected rollback restore failure' }
		if ($script:failReplaceBeforeAt -eq $script:replaceCalls) { throw 'injected replacement failure before commit' }
		if (-not $script:fakeFiles.ContainsKey([string]$stage) -or -not $script:fakeFiles.ContainsKey([string]$target)) { throw "fake replace path missing: $target" }
		if ($backup) { $script:fakeFiles[[string]$backup] = [byte[]]$script:fakeFiles[[string]$target] }
		$script:fakeFiles[[string]$target] = [byte[]]$script:fakeFiles[[string]$stage]
		$script:fakeFiles.Remove([string]$stage)
		if ($script:failReplaceAfterAt -eq $script:replaceCalls) { throw 'injected replacement failure after commit' }
	}
	RemoveTree = { param($path) if ($script:failRemoveTree) { throw 'injected cleanup failure' }; $prefix=[string]$path + '\'; foreach($key in @($script:fakeFiles.Keys | Where-Object { $_ -eq [string]$path -or $_.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) })) { $script:fakeFiles.Remove($key) } }
	GetProcessSnapshot = { return $script:freshProcessState }
	MoveNew = { param($stage,$target) if ($script:fakeFiles.ContainsKey([string]$target)) { throw 'fake no-overwrite move target already exists' }; if (-not $script:fakeFiles.ContainsKey([string]$stage)) { throw "fake stage missing: $stage" }; $script:fakeFiles[[string]$target]=[byte[]]$script:fakeFiles[[string]$stage]; $script:fakeFiles.Remove([string]$stage) }
	DeleteFile = { param($path) $script:fakeFiles.Remove([string]$path) }
	AcquireWriterExclusion = { param($live,$staged) return @{established=$script:writerLeaseEstablished;method=if($script:writerLeaseEstablished){Get-ScopedWriterExclusionMethod}else{''};handles=@()} }
	ReleaseWriterExclusion = { param($lease) if ($lease) { $lease.established=$false } }
}

function Invoke-FakeTransaction {
	$plan = @(
		[pscustomobject]@{ path='one.py'; source='source-one'; target='target-one'; sha256=(Get-FakeHash (ConvertTo-FakeBytes 'new-one')); priorSha256=(Get-FakeHash (ConvertTo-FakeBytes 'old-one')); priorExists=$true; bytes=7 },
		[pscustomobject]@{ path='two.py'; source='source-two'; target='target-two'; sha256=(Get-FakeHash (ConvertTo-FakeBytes 'new-two')); priorSha256=(Get-FakeHash (ConvertTo-FakeBytes 'old-two')); priorExists=$true; bytes=7 }
	)
	$manifest = Get-FakeText 'manifest' | ConvertFrom-Json
	Invoke-ScopedOverlayTransaction -Plan $plan -Manifest $manifest -ManifestPath 'manifest' -TransactionRoot 'C:\owner-release\.txn-r03' -SourceHead 'head-r03' -OverlayAdditions @('one.py','two.py') -Operations $script:fakeOperations
}
function Assert-Restored([string]$Context) {
	Assert-True ((Get-FakeText 'target-one') -ceq 'old-one') "$Context restored target-one exact bytes"
	Assert-True ((Get-FakeText 'target-two') -ceq 'old-two') "$Context restored target-two exact bytes"
	Assert-True ((Get-FakeText 'png-batch-protected') -ceq 'immutable-job-bytes') "$Context preserved protected batch bytes"
	Assert-True ((Get-FakeText 'release-pool-protected') -ceq 'immutable-pool-bytes') "$Context preserved protected pool bytes"
	Assert-True ((Get-FakeText 'owner-png-protected') -ceq 'immutable-png-bytes') "$Context preserved protected PNG bytes"
	$manifestAfter=Get-FakeText 'manifest'
	$baseline=( [pscustomobject]@{managedFiles=@([pscustomobject]@{path='one.py';sha256=(Get-FakeHash (ConvertTo-FakeBytes 'old-one'))},[pscustomobject]@{path='two.py';sha256=(Get-FakeHash (ConvertTo-FakeBytes 'old-two'))});overlayPaths=@();overlayReceipts=@()} | ConvertTo-Json -Depth 10) + "`n"
	Assert-True ((Get-FakeHash (ConvertTo-FakeBytes $manifestAfter)) -ceq (Get-FakeHash (ConvertTo-FakeBytes $baseline))) "$Context restored exact manifest bytes"
}
function Assert-TransactionFailure([string]$ExpectedText, [string]$Context) {
	$threw=$false
	try { [void](Invoke-FakeTransaction) } catch { $threw=$true; Assert-True ($_.Exception.Message -like "*$ExpectedText*") "$Context error reports $ExpectedText; got $($_.Exception.Message)" }
	Assert-True $threw "$Context throws"
}

# Exact manifest classification and fail-closed pre-replacement gate.
Assert-True ((Get-ScopedInstallHashDisposition -RelativePath 'x.py' -ExpectedHash 'expected' -InstalledHash 'expected' -AuthorizedRepairHashes @{'x.py'='legacy'}) -ceq 'MATCH') 'manifest match disposition'
Assert-True ((Get-ScopedInstallHashDisposition -RelativePath 'x.py' -ExpectedHash 'expected' -InstalledHash 'legacy' -AuthorizedRepairHashes @{'x.py'='legacy'}) -ceq 'AUTHORIZED_REPAIR') 'exact authorized repair disposition'
Assert-True ((Get-ScopedInstallHashDisposition -RelativePath 'x.py' -ExpectedHash 'expected' -InstalledHash 'other' -AuthorizedRepairHashes @{'x.py'='legacy'}) -ceq 'UNKNOWN_DRIFT') 'unknown drift disposition'
$gateFailed=$false
try { [void](Assert-ScopedInstallApplyGates -ManifestDrift @([pscustomobject]@{path='verify.py'}) -Apply:$true -ProcessState ([pscustomobject]@{complete=$true;problems=@();active=@()})) } catch { $gateFailed=$_.Exception.Message -like '*manifest*without an approved exact repair*' }
Assert-True $gateFailed 'manifest drift rejects before transaction'
$gateFailed=$false
try { [void](Assert-ScopedInstallApplyGates -ManifestDrift @() -Apply:$true -ProcessState ([pscustomobject]@{complete=$false;problems=@('COMMAND_LINE_UNAVAILABLE');active=@()})) } catch { $gateFailed=$_.Exception.Message -like '*PROCESS_INVENTORY_INCOMPLETE*' }
Assert-True $gateFailed 'incomplete process inventory rejects apply'

# Process inventory: writer roots and descendants block; missing required metadata blocks.
$root='C:\owner-release\ScrubBots Factory Studio'
$processes=@(
	[pscustomobject]@{ProcessId=10;ParentProcessId=1;Name='Godot_v4.7.2-stable_win64.exe';ExecutablePath="$root\Godot.exe";CommandLine="Godot --path `"$root\level_factory`""},
	[pscustomobject]@{ProcessId=11;ParentProcessId=10;Name='python.exe';ExecutablePath='C:\Python\python.exe';CommandLine='python.exe worker.py'},
	[pscustomobject]@{ProcessId=12;ParentProcessId=1;Name='svchost.exe';ExecutablePath='C:\Windows\System32\svchost.exe';CommandLine='svchost.exe'}
)
$inventory=Get-ScopedProcessInventoryState -Processes $processes -RuntimeRoot $root -CurrentPid 999
Assert-True $inventory.complete 'complete inventory accepted'
Assert-True (@($inventory.active.ProcessId) -contains 10 -and @($inventory.active.ProcessId) -contains 11) 'matching writer and child both identified'
$incomplete=Get-ScopedProcessInventoryState -Processes @([pscustomobject]@{ProcessId=3;Name='python.exe';ExecutablePath='C:\Python\python.exe'}) -RuntimeRoot $root -CurrentPid 999
Assert-True (-not $incomplete.complete -and $incomplete.status -eq 'PROCESS_INVENTORY_INCOMPLETE') 'missing parent/command metadata fails closed'
$emptyInventory=Get-ScopedProcessInventoryState -Processes @() -RuntimeRoot $root -CurrentPid 999
Assert-True (-not $emptyInventory.complete -and @($emptyInventory.problems) -contains 'PROCESS_INVENTORY_EMPTY') 'empty process inventory fails closed'

# A worker that appears only after staging is caught by the fresh pre-replacement snapshot.
Reset-FakeFileSystem
$script:freshProcessState=Get-ScopedProcessInventoryState -Processes @(
	[pscustomobject]@{ProcessId=40;ParentProcessId=1;Name='Godot_v4.7.2-stable_win64.exe';ExecutablePath="$root\Godot.exe";CommandLine="Godot --path `"$root\level_factory`""},
	[pscustomobject]@{ProcessId=41;ParentProcessId=40;Name='python.exe';ExecutablePath='C:\Python\python.exe';CommandLine='python.exe worker.py'}
) -RuntimeRoot $root -CurrentPid 999
$lateWriterBlocked=$false
 $lateWriterError=''
try { [void](Invoke-FakeTransaction) } catch { $lateWriterError=$_.Exception.Message; $lateWriterBlocked=$lateWriterError -like '*Active processes*' }
Assert-True $lateWriterBlocked "late writer/child snapshot blocks replacement: $lateWriterError"
Assert-True ($script:stageWriteCalls -gt 0 -and $script:replaceCalls -eq 0) 'late writer is discovered after staging and before the first replacement'
Assert-Restored 'late writer block'

# CIM failure or incomplete process metadata also blocks before any replacement.
foreach ($badState in @(
	[pscustomobject]@{complete=$false;status='PROCESS_INVENTORY_INCOMPLETE';problems=@('CIM_QUERY_FAILED:denied');active=@()},
	[pscustomobject]@{complete=$false;status='PROCESS_INVENTORY_INCOMPLETE';problems=@('COMMAND_LINE_UNAVAILABLE:41');active=@()}
)) {
	Reset-FakeFileSystem; $script:freshProcessState=$badState
	$inventoryBlocked=$false
	try { [void](Invoke-FakeTransaction) } catch { $inventoryBlocked=$_.Exception.Message -like '*PROCESS_INVENTORY_INCOMPLETE*' }
	Assert-True $inventoryBlocked 'fresh incomplete process inventory blocks replacement'
	Assert-True ($script:replaceCalls -eq 0) 'incomplete inventory leaves replacement count at zero'
	Assert-Restored 'incomplete fresh inventory'
}

# Without an exclusive-writer control, even a complete empty snapshot cannot prove quiescence.
Reset-FakeFileSystem
$script:writerLeaseEstablished=$false
$quiescenceBlocked=$false
try {
	$plan=@([pscustomobject]@{path='one.py';source='source-one';target='target-one';sha256=(Get-FakeHash (ConvertTo-FakeBytes 'new-one'));priorSha256=(Get-FakeHash (ConvertTo-FakeBytes 'old-one'));priorExists=$true;bytes=7})
	$manifest=Get-FakeText 'manifest' | ConvertFrom-Json
	[void](Invoke-ScopedOverlayTransaction -Plan $plan -Manifest $manifest -ManifestPath 'manifest' -TransactionRoot 'C:\owner-release\.txn-r04' -SourceHead 'head-r04' -OverlayAdditions @() -Operations $script:fakeOperations)
} catch { $quiescenceBlocked=$_.Exception.Message -like '*PROCESS_QUIESCENCE_UNPROVEN*' }
Assert-True $quiescenceBlocked 'missing acquired exclusive-writer lease reports PROCESS_QUIESCENCE_UNPROVEN'
Assert-True ($script:replaceCalls -eq 0 -and (Get-FakeText 'target-one') -ceq 'old-one') 'unproven quiescence leaves target unchanged'

# Execute wrapper outcome mapping with synthetic results for every public status.
$outcomeLines=@(Write-ScopedOverlayOutcome ([pscustomobject]@{status='COMMITTED';changedPaths=@('one.py');verifiedHashes=@([pscustomobject]@{path='one.py';sha256='a'*64})}))
Assert-True ($outcomeLines.Count -eq 2) 'committed output is one JSON line and one operator line'
$outcome=[string]$outcomeLines[0] | ConvertFrom-Json
Assert-True ($outcome.status -eq 'COMMITTED' -and $outcome.changedPaths[0] -eq 'one.py' -and $outcome.verifiedHashes.Count -eq 1 -and $outcome.verifiedHashes[0].sha256 -eq ('a'*64) -and [string]$outcomeLines[1] -eq 'OWNER_DESKTOP_STUDIO_SCOPED_OVERLAY_UPDATED') 'committed wrapper output carries exact scope and verified hash'
$outcomeLines=@(Write-ScopedOverlayOutcome ([pscustomobject]@{status='COMMITTED_CLEANUP_PENDING';changedPaths=@('one.py');verifiedHashes=@([pscustomobject]@{path='one.py';sha256='a'*64});transactionRoot='C:\owner-release\.txn-r04';cleanupError='access denied'}))
Assert-True ($outcomeLines.Count -eq 2) 'cleanup-pending output is one JSON line and one operator line'
$outcome=[string]$outcomeLines[0] | ConvertFrom-Json
Assert-True ($outcome.status -eq 'COMMITTED_CLEANUP_PENDING' -and $outcome.changedPaths[0] -eq 'one.py' -and $outcome.verifiedHashes[0].sha256 -eq ('a'*64) -and $outcome.evidencePath -eq $outcome.transactionRoot -and $outcome.errorReason -eq 'access denied' -and $outcome.nextAction -match 'Preserve' -and [string]$outcomeLines[1] -match 'COMMITTED_CLEANUP_PENDING') 'cleanup-pending wrapper output exposes evidence, reason and safe next action'
$outcomeLines=@(Write-ScopedOverlayOutcome ([pscustomobject]@{status='NO_OP';changedPaths=@()}))
Assert-True ($outcomeLines.Count -eq 2) 'no-op output is one JSON line and one operator line'
$outcome=[string]$outcomeLines[0] | ConvertFrom-Json
Assert-True ($outcome.status -eq 'NO_OP' -and $outcome.changedPaths.Count -eq 0 -and [string]$outcomeLines[1] -match 'no installed files changed') 'no-op wrapper output is distinct from commit'
$mappingFailed=$false
try { [void](Write-ScopedOverlayOutcome ([pscustomobject]@{status='TRANSACTION_FAILED_ROLLBACK_INCOMPLETE'})) } catch { $mappingFailed=$_.Exception.Message -like '*failing closed*' }
Assert-True $mappingFailed 'transaction failure cannot be downgraded to success'

# No-op must not call any I/O adapter.
$noop=Invoke-ScopedOverlayTransaction -Plan @() -Manifest ([pscustomobject]@{}) -ManifestPath 'none' -TransactionRoot 'none' -SourceHead 'head' -OverlayAdditions @() -Operations @{}
Assert-True ($noop.status -eq 'NO_OP') 'empty plan is a no-op'

# Staging failure: no payload or manifest replacement occurred.
Reset-FakeFileSystem; $script:failStageWriteAt=2; Assert-TransactionFailure 'ROLLBACK_VERIFIED' 'staging fault'; Assert-Restored 'staging fault'; Assert-True ($script:replaceCalls -eq 0) 'staging fault made zero live replacements'

# Payload replace faults before the second and after the second atomic replacement.
Reset-FakeFileSystem; $script:failReplaceBeforeAt=2; Assert-TransactionFailure 'ROLLBACK_VERIFIED' 'payload replace-before fault'; Assert-Restored 'payload replace-before fault'
Reset-FakeFileSystem; $script:failReplaceAfterAt=2; Assert-TransactionFailure 'ROLLBACK_VERIFIED' 'payload replace-after-second fault'; Assert-Restored 'payload replace-after-second fault'

# Manifest replacement may throw after the atomic replacement; it must still restore manifest and payloads.
Reset-FakeFileSystem; $script:failReplaceAfterAt=3; Assert-TransactionFailure 'ROLLBACK_VERIFIED' 'manifest replace-after fault'; Assert-Restored 'manifest replace-after fault'

# Final hash verification fault must reverse all live payload changes and manifest.
Reset-FakeFileSystem; $script:failFinalVerification=$true; Assert-TransactionFailure 'ROLLBACK_VERIFIED' 'final verification fault'; Assert-Restored 'final verification fault'

# A failed restore is reported honestly, all other restores are attempted, and transaction evidence remains.
Reset-FakeFileSystem; $script:failReplaceAfterAt=2; $script:failRollbackTarget='target-one'; Assert-TransactionFailure 'ROLLBACK_INCOMPLETE' 'restore fault'; Assert-True ((Get-FakeText 'target-two') -ceq 'old-two') 'other restore continues after one restore fails'; Assert-True (@($script:fakeFiles.Keys | Where-Object { $_ -like 'C:\owner-release\.txn-r03*' }).Count -gt 0) 'rollback evidence retained on incomplete recovery'

# Successful transaction updates only its two planned payloads and the manifest.
Reset-FakeFileSystem; $committed=Invoke-FakeTransaction; Assert-True ($committed.status -eq 'COMMITTED') 'successful transaction committed'; Assert-True ((Get-FakeText 'target-one') -ceq 'new-one' -and (Get-FakeText 'target-two') -ceq 'new-two') 'successful transaction writes planned payloads'; Assert-True ((Get-FakeText 'png-batch-protected') -ceq 'immutable-job-bytes' -and (Get-FakeText 'release-pool-protected') -ceq 'immutable-pool-bytes' -and (Get-FakeText 'owner-png-protected') -ceq 'immutable-png-bytes') 'successful transaction leaves batch, pool and PNG unchanged'

# A new source dependency is added only when both the manifest entry and target are absent.
Reset-FakeFileSystem
Put-FakeText 'source-new' 'new-atlas-module'
$newPlan=@([pscustomobject]@{path='new.py';source='source-new';target='target-new';sha256=(Get-FakeHash (ConvertTo-FakeBytes 'new-atlas-module'));priorSha256=$null;priorExists=$false;bytes=16})
$newManifest=Get-FakeText 'manifest' | ConvertFrom-Json
$added=Invoke-ScopedOverlayTransaction -Plan $newPlan -Manifest $newManifest -ManifestPath 'manifest' -TransactionRoot 'C:\owner-release\.txn-new' -SourceHead 'head-add' -OverlayAdditions @('new.py') -NewManagedPaths @('new.py') -Operations $script:fakeOperations
Assert-True ($added.status -eq 'COMMITTED' -and (Get-FakeText 'target-new') -ceq 'new-atlas-module') 'authorized absent target is atomically added'
$addedManifest=Get-FakeText 'manifest' | ConvertFrom-Json
Assert-True (@($addedManifest.managedFiles | Where-Object { $_.path -ceq 'new.py' }).Count -eq 1 -and $addedManifest.overlayReceipts[-1].files[0].priorExists -eq $false -and $addedManifest.overlayReceipts[-1].files[0].sha256 -ceq (Get-FakeHash (ConvertTo-FakeBytes 'new-atlas-module')) -and $addedManifest.overlayReceipts[-1].writerExclusionMethod -match 'no-overwrite move') 'addition receipt records prior absence, source hash and writer method'

# A race-created destination is never overwritten by a new-file move.
Reset-FakeFileSystem
Put-FakeText 'source-new' 'new-atlas-module'
$script:fakeOperations.AcquireWriterExclusion = { param($live,$staged) Put-FakeText 'target-new' 'owner-concurrent-bytes'; return @{established=$true;method=Get-ScopedWriterExclusionMethod;handles=@()} }
$newManifest=Get-FakeText 'manifest' | ConvertFrom-Json
$raceRejected=$false
$raceError=''
try { [void](Invoke-ScopedOverlayTransaction -Plan $newPlan -Manifest $newManifest -ManifestPath 'manifest' -TransactionRoot 'C:\owner-release\.txn-race' -SourceHead 'head-add' -OverlayAdditions @('new.py') -NewManagedPaths @('new.py') -Operations $script:fakeOperations) } catch { $raceError=$_.Exception.Message; $raceRejected=$raceError -match 'existence changed after exclusive lock|unexpectedly exists|target already exists' }
Assert-True $raceRejected "new target race fails closed without overwrite: $raceError"
Assert-True ((Get-FakeText 'target-new') -ceq 'owner-concurrent-bytes') 'new target race preserves concurrent owner bytes'
$script:fakeOperations.AcquireWriterExclusion = { param($live,$staged) return @{established=$script:writerLeaseEstablished;method=if($script:writerLeaseEstablished){Get-ScopedWriterExclusionMethod}else{''};handles=@()} }

# Cleanup failure after verified commit does not trigger rollback or claim failure of payload installation.
Reset-FakeFileSystem; $script:failRemoveTree=$true; $committed=Invoke-FakeTransaction; Assert-True ($committed.status -eq 'COMMITTED_CLEANUP_PENDING' -and $committed.verifiedHashes.Count -eq 2) 'cleanup failure preserves verified commit status and exact hashes'; Assert-True ((Get-FakeText 'target-one') -ceq 'new-one' -and (Get-FakeText 'target-two') -ceq 'new-two') 'cleanup failure does not attempt unsafe post-commit rollback'

'SCOPED_OVERLAY_TRANSACTION_IN_MEMORY_TESTS_PASS'
