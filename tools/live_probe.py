#!/usr/bin/env python3
"""TVA Live - Fase 0: sonda di SOLA LETTURA sulle fonti dati.

Non modifica il repository, non scrive fuori da --out, non usa altri secret oltre a
TMDB_READ_TOKEN / TMDB_API_KEY (letti da ambiente, mai stampati ne' salvati).
Uso:  TMDB_READ_TOKEN=... python3 tools/live_probe.py --out live-probe-out [--days 900]
Output: report.json, REPORT.md, samples/*.json   (tutto ripulito da token/credenziali)
Solo libreria standard. Codice d'uscita 0 salvo fuga di credenziali nei file (1).
"""
import argparse, datetime as dt, json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = 'TVA-Archives-live-probe/1.0 (read-only; +https://github.com/)'
TMDB = 'https://api.themoviedb.org/3'
SECRETS = [v for v in (os.environ.get('TMDB_READ_TOKEN'), os.environ.get('TMDB_API_KEY')) if v]
KEEP_HDR = ('retry-after', 'x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset', 'server', 'date', 'content-type', 'cache-control')

R = {'meta': {}, 'checks': [], 'samples': {}}   # checks: {id, area, status OK|WARN|FAIL|SKIP, note}


def scrub(s):
    s = str(s)
    for sec in SECRETS:
        s = s.replace(sec, '[REDACTED]')
    s = re.sub(r'(api_key|access_token|Bearer)[=\s:]+[A-Za-z0-9._\-]{8,}', r'\1=[REDACTED]', s)
    return s


def check(cid, area, status, note):
    R['checks'].append({'id': cid, 'area': area, 'status': status, 'note': scrub(note)})
    print('[%s] %s - %s' % (status, cid, scrub(note)[:160]), flush=True)


def http(url, headers=None, timeout=20, max_bytes=3_000_000, tmdb=False):
    """GET con diagnostica. Mai URL con chiavi nell'output: si registra solo host+percorso."""
    h = {'User-Agent': UA, 'Accept': '*/*'}
    h.update(headers or {})
    out = {'status': None, 'error': None, 'ms': None, 'bytes': 0, 'final': None, 'ctype': None, 'hdr': {}, 'text': ''}
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(max_bytes + 1)
            out.update(status=r.status, final=r.geturl(), ctype=r.headers.get('content-type'))
            out['hdr'] = {k: r.headers.get(k) for k in KEEP_HDR if r.headers.get(k)}
    except urllib.error.HTTPError as e:
        raw = e.read(200_000) if hasattr(e, 'read') else b''
        out.update(status=e.code, error='HTTPError', final=e.geturl() if hasattr(e, 'geturl') else None)
        out['hdr'] = {k: e.headers.get(k) for k in KEEP_HDR if e.headers.get(k)}
    except Exception as e:
        raw = b''
        out['error'] = type(e).__name__ + ': ' + scrub(str(e))[:120]
    out['ms'] = int((time.time() - t0) * 1000)
    out['bytes'] = len(raw)
    out['truncated'] = len(raw) > max_bytes
    out['text'] = raw[:max_bytes].decode('utf-8', 'replace')
    if out['final']:
        p = urllib.parse.urlsplit(out['final'])
        out['final'] = p.scheme + '://' + p.netloc + p.path
    return out


# ------------------------------------------------------------------ TMDB
def tmdb(path, **q):
    q.setdefault('language', 'it-IT')
    hdr = {'Accept': 'application/json'}
    if os.environ.get('TMDB_READ_TOKEN'):
        hdr['Authorization'] = 'Bearer ' + os.environ['TMDB_READ_TOKEN']
    elif os.environ.get('TMDB_API_KEY'):
        q['api_key'] = os.environ['TMDB_API_KEY']
    for attempt in range(3):
        r = http(TMDB + path + '?' + urllib.parse.urlencode(q), hdr, tmdb=True)
        if r['status'] == 429 and attempt < 2:
            time.sleep(2 + 3 * attempt)
            continue
        break
    time.sleep(0.05)
    try:
        r['json'] = json.loads(r['text']) if r['text'] else None
    except ValueError:
        r['json'] = None
    return r


