#!/usr/bin/env python3
"""Miss Minutes 2.0-b - archivio TMDB dei titoli del catalogo -> miss-minutes/knowledge/tmdb_titoli.json (solo dati pubblici, 0 EUR).
La chiave NON va nel codice: TMDB_READ_TOKEN o TMDB_API_KEY come variabile d'ambiente / Secret (stessi di tmdb_sync.py).
  python3 tools/mm_tmdb.py --scrivi      # mappa + override (gli override vincono), risolve i mancanti con regole stringenti, legge le STAGIONI, scrive l'archivio
  python3 tools/mm_tmdb.py --copertura   # riepilogo di copertura dell'archivio esistente (titoli, sinossi, stagioni, date, mancanti)
  python3 tools/mm_tmdb.py --verifica    # controlla la struttura del file esistente
  python3 tools/mm_tmdb.py --prova       # prova di parsing su una risposta TMDB simulata (nessuna rete)
Per titolo: sinossi (it-IT, con ripiego en-US), regia, cast principale, stato, date di uscita PER PAESE, URL TMDB. TMDB non e' una conferma ufficiale:
l'app la classifica «tmdb». Attribuzione richiesta da TMDB: «Questo prodotto usa le API di TMDB ma non è approvato né certificato da TMDB»."""
import os, sys, json, time, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = R + '/miss-minutes/knowledge/tmdb_titoli.json'
MAP = R + '/assets/images/catalog/tmdb_map.json'
PAESI = ('IT', 'US', 'GB', 'FR', 'DE', 'ES')

def clip(s, n):
    s = ' '.join(str(s).split())
    if len(s) <= n: return s
    c = s[:n]; k = max(c.rfind('. '), c.rfind('! '), c.rfind('? '))
    return c[:k + 1] if k > n * 0.5 else c.rsplit(' ', 1)[0] + '…'


import re, unicodedata
RISOLTI = R + '/miss-minutes/knowledge/tmdb_risolti.json'
OVR = R + '/assets/images/catalog/tmdb_overrides.json'

def norm(x):
    x = unicodedata.normalize('NFD', str(x).lower()); x = ''.join(c for c in x if not unicodedata.combining(c))
    x = re.sub(r'[^a-z0-9]+', ' ', x).strip()
    return re.sub(r'^(the|il|lo|la|i|gli|le) ', '', x)          # l'articolo iniziale non distingue i titoli

def varianti(titolo):
    """nomi da cercare su TMDB per un titolo del catalogo: senza «S<n>», senza «shorts», uno per ogni titolo separato da « / »"""
    base = re.sub(r'\s+S\d+$', '', titolo).strip()
    out = []
    for p in re.split(r'\s+/\s+', base):
        p = re.sub(r'\s+shorts?$', '', p, flags=re.I).strip()
        if p and p not in out: out.append(p)
    return out

def scegli(nomi, anno, tipo, risultati):
    """Funzione pura. risultati = [(kind, [risultato TMDB...]) per ogni nome].  Auto SOLO se: titolo (o originale) normalizzato IDENTICO,
    anno di uscita/prima messa in onda IDENTICO e UN solo candidato in tutto. Piu' nomi, piu' candidati o nessun anno -> mai associazione automatica."""
    cand = []
    for (nome, kind, res) in risultati:
        for r in res:
            nm = r.get('title') or r.get('name') or ''; on = r.get('original_title') or r.get('original_name') or ''
            y = (r.get('release_date') or r.get('first_air_date') or '')[:4]
            if norm(nome) in (norm(nm), norm(on)) and str(anno).isdigit() and y == str(anno):
                c = {'t': kind, 'id': r['id'], 'titolo': nm, 'anno': y, 'nome_cercato': nome}
                if not any(x['t'] == kind and x['id'] == r['id'] for x in cand): cand.append(c)
    if len(nomi) == 1 and len(cand) == 1:
        c = cand[0]; return 'auto', {'t': c['t'], 'id': c['id'], 'evidenza': {'titolo_tmdb': c['titolo'], 'anno': c['anno'], 'regola': 'titolo normalizzato identico + anno identico + candidato unico'}}
    return ('ambiguo' if cand else 'nessuno'), cand

