#!/usr/bin/env python3
"""W1 raccolta MCU da Wikidata (CC0). Richiede rete -> si esegue in Actions (modalita db_w1 di «TMDB sync (manuale)»).
Strategia robusta: SPARQL solo per ottenere QID (leggero), poi wbgetentities a blocchi di 50 (API stabile). Nessun dato TMDB.
Uscita: <out>/w1_wikidata.json (+ w1_manifest.json con esito per gruppo). User-Agent dichiarato, pause tra le richieste.
Uso: python3 tools/db_w1_harvest.py <out_dir> [--max N]"""
import json, sys, time, pathlib, urllib.request, urllib.parse, urllib.error
UA = 'TVA-Archives-W1/1.0 (progetto personale non commerciale; https://github.com/Posty2001/marvel-timeline)'
LANGS = 'en|it'
ANOM = []  # anomalie registrate (mai scartate in silenzio): salvate nei manifest
def anom(msg):
    ANOM.append(str(msg)[:300]); print('ANOMALIA:', str(msg)[:300], file=sys.stderr)
def get(url, hdr=None, tries=4):
    """GET JSON con tentativi limitati: 429/503 rispettano Retry-After (max 120 s), 5xx/timeout backoff; 4xx (tranne 429) non si ripetono."""
    last = ''
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=dict({'User-Agent': UA}, **(hdr or {}))), timeout=90))
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code in (429, 503):
                try: w = min(120, int(e.headers.get('Retry-After', '') or 0))
                except Exception: w = 0
                time.sleep(max(w, 8 * (i + 1)))
            elif 500 <= e.code < 600: time.sleep(5 * (i + 1))
            else: break
        except Exception as e:
            last = str(e)[:150]; time.sleep(4 * (i + 1))
    anom('GET fallita (%s): %s' % (last, url[:120]))
    return {'errore': last}
