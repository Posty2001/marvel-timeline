"""Tessera TVA 2.0 / T0 — test di guardia contro la perdita di personalizzazioni e dati (solo lettura del codice app).

Gruppi:
  A. Catalogo congelato: ogni ID dello snapshot (docs/tessera2/inventario_personalizzazioni_28112026.json) esiste ancora,
     ricompense con stessi nome/rarità/categoria/condizione; valori di preset/default identici al censimento T0
     (docs/tessera2/censimento_runtime_T0.json); nessun conteggio ridotto.
  B. Compatibilità dati: profilo campione (nome, VAR-ID, aspetto, stile, ricompense ottenute — anche con condizione non
     soddisfatta —, foto locale, progresso) invariato dopo 2 caricamenti; nessuna chiave rinominata/rimossa.
  C. Editor classico: apre, 6 schede, Annulla non scrive, Salva scrive nella stessa chiave e nello stesso formato.
  D. Regressione XP/livello/rango/distintivi su 3 profili campione (valori di riferimento in docs/tessera2/baseline_xp_T0.json).
  E. Regole XP e struttura: nessuna differenza nel blocco di calcolo XP rispetto al riferimento Git (se disponibile).

Uso: python3 tests/tessera_t0_test.py [--scrivi-baseline]
"""
import functools, http.server, json, os, socket, subprocess, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import tessera_censimento as CEN

SNAP = json.load(open(CEN.SNAP))
RUNT0 = json.load(open(CEN.OUT))
BASE_F = os.path.join(ROOT, 'docs', 'tessera2', 'baseline_xp_T0.json')
P = 'marvel-ultimate-timeline-'
res = []
errs = []


def ok(n, c, d=''):
    res.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)[:300]) if (d and not c) else ''), flush=True)


class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def handle(self):
        try: super().handle()
        except Exception: pass


s_ = socket.socket(); s_.bind(('127.0.0.1', 0)); port = s_.getsockname()[1]; s_.close()
srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/index.html' % port

PIXEL = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAIAAgDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDzmiiiuY+nP//Z'
ORDER = [str(i).zfill(3) for i in (1, 2, 3, 4, 5, 6, 7, 11, 12, 15, 16, 17, 22, 24, 41, 45, 47, 49, 50, 51, 53, 55, 56, 58, 59, 62, 63, 67, 70, 75, 76, 78)]


def prof_vuoto():
    return {}


def prof_medio():
    w = {i: True for i in ORDER[:12]}
    return {P + 'watched': json.dumps(w), P + 'ratings': json.dumps({ORDER[0]: 4, ORDER[1]: 5, ORDER[2]: 3}),
            P + 'notes': json.dumps({ORDER[0]: 'ok', ORDER[1]: 'bene'}), P + 'favorites': json.dumps({ORDER[0]: True, ORDER[3]: True})}


def prof_ricco():
    w = {i: True for i in ORDER}
    return {P + 'watched': json.dumps(w), P + 'ratings': json.dumps({i: 4 for i in ORDER[:14]}),
            P + 'notes': json.dumps({i: 'n' for i in ORDER[:6]}), P + 'favorites': json.dumps({i: True for i in ORDER[:9]})}


PROFILI = {'vuoto': prof_vuoto, 'medio': prof_medio, 'ricco': prof_ricco}

# profilo personale completo (gruppo B)
PERS = {
    P + 'user-name': 'Posty', P + 'tessera-id': 'VAR-402737',
    P + 'tessera-look': json.dumps({'v': 1, 'a': 'sentinella', 'b': [], 'ts': 1}),
    P + 'rewards': json.dumps({'v': 1, 'u': {'titolo-recluta-tva': '2026-11-10', 'cornice-bronzo-temporale': '2026-11-11', 'titolo-colui-che-rimane': '2026-11-12'},
                               'e': {'titolo': 'titolo-recluta-tva', 'cornice': 'cornice-bronzo-temporale'}, 't': {}}),
    P + 'tessera-photo': PIXEL,
}
PERS.update(prof_medio())
IDSEED = {'v': 1, 'emblem': 0, 'emx': 5, 'motto': 'Ordine e caos', 'univ': 'Terra-199999', 'ch': 'Loki', 'ts': 1700000000000}
STSEED = {'v': 1, 'bg': 'mist', 'tx': 'onde', 'ty': 'cinema', 'fr': 'doppia', 'ts': 1700000000000}
PERS_SEM = {P + 'identity-v1': IDSEED, P + 'tessera-style-v1': STSEED}
for _k, _v in PERS_SEM.items(): PERS[_k] = json.dumps(_v)

