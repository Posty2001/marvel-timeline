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
    per_classe = collections.Counter(x.get('classe') for x in rel['relazioni'])
    narr = [x for x in rel['relazioni'] if x.get('classe') == 'narrativa']
    tl = json.load(open(R/'data/atlante/blob/altTimelineData.json'))  # = window.marvelGetAltTimelineData: la Timeline numerata
    return {'voci_indice': len(idx), 'per_tipo': dict(c), 'identita': len(ide['identita']),
            'con_alias': sum(1 for x in ide['identita'] if x.get('alias')), 'con_interpreti': sum(1 for x in ide['identita'] if x.get('interpreti')),
            # le 4 classi NON si sommano mai in un unico «collegamenti»; le co-apparizioni NON sono nel registro (0 per regola)
            'relazioni_per_classe': {'narrativa': per_classe.get('narrativa', 0), 'editoriale': per_classe.get('editoriale', 0),
                                     'controparte': per_classe.get('controparte', 0), 'co_apparizione': 0},
            'relazioni_narrative_per_verifica': dict(collections.Counter(x.get('verifica') for x in narr)),
            'titoli_timeline_numerata': len(tl), 'titoli_con_voce_atlas': c.get('t', 0)}
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
    # 1) QID mai dati per scontati: si risolvono per etichetta esatta e si stampano per la verifica umana
    cand = {}
    for nome in ('Marvel Cinematic Universe', 'Marvel Universe', 'Marvel Comics'):
        r = get('https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&limit=6&search=' + urllib.parse.quote(nome))
        cand[nome] = [{'id': x['id'], 'label': x.get('label'), 'desc': x.get('description')} for x in r.get('search', [])] if 'search' in r else r
        time.sleep(1)
    out['wikidata_candidati_qid'] = cand
    # 2) universi di finzione con 'Marvel' nell'etichetta, con conteggio degli elementi (P1080), senza QID scritti a mano
    r = sparql('SELECT ?u ?ul (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P1080 ?u . ?u rdfs:label ?ul . FILTER(LANG(?ul)="en" && CONTAINS(LCASE(?ul),"marvel")) } GROUP BY ?u ?ul ORDER BY DESC(?n) LIMIT 60')
    time.sleep(2)
    out['wikidata_universi_marvel_P1080'] = [{'qid': b['u']['value'].rsplit('/', 1)[-1], 'label': b['ul']['value'], 'n': int(b['n']['value'])} for b in r['results']['bindings']] if 'results' in r else r
    # 3) fiction MCU: elementi per classe (P31 etichetta inglese) tramite l'universo MCU risolto per etichetta esatta
    q = ('SELECT ?cl (COUNT(DISTINCT ?x) AS ?n) WHERE { ?u rdfs:label "Marvel Cinematic Universe"@en . ?x wdt:P1080 ?u . ?x wdt:P31 ?c . ?c rdfs:label ?cl FILTER(LANG(?cl)="en") } GROUP BY ?cl ORDER BY DESC(?n) LIMIT 60')
    r = sparql(q); time.sleep(2)
    out['wikidata_MCU_per_classe_P31'] = [{'classe': b['cl']['value'], 'n': int(b['n']['value'])} for b in r['results']['bindings']] if 'results' in r else r
    # 4) personaggi Marvel (universo con 'Marvel' nell'etichetta, istanza di personaggio di finzione, anche sottoclassi)
    q = ('SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P1080 ?u . ?u rdfs:label ?ul FILTER(LANG(?ul)="en" && CONTAINS(LCASE(?ul),"marvel")) . ?x wdt:P31/wdt:P279* wd:Q95074 }')
    r = sparql(q); time.sleep(2)
    out['wikidata_personaggi_fittizi_Marvel'] = r['results']['bindings'][0]['n']['value'] if 'results' in r else r
    # 5) personaggi Marvel per EDITORE (P123 = etichetta Marvel Comics) - copre i fumetti anche senza P1080
    q = ('SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P31/wdt:P279* wd:Q95074 ; wdt:P123 ?e . ?e rdfs:label "Marvel Comics"@en }')
    r = sparql(q); time.sleep(2)
    out['wikidata_personaggi_fittizi_editore_Marvel_Comics'] = r['results']['bindings'][0]['n']['value'] if 'results' in r else r
    q = ('SELECT (COUNT(DISTINCT ?x) AS ?n) WHERE { ?x wdt:P1080 ?u . ?u rdfs:label ?ul FILTER(LANG(?ul)="en" && CONTAINS(LCASE(?ul),"marvel")) . ?x rdfs:label ?l FILTER(LANG(?l)="it") }')
    r = sparql(q); time.sleep(2)
    out['wikidata_Marvel_con_etichetta_italiana'] = r['results']['bindings'][0]['n']['value'] if 'results' in r else r
    tok = os.environ.get('TMDB_READ_TOKEN')
    if tok:
        h = {'Authorization': 'Bearer ' + tok}
        for nome, u in {'tmdb_film_marvel_studios': 'discover/movie?with_companies=420', 'tmdb_serie_marvel_studios': 'discover/tv?with_companies=420',
                        'tmdb_serie_marvel_animation': 'discover/tv?with_companies=13252'}.items():
            r = get('https://api.themoviedb.org/3/' + u, h); out[nome] = r.get('total_results', r)
    else: out['tmdb'] = 'saltato: TMDB_READ_TOKEN assente'
    k = os.environ.get('COMICVINE_API_KEY')
    out['comicvine'] = 'rimandato alle ondate fumetti (W5-W6) su decisione dell\'utente' if not k else 'chiave presente ma non usata in W1'
    out['gcd'] = 'non interrogato: servono account gratuito e dump (CC BY-SA 4.0)'
    return out
if __name__ == '__main__':
    res = {'quando': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'interni': interni()}
    if '--esterni' in sys.argv: res['esterni'] = esterni()
    s = json.dumps(res, ensure_ascii=False, indent=1)
    if '--out' in sys.argv: pathlib.Path(sys.argv[sys.argv.index('--out') + 1]).write_text(s)
    print(s)
