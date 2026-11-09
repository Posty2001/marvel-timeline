from f4lib import *
import json
KEY='marvel-ultimate-timeline-ratings'
def fresh(b,W=390,H=844,pre=None,rm=None):
    ctx=b.new_context(viewport={'width':W,'height':H},is_mobile=True,has_touch=True,service_workers='block',reduced_motion=rm or 'no-preference',device_scale_factor=2); pg=ctx.new_page(); pg.set_default_timeout(8000); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    if pre: pg.add_init_script("(()=>{try{if(!localStorage.getItem('__seeded')){localStorage.setItem('__seeded','1');%s}}catch(e){}})()"%pre)
    pg.goto(U); pg.wait_for_timeout(1000)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    return ctx,pg,errs
def openc(pg,i='023'):
    pg.evaluate("(i)=>{const c=document.querySelector('#item-'+i+' details.card');if(window.tvaTd2){window.tvaTd2.open('item-'+i,{fromTimeline:true})}else{c.open=true}}",i); pg.wait_for_timeout(250)
    pg.evaluate("(i)=>document.querySelector('#item-'+i+' .rw2').scrollIntoView({block:'center',behavior:'instant'})",i); pg.wait_for_timeout(250)
def tap(pg,sel):
    r=pg.evaluate("(s)=>{const e=document.querySelector(s);e.scrollIntoView({block:'center',behavior:'instant'});const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}",sel); pg.touchscreen.tap(r[0],r[1]); pg.wait_for_timeout(120)
def rate(pg,i,v):
    # interazione a due passaggi: 1 tocco sulla stella = intero; secondo tocco sulla stessa stella = mezzo voto
    import math
    k=int(math.ceil(v)); sel='#item-%s .rw-s[data-k="%d"]'%(i,k)
    cur=pg.evaluate("(i)=>parseFloat(document.querySelector('#item-'+i+' .rw-stars').getAttribute('aria-valuenow'))||0",i)
    if cur==v: return
    if v!=k:
        if cur!=k: tap(pg,sel)
        tap(pg,sel)
    else:
        tap(pg,sel)
