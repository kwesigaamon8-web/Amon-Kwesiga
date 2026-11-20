# Enigma Moltbook onboarding for 14 existing GitHub AI workers.
# Moltbook verification requires a distinct eligible human X account for each bot.
# All API keys stay on your Windows PC; no email is sent; no credentials enter GitHub.
[CmdletBinding(DefaultParameterSetName='Single')]
param(
    [Parameter(ParameterSetName='Single',Mandatory=$true)]
    [ValidatePattern('^G0[1-7][AB]$')]
    [string]$Agent,
    [Parameter(ParameterSetName='All',Mandatory=$true)]
    [switch]$All,
    [Parameter(ParameterSetName='List',Mandatory=$true)]
    [switch]$List
)
$ErrorActionPreference='Stop'
$root=Join-Path $HOME '.config\moltbook'
$mapPath=Join-Path $root 'enigma-claim-x-map.json'
$identities=@()
foreach($n in 1..7){
    $slot='G{0:00}' -f $n
    foreach($letter in @('A','B')){ $identities+=($slot+$letter) }
}
# The claim and API key files come from individual audited local registration
# scripts register_enigma_g01_claim.ps1 through register_enigma_g07_claim.ps1.
function Get-LocalFile([string]$id) {
    $slot=$id.Substring(0,3).ToLowerInvariant()
    $letter=$id.Substring(3,1)
    return Join-Path (Join-Path $root ('enigma-'+$slot)) ('agent-'+$letter+'.json')
}
function Secure-LocalFile([string]$file){
    if($env:OS -eq 'Windows_NT'){
        $sid=([System.Security.Principal.WindowsIdentity]::GetCurrent()).User.Value
        & icacls.exe $file /inheritance:r /grant:r ('*'+$sid+':(F)') '*S-1-5-18:(F)' | Out-Null
        if($LASTEXITCODE -ne 0){throw 'Cannot secure local state file permissions'}
    }
}
if($List){
    Write-Output 'These claim URLs exist ONLY on this computer. No API keys displayed.'
    foreach($id in $identities){
        $file=Get-LocalFile $id
        if(Test-Path -LiteralPath $file){
            try{
                $record=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json
                if($record.claim_url -match '^https://www\.moltbook\.com/claim/'){
                    Write-Output ($id+' | '+$record.agent_name+' | '+$record.claim_url)
                } else { Write-Output ($id+' | NEEDS HUMAN REVIEW OF SAVED DATA') }
            } catch { Write-Output ($id+' | CANNOT READ SAVED REGISTRATION') }
        } else { Write-Output ($id+' | NOT YET REGISTERED') }
    }
    exit 0
}
$planned=if($All){$identities}else{@($Agent)}
$used=@{}
if(Test-Path -LiteralPath $mapPath){
    try{
        $index=Get-Content -LiteralPath $mapPath -Raw|ConvertFrom-Json
        foreach($item in $index){
            if($item.x_handle -and $item.agent_id){
                $used[$item.x_handle.ToLowerInvariant()]=$item.agent_id
            }
        }
    } catch {throw 'Cannot safely read existing unique X-account map; review local state before continuing.'}
}
$added=@()
foreach($id in $planned){
    $slot=$id.Substring(0,3)
    $which=$id.Substring(3,1)
    $file=Get-LocalFile $id
    $helper=Join-Path $PSScriptRoot ('register_enigma_'+$slot.ToLowerInvariant()+'_claim.ps1')
    if(-not(Test-Path -LiteralPath $helper)){throw ('Missing secure local helper '+$helper)}
    if(Test-Path -LiteralPath $file){
        $old=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json
        if($old.claim_url -match '^https://www\.moltbook\.com/claim/'){
            Write-Output ($id+' already registered; human-approval URL: '+$old.claim_url)
            continue
        }
        throw ('Existing credential for '+$id+' is malformed. Stopping without overwrite.')
    }
    Write-Output ('Next agent '+$id+'. Moltbook only allows ONE verified bot per X account.')
    $reply=Read-Host 'Do you have an eligible distinct X account for this agent? Type YES to continue'
    if($reply -cne 'YES'){
        Write-Output ($id+' skipped; no Moltbook registration attempted')
        continue
    }
    $handle=(Read-Host 'Enter the unique X handle for your manual claim (without @)').Trim().TrimStart('@')
    if($handle -notmatch '^[a-zA-Z0-9_]{1,15}$'){
        Write-Output ($id+' skipped: X handle format invalid')
        continue
    }
    $lower=$handle.ToLowerInvariant()
    if($used.ContainsKey($lower)){
        Write-Output ($id+' skipped: X handle already allocated to '+$used[$lower])
        continue
    }
    Write-Output ('Calling Moltbook registration for '+$id+'. No emails will be sent.')
    # A separate secure helper saves the one-time API key before showing URL.
    try{
        & $helper -Agent $which
        if(-not(Test-Path -LiteralPath $file)){throw 'Registration response not safely saved'}
        $result=Get-Content -LiteralPath $file -Raw|ConvertFrom-Json
        if($result.claim_url -notmatch '^https://www\.moltbook\.com/claim/'){
            throw 'Could not verify expected claim URL'
        }
        $used[$lower]=$id
        $added+=@{agent_id=$id;x_handle=$lower}
        Write-Output ($id+' HUMAN APPROVAL: '+$result.claim_url)
    } catch {
        Write-Warning ($id+' registration NOT VERIFIED: '+$_.Exception.Message)
        Write-Warning 'Stop/review any partial registration before retrying to avoid orphaned keys.'
        break
    }
}
if($added.Count -gt 0){
    $entries=@()
    foreach($handle in ($used.Keys|Sort-Object)){
        $entries+=@{agent_id=$used[$handle];x_handle=$handle}
    }
    New-Item -ItemType Directory -Path $root -Force|Out-Null
    $entries|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $mapPath -Encoding UTF8
    Secure-LocalFile $mapPath
}
Write-Output 'To show saved official human claim links again:'
Write-Output ('.\crypto-agents\register_all_enigma_claims.ps1 -List')
Write-Output 'After approval, store each API key using GitHub Actions repository Secrets, never in a Git commit or chat.'
Write-Output 'These Google account aliases are NOT extra verified X identities. Registration is subject to Moltbook acceptance and claim rules.'
