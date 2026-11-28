#!/usr/bin/env python3
"""Dossier discorsivi in ITALIANO (livello A) generati ESCLUSIVAMENTE da fatti verificati del canon: nessun testo copiato dalle fonti, nessuna informazione aggiunta, nessuna IA a pagamento.
Frasi originali costruite da modelli fissi; i termini tecnici non tradotti (poteri, ruoli, titoli) restano nella lingua originale tra virgolette. Un dossier si genera solo se ci sono almeno 3 sezioni con dati.
Selezione dei «personaggi principali»: identita' di Livello B + identita' con >= 3 relazioni narrative verificate oppure ordinate tra le prime fasce di rilevanza (fumetti 40+/20-40 collegamenti Wikipedia).
Uso: python3 tools/db_dossier.py [--scrivi]  ->  data/atlante/espansione/dossier_it.json"""
import json, pathlib, re, sys, collections
R = pathlib.Path(__file__).resolve().parent.parent; E = R/'data/atlante/espansione'
GEN = {'male': 'maschile', 'female': 'femminile'}
STATO = {'alive': 'in vita', 'deceased': 'deceduto', 'dead': 'deceduto', 'unknown': 'di stato non noto', 'living': 'in vita'}
REL = {'famiglia_genitore': ('genitore di', 'figlio/a di'), 'famiglia_coniugi': ('coniuge di', 'coniuge di'), 'famiglia_fratelli': ('fratello/sorella di', 'fratello/sorella di'),
       'partner': ('partner di', 'partner di'), 'rivalita': ('rivale di', 'rivale di'), 'mentorato': ('mentore di', 'allievo/a di'), 'appartenenza': ('membro di', 'ha tra i membri')}
def lista(v, n=8):
    v = [x for x in dict.fromkeys(v) if x][:n]
    return ', '.join('«%s»' % x for x in v)
def pulisci(x): return re.sub(r'\s+', ' ', x or '').strip()
def U(v):   # valore -> lista di stringhe
    if v is None: return []
    return [x for x in (v if isinstance(v, list) else re.split(r'\s*;\s*', str(v))) if x]
def pick(r, *alt):   # variante di frase deterministica (evita testi tutti uguali senza inventare nulla)
    return alt[sum(map(ord, r['id'])) % len(alt)]
