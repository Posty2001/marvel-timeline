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
T_GEN = 2.5   # soglia per i prompt generici (solo nome): segnali più deboli; NON ancora calibrata, verrà misurata con le tue approvazioni per classe di confidenza
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

def carica_modelli(lab):
    import torch, open_clip
    E = {}; TF = {}; SCALE = {}; met = {}
    for m in ('clip', 'siglip'):
        t = time.time(); name, pre = MODELLI[m]; mod, _, prep = open_clip.create_model_and_transforms(name, pretrained=pre); mod.eval(); tok = open_clip.get_tokenizer(name)
        SCALE[m] = (float(mod.logit_scale.exp()), float(mod.logit_bias) if getattr(mod, 'logit_bias', None) is not None else None)
        def emb(ims, mod=mod, prep=prep):
            with torch.no_grad(): f = mod.encode_image(torch.stack([prep(i) for i in ims])); return f / f.norm(dim=-1, keepdim=True)
        E[m] = (mod, tok, emb); met['carica_' + m] = round(time.time() - t, 1)
    return E, SCALE, met
def testo(E, m, lab):
    import torch
    mod, tok, _ = E[m]
    with torch.no_grad(): tf = mod.encode_text(tok(['a movie still of ' + l if l not in NEG else l for l in lab])); return tf / tf.norm(dim=-1, keepdim=True)

