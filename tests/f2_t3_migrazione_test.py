"""Migrazione identita' e backup JSON sulla build INTEGRATA. Non modifica l'app: semina localStorage via init script. Riferimento = main 8f04c21 esportato da git."""
import sys,json,hashlib,threading,http.server,socketserver,copy,os
from playwright.sync_api import sync_playwright
import subprocess,tempfile
ROOT=os.environ.get('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); OUT=os.environ.get('F2_OUT',tempfile.mkdtemp()); PORT=8771
MAINROOT=tempfile.mkdtemp()
_ar=subprocess.run('git -C %s archive 8f04c21 | tar -x -C %s'%(ROOT,MAINROOT),shell=True,capture_output=True)
if _ar.returncode or not os.path.exists(MAINROOT+'/index.html'): print('BLOCKED riferimento main non esportabile da git'); sys.exit(0)
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def log_message(s,*a): pass
    def end_headers(s): s.send_header('Cache-Control','no-store'); super().end_headers()
class S(socketserver.ThreadingMixIn,http.server.HTTPServer): daemon_threads=True; allow_reuse_address=True
srv=S(('127.0.0.1',PORT),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
class H2(H):
    def __init__(s,*a,**k): http.server.SimpleHTTPRequestHandler.__init__(s,*a,directory=MAINROOT,**k)
srv2=S(('127.0.0.1',8773),H2); threading.Thread(target=srv2.serve_forever,daemon=True).start()
P='marvel-ultimate-timeline-'
def h(x): return hashlib.sha256((x or '').encode()).hexdigest()[:12]
import time
NOW=int(time.time()*1000)-3600000
V1='vabc123def4'; V2='vzzz999aaa1'
def base_store(me=None):
    return {"v":1,"vid":"vme000000a1","me":me or {"name":"Franco","emblem":3,"color":2,"motto":"Nel multiverso","univ":"Terra-616","ch":"Loki","share":{"emblem":True,"motto":False,"univ":False,"ch":False,"tid":True}},
    "nexus":{V1:{"vid":V1,"name":"Giulia","emblem":1,"color":1,"motto":"ciao","since":1760000000000,"status":"linked"},V2:{"vid":V2,"name":"Marco","emblem":2,"color":0,"motto":"","since":1760000100000,"status":"linked"}},
    "pendingOut":{"abcdefgh12345678":{"ts":NOW}},
    "reqs":{"rq_aaaaaaaa11":{"kind":"nx.invite","from":{"vid":"vnew111111a","name":"Luca","emblem":0,"color":0,"motto":""},"ts":NOW,"nonce":"abcdefgh12345678"}},
    "teams":{"tm_bbbbbbbb22":{"id":"tm_bbbbbbbb22","name":"Squadra Alfa","emblem":2,"goal":50,"owner":"vme000000a1","created":1760000400000,"members":{V1:{"name":"Giulia","seen":10,"ts":1760000400000}},"log":[{"ts":1760000500000,"text":"Giulia si e' unita"}]}},
    "evenings":{"ev_cccccccc33":{"id":"ev_cccccccc33","title":"Maratona Avengers","item":"012","when":1770000000000,"place":"Casa","note":"popcorn","host":"vme000000a1","hostName":"Franco","guests":{V1:{"name":"Giulia","rsvp":"si","ts":1760000600000}},"mine":"si","cancelled":False}},
    "duels":{"du_dddddddd44":{"id":"du_dddddddd44","seed":12345,"n":10,"qh":"abcdef01","by":V1,"byName":"Giulia","created":1760000700000,"scores":{V1:{"name":"Giulia","score":7,"total":10,"ms":50000,"ts":1760000800000}},"played":False},
             "du_eeeeeeee55":{"id":"du_eeeeeeee55","seed":777,"n":5,"qh":"abcdef02","by":"vme000000a1","byName":"Franco","created":1760000900000,"scores":{"vme000000a1":{"name":"Franco","score":4,"total":5,"ms":20000,"ts":1760001000000}},"played":True}},
    "shared":{"out":{},"inn":{"sh_ffffffff66":{"id":"sh_ffffffff66","kind":"picks","title":"Da vedere","desc":"","items":["001","002"],"ts":1760001100000,"from":V1,"fromName":"Giulia"}}},
    "inbox":[{"id":"n_aaaaaa11","k":"duel","ts":1760001200000,"read":False,"text":"Giulia ti sfida a un duello Marvel (10 domande).","ref":{"tab":"sfide","id":"du_dddddddd44"}},{"id":"n_bbbbbb22","k":"ev","ts":1760001300000,"read":True,"text":"Nuova serata","ref":{"tab":"serate","id":"ev_cccccccc33"}}],
    "seen":{},"best":{"solo":8,"n":10}}
PROG={ 'watched':json.dumps({"001":True,"002":True,"003":True}), 'badges-earned':json.dumps({"primo":"2026-10-01"}), 'rewards':json.dumps({"x":1}),
       'missioni-xp-bonus':'250','ratings':json.dumps({"001":9}), 'notes':json.dumps({"001":"bello"}), 'favorites':json.dumps(["001"]), 'last-watched':'003',
       'tessera-id':'VAR-243153','tessera-look':json.dumps({"m":"x","fi":"oro"}), 'dark-mode':'1'}
def seed(store=None,name='Franco',fav='Loki',prog=PROG,rawstore=None,drop=()):
    d={}
    for k,v in prog.items():
        if k not in drop: d[P+k]=v
    if name is not None: d[P+'user-name']=name
    if fav is not None: d[P+'fav-char']=fav
    if rawstore is not None: d[P+'tvafriends-v1']=rawstore
    elif store is not None: d[P+'tvafriends-v1']=json.dumps(store)
    return d
PROTECTED=['watched','badges-earned','rewards','missioni-xp-bonus','ratings','notes','favorites','last-watched','tessera-id','tessera-look','dark-mode']
R=[]
def run(name,seedd,check,pre=None,two_loads=False,extra=None):
    global REF
    with sync_playwright() as p:
        bm=p.chromium.launch(); cm=bm.new_context(**p.devices['iPhone 14'])
        cm.add_init_script("(()=>{const d=%s;try{if(!sessionStorage.getItem('__seeded')){sessionStorage.setItem('__seeded','1');for(const k in d)localStorage.setItem(k,d[k]);}}catch(e){}})();"%json.dumps(seedd))
        pm=cm.new_page(); pm.goto('http://127.0.0.1:8773/'); pm.wait_for_timeout(1800)
        REF=pm.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}"); bm.close()
    with sync_playwright() as p:
        b=p.chromium.launch(); cx=b.new_context(**p.devices['iPhone 14'],accept_downloads=True)
        init="(d)=>{ if(sessionStorage.getItem('__seeded'))return; sessionStorage.setItem('__seeded','1'); for(const k in d) localStorage.setItem(k,d[k]); }"
        cx.add_init_script("(()=>{const d=%s;try{if(!sessionStorage.getItem('__seeded')){sessionStorage.setItem('__seeded','1');for(const k in d)localStorage.setItem(k,d[k]);}}catch(e){}})();"%json.dumps(seedd))
        if pre: cx.add_init_script(pre)
        pg=cx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:140]))
        pg.goto('http://127.0.0.1:%d/'%PORT); pg.wait_for_timeout(1800)
        if two_loads: pg.reload(); pg.wait_for_timeout(1500)
        snap=lambda: pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}")
        after=snap()
        res={'name':name}
        try: ok,note=check(pg,seedd,after,cx)
        except Exception as e: ok,note=False,'ECCEZIONE '+str(e)[:200]
        res['ok']=ok; res['note']=note+(' | DIFF protetti: %s'%prot_same.last if getattr(prot_same,'last',None) else '');prot_same.last=[]; res['errors']=errs[:3]; R.append(res); print(('PASS' if ok else 'FAIL'),name,'-',note); b.close()
