#!/usr/bin/env python3
"""Numerazioni dell'app: «N° mostrato» (span.rec, usato dalle schede Atlante) e id interno (data-item, usato da altTimelineData, tmdbMap e mvMapData).
Coincidono quasi sempre; differiscono per 9 voci (blocco Fox: 013-019, 023-024). Questo modulo le espone in sola lettura da index.html.
Uso: python3 tools/atlante_numeri.py   (stampa le differenze)"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def carica(html=None):
    s = html if html is not None else open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    tl = {'%03d' % x['num']: x for x in json.loads(re.search(r'id="altTimelineData">(.*?)</script>', s, re.S).group(1))}
    mp = json.loads(re.search(r'id="tmdbMap">(.*?)</script>', s, re.S).group(1))['voci']
    vis2id, id2vis = {}, {}
    for m in re.finditer(r'<(?:li|div)[^>]*class="[^"]*card-wrap[^"]*"[^>]*data-item="(\d{3})"', s):
        r = re.search(r'class="rec">N&deg;(\d{3})<', s[m.end():m.end() + 2500])
        if r: id2vis[m.group(1)] = r.group(1); vis2id[r.group(1)] = m.group(1)
    return {'timeline': tl, 'tmdbMap': mp, 'vis2id': vis2id, 'id2vis': id2vis}

if __name__ == '__main__':
    c = carica(); d = {k: v for k, v in c['id2vis'].items() if k != v}
    print('card:', len(c['id2vis']), '| id != numero mostrato:', len(d))
    for k, v in sorted(d.items()): print('  item %s mostrato N°%s  %s' % (k, v, c['timeline'].get(k, {}).get('title')))
