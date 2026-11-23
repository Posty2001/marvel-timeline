"""TVA Live 1.1 - test dell'aggiornamento automatico (tools/live_update.py + tools/live_git_commit.sh).
Tutto isolato: fonti simulate, repository Git temporaneo con remoto locale, date simulate. Nessuna rete, nessun dato reale toccato.
Uso: python3 tests/live/update_test.py"""
import copy, datetime as dt, hashlib, json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
os.environ.setdefault('TMDB_READ_TOKEN', 'test-token-xyz')
BT = {'__file__': os.path.join(HERE, 'build_test.py'), '__name__': 'bt'}
exec(compile(open(BT['__file__'], encoding='utf-8').read().split('# ---------------------------------------------------------------- scenario principale')[0], BT['__file__'], 'exec'), BT)
sys.path.insert(0, os.path.join(ROOT, 'tools')); import live_update as U  # noqa: E402
Net, mkroot, MOVIES, TV, D, yt_feed, TODAY = (BT[k] for k in ('Net', 'mkroot', 'MOVIES', 'TV', 'D', 'yt_feed', 'TODAY'))
M0, T0 = copy.deepcopy(MOVIES), copy.deepcopy(TV)
RES = []
def ok(name, cond, extra=''):
    RES.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  >> ' + str(extra)), flush=True)
def reset_world():
    MOVIES.clear(); MOVIES.update(copy.deepcopy(M0)); TV.clear(); TV.update(copy.deepcopy(T0))

class Net2(Net):
    """Fonte simulata con variazioni controllate: film extra/rimossi, trailer extra, eccezione non-HTTP."""
    def __init__(self, extra=(), drop=(), yt_extra=(), boom=False, **kw):
        super().__init__(**kw); self.extra, self.drop, self.yt_extra, self.boom = list(extra), set(drop) | {8, 10}, list(yt_extra), boom   # 8 e 10 dipendono dal giorno (uscito/data passata): esclusi per rendere stabile il mondo simulato
    def __call__(self, url, headers=None, **kw):
        if self.boom and 'themoviedb' in url and '/discover/movie' in url: raise RuntimeError('boom non-HTTP')
        r = super().__call__(url, headers, **kw)
        if r['status'] == 200 and 'themoviedb' in url and '/discover/movie' in url and 'with_companies' in url:
            j = json.loads(r['text']); j['results'] = [x for x in j['results'] if x['id'] not in self.drop] + [{'id': i} for i in self.extra]; r['text'] = json.dumps(j)
        if r['status'] == 200 and 'youtube.com/feeds' in url and self.yt_extra:
            add = ''.join('<entry><yt:videoId>%s</yt:videoId><title>%s</title><link rel="alternate" href="https://www.youtube.com/watch?v=%s"/><published>2026-11-20T10:00:00+00:00</published><media:group><media:description>x</media:description></media:group></entry>' % (v, t, v) for v, t in self.yt_extra)
            r['text'] = r['text'].replace('</feed>', add + '</feed>')
        return r
def fresh(i): MOVIES[i] = D('Fresh Announcement %d' % i, '2027-1%d-01' % (i - 79), poster='/f%d.jpg' % i)
def live(root, n): return open(os.path.join(root, 'assets/live', n), encoding='utf-8').read() if os.path.exists(os.path.join(root, 'assets/live', n)) else None
def snap(root): return {n: live(root, n) for n in ('calendar.json', 'trailers.json', 'manifest.json', 'status.json')}
def go(root, net, today=TODAY, *extra):
    out = tempfile.mkdtemp(); rc = U.main(['--root', root, '--out', out, '--today', today, *extra], fetch=net); return rc, out
def msg(out): p = os.path.join(out, 'COMMIT_MSG.txt'); return open(p, encoding='utf-8').read() if os.path.exists(p) else ''
def res_of(out): return re.search(r'\*\*Esito: (\w+)', open(os.path.join(out, 'SUMMARY.md'), encoding='utf-8').read()).group(1).lower()
def day(n): return (dt.date.fromisoformat(TODAY) + dt.timedelta(days=n)).isoformat()

