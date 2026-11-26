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
        if GW['mode'] == 'hang': return
        if GW['mode'] == 'p503': return route.fulfill(status=502, headers=h, content_type='application/json', body=json.dumps({'error': 'provider', 'upstream': {'http': 503, 'status': 'UNAVAILABLE', 'message': 'overloaded'}}))
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
    def view(): return frame.evaluate("()=>window.__mm.view()")
    def go_home():
        frame.evaluate("()=>window.__mm.go('home')"); pg.wait_for_timeout(150)
    def to_set():
        go_home(); frame.click('#mmSet'); pg.wait_for_timeout(300)
    def wait_idle(): pg.wait_for_timeout(100); frame.wait_for_function("()=>!document.getElementById('mmSend').disabled", timeout=20000); pg.wait_for_timeout(400)
    def last_ai(): return frame.evaluate("()=>{const m=[...document.querySelectorAll('.mm-msg.assistant')];return m.length?m[m.length-1].innerText:''}")
    def nuser(t): return frame.evaluate("(t)=>[...document.querySelectorAll('.mm-msg.user')].filter(x=>x.textContent===t).length", t)
    # schermata iniziale reale (mascotte disegnata, non immagine statica)
    go_home()
    ok('home: mascotte olografica SVG animata', frame.locator('#mmMascot svg .holo-float').count() == 1 and frame.locator('#mmMascot img').count() == 0)
    ok('home: saluto + onda + 4 temi', 'Agente' in frame.inner_text('#mmGreet') and frame.locator('#mmWave i').count() > 10 and frame.locator('.mm-topic').count() == 4)
    frame.locator('.mm-topic > button').first.click(); pg.wait_for_timeout(250)
    ok('home: accordion apre le domande suggerite', frame.locator('.mm-topic[data-open=true] li button').count() >= 3)
    ok('nessuna emoji nell\'interfaccia', frame.evaluate("()=>!/\\p{Extended_Pictographic}/u.test(document.body.innerText)"))
    # cronologia
    frame.click('#navHist'); pg.wait_for_timeout(300)
    ok('cronologia: righe e gruppo Oggi', frame.locator('.mm-row').count() >= 1 and 'Oggi' in frame.inner_text('#mmHistList'))
    frame.fill('#mmSearch', 'zzzzqq'); pg.wait_for_timeout(200); ok('cronologia: ricerca senza risultati', 'Nessuna conversazione trovata' in frame.inner_text('#mmHistList'))
    frame.fill('#mmSearch', 'loki'); pg.wait_for_timeout(200); ok('cronologia: ricerca nel contenuto', frame.locator('.mm-row').count() >= 1)
    frame.fill('#mmSearch', '')
    frame.locator('.mm-row [aria-label="Rinomina conversazione"]').first.click(); frame.fill('.mm-row input.ren', 'Titolo di prova'); frame.press('.mm-row input.ren', 'Enter'); pg.wait_for_timeout(250)
    ok('cronologia: rinomina', 'Titolo di prova' in frame.inner_text('#mmHistList'))
    saved = pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')"); ok('cronologia salvata in locale', saved and 'Loki' in saved and 'Titolo di prova' in saved)
    frame.locator('.mm-row >> text=Titolo di prova').first.click(); pg.wait_for_timeout(300); ok('cronologia: apre la conversazione', view() == 'chat' and frame.locator('.mm-msg').count() >= 2)
    # impostazioni
    to_set()
    ok('impostazioni: tutti i controlli', all(frame.locator('#set-' + k).count() == 1 for k in ['online', 'local', 'memory', 'voice', 'cite', 'spoiler']) and frame.locator('.seg button').count() == 3)
    frame.locator('.seg button >> text=Brevi').click(); pg.wait_for_timeout(200)
    ok('impostazioni: lunghezza salvata', '"length":"short"' in pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')").replace(' ', ''))
    frame.locator('.seg button >> text=Medie').click()
    frame.locator('#set-online').click(force=True); pg.wait_for_timeout(300)
    ok('AI online non attivabile senza gateway', not frame.locator('#set-online').is_checked())
    frame.locator('.mm-srow >> text=Diagnostica').click(); pg.wait_for_timeout(250)
    frame.fill('#set-endpoint', 'https://evil.example.com'); frame.click('#mmDlgBody >> text=Salva'); pg.wait_for_timeout(300)
    ok('endpoint non workers.dev rifiutato', 'non valido' in frame.inner_text('#mmDlgBody') and not (pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-miss-minutes-v1')") or '').count('evil'))
    frame.fill('#set-endpoint', 'https://miss-minutes-api.test.workers.dev'); frame.click('#mmDlgBody >> text=Salva'); pg.wait_for_timeout(800)
    ok('endpoint valido salvato e verificato', 'raggiungibile' in frame.inner_text('#mmDlgBody') and any(c[1].startswith('/v1/health') for c in GW['calls']), frame.inner_text('#mmDlgBody')[-120:])
    frame.fill('#set-endpoint', ''); frame.click('#mmDlgBody >> text=Salva'); GW['calls'].clear(); frame.click('#mmDlgClose')
    # duplicazioni: i marcatori non sostituiscono mai le parole
    rr = frame.evaluate("()=>{const c=[{id:'kc:loki',title:'Loki'}];const f=t=>window.__mm.resolveRefs(t,c).text;return [f('Il potere di [[kc:loki]] è enorme.'),f('Venom [[kc:loki]] è un simbionte.'),f('Nella continuità dei fumetti Gorr [[kc:loki]] colpisce.')]}")
    ok('marcatori: titolo solo dopo parola funzione, mai duplicato', rr == ['Il potere di Loki è enorme.', 'Venom è un simbionte.', 'Nella continuità dei fumetti Gorr colpisce.'], rr)
    # con endpoint configurato: riavvia il frame con config simulata
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body="globalThis.MISS_MINUTES_CONFIG=Object.freeze({endpoint:'https://miss-minutes-api.test.workers.dev'});"))
    pg.reload(wait_until='load'); pg.wait_for_timeout(1200); pg.evaluate(START); pg.wait_for_timeout(500); (pg.click('#mmFab') if pg.locator('#mmOverlay.on').count() == 0 else None); pg.wait_for_timeout(2000)
    frame = [f for f in pg.frames if 'miss-minutes' in f.url][0]; frame.wait_for_function("()=>window.__mm&&window.__mm.engine")
    to_set(); frame.locator('#set-online').click(force=True); pg.wait_for_timeout(400)
    ok('consenso richiesto prima dell\'attivazione', 'Attivare l’AI online' in frame.inner_text('#mmDlgBody') and 'Non vengono inviati titoli visti' in frame.inner_text('#mmDlgBody'))
    frame.click('text=No, solo locale'); go_home(); a = ask('xyzzy quuxlore'); ok('rifiuto consenso: nessuna chiamata rete', len(GW['calls']) == 0)
    to_set(); frame.locator('#set-online').click(force=True); pg.wait_for_timeout(300); frame.click('text=Acconsento e attivo'); pg.wait_for_timeout(300); go_home()
    a = ask('Perché il tempo si ramifica zzyx?', 1500)
    ok('domanda sconosciuta -> online etichettata', frame.evaluate("()=>[...document.querySelectorAll('.mm-tag')].some(t=>/online/.test(t.textContent))"), a[:80])
    a = ask('Chi è Loki?'); n0 = nuser('Chi è Loki?'); frame.locator('.mm-act', has_text='AI online').last.click(); wait_idle()
    a = last_ai()
    ok('URL dalla risposta AI rimossi, id scheda risolto in titolo e chip', 'evil.example' not in a and 'Loki' in a and 'online' in a and frame.locator('.mm-msg.assistant').last.locator('.mm-chip').count() == 1, a)
    ok('nessuna domanda duplicata dopo "Chiedi all\'AI online"', nuser('Chi è Loki?') == n0, (n0, nuser('Chi è Loki?')))
    chat = [c for c in GW['calls'] if c[1].startswith('/v1/chat')][-1][2]; body = json.loads(chat)
    ok('payload senza dati personali', all(k in ('question', 'history', 'context', 'spoiler', 'length', 'cite', 'stream') for k in body) and body.get('length') == 'normal' and body.get('cite') is True and 'seen' not in chat and 'rating' not in chat and 'titoli su 138' not in chat and 'quanti titoli' not in chat.lower() and 'cosa guardo' not in chat.lower(), list(body))
    n = len(GW['calls']); a = ask('Quanti titoli ho visto?'); ok('domanda personale mai inviata online', len(GW['calls']) == n)
    # anomalie: pannello, Riprova, archivio locale
    q = 'zxcv qwerty sconosciuto lorem'
    GW['mode'] = 'quota'; frame.fill('#mmQ', q); frame.click('#mmSend'); wait_idle()
    ok('quota esaurita: pannello anomalia con Riprova', frame.locator('.mm-state.err').count() == 1 and 'Energia temporale' in frame.inner_text('.mm-state.err') and frame.locator('.mm-state.err >> text=Riprova').count() == 1)
    ok('anomalia: nessun dettaglio tecnico nella chat', not any(w in frame.inner_text('#mmChat') for w in ['HTTP', '429', 'provider', 'stage']))
    GW['mode'] = 'p503'; frame.locator('.mm-state.err >> text=Riprova').click(); wait_idle()
    ok('503 del provider: anomalia temporanea, domanda non duplicata', 'Anomalia temporanea' in frame.inner_text('.mm-state.err') and nuser(q) == 1, nuser(q))
    d = frame.evaluate("()=>window.__mm.diag()"); ok('diagnostica: 2 tentativi per errore transitorio', d and d['attempts'] == 2 and not d['ok'], d)
    GW['mode'] = 'ok'; frame.locator('.mm-state.err >> text=Riprova').click(); wait_idle()
    ok('Riprova: risposta online, nessun pannello, domanda unica', frame.locator('.mm-state').count() == 0 and nuser(q) == 1 and 'online' in frame.evaluate("()=>[...document.querySelectorAll('.mm-tag')].pop().textContent"))
    q2 = q + ' due'; GW['mode'] = 'quota'; frame.fill('#mmQ', q2); frame.click('#mmSend'); wait_idle()
    frame.locator('.mm-state.err >> text=Consulta l’archivio locale').click(); wait_idle()
    ok('archivio locale dopo anomalia', frame.locator('.mm-state').count() == 0 and 'locale' in frame.evaluate("()=>[...document.querySelectorAll('.mm-tag')].pop().textContent") and nuser(q2) == 1)
    GW['mode'] = 'hang'; frame.fill('#mmQ', q2 + ' tre'); frame.click('#mmSend'); pg.wait_for_timeout(800)
    ok('attesa compatta nella chat: messaggi precedenti visibili, nessun pannello invasivo', frame.locator('.mm-think').count() == 1 and frame.locator('.mm-state.wait').count() == 0 and frame.locator('.mm-msg').count() >= 3 and frame.locator('.mm-msg').first.is_visible() or frame.locator('.mm-msg.user').last.is_visible())
    ok('attesa: senza percentuali né passi simulati, Interrompi nella barra e nella chat', '%' not in frame.inner_text('.mm-think') and frame.locator('.mm-think .mm-bar-ind').count() == 1 and frame.locator('#mmStop').is_visible() and not frame.locator('#mmSend').is_visible() and frame.locator('.mm-think >> text=Interrompi').is_visible())
    frame.click('#mmStop'); wait_idle()
    ok('attesa interrompibile', frame.locator('.mm-think').count() == 0 and 'interrotta' in frame.inner_text('#mmBanner').lower() and frame.locator('#mmSend').is_visible() and nuser(q2 + ' tre') == 1)
    GW['mode'] = 'ok'
    # rigenera
    frame.locator('button[aria-label="Rigenera la risposta"]').last.click() if frame.locator('button[aria-label="Rigenera la risposta"]').count() else None
    wait_idle(); ok('rigenera non duplica la domanda', nuser(q2 + ' tre') == 1)
    ok('copia e ascolto presenti', frame.locator('button[aria-label="Copia la risposta"]').count() >= 1 and frame.locator('button[aria-label="Ascolta la risposta"]').count() >= 1)
    # seguiti locali con memoria delle entità
    frame.evaluate("()=>{window.__mm.store.state.prefs.online=false}"); ask('Chi è Thor?'); a = ask('e Loki?'); a2 = ask('confrontali'); ok('seguito locale: confronto sulle ultime due entità', 'Thor' in a2 and 'Loki' in a2, a2[:140])
    go_home()
    # chiusura
    frame.click('#mmClose'); pg.wait_for_timeout(300); ok('chiusura da pulsante', pg.locator('#mmOverlay.on').count() == 0)
    ok('nessun errore JS pagina', not errs, errs[:3])
    b.close()
bad = [n for n, c in res if not c]; print('mm_ui_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
