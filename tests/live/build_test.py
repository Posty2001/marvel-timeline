#!/usr/bin/env python3
"""Test del generatore TVA Live (fixture locali, nessuna rete)."""
import copy, json, os, shutil, sys, tempfile, types, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['TMDB_READ_TOKEN'] = 'FAKE_TOKEN_SHOULD_NEVER_LEAK_123456'
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import tva_live_build as B

PASS = FAIL = 0
def ok(c, msg):
    global PASS, FAIL
    if c: PASS += 1
    else: FAIL += 1; print('  FAIL:', msg)

TODAY = '2026-11-21'
def mkroot(manual=None):
    r = tempfile.mkdtemp()
    os.makedirs(r + '/tools/live'); os.makedirs(r + '/assets/images/catalog')
    shutil.copy(ROOT + '/tools/live/config.json', r + '/tools/live/config.json')
    json.dump(manual or {'schema': 1, 'entries': [], 'exclude': []}, open(r + '/tools/live/manual.json', 'w'))
    json.dump({'voci': {'073': {'t': 'movie', 'id': 1, 'p': '/a.jpg'}, '043': {'t': 'tv', 'id': 61550, 'p': '/b.jpg', 's': 1}, '044': {'t': 'tv', 'id': 61550, 'p': '/c.jpg', 's': 2}}}, open(r + '/assets/images/catalog/tmdb_map.json', 'w'))
    json.dump({'voci': {}}, open(r + '/assets/images/catalog/tmdb_overrides.json', 'w'))
    return r

def D(title, date, status='Planned', cos=('Marvel Studios',), genres=(), poster='/p.jpg', rel=None):
    return {'title': title, 'release_date': date, 'status': status, 'poster_path': poster, 'genres': [{'id': g} for g in genres],
            'production_companies': [{'name': c} for c in cos], 'release_dates': rel if rel is not None else {'results': []}}

MOVIES = {
  1: D('Known Film', '2027-05-01', rel={'results': [{'iso_3166_1': 'IT', 'release_dates': [{'type': 3, 'release_date': '2027-05-02T00:00:00Z'}]}]}),
  2: D('New Hero', '2027-07-10'),
  3: D('Placeholder Saga', '2028-01-01'),
  4: D('Rumored Thing', '2027-09-01', status='Rumored'),
  5: D('The Marvel Podcast Special', '2027-02-02'),
  6: D('Unrelated Keyword Film', '2027-03-03', cos=('Some Studio',)),
  7: D('Doomsday Test', '2027-12-18', poster=None),
  8: D('Just Released', '2026-11-10', status='Released'),
  9: D('Doc About Making', '2027-04-04', genres=(99,)),
  10: D('Stale Date Film', '2026-11-15', status='Post Production'),
  12: D('Cancelled Film', '2027-06-06', status='Canceled'),
  13: D('Animated Wonder', '2027-10-10', genres=(16,)),
}
TV = {
  61550: {'name': 'Known Show', 'status': 'Returning Series', 'poster_path': '/s.jpg', 'genres': [], 'production_companies': [{'name': 'Marvel Television'}],
          'seasons': [{'season_number': 0, 'air_date': '2026-12-01'}, {'season_number': 1, 'air_date': '2015-04-10'}, {'season_number': 2, 'air_date': '2027-03-01', 'poster_path': '/s2.jpg'}]},
  40: {'name': 'Canceled But Dated', 'status': 'Canceled', 'in_production': False, 'poster_path': '/c.jpg', 'genres': [], 'production_companies': [{'name': 'Marvel Studios'}],
       'seasons': [{'season_number': 1, 'air_date': '2020-01-01'}, {'season_number': 2, 'air_date': '2027-04-04'}]},
  41: {'name': 'Canceled Truly Undated', 'status': 'Canceled', 'poster_path': None, 'genres': [], 'production_companies': [{'name': 'Marvel Studios'}], 'seasons': [{'season_number': 1, 'air_date': '2019-01-01'}]},
  30: {'name': 'Planned Without Date', 'status': 'Planned', 'poster_path': None, 'genres': [], 'production_companies': [{'name': 'Marvel Studios'}], 'seasons': []},
  50: {'name': 'Animated Series', 'status': 'Returning Series', 'poster_path': '/an.jpg', 'genres': [{'id': 16}], 'production_companies': [{'name': 'Marvel Animation'}], 'seasons': [{'season_number': 1, 'air_date': '2027-02-02'}]},
  20: {'name': 'Brand New Series', 'status': 'In Production', 'poster_path': None, 'genres': [], 'production_companies': [{'name': 'Marvel Studios'}],
       'seasons': [{'season_number': 1, 'air_date': '2027-08-20'}]},
}
TV[70] = {'name': 'Wonder Man', 'status': 'Canceled', 'in_production': False, 'poster_path': None, 'genres': [], 'production_companies': [{'name': 'Marvel Studios'}], 'number_of_seasons': 1,
          'seasons': [{'season_number': 1, 'air_date': '2026-01-27', 'episode_count': 8}], 'last_episode_to_air': {'air_date': '2026-03-10'}}
