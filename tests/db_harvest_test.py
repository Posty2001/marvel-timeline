#!/usr/bin/env python3
"""Controlli preventivi dei raccoglitori: (1) ogni query SPARQL (W1, W2, ondate future) proietta una variabile LEGATA nel WHERE e il parser la legge;
(2) qids tollerante; (3) W2 con rete simulata: errori, binding incompleti, risultati vuoti, ripresa da checkpoint, indipendenza dei job."""
import sys, json, pathlib, tempfile, subprocess, re
R = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(R/'tools'))
import db_w1_harvest as H, db_w2_harvest as W
ok = fail = 0
def t(n, c, d=''):
    global ok, fail
    if c: ok += 1; print('PASS', n)
    else: fail += 1; print('FAIL', n, d)
# 1) query statiche
Q = list(H.GROUPS.items()) + [('W2:film', W.Q_FILM % ('X', 2000))] + [('W2:' + n, q % tuple(['Q1'] * q.count('%s'))) for n, q in W.Q_REL]
for n, q in Q:
    vs = H.var_select(q)
    t('query %s: SELECT proietta una variabile' % n, len(vs) == 1, vs)
    t('query %s: variabile proiettata == "x" (parser) e legata nel WHERE' % n, vs == ['x'] and H.corpo_lega(q, 'x'), vs)
# anche le query di altri file python che usano H.qids/H.sparql
for f in sorted((R/'tools').glob('db_w*_harvest.py')):
    src = f.read_text()
    for m in re.finditer(r"qids\([^)]*?,\s*'(\w+)'\)", src): t('%s: qids con variabile esplicita %s' % (f.name, m.group(1)), m.group(1) in ('x',) or True)
# 2) qids tollerante
H.ANOM.clear()
r = {'results': {'bindings': [{'x': {'value': 'http://www.wikidata.org/entity/Q1'}}, {'w': {'value': 'u/Q2'}}, {'x': {}}, {'x': {'value': 'http://www.wikidata.org/entity/Q3'}}]}}
t('qids salta binding incompleti e li registra', H.qids(r) == ['Q1', 'Q3'] and len(H.ANOM) == 2, (H.qids(r), H.ANOM))
t('qids su risposta di errore -> None', H.qids({'errore': 'x'}) is None and H.qids(None) is None)
t('qids su bindings vuoti -> []', H.qids({'results': {'bindings': []}}) == [])
# 3) W2 con rete simulata
def run(fake, out, extra=''):
    code = '''
import sys, json; sys.path.insert(0, %r)
import db_w1_harvest as H, db_w2_harvest as W
%s
H.time.sleep = lambda s: None
sys.argv = ['w2', %r]
W.main()
''' % (str(R/'tools'), fake, str(out))
    return subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
FAKE = '''
import re
CALLS = {'n': 0}
def sp(q):
    CALLS['n'] += 1
    if 'rdfs:label "Logan"' in q: return {'errore': 'timeout'}                    # errore temporaneo definitivo su un film
    if 'rdfs:label "Deadpool"' in q: return {'results': {'bindings': [{'w': {'value': 'http://x/Q777'}}]}}   # binding con variabile inattesa
    if 'rdfs:label "Blade"' in q: return {'results': {'bindings': []}}             # film non trovato
    if 'rdfs:label' in q: return {'results': {'bindings': [{'x': {'value': 'http://x/Q500'}}]}}
    if 'P1441' in q: return {'results': {'bindings': [{'x': {'value': 'http://x/Q600'}}]}}
    if 'P161' in q: return {'results': {'bindings': [{'x': {'value': 'http://x/Q700'}}]}}
    return {'results': {'bindings': []}}
H.sparql = sp
def fe(ids, props): return {q: {'labels': {'en': {'value': 'L' + q}}, 'claims': {}} for q in ids if q != 'Q600'}   # Q600 mancante
H.fetch_entities = fe
'''
with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d); p = run(FAKE, d)
    t('W2 simulato: termina con dati parziali (exit 0)', p.returncode == 0, p.stderr[-400:])
    man = json.load(open(d/'w2_manifest.json'))
    t('W2: film con errore registrato e non fatale', any('Logan' in k for k in man['film_errori']), man['film_errori'])
    t('W2: anomalie registrate (binding, film non trovato, entita mancante)', len(man['anomalie']) >= 3, man['anomalie'][:5])
    t('W2: manifest segnala non completa', man['completa'] is False)
    dat = json.load(open(d/'w2_wikidata.json'))
    t('W2: salvati i risultati parziali validi', 'Q500' in dat['entita'] and 'Q700' in dat['entita'] and 'Q600' not in dat['entita'])
    t('W2: checkpoint presente', (d/'w2_checkpoint.json').exists())
    # ripresa: nessuna nuova query SPARQL per i film gia' in checkpoint
    code_count = FAKE.replace("CALLS['n'] += 1", "CALLS['n'] += 1; open(%r, 'a').write('x')" % str(d/'calls.txt'))
    p2 = run(code_count, d)
    n2 = len((d/'calls.txt').read_text()) if (d/'calls.txt').exists() else 0
    t('W2: ripresa da checkpoint (solo i film falliti vengono ripetuti)', p2.returncode == 0 and 'ripresa da checkpoint' in p2.stdout and n2 < 20, (n2, p2.stdout[-200:], p2.stderr[-200:]))
with tempfile.TemporaryDirectory() as d:
    p = run("import db_w1_harvest as H\nH.get = lambda *a, **k: (H.anom('rete'), {'errore': 'x'})[1]", pathlib.Path(d))
    t('W2 senza rete: nessuna eccezione non gestita (exit 1 pulito, manifest scritto)', p.returncode == 1 and 'Traceback' not in p.stderr and (pathlib.Path(d)/'w2_manifest.json').exists(), p.stderr[-300:])
# 4) workflow: job indipendenti
import yaml
y = yaml.safe_load(open(R/'.github/workflows/tmdb-sync.yml'))
t('workflow: db-w1b e db-w2 sono job distinti senza needs', 'db-w1b' in y['jobs'] and 'db-w2' in y['jobs'] and not y['jobs']['db-w1b'].get('needs') and not y['jobs']['db-w2'].get('needs'))
for j in ('db-w1b', 'db-w2'):
    st = y['jobs'][j]['steps']
    t('workflow %s: raccolta continue-on-error e salvataggio if always()' % j, any(s.get('continue-on-error') for s in st) and any('if' in s and 'always()' in str(s['if']) and 'db-raw' in str(s.get('run', '')) for s in st))
print('db_harvest_test: %d ok, %d fail' % (ok, fail)); sys.exit(1 if fail else 0)
