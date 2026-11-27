#!/usr/bin/env python3
"""W0 prototipo (NON nel runtime): indice di ricerca a shard per 20-50k record.
Uso: build_search.py <out_dir> <N> [--reale]  (sintetico deterministico; --reale usa i 452 nomi storici + alias)"""
import json, sys, os, random, gzip, unicodedata, re, zlib, pathlib
def norm(s):
    s = unicodedata.normalize('NFKD', s.lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
SH = 64; CH = 1000
def shard(t): return zlib.crc32(t.encode()) % SH
def sintetico(N, reale):
    R = pathlib.Path(__file__).resolve().parents[2]
    base = [v['n'] for v in json.load(open(R/'atlante2/data/index.json'))['voci']]
    al = {x['id']: x.get('alias', []) for x in json.load(open(R/'data/atlante/identita.json'))['identita']}
    rnd = random.Random(7); sil = ['ka','ra','lo','mi','zen','thor','vol','dar','ex','on','ul','ta','gor','ney','bri','ana','xa','mor','el','ri']
    out = [(n, []) for n in base]
    while len(out) < N:
        w = lambda: ''.join(rnd.choice(sil) for _ in range(rnd.randint(2, 3))).capitalize()
        nome = w() + ' ' + w(); a = [w() + ' il ' + w()] if rnd.random() < .5 else []
        if rnd.random() < .3: a.append(nome.split()[0])
        out.append((nome, a))
    return out[:N]
def main():
    out = pathlib.Path(sys.argv[1]); N = int(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    recs = sintetico(N, True)
    names = []; post = [dict() for _ in range(SH)]; pre = {}
    for o, (n, al) in enumerate(recs):
        keys = [norm(n)] + [norm(a) for a in al]
        names.append([n, al])
        seen = set()
        for k in keys:
            for w in k.split():
                for i in range(len(w) - 2):
                    t = w[i:i+3]; seen.add(t)
                p = w[:2]; pre.setdefault(p, set()).add(o)
        for t in seen: post[shard(t)].setdefault(t, []).append(o)
    sz = {'nomi': 0, 'post': 0, 'pre': 0}
    (out/'n').mkdir(exist_ok=True); (out/'t').mkdir(exist_ok=True)
    for c in range(0, N, CH):
        b = json.dumps(names[c:c+CH], ensure_ascii=False, separators=(',', ':')).encode()
        (out/'n'/f'{c//CH}.json').write_bytes(b); sz['nomi'] += len(gzip.compress(b))
    for s in range(SH):
        d = {}
        for t, l in post[s].items():
            prev = 0; dl = []
            for x in l: dl.append(x - prev); prev = x
            d[t] = dl
        b = json.dumps(d, separators=(',', ':')).encode()
        (out/'t'/f'{s}.json').write_bytes(b); sz['post'] += len(gzip.compress(b))
    for p, l in pre.items(): pass
    b = json.dumps({p: sorted(l)[:200] for p, l in pre.items()}, separators=(',', ':')).encode()
    (out/'pre.json').write_bytes(b); sz['pre'] = len(gzip.compress(b))
    json.dump({'N': N, 'SH': SH, 'CH': CH, 'gz': sz}, open(out/'meta.json', 'w'))
    print('N', N, 'gz bytes', sz, 'tot MB', round(sum(sz.values())/1e6, 2))
main()
