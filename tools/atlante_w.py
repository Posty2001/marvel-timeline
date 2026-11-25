#!/usr/bin/env python3
"""A3.2 – Visual Asset Engine 2.0: definizione dell'ONDATA 1 (campione di 40 identità: 10 del pilota + 30 nuove) e candidati di scena.
Modi:
  --meta                 (offline) scrive data/atlante/engine/wave1.json: identità, prompt visivi, famiglie di varianti, titoli con id TMDB (da tmdbMap verificata)
  --pilota               (offline) converte candidati.json del pilota nei file per identità atlante2/data/pilot/c/<id>.json (con titoli ambigui marcati)
  --candidati --out DIR  (TMDB, chiave solo da variabili d'ambiente) scarica i SOLI METADATI delle immagini (percorsi CDN, dimensioni, voti) per le 30 identità nuove
Famiglie: identità dello stesso hub multiversale (varianti): un titolo che compare in due o più varianti della famiglia è «ambiguo» (cond=true) e non entra mai nell'automatico.
I prompt visivi sono ipotesi di lavoro del motore (non dati dell'Atlante)."""
import os, sys, json, time, argparse, glob, urllib.request, urllib.parse, urllib.error
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import atlante_numeri as N
OUT = os.path.join(ROOT, 'atlante2/data/pilot/c'); WAVE = os.path.join(ROOT, 'data/atlante/engine/wave1.json')
PILOTA = ['id-iron-man', 'id-thor', 'id-loki', 'id-peter-parker-mcu', 'id-peter-parker-raimi', 'id-peter-parker-garfield', 'id-wolverine', 'id-wade-wilson-deadpool', 'id-wanda-maximoff', 'id-thanos']
PR = {  # prompt visivo per identità (costume/tratto iconico); nome generico se non elencato
 'id-iron-man': 'Iron Man in red and gold armor', 'id-thor': 'Thor with long blond hair holding a hammer', 'id-loki': 'Loki in a green and gold horned helmet',
 'id-peter-parker-mcu': 'Spider-Man in a red and blue suit', 'id-peter-parker-raimi': 'Spider-Man in a red and blue suit', 'id-peter-parker-garfield': 'Spider-Man in a red and blue suit',
 'id-wolverine': 'Wolverine with metal claws', 'id-wade-wilson-deadpool': 'Deadpool in a red mask and suit with katanas', 'id-wanda-maximoff': 'Scarlet Witch with red magic energy',
 'id-thanos': 'Thanos, a giant purple alien with a golden gauntlet',
 'id-hulk': 'the Hulk, a giant green muscular monster', 'id-steve-rogers-capitan-america': 'Captain America in a blue suit with a round star shield', 'id-natasha-romanoff': 'Black Widow in a black tactical suit',
 'id-matt-murdock-daredevil': 'Daredevil in a masked suit with horns', 'id-bucky-barnes-soldato-d-inverno': 'the Winter Soldier with a metal arm and tactical gear', 'id-sam-wilson-capitan-america': 'Falcon with mechanical wings',
 'id-scott-lang-ant-man': 'Ant-Man in a red and black suit with a helmet', 'id-rocket': 'Rocket, a talking raccoon with a gun', 'id-peter-quill-star-lord': 'Star-Lord with a red jacket and a helmet mask',
 'id-gamora': 'Gamora, a green-skinned woman warrior', 'id-nebula': 'Nebula, a blue-skinned cyborg woman', 'id-drax': 'Drax, a muscular gray-skinned warrior with red scars',
 'id-t-challa-black-panther': 'Black Panther in a black suit with a panther mask', 'id-stephen-strange': 'Doctor Strange with a red cloak casting magic', 'id-clint-barton': 'Hawkeye with a bow and arrow',
 'id-carol-danvers-captain-marvel': 'Captain Marvel in a blue and red suit glowing with energy', 'id-james-rhodes-war-machine': 'War Machine in gray armor', 'id-nick-fury': 'Nick Fury with an eyepatch and a long black coat',
 'id-visione': 'Vision, a red-faced android with a yellow gem on the forehead', 'id-magneto': 'Magneto in a helmet controlling metal', 'id-charles-xavier-fox': 'Professor X, a bald man in a wheelchair',
 'id-mystica': 'Mystique, a blue-skinned shapeshifter', 'id-ciclope': 'Cyclops with a red visor', 'id-jean-grey-fenice': 'Jean Grey with red hair and glowing fire',
 'id-reed-richards': 'Mr. Fantastic in a blue Fantastic Four suit', 'id-sue-storm': 'Invisible Woman in a blue Fantastic Four suit', 'id-johnny-storm-human-torch': 'Human Torch engulfed in flames',
 'id-ben-grimm': 'The Thing, a rocky orange creature', 'id-victor-von-doom': 'Doctor Doom in a metal mask and green cloak', 'id-harry-osborn-green-goblin': 'the Goblin in green armor with a mask'}
NUOVE = [i for i in PR if i not in PILOTA]

def dossier():
    D = {}
    for x in glob.glob(os.path.join(ROOT, 'atlante2/data/d/*.json')): D.update(json.load(open(x, encoding='utf-8')))
    return D