print('1) bootstrap, nessuna modifica, heartbeat')
reset_world(); root = mkroot()
rc, out = go(root, Net2()); s1 = snap(root)
ok('bootstrap: esito update e file scritti (3 JSON + status)', rc == 0 and res_of(out) == 'update' and all(s1.values()))
st = json.loads(s1['status.json']); ok('status.json: ultima verifica e ultimo cambio registrati', st['last_check'] and st['last_change'] == st['last_check'] and st['content_hash'] == json.loads(s1['manifest.json'])['content_hash'])
rc, out = go(root, Net2()); ok('nessuna modifica: esito unchanged, nessun file riscritto, nessun messaggio di commit', rc == 0 and res_of(out) == 'unchanged' and snap(root) == s1 and not msg(out))
rc, out = go(root, Net2(), day(3)); ok('3 giorni dopo, invariato: ancora nessuna scrittura (niente commit quotidiani)', res_of(out) == 'unchanged' and snap(root) == s1)
rc, out = go(root, Net2(), day(8)); s2 = snap(root); st2 = json.loads(s2['status.json'])
ok('heartbeat dopo 8 giorni: contenuti identici, generated_at e last_check aggiornati, last_change invariato', res_of(out) == 'heartbeat' and json.loads(s2['calendar.json'])['items'] == json.loads(s1['calendar.json'])['items'] and json.loads(s2['trailers.json'])['items'] == json.loads(s1['trailers.json'])['items'] and json.loads(s2['manifest.json'])['generated_at'] > json.loads(s1['manifest.json'])['generated_at'] and st2['last_check'] > st['last_check'] and st2['last_change'] == st['last_change'], (st, st2))
ok('heartbeat: messaggio di commit esplicito, nessun cambiamento di contenuto', 'verifica periodica' in msg(out) and 'invariato' in msg(out))

print('2) nuova uscita, cambio data, nuovo trailer')
cal0 = {i['key']: i for i in json.loads(live(root, 'calendar.json'))['items']}
fresh(80); rc, out = go(root, Net2(extra=[80]), day(9)); cal1 = {i['key']: i for i in json.loads(live(root, 'calendar.json'))['items']}
new = set(cal1) - set(cal0); ok('nuova uscita: update, una sola voce nuova, provvisoria e senza scheda Timeline', res_of(out) == 'update' and len(new) == 1 and all(cal1[k]['confidence'] == 'provisional' and not cal1[k]['timelineId'] for k in new), new)
ok('nuova uscita: messaggio di commit con il riepilogo (+1 uscite)', '+1 uscite' in msg(out) and 'nuova: ' + list(new)[0] in msg(out))
ok('nuova uscita: le altre voci invariate byte per byte (updatedAt/firstSeen stabili)', all(json.dumps(cal1[k], sort_keys=True) == json.dumps(cal0[k], sort_keys=True) for k in cal0))
fresh(80); MOVIES[80]['release_date'] = '2027-11-15'; rc, out = go(root, Net2(extra=[80]), day(10)); cal2 = {i['key']: i for i in json.loads(live(root, 'calendar.json'))['items']}
k80 = list(new)[0]; ok('cambio data: update con vecchia e nuova data nel messaggio', res_of(out) == 'update' and cal1[k80]['date'] != cal2[k80]['date'] and ('%s -> %s' % (cal1[k80]['date'], cal2[k80]['date'])) in msg(out) and cal2[k80]['updatedAt'] == day(10), msg(out))
rc, out = go(root, Net2(extra=[80], yt_extra=[('NEWTRAILER1', 'Fresh Announcement 80 | Official Teaser')]), day(10)); tr = json.loads(live(root, 'trailers.json'))['items']
ok('nuovo trailer: update con un solo trailer in piu', res_of(out) == 'update' and any(t['key'] == 'yt:NEWTRAILER1' for t in tr) and '+1 trailer' in msg(out), msg(out))
s_ok = snap(root)

