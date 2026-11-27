#!/usr/bin/env python3
# mm2e.1 - viewport mobile (iOS): overlay sempre a schermo intero, nessuna esposizione della pagina sotto, scroll preservato.
import functools, http.server, os, socketserver, threading
from playwright.sync_api import sync_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Q, directory=ROOT)); srv.daemon_threads = True; threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
res = []
def ok(n, c, x=''): res.append((n, bool(c))); print('PASS' if c else 'FAIL', n, x)
FAKE = """(()=>{const vv=new EventTarget();vv.offsetTop=0;vv.offsetLeft=0;vv.width=390;vv.height=800;vv.scale=1;
Object.defineProperty(window,'visualViewport',{value:vv,configurable:true});
window.__vv=(top,h)=>{vv.offsetTop=top;vv.height=h;vv.dispatchEvent(new Event('resize'));vv.dispatchEvent(new Event('scroll'))};})()"""
START = "()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 800}, has_touch=True, is_mobile=True)
    ctx.add_init_script(FAKE)
    ctx.add_init_script("if(!localStorage.getItem('marvel-ultimate-timeline-watched'))localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify({'001':true}))")
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + '/index.html', wait_until='load'); pg.wait_for_timeout(1300); pg.evaluate(START); pg.wait_for_timeout(500)
    # posizione originale della pagina
    pg.evaluate("()=>{const s=document.scrollingElement;document.body.style.minHeight='4000px';s.scrollTop=250}"); pg.wait_for_timeout(200); y0 = pg.evaluate("()=>document.scrollingElement.scrollTop")
    y0 = pg.evaluate("()=>{const y=document.scrollingElement.scrollTop;window.tvaMissMinutesHost.show();return y}"); pg.wait_for_timeout(700)
    fr = [f for f in pg.frames if 'miss-minutes' in f.url][0]; fr.wait_for_function("()=>window.__mm&&window.__mm.engine", timeout=10000)
    geo = lambda: pg.evaluate("()=>{const o=document.getElementById('mmOverlay').getBoundingClientRect(),f=document.querySelector('#mmOverlay iframe').getBoundingClientRect();return {ot:o.top,ob:o.bottom,ol:o.left,or:o.right,ft:f.top,fb:f.bottom,ih:innerHeight,iw:innerWidth,cs:getComputedStyle(document.getElementById('mmOverlay')).backgroundColor,z:document.elementFromPoint(195,5).id+'|'+document.elementFromPoint(195,795).id,mo:document.documentElement.classList.contains('mm-open')}}")
    def full(g): return g['ot'] == 0 and abs(g['ob'] - g['ih']) < 1 and g['ol'] == 0 and abs(g['or'] - g['iw']) < 1 and g['cs'] != 'rgba(0, 0, 0, 0)' and g['z'].split('|')[0] == 'mmOverlay' or g['z'].split('|')[0] == ''
    g = geo(); ok('apertura: overlay a tutto schermo, sfondo opaco, pagina bloccata', g['ot'] == 0 and abs(g['ob'] - g['ih']) < 1 and g['cs'] == 'rgb(6, 4, 3)' and g['mo'], g)
    ok('apertura: iframe a schermo intero', g['ft'] == 0 and abs(g['fb'] - g['ih']) < 1, g)
    # tastiera aperta: visualViewport ridotto e traslato
    pg.evaluate("()=>window.__vv(120,400)"); pg.wait_for_timeout(120); g = geo()
    ok('tastiera: iframe segue il visualViewport (top 120, h 400)', abs(g['ft'] - 120) < 1 and abs(g['fb'] - 520) < 1, g)
    ok('tastiera: overlay resta a schermo intero (nessuno spazio vuoto, nessuna pagina visibile)', g['ot'] == 0 and abs(g['ob'] - g['ih']) < 1 and g['cs'] == 'rgb(6, 4, 3)', g)
    ok('tastiera: nei punti scoperti dall\'iframe c\'e\' sempre l\'overlay, mai la pagina', all(pg.evaluate("(y)=>document.elementFromPoint(195,y).closest('#mmOverlay')!==null", y) for y in (2, 60, 700, 797)))
    # sequenza rapida di transizioni (Invia: la tastiera si chiude mentre la risposta arriva) senza stati intermedi esposti
    for t, h in [(120, 400), (60, 520), (20, 640), (5, 760), (0, 800)]:
        pg.evaluate("([t,h])=>window.__vv(t,h)", [t, h]); pg.wait_for_timeout(16)
        gi = geo(); ok('transizione %d/%d: overlay sempre a schermo intero' % (t, h), gi['ot'] == 0 and abs(gi['ob'] - gi['ih']) < 1 and gi['cs'] == 'rgb(6, 4, 3)')
    pg.wait_for_timeout(700); g = geo(); ok('dopo l\'assestamento: iframe di nuovo a schermo intero', g['ft'] == 0 and abs(g['fb'] - g['ih']) < 1, g)
    # scroll della pagina ospite provocato da iOS: l'overlay non si sposta
    pg.evaluate("()=>{document.scrollingElement.scrollTop=900;window.dispatchEvent(new Event('scroll'))}"); pg.wait_for_timeout(100); g = geo()
    ok('scroll della pagina sotto: overlay immobile', g['ot'] == 0 and abs(g['ob'] - g['ih']) < 1, g)
    # documento dell'assistente non scorrevole
    d = fr.evaluate("()=>{const s=document.scrollingElement;s.scrollTop=300;return {st:s.scrollTop,ho:getComputedStyle(document.documentElement).overflow,bp:getComputedStyle(document.body).position}}")
    ok('iframe: documento non scorrevole (html overflow hidden, body fixed)', d['st'] == 0 and d['ho'] == 'hidden' and d['bp'] == 'fixed', d)
    # scroll della conversazione preservato alla chiusura/riapertura
    fr.evaluate("()=>{window.__mm.go('chat');const c=document.getElementById('mmChat');const f=document.createElement('div');f.id='fill';f.style.height='3000px';c.appendChild(f);c.scrollTop=420}"); fr.wait_for_timeout(200)
    pg.evaluate("()=>window.__vv(0,800)")
    pg.evaluate("()=>window.tvaMissMinutesHost.close()"); pg.wait_for_timeout(500); g = geo()
    ok('chiusura: classe mm-open rimossa e overlay nascosto', not g['mo'] and pg.evaluate("()=>getComputedStyle(document.getElementById('mmOverlay')).display") == 'none', g)
    y1 = pg.evaluate("()=>document.scrollingElement.scrollTop")
    ok('chiusura: posizione originale della pagina preservata', y1 == y0, (y0, y1))
    pg.evaluate("()=>window.tvaMissMinutesHost.show()"); pg.wait_for_timeout(500)
    cs = fr.evaluate("()=>document.getElementById('mmChat').scrollTop")
    ok('riapertura: scroll della conversazione preservato', abs(cs - 420) < 3, cs)
    g = geo(); ok('riapertura: di nuovo a schermo intero', g['ot'] == 0 and g['ft'] == 0 and abs(g['fb'] - g['ih']) < 1, g)
    ok('nessun errore di pagina', not errs, errs[:2])
fails = [n for n, c in res if not c]; print('\n%d/%d' % (len(res) - len(fails), len(res))); raise SystemExit(1 if fails else 0)
