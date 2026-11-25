#!/usr/bin/env python3
"""Atlante 2.0 - A1: estrazione del registro dati dall'index.html attuale (sola lettura).

Uso:
  python3 tools/atlante_estrai.py --scrivi        # (ri)genera data/atlante/*.json
  python3 tools/atlante_estrai.py --verifica      # test di round-trip + confronto con la baseline congelata
  python3 tools/atlante_estrai.py --baseline      # riscrive data/atlante/baseline_A0.json (solo se deliberato)

Non modifica index.html. Il registro e' un sorgente di migrazione: il runtime continua a usare l'HTML e i blob attuali
(strangler). Ogni scheda conserva id stabile, campi strutturati, collegamenti e l'HTML originale (fallback identico).
"""
import argparse, hashlib, json, os, re, sys
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'data', 'atlante')
TIPI = {  # prefisso id -> (file, tipo)
    'char': ('personaggi', 'personaggio'), 'uni': ('universi', 'universo'), 'org': ('organizzazioni', 'organizzazione'),
    'art': ('artefatti', 'artefatto'), 'luo': ('luoghi', 'luogo'), 'pia': ('pianeti', 'pianeta'),
    'evt': ('eventi', 'evento'), 'bat': ('battaglie', 'battaglia'), 'att': ('attori', 'attore'),
}
BLOB_ATLANTE = ['atlasData', 'relationshipGraphData', 'mvMapData', 'tesseraCharIdsData', 'tesseraCharPowersData',
                'tesseraCharLevelsData', 'altTimelineData', 'cmpActorData', 'tmdbMap']
NAV = re.compile(r"mvNavigate\('([^']+)','([^']+)'(?:,'([^']*)')?")

def leggi():
    return open(IDX, encoding='utf-8').read()

def blob(s, i):
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>' % re.escape(i), s, re.S)
    return m.group(1) if m else None

def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def sha(t):
    return hashlib.sha256(t.encode('utf-8')).hexdigest()

def estrai(s):
    soup = BeautifulSoup(s, 'lxml')
    reg = {f: [] for f, _ in TIPI.values()}
    for c in soup.select('li.card-wrap[id]'):
        p = c['id'].split('-')[0]
        if p not in TIPI:
            continue
        f, tipo = TIPI[p]
        t = c.select_one('.title')
        campi = []
        for r in c.select('.detail-row'):
            k, v = r.select_one('.detail-k'), r.select_one('.detail-v')
            if k and v:
                campi.append({'k': k.get_text(' ', strip=True), 'html': v.decode_contents(), 'testo': v.get_text(' ', strip=True)})
        collegamenti = []
        for a in c.select('[onclick]'):
            for m in NAV.finditer(a['onclick']):
                collegamenti.append({'a': m.group(1), 'tipo': m.group(2), 'lettera': m.group(3) or ''})
        reg[f].append({
            'id': c['id'], 'tipo': tipo, 'nome': t.get_text(' ', strip=True) if t else '',
            'ricerca': c.get('data-search', ''), 'campi': campi, 'collegamenti': collegamenti,
            'ha_fumetto': bool(c.select_one('.has-comic')), 'verifica': 'da_verificare', 'fonte': 'schede attuali di index.html',
            'html': str(c),
        })
    sezioni = [{'id': e['id'], 'html': str(e)} for e in soup.select('[id^="sec-"]') if re.match(r'sec-1[a-k]$', e['id'])]
    reg['sezioni_saghe'] = sezioni
    return reg

def misure(s, reg):
    ids = {e['id'] for f, L in reg.items() if f != 'sezioni_saghe' for e in L}
    blobs = {b: blob(s, b) for b in BLOB_ATLANTE}
    rotti = [(e['id'], l['a']) for f, L in reg.items() if f != 'sezioni_saghe' for e in L for l in e['collegamenti'] if l['a'] not in ids]
    return {
        'build': (re.search(r'name="tva-build" content="([^"]+)"', s[:20000]) or [None, None])[1],
        'conteggi': {f: len(L) for f, L in reg.items()},
        'link_mvNavigate': sum(len(e['collegamenti']) for f, L in reg.items() if f != 'sezioni_saghe' for e in L),
        'link_rotti': len(rotti),
        'ids_sha256': sha('\n'.join(sorted(ids))),
        'html_sha256': sha('\n'.join(e['html'] for f, L in sorted(reg.items()) for e in L if f != 'sezioni_saghe')),
        'blob': {b: (sha(canon(json.loads(t))) if t else None) for b, t in blobs.items()},
        'blob_raw_sha256': {b: (sha(t) if t else None) for b, t in blobs.items()},
    }

