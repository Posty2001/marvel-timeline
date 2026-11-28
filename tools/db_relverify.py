#!/usr/bin/env python3
"""Seconda fonte INDIPENDENTE (verifica semantica v2) per le relazioni narrative (D12): articolo Wikipedia (en) del personaggio di partenza o di arrivo (CC BY-SA, solo lettura via API MediaWiki).
Una relazione e' CONFERMATA solo da un costrutto relazionale esplicito e direzionale tra i due estremi («father of X», «X's wife», «member of X», «enemy of X»...): la sola presenza dei due nomi nella stessa frase NON basta.
Si conserva solo l'esito (vero/falso) e l'URL: nessuna frase, nessun testo. Esecuzione in Actions (rete). Uso: python3 tools/db_relverify.py <out_dir>   (input: data/atlante/espansione/relverify_input.json)"""
import json, sys, re, time, pathlib, urllib.request, urllib.parse, unicodedata
R = pathlib.Path(__file__).resolve().parent.parent; E = R/'data/atlante/espansione'
UA = 'TVA-Archives-RelVerify/1.0 (progetto personale non commerciale, sola lettura; https://github.com/Posty2001/marvel-timeline)'
# Verifica SEMANTICA (D12): non basta la compresenza di due nomi nella stessa frase. Serve un costrutto relazionale ESPLICITO e DIREZIONALE che colleghi i due estremi:
#   «<ruolo> of/to <Altro>»  (soggetto = detentore del ruolo)   oppure   «<Altro>'s <ruolo>»  (soggetto = l'altro ruolo).
PARENTE = r"(?:step|adoptive |adopted |biological |foster )?(?:father|mother|parent|dad|mom)"
FIGLIO = r"(?:step|adoptive |adopted |biological |foster )?(?:son|daughter|child)"
RUOLI = {
    'famiglia_genitore': {'da': [PARENTE], 'a': [FIGLIO]},   # da = genitore, a = figlio/a
    'mentorato': {'da': [r"mentor|teacher|trainer|master|sensei"], 'a': [r"apprentice|student|prot[eé]g[eé]e?|pupil|disciple|sidekick|ward"]},
}
SIMM = {
    'famiglia_coniugi': r"wife|husband|spouse|widow|widower|ex-wife|ex-husband",
    'famiglia_fratelli': r"brother|sister|sibling|twin",
    'partner': r"girlfriend|boyfriend|lover|partner|love interest|fianc[eé]e?|romantic partner",
    'rivalita': r"enemy|enemies|nemesis|archenemy|arch-enemy|archnemesis|rival|adversary|foe|antagonist|arch-nemesis",
}
VERBI = {'famiglia_coniugi': r"married|marries|wed|weds", 'partner': r"dates|dating|romantically involved with|in a relationship with|falls in love with", 'rivalita': r"fights|battles|opposes|is opposed by|clashes with|hunts|is hunted by|duels"}
def norm(s): s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower(); return re.sub(r'[^a-z0-9 ]+', ' ', s)
def get(url, tries=4):
    for i in range(tries):
        try:
            time.sleep(1.2); return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60))
        except Exception as e:
            time.sleep(5 * (i + 1)); last = str(e)[:100]
    return {'errore': last}
def testo(titolo):
    r = get('https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&redirects=1&format=json&formatversion=2&maxlag=5&titles=' + urllib.parse.quote(titolo))
    try: return r['query']['pages'][0].get('extract') or ''
    except Exception: return None
def nomi_distintivi(nomi):
    out = set()
    for n in nomi:
        n = norm(n).strip()
        if len(n) >= 4: out.add(n)
        t = n.split()
        if len(t) > 1 and len(t[-1]) >= 5: out.add(t[-1])
    return out
