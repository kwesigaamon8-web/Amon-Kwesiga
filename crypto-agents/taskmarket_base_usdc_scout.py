"""B1/B2 read-only Taskmarket Base USDC work scout (no wallet/signing/writes).

Source: https://docs.taskmarket.dev/api/reference ; public GET /api/tasks
A listed bounty is not an accepted contract or payment.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path

BASE = 'https://api.taskmarket.dev/api/tasks'
DOCS = 'https://docs.taskmarket.dev/api/reference'
OUT = Path('paid-opportunity-reports/taskmarket-base-usdc.json')
HEX_TX = re.compile(r'^0x[0-9a-fA-F]{64}$')
UNSAFE = re.compile(r'(?i)\b(seed phrase|private key|transfer (?:usdc|eth|coins)|deposit first|payment upfront|stake funds|register and pay|fake review|spam|guaranteed profit)\b')
SKILLS = re.compile(r'(?i)\b(python|typescript|javascript|data|csv|json|excel|reconcil|audit|qa|test|documentation|research|code|api|report|bookkeep|spreadsheet|invoice|scrap|financial|bug)\b')
NUMBER_WORDS = dict(zip(
    ('one two three four five six seven eight nine ten eleven twelve '
     'thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty').split(),
    range(1, 21)
))

def shared_pool_slots(description):
    """Spot explicitly shared TOTAL reward pools; never treat pool as a winner's pay."""
    s = description.lower()
    if 'share the full pool' in s or 'share the reward pool' in s:
        match = re.search(r'first\s+(\d+)\s+qualifying\s+(?:agents|entries|winners)', s)
        if match:
            return int(match.group(1))
    if 'split equally' in s:
        match = re.search(r'up to\s+(\d+|[a-z]+)\b', s)
        if match:
            token = match.group(1)
            return int(token) if token.isdecimal() else NUMBER_WORDS.get(token)
    return None


def decimal_usdc(row):
    try:
        raw = str(row.get('reward', '')).strip()
        if not re.fullmatch(r'\d+', raw):
            return None
        return Decimal(raw) / Decimal(1000000)
    except (TypeError, ValueError, InvalidOperation):
        return None

def parse_time(v):
    if not isinstance(v, str):
        return None
    try:
        t = dt.datetime.fromisoformat(v.replace('Z', '+00:00'))
        return t.replace(tzinfo=dt.timezone.utc) if t.tzinfo is None else t.astimezone(dt.timezone.utc)
    except ValueError:
        return None

def classify(row, now):
    if not isinstance(row, dict):
        return None
    task_id = str(row.get('id') or '')
    if not re.fullmatch(r'[A-Za-z0-9_-]{5,100}', task_id):
        return None
    amount = decimal_usdc(row)
    if amount is None or amount <= 0:
        return None
    description = str(row.get('description') or '')
    expiry = parse_time(row.get('expiryTime'))
    stake = row.get('stakeRequired')
    tx = str(row.get('escrowTxHash') or '')
    blockers = []
    if str(row.get('status') or '').lower() != 'open':
        blockers.append('not_open')
    if str(row.get('mode') or '') != 'bounty':
        blockers.append('not_simple_open_bounty')
    if stake is not False:
        blockers.append('stake_not_explicitly_false')
    if expiry is None or expiry <= now:
        blockers.append('deadline_absent_or_expired')
    if not HEX_TX.fullmatch(tx):
        blockers.append('funding_transaction_missing_or_invalid')
    if UNSAFE.search(description):
        blockers.append('unsafe_or_pay_first_language')
    submissions = row.get('submissionCount')
    competition = submissions if type(submissions) == int and submissions >= 0 else None
    pool_slots = shared_pool_slots(description)
    if pool_slots and pool_slots > 0 and competition is not None and competition >= pool_slots:
        blockers.append('shared_pool_more_submissions_than_max_paid_slots')
    share_at_capacity = (amount / Decimal(pool_slots)) if pool_slots and pool_slots > 0 else None
    if share_at_capacity is not None and share_at_capacity < Decimal('2'):
        blockers.append('shared_pool_sub_2_usdc_if_all_slots_used')
    status = 'HOLD' if blockers else 'SOURCE_OPEN_ESCROW_TX_PRESENT_NOT_PAYMENT_VERIFIED'
    fit = bool(SKILLS.search(description))
    score = (float(amount) / (1 + (competition or 0))) if competition is not None else 0
    return {
        'id': task_id, 'source_url': 'https://taskmarket.dev/tasks/' + task_id,
        'public_api_url': BASE + '/' + task_id + '?chainId=8453',
        'description_excerpt': description[:320],
        'advertised_usdc_base': str(amount), 'chain_id': 8453, 'token': 'USDC',
        'deadline_utc': expiry.isoformat() if expiry else None,
        'funding_tx_advertised': tx if HEX_TX.fullmatch(tx) else None,
        'submission_count': competition, 'fit_for_existing_skills': fit,
        'shared_reward_pool_slots': pool_slots,
        'usdc_per_winner_if_all_slots_filled': str(share_at_capacity) if share_at_capacity is not None else None,
        'competition_adjusted_score': round(score, 5),
        'status': status, 'blockers': blockers,
        'wallet_signing_required_to_submit': True, 'worker_wallet_connected': False,
        'payer_acceptance_verified': False, 'owner_deposit_verified': False
    }

