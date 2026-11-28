#!/usr/bin/env python3
"""Relazioni narrative DOCUMENTATE (Wikidata CC0) -> registro `data/atlante/espansione/relazioni_db.json` + runtime `atlante2/data/db/rel.json` (letto dal TVA Nexus).
Regole: solo relazioni narrative (mai co-apparizioni ne' collegamenti editoriali); nodi solo via ID; entrambi gli estremi nel registro; continuita' diverse -> NON si importa come relazione
(resta in coda: puo' essere una controparte); gia' presenti in `data/atlante/relazioni.json` -> non duplicate. Verifica D12: 'verificata' solo se confermata anche da una SECONDA fonte indipendente
(parametri infobox MCU Wiki/Marvel Database nei fatti del canon), altrimenti 'da verificare' (mostrata come tale, esclusa di default dai percorsi).
Uso: python3 tools/db_rel_build.py <rel_wikidata.json> [--scrivi]"""
import json, sys, pathlib, re, collections, hashlib
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
                    if not (a.startswith('org-') and da.startswith('id-')): stag.append({'da': da, 'a': a, 'tipo': tipo, 'motivo': 'estremi non coerenti (serve identita -> organizzazione)'}); continue
                elif not (da.startswith('id-') and a.startswith('id-')): stag.append({'da': da, 'a': a, 'tipo': tipo, 'motivo': 'estremi non entrambi identita'}); continue
                k = (tipo, da, a)
                if k in visti: continue
                visti.add(k)
                if frozenset((da, a)) in paia: cont['gia nel registro'] += 1; continue
                ua, ub = uni(da), uni(a)
                if tipo != 'appartenenza' and ua and ub and ua != ub:
                    stag.append({'da': da, 'a': a, 'tipo': tipo, 'motivo': 'continuita diverse (%s / %s): non e una relazione narrativa unica, possibile controparte' % (ua, ub)}); continue
                conf = []
                if tipo == 'appartenenza': conf = ['x'] if nome(a).split('(')[0].strip().lower() in testo_fatti(da) else []
                else: conf = ['x'] if (nome(a).split('(')[0].strip().lower() in testo_fatti(da) or nome(da).split('(')[0].strip().lower() in testo_fatti(a)) else []
                ver = 'verificata' if conf else 'da verificare'
                rid = 'rel-db-' + hashlib.sha1('|'.join(k).encode()).hexdigest()[:10]
                out.append({'id': rid, 'tipo': tipo, 'classe': CLASSE.get(tipo, 'narrativa'), 'da': da, 'a': a, 'simmetrica': tipo in SIMM, 'qualifica': qual, 'fonte': ['https://www.wikidata.org/wiki/' + q] + (['parametri infobox MCU Wiki/Marvel Database (CC BY-SA 3.0)'] if conf else []),
                            'verifica': ver, 'origine': 'db:wikidata:' + p, 'controversa': False})
    return {'versione': 1, 'fonte': 'Wikidata CC0 (+ seconda fonte dove indicata)', 'relazioni': out, 'staging': stag, 'conteggi': dict(cont) | {'relazioni': len(out), 'verificate': sum(1 for x in out if x['verifica'] == 'verificata'), 'staging': len(stag)}}
def runtime(g):
    tipi = sorted({x['tipo'] for x in g['relazioni']}); V = {'verificata': 2, 'da verificare': 0}
    rows = [[x['da'], x['a'], tipi.index(x['tipo']), 'c' if x['classe'] == 'controparte' else 'n', V[x['verifica']], x['qualifica'] or '', 0] for x in g['relazioni']]
    return {'v': 1, 'tipi': tipi, 'r': rows}
def main():
    raw = json.load(open(sys.argv[1])); g = costruisci(raw)
    print(json.dumps(g['conteggi'], ensure_ascii=False, indent=1))
    if '--scrivi' in sys.argv:
        (E / 'relazioni_db.json').write_text(json.dumps(g, ensure_ascii=False, indent=1) + '\n')
        (R / 'atlante2/data/db').mkdir(parents=True, exist_ok=True)
        (R / 'atlante2/data/db/rel.json').write_text(json.dumps(runtime(g), ensure_ascii=False, separators=(',', ':')) + '\n'); print('scritto relazioni_db.json e rel.json')
if __name__ == '__main__': main()
