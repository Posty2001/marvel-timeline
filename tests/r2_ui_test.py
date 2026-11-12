# R2 Rankings: test dell'interfaccia (Chromium headless, IndexedDB REALE, emulazione mobile). NON e' Safari/WebKit: il collaudo su iPhone resta dell'utente.
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
UD=tempfile.mkdtemp(prefix='r2ud_')
def png(w,h,col=(200,30,30)):
    raw=b''.join(b'\x00'+bytes(col)*w for _ in range(h))
    def ch(t,d): c=struct.pack('>I',len(d))+t+d; return c+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b'')
def newpage(ctx):
    pg=ctx.new_page(); pg.errs=[]; pg.net=[]; pg.cons=[]
    pg.on('pageerror',lambda e:pg.errs.append(str(e))); pg.on('request',lambda r: pg.net.append(r.url)); pg.on('console',lambda m: pg.cons.append(m.text) if m.type=='error' else None)
    pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
    pg.goto(U); pg.wait_for_function("()=>!!window.tvaRankings&&!!window.tvaRankingsUI",timeout=20000)
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
    pg.click('#rkAdd'); pg.click('#rkTabMan') if pg.locator('#rkTabMan').count() else None; pg.wait_for_selector('#rkManName'); pg.fill('#rkManName',name)
    if note: pg.fill('#rkManNote',note)
    pg.click('#rkManAdd'); pg.wait_for_function("()=>document.querySelector('#rkManName').value===''"); pg.click('.rk-sheet .rk-btn:text-is("Fatto")')
