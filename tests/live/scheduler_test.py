"""TVA Live 1.1 - test del workflow dello scheduler (docs/tva-live-scheduler/repo/.github/workflows/live-scheduler.yml).
Lo script del job viene estratto dallo YAML ed eseguito con un `gh` simulato (nessuna rete, nessun token reale).
Uso: python3 tests/live/scheduler_test.py"""
import base64, json, os, re, stat, subprocess, sys, tempfile, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
WF = os.path.join(ROOT, 'docs/tva-live-scheduler/repo/.github/workflows/live-scheduler.yml')
src = open(WF, encoding='utf-8').read(); Y = yaml.safe_load(src); ON = Y.get('on') or Y.get(True)
RES = []
def ok(name, cond, extra=''):
    RES.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else '  >> ' + str(extra)), flush=True)
script = [s for s in Y['jobs']['update']['steps'] if s.get('id') == 'run'][0]['run']
GH = r'''#!/usr/bin/env python3
import json, os, sys, base64
S = json.load(open(os.environ['SC'])); d = os.environ['SD']; a = sys.argv[1:]
def cnt(k):
    p = os.path.join(d, k); n = int(open(p).read()) if os.path.exists(p) else 0; open(p, 'w').write(str(n + 1)); return n
open(os.path.join(d, 'calls.log'), 'a').write(' '.join(a) + '\n')
if a[:2] == ['workflow', 'run']:
    if S.get('dispatch_fail'): sys.exit(1)
    open(os.path.join(d, 'did'), 'w').write([x.split('=', 1)[1] for x in a if x.startswith('dispatch_id=')][0]); sys.exit(0)
if a[0] == 'api' and a[1].endswith('/commits/main'):
    if S.get('api_fail'): sys.exit(1)
    print(S['main'][min(cnt('mainc'), len(S['main']) - 1)]); sys.exit(0)
if a[0] == 'api' and a[1].endswith('/commits/test/tva-archives'):
    print(S['head'][min(cnt('headc'), len(S['head']) - 1)]); sys.exit(0)
if a[0] == 'api' and '/contents/assets/live/' in a[1]:
    f = a[1].split('/contents/assets/live/')[1].split('?')[0]; print(base64.b64encode(json.dumps(S['branch'][f]).encode()).decode()); sys.exit(0)
if a[:2] == ['run', 'list']:
    jq = a[a.index('--jq') + 1]; did = open(os.path.join(d, 'did')).read()
    if S.get('run_missing'): sys.exit(0)
    assert ('TVA Live update ' + did) in jq, jq; print(S.get('run_id', 4242)); sys.exit(0)
if a[:2] == ['run', 'view']: print('completed\t' + S['conclusion']); sys.exit(0)
if a[:2] == ['run', 'download']:
    if S.get('result') is None: sys.exit(1)
    D = a[a.index('-D') + 1]; json.dump(S['result'], open(os.path.join(D, 'RESULT.json'), 'w')); sys.exit(0)
sys.exit(9)
'''
def run(sc, dry=False):
    d = tempfile.mkdtemp(); b = os.path.join(d, 'bin'); os.makedirs(b)
    for n, body in (('gh', GH), ('sleep', '#!/bin/sh\nexit 0\n')):
        open(os.path.join(b, n), 'w').write(body); os.chmod(os.path.join(b, n), 0o755)
    json.dump(sc, open(os.path.join(d, 'sc.json'), 'w')); go = os.path.join(d, 'out'); open(go, 'w').close(); sm = os.path.join(d, 'sum'); open(sm, 'w').close()
    env = dict(os.environ, PATH=b + ':' + os.environ['PATH'], SC=os.path.join(d, 'sc.json'), SD=d, GITHUB_OUTPUT=go, GITHUB_STEP_SUMMARY=sm, GITHUB_RUN_ID='77', GITHUB_RUN_ATTEMPT='1',
               GH_TOKEN=sc.get('token', 'github_pat_FAKE_SECRET_VALUE'), DRY_RUN='true' if dry else 'false', TARGET_REPO='Posty2001/marvel-timeline', TARGET_REF='test/tva-archives', TARGET_WORKFLOW='tmdb-sync.yml')
    p = subprocess.run(['bash', '-c', script], env=env, capture_output=True, text=True, timeout=60)
    outs = dict(l.split('=', 1) for l in open(go).read().splitlines() if '=' in l)
    cl = os.path.join(d, 'calls.log')
    return p.returncode, outs, open(sm).read(), p.stdout + p.stderr, open(cl).read() if os.path.exists(cl) else ''
