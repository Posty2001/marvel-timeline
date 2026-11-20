"""Integrita' del catalogo reale assets/episodes/ rispetto alle schede serie della Timeline."""
import json, os, re, sys
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
A = os.path.join(R, 'assets/episodes/')
ix = json.load(open(A + 'index.json', encoding='utf-8'))['voci']
html = open(R + '/index.html', encoding='utf-8').read()
cards = {m.group(1): m.group(2) for m in re.finditer(r'id="item-(\d+)"[^>]*data-type="serie"[^>]*data-search="([^"]*)"', html)}
tmap = json.load(open(R + '/assets/images/catalog/tmdb_map.json'))['voci']; ov = json.load(open(R + '/assets/images/catalog/tmdb_overrides.json'))['voci']
bad = []
def chk(n, c, x=''):
    print('PASS' if c else 'FAIL', n, x); (bad.append(n) if not c else None)
chk('ogni voce indice e\' una scheda serie', all(k in cards for k in ix))
chk('137/138 presenti come stagioni in attesa, senza episodi inventati', all(ix.get(k, {}).get('in_attesa') and ix[k]['episodi'] == 0 for k in ('137', '138')))
chk('Runaways (67466) non associata a nessuna scheda', all(v['tmdb'] != 67466 for v in ix.values()))
chk('file referenziati esistono e coincidono (id, stagione)', all(os.path.exists(A + '%d.json' % v['tmdb']) for v in ix.values()))
ok_names = True; tot = sp = 0
for k, v in ix.items():
    d = json.load(open(A + '%d.json' % v['tmdb'], encoding='utf-8'))
    exp = (ov.get(k) or tmap.get(k) or {}).get('id')
    if d['tmdb'] != v['tmdb'] or exp != v['tmdb']: ok_names = False; print('  incoerenza', k, v, exp)
    sel = [s for s in d['stagioni'] if v.get('s') is None or s['n'] == v['s']]
    if v.get('in_attesa'):
        if sel or v['episodi'] or v['speciali']: ok_names = False; print('  in_attesa con dati', k)
        continue
    m = sum(len(s['episodi']) for s in sel if s['n'] > 0); x = sum(len(s['episodi']) for s in sel if s['n'] == 0)
    if (m, x) != (v['episodi'], v['speciali']): ok_names = False; print('  conteggi', k, m, x, v)
    if v.get('s') is not None and not sel: ok_names = False; print('  stagione assente', k)
    tot += m; sp += x
chk('ID TMDB indice == mappa/override del repository; conteggi coerenti', ok_names)
# nomi TMDB vs titolo scheda (controllo di plausibilita')
def n(x): return re.sub(r'[^a-z0-9]+', '', x.lower())
mism = [(k, cards[k], v['nome']) for k, v in ix.items() if not (n(v['nome'])[:6] in n(cards[k]) or n(cards[k])[:6] in n(v['nome']))]
print('  nomi da verificare a mano:', mism)
chk('segnalazione nomi: solo traduzioni note (Spider-Man di quartiere, Daredevil Rinascita, VisionQuest)', all(k in ('120', '134', '122', '128', '135') for k, _, _ in mism))
att = [k for k, v in ix.items() if v.get('in_attesa')]
print('serie con dati', len(ix) - len(att), '| in attesa (stagione futura)', att, '/', len(cards), '| episodi principali', tot, '| speciali', sp, '| non coperte', sorted(set(cards) - set(ix) - set(att)))
sys.exit(1 if bad else 0)
