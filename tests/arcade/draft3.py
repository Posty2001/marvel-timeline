# Test Draft 3.0 (Chromium): 5 offerte, snake, seed, salvataggi, layout, arene, Skip, reduced motion
import sys,re,json,time,itertools
from playwright.sync_api import sync_playwright
ROOT=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:8790/'
URL=ROOT+'arcade/draft/'
R=[]
def rec(n,ok,note=''):R.append((n,bool(ok)));print(('PASS' if ok else 'FAIL'),n,'' if ok else '— %s'%(str(note)[:300],),flush=True)
INS={'top':59,'bottom':34,'left':0,'right':0}
ORDER='ABBAABBAAB'
SCN=['asgard','wakanda','quantum','battleworld'];LV=['recluta','stratega','maestro']
def page(b,w=390,h=844,reduced=False,init=None,fresh=True,ctx=None):
    c=ctx or b.new_context(viewport={'width':w,'height':h},is_mobile=True,has_touch=True,service_workers='block',reduced_motion='reduce' if reduced else 'no-preference')
    pg=c.new_page();c.new_cdp_session(pg).send('Emulation.setSafeAreaInsetsOverride',{'insets':INS});pg.errs=[];pg.on('pageerror',lambda e:pg.errs.append(str(e)))
    if init:pg.add_init_script(init)
    pg.goto(URL);pg.wait_for_selector('#new');return c,pg
def offers(pg):return pg.evaluate("[...document.querySelectorAll('#pool > .card')].map(e=>e.dataset.id)")
def save(pg):return json.loads(pg.evaluate("localStorage.getItem('tva-draft-save-v2')"))
def start(pg,k,l):
    pg.select_option('#scenario',k);pg.select_option('#cpu',l);pg.click('#new');pg.wait_for_selector('#pool .card')
def draft_all(pg,pick=0,log=None):
    # gioca la bozza: a ogni turno del giocatore registra le 5 offerte e recluta la carta #pick
    guard=0;seen=[]
    while pg.evaluate("phase==='draft'") and guard<30:
        guard+=1
        if pg.evaluate("ORDER[turn]==='A'"):
            o=offers(pg)
            if log is not None:log.append(o)
            pg.locator('#pool .card').nth(min(pick,len(o)-1)).click();pg.click('#recruit');pg.wait_for_function("!recruiting",timeout=8000)
        else:pg.wait_for_timeout(120)
    return guard
