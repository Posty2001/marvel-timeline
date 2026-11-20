# Test integrazione 120 ritratti di test (Chromium)
import sys,json,time
from playwright.sync_api import sync_playwright
ROOT=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8790/'
URL=ROOT+'arcade/draft/'
R=[]
def rec(n,ok,note=''):R.append(bool(ok));print(('PASS' if ok else 'FAIL'),n,'' if ok else '— %s'%(str(note)[:300],),flush=True)
INS={'top':59,'bottom':34,'left':0,'right':0}
def page(b,w=390,h=844,sw='block',init=None,ctx=None):
    c=ctx or b.new_context(viewport={'width':w,'height':h},is_mobile=True,has_touch=True,service_workers=sw)
    pg=c.new_page();c.new_cdp_session(pg).send('Emulation.setSafeAreaInsetsOverride',{'insets':INS});pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)))
    pg.goto(URL);pg.wait_for_selector('#new');return c,pg
def start(pg,k='asgard',l='recluta'):
    pg.select_option('#scenario',k);pg.select_option('#cpu',l);pg.click('#new');pg.wait_for_selector('#pool .card');pg.wait_for_function("Object.keys(PORT).length>0||true")
def draft_all(pg):
    g=0
    while pg.evaluate("phase==='draft'") and g<40:
        g+=1
        if pg.evaluate("ORDER[turn]==='A'"):pg.locator('#pool .card').first.click();pg.click('#recruit');pg.wait_for_function("!recruiting",timeout=8000)
        else:pg.wait_for_timeout(100)
