"""Test worldwide open-source intelligence on public synthetic source responses.

Synthetic data is for parser verification only; production country findings
must be backed by actual public World Bank / GitHub API responses.
"""
import json, sys
from pathlib import Path
sys.path.insert(0,"crypto-agents")
import world_osint_engine as e


def fake(url):
    if url==e.WB_COUNTRY:
        return [{"pages":1,"total":2},[
            {"iso2Code":"UG","name":"Uganda","region":{"value":"Sub-Saharan Africa"},
             "incomeLevel":{"value":"Low income"}},
            {"iso2Code":"US","name":"United States","region":{"value":"North America"},
             "incomeLevel":{"value":"High income"}}]]
    if "IT.NET.USER.ZS" in url:
        return [{"pages":1,"total":3},[
            {"country":{"id":"UG"},"date":"2024","value":34.5},
            {"country":{"id":"US"},"date":"2025","value":93.1},
            {"country":{"id":"UG"},"date":"2023","value":29}]]
    if "SP.POP.TOTL" in url:
        return [{"pages":1,"total":2},[
            {"country":{"id":"UG"},"date":"2024","value":50000000},
            {"country":{"id":"US"},"date":"2024","value":340000000}]]
    if "api.github.com/search/issues" in url:
        return {"items":[
            {"state":"open","number":77,"title":"Test paid software QA",
             "html_url":"https://github.com/independent-org/code/issues/77",
             "updated_at":"2026-11-18T00:00:00Z"},
            {"state":"open","number":35,"title":"Own offer",
             "html_url":"https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/35"},
            {"state":"closed","number":20,"title":"Closed",
             "html_url":"https://github.com/independent-org/code/issues/20"},
        ]}
    raise AssertionError("Unapproved test source: "+url)


def main():
    e.tests()
    assert e.WB_ROOT.startswith("https://api.worldbank.org")
    assert len(e.for_shard(0))==9 and len(e.for_shard(29))==8
    for url in ("http://api.worldbank.org/v2/country",
                "https://evil.example/steal", "https://web.archive.org/"):
        try:e.get_json(url)
        except ValueError:pass
        else:raise AssertionError("Untrusted endpoint accepted")

    s=e.gather(fake)
    assert len(s["countries"])==249
    ug=s["countries"]["UG"]
    assert ug["source_status"]=="INDICATOR_OBSERVED"
    assert ug["observations"]["IT.NET.USER.ZS"]["value"]==34.5
    assert ug["observations"]["IT.NET.USER.ZS"]["observation_year"]==2024
    assert ug["observations"]["SP.POP.TOTL"]["value"]==50000000
    assert s["countries"]["US"]["observations"]["official_country_metadata"]["worldbank_name"]=="United States"
    assert s["countries"]["AQ"]["source_status"]=="UNAVAILABLE"
    assert len(s["unverified_public_issue_candidates"])==1
    assert s["unverified_public_issue_candidates"][0]["funded_bounty_unverified"]
    assert not s["unverified_public_issue_candidates"][0]["external_application_sent"]
    assert s["verified_buyer_contracts"]==0
    assert s["verified_incoming_btc"]==0
    shards=[e.shard(i,s) for i in range(30)]
    assert sum(x["country_count"] for x in shards)==249
    assert sum(x["observed_metadata"] for x in shards)==2
    assert sum(x["observed_indicators"] for x in shards)==4
    assert all(x["owner"]["owner_sha256"]==e.canonical()["owner_sha256"] for x in shards)
    assert all(x["verified_new_earned_btc"]==0 for x in shards)
    assert all(x["other_virtual_roles_notified"] is False for x in shards)
    tampered=json.loads(json.dumps(s));tampered["owner"]["owner_sha256"]="0"*64
    try:e.shard(0,tampered)
    except ValueError:pass
    else:raise AssertionError("Incorrect human order accepted")
    print("B1B2_249_COUNTRY_OSINT_LIVE_SOURCE_SCHEMA_TESTS_PASS "+
          json.dumps({"codes":249,"shards":30,"synthetic_country_metadata":2,
                      "synthetic_indicators":4,
                      "real_outreach":0,"earnings_claimed":0}))


if __name__=="__main__":main()
