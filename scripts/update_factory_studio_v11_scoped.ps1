[CmdletBinding()]
param([switch]$Apply)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$ExpectedRepo = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator'
$Install = Join-Path $ExpectedRepo 'Release\ScrubBots Factory Studio'
$ManifestPath = Join-Path $Install '.factory-studio-install-manifest.json'
$TaskId = 'SB-LFX-018-R05-M03-V11'
$Targets = @(
    [pscustomobject]@{ Path='level_factory/scripts/factory_core_launcher.py'; Old='90ef660fc55af5eec157d6b8347052f4ea426e672ca9afe595fe024691f74d0f'; Add=$false },
    [pscustomobject]@{ Path='src/scrubbots_pixel_factory/studio_extensions.py'; Old='c26ff4129dd16518fc766a1dcf65ba3299bb3cc2dc8a0b40d9474345e0316e2b'; Add=$false },
    [pscustomobject]@{ Path='src/scrubbots_pixel_factory/supply_pipeline/release_pool.py'; Old='8ade04a6f744c9779608e3550fdc6a1ec15e421011574c0edf0034478853d5c3'; Add=$false },
    [pscustomobject]@{ Path='src/scrubbots_pixel_factory/supply_pipeline/current_game_contract.py'; Old=$null; Add=$true },
    [pscustomobject]@{ Path='src/scrubbots_pixel_factory/contracts/candidate_provenance.py'; Old=$null; Add=$true }
)

