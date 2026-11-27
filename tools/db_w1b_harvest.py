#!/usr/bin/env python3
"""W1.b raccolta di FATTI da MCU Wiki e Marvel Database (Fandom, MediaWiki Action API). Si esegue in Actions (rete).
Rispetto di licenza/accesso: testo CC BY-SA 3.0 (fandom.com/Licensing) -> si conservano SOLO fatti strutturati (parametri di infobox, nomi di poteri/equipaggiamento/...),
mai prosa ne' wikitext; attribuzione e URL per ogni pagina. API ufficiale di MediaWiki, User-Agent dichiarato, maxlag, >=1,2 s tra le richieste, nessun login, solo lettura.
Bersagli: voci in staging + canon W1 non attori/creatori/opere. Uso: python3 tools/db_w1b_harvest.py <out_dir> [--max N]"""
import json, sys, time, pathlib, urllib.request, urllib.parse, urllib.error
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_wiki_parse as P
R = pathlib.Path(__file__).resolve().parent.parent
E = R/'data/atlante/espansione'
UA = 'TVA-Archives-W1b/1.0 (progetto personale non commerciale, sola lettura; https://github.com/Posty2001/marvel-timeline)'
WIKI = {'mcuwiki': 'https://marvelcinematicuniverse.fandom.com/api.php', 'marveldb': 'https://marvel.fandom.com/api.php'}
PAUSA = 1.2
ERRLOG = []; ERR = object()
def api(base, params, tries=4):
    """MediaWiki API: tentativi limitati; 429/503 rispettano Retry-After; 4xx non si ripetono. Errore -> {'errore':..} e annotazione (mai silenzioso)."""
    url = base + '?' + urllib.parse.urlencode(dict(params, format='json', formatversion='2', maxlag='5'))
    last = ''
    for i in range(tries):
        try:
            time.sleep(PAUSA)
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=90))
            if isinstance(r, dict) and r.get('error', {}).get('code') == 'maxlag': last = 'maxlag'; time.sleep(10 * (i + 1)); continue
            return r
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code in (429, 503):
                try: w = min(120, int(e.headers.get('Retry-After', '') or 0))
                except Exception: w = 0
                time.sleep(max(w, 10 * (i + 1)))
            elif 500 <= e.code < 600: time.sleep(5 * (i + 1))
            else: break
        except Exception as e:
            last = str(e)[:150]; time.sleep(5 * (i + 1))
    ERRLOG.append('API fallita (%s): %s' % (last, str(params.get('titles') or params.get('srsearch'))[:60]))
    return {'errore': last}
def bersagli():
    out = []
    for f in ('staging/w1_staging.jsonl', 'canon/w1_mcu.jsonl'):
        for l in (E/f).read_text().splitlines():
            r = json.loads(l)
            t = r.get('tipo'); nome = r.get('nome')
            if not nome or t in ('attore', 'creatore', 'opera', 'episodio', None): continue
            if 'motivo' in r and 'una sola fonte' not in r['motivo']: continue
            q = r.get('q') or r.get('ids_esterni', {}).get('wikidata')
            out.append({'q': q, 'nome': nome, 'tipo': t})
    seen = set(); res = []
    for b in out:
        if b['q'] not in seen: seen.add(b['q']); res.append(b)
    return res
def pagine(wiki, titoli):
    """Per ogni titolo trovato: categorie + fatti. Batch da 20 titoli (contenuto), redirect risolti."""
    out = {}
    base = WIKI[wiki]
    for i in range(0, len(titoli), 20):
        blocco = titoli[i:i + 20]
        r = api(base, {'action': 'query', 'titles': '|'.join(blocco), 'redirects': 1, 'prop': 'revisions|categories', 'rvprop': 'content|ids', 'rvslots': 'main', 'cllimit': 'max'})
        if 'errore' in r: return None if not out else out
        q = r.get('query', {})
        rid = {x['from']: x['to'] for x in q.get('redirects', [])}; norm = {x['from']: x['to'] for x in q.get('normalized', [])}
        by = {p['title']: p for p in q.get('pages', [])}
        for t in blocco:
            tt = rid.get(norm.get(t, t), norm.get(t, t)); p = by.get(tt)
            if not p or p.get('missing'): out[t] = None; continue
            rev = (p.get('revisions') or [{}])[0]; wt = (rev.get('slots', {}).get('main', {}).get('content')) or ''
            cats = [c['title'].split(':', 1)[-1] for c in p.get('categories', [])] or P.categorie_wikitext(wt)
            out[t] = {'titolo': p['title'], 'pageid': p.get('pageid'), 'revid': rev.get('revid'), 'categorie': cats[:40], 'infobox': P.infobox(wt), 'sezioni': P.sezioni(wt),
                      'disambigua': ('disambig' in wt[:600].lower()) or any('disambiguation' in c.lower() for c in cats), 'url': 'https://%s/wiki/%s' % (base.split('/')[2], urllib.parse.quote(p['title'].replace(' ', '_')))}
    return out