def famiglie():
    ide = json.load(open(os.path.join(ROOT, 'data/atlante/identita.json'), encoding='utf-8')); F = {}
    for h in ide['hub']:
        for m in h['membri']:
            F.setdefault(m, set()).update(h['membri'])
    return F
def meta():
    c = N.carica(); mp, v2 = c['tmdbMap'], c['vis2id']; D = dossier(); idx = json.load(open(os.path.join(ROOT, 'atlante2/data/index.json'), encoding='utf-8')); BY = {v['i']: v for v in idx['voci']}; F = famiglie()
    ids = PILOTA + NUOVE; out = []
    tit = {}
    for i in ids:
        ts = []
        for a in D.get(i, {}).get('app') or []:
            it = v2.get(a[0], a[0]); e = mp.get(it)
            if e and e.get('id'): ts.append({'num': a[0], 'item': it, 'tmdb_id': e['id'], 'tipo': e['t'], 'titolo': a[1]})
        tit[i] = ts
    for i in ids:
        fam = sorted(F.get(i, set()) & set(ids) - {i}); amb = sorted({t['num'] for t in tit[i]} & {t['num'] for o in fam for t in tit.get(o, [])})
        fam_all = sorted(F.get(i, set()) - {i})  # anche varianti fuori campione
        amb_all = set(amb)
        for o in fam_all:
            if o in ids: continue
            for a in D.get(o, {}).get('app') or []:
                if a[0] in {t['num'] for t in tit[i]}: amb_all.add(a[0])
        out.append({'id': i, 'nome': BY[i]['n'], 'prompt': PR[i], 'pilota': i in PILOTA, 'famiglia': fam_all, 'titoli': tit[i], 'ambigui': sorted(amb_all)})
    os.makedirs(os.path.dirname(WAVE), exist_ok=True)
    json.dump({'schema': 1, 'ondata': 1, 'identita': out}, open(WAVE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('wave1:', len(out), 'identità;', sum(len(o['titoli']) for o in out), 'titoli-identità;', sum(len(o['ambigui']) for o in out), 'titoli ambigui')
def pilota():
    W = json.load(open(WAVE, encoding='utf-8')); A = {o['id']: o for o in W['identita']}; J = json.load(open(os.path.join(ROOT, 'atlante2/data/pilot/candidati.json'), encoding='utf-8')); os.makedirs(OUT, exist_ok=True)
    for i in J['identita']:
        w = A.get(i['id']); i = dict(i); i['ambigui'] = (w or {}).get('ambigui', []); i['wave'] = 1
        json.dump(i, open(os.path.join(OUT, i['id'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('convertite', len(J['identita']), 'identità pilota in', OUT)
API = 'https://api.themoviedb.org/3'
def get(path, **q):
    tok = os.environ.get('TMDB_READ_TOKEN'); key = os.environ.get('TMDB_API_KEY'); h = {'Accept': 'application/json'}
    if not tok and not key: sys.exit('Imposta TMDB_READ_TOKEN o TMDB_API_KEY (mai nel repository).')
    if tok: h['Authorization'] = 'Bearer ' + tok
    else: q['api_key'] = key
    url = API + path + '?' + urllib.parse.urlencode(q)
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and k < 3: time.sleep(2 + 3 * k); continue
            if e.code == 404: return None
            raise
def candidati(out):
    W = json.load(open(WAVE, encoding='utf-8')); cache = {}; os.makedirs(out, exist_ok=True); n = 0
    for o in W['identita']:
        if o['pilota']: continue
        imm = []; tl = []
        for t in o['titoli']:
            k = (t['tipo'], t['tmdb_id'])
            if k not in cache:
                d = get('/%s/%s/images' % (t['tipo'], t['tmdb_id']), include_image_language='null,en'); cache[k] = (d or {}).get('backdrops') or []; n += 1
            bd = sorted(cache[k], key=lambda b: -(b.get('vote_average') or 0))[:30]
            tl.append({'num': t['num'], 'titolo_atteso': t['titolo'], 'tipo': t['tipo'], 'tmdb_id': t['tmdb_id'], 'titolo_tmdb': t['titolo'], 'verificato': True, 'corretto_da_mappa': False})
            for b in bd: imm.append({'p': b['file_path'], 'w': b['width'], 'h': b['height'], 'v': round(b.get('vote_average') or 0, 2), 'n': b.get('vote_count') or 0, 'tag': False, 'src': 'backdrop', 'num': t['num']})
        json.dump({'id': o['id'], 'nome': o['nome'], 'nota': '', 'attore': {'nome': ''}, 'titoli': tl, 'immagini': imm, 'ambigui': o['ambigui'], 'wave': 1}, open(os.path.join(out, o['id'] + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    json.dump({'richieste_api': n, 'identita': [o['id'] for o in W['identita'] if not o['pilota']]}, open(os.path.join(out, '_indice.json'), 'w'), ensure_ascii=False); print('candidati scritti; richieste TMDB:', n)
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--meta', action='store_true'); ap.add_argument('--pilota', action='store_true'); ap.add_argument('--candidati', action='store_true'); ap.add_argument('--out', default='w1-out'); a = ap.parse_args()
    if a.meta: meta()
    if a.pilota: pilota()
    if a.candidati: candidati(a.out)
