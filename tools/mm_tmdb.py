#!/usr/bin/env python3
"""Miss Minutes 2.0-b - archivio TMDB dei titoli del catalogo -> miss-minutes/knowledge/tmdb_titoli.json (solo dati pubblici, 0 EUR).
La chiave NON va nel codice: TMDB_READ_TOKEN o TMDB_API_KEY come variabile d'ambiente / Secret (stessi di tmdb_sync.py).
  python3 tools/mm_tmdb.py --scrivi      # legge assets/images/catalog/tmdb_map.json (ID TMDB gia' risolti) e scrive l'archivio
  python3 tools/mm_tmdb.py --verifica    # controlla la struttura del file esistente
  python3 tools/mm_tmdb.py --prova       # prova di parsing su una risposta TMDB simulata (nessuna rete)
Per titolo: sinossi (it-IT, con ripiego en-US), regia, cast principale, stato, date di uscita PER PAESE, URL TMDB. TMDB non e' una conferma ufficiale:
l'app la classifica «tmdb». Attribuzione richiesta da TMDB: «Questo prodotto usa le API di TMDB ma non è approvato né certificato da TMDB»."""
import os, sys, json, time, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = R + '/miss-minutes/knowledge/tmdb_titoli.json'
MAP = R + '/assets/images/catalog/tmdb_map.json'
PAESI = ('IT', 'US', 'GB', 'FR', 'DE', 'ES')

def parse(t, d):
    """d = risposta TMDB (movie o tv con credits/release_dates appesi) -> voce compatta (funzione pura, testata offline)."""
    credits = d.get('credits') or {}
    regia = [c['name'] for c in credits.get('crew', []) if c.get('job') == 'Director'][:2]
    cast = [c['name'] for c in credits.get('cast', [])][:8]
    date = []
    if t == 'movie':
        for blocco in (d.get('release_dates') or {}).get('results', []):
            if blocco.get('iso_3166_1') in PAESI:
                ds = sorted(x['release_date'][:10] for x in blocco.get('release_dates', []) if x.get('release_date') and x.get('type') in (2, 3, 4, 5, 6))
                if ds: date.append({'paese': blocco['iso_3166_1'], 'data': ds[0]})
        if d.get('release_date'): date.append({'paese': 'TMDB', 'data': d['release_date'][:10]})
    else:
        if d.get('first_air_date'): date.append({'paese': 'TMDB', 'data': d['first_air_date'][:10]})
    voce = {'tmdb': {'t': t, 'id': d.get('id')}, 'titolo': d.get('title') or d.get('name') or '', 'sinossi_it': (d.get('overview') or '').strip()[:600],
            'regista': regia, 'cast': cast, 'stato': d.get('status') or '', 'date': date,
            'url': 'https://www.themoviedb.org/%s/%s' % ('movie' if t == 'movie' else 'tv', d.get('id'))}
    return voce

def scrivi():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from tmdb_sync import api
    mp = json.load(open(MAP, encoding='utf-8'))['voci']; voci = {}
    for num, v in sorted(mp.items()):
        t, i = v.get('t'), v.get('id')
        if t not in ('movie', 'tv') or not i: continue
        d = api('/%s/%d' % (t, i), append_to_response='credits,release_dates' if t == 'movie' else 'credits')
        if d and not (d.get('overview') or '').strip():       # sinossi it-IT assente -> ripiego en-US (dichiarato)
            en = api('/%s/%d' % (t, i), language='en-US')
            if en and en.get('overview'): d['overview'] = en['overview']; d['_lingua'] = 'en'
        if d:
            voce = parse(t, d)
            if d.get('_lingua') == 'en': voce['sinossi_lingua'] = 'en'
            voci[num] = voce
        time.sleep(0.1)
    out = {'versione': 1, 'generato': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'fonte': 'TMDB (api.themoviedb.org)',
           'attribuzione': "Questo prodotto usa le API di TMDB ma non è approvato né certificato da TMDB.", 'voci': voci}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('scritte %d voci in %s' % (len(voci), os.path.relpath(OUT, R)))

def verifica():
    if not os.path.exists(OUT): print('nessun archivio TMDB generato (facoltativo: l\'app funziona senza)'); return 0
    d = json.load(open(OUT, encoding='utf-8')); e = []
    if d.get('versione') != 1 or not isinstance(d.get('voci'), dict) or not d.get('generato'): e.append('struttura non valida')
    for n, v in (d.get('voci') or {}).items():
        if not n.isdigit() or not v.get('url', '').startswith('https://www.themoviedb.org/') or not isinstance(v.get('date'), list): e.append('voce %s non valida' % n)
    print('ERRORI: ' + '; '.join(e) if e else 'OK %d voci' % len(d['voci'])); return 1 if e else 0

def prova():
    d = {'id': 1, 'title': 'Prova', 'overview': ' Sinossi. ', 'status': 'Released', 'release_date': '2026-07-31',
         'credits': {'crew': [{'job': 'Director', 'name': 'A B'}, {'job': 'Editor', 'name': 'X'}], 'cast': [{'name': 'C D'}]},
         'release_dates': {'results': [{'iso_3166_1': 'IT', 'release_dates': [{'release_date': '2026-07-29T00:00:00.000Z', 'type': 3}, {'release_date': '2026-07-20T00:00:00.000Z', 'type': 1}]}, {'iso_3166_1': 'JP', 'release_dates': []}]}}
    v = parse('movie', d)
    ok = v['regista'] == ['A B'] and v['date'][0] == {'paese': 'IT', 'data': '2026-07-29'} and v['sinossi_it'] == 'Sinossi.' and v['url'].endswith('/movie/1') and len(v['date']) == 2
    print('prova parsing: ' + ('OK' if ok else 'FALLITA')); return 0 if ok else 1

if __name__ == '__main__':
    a = sys.argv[1:]
    if '--scrivi' in a: scrivi()
    elif '--prova' in a: sys.exit(prova())
    else: sys.exit(verifica())
