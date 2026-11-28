#!/usr/bin/env python3
"""W1 - costruzione OFFLINE da raw Wikidata: classifica -> risolve (dedup) -> valida (D12) -> canon/staging/coda -> indice runtime.
Uso: python3 tools/db_w1_build.py <raw.json> [--scrivi]   (senza --scrivi: simulazione con conteggi)
Regole: ID storici mai toccati; match esatto (nome/alias) = ARRICCHIMENTO (mai riscrittura); match parziale/multiplo = coda di revisione e voce trattenuta;
persone distinte mai fuse; nessun testo narrativo (solo campi strutturati + descrizione breve Wikidata CC0); Livello C."""
import hashlib, json, sys, re, unicodedata, pathlib, collections, zlib, gzip, hashlib
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
 ('episodio', ('television pilot','television series episode','episode of','television season','season of')),
 ('battaglia', ('fictional battle','fictional war')),
 ('evento', ('fictional event','fictional conflict')),
 ('pianeta', ('fictional planet','fictional star','fictional moon','fictional celestial')),
 ('universo', ('fictional universe','fictional dimension','fictional realm','fictional plane of existence','fictional world')),
 ('organizzazione', ('fictional command','fictional division','fictional department','fictional council','fictional tribunal','fictional court','fictional television network','fictional television station','fictional newspaper','fictional news ','fictional media')),
 ('luogo', ('fictional facility','fictional apartment','fictional residence','fictional restaurant','fictional house','fictional drinking establishment','fictional store','fictional hospital','fictional shop','fictional military base','fictional laboratory','fictional high or secondary school','fictional hotel','fictional diner','fictional university','fictional caf','fictional club','fictional police station','fictional bar','fictional bank','fictional office','fictional museum','fictional church','fictional street','fictional park','fictional airport','fictional bridge','fictional neighborhood','fictional neighbourhood','fictional district','fictional headquarters','fictional laboratory','fictional gym','fictional theater','fictional theatre','fictional casino','fictional warehouse','fictional factory','fictional hideout','fictional lair','fictional base','fictional embassy','fictional castle','fictional temple','fictional palace','fictional tower','fictional station','fictional forest','fictional motel','fictional college','fictional cemetery','fictional jungle','fictional mountain','fictional lake','fictional river','fictional ocean','fictional desert','fictional street','fictional alley','fictional bunker','fictional vault','fictional lab','fictional clinic','fictional courthouse','fictional church','fictional mansion','fictional farm','fictional ranch','fictional cabin','fictional safe house','fictional shelter','fictional cafeteria','fictional pub','fictional nightclub','fictional bakery','fictional gallery','fictional library','fictional pharmacy','fictional pawn shop','fictional gas station','fictional location','fictional city','fictional country','fictional building','fictional locale','fictional state','fictional nation','fictional island','fictional prison','fictional school','fictional place','fictional town','fictional village','fictional kingdom','fictional continent','fictional region','fictional organization headquarters')),
 ('civilta', ('fictional civilization','fictional nation state','fictional empire')),
 ('specie', ('fictional species','fictional race','fictional alien species','fictional ethnic group','fictional mutant species','fictional population')),
 ('organizzazione', ('fictional organization','fictional organisation','fictional team','superhero team','fictional intelligence agency','fictional government','fictional criminal organization','fictional company','fictional military unit','fictional group','fictional corporation','fictional agency','fictional institution','fictional secret society','fictional gang','fictional cult','fictional religion','fictional political party','fictional army')),
 ('artefatto', ('fictional motorcycle','fictional document','fictional painting','fictional artwork','fictional machine','fictional program','fictional virus','fictional serum','fictional potion','fictional jewelry','fictional costume','fictional armor','fictional armour','fictional automobile','fictional car','fictional suit','fictional weapon','fictional object','fictional artifact','fictional artefact','fictional material','fictional element','fictional technology','fictional vehicle','fictional item','fictional gem','fictional device','fictional spacecraft','fictional aircraft','fictional ship','fictional substance','fictional metal','fictional book','fictional magic','fictional language','fictional currency','fictional drug','fictional food')),
 ('entita-cosmica', ('fictional deity','fictional god','fictional cosmic entity','fictional entity','fictional celestial being','fictional demon','fictional spirit','fictional monster','fictional being','fictional creature')),
 ('identita', ('comics character','television character','film character','fictional human','fictional character','fictional alien','fictional robot','superhero','supervillain','fictional mutant','fictional animal','fictional cyborg','fictional android','fictional humanoid','fictional person','fictional hero','fictional villain','fictional antihero','fictional artificial intelligence','fictional extraterrestrial','fictional wizard','fictional sorcerer','fictional soldier','fictional spy','fictional scientist','fictional journalist','fictional lawyer','fictional physician','fictional criminal','fictional dog','fictional cat','fictional monkey','fictional bird','fictional dragon','fictional vampire','fictional zombie','fictional superhuman','fictional giant','fictional dwarf','fictional elf','fictional genius','fictional pirate','fictional president','fictional politician','fictional king','fictional queen','fictional prince','fictional princess','fictional warrior','fictional knight','fictional witch','fictional thief','fictional assassin','fictional mercenary','fictional detective','fictional doctor','fictional teacher','fictional student','fictional child','fictional woman','fictional man','fictional girl','fictional boy','fictional fictional character','fictional demigod','fictional ghost','fictional mutant character','fictional inventor','fictional engineer','fictional pilot','fictional astronaut','fictional agent','fictional officer','fictional commander','fictional captain','fictional general','fictional emperor','fictional priest','fictional monk','fictional sorceress')),
 ('opera', ('film','television series','animated series','animated film','video game','web series','short film','television film','miniseries','anthology','television program','animated television series','film series','media franchise','comic book series','novel','book series','tv series','streaming','documentary','television special','one-shot')),
]
REGOLE_FUM = [   # solo W5/W6 (fumetti): saghe, eventi e testate sono OPERE/EVENTI documentati, non «raggruppamenti editoriali»
 ('evento', ('comic book crossover', 'comics crossover', 'comic book storyline', 'comics storyline', 'story arc', 'crossover event', 'comic book event', 'comics event')),
 ('opera', ('comic book', 'comic strip', 'graphic novel', 'comic series', 'limited series', 'miniseries', 'manga', 'webcomic', 'comics series', 'comics anthology', 'one-shot', 'comic magazine')),
]
FUMETTI = False
def classifica(p31_labels, gruppi):
    L = [x.lower() for x in p31_labels if x]
    if FUMETTI:
        for tipo, keys in REGOLE_FUM:
            for l in L:
                if any(l == k or l.startswith(k) or k in l for k in keys): return tipo
    for tipo, keys in REGOLE:
        for l in L:
            if any(l == k or l.startswith(k) or k in l for k in keys): return tipo
    if 'human' in L:
        if any(g == 'interpreti_MCU' or g.endswith(':interpreti') or g.startswith('interpreti:') for g in gruppi): return 'attore'
        if any(g == 'creatori_MCU' or g.endswith(':creatori') or g.startswith('creatori:') for g in gruppi): return 'creatore'
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

