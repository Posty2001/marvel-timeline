#!/usr/bin/env python3
"""Parser di wikitext (MediaWiki) per W1.b: estrae SOLO fatti strutturati (parametri di infobox, elenchi di nomi sotto sezioni note).
Non conserva prosa. Tollerante ai nomi dei parametri (varianti tra wiki). Test: tests/db_wiki_parse_test.py"""
import re
def clean(v, n=400):
    v = re.sub(r'<!--.*?-->', '', v or '', flags=re.S)
    v = re.sub(r'<ref[^>]*?/>|<ref[^>]*>.*?</ref>', '', v, flags=re.S)
    for _ in range(4): v = re.sub(r'\{\{[^{}]*\}\}', '', v)
    v = re.sub(r'\[\[(?:File|Image|Category):[^\]]*\]\]', '', v, flags=re.I)
    v = re.sub(r'\[\[([^\]|]*)\|([^\]]*)\]\]', r'\2', v); v = re.sub(r'\[\[([^\]]*)\]\]', r'\1', v)
    v = re.sub(r'<br\s*/?>', '; ', v, flags=re.I); v = re.sub(r"<[^>]+>", '', v); v = v.replace("'''", '').replace("''", '')
    v = re.sub(r'\s+', ' ', v).strip(' ;,*')
    return v[:n]
def _split_params(body):
    out, depth, cur, i = [], 0, '', 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ('[[', '{{'): depth += 1; cur += two; i += 2; continue
        if two in (']]', '}}'): depth -= 1; cur += two; i += 2; continue
        if body[i] == '|' and depth == 0: out.append(cur); cur = ''; i += 1; continue
        cur += body[i]; i += 1
    out.append(cur); return out
def infobox(wt):
    """Primo template il cui nome contiene 'infobox' o 'template' (es. 'Character Infobox', 'Marvel Database:Character Template')."""
    i = 0
    while True:
        i = wt.find('{{', i)
        if i < 0: return {}
        depth, j = 0, i
        while j < len(wt):
            if wt[j:j + 2] == '{{': depth += 1; j += 2; continue
            if wt[j:j + 2] == '}}':
                depth -= 1; j += 2
                if depth == 0: break
                continue
            j += 1
        blocco = wt[i + 2:j - 2]; parti = _split_params(blocco); nome = parti[0].strip().lower()
        if 'infobox' in nome or nome.endswith('template'):
            d = {}
            for p in parti[1:]:
                if '=' not in p: continue
                k, v = p.split('=', 1); k = re.sub(r'[^a-z0-9]', '', k.lower())
                v = clean(v)
                if k and v: d[k] = v
            return d
        i += 2
SEZ = {'poteri': ('powers and abilities', 'powers', 'abilities', 'powers & abilities', 'superhuman abilities', 'special abilities'),
       'abilita': ('skills', 'skills and abilities', 'abilities', 'talents'),
       'equipaggiamento': ('equipment', 'weapons', 'gear', 'weapons and equipment', 'equipment and weapons', 'transportation', 'items'),
       'debolezze': ('weaknesses', 'limitations', 'weakness', 'vulnerabilities'),
       'trasformazioni': ('forms', 'transformations', 'alternate forms', 'costumes', 'suits')}
def sezioni(wt):
    out = {}
    parti = re.split(r'^(={2,4})\s*([^=\n]+?)\s*\1\s*$', wt, flags=re.M)
    # parti: [pre, marker, titolo, testo, marker, titolo, testo...]
    for k in range(1, len(parti) - 2, 3):
        t = clean(parti[k + 1]).lower(); testo = parti[k + 2]
        for chiave, nomi in SEZ.items():
            if t in nomi:
                voci = []
                for riga in testo.splitlines():
                    m = re.match(r"^[*;#]+\s*(.+)$", riga.strip())
                    if not m: continue
                    r = m.group(1); b = re.match(r"'''([^']{2,60})'''", r) or re.match(r"\[\[([^\]|]{2,60})(?:\|([^\]]*))?\]\]", r)
                    nome = clean((b.group(2) if (b and b.lastindex and b.lastindex >= 2 and b.group(2)) else b.group(1)), 80) if b else clean(re.split(r'[:\-–—]', r, 1)[0], 80)
                    if 2 <= len(nome) <= 60 and nome.lower() not in [x.lower() for x in voci]: voci.append(nome)
                out.setdefault(chiave, [])
                for v in voci:
                    if v not in out[chiave]: out[chiave].append(v)
    return out
def categorie_wikitext(wt): return [clean(c, 80) for c in re.findall(r'\[\[Category:([^\]|]+)', wt, flags=re.I)]
