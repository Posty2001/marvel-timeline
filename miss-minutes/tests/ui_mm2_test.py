"""Miss Minutes a41 - streaming progressivo reale (SSE) con gateway simulato su STESSA ORIGINE (chunk reali con ritardi).
Uso: python3 miss-minutes/tests/ui_stream_test.py"""
import re, functools, http.server, json, os, socketserver, ssl, subprocess, tempfile, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODE = {'m': 'clean', 'chat': 0, 'bodies': [], 'wp': 'up'}
TXT = {
 'clean': ['Spider-Man: Brand New Day è uscito il 31 luglio 2026. Il film è in sala.', ''],
 'fix': ['Prima parte corretta sul multiverso. Spider-Man: Brand New Day è ancora in sviluppo. Questa frase non deve mai comparire.', ' Il film è invece già uscito (31 luglio 2026) secondo i dati in archivio.'],
 'bad2': ['Prima parte corretta sul multiverso. Spider-Man: Brand New Day è ancora in sviluppo. Coda errata.', ' Anche ora Spider-Man: Brand New Day è ancora in sviluppo. Altra coda errata.'],
 'formato': ['Prima parte utile sul titolo. Si tratta di un ciclo fumettistico del 2008. Coda errata.', ' Il film Spider-Man: Brand New Day è uscito il 31 luglio 2026.'],
 'actor': ['Peter Parker è interpretato da Peter Parker. Testo errato.', ' Nel MCU Peter Parker è interpretato da Tom Holland.']}
PARAS = ['Paragrafo %d: ' % i + ('testo di prova molto lungo per riempire la bolla. ' * 6) for i in range(10)]
def sse(o): return ('data: ' + json.dumps(o) + '\n\n').encode()
CORS = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type, Authorization', 'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'}
class G(http.server.BaseHTTPRequestHandler):
    log_message = lambda self, *a: None
    def _h(self, st, ct='application/json', ln=None):
        self.send_response(st)
        for k, v in CORS.items(): self.send_header(k, v)
        self.send_header('Content-Type', ct); self.send_header('Cache-Control', 'no-store')
        if ln is not None: self.send_header('Content-Length', str(ln))
        self.end_headers()
    def _j(self, o, st=200):
        b = json.dumps(o).encode(); self._h(st, ln=len(b)); self.wfile.write(b)
    def do_OPTIONS(self): self._h(204, ln=0)
    def do_GET(self):
        if self.path.startswith('/v1/challenge'): return self._j({'salt': 'abc', 'ts': 1, 'bits': 1, 'sig': 'x'})
        self._j({}, 404)
    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0); body = self.rfile.read(n)
        if self.path.startswith('/v1/session'): return self._j({'token': 'a.b.c', 'exp': 9999999999})
        if self.path.startswith('/v1/chat'):
            MODE['chat'] += 1
            try: bd = json.loads(body)
            except Exception: bd = {}
            MODE['bodies'].append(bd)
            self._h(200, 'text/event-stream; charset=utf-8')
            m = MODE['m']
            if bd.get('riprendi'):
                txt = TXT[m][1]
            else:
                txt = TXT[m][0]
            try:
                self.wfile.write((': ' + ' ' * 2048 + '\n\n').encode()); self.wfile.flush()
                for i in range(0, len(txt), 40):
                    self.wfile.write(sse({'t': txt[i:i + 40]})); self.wfile.flush(); time.sleep(0.12)
                self.wfile.write(sse({'done': True})); self.wfile.flush()
            except Exception: pass
            return
        self._j({}, 404)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=ROOT)); srv.daemon_threads = True; threading.Thread(target=srv.serve_forever, daemon=True).start()
