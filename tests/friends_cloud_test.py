# TVA Friends — trasporto CLOUD. ATTENZIONE: SDK = MOCK, database = SIMULATORE con le regole PROPOSTE (users+friends). NON emulatore, NON Firebase reale.
# Il cloud e' disattivato nel prodotto (CLOUD_ENABLED=false): qui la pagina viene servita con la costante forzata a true SOLO per provare il codice.
import json,re,os,sys,socket,subprocess,time,urllib.request
ROOT=os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE=os.path.join(ROOT,'tests')
def freeport():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
PORT=freeport(); DBP=freeport()
U_=json.load(open(os.path.join(ROOT,'firebase','rules.users.proposed.json')))['rules']; F_=json.load(open(os.path.join(ROOT,'firebase','rules.friends.proposed.json')))['rules']
import tempfile
MR=os.path.join(tempfile.mkdtemp(),'merged.json'); json.dump({'rules':dict(U_,**F_)},open(MR,'w'))
SRV=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',ROOT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
DBS=subprocess.Popen(['node',os.path.join(HERE,'fa2_mockdb_server.js'),str(DBP),MR],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1.5)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%PORT
fails=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
src=open(os.path.join(HERE,'fa2_test.py'),encoding='utf-8').read()
exec(src[src.index('APP_STUB='):src.index('def seed_auth')])
def seed_auth(email,uid,verified=True):
    return "if(!sessionStorage.getItem('__authseeded')){sessionStorage.setItem('__authseeded','1');sessionStorage.setItem('__mockauth',%s);}"%json.dumps(json.dumps({'users':{email:{'uid':uid,'email':email,'pw':'x','v':verified}},'cur':email}))
def dbop(o):
    r=urllib.request.Request('http://127.0.0.1:%d/'%DBP,data=json.dumps(o).encode(),method='POST'); return json.loads(urllib.request.urlopen(r,timeout=10).read())
dump=lambda p: dbop({'op':'dump','path':p}).get('value')
_html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
assert 'var CLOUD_ENABLED = false;' in _html
PATCHED=_html.replace('var CLOUD_ENABLED = false;','var CLOUD_ENABLED = true;')
LS={'marvel-ultimate-timeline-watched':json.dumps({"001":True}),'marvel-ultimate-timeline-notes':json.dumps({"001":"SEGRETO-DIARIO-XYZ"})}
def mk(b,email,uid,verified=True,enabled=True):
    cx=b.new_context(viewport={'width':390,'height':844},service_workers='block'); pg=cx.new_page(); pg.errs=[]; pg.on('pageerror',lambda e:pg.errs.append(str(e))); pg.answer=True
    pg.on('dialog',lambda d:(d.accept() if pg.answer else d.dismiss()))
    pg.add_init_script("window.__mock={calls:[],offline:sessionStorage.getItem('__off')==='1'};"+seed_auth(email,uid,verified)+"if(!sessionStorage.getItem('__s')){sessionStorage.setItem('__s','1');"+"".join("localStorage.setItem(%s,%s);"%(json.dumps(k),json.dumps(v)) for k,v in LS.items())+"}")
    def route(r):
        u=r.request.url
        if u.split('?')[0]==U and enabled: return r.fulfill(status=200,content_type='text/html; charset=utf-8',body=PATCHED)
        if 'firebase-app-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=APP_STUB)
        if 'firebase-database-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=DBMOCK)
        if 'firebase-auth-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=AUTHMOCK)
        if 'mock-rtdb.firebaseio.com' in u:
            rq=urllib.request.Request('http://127.0.0.1:%d/'%DBP,data=r.request.post_data.encode(),method='POST')
            return r.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=urllib.request.urlopen(rq,timeout=10).read().decode())
        if any(h in u for h in ('identitytoolkit','securetoken','firebaseio','gstatic','tmdb')): return r.abort()
        return r.continue_()
    pg.route('**/*',route); return cx,pg
