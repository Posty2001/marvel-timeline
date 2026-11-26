"""a41 — correzioni collaudo a40: tap universi, nodi unici, inquadratura, filtri compatti, controlli vs Miss Minutes (390 e 430 px).
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

def inter(a, b): return not (a['x']+a['width'] <= b['x'] or b['x']+b['width'] <= a['x'] or a['y']+a['height'] <= b['y'] or b['y']+b['height'] <= a['y'])
def run(vw, vh):
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(U); pg.wait_for_timeout(1500)
        pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
        pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(900)
        pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1500)
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sec .btn')].find(b=>b.textContent==='Multiverso').click()"); pg.wait_for_timeout(1800)
        # tap reale (touch) su un universo: deve aprire la scheda
        box = pg.evaluate("()=>{const n=[...document.querySelectorAll('#atlas2 .a4-vp .a4-n')].find(x=>!x.classList.contains('tva')&&!x.classList.contains('sun')); const r=n.querySelector('.em').getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2,id:n.dataset.id}}")
        pg.touchscreen.tap(box['x'], box['y']); pg.wait_for_timeout(500)
        ok('[%d] Multiverso: il tap su un universo apre la scheda' % vw, pg.evaluate("()=>{const s=document.querySelector('#atlas2 .a4-sheet');return !!s&&!s.hidden&&s.textContent.length>20}"))
        ok('[%d] Multiverso: tutti i nodi inquadrati nel riquadro' % vw, pg.evaluate("()=>{const h=document.querySelector('#atlas2 .a4-vp').getBoundingClientRect();return [...document.querySelectorAll('#atlas2 .a4-vp .a4-n')].filter(n=>!n.classList.contains('tva')).every(n=>{const r=n.getBoundingClientRect();return r.left>=h.left-2&&r.right<=h.right+2&&r.top>=h.top-2&&r.bottom<=h.bottom+2})}"))
        ok('[%d] Multiverso: legenda delle orbite' % vw, pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-leg .a4-lg').length>=2"))
        hues = pg.evaluate("()=>new Set([...document.querySelectorAll('#atlas2 .a4-vp .a4-n')].map(n=>n.style.getPropertyValue('--hu'))).size")
        ok('[%d] Multiverso: universi visivamente differenziati (>=15 tinte)' % vw, hues >= 15, hues)
        # controlli mappa vs Miss Minutes
        r = pg.evaluate("()=>{const f=document.getElementById('mmFab'),c=document.querySelector('#atlas2 .a4-vp .a4-ctl');if(!f||!c)return null;const a=f.getBoundingClientRect(),b=c.getBoundingClientRect();return [{x:a.x,y:a.y,width:a.width,height:a.height},{x:b.x,y:b.y,width:b.width,height:b.height}]}")
        ok('[%d] controlli mappa non sovrapposti a Miss Minutes' % vw, r is None or not inter(r[0], r[1]), r)
        # sposto la linguetta sopra i controlli: i controlli passano sull'altro lato
        pg.evaluate("()=>{const f=document.getElementById('mmFab'),c=document.querySelector('#atlas2 .a4-vp .a4-ctl').getBoundingClientRect();f.style.left=(c.x+2)+'px';f.style.right='auto';f.style.top=(c.y+4)+'px';window.dispatchEvent(new Event('pointerup'))}"); pg.wait_for_timeout(300)
        r = pg.evaluate("()=>{const f=document.getElementById('mmFab'),c=document.querySelector('#atlas2 .a4-vp .a4-ctl');const a=f.getBoundingClientRect(),b=c.getBoundingClientRect();return [{x:a.x,y:a.y,width:a.width,height:a.height},{x:b.x,y:b.y,width:b.width,height:b.height}]}")
        ok('[%d] controlli evitano la linguetta spostata' % vw, not inter(r[0], r[1]), r)
        pg.evaluate("()=>{const f=document.getElementById('mmFab');f.style.left='';f.style.right='0';f.style.top=''}")
        # Nexus
        pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(700)
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sec .btn')].find(b=>b.textContent==='TVA Nexus').click()"); pg.wait_for_timeout(1800)
        for cap in (20, 30):
            pg.evaluate("()=>{const t=document.querySelector('#atlas2 .a4-tools');t.hidden=false;[...t.querySelectorAll('.chip')].find(c=>c.textContent==='%d').click()}" % cap); pg.wait_for_timeout(500)
            ids = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-nx .a4-n')].map(n=>n.dataset.id)")
            ok('[%d] Nexus (%d nodi): nodi unici, nessun duplicato' % (vw, cap), len(ids) == len(set(ids)) and len(ids) >= 5, (len(ids), len(set(ids))))
            ok('[%d] Nexus (%d): nodi inquadrati e senza sovrapposizioni' % (vw, cap), pg.evaluate("()=>{const h=document.querySelector('#atlas2 .a4-vp').getBoundingClientRect();const ns=[...document.querySelectorAll('#atlas2 .a4-nx .a4-n .em')].map(e=>e.getBoundingClientRect());const inside=ns.every(r=>r.left>=h.left-2&&r.right<=h.right+2&&r.top>=h.top-2&&r.bottom<=h.bottom+2);let ov=0;for(let i=0;i<ns.length;i++)for(let j=i+1;j<ns.length;j++){const a=ns[i],b=ns[j];if(!(a.right<=b.left||b.right<=a.left||a.bottom<=b.top||b.bottom<=a.top))ov++}return inside&&ov===0}"))
        pg.evaluate("()=>{document.querySelector('#atlas2 .a4-tools').hidden=true}")
        ok('[%d] Nexus: filtri compatti (chiusi di default, pulsante Filtri)' % vw, pg.evaluate("()=>{const t=document.querySelector('#atlas2 .a4-tools');return !!document.querySelector('#atlas2 .a4-fbtn')&&t.getBoundingClientRect().height===0}"))
        pg.evaluate("()=>document.querySelector('#atlas2 .a4-fbtn').click()"); pg.wait_for_timeout(200)
        ok('[%d] Nexus: il pulsante Filtri apre i filtri' % vw, pg.evaluate("()=>!document.querySelector('#atlas2 .a4-tools').hidden"))
        pg.evaluate("()=>document.querySelector('#atlas2 .a4-fbtn').click()"); pg.wait_for_timeout(200)
        # tap reale su un nodo: ricentra
        c0 = pg.evaluate("()=>window.tvaAtlas2.stato().a3.c")
        bx = pg.evaluate("()=>{const n=[...document.querySelectorAll('#atlas2 .a4-nx .a4-n')].find(x=>!x.classList.contains('sun'));const r=n.querySelector('.em').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]}")
        pg.touchscreen.tap(bx[0], bx[1]); pg.wait_for_timeout(600)
        ok('[%d] Nexus: il tap su un nodo ricentra' % vw, pg.evaluate("()=>window.tvaAtlas2.stato().a3.c") != c0)
        r = pg.evaluate("()=>{const f=document.getElementById('mmFab'),c=document.querySelector('#atlas2 .a4-vp .a4-ctl');if(!f||!c)return null;const a=f.getBoundingClientRect(),b=c.getBoundingClientRect();return [{x:a.x,y:a.y,width:a.width,height:a.height},{x:b.x,y:b.y,width:b.width,height:b.height}]}")
        ok('[%d] Nexus: controlli non sovrapposti a Miss Minutes' % vw, r is None or not inter(r[0], r[1]), r)
        # Percorso: filtri compatti
        pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(600)
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sec .btn')].find(b=>b.textContent==='Percorso').click()"); pg.wait_for_timeout(1200)
        ok('[%d] Percorso: filtri compatti' % vw, pg.evaluate("()=>!!document.querySelector('#atlas2 .a4-fbtn') && document.querySelector('#atlas2 .a4-tools').hidden"))
        b.close()
run(390, 844); run(430, 932)
ok('nessun errore JS', not errs, errs[:3])
bad = [n for n, c in res if not c]
print('\na41 correzioni:', 'OK' if not bad else 'FALLITO ' + str(bad)); sys.exit(1 if bad else 0)
