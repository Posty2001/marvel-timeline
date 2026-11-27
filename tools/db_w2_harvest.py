#!/usr/bin/env python3
"""W2 raccolta Wikidata (CC0) per film Marvel pre-MCU e paralleli: opere per titolo+anno (P31 film, P577), personaggi (P1441 presente-in), cast (P161), regia/sceneggiatura (P57/P58).
Il gruppo (franchise) determina la continuita' (mappa in db_w1_build.py GRP_UNI); personaggi presenti in piu' gruppi NON ricevono continuita' automatica.
Rete richiesta -> Actions. Uso: python3 tools/db_w2_harvest.py <out_dir>"""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_w1_harvest as H
FILM = {
 'x-men-fox': [('X-Men', 2000), ('X2', 2003), ('X-Men: The Last Stand', 2006), ('X-Men Origins: Wolverine', 2009), ('X-Men: First Class', 2011), ('The Wolverine', 2013), ('X-Men: Days of Future Past', 2014), ('X-Men: Apocalypse', 2016), ('Logan', 2017), ('Dark Phoenix', 2019)],
 'deadpool-fox': [('Deadpool', 2016), ('Deadpool 2', 2018)], 'new-mutants-fox': [('The New Mutants', 2020)],
 'spider-man-raimi': [('Spider-Man', 2002), ('Spider-Man 2', 2004), ('Spider-Man 3', 2007)], 'spider-man-garfield': [('The Amazing Spider-Man', 2012), ('The Amazing Spider-Man 2', 2014)],
 'venom-ssu': [('Venom', 2018), ('Venom: Let There Be Carnage', 2021), ('Venom: The Last Dance', 2024)], 'morbius-ssu': [('Morbius', 2022)], 'madame-web-ssu': [('Madame Web', 2024)], 'kraven-ssu': [('Kraven the Hunter', 2024)],
 'blade': [('Blade', 1998), ('Blade II', 2002), ('Blade: Trinity', 2004)], 'daredevil-elektra': [('Daredevil', 2003), ('Elektra', 2005)], 'ghost-rider': [('Ghost Rider', 2007), ('Ghost Rider: Spirit of Vengeance', 2011)],
 'hulk-2003': [('Hulk', 2003)], 'fantastic-four-1994': [('The Fantastic Four', 1994)], 'fantastic-four-fox': [('Fantastic Four', 2005), ('Fantastic Four: Rise of the Silver Surfer', 2007)], 'fantastic-four-trank': [('Fantastic Four', 2015)]}
def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    membri = {}; man = {'avvio': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'film': {}}
    for g, lista in FILM.items():
        for titolo, anno in lista:
            q = 'SELECT DISTINCT ?x WHERE { ?w rdfs:label "%s"@en . ?w wdt:P31/wdt:P279* wd:Q11424 . ?w wdt:P577 ?d . FILTER(YEAR(?d)=%d) }' % (titolo.replace('"', '\\"'), anno)
            ws = H.qids(H.sparql(q)) or []
            man['film']['%s|%s|%d' % (g, titolo, anno)] = ws
            for w in ws:
                membri.setdefault(w, set()).add(g)
                for nome, qq in (('personaggi', 'SELECT DISTINCT ?x WHERE { ?x wdt:P1441 wd:%s . }' % w), ('interpreti', 'SELECT DISTINCT ?x WHERE { wd:%s wdt:P161 ?x . ?x wdt:P31 wd:Q5 }' % w), ('creatori', 'SELECT DISTINCT ?x WHERE { { wd:%s wdt:P57 ?x } UNION { wd:%s wdt:P58 ?x } }' % (w, w))):
                    for x in (H.qids(H.sparql(qq)) or []): membri.setdefault(x, set()).add(g if nome == 'personaggi' else g + ':' + nome)
    ids = sorted(membri)
    # i gruppi 'g:interpreti'/'g:creatori' non contano per la continuita' (solo 'g' puro); restano come provenienza
    ents = H.fetch_entities(ids, 'labels|aliases|descriptions|claims|sitelinks')
    refs = set(); rec = {}
    for q, e in ents.items():
        if 'missing' in e: continue
        cl = e.get('claims', {}); c = {p: H.claim_ids(cl, p) for p in H.KEEP if p in cl}
        for p in ('P31', 'P279', 'P1080', 'P8345', 'P179', 'P175', 'P170', 'P106', 'P463'): refs.update(c.get(p, []))
        gr = sorted(membri[q])
        rec[q] = {'q': q, 'g': gr, 'l': {k: v['value'] for k, v in e.get('labels', {}).items()}, 'd': {k: v['value'] for k, v in e.get('descriptions', {}).items()},
                  'a': {k: [a['value'] for a in v] for k, v in e.get('aliases', {}).items()}, 'sl': {k: v['title'] for k, v in e.get('sitelinks', {}).items()}, 'c': c}
    lab = H.fetch_entities(sorted(refs - set(rec)), 'labels'); et = {q: (v.get('labels', {}).get('en', {}).get('value')) for q, v in lab.items()}
    for q, r in rec.items(): et.setdefault(q, r['l'].get('en'))
    man['entita'] = len(rec); man['fine'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    json.dump({'fonte': 'Wikidata (CC0)', 'recuperato': man['fine'], 'entita': rec, 'etichette': et}, open(out/'w2_wikidata.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(man, open(out/'w2_manifest.json', 'w'), indent=1); print(json.dumps({k: v for k, v in man.items() if k != 'film'}), 'film trovati', sum(1 for v in man['film'].values() if v), '/', len(man['film']))
    sys.exit(0 if rec else 1)
if __name__ == '__main__': main()