TV[71] = {'name': 'Spider-Noir', 'status': 'Returning Series', 'in_production': True, 'poster_path': None, 'genres': [], 'production_companies': [{'name': 'Amazon MGM'}], 'number_of_seasons': 2,
          'seasons': [{'season_number': 1, 'air_date': '2026-05-27', 'episode_count': 8}, {'season_number': 2, 'air_date': '2027-09-01', 'episode_count': 8}]}
SEARCH_TV = [{'id': 70, 'name': 'Wonder Man', 'first_air_date': '2026-01-27'}, {'id': 71, 'name': 'Spider-Noir', 'first_air_date': '2026-05-27'}, {'id': 72, 'name': 'Spider-Noir: Behind the Scenes', 'first_air_date': '2026-06-01'}]
CH = 'UCvC4D8onUfXzvjTOM-dBfEA'
def yt_feed(author='Marvel Entertainment'):
    def e(i, t, d, pub='2026-11-15'):
        return '<entry><yt:videoId>%s</yt:videoId><title>%s</title><link rel="alternate" href="https://www.youtube.com/watch?v=%s"/><published>%sT10:00:00+00:00</published><media:group><media:description>%s</media:description></media:group></entry>' % (i, t, i, pub, d)
    return ('<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom"><author><name>%s</name></author>' % author
            + e('AAAAAAAAAAA', 'Doomsday Test | Official Trailer', 'Only in theaters December 18. Tickets on sale.')
            + e('BBBBBBBBBBB', 'New Hero | Official Teaser', 'Coming soon.')
            + e('CCCCCCCCCCC', 'Marvel Podcast Episode 5 trailer', '')
            + e('DDDDDDDDDDD', 'Hot Toys unboxing', '')
            + e('FFFFFFFFFFF', 'Marvel Cosmic Invasion | The Siege of Castle Doom DLC #2 Launch Trailer', 'Available now on PlayStation, Xbox, Switch and PC.')
            + e('GGGGGGGGGGG', 'Mystery Project | Official Trailer', 'Nothing about its type.')
            + e('EEEEEEEEEEE', 'Doomsday Test | Official Trailer', 'dup title, other id', '2020-01-01')   # troppo vecchio
            + '</feed>')

