[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Rollback
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:TaskId = 'SB-LFX-018-R05-MASTER-M01'
$script:ControllerRelative = 'level_factory/scripts/factory_studio_exact_ui.gd'
$script:ExpectedOldControllerSha = 'e0a44647f5e54d9b18ca76cf50d8582be41e36bacc6f5400229cc777bfd0b9c2'
$script:ExpectedOldManifestSha = '56c9f32518fe01b2354942600c8d19662cab0713a23b42551304fccfbc0493eb'
$script:ExpectedOldControllerBytes = 197118
$script:ExpectedOldManifestBytes = 455309
$script:ExpectedR04ReceiptCommit = 'aded2fd5473ebd4af59e677451ee9eb26a1408bd'
$script:ExpectedR04ReceiptHead = 'ff777c8f3739261c4295f0f33b9ef83c4f2896a4'
$script:ExpectedR04PriorSha = '65a2eafee2620c8d35fafc84a8fb3748ad60d37a7a8bd9d33e634bed3e054c0c'
$script:ExpectedMode = 'OWNER_APPROVED_SCOPED_OVERLAY'
$script:ExpectedBaseRevision = '17643de6756ba3d9552351eb237db19bd8d0c269'
$script:ExpectedSourceRevision = '89d74c9fe758ad0766f7ff5290154a1f56548b14'
$script:ExpectedOverlayCount = 9
$script:ShortcutPath = 'C:\Users\sekip\Desktop\ScrubBots Factory Studio.lnk'
$script:ExpectedShortcutSha = 'cacfea6f3aa10866b80d3e0ee2bb1973752945d956ae57e1a783f6a7e6972a61'
$script:ExpectedLauncherSha = '27bea63d0b0eb44ef6a564bcee8ffeac03b07009b5aaa8b504be0445fa2c87c0'
$script:ExpectedProjectSha = '8326e0e2933ef1959ed67e9b61981a7860d54b13503ab90fe41507b839651836'
$script:ExpectedIconSha = '06049274e80487bed3c23f1cc9d549b5f17f851132b2e5361f4eda7d0ecb93fa'

$script:RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$script:ExpectedRepoRoot = 'C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator'
$script:ReleaseRoot = Join-Path $script:ExpectedRepoRoot 'Release\ScrubBots Factory Studio'
$script:ManifestPath = Join-Path $script:ReleaseRoot '.factory-studio-install-manifest.json'
$script:ControllerPath = Join-Path $script:ReleaseRoot ($script:ControllerRelative.Replace('/', '\'))
$script:SourcePath = Join-Path $script:RepoRoot ($script:ControllerRelative.Replace('/', '\'))
$script:RollbackController = Join-Path $script:ReleaseRoot '.r05-m01-rollback-controller-e0a44647f5e5.bin'
$script:RollbackManifest = Join-Path $script:ReleaseRoot '.r05-m01-rollback-manifest-56c9f32518fe.json'
$script:StageController = Join-Path $script:ReleaseRoot '.r05-m01-stage-controller.tmp'
$script:StageManifest = Join-Path $script:ReleaseRoot '.r05-m01-stage-manifest.tmp'

function Get-FileSha256([string]$Path) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $stream = [IO.File]::OpenRead($Path)
        try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
        finally { $stream.Dispose() }
    }
    finally { $sha.Dispose() }
}

function Assert-NoReparsePath([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Reparse point or junction is not allowed: $current"
            }
        }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent) { break }
        $current = $parent.FullName
    }
}

function Invoke-Git([string[]]$Arguments) {
    $output = & git -C $script:RepoRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git $($Arguments -join ' ') failed: $($output -join ' ')" }
    return (($output | Out-String).Trim())
}

