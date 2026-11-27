"""W1: integrazione UI della ricerca 'Archivio esteso' (iPhone 390x844). Usa dati FIXTURE copiati temporaneamente in atlante2/data/db e poi rimossi."""
import os, sys, shutil, subprocess, tempfile, socket, threading, http.server, functools, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT/'atlante2/data/db'
res = []; errs = []
def ok(n, c, d=''): res.append(bool(c)); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)) if (d and not c) else ''))
REAL = None
if DB.exists():
    REAL = pathlib.Path(tempfile.mkdtemp())/'db_reale'; shutil.move(str(DB), str(REAL))
T = pathlib.Path(tempfile.mkdtemp())
(T/'data/atlante').mkdir(parents=True); (T/'atlante2/data').mkdir(parents=True)
shutil.copytree(ROOT/'data/atlante/espansione', T/'data/atlante/espansione', ignore=shutil.ignore_patterns('raw'))
import json, hashlib
for f in (T/'data/atlante/espansione/canon').glob('w*_*.jsonl'): f.unlink()
rp = T/'data/atlante/espansione/ids_registro.json'; rg = json.load(open(rp)); rg['ids'] = {k: v for k, v in rg['ids'].items() if v.get('origine') == 'registro-storico'}
rg['ids_sha256'] = hashlib.sha256('\n'.join(sorted(rg['ids'])).encode()).hexdigest(); json.dump(rg, open(rp, 'w'), sort_keys=True)
for f in ('identita.json', 'manifest.json'): shutil.copy(ROOT/'data/atlante'/f, T/'data/atlante'/f)
shutil.copy(ROOT/'atlante2/data/index.json', T/'atlante2/data/index.json')
subprocess.run(['python3', 'tools/db_w1_build.py', 'tests/fixtures/w1_raw_fixture.json', '--scrivi', '--w1b', 'tests/fixtures/w1b'], cwd=ROOT, env=dict(os.environ, DB_ROOT=str(T)), check=True, capture_output=True)
def free():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
port = free(); srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=str(ROOT))); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:%d/index.html' % port
try:
    shutil.copytree(T/'atlante2/data/db', DB)
    def vai(pg, q):
        pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'search',q:''}})"); pg.wait_for_timeout(500); pg.fill('#atlas2 .a3-in', q); pg.wait_for_timeout(900)
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block')
        pg = ctx.new_page(); reqs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
        pg.goto(U); pg.wait_for_timeout(1500)
        pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
        pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(900)
        pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1500)
        ok('db.js e dati db NON caricati prima della ricerca (lazy)', not any('db.js' in r or 'data/db/' in r for r in reqs))
        vai(pg, 'zaxx')
        g = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-dbg .a3-dbi b')].map(e=>e.textContent)")
        ok('ricerca "zaxx": due voci omonime distinte nell\'Archivio esteso', len(g) == 2, g)
        ok('nessun messaggio "Nessun risultato" accanto ai risultati estesi', not pg.evaluate("()=>!!document.querySelector('#atlas2 .empty')"))
        pg.evaluate("()=>document.querySelector('#atlas2 .a3-dbg .a3-dbi').click()"); pg.wait_for_timeout(900)
        st = pg.evaluate("()=>tvaAtlas2.stato().a3.v"); ok('apertura scheda essenziale (view dbx)', st == 'dbx', st)
        txt = pg.evaluate("()=>document.querySelector('#atlas2 .a3-dbx').textContent")
        ok('scheda: Livello C dichiarato, fonti, nessun dossier inventato', 'Livello C' in txt and 'Wikidata' in txt and 'Poteri' not in txt, txt[:120])
        ok('scheda: link Wikidata sicuro', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-dbsrc a')].every(a=>a.rel.includes('noopener')&&a.target==='_blank'&&a.href.startsWith('https://'))"))
        pg.go_back(); pg.wait_for_timeout(800)
        vai(pg, 'orphan entry'); pg.evaluate("()=>document.querySelector('#atlas2 .a3-dbg .a3-dbi').click()"); pg.wait_for_timeout(900)
        t2 = pg.evaluate("()=>document.querySelector('#atlas2 .a3-dbx').textContent")
        ok('scheda Livello B: poteri/specie/organizzazioni con provenienza', 'Livello B' in t2 and 'Poteri' in t2 and 'Volo' in t2 and 'Telepatia' in t2 and 'Organizzazioni di appartenenza' in t2 and 'confermato da due fonti' in t2, t2[:300])
        ok('scheda B: fonti MCU Wiki con licenza CC BY-SA', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-dbsrc a')].some(a=>/CC BY-SA 3.0/.test(a.textContent)&&a.href.includes('fandom.com'))"))
        pg.go_back(); pg.wait_for_timeout(600)
        pg.evaluate("()=>tvaAtlas2.ext.api.nav('a3',{a3:{v:'search',q:''}})"); pg.wait_for_timeout(700)
        pg.evaluate("()=>document.querySelector('#atlas2 .a3-dbopen').click()"); pg.wait_for_timeout(900)
        tiles = pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-dbtile')].map(b=>b.textContent)")
        ok('catalogo esteso: categorie con conteggi', any('Personaggi' in x for x in tiles) and any('Interpreti' in x for x in tiles), tiles)
        pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-dbtile')].find(b=>/Personaggi/.test(b.textContent)).click()"); pg.wait_for_timeout(900)
        ok('catalogo esteso: elenco apribile', pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3-dbi').length")>=2)
        vai(pg, 'scarlet witch')
        ok('alias di voce esistente apre la scheda ESISTENTE', 'Wanda Maximoff' in pg.evaluate("()=>document.querySelector('#atlas2 .a3-dbg')?.textContent||''"))
        vai(pg, 'peter')
        ok('ricerca storica invariata', 'Personaggi' in pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3-sgroup h3')].map(h=>h.firstChild.textContent)"))
        ov = pg.evaluate("()=>document.documentElement.scrollWidth>innerWidth+1"); ok('nessun overflow orizzontale', not ov)
        b.close()
    ok('nessun errore JS', not errs, errs)
finally:
    shutil.rmtree(DB, ignore_errors=True)
    if REAL: shutil.move(str(REAL), str(DB))
sys.exit(0 if all(res) else 1)