def load_timeline_map():
    try:
        m = json.load(open(os.path.join(ROOT, 'assets/images/catalog/tmdb_map.json'), encoding='utf-8'))['voci']
        try:
            ov = json.load(open(os.path.join(ROOT, 'assets/images/catalog/tmdb_overrides.json'), encoding='utf-8'))
            if isinstance(ov, dict):
                m = dict(m, **{k: v for k, v in (ov.get('voci', ov)).items() if isinstance(v, dict) and 'id' in v})
        except Exception:
            pass
        idx = {}
        for tid, v in m.items():
            if isinstance(v, dict) and v.get('id'):
                idx.setdefault((v.get('t'), int(v['id'])), []).append(tid)
        return idx
    except Exception as e:
        check('timeline-map', 'Timeline', 'WARN', 'tmdb_map.json non leggibile: %s' % type(e).__name__)
        return {}


def probe_tmdb(days):
    idx = load_timeline_map()
    R['meta']['timeline_tmdb_entries'] = len(idx)
    if not SECRETS:
        check('tmdb-auth', 'TMDB', 'FAIL', 'Nessun secret TMDB nell ambiente (TMDB_READ_TOKEN / TMDB_API_KEY).')
        return
    r = tmdb('/configuration')
    ok = r['status'] == 200 and isinstance(r.get('json'), dict)
    check('tmdb-auth', 'TMDB', 'OK' if ok else 'FAIL', 'GET /configuration -> HTTP %s (%s ms)%s' % (r['status'], r['ms'], '' if ok else ' | ' + str(r['error'])))
    R['samples']['tmdb_rate_headers'] = r['hdr']
    if not ok:
        return
    # identita' delle societa' (non si assume nessun ID: si cercano per nome e si mostrano)
    comp = {}
    for q in ('Marvel Studios', 'Marvel Entertainment', 'Marvel Animation', 'Marvel Television', 'Marvel Studios Animation'):
        for it in ((tmdb('/search/company', query=q).get('json') or {}).get('results') or []):
            if 'marvel' in (it.get('name') or '').lower():
                comp[it['id']] = {'name': it.get('name'), 'country': it.get('origin_country')}
    R['samples']['tmdb_marvel_companies'] = comp
    core = [cid for cid, v in comp.items() if re.search(r'marvel (studios|entertainment|animation|television)', v['name'].lower())]
    check('tmdb-companies', 'TMDB', 'OK' if core else 'WARN', 'Societa Marvel trovate: %d (core usate: %s)' % (len(comp), ', '.join('%s=%s' % (c, comp[c]['name']) for c in core) or 'nessuna'))
    kw = {}
    for q in ('marvel cinematic universe (mcu)', 'marvel cinematic universe', 'mcu'):
        for it in ((tmdb('/search/keyword', query=q).get('json') or {}).get('results') or []):
            if 'marvel' in it.get('name', '').lower() or it.get('name', '').lower() == 'mcu':
                kw[it['id']] = it['name']
    R['samples']['tmdb_keywords'] = kw
    check('tmdb-keywords', 'TMDB', 'OK' if kw else 'WARN', 'Keyword Marvel/MCU trovate: %s' % (', '.join('%s=%s' % kv for kv in kw.items()) or 'nessuna'))

    today = dt.date.today()
    d0, d1 = (today - dt.timedelta(days=14)).isoformat(), (today + dt.timedelta(days=days)).isoformat()
    R['meta']['window'] = [d0, d1]
    found = {}   # (kind,id) -> {signals:set, base fields}

    def run(label, kind, params, pages=3):
        n = 0
        for p in range(1, pages + 1):
            r = tmdb('/discover/' + kind, page=p, sort_by=('primary_release_date.asc' if kind == 'movie' else 'first_air_date.asc'), **params)
            j = r.get('json') or {}
            if r['status'] != 200:
                check('discover-' + label, 'TMDB', 'FAIL', 'discover/%s %s -> HTTP %s' % (kind, label, r['status']))
                return n
            for it in j.get('results') or []:
                k = ('movie' if kind == 'movie' else 'tv', it['id'])
                e = found.setdefault(k, {'signals': set(), 'title': it.get('title') or it.get('name'), 'date': it.get('release_date') or it.get('first_air_date'), 'poster': bool(it.get('poster_path'))})
                e['signals'].add(label)
                n += 1
            if p >= (j.get('total_pages') or 1):
                break
        return n

    counts = {}
    if core:
        cs = '|'.join(str(c) for c in core)
        counts['movie/company'] = run('company', 'movie', {'with_companies': cs, 'primary_release_date.gte': d0, 'primary_release_date.lte': d1})
        counts['movie/company+type2|3'] = run('company-theatrical', 'movie', {'with_companies': cs, 'primary_release_date.gte': d0, 'primary_release_date.lte': d1, 'with_release_type': '2|3', 'region': 'US'})
        counts['tv/company'] = run('company', 'tv', {'with_companies': cs, 'first_air_date.gte': d0, 'first_air_date.lte': d1})
    if kw:
        ks = '|'.join(str(k) for k in kw)
        counts['movie/keyword'] = run('keyword', 'movie', {'with_keywords': ks, 'primary_release_date.gte': d0, 'primary_release_date.lte': d1})
        counts['tv/keyword'] = run('keyword', 'tv', {'with_keywords': ks, 'first_air_date.gte': d0, 'first_air_date.lte': d1})
    R['meta']['discover_counts'] = counts
    check('discover-counts', 'TMDB', 'OK' if found else 'WARN', 'Risultati discover per query: %s | titoli unici: %d' % (json.dumps(counts), len(found)))

    # dettaglio (max 60) con date per paese, stato, societa: serve a misurare dati mancanti e rumore
    rows, miss = [], {'no_date': 0, 'no_poster': 0, 'no_it_date': 0, 'status_planned_or_rumored': 0, 'only_keyword_no_marvel_company': 0}
    for (kind, tid), e in sorted(found.items(), key=lambda kv: kv[1]['date'] or '9999')[:60]:
        if kind == 'movie':
            d = tmdb('/movie/%d' % tid, append_to_response='release_dates').get('json') or {}
            rel = {}
            for c in ((d.get('release_dates') or {}).get('results') or []):
                if c.get('iso_3166_1') in ('US', 'IT'):
                    rel[c['iso_3166_1']] = [{'t': x.get('type'), 'd': (x.get('release_date') or '')[:10]} for x in c.get('release_dates', [])]
            extra = {'status': d.get('status'), 'release_by_country': rel, 'collection': (d.get('belongs_to_collection') or {}).get('name')}
            if not rel.get('IT'):
                miss['no_it_date'] += 1
        else:
            d = tmdb('/tv/%d' % tid).get('json') or {}
            ne = d.get('next_episode_to_air') or {}
            extra = {'status': d.get('status'), 'seasons': d.get('number_of_seasons'), 'networks': [n.get('name') for n in d.get('networks') or []], 'next_episode': (ne.get('air_date') or None)}
        cos = [c.get('name') for c in d.get('production_companies') or []]
        has_marvel_co = any('marvel' in (c or '').lower() for c in cos)
        if not e['date']:
            miss['no_date'] += 1
        if not e['poster']:
            miss['no_poster'] += 1
        if (extra.get('status') or '') in ('Planned', 'Rumored', 'In Production', 'Post Production'):
            miss['status_planned_or_rumored'] += 1
        if e['signals'] == {'keyword'} and not has_marvel_co:
            miss['only_keyword_no_marvel_company'] += 1
        rows.append(dict({'key': '%s:%d' % (kind, tid), 'title': e['title'], 'date': e['date'], 'signals': sorted(e['signals']),
                          'in_timeline': idx.get((kind, tid)) or None, 'marvel_company': has_marvel_co, 'companies': cos[:5]}, **extra))
    R['samples']['tmdb_upcoming'] = rows
    R['meta']['upcoming_missing_data'] = miss
    new = [r for r in rows if not r['in_timeline']]
    noise = [r for r in rows if r['signals'] == ['keyword'] and not r['marvel_company']]
    R['meta']['upcoming_total'] = len(rows)
    R['meta']['upcoming_not_in_timeline'] = len(new)
    R['meta']['upcoming_noise_candidates'] = len(noise)
    check('upcoming-coverage', 'TMDB', 'OK' if rows else 'WARN', 'Prossime uscite: %d | gia in Timeline: %d | nuove (non in Timeline): %d | possibile rumore (solo keyword, senza societa Marvel): %d' % (len(rows), len(rows) - len(new), len(new), len(noise)))
    check('upcoming-missing', 'TMDB', 'WARN' if any(miss.values()) else 'OK', 'Dati mancanti: ' + json.dumps(miss))
    check('tmdb-limits', 'TMDB', 'WARN', 'discover non restituisce titoli SENZA data: i progetti annunciati senza data non sono rilevabili con questa query (limite noto, da gestire con lista manuale/fonti ufficiali).')


