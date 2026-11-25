#!/usr/bin/env python3
"""A3.2 Visual Asset Engine - prototipo di preselezione (10 identità del pilota). Costo 0 €: gira su GitHub Actions (CPU), modelli aperti.

Cosa fa (per ogni identità, partendo da atlante2/data/pilot/candidati.json):
 1. filtri duri sui metadati: solo titoli verificati della continuità; titoli condivisi tra varianti della stessa famiglia -> esclusi dalla proposta automatica
 2. scarica le miniature w780 SOLO nel runner (mai nel repository), scarta le immagini troppo piccole o sfocate, deduplica (dHash + similarità degli embedding)
 3. punteggio visivo con CLIP o SigLIP (open_clip): l'identità contro tutte le altre identità del pilota e contro negativi generici (paesaggio, folla, testo, volto senza costume...)
 4. ritaglio suggerito 3:4 per finestra scorrevole sulla stessa metrica (funziona anche con maschere/caschi, dove il rilevatore di volti fallisce)
 5. top-N (3-5) con punteggi e ritaglio nel formato dell'app {z,cx,cy}; la decisione resta all'utente.
Nessun riconoscimento facciale degli attori. In uscita solo metadati (percorsi CDN, punteggi, ritagli, metriche di tempo/risorse): nessuna immagine nel repository.
Uso: python3 tools/atlante_engine.py --modello clip|siglip --out DIR [--max-per-identita N] [--sheet]
"""
import argparse, io, json, os, resource, sys, time, hashlib
from concurrent.futures import ThreadPoolExecutor
import numpy as np, requests
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, 'atlante2/data/pilot/candidati.json')
CDN = 'https://image.tmdb.org/t/p/w780'
MODELLI = {'clip': ('ViT-B-32', 'laion2b_s34b_b79k'), 'siglip': ('ViT-B-16-SigLIP', 'webli')}
# Descrizioni visive di lavoro per il solo motore (ipotesi di prompt, NON dati dell'Atlante). Famiglie: varianti dello stesso personaggio.
PROMPT = {
    'id-iron-man': 'Iron Man in red and gold armor', 'id-thor': 'Thor with long blond hair holding a hammer', 'id-loki': 'Loki in a green and gold horned helmet',
    'id-peter-parker-mcu': 'Spider-Man in a red and blue suit', 'id-peter-parker-raimi': 'Spider-Man in a red and blue suit', 'id-peter-parker-garfield': 'Spider-Man in a red and blue suit',
    'id-wolverine': 'Wolverine with metal claws', 'id-wade-wilson-deadpool': 'Deadpool in a red mask and suit with katanas',
    'id-wanda-maximoff': 'Scarlet Witch with red magic energy', 'id-thanos': 'Thanos, a giant purple alien with a golden gauntlet'}
FAMIGLIE = [['id-peter-parker-mcu', 'id-peter-parker-raimi', 'id-peter-parker-garfield'], ['id-wolverine'], ['id-wade-wilson-deadpool']]
NEGATIVI = ['a landscape without people', 'a crowd of many people', 'a movie logo or title text', 'a close-up of a person face without costume', 'a spaceship or a vehicle', 'an explosion or fire', 'a dark blurry scene']
MIN_W, MIN_SHARP = 1280, 40.0


def dhash(im, n=8):
    g = np.asarray(im.convert('L').resize((n + 1, n), Image.BILINEAR), dtype=np.int16); return int(''.join('1' if b else '0' for b in (g[:, 1:] > g[:, :-1]).flatten()), 2)
def ham(a, b): return bin(a ^ b).count('1')
def sharp(im):
    g = np.asarray(im.convert('L').resize((640, 360)), dtype=np.float32)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]; return float(lap.var())
def expo(im):
    m = float(np.asarray(im.convert('L'), dtype=np.float32).mean()) / 255.0; return max(0.0, 1 - abs(m - 0.42) / 0.42)
def scarica(p):
    for _ in range(3):
        try:
            r = requests.get(CDN + p, timeout=30)
            if r.status_code == 200: return Image.open(io.BytesIO(r.content)).convert('RGB')
        except Exception: time.sleep(1)
    return None