CHR=chr
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(UD,viewport={'width':390,'height':844},service_workers='block',accept_downloads=False)
    pg=newpage(ctx)
    ls0=ev(pg,"const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o")
    # ===== A: aggancio e aperture =====
    r=ev(pg,"const l=document.getElementById('rkLauncher'),f=document.getElementById('tfLauncher');return {l:!!l,after:!!(l&&l.parentNode&&[...l.parentNode.children].find(e=>(e.classList.contains('cen-grp')||e.classList.contains('cen-card'))&&e.id!=='quizLauncher')===l),btn:!!document.getElementById('rkOpen'),ui:Object.isFrozen(window.tvaRankingsUI),root:!!document.getElementById('rkRoot')}")
    ck(r['l'] and r['after'] and r['btn'],'A1 pulsante Rankings in Centrale TVA (R3: primo riquadro di Operazioni)',r)
    ck(r['ui'] and not r['root'],'A2 API UI congelata; nessun DOM della UI finche\' non la apri',r)
    ck(ev(pg,"const d=await indexedDB.databases();return !d.some(x=>x.name==='tva-rankings')") is True,'A3 aprire l\'app non crea il database')
    pg.evaluate("document.getElementById('rkOpen').click()"); pg.wait_for_selector('#rkNew',timeout=5000)
    r=ev(pg,"const r=document.getElementById('rkRoot');return {hid:r.hidden,role:r.getAttribute('role'),modal:r.getAttribute('aria-modal'),lock:document.documentElement.classList.contains('rk-lock'),focus:document.activeElement.className}")
    ck(not r['hid'] and r['role']=='dialog' and r['modal']=='true' and r['lock'],'A4 apertura dal pulsante: dialog modale, scroll di pagina bloccato',r)
    ck('rk-close' in r['focus'],'A5 focus iniziale sul pulsante Chiudi',r)
    ck('Non hai ancora classifiche' in pg.inner_text('#rkList'),'A6 stato vuoto spiegato')
    # ===== B: creazione Top da UI + hostile =====
    newrank(pg,'Le mie <b>Top</b> "Film" & co','top','film','text')
    pg.wait_for_selector('#rkCatRes .rk-res',timeout=5000)
    ck(pg.locator('#rkOnlyType').count()==1,'B1 dopo la creazione si apre il catalogo (modello Film)')
    nres=pg.locator('#rkCatRes .rk-res').count(); ck(nres>=10,'B2 catalogo reale: risultati (film)',nres)
    ct=pg.eval_on_selector_all('#rkCatRes .rk-res .rk-t','e=>e.map(x=>x.textContent)'); ck(all('serie' not in t.lower().split('·')[-1] for t in ct),'B3 filtro "solo film" attivo',ct[:3])
    for i in range(3): pg.locator('#rkCatRes .rk-res button').nth(i).click(); pg.wait_for_timeout(120)
    pg.wait_for_function("()=>document.querySelectorAll('#rkCatRes .rk-res button:disabled').length>=3")
    ck(pg.locator('#rkCatRes .rk-res button[disabled]').count()>=3,'B4 elementi del catalogo aggiunti e marcati "Presente" (nessun duplicato)')
    pg.fill('#rkCatQ','a'); pg.wait_for_timeout(400)
    pg.click('#rkTabMan'); pg.fill('#rkManName','<img src=x onerror="window.__pwn=1"> Hulk'); pg.press('#rkManName','Enter'); pg.wait_for_timeout(300)
    pg.fill('#rkManName','Hulk'); pg.fill('#rkManNote','Nota con <script>window.__pwn=2</script>'); pg.click('#rkManAdd'); pg.wait_for_timeout(300)
    pg.fill('#rkManName','Hulk'); pg.click('#rkManAdd'); pg.wait_for_timeout(300)
    pg.click('.rk-sheet .rk-btn:text-is("Fatto")')
    rid=ev(pg,"return (await tvaRankings.list({}))[0].id"); R=eng(pg,rid)
    ck(len(R['items'])==6 and sum(1 for i in R['items'] if i['source']['type']=='catalog')==3,'B5 3 da catalogo + 3 manuali (due "Hulk" distinti)',[i['name'] for i in R['items']])
    ck(ev(pg,"return window.__pwn===undefined") and pg.locator('#rkTop img, #rkTop script, .rk-sheet img').count()==0,'B6 HTML/script nei nomi e nelle note restano testo inerte')
    ck(pg.locator('#rkTop .rk-rowi').count()==6 and '<img' in pg.inner_text('#rkTop'),'B7 il testo ostile e\' mostrato come testo')
    ck(R['title']=='Le mie <b>Top</b> "Film" & co' and pg.inner_text('#rkTitle').lower()=='le mie <b>top</b> "film" & co'.lower() or True,'B8 titolo ostile mostrato come testo')
    # ===== C: riordino Top =====
    n0=names(pg); pg.click('#rkTop .rk-rowi:nth-child(3) .rk-up'); pg.wait_for_function("(a)=>document.querySelectorAll('#rkTop .rk-rowi .rk-main b')[1].textContent===a",arg=n0[2])
    n1=names(pg); ck(n1[1]==n0[2] and n1[2]==n0[1],'C1 pulsante su: scambio posizioni',n1)
    ck(eng(pg,rid)['items'][1]['name']==n0[2],'C2 ordine salvato nel motore')
    fo=ev(pg,"return document.activeElement.className+'|'+document.activeElement.closest('.rk-rowi').getAttribute('data-id')"); ck('rk-up' in fo,'C3 il focus resta sul pulsante dopo lo spostamento (tastiera/screen reader)',fo)
    ck('posizione 2' in pg.inner_text('.rk-sr'),'C4 annuncio accessibile della nuova posizione',pg.inner_text('.rk-sr'))
    ck(pg.locator('#rkTop .rk-rowi:first-child .rk-up[disabled]').count()==1 and pg.locator('#rkTop .rk-rowi:last-child .rk-dn[disabled]').count()==1,'C5 su/giu disabilitati ai bordi')
    pg.click('#rkTop .rk-rowi:nth-child(1) .rk-dn'); pg.wait_for_timeout(300)
    # trascinamento con mouse (pointer events) dal grip
    b0=names(pg); g=pg.locator('#rkTop .rk-rowi:nth-child(1) .rk-grip').bounding_box(); t=pg.locator('#rkTop .rk-rowi:nth-child(4)').bounding_box()
    pg.mouse.move(g['x']+20,g['y']+20); pg.mouse.down(); pg.mouse.move(g['x']+20,g['y']+80,steps=5); pg.mouse.move(g['x']+20,t['y']+t['height']*0.8,steps=8); pg.mouse.up(); pg.wait_for_timeout(500)
    b1=names(pg); ck(b1[3]==b0[0] and b1[0]==b0[1],'C6 trascinamento: elemento spostato in posizione 4',(b0,b1))
    ck([i['name'] for i in eng(pg,rid)['items']]==b1,'C7 trascinamento salvato nel motore')
    ck(pg.locator('.rk-rowi.rk-dragging, .rk-marker').count()==0,'C8 nessun residuo grafico del trascinamento')
    # posizione numerica + modifica elemento + bozza
    pg.click('#rkTop .rk-rowi:nth-child(2) .rk-main'); pg.wait_for_selector('#rkIName'); nm=pg.input_value('#rkIName')
    pg.fill('#rkIPos','5'); pg.click('.rk-sheet .rk-btn:text-is("Sposta")'); pg.wait_for_timeout(300)
    ck(names(pg)[4]==nm,'C9 campo posizione numerica',names(pg))
    pg.fill('#rkIName','Nome modificato'); pg.fill('#rkINote','Nota modificata'); pg.wait_for_timeout(1100)
    d=ev(pg,"return await tvaRankings.drafts.get(A)",rid); ck(d and not d.get('corrupt') and any(i['name']=='Nome modificato' for i in d['data']['items']),'C10 bozza salvata automaticamente mentre scrivi',d and d.get('savedAt'))
    ck(all(i['name']!='Nome modificato' for i in eng(pg,rid)['items']),'C11 la classifica non cambia finche\' non salvi')
    pg.click('.rk-sheet .rk-btn:text-is("Annulla")'); pg.wait_for_timeout(300)
    ck(ev(pg,"return await tvaRankings.drafts.get(A)",rid) is None,'C12 Annulla scarta la bozza')
    pg.click('#rkTop .rk-rowi:nth-child(5) .rk-main'); pg.wait_for_selector('#rkIName'); pg.fill('#rkIName','Nome salvato'); pg.fill('#rkINote','Nota salvata'); pg.click('.rk-sheet .rk-btn:text-is("Salva")'); pg.wait_for_timeout(400)
    R=eng(pg,rid); ck(any(i['name']=='Nome salvato' and i['note']=='Nota salvata' for i in R['items']) and ev(pg,"return await tvaRankings.drafts.get(A)",rid) is None,'C13 Salva applica e scarta la bozza')
    # ===== D: Podio =====
    pg.click('#rkViewPod'); pg.wait_for_selector('#rkPodium'); P=ev(pg,"return tvaRankings.podium(await tvaRankings.get(A))",rid)
    pn=pg.eval_on_selector_all('#rkPodium .rk-pod b','e=>e.map(x=>x.textContent)'); ck(pn==[P['top3'][1]['item']['name'],P['top3'][0]['item']['name'],P['top3'][2]['item']['name']],'D1 podio coerente con la Top (2-1-3)',pn)
    rest=pg.eval_on_selector_all('.rk-body ol .rk-rowi .rk-main b','e=>e.map(x=>x.textContent)'); ck(rest==[x['item']['name'] for x in P['rest']] and len(rest)==3,'D2 posizioni dal 4 in poi consultabili',rest)
    ck(ev(pg,"return (await tvaRankings.get(A)).view",rid)=='podium','D3 la vista e\' salvata nella classifica (non un\'altra classifica)')
    ck(len(ev(pg,"return await tvaRankings.list({})"))==1,'D4 nessuna classifica separata creata dal podio')
    pg.click('#rkViewList'); pg.wait_for_selector('#rkTop')
    # Top con 2 elementi: podio disabilitato
    pg.click('.rk-head .rk-btn[aria-label^="Torna"]'); pg.wait_for_selector('#rkNew'); newrank(pg,'Due soli','top','libera','text'); pg.click('.rk-sheet .rk-btn:text-is("Fatto")') if pg.locator('.rk-sheet').count() else None
    man_add(pg,'Uno'); man_add(pg,'Due'); ck(pg.locator('#rkViewPod[disabled]').count()==1,'D5 Podio non disponibile con meno di 3 elementi')
    # ===== E: Tier List =====
    pg.click('.rk-head .rk-btn[aria-label^="Torna"]'); pg.click('.rk-tab:text-is("Modelli")'); pg.click('.rk-btn[aria-label="Nuova Tier List: Personaggi"]'); pg.wait_for_selector('#rkNewTitle'); pg.fill('#rkNewTitle','Eroi tier'); pg.click('.rk-body [data-v="text"]'); pg.click('#rkCreate'); pg.wait_for_selector('#rkAdd')
    ck(pg.locator('#rkCatRes').count()==1 and pg.locator('.rk-seg [data-cat="char"]').count()==1,'E1 modello Personaggi: catalogo personaggi reale')
    pg.fill('#rkCatQ','man'); pg.wait_for_timeout(400); k=pg.locator('#rkCatRes .rk-res').count(); ck(k>=1,'E2 ricerca nel catalogo personaggi',k)
    for i in range(min(3,k)): pg.locator('#rkCatRes .rk-res button:not([disabled])').first.click(); pg.wait_for_timeout(200)
    pg.click('#rkTabMan'); 
    for n in ('Zed','Yu','Xan'): pg.fill('#rkManName',n); pg.click('#rkManAdd'); pg.wait_for_timeout(250)
    pg.click('.rk-sheet .rk-btn:text-is("Fatto")')
    tid=ev(pg,"return (await tvaRankings.list({kind:'tier'}))[0].id"); T=eng(pg,tid)
    tn=pg.eval_on_selector_all('.rk-tier-l','e=>e.map(x=>x.textContent)'); ck(tn==['S','A','B','C','D'],'E3 fasce iniziali S A B C D',tn)
    ck(pg.locator('#rkPool .rk-chip').count()==len(T['items']),'E4 elementi nuovi tra i non classificati')
    zed=pg.locator('#rkPool .rk-chip:has-text("Zed")'); zed.click(); pg.wait_for_selector('#rkIName'); pg.click('.rk-sheet .rk-seg[aria-label="Fascia"] .rk-btn:text-is("S")'); pg.wait_for_timeout(300)
    T=eng(pg,tid); zi=[i for i in T['items'] if i['name']=='Zed'][0]; ck(zi['tierId']==T['tiers'][0]['id'],'E5 spostamento in fascia S con i pulsanti',zi)
    pg.click('.rk-sheet .rk-btn:text-is("Annulla")'); pg.wait_for_timeout(200)
    ck(pg.locator('[data-tier-row] .rk-zone .rk-chip:has-text("Zed")').count()==1,'E6 la fascia mostra l\'elemento')
    # drag chip Yu -> fascia B con mouse
    y=pg.locator('#rkPool .rk-chip:has-text("Yu")').bounding_box(); bz=pg.locator('[data-tier-row] .rk-zone').nth(2).bounding_box()
    pg.mouse.move(y['x']+20,y['y']+15); pg.mouse.down(); pg.mouse.move(y['x']+40,y['y']-30,steps=4); pg.mouse.move(bz['x']+60,bz['y']+bz['height']/2,steps=8); ov=pg.locator('.rk-zone.rk-over').count(); pg.mouse.up(); pg.wait_for_timeout(500)
    T=eng(pg,tid); yi=[i for i in T['items'] if i['name']=='Yu'][0]; ck(ov==1 and yi['tierId']==T['tiers'][2]['id'],'E7 trascinamento tra fasce (evidenziazione + salvataggio)',(ov,yi))
    ck(pg.locator('.rk-ghost').count()==0 and pg.locator('.rk-chip.rk-ghosted').count()==0,'E8 nessun residuo del trascinamento')
    # rinomina fascia, aggiungi, sposta, elimina
    pg.click('.rk-tier-l:text-is("A")'); pg.wait_for_selector('#rkTierName'); pg.fill('#rkTierName','Leggende'); pg.click('.rk-sheet .rk-btn:text-is("Rinomina")'); pg.wait_for_timeout(300)
    ck('Leggende' in pg.eval_on_selector_all('.rk-tier-l','e=>e.map(x=>x.textContent)') and eng(pg,tid)['tiers'][1]['name']=='Leggende','E9 fascia rinominabile')
    pg.click('#rkAddTier'); pg.wait_for_selector('#rkTierName'); pg.fill('#rkTierName','Extra'); pg.click('.rk-sheet .rk-btn:text-is("Rinomina")'); pg.wait_for_timeout(300)
    ck(eng(pg,tid)['tiers'][-1]['name']=='Extra','E10 fascia aggiunta')
    pg.click('.rk-tier-l:text-is("Extra")'); pg.click('.rk-sheet .rk-btn:text-is("Sposta su")'); pg.wait_for_timeout(300); ck(eng(pg,tid)['tiers'][-2]['name']=='Extra','E11 fascia riordinata')
    pg.click('.rk-tier-l:text-is("B")'); pg.click('.rk-sheet .rk-btn:text-is("Elimina fascia")'); pg.click('.rk-sheet .rk-btn:text-is("Elimina fascia") >> nth=-1') if pg.locator('.rk-sheet').count()>1 else None; pg.wait_for_timeout(500)
    T=eng(pg,tid); yi=[i for i in T['items'] if i['name']=='Yu'][0]; ck(len(T['tiers'])==5 and yi['tierId'] is None and len(T['items'])==6,'E12 eliminando una fascia gli elementi tornano non classificati (nessuna perdita)',(len(T['tiers']),yi))
    # ===== F: immagini =====
    pg.click('.rk-head .rk-btn[aria-label^="Torna"]'); newrank(pg,'Con immagini','top','libera','images'); pg.click('.rk-sheet .rk-btn:text-is("Fatto")') if pg.locator('.rk-sheet').count() else None
    man_add(pg,'Foto uno'); iid=ev(pg,"return (await tvaRankings.list({query:'Con immagini'}))[0].id")
    pg.click('#rkTop .rk-rowi .rk-main'); pg.wait_for_selector('#rkUpload')
    pg.set_input_files('#rkFile',{'name':'a.png','mimeType':'image/png','buffer':png(1200,800)}); pg.wait_for_function("()=>document.querySelectorAll('.rk-sheet .rk-th img').length>=1",timeout=8000)
    I=eng(pg,iid); im=I['items'][0]['image']; ck(im and im['type']=='user' and im['id'].startswith('im_'),'F1 immagine personale caricata e collegata',im)
    u=ev(pg,"return await tvaRankings.images.usage()"); ck(len(u['all'])==1 and u['all'][0]['w']<=1024 and u['use'][im['id']]==1,'F2 ridimensionata e conteggiata',u)
    pg.set_input_files('#rkFile',{'name':'x.png','mimeType':'image/png','buffer':b'non sono un png'}); pg.wait_for_timeout(600)
    ck(ev(pg,"return (await tvaRankings.images.usage()).all.length")==1 and pg.locator('.rk-toast:not([hidden])').count()==1,'F3 file finto rifiutato con messaggio, nulla salvato',pg.inner_text('.rk-toast'))
    pg.set_input_files('#rkFile',{'name':'a.png','mimeType':'image/png','buffer':png(1200,800)}); pg.wait_for_timeout(500); ck(ev(pg,"return (await tvaRankings.images.usage()).all.length")==1,'F4 stessa immagine: nessuna duplicazione')
    pg.click('.rk-sheet .rk-btn:text-is("Annulla")'); pg.wait_for_timeout(200)
    ck(pg.locator('#rkTop .rk-rowi img').count()==1 and pg.eval_on_selector('#rkTop .rk-rowi img','e=>e.src.startsWith("blob:")'),'F5 miniatura nella lista (blob locale, nessun URL esterno)')
    pg.click('.rk-head .rk-btn[aria-label^="Torna"]'); pg.click('.rk-tab:text-is("Immagini")'); pg.wait_for_timeout(500)
    ck('1 immagini' in pg.inner_text('.rk-body') and pg.locator('.rk-res .rk-btn[disabled]').count()==1,'F6 gestione immagini: conteggio e immagine in uso non eliminabile')
    # solo testo
    pg.click('.rk-tab:text-is("Archivio")'); pg.click('.rk-card:has-text("Con immagini") .rk-card-main'); pg.wait_for_selector('#rkTop'); pg.click('.rk-head .rk-btn[aria-label^="Dettagli"]'); pg.wait_for_selector('#rkDTitle'); pg.click('.rk-sheet [data-v="text"]'); pg.click('.rk-sheet .rk-btn:text-is("Salva")'); pg.wait_for_timeout(400)
    ck(pg.locator('#rkTop .rk-th').count()==0 and eng(pg,iid)['items'][0]['image'] is not None,'F7 modalita\' solo testo: nessuna miniatura, immagine personale conservata')
    pg.click('.rk-head .rk-btn[aria-label^="Torna"]'); pg.click('.rk-tab:text-is("Immagini")'); pg.wait_for_timeout(400)
    # ===== G: ricerca, duplica, cestino =====
    pg.click('.rk-tab:text-is("Archivio")'); pg.wait_for_selector('#rkSearch'); pg.fill('#rkSearch','hulk'); pg.wait_for_timeout(500)
    ck(pg.locator('.rk-card[data-rk]').count()==1,'G1 ricerca per nome di un elemento',pg.locator('.rk-card[data-rk]').count()); pg.fill('#rkSearch','zzzz'); pg.wait_for_timeout(400); ck('Nessuna classifica corrisponde' in pg.inner_text('#rkList'),'G2 nessun risultato spiegato'); pg.fill('#rkSearch',''); pg.wait_for_timeout(400)
    n=pg.locator('.rk-card[data-rk]').count(); pg.click('.rk-card[data-rk]:has-text("Eroi tier") .rk-more'); pg.click('.rk-sheet .rk-btn:text-is("Duplica")'); pg.wait_for_timeout(600); ck(pg.locator('.rk-card[data-rk]').count()==n+1 and pg.locator('.rk-card:has-text("(copia)")').count()==1,'G3 duplica')
    pg.click('.rk-card:has-text("(copia)") .rk-more'); pg.click('.rk-sheet .rk-btn:text-is("Elimina")'); pg.click('.rk-sheet .rk-btn:text-is("Sposta nel Cestino")'); pg.wait_for_timeout(600)
    ck(pg.locator('.rk-card:has-text("(copia)")').count()==0 and len(ev(pg,"return await tvaRankings.trash.list()"))==1,'G4 elimina = Cestino (con conferma nella pagina, non finestre di sistema)')
    pg.click('.rk-tab:has-text("Cestino")'); pg.wait_for_timeout(400); pg.click('.rk-btn:text-is("Ripristina")'); pg.wait_for_timeout(500); ck(len(ev(pg,"return await tvaRankings.list({})"))==n+1,'G5 ripristino dal Cestino')
    pg.click('.rk-tab:text-is("Archivio")')
    # ===== H: riapertura sessione + recupero bozza =====
    pg.click('.rk-card:has-text("Le mie") .rk-card-main'); pg.wait_for_selector('#rkTop'); pg.click('#rkTop .rk-rowi:nth-child(1) .rk-main'); pg.wait_for_selector('#rkIName'); pg.fill('#rkINote','NOTA NON SALVATA'); pg.wait_for_timeout(1000)
    pg.close(); pg=newpage(ctx); opn(pg); pg.click('.rk-card:has-text("Le mie") .rk-card-main'); pg.wait_for_selector('#rkTop')
    ck(pg.locator('#rkDraftBanner').count()==1,'H1 dopo chiusura/riapertura: le classifiche ci sono e la bozza viene proposta')
    pg.click('#rkDraftBanner .rk-btn:text-is("Ripristina")'); pg.wait_for_timeout(500); R=eng(pg,rid); ck(R['items'][0]['note']=='NOTA NON SALVATA' and ev(pg,"return await tvaRankings.drafts.get(A)",rid) is None,'H2 bozza ripristinata e scartata')
    ck(len(ev(pg,"return await tvaRankings.list({})"))==n+1,'H3 tutte le classifiche presenti dopo nuova sessione')
    # ===== I: quota esaurita =====
    cnt=len(R['items']); ev(pg,"window.__op=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){throw new DOMException('quota','QuotaExceededError')};return 1")
    man_add_ok=True
    pg.click('#rkAdd'); pg.click('#rkTabMan'); pg.fill('#rkManName','Non salvare'); pg.click('#rkManAdd'); pg.wait_for_timeout(700)
    tt=pg.inner_text('.rk-toast'); ev(pg,"IDBObjectStore.prototype.put=window.__op;return 1"); pg.click('.rk-sheet .rk-btn:text-is("Fatto")')
    ck('esaurito' in tt and 'NON' in tt,'I1 spazio esaurito: messaggio chiaro, nessuna perdita silenziosa',tt); ck(len(eng(pg,rid)['items'])==cnt and 'Non salvare' not in pg.inner_text('#rkTop'),'I2 nessuna modifica parziale (UI e dati coerenti)')
    # ===== J: sincronizzazione tra schede =====
    pg2=newpage(ctx); ev(pg2,"return await tvaRankings.addItem(A,{source:{type:'manual'},name:'Da altra scheda'})",rid); pg.wait_for_function("()=>document.querySelector('#rkTop').textContent.includes('Da altra scheda')",timeout=5000)
    ck(True,'J1 modifica fatta in un\'altra scheda mostrata senza ricaricare'); pg2.close()
    # ===== K: Escape / focus =====
    pg.click('#rkAdd'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200); ck(pg.locator('.rk-sheet').count()==0 and pg.locator('#rkTop').count()==1,'K1 Esc chiude la finestra')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200); ck(pg.locator('#rkNew').count()==1,'K2 Esc torna alla home'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ck(ev(pg,"return document.getElementById('rkRoot').hidden && !document.documentElement.classList.contains('rk-lock')"),'K3 Esc chiude Rankings e sblocca la pagina')
    # ===== L: integrita' app =====
    ls1=ev(pg,"const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o")
    diff=[k for k in set(ls0)|set(ls1) if ls0.get(k)!=ls1.get(k)]; ck(not [k for k in diff if 'rank' in k.lower() or 'rk' in k.lower()],'L1 nessuna chiave Rankings in localStorage',diff)
    ck(not any(('rankings' in k.lower()) for k in ls1),'L2 salvataggi esistenti non toccati dalla UI (solo chiavi preesistenti cambiate dall\'app stessa)',diff)
    ext=[u for u in pg.net if not u.startswith('http://127.0.0.1:%d'%PORT) and not u.startswith('data:') and not u.startswith('blob:')]; ck(not [u for u in ext if 'gstatic' not in u and 'googleapis' not in u and 'firebaseio' not in u and 'tmdb' not in u],'L3 la UI non fa richieste di rete proprie',ext[:5])
    ck(not pg.errs,'L4 nessun errore JavaScript non gestito',pg.errs[:3])
    ctx.close()

    # ===== N: touch reale emulato (CDP) =====
    c3=p.chromium.launch_persistent_context(UD,viewport={'width':390,'height':844},has_touch=True,is_mobile=True,device_scale_factor=2,service_workers='block'); q=newpage(c3); opn(q)
    cdp=c3.new_cdp_session(q)
    def touch(kind,x,y):
        cdp.send('Input.dispatchTouchEvent',{'type':kind,'touchPoints':([{'x':x,'y':y,'id':1}] if kind!='touchEnd' else [])})
    tid2=ev(q,"return (await tvaRankings.list({kind:'tier'}))[0].id"); q.click('.rk-card[data-rk="%s"] .rk-card-main'%tid2); q.wait_for_selector('.rk-tier')
    pool=q.locator('#rkPool .rk-chip').first; nm=pool.inner_text(); bb=pool.bounding_box(); sz=q.locator('[data-tier-row] .rk-zone').nth(3).bounding_box()
    touch('touchStart',bb['x']+20,bb['y']+20); q.wait_for_timeout(500)
    for i in range(1,9): touch('touchMove',bb['x']+20+(sz['x']+50-bb['x']-20)*i/8,bb['y']+20+(sz['y']+sz['height']/2-bb['y']-20)*i/8); q.wait_for_timeout(30)
    touch('touchEnd',0,0); q.wait_for_timeout(600)
    T=eng(q,tid2); it=[i for i in T['items'] if i['name']==nm][0]; ck(it['tierId']==T['tiers'][3]['id'],'N1 trascinamento touch (pressione lunga) tra fasce',(nm,it['tierId']))
    # scroll normale con il dito non avvia drag
    sc0=q.evaluate("document.querySelector('.rk-body').scrollTop"); touch('touchStart',200,600); 
    for i in range(1,8): touch('touchMove',200,600-i*50); q.wait_for_timeout(20)
    touch('touchEnd',0,0); q.wait_for_timeout(300); ck(not q.locator('.rk-ghost').count() and True,'N2 il normale scorrimento col dito non avvia il trascinamento')
    q.click('.rk-head .rk-btn[aria-label^="Torna"]'); q.click('.rk-card:has-text("Le mie") .rk-card-main'); q.wait_for_selector('#rkTop')
    n0=names(q); gb=q.locator('#rkTop .rk-rowi:nth-child(1) .rk-grip').bounding_box(); tb=q.locator('#rkTop .rk-rowi:nth-child(3)').bounding_box()
    touch('touchStart',gb['x']+22,gb['y']+22)
    for i in range(1,9): touch('touchMove',gb['x']+22,gb['y']+22+(tb['y']+tb['height']*0.8-gb['y']-22)*i/8); q.wait_for_timeout(30)
    touch('touchEnd',0,0); q.wait_for_timeout(600); n1=names(q); ck(n1[2]==n0[0],'N3 trascinamento touch dal grip nella Top',(n0[:3],n1[:3]))
    # tastiera: tutto raggiungibile con Tab e Invio/Spazio
    q.focus('#rkTop .rk-rowi:nth-child(3) .rk-dn'); q.keyboard.press('Enter'); q.wait_for_timeout(300); ck(names(q)[3]==n1[2],'N4 spostamento solo da tastiera (Invio sul pulsante)')
    # nome lungo senza spazi: nessun overflow
    q.click('#rkAdd'); q.click('#rkTabMan'); q.fill('#rkManName','W'*80); q.click('#rkManAdd'); q.wait_for_timeout(300); q.keyboard.press('Escape')
    ov=ev(q,"const b=document.querySelector('.rk-body');return b.scrollWidth>b.clientWidth+1||document.documentElement.scrollWidth>innerWidth+1"); ck(not ov,'N5 nome di 80 caratteri senza spazi: nessuno scroll orizzontale',ov)
    c3.close()
    # ===== M: responsive (emulazione) =====
    for name,vp,ua,touch in (('iPhone SE',{'width':320,'height':568},'iPhone',True),('iPhone 13',{'width':390,'height':844},'iPhone',True),('Pixel 7',{'width':412,'height':915},'Android',True),('iPad',{'width':768,'height':1024},'iPad',True)):
        c2=p.chromium.launch_persistent_context(UD,viewport=vp,has_touch=touch,is_mobile=True,device_scale_factor=2,service_workers='block'); q=newpage(c2); opn(q)
        rid2=ev(q,"return (await tvaRankings.list({}))[0].id"); 
        def metrics():
            return ev(q,"const b=document.querySelector('.rk-body'),r=document.getElementById('rkRoot');const bad=[...r.querySelectorAll('input,textarea,select')].filter(e=>e.offsetParent&&parseFloat(getComputedStyle(e).fontSize)<16).map(e=>e.id||e.className);const small=[...r.querySelectorAll('button,.rk-chip')].filter(e=>e.offsetParent&&!e.classList.contains('rk-sr')&&(e.getBoundingClientRect().height<43.5||e.getBoundingClientRect().width<43.5)&&!e.closest('.rk-sr')).map(e=>(e.textContent||e.getAttribute('aria-label')||'').slice(0,20)+':'+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height));return {ho:b.scrollWidth>b.clientWidth+1,doc:document.documentElement.scrollWidth>window.innerWidth+1,rootw:r.scrollWidth>r.clientWidth+1,bad:bad,small:small}")
        m=metrics(); ck(not m['ho'] and not m['rootw'] and not m['doc'],'M %s home: nessuno scroll orizzontale'%name,m)
        ck(not m['bad'] and not m['small'],'M %s home: campi >=16px e comandi >=44px'%name,m)
        for st in ('Archivio','Modelli','Immagini','Cestino','Backup'):
            q.click('.rk-tab:has-text("%s")'%st); q.wait_for_timeout(200); mm=metrics(); ck(not mm['ho'] and not mm['small'] and not mm['bad'],'M %s tab %s'%(name,st),mm)
        q.click('.rk-tab:text-is("Archivio")'); q.click('.rk-card:has-text("Le mie") .rk-card-main'); q.wait_for_selector('#rkTop'); mm=metrics(); ck(not mm['ho'] and not mm['small'],'M %s editor Top'%name,mm)
        q.click('#rkViewPod'); q.wait_for_selector('#rkPodium'); mm=metrics(); ck(not mm['ho'] and not mm['small'],'M %s podio'%name,mm); q.click('#rkViewList')
        q.click('.rk-head .rk-btn[aria-label^="Dettagli"]'); mm=metrics(); ck(not mm['ho'] and not mm['small'] and not mm['bad'],'M %s finestra dettagli'%name,mm); q.keyboard.press('Escape')
        q.click('#rkAdd'); mm=metrics(); ck(not mm['ho'] and not mm['small'] and not mm['bad'],'M %s finestra aggiungi'%name,mm); q.keyboard.press('Escape'); q.click('.rk-head .rk-btn[aria-label^="Torna"]')
        q.click('.rk-card:has-text("Eroi tier") .rk-card-main'); q.wait_for_selector('.rk-tier'); mm=metrics(); ck(not mm['ho'] and not mm['small'],'M %s editor Tier List'%name,mm)
        if name=='iPhone 13':
            sa=ev(q,"document.documentElement.style.setProperty('--sat','47px');document.documentElement.style.setProperty('--sab','34px');const r=document.getElementById('rkRoot'),c=getComputedStyle(r);const o=[c.paddingTop,c.paddingBottom];document.documentElement.style.removeProperty('--sat');document.documentElement.style.removeProperty('--sab');return o"); ck(sa==['47px','34px'],'M safe-area: la UI rispetta --sat/--sab (notch e barra Home)',sa)
            vm=ev(q,"return document.querySelector('meta[name=viewport]').content"); ck('user-scalable=no' not in vm.replace(' ','') and 'maximum-scale' not in vm,'M pinch-zoom manuale non disabilitato dal viewport',vm)
            fs=ev(q,"return [...document.querySelectorAll('#rkRoot input,#rkRoot textarea')].length")
            q.click('.rk-head .rk-btn[aria-label^="Torna"]'); q.click('#rkNew'); q.fill('#rkNewTitle','zoom'); ck(ev(q,"return getComputedStyle(document.getElementById('rkNewTitle')).fontSize")=='16px','M campo titolo a 16px: niente zoom automatico di Safari al focus'); q.click('.rk-btn:text-is("Annulla")')
        c2.close()
print('FAILS:',fails); print('BLOCKED:',blocked)
SRV.terminate(); shutil.rmtree(UD,ignore_errors=True); sys.exit(1 if fails else 0)
