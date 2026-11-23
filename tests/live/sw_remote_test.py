"""TVA Live 1.1 Fase 3 - prova con SERVICE WORKER REALE: endpoint simulato con context.route (intercetta anche le richieste fatte dal service worker).
Verifica: lettura cross-origin con CORS attraverso il SW, cache del SW, funzionamento offline, contenuto manomesso rifiutato. Uso: python3 tests/live/sw_remote_test.py"""
import functools, http.server, json, os, re, socketserver, threading
os.environ['PW_EXPERIMENTAL_SERVICE_WORKER_NETWORK_EVENTS'] = '1'     # Playwright: le richieste fatte dal service worker passano da context.route
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
NS = {'__file__': os.path.join(HERE, 'remote_test.py'), '__name__': 'rt_helpers'}
src = open(NS['__file__'], encoding='utf-8').read().split('\nwith sync_playwright() as pw:\n')[0]; exec(compile(src, NS['__file__'], 'exec'), NS)
mk, CALN, TR, CAL, manifest, STATE, ok, res, sync_playwright, BASE, G = (NS[k] for k in ('mk', 'CALN', 'TR', 'CAL', 'manifest', 'STATE', 'ok', 'res', 'sync_playwright', 'BASE', 'G'))
EP = {'bundle': mk(CALN, TR, G(1)), 'up': True, 'log': []}
def ep_route(r):
    u = r.request.url; EP['log'].append(u); b = EP['bundle']; rel = u[len(BASE):] if u.startswith(BASE) else None
    body = json.dumps(b['ptr']) if rel == 'current.json' else b['files'].get(rel) if rel else None
    if not EP['up']: return r.abort('internetdisconnected')
    if body is None: return r.fulfill(status=404, body='', headers={'access-control-allow-origin': '*'})
    r.fulfill(status=200, body=body, headers={'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*', 'cache-control': 'max-age=600'})    # intestazioni come GitHub Pages
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(H, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
APP = 'http://127.0.0.1:%d/index.html' % srv.server_address[1]
def open_live(pg):
    pg.wait_for_selector('#item-073', state='attached', timeout=20000)
    pg.evaluate("()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(400)
    pg.evaluate("()=>document.getElementById('appTabMissioni').click()"); pg.wait_for_timeout(300); pg.evaluate("()=>document.getElementById('cenTab-live').click()")
    pg.wait_for_function("()=>window.tvaLive && window.tvaLive.data().status==='ok'", timeout=25000)
    return pg.evaluate("()=>{const x=window.tvaLive.data();return {s:x.source,e:x.remoteErr,rej:x.remoteRejected,v:x.version,cal:x.calendar.map(i=>i.key)}}")
tamper = lambda files, ptr: files.__setitem__(ptr['files']['calendar']['path'], files[ptr['files']['calendar']['path']].replace('Solo Remoto', 'Solo RemotX'))
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 820}); ctx.route(re.compile(r'https://posty2001\.github\.io/.*'), ep_route)      # service worker CONSENTITO
    STATE.update(cal=CAL, tr=NS['TR'], man=manifest(generated_at=G(-120)), fail=False)
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route(re.compile(r'.*/assets/live/.*'), lambda r: r.continue_())          # dati inclusi REALI del repository
    pg.goto(APP); pg.wait_for_selector('#item-073', state='attached'); pg.evaluate("()=>navigator.serviceWorker.ready.then(()=>true)"); pg.reload()
    ok('SW: service worker attivo e controlla la pagina', pg.evaluate("()=>!!navigator.serviceWorker.controller"))
    dd = open_live(pg)
    ok('SW: attraverso il service worker, HTTPS cross-origin + CORS: catalogo remoto verificato e accettato', dd['s'] == 'remote' and dd['e'] is None and 'tmdb:movie:5000' in dd['cal'], dd)
    ok('SW: nessun errore di pagina', not errs, errs)
    ok('SW: richieste all endpoint = puntatore + 3 file immutabili', len(EP['log']) >= 4 and EP['log'][0].endswith('/v1/current.json'), EP['log'])
    pg.wait_for_timeout(500); EP['up'] = False; ctx.set_offline(True); pg.reload(); dd = open_live(pg)
    ok('SW offline (endpoint giu): l app si apre e Live mostra l ultimo catalogo VALIDO remoto (dal SW o dalla copia locale), non quello incluso piu vecchio', dd['s'] in ('remote', 'cache') and 'tmdb:movie:5000' in dd['cal'], dd)
    ctx.set_offline(False); EP['up'] = True; EP['bundle'] = mk(CALN, TR, G(2), post=tamper); pg.reload(); dd = open_live(pg)
    ok('SW: contenuto remoto manomesso servito attraverso il SW: rifiutato (hash), resta l ultima versione valida', dd['rej'] is True and 'sha-256' in (dd['e'] or '').lower() and dd['s'] == 'cache' and 'tmdb:movie:5000' in dd['cal'], dd)
    b.close()
bad = [n for n, c in res if not c]; print('\n%d/%d PASS' % (len(res) - len(bad), len(res)))
for n in bad: print('FAIL: ' + n)
raise SystemExit(1 if bad else 0)
