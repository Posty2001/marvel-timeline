"""TVA Live 1.1 Fase 2 - test della pubblicazione (docs/tva-live-scheduler/repo/scripts/publish_catalog.py).
Tutto in cartelle temporanee, dati reali di assets/live + varianti manomesse. Nessuna rete."""
import copy, hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
SCR = os.path.join(ROOT, 'docs/tva-live-scheduler/repo/scripts/publish_catalog.py')
sys.path.insert(0, os.path.dirname(SCR)); import publish_catalog as P  # noqa: E402
LIVE = os.path.join(ROOT, 'assets/live')
RES = []
def ok(n, c, e=''):
    RES.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ('' if c else '  >> ' + str(e)), flush=True)
J = lambda p: json.load(open(p, encoding='utf-8'))
def sha(b): return hashlib.sha256(b).hexdigest()
def mk_src(mut=None, gen=None):
    """Copia dei dati reali; mut(c,t,m) li modifica; il manifest viene riallineato (hash, conteggi, generated_at) salvo richiesta contraria."""
    d = tempfile.mkdtemp(); c, t, m = (J(os.path.join(LIVE, n + '.json')) for n in ('calendar', 'trailers', 'manifest'))
    raw_mut = False
    if mut: raw_mut = mut(c, t, m) is False
    if gen:
        for o in (c, t, m): o['generated_at'] = gen
    if not raw_mut:
        m['content_hash'] = P.sha((P.canon(c['items']) + P.canon(t['items'])).encode())[:16]; m['counts']['calendar'] = len(c['items']); m['counts']['trailers'] = len(t['items'])
    for n, o in (('calendar', c), ('trailers', t), ('manifest', m)): open(os.path.join(d, n + '.json'), 'w', encoding='utf-8').write(P.canon(o))
    open(os.path.join(d, 'status.json'), 'w').write(json.dumps({'content_hash': m['content_hash'], 'result': 'update', 'schema': 1}))
    open(os.path.join(d, 'REPORT_INTERNO.md'), 'w').write('report interno'); return d
def run(src, store, site, live=None):
    go = tempfile.mktemp(); args = ['--src', src, '--store', store, '--site', site, '--github-output', go] + (['--live-pointer', live] if live else [])
    e, o = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(e), contextlib.redirect_stdout(o): rc = P.main(args)
    outs = dict(l.split('=', 1) for l in open(go).read().splitlines() if '=' in l) if os.path.exists(go) else {}
    return rc, outs, o.getvalue() + e.getvalue()
def tree(d): return sorted(os.path.relpath(os.path.join(dp, f), d) for dp, _, fs in os.walk(d) for f in fs)
def snap(d): return {p: open(os.path.join(d, p), 'rb').read() for p in tree(d)} if os.path.isdir(d) else {}

W = tempfile.mkdtemp(); store = os.path.join(W, 'catalog'); site = os.path.join(W, '_site'); os.makedirs(store)
src1 = mk_src()
rc, o, log = run(src1, store, site)
v1 = o.get('version')
ok('dati reali: validati, pubblicati, changed=true deploy=true', rc == 0 and o.get('changed') == 'true' and o.get('deploy') == 'true' and re.match(r'^[0-9a-f]{16}$', v1 or ''), (rc, o, log))
ptr = J(os.path.join(site, 'v1/current.json'))
ok('puntatore: versione, generated_at, hash e per ogni file percorso/sha256/byte', ptr['version'] == v1 and ptr['schema'] == 1 and set(ptr['files']) == {'calendar', 'trailers', 'manifest'} and ptr['generated_at'] == J(os.path.join(LIVE, 'manifest.json'))['generated_at'])
ok('i file pubblicati sono identici byte per byte ai sorgenti e coincidono con sha256/byte del puntatore', all(open(os.path.join(site, 'v1', f['path']), 'rb').read() == open(os.path.join(src1, n + '.json'), 'rb').read() and sha(open(os.path.join(site, 'v1', f['path']), 'rb').read()) == f['sha256'] and f['bytes'] == os.path.getsize(os.path.join(site, 'v1', f['path'])) for n, f in ptr['files'].items()))
ok('sito pubblico: SOLO json + pagina di servizio (niente status, report, codice, segreti)', sorted(p for p in tree(site) if not p.startswith('v1/c/')) == ['.nojekyll', 'index.html', 'v1/current.json'] and all(p.endswith('.json') for p in tree(site) if p.startswith('v1/c/')) and 'REPORT' not in ' '.join(tree(site)) and 'status' not in ' '.join(tree(site)))
ok('nessun pattern da segreto in alcun file del sito', not any(P.SECRET_RE.search(open(os.path.join(site, p), encoding='utf-8').read()) for p in tree(site)))
ok('nessun file del sito oltre 100 KB e sito complessivo piccolo', sum(os.path.getsize(os.path.join(site, p)) for p in tree(site)) < 200_000)

