"""TVA Atlas - riassegnazione sicura del ritratto privato tra identita' gemelle (Matt Murdock 2003 / MCU). Uso: python3 tests/a35_test.py"""
import os, socket, threading, http.server, functools
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); res = []
def ok(n, c, d=''): res.append(bool(c)); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)[:200]) if (d and not c) else ''))
s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
A, M = 'id-matt-murdock-daredevil', 'id-matt-murdock-mcu'
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 390, 'height': 844}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto('http://127.0.0.1:%d/index.html' % port); pg.wait_for_timeout(1500)
    pg.add_style_tag(url='atlante2/a3.css'); pg.add_script_tag(url='atlante2/ritratti.js'); pg.wait_for_function('window.tvaRit', timeout=8000)
    pg.evaluate("async()=>{const r=window.tvaRit; for (const i of ['%s','%s']) await r.del(i); await r.put({id:'%s',kind:'ref',fonte:'tmdb-scena',titolo:'prova',p:'/x.jpg',crop:{z:1,cx:.5,cy:.5}})}" % (A, M, A))
    pg.evaluate("()=>{var a=document.getElementById('atlas2'); if(a){a.hidden=false;a.removeAttribute('aria-hidden');a.style.cssText='display:block;position:fixed;inset:0;z-index:99999'}}")
    def clk(t): pg.evaluate("(t)=>[...document.querySelectorAll('.a3r-b')].find(b=>b.textContent===t).click()", t)
    def apri():
        pg.evaluate("()=>window.tvaRit.openEditor('%s','Matt',function(i){return i==='%s'?'Matt MCU':'Matt 2003'})" % (A, M)); pg.wait_for_timeout(500)
    apri(); ok('pulsanti Sposta/Copia presenti', pg.locator('text=Sposta su Matt MCU').count() == 1 and pg.locator('text=Copia su Matt MCU').count() == 1)
    clk('Copia su Matt MCU'); pg.wait_for_timeout(600)
    ok('copia: entrambe le identita\' hanno il ritratto', pg.evaluate("async()=>!!(await window.tvaRit.get('%s'))&&!!(await window.tvaRit.get('%s'))" % (A, M)))
    apri(); clk('Sposta su Matt MCU'); pg.wait_for_timeout(600)
    ok('spostamento su destinazione occupata: nessuna sovrascrittura, origine intatta', pg.evaluate("async()=>!!(await window.tvaRit.get('%s'))" % A))
    pg.evaluate("async()=>{await window.tvaRit.del('%s')}" % M); apri(); clk('Sposta su Matt MCU'); pg.wait_for_timeout(800)
    ok('spostamento: origine svuotata, destinazione con riassegnato_da', pg.evaluate("async()=>{const a=await window.tvaRit.get('%s'),b=await window.tvaRit.get('%s');return !a&&b&&b.riassegnato_da==='%s'}" % (A, M, A)))
    ok('nessun errore JS', not errs, errs); br.close()
print('A3.5 riassegnazione: %d / %d PASS' % (sum(res), len(res))); raise SystemExit(0 if all(res) else 1)
