#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
rows=[json.loads(x) for x in (ROOT/'data/traza_principal.jsonl').read_text().splitlines() if x.strip()]
assert len(rows)==20,(len(rows),'eventos')
assert rows[0]['type']=='init' and rows[-1]['type']=='done'
assert rows[-1]['dist']==[0,2,1,3,1,5,-1]
assert rows[0]['buckets'][0]==[[0,0]]
assert len(rows[0]['buckets'])==rows[0]['C']+1==7
assert any(r['type']=='relax' and (r['u'],r['v'],r['w'])==(2,4,0) for r in rows)
assert any(r['type']=='relax' and (r['u'],r['v'],r['old'],r['candidate'])==(2,1,4,2) for r in rows)
assert sorted(r['old'] for r in rows if r['type']=='stale')==[4,6,7]
for i,e in enumerate(rows):
    if e['type']=='relax':
        assert e['dist'][e['v']]==e['candidate'],(i,'candidato')
        assert e['old']==-1 or e['candidate']<e['old'],(i,'no mejora')
        assert [e['v'],e['candidate']] in e['buckets'][e['candidate']%(e['C']+1)],(i,'bucket')
    if e['type']=='pop':
        assert e['settled'][e['u']],(i,'no extraido')
print('OK: 20 eventos C++, relajaciones y buckets coherentes. Distancias finales:',rows[-1]['dist'])
