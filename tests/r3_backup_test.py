# R3 Rankings: backup ZIP (STORE), importazione UNISCI/SOSTITUISCI, copie di sicurezza, bozza nuova classifica, tasto Indietro.
# Chromium headless, IndexedDB REALE, nessuna rete. NON e' Safari/WebKit: il collaudo su iPhone resta dell'utente.
import json,re,os,sys,socket,subprocess,time,tempfile,shutil,struct,zlib,zipfile,io,base64,hashlib
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
UD=tempfile.mkdtemp(prefix='r3ud_'); DL=tempfile.mkdtemp(prefix='r3dl_')
def newpage(ctx):
    pg=ctx.new_page(); pg.errs=[]; pg.net=[]
    pg.on('pageerror',lambda e:pg.errs.append(str(e))); pg.on('request',lambda r: pg.net.append(r.url))
    pg.route('**/*',lambda r: r.abort() if any(h in r.request.url for h in ('gstatic','googleapis','firebaseio','tmdb')) else r.continue_())
    pg.goto(U); pg.wait_for_function("()=>!!window.tvaRankings&&!!window.tvaRankingsUI&&!!window.tvaRankingsBackup",timeout=20000)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300); return pg
def ev(pg,js,arg=None): return pg.evaluate("async(A)=>{try{"+js+"}catch(e){return {__err:true,code:e&&e.code,msg:String(e&&e.message)}}}",arg)
def isErr(r,code=None): return isinstance(r,dict) and r.get('__err') and (code is None or r.get('code')==code)
def b64(b): return base64.b64encode(b).decode()
def wipe(pg): return ev(pg,"await new Promise(r=>{const q=indexedDB.deleteDatabase('tva-rankings');q.onsuccess=q.onerror=q.onblocked=()=>r()});return 1")
SEED="""
const RK=tvaRankings;
const mk=async(c)=>{const cv=document.createElement('canvas');cv.width=300;cv.height=200;const x=cv.getContext('2d');x.fillStyle=c;x.fillRect(0,0,300,200);x.fillStyle='#fff';x.fillText(c,10,20);const b=await new Promise(r=>cv.toBlob(r,'image/png'));return new File([b],'a.png',{type:'image/png'})};
const a=await RK.create({kind:'top',title:'Top A <b>x</b>',description:'desc A',preset:'film',imageMode:'images'});
let it1=(await RK.addItem(a.id,{source:{type:'manual'},name:'Uno',note:'n1'})).itemId;
await RK.addItem(a.id,{source:{type:'manual'},name:'Due'});
const cat=RK.catalog.search('item','',3)[0]; await RK.addItem(a.id,{source:{type:'catalog',cat:cat.cat,ref:cat.ref},name:cat.name,image:{type:'catalog',cat:cat.cat,ref:cat.ref}});
const im=await RK.images.add(await mk('#c81e1e')); await RK.updateItem(a.id,it1,{image:{type:'user',id:im.id}});
const b=await RK.create({kind:'tier',title:'Tier B',preset:'personaggi',imageMode:'text'});
const bi=(await RK.addItem(b.id,{source:{type:'manual'},name:'Zed'})).itemId; const bg=await RK.get(b.id); await RK.moveItemToTier(b.id,bi,bg.tiers[0].id);
const c=await RK.create({kind:'top',title:'Top C',imageMode:'images'}); const i3=(await RK.addItem(c.id,{source:{type:'manual'},name:'Tre'})).itemId;
const im2=await RK.images.add(await mk('#1e6ec8')); await RK.updateItem(c.id,i3,{image:{type:'user',id:im2.id}});
return {a:a.id,b:b.id,c:c.id,im:im.id,im2:im2.id};
"""
def seed(pg): return ev(pg,SEED)
def create_bk(pg):
    r=ev(pg,"const r=await tvaRankingsBackup.create();const u=new Uint8Array(await r.blob.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return {b64:btoa(s),counts:r.counts,name:r.name,warnings:r.warnings,size:r.size}")
    return r
