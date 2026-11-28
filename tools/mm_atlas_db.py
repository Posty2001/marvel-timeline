#!/usr/bin/env python3
"""Archivio consultabile da Miss Minutes: voci del canon della Database Expansion (escluso lo storico, gia' coperto dai dati dell'app) in formato `knowledge`.
NON modifica motore, gateway ne' quote: e' solo un file di dati letto dal caricatore (miss-minutes/knowledge/atlas_db.json). Kind «scheda» (nessuna fusione con i personaggi dell'app);
continuita' sempre esplicita nel campo `universe` e nel nome (omonimi mai fusi). Testi: sintesi originali in italiano composte da fatti verificati; descrizione Wikidata (CC0) in lingua originale.
Uso: python3 tools/mm_atlas_db.py [--scrivi|--verifica]"""
import json, pathlib, sys, re
R = pathlib.Path(__file__).resolve().parent.parent; E = R/'data/atlante/espansione'; OUT = R/'miss-minutes/knowledge/atlas_db.json'
TIPO = {'identita': 'un personaggio', 'organizzazione': 'un\'organizzazione', 'artefatto': 'un oggetto o artefatto', 'luogo': 'un luogo', 'pianeta': 'un pianeta', 'evento': 'un evento o una saga', 'battaglia': 'una battaglia',
        'specie': 'una specie', 'civilta': 'una civiltà', 'opera': 'un\'opera (film, serie, testata o fumetto)', 'attore': 'un interprete', 'creatore': 'un autore o creatore', 'universo': 'un universo o una dimensione', 'entita-cosmica': 'un\'entità cosmica'}
def costruisci():
    idx = json.load(open(R/'atlante2/data/index.json')); un = {k: v['n'] for k, v in idx['meta']['universi'].items()}
    canon = {}; dz = json.load(open(E/'dossier_it.json')) if (E/'dossier_it.json').exists() else {}
    for f in sorted((E/'canon').glob('w*_*.jsonl')):
        if 'arricch' in f.name: continue
        for l in f.read_text().splitlines():
            if l.strip(): r = json.loads(l); canon.setdefault(r['id'], r)
    for i, r in canon.items():
        if r['tipo'] == 'universo': un.setdefault(i, r['nome'])
    out = []
    for i, r in sorted(canon.items()):
        u = un.get(r.get('universo') or '', '')
        d = ((r.get('descrizione') or {}).get('en') or '').strip()
        t = '%s è %s%s.' % (r['nome'], TIPO.get(r['tipo'], 'una voce'), (' nella continuità «%s»' % u) if u else '')
        if d: t += ' Descrizione Wikidata: %s.' % d[:160].rstrip('.')
        if r.get('interpreti'): t += ' Interpreti: %s.' % ', '.join(r['interpreti'][:3])
        if i in dz: t += ' ' + ' '.join(s['x'] for s in dz[i]['sezioni'][:2])[:300]
        f = r.get('fatti', {})
        out.append({'id': 'db:' + i, 'name': r['nome'], 'aliases': ([r['nome']] + r.get('alias', []))[:6], 'category': 'scheda',
                    'universe': u, 'text': t[:620], 'source': 'TVA Atlas · Database Expansion (Wikidata CC0' + ('; MCU Wiki/Marvel Database CC BY-SA, fatti' if any('CC BY-SA' in (x.get('licenza') or '') for x in r.get('fonti', [])) else '') + ')',
                    'spoiler': bool(f.get('morte')), 'verification': 'verificata'})
    return {'schema': 'knowledge-db-1', 'note': 'Voci del canon della Database Expansion; dati pubblici, nessun dato personale; omonimi mai fusi (continuita\' nel campo universe).', 'records': out}
def main():
    d = costruisci(); ids = [r['id'] for r in d['records']]; ok = len(ids) == len(set(ids)) and all(r['text'] and r['verification'] == 'verificata' for r in d['records'])
    print(json.dumps({'record': len(ids), 'ok': ok, 'bytes': len(json.dumps(d, ensure_ascii=False, separators=(',', ':')))}))
    if '--scrivi' in sys.argv: OUT.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n')
    sys.exit(0 if ok else 1)
if __name__ == '__main__': main()