REF={}
def prot_same(seedd,after):
    bad=[(k,str(REF.get(P+k))[:30],str(after.get(P+k))[:30]) for k in PROTECTED if REF.get(P+k)!=after.get(P+k)]
    prot_same.last=bad
    return bad
def store_cnt(s):
    try: o=json.loads(s)
    except Exception: return None
    return {k:(len(o[k]) if isinstance(o[k],(dict,list)) else o[k]) for k in ['nexus','pendingOut','reqs','teams','evenings','duels','inbox']}|{'shared_inn':len(o['shared']['inn'])}
IDK=P+'identity-v1'; BAK=P+'identity-premigration-v1'; FRK=P+'tvafriends-v1'

# S1 completo, nessun conflitto
def c1(pg,sd,a,cx):
    bad=prot_same(sd,a); idn=json.loads(a.get(IDK,'null')); bak=json.loads(a.get(BAK,'null'))
    cnt0=store_cnt(sd[FRK]); cnt1=store_cnt(a[FRK])
    ok=not bad and idn and bak and 'cf' not in idn and cnt0==cnt1 and bak['userName']=='Franco' and bak['me']['name']=='Franco'
    return ok,'protetti invariati=%s identity=%s backup=%s collezioni prima=%s dopo=%s'%(not bad,bool(idn),bool(bak),cnt0==cnt1,cnt0==cnt1)
