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
def patched_archive():
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'knowledge', 'tmdb_titoli.json'), encoding='utf-8')); d['versione'] = 2
    d['voci']['112']['stagione'] = {'n': 2, 'nome': 'Stagione 2', 'sinossi_it': 'Sinossi della seconda stagione di prova.', 'data': '2023-10-05', 'episodi': 6, 'cast': ['Attore Prova']}
    d['voci']['112']['serie'] = {'prima': '2021-06-09', 'ultima': '2023-11-09', 'n_stagioni': 2}
    d['voci']['119']['stagione'] = {'n': 3, 'nome': 'Stagione 3', 'sinossi_it': '', 'data': '2024-12-22', 'episodi': 4, 'cast': []}
    d['voci']['125'] = {'tmdb': {'t': 'movie', 'id': 999999}, 'titolo': 'Fantastic Four: First Steps', 'sinossi_it': 'Sinossi di prova.', 'regista': ['Regista Prova'], 'cast': [], 'stato': 'Released', 'date': [{'paese': 'US', 'data': '2025-07-25'}], 'url': 'https://www.themoviedb.org/movie/999999', 'risoluzione': 'auto'}
    return json.dumps(d)
def tmdb_route(route): route.fulfill(status=200, content_type='application/json', body=patched_archive())
with sync_playwright() as p:
    b = p.chromium.launch(args=['--host-resolver-rules=MAP miss-minutes-api.test.workers.dev 127.0.0.1'], proxy={'server': 'http://127.0.0.1:9', 'bypass': 'miss-minutes-api.test.workers.dev,127.0.0.1,localhost'}); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', ignore_https_errors=True)
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    ctx.route('**/en.wikipedia.org/**', wp_route)
    ctx.route('**/knowledge/tmdb_titoli.json', tmdb_route)
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
    fr.evaluate("()=>{window.__mm.store.state.prefs.speed='fast';window.__mm.store.save()}")
    def run(mode, q):
        MODE['m'] = mode; n0 = MODE['chat']; fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", q); t0 = time.time()
        while time.time() - t0 < 100:
            s = fr.evaluate(S)
            if s['txt'] and not s['busy']: break
            pg.wait_for_timeout(60)
        done(); return fr.evaluate(LAST), MODE['chat'] - n0, MODE['bodies'][n0:]
    MODE['wp'] = 'down'   # SOLO archivio TMDB: Wikipedia non raggiungibile, per provare che l'archivio basta
    m, n, bs = run('clean', 'Spider-Man: Brand New Day: di cosa parla? (K)'); f = bs[0]['fatti']
    tm = [x for x in f if x['classe'] == 'tmdb']
    ok('K. archivio TMDB usato: sinossi e regia di BND nei fatti inviati', any('sinossi TMDB' in x['testo'] and 'quattro anni' in x['testo'] and 'Destin Daniel Cretton' in x['testo'] for x in tm), [x['id'] for x in f])
    ok('K. date per paese (IT 29/07/2026, US 31/07/2026) e nessuna discordanza con la Timeline', any('IT 29/07/2026' in x['testo'] and 'US 31/07/2026' in x['testo'] and 'DISCORDANZA' not in x['testo'] for x in tm), [x['testo'][:160] for x in tm])
    ok('K. con la sinossi TMDB non c\'e\' la «lacuna» anche con Wikipedia giù', not any(x['classe'] == 'lacuna' for x in f), [x['classe'] for x in f])
    ok('K. il fatto TMDB e\' dichiarato non ufficiale e ordinato dopo archivio-app', all('non è una conferma ufficiale' in x['testo'] for x in tm if ':d' in x['id']) and [x['classe'] for x in f].index('archivio-app') < [x['classe'] for x in f].index('tmdb'), [x['classe'] for x in f])
    ok('K. sinossi non tagliata a meta\' parola (termina con punteggiatura o «…»)', all(re.search(r'[.!?…]( Regia:.*)?$', x['testo'].split(' Regia:')[0]) for x in tm if ':s' in x['id']), [x['testo'][-60:] for x in tm if ':s' in x['id']])
    ok('K. «Fonti consultate»: link TMDB reale al film, con data di generazione', fr.evaluate("()=>[...document.querySelectorAll('.mm-srcs a')].some(a=>a.href==='https://www.themoviedb.org/movie/969681')") and any(x['classe'] == 'tmdb' and x['when'] for x in m.get('srcs', [])), m.get('srcs'))
    ok('K. nessun dato personale nel payload', 'seen' not in json.dumps(bs[0]) and 'rating' not in json.dumps(bs[0]))
    # L. stagioni (archivio v2): dati DELLA STAGIONE, non della serie
    m, n, bs = run('clean', 'Loki S2: quando è uscita? (L)'); tm = [x for x in bs[0]['fatti'] if x['classe'] == 'tmdb']
    ok('L. stagione: sinossi, data (05/10/2023), episodi e cast della STAGIONE 2, senza «NON è la data»', any('sinossi TMDB della stagione 2' in x['testo'] and 'seconda stagione di prova' in x['testo'] for x in tm) and any('stagione 2: uscita TMDB 05/10/2023, 6 episodi' in x['testo'] and 'Attore Prova' in x['testo'] and 'NON è la data' not in x['testo'] for x in tm), [x['testo'][:200] for x in tm])
    m, n, bs = run('clean', 'What If...? S3: di cosa parla? (L3)'); tm = [x for x in bs[0]['fatti'] if x['classe'] == 'tmdb']
    ok('L. stagione senza sinossi propria: dichiarato «della SERIE (la stagione non ha sinossi propria…)»', any('della SERIE (la stagione non ha sinossi propria' in x['testo'] for x in tm), [x['testo'][:200] for x in tm])
    # N. associazione automatica: dichiarata come non confermata
    m, n, bs = run('clean', 'Fantastic Four: First Steps: regia? (N)'); tm = [x for x in bs[0]['fatti'] if x['classe'] == 'tmdb']
    ok('N. associazione TMDB automatica: dichiarata «non ancora confermata»', any('associazione TMDB automatica, non ancora confermata' in x['testo'] for x in tm) and any('Regista Prova' in x['testo'] for x in tm), [x['testo'][:160] for x in tm])
    # M. film con date TMDB discordanti dalla Timeline: discordanza dichiarata
    m, n, bs = run('clean', 'Ghost Rider: Spirit of Vengeance quando è uscito? (M)'); tm = [x for x in bs[0]['fatti'] if x['classe'] == 'tmdb']
    ok('M. date TMDB discordanti dalla Timeline: «DISCORDANZA» dichiarata', any('DISCORDANZA' in x['testo'] for x in tm), [x['testo'][:200] for x in tm])
    ok('nessun errore JS', not errs, errs[:2])
bad = [n for n, c in res if not c]
print('\nui_tmdb_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
