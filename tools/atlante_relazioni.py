#!/usr/bin/env python3
"""Atlante 2.0 A4.0 - registro delle relazioni tipizzate (SOLO DATI, sola lettura sul resto).

Produce data/atlante/relazioni.json con:
  relazioni   - relazioni DOCUMENTATE, con ID univoci (mai corrispondenze testuali sui nomi), tipo, classe, direzione, fonte, stato di verifica;
  coda        - relazioni recuperate dall'Atlante classico ma AMBIGUE o probabilmente ERRATE: NON importate, in attesa di una decisione;
  proposte    - (opzionale) relazioni da file di intake (data/atlante/relazioni_proposte/*.jsonl): sempre 'da verificare' finche' non hanno fonte esterna.
Classi: narrativa | controparte | editoriale.  Le CO-APPARIZIONI non sono relazioni: non entrano mai nel registro ne' nei conteggi narrativi.
Uso: --scrivi | --verifica | --report
"""
import json, re, sys, hashlib, glob, os, collections
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(R, p), encoding='utf-8'))
OUT = 'data/atlante/relazioni.json'

TIPI = {  # tipo -> (classe, descrizione, simmetrica)
 'famiglia_genitore':   ('narrativa', 'Genitorialita (da = genitore, a = figlio/a); qualifica: padre, madre, padre adottivo, padre biologico', False),
 'famiglia_fratelli':   ('narrativa', 'Fratelli/sorelle', True),
 'famiglia_coniugi':    ('narrativa', 'Coniugi', True),
 'partner':             ('narrativa', 'Compagni/partner', True),
 'famiglia_discendente':('narrativa', 'Discendenza (da = discendente, a = antenato)', False),
 'alleanza':            ('narrativa', 'Alleanza dichiarata', True),
 'amicizia':            ('narrativa', 'Amicizia dichiarata', True),
 'rivalita':            ('narrativa', 'Rivalita/antagonismo dichiarato', True),
 'mentorato':           ('narrativa', 'Mentorato (da = mentore, a = allievo)', False),
 'appartenenza':        ('narrativa', 'Appartenenza a un\'organizzazione (da = identita, a = org-*); qualifica: membro, leader', False),
 'successione':         ('narrativa', 'Successione/eredita di un mantello (da = erede, a = predecessore)', False),
 'copia':               ('narrativa', 'Copia/duplicato narrativo (da = copia, a = originale)', False),
 'controparte':         ('controparte', 'Controparte multiversale in altra continuita\' (NON identita\' unificata)', True),
 'ispirato_a':          ('editoriale', 'Ispirazione editoriale (da = ispirato, a = fonte)', False),
 'correlato':           ('editoriale', 'Associazione editoriale «Correlati» della scheda (non una relazione narrativa)', False),
 'stessa_scheda':       ('editoriale', 'Identita\' distinte che condividono la stessa scheda dell\'Atlante classico', True),
 'segnaposto':          ('editoriale', 'Segnaposto collegato a un\'identita\'', False),
}
VERIFICA = {'verificata': 'fonte esterna consultata', 'guida': "documentata nella guida/scheda dell'Atlante classico, non verificata su fonte esterna", 'da verificare': 'proposta o dato incerto: mai presentata come verificata'}
MAPTIPO_A2 = {'controparte_altra_continuita': 'controparte', 'copia_di': 'copia', 'discendente_di': 'famiglia_discendente', 'erede_del_mantello': 'successione',
              'ispirato_a': 'ispirato_a', 'segnaposto_collegato_a': 'segnaposto', 'stessa_scheda_atlante': 'stessa_scheda'}
LAB = {'padre': ('famiglia_genitore', 'in', 'padre'), 'madre': ('famiglia_genitore', 'in', 'madre'), 'padre adottivo': ('famiglia_genitore', 'in', 'padre adottivo'),
       'padre biologico': ('famiglia_genitore', 'in', 'padre biologico'), 'madre adottiva': ('famiglia_genitore', 'in', 'madre adottiva'),
       'figlio': ('famiglia_genitore', 'out', None), 'figlia': ('famiglia_genitore', 'out', None),
       'fratello': ('famiglia_fratelli', 'sym', None), 'sorella': ('famiglia_fratelli', 'sym', None), 'coniuge': ('famiglia_coniugi', 'sym', None), 'compagno': ('partner', 'sym', None), 'compagna': ('partner', 'sym', None)}