run('S1 profilo completo, nessun conflitto',seed(base_store()),c1)
# S2 conflitto nome
me2=base_store()['me']; me2['name']='Francesco'
def c2(pg,sd,a,cx):
    idn=json.loads(a.get(IDK,'null')); bad=prot_same(sd,a)
    ok=idn and idn.get('cf',{}).get('name')=={'f':'Francesco','t':'Franco'} and a[P+'user-name']=='Franco' and not bad and json.loads(a[FRK])['me']['name']=='Francesco'
    return ok,'cf.name=%s, user-name invariato=%s, me.name Friends invariato=%s'%(idn.get('cf'),a[P+'user-name']=='Franco',json.loads(a[FRK])['me']['name']=='Francesco')
run('S2 conflitto nome Friends≠Tessera',seed(base_store(me2)),c2)
# S3 conflitto personaggio
me3=base_store()['me']; me3['ch']='Thor'
def c3(pg,sd,a,cx):
    idn=json.loads(a.get(IDK,'null')); ok=idn and idn.get('cf',{}).get('ch')=={'f':'Thor','t':'Loki'} and idn['ch']=='Loki' and a[P+'fav-char']=='Loki'
    return ok,'cf.ch=%s ch identita=%s'%(idn.get('cf',{}).get('ch'),idn.get('ch'))
run('S3 conflitto personaggio',seed(base_store(me3)),c3)
# S4 senza tessera-id
def c4(pg,sd,a,cx):
    ok=json.loads(a.get(IDK,'null')) is not None and a.get(P+'tessera-id') in (None,'') or True
    import re
    bad=[x for x in prot_same(sd,a) if x[0]!='tessera-id']; fmt=bool(re.fullmatch(r'VAR-[0-9]{6}',a.get(P+'tessera-id','') or ''))
    return (IDK in a) and not bad and fmt, 'identity creata=%s, altri protetti invariati=%s, tessera-id generato dall app (casuale per design) formato valido=%s'%(IDK in a,not bad,fmt)
run('S4 senza tessera-id',seed(base_store(),drop=('tessera-id',)),c4)
# S5 nessun dato
def c5(pg,sd,a,cx): return (IDK not in a and BAK not in a),'nessuna identity/backup creata dal nulla: identity=%s backup=%s'%(IDK in a,BAK in a)
run('S5 installazione vuota',{},c5)
# S6 store corrotto
def c6(pg,sd,a,cx):
    raw=a.get(FRK); ok=not prot_same(sd,a)
    return ok,'store corrotto: raw originale conservato=%s (bak=%s) identity=%s protetti invariati=%s'%(raw=='{non json',(FRK+'-bak') in a,IDK in a,not prot_same(sd,a))
run('S6 store Friends corrotto',seed(rawstore='{non json'),c6)
# S7 quota piena sul backup: setItem fallisce per la chiave backup
pre7="(()=>{const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(String(k).indexOf('identity-premigration')>=0)throw new DOMException('Quota','QuotaExceededError');return o.call(this,k,v)}})();"
def c7(pg,sd,a,cx): return (IDK not in a and BAK not in a and not prot_same(sd,a) and a[FRK]==sd[FRK]),'backup non scrivibile -> migrazione annullata: identity=%s store identico=%s protetti invariati=%s'%(IDK in a,a[FRK]==sd[FRK],not prot_same(sd,a))
run('S7 quota piena sul backup',seed(base_store()),c7,pre=pre7)
# S7b quota piena sulla chiave identity
pre7b="(()=>{const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(String(k).indexOf('identity-v1')>=0)throw new DOMException('Quota','QuotaExceededError');return o.call(this,k,v)}})();"
def c7b(pg,sd,a,cx): return (IDK not in a and not prot_same(sd,a) and a[FRK]==sd[FRK]),'identity non scrivibile: identity assente=%s, originali intatti=%s'%(IDK not in a,a[FRK]==sd[FRK])
run('S7b quota piena sulla chiave identity',seed(base_store()),c7b,pre=pre7b)
# S8 idempotenza
def c8(pg,sd,a,cx):
    i1=a[IDK]; pg.reload(); pg.wait_for_timeout(1500); i2=pg.evaluate("localStorage.getItem(%s)"%json.dumps(IDK)); b2=pg.evaluate("localStorage.getItem(%s)"%json.dumps(BAK))
    return i1==i2 and b2==a[BAK],'identity identica dopo ricarica=%s, backup invariato=%s'%(i1==i2,b2==a[BAK])