def sparql(q):
    r = get('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(q), {'Accept': 'application/sparql-results+json'})
    time.sleep(2)
    return r
def var_select(q):
    """Variabili proiettate dalla SELECT (per il controllo preventivo query/parser)."""
    import re
    m = re.search(r'SELECT\s+(?:DISTINCT\s+)?(.*?)\s+WHERE', q, re.S)
    return re.findall(r'\?(\w+)', m.group(1)) if m else []
def corpo_lega(q, v):
    """True se ?v compare nel corpo WHERE (quindi puo' essere legata)."""
    i = q.find('WHERE'); return ('?' + v) in q[i + 5:] if i >= 0 else False
def qids(r, v='x'):
    """QID dalla variabile v. Tollerante: binding senza v/valore non-URI -> anomalia e saltato; risposta senza 'results' -> None."""
    if not isinstance(r, dict) or 'results' not in r: return None
    out = []
    for b in r['results'].get('bindings', []):
        val = (b.get(v) or {}).get('value') if isinstance(b, dict) else None
        if not val: anom("binding senza variabile '%s': %s" % (v, list(b)[:5] if isinstance(b, dict) else type(b).__name__)); continue
        out.append(val.rsplit('/', 1)[-1])
    return out
MCU = '?u rdfs:label "Marvel Cinematic Universe"@en .'
GROUPS = {
  # elementi dichiarati nell'universo di finzione MCU (personaggi, oggetti, organizzazioni, luoghi, specie, eventi...)
  'universo_MCU': 'SELECT DISTINCT ?x WHERE { %s ?x wdt:P1080 ?u . }' % MCU,
  # opere della franchise MCU (film, serie, ...) via franchise (P8345) o parte-di (P179)
  'opere_MCU': 'SELECT DISTINCT ?x WHERE { %s { ?x wdt:P8345 ?u } UNION { ?x wdt:P179 ?u } }' % MCU,
  # interpreti: cast (P161) delle opere MCU
  'interpreti_MCU': 'SELECT DISTINCT ?x WHERE { %s ?w wdt:P8345 ?u . ?w wdt:P161 ?x . ?x wdt:P31 wd:Q5 }' % MCU,
  # creatori: regia (P57), sceneggiatura (P58), creatore (P170) delle opere o dei personaggi MCU
  'creatori_MCU': 'SELECT DISTINCT ?x WHERE { %s { ?w wdt:P8345 ?u . ?w wdt:P57 ?x } UNION { ?w wdt:P8345 ?u . ?w wdt:P58 ?x } UNION { ?c wdt:P1080 ?u . ?c wdt:P170 ?x . ?x wdt:P31 wd:Q5 } }' % MCU,
}
KEEP = ('P31', 'P279', 'P1080', 'P8345', 'P179', 'P175', 'P170', 'P161', 'P57', 'P58', 'P106', 'P495', 'P577', 'P580')
def claim_ids(cl, p):
    out = []
    for c in cl.get(p, []):
        v = c.get('mainsnak', {}).get('datavalue', {}).get('value')
        if isinstance(v, dict) and 'id' in v: out.append(v['id'])
    return out
def fetch_entities(ids, props):
    res = {}; ids = list(ids); falliti = []
    for i in range(0, len(ids), 50):
        blk = ids[i:i + 50]
        r = get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&maxlag=5&props=%s&languages=%s&sitefilter=enwiki|itwiki&ids=%s' % (props, LANGS, '|'.join(blk)))
        if 'entities' in r: res.update(r['entities'])
        else: falliti.append(blk)
        time.sleep(0.6)
    for blk in falliti:  # un secondo giro a blocchi piu' piccoli
        for j in range(0, len(blk), 10):
            r = get('https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&maxlag=5&props=%s&languages=%s&sitefilter=enwiki|itwiki&ids=%s' % (props, LANGS, '|'.join(blk[j:j + 10])))
            if 'entities' in r: res.update(r['entities'])
            else: anom('blocco entita non recuperato: %s..' % blk[j])
            time.sleep(1)
    return res
def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 10**9
    man = {'avvio': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'gruppi': {}}; ANOM.clear()
    membri = {}
    for g, q in GROUPS.items():
        ids = qids(sparql(q))
        man['gruppi'][g] = {'ok': ids is not None, 'n': len(ids) if ids else 0}
        for x in (ids or [])[:mx]: membri.setdefault(x, []).append(g)
    ents = fetch_entities(membri, 'labels|aliases|descriptions|claims|sitelinks')
    refs = set(); rec = {}
    for q, e in ents.items():
        if 'missing' in e: continue
        cl = e.get('claims', {}); c = {p: claim_ids(cl, p) for p in KEEP if p in cl}
        for p in ('P31', 'P279', 'P1080', 'P8345', 'P179', 'P175', 'P170', 'P106'): refs.update(c.get(p, []))
        rec[q] = {'q': q, 'g': membri.get(q, []),
                  'l': {k: v['value'] for k, v in e.get('labels', {}).items()},
                  'd': {k: v['value'] for k, v in e.get('descriptions', {}).items()},
                  'a': {k: [a['value'] for a in v] for k, v in e.get('aliases', {}).items()},
                  'sl': {k: v['title'] for k, v in e.get('sitelinks', {}).items()}, 'c': c}
    lab = fetch_entities(sorted(refs - set(rec)), 'labels')
    etich = {q: (v.get('labels', {}).get('en', {}).get('value')) for q, v in lab.items()}
    for q, r in rec.items(): etich.setdefault(q, r['l'].get('en'))
    man['anomalie'] = ANOM[:200]; man['entita'] = len(rec); man['etichette_riferimenti'] = len(etich); man['fine'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    json.dump({'fonte': 'Wikidata (CC0)', 'recuperato': man['fine'], 'entita': rec, 'etichette': etich}, open(out / 'w1_wikidata.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(man, open(out / 'w1_manifest.json', 'w'), indent=1)
    print(json.dumps(man))
    sys.exit(0 if any(g['ok'] for g in man['gruppi'].values()) and rec else 1)
if __name__ == '__main__': main()
