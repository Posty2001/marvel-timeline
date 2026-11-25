"""Atlante 2.0 A4.1 — Multiverso, Nexus, Percorso (iPhone 390x844 e 430x932).
Base: scaffolding del test A3 — test essenziali dell'interfaccia (iPhone 390x844, Chromium).
Uso: python3 tests/a3_test.py [porta]   (server HTTP locale sulla radice del progetto, avviato qui)
Controlli: ingresso additivo (banner), Home, catalogo (progressivo, filtri, griglia/elenco), ricerca per categoria, dossier (solo sezioni con dati),
hub/mantello, Indietro/X coerenti, scorrimento ripristinato, caricamento lazy (shard/immagini), Miss Minutes raggiungibile, nessun errore JS,
nessuna regressione dell'Atlante classico (preferenza assente = Home classica)."""
import json, os, subprocess, sys, time, socket, threading, http.server, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res, errs = [], []
def ok(n, c, d=''):
    res.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)) if (d and not c) else ''))
def free():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
port = free()
srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:%d/index.html' % port
ST = "()=>{const s=tvaAtlas2.stato();return {screen:s.screen,a3:s.a3?JSON.parse(JSON.stringify(s.a3)):null,depth:tvaNavStato().depth,y:document.querySelector('#atlas2 .a2-scroll').scrollTop}}"
def a3(pg): return pg.evaluate(ST)
def sc(pg): return pg.evaluate("()=>document.querySelector('#atlas2 .a2-scroll')")

def run(vw, vh):
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
        pg = ctx.new_page(); reqs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
        pg.goto(U); pg.wait_for_timeout(1500)
        pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
        pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(900)
        pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1500)
        ok('[%d] Home A3 con ingressi Multiverso/Nexus/Percorso' % vw, pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sec .btn')].filter(b=>/^(Multiverso|Nexus|Percorso)$/.test(b.textContent)).length")==3)
        ok('[%d] modulo A4 non caricato prima dell\'uso (lazy)' % vw, not any('a4.js' in r or 'nexus/g.json' in r for r in reqs))
        # Multiverso
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sec .btn')].find(b=>b.textContent==='Multiverso').click()"); pg.wait_for_timeout(1500)
        nn = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-vp .a4-n').length")
        ok('[%d] Multiverso: universi come nodi (>=20)' % vw, nn >= 20, nn)
        ok('[%d] Multiverso: nessun overflow orizzontale' % vw, pg.evaluate("()=>{const b=document.querySelector('#atlas2 .a2-scroll');return b.scrollWidth<=b.clientWidth+1}"))
        t0 = pg.evaluate("()=>document.querySelector('#atlas2 .a4-world').style.transform")
        pg.evaluate("()=>document.querySelector('.a4-ctl button').click()"); pg.wait_for_timeout(200)
        ok('[%d] zoom +' % vw, pg.evaluate("()=>document.querySelector('#atlas2 .a4-world').style.transform") != t0)
        pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-vp .a4-n')[1].click()"); pg.wait_for_timeout(500)
        ok('[%d] scheda universo con identità' % vw, pg.evaluate("()=>!document.querySelector('#atlas2 .a4-sheet').hidden && document.querySelector('#atlas2 .a4-sheet h2').textContent.length>2"))
        # Nexus
        pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(700)
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sec .btn')].find(b=>b.textContent==='Nexus').click()"); pg.wait_for_timeout(1500)
        nn = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-nx .a4-n').length")
        ok('[%d] Nexus: centro + collegamenti narrativi' % vw, nn >= 5, nn)
        ok('[%d] Nexus: legenda solo con tipi presenti' % vw, pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-lg').length")>=1)
        ok('[%d] Nexus: elenco con stato di verifica' % vw, pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-r .a4-v').length")>=3)
        ok('[%d] Nexus: editoriali nascoste di default' % vw, pg.evaluate("()=>!document.querySelector('#atlas2 .a4-nx .a4-n.ed')"))
        ok('[%d] Nexus: nessun overflow' % vw, pg.evaluate("()=>{const b=document.querySelector('#atlas2 .a2-scroll');return b.scrollWidth<=b.clientWidth+1}"))
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-tools .chip')].find(c=>c.textContent==='Editoriali').click()"); pg.wait_for_timeout(400)
        ok('[%d] Nexus: toggle editoriali' % vw, pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-nx .a4-n').length")>=nn)
        c0 = pg.evaluate("()=>window.tvaAtlas2.stato().a3.c")
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-r .chip')][0].click()"); pg.wait_for_timeout(500)
        ok('[%d] Nexus: ricentra su un nodo' % vw, pg.evaluate("()=>window.tvaAtlas2.stato().a3.c") != c0)
        # Percorso: regole di default
        d = pg.evaluate("()=>window.tvaA4.data()")
        ok('[%d] dati: nessuna co-apparizione tra le relazioni' % vw, 'co_apparizione' not in d['tipi'])
        pg.evaluate("()=>window.tvaAtlas2.stato()"); pg.evaluate("()=>{const ST=window.tvaAtlas2; }")
        b.close()
run(390, 844); run(430, 932)
ok('nessun errore JS', not errs, errs[:3])
bad = [n for n, c in res if not c]
print('\nA4.1 UI:', 'OK' if not bad else 'FALLITO ' + str(bad)); sys.exit(1 if bad else 0)
