#!/usr/bin/env python3
"""A3.1 pilota - candidati di scena TMDB per 10 identita (SOLO METADATI, nessuna immagine scaricata).

Chiave: TMDB_READ_TOKEN (consigliato) o TMDB_API_KEY, SOLO da variabili d'ambiente (GitHub Secrets nel workflow).
Non viene mai scritta nell'output ne' nel frontend. Output: percorsi file TMDB (CDN image.tmdb.org) + dimensioni + voti.
Le immagini restano di proprieta' degli studi: qui non si copiano. Uso: python3 tools/atlante_pilot_tmdb.py --out DIR
Verifica offline (senza rete): python3 tools/atlante_pilot_tmdb.py --verifica
"""
import os, sys, json, re, time, argparse, unicodedata, urllib.request, urllib.parse, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://api.themoviedb.org/3'
SCHEMA = 1

def norm(x):
    x = unicodedata.normalize('NFD', (x or '').lower()); x = ''.join(c for c in x if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', x).strip()

# (N. voce Atlante, titolo inglese atteso, anno, tipo)
T = {
 '045': ('Iron Man', 2008, 'movie'), '047': ('Iron Man 2', 2010, 'movie'), '051': ('The Avengers', 2012, 'movie'),
 '053': ('Iron Man 3', 2013, 'movie'), '062': ('Avengers: Age of Ultron', 2015, 'movie'), '067': ('Captain America: Civil War', 2016, 'movie'),
 '075': ('Spider-Man: Homecoming', 2017, 'movie'), '084': ('Avengers: Infinity War', 2018, 'movie'), '089': ('Avengers: Endgame', 2019, 'movie'),
 '050': ('Thor', 2011, 'movie'), '055': ('Thor: The Dark World', 2013, 'movie'), '076': ('Thor: Ragnarok', 2017, 'movie'), '104': ('Thor: Love and Thunder', 2022, 'movie'),
 '095': ('Loki', 2021, 'tv'), '090': ('Spider-Man: Far From Home', 2019, 'movie'), '099': ('Spider-Man: No Way Home', 2021, 'movie'),
 '001': ('Spider-Man', 2002, 'movie'), '002': ('Spider-Man 2', 2004, 'movie'), '003': ('Spider-Man 3', 2007, 'movie'),
 '004': ('The Amazing Spider-Man', 2012, 'movie'), '005': ('The Amazing Spider-Man 2', 2014, 'movie'),
 '013': ('X-Men Origins: Wolverine', 2009, 'movie'), '014': ('X-Men', 2000, 'movie'), '015': ('X2', 2003, 'movie'), '016': ('X-Men: The Last Stand', 2006, 'movie'),
 '017': ('The Wolverine', 2013, 'movie'), '018': ('X-Men: Days of Future Past', 2014, 'movie'), '023': ('Logan', 2017, 'movie'), '117': ('Deadpool & Wolverine', 2024, 'movie'),
 '022': ('Deadpool', 2016, 'movie'), '024': ('Deadpool 2', 2018, 'movie'),
 '093': ('WandaVision', 2021, 'tv'), '102': ('Doctor Strange in the Multiverse of Madness', 2022, 'movie'),
}
# identita -> attore (per distinguere le varianti nello stesso titolo), regex del personaggio, titoli
P = [
 ('id-iron-man', 'Iron Man MCU', 'Robert Downey Jr.', r'tony stark|iron man', ['045','047','051','053','062','067','075','084','089'], ''),
 ('id-thor', 'Thor MCU', 'Chris Hemsworth', r'^thor', ['050','051','055','062','076','084','089','104'], ''),
 ('id-loki', 'Loki MCU', 'Tom Hiddleston', r'loki', ['050','051','055','076','095'], ''),
 ('id-peter-parker-mcu', 'Spider-Man MCU', 'Tom Holland', r'peter parker|spider', ['067','075','084','089','090','099'], 'No Way Home contiene tre Peter: scegli solo scene con Holland'),
 ('id-peter-parker-raimi', 'Spider-Man Raimi', 'Tobey Maguire', r'peter parker|spider', ['001','002','003','099'], 'No Way Home contiene tre Peter: scegli solo scene con Maguire'),
 ('id-peter-parker-garfield', 'Spider-Man Garfield', 'Andrew Garfield', r'peter parker|spider', ['004','005','099'], 'No Way Home contiene tre Peter: scegli solo scene con Garfield'),
 ('id-wolverine', 'Wolverine Fox', 'Hugh Jackman', r'logan|wolverine', ['013','014','015','016','017','018','023','117'], 'Solo titoli Fox: esclusa la serie animata X-Men 97 (variante diversa)'),
 ('id-wade-wilson-deadpool', 'Deadpool', 'Ryan Reynolds', r'wade wilson|deadpool', ['022','024','117'], 'Deadpool & Wolverine: variante Fox nel MCU'),
 ('id-wanda-maximoff', 'Wanda Maximoff MCU', 'Elizabeth Olsen', r'wanda|scarlet witch', ['062','084','089','093','102'], ''),
 ('id-thanos', 'Thanos MCU', 'Josh Brolin', r'thanos', ['084','089'], ''),
]

class Api:
    def __init__(self):
        self.tok = os.environ.get('TMDB_READ_TOKEN'); self.key = os.environ.get('TMDB_API_KEY'); self.n = 0
        if not self.tok and not self.key: sys.exit('Imposta TMDB_READ_TOKEN o TMDB_API_KEY (mai nel repository).')
    def get(self, path, **q):
        h = {'Accept': 'application/json'}
        if self.tok: h['Authorization'] = 'Bearer ' + self.tok
        else: q['api_key'] = self.key
        url = API + path + '?' + urllib.parse.urlencode(q)
        for k in range(4):
            try:
                self.n += 1
                with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r: return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and k < 3: time.sleep(2 + 3 * k); continue
                if e.code == 404: return None
                raise
            except urllib.error.URLError:
                if k < 3: time.sleep(2 + 3 * k); continue
                raise

def mappa():
    try: return json.load(open(os.path.join(ROOT, 'data/atlante/blob/tmdbMap.json')))['voci']
    except Exception: return {}

def risolvi(api, num, mp):
    tit, yr, tp = T[num]; g = (mp.get(num) or {}).get('id'); out = {'num': num, 'titolo_atteso': tit, 'tipo': tp, 'anno': yr, 'id_mappa': g, 'tmdb_id': None, 'titolo_tmdb': None, 'verificato': False, 'corretto_da_mappa': False}
    def anno_ok(d): return bool(d) and abs(int((d or '0000')[:4] or 0) - yr) <= 1
    if g:
        d = api.get('/%s/%s' % (tp, g), language='en-US')
        t = (d or {}).get('title') or (d or {}).get('name')
        if d and norm(t) == norm(tit) and anno_ok(d.get('release_date') or d.get('first_air_date')):
            out.update(tmdb_id=g, titolo_tmdb=t, verificato=True); return out
    q = {'query': tit, 'language': 'en-US'}; q['year' if tp == 'movie' else 'first_air_date_year'] = yr
    r = api.get('/search/' + tp, **q) or {}
    for c in r.get('results', []):
        t = c.get('title') or c.get('name')
        if norm(t) == norm(tit) and anno_ok(c.get('release_date') or c.get('first_air_date')):
            out.update(tmdb_id=c['id'], titolo_tmdb=t, verificato=True, corretto_da_mappa=bool(g and g != c['id'])); return out
    return out

def trova_attore(api, t, attore, rx):
    p = '/movie/%d/credits' if t['tipo'] == 'movie' else '/tv/%d/aggregate_credits'
    d = api.get(p % t['tmdb_id'], language='en-US') or {}
    for c in d.get('cast', []):
        chs = [c.get('character') or ''] + [x.get('character') or '' for x in c.get('roles', [])]
        if norm(c.get('name')) == norm(attore) and any(re.search(rx, norm(x)) for x in chs): return c['id'], c.get('name'), [x for x in chs if x][:2]
    for c in d.get('cast', []):
        if norm(c.get('name')) == norm(attore): return c['id'], c.get('name'), []
    return None, None, []

def immagini_titolo(api, t):
    d = api.get('/%s/%d/images' % (t['tipo'], t['tmdb_id']), include_image_language='null,en') or {}
    r = {}
    for b in d.get('backdrops', []):
        if b.get('width', 0) >= 1280: r[b['file_path']] = {'p': b['file_path'], 'w': b['width'], 'h': b['height'], 'v': round(b.get('vote_average') or 0, 2), 'n': b.get('vote_count') or 0, 'tag': False, 'src': 'backdrop'}
    return r

def tagged(api, pid, ids):
    out = {}
    for pg in range(1, 7):
        d = api.get('/person/%d/tagged_images' % pid, page=pg, language='en-US')
        if not d: break
        for b in d.get('results', []):
            m = b.get('media') or {}
            if m.get('id') in ids and b.get('image_type', 'backdrop') in ('backdrop', 'still', None) and b.get('width', 0) >= 1000 and b.get('file_path'):
                out[(m.get('id'), b['file_path'])] = {'w': b['width'], 'h': b['height'], 'v': round(b.get('vote_average') or 0, 2), 'n': b.get('vote_count') or 0}
        if pg >= (d.get('total_pages') or 1): break
    return out

def genera(api, per_titolo=24):
    mp = mappa(); cache = {}; res = []; avvisi = []
    for iid, nome, attore, rx, nums, nota in P:
        titoli = []; pid = None; pnome = None; chs = []
        for n in nums:
            if n not in cache: cache[n] = risolvi(api, n, mp); cache[n]['_img'] = immagini_titolo(api, cache[n]) if cache[n]['verificato'] else {}
            t = cache[n]; titoli.append(t)
            if not t['verificato']: avvisi.append('%s: titolo %s (%s) NON verificato' % (iid, n, t['titolo_atteso'])); continue
            if t['corretto_da_mappa']: avvisi.append('%s: id TMDB della mappa locandine errato per voce %s (%s -> %s)' % (iid, n, t['id_mappa'], t['tmdb_id']))
            if pid is None:
                pid, pnome, chs = trova_attore(api, t, attore, rx)
        if pid is None: avvisi.append('%s: attore %s non trovato nei crediti' % (iid, attore))
        tids = {t['tmdb_id']: t for t in titoli if t['tmdb_id']}
        tg = tagged(api, pid, set(tids)) if pid else {}
        imgs = []
        for t in titoli:
            if not t['verificato']: continue
            pool = {k: dict(v) for k, v in t['_img'].items()}
            for (mid, fp), v in tg.items():
                if mid == t['tmdb_id']:
                    if fp in pool: pool[fp]['tag'] = True
                    else: pool[fp] = {'p': fp, 'w': v['w'], 'h': v['h'], 'v': v['v'], 'n': v['n'], 'tag': True, 'src': 'tagged'}
            lst = sorted(pool.values(), key=lambda x: (not x['tag'], -x['v'], -x['n']))[:per_titolo]
            for x in lst: x['num'] = t['num']; imgs.append(x)
        res.append({'id': iid, 'nome': nome, 'nota': nota, 'attore': {'tmdb_person_id': pid, 'nome': pnome or attore, 'personaggio': chs, 'trovato': pid is not None},
                    'titoli': [{k: v for k, v in t.items() if not k.startswith('_')} for t in titoli], 'immagini': imgs})
    return {'schema': SCHEMA, 'generato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'fonte': 'TMDB (solo percorsi CDN, nessuna immagine copiata)', 'avvisi': avvisi, 'identita': res, 'richieste_api': api.n}

def report(o):
    L = ['# Pilota A3.1 - candidati scena TMDB', '', 'Richieste API: %d. Avvisi: %d' % (o['richieste_api'], len(o['avvisi'])), '']
    for a in o['avvisi']: L.append('- AVVISO ' + a)
    L += ['', '| Identita | Attore trovato | Titoli verificati | Candidati | Con attore taggato |', '|---|---|---|---|---|']
    for i in o['identita']:
        L.append('| %s | %s | %d/%d | %d | %d |' % (i['nome'], 'si' if i['attore']['trovato'] else 'NO', sum(t['verificato'] for t in i['titoli']), len(i['titoli']), len(i['immagini']), sum(1 for x in i['immagini'] if x['tag'])))
    return '\n'.join(L) + '\n'

def verifica_schema(o):
    errs = []
    if o.get('schema') != SCHEMA: errs.append('schema')
    ids = [x[0] for x in P]
    if [i['id'] for i in o.get('identita', [])] != ids: errs.append('identita diverse dal pilota')
    s = json.dumps(o)
    if re.search(r'api_key|bearer|TMDB_READ', s, re.I): errs.append('possibile chiave nell\'output')
    for i in o.get('identita', []):
        for x in i['immagini']:
            if not re.fullmatch(r'/[A-Za-z0-9_-]+\.(jpg|png)', x['p']): errs.append('percorso non valido ' + x['p'])
    return errs

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out'); ap.add_argument('--verifica', action='store_true'); ap.add_argument('--file'); a = ap.parse_args()
    if a.verifica:
        f = a.file or os.path.join(ROOT, 'atlante2/data/pilot/candidati.json')
        if not os.path.exists(f): print('candidati.json assente (ancora da generare con il workflow)'); sys.exit(0)
        e = verifica_schema(json.load(open(f))); print('OK' if not e else 'ERRORI: ' + '; '.join(e[:10])); sys.exit(1 if e else 0)
    if not a.out: sys.exit('--out richiesto')
    os.makedirs(a.out, exist_ok=True); o = genera(Api()); e = verifica_schema(o)
    json.dump(o, open(os.path.join(a.out, 'candidati.json'), 'w'), ensure_ascii=False, separators=(',', ':')); open(os.path.join(a.out, 'REPORT.md'), 'w').write(report(o) + ('\nERRORI SCHEMA: %s\n' % e if e else ''))
    print(report(o)); sys.exit(1 if e else 0)
