#!/usr/bin/env python3
"""W5/W6 fumetti: classificazione, universo 616, gruppi/creatori, staging per una sola fonte; fixture sintetica in radice temporanea."""
import subprocess, os, sys, shutil, json, pathlib, tempfile, hashlib
R = pathlib.Path(__file__).resolve().parent.parent
ok = fail = 0
def chk(c, m):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print('FAIL', m)
T = pathlib.Path(tempfile.mkdtemp(prefix='dbroot_'))
(T/'data/atlante').mkdir(parents=True); (T/'atlante2/data').mkdir(parents=True)
shutil.copytree(R/'data/atlante/espansione', T/'data/atlante/espansione', ignore=shutil.ignore_patterns('raw'))
for f in (T/'data/atlante/espansione/canon').glob('w*_*.jsonl'): f.unlink()
rp = T/'data/atlante/espansione/ids_registro.json'; rg = json.load(open(rp))
rg['ids'] = {k: v for k, v in rg['ids'].items() if v.get('origine') == 'registro-storico'}
rg['conteggi'] = {'totale': len(rg['ids']), 'attivi': len(rg['ids'])}; rg['ids_sha256'] = hashlib.sha256('\n'.join(sorted(rg['ids'])).encode()).hexdigest()
json.dump(rg, open(rp, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
for f in ('identita.json', 'manifest.json'): shutil.copy(R/'data/atlante'/f, T/'data/atlante'/f)
shutil.copy(R/'atlante2/data/index.json', T/'atlante2/data/index.json')
env = dict(os.environ, DB_ROOT=str(T))
def run(*a): return subprocess.run(a, cwd=R, capture_output=True, text=True, env=env)
fx = 'tests/fixtures/w5_raw_fixture.json'
for onda in ('w5', 'w6'):
    p = run('python3', 'tools/db_w1_build.py', fx, '--onda', onda, '--scrivi'); chk(p.returncode == 0, 'build ' + onda + ' ' + p.stderr[-300:])
canon = {}
for n in ('w5_fumetti_entita', 'w6_fumetti_opere'):
    f = T/'data/atlante/espansione/canon'/(n + '.jsonl')
    if f.exists():
        for l in f.read_text().splitlines():
            if l.strip(): r = json.loads(l); canon[r['nome']] = r
chk(canon.get('Marvel Universe', {}).get('id') == 'uni-earth-616' and canon['Marvel Universe']['tipo'] == 'universo', 'universo Marvel = uni-earth-616')
chk(canon.get('Moon Knight Zzyx', {}).get('universo') == 'uni-earth-616', 'personaggio assegnato alla continuita 616 (P1080)')
chk(canon.get('Order of the Zzyx', {}).get('tipo') == 'organizzazione' and canon.get('Zzyx Species', {}).get('tipo') == 'specie', 'organizzazioni e specie classificate')
chk(canon.get('Zzyx Saga', {}).get('tipo') == 'evento', 'saga/storyline = evento documentato (non scartata)')
chk(canon.get('Zzyx Comics Vol. 1', {}).get('tipo') == 'opera', 'testata = opera')
chk(canon.get('Zzyx Writer', {}).get('tipo') == 'creatore', 'creatore dei fumetti')
chk('Lone Source Zzyx' not in canon and 'Lone Source Zzyx' in (T/'data/atlante/espansione/staging/w5_staging.jsonl').read_text(), 'una sola fonte (nessun articolo Wikipedia) = staging (D12)')
chk(all(r['stato_verifica'] == 'verificata' for r in canon.values()), 'solo voci verificate in canon')
chk(run('python3', 'tools/db_ids.py', '--verifica').returncode == 0, 'registro ID coerente dopo W5/W6')
chk(run('python3', 'tools/db_canon.py', '--verifica').returncode == 0, 'canon W5/W6 valido a schema')
print('db_w5_test: %d ok, %d fail' % (ok, fail)); sys.exit(1 if fail else 0)