print('3) fonte irraggiungibile, catalogo parziale, errori di generazione')
rc, out = go(root, Net2(extra=[80], tmdb_ok=False), day(11)); _rj = json.load(open(os.path.join(out, 'RESULT.json')))
ok('RESULT.json: esito leggibile da macchina anche se rifiutato (motivi, hash, nessun dato sensibile)', _rj['schema'] == 1 and _rj['result'] == 'rejected' and _rj['blocking'] and set(_rj) == {'schema', 'result', 'dry_run', 'forced', 'content_changed', 'generated_at', 'content_hash', 'blocking', 'warnings'} and 'token' not in json.dumps(_rj).lower())
rc, out = go(root, Net2(extra=[80], tmdb_ok=False), day(11)); ok('TMDB irraggiungibile: rifiutato (exit 1), catalogo valido intatto', rc == 1 and res_of(out) == 'rejected' and snap(root) == s_ok and os.path.exists(os.path.join(out, 'rejected/calendar.json')) and 'TMDB non ok' in open(out + '/SUMMARY.md').read())
rc, out = go(root, Net2(extra=[80], fail_paths=('/movie/2',)), day(11)); ok('catalogo parziale (errore su un dettaglio): rifiutato, nulla scritto', rc == 1 and res_of(out) == 'rejected' and snap(root) == s_ok and 'partial' in open(out + '/SUMMARY.md').read())
rc, out = go(root, Net2(extra=[80], yt_ok=False), day(11)); ok('YouTube irraggiungibile: trailer validi mantenuti byte per byte, nessuna perdita, avviso nel riepilogo', rc == 0 and snap(root)['trailers.json'] == s_ok['trailers.json'] and 'YouTube non ok' in open(out + '/SUMMARY.md').read(), res_of(out))
s_ok = snap(root)
rc, out = go(root, Net2(extra=[80], channel_in_page=False), day(11)); ok('identita canale YouTube non verificata: nessun trailer nuovo accettato, trailer validi mantenuti', rc in (0, 1) and snap(root)['trailers.json'] == s_ok['trailers.json'])
fresh(81); rc, out = go(root, Net2(extra=[80, 81], yt_ok=False), day(11)); sy = json.loads(live(root, 'manifest.json'))
ok('YouTube giu + nuova uscita TMDB: calendario aggiornato, trailer invariati, manifest dichiara youtube stale e hash coerente', rc == 0 and res_of(out) == 'update' and sy['sources']['youtube']['status'] == 'stale' and sy['counts']['trailers'] == len(json.loads(live(root, 'trailers.json'))['items']) and sy['content_hash'] == U.B.hashlib.sha256((U.B.canon(json.loads(live(root, 'calendar.json'))['items']) + U.B.canon(json.loads(live(root, 'trailers.json'))['items'])).encode()).hexdigest()[:16])
del MOVIES[81]; s_ok = snap(root)
rc, out = go(root, Net2(extra=[80, 81], boom=True), day(11)); ok('errore imprevisto del generatore: exit != 0, nessun file toccato', rc != 0 and snap(root) == s_ok, rc)
reset_world(); fresh(80); MOVIES[80]['release_date'] = '2027-11-15'

