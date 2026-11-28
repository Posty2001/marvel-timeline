#!/usr/bin/env python3
"""Relazioni narrative DOCUMENTATE (Wikidata CC0) -> registro `data/atlante/espansione/relazioni_db.json` + runtime `atlante2/data/db/rel.json` (letto dal TVA Nexus).
Regole: solo relazioni narrative (mai co-apparizioni ne' collegamenti editoriali); nodi solo via ID; entrambi gli estremi nel registro; continuita' diverse -> NON si importa come relazione
(resta in coda: puo' essere una controparte); gia' presenti in `data/atlante/relazioni.json` -> non duplicate. Verifica D12: 'verificata' solo se confermata anche da una SECONDA fonte indipendente
(parametri infobox MCU Wiki/Marvel Database nei fatti del canon), altrimenti 'da verificare' (mostrata come tale, esclusa di default dai percorsi).
Uso: python3 tools/db_rel_build.py <rel_wikidata.json> [--scrivi]"""
import json, sys, pathlib, re, collections, hashlib, urllib.parse
R = pathlib.Path(__file__).resolve().parent.parent; E = R / 'data/atlante/espansione'
# proprieta' -> (tipo, direzione, qualifica): 'in' = (da=target, a=sorgente), 'out' = (da=sorgente, a=target)
MAPPA = {'P22': ('famiglia_genitore', 'in', 'padre'), 'P25': ('famiglia_genitore', 'in', 'madre'), 'P40': ('famiglia_genitore', 'out', None), 'P26': ('famiglia_coniugi', 'sim', None),
         'P3373': ('famiglia_fratelli', 'sim', None), 'P451': ('partner', 'sim', None), 'P7047': ('rivalita', 'sim', None), 'P1066': ('mentorato', 'in', None), 'P802': ('mentorato', 'out', None),
         'P463': ('appartenenza', 'out', 'membro'), 'P1365': ('successione', 'out', None), 'P1366': ('successione', 'in', None)}
SIMM = {'famiglia_coniugi', 'famiglia_fratelli', 'partner', 'rivalita', 'alleanza', 'amicizia', 'controparte'}
CLASSE = {'controparte': 'controparte'}
def carica():
    reg = json.load(open(E / 'ids_registro.json'))['ids']
    q2id = {v['ids_esterni']['wikidata']: k for k, v in reg.items() if v.get('ids_esterni', {}).get('wikidata') and v.get('stato') != 'lapide'}
    for f in (E / 'canon').glob('*_arricchimenti.jsonl'):
        for l in f.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                if r.get('wikidata') and r['id'] in reg: q2id.setdefault(r['wikidata'], r['id'])
    canon = {}
    for f in sorted((E / 'canon').glob('w*_*.jsonl')):
        if 'arricchimenti' in f.name: continue
        for l in f.read_text().splitlines():
            if l.strip(): r = json.loads(l); canon[r['id']] = r
    return reg, q2id, canon
