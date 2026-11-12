import json, re, sys
from playwright.sync_api import sync_playwright
U='http://127.0.0.1:8124/index.html'
res=[]; errs=[]
def ok(n,c,d=''):
    res.append((n,bool(c),d)); print(('PASS ' if c else 'FAIL ')+n+(' '+str(d) if (d and not c) else ''))
def start(b,w=390,h=844,storage=None):
    ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=True,has_touch=True,service_workers='block'); pg=ctx.new_page()
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(900)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    return ctx,pg
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg=start(b)
    # 1 tema scuro predefinito
    ok('tema scuro di default (classe html)', pg.evaluate("()=>document.documentElement.classList.contains('marvel-dark-mode')"))
    ok('checkbox dark spuntato', pg.evaluate("()=>document.getElementById('darkModeToggle').checked"))
    ok('sfondo body #101014', pg.evaluate("()=>getComputedStyle(document.body).backgroundColor")=='rgb(16, 16, 20)')
    ok('theme-color #101014', pg.evaluate("()=>document.querySelector('meta[name=theme-color]').content")=='#101014')
    # 2 home
    ok('build id', pg.evaluate("()=>document.querySelector('meta[name=tva-build]').content")=='20261023-1730-m342')
    ok('home visibile', pg.evaluate("()=>getComputedStyle(document.getElementById('homeHub')).display!=='none'"))
    ord=pg.evaluate("""()=>{const y=s=>{const e=document.querySelector(s);return e?e.getBoundingClientRect().top:-1};return {g:y('.home-hub-greeting'),h:y('#hhsNextRow'),n:y('.home-hub-nav'),s:y('.m34-stats'),a:y('#m34Atl'),m:y('#m34Mis')}}""")
    ok('gerarchia home M3.4: saluto<prossimo<statistiche<accessi<missione', 0<ord['g']<ord['h']<ord['s']<ord['a']<ord['m'], ord)
    ok('progress bar home', pg.evaluate("()=>!!document.querySelector('.home-hub-greeting .rs-prog')"))
    ok('stat ids presenti', pg.evaluate("()=>['hhsRating','hhsDone','hhsHours','hhsNextValue','hhgPct'].every(i=>document.getElementById(i))"))
    pg.evaluate("()=>document.getElementById('m34MGo').click()"); pg.wait_for_timeout(700)
    ok('card missioni apre tab Missioni', pg.evaluate("()=>document.getElementById('appTabMissioni').classList.contains('app-tab-active')"))
    # 3 navigazione
    for t in ['Home','Timeline','Atlante','Missioni','Tessera','Friends']:
        if t!='Atlante':
            pg.evaluate("(t)=>{const a=document.getElementById('atlas2Toggle'); if(a&&a.checked){a.checked=false;a.dispatchEvent(new Event('change',{bubbles:true}))}}",t)
        pg.evaluate("(t)=>document.getElementById('appTab'+t).click()",t); pg.wait_for_timeout(700)
        d=pg.evaluate("()=>[getComputedStyle(document.getElementById('appTabbar')).display, document.documentElement.scrollWidth<=innerWidth+1, document.getElementById('atlas2Toggle').checked]")
        if t=='Atlante': ok('Atlante: nuova TVA Archives immersiva, barra principale nascosta', d[2] and d[0]=='none', d)
        else: ok(f'tab {t}: barra visibile, nessun overflow', d[0]!='none' and d[1], d)
    pg.evaluate("()=>{const a=document.getElementById('atlas2Toggle'); a.checked=false;a.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    # 4 icone e testo
    ok('emoji sostituite da icone', pg.evaluate("()=>document.querySelectorAll('.rs-i').length")>50)
    ok('tabbar: icone SVG, nessuna emoji', pg.evaluate("()=>!/\\p{Extended_Pictographic}/u.test(document.getElementById('appTabbar').textContent)"))
    mono=pg.evaluate("""()=>{const bad=[];document.querySelectorAll('.home-hub p, .info-text, .detail-v, .mg-sub, .tessera-prossimo, .user-note').forEach(e=>{if(/mono|courier|plex|elite/i.test(getComputedStyle(e).fontFamily)&&e.offsetParent)bad.push(e.className)});return bad.slice(0,5)}""")
    ok('nessun blocco di testo in monospace', not mono, mono)
    # 5 salvataggi: visto + preferito + persistenza dopo reload
    pg.evaluate("()=>document.getElementById('appTabTimeline').click()"); pg.wait_for_timeout(600)
    pg.evaluate("()=>{document.querySelector('#item-001 .watch-box').click(); document.querySelector('#item-001 .fav-star').click()}"); pg.wait_for_timeout(400)
    st=pg.evaluate("()=>[document.querySelector('#item-001 .watch-check').checked, document.querySelector('#item-001 .fav-star').classList.contains('is-fav'), document.querySelector('#item-001').classList.contains('watched')]")
    ok('visto+preferito applicati', st==[True,True,True], st)
    wm=pg.evaluate("()=>{const e=document.querySelector('#item-001 .watch-mark');const c=getComputedStyle(e);return [c.backgroundColor,c.color]}")
    ok('stato visto riconoscibile (check oro)', wm[0]=='rgb(210, 177, 132)', wm)
    pg.reload(); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{journeyStarted.checked=true; journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(500)
    st2=pg.evaluate("()=>[document.querySelector('#item-001 .watch-check').checked, document.querySelector('#item-001 .fav-star').classList.contains('is-fav')]")
    ok('persistenza dopo reload', st2==[True,True], st2)
    pct=pg.evaluate("()=>document.getElementById('hhgPct').textContent")
    ok('progresso home aggiornato (1/138)', pct.strip() not in ('','0'), pct)
    # 6 tessera / friends elementi intatti
    pg.evaluate("()=>document.getElementById('appTabTessera').click()"); pg.wait_for_timeout(700)
    ids=pg.evaluate("()=>['tesseraId','tesseraRank','tesseraXp','tesseraLv'].map(i=>!!document.getElementById(i))")
    cls=pg.evaluate("()=>['.tessera-name-input','.tessera-id','.tessera-rank','.tessera-xp-lv','.tessera-xp-num','.tessera-stats .tessera-stat','#tesseraCondividiBtn'].map(s=>!!document.querySelector(s))")
    ok('tessera: nome, ID, rango, livello, XP, statistiche, condividi', all(cls), cls)
    pg.evaluate("()=>document.getElementById('appTabFriends').click()"); pg.wait_for_timeout(700)
    cls=pg.evaluate("()=>['.live-room-create-btn','.sync-code-row','.friends-group-create-row','.friends-lb-box','.friends-group-box'].map(s=>!!document.querySelector(s))")
    ok('friends: crea stanza, codice, gruppo, classifica presenti', all(cls), cls)
    # 7 tema chiaro raggiungibile e ritorno
    pg.evaluate("()=>{const t=document.getElementById('darkModeToggle');t.checked=false;t.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    ok('tema chiaro legacy raggiungibile', pg.evaluate("()=>!document.documentElement.classList.contains('marvel-dark-mode') && localStorage.getItem('marvel-skin-v2-dark')==='0'"))
    pg.evaluate("()=>{const t=document.getElementById('darkModeToggle');t.checked=true;t.dispatchEvent(new Event('change',{bubbles:true}))}")
    ok('ritorno al tema scuro salvato', pg.evaluate("()=>localStorage.getItem('marvel-skin-v2-dark')==='1'"))
    ctx.close()
    # 8 responsive 320/360/430 per tab
    for w in (320,360,430):
        ctx,pg=start(b,w,740)
        bad=[]
        for t in ['Home','Timeline','Missioni','Tessera','Friends']:
            pg.evaluate("(t)=>document.getElementById('appTab'+t).click()",t); pg.wait_for_timeout(600)
            o=pg.evaluate("""()=>{const W=innerWidth;const bad=[];document.querySelectorAll('body *').forEach(e=>{if(e.closest('svg,.a2,.intro-screen,.sidebar,.skip-link,.tf-ep-tabs,.tf-tabs')||e.classList.contains('skip-link'))return;const r=e.getBoundingClientRect();if(r.width>0&&r.height>0&&(r.right>W+1||r.left<-1)&&getComputedStyle(e).position!=='fixed'&&e.offsetParent!==null){const c=e.closest('details:not([open])');if(!c)bad.push(e.className||e.tagName)}});return [document.documentElement.scrollWidth-W, [...new Set(bad)].slice(0,6)]}""")
            if o[0]>1 or o[1]: bad.append((t,o))
        ok(f'{w}px: nessun overflow orizzontale', not bad, bad)
        ctx.close()
    # 9 tabbar e menu: safe area / sovrapposizione
    ctx,pg=start(b)
    pg.evaluate("()=>document.getElementById('appTabTimeline').click()"); pg.wait_for_timeout(500)
    g=pg.evaluate("()=>{const t=document.getElementById('appTabbar').getBoundingClientRect(),m=document.querySelector('.sidebar-open-btn').getBoundingClientRect();return [t.bottom<=innerHeight+1,t.height,m.width,m.height,m.bottom<t.top]}")
    ok('tabbar a filo schermo, menu 44px', g[0] and g[2]>=40 and g[4], g)
    ctx.close(); b.close()
ok('nessun pageerror', not errs, errs[:3])
f=[r for r in res if not r[1]]
print('TOTALE',len(res),'FAIL',len(f)); json.dump(res,open('/tmp/claude-0/t/rs_test.json','w'))
