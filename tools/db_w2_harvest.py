#!/usr/bin/env python3
"""W2 raccolta Wikidata (CC0) per film Marvel pre-MCU e paralleli: opere per titolo+anno (P31 film, P577), personaggi (P1441 presente-in), cast (P161), regia/sceneggiatura (P57/P58).
Il gruppo (franchise) determina la continuita' (mappa in db_w1_build.py GRP_UNI); personaggi presenti in piu' gruppi NON ricevono continuita' automatica.
Rete richiesta -> Actions. Uso: python3 tools/db_w2_harvest.py <out_dir>"""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_w1_harvest as H
FILM = {
 'x-men-fox': [('X-Men', 2000), ('X2', 2003), ('X-Men: The Last Stand', 2006), ('X-Men Origins: Wolverine', 2009), ('X-Men: First Class', 2011), ('The Wolverine', 2013), ('X-Men: Days of Future Past', 2014), ('X-Men: Apocalypse', 2016), ('Logan', 2017), ('Dark Phoenix', 2019)],
 'deadpool-fox': [('Deadpool', 2016), ('Deadpool 2', 2018)], 'new-mutants-fox': [('The New Mutants', 2020)],
 'spider-man-raimi': [('Spider-Man', 2002), ('Spider-Man 2', 2004), ('Spider-Man 3', 2007)], 'spider-man-garfield': [('The Amazing Spider-Man', 2012), ('The Amazing Spider-Man 2', 2014)],
 'venom-ssu': [('Venom', 2018), ('Venom: Let There Be Carnage', 2021), ('Venom: The Last Dance', 2024)], 'morbius-ssu': [('Morbius', 2022)], 'madame-web-ssu': [('Madame Web', 2024)], 'kraven-ssu': [('Kraven the Hunter', 2024)],
 'blade': [('Blade', 1998), ('Blade II', 2002), ('Blade: Trinity', 2004)], 'daredevil-elektra': [('Daredevil', 2003), ('Elektra', 2005)], 'ghost-rider': [('Ghost Rider', 2007), ('Ghost Rider: Spirit of Vengeance', 2011)],
 'hulk-2003': [('Hulk', 2003)], 'fantastic-four-1994': [('The Fantastic Four', 1994)], 'fantastic-four-fox': [('Fantastic Four', 2005), ('Fantastic Four: Rise of the Silver Surfer', 2007)], 'fantastic-four-trank': [('Fantastic Four', 2015)]}
Q_FILM = 'SELECT DISTINCT ?x WHERE { ?x rdfs:label "%s"@en . ?x wdt:P31/wdt:P279* wd:Q11424 . ?x wdt:P577 ?d . FILTER(YEAR(?d)=%d) }'
Q_REL = (('personaggi', 'SELECT DISTINCT ?x WHERE { ?x wdt:P1441 wd:%s . }'), ('interpreti', 'SELECT DISTINCT ?x WHERE { wd:%s wdt:P161 ?x . ?x wdt:P31 wd:Q5 }'),
         ('creatori', 'SELECT DISTINCT ?x WHERE { { wd:%s wdt:P57 ?x } UNION { wd:%s wdt:P58 ?x } }'))
def anno_di(e):
    for c in e.get('claims', {}).get('P577', []):
        v = c.get('mainsnak', {}).get('datavalue', {}).get('value')
        if isinstance(v, dict) and v.get('time'):
            try: yield int(v['time'].lstrip('+')[:4])
            except Exception: pass
def cerca_film(titolo, anno):
    """Fallback quando la query per etichetta esatta non trova nulla: ricerca testuale Wikidata (wbsearchentities) + verifica rigida
    (anno di uscita P577 uguale E P31 coerente con un film via descrizione/classe). Ritorna lista di QID verificati (puo' essere vuota) o None se la rete fallisce."""
    import urllib.parse
    r = H.get('https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&language=en&type=item&limit=10&search=' + urllib.parse.quote(titolo)); H.time.sleep(1)
    if 'search' not in r: return None
    cand = [x['id'] for x in r['search'] if 'film' in (x.get('description') or '').lower() or x.get('label', '').lower() == titolo.lower()]
    if not cand: return []
    ents = H.fetch_entities(cand, 'labels|claims')
    out = []
    for q, e in ents.items():
        if not isinstance(e, dict) or 'missing' in e: continue
        desc = next((x.get('description') or '' for x in r['search'] if x['id'] == q), '').lower()
        classi = set(H.claim_ids(e.get('claims', {}), 'P31')) | set(H.claim_ids(e.get('claims', {}), 'P279'))
        if anno in set(anno_di(e)) and ('Q11424' in classi or 'film' in desc): out.append(q)
    return out
