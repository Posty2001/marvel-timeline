#!/usr/bin/env python3
"""Valida il catalogo ritratti del Draft. Uso: python3 valida_ritratti.py <cartella assets/draft_portraits> [roster_ids.json]
Regole: ogni file immagine presente DEVE avere una voce approved completa; ogni voce approved DEVE avere file esistente con sha256 corrispondente;
nessun campo di provenienza vuoto; nessun percorso fuori cartella. Exit 1 se qualcosa non va."""
import sys, json, hashlib, re, pathlib
d = pathlib.Path(sys.argv[1]); m = json.loads((d / 'manifest.json').read_text())
req = m['required_for_approval']; err = []
ids = set(json.loads(open(sys.argv[2]).read())) if len(sys.argv) > 2 else None
if m.get('schema') != 1: err.append('schema non supportato')
if ids is not None and set(m['portraits']) != ids: err.append('le voci del catalogo non coincidono col roster (mancano %s, extra %s)' % (sorted(ids - set(m['portraits'])), sorted(set(m['portraits']) - ids)))
files = {p.name for p in d.iterdir() if p.suffix.lower() in ('.webp', '.png', '.jpg', '.jpeg')}
listed = set()
for pid, e in m['portraits'].items():
    st = e.get('status')
    if st not in m['allowed_status']: err.append('%s: status non valido %r' % (pid, st)); continue
    if st == 'test_stylized':
        miss = [k for k in ('file', 'license', 'sha256', 'asset_type') if e.get(k) in (None, '', False)]
        if miss: err.append('%s: test_stylized ma campi mancanti %s' % (pid, miss)); continue
        if e.get('rights_confirmed'): err.append('%s: test_stylized non può dichiarare rights_confirmed' % pid)
        f = d / e['file']
        if not re.fullmatch(r'[\w\-]+\.(webp|png|jpe?g)', e['file']) or not f.exists(): err.append('%s: file non valido/mancante' % pid); continue
        if hashlib.sha256(f.read_bytes()).hexdigest() != e['sha256']: err.append('%s: sha256 non corrisponde' % pid)
        listed.add(e['file'])
    elif st == 'approved':
        miss = [k for k in req if e.get(k) in (None, '', False)]
        if miss: err.append('%s: approved ma campi mancanti %s' % (pid, miss)); continue
        if not re.fullmatch(r'[\w\-]+\.(webp|png|jpe?g)', e['file']): err.append('%s: nome file non valido' % pid); continue
        f = d / e['file']
        if not f.exists(): err.append('%s: file mancante %s' % (pid, e['file'])); continue
        if hashlib.sha256(f.read_bytes()).hexdigest() != e['sha256']: err.append('%s: sha256 non corrisponde' % pid)
        listed.add(e['file'])
    elif e.get('file'): err.append('%s: file valorizzato ma status=%s (verrebbe ignorato)' % (pid, st))
for extra in sorted(files - listed): err.append('file non catalogato/non approvato nella cartella: %s' % extra)
n = sum(1 for e in m['portraits'].values() if e['status'] == 'approved')
print('voci %d · approvate %d · test_stylized %d · mancanti %d' % (len(m['portraits']), n, sum(1 for e in m['portraits'].values() if e['status'] == 'test_stylized'), sum(1 for e in m['portraits'].values() if e['status'] == 'missing')))
for e in err: print('ERRORE', e)
sys.exit(1 if err else 0)