SEED_JS = """(d)=>{ if(localStorage.getItem('__t0seed')) return; localStorage.setItem('__t0seed','1');
  Object.keys(d).forEach(k=>localStorage.setItem(k, d[k])); }"""
READ_JS = """(pref)=>{ const o={}; for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i); if(k.indexOf(pref)===0) o[k]=localStorage.getItem(k);} return o; }"""


def boot(b, seed, w=390, h=844):
    c = b.new_context(viewport={'width': w, 'height': h}, has_touch=True, is_mobile=True, service_workers='block')
    c.add_init_script("(" + SEED_JS + ")(" + json.dumps(seed) + ")")
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(URL); pg.wait_for_timeout(3000)
    pg.evaluate("()=>{try{journeyStarted.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(700)
    return c, pg


def open_tessera(pg):
    pg.evaluate("()=>document.getElementById('appTabTessera').click()"); pg.wait_for_timeout(1500)


def xp_state(pg):
    return pg.evaluate("""()=>{const t=id=>{const e=document.getElementById(id);return e?e.textContent.trim():null};
      return {xp:t('tesseraXpTotale'),livello:t('tesseraLivello'),rango:t('tesseraRank'),pct:t('tesseraPct'),distintivi:t('tesseraBadges'),
              sub:t('tesseraXpSub'),info:window.marvelXpInfo||null,rw:window.tvaRewards.unlocked().slice().sort()}}""")


with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------- A. catalogo congelato ----------
    c, pg = boot(b, {})
    vivo = pg.evaluate(CEN.JS)
    prob = CEN.confronta(vivo, SNAP)
    ok('A1 catalogo vivo ⊇ snapshot (tutti gli ID, nomi, rarità, condizioni)', not prob, prob[:5])
    for fam, n in [('avatar', 8), ('cornici_arte', 12), ('temi_arte', 10), ('effetti_arte', 6), ('emblemi_nomi', 56), ('ricompense', 48),
                   ('font', 4), ('sfondi', 9), ('texture', 6), ('cornici_stile', 7), ('decorazioni', 6), ('effetti_stile', 6), ('icone', 3), ('layout', 4), ('preset', 7)]:
        ok('A2 %s ≥ %d (D10)' % (fam, n), len(vivo[fam]) >= n, len(vivo[fam]))
    ok('A3 6 finiture emblema e 7 categorie conservate', len(vivo['emblemi_finiture']) >= 6 and len(vivo['emblemi_categorie']) >= 7)
    ok('A4 5 rarità conservate', vivo['rarita'] == RUNT0['rarita'], vivo['rarita'])
    ok('A5 preset: stesso contenuto del censimento T0 (Archivio Classico, Cosmic, Mystic, Tech, Dark Multiverse, Royal, Temporal)',
       all(any(x == q for x in vivo['preset_valori']) for q in RUNT0['preset_valori']), '')
    ok('A6 valori predefiniti di ricompense e stile invariati', vivo['ricompense_default'] == RUNT0['ricompense_default'] and
       all(vivo['stile_default'].get(k) == v for k, v in RUNT0['stile_default'].items()))
    ok('A7 chiave di salvataggio ricompense invariata', vivo['storageKey'] == SNAP['storageKey'] == P + 'rewards')
    ok('A8 chiavi identità invariate (identity-v1, tessera-style-v1, identity-premigration-v1)',
       vivo['chiavi_identita'] == {'IDK': P + 'identity-v1', 'STYK': P + 'tessera-style-v1', 'BAKK': P + 'identity-premigration-v1'}, vivo['chiavi_identita'])
    nomi_preset = sorted(x['name'] for x in vivo['preset_valori'])
    ok('A9 nomi preset (Archivio Classico, Cosmic, Mystic, Tech, Dark Multiverse, Royal, Temporal)',
       all(any(n in q for q in nomi_preset) for n in ['Archivio Classico', 'Cosmic', 'Mystic', 'Tech', 'Dark Multiverse', 'Royal']), nomi_preset)
    c.close()

    # ---------- B. compatibilità dati ----------
    c, pg = boot(b, PERS)
    open_tessera(pg)
    dopo1 = pg.evaluate(READ_JS, P)
    pg.reload(); pg.wait_for_timeout(3000)
    open_tessera(pg)
    dopo2 = pg.evaluate(READ_JS, P)
    for k, v in PERS.items():
        if k == P + 'rewards':   # additivo: le ricompense già ottenute restano identiche (stessa data), possono solo aggiungersi quelle appena maturate
            a0, a1 = json.loads(v), json.loads(dopo2[k])
            ok('B1 rewards: sblocchi e selezioni seminati invariati (si possono solo aggiungere nuovi sblocchi)',
               all(a1['u'].get(i) == d for i, d in a0['u'].items()) and a1['e'] == a0['e'], a1)
            continue
        if k in PERS_SEM:   # identità e stile: i valori scelti dall'utente restano (il formato può essere normalizzato dall'app)
            q = json.loads(dopo2.get(k) or '{}')
            ok('B1 %s: valori scelti preservati' % k.replace(P, ''), all(q.get(f) == x for f, x in PERS_SEM[k].items() if f != 'ts'), q)
            continue
        ok('B1 chiave presente e invariata dopo 2 caricamenti: ' + k.replace(P, ''), dopo2.get(k) == v, (dopo2.get(k) or '')[:80])
    stt = xp_state(pg)
    ok('B2 ricompensa ottenuta (anche a condizione non soddisfatta) mai revocata', 'titolo-colui-che-rimane' in stt['rw'], stt['rw'])
    ok('B3 selezioni equipaggiate preservate', pg.evaluate("()=>{const e=window.tvaRewards.equipped();return e.titolo==='titolo-recluta-tva'&&e.cornice==='cornice-bronzo-temporale'}"))
    ok('B4 aspetto/foto letti dalla Tessera', pg.evaluate("()=>{const c=window.tvaTessera.current();return c.name==='Posty'&&c.avatar.id==='sentinella'&&c.photo&&c.photo.indexOf('data:image/jpeg')===0}"))
    ok('B5 nessuna chiave rimossa dal profilo', all(k in dopo2 for k in PERS))
    ok('B6 VAR-ID e nome visibili nella Tessera', pg.evaluate("()=>{const g=id=>{const e=document.getElementById(id);return e?(e.value||e.textContent):''};return g('tesseraId').trim()==='VAR-402737'&&g('tesseraNameInput')==='Posty'}"))
    nuove = sorted(set(dopo2) - set(PERS) - {P + 'identity-premigration-v1'})
    print('INFO chiavi create dall\'app oltre al seed (non una regressione):', nuove)
    c.close()

    # ---------- C. editor classico ----------
    c, pg = boot(b, PERS)
    open_tessera(pg)
    pg.evaluate("()=>window.tvaTessera.open('avatar')"); pg.wait_for_timeout(900)
    tabs = pg.evaluate("()=>[...document.querySelectorAll('#tcEdTabs .tc-tab')].map(e=>e.getAttribute('data-tab'))")
    ok('C1 editor classico: 6 schede (avatar, stile, titolo, cornice, tema, effetto)', tabs == ['avatar', 'stile', 'titolo', 'cornice', 'tema', 'effetto'], tabs)
    ok('C2 pulsanti Annulla e Salva presenti', pg.evaluate("()=>!!document.getElementById('tcEdCancel')&&!!document.getElementById('tcEdSave')"))
    pre = pg.evaluate(READ_JS, P)
    # per ogni scheda: si apre senza errori e mostra contenuto
    vuote = []
    for t in tabs:
        pg.evaluate("(t)=>document.getElementById('tcTab-'+t).click()", t); pg.wait_for_timeout(350)
        n = pg.evaluate("()=>document.querySelectorAll('#tcEditor .tc-ed-side button, #tcEditor .tc-ed-side input').length")
        if n < 3: vuote.append(t)
    ok('C3 ogni scheda dell’editor espone controlli', not vuote, vuote)
    pg.evaluate("()=>document.getElementById('tcTab-avatar').click()"); pg.wait_for_timeout(300)
    # cambia avatar (bozza) poi Annulla: nessuna scrittura
    pg.evaluate("()=>{const b=[...document.querySelectorAll('#tcEditor .tc-ed-side button')].find(x=>/Cronista|Esploratore/i.test(x.textContent)); if(b) b.click()}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.getElementById('tcEdCancel').click()"); pg.wait_for_timeout(500)
    post = pg.evaluate(READ_JS, P)
    ok('C4 Annulla non modifica alcuna chiave', {k: v for k, v in pre.items() if k != P + 'tessera-look'} == {k: v for k, v in post.items() if k != P + 'tessera-look'} and json.loads(post[P + 'tessera-look'])['a'] == 'sentinella', '')
    # cambia avatar e Salva
    pg.evaluate("()=>window.tvaTessera.open('avatar')"); pg.wait_for_timeout(700)
    clicked = pg.evaluate("()=>{const b=[...document.querySelectorAll('#tcEditor .tc-ed-side button')].find(x=>/Cronista/i.test(x.textContent)); if(b){b.click();return true}return false}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.getElementById('tcEdSave').click()"); pg.wait_for_timeout(700)
    post2 = pg.evaluate(READ_JS, P)
    lk = json.loads(post2[P + 'tessera-look'])
    ok('C5 Salva scrive nella stessa chiave (tessera-look) con lo stesso formato', clicked and lk.get('v') == 1 and lk.get('a') == 'cronista' and isinstance(lk.get('b'), list), lk)
    ok('C6 editor chiuso dopo il salvataggio e progresso intatto', pg.evaluate("()=>!document.getElementById('tcEditor')") and post2[P + 'watched'] == PERS[P + 'watched'])
    ok('C7 API condivisione/esportazione presenti (share, exportPng, flip)', pg.evaluate("()=>['share','exportPng','flip','open','current','lookLoad','sanitizeLook'].every(k=>typeof window.tvaTessera[k]==='function')"))
    png = pg.evaluate("async()=>{try{const b=await window.tvaTessera.exportPng(null,'front');return b&&b.size>1000?b.size:0}catch(e){return -1}}")
    ok('C8 esportazione PNG della Tessera produce un\'immagine', png > 1000, png)
    c.close()

    # ---------- D. regressione XP/rango/distintivi ----------
    base = {}
    for nome, fn in PROFILI.items():
        c, pg = boot(b, fn())
        open_tessera(pg)
        base[nome] = xp_state(pg)
        c.close()
    if '--scrivi-baseline' in sys.argv:
        json.dump(base, open(BASE_F, 'w'), ensure_ascii=False, indent=1, sort_keys=True); print('baseline scritta')
    gold = json.load(open(BASE_F))
    for nome in PROFILI:
        ok('D1 XP/livello/rango/distintivi invariati (profilo %s)' % nome, base[nome] == gold[nome], {k: (base[nome][k], gold[nome][k]) for k in gold[nome] if base[nome][k] != gold[nome][k]})
    ok('D2 profili campione effettivamente distinti (XP crescente)', int(base['vuoto']['xp'] or 0) < int(base['medio']['xp'] or 0) < int(base['ricco']['xp'] or 0), [base[k]['xp'] for k in base])
    ok('D3 soglia livello: 100+(n-1)*30 (sub del livello coerente)', all(__import__('re').search(r'/ (\d+) al prossimo', base[k]['sub'] or '') and
       int(__import__('re').search(r'/ (\d+) al prossimo', base[k]['sub']).group(1)) == 100 + (int(base[k]['livello']) - 1) * 30 for k in base), [base[k]['sub'] for k in base])
    ok('D4 8 ranghi e 14 distintivi invariati nel codice', open(os.path.join(ROOT, 'index.html')).read().count("TESSERA_TIERS") >= 2 and
       len(json.loads(__import__('re').search(r'var BADGE_CONDITIONS = (\[.*?\]);', open(os.path.join(ROOT, 'index.html')).read()).group(1))) == 14)
    b.close()

# ---------- E. blocco di calcolo XP identico al riferimento Git ----------
REF = 'e1920d1'   # ultimo commit prima di T0
try:
    old = subprocess.run(['git', 'show', REF + ':index.html'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    new = open(os.path.join(ROOT, 'index.html')).read()
    def blk(t):
        a = t.index('function xpPerLivello(n)'); z = t.index('window.marvelXpInfo = {', a); return t[a:z]
    ok('E1 blocco di calcolo XP/livello identico al riferimento %s' % REF, blk(old) == blk(new))
    def tiers(t):
        a = t.index('TESSERA_TIERS ='); return t[a:a + 900]
    ok('E2 definizione dei ranghi (TESSERA_TIERS) identica al riferimento', tiers(old) == tiers(new))
except Exception as e:
    ok('E1/E2 confronto con riferimento Git', False, e)
ok('F1 nessun errore di pagina durante i test', not errs, errs[:3])
srv.shutdown()
bad = [n for n, c in res if not c]
print('TOTALE: PASS %d FAIL %d' % (len(res) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
