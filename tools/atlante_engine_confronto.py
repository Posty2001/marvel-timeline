#!/usr/bin/env python3
"""A3.2 - misure oggettive senza giudizio umano sul prototipo (10 identità): accordo CLIP/SigLIP, confusioni tra identità, riduzione dei candidati, tempi/risorse.
La PRECISIONE reale (la scena proposta è davvero il personaggio/variante giusta?) si misura solo con le approvazioni dell'utente: vedi docs/ATLANTE_2_0_A32_VISUAL_ASSET_ENGINE.md."""
import json, os, sys
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/atlante/engine')
def L(n):
    p = os.path.join(D, n); return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None
def main():
    out = []; P = {m: L('proposte_%s.json' % m) for m in ('clip', 'siglip')}; M = {m: L('metriche_%s.json' % m) for m in ('clip', 'siglip')}
    for m in ('clip', 'siglip'):
        if not P[m]: out.append('- %s: dati assenti' % m); continue
        cand = sum(v['candidati'] for v in M[m]['identita'].values()); prop = sum(len(i['proposte']) for i in P[m]['identita'])
        seen = {}
        for i in P[m]['identita']:
            for p in i['proposte']: seen.setdefault(p['p'], []).append(i['id'])
        conf = {k: v for k, v in seen.items() if len(v) > 1}
        st = M[m]['stadi_s']
        out.append('- **%s**: candidati %d -> proposte %d (riduzione %.1f%%); tempo totale %.0f s (%.1f min) su %d CPU, RAM di picco %d MB; stadi %s; immagini proposte a più identità: %d' % (m, cand, prop, 100 * (1 - prop / cand), M[m]['totale_s'], M[m]['totale_s'] / 60, M[m]['cpu'], M[m]['ram_picco_mb'], st, len(conf)))
    if P['clip'] and P['siglip']:
        out.append('\n| identità | proposte CLIP | proposte SigLIP | in comune (immagini) | in comune (titoli) |\n|---|---|---|---|---|'); tot = 0; n = 0
        s2 = {i['id']: i for i in P['siglip']['identita']}
        for i in P['clip']['identita']:
            a = {p['p'] for p in i['proposte']}; b = {p['p'] for p in s2[i['id']]['proposte']}; ta = {p['num'] for p in i['proposte']}; tb = {p['num'] for p in s2[i['id']]['proposte']}
            out.append('| %s | %d | %d | %d | %d/%d |' % (i['id'], len(a), len(b), len(a & b), len(ta & tb), len(ta | tb))); tot += len(a & b); n += min(len(a), len(b))
        out.append('\nAccordo medio sulle immagini: %.0f%% (immagini in comune / proposte minime).' % (100 * tot / max(1, n)))
    txt = '\n'.join(out); print(txt); open(os.path.join(D, 'CONFRONTO.md'), 'w', encoding='utf-8').write('# A3.2 - confronto CLIP / SigLIP (misure oggettive)\n\n' + txt + '\n')
main()
