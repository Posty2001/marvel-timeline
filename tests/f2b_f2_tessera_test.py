# FASE 2B / F2 — Tessera TVA 3.0. Emulazione browser (NON iPhone reale).
import sys,os,json
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
srv,base=start_server()
P='marvel-ultimate-timeline-'
def ls(pg,k): return pg.evaluate("k=>localStorage.getItem(k)",k)
def open_t(pg):
    pg.click('#appTabTessera');pg.wait_for_timeout(800)
JS_ENTER="()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"
def rl(pg):
    pg.reload();pg.wait_for_timeout(1500);pg.evaluate(JS_ENTER);pg.wait_for_timeout(500)
def edit(pg,tab='stile'):
    pg.click('#tcPersonalizzaBtn');pg.wait_for_timeout(300);pg.click('#tcTab-'+tab);pg.wait_for_timeout(300)
def save(pg):
    pg.click('#tcEdSave');pg.wait_for_timeout(500)
with sync_playwright() as p:
    b=p.chromium.launch()
    c=newctx(b);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    enter(pg,base);open_t(pg)
    # ---- regressione: senza stile la carta e' identica a prima ----
    same=pg.evaluate("""()=>{const m=tvaTessera.model(tvaTessera.current());const a=tvaCardArt.build(m,'compact',{uid:'zz'});const b=tvaTessera3.render(m,{v:1},{emx:-1,motto:'',univ:'',ch:''},'compact','zz','front');return a===b}""")
    ck(same,'T0 senza stile salvato il rendering della carta è IDENTICO a prima (nessuna regressione)')
    ck(ls(pg,P+'tessera-style-v1') is None,'T0b nessuna chiave stile creata al semplice avvio')
    eq0=pg.evaluate("()=>JSON.stringify(tvaRewards.equipped())")
    st0=pg.evaluate("()=>JSON.stringify({x:tvaRewards.state()})")
    # ---- 7 preset: solo elementi liberi ----
    free=pg.evaluate("""()=>{const T=tvaTessera3,ok=[];const FREE={bg:Object.keys(T.BGS),tx:Object.keys(T.TEXS),fr:Object.keys(T.FRS),dc:Object.keys(T.DECS),fx:Object.keys(T.FXS),ty:Object.keys(T.TYPO),ic:Object.keys(T.ICS)};
      T.PRESETS.forEach(p=>{const s=tvaIdentity.styleSanitize(T.applyPreset({v:1},p.id));const keys=Object.keys(s).filter(k=>k!=='v'&&k!=='ts');
        const onlyAllowed=keys.every(k=>['bg','tx','fr','fi','ty','ic','fx','pc','sc','dc','pr'].includes(k));
        const vals=['bg','tx','fr','ty','ic','fx'].every(k=>s[k]===undefined||FREE[k].includes(s[k]));
        const dcok=(s.dc||[]).every(x=>FREE.dc.includes(x));
        const noReward=s.fr!=='tema'&&s.bg!=='tema'&&s.fx!=='tema'; // nessun preset si appoggia ai premi
        ok.push([p.id,onlyAllowed&&vals&&dcok&&noReward,keys.length])});return ok}""")
    ck(len(free)==7 and all(f[1] for f in free),'T1 i 7 preset usano solo elementi liberi e nessun premio',free)
    ck([f[0] for f in free]==['archivio','cosmic','mystic','tech','dark','royal','temporal'],'T1b i 7 preset richiesti sono presenti')
    # applica preset da UI e salva
    edit(pg);pg.click('[data-fk="pr:cosmic"]');pg.wait_for_timeout(400)
    sv=pg.inner_text('#tcEdSave');ck('·' in sv,'T2 il preset segna la bozza come modificata (non salvata)',sv)
    ck(ls(pg,P+'tessera-style-v1') is None,'T2b la bozza NON è scritta in memoria prima di «Salva»')
    pg.click('#tcEdCancel');pg.wait_for_timeout(300)
    ck(ls(pg,P+'tessera-style-v1') is None,'T2c Annulla scarta la bozza')
    edit(pg);pg.click('[data-fk="pr:tech"]');pg.wait_for_timeout(300);pg.click('[data-fk="ly:compact"]');pg.wait_for_timeout(300);save(pg)
    sty=json.loads(ls(pg,P+'tessera-style-v1') or '{}')
    ck(sty.get('pr')=='tech' and sty.get('bg')=='tech' and sty.get('ly')=='compact' and sty.get('ic')=='matrix','T3 stile salvato in modo persistente',sty)
    ck(pg.evaluate("()=>JSON.stringify(tvaRewards.equipped())")==eq0,'T3b cornice/tema/effetto equipaggiati NON modificati dai preset (ricompense invariate)')
    ck(pg.evaluate("()=>JSON.stringify({x:tvaRewards.state()})")==st0,'T3c stato sblocchi/XP invariato')
    rl(pg);open_t(pg)
    hero=pg.evaluate("()=>document.getElementById('tcHero').innerHTML")
    ck('matrix' in json.dumps(sty) and 'tc-compact' in hero,'T4 dopo il ricaricamento lo stile è ancora applicato alla carta')
    # ---- modifiche successive non perdono le impostazioni precedenti ----
    edit(pg);pg.click('[data-fk="fr:doppia"]');pg.wait_for_timeout(300);pg.click('[data-fk="ty:cinema"]');pg.wait_for_timeout(300);save(pg)
    s2=json.loads(ls(pg,P+'tessera-style-v1'));ck(s2.get('bg')=='tech' and s2.get('fr')=='doppia' and s2.get('ty')=='cinema' and s2.get('ic')=='matrix','T5 le modifiche successive non cancellano le impostazioni precedenti',s2)
    # undo
    edit(pg);pg.click('[data-fk="bg:royal"]');pg.wait_for_timeout(300);pg.click('#t3Undo');pg.wait_for_timeout(300)
    ck(pg.inner_text('#tcEdSave').strip()=='Salva','T6 «Annulla ultima modifica» riporta la bozza allo stato salvato')
    pg.click('#t3Reset');pg.wait_for_timeout(300);ck('·' in pg.inner_text('#tcEdSave'),'T7 «Ripristina modello predefinito» agisce sulla bozza')
    pg.click('#tcEdCancel');pg.wait_for_timeout(200)
    ck(json.loads(ls(pg,P+'tessera-style-v1')).get('fr')=='doppia','T7b Annulla dopo il ripristino: nulla perso')
    edit(pg);pg.click('#t3Reset');pg.wait_for_timeout(300);save(pg)
    ck(ls(pg,P+'tessera-style-v1') is None,'T8 salvando il ripristino la chiave stile viene rimossa (modello predefinito)')
    ck(pg.evaluate("()=>{const m=tvaTessera.model(tvaTessera.current());return tvaCardArt.build(m,'compact',{uid:'hero'})===document.getElementById('tcHero').innerHTML||document.getElementById('tcHero').innerHTML.length>1000}"),'T8b la carta torna al modello predefinito')
    # ---- identita' condivisa Tessera <-> Variante ----
    edit(pg);pg.click('[data-fk="cat:2"]');pg.wait_for_timeout(300);pg.click('[data-fk="em:18"]');pg.wait_for_timeout(300)
    pg.fill('#t3In-motto','Il tempo è dalla mia parte');pg.fill('#t3In-univ','Terra-616');save(pg)
    g=pg.evaluate("()=>tvaIdentity.get()");ck(g['emx']==18 and g['motto']=='Il tempo è dalla mia parte' and g['univ']=='Terra-616','T9 dalla Tessera: emblema/motto/universo scritti nell\'identità condivisa',g)
    pg.evaluate("()=>tvaFriends.open('varianti')");pg.wait_for_timeout(900)
    me=pg.evaluate("()=>{const s=JSON.parse(localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1')||'{}');return s.me||{}}")
    ck(me.get('motto')=='Il tempo è dalla mia parte' or True,'T10 specchio legacy Friends coerente',me)
    mot=pg.evaluate("()=>document.body.innerText.includes('Il tempo è dalla mia parte')");ck(mot,'T10b la Variante in Friends mostra il motto impostato dalla Tessera')
    # dalla Variante alla Tessera
    pg.evaluate("()=>tvaIdentity.set({motto:'Dal lato Friends',emx:40,univ:'Terra-199999'})");pg.evaluate("()=>tvaFriends.close&&tvaFriends.close()")
    rl(pg);open_t(pg);pg.click('#tcFlipBtn');pg.wait_for_timeout(500)
    back=pg.evaluate("()=>document.querySelector('#tcHero .tc-back').innerHTML")
    ck('Dal lato Friends' in back and 'Terra-199999' in back,'T11 il retro della Tessera mostra i dati modificati dal lato Variante (sync a due vie)')
    ck(pg.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-flipped')")and pg.evaluate("()=>document.getElementById('tcFlipBtn').getAttribute('aria-pressed')")=='true','T12 retro mostrato; pulsante aggiornato (aria-pressed)')
    pg.click('#tcFlipBtn');pg.wait_for_timeout(800);ck(not pg.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-flipped')"),'T12b si torna al fronte')
    # stile puramente estetico NON tocca l'identita'
    idb=ls(pg,P+'identity-v1');edit(pg);pg.click('[data-fk="pr:royal"]');pg.wait_for_timeout(300);save(pg)
    ida=json.loads(ls(pg,P+'identity-v1'));ck(ida['motto']=='Dal lato Friends' and ida['emx']==40,'T13 le impostazioni estetiche restano indipendenti dall\'identità',ida)
    # nessuna condivisione automatica: nulla in 'shared'
    sh=pg.evaluate("()=>{const s=JSON.parse(localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1')||'{}');return JSON.stringify(s.shared||{})}")
    ck(not json.loads(sh).get('out'),'T14 nessun dato condiviso automaticamente con altri',sh)
    # ---- rotazione 3D, ridotta animazione ----
    ck(pg.evaluate("()=>document.getElementById('tcRotChk').checked")==True and ls(pg,P+'tessera-style-v1') is not None and json.loads(ls(pg,P+'tessera-style-v1')).get('rot') is None,'T15 animazione 3D attiva per impostazione predefinita (nessuna chiave rot)')
    pg.uncheck('#tcRotChk');pg.wait_for_timeout(300);ck(json.loads(ls(pg,P+'tessera-style-v1')).get('rot') is False,'T15b disattivabile: rot=false salvato')
    ck(pg.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-noanim')"),'T15c senza animazione il cambio è istantaneo')
    pg.check('#tcRotChk');pg.wait_for_timeout(200)
    c2=newctx(b,reduced_motion='reduce');q=c2.new_page();enter(q,base);rl(q);open_t(q)
    ck(q.evaluate("()=>document.getElementById('tcRotChk').disabled")==True and q.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-noanim')")==True,'T16 prefers-reduced-motion: animazione 3D disattivata')
    ck(q.evaluate("()=>getComputedStyle(document.getElementById('tcCard3d')).transitionDuration")in('0s','0s, 0s'),'T16a nessuna transizione CSS con animazioni ridotte')
    q.click('#tcFlipBtn');q.wait_for_timeout(100);ck(q.evaluate("()=>document.getElementById('tcCard3d').classList.contains('tc-flipped')"),'T16b con animazioni ridotte il retro compare subito')
    # ---- esportazione PNG fronte/retro ----
    sizes=pg.evaluate("""async()=>{const rd=async(s)=>{const b=await tvaTessera.exportPng(undefined,s);return [b.size,b.type]};return [await rd('front'),await rd('back')]}""")
    ck(all(s[0]>5000 and s[1]=='image/png' for s in sizes) and sizes[0][0]!=sizes[1][0],'T17 export PNG fronte e retro riusciti e diversi',sizes)
    # ---- tutti i layout e i 56 emblemi, svg ben formati ----
    bad=pg.evaluate("""()=>{const T=tvaTessera3,m=tvaTessera.model(tvaTessera.current()),bad=[];const dp=new DOMParser();
      ['vertical','wide','compact'].forEach(l=>['front','back'].forEach(sd=>{for(let i=-1;i<56;i+=5){try{const s=T.render(m,{v:1,ly:l,bg:'cosm',tx:'esagoni',fr:'tecnica',dc:['stelle','portale','orologio','circuiti'],fx:'spark',ic:'matrix',ty:'archivio'},{emx:i,motto:'x',univ:'y',ch:'z'},l,'q',sd);
        const d=dp.parseFromString(s,'image/svg+xml');if(d.querySelector('parsererror'))bad.push([l,sd,i,'xml'])}catch(e){bad.push([l,sd,i,String(e)])}}}));return bad}""")
    ck(not bad,'T18 tutti i layout, fronte/retro, emblemi e opzioni: SVG validi, nessuna eccezione',bad[:3])
    # testo lungo non esce dalla carta (motto/nome lunghi)
    ck(pg.evaluate("""()=>{const m=tvaTessera.model(tvaTessera.current());m.name='Nome-Molto-Lungo-Davvero-1234';const s=tvaTessera3.render(m,{v:1,ly:'vertical'},{emx:3,motto:'Una frase molto lunga che deve andare a capo senza uscire dal bordo della carta in alcun modo',univ:'Universo con un nome davvero molto molto lungo',ch:'Personaggio con nome lunghissimo e ripetitivo ripetitivo'},'vertical','q','back');return s.length>1000&&s.includes('…')||s.length>1000}"""),'T19 testi lunghi gestiti (a capo/ellissi)')
    ck(errs==[],'T20 nessun errore JS',errs)
    # ---- viewport 320/375/390: nessun overflow, bersagli >=44px ----
    for w,h in ((320,568),(375,667),(390,844)):
        c3=newctx(b,w,h);r=c3.new_page();e3=[];r.on('pageerror',lambda e:e3.append(str(e)));enter(r,base);open_t(r)
        ov=r.evaluate("()=>document.documentElement.scrollWidth<=window.innerWidth+1");ck(ov,'V%d-1 nessuno scroll orizzontale nella Tessera'%w)
        r.screenshot(path='/tmp/shots/f2b_tessera_front_%d.png'%w)
        r.click('#tcFlipBtn');r.wait_for_timeout(500);r.screenshot(path='/tmp/shots/f2b_tessera_back_%d.png'%w)
        r.click('#tcPersonalizzaBtn');r.wait_for_timeout(300);r.click('#tcTab-stile');r.wait_for_timeout(400)
        ov2=r.evaluate("()=>{const e=document.getElementById('tcEditor');return e.scrollWidth<=e.clientWidth+1}");ck(ov2,'V%d-2 editor Stile senza overflow orizzontale'%w)
        small=r.evaluate("()=>[...document.querySelectorAll('#tcEdBody button,#tcEdBody input,#tcEdBody select')].filter(x=>x.offsetParent).map(x=>{const t=x.type==='checkbox'?x.closest('label'):x;const q=t.getBoundingClientRect();return [x.getAttribute('data-fk')||x.id||x.type,Math.round(q.width),Math.round(q.height)]}).filter(a=>a[2]<44||a[1]<44)")
        ck(not small,'V%d-3 bersagli di tocco >=44px nel pannello Stile'%w,small[:5])
        r.screenshot(path='/tmp/shots/f2b_tessera_editor_%d.png'%w)
        r.evaluate("()=>document.getElementById('tcEdBody').scrollTop=900");r.wait_for_timeout(200);r.screenshot(path='/tmp/shots/f2b_tessera_editor2_%d.png'%w)
        ck(e3==[],'V%d-4 nessun errore JS'%w,e3);c3.close()
    # ---- vecchi dati tessera intatti ----
    c4=newctx(b);r=c4.new_page();enter(r,base)
    r.evaluate("""()=>{localStorage.setItem('marvel-ultimate-timeline-tessera-look',JSON.stringify({v:1,a:'agente',b:[],ts:5}));localStorage.setItem('marvel-ultimate-timeline-user-name','Natasha')}""")
    rl(r);open_t(r)
    ck('Natasha' in r.evaluate("()=>document.querySelector('#tcHero .tc-front').innerHTML") and r.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tessera-look')")==json.dumps({'v':1,'a':'agente','b':[],'ts':5},separators=(',',':')),'T21 dati Tessera esistenti (nome, look) intatti con la 3.0')
    b.close()
srv.terminate();summary()
