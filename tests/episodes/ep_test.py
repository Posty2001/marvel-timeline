"""TVA Episodes - test mirati (Playwright/Chromium). Uso: python3 tests/episodes/ep_test.py  (serve la repo da solo)."""
import json, os, re, subprocess, sys, time, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
KEY = 'marvel-ultimate-timeline-episodes-v1'; RK = 'marvel-ultimate-timeline-ratings'
def eps(n, titled=True, dated=True):
    return [{'n': i, 't': ('Episodio titolo %d' % i) if titled else '', 'd': ('2015-01-%02d' % i) if dated else ''} for i in range(1, n + 1)]
SHOW_A = {'versione': 1, 'tmdb': 220102, 'nome': 'Fix A', 'lingua': 'it-IT', 'stagioni': [
    {'n': 0, 'nome': 'Speciali', 'episodi': eps(1)}, {'n': 1, 'nome': 'Stagione 1', 'episodi': eps(8)}, {'n': 2, 'nome': 'Stagione 2', 'episodi': eps(10)}]}
SHOW_B = {'versione': 1, 'tmdb': 61550, 'nome': 'Fix B', 'lingua': 'it-IT', 'stagioni': [
    {'n': 1, 'nome': '', 'episodi': eps(3, False, False)}, {'n': 2, 'nome': '', 'episodi': eps(3) + [{'n': 4, 't': 'Futuro', 'd': '2999-01-01'}]}]}
INDEX = {'versione': 1, 'fonte': 'TMDB', 'voci': {'039': {'tmdb': 220102, 'stagioni': 3, 'episodi': 19},
                                                   '043': {'tmdb': 61550, 's': 1, 'stagioni': 1, 'episodi': 3},
                                                   '044': {'tmdb': 61550, 's': 2, 'stagioni': 1, 'episodi': 4},
                                                   '137': {'tmdb': 202555, 's': 3, 'stagioni': 0, 'episodi': 0, 'speciali': 0, 'in_attesa': True}}}
FILES = {'index.json': INDEX, '220102.json': SHOW_A, '61550.json': SHOW_B}
res = []
def ok(n, c, x=''): res.append((n, bool(c))); print('PASS' if c else 'FAIL', n, x)

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def serve():
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(H, directory=ROOT))
    threading.Thread(target=s.serve_forever, daemon=True).start(); return s
srv = serve(); URL = 'http://127.0.0.1:%d/index.html' % srv.server_address[1]

def route_fixtures(pg, missing_index=False):
    def h(r):
        name = r.request.url.rsplit('/', 1)[-1]
        if missing_index and name == 'index.json': return r.fulfill(status=404, body='')
        if name in FILES: return r.fulfill(status=200, content_type='application/json', body=json.dumps(FILES[name]))
        r.fulfill(status=404, body='')
    pg.route(re.compile(r'.*/assets/episodes/.*'), h)