class Net:
    def __init__(self, tmdb_ok=True, yt_ok=True, author='Marvel Entertainment', channel_in_page=True, fail_paths=()):
        self.fail_paths = fail_paths
        self.tmdb_ok, self.yt_ok, self.author, self.cip, self.log = tmdb_ok, yt_ok, author, channel_in_page, []
    def __call__(self, url, headers=None, **kw):
        self.log.append(url)
        R = lambda s, t='': {'status': s, 'text': t, 'error': None if s == 200 else 'HTTPError'}
        if 'themoviedb' in url:
            if not self.tmdb_ok: return R(500)
            p = urllib.parse.urlsplit(url).path.replace('/3', '', 1); q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            j = None
            if any(p.startswith(x) for x in self.fail_paths): return R(500)
            if p == '/search/tv': j = {'results': [r for r in SEARCH_TV if q.get('query', [''])[0].lower() in r['name'].lower()]}
            elif p == '/configuration': j = {'images': {}}
            elif p == '/search/company': j = {'results': [{'id': 420, 'name': 'Marvel Studios'}, {'id': 77, 'name': 'Marvel Productions'}, {'id': 5, 'name': 'Other'}]}
            elif p == '/search/keyword': j = {'results': [{'id': 180547, 'name': 'marvel cinematic universe (mcu)'}]}
            elif p == '/discover/movie':
                ids = [1, 2, 3, 4, 5, 7, 8, 9, 10, 12, 13] if 'with_companies' in q else [1, 6]
                j = {'total_pages': 1, 'results': [{'id': i} for i in ids]}
            elif p == '/discover/tv': j = {'total_pages': 1, 'results': ([{'id': 30, 'name': 'Planned Without Date'}, {'id': 20, 'name': 'Brand New Series'}] if 'with_status' in q else [{'id': 20}, {'id': 40}, {'id': 41}, {'id': 50}]) if 'with_companies' in q else []}
            elif p.startswith('/movie/'): j = MOVIES.get(int(p.split('/')[2]))
            elif p.startswith('/tv/'): j = TV.get(int(p.split('/')[2]))
            return R(200, json.dumps(j)) if j is not None else R(404)
        if 'youtube.com/feeds' in url:
            return R(200, yt_feed(self.author)) if self.yt_ok else R(404)
        if 'youtube.com/@' in url:
            return R(200, '<link rel="canonical" href="https://www.youtube.com/channel/%s">' % (CH if self.cip else 'UCxxxxxxxxxxxxxxxxxxxxxx'))
        return R(404)

def run(root, net, prev=None, today=TODAY):
    return B.run(types.SimpleNamespace(today=today, prev=prev), fetch=net, root=root)

def by_key(cal): return {i['key']: i for i in cal['items']}