def costruisci(raw):
    reg, q2id, canon = carica()
    esist = json.load(open(R / 'data/atlante/relazioni.json'))['relazioni']
    paia = {frozenset((x['da'], x['a'])) for x in esist if x['classe'] != 'editoriale'}
    ident = {x['id']: x for x in json.load(open(R / 'data/atlante/identita.json'))['identita']}
    def uni(i): return canon[i].get('universo') if i in canon else (ident.get(i) or {}).get('universo')
    IDXN = {v['i']: v['n'] for v in json.load(open(R / 'atlante2/data/index.json'))['voci']}
    def nome(i): return canon[i]['nome'] if i in canon else IDXN.get(i) or (ident.get(i) or {}).get('nome') or i
    def testo_fatti(i):   # testo (normalizzato) dei parametri-fatto di relazione delle fonti wiki, per la seconda conferma
        f = (canon.get(i) or {}).get('fatti') or {}
        return ' | '.join(' '.join(v) if isinstance(v, list) else str(v) for k, v in f.items() if k in ('parenti', 'affiliazioni', 'membri', 'alias_fonte')).lower()
    out, stag, visti = [], [], set()
    cont = collections.Counter()
    for q, props in sorted(raw['entita'].items()):
        S = q2id.get(q)
        if not S: continue
        for p, targets in props.items():
            if p not in MAPPA: cont['proprieta ignorata ' + p] += len(targets); continue
            tipo, dire, qual = MAPPA[p]
            for tq in targets:
                T = q2id.get(tq)
                if not T: cont['bersaglio non nel registro'] += 1; continue
                if T == S: continue
                da, a = (T, S) if dire == 'in' else (S, T)
                if dire == 'sim' and da > a: da, a = a, da
                if tipo == 'appartenenza':
                    if a.startswith('id-') and da.startswith('id-') and uni(da) and uni(a) and uni(da) == uni(a): pass   # gruppo storicamente censito come identita' (es. X-Men), stessa continuita'
                    elif not (a.startswith('org-') and da.startswith('id-')): stag.append({'da': da, 'a': a, 'tipo': tipo, 'motivo': 'estremi non coerenti (serve identita -> organizzazione)'}); continue
                elif not (da.startswith('id-') and a.startswith('id-')): stag.append({'da': da, 'a': a, 'tipo': tipo, 'motivo': 'estremi non entrambi identita'}); continue
                k = (tipo, da, a)
                if k in visti: continue
                visti.add(k)
                if frozenset((da, a)) in paia: cont['gia nel registro'] += 1; continue
                ua, ub = uni(da), uni(a)
                if (tipo != 'appartenenza' or a.startswith('id-')) and ua and ub and ua != ub:
                    stag.append({'da': da, 'a': a, 'tipo': tipo, 'motivo': 'continuita diverse (%s / %s): non e una relazione narrativa unica, possibile controparte' % (ua, ub)}); continue
                conf = []
                if tipo == 'appartenenza': conf = ['x'] if nome(a).split('(')[0].strip().lower() in testo_fatti(da) else []
                else: conf = ['x'] if (nome(a).split('(')[0].strip().lower() in testo_fatti(da) or nome(da).split('(')[0].strip().lower() in testo_fatti(a)) else []
                ver = 'verificata' if conf else 'da verificare'
                rid = 'rel-db-' + hashlib.sha1('|'.join(k).encode()).hexdigest()[:10]
                out.append({'id': rid, 'tipo': tipo, 'classe': CLASSE.get(tipo, 'narrativa'), 'da': da, 'a': a, 'simmetrica': tipo in SIMM, 'qualifica': qual, 'fonte': ['https://www.wikidata.org/wiki/' + q] + (['parametri infobox MCU Wiki/Marvel Database (CC BY-SA 3.0)'] if conf else []),
                            'verifica': ver, 'origine': 'db:wikidata:' + p, 'controversa': False})
    # --- seconda via: parenti documentati nelle infobox (MCU Wiki / Marvel Database): solo nomi risolti in modo UNIVOCO nella stessa continuita' ---
    def nn(x): return re.sub(r'\s+', ' ', re.sub(r'\(.*?\)', ' ', x or '')).strip().lower()
    per_nome = collections.defaultdict(set)
    for i in list(canon) + list(ident): 
        if i.startswith('id-'): per_nome[nn(nome(i))].add(i)
    GEN = {'father': ('g', 'padre'), 'mother': ('g', 'madre'), 'son': ('f', 'figlio'), 'daughter': ('f', 'figlia'), 'adopted son': ('f', 'figlio adottivo'), 'adopted daughter': ('f', 'figlia adottiva'),
           'husband': ('s', None), 'wife': ('s', None), 'brother': ('b', None), 'sister': ('b', None), 'ex-wife': None, 'ex-husband': None}
    for S, rec in sorted(canon.items()):
        if not S.startswith('id-'): continue
        for par in ((rec.get('fatti') or {}).get('parenti') or []):
            m = re.match(r'^(.*?)\s*\(([^)]*)\)\s*$', par)
            if not m: continue
            rel = re.split(r'[,;]', m.group(2))[0].strip().lower(); g_ = GEN.get(rel)
            if not g_: cont['parente non mappato'] += 1; continue
            cand = {c for c in per_nome.get(nn(m.group(1)), ()) if c != S and (uni(c) == uni(S) or not uni(c) or not uni(S))}
            if len(cand) != 1: cont['parente non univoco/assente'] += 1; continue
            T = next(iter(cand)); kind, qual = g_
            if kind == 'g': tipo, da, a = 'famiglia_genitore', T, S
            elif kind == 'f': tipo, da, a = 'famiglia_genitore', S, T
            elif kind == 's': tipo, da, a = 'famiglia_coniugi', min(S, T), max(S, T)
            else: tipo, da, a = 'famiglia_fratelli', min(S, T), max(S, T)
            if frozenset((da, a)) in paia: cont['parente gia presente'] += 1; continue
            ex = [x for x in out if x['tipo'] == tipo and {x['da'], x['a']} == {da, a}]
            if ex:
                if ex[0]['verifica'] != 'verificata': ex[0]['verifica'] = 'verificata'; ex[0]['fonte'].append('parametro "parenti" infobox MCU Wiki/Marvel Database (CC BY-SA 3.0)')
                cont['parente confermato (seconda fonte)'] += 1; continue
            k = (tipo, da, a)
            if k in visti: continue
            visti.add(k)
            rid = 'rel-db-' + hashlib.sha1('|'.join(k).encode()).hexdigest()[:10]
            out.append({'id': rid, 'tipo': tipo, 'classe': 'narrativa', 'da': da, 'a': a, 'simmetrica': tipo in SIMM, 'qualifica': qual, 'fonte': ['parametro "parenti" infobox MCU Wiki/Marvel Database (CC BY-SA 3.0)'],
                        'verifica': 'da verificare', 'origine': 'db:infobox:parenti', 'controversa': False})
    # --- terza via: alleati, avversari e appartenenze citati dalle infobox (UNA sola fonte: restano «da verificare»; mai verificate automaticamente senza seconda fonte) ---
    org_nome = collections.defaultdict(set)
    for i in list(canon) + list(ident):
        if i.startswith(('org-', 'id-')): org_nome[nn(nome(i))].add(i)
    VIA = (('alleati', 'alleanza', 'alleato'), ('nemici', 'rivalita', 'avversario'))
    for S, rec in sorted(canon.items()):
        if not S.startswith('id-'): continue
        f_ = rec.get('fatti') or {}
        for chiave, tipo, qual in VIA:
            for nm in ((f_.get('relazioni_fonte') or {}).get(chiave) or []):
                T = re.sub(r'\s*\([^)]*\)\s*$', '', nm).strip()
                cand = {c for c in per_nome.get(nn(T), ()) if c != S and uni(c) and uni(S) and uni(c) == uni(S)}
                if len(cand) != 1: cont['%s non univoco/assente' % chiave] += 1; continue
                U_ = next(iter(cand)); da, a = (min(S, U_), max(S, U_))
                if frozenset((da, a)) in paia: cont['%s gia nel registro' % chiave] += 1; continue
                k = (tipo, da, a)
                if k in visti or any(x['tipo'] == tipo and {x['da'], x['a']} == {da, a} for x in out if x['origine'].startswith('db:infobox')): continue
                visti.add(k)
                out.append({'id': 'rel-db-' + hashlib.sha1('|'.join(k).encode()).hexdigest()[:10], 'tipo': tipo, 'classe': 'narrativa', 'da': da, 'a': a, 'simmetrica': True, 'qualifica': None,
                            'fonte': ['parametro "%s" infobox MCU Wiki/Marvel Database (CC BY-SA 3.0), una sola fonte' % ('allies' if chiave == 'alleati' else 'enemies')], 'verifica': 'da verificare', 'origine': 'db:infobox:' + chiave, 'controversa': False})
        for nm in (f_.get('affiliazioni') or []):
            T = re.sub(r'\s*\([^)]*\)\s*$', '', nm).strip()
            cand = {c for c in org_nome.get(nn(T), ()) if c != S and (c.startswith('org-') or c.startswith('id-')) and uni(c) and uni(S) and uni(c) == uni(S)}
            if len(cand) != 1: cont['affiliazioni non univoco/assente'] += 1; continue
            U_ = next(iter(cand)); k = ('appartenenza', S, U_)
            if frozenset((S, U_)) in paia or k in visti or any(x['tipo'] == 'appartenenza' and x['da'] == S and x['a'] == U_ for x in out): continue
            if not (U_.startswith('org-') or (U_.startswith('id-') and 'x-men' in U_ or U_.startswith('id-') and U_ != S and not nn(nome(U_)) == nn(nome(S)) and (canon.get(U_, {}).get('fatti', {}) or {}).get('membri'))): continue
            visti.add(k)
            out.append({'id': 'rel-db-' + hashlib.sha1('|'.join(k).encode()).hexdigest()[:10], 'tipo': 'appartenenza', 'classe': 'narrativa', 'da': S, 'a': U_, 'simmetrica': False, 'qualifica': 'membro',
                        'fonte': ['parametro "affiliation" infobox MCU Wiki/Marvel Database (CC BY-SA 3.0), una sola fonte'], 'verifica': 'da verificare', 'origine': 'db:infobox:affiliazioni', 'controversa': False})
    # --- controparti: variante (Marvel Database «Nome (Earth-N)» + seconda fonte) <-> identita' base; classe separata, mai relazione narrativa ---
    for S, rec in sorted(canon.items()):
        for g in rec.get('gruppi', []):
            if g.startswith('base:') and rec['tipo'] == 'variante':
                B_ = g[5:]; da, a = min(S, B_), max(S, B_); k = ('controparte', da, a)
                if k in visti: continue
                visti.add(k)
                out.append({'id': 'rel-db-' + hashlib.sha1('|'.join(k).encode()).hexdigest()[:10], 'tipo': 'controparte', 'classe': 'controparte', 'da': da, 'a': a, 'simmetrica': True, 'qualifica': 'variante',
                            'fonte': ['Marvel Database (CC BY-SA 3.0): pagina «Nome (Earth-N)» + seconda fonte indipendente della voce'], 'verifica': 'verificata', 'origine': 'db:w8:variante', 'controversa': False})
    for x in out:   # metodo di verifica: SEMPRE esplicito (le verifiche automatiche non sono verifiche documentali effettive)
        x['metodo'] = ('automatica: Wikidata + riscontro relazionale direzionale (Wikipedia)' if x['verifica'] == 'verificata' and any('Wikipedia' in f for f in x['fonte']) else
                       ('automatica: nome della pagina + seconda fonte della voce' if x['classe'] == 'controparte' else 'automatica: Wikidata + parametro infobox') if x['verifica'] == 'verificata' else 'nessuna verifica (una sola fonte)')
    return {'versione': 1, 'fonte': 'Wikidata CC0 (+ seconda fonte dove indicata)', 'relazioni': out, 'staging': stag, 'conteggi': dict(cont) | {'relazioni': len(out), 'verificate': sum(1 for x in out if x['verifica'] == 'verificata'), 'staging': len(stag)}}
