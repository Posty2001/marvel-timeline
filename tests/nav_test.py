import json
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:8124/index.html'; res=[]; errs=[]
def ok(n,c,d=''):
    res.append((n,bool(c),d)); print(('PASS ' if c else 'FAIL ')+n+(' '+str(d) if (d and not c) else ''))
JS_STATE="""()=>{const g=i=>{const e=document.getElementById(i);return !!(e&&e.checked)};
 const vis=s=>{const e=document.querySelector(s);return !!e&&getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().height>0};
 const ov=['multiverseGraphToggle','universeTimelineToggle','altTimelineToggle','relationshipGraphToggle','kangTvaGraphToggle','tvaArchivesToggle','tesseraToggle','friendsToggle','infoOverlayToggle'].filter(g);
 return {a2:g('atlas2Toggle'),ov:ov,tab:vis('#appTabbar'),menu:vis('.sidebar-open-btn'),shell:vis('#tvaShell'),title:(document.querySelector('#tvaShell .ts-t')?getComputedStyle(document.querySelector('#tvaShell .ts-t'),'::before').content:''),
  home:vis('#homeHub'),a2vis:vis('#atlas2'),depth:window.tvaNavStato?window.tvaNavStato().depth:-1,
  legacyBack:(()=>{const e=document.querySelector('.mg-back-btn');return !!e&&e.offsetParent!==null&&getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().height>0})()}}"""
def st(pg): return pg.evaluate(JS_STATE)
def clickb(pg,rx,scope='#atlas2'):
    return pg.evaluate("([rx,sc])=>{const r=new RegExp(rx,'i');const b=[...document.querySelectorAll(sc+' button, '+sc+' a')].find(x=>r.test(x.textContent.trim())&&x.offsetParent!==null);if(!b)return false;b.click();return true}",[rx,scope])
