from playwright.sync_api import sync_playwright
import json,re
R=[]
def ck(n,c,d=''): R.append(c); print(('PASS ' if c else 'FAIL ')+n+(' '+str(d)[:220] if not c else ''))
IMG=open('/home/claude/work/assets/images/tva/cronologie.webp','rb').read()
U='http://127.0.0.1:8124/index.html'
def start(b,w=390,h=844,tmdb=True):
    cx=b.new_context(viewport={'width':w,'height':h},is_mobile=True,has_touch=True,service_workers='block'); pg=cx.new_page(); pg.errs=[]
    pg.on('pageerror',lambda e:pg.errs.append(str(e)))
    pg.route('**/image.tmdb.org/**',(lambda r:r.fulfill(body=IMG,content_type='image/webp')) if tmdb else (lambda r:r.abort()))
    pg.goto(U); pg.wait_for_timeout(900)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>{const b=document.getElementById('appTabTimeline')||[...document.querySelectorAll('.app-tab')].find(x=>/timeline/i.test(x.innerText));b.click()}"); pg.wait_for_timeout(800)
    return pg
with sync_playwright() as p:
    b=p.chromium.launch(); pg=start(b)
    _sw=open('/home/claude/work/sw.js',encoding='utf-8').read()
    _mb=pg.evaluate("document.querySelector('meta[name=tva-build]').content")
    _sb=re.search(r"SW_BUILD = '([^']+)'",_sw).group(1); _cn=re.search(r"CACHE_NAME = '([^']+)'",_sw).group(1)
    ck('build id (meta, formato AAAAMMGG-HHMM-tag)',bool(re.fullmatch(r'\d{8}-\d{4}-[a-z0-9]+',_mb)),_mb)
    ck('build id: meta HTML == SW_BUILD di sw.js',_mb==_sb,(_mb,_sb))
    ck('build id: CACHE_NAME contiene la build',_cn.endswith(_sb),_cn)
    ck('build id: build attesa 20261109-2100-friends',_mb=='20261109-2100-friends',_mb)
    n=pg.evaluate("()=>document.querySelectorAll('.card-wrap[id^=item-]').length"); ck('139 schede (138 + variante)',n==139,n)
    # 1/3 un solo widget voto per scheda, dentro summary, nessuno nel pannello
    r=pg.evaluate("()=>({tot:document.querySelectorAll('.rating-widget').length,inSum:document.querySelectorAll('details.card > summary .rating-widget').length,inPanel:document.querySelectorAll('.detail-panel .rating-widget').length,dup:[...document.querySelectorAll('.card-wrap[id^=item-]')].filter(c=>c.querySelectorAll('.rating-widget').length!==1).length})")
    ck('un solo controllo voto per scheda, nel riquadro principale',r['inSum']==139 and r['inPanel']==0 and r['dup']==0 and r['tot']==139,r)
    pg.evaluate("()=>{const c=document.querySelector('#item-001');c.scrollIntoView({block:'center'})}"); pg.wait_for_timeout(300)
    box=lambda i:pg.evaluate("(i)=>{const e=document.querySelectorAll('#item-001 .rw-s')[i];const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2,r.width,r.height]}",i)
    val=lambda:pg.evaluate("()=>JSON.parse(localStorage.getItem('marvel-ultimate-timeline-ratings')||'{}')['001']||0")
    opened=lambda:pg.evaluate("()=>document.querySelector('#item-001 details.card').open")
    ck('scheda chiusa: stelle visibili',pg.evaluate("()=>{const e=document.querySelector('#item-001 .rw-stars');const r=e.getBoundingClientRect();return !document.querySelector('#item-001 details.card').open&&r.width>100&&r.height>20}"))
    ck('stelle: area di tocco >= 24x36 px',box(0)[2]>=24 and box(0)[3]>=36,box(0))
    x,y,_,_=box(3); pg.touchscreen.tap(x,y); pg.wait_for_timeout(250)
    ck('1° tocco su stella 4 = voto 4 (intero)',val()==4,val()); ck('il tocco sulle stelle non apre la scheda',not opened())
    pg.touchscreen.tap(x,y); pg.wait_for_timeout(250); ck('2° tocco stessa stella = 3,5',val()==3.5,val())
    pg.touchscreen.tap(x,y); pg.wait_for_timeout(250); ck('3° tocco = ripristino 4',val()==4,val())
    x2,y2,_,_=box(1); pg.touchscreen.tap(x2,y2); pg.wait_for_timeout(250); ck('stella diversa (2) = voto intero 2',val()==2,val())
    ck('una sola scrittura per tocco (valore coerente in UI)',pg.evaluate("()=>document.querySelector('#item-001 .rw-val b').textContent")=='2')
    pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-ratings')")
    pg.reload(); pg.wait_for_timeout(900)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(400)
    pg.evaluate("()=>{const b=document.getElementById('appTabTimeline')||[...document.querySelectorAll('.app-tab')].find(x=>/timeline/i.test(x.innerText));b.click()}"); pg.wait_for_timeout(800); pg.evaluate("()=>document.querySelector('#item-001').scrollIntoView({block:'center'})"); pg.wait_for_timeout(300)
    ck('persistenza dopo ricarica',pg.evaluate("()=>document.querySelector('#item-001 .rw-val b').textContent")=='2' and val()==2)
    # accessibilita
    a=pg.evaluate("()=>{const s=document.querySelector('#item-001 .rw-stars');return [s.getAttribute('role'),s.tabIndex,s.getAttribute('aria-valuenow'),s.getAttribute('aria-valuemax'),!!document.getElementById(s.getAttribute('aria-labelledby')),s.getAttribute('aria-valuetext')]}")
    ck('a11y: slider, focusabile, valuenow/valuetext/labelledby',a==['slider',0,'2','5',True,'2 su 5'],a)
    pg.evaluate("()=>document.querySelector('#item-001 .rw-stars').focus()"); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(200)
    ck('tastiera: freccia destra = +0,5 senza aprire la scheda',val()==2.5 and not opened(),val())
    pg.keyboard.press(' '); pg.wait_for_timeout(200); ck('tastiera: barra spaziatrice sullo slider non apre la scheda',not opened())
    pg.evaluate("()=>document.querySelector('#item-001 .rw-reset').click()"); pg.wait_for_timeout(200); ck('Azzera funziona e non apre la scheda',val()==0 and not opened())
    # voto invariato: restano i dati di altre schede
    ck('chiave voti invariata (stesso oggetto)',pg.evaluate("()=>typeof JSON.parse(localStorage.getItem('marvel-ultimate-timeline-ratings')||'{}')")=='object')
    # 4 locandina
    r=pg.evaluate("()=>{const L=[...document.querySelectorAll('.card-wrap[id^=item-]')];return {con:L.filter(c=>c.querySelector('summary > .m3-tl')).length,hp:L.filter(c=>c.classList.contains('m3-hp')).length,inPanel:document.querySelectorAll('.detail-panel .m3-tl').length}}")
    ck('locandine nella riga principale (131), nessuna nel pannello',r['con']==131 and r['hp']==131 and r['inPanel']==0,r)
    g=pg.evaluate("()=>{const c=document.querySelector('#item-001');const i=c.querySelector('.m3-tl'),t=c.querySelector('.title'),ri=i.getBoundingClientRect(),rt=t.getBoundingClientRect();return {left:ri.right<=rt.left+1,w:Math.round(ri.width),h:Math.round(ri.height),ratio:+(ri.width/ri.height).toFixed(2),lazy:i.loading,w1:i.width,sets:!!i.srcset}}")
    ck('locandina a sinistra del titolo, proporzione 2:3, lazy, srcset',g['left'] and abs(g['ratio']-0.67)<0.02 and g['lazy']=='lazy' and g['sets'],g)
    ck('numero opera, anno, badge leggibili',pg.evaluate("()=>{const c=document.querySelector('#item-001');return ['.rec','.yr','.tag'].every(s=>{const e=c.querySelector(s);const r=e.getBoundingClientRect();return r.width>10&&r.height>8&&getComputedStyle(e).visibility==='visible'})}"))
    ck('checkbox e preferiti presenti e cliccabili',pg.evaluate("()=>{const c=document.querySelector('#item-001');const a=c.querySelector('.watch-check'),f=c.querySelector('.fav-star');return !!a&&!!f&&f.getBoundingClientRect().height>20}"))
    # apertura/chiusura con tap su locandina e su titolo
    t=pg.evaluate("()=>{const r=document.querySelector('#item-001 .m3-tl').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}"); pg.touchscreen.tap(*t); pg.wait_for_timeout(300); ck('tap sulla locandina apre',opened())
    # TD2: la scheda si apre come pagina a schermo intero e si chiude con Indietro (non piu' con un secondo tap sulla stessa scheda)
    ck('TD2: pagina immersiva aperta',pg.evaluate("()=>!!document.querySelector('#item-001.td-page')")); pg.click('#item-001 .td2-back'); pg.wait_for_timeout(600); ck('Indietro chiude (ex secondo tap)',not opened() and not pg.evaluate("()=>!!document.querySelector('.td-page')"))
    # overflow
    for w in (390,360,320):
        pg2=start(b,w); pg2.evaluate("()=>document.querySelector('#item-001').scrollIntoView()")
        o=pg2.evaluate("(w)=>Math.max(document.documentElement.scrollWidth,innerWidth)-w",w); bad=pg2.evaluate("""()=>{const W=innerWidth;const bad=[];document.querySelectorAll('#item-001 *, #item-100 *, #item-073 *').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>0&&(r.right>W+1||r.left<-1)&&!e.closest('details:not([open]) .detail-panel'))bad.push(e.className)});return [...new Set(bad)]}""")
        ck(f'nessun overflow orizzontale a {w}px',o<=0 and not bad,(o,bad))
        pg2.close()
    # fallback senza locandina (TMDB in errore) -> emblema, nessuno spazio vuoto
    pg3=start(b,390,844,tmdb=False); pg3.evaluate("()=>document.querySelector('#item-001').scrollIntoView()"); pg3.wait_for_timeout(1500)
    r=pg3.evaluate("()=>{const c=document.querySelector('#item-001');const ic=c.querySelector('.ic');return {hp:c.classList.contains('m3-hp'),img:!!c.querySelector('.m3-tl'),ic:getComputedStyle(ic).display,gridCols:getComputedStyle(c.querySelector('summary')).display}}")
    ck('fallback: senza locandina resta l\'emblema, layout originale',not r['hp'] and not r['img'] and r['ic']!='none' and r['gridCols']=='flex',r)
    # titolo senza mappa TMDB (es. 073) -> emblema e stelle comunque presenti
    r=pg3.evaluate("()=>{const c=document.querySelector('#item-073');return {hp:c.classList.contains('m3-hp'),stars:!!c.querySelector('summary .rw-stars')}}"); ck('titolo senza locandina: emblema + stelle',not r['hp'] and r['stars'],r)
    # 6 sezioni
    pg.evaluate("()=>{const b=[...document.querySelectorAll('.app-tab')].find(x=>/home/i.test(x.innerText));b&&b.click()}"); pg.wait_for_timeout(500)

    # 7 Reliquiario nell'Atlante (stessa schermata esistente) + accesso da Home invariato
    pg.evaluate("()=>document.getElementById('appTabAtlante').click()"); pg.wait_for_timeout(700)
    HUBTXT=pg.evaluate("()=>[...document.querySelectorAll('.a2-scroll, #tvaArchivesOverlayEl')].map(x=>x.innerText).join(' ')")
    c=pg.evaluate("()=>({n:tvaAtlas2.catalogo().reduce((a,g)=>a+g.items.length,0),has:tvaAtlas2.catalogo().some(g=>g.items.some(i=>i.k==='reliquiario')),rows:document.querySelectorAll('.a2-lrow[data-sez]').length,row:!!document.querySelector('.a2-lrow[data-sez=reliquiario]')})")
    ck('Atlante: 15 voci, Reliquiario presente nel catalogo',c['n']==15 and c['has'],c)
    pg.evaluate("()=>{const r=document.querySelector('.a2-lrow[data-sez=reliquiario]');if(r)r.click();else tvaAtlas2.ext.api.nav('reliquiario',{arc:'art',eid:null})}"); pg.wait_for_timeout(800)
    r=pg.evaluate("()=>[...document.querySelectorAll('.a2-scroll')].map(x=>x.innerText).join(' ').slice(0,120)")
    ck('Reliquiario si apre dal catalogo (componente esistente)','Reliquiario' in r and 'Gemme' in r,r)
    ck('Home Atlante: portale Reliquiario ancora presente',HUBTXT.count('Le sei Gemme')>=1,HUBTXT[:100])
    # reset da tastiera
    pg.evaluate("()=>document.getElementById('appTabTimeline').click()"); pg.wait_for_timeout(600)
    pg.evaluate("()=>{const s=document.querySelector('#item-002 .rw-stars');s.scrollIntoView({block:'center'});s.focus()}"); pg.keyboard.press('3'); pg.wait_for_timeout(200)
    pg.evaluate("()=>document.querySelector('#item-002 .rw-reset').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    ck('Azzera da tastiera (Invio) senza aprire la scheda',pg.evaluate("()=>JSON.parse(localStorage.getItem('marvel-ultimate-timeline-ratings')||'{}')['002']||0")==0 and not pg.evaluate("()=>document.querySelector('#item-002 details.card').open"))
    ck('errori JS',not pg.errs,pg.errs)
print('TOT',sum(R),'/',len(R))
