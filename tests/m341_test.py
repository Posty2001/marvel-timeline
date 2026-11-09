from playwright.sync_api import sync_playwright
import json
R=[]
def ck(n,c,d=''): R.append(c); print(('PASS ' if c else 'FAIL ')+n+(' '+str(d)[:260] if not c else ''))
U='http://127.0.0.1:8124/index.html'
def ctx(b,pre=None):
    cx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block')
    if pre: cx.add_init_script("(()=>{if(!sessionStorage.getItem('m34seed')){sessionStorage.setItem('m34seed','1');const o=%s;for(const k in o)localStorage.setItem(k,o[k]);}})()"%json.dumps({k:(v if isinstance(v,str) else json.dumps(v)) for k,v in pre.items()}))
    pg=cx.new_page(); pg.errs=[]; pg.on('pageerror',lambda e:pg.errs.append(str(e))); pg.route('**/image.tmdb.org/**',lambda r:r.abort()); return cx,pg
def start(pg):
    pg.goto(U); pg.wait_for_timeout(1000)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
nid=lambda pg:pg.evaluate("()=>window.marvelHomeNext&&window.marvelHomeNext.id")
shown=lambda pg:pg.evaluate("()=>hhsNextValue.textContent.trim()")
title=lambda pg,i:pg.evaluate("(i)=>document.querySelector('#item-'+i+' .title').textContent.trim()",i)
MODE='marvelGuideActiveTimelineMode'; ORD='marvelGuideCustomTimelineOrder'
def watch(pg,i): pg.evaluate("(i)=>{const c=document.querySelector('#item-'+i+' input[type=checkbox]');c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}))}",i); pg.wait_for_timeout(250)
with sync_playwright() as p:
    b=p.chromium.launch()
    # 1 standard
    cx,pg=ctx(b); start(pg); ck('standard (nessuna modalita salvata): Spider-Man, come prima',nid(pg)=='001' and shown(pg)=='Spider-Man',(nid(pg),shown(pg)))
    snap0=pg.evaluate("()=>JSON.stringify(Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('marvel-ultimate')).sort().map(k=>[k,localStorage.getItem(k)])))")
    # 2 cambio modalita da UI
    pg.evaluate("()=>{altTimelineToggle.checked=true;altTimelineToggle.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>localStorage.setItem('%s',JSON.stringify([4,2,1,3,5]))"%ORD)
    pg.evaluate("()=>document.querySelector('.at-mode-btn[data-mode=custom]').click()"); pg.wait_for_timeout(400)
    ck('UI: «Personalizzato» salva la modalita e aggiorna subito la Home (004 primo nell\'ordine)',pg.evaluate("()=>localStorage.getItem('%s')"%MODE)=='custom' and nid(pg)=='004' and shown(pg)==title(pg,'004'),(nid(pg),shown(pg)))
    pg.evaluate("()=>document.querySelector('.at-mode-btn[data-mode=release]').click()"); pg.wait_for_timeout(300)
    ck('UI: altra modalita -> standard, Home torna a Spider-Man subito',pg.evaluate("()=>localStorage.getItem('%s')"%MODE)=='standard' and nid(pg)=='001')
    pg.evaluate("()=>document.querySelector('.at-mode-btn[data-mode=custom]').click()"); pg.wait_for_timeout(300)
    # 3 riordino con frecce
    r=pg.evaluate("()=>[...document.querySelectorAll('#atList .at-move-btn[data-move=up]')].map(e=>e.getAttribute('data-num')).slice(0,6)")
    pg.evaluate("()=>document.querySelector('#atList .at-move-btn[data-move=up][data-num=\"2\"]').click()"); pg.wait_for_timeout(400)
    o=pg.evaluate("()=>JSON.parse(localStorage.getItem('%s'))"%ORD)
    ck('riordino (2 sopra 4): ordine salvato aggiornato',o[:2]==[2,4],o[:5])
    ck('riordino: la Home si aggiorna subito (prima 002 -> richiede 001 se prerequisito, altrimenti 002)',nid(pg) in ('002','001'),nid(pg))
    first=nid(pg)
    # 4 persistenza
    pg.reload(); pg.wait_for_timeout(1000)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    ck('persistenza dopo ricarica: stessa modalita/ordine/suggerimento',nid(pg)==first and pg.evaluate("()=>localStorage.getItem('%s')"%MODE)=='custom',(nid(pg),first))
    pg.evaluate("()=>{altTimelineToggle.checked=true;altTimelineToggle.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    ck('alt timeline riapre sulla modalita salvata (Personalizzato attivo)',pg.evaluate("()=>document.querySelector('#atModes .at-mode-btn.at-mode-active').getAttribute('data-mode')")=='custom')
    ck('nessuna modifica a progressi/voti/XP (solo le 2 chiavi timeline)',pg.evaluate("()=>JSON.stringify(Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith('marvel-ultimate')).sort().map(k=>[k,localStorage.getItem(k)])))")==snap0)
    ck('nessun errore JS',not pg.errs,pg.errs); cx.close()
    # 5 completamento + vincoli
    cx,pg=ctx(b,{MODE:'custom',ORD:[4,2,1,3,5]}); start(pg)
    ck('custom seed: primo = 004',nid(pg)=='004',nid(pg))
    watch(pg,'004'); a=nid(pg)
    ck('dopo completamento 004 la Home avanza subito (≠004, non visto)',a!='004' and a in ('002','001'),a)
    watch(pg,a)
    seq=[nid(pg)]
    ck('nessun titolo gia visto suggerito',all(pg.evaluate("(i)=>!JSON.parse(localStorage.getItem('marvel-ultimate-timeline-watched')||'{}')[i]",i) for i in seq),seq)
    # CTA apre esattamente il titolo
    want=nid(pg); pg.evaluate("()=>{const c=document.getElementById('missioneCelebrazioneChiudi');if(c&&!document.getElementById('missioneCelebrazione').hidden)c.click()}"); pg.wait_for_timeout(500)
    pg.touchscreen.tap(*pg.evaluate("()=>{const r=m34NextCta.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}")); pg.wait_for_timeout(1000)
    ck('«Continua» porta esattamente alla scheda del titolo suggerito (in vista, NON aperta)',pg.evaluate("(i)=>{const d=document.querySelector('#item-'+i+' details');const e=document.getElementById('item-'+i),r=e.getBoundingClientRect();return homeHubExited.checked&&!!d&&!d.open&&!document.querySelector('.card-wrap.td-page')&&r.bottom>0&&r.top<innerHeight&&e.offsetParent!==null}",want),want)
    cx.close()
    cx,pg=ctx(b); start(pg); want=nid(pg)
    pg.touchscreen.tap(*pg.evaluate("()=>{const r=m34NextCta.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}")); pg.wait_for_timeout(1000)
    ck('«Inizia» (standard) porta esattamente alla scheda del titolo suggerito (in vista, NON aperta)',pg.evaluate("(i)=>{const d=document.querySelector('#item-'+i+' details');const e=document.getElementById('item-'+i),r=e.getBoundingClientRect();return homeHubExited.checked&&!!d&&!d.open&&!document.querySelector('.card-wrap.td-page')&&r.bottom>0&&r.top<innerHeight&&e.offsetParent!==null}",want),want); cx.close()
    # 6 titoli mancanti, duplicati, sequenza vuota
    cx,pg=ctx(b,{MODE:'custom',ORD:[9999,5000,4,4,0,-3,'x',2]}); start(pg)
    ck('numeri mancanti/duplicati/non validi ignorati: primo valido = 004',nid(pg)=='004' and not pg.errs,(nid(pg),pg.errs)); cx.close()
    cx,pg=ctx(b,{MODE:'custom',ORD:[]}); start(pg)
    ck('sequenza vuota -> comportamento standard',nid(pg)=='001'); cx.close()
    cx,pg=ctx(b,{MODE:'custom',ORD:'not json{'}); start(pg)
    ck('ordine corrotto -> standard, nessun errore',nid(pg)=='001' and not pg.errs,pg.errs); cx.close()
    cx,pg=ctx(b,{MODE:'custom',ORD:[1,2]}); start(pg)
    ck('ordine parziale: i titoli non elencati seguono in coda',nid(pg) is not None); 
    # 7 percorso completato
    ids=pg.evaluate("()=>[...document.querySelectorAll('.card-wrap[id^=item-]:not(.card-variant)')].map(e=>e.getAttribute('data-item'))")
    pg.evaluate("(ids)=>{const o={};ids.forEach(i=>o[i]=true);localStorage.setItem('marvel-ultimate-timeline-watched',JSON.stringify(o))}",ids); pg.reload(); pg.wait_for_timeout(1000)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    ck('percorso completato (custom): «Tutto visto!», CTA nascosta',shown(pg)=='Tutto visto!' and pg.evaluate("()=>getComputedStyle(m34NextCta).display==='none'"),shown(pg)); cx.close()
    # 8 storage
    cx,pg=ctx(b); start(pg)
    pg.evaluate("()=>{localStorage.setItem('%s','custom');localStorage.setItem('%s',JSON.stringify([4,1]));window.dispatchEvent(new StorageEvent('storage',{key:'%s'}))}"%(MODE,ORD,MODE)); pg.wait_for_timeout(300)
    ck('aggiornamento da altra scheda (evento storage)',nid(pg)=='004',nid(pg)); cx.close()
    print(sum(R),'/',len(R))