# ------------------------------------------------------------------ YouTube
YT_CANDIDATES = ['@marvel', '@MarvelEntertainment', '@MarvelHQ', '@marvelstudios', '@MarvelItalia', '@MarvelEntertainmentIT']
CH_RE = [r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[\w-]{22})"', r'"externalId":"(UC[\w-]{22})"', r'"channelId":"(UC[\w-]{22})"', r'itemprop="(?:channelId|identifier)" content="(UC[\w-]{22})"']
HDR_YT = {'Cookie': 'CONSENT=YES+1; SOCS=CAI', 'Accept-Language': 'en-US,en;q=0.8'}
ATOM = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}


def parse_yt_feed(txt):
    root = ET.fromstring(txt)
    title = (root.findtext('a:title', namespaces=ATOM) or '').strip()
    author = (root.findtext('a:author/a:name', namespaces=ATOM) or '').strip()
    ents = []
    for e in root.findall('a:entry', ATOM):
        ents.append({'id': e.findtext('yt:videoId', namespaces=ATOM), 'title': (e.findtext('a:title', namespaces=ATOM) or '').strip(),
                     'published': e.findtext('a:published', namespaces=ATOM), 'url': (e.find('a:link', ATOM).get('href') if e.find('a:link', ATOM) is not None else None)})
    return title, author, ents


