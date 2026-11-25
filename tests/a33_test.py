"""A3.2 v2 – revisione rapida consecutiva (iPhone 390x844). Dati e immagini SINTETICI. Uso: python3 tests/a33_test.py"""
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
def pth(k): return '/sintetica%02d.jpg' % k
IDS = ['id-aa-uno', 'id-bb-due', 'id-cc-tre', 'id-dd-quattro']
def cand(i, iid):
    return {'id': iid, 'nome': 'Eroe ' + iid[3:5].upper(), 'attore': {'nome': 'Attore Prova'}, 'titoli': [{'num': '001', 'titolo_tmdb': 'Film prova', 'tmdb_id': 11, 'verificato': True}],
            'immagini': [{'p': pth(i * 20 + k), 'w': 1920, 'h': 1080, 'num': '001'} for k in range(12)]}
CROP = {'z': 1.5, 'cx': 0.45, 'cy': 0.5}
def pr(rk, p): return {'rk': rk, 'p': p, 'w': 1920, 'h': 1080, 'num': '001', 'sc': 0.9 - rk * .05, 'ck': 1 if rk == 1 else 0, 'crop': CROP}
PROP = {'schema': 2, 'identita': [
    {'id': IDS[0], 'conf': 'alta', 'proposte': [pr(1, pth(0)), pr(2, pth(1)), pr(3, pth(2))]},
    {'id': IDS[1], 'conf': 'alta', 'proposte': [pr(1, pth(20)), pr(2, pth(21))]},
    {'id': IDS[2], 'conf': 'alta', 'proposte': [pr(1, pth(0)), pr(2, pth(41)), pr(3, pth(42))]},   # la 1ª scena è la stessa dell'identità 0 → deve passare alla successiva
    {'id': IDS[3], 'conf': 'bassa', 'proposte': [pr(k + 1, pth(60 + k)) for k in range(10)]}]}
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, service_workers='block')
    ctx.route('https://image.tmdb.org/**', lambda r: r.fulfill(status=200, body=PNG, content_type='image/png', headers={'access-control-allow-origin': '*'}))
    ctx.route('**/atlante2/data/pilot/c/_indice.json', lambda r: r.fulfill(status=200, body=json.dumps({'identita': IDS}), content_type='application/json'))
    for i, iid in enumerate(IDS): ctx.route('**/atlante2/data/pilot/c/%s.json' % iid, lambda r, rq=None, i=i, iid=iid: r.fulfill(status=200, body=json.dumps(cand(i, iid)), content_type='application/json'))
    ctx.route('**/atlante2/data/pilot/proposte.json', lambda r: r.fulfill(status=200, body='{"identita":[]}', content_type='application/json'))
    ctx.route('**/atlante2/data/pilot/proposte2.json', lambda r: r.fulfill(status=200, body=json.dumps(PROP), content_type='application/json'))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/index.html' % port); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(600)
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1200)
    pg.evaluate("()=>tvaA3.open('id-iron-man')"); pg.wait_for_timeout(1500); pg.evaluate("()=>document.querySelector('#atlas2 .a3-ritbtn').click()"); pg.wait_for_timeout(900)
    # ritratto già salvato dall'utente per l'identità 1: non deve mai essere toccato
    pg.evaluate("""async()=>{await tvaRit.put({id:'id-bb-due',kind:'ref',fonte:'tmdb-scena',titolo:'SCELTO DALL UTENTE',scena:{p:'/sceltoUtente.jpg',w:1920,h:1080,num:'001'},crop:{z:1.2,cx:.5,cy:.5},ts:111,v:1})}""")
    pg.evaluate("()=>document.querySelector('.a3r .a3r-x').click()"); pg.evaluate("()=>tvaRit.revisione(()=>true)"); pg.wait_for_timeout(1500)
    txt = lambda: pg.evaluate("()=>document.querySelector('.a3r .a3r-main').innerText")
    t = txt()
    ok('coda: l\'identità con ritratto salvato è esclusa (1 / 3)', '1 / 3' in t, t[:80])
    ok('anteprima 3:4 e bersagli >= 44 px', pg.evaluate("()=>{const e=document.querySelector('.a3r .a3r-big').getBoundingClientRect(); const b=[...document.querySelectorAll('.a3r .a3r-b')].map(x=>x.getBoundingClientRect().height); return Math.abs(e.width/e.height-.75)<.02 && b.every(h=>h>=43.5)}"))
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Approva/.test(b.textContent)).click()"); pg.wait_for_timeout(2200)
    r0 = pg.evaluate("()=>tvaRit.get('id-aa-uno')")
    ok('approvata la 1ª: ritratto salvato con crop e rango', r0 and r0['kind'] in ('copy', 'ref') and r0['scena'].get('rk') == 1 and abs(r0['crop']['z'] - 1.5) < .01, r0)
    t = txt(); ok('passa all\'identità successiva (2 / 3, salvati 1)', '2 / 3' in t and 'salvati 1' in t, t[:90])
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Approva/.test(b.textContent)).click()"); pg.wait_for_timeout(2000)
    t = txt(); ok('scena già usata da un\'altra identità: non salvata, passa alla proposta 2', 'già usata' in t and 'proposta 2 di 3' in t and pg.evaluate("()=>tvaRit.get('id-cc-tre')") is None, t[:200])
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Approva/.test(b.textContent)).click()"); pg.wait_for_timeout(2200)
    r2 = pg.evaluate("()=>tvaRit.get('id-cc-tre')"); ok('approvata la proposta 2: rango 2 registrato', r2 and r2['scena'].get('rk') == 2, r2)
    t = txt(); ok('identità a confidenza bassa: 10 proposte e avviso', '3 / 3' in t and 'proposta 1 di 10' in t and 'BASSA' in t, t[:160])
    for _ in range(9): pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Altra proposta/.test(b.textContent)).click()"); pg.wait_for_timeout(120)
    ok('alla 10ª proposta «Altra proposta» è disattivato', pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].some(b=>b.disabled)"))
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Salta/.test(b.textContent)).click()"); pg.wait_for_timeout(500)
    t = txt(); ok('fine coda: riepilogo (2 salvati, 1 saltata)', 'Revisione terminata: 2 ritratti salvati, 1 identità saltate' in t, t)
    ub = pg.evaluate("()=>tvaRit.get('id-bb-due')"); ok('ritratto dell\'utente MAI sovrascritto', ub and ub['titolo'] == 'SCELTO DALL UTENTE' and ub['ts'] == 111 and ub['scena']['p'] == '/sceltoUtente.jpg', ub)
    v = pg.evaluate("()=>tvaRit.valutazioni()"); ok('valutazioni (solo metadati): 2 da proposta, rk1=1, rk3=2, nessun blob', v['da_proposta'] == 2 and v['rk1'] == 1 and v['rk3'] == 2 and 'blob' not in json.dumps(v) and 'dati' not in json.dumps(v), v)
    ok('nessun errore JS', not errs, errs)
    br.close()
print('\nA3.2-v2 revisione rapida: %d / %d PASS' % (sum(res), len(res))); raise SystemExit(0 if all(res) else 1)