def start(pg):
    pg.goto(U); pg.wait_for_timeout(1800)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
def opn(pg,t=None): pg.evaluate("(t)=>tvaFriends.open(t)",t); pg.wait_for_timeout(250); pg.evaluate("()=>document.querySelectorAll('#tfRoot details.tf-sec').forEach(d=>{d.open=true})")
def tab(pg,t): pg.click('#tfTab-'+t); pg.wait_for_timeout(200); pg.evaluate("()=>document.querySelectorAll('#tfRoot details.tf-sec').forEach(d=>{d.open=true})")
def store(pg): return json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1')") or 'null')
def toast(pg): return pg.inner_text('#tfToast')
FA='uidAAAAAAAAAAAAAAAAAAAA'; FB='uidBBBBBBBBBBBBBBBBBBBB'; FC='uidCCCCCCCCCCCCCCCCCCCC'
with sync_playwright() as p:
    b=p.chromium.launch()
    # prodotto reale: cloud disattivato, nessun controllo cloud in UI
    cx0,P0=mk(b,'a@test.it',FA,enabled=False); start(P0); opn(P0); ck(P0.evaluate("()=>tvaFriends.cloudEnabled()")==False and not P0.query_selector('#tfCloudPub'),'build di prodotto: cloud disattivato e senza controlli cloud')
    cxA,A=mk(b,'a@test.it',FA); cxB,B=mk(b,'b@test.it',FB); cxC,C=mk(b,'c@test.it',FC); [start(x) for x in (A,B,C)]
    ck(A.evaluate("()=>tvaFriends.cloudEnabled()")==True,'prova: cloud forzato a true (solo test)')
    for pg,n in ((A,'Alice'),(B,'Bruno'),(C,'Carlo')):
        opn(pg); pg.fill('#tfName',n); pg.click('#tfSaveMe'); pg.wait_for_timeout(150)
        ck('Cloud attivo' in pg.inner_text('#tfCloudNote'),'%s: cloud pronto con account verificato'%n)
    A.click('#tfCloudPub'); A.wait_for_timeout(500); B.click('#tfCloudPub'); B.wait_for_timeout(500); C.click('#tfCloudPub'); C.wait_for_timeout(500)
    vA,vB,vC=store(A)['vid'],store(B)['vid'],store(C)['vid']
    ck(dump('handles/'+vA)['uid']==FA and dump('handles/'+vB)['uid']==FB,'handle pubblicati con il proprio uid')
    ck(json.loads(dump('profiles/'+FA)['card'])['name']=='Alice' and 'SEGRETO' not in json.dumps(dump('profiles')),'profilo pubblico: solo carta (nessun dato privato)')
    # invito Nexus via cloud
    tab(A,'nexus'); A.click('#tfNxInvite'); A.fill('#tfCloudTo',vB); A.click('#tfCloudSend'); A.wait_for_timeout(700); ck('Inviato via cloud' in toast(A),'A invia l\'invito a B via cloud',toast(A))
    ib=dump('inbox/'+FB) or {}; ck(len(ib)==1 and list(ib.values())[0]['from']==FA and list(ib.values())[0]['inv']==True,'inbox di B: 1 messaggio, mittente = uid di A, marcato invito')
    ck('SEGRETO' not in json.dumps(dump('inbox')),'inbox: nessun dato privato')
    tab(B,'com'); B.click('#tfCloudPoll'); B.wait_for_timeout(900); ck('elaborati' in toast(B),'B controlla i messaggi',toast(B)); ck(dump('inbox/'+FB) is None,'messaggio consumato e rimosso dall\'inbox')
    tab(B,'nexus'); ck(B.evaluate("()=>document.querySelectorAll('[data-req]').length")==1 and not [1 for v in store(B)['nexus'].values()],'B: richiesta in attesa, nessun legame automatico')
    B.click('[data-act="nx-accept"]'); B.wait_for_timeout(300); B.fill('#tfCloudTo',vA); B.click('#tfCloudSend'); B.wait_for_timeout(900)
    ck(dump('links/'+FB) and list(dump('links/'+FB).values())==[True],'B registra il legame nel proprio nodo links')
    ck('Inviato via cloud' in toast(B),'B risponde via cloud',toast(B))
    tab(A,'com'); A.click('#tfCloudPoll'); A.wait_for_timeout(900); tab(A,'nexus'); ck(A.evaluate("()=>document.querySelectorAll('[data-vid]').length")==1,'A: legame attivo dopo la risposta via cloud')
    ck(dump('links/'+FA) and list(dump('links/'+FA).values())==[True],'A registra il legame (links)')
    # messaggio non-invito: A->B consentito (legame di B verso A), C->A negato (nessun legame)
    tab(A,'sfide'); A.click('#tfDuelNew'); A.fill('#tfCloudTo',vB); A.click('#tfCloudSend'); A.wait_for_timeout(800)
    ck(dump('inbox/'+FB) is not None,'sfida A->B recapitata (legame esistente lato B)')
    tab(C,'sfide'); C.click('#tfDuelNew'); C.fill('#tfCloudTo',vA); C.click('#tfCloudSend'); C.wait_for_timeout(800)
    ck('NON riuscito' in toast(C) and (dump('inbox/'+FA) or {})=={},'C (non collegato) NON puo\' inviare una sfida ad A: negato dal database',toast(C))
    # invito spam di C: consentito come invito, ma A puo' bloccare
    tab(C,'nexus'); C.click('#tfNxInvite'); C.fill('#tfCloudTo',vA); C.click('#tfCloudSend'); C.wait_for_timeout(800); ck(len(dump('inbox/'+FA) or {})==1,'invito di C recapitato (solo inviti ammessi senza legame)')
    # B legge l'inbox di A direttamente: negato
    r=B.evaluate("""async()=>{const f=(o)=>fetch('https://mock-rtdb.firebaseio.com/__op',{method:'POST',body:JSON.stringify(Object.assign({auth:{uid:'uidBBBBBBBBBBBBBBBBBBBB',token:{email_verified:true}}},o))}).then(r=>r.json());return [await f({op:'once',path:'inbox/uidAAAAAAAAAAAAAAAAAAAA'}),await f({op:'once',path:'links/uidAAAAAAAAAAAAAAAAAAAA'})]}""")
    ck(not r[0]['ok'] and not r[1]['ok'],'B non legge inbox e links di A')
    # offline: invio fallisce con messaggio, nessuna perdita
    A.evaluate("()=>{sessionStorage.setItem('__off','1');window.__mock.offline=true}"); tab(A,'sfide'); A.click('#tfDuelNew'); A.wait_for_timeout(300)
    A.evaluate("()=>{window.dispatchEvent(new Event('offline'))}")
    n0=len(store(A)['duels']); A.click('#tfDuelNew'); A.wait_for_timeout(300); ck(len(store(A)['duels'])==n0+1,'offline: i duelli si creano comunque (codice manuale)')
    A.fill('#tfCloudTo',vB); A.click('#tfCloudSend'); A.wait_for_timeout(500); ck('NON riuscito' in toast(A) and 'codice' in toast(A),'offline: invio cloud fallisce con messaggio chiaro e alternativa (codice)',toast(A))
    ck(A.input_value('#tfOutCode').startswith('TVA1.'),'offline: il codice manuale resta disponibile')
    ck(not [e for pg in (A,B,C) for e in pg.errs],'nessun errore JS',[e for pg in (A,B,C) for e in pg.errs][:3])
    ck('SEGRETO-DIARIO-XYZ' not in json.dumps(dump('')),'database: nessun dato privato in tutto il DB simulato')
    b.close()
SRV.terminate(); DBS.terminate(); print('FAILS:',fails); sys.exit(1 if fails else 0)
