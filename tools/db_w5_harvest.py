#!/usr/bin/env python3
"""Database Expansion W5/W6 - UNIVERSO DEI FUMETTI MARVEL. Raccolta di dati pubblici Wikidata (CC0); nessuna chiave, nessun Secret.
W5 = entita' narrative dei fumetti: personaggi, squadre/organizzazioni, specie, luoghi, oggetti, entita' cosmiche, universi (elementi dichiarati nell'universo di finzione Marvel con almeno 3 collegamenti
     Wikipedia: criterio di rilevanza oggettivo, documentabile e riproducibile; i personaggi minori senza voce enciclopedica restano per un'ondata di approfondimento).
W6 = opere e persone dei fumetti: testate, miniserie, saghe/eventi, graphic novel (pubblicati da Marvel Comics) e creatori (autori/disegnatori/creatori di personaggi).
Robusto e riprendibile come W2-W4: fasce di rilevanza separate (nessun timeout globale), anomalie nel manifest, checkpoint dopo ogni gruppo.
Uso: python3 tools/db_w5_harvest.py <out_dir> [w5|w6]   (rete richiesta -> Actions)"""
import json, sys, time, pathlib, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_w1_harvest as H
ONDA = sys.argv[2] if len(sys.argv) > 2 else 'w5'
UNI_LAB = ('Marvel Universe', 'Earth-616', 'Marvel Comics Universe', 'Ultimate Marvel', 'Ultimate Universe', 'Marvel 2099', 'Marvel Zombies', 'Age of Apocalypse', 'House of M', 'MC2', 'Earth-1610', 'Earth-65')
UL = ' '.join('"%s"@en' % x for x in UNI_LAB)
U = '?u rdfs:label ?ul . VALUES ?ul { %s } .' % UL
PUB = '?pub rdfs:label "Marvel Comics"@en .'
def fascia(lo, hi): return 'FILTER(?n >= %d%s)' % (lo, (' && ?n < %d' % hi) if hi else '')
def sel(corpo, lo, hi): return 'SELECT DISTINCT ?x WHERE { %s ?x wikibase:sitelinks ?n . %s }' % (corpo, fascia(lo, hi))
FASCE = [(40, 0), (20, 40), (12, 20), (8, 12), (5, 8), (3, 5)]
GRUPPI = {}
if ONDA == 'w5':
    for lo, hi in FASCE: GRUPPI['fumetti:%d-%s' % (lo, hi or 'max')] = sel('%s ?x wdt:P1080 ?u .' % U, lo, hi)
    # elementi senza P1080 ma presenti in opere pubblicate da Marvel Comics (P1441 «presente nell'opera», P674 «personaggi»): solo con almeno 5 collegamenti Wikipedia;
    # NON ricevono automaticamente la continuita' 616 (nessuna attribuzione certa)
    for lo, hi in FASCE[:5]: GRUPPI['fumetti_pubbl:%d-%s' % (lo, hi or 'max')] = sel('%s { ?x wdt:P1441 ?w } UNION { ?w wdt:P674 ?x } ?w wdt:P123 ?pub .' % PUB, lo, hi)
else:
    for lo, hi in FASCE:
        GRUPPI['opere:%d-%s' % (lo, hi or 'max')] = sel('%s ?x wdt:P123 ?pub .' % PUB, lo, hi)
    for lo, hi in FASCE[:5]:
        GRUPPI['creatori:%d-%s' % (lo, hi or 'max')] = sel('%s { ?w wdt:P123 ?pub . ?w wdt:P50 ?x } UNION { ?w wdt:P123 ?pub . ?w wdt:P110 ?x } UNION { ?c wdt:P1080 ?u . ?c wdt:P170 ?x } ?x wdt:P31 wd:Q5 .' % (PUB + ' ' + U), lo, hi)
        # (la sezione UNION usa sia PUB sia U: le variabili non coinvolte restano libere per ramo)
