#!/usr/bin/env python3
"""W1 - costruzione OFFLINE da raw Wikidata: classifica -> risolve (dedup) -> valida (D12) -> canon/staging/coda -> indice runtime.
Uso: python3 tools/db_w1_build.py <raw.json> [--scrivi]   (senza --scrivi: simulazione con conteggi)
Regole: ID storici mai toccati; match esatto (nome/alias) = ARRICCHIMENTO (mai riscrittura); match parziale/multiplo = coda di revisione e voce trattenuta;
persone distinte mai fuse; nessun testo narrativo (solo campi strutturati + descrizione breve Wikidata CC0); Livello C."""
import json, sys, re, unicodedata, pathlib, collections, zlib, gzip, hashlib
import os
R = pathlib.Path(os.environ.get('DB_ROOT') or pathlib.Path(__file__).resolve().parent.parent)
E = R/'data/atlante/espansione'
OUTRT = R/'atlante2/data/db'
def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def slug(s): return norm(s).replace(' ', '-')
PREF = {'identita':'id','organizzazione':'org','artefatto':'art','luogo':'luo','pianeta':'pia','evento':'ev','battaglia':'bat','specie':'sp','civilta':'civ',
        'opera':'op','attore':'att','creatore':'cr','universo':'uni','entita-cosmica':'cos'}
# P31 (etichetta en, minuscola) -> tipo. Ordine = priorita'.
REGOLE = [
 ('episodio', ('television series episode','episode of','television season','season of')),
 ('battaglia', ('fictional battle','fictional war')),
 ('evento', ('fictional event','fictional conflict')),
 ('pianeta', ('fictional planet','fictional star','fictional moon','fictional celestial')),
 ('universo', ('fictional universe','fictional dimension','fictional realm','fictional plane of existence','fictional world')),
 ('organizzazione', ('fictional television network','fictional television station','fictional newspaper','fictional news ','fictional media')),
 ('luogo', ('fictional facility','fictional apartment','fictional residence','fictional restaurant','fictional house','fictional drinking establishment','fictional store','fictional hospital','fictional shop','fictional military base','fictional laboratory','fictional high or secondary school','fictional hotel','fictional diner','fictional university','fictional caf','fictional club','fictional police station','fictional bar','fictional bank','fictional office','fictional museum','fictional church','fictional street','fictional park','fictional airport','fictional bridge','fictional neighborhood','fictional neighbourhood','fictional district','fictional headquarters','fictional laboratory','fictional gym','fictional theater','fictional theatre','fictional casino','fictional warehouse','fictional factory','fictional hideout','fictional lair','fictional base','fictional embassy','fictional castle','fictional temple','fictional palace','fictional tower','fictional station','fictional location','fictional city','fictional country','fictional building','fictional locale','fictional state','fictional nation','fictional island','fictional prison','fictional school','fictional place','fictional town','fictional village','fictional kingdom','fictional continent','fictional region','fictional organization headquarters')),
 ('civilta', ('fictional civilization','fictional nation state','fictional empire')),
 ('specie', ('fictional species','fictional race','fictional alien species','fictional ethnic group','fictional mutant species','fictional population')),
 ('organizzazione', ('fictional organization','fictional organisation','fictional team','superhero team','fictional intelligence agency','fictional government','fictional criminal organization','fictional company','fictional military unit','fictional group','fictional corporation','fictional agency','fictional institution','fictional secret society','fictional gang','fictional cult','fictional religion','fictional political party','fictional army')),
 ('artefatto', ('fictional armor','fictional armour','fictional automobile','fictional car','fictional suit','fictional weapon','fictional object','fictional artifact','fictional artefact','fictional material','fictional element','fictional technology','fictional vehicle','fictional item','fictional gem','fictional device','fictional spacecraft','fictional aircraft','fictional ship','fictional substance','fictional metal','fictional book','fictional magic','fictional language','fictional currency','fictional drug','fictional food')),
 ('entita-cosmica', ('fictional deity','fictional god','fictional cosmic entity','fictional entity','fictional celestial being','fictional demon','fictional spirit','fictional monster','fictional being','fictional creature')),
 ('identita', ('comics character','television character','film character','fictional human','fictional character','fictional alien','fictional robot','superhero','supervillain','fictional mutant','fictional animal','fictional cyborg','fictional android','fictional humanoid','fictional person','fictional hero','fictional villain','fictional antihero','fictional artificial intelligence','fictional extraterrestrial','fictional wizard','fictional sorcerer','fictional soldier','fictional spy','fictional scientist','fictional journalist','fictional lawyer','fictional physician','fictional criminal','fictional dog','fictional cat','fictional monkey','fictional bird','fictional dragon','fictional vampire','fictional zombie','fictional superhuman','fictional giant','fictional dwarf','fictional elf','fictional genius','fictional pirate','fictional president','fictional politician','fictional king','fictional queen','fictional prince','fictional princess','fictional warrior','fictional knight','fictional witch','fictional thief','fictional assassin','fictional mercenary','fictional detective','fictional doctor','fictional teacher','fictional student','fictional child','fictional woman','fictional man','fictional girl','fictional boy','fictional fictional character','fictional demigod','fictional ghost','fictional mutant character','fictional inventor','fictional engineer','fictional pilot','fictional astronaut','fictional agent','fictional officer','fictional commander','fictional captain','fictional general','fictional emperor','fictional priest','fictional monk','fictional sorceress')),
 ('opera', ('film','television series','animated series','animated film','video game','web series','short film','television film','miniseries','anthology','television program','animated television series','film series','media franchise','comic book series','novel','book series','tv series','streaming','documentary','television special','one-shot')),
]
def classifica(p31_labels, gruppi):
    L = [x.lower() for x in p31_labels if x]
    for tipo, keys in REGOLE:
        for l in L:
            if any(l == k or l.startswith(k) or k in l for k in keys): return tipo
    if 'human' in L:
        if 'interpreti_MCU' in gruppi: return 'attore'
        if 'creatori_MCU' in gruppi: return 'creatore'
    return None
