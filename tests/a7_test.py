"""A7 — rifinitura finale e ottimizzazione iPad. Viewport: iPhone 390x844 (invariato), iPhone orizzontale 844x390, iPad 820x1180 / 1180x820 / 1024x1366, Split View stretta 507x1180 e ridimensionamento.
Uso: python3 tests/a7_test.py"""
import os, socket, threading, http.server, functools, json, time
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res, errs = [], []
def ok(n, c, d=''):
    res.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)) if (d and not c) else ''))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def handle(self):
        try: super().handle()
        except Exception: pass
s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:%d/index.html' % port
OVF = "()=>document.documentElement.scrollWidth<=innerWidth+1"
def boot(b, w, h, mobile):
    c = b.new_context(viewport={'width': w, 'height': h}, has_touch=True, is_mobile=mobile, service_workers='block')
    c.add_init_script("localStorage.setItem('tva-atlante-ui','v2')")
    pg = c.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(U); pg.wait_for_timeout(3000)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(700)
    return c, pg
def tab(pg, t): pg.evaluate("(t)=>document.getElementById('appTab'+t).click()", t); pg.wait_for_timeout(1300)
def nav(pg, a): pg.evaluate("(a)=>window.tvaA3.ctx().api.nav('a3',{a3:eval('('+a+')')})", a); pg.wait_for_timeout(1500)
def metrics(pg):
    return pg.evaluate("""()=>{const q=s=>document.querySelector(s),r=e=>e?e.getBoundingClientRect():null;
      const it=[...document.querySelectorAll('.part ul.items > li.card-wrap')].filter(e=>e.offsetWidth>0).slice(0,4).map(e=>Math.round(e.getBoundingClientRect().left)).filter((v,i,a)=>a.indexOf(v)===i).length;
      const hub=q('#homeHub .home-hub-inner');
      return {items:it, hubW:hub?Math.round(r(hub).width):0}}""")