def blocco(W, E, SCALE, usate, tag, smoke=False):
    """Elabora un blocco di identità (lista di dict di wave). Ritorna (out per identità, metriche). `usate` = scene già proposte ad altre identità."""
    import torch
    met = {'stadi_s': {}}; T0 = time.time(); C = {}; pools = {}
    for o in W:
        c = json.load(open(os.path.join(ROOT, 'atlante2/data/pilot/c/%s.json' % o['id']), encoding='utf-8')); C[o['id']] = c
        ok = {t['num'] for t in c['titoli'] if t.get('verificato')}; amb = set(o['ambigui'])
        pools[o['id']] = [x for x in c['immagini'] if x['num'] in ok and x['num'] not in amb and x['w'] >= MIN_W and x['p'] not in usate]
    uniq = sorted({x['p'] for L in pools.values() for x in L})
    if smoke: uniq = uniq[:150]; pools = {k: [x for x in v if x['p'] in set(uniq)] for k, v in pools.items()}
    met['candidati_totali'] = sum(len(C[i]['immagini']) for i in C); met['immagini_uniche'] = len(uniq)
    t = time.time()
    with ThreadPoolExecutor(8) as ex: okd = list(ex.map(scarica, uniq))
    met['stadi_s']['download'] = round(time.time() - t, 1); uniq = [p for p, k in zip(uniq, okd) if k]
    Q = {}; t = time.time()
    for p in uniq:
        try: im = Image.open(path_of(p)).convert('RGB')
        except Exception: continue
        sh = sharp(im)
        if sh >= MIN_SHARP: Q[p] = {'sharp': sh, 'expo': expo(im), 'dh': dhash(im), 'w': im.size[0], 'h': im.size[1]}
    met['stadi_s']['qualita'] = round(time.time() - t, 1); met['immagini_nitide'] = len(Q)
    plist = {o['id']: [x.strip() for x in o['prompt'].split('|') if x.strip()] for o in W}; lab = []
    for o in W:
        for l in plist[o['id']]:
            if l not in lab: lab.append(l)
    for l in NEG:
        if l not in lab: lab.append(l)
    ix = {l: k for k, l in enumerate(lab)}; TF = {m: testo(E, m, lab) for m in E}
    def margin(m, f, prompts):
        sc, b = SCALE[m]; s = (f @ TF[m].T) * sc
        if b is not None: s = s + b
        mine = [ix[l] for l in prompts]; rest = [k for k in range(len(lab)) if k not in mine]; others = s[:, rest]; lse = torch.logsumexp(others, dim=1)
        return torch.stack([s[:, k] - lse for k in mine], dim=1).max(dim=1).values.numpy()
    P = list(Q); FE = {'clip': [], 'siglip': []}
    for m in ('clip', 'siglip'):
        t = time.time(); emb = E[m][2]
        for k in range(0, len(P), 32): FE[m].append(emb([Image.open(path_of(p)).convert('RGB') for p in P[k:k + 32]]))
        FE[m] = torch.cat(FE[m]) if FE[m] else torch.zeros((0, 512)); met['stadi_s']['scena_' + m] = round(time.time() - t, 1)
    pos = {p: k for k, p in enumerate(P)}; out = {}; res = {}
    for o in W:
        iid = o['id']; t = time.time(); L = [x for x in pools[iid] if x['p'] in Q]; keep = []
        for x in sorted(L, key=lambda x: -x.get('v', 0)):
            if all(ham(Q[x['p']]['dh'], Q[k['p']]['dh']) > 6 for k in keep): keep.append(x)
        if not keep: out[iid] = {'id': iid, 'nome': o['nome'], 'conf': 'bassa', 'buoni': 0, 'proposte': []}; continue
        ii = [pos[x['p']] for x in keep]; mc = margin('clip', FE['clip'][ii], plist[iid]); ms = margin('siglip', FE['siglip'][ii], plist[iid])
        pre = 0.6 * rank01(mc) + 0.4 * rank01(ms); top = [keep[j] for j in np.argsort(-pre)[:TOPW]]; tj = {x['p']: j for j, x in enumerate(keep)}; rows = []
        for x in top:
            im = Image.open(path_of(x['p'])).convert('RGB'); Wd, Ht = im.size; best = None
            for h0, nx, ny in SC:
                if x['h'] * h0 < MIN_CROP_H: continue
                w0 = 0.75 * h0 * Ht / Wd
                if w0 > 1: continue
                wins = [(x0, y0, w0, h0) for y0 in (np.linspace(0, 1 - h0, ny) if ny > 1 else [0.0]) for x0 in np.linspace(0, 1 - w0, nx)]
                crops = [im.crop((int(a0 * Wd), int(b0 * Ht), int((a0 + w0) * Wd), int((b0 + h0) * Ht))) for a0, b0, w0, h0 in wins]
                fw = E['clip'][2](crops); mw = margin('clip', fw, plist[iid])
                for w, v in zip(wins, mw):
                    sc2 = float(v) + 0.3 * w[3]
                    if best is None or sc2 > best[0]: best = (sc2, w, float(v), fw[int(np.argmax(mw))])
            if best is None: continue
            q = Q[x['p']]; rows.append({'x': x, 'mw': best[2], 'win': best[1], 'ms': float(ms[tj[x['p']]]), 'sharp': q['sharp'], 'expo': q['expo'], 'f': best[3], 'ch': x['h'] * best[1][3]})
        if rows:
            r_m = rank01([r['mw'] for r in rows]); r_s = rank01([r['ms'] for r in rows]); r_q = rank01([r['sharp'] for r in rows])
            for r, a1, a2, a3 in zip(rows, r_m, r_s, r_q): r['tot'] = 0.5 * a1 + 0.2 * a2 + 0.3 * (0.5 * a3 + 0.2 * r['expo'] + 0.3 * min(1.0, r['ch'] / 1000.0))
        rows.sort(key=lambda r: -r.get('tot', 0)); res[iid] = {'o': o, 'rows': rows, 'buoni': sum(1 for r in rows if r['mw'] >= (T_GEN if o.get('generico') else T_CLIP)), 'sec': round(time.time() - t, 1)}
        print(tag, iid, 'candidati', len(L), 'dopo dedup', len(keep), 'ritagli buoni', res[iid]['buoni'], res[iid]['sec'], 's', flush=True)
    owner = {}
    for iid, R in res.items():
        for r in R['rows']:
            p = r['x']['p']
            if p not in owner or r['mw'] > owner[p][1]: owner[p] = (iid, r['mw'])
    for o in W:
        iid = o['id']
        if iid not in res: continue
        R = res[iid]; alta = R['buoni'] >= 3; nmax = 5 if alta else 10; sel = []; per = {}
        for lim in ((2, 3, 4, 5) if alta else (2, 3, 5, 10)):   # tetto per titolo: più largo per la confidenza bassa (fino a 10 proposte anche con un solo titolo)
            for r in R['rows']:
                if len(sel) >= nmax: break
                p = r['x']['p']
                if r in sel or owner.get(p, (iid,))[0] != iid or per.get(r['x']['num'], 0) >= lim: continue
                if lim == 2 and any(float(r['f'] @ s2['f']) > 0.94 for s2 in sel): continue
                sel.append(r); per[r['x']['num']] = per.get(r['x']['num'], 0) + 1
            if len(sel) >= min(nmax, 3 if alta else 10): break
        props = []
        for k, r in enumerate(sel):
            x0, y0, w0, h0 = r['win']
            props.append({'rk': k + 1, 'p': r['x']['p'], 'w': r['x']['w'], 'h': r['x']['h'], 'num': r['x']['num'], 'sc': round(r['tot'], 3), 'm': round(r['mw'], 2), 'ms': round(r['ms'], 2), 'ck': 1 if (r['mw'] >= (T_GEN if o.get('generico') else T_CLIP) and r['ms'] >= (T_SIG - 1.5 if o.get('generico') else T_SIG)) else 0,
                          'crop': {'z': round(1 / h0, 4), 'cx': round(x0 + w0 / 2, 4), 'cy': round(y0 + h0 / 2, 4)}})
        out[iid] = {'id': iid, 'nome': o['nome'], 'conf': 'alta' if alta else 'bassa', 'gen': 1 if o.get('generico') else 0, 'buoni': R['buoni'], 'proposte': props, 'secondi': R['sec']}
    met['totale_s'] = round(time.time() - T0, 1); met['ram_picco_mb'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)
    met['identita'] = {i: {'conf': v['conf'], 'buoni': v['buoni'], 'proposte': len(v['proposte']), 'secondi': v.get('secondi')} for i, v in out.items()}
    for p in list(Q): 
        try: os.remove(path_of(p))   # le immagini non restano nel runner oltre il blocco
        except OSError: pass
    return out, met