print('4) soglie anti-anomalia, regressioni, force')
shutil.rmtree(root); root = mkroot(); go(root, Net2(extra=[80]), day(9)); s_ok = snap(root)
for i in range(81, 87): fresh(i)
rc, out = go(root, Net2(extra=[80] + list(range(81, 87))), day(11)); ok('troppe nuove uscite in un colpo (6 > 5): rifiutato, nulla scritto', rc == 1 and 'Troppe nuove voci' in open(out + '/SUMMARY.md').read() and snap(root) == s_ok)
rc, out = go(root, Net2(extra=[80] + list(range(81, 87))), day(11), '--force'); ok('--force supera la soglia: update con 6 nuove voci', rc == 0 and res_of(out) == 'update' and len(json.loads(live(root, 'calendar.json'))['items']) == len(cal2) + 6)
reset_world(); fresh(80); MOVIES[80]['release_date'] = '2027-11-15'
shutil.rmtree(root); root = mkroot(); go(root, Net2(extra=[80]), day(9)); s_ok = snap(root)
rc, out = go(root, Net2(extra=[80], drop=[1, 2, 3, 7, 13]), day(12)); ok('spariscono 5 uscite future insieme: rifiutato (rimozione anomala)', rc == 1 and 'Rimosse' in open(out + '/SUMMARY.md').read() and snap(root) == s_ok)
c = json.loads(live(root, 'calendar.json')); vi = next(i for i in c['items'] if not i['timelineId']); vi['timelineId'] = '999'; open(os.path.join(root, 'assets/live/calendar.json'), 'w').write(U.B.canon(c))
rc, out = go(root, Net2(extra=[80]), day(12)); ok('perdita del collegamento Timeline: rifiutato', rc == 1 and 'collegamento Timeline' in open(out + '/SUMMARY.md').read())
c = json.loads(live(root, 'calendar.json')); vi['timelineId'] = None; c['items'] = [vi if i['key'] == vi['key'] else i for i in c['items']]
conf = c['items'][0]; conf['confidence'] = 'confirmed'; open(os.path.join(root, 'assets/live/calendar.json'), 'w').write(U.B.canon(c))
rc, out = go(root, Net2(extra=[80]), day(12)); ok('declassamento da Confermato (fonte non piu nel feed): rifiutato', rc == 1 and 'Declassato da Confermato' in open(out + '/SUMMARY.md').read())
for n_, t_ in s_ok.items(): open(os.path.join(root, 'assets/live', n_), 'w').write(t_)
rc, out = go(root, Net2(extra=[80], tmdb_ok=False), day(12), '--force'); ok('--force NON supera i controlli di fonte (TMDB down resta rifiutato)', rc == 1)
ok('rejected: il candidato bloccato e salvato per l\'ispezione', os.path.exists(os.path.join(out, 'rejected/REPORT.md')))
fresh(81); sb = snap(root); rc, out = go(root, Net2(extra=[80, 81]), day(12), '--dry-run'); ok('--dry-run: calcola l\'esito (update) ma non scrive nulla in assets/live', rc == 0 and res_of(out) == 'update' and snap(root) == sb and 'prova a secco' in open(out + '/SUMMARY.md').read()); del MOVIES[81]

print('5) validatore: duplicati, link, schema (unit)')
base = {k: json.loads(s_ok[k + '.json']) for k in ('calendar', 'trailers', 'manifest')}; cfg = U.B.load_json(os.path.join(ROOT, 'tools/live/config.json'))
cur = {'calendar': base['calendar'], 'trailers': base['trailers'], 'manifest': base['manifest'], 'status': json.loads(s_ok['status.json'])}
def ev(mod): c = copy.deepcopy(base); mod(c); return U.evaluate(c, cur, cfg, TODAY)
r = ev(lambda c: c['calendar']['items'].append(copy.deepcopy(c['calendar']['items'][0]))); ok('chiavi duplicate nel calendario: rifiutato', r['result'] == 'rejected' and any('duplicate' in b for b in r['blocking']))
r = ev(lambda c: c['trailers']['items'] and c['trailers']['items'].append(copy.deepcopy(c['trailers']['items'][0]))); ok('chiavi duplicate nei trailer: rifiutato', r['result'] == 'rejected')
def bad_link(c): c['calendar']['items'][0]['sources'] = [{'name': 'x', 'url': 'http://evil.example/x', 'official': False}]
r = ev(bad_link); ok('link non https o non valido: rifiutato', r['result'] == 'rejected')
def bad_conf(c): c['calendar']['items'][0]['confidence'] = 'confirmed'; c['calendar']['items'][0]['sources'] = []
r = ev(bad_conf); ok('Confermato senza fonte ufficiale: rifiutato dalla validazione', r['result'] == 'rejected' and any('Validazione' in b for b in r['blocking']))
r = ev(lambda c: c['manifest']['sources']['tmdb'].update(status='stale')); ok('stato TMDB stale/partial/error mai promosso', r['result'] == 'rejected')
r = ev(lambda c: None); ok('catalogo identico: unchanged (il generated_at non e un cambiamento)', r['result'] == 'unchanged' or r['result'] == 'heartbeat')
r = ev(lambda c: c['manifest'].update(generated_at='2030-01-01T00:00:00+00:00')); ok('solo generated_at diverso: nessun cambiamento di contenuto', r['content_changed'] is False)