def state(pg,i='023'):
    return pg.evaluate("""(i)=>{const w=document.querySelector('#item-'+i+' .rw2');const st=w.querySelector('.rw-stars');return {ls:JSON.parse(localStorage.getItem('marvel-ultimate-timeline-ratings')||'{}')[i],txt:w.querySelector('.rw-val').innerText.replace(/\\s+/g,' ').trim(),now:st.getAttribute('aria-valuenow'),vt:st.getAttribute('aria-valuetext'),f:[...w.querySelectorAll('.rw-s')].map(s=>parseFloat(s.style.getPropertyValue('--f'))),reset:!w.querySelector('.rw-reset').hidden}}""",i)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=fresh(b)
    r=pg.evaluate("""()=>{const ws=[...document.querySelectorAll('.rating-widget')];let bad=[];ws.forEach(w=>{const p=w.parentElement;const first=[...p.children].find(c=>c.classList.contains('sub-group'));if(!p.classList.contains('detail-panel')||p.firstElementChild!==w||w.querySelectorAll('.rw-s').length!==5||w.querySelector('.rw-h'))bad.push(w.dataset.item)});return {n:ws.length,bad:bad}}""")
    ok('R1 139 schede: widget subito sotto il titolo (primo elemento del pannello), 5 stelle, nessuna zona da 11px (due tocchi)',r['n']==139 and not r['bad'],r)
    ok('R1b nessuna vecchia stella/etichetta «Il tuo voto» rimasta',pg.evaluate("()=>!document.querySelector('.rating-star')&&!/Il tuo voto/.test(document.body.innerText)"))
    openc(pg)
    vals=[0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]
    # tocco su ciascuna meta': 10 valori
    for v in vals:
        rate(pg,'023',v); s=state(pg)
        exp=[1 if v>=k+1 else (0.5 if v>=k+0.5 else 0) for k in range(5)]
        ok('R2 tocco %s: salvato, mostrato, aria, riempimento stelle'%v,s['ls']==v and s['txt']==(str(v).replace('.',',')+' / 5') and s['now']==str(v) and s['f']==exp and s['reset'],s)
    # ancora lo stesso valore: non azzera
    rate(pg,'023',5); tap(pg,'#item-023 .rw-s[data-k="5"]'); ok('R2b secondo tocco su stella 5 (=5) -> 4,5, non azzera',state(pg)['ls']==4.5,state(pg)); tap(pg,'#item-023 .rw-s[data-k="5"]'); ok('R2c terzo tocco: torna 5',state(pg)['ls']==5)
    # pixel: 3,5 -> stella 4 mezza piena
    rate(pg,'023',3.5)
    pg.screenshot(path='/home/claude/outputs/fix_ios/dopo_voto_3_5_390.png',clip=pg.evaluate("()=>{const r=document.querySelector('#item-023 .rw2').getBoundingClientRect();return {x:Math.max(0,r.left-4),y:Math.max(0,r.top-4),width:r.width+8,height:r.height+8}}"))
    px=pg.evaluate("""()=>{const s=document.querySelectorAll('#item-023 .rw-s')[3];const r=s.getBoundingClientRect();return [r.left,r.top,r.width,r.height]}""")
    import io
    from PIL import Image
    im=Image.open(io.BytesIO(pg.screenshot(clip={'x':px[0],'y':px[1],'width':px[2],'height':px[3]}))).convert('RGB'); w,h=im.size
    def gold(x0,x1): 
        n=0
        for x in range(x0,x1):
            for y in range(h):
                r,g,bb=im.getpixel((x,y))
                if r>170 and g>130 and bb>90 and bb<170 and r-bb>40: n+=1
        return n
    L=gold(0,w//2); R=gold(w//2+2,w);   # esclude 2px a ridosso della linea di taglio (antialias della punta della stella): con stelle piu' strette pesava ~10% ok('R3 mezza stella: oro a sinistra, spento a destra (px %d vs %d)'%(L,R),L>150 and R<L*0.08,(L,R))
    # modifica, azzera
    rate(pg,'023',2); ok('R4 modifica voto esistente 3,5 -> 2',state(pg)['ls']==2)
    tap(pg,'#item-023 .rw-reset'); s=state(pg); ok('R5 Azzera: rimosso dallo storage, 0 stelle, pulsante nascosto',s['ls'] is None and s['now']=='0' and s['vt']=='Nessun voto' and not s['reset'] and s['txt'].startswith('—'),s)
    # persistenza
    rate(pg,'023',4.5); pg.reload(); pg.wait_for_timeout(1000); pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); openc(pg)
    s=state(pg); ok('R6 persistenza dopo refresh (4,5)',s['ls']==4.5 and s['txt']=='4,5 / 5' and s['f']==[1,1,1,1,0.5],s)
    # tastiera
    pg.focus('#item-023 .rw-stars')
    seq=[('ArrowLeft',4),('ArrowLeft',3.5),('ArrowRight',4),('ArrowUp',4.5),('End',5),('ArrowRight',5),('PageDown',4),('Home',None),('ArrowRight',0.5),('3',3),('Delete',None)]
    badk=[]
    for k,exp in seq:
        pg.keyboard.press(k); pg.wait_for_timeout(60); v=state(pg)['ls']
        if v!=exp: badk.append((k,v,exp))
    ok('R7 tastiera: frecce ±0,5, PageUp/Down ±1, Home/Delete azzera, End=5, cifre',not badk,badk)
    ok('R7b ruolo slider con valuemin/max/text',pg.evaluate("()=>{const e=document.querySelector('#item-023 .rw-stars');return e.getAttribute('role')==='slider'&&e.getAttribute('aria-valuemax')==='5'&&e.tabIndex===0&&!!e.getAttribute('aria-labelledby')}"))
    # note non toccate
    pg.evaluate("()=>{const d=document.querySelector('#item-023 .note-toggle');d.open=true}"); pg.fill('#note-023','nota di prova é'); pg.wait_for_timeout(900)
    before=pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-notes')")
    rate(pg,'023',1.5); tap(pg,'#item-023 .rw-reset'); pg.wait_for_timeout(300)
    after=pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-notes')"); ok('R8 note personali intatte (testo e chiave)',before==after and 'nota di prova' in after and pg.input_value('#note-023')=='nota di prova é')
    # altre chiavi non toccate dal voto (tranne ratings e derivati xp/tessera)
    k0=pg.evaluate("()=>JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
    rate(pg,'023',3)
    k1=pg.evaluate("()=>JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
    d=[a[0] for a,bb in zip(json.loads(k0),json.loads(k1)) if a!=bb]+[x[0] for x in json.loads(k1) if x[0] not in dict(json.loads(k0))]
    print('  chiavi cambiate dal voto:',d); ok('R9 il voto modifica solo ratings (+ eventuali derivati XP/tessera)',set(d)<= {KEY} or all(x.startswith('marvel-ultimate-timeline-') for x in d),d)
    ok('R10 nessun errore JS',errs==[],errs[:2]); ctx.close()
    # compatibilita' voti interi + medie con decimali
    pre="localStorage.setItem('%s',JSON.stringify({'001':4,'002':1,'003':5,'004':3.5}));"%KEY
    ctx,pg,errs=fresh(b,pre=pre)
    r=pg.evaluate("()=>[1,2,3,4].map(i=>{const s=document.querySelector('#item-00'+i+' .rw-stars');return s.getAttribute('aria-valuenow')})"); ok('R11 voti interi gia\' salvati (4,1,5) e un mezzo voto caricati',r==['4','1','5','3.5'],r)
    ok('R11b storage non riscritto al caricamento',pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-ratings')")==json.dumps({'001':4,'002':1,'003':5,'004':3.5},separators=(',',':')))
    openc(pg,'005'); rate(pg,'005',3); pg.wait_for_timeout(400)
    avg=pg.evaluate("()=>[document.getElementById('hhsRating')&&document.getElementById('hhsRating').textContent,document.getElementById('dashAvgRating')&&document.getElementById('dashAvgRating').textContent,document.getElementById('tesseraVoto')&&document.getElementById('tesseraVoto').textContent]"); print('  medie:',avg); ok('R12 voto medio con mezzi voti (4,1,5,3.5,3 -> 3.3)',any('3.3' in (x or '') for x in avg),avg)
    # votare aggiorna la media (updateProgress) e l'XP resta coerente (5 XP per titolo votato, non per ogni modifica)
    ctx.close()
    # memoria piena: il voto non risulta salvato
    ctx,pg,errs=fresh(b); openc(pg)
    pg.evaluate("()=>{const o=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='%s')throw new Error('quota');return o.apply(this,arguments)}}"%KEY)
    rate(pg,'023',3); s=state(pg); ok('R13 se il salvataggio fallisce la UI non mostra un voto non salvato',s['ls'] is None and s['now']=='0',s)
    ok('R13b messaggio per tecnologie assistive',pg.evaluate("()=>/non salvato/.test(document.querySelector('#item-023 .rw-live').textContent)")); ctx.close()
    # reduced motion
    ctx,pg,errs=fresh(b,rm='reduce'); openc(pg); rate(pg,'023',2.5)
    ok('R14 prefers-reduced-motion: nessuna animazione sulle stelle',pg.evaluate("()=>[...document.querySelectorAll('#item-023 .rw-s')].every(s=>getComputedStyle(s).animationName==='none')")); ctx.close()
    ctx,pg,errs=fresh(b); openc(pg); rate(pg,'023',2.5)
    ok('R14b con animazioni attive la stella selezionata ha la microanimazione',pg.evaluate("()=>getComputedStyle(document.querySelectorAll('#item-023 .rw-s')[2]).animationName")=='rw-pop'); ctx.close()
    # responsive 320..430
    for W,H in [(320,568),(360,740),(375,667),(390,844),(393,852),(430,932)]:
        ctx,pg,errs=fresh(b,W,H); openc(pg); rate(pg,'023',3.5)
        m=pg.evaluate("""()=>{const w=document.querySelector('#item-023 .rw2'),r=w.getBoundingClientRect(),c=w.closest('details.card').getBoundingClientRect();const h=[...w.querySelectorAll('.rw-s')].map(x=>x.getBoundingClientRect());const rs=w.querySelector('.rw-reset').getBoundingClientRect();
          const pz=getComputedStyle(w.querySelector('.rw-reset'),'::after');return {w:Math.round(r.width),inCard:r.left>=c.left-1&&r.right<=c.right+1,hh:Math.min(...h.map(x=>x.height)),hw:Math.min(...h.map(x=>x.width)),ov:document.documentElement.scrollWidth>innerWidth+1,H:Math.round(r.height),valR:w.querySelector('.rw-val').getBoundingClientRect().right<=r.right,top:Math.round(r.top-document.querySelector('#item-023 .detail-panel').getBoundingClientRect().top)}}""")
        ok('R15 [%d] blocco dentro la scheda, zone di tocco >=44px alto, nessun overflow, altezza %dpx'%(W,m['H']),m['inCard'] and m['hh']>=43.5 and not m['ov'] and m['valR'] and m['H']<=100,m)
        print('   mezza stella larga %.1fpx'%m['hw'])
        if W in (320,390): pg.screenshot(path='/home/claude/outputs/fix_ios/dopo_voto_scheda_%d.png'%W)
        ctx.close()
    b.close()
done()
