#!/usr/bin/env python3
"""A3.2 – Visual Asset Engine 2.0 (ondata 1: 40 identità). Gira su GitHub Actions (CPU, 0 €). SOLO METADATI in uscita; le immagini restano nel runner.
Novità rispetto al prototipo:
 - il punteggio principale è quello del RITAGLIO 3:4 (ciò che il ritratto mostrerà davvero), non dell'intera scena
 - ensemble CLIP (ritagli) + SigLIP (scena intera) e consenso `ck`
 - contrasto con TUTTE le identità dell'ondata e con negativi (gruppo di eroi, folla, testo, volto senza costume, scena buia…): premia personaggio isolato e costume iconico
 - qualità: nitidezza, esposizione, risoluzione del ritaglio (altezza ≥ 700 px sull'originale)
 - titoli ambigui tra varianti della stessa famiglia (hub) esclusi dall'automatico; una scena non viene mai proposta a due identità
 - confidenza: se meno di 3 ritagli superano la soglia → `conf: bassa` e fino a 10 proposte (altrimenti 5)
Nessun riconoscimento facciale degli attori. Uso: python3 tools/atlante_engine2.py --out DIR [--smoke]"""
import argparse, hashlib, io, json, os, resource, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np, requests
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDN = 'https://image.tmdb.org/t/p/w780'; CACHE = '/tmp/atlante_imgs'
MODELLI = {'clip': ('ViT-B-32', 'laion2b_s34b_b79k'), 'siglip': ('ViT-B-16-SigLIP', 'webli')}
NEG = ['a landscape without people', 'a crowd of many people', 'a group of many superheroes together', 'two characters facing each other', 'a movie logo or title text',
       'a close-up of a person face without costume', 'a spaceship or a vehicle', 'an explosion or fire', 'a dark blurry scene', 'a city street at night']
MIN_W, MIN_SHARP, MIN_CROP_H, T_CLIP, T_SIG, TOPW = 1280, 40.0, 700, 5.0, 4.0, 16
SC = ((1.0, 6, 1), (0.78, 6, 2))   # (altezza finestra, posizioni orizzontali, posizioni verticali)

def sharp(im):
    g = np.asarray(im.convert('L').resize((640, 360)), dtype=np.float32); lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]; return float(lap.var())
def expo(im):
    m = float(np.asarray(im.convert('L'), dtype=np.float32).mean()) / 255.0; return max(0.0, 1 - abs(m - 0.42) / 0.42)
def dhash(im, n=8):
    g = np.asarray(im.convert('L').resize((n + 1, n), Image.BILINEAR), dtype=np.int16); return int(''.join('1' if b else '0' for b in (g[:, 1:] > g[:, :-1]).flatten()), 2)
def ham(a, b): return bin(a ^ b).count('1')
def path_of(p): return os.path.join(CACHE, hashlib.md5(p.encode()).hexdigest() + '.jpg')
def scarica(p):
    f = path_of(p)
    if os.path.exists(f): return True
    for _ in range(3):
        try:
            r = requests.get(CDN + p, timeout=30)
            if r.status_code == 200: open(f, 'wb').write(r.content); return True
        except Exception: time.sleep(1)
    return False