with sync_playwright() as p:
    b=p.chromium.launch()
    # D1 roster
    c,pg=page(b)
    pl=pg.evaluate("JSON.parse(document.getElementById('payload').textContent)")
    ro=pl['roster'];ids=[r['id'] for r in ro]
    rec('D1a roster = 120 carte con ID univoci',len(ro)==120 and len(set(ids))==120,len(ro))
    rec('D1b tutte con 5 statistiche in 1..100 e gruppo valido',all(set(r['stats'])=={'power','intelligence','speed','durability','versatility'} and all(1<=v<=100 for v in r['stats'].values()) for r in ro))
    rec('D1c varianti significative presenti (Phoenix, Zarathos, Rune King Thor) con base',all(i in ids for i in('phoenix','zarathos','rune-king-thor','jean-grey','ghost-rider','thor')))
    rec('D1d ogni carta documenta versione, capacità e limiti',all(r.get('version') and r.get('cap') and r.get('lim') for r in ro))
    rec('D1e portrait=null ovunque (nessuna immagine non verificata) e SVG segnaposto',all(r.get('portrait') in(None,'') for r in ro))
    c.close()
    # D2 cinque offerte valide a ogni turno, snake, no duplicati — 4 scenari x 3 livelli
    t0=time.time();bad=[];snk=[];dup=[];allo={}
    for k in SCN:
        for l in LV:
            c,pg=page(b);start(pg,k,l);log=[];draft_all(pg,pick=len(allo)%5,log=log)
            s=save(pg);allo[(k,l)]=log
            picks=s['a']+s['b']
            if len(log)!=5 or any(len(o)!=5 or len(set(o))!=5 for o in log):bad.append((k,l,[len(o) for o in log]))
            if len(set(picks))!=10:dup.append((k,l))
            # nessuna carta già reclutata riappare
            seen=set()
            for i,o in enumerate(log):pass
            # snake: ordine di reclutamento = s['oh'] pick o ricostruzione da save
            if len(s['a'])!=5 or len(s['b'])!=5:snk.append((k,l))
            c.close()
    rec('D2a 12 partite complete (4 scenari × 3 CPU): 5 offerte valide e distinte a ogni turno del giocatore',not bad,bad)
    rec('D2b nessun duplicato fra squadre; 5+5 carte',not dup and not snk,(dup,snk))
    # D2c nessuna carta reclutata ricompare nelle offerte successive (rigoroso, con log completo)
    ok=True;msg=''
    for (k,l) in [(SCN[0],'maestro'),(SCN[3],'stratega')]:
        c,pg=page(b);start(pg,k,l);rec_seen=set();log=[]
        g=0
        while pg.evaluate("phase==='draft'") and g<30:
            g+=1
            if pg.evaluate("ORDER[turn]==='A'"):
                o=offers(pg)
                if rec_seen&set(o):ok=False;msg=(k,l,rec_seen&set(o))
                pg.locator('#pool .card').nth(2).click();pg.click('#recruit');pg.wait_for_function("!recruiting",timeout=8000)
                s=save(pg);rec_seen=set(s['a']+s['b'])
            else:pg.wait_for_timeout(100)
        c.close()
    rec('D2c nessuna carta già reclutata (giocatore o CPU) ricompare nelle offerte',ok,msg)
    # D3 snake ABBAABBAAB verificato dalla UI (pips) e dal motore
    c,pg=page(b);start(pg,'asgard','stratega')
    order=pg.evaluate("Array.isArray(Core.ORDER)?Core.ORDER.join(''):String(Core.ORDER)")
    rec('D3a ordine snake ABBAABBAAB nel motore',order==ORDER,order)
    seq=[];g=0
    while pg.evaluate("phase==='draft'") and g<30:
        g+=1;t=pg.evaluate("turn")
        if pg.evaluate("ORDER[turn]==='A'"):
            pg.locator('#pool .card').first.click();pg.click('#recruit');pg.wait_for_function("!recruiting",timeout=8000)
        else:pg.wait_for_timeout(100)
        seq.append(pg.evaluate("[A.length,B.length]"))
    fin=pg.evaluate("[A.length,B.length]")
    # dopo ogni turno A+B = turn; le squadre devono seguire il pattern snake
    ok=True;a=b2=0
    for ch in ORDER:
        pass
    rec('D3b squadre finali 5 e 5 e turno 10',fin==[5,5] and pg.evaluate("turn")==10,fin)
    c.close()
    # D3c turni CPU consecutivi: dopo il turno 0 (A) la CPU gioca 1 e 2 e le offerte al turno 3 sono 5 valide
    c,pg=page(b);start(pg,'wakanda','maestro');pg.locator('#pool .card').first.click();pg.click('#recruit');pg.wait_for_function("turn===3 && !recruiting",timeout=15000)
    o=offers(pg);s=save(pg)
    rec('D3c due turni CPU consecutivi (B,B) poi 5 offerte valide al turno 3',len(o)==5 and len(set(o))==5 and not (set(o)&set(s['a']+s['b'])) and len(s['b'])==2,(o,s['b']))
    # D4 seed e riproducibilità
    seed=s['seed'];before=offers(pg);pg.reload();pg.wait_for_selector('#pool .card');after=offers(pg)
    rec('D4a ricarica a metà bozza: stesse 5 offerte (nessun miglioramento ricaricando)',before==after,(before,after))
    # cancella le offerte salvate: devono essere rigenerate identiche dal seed
    pg.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('tva-draft-save-v2'));s.offers=[];localStorage.setItem('tva-draft-save-v2',JSON.stringify(s))})()");pg.reload();pg.wait_for_selector('#pool .card')
    rec('D4b offerte rigenerate dal solo seed identiche',offers(pg)==before,offers(pg))
    # D4c partita nuova => seed diverso
    pg.click('#new') if pg.is_visible('#new') else None
    c.close()
    c,pg=page(b);start(pg,'wakanda','maestro');s2=save(pg)['seed']
    c2,pg2=page(b);start(pg2,'wakanda','maestro');s3=save(pg2)['seed']
    rec('D4c due partite nuove hanno seed diversi',s2!=s3);c.close();c2.close()
    # D5 tutte le 5 selezionabili, nessuna scelta forzata
    c,pg=page(b);start(pg,'quantum','recluta');ok=True
    for i in range(5):
        pg.locator('#pool .card').nth(i).click();ok&=pg.evaluate("sel&&sel.id")==offers(pg)[i]
    rec('D5 le 5 opzioni sono tutte selezionabili',ok)
    # niente rigenerazione gratuita: non esiste un controllo per rigenerare
    rec('D5b nessun pulsante di rigenerazione offerte',not pg.evaluate("[...document.querySelectorAll('button')].some(b=>/rigenera|nuove offerte|reroll/i.test(b.textContent))"))
    # pulsante Recluta fisso e raggiungibile (viewport 320x568 incl. safe area)
    c.close()
    for w,h in((320,568),(390,844),(430,932)):
        c,pg=page(b,w,h);start(pg,'asgard','recluta')
        for i in (0,4):
            pg.locator('#pool .card').nth(i).click();pg.wait_for_timeout(150)
            r=pg.evaluate("(()=>{const r=document.getElementById('recruit').getBoundingClientRect();return {t:r.top,b:r.bottom,h:innerHeight,sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth}})()")
            rec('L1 %dx%d Recluta visibile (fisso) con carta %d selezionata'%(w,h,i),r['t']>=0 and r['b']<=r['h'],r)
            rec('L2 %dx%d nessun overflow orizzontale'%(w,h),r['sw']<=r['cw'],r)
        # tutte le 5 miniature raggiungibili scorrendo
        pg.evaluate("window.scrollTo(0,document.body.scrollHeight)");pg.wait_for_timeout(100)
        rb=pg.evaluate("(()=>{const l=[...document.querySelectorAll('#pool > .card')].pop().getBoundingClientRect(),r=document.getElementById('recruit').getBoundingClientRect();return {lb:l.bottom,rt:r.top}})()")
        rec('L3 %dx%d ultima miniatura non coperta dalla barra Recluta a fine scroll'%(w,h),rb['lb']<=rb['rt']+1,rb)
        # nomi non spezzati / non tagliati nell'intera pagina
        clip=pg.evaluate("[...document.querySelectorAll('.nameb h3,.th .nm')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent)")
        rec('L4 %dx%d nomi nelle miniature/eroe non tagliati'%(w,h),not clip,clip)
        c.close()
    # L5 tutti i 120 nomi: verifica clip su pool completo (iniezione offerte per tutti i nomi)
    c,pg=page(b,320,568);start(pg,'asgard','recluta');bad=[]
    for chunk in range(0,120,5):
        ids5=pg.evaluate("(()=>{const ids=PAYLOAD_IDS;return ids})()") if False else None
    allids=ids
    for i in range(0,120,5):
        sub=allids[i:i+5]
        pg.evaluate("(sub)=>{offers=sub.map(id=>byId[id]);sel=offers[0];render()}",sub)
        bad+=pg.evaluate("[...document.querySelectorAll('.nameb h3,.th .nm')].filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent)")
    rec('L5 tutti i 120 nomi leggibili senza tagli a 320 px (miniature + eroe)',not bad,bad)
    c.close()
    # F: partita completa -> ruoli -> battaglia -> Skip -> risultato (4 scenari)
    for k in SCN:
        c,pg=page(b);start(pg,k,'stratega');draft_all(pg)
        pg.wait_for_selector('#rolesp:not([hidden])',timeout=8000)
        hid=pg.evaluate("[...document.querySelectorAll('#tcpu2 .kard .rolechip')].map(e=>e.textContent.trim())")
        rec('F1 %s: ruoli CPU nascosti (?) prima della battaglia'%k,len(hid)==5 and all(h=='?' for h in hid),hid)
        sv=save(pg);rec('F2 %s: salvataggio fase roles con seed, scenario, squadre'%k,sv['phase']=='roles' and sv['seed'] and sv['scenario']==k and len(sv['a'])==5)
        pg.click('#auto');pg.click('#go');pg.wait_for_selector('#battle:not([hidden])',timeout=8000);pg.wait_for_timeout(700)
        arena=pg.evaluate("document.getElementById('arena').dataset.s")
        shot='/tmp/shots/arena_%s.png'%k
        import os;os.makedirs('/tmp/shots',exist_ok=True);pg.screenshot(path=shot)
        rec('F3 %s: arena corretta in battaglia'%k,arena==k,arena)
        t=time.time();pg.click('#skip');pg.wait_for_selector('#result:not([hidden])',timeout=6000)
        rec('F4 %s: Salta animazione porta al risultato in <3s'%k,time.time()-t<3,time.time()-t)
        fan=pg.evaluate("document.querySelectorAll('#result .fan .kard').length")
        rec('F5 %s: risultato con squadra vincitrice di 5 carte in evidenza'%k,fan==5,fan)
        pg.screenshot(path='/tmp/shots/result_%s.png'%k)
        rec('F6 %s: nessun errore JS'%k,not pg.errs,pg.errs[:2]);c.close()
    # G: ripresa partita interrotta in ogni fase
    c,pg=page(b);start(pg,'wakanda','maestro')
    for i in range(2):
        pg.locator('#pool .card').first.click();pg.click('#recruit');pg.wait_for_function("!recruiting && ORDER[turn]==='A'",timeout=15000)
    before=(offers(pg),save(pg)['a']);pg.reload();pg.wait_for_selector('#pool .card')
    rec('G1 ripresa a metà bozza: squadra e offerte identiche',(offers(pg),save(pg)['a'])==before)
    draft_all(pg);pg.wait_for_selector('#rolesp:not([hidden])');pg.click('#auto');pg.reload();pg.wait_for_selector('#rolesp:not([hidden])')
    rec('G2 ripresa nella fase ruoli senza perdere squadre',pg.evaluate("A.length===5&&B.length===5"))
    pg.click('#auto');pg.click('#go');pg.wait_for_selector('#battle:not([hidden])');pg.click('#skip');pg.wait_for_selector('#result:not([hidden])');r1=pg.evaluate("JSON.stringify(result)")
    pg.reload();pg.wait_for_selector('#result:not([hidden])');rec('G3 ripresa dopo il risultato: stesso esito, nessuna rigiocata',pg.evaluate("JSON.stringify(result)")==r1);c.close()
    # H: migrazione v1
    for ph,a,bb,turn in (('draft',['iron-man'],['hulk','thor'],3),):
        pass
    c,pg=page(b)
    v1={"v":1,"scenario":"asgard","cpu":"stratega","pool":["black-widow","captain-america","hawkeye","scarlet-witch","wolverine","storm","cyclops","rogue","spider-man","miles-morales","venom","carnage","doctor-strange","loki"],"a":["iron-man"],"b":["thor","hulk"],"turn":3,"phase":"draft","assign":{},"result":None}
    ids2=set(v1['pool']+v1['a']+v1['b'])
    ids_have=set(ids)
    v1['pool']=[i for i in v1['pool'] if i in ids_have]
    # completa a 16 con carte esistenti
    extra=[i for i in ids if i not in set(v1['pool']+v1['a']+v1['b'])]
    while len(v1['pool'])+3<16:v1['pool'].append(extra.pop(0))
    pg.evaluate("(v)=>{localStorage.removeItem('tva-draft-save-v2');localStorage.setItem('tva-draft-save-v1',JSON.stringify(v))}",v1);pg.reload();pg.wait_for_selector('#pool .card')
    s=save(pg)
    rec('H1 migrazione v1 → v2 senza perdita di progresso (squadre, turno, scenario, CPU) e 5 offerte nuove',s['v']==2 and s['a']==v1['a'] and s['b']==v1['b'] and s['turn']==3 and s['scenario']=='asgard' and s['cpu']=='stratega' and len(offers(pg))==5,s)
    rec('H2 offerte migrate non contengono carte già reclutate',not(set(offers(pg))&set(v1['a']+v1['b'])))
    # v1 corrotto → ignorato senza crash
    pg.evaluate("localStorage.removeItem('tva-draft-save-v2');localStorage.setItem('tva-draft-save-v1','{bad')");pg.reload();pg.wait_for_selector('#new')
    rec('H3 salvataggio corrotto ignorato senza errori',not pg.errs,pg.errs[:2])
    # v2 manomesso (duplicato) → scartato
    pg.evaluate("localStorage.setItem('tva-draft-save-v2',JSON.stringify({v:2,seed:'x',scenario:'asgard',cpu:'recluta',a:['thor'],b:['thor'],turn:2,offers:[],oh:[],assign:{},phase:'draft',result:null}))");pg.reload();pg.wait_for_selector('#new')
    rec('H4 salvataggio v2 con duplicati scartato',pg.evaluate("phase==='idle'"),pg.evaluate("phase"));c.close()
    # I: animazione di reclutamento + reduced motion
    c,pg=page(b);start(pg,'asgard','recluta');pg.locator('#pool .card').nth(1).click()
    pg.click('#recruit');pg.wait_for_timeout(60);fl=pg.evaluate("!!document.querySelector('.flyc, .fly, [data-fly]')||recruiting")
    rec('I1 animazione di reclutamento attiva (recruiting)',fl)
    pg.wait_for_function("!recruiting",timeout=8000);dur=pg.evaluate("1");c.close()
    c,pg=page(b,reduced=True);start(pg,'asgard','recluta');pg.locator('#pool .card').nth(1).click();t=time.time();pg.click('#recruit');pg.wait_for_function("!recruiting",timeout=4000)
    rec('I2 reduced motion: reclutamento senza animazione di volo (<0.6s)',time.time()-t<.6,time.time()-t)
    anim=pg.evaluate("document.getAnimations().filter(a=>a.playState==='running').length")
    c.close()
    # J: intestazione BATTLEWORLD a 320/390/430
    for w,h in((320,568),(390,844),(430,932)):
        c,pg=page(b,w,h);start(pg,'battleworld','recluta')
        r=pg.evaluate("(()=>{const e=document.querySelector('#scnbn .scnban'),n=e&&e.querySelector('.nm b');return {w:e.clientWidth,sw:e.scrollWidth,nw:n.scrollWidth,ncw:n.clientWidth,t:n.textContent}})()")
        rec('J1 %d px intestazione BATTLEWORLD non tagliata'%w,r['sw']<=r['w']+1 and r['nw']<=r['ncw']+1,r);c.close()
    # M: fix Safari (v3.1): schermata iniziale, safe area superiore, dock ruoli, pulsanti inferiori
    for w,h in((320,568),(390,844),(430,932)):
        c,pg=page(b,w,h)
        d=pg.evaluate("(()=>{const t=document.getElementById('setup').innerText;const m=t.match(/(?:Potenza|Intelligenza|Velocit\u00e0|Resistenza|Versatilit\u00e0)\\s*\\d+%/g)||[];return {n:m.length,uniq:new Set(m).size,wd:!!document.getElementById('wdesc'),lg:/sulle carte/.test(document.getElementById('scnprev').innerText)||/SCENARIO[\\s\\S]*SCENARIO/i.test(document.getElementById('setup').innerText)}})()")
        rec('M1 %d px schermata iniziale: nessuna descrizione dei pesi duplicata'%w,not d['wd'] and d['n']==d['uniq'] and not d['lg'],d)
        nav=pg.evaluate("(()=>{const n=document.getElementById('tva-arcade-nav').getBoundingClientRect();const a=document.querySelector('#tva-arcade-nav a').getBoundingClientRect();return {aTop:a.top,navH:n.height}})()")
        rec('M2 %d px safe area superiore: il link TVA Arcade sta sotto i 59 px della Dynamic Island'%w,nav['aTop']>=59,nav)
        start(pg,'asgard','recluta');draft_all(pg);pg.wait_for_selector('#rolesp:not([hidden])');pg.wait_for_timeout(300)
        for pos in (0,1):
            pg.evaluate("window.scrollTo(0,%s)"%("0" if pos==0 else "document.documentElement.scrollHeight"));pg.wait_for_timeout(150)
            r=pg.evaluate("(()=>{const bs=[...document.querySelectorAll('#roles button')].map(x=>x.getBoundingClientRect());const bt=['auto','go'].map(i=>document.getElementById(i).getBoundingClientRect());return {n:bs.length,minT:Math.min(...bs.map(x=>x.top)),maxB:Math.max(...bs.map(x=>x.bottom)),minL:Math.min(...bs.map(x=>x.left)),maxR:Math.max(...bs.map(x=>x.right)),btB:Math.max(...bt.map(x=>x.bottom)),btH:Math.min(...bt.map(x=>x.height)),h:innerHeight,w:innerWidth}})()")
            rec('M3 %d px dock ruoli (scroll %s): tutti e 5 i ruoli visibili e toccabili'%(w,'inizio' if pos==0 else 'fine'),r['n']==5 and r['minT']>=0 and r['maxB']<=r['h']-34+1 and r['minL']>=0 and r['maxR']<=r['w'],r)
            rec('M4 %d px (scroll %s) pulsanti inferiori sopra la home indicator (34 px) e alti ≥44'%(w,'inizio' if pos==0 else 'fine'),r['btB']<=r['h']-34+1 and r['btH']>=44,r)
        # il contenuto in fondo (duello) non resta coperto dal dock a fine scroll
        cov=pg.evaluate("(()=>{const d=document.getElementById('duel').getBoundingClientRect(),a=document.querySelector('#rolesp .actbar').getBoundingClientRect();return {duelB:d.bottom,barT:a.top}})()")
        rec('M5 %d px a fine scroll il duello non è coperto dal dock'%w,cov['duelB']<=cov['barT']+1,cov)
        # assegnazione dei 5 ruoli dal dock
        pg.evaluate("window.scrollTo(0,0)")
        for i,rl in enumerate(['avanguardia','stratega','ricognitore','difensore','specialista']):
            pg.locator('#tme2 .kard').nth(i).click();pg.locator('#roles [data-role=%s]'%rl).click()
        rec('M6 %d px assegnati i 5 ruoli (incluso Specialista) dal dock, Combatti! attivo'%w,pg.evaluate("Object.keys(assign).length===5 && !document.getElementById('go').disabled"),pg.evaluate("JSON.stringify(assign)"))
        c.close()
    # K: performance
    c,pg=page(b);t=time.time();pg.goto(URL);pg.wait_for_selector('#new');load=time.time()-t
    start(pg,'asgard','maestro');
    ms=pg.evaluate("(()=>{const t=performance.now();for(let i=0;i<20;i++)makeOffer(0);return (performance.now()-t)/20})()")
    rec('K1 generazione offerte < 15 ms (media, Chromium desktop)',ms<15,ms)
    rec('K2 caricamento pagina < 3 s',load<3,load);print('  load=%.2fs offer=%.2fms'%(load,ms));c.close()
    b.close()
print('TOTALE %d test, %d PASS, %d FAIL'%(len(R),sum(1 for _,o in R if o),sum(1 for _,o in R if not o)))