# ---------------------------------------------------------------- scenario principale
print('1) classificazione, esclusioni, aggancio Timeline')
root = mkroot({'schema': 1, 'entries': [
    {'key': 'manual:announced-one', 'title': 'Announced Without Date', 'window': '2028', 'source_name': 'Marvel.com', 'source_url': 'https://www.marvel.com/x', 'verified_on': '2026-11-01'},
    {'key': 'manual:merge-new-hero', 'title': 'New Hero', 'date': '2027-07-10', 'source_name': 'Marvel.com', 'source_url': 'https://www.marvel.com/new-hero', 'verified_on': '2026-11-01', 'tmdb': {'type': 'movie', 'id': 2}},
    {'key': 'manual:dup-title', 'title': 'Brand New Series - Stagione 1', 'date': '2027-08-20', 'kind': 'season', 'source_name': 'Marvel.com', 'source_url': 'https://www.marvel.com/bns', 'verified_on': '2026-11-01'},
], 'exclude': ['tmdb:movie:9']})
net = Net()
cal, tr, man, excl, log = run(root, net)
K = by_key(cal)
ok(K['tmdb:movie:1']['timelineId'] == '073' and K['tmdb:movie:1']['confidence'] == 'provisional', 'film in Timeline agganciato e provvisorio')
ok(K['tmdb:movie:1']['dateIT'] == '2027-05-02', 'data IT letta')
ok(K['tmdb:tv:61550:S02']['timelineId'] == '044', 'stagione 2 agganciata alla scheda S2')
ok('tmdb:tv:61550:S01' not in K and 'tmdb:tv:61550:S00' not in K, 'stagione passata (>14gg) e speciali S0 non inclusi')
ok(K['tmdb:tv:20:S01']['timelineId'] is None and K['tmdb:tv:20:S01']['missing'] == ['poster', 'dateIT'] or 'poster' in K['tmdb:tv:20:S01']['missing'], 'nuova serie non in Timeline, poster mancante segnalato')
ok(K['tmdb:movie:3']['precision'] == 'year' and K['tmdb:movie:3']['confidence'] == 'provisional', 'data segnaposto 01-01 -> solo anno, provvisorio')
ok(K['tmdb:movie:7']['confidence'] == 'confirmed' and any(s['official'] for s in K['tmdb:movie:7']['sources']), 'data riportata da video ufficiale -> CONFERMATO con fonte')
ok(K['tmdb:movie:2']['confidence'] == 'confirmed' and K['tmdb:movie:2']['sources'][0]['name'] == 'Marvel.com', 'voce manuale con stessa data conferma e si fonde (non duplica)')
ok('manual:merge-new-hero' not in K, 'nessuna voce manuale duplicata per titolo TMDB')
ok(K['manual:announced-one']['state'] == 'announced' and K['manual:announced-one']['date'] is None and K['manual:announced-one']['window'] == '2028' and K['manual:announced-one']['confidence'] == 'provisional', 'annuncio manuale senza data: nessuna data inventata')
ok('manual:dup-title' not in K and 'tmdb:tv:20:S01' in K, 'dedup titolo+data uguali tra fonti diverse')
ok(K['tmdb:movie:8']['state'] == 'released' and K['tmdb:movie:8']['confidence'] is None, 'uscito di recente: state released, nessuna confidenza')
ok(K['tmdb:movie:10']['state'] == 'upcoming' and K['tmdb:movie:10']['confidence'] == 'provisional' and 'passato' in K['tmdb:movie:10']['reason'], 'data passata ma stato non aggiornato -> provvisorio da verificare')
for k in ('tmdb:movie:4', 'tmdb:movie:5', 'tmdb:movie:6', 'tmdb:movie:9'):
    ok(k not in K, 'escluso ' + k)
reasons = {e['key']: e['reason'] for e in excl}
ok('Rumored' in reasons['tmdb:movie:4'] and 'podcast' in reasons['tmdb:movie:5'] and 'societa Marvel' in reasons['tmdb:movie:6'] and 'manualmente' in reasons['tmdb:movie:9'], 'motivi di esclusione trasparenti')
ok(all(i['confidence'] != 'confirmed' or any(s['official'] for s in i['sources']) for i in cal['items']), 'mai CONFERMATO senza fonte ufficiale')
ok(not any(i['confidence'] == 'rumor' for i in cal['items']), 'nessuna indiscrezione')
tl = [i['timelineId'] for i in cal['items'] if i['timelineId'] and i['kind'] != 'season']
ok(len(tl) == len(set(tl)), 'nessuna scheda Timeline duplicata')

print('2) trailer: identita, filtri, collegamenti')
T = {t['key']: t for t in tr['items']}
ok(set(T) == {'yt:AAAAAAAAAAA', 'yt:BBBBBBBBBBB', 'yt:FFFFFFFFFFF', 'yt:GGGGGGGGGGG'}, 'solo trailer/teaser ufficiali recenti: %s' % sorted(T))
ok(T['yt:AAAAAAAAAAA']['relatesTo'] == 'tmdb:movie:7' and T['yt:BBBBBBBBBBB']['relatesTo'] == 'tmdb:movie:2', 'collegamento trailer->titolo univoco')
ok(T['yt:BBBBBBBBBBB']['kind'] == 'teaser', 'teaser riconosciuto')
ok(T['yt:FFFFFFFFFFF']['category'] == 'videogioco' and T['yt:FFFFFFFFFFF']['relatesTo'] is None, 'DLC di videogioco classificato videogioco, mai collegato a film/serie')
ok(T['yt:GGGGGGGGGGG']['category'] is None and T['yt:GGGGGGGGGGG']['categoryBasis'] == 'nessuna', 'trailer senza evidenza: nessuna categoria inventata')
ok(T['yt:AAAAAAAAAAA']['category'] == 'film' and T['yt:AAAAAAAAAAA']['categoryBasis'] == 'titolo collegato', 'categoria ereditata solo dal titolo collegato')
ok(man['sources']['youtube']['status'] == 'ok' and man['sources']['youtube']['identity'][0]['verified'] is True, 'identita @marvel verificata')
ok(man['sources']['youtube']['identity'][1]['enabled'] is False, '@MarvelHQ non abilitato')
ok(not any('MarvelHQ' in u or 'marvelstudios' in u.lower() or 'MarvelItalia' in u for u in net.log), 'nessuna richiesta a canali non autorizzati')
ok(man['sources']['news']['status'] == 'disabled' and not any('marvel.com' in u for u in net.log), 'News disabilitato, nessuna richiesta a marvel.com')

