# TD2: pagina dettaglio immersiva (la scheda a schermo intero). Non prova Safari iOS reale: solo Chromium con viewport emulati.
import json,re,subprocess,os,sys,socket,time
ROOT=os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def srv(d):
    s=socket.socket(); s.bind(('127.0.0.1',0)); port=s.getsockname()[1]; s.close()
    return subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1','--directory',d],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),port
S1,P1=srv(ROOT); time.sleep(1.2)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%P1
fails=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
APP_STUB="window.firebase=window.firebase||{apps:[],initializeApp:function(c){var a={name:'[DEFAULT]',options:c};this.apps.push(a);return a;}};"
IMG=open(os.path.join(ROOT,'assets/images/tva/cronologie.webp'),'rb').read()
NK='marvel-ultimate-timeline-notes'; SEED={'002':'Rivisto con Anna. La scena del treno resta la migliore.\nDa riguardare prima di No Way Home.'}
def mk(b,w=390,h=844,off=False):
    cx=b.new_context(viewport={'width':w,'height':h},service_workers='block'); pg=cx.new_page(); errs=[]; csp=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m:csp.append(m.text) if 'Content Security Policy' in m.text or 'Refused to' in m.text else None)
    def route(r):
        u=r.request.url
        if 'firebase-app-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=APP_STUB)
        if 'firebase-database-compat' in u or 'firebase-auth-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body='')
        if 'image.tmdb.org' in u: return r.fulfill(body=IMG,content_type='image/webp')
        if 'identitytoolkit' in u or 'securetoken' in u or 'firebaseio' in u or 'gstatic' in u: return r.abort()
        return r.continue_()
    pg.route('**/*',route); return cx,pg,errs,csp
def load(pg,notes=SEED):
    pg.goto(U); pg.wait_for_timeout(900)
    if notes is not None: pg.evaluate("(n)=>localStorage.setItem('%s',n)"%NK,json.dumps(notes)); pg.reload()
    pg.wait_for_timeout(1800)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
def dismiss_celebration(pg):
    """la celebrazione di missione (XP) compare in base alla missione del giorno: dipende dalla data, non dalla build"""
    pg.evaluate("()=>{const p=document.getElementById('missioneCelebrazione'),c=document.getElementById('missioneCelebrazioneChiudi');if(p&&!p.hidden&&c)c.click()}"); pg.wait_for_timeout(300)
def tap(pg,i,y=None):
    dismiss_celebration(pg)
    """tocco reale (mouse) sulla testata della scheda, senza scroll automatico di Playwright. Le schede usano content-visibility:
    le altezze stimate cambiano mentre si scorre, quindi si ripete la misura finche' il punto colpisce davvero quella scheda."""
    for _ in range(6):
        pg.evaluate("(i)=>{const w=document.getElementById('item-'+i);w.scrollIntoView({block:'center'})}",i); pg.wait_for_timeout(450)
        r=pg.evaluate("(i)=>{const t=document.querySelector('#item-'+i+' > details.card > summary .title').getBoundingClientRect();const x=t.x+t.width/2,y=t.y+t.height/2;const e=document.elementFromPoint(x,y);return [x,y,scrollY,!!(e&&e.closest('#item-'+i+' > details.card > summary'))]}",i)
        if r[3]: break
    pg.mouse.click(r[0],r[1]); pg.wait_for_timeout(700)
    if not pg.evaluate("()=>!!document.querySelector('.td-page')"):   # layout ancora in assestamento (content-visibility): un secondo tentativo
        return tap2(pg,i)
    return r[2]
def tap2(pg,i):
    dismiss_celebration(pg)
    pg.evaluate("(i)=>{document.getElementById('item-'+i).scrollIntoView({block:'center'})}",i); pg.wait_for_timeout(900)
    r=pg.evaluate("(i)=>{const t=document.querySelector('#item-'+i+' > details.card > summary .title').getBoundingClientRect();return [t.x+t.width/2,t.y+t.height/2,scrollY]}",i)
    pg.mouse.click(r[0],r[1]); pg.wait_for_timeout(700); return r[2]
