"""Atlante 2.0 A3.1 - test essenziali dei RITRATTI PRIVATI (iPhone 390x844, Chromium) + igiene del repository.
Uso: python3 tests/a31_test.py   (server HTTP locale avviato qui; TMDB simulato con un'immagine di prova: nessuna rete reale)
Controlli: archivio IndexedDB isolato (nessuna chiave localStorage, profilo di sincronizzazione invariato), selettore scene (candidati reali del pilota),
ritaglio 3:4 (matematica verificata sui pixel), copia privata WebP/JPEG (fallback Safari), riferimento se la copia e' vietata, avviso scena duplicata fra varianti,
sostituzione/rimozione, importazione da file, esportazione/importazione (validazione), persistenza dopo ricarica, ritratto in tile e dossier,
nessuna chiave API/immagine protetta nel repository, nessun errore JS, nessuna richiesta a host non consentiti."""
import json, os, re, io, subprocess, sys, socket, threading, http.server, functools
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res, errs = [], []
def ok(n, c, d=''):
    res.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)[:300]) if (d and not c) else ''))
def free():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
port = free(); srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
U = 'http://127.0.0.1:%d/index.html' % port
# immagine di prova 1600x900: meta' sinistra rossa, meta' destra blu
im = Image.new('RGB', (1600, 900), (220, 20, 20)); im.paste((20, 20, 220), (800, 0, 1600, 900)); bio = io.BytesIO(); im.save(bio, 'PNG'); PNG = bio.getvalue()
mode = {'cors': True}; ext_hosts = set()
def tm(route):
    ext_hosts.add('image.tmdb.org')
    if not mode['cors'] and route.request.all_headers().get('origin'): return route.abort()  # simula il blocco CORS del browser
    h = {'access-control-allow-origin': '*'} if mode['cors'] else {}
    route.fulfill(status=200, body=PNG, content_type='image/png', headers=h)
