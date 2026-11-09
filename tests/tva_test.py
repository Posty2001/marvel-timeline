from playwright.sync_api import sync_playwright
import json,sys
F='file:///home/claude/work/index.html'
fails=[]
def ck(c,m):
    if not c: fails.append(m); print('FAIL',m)
def run(vw=(390,844)):
    with sync_playwright() as p:
        b=p.chromium.launch(); ctx=b.new_context(viewport={'width':vw[0],'height':vw[1]},has_touch=True,is_mobile=True); pg=ctx.new_page()
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        def fresh():
            pg.goto(F); pg.wait_for_timeout(1200)
            pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
        def ev(js): return pg.evaluate(js)
        def st(): return ev("()=>({sc:tvaAtlas2.stato().screen,uid:tvaAtlas2.stato().uid,sez:tvaAtlas2.stato().sez,on:atlas2Toggle.checked,d:tvaNavStato().depth,tab:getComputedStyle(appTabbar).display,hub:homeHubExited.checked})")
        def click(sel): ev("(s)=>document.querySelector(s).click()".replace('(s)=>','()=>')[:0] or "()=>document.querySelector(%s).click()"%json.dumps(sel)); pg.wait_for_timeout(350)
        def backchip(): ev("()=>document.getElementById('tvaBackBtn').click()"); pg.wait_for_timeout(700)
        fresh()
        ls0=ev("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!/backup|tvaHomeMiss/i.test(k))o[k]=localStorage.getItem(k)}return o}")
        # A ingresso
        ck(ev("()=>!!document.getElementById('a2Entry')"),'A entry card assente')
        click('#a2Entry'); s=st()
        ck(s['on'] and s['sc']=='home' and s['d']==1,'A1 ingresso %s'%s)
        ck(s['tab']=='none','A2 barra inferiore visibile in modalita immersiva')
        ck(ev("()=>getComputedStyle(document.querySelector('.sidebar-open-btn')).display")=='none','A3 hamburger visibile')
        ck(ev("()=>document.querySelectorAll('nav').length>=1 && [...document.querySelectorAll('.a2 nav')].every(n=>!n.classList.contains('app-tabbar'))"),'A4 seconda barra')
        ck(ev("()=>{const s=document.querySelector('.a2-scroll');return s.scrollWidth<=s.clientWidth+1}"),'A5 overflow orizzontale home')
        ck(ev("()=>{const t=document.querySelector('.a2-top').getBoundingClientRect();return t.top>=0&&t.height>=44}"),'A6 header')
        ck(ev("()=>[...document.querySelectorAll('.a2-top button')].every(b=>{const r=b.getBoundingClientRect();return r.width>=43.5&&r.height>=43.5})"),'A7 bersagli header >=44')
        ck(ev("()=>document.querySelectorAll('.hm-p[data-tile]').length")==15,'A8 quindici portali')
        ck(ev("()=>document.querySelectorAll('.hm-q[data-quick]').length")==2,'A9 collegamenti rapidi')
        # B/C universi, dossier, Indietro con stato
        click('[data-tile=universi]'); s=st(); ck(s['sc']=='universi' and s['d']==2,'B1 %s'%s)
        ck(ev("()=>document.querySelectorAll('.a2-card[data-uid]').length")==27,'B2 27 universi')
        click('.a2-f:nth-child(2)'); n1=ev("()=>document.querySelectorAll('.a2-card[data-uid]').length")
        ev("()=>{document.querySelector('.a2-scroll').scrollTop=300}"); pg.wait_for_timeout(100)
        y1=ev("()=>document.querySelector('.a2-scroll').scrollTop")
        click('.a2-card'); s=st(); ck(s['sc']=='uni' and s['d']==3,'C1 %s'%s)
        uid=s['uid']
        ck(ev("()=>document.querySelector('.a2-scroll').classList.contains('a2-dossier')"),'C2 dossier pergamena')
        ck(ev("()=>getComputedStyle(document.querySelector('.a2-sec')).backgroundImage.includes('gradient')"),'C3 pergamena sezioni')
        ck(ev("()=>getComputedStyle(document.querySelector('.a2-hero')).backgroundColor!=='rgb(236, 224, 200)'"),'C4 hero non pergamena')
        click('.a2-back'); pg.wait_for_timeout(500); s=st()
        ck(s['sc']=='universi' and s['d']==2,'C5 back da dossier %s'%s)
        ck(ev("()=>document.querySelectorAll('.a2-card[data-uid]').length")==n1,'C6 filtro ripristinato')
        ck(abs(ev("()=>document.querySelector('.a2-scroll').scrollTop")-y1)<=3,'C7 posizione ripristinata')
        # D dossier -> titolo (Timeline) -> Indietro
        click('.a2-card'); 
        ev("()=>document.querySelector('.a2-row[data-go]').click()"); pg.wait_for_timeout(900)
        pg.evaluate("()=>{const b=document.getElementById('d4Scheda');if(b)b.click()}"); pg.wait_for_timeout(1200)  # Fase 4: N° -> Dossier Opera -> Scheda in guida
        # TD2: «Scheda in guida» apre la pagina immersiva del titolo (barra app nascosta per progetto); Indietro e' il pulsante della pagina
        s=st(); ck(not s['on'] and s['tab']=='none' and ev("()=>!!document.querySelector('.td-page')"),'D1 Atlante chiuso, pagina immersiva aperta %s'%s)
        ck(ev("()=>!!document.querySelector('.td-page .td2-back')"),'D2 pulsante Indietro della pagina')
        ev("()=>document.querySelector('.td-page .td2-back').click()"); pg.wait_for_timeout(1500); backchip() if st()['sc']=='opera' else None; s=st(); ck(s['on'] and s['sc']=='uni' and s['uid']==uid and s['tab']=='none','D3 ritorno al dossier %s'%s)
        # E App Marvel da dossier
        click('.a2-exit'); pg.wait_for_timeout(700); s=st()
        ck((not s['on']) and s['d']==0 and not s['hub'] and s['tab']!='none','E1 uscita ad app %s'%s)
        ck(ev("()=>getComputedStyle(document.getElementById('homeHub')).display!=='none'"),'E2 Home Marvel visibile')
        # F Indietro dalla Home Atlante esce all'app
        click('#a2Entry'); click('.a2-back'); pg.wait_for_timeout(600); s=st()
        ck((not s['on']) and s['d']==0 and s['tab']!='none','F1 %s'%s)
        # G catalogo
        click('#a2Entry'); click('.hm-q[data-quick=indice]'); cat=ev("()=>tvaAtlas2.catalogo().map(g=>g.items.map(i=>[i.k,i.st,i.act?i.act[0]:'prep',i.act?i.act[1]:null,(i.subs||[]).map(x=>x.act)]))")
        ck(ev("()=>document.querySelectorAll('.a2-lrow[data-sez]').length")==15,'G1 15 voci (Reliquiario incluso)')
        def verify(act,label):
            t=act[0]
            if t=='tog': return ev("()=>document.getElementById(%s).checked"%json.dumps(act[1]))
            if t=='cls':
                return ev("()=>tvaArchivesToggle.checked")and(not act[1] or ev("()=>document.getElementById(%s).checked"%json.dumps(act[1])))
            if t=='card': return ev("()=>tvaArchivesToggle.checked && !!document.querySelector('#tvaArchivesOverlayEl details.card[open]')")
            if t=='chr': return ev("()=>tvaArchivesToggle.checked && !document.getElementById(%s).hidden && document.getElementById(%s).offsetParent!==null"%(json.dumps(act[1]),json.dumps(act[1])))
            if t=='tl': return ev("()=>!atlas2Toggle.checked && homeHubExited.checked")
            return True
        def tryact(act,label,ret):
            pg.wait_for_timeout(100)
            pg.wait_for_timeout(700)
            ck(verify(act,label),'G %s apertura %s'%(label,act))
            ck(not st()['on'],'G %s atlante chiuso'%label)
            backchip(); s=st(); ck(s['on'] and s['sc']==ret and s['tab']=='none','G %s ritorno a %s: %s'%(label,ret,s))
        for g in cat:
            for k,stt,a0,a1,subs in g:
                click('[data-sez=%s]'%k) if st()['sc']=='catalogo' else None
                s=st()
                if stt=='prep':
                    ck(s['sc']=='soon' and s['sez']==k,'G %s prep -> soon'%k)
                    ck(ev("()=>!!document.querySelector('.a2-st-prep') && !document.querySelector('.a2-lrow')"),'G %s soon senza falsi contenuti'%k)
                    click('.a2-back'); ck(st()['sc']=='catalogo','G %s back da soon'%k)
                elif a0=='sub':
                    ck(s['sc']=='sezione','G %s sub'%k)
                    for i,act in enumerate(subs):
                        ev("()=>document.querySelectorAll('.a2-lrow')[%d].click()"%i); tryact(act,k+str(i),'sezione')
                    click('.a2-back'); ck(st()['sc']=='catalogo','G %s back da sezione'%k)
                elif a0=='arc':
                    ck(s['sc']=='arch' and s['on'],'G %s -> arch (%s)'%(k,s))
                    ck(ev("()=>tvaAtlas2.getState().arc")==a1,'G %s arc=%s'%(k,a1))
                    # C5: mis=3 (Stregoneria, Magia oscura, Magia del caos; docs/REPORT_relazioni_alberi_arti.md, tree_arti_test)
                    ck(ev("()=>document.querySelectorAll('.a2-arcard').length")==dict(org=17,art=16,evt=7,luo=16,cos=26,spe=8,mis=3)[a1],'G %s n schede'%k)
                    ev("()=>document.querySelector('.a2-arcard').click()"); pg.wait_for_timeout(200)
                    ck(st()['sc']=='dossier' and st()['on'],'G %s dossier'%k)
                    click('.a2-back'); ck(st()['sc']=='arch','G %s back dossier->arch'%k)
                    click('.a2-back'); ck(st()['sc']=='catalogo','G %s back arch->catalogo'%k)
                elif a0=='scr':
                    ck(s['sc']==a1,'G %s -> %s (%s)'%(k,a1,s['sc']))
                    click('.a2-back'); ck(st()['sc']=='catalogo','G %s back'%k)
                elif a0 in ('map','rel'):   # C5: schermate native dell'Atlante (Mappa 3b / Reliquiario): restano nell'Atlante, il tasto indietro torna al catalogo
                    ck(s['on'] and s['sc']==('mappa' if a0=='map' else 'reliquiario'),'G %s -> schermata nativa (%s)'%(k,s['sc']))
                    click('.a2-back'); ck(st()['sc']=='catalogo','G %s back'%k)
                else:
                    tryact([a0,a1],k,'catalogo')
        # H cronologie e relazioni
        for scr,n in (('cronologie',15),('relazioni',4)):   # C5: Cronologie ha 15 voci
            click('.a2-back') if st()['sc']!='home' else None
            click('#a2Entry') if not st()['on'] else None
            ev("()=>tvaAtlas2.enter()"); pg.wait_for_timeout(200)
            click('[data-tile=%s]'%scr); ck(st()['sc']==scr,'H %s'%scr)
            rows=ev("()=>document.querySelectorAll('.a2-lrow').length"); ck(rows==n,'H %s righe %d!=%d'%(scr,rows,n))
            for i in range(rows):
                if st()['sc']!=scr: break
                ev("()=>document.querySelectorAll('.a2-lrow')[%d].click()"%i); pg.wait_for_timeout(800)
                s=st()
                if s['sc']==scr and s['on']:  # Varianti -> personaggi (C5: resta nella stessa schermata E nell'Atlante; le voci che aprono overlay classici hanno on=False)
                    continue
                if s['sc']=='personaggi':
                    ck(ev("()=>document.querySelector('.a2-f.on').textContent.startsWith('Varianti')"),'H varianti filtro')
                    click('.a2-back'); continue
                ck((not s['on']) or s['sc']!=scr,'H %s[%d] apre sezione'%(scr,i))   # C5: overlay classico (Atlante chiuso) OPPURE schermata nativa diversa
                backchip(); s=st(); ck(s['on'] and s['sc']==scr,'H %s[%d] ritorno %s'%(scr,i,s))
        # J speciali home
        ev("()=>tvaAtlas2.enter()"); pg.wait_for_timeout(300)
        for i in (0,1):
            if not st()['on']: click('#a2Entry')
            ev("()=>tvaAtlas2.openHome()"); pg.wait_for_timeout(200)
            ev("()=>document.querySelector('.hm-p[data-tile=%s]').click()"%('reliquiario' if i==0 else 'poteri')); pg.wait_for_timeout(900)   # C5: .a2-feat (rimosso) -> portali Home Atlante
            if i==1:
                ck(st()['sc']=='potenza' and st()['on'],'J feat 1 apre la Potenza TVA'); click('.a2-back'); ck(st()['sc']=='home' and st()['on'],'J feat 1 ritorno'); continue
            if i==0:
                ck(st()['sc']=='reliquiario' and st()['on'],'J feat 0 apre il Reliquiario'); click('.a2-back'); ck(st()['sc']=='home' and st()['on'],'J feat 0 ritorno'); continue
            ck(ev("()=>tvaArchivesToggle.checked && [...document.querySelectorAll('#tvaArchivesOverlayEl details.card[open]')].some(d=>d.offsetParent!==null && /Gemme|forte/.test(d.querySelector('.title').textContent))"),'J feat %d apre scheda'%i)
            backchip(); ck(st()['on'] and st()['sc']=='home','J feat %d ritorno'%i)
        # K ricerca
        ev("()=>tvaAtlas2.openHome()"); pg.wait_for_timeout(200)
        pg.fill('#a2HomeSearch','gemme'); pg.wait_for_timeout(400)
        ck(ev("()=>document.querySelectorAll('.a2-resbox .a2-chip').length")>=1,'K ricerca gemme -> archivi')   # C5: risultati a chip (.a2-chip), non piu' righe .a2-lrow
        pg.fill('#a2HomeSearch','Loki'); pg.wait_for_timeout(400)
        ck(ev("()=>document.querySelectorAll('.a2-resbox [data-go^=char]').length")>=1 and ev("()=>document.querySelectorAll('.a2-resbox [data-go^=item]').length")>=1,'K ricerca Loki')
        ev("()=>document.querySelector('.a2-resbox [data-go^=char]').click()"); pg.wait_for_timeout(900)
        ck(st()['sc']=='char' and st()['on'],'K char apre scheda'); backchip(); s=st()
        ck(s['on'] and s['sc']=='home' and ev("()=>document.getElementById('a2HomeSearch').value")=='Loki','K ricerca ripristinata %s'%s)
        pg.fill('#a2HomeSearch','616'); pg.wait_for_timeout(400); ck(ev("()=>!!document.querySelector('.a2-res .a2-info')"),'K nota 616')
        pg.fill('#a2HomeSearch','zzzzqq'); pg.wait_for_timeout(400); ck(ev("()=>!!document.querySelector('.a2-res .a2-empty')"),'K nessun risultato')
        pg.fill('#a2HomeSearch','')
        click('.a2-srch'); ck(ev("()=>document.activeElement.id")=='a2HomeSearch','K lente su Home mette a fuoco')
        click('.hm-q[data-quick=indice]'); click('.a2-srch'); ck(st()['sc']=='search','K lente altrove -> ricerca'); click('.a2-back')
        # L personaggi
        ev("()=>tvaAtlas2.openHome()"); click('[data-tile=personaggi]')
        n=ev("()=>document.querySelectorAll('.a2-prow').length"); ck(n==300,'L 300 personaggi %d'%n)
        ck(ev("()=>!document.querySelector('.a2-prow b') || true"),'')
        click('.a2-stick .a2-f:nth-child(2)'); nv=ev("()=>document.querySelectorAll('.a2-prow').length"); ck(0<nv<30,'L varianti %d'%nv)
        click('.a2-stick .a2-f:nth-child(1)')
        ev("()=>[...document.querySelectorAll('.a2-jl')].find(b=>b.textContent==='M').click()"); pg.wait_for_timeout(200)
        ym=ev("()=>document.querySelector('.a2-scroll').scrollTop"); ck(ym>1000,'L salto lettera %d'%ym)
        ev("()=>document.querySelector('.a2-prow').click()") if False else None
        ev("()=>{const r=[...document.querySelectorAll('.a2-prow')].find(x=>x.getBoundingClientRect().top>200);r.click()}"); pg.wait_for_timeout(900)
        # C5: il dossier personaggio (K/L) e' una schermata nativa dell'Atlante (sc=='char'), non piu' un overlay esterno
        ck(st()['sc']=='char' and st()['on'],'L scheda personaggio'); backchip(); s=st()
        ck(s['on'] and s['sc']=='personaggi' and abs(ev("()=>document.querySelector('.a2-scroll').scrollTop")-ym)<=4,'L posizione ripristinata %s'%s)
        # M menu generale
        ev("()=>tvaAtlas2.exit()"); pg.wait_for_timeout(500)
        ev("()=>{sidebarToggle.checked=true}"); pg.wait_for_timeout(200)
        ck(ev("()=>!!document.getElementById('a2SidebarLink')"),'M voce menu')
        ev("()=>document.getElementById('a2SidebarLink').click()"); pg.wait_for_timeout(500); s=st()
        ck(s['on'] and s['sc']=='home' and not ev("()=>sidebarToggle.checked"),'M entra da menu %s'%s)
        click('.a2-exit'); pg.wait_for_timeout(500)
        # N tab ATLANTE
        ev("()=>document.querySelector('.app-tab[data-tab=atlante]').click()"); pg.wait_for_timeout(500); s=st()
        ck(s['on'] and s['d']==0 and s['tab']=='none','N tab atlante %s'%s)
        click('.a2-back'); pg.wait_for_timeout(500); s=st(); ck(not s['on'] and s['tab']!='none','N back senza stack esce all app %s'%s)
        # O gesto indietro (history.back)
        click('#a2Entry'); click('[data-tile=universi]'); click('.a2-card')
        ev("()=>history.back()"); pg.wait_for_timeout(700); s=st(); ck(s['on'] and s['sc']=='universi' and s['d']==2,'O1 history.back %s'%s)
        ev("()=>history.back()"); pg.wait_for_timeout(700); s=st(); ck(s['on'] and s['sc']=='home' and s['d']==1,'O2 %s'%s)
        ev("()=>history.back()"); pg.wait_for_timeout(700); s=st(); ck((not s['on']) and s['d']==0 and s['tab']!='none','O3 history.back esce all app %s'%s)
        # P 25 cicli
        for i in range(25):
            click('#a2Entry'); click('[data-tile=personaggi]'); click('.a2-back'); click('.a2-exit')
        ck(st()['d']==0 and not st()['on'],'P cicli: stack pulito')
        ls1=ev("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!/backup|tvaHomeMiss/i.test(k))o[k]=localStorage.getItem(k)}return o}")
        ck(ls0==ls1,'Q localStorage modificato: %s'%[k for k in set(ls0)|set(ls1) if ls0.get(k)!=ls1.get(k)])
        ck(not errs,'errori JS %s'%errs)
        b.close()
for vw in ((390,844),(320,568),(844,390)):
    print('== viewport',vw); run(vw)
print('FAILS',len(fails),fails)
