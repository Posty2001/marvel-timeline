from f4lib import *
import json
def snap(pg):
    o=pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k);}return o}")
    o.pop('marvel-ultimate-timeline-tessera-id',None); return o
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg,errs=boot(b)
    A="tvaAtlas2.getState()"
    # --- D1: chip N° da un personaggio
    pg.evaluate("()=>tvaGo('char','char-wade-wilson-deadpool')"); pg.wait_for_timeout(500)
    ok('B1 pagina personaggio aperta',pg.evaluate("()=>"+A+".screen")=='char')
    n=pg.locator('.a2-char [data-go^="item:"]').count(); ok('B2 la pagina ha chip N°',n>0,n)
    pg.locator('.a2-char [data-go^="item:"]').first.click(); pg.wait_for_timeout(500)
    st=pg.evaluate("()=>"+A)
    ok('B3 chip N° apre il Dossier Opera',st['screen']=='opera' and st['eid'].startswith('item-'),st)
    ok('B4 Atlante ancora aperto (nessun salto nella Timeline)',pg.evaluate("()=>document.getElementById('atlas2Toggle').checked"))
    # back -> pagina personaggio
    pg.click('.a2-back'); pg.wait_for_timeout(600)
    st=pg.evaluate("()=>"+A); ok('B5 Indietro torna al personaggio',st['screen']=='char' and st['eid']=='char-wade-wilson-deadpool',st)
    # --- Scheda in guida e ritorno
    pg.evaluate("()=>tvaGo('item','item-023')"); pg.wait_for_timeout(400)
    pg.click('#d4Scheda'); pg.wait_for_timeout(1200)
    r=pg.evaluate("()=>({atl:document.getElementById('atlas2Toggle').checked,card:(()=>{const c=document.getElementById('item-023');const r=c.getBoundingClientRect();return {open:c.querySelector('details').open,page:c.classList.contains('td-page'),vis:c.offsetParent!==null,top:Math.round(r.top)}})()})")
    ok('B6 «Scheda in guida» chiude l\'Atlante e apre la scheda originale',(not r['atl']) and r['card']['open'] and (r['card']['vis'] or r['card']['page']),r)  # TD2: la scheda originale e' la pagina immersiva
    pg.click('.td2-back:visible, #tvaBackBtn:visible')  # TD2: dalla pagina immersiva Indietro e' il pulsante della pagina; pg.wait_for_timeout(900)
    st=pg.evaluate("()=>({atl:document.getElementById('atlas2Toggle').checked,s:"+A+"})")
    ok('B7 Indietro dalla scheda riporta al Dossier Opera',st['atl'] and st['s']['screen']=='opera' and st['s']['eid']=='item-023',st)
    # --- tutti i contesti dell'Atlante portano al Dossier Opera
    ctxs={}
    pg.evaluate("()=>tvaAtlas2.ext.api.nav('search')"); pg.fill('#a2Search','logan'); pg.wait_for_timeout(500)
    pg.locator('.d4-res-tit .a2-chip').first.click(); pg.wait_for_timeout(400); ctxs['ricerca']=pg.evaluate("()=>"+A+".screen")
    pg.evaluate("()=>tvaAtlas2.openUni('uni-earth-10005-fox-verse')"); pg.wait_for_timeout(500)
    pg.locator('.ud-ref, [data-go^="item:"]').first.click(); pg.wait_for_timeout(400); ctxs['dossier universo']=pg.evaluate("()=>"+A+".screen")
    pg.evaluate("()=>tvaGo('att','att-hugh-jackman')"); pg.wait_for_timeout(400)
    pg.locator('.a2-att [data-go^="item:"]').first.click(); pg.wait_for_timeout(400); ctxs['attore']=pg.evaluate("()=>"+A+".screen")
    pg.evaluate("()=>tvaGo('arc','org:org-s-h-i-e-l-d')") ; pg.wait_for_timeout(400)
    ok('B8 contesti -> Dossier Opera',all(v=='opera' for v in ctxs.values()),ctxs)
    # --- 3B / 3C invariati: aprono la scheda in guida
    pg.evaluate("()=>tvaAtlas2.ext.api.crOpen('uni',{uid:'uni-earth-10005-fox-verse'})"); pg.wait_for_timeout(700)
    n3=pg.locator('.a2 [data-go^="item:"]').count(); ok('B9 3C ha titoli cliccabili',n3>0,n3)
    pg.locator('.a2 [data-go^="item:"]').first.click(); pg.wait_for_timeout(1200)
    st=pg.evaluate("()=>({atl:document.getElementById('atlas2Toggle').checked})"); ok('B10 3C: il titolo apre ancora la scheda in guida (invariato)',not st['atl'],st)
    pg.evaluate("()=>tvaAtlas2.enter()"); pg.wait_for_timeout(400)
    # --- stato Visto: stessa logica della Timeline
    def run(mode):
        c2=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,service_workers='block'); q=c2.new_page(); q.set_default_timeout(8000); e2=[]; q.on('pageerror',lambda e:e2.append(str(e)))
        q.add_init_script("Date.now=(()=>{const t=1792400000000;return()=>t})();"); q.goto(U); q.wait_for_timeout(900)
        q.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); q.wait_for_timeout(300)
        q.evaluate("()=>tvaAtlas2.enter()"); q.wait_for_timeout(400)
        s0=snap(q)
        if mode=='dossier':
            q.evaluate("()=>tvaGo('item','item-023')"); q.wait_for_timeout(400); q.click('#d4Seen'); q.wait_for_timeout(500)
            on=q.evaluate("()=>document.getElementById('d4Seen').getAttribute('aria-pressed')")
        else:
            q.evaluate("()=>document.querySelector('#item-023 .watch-check').click()"); q.wait_for_timeout(500); on='true'
        s1=snap(q)
        if mode=='dossier':
            q.click('#d4Seen'); q.wait_for_timeout(500); s2=snap(q); off=q.evaluate("()=>document.getElementById('d4Seen').getAttribute('aria-pressed')")
        else:
            q.evaluate("()=>document.querySelector('#item-023 .watch-check').click()"); q.wait_for_timeout(500); s2=snap(q); off='false'
        c2.close(); return s0,s1,s2,on,off,e2
    d=run('dossier'); t=run('timeline')
    ok('B11 Visto dal Dossier = clic sulla Timeline (stesso localStorage dopo la spunta)',d[1]==t[1],{k:(d[1].get(k),t[1].get(k)) for k in set(d[1])|set(t[1]) if d[1].get(k)!=t[1].get(k)})
    ok('B12 Visto togliendo la spunta = stesso stato di partenza e stesso risultato della Timeline',d[2]==t[2],{k:(d[2].get(k),t[2].get(k)) for k in set(d[2])|set(t[2]) if d[2].get(k)!=t[2].get(k)})
    ok('B13 la spunta cambia davvero (progressi salvati)',d[1]!=d[0],'nessuna differenza')
    ok('B14 aria-pressed coerente',d[3]=='true' and d[4]=='false',(d[3],d[4]))
    ok('B15 nessun errore JS',errs==[] and d[5]==[] and t[5]==[],(errs,d[5],t[5]))
    b.close()
done()
