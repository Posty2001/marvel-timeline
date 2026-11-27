"""Miss Minutes 2.0 fase C.1 - interfaccia pulita, intento, spoiler, soggetto, correzione, stato di uscita.
Uso: python3 miss-minutes/tests/ui_c1_test.py"""
import functools, http.server, json, os, socketserver, ssl, subprocess, tempfile, threading, time
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODE = {'m': 'ok', 'chat': 0, 'body': None, 'qs': [], 'fail_once': None}
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
            try: msgs = (MODE['body'] or {}).get('messages') or []; qtxt = [m for m in msgs if m.get('role') == 'user'][-1].get('text') or [m for m in msgs if m.get('role') == 'user'][-1].get('content') or ''
            except Exception: qtxt = ''
            MODE['qs'].append(qtxt)
            if MODE['fail_once'] and MODE['fail_once'] in str(qtxt) and not MODE.get('failed'):
                MODE['failed'] = 1; return self._j({'error': 'rate', 'message': 'x'}, 429)
            self._h(200, 'text/event-stream; charset=utf-8')
            try:
                self.wfile.write(sse({'t': '' + MODE.get('reply', 'Risposta di prova generica sul tema richiesto. ') + ''})); self.wfile.flush(); time.sleep(0.05)
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

def ask(fr, q, reply):
    MODE['reply'] = reply; n0 = MODE['chat']
    fr.evaluate("(q)=>window.__mm.ask(q,{forceOnline:true})", q)
    return fr.evaluate("()=>{const s=window.__mm.store.current();const m=s.messages[s.messages.length-1];return {text:m.text,tag:m.tag,srcs:m.srcs||[],vf:m.vf}}")
with sync_playwright() as p:
    b = p.chromium.launch(args=['--host-resolver-rules=MAP miss-minutes-api.test.workers.dev 127.0.0.1'], proxy={'server': 'http://127.0.0.1:9', 'bypass': 'miss-minutes-api.test.workers.dev,127.0.0.1,localhost'}); ctx = b.new_context(viewport={'width': 390, 'height': 800}, ignore_https_errors=True)
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    pg.click('#mmFab'); pg.wait_for_timeout(600)
    fr = [f for f in pg.frames if 'miss-minutes' in f.url][0]; fr.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000)
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.online=true;p.consent=true;p.spoiler=true;window.__mm.store.save()}")
    fr.evaluate("()=>window.__mm.go('chat')")
    # 1) mcu07: domanda generale -> AI online, NON statistiche personali
    r = ask(fr, 'Quanti film compongono la Saga dell\'Infinito?', 'La Saga dell\'Infinito comprende 23 film.')
    ok('mcu07: risposta online, non statistica personale', MODE['chat'] == 1 and r['tag'].startswith('online') and 'Hai segnato' not in r['text'], r['tag'])
    r = ask(fr, 'Quanti film ho visto?', 'x'); ok('«Quanti film ho visto?» resta personale (locale)', MODE['chat'] == 1 and r['tag'] == 'dati locali', r['tag'])
    # 2) interfaccia pulita: nessun tag tecnico, nessuna fonte visibile finche' non si preme «Fonti»
    fr.evaluate("()=>window.__mm.go('chat')"); fr.wait_for_timeout(300)
    t = fr.evaluate("()=>document.getElementById('mmChat').innerText")
    ok('nessun «controlli automatici / spoiler non garantiti / Fonti consultate» sotto le risposte', not any(x in t for x in ['controlli automatici', 'spoiler non garantiti', 'Fonti consultate', 'non è una conferma', 'consultata il']), t[-200:])
    # 3) spoiler: esplicito -> payload 'off'; altrimenti 'avoid' (preferenza invariata)
    MODE['body'] = None; ask(fr, 'Fammi uno spoiler: chi muore in Avengers: Infinity War?', 'Muoiono Gamora, Loki e Vision.'); sp1 = MODE['body'].get('spoiler')
    ask(fr, 'Parlami di Thor', 'Thor e il dio del tuono.'); sp2 = MODE['body'].get('spoiler')
    ok('spoiler esplicito: consentito solo per quella domanda', sp1 == 'off' and sp2 == 'avoid', (sp1, sp2))
    # 4) stato di uscita nei fatti: BND (TMDB Released) -> «già uscito»; titolo senza stato -> nessuna deduzione dalla data
    MODE['body'] = None; ask(fr, 'Spider-Man: Brand New Day è già uscito?', 'Sì, è uscito il 29 luglio 2026 in Italia.')
    ft = ' | '.join(f['testo'] for f in MODE['body'].get('fatti', []))
    ok('fatti: BND «già uscito (stato TMDB: Released)»', 'già uscito (stato TMDB: Released)' in ft, ft[:300])
    ok('fatti: nessuna etichetta «non è una conferma ufficiale»', 'non è una conferma ufficiale' not in ft)
    ok('BND: nessun avviso sulla data italiana documentata', 'in archivio risultano' not in fr.evaluate("()=>window.__mm.store.current().messages.slice(-1)[0].text"))
    # 5) soggetto conservato nei seguiti (anche dopo una domanda senza titolo)
    MODE['body'] = None; ask(fr, 'Chi ha diretto Spider-Man: Brand New Day?', 'Lo dirige Destin Daniel Cretton.'); ask(fr, 'E chi è il protagonista?', 'Tom Holland.'); r = ask(fr, 'E quando è uscito?', 'Non è ancora uscito.')
    ok('seguito a 2 domande di distanza: contraddizione ancora intercettata (soggetto conservato)', r['vf'] and r['vf'].get('retried', 0) >= 1 or 'Su questo punto' in r['text'], r['text'][:200])
    # 6) correzione col dato documentato, senza «non lo riporto» ne' ⚠
    ok('nota di correzione naturale con il dato documentato', 'Su questo punto mi attengo ai dati documentati' in r['text'] and '⚠' not in r['text'] and 'non lo riporto' not in r['text'] and 'luglio' in r['text'].lower() or '29/07/2026' in r['text'], r['text'][-300:])
    ok('nessun errore di pagina', not errs, errs[:2])
fails = [n for n, c in res if not c]; print('\n%d/%d' % (len(res) - len(fails), len(res))); raise SystemExit(1 if fails else 0)
