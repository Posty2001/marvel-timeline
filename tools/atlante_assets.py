#!/usr/bin/env python3
"""A3.1 - Registro degli asset visivi (solo METADATI e regole; nessuna immagine protetta).
Genera data/atlante/assets.json a partire da atlante2/data/index.json + atlante2/data/pilot/candidati.json.
Le immagini scelte restano sul dispositivo dell'utente (archivio privato, esportabile): qui si registra lo stato per identita.
Uso: python3 tools/atlante_assets.py --scrivi | --verifica"""
import json, os, re, sys, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data/atlante/assets.json')
LICENZA = 'Nessun diritto concesso da TMDB sulle immagini: fotogramma di proprieta\' dello studio titolare. Uso personale e non commerciale; non ridistribuire; non incluso nel repository, nello ZIP o nel deploy.'
REGOLE = [
 'Un ritratto appartiene a UNA identita e UNA continuita (campo continuita = universo dell\'identita).',
 'Stessa scena TMDB su due identita: l\'app chiede conferma esplicita (le varianti devono avere ritratti distinti).',
 'Nessun archetipo condiviso o ricolorato; nessuna locandina come ritratto; fotografie degli attori solo per voci di tipo t (interprete).',
 'Le immagini protette non entrano nel repository: asset di tipo ritratto hanno modalita privata-locale; il repository conserva solo metadati.',
 'Illustrazioni originali (universi, luoghi, artefatti, eventi): modalita originale, da produrre e verificare separatamente (non nel pilota).']

def costruisci():
    ix = json.load(open(os.path.join(ROOT, 'atlante2/data/index.json'))); by = {v['i']: v for v in ix['voci']}
    c = json.load(open(os.path.join(ROOT, 'atlante2/data/pilot/candidati.json')))
    ass = []
    for i in c['identita']:
        v = by[i['id']]
        ass.append({'asset_id': 'ast-' + i['id'][3:] + '-001', 'entita': i['id'], 'nome': v['n'], 'tipo': 'ritratto', 'continuita': v['u'], 'livello': 'L4',
                    'modalita': 'privata-locale', 'fonte': {'nome': 'TMDB', 'tipo': 'scena-da-titolo', 'interprete': i['attore']['nome'], 'titoli': [t['titolo_tmdb'] for t in i['titoli'] if t['verificato']]},
                    'attribuzione': 'Fotogramma © studio titolare; indice TMDB (questo prodotto usa le API TMDB ma non e\' approvato o certificato da TMDB)',
                    'licenza_o_condizioni': LICENZA, 'formato': 'WebP 3:4 480x640 (JPEG se WebP non codificabile)', 'risoluzione_origine_min': '1280 px di larghezza',
                    'candidati': len(i['immagini']), 'stato': 'in-attesa-selezione', 'verifica': {'stato': 'non-verificato', 'verificato_da': None, 'data': None}, 'nota': i['nota']})
    return {'schema': 1, 'descrizione': 'Registro asset visivi Atlante 2.0 (A3.1 pilota). Solo metadati: nessuna immagine protetta nel repository.', 'regole': REGOLE, 'asset': ass,
            'sha256_candidati': hashlib.sha256(open(os.path.join(ROOT, 'atlante2/data/pilot/candidati.json'), 'rb').read()).hexdigest()}

def verifica():
    e = []; o = json.load(open(OUT)); ix = json.load(open(os.path.join(ROOT, 'atlante2/data/index.json'))); by = {v['i']: v for v in ix['voci']}
    ids = [a['asset_id'] for a in o['asset']]
    if len(ids) != len(set(ids)): e.append('asset_id duplicati')
    seen = set()
    for a in o['asset']:
        if a['entita'] not in by: e.append('entita ignota ' + a['entita'])
        elif by[a['entita']]['u'] != a['continuita']: e.append('continuita non coerente ' + a['entita'])
        k = (a['entita'], a['continuita'], a['tipo'])
        if k in seen: e.append('asset doppio per identita+continuita ' + a['entita'])
        seen.add(k)
        if a['tipo'] == 'ritratto' and a['modalita'] != 'privata-locale': e.append('ritratto non privato ' + a['entita'])
        if by.get(a['entita'], {}).get('t') == 't' and a['tipo'] != 'foto-interprete': e.append('voce interprete con tipo diverso da foto-interprete')
        if by.get(a['entita'], {}).get('t') != 't' and a['tipo'] == 'foto-interprete': e.append('foto interprete su voce non interprete')
        if re.search(r'https?://|\.(jpe?g|png|webp)\b', json.dumps(a)): e.append('URL o file immagine nel registro: ' + a['entita'])
        for k2 in ('fonte', 'attribuzione', 'licenza_o_condizioni', 'verifica', 'continuita'):
            if not a.get(k2): e.append('campo mancante %s in %s' % (k2, a['entita']))
    return e

if __name__ == '__main__':
    if '--scrivi' in sys.argv:
        o = costruisci(); json.dump(o, open(OUT, 'w'), ensure_ascii=False, indent=1); open(OUT, 'a').write('\n'); print('scritto', OUT, len(o['asset']), 'asset')
    if '--verifica' in sys.argv:
        e = verifica(); print('OK' if not e else 'ERRORI: ' + '; '.join(e)); sys.exit(1 if e else 0)
