# TD1: restyling schede + Diario TVA. Confronti "prima/dopo" attivi solo se TD_OLD_INDEX_DIR punta a una cartella con la build precedente (altrimenti NOT RUN).
import json,re,subprocess,os,sys,socket,time
ROOT=os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD=os.environ.get('TD_OLD_INDEX_DIR')
def srv(d):
    s=socket.socket(); s.bind(('127.0.0.1',0)); port=s.getsockname()[1]; s.close()
    return subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1','--directory',d],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL),port
S1,P1=srv(ROOT); S2,P2=(srv(OLD) if OLD else (None,None)); time.sleep(1.3)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%P1; UO=('http://127.0.0.1:%d/index.html'%P2) if P2 else None
fails=[]; notrun=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
def nr(m): print('NOT RUN '+m); notrun.append(m)
APP_STUB="window.firebase=window.firebase||{apps:[],initializeApp:function(c){var a={name:'[DEFAULT]',options:c};this.apps.push(a);return a;}};"
NK='marvel-ultimate-timeline-notes'
def mkpage(b,url,w=390,h=844):
    cx=b.new_context(viewport={'width':w,'height':h},service_workers='block'); pg=cx.new_page(); errs=[]; csp=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m:csp.append(m.text) if 'Content Security Policy' in m.text or 'Refused to' in m.text else None)
    def route(r):
        u=r.request.url
        if 'firebase-app-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=APP_STUB)
        if 'firebase-database-compat' in u or 'firebase-auth-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body='')
        if 'identitytoolkit' in u or 'securetoken' in u or 'firebaseio' in u or 'gstatic' in u or 'tmdb' in u: return r.abort()
        return r.continue_()
    pg.route('**/*',route); return cx,pg,errs,csp
def load(pg,url,notes=None,wait=1800):
    pg.goto(url); pg.wait_for_timeout(900)
    if notes is not None:
        pg.evaluate("(n)=>localStorage.setItem('%s',n)"%NK,json.dumps(notes)); pg.reload(); pg.wait_for_timeout(wait)
    else: pg.wait_for_timeout(wait-600)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
def opn(pg,i):
    pg.evaluate("(i)=>{const w=document.getElementById('item-'+i);w.scrollIntoView({block:'center'});if(window.tvaTd2){window.tvaTd2.open('item-'+i,{fromTimeline:true});const nt=w.querySelector('details.note-toggle'),ta=w.querySelector('textarea.user-note');if(nt&&ta&&ta.value)nt.open=true}else{w.querySelector('details.card').open=true}}",i); pg.wait_for_timeout(400)
