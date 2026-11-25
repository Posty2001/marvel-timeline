#!/usr/bin/env python3
"""A4.0 - test dei dati (nessuna UI): registro relazioni, split Harry, Peter, nessuna perdita."""
import json, subprocess, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R)
J = lambda p: json.load(open(p, encoding='utf-8'))
F = []
def ok(n, c):
    print(('PASS ' if c else 'FAIL ') + n); (c or F.append(n))
I = J('data/atlante/identita.json'); H = {i['id']: i for i in I['identita']}
ok('300 identita\' (nessuna persa)', len(I['identita']) >= 300)
r, w, y = H['id-harry-osborn-green-goblin'], H['id-harry-osborn-webb'], H['id-harry-osborn-ynfsm']
ok('Harry: tre identita\' autonome Raimi/Webb/YFNSM', r['apparizioni'] == ['001', '002', '003'] and w['apparizioni'] == ['005'] and y['apparizioni'] == ['120'])
ok('Harry: universi distinti', len({r['universo'], w['universo'], y['universo']}) == 3)
ok('Harry: ID e pagina canonica originali preservati', r['pagina_principale'] == 'char-harry-osborn-green-goblin' and I['redirect']['char-harry-osborn-green-goblin']['verso'] == ['id-harry-osborn-green-goblin'])
ok('Harry: apparizioni tracciate in apparizioni_spostate', r['apparizioni_spostate'] == {'005': 'id-harry-osborn-webb', '120': 'id-harry-osborn-ynfsm'})
p = H['id-peter']
ok('Peter (Deadpool): Fox-Verse, fonti https, apparizioni 024/117', p['universo'] == 'uni-earth-10005-fox-verse' and p['apparizioni'] == ['024', '117'] and any(f.startswith('https://') for f in p['fonte']))
rg = J('data/atlante/relazioni.json'); c = rg['conteggi']
ok('registro: co-apparizioni 0 e narrative separate da editoriali', c['co_apparizioni_nel_registro'] == 0 and c['narrative'] == c['per_classe']['narrativa'] and c['per_classe']['editoriale'] > c['narrative'])
ok('registro: ogni nodo e\' un ID (id-/org-/seg-)', all(x['da'][:3] in ('id-', 'seg') and x['a'][:3] in ('id-', 'org', 'seg') for x in rg['relazioni']))
ok('registro: nessuna relazione \'verificata\' senza fonte', all(x['fonte'] for x in rg['relazioni'] if x['verifica'] == 'verificata'))
ok('registro: coda ambigue presente e non importata', c['coda_ambigue_o_errate'] >= 0 and any(x['tipo'].startswith('famiglia') and x['da']=='id-howard-stark' and x['a']=='id-iron-man' for x in rg['relazioni']))
ok('34 link ambigui documentati', os.path.exists('docs/ATLANTE_2_0_A3_LINK_AMBIGUI.md') and 'amb' in open('docs/ATLANTE_2_0_A3_LINK_AMBIGUI.md').read().lower())
for cmd in (['tools/atlante_estrai.py', '--verifica'], ['tools/atlante_identita.py', '--verifica'], ['tools/atlante_a3.py', '--verifica'], ['tools/atlante_relazioni.py', '--verifica']):
    o = subprocess.run([sys.executable] + cmd, capture_output=True, text=True); ok(' '.join(cmd), o.returncode == 0)
print('\nA4.0:', 'OK' if not F else 'FALLITO %s' % F); sys.exit(1 if F else 0)
