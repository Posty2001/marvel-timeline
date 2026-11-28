#!/usr/bin/env python3
"""Dossier discorsivi in ITALIANO (livello A) generati ESCLUSIVAMENTE da fatti verificati del canon: nessun testo copiato dalle fonti, nessuna informazione aggiunta, nessuna IA a pagamento.
Frasi originali costruite da modelli fissi; i termini tecnici non tradotti (poteri, ruoli, titoli) restano nella lingua originale tra virgolette. Un dossier si genera solo se ci sono almeno 3 sezioni con dati.
Selezione dei «personaggi principali»: identita' di Livello B + identita' con >= 3 relazioni narrative verificate oppure ordinate tra le prime fasce di rilevanza (fumetti 40+/20-40 collegamenti Wikipedia).
Uso: python3 tools/db_dossier.py [--scrivi]  ->  data/atlante/espansione/dossier_it.json"""
import json, pathlib, re, sys, collections
R = pathlib.Path(__file__).resolve().parent.parent; E = R/'data/atlante/espansione'
GEN = {'male': 'maschile', 'female': 'femminile'}
STATO = {'alive': 'in vita', 'deceased': 'deceduto', 'dead': 'deceduto', 'unknown': 'di stato non noto', 'living': 'in vita'}
REL = {'famiglia_genitore': ('genitore di', 'figlio/a di'), 'famiglia_coniugi': ('coniuge di', 'coniuge di'), 'famiglia_fratelli': ('fratello/sorella di', 'fratello/sorella di'),
       'partner': ('partner di', 'partner di'), 'rivalita': ('rivale di', 'rivale di'), 'mentorato': ('mentore di', 'allievo/a di'), 'appartenenza': ('membro di', 'ha tra i membri')}
def lista(v, n=8):
    v = [x for x in dict.fromkeys(v) if x][:n]
    return ', '.join('«%s»' % x for x in v)
def pulisci(x): return re.sub(r'\s+', ' ', x or '').strip()
def componi(r, rels, nomi):
    f = r.get('fatti', {}); S = []
    nome = r['nome']
    # 1) Identita'
    fr = []
    if f.get('nome_reale'): fr.append('Nome reale o di nascita secondo le fonti: %s.' % pulisci(f['nome_reale'] if isinstance(f['nome_reale'], str) else '; '.join(f['nome_reale'])))
    pr = []
    if f.get('genere') and str(f['genere']).lower() in GEN: pr.append('di genere %s' % GEN[str(f['genere']).lower()])
    if f.get('specie'): pr.append('appartenente a: %s' % lista(f['specie'], 3))
    if f.get('stato') and str(f['stato']).lower() in STATO: pr.append('attualmente %s secondo le fonti' % STATO[str(f['stato']).lower()])
    if pr: fr.append('%s è un personaggio %s.' % (nome, ', '.join(pr)))
    if f.get('cittadinanza'): fr.append('Cittadinanza documentata: %s.' % lista(f['cittadinanza'], 4))
    if f.get('occupazione'): fr.append('Occupazioni documentate: %s.' % lista(f['occupazione'], 5))
    if r.get('alias'): fr.append('È noto anche come %s.' % lista(r['alias'], 6))
    if fr: S.append(('Identità', ' '.join(fr)))
    # 2) Poteri e abilita'
    pa = []
    if f.get('poteri'): pa.append('Poteri documentati: %s.' % lista(f['poteri']))
    if f.get('abilita'): pa.append('Abilità: %s.' % lista(f['abilita']))
    if f.get('equipaggiamento'): pa.append('Equipaggiamento: %s.' % lista(f['equipaggiamento'], 6))
    if f.get('debolezze'): pa.append('Debolezze: %s.' % lista(f['debolezze'], 5))
    if pa: S.append(('Poteri, abilità ed equipaggiamento', ' '.join(pa)))
    # 3) Affiliazioni e luoghi
    af = []
    if f.get('affiliazioni'): af.append('Affiliazioni citate dalle fonti: %s.' % lista(f['affiliazioni'], 8))
    if f.get('ubicazione'): af.append('Luoghi collegati: %s.' % lista(f['ubicazione'], 5))
    if af: S.append(('Affiliazioni e luoghi', ' '.join(af)))
    # 4) Relazioni documentate (verificate)
    rl = []
    for t, da, a in rels:
        ver, inv = REL.get(t, (None, None))
        if not ver: continue
        altro = nomi.get(a if da == r['id'] else da)
        if not altro: continue
        rl.append('%s %s' % (ver if da == r['id'] else inv, altro))
    if rl: S.append(('Relazioni narrative verificate', '%s è: %s.' % (nome, '; '.join(dict.fromkeys(rl[:8])))))
    # 5) Interpreti e apparizioni
    ap = []
    ip = r.get('interpreti') or f.get('interpreti_fonte')
    if ip: ap.append('Interpretato da %s.' % ', '.join(dict.fromkeys(ip)))
    for k, lab in (('apparizioni_narrativa', 'nella continuità narrativa'), ('apparizioni_alternativi', 'in universi alternativi'), ('apparizioni_fumetti', 'nei fumetti'), ('apparizioni_videogiochi', 'nei videogiochi'), ('apparizioni_adattamenti', 'in adattamenti e opere derivate')):
        if f.get(k): ap.append('Apparizioni %s (esempi): %s.' % (lab, lista(f[k], 4)))
    if ap: S.append(('Interpreti e apparizioni', ' '.join(ap)))
    return S
def main():
    rels = collections.defaultdict(list); nomi = {}
    for x in json.load(open(E/'relazioni_db.json'))['relazioni']:
        if x['verifica'] == 'verificata' and x['classe'] == 'narrativa': rels[x['da']].append((x['tipo'], x['da'], x['a'])); rels[x['a']].append((x['tipo'], x['da'], x['a']))
    canon = {}
    for f in sorted((E/'canon').glob('w*_*.jsonl')):
        if 'arricch' in f.name: continue
        for l in f.read_text().splitlines():
            if l.strip(): r = json.loads(l); canon.setdefault(r['id'], r)
    for i, v in json.load(open(R/'atlante2/data/index.json')).items() if False else []: pass
    idx = {v['i']: v['n'] for v in json.load(open(R/'atlante2/data/index.json'))['voci']}
    for i, r in canon.items(): nomi[i] = r['nome']
    for i, n in idx.items(): nomi.setdefault(i, n)
    out = {}
    for i, r in canon.items():
        if r['tipo'] != 'identita': continue
        top = r.get('livello') == 'B' or len(rels.get(i, [])) >= 3 or any(g.startswith(('fumetti:40', 'fumetti:20-40', 'fumetti_pubbl:40', 'fumetti_pubbl:20-40')) for g in r.get('gruppi', []))
        if not top: continue
        S = componi(r, rels.get(i, []), nomi)
        if len(S) >= 3: out[i] = {'sezioni': [{'t': t, 'x': x} for t, x in S], 'generato': 'da fatti verificati del canon (nessun testo copiato)'}
    print(json.dumps({'dossier': len(out), 'candidati_top': sum(1 for r in canon.values() if r['tipo'] == 'identita')}))
    if '--scrivi' in sys.argv:
        (E/'dossier_it.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n')
    return out
if __name__ == '__main__':
    o = main()
    for k in list(o)[:1]: print(json.dumps(o[k], ensure_ascii=False, indent=1)[:1500])
