#!/usr/bin/env python3
"""W8: raccolta mirata su Marvel Database (Fandom, CC BY-SA 3.0; API MediaWiki; solo titoli, categorie e parametri-fatto brevi, mai prosa) per
artefatti/armi, universi/dimensioni, entita' cosmiche, specie/civilta', eventi/saghe e varianti/incarnazioni dei personaggi principali.
Configurazione: data/atlante/espansione/w8_config.json {"modo": "scoperta"|"raccolta", "categorie": {tipo: [nome categoria,...]}, "max_per_tipo": N, "varianti_min_albi": N}.
Modo «scoperta»: elenca (con numero di pagine) le categorie il cui nome inizia con prefissi noti -> manifest (serve a fissare i nomi esatti).
Modo «raccolta»: membri delle categorie -> pagine (categorie + parametri-fatto) in blocchi; varianti via ricerca per prefisso «Nome (Earth-» sui personaggi con piu' albi (Comic Vine).
Riprendibile (w8_checkpoint.json); anomalie nel manifest. Uso: python3 tools/db_w8_harvest.py <out_dir>   (rete -> Actions)"""
import json, sys, time, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_w1b_harvest as B
E = B.E; ERR = B.ERR
PREFISSI = ['Artifact', 'Weapon', 'Race', 'Species', 'Cosmic', 'Universe', 'Dimension', 'Realm', 'Event', 'Crossover', 'Alternate', 'Alien', 'Deities', 'Gods', 'Eternals', 'Celestial', 'Mutant', 'Inhuman', 'Skrull', 'Kree', 'Weapons', 'Armor', 'Magical', 'Technolog']
def membri(cat, anom, mx=100000):
    out, cont = [], None
    while len(out) < mx:
        p = {'action': 'query', 'list': 'categorymembers', 'cmtitle': 'Category:' + cat, 'cmlimit': 500, 'cmtype': 'page', 'cmnamespace': 0}
        if cont: p['cmcontinue'] = cont
        r = B.api(B.WIKI['marveldb'], p)
        if 'errore' in r: anom.append('categoria %s: %s' % (cat, r['errore'])); break
        out += [x['title'] for x in r.get('query', {}).get('categorymembers', [])]
        cont = r.get('continue', {}).get('cmcontinue')
        if not cont: break
    return out
def scoperta(anom):
    cats = {}
    for pre in PREFISSI:
        cont = None
        for _ in range(4):
            p = {'action': 'query', 'list': 'allcategories', 'acprefix': pre, 'aclimit': 200, 'acprop': 'size'}
            if cont: p['accontinue'] = cont
            r = B.api(B.WIKI['marveldb'], p)
            if 'errore' in r: anom.append('scoperta %s: %s' % (pre, r['errore'])); break
            for c in r.get('query', {}).get('allcategories', []):
                if c.get('pages', 0) >= 5: cats[c['category']] = c['pages']
            cont = r.get('continue', {}).get('accontinue')
            if not cont: break
    return cats
def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); anom = []
    cfg = json.load(open(E / 'w8_config.json')); man = {'avvio': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'modo': cfg['modo']}
    if cfg['modo'] == 'scoperta':
        cats = scoperta(anom); man['categorie'] = dict(sorted(cats.items(), key=lambda x: -x[1])[:400])
        # prova anche i nomi di configurazione
        man['prova'] = {c: len(membri(c, anom, 600)) for t in cfg.get('categorie', {}).values() for c in t}
        man['anomalie'] = (anom + B.ERRLOG)[:200]; json.dump(man, open(out / 'w8_manifest.json', 'w'), indent=1, ensure_ascii=False); print(json.dumps({k: (len(v) if hasattr(v, '__len__') else v) for k, v in man.items()})); return
    ck = {'v': 1, 'membri': {}, 'pagine': {}, 'varianti': {}}; ckf = out / 'w8_checkpoint.json'
    if ckf.exists():
        try: ck = json.load(open(ckf)); print('ripresa')
        except Exception as e: anom.append('checkpoint illeggibile: %s' % e)
    def salva(): json.dump(ck, open(ckf, 'w'), ensure_ascii=False, separators=(',', ':'))
    mx = cfg.get('max_per_tipo', 4000)
    for tipo, cs in cfg['categorie'].items():
        for c in cs:
            if c in ck['membri']: continue
            ck['membri'][c] = {'tipo': tipo, 't': membri(c, anom, mx)}; salva()
    # varianti: ricerca per prefisso sui personaggi con piu' albi
    try:
        cv = json.load(open(E / 'raw/cv2_marvel.json'))['risorse']['characters']
    except Exception: cv = []
    pers = [x for x in cv if (x.get('c') or 0) >= cfg.get('varianti_min_albi', 400)]
    for x in pers:
        nome = (x.get('rn') or x['n']).split(',')[0].split('/')[0].strip()
        if not nome or nome in ck['varianti']: continue
        r = B.api(B.WIKI['marveldb'], {'action': 'query', 'list': 'prefixsearch', 'pssearch': nome + ' (Earth-', 'pslimit': 100, 'psnamespace': 0})
        if 'errore' in r: anom.append('varianti %s: %s' % (nome, r['errore'])); continue
        ck['varianti'][nome] = [y['title'] for y in r.get('query', {}).get('prefixsearch', []) if '(Earth-' in y['title']]
        if len(ck['varianti']) % 25 == 0: salva()
    salva()
    titoli = sorted({t for m in ck['membri'].values() for t in m['t']} | {t for v in ck['varianti'].values() for t in v if not t.endswith('(Earth-616)')})
    da = [t for t in titoli if t not in ck['pagine']]; man['titoli'] = len(titoli)
    for i in range(0, len(da), 20):
        try: r = B.pagine('marveldb', da[i:i + 20], None)
        except Exception as e: anom.append('blocco %s: %s' % (da[i], str(e)[:80])); continue
        if r is None: continue
        for t, v in r.items(): ck['pagine'][t] = None if not v else {'titolo': v['titolo'], 'url': v['url'], 'disambigua': v['disambigua'], 'categorie': v['categorie'][:25], 'infobox': v['infobox']}
        if (i // 20) % 10 == 0: salva()
    salva()
    trov = {t: v for t, v in ck['pagine'].items() if v}
    json.dump({'fonte': 'Marvel Database (Fandom), CC BY-SA 3.0, solo categorie/parametri-fatto', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'membri': {c: m for c, m in ck['membri'].items()}, 'varianti': ck['varianti'], 'pagine': trov},
              open(out / 'w8_md.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    man.update({'membri': {c: len(m['t']) for c, m in ck['membri'].items()}, 'varianti_nomi': len(ck['varianti']), 'pagine': len(trov), 'anomalie': (anom + B.ERRLOG)[:200], 'fine': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
    json.dump(man, open(out / 'w8_manifest.json', 'w'), indent=1, ensure_ascii=False); print(json.dumps({k: v for k, v in man.items() if k not in ('anomalie', 'membri')})); sys.exit(0 if trov else 1)
if __name__ == '__main__': main()
