# R3 Rankings: test UI (backup/import, bozza, Indietro, raggiungibilita') (Chromium headless, IndexedDB REALE, emulazione mobile). NON e' Safari/WebKit: il collaudo su iPhone resta dell'utente.
import json,re,os,sys,socket,subprocess,time,tempfile,shutil,struct,zlib
ROOT=os.environ.get('TVA_ROOT') or os.environ.get('Q_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def freeport():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
PORT=freeport()
SRV=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',ROOT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1.2)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%PORT
fails=[]; blocked=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i); sys.stdout.flush()
    if not c: fails.append(m)
def bl(m,why): print('BLOCKED '+m+' :: '+why); blocked.append(m)
UD=tempfile.mkdtemp(prefix='r3ud_')
def png(w,h,col=(200,30,30)):
    raw=b''.join(b'\x00'+bytes(col)*w for _ in range(h))
    def ch(t,d): c=struct.pack('>I',len(d))+t+d; return c+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b'')
def newpage(ctx):
    pg=ctx.new_page(); pg.errs=[]; pg.net=[]; pg.cons=[]
    pg.on('pageerror',lambda e:pg.errs.append(str(e))); pg.on('request',lambda r: pg.net.append(r.url)); pg.on('console',lambda m: pg.cons.append(m.text) if m.type=='error' else None)
    pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
    pg.goto(U); pg.wait_for_function("()=>!!window.tvaRankings&&!!window.tvaRankingsUI&&!!window.tvaRankingsBackup",timeout=20000)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300); return pg
def ev(pg,js,arg=None): return pg.evaluate("async(A)=>{try{"+js+"}catch(e){return {__err:true,code:e&&e.code,msg:String(e&&e.message)}}}",arg)
def opn(pg): pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_selector('#rkNew',timeout=5000)
def names(pg): return pg.eval_on_selector_all('#rkTop .rk-rowi .rk-main b','e=>e.map(x=>x.textContent)')
def eng(pg,rid): return ev(pg,"return await tvaRankings.get(A)",rid)
def newrank(pg,title,kind='top',preset='libera',mode='text'):
    if not pg.locator('#rkNew').count(): pg.click('.rk-tab:text-is("Archivio")')
    pg.click('#rkNew'); pg.wait_for_selector('#rkNewTitle'); pg.fill('#rkNewTitle',title)
    pg.click('.rk-body [data-v="%s"]'%kind if kind=='tier' else '.rk-body [data-v="top"]')
    pg.click('.rk-body [data-v="%s"]'%preset); pg.click('.rk-body [data-v="%s"]'%mode); pg.click('#rkCreate'); pg.wait_for_selector('#rkAdd',timeout=5000)
def man_add(pg,name,note=''):
    (pg.click('#rkAdd') if not pg.locator('.rk-sheet').count() else None); pg.click('#rkTabMan') if pg.locator('#rkTabMan').count() else None; pg.wait_for_selector('#rkManName'); pg.fill('#rkManName',name)
    if note: pg.fill('#rkManNote',note)
    pg.click('#rkManAdd'); pg.wait_for_function("()=>document.querySelector('#rkManName').value===''"); pg.click('.rk-sheet .rk-btn:text-is("Fatto")')

