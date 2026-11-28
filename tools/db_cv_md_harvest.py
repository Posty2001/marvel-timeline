#!/usr/bin/env python3
"""Seconda fonte per le voci Comic Vine: esistenza della pagina omonima su Marvel Database (Fandom, CC BY-SA 3.0; solo titolo/URL/categorie, nessuna prosa).
Bersagli: data/atlante/espansione/cv_bersagli.json (titoli candidati per voce). Riprendibile (cvmd_checkpoint.json).
Uso: python3 tools/db_cv_md_harvest.py <out_dir>   (rete -> Actions)"""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_w1b_harvest as B
E = B.E
def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    bers = json.load(open(E / 'cv_bersagli.json'))['bersagli']
    titoli = sorted({t for b in bers for t in b['titoli']})
    ck = {'v': 1, 'pagine': {}}; f = out / 'cvmd_checkpoint.json'
    if f.exists():
        try: ck = json.load(open(f)); print('ripresa', len(ck['pagine']))
        except Exception as e: print('checkpoint illeggibile', e)
    da = [t for t in titoli if t not in ck['pagine']]
    for i in range(0, len(da), 20):
        blocco = da[i:i + 20]
        try: r = B.pagine('marveldb', blocco, None)
        except Exception as e: print('blocco', blocco[0], str(e)[:100]); continue
        if r is None: continue
        for t, v in r.items():
            ck['pagine'][t] = None if not v else {'titolo': v['titolo'], 'url': v['url'], 'disambigua': v['disambigua'], 'categorie': v['categorie'][:10]}
        if (i // 20) % 10 == 0: json.dump(ck, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(ck, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
    trov = {t: v for t, v in ck['pagine'].items() if v}
    json.dump({'fonte': 'Marvel Database (Fandom), CC BY-SA 3.0, solo titolo/URL/categorie', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'pagine': trov, 'interrogati': len(ck['pagine'])},
              open(out / 'cvmd.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('titoli', len(titoli), 'interrogati', len(ck['pagine']), 'trovati', len(trov)); sys.exit(0 if ck['pagine'] else 1)
if __name__ == '__main__': main()
