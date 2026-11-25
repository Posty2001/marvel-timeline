#!/usr/bin/env python3
"""A3.2 - prepara atlante2/data/pilot/proposte.json (solo metadati) dalle proposte CLIP, segnando con ck=1 le scene confermate anche da SigLIP (consenso dei due modelli).
Uso: python3 tools/atlante_engine_pubblica.py [--verifica]"""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); E = os.path.join(R, 'data/atlante/engine'); OUT = os.path.join(R, 'atlante2/data/pilot/proposte.json')
def main():
    c = json.load(open(os.path.join(E, 'proposte_clip.json'), encoding='utf-8')); s = json.load(open(os.path.join(E, 'proposte_siglip.json'), encoding='utf-8'))
    sp = {i['id']: {p['p'] for p in i['proposte']} for i in s['identita']}; ids = []
    for i in c['identita']:
        ps = []
        for p in i['proposte']:
            q = {k: p[k] for k in ('rk', 'p', 'w', 'h', 'num', 'sc', 'crop')}; q['ck'] = 1 if p['p'] in sp.get(i['id'], set()) else 0; ps.append(q)
        ids.append({'id': i['id'], 'nome': i['nome'], 'proposte': ps})
    out = {'schema': 1, 'motore': 'A3.2 prototipo (CLIP + consenso SigLIP)', 'generato': c['generato'], 'diritti': c['diritti'], 'identita': ids}
    txt = json.dumps(out, ensure_ascii=False, indent=1) + '\n'
    if '--verifica' in sys.argv:
        ok = os.path.exists(OUT) and open(OUT, encoding='utf-8').read() == txt; print('OK' if ok else 'DIFFERENTE'); sys.exit(0 if ok else 1)
    open(OUT, 'w', encoding='utf-8').write(txt); print('scritto', OUT, sum(len(i['proposte']) for i in ids), 'proposte,', sum(p['ck'] for i in ids for p in i['proposte']), 'con consenso')
main()
