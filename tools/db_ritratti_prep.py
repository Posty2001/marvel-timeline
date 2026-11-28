#!/usr/bin/env python3
"""Preparazione (solo metadati locali, nessuna rete, nessuna immagine) delle proposte di ritratto per le nuove identita' con interpreti documentati.
Elenca gli ID candidati per la pipeline PRIVATA esistente (`tools/atlante_engine2.py`, immagini solo in IndexedDB, mai nel repository). L'esecuzione resta SOSPESA finche' le condizioni d'uso TMDB
per l'archiviazione non sono confermate (nessun nuovo metadato TMDB archiviato). Le voci senza immagine usano l'emblema originale (monogramma/composizione) e non sono presentate come ritratti.
Uso: python3 tools/db_ritratti_prep.py [--scrivi]"""
import json, glob, pathlib, sys
R = pathlib.Path(__file__).resolve().parent.parent; E = R / 'data/atlante/espansione'
out = []
for f in sorted(glob.glob(str(E / 'canon/w*_*.jsonl'))):
    if 'arricch' in f: continue
    for l in open(f):
        r = json.loads(l)
        if r['tipo'] == 'identita' and r.get('interpreti'):
            out.append({'id': r['id'], 'nome': r['nome'], 'interpreti': r['interpreti'][:3], 'universo': r.get('universo'), 'livello': r['livello']})
d = {'stato': 'sospesa: termini TMDB per l\'archiviazione non confermati', 'candidati': len(out), 'voci': out}
print(json.dumps({'candidati': len(out)}))
if '--scrivi' in sys.argv: (E / 'ritratti_candidati.json').write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n')
