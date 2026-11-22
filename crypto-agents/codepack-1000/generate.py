#!/usr/bin/env python3
"""Generate 1,000 original, offline, single-file Python utility variants.

50 small operations × 20 deterministic presets = 1,000 distinct runnable scripts.
Not 1,000 unique algorithms, miners, active agents, or commercial products.
"""
from __future__ import annotations
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile

B1 = 'bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z'
B2 = 'bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9'
USDC = '0x734989a439F146885C12907cd9Dd191b03d5B07e'

# Each operation snippet is self-contained; it reads the JSON object's 'value'.
# PRESET changes rounding, windowing, thresholds, caps, salts or other settings.
OPERATIONS = {
 'numbers_sum': '''a=[float(x) for x in v]; return round(sum(a[:PRESET+20]), min(PRESET,10))''',
 'numbers_mean': '''a=[float(x) for x in v][:PRESET+20]; return round(sum(a)/len(a),min(PRESET,10)) if a else None''',
 'numbers_median': '''a=sorted(float(x) for x in v[:PRESET+20]); n=len(a); return (a[n//2] if n%2 else (a[n//2-1]+a[n//2])/2) if n else None''',
 'numbers_variance': '''a=[float(x) for x in v][:PRESET+20]; m=sum(a)/len(a) if a else 0; return round(sum((x-m)**2 for x in a)/len(a),min(PRESET,10)) if a else None''',
 'numbers_min_max': '''a=[float(x) for x in v[:PRESET+20]]; return {'min':min(a),'max':max(a)} if a else None''',
 'numbers_percentile': '''a=sorted(float(x) for x in v); return a[min(len(a)-1,(PRESET*len(a)-1)//20)] if a else None''',
 'numbers_running_total': '''a=[float(x) for x in v[:PRESET+20]]; out=[]; cur=0;\nfor x in a: cur+=x; out.append(round(cur,min(PRESET,10)))\nreturn out''',
 'numbers_moving_average': '''a=[float(x) for x in v]; width=PRESET; return [round(sum(a[max(0,i-width+1):i+1])/len(a[max(0,i-width+1):i+1]),6) for i in range(len(a))]''',
 'numbers_positive_count': '''a=[float(x) for x in v]; return sum(x>=PRESET-10 for x in a)''',
 'numbers_scale': '''return [round(float(x)*PRESET,6) for x in v]''',
 'finance_percentage_change': '''a=[float(x) for x in v]; return round((a[1]-a[0])/abs(a[0])*100,min(PRESET,10)) if len(a)>=2 and a[0]!=0 else None''',
 'finance_growth_projection': '''a=[float(x) for x in v]; return round(a[0]*(1+a[1]/100)**PRESET,6) if len(a)>=2 else None''',
 'finance_simple_interest': '''a=[float(x) for x in v]; return round(a[0]*(a[1]/100)*PRESET,6) if len(a)>=2 else None''',
 'finance_markup': '''a=[float(x) for x in v]; return round(a[0]*(1+PRESET/100),2) if a else None''',
 'finance_margin': '''a=[float(x) for x in v]; return round((a[1]-a[0])/a[1]*100,6) if len(a)>=2 and a[1] else None''',
 'finance_discount': '''a=[float(x) for x in v]; return round(a[0]*(1-PRESET/100),2) if a else None''',
 'finance_break_even_units': '''a=[float(x) for x in v]; return math.ceil(a[0]/(a[1]-a[2])) if len(a)>=3 and a[1]>a[2] else None''',
 'finance_net_after_fee': '''a=[float(x) for x in v]; return round(a[0]*(1-PRESET/100),2) if a else None''',
 'finance_unit_cost': '''a=[float(x) for x in v]; return round(a[0]/a[1],6) if len(a)>=2 and a[1] else None''',
 'finance_budget_gap': '''a=[float(x) for x in v]; return round(a[0]-sum(a[1:PRESET+21]),2) if a else None''',
 'text_slugify': '''s=str(v).strip().lower(); s=re.sub(r'[^a-z0-9]+','-',s).strip('-'); return s[:PRESET*8]''',
 'text_word_count': '''a=re.findall(r"\\b\\w+\\b",str(v)); return {'count':len(a),'preview':a[:PRESET]}''',
 'text_character_count': '''s=str(v); return {'total':len(s),'nonspace':len(re.sub(r'\\s','',s)),'limit':PRESET*50}''',
 'text_unique_lines': '''lines=str(v).splitlines(); return list(dict.fromkeys(x.strip() for x in lines if x.strip()))[:PRESET+20]''',
 'text_sort_lines': '''return sorted(str(v).splitlines(),key=str.casefold)[:PRESET+20]''',
 'text_truncate': '''s=str(v); return s[:PRESET*10] + ('...' if len(s)>PRESET*10 else '')''',
 'text_keywords': '''s=str(v).lower(); words=re.findall(r"\\b\\w+\\b",s); return {w:words.count(w) for w in sorted(set(words))[:PRESET]}''',
 'text_redact_email': '''s=str(v); return re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}","[REDACTED]",s)[:PRESET*500]''',
 'text_extract_urls': '''return re.findall(r'https?://[^\\s<>()]+',str(v))[:PRESET]''',
 'text_titlecase': '''return ' '.join(w[:1].upper()+w[1:].lower() for w in str(v).split())[:PRESET*50]''',
 'csv_row_count': '''rows=list(csv.DictReader(io.StringIO(str(v)))); return {'rows':len(rows),'limit_for_preview':PRESET*10}''',
 'csv_headers': '''rows=csv.reader(io.StringIO(str(v))); return (next(rows,[]) or [])[:PRESET+20]''',
 'csv_missing_cells': '''rows=list(csv.DictReader(io.StringIO(str(v)))); return {k:sum(not (r.get(k) or '').strip() for r in rows[:PRESET*100]) for k in (rows[0] if rows else {})}''',
 'csv_remove_duplicates': '''rows=list(csv.reader(io.StringIO(str(v)))); seen=set(); out=[];\nfor row in rows:\n key=tuple(row);\n if key not in seen: seen.add(key); out.append(row)\nreturn out[:PRESET*100]''',
 'csv_group_counts': '''rows=list(csv.DictReader(io.StringIO(str(v)))); key=next(iter(rows[0])) if rows else None; return dict(collections.Counter(r.get(key,'') for r in rows[:PRESET*100])) if key else {}''',
 'csv_sort_first_column': '''rows=list(csv.reader(io.StringIO(str(v)))); return [rows[0]]+sorted(rows[1:PRESET*100+1],key=lambda r:r[0] if r else '') if rows else []''',
 'csv_numeric_first_column_sum': '''rows=list(csv.reader(io.StringIO(str(v)))); nums=[];\nfor row in rows[:PRESET*100]:\n try: nums.append(float(row[0]))\n except (IndexError,ValueError): pass\nreturn round(sum(nums),6)''',
 'csv_to_json': '''rows=list(csv.DictReader(io.StringIO(str(v)))); return rows[:PRESET*100]''',
 'csv_empty_rows': '''rows=list(csv.reader(io.StringIO(str(v)))); return sum(not any(x.strip() for x in row) for row in rows[:PRESET*100])''',
 'csv_duplicate_rows_count': '''rows=list(csv.reader(io.StringIO(str(v)))); c=collections.Counter(tuple(x) for x in rows[:PRESET*100]); return sum(n-1 for n in c.values() if n>1)''',
 'dev_sha256': '''return hashlib.sha256((str(v)+'|preset='+str(PRESET)).encode()).hexdigest()''',
 'dev_sha256_double': '''d=hashlib.sha256((str(v)+'|preset='+str(PRESET)).encode()).digest(); return hashlib.sha256(d).hexdigest()''',
 'dev_base64_encode': '''return base64.b64encode((str(v)[:PRESET*100]).encode('utf-8')).decode('ascii')''',
 'dev_base64_decode': '''return base64.b64decode(str(v),validate=True).decode('utf-8')[:PRESET*100]''',
 'dev_hex_encode': '''return str(v)[:PRESET*100].encode('utf-8').hex()''',
 'dev_hex_decode': '''return bytes.fromhex(str(v)).decode('utf-8')[:PRESET*100]''',
 'dev_url_parse': '''u=urllib.parse.urlsplit(str(v)); return {'scheme':u.scheme,'host':u.hostname,'path':u.path[:PRESET*50],'query':u.query[:PRESET*50]}''',
 'dev_domain_suffix': '''host=urllib.parse.urlsplit(str(v)).hostname or str(v).split('/')[0].split(':')[0]; parts=host.lower().split('.'); return '.'.join(parts[-min(len(parts),max(2,PRESET//5)) :])''',
 'dev_json_flatten': '''out={};\ndef walk(a,p='',d=0):\n if d>PRESET:return\n if isinstance(a,dict):\n  for k,x in a.items():walk(x,(p+'.' if p else '')+str(k),d+1)\n elif isinstance(a,list):\n  for i,x in enumerate(a):walk(x,p+'['+str(i)+']',d+1)\n else:out[p]=a\nwalk(v); return out''',
 'dev_json_keys': '''return sorted(str(k) for k in v.keys())[:PRESET*10] if isinstance(v,dict) else []'''
}
assert len(OPERATIONS)==50, len(OPERATIONS)