def risolvi_mancanti(api, mancanti):
    """mancanti = [(num, titolo, anno, tipo)] -> {num: {...}}; mai associazioni a caso"""
    out = {}
    for num, tit, anno, tipo in mancanti:
        nomi = varianti(tit); kinds = ['movie'] if tipo == 'film' else ['tv'] if tipo == 'serie' else ['movie', 'tv']; ris = []
        for n in nomi:
            for k in kinds:
                q = {'query': n}
                if k == 'movie' and str(anno).isdigit(): q['year'] = anno
                res = api('/search/' + k, **q).get('results', []) or api('/search/' + k, **dict(q, language='en-US')).get('results', [])
                if not res and k == 'movie': res = api('/search/' + k, query=n).get('results', [])
                ris.append((n, k, res))
        st, dato = scegli(nomi, anno, tipo, ris)
        out[num] = {'titolo': tit, 'anno': anno, 'tipo': tipo, 'stato': st}
        if st == 'auto': out[num].update(dato)
        else: out[num]['candidati'] = dato
    return out

def parse_stagione(d):
    credits = d.get('credits') or {}
    eps = d.get('episodes') or []
    return {'n': d.get('season_number'), 'nome': d.get('name') or '', 'sinossi_it': clip(d.get('overview') or '', 600), 'data': (d.get('air_date') or '')[:10],
            'episodi': len(eps) or d.get('episode_count') or 0, 'cast': [c['name'] for c in credits.get('cast', [])][:8]}

def mappa_effettiva(risolti=None):
    mp = json.load(open(MAP, encoding='utf-8'))['voci']
    ov = json.load(open(OVR, encoding='utf-8'))['voci'] if os.path.exists(OVR) else {}
    out = {n: dict(v, risoluzione='mappa') for n, v in mp.items()}
    for n, v in ov.items():
        if v.get('skip'): out.pop(n, None); continue
        out[n] = {k: v[k] for k in ('t', 'id', 's') if k in v}; out[n]['risoluzione'] = 'override'
    for n, v in (risolti or {}).items():
        if v.get('stato') == 'auto' and n not in out: out[n] = {'t': v['t'], 'id': v['id'], 'risoluzione': 'auto'}
    return out

def parse(t, d):
    """d = risposta TMDB (movie o tv con credits/release_dates appesi) -> voce compatta (funzione pura, testata offline)."""
    credits = d.get('credits') or {}
    regia = [c['name'] for c in credits.get('crew', []) if c.get('job') == 'Director'][:2]
    cast = [c['name'] for c in credits.get('cast', [])][:8]
    date = []
    if t == 'movie':
        for blocco in (d.get('release_dates') or {}).get('results', []):
            if blocco.get('iso_3166_1') in PAESI:
                rd = [x for x in blocco.get('release_dates', []) if x.get('release_date')]
                # priorita': 3 = cinema (wide), poi 4 digitale/5 fisico/6 TV; 1-2 (anteprime/festival/limited) solo se non c'e' altro
                for tipi in ((3,), (4, 5, 6), (2, 1)):
                    ds = sorted(x['release_date'][:10] for x in rd if x.get('type') in tipi)
                    if ds: date.append({'paese': blocco['iso_3166_1'], 'data': ds[0]}); break
        if d.get('release_date'): date.append({'paese': 'TMDB', 'data': d['release_date'][:10]})
    else:
        if d.get('first_air_date'): date.append({'paese': 'TMDB', 'data': d['first_air_date'][:10]})
    voce = {'tmdb': {'t': t, 'id': d.get('id')}, 'titolo': d.get('title') or d.get('name') or '', 'sinossi_it': clip(d.get('overview') or '', 700),
            'regista': regia, 'cast': cast, 'stato': d.get('status') or '', 'date': date,
            'url': 'https://www.themoviedb.org/%s/%s' % ('movie' if t == 'movie' else 'tv', d.get('id'))}
    return voce