def componi(r, rels, nomi, altre=None, uni=None, cvn=None):
    f = r.get('fatti', {}); S = []; usati = set(); nome = r['nome']
    def u(*k): usati.update(x for x in k if f.get(x)); return [y for x in k for y in U(f.get(x))]
    # 1) Sintesi
    t = []
    cont = (uni or {}).get(r.get('universo') or '')
    t.append(pick(r, '%s è un personaggio%s.', '%s compare come personaggio%s.', 'La scheda riguarda %s, personaggio%s.') % (nome, (' della continuità «%s»' % cont) if cont else ''))
    cr = u('creatori_fonte')
    if cr: t.append('Secondo le fonti consultate è stato creato da %s.' % lista(cr, 4))
    pa = u('prima_apparizione')
    if pa: t.append('La prima apparizione documentata è %s.' % lista(pa, 2))
    if cvn: t.append('Su Comic Vine risulta in circa %d albi.' % cvn)
    d = (r.get('descrizione') or {}).get('it')
    if d: usati.add('descrizione'); t.append('Descrizione di riferimento (Wikidata, CC0): %s.' % pulisci(d).rstrip('.'))
    if len(t) > 1: S.append(('Sintesi', ' '.join(t)))
    # 2) Origini e identita'
    o = []
    if f.get('nome_reale'): o.append('Nome reale o di nascita: %s.' % ', '.join(u('nome_reale')))
    if f.get('genere') and str(f['genere']).lower() in GEN: usati.add('genere'); o.append('Genere: %s.' % GEN[str(f['genere']).lower()])
    if f.get('nascita'): o.append('Dati di nascita riportati: %s.' % '; '.join(u('nascita')))
    if f.get('origine'): o.append('Origine dei poteri o della condizione: %s.' % lista(u('origine'), 3))
    if f.get('specie'): o.append('Specie o razza: %s.' % lista(u('specie'), 3))
    if f.get('cittadinanza'): o.append('Cittadinanza: %s.' % lista(u('cittadinanza'), 4))
    if f.get('occupazione'): o.append('Occupazioni documentate: %s.' % lista(u('occupazione'), 6))
    if o: S.append(('Origini e identità', ' '.join(o)))
    # 3) Vicende essenziali (solo dati: stato, luoghi, morte)
    v = []
    if f.get('stato') and str(f['stato']).lower() in STATO: usati.add('stato'); v.append('Stato attuale secondo le fonti: %s.' % STATO[str(f['stato']).lower()])
    if f.get('morte'): v.append('Dati sulla morte riportati: %s.' % '; '.join(u('morte')))
    if f.get('ubicazione'): v.append('Luoghi e basi collegati: %s.' % lista(u('ubicazione'), 5))
    if f.get('affiliazioni'): v.append('Organizzazioni e gruppi di appartenenza citati: %s.' % lista(u('affiliazioni'), 10))
    if v: S.append(('Affiliazioni, luoghi e vicende', ' '.join(v)))
    # 4) Poteri e abilita'
    pa = []
    if f.get('poteri'): pa.append('Poteri documentati: %s.' % lista(u('poteri'), 12))
    if f.get('abilita'): pa.append('Abilità: %s.' % lista(u('abilita'), 12))
    if pa: S.append(('Poteri e abilità', ' '.join(pa)))
    # 5) Equipaggiamento e debolezze
    eq = []
    if f.get('equipaggiamento'): eq.append('Equipaggiamento, armi e mezzi: %s.' % lista(u('equipaggiamento'), 10))
    if f.get('debolezze'): eq.append('Debolezze: %s.' % lista(u('debolezze'), 8))
    if eq: S.append(('Equipaggiamento e debolezze', ' '.join(eq)))
    # 6) Trasformazioni, alias e altre continuita'
    tr = []
    if f.get('alias_fonte') or r.get('alias'): tr.append('Identità e nomi alternativi: %s.' % lista(list(dict.fromkeys(u('alias_fonte') + (r.get('alias') or []))), 10))
    if altre: tr.append('Il nome compare anche in altre continuità dell\'Atlante: %s (voci distinte, mai unificate).' % lista(altre, 8))
    if tr: S.append(('Identità alternative e continuità', ' '.join(tr)))
    # 7) Relazioni: verificate (separate) e indicate dalle fonti (non verificate singolarmente)
    rl = []
    for t_, da, a in rels:
        ver, inv = REL.get(t_, (None, None))
        if not ver: continue
        altro = nomi.get(a if da == r['id'] else da)
        if altro: rl.append('%s %s' % (ver if da == r['id'] else inv, altro))
    rr = []
    if rl: rr.append('Relazioni narrative verificate: %s è %s.' % (nome, '; '.join(dict.fromkeys(rl[:10]))))
    rf = f.get('relazioni_fonte') or {}
    if rf: usati.add('relazioni_fonte')
    for k, lab in (('parenti', 'Familiari indicati dalle fonti'), ('alleati', 'Alleati indicati dalle fonti'), ('nemici', 'Avversari indicati dalle fonti')):
        l = rf.get(k) or (f.get('parenti') if k == 'parenti' else None)
        if l: usati.add(k); rr.append('%s (non verificati individualmente): %s.' % (lab, lista(l, 8)))
    if rr: S.append(('Relazioni', ' '.join(rr)))
    # 8) Interpreti e apparizioni
    ap = []
    ip = r.get('interpreti') or u('interpreti_fonte')
    if ip: ap.append('Interpretato da %s.' % ', '.join(dict.fromkeys(ip)))
    for k, lab in (('apparizioni_narrativa', 'nella continuità narrativa'), ('apparizioni_alternativi', 'in universi alternativi'), ('apparizioni_fumetti', 'nei fumetti'), ('apparizioni_videogiochi', 'nei videogiochi'), ('apparizioni_adattamenti', 'in adattamenti')):
        if f.get(k): usati.add(k); ap.append('Apparizioni %s (esempi): %s.' % (lab, lista(f[k], 5)))
    if ap: S.append(('Interpreti e apparizioni', ' '.join(ap)))
    return S, len(usati)