store=lambda pg,k=NK: pg.evaluate("(k)=>localStorage.getItem(k)",k)
html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
js=re.search(r'<script id="td1-js">(.*?)</script>',html,re.S).group(1); code=re.sub(r'/\*.*?\*/','',js,flags=re.S)
ck(not re.search(r'localStorage|sessionStorage|indexedDB|firebase|fetch\(|XMLHttpRequest|sendBeacon|WebSocket|document\.cookie',code),'analisi statica: il modulo di restyling non usa storage, rete, Firebase')
ck(re.search(r'name="tva-build" content="([^"]+)"',html).group(1)==re.search(r"SW_BUILD = '([^']+)'",open(os.path.join(ROOT,'sw.js')).read()).group(1),'build HTML = build service worker')
SEED={'002':'Rivisto con Anna.\nLa scena del treno resta la migliore.','040':'Nota con <b>tag</b> & "virgolette" e àèìòù 🎬'}
with sync_playwright() as p:
    b=p.chromium.launch()
    cx,pg,errs,csp=mkpage(b,U); load(pg,U,SEED)
    st=pg.evaluate("()=>({cards:document.querySelectorAll('.card-wrap[data-item]').length,diary:document.querySelectorAll('.card-wrap .td-diary').length,info:document.querySelectorAll('.card-wrap .td-info').length,act:document.querySelectorAll('.card-wrap .td-actions').length,bare:[...document.querySelectorAll('.card-wrap[data-item]')].filter(w=>!w.querySelector('.td-actions')&&(w.querySelector('details.watch-picker')||w.querySelector('label.local-file-btn'))).length,hasBtn:[...document.querySelectorAll('.card-wrap[data-item]')].filter(w=>w.querySelector('details.watch-picker')||w.querySelector('label.local-file-btn')).length,ta:document.querySelectorAll('textarea.user-note').length})")
    ck(st['cards']==139 and st['diary']==139 and st['info']==139 and st['act']==st['hasBtn'] and st['bare']==0 and st['ta']==139,'tutte le 139 schede ristrutturate: Diario e info; pulsanti raggruppati su tutte le schede che li hanno (le altre, non ancora uscite, non ne hanno)',st)
    ck(store(pg)==json.dumps(SEED),'note esistenti: storage byte-identico dopo il caricamento (nessuna scrittura/migrazione)')
    # scheda vuota
    opn(pg,'001')
    v=pg.evaluate("()=>{const d=document.querySelector('#item-001 .td-diary');const r=d.getBoundingClientRect();return {vis:r.width>0&&r.height>0,title:d.querySelector('.td-d-t').textContent,priv:d.querySelector('.td-d-priv').textContent,sub:d.querySelector('.td-d-sub').textContent,prev:d.querySelector('.td-d-prev').textContent,cta:d.querySelector('.td-cta').textContent,ctaVis:d.querySelector('.td-cta').offsetParent!==null,open:d.querySelector('details').open,del:d.querySelector('.td-d-del').hidden}}")
    ck(v['vis'] and v['title']=='Diario TVA' and 'Privato' in v['priv'] and v['sub']=='Le tue note personali su Spider-Man' and 'Ancora nessuna nota' in v['prev'] and v['cta']=='+ Aggiungi una nuova nota' and v['ctaVis'] and not v['open'],'Diario visibile senza note: titolo, sottotitolo con nome titolo, badge Privato, stato vuoto, CTA',v)
    # nota esistente
    opn(pg,'002')
    v=pg.evaluate("()=>{const d=document.querySelector('#item-002 .td-diary');const ta=d.querySelector('textarea');return {open:d.querySelector('details').open,val:ta.value,cta:d.querySelector('.td-cta').textContent,prev:d.querySelector('.td-d-prev').textContent}}")
    ck(v['val']==SEED['002'] and v['open'] and 'Modifica' in v['cta'],'nota esistente: testo riutilizzato identico e leggibile/modificabile',v)
    v=pg.evaluate("()=>{const ta=document.querySelector('#note-040');return ta.value}")
    ck(v==SEED['040'],'nota con caratteri speciali/HTML mostrata come testo, identica',v)
    ck(pg.evaluate("()=>!document.querySelector('#item-040 .td-diary b')"),'nessuna iniezione HTML dal testo della nota')
    pg.evaluate("()=>document.querySelector('#item-002 .note-toggle').open=false"); pg.wait_for_timeout(200)
    ck('Rivisto con Anna.' in pg.evaluate("()=>document.querySelector('#item-002 .td-d-prev').textContent"),'anteprima della nota nello stato chiuso')
    # modifica + persistenza
    pg.click('#item-002 .td-cta'); pg.wait_for_timeout(200)
    ck(pg.evaluate("()=>document.querySelector('#item-002 .note-toggle').open")==True and pg.evaluate("()=>document.activeElement&&document.activeElement.id")=='note-002','"Modifica nota" apre l\'editor e dà il focus alla nota')
    pg.fill('#note-002','Seconda versione della nota\ncon due righe'); pg.wait_for_timeout(700)
    n=json.loads(store(pg)); ck(n['002']=='Seconda versione della nota\ncon due righe' and n['040']==SEED['040'],'modifica salvata (e le altre note intatte)',n)
    pg.reload(); pg.wait_for_timeout(1800); pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}")
    ck(pg.evaluate("()=>document.querySelector('#note-002').value")=='Seconda versione della nota\ncon due righe','persistenza dopo ricarica')
    # nuova nota su scheda vuota + offline
    cx.set_offline(True); opn(pg,'001'); pg.click('#item-001 .td-cta'); pg.fill('#note-001','scritta offline'); pg.wait_for_timeout(700)
    ck(json.loads(store(pg)).get('001')=='scritta offline','nuova nota scritta offline salvata (CTA "+ Aggiungi una nuova nota")'); cx.set_offline(False)
    ck('scritta offline' in pg.evaluate("()=>document.querySelector('#item-001 .td-d-prev').textContent") and 'Modifica' in pg.evaluate("()=>document.querySelector('#item-001 .td-cta').textContent"),'anteprima e pulsante aggiornati dopo il salvataggio')
    # eliminazione: annulla, poi conferma
    before=store(pg)
    pg.click('#item-001 .td-d-del'); pg.wait_for_timeout(200)
    ck(pg.evaluate("()=>!document.querySelector('#item-001 .td-d-confirm').hidden"),'Elimina nota: chiede conferma')
    pg.click('#item-001 .td-d-confirm .td-btn:not(.td-btn-danger)'); pg.wait_for_timeout(500)
    ck(store(pg)==before and pg.evaluate("()=>document.querySelector('#note-001').value")=='scritta offline','Annulla: nota intatta')
    pg.click('#item-001 .td-d-del'); pg.click('#item-001 .td-d-confirm .td-btn-danger'); pg.wait_for_timeout(700)
    n=json.loads(store(pg)); ck('001' not in n and n['002'].startswith('Seconda') and n['040']==SEED['040'],'Conferma: eliminata solo quella nota',n)
    # svuotamento manuale: richiede conferma, nulla viene salvato finche' non confermi
    opn(pg,'002'); pg.fill('#note-002',''); pg.wait_for_timeout(700)
    ck(pg.evaluate("()=>!document.querySelector('#item-002 .td-d-confirm').hidden")==True and json.loads(store(pg)).get('002','').startswith('Seconda'),'testo svuotato a mano: conferma richiesta e nota ancora in storage')
    pg.click('#item-002 .td-d-confirm .td-btn:not(.td-btn-danger)'); pg.wait_for_timeout(500)
    ck(pg.evaluate("()=>document.querySelector('#note-002').value").startswith('Seconda') and json.loads(store(pg))['002'].startswith('Seconda'),'svuotamento annullato: testo ripristinato')
    pg.fill('#note-002',''); pg.wait_for_timeout(300); pg.click('#item-002 .td-d-confirm .td-btn-danger'); pg.wait_for_timeout(700)
    ck('002' not in json.loads(store(pg)),'svuotamento confermato: nota eliminata')
    # nota lunga
    long='x'*5000+' fine'; pg.click('#item-002 .td-cta') if pg.evaluate("()=>!document.querySelector('#item-002 .note-toggle').open") else None; pg.fill('#note-002',long); pg.wait_for_timeout(700)
    ck(json.loads(store(pg))['002']==long,'nota lunga (5000 caratteri) salvata integralmente')
    ck(pg.evaluate("()=>document.querySelector('#note-002').maxLength")==100000,'limite 100000 caratteri = validatore di import/export del profilo')
    # regressione: voti, progressi, preferiti dopo la ristrutturazione
    pg.evaluate("()=>{document.querySelector('#item-003 .watch-check').click()}"); pg.wait_for_timeout(300)
    [ (pg.evaluate("()=>{const b=document.querySelector('.td2-back');if(b)b.click()}"), pg.wait_for_timeout(700)) for _ in range(4) ]; pg.evaluate("()=>document.querySelector('#item-003').scrollIntoView({block:'center'})"); pg.wait_for_timeout(250); pg.click('#item-003 .rw-s[data-k="4"]'); pg.wait_for_timeout(400)
    pg.evaluate("()=>{document.querySelector('#item-003 .fav-star').click()}"); pg.wait_for_timeout(300)
    ck(json.loads(store(pg,'marvel-ultimate-timeline-watched')).get('003') and str(json.loads(store(pg,'marvel-ultimate-timeline-ratings')).get('003'))=='4' and '003' in store(pg,'marvel-ultimate-timeline-favorites'),'progressi, voto e preferiti continuano a funzionare')
    ck(errs==[] and csp==[],'nessun errore JS/CSP',(errs+csp)[:3]); cx.close()
    # confronto con build precedente
    if UO:
        def snap(url):
            cx,pg,e,c=mkpage(b,url); load(pg,url,SEED)
            r=pg.evaluate("""()=>{const o={ids:[],rows:{},links:{},local:{},rate:{}};document.querySelectorAll('.card-wrap[data-item]').forEach(w=>{const id=w.dataset.item;o.ids.push(w.id);
              o.rows[id]=[...w.querySelectorAll('.detail-panel .detail-row')].filter(r=>!r.classList.contains('td-pos')).map(r=>(r.querySelector('.detail-k')?.textContent||'')+'='+(r.querySelector('.detail-v')?.textContent||'').replace(/\\s+/g,' ').trim()).sort().join('|');
              o.links[id]=[...w.querySelectorAll('.watch-plat-btn')].map(a=>a.getAttribute('href')+'|'+a.getAttribute('target')+'|'+a.getAttribute('rel')).join(';');
              const lf=w.querySelector('label.local-file-btn');o.local[id]=lf?(lf.getAttribute('for')+'|'+lf.getAttribute('onclick')):null;
              o.rate[id]=w.querySelectorAll('.rating-star').length;
              o.sg=(o.sg||0)+w.querySelectorAll('details.sub-group').length});return o}""")
            r['notes']=store(pg); r['title']=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[data-item] .title')].map(e=>e.textContent.trim()).join('|')"); cx.close(); return r
        a=snap(UO); n=snap(U)
        ck(a['ids']==n['ids'],'ordine e identificativi delle 139 schede identici (Timeline/ordinamenti invariati)')
        ck(a['title']==n['title'],'titoli identici')
        d=[k for k in a['rows'] if a['rows'][k]!=n['rows'][k]]; ck(not d,'dati delle schede (Universo, Ambientazione, Durata, Personaggi, chip) identici su tutte le schede',d[:3])
        ck(a['links']==n['links'],'collegamenti "Guarda" (href/target/rel) identici su tutte le schede')
        ck(a['local']==n['local'],'pulsante "File locale" (for/onclick) identico su tutte le schede')
        ck(a['sg']==n['sg'] and a['rate']==n['rate'],'accordion (Trama/Curiosità/Dietro le quinte/Collegamenti) e stelle voto invariati',(a['sg'],n['sg']))
        ck(a['notes']==n['notes'],'storage note identico tra build precedente e nuova')
    else: nr('confronto con build precedente (TD_OLD_INDEX_DIR non impostata)')
    # responsive
    for W,H in ((320,640),(360,740),(390,844),(430,932)):
        cx,pg,e,c=mkpage(b,U,W,H); load(pg,U,SEED)
        pg.evaluate("()=>{document.querySelector('#item-040 .title').textContent='Titolo molto lungo di prova con ParolaLunghissimaSenzaSpaziAttraversoTuttaLaLarghezzaDelloSchermo e altri termini ancora'}")
        for i in ('002','040','001'): opn(pg,i); pg.evaluate("(i)=>{document.querySelectorAll('#item-'+i+' details.sub-group').forEach(d=>d.open=true);document.querySelector('#item-'+i+' details.watch-picker').open=true}",i)
        pg.wait_for_timeout(300)
        r=pg.evaluate("""()=>{const W=document.documentElement.clientWidth,bad=[];for(const i of ['002','040','001']){document.querySelectorAll('#item-'+i+' *').forEach(e=>{const r=e.getBoundingClientRect();if(r.width&&e.offsetParent&&(r.right>W+0.5||r.left<-0.5)&&!e.closest('.watch-box,.fav-star'))bad.push(i+':'+e.tagName+'.'+e.className.toString().slice(0,30)+':'+Math.round(r.right))})}
          const tb=[...document.querySelectorAll('#item-002 .td-cta,#item-001 .td-cta,#item-002 .td-btn,#item-002 .td-actions>*>summary,#item-002 .td-actions>label,#item-002 .sub-group>summary,#item-002 > details.card > summary')].filter(e=>e.offsetParent).map(e=>[e.className.toString().slice(0,18),Math.round(e.getBoundingClientRect().height)]);
          return {ow:document.documentElement.scrollWidth-W,bad:bad.slice(0,5),minTouch:Math.min(...tb.map(x=>x[1])),fs:getComputedStyle(document.querySelector('#note-002')).fontSize}}""")
        ck(r['ow']<=0 and not r['bad'],'%d px: nessun overflow orizzontale né elementi fuori schermo (titolo lunghissimo incluso)'%W,r)
        ck(r['minTouch']>=44 and r['fs']=='16px','%d px: bersagli tattili >= 44px, nota a 16px (no zoom iOS)'%W,r)
        if W==390:
            pg.evaluate("()=>{const t=document.getElementById('darkModeToggle');if(t){t.checked=true;t.dispatchEvent(new Event('change',{bubbles:true}))}}"); pg.wait_for_timeout(300)
            contr=pg.evaluate("""()=>{function lum(c){const m=c.match(/[\\d.]+/g).map(Number);const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(m[0])+.7152*f(m[1])+.0722*f(m[2])}
              function bgOf(e){while(e){const c=getComputedStyle(e).backgroundColor;const m=c.match(/[\\d.]+/g);if(m&&(m.length<4||+m[3]>.5))return c;e=e.parentElement}return 'rgb(20,18,15)'}
              const out=[];document.querySelectorAll('#item-002 .td-btn-main, #item-002 .td-actions > details > summary, #item-002 .td-actions > label, #item-002 .td-d-t, #item-002 .td-d-sub, #item-002 .td-d-priv').forEach(e=>{if(!e.offsetParent)return;const fg=getComputedStyle(e).color,bg=bgOf(e);const a=lum(fg),b=lum(bg);out.push([e.className.toString().slice(0,16),((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2)])});return out}""")
            ck(all(float(c[1])>=4.5 for c in contr),'contrasto >= 4.5:1 su pulsanti e titoli del Diario (tema scuro)',contr)
        cx.close()
    # schermate (percorso fisso, non asserzioni)
    b.close()
S1.terminate()
if S2: S2.terminate()
print('FAILS:',fails,'| NOT RUN:',notrun); sys.exit(1 if fails else 0)
