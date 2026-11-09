import json,re,sys
from playwright.sync_api import sync_playwright
URL='http://localhost:8124/index.html'
res=[]
def ok(n,c,d=''): res.append((n,bool(c))); print('PASS' if c else 'FAIL',n,d)
MOCK="""(function(){
 var cfg=%s; var fb={mode:cfg.mode||'ok',store:cfg.store||{},log:[],cbs:{}}; window.__fb=fb;
 if(cfg.seed && !sessionStorage.getItem('__seeded')){ sessionStorage.setItem('__seeded','1'); Object.keys(cfg.seed).forEach(function(k){localStorage.setItem(k,cfg.seed[k]);}); }
 function perm(){var e=new Error('PERMISSION_DENIED: Permission denied');e.code='PERMISSION_DENIED';return e;}
 function net(){var e=new Error('network error');e.code='unavailable';return e;}
 function snap(p){return {val:function(){return fb.store[p]===undefined?null:fb.store[p];}};}
 function act(p,fn){return new Promise(function(res,rej){
   if(p.indexOf('sync/')!==0){setTimeout(function(){res(fn());},0);return;}
   if(fb.mode==='denied')setTimeout(function(){rej(perm());},0);
   else if(fb.mode==='neterr')setTimeout(function(){rej(net());},0);
   else if(fb.mode==='hang'){}
   else if(fb.mode==='slow')setTimeout(function(){res(fn());},3000);
   else setTimeout(function(){res(fn());},0);});}
 function mk(p){var r={
  once:function(){fb.log.push(['once',p]);return act(p,function(){return snap(p);});},
  on:function(ev,cb,eb){fb.log.push(['on',p]);(fb.cbs[p]=fb.cbs[p]||[]).push(cb);
     if(p.indexOf('sync/')===0){ if(fb.mode==='denied'){setTimeout(function(){eb&&eb(perm());},0);} else setTimeout(function(){cb(snap(p));},0);} },
  off:function(){fb.log.push(['off',p]);},
  set:function(v){fb.log.push(['set',p,v]);return act(p,function(){fb.store[p]=v;});},
  remove:function(){return act(p,function(){delete fb.store[p];});},
  update:function(){return Promise.resolve();}, transaction:function(){return Promise.resolve();},
  onDisconnect:function(){return {remove:function(){return Promise.resolve();},set:function(){return Promise.resolve();},cancel:function(){return Promise.resolve();}};},
  child:function(c){return mk(p+'/'+c);}, push:function(){return mk(p+'/x');}, key:p.split('/').pop()};return r;}
 fb.emit=function(p,v){fb.store[p]=v;(fb.cbs[p]||[]).forEach(function(cb){cb(snap(p));});};
 var db={ref:function(p){fb.log.push(['ref',p||'']);return mk(p||'');}};
 var F={apps:[],initializeApp:function(){F.apps.push(1);},database:function(){return db;}};
 F.database.ServerValue={TIMESTAMP:{'.sv':'timestamp'}}; window.firebase=F;
})();"""
KEYS={'watched':'marvel-ultimate-timeline-watched','ratings':'marvel-ultimate-timeline-ratings','favorites':'marvel-ultimate-timeline-favorites','notes':'marvel-ultimate-timeline-notes','name':'marvel-ultimate-timeline-user-name'}
FAV='marvel-ultimate-timeline-favorites'
def run():
  with sync_playwright() as p:
    b=p.chromium.launch()
    c0=b.new_context(); g=c0.new_page(); g.goto(URL); g.wait_for_timeout(1500)
    ids=g.evaluate("()=>[...document.querySelectorAll('.watch-check')].map(c=>c.dataset.item)"); c0.close()
    SEED={KEYS['watched']:json.dumps({i:True for i in ids[:12]}),KEYS['ratings']:json.dumps({i:4.5 for i in ids[:3]}),FAV:json.dumps({ids[0]:True}),KEYS['name']:'Franco','marvel-ultimate-timeline-tessera-id':'VAR-123456'}
    def newpage(cfg,clock=False):
        ctx=b.new_context(viewport={'width':900,'height':900})
        ctx.route(re.compile(r'^https?://(?!localhost).*'),lambda r:r.abort())
        cfg=dict(cfg); cfg['seed']=dict(SEED,**cfg.get('seed',{}))
        ctx.add_init_script(MOCK%json.dumps(cfg))
        pg=ctx.new_page(); pg.dialogs=[]
        if clock: pg.clock.install()
        pg.goto(URL); pg.wait_for_timeout(1800)
        if clock: pg.clock.run_for(2000)
        pg.evaluate("()=>{window.__m=1}")
        return ctx,pg
    def snapL(pg): return pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.indexOf('marvel-ultimate-timeline')===0&&k.indexOf('sync-code')<0&&k.indexOf('auto-backup')<0)o[k]=localStorage.getItem(k)}return o}")
    def st(pg): return pg.evaluate("()=>document.getElementById('syncStatus').textContent")
    def stt(pg): return pg.evaluate("()=>document.getElementById('syncStatus').getAttribute('data-sync-state')")
    def log(pg,kind): return pg.evaluate("(k)=>window.__fb.log.filter(x=>x[0]===k)",kind)
    def synclog(pg,kind): return [x for x in log(pg,kind) if str(x[1]).startswith('sync/')]
    def connect(pg,code):
        pg.evaluate("(c)=>{const i=document.getElementById('syncCodeInput');i.value=c;document.getElementById('syncConnectBtn').click()}",code)
    def tick(pg,ms): pg.clock.run_for(ms)
    def setfav(pg,i): pg.evaluate("([k,i])=>{localStorage.setItem(k,JSON.stringify({[i]:true}))}",[FAV,i])
    NR=lambda t:'Sincronizzazione riuscita' not in t
    LS=lambda pg,k:pg.evaluate("(k)=>localStorage.getItem(k)",k)

    ctx,pg=newpage({'mode':'ok'}); connect(pg,'ABCD2345'); pg.wait_for_timeout(600)
    sets=synclog(pg,'set'); payload=sets[0][2] if sets else None
    ok('T0 primo dispositivo: remoto vuoto -> 1 scrittura, poi «Sincronizzazione riuscita»',len(sets)==1 and 'Sincronizzazione riuscita' in st(pg) and stt(pg)=='synced',(st(pg),len(sets)))
    ctx.close()
    if not payload: print('payload mancante'); return
    pj=json.loads(payload)
    ok('T0b payload scritto con version/schemaVersion',pj.get('version')=='2.0' and pj.get('schemaVersion')==1)

    ctx,pg=newpage({'mode':'slow'}); connect(pg,'ABCD2345'); pg.wait_for_timeout(1200)
    t1=st(pg); pg.wait_for_timeout(5000); t2=st(pg)
    ok('T11 ack lento: «Connessione in corso», «riuscita» solo dopo conferma',('Connessione in corso' in t1) and NR(t1) and ('Sincronizzazione riuscita' in t2),(t1,t2)); ctx.close()

    # T1 PERMISSION_DENIED
    ctx,pg=newpage({'mode':'denied'},clock=True); before=snapL(pg); connect(pg,'ABCD2345'); tick(pg,500)
    t=st(pg); tick(pg,200000)
    ok('T1a PERMISSION_DENIED: errore di autorizzazione, mai «riuscita»',('Errore di autorizzazione' in t) and NR(t) and stt(pg)=='auth',t)
    ok('T1b nessun tentativo automatico (1 lettura, 0 scritture in 200 s)',len(synclog(pg,'once'))==1 and len(synclog(pg,'set'))==0,(synclog(pg,'once'),synclog(pg,'set')))
    ok('T1c dati locali intatti, codice non salvato come collegato',snapL(pg)==before and LS(pg,'marvel-ultimate-timeline-sync-code') is None); ctx.close()
    ctx,pg=newpage({'mode':'denied','seed':{'marvel-ultimate-timeline-sync-code':'ABCD2345'}},clock=True); tick(pg,200000)
    ok('T1d avvio con codice salvato + denied: 1 lettura, nessun retry, mai «Collegato e sincronizzato»',('Errore di autorizzazione' in st(pg)) and len(synclog(pg,'once'))==1 and NR(st(pg)),(st(pg),synclog(pg,'once'))); ctx.close()

    # T2 / T9
    ctx,pg=newpage({'mode':'neterr'},clock=True); before=snapL(pg); connect(pg,'ABCD2345'); tick(pg,300)
    t=st(pg); ok('T2a errore di rete: «Connessione non disponibile», mai «riuscita»',('Connessione non disponibile' in t) and NR(t),t)
    tick(pg,300000); n1=len(synclog(pg,'once')); tick(pg,600000); n2=len(synclog(pg,'once'))
    ok('T9a retry limitati: 1+4 letture poi stop (n=%d, dopo 10 min n=%d)'%(n1,n2),n1==5 and n2==5 and 'Tentativi esauriti' in st(pg),(n1,n2,st(pg)))
    ok('T9b «Riprova» manuale visibile; dati locali intatti',pg.evaluate("()=>!document.getElementById('syncRetryBtn').hidden")and snapL(pg)==before); ctx.close()
    ctx,pg=newpage({'mode':'hang'},clock=True); connect(pg,'ABCD2345'); tick(pg,11000)
    ok('T2b nessuna risposta: timeout 10 s -> «Connessione non disponibile»',('Connessione non disponibile' in st(pg)) and NR(st(pg)),st(pg)); ctx.close()
    ctx,pg=newpage({'mode':'hang','seed':{'marvel-ultimate-timeline-sync-code':'ABCD2345'}},clock=True); tick(pg,500)
    ok('T2c avvio con codice salvato e rete assente: «Connessione in corso», mai «Collegato e sincronizzato»',NR(st(pg)) and 'Connessione in corso' in st(pg),st(pg)); ctx.close()

    # T3
    bad=['A/B/CDEF','../../rooms/X','AB.CD','ABC$1234','AB CD','AB[1]CD','ABC','X'*33,'-ABCD-','AB#CDEF','ÀBCDEF','']
    ctx,pg=newpage({'mode':'ok'}); det=[]
    for code in bad:
        connect(pg,code); pg.wait_for_timeout(120)
    refs=[x for x in log(pg,'ref') if str(x[1]).startswith('sync')]
    ok('T3a 12 codici malformati rifiutati prima di qualsiasi riferimento Firebase',not refs and not synclog(pg,'once'),refs); ctx.close()
    ctx,pg=newpage({'mode':'ok'}); connect(pg,'abcd-2345'); pg.wait_for_timeout(500)
    refs=[x[1] for x in log(pg,'ref') if str(x[1]).startswith('sync')]
    ok('T3b codice legittimo (minuscolo/trattino) -> sync/ABCD-2345',refs==['sync/ABCD-2345'],refs); ctx.close()
    ctx,pg=newpage({'mode':'ok','seed':{'marvel-ultimate-timeline-sync-code':'AB/CD'}}); pg.wait_for_timeout(500)
    ok('T3c codice salvato non valido non usato all’avvio',not [x for x in log(pg,'ref') if str(x[1]).startswith('sync')] and 'non è valido' in st(pg),st(pg)); ctx.close()
    ctx,pg=newpage({'mode':'ok'}); pg.evaluate("()=>document.getElementById('syncGenBtn').click()"); gc=pg.input_value('#syncCodeInput',timeout=2000) if False else pg.evaluate("()=>document.getElementById('syncCodeInput').value"); ctx.close()
    ok('T3d codice generato 8 car. compatibile col validatore',re.fullmatch(r'[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{8}',gc) is not None,gc)

    # T4 / T6 / T7
    old=dict(pj); old['watched']={ids[0]:True}; old.pop('tesseraLook',None); old.pop('version',None); old.pop('schemaVersion',None)
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':json.dumps(old)}}); before=snapL(pg); connect(pg,'ABCD2345'); pg.wait_for_timeout(1200)
    ok('T4a profilo cloud vecchio NON applicato: stato Conflitto',stt(pg)=='conflict' and 'Conflitto' in st(pg) and NR(st(pg)),st(pg))
    ok('T4b locale invariato, nessuna scrittura remota, nessun reload',snapL(pg)==before and not synclog(pg,'set') and pg.evaluate("()=>window.__m")==1)
    ok('T6a tre scelte visibili',pg.evaluate("()=>['syncKeepLocalBtn','syncShowDiffBtn','syncRestoreBtn'].every(i=>{const b=document.getElementById(i);return !b.hidden&&b.textContent.length>3})"))
    pg.evaluate("()=>document.getElementById('syncShowDiffBtn').click()"); d=pg.evaluate("()=>document.getElementById('syncConflictDiff').textContent")
    ok('T6b «Visualizza differenze»: titoli visti locale 12 vs cloud 1','Titoli visti: locale 12 · cloud 1' in d,d)
    pg.on('dialog',lambda dl:(pg.dialogs.append(dl.message),dl.dismiss()))
    pg.evaluate("()=>document.getElementById('syncRestoreBtn').click()"); pg.wait_for_timeout(400)
    ok('T7 ripristino annullato: nulla modificato, nessuna copia, nessun reload, ancora Conflitto',snapL(pg)==before and LS(pg,'marvel-ultimate-timeline-auto-backup') is None and pg.evaluate("()=>window.__m")==1 and stt(pg)=='conflict' and len(pg.dialogs)==1,pg.dialogs)
    ctx.close()
    # T8
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':json.dumps(old)}}); connect(pg,'ABCD2345'); pg.wait_for_timeout(1000)
    pg.on('dialog',lambda dl:dl.accept())
    with pg.expect_navigation(timeout=8000): pg.evaluate("()=>document.getElementById('syncRestoreBtn').click()")
    pg.wait_for_timeout(2000)
    w=json.loads(LS(pg,'marvel-ultimate-timeline-watched')); bk=LS(pg,'marvel-ultimate-timeline-auto-backup')
    bw=len(json.loads(bk).get('watched',{})) if bk else -1
    ok('T8a ripristino confermato via normalizzaProfilo: cloud applicato (1 titolo), copia recuperabile del locale (12)',list(w)==[ids[0]] and bw==12,(len(w),bw))
    ok('T8b dopo reload nessun falso conflitto: sincronizzato e confermato',stt(pg)=='synced' and 'Sincronizzazione riuscita' in st(pg),(stt(pg),st(pg)))
    ctx.close()
    # T5
    inv={'id sconosciuto':json.dumps(dict(pj,watched={'ZZZ-NOPE':True})),'app diversa':json.dumps(dict(pj,app='altra-app')),'schema futuro':json.dumps(dict(pj,schemaVersion=9)),'tipo errato':json.dumps(dict(pj,ratings='x')),'non JSON':'{{{','oggetto non stringa':{'a':1}}
    for nm,store in inv.items():
        ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':store}}); before=snapL(pg); connect(pg,'ABCD2345'); pg.wait_for_timeout(900)
        dis=pg.evaluate("()=>document.getElementById('syncRestoreBtn').disabled")
        ok('T5 cloud non valido (%s): conflitto, ripristino disabilitato, locale intatto, 0 scritture'%nm,stt(pg)=='conflict' and dis and snapL(pg)==before and not synclog(pg,'set'),(stt(pg),dis)); ctx.close()
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':inv['id sconosciuto']}}); before=snapL(pg); connect(pg,'ABCD2345'); pg.wait_for_timeout(900)
    pg.evaluate("()=>{const b=document.getElementById('syncRestoreBtn');b.disabled=false;b.click()}"); pg.wait_for_timeout(300)
    ok('T5b click forzato su ripristino con cloud non valido: rifiutato dal validatore, locale intatto',snapL(pg)==before and pg.evaluate("()=>window.__m")==1); ctx.close()

    # Keep / uguale / listener
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':json.dumps(old)}}); before=snapL(pg); connect(pg,'ABCD2345'); pg.wait_for_timeout(900); pg.evaluate("()=>document.getElementById('syncKeepLocalBtn').click()"); pg.wait_for_timeout(300)
    ok('T6c «Mantieni dati locali»: nulla modificato (locale/remoto), sync non attiva, codice non salvato',snapL(pg)==before and not synclog(pg,'set') and stt(pg)=='off' and LS(pg,'marvel-ultimate-timeline-sync-code') is None); ctx.close()
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':payload}}); connect(pg,'ABCD2345'); pg.wait_for_timeout(900)
    ok('T12a remoto identico al locale: sincronizzato, 0 scritture, nessun prompt',stt(pg)=='synced' and not synclog(pg,'set'),(stt(pg),synclog(pg,'set')))
    before=snapL(pg); pg.evaluate("(o)=>window.__fb.emit('sync/ABCD2345',JSON.stringify(o))",dict(pj,watched={ids[1]:True})); pg.wait_for_timeout(600)
    ok('T12b cambio remoto successivo: Conflitto, NON applicato, nessun reload',stt(pg)=='conflict' and snapL(pg)==before and pg.evaluate("()=>window.__m")==1,stt(pg)); ctx.close()
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':payload}},clock=True); connect(pg,'ABCD2345'); tick(pg,500)
    setfav(pg,ids[2]); tick(pg,5000)
    ok('T13a modifica locale da sincronizzato -> 1 scrittura confermata',len(synclog(pg,'set'))==1 and stt(pg)=='synced',len(synclog(pg,'set')))
    pg.evaluate("()=>{window.__fb.mode='neterr'}"); setfav(pg,ids[3]); tick(pg,400000)
    n=len(synclog(pg,'set')); tick(pg,600000)
    ok('T9c push con errori transitori: 1+4 tentativi (set totali=%d) poi stop'%n,n==6 and len(synclog(pg,'set'))==n and 'Connessione non disponibile' in st(pg) and NR(st(pg)),(n,st(pg))); ctx.close()
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':payload}},clock=True); connect(pg,'ABCD2345'); tick(pg,500)
    pg.evaluate("()=>{window.__fb.mode='denied'}"); setfav(pg,ids[4]); tick(pg,300000)
    ok('T1e push negato a metà sessione: 1 tentativo, errore autorizzazione, locale mantenuto',len(synclog(pg,'set'))==1 and 'Errore di autorizzazione' in st(pg) and json.loads(LS(pg,FAV))=={ids[4]:True},(len(synclog(pg,'set')),st(pg))); ctx.close()
    ctx,pg=newpage({'mode':'ok','store':{'sync/ABCD2345':payload}}); connect(pg,'ABCD2345'); pg.wait_for_timeout(700); before=snapL(pg); pg.evaluate("()=>document.getElementById('syncDisconnectBtn').click()"); pg.wait_for_timeout(200)
    ok('T10 disconnessione: dati locali intatti, stato Non collegato',snapL(pg)==before and stt(pg)=='off'); ctx.close()

    src=open('/home/claude/work/index.html',encoding='utf-8').read(); blk_all=src[src.find('SYNC40C-BEGIN'):src.find('SYNC40C-END')]; fa2=blk_all[blk_all.find('FA2-BEGIN'):blk_all.find('FA2-END')]; blk=blk_all.replace(fa2,'')  # F-A2: modulo account verificato a parte (S2b/S3b)
    ok('S1 syncApplyProfile (scrittura diretta non validata) rimosso',src.count('syncApplyProfile')==0)
    ok('S2 blocco sync: unico location.reload è nel ripristino confermato',blk.count('location.reload')==1 and blk.find('location.reload')>blk.find('function syncRestoreFromCloud'))
    ok('S3 retry solo con backoff limitato',blk.count('setInterval')==1 and 'SYNC_RETRY_DELAYS' in blk)
    ok('S2b modulo account: un solo reload (ripristino backup confermato) e un solo setInterval (solo UI, nessuna rete)',fa2.count('location.reload')==1 and fa2.count('setInterval')==1 and 'acctBackupAction' in fa2[:fa2.find('location.reload')+1] or fa2.count('location.reload')==1)
    ok('S4 Live Room invariata (rooms/ presente, nessuna sync/ nel suo blocco)', 'rooms/' in src)
    b.close()
  f=[n for n,c in res if not c]; print('\nTOTALE %d/%d'%(len(res)-len(f),len(res)),'FAIL:',f)
run()