GLOSS = {'eye': 'occhio', 'of': 'di', 'battle': 'battaglia', 'the': '', 'hall': 'sala', 'gauntlet': 'guanto', 'shield': 'scudo', 'hammer': 'martello', 'tower': 'torre', 'island': 'isola', 'sword': 'spada', 'book': 'libro', 'ring': 'anello', 'rings': 'anelli', 'ten': 'dieci', 'blip': 'blip', 'fall': 'caduta'}
def tr(k): return ' '.join(x for x in (GLOSS.get(w, w) for w in norm(k).split()) if x)
def contiguo(piccolo, grande):
    a, b = piccolo.split(), grande.split()
    return bool(a) and any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))
def risolvi(tipo, nome, chiavi, full, part, perf, wd_uni, info, idx_by):
    """Ritorna ('arricchisci', id) | ('nuovo', None) | ('ambiguo', motivo). Regole deterministiche, mai fusioni per solo nome."""
    cand = sorted(full | part)
    if tipo != 'identita':
        for i in cand:
            v = idx_by[i]; base = re.sub(r'\s*\(.*?\)', '', v['n'])
            nomi = {norm(v['n']), norm(base)} | {norm(x) for x in re.findall(r'\(([^)]*)\)', v['n'])} | {norm(x) for x in re.split(r'[/,]', base)}
            if {norm(nome), tr(nome)} & nomi or tr(nome) in {tr(x) for x in nomi}: return 'arricchisci', i
        if tipo in ('attore', 'creatore', 'opera'): return 'ambiguo', 'omonimia con voci storiche: ' + ','.join(cand)
        return ('nuovo', None) if all(len(set(norm(nome).split()) & set(norm(idx_by[i]['n']).split())) < 2 or True for i in cand) else ('ambiguo', 'token')
    # persone/personaggi
    perf_n = {norm(x) for x in perf}
    ov = [i for i in cand if perf_n & {norm(x) for x in info.get(i, {}).get('interpreti', [])}]
    if len(ov) == 1: return 'arricchisci', ov[0]
    if len(ov) > 1: return 'ambiguo', 'piu\' identita con lo stesso interprete: ' + ','.join(ov)
    if perf_n and cand and all(info.get(i, {}).get('interpreti') for i in cand): return 'nuovo', None   # interpreti tutti diversi: persone/continuita' distinte
    if wd_uni:
        mcu_c = [i for i in cand if info.get(i, {}).get('universo') == wd_uni]
        nn = norm(nome); mc = [i for i in mcu_c if any(contiguo(nn, norm(x)) for x in [idx_by[i]['n']] + info.get(i, {}).get('alias', []) ) and not re.search(r'^\s*' + re.escape(nn) + r'\s*$', '')]
        if len(mc) == 1: return 'arricchisci', mc[0]
        if len(mc) > 1: return 'ambiguo', 'piu\' candidati MCU: ' + ','.join(mc)
    return 'ambiguo', 'continuita\'/identita\' non determinabili da fonti strutturate: ' + ','.join(cand)

CAT = {'identita': ('characters', 'individuals', 'people'), 'luogo': ('locations', 'places', 'buildings', 'planets', 'cities'), 'pianeta': ('planets', 'locations', 'realms'),
       'artefatto': ('objects', 'weapons', 'artifacts', 'artefacts', 'technology', 'vehicles', 'armor', 'items', 'devices', 'equipment', 'costumes'),
       'organizzazione': ('organizations', 'organisations', 'teams', 'groups', 'companies', 'corporations', 'agencies', 'media'), 'specie': ('species', 'races'),
       'battaglia': ('events', 'battles', 'conflicts', 'wars'), 'evento': ('events', 'battles', 'conflicts'), 'universo': ('realities', 'dimensions', 'universes', 'realms', 'locations'),
       'entita-cosmica': ('characters', 'deities', 'cosmic', 'beings', 'entities'), 'civilta': ('civilizations', 'nations', 'species', 'organizations')}
