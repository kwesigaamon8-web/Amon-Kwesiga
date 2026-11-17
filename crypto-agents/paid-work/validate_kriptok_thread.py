"""Validate original eight-post KriptoK Superteam submission draft for basic integrity.

This checks files and stated source constraints; it cannot verify an external X
post, community participation, sponsor acceptance or a USDC receipt.
"""
import re
from pathlib import Path

PATH=Path("crypto-agents/paid-work/kriptok-creator-original-thread.md")
def extract(src):
    return re.findall(r"(?ms)^### Post ([1-8])\n\n(.*?)(?=^### Post [1-8]\n|\n## Source and original-work verification)", src)
def test():
    txt=PATH.read_text(encoding="utf-8")
    posts=extract(txt)
    assert len(posts)==8, "Exactly 8 ordered X posts required"
    assert [int(n) for n,_ in posts]==list(range(1,9)), "Sequence must be 1..8"
    for n,body in posts:
        text=body.strip()
        assert len(text)>=65, f"Post {n} is too short for an educational thread"
        assert len(text)<=280, f"Post {n} exceeds legacy X character budget"
        assert not re.search(r"(?i)guaranteed.*profit|risk.free|I traded|I deposited|I bought",text)
    assert "@KriptoK" in txt and "@KriptoKLeague" in txt
    assert "https://superteam.fun/earn/listing/kriptok-creator-challenge-01/" in txt
    assert "https://www.kriptok.io/" in txt
    assert "no X post" in txt, "No false submission representation"
    assert "200 USDC" in txt and "*total prize pool*" in txt
    assert "Solana USDC" in txt and "cannot receive Solana USDC" in txt
    print("KRIPTOK_ORIGINAL_X_THREAD_VALIDATED",len(posts),"posts",
          [len(body.strip()) for _,body in posts],
          "NO_EXTERNAL_POST_OR_PRIZE_VERIFIED")
if __name__=="__main__":
    test()