def salva(out, nome, obj): json.dump(obj, open(out / nome, 'w'), ensure_ascii=False, separators=(',', ':'))
def main():
    """Robusta e riprendibile: ogni film e' isolato (try/except), il checkpoint w2_checkpoint.json si salva dopo ogni film e viene ripreso se presente in <out_dir>;
    anomalie registrate nel manifest; risultati parziali validi sempre salvati."""
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); H.ANOM.clear()
    ck = {'film': {}, 'rel': {}}
    if (out / 'w2_checkpoint.json').exists():
        try: ck = json.load(open(out / 'w2_checkpoint.json')); print('ripresa da checkpoint:', len(ck['film']), 'film')
        except Exception as e: H.anom('checkpoint illeggibile, si riparte: %s' % e)
    ck.setdefault('fb', []); ck.setdefault('film', {}); ck.setdefault('rel', {})
    man = {'avvio': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'film': {}, 'film_errori': []}
    membri = {}
    for g, lista in FILM.items():
        for titolo, anno in lista:
            k = '%s|%s|%d' % (g, titolo, anno)
            try:
                if k not in ck['film'] or (not ck['film'][k] and k not in ck.setdefault('fb', [])):
                    r = H.sparql(Q_FILM % (titolo.replace('"', '\\"'), anno)); ws = H.qids(r)
                    if ws is None: man['film_errori'].append(k); H.anom('film senza risposta valida: %s' % k); continue
                    ck['film'][k] = ws
                    if not ws:
                        fb = cerca_film(titolo, anno)
                        if fb is not None: ck['fb'].append(k)
                        if fb: ws = fb; ck['film'][k] = ws; H.anom('film trovato solo con ricerca testuale (fallback verificato per anno): %s -> %s' % (k, ws))
                        else: H.anom('film non trovato su Wikidata (query e ricerca): %s' % k)
                ws = ck['film'][k]; man['film'][k] = ws
                for w in ws:
                    membri.setdefault(w, set()).add(g)
                    if w not in ck['rel']:
                        rel = {}; ok = True
                        for nome, qq in Q_REL:
                            x = H.qids(H.sparql(qq % ((w, w) if nome == 'creatori' else (w,))))
                            if x is None: ok = False; H.anom('relazione %s non recuperata per %s (%s)' % (nome, w, k)); continue
                            rel[nome] = x
                        if ok: ck['rel'][w] = rel
                        else: ck.setdefault('parziali', {})[w] = rel
                    for nome, xs in (ck['rel'].get(w) or ck.get('parziali', {}).get(w) or {}).items():
                        for x in xs: membri.setdefault(x, set()).add(g if nome == 'personaggi' else g + ':' + nome)
            except Exception as e:
                man['film_errori'].append(k); H.anom('film %s: eccezione %s' % (k, str(e)[:120]))
            salva(out, 'w2_checkpoint.json', ck)
    ids = sorted(membri); rec = {}; et = {}
    try:
        ents = H.fetch_entities(ids, 'labels|aliases|descriptions|claims|sitelinks')
        refs = set()
        for q, e in ents.items():
            if not isinstance(e, dict) or 'missing' in e: continue
            cl = e.get('claims', {}); c = {p: H.claim_ids(cl, p) for p in H.KEEP if p in cl}
            for p in ('P31', 'P279', 'P1080', 'P8345', 'P179', 'P175', 'P170', 'P106', 'P463'): refs.update(c.get(p, []))
            rec[q] = {'q': q, 'g': sorted(membri[q]), 'l': {k: v['value'] for k, v in e.get('labels', {}).items()}, 'd': {k: v['value'] for k, v in e.get('descriptions', {}).items()},
                      'a': {k: [a['value'] for a in v] for k, v in e.get('aliases', {}).items()}, 'sl': {k: v['title'] for k, v in e.get('sitelinks', {}).items()}, 'c': c}
        mancanti = [q for q in ids if q not in rec]
        if mancanti: H.anom('%d entita senza dati (mancanti/non recuperate): %s' % (len(mancanti), mancanti[:10]))
        lab = H.fetch_entities(sorted(refs - set(rec)), 'labels'); et = {q: (v.get('labels', {}).get('en', {}).get('value')) for q, v in lab.items() if isinstance(v, dict)}
        for q, r in rec.items(): et.setdefault(q, r['l'].get('en'))
    except Exception as e: H.anom('fase entita: %s' % e)
    man['entita'] = len(rec); man['fine'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); man['anomalie'] = H.ANOM[:300]
    man['completa'] = not man['film_errori'] and len(rec) == len(ids)
    salva(out, 'w2_wikidata.json', {'fonte': 'Wikidata (CC0)', 'recuperato': man['fine'], 'completa': man['completa'], 'entita': rec, 'etichette': et})
    json.dump(man, open(out / 'w2_manifest.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in man.items() if k not in ('film', 'anomalie')}), 'film trovati', sum(1 for v in man['film'].values() if v), '/', len(man['film']), '| anomalie', len(H.ANOM))
    sys.exit(0 if rec else 1)
if __name__ == '__main__': main()