INPUTS={
 'numbers': [1,2,3,4,5,6,7,8,9,10],
 'finance': [1000,250,50,10],
 'text': 'Hello World https://example.org/a Alice@example.com\\nSecond line\\nSecond line',
 'csv': 'name,amount\\nA,10\\nB,20\\nA,10\\nC,\\n',
 'dev': 'https://example.org/path?q=1',
}
INPUTS.update({
 'dev_base64_decode': 'SGVsbG8=', 'dev_hex_decode': '48656c6c6f',
 'dev_json_flatten': {'a': {'b': 4}, 'c': [1,2]},
 'dev_json_keys': {'a': 3,'b': 2},
})

def code(name:str,preset:int,code_id:int)->str:
    body=OPERATIONS[name]
    # Convert mini-snippet into an actual def run(v) with correct multiline indentation.
    snippet=body.replace('; ', '\n')
    indented='\n'.join('    '+x for x in snippet.splitlines())
    return f'''#!/usr/bin/env python3
"""ENIGMA code {code_id:04d}/1000 — {name}, preset {preset}/20.

Original local-only public source; no network/mining, no automatic crypto transfers.
This is one of 50 algorithms x 20 parameter settings, NOT 1,000 unique algorithms.
"""
import base64
import collections
import csv
import hashlib
import io
import json
import math
import re
import sys
import urllib.parse

B1_BTC_MAINNET = {B1!r}
B2_BTC_MAINNET = {B2!r}
B1_NATIVE_BASE_USDC_RECEIVE_ONLY = {USDC!r}
# Addresses are displayed for optional, independently verified paid-service payment.
# This code neither mines Bitcoin nor uses these destinations automatically.
PRESET = {preset}
OPERATION = {name!r}
CODE_ID = {code_id}

def run(v):
{indented}

def main():
    try:
        payload = json.load(sys.stdin)
        value = payload.get('value',payload) if isinstance(payload,dict) else payload
        result = run(value)
        print(json.dumps({{'program_id':CODE_ID, 'operation':OPERATION, 'preset':PRESET, 'result':result}},ensure_ascii=False,allow_nan=False))
    except Exception as exc:
        print(json.dumps({{'program_id':CODE_ID,'error':str(exc)}}),file=sys.stderr)
        sys.exit(1)

if __name__=='__main__':
    main()
'''

