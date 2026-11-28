#!/usr/bin/env python3
"""W9 (chiusura Database Expansion, 28/11): (1) deroga D12 controllata per varianti e universi; (2) correzione delle classificazioni editoriali; (3) fusione dei duplicati con lapide.
Tre stati: «verificata» (>=2 fonti indipendenti), «documentata-fonte-singola» (una fonte attendibile con identita', universo e continuita' documentati; MAI XP/completamenti),
«da-verificare» (casi ambigui: restano in staging). Idempotente. Uso: python3 tools/db_w9_chiusura.py [--scrivi]"""
import json, pathlib, re, sys, collections, hashlib
R = pathlib.Path(__file__).resolve().parent.parent; E = R / 'data/atlante/espansione'
PAT = re.compile(r'^(.*) \((Earth-\d+)\)$'); BASE = lambda n: re.sub(r'\s*\([^)]*\)\s*$', '', n or '').strip()
SOGLIA_UNI = 5      # un'Earth-N e' «continuita' documentata» se ha pagine di >= 5 identita' distinte
TETTO_BASE = 12     # prudenza editoriale: al massimo 12 varianti per identita' base (le piu' documentate)
FUSIONI = {'cos-doctor-doom': 'id-doctor-doom', 'cos-hogun': 'id-hogun', 'cos-surtur': 'id-surtur'}   # stessa entita': scheda unica (ID cos-* ritirato con lapide)
LUOGHI = {'cos-knowhere'}                                         # un luogo, non un'entita'
COSMICA = re.compile(r'abstract|celestial|cosmic force|cosmic being|deities|sky lords', re.I)
COLLETTIVI = {'cos-celestials', 'cos-proemial-gods'}
def leggi(p): return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []
def scrivi_righe(p, rows): p.write_text('\n'.join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in rows) + ('\n' if rows else ''))
def categorie(r):
    f = r.get('fatti') or {}; t = ' '.join(str(x) for k in ('origine', 'occupazione', 'specie', 'affiliazioni') for x in (f.get(k) if isinstance(f.get(k), list) else [f.get(k) or '']))
    c = ['personaggio']
    if re.search(r'demon|arch-demon', t, re.I): c.append('demone')
    if re.search(r'\bgod\b|deit|goddess', t, re.I): c.append('divinita')
    if COSMICA.search(t) and 'former' not in t.lower(): c.append('entita-cosmica')
    return c