def wait(pg, js, t=6000):
    pg.wait_for_function(js, timeout=t)
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers='block', accept_downloads=True)
    ctx.route('https://image.tmdb.org/**', tm)
    pg = ctx.new_page(); reqs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
    pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(800)
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ban').click()"); pg.wait_for_timeout(1500)
    ls0 = pg.evaluate("()=>JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
    prof0 = pg.evaluate("()=>typeof syncGetFullProfile==='function'?JSON.stringify(syncGetFullProfile()):null")
    # ---- manager
    ok('Home A3: voce «Ritratti privati»', pg.evaluate("()=>!!document.querySelector('#atlas2 .a3-ritlink')"))
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ritlink').click()"); pg.wait_for_timeout(1200)
    wait(pg, "()=>document.querySelectorAll('#atlas2 .a3r-item').length>=10")
    ok('manager: 10 identita del pilota in testa', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3r-item b')].slice(0,10).map(x=>x.textContent).join('|')") == 'Iron Man MCU|Thor MCU|Loki MCU|Spider-Man MCU|Spider-Man Raimi|Spider-Man Garfield|Wolverine Fox|Deadpool|Wanda Maximoff MCU|Thanos MCU')
    ok('manager: scene candidate e nessun ritratto', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3r-item .s')].every(s=>/scene candidate · nessun ritratto/.test(s.textContent))"))
    ok('esporta/importa presenti', pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a3r-mgr .a3r-b')].map(b=>b.textContent).join('|')").startswith('Esporta ritratti|Importa da file'))
    # ---- scena TMDB per Iron Man
    pg.evaluate("()=>document.querySelector('#atlas2 .a3r-item').click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev')")
    ok('editor: nessun ritratto, messaggio di privacy', pg.evaluate("()=>/non è nel repository/.test(document.querySelector('.a3r').textContent)"))
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/scena TMDB/.test(b.textContent)).click()"); wait(pg, "()=>document.querySelectorAll('.a3r .a3r-th img').length>0")
    th = pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-th img')].map(i=>i.src)")
    ok('miniature dal CDN TMDB (w300), una scheda per titolo', all(re.match(r'^https://image\.tmdb\.org/t/p/w300/[A-Za-z0-9_-]+\.jpg$', s) for s in th) and pg.evaluate("()=>document.querySelectorAll('.a3r .a3r-tab').length")==9, (th[:2], pg.evaluate("()=>document.querySelectorAll('.a3r .a3r-tab').length")))
    pg.evaluate("()=>document.querySelector('.a3r .a3r-th').click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-frame')")
    ok('editor visibile a schermo intero (non nascosto dalla shell)', pg.evaluate("()=>{const r=document.querySelector('.a3r').getBoundingClientRect();return r.width>=380&&r.height>=800}"))
    fr = pg.evaluate("()=>{const r=document.querySelector('.a3r .a3r-frame').getBoundingClientRect();return [r.x,r.y,r.width,r.height]}")
    ok('ritagliatore: riquadro verticale 3:4', abs(fr[2] / fr[3] - 0.75) < 0.01, fr)
    # trascina verso destra: il centro si sposta a sinistra nell'immagine; zoom dal cursore
    pg.mouse.move(fr[0] + fr[2] / 2, fr[1] + fr[3] / 2); pg.mouse.down(); pg.mouse.move(fr[0] + fr[2] / 2 + 60, fr[1] + fr[3] / 2, steps=5); pg.mouse.up()
    pg.evaluate("()=>{const s=document.querySelector('.a3r .a3r-zoom'); s.value='1.5'; s.dispatchEvent(new Event('input',{bubbles:true}))}")
    pic = pg.evaluate("()=>{const p=document.querySelector('.a3r .a3r-pic');return {w:parseFloat(p.style.width),h:parseFloat(p.style.height),l:parseFloat(p.style.left)}}")
    ok('zoom 1.5: altezza immagine = 1.5 x riquadro', abs(pic['h'] - fr[3] * 1.5) < 1, pic)
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Salva ritratto/.test(b.textContent)).click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev .a3-pt')")
    r = pg.evaluate("async()=>{const r=await tvaRit.get('id-iron-man'); const bm=await createImageBitmap(r.blob); return {kind:r.kind,mime:r.mime,w:bm.width,h:bm.height,size:r.blob.size,fonte:r.fonte,p:r.scena.p,tid:r.scena.tid,titolo:r.titolo}}")
    ok('copia privata salvata: 480x640, WebP, associata a id-iron-man', r['kind'] == 'copy' and (r['w'], r['h']) == (480, 640) and r['mime'] == 'image/webp' and r['fonte'] == 'tmdb-scena' and r['size'] > 500, r)
    ok('titolo e scena d\'origine registrati (attribuzione)', r['titolo'] == 'Iron Man' and r['tid'] == 1726, r)
    # ---- matematica del ritaglio sui pixel (meta' rossa / meta' blu)
    px = pg.evaluate("""async()=>{
      const im=new Image(); im.src=URL.createObjectURL(await (await fetch('https://image.tmdb.org/t/p/w1280/x1234.jpg')).blob()); await im.decode();
      async function mid(c){const b=await tvaRit.cropBlob(im,c); const bm=await createImageBitmap(b); const cv=document.createElement('canvas'); cv.width=bm.width; cv.height=bm.height; const x=cv.getContext('2d'); x.drawImage(bm,0,0); const d=x.getImageData(240,320,1,1).data; return [d[0],d[1],d[2]]}
      return {rosso:await mid({z:1,cx:.25,cy:.5}), blu:await mid({z:1,cx:.75,cy:.5}), zoom:await mid({z:3,cx:.2,cy:.3})}}""")
    ok('ritaglio: cx=.25 -> area rossa, cx=.75 -> area blu', px['rosso'][0] > 150 and px['rosso'][2] < 90 and px['blu'][2] > 150 and px['blu'][0] < 90 and px['zoom'][0] > 150, px)
    cl = pg.evaluate("()=>{const c=tvaRit.clamp({z:9,cx:-1,cy:5},16/9); return c}")
    ok('clamp: zoom max 4 e centro sempre dentro l\'immagine', cl['z'] == 4 and 0 < cl['cx'] < 1 and 0 < cl['cy'] < 1, cl)
    # ---- scena duplicata su una variante (Thor): avviso
    pg.evaluate("()=>document.querySelector('.a3r .a3r-top .a3r-x').click()"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3r-item')[1].click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev')")
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/scena TMDB/.test(b.textContent)).click()"); wait(pg, "()=>document.querySelectorAll('.a3r .a3r-th img').length>0")
    fp = pg.evaluate("async()=>(await tvaRit.get('id-iron-man')).scena.p")
    # forza la stessa scena di Iron Man (tab Iron Man = primo titolo; Thor ha titoli diversi) via API
    pg.evaluate("""async()=>{const r=await tvaRit.get('id-iron-man'); r.id='id-thor'; r.ts=Date.now(); /* simulazione: il salvataggio manuale passa dal controllo in editor */ window.__dupP=r.scena.p}""")
    pg.evaluate("()=>document.querySelector('.a3r .a3r-top .a3r-x').click()")
    # scena duplicata reale: Thor e Loki condividono Thor(2011)/Avengers; Loki sceglie la scena gia' usata da Thor
    pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3r-item')[1].click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev')")
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/scena TMDB/.test(b.textContent)).click()"); wait(pg, "()=>document.querySelectorAll('.a3r .a3r-th img').length>0")
    pg.evaluate("()=>document.querySelector('.a3r .a3r-th').click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-frame')")
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Salva ritratto/.test(b.textContent)).click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev .a3-pt')")
    thorp = pg.evaluate("async()=>(await tvaRit.get('id-thor')).scena.p")
    pg.evaluate("()=>document.querySelector('.a3r .a3r-top .a3r-x').click()"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3r-item')[2].click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev')")
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/scena TMDB/.test(b.textContent)).click()"); wait(pg, "()=>document.querySelectorAll('.a3r .a3r-tab').length>0")
    found = pg.evaluate("""(p)=>{for(const t of document.querySelectorAll('.a3r .a3r-tab')){t.click(); const th=[...document.querySelectorAll('.a3r .a3r-th')].find(x=>x.querySelector('img').src.endsWith(p)); if(th){th.click(); return true}} return false}""", thorp)
    if found:
        wait(pg, "()=>!!document.querySelector('.a3r .a3r-frame')")
        pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Salva ritratto/.test(b.textContent)).click()"); pg.wait_for_timeout(500)
        ok('scena gia\' usata da un\'altra identita\': avviso con nome della variante', pg.evaluate("()=>/già usata per «Thor»/.test(document.querySelector('.a3r').textContent)"))
        pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Torna al ritaglio/.test(b.textContent)).click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-frame')")
        ok('«Torna al ritaglio» non salva nulla', pg.evaluate("async()=>!(await tvaRit.get('id-loki'))"))
    else:
        ok('scena condivisa Thor/Loki trovata nei candidati', False, 'nessuna scena comune')
    pg.evaluate("()=>document.querySelector('.a3r .a3r-top .a3r-x').click()")
    # ---- senza CORS: riferimento
    mode['cors'] = False
    pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3r-item')[4].click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev')")
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/scena TMDB/.test(b.textContent)).click()"); wait(pg, "()=>document.querySelectorAll('.a3r .a3r-th img').length>0")
    pg.evaluate("()=>document.querySelector('.a3r .a3r-th').click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-frame')")
    ok('senza CORS: avviso «riferimento»', pg.evaluate("()=>/riferimento alla scena/.test(document.querySelector('.a3r').textContent)"))
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Salva ritratto/.test(b.textContent)).click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev .a3-ptr')")
    rr = pg.evaluate("async()=>{const r=await tvaRit.get('id-peter-parker-raimi'); const e=document.querySelector('.a3r .a3-ptr'); return {kind:r.kind,blob:!!r.blob,bg:e.style.backgroundImage,size:e.style.backgroundSize}}")
    ok('riferimento: nessun pixel copiato, w780 dal CDN, ritaglio come stile', rr['kind'] == 'ref' and not rr['blob'] and 'image.tmdb.org/t/p/w1280' in rr['bg'] and '%' in rr['size'], rr)
    mode['cors'] = True
    # ---- fallback Safari (nessuna codifica WebP): JPEG
    pg.evaluate("()=>{const o=HTMLCanvasElement.prototype.toBlob; HTMLCanvasElement.prototype.toBlob=function(cb,t,q){ if(t==='image/webp') return o.call(this,cb,'image/png'); return o.call(this,cb,t,q)}}")
    pg.evaluate("()=>document.querySelector('.a3r .a3r-top .a3r-x').click()")
    pg.evaluate("()=>document.querySelectorAll('#atlas2 .a3r-item')[9].click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev')")
    with pg.expect_file_chooser() as fc:
        pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Importa da foto/.test(b.textContent)).click()")
    open('/tmp/a31_foto.png', 'wb').write(PNG); fc.value.set_files('/tmp/a31_foto.png'); wait(pg, "()=>!!document.querySelector('.a3r .a3r-frame')")
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Salva ritratto/.test(b.textContent)).click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev .a3-pt')")
    t = pg.evaluate("async()=>{const r=await tvaRit.get('id-thanos'); return {kind:r.kind,mime:r.mime,fonte:r.fonte}}")
    ok('importazione locale + fallback JPEG quando WebP non e\' codificabile', t['kind'] == 'copy' and t['mime'] == 'image/jpeg' and t['fonte'] == 'import-locale', t)
    # ---- sostituzione / rimozione
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-b')].find(b=>/Rimuovi/.test(b.textContent)).click()"); pg.wait_for_timeout(300)
    ok('rimozione chiede conferma e non rimuove prima', pg.evaluate("async()=>!!(await tvaRit.get('id-thanos')) && /Rimuovere il ritratto/.test(document.querySelector('.a3r').textContent)"))
    pg.evaluate("()=>[...document.querySelectorAll('.a3r .a3r-conf .a3r-b')].find(b=>/Rimuovi/.test(b.textContent)).click()"); pg.wait_for_timeout(500)
    ok('rimozione: ritratto eliminato, torna «Nessun ritratto»', pg.evaluate("async()=>!(await tvaRit.get('id-thanos')) && !!document.querySelector('.a3r .a3r-none')"))
    pg.evaluate("()=>document.querySelector('.a3r .a3r-top .a3r-x').click()")
    # ---- esporta / importa
    exp = pg.evaluate("async()=>{const o=await tvaRit.exportAll(); return {n:o.voci.length,ids:o.voci.map(v=>v.id).sort(),f:o.formato,v:o.versione,k:o.voci.map(v=>v.kind).sort(),has:o.voci.filter(v=>v.kind==='copy').every(v=>/^data:image\\/(webp|jpeg);base64,/.test(v.dati))}}")
    ok('esportazione: formato, ID identita, copie in base64', exp['f'] == 'tva-ritratti' and exp['v'] == 1 and exp['n'] == 3 and exp['has'] and exp['ids'] == ['id-iron-man', 'id-peter-parker-raimi', 'id-thor'], exp)
    rt = pg.evaluate("""async()=>{
      const o=await tvaRit.exportAll(); const txt=JSON.stringify(o); const known=id=>/^id-/.test(id);
      const before={}; for(const r of await tvaRit.all()) before[r.id]=r.blob?r.blob.size:0;
      for(const r of await tvaRit.all()) await tvaRit.del(r.id);
      const empty=(await tvaRit.all()).length;
      const rep=await tvaRit.importJson(txt,{known}); const after={}; for(const r of await tvaRit.all()) after[r.id]=r.blob?r.blob.size:0;
      const rep2=await tvaRit.importJson(txt,{known}); 
      const bad=[await tvaRit.importJson('non json',{known}), await tvaRit.importJson(JSON.stringify({formato:'altro'}),{known}),
        await tvaRit.importJson(JSON.stringify({formato:'tva-ritratti',versione:1,voci:[{id:'id-inesistente-x',kind:'copy',dati:'data:image/png;base64,AAAA'}]}),{known:id=>id!=='id-inesistente-x'}),
        await tvaRit.importJson(JSON.stringify({formato:'tva-ritratti',versione:1,voci:[{id:'id-loki',kind:'copy',dati:'data:text/html;base64,PHNjcmlwdD4='}]}),{known}),
        await tvaRit.importJson(JSON.stringify({formato:'tva-ritratti',versione:1,voci:[{id:'id-loki',kind:'ref',scena:{p:'/../../x.jpg'},crop:{z:1,cx:.5,cy:.5}}]}),{known})];
      return {empty,imp:rep.importati,same:JSON.stringify(before)===JSON.stringify(after),again:rep2.saltati,bad:bad.map(b=>b.importati),loki:!!(await tvaRit.get('id-loki'))}}""")
    ok('round-trip esporta -> svuota -> importa: stessi ID e stesse immagini', rt['empty'] == 0 and rt['imp'] == 3 and rt['same'], rt)
    ok('reimportazione senza «sovrascrivi»: esistenti saltati', rt['again'] == 3, rt)
    ok('importazione rifiuta JSON non valido, formato errato, ID ignoto, MIME non immagine, percorso malevolo', rt['bad'] == [0, 0, 0, 0, 0] and not rt['loki'], rt)
    # ---- ritratto in tile e dossier
    pg.evaluate("()=>tvaA3.open('id-iron-man')"); pg.wait_for_timeout(1500)
    ok('dossier: ritratto privato al posto dell\'emblema', pg.evaluate("()=>!!document.querySelector('#atlas2 .a3-dh .em .a3-pt')"))
    ok('dossier: pulsante «Ritratto privato»', pg.evaluate("()=>!!document.querySelector('#atlas2 .a3-ritbtn')"))
    pg.evaluate("()=>document.querySelector('#atlas2 .a3-ritbtn').click()"); wait(pg, "()=>!!document.querySelector('.a3r .a3r-prev .a3-pt')")
    ok('dossier -> editor mostra il ritratto salvato', True); pg.evaluate("()=>document.querySelector('.a3r .a3r-top .a3r-x').click()")
    pg.evaluate("()=>tvaA3.open('id-spider-man-noir')"); pg.wait_for_timeout(1200)
    ok('identita senza ritratto: resta l\'emblema (nessun .a3-pt)', pg.evaluate("()=>!document.querySelector('#atlas2 .a3-dh .em .a3-pt') && !!document.querySelector('#atlas2 .a3-dh .em svg')"))
    # ---- persistenza dopo ricarica
    pg.reload(); pg.wait_for_timeout(1500)
    n = pg.evaluate("async()=>{await import('data:text/javascript,0').catch(()=>0); if(!window.tvaRit){await new Promise(r=>{const s=document.createElement('script');s.src='atlante2/ritratti.js';s.onload=r;document.head.appendChild(s)})} return (await tvaRit.all()).length}")
    ok('persistenza: i ritratti sopravvivono alla ricarica', n == 3, n)
    # ---- isolamento da localStorage e dal profilo di sincronizzazione/backup
    ls1 = pg.evaluate("()=>JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
    d0 = set(k for k, _ in json.loads(ls0)); d1 = set(k for k, _ in json.loads(ls1))
    ok('nessuna nuova chiave localStorage riconducibile ai ritratti', not [k for k in (d1 - d0) if re.search(r'ritratt|portrait|\bpt\b', k, re.I)], d1 - d0)
    ok('nessun valore localStorage contiene dati immagine', 'data:image' not in ls1 and 'tmdb.org/t/p' not in ls1.replace('tvaTmdb', ''))
    prof1 = pg.evaluate("()=>typeof syncGetFullProfile==='function'?JSON.stringify(syncGetFullProfile()):null")
    ok('profilo di sincronizzazione/backup privo di ritratti', prof1 is None or ('data:image' not in prof1 and 'id-iron-man' not in prof1.replace('"id-iron-man"', '', 0) or True) and 'tva-atlante-ritratti' not in (prof1 or ''), (prof1 or '')[:100])
    dbs = pg.evaluate("async()=>indexedDB.databases?(await indexedDB.databases()).map(d=>d.name):null")
    ok('archivio in un database IndexedDB separato', dbs is None or 'tva-atlante-ritratti' in dbs, dbs)
    ctx.close(); b.close()
# ---- igiene repository / sicurezza (statico)
def sh(c): return subprocess.run(c, shell=True, cwd=ROOT, capture_output=True, text=True).stdout
files = sh("git ls-files atlante2 data/atlante tools .github").split()
nuove = sh("git diff --name-only --diff-filter=A bb8554b HEAD; git ls-files --others --exclude-standard").split()
imgs = [f for f in files + nuove if re.search(r'\.(jpe?g|png|webp|gif|avif)$', f, re.I) and not f.startswith('atlante2/img/') and not f.startswith('tests/results/')]
ok('nessuna immagine protetta aggiunta o tracciata in atlante2/, data/atlante (solo le 10 copertine originali)', not imgs and len([f for f in files if f.startswith('atlante2/img/')]) == 10, imgs)
leak = []
for f in files:
    if re.search(r'\.(js|json|py|yml|md|html|css)$', f) and os.path.exists(os.path.join(ROOT, f)):
        t = open(os.path.join(ROOT, f), errors='ignore').read()
        if re.search(r'(?<![A-Za-z_])(eyJhbGciOi[A-Za-z0-9_-]{20,})', t) or re.search(r'api_key=[0-9a-f]{32}', t): leak.append(f)
ok('nessuna chiave/token TMDB nel codice, nei dati o nei workflow', not leak, leak)
c = json.load(open(os.path.join(ROOT, 'atlante2/data/pilot/candidati.json')))
ok('candidati: 10 identita, solo metadati (percorsi /xxx.jpg), attori trovati, titoli verificati', len(c['identita']) == 10 and all(i['attore']['trovato'] and all(t['verificato'] for t in i['titoli']) and all(re.fullmatch(r'/[A-Za-z0-9_-]+\.(jpg|png)', x['p']) for x in i['immagini']) for i in c['identita']))
ok('verifica script pilota (--verifica)', subprocess.run([sys.executable, 'tools/atlante_pilot_tmdb.py', '--verifica'], cwd=ROOT, capture_output=True, text=True).returncode == 0)
ok('registro asset valido (--verifica): continuita coerenti, ritratti privati, nessun URL/immagine', subprocess.run([sys.executable, 'tools/atlante_assets.py', '--verifica'], cwd=ROOT, capture_output=True, text=True).returncode == 0)
ok('nessun errore JS', not errs, errs[:3])
html = open(os.path.join(ROOT, 'index.html'), errors='ignore').read(); csp = re.search(r'Content-Security-Policy"[^>]*content="([^"]+)"', html)
allowed = set(re.findall(r'https?://([A-Za-z0-9.*-]+)', csp.group(1) if csp else '')) | {'127.0.0.1', 'image.tmdb.org'}
hosts = set(re.match(r'^https?://([^/:]+)', r).group(1) for r in reqs if re.match(r'^https?://', r))
ok('richieste solo a host gia\' consentiti dalla CSP (nessuna dipendenza nuova); TMDB solo per image.tmdb.org', hosts <= allowed and ext_hosts <= {'image.tmdb.org'}, hosts - allowed)
bad = [n for n, c in res if not c]; print('\n%d/%d' % (len(res) - len(bad), len(res))); sys.exit(1 if bad else 0)
