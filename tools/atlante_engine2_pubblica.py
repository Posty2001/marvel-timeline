#!/usr/bin/env python3
"""Pubblica le proposte del motore 2.0 per l'app: data/atlante/engine/proposte2_w1.json -> atlante2/data/pilot/proposte2.json (solo metadati, nessuna immagine).
Mantiene solo i campi usati dall'app; verifica percorsi CDN, ritagli e unicità delle scene tra identità. Uso: python3 tools/atlante_engine2_pubblica.py [--verifica]"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data/atlante/engine/proposte2_w1.json'); DST = os.path.join(ROOT, 'atlante2/data/pilot/proposte2.json'); RX = re.compile(r'^/[A-Za-z0-9_-]{5,60}\.(jpg|png)$')
def costruisci():
    s = json.load(open(SRC, encoding='utf-8')); out = []; viste = {}
    for i in s['identita']:
        pr = []
        for x in i['proposte']:
            c = x['crop']
            assert RX.match(x['p']), x['p']; assert 1 <= c['z'] <= 4 and 0 <= c['cx'] <= 1 and 0 <= c['cy'] <= 1, (i['id'], c)
            assert x['p'] not in viste or viste[x['p']] == i['id'], 'scena in due identità: ' + x['p']; viste[x['p']] = i['id']
            pr.append({k: x[k] for k in ('rk', 'p', 'w', 'h', 'num', 'sc', 'm', 'ck', 'crop')})
        assert 0 < len(pr) <= 10 and (i['conf'] == 'bassa' or len(pr) <= 5), (i['id'], len(pr), i['conf'])
        out.append({'id': i['id'], 'nome': i['nome'], 'conf': i['conf'], 'proposte': pr})
    return {'schema': 2, 'motore': s['motore'], 'generato': s['generato'], 'diritti': s['diritti'], 'identita': out}
if __name__ == '__main__':
    o = costruisci()
    if '--verifica' in sys.argv: print('OK', len(o['identita']), 'identità,', sum(len(i['proposte']) for i in o['identita']), 'proposte'); sys.exit(0)
    json.dump(o, open(DST, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':')); print('scritto', DST)
