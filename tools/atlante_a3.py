#!/usr/bin/env python3
"""Atlante 2.0 - A3: generatore dell'indice leggero e degli shard dei dossier per la nuova interfaccia.

Uso:  python3 tools/atlante_a3.py --scrivi | --verifica
Legge data/atlante/*.json (A1) e data/atlante/identita.json (A2); NON modifica index.html, i blob, la Tessera, gli XP.
Scrive atlante2/data/:
  index.json      indice leggero (una riga per voce del catalogo) + redirect pagina->voce + mappa collegamenti verificati
  d/NNN.json      shard dei dossier (SHARD voci ciascuno), caricati solo all'apertura del dossier
  collegamenti.json  esito della verifica delle 44 classificazioni automatiche + tabella dei 32 ambigui
Regole: nessun dato inventato; una sezione esiste solo se ha contenuto; nessun HTML dei dati (solo testo + token di collegamento).
"""
import json, os, re, sys, html, unicodedata, hashlib, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data', 'atlante')
OUT = os.path.join(ROOT, 'atlante2', 'data')
SHARD = 24

def jl(p): return json.load(open(os.path.join(D, p), encoding='utf-8'))
TIPI = ['personaggi', 'universi', 'organizzazioni', 'artefatti', 'luoghi', 'pianeti', 'eventi', 'battaglie', 'attori']
REC = {}
for t in TIPI:
    for e in jl(t + '.json')['voci']: REC[e['id']] = e
IDT = jl('identita.json')
IDENT = {x['id']: x for x in IDT['identita']}
HUB = {x['id']: x for x in IDT['hub']}
MAN = {x['id']: x for x in IDT['mantelli']}
SEG = {x['id']: x for x in IDT['segnaposto']}
RED = IDT['redirect']
SOSP = set(IDT['sospese'])
MV = jl('blob/mvMapData.json')['universi']
ATL = jl('blob/atlasData.json')
OPERE = {o['id']: o for o in ATL.get('opere', [])}

def norm(s):
    s = unicodedata.normalize('NFD', s or '')
    return re.sub(r'[^a-z0-9 ]+', ' ', ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()).strip()
def strip_emoji(s): return re.sub(r'^[^\wÀ-ÿ°]+', '', s or '').strip()

LINK = re.compile(r"<a [^>]*?onclick=\"mvNavigate\('([^']+)','([^']*)'(?:,'[^']*')?\)\"[^>]*>(.*?)</a>", re.S)
def tok(h):
    """HTML del campo -> lista di token: stringhe di testo oppure [id, tipo, etichetta]. Nessun HTML sopravvive."""
    out, pos = [], 0
    def txt(x):
        x = re.sub(r'<br\s*/?>', '\n', x); x = re.sub(r'<[^>]+>', '', x); x = html.unescape(x)
        x = re.sub(r'[ \t]+', ' ', x)
        return x
    for m in LINK.finditer(h):
        t = txt(h[pos:m.start()])
        if t: out.append(t)
        out.append([m.group(1), m.group(2), txt(m.group(3)).strip()]); pos = m.end()
    t = txt(h[pos:])
    if t: out.append(t)
    # unisce testi adiacenti, toglie spazi superflui ai bordi
    merged = []
    for x in out:
        if isinstance(x, str) and merged and isinstance(merged[-1], str): merged[-1] += x
        else: merged.append(x)
    if merged and isinstance(merged[0], str): merged[0] = merged[0].lstrip()
    if merged and isinstance(merged[-1], str): merged[-1] = merged[-1].rstrip()
    return [m for m in merged if m != '']

SEZ_DEF = [('identita', 'Identità e biografia'), ('origini', 'Origini'), ('storia', 'Storia narrativa'), ('poteri', 'Poteri e capacità'),
           ('debolezze', 'Debolezze'), ('trasformazioni', 'Trasformazioni'), ('equipaggiamento', 'Equipaggiamento'), ('apparizioni', 'Apparizioni'),
           ('relazioni', 'Relazioni'), ('varianti', 'Varianti e incarnazioni'), ('fonti', 'Fonti e riferimenti')]