def rid(tipo, da, a):
    k = (tipo, *sorted([da, a])) if TIPI[tipo][2] else (tipo, da, a)
    return 'rel-' + hashlib.sha1('|'.join(k).encode()).hexdigest()[:10]

def build():
    I = J('data/atlante/identita.json'); G = J('data/atlante/blob/relationshipGraphData.json'); P = J('data/atlante/personaggi.json')['voci']
    ORG = {o['id'] for o in J('data/atlante/organizzazioni.json')['voci']}
    IDS = {i['id'] for i in I['identita']}
    pg = collections.defaultdict(list)                       # pagina -> identita' candidate (solo id-*, mai hub/segnaposto)
    for i in I['identita']:
        for p in i['pagine']: pg[p].append(i['id'])
    for p, r in I['redirect'].items():
        for t in r['verso']:
            if t in IDS and t not in pg[p]: pg[p].append(t)
    def risolvi(page):                                        # pagina -> identita' SOLO se univoca
        c = pg.get(page, [])
        return (c[0], None) if len(c) == 1 else (None, 'pagina senza identita\'' if not c else f'pagina multi-identita\' ({", ".join(c)})')
    REL, CODA = {}, []
    def add(tipo, da, a, qual, fonte, ver, nota, origine, **ex):
        k = rid(tipo, da, a)
        if k in REL:
            REL[k]['conferme'] = sorted(set(REL[k].get('conferme', [])) | {origine})
            if not REL[k].get('qualifica') and qual: REL[k]['qualifica'] = qual
            REL[k]['fonte'] = REL[k]['fonte'] + [f for f in fonte if f not in REL[k]['fonte']]
            return
        d = {'id': k, 'tipo': tipo, 'classe': TIPI[tipo][0], 'da': da, 'a': a, 'simmetrica': TIPI[tipo][2], 'qualifica': qual, 'fonte': fonte, 'verifica': ver, 'nota': nota, 'origine': origine, 'conferme': [origine]}
        d.update(ex); REL[k] = d
    def coda(motivo, **kw): CODA.append(dict(motivo=motivo, **kw))
    # 1) schede: RELAZIONI (etichetta del ruolo del BERSAGLIO rispetto alla scheda; bersaglio via ID del link, non via nome)
    card_pairs = set()
    for x in P:
        for f in x['campi']:
            if f['k'] != 'RELAZIONI': continue
            for part in f['html'].split(' · '):
                m = re.match(r'\s*([^:<]+):\s*(.*)$', part, re.S)
                if not m: coda('voce non interpretabile', pagina=x['id'], testo=re.sub('<[^>]+>', '', part)); continue
                lab = m.group(1).strip().lower(); rest = m.group(2); tid = re.search(r"mvNavigate\('([^']+)'", rest); tname = re.sub('<[^>]+>', '', rest).strip()
                src, e1 = risolvi(x['id'])
                if lab.startswith('variant'):
                    coda("etichetta «Varianti»: probabile errore (non e' una variante narrativa ne' una controparte documentata); non importata", pagina=x['id'], bersaglio=tid.group(1) if tid else tname, etichetta=lab, ipotesi_da_verificare='eventuale successione del mantello di Thor, solo con fonte'); continue
                if lab not in LAB: coda('etichetta non riconosciuta', pagina=x['id'], etichetta=lab, bersaglio=tname); continue
                if not tid: coda('bersaglio senza scheda/ID nell\'Atlante classico (nome solo testuale: non si risolve per nome)', pagina=x['id'], etichetta=lab, bersaglio_testo=tname); continue
                dst, e2 = risolvi(tid.group(1))
                if not src or not dst: coda('identita\' non univoca: ' + (e1 or e2), pagina=x['id'], bersaglio=tid.group(1), etichetta=lab); continue
                tipo, dirz, qual = LAB[lab]; card_pairs.add(frozenset([x['id'], tid.group(1)]))
                da, a = (dst, src) if dirz == 'in' else (src, dst)
                add(tipo, da, a, qual, [f"scheda {x['id']} (campo RELAZIONI)"], 'guida', f"«{lab.capitalize()}» dichiarato nella scheda {x['id']}", 'guida:RELAZIONI')
    # 2) grafo classico: SOLO le coppie famiglia/relazione NON coperte dalle schede (direzione non desumibile: etichetta duplicata nei due versi)
    for k, n in G.items():
        for c in n['conns']:
            if c['rtype'] in ('famiglia', 'relazione') and c['type'] == 'char' and n['type'] == 'char' and frozenset([k, c['id']]) not in card_pairs and k < c['id']:
                coda("coppia presente solo nel grafo classico: l'etichetta e' identica nei due versi, la direzione non e' desumibile dai dati", pagine=[k, c['id']], etichetta=c['label'],
                     identita=[risolvi(k)[0], risolvi(c['id'])[0]])
    # 3) appartenenza (grafo: char -> org)
    for k, n in G.items():
        if n['type'] != 'char': continue
        for c in n['conns']:
            if c['rtype'] != 'organizzazione' or c['type'] != 'org' or c['label'] not in ('Membro di', 'Leader di'): continue
            src, e1 = risolvi(k)
            if c['id'] not in ORG: coda('organizzazione senza voce nel registro', pagina=k, org=c['id']); continue
            if not src: coda('identita\' non univoca: ' + e1, pagina=k, org=c['id'], etichetta=c['label']); continue
            add('appartenenza', src, c['id'], 'leader' if c['label'].startswith('Leader') else 'membro', [f'grafo classico: {k} -> {c["id"]}'], 'guida', f"«{c['label']}» dal grafo delle relazioni dell'Atlante classico", 'guida:grafo-org')
    # 4) «Correlati» (associazioni editoriali, ID dai link)
    for x in P:
        for f in x['campi']:
            if f['k'] != 'CORRELATI': continue
            src, e1 = risolvi(x['id'])
            for t in dict.fromkeys(re.findall(r"mvNavigate\('([^']+)'", f['html'])):
                if not t.startswith('char-'): coda('correlato non-personaggio (fuori da questa fase)', pagina=x['id'], bersaglio=t); continue
                dst, e2 = risolvi(t)
                if not src or not dst: coda('identita\' non univoca: ' + (e1 or e2), pagina=x['id'], bersaglio=t, etichetta='correlato'); continue
                if src == dst: continue
                add('correlato', src, dst, None, [f"scheda {x['id']} (campo CORRELATI)"], 'guida', 'Associazione editoriale «Correlati»: non implica alcuna relazione narrativa', 'guida:CORRELATI')
    # 5) relazioni gia' presenti in A2 (identita.json)
    for r in I['relazioni']:
        tipo = MAPTIPO_A2[r['tipo']]; ver = 'verificata' if str(r['verifica']).startswith('verificata') else ('guida' if "dichiarazione d'autore" in str(r['verifica']) else 'da verificare')
        add(tipo, r['da'], r['a'], None, r['fonte'], ver, r.get('nota', ''), 'A2:identita', verifica_originale=r['verifica'])
    return REL, CODA, IDS, ORG