CAMPI = {'specie': ('species', 'race', 'races'), 'stato': ('status',), 'genere': ('gender', 'sex'), 'affiliazioni': ('affiliation', 'affiliations', 'team', 'teams', 'organization', 'organizations'),
         'prima_apparizione': ('firstappearance', 'debut', 'firstappearances', 'first'), 'alias_fonte': ('aliases', 'alias', 'currentalias', 'nicknames', 'nickname', 'otheraliases'),
         'interpreti_fonte': ('portrayedby', 'actor', 'actors', 'portrayed', 'playedby'), 'parenti': ('relatives', 'family', 'relations'),
         'poteri': ('powers',), 'abilita': ('abilities',), 'equipaggiamento': ('weapons', 'equipment', 'transportation'), 'debolezze': ('weaknesses',), 'origine': ('origin',), 'creatori_fonte': ('creators',),
         'nome_reale': ('realname',), 'cittadinanza': ('citizenship',), 'occupazione': ('occupation',), 'nascita': ('dob', 'placeofbirth'), 'morte': ('dod', 'death', 'causeofdeath', 'killedby'),
         'ubicazione': ('location', 'continent', 'homeplanet', 'place', 'baseofoperations', 'headquarters', 'locations'), 'utenti': ('users', 'owners', 'owner', 'notableusers', 'notableowners', 'currentowner', 'pilot'),
         'creatore_oggetto': ('creator', 'made', 'builder'), 'membri': ('members', 'leader', 'leaders', 'founder', 'currentmembers', 'formermembers'), 'esito': ('result', 'date'), 'popolazione': ('population',)}
APP_CHIAVI = {'movie': 'n', 'tvseries': 'n', 'webseries': 'n', 'docuseries': 'n', 'tvmovie': 'n', 'oneshot': 'n', 'comic': 'f', 'game': 'v', 'book': 'a', 'themepark': 'a'}
APP_CAMPI = {'n': 'apparizioni_narrativa', 'x': 'apparizioni_alternativi', 'f': 'apparizioni_fumetti', 'v': 'apparizioni_videogiochi', 'a': 'apparizioni_adattamenti'}
RE_ADATT = re.compile(r'\b(lego|parod|adaptation|trailer maker|prequel comic|animated adaptation|junior|puzzle|novelization|audio)\b', re.I)
RE_ALT = re.compile(r"what if|marvel zombies|\(alternate|alternate (?:universe|timeline|reality|version)|variant|\(earth-|multiverse of madness variant", re.I)
def classe_app(titolo, chiave):
    c = APP_CHIAVI.get(chiave, 'n')
    if c == 'n':
        if RE_ADATT.search(titolo): return 'a'
        if RE_ALT.search(titolo): return 'x'   # universo alternativo: NON si attribuisce alla stessa incarnazione
    return c

LISTE = ('poteri', 'abilita', 'equipaggiamento', 'debolezze')
SCALARI = ('stato', 'genere', 'prima_apparizione', 'origine', 'nome_reale', 'nascita', 'morte', 'esito', 'popolazione')
def carica_w1b(d):
    if not d: return {}, {}
    d = pathlib.Path(d); m = json.load(open(d/'w1b_mcuwiki.json'))['pagine'] if (d/'w1b_mcuwiki.json').exists() else {}
    db = json.load(open(d/'w1b_marveldb.json')) if (d/'w1b_marveldb.json').exists() else {'pagine': {}, 'ricerca': {}}
    mdb = {n: db['pagine'].get(t) for n, t in db.get('ricerca', {}).items()}
    return m, mdb
def split_par(v):
    """Elenco con possibili parentesi: spezza su virgole/punto e virgola/asterischi FUORI dalle parentesi (conserva «Nome (relazione)»)."""
    out, cur, d = [], '', 0
    for ch in v:
        if ch == '(': d += 1
        elif ch == ')': d = max(0, d - 1)
        if ch in ',;*' and d == 0: out.append(cur); cur = ''
        else: cur += ch
    out.append(cur)
    return [x.strip(' :.-') for x in out if 3 <= len(x.strip(' :.-')) <= 90 and re.search(r'[A-Za-z]', x)]
def _lista(v, cap=12):
    v = re.sub(r'\(\s*(?:formerly|former|mentioned|footage|flashbacks?|deceased)\s*\)', '', v, flags=re.I)   # annotazioni del wiki, non nomi
    v = re.sub(r'\b(?:formerly|currently|previously)\s*:', ';', v, flags=re.I)
    out = []
    for x in re.split(r'[;,*]', v):
        x = x.strip(' :.-')
        if x.count('(') != x.count(')'): x = x.replace('(', '').replace(')', '').strip()
        if len(x) >= 3 and re.search(r'[A-Za-z]', x) and x not in out: out.append(x)
    return out[:cap]