function Sha([byte[]]$Bytes) {
    $h=[Security.Cryptography.SHA256]::HashData($Bytes)
    ([BitConverter]::ToString($h)).Replace('-','').ToLowerInvariant()
}
function Git([string[]]$Args) {
    $o=& git -C $Repo @Args 2>&1
    if($LASTEXITCODE -ne 0){ throw "git $($Args -join ' ') failed: $($o -join ' ')" }
    (($o | Out-String).Trim())
}
function NoReparse([string]$Path) {
    $p=[IO.Path]::GetFullPath($Path)
    while($p){
        if(Test-Path -LiteralPath $p){
            $i=Get-Item -LiteralPath $p -Force
            if(($i.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){ throw "Reparse point blocks scoped update: $p" }
        }
        $parent=[IO.Directory]::GetParent($p); if($null -eq $parent){break}; $p=$parent.FullName
    }
}
function InstalledStudioProcesses {
    $release=[IO.Path]::GetFullPath($Install).TrimEnd('\')
    @(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^godot(_console)?\.exe$' -and
        (($_.CommandLine + "`n" + $_.ExecutablePath).IndexOf($release,[StringComparison]::OrdinalIgnoreCase) -ge 0)
    })
}

if($Repo -ine $ExpectedRepo){ throw "Unexpected repository root: $Repo" }
NoReparse $Repo; NoReparse $Install; NoReparse $ManifestPath
if(!(Test-Path -LiteralPath $Install -PathType Container)){ throw 'Existing installed Release project is missing.' }
$head=Git @('rev-parse','HEAD'); $remote=Git @('rev-parse','origin/main')
if($head -cne $remote){ throw "Published HEAD must equal origin/main before installation: HEAD=$head origin/main=$remote" }
if(Git @('status','--porcelain=v1','--untracked-files=no')){ throw 'Tracked checkout must be clean before installation.' }
$processes=InstalledStudioProcesses
if($processes.Count){ throw "OWNER_CLOSE_APP_REQUIRED: installed Studio/Godot process PID $($processes[0].ProcessId) is using this Release." }
if(!(Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw 'Installed manifest is missing.' }
$manifestBytes=[IO.File]::ReadAllBytes($ManifestPath); $manifestSha=Sha $manifestBytes
$manifest=[Text.Encoding]::UTF8.GetString($manifestBytes)|ConvertFrom-Json
if($manifest.formatVersion -ne 1 -or $manifest.installationMode -cne 'OWNER_APPROVED_SCOPED_OVERLAY' -or $manifest.baseRevision -cne '17643de6756ba3d9552351eb237db19bd8d0c269') { throw 'MANAGED_INSTALL_CONFLICT: installed format/mode/base revision differs from the approved scoped overlay.' }
if(@($manifest.managedFiles).Count -ne 2316 -or @($manifest.overlayPaths).Count -ne 9 -or @($manifest.overlayReceipts).Count -ne 3){ throw 'MANAGED_INSTALL_CONFLICT: installed manifest counts or historical receipts changed.' }
$plans=[Collections.Generic.List[object]]::new(); $missingDeps=[Collections.Generic.List[string]]::new(); $installedBytesTotal=0; $sourceBytesTotal=0
foreach($t in $Targets){
    $src=Join-Path $Repo ($t.Path -replace '/','\'); $dst=Join-Path $Install ($t.Path -replace '/','\')
    NoReparse $src; NoReparse $dst
    if(!(Test-Path -LiteralPath $src -PathType Leaf)){ throw "Published source file missing: $($t.Path)" }
    $gitBlob=Git @('rev-parse',"HEAD:$($t.Path)"); $workBlob=Git @('hash-object',"--path=$($t.Path)",$src)
    if($gitBlob -cne $workBlob){ throw "Source differs from published Git bytes: $($t.Path)" }
    $bytes=[IO.File]::ReadAllBytes($src); $newSha=Sha $bytes; $sourceBytesTotal += $bytes.Length
    $entries=@($manifest.managedFiles | Where-Object path -CEQ $t.Path)
    $overlays=@($manifest.overlayPaths | Where-Object { $_ -ceq $t.Path })
    if($t.Add){
        if($entries.Count -or $overlays.Count -or (Test-Path -LiteralPath $dst)){ throw "MANAGED_INSTALL_CONFLICT: additive destination exists or is already tracked: $($t.Path)" }
        $oldSha=$null; $oldBytes=$null
    } else {
        if($entries.Count -ne 1 -or $overlays.Count -ne 1 -or !(Test-Path -LiteralPath $dst -PathType Leaf)){ throw "MANAGED_INSTALL_CONFLICT: target is not uniquely managed/overlaid: $($t.Path)" }
        $oldBytes=[IO.File]::ReadAllBytes($dst); $oldSha=Sha $oldBytes; $installedBytesTotal += $oldBytes.Length
        if($oldSha -cne $t.Old -or $entries[0].sha256.ToLowerInvariant() -cne $oldSha){ throw "MANAGED_INSTALL_CONFLICT: installed or manifest SHA changed for $($t.Path); installed=$oldSha" }
    }
    $plans.Add([pscustomobject]@{ Path=$t.Path; Source=$src; Destination=$dst; Bytes=$bytes; NewSha=$newSha; OldBytes=$oldBytes; OldSha=$oldSha; Add=$t.Add })
}
$manifestCopy=ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $manifest -Depth 100 -Compress)
foreach($plan in $plans){
    $entry=@($manifestCopy.managedFiles | Where-Object path -CEQ $plan.Path)
    if($plan.Add){
        $manifestCopy.managedFiles += [pscustomobject][ordered]@{path=$plan.Path;sha256=$plan.NewSha}
        $manifestCopy.overlayPaths += $plan.Path
    } else { $entry[0].sha256=$plan.NewSha }
}
$receipt=[pscustomobject][ordered]@{
    taskId=$TaskId; sourceCommit=(Git @('log','-1','--format=%H','--',$Targets[0].Path)); sourceHead=$head
    files=@($plans | ForEach-Object { [pscustomobject][ordered]@{path=$_.Path;priorSha256=$_.OldSha;sha256=$_.NewSha;bytes=$_.Bytes.Length} })
    installedAtUtc=[DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
}
$manifestCopy.overlayReceipts=@($manifestCopy.overlayReceipts)+@($receipt)
$newManifestBytes=[Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Json -InputObject $manifestCopy -Depth 100)+"`n")
$newManifestSha=Sha $newManifestBytes
"PREFLIGHT_OK MODE=$(if($Apply){'APPLY'}else{'READ_ONLY'}) HEAD=$head MANIFEST_SHA=$manifestSha TARGETS=$($plans.Count) REPLACEMENTS=$(@($plans|Where-Object{-not $_.Add}).Count) ADDITIONS=$(@($plans|Where-Object{$_.Add}).Count) PRIOR_RUNTIME_BYTES=$installedBytesTotal NEW_RUNTIME_BYTES=$sourceBytesTotal NEW_MANIFEST_SHA=$newManifestSha"
foreach($p in $plans){ "TARGET $($p.Path) $(if($p.Add){'ADD'}else{'REPLACE'}) prior=$($p.OldSha) new=$($p.NewSha) bytes=$($p.Bytes.Length)" }
if(!$Apply){ exit 0 }

$stagePaths=[Collections.Generic.List[string]]::new(); $written=[Collections.Generic.List[object]]::new(); $manifestStage="$ManifestPath.m03-v11-stage"
if(Test-Path -LiteralPath $manifestStage){ throw 'Refusing to overwrite existing manifest stage file.' }
try {
    foreach($p in $plans){
        $parent=Split-Path -Parent $p.Destination
        if(!(Test-Path -LiteralPath $parent -PathType Container)){ throw "Required installed directory is absent: $parent" }
        $stage="$($p.Destination).m03-v11-stage"
        if(Test-Path -LiteralPath $stage){ throw "Refusing to overwrite existing stage file: $stage" }
        [IO.File]::WriteAllBytes($stage,$p.Bytes); $stagePaths.Add($stage)
        if((Sha ([IO.File]::ReadAllBytes($stage))) -cne $p.NewSha){ throw "Staged file hash mismatch: $($p.Path)" }
    }
    [IO.File]::WriteAllBytes($manifestStage,$newManifestBytes); $stagePaths.Add($manifestStage)
    if((Sha ([IO.File]::ReadAllBytes($manifestStage))) -cne $newManifestSha){ throw 'Staged manifest hash mismatch.' }
    if((Sha ([IO.File]::ReadAllBytes($ManifestPath))) -cne $manifestSha -or (InstalledStudioProcesses).Count){ throw 'Installed state or app process changed during staging; no install performed.' }
    foreach($p in $plans){
        if($p.Add){ [IO.File]::Move("$($p.Destination).m03-v11-stage",$p.Destination) }
        else { [IO.File]::Replace("$($p.Destination).m03-v11-stage",$p.Destination,$null) }
        $written.Add($p)
        if((Sha ([IO.File]::ReadAllBytes($p.Destination))) -cne $p.NewSha){ throw "Installed file hash mismatch: $($p.Path)" }
    }
    [IO.File]::Replace($manifestStage,$ManifestPath,$null)
    if((Sha ([IO.File]::ReadAllBytes($ManifestPath))) -cne $newManifestSha){ throw 'Installed manifest hash mismatch.' }
    foreach($p in $plans){ if((Sha ([IO.File]::ReadAllBytes($p.Destination))) -cne $p.NewSha){ throw "Final verification failed: $($p.Path)" } }
    'SCOPED_RUNTIME_UPDATE_APPLIED_AND_HASH_VERIFIED'
}
catch {
    $failure=$_
    for($i=$written.Count-1;$i -ge 0;$i--){
        $p=$written[$i]
        try {
            if($p.Add){ [IO.File]::Delete($p.Destination) }
            else { [IO.File]::WriteAllBytes($p.Destination,$p.OldBytes) }
        } catch { throw "UPDATE_FAILED_ROLLBACK_INCOMPLETE path=$($p.Path) original=$failure rollback=$_" }
    }
    if((Test-Path -LiteralPath $ManifestPath) -and (Sha ([IO.File]::ReadAllBytes($ManifestPath))) -ne $manifestSha){ [IO.File]::WriteAllBytes($ManifestPath,$manifestBytes) }
    throw "UPDATE_FAILED_ROLLED_BACK: $failure"
}
finally { foreach($s in $stagePaths){ if(Test-Path -LiteralPath $s){ Remove-Item -LiteralPath $s -Force } } }
