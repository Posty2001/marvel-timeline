"""a42 (build consolidata) — Osservatorio in Home, catalogo universi, barra categorie, Nexus (nomi, alias, relazioni multiple, trail, filtri tipo).
Uso: python3 tests/a43_test.py   (Chromium con emulazione iPhone 390/430 px; WebKit non disponibile nell'ambiente)"""
import os, socket, threading, http.server, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res, errs = [], []
def ok(n, c, d=''):
    res.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)) if (d and not c) else ''))
def free():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
port = free(); srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:%d/index.html' % port
SCR = "document.querySelector('#atlas2 .a2-scroll')"
CH = "document.querySelector('#atlas2 .a3 .chips')"
def go(pg, js, w=900): pg.evaluate(js); pg.wait_for_timeout(w)
def boot(b, vw, vh):
    ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    go(pg, "()=>document.getElementById('a2Entry').click()"); go(pg, "()=>document.querySelector('#atlas2 .a3-ban').click()", 1500); return pg
def run(vw, vh):
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = boot(b, vw, vh); T = '[%d] ' % vw
        # ---- Home: Osservatorio
        r = pg.evaluate("()=>{const x=document.querySelector('#atlas2 .a3-obsbtn');if(!x)return null;const b=x.getBoundingClientRect();return {top:b.top,h:b.height,txt:x.textContent}}")
        ok(T + 'Home: pulsante «Osservatorio del Multiverso» visibile senza scorrere', r and r['top'] < vh - 60 and r['h'] >= 44 and 'Osservatorio del Multiverso' in r['txt'], r)
        ok(T + 'Home: hero compatta (<=335 px) e riga pulsanti senza overflow', pg.evaluate("()=>{const h=document.querySelector('#atlas2 .a3-hero').getBoundingClientRect().height,r=document.querySelector('#atlas2 .a3-hrow');return h<=335&&r.scrollWidth<=r.clientWidth+1}"))
        ok(T + 'Home: Atlante classico ancora raggiungibile', pg.evaluate("()=>!![...document.querySelectorAll('#atlas2 .btn')].find(b=>b.textContent==='Atlante classico')"))
        ok(T + 'Home: portale compatto Osservatorio (130-150 px), miniatura a sinistra, titolo a destra, tutta la scheda cliccabile', pg.evaluate("()=>{const o=document.querySelector('#atlas2 [data-portal=mv]');if(!o||o.tagName!=='BUTTON')return false;const r=o.getBoundingClientRect(),m=o.querySelector('svg.a3-obs-svg circle'),t=o.querySelector('.a3-pt-t b');if(!m||!t)return false;const mr=o.querySelector('.a3-pt-map').getBoundingClientRect(),tr=t.getBoundingClientRect();return r.height>=125&&r.height<=150&&mr.right<=tr.left+1&&/Osservatorio/.test(t.textContent)&&!/catalogo/i.test(o.textContent)&&o.textContent.length<90}"))
        ok(T + 'Home: Nexus e Percorsi come due portali compatti affiancati', pg.evaluate("()=>{const a=document.querySelector('#atlas2 [data-portal=nx]'),b=document.querySelector('#atlas2 [data-portal=pc]');if(!a||!b)return false;const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();return Math.abs(x.top-y.top)<2&&x.right<=y.left+1&&x.height<=90&&y.height<=90&&x.left>=0&&y.right<=innerWidth&&document.documentElement.scrollWidth<=innerWidth}"))
        ok(T + 'Home: titolo sezione «Hub di identità» (nessun «Hub multiversali»)', pg.evaluate("()=>{const t=document.querySelector('#atlas2').innerText;return /Hub di identità/.test(t)&&!/Hub multiversal/i.test(t)}"))
        go(pg, "()=>document.querySelector('#atlas2 .a3-obsbtn').click()", 1800)
        n = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-vp .a4-n').length"); ok(T + 'Osservatorio raggiungibile dalla Home: mappa con universi come nodi', n >= 20, n)
        ok(T + 'Osservatorio: titolo «Osservatorio del Multiverso»', pg.evaluate("()=>/Osservatorio del Multiverso/.test(document.querySelector('#atlas2').innerText)"))
        # etichette universi: nome breve + Terra-N, senza parole spezzate
        bad = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-vp .a4-n .lb')].filter(l=>l.scrollWidth>l.clientWidth+1||/\\u00AD/.test(l.textContent)).map(l=>[l.textContent,l.scrollWidth,l.clientWidth])")
        ok(T + 'Mappa: etichette senza parole spezzate o tagliate', not bad, bad[:3])
        hue_map = pg.evaluate("()=>{const n=document.querySelector('#atlas2 .a4-n[data-id=\"uni-earth-96283-raimi-verse\"]');return n&&n.style.getPropertyValue('--hu')}")
        # ---- Catalogo universi
        pg.evaluate("()=>history.back()"); pg.wait_for_timeout(600)
        go(pg, "()=>{tvaAtlas2.setState({screen:'a3',a3:{v:'cat',t:'U',m:'g',n:36}})}", 1500)
        ok(T + 'Catalogo universi: banner verso l\'Osservatorio', pg.evaluate("()=>!!document.querySelector('#atlas2 .a3-obsnote .btn')"))
        d = pg.evaluate("""()=>{const ts=[...document.querySelectorAll('#atlas2 .a3-tile.t-U')];return ts.map(t=>({n:t.querySelector('.t b').textContent,c:(t.querySelector('.t .cls')||{}).textContent||'',hu:t.style.getPropertyValue('--hu'),
          txt:[...t.querySelectorAll('svg text')].map(x=>{const bb=x.getBBox();return {t:x.textContent,x:bb.x,w:bb.width}}),par:(t.querySelector('svg')||{getAttribute(){}}).getAttribute('preserveAspectRatio')}))}""")
        ok(T + 'Catalogo universi: nome completo in vista grande (es. «Terra-199999 · MCU»)', any(x['n'] == 'Terra-199999 · MCU' for x in d), [x['n'] for x in d][:4])
        ok(T + 'Catalogo universi: classificazione separata dal nome', sum(1 for x in d if x['c']) >= 15 and all(x['c'] != x['n'] for x in d), [(x['n'], x['c']) for x in d][:3])
        ok(T + 'Catalogo universi: numeri interi (testo emblema dentro il riquadro, scala senza ritaglio)', all(all(t['x'] >= 0 and t['x'] + t['w'] <= 160 for t in x['txt']) and x['par'] == 'xMidYMid meet' for x in d), [x for x in d if x['txt']][:1])
        ok(T + 'Catalogo universi: tinte diverse tra universi (>=15)', len(set(x['hu'] for x in d)) >= 15, len(set(x['hu'] for x in d)))
        hue_tile = next((x['hu'] for x in d if 'Raimi' in x['n']), None)
        ok(T + 'Colori coerenti tra catalogo e mappa (stessa tinta per lo stesso universo)', hue_tile and hue_tile == hue_map, (hue_tile, hue_map))
        ok(T + 'Catalogo universi: nessun overflow orizzontale', pg.evaluate("()=>{const b=" + SCR + ";return b.scrollWidth<=b.clientWidth+1}"))
        # ---- Barra categorie: posizione orizzontale
        go(pg, "()=>{tvaAtlas2.setState({screen:'a3',a3:{v:'cat',t:'p',m:'c',n:36}})}", 1500)
        ov = pg.evaluate("()=>{const c=" + CH + ";return c.scrollWidth>c.clientWidth+40}"); ok(T + 'Barra categorie scorrevole (contenuto piu\' largo dello schermo)', ov)
        pg.evaluate("()=>{" + CH.replace('document', 'document') + ".scrollLeft=300}"); pg.wait_for_timeout(200)
        before = pg.evaluate("()=>" + CH + ".scrollLeft")
        # tocca una categoria visibile (non la prima)
        pg.evaluate("()=>{const c=" + CH + ";const r=c.getBoundingClientRect();const k=[...c.querySelectorAll('.chip')].find(x=>{const b=x.getBoundingClientRect();return b.left>r.left+20&&b.right<r.right-20&&!x.classList.contains('on')});k.click()}"); pg.wait_for_timeout(900)
        s1 = pg.evaluate("()=>{const c=" + CH + ";const on=c.querySelector('.chip.on'),r=c.getBoundingClientRect(),b=on.getBoundingClientRect();return {x:c.scrollLeft,vis:b.left>=r.left-1&&b.right<=r.right+1,t:on.textContent}}")
        ok(T + 'Cambio categoria: la barra NON torna all\'inizio', s1['x'] > 100, (before, s1))
        ok(T + 'Cambio categoria: categoria selezionata evidenziata e interamente visibile', s1['vis'], s1)
        # campioni durante il render: nessun reset a 0
        pg.evaluate("()=>{const c=" + CH + ";window.__cx=[];const f=()=>{const q=" + CH + ";if(q)window.__cx.push(q.scrollLeft);if(window.__cx.length<90)requestAnimationFrame(f)};f()}")
        pg.evaluate("()=>{const c=" + CH + ";const r=c.getBoundingClientRect();const k=[...c.querySelectorAll('.chip')].find(x=>{const b=x.getBoundingClientRect();return b.left>r.left+10&&b.right<r.right-10&&!x.classList.contains('on')});if(k)k.click()}"); pg.wait_for_timeout(1500)
        cx = pg.evaluate("()=>window.__cx"); ok(T + 'Nessuno scatto: la posizione non passa mai da 0 durante il rendering', min(cx[3:]) > 60, (min(cx[3:]), cx[:12]))
        # vista e filtri
        x0 = pg.evaluate("()=>" + CH + ".scrollLeft")
        for lab in ['Griglia grande', 'Elenco', 'Griglia compatta']:
            pg.evaluate("(l)=>document.querySelector('#atlas2 .a3-seg button[aria-label=\"'+l+'\"]').click()", lab); pg.wait_for_timeout(350)
            ok(T + 'Cambio vista «%s»: posizione barra invariata' % lab, abs(pg.evaluate("()=>" + CH + ".scrollLeft") - x0) <= 2)
        # dossier e ritorno
        pg.evaluate("()=>{const i=document.querySelector('#atlas2 .a3-in');i.value='a';i.dispatchEvent(new Event('input',{bubbles:true}))}"); pg.wait_for_timeout(500)
        st0 = pg.evaluate("()=>{const s=tvaAtlas2.stato().a3;return {t:s.t,q:s.q,x:" + CH + ".scrollLeft}}")
        go(pg, "()=>document.querySelector('#atlas2 .a3-tile').click()", 1200)
        ok(T + 'Dossier aperto dal catalogo', pg.evaluate("()=>['dos','hub'].includes(tvaAtlas2.stato().a3.v)"))
        go(pg, "()=>history.back()", 1500)
        st1 = pg.evaluate("()=>{const s=tvaAtlas2.stato().a3;return {v:s.v,t:s.t,q:s.q,x:" + CH + ".scrollLeft,on:" + CH + ".querySelector('.chip.on').textContent,inp:document.querySelector('#atlas2 .a3-in').value}}")
        ok(T + 'Ritorno dal dossier: categoria, filtro di testo e scorrimento orizzontale ripristinati', st1['v'] == 'cat' and st1['t'] == st0['t'] and st1['q'] == 'a' and st1['inp'] == 'a' and abs(st1['x'] - st0['x']) <= 4, (st0, st1))
        pg.close()
        # ---- Nexus
        pg = boot(b, vw, vh)
        go(pg, "()=>tvaAtlas2.setState({screen:'a3',a3:{v:'nx',c:'id-iron-man'}})", 2200)
        lab = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-nx .a4-n')].map(n=>({id:n.dataset.id,l:n.querySelector('.lb').firstChild.textContent,s:(n.querySelector('.lb small')||{}).textContent||'',w:n.querySelector('.lb').scrollWidth,cw:n.querySelector('.lb').clientWidth,h:n.querySelector('.lb').scrollHeight,ch:n.querySelector('.lb').clientHeight,title:n.title}))")
        ok(T + 'Nexus: nodi con nome breve (<=18 caratteri) e nome completo nel titolo', all(len(x['l']) <= 18 for x in lab) and any(x['title'] != x['l'] for x in lab), [x['l'] for x in lab if len(x['l']) > 18])
        ok(T + 'Nexus: nessuna parola spezzata (etichette non tagliate)', all(x['w'] <= x['cw'] + 1 and x['h'] <= x['ch'] + 1 for x in lab), [x for x in lab if x['w'] > x['cw'] + 1 or x['h'] > x['ch'] + 1][:2])
        ls = [(x['l'], x['s']) for x in lab]; ok(T + 'Nexus: nessun nodo con etichetta identica a un altro (alias distinti)', len(set(ls)) == len(ls), [k for k in ls if ls.count(k) > 1][:3])
        # Iron Man ↔ Steve Rogers: relazioni multiple
        row = pg.evaluate("()=>{const r=[...document.querySelectorAll('#atlas2 .a4-r')].find(r=>/Steve Rogers/.test(r.querySelector('.chip').textContent));return r?[...r.querySelectorAll('.a4-rl1 .s')].map(x=>x.textContent):null}")
        ok(T + 'Nexus: Iron Man–Steve Rogers mostra TUTTE le relazioni documentate (non solo rivalità)', row and any('Rivalit' in t for t in row) and any('Amicizia' in t for t in row), row)
        nl = pg.evaluate("()=>{const s=[...document.querySelectorAll('#atlas2 .a4-edges line')];return s.length}"); nodes = len(lab) - 1
        ok(T + 'Nexus: archi paralleli per le relazioni multiple (linee > nodi)', nl > nodes, (nl, nodes))
        # Percorso esplorato (trail) + filtro per tipo
        ok(T + 'Nexus: filtri per tipo di relazione disponibili', pg.evaluate("()=>{const t=document.querySelector('#atlas2 .a4-tools');t.hidden=false;return [...t.querySelectorAll('.chip')].some(c=>/Rivalit/.test(c.textContent))}"))
        n0 = pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-r').length")
        pg.evaluate("()=>{const t=document.querySelector('#atlas2 .a4-tools');[...t.querySelectorAll('.chip')].find(c=>/^Rivalit/.test(c.textContent)).click()}"); pg.wait_for_timeout(400)
        ok(T + 'Nexus: nascondere «Rivalità» rimuove solo quel tipo (Steve resta con Amicizia)', pg.evaluate("()=>{const r=[...document.querySelectorAll('#atlas2 .a4-r')].find(r=>/Steve Rogers/.test(r.querySelector('.chip').textContent));return !!r&&!/Rivalit/.test(r.textContent)&&/Amicizia/.test(r.textContent)}"))
        pg.evaluate("()=>{const t=document.querySelector('#atlas2 .a4-tools');t.hidden=false;[...t.querySelectorAll('.chip')].find(c=>/^Rivalit/.test(c.textContent)).click()}"); pg.wait_for_timeout(300)
        go(pg, "()=>document.querySelectorAll('#atlas2 .a4-nx .a4-n:not(.sun)')[0].click()", 900); go(pg, "()=>document.querySelectorAll('#atlas2 .a4-nx .a4-n:not(.sun)')[0].click()", 900)
        tr = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-trail .chip')].map(c=>c.textContent)")
        ok(T + 'Nexus: traccia dell\'esplorazione con tappe toccabili', len(tr) == 2, tr)
        pg.evaluate("()=>document.querySelector('#atlas2 .a4-trail .chip').click()"); pg.wait_for_timeout(600)
        ok(T + 'Nexus: toccando una tappa si torna a quel punto', pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-trail .chip').length")==0, pg.evaluate("()=>tvaAtlas2.stato().a3.c"))
        # alias condiviso: Harry Osborn (tre identità)
        go(pg, "()=>tvaAtlas2.setState({screen:'a3',a3:{v:'nx',c:'id-norman-osborn-green-goblin'}})", 2000)
        lab2 = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-nx .a4-n')].map(n=>[n.querySelector('.lb').firstChild.textContent,(n.querySelector('.lb small')||{}).textContent||''])")
        ok(T + 'Nexus: identita\' con lo stesso alias distinte (es. Norman/Harry Osborn)', len(set(map(tuple, lab2))) == len(lab2), lab2)
        ok(T + 'Nexus: nessun overflow orizzontale', pg.evaluate("()=>{const b=" + SCR + ";return b.scrollWidth<=b.clientWidth+1}"))
        b.close()
for vw, vh in [(390, 844), (430, 932)]: run(vw, vh)
ok('nessun errore JS', not errs, errs[:2])
bad = [n for n, c in res if not c]; print('\na42 UI: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
