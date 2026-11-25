"""A3.2 – approvazione rapida delle proposte del motore (iPhone 390x844). Dati e immagini SINTETICI (nessuna immagine protetta). Uso: python3 tests/a32e_test.py"""
import io, os, json, socket, threading, http.server, functools
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
cj = json.load(open(os.path.join(ROOT, 'atlante2/data/pilot/candidati.json'), encoding='utf-8'))
inf = [i for i in cj['identita'] if i['id'] == 'id-iron-man'][0]; im0 = inf['immagini'][0]
CROP = {'z': 1.6, 'cx': 0.46, 'cy': 0.5}
PROP = {'schema': 1, 'identita': [{'id': 'id-iron-man', 'nome': 'Iron Man MCU', 'proposte': [
    {'rk': k + 1, 'p': inf['immagini'][k * 7]['p'], 'w': inf['immagini'][k * 7]['w'], 'h': inf['immagini'][k * 7]['h'], 'num': inf['immagini'][k * 7]['num'], 'sc': 0.9 - k * 0.1, 'crop': CROP} for k in range(4)]}]}
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, service_workers='block')
    ctx.route('https://image.tmdb.org/**', lambda r: r.fulfill(status=200, body=PNG, content_type='image/png', headers={'access-control-allow-origin': '*'}))
    ctx.route('**/atlante2/data/pilot/proposte.json', lambda r: r.fulfill(status=200, body=json.dumps(PROP), content_type='application/json'))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/index.html' % port); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(600)
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1200)
    pg.evaluate("()=>tvaA3.open('id-iron-man')"); pg.wait_for_timeout(1200)
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ritbtn').click()"); pg.wait_for_timeout(900)
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/scena TMDB/.test(b.textContent)).click()"); pg.wait_for_timeout(1500)
    ok('sezione proposte automatiche con 4 schede', pg.evaluate("()=>document.querySelectorAll('.a3r .a3r-pc').length") == 4)
    ok('anteprima 3:4 con ritaglio suggerito applicato (background-size)', pg.evaluate("()=>{const e=document.querySelector('.a3r .a3r-pv'); const r=e.getBoundingClientRect(); return Math.abs(r.width/r.height-0.75)<0.02 && /%/.test(e.style.backgroundSize)}"))
    ok('bersaglio ✓ Approva >= 44 px', pg.evaluate("()=>document.querySelector('.a3r .a3r-ok').getBoundingClientRect().height") >= 43.5)
    pg.evaluate("()=>document.querySelectorAll('.a3r .a3r-ok')[1].click()"); pg.wait_for_timeout(2500)
    rec = pg.evaluate("()=>tvaRit.get('id-iron-man')")
    ok('approvazione con un tocco: ritratto salvato', rec and rec.get('kind') in ('copy', 'ref'), rec)
    ok('crop = quello suggerito, rango 2 registrato', rec and abs(rec['crop']['z'] - 1.6) < 0.01 and abs(rec['crop']['cx'] - 0.46) < 0.02 and rec['scena'].get('rk') == 2, rec and (rec.get('crop'), rec.get('scena')))
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Sostituisci|scena TMDB/.test(b.textContent)).click()"); pg.wait_for_timeout(1500)
    pg.evaluate("()=>document.querySelector('.a3r .a3r-pv').click()"); pg.wait_for_timeout(1500)
    ok('tocco sulla scena: ritaglio precompilato da rivedere, con Salva ritratto', pg.evaluate("()=>!!document.querySelector('.a3r .a3r-crop') && [...document.querySelectorAll('.a3r .a3r-b')].some(b=>/Salva ritratto/.test(b.textContent))"))
    ok('nessun errore JS', not errs, errs)
    br.close()
print('\nA3.2-approvazione: %d / %d PASS' % (sum(res), len(res))); raise SystemExit(0 if all(res) else 1)
