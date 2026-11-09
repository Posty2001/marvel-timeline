# F-A2/F-A3: profilo per account + sync cloud. ATTENZIONE: SDK Firebase = MOCK; database = SIMULATORE con le regole PROPOSTE (non emulatore, non Firebase reale).
# Prova: logica client (migrazione, isolamento, conflitti, CAS, offline, backup) e autorizzazioni contro il simulatore. NON prova l'SDK reale ne' il server Firebase (BLOCKED).
import json,re,subprocess,os,sys,socket,time,urllib.request
ROOT=os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE=os.path.join(ROOT,'tests')
def freeport():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
PORT=freeport(); DBP=freeport()
SRV=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',ROOT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
DBS=subprocess.Popen(['node',os.path.join(HERE,'fa2_mockdb_server.js'),str(DBP)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1.5)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%PORT
PATCHED_HTML=open(os.path.join(os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'index.html'),encoding='utf-8').read()
assert 'var ACCT_SYNC_ENABLED = false;' in PATCHED_HTML
PATCHED_HTML=PATCHED_HTML.replace('var ACCT_SYNC_ENABLED = false;','var ACCT_SYNC_ENABLED = true;')
fails=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
def dbop(o):
    r=urllib.request.Request('http://127.0.0.1:%d/'%DBP,data=json.dumps(o).encode(),method='POST'); return json.loads(urllib.request.urlopen(r,timeout=10).read())
dump=lambda p: dbop({'op':'dump','path':p}).get('value')
CFG="window.FIREBASE_CONFIG_TEST=1;"
APP_STUB="window.firebase=window.firebase||{apps:[],initializeApp:function(c){var a={name:'[DEFAULT]',options:c};this.apps.push(a);return a;}};"
DBMOCK=r"""
(function(){
  var M=window.__mock;
  function auth(){var u=firebase.auth().currentUser; return u?{uid:u.uid,token:{email_verified:!!u.emailVerified,email:u.email}}:null}
  function call(o){ if(M.offline) return Promise.reject({code:'network-error',message:'offline'});
    o.auth=auth(); M.ops=(M.ops||0)+1;
    return fetch('https://mock-rtdb.firebaseio.com/__op',{method:'POST',body:JSON.stringify(o)}).then(function(r){return r.json()}).then(function(j){ if(!j.ok) return Promise.reject({code:'PERMISSION_DENIED',message:'permission_denied '+(j.why||'')}); return j; }); }
  function snap(v){return {val:function(){return v===undefined?null:v},exists:function(){return v!==null&&v!==undefined}}}
  function ref(p){
    var r={path:p,
      child:function(c){return ref(p+'/'+c)},
      once:function(){return call({op:'once',path:p}).then(function(j){return snap(j.value)})},
      set:function(v){var u={};u[p]=v;M.writes=(M.writes||[]).concat([p]);return call({op:'write',updates:u})},
      remove:function(){var u={};u[p]=null;return call({op:'write',updates:u})},
      update:function(up){var u={};Object.keys(up).forEach(function(k){u[p+'/'+k]=up[k]});M.writes=(M.writes||[]).concat([p+'*']);return call({op:'write',updates:u})},
      on:function(ev,cb,eb){var last,stop=false;var tick=function(){ if(stop)return; r.once().then(function(s){var v=s.val(); if(JSON.stringify(v)!==last){last=JSON.stringify(v);cb(s)}},function(e){if(eb)eb(e)}).then(function(){ if(!stop) setTimeout(tick,600)}) }; r.__stops=(r.__stops||[]).concat([function(){stop=true}]); setTimeout(tick,0)},
      off:function(){(r.__stops||[]).forEach(function(f){f()})}};
    return r;}
  var D=function(){return {ref:ref}}; D.ServerValue={TIMESTAMP:{'.sv':'timestamp'}};
  firebase.database=D;
})();
"""
AUTHMOCK=r"""
(function(){
  var M=window.__mock; var KEY='__mockauth';
  function db(){try{return JSON.parse(sessionStorage.getItem(KEY)||'{"users":{},"cur":null}')}catch(e){return {users:{},cur:null}}}
  var listeners=[]; var A={languageCode:null,currentUser:null};
  function mk(rec){return {uid:rec.uid,email:rec.email,get emailVerified(){return !!db().users[rec.email].v},
    getIdToken:function(){return M.offline?Promise.reject({code:'auth/network-request-failed'}):Promise.resolve('tok')},sendEmailVerification:function(){return Promise.resolve()},reload:function(){return Promise.resolve()}}}
  var d0=db(); if(d0.cur&&d0.users[d0.cur]) A.currentUser=mk(d0.users[d0.cur]);
  A.onAuthStateChanged=function(cb){listeners.push(cb);setTimeout(function(){cb(A.currentUser)},5);return function(){}};
  A.signOut=function(){var d=db();d.cur=null;sessionStorage.setItem(KEY,JSON.stringify(d));A.currentUser=null;listeners.forEach(function(l){l(null)});return Promise.resolve()};
  firebase.auth=function(){return A};
})();
"""
def seed_auth(email,uid,verified=True):
    return "if(!sessionStorage.getItem('__authseeded')){sessionStorage.setItem('__authseeded','1');sessionStorage.setItem('__mockauth',%s);}"%json.dumps(json.dumps({'users':{email:{'uid':uid,'email':email,'pw':'x','v':verified}},'cur':email}))
def mkdev(b,email,uid,verified=True,ls=None):
    cx=b.new_context(viewport={'width':390,'height':844},service_workers='block'); pg=cx.new_page(); pg.dialogs=[]
    errs=[]; pg.errs=errs; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.confirm_answer=True; pg.confirm_log=[]
    def dlg(d):
        pg.confirm_log.append(d.message)
        d.accept() if pg.confirm_answer else d.dismiss()
    pg.on('dialog',dlg)
    init="window.__mock={calls:[],offline:sessionStorage.getItem('__off')==='1'};"+seed_auth(email,uid,verified)
    if ls: init+="if(!sessionStorage.getItem('__seeded')){sessionStorage.setItem('__seeded','1');"+"".join("localStorage.setItem(%s,%s);"%(json.dumps(k),json.dumps(v)) for k,v in ls.items())+"}"
    pg.add_init_script(init)
    def route(r):
        u=r.request.url
        if u==U or u.endswith('/index.html'): return r.fulfill(status=200,content_type='text/html; charset=utf-8',body=PATCHED_HTML)
        if 'firebase-app-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=APP_STUB)
        if 'firebase-database-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=DBMOCK)
        if 'firebase-auth-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=AUTHMOCK)
        if 'mock-rtdb.firebaseio.com' in u:
            rq=urllib.request.Request('http://127.0.0.1:%d/'%DBP,data=r.request.post_data.encode(),method='POST')
            return r.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=urllib.request.urlopen(rq,timeout=10).read().decode())
        if 'identitytoolkit' in u or 'securetoken' in u or 'firebaseio' in u or 'gstatic' in u: return r.abort()
        return r.continue_()
    pg.route('**/*',route)
    return cx,pg