with sync_playwright() as p:
    b = p.chromium.launch()
    shots = {}
    for name, w, h, mobile in [('iPhone', 390, 844, True), ('iPhone-orizz', 844, 390, True), ('Split-stretta', 507, 1180, False), ('iPad-vert', 820, 1180, False), ('iPad-orizz', 1180, 820, False), ('iPadPro', 1024, 1366, False)]:
        c, pg = boot(b, w, h, mobile); tablet = w >= 768 and h >= 600
        # schermate principali: nessun overflow orizzontale
        for t in ['Home', 'Timeline', 'Missioni']:
            tab(pg, t); ok('%s · %s: nessun overflow orizzontale' % (name, t), pg.evaluate(OVF))
            if t == 'Home': m = metrics(pg); ok('%s · Home: colonna %s' % (name, 'ampia (tablet)' if tablet else 'stretta invariata'), (m['hubW'] > 600) if tablet else (m['hubW'] <= 440), m)
            if t == 'Timeline': m = metrics(pg); ok('%s · Timeline: %s' % (name, 'schede su più colonne' if tablet else 'una colonna invariata'), (m['items'] >= 2) if tablet else (m['items'] <= 1), m)
        # Atlas
        tab(pg, 'Atlante'); pg.wait_for_timeout(1500)
        pg.evaluate("()=>window.__ids=window.tvaA3.ctx().IDX.voci.filter(v=>v.t==='p'&&v.k!=='c').map(v=>v.i)")
        for k, a in [('Catalogo', "{v:'cat',t:'p',m:'g',n:60}"), ('Osservatorio', "{v:'mv'}"), ('Nexus', "{v:'nx',c:'id-iron-man'}"), ('Percorso', "{v:'pc',a:'',b:'',m:'n'}"), ('Progressione', "{v:'pr'}"), ('Preferiti', "{v:'pf'}")]:
            nav(pg, a); ok('%s · %s: nessun overflow orizzontale' % (name, k), pg.evaluate("()=>{const s=document.querySelector('#atlas2 .a2-scroll');return !s||s.scrollWidth<=s.clientWidth+1}"))
            if k == 'Nexus':
                cols = pg.evaluate("()=>{const r=document.querySelector('#atlas2 .a4-root');return r?getComputedStyle(r).gridTemplateColumns.split(' ').length:0}")
                ok('%s · Nexus: %s' % (name, 'mappa + pannello laterale' if tablet else 'una colonna invariata'), (cols == 2) if tablet else (cols <= 1), cols)
        pg.evaluate("()=>window.tvaA3.open(window.__ids[3])"); pg.wait_for_timeout(2200)
        d = pg.evaluate("""()=>{const s=document.querySelector('#atlas2 .a3-side'),m=document.querySelector('#atlas2 .a3-main');if(!s||!m)return null;const a=s.getBoundingClientRect(),b=m.getBoundingClientRect();return {sideL:Math.round(a.left),mainL:Math.round(b.left),sideW:Math.round(a.width),disp:getComputedStyle(s).display}}""")
        if tablet: ok('%s · Dossier: ritratto/azioni e informazioni affiancati' % name, d and d['mainL'] > d['sideL'] + d['sideW'] - 5 and d['sideW'] >= 250, d)
        else: ok('%s · Dossier: contenitori trasparenti, layout telefono' % name, d and d['disp'] == 'contents', d)
        ok('%s · Dossier: nessun overflow' % name, pg.evaluate("()=>{const s=document.querySelector('#atlas2 .a2-scroll');return s.scrollWidth<=s.clientWidth+1}"))
        if w >= 1180 and h >= 600:
            ok('%s · Atlas: barra laterale della guida non copre il contenuto' % name, pg.evaluate("()=>{const sb=document.querySelector('nav.sidebar');const r=sb.getBoundingClientRect();return r.right<=1||getComputedStyle(sb).visibility==='hidden'}"))
        # Miss Minutes: solo grafica, host intatto
        pg.evaluate("()=>window.tvaMissMinutesHost.show()"); pg.wait_for_timeout(2200)
        ok('%s · Miss Minutes: overlay a schermo intero e senza overflow' % name, pg.evaluate("()=>{const o=document.getElementById('mmOverlay')||document.querySelector('.mm-ov, #mmHost');const f=document.querySelector('iframe[title=\"Miss Minutes\"]');if(!f)return false;const r=f.getBoundingClientRect();return r.width>=innerWidth-1&&r.height>=100}"))
        pg.evaluate("()=>window.tvaMissMinutesHost.close()")
        # Tessera / Friends (overlay)
        for t in ['Tessera', 'Friends']:
            tab(pg, t); ok('%s · %s: nessun overflow orizzontale' % (name, t), pg.evaluate(OVF))
        if name == 'iPad-vert':
            # ridimensionamento finestra / Split View: da tablet a stretto e ritorno
            pg.set_viewport_size({'width': 507, 'height': 1180}); pg.wait_for_timeout(600)
            tab(pg, 'Timeline'); m = metrics(pg); ok('Ridimensionamento → Split View stretta: Timeline torna a una colonna', m['items'] <= 1, m)
            pg.set_viewport_size({'width': 1180, 'height': 820}); pg.wait_for_timeout(600)
            m = metrics(pg); ok('Ridimensionamento → orizzontale: schede su più colonne', m['items'] >= 2, m)
        c.close()
    # prestazioni iPhone: apertura catalogo (315 voci) e dossier sotto soglia
    c, pg = boot(b, 390, 844, True); tab(pg, 'Atlante'); pg.wait_for_timeout(1500)
    t0 = time.time(); nav(pg, "{v:'cat',t:'p',m:'g',n:60}"); dt = time.time() - t0
    ok('iPhone: catalogo aperto entro 4 s (inclusa attesa di 1,5 s)', dt < 4, round(dt, 2))
    lt = pg.evaluate("()=>new Promise(r=>{let n=0;const o=new PerformanceObserver(l=>{l.getEntries().forEach(e=>n=Math.max(n,e.duration))});try{o.observe({type:'longtask',buffered:true})}catch(e){}setTimeout(()=>r(n),500)})")
    ok('iPhone: nessun long task > 700 ms dopo l’apertura del catalogo', lt < 700, lt)
    # testi tecnici visibili
    tab(pg, 'Atlante'); nav(pg, "{v:'home'}"); t = pg.inner_text('#atlas2')
    bad = [x for x in ['pilota', 'A3.1', 'ANTEPRIMA', 'Anteprima A3', 'collaudo', 'IndexedDB', 'registro dati', 'Atlante 2.0'] if x.lower() in t.lower()]
    ok('Home TVA Atlas: nessun riferimento tecnico/di sviluppo visibile', not bad, bad)
    nav(pg, "{v:'rit'}"); t = pg.inner_text('#atlas2'); bad = [x for x in ['Pilota', 'A3.1', 'prototipo'] if x.lower() in t.lower()]
    ok('Ritratti privati: nessun riferimento tecnico visibile', not bad, bad)
    # dati personali non toccati
    ok('Nessun errore di pagina', not errs, errs[:2])
    b.close()
n = sum(1 for _, c in res if c); print('\nA7: %d / %d PASS' % (n, len(res)))
raise SystemExit(0 if n == len(res) else 1)