def fatti_da(pag, tipo):
    f = {}
    ib = pag.get('infobox', {})
    for campo, chiavi in CAMPI.items():
        vals = [ib[k] for k in chiavi if k in ib]
        if not vals: continue
        if campo in LISTE:
            voci = []
            for v in vals:
                for x in _lista(v):
                    if len(x) <= 80 and x not in voci: voci.append(x)   # solo nomi brevi (mai frasi/prosa)
            if voci: f[campo] = voci[:25]
        elif campo in SCALARI: f[campo] = '; '.join(dict.fromkeys(v[:120] for v in vals))[:160]
        else:
            voci = []
            for v in vals:
                for x in _lista(v):
                    if x not in voci: voci.append(x)
            f[campo] = voci[:12]
    rf = {}
    for campo, chiavi in (('parenti', ('relatives', 'family')), ('alleati', ('allies',)), ('nemici', ('enemies',))):
        voci = []
        for k in chiavi:
            for x in split_par(ib.get(k, '')):
                if x not in voci: voci.append(x)
        if voci: rf[campo] = voci[:30]
    if rf: f['relazioni_fonte'] = rf
    app = {}
    for k, c in APP_CHIAVI.items():
        for v in ([ib[k]] if k in ib else []):
            for x in _lista(v, 40):
                cl = classe_app(x, k)
                if x not in app.setdefault(cl, []): app[cl].append(x)
    for cl, voci in app.items(): f[APP_CAMPI[cl]] = voci[:20]
    for c in LISTE:
        v = pag.get('sezioni', {}).get(c)
        if v:
            cur = f.setdefault(c, [])
            for x in v[:25]:
                x = x.strip(' :')
                if x and x not in cur: cur.append(x)
            f[c] = cur[:25]
    return f
def corrobora(nome, alias, tipo, perf, mcu_p, mdb_p):
    """Seconda fonte indipendente (D12): pagina MCU Wiki coerente per titolo, categoria e (se disponibili) interpreti. Marvel Database = conferma/fatti aggiuntivi."""
    chiavi = {norm(nome)} | {norm(a) for a in alias}
    out = {'ok': False, 'motivo': None, 'fonti': [], 'fatti': {}, 'fatti_fonti': {}}
    def valida(p):
        if not p: return 'nessuna pagina'
        if p.get('disambigua'): return 'pagina di disambiguazione'
        if norm(re.sub(r'\s*\(.*?\)', '', p['titolo'])) not in chiavi and norm(p['titolo']) not in chiavi: return 'titolo non corrispondente'
        cats = ' '.join(c.lower() for c in p.get('categorie', []))
        if not any(k in cats for k in CAT.get(tipo, ())): return 'categorie incoerenti con il tipo ' + tipo
        if tipo == 'identita':
            pp = {norm(x) for x in re.split(r'[;,]', ' ; '.join(v for k, v in p.get('infobox', {}).items() if k in CAMPI['interpreti_fonte']))}; pp.discard('')
            if pp and perf and not (pp & {norm(x) for x in perf}): return 'interpreti non coincidenti'
        return None
    for cod, p, lic in (('mcuwiki', mcu_p, 'MCU Wiki'), ('marveldb', mdb_p, 'Marvel Database')):
        m = valida(p)
        if m: out['motivo'] = out['motivo'] or (lic + ': ' + m); continue
        out['fonti'].append({'fonte': lic + ' (Fandom) - fatti, nessun testo copiato; contributori della pagina', 'url': p['url'], 'licenza': 'CC BY-SA 3.0', 'cod': cod})
        for c, v in fatti_da(p, tipo).items():
            cur = out['fatti'].setdefault(c, [] if isinstance(v, list) else v)
            if isinstance(v, list):
                for x in v:
                    if x not in cur: cur.append(x)
            out['fatti_fonti'].setdefault(c, []).append(cod)
    out['ok'] = any(f['cod'] == 'mcuwiki' for f in out['fonti'])   # la seconda fonte di identita' e' la MCU Wiki; Marvel DB da sola non basta per l'MCU
    if out['ok']: out['motivo'] = None
    return out