print('2b) stato Canceled, categorie, completezza')
ok('tmdb:tv:40:S02' in K and 'tmdb:tv:40:S02' in K and K['tmdb:tv:40:S02']['warnings'] == ['tmdb_canceled'] and K['tmdb:tv:40:S02']['confidence'] == 'provisional' and 'Attenzione' in K['tmdb:tv:40:S02']['reason'], 'serie Canceled con stagione datata: inclusa, provvisoria, con avviso (lo stato non e una prova)')
ok('tmdb:tv:41' not in K and 'tmdb:tv:41:S01' not in K and any(e['key'] == 'tmdb:tv:41' and 'dati insufficienti' in e['reason'] for e in excl), 'serie Canceled senza date: non reinserita, motivo trasparente')
ok('tmdb:movie:12' not in K and any(e['key'] == 'tmdb:movie:12' for e in excl), 'film Canceled escluso')
ok(K['tmdb:movie:13']['category'] == 'animazione' and K['tmdb:tv:50:S01']['category'] == 'animazione' and K['tmdb:movie:1']['category'] == 'film' and K['tmdb:tv:20:S01']['category'] == 'serie', 'categorie: animazione solo con genere TMDB, altrimenti film/serie dal tipo')
ok(any(d['key'] == 'tmdb:tv:40' and d['status'] == 'Canceled' and d['items_in_window'] == ['tmdb:tv:40:S02'] for d in log['tv_diagnostics']), 'diagnostica TV: stato, stagioni e decisione')
ok([u['key'] for u in log['undated_candidates']] == ['tmdb:tv:30'] and 'tmdb:tv:30' not in K, 'produzione TV pianificata senza data: solo in diagnostica, non pubblicata')
ok(any('film senza data' in l for l in log['limits']), 'limite dichiarato: film senza data non rilevabili')
ok(all(i['category'] in B.CATEGORIES for i in cal['items']), 'ogni voce ha una categoria valida')
print('3) identita non verificata -> nessun trailer')
_, tr2, man2, _, _ = run(mkroot(), Net(author='Qualcun Altro'))
ok(tr2['items'] == [] and man2['sources']['youtube']['status'] == 'unverified', 'autore incoerente: trailer non pubblicati')
_, tr3, man3, _, _ = run(mkroot(), Net(channel_in_page=False))
ok(tr3['items'] == [] and man3['sources']['youtube']['status'] == 'unverified', 'channel_id non risolto dall handle: trailer non pubblicati')

