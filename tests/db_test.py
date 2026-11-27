#!/usr/bin/env python3
"""W0 Database Expansion: verifiche automatiche essenziali."""
import subprocess, json, sys, pathlib, re
R = pathlib.Path(__file__).resolve().parent.parent
ok = fail = 0
def chk(c, m):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print('FAIL', m)
def run(*a): return subprocess.run(a, cwd=R, capture_output=True, text=True)
chk(run('python3','tools/db_ids.py','--verifica').returncode==0, 'registro ID')
chk(run('python3','tools/db_canon.py','--verifica').returncode==0, 'canon storico')
reg = json.load(open(R/'data/atlante/espansione/ids_registro.json'))
idx = json.load(open(R/'atlante2/data/index.json'))
chk(all(v['i'] in reg['ids'] and reg['ids'][v['i']]['stato']=='attivo' for v in idx['voci']), 'ID indice tutti registrati e attivi (immutabilita)')
chk(len(idx['voci'])==452, '452 voci invariate')
chk(run('git','diff','--quiet','HEAD','--','atlante2','index.html','sw.js','miss-minutes','assets').returncode==0, 'runtime a70 / Miss Minutes non modificati')
wf = (R/'.github/workflows/tmdb-sync.yml').read_text()
chk('workflow_dispatch' in wf and not re.search(r'^  (push|schedule|pull_request):', wf, re.M), 'workflow solo manuale')
chk('contents: read' in wf and 'git push' not in wf.split('db-censimento:')[-1], 'job censimento in sola lettura')
src = (R/'tools/db_censimento.py').read_text()
chk(not re.search(r'print\([^)]*(api_key|TOKEN)', src.replace("'COMICVINE_API_KEY'",'')), 'nessuna stampa di chiavi')
# test di non-regressione dei verificatori Atlas
for t in ('tools/atlante_a3.py','tools/atlante_identita.py','tools/atlante_relazioni.py','tools/atlante_a4.py'):
    chk(run('python3',t,'--verifica').returncode==0, t)
# prototipo ricerca
b = run('python3','tools/db_proto/build_search.py','/tmp/dbp_t','5000'); chk(b.returncode==0,'build indice prototipo')
chk(run('node','tools/db_proto/test_search.js','/tmp/dbp_t').returncode==0, 'ricerca alias/infix/accenti')
print(f'db_test: {ok} ok, {fail} fail'); sys.exit(1 if fail else 0)
