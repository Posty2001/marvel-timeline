#!/usr/bin/env python3
"""W5.b: fatti da Marvel Database (Fandom, CC BY-SA 3.0; solo parametri di infobox brevi, mai prosa) per le entita' dei fumetti (Earth-616) di W5 (canon + staging «una sola fonte»).
Seconda fonte indipendente per i fumetti (D12): pagina coerente per titolo/categoria. Stesse regole di rispetto di W1.b (API MediaWiki, User-Agent, pause, nessun login, sola lettura).
Riprendibile (w5b_checkpoint.json), anomalie nel manifest. Uso: python3 tools/db_w5b_harvest.py <out_dir> [--max N]   (rete -> Actions)"""
import json, sys, time, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import db_w1b_harvest as B
E = B.E; ERR = B.ERR
def bersagli(max_n=10**9):
    out, vis = [], set()
    for f in ('canon/w5_fumetti_entita.jsonl', 'staging/w5_staging.jsonl'):
        p = E / f
        if not p.exists(): continue
        for l in p.read_text().splitlines():
            if not l.strip(): continue
            r = json.loads(l); t, n = r.get('tipo'), r.get('nome')
            if not n or t in ('attore', 'creatore', 'opera', 'episodio', 'evento', None): continue
            if 'motivo' in r and 'una sola fonte' not in r['motivo']: continue
            if n in vis: continue
            vis.add(n); out.append({'nome': n, 'tipo': t})
    return out[:max_n]
def cerca(nome):
    r = B.api(B.WIKI['marveldb'], {'action': 'query', 'list': 'search', 'srsearch': '"%s" Earth-616' % nome, 'srnamespace': 0, 'srlimit': 5})
    if 'errore' in r: return ERR
    for x in r.get('query', {}).get('search', []):
        if x['title'].endswith('(Earth-616)'): return x['title']
    return None
def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); anom = []
    mx = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 10**9
    ck = {'v': 1, 'pagine': {}, 'ricerca': {}}; ckf = out / 'w5b_checkpoint.json'
    if ckf.exists():
        try: ck = json.load(open(ckf)); print('ripresa')
        except Exception as e: anom.append('checkpoint illeggibile: %s' % e)
    Bs = bersagli(mx); man = {'avvio': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'bersagli': len(Bs)}
    # 1) titolo diretto «Nome (Earth-616)» in blocchi da 20; 2) ricerca solo per i mancanti di tipo identita/organizzazione/entita-cosmica
    diretti = {b['nome']: b['nome'] + ' (Earth-616)' for b in Bs}
    da = [t for t in diretti.values() if t not in ck['pagine']]
    for i in range(0, len(da), 20):
        blocco = da[i:i + 20]
        try:
            r = B.pagine('marveldb', blocco, None)
            if r is not None: ck['pagine'].update(r)
        except Exception as e: anom.append('blocco %s: %s' % (blocco[0], str(e)[:100]))
        json.dump(ck, open(ckf, 'w'), ensure_ascii=False, separators=(',', ':'))
    for b in Bs:
        t = diretti[b['nome']]
        if ck['pagine'].get(t): ck['ricerca'][b['nome']] = t; continue
        if b['tipo'] in ('identita', 'organizzazione', 'entita-cosmica') and b['nome'] not in ck['ricerca']:
            try:
                s = cerca(b['nome'])
                if s is not ERR: ck['ricerca'][b['nome']] = s
            except Exception as e: anom.append('ricerca %s: %s' % (b['nome'], str(e)[:100]))
    alt = sorted({t for t in ck['ricerca'].values() if t and t not in ck['pagine']})
    for i in range(0, len(alt), 20):
        r = B.pagine('marveldb', alt[i:i + 20], None)
        if r: ck['pagine'].update(r)
        json.dump(ck, open(ckf, 'w'), ensure_ascii=False, separators=(',', ':'))
    pp = {n: t for n, t in ck['ricerca'].items() if t}
    pagine = {t: v for t, v in ck['pagine'].items() if v}
    man.update({'trovate': len(pp), 'pagine': len(pagine), 'con_infobox': sum(1 for v in pagine.values() if v['infobox']), 'chiavi': collections.Counter(k for v in pagine.values() for k in v['infobox']).most_common(40),
                'anomalie': (anom + B.ERRLOG)[:300], 'fine': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
    json.dump({'fonte': 'Marvel Database (Fandom), CC BY-SA 3.0, solo fatti strutturati', 'ricerca': pp, 'pagine': pagine}, open(out / 'w5b_marveldb.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(man, open(out / 'w5b_manifest.json', 'w'), indent=1); print(json.dumps({k: v for k, v in man.items() if k not in ('anomalie', 'chiavi')}))
    sys.exit(0 if pagine else 1)
if __name__ == '__main__': main()
