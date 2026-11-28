#!/usr/bin/env python3
"""W8: regole di verifica (D12) e coerenza dei dati. Uso: python3 tests/db_w8_test.py"""
import json, sys, subprocess, pathlib, collections, re
R = pathlib.Path(__file__).resolve().parent.parent; E = R / 'data/atlante/espansione'
sys.path.insert(0, str(R / 'tools'))
ok = fail = 0
def chk(c, m):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print('FAIL', m)
import db_w8_build as B
chk(B.serie('[[Ultimate Spider-Man]] #1 (2000)') == 'ultimate spider man', 'serie: estrae la testata dalla prima apparizione')
chk(B.base('Kree (Earth-616)') == 'Kree' and B.norm('Étoile  d\'Or!') == 'etoile d or', 'normalizzazione nomi')
rows = [json.loads(l) for l in (E / 'canon/w8_narrativo.jsonl').read_text().splitlines() if l.strip()] if (E / 'canon/w8_narrativo.jsonl').exists() else []
chk(len(rows) > 0, 'canon W8 presente')
chk(len({r['id'] for r in rows}) == len(rows), 'ID W8 unici')
chk(all(len(r['fonti']) >= 2 for r in rows), 'ogni voce W8 ha almeno DUE fonti (D12)')
chk(all(('wikidata' in r['ids_esterni']) or any('Comic Vine' in f['fonte'] for f in r['fonti']) for r in rows), 'seconda fonte = Wikidata o Comic Vine (mai la sola citazione della prima apparizione)')
chk(all(r['stato_verifica'] == 'verificata' and r['origine'] == 'W8' for r in rows), 'W8: solo voci verificate')
stg = [json.loads(l) for l in (E / 'staging/w8_staging.jsonl').read_text().splitlines() if l.strip()] if (E / 'staging/w8_staging.jsonl').exists() else []
chk(all('una sola fonte' in s['motivo'] for s in stg), 'staging W8: motivo documentato')
nomi_stg = {(s['tipo'], s['nome']) for s in stg}; chk(not any((r['tipo'], r['nome']) in nomi_stg for r in rows), 'nessuna voce contemporaneamente in canon e staging')
chk(subprocess.run(['python3', 'tools/db_canon.py'], cwd=R, capture_output=True).returncode == 0, 'schema canonico valido (tutti i canon)')
chk(subprocess.run(['python3', 'tools/db_ids.py', '--verifica'], cwd=R, capture_output=True).returncode == 0, 'registro ID append-only coerente')
rel = json.load(open(E / 'relazioni_db.json'))['relazioni']
chk(all(x.get('metodo') for x in rel), 'ogni relazione dichiara il metodo di verifica (automatica vs nessuna)')
chk(all(x['verifica'] != 'verificata' or x['metodo'].startswith('automatica') for x in rel), 'nessuna verifica automatica presentata come documentale')
chk(not any(x['classe'] == 'narrativa' and x['tipo'] == 'controparte' for x in rel), 'controparti separate dalle relazioni narrative')
chk(all(x['classe'] != 'narrativa' or x['tipo'] != 'controparte' for x in rel), 'classe/tipo coerenti')
liv = json.load(open(E / 'livelli_w8.json'))['livelli']; dz = json.load(open(E / 'dossier_it.json'))
chk(all(i in dz and dz[i]['q']['sezioni'] >= 4 for i in liv), 'ogni promozione A/B ha un dossier con almeno 4 sezioni')
chk(all(liv[i] != 'A' or (dz[i]['q']['sezioni'] >= 6 and dz[i]['q']['caratteri'] >= 900 and dz[i]['q']['campi'] >= 10) for i in liv), 'soglie del Livello A rispettate')
chk(all('base:' in ' '.join(r['gruppi']) for r in rows if r['tipo'] == 'variante'), 'ogni variante dichiara la base (controparte)')
print('db_w8_test: %d ok, %d fail' % (ok, fail)); sys.exit(1 if fail else 0)
