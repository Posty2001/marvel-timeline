"""Miss Minutes mm6.1 - hotfix scorrimento: risposta posizionata all'inizio, nessuno scorrimento forzato, freccia verso il fondo, persistenza. Gateway simulato.
Uso: python3 miss-minutes/tests/ui_mm61_test.py"""
import functools, http.server, json, os, socketserver, threading
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(H, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
res = []
def ok(n, c, x=''): res.append((n, bool(c))); print('PASS' if c else 'FAIL', n, x)
GW = {'chat': 0, 'mode': 'ok'}
def gw(route):
    r = route.request; u = r.url.split('workers.dev')[1]
    h = {'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*'}
    if r.method == 'OPTIONS': return route.fulfill(status=204, headers=h)
    if u.startswith('/v1/challenge'): return route.fulfill(status=200, headers=h, content_type='application/json', body=json.dumps({'salt': 'abc', 'ts': 1, 'bits': 1, 'sig': 'x'}))
    if u.startswith('/v1/session'): return route.fulfill(status=200, headers=h, content_type='application/json', body=json.dumps({'token': 'a.b.c', 'exp': 9999999999}))
    if u.startswith('/v1/chat'):
        GW['chat'] += 1
        if GW['mode'] == 'hang': return
        return route.fulfill(status=200, headers=h, content_type='application/json', body=json.dumps({'answer': '\n\n'.join('Paragrafo %d: ciò che è confermato, ciò che è ipotesi e le indiscrezioni sul tema richiesto, con dettagli sufficienti a occupare più righe sullo schermo.' % i for i in range(1, 15))}))
    route.fulfill(status=404, headers=h, body='{}')
CFG = "globalThis.MISS_MINUTES_CONFIG=Object.freeze({endpoint:'https://miss-minutes-api.test.workers.dev'});"
START = "()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route('**/*.workers.dev/**', gw); ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    def getframe():
        f = [f for f in pg.frames if 'miss-minutes' in f.url][0]; f.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000); return f
    pg.click('#mmFab'); fr = getframe(); pg.wait_for_timeout(400)
    M = "()=>{const c=document.getElementById('mmChat');const a=[...c.querySelectorAll('.mm-msg.assistant')].pop();const cr=c.getBoundingClientRect();const ar=a?a.getBoundingClientRect():null;const d=document.getElementById('mmDown');const dr=d.getBoundingClientRect();return {top:c.scrollTop,max:c.scrollHeight-c.clientHeight,ah:ar?ar.top-cr.top:null,down:!d.hidden&&dr.width>0,dbot:dr.bottom,cbot:cr.bottom}}"
    def wait_done(): fr.wait_for_function("()=>!document.getElementById('mmSend').disabled", timeout=150000); pg.wait_for_timeout(500)
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.online=true;p.consent=true;window.__mm.store.save()}")
    # 1. prima domanda breve: nessuna freccia se non serve
    fr.evaluate("()=>{window.__mm.ask('Ciao');return 1}"); wait_done()
    s = fr.evaluate(M); ok('risposta breve: nessuna freccia', not s['down'], s)
    # 2. risposta lunga (AI online simulata)
    for i in range(3):
        GW['chat'] += 0
        fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", 'Confronta in modo teorico Doom e Thanos in Doomsday numero %d' % i); wait_done()
    s = fr.evaluate(M); print(s)
    ok('mm2.0-b: risposta lunga generata in streaming, seguita fino in fondo (nessun salto in cima alla risposta)', s['max'] - s['top'] < 6, s)
    ok('mm2.0-b: seguendo il testo non serve la freccia (nascosta)', not s['down'], s)
    # 3. lettura libera: nessuno spostamento forzato
    fr.evaluate("()=>{document.getElementById('mmChat').scrollTop-=300;return 1}"); pg.wait_for_timeout(900); t1 = fr.evaluate(M)['top']; pg.wait_for_timeout(900); t2 = fr.evaluate(M)['top']
    ok('nessuno scorrimento automatico durante la lettura', t1 == t2, (t1, t2))
    # 4. freccia: vai in fondo, poi sparisce
    fr.click('#mmDown'); pg.wait_for_timeout(900); s = fr.evaluate(M)
    ok('la freccia porta alla fine della conversazione', s['max'] - s['top'] <= 2, s); ok('la freccia sparisce in fondo', not s['down'], s)
    # 5. invio: mostra la domanda e l'indicatore (fondo), poi risposta dall'inizio
    GW['mode'] = 'hang'; fr.evaluate("()=>{window.__mm.ask('Confronta in modo teorico Doom e Thanos in Doomsday attesa');return 1}"); pg.wait_for_timeout(700)
    s = fr.evaluate(M); ok('all\'invio: domanda e indicatore visibili (fondo)', fr.locator('.mm-think').count() == 1 and s['max'] - s['top'] <= 3, s)
    fr.click('.stopmini'); pg.wait_for_timeout(600); GW['mode'] = 'ok'
    # 6. persistenza dello scorrimento (mm6): ricaricamento pagina
    fr.evaluate("()=>{const c=document.getElementById('mmChat');c.scrollTop=Math.max(0,c.scrollHeight-c.clientHeight-400);return 1}"); pg.wait_for_timeout(700); t0 = fr.evaluate(M)['top']
    pg.reload(wait_until='load'); pg.wait_for_timeout(1500); pg.evaluate(START); pg.wait_for_timeout(600)
    if pg.locator('#mmOverlay.on').count() == 0: pg.click('#mmFab')
    fr = getframe(); pg.wait_for_timeout(900); s = fr.evaluate(M)
    ok('scorrimento ripristinato dopo il ricaricamento', abs(s['top'] - t0) < 30, (t0, s))
    ok('nessun errore JS', not errs, errs)
    b.close()
bad = [n for n, c in res if not c]; print('mm61_ui_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