def qnum(q): return int(q[1:])
def main():
    if '--solo-runtime' in sys.argv: return costruisci_runtime()   # rigenera solo l'indice runtime dai canon esistenti
    raw = json.load(open(sys.argv[1])); scrivi = '--scrivi' in sys.argv
    MCUP, MDBP = carica_w1b(sys.argv[sys.argv.index('--w1b') + 1] if '--w1b' in sys.argv else None)
    ent, et = raw['entita'], raw['etichette']
    mcu = {q for q, l in et.items() if l == 'Marvel Cinematic Universe'}
    ONDA = sys.argv[sys.argv.index('--onda') + 1] if '--onda' in sys.argv else 'w1'
    global FUMETTI; FUMETTI = ONDA in ('w5', 'w6')
    GRP_UNI = {'x-men-fox': 'uni-earth-10005-fox-verse', 'wolverine-fox': 'uni-earth-10005-fox-verse', 'deadpool-fox': 'uni-earth-10005-fox-verse', 'new-mutants-fox': 'uni-earth-10005-fox-verse',
               'spider-man-raimi': 'uni-earth-96283-raimi-verse', 'spider-man-garfield': 'uni-earth-120703-garfield-verse', 'venom-ssu': 'uni-sony-s-spider-man-universe-ssu', 'morbius-ssu': 'uni-sony-s-spider-man-universe-ssu',
               'madame-web-ssu': 'uni-sony-s-spider-man-universe-ssu', 'kraven-ssu': 'uni-sony-s-spider-man-universe-ssu', 'blade': 'uni-blade-verse', 'daredevil-elektra': 'uni-daredevil-elektra-verse', 'ghost-rider': 'uni-ghost-rider-verse',
               'hulk-2003': 'uni-hulk-2003-verse', 'fantastic-four-1994': 'uni-fantastic-four-1994', 'fantastic-four-fox': 'uni-earth-121698', 'fantastic-four-trank': 'uni-earth-trn123',
               # W3 (serie TV e film live-action non MCU)
               'netflix-mcu': 'uni-earth-199999-mcu', 'agents-of-shield': 'uni-earth-199999-mcu', 'marvel-tv-mcu': 'uni-earth-199999-mcu', 'legion': 'uni-legion-verse', 'the-gifted': 'uni-the-gifted-verse',
               # W4 (animazione)
               'what-if': 'uni-rami-di-what-if', 'x-men-97': 'uni-x-men-97-verse', 'spider-verse-sony': 'uni-spider-verse-sony-animato', 'yfnsm': 'uni-your-friendly-neighborhood-spider-man-verse',
               'marvel-zombies': 'uni-marvel-zombies-verse', 'marvel-animation-universe': 'uni-marvel-animation-universe-2006-2017'}
    def uni_di(r):
        if ONDA in ('w5', 'w6'):   # fumetti: solo la continuita' principale e' assegnata in modo certo (P1080 = Marvel Universe / Earth-616); altri universi non si assegnano automaticamente
            ls = {et.get(x) for x in r['c'].get('P1080', [])}
            return 'uni-earth-616' if ls & {'Marvel Universe', 'Earth-616', 'Marvel Comics Universe'} else None
        if ONDA == 'w1': return 'uni-earth-199999-mcu' if (mcu & set(r['c'].get('P1080', []))) else None
        us = {GRP_UNI[g] for g in r['g'] if g in GRP_UNI}
        return next(iter(us)) if len(us) == 1 else None   # piu' continuita' (es. interprete in piu' franchise) = nessuna assegnazione automatica
    NOMEFILE = {'w1': 'w1_mcu', 'w2': 'w2_pre_mcu', 'w3': 'w3_tv_live_action', 'w4': 'w4_animazione', 'w5': 'w5_fumetti_entita', 'w6': 'w6_fumetti_opere'}[ONDA]; ORIG = {'w1': 'W1', 'w2': 'W2', 'w3': 'W3', 'w4': 'W4', 'w5': 'W5', 'w6': 'W6'}[ONDA]
    idx, pieni, parz = carica_esistente(); tipo_esist = {v['i']: v['t'] for v in idx}
    reg = json.load(open(E/'ids_registro.json'))['ids']
    q2id = {v['ids_esterni']['wikidata']: k for k, v in reg.items() if v.get('ids_esterni', {}).get('wikidata') and v.get('stato') != 'lapide'}
    usati = set(reg)
    INFO = {x['id']: x for x in json.load(open(R/'data/atlante/identita.json'))['identita']}; IDX_BY = {v['i']: v for v in idx}; gia_arr = {}
    canon, stag, coda, arr = [], [], collections.defaultdict(list), []
    cont = collections.Counter()
    for q in sorted(ent, key=qnum):
        r = ent[q]; nome = r['l'].get('en')
        p31 = [et.get(x) for x in r['c'].get('P31', [])]
        tipo = classifica(p31, r['g'])
        mot = None
        if not nome: mot = 'senza etichetta inglese'
        elif tipo is None and any(k in ' '.join(x.lower() for x in p31 if x) for k in ('occurrence', 'catchphrase', 'phase', 'saga', 'storyline', 'fictional period')): mot = 'fuori ambito: raggruppamento editoriale o locuzione (coperto da sezioni/saghe o non e\' un\'entita\'): ' + '|'.join(x for x in p31 if x)[:60]
        elif tipo is None: mot = 'classe non riconosciuta: ' + '|'.join(x for x in p31 if x)[:80]; coda['non_classificati'].append({'q': q, 'nome': nome, 'p31': p31})
        elif tipo == 'episodio': mot = 'episodio/stagione: fuori ambito W1'
        if mot:
            cont['staging:' + (tipo or 'n/d')] += 1; stag.append({'q': q, 'nome': nome, 'tipo': tipo, 'motivo': mot}); continue
        alias = sorted({a for l in ('en', 'it') for a in r['a'].get(l, []) if a} | ({r['l']['it']} if r['l'].get('it') and r['l']['it'] != nome else set()))
        chiavi = {norm(nome)} | {norm(a) for a in alias} | ({norm(re.sub(r'\s*\(.*?\)', '', r['sl']['itwiki']))} if r['sl'].get('itwiki') else set())
        # risoluzione contro l'archivio storico: solo tipi compatibili contano
        compat = {'identita': 'p', 'universo': 'U', 'organizzazione': 'o', 'artefatto': 'a', 'luogo': 'l', 'pianeta': 'P', 'evento': 'e', 'opera': None, 'attore': 't', 'creatore': None, 'battaglia': 'e', 'specie': None, 'civilta': None, 'entita-cosmica': 'p'}
        full = set().union(*[pieni.get(k, set()) for k in chiavi if k]) if chiavi else set()
        full = {i for i in full if compat.get(tipo) and (tipo_esist[i] == compat.get(tipo) or (tipo == 'identita' and tipo_esist[i] in ('h', 'm')))}
        part = set().union(*[parz.get(k, set()) for k in chiavi if k])
        part = {i for i in part if compat.get(tipo) and tipo_esist[i] == compat.get(tipo)} - full
        if tipo not in ('identita', 'attore', 'creatore', 'opera', 'specie', 'civilta', 'entita-cosmica') and not full:
            # categorie non-persona: l'archivio storico e' in italiano e Wikidata spesso non ha l'etichetta italiana -> confronto cross-lingua per token distintivi
            STOP = {'battle', 'battaglia', 'stone', 'stones', 'gemma', 'armor', 'armour', 'infinity', 'avengers', 'universe', 'realm', 'earth'}
            tk = {w for k in chiavi for w in k.split() if len(w) >= 5} - STOP
            for v in idx:
                if compat.get(tipo) == v['t'] and tk & ({w for w in norm(v['n']).split() if len(w) >= 5} - STOP): part.add(v['i'])
        if len(full) == 1 and not part:
            arr.append({'id': next(iter(full)), 'wikidata': q, 'alias_nuovi': [a for a in alias if norm(a) not in pieni or next(iter(full)) not in pieni[norm(a)]][:20],
                        'interpreti': sorted({et.get(x) for x in r['c'].get('P175', []) if et.get(x)}), '_sc': bool(uni_di(r)) and INFO.get(next(iter(full)), {}).get('universo') == uni_di(r), 'fonte': 'Wikidata (CC0)'}); cont['arricchimento'] += 1; continue
        if full or part:
            perf = [et.get(x) for x in r['c'].get('P175', []) if et.get(x)]
            esito, arg = risolvi(tipo, nome, chiavi, full, part, perf, uni_di(r), INFO, IDX_BY)
            if esito == 'arricchisci':
                stessa_cont = bool(uni_di(r)) and INFO.get(arg, {}).get('universo') == uni_di(r)   # stessa continuita' dell'identita' storica: elementi Wikidata multipli = stesso personaggio (arricchimento additivo)
                if arg in gia_arr and gia_arr[arg][0] != norm(nome) and not stessa_cont:
                    coda['possibili_duplicati'].append({'q': q, 'nome': nome, 'tipo': tipo, 'esistenti_esatti': sorted(full), 'esistenti_parziali': sorted(part), 'motivo': 'stessa voce storica gia\' arricchita da un altro elemento Wikidata con nome diverso: ' + arg})
                    stag.append({'q': q, 'nome': nome, 'tipo': tipo, 'motivo': 'ambiguo: due elementi Wikidata distinti per la stessa voce storica'}); cont['coda_ambigui'] += 1; continue
                gia_arr.setdefault(arg, (norm(nome), q))
                arr.append({'id': arg, 'wikidata': q, 'alias_nuovi': [a for a in alias if arg not in pieni.get(norm(a), set())][:20], 'interpreti': sorted(set(perf)), '_sc': stessa_cont, 'fonte': 'Wikidata (CC0)', 'regola': 'risoluzione assistita'}); cont['arricchimento_regole'] += 1; continue
            if esito == 'ambiguo':
                coda['possibili_duplicati'].append({'q': q, 'nome': nome, 'tipo': tipo, 'esistenti_esatti': sorted(full), 'esistenti_parziali': sorted(part), 'motivo': arg})
                stag.append({'q': q, 'nome': nome, 'tipo': tipo, 'motivo': 'ambiguo: ' + arg[:80]}); cont['coda_ambigui'] += 1; continue
            cont['nuovo_dopo_confronto'] += 1   # distinto dalle voci storiche: prosegue come nuova voce
        # D12: dichiarazione Wikidata + articolo Wikipedia indipendente (en) => verificata a livello di identita'/esistenza; altrimenti staging
        perf_wd = [et.get(x) for x in r['c'].get('P175', []) if et.get(x)]
        cor = corrobora(nome, alias, tipo, perf_wd, MCUP.get(nome), MDBP.get(nome)) if (MCUP or MDBP) else {'ok': False, 'motivo': None, 'fonti': [], 'fatti': {}, 'fatti_fonti': {}}
        wiki = bool({'enwiki', 'itwiki'} & set(r['sl']))
        if not wiki and not cor['ok']:
            stag.append({'q': q, 'nome': nome, 'tipo': tipo, 'motivo': 'una sola fonte (nessun articolo Wikipedia' + ('; seconda fonte scartata: ' + cor['motivo'] if cor['motivo'] else '') + '): resta in staging (D12)'}); cont['staging:una_fonte'] += 1; continue
        if q in q2id: rid = q2id[q]
        else:
            base = PREF[tipo] + '-' + (slug(nome) or q.lower()); rid = base
            if ONDA == 'w5' and tipo == 'universo' and nome in ('Marvel Universe', 'Earth-616', 'Marvel Comics Universe') and 'uni-earth-616' not in usati: rid = base = 'uni-earth-616'
            if rid in usati: rid = base + '-' + q.lower()
        usati.add(rid)
        uni = uni_di(r)
        rec = {'id': rid, 'tipo': tipo, 'nome': nome, 'livello': 'C', 'stato_verifica': 'verificata', 'origine': ORIG if wiki else ORIG + 'b',
               'ids_esterni': {'wikidata': q}, 'gruppi': r['g'],
               'fonti': [{'fonte': 'Wikidata', 'url': 'https://www.wikidata.org/wiki/' + q, 'licenza': 'CC0'}]}
        if wiki: rec['fonti'].append({'fonte': 'Wikipedia - solo riferimento', 'url': ('https://en.wikipedia.org/wiki/' + r['sl']['enwiki'].replace(' ', '_')) if 'enwiki' in r['sl'] else ('https://it.wikipedia.org/wiki/' + r['sl']['itwiki'].replace(' ', '_')), 'licenza': 'CC BY-SA 4.0 (nessun testo copiato)'})
        for f in cor['fonti']: rec['fonti'].append({k: v for k, v in f.items() if k != 'cod'})
        if cor['fatti']:
            rec['fatti'] = cor['fatti']; rec['fatti_fonti'] = cor['fatti_fonti']
            if sum(1 for c in ('poteri', 'abilita', 'equipaggiamento', 'debolezze', 'affiliazioni', 'specie', 'stato', 'trasformazioni') if rec['fatti'].get(c)) >= 3: rec['livello'] = 'B'
        if cor['ok']: rec['ids_esterni']['mcuwiki'] = MCUP[nome]['titolo']
        if r['l'].get('it') and r['l']['it'] != nome: rec['nome_it'] = r['l']['it']
        if alias: rec['alias'] = alias
        if uni: rec['universo'] = uni
        d = {k: v for k, v in r['d'].items() if v}
        if d: rec['descrizione'] = d
        ip = sorted({et.get(x) for x in r['c'].get('P175', []) if et.get(x)})
        if ip: rec['interpreti'] = ip
        rec['wikipedia'] = {k[:2]: v for k, v in r['sl'].items()}
        canon.append(rec); cont['canon:' + tipo] += 1
    per_id = collections.defaultdict(set)
    nome_q = {a['wikidata']: norm(ent[a['wikidata']]['l'].get('en')) for a in arr}
    for a in arr: per_id[a['id']].add(nome_q[a['wikidata']])
    conf = {i for i, n in per_id.items() if len(n) > 1 and not all(a.get('_sc') for a in arr if a['id'] == i)}
    for a in [a for a in arr if a['id'] in conf]:
        r = ent[a['wikidata']]; coda['possibili_duplicati'].append({'q': a['wikidata'], 'nome': r['l'].get('en'), 'tipo': 'identita', 'esistenti_esatti': [a['id']], 'esistenti_parziali': [], 'motivo': 'nomi Wikidata diversi puntano alla stessa voce storica'})
        stag.append({'q': a['wikidata'], 'nome': r['l'].get('en'), 'tipo': 'identita', 'motivo': 'ambiguo: nomi diversi per la stessa voce storica'}); cont['coda_ambigui'] += 1
    arr = [a for a in arr if a['id'] not in conf]
    ris = {'canon': len(canon), 'staging': len(stag), 'arricchimenti': len(arr), 'coda': {k: len(v) for k, v in coda.items()}, 'per_tipo': {k[6:]: v for k, v in cont.items() if k.startswith('canon:')},
           'staging_per_motivo': dict(collections.Counter(x['motivo'].split(':')[0] for x in stag)), 'mcu_qid': sorted(mcu), 'input_entita': len(ent)}
    print(json.dumps(ris, ensure_ascii=False, indent=1))
    if not scrivi: return
    (E/'canon').mkdir(exist_ok=True); (E/'staging').mkdir(exist_ok=True); (E/'review').mkdir(exist_ok=True)
    w = lambda p, rows: (E/p).write_text('\n'.join(json.dumps(x, ensure_ascii=False, sort_keys=True) for x in rows) + ('\n' if rows else ''))
    w(f'canon/{NOMEFILE}.jsonl', canon); w(f'canon/{ONDA}_arricchimenti.jsonl', [{k: v for k, v in a.items() if k != '_sc'} for a in arr]); w(f'staging/{ONDA}_staging.jsonl', stag)
    json.dump(dict(coda), open(E/f'review/{ONDA}_coda.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    json.dump(ris, open(E/f'{ONDA}_conteggi.json', 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    rp = E/'ids_registro.json'; rg = json.load(open(rp)); vivi = {c['id'] for c in canon}; q_arr = {a['wikidata']: a['id'] for a in arr}; ritirati = 0
    for k, v in rg['ids'].items():
        if v.get('origine') in (ORIG, ORIG + 'b') and v.get('stato') == 'attivo' and k not in vivi:
            q = v.get('ids_esterni', {}).get('wikidata'); v['stato'] = 'lapide'; ritirati += 1
            if q in q_arr: v['verso'] = q_arr[q]
            else: v['motivo'] = 'ritirato: riclassificato/ambiguo dopo la risoluzione assistita (mai pubblicato come voce visibile)'
    if ritirati: rg['ids_sha256'] = hashlib.sha256('\n'.join(sorted(rg['ids'])).encode()).hexdigest(); json.dump(rg, open(rp, 'w'), ensure_ascii=False, indent=1, sort_keys=True)
    import subprocess; subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve().parent/'db_ids.py'), '--scrivi'], check=True, env=dict(__import__('os').environ, DB_ROOT=str(R)))
    costruisci_runtime()
