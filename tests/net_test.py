import json,sys
from playwright.sync_api import sync_playwright
F=sys.argv[1] if len(sys.argv)>1 else 'file:///home/claude/work/index.html'
fails=[]
def ck(c,m,info=''):
    print(('PASS ' if c else 'FAIL ')+m,info if not c else '')
    if not c: fails.append(m)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':390,'height':844}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pass
    pg.set_default_timeout(8000); pg.goto(F); pg.wait_for_timeout(900)
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true}"); pg.wait_for_timeout(300)
    # --- struttura / integrità dei link
    r=pg.evaluate("""()=>{const gos=[...document.querySelectorAll('[data-go]')];const bad=[];const kinds={};
      gos.forEach(a=>{const [k,...r]=a.getAttribute('data-go').split(':');const id=r.join(':');kinds[k]=(kinds[k]||0)+1;
        if(k==='arc'){const M=tvaAtlas2.arcModel();const [c,...e]=r;const ee=e.join(':');if(c==='pot'){if(!document.getElementById(ee)||tvaAtlas2.potTier(ee)==null) bad.push(a.getAttribute('data-go'));}else if(!(M.byId[ee]&&M.byId[ee].cat===c)) bad.push(a.getAttribute('data-go'));}
        else if(!document.getElementById(id)) bad.push(a.getAttribute('data-go'));});
      return {n:gos.length,kinds,bad:bad.slice(0,10),nb:bad.length,
      tvaIdx:!!window.tvaIdx,back:!!document.getElementById('tvaBackBtn'),
      lkItems:document.querySelectorAll('li.card-wrap[id^=item-][data-tva-linked]').length,
      uniCards:document.querySelectorAll('li[id^=uni-][data-tva-net]').length}}""")
    print(r)
    ck(r['nb']==0,'tutti i data-go puntano a un ID esistente',r['bad'])
    ck(r['uniCards']==27,'27 schede universo arricchite',r['uniCards'])
    ck(r['kinds'].get('item',0)>600,'link N° verso titoli',r['kinds'])
    ck(not errs,'nessun errore JS',errs)
    # testo delle schede invariato (textContent dei detail-v APP.)
    # --- Anim: filtro universo ora include le serie animate certe
    pg.evaluate("()=>window.marvelEsploraUniverso('uni-x-men-97-verse','X-Men 97')"); pg.wait_for_timeout(300)
    vis=pg.evaluate("()=>[...document.querySelectorAll('li.card-wrap')].filter(l=>!l.closest('.tva-archives-overlay')&&l.offsetParent!==null).map(l=>l.id)")
    exp=pg.evaluate("()=>{const a=JSON.parse(document.getElementById('atlasData').textContent);return a.animate.filter(x=>x.universi.includes('uni-x-men-97-verse')).map(x=>x.id)}")
    ck(sorted(vis)==sorted(exp+[i for i in vis if i.startswith('item-')]),'X-Men97: anim = atlas',(vis,exp))
    pg.evaluate("()=>window.marvelUniFiltroReset()")
    # --- navigazione: Timeline -> Film -> Universo (Atlante) -> Film -> Back x2
    pg.evaluate("()=>window.scrollTo(0,0)")
    pg.evaluate("()=>tvaSettleScroll(document.getElementById('item-125'))"); pg.wait_for_timeout(2500)
    y0=pg.evaluate("()=>pageYOffset"); t0=pg.evaluate("()=>document.getElementById('item-125').getBoundingClientRect().top")
    pg.evaluate("()=>window.tvaTd2?tvaTd2.open('item-125',{fromTimeline:true,restoring:true}):document.querySelector('#item-125 details').setAttribute('open','')")
    chip=pg.query_selector("#item-125 [data-go='uni:uni-earth-828']"); ck(chip is not None,'scheda 125 ha chip Earth-828')
    chip.scroll_into_view_if_needed(); chip.click(); pg.wait_for_timeout(900)
    st=pg.evaluate("()=>({a2:atlas2Toggle.checked,classic:tvaArchivesToggle.checked,tab:document.querySelector('.app-tab-active')?.dataset.tab,back:!document.getElementById('tvaBackBtn').hidden,depth:tvaNavStato().depth,scr:tvaAtlas2.stato().screen,uid:tvaAtlas2.stato().uid})")
    print(st); ck(st['a2'] and not st['classic'] and st['back'] and st['depth']==1 and st['tab']=='atlante' and st['scr']=='uni' and st['uid']=='uni-earth-828','Timeline→Universo apre Atlante 2.0 sulla scheda',st)
    t=pg.query_selector("#atlas2 [data-go='item:item-125']"); ck(t is not None,'scheda universo→titolo 125')
    t.scroll_into_view_if_needed(); t.click(); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{const b=document.getElementById('d4Scheda');if(b)b.click()}"); pg.wait_for_timeout(1200)  # Fase 4: N° -> Dossier Opera -> Scheda in guida
    st=pg.evaluate("()=>({a2:atlas2Toggle.checked,tab:document.querySelector('.app-tab-active')?.dataset.tab,depth:tvaNavStato().depth,top:document.getElementById('item-125').getBoundingClientRect().top,open:document.querySelector('#item-125 details').open})")
    print(st); ck((not st['a2']) and st['depth']==3 and st['tab']=='timeline' and st['open'] and abs(st['top'])<120,'Universo→Film apre la Timeline sulla scheda',st)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(900)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(900)
    st=pg.evaluate("()=>({a2:atlas2Toggle.checked,depth:tvaNavStato().depth,scr:tvaAtlas2.stato().screen,uid:tvaAtlas2.stato().uid})")
    ck(st['a2'] and st['depth']==1 and st['scr']=='uni' and st['uid']=='uni-earth-828','Back 1 → scheda universo 2.0',st)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1200)
    st=pg.evaluate("()=>({a2:atlas2Toggle.checked,depth:tvaNavStato().depth,hid:document.getElementById('tvaBackBtn').hidden})")
    t1=pg.evaluate("()=>document.getElementById('item-125').getBoundingClientRect().top")
    ck((not st['a2']) and st['depth']==0 and st['hid'] and abs(t1-t0)<12,'Back 2 → Timeline stessa posizione (scheda 125)',(st,y0,t0,t1))
    # --- personaggio → apparizioni → film → back
    pg.evaluate("()=>tvaGo('char','char-peter-parker')"); pg.wait_for_timeout(1200)
    a=pg.query_selector("#char-peter-parker a.tva-lk[data-go='item:item-089']"); ck(a is not None,'Peter Parker ha link N°089')
    if a:
        a.scroll_into_view_if_needed(); a.click(); pg.wait_for_timeout(900)
        ck(pg.evaluate("()=>!tvaArchivesToggle.checked&&document.getElementById('item-089').getBoundingClientRect().top<150"),'Personaggio→Film apre la scheda 089')
        pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(900)
        ck(pg.evaluate("()=>tvaArchivesToggle.checked&&document.querySelector('#char-peter-parker details').open"),'Back → scheda personaggio ancora aperta')
        # missioni
    pg.evaluate("()=>window.marvelUniFiltroReset()")
    for _ in range(6):
        if pg.evaluate("()=>tvaNavStato().depth")==0: break
        pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(700)
    # --- filtro preservato attraverso la navigazione
    pg.evaluate("()=>{window.marvelUniFiltroReset();window.marvelChiudiOverlay();}")
    pg.evaluate("()=>window.marvelEsploraUniverso('uni-earth-121698','Earth-121698')"); pg.wait_for_timeout(300)
    vis0=pg.evaluate("()=>[...document.querySelectorAll('li.card-wrap[id^=item-]')].filter(l=>l.offsetParent!==null).map(l=>l.id)")
    pg.evaluate("()=>{window.tvaTd2?tvaTd2.open('item-029',{fromTimeline:true}):document.querySelector('#item-029 details').setAttribute('open','')}")
    pg.query_selector("#item-029 [data-go^='uni:']").click(); pg.wait_for_timeout(800)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(900)
    st=pg.evaluate("()=>({f:marvelUniFiltroStato().uid,atl:tvaArchivesToggle.checked,vis:[...document.querySelectorAll('li.card-wrap[id^=item-]')].filter(l=>l.offsetParent!==null).map(l=>l.id),ban:document.getElementById('mvUniversoBanner').hidden})")
    ck(st['f']=='uni-earth-121698' and not st['atl'] and st['vis']==vis0 and not st['ban'],'Filtro universo preservato dopo andata/ritorno',st)
    # filtro attivo + vado a un titolo non appartenente → il filtro viene tolto
    pg.evaluate("()=>tvaGo('item','item-089')"); pg.wait_for_timeout(1200)
    st=pg.evaluate("()=>({f:marvelUniFiltroStato().uid,vis:document.getElementById('item-089').offsetParent!==null})")
    ck(st['f'] is None and st['vis'],'Titolo fuori filtro: filtro rimosso e scheda raggiunta',st)
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(900)
    ck(pg.evaluate("()=>marvelUniFiltroStato().uid")=='uni-earth-121698','Back ripristina il filtro universo')
    pg.evaluate("()=>window.marvelUniFiltroReset()")
    # --- progressi: universo mostra X/N
    pg.evaluate("()=>{const c=document.querySelector('#item-029 .watch-check');c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    txt=pg.evaluate("()=>document.querySelector('#uni-earth-121698 .tva-prog-t').textContent"); ck(txt.startswith('1/2'),'progresso universo 1/2',txt)
    # missioni -> titoli richiesti -> scheda
    pg.evaluate("()=>document.getElementById('appTabMissioni').click()"); pg.wait_for_timeout(900)
    mi=pg.evaluate("()=>({n:document.querySelectorAll('.tva-mis').length,txt:document.getElementById('missioneTematicaTesto').textContent,chips:[...document.querySelectorAll('.tva-mis [data-go]')].map(c=>c.getAttribute('data-go')),segreta:document.querySelectorAll('#missioneSegreta .tva-mis').length})")
    print(mi); ck(mi['n']>=1 and len(mi['chips'])>=1 and mi['segreta']==0,'Missioni: titoli richiesti con link (la segreta resta segreta)',mi)
    # i titoli proposti per la missione tematica appartengono davvero alla categoria
    cat_ok=pg.evaluate("()=>{const c=marvelMissioniInfo.tematica.cat;return marvelMissioniInfo.tematica.ids.every(id=>(document.getElementById('item-'+id).getAttribute('data-cats')||'').split(' ').includes(c))}")
    ck(cat_ok,'Missione tematica: tutti i titoli proposti hanno la categoria richiesta')
    cid=mi['chips'][0]
    pg.evaluate("g=>{const c=document.querySelector('.tva-mis [data-go=\"'+g+'\"]');c.scrollIntoView({block:'center'});}",cid); pg.wait_for_timeout(300)
    dy=pg.evaluate("()=>document.querySelector('.tva-mis').getBoundingClientRect().top")
    pg.evaluate("g=>document.querySelector('.tva-mis [data-go=\"'+g+'\"]').click()",cid); pg.wait_for_timeout(1300)
    tid=cid.split(':')[1]
    ck(pg.evaluate("t=>document.getElementById(t).getBoundingClientRect().top<150&&document.getElementById(t).offsetParent!==null",tid),'Missione → titolo richiesto → scheda in Timeline')
    pg.evaluate("()=>{const b=document.getElementById('tvaBackBtn');(document.querySelector('.td-page .td2-back')||(b.offsetParent!==null?b:document.querySelector('.a2-back'))).click()}"); pg.wait_for_timeout(1200)
    d2=pg.evaluate("()=>document.querySelector('.tva-mis').getBoundingClientRect().top")
    ck(abs(d2-dy)<12,'Back → di nuovo sulle Missioni nella stessa posizione',(dy,d2))
    # spunta XP/progressi: guardare il titolo non cambia altro che lo stato previsto
    # ricerca → risultato → scheda
    ck(not errs,'nessun errore JS finale',errs)
    b.close()
print('FAILS',len(fails),fails)