def scrivi():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from tmdb_sync import api, catalogo
    cat = catalogo(); mp = mappa_effettiva()
    mancanti = [c for c in cat if c[0] not in mp and not (json.load(open(OVR))['voci'].get(c[0], {}).get('skip') if os.path.exists(OVR) else False)]
    risolti = risolvi_mancanti(api, mancanti)
    json.dump({'versione': 1, 'generato': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
               'nota': "Associazioni TMDB per i titoli senza mappa/override. 'auto' = regola stringente (titolo identico + anno identico + candidato unico), DA CONFERMARE dall'utente copiandola in tmdb_overrides.json; 'ambiguo'/'nessuno' = nessuna associazione.",
               'voci': risolti}, open(RISOLTI, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    mp = mappa_effettiva(risolti); voci = {}
    for num, v in sorted(mp.items()):
        t, i, sea = v.get('t'), v.get('id'), v.get('s')
        if t not in ('movie', 'tv') or not i: continue
        d = api('/%s/%d' % (t, i), append_to_response='credits,release_dates' if t == 'movie' else 'credits')
        if d and not (d.get('overview') or '').strip():       # sinossi it-IT assente -> ripiego en-US (dichiarato)
            en = api('/%s/%d' % (t, i), language='en-US')
            if en and en.get('overview'): d['overview'] = en['overview']; d['_lingua'] = 'en'
        if not d: continue
        voce = parse(t, d)
        if d.get('_lingua') == 'en': voce['sinossi_lingua'] = 'en'
        voce['risoluzione'] = v.get('risoluzione', 'mappa')
        if t == 'tv':
            voce['serie'] = {'prima': (d.get('first_air_date') or '')[:10], 'ultima': (d.get('last_air_date') or '')[:10], 'n_stagioni': d.get('number_of_seasons')}
            if sea:
                sd = api('/tv/%d/season/%d' % (i, sea), append_to_response='credits')
                if sd: voce['stagione'] = parse_stagione(sd)
        voci[num] = voce
        time.sleep(0.1)
    out = {'versione': 2, 'generato': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'fonte': 'TMDB (api.themoviedb.org)',
           'attribuzione': "Questo prodotto usa le API di TMDB ma non è approvato né certificato da TMDB.", 'voci': voci}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ris = {k: v['stato'] for k, v in risolti.items()}
    print('scritte %d voci in %s; mancanti risolti: %s' % (len(voci), os.path.relpath(OUT, R), ris))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        open(os.environ['GITHUB_STEP_SUMMARY'], 'a').write('### Archivio TMDB Miss Minutes\n- Voci: %d\n- Stagioni lette: %d\n- Mancanti: %s\n' % (len(voci), sum(1 for v in voci.values() if 'stagione' in v), json.dumps(ris, ensure_ascii=False)))

def verifica(minimo=130):
    if not os.path.exists(OUT): print('nessun archivio TMDB generato (facoltativo: l\'app funziona senza)'); return 0
    d = json.load(open(OUT, encoding='utf-8')); e = []
    if d.get('versione') not in (1, 2) or not isinstance(d.get('voci'), dict) or not d.get('generato'): e.append('struttura non valida')
    for n, v in (d.get('voci') or {}).items():
        if not n.isdigit() or not v.get('url', '').startswith('https://www.themoviedb.org/') or not isinstance(v.get('date'), list): e.append('voce %s non valida' % n)
        if d.get('versione') == 2 and v.get('tmdb', {}).get('t') == 'tv' and 'serie' not in v: e.append('voce %s: serie senza dati di serie' % n)
    if len(d.get('voci', {})) < minimo: e.append('copertura insufficiente: %d < %d voci' % (len(d['voci']), minimo))
    print('ERRORI: ' + '; '.join(e) if e else 'OK %d voci' % len(d['voci'])); return 1 if e else 0

def copertura():
    d = json.load(open(OUT, encoding='utf-8')); v = d['voci']
    tv = [x for x in v.values() if x['tmdb']['t'] == 'tv']; mv = [x for x in v.values() if x['tmdb']['t'] == 'movie']
    print('voci %d (film %d, serie %d) generato %s' % (len(v), len(mv), len(tv), d['generato']))
    print('sinossi %d | cast %d | regia film %d/%d | date IT film %d | date US film %d' % (sum(1 for x in v.values() if x['sinossi_it']), sum(1 for x in v.values() if x['cast']), sum(1 for x in mv if x['regista']), len(mv), sum(1 for x in mv if any(y['paese'] == 'IT' for y in x['date'])), sum(1 for x in mv if any(y['paese'] == 'US' for y in x['date']))))
    print('stagioni: %d con dati di stagione, %d con sinossi di stagione' % (sum(1 for x in tv if 'stagione' in x), sum(1 for x in tv if x.get('stagione', {}).get('sinossi_it'))))
    print('risoluzione:', {k: sum(1 for x in v.values() if x.get('risoluzione') == k) for k in ('mappa', 'override', 'auto')})
    if os.path.exists(RISOLTI): print('mancanti:', {k: x['stato'] for k, x in json.load(open(RISOLTI))['voci'].items()})

def prova():
    d = {'id': 1, 'title': 'Prova', 'overview': ' Sinossi. ', 'status': 'Released', 'release_date': '2026-07-31',
         'credits': {'crew': [{'job': 'Director', 'name': 'A B'}, {'job': 'Editor', 'name': 'X'}], 'cast': [{'name': 'C D'}]},
         'release_dates': {'results': [{'iso_3166_1': 'IT', 'release_dates': [{'release_date': '2026-07-29T00:00:00.000Z', 'type': 3}, {'release_date': '2026-07-20T00:00:00.000Z', 'type': 1}]}, {'iso_3166_1': 'JP', 'release_dates': []}]}}
    v = parse('movie', d)
    ok = v['regista'] == ['A B'] and v['date'][0] == {'paese': 'IT', 'data': '2026-07-29'} and clip('Frase uno. ' * 100, 700).endswith('uno.') and len(clip('parola ' * 200, 700)) <= 701 and v['sinossi_it'] == 'Sinossi.' and v['url'].endswith('/movie/1') and len(v['date']) == 2
    # scegli(): regole stringenti, mai associazioni a caso
    R_ = lambda **k: dict(k)
    a1 = scegli(['Fantastic Four: First Steps'], '2025', 'film', [('Fantastic Four: First Steps', 'movie', [R_(id=1, title='The Fantastic Four: First Steps', release_date='2025-07-23')])])
    a2 = scegli(['Fantastic Four: First Steps'], '2025', 'film', [('Fantastic Four: First Steps', 'movie', [R_(id=1, title='The Fantastic Four: First Steps', release_date='2025-07-23'), R_(id=2, title='Fantastic Four: First Steps', release_date='2025-01-01')])])
    a3 = scegli(['I Am Groot'], '2022', 'speciale', [('I Am Groot', 'movie', []), ('I Am Groot', 'tv', [R_(id=9, name='I Am Groot', first_air_date='2022-08-10')])])
    a4 = scegli(['Team Thor', 'Team Darryl'], '2016', 'speciale', [('Team Thor', 'movie', [R_(id=3, title='Team Thor', release_date='2016-09-13')]), ('Team Darryl', 'movie', [R_(id=4, title='Team Darryl', release_date='2016-09-13')])])
    a5 = scegli(['Foo'], '2022', 'film', [('Foo', 'movie', [R_(id=5, title='Foo', release_date='2019-01-01')])])
    ok2 = a1[0] == 'auto' and a1[1]['id'] == 1 and a2[0] == 'ambiguo' and a3[0] == 'auto' and a3[1]['t'] == 'tv' and a4[0] == 'ambiguo' and a5[0] == 'nessuno'
    ok3 = varianti('Team Thor / Team Darryl shorts') == ['Team Thor', 'Team Darryl'] and varianti('Loki S2') == ['Loki'] and varianti('I Am Groot shorts') == ['I Am Groot'] and norm('The Defenders') == 'defenders'
    ss = parse_stagione({'season_number': 2, 'name': 'Stagione 2', 'overview': 'Trama S2.', 'air_date': '2023-10-05', 'episodes': [{}] * 6, 'credits': {'cast': [{'name': 'T H'}]}})
    ok4 = ss['n'] == 2 and ss['data'] == '2023-10-05' and ss['episodi'] == 6 and ss['cast'] == ['T H']
    print('prova parsing: ' + ('OK' if ok and ok2 and ok3 and ok4 else 'FALLITA %s' % [ok, ok2, ok3, ok4])); return 0 if ok and ok2 and ok3 and ok4 else 1

if __name__ == '__main__':
    a = sys.argv[1:]
    if '--scrivi' in a: scrivi()
    elif '--prova' in a: sys.exit(prova())
    elif '--copertura' in a: copertura()
    else: sys.exit(verifica())
