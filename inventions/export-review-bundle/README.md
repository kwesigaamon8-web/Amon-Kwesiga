# Export Interoperability Review — synthetic service prototype

18 November 2026 (Kampala). Original integration sample; no customer work or income claimed.

## Proposed paid deliverable
Review one authorized public JSON export and one related CSV export, each up to1MB, with a concise issue inventory and regression fixtures. Proposed fee25,000 sats, subject to written agreement. Target market: GitHub API/export maintainers and BitcoinTalk Services integration buyers. No buyer, accepted price, regional eligibility or BTC-mainnet payout willingness established. Mainnet must be agreed before commissioning; no Lightning/alternative route assumed.

Problem: an export may parse while retaining ambiguous duplicate JSON names or spreadsheet-sensitive CSV cells. The service combines two existing tools into one reviewer handoff; it is distinct from the editorial guide bundle. It does not assert cross-format semantic equality or repair customer data.

Alternatives checked: [JSON Schema](https://json-schema.org/understanding-json-schema/reference/object) validates object properties and required fields; [csvkit](https://csvkit.readthedocs.io/en/latest/changelog.html) includes CSV structural checks; [jq](https://jqlang.org/manual/) handles broader JSON transformations. Use established tools where sufficient. Our narrow service adds a documented review and buyer-specific fixtures, not a novel parser or security certification.

## Reproduction
Place the existing repository modules csv-preview-guard/csv_preview_guard.py and json-key-collision/json_key_collision.py in an authorized working directory:
```python
import csv_preview_guard, json_key_collision
bad_json = '{"status":"draft","status":"published"}'
bad_csv = 'id,status\n1,draft,unexpected\n2,=1'
j = json_key_collision.inspect(bad_json)
c = csv_preview_guard.inspect(bad_csv)
assert j['duplicate_members'] == [
    {'object_index':1,'name':'status','occurrences':2}]
assert [x['kind'] for x in c['issues']] == [
    'width_mismatch','formula_like_prefix']
assert json_key_collision.inspect(
    '{"status":"published"}')['duplicate_members'] == []
assert csv_preview_guard.inspect(
    'id,status\n1,published\n2,draft')['issues'] == []
assert bad_json == '{"status":"draft","status":"published"}' and bad_csv == 'id,status\n1,draft,unexpected\n2,=1'
```
All five assertions passed locally. The alternative fixture illustrates an author's possible resolution; no automatic rule decides which duplicate value is correct. Formula-like prefixes can be benign. Limited checks do not establish safe opening, schema validity, field meaning or customer acceptance. Never publish private reports or raw client data.

## Qualification evidence
No new comments in owner issue10 or collective issue1 after the last checked public comments. Mempool summaries for both approved addresses returned zero confirmed and mempool funded outputs; no payment relation established. One genuinely running buyer-research worker checked BitGigs buying/all filters: visible entries were stale or service sellers, not verified funded requests (https://bitgigs.com/?filtervalue=filter_1). No outreach, email, external login, spending, submission or commitments.

Next gate: independent buyer explicitly agrees scope, fee, deadline, acceptance criteria and BTC-mainnet settlement. This is an internal tested service sample, not a delivered or accepted job.
