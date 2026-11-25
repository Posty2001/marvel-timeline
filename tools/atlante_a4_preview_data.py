#!/usr/bin/env python3
"""Genera i dati REALI (compatti) per l'anteprima interattiva A4 (docs/atlante2/a4/anteprima_v2.html). Solo lettura dei registri."""
import json, re, os, collections, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(R, p), encoding='utf-8'))
I = J('data/atlante/identita.json'); U = J('data/atlante/universi.json')['voci']; RG = J('data/atlante/relazioni.json'); P = J('data/atlante/personaggi.json')['voci']
MV = J('data/atlante/blob/mvMapData.json')['universi']; OR = J('data/atlante/organizzazioni.json')['voci']
CLS = {'Continuità principale': 'P', 'Universo autonomo': 'A', 'Diramazione / universo alternativo': 'D', 'Luogo narrativo (non un universo)': 'L', 'Raggruppamento editoriale': 'E'}
ids = [i for i in I['identita'] if i['conta_come_personaggio']]
cnt = collections.Counter(i['universo'] for i in ids)
uni = []
for x in U:
    c = {f['k']: f['testo'] for f in x['campi']}
    nat = c['NATURA']; cl = CLS[nat.split(' — ')[0]]
    uni.append({'id': x['id'], 'n': x['nome'], 'c': cl, 'k': cnt.get(x['id'], 0), 'nat': nat, 'd': c.get('DESCRIZIONE', '')[:260], 't': [int(t) for t in MV[x['id']]['titoliIds']] if x['id'] in MV else []})
ui = {u['id']: n for n, u in enumerate(uni)}
# titoli (nome dalle schede, mai da nomi di persone)
tn = collections.defaultdict(collections.Counter)
for x in P:
    for f in x['campi']:
        if f['k'] in ('PRIMA APP.', 'ULTIMA APP.', 'ALTRE APP.'):
            for m in re.finditer(r'N°(\d{3})\s*[—-]\s*([^·;|\n]+?)(?=\s*(?:·|;|\||$|\n|N°\d{3}))', f['testo']): tn[m.group(1)][m.group(2).strip().rstrip(',').strip()] += 1
tit = {int(k): v.most_common(1)[0][0] for k, v in tn.items()}
nodes = []; ix = {}
for i in ids:
    ix[i['id']] = len(nodes); nodes.append({'id': i['id'], 'n': i['nome'], 'u': ui.get(i['universo'], -1), 'a': [int(a) for a in i['apparizioni']], 'k': 'i', 'p': i['pagina_principale']})
for o in OR:
    ix[o['id']] = len(nodes); nodes.append({'id': o['id'], 'n': re.sub(r'^org-', '', o['id']).replace('-', ' ').upper() if not o.get('nome') else o['nome'], 'u': -1, 'a': [], 'k': 'o', 'p': o['id']})
for s in I['segnaposto']:
    ix[s['id']] = len(nodes); nodes.append({'id': s['id'], 'n': s['nome'], 'u': -1, 'a': [], 'k': 's', 'p': ''})
# nomi org dal registro (campo titolo se presente)
for o in OR:
    nm = o.get('titolo') or o.get('nome') or next((f['testo'] for f in o['campi'] if f['k'] == 'TITOLO'), None)
    if nm: nodes[ix[o['id']]]['n'] = nm
rel = []
TI = {}
for r in RG['relazioni']:
    if r['da'] not in ix or r['a'] not in ix: continue
    TI.setdefault(r['tipo'], len(TI))
    rel.append([ix[r['da']], ix[r['a']], r['tipo'], r['qualifica'] or '', r['verifica'], 1 if r['simmetrica'] else 0, r['classe'][0], (r['fonte'][0] if r['fonte'] else '')[:90]])
out = {'uni': uni, 'nodes': nodes, 'rel': rel, 'tit': tit, 'cnt': RG['conteggi'], 'tipi': {k: v['classe'] for k, v in RG['schema']['tipi'].items()}}
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
if __name__ == '__main__': sys.stdout.write(s)