SH, CH = 16, 500
IT = {'alive': 'In vita', 'deceased': 'Deceduto', 'dead': 'Deceduto', 'unknown': 'Sconosciuto', 'male': 'Maschio', 'female': 'Femmina', 'human': 'Umano', 'humans': 'Umani', 'asgardian': 'Asgardiano', 'kree': 'Kree', 'skrull': 'Skrull', 'mutant': 'Mutante', 'inhuman': 'Inumano', 'android': 'Androide', 'robot': 'Robot',
      'flight': 'Volo', 'super strength': 'Forza sovrumana', 'superhuman strength': 'Forza sovrumana', 'super speed': 'Velocità sovrumana', 'superhuman speed': 'Velocità sovrumana', 'superhuman durability': 'Resistenza sovrumana', 'durability': 'Resistenza', 'invulnerability': 'Invulnerabilità',
      'healing factor': 'Fattore rigenerante', 'accelerated healing': 'Guarigione accelerata', 'telepathy': 'Telepatia', 'telekinesis': 'Telecinesi', 'teleportation': 'Teletrasporto', 'energy projection': 'Proiezione di energia', 'shapeshifting': 'Mutaforma', 'invisibility': 'Invisibilità',
      'immortality': 'Immortalità', 'longevity': 'Longevità', 'magic': 'Magia', 'sorcery': 'Stregoneria', 'martial arts': 'Arti marziali', 'hand-to-hand combat': 'Combattimento corpo a corpo', 'expert marksman': 'Tiratore esperto', 'master tactician': 'Stratega esperto', 'genius intellect': 'Intelletto geniale',
      'master spy': 'Spia esperta', 'expert combatant': 'Combattente esperto', 'enhanced senses': 'Sensi potenziati', 'superhuman senses': 'Sensi sovrumani', 'size manipulation': 'Manipolazione delle dimensioni', 'weather manipulation': 'Controllo del clima', 'time travel': 'Viaggio nel tempo', 'regeneration': 'Rigenerazione',
      'shield': 'Scudo', 'sword': 'Spada', 'armor': 'Armatura', 'armour': 'Armatura', 'hammer': 'Martello', 'bow': 'Arco', 'suit': 'Costume', 'magic': 'Magia'}
