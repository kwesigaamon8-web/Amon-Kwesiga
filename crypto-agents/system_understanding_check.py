"""Verify that an ACTUALLY running B worker can explain the system.

This creates NO model processes, child agents, external posts, customers or
payments on its own. Passing a short model-answer quiz is evidence of a
correct response, not proof of deep comprehension or real-world compliance.
"""
from __future__ import annotations
import re

COMPANY_BTC={
    "transferexperiment":"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
    "BountyScoutAI":"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
}
OWNER_ORDER="OWNER-20261114-151242"
STRUCTURE=(
    "Human OWNER alone sets the goal; one Chief D coordinates the TWO "
    "separate companies B1=transferexperiment and B2=BountyScoutAI, "
    "each with TEN local directors D01-D10. Each director has two "
    "advisory assistants and 15 manager roles. Each manager has 50 W worker "
    "roles; each W has 150 S; each S has 500 G; each G has 666 H. "
    "H has no defined internal child. Assistants are not mandatory parent "
    "levels. A worker reports to ONE exact immediate parent. "
    "Recruiters give every ACTUALLY activated recruit the same legal "
    "crypto-earning order, a distinct task, a correct company wallet, and "
    "the instruction to pass the mission to further actually activated "
    "children. Other AI operators remain independent and join only by "
    "consent using permitted authenticated accounts. "
    "Seven billion addressable H identities are not seven billion live models. "
    "Genuine success requires a real customer and original useful work, "
    "authorized submission, customer acceptance and a confirmed correct "
    "network incoming transaction. A source link, draft, pledge or role "
    "definition is NOT received cryptocurrency."
)

def grade_answer(answer, company, role, parent, address):
    """Deterministic and conservative check of independently generated text."""
    if company not in COMPANY_BTC or address!=COMPANY_BTC[company]:
        raise ValueError("Company wallet mismatch in system quiz")
    t=str(answer or "").strip()
    lines={}
    for tag in ("CHAIN","PARENT","RECRUIT","WALLET","PROOF"):
        m=re.search(r"(?im)^\s*"+tag+r"\s*:\s*(.+)$",t)
        lines[tag]=m.group(1).strip() if m else ""
    chain=lines["CHAIN"].lower()
    recruit=lines["RECRUIT"].lower()
    payment=lines["WALLET"].lower()
    proof=lines["PROOF"].lower()
    checks={
        "correct_two_company_hierarchy":("chief d" in chain or "chief_d" in chain)
            and ("owner" in chain) and ("b1" in chain or "transferexperiment" in chain)
            and ("b2" in chain or "bountyscoutai" in chain),
        "own_direct_parent":bool(parent) and lines["PARENT"].strip()==parent,
        "recruit_chain_and_true_activation":("recruit" in recruit or "child" in recruit)
            and ("activ" in recruit or "live" in recruit or "run" in recruit)
            and ("pass" in recruit or "teach" in recruit or "instruct" in recruit)
            and ("7b" in recruit or "billion" in recruit or "dormant" in recruit or "defined" in recruit),
        "correct_company_wallet_and_network":company.lower() in payment
            and address in lines["WALLET"]
            and ("btc" in payment or "bitcoin" in payment)
            and "mainnet" in payment
            and COMPANY_BTC["BountyScoutAI" if company=="transferexperiment" else "transferexperiment"] not in lines["WALLET"],
        "actual_money_not_promises":("buyer" in proof or "client" in proof or "payer" in proof)
            and ("accept" in proof or "contract" in proof)
            and ("txid" in proof or "transaction" in proof or "on-chain" in proof)
            and ("not" in proof or "only" in proof or "verified" in proof or "proof" in proof),
        "all_required_lines":all(len(v)>=12 for v in lines.values()),
    }
    return {"checks":checks,"passed":all(checks.values()),"answer":t[:2000],
        "company":company,"role":role,"parent":parent,
        "schema":"B_REAL_SYSTEM_COMPREHENSION_V1",
        "no_external_payment_proven":True,
        "real_model_execution_not_inferred_from_answer":True}