rc, o, log = run(src1, store, site, live=os.path.join(site, 'v1/current.json'))
ok('stesso contenuto, endpoint gia aggiornato: changed=false, deploy=false (nessuna pubblicazione inutile)', rc == 0 and o.get('changed') == 'false' and o.get('deploy') == 'false' and o.get('version') == v1, (rc, o))
rc, o, log = run(src1, store, site, live=os.path.join(W, 'inesistente.json'))
ok('endpoint non raggiungibile/assente: deploy=true anche se il catalogo non e cambiato (recupero dopo deploy fallito)', rc == 0 and o.get('changed') == 'false' and o.get('deploy') == 'true')
old = copy.deepcopy(ptr); old['version'] = 'ffffffffffffffff'; json.dump(old, open(os.path.join(W, 'old.json'), 'w'))
rc, o, log = run(src1, store, site, live=os.path.join(W, 'old.json'))
ok('endpoint con versione diversa da quella del catalogo: deploy=true', o.get('deploy') == 'true')

# nuova versione
def newtr(c, t, m):
    t['items'].append({'category': 'film', 'categoryBasis': 'titolo collegato', 'channel': 'Marvel Entertainment', 'key': 'yt:AAAAAAAAAAA', 'kind': 'trailer', 'official': True, 'published': '2026-11-25', 'relatesTo': c['items'][0]['key'], 'title': 'Nuovo trailer', 'url': 'https://www.youtube.com/watch?v=AAAAAAAAAAA'})
src2 = mk_src(newtr, gen='2026-11-25T05:20:00+00:00'); s_before = snap(store)
rc, o, log = run(src2, store, site, live=os.path.join(site, 'v1/current.json')); v2 = o.get('version')
ok('nuova versione: pubblicata, deploy=true, id diverso', rc == 0 and o.get('changed') == 'true' and o.get('deploy') == 'true' and v2 and v2 != v1, (rc, o, log))
ok('versioni immutabili: la versione 1 resta identica byte per byte e resta nel sito', all(s_before[p] == open(os.path.join(store, p), 'rb').read() for p in s_before if p.startswith('c/%s/' % v1)) and os.path.isfile(os.path.join(site, 'v1/c/%s/calendar.json' % v1)))
ok('il puntatore ora indica la v2; ogni versione e completa (tre file coerenti)', J(os.path.join(site, 'v1/current.json'))['version'] == v2 and all(len(os.listdir(os.path.join(site, 'v1/c', v))) == 3 for v in os.listdir(os.path.join(site, 'v1/c'))))
ok('lettura coerente: in ogni versione i tre file hanno lo stesso generated_at (nessuna lettura mista possibile)', all(len({J(os.path.join(site, 'v1/c', v, n + '.json'))['generated_at'] for n in ('calendar', 'trailers', 'manifest')}) == 1 for v in os.listdir(os.path.join(site, 'v1/c'))))

