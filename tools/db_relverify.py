#!/usr/bin/env python3
"""Seconda fonte INDIPENDENTE per le relazioni narrative (D12): articolo Wikipedia (en) del personaggio di partenza o di arrivo (CC BY-SA, solo lettura via API MediaWiki).
Una relazione e' CONFERMATA solo se nel testo dell'articolo compare, NELLA STESSA FRASE, il nome (o un alias distintivo) dell'altro estremo e un termine tipico di QUEL tipo di relazione
(es. father/mother/son per genitorialita', wife/husband per coniugi, enemy/nemesis/rival per rivalita', mentor/student per mentorato, member/joined per appartenenza).
Si conserva solo l'esito (vero/falso) e l'URL: nessuna frase, nessun testo. Esecuzione in Actions (rete). Uso: python3 tools/db_relverify.py <out_dir>   (input: data/atlante/espansione/relverify_input.json)"""
import json, sys, re, time, pathlib, urllib.request, urllib.parse, unicodedata
R = pathlib.Path(__file__).resolve().parent.parent; E = R/'data/atlante/espansione'
UA = 'TVA-Archives-RelVerify/1.0 (progetto personale non commerciale, sola lettura; https://github.com/Posty2001/marvel-timeline)'
KW = {'famiglia_genitore': r'father|mother|son|daughter|parent|child|children|dad|mom|stepfather|stepmother|adopted|raised|grandfather|grandmother|biological',
      'famiglia_coniugi': r'wife|husband|married|spouse|marriage|wed|fianc|widow',
      'famiglia_fratelli': r'brother|sister|sibling|twin',
      'partner': r'girlfriend|boyfriend|lover|partner|romantic|romance|relationship|dating|affair|love interest|engaged|fianc',
      'rivalita': r'enem|nemesis|rival|arch-?enem|adversar|antagonist|foe|opponent|fights|battles|villain|opposes|archnemesis',
      'mentorato': r'mentor|trainer|taught|teacher|apprentice|student|prot[eé]g[eé]|trained|teaches|protege|sidekick',
      'appartenenza': r'member|joins|joined|team|part of|belongs|founder|founding|leader|recruit|affiliat|agent of'}
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
def conferma(txt, kw, altro):
    t = norm(txt).split('  '); nt = norm(txt); frasi = re.split(r'(?<=[.!?])\s+', txt)
    for fr in frasi:
        f = norm(fr)
        if re.search(kw, f) and any(re.search(r'\b' + re.escape(n) + r'\b', f) for n in altro): return True
    return False
def main():
    inp = json.load(open(E/'relverify_input.json')); out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    cache = {}; res = {}; ck = out/'relverify_checkpoint.json'
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
            if cache[wp] and conferma(cache[wp], KW[r['tipo']], altro): ok = True; url = 'https://en.wikipedia.org/wiki/' + urllib.parse.quote(wp.replace(' ', '_')); break
        res[r['id']] = {'ok': ok, 'url': url, 'articoli': tentate}
        if len(res) % 20 == 0: json.dump({'res': res}, open(ck, 'w'))
    json.dump({'res': res}, open(ck, 'w'))
    json.dump({'fonte': 'Wikipedia (CC BY-SA), solo esito', 'recuperato': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'esiti': res}, open(out/'relverify.json', 'w'), separators=(',', ':'))
    print(json.dumps({'relazioni': len(res), 'confermate': sum(1 for v in res.values() if v['ok'])}))
if __name__ == '__main__': main()