def teach_and_check(model, company, role, parent, address):
    if company not in COMPANY_BTC or address!=COMPANY_BTC[company]:
        raise ValueError("Company payment route mismatch")
    result={"schema":"B_REAL_SYSTEM_COMPREHENSION_V1",
        "owner_order_id":OWNER_ORDER,"company":company,"worker_id":role,
        "direct_parent":parent,"lesson_assigned":True,
        "model_execution":"NOT_RUN","answer":"","grade":None,
        "assessment":"NOT_RUN","actual_understanding_guaranteed":False,
        "correct_chain_payment_verified":False,
        "external_agent_recruited":False}
    if model is None:return result
    question=(
        "You are "+company+"/"+role+"; your exact immediate parent is "
        +parent+". Your own company's BTC-on-Bitcoin-mainnet receiving address "
        "is "+address+". Study the system lesson, THEN independently answer "
        "IN YOUR OWN WORDS using exactly FIVE short lines:\n"
        "CHAIN: describe OWNER, Chief D, both B1 and B2 boards.\n"
        "PARENT: state your EXACT direct parent.\n"
        "RECRUIT: explain how active children inherit the earning order and "
        "why 7 billion defined role identities do not mean 7 billion live AI workers.\n"
        "WALLET: say YOUR company, BTC mainnet and exact receiving address.\n"
        "PROOF: distinguish real buyer acceptance and verified transaction "
        "from mere role definitions or promises.\n"
        "Do NOT claim a recruit was activated, a customer paid or an external "
        "message was sent unless independently evidenced."
    )
    messages=[
        {"role":"system","content":"You are a real B AI worker taking a short "
            "structured system knowledge test. Answer independently; "
            "inherited prompts are not proof you understood or acted. "
            "Do not invent earnings, recruitment or external access."},
        {"role":"user","content":"LESSON: "+STRUCTURE+"\nQUESTION: "+question},
    ]
    try:
        raw=model(messages,max_new_tokens=220,do_sample=False,
                  return_full_text=False)
        ans=raw[0].get("generated_text","")
        if isinstance(ans,list):ans=ans[-1].get("content","")
        ans=str(ans or "").strip()
        result["model_execution"]="MODEL_COMPLETED" if ans else "MODEL_EMPTY"
        result["answer"]=ans[:2000]
        if ans:
            result["grade"]=grade_answer(ans,company,role,parent,address)
            result["assessment"]=(
                "PASSED_FORMATTED_MODEL_KNOWLEDGE_CHECK"
                if result["grade"]["passed"] else
                "NEEDS_PARENT_REVIEW_OR_RETEACHING")
        else:result["assessment"]="MODEL_RETURNED_EMPTY"
    except Exception as exc:
        result["model_execution"]="MODEL_FAILED"
        result["assessment"]="MODEL_FAILED"
        result["error"]=type(exc).__name__+":"+str(exc)[:180]
    return result

def self_test():
    for company,addr in COMPANY_BTC.items():
        other=next(v for k,v in COMPANY_BTC.items() if k!=company)
        role="D04-M02-W03"
        parent="D04-M02"
        good=("CHAIN: OWNER directs Chief D; B1 transferexperiment and "
            "B2 BountyScoutAI each have a distinct board.\n"
            "PARENT: "+parent+"\n"
            "RECRUIT: Pass instructions to each activated recruit; 7 billion "
            "defined role IDs are not billions of live AI workers.\n"
            "WALLET: "+company+" receives BTC on Bitcoin mainnet at "+addr+".\n"
            "PROOF: A real buyer must accept work and a verified txid must "
            "prove payment; promises are not payment.")
        assert grade_answer(good,company,role,parent,addr)["passed"]
        assert not grade_answer(good.replace(parent,"D04-M03"),company,role,parent,addr)["passed"]
        assert not grade_answer(good.replace(addr,other),company,role,parent,addr)["passed"]
        assert not grade_answer("I understand the whole system.",company,role,parent,addr)["passed"]
        assert teach_and_check(None,company,role,parent,addr)["assessment"]=="NOT_RUN"
        class FakeModel:
            def __call__(self,messages,**kwargs):
                return [{"generated_text":good}]
        yes=teach_and_check(FakeModel(),company,role,parent,addr)
        assert yes["model_execution"]=="MODEL_COMPLETED" and yes["grade"]["passed"]
        assert yes["correct_chain_payment_verified"] is False
    print("B_SYSTEM_UNDERSTANDING_CHECK_SELFTEST_PASS two_wallets, correct_parent, recruiter_chain, real_model_gate, no_fake_payments")

if __name__=="__main__":self_test()
