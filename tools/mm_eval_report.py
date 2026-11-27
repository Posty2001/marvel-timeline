#!/usr/bin/env python3
"""Fase C - report di valutazione di Miss Minutes 2.0 a partire dalle risposte REALI raccolte in-app.

Uso:
  python3 tools/mm_eval_report.py [--risultati miss-minutes/eval/risultati.json] [--manuale miss-minutes/eval/manuale.json] [--md docs/...md]
  python3 tools/mm_eval_report.py --autotest          # prova dello strumento su dati SINTETICI (mai presentati come reali)

Metriche: accuratezza, freschezza, correttezza delle fonti, allucinazioni, latenza, capacita' di dichiarare incertezza.
I criteri automatici sono INDICATIVI: un `no` che scatta e' una SOSPETTA allucinazione (da confermare), mai una prova.
`manuale.json` = {"<id>": "corretta|sbagliata|incerta"} sovrascrive l'esito automatico. Nessun dato inventato: senza risultati reali il report lo dice.
"""
import argparse, json, os, re, statistics, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(R, *p)
HEDGE = re.compile(r"non (è|sono|risulta|posso|so|ho|abbiamo|mi risulta|ci sono|esiste)\b.{0,60}?(confermat|ufficial|sicur|certo|noto|verificat|disponibil|annunciat|informazion|dati|prove|esist)|non lo so|non (ne )?ho (informazioni|dati|certezz)|non posso (confermare|verificare)|ipotes|speculaz|teori|\bvoci\b|rumor|potrebbe|potrebbero|incert|non (risulta|esiste)|non ancora|non sono riuscit", re.I)
OKHOST = re.compile(r"^https://([a-z0-9-]+\.)*(themoviedb\.org|wikipedia\.org|wikidata\.org|marvel\.com|disneyplus\.com)(/|$)", re.I)
FACT = ('fatto', 'fresco')

def rx(l): return [re.compile(x, re.I) for x in (l or [])]
def grade(dom, rec):
    """-> (esito, motivo, sospetta_allucinazione)"""
    if not rec or not rec.get('ok'): return ('assente', rec.get('code', 'nessuna risposta') if rec else 'non eseguita', False)
    t = rec['text']; hedge = bool(HEDGE.search(t)); sus = any(r.search(t) for r in rx(dom.get('no')))
    anyok = (not dom.get('ok')) or any(r.search(t) for r in rx(dom['ok']))
    allok = all(r.search(t) for r in rx(dom.get('tutti')))
    tipo = dom['tipo']; vfok = (rec.get('vf') or {}).get('ok', True)
    if tipo == 'incerto':
        return ('corretta', 'dichiara incertezza', False) if hedge else ('sbagliata', 'affermazione senza dichiarare incertezza', True)
    if sus: return ('sbagliata', 'contiene un\'affermazione attesa come errata (da confermare)', True)
    if anyok and allok: return ('corretta', 'attesa soddisfatta', False)
    if hedge and dom.get('hedge'): return ('incerta', 'incertezza dichiarata invece della risposta', False)
    if tipo == 'falsa': return ('sbagliata', 'premessa falsa avallata', True)
    if not vfok and hedge: return ('incerta', 'verifica non superata: passaggio omesso con dichiarazione', False)
    return ('sbagliata', 'attesa non soddisfatta' + ('' if anyok else ' (dato atteso assente)') + ('' if allok else ' (elementi mancanti)'), False)