def a2back(pg): pg.evaluate("()=>document.querySelector('#atlas2 .a2-back').click()"); pg.wait_for_timeout(500)
with sync_playwright() as p:
    b=p.chromium.launch(); ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block'); pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(1500)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    # 1 Home -> TVA Archives (card cinematografica)
    ok('Home visibile', st(pg)['home'])
    pg.evaluate("()=>document.getElementById('a2Entry').click()"); pg.wait_for_timeout(900); s=st(pg)
    ok('Home -> TVA Archives immersiva (no barra, no menu)', s['a2'] and s['a2vis'] and not s['tab'] and not s['menu'] and not s['ov'], s)
    # 2 Tutti gli archivi
    ok('click "Tutti gli archivi"', clickb(pg,'Indice completo')); pg.wait_for_timeout(700); s=st(pg)
    ok('Tutti gli archivi: nuova UI', s['a2'] and not s['ov'] and not s['tab'] and not s['menu'], s)
    # 3 Multiverso -> Grafico
    ok('click Multiverso', clickb(pg,'^Multiverso')); pg.wait_for_timeout(1000); s=st(pg)
    ok('Multiverso (3B): apre la nuova mappa', st(pg)['a2'] and pg.evaluate("()=>tvaAtlas2.stato().screen")=='mappa')
    pg.click('#mpLegenda'); pg.wait_for_timeout(300); pg.click('#mpClassic1'); pg.wait_for_timeout(1000); s=st(pg)
    ok('Multiverso: Grafico in shell TVA, nessuna barra/menu, nessun vecchio Indietro', s['ov']==['multiverseGraphToggle'] and s['shell'] and not s['tab'] and not s['menu'] and not s['legacyBack'], s)
    ok('Grafico: titolo header', 'Grafico del Multiverso' in s['title'], s['title'])
    ok('Grafico interattivo (rami presenti)', pg.evaluate("()=>!!document.querySelector('.mv-map-branch')"))
    pg.evaluate("()=>document.querySelector('.mv-map-branch').click()"); pg.wait_for_timeout(500)
    ok('Grafico: click su ramo senza errori / resta nella shell', st(pg)['shell'])
    pg.evaluate("()=>document.querySelector('#tvaShell .ts-back').click()"); pg.wait_for_timeout(800); s=st(pg)
    ok('Indietro dal grafico -> mappa (3B), non legacy', s['a2'] and not s['ov'] and not s['shell'] and pg.evaluate("()=>tvaAtlas2.stato().screen")=='mappa', s)
    pg.evaluate("()=>tvaBack()"); pg.wait_for_timeout(700); s=st(pg)
    ok('Indietro dalla mappa -> Tutti gli archivi', s['a2'] and not s['ov'] and pg.evaluate("()=>tvaAtlas2.stato().screen")=='catalogo', s)
    # 4 Artefatti -> Dettaglio
    ok('click Artefatti', clickb(pg,'^Artefatti')); pg.wait_for_timeout(700); s=st(pg)
    ok('Artefatti: nuova UI', s['a2'] and not s['ov'] and not s['tab'], s)
    n=pg.evaluate("()=>{const r=[...document.querySelectorAll('#atlas2 .a2-scroll button')].filter(b=>b.offsetParent&&!/Indietro|App Marvel/.test(b.textContent)&&b.closest('.a2-scroll'));return r.length}")
    ok('Artefatti: elenco con schede', n>2, n)
    pg.evaluate("()=>{const r=[...document.querySelectorAll('#atlas2 .a2-scroll button.a2-arcard')].filter(b=>b.offsetParent);r[0].click()}"); pg.wait_for_timeout(800); s=st(pg)
    ok('Artefatti -> Dettaglio: dossier nuova UI', s['a2'] and not s['ov'] and not s['tab'] and not s['menu'], s)
    # 5 Dossier -> collegamento ad altra sezione -> Indietro
    link=pg.evaluate("()=>{const c=[...document.querySelectorAll('#atlas2 [data-go]')].filter(x=>x.offsetParent);return c.length?c[0].getAttribute('data-go'):null}")
    print('link nel dossier:',link)
    if link:
        d0=st(pg)['depth']; pg.evaluate("()=>[...document.querySelectorAll('#atlas2 [data-go]')].filter(x=>x.offsetParent)[0].click()"); pg.wait_for_timeout(1000); s=st(pg)
        ok('Collegamento dossier: resta in nuova UI o Timeline (mai overlay legacy)', not s['ov'] , s)
        if s['a2']: a2back(pg)
        else: pg.evaluate("()=>document.getElementById('tvaBackBtn').click()"); pg.wait_for_timeout(800)
        s2=st(pg); ok('Indietro dopo collegamento: torna al dossier/Atlante', s2['a2'] or s2['tab'], s2)
    # 6 altre voci legacy dall'Atlante: shell + ritorno
    pg.evaluate("()=>{const a=document.getElementById('atlas2Toggle'); if(!a.checked){a.checked=true;a.dispatchEvent(new Event('change',{bubbles:true}))}}"); pg.wait_for_timeout(500)
    for rx,tg,ttl in [('Cronologie','', ''),]: pass
    ctx.close()
    # 7 giro per ogni overlay classico: titolo, shell, back
    for tg,title in [('universeTimelineToggle','Timeline degli Universi'),('altTimelineToggle','Timeline alternativa'),('relationshipGraphToggle','Relazioni'),('kangTvaGraphToggle','Kang')]:  # l'archivio classico non è più raggiungibile: è coperto da leg_test (guardia -> Atlante)
        ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block'); pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(U); pg.wait_for_timeout(1200)
        pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
        pg.evaluate("()=>document.getElementById('appTabAtlante').click()"); pg.wait_for_timeout(700)
        pg.evaluate("(t)=>{window.tvaPushNav('Atlante');window.marvelChiudiOverlay();const e=document.getElementById(t);e.checked=true;e.dispatchEvent(new Event('change',{bubbles:true}))}",tg); pg.wait_for_timeout(900); s=st(pg)
        ok(f'{tg}: shell TVA, no barra/menu/vecchio Indietro', s['ov']==[tg] and s['shell'] and not s['tab'] and not s['menu'] and not s['legacyBack'] and title in s['title'], s)
        pg.evaluate("()=>document.querySelector('#tvaShell .ts-back').click()"); pg.wait_for_timeout(800); s=st(pg)
        ok(f'{tg}: Indietro -> Atlante', s['a2'] and not s['ov'], s)
        ctx.close()
    # 8 Friends -> Home
    ctx=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block'); pg=ctx.new_page(); pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>document.getElementById('appTabFriends').click()"); pg.wait_for_timeout(700); s=st(pg)
    ok('Friends: UI nuova, barra presente, overlay Friends', pg.evaluate("()=>{const r=document.getElementById('tfRoot');return !!r&&!r.hidden&&getComputedStyle(r).display!=='none'}") and not s['ov'] and not s['shell'], s)
    pg.evaluate("()=>document.getElementById('appTabHome').click()"); pg.wait_for_timeout(700); s=st(pg)
    ok('Friends -> Home', s['home'] and not s['ov'] and s['tab'], s)
    # 9 Home -> Esplora il Multiverso -> Indietro -> Home
    pg.evaluate("()=>document.querySelector('label[for=multiverseGraphToggle].home-hub-btn').click()"); pg.wait_for_timeout(800); s=st(pg)
    ok('Home -> Esplora il Multiverso: shell TVA', s['ov']==['multiverseGraphToggle'] and s['shell'] and not s['tab'], s)
    pg.evaluate("()=>document.querySelector('#tvaShell .ts-back').click()"); pg.wait_for_timeout(800); s=st(pg)
    ok('Indietro (senza cronologia) -> Home', s['home'] and not s['ov'] and s['tab'], s)
    ctx.close(); b.close()
ok('nessun pageerror', not errs, errs[:3])
print('TOTALE',len(res),'FAIL',len([r for r in res if not r[1]])); json.dump(res,open('/tmp/claude-0/t/nav_test.json','w'))
