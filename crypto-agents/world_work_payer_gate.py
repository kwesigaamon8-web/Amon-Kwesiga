"""BTC-mainnet payment proof gate for accepted B1/B2 customer work.

No credentials, wallet signing or outbound messages; two public explorers
must agree on the same tx's confirmed outputs and payer's own public comment
must identify the transfer as settlement of the accepted deliverable.
A deposit without payer/work provenance is NOT earned revenue.
"""
from __future__ import annotations
import json, re, sys, urllib.parse, urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from btc_receiver_safety import require_approved_receiver

BTC_RECEIVERS={
    "B1":("transferexperiment","bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"),
    "B2":("BountyScoutAI","bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"),
}
EXPLORERS=("https://mempool.space/api/tx/","https://blockstream.info/api/tx/")
TXID=re.compile(r"^[a-fA-F0-9]{64}$")
GITHUB_ISSUE=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9]\d*)$")
GITHUB_COMMENT=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9]\d*)#issuecomment-([1-9]\d*)$")

def check_http_json(url):
    x=urllib.parse.urlsplit(url)
    if x.scheme!="https" or x.hostname not in ("mempool.space","blockstream.info","api.github.com") or x.username or x.password:
        raise ValueError("UNAPPROVED_PUBLIC_EVIDENCE_SOURCE")
    h={"User-Agent":"B1B2-Payer-ReadOnly-Proof/1.0","Accept":"application/json"}
    with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=14) as r:
        raw=r.read(1_200_001)
        if len(raw)>1_200_000:raise ValueError("EVIDENCE_EXCEEDS_LIMIT")
    return json.loads(raw)

def verify_issuer_agreement(terms,request=check_http_json):
    """Fetch actual original issue + issuer's acceptance comment, not a text flag."""
    if not isinstance(terms,dict):raise ValueError("INVALID_TERMS")
    issue_link=str(terms.get("original_issue_url") or "")
    match=GITHUB_ISSUE.fullmatch(issue_link)
    if not match:raise ValueError("MISSING_ORIGINAL_GITHUB_ISSUE")
    cm=GITHUB_COMMENT.fullmatch(str(terms.get("sponsor_acceptance_comment_url") or ""))
    if not cm or cm.groups()[:3]!=match.groups():
        raise ValueError("SPONSOR_ACCEPTANCE_NOT_IN_ORIGINAL_ISSUE")
    org,repo,number=match.groups()
    issue=request(f"https://api.github.com/repos/{org}/{repo}/issues/{number}")
    comment=request(f"https://api.github.com/repos/{org}/{repo}/issues/comments/{cm.group(4)}")
    if not isinstance(issue,dict) or not isinstance(comment,dict):
        raise ValueError("ISSUER_EVIDENCE_UNAVAILABLE")
    issuer=str((issue.get("user") or {}).get("login") or "")
    author=str((comment.get("user") or {}).get("login") or "")
    association=str(comment.get("author_association") or "")
    if not issuer or (author!=issuer and association not in ("OWNER","MEMBER","COLLABORATOR")):
        raise ValueError("SPONSOR_COMMENT_NOT_BY_AUTHORIZED_ISSUER")
    body=str(comment.get("body") or "")
    deliverable=str(terms.get("accepted_deliverable_url") or "")
    if not deliverable.startswith("https://github.com/") or deliverable not in body:
        raise ValueError("SPONSOR_DID_NOT_REFERENCE_DELIVERABLE")
    if not re.search(r"(?i)\b(accepted|approved|merged|completed and approved)\b",body):
        raise ValueError("SPONSOR_HAS_NOT_APPROVED_RESULT")
    sats=terms.get("agreed_sats")
    if type(sats) is not int or sats<=0:
        raise ValueError("NO_AGREED_SATOSHI_AMOUNT")
    if str(sats) not in body or not re.search(r"(?i)(?:bitcoin|btc)\s*(?:mainnet)?|mainnet\s*bitcoin",body):
        raise ValueError("PAYER_DID_NOT_CONFIRM_AMOUNT_AND_NATIVE_BTC")
    if not terms.get("payer_identity") or terms["payer_identity"]!=author:
        raise ValueError("PAYER_IDENTITY_NOT_VERIFIED")
    return {"sponsor":author,"association":association,
            "accepted_deliverable_url":deliverable,
            "sponsor_acceptance_comment_url":comment.get("html_url") or cm.group(0),
            "agreed_sats":sats,"native_btc_payout_terms_independently_seen":True}