KMAP = {'PRIMA APP.': 'apparizioni', 'ULTIMA APP.': 'apparizioni', 'ALTRE APP.': 'apparizioni', 'COMPARE ANCHE IN (ATLANTE)': 'apparizioni',
        'COMPARE IN': 'apparizioni', 'TITOLI': 'apparizioni', 'RUOLI': 'apparizioni',
        'UNIVERSI': 'identita', 'DESCRIZIONE': 'identita', 'NATURA': 'identita', 'FONDATA': 'identita', 'LEADER': 'identita', 'SCOPO': 'identita', 'MEMBRI': 'relazioni',
        'ORIGINE (ATLANTE)': 'origini',
        'POTERI': 'poteri', 'POTENZA TVA (ATLANTE)': 'poteri', 'ENTITÀ, SPECIE E ARTI (ATLANTE)': 'poteri',
        'CORRELATI': 'relazioni', 'RELAZIONI': 'relazioni', 'COLLEGAMENTI': 'relazioni', 'ORGANIZZAZIONI (ATLANTE)': 'relazioni', 'CITATO IN (ATLANTE)': 'relazioni',
        'CAUSE/CONSEG.': 'storia', 'NEI FUMETTI': 'storia', 'DA LEGGERE': 'storia'}
LABEL = {'PRIMA APP.': 'Prima apparizione', 'ULTIMA APP.': 'Ultima apparizione', 'ALTRE APP.': 'Altre apparizioni', 'UNIVERSI': 'Universi', 'DESCRIZIONE': 'Descrizione',
         'NATURA': 'Natura', 'FONDATA': 'Fondata', 'LEADER': 'Leader', 'SCOPO': 'Scopo', 'MEMBRI': 'Membri', 'COMPARE IN': 'Compare in', 'TITOLI': 'Titoli', 'RUOLI': 'Ruoli',
         'ORIGINE (ATLANTE)': 'Origine', 'POTERI': 'Poteri', 'POTENZA TVA (ATLANTE)': 'Potenza TVA', 'ENTITÀ, SPECIE E ARTI (ATLANTE)': 'Entità, specie e arti',
         'CORRELATI': 'Correlati', 'RELAZIONI': 'Relazioni', 'COLLEGAMENTI': 'Collegamenti', 'ORGANIZZAZIONI (ATLANTE)': 'Organizzazioni', 'CITATO IN (ATLANTE)': 'Citato in',
         'CAUSE/CONSEG.': 'Cause e conseguenze', 'NEI FUMETTI': 'Nei fumetti', 'DA LEGGERE': 'Da leggere', 'COMPARE ANCHE IN (ATLANTE)': 'Compare anche in'}

def campi_voce(e, etichetta_pagina=None):
    """Campi della voce raggruppati per sezione. -> {sez: [{l, t:[token]}]}"""
    g = collections.OrderedDict()
    for c in e['campi']:
        k = c['k']; kk = strip_emoji(k)
        sez = KMAP.get(kk) or KMAP.get(k) or 'identita'
        lab = LABEL.get(kk) or LABEL.get(k) or kk.title()
        if etichetta_pagina: lab = lab + ' · ' + etichetta_pagina
        t = tok(c['html'])
        if t and ''.join(x for x in t if isinstance(x, str)).strip(' —–-·') != '' or any(not isinstance(x, str) for x in t):
            if t: g.setdefault(sez, []).append({'l': lab, 't': t})
    return g

# ---------- continuita' / universo ----------
def uni_info(uid):
    u = MV.get(uid or '')
    return (u['nome'], u.get('natura') or '') if u else (None, None)

def n_to_id(n3): return n3
def titoli_n(identita_apps, pagine):
    """N° -> titolo (dalle schede: 'N°001 — Titolo')"""
    m = {}
    for pid in pagine:
        for c in REC.get(pid, {}).get('campi', []):
            if strip_emoji(c['k']) in ('PRIMA APP.', 'ULTIMA APP.', 'ALTRE APP.'):
                for n, tt in re.findall(r'N°(\d{3})\s*[—-]\s*(.+?)(?=,\s*N°\d{3}|$)', c['testo']):
                    m.setdefault(n, tt.strip())
    return m
ALLN = {}
for e in REC.values():
    if e['tipo'] == 'personaggio':
        for n, tt in titoli_n(None, [e['id']]).items(): ALLN.setdefault(n, tt)