print('6) scrittura atomica')
d = tempfile.mkdtemp(); open(d + '/calendar.json', 'w').write('OLD-C'); open(d + '/manifest.json', 'w').write('OLD-M')
orig = os.replace; n = {'c': 0}
def flaky(a, b):
    n['c'] += 1
    if n['c'] == 2: raise OSError('disco pieno simulato')
    return orig(a, b)
os.replace = flaky
try:
    try: U.write_atomic(d, {'calendar.json': 'NEW-C', 'manifest.json': 'NEW-M'}); raised = False
    except OSError: raised = True
finally: os.replace = orig
ok('scrittura interrotta a meta: ripristino di tutti i file, nessun temporaneo residuo', raised and open(d + '/calendar.json').read() == 'OLD-C' and open(d + '/manifest.json').read() == 'OLD-M' and not [f for f in os.listdir(d) if f.endswith('.tmp')])

print('7) repository Git temporaneo con remoto locale (commit solo dati, solo branch TEST)')
def sh(cwd, *c, check=True):
    r = subprocess.run(c, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode: raise RuntimeError(' '.join(c) + '\n' + r.stdout + r.stderr)
    return r
reset_world(); fresh(80); MOVIES[80]['release_date'] = '2027-11-15'
remote = tempfile.mkdtemp(); sh(remote, 'git', 'init', '-q', '--bare', '-b', 'test/tva-archives')
root = mkroot(); os.makedirs(root + '/tools', exist_ok=True); shutil.copy(os.path.join(ROOT, 'tools/live_git_commit.sh'), root + '/tools/'); open(root + '/index.html', 'w').write('<html>app</html>'); open(root + '/README', 'w').write('x')
go(root, Net2(), TODAY)
sh(root, 'git', 'init', '-q', '-b', 'test/tva-archives'); sh(root, 'git', 'config', 'user.email', 'a@a'); sh(root, 'git', 'config', 'user.name', 'a'); sh(root, 'git', 'add', '-A'); sh(root, 'git', 'commit', '-q', '-m', 'init'); sh(root, 'git', 'remote', 'add', 'origin', remote); sh(root, 'git', 'push', '-q', 'origin', 'test/tva-archives')
def commits(): return int(sh(remote, 'git', 'rev-list', '--count', 'test/tva-archives').stdout)
def publish(out): return sh(root, 'bash', 'tools/live_git_commit.sh', os.path.join(out, 'COMMIT_MSG.txt'), 'origin', check=False)
n0 = commits(); rc, out = go(root, Net2(), TODAY); p = sh(root, 'bash', 'tools/live_git_commit.sh', '/dev/null', 'origin', check=False)
ok('git: catalogo invariato -> nessun commit, il remoto non cambia', rc == 0 and p.returncode == 0 and commits() == n0)
fresh(80); rc, out = go(root, Net2(extra=[80]), day(1)); p = publish(out); files = sh(remote, 'git', 'show', '--name-only', '--format=%an%n%s', 'test/tva-archives').stdout.split('\n')
ok('git: nuova uscita -> un commit sul branch TEST con il riepilogo', p.returncode == 0 and commits() == n0 + 1 and 'tva-live-bot' in files[0] and '+1 uscite' in files[1], p.stderr)
ok('git: il commit tocca SOLO i file di dati di assets/live (mai index.html, tools, ecc.)', set(f for f in files[2:] if f) <= {'assets/live/calendar.json', 'assets/live/trailers.json', 'assets/live/manifest.json', 'assets/live/status.json'} and 'assets/live/calendar.json' in files)
ok('git: nessun altro branch creato, main assente', sh(remote, 'git', 'for-each-ref', '--format=%(refname)').stdout.split() == ['refs/heads/test/tva-archives'])
n1 = commits(); prev_cal = live(root, 'calendar.json')
for k in range(2, 7): rc, out = go(root, Net2(extra=[80]), day(k)); publish(out)
ok('git: 5 giorni consecutivi senza novita -> nessun commit quotidiano', commits() == n1)
rc, out = go(root, Net2(extra=[80]), day(9)); p = publish(out)
ok('git: dopo 8 giorni una sola verifica periodica (heartbeat) con solo generated_at/status', res_of(out) == 'heartbeat' and commits() == n1 + 1 and 'verifica periodica' in sh(remote, 'git', 'log', '-1', '--format=%s', 'test/tva-archives').stdout)
rc, out = go(root, Net2(extra=[80], tmdb_ok=False), day(10)); p = publish(out); ok('git: TMDB down -> rifiutato, nessun commit, catalogo valido intatto sul remoto', rc == 1 and commits() == n1 + 1)
sh(root, 'git', 'checkout', '-q', '-b', 'main'); fresh(80); MOVIES[80]['release_date'] = '2027-12-25'; rc, out = go(root, Net2(extra=[80]), day(11)); p = publish(out)
ok('git: su un branch diverso (main) il commit e rifiutato (exit 3) e nulla parte', p.returncode == 3 and commits() == n1 + 1 and 'refs/heads/main' not in sh(remote, 'git', 'for-each-ref', '--format=%(refname)').stdout)
sh(root, 'git', 'checkout', '-q', '-f', 'test/tva-archives'); sh(root, 'git', 'branch', '-D', 'main', check=False)
open(root + '/stray.txt', 'w').write('x'); sh(root, 'git', 'add', 'stray.txt'); fresh(80); MOVIES[80]['release_date'] = '2027-12-25'; rc, out = go(root, Net2(extra=[80]), day(11)); p = publish(out)
ok('git: file estraneo in stage -> rifiutato (exit 4), nulla pubblicato', p.returncode == 4 and commits() == n1 + 1)
sh(root, 'git', 'reset', '-q', '--hard', 'origin/test/tva-archives'); os.remove(root + '/stray.txt') if os.path.exists(root + '/stray.txt') else None
other = tempfile.mkdtemp(); sh(other, 'git', 'clone', '-q', remote, 'c'); oc = other + '/c'; sh(oc, 'git', 'config', 'user.email', 'o@o'); sh(oc, 'git', 'config', 'user.name', 'o'); open(oc + '/docs.txt', 'w').write('altro'); sh(oc, 'git', 'add', '-A'); sh(oc, 'git', 'commit', '-q', '-m', 'push concorrente'); sh(oc, 'git', 'push', '-q', 'origin', 'test/tva-archives')
rc, out = go(root, Net2(extra=[80]), day(11)); p = publish(out)
ok('git: push concorrente di altri sul branch -> rebase automatico e pubblicazione riuscita', res_of(out) == 'update' and p.returncode == 0 and 'docs.txt' in sh(remote, 'git', 'ls-tree', '--name-only', 'test/tva-archives').stdout and '2027-12-25' in sh(remote, 'git', 'show', 'test/tva-archives:assets/live/calendar.json').stdout, p.stderr)
sh(root, 'git', 'checkout', '-q', 'HEAD~1', '--', 'assets/live'); ok('git: cronologia recuperabile (ripristino del catalogo precedente da un commit)', '2027-12-25' not in live(root, 'calendar.json') and '2027-11-01' in live(root, 'calendar.json'))

print('8) avvisi end-to-end: catalogo generato dall\'aggiornatore -> app, orologio simulato, nessun duplicato')
reset_world(); r2 = mkroot(); seq = []
def cat(net, d_): go(r2, net, d_); seq.append({k: json.loads(live(r2, k + '.json')) for k in ('calendar', 'trailers', 'manifest')})
cat(Net2(), TODAY); cat(Net2(), day(8))
fresh(80); cat(Net2(extra=[80]), day(9)); MOVIES[80]['release_date'] = '2027-11-15'; cat(Net2(extra=[80]), day(9))
cat(Net2(extra=[80], yt_extra=[('NEWTRAILER1', 'Fresh Announcement 80 | Official Teaser')]), day(9))
NS = {'__file__': os.path.join(HERE, 'ui_test.py'), '__name__': 'ui_helpers'}
exec(compile(open(NS['__file__'], encoding='utf-8').read().split('with sync_playwright() as pw:')[0], NS['__file__'], 'exec'), NS)
STATE, new_ctx, open_page, reload, go_live, jl, PK = (NS[k] for k in ('STATE', 'new_ctx', 'open_page', 'reload', 'go_live', 'jl', 'PK'))
with NS['sync_playwright']() as pw:
    b = pw.chromium.launch(); T = dt.datetime(2026, 11, 21, 10)
    def clock(ctx, n): ctx.clock.set_fixed_time(T + dt.timedelta(days=n))
    def show(c): STATE.update(cal=c['calendar']['items'], tr=c['trailers']['items'], man=c['manifest'], fail=False)
    show(seq[0]); ctx = new_ctx(b); ctx.clock.install(time=T); clock(ctx, 0); pg = open_page(ctx); go_live(pg, 'avv'); pg.wait_for_timeout(200)
    def inbox(): return pg.evaluate("()=>window.tvaLive.prefs().inbox")
    def visit(idx, n): show(seq[idx]); clock(ctx, n); reload(pg); go_live(pg, 'avv'); pg.wait_for_timeout(250)
    ok('app: primo catalogo generato dall\'aggiornatore -> nessun avviso', len(inbox()) == 0)
    visit(1, 8); ok('app: heartbeat (solo generated_at) -> nessun avviso', len(inbox()) == 0)
    visit(2, 9); ok('app: nuova uscita -> un solo avviso', [a['t'] for a in inbox()] == ['new'])
    visit(2, 9); visit(2, 10); ok('app: riaperture -> nessun duplicato', [a['t'] for a in inbox()] == ['new'])
    visit(3, 10); ok('app: cambio data -> un avviso con vecchia e nuova data', sorted(a['t'] for a in inbox()) == ['date', 'new'])
    visit(4, 11); visit(4, 11); ok('app: nuovo trailer -> un avviso, nessun duplicato', sorted(a['t'] for a in inbox()) == ['date', 'new', 'trailer'])
    ok('app: preferenze e titoli seguiti intatti dall\'aggiornamento', pg.evaluate("()=>{const p=window.tvaLive.prefs();return Array.isArray(p.followed)&&p.v===1}"))
    b.close()

print('9) controlli statici: permessi minimi, nessun deploy, nessun costo')
wf = open(os.path.join(ROOT, '.github/workflows/tmdb-sync.yml'), encoding='utf-8').read()
import yaml
Y = yaml.safe_load(wf); trig = Y.get('on') or Y.get(True)
ok('workflow: solo workflow_dispatch (nessun cron, nessun push/pull_request trigger)', list(trig) == ['workflow_dispatch'])
ok('workflow: permessi globali in sola lettura', Y['permissions'] == {'contents': 'read'})
lj = Y['jobs']['live-update']
ok('job live-update: unico permesso contents: write, concurrency senza annullamento, timeout', lj['permissions'] == {'contents': 'write'} and lj['concurrency']['group'] == 'tva-live-update' and lj['concurrency']['cancel-in-progress'] is False and lj['timeout-minutes'] <= 10)
ok('job sync (storico): nessun permesso di scrittura, saltato quando live_commit e attivo', 'permissions' not in Y['jobs']['sync'] and 'live_commit' in Y['jobs']['sync']['if'])
ok('live-update: guard sul ref test/tva-archives e checkout fissato su quel branch', 'refs/heads/test/tva-archives' in lj['steps'][0]['run'] and lj['steps'][1]['with']['ref'] == 'test/tva-archives')
ok('live-update: commit solo tramite lo script, solo se update/heartbeat', any('live_git_commit.sh' in str(s.get('run', '')) and 'update' in str(s.get('if', '')) and 'heartbeat' in str(s.get('if', '')) for s in lj['steps']))
ok('workflow: nessun git push diretto, nessun riferimento a main, nessun deploy/Netlify', not re.search(r'git push|refs/heads/main|netlify|deploy', wf.split('live-update:')[1], re.I) and 'git push' not in wf)
sc = open(os.path.join(ROOT, 'tools/live_git_commit.sh'), encoding='utf-8').read()
ok('script commit: refspec fisso sul branch TEST, mai main, file consentiti solo assets/live', 'HEAD:refs/heads/$BRANCH' in sc and 'BRANCH="test/tva-archives"' in sc and 'main' not in re.sub(r'#.*', '', sc) and 'index.html' not in sc)
up = open(os.path.join(ROOT, 'tools/live_update.py'), encoding='utf-8').read()
ok('aggiornatore: solo libreria standard, nessun accesso a index.html/preferenze/dati personali', not re.search(r'^\s*(import|from)\s+(requests|boto3|openai|anthropic)', up, re.M) and 'index.html' not in up and 'localStorage' not in up)
# (Fase 3: index.html e sw.js cambiano legittimamente - verifiche dedicate in remote_test.py)

tpl = open(os.path.join(ROOT, 'docs/tva-live-scheduler/repo/.github/workflows/live-scheduler.yml'), encoding='utf-8').read(); TY = yaml.safe_load(tpl)
ok('scheduler: YAML valido, cron giornaliero + manuale, token solo da secret, avvia solo il branch TEST (test completi: scheduler_test.py)', (TY.get('on') or TY.get(True)).keys() == {'schedule', 'workflow_dispatch'} and 'secrets.TVA_DISPATCH_TOKEN' in tpl and TY['env']['TARGET_REF'] == 'test/tva-archives' and not re.search(r'ghp_|github_pat_', tpl) and TY['concurrency']['cancel-in-progress'] is False)
ok('scheduler: nessun Netlify/deploy e nessun riferimento a main per il dispatch', not re.search(r'--ref main', tpl) and [l.strip() for l in tpl.splitlines() if 'netlify' in l.lower()] == ['ORIGIN: https://tva-archives-test-1110.netlify.app'])   # Netlify solo come Origin del test CORS
wfs = os.listdir(os.path.join(ROOT, '.github/workflows')); ok('il modello NON e installato come workflow di questo repository', sorted(wfs) == ['live-probe.yml', 'tmdb-sync.yml'])
bad = [n for n, c in RES if not c]
print('\nRISULTATO: %d ok, %d falliti' % (len(RES) - len(bad), len(bad)))
for n in bad: print(' FAIL:', n)
sys.exit(1 if bad else 0)
