"""A3.2 v3 – filtro «senza ritratto», contatore completati/mancanti, composizione dei ritratti delle varianti negli hub, export valutazioni (iPhone 390x844). Dati SINTETICI. Uso: python3 tests/a34_test.py"""
import re, io, os, json, socket, threading, http.server, functools
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = []
def ok(n, c, d=''):
    res.append(bool(c)); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)) if (d and not c) else ''))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
im = Image.new('RGB', (1920, 1080), (30, 40, 120)); d = ImageDraw.Draw(im); d.ellipse((760, 240, 1160, 640), fill=(240, 200, 120)); b = io.BytesIO(); im.save(b, 'PNG'); PNG = b.getvalue()
J = lambda pg, e: pg.evaluate(e)
def rec(i, p, rk=None, loc=False):
    r = {'id': i, 'kind': 'ref', 'fonte': 'import-locale' if loc else 'tmdb-scena', 'titolo': 't', 'scena': None if loc else {'p': p, 'w': 1920, 'h': 1080, 'num': '001', **({'rk': rk, 'sc': .8} if rk else {})}, 'crop': {'z': 1.5, 'cx': .5, 'cy': .5}, 'ts': 5, 'v': 1}
    return r
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, service_workers='block')
    ctx.route('https://image.tmdb.org/**', lambda r: r.fulfill(status=200, body=PNG, content_type='image/png', headers={'access-control-allow-origin': '*'}))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/index.html' % port); pg.wait_for_timeout(1200)
    J(pg, "()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    J(pg, "()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(600)
    J(pg, "()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1200)
    J(pg, "()=>tvaA3.open('id-iron-man')"); pg.wait_for_timeout(1200); J(pg, "()=>document.querySelector('#atlas2 .a3-ritbtn').click()"); pg.wait_for_timeout(900); J(pg, "()=>document.querySelector('.a3r .a3r-x').click()")
    for r in (rec('id-peter-parker-mcu', '/aaaaaaaa1.jpg', 1), rec('id-peter-parker-raimi', '/aaaaaaaa2.jpg', 4), rec('id-iron-man', '/aaaaaaaa3.jpg', 2), rec('id-thor', '/aaaaaaaa4.jpg'), rec('id-loki', None, None, True)):
        J(pg, "async(r)=>{await tvaRit.put(r)}".replace('(r)=>', '()=>').replace('tvaRit.put(r)', 'tvaRit.put(' + json.dumps(r) + ')'))
    # export: include TUTTI i ritratti (anche l'import da file locale), con origine
    v = J(pg, "()=>tvaRit.valutazioni()")
    ok('valutazioni v2: totale = tutti i ritratti (5), file locali separati', v['totale'] == 5 and v['file_locali'] == 1 and v['scene_manuali'] == 1 and v['da_proposta'] == 3, {k: v[k] for k in ('totale', 'file_locali', 'scene_manuali', 'da_proposta')})
    ok('valutazioni: rk1/rk3/rk5', v['rk1'] == 1 and v['rk3'] == 2 and v['rk5'] == 3, (v['rk1'], v['rk3'], v['rk5']))
    # hub: composizione dei ritratti delle varianti
    J(pg, "()=>tvaA3.open('hub-peter-parker')"); pg.wait_for_timeout(1800)
    ok('hub: composizione a 2 ritratti (varianti con ritratto salvato)', J(pg, "()=>!!document.querySelector('#atlas2 .a3-dh .a3-comp.n2') && document.querySelectorAll('#atlas2 .a3-dh .a3-comp .a3-pt').length===2"))
    J(pg, "()=>tvaA3.open('hub-wilson-fisk')"); pg.wait_for_timeout(1500)
    ok('hub senza ritratti delle varianti: resta l\'emblema (nessuna composizione)', J(pg, "()=>!document.querySelector('#atlas2 .a3-dh .a3-comp')"))
    # catalogo: contatore + filtro
    br2 = ctx.new_page()
    br2.goto('http://127.0.0.1:%d/index.html' % port); br2.wait_for_timeout(1200)
    br2.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); br2.wait_for_timeout(300)
    br2.evaluate("()=>document.getElementById('a2Entry').click()"); br2.wait_for_timeout(600); br2.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); br2.wait_for_timeout(1200)
    br2.evaluate("()=>[...document.querySelectorAll('#atlas2 .btn')].find(b=>/Esplora il catalogo/.test(b.textContent)).click()"); br2.wait_for_timeout(1200)
    # nel nuovo contesto pagina l'IndexedDB è la stessa origine: i 4 ritratti con scena + 1 locale sono presenti
    c = br2.evaluate("()=>document.querySelector('#atlas2 .a3-count').textContent")
    ok('contatore catalogo: «ritratti N/300 completati, M mancanti»', re.search(r'/\d+ completati', c) and 'mancanti' in c, c)
    n0 = br2.evaluate("()=>document.querySelectorAll('#atlas2 .a3-tile').length")
    br2.evaluate("()=>document.querySelector('#atlas2 .a3-fbtn').click()"); br2.wait_for_timeout(200)
    ok('pulsante «Solo senza ritratto» nel pannello filtri', br2.evaluate("()=>!!document.querySelector('#atlas2 .a3-seno') && document.querySelector('#atlas2 .a3-seno').getBoundingClientRect().height>=43.5"))
    br2.evaluate("()=>document.querySelector('#atlas2 .a3-seno').click()"); br2.wait_for_timeout(700)
    c2 = br2.evaluate("()=>document.querySelector('#atlas2 .a3-count').textContent")
    nomi = br2.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-tile')].map(e=>e.getAttribute('aria-label'))")
    ok('filtro attivo: elenco senza i personaggi con ritratto', re.search(r'su \d+', c2) and not any(n and n.startswith('Iron Man') and 'MCU' in n for n in nomi) and not any(n and n.startswith('Thor MCU') for n in nomi), (c2, nomi[:5]))
    br2.evaluate("()=>document.querySelector('#atlas2 .a3-seno').click()"); br2.wait_for_timeout(500)
    ok('filtro disattivabile', br2.evaluate("()=>!/su \\d+/.test(document.querySelector('#atlas2 .a3-count').textContent)"))
    ok('nessun errore JS', not errs, errs)
    br.close()
print('\nA3.2-v3: %d / %d PASS' % (sum(res), len(res))); raise SystemExit(0 if all(res) else 1)