def carica_esistente():
    idx = json.load(open(R/'atlante2/data/index.json'))['voci']
    ide = {x['id']: x for x in json.load(open(R/'data/atlante/identita.json'))['identita']}
    pieni = collections.defaultdict(set); parz = collections.defaultdict(set)
    for v in idx:
        keys = {norm(v['n'])} | {norm(a) for a in ide.get(v['i'], {}).get('alias', [])}
        for k in keys:
            if k: pieni[k].add(v['i'])
        nome = v['n']; base = re.sub(r'\s*\(.*?\)', '', nome)
        par = set(re.findall(r'\(([^)]*)\)', nome))
        for k in {norm(base)} | {norm(x) for x in re.split(r'[/,]', base)} | {norm(x) for x in par}:
            if k and k not in keys: parz[k].add(v['i'])
    return idx, pieni, parz
def qnum(q): return int(q[1:])
def main():
    raw = json.load(open(sys.argv[1])); scrivi = '--scrivi' in sys.argv
    ent, et = raw['entita'], raw['etichette']
    mcu = {q for q, l in et.items() if l == 'Marvel Cinematic Universe'}
    idx, pieni, parz = carica_esistente(); tipo_esist = {v['i']: v['t'] for v in idx}
    reg = json.load(open(E/'ids_registro.json'))['ids']
    q2id = {v['ids_esterni']['wikidata']: k for k, v in reg.items() if v.get('ids_esterni', {}).get('wikidata')}
    usati = set(reg)
    canon, stag, coda, arr = [], [], collections.defaultdict(list), []
    cont = collections.Counter()
    for q in sorted(ent, key=qnum):
        r = ent[q]; nome = r['l'].get('en')
        p31 = [et.get(x) for x in r['c'].get('P31', [])]
        tipo = classifica(p31, r['g'])
        mot = None
        if not nome: mot = 'senza etichetta inglese'
        elif tipo is None: mot = 'classe non riconosciuta: ' + '|'.join(x for x in p31 if x)[:80]; coda['non_classificati'].append({'q': q, 'nome': nome, 'p31': p31})
        elif tipo == 'episodio': mot = 'episodio/stagione: fuori ambito W1'
        if mot:
            cont['staging:' + (tipo or 'n/d')] += 1; stag.append({'q': q, 'nome': nome, 'tipo': tipo, 'motivo': mot}); continue
        alias = sorted({a for l in ('en', 'it') for a in r['a'].get(l, []) if a} | ({r['l']['it']} if r['l'].get('it') and r['l']['it'] != nome else set()))
        chiavi = {norm(nome)} | {norm(a) for a in alias} | ({norm(re.sub(r'\s*\(.*?\)', '', r['sl']['itwiki']))} if r['sl'].get('itwiki') else set())
        # risoluzione contro l'archivio storico: solo tipi compatibili contano
        compat = {'identita': 'p', 'universo': 'U', 'organizzazione': 'o', 'artefatto': 'a', 'luogo': 'l', 'pianeta': 'P', 'evento': 'e', 'opera': 't', 'attore': None, 'creatore': None}
        full = set().union(*[pieni.get(k, set()) for k in chiavi if k]) if chiavi else set()
        full = {i for i in full if compat.get(tipo) is None or tipo_esist[i] == compat.get(tipo) or tipo_esist[i] in ('h', 'm')}
        part = set().union(*[parz.get(k, set()) for k in chiavi if k])
        part = {i for i in part if compat.get(tipo) is None or tipo_esist[i] == compat.get(tipo)} - full
        if tipo not in ('identita', 'attore', 'creatore', 'opera') and not full:
            # categorie non-persona: l'archivio storico e' in italiano e Wikidata spesso non ha l'etichetta italiana -> confronto cross-lingua per token distintivi
            STOP = {'battle', 'battaglia', 'stone', 'stones', 'gemma', 'armor', 'armour', 'infinity', 'avengers', 'universe', 'realm', 'earth'}
            tk = {w for k in chiavi for w in k.split() if len(w) >= 5} - STOP
            for v in idx:
                if compat.get(tipo) == v['t'] and tk & ({w for w in norm(v['n']).split() if len(w) >= 5} - STOP): part.add(v['i'])
        if len(full) == 1 and not part:
            arr.append({'id': next(iter(full)), 'wikidata': q, 'alias_nuovi': [a for a in alias if norm(a) not in pieni or next(iter(full)) not in pieni[norm(a)]][:20],
                        'interpreti': sorted({et.get(x) for x in r['c'].get('P175', []) if et.get(x)}), 'fonte': 'Wikidata (CC0)'}); cont['arricchimento'] += 1; continue
        if full or part:
            coda['possibili_duplicati'].append({'q': q, 'nome': nome, 'tipo': tipo, 'esistenti_esatti': sorted(full), 'esistenti_parziali': sorted(part)})
            stag.append({'q': q, 'nome': nome, 'tipo': tipo, 'motivo': 'possibile duplicato: in coda di revisione'}); cont['coda_duplicati'] += 1; continue
        # D12: dichiarazione Wikidata + articolo Wikipedia indipendente (en) => verificata a livello di identita'/esistenza; altrimenti staging
        if not ({'enwiki', 'itwiki'} & set(r['sl'])):
            stag.append({'q': q, 'nome': nome, 'tipo': tipo, 'motivo': 'una sola fonte (nessun articolo Wikipedia): resta in staging (D12)'}); cont['staging:una_fonte'] += 1; continue
        if q in q2id: rid = q2id[q]
        else:
            base = PREF[tipo] + '-' + (slug(nome) or q.lower()); rid = base
            if rid in usati: rid = base + '-' + q.lower()
        usati.add(rid)
        uni = 'uni-earth-199999-mcu' if (mcu & set(r['c'].get('P1080', []))) else None
        rec = {'id': rid, 'tipo': tipo, 'nome': nome, 'livello': 'C', 'stato_verifica': 'verificata', 'origine': 'W1',
               'ids_esterni': {'wikidata': q}, 'gruppi': r['g'],
               'fonti': [{'fonte': 'Wikidata', 'url': 'https://www.wikidata.org/wiki/' + q, 'licenza': 'CC0'},
                         {'fonte': 'Wikipedia (en) - solo riferimento', 'url': ('https://en.wikipedia.org/wiki/' + r['sl']['enwiki'].replace(' ', '_')) if 'enwiki' in r['sl'] else ('https://it.wikipedia.org/wiki/' + r['sl']['itwiki'].replace(' ', '_')), 'licenza': 'CC BY-SA 4.0 (nessun testo copiato)'}]}
        if r['l'].get('it') and r['l']['it'] != nome: rec['nome_it'] = r['l']['it']
        if alias: rec['alias'] = alias
        if uni: rec['universo'] = uni
        d = {k: v for k, v in r['d'].items() if v}
        if d: rec['descrizione'] = d
        ip = sorted({et.get(x) for x in r['c'].get('P175', []) if et.get(x)})
        if ip: rec['interpreti'] = ip
        rec['wikipedia'] = {k[:2]: v for k, v in r['sl'].items()}
        canon.append(rec); cont['canon:' + tipo] += 1
    ris = {'canon': len(canon), 'staging': len(stag), 'arricchimenti': len(arr), 'coda': {k: len(v) for k, v in coda.items()}, 'per_tipo': {k[6:]: v for k, v in cont.items() if k.startswith('canon:')},
           'staging_per_motivo': dict(collections.Counter(x['motivo'].split(':')[0] for x in stag)), 'mcu_qid': sorted(mcu), 'input_entita': len(ent)}
    print(json.dumps(ris, ensure_ascii=False, indent=1))
    if not scrivi: return
    (E/'canon').mkdir(exist_ok=True); (E/'staging').mkdir(exist_ok=True); (E/'review').mkdir(exist_ok=True)
    w = lambda p, rows: (E/p).write_text('\n'.join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in rows) + ('\n' if rows else ''))
    w('canon/w1_mcu.jsonl', canon); w('canon/w1_arricchimenti.jsonl', arr); w('staging/w1_staging.jsonl', stag)
    json.dump(dict(coda), open(E/'review/w1_coda.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    json.dump(ris, open(E/'w1_conteggi.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    import subprocess; subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve().parent/'db_ids.py'), '--scrivi'], check=True, env=dict(__import__('os').environ, DB_ROOT=str(R)))
    costruisci_runtime(canon, arr)
