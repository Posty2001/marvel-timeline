#!/usr/bin/env python3
"""Ricostruzione INCREMENTALE del database esteso (ordine fisso, nessuna perdita di ID).
Uso: python3 tools/db_ricostruisci.py [--verifica] [--solo-derivati]
Passi: 1) registro ID append-only (--scrivi: gli ID gia' registrati NON cambiano)  2) dossier + livelli A/B  3) indice runtime (cancella e rigenera atlante2/data/db/)
4) relazioni runtime rel.json (DEVE seguire il passo 3)  5) archivio Miss Minutes (solo dati)  6) conteggi canonici  7) candidati ritratti (solo metadati)
Guardia: se il registro ID perde ID rispetto a HEAD, si ferma (gli ID rimossi devono diventare lapidi, mai sparire)."""
import json, subprocess, sys, pathlib
R = pathlib.Path(__file__).resolve().parent.parent; E = 'data/atlante/espansione/ids_registro.json'
def run(*a, ok=(0,)):
    print('>>', ' '.join(a)); p = subprocess.run(a, cwd=R, capture_output=True, text=True)
    if p.returncode not in ok: print(p.stdout[-1500:], p.stderr[-1500:]); sys.exit('FALLITO: ' + ' '.join(a))
    return p.stdout
def ids_registro(testo):
    d = json.loads(testo); d = d.get('ids', d) if isinstance(d, dict) else d
    return set(d if isinstance(d, list) else d.keys())
def guardia():
    try: prima = ids_registro(subprocess.run(['git', 'show', 'HEAD:' + E], cwd=R, capture_output=True, text=True, check=True).stdout)
    except Exception: return
    ora = ids_registro((R / E).read_text()); persi = prima - ora
    if persi: sys.exit('GUARDIA: %d ID del registro sono spariti (es. %s): ripristinare da git e usare lapidi' % (len(persi), sorted(persi)[:3]))
    print('guardia registro ID: ok (%d ID, +%d nuovi)' % (len(ora), len(ora - prima)))
def main():
    if '--verifica' in sys.argv:
        run('python3', 'tools/db_ids.py', '--verifica'); guardia(); run('python3', 'tools/db_conteggi.py'); return
    if '--solo-derivati' not in sys.argv: run('python3', 'tools/db_ids.py', '--scrivi')
    guardia()
    run('python3', 'tools/db_dossier.py', '--scrivi', ok=(0, 1))   # BrokenPipe in stampa non e' un errore
    run('python3', 'tools/db_w1_build.py', '--solo-runtime')
    run('python3', 'tools/db_rel_build.py', '--scrivi')
    run('python3', 'tools/mm_atlas_db.py', '--scrivi')
    run('python3', 'tools/db_conteggi.py', '--scrivi')
    run('python3', 'tools/db_ritratti_prep.py', '--scrivi')
    print('ricostruzione completata')
if __name__ == '__main__': main()