H = 'sha256:abc123'
def sc(result, conclusion='success', **kw):
    r = {'schema': 1, 'result': result, 'dry_run': False, 'forced': False, 'content_changed': result == 'update', 'generated_at': '2026-11-24T05:20:00', 'content_hash': H, 'blocking': [], 'warnings': []}
    r.update(kw.pop('res', {}))
    s = {'main': ['m1'], 'head': ['h1', 'h2'], 'conclusion': conclusion, 'result': r,
         'branch': {'manifest.json': {'content_hash': H}, 'status.json': {'content_hash': H, 'result': result}}}
    if kw.pop('no_result', False): s['result'] = None
    s.update(kw); return s

ok('struttura: cron giornaliero + avvio manuale con dry_run', ON.keys() == {'schedule', 'workflow_dispatch'} and re.match(r'^\d+ \d+ \* \* \*$', ON['schedule'][0]['cron']) and 'dry_run' in ON['workflow_dispatch']['inputs'])
ok('permessi: globali vuoti, job update senza permessi, solo keepalive con contents: write', Y['permissions'] == {} and Y['jobs']['update']['permissions'] == {} and Y['jobs']['keepalive']['permissions'] == {'contents': 'write'})
ok('branch bersaglio fisso (non e un input) e mai main come ref', Y['env']['TARGET_REF'] == 'test/tva-archives' and set(ON['workflow_dispatch']['inputs']) == {'dry_run'} and '--ref main' not in src)
ok('token solo da secrets.TVA_DISPATCH_TOKEN; nessuna stampa del token; nessun upload di artifact', 'secrets.TVA_DISPATCH_TOKEN' in src and not re.search(r'echo[^\n]*GH_TOKEN|upload-artifact|github_pat_|ghp_', src, re.I))
ok('keepalive parte anche se update fallisce e solo da cron', 'always()' in Y['jobs']['keepalive']['if'] and 'schedule' in Y['jobs']['keepalive']['if'])
ok('nessun contesto non fidato interpolato nello script (solo env/costanti)', '${{ github.event' not in script and '${{ inputs' not in script)

for oc in ('unchanged', 'heartbeat', 'update'):
    rc, o, s, out, calls = run(sc(oc))
    ok('%s: scheduler verde, verified=true, outcome corretto' % oc, rc == 0 and o.get('outcome') == oc and o.get('verified') == 'true' and o.get('content_hash') == H, (rc, o, out[-300:]))
    ok('%s: dispatch sul branch TEST con live_commit e correlazione, mai main' % oc, '--ref test/tva-archives' in calls and 'live_commit=true' in calls and 'dispatch_id=77-1' in calls and 'live_dry_run=false' in calls and re.findall(r'--ref (\S+)', calls) == ['test/tva-archives'])
    ok('%s: riepilogo con esito e head_sha = commit verificato' % oc, oc.upper() in s and o.get('head_sha') == 'h2', o)
    ok('%s: il token non compare in log, riepilogo, output, chiamate' % oc, 'FAKE_SECRET' not in out + s + json.dumps(o) + calls)
