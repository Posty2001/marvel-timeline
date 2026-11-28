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
def pagine_prefisso(pre, anom, rx):
    import re
    out, cont = [], None
    while True:
        p = {'action': 'query', 'list': 'allpages', 'apprefix': pre, 'aplimit': 500, 'apnamespace': 0, 'apfilterredir': 'nonredirects'}
        if cont: p['apcontinue'] = cont
        r = B.api(B.WIKI['marveldb'], p)
        if 'errore' in r: anom.append('prefisso %s: %s' % (pre, r['errore'])); break
        out += [x['title'] for x in r.get('query', {}).get('allpages', []) if re.match(rx, x['title'])]
        cont = r.get('continue', {}).get('apcontinue')
        if not cont: break
    return out
import urllib.request, urllib.parse, re as _re
def wd_etichette(nomi, anom):
    """Seconda fonte: elementi Wikidata con ETICHETTA inglese esatta e classe «fictional ...» (nessun testo; solo QID/etichetta/classe)."""
    out = {}
    for i in range(0, len(nomi), 100):
        bl = nomi[i:i + 100]
        vals = ' '.join('"%s"@en' % n.replace('\\', '').replace('"', '') for n in bl)
        q = ('SELECT ?l ?x ?cl WHERE { VALUES ?l { %s } ?x rdfs:label ?l . ?x wdt:P31 ?c . ?c rdfs:label ?cl . FILTER(LANG(?cl)="en" && CONTAINS(LCASE(STR(?cl)),"fictional")) '
             '{ ?x wdt:P1080 ?u . ?u rdfs:label ?ul . FILTER(LANG(?ul)="en" && (CONTAINS(LCASE(STR(?ul)),"marvel") || CONTAINS(LCASE(STR(?ul)),"earth-"))) } UNION { { ?x wdt:P1441 ?w } UNION { ?w wdt:P674 ?x } ?w wdt:P123 ?pub . ?pub rdfs:label "Marvel Comics"@en } }' % vals)
        for t in range(3):
            try:
                time.sleep(1.5)
                r = json.load(urllib.request.urlopen(urllib.request.Request('https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': q, 'format': 'json'}), headers={'User-Agent': B.UA, 'Accept': 'application/sparql-results+json'}), timeout=90))
                for b in r['results']['bindings']:
                    out.setdefault(b['l']['value'], {})[b['x']['value'].rsplit('/', 1)[-1]] = b['cl']['value']
                break
            except Exception as e:
                if t == 2: anom.append('wd blocco %d: %s' % (i, str(e)[:80]))
                time.sleep(8 * (t + 1))
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
    for tipo, ps in cfg.get('prefissi_pagine', {}).items():
        for pre, rx in ps:
            k = 'prefisso:' + pre
            if k in ck['membri']: continue
            ck['membri'][k] = {'tipo': tipo, 't': pagine_prefisso(pre, anom, rx)}; salva()
    # varianti: ricerca per prefisso sui personaggi con piu' albi
    try:
        cv = json.load(open(out / 'cv2_marvel.json' if (out / 'cv2_marvel.json').exists() else E / 'raw/cv2_marvel.json'))['risorse']['characters']
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
    base = lambda t: _re.sub(r'\s*\([^)]*\)\s*$', '', t).strip()
    nomi = sorted({base(t) for m in ck['membri'].values() for t in m['t'] if ck['pagine'].get(t)} - set(ck.setdefault('wd2', {}).keys()))
    ck.setdefault('wd2_fatti', [])
    gia = set(ck['wd2_fatti']); nuovi = [n for n in nomi if n not in gia]
    for i in range(0, len(nuovi), 400):
        bl = nuovi[i:i + 400]; r = wd_etichette(bl, anom)
        for n in bl: ck['wd2'][n] = r.get(n, {}); ck['wd2_fatti'].append(n)
        salva()
    trov = {t: v for t, v in ck['pagine'].items() if v}
    json.dump({'fonte': 'Marvel Database (Fandom), CC BY-SA 3.0, solo categorie/parametri-fatto', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'membri': {c: m for c, m in ck['membri'].items()}, 'varianti': ck['varianti'], 'wd': {n: v for n, v in ck.get('wd2', {}).items() if v}, 'pagine': trov},
              open(out / 'w8_md.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    man.update({'membri': {c: len(m['t']) for c, m in ck['membri'].items()}, 'varianti_nomi': len(ck['varianti']), 'pagine': len(trov), 'anomalie': (anom + B.ERRLOG)[:200], 'fine': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
    json.dump(man, open(out / 'w8_manifest.json', 'w'), indent=1, ensure_ascii=False); print(json.dumps({k: v for k, v in man.items() if k not in ('anomalie', 'membri')})); sys.exit(0 if trov else 1)
if __name__ == '__main__': main()