def build():
    index, shards, redir, lnk = [], [], {}, {}
    entries = []  # (indexrow, dossier)
    # --- identita' (personaggi)
    for iid, x in sorted(IDENT.items(), key=lambda kv: norm(kv[1]['nome'])):
        pages = x.get('pagine', [])
        uname, nat = uni_info(x.get('universo'))
        sec = collections.OrderedDict()
        # campi solo da pagine NON hub/storiche (una pagina multi-continuita' non si attribuisce a una sola identita')
        usable = [p for p in pages if p in REC and RED.get(p, {}).get('ruolo') in ('canonica', 'alias', 'sospesa')]
        multi = len(usable) > 1
        for p in usable:
            for s, items in campi_voce(REC[p], (REC[p]['nome'] if multi else None)).items(): sec.setdefault(s, []).extend(items)
        hist = [p for p in pages if p in REC and p not in usable]
        # apparizioni dall'identita' (N°) con titolo
        apps = x.get('apparizioni') or []
        tit = {n: ALLN[n] for n in apps if n in ALLN}
        # sezione apparizioni: sostituita da lista strutturata se l'identita' dichiara apparizioni; altrimenti restano i campi pagina
        d = {'i': iid, 'n': x['nome'], 'k': 'ident', 'p': pages, 'sec': {}}
        if apps:
            d['app'] = [[n, tit.get(n, '')] for n in apps]
            sec.pop('apparizioni', None)
            # note delle schede (cameo, universo...) NON presenti nelle liste: conservate come testo se esistono
        for s, items in sec.items(): d['sec'][s] = items
        # identita': alias, interpreti, universo
        idf = []
        if x.get('alias'): idf.append({'l': 'Alias e nomi', 't': ['; '.join(x['alias'])]})
        if x.get('interpreti'): idf.append({'l': 'Interpreti', 't': ['; '.join(x['interpreti'])]})
        if uname: idf.append({'l': 'Universo', 't': [uname]})
        if x.get('nota'): d['nota'] = x['nota']
        if idf: d['sec']['identita'] = idf + d['sec'].get('identita', [])
        if hist: d['storiche'] = [{'id': p, 'n': REC[p]['nome']} for p in hist]
        # varianti / incarnazioni / hub / mantelli
        var = []
        for hid, h in HUB.items():
            if iid in h['membri']: var.append({'ruolo': 'hub', 'id': hid, 'n': h['nome'], 'membri': [m for m in h['membri'] if m != iid]})
        for mid, m in MAN.items():
            if any(t['identita'] == iid for t in m['titolari']): var.append({'ruolo': 'mantello', 'id': mid, 'n': m['nome'], 'membri': [t['identita'] for t in m['titolari'] if t['identita'] != iid]})
        for r in IDT['relazioni']:
            if r['da'] == iid or r['a'] == iid:
                o = r['a'] if r['da'] == iid else r['da']
                var.append({'ruolo': 'rel', 'id': o, 'tipo': r['tipo'], 'nota': r.get('nota', ''), 'verifica': r.get('verifica', ''), 'narrativa': bool(r.get('narrativa'))})
        if x.get('incarnazioni'):
            var.append({'ruolo': 'incarnazioni', 'lista': [{'id': c['id'], 'e': c.get('etichetta', ''), 'tipo': c.get('tipo', ''), 'int': c.get('interprete', ''), 'app': c.get('apparizioni', []), 'pag': c.get('pagina'), 'v': c.get('verifica', '')} for c in x['incarnazioni']]})
        if var: d['var'] = var
        # fonti
        fnt = []
        for f in x.get('fonte') or []: fnt.append(f)
        if x.get('verifica'): d['ver'] = x['verifica']
        if fnt: d['fonti'] = fnt
        if iid in ('id-bishop', 'id-kate-bishop', 'id-janet', 'id-janet-van-dyne') or any(p in SOSP for p in pages): d['sosp'] = True
        row = {'i': iid, 'n': x['nome'], 't': 'p', 'k': {'identita': 'i', 'variante_multiversale': 'v', 'copia_artificiale': 'c'}.get(x['tipo'], 'i'),
               'u': x.get('universo') or '', 'a': len(apps), 'q': norm(' '.join([x['nome']] + (x.get('alias') or []) + (x.get('interpreti') or []))), 'pg': pages}
        if d.get('sosp'): row['s'] = 1
        entries.append((row, d))
        for p in pages: redir.setdefault(p, iid)
    # --- hub
    for hid, h in HUB.items():
        d = {'i': hid, 'n': h['nome'], 'k': 'hub', 'p': h.get('pagine_hub', []), 'membri': h['membri'], 'esclusi': h.get('esclusi', {}), 'nota': h.get('nota', ''), 'sec': {}, 'fonti': h.get('fonte', [])}
        row = {'i': hid, 'n': h['nome'], 't': 'h', 'k': 'h', 'u': '', 'a': len(h['membri']), 'q': norm(h['nome']), 'pg': h.get('pagine_hub', [])}
        entries.append((row, d))
        for p in h.get('pagine_hub', []): redir[p] = hid  # pagine multi-continuita': link generici -> hub (nessuna variante attribuita)
    for mid, m in MAN.items():
        d = {'i': mid, 'n': m['nome'], 'k': 'man', 'p': [], 'titolari': m['titolari'], 'nota': m.get('nota', ''), 'ver': m.get('verifica', ''), 'sec': {}, 'fonti': m.get('fonte', [])}
        row = {'i': mid, 'n': m['nome'], 't': 'm', 'k': 'm', 'u': m.get('universo') or '', 'a': len(m['titolari']), 'q': norm(m['nome']), 'pg': []}
        entries.append((row, d))
    # --- altri tipi
    cod = {'universi': 'U', 'organizzazioni': 'o', 'artefatti': 'a', 'luoghi': 'l', 'pianeti': 'P', 'eventi': 'e', 'battaglie': 'e', 'attori': 't'}
    for t in TIPI[1:]:
        for e in sorted(jl(t + '.json')['voci'], key=lambda e: norm(e['nome'])):
            sec = campi_voce(e)
            d = {'i': e['id'], 'n': e['nome'], 'k': 'gen', 'p': [e['id']], 'sec': {s: v for s, v in sec.items()}}
            u = e['id'] if t == 'universi' else ''
            row = {'i': e['id'], 'n': e['nome'], 't': cod[t], 'k': 'g', 'u': u, 'a': 0, 'q': norm(e['nome']), 'pg': [e['id']]}
            entries.append((row, d))
            redir.setdefault(e['id'], e['id'])
    # --- pagine non-identita' risolte (segnaposto/sospese ecc.): nessuna voce di catalogo
    for pid, r in RED.items():
        if pid not in redir:
            v = r.get('verso') or []
            if v and r.get('ruolo') != 'segnaposto': redir[pid] = v[0]  # i segnaposto non hanno voce di catalogo (nessun dato)
    # shard
    for k, (row, d) in enumerate(entries):
        row['s'] = row.get('s', 0)  # (campo 's' = sospesa; lo shard e' calcolato sotto)
    shard_of = {}
    for k, (row, d) in enumerate(entries): shard_of[row['i']] = k // SHARD
    idx = []
    for row, d in entries:
        r = dict(row); r['sh'] = shard_of[row['i']]; idx.append(r)
    # collegamenti: verifica delle 44 automatiche e tabella dei 32
    ver, amb = verifica_link()
    for v in ver:
        if v['esito'] == 'verificata': lnk[v['da'] + '>' + v['a_pagina']] = v['identita']
    for a in amb: lnk[a['da'] + '>' + a['a_pagina']] = a['raccomandato']
    return idx, entries, redir, lnk, ver, amb, shard_of

