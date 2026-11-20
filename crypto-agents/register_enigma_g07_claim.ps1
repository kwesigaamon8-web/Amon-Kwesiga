# Enigma G07 — obtain official Moltbook claim links, ONE agent per invocation.
# Runs locally on your Windows PC; never sends email, never uploads secrets to GitHub.
[CmdletBinding()]
param([Parameter(Mandatory=$true)]
      [ValidateSet('A','B')][string]$Agent)
$ErrorActionPreference='Stop'
$catalog=@{
  A=@{Name='EnigmaG07BTCVerifier'; Description='Evidence-first public-interest software country research by Enigma AI agent.'}
  B=@{Name='EnigmaG07MiningLab'; Description='Tested original helpful software and buyer-approved custom projects by Enigma AI agent.'}
}
$agentSpec=$catalog[$Agent]
$folder=Join-Path $HOME '.config\moltbook\enigma-g07'
$secretFile=Join-Path $folder ('agent-'+$Agent+'.json')
if(Test-Path -LiteralPath $secretFile){
    $old=Get-Content -LiteralPath $secretFile -Raw | ConvertFrom-Json
    if($old.agent_name -eq $agentSpec.Name -and $old.claim_url -match '^https://www\.moltbook\.com/claim/'){
        Write-Output ('Existing human-approval link for agent '+$Agent+': '+$old.claim_url)
        Write-Output ('Local secret retained at '+$secretFile)
        exit 0
    }
    throw 'Credential file already exists but does not match this agent. Stopping to avoid overwriting secrets.'
}
# Moltbook's official registration endpoint. Owner alone handles email / X approval.
$payload=@{ name=$agentSpec.Name; description=$agentSpec.Description } | ConvertTo-Json -Compress
try {
    $registration=Invoke-RestMethod -Uri 'https://www.moltbook.com/api/v1/agents/register' -Method POST -ContentType 'application/json' -Body $payload -TimeoutSec 25
} catch {
    throw 'Official registration failed or was rejected. Review the Moltbook account rules. No claim link was generated.'
}
$a=$registration.agent
if(-not $a -or -not $a.api_key -or -not $a.claim_url){throw 'Moltbook did not return the API key AND claim URL. Cannot safely finish registration.'}
if([string]$a.claim_url -notmatch '^https://www\.moltbook\.com/claim/[a-zA-Z0-9_-]+$'){throw 'Claim URL is not an expected official Moltbook URL.'}
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$record=@{
  agent_name=$agentSpec.Name
  api_key=[string]$a.api_key
  claim_url=[string]$a.claim_url
  verification_code=[string]$a.verification_code
  registered_at_utc=[DateTime]::UtcNow.ToString('o')
}
try {
    $record | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $secretFile -Encoding UTF8 -NoNewline
    # Harden the secret file on Windows to the logged-in user and SYSTEM.
    if($env:OS -eq 'Windows_NT'){
        $sid=([System.Security.Principal.WindowsIdentity]::GetCurrent()).User.Value
        & icacls.exe $secretFile /inheritance:r /grant:r ('*'+$sid+':(F)') '*S-1-5-18:(F)' | Out-Null
        if($LASTEXITCODE -ne 0){throw 'Credential ACL could not be restricted'}
    }
} catch {
    throw 'Could not safely store credentials. Rotate the generated key via the official owner dashboard if a claim was made.'
}
Write-Output ('Agent '+$Agent+' claim link: '+$a.claim_url)
Write-Output ('API key saved ONLY in local file: '+$secretFile)
Write-Output 'You must complete Moltbook email + X verification yourself. One verified bot per X account.'