def wp_titolo(rec):
    for f in (rec or {}).get('fonti', []):
        if f.get('fonte', '').startswith('Wikipedia') and '/wiki/' in f.get('url', ''): return urllib.parse.unquote(f['url'].split('/wiki/', 1)[1]).replace('_', ' ')
    return None
def input_verifica(g):
    """Input per tools/db_relverify.py (seconda fonte Wikipedia): per ogni relazione da verificare, titoli Wikipedia e nomi distintivi dei due estremi."""
    reg, q2id, canon = carica(); ident = {x['id']: x for x in json.load(open(R / 'data/atlante/identita.json'))['identita']}
    IDXN = {v['i']: v['n'] for v in json.load(open(R / 'atlante2/data/index.json'))['voci']}
    def nomi(i):
        if i in canon: return [canon[i]['nome']] + canon[i].get('alias', [])[:6]
        x = ident.get(i) or {}; nm = IDXN.get(i) or x.get('nome') or i; return [p for p in re.split(r'/| - ', re.sub(r'\(.*?\)', ' ', nm)) if p.strip()] + x.get('alias', [])[:6]
    def wp(i):
        t = wp_titolo(canon.get(i))
        if t: return t
        if i in canon: return None
        x = ident.get(i) or {}; return None   # le voci storiche non hanno titolo Wikipedia verificato: nessun tentativo per nome (evita omonimi)
    out = []
    for x in g['relazioni']:
        if x['verifica'] == 'verificata': continue
        out.append({'id': x['id'], 'tipo': x['tipo'], 'da_wp': wp(x['da']), 'a_wp': wp(x['a']), 'da_nomi': nomi(x['da']), 'a_nomi': nomi(x['a'])})
    return {'versione': 1, 'relazioni': [o for o in out if o['da_wp'] or o['a_wp']]}
