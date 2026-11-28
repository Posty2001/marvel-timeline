#!/usr/bin/env python3
"""Dati statici per le condizioni di sblocco degli sfondi animati della Tessera TVA 3.0.

Regola «identità legate a Spider-Man» (Spider-Verse): identità del registro principale di TVA Atlas (k = 'i', con dossier effettivo)
  (a) membri dell'hub «hub-peter-parker», oppure
  (b) appartenenti a un universo dedicato a Spider-Man (id universo contenente «spider», oppure Raimi-verse, Garfield-verse).
Nessun dato inventato: tutto deriva da atlante2/data/index.json e dai dossier degli hub.

Uso: python3 tools/tessera2_dati.py --scrivi | --verifica
"""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tessera2', 'data', 'regole.json')
UNI_EXTRA = ('raimi-verse', 'garfield-verse')


def calcola():
    idx = json.load(open(os.path.join(ROOT, 'atlante2/data/index.json')))
    BY = {v['i']: v for v in idx['voci']}
    sh = BY['hub-peter-parker']['sh']
    hub = json.load(open(os.path.join(ROOT, 'atlante2/data/d/%03d.json' % sh)))['hub-peter-parker']['membri']
    uni = sorted({v['u'] for v in idx['voci'] if v.get('u') and ('spider' in v['u'] or any(x in v['u'] for x in UNI_EXTRA))})
    ids = {i for i in hub if i in BY and BY[i]['k'] == 'i'}
    ids |= {i for i, v in BY.items() if v['k'] == 'i' and v.get('u') in uni}
    return {'v': 1, 'regola': 'spiderman: identità (k=i) membri di hub-peter-parker o appartenenti a un universo dedicato a Spider-Man',
            'universi': uni, 'hub': 'hub-peter-parker', 'spiderman': sorted(ids)}


if __name__ == '__main__':
    d = calcola()
    if '--scrivi' in sys.argv:
        json.dump(d, open(OUT, 'w'), ensure_ascii=False, indent=1, sort_keys=True); print('scritto', os.path.relpath(OUT, ROOT), len(d['spiderman']), 'identità')
    else:
        cur = json.load(open(OUT)) if os.path.exists(OUT) else None
        ok = cur == json.loads(json.dumps(d, sort_keys=True))
        print('OK' if ok else 'DIVERSO: rigenerare con --scrivi', len(d['spiderman']), 'identità')
        sys.exit(0 if ok else 1)