rc, o, s, out, _ = run(sc('rejected', 'failure', res={'blocking': ['Troppe nuove uscite (7 > 5)']}))
ok('rejected: scheduler rosso, verified=false, motivi nel riepilogo', rc == 1 and o.get('outcome') == 'rejected' and o.get('verified') == 'false' and 'Troppe nuove uscite' in s and 'RIFIUTATO' in s, (rc, o))
rc, o, s, out, _ = run(sc('update', 'failure'))
ok('update ma run fallito (commit non riuscito): rosso, verified=false', rc == 1 and o.get('verified') == 'false', (rc, o))
rc, o, s, out, _ = run(sc('update', branch={'manifest.json': {'content_hash': 'sha256:OLD'}, 'status.json': {'content_hash': H, 'result': 'update'}}))
ok('update ma il branch non contiene il contenuto validato: rosso, verified=false', rc == 1 and o.get('verified') == 'false', (rc, o))
rc, o, s, out, _ = run(sc('heartbeat', branch={'manifest.json': {'content_hash': H}, 'status.json': {'content_hash': H, 'result': 'unchanged'}}))
ok('heartbeat non registrato in status.json: rosso', rc == 1 and o.get('verified') == 'false', (rc, o))
rc, o, s, out, _ = run(sc('update', no_result=True))
ok('nessun RESULT.json (generazione fallita): rosso, verified=false', rc == 1 and o.get('verified') == 'false' and 'RESULT.json' in out, (rc, o))
rc, o, s, out, _ = run(sc('update', res={'result': 'boh'}))
ok('esito sconosciuto: rosso', rc == 1 and o.get('verified') == 'false')
rc, o, s, out, _ = run(sc('update', main=['m1', 'm2']))
ok('main cambiato durante il run: rosso e nessuna pubblicazione', rc == 1 and o.get('verified') == 'false' and 'main' in out, (rc, o))
rc, o, s, out, _ = run(sc('update', dispatch_fail=True))
ok('dispatch rifiutato (permessi token): rosso con messaggio chiaro', rc == 1 and 'Avvio del workflow rifiutato' in out and o.get('verified') == 'false')
rc, o, s, out, _ = run(sc('update', run_missing=True))
ok('run non ritrovato: rosso (nessun dato assunto)', rc == 1 and 'non trovato' in out and o.get('verified') == 'false')
rc, o, s, out, calls = run(sc('update', api_fail=True))
ok('token scaduto/non valido: rosso prima di avviare qualunque cosa', rc == 1 and 'workflow run' not in calls and o.get('verified') == 'false', calls)
rc, o, s, out, calls = run(sc('update', token=''))
ok('secret mancante: rosso, nessuna chiamata a GitHub', rc == 1 and calls == '' and 'TVA_DISPATCH_TOKEN' in out)
rc, o, s, out, calls = run(sc('update', head=['h1', 'h1']), dry=True)
ok('prova a secco: dispatch con live_dry_run=true, verde, mai verified', rc == 0 and 'live_dry_run=true' in calls and o.get('verified') == 'false' and 'PROVA A SECCO' in s, (rc, o, out[-200:]))
rc, o, s, out, calls = run(sc('update', head=['h1', 'h2']), dry=True)
ok('prova a secco ma il branch e cambiato: rosso', rc == 1)
rc, o, s, out, calls = run(sc('unchanged', head=['h1', 'h2']))
ok('unchanged con branch avanzato da altri commit: verde (catalogo coerente)', rc == 0 and o.get('verified') == 'true')

tsrc = open(os.path.join(ROOT, '.github/workflows/tmdb-sync.yml'), encoding='utf-8').read(); T = yaml.safe_load(tsrc); TI = (T.get(True) or T['on'])['workflow_dispatch']['inputs']
ok('tmdb-sync.yml espone gli input usati dallo scheduler', all(k in TI for k in ('solo_live_build', 'live_commit', 'live_dry_run', 'dispatch_id')))
ok('tmdb-sync.yml: run-name con correlazione e dry-run senza commit', "run-name:" in tsrc and "format('TVA Live update {0}', inputs.dispatch_id)" in tsrc and '!inputs.live_dry_run &&' in tsrc)
ok('il titolo cercato dallo scheduler coincide con il run-name del workflow', 'title="TVA Live update $did"' in script)
ok('tmdb-sync.yml: permessi invariati (globale read, write solo in live-update)', T['permissions'] == {'contents': 'read'} and T['jobs']['live-update']['permissions'] == {'contents': 'write'} and 'permissions' not in T['jobs']['sync'])
bad = [n for n, c in RES if not c]
print('\n%d/%d PASS' % (len(RES) - len(bad), len(RES)))
for n in bad: print('FAIL: ' + n)
sys.exit(1 if bad else 0)