def rank01(v):
    v = np.asarray(v, dtype=float); o = np.argsort(np.argsort(v)); return o / max(1, len(v) - 1)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='engine2-out'); ap.add_argument('--smoke', action='store_true'); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
    import torch, open_clip
    torch.set_num_threads(os.cpu_count() or 2); T0 = time.time(); met = {'stadi_s': {}}
    W = json.load(open(os.path.join(ROOT, 'data/atlante/engine/wave1.json'), encoding='utf-8'))['identita']
    if a.smoke: W = W[:6]
    # candidati per identità
    C = {}; pools = {}
    for o in W:
        c = json.load(open(os.path.join(ROOT, 'atlante2/data/pilot/c/%s.json' % o['id']), encoding='utf-8')); C[o['id']] = c
        ok = {t['num'] for t in c['titoli'] if t.get('verificato')}; amb = set(o['ambigui'])
        pools[o['id']] = [x for x in c['immagini'] if x['num'] in ok and x['num'] not in amb and x['w'] >= MIN_W]
    uniq = sorted({x['p'] for L in pools.values() for x in L})
    if a.smoke: uniq = uniq[:150]; pools = {k: [x for x in v if x['p'] in set(uniq)] for k, v in pools.items()}
    met['candidati_totali'] = sum(len(C[i]['immagini']) for i in C); met['immagini_uniche'] = len(uniq)
    t = time.time()
    with ThreadPoolExecutor(8) as ex: okd = list(ex.map(scarica, uniq))
    met['stadi_s']['download'] = round(time.time() - t, 1); uniq = [p for p, k in zip(uniq, okd) if k]
    # qualità + dedup globale per dHash
    Q = {}; t = time.time()
    for p in uniq:
        try: im = Image.open(path_of(p)).convert('RGB')
        except Exception: continue
        s = sharp(im)
        if s >= MIN_SHARP: Q[p] = {'sharp': s, 'expo': expo(im), 'dh': dhash(im), 'w': im.size[0], 'h': im.size[1]}
    met['stadi_s']['qualita'] = round(time.time() - t, 1); met['immagini_nitide'] = len(Q)
    labels = [o['prompt'] for o in W]; lab = []
    for l in labels + NEG:
        if l not in lab: lab.append(l)
    ix = {l: k for k, l in enumerate(lab)}; E = {}; TF = {}; SCALE = {}
    for m in ('clip', 'siglip'):
        t = time.time(); name, pre = MODELLI[m]; mod, _, prep = open_clip.create_model_and_transforms(name, pretrained=pre); mod.eval(); tok = open_clip.get_tokenizer(name)
        with torch.no_grad():
            tf = mod.encode_text(tok(['a movie still of ' + l if l not in NEG else l for l in lab])); TF[m] = tf / tf.norm(dim=-1, keepdim=True)
        SCALE[m] = (float(mod.logit_scale.exp()), float(mod.logit_bias) if getattr(mod, 'logit_bias', None) is not None else None)
        def emb(ims, mod=mod, prep=prep):
            with torch.no_grad(): f = mod.encode_image(torch.stack([prep(i) for i in ims])); return f / f.norm(dim=-1, keepdim=True)
        E[m] = (mod, prep, emb); met['stadi_s']['carica_' + m] = round(time.time() - t, 1)
    def margin(m, f, ident_prompt):
        sc, b = SCALE[m]; s = (f @ TF[m].T) * sc
        if b is not None: s = s + b
        k = ix[ident_prompt]; others = torch.cat([s[:, :k], s[:, k + 1:]], dim=1); return (s[:, k] - torch.logsumexp(others, dim=1)).numpy()
    # embedding scena intera, una volta per immagine unica (entrambi i modelli)
    P = list(Q); FE = {'clip': [], 'siglip': []}
    for m in ('clip', 'siglip'):
        t = time.time(); emb = E[m][2]
        for k in range(0, len(P), 32):
            ims = [Image.open(path_of(p)).convert('RGB') for p in P[k:k + 32]]; FE[m].append(emb(ims))
        FE[m] = torch.cat(FE[m]); met['stadi_s']['scena_' + m] = round(time.time() - t, 1)
    pos = {p: k for k, p in enumerate(P)}
    # per identità
    out = {}; res = {}
    for o in W:
        iid = o['id']; t = time.time(); L = [x for x in pools[iid] if x['p'] in Q]
        # dedup nell'identità (hash)
        keep = []
        for x in sorted(L, key=lambda x: -x.get('v', 0)):
            if all(ham(Q[x['p']]['dh'], Q[k['p']]['dh']) > 6 for k in keep): keep.append(x)
        if not keep: out[iid] = {'id': iid, 'nome': o['nome'], 'conf': 'bassa', 'buoni': 0, 'proposte': []}; continue
        ii = [pos[x['p']] for x in keep]; mc = margin('clip', FE['clip'][ii], o['prompt']); ms = margin('siglip', FE['siglip'][ii], o['prompt'])
        pre = 0.6 * rank01(mc) + 0.4 * rank01(ms); top = [keep[j] for j in np.argsort(-pre)[:TOPW]]; tj = {x['p']: j for j, x in enumerate(keep)}; rows = []
        for x in top:
            im = Image.open(path_of(x['p'])).convert('RGB'); Wd, Ht = im.size; best = None
            for h0, nx, ny in SC:
                if x['h'] * h0 < MIN_CROP_H: continue
                w0 = 0.75 * h0 * Ht / Wd
                if w0 > 1: continue
                wins = [(x0, y0, w0, h0) for y0 in (np.linspace(0, 1 - h0, ny) if ny > 1 else [0.0]) for x0 in np.linspace(0, 1 - w0, nx)]
                crops = [im.crop((int(a0 * Wd), int(b0 * Ht), int((a0 + w0) * Wd), int((b0 + h0) * Ht))) for a0, b0, w0, h0 in wins]
                fw = E['clip'][2](crops); mw = margin('clip', fw, o['prompt'])
                for w, v in zip(wins, mw):
                    s = float(v) + 0.3 * w[3]
                    if best is None or s > best[0]: best = (s, w, float(v), fw[int(np.argmax(mw))])
            if best is None: continue
            q = Q[x['p']]; rows.append({'x': x, 'mw': best[2], 'win': best[1], 'ms': float(ms[tj[x['p']]]), 'mc': float(mc[tj[x['p']]]), 'sharp': q['sharp'], 'expo': q['expo'], 'f': best[3], 'ch': x['h'] * best[1][3]})
        if rows:
            r_m = rank01([r['mw'] for r in rows]); r_s = rank01([r['ms'] for r in rows]); r_q = rank01([r['sharp'] for r in rows])
            for r, a1, a2, a3 in zip(rows, r_m, r_s, r_q): r['tot'] = 0.5 * a1 + 0.2 * a2 + 0.3 * (0.5 * a3 + 0.2 * r['expo'] + 0.3 * min(1.0, r['ch'] / 1000.0))
        rows.sort(key=lambda r: -r.get('tot', 0)); buoni = sum(1 for r in rows if r['mw'] >= T_CLIP); res[iid] = {'o': o, 'rows': rows, 'buoni': buoni, 'sec': round(time.time() - t, 1)}
        print(iid, 'candidati', len(L), 'dopo dedup', len(keep), 'ritagli buoni', buoni, round(time.time() - t, 1), 's', flush=True)
    # selezione con diversità e unicità tra identità
    owner = {}
    for iid, R in res.items():
        for r in R['rows']:
            p = r['x']['p']
            if p not in owner or r['mw'] > owner[p][1]: owner[p] = (iid, r['mw'])
    for o in W:
        iid = o['id']
        if iid not in res: continue
        R = res[iid]; alta = R['buoni'] >= 3; nmax = 5 if alta else 10; sel = []; per = {}
        for lim in (2, 3, 4):
            for r in R['rows']:
                if len(sel) >= nmax: break
                p = r['x']['p']
                if r in sel or owner.get(p, (iid,))[0] != iid or per.get(r['x']['num'], 0) >= lim: continue
                if lim == 2 and any(float(r['f'] @ s['f']) > 0.94 for s in sel): continue
                sel.append(r); per[r['x']['num']] = per.get(r['x']['num'], 0) + 1
            if len(sel) >= min(nmax, 3 if alta else 6): break
        props = []
        for k, r in enumerate(sel):
            x0, y0, w0, h0 = r['win']
            props.append({'rk': k + 1, 'p': r['x']['p'], 'w': r['x']['w'], 'h': r['x']['h'], 'num': r['x']['num'], 'sc': round(r['tot'], 3), 'm': round(r['mw'], 2), 'ms': round(r['ms'], 2), 'ck': 1 if (r['mw'] >= T_CLIP and r['ms'] >= T_SIG) else 0,
                          'crop': {'z': round(1 / h0, 4), 'cx': round(x0 + w0 / 2, 4), 'cy': round(y0 + h0 / 2, 4)}})
        out[iid] = {'id': iid, 'nome': o['nome'], 'conf': 'alta' if alta else 'bassa', 'buoni': R['buoni'], 'proposte': props, 'secondi': R['sec']}
    met['totale_s'] = round(time.time() - T0, 1); met['ram_picco_mb'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0); met['cpu'] = os.cpu_count()
    met['identita'] = {i: {'conf': v['conf'], 'buoni': v['buoni'], 'proposte': len(v['proposte']), 'secondi': v.get('secondi')} for i, v in out.items()}
    meta = {'schema': 2, 'generato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'motore': 'A3.2 v2 (CLIP ritagli + SigLIP scena, contrasto e qualità)', 'soglie': {'clip': T_CLIP, 'siglip': T_SIG},
            'diritti': {'fonte': 'TMDB (percorsi CDN, nessuna immagine copiata)', 'uso': 'solo privato/locale sul dispositivo dell\'utente', 'pubblicazione': False, 'immagini_nel_repository': False},
            'identita': [out[o['id']] for o in W if o['id'] in out]}
    json.dump(meta, open(os.path.join(a.out, 'proposte2_w1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(met, open(os.path.join(a.out, 'metriche2_w1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print(json.dumps({k: v for k, v in met.items() if k != 'identita'}, ensure_ascii=False))
if __name__ == '__main__': main()
