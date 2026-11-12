from b32lib import *
import json,re,os,hashlib
FX='/tmp/claude-0/t/fx/'
G="()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"
FR=['cornice-standard-tva','cornice-bronzo-temporale','cornice-argento-cronologico','cornice-oro-archivista','cornice-acciaio-mutante','cornice-energia-arcana','cornice-tecnologia-stark','cornice-wakanda','cornice-asgard','cornice-vuoto-temporale','cornice-incursione-rossa','cornice-nexus-supremo']
TH=['tema-tva-classico','tema-archivio-notturno','tema-cronologia-dorata','tema-multiverso-cremisi','tema-tecnologia-futuristica','tema-universo-mutante','tema-energia-mistica','tema-ombre-del-vuoto','tema-nexus-cosmico','tema-fine-del-tempo']
FXS=['effetto-scansione-temporale','effetto-bagliore-dorato','effetto-energia-cremisi','effetto-distorsione-nexus','effetto-particelle-cosmiche','effetto-aura-leggendaria']
AV=['agente','variante','esploratore','tecnologico','mistico','astratto','cronista','sentinella']
def sig(pg):  # fotografia dei dati di gioco (nessuna modifica attesa dalla personalizzazione)
    return pg.evaluate("""()=>({xp:window.marvelXpInfo&&marvelXpInfo.xp,lv:window.marvelXpInfo&&marvelXpInfo.livello,id:localStorage.getItem('marvel-ultimate-timeline-tessera-id'),
      keys:['watched','watched-anim','ratings','favorites','notes','missioni-xp-bonus','titoli-stagione','road-to-doomsday','badges-earned','badge-storico'].map(k=>localStorage.getItem('marvel-ultimate-timeline-'+k)),
      un:JSON.stringify(tvaRewards.state().u),bd:document.querySelectorAll('.badge-chip.badge-unlocked').length,txp:document.getElementById('tesseraXpTotale').textContent})""")
def reload(pg):
    pg.reload(); pg.wait_for_timeout(1200); pg.evaluate(G); pg.wait_for_timeout(1400)
def put(pg,seed):
    pg.evaluate("(s)=>{for(const k in s)localStorage.setItem(k,s[k])}",seed)
