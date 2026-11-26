#!/usr/bin/env python3
"""A4.1 — genera i dati leggeri del Nexus/Multiverso (atlante2/data/nexus/g.json) dal registro relazioni e dalle identita.
Uso: python3 tools/atlante_a4.py --scrivi | --verifica     (0 EUR, nessuna immagine, nessun dato inventato)"""
import json, sys, os, hashlib
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(R, p), encoding='utf-8'))
VER = {'verificata': 2, 'guida': 1, 'da verificare': 0}
CLS = {'narrativa': 'n', 'controparte': 'c', 'editoriale': 'e'}

def costruisci():
    rg, ident, idx = J('data/atlante/relazioni.json'), J('data/atlante/identita.json'), J('atlante2/data/index.json')
    noti = {v['i'] for v in idx['voci']}
    tipi = sorted({x['tipo'] for x in rg['relazioni']})
    rel, persi = [], 0
    for x in rg['relazioni']:
        if x['da'] not in noti or x['a'] not in noti: persi += 1; continue   # nodo senza voce in Atlante 2.0: non mostrato
        rel.append([x['da'], x['a'], tipi.index(x['tipo']), CLS[x['classe']], VER.get(x['verifica'], 0), x.get('qualifica') or '', 1 if x.get('controversa') else 0])
    app = {i['id']: i['apparizioni'] for i in ident['identita'] if i.get('apparizioni')}
    uni = {i['id']: i.get('universo') for i in ident['identita']}
    mv = J('data/atlante/blob/mvMapData.json')['universi']
    ut = {k: v['titoliIds'] for k, v in sorted(mv.items()) if v.get('titoliIds')}   # universo -> numeri dei titoli (confronto tra universi, A4.3)
    return {'v': 1, 'tipi': tipi, 'r': rel, 'app': app, 'ut': ut, 'nodi_senza_voce': persi}

def out(): return os.path.join(R, 'atlante2/data/nexus/g.json')

def main():
    g = costruisci(); s = json.dumps(g, ensure_ascii=False, separators=(',', ':'))
    if '--scrivi' in sys.argv:
        os.makedirs(os.path.dirname(out()), exist_ok=True); open(out(), 'w', encoding='utf-8').write(s + '\n'); print('scritto', len(s), 'byte;', len(g['r']), 'relazioni;', g['nodi_senza_voce'], 'senza voce')
    elif '--verifica' in sys.argv:
        ok = True
        def chk(n, c):
            nonlocal ok; print(('PASS ' if c else 'FAIL ') + n); ok = ok and c
        cur = open(out(), encoding='utf-8').read().strip() if os.path.exists(out()) else ''
        chk('nessuna deriva rispetto al registro', cur == s)
        chk('nessuna co-apparizione tra le relazioni', all(g['tipi'][r[2]] != 'co_apparizione' for r in g['r']))
        chk('classe coerente (editoriale solo tipi editoriali)', all((r[3] == 'e') == (g['tipi'][r[2]] in ('correlato', 'stessa_scheda', 'segnaposto', 'ispirato_a')) for r in g['r']))
        chk('titoli per universo presenti (confronto A4.3)', len(g['ut']) >= 15 and '125' in g['ut'].get('uni-earth-828', []))
        chk('relazioni narrative/controparte: 1', sum(1 for r in g['r'] if r[3] in 'nc') > 100)
        sys.exit(0 if ok else 1)
    else: print(__doc__)
main()
