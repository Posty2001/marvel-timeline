# FASE 2B / F0 — identita' condivisa, migrazione, backup/ripristino. Emulazione browser (non iPhone reale).
import sys,os,json
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
srv,base=start_server()
P='marvel-ultimate-timeline-'
def ls(pg,k): return pg.evaluate("k=>localStorage.getItem(k)",k)
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---- 1) dati preesistenti (profilo "vecchio") con conflitti ----
    c=newctx(b);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(base+'/index.html');pg.wait_for_timeout(1200)
    old_me={'name':'Carol','emblem':4,'color':2,'motto':'Sempre avanti','univ':'Terra-616','ch':'Thor','share':{'emblem':True,'motto':True,'univ':False,'ch':False,'tid':True}}
    store={'v':1,'vid':'vabcdefghij','me':old_me,'nexus':{},'pendingOut':{},'reqs':{},'teams':{},'evenings':{},'duels':{},'shared':{'out':{},'inn':{}},'inbox':[],'seen':{},'best':{'solo':0,'n':0}}
    pg.evaluate("([a,s])=>{localStorage.removeItem('marvel-ultimate-timeline-identity-v1');localStorage.removeItem('marvel-ultimate-timeline-identity-premigration-v1');localStorage.setItem(a,s);localStorage.setItem('marvel-ultimate-timeline-user-name','Wanda');localStorage.setItem('marvel-ultimate-timeline-fav-char','Iron Man')}",[P+'tvafriends-v1',json.dumps(store)])
    orig_friends=ls(pg,P+'tvafriends-v1')
    r=pg.evaluate("()=>tvaIdentity.migrate()")
    ck(r['ok'] and r['created'],'F0-1 migrazione eseguita',r)
    ck(set(r['conflicts'])=={'name','ch'},'F0-2 conflitti rilevati (nome, personaggio) senza sovrascrivere',r)
    idn=json.loads(ls(pg,P+'identity-v1'))
    ck(idn['emblem']==4 and idn['motto']=='Sempre avanti' and idn['univ']=='Terra-616' and idn['v']==1,'F0-3 identità creata dai dati Friends',idn)
    ck(ls(pg,P+'user-name')=='Wanda' and ls(pg,P+'fav-char')=='Iron Man','F0-4 dati Tessera originali intatti')
    ck(ls(pg,P+'tvafriends-v1')==orig_friends,'F0-5 archivio Friends originale intatto (nessuna sovrascrittura silenziosa)')
    ck(idn['cf']['name']=={'f':'Carol','t':'Wanda'} and idn['cf']['ch']=={'f':'Thor','t':'Iron Man'},'F0-6 valori in conflitto conservati entrambi',idn.get('cf'))
    bak=json.loads(ls(pg,P+'identity-premigration-v1'))
    ck(bak['me']==old_me and bak['userName']=='Wanda' and bak['favChar']=='Iron Man','F0-7 copia di sicurezza degli originali presente e identica')
    # idempotenza
    r2=pg.evaluate("()=>tvaIdentity.migrate()");ck(r2['ok'] and not r2['created'] and ls(pg,P+'identity-v1')==json.dumps(json.loads(ls(pg,P+'identity-v1')),separators=(',',':')),'F0-8 migrazione idempotente')
    # ---- 2) lettura unificata e scrittura a due vie ----
    g=pg.evaluate("()=>tvaIdentity.get()");ck(g['name']=='Wanda' and g['emblem']==4 and g['ch']=='Iron Man','F0-9 get(): nome e personaggio dalla Tessera, resto dall\'identità',g)
    pg.evaluate("()=>tvaIdentity.set({motto:'Nuovo motto',univ:'Terra-199999',emx:20})")
    g=pg.evaluate("()=>tvaIdentity.get()")
    ck(g['motto']=='Nuovo motto' and g['emx']==20 and g['emblem']==pg.evaluate("()=>tvaIdentity.legacyOf(20)"),'F0-10 set(): emblema nuovo con fallback legacy valido (0–11)',g)
    ck(0<=json.loads(ls(pg,P+'identity-v1'))['emblem']<=11,'F0-11 campo legacy sempre 0–11 (compatibilità vecchie versioni)')
    # risoluzione esplicita
    pg.evaluate("()=>tvaIdentity.resolve('name','friends')");ck(ls(pg,P+'user-name')=='Carol','F0-12 risoluzione conflitto nome su scelta esplicita')
    pg.evaluate("()=>tvaIdentity.resolve('ch','tessera')");ck(not json.loads(ls(pg,P+'identity-v1')).get('cf'),'F0-13 conflitti risolti, nessuno residuo')
    # ---- 3) ripristino originali ----
    ok=pg.evaluate("()=>tvaIdentity.restoreOriginals()")
    me2=json.loads(ls(pg,P+'tvafriends-v1'))['me']
    ck(ok and me2==old_me and ls(pg,P+'user-name')=='Wanda' and ls(pg,P+'fav-char')=='Iron Man' and ls(pg,P+'identity-v1') is None,'F0-14 gli originali sono recuperabili dalla copia')
    # ---- 4) backup / ripristino profilo ----
    pg.evaluate("()=>localStorage.removeItem('marvel-ultimate-timeline-fav-char')")  # 'Iron Man' di prova non e' nell'indice reale: il profilo lo rifiuterebbe giustamente
    pg.evaluate("()=>{tvaIdentity.migrate();tvaIdentity.set({motto:'Round trip',emx:33});tvaIdentity.styleSave({m:'a1',pc:'#112233',dc:['x','y'],fxi:55,rot:true})}")
    snap_id=ls(pg,P+'identity-v1');snap_st=ls(pg,P+'tessera-style-v1')
    # esporta via bottone reale
    pg.evaluate("()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}")
    with pg.expect_download() as d: pg.evaluate("()=>document.getElementById('exportBtn')?.click()")
    prof=json.load(open(d.value.path())) if d.value else {}
    ck('identity' in prof and 'tesseraStyle' in prof,'F0-15 le nuove chiavi sono nell\'esportazione profilo',list(prof.keys())[-8:])
    ck(prof.get('identity',{}).get('motto')=='Round trip' and prof.get('tesseraStyle',{}).get('fxi')==55,'F0-16 contenuto esportato corretto')
    # importazione REALE (input file + conferma) in un profilo pulito
    def do_import(obj,tag):
        cx=newctx(b);q=cx.new_page();q.on('dialog',lambda d:(d.accept()));q.goto(base+'/index.html');q.wait_for_timeout(1200)
        pth='/tmp/imp_%s.json'%tag;open(pth,'w').write(json.dumps(obj))
        q.set_input_files('#importFile',pth);q.wait_for_timeout(600);q.wait_for_timeout(2000);q.wait_for_load_state();q.wait_for_timeout(800);return q
    q=do_import(prof,'ok')
    ck(json.loads(ls(q,P+'identity-v1') or '{}').get('motto')=='Round trip' and json.loads(ls(q,P+'tessera-style-v1') or '{}').get('fxi')==55,'F0-17 round-trip: identità e stile ripristinati dall\'import reale',(ls(q,P+'identity-v1'),))
    old=dict(prof);[old.pop(k) for k in('identity','tesseraStyle')]
    q=do_import(old,'old');ck(ls(q,P+'tessera-style-v1') is None,'F0-19 profilo VECCHIO senza nuove chiavi: importato, stile iniziale',ls(q,P+'tessera-style-v1'))
    g=q.evaluate("()=>tvaIdentity.get()");ck(g['emblem']>=0 and g['emx']==-1,'F0-19b dopo import vecchio l\'identità è valida (ripiego/migrazione)',g)
    bad=dict(prof);bad['identity']={'v':1,'emx':99};q=do_import(bad,'bad1');ck(ls(q,P+'identity-v1') is None or json.loads(ls(q,P+'identity-v1')).get('emx')!=99,'F0-20 identità non valida: NON applicata')
    bad=dict(prof);bad['tesseraStyle']={'v':1,'pc':'rosso'};q=do_import(bad,'bad2');ck(ls(q,P+'tessera-style-v1') is None,'F0-21 stile non valido: NON applicato')
    # ---- 5) robustezza ----
    pg.evaluate("()=>{localStorage.setItem('marvel-ultimate-timeline-identity-v1','{rotto')}")
    g=pg.evaluate("()=>tvaIdentity.get()");ck(isinstance(g,dict) and g['emblem']>=0,'F0-22 chiave identità corrotta: nessun crash, lettura di ripiego')
    ck(not errs,'F0-23 nessun errore JavaScript',errs[:3])
    # profilo pulito: nessun dato Friends
    c2=newctx(b);pg2=c2.new_page();pg2.goto(base+'/index.html');pg2.wait_for_timeout(1200)
    g=pg2.evaluate("()=>tvaIdentity.get()");ck(g['emblem']==0 and g['emx']==-1 and g['motto']=='' ,'F0-24 nuovo utente: identità vuota di default')
    b.close()
srv.terminate();summary()