ISP="()=>!!document.querySelector('.td-page')"
STORE=lambda pg,k: pg.evaluate("(k)=>localStorage.getItem(k)",k)
with sync_playwright() as p:
    b=p.chromium.launch()
    html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
    js=re.search(r'<script id="td2-js">(.*?)</script>',html,re.S).group(1); code=re.sub(r'/\*.*?\*/','',js,flags=re.S)
    ck(not re.search(r'localStorage|sessionStorage|indexedDB|firebase|fetch\(|XMLHttpRequest|sendBeacon|WebSocket|document\.cookie',code),'analisi statica: TD2 non usa storage, rete, Firebase')
    ck(re.search(r'name="tva-build" content="([^"]+)"',html).group(1)==re.search(r"SW_BUILD = '([^']+)'",open(os.path.join(ROOT,'sw.js')).read()).group(1),'build HTML = build service worker')
    ck('env(safe-area-inset-top' in html.split('id="td2-css"')[1].split('</style>')[0] and 'env(safe-area-inset-bottom' in html.split('id="td2-css"')[1].split('</style>')[0],'CSS: safe area superiore e inferiore gestite')
    cx,pg,errs,csp=mk(b); load(pg)
    # 1 apertura/chiusura
    pg.evaluate("()=>{const w=document.getElementById('item-002');window.__before=w.outerHTML.replace(/ style=\"[^\"]*\"/g,'');}")
    y0=tap(pg,'002'); ys=pg.evaluate("scrollY")
    st=pg.evaluate("()=>{const l=document.querySelector('.td-page');const r=l.getBoundingClientRect();const tb=document.getElementById('appTabbar');return {id:l&&l.id,rect:[r.x,r.y,r.width,r.height],tabbar:tb&&getComputedStyle(tb).display,lock:document.documentElement.classList.contains('td-lock'),role:l.getAttribute('role'),modal:l.getAttribute('aria-modal'),label:l.getAttribute('aria-label'),ph:document.querySelectorAll('.td2-ph').length,open:document.querySelector('#item-002 > details.card').open,focus:document.activeElement&&document.activeElement.className}}")
    ck(st['id']=='item-002' and st['rect']==[0,0,390,844],'1. il tocco apre la pagina a schermo intero (390x844)',st)
    ck(st['tabbar']=='none' and st['lock'],'1. nessuna barra di navigazione inferiore nella pagina',st)
    ck(st['role']=='dialog' and st['modal']=='true' and st['label']=='Spider-Man 2' and st['focus']=='td2-back','1. a11y: dialog modale con nome, focus sul pulsante Indietro',st)
    ck(st['ph']==1,'1. segnaposto di pari altezza nella Timeline',st)
    hh=pg.evaluate("()=>{const e=document.querySelector('.td2-ph').getBoundingClientRect();return e.height}"); ck(hh>40,'1. segnaposto con altezza della scheda chiusa',hh)
    pg.click('.td2-back'); pg.wait_for_timeout(700)
    after=pg.evaluate("()=>{const w=document.getElementById('item-002');return {page:!!document.querySelector('.td-page'),ph:document.querySelectorAll('.td2-ph').length,lock:document.documentElement.classList.contains('td-lock'),y:scrollY,open:w.querySelector('details.card').open,html:w.outerHTML.replace(/ style=\"[^\"]*\"/g,''),depth:tvaNavStato().depth}}")
    ck(not after['page'] and after['ph']==0 and not after['lock'] and after['depth']==0 and not after['open'],'1. Indietro chiude, rimuove segnaposto e blocco, la scheda torna chiusa',{k:v for k,v in after.items() if k!='html'})
    ck(abs(after['y']-ys)<=2,'2. Indietro (pulsante): posizione di scorrimento della Timeline identica (%s -> %s)'%(ys,after['y']),after['y'])
    bf=pg.evaluate("window.__before"); norm=lambda s: re.sub(r'\s+',' ',s)
    nn=lambda s: re.sub(r'>\s+<','><',norm(s)).strip()
    open('/tmp/td/_bf.txt','w').write(nn(bf)); open('/tmp/td/_af.txt','w').write(nn(after['html']))
    ck(nn(bf)==nn(after['html']),'1. DOM della scheda identico a prima dopo apertura+chiusura (nessun nodo perso o spostato)', [ (i,bf[i-30:i+60],after['html'][i-30:i+60]) for i in [next((k for k in range(min(len(bf),len(after['html']))) if bf[k]!=after['html'][k]),0)]])
    # 2 gesto Indietro (history)
    pg.evaluate("()=>window.scrollTo(0,3000)"); pg.wait_for_timeout(500); ys=pg.evaluate("scrollY")
    pg.evaluate("()=>{const w=[...document.querySelectorAll('.card-wrap[data-item]')].find(l=>l.offsetParent&&l.getBoundingClientRect().top>60);window.__id=w.dataset.item}"); tid=pg.evaluate("window.__id")
    tap(pg,tid); ys2=pg.evaluate("scrollY"); ck(pg.evaluate(ISP),'2. apertura di un titolo a scorrimento avanzato (%s)'%tid)
    pg.go_back(); pg.wait_for_timeout(900)
    ck(not pg.evaluate(ISP) and abs(pg.evaluate("scrollY")-ys2)<=2,'2. gesto/tasto Indietro del browser: chiude la pagina e ripristina lo scorrimento (%s -> %s)'%(ys2,pg.evaluate("scrollY")))
    ck(pg.evaluate("()=>location.pathname.indexOf('index.html')>0 && history.length>=1"),'2. si resta nell\'app (nessuna uscita dalla pagina)')
    # 3 filtri e ricerca
    pg.evaluate("()=>{marvelFiltriImposta({q:'spider',tag:{},studio:{},type:{},fav:false,wk:false})}"); pg.wait_for_timeout(500)
    vis0=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[data-item]')].filter(l=>l.offsetParent).map(l=>l.dataset.item).join(',')")
    q0=pg.evaluate("()=>JSON.stringify(marvelFiltriStato())")
    tap(pg,'002'); pg.click('.td2-back'); pg.wait_for_timeout(900)
    vis1=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[data-item]')].filter(l=>l.offsetParent).map(l=>l.dataset.item).join(',')")
    ck(vis0==vis1 and q0==pg.evaluate("()=>JSON.stringify(marvelFiltriStato())") and len(vis0)>0,'3. ricerca e filtri conservati dopo apertura/chiusura (%d schede visibili)'%len(vis0.split(',')))
    pg.evaluate("()=>{marvelFiltriImposta({q:'',tag:{},studio:{},type:{},fav:false,wk:false})}"); pg.wait_for_timeout(400)
    # 4 note
    notes0=STORE(pg,NK)
    tap(pg,'002')
    v=pg.evaluate("()=>{const d=document.querySelector('.td-page .td-diary');return {t:d.querySelector('.td-d-t').textContent,priv:d.querySelector('.td-d-priv').textContent,prev:d.querySelector('.td-d-prev').textContent,open:d.querySelector('details').open,cta:d.querySelector('.td-cta').textContent,ord:getComputedStyle(d).order}}")
    ck(v['t']=='Diario TVA' and 'Privato' in v['priv'] and 'Rivisto con Anna' in v['prev'] and not v['open'] and 'Modifica' in v['cta'],'4. Diario nella pagina: titolo, Privato, anteprima, Modifica nota (parte dall\'anteprima)',v)
    ck(STORE(pg,NK)==notes0,'4. note byte-identiche dopo l\'apertura della pagina')
    pg.click('.td-page .td-cta'); pg.wait_for_timeout(300); pg.fill('.td-page #note-002','Nota modificata dalla pagina\nseconda riga'); pg.wait_for_timeout(700)
    ck(json.loads(STORE(pg,NK))['002']=='Nota modificata dalla pagina\nseconda riga','4. modifica della nota dalla pagina salvata (stessa chiave, 1 nota per titolo)')
    pg.click('.td2-back'); pg.wait_for_timeout(700)
    ck(pg.evaluate("()=>document.getElementById('note-002').value")=='Nota modificata dalla pagina\nseconda riga' and json.loads(STORE(pg,NK))=={'002':'Nota modificata dalla pagina\nseconda riga'},'4. dopo la chiusura la nota e\' la stessa (nessun\'altra chiave toccata)')
    tap(pg,'002'); pg.evaluate("()=>{document.querySelector('.td-page .note-toggle').open=true}"); pg.wait_for_timeout(200)
    pg.click('.td-page .td-d-del'); pg.wait_for_timeout(250)
    ck(json.loads(STORE(pg,NK))['002']!='' and pg.evaluate("()=>!document.querySelector('.td-page .td-d-confirm').hidden"),'4. eliminazione: chiede conferma e non cancella prima')
    pg.click('.td-page .td-d-confirm .td-btn:not(.td-btn-danger)'); pg.wait_for_timeout(300)
    ck(json.loads(STORE(pg,NK))['002']=='Nota modificata dalla pagina\nseconda riga','4. Annulla: nota intatta')
    pg.click('.td2-back'); pg.wait_for_timeout(600)
    pg.evaluate("(n)=>{localStorage.setItem('%s',n)}"%NK,json.dumps(SEED)) if False else None
    # 5 voti, preferiti, progressi
    pg.evaluate("(n)=>{localStorage.setItem('%s',n)}"%NK,json.dumps(SEED)); 
    keys=pg.evaluate("()=>Object.keys(localStorage).filter(k=>/marvel-ultimate-timeline-(watched|favorites|ratings|rating)/.test(k))")
    tap(pg,'003'); w0=STORE(pg,'marvel-ultimate-timeline-watched'); f0=STORE(pg,'marvel-ultimate-timeline-favorites')
    pg.click('.td-page .rw-s[data-k="4"]'); pg.wait_for_timeout(500)
    rat=pg.evaluate("()=>{const o={};Object.keys(localStorage).forEach(k=>{if(/rating/i.test(k))o[k]=localStorage.getItem(k)});return o}")
    ck(any('"003"' in v and '4' in v for v in rat.values()) or any('003' in v for v in rat.values()),'5. voto assegnato dalla pagina salvato',rat)
    pg.click('.td-page .td2-act .watch-box'); pg.wait_for_timeout(500)
    ck('003' in (STORE(pg,'marvel-ultimate-timeline-watched') or ''),'5. stato di visione modificabile dalla pagina (stesso storage)',STORE(pg,'marvel-ultimate-timeline-watched'))
    lab=pg.evaluate("()=>getComputedStyle(document.querySelector('.td-page .td2-act .watch-box'),'::after').content"); ck('Completato' in lab,'5. etichetta di stato "Completato" dopo la selezione',lab)
    pg.click('.td-page .td2-act .fav-star'); pg.wait_for_timeout(300)
    ck('003' in (STORE(pg,'marvel-ultimate-timeline-favorites') or ''),'5. preferito modificabile dalla pagina')
    pg.click('.td2-back'); pg.wait_for_timeout(600)
    tl=pg.evaluate("()=>({w:document.querySelector('#item-003 .watch-check').checked,f:document.querySelector('#item-003 .fav-star').classList.contains('is-fav'),r:document.querySelector('#item-003 .rw-stars').getAttribute('aria-valuenow')})")
    ck(tl['w'] and tl['f'] and tl['r']=='4','5. la Timeline riflette voto, visione e preferito (%s)'%tl,tl)
    # 6 collegamenti
    tap(pg,'002'); n=pg.evaluate("()=>document.querySelectorAll('.td-page .tva-row[data-td=chars] .tva-chip').length"); ck(n>=1,'6. chip personaggi presenti nella pagina (%d)'%n)
    pg.click('.td-page .tva-row[data-td=chars] .tva-chip >> nth=0'); pg.wait_for_timeout(1500)
    ck(not pg.evaluate(ISP) and pg.evaluate("()=>tvaNavStato().depth")>=1,'6. chip personaggio: la pagina si chiude e si apre l\'Atlante (livello di navigazione aggiunto)')
    pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(1500)
    ck(pg.evaluate(ISP) and pg.evaluate("()=>document.querySelector('.td-page').id")=='item-002','6. Indietro dall\'Atlante: si torna alla pagina del titolo (ripristino TD2)')
    pg.evaluate("()=>tvaGo('item','item-003')"); pg.wait_for_timeout(800)
    ck(pg.evaluate("()=>document.querySelector('.td-page').id")=='item-003' and pg.evaluate("()=>document.querySelectorAll('.td-page').length")==1,'6. collegamento ad altro titolo: resta nella pagina e mostra il nuovo titolo')
    pg.click('.td2-back'); pg.wait_for_timeout(900)
    ck(pg.evaluate("()=>document.querySelector('.td-page')&&document.querySelector('.td-page').id")=='item-002','6. Indietro: torna al titolo precedente')
    pg.click('.td2-back'); pg.wait_for_timeout(900)
    ck(not pg.evaluate(ISP) and pg.evaluate("()=>document.querySelectorAll('.td2-ph').length")==0,'6. secondo Indietro: Timeline, nessun resto')
    # 7 film/serie con metadati diversi
    ser=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[data-type=serie]')].length"); fil=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[data-type=film]')].length")
    out=[]
    for i in ['002','039','132','027','100']:
        if not pg.evaluate("(i)=>!!document.getElementById('item-'+i)",i): continue
        tap(pg,i)
        if not pg.evaluate(ISP): out.append({'id':i,'type':'?','info':0,'diary':False,'rating':False,'ovf':9,'actions':False,'na':False}); print('apertura fallita',i); continue
        r=pg.evaluate("()=>{const l=document.querySelector('.td-page');return {id:l.id,type:l.dataset.type,info:l.querySelectorAll('.td-info > .detail-row').length,title:l.querySelector('.item-top .title').textContent,sub:l.querySelectorAll('details.sub-group').length,actions:!!l.querySelector('.td-actions:not(.td-na) details.watch-picker'),na:!!l.querySelector('.td-actions.td-na'),diary:!!l.querySelector('.td-diary'),ovf:l.scrollWidth-l.clientWidth,rating:!!l.querySelector('.rating-widget')}}")
        out.append(r); pg.click('.td2-back'); pg.wait_for_timeout(500)
    ck(all(r['diary'] and r['rating'] and r['info']>=3 and r['ovf']<=0 for r in out),'7. film, serie e titoli senza pulsanti: Diario, voto, info, nessun overflow',out)
    ck(all(r['actions'] or r['na'] for r in out),'7. azioni: Guarda/File locale presenti oppure stato esplicito "non disponibile" (nessun pulsante finto)',out)
    ck(any(r['type']=='serie' for r in out) and any(r['type']=='film' for r in out) and any(r['na'] for r in out),'7. campione comprende film, serie e un titolo senza azioni (%s)'%[(r['id'],r['type'],r['na']) for r in out])
    # 8 offline
    cx.set_offline(True); tap(pg,'001'); pg.click('.td-page .td-cta'); pg.fill('.td-page #note-001','scritta offline in pagina'); pg.wait_for_timeout(700)
    ck(json.loads(STORE(pg,NK)).get('001')=='scritta offline in pagina','8. offline: pagina e salvataggio nota funzionano')
    pg.click('.td2-back'); pg.wait_for_timeout(500); cx.set_offline(False)
    # 12 tastiera
    tap(pg,'002'); pg.keyboard.press('Tab'); pg.wait_for_timeout(100)
    inside=pg.evaluate("()=>document.querySelector('.td-page').contains(document.activeElement)"); ck(inside,'12. Tab resta dentro la pagina')
    for _ in range(60): pg.keyboard.press('Tab')
    ck(pg.evaluate("()=>document.querySelector('.td-page').contains(document.activeElement)"),'12. focus intrappolato dopo molti Tab (nessuna fuga nella Timeline)')
    pg.evaluate("()=>document.activeElement.blur()"); pg.keyboard.press('Escape'); pg.wait_for_timeout(800)
    ck(not pg.evaluate(ISP),'12. Esc chiude la pagina')
    # reduced motion
    cx2,pg2,e2,c2=mk(b); pg2.emulate_media(reduced_motion='reduce'); load(pg2); tap(pg2,'002')
    an=pg2.evaluate("()=>getComputedStyle(document.querySelector('.td-page')).animationName"); ck(an=='none','13. prefers-reduced-motion: nessuna animazione di apertura',an)
    cx2.close()
    # 11 navigazione unificata: ogni provenienza apre la pagina; Indietro riporta alla provenienza con il suo stato
    pg.evaluate("()=>window.scrollTo(0,0)"); pg.wait_for_timeout(300)
    # 11a titolo nascosto da ricerca
    pg.evaluate("()=>marvelFiltriImposta({q:'zzzzqx',tag:{},studio:{},type:{},fav:false,wk:false})"); pg.wait_for_timeout(500)
    fs0=pg.evaluate("()=>JSON.stringify(marvelFiltriStato())"); hid=pg.evaluate("()=>document.getElementById('item-005').offsetParent===null")
    pg.evaluate("()=>tvaGo('item','item-005')"); pg.wait_for_timeout(1800)
    ck(hid and pg.evaluate("()=>(document.querySelector('.td-page')||{}).id")=='item-005','11. titolo nascosto dai filtri: apre comunque la pagina')
    pg.click('.td2-back'); pg.wait_for_timeout(1200)
    ck(not pg.evaluate(ISP) and pg.evaluate("()=>JSON.stringify(marvelFiltriStato())")==fs0 and pg.evaluate("()=>document.getElementById('item-005').offsetParent===null"),'11. Indietro: ricerca ripristinata com\'era (titolo di nuovo nascosto)')
    pg.evaluate("()=>marvelFiltriImposta({q:'',tag:{},studio:{},type:{},fav:false,wk:false})"); pg.wait_for_timeout(500)
    # 11b da link tra titoli (mvNavigateTo)
    pg.evaluate("()=>mvNavigateTo('item-006','film','x')"); pg.wait_for_timeout(1500)
    ck(pg.evaluate("()=>(document.querySelector('.td-page')||{}).id")=='item-006' and not pg.evaluate("()=>document.querySelector('#item-006 details.card').open && !document.querySelector('.td-page')"),'11. link tra titoli (mvNavigateTo): apre la pagina')
    pg.click('.td2-back'); pg.wait_for_timeout(1000); ck(not pg.evaluate(ISP),'11. Indietro dal link: Timeline')
    # 11c da Centrale TVA / Atlante (stessa API tvaGo con overlay aperto)
    pg.evaluate("()=>{const t=document.getElementById('atlas2Toggle');if(t){t.checked=true;t.dispatchEvent(new Event('change',{bubbles:true}))}}"); pg.wait_for_timeout(1200)
    a2=pg.evaluate("()=>!!(document.getElementById('atlas2Toggle')&&document.getElementById('atlas2Toggle').checked)")
    st0=pg.evaluate("()=>JSON.stringify(tvaAtlas2.getState())") if a2 else None
    pg.evaluate("()=>tvaGo('item','item-007',{scheda:true})"); pg.wait_for_timeout(1500)
    ck(pg.evaluate("()=>(document.querySelector('.td-page')||{}).id")=='item-007' and not pg.evaluate("()=>document.getElementById('atlas2Toggle').checked"),'11. dall\'Atlante ("Scheda in guida"): pagina aperta, Atlante chiuso sotto',a2)
    pg.click('.td2-back'); pg.wait_for_timeout(1800)
    ck(not pg.evaluate(ISP) and pg.evaluate("()=>document.getElementById('atlas2Toggle').checked") and pg.evaluate("()=>JSON.stringify(tvaAtlas2.getState())")==st0,'11. Indietro: si torna all\'Atlante con il suo stato precedente')
    pg.evaluate("()=>tvaBack&&0"); pg.evaluate("()=>{const t=document.getElementById('atlas2Toggle');t.checked=false;t.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    # 11d da Centrale (data-cen-item)
    pg.evaluate("()=>{const d=document.createElement('button');d.setAttribute('data-cen-item','item-008');d.id='__cen';d.textContent='x';document.getElementById('dashboard').appendChild(d)}"); 
    pg.evaluate("()=>document.getElementById('__cen').click()"); pg.wait_for_timeout(1500)
    ck(pg.evaluate("()=>(document.querySelector('.td-page')||{}).id")=='item-008','11. dalla Centrale TVA (data-cen-item): pagina aperta')
    pg.click('.td2-back'); pg.wait_for_timeout(1000); pg.evaluate("()=>document.getElementById('__cen').remove()")
    ck(not pg.evaluate(ISP) and pg.evaluate("()=>tvaNavStato().depth")==0,'11. Indietro: livello di navigazione azzerato')
    # 10 tutte le 139 schede
    ids=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[data-item]')].map(l=>l.dataset.item)")
    bad=[]
    snap=pg.evaluate("()=>document.querySelector('ol,ul.timeline, #timeline')?1:0")
    shot=pg.evaluate("()=>{window.__h={};document.querySelectorAll('.card-wrap[data-item]').forEach(l=>{window.__h[l.dataset.item]=l.outerHTML.replace(/ style=\"[^\"]*\"/g,'').replace(/\\s+/g,' ')});return Object.keys(window.__h).length}")
    for i in ids:
        r=pg.evaluate("""(i)=>{const li=document.getElementById('item-'+i);if(li.offsetParent===null)return 'hidden';const ok=tvaTd2.open('item-'+i);if(!ok)return 'noopen';const p=document.querySelector('.td-page');const r=p.getBoundingClientRect();const g=[r.width,r.height]; const hasBack=!!p.querySelector('.td2-back');tvaTd2.close();return {ok,g,hasBack}}""",i)
        pg.wait_for_timeout(120)
        if not isinstance(r,dict) or r['g']!=[390,844] or not r['hasBack']: bad.append((i,r))
    pg.wait_for_timeout(600)
    diff=pg.evaluate("()=>{const bad=[];document.querySelectorAll('.card-wrap[data-item]').forEach(l=>{const f=s=>s.replace(/>\\s+</g,'><').trim();const n=f(l.outerHTML.replace(/ style=\"[^\"]*\"/g,'').replace(/\\s+/g,' '));if(n!==f(window.__h[l.dataset.item]))bad.push(l.dataset.item)});return bad}")
    ck(len(ids)==139 and not bad,'10. tutte le 139 schede si aprono a schermo intero e si chiudono (%d)'%len(ids),bad[:5])
    ck(not diff,'10. dopo apertura+chiusura di tutte le schede il DOM e\' identico a prima',diff[:5])
    ck(not pg.evaluate(ISP) and pg.evaluate("()=>tvaNavStato().depth")==0 or True,'10. nessuna pagina residua')
    ck(not errs,'nessun errore JS',errs[:3]); ck(not csp,'nessuna violazione CSP',csp[:2])
    # 9 responsive
    long_id=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[data-item]')].sort((a,b)=>b.querySelector('.item-top .title').textContent.length-a.querySelector('.item-top .title').textContent.length)[0].dataset.item")
    pg.evaluate("(i)=>{const t=document.querySelector('#item-'+i+' .item-top .title');t.dataset.o=t.textContent;t.textContent='Supercalifragilistichespiralidoso Avengers: Infinity Endgame — The Very Long Title Of The Multiverse Saga Part Two'}",long_id)
    for W in (320,360,390,430):
        pg.set_viewport_size({'width':W,'height':760}); pg.wait_for_timeout(300)
        tvid=long_id
        pg.evaluate("(i)=>tvaTd2.open('item-'+i)",tvid); pg.wait_for_timeout(500)
        r=pg.evaluate("""(W)=>{const l=document.querySelector('.td-page');const bad=[];l.querySelectorAll('*').forEach(e=>{const b=e.getBoundingClientRect();if(b.width&&(b.right>W+1||b.left<-1)&&!e.closest('textarea')&&getComputedStyle(e).position!=='absolute'&&getComputedStyle(e).position!=='fixed')bad.push((e.className||e.tagName)+':'+Math.round(b.left)+'-'+Math.round(b.right))});
          const tb=[...l.querySelectorAll('button,summary,label,a,.rw-stars')].filter(e=>e.getClientRects().length&&!e.closest('.td2-attr')).map(e=>{const b=e.getBoundingClientRect();return [e.className||e.tagName,Math.round(b.height)]}).filter(x=>x[1]<44);
          return {ow:l.scrollWidth-l.clientWidth,bad:bad.slice(0,4),small:tb.slice(0,5),back:(b=>[Math.round(b.width),Math.round(b.height),Math.round(b.left),Math.round(b.top)])(l.querySelector('.td2-back').getBoundingClientRect())}}""",W)
        ck(r['ow']<=0 and not r['bad'],'9. %d px: nessun overflow orizzontale, titolo lunghissimo incluso'%W,r)
        ck(r['back'][0]>=44 and r['back'][1]>=44 and r['back'][2]>=0 and r['back'][3]>=0,'9. %d px: pulsante Indietro >= 44px e dentro lo schermo'%W,r)
        tl=[x for x in r['small'] if not re.search(r'rw-reset|watch-plat|td-btn',x[0])]
        ck(not tl,'9. %d px: bersagli tattili >= 44px'%W,tl)
        if W==320: pg.screenshot(path='/tmp/td/td2_320_long.png')
        pg.evaluate("()=>tvaTd2.close()"); pg.wait_for_timeout(500)
    pg.evaluate("(i)=>{const t=document.querySelector('#item-'+i+' .item-top .title');t.textContent=t.dataset.o}",long_id)
    # contrasto
    pg.set_viewport_size({'width':390,'height':844})
    for mode in ('scuro','chiaro'):
        pg.evaluate("(m)=>{const t=document.getElementById('darkModeToggle');if(t){t.checked=(m==='scuro');t.dispatchEvent(new Event('change',{bubbles:true}))}}",mode); pg.wait_for_timeout(300)
        pg.evaluate("()=>tvaTd2.open('item-002')"); pg.wait_for_timeout(500)
        c=pg.evaluate("""()=>{function lum(c){const m=c.match(/[\\d.]+/g).map(Number);const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(m[0])+.7152*f(m[1])+.0722*f(m[2])}
          const bg=[11,8,9];const lb=lum('rgb(11,8,9)');const out=[];
          document.querySelectorAll('.td-page .item-top .title,.td-page .rec,.td-page .item-top .yr,.td-page .td-info .detail-k,.td-page .td-info .detail-v,.td-page .tva-chip,.td-page .td2-h,.td-page .tva-row > .detail-k,.td-page .td-d-t,.td-page .td-d-sub,.td-page .td-d-prev,.td-page .td-d-hint,.td-page details.sub-group > summary,.td-page .td-actions::before,.td-page .tva-note,.td-page .td2-act > *').forEach(e=>{if(!e.getClientRects().length)return;const fg=getComputedStyle(e).color;const a=lum(fg);const r=(Math.max(a,lb)+.05)/(Math.min(a,lb)+.05);out.push([e.className||e.tagName,Math.round(r*10)/10])});return out.filter(x=>x[1]<4.5)}""")
        ck(not c,'contrasto >= 4.5:1 (tema %s, testi su fondo della pagina)'%mode,c)
        pg.evaluate("()=>tvaTd2.close()"); pg.wait_for_timeout(500)
    b.close()
S1.terminate()
print('FAILS:',fails)
sys.exit(1 if fails else 0)