def make_request(terms,fleet,request=check_http_json):
    if fleet not in BTC_RECEIVERS:raise ValueError("UNKNOWN_FLEET")
    proof=verify_issuer_agreement(terms,request)
    name,addr=BTC_RECEIVERS[fleet]
    require_approved_receiver(name,addr)
    body=(f"Thank you for accepting the work at {proof['accepted_deliverable_url']}. "
          f"As agreed in {proof['sponsor_acceptance_comment_url']}, "
          f"please pay {proof['agreed_sats']} satoshis as native Bitcoin mainnet "
          f"to {addr} and share the confirmed transaction ID. "
          "This is a Bitcoin mainnet address, not a Lightning, Stacks sBTC or testnet destination.")
    return {"request_text_ready_not_sent":body,"address":addr,
            "fleet":fleet,"network":"bitcoin-mainnet",
            "accepted_source":proof,"public_comment_posted":False,
            "payment_sent_or_verified":False}

def inspect_tx(txid,fleet,agreed_sats,issuer_txid_confirmation,request=check_http_json):
    """Two-explorer tx proof + issuer's independently checked exact TXID statement.

    issuer_txid_confirmation must already be from the same issuer verified in
    verify_issuer_agreement. Never infer buyer or earned income from receipt alone.
    """
    if not isinstance(txid,str) or not TXID.fullmatch(txid):
        raise ValueError("NO_VALID_NATIVE_BTC_TXID")
    if fleet not in BTC_RECEIVERS or type(agreed_sats) is not int or agreed_sats<=0:
        raise ValueError("INVALID_PAYMENT_CONTEXT")
    name,address=BTC_RECEIVERS[fleet]
    require_approved_receiver(name,address)
    if not isinstance(issuer_txid_confirmation,dict) or (
        issuer_txid_confirmation.get("payer_authenticated_in_original_task") is not True
        or issuer_txid_confirmation.get("txid")!=txid
        or issuer_txid_confirmation.get("accepted_work_sha256") is None
        or issuer_txid_confirmation.get("confirmed_payment_purpose") is not True
    ):
        raise ValueError("UNPROVEN_PAYER_WORK_TX_RELATIONSHIP")
    checked=[]
    for origin in EXPLORERS:
        tx=request(origin+txid)
        if not isinstance(tx,dict) or tx.get("txid")!=txid:
            raise ValueError("EXPLORER_TX_HASH_MISMATCH")
        status=tx.get("status") or {}
        if status.get("confirmed") is not True or type(status.get("block_height")) is not int:
            raise ValueError("UNCONFIRMED_TRANSACTION_NOT_PAID")
        outputs=tx.get("vout")
        if not isinstance(outputs,list):raise ValueError("INVALID_TX_OUTPUTS")
        value=sum(o.get("value",0) for o in outputs if isinstance(o,dict)
                  and o.get("scriptpubkey_address")==address and type(o.get("value")) is int and o["value"]>0)
        if value<agreed_sats:raise ValueError("INSUFFICIENT_SATS_AT_APPROVED_ADDRESS")
        checked.append({"explorer":urllib.parse.urlsplit(origin).hostname,
                        "output_sats":value,"block_height":status["block_height"]})
    if checked[0]["output_sats"]!=checked[1]["output_sats"] or checked[0]["block_height"]!=checked[1]["block_height"]:
        raise ValueError("INDEPENDENT_EXPLORERS_DISAGREE")
    return {"native_bitcoin_received_observed":True,"payer_work_relation_supplied_and_requires_authentic_source":True,
            "confirmed_in_two_independent_explorers":True,
            "txid":txid,"fleet":fleet,"confirmed_sats":checked[0]["output_sats"],
            "outputs":checked,"has_private_key_or_wallet_signing":False}