print('4) cronologia, idempotenza, fallback')
prev = tempfile.mkdtemp(); B.write_all(prev, cal, tr, man, excl, log)
cal_b, tr_b, man_b, _, _ = run(root, Net(), prev=prev, today='2026-11-22')
ok(by_key(cal_b)['tmdb:movie:1']['firstSeen'] == TODAY and by_key(cal_b)['tmdb:movie:1']['updatedAt'] == TODAY, 'firstSeen/updatedAt conservati se invariato')
ok(by_key(cal_b)['tmdb:movie:1']['confidence'] == 'provisional', 'data TMDB invariata: resta provvisoria')
ok(man_b['content_hash'] == man['content_hash'], 'idempotente: stesso contenuto, stesso hash')
MOVIES[2]['release_date'] = '2027-08-01'
cal_c, *_ = run(root, Net(), prev=prev, today='2026-11-22')
h = by_key(cal_c)['tmdb:movie:2']
ok(h['history'][-1] == {'at': '2026-11-22', 'from': '2027-07-10', 'to': '2027-08-01'} and h['confidence'] == 'provisional', 'cambio data registrato; la conferma manuale (data diversa) non resta')
MOVIES[2]['release_date'] = '2027-07-10'
cal_d, tr_d, man_d, _, log_d = run(root, Net(tmdb_ok=False, yt_ok=False), prev=prev)
ok(man_d['sources']['tmdb']['status'] == 'stale' and cal_d['items'] == cal['items'], 'TMDB giu: ultimo calendario valido mantenuto (stale)')
ok(man_d['sources']['youtube']['status'] == 'stale' and tr_d['items'] == tr['items'], 'YouTube giu: ultimi trailer validi mantenuti (stale)')
cal_e, _, man_e, _, _ = run(mkroot(), Net(tmdb_ok=False))
ok(man_e['sources']['tmdb']['status'] == 'error' and cal_e['items'] == [], 'TMDB giu senza precedente: errore dichiarato, calendario vuoto valido')

print('4b) diagnostica titoli richiesti e errori parziali')
diag = {e['query']: e for e in log['requested_diagnostics']}
wm, sn = diag['Wonder Man']['matches'][0], diag['Spider-Noir']['matches'][0]
ok(wm['status'] == 'Canceled' and wm['future_dated'] is False and 'NON e una prova' in wm['verdict'], 'Wonder Man: stato generale Canceled, nessuna stagione futura: dati insufficienti, non prova di cancellazione')
ok(sn['status'] == 'Returning Series' and sn['future_dated'] is True and 'S02 2027-09-01' in sn['verdict'], 'Spider-Noir: stagione futura datata distinta dallo stato generale')
ok(len(diag['Spider-Noir']['matches']) == 1 and diag['Spider-Noir']['search_results'][1]['id'] == 72, 'diagnostica: solo corrispondenza esatta del titolo, altri risultati solo elencati')
ok('tmdb:tv:70' not in K and 'tmdb:tv:71:S02' not in K and 'tmdb:tv:71' not in K, 'diagnostica NON pubblica nulla nel calendario')
rep_txt = open(os.path.join(tempfile.mkdtemp(), 'x'), 'w') if False else None
dd = tempfile.mkdtemp(); B.write_all(dd, cal, tr, man, excl, log); R = open(dd + '/REPORT.md', encoding='utf-8').read()
ok('Diagnostica titoli richiesti' in R and 'Wonder Man' in R and 'Spider-Noir' in R and 'stato generale' in R, 'REPORT: sezione diagnostica titoli richiesti')
prevp = tempfile.mkdtemp(); B.write_all(prevp, cal, tr, man, excl, log)
cal_p, _, man_p, _, log_p = run(root, Net(fail_paths=('/movie/2',)), prev=prevp)
ok(man_p['sources']['tmdb']['status'] == 'partial' and 'tmdb:movie:2' in by_key(cal_p) and 'tmdb:movie:2' in log_p['partial_carried_over'], 'errore parziale TMDB: la voce del catalogo valido non viene persa')
ok(by_key(cal_p)['tmdb:movie:2'] == by_key(cal)['tmdb:movie:2'], 'voce mantenuta identica (nessuna modifica inventata)')

print('5) validazione')
cfg = B.load_json(ROOT + '/tools/live/config.json')
def expect_fail(mut, label):
    c, t, m = copy.deepcopy(cal), copy.deepcopy(tr), copy.deepcopy(man); mut(c, t, m)
    try: B.validate(c, t, m, cfg); ok(False, label)
    except B.ValidationError: ok(True, label)