def _alt(nomi): return '(?:' + '|'.join(re.escape(n) for n in sorted(nomi, key=len, reverse=True)) + ')'
def conferma(txt, tipo, altro, soggetto_e_da=True):
    """True se il testo (articolo del soggetto) contiene un costrutto relazionale esplicito verso uno degli `altro` nomi, coerente con la direzione.
    soggetto_e_da: il soggetto dell'articolo e' l'estremo `da` (per i tipi direzionali)."""
    N = _alt(altro); T = norm(txt)
    frasi = [norm(f) for f in re.split(r'(?<=[.!?])\s+', txt)]
    art = r"(?:the |his |her |its |their |a |an )?"
    for f in frasi:
        if not re.search(r'\b' + N + r'\b', f): continue
        if tipo in RUOLI:
            mio = RUOLI[tipo]['da' if soggetto_e_da else 'a'][0]; suo = RUOLI[tipo]['a' if soggetto_e_da else 'da'][0]
            # «(sono) il <mio ruolo> di <Altro>»  oppure  «<Altro> (è) il mio <ruolo dell'altro>»
            if re.search(r'\b' + art + r'(?:' + mio + r')\s+(?:of|to)\s+' + art + N + r'\b', f): return True
            if re.search(r'\b' + N + r"\s*(?:s|is|was)?\s*" + art + r'(?:' + suo + r')\b', f) and re.search(r"\b(?:his|her|their)\s+(?:" + suo + r')\b', f) and re.search(N + r"\s+s\s+(?:" + suo + ")|(?:" + suo + r")\s*,?\s*" + N, f) : return True
            if re.search(r'\b' + art + r'(?:' + suo + r')\s+' + N + r'\b', f) and re.search(r'\b(?:his|her|their)\s+(?:' + suo + r')\b', f): return True
        elif tipo in SIMM:
            r = SIMM[tipo]
            if re.search(r'\b' + art + r'(?:' + r + r')\s+(?:of|to|with)\s+' + art + N + r'\b', f): return True
            if re.search(r'\b' + N + r"\s+s\s+(?:" + r + r')\b', f): return True
            if re.search(r'\b(?:his|her|their)\s+(?:' + r + r')\s*,?\s*' + N + r'\b', f): return True
            if tipo in VERBI and re.search(r'\b(?:' + VERBI[tipo] + r')\s+' + art + N + r'\b', f): return True
        elif tipo == 'appartenenza':
            if re.search(r"\b(?:member|members|leader|founder|co-founder|founding member|recruit|agent|operative)\s+(?:of|in)\s+" + art + N + r'\b', f): return True
            if re.search(r'\b(?:joins|joined|joining|is a member of|was a member of|belongs to|leads|led|founded)\s+' + art + N + r'\b', f): return True
    return False
def main():
    inp = json.load(open(E/'relverify_input.json')); out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    cache = {}; res = {}; ck = out/'relverify2_checkpoint.json'
    if ck.exists():
        try: res = json.load(open(ck)).get('res', {})
        except Exception: pass
    for r in inp['relazioni']:
        if r['id'] in res: continue
        ok = False; url = None; tentate = 0
        for lato in ('da', 'a'):
            wp = r[lato + '_wp']
            if not wp: continue
            altro = nomi_distintivi(r['a_nomi' if lato == 'da' else 'da_nomi'])
            if wp not in cache: cache[wp] = testo(wp)
            tentate += 1
            if cache[wp] and conferma(cache[wp], r['tipo'], altro, lato == 'da'): ok = True; url = 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(wp.replace(' ', '_')); break
        res[r['id']] = {'ok': ok, 'url': url, 'articoli': tentate}
        if len(res) % 20 == 0: json.dump({'res': res}, open(ck, 'w'))
    json.dump({'res': res}, open(ck, 'w'))
    json.dump({'fonte': 'Wikipedia (CC BY-SA), solo esito', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'esiti': res}, open(out/'relverify2.json', 'w'), separators=(',', ':'))
    print(json.dumps({'relazioni': len(res), 'confermate': sum(1 for v in res.values() if v['ok'])}))
if __name__ == '__main__': main()
