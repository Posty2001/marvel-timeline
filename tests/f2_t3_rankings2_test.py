# Rankings 2.0: preservazione dati IndexedDB (build precedente -> nuova), avviso record, layout 320/390/412/768, podio/Tier, tastiera. Chromium emulato (NON Safari reale).
import os,sys,json,subprocess,tempfile,shutil,time
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
NEW=ROOT; OLDREF=os.environ.get('RK_OLD_REF','188fd80')
tmp=tempfile.mkdtemp(); OLD=tmp+'/old'; os.makedirs(OLD)
r=subprocess.run('git -C %s archive %s | tar -x -C %s'%(NEW,OLDREF,OLD),shell=True)
if r.returncode!=0 or not os.path.exists(OLD+'/index.html'): blocked('R2-0 build precedente non esportabile',OLDREF); summary(); sys.exit(0)
LINK=tmp+'/cur'; os.symlink(OLD,LINK)
import socket
def fp2():
    s=socket.socket();s.bind(('127.0.0.1',0));p=s.getsockname()[1];s.close();return p
port=fp2(); srv=subprocess.Popen([sys.executable,'-m','http.server',str(port),'--bind','127.0.0.1','--directory',LINK],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
base='http://127.0.0.1:%d'%port
def swap(to):
    os.remove(LINK); os.symlink(to,LINK)
DUMP="""async()=>{const db=await new Promise((res,rej)=>{const q=indexedDB.open('tva-rankings');q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error)});
 const out={};for(const n of [...db.objectStoreNames]){const rows=await new Promise((res,rej)=>{const t=db.transaction(n,'readonly').objectStore(n).getAll();t.onsuccess=()=>res(t.result);t.onerror=()=>rej(t.error)});
  out[n]=await Promise.all(rows.map(async r=>{const o={};for(const k of Object.keys(r).sort()){const v=r[k];if(v instanceof Blob){o[k]='BLOB:'+v.type+':'+v.size}else o[k]=v}return JSON.stringify(o)}));out[n].sort()}
 db.close();return out}"""
def _png():
    import zlib,struct,base64
    w=h=24; raw=b''.join(b'\x00'+b''.join(bytes([(x*10)%256,(y*10)%256,160]) for x in range(w)) for y in range(h))
    def ch(t,d): c=struct.pack('>I',len(d))+t+d; return c+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return base64.b64encode(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b'')).decode()