expect_fail(lambda c, t, m: c['items'][0].update(confidence='confirmed', sources=[{'name': 'TMDB', 'url': 'https://x.org', 'official': False}], state='upcoming', date='2027-01-01'), 'CONFERMATO senza fonte ufficiale rifiutato')
expect_fail(lambda c, t, m: c['items'].append(copy.deepcopy(c['items'][0])), 'chiave duplicata rifiutata')
expect_fail(lambda c, t, m: c['items'][0].update(date='21/11/2026'), 'data malformata rifiutata')
expect_fail(lambda c, t, m: c['items'][0].update(sources=[{'name': 'x', 'url': 'http://insecure', 'official': False}]), 'fonte non https rifiutata')
expect_fail(lambda c, t, m: t['items'][0].update(relatesTo='tmdb:movie:99999'), 'relatesTo inesistente rifiutato')
expect_fail(lambda c, t, m: c['items'].extend(copy.deepcopy(c['items']) * 0 + [dict(copy.deepcopy(c['items'][1]), key='tmdb:movie:777', timelineId='073'), dict(copy.deepcopy(c['items'][2]), key='tmdb:movie:778', timelineId='073')]), 'stessa scheda Timeline su due voci rifiutata')
expect_fail(lambda c, t, m: c['items'][0].update(confidence=None, state='upcoming'), 'upcoming senza confidenza rifiutato')
for bad, lab in (({'entries': [{'key': 'manual:abc', 'title': 'x'}]}, 'voce manuale senza fonte'), ({'entries': [{'key': 'manual:abc', 'title': 'x', 'source_name': 'a', 'source_url': 'http://x', 'verified_on': '2026-01-01'}]}, 'source_url non https')):
    try: B.validate_manual(bad); ok(False, lab)
    except B.ValidationError: ok(True, lab + ' rifiutata')
ok(len(json.dumps(cal)) < cfg['budget_bytes']['calendar'], 'budget dimensione rispettato')

print('6) sicurezza output')
out = tempfile.mkdtemp(); B.write_all(out, cal, tr, man, excl, log)
txt = ''.join(open(os.path.join(out, f), encoding='utf-8').read() for f in os.listdir(out))
ok('FAKE_TOKEN' not in txt and 'Bearer' not in txt and 'api_key' not in txt, 'nessun token/credenziale nei file')
ok(not any('FAKE_TOKEN' in u for u in net.log), 'token mai nell URL (solo intestazione)')

print('6b) dati reali integrati (assets/live)')
if os.path.exists(ROOT + '/assets/live/calendar.json') and not (B.load_json(ROOT + '/assets/live/manifest.json') or {}).get('seed'):
    rc, rt, rm = [B.load_json(ROOT + '/assets/live/%s.json' % n) for n in ('calendar', 'trailers', 'manifest')]
    try: B.validate(rc, rt, rm, cfg); ok(True, 'JSON reali validi')
    except B.ValidationError as e: ok(False, 'JSON reali validi: %s' % e)
    ok(all(i['confidence'] == 'provisional' or any(s.get('official') for s in i['sources']) for i in rc['items'] if i['state'] == 'upcoming'), 'date reali: Confermato solo con fonte ufficiale (il resto resta provvisorio)')
    ok(all(i['timelineId'] is None or i['key'].startswith('tmdb') for i in rc['items']) and len({i['timelineId'] for i in rc['items'] if i['timelineId']}) == sum(1 for i in rc['items'] if i['timelineId']), 'Timeline: nessuna scheda doppia, voci nuove solo in Live')
print('7) date da testo ufficiale')
ok(B.dates_in_text('In theaters December 18', 2027) == {'2027-12-18'}, 'Month D')
ok(B.dates_in_text('Coming 18 Dec 2027', 2026) == {'2027-12-18'}, 'D Mon YYYY')
ok(B.dates_in_text('May 1st, 2028', 2026) == {'2028-05-01'}, 'ordinale')
ok(B.dates_in_text('this summer', 2027) == set(), 'nessuna data inventata')
print('RISULTATO: %d ok, %d falliti' % (PASS, FAIL)); sys.exit(1 if FAIL else 0)
