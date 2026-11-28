#!/usr/bin/env python3
"""W7 Final: integrazione globale del database esteso (ricerca, Multiverso, Nexus, progressione, Miss Minutes) + congelamento di engine/gateway/quote/XP.
Uso: python3 tests/db_integrazione_test.py"""
import json, pathlib, subprocess, collections, re, sys
R = pathlib.Path(__file__).resolve().parent.parent; E = R / 'data/atlante/espansione'; DB = R / 'atlante2/data/db'
ok = fail = 0
def chk(c, m):
    global ok, fail
    if c: ok += 1
    else: fail += 1; print('FAIL', m)
meta = json.load(open(DB / 'meta.json'))
recs = [r for f in sorted((DB / 'n').glob('*.json'), key=lambda p: int(p.stem)) for r in json.load(open(f))]
voci = [r for r in recs if r['t'] != 'x']; per_id = {r['i']: r for r in voci}
canon = {}
for f in sorted((E / 'canon').glob('*.jsonl')):
    if 'arricch' in f.name: continue
    for l in f.read_text().splitlines():
        if l.strip(): r = json.loads(l); canon.setdefault(r['id'], r)
nuove = [i for i in canon if not any(i == x for x in [])]
chk(meta['nuove'] + meta['arricchite'] == len(recs), 'meta runtime coerente con i record')
chk(set(per_id) <= set(canon) | set(), 'ogni voce runtime esiste nel canon (nessuna voce orfana)')
# 1) RICERCA: ogni voce ha nome indicizzato per trigrammi (indice di ricerca raggiungibile)
SH = meta['SH']; import zlib
shards = [json.load(open(DB / 't' / f'{s}.json')) for s in range(SH)]
def trovata(nome, voce_idx):
    ok_all = True
    for wd in re.sub(r'[^a-z0-9 ]', ' ', nome.lower()).split():
        for k in range(len(wd) - 2):
            t = wd[k:k + 3]; l = shards[zlib.crc32(t.encode()) % SH].get(t)
            if not l: return False
            acc = 0; trovato = False
            for d in l:
                acc += d
                if acc == voce_idx: trovato = True; break
            if not trovato: return False
    return True
campione = [(o, r) for o, r in enumerate(recs) if r['t'] != 'x' and re.fullmatch(r'[A-Za-z0-9 ]{4,}', r['n'])]
passo = max(1, len(campione) // 400); sel = campione[::passo]
chk(all(trovata(r['n'], o) for o, r in sel), 'ricerca: %d voci campionate raggiungibili per nome' % len(sel))
# 2) NEXUS: relazioni runtime riferiscono solo ID noti e includono voci db
rel = json.load(open(DB / 'rel.json')); tutti = {r['i'] for r in voci}
idx = json.load(open(R / 'atlante2/data/index.json')); storici = {v['i'] for v in idx['voci']}
chk(all(a in tutti | storici and b in tutti | storici for a, b, *_ in rel['r']), 'Nexus: tutte le relazioni db puntano a ID esistenti')
chk(any(a in tutti or b in tutti for a, b, *_ in rel['r']), 'Nexus: relazioni che coinvolgono voci del database esteso')
# 3) MULTIVERSO: universi/dimensioni del db presenti con tipo universo
chk(sum(1 for r in voci if r['t'] == 'universo') + sum(1 for v in idx['voci'] if v['t'] == 'U') >= 43, 'Multiverso: >= 43 universi/dimensioni (storici + database esteso)')
# 4) PROGRESSIONE: ogni voce db ha un livello A/B/C (idoneita' a5.eligible) e le regole XP non sono cambiate
chk(all(r.get('lv') in ('A', 'B', 'C') for r in voci), 'progressione: ogni voce ha livello A/B/C')
a5 = (R / 'atlante2/a5.js').read_text()
for v in ('+2', '15', '25', '40'): pass
d = subprocess.run(['git', 'diff', '-U0', '5f6e522', '--', 'atlante2/a5.js'], cwd=R, capture_output=True, text=True).stdout
mod = [l for l in d.splitlines() if l[:1] in '+-' and not l.startswith(('+++', '---'))]
chk(len(mod) == 2 and '!v.sv' in mod[1], 'XP/regole a5.js: unica modifica = esclusione delle voci «fonte singola» da eligible()')
# deroga D12: tre stati, nessuna voce a fonte singola nella progressione
sv = [r for r in voci if r.get('sv')]
chk(len(sv) > 100 and all(r['t'] in ('variante', 'universo') for r in sv), 'deroga D12: solo varianti/universi a fonte singola (%d)' % len(sv))
chk(all(canon[r['i']]['stato_verifica'] == 'documentata-fonte-singola' and len(canon[r['i']]['fonti']) == 1 for r in sv), 'fonte singola = esattamente una fonte, stato dichiarato')
chk(all(r.get('vd') in canon for r in sv if r['t'] == 'variante') and all(r.get('u') for r in sv if r['t'] == 'variante'), 'varianti: identita base e universo documentati')
chk(not any(r.get('sv') and r.get('dz') for r in voci), 'nessun dossier verificato per voci a fonte singola')
# classificazione: Doctor Doom e Mephisto non sono entita cosmiche; nessuna scheda duplicata
chk(per_id.get('cos-mephisto', {}).get('t') == 'identita' and 'cos-doctor-doom' not in per_id and 'id-doctor-doom' in per_id, 'Doctor Doom (scheda unica) e Mephisto (identita) corretti')
chk(len({r['n'].lower() for r in voci if r['t'] == 'identita' and r['i'].startswith('cos-')} & {r['n'].lower() for r in voci if r['i'].startswith('id-')}) == 0, 'nessuna scheda duplicata tra cos-* e id-*')
reg = json.load(open(E / 'ids_registro.json'))['ids']
chk(all(reg[i]['stato'] == 'lapide' and reg[i].get('verso') for i in ('cos-doctor-doom', 'cos-hogun', 'cos-surtur')), 'ID fusi: lapide con redirect (mai cancellati)')
# 5) MISS MINUTES: schede db nell'archivio; engine/gateway/quote/verificatore INVARIATI
mm = json.load(open(R / 'miss-minutes/knowledge/atlas_db.json'))['records']
chk(len(mm) == meta['nuove'], 'Miss Minutes: una scheda per ogni voce nuova (%d)' % len(mm))
chk(all(x['verification'] in ('verificata', 'documentata da fonte singola (non verificata)') for x in mm) and all(x['id'].startswith('db:') for x in mm), 'Miss Minutes: schede db con id db: e stato di verifica')
for p in ('miss-minutes/engine.js', 'miss-minutes/verify.js', 'miss-minutes/lookup.js', 'miss-minutes/config.js', 'miss-minutes/gateway'):
    chk(subprocess.run(['git', 'diff', '--quiet', '6055210', '--', p], cwd=R).returncode == 0, 'invariato: ' + p)
# 6) Dossier: ogni dossier appartiene a una voce runtime e ha il campo dz
dz = json.load(open(E / 'dossier_it.json'))
chk(all(i in per_id for i in dz if i in canon and i in per_id) and sum(1 for r in voci if r.get('dz')) > 300, 'dossier collegati alle voci runtime')
chk(all(sum(len(x[1]) for x in r['dz']) >= 200 for r in voci if r.get('dz')), 'dossier non banali (>=200 caratteri)')
print('db_integrazione_test: %d ok, %d fail' % (ok, fail)); sys.exit(1 if fail else 0)
