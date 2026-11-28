"""Integrazione NATIVA del database esteso (dati reali, iPhone 390x844): le voci db entrano in ricerca/cataloghi senza archivio separato."""
import sys, socket, threading, http.server, functools, pathlib, json
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
res = []; errs = []
def ok(n, c, d=''): res.append(bool(c)); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)[:200]) if (d and not c) else ''))
st = json.load(open(ROOT/'atlante2/data/db/stub.json'))
nuove = [r for r in st['r'] if r[4] == 'B'][:1] or st['r'][:1]
nome = nuove[0][1]; ident = nuove[0][0]
def free():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
port = free(); srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=str(ROOT))); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:%d/index.html' % port
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(900)
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(2000)
    pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'search',q:''}})"); pg.wait_for_timeout(600)
    pg.fill('#atlas2 .a3-in', nome); pg.wait_for_timeout(1000)
    ok('nessun gruppo separato «Archivio esteso» nella ricerca', not pg.evaluate("()=>!!document.querySelector('#atlas2 .a3-dbg')"))
    ok('la voce db compare nei risultati nativi', nome.split(' (')[0] in pg.evaluate("()=>document.querySelector('#atlas2').textContent"))
    pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'dbx',id:%s,o:%s}})" % (json.dumps(ident), json.dumps(nuove[0][5]))); pg.wait_for_timeout(1200)
    t = pg.evaluate("()=>(document.querySelector('#atlas2 .a3-dbx')||{}).textContent||''")
    ok('scheda db: livello dichiarato e fonti', ('Livello' in t or 'voce essenziale' in t or 'scheda strutturata' in t) and len(t) > 40, t)
    ok('link esterni sicuri', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-dbsrc a')].every(a=>a.rel.includes('noopener')&&a.target==='_blank'&&a.href.startsWith('https://'))"))
    pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'search',q:''}})"); pg.wait_for_timeout(600)
    pg.fill('#atlas2 .a3-in', 'peter'); pg.wait_for_timeout(900)
    ok('ricerca storica invariata', 'Personaggi' in pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sgroup h3')].map(h=>h.firstChild.textContent)"))
    ok('nessun overflow orizzontale', not pg.evaluate("()=>document.documentElement.scrollWidth>innerWidth+1"))
    b.close()
ok('nessun errore JS', not errs, errs)
sys.exit(0 if all(res) else 1)