def probe_marvel_links():
    """Identita' ufficiale: quali canali YouTube cita marvel.com stesso."""
    r = http('https://www.marvel.com/', {'Accept-Language': 'en-US'})
    links = sorted(set(re.findall(r'https?://(?:www\.)?youtube\.com/(?:@[\w.\-]+|channel/UC[\w-]{22}|c/[\w\-]+|user/[\w\-]+)', r['text'])))
    R['samples']['marvel_com_home'] = {'status': r['status'], 'bytes': r['bytes'], 'error': r['error'], 'youtube_links': links,
                                       'feed_links': re.findall(r'<link[^>]+type="application/(?:rss|atom)\+xml"[^>]*>', r['text'])[:10]}
    check('marvel-com-home', 'Notizie', 'OK' if r['status'] == 200 else 'WARN', 'marvel.com -> HTTP %s (%s B) | link YouTube dichiarati dal sito: %s' % (r['status'], r['bytes'], ', '.join(links) or 'nessuno'))
    return links, r['text']


def probe_youtube(declared_links, extra_handles):
    handles = list(dict.fromkeys(YT_CANDIDATES + [h for h in extra_handles if h]))
    for l in declared_links:
        m = re.search(r'youtube\.com/(@[\w.\-]+)', l)
        if m:
            handles.append(m.group(1))
    handles = list(dict.fromkeys(handles))
    res = []
    for h in handles:
        page = http('https://www.youtube.com/%s' % h, HDR_YT)
        cid = None
        for rx in CH_RE:
            m = re.search(rx, page['text'])
            if m:
                cid = m.group(1)
                break
        entry = {'handle': h, 'page_status': page['status'], 'channel_id': cid, 'declared_by_marvel_com': any(h.lower() in l.lower() for l in declared_links),
                 'verified_badge_in_html': 'BADGE_STYLE_TYPE_VERIFIED' in page['text'],
                 'og_title': (re.search(r'<meta property="og:title" content="([^"]+)"', page['text']) or [None, None])[1]}
        if cid:
            feed = None
            for attempt in range(3):
                feed = http('https://www.youtube.com/feeds/videos.xml?channel_id=' + cid)
                if feed['status'] == 200:
                    break
                time.sleep(2)
            entry['rss_status'] = feed['status']
            entry['rss_attempts'] = attempt + 1
            if feed['status'] == 200:
                try:
                    title, author, ents = parse_yt_feed(feed['text'])
                    kinds = lambda e: re.search(r'trailer|teaser|official', e['title'], re.I) is not None
                    entry.update(feed_title=title, feed_author=author, entries=len(ents), newest=(ents[0]['published'] if ents else None),
                                 trailer_like=sum(1 for e in ents if kinds(e)), sample=ents[:6])
                except ET.ParseError as e:
                    entry['rss_parse_error'] = str(e)[:80]
        res.append(entry)
    R['samples']['youtube_channels'] = res
    good = [e for e in res if e.get('entries')]
    for e in res:
        st = 'OK' if e.get('entries') else ('WARN' if e['page_status'] == 200 else 'FAIL')
        check('yt-' + e['handle'], 'YouTube', st, '%s -> pagina HTTP %s | channel_id %s | RSS %s | voci %s | titolo %s | dichiarato da marvel.com: %s' % (
            e['handle'], e['page_status'], e['channel_id'], e.get('rss_status'), e.get('entries'), e.get('feed_title') or e.get('og_title'), e['declared_by_marvel_com']))
    check('yt-summary', 'YouTube', 'OK' if good else 'FAIL', 'Canali con RSS utilizzabile: %d su %d. Identita ufficiale = DA CONFERMARE a mano se non dichiarata da marvel.com (vedi samples/youtube_channels).' % (len(good), len(res)))