import zipfile,io
DL=tempfile.mkdtemp(prefix='r3dl_')
def tab(pg,t): pg.click('.rk-tab:text-is("%s")'%t); pg.wait_for_timeout(250)
def wipe(pg): return ev(pg,"await new Promise(r=>{const q=indexedDB.deleteDatabase('tva-rankings');q.onsuccess=q.onerror=q.onblocked=()=>r()});return 1")
with sync_playwright() as p:
    # ---- N: raggiungibilita' in Centrale TVA ----
    br=p.chromium.launch()
    for name,vp in (('390x844',{'width':390,'height':844}),('320x568',{'width':320,'height':568})):
        c=br.new_context(viewport=vp,has_touch=True,is_mobile=True); pg=c.new_page(); pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
        pg.goto(U); pg.wait_for_function("()=>!!window.tvaRankingsUI"); pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
        r=pg.evaluate("()=>({card:!!document.getElementById('hhPlayRank'),launcherGone:!document.getElementById('rkLauncher')})")
        ck(r['card'] and r['launcherGone'],'N1 %s: [adattato rifinitura] Rankings si apre dalla card Home (il riquadro in Operazioni e\' stato rimosso)'%name,r)
        pg.evaluate('tvaRankingsUI.open()'); pg.wait_for_selector('#rkNew',timeout=5000); ck(True,'N2 %s: il pulsante apre Rankings'%name); c.close()
    br.close()
    ctx=p.chromium.launch_persistent_context(UD,viewport={'width':390,'height':844},has_touch=True,is_mobile=True,service_workers='block',accept_downloads=True,downloads_path=DL)
    pg=newpage(ctx); wipe(pg)
    # ---- H: tasto Indietro ----
    hs0=pg.evaluate("()=>({len:history.length,st:JSON.stringify(history.state),hash:location.hash,href:location.href})")
    opn(pg); hs1=pg.evaluate("()=>({len:history.length,st:JSON.stringify(history.state),hash:location.hash})")
    ck(hs1['len']==hs0['len']+1 and hs1['hash']==hs0['hash'],'H1 aprire Rankings aggiunge UNA sola voce di cronologia, hash invariato',(hs0,hs1))
    st=json.loads(hs1['st'] or '{}') or {}; st0=json.loads(hs0['st'] or '{}') or {}; ck(st.get('tvaRk')==1 and all(st.get(k)==v for k,v in st0.items()),'H2 lo stato della cronologia dell\'app e\' conservato (solo tvaRk aggiunto)',(st,st0))
    pg.go_back(); pg.wait_for_timeout(400); ck(not pg.locator('.rk-root').is_visible() if pg.locator('.rk-root').count() else True,'H3 Indietro dalla home di Rankings chiude Rankings')
    hs2=pg.evaluate("()=>({st:JSON.stringify(history.state),hash:location.hash,href:location.href})"); ck(hs2['href']==hs0['href'] and hs2['st']==hs0['st'],'H4 dopo Indietro: stesso indirizzo e stesso stato di cronologia dell\'app di prima',(hs0,hs2))
    ck(pg.evaluate("()=>journeyStarted.checked===true"),'H5 il viaggio/app non e\' stato riavviato dal tasto Indietro')
    opn(pg); newrank(pg,'Per Indietro','top','libera','text'); man_add(pg,'Uno')
    pg.go_back(); pg.wait_for_timeout(500); ck(pg.locator('#rkNew').count()>0 and pg.locator('.rk-root').is_visible(),'H6 Indietro dall\'editor torna alla lista (Rankings resta aperto)')
    pg.click('.rk-card[data-rk] .rk-card-main'); pg.wait_for_selector('#rkAdd'); pg.click('#rkAdd'); pg.wait_for_selector('.rk-sheet'); pg.go_back(); pg.wait_for_timeout(500)
    ck(pg.locator('.rk-sheet:visible').count()==0 and pg.locator('#rkAdd').count()>0,'H7 Indietro con un pannello aperto chiude solo il pannello (si resta nell\'editor)')
    pg.go_back(); pg.wait_for_timeout(500); pg.go_back(); pg.wait_for_timeout(500)
    ck(not (pg.locator('.rk-root').count() and pg.locator('.rk-root').is_visible()),'H8 altri Indietro: si esce da Rankings e non si resta intrappolati')
    ck(pg.evaluate("()=>location.href")==hs0['href'],'H9 si resta sulla stessa pagina dell\'app (nessuna uscita dal sito)')
    opn(pg); pg.click('.rk-head [aria-label*="hiudi"], .rk-head .rk-x, #rkClose') if pg.locator('.rk-head [aria-label*="hiudi"], .rk-head .rk-x, #rkClose').count() else pg.evaluate("tvaRankingsUI.close()"); pg.wait_for_timeout(500)
    hs3=pg.evaluate("()=>({len:history.length,st:JSON.stringify(history.state),href:location.href})"); ck(hs3['st']==hs0['st'] and hs3['href']==hs0['href'],'H10 chiusura con il pulsante: la voce di cronologia aggiunta viene rimossa, stato dell\'app identico',(hs0,hs3))
    for i in range(3): opn(pg); pg.evaluate("tvaRankingsUI.close()"); pg.wait_for_timeout(300)
    hs4=pg.evaluate("()=>({st:JSON.stringify(history.state),href:location.href})"); ck(hs4['st']==hs0['st'],'H11 aprire/chiudere piu\' volte non accumula voci ne\' altera lo stato',hs4)
    # ---- D: bozza "nuova classifica" ----
    wipe(pg); pg.reload(); pg.wait_for_function("()=>!!window.tvaRankings"); pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    opn(pg); pg.click('#rkNew'); pg.wait_for_selector('#rkNewTitle'); pg.fill('#rkNewTitle','Bozza <i>importante</i>'); pg.fill('#rkNewDesc','Descrizione in corso'); pg.click('.rk-body [data-v="tier"]'); pg.click('.rk-body [data-v="film"]'); pg.click('.rk-body [data-v="text"]'); pg.wait_for_timeout(900)
    d=ev(pg,"return await tvaRankings.newDraft.get()"); ck(d and d['data']['title']=='Bozza <i>importante</i>' and d['data']['kind']=='tier','D1 la bozza si salva da sola mentre scrivi (titolo, tipo, categoria)',d)
    pg.close(); pg=newpage(ctx); opn(pg)
    ck(pg.locator('#rkNdBanner').count()==1 and 'Bozza' in pg.inner_text('#rkNdBanner'),'D2 dopo ricarica/chiusura pagina: avviso "bozza non completata" nella lista')
    ck(pg.evaluate("()=>!document.querySelector('#rkNdBanner').innerHTML.includes('<i>')"),'D3 il testo della bozza e\' mostrato come testo (nessun HTML interpretato)')
    pg.click('#rkNdBanner .rk-pri'); pg.wait_for_selector('#rkNewTitle'); ck(pg.input_value('#rkNewTitle')=='Bozza <i>importante</i>' and pg.input_value('#rkNewDesc')=='Descrizione in corso','D4 "Continua" ripristina titolo e descrizione')
    ck(pg.locator('.rk-body [data-v="tier"][aria-pressed="true"]').count()==1 and pg.locator('.rk-body [data-v="film"][aria-pressed="true"]').count()==1 and pg.locator('.rk-body [data-v="text"][aria-pressed="true"]').count()==1,'D5 ripristinati anche tipo, categoria e modalita\' immagini')
    ck(pg.locator('#rkNewDraftBanner').count()==1,'D6 il form mostra che la bozza e\' stata ripristinata')
    pg.click('#rkCreate'); pg.wait_for_selector('#rkAdd',timeout=5000); ck(ev(pg,"return await tvaRankings.newDraft.get()") is None,'D7 creando la classifica la bozza viene eliminata')
    r=ev(pg,"const L=await tvaRankings.list({});return L.map(x=>[x.title,x.kind])"); ck(r==[['Bozza <i>importante</i>','tier']],'D8 classifica creata con i dati ripristinati',r)
    pg.evaluate("tvaRankingsUI.close()"); opn(pg); pg.click('#rkNew'); pg.wait_for_selector('#rkNewTitle'); pg.fill('#rkNewTitle','Da scartare'); pg.wait_for_timeout(800); pg.click('.rk-row-a .rk-btn:text-is("Annulla")'); pg.wait_for_timeout(400)
    ck(ev(pg,"return await tvaRankings.newDraft.get()") is None and pg.locator('#rkNdBanner').count()==0,'D9 "Annulla" scarta la bozza')
    pg.click('#rkNew'); pg.wait_for_selector('#rkNewTitle'); pg.fill('#rkNewTitle','   '); pg.wait_for_timeout(800); ck(ev(pg,"return await tvaRankings.newDraft.get()") is None,'D10 form vuoto/spazi: nessuna bozza inutile salvata')
    pg.click('.rk-row-a .rk-btn:text-is("Annulla")')
    # ---- B: backup UI ----
    wipe(pg); pg.reload(); pg.wait_for_function("()=>!!window.tvaRankings"); pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    SEED=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'r3_backup_test.py')).read().split('SEED="""')[1].split('"""')[0]
    S=ev(pg,SEED); opn(pg); tab(pg,'Backup')
    with pg.expect_download(timeout=15000) as dl: pg.click('#rkExport')
    f=dl.value; path=DL+'/'+f.suggested_filename; f.save_as(path); data=open(path,'rb').read()
    ck(f.suggested_filename.startswith('tva-rankings-backup-') and f.suggested_filename.endswith('.zip'),'B1 esportazione: scarica un .zip con nome datato',f.suggested_filename)
    zf=zipfile.ZipFile(io.BytesIO(data)); ck(zf.testzip() is None and all(i.compress_type==0 for i in zf.infolist()),'B2 il file scaricato e\' uno ZIP STORE valido (Python zipfile)')
    pg.wait_for_selector('#rkExpOut .rk-ok'); ck('3 classifiche' in pg.inner_text('#rkExpOut'),'B3 resoconto di esportazione con conteggi')
    # file corrotto -> rifiutato, nessun dato toccato
    bad=bytearray(data); bad[100]^=0xFF; open(DL+'/bad.zip','wb').write(bytes(bad)); pg.set_input_files('#rkImpFile',DL+'/bad.zip'); pg.wait_for_selector('#rkImpErr',timeout=8000)
    ck('RIFIUTATO' in pg.inner_text('#rkImpErr') and pg.locator('.rk-sheet:visible').count()==0,'B4 ZIP corrotto: rifiutato con messaggio, nessuna anteprima di importazione')
    open(DL+'/junk.zip','wb').write(b'questo non e uno zip'); pg.set_input_files('#rkImpFile',DL+'/junk.zip'); pg.wait_for_selector('#rkImpErr'); ck('RIFIUTATO' in pg.inner_text('#rkImpErr'),'B5 file non ZIP rifiutato')
    # UNISCI su dati identici
    pg.set_input_files('#rkImpFile',DL+'/'+f.suggested_filename); pg.wait_for_selector('#rkPrevList',timeout=8000)
    t=pg.inner_text('.rk-sheet'); ck('3 classifiche' in t and '0 nuove' in t and '3 già presenti' in t,'B6 anteprima prima di importare: conteggi e stato per classifica',t[:200])
    ck(pg.locator('#rkPrevList li').count()==3 and pg.locator('#rkDoMerge').count()==1 and pg.locator('#rkDoReplace').count()==0,'B7 modalita\' Unisci predefinita (nessun pulsante di sostituzione finche\' non scelto)')
    pg.click('#rkDoMerge'); pg.wait_for_selector('#rkImpResult .rk-ok, #rkImpResult p',timeout=8000); pg.wait_for_timeout(300)
    ck('Importate 0' in pg.inner_text('#rkImpResult') or 'identic' in pg.inner_text('#rkImpResult'),'B8 UNISCI su classifiche identiche: nulla importato, resoconto chiaro',pg.inner_text('#rkImpResult')[:200])
    n0=ev(pg,"return (await tvaRankings.list({})).length"); ck(n0==3,'B9 nessun duplicato creato')
    pg.evaluate("document.querySelector('.rk-sheet')&&[...document.querySelectorAll('.rk-sheet .rk-btn')].filter(b=>/Chiudi|Fatto|Annulla/.test(b.textContent)).slice(-1).forEach(b=>b.click())"); pg.wait_for_timeout(300)
    # SOSTITUISCI: accesso protetto + backup preventivo
    ev(pg,"await tvaRankings.updateMeta(A,{title:'Modificata locale'});return 1",S['a'])
    pg.set_input_files('#rkImpFile',DL+'/'+f.suggested_filename); pg.wait_for_selector('#rkPrevList'); pg.click('.rk-sheet [data-v="replace"]'); pg.wait_for_selector('#rkDoReplace')
    ck(pg.is_disabled('#rkDoReplace'),'B10 SOSTITUISCI: pulsante disattivato finche\' non confermi di aver capito')
    pg.check('#rkReplaceOk'); ck(not pg.is_disabled('#rkDoReplace'),'B11 spuntata la conferma, il pulsante si attiva')
    # blocco: backup preventivo che fallisce
    ev(pg,"window.__ga=IDBObjectStore.prototype.getAll;IDBObjectStore.prototype.getAll=function(){if(this.name==='images')throw new DOMException('disco pieno simulato','QuotaExceededError');return window.__ga.apply(this,arguments)};return 1")
    st0=ev(pg,"const L=await tvaRankings.list({});return L.map(x=>x.title).sort()"); sn0=ev(pg,"return (await tvaRankings.backup.snapshots.list()).length")
    pg.click('#rkDoReplace'); pg.wait_for_selector('#rkImpFail',timeout=8000); st1=ev(pg,"const L=await tvaRankings.list({});return L.map(x=>x.title).sort()")
    ck(st0==st1 and ev(pg,"return (await tvaRankings.backup.snapshots.list()).length")==sn0 and 'NON' in pg.inner_text('#rkImpFail').upper(),'B12 backup preventivo fallito: la sostituzione NON avviene, dati e copie invariati, messaggio chiaro',(st0,st1,pg.inner_text('#rkImpFail')[:160]))
    ck(not pg.is_disabled('.rk-sheet .rk-btn:text-is("Annulla")'),'B13 dopo il blocco si puo\' annullare o riprovare')
    if not hasattr(pg,'x'): pass
    ev(pg,"IDBObjectStore.prototype.getAll=window.__ga;return 1")
    pg.check('#rkReplaceOk') if not pg.is_checked('#rkReplaceOk') else None
    with pg.expect_download(timeout=15000) as dl2: pg.click('#rkDoReplace')
    ck(dl2.value.suggested_filename.startswith('prima-della-sostituzione'),'B14 SOSTITUISCI riuscita: prima scarica il backup preventivo ("prima-della-sostituzione-...")',dl2.value.suggested_filename)
    pg.wait_for_selector('#rkImpResult .rk-ok, #rkImpResult p',timeout=10000); pg.wait_for_timeout(500)
    st2=ev(pg,"const L=await tvaRankings.list({});return L.map(x=>x.title).sort()"); ck('Modificata locale' not in st2 and len(st2)==3,'B15 dopo SOSTITUISCI: stato del backup ripristinato (la modifica locale non c\'e\' piu\')',st2)
    ck(ev(pg,"return (await tvaRankings.backup.snapshots.list()).length")==1,'B16 creata una copia di sicurezza nell\'app')
    pg.evaluate("[...document.querySelectorAll('.rk-sheet .rk-btn')].filter(b=>/Chiudi|Fatto|Annulla/.test(b.textContent)).slice(-1).forEach(b=>b.click())"); pg.wait_for_timeout(300)
    tab(pg,'Archivio'); tab(pg,'Backup'); pg.wait_for_selector('#rkSnapBox .rk-card[data-snap]')
    ck(pg.locator('#rkSnapBox .rk-card[data-snap]').count()==1,'B17 la copia compare in "Copie di sicurezza"')
    pg.click('#rkSnapBox .rk-card[data-snap] .rk-pri'); pg.wait_for_selector('.rk-sheet .rk-btn.rk-pri:text-is("Ripristina")'); pg.click('.rk-sheet .rk-btn.rk-pri:text-is("Ripristina")'); pg.wait_for_timeout(1500)
    st3=ev(pg,"const L=await tvaRankings.list({});return L.map(x=>x.title).sort()"); ck('Modificata locale' in st3,'B18 "Ripristina" riporta lo stato precedente alla sostituzione (la modifica locale torna)',st3)
    ck(pg.evaluate("()=>!document.querySelector('.rk-root').scrollWidth>innerWidth+1 || document.querySelector('.rk-root').scrollWidth<=innerWidth+1"),'B19 nessuno scroll orizzontale nella scheda Backup')
    ck(not pg.errs,'B20 nessun errore JavaScript',pg.errs[:3])
    ext=[u for u in pg.net if not u.startswith('http://127.0.0.1:%d'%PORT) and not u.startswith(('data:','blob:')) and not any(h in u for h in ('gstatic','googleapis','firebaseio','tmdb'))]; ck(not ext,'B21 nessuna richiesta di rete verso servizi esterni',ext[:3])
    ctx.close()
print('FAILS:',fails); print('BLOCKED:',blocked)
SRV.terminate(); shutil.rmtree(UD,ignore_errors=True); shutil.rmtree(DL,ignore_errors=True); sys.exit(1 if fails else 0)