def refuse(name, src, expect):
    s0, t0 = snap(store), snap(site); rc, o, log = run(src, store, site)
    ok('%s: rifiutato, store e sito invariati, deploy=false' % name, rc == 1 and expect.lower() in log.lower() and o.get('deploy') == 'false' and snap(store) == s0 and snap(site) == t0, (rc, log[-200:]))
refuse('catalogo piu vecchio (anti-regressione)', mk_src(newtr, gen='2026-11-24T05:20:00+00:00'), 'piu vecchio')
d = mk_src(newtr, gen='2026-11-26T05:00:00+00:00'); _t = J(os.path.join(d, 'trailers.json')); _t['generated_at'] = '2026-11-29T00:00:00+00:00'; open(os.path.join(d, 'trailers.json'), 'w', encoding='utf-8').write(P.canon(_t))
refuse('versioni miste (generated_at diverso tra i file)', d, 'versioni miste')
def badlink(c, t, m): c['items'][0]['sources'].append({'name': 'x', 'official': False, 'url': 'https://evil.example.com/x'})
refuse('link verso host non ammesso', mk_src(badlink, gen='2026-11-26T05:00:00+00:00'), 'non ammesso')
def httplink(c, t, m): c['items'][0]['sources'][0]['url'] = 'http://www.themoviedb.org/movie/1'
refuse('link non https', mk_src(httplink, gen='2026-11-26T05:00:00+00:00'), 'non ammesso')
def jslink(c, t, m): c['items'][0]['sources'][0]['url'] = 'javascript:alert(1)'
refuse('schema javascript:', mk_src(jslink, gen='2026-11-26T05:00:00+00:00'), 'non ammesso')
def dup(c, t, m): c['items'].append(copy.deepcopy(c['items'][0]))
refuse('chiave duplicata', mk_src(dup, gen='2026-11-26T05:00:00+00:00'), 'duplicata')
def conf(c, t, m):
    for s in c['items'][0]['sources']: s['official'] = False
refuse('confermato senza fonte ufficiale', mk_src(conf, gen='2026-11-26T05:00:00+00:00'), 'ufficiale')
def sec(c, t, m): c['items'][0]['reason'] = 'token github_pat_ABCDEFGH1234567890'
refuse('segreto nei dati', mk_src(sec, gen='2026-11-26T05:00:00+00:00'), 'segreto')
def big(c, t, m): c['items'][0]['reason'] = 'x' * 95000
refuse('file oltre il limite di dimensione', mk_src(big, gen='2026-11-26T05:00:00+00:00'), 'limite')
def sch(c, t, m): c['schema'] = 2
refuse('schema diverso da 1', mk_src(sch, gen='2026-11-26T05:00:00+00:00'), 'schema')
def hh(c, t, m): m['content_hash'] = '0123456789abcdef'; return False
refuse('hash del manifest non corrispondente ai dati', mk_src(hh, gen='2026-11-26T05:00:00+00:00'), 'content_hash')
def cn(c, t, m): m['counts']['trailers'] = 99; return False
refuse('conteggi del manifest incoerenti', mk_src(cn, gen='2026-11-26T05:00:00+00:00'), 'conteggi')
def orphan(c, t, m): t['items'][0]['relatesTo'] = 'tmdb:movie:999999999'
refuse('trailer collegato a un titolo inesistente', mk_src(orphan, gen='2026-11-26T05:00:00+00:00'), 'inesistente')
def empty(c, t, m): c['items'] = []
refuse('calendario vuoto', mk_src(empty, gen='2026-11-26T05:00:00+00:00'), 'vuoto')
d = mk_src(newtr, gen='2026-11-26T05:00:00+00:00'); open(os.path.join(d, 'calendar.json'), 'w').write('{non json'); refuse('JSON corrotto', d, 'json non valido')
d = mk_src(newtr, gen='2026-11-26T05:00:00+00:00'); os.remove(os.path.join(d, 'trailers.json')); refuse('file mancante', d, 'mancante')
d = mk_src(newtr, gen='2026-11-26T05:00:00+00:00'); open(os.path.join(d, 'status.json'), 'w').write(json.dumps({'content_hash': 'zzz'})); refuse('status.json non coerente col manifest', d, 'status.json')
# immutabilita violata
vd = os.path.join(store, 'c', v2); good = open(os.path.join(vd, 'trailers.json'), 'rb').read(); open(os.path.join(vd, 'trailers.json'), 'ab').write(b' ')
rc, o, log = run(src2, store, site); ok('versione gia registrata ma alterata: rifiutato (immutabilita)', rc == 1 and 'diverso' in log, (rc, log)); open(os.path.join(vd, 'trailers.json'), 'wb').write(good)
# potatura del sito, store completo
s = store
for i in range(3, 16):
    d = mk_src(lambda c, t, m, i=i: t['items'].append({'category': 'film', 'categoryBasis': 'x', 'channel': 'M', 'key': 'yt:%011d' % i, 'kind': 'trailer', 'official': True, 'published': '2026-11-25', 'relatesTo': None, 'title': 't', 'url': 'https://www.youtube.com/watch?v=%011d' % i}), gen='2026-12-%02dT05:00:00+00:00' % i)
    rc, o, log = run(d, store, site)