def it(v): return IT.get(v.lower().strip(), v)

def costruisci_runtime():
    canon, arr = [], []
    for f in sorted((E/'canon').glob('w*_*.jsonl')):
        rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        (arr if 'arricchimenti' in f.name else canon).extend(rows)
    import shutil
    if OUTRT.exists(): shutil.rmtree(OUTRT)
    (OUTRT/'n').mkdir(parents=True); (OUTRT/'t').mkdir()
    recs = []
    for c in sorted(canon, key=lambda x: x['id']):
        recs.append({'i': c['id'], 'n': c['nome'], 'it': c.get('nome_it'), 't': c['tipo'], 'al': c.get('alias', []), 'd': (c.get('descrizione', {}).get('it') or c.get('descrizione', {}).get('en')),
                     'u': c.get('universo'), 'ip': c.get('interpreti', []), 'wd': c['ids_esterni']['wikidata'], 'wp': c.get('wikipedia', {}).get('en'), 'lv': c['livello'],
                     'f': {k: ([it(x) for x in v] if isinstance(v, list) else it(v)) for k, v in c.get('fatti', {}).items() if k not in ('interpreti_fonte', 'parenti', 'alias_fonte', 'creatori_fonte', 'relazioni_fonte')} or None,
                     'ff': {k: len(set(v)) for k, v in c.get('fatti_fonti', {}).items()} or None, 'xs': [[x['fonte'].split(' (')[0], x['url']] for x in c['fonti'] if x.get('licenza') == 'CC BY-SA 3.0']})
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
    LET = {'identita': 'p', 'entita-cosmica': 'p', 'organizzazione': 'o', 'artefatto': 'a', 'luogo': 'l', 'pianeta': 'P', 'evento': 'e', 'battaglia': 'e', 'universo': 'U', 'attore': 't', 'opera': 'O', 'creatore': 'C', 'specie': 'S', 'civilta': 'S'}
    stub = {'v': 1, 'r': [], 'x': {}, 'uni': {}}
    for o, r in enumerate(recs):
        if r['t'] == 'x': stub['x'][r['x']] = ' '.join(dict.fromkeys(norm(a) for a in r['al'] if a))[:160]; continue
        q = ' '.join(dict.fromkeys(w for w in norm(' '.join([r.get('it') or ''] + r['al'][:6] + r.get('ip', [])[:3])).split() if w))[:140]
        stub['r'].append([r['i'], r['n'], LET.get(r['t'], 'p'), r.get('u') or '', r['lv'], o, q])
        if r['t'] == 'universo': stub['uni'][r['i']] = {'n': r['n'], 'c': 'Luogo narrativo'}
    (OUTRT/'stub.json').write_text(json.dumps(stub, ensure_ascii=False, separators=(',', ':')))
    (OUTRT/'pre.json').write_text(json.dumps({p: sorted(l)[:300] for p, l in pre.items()}, separators=(',', ':')))
    tot = sum(len(gzip.compress(p.read_bytes())) for p in OUTRT.rglob('*.json'))
    tipi = collections.Counter(r['t'] for r in recs if r['t'] != 'x')
    (OUTRT/'meta.json').write_text(json.dumps({'tipi': dict(tipi), 'versione': 1, 'N': len(recs), 'SH': SH, 'CH': CH, 'nuove': len(canon), 'arricchite': len(arr), 'gz': tot}))
    print('runtime db:', len(recs), 'record, gz', tot, 'byte')
if __name__ == '__main__': main()
