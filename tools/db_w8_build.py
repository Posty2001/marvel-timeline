#!/usr/bin/env python3
"""W8: costruzione del canon narrativo da raw/w8_md.json (Marvel Database: categorie/parametri-fatto; Wikidata: etichette esatte di classe «fictional»; Comic Vine: ID/nome).
Voce nuova = Marvel Database + una SECONDA fonte indipendente (D12): (a) elemento Wikidata con etichetta esatta e classe «fictional ...», oppure (b) prima apparizione dell'infobox che
cita una testata presente su Comic Vine (stessa serie). Altrimenti: staging («una sola fonte»). Varianti: pagina «Nome (Earth-N)» + base nel canon + stessa regola; mai fuse con la base
(controparte). Nessun testo copiato; solo titolo, categorie e parametri-fatto brevi. Uso: python3 tools/db_w8_build.py --scrivi | --verifica   (nessuna rete)"""
import json, sys, re, pathlib, unicodedata, collections, hashlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
_argv = sys.argv; sys.argv = ['x', '--solo-runtime']
import db_w1_build as W   # solo funzioni pure (fatti_da, norm); nessun effetto collaterale all'importazione
sys.argv = _argv
R = pathlib.Path(__file__).resolve().parent.parent; E = R / 'data/atlante/espansione'
PREF = {'artefatto': 'art', 'specie': 'sp', 'evento': 'ev', 'entita-cosmica': 'cos', 'universo': 'uni', 'variante': 'var'}
def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s)).strip()
def base(n): return re.sub(r'\s*\([^)]*\)\s*$', '', n or '').strip()
def slug(s): return norm(s).replace(' ', '-')
def serie(t):
    t = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r'\1', t or ''); t = re.sub(r"<[^>]*>|''+|\{\{.*?\}\}", ' ', t)
    t = re.split(r'#|\bVol\b|\(', t)[0]
    return norm(t)
def carica():
    md = json.load(open(E / 'raw/w8_md.json'))
    cv = json.load(open(E / 'raw/cv2_marvel.json'))['risorse']
    return md, cv
def canon_esistente():
    out = []
    for f in sorted((E / 'canon').glob('w*_*.jsonl')):
        if 'arricchimenti' in f.name or f.name == 'w8_narrativo.jsonl': continue
        out += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    return out
def numeri_universo(c, uni_idx):
    out = set(re.findall(r'earth-?\s?(\d+)', (c.get('nome') or '').lower()))
    return out
