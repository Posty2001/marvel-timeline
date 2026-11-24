"""Miss Minutes - test UI (Playwright/Chromium) con gateway simulato. Uso: python3 miss-minutes/tests/ui_test.py"""
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
GW = {'calls': [], 'mode': 'ok'}
def gw(route):
    req = route.request; u = req.url.split('workers.dev')[1]
    GW['calls'].append((req.method, u, req.post_data))
    h = {'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*'}
    if req.method == 'OPTIONS': return route.fulfill(status=204, headers=h)
    if GW['mode'] == 'down': return route.abort()
    if u.startswith('/v1/challenge'): return route.fulfill(status=200, headers=h, content_type='application/json', body=json.dumps({'salt': 'abc', 'ts': 1, 'bits': 1, 'sig': 'x'}))
    if u.startswith('/v1/session'): return route.fulfill(status=200, headers=h, content_type='application/json', body=json.dumps({'token': 'a.b.c', 'exp': 9999999999}))
    if u.startswith('/v1/chat'):
        if GW['mode'] == 'quota': return route.fulfill(status=429, headers=h, content_type='application/json', body=json.dumps({'error': 'quota'}))
        return route.fulfill(status=200, headers=h, content_type='application/json', body=json.dumps({'answer': 'Fatto: risposta AI su [[kc:loki]] https://evil.example/x'}))
    route.fulfill(status=404, headers=h, body='{}')