def pct(a, b): return '%.0f%%' % (100.0 * a / b) if b else 'n/d'
def med(v): return int(statistics.median(v)) if v else 0
def p90(v):
    if not v: return 0
    v = sorted(v); return int(v[min(len(v) - 1, int(round(0.9 * (len(v) - 1))))])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--risultati', default=None); ap.add_argument('--manuale', default=D('miss-minutes', 'eval', 'manuale.json'))
    ap.add_argument('--md'); ap.add_argument('--autotest', action='store_true'); a = ap.parse_args()
    dom = json.load(open(D('miss-minutes', 'eval', 'domande.json')))['domande']; byid = {d['id']: d for d in dom}
    if a.autotest: return autotest(dom)
    if not a.risultati:   # file esportato dall'iPhone (miss-minutes-valutazione-AAAAMMGG-HHMM.json) piu' recente, altrimenti risultati.json
        import glob
        cand = sorted(glob.glob(D('miss-minutes', 'eval', 'miss-minutes-valutazione-*.json')) + glob.glob(D('miss-minutes', 'eval', 'risultati.json')))
        a.risultati = cand[-1] if cand else D('miss-minutes', 'eval', 'risultati.json')
    if not os.path.exists(a.risultati):
        print('NESSUN RISULTATO REALE: %s non esiste. Esegui la valutazione in-app (Impostazioni → Valutazione risposte), copia il JSON e salvalo qui.' % a.risultati); return 2
    raw = json.load(open(a.risultati)); recs = {r['id']: r for r in raw['risultati']}
    man = json.load(open(a.manuale)) if os.path.exists(a.manuale) else {}
    rows = []
    for d in dom:
        r = recs.get(d['id']); e, why, sus = grade(d, r)
        if d['id'] in man: e, why = {'corretta': 'corretta', 'sbagliata': 'sbagliata', 'incerta': 'incerta'}.get(man[d['id']], e), 'giudizio manuale'; sus = sus and e == 'sbagliata'
        rows.append({'d': d, 'r': r, 'esito': e, 'why': why, 'sus': sus})
    done = [x for x in rows if x['esito'] != 'assente']; n = len(done)
    L = []; A = L.append
    A('# Miss Minutes 2.0 — fase C: risultati della valutazione sulle risposte reali\n')
    A('Origine: `%s` · avvio %s · fine %s · domande eseguite %d/%d%s.\n' % (os.path.relpath(a.risultati, R), raw.get('avvio'), raw.get('fine'), n, len(dom), ' · INTERROTTA PER QUOTA' if raw.get('quota') else ''))
    A('> I criteri automatici sono indicativi (`miss-minutes/eval/domande.json`); i giudizi manuali dell\'utente (`manuale.json`) prevalgono. Nessuna correzione specifica per singola domanda: i difetti emersi vanno risolti con regole generali.\n')
    c = lambda s: sum(1 for x in done if x['esito'] == s)
    A('## Sintesi\n'); A('| Metrica | Valore |'); A('|---|---|')
    A('| Risposte corrette (attesa soddisfatta) | %d/%d (%s) |' % (c('corretta'), n, pct(c('corretta'), n)))
    A('| Incertezza dichiarata al posto della risposta | %d/%d (%s) |' % (c('incerta'), n, pct(c('incerta'), n)))
    A('| Risposte sbagliate | %d/%d (%s) |' % (c('sbagliata'), n, pct(c('sbagliata'), n)))
    A('| Accuratezza «sicura» (corrette + incertezza dichiarata) | %s |' % pct(c('corretta') + c('incerta'), n))
    # allucinazioni
    fact = [x for x in done if x['d']['tipo'] in FACT]
    sus = [x for x in done if x['sus']]
    A('| Sospette allucinazioni (da confermare) | %d/%d (%s) |' % (len(sus), n, pct(len(sus), n)))
    wrongconf = [x for x in fact if x['esito'] == 'sbagliata']
    A('| Errori su domande di fatto con tono sicuro | %d/%d (%s) |' % (len(wrongconf), len(fact), pct(len(wrongconf), len(fact))))
    vfs = [x for x in done if (x['r'].get('vf') or {}).get('ok') is False]; ret = [x for x in done if (x['r'].get('vf') or {}).get('retried')]
    A('| Interventi del verificatore (passaggio omesso / rigenerato) | %d omessi · %d rigenerati |' % (len(vfs), len(ret)))
    # freschezza
    fr = [x for x in done if x['d']['tipo'] == 'fresco']
    A('| Freschezza (domande su uscite/novità: corrette o incertezza) | %d/%d (%s) |' % (sum(1 for x in fr if x['esito'] in ('corretta', 'incerta')), len(fr), pct(sum(1 for x in fr if x['esito'] in ('corretta', 'incerta')), len(fr))))
    A('| …di cui con dato aggiornato esatto | %s |' % pct(sum(1 for x in fr if x['esito'] == 'corretta'), len(fr)))
    lkn = sum(1 for x in done if (x['r'].get('lk') or {}).get('net')); lkc = sum(1 for x in done if (x['r'].get('lk') or {}).get('cache')); lkk = sum(1 for x in done if (x['r'].get('lk') or {}).get('ko'))
    A('| Ricerche Wikipedia/Wikidata: in rete / da cache / non riuscite (risposte) | %d / %d / %d |' % (lkn, lkc, lkk))
    # incertezza
    inc = [x for x in done if x['d']['tipo'] in ('incerto', 'falsa')]
    A('| Capacità di dichiarare incertezza o smentire (teorie + false premesse) | %d/%d (%s) |' % (sum(1 for x in inc if x['esito'] in ('corretta', 'incerta')), len(inc), pct(sum(1 for x in inc if x['esito'] in ('corretta', 'incerta')), len(inc))))
    # fonti
    withsrc = [x for x in fact if x['r'].get('srcs')]
    badurl = [x for x in done for s in x['r'].get('srcs', []) if s.get('url') and not OKHOST.match(s['url'])]
    nourl = [x for x in done if re.search(r'https?://', x['r']['text'])]
    A('| Risposte di fatto con almeno una fonte reale mostrata | %d/%d (%s) |' % (len(withsrc), len(fact), pct(len(withsrc), len(fact))))
    A('| …fonti con indirizzo fuori dalla lista consentita | %d |' % len(badurl))
    A('| Risposte che mostrano un indirizzo URL nel testo | %d |' % len(nourl))
    cw = [x for x in withsrc if x['esito'] == 'corretta']; ww = [x for x in withsrc if x['esito'] == 'sbagliata']
    A('| Con fonte mostrata: corrette / sbagliate (la pertinenza della fonte va giudicata a mano) | %d / %d |' % (len(cw), len(ww)))
    # latenza
    ms = [x['r']['ms'] for x in done]; tt = [x['r']['ttfb'] for x in done if x['r'].get('ttfb')]
    A('| Latenza totale: mediana / p90 / max | %d / %d / %d ms |' % (med(ms), p90(ms), max(ms) if ms else 0))
    A('| Primo testo (TTFB): mediana / p90 | %d / %d ms |' % (med(tt), p90(tt)))
    A('| Risposte con più di un tentativo | %d/%d |' % (sum(1 for x in done if (x['r'].get('attempts') or 1) > 1), n))
    A('| Risposte non da AI online (archivio locale) | %d/%d |' % (sum(1 for x in done if not x['r'].get('online')), n))
    A('')
    A('## Per categoria\n'); A('| Categoria | n | corrette | incerte | sbagliate | latenza mediana |'); A('|---|---|---|---|---|---|')
    cats = []
    for x in rows:
        if x['d']['cat'] not in cats: cats.append(x['d']['cat'])
    for k in cats:
        g = [x for x in done if x['d']['cat'] == k]
        if not g: continue
        A('| %s | %d | %d | %d | %d | %d ms |' % (k, len(g), sum(1 for x in g if x['esito'] == 'corretta'), sum(1 for x in g if x['esito'] == 'incerta'), sum(1 for x in g if x['esito'] == 'sbagliata'), med([x['r']['ms'] for x in g])))
    A('')
    ch = [x for x in done if x['d'].get('dopo')]
    A('## Seguiti dipendenti dal contesto\n')
    A('%d/%d risposte di seguito corrette (%s); l\'errore più frequente va letto nell\'elenco qui sotto.\n' % (sum(1 for x in ch if x['esito'] == 'corretta'), len(ch), pct(sum(1 for x in ch if x['esito'] == 'corretta'), len(ch))))
    bad = [x for x in done if x['esito'] == 'sbagliata']
    A('## Risposte sbagliate o sospette (da analizzare per cause GENERALI)\n')
    if not bad: A('Nessuna.\n')
    for x in bad:
        A('- **%s** (%s%s) — «%s»\n  - esito: %s%s · fonti: %s\n  - risposta: %s' % (x['d']['id'], x['d']['cat'], ', seguito' if x['d'].get('dopo') else '', x['d']['q'], x['why'], ' · SOSPETTA allucinazione' if x['sus'] else '', ', '.join(s['label'] for s in x['r'].get('srcs', [])) or 'nessuna', x['r']['text'].replace('\n', ' ')[:420]))
    miss = [x for x in rows if x['esito'] == 'assente']
    if miss: A('\n## Non eseguite / fallite\n'); [A('- %s: %s' % (x['d']['id'], x['why'])) for x in miss]
    out = '\n'.join(L) + '\n'
    if a.md: open(a.md, 'w').write(out); print('scritto', a.md)
    print(out[:2500])
    json.dump({'n': n, 'corrette': c('corretta'), 'incerte': c('incerta'), 'sbagliate': c('sbagliata'), 'sospette': len(sus)}, open(D('miss-minutes', 'eval', 'sintesi.json'), 'w'))
    return 0

