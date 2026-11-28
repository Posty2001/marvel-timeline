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
    if '--scrivi' in sys.argv: return
    if '--bersagli' in sys.argv:
        json.dump({'v': 1, 'bersagli': [dict(b, titoli=titoli_md(b)) for b in nuovi]}, open(E / 'cv_bersagli.json', 'w'), ensure_ascii=False, separators=(',', ':'))
        print('abbinati', len(abb), 'nuovi bersagli', len(nuovi), collections.Counter(b['ris'] for b in nuovi))
        json.dump(abb, open(E / 'cv_match.json', 'w'), ensure_ascii=False, separators=(',', ':')); return
PREF = {'identita': 'id', 'organizzazione': 'org', 'evento': 'ev', 'opera': 'op'}
CVF = lambda x: {'fonte': 'Comic Vine', 'url': x['u'], 'licenza': 'solo ID/nome/conteggi (nessun testo copiato)'}
def scrivi():
    cv = carica_cv(); canon = canon_tutto(); abb, nuovi = candidati(cv, canon)
    md = json.load(open(E / 'raw/cvmd.json'))['pagine'] if (E / 'raw/cvmd.json').exists() else {}
    reg = json.load(open(E / 'ids_registro.json'))['ids']; usati = set(reg) | {c['id'] for c in canon}
    cvx = {(r, norm(base(x['n']))): x for r, l in cv.items() for x in l}
    ricon = {(c['nome'], c['tipo']) for c in canon}
    out, stag, cont = [], [], collections.Counter()
    nomi_esist = {norm(base(c['nome'])) for c in canon} | {norm(base(v['n'])) for v in storico()}
    def nuovo_id(tipo, nome, cvid):
        b = PREF[tipo] + '-' + (slug(nome) or 'cv-%d' % cvid)
        if b in usati: b = b + '-cv%d' % cvid
        usati.add(b); return b
    for b in nuovi:
        pag = None
        for t in b['titoli'] if 'titoli' in b else titoli_md(b):
            v = md.get(t)
            if v and not v['disambigua'] and norm(base(v['titolo'])) == norm(base(t)) and v['categorie']: pag = v; break
        if not pag: stag.append({'nome': b['nome'], 'tipo': b['tipo'], 'cv': b['cv'], 'motivo': 'una sola fonte (Comic Vine; nessuna pagina omonima su Marvel Database): resta in staging (D12)'}); cont['staging'] += 1; continue
        nome = b['nome'] + (' (Earth-616)' if b['omonimo_storico'] and b['tipo'] == 'identita' else '')
        rid = nuovo_id(b['tipo'], nome, b['cv'])
        rec = {'id': rid, 'tipo': b['tipo'], 'nome': nome, 'livello': 'C', 'stato_verifica': 'verificata', 'origine': 'W5c', 'universo': 'uni-earth-616', 'gruppi': ['cv:' + b['ris']],
               'ids_esterni': {'comicvine': str(b['cv']), 'marveldb': pag['titolo']},
               'fonti': [CVF(b), {'fonte': 'Marvel Database', 'url': pag['url'], 'licenza': 'CC BY-SA 3.0'}]}
        out.append(rec); cont['nuovi:' + b['tipo']] += 1
    # promozione dello staging «una sola fonte» di W5/W6 (Wikidata) con corrispondenza esatta Comic Vine = seconda fonte indipendente
    prom = 0
    for f in ('w5_staging', 'w6_staging'):
        for l in (E / 'staging' / (f + '.jsonl')).read_text().splitlines():
            r = json.loads(l)
            if 'una sola fonte' not in r.get('motivo', '') or not r.get('nome') or r.get('tipo') not in ('identita', 'organizzazione', 'evento'): continue
            ris = {'identita': 'characters', 'organizzazione': 'teams', 'evento': 'story_arcs'}[r['tipo']]
            x = cvx.get((ris, norm(base(r['nome']))))
            if not x or any(o['ids_esterni'].get('comicvine') == str(x['id']) for o in out): continue
            if any(c.get('ids_esterni', {}).get('wikidata') == r['q'] for c in canon): continue
            rid = nuovo_id(r['tipo'], r['nome'], x['id'])
            out.append({'id': rid, 'tipo': r['tipo'], 'nome': r['nome'], 'livello': 'C', 'stato_verifica': 'verificata', 'origine': 'W5c', 'universo': 'uni-earth-616', 'gruppi': ['cv:promozione'],
                        'ids_esterni': {'wikidata': r['q'], 'comicvine': str(x['id'])},
                        'fonti': [{'fonte': 'Wikidata', 'url': 'https://www.wikidata.org/wiki/' + r['q'], 'licenza': 'CC0'}, CVF({'u': x['u']})]})
            prom += 1
    cont['staging_promosse'] = prom
    (E / 'canon/w5_cv.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in out) + '\n')
    (E / 'staging/w5_cv_staging.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in stag) + ('\n' if stag else ''))
    json.dump(abb, open(E / 'cv_match.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'abbinati': len(abb), 'nuovi': len(out) - prom, 'promosse': prom, 'staging': len(stag), 'dettaglio': dict(cont)}, open(E / 'w5c_conteggi.json', 'w'), ensure_ascii=False, indent=1)
    print(dict(cont), 'abbinati', len(abb))
if '--scrivi' in sys.argv: scrivi(); sys.exit(0)
if __name__ == '__main__': main()