def verify_earned_job(terms, fleet, txid, issuer_payment_comment_url, request=check_http_json):
    """Only full chain: independent original sponsor approval, payer TXID statement, dual blockchain outputs."""
    accepted=verify_issuer_agreement(terms,request)
    original=GITHUB_ISSUE.fullmatch(terms["original_issue_url"])
    payment=GITHUB_COMMENT.fullmatch(str(issuer_payment_comment_url or ""))
    if not original or not payment or payment.groups()[:3]!=original.groups():
        raise ValueError("PAYMENT_CONFIRMATION_NOT_IN_ORIGINAL_TASK")
    org,repo,issue=original.groups()
    note=request(f"https://api.github.com/repos/{org}/{repo}/issues/comments/{payment.group(4)}")
    if not isinstance(note,dict) or str((note.get("user") or {}).get("login") or "")!=accepted["sponsor"]:
        raise ValueError("PAYMENT_CONFIRMATION_NOT_BY_SPONSOR")
    content=str(note.get("body") or "")
    if txid not in content or terms["accepted_deliverable_url"] not in content:
        raise ValueError("SPONSOR_PAYMENT_PROOF_MISSING_TXID_AND_ACCEPTED_WORK")
    if not __import__("re").search(r"(?i)\b(paid|settled|payment\s+(?:sent|made))\b",content):
        raise ValueError("SPONSOR_DID_NOT_CONFIRM_PAYMENT")
    support={"payer_authenticated_in_original_task":True,
             "txid":txid,"accepted_work_sha256":__import__("hashlib").sha256(
                 terms["accepted_deliverable_url"].encode()).hexdigest(),
             "confirmed_payment_purpose":True}
    output=inspect_tx(txid,fleet,accepted["agreed_sats"],support,request)
    output["sponsor_acceptance_evidence"]=terms["sponsor_acceptance_comment_url"]
    output["sponsor_payment_evidence"]=issuer_payment_comment_url
    output["earned_payment_supported_by_sponsor_and_two_explorers"]=True
    return output


def self_test():
    assert len(TXID.pattern)>0
    terms={"original_issue_url":"https://github.com/real/owner/issues/7",
           "sponsor_acceptance_comment_url":"https://github.com/real/owner/issues/7#issuecomment-88",
           "accepted_deliverable_url":"https://github.com/real/owner/pull/8",
           "agreed_sats":1200,"payer_identity":"original-issuer"}
    def fake(url):
        if url.endswith("/issues/7"):return {"user":{"login":"original-issuer"}}
        if url.endswith("/issues/comments/88"):
            return {"user":{"login":"original-issuer"},"author_association":"OWNER",
                    "body":"Accepted https://github.com/real/owner/pull/8; approved 1200 sats Bitcoin mainnet.",
                    "html_url":terms["sponsor_acceptance_comment_url"]}
        raise ValueError("Unexpected URL")
    msg=make_request(terms,"B1",fake)
    assert msg["public_comment_posted"] is False and msg["payment_sent_or_verified"] is False
    assert BTC_RECEIVERS["B1"][1] in msg["request_text_ready_not_sent"]
    def fail(fn):
        try:fn()
        except ValueError:return
        raise AssertionError("Unsafe action falsely accepted")
    fail(lambda: make_request(terms|{"agreed_sats":0},"B1",fake))
    fail(lambda: make_request(terms|{"payer_identity":"wrong"},"B1",fake))
    fail(lambda: make_request(terms|{"sponsor_acceptance_comment_url":
        "https://github.com/other/org/issues/7#issuecomment-88"},"B1",fake))
    txid="a"*64
    def txgood(url):
        return {"txid":txid,"status":{"confirmed":True,"block_height":976000},
                "vout":[{"scriptpubkey_address":BTC_RECEIVERS["B2"][1],"value":1300}]}
    source={"payer_authenticated_in_original_task":True,"txid":txid,
            "accepted_work_sha256":"hash-placeholder","confirmed_payment_purpose":True}
    verified=inspect_tx(txid,"B2",1200,source,txgood)
    def proof_api(url):
        if url.endswith("/issues/7") or url.endswith("/issues/comments/88"):
            return fake(url)
        if url.endswith("/issues/comments/99"):
            return {"user":{"login":"original-issuer"},
                    "body":"Paid Bitcoin mainnet txid "+txid+" for https://github.com/real/owner/pull/8"}
        if url.startswith("https://mempool.space/api/tx/") or url.startswith("https://blockstream.info/api/tx/"):
            return txgood(url)
        raise ValueError("Unexpected test source")
    independent=verify_earned_job(terms,"B2",txid,
        "https://github.com/real/owner/issues/7#issuecomment-99",proof_api)
    assert independent["earned_payment_supported_by_sponsor_and_two_explorers"]
    fail(lambda: verify_earned_job(terms,"B2",txid,
        "https://github.com/another/repo/issues/7#issuecomment-99",proof_api))
    assert verified["confirmed_sats"]==1300
    fail(lambda: inspect_tx(txid,"B2",1200,{},txgood))
    fail(lambda: inspect_tx(txid,"B1",1200,source,txgood))
    fail(lambda: inspect_tx(txid,"B2",1200,source,lambda url:{"txid":txid,
         "status":{"confirmed":False},"vout":[{"scriptpubkey_address":BTC_RECEIVERS["B2"][1],"value":1300}]}))
    fail(lambda: inspect_tx("not-a-txid","B2",1200,source,txgood))
    print("B1B2_TWO_EXPLORER_PAYER_PAYMENT_PROOF_TESTS_PASS")

