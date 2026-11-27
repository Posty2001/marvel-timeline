#!/usr/bin/env python3
"""W0 censimento: conteggi INTERNI (sempre) + ESTERNI (solo con rete: Actions). Solo lettura, nessun dato scritto nel repo.
Uso: python3 tools/db_censimento.py [--esterni] [--out out.json]
Esterni: Wikidata (SPARQL, User-Agent dichiarato, 1 query ogni ~2 s), TMDB (token da env TMDB_READ_TOKEN), Comic Vine (env COMICVINE_API_KEY, opzionale,
<=200 richieste/ora/risorsa: qui ~4 richieste). Nessuna chiave viene stampata o scritta. QID da verificare: lo script ne stampa l'etichetta ufficiale."""
import json, os, sys, time, pathlib, urllib.request, urllib.parse, collections
R = pathlib.Path(__file__).resolve().parent.parent
UA = 'TVA-Archives-census/1.0 (progetto personale non commerciale; https://github.com/Posty2001/marvel-timeline)'
def interni():
    idx = json.load(open(R/'atlante2/data/index.json'))['voci']
    c = collections.Counter(v['t'] for v in idx)
    ide = json.load(open(R/'data/atlante/identita.json'))
    rel = json.load(open(R/'data/atlante/relazioni.json'))
    nrel = len(rel.get('relazioni', rel if isinstance(rel, list) else []))
    ritr = 0
    try: ritr = len(json.load(open(R/'data/atlante/assets.json')).get('ritratti', {}))
    except Exception: pass
    return {'voci_indice': len(idx), 'per_tipo': dict(c), 'identita': len(ide['identita']),
            'con_alias': sum(1 for x in ide['identita'] if x.get('alias')), 'con_interpreti': sum(1 for x in ide['identita'] if x.get('interpreti')),
            'relazioni_registro': nrel, 'titoli_timeline': c.get('t', 0)}
def get(url, headers=None, tries=3):
    for i in range(tries):
        try:
            rq = urllib.request.Request(url, headers=dict({'User-Agent': UA}, **(headers or {})))
            return json.load(urllib.request.urlopen(rq, timeout=60))
        except Exception as e:
            last = str(e)[:120]; time.sleep(3 * (i + 1))
    return {'errore': last}
def sparql(q):
    return get('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(q), {'Accept': 'application/sparql-results+json'})
def esterni():
    out = {}
    lab = get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&languages=en&ids=Q931597|Q642878|Q95074|Q1235940')
    out['wikidata_etichette_qid'] = {k: v.get('labels', {}).get('en', {}).get('value') for k, v in lab.get('entities', {}).items()} if 'entities' in lab else lab
    for nome, q in {
        'personaggi_universo_marvel_P1080': 'SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P1080 wd:Q931597 . }',
        'personaggi_fittizi_marvel_P1080_istanza': 'SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P1080 wd:Q931597 ; wdt:P31/wdt:P279* wd:Q95074 . }',
        'elementi_MCU_P1080': 'SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P1080 wd:Q642878 . }',
        'con_etichetta_italiana': 'SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P1080 wd:Q931597 . ?x rdfs:label ?l FILTER(LANG(?l)="it") }',
    }.items():
        r = sparql(q); time.sleep(2)
        out['wikidata_' + nome] = r['results']['bindings'][0]['n']['value'] if 'results' in r else r
    tok = os.environ.get('TMDB_READ_TOKEN')
    if tok:
        h = {'Authorization': 'Bearer ' + tok}
        for nome, u in {'tmdb_film_marvel_studios': 'discover/movie?with_companies=420', 'tmdb_serie_marvel_studios': 'discover/tv?with_companies=420',
                        'tmdb_serie_marvel_animation': 'discover/tv?with_companies=13252'}.items():
            r = get('https://api.themoviedb.org/3/' + u, h); out[nome] = r.get('total_results', r)
    else: out['tmdb'] = 'saltato: TMDB_READ_TOKEN assente'
    k = os.environ.get('COMICVINE_API_KEY')
    if k:
        for nome, res in {'comicvine_personaggi_marvel': 'characters', 'comicvine_volumi_marvel': 'volumes'}.items():
            r = get('https://comicvine.gamespot.com/api/%s/?api_key=%s&format=json&limit=1&field_list=id&filter=publisher:31' % (res, k))
            out[nome] = r.get('number_of_total_results', r.get('error', r)); time.sleep(1)
    else: out['comicvine'] = 'saltato: COMICVINE_API_KEY assente (D7: solo piano gratuito)'
    out['gcd'] = 'non interrogato in W0: servono account gratuito e dump (CC BY-SA 4.0)'
    return out
if __name__ == '__main__':
    res = {'quando': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'interni': interni()}
    if '--esterni' in sys.argv: res['esterni'] = esterni()
    s = json.dumps(res, ensure_ascii=False, indent=1)
    if '--out' in sys.argv: pathlib.Path(sys.argv[sys.argv.index('--out') + 1]).write_text(s)
    print(s)