run('S8 idempotenza (ricarica)',seed(base_store(me2)),c8)
# S9 rollback
def c9(pg,sd,a,cx):
    r=pg.evaluate("tvaIdentity.restoreOriginals()"); after=pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}")
    same_store=json.loads(after[FRK])['me']==json.loads(sd[FRK])['me']
    same=(after.get(P+'user-name')==sd[P+'user-name'] and after.get(P+'fav-char')==sd[P+'fav-char'] and after.get(P+'tessera-look')==sd[P+'tessera-look'])
    others=store_cnt(after[FRK])==store_cnt(sd[FRK])
    return r and same and same_store and others and IDK not in after and not prot_same(sd,after),'restoreOriginals=%s, valori ripristinati=%s, me Friends identico=%s, collezioni identiche=%s, identity rimossa=%s'%(r,same,same_store,others,IDK not in after)
run('S9 rollback restoreOriginals (con conflitti)',seed(base_store(me2)),c9)
# S10 stringhe ostili/lunghe
me10=base_store()['me']; me10['motto']='A'*500+'‮\x00x'; me10['name']='N '+'B'*80
def c10(pg,sd,a,cx):
    idn=json.loads(a.get(IDK,'null')); ok=idn and len(idn['motto'])<=60 and '‮' not in idn['motto'] and '\x00' not in idn['motto']
    return ok,'motto troncato a %s caratteri, controlli/bidi rimossi=%s'%(len(idn['motto']) if idn else None,ok)
run('S10 stringhe ostili',seed(base_store(me10)),c10)
# S11 backup Friends: esporta e reimporta
def c11(pg,sd,a,cx):
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    pg.evaluate("tvaFriends.open()"); pg.wait_for_timeout(800)
    btn=pg.evaluate("(()=>{const b=[...document.querySelectorAll('#tfRoot button')].find(x=>/Esporta backup Friends/.test(x.textContent));return !!b})()")
    if not btn:
        pg.evaluate("[...document.querySelectorAll('#tfRoot .tf-tab')].find(x=>/Archivio/i.test(x.textContent))?.click()"); pg.wait_for_timeout(500)
    with pg.expect_download(timeout=8000) as dl:
        pg.evaluate("[...document.querySelectorAll('#tfRoot button')].find(x=>/Esporta backup Friends/.test(x.textContent)).click()")
    path=dl.value.path(); txt=open(path,encoding='utf-8').read(); ex=json.loads(txt)
    same=store_cnt(txt)==store_cnt(sd[FRK]); print('   S11 cnt export',store_cnt(txt),'fixture',store_cnt(sd[FRK]))
    open(OUT+'/backup_friends_esportato.json','w').write(txt)
    return same and ex['v']==1,'backup JSON esportato (%d byte) con collezioni identiche alle fixture=%s'%(len(txt),same)