def cli_main():
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser(description="Only read verified issuer evidence and create an unsent B1/B2 BTC request or verify payer-linked TXID")
    group=p.add_mutually_exclusive_group()
    group.add_argument("--prepare-request",metavar="TASK_JSON")
    group.add_argument("--verify-transaction",metavar="TASK_JSON")
    p.add_argument("--fleet",choices=("B1","B2"))
    p.add_argument("--txid")
    p.add_argument("--sponsor-payment-comment")
    a=p.parse_args()
    self_test()
    task_path=a.prepare_request or a.verify_transaction
    if task_path is None:
        return
    if not a.fleet:
        p.error("--fleet B1/B2 required")
    # Path allowlist makes user-file input explicit and avoids accidentally
    # reading private content elsewhere on the runner.
    root=(HERE/"world-work-factory"/"accepted-jobs").resolve()
    path=Path(task_path).resolve()
    if root not in path.parents or path.suffix.lower()!=".json":
        raise ValueError("ACCEPTED_TASK_EVIDENCE_OUTSIDE_PUBLIC_ALLOWLIST")
    if not path.is_file():raise ValueError("ACCEPTED_TASK_EVIDENCE_NOT_FOUND")
    terms=json.loads(path.read_text(encoding="utf-8"))
    if a.prepare_request:
        report=make_request(terms,a.fleet)
        label="B1B2_ACCEPTED_SPONSOR_PAYMENT_REQUEST_READY_NOT_SENT"
    else:
        if not a.txid or not a.sponsor_payment_comment:
            p.error("Transaction verification requires --txid and --sponsor-payment-comment")
        report=verify_earned_job(terms,a.fleet,a.txid,a.sponsor_payment_comment)
        label="B1B2_SPONSOR_LINKED_TWO_EXPLORER_BTC_PAYMENT_VERIFIED"
    out=HERE/"world-work-factory"/"payment-evidence"
    out.mkdir(parents=True,exist_ok=True)
    suffix="request" if a.prepare_request else "verified-receipt"
    dest=out/(path.stem+"-"+a.fleet+"-"+suffix+".json")
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(label+" "+json.dumps({"evidence_file":str(dest),"source_task":str(path),
          "network":"bitcoin-mainnet",
          "payment_verified":bool(report.get("earned_payment_supported_by_sponsor_and_two_explorers")),
          "message_sent":False}))


if __name__=="__main__":
    cli_main()