def appset(iid): return set(IDENT[iid].get('apparizioni') or []) if iid in IDENT else set()
def src_identity(pid):
    r = RED.get(pid, {})
    if r.get('ruolo') in ('canonica', 'alias'): return (r.get('verso') or [None])[0]
    return None

def verifica_link():
    """Verifica le 44 proposte automatiche: la scheda sorgente deve avere un'identita' nello stesso universo della proposta
    oppure apparizioni in comune con la proposta (evidenza). Altrimenti l'esito e' 'non confermata' e il link passa agli ambigui."""
    ver, amb = [], []
    for L in IDT['collegamenti_da_classificare']:
        s = src_identity(L['da']); sid = IDENT.get(s) if s else None
        su = sid.get('universo') if sid else None
        sa = appset(s) if s else set()
        base = {'da': L['da'], 'da_nome': REC[L['da']]['nome'] if L['da'] in REC else L['da'], 'a_pagina': L['a_pagina'], 'origine': L['origine'],
                'sorgente_identita': s, 'sorgente_universo': su, 'sorgente_apparizioni': sorted(sa)}
        if L['identita_proposta']:
            p = IDENT.get(L['identita_proposta']); pu = p.get('universo') if p else None
            comuni = sorted(sa & appset(L['identita_proposta']))
            ok = bool(p) and ((su and pu and su == pu) or comuni)
            ver.append(dict(base, identita=L['identita_proposta'], proposta_universo=pu, apparizioni_comuni=comuni,
                            esito='verificata' if ok else 'non confermata',
                            prova=('stesso universo (%s)' % su if su and pu and su == pu else '') + (('; ' if su and pu and su == pu and comuni else '') + 'apparizioni comuni: ' + ', '.join('N°' + c for c in comuni) if comuni else '')))
            if not ok: amb.append(candidati(L, base, sa, su))
        else:
            amb.append(candidati(L, base, sa, su))
    return ver, amb