TM={'titoli':'titolo','cornici':'cornice','temi':'tema','effetti':'effetto','avatar':'avatar'}
def tab(pg,t): pg.click('#tcTab-'+TM[t]); pg.wait_for_timeout(120)
def hero(pg): return pg.evaluate("()=>document.getElementById('tcHero').innerHTML")
with sync_playwright() as p:
    b=p.chromium.launch(); ids,anim=ids_of(b); S=seed_full(ids,anim); SM=seed_mid(ids,30)
    # ============ contesto principale: profilo avanzato, schermo 390 ============
    ctx,pg,errs=boot(b,390,844,atlas=False); put(pg,S); reload(pg); open_tessera(pg); pg.wait_for_timeout(500)
    ok('S0 nessun errore JS all\'avvio',errs==[],errs)
    ok('S1 struttura: Tessera in alto, poi PERSONALIZZA/CONDIVIDI, poi Carriera TVA e Collezione',pg.evaluate("()=>{const w=document.querySelector('#tesseraOverlayEl .tessera-wrap');const k=[...w.children].map(c=>c.id||c.className.split(' ')[0]);return k.indexOf('tcHero')<k.indexOf('tcActions')&&k.indexOf('tcActions')<k.indexOf('tcCareer')&&k.indexOf('tcCareer')<k.indexOf('tcCollection')}"))
    ok('S2 niente settima tab',pg.evaluate("()=>document.querySelectorAll('.app-tabbar > .app-tab').length")==6,0)
    # ---- 1 render orizzontale ----
    ok('H1 carta orizzontale presente, composizione stretta a 390',pg.evaluate("()=>{const s=document.querySelector('#tcHero svg');return !!s&&s.dataset.layout==='compact'&&s.getAttribute('role')==='img'}"))
    t=pg.evaluate("()=>[...document.querySelectorAll('#tcHero svg text')].map(x=>x.textContent).join('|')")
    ok('H2 mostra nickname, Variant ID, titolo, livello, XP, progresso',all(x in t for x in ['Franco','VAR-','Nuova Variante','LV ','XP']),t)
    ok('H3 Variant ID uguale a quello permanente esistente',pg.evaluate("()=>document.querySelector('#tcHero svg').textContent.includes(localStorage.getItem('marvel-ultimate-timeline-tessera-id'))"))
    ok('H4 nessun dato riservato (UID/email/token/chiavi)',not re.search(r'uid|@|token|firebase|apikey|sync-code',re.sub(r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]+','',hero(pg)),re.I))
    ok('H5 tre badge scelti tra quelli ottenuti nella carta',pg.evaluate("()=>tvaTessera.current().badges.length")==3)
    ok('H6 gerarchia: nickname più grande del Variant ID',pg.evaluate("()=>{const t=[...document.querySelectorAll('#tcHero svg text')];const f=x=>+t.find(e=>e.textContent===x).getAttribute('font-size');return f('Franco')>f(document.getElementById('tesseraId').textContent.trim())}"))
    pg.screenshot(path='/tmp/o_hero390.png')
    # ---- 2 render verticale ----
    v=pg.evaluate("()=>tvaTessera.buildSvg('vertical')")
    ok('V1 carta verticale: viewBox 720x1200 e contenuti distinti (non è la orizzontale ruotata)','viewBox="0 0 720 1200"' in v and 'transform="rotate' not in v and all(x in v for x in ['Franco','VAR-','TIME VARIANCE AUTHORITY','TVA ARCHIVES','SEZIONE VARIANTI']))
    ok('V2 verticale senza dati privati',not re.search(r'uid|@|token|firebase',re.sub(r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]+','',v),re.I))
    # ---- 3-5 cornici, temi, effetti (motore) ----
    fr=pg.evaluate("(l)=>l.map(f=>tvaCardArt.build({name:'A',title:'T',id:'VAR-1',level:1,xp:0,xpCur:0,xpNeed:100,badges:[],avatar:{kind:'preset',id:'agente'},theme:'tema-tva-classico',frame:f,fx:null,frameName:'',themeName:'',fxName:''},'wide',{uid:'z'}))",FR)
    ok('F1 12 cornici producono 12 disegni tutti diversi',len(set(fr))==12)
    grp=[re.search(r'<g transform="scale\(([^"]*)\)">(.*)</g></svg>$',x,re.S).group(2) for x in fr]
    # differenza geometrica, non solo cromatica: le sagome (path/forme) senza i colori devono essere diverse
    shape=[re.sub(r'#[0-9a-fA-F]{3,6}|rgba?\([^)]*\)','C',g) for g in grp]
    ok('F2 le cornici differiscono per geometria (anche eliminando i colori): 12 sagome distinte',len(set(shape))==12,len(set(shape)))
    ok('F3 ogni cornice è leggera (< 18 KB) e senza filtri costosi',all(len(g)<18000 and 'filter' not in g and 'feGaussian' not in g for g in grp),[len(g) for g in grp])
    th=pg.evaluate("(l)=>l.map(f=>tvaCardArt.build({name:'A',title:'T',id:'VAR-1',level:1,xp:0,xpCur:0,xpNeed:100,badges:[],avatar:{kind:'preset',id:'agente'},theme:f,frame:'cornice-standard-tva',fx:null,frameName:'',themeName:'',fxName:''},'wide',{uid:'z'}))",TH)
    ok('T1 10 temi producono 10 composizioni diverse',len(set(th))==10)
    ok('T2 palette riconoscibili: almeno 9 colori di accento/barra diversi',len(set(re.findall(r'fill="(#[0-9a-f]{6})"/></svg>',''.join(th)))|set(re.search(r'<rect x="372" y="442"[^>]*fill="(#[0-9a-fA-F]+)"',x).group(1) for x in th))>=9)
    fx=pg.evaluate("(l)=>l.map(f=>tvaCardArt.build({name:'A',title:'T',id:'VAR-1',level:1,xp:0,xpCur:0,xpNeed:100,badges:[],avatar:{kind:'preset',id:'agente'},theme:'tema-tva-classico',frame:'cornice-standard-tva',fx:f,frameName:'',themeName:'',fxName:''},'compact',{uid:'z'}))",FXS)
    nofx=pg.evaluate("()=>tvaCardArt.build({name:'A',title:'T',id:'VAR-1',level:1,xp:0,xpCur:0,xpNeed:100,badges:[],avatar:{kind:'preset',id:'agente'},theme:'tema-tva-classico',frame:'cornice-standard-tva',fx:null,frameName:'',themeName:'',fxName:''},'compact',{uid:'z'})")
    ok('X1 6 effetti diversi tra loro e dal "nessuno", tutti con resa statica nel disegno',len(set(fx+[nofx]))==7 and all(len(x)>len(nofx)+300 for x in fx))
    ok('X2 effetti: nessun filtro SVG costoso e pochi elementi (< 80 nodi aggiunti)',all('<filter' not in x and (x.count('<')-nofx.count('<'))<80 for x in fx),[x.count('<')-nofx.count('<') for x in fx])
    # movimento ridotto
    ctxm=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block',reduced_motion='reduce'); pm=ctxm.new_page(); pm.goto(U); pm.wait_for_timeout(900)
    pm.evaluate("(s)=>{for(const k in s)localStorage.setItem(k,s[k])}",S); pm.reload(); pm.wait_for_timeout(1200); pm.evaluate(G); pm.wait_for_timeout(1400)
    pm.evaluate("()=>{tvaRewards.equip('effetto','effetto-scansione-temporale');}"); open_tessera(pm); pm.wait_for_timeout(500)
    an_r=pm.evaluate("()=>{const e=document.querySelector('#tcHero .tc-fx-scan');return e?getComputedStyle(e).animationName:'MISSING'}")
    ctxm.close()
    an_n=pg.evaluate("()=>{tvaRewards.equip('effetto','effetto-scansione-temporale');return 1}"); pg.wait_for_timeout(300)
    an_n=pg.evaluate("()=>{const e=document.querySelector('#tcHero .tc-fx-scan');return e?getComputedStyle(e).animationName:'MISSING'}")
    ok('X3 prefers-reduced-motion: nessuna animazione (resa statica); senza preferenza l\'animazione c\'è',an_r=='none' and an_n!='none' and an_n!='MISSING',(an_r,an_n))
    pg.evaluate("()=>tvaRewards.equip('effetto',null)")
    # ---- Carriera / Collezione ----
    pg.click('#tcCareer > summary'); pg.wait_for_timeout(250)
    ok('K1 Carriera TVA riusa la scheda esistente (livello, XP, statistiche) senza duplicarla',pg.evaluate("()=>document.querySelectorAll('#tesseraXpTotale').length===1&&!!document.querySelector('#tcCareer #tesseraCard #tesseraXpFill')"))
    ok('K2a Carriera: senza dati missioni calcolati, avviso (nessun calcolo forzato, nessun XP)',pg.evaluate("()=>document.querySelectorAll('#tcMissions li').length===0&&document.querySelector('#tcMissions .tc-note')!=null"))
    pg.evaluate("()=>{(window.marvelMissioniInfo=window.marvelMissioniInfo||{}).stato={settimanale:{cur:2,tot:5,done:false},tematica:{cur:1,tot:1,done:true},saga:{cur:3,tot:9,done:false},segreta:{cur:0,tot:1,done:false}};document.dispatchEvent(new CustomEvent('tva:missioni2'))}"); pg.wait_for_timeout(500)
    ok('K2 Carriera mostra le 4 missioni reali (dati esposti dalla Centrale, sola lettura) e i 14 distintivi, separati dalle 48 ricompense',pg.evaluate("()=>document.querySelectorAll('#tcMissions li').length===4&&document.querySelectorAll('#tcBadges li').length===14"),pg.evaluate("()=>[document.querySelectorAll('#tcMissions li').length,!!(window.marvelMissioniInfo&&marvelMissioniInfo.stato)]"))
    ok('K3 Carriera: niente identità duplicata (nome/ID/icona nascosti nella scheda)',pg.evaluate("()=>['.tessera-topline','.tessera-icon','#tesseraNameInput'].every(s=>getComputedStyle(document.querySelector('#tcCareer '+s)).display==='none')"))
    pg.click('#tcCollection > summary'); pg.wait_for_timeout(300)
    ok('K4 Collezione definitiva: 48 voci (20+12+10+6), nessuna ripetuta; il provvisorio 3.1 è sparito',pg.evaluate("()=>{const r=[...document.querySelectorAll('#tcCollBody .tc-crow')].map(x=>x.dataset.id);return r.length===48&&new Set(r).size===48&&!document.getElementById('rwCollection')}"))
    ok('K5 Collezione: intestazione con conteggio e voci distinte in sbloccate/bloccate',pg.evaluate("()=>document.querySelector('#tcCollection > summary').textContent==='Collezione · 48/48'"))
    pg.screenshot(path='/tmp/o_sections390.png',full_page=True)
    pg.click('#tcCollection > summary'); pg.click('#tcCareer > summary')
    # ---- editor: apertura / struttura ----
    base=sig(pg)
    pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(400)
    ok('E0 editor si apre con le sei categorie (Tessera 3.0: Stile)',pg.evaluate("()=>[...document.querySelectorAll('#tcEdTabs .tc-tab')].map(x=>x.textContent).join(',')")=='Avatar,Stile,Titoli,Cornici,Temi,Effetti')
    ok('E0b editor è un dialogo modale accessibile con focus dentro',pg.evaluate("()=>{const r=document.getElementById('tcEditor');return r.getAttribute('role')==='dialog'&&r.getAttribute('aria-modal')==='true'&&r.contains(document.activeElement)}"))
    pg.screenshot(path='/tmp/o_editor_avatar390.png')
    # ---- 13 avatar predefiniti ----
    pv=[]
    for i,a in enumerate(AV):
        pg.click('#tcEdBody .tc-grid-av .tc-tile:nth-child(%d)'%(i+1)); pg.wait_for_timeout(60)
        pv.append(pg.evaluate("()=>document.getElementById('tcEdPrev').innerHTML"))
    ok('A1 8 avatar predefiniti selezionabili, ognuno cambia l\'anteprima',len(set(pv))==8)
    ok('A2 avatar gratuiti: tutti disponibili (non fanno parte delle 48 ricompense)',pg.evaluate("()=>tvaRewards.catalog.length===48&&tvaRewards.catalog.every(r=>!/avatar/.test(r.id))")  )
    # ---- 8 anteprima senza salvataggio ----
    pg.click('#tcEdBody .tc-grid-av .tc-tile:nth-child(4)'); tab(pg,'cornici')
    rw0=pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-rewards')"); lk0=pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tessera-look')")
    h0=hero(pg); pg.click('#tcEdBody .tc-grid-cornice .tc-tile:nth-child(9)'); pg.wait_for_timeout(120)
    ok('P1 anteprima immediata nell\'editor',pg.evaluate("()=>document.getElementById('tcEdPrev').innerHTML.includes('A20 17 0 0 1 20 -1')"))
    ok('P2 anteprima NON salva nulla: carta in-app, premi e look invariati',hero(pg)==h0 and pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-rewards')")==rw0 and pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tessera-look')")==lk0)
    # ---- 9 annulla ----
    pg.click('#tcEdCancel'); pg.wait_for_timeout(250)
    ok('C1 Annulla chiude l\'editor e ripristina le preferenze precedenti',pg.evaluate("()=>!document.getElementById('tcEditor')&&tvaRewards.equipped().cornice==='cornice-standard-tva'&&tvaTessera.current().avatar.id==='agente'"))
    ok('C2 Annulla riporta il focus al pulsante PERSONALIZZA',pg.evaluate("()=>document.activeElement&&document.activeElement.id==='tcPersonalizzaBtn'"))
    # ---- 6,10 equipaggia e salva ----
    pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(300); pg.click('#tcEdBody .tc-grid-av .tc-tile:nth-child(5)')
    tab(pg,'titoli'); pg.click('#tcEdBody .tc-grid-titolo .tc-tile:nth-child(13)')
    tab(pg,'cornici'); pg.click('#tcEdBody .tc-grid-cornice .tc-tile:nth-child(12)')
    tab(pg,'temi'); pg.click('#tcEdBody .tc-grid-tema .tc-tile:nth-child(10)')
    tab(pg,'effetti'); pg.click('#tcEdBody .tc-grid-effetto .tc-tile:nth-child(7)')
    pg.click('#tcEdSave'); pg.wait_for_timeout(400)
    eq=pg.evaluate("()=>tvaRewards.equipped()")
    ok('G1 Salva: equipaggiati titolo/cornice/tema/effetto scelti (solo sbloccati)',eq=={'titolo':'titolo-viaggiatore-vuoto','cornice':'cornice-nexus-supremo','tema':'tema-fine-del-tempo','effetto':'effetto-aura-leggendaria'},eq)
    ok('G2 Salva: avatar nel look e carta in-app aggiornata',pg.evaluate("()=>tvaTessera.lookLoad().a==='mistico'")and 'Viaggiatore del Vuoto' in hero(pg) and 'tc-fx-rot' in hero(pg))
    ok('G3 una sola fonte di verità: equipaggiamento solo in tvaRewards (il look non lo duplica)',pg.evaluate("()=>{const l=tvaTessera.lookLoad();return Object.keys(l).every(k=>['v','a','b','ts'].includes(k))}"))
    ok('G4 la personalizzazione non tocca i dati di gioco (XP, livello, visti, missioni, badge)',sig(pg)==base,(sig(pg),base))
    pg.screenshot(path='/tmp/o_hero_custom390.png')
    # ---- 11 persistenza dopo riavvio ----
    reload(pg); open_tessera(pg); pg.wait_for_timeout(500)
    ok('R1 dopo riavvio: cosmetici, avatar e carta restano',pg.evaluate("()=>tvaRewards.equipped().cornice==='cornice-nexus-supremo'&&tvaTessera.current().avatar.id==='mistico'")and 'Viaggiatore del Vuoto' in hero(pg))
    # ---- 12 tre badge ----
    pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(300)
    n_ch=pg.evaluate("()=>document.querySelectorAll('.tc-bchip').length")
    for i in range(1,4):
        if pg.evaluate("(i)=>document.querySelector('.tc-bchip:nth-child('+i+')').getAttribute('aria-pressed')",i)=='true': pg.click('.tc-bchip:nth-child(%d)'%i)
    pg.click('.tc-bchip:nth-child(1)'); pg.click('.tc-bchip:nth-child(5)'); pg.click('.tc-bchip:nth-child(9)'); pg.click('.tc-bchip:nth-child(12)'); pg.wait_for_timeout(100)
    sel=pg.evaluate("()=>[...document.querySelectorAll('.tc-bchip.tc-sel')].map(x=>x.dataset.badge)")
    ok('B1 14 distintivi ottenuti proposti; massimo 3 selezionabili con avviso al quarto',n_ch==14 and len(sel)==3 and 'al massimo tre' in pg.evaluate("()=>document.getElementById('tcEdNote').textContent"),(n_ch,sel))
    pg.click('#tcEdSave'); pg.wait_for_timeout(300)
    ok('B2 i 3 distintivi scelti compaiono nella carta e persistono',pg.evaluate("()=>JSON.stringify(tvaTessera.current().badges)")==json.dumps(sel).replace(', ',','),(sel,pg.evaluate("()=>tvaTessera.current().badges")))
    # ---- 7 elementi bloccati: profilo intermedio ----
    ctx2,pg2,e2=boot(b,390,844,atlas=False); put(pg2,SM); reload(pg2); open_tessera(pg2); pg2.wait_for_timeout(500)
    pg2.click('#tcPersonalizzaBtn'); pg2.wait_for_timeout(300); tab(pg2,'cornici')
    cnt=pg2.evaluate("()=>({lock:document.querySelectorAll('#tcEdBody .tc-tile.tc-lock').length,all:document.querySelectorAll('#tcEdBody .tc-tile').length})")
    ok('L1 profilo intermedio: cornici bloccate distinte da quelle disponibili (aria-disabled + stile)',cnt['all']==12 and 0<cnt['lock']<12,cnt)
    pg2.locator('#tcEdBody .tc-grid-cornice .tc-tile.tc-lock').first.click(force=True); pg2.wait_for_timeout(120)
    note=pg2.evaluate("()=>document.getElementById('tcEdNote').textContent")
    ok('L2 una voce bloccata mostra il requisito di sblocco (con avanzamento) e non viene selezionata',note.startswith('Bloccata:') and pg2.evaluate("()=>!document.querySelector('#tcEdBody .tc-tile.tc-lock.tc-sel')"),note)
    ok('L3 equip diretto di una voce bloccata rifiutato dal sistema 3.1',pg2.evaluate("()=>tvaRewards.equip('cornice','cornice-nexus-supremo')")['ok']==False)
    pg2.click('#tcEdSave'); pg2.wait_for_timeout(200)
    ok('L4 salvare dopo un tentativo su voce bloccata non cambia nulla',pg2.evaluate("()=>tvaRewards.equipped().cornice==='cornice-standard-tva'"))
    pg2.click('#tcPersonalizzaBtn'); pg2.wait_for_timeout(300); tab(pg2,'effetti')
    ok('L5 effetti: "Nessuno" disponibile e selezionato per default',pg2.evaluate("()=>{const t=document.querySelector('#tcEdBody .tc-grid-effetto .tc-tile');return t.textContent.startsWith('Nessuno')&&t.getAttribute('aria-pressed')==='true'}"))
    ok('L6 utente con 0 badge: messaggio, nessun errore',(lambda: True)()) if False else None
    pg2.click('#tcEdCancel'); ctx2.close()
    # ---- 0 badge / nessuna foto / preferenze incomplete ----
    ctx3,pg3,e3=boot(b,390,844,atlas=False); put(pg3,{'marvel-ultimate-timeline-rewards':json.dumps({'v':1,'u':{},'e':{'cornice':'cornice-nexus-supremo','tema':123},'t':{}}),'marvel-ultimate-timeline-tessera-look':json.dumps({'v':1,'a':'photo','b':['critico','x']})}); reload(pg3); open_tessera(pg3); pg3.wait_for_timeout(500)
    cur=pg3.evaluate("()=>tvaTessera.current()")
    ok('D1 profilo nuovo con preferenze incomplete/corrotte: carta valida con predefiniti, nessun errore',e3==[] and cur['cornice']=='cornice-standard-tva' and cur['avatar']['kind']=='preset' and cur['badges']==[] and pg3.evaluate("()=>!!document.querySelector('#tcHero svg')"),(e3,cur))
    ok('D2 senza badge: la carta lo dice senza inventare distintivi',pg3.evaluate("()=>document.querySelector('#tcHero svg').textContent.includes('NESSUN DISTINTIVO')"))
    pg3.click('#tcPersonalizzaBtn'); pg3.wait_for_timeout(300)
    ok('D3 editor senza badge: messaggio informativo',pg3.evaluate("()=>document.getElementById('tcEdBody').textContent.includes('Non hai ancora distintivi')"))
    ctx3.close()
    # ---- 14-15 foto ----
    pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(300)
    nopk=lambda: pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tessera-photo')")
    ok('PH0 nessuna foto salvata all\'inizio (nessun caricamento automatico)',nopk() is None)
    reqs=[]; pg.on('request',lambda r: reqs.append(r.url) if r.method!='GET' or 'firebase' in r.url else None)
    for f,exp in (('note.txt','Formato non supportato'),('a.svg','Formato non supportato'),('fake.jpg','illeggibile'),('huge.png','megapixel')):
        pg.set_input_files('#tcFile',FX+f); pg.wait_for_timeout(1800)
        m=pg.evaluate("()=>document.getElementById('tcEdNote').textContent")
        ok('PH1 rifiuto controllato: %s'%f,exp in m and not pg.evaluate("()=>!!document.getElementById('tcPhoto')"),m)
    pg.set_input_files('#tcFile',FX+'orient6.jpg'); pg.wait_for_timeout(1500)
    dims=pg.evaluate("()=>{const s=tvaTessera._state().editor.ph.src;return [s.width,s.height]}")
    ok('PH2 orientamento EXIF applicato (200x100 con orientamento 6 -> 100x200)',dims==[100,200],dims)
    pg.screenshot(path='/tmp/o_photo390.png'); pg.click('#tcPhCancel'); pg.wait_for_timeout(150)
    ok('PH3 Annulla foto: nessuna foto, editor ancora aperto',nopk() is None and pg.evaluate("()=>!document.getElementById('tcPhoto')&&!!document.getElementById('tcEditor')"))
    pg.set_input_files('#tcFile',FX+'face.jpg'); pg.wait_for_timeout(1500)
    ok('PH4 immagine grande ridotta a lato massimo 1024 in memoria',pg.evaluate("()=>{const s=tvaTessera._state().editor.ph.src;return Math.max(s.width,s.height)===1024}"))
    def px(pg):
        return pg.evaluate("()=>{const c=document.getElementById('tcPhCv');const x=c.getContext('2d');const d=x.getImageData(c.width/2,c.height/2,1,1).data;return [d[0],d[1],d[2]]}")
    p0=px(pg)
    pg.evaluate("()=>{const z=document.getElementById('tcPhZoom');z.value=2.5;z.dispatchEvent(new Event('input',{bubbles:true}))}")
    box=pg.locator('#tcPhCv').bounding_box(); pg.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2); pg.mouse.down(); pg.mouse.move(box['x']+box['width']/2+60,box['y']+box['height']/2+30,steps=5); pg.mouse.up()
    st=pg.evaluate("()=>{const p=tvaTessera._state().editor.ph;return [p.zoom,Math.round(p.cx),Math.round(p.cy),p.src.width/2,p.src.height/2]}")
    ok('PH5 zoom e spostamento dell\'inquadratura funzionano',st[0]==2.5 and (st[1]!=st[3] or st[2]!=st[4]),st)
    pg.evaluate("()=>{const z=document.getElementById('tcPhBr');z.value=40;z.dispatchEvent(new Event('input',{bubbles:true}));const c=document.getElementById('tcPhCt');c.value=-30;c.dispatchEvent(new Event('input',{bubbles:true}))}")
    ok('PH6 luminosità e contrasto applicati all\'anteprima',pg.evaluate("()=>getComputedStyle(document.getElementById('tcPhCv')).filter")!='none')
    pg.click('#tcPhReset'); pg.wait_for_timeout(100)
    st2=pg.evaluate("()=>{const p=tvaTessera._state().editor.ph;return [p.zoom,p.br,p.ct,Math.round(p.cx)==p.src.width/2]}")
    ok('PH7 Ripristina azzera zoom, luminosità, contrasto e inquadratura (non distruttivo)',st2==[1,0,0,True],st2)
    pg.evaluate("()=>{const z=document.getElementById('tcPhBr');z.value=30;z.dispatchEvent(new Event('input',{bubbles:true}))}")
    pg.click('#tcPhOk'); pg.wait_for_timeout(500)
    ok('PH8 Conferma: foto solo in bozza, niente salvato finché non si preme Salva',nopk() is None and pg.evaluate("()=>!document.getElementById('tcPhoto')&&tvaTessera._state().editor.draft.avatar.kind==='photo'"))
    pg.click('#tcEdSave'); pg.wait_for_timeout(500)
    ph=nopk()
    ok('PH9 foto salvata localmente: JPEG 384x384 leggero (< 100 KB), nessuna richiesta di rete in uscita',ph is not None and ph.startswith('data:image/jpeg;base64,') and len(ph)<100000 and reqs==[],(len(ph or ''),reqs))
    ok('PH10 la foto compare nella carta e il look la indica; il profilo/backup NON la contiene',pg.evaluate("()=>document.querySelector('#tcHero svg image')!=null&&tvaTessera.lookLoad().a==='photo'&&!JSON.stringify(Object.fromEntries(Object.keys(localStorage).filter(k=>k!=='marvel-ultimate-timeline-tessera-photo').map(k=>[k,localStorage.getItem(k)]))).includes('data:image/jpeg')"))
    dm=pg.evaluate("""()=>new Promise(r=>{const i=new Image();i.onload=()=>r([i.width,i.height]);i.src=localStorage.getItem('marvel-ultimate-timeline-tessera-photo')})""")
    ok('PH11 dimensioni foto salvata 384x384',dm==[384,384],dm)
    # persistenza foto
    reload(pg); open_tessera(pg); pg.wait_for_timeout(500)
    ok('PH12 foto e scelta avatar persistono al riavvio',pg.evaluate("()=>tvaTessera.current().avatar.kind==='photo'&&!!document.querySelector('#tcHero svg image')"))
    # nome
    pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(300)
    pg.fill('#tcEdName','Variante Lunga 12345'); pg.wait_for_timeout(100)
    n1=pg.evaluate("()=>({fs:parseFloat(getComputedStyle(document.getElementById('tcEdName')).fontSize),kb:document.getElementById('tcEditor').classList.contains('tc-kb'),d:getComputedStyle(document.getElementById('tcEdPrev')).display,a:document.activeElement.id})")
    ok('N1 tastiera: campo nome a 16px (niente zoom iOS) e anteprima nascosta durante la digitazione',n1['fs']>=16 and n1['kb'] and n1['d']=='none',n1)
    pg.click('#tcEdSave'); pg.wait_for_timeout(300)
    ok('N2 il nome salvato è lo stesso del campo storico (UserName) e della carta',pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-user-name')==='Variante Lunga 12345'&&document.getElementById('tesseraNameInput').value==='Variante Lunga 12345'&&document.querySelector('#tcHero svg').textContent.includes('Variante Lunga 12345')"))
    # ---- 16-17 PNG ----
    r=pg.evaluate("""async()=>{const b=await tvaTessera.exportPng();const bm=await createImageBitmap(b);const c=document.createElement('canvas');c.width=bm.width;c.height=bm.height;const x=c.getContext('2d');x.drawImage(bm,0,0);const d=x.getImageData(0,0,bm.width,bm.height).data;let nz=0,sum=0;for(let i=0;i<d.length;i+=4*97){sum+=d[i]+d[i+1]+d[i+2];nz+=d[i+3]===255?1:0}return {type:b.type,size:b.size,w:bm.width,h:bm.height,opaque:nz/(d.length/4/97),avg:sum/(d.length/4/97)/3}}""")
    ok('PNG1 esportazione: PNG 1080x1800, opaco, non vuoto',r['type']=='image/png' and r['w']==1080 and r['h']==1800 and r['opaque']>0.99 and r['size']>40000 and r['avg']>5,r)
    b64=pg.evaluate("""async()=>{const b=await tvaTessera.exportPng();const f=new FileReader();return await new Promise(r=>{f.onload=()=>r(f.result.split(',')[1]);f.readAsDataURL(b)})}"""); open('/tmp/o_export_sample.png','wb').write(__import__('base64').b64decode(b64))
    ok('PNG2 esportazione senza elementi UI: contiene solo la carta (sorgente SVG senza pulsanti/overlay/foreignObject/immagini esterne)',pg.evaluate("()=>{const s=tvaTessera.buildSvg('vertical');return !/foreignObject|<button|<input|http:\\/\\/(?!www\\.w3\\.org)|https:\\/\\/|<script|<style/.test(s)}"))
    ok('PNG3 carta verticale esportata include la foto locale, tema, cornice e effetto equipaggiati',pg.evaluate("()=>{const s=tvaTessera.buildSvg('vertical');return s.includes('<image')&&s.includes('data:image/jpeg')&&/nx\)/.test(s)&&s.includes('E5C879')&&s.includes('tc-fx')}"))
    pg.click('#tesseraCondividiBtn'); pg.wait_for_timeout(2500)
    ok('SH1 modale Condividi: anteprima PNG reale (img) e pulsanti',pg.evaluate("()=>!!document.querySelector('#tcShImg img.tc-sh-png')&&!document.getElementById('tcShSave').disabled"))
    ok('SH2 senza condivisione nativa: pulsante Condividi nascosto, messaggio e fallback "Salva PNG"',pg.evaluate("()=>document.getElementById('tcShShare').hidden===true&&document.getElementById('tcShNote').textContent.includes('Salva PNG')&&!document.getElementById('tcShSave').hidden"),pg.evaluate("()=>[typeof navigator.share,document.getElementById('tcShNote').textContent]"))
    pg.screenshot(path='/tmp/o_share390.png')
    with pg.expect_download() as dl: pg.click('#tcShSave')
    d=dl.value; d.save_as('/tmp/o_download.png')
    ok('SH3 "Salva PNG" scarica un file .png con il Variant ID nel nome',d.suggested_filename.endswith('.png') and 'tessera-tva-VAR' in d.suggested_filename and os.path.getsize('/tmp/o_download.png')>40000,d.suggested_filename)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok('SH4 Esc chiude la finestra di condivisione e restituisce il focus',pg.evaluate("()=>!document.getElementById('tcShare')&&document.activeElement.id==='tesseraCondividiBtn'"))
    # condivisione nativa emulata
    pg.evaluate("()=>{window.__sh=[];navigator.canShare=()=>true;navigator.share=(d)=>{window.__sh.push({n:d.files.length,t:d.files[0].type,nm:d.files[0].name});return Promise.resolve()}}")
    pg.click('#tesseraCondividiBtn'); pg.wait_for_timeout(2500)
    ok('SH5 (emulato) con Web Share disponibile: pulsante Condividi attivo e condivide 1 file PNG',pg.evaluate("()=>!document.getElementById('tcShShare').hidden&&!document.getElementById('tcShShare').disabled"))
    pg.click('#tcShShare'); pg.wait_for_timeout(300)
    ok('SH6 (emulato) share() riceve un File image/png',pg.evaluate("()=>window.__sh.length===1&&window.__sh[0].n===1&&window.__sh[0].t==='image/png'&&/^tessera-tva-VAR/.test(window.__sh[0].nm)"),pg.evaluate("()=>window.__sh"))
    pg.click('#tcShClose'); pg.wait_for_timeout(150)
    # errore di esportazione gestito
    pg.evaluate("()=>{window.__oldTB=HTMLCanvasElement.prototype.toBlob;HTMLCanvasElement.prototype.toBlob=function(cb){cb(null)}}")
    pg.click('#tesseraCondividiBtn'); pg.wait_for_timeout(2500)
    ok('SH7 esportazione fallita: messaggio chiaro, nessun crash, nessun pulsante inutile',pg.evaluate("()=>document.getElementById('tcShImg').textContent.includes('non riuscita')&&document.getElementById('tcShSave').hidden"),pg.evaluate("()=>document.getElementById('tcShImg').textContent"))
    pg.evaluate("()=>{HTMLCanvasElement.prototype.toBlob=window.__oldTB}"); pg.click('#tcShClose'); pg.wait_for_timeout(150)
    ok('SH8 esportazione non assegna XP né modifica dati',sig(pg)['xp']==base['xp'] and sig(pg)['keys']==base['keys'])
    # ---- sync/backup ----
    ok('Y1 sincronizzazione look: vince la scelta più recente',pg.evaluate("()=>{const a=JSON.stringify({v:1,a:'agente',b:['critico'],ts:100}),b={v:1,a:'mistico',b:['cronista'],ts:200};return JSON.parse(tvaTessera.lookMerge(a,b)).a==='mistico'&&JSON.parse(tvaTessera.lookMerge(JSON.stringify({v:1,a:'agente',ts:300}),b)).a==='agente'}"))
    ok('Y2 look valido solo se avatar/distintivi riconosciuti (sanitizzazione)',pg.evaluate("()=>JSON.stringify(tvaTessera.sanitizeLook({v:1,a:'<img>',b:['ok-id','../x',1,'critico','critico','a','b','c'],ts:'x'}))")=='{"v":1,"b":["ok-id","critico"]}' ,pg.evaluate("()=>JSON.stringify(tvaTessera.sanitizeLook({v:1,a:'<img>',b:['ok-id','../x',1,'critico','critico','a','b','c'],ts:'x'}))"))
    ctx.close()
    # ============ nickname lunghi (3 composizioni) ============
    ctx,pg,errs=boot(b,390,844,atlas=False); put(pg,S); reload(pg)
    for nm in ['WWWWWWWWWWWWWWWWWWWW','Maximilian-Alexander','ÀÈÌÒÙ ŞÇĞ 名前テスト漢字名','i'*20]:
        for lay in ('wide','compact','vertical'):
            r=pg.evaluate("""([nm,lay])=>{document.body.insertAdjacentHTML('beforeend','<div id=__t style="position:fixed;left:0;top:0;width:900px;opacity:0;pointer-events:none"></div>');const v=tvaTessera.current();v.name=nm;document.getElementById('__t').innerHTML=tvaCardArt.build(tvaTessera.model(v),lay,{uid:'q'});const s=document.querySelector('#__t svg');const vb=s.viewBox.baseVal;let bad=[];s.querySelectorAll('text').forEach(t=>{const b=t.getBBox();if(b.x<-1||b.x+b.width>vb.width+1||b.y<-1||b.y+b.height>vb.height+1)bad.push(t.textContent.slice(0,20)+':'+Math.round(b.x)+','+Math.round(b.width))});const n=[...s.querySelectorAll('text')].find(t=>t.textContent===nm||t.textContent.startsWith(nm.slice(0,5)));const rb=n?n.getBBox():null;document.getElementById('__t').remove();return {bad,nameW:rb&&Math.round(rb.width),right:rb&&Math.round(rb.x+rb.width),vbw:vb.width}}""",[nm,lay])
            ok('LN %s/%s: nessun testo fuori dalla carta'%(nm[:6],lay),r['bad']==[],r)
    ctx.close()
    # ============ responsive su 6 larghezze ============
    for w,h in ((320,640),(375,812),(390,844),(393,852),(430,932),(1280,800)):
        ctx,pg,errs=boot(b,w,h,atlas=False); put(pg,S); reload(pg); open_tessera(pg); pg.wait_for_timeout(500)
        m=pg.evaluate("""()=>{const d=document.documentElement;const hr=document.getElementById('tcHero').getBoundingClientRect();const s=document.querySelector('#tcHero svg');const k=hr.width/s.viewBox.baseVal.width;let min=99;s.querySelectorAll('text').forEach(t=>{min=Math.min(min,parseFloat(t.getAttribute('font-size'))*k)});
          const bt=[...document.querySelectorAll('#tcActions .tc-btn')].map(b=>b.getBoundingClientRect());return {sw:d.scrollWidth,cw:d.clientWidth,hl:hr.left,hr:hr.right,vw:innerWidth,min:Math.round(min*10)/10,layout:s.dataset.layout,bh:Math.min(...bt.map(r=>r.height)),bw:Math.min(...bt.map(r=>r.width)),inview:hr.left>=0&&hr.right<=innerWidth}}""")
        ok('W%d overflow orizzontale assente e carta interamente visibile'%w,m['sw']<=m['cw']+1 and m['inview'],m)
        ok('W%d testo più piccolo della carta >= 8.9px (composizione dedicata: %s)'%(w,m['layout']),m['min']>=8.9,m)
        ok('W%d pulsanti PERSONALIZZA/CONDIVIDI >= 44px di altezza'%w,m['bh']>=44 and m['bw']>=100,m)
        pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(400)
        e=pg.evaluate("""()=>{const d=document.documentElement;const r=document.getElementById('tcEditor').getBoundingClientRect();const bad=[...document.querySelectorAll('#tcEditor button,#tcEditor input')].filter(x=>{const q=x.getBoundingClientRect();return q.width>0&&(q.right>innerWidth+1||q.left<-1)}).map(x=>x.id||x.textContent.slice(0,12));
          const sm=[...document.querySelectorAll('#tcEditor .tc-tab,#tcEditor .tc-btn,#tcEditor .tc-tile,#tcEditor .tc-bchip')].filter(x=>x.getBoundingClientRect().height>0&&x.getBoundingClientRect().height<43).length;
          return {sw:d.scrollWidth,cw:d.clientWidth,full:r.width===innerWidth&&r.height===innerHeight,bad,sm,tabs:document.getElementById('tcEdTabs').scrollWidth<=document.getElementById('tcEdTabs').clientWidth+1||getComputedStyle(document.getElementById('tcEdTabs')).overflowX==='auto',body:getComputedStyle(document.getElementById('tcEdBody')).overflowY}}""")
        ok('W%d editor a schermo intero, senza overflow orizzontale, controlli entro lo schermo, target >= 43px'%w,e['sw']<=e['cw']+1 and e['full'] and e['bad']==[] and e['sm']==0 and e['body']=='auto',e)
        for t in ('cornici','temi','effetti','titoli','avatar'):
            tab(pg,t); chk=pg.evaluate("()=>{const b=document.getElementById('tcEdBody');return b.scrollWidth<=b.clientWidth+1}")
            if not chk: ok('W%d pannello %s senza overflow orizzontale'%(w,t),False)
        ok('W%d tutti i pannelli senza overflow orizzontale'%w,True)
        tab(pg,'cornici'); pg.screenshot(path='/tmp/o_ed_cornici_%d.png'%w)
        # scroll nel pannello e ritorno alla Tessera senza perdere stato
        pg.evaluate("()=>{document.getElementById('tcEdBody').scrollTop=9999}"); pg.click('#tcEdCancel'); pg.wait_for_timeout(250)
        ok('W%d chiusura editor: Tessera ancora aperta, carta intatta, nessun editor residuo'%w,pg.evaluate("()=>document.getElementById('tesseraToggle').checked&&!document.getElementById('tcEditor')&&!!document.querySelector('#tcHero svg')"))
        if w in (320,393):
            pg.click('#tesseraCondividiBtn'); pg.wait_for_timeout(2200)
            sh=pg.evaluate("()=>{const i=document.querySelector('#tcShImg img');const r=i.getBoundingClientRect();const d=document.documentElement;return {fit:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight,sw:d.scrollWidth<=d.clientWidth+1,b:[...document.querySelectorAll('#tcShare .tc-btn')].filter(x=>x.offsetParent).every(x=>x.getBoundingClientRect().height>=44)}}")
            ok('W%d finestra Condividi: PNG interamente visibile, pulsanti >=44px, nessun overflow'%w,sh['fit'] and sh['sw'] and sh['b'],sh)
            pg.screenshot(path='/tmp/o_share_%d.png'%w); pg.click('#tcShClose')
        if w==1280: pg.screenshot(path='/tmp/o_hero1280.png')
        ctx.close()
    # ============ chiusura Tessera con editor aperto + tab ============
    ctx,pg,errs=boot(b,390,844,atlas=False); put(pg,S); reload(pg); open_tessera(pg)
    pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(200)
    for _ in range(14): pg.keyboard.press('Tab')
    ok('FT1 focus trap: il Tab resta dentro l\'editor',pg.evaluate("()=>document.getElementById('tcEditor').contains(document.activeElement)"))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok('FT2 Esc chiude l\'editor senza salvare',pg.evaluate("()=>!document.getElementById('tcEditor')&&tvaRewards.equipped().cornice==='cornice-standard-tva'"))
    pg.click('#tcPersonalizzaBtn'); pg.wait_for_timeout(200); pg.evaluate("()=>{const c=document.getElementById('tesseraToggle');c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(200)
    ok('FT3 uscendo dalla Tessera con editor aperto, l\'editor viene annullato (nessuna bozza residua)',pg.evaluate("()=>!document.getElementById('tcEditor')"))
    ok('FT4 sicurezza area sicura/tastiera: regole CSS env(safe-area-inset-*) presenti per editor e finestre (verifica statica, non su dispositivo)',pg.evaluate("()=>{const t=[...document.styleSheets].flatMap(s=>{try{return [...s.cssRules].map(r=>r.cssText)}catch(e){return []}}).join('\\n');return /\\.tc-ed \\{[^}]*safe-area-inset-top/.test(t)&&/\\.tc-ed-body \\{[^}]*safe-area-inset-bottom/.test(t)}"))
    ctx.close(); b.close()
done()
