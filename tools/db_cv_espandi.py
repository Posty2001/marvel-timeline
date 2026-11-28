#!/usr/bin/env python3
"""W5/W6 Comic Vine: espansione dei fumetti (personaggi secondari, team, saghe, testate) e promozione dello staging.
Comic Vine = SOLO ID, nome e conteggi (nessun testo copiato). Regola D12: voce nuova = Comic Vine + pagina omonima su Marvel Database (seconda fonte indipendente,
titolo esatto); altrimenti staging. Abbinamento a voci esistenti solo per nome normalizzato esatto con candidato Earth-616 UNICO.
Uso: python3 tools/db_cv_espandi.py --bersagli | --scrivi | --verifica   (nessuna rete)"""
import json, sys, re, pathlib, unicodedata, collections
R = pathlib.Path(__file__).resolve().parent.parent
E = R / 'data/atlante/espansione'
SOGLIA_PERS = 40   # numero minimo di albi in cui compare (Comic Vine) per un personaggio nuovo
def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s)).strip()
def base(n): return re.sub(r'\s*\([^)]*\)\s*$', '', n or '').strip()
def slug(s): return norm(s).replace(' ', '-')
def canon_tutto():
    out = []
    for f in sorted((E / 'canon').glob('w*_*.jsonl')):
        if 'arricchimenti' in f.name or f.name == 'w5_cv.jsonl': continue
        for l in f.read_text().splitlines():
            if l.strip(): out.append(json.loads(l))
    return out
def storico():
    i = json.load(open(R / 'atlante2/data/index.json')); return i['voci']
def indice(canon):
    ix = collections.defaultdict(list)
    for c in canon:
        for k in {c['nome'], base(c['nome']), c.get('nome_it') or '', *c.get('alias', [])}:
            if k: ix[norm(base(k))].append(c)
    return ix
TIPO_CV = {'characters': 'identita', 'teams': 'organizzazione', 'story_arcs': 'evento', 'volumes': 'opera'}
def carica_cv():
    d = json.load(open(E / 'raw/cv2_marvel.json'))['risorse']; return d
def candidati(cv, canon):
    ix = indice(canon); ex = {norm(base(v['n'])) for v in storico()} | {norm(base(v.get('it') or '')) for v in storico()}
    abb, nuovi, gia = [], [], 0
    visti = set()
    for ris, lst in cv.items():
        t = TIPO_CV[ris]
        for x in lst:
            n = base(x['n']); k = norm(n)
            if not k or (ris, k) in visti: continue
            visti.add((ris, k))
            if ris == 'characters' and (x.get('c') or 0) < SOGLIA_PERS: pass
            m = [c for c in ix.get(k, []) if c.get('tipo') == t or (t == 'identita' and c.get('tipo') in ('identita', 'entita-cosmica'))]
            m616 = [c for c in m if c.get('universo') == 'uni-earth-616']
            if len(m616) == 1: abb.append({'id': m616[0]['id'], 'cv': x['id'], 'ris': ris, 'u': x['u']}); continue
            if len(m616) > 1: continue
            if ris == 'characters' and (x.get('c') or 0) < SOGLIA_PERS: continue
            nuovi.append({'nome': n, 'tipo': t, 'cv': x['id'], 'ris': ris, 'u': x['u'], 'c': x.get('c'), 'y': x.get('y'), 'omonimo_storico': k in ex or bool(m)})
    return abb, nuovi
def titoli_md(b):
    n, ris = b['nome'], b['ris']
    if ris in ('characters', 'teams'): return [n + ' (Earth-616)']
    if ris == 'volumes': return [n + ' Vol 1']
    return [n, n + ' (Event)']
def main():
    cv = carica_cv(); canon = canon_tutto(); abb, nuovi = candidati(cv, canon)
    if '--bersagli' in sys.argv:
        json.dump({'v': 1, 'bersagli': [dict(b, titoli=titoli_md(b)) for b in nuovi]}, open(E / 'cv_bersagli.json', 'w'), ensure_ascii=False, separators=(',', ':'))
        print('abbinati', len(abb), 'nuovi bersagli', len(nuovi), collections.Counter(b['ris'] for b in nuovi))
        json.dump(abb, open(E / 'cv_match.json', 'w'), ensure_ascii=False, separators=(',', ':')); return
if __name__ == '__main__': main()