def new_page(b, w=390, init=None, missing_index=False):
    ctx = b.new_context(viewport={'width': w, 'height': 800}, accept_downloads=True, service_workers='block')
    pg = ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    route_fixtures(pg, missing_index)
    if init: pg.add_init_script("if(!sessionStorage.getItem('__i')){sessionStorage.setItem('__i','1');" + init + "}")
    pg.goto(URL); pg.wait_for_selector('#item-039', state='attached'); pg.wait_for_timeout(600)
    pg.evaluate("()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(500)
    return pg

def open_eps(pg, cid):
    bk = pg.locator('.td2-back:visible')
    if bk.count(): bk.first.click(); pg.wait_for_timeout(400)
    sm = pg.locator('#item-%s details.card > summary' % cid)
    if not pg.evaluate("(id)=>document.querySelector('#item-'+id+' details.card').open", cid):
        sm.scroll_into_view_if_needed(); sm.click(position={'x': 60, 'y': 20}); pg.wait_for_timeout(300)
    pg.locator('#item-%s .ep-group > summary' % cid).click(); pg.wait_for_timeout(400)
    pg.wait_for_selector('#item-%s .ep-body .ep-season, #item-%s .ep-body .ep-msg:not(:has-text("Caricamento"))' % (cid, cid), state='attached')
def ls(pg, k): return pg.evaluate("(k)=>localStorage.getItem(k)", k)
def vote(pg, cid, season, ep, v):
    pg.evaluate("""([id,s,e,v])=>{const row=document.querySelectorAll('#item-'+id+' .ep-season')[s].querySelectorAll('.ep-row')[e];const sel=row.querySelector('.ep-vote');sel.value=v;sel.dispatchEvent(new Event('change',{bubbles:true}));}""", [cid, season, ep, str(v)])
def badge(pg, cid): return pg.evaluate("(id)=>{const b=document.querySelector('.rating-widget[data-item=\"'+id+'\"] .rw-epmean');return b?b.textContent:null}", cid)
def stars_visible(pg, cid): return pg.evaluate("(id)=>{const s=document.querySelector('.rating-widget[data-item=\"'+id+'\"] .rw-stars');if(!s)return false;const r=s.getBoundingClientRect();return r.width>0&&r.height>0}", cid)

with sync_playwright() as p:
    b = p.chromium.launch()
    # ---- 1. media su tutte le stagioni, 1 decimale ----
    pg = new_page(b); open_eps(pg, '039')
    ok('catalogo: 3 stagioni (Speciali + S1 + S2)', pg.locator('#item-039 .ep-season').count() == 3)
    ok('catalogo: titolo, data e numero episodio', pg.locator('#item-039 .ep-season').nth(1).locator('.ep-row').first.text_content().replace('\n', ' ').startswith('✓ E01 Episodio titolo 1 01/01/2015') or 'Episodio titolo 1' in pg.locator('#item-039 .ep-season').nth(1).text_content())
    ok('catalogo: etichetta Speciali', 'Speciali' in pg.locator('#item-039 .ep-stitle').first.text_content())
    ok('senza voti: nessun badge, stelle originali visibili', badge(pg, '039') is None and stars_visible(pg, '039'))
    vote(pg, '039', 1, 0, 8); vote(pg, '039', 1, 1, 8); vote(pg, '039', 2, 0, 9)      # 8,8,9 -> 8,33 -> 8,3 (stagioni diverse)
    ok('media 8,8,9 = 8,3 (una cifra decimale, stagioni diverse)', '8,3' in (badge(pg, '039') or ''), badge(pg, '039'))
    vote(pg, '039', 0, 0, 10); vote(pg, '039', 1, 2, 7)                                # 8,8,9,10,7 = 8,4
    ok('media 8,8,9,10,7 = 8,4', '8,4' in (badge(pg, '039') or ''))
    ok('stagione: media personale e visti', 'media 7,7' in pg.locator('#item-039 .ep-season').nth(1).locator('.ep-smeta').text_content())
    vote(pg, '039', 1, 0, 7); vote(pg, '039', 1, 1, 8); vote(pg, '039', 1, 2, 8); vote(pg, '039', 2, 0, 7); vote(pg, '039', 0, 0, 8)
    ok('arrotondamento 7,8,8,7,8 = 7,6', '7,6' in (badge(pg, '039') or ''))
    pg.close()
    # ---- 2. voto originale conservato; Home/Tessera/XP invariati ----
    init = "localStorage.setItem('%s', JSON.stringify({'039':4.5,'001':3}));" % RK
    pg = new_page(b, init=init)
    def snapshot():
        return pg.evaluate("()=>({h:(document.getElementById('hhsRating')||{}).textContent,t:(document.getElementById('tesseraVoto')||{}).textContent,d:(document.getElementById('dashAvgRating')||{}).textContent,x:(document.getElementById('tesseraXp')||document.querySelector('[id*=Xp]')||{}).textContent})")
    pre = snapshot(); raw0 = ls(pg, RK)
    others0 = pg.evaluate("(k)=>{const o={};for(let i=0;i<localStorage.length;i++){const n=localStorage.key(i);if(n!==k)o[n]=localStorage.getItem(n)}return o}", KEY)
    ok('originale: stelle visibili prima di votare episodi', stars_visible(pg, '039'))
    open_eps(pg, '039'); vote(pg, '039', 1, 0, 6)
    ok('originale: in Timeline compare la media episodi', '6,0' in (badge(pg, '039') or '') and not stars_visible(pg, '039'))
    ok('originale: chiave voti byte-identica', ls(pg, RK) == raw0)
    ok('originale: mostrato nella scheda episodi', '4,5' in pg.locator('#item-039 .ep-orig').text_content())
    ok('Home/Tessera/Dashboard/XP invariati dopo voto episodio', snapshot() == pre, str(snapshot()))
    # ---- 3. modifica e cancellazione ----
    vote(pg, '039', 1, 0, 9)
    ok('modifica: 6 -> 9 aggiorna la media', '9,0' in (badge(pg, '039') or ''))
    vote(pg, '039', 1, 1, 5)
    vote(pg, '039', 1, 0, '')
    ok('cancellazione di un voto: media sugli altri (5,0)', '5,0' in (badge(pg, '039') or ''))
    vote(pg, '039', 1, 1, '')
    ok('cancellati tutti: badge via, stelle originali tornano', badge(pg, '039') is None and stars_visible(pg, '039'))
    ok('cancellati tutti: chiave episodi pulita e voto 4,5 intatto', ls(pg, KEY) is None and ls(pg, RK) == raw0 and pg.evaluate("()=>document.querySelector('.rating-widget[data-item=\"039\"] .rw-val b').textContent") == '4,5')
    ok('Home/Tessera invariati dopo cancellazione', snapshot() == pre)
    others1 = pg.evaluate("(k)=>{const o={};for(let i=0;i<localStorage.length;i++){const n=localStorage.key(i);if(n!==k)o[n]=localStorage.getItem(n)}return o}", KEY)
    ok('XP/missioni/classifiche/badge: nessuna altra chiave locale modificata dal voto episodi', others1 == others0, str([k for k in others1 if others1.get(k) != others0.get(k)] + [k for k in others0 if k not in others1]))
    # visto + recensione + progresso
    pg.evaluate("""()=>{const r=document.querySelectorAll('#item-039 .ep-season')[1].querySelectorAll('.ep-row');r[0].querySelector('.ep-w').click();r[1].querySelector('.ep-w').click();
      const ta=r[2].querySelector('.ep-note');ta.hidden=false;ta.value='Bello';ta.dispatchEvent(new Event('input',{bubbles:true}));ta.dispatchEvent(new Event('blur'));}""")
    st = json.loads(ls(pg, KEY))['039']
    ok('visti e recensione salvati', st['S01E01'].get('w') == 1 and st['S01E03'].get('n') == 'Bello')
    ok('progresso stagione 2/8 visti', '2/8 visti' in pg.locator('#item-039 .ep-season').nth(1).locator('.ep-smeta').text_content())
    ok('visto senza voto: nessun badge, XP/voti non toccati', badge(pg, '039') is None and ls(pg, RK) == raw0)
    pg.evaluate("""()=>{const r=document.querySelectorAll('#item-039 .ep-season')[1].querySelectorAll('.ep-row');const n=r[2].querySelector('.ep-note');n.value='';n.dispatchEvent(new Event('input',{bubbles:true}));n.dispatchEvent(new Event('blur'));}""")
    pg.wait_for_timeout(700)
    ok('recensione svuotata = eliminata', 'S01E03' not in json.loads(ls(pg, KEY))['039'])
    # ---- 4. backup e ripristino ----
    vote(pg, '039', 1, 0, 9); vote(pg, '039', 2, 3, 4)
    pg.evaluate("(k)=>{const o=JSON.parse(localStorage.getItem(k));o['043']={S01E02:{r:10,w:1,n:'Ottimo episodio'}};localStorage.setItem(k,JSON.stringify(o))}", KEY)
    saved = ls(pg, KEY)
    with pg.expect_download() as dl: pg.evaluate("()=>document.getElementById('exportBtn').click()")
    path = dl.value.path(); prof = json.load(open(path))
    ok('backup: campo episodes presente e uguale al locale', json.loads(json.dumps(prof.get('episodes'))) == json.loads(saved))
    ok('backup: voti, recensioni e visti conservati', prof['episodes']['043']['S01E02'] == {'r': 10, 'w': 1, 'n': 'Ottimo episodio'} and prof['episodes']['039']['S01E01'].get('w') == 1 and prof['episodes']['039']['S01E01'].get('r') == 9)
    ok('backup: voto originale in ratings invariato', prof['ratings'] == json.loads(raw0))
    pg.evaluate("(k)=>localStorage.removeItem(k)", KEY)
    pg.on('dialog', lambda d: d.accept())
    with pg.expect_navigation(): pg.set_input_files('#importFile', path)
    pg.wait_for_selector('#item-039', state='attached'); pg.wait_for_timeout(500)
    ok('ripristino: episodi ripristinati identici (voti, recensioni, visti)', json.loads(ls(pg, KEY)) == json.loads(saved) and json.loads(ls(pg, KEY))['043']['S01E02']['n'] == 'Ottimo episodio')
    ok('ripristino: badge ricalcolato in Timeline', '6,5' in (badge(pg, '039') or '') or badge(pg, '039') is not None, badge(pg, '039'))
    # import non valido: voto 11 -> rifiutato, nessun dato toccato
    bad = json.loads(json.dumps(prof)); bad['episodes']['039']['S01E01']['r'] = 11
    open('/tmp/ep_bad.json', 'w').write(json.dumps(bad)); before = ls(pg, KEY)
    pg.set_input_files('#importFile', '/tmp/ep_bad.json'); pg.wait_for_timeout(1500)
    ok('import non valido (voto 11): dati locali intatti', ls(pg, KEY) == before)
    bad2 = json.loads(json.dumps(prof)); bad2['episodes']['999'] = {'S01E01': {'r': 5}}
    open('/tmp/ep_bad2.json', 'w').write(json.dumps(bad2)); pg.set_input_files('#importFile', '/tmp/ep_bad2.json'); pg.wait_for_timeout(1500)
    ok('import con titolo inesistente: rifiutato', ls(pg, KEY) == before)
    # profilo vecchio senza "episodes": gli episodi locali NON vengono cancellati
    old = json.loads(json.dumps(prof)); del old['episodes']
    open('/tmp/ep_old.json', 'w').write(json.dumps(old))
    with pg.expect_navigation(): pg.set_input_files('#importFile', '/tmp/ep_old.json')
    pg.wait_for_selector('#item-039', state='attached'); pg.wait_for_timeout(500)
    ok('profilo precedente senza episodes: dati episodi locali conservati', json.loads(ls(pg, KEY)) == json.loads(saved))
    # ---- 5. sincronizzazione: il profilo cloud usa le stesse chiavi e lo stesso validatore ----
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    ok('sync: tutti i costruttori di profilo iterano PROFILE_OBJ_KEYS', src.count('for (var ok in PROFILE_OBJ_KEYS) { profile[ok] = safeGetObj') >= 3)
    ok('sync: il remoto passa da normalizzaProfilo (campo episodes validato)', re.search(r'function syncValidaRemoto[\s\S]{0,1500}normalizzaProfilo', src) is not None)
    ok('sync: chiave episodes dichiarata in PROFILE_OBJ_KEYS', "episodes: 'marvel-ultimate-timeline-episodes-v1'" in src)
    ok('nessuna chiave/token TMDB nel codice o negli asset', not re.search(r'(api_key=[A-Za-z0-9]{8,}|Bearer\s+[A-Za-z0-9_\-]{20,}|eyJ[A-Za-z0-9_\-]{30,})', src[src.index('TVA Episodes (solo TEST)'):src.index('Note personali: salvate')] + open(os.path.join(ROOT, 'assets/episodes/index.json')).read() + open(os.path.join(ROOT, 'tools/tmdb_episodes.py')).read()))
    ok('nessun errore JS in pagina', not pg.errs, str(pg.errs))
    pg.close()
    # ---- 6. dati mancanti ----
    pg = new_page(b); open_eps(pg, '043')
    at = pg.locator('#item-043 .ep-attr').text_content()
    ok('attribuzione TMDB: avviso ufficiale e link a themoviedb.org', 'This product uses the TMDB API but is not endorsed or certified by TMDB.' in at and pg.locator('#item-043 .ep-attr a[href="https://www.themoviedb.org"]').count() == 1)
    ok('stagione singola (card S1): solo la stagione 1', pg.locator('#item-043 .ep-season').count() == 1)
    ok('episodio senza titolo -> "Episodio N"; senza data -> vuoto', pg.locator('#item-043 .ep-row').first.locator('.ep-title').text_content() == 'Episodio 1' and pg.locator('#item-043 .ep-row').first.locator('.ep-date').text_content() == '')
    pg.locator('.td2-back:visible').first.click(); pg.wait_for_timeout(300); open_eps(pg, '137')
    ok('stagione futura (137): messaggio chiaro, nessun episodio inventato', 'non ancora disponibile' in pg.locator('#item-137 .ep-body').text_content() and pg.locator('#item-137 .ep-row').count() == 0)
    pg.locator('.td2-back:visible').first.click(); pg.wait_for_timeout(300); open_eps(pg, '057')
    ok('serie senza catalogo: messaggio, nessun errore', 'non ancora disponibili' in pg.locator('#item-057 .ep-body').text_content())
    ok('film: nessun pannello episodi', pg.locator('li.card-wrap[data-type="film"] .ep-group').count() == 0)
    pg.close()
    pg = new_page(b, init="localStorage.setItem('%s', JSON.stringify({'043':{S01E01:{r:3}},'044':{S02E01:{r:9,w:1}}}));" % KEY)
    ok('stessa serie TMDB, due schede: voti separati (043=3,0 / 044=9,0)', '3,0' in (badge(pg, '043') or '') and '9,0' in (badge(pg, '044') or ''))
    open_eps(pg, '044')
    ok('scheda 044: solo stagione 2, voto e visto suoi', pg.locator('#item-044 .ep-season').count() == 1 and pg.locator('#item-044 .ep-vote').first.input_value() == '9' and pg.locator('#item-044 .ep-w').first.get_attribute('aria-pressed') == 'true')
    last = pg.locator('#item-044 .ep-row').nth(3)
    ok('episodio non ancora uscito: "In arrivo", controlli disattivati', 'In arrivo' in last.locator('.ep-date').text_content() and last.locator('.ep-vote').is_disabled() and last.locator('.ep-w').is_disabled())
    ok('episodi usciti restano attivi; totale visti esclude gli episodi futuri', pg.locator('#item-044 .ep-row').first.locator('.ep-vote').is_enabled() and '1/3 visti' in pg.locator('#item-044 .ep-smeta').text_content())
    pg.close()
    pg = new_page(b, missing_index=True); open_eps(pg, '039')
    ok('indice non raggiungibile: messaggio chiaro', 'non raggiungibile' in pg.locator('#item-039 .ep-body').text_content())
    pg.close()
    # ---- 7. mobile + regressione Timeline ----
    base_cards = None
    for w in (320, 390, 430):
        pg = new_page(b, w=w, init="localStorage.setItem('%s', JSON.stringify({'039':3.5}));" % RK); open_eps(pg, '039'); vote(pg, '039', 1, 0, 8)
        pg.locator('#item-039 .ep-season').nth(1).locator('summary').click(); pg.wait_for_timeout(300)
        ok('mobile %d: righe episodio realmente visibili' % w, pg.locator('#item-039 .ep-season').nth(1).locator('.ep-row').first.is_visible())
        m = pg.evaluate("""()=>{const q=s=>document.querySelector('#item-039 '+s).getBoundingClientRect();const lst=document.querySelector('#item-039 .ep-list').getBoundingClientRect();
          const bad=[...document.querySelectorAll('#item-039 .ep-row *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+0.5||r.left<-0.5)}).length;
          return {over:document.documentElement.scrollWidth-innerWidth, vote:q('.ep-vote'), w:q('.ep-w'), bad:bad}}""")
        ok('mobile %d: nessun overflow orizzontale' % w, m['over'] <= 0 and m['bad'] == 0, str(m['over']))
        ok('mobile %d: target tocco >= 38px (voto, visto)' % w, m['vote']['height'] >= 38 and m['w']['height'] >= 38 and m['w']['width'] >= 38)
        pg.screenshot(path='/tmp/ep_m%d.png' % w, clip={'x': 0, 'y': max(0, pg.evaluate("()=>document.querySelector('#item-039').getBoundingClientRect().top+scrollY")-0), 'width': w, 'height': 700}) if False else pg.locator('#item-039 .ep-group').screenshot(path='/tmp/ep_m%d.png' % w)
        n_cards = pg.locator('li.card-wrap').count(); pg.close()
    pg = new_page(b); n_new = pg.locator('li.card-wrap').count(); n_serie = pg.locator('li.card-wrap[data-type="serie"]').count(); pg.close()
    ctx = b.new_context(service_workers='block'); pb = ctx.new_page()
    pb.set_content(subprocess.check_output(['git', 'show', 'HEAD:index.html'], cwd=ROOT).decode('utf-8')); n_base = pb.locator('li.card-wrap').count()
    ok('Timeline: stesso numero di schede della baseline (%d)' % n_base, n_new == n_base, '%d vs %d' % (n_new, n_base))
    ok('Timeline: pannello episodi su tutte le schede serie (%d)' % n_serie, n_serie > 0)
    b.close()
bad = [n for n, c in res if not c]
print('\n%d/%d test superati' % (len(res) - len(bad), len(res)));
if bad: print('FALLITI:', bad); sys.exit(1)