def costruisci():
    md, cv = carica(); can = canon_esistente(); idx = json.load(open(R / 'atlante2/data/index.json'))
    reg = json.load(open(E / 'ids_registro.json'))['ids']; usati = set(reg) | {c['id'] for c in can}
    volumi = {serie(v['n']) for v in cv['volumes']} | {serie(re.sub(r'\bVol\.? ?\d+', '', v['n'])) for v in cv['volumes']}; volumi.discard('')
    cvnomi = {norm(base(x['n'])) for r in ('characters', 'teams') for x in cv[r]}
    ex = json.load(open(E / 'raw/cv_extra.json'))['risorse'] if (E / 'raw/cv_extra.json').exists() else {}
    CVN = {'artefatto': {norm(base(n)) for _, n in ex.get('objects', [])}, 'specie': {norm(base(n)) for _, n in ex.get('origins', [])},
           'evento': {norm(base(n)) for _, n in ex.get('concepts', [])} | {norm(base(x['n'])) for x in cv['story_arcs']}, 'entita-cosmica': cvnomi | {norm(base(n)) for _, n in ex.get('concepts', [])}, 'universo': set(), 'variante': set()}
    esiste = collections.defaultdict(set)
    for c in can:
        for k in {c['nome'], base(c['nome']), *(c.get('alias') or [])}: esiste[(norm(base(k)))].add(c['tipo'])
    for v in idx['voci']: esiste[norm(base(v['n']))].add({'p': 'identita', 'U': 'universo', 'o': 'organizzazione', 'a': 'artefatto', 'l': 'luogo', 'P': 'pianeta', 'e': 'evento'}.get(v['t'], v['t']))
    num_uni = set()
    for c in can + [{'nome': v['n']} for v in idx['voci'] if v['t'] == 'U']:
        if c.get('tipo', 'universo') == 'universo':
            num_uni |= set(re.findall(r'earth-?\s?(\d+)', c['nome'].lower()))
    for u in idx['meta']['universi'].values(): num_uni |= set(re.findall(r'earth-?\s?(\d+)', u['n'].lower()))
    wd = md.get('wd', {}); pag = md['pagine']
    qid_es = {(c.get('ids_esterni') or {}).get('wikidata') for c in can} | {v.get('ids_esterni', {}).get('wikidata') for v in reg.values()}; qid_es.discard(None)
    out, stag, cont = [], [], collections.Counter()
    def seconda(tipo, titolo, p, nome):
        """Seconda fonte INDIPENDENTE sull'esistenza della voce: Wikidata (etichetta esatta + classe fictional + legame con Marvel) o Comic Vine (nome esatto nella risorsa corrispondente).
        La prima apparizione dell'infobox che cita una testata di Comic Vine NON e' considerata verifica (attesta la serie, non la voce)."""
        s = []
        if wd.get(nome):
            q_ = [q for q in sorted(wd[nome]) if q not in qid_es]
            if q_: s.append(('wikidata', q_[0]))
            else: return None   # elemento Wikidata gia' presente nel canon (voce esistente)
        if len(norm(nome)) >= 4 and norm(nome) in CVN.get(tipo, set()): s.append(('comicvine-nome', nome))
        return s
    def aggiungi(tipo, nome, titolo, p, sec, extra=None, gruppo='w8'):
        rid = PREF[tipo] + '-' + (slug(nome) or hashlib.sha1(titolo.encode()).hexdigest()[:8])
        if rid in usati: rid += '-' + hashlib.sha1(titolo.encode()).hexdigest()[:5]
        usati.add(rid)
        rec = {'id': rid, 'tipo': tipo, 'nome': nome, 'livello': 'C', 'stato_verifica': 'verificata', 'origine': 'W8', 'gruppi': [gruppo], 'ids_esterni': {'marveldb': p['titolo']},
               'fonti': [{'fonte': 'Marvel Database', 'url': p['url'], 'licenza': 'CC BY-SA 3.0'}]}
        for k, v in sec:
            if k == 'wikidata': rec['ids_esterni']['wikidata'] = v; rec['fonti'].append({'fonte': 'Wikidata', 'url': 'https://www.wikidata.org/wiki/' + v, 'licenza': 'CC0'})
            else: rec['fonti'].append({'fonte': 'Comic Vine (corrispondenza per nome)', 'url': 'https://comicvine.gamespot.com/', 'licenza': 'solo ID/nome (nessun testo copiato)'})
        cats = ' | '.join(p.get('categorie', []))
        if tipo != 'universo' and 'Earth-616' in (titolo + ' ' + cats): rec['universo'] = 'uni-earth-616'
        fa = W.fatti_da({'infobox': p.get('infobox', {}), 'sezioni': {}}, tipo)
        if fa:
            rec['fatti'] = fa; rec['fatti_fonti'] = {k: ['marveldb'] for k in fa}
        if extra: rec.update(extra)
        out.append(rec); cont['nuovi:' + tipo] += 1
    # 1) membri di categoria
    visti = set()
    conta = collections.Counter((m['tipo'], norm(base(t))) for c_, m in md['membri'].items() if not c_.startswith('prefisso:') for t in dict.fromkeys(m['t']))
    COSM = {'Abstract Entities', 'Celestials', 'Alien Gods', 'Dimensional Rulers', 'Pantheons', 'Elder Gods', 'Living Embodiments', 'Cosmic Entities'}
    for cat, m in md['membri'].items():
        tipo = m['tipo']
        if cat.startswith('prefisso:'): continue
        for t in m['t']:
            p = pag.get(t)
            if not p or p['disambigua'] or (tipo, t) in visti: continue
            visti.add((tipo, t)); nome = base(t)
            if tipo == 'entita-cosmica' and not (COSM & set(p.get('categorie', []))): cont['cosmica: categoria non pertinente'] += 1; continue
            if conta[(tipo, norm(nome))] > 1: nome = t   # omonimi tra continuita': il titolo completo distingue (mai fusi)
            if not nome or len(nome) > 70: continue
            if tipo in esiste.get(norm(base(nome)), ()) or (tipo == 'entita-cosmica' and 'identita' in esiste.get(norm(base(nome)), ())): cont['gia presente'] += 1; continue
            if tipo in ('artefatto', 'specie', 'evento') and re.search(r'\b(Earth-\d+|Vol \d+|Vol\.)', t) and tipo != 'artefatto': cont['titolo con universo/volume'] += 1
            sec = seconda(tipo, t, p, base(nome))
            if sec is None: cont['gia presente (QID)'] += 1; continue
            if not sec: stag.append({'nome': nome, 'tipo': tipo, 'marveldb': t, 'motivo': 'una sola fonte (Marvel Database): resta in staging (D12)'}); cont['staging'] += 1; continue
            aggiungi(tipo, nome, t, p, sec)
    # 2) universi «Earth-N»
    for k, m in md['membri'].items():
        if not k.startswith('prefisso:'): continue
        for t in m['t']:
            n = re.match(r'^Earth-(\d+)$', t)
            if not n or n.group(1) in num_uni: continue
            p = pag.get(t)
            if not p or p['disambigua']: continue
            sec = seconda('universo', t, p, t)
            if sec is None: cont['gia presente (QID)'] += 1; continue
            if not sec: stag.append({'nome': t, 'tipo': 'universo', 'marveldb': t, 'motivo': 'una sola fonte (Marvel Database): resta in staging (D12)'}); cont['staging'] += 1; continue
            num_uni.add(n.group(1)); aggiungi('universo', t, t, p, sec)
    # 3) varianti: «Nome (Earth-N)» di un personaggio gia' nel canon/storico, universo diverso da Earth-616
    ident = collections.defaultdict(list)
    for c in can:
        if c['tipo'] == 'identita': ident[norm(base(c['nome']))].append(c['id'])
    for v in idx['voci']:
        if v['t'] == 'p': ident[norm(base(v['n']))].append(v['i'])
    uni_ids = {}
    for c in can + out:
        if c['tipo'] == 'universo':
            for nn_ in re.findall(r'earth-?\s?(\d+)', c['nome'].lower()): uni_ids.setdefault(nn_, c['id'])
    for v in idx['voci']:
        if v['t'] == 'U':
            for nn_ in re.findall(r'earth-?\s?(\d+)', v['n'].lower()): uni_ids.setdefault(nn_, v['i'])
    for nome_base, tit in md['varianti'].items():
        base_ids = ident.get(norm(nome_base), [])
        if not base_ids: cont['variante senza base'] += 1; continue
        for t in tit:
            mm = re.match(r'^(.*) \(Earth-(\d+)\)$', t)
            if not mm or mm.group(2) == '616': continue
            p = pag.get(t)
            if not p or p['disambigua'] or 'Characters' not in ' '.join(p.get('categorie', [])) and not p.get('infobox'): continue
            if norm(mm.group(1)) != norm(nome_base): continue
            nm = '%s (Earth-%s)' % (mm.group(1), mm.group(2))
            if 'variante' in esiste.get(norm(base(nm)), ()) and False: continue
            sec = seconda('variante', t, p, nm)
            if sec is None: continue
            if not sec: stag.append({'nome': nm, 'tipo': 'variante', 'marveldb': t, 'base': base_ids[0], 'motivo': 'una sola fonte (Marvel Database): resta in staging (D12)'}); cont['staging'] += 1; continue
            ex = {'gruppi': ['w8:variante', 'base:' + base_ids[0]]}
            if mm.group(2) in uni_ids: ex['universo'] = uni_ids[mm.group(2)]
            aggiungi('variante', nm, t, p, sec, ex, 'w8:variante')
    return out, stag, cont
def main():
    out, stag, cont = costruisci()
    if '--scrivi' in sys.argv:
        (E / 'canon/w8_narrativo.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in out) + '\n')
        (E / 'staging/w8_staging.jsonl').write_text('\n'.join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in stag) + '\n')
        json.dump({'nuovi': len(out), 'staging': len(stag), 'dettaglio': dict(cont)}, open(E / 'w8_conteggi.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({'nuovi': len(out), 'staging': len(stag), **dict(cont)}, ensure_ascii=False))
if __name__ == '__main__': main()