def screen(payload, now=None, minimum=Decimal('2')):
    now = now or dt.datetime.now(dt.timezone.utc)
    rows = payload.get('tasks', []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        rows = []
    results = []
    for row in rows:
        item = classify(row, now)
        if item and Decimal(item['advertised_usdc_base']) >= minimum:
            results.append(item)
    results.sort(key=lambda x: (
        x['status'].startswith('SOURCE_OPEN'), x['fit_for_existing_skills'],
        x['competition_adjusted_score']), reverse=True)
    return results

def self_test():
    now = dt.datetime(2026, 11, 18, tzinfo=dt.timezone.utc)
    base = {
        'id': 'TSK-VALID1', 'description': 'Python CSV invoice reconciliation',
        'reward': '9000000', 'status': 'open', 'mode': 'bounty',
        'stakeRequired': False, 'expiryTime': '2026-11-20T00:00:00Z',
        'escrowTxHash': '0x' + 'a' * 64, 'submissionCount': 2
    }
    rows = [
        base, dict(base, id='TSK-OLD22', expiryTime='2026-11-17T00:00:00Z'),
        dict(base, id='TSK-NOTX3', escrowTxHash=None),
        dict(base, id='TSK-STAKE', stakeRequired=True),
        dict(base, id='TSK-CHEAP', reward='100000'),
        dict(base, id='TSK-PHISH', description='Share private key for reward'),
        dict(base, id='TSK-SPLIT', reward='5000000',
             description='5 USDC total reward pool. The first 50 qualifying agents share the full pool equally.',
             submissionCount=52)
    ]
    found = screen({'tasks': rows}, now)
    assert len(found) == 6 and found[0]['id'] == 'TSK-VALID1'
    pool = next(x for x in found if x['id'] == 'TSK-SPLIT')
    assert pool['status'] == 'HOLD' and pool['usdc_per_winner_if_all_slots_filled'] == '0.1'
    assert shared_pool_slots('9 USDC, split equally among accepted passes, up to nine.') == 9
    assert found[0]['advertised_usdc_base'] == '9'
    assert found[0]['status'].startswith('SOURCE_OPEN')
    assert all(x['status'] == 'HOLD' for x in found[1:])
    assert all(not x['owner_deposit_verified'] for x in found)
    # Real 19 Nov 2026 listing: 5 USDC pool, first 50 qualify,
    # already 53 entries. An open UI status does not restore paid slots.
    full_pool = dict(base,
        id='TSK-SATURATED',
        description=('5 USDC total reward pool. Open bounty, no claim step. '
                     'One qualifying public post per agent; the first 50 qualifying '
                     'agents share the full pool equally.'),
        reward='5000000', submissionCount=53)
    saturated = classify(full_pool, now)
    assert saturated['status'] == 'HOLD'
    assert saturated['shared_reward_pool_slots'] == 50
    assert saturated['usdc_per_winner_if_all_slots_filled'] == '0.1'
    assert 'shared_pool_more_submissions_than_max_paid_slots' in saturated['blockers']
    assert screen({'not_tasks': rows}, now) == []
    assert classify(dict(base, reward='NAN'), now) is None
    print('TASKMARKET_READ_ONLY_SCOUT_TEST_PASS: unit conversion, deadline, stake, tx, unsafe words')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        return self_test()
    output = {
        'checked_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'source': BASE, 'docs': DOCS,
        'network': 'Base mainnet (8453)', 'asset': 'USDC',
        'read_only': True, 'task_claims': 0, 'submissions': 0,
        'verified_crypto_receipts': 0,
        'limitations': 'Funding tx listed is not independent escrow proof. No agent has signed, won or received coins. Verify original task and Base settlement separately.'
    }
    records, errors, cursor, raw_count = [], [], None, 0
    for _ in range(3):
        query = {
            'status': 'open', 'mode': 'bounty', 'chainId': '8453',
            'sort': 'reward_desc', 'limit': '100'
        }
        if cursor:
            query['cursor'] = cursor
        url = BASE + '?' + urllib.parse.urlencode(query)
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'B1B2-PaidWorkReadOnly/1.0',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=12) as r:
                payload = json.load(r)
            rows = payload.get('tasks', []) if isinstance(payload, dict) else []
            raw_count += len(rows) if isinstance(rows, list) else 0
            records.extend(screen(payload))
            cursor = payload.get('nextCursor') if isinstance(payload, dict) and payload.get('hasMore') else None
            if not cursor:
                break
        except Exception as e:
            errors.append(type(e).__name__ + ': ' + str(e)[:180])
            break
    dedup = {r['id']: r for r in records}
    results = list(dedup.values())
    results.sort(key=lambda x: (
        x['status'].startswith('SOURCE_OPEN'),
        x['fit_for_existing_skills'],
        x['competition_adjusted_score']), reverse=True)
    payable_unverified = [x for x in results if x['status'].startswith('SOURCE_OPEN')]
    held = [x for x in results if x['status'] == 'HOLD']
    output.update({
        'source_rows_checked': raw_count,
        'screened_task_count': len(results),
        'candidate_count': len(payable_unverified),
        'held_task_count': len(held),
        'candidate_unverified': payable_unverified[:40],
        'rejected_or_held': held[:40],
        'source_errors': errors,
        'status': 'SOURCE_ERROR_DO_NOT_CLAIM_EMPTY_MARKET' if errors else 'PUBLIC_SOURCE_SCREENED',
        'next_action': 'Verify original task and escrow on Base. Submission requires a wallet signature, not authorized here.'
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print('TASKMARKET_BASE_USDC_SCOUT', json.dumps({
        'rows': raw_count, 'candidates': len(payable_unverified),
        'held': len(held), 'source_errors': errors,
        'top': [(x['id'], x['advertised_usdc_base'], x['status']) for x in payable_unverified[:5]]
    }))

if __name__ == '__main__':
    main()
