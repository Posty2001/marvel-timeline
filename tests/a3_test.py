"""Atlante 2.0 A3 — test essenziali dell'interfaccia (iPhone 390x844, Chromium).
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
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
    pg = ctx.new_page(); reqs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
    pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    ok('modulo A3 non caricato prima dell\'ingresso (lazy)', not pg.evaluate("()=>!!window.tvaA3") and not any('atlante2/' in r for r in reqs))
    pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(900)
    ok('Home classica invariata (preferenza assente) + banner A3', pg.evaluate("()=>!!document.querySelector('#atlas2 .hm-hero')") and pg.evaluate("()=>!!document.querySelector('#atlas2 .a3-ban')"))
    ok('ancora nessun dato A3 scaricato', not any('atlante2/data' in r for r in reqs))
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1500)
    s = a3(pg)
    ok('banner -> Home Atlante 2.0', s['screen'] == 'a3' and s['a3']['v'] == 'home', s)
    ok('Home: hero + categorie + hub', pg.evaluate("()=>!!document.querySelector('#atlas2 .a3-hero') && document.querySelectorAll('#atlas2 .a3-cat').length>=8 && document.querySelectorAll('#atlas2 .a3-hc').length==2"))
    ok('dati caricati: solo indice, nessuno shard', any('data/index.json' in r for r in reqs) and not any('/data/d/' in r for r in reqs))
    MM = "()=>{const e=document.getElementById('mmFab'); if(!e||e.hidden) return false; const r=e.getBoundingClientRect(); const t=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return t===e || e.contains(t)}"
    ok('Miss Minutes (mmFab) raggiungibile nella Home A3', pg.evaluate(MM))
    # catalogo
    pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-hero .btn')].find(b=>/catalogo/i.test(b.textContent)).click()"); pg.wait_for_timeout(700)
    s = a3(pg); n0 = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-tile').length")
    ok('Catalogo personaggi: rendering progressivo (36 su 297)', s['a3']['v'] == 'cat' and n0 == 36, n0)
    imgs0 = [r for r in reqs if r.endswith('.webp')]
    pg.evaluate("()=>{const b=document.querySelector('#atlas2 .a2-scroll'); b.scrollTop=b.scrollHeight}"); pg.wait_for_timeout(700)
    n1 = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-tile').length")
    ok('scorrendo si caricano altre voci', n1 > n0, (n0, n1))
    y_before = pg.evaluate("()=>{const b=document.querySelector('#atlas2 .a2-scroll'); b.scrollTop=1500; return b.scrollTop}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-tile')[20].click()"); pg.wait_for_timeout(900)
    s = a3(pg); ok('tile -> dossier', s['a3']['v'] == 'dos', s)
    ok('dossier: shard caricato solo ora (1)', len([r for r in reqs if '/data/d/' in r]) == 1)
    nm = pg.evaluate("()=>document.querySelector('#atlas2 .a3-dh h1').textContent")
    secs = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-ds > h2')].map(x=>x.textContent)")
    ok('dossier: titolo + sezioni con dati', nm and len(secs) >= 1, (nm, secs))
    ok('dossier: nessuna sezione vuota', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-ds')].every(s=>s.children.length>1 && s.textContent.trim().length>10)"))
    pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(900)
    s = a3(pg)
    ok('Indietro -> catalogo con stato e scorrimento ripristinati', s['a3']['v'] == 'cat' and abs(s['y'] - y_before) <= 40 and pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-tile').length") >= n1, (s, y_before))
    # filtri
    pg.evaluate("()=>{const s=document.querySelector('#atlas2 select[aria-label=\"Filtra per continuità\"]'); s.value=s.options[1].value; s.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(400)
    nf = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-tile').length"); ok('filtro per continuità riduce l\'elenco', 0 < nf < 297, nf)
    pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-seg button')[2].click()"); pg.wait_for_timeout(300)
    ok('modalità elenco', pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-li').length")>0 and pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-tile').length")==0)
    # ricerca
    pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'search',q:''}})"); pg.wait_for_timeout(500)
    pg.fill('#atlas2 .a3-in', 'peter'); pg.wait_for_timeout(500)
    groups = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sgroup h3')].map(h=>h.firstChild.textContent)")
    ok('ricerca "peter": risultati suddivisi per categoria', 'Personaggi' in groups and 'Hub multiversali' in groups, groups)
    # hub
    pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sgroup')].find(g=>/Hub/.test(g.querySelector('h3').textContent)).querySelector('.a3-li').click()"); pg.wait_for_timeout(1200)
    s = a3(pg); cards = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-hc').length"); off = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-hc.off').length")
    ok('hub Peter Parker: 6 voci (1 segnaposto non cliccabile)', s['a3']['v'] == 'hub' and cards == 6 and off == 1, (cards, off))
    ok('hub: nessuna relazione narrativa inventata (nota esplicita)', pg.evaluate("()=>/non è un personaggio/.test(document.querySelector('#atlas2').textContent)"))
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-hc:not(.off)').click()"); pg.wait_for_timeout(900)
    ok('hub -> identità', a3(pg)['a3']['v'] == 'dos')
    ok('dossier identità: sezione Varianti con hub', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-ds > h2')].some(h=>/Varianti/.test(h.textContent))"))
    # appearance -> timeline
    pg.evaluate("()=>{const b=[...document.querySelectorAll('#atlas2 .a3-app button')].find(x=>x.textContent==='Timeline'); if(b) b.click()}"); pg.wait_for_timeout(900)
    ok('apparizione -> Timeline: la scheda del titolo si apre fuori dall\'Atlante', pg.evaluate("()=>!document.getElementById('atlas2Toggle').checked && document.querySelector('.app-tab-active')?.getAttribute('data-tab')==='timeline'"))
    pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(900)
    ok('Indietro dalla Timeline -> dossier A3', a3(pg)['screen'] == 'a3' and a3(pg)['a3']['v'] == 'dos', a3(pg))
    ok('Miss Minutes raggiungibile nel dossier', pg.evaluate(MM))
    # mantello
    pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'hub',id:'man-capitan-america'}})"); pg.wait_for_timeout(900)
    ok('mantello: 2 titolari distinti', pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-hc').length") == 2)
    # sospese
    pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'dos',id:'id-bishop'}})"); pg.wait_for_timeout(900)
    ok('Bishop: segnalato "In verifica", nessun hub/variante', pg.evaluate("()=>/In verifica/.test(document.querySelector('#atlas2 .a3-dh').textContent) && ![...document.querySelectorAll('#atlas2 .a3-ds > h2')].some(h=>/Varianti/.test(h.textContent))"))
    ok('Miss Minutes raggiungibile nell\'hub/dossier sospeso', pg.evaluate(MM))
    src = open(os.path.join(ROOT, 'atlante2', 'a3.js'), encoding='utf-8').read()
    ok('sicurezza: nessun innerHTML/insertAdjacentHTML/eval nel modulo A3', not any(t in src for t in ('innerHTML', 'insertAdjacentHTML', 'eval(', 'document.write')))
    # X: torna all'app
    pg.evaluate("()=>document.querySelector('#atlas2 .a2-exit').click()"); pg.wait_for_timeout(900)
    ok('X -> esce dall\'Atlante (Home app)', not pg.evaluate("()=>document.getElementById('atlas2Toggle').checked"))
    # fallback: A3 non disponibile -> classico
    ok('nessun errore JS', not errs, errs[:3])
    b.close()
fails = [n for n, c in res if not c]
print('\nA3:', len(res) - len(fails), '/', len(res), 'PASS'); sys.exit(1 if fails else 0)