def meta_out(motore, ident):
    return {'schema': 2, 'generato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'motore': motore, 'soglie': {'clip': T_CLIP, 'siglip': T_SIG},
            'diritti': {'fonte': 'TMDB (percorsi CDN, nessuna immagine copiata)', 'uso': 'solo privato/locale sul dispositivo dell\'utente', 'pubblicazione': False, 'immagini_nel_repository': False}, 'identita': ident}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='engine-out'); ap.add_argument('--smoke', action='store_true'); ap.add_argument('--tutte', action='store_true', help='ondata completa a blocchi riprendibili'); ap.add_argument('--budget-min', type=float, default=95.0); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); os.makedirs(CACHE, exist_ok=True); import torch; torch.set_num_threads(os.cpu_count() or 2); T0 = time.time()
    if not a.tutte:   # ondata 1 (compatibilità)
        W = json.load(open(os.path.join(ROOT, 'data/atlante/engine/wave1.json'), encoding='utf-8'))['identita']
        if a.smoke: W = W[:6]
        E, SCALE, mm = carica_modelli(None); out, met = blocco(W, E, SCALE, set(), 'w1', a.smoke); met.update(mm); met['cpu'] = os.cpu_count()
        json.dump(meta_out('A3.2 v2 (CLIP ritagli + SigLIP scena, contrasto e qualità)', [out[o['id']] for o in W if o['id'] in out]), open(os.path.join(a.out, 'proposte2_w1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(met, open(os.path.join(a.out, 'metriche2_w1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print(json.dumps({k: v for k, v in met.items() if k != 'identita'}, ensure_ascii=False)); return
    # ---- ondata completa a blocchi: ogni blocco è salvato a parte; i blocchi già presenti vengono saltati (ripresa dopo interruzione)
    WA = json.load(open(os.path.join(ROOT, 'data/atlante/engine/waveall.json'), encoding='utf-8')); BY = {o['id']: o for o in WA['identita']}; bd = os.path.join(a.out, 'blocchi'); os.makedirs(bd, exist_ok=True)
    rep = os.path.join(ROOT, 'data/atlante/engine/blocchi'); rifare = set(WA['rifare_ondata1']); usate = set()
    def leggi(f):
        try: return json.load(open(f, encoding='utf-8'))
        except Exception: return None
    w1 = leggi(os.path.join(ROOT, 'data/atlante/engine/proposte2_w1.json')) or {'identita': []}
    for i in w1['identita']:
        if i['id'] not in rifare:
            for x in i['proposte']: usate.add(x['p'])
    fatti = set()
    for k in range(len(WA['blocchi'])):
        f = os.path.join(rep, 'b%02d.json' % k); d = leggi(f)
        if d:
            fatti.add(k)
            for i in d['identita']:
                for x in i['proposte']: usate.add(x['p'])
    print('blocchi totali', len(WA['blocchi']), 'già fatti', sorted(fatti), flush=True)
    E, SCALE, mm = carica_modelli(None); tempi = []
    for k, ids in enumerate(WA['blocchi']):
        if k in fatti: continue
        medio = (sum(tempi) / len(tempi)) if tempi else 0.0
        if tempi and (time.time() - T0) / 60 + 1.25 * medio / 60 > a.budget_min: print('budget di tempo raggiunto: riprendere con un nuovo lancio', flush=True); break
        t = time.time(); W = [BY[i] for i in ids if os.path.exists(os.path.join(ROOT, 'atlante2/data/pilot/c/%s.json' % i))]
        out, met = blocco(W, E, SCALE, usate, 'b%02d' % k, a.smoke); met['blocco'] = k; met['cpu'] = os.cpu_count()
        for i in out.values():
            for x in i['proposte']: usate.add(x['p'])
        json.dump(meta_out('A3.2 v3 blocco %d' % k, [out[i] for i in ids if i in out]), open(os.path.join(bd, 'b%02d.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        json.dump(met, open(os.path.join(bd, 'm%02d.json' % k), 'w', encoding='utf-8'), ensure_ascii=False, indent=1); tempi.append(time.time() - t); print('BLOCCO', k, 'ok in', round(tempi[-1] / 60, 1), 'min', flush=True)
        if a.smoke: break
if __name__ == '__main__': main()
