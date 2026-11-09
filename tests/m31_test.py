from playwright.sync_api import sync_playwright
import re,sys,json,importlib.util,subprocess
R=[]
def ck(n,c,d=''): R.append(c); print(('PASS ' if c else 'FAIL ')+n+(' '+str(d)[:200] if not c else ''))
IMG=open('/home/claude/work/assets/images/tva/cronologie.webp','rb').read()
def run(map_voci=None,custom=None,tmdb_ok=True,off=False,fn=None):
    with sync_playwright() as p:
        b=p.chromium.launch(); cx=b.new_context(viewport={'width':390,'height':844},service_workers='block'); pg=cx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); reqs=[]
        def idx(route):
            r=route.fetch(); t=r.text()
            if map_voci is not None: t=re.sub(r'id="tmdbMap">.*?</script>','id="tmdbMap">'+json.dumps({'voci':map_voci})+'</script>',t,flags=re.S) 
            route.fulfill(response=r,body=t)
        pg.route('**/index.html',idx)
        def tm(route):
            reqs.append(route.request.url)
            route.fulfill(body=IMG,content_type='image/webp') if tmdb_ok else route.abort()
        pg.route('**/image.tmdb.org/**',tm)
        if off: pg.add_init_script("localStorage.setItem('tvaTmdbOff','1')")
        pg.goto('http://localhost:8124/index.html'); pg.wait_for_timeout(1200)
        if custom: pg.evaluate("(c)=>{window.TVA_IMG_MANIFEST['item:100']=c}",custom)
        out=fn(pg,reqs); out['errs']=errs; b.close(); return out
def hero(pg):
    pg.evaluate("()=>tvaAtlas2.openOpera('item-100')"); pg.wait_for_timeout(900)
    return pg.evaluate("""()=>{const i=document.querySelector('.m3-poster');return {has:!!i,src:i&&i.getAttribute('data-src'),ok:i&&i.naturalWidth>0,srcset:i&&i.srcset,url:i&&i.currentSrc,attr:!!document.querySelector('.m3-tmdb a[href*=themoviedb]'),artHidden:[...document.querySelectorAll('.d4-hero-opr svg')].every(s=>getComputedStyle(s.parentElement).display==='none'||true)}}""")
V={'100':{'t':'tv','id':1,'p':'/abc_DEF-1.jpg'}}
r=run({},fn=lambda pg,rq:{**hero(pg),'cnt':pg.evaluate("tvaTmdb.count()"),'rq':len(rq)}); ck('default: nessuna locandina, nessuna richiesta TMDB',not r['has'] and r['cnt']==0 and r['rq']==0,r)
r=run(V,fn=lambda pg,rq:{**hero(pg),'rq':rq}); ck('TMDB: locandina caricata + attribuzione',r['has'] and r['src']=='tmdb' and r['ok'] and r['attr'],r)
ck('TMDB: srcset w342 1x / w500 2x, https',bool(re.search(r'https://image\.tmdb\.org/t/p/w342/abc_DEF-1\.jpg 1x, https://image\.tmdb\.org/t/p/w500/abc_DEF-1\.jpg 2x',r['srcset'] or '')),r['srcset'])
r=run(V,custom={'src':'assets/images/tva/cronologie.webp','w':1280,'h':720,'licence':'t','verified':True},fn=lambda pg,rq:{**hero(pg),'rq':len(rq)}); ck('priorita: personalizzata vince su TMDB',r['has'] and r['src'] is None and r['rq']==0 and not r['attr'],r)
r=run(V,custom={'src':'assets/images/tva/nope.webp','w':1,'h':1,'licence':'t','verified':True},fn=lambda pg,rq:hero(pg)); ck('personalizzata rotta -> TMDB',r['has'] and r['src']=='tmdb',r)
r=run(V,custom={'src':'assets/images/tva/cronologie.webp','licence':'t','verified':False},fn=lambda pg,rq:{**hero(pg)}); ck('non verificata ignorata -> TMDB',r['src']=='tmdb',r)
r=run(V,tmdb_ok=False,fn=lambda pg,rq:hero(pg)); ck('TMDB in errore -> emblema (nessuna img rotta)',not r['has'],r)
r=run(V,off=True,fn=lambda pg,rq:{**hero(pg),'rq':len(rq)}); ck('interruttore tvaTmdbOff',not r['has'] and r['rq']==0,r)
def tl(pg,rq):
    pg.evaluate("()=>{const d=document.querySelector('#item-100 details.card');d.open=true;d.scrollIntoView()}"); pg.wait_for_timeout(1200)
    return pg.evaluate("()=>{const i=document.querySelector('#item-100 .detail-panel .m3-tl');return {has:!!i,ok:!!i&&(i.getAttribute('src')||'').indexOf('https://image.tmdb.org/t/p/w154/')===0,vis:!!document.querySelector('#item-100').offsetParent,cur:i&&i.currentSrc,cmp:i&&i.complete,first:(f=>f.className==='td-info'&&f.firstElementChild?f.firstElementChild.className:f.className)(document.querySelector('#item-100 .detail-panel').firstElementChild)}}")
r=run(V,fn=tl); ck('timeline: (M3.2) locandina nella riga principale, non nel pannello',not r['has'] and r['first']=='detail-row',r)  # TD1/TD2: le righe dati sono raggruppate in .td-info; il test verifica che la prima voce sia ancora una riga dati (nessuna locandina nel pannello)
r=run({},fn=tl); ck('timeline: senza mappa nessuna miniatura',not r['has'],r)
r=run(V,fn=lambda pg,rq:{**hero(pg)}); ck('nessun errore JS',not r['errs'],r['errs'])
s=open('/home/claude/work/index.html',encoding='utf-8').read()
ck('nessuna chiave/token nel codice',not re.search(r'api_key=|Bearer |TMDB_API_KEY|TMDB_READ_TOKEN',s))
# tool con API simulata
sp=importlib.util.spec_from_file_location('ts','/home/claude/work/tools/tmdb_sync.py'); ts=importlib.util.module_from_spec(sp); sp.loader.exec_module(ts)
def fake(path,**q):
    if path=='/search/movie': return {'results':[{'id':5,'title':'Spider-Man','release_date':'2002-05-01'},{'id':6,'title':'Altro','release_date':'2002-01-01'}]}
    if path=='/search/tv': return {'results':[{'id':9,'name':'Loki'},{'id':10,'name':'Loki'}]}
    return {}
ts.api=fake
ck('tool: film con match esatto',ts.risolvi('001','Spider-Man','2002','film')==('movie',5,None))
ck('tool: ambiguo -> da rivedere (nessun abbinamento a caso)',ts.risolvi('x','Loki S2','2023','serie')[0] is None)
ck('tool: anno lontano rifiutato',ts.risolvi('x','Spider-Man','2010','film')[0] is None)
print('TOT',sum(R),'/',len(R))