def cerca_marveldb(nome):
    r = api(WIKI['marveldb'], {'action': 'query', 'list': 'search', 'srsearch': '"%s" Earth-199999' % nome, 'srnamespace': 0, 'srlimit': 5})
    if 'errore' in r: return ERR
    for x in r.get('query', {}).get('search', []):
        if x['title'].endswith('(Earth-199999)'): return x['title']
    return None
def main():
    """Robusta e riprendibile: checkpoint w1b_checkpoint.json (pagine gia' lette per wiki/titolo e ricerche Marvel Database) ripreso se presente in <out_dir>;
    ogni blocco e' isolato, errori/anomalie nel manifest, risultati parziali sempre salvati."""
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); ANOM = []
    mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 10**9
    ck = {'mcuwiki': {}, 'marveldb': {}, 'ricerca': {}}
    if (out/'w1b_checkpoint.json').exists():
        try: ck = json.load(open(out/'w1b_checkpoint.json')); print('ripresa da checkpoint')
        except Exception as e: ANOM.append('checkpoint illeggibile: %s' % e)
    def salva_ck(): json.dump(ck, open(out/'w1b_checkpoint.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    B = bersagli()[:mx]; man = {'avvio': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'bersagli': len(B)}
    def fase(wiki, titoli):
        da = [t for t in titoli if t not in ck[wiki]]
        for i in range(0, len(da), 20):
            blocco = da[i:i + 20]
            try:
                r = pagine(wiki, blocco)
                if r is None: continue
                ck[wiki].update(r)
            except Exception as e: ANOM.append('%s blocco %s: %s' % (wiki, blocco[0], str(e)[:100]))
            salva_ck()
    fase('mcuwiki', [b['nome'] for b in B])
    for b in B:
        if b['tipo'] in ('identita', 'entita-cosmica', 'specie') and b['nome'] not in ck['ricerca']:
            try:
                t = cerca_marveldb(b['nome'])
                if t is not ERR: ck['ricerca'][b['nome']] = t
            except Exception as e: ANOM.append('ricerca %s: %s' % (b['nome'], str(e)[:100]))
    salva_ck()
    titoli = {n: t for n, t in ck['ricerca'].items() if t}
    fase('marveldb', sorted(set(titoli.values())))
    mcu = ck['mcuwiki']; mdb = ck['marveldb']
    man['mcuwiki_trovate'] = sum(1 for v in mcu.values() if v); man['marveldb_cercati'] = len(ck['ricerca']); man['marveldb_trovate'] = sum(1 for v in mdb.values() if v)
    man['non_ottenuti'] = sum(1 for b in B if b['nome'] not in mcu)
    man['anomalie'] = (ANOM + ERRLOG)[:300]; man['completa'] = not man['non_ottenuti'] and not ANOM and not ERRLOG
    json.dump({'fonte': 'Marvel Cinematic Universe Wiki (Fandom), CC BY-SA 3.0, solo fatti strutturati', 'pagine': mcu}, open(out/'w1b_mcuwiki.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'fonte': 'Marvel Database (Fandom), CC BY-SA 3.0, solo fatti strutturati', 'ricerca': titoli, 'pagine': mdb}, open(out/'w1b_marveldb.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    man['fine'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()); json.dump(man, open(out/'w1b_manifest.json', 'w'), indent=1); print(json.dumps({k: v for k, v in man.items() if k != 'anomalie'}), '| anomalie', len(man['anomalie']))
    sys.exit(0 if man['mcuwiki_trovate'] or man['marveldb_trovate'] else 1)
if __name__ == '__main__': main()