SH, CH = 16, 500
def costruisci_runtime(canon, arr):
    import shutil
    if OUTRT.exists(): shutil.rmtree(OUTRT)
    (OUTRT/'n').mkdir(parents=True); (OUTRT/'t').mkdir()
    recs = []
    for c in sorted(canon, key=lambda x: x['id']):
        recs.append({'i': c['id'], 'n': c['nome'], 'it': c.get('nome_it'), 't': c['tipo'], 'al': c.get('alias', []), 'd': (c.get('descrizione', {}).get('it') or c.get('descrizione', {}).get('en')),
                     'u': c.get('universo'), 'ip': c.get('interpreti', []), 'wd': c['ids_esterni']['wikidata'], 'wp': c.get('wikipedia', {}).get('en')})
    for a in arr:  # alias/interpreti di voci GIA' esistenti: servono solo alla ricerca (aprono la scheda esistente)
        recs.append({'i': a['id'], 'x': a['id'], 'n': a['id'], 't': 'x', 'al': a['alias_nuovi'] + a['interpreti'], 'wd': a['wikidata']})
    sh = [dict() for _ in range(SH)]
    for o, r in enumerate(recs):
        keys = [r['n'], r.get('it') or ''] + r['al'] + r.get('ip', []) if r['t'] != 'x' else r['al']
        tri = set()
        for k in keys:
            for wd in norm(k).split():
                for i in range(len(wd) - 2): tri.add(wd[i:i + 3])
        for t in tri: sh[zlib.crc32(t.encode()) % SH].setdefault(t, []).append(o)
    pre = {}
    for o, r in enumerate(recs):
        for k in ([r['n'], r.get('it') or ''] + r['al'] + r.get('ip', []) if r['t'] != 'x' else r['al']):
            for wd in norm(k).split():
                if len(wd) >= 1: pre.setdefault(wd[:2].ljust(2, '_'), set()).add(o)
    for c in range(0, len(recs), CH):
        (OUTRT/'n'/f'{c//CH}.json').write_text(json.dumps(recs[c:c + CH], ensure_ascii=False, separators=(',', ':')))
    for s in range(SH):
        d = {}
        for t, l in sh[s].items():
            prev = 0; dl = []
            for x in sorted(l): dl.append(x - prev); prev = x
            d[t] = dl
        (OUTRT/'t'/f'{s}.json').write_text(json.dumps(d, separators=(',', ':')))
    (OUTRT/'pre.json').write_text(json.dumps({p: sorted(l)[:300] for p, l in pre.items()}, separators=(',', ':')))
    tot = sum(len(gzip.compress(p.read_bytes())) for p in OUTRT.rglob('*.json'))
    (OUTRT/'meta.json').write_text(json.dumps({'versione': 1, 'N': len(recs), 'SH': SH, 'CH': CH, 'nuove': len(canon), 'arricchite': len(arr), 'gz': tot}))
    print('runtime db:', len(recs), 'record, gz', tot, 'byte')
if __name__ == '__main__': main()
