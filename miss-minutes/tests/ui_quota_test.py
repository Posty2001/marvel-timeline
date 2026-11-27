"""mm2e.2 - gestione quote in app (gateway simulato): messaggio con tipo/origine/orario, blocco locale senza richieste inutili, residuo, ripristino."""
import functools, http.server, json, os, socketserver, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(H, directory=ROOT)); srv.daemon_threads = True; threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
res = []
def ok(n, c, x=''): res.append((n, bool(c))); print('PASS' if c else 'FAIL', n, x)
GW = {'chat': 0, 'quota': 0, 'mode': 'ok', 'left': 37}
def gw(route):
    req = route.request; u = req.url.split('workers.dev')[1]
    h = {'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*'}
    if req.method == 'OPTIONS': return route.fulfill(status=204, headers=h)
    j = lambda st, o: route.fulfill(status=st, headers=h, content_type='application/json', body=json.dumps(o))
    if u.startswith('/v1/challenge'): return j(200, {'salt': 'abc', 'ts': 1, 'bits': 1, 'sig': 'x'})
    if u.startswith('/v1/session'): return j(200, {'token': 'a.b.c', 'exp': 9999999999})
    now = int(time.time())
    if u.startswith('/v1/quota'):
        GW['quota'] += 1; l = GW['left']
        return j(200, {'now': now, 'disponibili': l, 'limitante': 'dispositivo-giorno', 'ripristino': now + 3600, 'limiti': [{'scope': 'dispositivo-giorno', 'kind': 'giornaliero', 'limit': 100, 'used': 100 - l, 'remaining': l, 'resetAt': now + 3600}, {'scope': 'globale-giorno', 'kind': 'giornaliero', 'limit': 450, 'used': 10, 'remaining': 440, 'resetAt': now + 7200}]})
    if u.startswith('/v1/chat'):
        GW['chat'] += 1
        if GW['mode'] == 'dev': return j(429, {'error': 'quota', 'scope': 'dispositivo-giorno', 'kind': 'giornaliero', 'source': 'gateway', 'limit': 100, 'used': 100, 'resetAt': now + 3 * 3600, 'retryAfter': 3 * 3600})
        if GW['mode'] == 'goog': return j(429, {'error': 'provider-quota', 'source': 'gemini', 'kind': 'giornaliero', 'resetAt': now + 5 * 3600, 'retryAfter': 5 * 3600, 'upstream': {'http': 429, 'status': 'RESOURCE_EXHAUSTED', 'message': 'q'}})
        return j(200, {'answer': 'Risposta di prova.'})
    route.fulfill(status=404, headers=h, body='{}')

with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 800}, service_workers='block')
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    ctx.route('**/*.workers.dev/**', gw)
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body="globalThis.MISS_MINUTES_CONFIG=Object.freeze({endpoint:'https://miss-minutes-api.test.workers.dev'});"))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    START = "()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    pg.click('#mmFab'); pg.wait_for_timeout(800)
    fr = [f for f in pg.frames if 'miss-minutes' in f.url][0]; fr.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000)
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.online=true;p.consent=true;window.__mm.store.save();window.__mm.go('chat')}")
    Q = 'Perché il multiverso Marvel è così intricato zzyx?'
    def ask(q):
        fr.evaluate("(q)=>{window.__mm.ask(q,{forceOnline:true});return 1}", q); fr.wait_for_function("()=>!document.getElementById('mmSend').disabled", timeout=30000); fr.wait_for_timeout(500)
    def err_text(): return fr.evaluate("()=>{const e=document.querySelector('.mm-state.err');return e?e.innerText:''}")
    # 1) limite del dispositivo (gateway)
    GW['mode'] = 'dev'; ask(Q); t = err_text()
    ok('429 gateway: dice che è un limite di Miss Minutes (non di Google), quale e quanto vale', 'non di Google' in t and 'questo dispositivo' in t and '100 richieste' in t, t[:300])
    ok('429 gateway: orario di ripristino in ora italiana', 'ora italiana' in t and ('alle' in t), t[:300])
    ok('una sola richiesta inviata, nessun tentativo automatico', GW['chat'] == 1, GW['chat'])
    # 2) seconda domanda: blocco locale, nessuna richiesta di rete
    ask(Q + ' bis'); ok('limite noto: nessuna nuova richiesta al gateway', GW['chat'] == 1, GW['chat'])
    d = fr.evaluate("()=>window.__mm.diag()"); ok('diagnostica: tentativi 0, richiesta NON inviata, ambito e tipo', d and d['attempts'] == 0 and d.get('quota') and d['quota']['scope'] == 'dispositivo-giorno', d)
    dt = fr.evaluate("()=>window.__mm.diagText ? window.__mm.diagText() : ''")
    # 3) residuo nella diagnostica (non consuma) e rimozione del blocco
    fr.evaluate("()=>window.__mm.go('set')"); fr.wait_for_timeout(200)
    fr.evaluate("()=>{const b=[...document.querySelectorAll('button')].find(x=>/Diagnostica/.test(x.textContent));if(b)b.click()}"); fr.wait_for_timeout(500)
    fr.locator('button', has_text='Richieste disponibili').first.click(); fr.wait_for_timeout(700)
    body = fr.inner_text('#mmDlgBody')
    ok('residuo: numero di richieste disponibili e limite più stringente', 'Richieste disponibili ora: 37' in body and 'Questo dispositivo' in body and 'ora italiana' in body, body[:400])
    ok('residuo: la lettura non consuma richieste di chat', GW['chat'] == 1 and GW['quota'] >= 1)
    ok('residuo > 0: blocco locale rimosso', 'blocco locale è stato rimosso' in body)
    GW['mode'] = 'ok'; fr.evaluate("()=>window.__mm.go('chat')"); ask(Q + ' ter'); ok('dopo la rimozione del blocco la richiesta riparte', GW['chat'] == 2, GW['chat'])
    # 4) limite di Google distinto da quello del gateway
    fr.evaluate("()=>{try{localStorage.removeItem('marvel-ultimate-timeline-miss-minutes-quota')}catch(e){}}")
    GW['mode'] = 'goog'; ask(Q + ' quater'); t = err_text()
    ok('429 Google: dichiarato come limite di Google, quota giornaliera, ripristino', 'Limite di Google, non di Miss Minutes' in t and 'giornaliera' in t and 'ora italiana' in t, t[:300])
    ok('nessun tentativo automatico anche per Google', GW['chat'] == 3, GW['chat'])
    ok('nessun errore di pagina', not errs, errs[:2])
fails = [n for n, c in res if not c]; print('\n%d/%d' % (len(res) - len(fails), len(res))); raise SystemExit(1 if fails else 0)
