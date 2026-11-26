"""A4.3 — Percorsi e confronti + dati Fantastici Quattro + titoli senza parole spezzate (390 e 430 px).
Uso: python3 tests/a43_percorsi_test.py"""
import os, socket, threading, http.server, functools, json
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
ST = "()=>{const s=tvaAtlas2.stato();return {screen:s.screen,a3:s.a3?JSON.parse(JSON.stringify(s.a3)):null}}"
# dati: Fantastici Quattro per continuita'
d = json.load(open(os.path.join(ROOT, 'atlante2/data/index.json')))
by = {v['i']: v for v in d['voci']}
ok('dati: identita\' FF distinte per continuita\' (Story/1994/Trank/First Steps/Illuminati)', all(k in by for k in ['id-reed-richards', 'id-reed-richards-1994', 'id-reed-richards-trank', 'id-reed-richards-first-steps', 'id-reed-richards-illuminati', 'id-sue-storm-first-steps', 'id-johnny-storm-human-torch-first-steps', 'id-ben-grimm-first-steps']))
t828 = sorted(v['n'] for v in d['voci'] if v.get('u') == 'uni-earth-828' and v['t'] == 'p')
ok('dati: Terra-828 contiene Reed, Sue, Johnny, Ben, Franklin e Galactus (non solo 2)', len(t828) >= 6 and any('Reed' in n for n in t828) and any('Sue' in n for n in t828) and any('Franklin' in n for n in t828) and any('Galactus' in n for n in t828), t828)
ok('dati: Terra-838 contiene Reed Richards (Illuminati)', any('Reed' in v['n'] for v in d['voci'] if v.get('u') == 'uni-earth-838'))
ok('dati: nessuna fusione (Reed Story e First Steps sono voci diverse con universi diversi)', by['id-reed-richards']['u'] == 'uni-earth-121698' and by['id-reed-richards-first-steps']['u'] == 'uni-earth-828')
def run(vw, vh):
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(U); pg.wait_for_timeout(1500)
        pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
        pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(900)
        pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1500)
        T = '[%d] ' % vw
        # Osservatorio: scheda Terra-828 senza parole spezzate
        pg.evaluate("()=>document.querySelector('#atlas2 [data-portal=mv]').click()"); pg.wait_for_timeout(1800)
        pg.evaluate("()=>{const n=document.querySelector('#atlas2 .a4-vp .a4-n[data-id=\"uni-earth-828\"]');n.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}));n.click()}"); pg.wait_for_timeout(900)
        tiles = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-sheet .a3-tile .t b')].map(b=>b.textContent)")
        ok(T + 'Osservatorio Terra-828: schede dei Fantastici Quattro + Franklin + Galactus', len(tiles) >= 6 and any('Reed' in x for x in tiles) and any('Galactus' in x for x in tiles), tiles)
        ok(T + 'Osservatorio: nessuna parola spezzata nei nomi delle schede', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-sheet .a3-tile .t b')].every(b=>b.scrollWidth<=b.clientWidth+1)"))
        # Confronto dettagliato dal pannello
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-sheet .btn')].find(b=>/Confronta con/.test(b.textContent)).click()"); pg.wait_for_timeout(300)
        pg.evaluate("()=>{const n=document.querySelector('#atlas2 .a4-vp .a4-n[data-id=\"uni-earth-199999-mcu\"]');n.click()}"); pg.wait_for_timeout(700)
        ok(T + 'Confronto nel pannello con pulsante «Confronto dettagliato»', pg.evaluate("()=>!![...document.querySelectorAll('#atlas2 .a4-sheet .btn')].find(b=>b.textContent==='Confronto dettagliato')"))
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-sheet .btn')].find(b=>b.textContent==='Confronto dettagliato').click()"); pg.wait_for_timeout(1500)
        s = pg.evaluate(ST); ok(T + 'Vista Confronto aperta con i due universi', s['a3']['v'] == 'cp' and s['a3']['ua'] and s['a3']['ub'], s)
        ok(T + 'Confronto: sezioni titoli in comune, controparti, solo in A / solo in B', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-out .a4-path h3')].map(h=>h.textContent).length")>=4)
        ok(T + 'Confronto: Terra-828 ↔ MCU condividono il titolo N°125 con nome', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-cmpt')].some(x=>/^N°125/.test(x.textContent))"))
        ok(T + 'Confronto: nessun overflow orizzontale', pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"))
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a4-swap')][0].click()"); pg.wait_for_timeout(500)
        s2 = pg.evaluate(ST); ok(T + 'Confronto: inversione A/B', s2['a3']['ua'] == s['a3']['ub'] and s2['a3']['ub'] == s['a3']['ua'])
        ok(T + 'Confronto: persistenza dello stato dopo ricarica logica (setState)', pg.evaluate("()=>{const x=tvaAtlas2.stato();return !!x.a3&&x.a3.v==='cp'}"))
        # Percorsi dalla Home
        pg.evaluate("()=>tvaAtlas2.setState({screen:'a3',a3:{v:'home'}})"); pg.wait_for_timeout(900)
        pg.evaluate("()=>document.querySelector('#atlas2 [data-portal=pc]').click()"); pg.wait_for_timeout(1500)
        ok(T + 'Percorsi: linguette Percorso / Confronto e pulsante Inverti', pg.evaluate("()=>document.querySelectorAll('#atlas2 .a4-tabs .chip').length===2&&!!document.querySelector('#atlas2 .a4-swap')"))
        pg.evaluate("()=>tvaAtlas2.setState({screen:'a3',a3:{v:'pc',a:'id-iron-man',b:'id-thor',m:'n',doc:1}})"); pg.wait_for_timeout(1500)
        info = pg.evaluate("()=>({paths:document.querySelectorAll('#atlas2 .a4-path').length,steps:document.querySelectorAll('#atlas2 .a4-step').length,un:document.querySelectorAll('#atlas2 .a4-un').length,opn:document.querySelectorAll('#atlas2 .a4-opn').length,t:(document.querySelector('#atlas2 .a4-out')||{}).textContent})")
        ok(T + 'Percorso: passi con nome, universo e «Apri nel TVA Nexus»', info['paths'] >= 1 and info['steps'] >= 2 and info['un'] >= 2 and info['opn'] >= 1, info)
        pg.evaluate("()=>document.querySelector('#atlas2 .a4-swap').click()"); pg.wait_for_timeout(1200)
        s3 = pg.evaluate(ST); ok(T + 'Percorso: inversione partenza/arrivo', s3['a3']['a'] == 'id-thor' and s3['a3']['b'] == 'id-iron-man', s3)
        pg.evaluate("()=>document.querySelector('#atlas2 .a4-opn').click()"); pg.wait_for_timeout(1500)
        ok(T + 'Percorso: apertura nel Nexus', pg.evaluate(ST)['a3']['v'] == 'nx')
        ok(T + 'Percorsi: nessun overflow orizzontale', pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"))
        b.close()
run(390, 844); run(430, 932)
ok('nessun errore JS', not errs, errs[:3])
bad = [n for n, c in res if not c]; print('\nA4.3: %d ok, %d falliti' % (len(res) - len(bad), len(bad))); raise SystemExit(1 if bad else 0)