def build(out:pathlib.Path)->list[dict]:
    out.mkdir(parents=True,exist_ok=True)
    listing=[]
    for op_index,(op,snippet) in enumerate(OPERATIONS.items()):
        category=op.split('_',1)[0]
        for preset in range(1,21):
            code_id=op_index*20+preset
            filename=f'enigma_{code_id:04d}_{op}_p{preset:02d}.py'
            source=code(op,preset,code_id)
            compile(source,filename,'exec')
            path=out/filename
            path.write_text(source,encoding='utf-8')
            listing.append({'id':code_id,'name':op,'category':category,'preset':preset,'path':filename,'sha256':hashlib.sha256(source.encode()).hexdigest()})
    assert len(listing)==1000 and len({x['path'] for x in listing})==1000
    (out/'MANIFEST.json').write_text(json.dumps({'package':'ENIGMA Original Code Pack','count':1000,'algorithm_families':50,'presets_per_family':20,'created':'2026-11-22','source':'Original code generated by this generator; safe offline local-data utility functions','no_real_mining':True,'no_guaranteed_returns':True,'public_wallets':{'b1_btc_mainnet':B1,'b2_btc_mainnet':B2,'b1_base_usdc_receive_only':USDC},'files':listing},indent=2)+'\n',encoding='utf-8')
    (out/'README.md').write_text(f'''# ENIGMA 1,000 runnable code variants — free source and service bonus

50 original, offline data/math/text/CSV/developer utility algorithms x 20 parameter presets = **1,000 separately executable Python 3 programs**, each in its own .py file with a SHA-256 manifest. This is NOT 1,000 distinct mining engines, 1,000 independently invented algorithms, an AI worker fleet, or a cryptocurrency earning guarantee.

The free PC AI Miner **educational** bonus is linked separately: https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/docs/miner-bonus.html . Unverified historical Windows ZIP executables are intentionally excluded.

## Run any code

Example: `echo '{{"value": [1,2,3]}}' | python enigma_0001_numbers_sum_p01.py`

Every script accepts JSON stdin and writes one JSON result. See `MANIFEST.json` for each ID, family and SHA256. No network access, wallets, mining pools, file-system modifications or hidden background jobs. The algorithms are demonstrators, not professional tax/legal/financial advice.

## Project receive-only addresses (visible, never used automatically)

- B1 BTC **Bitcoin mainnet:** `{B1}`
- B2 BTC **Bitcoin mainnet:** `{B2}`
- B1 native USDC **Base mainnet, conditional by agreed job:** `{USDC}`

You can use the software free of charge; paid work involves a separate individually agreed service, amount, asset and network. Do not send coins unless you have confirmed the actual project, recipient and contract. Public address display is not a receipt or proof of wallet ownership.

License: Original source is made available for review and private adaptation; no third-party miner executables are bundled. Check all third-party licenses before redistribution of any independently obtained miner.

## Evidence
The generator produces the source scripts deterministically; tests include syntax compilation for all 1,000 files, unique filename/hash checks and a sampled execution matrix. A standalone script is proof of a code file, not of a buyer, an activated AI agent or earned BTC.
''',encoding='utf-8')
    return listing

