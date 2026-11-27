"""Miss Minutes 2.0 fase C - runner di valutazione (eval.js + dialogo) con gateway simulato.
Uso: python3 miss-minutes/tests/ui_eval_test.py"""
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
                self.wfile.write(sse({'t': 'Risposta di prova generica sul tema richiesto. '})); self.wfile.flush(); time.sleep(0.05)
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
    
with sync_playwright() as p:
    b = p.chromium.launch(args=['--host-resolver-rules=MAP miss-minutes-api.test.workers.dev 127.0.0.1'], proxy={'server': 'http://127.0.0.1:9', 'bypass': 'miss-minutes-api.test.workers.dev,127.0.0.1,localhost'}); ctx = b.new_context(viewport={'width': 390, 'height': 800}, ignore_https_errors=True)
    ctx.route('**/miss-minutes/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    pg.click('#mmFab'); pg.wait_for_timeout(600)
    fr = [f for f in pg.frames if 'miss-minutes' in f.url][0]; fr.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000)
    fr.evaluate("()=>{const p=window.__mm.store.state.prefs;p.online=true;p.consent=true;window.__mm.store.save()}")
    # 1) il set esiste, e' ben formato e copre le categorie richieste
    sset = fr.evaluate("async()=>await (await fetch('eval/domande.json')).json()")
    D = sset['domande']; cats = {x['cat'] for x in D}
    ok('set >= 50 domande', len(D) >= 50, len(D))
    ok('categorie richieste coperte', {'MCU', 'Sony', 'Fox', 'Fumetti', 'Multiverso', 'Attori', 'Cronologia', 'Novità', 'Teorie', 'Seguiti'} <= cats, sorted(cats))
    ids = [x['id'] for x in D]; ok('id unici e catene valide', len(ids) == len(set(ids)) and all((not x.get('dopo')) or x['dopo'] in ids for x in D))
    ok('seguiti dipendenti dal contesto >= 6', sum(1 for x in D if x.get('dopo')) >= 6)
    # 2) il runner: catena di 3 + una domanda singola, con un errore di quota transitoria simulato (gap=0, retry accelerato)
    fr.evaluate("()=>{window.MMEval=undefined}")
    fr.add_script_tag(url='eval.js'); fr.wait_for_function("()=>window.MMEval", timeout=5000)
    sel = [x for x in D if x['id'] in ('seg01a', 'seg01b', 'seg01c', 'mcu01')]
    MODE['qs'] = []
    out = fr.evaluate("""async(sel)=>{const m=window.__mm;const h={newChat:()=>{m.store.state.active=null},count:()=>{const s=m.store.current();return s?s.messages.length:0},ask:q=>m.ask(q,{forceOnline:true}),diag:()=>m.diag(),last:()=>{const s=m.store.current();if(!s||!s.messages.length)return null;const x=s.messages[s.messages.length-1];return x.role==='assistant'?x:null}};
      const sessBefore=m.store.state.sessions.length; const r=await window.MMEval.run(h,sel,{gap:0},null,null); r.nsess=m.store.state.sessions.length-sessBefore; return r}""", sel, )
    R = out['risultati']
    ok('4 risposte raccolte, tutte ok', len(R) == 4 and all(x['ok'] for x in R), [x.get('code') for x in R])
    ok('catena = una sola conversazione, singola = altra', out['nsess'] == 2, out['nsess'])
    ok('risposte online reali (non locali)', all(x['online'] for x in R), [x['tag'] for x in R])
    ok('metadati: ms, ttfb, stream, vf', all(x['ms'] > 0 and x['stream'] for x in R) and all(x['vf'] for x in R), [(x['ms'], x['stream']) for x in R][:2])
    ok('testo e domanda registrati', 'Risposta di prova' in R[0]['text'] and any(x['q'].startswith('E chi') and x['dopo'] == 'seg01a' for x in R), [R[0]['text'][:80], R[1]['q']])
    ok('il gateway ha ricevuto 4 richieste, forzate online', MODE['chat'] == 4, MODE['chat'])
    out2 = fr.evaluate("""()=>{const m=window.__mm;return m.store.state.sessions.length}""")
    ok('nessun errore di pagina', not errs, errs[:2])
    # 3) dialogo e riga in Impostazioni
    fr.evaluate("()=>window.__mm.go('set')"); fr.wait_for_timeout(300)
    ok('riga Valutazione risposte in Impostazioni', fr.evaluate("()=>[...document.querySelectorAll('.mm-srow')].some(b=>/Valutazione risposte/.test(b.innerText))"))
    fr.evaluate("()=>window.__mm.evalDialog()"); fr.wait_for_timeout(300)
    ok('dialogo con Avvia / Salva il file JSON', fr.evaluate("()=>{const t=document.getElementById('mmDlgBody').innerText;return /Avvia la valutazione completa/.test(t)&&/Salva il file JSON/.test(t)}"))
    # export come FILE dall'interfaccia (download), con riepilogo calcolato sul dispositivo
    fr.evaluate("(o)=>localStorage.setItem('marvel-ultimate-timeline-miss-minutes-eval-v1',JSON.stringify(o))", out)
    fr.evaluate("()=>document.getElementById('mmDlg').close&&document.getElementById('mmDlg').close()"); fr.evaluate("()=>window.__mm.evalDialog()"); fr.wait_for_timeout(600)
    ok('riepilogo mostrato nel dialogo', fr.evaluate("()=>/Eseguite 4\\/123/.test(document.getElementById('mmDlgBody').innerText)"), fr.evaluate("()=>document.getElementById('mmDlgBody').innerText.slice(0,300)"))
    with pg.expect_download(timeout=8000) as dl:
        fr.evaluate("()=>[...document.querySelectorAll('#mmDlgBody button')].find(b=>/Salva il file JSON/.test(b.innerText)).click()")
    f = dl.value; import json as _j; body = _j.load(open(f.path()))
    ok('file scaricato .json con nome datato', bool(__import__('re').match(r'^miss-minutes-valutazione-\d{8}-\d{4}\.json$', f.suggested_filename)), f.suggested_filename)
    ok('file con risultati + riepilogo', len(body['risultati']) == 4 and body['riepilogo']['eseguite'] == 4 and 'categorie' in body['riepilogo'])
fails = [n for n, c in res if not c]; print('\n%d/%d' % (len(res) - len(fails), len(res))); raise SystemExit(1 if fails else 0)