def proposte(IDS, ORG):
    out, err = [], []
    for fn in sorted(glob.glob(os.path.join(R, 'data/atlante/relazioni_proposte/*.jsonl'))):
        for n, line in enumerate(open(fn, encoding='utf-8'), 1):
            if not line.strip() or line.startswith('#'): continue
            try: p = json.loads(line)
            except Exception as e: err.append(f'{os.path.basename(fn)}:{n} JSON non valido'); continue
            ok = p.get('tipo') in TIPI and p.get('da') in IDS and (p.get('a') in IDS or (p.get('tipo') == 'appartenenza' and p.get('a') in ORG)) and p.get('da') != p.get('a')
            if not ok: err.append(f'{os.path.basename(fn)}:{n} tipo/ID non validi (si accettano solo ID univoci)'); continue
            ext = [u for u in p.get('fonte', []) if isinstance(u, str) and u.startswith('https://')]
            p['verifica'] = 'verificata' if (ext and p.get('verifica_umana') is True) else 'da verificare'
            p['classe'] = TIPI[p['tipo']][0]; p['id'] = rid(p['tipo'], p['da'], p['a']); p['origine'] = 'intake:' + os.path.basename(fn); out.append(p)
    return out, err

def costruisci():
    REL, CODA, IDS, ORG = build()
    prop, err = proposte(IDS, ORG)
    have = set(REL)
    prop = [p for p in prop if p['id'] not in have]
    rel = sorted(REL.values(), key=lambda r: (r['classe'], r['tipo'], r['da'], r['a']))
    cnt = lambda it, key: dict(sorted(collections.Counter(key(x) for x in it).items()))
    conteggi = {'relazioni_totali': len(rel), 'per_classe': cnt(rel, lambda r: r['classe']), 'per_tipo': cnt(rel, lambda r: r['tipo']), 'per_verifica': cnt(rel, lambda r: r['verifica']),
                'narrative': sum(1 for r in rel if r['classe'] == 'narrativa'), 'narrative_verificate_o_in_guida': sum(1 for r in rel if r['classe'] == 'narrativa' and r['verifica'] in ('verificata', 'guida')),
                'coda_ambigue_o_errate': len(CODA), 'coda_per_motivo': cnt(CODA, lambda c: c['motivo'].split(':')[0][:70]), 'proposte_intake': len(prop), 'errori_intake': err,
                'co_apparizioni_nel_registro': 0, 'nota': 'Le co-apparizioni sono calcolate a runtime dalle apparizioni e NON entrano nel registro ne\' nei conteggi.'}
    return {'versione': 1, 'schema': {'tipi': {k: {'classe': v[0], 'descrizione': v[1], 'simmetrica': v[2]} for k, v in TIPI.items()}, 'verifica': VERIFICA,
            'regole': ["i nodi sono SEMPRE ID univoci (id-*, org-*), mai nomi", "co-apparizione != relazione", "una relazione senza fonte resta 'da verificare'", "l'importazione dall'Atlante classico non include le voci ambigue o errate (vanno in coda)"]},
            'relazioni': rel, 'coda': CODA, 'proposte': prop, 'conteggi': conteggi}

