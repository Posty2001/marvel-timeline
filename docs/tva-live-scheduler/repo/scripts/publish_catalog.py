#!/usr/bin/env python3
"""TVA Live - pubblicazione del catalogo (repository tva-live-scheduler). Solo libreria standard.

Prende i tre JSON gia verificati (calendar, trailers, manifest) e:
  1. li RIVALIDA in modo indipendente (schema, coerenza, link, dimensioni, nessun segreto);
  2. li registra come VERSIONE IMMUTABILE  catalog/c/<id>/  (id = hash dei tre file; mai riscritta);
  3. aggiorna il puntatore catalog/current.json (solo se la versione cambia e solo in avanti nel tempo);
  4. costruisce il sito pubblico  _site/v1/  con SOLO: current.json + le ultime N versioni + una pagina di servizio.
Nulla viene scritto se un controllo fallisce. Esce 0 (ok), 1 (rifiutato), 2 (errore di uso).
Uscite per GitHub Actions: changed, deploy, version."""
import argparse, datetime as dt, hashlib, json, os, re, shutil, sys, tempfile, urllib.request

FILES = ('calendar', 'trailers', 'manifest')
BUDGET = {'calendar': 90000, 'trailers': 40000, 'manifest': 8000}      # byte: stessi limiti del generatore
HOSTS = {'www.youtube.com', 'youtu.be', 'www.themoviedb.org', 'www.marvel.com', 'marvel.com'}
KEY_RE = re.compile(r'^(tmdb:(movie|tv):\d+(:S\d{2})?|manual:[a-z0-9\-]{3,60})$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SECRET_RE = re.compile(r'github_pat_|ghp_[A-Za-z0-9]|gho_|ghs_|eyJ[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}|(api[_-]?key|secret|password|token)\s*[=:]\s*\S{8,}', re.I)
SITE_PREFIX = 'v1'
CATEGORIES = ('film', 'serie', 'animazione', 'videogioco', None)


class Reject(Exception):
    pass


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, indent=1) + '\n'


def parse_ts(s):
    try:
        t = dt.datetime.fromisoformat(s)
    except (TypeError, ValueError):
        raise Reject('generated_at non valido: %r' % (s,))
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def walk_urls(o, out):
    if isinstance(o, dict):
        for v in o.values(): walk_urls(v, out)
    elif isinstance(o, list):
        for v in o: walk_urls(v, out)
    elif isinstance(o, str) and re.match(r'^(https?:|javascript:|data:|vbscript:|file:|ftp:|blob:|//)', o, re.I):
        out.append(o)


