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
    # fase risorse narrative extra (W8): solo ID e nome di oggetti, origini (specie), concetti e luoghi: seconda fonte per nome (nessun testo); niente filtro editore (non disponibile)
    ef = out / 'cv_extra_checkpoint.json'; ex = {}
    if ef.exists():
        try: ex = json.load(open(ef))
        except Exception: ex = {}
    for ris, mx in (('objects', 70000), ('origins', 2000), ('concepts', 25000), ('locations', 40000)):
        got = ex.setdefault(ris, {'off': 0, 'fine': False, 'v': []})
        while not got['fine'] and got['off'] < mx:
            r = api(ris, {'field_list': 'id,name', 'limit': 100, 'offset': got['off']})
            if 'errore' in r: anom.append('%s offset %d: %s' % (ris, got['off'], r['errore'])); break
            res = r.get('results') or []
            got['v'] += [[x['id'], x.get('name')] for x in res if x.get('name')]
            got['off'] += len(res)
            if len(res) < 100 or got['off'] >= r.get('number_of_total_results', 0): got['fine'] = True
            if (got['off'] // 100) % 20 == 0: json.dump(ex, open(ef, 'w'), separators=(',', ':'))
        json.dump(ex, open(ef, 'w'), separators=(',', ':'))
    json.dump({'fonte': 'Comic Vine API (chiave gratuita): solo ID e nome', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'risorse': {k: v['v'] for k, v in ex.items()}}, open(out / 'cv_extra.json', 'w'), separators=(',', ':'))
    # fase relazioni (W8): amici/nemici/team dei personaggi indicati in data/atlante/espansione/cv_rel_bersagli.json (solo ID e nomi; nessun testo)
    bf = pathlib.Path(__file__).resolve().parent.parent / 'data/atlante/espansione/cv_rel_bersagli.json'
    if bf.exists():
        ids = json.load(open(bf))['ids']; rf = out / 'cv_rel_checkpoint.json'; rel = {}
        if rf.exists():
            try: rel = json.load(open(rf))
            except Exception: rel = {}
        for n, cid in enumerate(ids):
            if str(cid) in rel: continue
            try:
                time.sleep(1.1)
                u = 'https://comicvine.gamespot.com/api/character/4005-%d/?%s' % (cid, urllib.parse.urlencode({'api_key': KEY, 'format': 'json', 'field_list': 'id,character_friends,character_enemies,teams'}))
                r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=60))
                if r.get('status_code') != 1: anom.append('rel %d: %s' % (cid, str(r.get('error'))[:60])); continue
                x = r['results']; rel[str(cid)] = {'f': [y['id'] for y in x.get('character_friends') or []], 'e': [y['id'] for y in x.get('character_enemies') or []], 't': [y['id'] for y in x.get('teams') or []]}
            except Exception as e: anom.append('rel %d: %s' % (cid, str(e)[:60])); time.sleep(5)
            if n % 25 == 0: json.dump(rel, open(rf, 'w'), separators=(',', ':'))
        json.dump(rel, open(rf, 'w'), separators=(',', ':'))
        json.dump({'fonte': 'Comic Vine API (chiave gratuita): solo ID di amici/nemici/team', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'personaggi': rel}, open(out / 'cv_rel.json', 'w'), separators=(',', ':'))
    json.dump({'fonte': 'Comic Vine API (chiave gratuita, uso non commerciale; solo ID e numeri)', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'risorse': {k: v['v'] for k, v in ck.items()}, 'anomalie': anom}, open(out / 'cv2_marvel.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print(json.dumps({k: len(v['v']) for k, v in ck.items()}), anom[:3]); sys.exit(0)
if __name__ == '__main__': main()