def main():
    scrivi = '--scrivi' in sys.argv; log = collections.Counter()
    files = [f for f in sorted((E / 'canon').glob('w*_*.jsonl')) if 'arricchimenti' not in f.name and f.name != 'w9_deroga.jsonl']
    # --- 1) classificazione + fusione duplicati
    arr_new = []; lapidi = {}
    for f in files:
        rows = leggi(f); out = []
        for r in rows:
            if r['id'] in FUSIONI:
                lapidi[r['id']] = FUSIONI[r['id']]; log['fusi (scheda unica)'] += 1
                arr_new.append({'id': FUSIONI[r['id']], 'alias_nuovi': [], 'fonte': 'Wikidata (CC0)', 'interpreti': [], 'wikidata': (r.get('ids_esterni') or {}).get('wikidata')}); continue
            if r['tipo'] == 'entita-cosmica':
                if r['id'] in LUOGHI: r['tipo'] = 'luogo'; r['categorie'] = ['luogo']; log['riclassificati -> luogo'] += 1
                elif r['id'] in COLLETTIVI or COSMICA.search(str((r.get('fatti') or {}).get('origine', ''))) and 'former' not in str((r.get('fatti') or {}).get('origine', '')).lower():
                    r['categorie'] = sorted(set(categorie(r)) - {'personaggio'} | {'entita-cosmica'}) if r['id'] in COLLETTIVI else categorie(r); log['restano entita-cosmica'] += 1
                else: r['tipo'] = 'identita'; r['categorie'] = categorie(r); log['riclassificati -> identita'] += 1
            out.append(r)
        if scrivi and out != rows: scrivi_righe(f, out)
    # arricchimenti di fusione: nessun duplicato
    ap = E / 'canon/w9_arricchimenti.jsonl'; ex = {a['id']: a for a in leggi(ap)}
    for a in arr_new: ex.setdefault(a['id'], a)
    # --- 2) deroga D12 su staging w8
    canon = {}
    for f in sorted((E / 'canon').glob('*.jsonl')):
        if 'arricchimenti' in f.name: continue
        for r in leggi(f): canon.setdefault(r['id'], r)
    stp = E / 'staging/w8_staging.jsonl'; st = leggi(stp)
    V = [s for s in st if s['tipo'] == 'variante']; U = [s for s in st if s['tipo'] == 'universo']
    base_per_uni = collections.defaultdict(set)
    for v in V: base_per_uni[PAT.match(v['nome']).group(2)].add(v['base'])
    uni_pag = {u['nome']: u for u in U if re.fullmatch(r'Earth-\d+', u['nome'])}
    uni_canon = {}
    for i, r in canon.items():
        m = re.match(r'uni-earth-(\d+)', i)
        if r['tipo'] == 'universo' and m: uni_canon['Earth-' + m.group(1)] = i
    cand = []; resto = []
    for v in V:
        b = canon.get(v['base']); m = PAT.match(v['nome']); e = m.group(2) if m else None
        stem_ok = b and e and BASE(b['nome']).lower() == m.group(1).strip().lower()
        ok = (stem_ok and b['tipo'] == 'identita' and b.get('livello') in ('A', 'B') and (e in uni_pag or e in uni_canon)
              and len(base_per_uni[e]) >= SOGLIA_UNI and e != 'Earth-616' and (b.get('universo') or '') != uni_canon.get(e) and v['nome'].lower() not in {x['nome'].lower() for x in canon.values()})
        (cand if ok else resto).append((v, b, e) if ok else v)
    per_base = collections.defaultdict(list)
    for v, b, e in cand: per_base[v['base']].append((len(base_per_uni[e]), e, v, b))
    scelte = []
    for bid, l in per_base.items():
        for n, e, v, b in sorted(l, key=lambda x: (-x[0], int(x[1].split('-')[1])))[:TETTO_BASE]: scelte.append((v, b, e))
    scelti = {id(v) for v, _, _ in scelte}
    for v, b, e in cand:
        if id(v) not in scelti: resto.append(v)
    nuovi = []; usati = set(canon)
    uni_nuove = {}
    def fonte(t): return [{'fonte': 'Marvel Database', 'url': 'https://marvel.fandom.com/wiki/' + t.replace(' ', '_'), 'licenza': 'CC BY-SA 3.0'}]
    for v, b, e in sorted(scelte, key=lambda x: x[0]['nome']):
        uid = uni_canon.get(e) or 'uni-' + e.lower()
        if e not in uni_canon and uid not in uni_nuove:
            uni_nuove[uid] = {'id': uid, 'tipo': 'universo', 'nome': e, 'livello': 'C', 'stato_verifica': 'documentata-fonte-singola', 'origine': 'W9', 'gruppi': ['w9-deroga'], 'ids_esterni': {'marveldb': e},
                              'fonti': fonte(e), 'continuita_nota': 'Continuità «%s» documentata da una sola fonte (Marvel Database): pagine di %d identità distinte. Non verificata da una seconda fonte indipendente.' % (e, len(base_per_uni[e]))}
        vid = 'var-' + re.sub(r'[^a-z0-9]+', '-', v['nome'].lower()).strip('-')
        if vid in usati: vid += '-' + hashlib.sha1(v['nome'].encode()).hexdigest()[:5]
        usati.add(vid)
        nuovi.append({'id': vid, 'tipo': 'variante', 'nome': v['nome'], 'livello': 'C', 'stato_verifica': 'documentata-fonte-singola', 'origine': 'W9', 'gruppi': ['w9-deroga'], 'universo': uid, 'variante_di': b['id'],
                      'ids_esterni': {'marveldb': v['nome']}, 'fonti': fonte(v['nome']),
                      'continuita_nota': 'Variante di «%s» nella continuità %s, documentata da una sola fonte (Marvel Database). Non verificata da una seconda fonte indipendente; non conta per progressione e completamenti.' % (b['nome'], e)})
    nuovi = list(uni_nuove.values()) + nuovi; uni_nuove_nomi = {u['nome'] for u in uni_nuove.values()}
    for u in U:
        if u['nome'] in uni_nuove_nomi: continue
        resto.append(u)
    for r in resto: r['stato'] = 'da-verificare'
    log['varianti promosse (fonte singola)'] = len(scelte); log['universi promossi (fonte singola)'] = len(uni_nuove); log['varianti restate in staging'] = sum(1 for r in resto if r['tipo'] == 'variante')
    log['universi restati in staging'] = len(U) - len(uni_nuove); log['staging: stato da-verificare'] = len(resto)
    print(json.dumps(dict(log), ensure_ascii=False, indent=1))
    if not scrivi: return
    scrivi_righe(E / 'canon/w9_deroga.jsonl', nuovi); scrivi_righe(ap, list(ex.values()))
    scrivi_righe(stp, [s for s in st if s['tipo'] not in ('variante', 'universo')] + resto)
    rp = E / 'ids_registro.json'; rg = json.load(open(rp))
    for k, v in lapidi.items():
        if k in rg['ids']: rg['ids'][k]['stato'] = 'lapide'; rg['ids'][k]['verso'] = v
    rg['ids_sha256'] = hashlib.sha256('\n'.join(sorted(rg['ids'])).encode()).hexdigest(); json.dump(rg, open(rp, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    # relazioni db: i riferimenti agli ID fusi vengono riportati sulla scheda unica
    rl = json.load(open(E / 'relazioni_db.json')); n = 0
    for x in rl['relazioni']:
        for k in ('da', 'a'):
            if x[k] in lapidi: x[k] = lapidi[x[k]]; n += 1
    json.dump(rl, open(E / 'relazioni_db.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True); print('relazioni riportate sulle schede uniche:', n)
if __name__ == '__main__': main()
