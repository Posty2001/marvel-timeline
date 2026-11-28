#!/usr/bin/env python3
"""Conteggi CANONICI deduplicati (per ID e per QID Wikidata) per categoria e per ondata; relazioni narrative separate da co-apparizioni/editoriali (mai nei conteggi). Uso: python3 tools/db_conteggi.py [--scrivi]"""
import json, pathlib, collections, sys
R = pathlib.Path(__file__).resolve().parent.parent; E = R/'data/atlante/espansione'
LIV = json.load(open(E/'livelli_w8.json'))['livelli'] if (E/'livelli_w8.json').exists() else {}
def main():
    ids, qid, per_t, per_w, livelli = set(), {}, collections.Counter(), collections.defaultdict(collections.Counter), collections.Counter()
    dup_id = dup_q = 0
    for f in sorted((E/'canon').glob('*.jsonl')):
        if 'arricchimenti' in f.name: continue
        for l in f.read_text().splitlines():
            if not l.strip(): continue
            r = json.loads(l)
            if r['id'] in ids: dup_id += 1; continue
            ids.add(r['id']); q = (r.get('ids_esterni') or {}).get('wikidata')
            if q:
                if q in qid: dup_q += 1; continue
                qid[q] = r['id']
            per_t[r['tipo']] += 1; per_w[f.stem][r['tipo']] += 1; livelli[LIV.get(r['id'], r.get('livello', '?'))] += 1
    storico = per_w.pop('storico', {})
    rel_db = json.load(open(E/'relazioni_db.json'))['relazioni']; rel_st = json.load(open(R/'data/atlante/relazioni.json'))['relazioni']
    cl = lambda L: collections.Counter((x['classe'], x['verifica']) for x in L)
    out = {'voci_canoniche': len(ids), 'duplicati_id_scartati': dup_id, 'duplicati_qid_scartati': dup_q, 'per_categoria': dict(per_t), 'per_livello': dict(livelli),
           'per_ondata': {k: {'totale': sum(v.values()), **dict(v)} for k, v in per_w.items()}, 'storico': dict(storico),
           'relazioni_db': {'narrative': sum(1 for x in rel_db if x['classe'] == 'narrativa'), 'controparti': sum(1 for x in rel_db if x['classe'] == 'controparte'), 'verificate': sum(1 for x in rel_db if x['verifica'] == 'verificata'),
                            'da_verificare': sum(1 for x in rel_db if x['verifica'] != 'verificata')},
           'relazioni_storiche': {'narrative_verificate': sum(1 for x in rel_st if x['classe'] == 'narrativa' and x['verifica'] == 'verificata'), 'narrative_totali': sum(1 for x in rel_st if x['classe'] == 'narrativa'),
                                  'editoriali_escluse': sum(1 for x in rel_st if x['classe'] == 'editoriale')},
           'note': 'co-apparizioni e collegamenti editoriali NON sono relazioni narrative e non entrano nei conteggi'}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if '--scrivi' in sys.argv: (E/'conteggi_canonici.json').write_text(json.dumps(out, ensure_ascii=False, indent=1)+'\n')
if __name__ == '__main__': main()