run('S11 export backup Friends (JSON)',seed(base_store()),c11)
# S12 export profilo -> import profilo (round trip) e profilo "vecchio" senza identity/tesseraStyle
def c12(pg,sd,a,cx):
    with pg.expect_download(timeout=8000) as dl: pg.evaluate("document.getElementById('exportBtn').click()")
    prof=json.loads(open(dl.value.path(),encoding='utf-8').read())
    has=('identity' in prof, 'tesseraStyle' in prof, 'tesseraLook' in prof)
    # profilo vecchio: senza identity/tesseraStyle
    old=dict(prof); old.pop('identity',None); old.pop('tesseraStyle',None)
    fp=OUT+'/_profilo_vecchio.json'; open(fp,'w').write(json.dumps(old))
    pg.on('dialog',lambda d:d.accept())
    pg.set_input_files('#importFile',fp); pg.wait_for_timeout(1500)
    after=pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}")
    fr_same=after.get(FRK)==sd[FRK]
    return fr_same, 'profilo esportato contiene identity/tesseraStyle/tesseraLook=%s; dopo import profilo VECCHIO: store Friends invariato=%s, identity-v1 presente=%s, premigration presente=%s, user-name=%s'%(has,fr_same,IDK in after,BAK in after,after.get(P+'user-name'))
run('S12 profilo: export e import di profilo vecchio',seed(base_store()),c12)
# S13 profilo NUOVO (con identity) importato su dispositivo senza dati
def c13(pg,sd,a,cx):
    with pg.expect_download(timeout=8000) as dl: pg.evaluate("document.getElementById('exportBtn').click()")
    prof=json.loads(open(dl.value.path(),encoding='utf-8').read()); fp=OUT+'/_profilo_nuovo.json'; open(fp,'w').write(json.dumps(prof))
    open(OUT+'/_profilo_nuovo_len','w').write(str(len(json.dumps(prof))))
    return prof.get('identity') is not None,'profilo esportato include identity=%s (campi: %s)'%(prof.get('identity') is not None,[k for k in prof if k in('identity','tesseraStyle','tesseraLook','userName','favChar')])
run('S13 profilo nuovo esportato',seed(base_store(me2)),c13)

# ---------- backup JSON verificato + rollback (integrata) ----------
import tempfile
def bk(pg): return pg.evaluate("tvaIdentity.backupText()")
def c14(pg,sd,a,cx):
    t=bk(pg); o=json.loads(t); info=pg.evaluate("tvaIdentity.backupInfo()")
    ok=o['kind']=='tva-friends-identity-backup' and o['friendsRaw']==sd[FRK] and o['tid']==sd[P+'tessera-id'] and o['userName']==sd[P+'user-name'] and o['look']==sd[P+'tessera-look'] and info['valid'] and info['hasFriends'] and bool(o['sum'])
    return ok,'backup JSON: tipo=%s, dati Friends completi e identici all originale=%s, tessera-id/nome/look inclusi=%s, checksum valido=%s, %d byte'%(o['kind'],o['friendsRaw']==sd[FRK],o['tid']==sd[P+'tessera-id'],info['valid'],info['bytes'])
run('S14 backup JSON completo e verificato prima della migrazione',seed(base_store(me2)),c14)
def c15(pg,sd,a,cx):
    t=bk(pg); bad=t.replace('Giulia','Giuliz',1); assert bad!=t; o=json.loads(bad)
    r=pg.evaluate("(b)=>[tvaIdentity.backupParse(b),tvaIdentity.restoreFull(JSON.parse(b))]",bad)
    after=pg.evaluate("localStorage.getItem(%s)"%json.dumps(FRK))
    return r[0] is None and r[1]['ok'] is False and after==sd[FRK],'backup manomesso: rifiutato dal parser=%s, ripristino rifiutato=%s, store invariato=%s'%(r[0] is None,r[1]['ok'] is False,after==sd[FRK])
run('S15 backup manomesso rifiutato',seed(base_store()),c15)
def c16(pg,sd,a,cx):
    # simulo uso dopo la migrazione: aggiungo una squadra e cambio nome, poi ripristino COMPLETO
    pg.evaluate("""()=>{const k=%s;const o=JSON.parse(localStorage.getItem(k));o.teams['tm_zzzzzzzz99']={id:'tm_zzzzzzzz99',name:'Nuova',emblem:0,goal:50,owner:o.vid,created:Date.now(),members:{},log:[]};localStorage.setItem(k,JSON.stringify(o));localStorage.setItem('marvel-ultimate-timeline-user-name','Altro')}"""%json.dumps(FRK))
    r=pg.evaluate("tvaIdentity.restoreFull()"); after=pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}")
    ok=r['ok'] and after[FRK]==sd[FRK] and after[P+'user-name']==sd[P+'user-name'] and after[P+'fav-char']==sd[P+'fav-char'] and after[P+'tessera-look']==sd[P+'tessera-look'] and IDK not in after
    pg.reload(); pg.wait_for_timeout(1500)
    again=pg.evaluate("localStorage.getItem(%s)"%json.dumps(IDK)); cnt=store_cnt(pg.evaluate("localStorage.getItem(%s)"%json.dumps(FRK)))
    return ok and again is not None and cnt==store_cnt(sd[FRK]),'ripristino completo: store Friends identico all originale=%s, nome/personaggio/look ripristinati, identita rimossa=%s; dopo ricarica la migrazione riparte=%s, collezioni identiche=%s'%(after[FRK]==sd[FRK],IDK not in after,again is not None,cnt==store_cnt(sd[FRK]))
