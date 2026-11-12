# R1 Rankings: test del motore (Chromium headless, IndexedDB REALE). Nessuna rete. Nessun Safari/WebKit (non disponibile in sandbox).
import json,re,os,sys,socket,subprocess,time,tempfile,shutil,hashlib
ROOT=os.environ.get('TVA_ROOT') or os.environ.get('Q_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def freeport():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p
PORT=freeport()
SRV=subprocess.Popen([sys.executable,'-m','http.server',str(PORT),'--bind','127.0.0.1','--directory',ROOT],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1.2)
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:%d/index.html'%PORT
fails=[]; blocked=[]
def ck(c,m,i=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else i)
    if not c: fails.append(m)
UD=tempfile.mkdtemp(prefix='r1ud_')
def newpage(ctx,init=None):
    pg=ctx.new_page(); pg.errs=[]; pg.net=[]
    pg.on('pageerror',lambda e:pg.errs.append(str(e))); pg.on('request',lambda r: pg.net.append(r.url))
    if init: pg.add_init_script(init)
    pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
    pg.goto(U); pg.wait_for_function("()=>!!window.tvaRankings",timeout=20000); return pg
def ev(pg,js,arg=None):
    return pg.evaluate("async(A)=>{try{"+js+"}catch(e){return {__err:true,code:e&&e.code,msg:String(e&&e.message)}}}",arg)
def isErr(r,code=None): return isinstance(r,dict) and r.get('__err') and (code is None or r.get('code')==code)
CHR=chr
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(UD,viewport={'width':390,'height':844},service_workers='block')
    pg=newpage(ctx)
    # ===== E: isolamento / API =====
    r=ev(pg,"return {frozen:Object.isFrozen(window.tvaRankings),ver:tvaRankings.version,schema:tvaRankings.schema,dbs:(indexedDB.databases?(await indexedDB.databases()).map(d=>d.name):null),ls:Object.keys(localStorage).length}")
    ck(r['frozen'] and r['schema']==1,'E1 API congelata, schema 1',r)
    ck(r['dbs'] is not None and 'tva-rankings' not in r['dbs'],'E2 nessun database creato prima del primo uso (nessun effetto sull\'avvio)',r['dbs'])
    ls0=ev(pg,"const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o")
    # ===== C: CRUD =====
    st=ev(pg,"return await tvaRankings.status()"); ck(st.get('backend')=='indexeddb' and st.get('persistent') is True,'S1 persistenza su IndexedDB reale',st)
    a=ev(pg,"return await tvaRankings.create({kind:'top',title:'  I miei <b>Top</b> villain  ',description:'Riga 1\\r\\nRiga 2',preset:'villain',imageMode:'text'})")
    ck(not isErr(a) and a['rev']==1 and a['kind']=='top' and a['items']==[] and a['id'].startswith('rk_'),'C1 crea Top',a)
    ck(a['title']=='I miei <b>Top</b> villain' and a['description']=='Riga 1\nRiga 2','C1b titolo normalizzato (spazi) e testo conservato come TESTO (l\'escaping e\' compito della UI)',a['title'])
    ck(isErr(ev(pg,"return await tvaRankings.create({kind:'boh',title:'x'})"),'invalid'),'C2 kind non valido rifiutato')
    ck(isErr(ev(pg,"return await tvaRankings.create({kind:'top',title:'   '})"),'invalid'),'C3 titolo vuoto rifiutato')
    ck(isErr(ev(pg,"return await tvaRankings.create({kind:'top',title:{a:1}})"),'invalid'),'C4 titolo non stringa rifiutato')
    ck(not isErr(ev(pg,"return await tvaRankings.create({kind:'tier',title:'t',tiers:[]})")),'C5 Tier List senza fasce esplicite: usa S A B C D')
    m=ev(pg,"return await tvaRankings.updateMeta('%s',{title:'Rinominata',description:'d2',preset:'film',imageMode:'images'})"%a['id'])
    ck(not isErr(m) and m['title']=='Rinominata' and m['rev']==2 and m['preset']=='film' and m['imageMode']=='images','C6 modifica metadati: rev incrementata',m)
    g=ev(pg,"return await tvaRankings.get('%s')"%a['id']); ck(g['title']=='Rinominata' and g['rev']==2,'C7 rilettura da IndexedDB coerente')
    ck(isErr(ev(pg,"return await tvaRankings.get('rk_0000000000000000')"),'not-found'),'C8 id inesistente: not-found')
    ck(isErr(ev(pg,"return await tvaRankings.get('../../x')"),'invalid'),'C9 id malformato rifiutato')
    ck(isErr(ev(pg,"return await tvaRankings.updateMeta('%s',{title:''})"%a['id']),'invalid') and ev(pg,"return (await tvaRankings.get('%s')).rev"%a['id'])==2,'C10 modifica invalida: rifiutata e stato invariato (atomica)')
    # ===== I: elementi =====
    top=ev(pg,"return await tvaRankings.create({kind:'top',title:'Film preferiti',preset:'film'})")
    tid=top['id']
    cs=ev(pg,"return tvaRankings.catalog.search('item','spider',50)"); ck(isinstance(cs,list) and len(cs)>=3,'I1 ricerca catalogo titoli reale (139 schede)',len(cs) if isinstance(cs,list) else cs)
    nitems=ev(pg,"return [tvaRankings.catalog.search('item','',1000).length,tvaRankings.catalog.search('char','',1000).length,tvaRankings.catalog.search('universe','',1000).length,tvaRankings.catalog.search('saga','',1000).length,tvaRankings.catalog.search('org','',1000).length,tvaRankings.catalog.search('actor','',1000).length]")
    ck(nitems==[139,304,27,13,17,49],'I2 dimensioni cataloghi = dati reali dell\'app (139 titoli, 304 personaggi, 27 universi, 13 saghe, 17 organizzazioni, 49 attori)',nitems)
    ft=ev(pg,"return tvaRankings.catalog.search('item','',1000,{type:'film'}).length"); ck(0<ft<139,'I2b filtro preset Film sul catalogo reale',ft)
    x1=ev(pg,"const c=tvaRankings.catalog.search('item','spider',5)[0];const r=await tvaRankings.addItem('%s',{source:{type:'catalog',cat:'item',ref:c.ref}});return {r:r.ranking.items,c}"%tid)
    ck(not isErr(x1) and len(x1['r'])==1 and x1['r'][0]['name']==x1['c']['name'] and x1['r'][0]['source']['ref']==x1['c']['ref'],'I3 elemento da catalogo: nome dal catalogo, id stabile (cat+ref)',x1)
    ck(isErr(ev(pg,"return await tvaRankings.addItem('%s',{source:{type:'catalog',cat:'item',ref:'%s'}})"%(tid,x1['c']['ref'])),'duplicate'),'I4 stesso elemento di catalogo due volte: rifiutato (duplicato)')
    ck(isErr(ev(pg,"return await tvaRankings.addItem('%s',{source:{type:'catalog',cat:'item',ref:'999'}})"%tid),'invalid'),'I5 riferimento di catalogo inesistente: rifiutato')
    ck(isErr(ev(pg,"return await tvaRankings.addItem('%s',{source:{type:'catalog',cat:'zzz',ref:'001'}})"%tid),'invalid'),'I6 categoria di catalogo inventata: rifiutata')
    m1=ev(pg,"return await tvaRankings.addItem('%s',{name:'Hulk',note:'versione 1'})"%tid); m2=ev(pg,"return await tvaRankings.addItem('%s',{name:'Hulk',note:'versione 2'})"%tid)
    ids=[i['id'] for i in m2['ranking']['items']]
    ck(not isErr(m1) and not isErr(m2) and len(set(ids))==3 and sum(1 for i in m2['ranking']['items'] if i['name']=='Hulk')==2,'I7 due elementi manuali con lo stesso nome restano distinti (id diversi)',ids)
    ck(isErr(ev(pg,"return await tvaRankings.addItem('%s',{name:''})"%tid),'invalid'),'I8 elemento manuale senza nome rifiutato')
    cc=ev(pg,"const c=tvaRankings.catalog.search('char','thor',5);const r=await tvaRankings.addItem('%s',{source:{type:'catalog',cat:'char',ref:c[0].ref},note:'nota <script>x</script>'});return r.ranking.items.slice(-1)[0]"%tid)
    ck(not isErr(cc) and cc['source']['cat']=='char' and cc['source']['ref'].startswith('char-') and cc['note']=='nota <script>x</script>','I9 personaggio da catalogo + nota personale (testo inerte)',cc)
    up=ev(pg,"return await tvaRankings.updateItem('%s','%s',{name:'Hulk (rinominato)',note:'cambiata'})"%(tid,m1['itemId'])); it=[i for i in up['ranking']['items'] if i['id']==m1['itemId']][0]
    ck(it['name']=='Hulk (rinominato)' and it['note']=='cambiata','I10 modifica nome/nota elemento')
    rm=ev(pg,"return await tvaRankings.removeItem('%s','%s')"%(tid,m2['itemId'])); ck(len(rm['ranking']['items'])==3 and all(i['id']!=m2['itemId'] for i in rm['ranking']['items']),'I11 elimina elemento')
    # ===== R: riordino Top =====
    names=lambda r:[i['name'] for i in r['items']]
    for n in ('A','B','C','D','E'): ev(pg,"return await tvaRankings.addItem('%s',{name:'%s'})"%(tid,n))
    cur=ev(pg,"return await tvaRankings.get('%s')"%tid); ids={i['name']:i['id'] for i in cur['items']}; base=names(cur)
    r1=ev(pg,"return await tvaRankings.moveItem('%s','%s',0)"%(tid,ids['E'])); ck(names(r1['ranking'])[0]=='E' and len(r1['ranking']['items'])==len(base),'R1 sposta in testa (posizione 1)')
    r2=ev(pg,"return await tvaRankings.moveItem('%s','%s',999)"%(tid,ids['E'])); ck(names(r2['ranking'])[-1]=='E' and sorted(names(r2['ranking']))==sorted(base),'R2 indice oltre il limite: portato in fondo, nessun elemento perso')
    r3=ev(pg,"return await tvaRankings.moveItem('%s','%s',-5)"%(tid,ids['D'])); ck(names(r3['ranking'])[0]=='D','R3 indice negativo: portato in testa')
    r4=ev(pg,"return await tvaRankings.moveItemBy('%s','%s',1)"%(tid,ids['D'])); ck(names(r4['ranking'])[1]=='D','R4 pulsante "giu\'" (+1)')
    r5=ev(pg,"return await tvaRankings.moveItemBy('%s','%s',-1)"%(tid,ids['D'])); ck(names(r5['ranking'])[0]=='D','R5 pulsante "su\'" (-1)')
    r6=ev(pg,"return await tvaRankings.moveItemBy('%s','%s',-1)"%(tid,ids['D'])); ck(names(r6['ranking'])[0]=='D' and r6['ranking']['rev']>r5['ranking']['rev']-1,'R6 "su\'" in prima posizione: invariato, nessun errore')
    ck(isErr(ev(pg,"return await tvaRankings.moveItem('%s','it_0000000000000000',0)"%tid),'not-found'),'R7 elemento inesistente: not-found')
    ck(isErr(ev(pg,"return await tvaRankings.moveItem('%s','%s',NaN)"%(tid,ids['A'])),'invalid'),'R8 posizione non numerica rifiutata')
    fin=ev(pg,"return await tvaRankings.get('%s')"%tid); ck(names(fin)==names(r6['ranking']),'R9 l\'ordine e\' persistito')
    # ===== P: podio =====
    pd=ev(pg,"const r=await tvaRankings.get('%s');return tvaRankings.podium(r)"%tid)
    ck(pd['eligible'] and [x['item']['id'] for x in pd['top3']]==[i['id'] for i in fin['items'][:3]] and [x['position'] for x in pd['top3']]==[1,2,3],'P1 podio = prime tre posizioni della Top, nessun dato separato')
    ck([x['item']['id'] for x in pd['rest']]==[i['id'] for i in fin['items'][3:]] and pd['rest'][0]['position']==4,'P2 le altre posizioni restano consultabili (4..n)')
    mv=ev(pg,"await tvaRankings.moveItem('%s','%s',0);const r=await tvaRankings.get('%s');return tvaRankings.podium(r)"%(tid,fin['items'][-1]['id'],tid))
    ck(mv['top3'][0]['item']['id']==fin['items'][-1]['id'],'P3 dopo un riordino il podio segue la Top')
    small=ev(pg,"const t=await tvaRankings.create({kind:'top',title:'Piccola'});await tvaRankings.addItem(t.id,{name:'a'});const r=await tvaRankings.addItem(t.id,{name:'b'});return tvaRankings.podium(r.ranking)")
    ck(small['eligible'] is False and small['top3']==[],'P4 con meno di tre elementi il podio non e\' disponibile')
    ck(ev(pg,"const t=await tvaRankings.create({kind:'tier',title:'tl'});return tvaRankings.podium(t)")['eligible'] is False,'P5 una Tier List non ha podio')
    vw=ev(pg,"const r=await tvaRankings.updateMeta('%s',{view:'podium'});return r.view"%tid); ck(vw=='podium','P6 preferenza di vista "podio" salvata sulla Top')
    ck(ev(pg,"const t=await tvaRankings.create({kind:'tier',title:'tl2'});return (await tvaRankings.updateMeta(t.id,{view:'podium'})).view")=='list','P7 vista podio non applicabile alle Tier List')
    # ===== T: Tier List =====
    tl=ev(pg,"return await tvaRankings.create({kind:'tier',title:'Tier film',preset:'film'})")
    ck([t['name'] for t in tl['tiers']]==['S','A','B','C','D'] and len({t['id'] for t in tl['tiers']})==5,'T1 fasce iniziali S A B C D con id stabili',tl['tiers'])
    L=tl['id']; T={t['name']:t['id'] for t in tl['tiers']}
    its=[]
    for n in ('x1','x2','x3','x4'): its.append(ev(pg,"return (await tvaRankings.addItem('%s',{name:'%s'})).itemId"%(L,n)))
    g=ev(pg,"return await tvaRankings.get('%s')"%L); ck(all(i['tierId'] is None for i in g['items']),'T2 nuovi elementi tra i non classificati')
    tv=lambda: ev(pg,"return tvaRankings.tierView(await tvaRankings.get('%s'))"%L)
    ev(pg,"await tvaRankings.moveItemToTier('%s','%s','%s')"%(L,its[0],T['S'])); ev(pg,"await tvaRankings.moveItemToTier('%s','%s','%s')"%(L,its[1],T['S'])); ev(pg,"await tvaRankings.moveItemToTier('%s','%s','%s',0)"%(L,its[2],T['S']))
    v=tv(); sn=[i['name'] for i in [t for t in v['tiers'] if t['name']=='S'][0]['items']]
    ck(sn==['x3','x1','x2'],'T3 sposta elementi tra fasce e inserisce in posizione dentro la fascia',sn)
    ck([i['name'] for i in v['unranked']]==['x4'],'T4 i non classificati restano consultabili')
    ev(pg,"await tvaRankings.moveItemBy('%s','%s',1)"%(L,its[2])); sn=[i['name'] for i in [t for t in tv()['tiers'] if t['name']=='S'][0]['items']]; ck(sn==['x1','x3','x2'],'T5 riordino dentro la fascia con pulsante giu\'',sn)
    ev(pg,"await tvaRankings.moveItemToTier('%s','%s','%s')"%(L,its[2],T['B'])); v=tv()
    ck([i['name'] for i in [t for t in v['tiers'] if t['name']=='B'][0]['items']]==['x3'] and [i['name'] for i in [t for t in v['tiers'] if t['name']=='S'][0]['items']]==['x1','x2'],'T6 spostamento tra fasce diverse')
    ev(pg,"await tvaRankings.moveItemToTier('%s','%s',null)"%(L,its[2])); ck(sorted(i['name'] for i in tv()['unranked'])==['x3','x4'],'T7 riporta tra i non classificati (fascia null)')
    rn=ev(pg,"return await tvaRankings.renameTier('%s','%s','Capolavori <i>')"%(L,T['S'])); ck([t for t in rn['ranking']['tiers'] if t['id']==T['S']][0]['name']=='Capolavori <i>','T8 fascia rinominabile')
    ck(isErr(ev(pg,"return await tvaRankings.renameTier('%s','%s','   ')"%(L,T['S'])),'invalid'),'T9 nome fascia vuoto rifiutato')
    ck(len([t for t in ev(pg,"return await tvaRankings.renameTier('%s','%s','%s')"%(L,T['A'],'x'*80))['ranking']['tiers'] if len(t['name'])>24])==0,'T10 nome fascia limitato a 24 caratteri')
    ad=ev(pg,"return await tvaRankings.addTier('%s','Extra')"%L); ck(len(ad['ranking']['tiers'])==6 and ad['tierId'].startswith('ti_'),'T11 aggiunta fascia')
    mt=ev(pg,"return await tvaRankings.moveTier('%s','%s',0)"%(L,ad['tierId'])); ck(mt['ranking']['tiers'][0]['id']==ad['tierId'],'T12 riordino fasce')
    before=len(ev(pg,"return (await tvaRankings.get('%s')).items"%L)); rt=ev(pg,"return await tvaRankings.removeTier('%s','%s')"%(L,T['S']))
    ck(len(rt['ranking']['items'])==before and all(i['tierId'] is None or i['tierId']!=T['S'] for i in rt['ranking']['items']) and sorted(i['name'] for i in rt['ranking']['items'] if not i['tierId'])==['x1','x2','x3','x4'],'T13 eliminando una fascia gli elementi NON si perdono (tornano non classificati)')
    ck(isErr(ev(pg,"return await tvaRankings.moveItemToTier('%s','%s','ti_000000000000')"%(L,its[0])),'invalid'),'T14 fascia inesistente rifiutata')
    ck(isErr(ev(pg,"return await tvaRankings.moveItemToTier('%s','%s',null)"%(tid,fin['items'][0]['id'])),'invalid'),'T15 le Top non hanno fasce')
    ck(isErr(ev(pg,"return await tvaRankings.addTier('%s','x')"%tid),'invalid'),'T16 addTier su una Top rifiutato')
    ck(isErr(ev(pg,"let r;for(let i=0;i<20;i++){r=await tvaRankings.addTier('%s','f'+i)};return r"%L),'limit'),'T17 massimo tecnico di 20 fasce')
    ck(isErr(ev(pg,"const t=await tvaRankings.create({kind:'tier',title:'una',tiers:['S']});return await tvaRankings.removeTier(t.id,t.tiers[0].id)"),'invalid'),'T18 non si elimina l\'ultima fascia')
    # ===== D: duplicazione =====
    dp=ev(pg,"return await tvaRankings.duplicate('%s')"%L); orig=ev(pg,"return await tvaRankings.get('%s')"%L)
    ck(not isErr(dp) and dp['id']!=L and dp['title']==orig['title']+' (copia)' and dp['rev']==1,'D1 duplica classifica (nuovo id, titolo "(copia)")')
    ck(len(dp['items'])==len(orig['items']) and not ({i['id'] for i in dp['items']} & {i['id'] for i in orig['items']}) and not ({t['id'] for t in dp['tiers']} & {t['id'] for t in orig['tiers']}),'D2 la copia ha elementi e fasce con id NUOVI')
    omap={t['id']:t['name'] for t in orig['tiers']}; dmap={t['id']:t['name'] for t in dp['tiers']}
    ck([ (i['name'],omap.get(i['tierId'])) for i in orig['items']]==[(i['name'],dmap.get(i['tierId'])) for i in dp['items']],'D3 la copia conserva fasce, ordine e note')
    ev(pg,"await tvaRankings.removeItem('%s','%s')"%(dp['id'],dp['items'][0]['id'])); ck(len(ev(pg,"return (await tvaRankings.get('%s')).items"%L))==len(orig['items']),'D4 originale e copia sono indipendenti')
    # ===== X: elimina / cestino =====
    n0=len(ev(pg,"return await tvaRankings.list()")); ck(ev(pg,"return await tvaRankings.remove('%s')"%dp['id']) is True,'X1 elimina')
    ck(len(ev(pg,"return await tvaRankings.list()"))==n0-1 and isErr(ev(pg,"return await tvaRankings.get('%s')"%dp['id']),'not-found'),'X2 non piu\' in elenco')
    trs=ev(pg,"return await tvaRankings.trash.list()"); ck(any(t['id']==dp['id'] for t in trs),'X3 nessuna perdita: la classifica e\' nel cestino recuperabile')
    rs=ev(pg,"return await tvaRankings.trash.restore('%s')"%dp['id']); ck(not isErr(rs) and rs['id']==dp['id'] and len(rs['items'])==len(dp['items'])-1,'X4 ripristino dal cestino')
    ck(not any(t['id']==dp['id'] for t in ev(pg,"return await tvaRankings.trash.list()")),'X5 uscita dal cestino dopo il ripristino')
    ev(pg,"await tvaRankings.remove('%s')"%dp['id']); ev(pg,"await tvaRankings.trash.purge('%s')"%dp['id']); ck(not any(t['id']==dp['id'] for t in ev(pg,"return await tvaRankings.trash.list()")),'X6 eliminazione definitiva solo su richiesta esplicita')
    ck(isErr(ev(pg,"return await tvaRankings.remove('rk_0000000000000000')"),'not-found'),'X7 elimina inesistente: not-found')
    # ===== L: ricerca elenco =====
    ev(pg,"await tvaRankings.create({kind:'top',title:'Colonne sonore',description:'Le piu belle musiche',preset:'libera'})")
    q=lambda o: ev(pg,"return (await tvaRankings.list(%s)).map(x=>x.title)"%json.dumps(o))
    ck('Colonne sonore' in q({'query':'MUSICHE'}) and 'Colonne sonore' in q({'query':'colonne'}),'L1 ricerca per titolo e descrizione (senza maiuscole/accenti)')
    ck('Film preferiti' in q({'query':'hulk'}) ,'L2 ricerca anche tra i nomi degli elementi')
    ck(ev(pg,"const l=await tvaRankings.list({kind:'tier'});return l.length>0&&l.every(x=>x.kind==='tier')") is True and 'Film preferiti' not in q({'kind':'tier'}),'L3 filtro per tipo')
    ck('Film preferiti' in q({'preset':'film'}),'L4 filtro per categoria')
    # ===== IM: immagini =====
    mk="""const mk=(w,h,c)=>new Promise(r=>{const cv=document.createElement('canvas');cv.width=w;cv.height=h;const x=cv.getContext('2d');x.fillStyle=c||'#c33';x.fillRect(0,0,w,h);x.fillStyle='#fff';x.fillRect(w/4,h/4,w/2,h/2);cv.toBlob(b=>r(b),'image/png')});"""
    im=ev(pg,mk+"const b=await mk(300,200);const r=await tvaRankings.images.add(b);const b2=await mk(300,200);const r2=await tvaRankings.images.add(b2);return {r,same:r.id===r2.id,c2:r2.created}")
    ck(not isErr(im) and im['r']['id'].startswith('im_') and im['r']['mime'] in ('image/webp','image/jpeg'),'IM1 immagine PNG accettata e ricodificata (WebP/JPEG)',im)
    ck(im['same'] and im['c2'] is False,'IM2 stessa immagine: stesso id, nessun duplicato')
    big=ev(pg,mk+"const r=await tvaRankings.images.add(await mk(3000,2000,'#36c'));return r")
    ck(not isErr(big) and max(big['w'],big['h'])<=1024 and big['w']>big['h'],'IM3 immagine grande ridimensionata (<=1024, proporzioni)',big)
    ck(isErr(ev(pg,"return await tvaRankings.images.add(new Blob(['<svg xmlns=\"http://www.w3.org/2000/svg\"><script>alert(1)</script></svg>'],{type:'image/png'}))"),'image-invalid'),'IM4 SVG (anche con MIME falso): rifiutato')
    ck(isErr(ev(pg,"return await tvaRankings.images.add(new Blob(['not an image at all'],{type:'image/png'}))"),'image-invalid'),'IM5 testo travestito da PNG: rifiutato')
    ck(isErr(ev(pg,"return await tvaRankings.images.add(new Blob([],{type:'image/png'}))"),'image-invalid'),'IM6 file vuoto: rifiutato')
    ck(isErr(ev(pg,"const a=new Uint8Array(11*1024*1024);a.set([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a]);return await tvaRankings.images.add(new Blob([a],{type:'image/png'}))"),'image-too-large'),'IM7 file oltre 10 MB: rifiutato')
    ck(isErr(ev(pg,"const a=new Uint8Array(40);a.set([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a,0,0,0,13,0x49,0x48,0x44,0x52,0,1,0x11,0x70,0,1,0x11,0x70,8,6,0,0,0]);return await tvaRankings.images.add(new Blob([a],{type:'image/png'}))")),'IM8 PNG con dimensioni dichiarate enormi e dati assenti: rifiutato (nessun crash)')
    ck(isErr(ev(pg,"return await tvaRankings.images.add('stringa')"),'image-invalid') and isErr(ev(pg,"return await tvaRankings.images.add({size:1})"),'image-invalid'),'IM9 input non-Blob rifiutato')
    # collegamento immagine -> elemento, integrita' referenziale
    ph=ev(pg,"const t=await tvaRankings.create({kind:'top',title:'Con foto',imageMode:'images'});const r=await tvaRankings.addItem(t.id,{name:'Foto',image:{type:'user',id:'%s'}});return {t:t.id,it:r.ranking.items[0]}"%im['r']['id'])
    ck(not isErr(ph) and ph['it']['image']['id']==im['r']['id'],'IM10 immagine personale associata a un elemento',ph)
    ck(isErr(ev(pg,"return await tvaRankings.addItem('%s',{name:'X',image:{type:'user',id:'im_000000000000000000000000'}})"%ph['t']),'image-invalid') and len(ev(pg,"return (await tvaRankings.get('%s')).items"%ph['t']))==1,'IM11 immagine inesistente: operazione rifiutata, nessuna modifica parziale')
    ck(isErr(ev(pg,"return await tvaRankings.addItem('%s',{name:'X',image:{type:'url',src:'http://evil.example/x.png'}})"%ph['t'])),'IM12 URL esterni come immagine non ammessi')
    cim=ev(pg,"return await tvaRankings.addItem('%s',{name:'Cat',image:{type:'catalog',cat:'item',ref:'001'}})"%ph['t']); ck(not isErr(cim) and cim['ranking']['items'][-1]['image']=={'type':'catalog','cat':'item','ref':'001'},'IM13 immagine di catalogo = riferimento (nessun URL salvato)')
    ck(isErr(ev(pg,"return await tvaRankings.images.remove('%s')"%im['r']['id']),'conflict'),'IM14 immagine in uso: non eliminabile')
    gb=ev(pg,"return await tvaRankings.images.gc()"); ck(gb['removed']>=1 and ev(pg,"return (await tvaRankings.images.usage()).use['%s']"%im['r']['id'])==1,'IM15 pulizia: rimuove solo immagini orfane, conserva quelle in uso',gb)
    blob=ev(pg,"const b=await tvaRankings.images.get('%s');return {t:b.type,s:b.size}"%im['r']['id']); ck(blob['s']>0 and blob['t'] in ('image/webp','image/jpeg'),'IM16 lettura immagine salvata')
    # testo-only
    tx_=ev(pg,"const t=await tvaRankings.create({kind:'top',title:'Solo testo',imageMode:'text'});await tvaRankings.addItem(t.id,{name:'uno'});await tvaRankings.addItem(t.id,{name:'due'});await tvaRankings.addItem(t.id,{name:'tre'});const g=await tvaRankings.get(t.id);return g")
    ck(tx_['imageMode']=='text' and all(i['image'] is None for i in tx_['items']) and len(tx_['items'])==3,'TX1 classifica solo testuale completa e consultabile')
    # ===== V: validazione ostile =====
    po=ev(pg,"""const t=await tvaRankings.create({kind:'top',title:'Ostile'});
      const evil={id:t.id,kind:'top',title:'ok'+String.fromCharCode(0x202e,0x200b,0)+'fine',description:'x'.repeat(5000),preset:'<script>',imageMode:'<>',view:{a:1},items:[{id:'it_0000000000000001',name:'<img src=x onerror=alert(1)>',note:'n'.repeat(9000),source:{type:'manual'},image:null,extra:'zzz',__proto__:{polluted:1}}],tiers:'boh',share:{visibility:'public',ownerVid:'evil',shareId:'x'},constructor:{prototype:{polluted:2}}};
      const v=tvaRankings.validate(evil);return {v,pol:({}).polluted,pol2:Object.prototype.polluted}""")
    vv=po['v']; ck(vv['ok'] and vv['value']['title']=='ok fine','V1 caratteri di controllo/bidi rimossi dal titolo',vv.get('value',{}).get('title'))
    ck(len(vv['value']['description'])<=500 and vv['value']['items'][0]['note'].__len__()<=500,'V2 lunghezze limitate (descrizione, note)')
    ck(vv['value']['preset']=='libera' and vv['value']['imageMode']=='text' and vv['value']['view']=='list' and 'extra' not in vv['value']['items'][0],'V3 enum non validi -> valori sicuri; campi sconosciuti scartati')
    ck(vv['value']['share']['visibility']=='private' and vv['value']['share']['shareId'] is None and vv['value']['share']['ownerVid'] is None,'V4 struttura di condivisione presente ma inerte (privata, nessun id remoto, vid non valido scartato)')
    ck(po['pol'] is None and po['pol2'] is None,'V5 nessun prototype pollution')
    ck(vv['value']['items'][0]['name']=='<img src=x onerror=alert(1)>','V6 HTML nel nome conservato come testo inerte (il motore non scrive nel DOM)')
    badv=ev(pg,"""const bad=[null,[],'x',5,{id:'rk_1'},{id:'rk_0123456789abcdef',kind:'top'},{id:'rk_0123456789abcdef',kind:'top',title:'t',items:'no'},{id:'rk_0123456789abcdef',kind:'tier',title:'t',tiers:[]},{id:'rk_0123456789abcdef',kind:'top',title:'t',items:[{id:'bad',name:'x',source:{type:'manual'}}]},{id:'rk_0123456789abcdef',kind:'top',title:'t',items:[{id:'it_0123456789abcdef',name:'x',source:{type:'catalog',cat:'item',ref:'abc'}}]},{id:'rk_0123456789abcdef',kind:'top',title:'t',items:[{id:'it_0123456789abcdef',name:'x',source:{type:'manual'},image:{type:'url',src:'http://x'}}]}];return bad.map(b=>tvaRankings.validate(b).ok)""")
    ck(badv.count(True)==1,'V7 strutture malformate rifiutate (11 casi; "items:no" tollerato come elenco vuoto)',badv)
    lim=ev(pg,"""const t=await tvaRankings.create({kind:'top',title:'Limite'});const items=[];for(let i=0;i<501;i++)items.push({id:'it_'+i.toString(16).padStart(16,'0'),name:'n'+i,source:{type:'manual'},image:null});return await tvaRankings.save({...t,items},{expectedRev:t.rev})""")
    ck(isErr(lim,'limit'),'V8 oltre 500 elementi: rifiutato (limite tecnico)')
    d500=ev(pg,"""const t=await tvaRankings.create({kind:'top',title:'500'});const items=[];for(let i=0;i<500;i++)items.push({id:'it_'+i.toString(16).padStart(16,'0'),name:'n'+i,source:{type:'manual'},image:null});const r=await tvaRankings.save({...t,items},{expectedRev:t.rev});return {n:r.ranking.items.length,w:r.warnings.length}""")
    ck(not isErr(d500) and d500['n']==500,'V9 500 elementi: nessun limite artificiale basso (non 5/10)',d500)
    dup=ev(pg,"""const t=await tvaRankings.create({kind:'top',title:'Dup'});const mkI=(n,id,ref)=>({id,name:n,source:ref?{type:'catalog',cat:'item',ref}:{type:'manual'},image:null});const r=await tvaRankings.save({...t,items:[mkI('a','it_0000000000000001','001'),mkI('b','it_0000000000000002','001'),mkI('c','it_0000000000000001'),mkI('d','it_0000000000000003')]},{expectedRev:t.rev});return {names:r.ranking.items.map(i=>i.name),w:r.warnings}""")
    ck(dup['names']==['a','d'] and len(dup['w'])==2,'V10 duplicati (stesso catalogo / stesso id) scartati E segnalati nei warning (nessuna perdita silenziosa)',dup)
    # ===== record corrotti nel database =====
    cr=ev(pg,"""const db=await new Promise((res,rej)=>{const q=indexedDB.open('tva-rankings');q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error)});
      await new Promise((res,rej)=>{const t=db.transaction('rankings','readwrite');t.objectStore('rankings').put({id:'rk_deadbeefdeadbeef',kind:'top'});t.objectStore('rankings').put({id:'rk_feedfeedfeedfeed',kind:'zzz',title:'x'});t.oncomplete=res;t.onerror=()=>rej(t.error)});db.close();
      const l=await tvaRankings.list();return {n:l.length,c:l.corrupt,g:await tvaRankings.get('rk_deadbeefdeadbeef').then(()=>'ok',e=>e.code)}""")
    ck(isinstance(cr,dict) and len(cr['c'])==2 and cr['g']=='invalid' and cr['n']>0,'V11 record corrotti: elenco funziona, i corrotti sono SEGNALATI (non scartati in silenzio)',cr)
    raw=ev(pg,"""const db=await new Promise(r=>{const q=indexedDB.open('tva-rankings');q.onsuccess=()=>r(q.result)});const n=await new Promise(r=>{const q=db.transaction('rankings').objectStore('rankings').count();q.onsuccess=()=>r(q.result)});const has=await new Promise(r=>{const q=db.transaction('rankings').objectStore('rankings').get('rk_deadbeefdeadbeef');q.onsuccess=()=>r(!!q.result)});db.close();return has""")
    ck(raw is True,'V12 i dati corrotti restano nel database (recuperabili), non vengono cancellati')
    # ===== B: bozze =====
    dr=ev(pg,"""const t=await tvaRankings.create({kind:'top',title:'Con bozza'});await tvaRankings.addItem(t.id,{name:'a'});const cur=await tvaRankings.get(t.id);
      const snap=JSON.parse(JSON.stringify(cur));snap.items.push({id:'it_00000000000000aa',name:'in bozza',note:'',source:{type:'manual'},image:null,tierId:null});snap.title='Titolo bozza';
      await tvaRankings.drafts.save(t.id,snap,cur.rev);const g=await tvaRankings.get(t.id);const d=await tvaRankings.drafts.get(t.id);const l=await tvaRankings.drafts.list();
      return {t:t.id,savedTitle:g.title,draftTitle:d.data.title,n:d.data.items.length,stale:d.stale,inList:l.some(x=>x.id===t.id)}""")
    ck(dr['savedTitle']=='Con bozza' and dr['draftTitle']=='Titolo bozza' and dr['n']==2 and dr['stale'] is False and dr['inList'],'B1 bozza salvata separatamente dalla classifica; non altera i dati salvati')
    cm=ev(pg,"const x=await tvaRankings.drafts.commit('%s');return {title:x.ranking.title,n:x.ranking.items.length,rev:x.ranking.rev,d:await tvaRankings.drafts.get('%s')}"%(dr['t'],dr['t']))
    ck(cm['title']=='Titolo bozza' and cm['n']==2 and cm['d'] is None,'B2 conferma bozza: applicata e bozza eliminata',cm)
    dr2=ev(pg,"""const cur=await tvaRankings.get('%s');const snap=JSON.parse(JSON.stringify(cur));snap.title='Bozza B';await tvaRankings.drafts.save(cur.id,snap,cur.rev);
      await tvaRankings.updateMeta(cur.id,{description:'modifica altrove'});const d=await tvaRankings.drafts.get(cur.id);let code=null;try{await tvaRankings.drafts.commit(cur.id)}catch(e){code=e.code}
      const after=await tvaRankings.get(cur.id);return {stale:d.stale,code,title:after.title,desc:after.description,still:!!(await tvaRankings.drafts.get(cur.id))}"""%dr['t'])
    ck(dr2['stale'] is True and dr2['code']=='conflict' and dr2['title']=='Titolo bozza' and dr2['desc']=='modifica altrove' and dr2['still'] is True,'B3 bozza obsoleta (modifica altrove): conflitto segnalato, nulla sovrascritto, bozza conservata',dr2)
    ev(pg,"await tvaRankings.drafts.discard('%s')"%dr['t']); ck(ev(pg,"return await tvaRankings.drafts.get('%s')"%dr['t']) is None,'B4 scarto della bozza')
    au=ev(pg,"""const t=await tvaRankings.create({kind:'top',title:'Auto'});let title='v1';const h=tvaRankings.drafts.autosave(t.id,()=>({...t,title}),{delay:50,baseRev:t.rev});h.touch();title='v2';h.touch();title='v3';h.touch();
      const before=await tvaRankings.drafts.get(t.id);await new Promise(r=>setTimeout(r,250));const after=await tvaRankings.drafts.get(t.id);title='v4';h.touch();await h.flush();const f=await tvaRankings.drafts.get(t.id);h.stop();return {before:before&&before.data.title,after:after.data.title,f:f.data.title,saved:(await tvaRankings.get(t.id)).title}""")
    ck(au['after']=='v3' and au['f']=='v4' and au['saved']=='Auto','B5 salvataggio automatico con debounce (ultima versione) + flush; i dati ufficiali restano invariati',au)
    ck(isErr(ev(pg,"return await tvaRankings.drafts.save('rk_0123456789abcdef',{kind:'top'},0)"),'invalid'),'B6 bozza malformata rifiutata')
    # ===== CC: concorrenza tra schede =====
    cc0=ev(pg,"return await tvaRankings.create({kind:'top',title:'Concorrenza'})"); cid=cc0['id']
    pg2=newpage(ctx)
    pg.evaluate("()=>{window.__go=async(id,tag)=>{const r=[];for(let i=0;i<25;i++)r.push(tvaRankings.addItem(id,{name:tag+i}));await Promise.all(r);return true};return 1}")
    pg2.evaluate("()=>{window.__go=async(id,tag)=>{const r=[];for(let i=0;i<25;i++)r.push(tvaRankings.addItem(id,{name:tag+i}));await Promise.all(r);return true};return 1}")
    pg.evaluate("([id])=>{window.__p=window.__go(id,'A')}",[cid]); pg2.evaluate("([id])=>{window.__p=window.__go(id,'B')}",[cid])
    pg.evaluate("()=>window.__p"); pg2.evaluate("()=>window.__p")
    fin=ev(pg,"return await tvaRankings.get('%s')"%cid)
    nm=[i['name'] for i in fin['items']]
    ck(len(nm)==50 and len(set(nm))==50 and len({i['id'] for i in fin['items']})==50 and fin['rev']==51,'CC1 due schede scrivono insieme (50 aggiunte): nessun elemento perso o duplicato, rev=51',(len(nm),fin['rev']))
    ck(all(('A%d'%i) in nm and ('B%d'%i) in nm for i in range(25)),'CC2 tutte le aggiunte di entrambe le schede presenti')
    cf=ev(pg,"const c=await tvaRankings.get('%s');await tvaRankings.updateMeta(c.id,{title:'nuovo'});let code=null;try{await tvaRankings.save(c,{expectedRev:c.rev})}catch(e){code=e.code}const a=await tvaRankings.get(c.id);return {code,title:a.title,n:a.items.length}"%cid)
    ck(cf['code']=='conflict' and cf['title']=='nuovo' and cf['n']==50,'CC3 salvataggio con revisione obsoleta: rifiutato (conflict), nessuna sovrascrittura',cf)
    ev(pg2,"window.__evs=[];tvaRankings.on(e=>window.__evs.push(e));return 1"); ev(pg,"return await tvaRankings.updateMeta('%s',{description:'ping'})"%cid); pg2.wait_for_timeout(400)
    evs=ev(pg2,"return window.__evs"); ck(any(e['type']=='changed' and e['id']==cid for e in evs),'CC4 l\'altra scheda riceve la notifica di modifica (BroadcastChannel)',evs)
    pg2.close()
    # ===== Q: spazio esaurito =====
    q0=ev(pg,"const t=await tvaRankings.create({kind:'top',title:'Quota'});await tvaRankings.addItem(t.id,{name:'prima'});return await tvaRankings.get(t.id)")
    qe=ev(pg,"""const P=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){throw new DOMException('quota','QuotaExceededError')};let code=null,msg=null;try{await tvaRankings.addItem('%s',{name:'non deve salvarsi'})}catch(e){code=e.code;msg=e.message}
      let code2=null;try{await tvaRankings.create({kind:'top',title:'nuova non salvata'})}catch(e){code2=e.code}IDBObjectStore.prototype.put=P;const a=await tvaRankings.get('%s');return {code,msg,code2,n:a.items.length,rev:a.rev,l:(await tvaRankings.list()).filter(x=>x.title==='nuova non salvata').length}"""%(q0['id'],q0['id']))
    ck(qe['code']=='quota' and 'Spazio esaurito' in qe['msg'] and qe['code2']=='quota','Q1 spazio esaurito: errore esplicito "quota" con messaggio chiaro (aggiunta e creazione)',qe)
    ck(qe['n']==1 and qe['rev']==q0['rev'] and qe['l']==0,'Q2 nessuna modifica parziale: dati invariati dopo il fallimento')
    qa=ev(pg,"""const O=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(...a){const r=O.apply(this,a);try{this.transaction.abort()}catch(e){}return r};let code=null;try{await tvaRankings.addItem('%s',{name:'abort'})}catch(e){code=e.code}IDBObjectStore.prototype.put=O;const a=await tvaRankings.get('%s');return {code,n:a.items.length}"""%(q0['id'],q0['id']))
    ck(qa['code'] in ('storage-error','quota') and qa['n']==1,'Q3 transazione annullata a meta\': errore esplicito e dati integri',qa)
    ok_after=ev(pg,"const r=await tvaRankings.addItem('%s',{name:'dopo'});return r.ranking.items.length"%q0['id']); ck(ok_after==2,'Q4 dopo l\'errore il motore continua a funzionare')
    # ===== A: atomicita' duplicazione con errore =====
    n_before=len(ev(pg,"return await tvaRankings.list()"))
    dq=ev(pg,"""const P=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){throw new DOMException('q','QuotaExceededError')};let code=null;try{await tvaRankings.duplicate('%s')}catch(e){code=e.code}IDBObjectStore.prototype.put=P;return code"""%L)
    ck(dq=='quota' and len(ev(pg,"return await tvaRankings.list()"))==n_before,'Q5 duplicazione con spazio esaurito: nessuna copia parziale')
    ck(ev(pg,"return (await tvaRankings.status()).persistent")is True,'Q6 stato ancora persistente dopo gli errori')
    # ===== N: stato di rete / isolamento =====
    ext=[u for u in pg.net if not u.startswith('http://127.0.0.1:%d'%PORT) and not u.startswith('data:') and not u.startswith('blob:')]
    ck(not [u for u in ext if 'tmdb' not in u and 'gstatic' not in u and 'googleapis' not in u],'N1 nessuna richiesta di rete introdotta dal motore (solo risorse storiche dell\'app, bloccate nel test)',ext[:3])
    ls1=ev(pg,"const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o")
    new={k for k in ls1 if k not in ls0}; chg={k for k in ls0 if ls0[k]!=ls1.get(k)}
    ck(not [k for k in new|chg if 'rank' in k.lower()] and set(ls1)-set(ls0)<=set(),'N2 il motore non scrive in localStorage (salvataggi esistenti non toccati)',(new,chg))
    ck(not pg.errs,'N3 nessun errore di pagina durante tutti i test',pg.errs[:3])
    snapshot=ev(pg,"const l=await tvaRankings.list();return l.map(x=>x.id)"); ids_all=set(snapshot)
    pg.close(); ctx.close()
    # ===== PR: nuova sessione del browser =====
    ctx=p.chromium.launch_persistent_context(UD,viewport={'width':390,'height':844},service_workers='block'); pg=newpage(ctx)
    l2=ev(pg,"const l=await tvaRankings.list();return l.map(x=>x.id)")
    ck(set(l2)==ids_all and len(ids_all)>10,'PR1 riapertura del browser (nuova sessione): tutte le classifiche presenti (%d)'%len(ids_all),(len(l2),len(ids_all)))
    g2=ev(pg,"return await tvaRankings.get('%s')"%L); ck([t['name'] for t in g2['tiers']][0]=='Extra' and len(g2['items'])==4,'PR2 Tier List identica dopo la riapertura')
    imb=ev(pg,"const b=await tvaRankings.images.get('%s');return b.size"%im['r']['id']); ck(imb>0,'PR3 immagine personale ancora leggibile dopo la riapertura')
    dd=ev(pg,"return (await tvaRankings.drafts.list()).length"); ck(dd>=1,'PR4 bozze recuperabili dopo la riapertura',dd)
    pg.close(); ctx.close()
    # ===== MEM: IndexedDB non disponibile =====
    br=p.chromium.launch(); cx=br.new_context(service_workers='block'); pm=newpage(cx,"Object.defineProperty(window,'indexedDB',{value:undefined,configurable:true})")
    sm=ev(pm,"return await tvaRankings.status()"); ck(sm['backend']=='memory' and sm['persistent'] is False and sm['warning'] and 'NON vengono salvati' in sm['warning'],'M1 senza IndexedDB: modalita\' in memoria DICHIARATA (persistent=false + avviso), nessuna perdita silenziosa',sm)
    mo=ev(pm,"const t=await tvaRankings.create({kind:'top',title:'mem'});await tvaRankings.addItem(t.id,{name:'a'});let c=null;try{await tvaRankings.addItem(t.id,{name:''})}catch(e){c=e.code}return {n:(await tvaRankings.get(t.id)).items.length,c}")
    ck(mo['n']==1 and mo['c']=='invalid','M2 la modalita\' in memoria mantiene la stessa validazione e atomicita\'',mo)
    cx.close(); br.close()
shutil.rmtree(UD,ignore_errors=True)
SRV.terminate()
print('\nTOTALE: %d FAIL'%len(fails)); print('FAILS:',fails)
sys.exit(1 if fails else 0)
