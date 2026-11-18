"""Anchor Rename Handoff: explicit rename plan, not a link checker.
No files changed, network requests or scripts executed. Input is public data.
"""
import json,sys,unittest
from urllib.parse import unquote,quote
def plan(hrefs,renames,available_ids):
    if not isinstance(renames,dict) or any(not isinstance(k,str) or not k or not isinstance(v,str) or not v for k,v in renames.items()):
        raise ValueError("nonempty string rename mapping required")
    result=[]
    for index,href in enumerate(hrefs):
        if not isinstance(href,str): raise ValueError("string links required")
        if not href.startswith("#") or href=="#" or ":~:text=" in href: continue
        old=unquote(href[1:])
        if old not in renames: continue
        new=renames[old]
        result.append({"link_index":index,"old_fragment":old,
                       "suggested_href":"#"+quote(new,safe="") if new in available_ids else None,
                       "status":"REVIEW_RENAME" if new in available_ids else "TARGET_MISSING"})
    return {"changes":result,"applied":False,"browser_verified":False}
class Tests(unittest.TestCase):
    def test_rename(self):
        self.assertEqual(plan(["#old"],{"old":"new"},["new"])["changes"][0]["suggested_href"],"#new")
    def test_missing(self):
        self.assertEqual(plan(["#old"],{"old":"new"},[])["changes"][0]["status"],"TARGET_MISSING")
    def test_external(self):
        self.assertEqual(plan(["https://example.org/#old","other#old","#"],{"old":"new"},["new"])["changes"],[])
    def test_unicode(self):
        self.assertEqual(plan(["#old%20name"],{"old name":"new name"},["new name"])["changes"][0]["suggested_href"],"#new%20name")
    def test_no_auto_changes(self):
        self.assertFalse(plan([],{},[])["applied"])
if __name__=="__main__": unittest.main()