PNG=_png()
SEED="""async(png)=>{const bin=atob(png),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
 const t=await tvaRankings.create({kind:'top',title:'La mia classifica reale con dodici elementi',preset:'libera',imageMode:'images',description:'12 elementi'});
 const rid=(t.ranking||t).id; const names=['Uno','Due','Tre','Quattro','Cinque','Sei','Sette','Otto','Nove','Dieci','Undici','Dodici con un nome parecchio lungo'];
 for(let i=0;i<12;i++){await tvaRankings.addItem(rid,{source:{type:'manual'},name:names[i],note:'nota '+i})}
 let img=null; try{img=await tvaRankings.images.add(new Blob([u],{type:'image/png'}))}catch(e){}
 const full=await tvaRankings.get(rid); let imgOk=false; if(img){try{await tvaRankings.updateItem(rid,full.items[0].id,{image:{type:'user',id:img.id}});imgOk=true}catch(e){}}
 await tvaRankings.updateMeta(rid,{view:'podium'});
 const u2=await tvaRankings.create({kind:'tier',title:'Tier di prova',preset:'libera',imageMode:'text'}); const uid=(u2.ranking||u2).id;
 for(const n of ['A1','B2','C3']){await tvaRankings.addItem(uid,{source:{type:'manual'},name:n})}
 const tr=await tvaRankings.create({kind:'top',title:'Da cestinare',preset:'libera'}); await tvaRankings.remove((tr.ranking||tr).id);
 return {rid,uid,imgOk}}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---- A) dati: crea con build precedente, apri con la nuova ----
    c=newctx(b); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:150]))
    enter(pg,base); pg.wait_for_timeout(500)
    seeded=pg.evaluate(SEED,PNG); d0=pg.evaluate(DUMP)
    ck(len(d0.get('rankings',[]))>=2,'D0 dati creati con la build precedente (%s)'%OLDREF,seeded)
    swap(NEW); pg.goto(base+'/index.html?nuova=1'); pg.wait_for_timeout(1800)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(1000)
    ck(pg.evaluate("getComputedStyle(document.getElementById('rkRoot')).getPropertyValue('--holo').trim().toLowerCase()")=='#182b38','D1 la build caricata e\' la nuova (Rankings 2.0)')
    ck(pg.evaluate("document.querySelector('#rkCorruptBanner')===null && !document.body.innerText.includes(' record non leggibili sono stati lasciati')"),'D2 nessun avviso «record non leggibili» con 0 record illeggibili (bug dell\'array vuoto corretto)')
    ck(pg.evaluate("document.querySelectorAll('.rk-card[data-rk]').length")==2,'D3 le classifiche esistenti compaiono tutte nell\'Archivio (2)')
    pg.evaluate("[...document.querySelectorAll('.rk-card-main')].find(x=>x.textContent.includes('dodici elementi')).click()"); pg.wait_for_timeout(1000)
    ck(pg.evaluate("document.querySelectorAll('.rk-podium .rk-pod').length")==3 and pg.evaluate("document.querySelectorAll('#rkPodium ~ ol .rk-rowi').length")==9,'D4 classifica a 12 elementi: podio (3) + resto (9), stessi dati')
    pg.evaluate("document.getElementById('rkViewList').click()"); pg.wait_for_timeout(700)
    ck(pg.evaluate("document.querySelectorAll('#rkTop .rk-rowi').length")==12,'D5 vista Elenco: tutti i 12 elementi')
    pg.evaluate("document.getElementById('rkViewPod').click()"); pg.wait_for_timeout(500)
    d1=pg.evaluate(DUMP)
    # la vista cambia meta (view) solo nel rowd della classifica: confronto escludendo la sola chiave view/rev/updatedAt della classifica aperta
    import re
    def strip(d):
        o={}
        for k,v in d.items():
            o[k]=[re.sub(r'"(view|rev|updatedAt)":[^,}]*,?','',x) for x in v]; o[k].sort()
        return o
    ck(strip(d0)==strip(d1),'D6 IndexedDB identico dopo apertura/navigazione (escluse le sole preferenze di vista e revisione)')
    ck(all(len(d0[k])==len(d1[k]) for k in d0),'D7 numero di record invariato in ogni archivio (rankings, immagini, bozze, cestino)')
    if seeded.get('imgOk'):
        ck(pg.evaluate("!!document.querySelector('#rkPodium .rk-th img')"),'D8 immagine personale mostrata nel podio')
    else: blocked('D8 immagine personale nel podio','seed immagine non disponibile in questo ambiente')
    ck(not errs,'D9 nessun errore JavaScript',errs); c.close()
    # ---- B) record illeggibile: avviso con numero, record NON toccato ----
    c=newctx(b); pg=c.new_page(); enter(pg,base); pg.wait_for_timeout(500)
    pg.evaluate("""async()=>{await tvaRankings.create({kind:'top',title:'Buona',preset:'libera'});
      const db=await new Promise(r=>{const q=indexedDB.open('tva-rankings');q.onsuccess=()=>r(q.result)});
      await new Promise(r=>{const t=db.transaction('rankings','readwrite');t.objectStore('rankings').put({id:'rk_corrotto000000',kind:'top',title:123,items:'x'});t.oncomplete=r});db.close()}""")
    before=pg.evaluate(DUMP)
    pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(1000)
    txt=pg.evaluate("(document.getElementById('rkCorruptBanner')||{}).textContent||''")
    ck(txt.startswith('1 record non leggibile') and 'rk_corrotto000000' in txt,'B1 con 1 record illeggibile: avviso con numero e identificativo',txt)
    ck(pg.evaluate("document.querySelectorAll('.rk-card[data-rk]').length")==1,'B2 la classifica valida resta visibile')
    ck(pg.evaluate(DUMP)==before,'B3 il record illeggibile NON e\' stato modificato né cancellato'); c.close()
    # ---- C) layout e componenti ----
    for W,H in ((320,640),(390,844),(412,915),(768,1024)):
        c=newctx(b,W,H); pg=c.new_page(); enter(pg,base); pg.wait_for_timeout(400); seeded=pg.evaluate(SEED,PNG)
        pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(900)
        def ov(): return pg.evaluate("(()=>{const R=document.getElementById('rkRoot');return {sw:R.scrollWidth-R.clientWidth,doc:document.documentElement.scrollWidth-innerWidth,bad:[...R.querySelectorAll('*')].filter(e=>{const b=e.getBoundingClientRect();return b.width>0&&b.right>innerWidth+1&&!e.closest('.rk-tabs')}).slice(0,3).map(e=>e.tagName+'.'+e.className)}})()")
        small="""(()=>{const R=document.getElementById('rkRoot');return [...R.querySelectorAll('button,.rk-in,select,input:not([type=hidden]):not([type=file])')].filter(e=>{const r=e.getBoundingClientRect();const cs=getComputedStyle(e);return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&(r.width<43.5||r.height<43.5)}).slice(0,4).map(e=>(e.getAttribute('aria-label')||e.textContent).slice(0,24)+' '+Math.round(e.getBoundingClientRect().width)+'x'+Math.round(e.getBoundingClientRect().height))})()"""
        o=ov(); ck(o['sw']<=0 and o['doc']<=0 and not o['bad'],'L%d-1 Archivio: nessun overflow orizzontale'%W,o)
        ck(pg.evaluate(small)==[],'L%d-2 Archivio: aree touch >= 44px'%W,pg.evaluate(small))
        ck(pg.evaluate("(()=>{const e=document.getElementById('rkSearch');return parseFloat(getComputedStyle(e).fontSize)>=16})()"),'L%d-3 campo ricerca >= 16px'%W)
        # filtri e comandi compatti: ricerca+nuova su una riga; altezza zona comandi
        hh=pg.evaluate("(()=>{const t=document.querySelector('.rk-tool').getBoundingClientRect(),f=document.querySelector('.rk-filters').getBoundingClientRect();return [Math.round(f.bottom-t.top),Math.round(t.top-document.querySelector('.rk-tabs').getBoundingClientRect().bottom)]})()")
        ck(hh[0]<=112,'L%d-4 comandi Archivio compatti (ricerca+nuova+filtri %dpx)'%(W,hh[0]),hh)
        pg.evaluate("[...document.querySelectorAll('.rk-card-main')].find(x=>x.textContent.includes('dodici elementi')).click()"); pg.wait_for_timeout(900)
        ph=pg.evaluate("Math.round(document.getElementById('rkPodium').getBoundingClientRect().height)")
        lo,hi=(160,192) if W<=350 else (185,215)
        ck(lo<=ph<=hi,'L%d-5 podio compatto: %dpx (atteso %d-%d)'%(W,ph,lo,hi))
        sizes=pg.evaluate("(()=>{const f=s=>Math.round(document.querySelector(s).getBoundingClientRect().width);return [f('.rk-pod.p1 .rk-th'),f('.rk-pod.p2 .rk-th'),f('.rk-pod.p3 .rk-th')]})()")
        ck(sizes[0]>sizes[1]>=sizes[2]-1,'L%d-6 primo posto centrale e piu grande'%W,sizes)
        ck(pg.evaluate("[...document.querySelectorAll('.rk-medal')].map(e=>e.textContent).sort().join('')")=='123' and pg.evaluate("(()=>{const e=document.querySelector('.rk-pod.p1');const m=document.querySelector('.rk-pod.p1 .rk-medal').getBoundingClientRect();return m.width>=24})()"),'L%d-7 medaglie 1-2-3 leggibili'%W)
        o=ov(); ck(o['sw']<=0 and o['doc']<=0 and not o['bad'],'L%d-8 Podio: nessun overflow'%W,o)
        ck(pg.evaluate(small)==[],'L%d-9 Podio: aree touch >= 44px'%W,pg.evaluate(small))
        pg.evaluate("document.getElementById('rkViewList').click()"); pg.wait_for_timeout(600)
        o=ov(); ck(o['sw']<=0 and o['doc']<=0 and not o['bad'],'L%d-10 Elenco Top (12 elementi, titoli lunghi): nessun overflow'%W,o)
        ck(pg.evaluate(small)==[],'L%d-11 Elenco: aree touch >= 44px'%W,pg.evaluate(small))
        pg.evaluate("document.querySelector('.rk-head .rk-ib[aria-label^=Torna]').click()"); pg.wait_for_timeout(500)
        pg.evaluate("[...document.querySelectorAll('.rk-card-main')].find(x=>x.textContent.includes('Tier di prova')).click()"); pg.wait_for_timeout(900)
        ar=pg.evaluate("(()=>{const r=document.querySelector('.rk-tcard').getBoundingClientRect();return Math.round(r.height/r.width*30)/10})()")
        ck(abs(ar-3.3)<=0.15,'L%d-12 scheda Tier proporzione 3:%s (atteso 3:3,3)'%(W,ar))
        n=pg.evaluate("(()=>{const z=document.querySelector('.rk-zone');return getComputedStyle(z).gridTemplateColumns.split(' ').length})()")
        ck(n>=2,'L%d-13 Tier: %d schede per riga (adattivo)'%(W,n))
        o=ov(); ck(o['sw']<=0 and o['doc']<=0 and not o['bad'],'L%d-14 Tier: nessun overflow'%W,o)
        ck(pg.evaluate(small)==[],'L%d-15 Tier: aree touch >= 44px'%W,pg.evaluate(small))
        if W==390:
            # tastiera: sposta tra fasce e nella fascia
            tid=pg.evaluate("document.querySelector('.rk-tcard').getAttribute('data-id')")
            t0=pg.evaluate("(id)=>document.querySelector('[data-id=\"'+id+'\"]').closest('.rk-tier,#rkPool').getAttribute('data-tier-row')||'pool'",tid)
            pg.focus('.rk-tcard'); pg.keyboard.press('ArrowUp'); pg.wait_for_timeout(700)
            t1=pg.evaluate("(id)=>{const e=document.querySelector('[data-id=\"'+id+'\"]');return e&&e.closest('.rk-tier')?e.closest('.rk-tier').getAttribute('data-tier-row'):'pool'}",tid)
            ck(t0!=t1,'K1 tastiera: ↑ sposta la scheda dalla zona «non classificati» all\'ultima fascia',(t0,t1))
            # menu azioni archivio
            pg.evaluate("document.querySelector('.rk-head .rk-ib[aria-label^=Torna]').click()"); pg.wait_for_timeout(500)
            pg.click('.rk-card[data-rk] .rk-more'); pg.wait_for_timeout(300)
            labs=pg.evaluate("[...document.querySelectorAll('.rk-sheet .rk-menu .rk-btn')].map(x=>x.textContent)")
            ck(labs==['Apri','Modifica','Duplica','Elimina'],'K2 menu azioni: Apri, Modifica, Duplica, Elimina',labs)
            pg.keyboard.press('Escape'); pg.evaluate("document.querySelector('.rk-sheet .rk-btn').click()") if False else None
        c.close()
    # ---- D) movimento ridotto ----
    c=newctx(b,390,844,reduced_motion='reduce'); pg=c.new_page(); enter(pg,base); pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(800)
    ck(pg.evaluate("getComputedStyle(document.querySelector('.rk-btn')).transitionDuration")in('0s','0s, 0s'),'M1 prefers-reduced-motion: nessuna transizione'); c.close()
    # ---- E) assenza di rete esterna, nessuna dipendenza CDN ----
    c=newctx(b); pg=c.new_page(); reqs=[]; pg.on('request',lambda r:reqs.append(r.url)); enter(pg,base); pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(1000)
    ext=[u for u in reqs if not u.startswith(base) and not u.startswith('data:') and not u.startswith('blob:') and 'fonts.g' not in u and 'tmdb' not in u and 'gstatic' not in u and 'firebase' not in u.lower() and 'googleapis' not in u]
    ck(not ext,'N1 nessuna nuova dipendenza esterna aperta da Rankings',ext[:3]); c.close()
    b.close()
srv.terminate(); shutil.rmtree(tmp,ignore_errors=True); summary()
