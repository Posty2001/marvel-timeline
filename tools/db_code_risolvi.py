#!/usr/bin/env python3
"""Risoluzione a regole delle code ambigue W1-W4 (nessuna fusione per solo nome, continuita' sempre distinte).
Regole (deterministiche, documentate):
 C1 «collegamento al personaggio-base»: UN solo candidato storico e nome/alias coincidenti (dopo normalizzazione) -> l'elemento Wikidata e' il personaggio generale: si registra come ID esterno ALTERNATIVO
    dell'identita' (nessun fatto copiato, nessuna fusione).
 C2 «concetto multi-continuita'»: l'elemento coincide per nome con PIU' identita' di continuita' diverse (o con un hub) -> non e' una voce nuova ne' un arricchimento: si registra come riferimento generico dell'hub/del
    gruppo di identita' (mai attribuito a una sola incarnazione).
 C3 «nome non corrispondente»: nessun candidato ha lo stesso nome/alias (il match era solo parziale) -> e' un personaggio diverso: rinviato all'ondata fumetti (W5) come voce nuova da verificare.
Uso: python3 tools/db_code_risolvi.py [--scrivi]  -> data/atlante/espansione/review/risoluzioni_code.json"""
import json, pathlib, re, sys, unicodedata
R = pathlib.Path(__file__).resolve().parent.parent; E = R/'data/atlante/espansione'
def norm(s): s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower(); return re.sub(r'[^a-z0-9]+', ' ', re.sub(r'\(.*?\)', ' ', s)).strip()
ident = {x['id']: x for x in json.load(open(R/'data/atlante/identita.json'))['identita']}
hub = json.load(open(R/'data/atlante/identita.json')).get('hub') or []
hub_ids = {h['id'] if isinstance(h, dict) else h for h in hub}
idx = {v['i']: v['n'] for v in json.load(open(R/'atlante2/data/index.json'))['voci']}
IT = {'mystica': 'mystique', 'fenice': 'phoenix', 'vedova nera': 'black widow', 'avvoltoio': 'vulture', 'raven': 'raven', 'uomo ragno': 'spider man', 'donna invisibile': 'invisible woman'}
def nomi(i):
    x = ident.get(i) or {}; out = {norm(idx.get(i, '')), norm(x.get('nome'))} | {norm(a) for a in x.get('alias', [])}
    out |= {norm(p) for p in re.findall(r'\(([^)]*)\)', x.get('nome', ''))}
    for nm in (x.get('nome', ''), idx.get(i, '')):
        for p in re.split(r' - |/', re.sub(r'\(.*?\)', ' ', nm)): out.add(norm(p))
    out |= {IT.get(o, o) for o in list(out)}
    return {o for o in out if o}
def classifica(r):
    n = norm(r['nome']); esatti = r.get('esistenti_esatti') or []; parz = r.get('esistenti_parziali') or []
    corr = [c for c in esatti + parz if n in nomi(c) or any(n == t for t in nomi(c)) or any(len(n.split()) > 1 and n.split()[-1] == t.split()[-1] and n.split()[0] == t.split()[0] for t in nomi(c))]
    if r['tipo'] != 'identita': return 'C3', []
    if len(corr) == 1 and corr[0] not in hub_ids: return 'C1', corr
    if len(corr) >= 2 or any(c in hub_ids for c in corr): return 'C2', corr
    # nessun nome coincidente: il candidato e' diverso
    return 'C3', []
def main():
    tot = {'C1': [], 'C2': [], 'C3': []}; viste = set()
    for w in ('w1', 'w2', 'w3', 'w4'):
        f = E/'review'/f'{w}_coda.json'
        if not f.exists(): continue
        for r in json.load(open(f)).get('possibili_duplicati', []):
            k = (r['q'], r['nome'])
            if k in viste: continue
            viste.add(k); c, ids = classifica(r)
            tot[c].append({'q': r['q'], 'nome': r['nome'], 'onda': w, 'identita': ids, 'regola': c})
    out = {'versione': 1, 'regole': __doc__, 'esiti': tot, 'conteggi': {k: len(v) for k, v in tot.items()}}
    print(json.dumps(out['conteggi']))
    for c in ('C2', 'C3'): print(c, [(x['nome'], x['q']) for x in tot[c]])
    if '--scrivi' in sys.argv:
        (E/'review/risoluzioni_code.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n')
if __name__ == '__main__': main()