def main():
    rels = collections.defaultdict(list); nomi = {}
    for x in json.load(open(E/'relazioni_db.json'))['relazioni']:
        if x['verifica'] == 'verificata' and x['classe'] == 'narrativa': rels[x['da']].append((x['tipo'], x['da'], x['a'])); rels[x['a']].append((x['tipo'], x['da'], x['a']))
    canon = {}
    for f in sorted((E/'canon').glob('w*_*.jsonl')):
        if 'arricch' in f.name: continue
        for l in f.read_text().splitlines():
            if l.strip(): r = json.loads(l); canon.setdefault(r['id'], r)
    idxj = json.load(open(R/'atlante2/data/index.json')); idx = {v['i']: v['n'] for v in idxj['voci']}
    uni = {k: v['n'] for k, v in idxj['meta']['universi'].items()}
    for i, r in canon.items():
        nomi[i] = r['nome']
        if r['tipo'] == 'universo': uni.setdefault(i, r['nome'])
    for i, n in idx.items(): nomi.setdefault(i, n)
    base = lambda n: re.sub(r'\s*\([^)]*\)\s*$', '', n).strip().lower()
    per_nome = collections.defaultdict(list)
    for v in idxj['voci']:
        if v['t'] == 'p': per_nome[base(v['n'])].append((v['i'], uni.get(v.get('u') or '', '')))
    for i, r in canon.items():
        if r['tipo'] == 'identita': per_nome[base(r['nome'])].append((i, uni.get(r.get('universo') or '', '')))
    cv = {}
    try:
        cvm = {x['id']: x['cv'] for x in json.load(open(E/'cv_match.json'))}
        cvd = {x['id']: x.get('c') for x in json.load(open(E/'raw/cv2_marvel.json'))['risorse']['characters']}
        cv = {i: cvd.get(c) for i, c in cvm.items() if cvd.get(c)}
    except Exception: pass
    for r in canon.values():   # voci nate da Comic Vine: ID in ids_esterni
        try:
            c = int(r['ids_esterni'].get('comicvine') or 0)
            if c and r['tipo'] == 'identita' and r['id'] not in cv: cv[r['id']] = cvd.get(c)
        except Exception: pass
    out = {}; liv = {}; stat = collections.Counter()
    for i, r in canon.items():
        if r['tipo'] != 'identita': continue
        top = r.get('livello') == 'B' or len(rels.get(i, [])) >= 3 or any(g.startswith(('fumetti:40', 'fumetti:20-40', 'fumetti:12-20', 'fumetti_pubbl:40', 'fumetti_pubbl:20-40')) for g in r.get('gruppi', [])) or (cv.get(i) or 0) >= 150
        if not top: continue
        altre = sorted({u for j, u in per_nome.get(base(r['nome']), []) if j != i and u})
        S, nf = componi(r, rels.get(i, []), nomi, altre, uni, cv.get(i))
        if len(S) < 3: continue
        car = sum(len(x) for _, x in S); nver = len(rels.get(i, []))
        q = 'A' if (len(S) >= 6 and car >= 900 and nf >= 10 and (nver >= 1 or len(r.get('fonti', [])) >= 3)) else ('B' if (len(S) >= 4 and car >= 450 and nf >= 6) else 'C')
        out[i] = {'sezioni': [{'t': t, 'x': x} for t, x in S], 'q': {'sezioni': len(S), 'caratteri': car, 'campi': nf, 'relazioni_verificate': nver}, 'generato': 'da fatti verificati del canon (nessun testo copiato)'}
        stat[q] += 1
        if q in ('A', 'B') and r.get('livello') != 'A': liv[i] = q
    print(json.dumps({'dossier': len(out), 'qualita': dict(stat), 'promozioni': len(liv), 'identita': sum(1 for r in canon.values() if r['tipo'] == 'identita')}))
    if '--scrivi' in sys.argv:
        (E/'dossier_it.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
        (E/'livelli_w8.json').write_text(json.dumps({'regola': 'A: >=6 sezioni, >=900 car., >=10 campi-fatto, >=1 relazione verificata o >=3 fonti; B: >=4 sezioni, >=450 car., >=6 campi', 'livelli': liv}, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
    return out
if __name__ == '__main__':
    o = main()
    for k in list(o)[:1]: print(json.dumps(o[k], ensure_ascii=False, indent=1)[:2500])
