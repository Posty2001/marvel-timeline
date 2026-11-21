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
}
TV = {
  61550: {'name': 'Known Show', 'status': 'Returning Series', 'poster_path': '/s.jpg', 'genres': [], 'production_companies': [{'name': 'Marvel Television'}],
          'seasons': [{'season_number': 0, 'air_date': '2026-12-01'}, {'season_number': 1, 'air_date': '2015-04-10'}, {'season_number': 2, 'air_date': '2027-03-01', 'poster_path': '/s2.jpg'}]},
  20: {'name': 'Brand New Series', 'status': 'In Production', 'poster_path': None, 'genres': [], 'production_companies': [{'name': 'Marvel Studios'}],
       'seasons': [{'season_number': 1, 'air_date': '2027-08-20'}]},
}
CH = 'UCvC4D8onUfXzvjTOM-dBfEA'
def yt_feed(author='Marvel Entertainment'):
    def e(i, t, d, pub='2026-11-15'):
        return '<entry><yt:videoId>%s</yt:videoId><title>%s</title><link rel="alternate" href="https://www.youtube.com/watch?v=%s"/><published>%sT10:00:00+00:00</published><media:group><media:description>%s</media:description></media:group></entry>' % (i, t, i, pub, d)
    return ('<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom"><author><name>%s</name></author>' % author
            + e('AAAAAAAAAAA', 'Doomsday Test | Official Trailer', 'Only in theaters December 18. Tickets on sale.')
            + e('BBBBBBBBBBB', 'New Hero | Official Teaser', 'Coming soon.')
            + e('CCCCCCCCCCC', 'Marvel Podcast Episode 5 trailer', '')
            + e('DDDDDDDDDDD', 'Hot Toys unboxing', '')
            + e('EEEEEEEEEEE', 'Doomsday Test | Official Trailer', 'dup title, other id', '2020-01-01')   # troppo vecchio
            + '</feed>')

class Net:
    def __init__(self, tmdb_ok=True, yt_ok=True, author='Marvel Entertainment', channel_in_page=True):
        self.tmdb_ok, self.yt_ok, self.author, self.cip, self.log = tmdb_ok, yt_ok, author, channel_in_page, []
    def __call__(self, url, headers=None, **kw):
        self.log.append(url)
        R = lambda s, t='': {'status': s, 'text': t, 'error': None if s == 200 else 'HTTPError'}
        if 'themoviedb' in url:
            if not self.tmdb_ok: return R(500)
            p = urllib.parse.urlsplit(url).path.replace('/3', '', 1); q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
            j = None
            if p == '/configuration': j = {'images': {}}
            elif p == '/search/company': j = {'results': [{'id': 420, 'name': 'Marvel Studios'}, {'id': 77, 'name': 'Marvel Productions'}, {'id': 5, 'name': 'Other'}]}
            elif p == '/search/keyword': j = {'results': [{'id': 180547, 'name': 'marvel cinematic universe (mcu)'}]}
            elif p == '/discover/movie':
                ids = [1, 2, 3, 4, 5, 7, 8, 9, 10] if 'with_companies' in q else [1, 6]
                j = {'total_pages': 1, 'results': [{'id': i} for i in ids]}
            elif p == '/discover/tv': j = {'total_pages': 1, 'results': [{'id': 20}] if 'with_companies' in q else []}
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
ok(set(T) == {'yt:AAAAAAAAAAA', 'yt:BBBBBBBBBBB'}, 'solo trailer/teaser ufficiali recenti: %s' % sorted(T))
ok(T['yt:AAAAAAAAAAA']['relatesTo'] == 'tmdb:movie:7' and T['yt:BBBBBBBBBBB']['relatesTo'] == 'tmdb:movie:2', 'collegamento trailer->titolo univoco')
ok(T['yt:BBBBBBBBBBB']['kind'] == 'teaser', 'teaser riconosciuto')
ok(man['sources']['youtube']['status'] == 'ok' and man['sources']['youtube']['identity'][0]['verified'] is True, 'identita @marvel verificata')
ok(man['sources']['youtube']['identity'][1]['enabled'] is False, '@MarvelHQ non abilitato')
ok(not any('MarvelHQ' in u or 'marvelstudios' in u.lower() or 'MarvelItalia' in u for u in net.log), 'nessuna richiesta a canali non autorizzati')
ok(man['sources']['news']['status'] == 'disabled' and not any('marvel.com' in u for u in net.log), 'News disabilitato, nessuna richiesta a marvel.com')

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

print('7) date da testo ufficiale')
ok(B.dates_in_text('In theaters December 18', 2027) == {'2027-12-18'}, 'Month D')
ok(B.dates_in_text('Coming 18 Dec 2027', 2026) == {'2027-12-18'}, 'D Mon YYYY')
ok(B.dates_in_text('May 1st, 2028', 2026) == {'2028-05-01'}, 'ordinale')
ok(B.dates_in_text('this summer', 2027) == set(), 'nessuna data inventata')
print('RISULTATO: %d ok, %d falliti' % (PASS, FAIL)); sys.exit(1 if FAIL else 0)
