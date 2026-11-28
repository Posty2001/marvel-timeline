"""A5 — interfaccia: preferiti, raccolte, progressione, tracker del dossier, XP in Tessera, dati esistenti intatti. Uso: python3 tests/a5_ui_test.py"""
import os, socket, threading, http.server, functools, json
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res, errs = [], []
def ok(n, c, d=''):
    res.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)) if (d and not c) else ''))
def free():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
port = free(); srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:%d/index.html' % port
def go(pg, js, w=700): pg.evaluate(js); pg.wait_for_timeout(w)
def boot(ctx, init=None):
    if init: ctx.add_init_script(init)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(U); pg.wait_for_timeout(3000)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    go(pg, "()=>document.getElementById('a2Entry').click()"); go(pg, "()=>document.querySelector('#atlas2 .a3-ban').click()", 1500); return pg
XPJS = "()=>window.marvelXpInfo&&window.marvelXpInfo.xp"
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 800}, is_mobile=True, has_touch=True, service_workers='block')
    pg = boot(ctx)
    other0 = pg.evaluate("()=>Object.keys(localStorage).filter(k=>!k.startsWith('tva-atlante-v2')).sort().map(k=>[k,localStorage.getItem(k)])")
    # Home: portali
    ok('Home: portali «Preferiti e raccolte» e «Progressione»', pg.evaluate("()=>!!document.querySelector('#atlas2 [data-portal=pf]')&&!!document.querySelector('#atlas2 [data-portal=pr]')"))
    # dossier di un personaggio reale
    ids = pg.evaluate("()=>{const c=window.tvaA3.ctx();return (c.IDX.voci.filter(v=>v.t==='p'&&v.k!=='c').slice(0,40)).map(v=>v.i)}")
    pg.evaluate("(i)=>window.tvaA3.open(i)", ids[0]); pg.wait_for_timeout(1800)
    ok('Dossier: pulsanti Preferito e Raccolte', pg.evaluate("()=>!!document.querySelector('#atlas2 .a5-fav')&&!!document.querySelector('#atlas2 .a5-col')"))
    ok('A6: pulsante «Chiedi a Miss Minutes», host.ask e tvaAtlasOpen presenti', pg.evaluate("()=>!!document.querySelector('#atlas2 .a5-mm')&&typeof window.tvaMissMinutesHost.ask==='function'&&typeof window.tvaAtlasOpen==='function'"))
    ok('A6: senza preferenza v2 host.open(atl:) rifiuta (fallback classico)', pg.evaluate("(i)=>window.tvaMissMinutesHost.open('atl:'+i)", ids[5]) is False)
    pg.evaluate("()=>localStorage.setItem('tva-atlante-ui','v2')")
    pg.evaluate("(i)=>window.tvaMissMinutesHost.open('atl:'+i)", ids[5]); pg.wait_for_timeout(2200)
    ok('A6: con preferenza v2 host.open(atl:<id>) apre il dossier', pg.evaluate("(i)=>(window.tvaA3.ctx().api.ST.a3||{}).id===i", ids[5]))
    pg.evaluate("()=>localStorage.removeItem('tva-atlante-ui')")
    pg.evaluate("(i)=>window.tvaA3.open(i)", ids[0]); pg.wait_for_timeout(1500)
    pg.click('#atlas2 .a5-fav'); pg.wait_for_timeout(300)
    st = json.loads(pg.evaluate("()=>localStorage.getItem('tva-atlante-v2')"))
    ok('Preferito salvato in tva-atlante-v2', ids[0] in st['fav'] and pg.get_attribute('#atlas2 .a5-fav', 'aria-pressed') == 'true', st)
    pg.click('#atlas2 .a5-col'); pg.wait_for_timeout(300)
    if os.environ.get('DBG'): print(pg.evaluate("()=>{const o=document.querySelector('.a5-ov');const r=o.getBoundingClientRect();const i=document.querySelector('.a5-inp').getBoundingClientRect();return [!!document.getElementById('a5-css'),getComputedStyle(o).position,r.width,r.height,i.width,i.height,o.parentNode.tagName]}"))
    pg.fill('.a5-sheet .a5-inp', 'Prova'); pg.click('.a5-sheet >> text=Crea e aggiungi'); pg.wait_for_timeout(300)
    st = json.loads(pg.evaluate("()=>localStorage.getItem('tva-atlante-v2')")); cols = list(st['col'].values())
    ok('Raccolta creata con la voce', len(cols) == 1 and cols[0]['n'] == 'Prova' and cols[0]['ids'] == [ids[0]], cols)
    pg.click('.a5-sheet >> text=Chiudi'); pg.wait_for_timeout(200)
    # tracker: stessa apertura, 10 s + scroll + 2 sezioni
    pg.evaluate("(i)=>window.tvaA3.open(i)", ids[1]); pg.wait_for_timeout(1800)
    for _ in range(6):
        pg.evaluate("()=>{const s=document.querySelector('#atlas2 .a2-scroll');s.scrollTop=s.scrollHeight}"); pg.wait_for_timeout(600)
        pg.evaluate("()=>{const s=document.querySelector('#atlas2 .a2-scroll');s.scrollTop=0}"); pg.wait_for_timeout(400)
    st = json.loads(pg.evaluate("()=>localStorage.getItem('tva-atlante-v2')"))
    ok('Prima dei 10 s il dossier NON è esplorato', ids[1] not in st['esp'], st['esp'])
    for _ in range(30):
        pg.evaluate("()=>{const s=document.querySelector('#atlas2 .a2-scroll');s.scrollTop+=260}"); pg.wait_for_timeout(300)
    st = json.loads(pg.evaluate("()=>localStorage.getItem('tva-atlante-v2')"))
    ok('Dopo 10 s + scroll + sezioni: esplorato una volta sola', ids[1] in st['esp'] and len(st['esp']) == 1, (st['esp'], pg.evaluate('()=>window.tvaA5.last&&window.tvaA5.last.metrics()'), pg.evaluate("()=>[document.querySelector('#atlas2 .a3-prog span')&&document.querySelector('#atlas2 .a3-prog span').textContent, document.querySelectorAll('#atlas2 .a3-ds').length, document.querySelector('#atlas2 .a2-scroll').scrollTop, document.querySelector('#atlas2 .a2-scroll').scrollHeight]")))
    # uscire dal dossier prima dei 10 s non conta
    pg.evaluate("(i)=>window.tvaA3.open(i)", ids[2]); pg.wait_for_timeout(2500); pg.evaluate("(i)=>window.tvaA3.open(i)", ids[3]); pg.wait_for_timeout(2500)
    st = json.loads(pg.evaluate("()=>localStorage.getItem('tva-atlante-v2')")); ok('Apertura breve: non conta', ids[2] not in st['esp'] and ids[3] not in st['esp'])
    # progressione
    go(pg, "()=>window.tvaA3.ctx().api.nav('a3',{a3:{v:'pr'}})", 1500)
    t = pg.inner_text('#atlas2')
    ok('Progressione: tetto, criterio e badge con stato', '/ 30 XP' in t and 'almeno 10 secondi' in t and 'Esploratore' in t, t[:300])  # con le voci db verificate nel registro anche i traguardi di registro diventano raggiungibili
    ok('Progressione: nessun overflow orizzontale', pg.evaluate("()=>{const s=document.querySelector('#atlas2 .a2-scroll');return s.scrollWidth<=s.clientWidth+1}"))
    go(pg, "()=>window.tvaA3.ctx().api.nav('a3',{a3:{v:'pf'}})", 1500)
    t = pg.inner_text('#atlas2'); ok('Preferiti e raccolte: elenco e raccolta', 'Preferiti (1)' in t and 'Prova' in t, t[:200])
    # dati esistenti intatti
    other1 = pg.evaluate("()=>Object.keys(localStorage).filter(k=>!k.startsWith('tva-atlante-v2')&&!k.startsWith('tva-a3')).sort().map(k=>[k,localStorage.getItem(k)])")
    keep = [x for x in other0 if not x[0].startswith('tva-a3')]
    changed = [k for k, v in keep if dict(other1).get(k) != v and not k.endswith('-ts') and 'last' not in k]
    ok('Nessuna chiave esistente riscritta dall\'Atlante A5', not [k for k in changed if k.startswith('marvel-ultimate-timeline')], changed[:5])
    # Tessera: XP con e senza chiave, accredito futuro non conta
    pg.close()
    base_ctx = b.new_context(viewport={'width': 390, 'height': 800}, is_mobile=True, service_workers='block'); pgx = base_ctx.new_page(); pgx.goto(U); pgx.wait_for_timeout(2500); xp0 = pgx.evaluate(XPJS); pgx.close()
    seed = "localStorage.setItem('tva-atlante-v2',JSON.stringify({v:1,fav:{},col:{},esp:{},ric:{},badge:{},xp:{'2000-01-01':30,'2000-01-02':30,'2999-01-01':30}}))"
    c2 = b.new_context(viewport={'width': 390, 'height': 800}, is_mobile=True, service_workers='block'); c2.add_init_script(seed); p2 = c2.new_page(); p2.goto(U); p2.wait_for_timeout(2500); xp1 = p2.evaluate(XPJS)
    ok('Tessera: +60 XP (due giorni accreditati), il giorno futuro non conta', xp0 is not None and xp1 == xp0 + 60, (xp0, xp1))
    c3 = b.new_context(viewport={'width': 390, 'height': 800}, is_mobile=True, service_workers='block'); c3.add_init_script("localStorage.setItem('tva-atlante-v2','{corrotto')"); p3 = c3.new_page(); p3.goto(U); p3.wait_for_timeout(2500)
    ok('Tessera: chiave corrotta → nessun errore, XP invariati', p3.evaluate(XPJS) == xp0)
    ok('Nessun errore di pagina', not errs, errs[:3])
    b.close()
f = [n for n, c in res if not c]; print('\n%d/%d' % (len(res) - len(f), len(res))); raise SystemExit(1 if f else 0)
