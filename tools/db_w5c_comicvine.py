#!/usr/bin/env python3
"""W5.c / W6.b: ranking di rilevanza e ID dai fumetti Marvel tramite l'API GRATUITA di Comic Vine (chiave personale, solo nei Secret di GitHub: COMICVINE_API_KEY; nessuna fatturazione).
Si conservano SOLO fatti minimi: ID Comic Vine, nome, n. di albi (count_of_issue_appearances), primo albo (nome/data), URL: nessuna descrizione/testo/immagine (decisione D: consultazione e ID).
Limiti rispettati: <= 1 richiesta/secondo, User-Agent dichiarato, pagine da 100, riprendibile (cv2_checkpoint.json). Uso: python3 tools/db_w5c_comicvine.py <out_dir>   (rete + chiave -> Actions)"""
import json, os, sys, time, pathlib, urllib.request, urllib.parse
UA = 'TVA-Archives-CV/1.0 (progetto personale non commerciale; https://github.com/Posty2001/marvel-timeline)'
KEY = os.environ.get('COMICVINE_API_KEY', '')
MARVEL = 31   # id editore Marvel su Comic Vine
RISORSE = {   # risorsa -> (campi, massimo elementi scorsi): il filtro per editore NON e' supportato dall'API su queste risorse: si scorre per rilevanza e si tiene solo Marvel lato client
    'characters': ('id,name,count_of_issue_appearances,first_appeared_in_issue,site_detail_url,real_name,publisher', 12000),
    'teams': ('id,name,count_of_issue_appearances,first_appeared_in_issue,site_detail_url,publisher', 4000),
    'story_arcs': ('id,name,count_of_issues,first_appeared_in_issue,site_detail_url,publisher', 3000),
    'volumes': ('id,name,count_of_issues,start_year,site_detail_url,publisher', 8000)}
def api(risorsa, params, tries=4):
    url = 'https://comicvine.gamespot.com/api/%s/?%s' % (risorsa, urllib.parse.urlencode(dict(params, api_key=KEY, format='json')))
    last = ''
    for i in range(tries):
        try:
            time.sleep(1.1); r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60))
            if r.get('status_code') == 1: return r
            last = str(r.get('error'))[:80]
            if r.get('status_code') in (100, 101): break   # chiave non valida / oggetto non trovato: inutile riprovare
        except Exception as e: last = str(e)[:80]
        time.sleep(5 * (i + 1))
    return {'errore': last}
def main():
    if not KEY: print('COMICVINE_API_KEY assente: nessuna raccolta (nessun errore)'); sys.exit(0)
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); ckf = out / 'cv2_checkpoint.json'; ck = {}
    if ckf.exists():
        try: ck = json.load(open(ckf))
        except Exception: ck = {}
    anom = []
    for ris, (campi, mx) in RISORSE.items():
        got = ck.setdefault(ris, {'off': 0, 'fine': False, 'v': []})
        while not got['fine'] and got['off'] < mx:
            p = {'field_list': campi, 'limit': 100, 'offset': got['off']}
            p['sort'] = 'count_of_issue_appearances:desc' if ris in ('characters', 'teams') else 'count_of_issues:desc'
            r = api(ris, p)
            if 'errore' in r: anom.append('%s offset %d: %s' % (ris, got['off'], r['errore'])); break
            res = r.get('results') or []
            for x in res:
                if (x.get('publisher') or {}).get('id') != MARVEL: continue
                fi = x.get('first_appeared_in_issue') or {}
                got['v'].append({'id': x['id'], 'n': x.get('name'), 'c': x.get('count_of_issue_appearances') or x.get('count_of_issues'), 'fa': fi.get('name'), 'u': x.get('site_detail_url'), 'rn': x.get('real_name'), 'y': x.get('start_year')})
            got['off'] += len(res); got['visti'] = got.get('visti', 0) + len(res)
            if len(res) < 100 or got['off'] >= r.get('number_of_total_results', 0): got['fine'] = True
            json.dump(ck, open(ckf, 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'fonte': 'Comic Vine API (chiave gratuita, uso non commerciale; solo ID e numeri)', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'risorse': {k: v['v'] for k, v in ck.items()}, 'anomalie': anom}, open(out / 'cv2_marvel.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(json.dumps({k: len(v['v']) for k, v in ck.items()}), anom[:3]); sys.exit(0)
if __name__ == '__main__': main()
