#!/usr/bin/env python3
"""Verifica in SOLA LETTURA della mappa locandine (tmdbMap, chiavi = id interno degli item) contro TMDB: titolo, anno, tipo/stagione, produttori.
Atteso (titolo, data) = altTimelineData dell'app, stessa chiave. Non modifica nulla: scrive un report; ogni correzione e' una decisione separata.
Chiave solo da TMDB_READ_TOKEN / TMDB_API_KEY (Secret). Uso: python3 tools/tmdb_verifica_mappa.py --out DIR | --offline (solo controlli locali)"""
import os, sys, json, re, argparse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atlante_numeri as N
from atlante_pilot_tmdb import Api, norm

def base_title(t): return re.sub(r'\s+S\d+$', '', t or '').strip()

def verifica(api, c):
    out = []
    for k in sorted(c['tmdbMap']):
        m = c['tmdbMap'][k]; e = c['timeline'].get(k); r = {'item': k, 'numero_mostrato': c['id2vis'].get(k), 'tmdb_id': m['id'], 'tipo': m['t'], 'stagione': m.get('s')}
        if not e: r.update(esito='item-assente-in-timeline'); out.append(r); continue
        rel = e.get('release') or ''; tit, yr = base_title(e['title']), (int(rel[:4]) if rel[:4].isdigit() else None); r.update(titolo_app=e['title'], anno_app=yr, saga=e.get('saga'), studio=e.get('studio'))
        d = api.get('/%s/%s' % (m['t'], m['id']), language='en-US')
        if not d: r.update(esito='id-inesistente'); out.append(r); continue
        t = d.get('title') or d.get('name'); dt = d.get('release_date') or d.get('first_air_date') or ''
        if m['t'] == 'tv' and m.get('s'):
            ss = [s for s in d.get('seasons', []) if s.get('season_number') == m['s']]
            dt = (ss[0].get('air_date') if ss else '') or dt; r['stagione_trovata'] = bool(ss)
        ty = int(dt[:4]) if dt[:4].isdigit() else None
        r.update(titolo_tmdb=t, anno_tmdb=ty, produttori=[x['name'] for x in d.get('production_companies', [])][:4], poster_attuale_uguale=(d.get('poster_path') == m.get('p')))
        tok = norm(t) == norm(tit); yok = (yr is None) or (ty is not None and abs(ty - yr) <= 1)
        r['esito'] = 'ok' if tok and yok else ('titolo-diverso' if not tok else 'anno-diverso')
        if r['esito'] != 'ok':
            q = {'query': tit, 'language': 'en-US'}
            if yr: q['year' if m['t'] == 'movie' else 'first_air_date_year'] = yr
            cand = [x for x in (api.get('/search/' + m['t'], **q) or {}).get('results', []) if norm(x.get('title') or x.get('name')) == norm(tit)]
            r['proposta'] = [{'id': x['id'], 'titolo': x.get('title') or x.get('name'), 'data': x.get('release_date') or x.get('first_air_date'), 'poster': x.get('poster_path')} for x in cand[:3]]
        out.append(r)
    return out

def riepilogo(rs):
    from collections import Counter
    c = Counter(r['esito'] for r in rs); L = ['# Verifica mappa locandine (tmdbMap) contro TMDB', '', 'Voci: %d | %s' % (len(rs), ' | '.join('%s: %d' % kv for kv in sorted(c.items()))), '']
    bad = [r for r in rs if r['esito'] != 'ok']
    if bad:
        L += ['| item | app | TMDB | esito | proposta |', '|---|---|---|---|---|']
        for r in bad: L.append('| %s | %s (%s) | %s (%s) | %s | %s |' % (r['item'], r.get('titolo_app'), r.get('anno_app'), r.get('titolo_tmdb'), r.get('anno_tmdb'), r['esito'], r.get('proposta')))
    L += ['', 'Poster diverso dall\'attuale su TMDB (informativo, non un errore): %d' % sum(1 for r in rs if r.get('poster_attuale_uguale') is False)]
    return '\n'.join(L) + '\n'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out'); ap.add_argument('--offline', action='store_true'); a = ap.parse_args(); c = N.carica()
    if a.offline:
        miss = [k for k in c['tmdbMap'] if k not in c['timeline']]; print('voci mappa:', len(c['tmdbMap']), '| senza item in timeline:', miss); sys.exit(1 if miss else 0)
    os.makedirs(a.out, exist_ok=True); rs = verifica(Api(), c)
    json.dump({'schema': 1, 'generato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'voci': rs}, open(os.path.join(a.out, 'verifica_mappa.json'), 'w'), ensure_ascii=False, indent=1)
    open(os.path.join(a.out, 'VERIFICA_MAPPA.md'), 'w').write(riepilogo(rs)); print(riepilogo(rs))