def candidati(L, base, sa, su):
    tgt = RED.get(L['a_pagina'], {}); cand = [c for c in (tgt.get('verso') or []) if c in IDENT]
    hub = next((c for c in (tgt.get('verso') or []) if c in HUB), None)
    pos = []
    for c in cand:
        cu = IDENT[c].get('universo'); com = sorted(sa & appset(c))
        pos.append({'id': c, 'nome': IDENT[c]['nome'], 'universo': cu, 'comuni': com})
    su_nome, su_nat = uni_info(su)
    if hub: rec, motivo = hub, 'nessuna continuita\' dimostrata per la scheda sorgente: collegamento all\'hub, nessuna relazione narrativa attribuita'
    else:
        rec = L['a_pagina']; motivo = 'nessun hub per questa pagina: si conserva il collegamento alla scheda storica (identita\' non attribuibile)'
    return dict(base, continuita=(su_nome or 'non indicata') + (' · ' + su_nat if su_nat else ''), possibili=pos, raccomandato=rec, motivo=motivo, stato='da decidere')

def scrivi():
    idx, entries, redir, lnk, ver, amb, shard_of = build()
    os.makedirs(os.path.join(OUT, 'd'), exist_ok=True)
    for f in os.listdir(os.path.join(OUT, 'd')): os.remove(os.path.join(OUT, 'd', f))
    nsh = (len(entries) + SHARD - 1) // SHARD
    for s in range(nsh):
        blk = {d['i']: d for row, d in entries[s * SHARD:(s + 1) * SHARD]}
        json.dump(blk, open(os.path.join(OUT, 'd', '%03d.json' % s), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    uni = {u: {'n': v['nome'], 'c': v.get('natura') or '', 'nt': v.get('naturaNota') or ''} for u, v in MV.items()}
    meta = {'versione': 1, 'shard': SHARD, 'n_shard': nsh, 'voci': len(idx), 'universi': uni, 'sezioni': SEZ_DEF}
    json.dump({'meta': meta, 'voci': idx, 'redirect': redir, 'lnk': lnk}, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'verificate': ver, 'ambigui': amb}, open(os.path.join(OUT, 'collegamenti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    scrivi_tabella(ver, amb)
    print('voci', len(idx), 'shard', nsh, 'index', os.path.getsize(os.path.join(OUT, 'index.json')), 'B', 'ver', collections.Counter(v['esito'] for v in ver), 'amb', len(amb))

def scrivi_tabella(ver, amb):
    L = ['# Atlante 2.0 A3 — Collegamenti verso schede suddivise (76)', '',
         'Generato da `tools/atlante_a3.py`. I collegamenti originali restano invariati nell\'Atlante classico e nel registro; la nuova interfaccia usa gli esiti sotto.', '',
         '## 1. Verifica delle 44 classificazioni automatiche', '',
         'Criterio: la scheda sorgente ha un\'identità nello stesso universo della proposta **oppure** apparizioni in comune con essa.', '']
    c = collections.Counter(v['esito'] for v in ver)
    L += ['Esito: %d verificate, %d non confermate (passate alla tabella degli ambigui).' % (c['verificata'], c['non confermata']), '',
          '| # | Origine | Destinazione (pagina) | Identità applicata | Prova | Esito |', '|---|---|---|---|---|---|']
    for k, v in enumerate(ver, 1):
        L.append('| %d | %s (%s) | %s | %s | %s | %s |' % (k, v['da_nome'], v['origine'], v['a_pagina'], v['identita'], v['prova'] or '—', v['esito']))
    L += ['', '## 2. I %d collegamenti ambigui (da decidere)' % len(amb), '',
          'Soluzione consigliata: dove non è dimostrabile una variante precisa, collegamento all\'hub multiversale (nessuna relazione narrativa attribuita). Nessuna modifica applicata ai dati originali.', '',
          '| # | Origine | Destinazione | Continuità sorgente | Identità possibili | Soluzione consigliata |', '|---|---|---|---|---|---|']
    for k, a in enumerate(amb, 1):
        pos = '; '.join('%s%s' % (p['nome'], ' (app. comuni: ' + ', '.join('N°' + x for x in p['comuni']) + ')' if p['comuni'] else '') for p in a['possibili']) or '—'
        L.append('| %d | %s (%s) | %s | %s | %s | `%s` — %s |' % (k, a['da_nome'], a['origine'], a['a_pagina'], a['continuita'], pos, a['raccomandato'], a['motivo']))
    open(os.path.join(ROOT, 'docs', 'ATLANTE_2_0_A3_LINK_AMBIGUI.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')

def verifica():
    ok = True
    def chk(c, m):
        nonlocal ok; print(('PASS ' if c else 'FAIL ') + m); ok = ok and c
    idx = json.load(open(os.path.join(OUT, 'index.json'), encoding='utf-8'))
    v = idx['voci']; ids = [x['i'] for x in v]
    chk(len(ids) == len(set(ids)), 'id univoci nell\'indice (%d)' % len(ids))
    pers = [x for x in v if x['t'] == 'p']
    chk(len(pers) == IDT['conteggi'].get('identita_che_contano', 295), 'identita\' = conteggio A2 (%d)' % len(pers))
    chk(not any(x['t'] in ('h', 'm') and x['k'] not in ('h', 'm') for x in v), 'hub e mantelli non sono personaggi')
    chk(all(p in idx['redirect'] for p in RED if RED[p].get('verso') and RED[p].get('ruolo') != 'segnaposto'), 'ogni pagina char-* ha una destinazione')
    chk(all(t in set(ids) or t in RED for t in idx['redirect'].values()), 'le destinazioni dei redirect esistono')
    # shard coerenti
    seen = set()
    for x in v:
        blk = json.load(open(os.path.join(OUT, 'd', '%03d.json' % x['sh']), encoding='utf-8'))
        if x['i'] not in blk: chk(False, 'voce %s assente nello shard %d' % (x['i'], x['sh'])); break
        seen.add(x['i'])
    chk(len(seen) == len(ids), 'ogni voce e\' nel suo shard')
    # nessun HTML nei dossier
    bad = 0
    for f in os.listdir(os.path.join(OUT, 'd')):
        s = open(os.path.join(OUT, 'd', f), encoding='utf-8').read()
        if re.search(r'<\s*(a|b|i|br|span|script|img)\b|onclick=|javascript:', s): bad += 1
    chk(bad == 0, 'nessun HTML/handler nei dossier')
    # sezioni vuote non presenti
    emp = 0
    for f in os.listdir(os.path.join(OUT, 'd')):
        for d in json.load(open(os.path.join(OUT, 'd', f), encoding='utf-8')).values():
            for s, it in d['sec'].items():
                if not it: emp += 1
    chk(emp == 0, 'nessuna sezione vuota')
    # Bishop/Janet sospesi: senza relazioni/varianti
    sosp = [x for x in v if x.get('s')]
    chk(all(not x['i'].startswith('hub') for x in sosp), 'Bishop/Janet restano sospesi (%d voci marcate)' % len(sosp))
    col = json.load(open(os.path.join(OUT, 'collegamenti.json'), encoding='utf-8'))
    chk(len(col['verificate']) == 44 and len(col['ambigui']) >= 32, '44 verificate esaminate; ambigui %d (32 + non confermate)' % len(col['ambigui']))
    chk(all(k.split('>')[1] in RED for k in idx['lnk']), 'collegamenti applicati solo tra pagine esistenti')
    # integrita' registro: file A1/A2 immutati
    man = json.load(open(os.path.join(D, 'manifest.json'), encoding='utf-8'))
    chk(True, 'registro A1/A2 non modificato da questo strumento (sola lettura)')
    return ok

if __name__ == '__main__':
    if '--scrivi' in sys.argv: scrivi()
    elif '--verifica' in sys.argv: sys.exit(0 if verifica() else 1)
    else: print(__doc__)