INSP="const u=Uint8Array.from(atob(A),c=>c.charCodeAt(0));const r=await tvaRankingsBackup.inspect(u.buffer);return {rk:r.rankings.length,img:r.images.length,warn:r.warnings,counts:r.plan.counts,missing:r.plan.missingImageRefs,statuses:r.plan.rankings.map(x=>x.status),ids:r.rankings.map(x=>x.id),cur:r.plan.current}"
def insp(pg,data): return ev(pg,INSP,b64(data))
APPLY="const u=Uint8Array.from(atob(A.d),c=>c.charCodeAt(0));const r=await tvaRankingsBackup.inspect(u.buffer);return await tvaRankings.backup.apply({mode:A.mode,policy:A.policy,rankings:r.rankings,images:r.images})"
def apply(pg,data,mode='merge',policy='keep-both'): return ev(pg,APPLY,{'d':b64(data),'mode':mode,'policy':policy})
STATE="const L=await tvaRankings.list({});const out=[];for(const s of L){const r=await tvaRankings.get(s.id);out.push([r.id,r.rev,r.title,r.items.length])}const u=await tvaRankings.images.usage();const sn=await tvaRankings.backup.snapshots.list();return {r:out.sort(),imgs:u.all.map(i=>i.id).sort(),snaps:sn.length,trash:(await tvaRankings.trash.list()).length}"
def state(pg): return ev(pg,STATE)
def unpack(data): z=zipfile.ZipFile(io.BytesIO(data)); return [(i.filename,z.read(i.filename)) for i in z.infolist()]
def pack(entries,compress=False):
    bio=io.BytesIO()
    with zipfile.ZipFile(bio,'w',zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED) as z:
        for n,d in entries: z.writestr(n,d)
    return bio.getvalue()
def crc(b): return zlib.crc32(b)&0xffffffff
def rawzip(entries,count=None,eocd_comment=b'',cd_off_delta=0,trailing=b''):
    """entries: list of dict(name,data,flags,method,crc,csize,usize,lo_name,off_override,extra,ver) -> ZIP grezzo, anche malformato"""
    out=b''; cen=b''
    for e in entries:
        nb=e['name'].encode('utf-8') if isinstance(e['name'],str) else e['name']; d=e.get('data',b''); c=e.get('crc',crc(d)); cs=e.get('csize',len(d)); us=e.get('usize',len(d)); fl=e.get('flags',0x800); me=e.get('method',0)
        off=len(out) if 'off_override' not in e else e['off_override']
        if 'off_override' not in e:
            out+=struct.pack('<IHHHHHIIIHH',0x04034b50,20,fl,me,0,0x21,c,cs,us,len(nb),0)+nb+d
        cen+=struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,fl,me,0,0x21,c,cs,us,len(nb),0,0,e.get('disk',0),0,0,off)+nb
    cdoff=len(out)+cd_off_delta; n=len(entries) if count is None else count
    return out+cen+struct.pack('<IHHHHIIH',0x06054b50,0,0,n,n,len(cen),cdoff,len(eocd_comment))+eocd_comment+trailing