IMGS="[...document.querySelectorAll('%s img')].map(i=>({s:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0}))"
with sync_playwright() as p:
    b=p.chromium.launch()
    c,pg=page(b);start(pg)
    pg.wait_for_function("Object.keys(PORT).length===120",timeout=8000)
    ids=pg.evaluate("Object.keys(PORT)")
    rec('R1a il manifest associa 120 ritratti alle 120 carte (PORT)',len(ids)==120 and set(ids)==set(pg.evaluate("[...new Set(Object.keys(byId))]")),len(ids))
    bad=[];tot=0
    for i in range(0,120,5):
        sub=ids[i:i+5]
        pg.evaluate("(s)=>{offers=s.map(id=>byId[id]);sel=offers[0];render()}",sub)
        pg.wait_for_function("[...document.querySelectorAll('#pool img,#hero img')].every(i=>i.complete)",timeout=8000)
        pool=pg.evaluate(IMGS%'#pool > .card')
        pdata=pg.evaluate("[...document.querySelectorAll('#pool > .card')].map(e=>e.dataset.id)")
        hero=pg.evaluate(IMGS%'#hero')
        for j,id in enumerate(pdata):
            tot+=1
            if not(pool[j]['ok'] and pool[j]['s'].endswith('/%s.webp'%id)):bad.append(('pool',id,pool[j]))
        if not(hero and hero[0]['ok'] and hero[0]['s'].endswith('/%s.webp'%sub[0])):bad.append(('hero',sub[0],hero))
    rec('R1b tutte le 120 carte caricano il ritratto corretto (miniatura e carta selezionata)',not bad and tot==120,bad[:3])
    # ruolo/ squadre/ battaglia/ risultato in 4 scenari
    c.close()
    for k in('asgard','wakanda','quantum','battleworld'):
        c,pg=page(b);start(pg,k,'stratega');draft_all(pg);pg.wait_for_selector('#rolesp:not([hidden])')
        team=pg.evaluate("[A.map(c=>c.id),B.map(c=>c.id)]")
        pg.wait_for_function("[...document.querySelectorAll('#tme2 img,#tcpu2 img')].every(i=>i.complete)",timeout=8000)
        me=pg.evaluate(IMGS%'#tme2');cpu=pg.evaluate(IMGS%'#tcpu2')
        okm=len(me)==5 and all(x['ok'] for x in me) and [x['s'].split('/')[-1][:-5] for x in me]==team[0]
        okc=len(cpu)==5 and all(x['ok'] for x in cpu) and [x['s'].split('/')[-1][:-5] for x in cpu]==team[1]
        rec('R2 %s squadre: 5+5 ritratti corretti nella schermata ruoli'%k,okm and okc,(me,cpu))
        pg.click('#auto');pg.click('#go');pg.wait_for_selector('#battle:not([hidden])');pg.wait_for_timeout(1200)
        bt=pg.evaluate("[...document.querySelectorAll('#stage img,#bme img,#bcpu img')].map(i=>({s:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0}))")
        allids=set(team[0]+team[1])
        rec('R3 %s battaglia: ritratti presenti, caricati e delle carte in campo'%k,len(bt)>=2 and all(x['ok'] and x['s'].split('/')[-1][:-5] in allids for x in bt),bt[:3])
        pg.screenshot(path='/tmp/shots/rit_battaglia_%s.png'%k)
        pg.click('#skip');pg.wait_for_selector('#result:not([hidden])');pg.wait_for_timeout(1300)
        rs=pg.evaluate(IMGS%'#result .fan')
        rec('R4 %s risultato: 5 ritratti della squadra vincitrice'%k,len(rs)==5 and all(x['ok'] for x in rs),rs)
        pg.screenshot(path='/tmp/shots/rit_risultato_%s.png'%k)
        rec('R4b %s nessun errore JS'%k,not pg.errs,pg.errs[:2]);c.close()
    # fallback
    def fb(name,setup,expect_svg_ids=None):
        c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block');pg=c.new_page();pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)));setup(pg)
        pg.goto(URL);pg.wait_for_selector('#new');pg.click('#new');pg.wait_for_selector('#pool .card');pg.wait_for_timeout(1200)
        return c,pg
    # F1 un file manca
    c,pg=fb('x',lambda pg:pg.route('**/draft_portraits/*.webp',lambda r:r.abort() if any(x in r.request.url for x in ['/thor.webp','/bishop.webp']) else r.continue_()))
    pg.evaluate("(s)=>{offers=s.map(id=>byId[id]);sel=offers[0];render()}",['thor','bishop','loki','hela','odin']);pg.wait_for_timeout(1500)
    st=pg.evaluate("[...document.querySelectorAll('#pool > .card')].map(e=>({id:e.dataset.id,img:!!e.querySelector('img'),svg:!!e.querySelector('svg'),ok:(e.querySelector('img')||{complete:false,naturalWidth:0}).naturalWidth>0}))")
    rec('F1 se un ritratto manca (404/rete) compare il segnaposto SVG di quella carta e le altre restano illustrate',all(x['svg'] for x in st if x['id'] in('thor','bishop')) and all(x['ok'] for x in st if x['id'] in('loki','hela','odin')) and not pg.errs,st)
    c.close()
    # F2 file corrotto
    c,pg=fb('x',lambda pg:pg.route('**/draft_portraits/loki.webp',lambda r:r.fulfill(status=200,content_type='image/webp',body=b'not an image')))
    pg.evaluate("(s)=>{offers=s.map(id=>byId[id]);sel=offers[0];render()}",['loki','hela','odin','thor','bishop']);pg.wait_for_timeout(1500)
    rec('F2 immagine corrotta: fallback SVG, nessun errore',pg.evaluate("!!document.querySelector('#pool > .card[data-id=loki] svg') && !document.querySelector('#pool > .card[data-id=loki] img')") and not pg.errs)
    c.close()
    # F3 manifest assente
    c,pg=fb('x',lambda pg:pg.route('**/draft_portraits/manifest.json',lambda r:r.fulfill(status=404,body='')))
    rec('F3 manifest assente: tutte le carte usano il segnaposto SVG, gioco funzionante',pg.evaluate("document.querySelectorAll('#pool img').length===0 && document.querySelectorAll('#pool svg').length>=5") and not pg.errs)
    c.close()
    # F4 manifest con voce non valida / diritti dichiarati / status sconosciuto -> ignorata
    def bad_manifest(r):
        j=json.loads(r.fetch().text());j['portraits']['thor']['status']='candidate';j['portraits']['loki']['file']='../x.webp';j['portraits']['hela']['rights_confirmed']=True;j['portraits']['odin']['sha256']=None
        r.fulfill(status=200,content_type='application/json',body=json.dumps(j))
    c,pg=fb('x',lambda pg:pg.route('**/draft_portraits/manifest.json',bad_manifest))
    pg.evaluate("(s)=>{offers=s.map(id=>byId[id]);sel=offers[0];render()}",['thor','loki','hela','odin','bishop']);pg.wait_for_timeout(800)
    r=pg.evaluate("Object.fromEntries([...document.querySelectorAll('#pool > .card')].map(e=>[e.dataset.id,!!e.querySelector('img')]))")
    rec('F4 voci non valide (status, percorso, rights, sha) ignorate; voce valida usata',(not r['thor'] and not r['loki'] and not r['hela'] and not r['odin'] and r['bishop']),r)
    c.close()
    # offline con service worker
    c=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("try{sessionStorage.setItem('tva-return-home','1')}catch(e){}")
    pg.goto(ROOT,wait_until='domcontentloaded');t=0
    while t<60 and not pg.evaluate("!!(navigator.serviceWorker&&navigator.serviceWorker.controller)"):
        pg.wait_for_timeout(500);t+=1
        if t==20:pg.reload()
    pg.goto(URL);pg.wait_for_timeout(500)
    t=0
    while t<60:
        n=pg.evaluate("caches.keys().then(async ks=>{let n=0;for(const k of ks){const c=await caches.open(k);n+=(await c.keys()).filter(r=>r.url.includes('draft_portraits')).length}return n})")
        if n>=121:break
        pg.wait_for_timeout(500);t+=1
    rec('O1 precache SW: manifest + 120 ritratti in cache',n>=121,n)
    c.set_offline(True)
    pg.goto(URL,wait_until='domcontentloaded');pg.wait_for_selector('#new',timeout=8000);pg.click('#new');pg.wait_for_selector('#pool .card')
    pg.wait_for_function("Object.keys(PORT).length===120",timeout=8000);pg.wait_for_function("[...document.querySelectorAll('#pool img,#hero img')].every(i=>i.complete)",timeout=8000)
    imgs=pg.evaluate(IMGS%'#pool > .card')
    rec('O2 offline: selezione con 5 ritratti reali (da cache)',len(imgs)==5 and all(x['ok'] for x in imgs),imgs)
    draft_all(pg);pg.wait_for_selector('#rolesp:not([hidden])');pg.click('#auto');pg.click('#go');pg.wait_for_selector('#battle:not([hidden])');pg.wait_for_timeout(800)
    bt=pg.evaluate("[...document.querySelectorAll('#stage img')].map(i=>i.complete&&i.naturalWidth>0)")
    pg.click('#skip');pg.wait_for_selector('#result:not([hidden])');pg.wait_for_timeout(800)
    rs=pg.evaluate(IMGS%'#result .fan')
    rec('O3 offline: partita completa, battaglia e risultato con ritratti',len(bt)>=2 and all(bt) and len(rs)==5 and all(x['ok'] for x in rs) and not errs,(bt,rs,errs[:2]));c.close()
    b.close()
print('TOTALE %d test, %d PASS, %d FAIL'%(len(R),sum(R),len(R)-sum(R)))