function Assert-PublishedSource {
    if ($script:RepoRoot -ine $script:ExpectedRepoRoot) { throw "Unexpected repository root: $script:RepoRoot" }
    $gitRoot = (Invoke-Git @('rev-parse', '--show-toplevel')).Replace('/', '\').TrimEnd('\')
    $canonicalRoot = [IO.Path]::GetFullPath($script:ExpectedRepoRoot).TrimEnd('\')
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals($gitRoot, $canonicalRoot)) { throw 'Git root does not match canonical Desktop checkout.' }
    if ((Invoke-Git @('branch', '--show-current')) -cne 'main') { throw 'Updater requires branch main.' }
    $head = Invoke-Git @('rev-parse', 'HEAD')
    $origin = Invoke-Git @('rev-parse', 'origin/main')
    if ($head -cne $origin) { throw 'HEAD is not the latest locally fetched origin/main.' }
    $dirty = Invoke-Git @('status', '--porcelain=v1', '--untracked-files=no')
    if ($dirty) { throw 'Tracked working tree is not clean.' }
    $sourceCommit = Invoke-Git @('log', '-1', '--format=%H', '--', $script:ControllerRelative)
    if ($sourceCommit -notmatch '^[0-9a-f]{40}$') { throw 'Could not identify the published controller source commit.' }
    $sourceHash = Get-FileSha256 $script:SourcePath
    $blob = Invoke-Git @('rev-parse', "HEAD:$($script:ControllerRelative)")
    $workingBlob = Invoke-Git @('hash-object', "--path=$($script:ControllerRelative)", $script:SourcePath)
    if ($workingBlob -cne $blob) { throw 'Working controller bytes do not match the published Git blob.' }
    return [pscustomobject]@{ Head = $head; SourceCommit = $sourceCommit; SourceSha = $sourceHash }
}

function Assert-ManifestState($Manifest, [string]$InstalledControllerSha) {
    if ($Manifest.formatVersion -ne 1) { throw 'Installed manifest formatVersion is not 1.' }
    if ($Manifest.installationMode -cne $script:ExpectedMode) { throw 'Installed installationMode changed.' }
    if ($Manifest.baseRevision -cne $script:ExpectedBaseRevision) { throw 'Installed baseRevision changed.' }
    if ($Manifest.sourceRevision -cne $script:ExpectedSourceRevision) { throw 'Installed sourceRevision changed.' }
    if (@($Manifest.managedFiles).Count -ne 2316) { throw 'Installed managedFiles count is not 2,316.' }
    if (@($Manifest.overlayPaths).Count -ne $script:ExpectedOverlayCount) { throw 'Installed overlayPaths count is not nine.' }
    $approvedOverlay = @($Manifest.overlayPaths | Where-Object { $_ -ceq $script:ControllerRelative })
    $managedTarget = @($Manifest.managedFiles | Where-Object { $_.path -ceq $script:ControllerRelative })
    if ($approvedOverlay.Count -ne 1 -or $managedTarget.Count -ne 1) { throw 'Controller is not approved exactly once in both manifest lists.' }
    if ($managedTarget[0].sha256 -cne $InstalledControllerSha) { throw 'Controller SHA in manifest does not match installed bytes.' }
    return $managedTarget[0]
}

function Get-OtherManagedSignature($Manifest) {
    $pairs = @($Manifest.managedFiles | Where-Object { $_.path -cne $script:ControllerRelative } | Sort-Object -Property path | ForEach-Object { "$($_.path)|$($_.sha256)" })
    if ($pairs.Count -ne 2315) { throw 'Expected exactly 2,315 non-controller managed entries.' }
    return [string]::Join("`n", $pairs)
}

function Assert-R04Receipt($Manifest) {
    $receipts = @($Manifest.overlayReceipts)
    if ($receipts.Count -ne 1) { throw 'The exact R04 overlay receipt must be preserved before appending M01.' }
    $receipt = $receipts[0]
    if ($receipt.taskId -cne 'SB-LFX-018-R05-G02-R04' -or $receipt.sourceCommit -cne $script:ExpectedR04ReceiptCommit -or $receipt.sourceHead -cne $script:ExpectedR04ReceiptHead -or $receipt.controllerPath -cne $script:ControllerRelative -or $receipt.priorSha256 -cne $script:ExpectedR04PriorSha -or $receipt.controllerSha256 -cne $script:ExpectedOldControllerSha) {
        throw 'The existing R04 provenance receipt differs from the accepted baseline.'
    }
}

function Assert-NotAlreadyInstalled([string]$InstalledSha, [string]$SourceSha) {
    if ($InstalledSha -ceq $SourceSha) { throw 'Installed controller already equals current source.' }
}

function New-UpdatedManifest($Manifest, [string]$OldSha, [string]$NewSha, [string]$SourceCommit, [string]$SourceHead) {
    Assert-R04Receipt $Manifest
    $target = Assert-ManifestState $Manifest $OldSha
    $copy = ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $Manifest -Depth 100 -Compress)
    $copyTarget = @($copy.managedFiles | Where-Object { $_.path -ceq $script:ControllerRelative })[0]
    $copyTarget.sha256 = $NewSha
    $receipt = [pscustomobject][ordered]@{
        taskId = $script:TaskId
        sourceCommit = $SourceCommit
        sourceHead = $SourceHead
        controllerPath = $script:ControllerRelative
        priorSha256 = $OldSha
        controllerSha256 = $NewSha
        installedAtUtc = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    }
    $copy.overlayReceipts = @($copy.overlayReceipts) + @($receipt)
    return $copy
}