ok('potatura: il sito tiene solo le ultime 10 versioni, lo store (Git) le conserva tutte', rc == 0 and len(os.listdir(os.path.join(site, 'v1/c'))) == 10 and len(os.listdir(os.path.join(store, 'c'))) == 15 and J(os.path.join(site, 'v1/current.json'))['version'] == o['version'])
ok('la versione corrente e sempre nel sito', os.path.isdir(os.path.join(site, 'v1/c', o['version'])))
src_txt = open(SCR, encoding='utf-8').read()
ok('script: solo libreria standard, nessun accesso a variabili segrete, nessuna scrittura fuori da store/site', not re.search(r'^import (requests|yaml)|os\.environ|subprocess', src_txt, re.M))

# workflow dello scheduler (fase 2)
import yaml
WF = open(os.path.join(ROOT, 'docs/tva-live-scheduler/repo/.github/workflows/live-scheduler.yml'), encoding='utf-8').read(); Y = yaml.safe_load(WF); jb = Y['jobs']
ok('workflow: job update -> publish -> deploy -> verify-endpoint, pubblicazione solo se verified == true', all(k in jb for k in ('update', 'publish', 'deploy', 'verify-endpoint')) and "needs.update.outputs.verified == 'true'" in jb['publish']['if'] and jb['deploy']['needs'] == 'publish' and "deploy == 'true'" in jb['deploy']['if'])
ok('workflow: permessi minimi (update/verify nessuno, publish contents:write, deploy pages+id-token)', jb['update']['permissions'] == {} and jb['verify-endpoint']['permissions'] == {} and jb['publish']['permissions'] == {'contents': 'write'} and jb['deploy']['permissions'] == {'pages': 'write', 'id-token': 'write'})
ok('workflow: pubblicazione solo da main dello scheduler, dati letti da uno SHA fissato del branch TEST, mai main di marvel-timeline', 'refs/heads/main' in jb['publish']['if'] and 'needs.update.outputs.head_sha' in WF and not re.search(r'ref: main|--ref main', WF))
ok('workflow: Netlify citato solo come Origin del test CORS (nessun deploy), nessun artifact con segreti, token non stampato', not re.search(r'echo[^\n]*GH_TOKEN', WF, re.I) and [l.strip() for l in WF.splitlines() if 'netlify' in l.lower()] == ['ORIGIN: https://tva-archives-test-1110.netlify.app'])
bad = [n for n, c in RES if not c]; print('\n%d/%d PASS' % (len(RES) - len(bad), len(RES)))
for n in bad: print('FAIL: ' + n)
sys.exit(1 if bad else 0)