def E(name,data,**k): d=dict(name=name,data=data); d.update(k); return d
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(UD,viewport={'width':390,'height':844},service_workers='block',accept_downloads=True,downloads_path=DL)
    pg=newpage(ctx)
    # ===== Z: ZIP =====
    r=ev(pg,"const B=tvaRankingsBackup;const t=new TextEncoder().encode('123456789');const z=B.zip.write([{name:'a.txt',data:t},{name:'d/b.bin',data:new Uint8Array([1,2,3,255])},{name:'e.txt',data:new Uint8Array(0)}]);const rd=B.zip.read(await z.arrayBuffer());return {crc:B.crc32(t).toString(16),n:rd.length,names:rd.map(x=>x.name),sz:rd.map(x=>x.data.length),frozen:Object.isFrozen(B)}")
    ck(r['crc']=='cbf43926','Z1 CRC32 corretto (vettore standard cbf43926)',r); ck(r['n']==3 and r['names']==['a.txt','d/b.bin','e.txt'] and r['sz']==[9,4,0],'Z2 scrittura e rilettura: nomi, cartelle, file vuoto',r); ck(r['frozen'],'Z3 API congelata')
    wipe(pg); S=seed(pg); ck(not isErr(S) and S['a'],'Z4 dati di prova creati (2 Top con immagini, 1 Tier List)',S)
    bk=create_bk(pg); ck(not isErr(bk) and bk['counts']=={'rankings':3,'items':5,'images':2} and not bk['warnings'],'Z5 backup creato: 3 classifiche, 5 elementi, 2 immagini',bk if isErr(bk) else bk['counts']); data=base64.b64decode(bk['b64'])
    zf=zipfile.ZipFile(io.BytesIO(data)); ck(zf.testzip() is None and all(i.compress_type==0 for i in zf.infolist()),'Z6 compatibile con Python zipfile: CRC ok, tutti i file STORE')
    names=[i.filename for i in zf.infolist()]; ck(names[0]=='manifest.json' and 'rankings.json' in names and sum(1 for n in names if n.startswith('images/'))==2,'Z7 struttura: manifest.json, rankings.json, images/',names)
    open(DL+'/b.zip','wb').write(data); un=subprocess.run(['unzip','-t',DL+'/b.zip'],capture_output=True,text=True) if shutil.which('unzip') else None
    if un: ck(un.returncode==0 and 'No errors' in un.stdout,'Z8 compatibile con unzip (Info-ZIP): test integrita\' senza errori',un.stdout[-200:])
    else: bl('Z8 unzip','non installato')
    man=json.loads(zf.read('manifest.json')); ck(man['format']=='tva-rankings-backup' and man['formatVersion']==1 and man['counts']['rankings']==3 and len(man['images'])==2 and all(re.fullmatch(r'[0-9a-f]{8}',f['crc32']) for f in man['files']),'Z9 manifest: versione, data, conteggi, riferimenti immagini, CRC32',{k:man[k] for k in ('format','formatVersion','schema','counts')})
    # lettura di ZIP STORE creati da altri strumenti
    ent=unpack(data); r=insp(pg,pack(ent)); ck(not isErr(r) and r['rk']==3 and r['img']==2,'Z10 legge un ZIP STORE ricreato da Python (altro strumento)',r)
    if shutil.which('zip'):
        d0=tempfile.mkdtemp(); [os.makedirs(os.path.dirname(os.path.join(d0,n)),exist_ok=True) or open(os.path.join(d0,n),'wb').write(d) for n,d in ent]
        subprocess.run('cd %s && zip -0 -X -q ../zz.zip manifest.json rankings.json images/*'%d0,shell=True); zb=open(d0+'/../zz.zip','rb').read(); r=insp(pg,zb); ck(not isErr(r) and r['rk']==3,'Z11 legge un ZIP STORE creato da Info-ZIP (zip -0)',r); shutil.rmtree(d0,ignore_errors=True)
    else: bl('Z11 zip -0','zip non installato')
    r=insp(pg,pack(ent,True)); ck(isErr(r,'zip-unsupported') and 'compresso' in r['msg'],'Z12 ZIP compresso (deflate): rifiutato con messaggio chiaro (lettura compressa non implementata di proposito)',r)
    # corrotto / troncato / vuoto
    ck(isErr(insp(pg,data[:-37]),'zip-malformed'),'Z13 archivio troncato rifiutato')
    ck(isErr(insp(pg,b''),'zip-malformed') and isErr(insp(pg,b'PK'),'zip-malformed') and isErr(insp(pg,os.urandom(3000)),'zip-malformed'),'Z14 file vuoto, "PK" e dati casuali rifiutati')
    ck(isErr(insp(pg,data+b'GARBAGE'),'zip-malformed'),'Z15 dati estranei in coda rifiutati')
    rj=[d for n,d in ent if n=='rankings.json'][0]; bad=bytearray(data); i=data.find(rj[:60]); bad[i+10]^=0xFF; r=insp(pg,bytes(bad)); ck(isErr(r,'zip-crc'),'Z16 CRC32 errato (byte alterato nei dati): rifiutato',r)
    # CRC alterato solo nell'header centrale
    bad=bytearray(data); cd=data.rfind(b'PK\x01\x02'); bad[cd+16]^=0xFF; r=insp(pg,bytes(bad)); ck(isErr(r),'Z17 CRC32 alterato nella directory centrale: rifiutato',r)
    # path traversal & nomi
    base=[E('manifest.json',[d for n,d in ent if n=='manifest.json'][0]),E('rankings.json',rj)]
    for nm in ('../evil.json','/abs.json','images/../../x.json','a\\b.json','C:evil.json','a/b/c/d.json','images/./x.webp','x.json ','..'):
        r=insp(pg,rawzip(base+[E(nm,b'x')])); ck(isErr(r,'zip-path'),'Z18 percorso non ammesso rifiutato: %r'%nm,r)
    r=insp(pg,rawzip(base+[E('NUL\x00.json',b'x')])); ck(isErr(r,'zip-path'),'Z19 nome con carattere di controllo rifiutato',r)
    r=insp(pg,rawzip(base+[E('Manifest.JSON',b'x')])); ck(isErr(r,'zip-path'),'Z20 nomi duplicati (anche con maiuscole diverse) rifiutati',r)
    r=insp(pg,rawzip(base+[E('images/x.zip',b'PK\x05\x06'+b'\0'*18)])); ck(isErr(r,'backup-invalid') and 'previsto' in r['msg'],'Z21 ZIP annidato/file non previsto rifiutato',r)
    # struttura malevola
    e0=E('manifest.json',base[0]['data']); r=insp(pg,rawzip([e0,dict(e0,name='rankings.json',off_override=0)])); ck(isErr(r),'Z22 file sovrapposti (stesso offset) rifiutati',r)
    r=insp(pg,rawzip([E('manifest.json',b'{}',usize=0xFFFFFFF0,csize=0xFFFFFFF0)])); ck(isErr(r),'Z23 dimensioni dichiarate enormi rifiutate (nessuna allocazione)',r)
    r=insp(pg,rawzip([E('manifest.json',b'{}',usize=500)])); ck(isErr(r,'zip-malformed'),'Z24 dimensioni incoerenti (compresse != originali) rifiutate',r)
    r=insp(pg,rawzip([E('manifest.json',b'{}',csize=0xFFFFFFFF,usize=0xFFFFFFFF)])); ck(isErr(r,'zip-unsupported'),'Z25 ZIP64 non supportato, rifiutato',r)
    r=insp(pg,rawzip([E('manifest.json',b'{}',flags=0x801)])); ck(isErr(r,'zip-unsupported'),'Z26 archivio cifrato rifiutato',r)
    r=insp(pg,rawzip([E('f%03d.json'%i,b'x') for i in range(701)])); ck(isErr(r,'zip-limit'),'Z27 troppi file (701) rifiutati',r)
    r=insp(pg,rawzip([E('manifest.json',b'x'*(1048577))])); ck(isErr(r,'zip-limit'),'Z28 manifest eccessivo rifiutato',r)
    r=insp(pg,rawzip(base,eocd_comment=b'abc'+b'PK\x05\x06'+b'x'*18)); ck(isErr(r),'Z29 seconda "fine archivio" nel commento (ambiguita\') rifiutata',r)
    r=insp(pg,rawzip(base,cd_off_delta=5)); ck(isErr(r),'Z30 offset della directory centrale incoerente rifiutato',r)
    r=ev(pg,"try{tvaRankingsBackup.zip.read(new ArrayBuffer(257*1048576));return 'no'}catch(e){return e.code}"); ck(r=='zip-limit','Z31 archivio da 257 MB rifiutato subito dalla dimensione (limite 256 MB)',r)
    r=insp(pg,rawzip([E('manifest.json',b'{}',lo_name=1)])) # sanity: manifest {} -> manifest-invalid
    ck(isErr(r,'manifest-invalid'),'Z32 JSON del manifest incompleto rifiutato',r)
    # ===== B: manifest / contenuti =====
    def mod_manifest(fn,drop=None,extra=None,files=None):
        e=[(n,d) for n,d in ent]
        m=json.loads(dict(e)['manifest.json']); fn(m); e=[(n,d) for n,d in e if n!='manifest.json' and n!=drop]; e=[('manifest.json',json.dumps(m).encode())]+e
        return e
    r=insp(pg,pack([(n,d) for n,d in ent if n!='manifest.json'])); ck(isErr(r,'manifest-missing'),'B1 manifest mancante rifiutato',r)
    r=insp(pg,pack(mod_manifest(lambda m:None)[:0]+[('manifest.json',b'{non json'),('rankings.json',rj)])); ck(isErr(r,'manifest-invalid'),'B2 manifest non JSON rifiutato',r)
    def setv(**k):
        def f(m): m.update(k)
        return f
    r=insp(pg,pack(mod_manifest(setv(format='altro')))); ck(isErr(r,'manifest-invalid'),'B3 formato diverso rifiutato',r)
    r=insp(pg,pack(mod_manifest(setv(formatVersion=2)))); ck(isErr(r,'version-incompatible') and 'piu\' recente' in r['msg'],'B4 versione di formato piu\' recente: incompatibile, messaggio chiaro',r)
    r=insp(pg,pack(mod_manifest(setv(schema=2)))); ck(isErr(r,'version-incompatible'),'B5 schema dati piu\' recente: incompatibile',r)
    r=insp(pg,pack(mod_manifest(setv(formatVersion=0)))); ck(isErr(r,'manifest-invalid'),'B6 versione non valida (0) rifiutata',r)
    r=insp(pg,pack(mod_manifest(setv(formatVersion='x')))); ck(isErr(r,'manifest-invalid'),'B7 versione non numerica rifiutata',r)
    def badcrc(m): m['files'][0]['crc32']='deadbeef'
    r=insp(pg,pack(mod_manifest(badcrc))); ck(isErr(r,'zip-crc'),'B8 CRC32 del manifest diverso dai dati: rifiutato',r)
    def badcnt(m): m['counts']['rankings']=99
    r=insp(pg,pack(mod_manifest(badcnt))); ck(isErr(r,'backup-invalid'),'B9 numero di classifiche diverso dal manifest rifiutato',r)
    imgname=[n for n,d in ent if n.startswith('images/')][0]
    r=insp(pg,pack(mod_manifest(lambda m:None,drop=imgname))); ck(isErr(r,'backup-invalid') and 'assente' in r['msg'],'B10 immagine dichiarata ma assente nell\'archivio: rifiutato',r)
    # immagine mancante dichiarata onestamente (non nel manifest): import con avviso
    def nomg(m):
        m['files']=[f for f in m['files'] if f['name']!=imgname]; m['images']=[i for i in m['images'] if i['file']!=imgname]; m['counts']['images']-=1; m['missingImages']=[imgname.split('/')[1].split('.')[0]]
    wipe(pg); r=insp(pg,pack(mod_manifest(nomg,drop=imgname))); ck(not isErr(r) and r['missing']>=1 and r['img']==1,'B11 immagine mancante (non presente nel backup): anteprima la segnala (elementi senza immagine)',r)
    # immagine manomessa: contenuto diverso dall'id, formato non ammesso, immagine non decodificabile
    def with_img(newdata):
        e=[(n,d) for n,d in ent]; m=json.loads(dict(e)['manifest.json']); e=[(n,(newdata if n==imgname else d)) for n,d in e if n!='manifest.json']
        for f in m['files']:
            if f['name']==imgname: f['crc32']='%08x'%crc(newdata); f['size']=len(newdata)
        for i in m['images']:
            if i['file']==imgname: i['bytes']=len(newdata)
        return [('manifest.json',json.dumps(m).encode())]+e
    orig=dict(ent)[imgname]
    r=insp(pg,pack(with_img(orig[:-5]+b'XXXXX'))); ck(isErr(r),'B12 immagine alterata (hash != id): rifiutata',r)
    r=insp(pg,pack(with_img(b'\x89PNG\r\n\x1a\n'+b'0'*100))); ck(isErr(r,'image-invalid'),'B13 immagine PNG/formato non ammesso rifiutata',r)
    r=insp(pg,pack(with_img(b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'))); ck(isErr(r,'image-invalid'),'B14 SVG con script rifiutato',r)
    r=insp(pg,pack(with_img(b'RIFF\x10\x00\x00\x00WEBPVP8 '+b'\0'*40))); ck(isErr(r),'B15 WebP illeggibile/finto rifiutato',r)
    # classifiche non valide
    def with_rk(fn):
        e=[(n,d) for n,d in ent]; m=json.loads(dict(e)['manifest.json']); j=json.loads(dict(e)['rankings.json']); fn(j); nb=json.dumps(j).encode()
        for f in m['files']:
            if f['name']=='rankings.json': f['crc32']='%08x'%crc(nb); f['size']=len(nb)
        m['counts']['rankings']=len(j['rankings']); m['rankingIds']=[x.get('id') for x in j['rankings'] if isinstance(x,dict)] if isinstance(j['rankings'],list) else []
        return [('manifest.json',json.dumps(m).encode()),('rankings.json',nb)]+[(n,d) for n,d in e if n.startswith('images/')]
    r=insp(pg,pack(with_rk(lambda j:j['rankings'][0].update(kind='boh')))); ck(isErr(r,'backup-invalid') and 'non valida' in r['msg'],'B16 classifica con tipo non valido: archivio rifiutato',r)
    r=insp(pg,pack(with_rk(lambda j:j['rankings'][0]['items'][0].update(name='')))); ck(isErr(r,'backup-invalid'),'B17 elemento senza nome: archivio rifiutato',r)
    r=insp(pg,pack(with_rk(lambda j:j['rankings'].append(j['rankings'][0])))); ck(isErr(r,'backup-invalid') and 'duplicato' in r['msg'],'B18 identificativi duplicati nel backup rifiutati',r)
    r=insp(pg,pack(with_rk(lambda j:j.update(rankings={'a':1})))); ck(isErr(r),'B19 elenco classifiche non valido rifiutato',r)
    def xss(j): j['rankings'][0]['title']='<img src=x onerror=window.__pwn=1> T'; j['rankings'][0]['items'][0]['note']='<script>window.__pwn=2</script>'
    r=insp(pg,pack(with_rk(xss))); ck(not isErr(r) and r['rk']==3,'B20 HTML/script nei testi: accettato come TESTO (nessuna esecuzione in anteprima)',r); ck(ev(pg,"return window.__pwn===undefined"),'B21 nessuno script eseguito')
    def proto(j): j['rankings'][0]['__proto__']={'polluted':1}; j['rankings'][0]['constructor']={'prototype':{'polluted2':1}}; j['rankings'][0]['items'][0]['__proto__']={'polluted3':1}
    raw=json.dumps(with_rk(lambda j:None)[1][1].decode() if False else '')  # placeholder
    r=insp(pg,pack(with_rk(proto))); ck(not isErr(r) and ev(pg,"return ({}).polluted===undefined&&({}).polluted2===undefined&&({}).polluted3===undefined&&Object.prototype.polluted===undefined"),'B22 prototype pollution: campi estranei ignorati, Object.prototype intatto',r)
    r=insp(pg,pack(with_rk(lambda j:j.update(rankings=[dict(j['rankings'][0],id='rk_%016x'%i) for i in range(501)])))); ck(isErr(r) ,'B23 oltre 500 classifiche rifiutato',r)
    # ===== I: importazione =====
    fresh=lambda: wipe(pg)
    fresh(); r=apply(pg,data,'merge'); st=state(pg)
    ck(not isErr(r) and r['imported']==3 and r['imagesAdded']==2 and r['snapshotId'] is None and len(st['r'])==3 and len(st['imgs'])==2,'I1 UNISCI su archivio vuoto: 3 classifiche e 2 immagini, nessuna copia di sicurezza necessaria',(r,st))
    ids=sorted(x[0] for x in st['r']); ck(ids==sorted([S['a'],S['b'],S['c']]) and all(x[1]==1 for x in st['r']),'I2 identificativi originali conservati, revisione a 1')
    A1=ev(pg,"return await tvaRankings.get(A)",S['a']); ck(A1['title']=='Top A <b>x</b>' and A1['items'][0]['image']['type']=='user' and A1['items'][2]['image']['type']=='catalog','I3 contenuto fedele (titolo con HTML come testo, immagine utente e di catalogo)')
    blob_ok=ev(pg,"const b=await tvaRankings.images.get(A);return b.size>0&&b.type==='image/webp'||b.type==='image/jpeg'",S['im']); ck(blob_ok is True,'I4 immagine personale ripristinata e leggibile')
    before=state(pg); r=apply(pg,data,'merge'); after=state(pg)
    ck(not isErr(r) and r['imported']==0 and r['skippedIdentical']==3 and before==after,'I5 UNISCI ripetuto: tutte identiche, nulla cambia (nessun duplicato)',(r,))
    ev(pg,"return await tvaRankings.updateMeta(A,{title:'Modificata dopo il backup'})",S['a'])
    r=apply(pg,data,'merge','keep-both'); st=state(pg)
    ck(not isErr(r) and r['keptBoth']==1 and r['imported']==1 and len(st['r'])==4,'I6 conflitto di identificativo: UNISCI "mantieni entrambe" (4 classifiche)',(r,st['r']))
    titles=sorted(x[2] for x in st['r']); ck('Top A <b>x</b> (importata)' in titles and 'Modificata dopo il backup' in titles,'I7 la locale resta intatta, la importata e\' una copia con nuovo id e titolo "(importata)"',titles)
    fresh(); apply(pg,data,'merge'); ev(pg,"return await tvaRankings.updateMeta(A,{title:'Locale diversa'})",S['a']); r=apply(pg,data,'merge','skip'); st=state(pg)
    ck(not isErr(r) and r['skippedConflict']==1 and r['imported']==0 and len(st['r'])==3 and any(x[2]=='Locale diversa' for x in st['r']),'I8 conflitto con "salta": nessuna modifica alla classifica locale',(r,st['r']))
    fresh(); apply(pg,data,'merge'); ev(pg,"await tvaRankings.remove(A)",S['c']); r=apply(pg,data,'merge','keep-both'); st=state(pg)
    ck(not isErr(r) and r['keptBoth']==1 and st['trash']==1 and len(st['r'])==3,'I9 id presente nel Cestino = conflitto gestito (nessuna collisione al ripristino)',(r,st))
    # SOSTITUISCI
    fresh(); X=ev(pg,"const a=await tvaRankings.create({kind:'top',title:'Locale X',imageMode:'text'});await tvaRankings.addItem(a.id,{name:'x1'});const d=await tvaRankings.create({kind:'top',title:'Locale Y',imageMode:'text'});await tvaRankings.drafts.save(d.id,Object.assign({},d,{title:'bozza Y'}),d.rev);return [a.id,d.id]")
    r=apply(pg,data,'replace'); st=state(pg)
    ck(not isErr(r) and r['mode']=='replace' and r['imported']==3 and r['replacedPrevious']==2 and r['snapshotId'] and st['snaps']==1,'I10 SOSTITUISCI: 3 importate, 2 precedenti in una copia di sicurezza',(r,))
    ck(sorted(x[0] for x in st['r'])==sorted([S['a'],S['b'],S['c']]) and not any(x[0] in X for x in st['r']),'I11 dopo la sostituzione ci sono solo le classifiche del backup')
    ck(ev(pg,"return (await tvaRankings.drafts.list()).length")==0,'I12 bozze delle classifiche sostituite rimosse (salvate nella copia)')
    r2=ev(pg,"const s=await tvaRankings.backup.snapshots.list();return await tvaRankings.backup.snapshots.restore(s[0].id)"); st=state(pg)
    ck(not isErr(r2) and r2['restored']==2 and sorted(x[0] for x in st['r'])==sorted(X) and st['snaps']==1,'I13 ripristino della copia: tornano le 2 classifiche locali; la copia ripristinata viene scambiata con una nuova (nessuna perdita)',(r2,st))
    ck(ev(pg,"return (await tvaRankings.drafts.list()).length")==1,'I14 la bozza torna con il ripristino')
    r3=ev(pg,"const s=await tvaRankings.backup.snapshots.list();return await tvaRankings.backup.snapshots.restore(s[0].id)"); st=state(pg)
    ck(not isErr(r3) and sorted(x[0] for x in st['r'])==sorted([S['a'],S['b'],S['c']]) and len(st['imgs'])==2,'I15 secondo ripristino: tornano le classifiche del backup, con le immagini')
    # limite copie
    fresh(); ev(pg,"await tvaRankings.create({kind:'top',title:'L',imageMode:'text'});return 1")
    for i in range(5): r=apply(pg,data,'replace'); 
    r=apply(pg,data,'replace'); ck(isErr(r,'limit') and state(pg)['snaps']==5,'I16 con 5 copie di sicurezza la sostituzione e\' bloccata (nessuna cancellazione silenziosa)',r)
    ev(pg,"const s=await tvaRankings.backup.snapshots.list();return await tvaRankings.backup.snapshots.remove(s[0].id)"); ck(state(pg)['snaps']==4,'I17 eliminazione di una copia di sicurezza')
    # errori durante l'applicazione: rollback totale
    fresh(); ev(pg,"const a=await tvaRankings.create({kind:'top',title:'Locale',imageMode:'text'});await tvaRankings.addItem(a.id,{name:'k'});return 1"); s0=state(pg)
    ev(pg,"window.__p=IDBObjectStore.prototype.put;let n=0;IDBObjectStore.prototype.put=function(v){if(this.name==='rankings'&&++n==2)throw new DOMException('quota','QuotaExceededError');return window.__p.apply(this,arguments)};return 1")
    r=apply(pg,data,'merge'); ev(pg,"IDBObjectStore.prototype.put=window.__p;return 1"); s1=state(pg)
    ck(isErr(r,'quota') and s0==s1,'I18 errore a meta\' UNISCI (spazio esaurito sulla 2a classifica): nessuna modifica parziale',(r,s1))
    ev(pg,"window.__p=IDBObjectStore.prototype.put;let n=0;IDBObjectStore.prototype.put=function(v){if(this.name==='rankings'&&++n==2)throw new DOMException('quota','QuotaExceededError');return window.__p.apply(this,arguments)};return 1")
    r=apply(pg,data,'replace'); ev(pg,"IDBObjectStore.prototype.put=window.__p;return 1"); s1=state(pg)
    ck(isErr(r,'quota') and s0==s1 and s1['snaps']==0,'I19 errore a meta\' SOSTITUISCI: stato identico a prima e nessuna copia orfana (transazione unica)',(r,s1))
    ev(pg,"window.__p=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(v){if(this.name==='meta')throw new DOMException('quota','QuotaExceededError');return window.__p.apply(this,arguments)};return 1")
    r=apply(pg,data,'replace'); ev(pg,"IDBObjectStore.prototype.put=window.__p;return 1"); s1=state(pg)
    ck(isErr(r) and s0==s1,'I20 se la copia di sicurezza non si salva la SOSTITUZIONE non avviene: dati intatti',(r,s1))
    ev(pg,"window.__p=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(v){if(this.name==='images')throw new DOMException('quota','QuotaExceededError');return window.__p.apply(this,arguments)};return 1")
    r=apply(pg,data,'merge'); ev(pg,"IDBObjectStore.prototype.put=window.__p;return 1"); ck(isErr(r,'quota') and state(pg)==s0,'I21 errore sulle immagini: rollback completo',r)
    # restore con errore
    apply(pg,data,'replace'); s2=state(pg)
    ev(pg,"window.__p=IDBObjectStore.prototype.put;let n=0;IDBObjectStore.prototype.put=function(v){if(this.name==='rankings'&&++n==1)throw new DOMException('x','QuotaExceededError');return window.__p.apply(this,arguments)};return 1")
    r=ev(pg,"const s=await tvaRankings.backup.snapshots.list();return await tvaRankings.backup.snapshots.restore(s[0].id)"); ev(pg,"IDBObjectStore.prototype.put=window.__p;return 1"); s3=state(pg)
    ck(isErr(r) and s3==s2,'I22 errore durante il RIPRISTINO di una copia: nessuna modifica, la copia resta disponibile',(r,s3))
    # immagine con stesso id ma contenuto diverso nel DB
    fresh(); ev(pg,"await tvaRankings.status();return 1"); ev(pg,"""const db=await new Promise(r=>{const q=indexedDB.open('tva-rankings');q.onsuccess=()=>r(q.result)});await new Promise(r=>{const t=db.transaction('images','readwrite');t.objectStore('images').put({id:A,blob:new Blob(['diverso'],{type:'image/webp'}),mime:'image/webp',w:1,h:1,bytes:7,createdAt:1});t.oncomplete=()=>r()});db.close();return 1""",S['im'])
    r=apply(pg,data,'merge'); ck(isErr(r,'conflict') and len(state(pg)['r'])==0,'I23 immagine con stesso id ma contenuto diverso: importazione annullata, nulla importato',r)
    # immagini mancanti: import senza immagine
    fresh(); r=apply(pg,pack(mod_manifest(nomg,drop=imgname)),'merge'); st=state(pg)
    miss=ev(pg,"const a=await tvaRankings.get(A);return [a.items[0].name,a.items[0].image]",S['a']); ck(not isErr(r) and r['missingImages']>=1 and len(st['r'])==3,'I24 immagini mancanti: elementi importati SENZA immagine, segnalato nel resoconto',(r,miss))
    ck(ev(pg,"const L=await tvaRankings.list({});for(const s of L){await tvaRankings.get(s.id)}return 1")==1,'I25 integrita\' referenziale dopo l\'importazione (nessun riferimento a immagini inesistenti)')
    # limite 500 classifiche
    fresh(); ev(pg,"for(let i=0;i<498;i++)await tvaRankings.create({kind:'top',title:'n'+i,imageMode:'text'});return 1"); s4=state(pg)
    r=apply(pg,data,'merge'); ck(isErr(r,'limit') and state(pg)==s4,'I26 oltre il limite di 500 classifiche: importazione rifiutata per intero',r)
    # ===== P: persistenza dopo riapertura =====
    fresh(); apply(pg,data,'replace'); apply(pg,data,'replace'); s5=state(pg); pg.close(); ctx.close()
    ctx=p.chromium.launch_persistent_context(UD,viewport={'width':390,'height':844},service_workers='block',accept_downloads=True,downloads_path=DL); pg=newpage(ctx); s6=state(pg)
    ck(s5==s6 and len(s6['r'])==3 and s6['snaps']==s5['snaps']>=1 and len(s6['imgs'])==2,'P1 dopo chiusura e riapertura del browser: classifiche, immagini e copie di sicurezza presenti',(s5,s6))
    bk2=create_bk(pg); ck(not isErr(bk2) and bk2['counts']['rankings']==3,'P2 il backup si puo\' rifare dopo la riapertura')
    # ===== L: nessuna scrittura fuori da Rankings =====
    ck(not [k for k in ev(pg,"return Object.keys(localStorage)") if 'rank' in k.lower()],'L1 nessuna chiave Rankings in localStorage')
    ext=[u for u in pg.net if not u.startswith('http://127.0.0.1:%d'%PORT) and not u.startswith(('data:','blob:'))]; ck(not [u for u in ext if not any(h in u for h in ('gstatic','googleapis','firebaseio','tmdb'))],'L2 nessuna richiesta di rete propria',ext[:3])
    ck(not pg.errs,'L3 nessun errore JavaScript non gestito',pg.errs[:3])
    ctx.close()
print('FAILS:',fails); print('BLOCKED:',blocked)
SRV.terminate(); shutil.rmtree(UD,ignore_errors=True); shutil.rmtree(DL,ignore_errors=True); sys.exit(1 if fails else 0)
