# Consolidamento 20261017-1600: categorie, bidirezionalita', Indietro (filtri, ricerca, scorrimento, .a2-scroll), history, tabbar, salvataggi
import json,sys,time
from playwright.sync_api import sync_playwright
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/work/index.html'
fails=[]
def ck(c,m,info=''):
    print(('PASS ' if c else 'FAIL ')+m,'' if c else info)
    if not c: fails.append(m)
MCU='uni-earth-199999-mcu'
with sync_playwright() as p:
    b=p.chromium.launch()
    def newpage(w=390,h=844):
        ctx=b.new_context(viewport={'width':w,'height':h}); pg=ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e))); pg.set_default_timeout(10000)
        pg.goto(F); pg.wait_for_timeout(1200)
        pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true}"); pg.wait_for_timeout(300)
        return ctx,pg,errs
    ctx,pg,errs=newpage()
    # ---------- 1. categorie: appartenenza / crossover / variante / ambientazione / origine / presenza ----------
    r=pg.evaluate("""()=>{const A=JSON.parse(document.getElementById('atlasData').textContent);const out={bad:[]};
      const uids=A.universi.map(u=>u.id);
      uids.forEach(u=>{tvaAtlas2.openUni(u,true);
        const q=s=>[...document.querySelectorAll('#atlas2 '+s+' .a2-row')].map(b=>b.getAttribute('data-go').split(':')[1].replace('item-',''));
        const raw=A.opere.filter(o=>o.universi.includes(u));
        const P=raw.filter(o=>o.ruolo==='primario').map(o=>o.id).sort(), C=raw.filter(o=>o.ruolo==='crossover').map(o=>o.id).sort();
        const got=q('.a2-sec-prim').filter(i=>!/^anim|^p4/.test(i)).sort(), gotC=q('.a2-sec-cro').filter(i=>!/^anim|^p4/.test(i)).sort();
        const anim=A.animate.filter(x=>x.universi.includes(u));
        const animP=anim.filter(x=>x.universi.length===1).length, animC=anim.filter(x=>x.universi.length>1).length;
        if(JSON.stringify(got)!==JSON.stringify(P)) out.bad.push(['prim',u,got.length,P.length]);
        if(JSON.stringify(gotC)!==JSON.stringify(C)) out.bad.push(['cro',u,gotC.length,C.length]);
        const nAnimRows=[...document.querySelectorAll('#atlas2 .a2-sec-prim .a2-row,#atlas2 .a2-sec-cro .a2-row')].filter(b=>/^item:anim|^item:p4/.test(b.getAttribute('data-go'))).length;
        if(nAnimRows!==anim.length) out.bad.push(['anim',u,nAnimRows,anim.length]);
        // nessun titolo crossover in 'appartenenza' e viceversa
        const inBoth=q('.a2-sec-prim').filter(i=>q('.a2-sec-cro').includes(i)); if(inBoth.length) out.bad.push(['both',u,inBoth]);
      });
      out.n=uids.length;return out}""")
    ck(r['n']==27 and not r['bad'],'27 universi: sezioni Appartenenza/Crossover coincidono con atlasData.ruolo (e serie animate multi-universo = crossover)',r['bad'][:6])
    r=pg.evaluate("""()=>{tvaAtlas2.openUni('uni-earth-828',true);const t=s=>document.querySelector('#atlas2 '+s);const txt=[...document.querySelectorAll('#atlas2 .a2-sec')].map(s=>(s.querySelector('h3')||{textContent:''}).textContent);
      const prim=t('.a2-sec-prim'),cro=t('.a2-sec-cro');const h4=[...document.querySelectorAll('#atlas2 h4.a2-sub')].map(h=>h.textContent);
      const chips=h=>{const x=[...document.querySelectorAll('#atlas2 h4.a2-sub')].find(e=>e.textContent.startsWith(h));return x?[...x.nextElementSibling.querySelectorAll('.a2-chip')].map(c=>c.getAttribute('data-go')+'|'+c.textContent):[]};
      return {txt,primEmpty:prim?prim.querySelector('.a2-empty').textContent:null,croRows:[...cro.querySelectorAll('.a2-row')].map(r=>r.textContent),h4,orig:chips('Originari'),pres:chips('Presenti'),
        legend:!!document.querySelector('#atlas2 .a2-legend'),info:document.querySelectorAll('#atlas2 .a2-info').length}}""")
    print(r)
    ck(any(x.startswith('Titoli di appartenenza (0)') for x in r['txt']) and 'in via esclusiva' in (r['primEmpty'] or ''),'Earth-828: nessun titolo di appartenenza esclusiva (stato vuoto esplicito)')
    ck(len(r['croRows'])==1 and 'N°125' in r['croRows'][0] and 'insieme a: MCU' in r['croRows'][0] and "Ambientazione: anni '60 stilizzati" in r['croRows'][0],'Earth-828: N°125 in Crossover, con altro universo e Ambientazione separata',r['croRows'])
    ck(len(r['orig'])==2 and any('franklin' in c for c in r['orig']) and any('galactus' in c for c in r['orig']),'Earth-828: originari = Franklin Richards, Galactus',r['orig'])
    ck(len(r['pres'])==4 and all('orig.:' in c for c in r['pres']) and any('reed-richards' in c for c in r['pres']),'Earth-828: 4 personaggi PRESENTI con origine altrove indicata (Reed, Sue, Ben, Johnny)',r['pres'])
    ck(r['legend'],'legenda delle categorie presente nella scheda universo')
    # MCU: nota di numerazione, nessun duplicato, nessuna associazione 616
    r=pg.evaluate("""(M)=>{tvaAtlas2.openUni(M,true);const A=JSON.parse(document.getElementById('atlasData').textContent);
      return {info:[...document.querySelectorAll('#atlas2 .a2-hero .a2-info-d')].map(x=>x.textContent),uni616:!!document.getElementById('uni-earth-616'),n:A.universi.length,
        go616:document.querySelectorAll('[data-go*="616"]').length,ids616:[...document.querySelectorAll('[id*="616"]')].map(e=>e.id).filter(i=>!/\\d616|616\\d/.test(i)),
        var:[...document.querySelectorAll('#atlas2 .a2-sec-var .a2-row')].map(b=>b.getAttribute('data-go')),
        prog:document.querySelector('#atlas2 .a2-prog-t').textContent}}""",MCU)
    ck(len(r['info'])==1 and 'Earth-199999' in r['info'][0] and 'Earth-616' in r['info'][0] and 'non sono state modificate' in r['info'][0],'MCU: nota esplicativa Earth-199999 / Earth-616',r['info'])
    ck(not r['uni616'] and r['n']==27 and r['go616']==0 and not r['ids616'],'nessuna scheda/duplicato/link «616»; 27 universi invariati',r)
    ck(r['var']==['item:item-133'],'MCU: versione alternativa N°133 elencata a parte (non conteggiata)',r['var'])
    ck('di cui 8 crossover' in r['prog'],'MCU: progresso distingue i crossover',r['prog'])
    pg.evaluate("()=>{tvaAtlas2.openHome()}"); pg.wait_for_timeout(100)
    pg.evaluate("()=>{const i=document.getElementById('a2HomeSearch');i.value='616';i.dispatchEvent(new Event('input',{bubbles:true}))}"); pg.wait_for_timeout(400)
    ck(pg.evaluate("()=>!!document.querySelector('#atlas2 .a2-res .a2-info')"),'ricerca «616» nell’Atlante 2.0 mostra la nota di numerazione')
    pg.evaluate("()=>{const i=document.getElementById('a2HomeSearch');i.value='';i.dispatchEvent(new Event('input',{bubbles:true}))}"); pg.wait_for_timeout(300)
    # schede titolo/personaggio in Timeline: etichette per ruolo
    r=pg.evaluate("""()=>{const k=id=>[...document.querySelectorAll('#'+id+' .tva-row .detail-k')].map(x=>x.textContent);return {p:k('item-001'),c:k('item-125'),v:k('item-133'),ch:k('char-reed-richards'),bl:k('char-blade')}}""")
    ck(r['p'].count('UNIVERSO DI APPARTENENZA')==1 and 'CROSSOVER · UNIVERSI COINVOLTI' in r['c'] and 'AMBIENTAZIONE' in r['c'] and 'UNIVERSO (VERSIONE ALTERNATIVA)' in r['v'],'schede titolo: etichette Appartenenza / Crossover / Versione alternativa + Ambientazione',r)
    ck('COMPARE ANCHE IN (ATLANTE)' in r['ch'] and 'ORIGINE (ATLANTE)' in r['ch'] and 'ORIGINE (ATLANTE)' in r['bl'],'schede personaggio: righe Origine / Compare anche in (Atlante)',r)
    # ---------- 2. bidirezionalita' ----------
    r=pg.evaluate("""()=>{const I=tvaIdx,out={};const gos=(root,k)=>[...new Set([...root.querySelectorAll('[data-go^="'+k+':"]')].map(a=>a.getAttribute('data-go').slice(k.length+1)))];
      const uids=JSON.parse(document.getElementById('atlasData').textContent).universi.map(u=>u.id);
      const iu=[],ui=[];Object.values(I.titoli).forEach(t=>{gos(t.li,'uni').forEach(u=>{const a2=I.titoliDi(u).map(e=>e.id).concat(I.varianti(u).map(e=>e.id));if(!a2.includes(t.id))iu.push(t.id+'>'+u)})});
      uids.forEach(u=>I.titoliDi(u).concat(I.varianti(u)).forEach(e=>{if(!gos(e.li,'uni').includes(u))ui.push(u+'>'+e.id)}));
      out.itemUni=[iu.length,ui.length];
      const cls=[];uids.forEach(u=>{const c=document.getElementById(u);const ids=gos(c,'item');const exp=I.titoliDi(u).concat(I.varianti(u)).map(e=>e.id);
        exp.forEach(i=>{if(!ids.includes(i))cls.push('mancante '+u+':'+i)});ids.forEach(i=>{if(!exp.includes(i))cls.push('extra '+u+':'+i)})});out.classico=cls.slice(0,6);
      const ic=[],ci=[];Object.values(I.titoli).forEach(t=>gos(t.li,'char').forEach(c=>{if(!gos(I.personaggi[c].li,'item').includes(t.id))ic.push(t.id+'>'+c)}));
      Object.values(I.personaggi).forEach(c=>gos(c.li,'item').forEach(i=>{if(!gos(I.titoli[i].li,'char').includes(c.id))ci.push(c.id+'>'+i)}));out.itemChar=[ic.length,ci.length];
      const cu=[],uc=[];Object.values(I.personaggi).forEach(c=>gos(c.li,'uni').forEach(u=>{const s=I.origineDi(u).concat(I.presentiDi(u));if(!s.includes(c.id))cu.push(c.id+'>'+u)}));
      uids.forEach(u=>I.origineDi(u).concat(I.presentiDi(u)).forEach(c=>{if(!gos(I.personaggi[c].li,'uni').includes(u))uc.push(u+'>'+c)}));out.charUni=[cu.length,uc.length,cu.slice(0,4),uc.slice(0,4)];
      const cc=[];uids.forEach(u=>{const card=document.getElementById(u);const g=gos(card,'char').sort();const e=I.origineDi(u).concat(I.presentiDi(u)).sort();if(JSON.stringify(g)!==JSON.stringify(e))cc.push(u+' '+g.length+'/'+e.length)});out.classicoChar=cc.slice(0,5);
      return out}""")
    print(r)
    ck(r['itemUni']==[0,0],'titolo <-> universo bidirezionale (varianti incluse, 139 + serie animate)',r['itemUni'])
    ck(not r['classico'],'scheda universo classica elenca esattamente gli stessi titoli (+ variante) della 2.0',r['classico'])
    ck(r['itemChar']==[0,0],'titolo <-> personaggio bidirezionale',r['itemChar'])
    ck(r['charUni'][:2]==[0,0],'personaggio <-> universo bidirezionale (origine + presenza)',r['charUni'])
    ck(not r['classicoChar'],'scheda universo classica elenca esattamente gli stessi personaggi (originari + presenti) della 2.0',r['classicoChar'])
    ck(not errs,'nessun errore JS (categorie/bidirezionalita)',errs)
    ctx.close()
    # ---------- 3. Indietro: filtri, ricerca, posizione ----------
    ctx,pg,errs=newpage()
    pg.evaluate("()=>{window.scrollTo(0,0)}")
    # baseline di salvataggi
    pg.evaluate("()=>{document.querySelector('.watch-check[data-item=\"001\"]').click();document.querySelector('.fav-star[data-item=\"003\"]').click()}"); pg.wait_for_timeout(400)
    LS="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.indexOf('tvaHomeMiss:')===0)continue;/* cache degli asset opzionali assenti, non dato utente */o[k]=localStorage.getItem(k)}return o}"
    ls0=pg.evaluate(LS)
    pg.evaluate("()=>{const s=document.getElementById('searchBox');s.value='man';s.dispatchEvent(new Event('input',{bubbles:true}))}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>document.querySelector('.filter-btn[data-tag=\"rosso\"]').click()"); pg.wait_for_timeout(300)
    ls1=pg.evaluate(LS)       # dopo le azioni dell'utente (i filtri si salvano da soli)
    ST="""()=>{const vis=[...document.querySelectorAll('li.card-wrap[id^="item-"]')].filter(l=>l.style.display!=='none').map(l=>l.id);
      return {q:document.getElementById('searchBox').value,off:[...document.querySelectorAll('.filter-btn.off')].map(b=>b.dataset.tag||b.dataset.studio||b.dataset.type||b.id).sort(),nvis:vis.length,vis:vis.join(),y:pageYOffset,
        fl:JSON.stringify(marvelFiltriStato())}}"""
    pg.evaluate("()=>{const l=[...document.querySelectorAll('li.card-wrap[id^=\"item-\"]')].filter(l=>l.style.display!=='none');window.__first=l[Math.min(6,l.length-1)].id;document.getElementById(window.__first).scrollIntoView({block:'start'});window.scrollBy(0,-90)}"); pg.wait_for_timeout(500)
    s0=pg.evaluate(ST); top0=pg.evaluate("()=>document.getElementById(window.__first).getBoundingClientRect().top")
    print('stato iniziale',{k:s0[k] for k in ('q','off','nvis','y')})
    ck(s0['q']=='man' and 'rosso' in s0['off'] and s0['nvis']>0,'prerequisito: ricerca «man» + priorita\' rosso nascosta attive')
    # Timeline -> chip universo (apre l'Atlante 2.0) -> riga titolo nascosto da ricerca/filtro -> Timeline
    pg.evaluate("()=>{const li=document.getElementById(window.__first);li.querySelector('details').setAttribute('open','');}"); pg.wait_for_timeout(200)
    ok=pg.evaluate("()=>{const a=document.getElementById(window.__first).querySelector('[data-go^=\"uni:\"]');if(!a)return false;a.click();return true}"); pg.wait_for_timeout(700)
    st=pg.evaluate("()=>({a2:atlas2Toggle.checked,depth:tvaNavStato().depth})"); ck(ok and st['a2'] and st['depth']==1,'Timeline -> Atlante 2.0 (depth 1)',st)
    # nell'Atlante: il primo titolo di appartenenza che la ricerca «man» nasconde
    tgt=pg.evaluate("""()=>{const rows=[...document.querySelectorAll('#atlas2 .a2-sec-prim .a2-row')];for(const r of rows){const id=r.getAttribute('data-go').split(':')[1];const li=document.getElementById(id);if(li&&li.style.display==='none'&&!li.closest('.tva-archives-overlay'))return id}return null}""")
    ck(tgt is not None,'esiste un titolo dell’universo nascosto dai filtri attivi',tgt)
    pg.evaluate("(id)=>{document.querySelector('#atlas2 [data-go=\"item:'+id+'\"]').click()}",tgt); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{const b=document.getElementById('d4Scheda');if(b)b.click()}"); pg.wait_for_timeout(1500)  # Fase 4: il chip N° apre il Dossier Opera; la scheda si raggiunge da 'Scheda in guida'
    r=pg.evaluate("""(id)=>{const li=document.getElementById(id);const r=li.getBoundingClientRect();return {vis:(li.offsetParent!==null&&li.style.display!=='none')||li.classList.contains('td-page'),top:r.top,depth:tvaNavStato().depth,q:document.getElementById('searchBox').value,a2:atlas2Toggle.checked}}""",tgt)
    ck(r['vis'] and r['depth']==3 and not r['a2'] and r['top']<400,'link a titolo nascosto: la scheda viene mostrata (filtri responsabili azzerati)',r)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1200)  # Fase 4: scheda -> Dossier Opera
    ls2=pg.evaluate(LS)
    chg=[k for k in set(ls1)|set(ls2) if ls1.get(k)!=ls2.get(k) and k!='marvel-ultimate-timeline-auto-backup']   # auto-backup: copia di sicurezza ritardata scritta dall'app dopo la spunta iniziale, non dalla navigazione
    ck(not chg,'sbloccare la scheda non scrive nulla in localStorage (preferenze dei filtri salvate invariate)',chg)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1200)
    st=pg.evaluate("()=>({a2:atlas2Toggle.checked,depth:tvaNavStato().depth,scr:tvaAtlas2.stato().screen})"); ck(st['a2'] and st['depth']==1 and st['scr']=='uni','Back 1 -> scheda universo 2.0',st)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1800)
    s1=pg.evaluate(ST); top1=pg.evaluate("()=>document.getElementById(window.__first).getBoundingClientRect().top")
    ck(s1['q']==s0['q'] and s1['off']==s0['off'] and s1['vis']==s0['vis'],'Back 2: ricerca, filtri e schede visibili identici a prima',{'a':{k:s0[k] for k in('q','off','nvis')},'b':{k:s1[k] for k in('q','off','nvis')}})
    ck(abs(top1-top0)<=8 and pg.evaluate("()=>tvaNavStato().depth")==0,'Back 2: posizione di scorrimento ripristinata sulla stessa scheda',(top0,top1,s0['y'],s1['y']))
    ck(json.loads(s1['fl'])['q']=='man','marvelFiltriStato riflette il ripristino')
    ls3=pg.evaluate(LS); chg=[k for k in set(ls1)|set(ls3) if ls1.get(k)!=ls3.get(k) and k!='marvel-ultimate-timeline-auto-backup']
    ck(not chg,'dopo Indietro i salvataggi/filtri persistenti sono identici',chg)
    ck(not errs,'nessun errore JS (Indietro)',errs); ctx.close()
    # ---------- 3b. posizione dentro .a2-scroll ----------
    ctx,pg,errs=newpage()
    pg.evaluate("()=>{const l=document.getElementById('item-050');l.querySelector('details').setAttribute('open','');}")
    pg.evaluate("()=>tvaSettleScroll(document.getElementById('item-050'))"); pg.wait_for_timeout(2000)
    y0=pg.evaluate("()=>pageYOffset"); t0=pg.evaluate("()=>document.getElementById('item-050').getBoundingClientRect().top")
    pg.evaluate("()=>document.querySelector('#item-050 [data-go^=\"uni:\"]').click()"); pg.wait_for_timeout(700)
    pg.evaluate("(m)=>{tvaAtlas2.openUni(m,true)}",MCU) if pg.evaluate("()=>tvaAtlas2.stato().uid")!=MCU else None
    pg.wait_for_timeout(300)
    pg.evaluate("()=>{const s=document.querySelector('.a2-scroll');s.scrollTop=2300}"); pg.wait_for_timeout(300)
    rec=pg.evaluate("""()=>{const s=document.querySelector('.a2-scroll');const sr=s.getBoundingClientRect();const x=innerWidth/2;let e=document.elementFromPoint(x,sr.top+sr.height*0.5);const row=e.closest('.a2-row');
      window.__row=row.getAttribute('data-go');return {y:s.scrollTop,id:window.__row,top:row.getBoundingClientRect().top-sr.top,win:pageYOffset}}""")
    print('a2 prima del click',rec)
    ck(rec['y']>1500,'Atlante 2.0 scorso in profondita\' dentro .a2-scroll',rec)
    pg.evaluate("()=>document.querySelector('#atlas2 [data-go=\"'+window.__row+'\"]').click()"); pg.wait_for_timeout(1800)
    pg.evaluate("()=>{const b=document.getElementById('d4Scheda');if(b)b.click()}"); pg.wait_for_timeout(1500)  # Fase 4: il chip N° apre il Dossier Opera; la scheda si raggiunge da 'Scheda in guida'
    st=pg.evaluate("()=>({a2:atlas2Toggle.checked,depth:tvaNavStato().depth})"); ck(not st['a2'] and st['depth']>=1,'Atlante -> Film -> Timeline',st)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1200)  # Fase 4: scheda -> Dossier Opera
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1500)
    after=pg.evaluate("""()=>{const s=document.querySelector('.a2-scroll');const sr=s.getBoundingClientRect();const row=document.querySelector('#atlas2 [data-go="'+window.__row+'"]');
      return {a2:atlas2Toggle.checked,y:s.scrollTop,top:row?row.getBoundingClientRect().top-sr.top:null,win:pageYOffset,uid:tvaAtlas2.stato().uid}}""")
    print('a2 dopo Indietro',after)
    ck(after['a2'] and after['uid']==MCU and abs(after['y']-rec['y'])<=4 and abs(after['top']-rec['top'])<=4,'Back: .a2-scroll ripristinato (scrollTop e riga di riferimento), non solo window.pageYOffset',(rec,after))
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1500)
    t1=pg.evaluate("()=>document.getElementById('item-050').getBoundingClientRect().top")
    ck(abs(t1-t0)<=10 and not pg.evaluate("()=>atlas2Toggle.checked"),'Back finale: Timeline alla stessa posizione',(t0,t1))
    # home Atlante: ricerca + filtro + scroll -> scheda -> Indietro (freccia interna) 
    pg.evaluate("()=>{tvaAtlas2.openUniversi()}"); pg.wait_for_timeout(200)
    pg.evaluate("()=>{const f=[...document.querySelectorAll('#atlas2 .a2-f')].find(b=>/Autonomo/.test(b.textContent));f.click()}"); pg.wait_for_timeout(200)
    pg.evaluate("()=>{const s=document.querySelector('.a2-scroll');s.scrollTop=260}"); pg.wait_for_timeout(300)
    h0=pg.evaluate("()=>({y:document.querySelector('.a2-scroll').scrollTop,nat:tvaAtlas2.stato().nat})")
    pg.evaluate("()=>document.querySelector('#atlas2 .a2-card').click()"); pg.wait_for_timeout(300)
    pg.click('#atlas2 .a2-back'); pg.wait_for_timeout(500)
    h1=pg.evaluate("()=>({y:document.querySelector('.a2-scroll').scrollTop,nat:tvaAtlas2.stato().nat,scr:tvaAtlas2.stato().screen})")
    ck(h1['scr']=='universi' and h1['nat']==h0['nat'] and abs(h1['y']-h0['y'])<=4,'Atlante 2.0: freccia interna ripristina filtro e scorrimento della panoramica',(h0,h1))
    ck(not errs,'nessun errore JS (.a2-scroll)',errs); ctx.close()
    # ---------- 4. stack, history.pushState, gesto Indietro ----------
    ctx,pg,errs=newpage()
    H="()=>({d:tvaNavStato().depth,a2:atlas2Toggle.checked,uid:tvaAtlas2.stato().uid,hl:history.length,hs:history.state&&history.state.tva})"
    pg.evaluate("()=>tvaGo('uni','uni-earth-828')"); pg.wait_for_timeout(500)
    pg.evaluate("()=>tvaGo('item','item-125')"); pg.wait_for_timeout(1500)
    pg.evaluate("()=>tvaGo('char','char-peter-parker')"); pg.wait_for_timeout(1500)
    s=pg.evaluate(H); ck(s['d']==3,'tre livelli nello stack',s)
    seq=[]
    for i in range(3):
        pg.evaluate("()=>history.back()"); pg.wait_for_timeout(1700); seq.append(pg.evaluate(H))
    print('gesto indietro x3',seq)
    ck([x['d'] for x in seq]==[2,1,0] and seq[1]['a2'] and seq[1]['uid']=='uni-earth-828' and not seq[2]['a2'],'gesto/tasto Indietro del browser: un livello alla volta, fino alla Timeline',seq)
    # frammento: non deve consumare lo stack
    pg.evaluate("()=>tvaGo('uni','uni-earth-828')"); pg.wait_for_timeout(500); d0=pg.evaluate(H)
    pg.evaluate("()=>{location.hash='#parte2'}"); pg.wait_for_timeout(500); d1=pg.evaluate(H)
    ck(d1['d']==d0['d'],'cambio di #frammento non estrae livelli dallo stack',(d0,d1))
    pg.evaluate("()=>history.back()"); pg.wait_for_timeout(600); d2=pg.evaluate(H)
    ck(d2['d']==d0['d'],'Indietro dal frammento torna alla voce del livello (nessun ripristino spurio)',d2)
    pg.evaluate("()=>history.back()"); pg.wait_for_timeout(1500); d3=pg.evaluate(H)
    ck(d3['d']==0 and not d3['a2'],'ulteriore Indietro ripristina il livello',d3)
    # azzeramento da tab: voci history orfane consumate senza effetti, nuova navigazione funziona
    pg.evaluate("()=>tvaGo('uni','uni-earth-828')"); pg.wait_for_timeout(500)
    pg.evaluate("()=>tvaGo('item','item-125')"); pg.wait_for_timeout(1500)
    pg.click('.app-tab[data-tab="timeline"]'); pg.wait_for_timeout(500)
    d4=pg.evaluate(H); ck(d4['d']==0 and pg.evaluate("()=>document.getElementById('tvaBackBtn').hidden"),'tab di primo livello azzera lo stack',d4)
    pg.evaluate("()=>history.back()"); pg.wait_for_timeout(600); d5=pg.evaluate(H)
    ck(d5['d']==0 and not d5['a2'],'voce history orfana consumata senza ripristini',d5)
    pg.evaluate("()=>tvaGo('uni','uni-earth-96283-raimi-verse')"); pg.wait_for_timeout(500)
    pg.evaluate("()=>history.back()"); pg.wait_for_timeout(1500); d6=pg.evaluate(H)
    ck(d6['d']==0 and not d6['a2'],'dopo voci orfane la nuova navigazione e il suo Indietro restano corretti',d6)
    # passaggi ripetuti + limite stack
    t=time.time(); bad=0
    for i in range(25):
        pg.evaluate("()=>tvaGo('uni','uni-earth-828')"); pg.wait_for_timeout(120)
        pg.evaluate("()=>tvaGo('item','item-125')"); pg.wait_for_timeout(250)
        pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(250)
        pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(300)
        x=pg.evaluate(H)
        if x['d']!=0 or x['a2']: bad+=1
    ck(bad==0,'25 cicli Timeline->Atlante->Film->Indietro x2: sempre depth 0 e Timeline',bad)
    for i in range(46):
        pg.evaluate("(i)=>tvaGo(i%2?'item':'uni',i%2?'item-125':'uni-earth-828')",i); pg.wait_for_timeout(60)
    x=pg.evaluate(H); ck(x['d']==40,'limite stack 40 rispettato',x)
    n=0
    while pg.evaluate("()=>tvaNavStato().depth")>0 and n<60:
        pg.evaluate("()=>history.back()"); pg.wait_for_timeout(260); n+=1
    x=pg.evaluate(H); ck(x['d']==0,'46 passaggi consumati dal gesto Indietro senza blocchi',(x,n))
    ck(not errs,'nessun errore JS (history)',errs)
    ctx.close()
    # ---------- 5. tabbar ::after ----------
    for (w,h) in ((320,568),(390,844),(430,932),(844,390)):
        ctx,pg,errs=newpage(w,h)
        r=pg.evaluate("""()=>{const b=document.getElementById('appTabbar'),R=document.documentElement;const a=getComputedStyle(b,'::after');const rect=b.getBoundingClientRect();
          const m={bottomGap:innerHeight-rect.bottom,afterH:a.height,afterTop:a.top,afterPE:a.pointerEvents,sh:R.scrollHeight,sw:R.scrollWidth,cw:R.clientWidth,bg:a.backgroundColor,barBg:getComputedStyle(b).backgroundColor,pos:getComputedStyle(b).position};
          R.classList.add('tva-no-ext');m.shOff=R.scrollHeight;m.afterOff=getComputedStyle(b,'::after').display;R.classList.remove('tva-no-ext');return m}""")
        ck(abs(r['bottomGap'])<0.5 and r['afterH']=='160px' and r['afterPE']=='none' and r['sh']==r['shOff'] and r['sw']<=r['cw'] and r['afterOff']=='none' and r['bg']==r['barBg'],'[%dx%d] tabbar: bordo = fondo viewport; ::after non altera scroll/hit-test e si disattiva'%(w,h),r)
        ctx.close()
    b.close()
print('FAILS',len(fails),fails)