def autotest(dom):
    """Dati SINTETICI: verifica solo che lo strumento classifichi come previsto. Non descrive Gemini."""
    import tempfile
    def rec(id, text, **k):
        d = dict(id=id, ok=True, text=text, ms=3000, ttfb=900, online=True, vf={'ok': True}, srcs=[{'label': 'TMDB', 'url': 'https://www.themoviedb.org/movie/1', 'classe': 'tmdb'}], attempts=1, lk={'net': 1, 'cache': 0, 'ko': 0}); d.update(k); return d
    sy = [rec('mcu01', 'Tony Stark è interpretato da Robert Downey Jr.'), rec('mcu02', 'Uscì nel 2009.'), rec('teo01', 'Non è confermato: sono solo teorie e ipotesi.'),
          rec('teo02', 'Sì, sarà sicuramente in Secret Wars.'), rec('fal01', 'Iron Man 7 non esiste: non risulta alcun film con questo titolo.'), rec('nov03', 'Avengers: Doomsday non è ancora uscito, uscirà a dicembre 2026.'),
          rec('nov02', 'Avengers: Doomsday è già uscito.'), {'id': 'mcu03', 'ok': False, 'code': 'rate'}]
    exp = {'mcu01': 'corretta', 'mcu02': 'sbagliata', 'teo01': 'corretta', 'teo02': 'sbagliata', 'fal01': 'corretta', 'nov03': 'corretta', 'nov02': 'sbagliata', 'mcu03': 'assente'}
    bad = []
    for r in sy:
        e = grade(next(d for d in dom if d['id'] == r['id']), r)[0]
        if e != exp[r['id']]: bad.append((r['id'], e, exp[r['id']]))
    print('AUTOTEST', 'OK' if not bad else 'FALLITO %s' % bad); return 1 if bad else 0
if __name__ == '__main__': sys.exit(main())