# ------------------------------------------------------------------ Notizie
NEWS_CANDIDATES = ['https://www.marvel.com/rss', 'https://www.marvel.com/feed', 'https://www.marvel.com/feed.xml', 'https://www.marvel.com/articles/rss',
                   'https://www.marvel.com/articles/feed', 'https://www.marvel.com/news/feed', 'https://www.marvel.com/rss.xml', 'https://www.marvel.com/articles?format=rss']


def parse_feed(txt):
    head = txt.lstrip()[:300].lower()
    if '<rss' not in head and '<feed' not in head and '<?xml' not in head:
        return None
    root = ET.fromstring(txt)
    items = []
    if root.tag.endswith('rss') or root.find('channel') is not None:
        for it in root.iter('item'):
            items.append({'title': (it.findtext('title') or '').strip(), 'link': (it.findtext('link') or '').strip(), 'date': (it.findtext('pubDate') or '').strip()})
    else:
        ns = '{http://www.w3.org/2005/Atom}'
        for it in root.iter(ns + 'entry'):
            l = it.find(ns + 'link')
            items.append({'title': (it.findtext(ns + 'title') or '').strip(), 'link': l.get('href') if l is not None else '', 'date': it.findtext(ns + 'updated') or it.findtext(ns + 'published') or ''})
    return items


def probe_news(home_html):
    cands = list(NEWS_CANDIDATES)
    for tag in re.findall(r'<link[^>]+type="application/(?:rss|atom)\+xml"[^>]*>', home_html):
        m = re.search(r'href="([^"]+)"', tag)
        if m:
            cands.append(urllib.parse.urljoin('https://www.marvel.com/', m.group(1)))
    cands = list(dict.fromkeys(cands))
    out, usable = [], 0
    for u in cands:
        r = http(u, {'Accept': 'application/rss+xml, application/atom+xml, text/xml, */*'})
        entry = {'url': u, 'status': r['status'], 'ctype': r['ctype'], 'final': r['final'], 'bytes': r['bytes'], 'error': r['error'], 'is_feed': False}
        if r['status'] == 200:
            try:
                items = parse_feed(r['text'])
                if items is not None:
                    entry.update(is_feed=True, items=len(items), sample=items[:5])
                    usable += 1 if items else 0
            except ET.ParseError:
                entry['parse_error'] = True
        out.append(entry)
    R['samples']['news_candidates'] = out
    check('news-feeds', 'Notizie', 'OK' if usable else 'WARN', 'Candidati testati: %d | feed RSS/Atom validi con voci: %d' % (len(out), usable))
    rb = http('https://www.marvel.com/robots.txt')
    lines = [l.strip() for l in rb['text'].splitlines() if re.search(r'^(user-agent|disallow|sitemap)|rss|feed|articles', l, re.I)][:60]
    R['samples']['marvel_robots'] = {'status': rb['status'], 'relevant_lines': lines}
    check('news-robots', 'Notizie', 'OK' if rb['status'] == 200 else 'WARN', 'robots.txt marvel.com -> HTTP %s (righe rilevanti salvate nei campioni). I Termini d uso vanno letti a mano prima di qualsiasi uso automatico.' % rb['status'])
    wk = http('https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=timestamp&format=json&titles=List_of_Marvel_Cinematic_Universe_films')
    check('wikipedia', 'Fonti secondarie', 'OK' if wk['status'] == 200 else 'WARN', 'Wikipedia API (verifica incrociata opzionale, CC BY-SA) -> HTTP %s' % wk['status'])


# ------------------------------------------------------------------ Report
def diagnose():
    st = {c['id']: c['status'] for c in R['checks']}
    area = lambda a: [c for c in R['checks'] if c['area'] == a]
    d = []
    tm = [c for c in area('TMDB')]
    d.append(('TMDB (calendario)', 'utilizzabile' if st.get('tmdb-auth') == 'OK' and st.get('upcoming-coverage') == 'OK' else 'NON confermato'))
    d.append(('YouTube RSS (trailer)', 'utilizzabile' if st.get('yt-summary') == 'OK' else 'NON confermato'))
    d.append(('Feed notizie ufficiali', 'trovato' if st.get('news-feeds') == 'OK' else 'NON trovato: Live 1.0 senza notizie o con fonte alternativa da approvare'))
    d.append(('Aggiornamento automatico', 'NON garantito: la Fase 0 non lo verifica; serve una prova dedicata (cron su branch di default vs vincolo main congelato)'))
    return d


