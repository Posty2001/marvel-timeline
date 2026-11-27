#!/usr/bin/env python3
"""Database Expansion W0 — registro append-only degli ID (immutabili).
Uso: python3 tools/db_ids.py --scrivi | --verifica
Registro: data/atlante/espansione/ids_registro.json
Regole: un ID gia' registrato non cambia e non sparisce (al piu' 'lapide' con redirect);
        nuovi ID solo in append; nessun ID reinventato."""
import json, sys, hashlib, re, pathlib
import os
R = pathlib.Path(os.environ.get('DB_ROOT') or pathlib.Path(__file__).resolve().parent.parent)
IDX = R/'atlante2/data/index.json'
REG = R/'data/atlante/espansione/ids_registro.json'
MAN = R/'data/atlante/manifest.json'
SLUG = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
PREFIX = {'p':'id','U':'uni','t':'title','o':'org','a':'art','l':'loc','P':'pla','e':'ev','h':'hub','m':'mantle'}

def sha(l): return hashlib.sha256('\n'.join(sorted(l)).encode()).hexdigest()

def corrente():
    i = json.load(open(IDX))
    ids = {}
    for v in i['voci']:
        ids[v['i']] = {'tipo': v['t'], 'rif': 'voce', 'pagine': v.get('pg', [])}
    for p in sorted({p for v in i['voci'] for p in v.get('pg', [])} - set(ids)):
        ids[p] = {'tipo': 'pagina', 'rif': 'pagina-registro-storico'}
    for old, new in i['redirect'].items():
        if old not in ids:
            ids[old] = {'tipo': 'redirect', 'rif': 'redirect', 'verso': new}
    for f in sorted((R/'data/atlante/espansione/canon').glob('w*_*.jsonl')):
        if 'arricchimenti' in f.name: continue
        for l in f.read_text().splitlines():
            r = json.loads(l)
            ids[r['id']] = {'tipo': r['tipo'], 'rif': 'canon', 'ids_esterni': r.get('ids_esterni', {}), 'origine': r['origine']}
    return ids

def carica():
    return json.load(open(REG)) if REG.exists() else None

def scrivi():
    cur = corrente(); reg = carica()
    if reg is None:
        reg = {'versione': 1, 'politica': 'append-only; ID mai riusati; rimozioni solo come lapide con redirect',
               'ids': {}}
    n_new = 0
    for k, v in sorted(cur.items()):
        if k not in reg['ids']:
            reg['ids'][k] = dict({'origine': 'registro-storico', 'ondata': 'W0'}, **v, stato='attivo'); n_new += 1
        else:
            reg['ids'][k]['stato'] = 'attivo' if reg['ids'][k].get('stato') != 'lapide' else 'lapide'
    for k, v in reg['ids'].items():
        if k not in cur and v.get('stato') == 'attivo':
            v['stato'] = 'MANCANTE'  # la verifica fallira': va deciso (lapide+redirect) da un umano
    reg['conteggi'] = {'totale': len(reg['ids']), 'attivi': sum(1 for v in reg['ids'].values() if v['stato'] == 'attivo')}
    reg['ids_sha256'] = sha(reg['ids'])
    json.dump(reg, open(REG, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    print('scritto', REG.name, reg['conteggi'], 'nuovi', n_new)

def verifica():
    errs = []; reg = carica()
    if not reg: print('ERRORE: registro assente'); return 1
    cur = corrente()
    for k, v in reg['ids'].items():
        if v['stato'] == 'MANCANTE' or (v['stato'] == 'attivo' and k not in cur):
            errs.append('ID sparito senza lapide: ' + k)
        if v['stato'] == 'lapide' and not v.get('verso'):
            errs.append('lapide senza redirect: ' + k)
        if not SLUG.match(k): errs.append('ID non conforme (slug ascii): ' + k)
    for k in cur:
        if k not in reg['ids']: errs.append('ID non registrato (eseguire --scrivi): ' + k)
    if reg['ids_sha256'] != sha(reg['ids']): errs.append('checksum registro non coerente')
    man = json.load(open(MAN))
    if len(man.get('conteggi', {})) and 'ids_sha256' not in man: errs.append('manifest senza ids_sha256')
    print('ID registrati:', len(reg['ids']), '| errori:', len(errs))
    for e in errs[:20]: print(' -', e)
    return 1 if errs else 0

if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else '--verifica'
    if a == '--scrivi': scrivi(); sys.exit(verifica())
    sys.exit(verifica())