function Write-CreateNew([string]$Path, [byte[]]$Bytes) {
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($Bytes, 0, $Bytes.Length); $stream.Flush($true) }
    finally { $stream.Dispose() }
}

function Move-ReplaceFile([string]$Source, [string]$Destination) {
    if (-not ('R04AtomicFile' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class R04AtomicFile {
 [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true, EntryPoint="MoveFileExW")]
 static extern bool MoveFileEx(string existingName, string newName, uint flags);
 public static void Replace(string existingName, string newName) {
  if (!MoveFileEx(existingName,newName,0x1|0x8)) throw new Win32Exception(Marshal.GetLastWin32Error());
 }
}
'@
    }
    [R04AtomicFile]::Replace($Source, $Destination)
}

function Assert-WritePreconditions([string]$ExpectedInstalledControllerSha, [string]$ExpectedInstalledManifestSha, [string[]]$WritePaths) {
    Assert-NoReparsePath $script:RepoRoot
    Assert-NoReparsePath $script:ReleaseRoot
    Assert-NoReparsePath $script:ControllerPath
    Assert-NoReparsePath $script:ManifestPath
    foreach ($path in $WritePaths) { Assert-NoReparsePath $path }
    $processes = @(Get-InstalledStudioProcesses)
    if ($processes.Count -ne 0) { throw 'Installed Factory Studio is running; no write is allowed.' }
    if ((Get-FileSha256 $script:ControllerPath) -cne $ExpectedInstalledControllerSha -or (Get-FileSha256 $script:ManifestPath) -cne $ExpectedInstalledManifestSha) {
        throw 'Installed controller/manifest state changed before a write.'
    }
}

function Restore-Previous([byte[]]$ControllerBytes, [byte[]]$ManifestBytes, [string]$CurrentControllerSha, [string]$CurrentManifestSha) {
    Assert-WritePreconditions $CurrentControllerSha $CurrentManifestSha @($script:StageController)
    Write-CreateNew $script:StageController $ControllerBytes
    Assert-WritePreconditions $CurrentControllerSha $CurrentManifestSha @($script:StageManifest)
    Write-CreateNew $script:StageManifest $ManifestBytes
    if ((Get-FileSha256 $script:StageController) -cne $script:ExpectedOldControllerSha -or (Get-FileSha256 $script:StageManifest) -cne $script:ExpectedOldManifestSha) { throw 'Rollback stage hash verification failed.' }
    Assert-WritePreconditions $CurrentControllerSha $CurrentManifestSha @($script:StageController, $script:ControllerPath)
    Move-ReplaceFile $script:StageController $script:ControllerPath
    Assert-WritePreconditions $script:ExpectedOldControllerSha $CurrentManifestSha @($script:StageManifest, $script:ManifestPath)
    Move-ReplaceFile $script:StageManifest $script:ManifestPath
    if ((Get-FileSha256 $script:ControllerPath) -cne $script:ExpectedOldControllerSha) { throw 'Controller rollback hash verification failed.' }
    if ((Get-FileSha256 $script:ManifestPath) -cne $script:ExpectedOldManifestSha) { throw 'Manifest rollback hash verification failed.' }
}

