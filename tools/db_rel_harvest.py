#!/usr/bin/env python3
"""Raccolta delle relazioni narrative DOCUMENTATE da Wikidata (CC0) per le entita' del registro (identita' storiche arricchite + nuove).
Solo proprieta' di relazione (famiglia, partner, appartenenza, mentorato, successione, rivalita'): nessuna co-apparizione, nessuna prosa.
Riprendibile (checkpoint per blocco), tollerante agli errori. Uso: python3 tools/db_rel_harvest.py <out_dir>"""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_w1_harvest as H
R = pathlib.Path(__file__).resolve().parent.parent; E = R / 'data/atlante/espansione'
PROPS = ('P22', 'P25', 'P26', 'P40', 'P3373', 'P1038', 'P451', 'P1327', 'P7047', 'P1066', 'P802', 'P463', 'P1365', 'P1366', 'P1344', 'P144')
def qids_registro():
    q = set()
    for v in json.load(open(E / 'ids_registro.json'))['ids'].values():
        if v.get('stato') != 'lapide' and v.get('ids_esterni', {}).get('wikidata') and v.get('tipo') in ('identita', 'organizzazione', 'entita-cosmica', 'specie', 'civilta'): q.add(v['ids_esterni']['wikidata'])
    for f in (E / 'canon').glob('*_arricchimenti.jsonl'):
        for l in f.read_text().splitlines():
            if l.strip():
                r = json.loads(l)
                if r.get('wikidata'): q.add(r['wikidata'])
    return sorted(q)
def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); H.ANOM.clear()
    ck = {}
    if (out / 'rel_checkpoint.json').exists():
        try: ck = json.load(open(out / 'rel_checkpoint.json')); print('ripresa da checkpoint:', len(ck), 'entita')
        except Exception as e: H.anom('checkpoint illeggibile: %s' % e)
    ids = qids_registro(); da = [q for q in ids if q not in ck]
    for i in range(0, len(da), 50):
        blk = da[i:i + 50]
        try:
            ents = H.fetch_entities(blk, 'claims')
            for q in blk:
                e = ents.get(q)
                if not isinstance(e, dict) or 'missing' in e: continue
                ck[q] = {p: H.claim_ids(e.get('claims', {}), p) for p in PROPS if p in e.get('claims', {})}
        except Exception as ex: H.anom('blocco %s: %s' % (blk[0], str(ex)[:100]))
        json.dump(ck, open(out / 'rel_checkpoint.json', 'w'), separators=(',', ':'))
    man = {'entita_richieste': len(ids), 'entita_lette': len(ck), 'con_relazioni': sum(1 for v in ck.values() if v), 'anomalie': H.ANOM[:200], 'completa': len(ck) >= len(ids) * 0.97, 'fine': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    json.dump({'fonte': 'Wikidata (CC0)', 'recuperato': man['fine'], 'entita': {q: v for q, v in ck.items() if v}}, open(out / 'rel_wikidata.json', 'w'), separators=(',', ':'))
    json.dump(man, open(out / 'rel_manifest.json', 'w'), indent=1); print(json.dumps({k: v for k, v in man.items() if k != 'anomalie'}), '| anomalie', len(H.ANOM))
    sys.exit(0 if ck else 1)
if __name__ == '__main__': main()