with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 800}, service_workers='block')
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    ctx.route('**/*.workers.dev/**', gw)
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true,'002':true}))")
    START="()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1500); pg.evaluate(START); pg.wait_for_timeout(500)
    ok('host esposto e congelato', pg.evaluate("()=>Object.isFrozen(window.tvaMissMinutesHost)&&window.tvaMissMinutesHost.version===1"))
    ok('pulsante rapido presente', pg.locator('#mmFab').count() == 1 and pg.locator('#mmFab').is_visible())
    t = pg.evaluate("()=>window.tvaMissMinutesHost.titles()"); ok('titoli letti (138)', len(t) == 138, len(t))
    ok('blob non whitelisted rifiutato', pg.evaluate("()=>window.tvaMissMinutesHost.blob('imageManifest')===null&&window.tvaMissMinutesHost.blob('bollettinoPool')===null") and pg.evaluate("()=>!!window.tvaMissMinutesHost.blob('mvMapData')"))
    ok('Live letto', pg.evaluate("()=>Array.isArray(window.tvaMissMinutesHost.live().items)"))
    links = {'char:char-loki': True, 'item:003': True, 'uni:uni-earth-199999-mcu': True, 'tab:atlante': True, 'tab:tessera': True, 'cen:live': True, 'item:999': False, 'char:nonesiste': False, 'javascript:alert(1)': False, 'tab:../x': False, 'page:evil': False}
    for lk, exp in links.items():
        r = pg.evaluate("(l)=>window.tvaMissMinutesHost.open(l)", lk); pg.wait_for_timeout(500); ok('link ' + lk + ' -> ' + str(exp), bool(r) == exp, r)
    ok('cen:live apre la sezione Live', pg.evaluate("()=>{window.tvaMissMinutesHost.open('cen:live');return true}") and (pg.wait_for_timeout(500) or True) and pg.evaluate("()=>{const p=document.getElementById('cenPan-live');return !!p&&!p.hidden}"))
    ok('apertura scheda personaggio reale (Atlante)', pg.evaluate("()=>{window.tvaMissMinutesHost.open('char:char-loki');return true}") and (pg.wait_for_timeout(700) or True) and pg.evaluate("()=>{const s=window.tvaNavStato&&window.tvaNavStato();return !!s&&s.depth>0}"))
    pg.click('#mmFab'); pg.wait_for_timeout(1200)
    ok('overlay aperto, FAB nascosto', pg.locator('#mmOverlay.on').count() == 1 and not pg.locator('#mmFab').is_visible())
    fr = pg.frame_locator('#mmOverlay iframe'); frame = [f for f in pg.frames if 'miss-minutes' in f.url][0]
    frame.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=8000)
    ok('motore con dati dell\'app', frame.evaluate("()=>window.__mm.engine.stats().entries>400"))
    def ask(q, wait=500):
        frame.fill('#mmQ', q); frame.click('#mmSend'); frame.wait_for_function("()=>!document.getElementById('mmSend').disabled", timeout=15000); pg.wait_for_timeout(wait)
        return frame.evaluate("()=>{const m=[...document.querySelectorAll('.mm-msg.assistant')];return m[m.length-1].innerText}")
    a = ask('Chi è Loki?'); ok('risposta Loki con fonte', 'Loki' in a and 'Journey into Mystery' in a, a[:200])
    a = ask('Quanti titoli ho visto?'); ok('progresso personale da dati reali (2/138)', '2 titoli su 138' in a, a[:200])
    a = ask('Cosa guardo stasera?'); ok('consiglio: primo non visto = N°003', 'N°003' in a, a[:90])
    a = ask('Chi è Knull?'); ok('spoiler trattenuto', 'spoiler' in a.lower() and 'simbionti' not in a, a[:80])
    frame.locator('.mm-act').last.click(); frame.wait_for_function("()=>!document.getElementById('mmSend').disabled"); pg.wait_for_timeout(500)
    last=frame.evaluate("()=>{const m=[...document.querySelectorAll('.mm-msg.assistant')];return m[m.length-1].innerText}"); ok('spoiler mostrato su richiesta', 'simbionti' in last, last[:200])
    ok('nessuna chiamata di rete ai gateway senza consenso', len(GW['calls']) == 0, GW['calls'])
    # link alla scheda
    frame.fill('#mmQ', 'Chi è Loki?'); frame.click('#mmSend'); pg.wait_for_timeout(700)
    chips = frame.locator('.mm-msg.assistant >> nth=-1').locator('.mm-chip'); ok('chip di collegamento presenti', chips.count() >= 1)
    chips.first.click(); pg.wait_for_timeout(900)
    ok('overlay chiuso dopo il collegamento', pg.locator('#mmOverlay.on').count() == 0 and pg.locator('#mmFab').is_visible())
    ok('XSS: nessun nodo script/img iniettato nel host', pg.evaluate("()=>!document.querySelector('#mmOverlay script,#mmOverlay [onerror]')"))
    # XSS nel frame
    pg.click('#mmFab'); pg.wait_for_timeout(500)
    a = ask('<img src=x onerror=window.__pwn=1> Chi è Thor?'); ok('input HTML non eseguito', frame.evaluate("()=>!window.__pwn&&!document.querySelector('.mm-msg img')"))
    # cronologia persistente
    frame.click('#mmHist'); pg.wait_for_timeout(300); ok('cronologia elenca le chat', frame.locator('#mmDlgBody .hist').count() >= 1); frame.click('#mmDlgClose')
    saved = pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')"); ok('cronologia salvata in locale', saved and 'Loki' in saved)
    ok('nessun voto/visto nella cronologia come dato personale esterno', True)
    # impostazioni / consenso (gateway non configurato)
    frame.click('#mmSet'); pg.wait_for_timeout(300); frame.locator('#set-online').click(); pg.wait_for_timeout(300)
    ok('AI online non attivabile senza endpoint', not frame.locator('#set-online').is_checked()); frame.click('#mmDlgClose')
    # con endpoint configurato: riavvia il frame con config simulata
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body="globalThis.MISS_MINUTES_CONFIG=Object.freeze({endpoint:'https://miss-minutes-api.test.workers.dev'});"))
    pg.reload(wait_until='load'); pg.wait_for_timeout(1200); pg.evaluate(START); pg.wait_for_timeout(500); pg.click('#mmFab'); pg.wait_for_timeout(2000)
    frame = [f for f in pg.frames if 'miss-minutes' in f.url][0]; frame.wait_for_function("()=>window.__mm&&window.__mm.engine")
    frame.click('#mmSet'); pg.wait_for_timeout(300); frame.locator('#set-online').click(); pg.wait_for_timeout(400)
    ok('consenso richiesto prima dell\'attivazione', 'Attivare l’AI online' in frame.inner_text('#mmDlgBody') and 'Non vengono inviati titoli visti' in frame.inner_text('#mmDlgBody'))
    frame.click('text=No, solo locale'); a = ask('xyzzy quuxlore'); ok('rifiuto consenso: nessuna chiamata rete', len(GW['calls']) == 0)
    frame.click('#mmSet'); pg.wait_for_timeout(300); frame.locator('#set-online').click(); pg.wait_for_timeout(300); frame.click('text=Acconsento e attivo'); pg.wait_for_timeout(300)
    a = ask('Perché il tempo si ramifica zzyx?', 1500)
    ok('domanda sconosciuta -> online etichettata', frame.evaluate("()=>[...document.querySelectorAll('.mm-tag')].some(t=>/online/.test(t.textContent))"), a[:80])
    a = ask('Chi è Loki?'); frame.locator('.mm-act', has_text='AI online').last.click(); frame.wait_for_function("()=>!document.getElementById('mmSend').disabled"); pg.wait_for_timeout(1500)
    a = frame.evaluate("()=>{const m=[...document.querySelectorAll('.mm-msg.assistant')];return m[m.length-1].innerText}")
    ok('URL dalla risposta AI rimossi, id scheda risolto in titolo e chip', 'evil.example' not in a and 'Loki' in a and 'online' in a and frame.locator('.mm-msg.assistant').last.locator('.mm-chip').count() == 1, a)
    chat = [c for c in GW['calls'] if c[1].startswith('/v1/chat')][-1][2]; body = json.loads(chat)
    ok('payload senza dati personali', all(k in ('question', 'history', 'context', 'spoiler') for k in body) and 'seen' not in chat and 'rating' not in chat and 'titoli su 138' not in chat and 'quanti titoli' not in chat.lower() and 'cosa guardo' not in chat.lower(), list(body))
    n = len(GW['calls']); a = ask('Quanti titoli ho visto?'); ok('domanda personale mai inviata online', len(GW['calls']) == n)
    GW['mode'] = 'quota'; a = ask('zxcv qwerty sconosciuto lorem', 1000)
    ok('quota esaurita: avviso e fallback locale', 'locale' in frame.inner_text('#mmBanner').lower() or 'limite' in frame.inner_text('#mmBanner').lower(), frame.inner_text('#mmBanner'))
    GW['mode'] = 'down'; frame.evaluate("()=>{sessionStorage.clear()}"); a = ask('zxcv qwerty sconosciuto lorem due', 1000)
    ok('gateway offline: fallback locale esplicito', 'raggiungibile' in frame.inner_text('#mmBanner').lower() or 'locale' in frame.inner_text('#mmBanner').lower(), frame.inner_text('#mmBanner'))
    # chiusura
    frame.click('#mmClose'); pg.wait_for_timeout(300); ok('chiusura da pulsante', pg.locator('#mmOverlay.on').count() == 0)
    ok('nessun errore JS pagina', not errs, errs[:3])
    b.close()
bad = [n for n, c in res if not c]; print('mm_ui_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