function Get-InstalledStudioProcesses {
    if (-not ('R04InstalledCwd' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class R04InstalledCwd {
 [StructLayout(LayoutKind.Sequential)] public struct PBI { public IntPtr R1; public IntPtr Peb; public IntPtr R2a; public IntPtr R2b; public IntPtr Pid; public IntPtr R3; }
 [StructLayout(LayoutKind.Sequential)] public struct US { public ushort Length; public ushort MaximumLength; public IntPtr Buffer; }
 [DllImport("kernel32.dll", SetLastError=true)] static extern IntPtr OpenProcess(uint access, bool inherit, int pid);
 [DllImport("kernel32.dll", SetLastError=true)] static extern bool ReadProcessMemory(IntPtr process, IntPtr address, byte[] buffer, int size, out IntPtr read);
 [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr handle);
 [DllImport("ntdll.dll")] static extern int NtQueryInformationProcess(IntPtr process, int cls, ref PBI pbi, int len, out int returned);
 static IntPtr Add(IntPtr p,int n)=>new IntPtr(p.ToInt64()+n);
 static byte[] Read(IntPtr h,IntPtr a,int n){byte[] b=new byte[n];IntPtr got;if(!ReadProcessMemory(h,a,b,n,out got)||got.ToInt64()!=n)throw new Exception();return b;}
 static IntPtr Ptr(byte[] b,int o)=>IntPtr.Size==8?new IntPtr(BitConverter.ToInt64(b,o)):new IntPtr(BitConverter.ToInt32(b,o));
 public static string Get(int pid){IntPtr h=OpenProcess(0x1010,false,pid);if(h==IntPtr.Zero)return "<unreadable>";try{PBI p=new PBI();int n;if(NtQueryInformationProcess(h,0,ref p,Marshal.SizeOf(typeof(PBI)),out n)!=0)return "<unreadable>";IntPtr pp=Ptr(Read(h,Add(p.Peb,IntPtr.Size==8?0x20:0x10),IntPtr.Size),0);byte[] u=Read(h,Add(pp,IntPtr.Size==8?0x38:0x24),IntPtr.Size==8?16:8);ushort len=BitConverter.ToUInt16(u,0);if(len==0)return "";IntPtr b=Ptr(u,IntPtr.Size==8?8:4);return Encoding.Unicode.GetString(Read(h,b,len));}catch{return "<unreadable>";}finally{CloseHandle(h);}}
}
'@
    }
    $release = [IO.Path]::GetFullPath($script:ReleaseRoot).TrimEnd('\')
    $matches = @()
    $godot = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^godot(_console)?\.exe$' })
    foreach ($process in $godot) {
        $cwd = [R04InstalledCwd]::Get([int]$process.ProcessId)
        $references = (($process.ExecutablePath + "`n" + $process.CommandLine + "`n" + $cwd).IndexOf($release, [StringComparison]::OrdinalIgnoreCase) -ge 0)
        if ($references) { $matches += $process }
        elseif ($cwd -eq '<unreadable>' -and -not (($process.ExecutablePath + "`n" + $process.CommandLine).IndexOf($release, [StringComparison]::OrdinalIgnoreCase) -ge 0)) {
            throw "Cannot determine whether Godot PID $($process.ProcessId) belongs to installed Studio."
        }
    }
    return $matches
}

function Assert-Preflight {
    Assert-NoReparsePath $script:RepoRoot
    Assert-NoReparsePath $script:ReleaseRoot
    Assert-NoReparsePath $script:ManifestPath
    Assert-NoReparsePath $script:ControllerPath
    Assert-NoReparsePath $script:SourcePath
    Assert-NoReparsePath $script:ShortcutPath
    if (-not (Test-Path -LiteralPath $script:ReleaseRoot -PathType Container)) { throw 'Installed Release root is missing.' }
    if (-not (Test-Path -LiteralPath $script:ManifestPath -PathType Leaf) -or -not (Test-Path -LiteralPath $script:ControllerPath -PathType Leaf) -or -not (Test-Path -LiteralPath $script:SourcePath -PathType Leaf)) { throw 'Required manifest or controller file is missing.' }
    if ((Get-Item -LiteralPath $script:ManifestPath).Length -ne $script:ExpectedOldManifestBytes) { throw 'Installed manifest byte length changed.' }
    if ((Get-Item -LiteralPath $script:ControllerPath).Length -ne $script:ExpectedOldControllerBytes) { throw 'Installed controller byte length changed.' }
    if ((Get-FileSha256 $script:ManifestPath) -cne $script:ExpectedOldManifestSha) { throw 'Installed manifest SHA differs from the authorized prior state.' }
    $installedSha = Get-FileSha256 $script:ControllerPath
    if ($installedSha -cne $script:ExpectedOldControllerSha) { throw 'Installed controller is altered or already updated.' }
    $source = Assert-PublishedSource
    Assert-NotAlreadyInstalled $installedSha $source.SourceSha
    $manifest = Get-Content -LiteralPath $script:ManifestPath -Raw | ConvertFrom-Json
    [void](Assert-ManifestState $manifest $installedSha)
    Assert-R04Receipt $manifest
    $otherManagedSignature = Get-OtherManagedSignature $manifest
    $launcherPath = Join-Path $script:ReleaseRoot 'scripts\launch_factory_studio.ps1'
    $projectPath = Join-Path $script:ReleaseRoot 'level_factory\project.godot'
    $iconPath = Join-Path $script:ReleaseRoot 'level_factory\assets\icons\ScrubBots_Factory_Studio.ico'
    $related = @(
        [pscustomobject]@{ Path = $launcherPath; Sha = $script:ExpectedLauncherSha }
        [pscustomobject]@{ Path = $projectPath; Sha = $script:ExpectedProjectSha }
        [pscustomobject]@{ Path = $iconPath; Sha = $script:ExpectedIconSha }
        [pscustomobject]@{ Path = $script:ShortcutPath; Sha = $script:ExpectedShortcutSha }
    )
    foreach ($item in $related) {
        if (-not (Test-Path -LiteralPath $item.Path -PathType Leaf) -or (Get-FileSha256 $item.Path) -cne $item.Sha) { throw "Unrelated launcher/project/icon/shortcut hash changed: $($item.Path)" }
    }
    $tasks = Get-Content -LiteralPath (Join-Path $script:RepoRoot 'TASKS.md') -Raw
    if ($tasks -notmatch 'STUDIO_OWNER_NORMAL_X_CLOSED_ATTESTED') { throw 'Published TASKS does not contain the recorded normal X-close attestation.' }
    $processes = @(Get-InstalledStudioProcesses)
    if ($processes.Count -ne 0) { throw 'An exact installed Factory Studio Godot process is running.' }
    if ((Test-Path -LiteralPath $script:RollbackController) -or (Test-Path -LiteralPath $script:RollbackManifest)) { throw 'A recovery path already exists; refusing to overwrite or create extra copies.' }
    if ((Test-Path -LiteralPath $script:StageController) -or (Test-Path -LiteralPath $script:StageManifest)) { throw 'A task staging path already exists; refusing to overwrite it.' }
    return [pscustomobject]@{ Head = $source.Head; SourceCommit = $source.SourceCommit; SourceSha = $source.SourceSha; InstalledSha = $installedSha; ManifestSha = $script:ExpectedOldManifestSha; ManagedCount = @($manifest.managedFiles).Count; OverlayCount = @($manifest.overlayPaths).Count; OtherManagedSignature = $otherManagedSignature }
}

function Invoke-Apply($Preflight) {
    $controllerBytes = [IO.File]::ReadAllBytes($script:ControllerPath)
    $manifestBytes = [IO.File]::ReadAllBytes($script:ManifestPath)
    $sourceBytes = [IO.File]::ReadAllBytes($script:SourcePath)
    $newManifest = Get-Content -LiteralPath $script:ManifestPath -Raw | ConvertFrom-Json
    $newManifest = New-UpdatedManifest $newManifest $Preflight.InstalledSha $Preflight.SourceSha $Preflight.SourceCommit $Preflight.Head
    $newManifestBytes = [Text.UTF8Encoding]::new($false).GetBytes((ConvertTo-Json -InputObject $newManifest -Depth 100) + "`n")
    $newManifestHash = ([BitConverter]::ToString(([Security.Cryptography.SHA256]::Create()).ComputeHash($newManifestBytes))).Replace('-', '').ToLowerInvariant()
    if ($controllerBytes.Length -ne $script:ExpectedOldControllerBytes -or $manifestBytes.Length -ne $script:ExpectedOldManifestBytes) { throw 'Target sizes changed between preflight and apply.' }
    Assert-WritePreconditions $Preflight.InstalledSha $Preflight.ManifestSha @($script:StageController)
    if ((Get-FileSha256 $script:SourcePath) -cne $Preflight.SourceSha) { throw 'Published source changed between preflight and apply.' }
    $rollbackControllerCreated = $false
    try {
        Write-CreateNew $script:StageController $sourceBytes
        Assert-WritePreconditions $Preflight.InstalledSha $Preflight.ManifestSha @($script:StageManifest)
        Write-CreateNew $script:StageManifest $newManifestBytes
        if ((Get-FileSha256 $script:StageController) -cne $Preflight.SourceSha -or (Get-FileSha256 $script:StageManifest) -cne $newManifestHash) { throw 'Staged target hash verification failed.' }
        Assert-WritePreconditions $Preflight.InstalledSha $Preflight.ManifestSha @($script:RollbackController)
        Write-CreateNew $script:RollbackController $controllerBytes
        $rollbackControllerCreated = $true
        Assert-WritePreconditions $Preflight.InstalledSha $Preflight.ManifestSha @($script:RollbackManifest)
        Write-CreateNew $script:RollbackManifest $manifestBytes
        if ((Get-FileSha256 $script:RollbackController) -cne $script:ExpectedOldControllerSha -or (Get-FileSha256 $script:RollbackManifest) -cne $script:ExpectedOldManifestSha) { throw 'Recovery copy hash verification failed.' }
        Assert-WritePreconditions $Preflight.InstalledSha $Preflight.ManifestSha @($script:StageController, $script:ControllerPath)
        Move-ReplaceFile $script:StageController $script:ControllerPath
        if ((Get-FileSha256 $script:ControllerPath) -cne $Preflight.SourceSha) { throw 'Installed controller SHA verification failed.' }
        Assert-WritePreconditions $Preflight.SourceSha $Preflight.ManifestSha @($script:StageManifest, $script:ManifestPath)
        Move-ReplaceFile $script:StageManifest $script:ManifestPath
        if ((Get-FileSha256 $script:ManifestPath) -cne $newManifestHash) { throw 'Updated manifest SHA verification failed.' }
        $installedManifest = Get-Content -LiteralPath $script:ManifestPath -Raw | ConvertFrom-Json
        [void](Assert-ManifestState $installedManifest $Preflight.SourceSha)
        if ($installedManifest.overlayReceipts.Count -ne 2 -or $installedManifest.overlayReceipts[1].sourceCommit -cne $Preflight.SourceCommit -or $installedManifest.overlayReceipts[1].controllerSha256 -cne $Preflight.SourceSha) { throw 'Appended overlay receipt verification failed.' }
        if ((Get-OtherManagedSignature $installedManifest) -cne $Preflight.OtherManagedSignature) { throw 'A non-controller managed path/SHA pair changed.' }
        "INSTALLED_CONTROLLER_HASH_VERIFIED=$($Preflight.SourceSha)"
        "MANIFEST_SHA256=$newManifestHash MANAGED_COUNT=$(@($installedManifest.managedFiles).Count) OVERLAY_RECEIPTS=$($installedManifest.overlayReceipts.Count)"
        "RECOVERY_CONTROLLER=$($script:RollbackController) BYTES=$((Get-Item -LiteralPath $script:RollbackController).Length) SHA256=$(Get-FileSha256 $script:RollbackController)"
        "RECOVERY_MANIFEST=$($script:RollbackManifest) BYTES=$((Get-Item -LiteralPath $script:RollbackManifest).Length) SHA256=$(Get-FileSha256 $script:RollbackManifest)"
    }
    catch {
        $failure = $_
        if ($rollbackControllerCreated) { throw "Apply failed; explicit guarded -Rollback is required if restoration is desired. Recovery copies are retained. Original error: $failure" }
        throw $failure
    }
}

function Invoke-Rollback {
    Assert-NoReparsePath $script:RepoRoot
    Assert-NoReparsePath $script:ReleaseRoot
    Assert-NoReparsePath $script:ControllerPath
    Assert-NoReparsePath $script:ManifestPath
    Assert-NoReparsePath $script:RollbackController
    Assert-NoReparsePath $script:RollbackManifest
    $source = Assert-PublishedSource
    if (-not (Test-Path -LiteralPath $script:RollbackController -PathType Leaf) -or -not (Test-Path -LiteralPath $script:RollbackManifest -PathType Leaf)) { throw 'Both exact R04 recovery copies are required for rollback.' }
    $controllerBackup = [IO.File]::ReadAllBytes($script:RollbackController)
    $manifestBackup = [IO.File]::ReadAllBytes($script:RollbackManifest)
    if ($controllerBackup.Length -ne $script:ExpectedOldControllerBytes -or $manifestBackup.Length -ne $script:ExpectedOldManifestBytes) { throw 'Recovery copy size differs from approved old state.' }
    if ((Get-FileSha256 $script:RollbackController) -cne $script:ExpectedOldControllerSha -or (Get-FileSha256 $script:RollbackManifest) -cne $script:ExpectedOldManifestSha) { throw 'Recovery copy SHA mismatch.' }
    $currentControllerSha = Get-FileSha256 $script:ControllerPath
    $currentManifestSha = Get-FileSha256 $script:ManifestPath
    $currentManifest = Get-Content -LiteralPath $script:ManifestPath -Raw | ConvertFrom-Json
    [void](Assert-ManifestState $currentManifest $source.SourceSha)
    if ((Get-FileSha256 $script:SourcePath) -cne $source.SourceSha) { throw 'Published controller bytes changed during rollback preflight.' }
    $receipts = @($currentManifest.overlayReceipts)
    if ($receipts.Count -ne 2 -or $receipts[0].taskId -cne 'SB-LFX-018-R05-G02-R04' -or $receipts[0].controllerSha256 -cne $script:ExpectedOldControllerSha -or $receipts[1].taskId -cne $script:TaskId -or $receipts[1].sourceCommit -cne $source.SourceCommit -or $receipts[1].sourceHead -cne $source.Head -or $receipts[1].controllerSha256 -cne $source.SourceSha) { throw 'The installed R04/M01 receipt chain does not match the published source.' }
    if ($currentControllerSha -cne $source.SourceSha) { throw 'Current installed controller differs from the published M01 source.' }
    $processes = @(Get-InstalledStudioProcesses)
    if ($processes.Count -ne 0) { throw 'Installed Factory Studio is running; rollback is prohibited.' }
    if ((Test-Path -LiteralPath $script:StageController) -or (Test-Path -LiteralPath $script:StageManifest)) { throw 'A staging file already exists; refusing rollback writes.' }
    Restore-Previous $controllerBackup $manifestBackup $currentControllerSha $currentManifestSha
    'ROLLBACK_RESTORED_OLD_CONTROLLER_AND_MANIFEST_HASHES_VERIFIED'
}

if ($Apply -and $Rollback) { throw 'Choose either -Apply or -Rollback, not both.' }
if ($MyInvocation.InvocationName -eq '.') { return }
try {
    if ($Rollback) {
        Invoke-Rollback
    }
    else {
        $preflight = Assert-Preflight
        "PREFLIGHT_OK MODE=$(if ($Apply) {'APPLY'} else {'READ_ONLY'}) HEAD=$($preflight.Head) SOURCE_COMMIT=$($preflight.SourceCommit) SOURCE_SHA=$($preflight.SourceSha) INSTALLED_SHA=$($preflight.InstalledSha) MANAGED_COUNT=$($preflight.ManagedCount) OVERLAY_COUNT=$($preflight.OverlayCount)"
        if ($Apply) { Invoke-Apply $preflight }
    }
}
catch {
    Write-Error "INSTALL BLOCKED: $_"
    exit 2
}