def write_out(out):
    os.makedirs(os.path.join(out, 'samples'), exist_ok=True)
    R['meta']['generated_at'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    R['meta']['runner'] = {'github_run_id': os.environ.get('GITHUB_RUN_ID'), 'sha': (os.environ.get('GITHUB_SHA') or '')[:7], 'ref': os.environ.get('GITHUB_REF_NAME')}
    R['meta']['secrets_present'] = {'TMDB_READ_TOKEN': bool(os.environ.get('TMDB_READ_TOKEN')), 'TMDB_API_KEY': bool(os.environ.get('TMDB_API_KEY'))}
    R['diagnosis'] = diagnose()
    for k, v in R['samples'].items():
        open(os.path.join(out, 'samples', k + '.json'), 'w', encoding='utf-8').write(scrub(json.dumps(v, ensure_ascii=False, indent=1, default=list)))
    rep = {'meta': R['meta'], 'checks': R['checks'], 'diagnosis': R['diagnosis']}
    open(os.path.join(out, 'report.json'), 'w', encoding='utf-8').write(scrub(json.dumps(rep, ensure_ascii=False, indent=1, default=list)))
    L = ['# TVA Live - Fase 0: esito sonde', '', 'Generato: %s (UTC) | run %s | sha %s' % (R['meta']['generated_at'], R['meta']['runner']['github_run_id'], R['meta']['runner']['sha']), '',
         '## Diagnosi', ''] + ['- **%s**: %s' % x for x in R['diagnosis']] + ['', '## Controlli', '', '| Esito | Area | Controllo | Nota |', '|---|---|---|---|']
    for c in R['checks']:
        L.append('| %s | %s | %s | %s |' % (c['status'], c['area'], c['id'], c['note'].replace('|', '/').replace('\n', ' ')))
    L += ['', '## Metriche', '', '```json', scrub(json.dumps(R['meta'], ensure_ascii=False, indent=1, default=list)), '```', '',
          'Campioni in `samples/`: tmdb_upcoming.json (prossime uscite con in_timeline / nuove / rumore), youtube_channels.json, news_candidates.json, marvel_robots.json.', '',
          'Nessun token o credenziale e incluso: i file sono scansionati prima del caricamento.']
    open(os.path.join(out, 'REPORT.md'), 'w', encoding='utf-8').write(scrub('\n'.join(L)))


def leak_scan(out):
    for dp, _, fs in os.walk(out):
        for f in fs:
            t = open(os.path.join(dp, f), encoding='utf-8', errors='replace').read()
            if any(s in t for s in SECRETS):
                return os.path.join(dp, f)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='live-probe-out')
    ap.add_argument('--days', type=int, default=900)
    ap.add_argument('--handles', default='', help='handle YouTube extra, separati da virgola')
    a = ap.parse_args()
    for name, fn in (('tmdb', lambda: probe_tmdb(a.days)),):
        try:
            fn()
        except Exception as e:
            check(name + '-crash', 'TMDB', 'FAIL', 'Eccezione: %s %s' % (type(e).__name__, str(e)[:100]))
    links, home = [], ''
    try:
        links, home = probe_marvel_links()
    except Exception as e:
        check('marvel-home-crash', 'Notizie', 'FAIL', 'Eccezione: %s' % type(e).__name__)
    try:
        probe_youtube(links, [h.strip() for h in a.handles.split(',')])
    except Exception as e:
        check('youtube-crash', 'YouTube', 'FAIL', 'Eccezione: %s %s' % (type(e).__name__, str(e)[:100]))
    try:
        probe_news(home)
    except Exception as e:
        check('news-crash', 'Notizie', 'FAIL', 'Eccezione: %s %s' % (type(e).__name__, str(e)[:100]))
    write_out(a.out)
    bad = leak_scan(a.out)
    if bad:
        for dp, _, fs in os.walk(a.out):
            for f in fs:
                os.remove(os.path.join(dp, f))
        sys.exit('Credenziale rilevata in %s: output eliminato.' % os.path.basename(bad))
    print('Report scritto in', a.out)


if __name__ == '__main__':
    main()