KEEP = H.KEEP + ('P123', 'P50', 'P110', 'P1441', 'P674', 'P138')
RE_UNI = re.compile(r'marvel|earth-|ultimate|mutant|x-men|spider|age of|house of|zombies|2099|what if|mc2|exiles|ruins', re.I)
def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); H.ANOM.clear()
    nm = ONDA + '_'
    ck_f = out / (nm + 'checkpoint.json'); ck = {'gruppi': {}}
    if ck_f.exists():
        try: ck = json.load(open(ck_f)); print('ripresa:', len(ck['gruppi']), 'gruppi')
        except Exception as e: H.anom('checkpoint illeggibile: %s' % e)
    man = {'avvio': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'gruppi': {}}
    mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 10**9
    for g, q in GRUPPI.items():
        if g in ck['gruppi']: man['gruppi'][g] = {'ok': True, 'n': len(ck['gruppi'][g]), 'da_checkpoint': True}; continue
        ids = H.qids(H.sparql(q))
        man['gruppi'][g] = {'ok': ids is not None, 'n': len(ids) if ids else 0}
        if ids is not None: ck['gruppi'][g] = ids[:mx]; json.dump(ck, open(ck_f, 'w'))
        else: H.anom('gruppo senza risposta (si riprova al prossimo avvio): ' + g)
    membri = {}
    for g, ids in ck['gruppi'].items():
        for x in ids: membri.setdefault(x, []).append(g)
    ents = H.fetch_entities(membri, 'labels|aliases|descriptions|claims|sitelinks')
    rec = {}; refs = set(); cnt1080 = {}
    def aggiungi(q, e, gr):
        cl = e.get('claims', {}); c = {p: H.claim_ids(cl, p) for p in KEEP if p in cl}
        for p in ('P31', 'P279', 'P1080', 'P8345', 'P179', 'P175', 'P170', 'P106', 'P123'): refs.update(c.get(p, []))
        rec[q] = {'q': q, 'g': gr, 'l': {k: v['value'] for k, v in e.get('labels', {}).items()}, 'd': {k: v['value'] for k, v in e.get('descriptions', {}).items()},
                  'a': {k: [a['value'] for a in v] for k, v in e.get('aliases', {}).items()}, 'sl': {k: v['title'] for k, v in e.get('sitelinks', {}).items()}, 'c': c}
    for q, e in ents.items():
        if 'missing' in e: continue
        aggiungi(q, e, membri.get(q, []))
        for u in rec[q]['c'].get('P1080', []): cnt1080[u] = cnt1080.get(u, 0) + 1
    # universi di finzione referenziati (solo Marvel): entrano come voci universo
    if ONDA == 'w5':
        lab0 = H.fetch_entities(sorted(cnt1080), 'labels')
        cand = [u for u in cnt1080 if u not in rec and cnt1080[u] >= 3 and RE_UNI.search((lab0.get(u, {}).get('labels', {}).get('en', {}) or {}).get('value', ''))]
        for q, e in H.fetch_entities(cand, 'labels|aliases|descriptions|claims|sitelinks').items():
            if 'missing' not in e: aggiungi(q, e, ['universi_fumetti'])
    lab = H.fetch_entities(sorted(refs - set(rec)), 'labels')
    etich = {q: (v.get('labels', {}).get('en', {}).get('value')) for q, v in lab.items()}
    for q, r in rec.items(): etich.setdefault(q, r['l'].get('en'))
    man['anomalie'] = H.ANOM[:200]; man['entita'] = len(rec); man['fine'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    man['completa'] = all(g in ck['gruppi'] for g in GRUPPI)
    json.dump({'fonte': 'Wikidata (CC0)', 'recuperato': man['fine'], 'entita': rec, 'etichette': etich}, open(out / (nm + 'wikidata.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(man, open(out / (nm + 'manifest.json'), 'w'), indent=1); print(json.dumps({k: v for k, v in man.items() if k != 'anomalie'}))
    sys.exit(0 if rec else 1)
if __name__ == '__main__': main()
