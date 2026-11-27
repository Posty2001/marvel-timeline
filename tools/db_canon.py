#!/usr/bin/env python3
"""W0: importazione sottile dei 452 record storici nel formato canonico (nessun dato nuovo, ID invariati).
Uso: python3 tools/db_canon.py --scrivi | --verifica"""
import json, sys, pathlib, re
import os
R = pathlib.Path(os.environ.get('DB_ROOT') or pathlib.Path(__file__).resolve().parent.parent)
IDX = R/'atlante2/data/index.json'; IDE = R/'data/atlante/identita.json'
OUT = R/'data/atlante/espansione/canon/storico.jsonl'
SCH = R/'data/atlante/espansione/schema/record_canonico.schema.json'
TIPO = {'p':'identita','U':'universo','t':'titolo','o':'organizzazione','a':'artefatto','l':'luogo','P':'luogo','e':'evento','h':'hub','m':'mantello'}
def build():
    idx = json.load(open(IDX)); ide = {x['id']: x for x in json.load(open(IDE))['identita']}
    rows = []
    for v in idx['voci']:
        x = ide.get(v['i'], {})
        r = {'id': v['i'], 'tipo': TIPO[v['t']], 'nome': v['n'], 'livello': 'A' if v['t']=='p' else 'B',
             'stato_verifica': 'verificata', 'origine': 'registro-storico'}
        if x.get('alias'): r['alias'] = x['alias']
        if v.get('u'): r['universo'] = v['u']
        rows.append(r)
    return rows
def valida(rows):
    s = json.load(open(SCH)); props = s['properties']; errs = []; seen = set()
    for r in rows:
        for k in s['required']:
            if k not in r: errs.append(f"{r.get('id')}: manca {k}")
        for k in r:
            if k not in props: errs.append(f"{r['id']}: campo non previsto {k}")
        if not re.match(props['id']['pattern'], r['id']): errs.append('id non conforme '+r['id'])
        if r['tipo'] not in props['tipo']['enum']: errs.append('tipo '+r['tipo'])
        if r['livello'] not in props['livello']['enum']: errs.append('livello '+r['id'])
        if r['id'] in seen: errs.append('duplicato '+r['id'])
        seen.add(r['id'])
    return errs
if __name__ == '__main__':
    rows = build()
    if '--scrivi' in sys.argv:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows)+'\n')
    cur = [json.loads(l) for l in OUT.read_text().splitlines()] if OUT.exists() else []
    errs = valida(cur)
    if cur != rows: errs.append('canon non allineato al registro storico (eseguire --scrivi)')
    for f in sorted((OUT.parent).glob('w*_*.jsonl')):
        if 'arricchimenti' in f.name: continue
        extra = [json.loads(l) for l in f.read_text().splitlines()]
        errs += [f.name + ': ' + e for e in valida(extra)]
        errs += [f.name + ': id gia\' in storico ' + r['id'] for r in extra if r['id'] in {c['id'] for c in cur}]
    print('record canonici:', len(cur), '| errori:', len(errs)); [print(' -', e) for e in errs[:15]]
    sys.exit(1 if errs else 0)
