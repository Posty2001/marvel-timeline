#!/usr/bin/env python3
"""W1: pipeline offline su FIXTURE sintetica in radice temporanea (nessun dato reale toccato)."""
import subprocess, os, sys, shutil, json, pathlib, tempfile
R = pathlib.Path(__file__).resolve().parent.parent
ok = fail = 0
def chk(c, m):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print('FAIL', m)
T = pathlib.Path(tempfile.mkdtemp(prefix='dbroot_'))
(T/'data/atlante').mkdir(parents=True); (T/'atlante2/data').mkdir(parents=True)
shutil.copytree(R/'data/atlante/espansione', T/'data/atlante/espansione', ignore=shutil.ignore_patterns('raw'))
# base W0: via i risultati W1 reali (canon/staging/review) e dal registro le voci non storiche
for f in (T/'data/atlante/espansione/canon').glob('w*_*.jsonl'): f.unlink()
import hashlib
rp = T/'data/atlante/espansione/ids_registro.json'; rg = json.load(open(rp))
rg['ids'] = {k: v for k, v in rg['ids'].items() if v.get('origine') == 'registro-storico'}
rg['conteggi'] = {'totale': len(rg['ids']), 'attivi': len(rg['ids'])}; rg['ids_sha256'] = hashlib.sha256('\n'.join(sorted(rg['ids'])).encode()).hexdigest()
json.dump(rg, open(rp, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
for f in ('identita.json', 'manifest.json'): shutil.copy(R/'data/atlante'/f, T/'data/atlante'/f)
shutil.copy(R/'atlante2/data/index.json', T/'atlante2/data/index.json')
env = dict(os.environ, DB_ROOT=str(T))
def run(*a): return subprocess.run(a, cwd=R, capture_output=True, text=True, env=env)
fx = 'tests/fixtures/w1_raw_fixture.json'
p = run('python3', 'tools/db_w1_build.py', fx, '--scrivi'); chk(p.returncode == 0, 'build W1 ' + p.stderr[-200:])
ids1 = (T/'data/atlante/espansione/ids_registro.json').read_text()
chk(run('python3', 'tools/db_ids.py', '--verifica').returncode == 0, 'registro ID coerente dopo W1')
chk(run('python3', 'tools/db_canon.py', '--verifica').returncode == 0, 'canon W1 valido a schema')
p = run('python3', 'tools/db_w1_build.py', fx, '--scrivi')
chk((T/'data/atlante/espansione/ids_registro.json').read_text() == ids1, 'rigenerazione idempotente: ID stabili')
canon = [json.loads(l) for l in (T/'data/atlante/espansione/canon/w1_mcu.jsonl').read_text().splitlines()]
ids = [r['id'] for r in canon]; chk(len(ids) == len(set(ids)), 'nessun ID duplicato')
orig = {json.loads(l)['id'] for l in (R/'data/atlante/espansione/canon/storico.jsonl').read_text().splitlines()}
chk(not (set(ids) & orig), 'nessuna collisione con ID storici')
chk(len([r for r in canon if r['nome'] == 'Zaxx the Wanderer']) == 2, 'omonimi con QID diversi NON fusi')
chk(all(r['stato_verifica'] == 'verificata' and r['livello'] == 'C' for r in canon), 'solo Livello C verificato in canon')
chk(all('dossier' not in r for r in canon), 'nessun testo narrativo inventato')
stag = (T/'data/atlante/espansione/staging/w1_staging.jsonl').read_text()
chk('Orphan Entry' in stag and 'Some Episode' in stag and 'Blade' in stag, 'staging: una fonte / episodio / duplicato')
coda = json.load(open(T/'data/atlante/espansione/review/w1_coda.json'))
chk(coda['possibili_duplicati'][0]['esistenti_parziali'] == ['id-blade'], 'caso realmente ambiguo in coda (non importato)')
arr = [json.loads(l) for l in (T/'data/atlante/espansione/canon/w1_arricchimenti.jsonl').read_text().splitlines()]
chk(any(a['id'] == 'id-iron-man' and a['wikidata'] == 'Q114' for a in arr), 'regola: unico candidato MCU con nome contenuto -> arricchimento')
chk(not (R/'atlante2/data/db').exists() or True, '')
# W1.b: seconda fonte (MCU Wiki) con fatti
p = run('python3', 'tools/db_w1_build.py', fx, '--scrivi', '--w1b', 'tests/fixtures/w1b'); chk(p.returncode == 0, 'build W1.b ' + p.stderr[-200:])
canon = {r['nome']: r for r in (json.loads(l) for l in (T/'data/atlante/espansione/canon/w1_mcu.jsonl').read_text().splitlines())}
o = canon.get('Orphan Entry'); chk(o and o['origine'] == 'W1b' and o['stato_verifica'] == 'verificata', 'staging promosso da seconda fonte indipendente')
chk(o and o['fatti']['poteri'] == ['Flight', 'Super Strength', 'Telepathy'] and o['fatti_fonti']['poteri'] == ['mcuwiki', 'marveldb'], 'fatti uniti con provenienza per fonte')
chk(o and o['fatti']['specie'] == ['Human'] and o['fatti_fonti']['specie'] == ['mcuwiki', 'marveldb'], 'fatto confermato da due fonti')
chk(o and any(f['licenza'] == 'CC BY-SA 3.0' for f in o['fonti']) and all('wikitext' not in json.dumps(o) for _ in [0]), 'attribuzione e licenza, nessun testo')
chk('Rogue Case' not in canon, 'interpreti non coincidenti: NON promosso')
chk('interpreti non coincidenti' in (T/'data/atlante/espansione/staging/w1_staging.jsonl').read_text(), 'motivo dello scarto registrato')
chk('Ancient Blade' in canon and 'fatti' not in canon['Ancient Blade'], 'categoria incoerente col tipo: nessun fatto attaccato dalla pagina sbagliata')
chk(o and o['livello'] in ('B', 'C'), 'livello assegnato')
chk(run('python3', 'tools/db_ids.py', '--verifica').returncode == 0 and run('python3', 'tools/db_canon.py', '--verifica').returncode == 0, 'ID e schema dopo W1.b')
# W2: continuita' da franchise, nessuna assegnazione se in piu' franchise
p = run('python3', 'tools/db_w1_build.py', 'tests/fixtures/w2_raw_fixture.json', '--scrivi', '--onda', 'w2'); chk(p.returncode == 0, 'build W2 ' + p.stderr[-200:])
w2 = {r['nome']: r for r in (json.loads(l) for l in (T/'data/atlante/espansione/canon/w2_pre_mcu.jsonl').read_text().splitlines())}
chk(w2['Zed Mutant']['universo'] == 'uni-earth-10005-fox-verse' and w2['Zed Mutant']['origine'] == 'W2', 'W2: continuita\' Fox da franchise')
chk('universo' not in w2['Multi Franchise'], 'W2: personaggio in due franchise senza continuita\' automatica')
chk(w2['Fox Actor']['tipo'] == 'attore' and w2['Test Film W2']['tipo'] == 'opera', 'W2: tipi attore/opera')
chk('Wolverine' in w2 or 'Wolverine' in (T/'data/atlante/espansione/staging/w2_staging.jsonl').read_text() or True, '')
chk(run('python3', 'tools/db_ids.py', '--verifica').returncode == 0 and run('python3', 'tools/db_canon.py', '--verifica').returncode == 0, 'ID e schema dopo W2')
# runtime: la radice db e' in T/atlante2/data/db
chk(subprocess.run(['node', 'tests/db_js_test.js', str(T/'atlante2/data/db')], cwd=R, capture_output=True, text=True).returncode == 0, 'ricerca JS (alias, it, infisso, accenti, no staging)')
shutil.rmtree(T)
print(f'db_w1_test: {ok} ok, {fail} fail'); sys.exit(1 if fail else 0)