def rss_mb(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--modello', default='clip', choices=list(MODELLI)); ap.add_argument('--out', default='engine-out'); ap.add_argument('--max-per-identita', type=int, default=0)
    ap.add_argument('--top', type=int, default=5); ap.add_argument('--sheet', action='store_true'); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    T0 = time.time(); met = {'modello': a.modello, 'stadi_s': {}}
    import torch, open_clip
    torch.set_num_threads(os.cpu_count() or 2)
    t = time.time(); name, pre = MODELLI[a.modello]; model, _, prep = open_clip.create_model_and_transforms(name, pretrained=pre); model.eval(); tok = open_clip.get_tokenizer(name)
    met['stadi_s']['carica_modello'] = round(time.time() - t, 1)
    J = json.load(open(CAND, encoding='utf-8')); ids = [i['id'] for i in J['identita']]
    # testo: identità del pilota + negativi
    labels = [PROMPT[i] for i in ids] + NEGATIVI; uniq = []
    for l in labels:
        if l not in uniq: uniq.append(l)
    with torch.no_grad():
        tf = model.encode_text(tok(['a movie still of ' + l if l not in NEGATIVI else l for l in uniq])); tf = tf / tf.norm(dim=-1, keepdim=True)
    ix = {l: k for k, l in enumerate(uniq)}; scale = float(model.logit_scale.exp()) if hasattr(model, 'logit_scale') else 100.0
    bias = float(model.logit_bias) if hasattr(model, 'logit_bias') and model.logit_bias is not None else None
    def embed(ims):
        with torch.no_grad():
            f = model.encode_image(torch.stack([prep(i) for i in ims])); return f / f.norm(dim=-1, keepdim=True)
    def prob(f, ident):
        """Margine logaritmico (log-odds) dell'etichetta dell'identità contro TUTTE le altre (identità del pilota + negativi): non satura e ordina le scene
        anche quando tutte appartengono al film giusto (la probabilità softmax saturava a 1.0 e non discriminava)."""
        s = (f @ tf.T) * scale
        if bias is not None: s = s + bias
        k = ix[PROMPT[ident]]; others = torch.cat([s[:, :k], s[:, k + 1:]], dim=1)
        return (s[:, k] - torch.logsumexp(others, dim=1)).numpy()
    # famiglie: titoli condivisi
    fam_of = {i: f for f in FAMIGLIE for i in f}; by = {i['id']: i for i in J['identita']}
    out, cnt = [], {}
    for ident in J['identita']:
        iid = ident['id']; tm = time.time(); st = {'candidati': len(ident['immagini'])}
        ok_titoli = {t['num'] for t in ident['titoli'] if t.get('verificato')}
        escl = set()
        for o in fam_of.get(iid, []):
            if o != iid and o in by:
                escl |= ok_titoli & {t['num'] for t in by[o]['titoli'] if t.get('verificato')}
        pool = [x for x in ident['immagini'] if x['num'] in ok_titoli and x['num'] not in escl and x['w'] >= MIN_W]
        st['dopo_filtri_metadati'] = len(pool); st['titoli_condivisi_esclusi'] = sorted(escl)
        if a.max_per_identita: pool = sorted(pool, key=lambda x: -x.get('v', 0))[:a.max_per_identita]
        t1 = time.time()
        with ThreadPoolExecutor(8) as ex: imgs = list(ex.map(lambda x: scarica(x['p']), pool))
        met['stadi_s']['download'] = round(met['stadi_s'].get('download', 0) + time.time() - t1, 1)
        rows = []
        for x, im in zip(pool, imgs):
            if im is None: continue
            sh = sharp(im)
            if sh < MIN_SHARP: continue
            rows.append({'x': x, 'im': im, 'sharp': sh, 'expo': expo(im), 'dh': dhash(im)})
        st['scaricate_ok_nitide'] = len(rows)
        # dedup dHash
        keep = []
        for r in rows:
            if all(ham(r['dh'], k['dh']) > 6 for k in keep): keep.append(r)
        st['dopo_dedup_hash'] = len(keep)
        t2 = time.time(); F = []
        for k in range(0, len(keep), 16): F.append(embed([r['im'] for r in keep[k:k + 16]]))
        if keep:
            F = torch.cat(F); pr = prob(F, iid)
            for r, p_, f in zip(keep, pr, F): r['p'] = float(p_); r['f'] = f
        met['stadi_s']['punteggio_immagine'] = round(met['stadi_s'].get('punteggio_immagine', 0) + time.time() - t2, 1)
        # ritaglio 3:4 a finestre sulle migliori 12
        keep.sort(key=lambda r: -r.get('p', 0)); top = keep[:12]; t3 = time.time()
        for r in top:
            W_, H_ = r['im'].size; best = None
            for h0 in (1.0, 0.8, 0.64):
                w0 = 0.75 * h0 * H_ / W_
                if w0 > 1: continue
                xs = np.linspace(0, 1 - w0, 7 if h0 < 1 else 7); ys = [0.0] if h0 == 1.0 else np.linspace(0, 1 - h0, 3)
                wins = [(x0, y0, w0, h0) for y0 in ys for x0 in xs]
                crops = [r['im'].crop((int(x0 * W_), int(y0 * H_), int((x0 + w0) * W_), int((y0 + h0) * H_))) for x0, y0, w0, h0 in wins]
                fw = embed(crops); pw = prob(fw, iid)
                for w, p_ in zip(wins, pw):
                    # leggero favore ai ritagli ampi: stesso punteggio, preferisci la finestra più grande se la differenza è piccola
                    s = float(p_) + 0.3 * w[3]
                    if best is None or s > best[0]: best = (s, w, float(p_))
            r['crop'] = best
        met['stadi_s']['ritaglio'] = round(met['stadi_s'].get('ritaglio', 0) + time.time() - t3, 1)
        # punteggio finale e diversità
        def rank_norm(v):
            o = np.argsort(np.argsort(v)); return o / max(1, len(v) - 1)
        if top:
            pid = rank_norm(np.array([r['crop'][2] if r.get('crop') else r['p'] for r in top])); psh = rank_norm(np.array([r['sharp'] for r in top])); pex = np.array([r['expo'] for r in top])
            for r, a1, a2, a3 in zip(top, pid, psh, pex): r['tot'] = 0.6 * a1 + 0.25 * a2 + 0.15 * a3
        top.sort(key=lambda r: -r.get('tot', 0)); scelte, per_titolo = [], {}
        for r in top:
            if len(scelte) >= a.top: break
            if per_titolo.get(r['x']['num'], 0) >= 2: continue
            if any(float(r['f'] @ s['f']) > 0.93 for s in scelte): continue
            scelte.append(r); per_titolo[r['x']['num']] = per_titolo.get(r['x']['num'], 0) + 1
        props = []
        for k, r in enumerate(scelte):
            s, (x0, y0, w0, h0), pc = r['crop']
            props.append({'rk': k + 1, 'p': r['x']['p'], 'w': r['x']['w'], 'h': r['x']['h'], 'num': r['x']['num'], 'sc': round(r['tot'], 3), 'pid': round(r['p'], 2), 'pcrop': round(pc, 2),
                          'nitidezza': round(r['sharp'], 1), 'crop': {'z': round(1 / h0, 4), 'cx': round(x0 + w0 / 2, 4), 'cy': round(y0 + h0 / 2, 4)}})
        st['proposte'] = len(props); st['secondi'] = round(time.time() - tm, 1); cnt[iid] = st
        out.append({'id': iid, 'nome': ident['nome'], 'proposte': props})
        if a.sheet and scelte:
            th = [r['im'].resize((300, 169)) for r in scelte]; sh = Image.new('RGB', (310 * len(th), 190), (20, 20, 20)); d = ImageDraw.Draw(sh)
            for k, (r, im) in enumerate(zip(scelte, th)):
                sh.paste(im, (k * 310, 0)); d.text((k * 310 + 4, 172), '#%d p=%.2f t=%s' % (k + 1, r['p'], r['x']['num']), fill=(255, 255, 255))
            sh.save(os.path.join(a.out, 'sheet_%s.png' % iid))
        print(iid, st, flush=True)
        for r in rows: r['im'].close()
    met['totale_s'] = round(time.time() - T0, 1); met['ram_picco_mb'] = round(rss_mb()); met['cpu'] = os.cpu_count(); met['identita'] = cnt
    meta = {'schema': 1, 'generato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'motore': 'A3.2 prototipo', 'modello': a.modello, 'pesi': MODELLI[a.modello],
            'diritti': {'fonte': 'TMDB (percorsi CDN, nessuna immagine copiata)', 'uso': 'solo privato/locale su dispositivo dell\'utente', 'pubblicazione': False, 'immagini_nel_repository': False,
                        'nota': 'TMDB non concede diritti sui contenuti Marvel/Disney; il motore propone, l\'utente decide; le miniature scaricate nel runner sono scartate a fine job'},
            'identita': out}
    json.dump(meta, open(os.path.join(a.out, 'proposte_%s.json' % a.modello), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(met, open(os.path.join(a.out, 'metriche_%s.json' % a.modello), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(met, ensure_ascii=False))

if __name__ == '__main__': main()