def validate(raw):
    """raw: {nome: bytes}. Ritorna dict nome->oggetto. Solleva Reject."""
    errs = []
    need = lambda c, m: errs.append(m) if not c else None   # noqa: E731
    obj = {}
    for n in FILES:
        b = raw[n]
        need(len(b) <= BUDGET[n], '%s supera il limite di %d byte' % (n, BUDGET[n]))
        try:
            obj[n] = json.loads(b.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise Reject('%s: JSON non valido' % n)
        need(isinstance(obj[n], dict) and obj[n].get('schema') == 1, '%s: schema diverso da 1' % n)
        need(not SECRET_RE.search(b.decode('utf-8')), '%s: contiene un pattern da segreto/credenziale' % n)
    if errs: raise Reject('; '.join(errs))
    c, t, m = obj['calendar'], obj['trailers'], obj['manifest']
    need(isinstance(c.get('items'), list) and isinstance(t.get('items'), list), 'items mancanti')
    if errs: raise Reject('; '.join(errs))
    need(c.get('generated_at') == t.get('generated_at') == m.get('generated_at'), 'generated_at diverso tra calendar, trailers e manifest (versioni miste)')
    parse_ts(m.get('generated_at'))
    need(len(c['items']) >= 1, 'calendario vuoto')
    keys = set()
    for it in c['items']:
        k = it.get('key', '?')
        need(KEY_RE.match(k or ''), 'chiave non valida: %s' % k); need(k not in keys, 'chiave duplicata: %s' % k); keys.add(k)
        need(it.get('kind') in ('movie', 'series', 'season', 'special'), '%s: kind' % k)
        need(isinstance(it.get('title'), str) and it['title'].strip() and len(it['title']) <= 200, '%s: titolo' % k)
        need(it.get('date') is None or DATE_RE.match(it['date'] or ''), '%s: data' % k)
        need(it.get('state') in ('upcoming', 'released', 'announced'), '%s: state' % k)
        need(it.get('confidence') in ('confirmed', 'provisional', None), '%s: confidence' % k)
        need(it.get('state') != 'upcoming' or it.get('date'), '%s: upcoming senza data' % k)
        need(it.get('category') in CATEGORIES, '%s: category' % k)
        src = it.get('sources')
        need(isinstance(src, list) and src, '%s: fonti mancanti' % k)
        if it.get('confidence') == 'confirmed':
            need(isinstance(src, list) and any(isinstance(s, dict) and s.get('official') for s in src), '%s: CONFERMATO senza fonte ufficiale' % k)
    tk = set()
    for x in t['items']:
        k = x.get('key', '?')
        need(re.match(r'^yt:[\w-]{11}$', k or ''), 'trailer chiave: %s' % k); need(k not in tk, 'trailer duplicato: %s' % k); tk.add(k)
        need(x.get('relatesTo') is None or x['relatesTo'] in keys, '%s: relatesTo inesistente' % k)
        need(DATE_RE.match(x.get('published', '') or ''), '%s: data' % k)
        need(str(x.get('url', '')).startswith(('https://www.youtube.com/', 'https://youtu.be/')), '%s: url non ammesso' % k)
    urls = []
    for n in FILES: walk_urls(obj[n], urls)
    for u in urls:
        m2 = re.match(r'^https://([^/:?#@]+)(/|$|\?|#)', u)
        need(m2 and m2.group(1).lower() in HOSTS, 'link non ammesso: %s' % u[:80])
    need(m.get('content_hash') == sha((canon(c['items']) + canon(t['items'])).encode())[:16], 'content_hash del manifest non corrisponde ai dati')
    cn = m.get('counts') or {}
    need(cn.get('calendar') == len(c['items']) and cn.get('trailers') == len(t['items']), 'conteggi del manifest incoerenti con calendario/trailer')
    if errs: raise Reject('; '.join(errs[:15]))
    return obj


def version_id(shas):
    return sha('\n'.join('%s:%s' % (n, shas[n]) for n in FILES).encode())[:16]


def load_version(store, vid):
    d = os.path.join(store, 'c', vid)
    return {n: open(os.path.join(d, n + '.json'), 'rb').read() for n in FILES}


def read_pointer(src):
    """Legge un puntatore da file o URL https. None se assente/illeggibile."""
    try:
        if re.match(r'^https://', src):
            with urllib.request.urlopen(urllib.request.Request(src, headers={'Cache-Control': 'no-cache', 'User-Agent': 'tva-live-publisher'}), timeout=20) as r:
                return json.loads(r.read(100000).decode('utf-8'))
        return json.load(open(src, encoding='utf-8'))
    except Exception:   # noqa: BLE001 - assente o non raggiungibile: si assume "da pubblicare"
        return None


def pointer_for(vid, raw, gen, chash):
    return {'schema': 1, 'version': vid, 'generated_at': gen, 'content_hash': chash,
            'files': {n: {'path': 'c/%s/%s.json' % (vid, n), 'sha256': sha(raw[n]), 'bytes': len(raw[n])} for n in FILES}}


def build_site(store, site, keep, cur_vid):
    vids = []
    for vid in os.listdir(os.path.join(store, 'c')) if os.path.isdir(os.path.join(store, 'c')) else []:
        try:
            vids.append((parse_ts(json.loads(load_version(store, vid)['manifest'])['generated_at']), vid))
        except Exception:   # noqa: BLE001
            continue
    vids.sort(reverse=True)
    chosen = [v for _, v in vids][:keep]
    if cur_vid not in chosen: chosen = [cur_vid] + chosen[:keep - 1]
    tmp = site + '.tmp'; shutil.rmtree(tmp, ignore_errors=True)
    base = os.path.join(tmp, SITE_PREFIX); os.makedirs(os.path.join(base, 'c'))
    for vid in chosen:
        os.makedirs(os.path.join(base, 'c', vid))
        for n in FILES: shutil.copyfile(os.path.join(store, 'c', vid, n + '.json'), os.path.join(base, 'c', vid, n + '.json'))
    shutil.copyfile(os.path.join(store, 'current.json'), os.path.join(base, 'current.json'))
    open(os.path.join(tmp, '.nojekyll'), 'w').close()
    open(os.path.join(tmp, 'index.html'), 'w', encoding='utf-8').write('<!doctype html><meta charset="utf-8"><title>TVA Live data</title><p>Dati pubblici di TVA Live (JSON). Puntatore: <a href="v1/current.json">v1/current.json</a>.</p>\n')
    total = 0
    for dp, _, fs in os.walk(tmp):
        for f in fs:
            p = os.path.join(dp, f); total += os.path.getsize(p)
            ext = os.path.splitext(f)[1]
            if f not in ('.nojekyll', 'index.html') and ext != '.json': raise Reject('file non ammesso nel sito: ' + f)
            if ext == '.json' and SECRET_RE.search(open(p, encoding='utf-8').read()): raise Reject('possibile segreto in ' + f)
    if total > 2_000_000: raise Reject('sito troppo grande: %d byte' % total)
    shutil.rmtree(site, ignore_errors=True); os.replace(tmp, site)
    return chosen


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True); ap.add_argument('--store', default='catalog'); ap.add_argument('--site', default='_site')
    ap.add_argument('--live-pointer', default=None, help='URL https o file del puntatore attualmente pubblicato')
    ap.add_argument('--keep', type=int, default=10); ap.add_argument('--github-output', default=None)
    a = ap.parse_args(argv)
    def out(**kw):
        for k, v in kw.items(): print('%s=%s' % (k, v))
        if a.github_output:
            with open(a.github_output, 'a', encoding='utf-8') as f:
                for k, v in kw.items(): f.write('%s=%s\n' % (k, v))
    try:
        raw = {}
        for n in FILES:
            p = os.path.join(a.src, n + '.json')
            if not os.path.isfile(p): raise Reject('file mancante: ' + n + '.json')
            raw[n] = open(p, 'rb').read()
        obj = validate(raw)
        st = os.path.join(a.src, 'status.json')
        if os.path.isfile(st):
            s = json.load(open(st, encoding='utf-8'))
            if s.get('content_hash') != obj['manifest']['content_hash']: raise Reject('status.json non corrisponde al manifest')
        shas = {n: sha(raw[n]) for n in FILES}; vid = version_id(shas); gen = obj['manifest']['generated_at']
        cur_p = os.path.join(a.store, 'current.json'); cur = json.load(open(cur_p, encoding='utf-8')) if os.path.isfile(cur_p) else None
        vdir = os.path.join(a.store, 'c', vid)
        if os.path.isdir(vdir):                                   # immutabilita: una versione esistente non si riscrive
            ex = load_version(a.store, vid)
            if any(ex[n] != raw[n] for n in FILES): raise Reject('versione %s gia presente con contenuto diverso' % vid)
        if cur and cur['version'] != vid and parse_ts(gen) < parse_ts(cur['generated_at']):
            raise Reject('catalogo piu vecchio di quello pubblicato (%s < %s): rifiutato' % (gen, cur['generated_at']))
        ptr = pointer_for(vid, raw, gen, obj['manifest']['content_hash'])
        changed = not cur or cur['version'] != vid or not os.path.isdir(vdir)
        if changed:
            os.makedirs(vdir, exist_ok=True)
            for n in FILES: open(os.path.join(vdir, n + '.json'), 'wb').write(raw[n])
            tmp = tempfile.NamedTemporaryFile('w', delete=False, dir=a.store, encoding='utf-8', suffix='.tmp'); json.dump(ptr, tmp, indent=1, sort_keys=True); tmp.write('\n'); tmp.close()
            os.replace(tmp.name, cur_p)
        chosen = build_site(a.store, a.site, a.keep, vid)
        live = read_pointer(a.live_pointer) if a.live_pointer else None
        deploy = changed or not live or live.get('version') != vid
        out(changed=str(changed).lower(), deploy=str(deploy).lower(), version=vid)
        print('Versioni nel sito: %s | generated_at %s' % (', '.join(chosen), gen))
        return 0
    except Reject as e:
        print('RIFIUTATO: %s' % e, file=sys.stderr); out(changed='false', deploy='false', version='')
        return 1


if __name__ == '__main__':
    sys.exit(main())
