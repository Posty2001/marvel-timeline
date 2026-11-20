#!/usr/bin/env python3
"""TVA Episodes - genera il catalogo episodi (titoli IT, date) da TMDB.

Uso:   TMDB_READ_TOKEN=... python3 tools/tmdb_episodes.py [--out assets/episodes] [--only 043,044]
Riusa tools/tmdb_sync.py (stesso TMDB_READ_TOKEN/TMDB_API_KEY da ambiente, mai scritti ne' stampati).
Input : assets/images/catalog/tmdb_map.json + tmdb_overrides.json  (voci t='tv': senza 's' = intera serie, con 's' = singola stagione)
Output: <out>/<tmdbId>.json   {versione, tmdb, nome, lingua, stagioni:[{n, nome, episodi:[{n, t, d}]}]}
        <out>/index.json      {versione, fonte, aggiornato, voci:{idTimeline:{tmdb, s?, stagioni, episodi}}}
Un'esecuzione parziale (errore di rete) non sovrascrive i file gia' buoni: l'indice cita solo serie scaricate.
"""
import argparse, datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tmdb_sync   # riuso dell'integrazione esistente: stesso token (env), retry 429, nessun URL/chiave in output

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def get(path, params=None):
    return tmdb_sync.api(path, **(params or {}))


def clean_show(tmdb):
    d = get('/tv/%d' % tmdb, {'language': 'it-IT'})
    if not d:
        return None
    stagioni = []
    for s in d.get('seasons') or []:
        n = s.get('season_number')
        if not isinstance(n, int):
            continue
        sd = get('/tv/%d/season/%d' % (tmdb, n), {'language': 'it-IT'})
        if not sd:
            continue
        eps = []
        for e in sd.get('episodes') or []:
            en = e.get('episode_number')
            if not isinstance(en, int) or en < 0 or en > 999:
                continue
            dt = e.get('air_date') or ''
            eps.append({'n': en, 't': (e.get('name') or '').strip()[:200], 'd': dt if DATE_RE.match(dt) else ''})
        eps.sort(key=lambda x: x['n'])
        stagioni.append({'n': n, 'nome': (sd.get('name') or '').strip()[:120], 'episodi': eps})
    stagioni.sort(key=lambda x: x['n'])
    return {'versione': 1, 'tmdb': tmdb, 'nome': (d.get('name') or '').strip(), 'lingua': 'it-IT', 'stagioni': stagioni}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', default='assets/images/catalog/tmdb_map.json')
    ap.add_argument('--out', default='assets/episodes')
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    voci = json.load(open(a.map, encoding='utf-8'))['voci']
    ovp = os.path.join(os.path.dirname(a.map), 'tmdb_overrides.json')   # correzioni manuali gia' usate da tmdb_sync
    if os.path.exists(ovp):
        for k, o in json.load(open(ovp, encoding='utf-8')).get('voci', {}).items():
            if o.get('t') == 'tv' and o.get('id'):
                voci[k] = dict(voci.get(k, {}), **o)
    only = set(x for x in a.only.split(',') if x)
    tv = {k: v for k, v in voci.items() if v.get('t') == 'tv' and (not only or k in only)}
    os.makedirs(a.out, exist_ok=True)
    idx_path = os.path.join(a.out, 'index.json')
    try:
        indice = json.load(open(idx_path, encoding='utf-8'))
        indice['voci'] = indice.get('voci') or {}
    except (OSError, ValueError):
        indice = {'versione': 1, 'fonte': 'TMDB', 'voci': {}}
    cache, falliti = {}, []
    for k in sorted(tv):
        tmdb = tv[k]['id']
        try:
            if tmdb not in cache:
                cache[tmdb] = clean_show(tmdb)
        except RuntimeError as e:
            falliti.append((k, str(e))); continue
        show = cache[tmdb]
        if not show or not show['stagioni']:
            falliti.append((k, 'nessun dato')); continue
        s = tv[k].get('s')
        sel = [x for x in show['stagioni'] if s is None or x['n'] == s]
        if not sel:
            falliti.append((k, 'stagione %s assente' % s)); continue
        with open(os.path.join(a.out, '%d.json' % tmdb), 'w', encoding='utf-8') as f:
            json.dump(show, f, ensure_ascii=False, separators=(',', ':'))
        v = {'nome': show['nome'], 'tmdb': tmdb, 'stagioni': len([x for x in sel if x['n'] > 0]),
             'episodi': sum(len(x['episodi']) for x in sel if x['n'] > 0), 'speciali': sum(len(x['episodi']) for x in sel if x['n'] == 0)}
        if s is not None:
            v['s'] = s
        indice['voci'][k] = v
    indice['aggiornato'] = datetime.date.today().isoformat()
    with open(idx_path, 'w', encoding='utf-8') as f:
        json.dump(indice, f, ensure_ascii=False, indent=1, sort_keys=True)
    print('Serie coperte: %d/%d - episodi: %d' % (len(indice['voci']), len(tv), sum(v['episodi'] for v in indice['voci'].values())))
    for k, m in falliti:
        print('  mancante', k, m)


if __name__ == '__main__':
    main()