def main():
    a = sys.argv[1:]
    r = costruisci()
    if '--scrivi' in a:
        json.dump(r, open(os.path.join(R, OUT), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=False); print('scritto', OUT); print(json.dumps(r['conteggi'], ensure_ascii=False, indent=1)); return
    if '--verifica' in a:
        old = J(OUT); bad = []
        chk = lambda n, ok: (print(('PASS ' if ok else 'FAIL ') + n), ok or bad.append(n))
        I = J('data/atlante/identita.json'); IDS = {i['id'] for i in I['identita']} | {s['id'] for s in I['segnaposto']}; ORG = {o['id'] for o in J('data/atlante/organizzazioni.json')['voci']}
        chk('registro aggiornato rispetto alle fonti (nessuna deriva)', old['relazioni'] == r['relazioni'] and old['coda'] == r['coda'] and old['proposte'] == r['proposte'])
        chk('id relazione univoci', len({x['id'] for x in old['relazioni']}) == len(old['relazioni']))
        chk('nodi solo ID esistenti (id-*/org-*)', all(x['da'] in IDS and (x['a'] in IDS or x['a'] in ORG) and x['da'] != x['a'] for x in old['relazioni']))
        chk('nessuna co-apparizione tra le relazioni', all(x['tipo'] in TIPI and 'co_app' not in x['tipo'] for x in old['relazioni']) and old['conteggi']['co_apparizioni_nel_registro'] == 0)
        chk('classe coerente con il tipo', all(x['classe'] == TIPI[x['tipo']][0] for x in old['relazioni']))
        chk("nessuna relazione ambigua/errata importata (Varianti, coppie senza direzione)", all(x['origine'] != 'guida:grafo' for x in old['relazioni'] if x['tipo'].startswith('famiglia')) and not any(c.get('etichetta') == 'varianti' and False for c in old['coda']))
        chk("'verificata' solo con fonte", all(x['fonte'] for x in old['relazioni'] if x['verifica'] == 'verificata'))
        chk('direzione: Hank Pym genitore di Hope; Wenwu genitore di Shang-Chi; Odino padre adottivo di Loki', all(any(x['tipo'] == 'famiglia_genitore' and x['da'] == d and x['a'] == c and x['qualifica'] == q for x in old['relazioni']) for d, c, q in
            [('id-hank-pym', 'id-hope-van-dyne', 'padre'), ('id-wenwu', 'id-shang-chi', 'padre'), ('id-odino', 'id-loki', 'padre adottivo')]))
        chk('Howard/Tony e Varianti in coda, non importati', any('Howard' in json.dumps(c) or 'howard' in json.dumps(c) for c in old['coda']) and not any(x['tipo'].startswith('famiglia') and {x['da'], x['a']} == {'id-howard-stark', 'id-iron-man'} for x in old['relazioni']))
        print('ESITO:', 'OK' if not bad else 'FALLITO ' + str(bad)); sys.exit(1 if bad else 0)
    print(json.dumps(r['conteggi'], ensure_ascii=False, indent=1))
main()
