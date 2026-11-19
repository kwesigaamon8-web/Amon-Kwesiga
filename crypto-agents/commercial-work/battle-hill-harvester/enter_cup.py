"""Create ONE battle.training account, register an original bot, and enter the free Base-USDC cup.

IMPORTANT: Run once only. Never log account keys/claim URLs or commit plaintext credentials.
Requires local RSA public key below; matching RSA PRIVATE key is held by the owner separately.
"""
import base64,json,pathlib,time,urllib.request,urllib.error
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding

BASE="https://api.battle.training"
ROOT=pathlib.Path("crypto-agents/commercial-work/battle-hill-harvester")
H="b1b2chiefd26"
BOT="b1b2-hill-harvester"
USDC_BASE="0x734989a439F146885C12907cd9Dd191b03d5B07e"
PUBLIC_PEM=b"""-----BEGIN PUBLIC KEY-----
MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAyy0b4rm9VUh+AEsS+dCr
4lsR11ctVGFpO0SVfJrtElmzgfQyIP4p9kzKxYNwzX7nR5a/nUVQakOYe7cg+7xu
S68mH1StyNB50ZdfUbUA9u3u0+AYRgCtt/4MLbJs6rqJTv951IprlbRYjwBPk8Oj
5yeouviW6/vXyMh/8fU0jJiC0ZVtJG+YHPjU0Ty22TZQWEaFRry6hRp08I66zLbh
onHnAglAPUPlbHxVVI3/wpLNNzUIQQYUY84fBuNmliZIsItK1kEZo7viNF7kOKlI
Jiq3fbCGtZ2NW/U2ssaIBq+Nqr6s2LQ4+4cuabXE0qBSe2C1HrCL9AYpCzsZ76X2
PDh0NP3BEkZOwT8foZlC7dJsCv5pBSc+LIsjCou4mZvvAPCGuM9TLHq26LGEzSw9
Ua8j3a2JwtYcPTmYSxWhjO2EqBzr1/RWgA8MAwAnxi8EW8I4zC+MnjfEWZPLFK4k
3dga8YKlfnRMzOhSzmxx9i9npmEwoIcbeXBrDIFxY9hHAgMBAAE=
-----END PUBLIC KEY-----
"""

def request(method,path,payload=None,key=None):
    body=None if payload is None else json.dumps(payload).encode()
    headers={"User-Agent":"B1B2-FreeOriginalCupBot/1.0","Accept":"application/json"}
    if body is not None:headers["Content-Type"]="application/json"
    if key:headers["Authorization"]="Bearer "+key
    req=urllib.request.Request(BASE+path,data=body,method=method,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            content=response.read(100000).decode("utf-8","replace")
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        # No server body: sensitive authentication details may be echoed there.
        raise RuntimeError("API_HTTP_"+str(e.code)+" at "+path.split("?")[0])
def secret_payload(account):
    public=serialization.load_pem_public_key(PUBLIC_PEM)
    secret=Fernet.generate_key()
    ciphertext=Fernet(secret).encrypt(json.dumps(account).encode())
    wrapped=public.encrypt(secret,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    result={"algorithm":"RSA-3072-OAEP-SHA256 + Fernet-AES128-HMAC","protected_fields":"Original account JSON including account key and claim URL. NEVER publish the private key.","wrapped_key_b64":base64.b64encode(wrapped).decode(),"ciphertext_b64":base64.b64encode(ciphertext).decode(),"bot":BOT,"payout_network":"Base","payout_address":USDC_BASE}
    (ROOT/"account-encrypted.json").write_text(json.dumps(result,indent=2)+"\n")
def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    report={"checked_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"handle":H,"bot":BOT,"contest":"promotedby-cup-nov-2026","payout_network":"Base USDC","payout_address":USDC_BASE,"registered":False,"payout_set":False,"bot_created":False,"version_uploaded":False,"enrolled":False,"prize_earned":False,"received_on_chain":False,"error":None}
    key=None
    try:
        if (ROOT/"account-encrypted.json").exists():
            raise RuntimeError("EXISTING_ENCRYPTED_ACCOUNT_ABORT_TO_PREVENT_DUPLICATE")
        tests=ROOT/"test-results.json"
        if not tests.exists():
            raise RuntimeError("OFFICIAL_LOCAL_TEST_EVIDENCE_NOT_READY")
        evidence=json.loads(tests.read_text())
        if "replays verified 24/24" not in evidence.get("log","") or "tick errors 0" not in evidence.get("log",""):
            raise RuntimeError("LOCAL_TEST_FAILURE_OR_INCOMPLETE")
        if not (ROOT/"controller.js").exists():
            raise RuntimeError("NO_ORIGINAL_CONTROLLER")
        account=request("POST","/api/accounts",{"handle":H})
        if not isinstance(account,dict):
            raise RuntimeError("UNEXPECTED_ACCOUNT_RESPONSE")
        secret_payload(account) # Save credential encrypted BEFORE performing follow-up actions.
        data=account.get("data",account)
        key=data.get("key") or data.get("api_key") or data.get("account_key") or data.get("token")
        report["registered"]=True
        if not isinstance(key,str) or len(key)<12:
            raise RuntimeError("ACCOUNT_KEY_PATH_UNKNOWN_REQUIRES_PRIVATE_DECRYPTION")
        payout=request("PUT","/api/me/payout",{"address":USDC_BASE},key)
        report["payout_set"]=True
        created=request("POST","/api/bots",{"name":BOT,"agent":"chatgpt","model":"gpt-6"},key)
        report["bot_created"]=True
        source=(ROOT/"controller.js").read_text()
        upload=request("POST","/api/bots/"+BOT+"/versions",{"label":"v1-hill-harvester","source":source,"notes":"Original controller: APC objective multiplier, escort MBT, smoke engineer, second objective scout. Official local simulation: 13-11, 24/24 verified."},key)
        report["version_uploaded"]=True
        enter=request("POST","/api/ladders/promotedby-cup-nov-2026/enrol",{"bot":BOT},key)
        report["enrolled"]=True
        report["public_bot_page"]="https://battle.training/bots/"+BOT
        report["public_cup_page"]="https://battle.training/cup/promotedby-cup-nov-2026"
        # Public verify account state; do not leak accidental API token in returned object.
        proof=request("GET","/api/me",key=key)
        s=json.dumps(proof).lower()
        report["payout_address_seen_in_private_account"]=USDC_BASE.lower() in s
        report["bot_seen_in_private_account"]=BOT.lower() in s
    except Exception as err:
        report["error"]=str(err)[:220]
    finally:
        (ROOT/"entry-status.json").write_text(json.dumps(report,indent=2)+"\n")
        print("CUP_NO_COST_ENTRY_STATUS",json.dumps(report))
if __name__=="__main__":main()