def applica_verifica(g, ver):
    n = 0
    for x in g['relazioni']:
        v = (ver or {}).get(x['id'])
        if x['verifica'] != 'verificata' and v and v.get('ok'):
            x['verifica'] = 'verificata'; x['fonte'].append('Wikipedia (CC BY-SA 4.0), riscontro relazionale direzionale: ' + v['url']); n += 1
    return n
def runtime(g):
    tipi = sorted({x['tipo'] for x in g['relazioni']}); V = {'verificata': 2, 'da verificare': 0}
    rows = [[x['da'], x['a'], tipi.index(x['tipo']), 'c' if x['classe'] == 'controparte' else 'n', V[x['verifica']], x['qualifica'] or '', 0] for x in g['relazioni']]
    return {'v': 1, 'tipi': tipi, 'r': rows}
def main():
    raw = json.load(open(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else str(R / 'data/atlante/espansione/raw/rel_wikidata.json'))); g = costruisci(raw)
    vf = R / 'data/atlante/espansione/raw/relverify2.json'
    if vf.exists(): g['conteggi']['confermate_wikipedia'] = applica_verifica(g, json.load(open(vf))['esiti']); g['conteggi']['verificate'] = sum(1 for x in g['relazioni'] if x['verifica'] == 'verificata')
    print(json.dumps(g['conteggi'], ensure_ascii=False, indent=1))
    if '--input-verifica' in sys.argv:
        (R / 'data/atlante/espansione/relverify_input.json').write_text(json.dumps(input_verifica(g), ensure_ascii=False, separators=(',', ':')) + '\n'); print('scritto relverify_input.json')
    if '--scrivi' in sys.argv:
        (E / 'relazioni_db.json').write_text(json.dumps(g, ensure_ascii=False, indent=1) + '\n')
        (R / 'atlante2/data/db').mkdir(parents=True, exist_ok=True)
        (R / 'atlante2/data/db/rel.json').write_text(json.dumps(runtime(g), ensure_ascii=False, separators=(',', ':')) + '\n'); print('scritto relazioni_db.json e rel.json')
if __name__ == '__main__': main()