def setoff(pg,v):
    pg.evaluate('(v)=>{sessionStorage.setItem("__off",v?"1":"0");window.__mock.offline=v}',v)
def prep(pg):
    pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.getElementById('appTabMissioni').click()"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.getElementById('cenTab-operazioni').click()"); pg.wait_for_timeout(300)
def ensure_cfg(): pass
S=lambda pg: pg.evaluate("()=>window.tvaAccountSync&&tvaAccountSync.state()")
def wait_state(pg,st,t=15000):
    try: pg.wait_for_function("(s)=>window.tvaAccountSync&&tvaAccountSync.state().state===s",arg=st,timeout=t); return True
    except Exception: return False
KEYS_JS="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}"
ADDITIVE=('marvel-ultimate-timeline-acct-base','marvel-ultimate-timeline-acct-sync','marvel-ultimate-timeline-profile-owner','marvel-ultimate-timeline-device-id','marvel-ultimate-timeline-auto-backup')
def userkeys(pg): return {k:v for k,v in pg.evaluate(KEYS_JS).items() if k not in ADDITIVE}
DA={'marvel-ultimate-timeline-watched':'{"001":true,"005":true}','marvel-ultimate-timeline-ratings':'{"001":4.5}','marvel-ultimate-timeline-notes':'{"001":"nota segreta di A"}','marvel-ultimate-timeline-user-name':'Aaa'}
DB_={'marvel-ultimate-timeline-watched':'{"002":true}','marvel-ultimate-timeline-ratings':'{"002":3.5}','marvel-ultimate-timeline-notes':'{"002":"nota di B"}','marvel-ultimate-timeline-user-name':'Bbb'}
FA='uidAAAA'; FB='uidBBBB'
_html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
cfg_ok='INSERISCI_QUI' not in re.search(r'FIREBASE_CONFIG\s*=\s*\{[^}]*\}',_html,re.S).group(0)
ck(cfg_ok,'FIREBASE_CONFIG presente e non segnaposto (sync abilitabile)')
with sync_playwright() as p:
    b=p.chromium.launch()
    # ===== S1 migrazione: dati locali -> account A (conferma esplicita), nessuna perdita
    cxA1,A1=mkdev(b,'a@test.it',FA,ls=DA); prep(A1)
    before=userkeys(A1)
    ck(dump('users')is None,'DB vuoto prima dell\'attivazione (nessun upload automatico)')
    ck(A1.evaluate("()=>!document.getElementById('faSyncOn').hidden"),'pulsante «Attiva sincronizzazione» visibile')
    A1.confirm_answer=False; A1.click('#faSyncOn'); A1.wait_for_timeout(1500)
    ck(dump('users')is None and A1.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-acct-sync')")is None,'migrazione RIFIUTATA: nulla inviato, flag non impostato')
    ck(userkeys(A1)==before,'migrazione rifiutata: dati locali identici')
    A1.confirm_answer=True; A1.click('#faSyncOn'); ck(wait_state(A1,'synced'),'migrazione confermata: stato synced',S(A1))
    ck(any('Caricare nel tuo account' in m for m in A1.confirm_log),'consenso esplicito richiesto prima dell\'upload')
    prof=dump('users/%s/profile'%FA); meta=dump('users/%s/meta'%FA)
    ck(isinstance(prof,str) and 'nota segreta di A' in prof and '"001":4.5' in prof.replace(' ',''),'profilo A nel cloud contiene note/voti locali')
    ck(meta and meta['rev']==1 and meta['schema']==1 and isinstance(meta['updatedAt'],int) and len(meta['device'])>=6,'meta: rev 1, schema 1, updatedAt server, device',meta)
    bk=dump('users/%s/backups'%FA) or {}
    ck(len(bk)==1 and list(bk.values())[0]['reason']=='migrazione' and re.match(r'^[0-9a-f]{64}$',list(bk.values())[0]['sha256']) and list(bk.values())[0]['profile']==prof,'backup «migrazione» creato con SHA-256 e contenuto = profilo caricato')
    ck(userkeys(A1)==before,'migrazione: dati locali (progressi, voti, note, impostazioni) INVARIATI')
    ck(A1.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-profile-owner')")==FA,'proprietario locale = uid A')
    # persistenza dopo reload (auto-riattivazione) e nessuna nuova scrittura se uguale
    A1.evaluate("()=>window.__mock.writes=[]"); A1.reload(); prep(A1)
    ck(wait_state(A1,'synced'),'dopo ricarica: sync riattivata e allineata',S(A1))
    A1.wait_for_timeout(5000)
    ck(dump('users/%s/meta/rev'%FA)==1,'nessuna riscrittura inutile (rev ancora 1)')
    # ===== S2 isolamento: account B sul proprio dispositivo
    cxB,B1=mkdev(b,'b@test.it',FB,ls=DB_); prep(B1)
    B1.click('#faSyncOn'); ck(wait_state(B1,'synced'),'B: migrazione e sync',S(B1))
    pB=dump('users/%s/profile'%FB)
    ck(pB and 'nota di B' in pB and 'nota segreta di A' not in pB,'profilo B separato: contiene solo i dati di B')
    ck('nota di B' not in dump('users/%s/profile'%FA),'profilo A non contiene dati di B')
    # autorizzazioni: B tenta di leggere/scrivere i dati di A tramite il client (token B)
    r=B1.evaluate("""async()=>{const out={};const f=(o)=>fetch('https://mock-rtdb.firebaseio.com/__op',{method:'POST',body:JSON.stringify(Object.assign({auth:{uid:'uidBBBB',token:{email_verified:true}}},o))}).then(r=>r.json());
      out.read=await f({op:'once',path:'users/uidAAAA/profile'});out.write=await f({op:'write',updates:{'users/uidAAAA/profile':'{}'}});out.enum=await f({op:'once',path:'users'});
      out.unv=await f({op:'once',path:'users/uidBBBB/profile',auth:{uid:'uidBBBB',token:{email_verified:false}}});return out}""")
    ck(not r['read']['ok'] and not r['write']['ok'] and not r['enum']['ok'],'AUTORIZZAZIONI: B non legge, non scrive, non enumera i dati di A',r)
    ck(not r['unv']['ok'],'AUTORIZZAZIONI: token con email non verificata respinto anche sul proprio uid')
    ck('nota segreta di A' in dump('users/%s/profile'%FA),'dopo i tentativi di B il profilo di A e\' intatto')
    # ===== S3 secondo dispositivo di A, vuoto: conflitto, nessuna applicazione automatica
    cxA2,A2=mkdev(b,'a@test.it',FA); prep(A2)
    k0=userkeys(A2)
    A2.click('#faSyncOn'); ck(wait_state(A2,'conflict'),'dispositivo 2 vuoto: cloud con dati -> conflitto, non applicato',S(A2))
    ck(userkeys(A2)==k0,'conflitto: dati locali del dispositivo 2 non modificati in automatico')
    ck(dump('users/%s/meta/rev'%FA)==1,'conflitto: il cloud non e\' stato sovrascritto')
    A2.click('#syncRestoreBtn'); A2.wait_for_timeout(3500); prep(A2)
    ck(wait_state(A2,'synced'),'ripristino dal cloud scelto: dispositivo 2 allineato',S(A2))
    ck('nota segreta di A' in json.dumps(userkeys(A2)),'dispositivo 2 ha ora i dati di A')
    # ===== S4 aggiornamento da altro dispositivo: stato «update», applicazione esplicita
    A1.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-ratings','{\"001\":4.5,\"005\":3}')"); A1.reload(); prep(A1)
    # A1 ha una modifica locale non sincronizzata + il cloud e' invariato -> deve sincronizzare (push) se uguale base; verifichiamo rev
    A1.wait_for_timeout(6000)
    ck(wait_state(A1,'synced',8000),'A1: modifica locale inviata (cloud era la sua base)',S(A1))
    ck(dump('users/%s/meta/rev'%FA)==2,'rev incrementata a 2 con CAS',dump('users/%s/meta'%FA))
    ck(wait_state(A2,'update',15000),'dispositivo 2 (invariato) vede lo stato «update» e non applica da solo',S(A2))
    k2=userkeys(A2); ck('"005":3' not in k2.get('marvel-ultimate-timeline-ratings',''),'stato update: dati locali ancora invariati')
    A2.click('#syncRestoreBtn'); A2.wait_for_timeout(3500); prep(A2)
    ck(wait_state(A2,'synced'),'«Applica aggiornamento»: dispositivo 2 allineato',S(A2))
    ck('"005":3' in userkeys(A2).get('marvel-ultimate-timeline-ratings',''),'dispositivo 2 ha il nuovo voto')
    # ===== S5 CAS: dispositivo obsoleto non sovrascrive
    # A1 offline con modifica locale; A2 (online) invia rev 3; poi A1 torna online -> conflitto vero, nessuna sovrascrittura
    setoff(A1,True)
    A1.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','Da A1')"); A1.reload(); prep(A1)
    A2.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','Da A2')"); A2.reload(); prep(A2)
    ck(wait_state(A2,'synced') ,'A2 sincronizzato dopo modifica',S(A2)); A2.wait_for_timeout(2000)
    ck(dump('users/%s/meta/rev'%FA)==3,'A2 ha scritto rev 3',dump('users/%s/meta'%FA))
    ck(S(A1)['state']=='offline','A1 offline: stato offline, modifica locale conservata',S(A1))
    ck(userkeys(A1).get('marvel-ultimate-timeline-user-name')=='Da A1','A1 offline: dato locale non perso')
    setoff(A1,False); A1.reload(); prep(A1)
    A1.wait_for_timeout(1500)
    s1=S(A1)
    ck(s1['state'] in ('conflict','update','synced','connecting'),'A1 (obsoleto) non in errore di autorizzazione',s1)
    prof_now=dump('users/%s/profile'%FA)
    ck('Da A2' in prof_now and 'Da A1' not in prof_now,'CAS/conflitto: il cloud non e\' stato sovrascritto dal dispositivo obsoleto')
    ck(wait_state(A1,'conflict',15000),'A1: conflitto reale rilevato (modifiche locali + cloud cambiato)',S(A1))
    # scelta esplicita "usa questo dispositivo": backup del cloud PRIMA, poi sostituzione
    nb0=len(dump('users/%s/backups'%FA) or {})
    A1.click('#syncUseLocalBtn'); A1.wait_for_timeout(3500)
    bks=dump('users/%s/backups'%FA) or {}
    ck(any(v['reason']=='prima-sostituzione' and 'Da A2' in v['profile'] for v in bks.values()),'«Usa questo dispositivo»: backup cloud (Da A2) creato prima di sostituire',[v['reason'] for v in bks.values()])
    ck('Da A1' in dump('users/%s/profile'%FA),'cloud sostituito con A1 solo dopo scelta esplicita')
    # ===== S6 dati di un altro account sul dispositivo: mai caricati
    cxF,F1=mkdev(b,'b@test.it',FB,ls=dict(DA,**{'marvel-ultimate-timeline-profile-owner':FA})); 
    dbop({'op':'raw','path':'users/%s'%FB,'value':None})
    prep(F1); F1.click('#faSyncOn'); F1.wait_for_timeout(3500)
    ck(S(F1)['state']=='foreign','dispositivo con dati dell\'account A, accesso come B: stato «foreign»',S(F1))
    ck(dump('users/%s'%FB)is None,'nessun dato dell\'account A e\' stato caricato nello spazio di B')
    ck(not any('Caricare nel tuo account' in m for m in F1.confirm_log),'nessuna proposta di upload dei dati altrui')
    # ===== S7 offline: modifiche locali preservate, riallineamento al ritorno
    wait_state(A1,'synced',10000); setoff(A1,True)
    A1.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','Offline A1')"); A1.reload(); prep(A1); A1.wait_for_timeout(3000)
    ck(S(A1)['state']=='offline' and userkeys(A1).get('marvel-ultimate-timeline-user-name')=='Offline A1','offline: stato offline e modifica locale conservata',S(A1))
    # ===== S8 backup: verifica e ripristino, alterazione rilevata
    setoff(A1,False); A1.reload(); prep(A1); ck(wait_state(A1,'synced',20000),'ritorno online: riallineamento automatico',S(A1))
    ck('Offline A1' in (dump('users/%s/profile'%FA) or ''),'modifica fatta offline inviata al ritorno online')
    bk=dump('users/%s/backups'%FA); bid=[k for k,v in bk.items() if v['reason']=='migrazione'][0]
    dbop({'op':'raw','path':'users/%s/backups/%s/profile'%(FA,bid),'value':bk[bid]['profile'].replace('nota segreta','NOTA MANOMESSA')})
    A1.click('#faBackups summary'); A1.click('#faBackupRefresh'); A1.wait_for_timeout(1500)
    kb=userkeys(A1)
    A1.click('#faBackupList li[data-bk="%s"] [data-bk-act="restore"]'%bid); A1.wait_for_timeout(2500)
    ck(userkeys(A1)==kb,'backup alterato: ripristino rifiutato, dati locali invariati')
    ck('SHA-256' in A1.evaluate("()=>document.body.innerText") or 'alterato' in A1.evaluate("()=>document.body.innerText"),'backup alterato: motivo (SHA-256) mostrato all\'utente')
    dbop({'op':'raw','path':'users/%s/backups/%s/profile'%(FA,bid),'value':bk[bid]['profile']})
    A1.click('#faBackupRefresh'); A1.wait_for_timeout(1500)
    A1.click('#faBackupList li[data-bk="%s"] [data-bk-act="restore"]'%bid); A1.wait_for_timeout(4500); prep(A1)
    ck(any('Ripristinare il backup' in m for m in A1.confirm_log),'ripristino backup: conferma esplicita richiesta')
    ck('nota segreta di A' in json.dumps(userkeys(A1)),'backup integro: ripristinato in locale')
    # ===== S9 logout: sync sospesa, dati locali intatti
    kk=userkeys(A1); A1.click('#faLogoutBtn'); A1.wait_for_timeout(1500)
    ck(userkeys(A1)==kk,'logout: dati locali invariati')
    ck(A1.evaluate("()=>tvaAccountSync.state().state")in('off',) ,'logout: sincronizzazione sospesa',S(A1))
    # ===== S10 modifiche offline NON perse in caso di conflitto; copia di sicurezza prima di ripristinare
    FC='uidCCCC'
    cxC1,C1=mkdev(b,'c@test.it',FC,ls=DA); prep(C1); C1.click('#faSyncOn'); ck(wait_state(C1,'synced'),'C1: sync iniziale',S(C1))
    cxC2,C2=mkdev(b,'c@test.it',FC); prep(C2); C2.click('#faSyncOn'); wait_state(C2,'conflict'); C2.click('#syncRestoreBtn'); C2.wait_for_timeout(3500); prep(C2); ck(wait_state(C2,'synced'),'C2 allineato',S(C2))
    setoff(C1,True); C1.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','C1-offline')"); C1.reload(); prep(C1)
    C2.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','C2-online')"); C2.reload(); prep(C2); wait_state(C2,'synced'); C2.wait_for_timeout(2500)
    setoff(C1,False); C1.reload(); prep(C1)
    ck(wait_state(C1,'conflict',20000),'C1 torna online con cloud cambiato: conflitto (non sovrascrive in silenzio)',S(C1))
    ck(userkeys(C1).get('marvel-ultimate-timeline-user-name')=='C1-offline','conflitto aperto: la modifica offline e\' ancora sul dispositivo')
    ck('C2-online' in (dump('users/%s/profile'%FC) or '') and 'C1-offline' not in (dump('users/%s/profile'%FC) or ''),'conflitto aperto: il cloud non e\' stato toccato')
    C1.click('#syncRestoreBtn'); C1.wait_for_timeout(3500); prep(C1)
    ck('C2-online' in json.dumps(userkeys(C1)),'ripristino dal cloud: dispositivo ora allineato')
    ab=C1.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-auto-backup')")
    ck(ab and 'C1-offline' in ab,'copia di sicurezza locale contiene la modifica offline (recuperabile)')
    # ===== S11 logout e cambio account: nessuna esposizione dei dati precedenti
    C1.click('#faBackups summary'); C1.click('#faBackupRefresh'); C1.wait_for_timeout(1200)
    ck(C1.evaluate("()=>document.getElementById('faBackupList').children.length")>0,'prima del logout: elenco backup dell\'account C presente')
    C1.click('#faLogoutBtn'); C1.wait_for_timeout(1500)
    ck(C1.evaluate("()=>document.getElementById('faBackupList').textContent.trim()==='' || document.getElementById('faBackups').hidden"),'dopo il logout: elenco backup non piu\' visibile/vuoto')
    ck(S(C1)['state']=='off','dopo il logout: nessuna connessione al cloud',S(C1))
    ops0=C1.evaluate("()=>window.__mock.ops||0"); C1.wait_for_timeout(6000)
    ck(C1.evaluate("()=>window.__mock.ops||0")==ops0,'dopo il logout: nessuna richiesta al database')
    FD='uidDDDD'; before_d=dump('users')
    C1.evaluate("(a)=>{sessionStorage.setItem('__mockauth',a)}",json.dumps({'users':{'d@test.it':{'uid':FD,'email':'d@test.it','pw':'x','v':True}},'cur':'d@test.it'}))
    C1.reload(); prep(C1); C1.wait_for_timeout(6000)
    ck(S(C1)['state'] in ('off',) or S(C1)['mode']!='account','cambio account: l\'account D NON si connette in automatico con il flag dell\'account C',S(C1))
    ck(dump('users/%s'%FD) is None,'cambio account: nulla scritto nello spazio di D')
    C1.click('#faSyncOn'); C1.wait_for_timeout(4000)
    ck(S(C1)['state']=='foreign','cambio account: D su dispositivo con dati di C -> «foreign», nessun upload',S(C1))
    ck(dump('users/%s'%FD) is None,'cambio account: dopo l\'attivazione ancora nulla nel cloud di D')
    ck(C1.evaluate("()=>document.getElementById('faBackupList').textContent.indexOf('C1-offline')<0 && document.getElementById('faBackupList').textContent.indexOf('C2-online')<0"),'cambio account: nessun contenuto di C nell\'elenco backup di D')
    allerr=[e for pg in (A1,A2,B1,F1,C1,C2) for e in pg.errs]
    ck(not allerr,'nessun errore JS nella pagina',allerr[:3])
    b.close()
SRV.terminate(); DBS.terminate()
print('FAILS:',fails); sys.exit(1 if fails else 0)
