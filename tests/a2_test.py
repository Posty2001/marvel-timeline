import json,sys
from playwright.sync_api import sync_playwright
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/work/index.html'
fails=[]
def ck(c,m,info=''):
    if not c: print('FAIL',m,info); fails.append(m)
    else: print('PASS',m)
with sync_playwright() as p:
    b=p.chromium.launch()
    for vw,vh in ((320,640),(390,844),(430,932)):
        pg=b.new_page(viewport={'width':vw,'height':vh}); pg.set_default_timeout(8000); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(F); pg.wait_for_timeout(900)
        pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true}"); pg.wait_for_timeout(300)
        # safe area simulata (iPhone con Dynamic Island, standalone)
        pg.evaluate("()=>{const r=document.documentElement.style;r.setProperty('--sat','59px');r.setProperty('--sab','34px')}")
        pg.click('#appTabAtlante'); pg.wait_for_timeout(700)
        st=pg.evaluate("()=>({a2:atlas2Toggle.checked,cl:tvaArchivesToggle.checked,tab:document.querySelector('.app-tab-active')?.dataset.tab,cards:(tvaAtlas2.openUniversi(),document.querySelectorAll('#atlas2 .a2-card').length)})")
        ck(st['a2'] and not st['cl'] and st['tab']=='atlante' and st['cards']==27,'[%d] tab Atlante apre 2.0 con 27 universi'%vw,st)
        g=pg.evaluate("""()=>{const m=document.querySelector('.sidebar-open-btn').getBoundingClientRect();const t=document.querySelector('.a2-ttl').getBoundingClientRect();const top=document.querySelector('.a2-top').getBoundingClientRect();
          const sc=document.querySelector('.a2-scroll');const bar=document.getElementById('appTabbar').getBoundingClientRect();
          return {menuR:m.right,ttlL:t.left,topH:top.height,topPadT:getComputedStyle(document.querySelector('.a2-top')).paddingTop,swOver:sc.scrollWidth-sc.clientWidth,docOver:document.documentElement.scrollWidth-innerWidth,classicR:document.querySelector('.a2-exit').getBoundingClientRect().right,vw:innerWidth,barTop:bar.top,scB:sc.getBoundingClientRect().bottom}}""")
        ck(g['ttlL']>=g['menuR']-1,'[%d] titolo non sovrapposto al menu circolare'%vw,g)
        ck(g['swOver']<=1 and g['docOver']<=1,'[%d] nessun overflow orizzontale'%vw,g)
        ck(g['classicR']<=g['vw']+0.5,'[%d] pulsante archivio classico dentro lo schermo'%vw,g)
        ck(g['topPadT']=='70.8px' or float(g['topPadT'][:-2])>=59,'[%d] header rispetta la safe area superiore'%vw,g['topPadT'])
        # target tattili
        small=pg.evaluate("""()=>[...document.querySelectorAll('#atlas2 button')].filter(b=>b.offsetParent!==null&&!b.hidden).map(b=>[b.className,b.getBoundingClientRect().height]).filter(x=>x[1]<40).slice(0,5)""")
        ck(not small,'[%d] target tattili >=40px'%vw,small)
        if vw==390:
            pg.screenshot(path='a2_home.png')
        # ogni universo
        unis=pg.evaluate("()=>Object.keys(JSON.parse(document.getElementById('mvMapData').textContent).universi)")
        okAll=True; sets={}
        for uid in unis:
            pg.evaluate("u=>{tvaAtlas2.openUniversi();}",uid); pg.wait_for_timeout(60)
            pg.evaluate("u=>document.querySelector('#atlas2 .a2-card[data-uid=\"'+u+'\"]').click()",uid); pg.wait_for_timeout(80)
            r=pg.evaluate("""(u)=>{const q=sel=>[...document.querySelectorAll('#atlas2 '+sel+' .a2-row')].map(b=>b.getAttribute('data-go').split(':')[1]);
              const rows=q('.a2-sec-prim').concat(q('.a2-sec-cro'));const exp=tvaIdx.titoliDi(u).map(e=>e.id);const dupl=rows.length!==new Set(rows).size;
              const expC=exp.filter(id=>tvaIdx.ruoloDi(tvaIdx.titoli[id])==='crossover'), expP=exp.filter(id=>tvaIdx.ruoloDi(tvaIdx.titoli[id])==='appartenenza');
              const catOk=JSON.stringify(q('.a2-sec-prim').sort())===JSON.stringify(expP.slice().sort())&&JSON.stringify(q('.a2-sec-cro').sort())===JSON.stringify(expC.slice().sort());
              const vOk=JSON.stringify(q('.a2-sec-var').sort())===JSON.stringify(tvaIdx.varianti(u).map(e=>e.id).sort());
              const emp=[...document.querySelectorAll('#atlas2 .a2-empty')].map(x=>x.textContent);
              const sc=document.querySelector('.a2-scroll');
              return {rows,exp,dupl,emp,catOk,vOk,over:sc.scrollWidth-sc.clientWidth,h:document.querySelector('#atlas2 .a2-hero h2').textContent}}""",uid)
            if not r['catOk'] or not r['vOk']: okAll=False; print('  categorie KO',uid)
            if sorted(r['rows'])!=sorted(r['exp']) or r['dupl'] or r['over']>1: okAll=False; print('  KO',uid,r['rows'][:5],r['exp'][:5],r['over'])
            if not r['exp'] and not r['emp']: okAll=False; print('  no empty state',uid)
            sets[uid]=tuple(sorted(r['rows']))
        ck(okAll,'[%d] ogni scheda universo mostra esattamente i suoi titoli (27 universi)'%vw)
        if vw==390:
            dups={}
            for u,s in sets.items():
                if s: dups.setdefault(s,[]).append(u)
            print('  liste identiche (ammesse solo se i dati coincidono):',[v for v in dups.values() if len(v)>1])
            for k in ('uni-earth-828','uni-earth-121698','uni-earth-199999-mcu','uni-earth-96283-raimi-verse','uni-earth-120703-garfield-verse','uni-sony-s-spider-man-universe-ssu','uni-earth-10005-fox-verse','uni-earth-838','uni-x-men-97-verse'):
                print('  ',k,len(sets[k]),list(sets[k])[:8])
            ck(sets['uni-earth-828']==('item-125',),'Earth-828 = solo 125')
            ck(sets['uni-earth-121698']==('item-029','item-030'),'Earth-121698 = 029, 030')
            ck(sets['uni-earth-838']==(),'Earth-838 vuoto')
            ck(set(sets['uni-earth-96283-raimi-verse'])!=set(sets['uni-earth-120703-garfield-verse']) and set(sets['uni-earth-96283-raimi-verse'])!=set(sets['uni-sony-s-spider-man-universe-ssu']),'Universi Spider-Man diversi tra loro')
            pg.evaluate("()=>{tvaAtlas2.openUniversi();document.querySelector('#atlas2 .a2-card[data-uid=\"uni-earth-199999-mcu\"]').click()}"); pg.wait_for_timeout(200)
            pg.screenshot(path='a2_mcu.png')
            # ordine per uscita monotono
            pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a2-f')].find(b=>/uscita/.test(b.textContent)).click()"); pg.wait_for_timeout(150)
            ordn=pg.evaluate("()=>{const A=JSON.parse(document.getElementById('atlasData').textContent).opere;const U={};A.forEach(o=>U[o.id]=o.uscita||'');return [...document.querySelectorAll('#atlas2 .a2-sec-prim .a2-row')].map(b=>U[b.getAttribute('data-go').split('item-')[1]]||'9999')}")
            ck(ordn==sorted(ordn),'ordine per data di uscita crescente (MCU, sezione appartenenza)')
            pg.evaluate("()=>{tvaAtlas2.openUniversi();document.querySelector('#atlas2 .a2-card[data-uid=\"uni-earth-828\"]').click()}"); pg.wait_for_timeout(200)
            pg.screenshot(path='a2_828.png')
            # ricerca universale (Home TVA Archives)
            pg.evaluate("()=>tvaAtlas2.openHome()"); pg.wait_for_timeout(100)
            pg.fill('#a2HomeSearch','spider'); pg.wait_for_timeout(400)
            nres=pg.evaluate("()=>[document.querySelectorAll('#atlas2 .a2-resbox h3').length,document.querySelectorAll('#atlas2 .a2-resbox [data-go^=uni]').length]")
            ck(nres[0]>=2 and nres[1]>=3,'ricerca "spider": gruppi risultato + universi',nres)
            tch=pg.query_selector("#atlas2 .a2-resbox [data-go^='item:']"); ck(tch is not None,'ricerca → titolo cliccabile')
            tgt=tch.get_attribute('data-go').split(':')[1]; tch.click(); pg.wait_for_timeout(1300)
            pg.evaluate("()=>{const b=document.getElementById('d4Scheda');if(b)b.click()}"); pg.wait_for_timeout(1500)  # Fase 4: il chip N° apre il Dossier Opera; la scheda si raggiunge da 'Scheda in guida'
            ck(pg.evaluate("t=>!atlas2Toggle.checked&&document.getElementById(t).getBoundingClientRect().top<150",tgt),'Ricerca → Risultato → scheda in Timeline')
            pg.click('.td2-back:visible, #tvaBackBtn:visible')  # TD2: dalla pagina immersiva Indietro e' il pulsante della pagina; pg.wait_for_timeout(900)
            # C5: dalla Timeline si torna prima al Dossier Opera (Fase 4: schermata 'opera' nel percorso); un secondo Indietro riporta alla Home con la ricerca
            ck(pg.evaluate("()=>atlas2Toggle.checked&&tvaAtlas2.stato().screen==='opera'"),'Indietro dalla Timeline -> Dossier Opera')
            pg.evaluate("()=>document.getElementById('tvaBackBtn').click()"); pg.wait_for_timeout(900)   # gesto/Indietro di sistema (il chip e' fuori vista dentro l'Atlante)
            q=pg.evaluate("()=>[atlas2Toggle.checked,tvaAtlas2.stato().sq,document.getElementById('a2HomeSearch').value]")
            ck(q==[True,'spider','spider'],'Back: ricerca conservata',q)
            pg.fill('#a2HomeSearch',''); pg.wait_for_timeout(300)
            pg.evaluate("()=>tvaAtlas2.openUniversi()"); pg.wait_for_timeout(150)
            pg.evaluate("()=>[...document.querySelectorAll('#atlas2 .a2-filters:not(.a2-fam) .a2-f')].find(b=>/Diramazione/.test(b.textContent)).click()"); pg.wait_for_timeout(200)
            nn=pg.evaluate("()=>[document.querySelectorAll('#atlas2 .a2-card').length,[...document.querySelectorAll('#atlas2 .a2-badge')].every(x=>x.textContent==='Diramazione')]")
            ck(nn==[5,True],'filtro tipologia Diramazione = 5 universi',nn)
            # scroll conservato dopo apertura universo e ritorno (freccia in-app)
            pg.evaluate("()=>{const s=tvaAtlas2.stato();s.nat='tutti';s.fam='tutte';s.q='';}")
            pg.evaluate("()=>{tvaAtlas2.openUniversi();}"); pg.wait_for_timeout(100)
            pg.evaluate("()=>{document.querySelector('.a2-scroll').scrollTop=500}"); pg.wait_for_timeout(200)
            pg.evaluate("()=>document.querySelectorAll('#atlas2 .a2-card')[2].click()"); pg.wait_for_timeout(200)
            pg.click('#atlas2 .a2-back'); pg.wait_for_timeout(500)
            ck(abs(pg.evaluate("()=>document.querySelector('.a2-scroll').scrollTop")-500)<30,'freccia in-app: scorrimento della panoramica ripristinato')
            # archivio classico: non più raggiungibile dal dossier (integrazione legacy); il toggle viene reindirizzato all'Atlante
            pg.evaluate("()=>tvaAtlas2.openUni('uni-earth-828',true)"); pg.wait_for_timeout(200)
            ck(pg.evaluate("()=>!document.querySelector('#atlas2 .a2-foot .a2-ghost')&&!/archivio classico/i.test(document.getElementById('atlas2').innerText)"),'il dossier universo non rimanda all\'archivio classico')
        # fondo contenuto non coperto dalla tabbar
        pg.evaluate("()=>{tvaAtlas2.openUni('uni-earth-199999-mcu');}"); pg.wait_for_timeout(200)
        pg.evaluate("()=>{const s=document.querySelector('.a2-scroll');s.scrollTop=s.scrollHeight}"); pg.wait_for_timeout(300)
        e=pg.evaluate("()=>({last:[...document.querySelectorAll('.a2-scroll > *')].pop().getBoundingClientRect().bottom,bar:innerHeight-34})")
        ck(e['last']<=e['bar']+0.5,'[%d] ultimo elemento sopra la safe area inferiore (la barra dell’app è nascosta)'%vw,e)
        ck(not errs,'[%d] nessun errore JS'%vw,errs)
        pg.close()
    b.close()
print('FAILS',len(fails),fails)
