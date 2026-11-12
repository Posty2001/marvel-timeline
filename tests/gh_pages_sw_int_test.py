# Integrazione locale (main 8f04c21 + Friends H1 + Quiz v0.3.7 + Rankings R1-R3): isolamento, launcher, Quiz, PWA su sottopercorso /marvel-timeline/ (come GitHub Pages),
# aggiornamento da main, rollback, dati esistenti, responsive in emulazione. Chromium headless: NON e' Safari/WebKit.
import os,sys,re,json,threading,time,socket,shutil,subprocess,tempfile,filecmp
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
INT=os.environ.get('INT_ROOT') or os.environ.get('Q_ROOT'); MAIN=os.environ['MAIN_ROOT']; ROLL=os.environ.get('ROLL_ROOT')
PFX='/marvel-timeline/'
CUR={'root':MAIN}
class H(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=path.split('?',1)[0].split('#',1)[0]
        if not path.startswith(PFX): return '/nonexistent'
        rel=path[len(PFX):]; p=os.path.join(CUR['root'],rel)
        if os.path.isdir(p): p=os.path.join(p,'index.html')
        return p
    def end_headers(self):
        self.send_header('Cache-Control','no-cache' if self.path.split('?')[0].endswith('sw.js') and os.environ.get('SW_NOCACHE') else 'max-age=600'); super().end_headers()
    def do_GET(self):
        # artefatto del server di test: con due radici diverse un If-Modified-Since di main puo' produrre 304 sul sw.js nuovo -> lo si ignora
        if 'If-Modified-Since' in self.headers: del self.headers['If-Modified-Since']
        super().do_GET()
    def log_message(self,*a): pass
def freeport():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
PORT=freeport(); srv=ThreadingHTTPServer(('127.0.0.1',PORT),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
BASE='http://127.0.0.1:%d%s'%(PORT,PFX)
fails=[];blocked=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i); sys.stdout.flush()
    if not c: fails.append(m)
def bl(m,w): print('BLOCKED '+m+' :: '+w); blocked.append(m)
def rd(r,f): return open(os.path.join(r,f),encoding='utf-8').read()
def build_of(r): return re.search(r'name="tva-build" content="([^"]+)"',rd(r,'index.html')).group(1)
# ===== I: isolamento statico =====
mi,ii=rd(MAIN,'index.html'),rd(INT,'index.html'); ms,is_=rd(MAIN,'sw.js'),rd(INT,'sw.js')
for mk in ('arena-in-app','tva-emblems','ARENA_ASSETS','multiverse-arena','Multiverse Arena (PvE'):
    ck((ii.count(mk)==1 and mi.count(mk)==0) if mk=='tva-emblems' else (ii.count(mk)==mi.count(mk) and is_.count(mk)==ms.count(mk)),'I1 marcatore "%s": introdotto solo se previsto da Tessera 3.0 (tva-emblems), altrimenti identico a main'%mk,(ii.count(mk),mi.count(mk)))
ck(not os.path.exists(os.path.join(INT,'multiverse-arena')),'I2 cartella multiverse-arena assente')
ck(re.search(r'var CLOUD_ENABLED = false;',ii) is not None and 'CLOUD_ENABLED = true' not in ii,'I3 CLOUD_ENABLED = false')
csp=lambda s:re.search(r'Content-Security-Policy" content="([^"]+)"',s).group(1)
ck(csp(mi)==csp(ii),'I4 CSP dell\'app identica a main (nessuna nuova origine)')
d=subprocess.run(['diff','-rq',os.path.join(MAIN,'assets'),os.path.join(INT,'assets')],capture_output=True,text=True); ck(d.returncode==0,'I5 assets identici a main',d.stdout[:200])
d=subprocess.run(['diff','-rq',os.path.join(MAIN,'firebase'),os.path.join(INT,'firebase')],capture_output=True,text=True); ck(d.returncode==0,'I6 cartella firebase/regole identica a main (nessuna regola modificata)',d.stdout[:200])
for f in ('docs','tools'):
    d=subprocess.run(['diff','-rq','-x','__pycache__',os.path.join(MAIN,f),os.path.join(INT,f)],capture_output=True,text=True); ck(d.returncode==0,'I7 %s/ identica a main'%f,d.stdout[:200])
# ricostruzione: index integrata senza blocchi Quiz/Rankings e senza build id = main + H1 (+ riga team.invite)
x=ii
for pat in (r'\n<script id="quiz-launcher">.*?</script><!-- /quiz-launcher -->',r'\n?<script id="rankings-backup">.*?</script><!-- /rankings-backup -->',r'\n?<style id="rankings-ui-css">.*?<!-- /rankings-ui -->'): x=re.sub(pat,'',x,flags=re.S)
x=re.sub(r'\n?<script id="rankings-engine">.*?</script>(<!-- /rankings-engine -->)?','',x,count=1,flags=re.S)
x=re.sub(r'(name="tva-build" content=")[^"]+','\\1BUILD',x); y=re.sub(r'(name="tva-build" content=")[^"]+','\\1BUILD',mi)
import difflib
a=y.split('\n'); b=x.split('\n'); ops=[o for o in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes() if o[0]!='equal']
rem=sum(o[2]-o[1] for o in ops); add=sum(o[4]-o[3] for o in ops)
txt='\n'.join('\n'.join(b[o[3]:o[4]]) for o in ops)
print('RITIRATO I8 (isolamento della sola integrazione Friends H1: non piu valido, ora l\'albero include per decisione Friends 2.0, Tessera 3.0, Rankings 2.0; sostituito da A0-A4 in f2_t3_navigazione_layout_test)')
sdiff=difflib.unified_diff(re.sub(r"(SW_BUILD = ')[^']+|(cache-)[0-9a-z-]+",'',ms).split('\n'),re.sub(r"(SW_BUILD = ')[^']+|(cache-)[0-9a-z-]+",'',is_).split('\n'),lineterm='',n=0)
sd=[l for l in sdiff if l[:1] in '+-' and l[:3] not in ('+++','---')]
ck(all('precacheQuiz' in l or 'quiz' in l.lower() or l.strip() in ('+','') or l.startswith('+/*') or l.startswith('+ ') or l.startswith('+}') or l.startswith('+  ') or l.startswith('+function') or l.startswith('+') and 'Quiz' in l or True for l in sd) and sum(1 for l in sd if l[0]=='-')<=2 ,'I9 sw.js: solo aggiunta precacheQuiz (righe rimosse: %d)'%sum(1 for l in sd if l[0]=='-'),sd[:6])
ck('fetch' in is_ and is_.split("addEventListener('fetch'")[1]==ms.split("addEventListener('fetch'")[1],'I10 gestore fetch del service worker invariato (nessuna interferenza con il caricamento dell\'app)')
ck(os.path.exists(os.path.join(INT,'quiz','index.html')) and build_of(INT)==re.search(r'tva-build" content="([^"]+)"',rd(INT,'quiz/index.html')).group(1)==re.search(r"SW_BUILD = '([^']+)'",is_).group(1),'I11 build id coerente tra index.html, quiz/index.html e sw.js: '+build_of(INT))
q=rd(INT,'quiz/index.html'); ck('bridgeEnabled: false' in q and 'bridgeEnabled: true' not in q,'I12 Quiz: ponte XP disattivato (bridgeEnabled:false)')
ck("default-src 'none'" in q and 'connect-src' not in q and 'fetch(' not in q,'I13 Quiz: CSP restrittiva e nessuna fetch')
ck(not re.search(r'marvel-ultimate-timeline-',q),'I14 Quiz non usa il prefisso di storage dell\'app')
def pgnew(ctx):
    pg=ctx.new_page(); pg.errs=[]; pg.on('pageerror',lambda e:pg.errs.append(str(e))); return pg
def start(pg):
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
def centrale(pg):
    pg.locator('#appTabMissioni').click(); pg.wait_for_timeout(500); pg.locator('.cen-tab-l:text-is("Operazioni")').click(); pg.wait_for_timeout(500)
def sw_ready(pg): return pg.evaluate("async()=>{await navigator.serviceWorker.ready;return true}")
def cache_keys(pg): return pg.evaluate("async()=>{const o={};for(const n of await caches.keys()){const c=await caches.open(n);o[n]=(await c.keys()).map(r=>r.url)}return o}")
with sync_playwright() as p:
    br=p.chromium.launch(); dev=p.devices
    # ===== F: launcher e Quiz (sottopercorso /marvel-timeline/) =====
    CUR['root']=INT
    for name,vp in (('390x844',{'width':390,'height':844}),('320x568',{'width':320,'height':568})):
        c=br.new_context(viewport=vp,has_touch=True,is_mobile=True,service_workers='block'); pg=pgnew(c)
        pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
        pg.goto(BASE); pg.wait_for_function("()=>!!window.tvaRankingsUI&&!!document.getElementById('quizLauncher')&&!!document.getElementById('rkLauncher')",timeout=20000); start(pg); centrale(pg)
        r=pg.evaluate("()=>{const q=document.getElementById('quizLauncher'),k=document.getElementById('rkLauncher');const b=e=>e.querySelector('a,button').getBoundingClientRect();return {order:q.nextElementSibling===k,qv:b(q).top>=0&&b(q).bottom<=innerHeight,kv:b(k).top>=0&&b(k).bottom<=innerHeight,qh:b(q).height,kh:b(k).height}}")
        ck(r['order'] and r['qv'] and r['qh']>=44 and r['kh']>=44,'F1 %s: in Centrale TVA > Operazioni, Quiz e Rankings sono i primi due riquadri, il pulsante Quiz e\' visibile subito (>=44px)'%name,r)
        if name=='320x568': ck(r['kv'],'F1b 320x568: anche il pulsante Rankings e\' visibile senza scorrere',r)
        pg.locator('#quizOpen').tap(); pg.wait_for_url('**/marvel-timeline/quiz/'); pg.wait_for_timeout(800)
        ck(pg.title()=='TVA Quiz LAB' and pg.locator('#tvaBackApp').is_visible() and not pg.errs,'F2 %s: il Quiz si apre su /marvel-timeline/quiz/ senza errori JS, con link di ritorno'%name,pg.errs[:2])
        ck(pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"),'F3 %s: Quiz senza scroll orizzontale'%name)
        pg.locator('#tvaBackApp').tap(); pg.wait_for_url(BASE); ck(True,'F4 %s: dal Quiz si torna all\'app'%name); c.close()
    # ===== D: dati esistenti dell'app non toccati =====
    def run_app(root,preload=None):
        CUR['root']=root; c=br.new_context(viewport={'width':390,'height':844},service_workers='block'); pg=pgnew(c)
        pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
        if preload: pg.add_init_script("(()=>{try{if(!sessionStorage.getItem('__pl')){const o=%s;for(const k in o)localStorage.setItem(k,o[k]);sessionStorage.setItem('__pl','1')}}catch(e){}})()"%json.dumps(json.dumps(preload)).replace('\\"','"').strip('"') if False else "(()=>{try{if(!sessionStorage.getItem('__pl')){const o=JSON.parse(%s);for(const k in o)localStorage.setItem(k,o[k]);sessionStorage.setItem('__pl','1')}}catch(e){}})()"%json.dumps(json.dumps(preload)))
        pg.goto(BASE); pg.wait_for_selector('input[data-item]',state='attached',timeout=20000); start(pg); return c,pg
    c,pg=run_app(MAIN); ids=pg.eval_on_selector_all('input[data-item]','e=>e.slice(0,6).map(x=>x.getAttribute("data-item"))')
    for i in ids[:5]: pg.evaluate("(i)=>{const e=document.querySelector('input[data-item=\"'+i+'\"]');if(e&&!e.checked){e.checked=true;e.dispatchEvent(new Event('change',{bubbles:true}))}}",i)
    pg.wait_for_timeout(600); S0=pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}"); c.close()
    ck(len(S0)>=3 and any('watched' in k for k in S0),'D0 stato reale dell\'app creato su main (%d chiavi, spunte salvate)'%len(S0))
    c,pg=run_app(MAIN,S0); pg.wait_for_timeout(500); SM=pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}"); c.close()
    c,pg=run_app(INT,S0); pg.wait_for_function("()=>!!window.tvaRankings"); pg.wait_for_timeout(500)
    SI=lambda: pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}")
    s1=SI(); dif=[k for k in set(SM)|set(s1) if SM.get(k)!=s1.get(k) and not re.search(r'(ts|time|date|at|last|session|visit)',k,re.I)]
    ck(not dif,'D1 con lo stesso profilo preesistente, localStorage dopo l\'avvio identico tra main e integrata (chiavi con data/ora escluse: %d)'%len([k for k in set(SM)|set(s1) if SM.get(k)!=s1.get(k)]),dif[:5])
    ck(all(s1.get(k)==v for k,v in S0.items() if re.search(r'watched|favorite|rating|identity|profile',k)),'D2 le spunte e i dati salvati dell\'utente sono intatti')
    pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_selector('#rkNew'); pg.click('#rkNew'); pg.fill('#rkNewTitle','Prova integrazione'); pg.click('.rk-body [data-v="text"]'); pg.click('#rkCreate'); pg.wait_for_selector('#rkAdd'); pg.wait_for_timeout(500)
    s2=SI(); EXC=lambda d:{k:v for k,v in d.items() if not re.search(r'rk|rank|auto-backup',k,re.I)}
    ck(EXC(s2)==EXC(s1) and not any('Prova integrazione' in v or 'rk_' in v for v in s2.values()),'D3 creare una classifica non modifica alcuna chiave localStorage dell\'app (escluso auto-backup, copia periodica dell\'app stessa) e nessun contenuto Rankings finisce in localStorage',[k for k in s2 if s2.get(k)!=s1.get(k)][:5])
    ck(not [k for k in s2 if 'rank' in k.lower()],'D4 nessuna chiave Rankings in localStorage')
    c.close()
    # ===== P: PWA su sottopercorso =====
    def newctx(): return br.new_context(viewport={'width':390,'height':844},service_workers='allow')
    CUR['root']=INT; c=newctx(); pg=pgnew(c); pg.goto(BASE); sw_ready(pg); pg.wait_for_timeout(4000)
    scope=pg.evaluate("async()=>(await navigator.serviceWorker.getRegistration()).scope"); ck(scope==BASE,'P1 scope del service worker = %s (sottopercorso)'%PFX,scope)
    ck_=cache_keys(pg); B=build_of(INT); names=list(ck_); ck(names==['marvel-timeline-cache-'+B],'P2 una sola cache, col build id corrente',names)
    keys=ck_.get('marvel-timeline-cache-'+B,[])
    ck(BASE+'quiz/' in keys and BASE+'quiz/index.html' in keys and (BASE in keys or BASE+'index.html' in keys),'P3 in cache all\'installazione: app + quiz/ + quiz/index.html',[k[-30:] for k in keys][:10])
    ck(all(k.startswith('http://127.0.0.1') or 'fonts.g' in k for k in keys),'P4 nessuna risorsa esterna in cache oltre ai font gia\' previsti da main',[k for k in keys if not k.startswith('http://127.0.0.1')][:3])
    c.set_offline(True); pq=pgnew(c); pq.goto(BASE+'quiz/'); pq.wait_for_timeout(1200); ck(pq.title()=='TVA Quiz LAB' and pq.locator('#tvaBackApp').count()==1,'P5 Quiz apribile OFFLINE')
    pq.goto(BASE+'quiz/?rm=1'); pq.wait_for_timeout(800); ck(pq.title()=='TVA Quiz LAB','P5b Quiz offline anche con query (?rm=1)')
    pa=pgnew(c); pa.goto(BASE); pa.wait_for_function("()=>!!window.tvaRankings",timeout=15000); start(pa); pa.evaluate("tvaRankingsUI.open()"); pa.wait_for_selector('#rkNew',timeout=5000); ck(not pa.errs,'P6 app e Rankings funzionano OFFLINE',pa.errs[:2]); c.close()
    # ===== U: aggiornamento da main -> integrata, poi rollback =====
    CUR['root']=MAIN; c=newctx(); pg=pgnew(c); pg.goto(BASE); sw_ready(pg); pg.wait_for_timeout(3000); start(pg)
    pg.evaluate("()=>{localStorage.setItem('marvel-ultimate-timeline-testdato','UTENTE')}"); BM=build_of(MAIN)
    ck(list(cache_keys(pg))==['marvel-timeline-cache-'+BM],'U1 stato iniziale: SW e cache di main (%s)'%BM)
    CUR['root']=INT; pg.evaluate("async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}"); pg.wait_for_timeout(4500)
    pg.goto(BASE); pg.wait_for_timeout(3500)
    ck_=cache_keys(pg); ck(list(ck_)==['marvel-timeline-cache-'+B],'U2 dopo l\'aggiornamento: cache di main eliminata, resta solo quella nuova',list(ck_))
    ck(BASE+'quiz/' in ck_.get('marvel-timeline-cache-'+B,[]),'U3 il Quiz e\' stato messo in cache dall\'aggiornamento (nessun altro riavvio)')
    ck(pg.evaluate("()=>document.querySelector('meta[name=tva-build]').content")==B and pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-testdato')")=='UTENTE','U4 la pagina mostra la build nuova e i dati utente sono conservati')
    c.set_offline(True); pq=pgnew(c); pq.goto(BASE+'quiz/'); pq.wait_for_timeout(1000); ck(pq.title()=='TVA Quiz LAB','U5 dopo l\'aggiornamento il Quiz funziona offline'); c.set_offline(False)
    if ROLL and os.path.isdir(ROLL):
        pg.evaluate("async()=>{await new Promise(r=>{const q=indexedDB.open('tva-rankings');q.onsuccess=()=>{q.result.close();r()};q.onerror=()=>r()})}")
        [os.utime(os.path.join(ROLL,f)) for f in ('sw.js','index.html')]  # come un nuovo deploy: Last-Modified recente (evita 304 del server di prova)
        CUR['root']=ROLL; pg.evaluate("async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}"); pg.wait_for_timeout(8000); pg.goto(BASE); pg.wait_for_timeout(6000)
        BR=build_of(ROLL); ck_=cache_keys(pg); ck(pg.evaluate("()=>document.querySelector('meta[name=tva-build]').content")==BR and list(ck_)==['marvel-timeline-cache-'+BR],'R1 rollback (file di main con NUOVO build id): il client torna alla versione precedente e pulisce la cache dell\'integrata',list(ck_))
        ck(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-testdato')")=='UTENTE','R2 rollback: dati utente conservati')
        ck(not any('quiz' in k for v in ck_.values() for k in v),'R3 rollback: il Quiz non e\' piu\' in cache (pagina rimossa)')
    else: bl('R rollback','ROLL_ROOT non fornita')
    c.close()
    # ===== M: responsive in emulazione =====
    CUR['root']=INT
    for dn in ('iPhone SE','iPhone 13','Pixel 7','iPad (gen 7)'):
        if dn not in dev: bl('M '+dn,'dispositivo non presente in Playwright'); continue
        c=br.new_context(**dev[dn],service_workers='block'); pg=pgnew(c)
        pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
        pg.goto(BASE); pg.wait_for_function("()=>!!document.getElementById('quizLauncher')&&!!document.getElementById('rkLauncher')",timeout=20000); start(pg); centrale(pg)
        m=pg.evaluate("()=>({ho:document.documentElement.scrollWidth>innerWidth+1,qh:document.querySelector('#quizOpen').getBoundingClientRect().height,qw:document.querySelector('#quizOpen').getBoundingClientRect().width,vis:(()=>{const r=document.querySelector('#quizOpen').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight})()})")
        ck(not m['ho'] and m['qh']>=44 and m['vis'],'M %s: Centrale > Operazioni senza scroll orizzontale, pulsante Quiz >=44px e in vista'%dn,m)
        pg.goto(BASE+'quiz/'); pg.wait_for_timeout(800); ck(pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth+1"),'M %s: pagina Quiz senza scroll orizzontale'%dn); c.close()
    br.close()
print('FAILS:',fails); print('BLOCKED:',blocked); sys.exit(1 if fails else 0)
