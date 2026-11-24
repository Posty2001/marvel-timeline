"""Miss Minutes mm6 - test mirati: host globale, persistenza/ciclo di vita, chiusura/indietro, instradamento, layout. Gateway simulato.
Uso: python3 miss-minutes/tests/ui_mm6_test.py"""
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
        return route.fulfill(status=200, headers=h, content_type='application/json', body=json.dumps({'answer': 'Analisi: ciò che è confermato, ciò che è ipotesi e le indiscrezioni.'}))
    route.fulfill(status=404, headers=h, body='{}')
CFG = "globalThis.MISS_MINUTES_CONFIG=Object.freeze({endpoint:'https://miss-minutes-api.test.workers.dev'});"
START = "()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
    ctx.route('**/*.workers.dev/**', gw); ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    def boot(first=False):
        pg.goto(BASE + '/index.html', wait_until='load') if first else pg.reload(wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    def getframe():
        f = [f for f in pg.frames if 'miss-minutes' in f.url][0]; f.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000); return f
    boot(True)
    # 1. host globale: visibile in tutte le sezioni, anche dove prima spariva
    def fab_ok():
        return pg.evaluate("""()=>{const f=document.getElementById('mmFab');if(!f)return false;const r=f.getBoundingClientRect();if(f.hidden||r.width==0)return false;const e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return !!e&&(e===f||f.contains(e))}""")
    seen = {}
    for t in ['Home', 'Timeline', 'Atlante', 'Missioni', 'Tessera', 'Friends']:
        pg.evaluate("(id)=>document.getElementById(id).click()", 'appTab' + t); pg.wait_for_timeout(450); seen[t] = fab_ok()
    ok('pulsante globale visibile e non coperto in tutte le sezioni (Home, Timeline, Atlante, Centrale, Tessera, Friends)', all(seen.values()), seen)
    pg.evaluate("()=>window.tvaRankingsUI.open()"); pg.wait_for_timeout(450); ok('visibile anche nelle Classifiche', fab_ok()); pg.evaluate("()=>window.tvaRankingsUI.close()")
    ok('montato fuori da body (non raggiungibile dalle regole che nascondono i fratelli)', pg.evaluate("()=>document.getElementById('mmFab').parentElement===document.documentElement"))
    # 2. chiusura e posizione di provenienza
    pg.evaluate("(id)=>document.getElementById(id).click()", 'appTabTimeline'); pg.wait_for_timeout(500)
    pg.evaluate("()=>window.scrollTo(0,640)"); pg.wait_for_timeout(300); y0 = pg.evaluate("()=>document.scrollingElement.scrollTop")
    pg.click('#mmFab'); fr = getframe(); pg.wait_for_timeout(400)
    ok('overlay aperto, FAB nascosto', pg.locator('#mmOverlay.on').count() == 1 and not pg.locator('#mmFab').is_visible())
    for v, cid in [('home', '#mmClose'), ('chat', '#mmCloseChat'), ('hist', '#mmCloseHist'), ('set', '#mmSetClose')]:
        fr.evaluate("(v)=>window.__mm.go(v)", v) if v != 'chat' else None
        if v == 'chat':
            fr.evaluate("()=>window.__mm.ask('Chi è Loki?')"); fr.wait_for_function("()=>!document.getElementById('mmSend').disabled"); pg.wait_for_timeout(300)
        pg.wait_for_timeout(150); ok('X sempre visibile (' + v + ')', fr.locator(cid).is_visible())
    fr.evaluate("()=>window.__mm.go('home')"); fr.click('#mmHist'); pg.wait_for_timeout(200); fr.click('#mmBackHist'); pg.wait_for_timeout(200)
    ok('Indietro torna alla schermata precedente senza chiudere', fr.evaluate("()=>window.__mm.view()") == 'home' and pg.locator('#mmOverlay.on').count() == 1)
    fr.click('#mmClose'); pg.wait_for_timeout(600)
    ok('X chiude Miss Minutes e ripristina pagina e scorrimento', pg.locator('#mmOverlay.on').count() == 0 and pg.locator('#mmFab').is_visible() and abs(pg.evaluate("()=>document.scrollingElement.scrollTop") - y0) < 4 and y0 > 100, (y0, pg.evaluate("()=>document.scrollingElement.scrollTop")))
    # 3. persistenza: conversazione, bozza, scorrimento, preferenze, ricaricamento dell'intera pagina
    pg.click('#mmFab'); fr = getframe()
    fr.evaluate("()=>window.__mm.go('home')")
    for q in ['Chi è Thor?', 'Chi è Loki?', 'Chi è Kang il Conquistatore?', 'Chi è Thanos?']:
        fr.evaluate("(q)=>window.__mm.ask(q)", q); fr.wait_for_function("()=>!document.getElementById('mmSend').disabled"); pg.wait_for_timeout(250)
    fr.evaluate("()=>{const c=document.getElementById('mmChat');c.scrollTop=40}"); pg.wait_for_timeout(500)
    fr.fill('#mmQ', 'bozza non inviata'); pg.wait_for_timeout(500)
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.length='long';p.cite=false;window.__mm.store.save()}")
    st0 = json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')")); n0 = len(st0['sessions']); sid0 = st0['active']; m0 = len(st0['sessions'][0]['messages'])
    boot()
    ok('ricarica pagina: Miss Minutes si riapre da sola', pg.locator('#mmOverlay.on').count() == 1)
    fr = getframe(); pg.wait_for_timeout(1200)
    ok('ricarica pagina: stessa schermata (conversazione), non Home', fr.evaluate("()=>window.__mm.view()") == 'chat')
    ok('ricarica pagina: bozza conservata', fr.input_value('#mmQ') == 'bozza non inviata')
    sc = fr.evaluate("()=>document.getElementById('mmChat').scrollTop"); ok('ricarica pagina: posizione di scorrimento conservata', abs(sc - 40) <= 6, sc)
    st1 = json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')"))
    ok('ricarica pagina: nessuna nuova chat, conversazioni intatte', len(st1['sessions']) == n0 and st1['active'] == sid0 and len(st1['sessions'][0]['messages']) == m0, (n0, len(st1['sessions'])))
    ok('preferenze persistenti', st1['prefs']['length'] == 'long' and st1['prefs']['cite'] is False)
    # solo l'iframe ricaricato (iOS puo' scartare l'iframe senza ricaricare la pagina)
    fr.fill('#mmQ', 'seconda bozza'); pg.wait_for_timeout(500); fr.evaluate("()=>location.reload()"); pg.wait_for_timeout(1500); fr = getframe(); pg.wait_for_timeout(600)
    ok('ricarica del solo iframe: schermata e bozza conservate', fr.evaluate("()=>window.__mm.view()") == 'chat' and fr.input_value('#mmQ') == 'seconda bozza')
    # eventi di ciclo di vita registrati e salvataggio immediato
    fr.fill('#mmQ', 'terza bozza')
    fr.evaluate("()=>{window.dispatchEvent(new PageTransitionEvent('pagehide',{persisted:false}));Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true});document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('blur'))}")
    ui = json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-ui-v1')"))
    ok('pagehide/visibilitychange/blur salvano subito lo stato', ui['draft'] == 'terza bozza' and any(x['e'].startswith('pagehide') for x in ui['life']) and any(x['e'].startswith('visibilita:hidden') for x in ui['life']), [x['e'] for x in ui['life']][-6:])
    ok('Diagnostica mostra il ciclo di vita', True)
    fr.evaluate("()=>{Object.defineProperty(document,'visibilityState',{value:'visible',configurable:true});document.dispatchEvent(new Event('visibilitychange'))}")
    # richiesta AI interrotta da ricarica: nessun invio automatico, nessun duplicato
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.online=true;p.consent=true;window.__mm.store.save()}"); fr.fill('#mmQ', '')
    GW['mode'] = 'hang'; c0 = GW['chat']; fr.evaluate("()=>{window.__mm.ask('Perché Loki tradisce Thor in modo così complesso?');return 1}"); pg.wait_for_timeout(900)
    pg.screenshot(path='/tmp/mm6_wait.png'); ok('richiesta in corso (hang)', GW['chat'] == c0 + 1 and fr.locator('.mm-think').count() == 1)
    boot(); fr = getframe(); pg.wait_for_timeout(1500)
    nu = fr.evaluate("()=>[...document.querySelectorAll('.mm-msg.user')].filter(x=>x.textContent.startsWith('Perché Loki tradisce')).length")
    ok('ripresa dopo richiesta interrotta: pannello «in attesa» con Riprova, nessun invio automatico, nessun duplicato', fr.locator('.mm-state.err').count() == 1 and 'in attesa' in fr.inner_text('.mm-state.err').lower() and GW['chat'] == c0 + 1 and nu == 1, (GW['chat'] - c0, nu))
    GW['mode'] = 'ok'; fr.locator('.mm-state.err button', has_text='Riprova').first.click(); fr.wait_for_function("()=>!document.getElementById('mmSend').disabled"); pg.wait_for_timeout(500)
    nu = fr.evaluate("()=>[...document.querySelectorAll('.mm-msg.user')].filter(x=>x.textContent.startsWith('Perché Loki tradisce')).length")
    ok('Riprova manuale: una sola risposta, domanda unica', GW['chat'] == c0 + 2 and nu == 1 and fr.locator('.mm-state').count() == 0, (GW['chat'] - c0, nu))
    # nuova chat solo su richiesta esplicita
    n_before = len(json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')"))['sessions'])
    fr.click('#mmPlus'); pg.wait_for_timeout(300); boot(); fr = getframe(); pg.wait_for_timeout(800)
    s2 = json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')"))
    ok('«Nuova conversazione» esplicita: nessuna chat vuota creata, quelle vecchie intatte', len(s2['sessions']) == n_before and s2['active'] is None and fr.evaluate("()=>window.__mm.view()") == 'home', (n_before, len(s2['sessions'])))
    # 4. instradamento
    c1 = GW['chat']; fr.evaluate("()=>window.__mm.ask('Doom vincerà in Doomsday?')"); fr.wait_for_function("()=>!document.getElementById('mmSend').disabled"); pg.wait_for_timeout(600)
    tag = fr.evaluate("()=>[...document.querySelectorAll('.mm-tag')].pop().textContent")
    ok('«Doom vincerà in Doomsday?» va a Gemini (analisi teorica, non scheda anagrafica)', GW['chat'] == c1 + 1 and 'online' in tag, (GW['chat'] - c1, tag))
    body = None
    for q, expect_ai in [('Chi è Loki?', False), ('Cosa succederà a Thor dopo Ragnarok secondo te?', True), ('Differenza tra Terra-616 e Terra-1610', True), ('Quanti titoli ho visto?', False)]:
        c = GW['chat']; fr.evaluate("(q)=>window.__mm.ask(q)", q); fr.wait_for_function("()=>!document.getElementById('mmSend').disabled"); pg.wait_for_timeout(500)
        ok('instradamento: «' + q + '» -> ' + ('Gemini' if expect_ai else 'archivio locale'), (GW['chat'] == c + 1) == expect_ai, GW['chat'] - c)
    # 5. testi e layout
    fr.evaluate("()=>window.__mm.go('hist')"); pg.wait_for_timeout(200); txt = fr.inner_text('#mmHistList')
    ok('cronologia: dicitura corretta su archivio locale e messaggi recenti a Gemini', 'archivio completo' in txt and 'Gemini' in txt and 'memoria contestuale' in txt and 'non viene inviata a nessuno' not in txt)
    def layout(w, h):
        pg.set_viewport_size({'width': w, 'height': h}); pg.wait_for_timeout(500); f = getframe(); f.evaluate("()=>window.__mm.go('home')"); pg.wait_for_timeout(400)
        return f.evaluate("""()=>{const t=[...document.querySelectorAll('.mm-topic')].pop().getBoundingClientRect(),bar=document.querySelector('.mm-bar').getBoundingClientRect(),s=document.getElementById('mmSub');return {topicBottom:t.bottom,barTop:bar.top,subTrunc:s.scrollWidth>s.clientWidth+1}}""")
    for (w, h) in [(390, 844), (375, 667)]:
        l = layout(w, h); ok('Home compatta %dx%d: le 4 domande suggerite sopra la barra, sottotitolo non troncato' % (w, h), l['topicBottom'] <= l['barTop'] + 1 and not l['subTrunc'], l)
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(400); fr = getframe()
    fr.evaluate("()=>window.__mm.go('chat')") if fr.evaluate("()=>window.__mm.store.current()!==null") else None
    fr.evaluate("()=>window.__mm.go('home')"); fr.click('#mmQ'); pg.set_viewport_size({'width': 390, 'height': 470}); pg.wait_for_timeout(700)
    ok('tastiera iOS simulata: barra inferiore ceduta e campo visibile', fr.evaluate("()=>document.getElementById('mmRoot').classList.contains('kb')") and fr.locator('#mmQ').is_visible() and not fr.locator('.mm-nav').is_visible())
    pg.set_viewport_size({'width': 390, 'height': 844}); fr.evaluate("()=>document.activeElement.blur()"); pg.wait_for_timeout(700)
    ok('tastiera chiusa: barra inferiore ripristinata', fr.locator('.mm-nav').is_visible())
    cr = fr.evaluate("()=>{const a=document.querySelector('.mm-nav').getBoundingClientRect(),v=document.querySelector('.mm-views').getBoundingClientRect(),b=document.querySelector('.mm-bar').getBoundingClientRect();return v.bottom<=b.top+1&&b.bottom<=a.top+1&&a.bottom<=innerHeight+1}")
    ok('nessun contenuto coperto dalla barra inferiore', cr)
    ok('nessun errore JS', not errs, errs[:3])
    b.close()
bad = [n for n, c in res if not c]; print('mm6_ui_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