run('S16 rollback COMPLETO dal backup (store Friends incluso) e nuova migrazione',seed(base_store(me2)),c16)
def openarch(pg):
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(400)
    pg.evaluate("tvaFriends.open('archivio')"); pg.wait_for_timeout(700)
def c17(pg,sd,a,cx):
    openarch(pg); fail=pg.evaluate("document.getElementById('tfBkFail')?document.getElementById('tfBkFail').textContent:null"); st=pg.evaluate("tvaIdentity.status()")
    cnt=store_cnt(pg.evaluate("localStorage.getItem(%s)"%json.dumps(FRK)))
    return bool(fail) and st['failed']=='backup' and IDK not in a and cnt==store_cnt(sd[FRK]),'backup non scrivibile: avviso visibile all utente=%s ("%s"), migrazione annullata, dati Friends intatti=%s'%(bool(fail),(fail or '')[:70],cnt==store_cnt(sd[FRK]))
run('S17 errore di backup: migrazione annullata e avviso in Friends',seed(base_store()),c17,pre=pre7)
def c18(pg,sd,a,cx):
    openarch(pg)
    with pg.expect_download(timeout=8000) as dl: pg.evaluate("document.getElementById('tfBkDl').click()")
    txt=open(dl.value.path(),encoding='utf-8').read()
    return txt==bk(pg) and dl.value.suggested_filename.startswith('tva-backup-friends-identita-') and json.loads(txt)['friendsRaw']==sd[FRK],'download dal pulsante: file %s identico al backup verificato=%s'%(dl.value.suggested_filename,txt==bk(pg))
run('S18 scarico del backup JSON dalla UI',seed(base_store()),c18)
def c19(pg,sd,a,cx):
    openarch(pg); t=bk(pg); fp=tempfile.mkdtemp()+'/b.json'; open(fp,'w').write(t)
    pg.evaluate("""()=>{const k=%s;const o=JSON.parse(localStorage.getItem(k));o.teams={};o.duels={};localStorage.setItem(k,JSON.stringify(o))}"""%json.dumps(FRK))
    pg.on('dialog',lambda d:d.accept()); pg.set_input_files('#tfBkFile',fp); pg.wait_for_timeout(900)
    ok=pg.evaluate("localStorage.getItem(%s)"%json.dumps(FRK))==sd[FRK]
    bad=tempfile.mkdtemp()+'/x.json'; open(bad,'w').write('{non valido'); before=pg.evaluate("localStorage.getItem(%s)"%json.dumps(FRK))
    pg.set_input_files('#tfBkFile',bad); pg.wait_for_timeout(600); after=pg.evaluate("localStorage.getItem(%s)"%json.dumps(FRK))
    return ok and before==after,'ripristino da file dalla UI: dati Friends tornati identici=%s; file non valido: nessuna modifica=%s'%(ok,before==after)
run('S19 ripristino da file dalla UI (valido e non valido)',seed(base_store()),c19)
def c20(pg,sd,a,cx):
    # senza avvio dalla UI, ricarica ripetuta non altera ne' backup ne' dati: 3 caricamenti
    t0=bk(pg)
    for _ in range(2): pg.reload(); pg.wait_for_timeout(1200)
    return bk(pg)==t0 and pg.evaluate("localStorage.getItem(%s)"%json.dumps(FRK))==sd[FRK],'3 caricamenti consecutivi: backup invariato e store Friends identico all originale'
run('S20 ricariche ripetute non alterano backup e dati',seed(base_store()),c20)
json.dump(R,open(OUT+'/risultati.json','w'),indent=1,ensure_ascii=False)
print('TOTALE',sum(1 for r in R if r['ok']),'/',len(R))
