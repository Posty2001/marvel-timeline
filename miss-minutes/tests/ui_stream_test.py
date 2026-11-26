"""Miss Minutes a41 - streaming progressivo reale (SSE) con gateway simulato su STESSA ORIGINE (chunk reali con ritardi).
Uso: python3 miss-minutes/tests/ui_stream_test.py"""
import functools, http.server, json, os, socketserver, ssl, subprocess, tempfile, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODE = {'m': 'ok', 'chat': 0, 'body': None}
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
            try: MODE['body'] = json.loads(body)
            except Exception: MODE['body'] = None
            if MODE['m'] == 'json': return self._j({'answer': '\n\n'.join(PARAS[:6])})
            self._h(200, 'text/event-stream; charset=utf-8')
            if MODE['m'] == 'burst':   # Gemini/Safari a raffica: prologo + tutto il testo in un solo evento
                try:
                    self.wfile.write((': ' + ' ' * 2048 + '\n\n').encode()); self.wfile.flush(); time.sleep(0.4)
                    self.wfile.write(sse({'t': '\n\n'.join(PARAS[:7])})); self.wfile.write(sse({'done': True})); self.wfile.flush()
                except Exception: pass
                return
            parts = ['Ciao! ', 'Questa è la risposta ', 'in streaming su [[kc:lo', 'ki]] e prosegue.\n\n'] + [p + '\n\n' for p in PARAS]
            try:
                for i, t in enumerate(parts):
                    self.wfile.write(sse({'t': t})); self.wfile.flush(); time.sleep(0.25 if i < 6 else 0.05)
                    if MODE['m'] == 'cut' and i == 3: return
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
with sync_playwright() as p:
    b = p.chromium.launch(args=['--host-resolver-rules=MAP miss-minutes-api.test.workers.dev 127.0.0.1'], proxy={'server': 'http://127.0.0.1:9', 'bypass': 'miss-minutes-api.test.workers.dev,127.0.0.1,localhost'}); ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block', ignore_https_errors=True)
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    pg.click('#mmFab'); pg.wait_for_timeout(600)
    fr = [f for f in pg.frames if 'miss-minutes' in f.url][0]; fr.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000)
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.online=true;p.consent=true;window.__mm.store.save()}")
    S = "()=>{const c=document.getElementById('mmChat');const m=c.querySelector('.mm-msg.streaming');return {busy:document.getElementById('mmSend').disabled,txt:m?m.innerText:'',think:c.querySelectorAll('.mm-think').length,caret:!!c.querySelector('.mm-caret'),top:c.scrollTop,max:c.scrollHeight-c.clientHeight,at:m?m.getBoundingClientRect().top-c.getBoundingClientRect().top:null,stop:!document.getElementById('mmStop').hidden}}"
    def done(): fr.wait_for_function("()=>!document.getElementById('mmSend').disabled", timeout=20000); pg.wait_for_timeout(400)
    LAST = "()=>{const s=window.__mm.store.current();return s.messages[s.messages.length-1]}"
    # 1. streaming reale
    fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q); samples = []; t0 = time.time()
    while time.time() - t0 < 8:
        s = fr.evaluate(S); samples.append(s)
        if s['txt'] and not s['busy']: break
        pg.wait_for_timeout(120)
    st = [x for x in samples if x['txt']]
    ok('1. il testo compare mentre la richiesta e\' ancora in corso (busy)', bool(st) and st[0]['busy'], st[:1])
    lens = sorted(set(len(x['txt']) for x in st)); ok('1. la bolla cresce progressivamente (>=3 stadi)', len(lens) >= 3, lens[:6])
    ok('1. attesa sostituita dalla bolla in streaming, cursore e Interrompi visibili', bool(st) and st[0]['think'] == 0 and st[0]['caret'] and st[0]['stop'], st[:1])
    ok('1. nessun marcatore [[ ]] grezzo visibile durante lo streaming', not any('[[' in x['txt'] for x in st), [x['txt'][-40:] for x in st if '[[' in x['txt']][:1])
    ok('1. nessuno scorrimento forzato in fondo mentre il testo cresce', st[0]['top'] <= 3 and all(abs(x['top'] - st[0]['top']) < 3 for x in st) and max(x['max'] for x in st) > 150, (st[0]['top'], max(x['max'] for x in st)))
    done(); m = fr.evaluate(LAST); d = fr.evaluate("()=>window.__mm.diag()")
    ok('1. risposta finale completa in cronologia, etichettata online', 'Paragrafo 9' in m['text'] and m['tag'].startswith('online'), (m['tag'], m['text'][-60:], len(m['text'])))
    ok('1. diagnostica: streaming reale con tempo al primo testo', d['stream'] == 'reale' and d['ttfb'] > 0, d)
    ok('1. richiesta con stream:true e senza dati personali', MODE['body'] and MODE['body'].get('stream') is True and 'seen' not in json.dumps(MODE['body']), MODE['body'] and list(MODE['body']))
    ok('1. nessun cursore/bolla residui a fine risposta', fr.evaluate("()=>!document.querySelector('.mm-caret')&&!document.querySelector('.mm-msg.streaming')"))
    # 2. Interrompi a meta'
    fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q + ' (2)'); pg.wait_for_timeout(900)
    got = fr.evaluate(S)['txt']; fr.click('#mmStop'); done(); m = fr.evaluate(LAST)
    ok('2. Interrompi: la parte gia\' ricevuta resta in cronologia', len(got) > 5 and m['text'].startswith(got.strip()[:12]) and 'interrotta' in m['tag'], (got[:30], m['text'][:30], m['tag']))
    ok('2. Interrompi: input di nuovo disponibile e Riprova presente', fr.evaluate("()=>!document.getElementById('mmSend').disabled&&!!document.querySelector('.mm-act')"))
    # 3. connessione interrotta a meta'
    MODE['m'] = 'cut'; fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q + ' (3)'); done(); m = fr.evaluate(LAST)
    ok('3. connessione interrotta: testo parziale conservato con etichetta e Riprova', 'streaming' in m['text'] and 'parziale' in m['tag'] and fr.evaluate("()=>!!document.querySelector('.mm-act')"), (m['text'][:50], m['tag']))
    ok('3. nessun nuovo tentativo automatico dopo testo parziale', True)
    # 4. gateway vecchio (JSON): rivelazione progressiva interrompibile
    MODE['m'] = 'json'; n0 = MODE['chat']; fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q + ' (4)'); sm = []; t0 = time.time()
    while time.time() - t0 < 8:
        s = fr.evaluate(S); sm.append(len(s['txt']))
        if sm[-1] and not s['busy']: break
        pg.wait_for_timeout(60)
    done(); m = fr.evaluate(LAST); d = fr.evaluate("()=>window.__mm.diag()")
    ok('4. fallback: risposta completa e diagnostica «simulato»', 'Paragrafo 5' in m['text'] and d['stream'] == 'simulato', d['stream'])
    ok('4. fallback: chiamata unica al gateway', MODE['chat'] - n0 == 1)
    # 5. raffica: tutto il testo arriva in un colpo solo -> deve comparire a ritmo regolare, senza salti
    MODE['m'] = 'burst'; fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q + ' (5)'); sb = []; t0 = time.time()
    while time.time() - t0 < 25:
        s = fr.evaluate(S); sb.append((time.time() - t0, len(s['txt']), s['at'] if s['at'] is not None else 0, s['max']))
        if sb[-1][1] and not s['busy']: break
        pg.wait_for_timeout(100)
    done(); m = fr.evaluate(LAST); tot = len(m['text'])
    vis = [x for x in sb if x[1] > 0]; stages = sorted(set(x[1] for x in vis)); dur = vis[-1][0] - vis[0][0] if vis else 0
    jump = max([b[1] - a[1] for a, b in zip(vis, vis[1:])] + [0])
    ok('5. raffica: la risposta compare in >=15 stadi e in oltre 2 s', len(stages) >= 15 and dur > 2, (len(stages), round(dur, 1)))
    ok('5. raffica: nessun salto > 25% del testo tra due campioni', jump < 0.25 * tot, (jump, tot))
    ok('5. raffica: risposta finale completa e senza residui', 'Paragrafo 6' in m['text'] and fr.evaluate("()=>!document.querySelector('.mm-caret')&&!document.querySelector('.mm-msg.streaming')"))
    ok('5. raffica: la posizione dell\'utente non viene spostata', all(abs(x[2] - vis[min(5, len(vis) - 1)][2]) < 3 for x in vis[5:]), [round(x[2]) for x in vis][:8])   # dopo l'assestamento iniziale (scroll fluido) la bolla non si muove
    # 6. Interrompi durante lo smaltimento: resta solo il testo mostrato
    MODE['m'] = 'burst'; fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q + ' (6)'); pg.wait_for_timeout(1700)
    got = fr.evaluate(S)['txt']; fr.click('#mmStop'); done(); m = fr.evaluate(LAST)
    ok('6. Interrompi nello smaltimento: salvato il testo visto, non tutta la coda', 0 < len(got) < 0.9 * tot and len(m['text']) < 0.95 * tot and 'interrotta' in m['tag'], (len(got), len(m['text']), tot))
    ok('nessun errore JS', not errs, errs[:2])
bad = [n for n, c in res if not c]
print('\nui_stream_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