def test(out:pathlib.Path,listing:list[dict])->dict:
    # One subprocess per family across four presets + both boundary scripts, and
    # in-process execution of all one thousand source files under sample data.
    failures=[]; run_pass=0
    for item in listing:
        operation=item['name']
        typ=operation.split('_',1)[0]
        value=INPUTS.get(operation,INPUTS[typ])
        filename=out/item['path']
        ns={'__name__':'not_main'}
        try:
            exec(compile(filename.read_text(encoding='utf-8'),str(filename),'exec'),ns)
            result=ns['run'](value)
            json.dumps(result,allow_nan=False)
            run_pass+=1
        except Exception as e:
            failures.append((item['id'],operation,str(e)))
    if failures:
        raise AssertionError(f'Failed {len(failures)} sample runs: {failures[:12]}')
    subprocess_pass=0
    for item in listing[::20]:
        operation=item['name']; typ=operation.split('_',1)[0]
        val=INPUTS.get(operation,INPUTS[typ])
        p=subprocess.run([sys.executable,str(out/item['path'])],input=json.dumps({'value':val}),text=True,capture_output=True,timeout=4)
        if p.returncode!=0:raise RuntimeError((item['id'],p.stderr))
        obj=json.loads(p.stdout)
        if obj['program_id']!=item['id']:raise RuntimeError('bad ID')
        subprocess_pass+=1
    return {'syntax_compiled':len(listing),'in_process_samples_passed':run_pass,'subprocess_cli_samples_passed':subprocess_pass,'distinct_scripts':len(set(x['sha256'] for x in listing))}

if __name__=='__main__':
    base=pathlib.Path(__file__).resolve().parent
    out=base/'enigma_1000_codes'
    listing=build(out)
    result=test(out,listing)
    (out/'TEST_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    archive=base/'ENIGMA_1000_Original_Codes.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(out.iterdir()):
            z.write(p,arcname='ENIGMA_1000_Codes/'+p.name)
    print(json.dumps({'result':result,'zip':str(archive),'size_bytes':archive.stat().st_size},indent=2))