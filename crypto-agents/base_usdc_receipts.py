"""Read-only public Base mainnet USDC receiving-address observation.

Not a wallet, payment collector, beneficiary ownership check or earnings proof.
Read only via eth_chainId, eth_blockNumber, eth_call, and eth_getLogs.
No private keys, transactions, signatures, gas, deposits or authentication.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import urllib.request
from pathlib import Path

ADDRESS = '0x734989a439F146885C12907cd9Dd191b03d5B07e'
USDC = '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
RPC = 'https://base-rpc.publicnode.com'
CHAIN_ID = 8453
TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
BALANCE_SELECTOR = '0x70a08231'
DECIMALS_SELECTOR = '0x313ce567'
LOOKBACK = 24000
CHUNK = 1000
OUT = Path('paid-opportunity-reports/base-usdc-receipts.json')


def valid_hex(value, digits=None):
    if not isinstance(value, str) or not value.startswith('0x'):
        return False
    body = value[2:]
    return (digits is None or len(body) == digits) and bool(body) and all(c in '0123456789abcdefABCDEF' for c in body)


def units_text(raw):
    if not isinstance(raw, int) or raw < 0:
        raise ValueError('Invalid token amount')
    return f'{raw // 1000000}.{raw % 1000000:06d}'


def rpc(method, params):
    request = urllib.request.Request(
        RPC,
        data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(),
        headers={'Content-Type':'application/json','User-Agent':'B1-B2-ReadOnly-USDC-Receipt-Check/1.0'},
        method='POST')
    with urllib.request.urlopen(request, timeout=9) as response:
        answer = json.loads(response.read(1000000))
    if not isinstance(answer, dict) or answer.get('error') or 'result' not in answer:
        raise ValueError('RPC error or invalid payload')
    return answer['result']


def parse_logs(logs, start, end):
    if not isinstance(logs, list):
        raise ValueError('Logs response not a list')
    found=[]
    for x in logs:
        if not isinstance(x,dict) or x.get('removed') is True:
            continue
        topics=x.get('topics')
        if (str(x.get('address','')).lower()!=USDC.lower() or
                not isinstance(topics,list) or len(topics)<3 or
                not isinstance(topics[0],str) or topics[0].lower()!=TRANSFER_TOPIC or
                not valid_hex(topics[2],64) or
                topics[2][-40:].lower()!=ADDRESS[2:].lower() or
                not valid_hex(x.get('transactionHash'),64) or
                not valid_hex(x.get('data')) or
                not valid_hex(x.get('blockNumber'))):
            continue
        block=int(x['blockNumber'],16)
        if not (start <= block <= end):
            continue
        amount=int(x['data'],16)
        found.append({'txid':x['transactionHash'],'block':block,
                      'value_usdc':units_text(amount),'raw_micro_usdc':amount,
                      'to_address':ADDRESS,'asset_contract':USDC,
                      'explorer':'https://basescan.org/tx/'+x['transactionHash'],
                      'settled_earned_income':False,'payer_purpose':'not_verified'})
    return found


def scan(call=rpc):
    result={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'owner_shared_receiving_address':ADDRESS,'network':'Base mainnet',
            'rpc_endpoint':RPC,
            'chain_id_expected':CHAIN_ID,'token':'native Circle USDC',
            'token_contract':USDC,'wallet_control_independently_verified':False,
            'payment_purpose_verified':False,'earned_receipts_verified':0,
            'spending_authority':False,'signatures_made':0,
            'scan_complete':False,'warnings':[],'recent_transfers_observed':[]}
    try:
        chain=int(call('eth_chainId',[]),16)
        if chain!=CHAIN_ID:
            raise ValueError('Unexpected RPC chain; no payment information can be trusted')
        result['chain_id_observed']=chain
        decimals=int(call('eth_call',[{'to':USDC,'data':DECIMALS_SELECTOR},'latest']),16)
        if decimals != 6:
            raise ValueError('USDC decimals mismatch; cannot value tokens')
        balance_call=BALANCE_SELECTOR + ADDRESS[2:].lower().zfill(64)
        balance=int(call('eth_call',[{'to':USDC,'data':balance_call},'latest']),16)
        result['current_public_usdc_balance']=units_text(balance)
        result['balance_is_not_new_receipt_or_earned_income']=True
        head=int(call('eth_blockNumber',[]),16)
        start=max(0,head-LOOKBACK+1)
        result['block_window']={'start':start,'end':head,'size':head-start+1}
        to_topic='0x' + ADDRESS[2:].lower().zfill(64)
        found=[]
        for begin in range(start,head+1,CHUNK):
            end=min(begin+CHUNK-1,head)
            try:
                logs=call('eth_getLogs',[{'fromBlock':hex(begin),'toBlock':hex(end),
                                          'address':USDC,'topics':[TRANSFER_TOPIC,None,to_topic]}])
                found.extend(parse_logs(logs,begin,end))
            except Exception as exc:
                result['warnings'].append({'from_block':begin,'to_block':end,
                                           'reason':type(exc).__name__+': '+str(exc)[:110]})
        result['recent_transfers_observed']=list({(t['txid'],t['block'],t['raw_micro_usdc']):t for t in found}.values())[:100]
        result['scan_complete']=not result['warnings']
        result['source_status']='PUBLIC_BALANCE_AND_LOG_WINDOW_OBSERVED' if result['scan_complete'] else 'PARTIAL_LOG_SCAN'
    except Exception as exc:
        result['source_status']='UNAVAILABLE_OR_UNVERIFIED'
        result['warnings'].append({'reason':type(exc).__name__+': '+str(exc)[:120]})
    return result


def self_test():
    assert units_text(1234567)=='1.234567'
    assert units_text(0)=='0.000000'
    assert valid_hex('0x'+('ab'*32),64)
    assert not valid_hex('0xzz',2)
    sample={'address':USDC,'topics':[TRANSFER_TOPIC,'0x'+'00'*32,'0x'+ADDRESS[2:].lower().zfill(64)],
            'blockNumber':hex(90),'data':hex(3500000),'transactionHash':'0x'+'ab'*32}
    assert parse_logs([sample],0,100)[0]['value_usdc']=='3.500000'
    assert parse_logs([{**sample,'address':'0x'+'12'*20}],0,100)==[]
    assert parse_logs([{**sample,'topics':[TRANSFER_TOPIC,'0x'+'00'*32,'0x'+'56'*32]}],0,100)==[]
    def fake(method,params):
        if method=='eth_chainId':return hex(CHAIN_ID)
        if method=='eth_blockNumber':return hex(150)
        if method=='eth_call':
            if params[0]['data']==DECIMALS_SELECTOR:return hex(6)
            return hex(2500000)
        if method=='eth_getLogs':
            lo=int(params[0]['fromBlock'],16);hi=int(params[0]['toBlock'],16)
            return [sample] if lo<=90<=hi else []
        raise AssertionError(method)
    got=scan(fake)
    assert got['scan_complete'] and got['current_public_usdc_balance']=='2.500000',got
    assert len(got['recent_transfers_observed'])==1,got
    assert not got['payment_purpose_verified'] and got['earned_receipts_verified']==0
    def wrong_chain(method,params): return '0x1'
    assert scan(wrong_chain)['source_status']=='UNAVAILABLE_OR_UNVERIFIED'
    print('BASE_USDC_READ_ONLY_SELF_TEST_PASS: chain, token, six decimals, filters, unknown payer')


def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:
        self_test();return
    data=scan()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('BASE_USDC_PUBLIC_RECEIPT_OBSERVATION',json.dumps({
        'status':data['source_status'],
        'balance_observed':data.get('current_public_usdc_balance','UNKNOWN'),
        'recent_transfer_count':len(data['recent_transfers_observed']),
        'scan_complete':data['scan_complete'],
        'warnings':len(data['warnings']),
        'verified_earned_receipts':0,'owner_wallet_control_verified':False}))

if __name__=='__main__':main()
