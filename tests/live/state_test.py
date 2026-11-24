"""TVA Live - stato locale (init, lastVisit, seen, seenT) e assenza di avvisi duplicati con catalogo corretto."""
import json, re, copy, functools, http.server, socketserver, threading, datetime as dt
from playwright.sync_api import sync_playwright
import os
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.ThreadingTCPServer(('127.0.0.1',0),functools.partial(H,directory=ROOT)); threading.Thread(target=srv.serve_forever,daemon=True).start()
URL='http://127.0.0.1:%d/index.html'%srv.server_address[1]
cal=json.load(open(ROOT+'/assets/live/calendar.json')); man=json.load(open(ROOT+'/assets/live/manifest.json')); tr=json.load(open(ROOT+'/assets/live/trailers.json'))
KS='marvel-ultimate-timeline-live-state-v1'; KP='marvel-ultimate-timeline-live-v1'
seen={i['key']:{'d':i['date'],'c':i['confidence'],'s':i['state']} for i in cal['items']}
STATE0={'init':True,'lastVisit':1763900000000,'seen':seen,'seenT':[t['key'] for t in tr['items']]}
PREF0={'followed':['tmdb:movie:1003596'],'muted':[],'onlyUnwatched':False}
res=[]
def ok(n,c,x=''): res.append(bool(c)); print('PASS' if c else 'FAIL',n,x)
def corrected():
    c=copy.deepcopy(cal)
    for i in c['items']:
        if i['key']=='tmdb:movie:1003596':
            i['confidence']='provisional'; i['reason']='Data italiana da TMDB, non confermata. Fonti ufficiali per altri mercati: Regno Unito 16 dic 2026; USA 18 dic 2026'
            i['sources']=[i['sources'][0]]; i['dateBasis']='IT'; i['officialDates']=[{'market':'UK','date':'2026-12-16','channel':'Marvel Entertainment','url':'https://www.youtube.com/watch?v=hGaXQ8L_Z28','title':'x'}]
    return c
MODE={'cal':cal}
def routes(pg):
    def h(r):
        n=r.request.url.rsplit('/',1)[-1].split('?')[0]
        b={'calendar.json':MODE['cal'],'trailers.json':tr,'manifest.json':man}.get(n)
        r.fulfill(status=200,content_type='application/json',body=json.dumps(b)) if b is not None else r.fulfill(status=404,body='')
    pg.route(re.compile(r'.*/assets/live/.*'),h)
    pg.route(re.compile(r'https://posty2001\.github\.io/.*'),lambda r:r.abort('internetdisconnected'))
def boot(ctx):
    pg=ctx.new_page(); pg.errs=[]; pg.on('pageerror',lambda e:pg.errs.append(str(e))); routes(pg); pg.goto(URL); pg.wait_for_function("()=>window.tvaLive&&window.tvaLive.data().status==='ok'"); pg.wait_for_timeout(500); return pg
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(service_workers='block'); pg=ctx.new_page(); routes(pg); pg.goto(URL)
    pg.evaluate("([a,b,c,d])=>{localStorage.clear();localStorage.setItem(a,JSON.stringify(b));localStorage.setItem(c,JSON.stringify(d))}",[KS,STATE0,KP,PREF0]); pg.close()
    # 1) catalogo invariato: stato locale invariato, zero avvisi
    pg=boot(ctx); un=pg.evaluate("()=>window.tvaLive.unread()")
    st=json.loads(pg.evaluate("(k)=>localStorage.getItem(k)",KS))
    ok('stato locale presente dopo avvio: init, lastVisit, seen',st.get('init') is True and st.get('lastVisit')>=1763900000000 and set(st['seen'])==set(seen), list(st))
    ok('catalogo invariato: nessun avviso',un==0,un)
    pr=json.loads(pg.evaluate("(k)=>localStorage.getItem(k)",KP)); ok('preferenze: seguiti conservati',pr.get('followed')==['tmdb:movie:1003596'],pr)
    # 2) catalogo corretto (Doomsday declassato a provvisorio): un solo avviso, non duplicato
    MODE['cal']=corrected(); pg.reload(); pg.wait_for_function("()=>window.tvaLive&&window.tvaLive.data().status==='ok'"); pg.wait_for_timeout(500)
    u1=pg.evaluate("()=>window.tvaLive.unread()"); ok('declassamento a Provvisorio: nessun avviso (gli avvisi riguardano date, conferme e trailer); il badge cambia',u1==0,u1)
    ok('stato locale aggiornato al nuovo stato',json.loads(pg.evaluate("(k)=>localStorage.getItem(k)",KS))['seen']['tmdb:movie:1003596']['c']=='provisional')
    for i in range(3): pg.reload(); pg.wait_for_timeout(1800)
    u2=pg.evaluate("()=>window.tvaLive.unread()"); ok('3 ricariche: nessun avviso duplicato',u2==u1,(u1,u2))
    ctx.set_offline(True); pg.wait_for_timeout(800); ctx.set_offline(False); pg.wait_for_timeout(2000); pg.reload(); pg.wait_for_timeout(2000)
    u3=pg.evaluate("()=>window.tvaLive.unread()"); ok('offline/online/ricarica: avvisi invariati',u3==u1,(u1,u3))
    st=json.loads(pg.evaluate("(k)=>localStorage.getItem(k)",KS)); ok('seen aggiornato a provvisorio (nessuna ripetizione futura)',st['seen']['tmdb:movie:1003596']['c']=='provisional',st['seen']['tmdb:movie:1003596'])
    ok('nessun errore JS',not pg.errs,pg.errs); b.close()
print('RISULTATO',sum(res),'/',len(res)); raise SystemExit(0 if all(res) else 1)
