"""Miss Minutes mm2.0-b autoscroll (derivato dal test streaming) - a41 - streaming progressivo reale (SSE) con gateway simulato su STESSA ORIGINE (chunk reali con ritardi).
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
    def done(): fr.wait_for_function("()=>!document.getElementById('mmSend').disabled", timeout=150000); pg.wait_for_timeout(400)
    LAST = "()=>{const s=window.__mm.store.current();return s.messages[s.messages.length-1]}"
    fr.evaluate("()=>{window.__mm.store.state.prefs.speed='fast';window.__mm.store.save()}")
    M = "()=>{const c=document.getElementById('mmChat');const d=document.getElementById('mmDown');return {top:c.scrollTop,dist:c.scrollHeight-c.scrollTop-c.clientHeight,h:c.scrollHeight,ch:c.clientHeight,down:!d.hidden,busy:document.getElementById('mmSend').disabled,beh:getComputedStyle(c).scrollBehavior,fol:window.__mm.follow(),len:(c.querySelector('.mm-msg.streaming')||{innerText:''}).innerText.length}}"
    def samp(sec, step=120):
        out = []; t0 = time.time()
        while time.time() - t0 < sec: out.append(fr.evaluate(M)); pg.wait_for_timeout(step)
        return out
    def getbox():
        fb = fr.frame_element().bounding_box(); b0_ = fr.evaluate("()=>{const r=document.getElementById('mmChat').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}"); return [fb['x'] + b0_[0], fb['y'] + b0_[1]]
    # 1. in fondo: segue il testo
    fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q + ' (1)')
    pg.wait_for_function("()=>true"); t0 = time.time()
    while time.time() - t0 < 30 and fr.evaluate(M)['h'] <= fr.evaluate(M)['ch'] + 200: pg.wait_for_timeout(200)
    a = samp(5)
    ok('1. contenuto piu\' alto della vista (test significativo)', a[0]['h'] > a[0]['ch'] + 100, (a[0]['h'], a[0]['ch']))
    ok('1. in fondo: l\'autoscroll segue il testo (distanza dal fondo < 60 px)', all(x['dist'] < 60 for x in a), [round(x['dist']) for x in a][:10])
    tops = [x['top'] for x in a]; ok('1. nessun salto all\'indietro dello scroll', all(b >= a_ - 1 for a_, b in zip(tops, tops[1:])), tops[:8])
    ok('1. nessuna animazione smooth sovrapposta durante lo streaming', all(x['beh'] == 'auto' for x in a), a[0]['beh'])
    box = getbox()
    # 2. scorro verso l'alto: l'autoscroll si sospende
    pg.mouse.move(box[0], box[1]); pg.mouse.wheel(0, -500); pg.wait_for_timeout(500)
    b0 = fr.evaluate(M); b = samp(3)
    ok('2. scorrendo verso l\'alto la vista resta ferma mentre il testo cresce', all(abs(x['top'] - b0['top']) < 3 for x in b) and b[-1]['h'] > b0['h'], (b0['top'], [round(x['top']) for x in b][:5], b0['h'], b[-1]['h']))
    ok('2. appare la freccia verso il basso', b[-1]['down'], b[-1])
    # 3. freccia: riprende
    fr.click('#mmDown'); pg.wait_for_timeout(700); c = samp(3)
    ok('3. con la freccia l\'autoscroll riprende e segue il testo', all(x['dist'] < 60 for x in c[2:]), [round(x['dist']) for x in c])
    # 4. risalgo e poi torno in fondo a mano
    pg.mouse.move(box[0], box[1]); pg.mouse.wheel(0, -500); pg.wait_for_timeout(500); d0 = fr.evaluate(M)
    pg.mouse.wheel(0, 5000); pg.wait_for_timeout(900); d = samp(3)
    ok('4. tornando in fondo manualmente l\'autoscroll riprende', all(x['dist'] < 60 for x in d[2:]), [round(x['dist']) for x in d])
    # 5. nessun salto finale (resto in fondo, quindi continuo a seguire fino alla fine)
    pre = None
    while True:
        s_ = fr.evaluate(M)
        if not s_['busy']: break
        pre = s_; pg.wait_for_timeout(200)
    pg.wait_for_timeout(800); post = fr.evaluate(M)
    ok('5. a fine risposta resto in fondo (nessun salto in cima alla risposta)', post['dist'] < 60, post)
    # 6. risposta 2: scorro su e NON torno: a fine risposta la posizione non cambia
    fr.evaluate("(q)=>{window.__mm.ask(q);return 1}", Q + ' (6)'); t0 = time.time()
    while time.time() - t0 < 30 and fr.evaluate(M)['h'] <= fr.evaluate(M)['ch'] + 300: pg.wait_for_timeout(200)
    pg.wait_for_timeout(1500); pg.mouse.move(box[0], box[1]); pg.mouse.wheel(0, -700); pg.wait_for_timeout(600); keep = fr.evaluate(M)['top']
    while fr.evaluate(M)['busy']: pg.wait_for_timeout(250)
    pg.wait_for_timeout(900); end = fr.evaluate(M)
    ok('6. con autoscroll sospeso, a fine risposta la posizione non viene spostata', abs(end['top'] - keep) < 3, (keep, end['top']))
    ok('nessun errore JS', not errs, errs[:2])
bad = [n for n, c in res if not c]
print('\nui_scroll_test: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