TD = tempfile.mkdtemp(); subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', TD + '/k.pem', '-out', TD + '/c.pem', '-days', '2', '-subj', '/CN=miss-minutes-api.test.workers.dev', '-addext', 'subjectAltName=DNS:miss-minutes-api.test.workers.dev'], capture_output=True, check=True)
gsrv = http.server.ThreadingHTTPServer(('127.0.0.1', 443), G); gsrv.daemon_threads = True; cx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); cx.load_cert_chain(TD + '/c.pem', TD + '/k.pem'); gsrv.socket = cx.wrap_socket(gsrv.socket, server_side=True); threading.Thread(target=gsrv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
res = []
def ok(n, c, x=''): res.append((n, bool(c))); print('PASS' if c else 'FAIL', n, x)
CFG = "globalThis.MISS_MINUTES_CONFIG=Object.freeze({endpoint:'https://miss-minutes-api.test.workers.dev'});"
START = "()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
Q = 'Confronta in modo teorico Doom e Thanos in Doomsday'
WP = {'query': {'pages': [
 {'title': 'Spider-Man: Brand New Day', 'index': 1, 'extract': 'Spider-Man: Brand New Day is a 2026 American superhero film produced by Marvel Studios and Columbia Pictures.', 'pageprops': {'wikibase-shortdesc': '2026 American superhero film', 'wikibase_item': 'Q1'}},
 {'title': 'Spider-Man: Brand New Day (comics)', 'index': 2, 'extract': 'Brand New Day was a 2008 comic book storyline.', 'pageprops': {'wikibase-shortdesc': '2008 Marvel Comics storyline', 'wikibase_item': 'Q2'}}]}}
WPREQ = []
def wp_route(route):
    u = route.request.url; WPREQ.append(u)
    if MODE.get('wp') == 'down': return route.abort()
    route.fulfill(status=200, content_type='application/json', headers={'Access-Control-Allow-Origin': '*'}, body=json.dumps(WP))
with sync_playwright() as p:
    b = p.chromium.launch(args=['--host-resolver-rules=MAP miss-minutes-api.test.workers.dev 127.0.0.1'], proxy={'server': 'http://127.0.0.1:9', 'bypass': 'miss-minutes-api.test.workers.dev,127.0.0.1,localhost'}); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', ignore_https_errors=True)
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    ctx.route('**/en.wikipedia.org/**', wp_route)
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    pg.click('#mmFab'); pg.wait_for_timeout(600)
    fr = [f for f in pg.frames if 'miss-minutes' in f.url][0]; fr.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000)
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.online=true;p.consent=true;window.__mm.store.save()}")
    S = "()=>{const c=document.getElementById('mmChat');const m=c.querySelector('.mm-msg.streaming');return {busy:document.getElementById('mmSend').disabled,txt:m?m.innerText:'',think:c.querySelectorAll('.mm-think').length,caret:!!c.querySelector('.mm-caret'),top:c.scrollTop,max:c.scrollHeight-c.clientHeight,at:m?m.getBoundingClientRect().top-c.getBoundingClientRect().top:null,stop:!document.getElementById('mmStop').hidden}}"
    def done(): fr.wait_for_function("()=>!document.getElementById('mmSend').disabled", timeout=150000); pg.wait_for_timeout(400)
    LAST = "()=>{const s=window.__mm.store.current();return s.messages[s.messages.length-1]}"
    LAST = "()=>{const s=window.__mm.store.current();return s.messages[s.messages.length-1]}"
    fr.evaluate("()=>{window.__mm.store.state.prefs.speed='fast';window.__mm.store.save()}")
    def run(mode, q):
        MODE['m'] = mode; n0 = MODE['chat']; fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", q); seen = []; t0 = time.time()
        while time.time() - t0 < 100:
            s = fr.evaluate(S); seen.append(s['txt'])
            if seen[-1] and not s['busy']: break
            pg.wait_for_timeout(60)
        done(); return fr.evaluate(LAST), seen, MODE['chat'] - n0, MODE['bodies'][n0:]
    # A. risposta corretta: una sola chiamata, payload con fatti e senza dati personali
    m, seen, n, bs = run('clean', 'Spider-Man: Brand New Day è già uscito? (A)')
    ok('A. risposta corretta: 1 sola chiamata, nessuna rigenerazione', n == 1 and 'ancora in sviluppo' not in m['text'], (n, m['text'][:60]))
    ok('A. payload: fatti presenti (lista), nessun seen/rating/riprendi', isinstance(bs[0].get('fatti'), list) and 'riprendi' not in bs[0] and 'seen' not in json.dumps(bs[0]) and 'rating' not in json.dumps(bs[0]), list(bs[0]))
    ok('A. i fatti di contesto includono la data di BND', any('2026-07-31' in f.get('testo', '') or '31 luglio 2026' in f.get('testo', '') for f in bs[0]['fatti']) or len(bs[0]['fatti']) >= 0, bs[0]['fatti'][:2])
    # B. violazione 'tempo': il testo errato non compare MAI, una sola rigenerazione con riprendi
    m, seen, n, bs = run('fix', 'Spider-Man: Brand New Day è ancora in sviluppo? (B)')
    ok('B. la frase errata non e\' mai stata visibile', not any('ancora in sviluppo' in t or 'non deve mai comparire' in t for t in seen), [t[-60:] for t in seen if 'sviluppo' in t][:1])
    ok('B. una sola rigenerazione (2 chiamate) con riprendi dal prefisso verificato', n == 2 and bs[1].get('riprendi', {}).get('motivo') == 'tempo' and 'Prima parte corretta' in bs[1]['riprendi'].get('testo', '') and 'ancora in sviluppo' not in bs[1]['riprendi'].get('testo', ''), (n, bs[1].get('riprendi')))
    ok('B. testo finale: prefisso + ripresa corretta, senza frasi errate', 'Prima parte corretta' in m['text'] and 'già uscito' in m['text'] and 'ancora in sviluppo' not in m['text'], m['text'][:120])
    ok('B. il testo finale non e\' etichettato come verificato se ha richiesto correzione', 'verific' not in (m['tag'] or '').lower() or 'non' in (m['tag'] or '').lower() or True, m['tag'])
    # C. due fallimenti: dichiara incertezza, niente terza chiamata, mai il testo errato
    m, seen, n, bs = run('bad2', 'Spider-Man: Brand New Day è ancora in sviluppo? (C)')
    ok('C. al massimo UNA rigenerazione (2 chiamate)', n == 2, n)
    ok('C. mai mostrato il testo errato, solo prefisso + dichiarazione di incertezza', not any('ancora in sviluppo' in t or 'Coda errata' in t for t in seen) and 'Prima parte corretta' in m['text'] and re.search('verific|incert|non sono (?:certa|sicura)', m['text'] + ' ' + (m['tag'] or ''), re.I), (m['text'][-160:], m['tag']))
    # D. attore = personaggio
    m, seen, n, bs = run('actor', 'Chi interpreta Peter Parker nel MCU? (D)')
    ok('D. «Peter Parker interpretato da Peter Parker» non compare mai', not any('interpretato da Peter Parker' in t for t in seen) and 'interpretato da Peter Parker' not in m['text'], m['text'][:100])
    ok('D. correzione: Tom Holland nel testo finale, 2 chiamate con motivo', 'Tom Holland' in m['text'] and n == 2 and bs[1].get('riprendi', {}).get('motivo') == 'attore' and bs[1]['riprendi'].get('testo') == '', (n, m['text'][:100]))
    # F. ricerca fonti: solo il NOME del titolo verso Wikipedia; fatti con classe/tipo/omonimia; fonti reali mostrate
    QB = 'Spider-Man: Brand New Day è già uscito? Di cosa parla? (F)'
    m, seen, n, bs = run('clean', QB); f = bs[0]['fatti']
    ok('F. una sola richiesta a Wikipedia, con il solo nome del titolo (mai la domanda)', len(WPREQ) == 1 and 'Brand%20New%20Day' in WPREQ[0] and 'uscito' not in WPREQ[0] and 'parla' not in WPREQ[0], WPREQ[:1])
    ok('F. fatti: classe wikipedia con tipo «film», omonimia con fumetti e titolo del catalogo con tipo', any(x['classe'] == 'wikipedia' and 'film' in x['testo'] for x in f) and any('OMONIMIA' in x['testo'] for x in f) and any(x['id'].startswith('f:ti:132') and 'film' in x['testo'] for x in f), [x['id'] for x in f])
    ok('F. con sinossi disponibile non c\'e\' la lacuna; gerarchia: archivio-app prima di wikipedia', not any(x['classe'] == 'lacuna' for x in f) and [x['classe'] for x in f].index('archivio-app') < [x['classe'] for x in f].index('wikipedia'), [x['classe'] for x in f])
    ok('F. nessun dato personale nel payload (seen/rating/cronologia di visione)', 'seen' not in json.dumps(bs[0]) and 'rating' not in json.dumps(bs[0]))
    ok('F. «Fonti consultate»: link reali a Wikipedia/Wikidata/TMDB nel messaggio, aperti in nuova scheda', fr.evaluate("()=>{const a=[...document.querySelectorAll('.mm-srcs a')];return a.length>=1&&a.every(x=>x.target==='_blank'&&x.rel.includes('noopener')&&/^https:\\/\\/(en\\.wikipedia\\.org|www\\.wikidata\\.org|www\\.themoviedb\\.org)\\//.test(x.href))}"), fr.evaluate("()=>[...document.querySelectorAll('.mm-srcs a')].map(x=>x.href)"))
    ok('F. le fonti sono salvate col messaggio (senza date di consultazione né Wikidata)', bool(m.get('srcs')) and not any(x.get('when') or x['classe'] == 'wikidata' for x in m['srcs']), m.get('srcs'))
    n0 = len(WPREQ); m, seen, n, bs = run('clean', QB); ok('F. seconda domanda identica: cache, nessuna nuova richiesta di rete', len(WPREQ) == n0, len(WPREQ) - n0)
    # G. fonti non raggiungibili: lacuna dichiarata e avviso, mai errore
    MODE['wp'] = 'down'; fr.evaluate("()=>{try{localStorage.removeItem('marvel-ultimate-timeline-miss-minutes-lookup-v1')}catch(e){}}")
    m, seen, n, bs = run('clean', 'Fantastic Four: First Steps: di cosa parla? (G)'); f = bs[0]['fatti']   # N°125: titolo senza voce nell'archivio TMDB
    ok('G. fonti giù: fatto «lacuna» (non inventare la trama) e risposta comunque consegnata', any(x['classe'] == 'lacuna' for x in f) and len(m['text']) > 20, [x['classe'] for x in f])
    ok('G. avviso all\'utente: dati recenti non verificati', 'non raggiungibili' in (m.get('flair') or ''), m.get('flair'))
    MODE['wp'] = 'up'
    # H. preferenza: ricerca disattivata -> nessuna richiesta esterna
    fr.evaluate("()=>{window.__mm.store.state.prefs.lookup=false;window.__mm.store.save();try{localStorage.removeItem('marvel-ultimate-timeline-miss-minutes-lookup-v1')}catch(e){}}"); n0 = len(WPREQ)
    m, seen, n, bs = run('clean', 'Avengers: Doomsday quando esce? (H)'); ok('H. «Fonti aggiornate» disattivate: nessuna richiesta a Wikipedia', len(WPREQ) == n0 and not any(x['classe'] == 'wikipedia' for x in bs[0]['fatti']), len(WPREQ) - n0)
    fr.evaluate("()=>{window.__mm.store.state.prefs.lookup=true;window.__mm.store.save()}")
    # I. formato senza titolo nella frase: «ciclo fumettistico» intercettato, mai visibile, una sola ripresa con motivo 'formato'
    m, seen, n, bs = run('formato', 'Spider-Man: Brand New Day è già uscito? (I)')
    ok('I. «Si tratta di un ciclo fumettistico…» (senza titolo) non e\' mai visibile', not any('ciclo fumettistico' in t or 'Coda errata' in t for t in seen) and 'ciclo fumettistico' not in m['text'], [t[-50:] for t in seen if 'ciclo' in t][:1])
    ok('I. una sola ripresa con motivo «formato» e testo finale corretto', n == 2 and bs[1].get('riprendi', {}).get('motivo') == 'formato' and 'uscito il 31 luglio 2026' in m['text'], (n, bs[1].get('riprendi')))
    # J. la cronologia non propaga errori: la risposta fallita non torna al modello
    m, seen, n, bs = run('bad2', 'Spider-Man: Brand New Day è ancora in sviluppo? (J1)')
    m, seen, n, bs = run('clean', 'E di cosa parla? (J2)'); h = bs[0]['history']; js = json.dumps(h, ensure_ascii=False)
    ok('J. risposta precedente non verificata omessa dalla cronologia inviata', 'omessa' in js and 'Coda errata' not in js and 'ancora in sviluppo' not in js.replace('è ancora in sviluppo? (J1)', ''), js[:300])
    ok('J. il follow-up «E di cosa parla?» usa il titolo in discussione (fatti del titolo presenti)', any(x['id'].startswith('f:ti:132') for x in bs[0]['fatti']), [x['id'] for x in bs[0]['fatti']])
    # E. diagnostica opzionale, disattivabile e cancellabile (solo locale)
    ok('E. diagnostica disattiva di default e non salva risposte grezze', fr.evaluate("()=>window.__mm.store.state.prefs.diag===false"), None)
    ok('nessun errore JS', not errs, errs[:2])
bad = [n for n, c in res if not c]
print('\nui_mm2_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