def scrivi(s, reg):
    os.makedirs(OUT, exist_ok=True)
    for f, L in reg.items():
        json.dump({'versione': 1, 'sorgente': 'index.html', 'voci': L}, open(os.path.join(OUT, f + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    bd = os.path.join(OUT, 'blob'); os.makedirs(bd, exist_ok=True)
    for b in BLOB_ATLANTE:
        t = blob(s, b)
        if t:
            open(os.path.join(bd, b + '.json'), 'w', encoding='utf-8').write(t)   # testo identico all'originale
    json.dump(misure(s, reg), open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def verifica():
    s = leggi(); ok = True
    def chk(n, c, d=''):
        nonlocal ok
        print(('PASS ' if c else 'FAIL ') + n + (' ' + str(d) if (d and not c) else '')); ok &= bool(c)
    reg = estrai(s); m = misure(s, reg)
    # 1) JSON su disco = estrazione corrente (nessuna deriva)
    for f, L in reg.items():
        p = os.path.join(OUT, f + '.json')
        d = json.load(open(p, encoding='utf-8'))['voci'] if os.path.exists(p) else None
        chk('registro %s identico all\'estrazione (%d voci)' % (f, len(L)), d == L)
    # 2) round-trip HTML: ogni scheda del registro compare identica in index.html e viceversa
    soup = BeautifulSoup(s, 'lxml'); orig = {c['id']: str(c) for c in soup.select('li.card-wrap[id]') if c['id'].split('-')[0] in TIPI}
    dal_reg = {e['id']: e['html'] for f, L in reg.items() if f != 'sezioni_saghe' for e in L}
    chk('round-trip HTML: stessi id (0 persi, 0 in piu)', set(orig) == set(dal_reg), set(orig) ^ set(dal_reg))
    chk('round-trip HTML: contenuto identico per ogni scheda', all(orig[i] == dal_reg[i] for i in orig))
    chk('id univoci', len(dal_reg) == sum(len(L) for f, L in reg.items() if f != 'sezioni_saghe'))
    # 3) blob: file su disco identici al testo originale, JSON valido
    for b in BLOB_ATLANTE:
        t = blob(s, b); p = os.path.join(OUT, 'blob', b + '.json')
        chk('blob %s identico (byte)' % b, t is not None and os.path.exists(p) and open(p, encoding='utf-8').read() == t)
    # 4) integrita' dati
    chk('0 link mvNavigate rotti', m['link_rotti'] == 0, m['link_rotti'])
    g = json.loads(blob(s, 'relationshipGraphData')); ids = set(dal_reg)
    chk('grafo: 0 archi verso nodi inesistenti', all(c['id'] in g for v in g.values() for c in v['conns']))
    ci = json.loads(blob(s, 'tesseraCharIdsData'))
    chk('Tessera: 0 id personaggio orfani', all((i in ids) for i in (ci if isinstance(ci, list) else ci.keys()) if str(i).startswith('char-')))
    # 5) baseline congelata A0
    bp = os.path.join(OUT, 'baseline_A0.json')
    if os.path.exists(bp):
        b = json.load(open(bp, encoding='utf-8'))
        for k in ('conteggi', 'link_mvNavigate', 'link_rotti', 'ids_sha256', 'html_sha256', 'blob'):
            chk('baseline A0: %s invariato' % k, b[k] == m[k], (b[k], m[k]) if k in ('conteggi', 'link_mvNavigate') else '')
    else:
        chk('baseline A0 presente', False)
    print('ESITO:', 'OK' if ok else 'FALLITO'); return 0 if ok else 1

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--scrivi', action='store_true'); ap.add_argument('--verifica', action='store_true'); ap.add_argument('--baseline', action='store_true')
    a = ap.parse_args(); s = leggi()
    if a.scrivi or a.baseline:
        reg = estrai(s); scrivi(s, reg); print('scritto', OUT, misure(s, reg)['conteggi'])
        if a.baseline:
            json.dump(misure(s, reg), open(os.path.join(OUT, 'baseline_A0.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('baseline A0 scritta')
    if a.verifica: sys.exit(verifica())
