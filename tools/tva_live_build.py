#!/usr/bin/env python3
"""TVA Live 1.0 - generatore dei JSON statici (assets/live/*.json).

Uso:  TMDB_READ_TOKEN=... python3 tools/tva_live_build.py --out live-data [--prev assets/live] [--today YYYY-MM-DD]
Non scrive mai in assets/live direttamente e non fa commit: produce una cartella --out
(calendar.json, trailers.json, manifest.json, REPORT.md) da scaricare come artifact e integrare a mano.
Solo libreria standard. Il token TMDB e' letto dall'ambiente e non compare mai nei file.

Regole di classificazione (vedi docs/TVA_LIVE.md):
  - confidence 'confirmed' SOLO con una fonte ufficiale verificabile (video del canale ufficiale che riporta la
    stessa data, oppure voce manuale con source_url ufficiale e data). Una data TMDB, anche stabile, resta 'provisional'.
  - nessuna indiscrezione: stato TMDB Rumored/Canceled escluso; voci senza societa Marvel (solo keyword) escluse.
  - titoli gia usciti: state 'released', confidence null (non e un'informazione di calendario).
"""
import argparse, datetime as dt, hashlib, json, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = 1
UA = 'TVA-Archives-live-build/1.0 (read-only)'
TMDB = 'https://api.themoviedb.org/3'
CATEGORIES = ('film', 'serie', 'animazione', 'videogioco')
WARNINGS = ('tmdb_canceled',)
TV_STATUS_IT = {'Returning Series': 'Serie in corso', 'In Production': 'In produzione', 'Planned': 'Progetto pianificato', 'Pilot': 'Episodio pilota', 'Ended': 'Serie conclusa', 'Canceled': 'Serie segnata come cancellata'}
KEY_RE = re.compile(r'^(tmdb:(movie|tv):\d+(:S\d{2})?|manual:[a-z0-9\-]{3,60})$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SECRETS = [v for v in (os.environ.get('TMDB_READ_TOKEN'), os.environ.get('TMDB_API_KEY')) if v]
ATOM = {'a': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}
MONTHS = {m: i + 1 for i, m in enumerate(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS['sept'] = 9


# ------------------------------------------------------------------ utilita
def scrub(s):
    s = str(s)
    for sec in SECRETS:
        s = s.replace(sec, '[REDACTED]')
    return s


def norm(t):
    t = unicodedata.normalize('NFKD', t or '').encode('ascii', 'ignore').decode().lower()
    t = re.sub(r"[’'`]", '', t)
    t = re.sub(r'\b(marvel studios|marvels?|disney\+?|official|il|lo|la|the|a|an)\b', ' ', t)
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()


def title_base(t):
    """Titolo dell'opera da un titolo video: 'Avengers | Official Trailer' -> 'avengers' (normalizzato)."""
    t = re.split(r'\s[|\u2013\u2014]\s|\s-\s', t or '')[0]
    t = re.sub(r'(?i)\b(official|final|teaser|trailer|first look|new look)\b.*$', '', t)
    return norm(t)


def http(url, headers=None, timeout=20, max_bytes=2_000_000):
    h = {'User-Agent': UA, 'Accept': '*/*'}
    h.update(headers or {})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
            return {'status': r.status, 'text': r.read(max_bytes).decode('utf-8', 'replace'), 'error': None}
    except urllib.error.HTTPError as e:
        return {'status': e.code, 'text': '', 'error': 'HTTPError'}
    except Exception as e:
        return {'status': None, 'text': '', 'error': type(e).__name__}


class Tmdb:
    """Client minimale: il token resta nell'intestazione, mai nell'URL ne' nei log."""
    def __init__(self, fetch=http):
        self.fetch, self.calls, self.errors = fetch, 0, []

    def get(self, path, **q):
        q.setdefault('language', 'it-IT')
        hdr = {'Accept': 'application/json'}
        if os.environ.get('TMDB_READ_TOKEN'):
            hdr['Authorization'] = 'Bearer ' + os.environ['TMDB_READ_TOKEN']
        elif os.environ.get('TMDB_API_KEY'):
            q['api_key'] = os.environ['TMDB_API_KEY']
        r = None
        for attempt in range(3):
            self.calls += 1
            r = self.fetch(TMDB + path + '?' + urllib.parse.urlencode(q), hdr)
            if r['status'] == 429 and attempt < 2:
                time.sleep(2 + 3 * attempt)
                continue
            break
        time.sleep(0.03)
        if r['status'] != 200:
            self.errors.append({'path': path, 'status': r['status'], 'error': r['error']})
            return None
        try:
            return json.loads(r['text'])
        except ValueError:
            self.errors.append({'path': path, 'status': 200, 'error': 'JSON non valido'})
            return None


# ------------------------------------------------------------------ Timeline
def load_json(path, default=None):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def timeline_index(root=ROOT):
    """(tipo, tmdbId) -> [(idTimeline, stagione|None)] da tmdb_map + overrides (skip escluso)."""
    voci = dict((load_json(os.path.join(root, 'assets/images/catalog/tmdb_map.json'), {}) or {}).get('voci', {}))
    ov = (load_json(os.path.join(root, 'assets/images/catalog/tmdb_overrides.json'), {}) or {}).get('voci', {})
    for k, v in ov.items():
        if isinstance(v, dict) and v.get('skip'):
            voci.pop(k, None)
        elif isinstance(v, dict) and v.get('id'):
            voci[k] = dict(voci.get(k, {}), **v)
    idx = {}
    for tid, v in voci.items():
        if isinstance(v, dict) and v.get('id') and v.get('t') in ('movie', 'tv'):
            idx.setdefault((v['t'], int(v['id'])), []).append((tid, v.get('s'), v.get('p')))
    return idx


def link_timeline(idx, ttype, tid, season=None):
    ents = idx.get((ttype, tid))
    if not ents:
        return None
    if ttype == 'movie' or season is None:
        return ents[0][0]
    for card, s, _ in ents:
        if s == season:
            return card
    for card, s, _ in ents:
        if s is None:        # scheda "intera serie"
            return card
    return None


# ------------------------------------------------------------------ date da testo ufficiale
def dates_in_text(text, ref_year):
    """Estrae date 'Month D[, YYYY]' / 'D Month[ YYYY]' (EN). Senza anno: ref_year."""
    out = set()
    t = (text or '').lower()
    pats = [r'\b(%s)\.?\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?\b', r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(%s)\.?(?:,?\s+(\d{4}))?\b']
    mon = '|'.join(sorted(MONTHS, key=len, reverse=True))
    for i, p in enumerate(pats):
        for m in re.finditer(p % mon, t):
            mo, d, y = (m.group(1), m.group(2), m.group(3)) if i == 0 else (m.group(2), m.group(1), m.group(3))
            try:
                out.add(dt.date(int(y) if y else ref_year, MONTHS[mo], int(d)).isoformat())
            except (ValueError, KeyError):
                pass
    return out


# ------------------------------------------------------------------ TMDB -> voci calendario
def is_placeholder(date, cfg):
    return bool(date) and date[5:] in cfg['placeholder_dates_mmdd']


def classify_tmdb(date, status, today, official_dates, cfg):
    """Ritorna (state, confidence, precision, reason). Mai 'confirmed' senza fonte ufficiale."""
    if not date:
        return 'announced', 'provisional', 'none', 'Data non indicata dalle fonti'
    if date < today:
        if status in ('Released', 'Ended', 'Returning Series'):
            return 'released', None, 'day', 'Gia uscito'
        return 'upcoming', 'provisional', 'day', 'Data nel passato ma stato TMDB non aggiornato (%s): da verificare' % (status or 'n/d')
    if date in official_dates:
        return 'upcoming', 'confirmed', 'day', 'Data riportata da un contenuto ufficiale verificato (vedi fonte)'
    if is_placeholder(date, cfg):
        return 'upcoming', 'provisional', 'year', 'Data segnaposto TMDB (inizio/fine anno): solo l anno e indicativo'
    why = {'Planned': 'Progetto pianificato', 'In Production': 'In produzione', 'Post Production': 'In post-produzione', 'Released': 'Gia uscito', **TV_STATUS_IT}.get(status or '', 'Stato non specificato')
    return 'upcoming', 'provisional', 'day', 'Data da TMDB, non confermata da una fonte ufficiale. ' + why


def build_calendar(tmdb, cfg, idx, today, manual, official_text_by_title, log):
    c = cfg['tmdb']
    d0 = (dt.date.fromisoformat(today) - dt.timedelta(days=cfg['window']['past_days'])).isoformat()
    d1 = (dt.date.fromisoformat(today) + dt.timedelta(days=cfg['window']['future_days'])).isoformat()
    excluded, found = [], {}
    comp_re = re.compile(c['company_name_regex'], re.I)
    core = []
    for q in ('Marvel Studios', 'Marvel Entertainment', 'Marvel Animation', 'Marvel Television'):
        for it in ((tmdb.get('/search/company', query=q) or {}).get('results') or []):
            if comp_re.search(it.get('name') or '') and it['id'] not in core:
                core.append(it['id'])
    kws = []
    for q in c['keyword_names']:
        for it in ((tmdb.get('/search/keyword', query=q) or {}).get('results') or []):
            if (it.get('name') or '').lower() in [k.lower() for k in c['keyword_names']] and it['id'] not in kws:
                kws.append(it['id'])
    log['tmdb_company_ids'], log['tmdb_keyword_ids'] = core, kws

    def run(sig, kind, params):
        for p in range(1, 4):
            sort = 'primary_release_date.asc' if kind == 'movie' else 'first_air_date.asc'
            j = tmdb.get('/discover/' + kind, page=p, sort_by=sort, **params) or {}
            for it in j.get('results') or []:
                k = (kind, it['id'])
                found.setdefault(k, set()).add(sig)
            if p >= (j.get('total_pages') or 1):
                break
    if core:
        cs = '|'.join(map(str, core))
        run('company', 'movie', {'with_companies': cs, 'primary_release_date.gte': d0, 'primary_release_date.lte': d1})
        run('company', 'tv', {'with_companies': cs, 'first_air_date.gte': d0, 'first_air_date.lte': d1})
    if kws:
        ks = '|'.join(map(str, kws))
        run('keyword', 'movie', {'with_keywords': ks, 'primary_release_date.gte': d0, 'primary_release_date.lte': d1})
        run('keyword', 'tv', {'with_keywords': ks, 'first_air_date.gte': d0, 'first_air_date.lte': d1})
    # serie gia in Timeline: nuove stagioni (discover per first_air_date non le vede)
    for (t, tid) in sorted(idx):
        if t == 'tv':
            found.setdefault((t, tid), set()).add('timeline')
    log['candidates'] = len(found)

    items, budget = {}, c['max_detail_requests']
    excl_manual = set(manual.get('exclude') or [])
    for (kind, tid), sigs in sorted(found.items()):
        key0 = 'tmdb:%s:%d' % (kind, tid)
        if key0 in excl_manual:
            excluded.append({'key': key0, 'reason': 'Escluso manualmente (tools/live/manual.json)'})
            continue
        if budget <= 0:
            log.setdefault('warnings', []).append('Limite richieste di dettaglio raggiunto: candidati rimanenti ignorati')
            break
        budget -= 1
        d = tmdb.get('/%s/%d' % (kind, tid), **({'append_to_response': 'release_dates'} if kind == 'movie' else {}))
        if not d:
            excluded.append({'key': key0, 'reason': 'Dettaglio TMDB non disponibile'})
            continue
        title = d.get('title') or d.get('name') or ''
        in_tl = (kind, tid) in idx
        cos = [x.get('name') or '' for x in d.get('production_companies') or []]
        marvel_co = any(comp_re.search(x) for x in cos)
        genres = [g.get('id') for g in d.get('genres') or []]
        why = None
        status = d.get('status')
        if status in (c['exclude_status_movie'] if kind == 'movie' else c['exclude_status_tv']):
            why = 'Stato TMDB %s (%s)' % (status, 'film: non e una produzione confermata' if kind == 'movie' else 'non e una produzione confermata')
        elif re.search(c['exclude_title_regex'], title, re.I) and not in_tl:
            why = 'Contenuto non filmico/seriale (titolo: podcast/extra)'
        elif any(g in c['exclude_genre_ids'] for g in genres) and not in_tl:
            why = 'Genere estraneo (talk/news/reality/documentario)'
        elif not in_tl and not marvel_co and c['keyword_only_policy'] == 'exclude':
            why = 'Nessuna societa Marvel tra i produttori (solo keyword): possibile contenuto estraneo'
        if why:
            excluded.append({'key': key0, 'title': title, 'reason': why})
            continue
        poster = d.get('poster_path')
        category = 'animazione' if c['animation_genre_id'] in genres else ('film' if kind == 'movie' else 'serie')
        warn = ['tmdb_canceled'] if (kind == 'tv' and status == 'Canceled') else []
        src = [{'name': 'TMDB', 'url': 'https://www.themoviedb.org/%s/%d' % (kind, tid), 'official': False}]
        cand = []   # (key, kind, date, dateIT, season, poster)
        if kind == 'movie':
            rel = {}
            for ctry in ((d.get('release_dates') or {}).get('results') or []):
                if ctry.get('iso_3166_1') in ('US', 'IT'):
                    ds = sorted((x.get('release_date') or '')[:10] for x in ctry.get('release_dates', []) if x.get('type') in (2, 3) and x.get('release_date'))
                    rel[ctry['iso_3166_1']] = ds[0] if ds else None
            date = d.get('release_date') or rel.get('US') or None
            cand.append((key0, 'movie', date or None, rel.get('IT'), None, poster))
        else:
            for s in d.get('seasons') or []:
                n, ad = s.get('season_number'), s.get('air_date')
                if not isinstance(n, int) or n < 1 or not ad or not (d0 <= ad <= d1):
                    continue
                cand.append(('%s:S%02d' % (key0, n), 'series' if n == 1 and not in_tl else 'season', ad, None, n, s.get('poster_path') or poster))
            ne = d.get('next_episode_to_air') or {}
            if not cand and ne.get('air_date') and d0 <= ne['air_date'] <= d1 and ne.get('season_number'):
                n = ne['season_number']
                cand.append(('%s:S%02d' % (key0, n), 'season', ne['air_date'], None, n, poster))
        if kind == 'tv':     # diagnostica: lo stato generale della serie NON e una prova; contano stagioni/episodi datati
            ne0 = d.get('next_episode_to_air') or {}
            log.setdefault('tv_diagnostics', []).append({'key': key0, 'title': title, 'status': status, 'in_production': d.get('in_production'), 'last_air': d.get('last_air_date'),
                'seasons': [{'n': s.get('season_number'), 'air_date': s.get('air_date')} for s in (d.get('seasons') or [])][-6:], 'next_episode': ne0.get('air_date'),
                'in_timeline': in_tl, 'items_in_window': [k for k, *_ in cand]})
            if not cand and status == 'Canceled':
                excluded.append({'key': key0, 'title': title, 'reason': 'Stato TMDB Canceled e nessuna stagione/episodio con data nella finestra: dati insufficienti (non inserito, non e una prova di cancellazione)'})
                continue
        for key, ikind, date, date_it, season, post in cand:
            if date and not (d0 <= date <= d1):
                continue
            nt = norm(title)
            yr = int((date or today)[:4])
            odates = set()
            for ttl, txts in official_text_by_title.items():
                if len(nt) >= 4 and len(ttl) >= 4 and (nt in ttl or ttl in nt):
                    for t in txts:
                        odates |= dates_in_text(t['text'], yr)
                        if date in dates_in_text(t['text'], yr):
                            src.append({'name': 'YouTube - ' + t['channel'], 'url': t['url'], 'official': True})
            state, conf, prec, reason = classify_tmdb(date, status, today, odates, cfg['tmdb'])
            if warn and state != 'released':
                reason += '. Attenzione: TMDB segna la serie come cancellata ma riporta una stagione/episodio con data: da verificare con una fonte ufficiale'
            if state == 'released' and (dt.date.fromisoformat(today) - dt.date.fromisoformat(date)).days > cfg['window']['past_days']:
                continue
            missing = [k for k, v in (('poster', post), ('dateIT', date_it if ikind == 'movie' else 'n/a'), ('date', date)) if not v]
            items[key] = {
                'key': key, 'kind': ikind, 'title': title if season is None else '%s - Stagione %d' % (title, season),
                'date': date, 'precision': prec, 'window': None, 'dateIT': date_it, 'state': state, 'confidence': conf, 'reason': reason,
                'timelineId': link_timeline(idx, kind, tid, season), 'tmdb': {'type': kind, 'id': tid, **({'season': season} if season else {})},
                'poster': post, 'sources': src[:3], 'signals': sorted(sigs), 'missing': missing, 'category': category, 'warnings': warn}
    # voci manuali (verificate): annunci senza data o titoli assenti in TMDB
    for e in manual.get('entries') or []:
        k = e['key']
        tm = e.get('tmdb')
        if tm:
            tk = 'tmdb:%s:%d' % (tm['type'], tm['id'])
            hit = items.get(tk) or next((v for kk, v in items.items() if kk.startswith(tk + ':S')), None)
            if hit:                              # dedup: la voce manuale arricchisce quella TMDB, non la duplica
                hit['sources'].insert(0, {'name': e['source_name'], 'url': e['source_url'], 'official': True})
                if e.get('date') == hit['date']:
                    hit.update(confidence='confirmed', reason='Data riportata da fonte ufficiale (voce manuale verificata il %s)' % e['verified_on'])
                log.setdefault('manual_merged', []).append(k)
                continue
        conf = 'confirmed' if e.get('date') else 'provisional'
        items[k] = {'key': k, 'kind': e.get('kind', 'movie'), 'title': e['title'], 'date': e.get('date'), 'precision': 'day' if e.get('date') else ('year' if e.get('window') else 'none'),
                    'window': e.get('window'), 'dateIT': None, 'state': 'upcoming' if e.get('date') else 'announced', 'confidence': conf,
                    'reason': ('Data riportata da fonte ufficiale (verificata il %s)' % e['verified_on']) if e.get('date') else 'Annunciato dalla fonte ufficiale senza data (verificato il %s)' % e['verified_on'],
                    'timelineId': link_timeline(idx, tm['type'], tm['id']) if tm else None, 'tmdb': tm, 'poster': None,
                    'sources': [{'name': e['source_name'], 'url': e['source_url'], 'official': True}], 'signals': ['manual'], 'missing': ['poster'],
                    'category': e.get('category') or ('film' if e.get('kind', 'movie') == 'movie' else 'serie'), 'warnings': []}
    # completezza: produzioni TV pianificate/in produzione SENZA data (discover per data non le vede). Solo diagnostica: non si pubblicano
    # senza fonte ufficiale; vanno verificate a mano e, se confermate, inserite in tools/live/manual.json.
    undated = []
    if core:
        have = {k for k in items} | {'tmdb:tv:%d' % t for (kk, t) in found if kk == 'tv'}
        for pg in (1, 2):
            j = tmdb.get('/discover/tv', page=pg, with_companies='|'.join(map(str, core)), with_status=c['undated_tv_status']) or {}
            for it in j.get('results') or []:
                k = 'tmdb:tv:%d' % it['id']
                if k in have or any(u['key'] == k for u in undated) or k in excl_manual:
                    continue
                undated.append({'key': k, 'title': it.get('name'), 'first_air_date': it.get('first_air_date') or None, 'url': 'https://www.themoviedb.org/tv/%d' % it['id']})
            if pg >= (j.get('total_pages') or 1):
                break
    log['undated_candidates'] = undated[:40]
    log['limits'] = ['I film senza data non sono rilevabili con discover/movie (richiede un intervallo di date): usare tools/live/manual.json con fonte ufficiale.']
    return list(items.values()), excluded


def dedupe(items, log):
    """Una sola voce per chiave; stesso titolo normalizzato + stessa data + stesso tipo con chiavi diverse -> si tiene la piu ricca."""
    by_key, out, seen = {}, [], {}
    for it in items:
        by_key.setdefault(it['key'], it)
    for it in sorted(by_key.values(), key=lambda x: (x['date'] or '9999', x['title'])):
        sig = (norm(it['title']), it['date'], it['kind'] if it['kind'] in ('movie',) else 'tv')
        if sig in seen and sig[0]:
            keep, drop = seen[sig], it
            if len(drop['sources']) > len(keep['sources']):
                out.remove(keep); out.append(drop); seen[sig] = drop; keep, drop = drop, keep
            log.setdefault('deduped', []).append({'dropped': drop['key'], 'kept': keep['key']})
            continue
        seen[sig] = it
        out.append(it)
    return out


def merge_history(items, prev_items, today):
    prev = {p['key']: p for p in prev_items}
    for it in items:
        p = prev.get(it['key'])
        it['firstSeen'] = (p or {}).get('firstSeen', today)
        hist = list((p or {}).get('history') or [])
        if p and p.get('date') != it['date']:
            hist.append({'at': today, 'from': p.get('date'), 'to': it['date']})
        if p and p.get('confidence') != it['confidence'] and it['confidence'] == 'confirmed':
            hist.append({'at': today, 'confidence': 'confirmed'})
        it['history'] = hist[-5:]
        it['updatedAt'] = today if (not p or any(p.get(f) != it.get(f) for f in ('date', 'confidence', 'state', 'title'))) else p.get('updatedAt', today)


# ------------------------------------------------------------------ YouTube
def parse_yt_feed(txt):
    root = ET.fromstring(txt)
    author = (root.findtext('a:author/a:name', namespaces=ATOM) or '').strip()
    ents = []
    for e in root.findall('a:entry', ATOM):
        link = e.find('a:link', ATOM)
        ents.append({'id': e.findtext('yt:videoId', namespaces=ATOM), 'title': (e.findtext('a:title', namespaces=ATOM) or '').strip(),
                     'published': (e.findtext('a:published', namespaces=ATOM) or '')[:10], 'url': link.get('href') if link is not None else None,
                     'desc': (e.findtext('media:group/media:description', namespaces=ATOM) or '')[:600]})
    return author, ents


def verify_channel(ch, fetch):
    """Identita ufficiale: (1) pagina canale risolve allo stesso channel_id, (2) autore del feed coerente col nome atteso."""
    checks = []
    page = fetch('https://www.youtube.com/' + ch['handle'], {'Cookie': 'CONSENT=YES+1; SOCS=CAI', 'Accept-Language': 'en-US,en;q=0.8'})
    ids = set(re.findall(r'(?:<link rel="canonical" href="https://www\.youtube\.com/channel/|"externalId":"|"channelId":")(UC[\w-]{22})', page['text']))
    checks.append({'check': 'handle->channel_id', 'ok': ch['channel_id'] in ids, 'detail': 'HTTP %s' % page['status']})
    return checks


def trailer_category(title, desc, yt):
    """(categoria, base). Solo con evidenza: parole chiave di videogioco nel titolo/descrizione; altrimenti None (poi eventualmente dal titolo collegato)."""
    if re.search(yt['game_title_regex'], title or '', re.I):
        return 'videogioco', 'titolo'
    if re.search(yt['game_desc_regex'], desc or '', re.I):
        return 'videogioco', 'descrizione'
    return None, 'nessuna'


def build_trailers(cfg, fetch, today, log):
    yt, out, ident, seen = cfg['youtube'], [], [], set()
    status = 'ok'
    official_text = {}
    for ch in yt['channels']:
        if not ch.get('enabled'):
            ident.append({'handle': ch['handle'], 'enabled': False, 'note': ch.get('role')})
            continue
        checks = verify_channel(ch, fetch)
        feed = None
        for attempt in range(3):
            feed = fetch('https://www.youtube.com/feeds/videos.xml?channel_id=' + ch['channel_id'])
            if feed['status'] == 200:
                break
            time.sleep(2)
        entry = {'handle': ch['handle'], 'channel_id': ch['channel_id'], 'enabled': True}
        if feed['status'] != 200:
            checks.append({'check': 'rss', 'ok': False, 'detail': 'HTTP %s' % feed['status']})
            entry.update(verified=False, checks=checks)
            ident.append(entry); status = 'error'
            continue
        try:
            author, ents = parse_yt_feed(feed['text'])
        except ET.ParseError:
            checks.append({'check': 'rss', 'ok': False, 'detail': 'XML non valido'})
            entry.update(verified=False, checks=checks); ident.append(entry); status = 'error'
            continue
        checks.append({'check': 'autore feed', 'ok': bool(re.search(ch['expect_author_regex'], author, re.I)), 'detail': author})
        verified = all(c['ok'] for c in checks)
        entry.update(verified=verified, checks=checks, author=author)
        ident.append(entry)
        if not verified:
            status = 'unverified'
            continue
        for e in ents:
            if not e['id'] or e['id'] in seen:
                continue
            ttl = e['title']
            if not re.search(yt['include_title_regex'], ttl, re.I) or re.search(yt['exclude_title_regex'], ttl, re.I):
                continue
            seen.add(e['id'])
            kind = 'teaser' if re.search(r'teaser', ttl, re.I) else 'trailer'
            cat, basis = trailer_category(ttl, e['desc'], yt)
            out.append({'key': 'yt:' + e['id'], 'title': ttl, 'published': e['published'], 'url': e['url'] or 'https://www.youtube.com/watch?v=' + e['id'],
                        'channel': ch['label'], 'kind': kind, 'official': True, 'relatesTo': None, 'category': cat, 'categoryBasis': basis, '_desc': e['desc']})
            if cat != 'videogioco':          # un video di videogioco non conferma date di film/serie
                official_text.setdefault(title_base(ttl), []).append({'text': ttl + ' ' + e['desc'], 'url': e['url'], 'channel': ch['label']})
    cut = (dt.date.fromisoformat(today) - dt.timedelta(days=yt['retention_days'])).isoformat()
    out = sorted([t for t in out if t['published'] >= cut], key=lambda t: t['published'], reverse=True)[:yt['max_items']]
    log['youtube_identity'] = ident
    return out, status, ident, official_text


def link_trailers(trailers, calendar, idx_titles):
    cal = [(norm(i['title']), i['key']) for i in calendar if i['title']]
    cat_of = {i['key']: i.get('category') for i in calendar}
    for t in trailers:
        base = title_base(t['title'])
        hits = [k for n, k in cal if base and len(base) >= 4 and (base in n or n in base)] if t.get('category') != 'videogioco' else []
        t['relatesTo'] = hits[0] if len(hits) == 1 else None      # solo se univoco (mai per i videogiochi)
        if t.get('category') is None and t['relatesTo'] and cat_of.get(t['relatesTo']):
            t['category'], t['categoryBasis'] = cat_of[t['relatesTo']], 'titolo collegato'
        t.setdefault('category', None); t.setdefault('categoryBasis', 'nessuna')      # nessuna categoria senza evidenza (mai "film" per default)
        t.pop('_desc', None)


# ------------------------------------------------------------------ validazione
class ValidationError(Exception):
    pass


def validate(calendar, trailers, manifest, cfg):
    errs = []
    def need(c, msg):
        if not c:
            errs.append(msg)
    keys = set()
    for it in calendar['items']:
        k = it.get('key', '?')
        need(KEY_RE.match(k or ''), 'chiave non valida: %s' % k)
        need(k not in keys, 'chiave duplicata: %s' % k)
        keys.add(k)
        need(it.get('kind') in ('movie', 'series', 'season', 'special'), '%s: kind' % k)
        need(isinstance(it.get('title'), str) and it['title'].strip(), '%s: titolo' % k)
        need(it.get('date') is None or DATE_RE.match(it['date']), '%s: data' % k)
        need(it.get('precision') in ('day', 'month', 'year', 'none'), '%s: precision' % k)
        need(it.get('state') in ('upcoming', 'released', 'announced'), '%s: state' % k)
        need(it.get('confidence') in ('confirmed', 'provisional', None), '%s: confidence' % k)
        need((it['state'] == 'released') == (it.get('confidence') is None), '%s: confidence nulla solo per i titoli usciti' % k)
        if it.get('confidence') == 'confirmed':
            need(any(s.get('official') for s in it.get('sources', [])), '%s: CONFERMATO senza fonte ufficiale' % k)
        need(it.get('state') != 'upcoming' or it.get('date'), '%s: upcoming senza data' % k)
        need(isinstance(it.get('sources'), list) and it['sources'] and all(str(s.get('url', '')).startswith('https://') for s in it['sources']), '%s: fonti' % k)
        need(it.get('timelineId') is None or re.match(r'^\d{3}$', str(it['timelineId'])), '%s: timelineId' % k)
        need(isinstance(it.get('missing'), list), '%s: missing' % k)
        need(it.get('category') in CATEGORIES + (None,), '%s: category' % k)
        need(isinstance(it.get('warnings', []), list) and all(w in WARNINGS for w in it.get('warnings', [])), '%s: warnings' % k)
    tl = [i['timelineId'] for i in calendar['items'] if i.get('timelineId') and i['kind'] != 'season']
    need(len(tl) == len(set(tl)), 'stessa scheda Timeline agganciata a piu voci (movie/series)')
    tk = set()
    for t in trailers['items']:
        need(re.match(r'^yt:[\w-]{11}$', t.get('key', '')), 'trailer chiave: %s' % t.get('key'))
        need(t['key'] not in tk, 'trailer duplicato %s' % t['key']); tk.add(t['key'])
        need(str(t.get('url', '')).startswith('https://www.youtube.com/') or str(t.get('url', '')).startswith('https://youtu.be/'), '%s: url' % t['key'])
        need(t.get('relatesTo') is None or t['relatesTo'] in keys, '%s: relatesTo inesistente' % t['key'])
        need(DATE_RE.match(t.get('published', '')), '%s: data' % t['key'])
        need(t.get('category') in CATEGORIES + (None,), '%s: category' % t['key'])
    for name, obj in (('calendar', calendar), ('trailers', trailers), ('manifest', manifest)):
        n = len(json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode())
        need(n <= cfg['budget_bytes'][name], '%s supera il budget (%d B)' % (name, n))
    if errs:
        raise ValidationError('; '.join(errs[:15]))


def validate_manual(manual):
    errs = []
    seen = set()
    for e in manual.get('entries') or []:
        k = e.get('key', '')
        if not re.match(r'^manual:[a-z0-9\-]{3,60}$', k) or k in seen:
            errs.append('manuale: chiave non valida/duplicata %r' % k)
        seen.add(k)
        for f in ('title', 'source_name', 'source_url', 'verified_on'):
            if not e.get(f):
                errs.append('manuale %s: manca %s' % (k, f))
        if e.get('source_url') and not str(e['source_url']).startswith('https://'):
            errs.append('manuale %s: source_url deve essere https' % k)
        if e.get('verified_on') and not DATE_RE.match(e['verified_on']):
            errs.append('manuale %s: verified_on' % k)
        if e.get('date') and not DATE_RE.match(e['date']):
            errs.append('manuale %s: date' % k)
        if e.get('category') and e['category'] not in CATEGORIES:
            errs.append('manuale %s: category (%s)' % (k, ', '.join(CATEGORIES)))
        if e.get('tmdb') and not (e['tmdb'].get('type') in ('movie', 'tv') and isinstance(e['tmdb'].get('id'), int)):
            errs.append('manuale %s: tmdb' % k)
    if errs:
        raise ValidationError('; '.join(errs))


# ------------------------------------------------------------------ orchestrazione
def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=1) + '\n'


def run(args, fetch=http, root=ROOT):
    cfg = load_json(os.path.join(root, 'tools/live/config.json'))
    manual = load_json(os.path.join(root, 'tools/live/manual.json'), {'entries': [], 'exclude': []})
    validate_manual(manual)
    today = args.today or dt.datetime.now(dt.timezone.utc).date().isoformat()
    prev_dir = args.prev
    prev_cal = (load_json(os.path.join(prev_dir, 'calendar.json'), {}) or {}).get('items', []) if prev_dir else []
    prev_tr = (load_json(os.path.join(prev_dir, 'trailers.json'), {}) or {}).get('items', []) if prev_dir else []
    log, manifest_sources = {}, {}
    idx = timeline_index(root)

    trailers, ystatus, ident, official_text = build_trailers(cfg, fetch, today, log)
    if ystatus in ('error', 'unverified') and not trailers and prev_tr and ystatus == 'error':
        trailers, ystatus = prev_tr, 'stale'                     # rete assente: si mantiene l'ultimo valido
    manifest_sources['youtube'] = {'status': ystatus, 'identity': ident, 'count': len(trailers)}

    tm = Tmdb(fetch)
    calendar_items, excluded, tstatus = [], [], 'ok'
    if not SECRETS:
        tstatus = 'error'; log['tmdb_error'] = 'Nessun secret TMDB'
    else:
        probe = tm.get('/configuration')
        if probe is None:
            tstatus = 'error'; log['tmdb_error'] = 'Accesso TMDB non riuscito'
        else:
            calendar_items, excluded = build_calendar(tm, cfg, idx, today, manual, official_text, log)
            if tm.errors:
                tstatus = 'partial' if calendar_items else 'error'
    if tstatus == 'error' and prev_cal:
        calendar_items, tstatus = prev_cal, 'stale'
    elif tstatus in ('ok', 'partial'):
        calendar_items = dedupe(calendar_items, log)
        merge_history(calendar_items, prev_cal, today)
    manifest_sources['tmdb'] = {'status': tstatus, 'count': len(calendar_items), 'requests': tm.calls, 'errors': tm.errors[:10]}
    manifest_sources['manual'] = {'status': 'ok', 'count': len(manual.get('entries') or [])}
    manifest_sources['news'] = {'status': 'disabled', 'reason': cfg['news']['reason']}
    if tstatus == 'ok' or tstatus == 'partial':
        pass
    link_trailers(trailers, calendar_items, None)

    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds') if not args.today else today + 'T00:00:00+00:00'
    calendar = {'schema': SCHEMA, 'generated_at': now, 'items': sorted(calendar_items, key=lambda x: (x['date'] or '9999-12-31', x['title']))}
    trailers_o = {'schema': SCHEMA, 'generated_at': now, 'items': trailers}
    counts = {'calendar': len(calendar['items']), 'confirmed': sum(1 for i in calendar['items'] if i['confidence'] == 'confirmed'),
              'provisional': sum(1 for i in calendar['items'] if i['confidence'] == 'provisional'), 'released': sum(1 for i in calendar['items'] if i['state'] == 'released'),
              'in_timeline': sum(1 for i in calendar['items'] if i['timelineId']), 'not_in_timeline': sum(1 for i in calendar['items'] if not i['timelineId']),
              'excluded': len(excluded), 'trailers': len(trailers), 'undated_candidates': len(log.get('undated_candidates', [])),
              'by_category': {c: sum(1 for i in calendar['items'] if i.get('category') == c) for c in CATEGORIES}, 'trailers_by_category': {str(c): sum(1 for t in trailers if t.get('category') == c) for c in CATEGORIES + (None,)}}
    manifest = {'schema': SCHEMA, 'generated_at': now, 'sources': manifest_sources, 'counts': counts, 'attribution': {'tmdb': True},
                'content_hash': hashlib.sha256((canon(calendar['items']) + canon(trailers)).encode()).hexdigest()[:16],
                'notes': ['Confermato = fonte ufficiale verificabile; altrimenti provvisorio.', 'Indiscrezioni escluse in 1.0.']}
    validate(calendar, trailers_o, manifest, cfg)
    return calendar, trailers_o, manifest, excluded, log


def write_all(out, calendar, trailers, manifest, excluded, log):
    os.makedirs(out, exist_ok=True)
    for name, obj in (('calendar', calendar), ('trailers', trailers), ('manifest', manifest)):
        open(os.path.join(out, name + '.json'), 'w', encoding='utf-8').write(scrub(canon(obj)))
    L = ['# TVA Live - esito generazione', '', 'Generato: %s' % manifest['generated_at'], '', '## Fonti', '']
    for k, v in manifest['sources'].items():
        L.append('- **%s**: %s%s' % (k, v.get('status'), (' (%d voci)' % v['count']) if 'count' in v else ''))
    L += ['', '## Conteggi', '', '```json', json.dumps(manifest['counts'], indent=1), '```', '', '## Calendario', '']
    for i in calendar['items']:
        L.append('- %s | %s | %s | %s | Timeline: %s | %s' % (i['date'] or i['window'] or 's.d.', i['title'], i['state'], i['confidence'] or '-', i['timelineId'] or 'NO', i['reason']))
    L += ['', '## Esclusi (%d)' % len(excluded), ''] + ['- %s %s: %s' % (e['key'], e.get('title', ''), e['reason']) for e in excluded]
    ud = log.get('undated_candidates') or []
    L += ['', '## Candidati senza data (solo TMDB, NON pubblicati: verificare con fonte ufficiale e, se confermati, inserire in tools/live/manual.json)', ''] + (['- %s %s (%s)' % (u['key'], u['title'], u['url']) for u in ud] or ['- nessuno'])
    L += ['', '## Identita canali YouTube', '', '```json', json.dumps(log.get('youtube_identity'), indent=1, ensure_ascii=False), '```', '', '## Diagnostica', '', '```json',
          json.dumps({k: v for k, v in log.items() if k not in ('youtube_identity', 'undated_candidates')}, indent=1, ensure_ascii=False), '```']
    open(os.path.join(out, 'REPORT.md'), 'w', encoding='utf-8').write(scrub('\n'.join(L)))
    for dp, _, fs in os.walk(out):
        for f in fs:
            if any(s in open(os.path.join(dp, f), encoding='utf-8').read() for s in SECRETS):
                for f2 in fs:
                    os.remove(os.path.join(dp, f2))
                sys.exit('Credenziale rilevata: output eliminato.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='live-data')
    ap.add_argument('--prev', default=os.path.join(ROOT, 'assets/live'), help='cartella con i JSON precedenti (per cronologia e fallback)')
    ap.add_argument('--today', default=None)
    a = ap.parse_args()
    try:
        res = run(a)
    except ValidationError as e:
        sys.exit('Validazione fallita, nessun file scritto: ' + scrub(str(e)))
    write_all(a.out, *res)
    print('Scritto in', a.out, json.dumps(res[2]['counts']))


if __name__ == '__main__':
    main()
