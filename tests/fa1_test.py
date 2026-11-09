# F-A1: autenticazione facoltativa email/password. ATTENZIONE: i test usano un MOCK dell'SDK Firebase Auth (la rete verso gstatic/Firebase e' bloccata nel sandbox):
# verificano UI, validazioni, stati, offline, CSP della pagina e protezione dei dati locali; NON provano l'SDK reale ne' il server Firebase (quelle prove sono BLOCKED).
import json,re,subprocess,os,sys,tempfile,socket,time
ROOT=os.environ.get('TVA_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_s=socket.socket(); _s.bind(('127.0.0.1',0)); PORT=_s.getsockname()[1]; _s.close()
SRV=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',ROOT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1.2)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%PORT
fails=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
APP_STUB="window.firebase=window.firebase||{apps:[],initializeApp:function(c){var a={name:'[DEFAULT]',options:c};this.apps.push(a);window.__mock.inits=(window.__mock.inits||0)+1;return a;}};"
MOCK=r"""
(function(){
  var M=window.__mock=window.__mock||{calls:[],delay:0,offline:false,neverInit:false,verifyFails:false};
  var KEY='__mockauth';
  function db(){try{return JSON.parse(sessionStorage.getItem(KEY)||'{"users":{},"cur":null}')}catch(e){return {users:{},cur:null}}}
  function save(d){sessionStorage.setItem(KEY,JSON.stringify(d))}
  var listeners=[]; var A={languageCode:null,currentUser:null};
  function mk(rec){return {uid:rec.uid,email:rec.email,get emailVerified(){return !!db().users[rec.email].v},
    sendEmailVerification:function(s){M.calls.push(['sendEmailVerification',s||null]);return later(function(){if(M.verifyFails)throw {code:'auth/unauthorized-continue-uri'}})},
    reload:function(){M.calls.push(['reload']);return later(function(){})}}}
  function later(fn){return new Promise(function(res,rej){setTimeout(function(){if(M.offline){return rej({code:'auth/network-request-failed'})}try{res(fn())}catch(e){rej(e)}},M.delay)})}
  function notify(){listeners.forEach(function(l){l(A.currentUser)})}
  var d0=db(); if(d0.cur&&d0.users[d0.cur]) A.currentUser=mk(d0.users[d0.cur]);
  A.onAuthStateChanged=function(cb){listeners.push(cb);if(!M.neverInit)setTimeout(function(){cb(A.currentUser)},5);return function(){listeners=listeners.filter(function(x){return x!==cb})}};
  A.createUserWithEmailAndPassword=function(e,p){M.calls.push(['create',e]);return later(function(){var d=db();if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e))throw {code:'auth/invalid-email'};if(p.length<6)throw {code:'auth/weak-password'};if(d.users[e])throw {code:'auth/email-already-in-use'};d.users[e]={uid:'u'+Object.keys(d.users).length,email:e,pw:p,v:false};d.cur=e;save(d);A.currentUser=mk(d.users[e]);setTimeout(notify,0);return {user:A.currentUser}})};
  A.signInWithEmailAndPassword=function(e,p){M.calls.push(['signIn',e]);return later(function(){var d=db();var r=d.users[e];if(!r||r.pw!==p)throw {code:'auth/invalid-credential'};d.cur=e;save(d);A.currentUser=mk(r);setTimeout(notify,0);return {user:A.currentUser}})};
  A.sendPasswordResetEmail=function(e,s){M.calls.push(['reset',e,s||null]);return later(function(){if(!db().users[e])throw {code:'auth/user-not-found'}})};
  A.signOut=function(){M.calls.push(['signOut']);return later(function(){var d=db();d.cur=null;save(d);A.currentUser=null;setTimeout(notify,0)})};
  M.verify=function(e){var d=db();d.users[e].v=true;save(d)};
  firebase.auth=function(){return A};
})();
"""
KEYS_JS="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return JSON.stringify(o)}"
def mkpage(b,mock=True,w=390,h=844,init=None):
    cx=b.new_context(viewport={'width':w,'height':h},service_workers='block'); pg=cx.new_page()
    errs=[]; csp=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('console',lambda m:csp.append(m.text) if 'Content Security Policy' in m.text or 'Refused to' in m.text else None)
    pg.add_init_script("window.__mock={calls:[],delay:0,offline:false,neverInit:false,verifyFails:false};"+(init or ''))
    def route(r):
        u=r.request.url
        if 'firebase-app-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body=APP_STUB)
        if 'firebase-database-compat' in u: return r.fulfill(status=200,content_type='application/javascript',body='')
        if 'firebase-auth-compat' in u:
            return r.fulfill(status=200,content_type='application/javascript',body=MOCK) if mock else r.abort()
        if 'identitytoolkit' in u or 'securetoken' in u or 'firebaseio' in u: return r.abort()
        return r.continue_()
    pg.route('**/*',route)
    return cx,pg,errs,csp
def go(pg):
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
def open_ops(pg):
    pg.evaluate("()=>document.getElementById('appTabMissioni').click()"); pg.wait_for_timeout(400)
    pg.evaluate("()=>document.getElementById('cenTab-operazioni').click()"); pg.wait_for_timeout(400)
    pg.evaluate("()=>document.getElementById('faAccount').scrollIntoView()"); pg.wait_for_timeout(200)
st=lambda pg: pg.evaluate("()=>document.getElementById('faAccount').dataset.faState")
msgt=lambda pg: pg.evaluate("()=>{const m=document.getElementById('faMsg');return m.hidden?'':m.textContent}")
calls=lambda pg: pg.evaluate("()=>window.__mock.calls.map(c=>c[0])")
def fill(pg,i,v): pg.fill('#'+i,v)
SEED={'marvel-ultimate-timeline-watched':'{"1":true,"5":true}','marvel-ultimate-timeline-ratings':'{"1":9}','marvelGuideCustomTimelineOrder':'[3,1,2]','marvelGuideActiveTimelineMode':'custom','marvel-ultimate-timeline-user-name':'Test','marvel-ultimate-timeline-badges-earned':'{"b1":1}','marvel-ultimate-timeline-missioni-xp-bonus':'{"x":120}'}
_html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
_js=re.search(r'<script id="fa1-js">(.*?)</script>',_html,re.S).group(1)
_code=re.sub(r'/\*.*?\*/','',_js,flags=re.S)
ck(not re.search(r'localStorage|\.database\(|\.ref\(|rooms/|sync/|users/|setItem|removeItem|document\.cookie',_code),'analisi statica: il modulo non usa localStorage, RTDB, sync/, rooms/, users/')
ck(not re.search(r'marvel-ultimate-timeline|marvelGuide|PROFILE_|esportaProfilo|sostituisciProfilo|normalizzaProfilo|AUTO_BACKUP|costruisciProfilo',_code),'analisi statica: il modulo non referenzia chiavi, funzioni o strutture del profilo (progressi, voti, XP, badge, preferenze, Timeline)')
ck(not re.search(r'signInWithPopup|signInWithRedirect|signInAnonymously|GoogleAuthProvider|signInWithCredential|signInWithCustomToken',_js),'analisi statica: nessun accesso Google/anonimo/popup/redirect')
_csp=re.search(r'Content-Security-Policy" content="([^"]+)"',_html).group(1)
ck('identitytoolkit.googleapis.com' in _csp and 'securetoken.googleapis.com' in _csp and '*.googleapis.com' not in _csp and 'frame-src' not in _csp,'CSP: due host Auth aggiunti, nessun wildcard googleapis, nessun frame')
ck(_html.count('firebase-auth-compat.js')==1 and 'firebasejs/10.13.0/firebase-auth-compat.js' in _html,'SDK Auth: stessa versione (10.13.0) e origine degli SDK esistenti')
with sync_playwright() as p:
    b=p.chromium.launch()
    cx,pg,errs,csp=mkpage(b); pg.goto(U); pg.wait_for_timeout(1200)
    pg.evaluate("(o)=>{for(const k in o)localStorage.setItem(k,o[k])}",SEED)
    pg.reload(); pg.wait_for_timeout(1200); go(pg); open_ops(pg); pg.wait_for_timeout(6500); before=pg.evaluate(KEYS_JS)   # baseline dopo che la scheda Missioni ha normalizzato i propri dati (comportamento preesistente)
    ck(pg.evaluate("()=>!!document.getElementById('faAccount')&&document.getElementById('faAccount').closest('.cen-grp')&&document.getElementById('faAccount').closest('.cen-grp').querySelector('h3').textContent")=='Account personale (facoltativo)','pannello nel gruppo «Account personale (facoltativo)» di Operazioni')
    ck(st(pg)=='out','avvio senza sessione: stato «out» (nessun login obbligatorio)',st(pg))
    ck(pg.evaluate("()=>firebase.auth().languageCode")=='it','auth.languageCode = it')
    ck(pg.evaluate("()=>window.__mock.inits")==1,'initializeApp una sola volta')
    ck(pg.evaluate("()=>!!document.querySelector('.card-wrap')"),'archivio locale utilizzabile senza account')
    ck(pg.evaluate("()=>typeof tvaAuth.getStatus==='function'&&Object.isFrozen(tvaAuth)"),'API pubblica minima e congelata')
    open_ops(pg)
    # --- registrazione: validazioni lato client
    pg.click('#faGoRegister'); ck(st(pg)=='register','vista registrazione')
    ck(pg.evaluate("()=>['faRegPw','faRegPw2','faLoginPw'].every(i=>document.getElementById(i).type==='password')"),'campi password di tipo password')
    ck(pg.evaluate("()=>document.getElementById('faRegEmail').autocomplete==='email'&&document.getElementById('faRegPw').autocomplete==='new-password'&&document.getElementById('faLoginPw').autocomplete==='current-password'"),'attributi autocomplete corretti (password manager iOS)')
    fill(pg,'faRegEmail','non-una-email'); fill(pg,'faRegPw','abcdefgh'); fill(pg,'faRegPw2','abcdefgh'); pg.click('#faRegBtn'); pg.wait_for_timeout(150)
    ck('non è valido' in msgt(pg) and calls(pg)==[],'email non valida: errore e nessuna chiamata',msgt(pg))
    fill(pg,'faRegEmail','a@test.it'); fill(pg,'faRegPw','abc'); fill(pg,'faRegPw2','abc'); pg.click('#faRegBtn'); pg.wait_for_timeout(150)
    ck('almeno 8' in msgt(pg) and calls(pg)==[],'password corta: errore e nessuna chiamata',msgt(pg))
    fill(pg,'faRegPw','abcdefgh'); fill(pg,'faRegPw2','abcdefgX'); pg.click('#faRegBtn'); pg.wait_for_timeout(150)
    ck('non coincidono' in msgt(pg) and calls(pg)==[],'conferma diversa: errore e nessuna chiamata',msgt(pg))
    ck(pg.evaluate("()=>document.getElementById('faRegPw2').getAttribute('aria-invalid')")=='true','campo errato marcato aria-invalid')
    # --- registrazione OK + doppio invio
    pg.evaluate("()=>window.__mock.delay=400")
    fill(pg,'faRegPw2','abcdefgh'); pg.click('#faRegBtn')
    pg.wait_for_timeout(100)
    ck(pg.evaluate("()=>document.getElementById('faAccount').getAttribute('aria-busy')")=='true' and pg.evaluate("()=>document.getElementById('faRegBtn').disabled"),'stato di caricamento: aria-busy e pulsante disabilitato')
    pg.evaluate("()=>document.getElementById('faFormRegister').requestSubmit()"); pg.wait_for_timeout(900)
    ck(calls(pg).count('create')==1,'doppio invio: una sola creazione',calls(pg))
    ck(st(pg)=='verify','dopo la registrazione: vista «email da verificare»',st(pg))
    sv=pg.evaluate("()=>window.__mock.calls.filter(c=>c[0]==='sendEmailVerification')")
    ck(len(sv)==1 and sv[0][1] and sv[0][1]['url'].startswith('http://127.0.0.1') and sv[0][1]['handleCodeInApp']==False,'email di verifica inviata con continue URL della pagina',sv)
    ck(pg.evaluate("()=>document.getElementById('faResendBtn').disabled"),'reinvio bloccato (cooldown)')
    ck(pg.evaluate("()=>['faRegPw','faRegPw2','faLoginPw'].every(i=>document.getElementById(i).value==='')"),'password cancellate dai campi dopo l\'invio')
    ck(pg.evaluate("()=>document.getElementById('faVerifyWho').textContent")=='a@test.it','email mostrata')
    # --- persistenza sessione dopo reload
    pg.reload(); pg.wait_for_timeout(1500); go(pg); open_ops(pg)
    ck(st(pg)=='verify','sessione persistente dopo ricarica (utente non verificato)',st(pg))
    # --- "Ho verificato" prima della verifica
    pg.click('#faCheckBtn'); pg.wait_for_timeout(300)
    ck(st(pg)=='verify' and 'non risulta ancora' in msgt(pg),'«Ho verificato» senza verifica: resta in attesa',msgt(pg))
    pg.evaluate("()=>window.__mock.verify('a@test.it')"); pg.click('#faCheckBtn'); pg.wait_for_timeout(500)
    ck(st(pg)=='in' and 'ACCOUNT VERIFICATO' in pg.inner_text('#faViewIn'),'dopo la verifica: account attivo',st(pg))
    ck('non sono ancora sincronizzati' in pg.inner_text('#faViewIn') and pg.evaluate("()=>document.getElementById('faSync').hidden"),'F-A2/F-A3 non attivate: nota «non sincronizzati» e pannello sync nascosto')
    # --- logout
    pg.click('#faLogoutBtn'); pg.wait_for_timeout(500)
    ck(st(pg)=='out' and 'invariati' in msgt(pg),'logout: torna «out», dati locali dichiarati invariati',msgt(pg))
    # --- login errato (messaggio generico) / corretto
    pg.click('#faGoLogin'); fill(pg,'faLoginEmail','a@test.it'); fill(pg,'faLoginPw','sbagliata1'); pg.click('#faLoginBtn'); pg.wait_for_timeout(700)
    ck(msgt(pg)=='Email o password non corretti.','login errato: messaggio generico',msgt(pg))
    fill(pg,'faLoginEmail','mai-registrata@test.it'); pg.click('#faLoginBtn'); pg.wait_for_timeout(700)
    ck(msgt(pg)=='Email o password non corretti.','email inesistente: stesso messaggio (no enumerazione)',msgt(pg))
    fill(pg,'faLoginEmail','a@test.it'); fill(pg,'faLoginPw','abcdefgh'); pg.click('#faLoginBtn'); pg.wait_for_timeout(1200)
    ck(st(pg)=='in','login corretto: account verificato attivo',st(pg))
    pg.click('#faLogoutBtn'); pg.wait_for_timeout(600)
    # --- email già registrata
    pg.click('#faGoRegister'); fill(pg,'faRegEmail','a@test.it'); fill(pg,'faRegPw','abcdefgh'); fill(pg,'faRegPw2','abcdefgh'); pg.click('#faRegBtn'); pg.wait_for_timeout(900)
    ck('Esiste già un account' in msgt(pg) and st(pg)=='register','email già in uso: messaggio chiaro',msgt(pg))
    # --- recupero password
    pg.click('#faFormRegister [data-fa-go="login"]'); pg.click('#faFormLogin [data-fa-go="reset"]'); ck(st(pg)=='reset','vista recupero password')
    fill(pg,'faResetEmail','sconosciuta@test.it'); pg.click('#faResetBtn'); pg.wait_for_timeout(900)
    m1=msgt(pg); ck('Se l’indirizzo è registrato' in m1,'reset email sconosciuta: risposta neutra',m1)
    fill(pg,'faResetEmail','a@test.it'); pg.click('#faResetBtn'); pg.wait_for_timeout(900)
    ck(msgt(pg)==m1,'reset email nota: stessa risposta neutra (nessuna enumerazione)')
    rs=pg.evaluate("()=>window.__mock.calls.filter(c=>c[0]==='reset')")
    ck(len(rs)==2 and rs[0][2] and rs[0][2]['url'].startswith('http://127.0.0.1'),'reset: chiamato con continue URL',rs)
    # --- offline
    pg.click('#faFormReset [data-fa-go="login"]'); n0=len(pg.evaluate("()=>window.__mock.calls"))
    cx.set_offline(True); pg.evaluate("()=>window.dispatchEvent(new Event('offline'))"); pg.wait_for_timeout(200)
    ck(pg.evaluate("()=>!document.getElementById('faNet').hidden"),'offline: banner visibile')
    fill(pg,'faLoginEmail','a@test.it'); fill(pg,'faLoginPw','abcdefgh'); pg.click('#faLoginBtn'); pg.wait_for_timeout(300)
    ck('Connessione assente' in msgt(pg) and len(pg.evaluate("()=>window.__mock.calls"))==n0,'offline: messaggio chiaro, nessuna chiamata',msgt(pg))
    cx.set_offline(False); pg.evaluate("()=>window.dispatchEvent(new Event('online'))"); pg.wait_for_timeout(200)
    ck(pg.evaluate("()=>document.getElementById('faNet').hidden"),'ritorno online: banner nascosto')
    # errore di rete a livello SDK
    pg.evaluate("()=>window.__mock.offline=true"); pg.click('#faLoginBtn'); pg.wait_for_timeout(500)
    ck('Connessione assente' in msgt(pg) and not pg.evaluate("()=>document.getElementById('faLoginBtn').disabled"),'errore di rete SDK: messaggio e pulsanti riabilitati',msgt(pg))
    pg.evaluate("()=>window.__mock.offline=false")
    # --- dati locali intoccati e nessun localStorage scritto dal modulo
    after=pg.evaluate(KEYS_JS)
    def norm(s):   # l'app riscrive la copia di sicurezza con un nuovo timestamp a ogni avvio (comportamento preesistente): si confronta il contenuto, non l'orario
        o=json.loads(s); k='marvel-ultimate-timeline-auto-backup'
        if k in o:
            try: j=json.loads(o[k]); j.pop('exportedAt',None); o[k]=json.dumps(j,sort_keys=True)
            except Exception: pass
        return json.dumps(o,sort_keys=True)
    before,after=norm(before),norm(after)
    if before!=after and 'marvel-ultimate-timeline-auto-backup' in json.loads(before) and 'marvel-ultimate-timeline-auto-backup' in json.loads(after):
        _b=json.loads(json.loads(before)['marvel-ultimate-timeline-auto-backup']); _a=json.loads(json.loads(after)['marvel-ultimate-timeline-auto-backup'])
        print('DIFF auto-backup:',{k:(str(_b.get(k))[:80],str(_a.get(k))[:80]) for k in set(_a)|set(_b) if _a.get(k)!=_b.get(k)})
    ck(before==after,'localStorage identico dopo l\'intero flusso (progressi, voti, XP, badge, Timeline, preferenze)',[k for k in set(json.loads(before))|set(json.loads(after)) if json.loads(before).get(k)!=json.loads(after).get(k)])
    ck(pg.evaluate("()=>localStorage.getItem('marvelGuideCustomTimelineOrder')")=='[3,1,2]' and pg.evaluate("()=>localStorage.getItem('marvelGuideActiveTimelineMode')")=='custom','Timeline personalizzata e modalità attiva invariate')
    ck(pg.evaluate("()=>typeof firebase.database==='undefined'"),'il modulo account non usa il database (nessun accesso a sync/rooms/users)')
    ck(csp==[],'nessuna violazione CSP in pagina',csp[:3])
    ck(errs==[],'nessun errore JS',errs[:3])
    # --- layout iPhone
    pg.click('#faFormLogin [data-fa-go="register"]'); pg.wait_for_timeout(150)
    lay=pg.evaluate("""()=>{const r=document.getElementById('faAccount');const b=r.getBoundingClientRect();const inp=[...r.querySelectorAll('input:not([hidden])')].filter(e=>e.offsetParent);const btn=[...r.querySelectorAll('button')].filter(e=>e.offsetParent);
      return {ow:document.documentElement.scrollWidth-document.documentElement.clientWidth,right:Math.round(b.right),vw:innerWidth,fs:Math.min(...inp.map(e=>parseFloat(getComputedStyle(e).fontSize))),minH:Math.min(...btn.map(e=>e.getBoundingClientRect().height)),n:inp.length}}""")
    ck(lay['ow']<=0 and lay['right']<=lay['vw'],'390px: nessuno scroll orizzontale',lay)
    ck(lay['fs']>=16,'input a 16px (niente zoom automatico Safari iOS)',lay)
    ck(lay['minH']>=44,'bersagli tattili >= 44px',lay)
    pg.screenshot(path='/tmp/fa1/shot_register_390.png')
    cx.close()
    # --- sessione che non risponde (watchdog)
    cx,pg,errs,csp=mkpage(b,init="window.__mock.neverInit=true;"); pg.goto(U); pg.wait_for_timeout(9800)
    ck(st(pg)=='unavailable','sessione che non risponde: dopo 8 s «non disponibile», nessun blocco',st(pg))
    ck(pg.evaluate("()=>!!document.querySelector('.card-wrap')"),'archivio locale comunque utilizzabile')
    cx.close()
    # --- SDK Auth non caricabile (es. prima visita offline)
    cx,pg,errs,csp=mkpage(b,mock=False); pg.goto(U); pg.wait_for_timeout(1500)
    ck(st(pg)=='unavailable','SDK Auth assente: stato «non disponibile»',st(pg))
    ck(errs==[],'SDK assente: nessun errore JS',errs[:3])
    cx.close()
    # --- invio email di verifica fallito alla registrazione
    cx,pg,errs,csp=mkpage(b,init="window.__mock.verifyFails=true;"); pg.goto(U); pg.wait_for_timeout(1000); go(pg); open_ops(pg)
    pg.click('#faGoRegister'); fill(pg,'faRegEmail','b@test.it'); fill(pg,'faRegPw','abcdefgh'); fill(pg,'faRegPw2','abcdefgh'); pg.click('#faRegBtn'); pg.wait_for_timeout(800)
    ck(st(pg)=='verify' and 'non è riuscito' in msgt(pg) and 'Dominio non autorizzato' in msgt(pg) and not pg.evaluate("()=>document.getElementById('faResendBtn').disabled"),'invio verifica fallito: account creato, errore mostrato, reinvio disponibile',msgt(pg))
    cx.close()
    # --- tema scuro: leggibilita' (contrasto testo)
    cx,pg,errs,csp=mkpage(b); pg.goto(U); pg.wait_for_timeout(1000); go(pg); open_ops(pg)
    pg.evaluate("()=>{const t=document.getElementById('darkModeToggle');t.checked=true;t.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    pg.screenshot(path='/tmp/fa1/shot_out_dark_390.png')
    cx.close()
    # --- uso senza login, uso con account, logout e CAMBIO ACCOUNT: i dati locali non vengono mai toccati dal modulo
    cx,pg,errs,csp=mkpage(b); pg.goto(U); pg.wait_for_timeout(1000); go(pg)
    ids=pg.evaluate("()=>[...document.querySelectorAll('.watch-check[data-item]')].slice(0,6).map(c=>c.dataset.item)")
    mark=lambda i: pg.evaluate("(i)=>{const c=document.querySelector('.watch-check[data-item=\"'+i+'\"]');c.checked=!c.checked;c.dispatchEvent(new Event('change',{bubbles:true}))}",i)
    _m=mark; mark=lambda i:(_m(i),pg.wait_for_timeout(350),pg.evaluate("()=>{const b=document.getElementById('missioneCelebrazioneChiudi');const d=document.getElementById('missioneCelebrazione');if(d&&!d.hidden&&b)b.click()}"),pg.wait_for_timeout(200))   # chiude l'eventuale celebrazione missione (comportamento dell'app)
    W=lambda: json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-watched')||'{}'"))
    PRO=lambda: norm(pg.evaluate(KEYS_JS))
    mark(ids[0]); pg.wait_for_timeout(300)
    ck(st(pg)=='out' and bool(W().get(ids[0])),'senza login: l\'archivio funziona (titolo segnato come visto e salvato)',W())
    open_ops(pg)
    pg.click('#faGoRegister'); fill(pg,'faRegEmail','x@test.it'); fill(pg,'faRegPw','abcdefgh'); fill(pg,'faRegPw2','abcdefgh'); pg.click('#faRegBtn'); pg.wait_for_timeout(700)
    pg.evaluate("()=>window.__mock.verify('x@test.it')"); pg.click('#faCheckBtn'); pg.wait_for_timeout(500)
    ck(st(pg)=='in','account A attivo')
    mark(ids[1]); pg.wait_for_timeout(300)
    ck(bool(W().get(ids[0])) and bool(W().get(ids[1])),'con account: i progressi continuano a essere salvati e quelli precedenti restano',W())
    snapA=PRO()
    pg.click('#faLogoutBtn'); pg.wait_for_timeout(600)
    ck(st(pg)=='out' and PRO()==snapA,'logout: dati locali identici')
    mark(ids[2]); pg.wait_for_timeout(300)
    ck(all(W().get(i) for i in ids[:3]),'dopo il logout: archivio ancora utilizzabile e dati intatti',W())
    snapB=PRO()
    pg.click('#faGoRegister'); fill(pg,'faRegEmail','y@test.it'); fill(pg,'faRegPw','abcdefgh'); fill(pg,'faRegPw2','abcdefgh'); pg.click('#faRegBtn'); pg.wait_for_timeout(700)
    pg.evaluate("()=>window.__mock.verify('y@test.it')"); pg.click('#faCheckBtn'); pg.wait_for_timeout(500)
    ck(st(pg)=='in' and PRO()==snapB,'cambio account (registrazione di un secondo account): dati locali identici',st(pg))
    pg.click('#faLogoutBtn'); pg.wait_for_timeout(500)
    pg.click('#faGoLogin'); fill(pg,'faLoginEmail','x@test.it'); fill(pg,'faLoginPw','abcdefgh'); pg.click('#faLoginBtn'); pg.wait_for_timeout(900)
    ck(st(pg)=='in' and PRO()==snapB,'cambio account (login del primo): dati locali identici e nessuna fusione tra account',st(pg))
    pg.reload(); pg.wait_for_timeout(6500)   # dopo il riavvio l'app normalizza e salva da sola la copia di sicurezza: si confronta il contenuto
    _d=lambda a,b2:[k for k in set(json.loads(a))|set(json.loads(b2)) if json.loads(a).get(k)!=json.loads(b2).get(k)]
    dd=_d(snapB,PRO()); print('  (chiavi cambiate al riavvio, per l\'app:',dd,')')
    ck(set(dd)<={'marvel-ultimate-timeline-auto-backup'} and all(W().get(i) for i in ids[:3]),'dopo riavvio con sessione attiva: dati identici (salvo la copia di sicurezza che l\'app riscrive da sola)',dd)
    ck(errs==[] and csp==[],'nessun errore JS/CSP nel flusso di uso/cambio account',(errs+csp)[:3])
    cx.close()
    b.close()
SRV.terminate()
print('FAILS:',fails); sys.exit(1 if fails else 0)
