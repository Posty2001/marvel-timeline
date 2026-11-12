from f4lib import *
import json, re
def tab(pg,n): pg.evaluate("(n)=>document.getElementById(n).click()",n); pg.wait_for_timeout(500)
def vis(pg,sel): return pg.evaluate("(s)=>{const e=document.querySelector(s);return !!e&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden'}",sel)
def ls(pg): return pg.evaluate("()=>JSON.stringify(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))")
def sec(pg,s): pg.evaluate("(s)=>document.getElementById('cenTab-'+s).click()",s); pg.wait_for_timeout(350)
def sub(pg,s): pg.evaluate("(s)=>document.getElementById('cenSub-'+s).click()",s); pg.wait_for_timeout(300)
def mark(pg,ids):
    for i in ids:
        pg.evaluate("(i)=>{const c=document.querySelector('.watch-check[data-item=\"'+i+'\"]');if(!c.checked){c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}))}}",i)
    pg.wait_for_timeout(500)
def go(pg):
    pg.evaluate("()=>{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
with sync_playwright() as p:
    b=p.chromium.launch()
    # ============ funzionale (390) ============
    ctx,pg,errs=boot(b,390,844,atlas=False); go(pg)
    ok('N0 barra: 6 voci invariate',pg.evaluate("()=>[...document.querySelectorAll('#appTabbar .app-tab')].map(t=>t.id).join()")=='appTabHome,appTabTimeline,appTabAtlante,appTabMissioni,appTabTessera,appTabFriends')
    tab(pg,'appTabMissioni')
    ok('N1 Centrale: Panoramica attiva, 4 sezioni, un solo pannello visibile',pg.evaluate("()=>[...document.querySelectorAll('.cen-tab')].map(t=>t.dataset.sec).join()")=='panoramica,missioni,strumenti,operazioni' and pg.evaluate("()=>[...document.querySelectorAll('.cen-panel')].filter(p=>p.getClientRects().length).map(p=>p.dataset.sec).join()")=='panoramica')
    ok('N1b ARIA: tablist/tab/tabpanel e aria-selected',pg.evaluate("()=>{const t=[...document.querySelectorAll('.cen-tab')];return document.querySelector('.cen-nav').getAttribute('role')==='tablist'&&t.every(x=>x.getAttribute('role')==='tab'&&document.getElementById(x.getAttribute('aria-controls')).getAttribute('role')==='tabpanel')&&t.filter(x=>x.getAttribute('aria-selected')==='true').length===1}"))
    ok('N1c [B2.1] ordine e etichette: PANORAMICA · MISSIONI · OSSERVATORIO · OPERAZIONI; icona radar SVG, nessuna emoji attrezzi',pg.evaluate("()=>[...document.querySelectorAll('.cen-tab-l')].map(x=>x.textContent).join()")=='Panoramica,Missioni,Osservatorio,Operazioni' and pg.evaluate("()=>!!document.querySelector('#cenTab-strumenti svg.cen-radar')&&!/🧰/.test(document.getElementById('dashboard').innerText)"))
    ok('N1d [B2.1] panoramica: scorciatoie nell\'ordine Missioni, Osservatorio, Operazioni',pg.evaluate("()=>[...document.querySelectorAll('.cen-sbtn[data-go-sec]')].map(x=>x.dataset.goSec).join()")=='missioni,strumenti,operazioni')
    for s in ('missioni','strumenti','operazioni','panoramica'):
        sec(pg,s); okk=pg.evaluate("(s)=>[...document.querySelectorAll('.cen-panel')].filter(p=>p.getClientRects().length).map(p=>p.dataset.sec).join()==s&&document.getElementById('cenTab-'+s).getAttribute('aria-selected')==='true'",s); ok('N2 sezione %s'%s,okk)
    pg.focus('#cenTab-panoramica'); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(200)
    ok('N3 tastiera: freccia destra attiva la sezione successiva',pg.evaluate("()=>document.getElementById('cenTab-missioni').getAttribute('aria-selected')==='true'"))
    # contesto conservato
    sub(pg,'stagioni'); sec(pg,'operazioni'); sec(pg,'missioni')
    ok('N4 contesto: la sotto-sezione Stagioni resta dopo il cambio di sezione',pg.evaluate("()=>document.getElementById('cenSub-stagioni').getAttribute('aria-selected')==='true'"))
    sub(pg,'attive'); pg.evaluate("()=>window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})"); y1=pg.evaluate("()=>scrollY"); sec(pg,'strumenti'); sec(pg,'missioni'); y2=pg.evaluate("()=>scrollY")
    ok('N4b contesto: posizione di scorrimento di Missioni ripristinata (%d→%d)'%(y1,y2),abs(y1-y2)<80,(y1,y2))
    # ============ Missioni ============
    sec(pg,'missioni'); sub(pg,'attive')
    ids=['missioneSettimanale','missioneTematica','missioneSaga','missioneSegreta']
    ok('M1 4 missioni esistenti (stessi id) dentro Attive, una volta sola',all(pg.evaluate("(i)=>document.querySelectorAll('#'+i).length===1&&!!document.querySelector('#cenSubPan-attive #'+i)",i) for i in ids))
    for k in ('settimanale','tematica','saga','segreta'):
        pg.evaluate("(k)=>{const b=document.querySelector('.cen-dbtn[data-mission=\"'+k+'\"]');b.click()}",k); pg.wait_for_timeout(250)
        t=pg.evaluate("(k)=>{const d=document.getElementById('cenDos-'+k);return {v:d.getClientRects().length>0,t:d.innerText}}",k)
        ok('M2 dossier %s: descrizione, requisiti, stato, ricompensa, scadenza'%k,t['v'] and all(x in t['t'].upper() for x in ('DESCRIZIONE','REQUISITI','STATO','RICOMPENSA','SCADENZA')),t['t'][:160])
        if k=='segreta':
            hidden=pg.evaluate("()=>{const d=document.getElementById('cenDos-segreta').innerText;return !D}".replace('D','document.querySelector(\".cen-work\")')) if False else True
            ok('M2s dossier segreta: nessun titolo rivelato (protezione spoiler)',pg.evaluate("()=>!document.getElementById('cenDos-segreta').querySelector('.cen-work')")and 'nascost' in t['t'].lower(),t['t'][:200])
    ok('M3 dossier tematica/saga: titoli idonei con link (componente esistente .tva-mis)',pg.evaluate("()=>['missioneTematica','missioneSaga'].every(i=>document.querySelector('#'+i+' > .tva-mis .tva-chip')&&getComputedStyle(document.querySelector('#'+i+' > .tva-mis')).display!=='none')"))
    sub(pg,'stagioni')
    st=pg.evaluate("()=>({n:document.getElementById('stagioneTvaNome').textContent,f:document.getElementById('stagioneTvaFrac').textContent,t:document.getElementById('cenDos-stagione').innerText,once:document.querySelectorAll('#stagioneTvaCard').length})")
    ok('M4 Stagioni: «La Guerra delle Incursioni» 0/10, condizioni e ricompense',st['n']=='La Guerra delle Incursioni' and st['f']=='0/10' and st['once']==1 and '+500 XP' in st['t'] and 'Custode delle Incursioni' in st['t'],st)
    sub(pg,'speciali')
    rt=pg.evaluate("()=>({f:document.getElementById('rtdFrac').textContent,n:document.querySelectorAll('#rtdList .rtd-item').length,note:document.querySelector('.rtd-note').textContent,xp:document.getElementById('cenDos-rtd').innerText})")
    ok('M5 Speciali: Road to Doomsday 0/16, 16 schede, distinzione watchlist ufficiale/editoriale, +300 XP',rt['f']=='0/16' and rt['n']==16 and 'watchlist ufficiale' in rt['note'] and 'editoriali di TVA Archive' in rt['note'] and '+300 XP' in rt['xp'],rt)
    sub(pg,'archivio'); ok('M6 Archivio: vuoto all\'inizio, nessuna voce inventata',pg.evaluate("()=>document.querySelectorAll('#cenArchive .cen-arch-l li').length===0&&/Nessuna missione conclusa/.test(document.getElementById('cenArchive').innerText)"))
    # ============ apertura diretta missione, hash ============
    pg.evaluate("()=>tvaCentrale.openMission('rtd')"); pg.wait_for_timeout(600)
    ok('M7 openMission(rtd): Speciali attivo, elenco aperto',pg.evaluate("()=>document.getElementById('cenSub-speciali').getAttribute('aria-selected')==='true'&&document.getElementById('rtdDetails').open"))
    pg.evaluate("()=>tvaCentrale.openMission('saga')"); pg.wait_for_timeout(600)
    ok('M7b openMission(saga): Attive, dossier aperto',pg.evaluate("()=>document.getElementById('cenSub-attive').getAttribute('aria-selected')==='true'&&!document.getElementById('cenDos-saga').hidden"))
    pg.evaluate("()=>{location.hash='#cen-operazioni'}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>{location.hash='#cen-osservatorio'}"); pg.wait_for_timeout(500); ok('M8a [B2.1] ancora #cen-osservatorio (alias) apre Osservatorio',pg.evaluate("()=>document.getElementById('cenTab-strumenti').getAttribute('aria-selected')==='true'"))
    pg.evaluate("()=>{location.hash='#cen-strumenti'}"); pg.wait_for_timeout(300); pg.evaluate("()=>{location.hash='#cen-operazioni'}"); pg.wait_for_timeout(500)
    ok('M8 ancora #cen-operazioni',pg.evaluate("()=>document.getElementById('cenTab-operazioni').getAttribute('aria-selected')==='true'"))
    # ============ anteprima in Panoramica ============
    sec(pg,'panoramica')
    pv=pg.evaluate("()=>({rows:document.querySelectorAll('.cen-prev .cen-pr').length,hasStag:/La Guerra delle Incursioni/.test(document.body.innerText),agent:document.querySelector('.cen-agent').innerText})")
    ok('P1 Panoramica: agente, livello, progresso, prossimo titolo, 4 missioni + stagione',pv['rows']==5 and 'LV.' in pv['agent'] and pg.evaluate("()=>!!document.querySelector('.dash-holo-main')&&getComputedStyle(document.getElementById('dashLastNext')).display!=='none'"),pv)
    # ============ titoli dalla Centrale e ritorno ============
    st0=pg.evaluate("()=>tvaNavStato().depth")
    pg.evaluate("()=>document.getElementById('nextWatchCard').click()"); pg.wait_for_timeout(1200)
    r=pg.evaluate("()=>({view:document.documentElement.dataset.tvaView,tab:document.querySelector('.app-tab-active').dataset.tab,back:document.getElementById('tvaBackBtn').hidden?'':document.getElementById('tvaBackBtn').innerText,card:!!document.querySelector('#item-001').getClientRects().length,depth:tvaNavStato().depth})")
    ok('T1 titolo dalla Centrale: vista Timeline, scheda visibile, tab Timeline, Indietro «Centrale TVA»',r['view']=='timeline' and r['card'] and r['tab']=='timeline' and 'Centrale TVA' in r['back'] and r['depth']==st0+1,r)
    pg.evaluate("()=>document.getElementById('tvaBackBtn').click()"); pg.wait_for_timeout(900)
    r=pg.evaluate("()=>({view:document.documentElement.dataset.tvaView,tab:document.querySelector('.app-tab-active').dataset.tab,sec:document.querySelector('.cen-tab[aria-selected=true]').dataset.sec,vis:!!document.querySelector('#cenPan-panoramica').getClientRects().length,depth:tvaNavStato().depth})")
    ok('T2 Indietro: ritorno alla Centrale (sezione Panoramica) e tab Centrale',r['view']=='centrale' and r['tab']=='missioni' and r['sec']=='panoramica' and r['vis'] and r['depth']==st0,r)
    # da dossier missione (Missioni/Attive) a titolo e ritorno
    sec(pg,'missioni'); sub(pg,'attive'); pg.evaluate("(k)=>{const b=document.querySelector('.cen-dbtn[data-mission=\"'+k+'\"]');if(b.getAttribute('aria-expanded')!=='true')b.click()}",'tematica'); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.querySelector('#missioneTematica > .tva-mis .tva-chip').click()"); pg.wait_for_timeout(1300)
    ok('T3 chip titolo di una missione: apre la scheda in Timeline',pg.evaluate("()=>document.documentElement.dataset.tvaView==='timeline'&&document.querySelector('.app-tab-active').dataset.tab==='timeline'"))
    pg.evaluate("()=>document.getElementById('tvaBackBtn').click()"); pg.wait_for_timeout(900)
    ok('T4 Indietro: Missioni/Attive con dossier ancora aperto',pg.evaluate("()=>document.documentElement.dataset.tvaView==='centrale'&&document.getElementById('cenSub-attive').getAttribute('aria-selected')==='true'&&document.querySelector('.cen-tab[aria-selected=true]').dataset.sec==='missioni'&&!document.getElementById('cenDos-tematica').hidden"),pg.evaluate("()=>JSON.stringify([tvaCentrale.getState(),document.documentElement.dataset.tvaView,document.getElementById('cenDos-tematica').hidden,document.querySelector('.cen-tab[aria-selected=true]').dataset.sec,tvaNavStato()])"))
    # RTD
    sub(pg,'speciali'); pg.evaluate("()=>{document.getElementById('rtdDetails').open=true}"); pg.wait_for_timeout(200)
    pg.evaluate("()=>document.querySelector('#rtdList .rtd-link').click()"); pg.wait_for_timeout(1300)
    ok('T5 scheda dal percorso Road to Doomsday: Timeline',pg.evaluate("()=>document.documentElement.dataset.tvaView==='timeline'"))
    pg.evaluate("()=>document.getElementById('tvaBackBtn').click()"); pg.wait_for_timeout(900); ok('T6 Indietro da RTD: Speciali',pg.evaluate("()=>document.documentElement.dataset.tvaView==='centrale'&&document.getElementById('cenSub-speciali').getAttribute('aria-selected')==='true'"))
    # scrollIntoView / ricerca / tvaGo
    pg.evaluate("()=>document.getElementById('item-005').scrollIntoView()"); pg.wait_for_timeout(300); ok('T7 scrollIntoView verso un titolo dalla Centrale: Timeline + tab Timeline',pg.evaluate("()=>document.documentElement.dataset.tvaView==='timeline'&&document.querySelector('.app-tab-active').dataset.tab==='timeline'&&!!document.querySelector('#item-005').getClientRects().length"))
    pg.evaluate("()=>document.getElementById('dashboard').scrollIntoView()"); pg.wait_for_timeout(300); ok('T8 scrollIntoView verso la Centrale: vista Centrale + tab Centrale',pg.evaluate("()=>document.documentElement.dataset.tvaView==='centrale'&&document.querySelector('.app-tab-active').dataset.tab==='missioni'"))
    tab(pg,'appTabTimeline'); pg.evaluate("()=>tvaGo('item','010')"); pg.wait_for_timeout(1200); ok('T9 tvaGo item dalla Timeline: scheda visibile',pg.evaluate("()=>!!document.querySelector('#item-010').getClientRects().length"))
    tab(pg,'appTabMissioni'); ok('T10 cambio tab: Centrale ripristinata nel contesto precedente (un solo pannello visibile)',pg.evaluate("()=>document.documentElement.dataset.tvaView==='centrale'&&[...document.querySelectorAll('.cen-panel')].filter(p=>p.getClientRects().length).length===1"))
    # Atlante / Friends dalla Centrale
    pg.evaluate("()=>document.querySelector('.cen-sbtn[data-act=atlante]').click()"); pg.wait_for_timeout(700)
    ok('T11 collegamento Atlante: apre l\'Atlante esistente (home) senza enciclopedia parallela',pg.evaluate("()=>document.getElementById('atlas2Toggle').checked&&tvaAtlas2.getState().screen==='home'&&!document.querySelector('#dashboard [id^=atlas]')"))
    tab(pg,'appTabFriends'); ok('T12 Friends 2.0 si apre dalla barra (non la vecchia sala)',pg.evaluate("()=>{const r=document.getElementById('tfRoot');return !!r&&!r.hidden&&getComputedStyle(r).display!=='none'&&!document.getElementById('friendsToggle').checked}")); tab(pg,'appTabMissioni')
    ok('T12b nessun overlay residuo in Centrale',pg.evaluate("()=>![...document.querySelectorAll('input[type=checkbox][id$=Toggle]')].some(c=>c.checked&&c.id!=='sidebarToggle'&&c.id!=='expandAllToggle'&&c.id!=='darkModeToggle'&&!/spoiler/i.test(c.id))"))
    # ============ dati: nessuna scrittura per sola navigazione ============
    k0=ls(pg)
    for s in ('missioni','operazioni','strumenti','panoramica'): sec(pg,s)
    sub_=['attive','stagioni','speciali','archivio']
    sec(pg,'missioni')
    for s in sub_: sub(pg,s)
    pg.evaluate("()=>document.querySelectorAll('.cen-dbtn').forEach(b=>b.click())"); pg.wait_for_timeout(300)
    ok('D1 navigare/aprire dossier non scrive in localStorage',ls(pg)==k0)
    # ============ operazioni ============
    sec(pg,'operazioni')
    need=['resetBtn','resetAllBtn','markAllBtn','exportBtn','importBtn','syncCodeInput','syncGenBtn','syncConnectBtn']
    ok('O1 operazioni presenti una volta sola nel pannello Operazioni e visibili',all(pg.evaluate("(i)=>document.querySelectorAll('#'+i).length===1&&!!document.querySelector('#cenPan-operazioni #'+i)&&document.getElementById(i).getClientRects().length>0",i) for i in need if i!='syncDisconnectBtn'))
    ok('O1b modalità scura e backup automatico raggiungibili',pg.evaluate("()=>!!document.querySelector('#cenPan-operazioni label[for=darkModeToggle]')&&!!document.querySelector('#cenPan-operazioni #autoBackupHint')&&!!document.querySelector('#cenPan-operazioni #syncDisconnectBtn')"))
    ok('O2 reset distruttivi in «Zona pericolosa»',pg.evaluate("()=>!!document.querySelector('.cen-danger #resetBtn')&&!!document.querySelector('.cen-danger #resetAllBtn')&&!document.querySelector('.cen-danger #markAllBtn')"))
    # voto + visto
    mark(pg,['001','002'])
    pg.evaluate("()=>{const k='marvel-ultimate-timeline-ratings';localStorage.setItem(k,JSON.stringify({'001':4.5}))}")
    pg.evaluate("()=>document.getElementById('resetBtn').click()"); pg.wait_for_timeout(250)
    ok('O3 Resetta progresso: conferma 1 visibile (distinguibile)',pg.evaluate("()=>getComputedStyle(document.getElementById('resetConfirmOverlay')).display!=='none'"))
    pg.evaluate("()=>document.getElementById('resetConfirmCancel').click()"); pg.wait_for_timeout(200)
    ok('O3b Annulla: nulla cambia',pg.evaluate("()=>document.querySelector('.watch-check[data-item=\"001\"]').checked&&getComputedStyle(document.getElementById('resetConfirmOverlay')).display==='none'"))
    pg.evaluate("()=>document.getElementById('resetBtn').click()"); pg.wait_for_timeout(200); pg.evaluate("()=>document.getElementById('resetConfirmOk').click()"); pg.wait_for_timeout(300)
    ok('O3c seconda conferma richiesta',pg.evaluate("()=>getComputedStyle(document.getElementById('resetConfirmOverlay2')).display!=='none'"))
    pg.evaluate("()=>document.getElementById('resetConfirmOk2').click()"); pg.wait_for_timeout(600)
    ok('O3d reset: visti azzerati, voti/note/preferiti invariati (semantica invariata)',pg.evaluate("()=>[...document.querySelectorAll('.watch-check')].every(c=>!c.checked)&&JSON.parse(localStorage.getItem('marvel-ultimate-timeline-ratings')||'{}')['001']===4.5"))
    # reset totale: due conferme, digitare CANCELLA
    pg.evaluate("()=>document.getElementById('resetAllBtn').click()"); pg.wait_for_timeout(250); pg.evaluate("()=>document.getElementById('resetAllConfirmContinue').click()"); pg.wait_for_timeout(250)
    ok('O4 Resetta tutto: seconda conferma con parola CANCELLA, pulsante disabilitato finché non digitata',pg.evaluate("()=>getComputedStyle(document.getElementById('resetAllConfirmOverlay2')).display!=='none'&&document.getElementById('resetAllConfirmOk').disabled"))
    pg.evaluate("()=>document.getElementById('resetAllConfirmCancel2').click()"); pg.wait_for_timeout(200)
    ok('O4b annullato: voto ancora presente',pg.evaluate("()=>JSON.parse(localStorage.getItem('marvel-ultimate-timeline-ratings')||'{}')['001']===4.5"))
    # segna tutti: visti, poi "non visti" con conferma
    pg.evaluate("()=>document.getElementById('markAllBtn').click()"); pg.wait_for_timeout(900)
    n=pg.evaluate("()=>[...document.querySelectorAll('.watch-check')].filter(c=>c.checked).length"); ok('O5 Segna tutti visti: %d schede'%n,n>=138,n)
    ok('O5b etichetta cambia in «SEGNA TUTTI NON VISTI»',pg.evaluate("()=>/NON VISTI/.test(document.getElementById('markAllBtn').textContent)"))
    pg.evaluate("()=>document.getElementById('markAllBtn').click()"); pg.wait_for_timeout(300)
    ok('O5c «non visti» chiede conferma e non agisce subito',pg.evaluate("()=>!!document.querySelector('body > .reset-confirm-overlay')&&[...document.querySelectorAll('.watch-check')].filter(c=>c.checked).length>=138"))
    pg.evaluate("()=>document.querySelector('body > .reset-confirm-overlay .reset-confirm-cancel').click()"); pg.wait_for_timeout(200)
    ok('O5d annulla: progresso intatto',pg.evaluate("()=>!document.querySelector('body > .reset-confirm-overlay')&&[...document.querySelectorAll('.watch-check')].filter(c=>c.checked).length>=138"))
    pg.evaluate("()=>document.getElementById('markAllBtn').click()"); pg.wait_for_timeout(300); pg.evaluate("()=>document.querySelector('body > .reset-confirm-overlay .reset-confirm-ok').click()"); pg.wait_for_timeout(800)
    ok('O5e conferma: visti azzerati (semantica del comando invariata)',pg.evaluate("()=>[...document.querySelectorAll('.watch-check')].filter(c=>c.checked).length===0"))
    pg.evaluate("()=>localStorage.removeItem('marvel-ultimate-timeline-ratings')"); pg.reload(); pg.wait_for_timeout(1200); go(pg)
    # ============ XP / missioni senza duplicati ============
    BANK='marvel-ultimate-timeline-missioni-xp-bonus'
    xp0=pg.evaluate("()=>parseInt(document.getElementById('tesseraXpTotale').textContent,10)")
    mark(pg,['001']); xp1=pg.evaluate("()=>parseInt(document.getElementById('tesseraXpTotale').textContent,10)")
    ok('X1 XP: titolo obbligatorio = +30 (regola esistente) (%d→%d)'%(xp0,xp1),xp1-xp0==30,(xp0,xp1))
    pg.evaluate("()=>{const c=document.querySelector('.watch-check[data-item=\"001\"]');c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    t=pg.evaluate("()=>{const e=[...document.querySelectorAll('li.card-wrap[data-tag=\"blu\"]')][0];return e?e.dataset.item:null}")
    if t:
        a=pg.evaluate("()=>parseInt(document.getElementById('tesseraXpTotale').textContent,10)"); mark(pg,[t]); bb=pg.evaluate("()=>parseInt(document.getElementById('tesseraXpTotale').textContent,10)"); ok('X1b titolo consigliato = +20 (%d→%d)'%(a,bb),bb-a==20,(a,bb))
    # completamento missione settimanale: 3 titoli -> +250 una volta sola
    pg.evaluate("()=>{[...document.querySelectorAll('.watch-check')].forEach(c=>{if(c.checked){c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}))}})}"); pg.wait_for_timeout(500)
    bank0=json.loads(pg.evaluate("()=>localStorage.getItem('%s')||'null'"%BANK) or 'null') or {'totale':0,'ricompensate':[]}
    mark(pg,['001','002','003'])
    bank=json.loads(pg.evaluate("()=>localStorage.getItem('%s')"%BANK))
    wk=[k for k in bank['ricompensate'] if k.endswith('-settimanale')]
    ok('X2 missione settimanale completata: ricompensa registrata una volta (+250)',len(wk)==1 and bank['totale']>=250,bank)
    sec(pg,'missioni'); sub(pg,'attive')
    ok('X2b Attive: missione settimanale 3/3 completata',pg.evaluate("()=>document.getElementById('missioneSettimanaleFrac').textContent==='3/3'&&document.getElementById('missioneSettimanale').classList.contains('missione-completa')"))
    pg.evaluate("(k)=>{const b=document.querySelector('.cen-dbtn[data-mission=\"'+k+'\"]');if(b.getAttribute('aria-expanded')!=='true')b.click()}",'settimanale'); pg.wait_for_timeout(300)
    ok('X2c dossier: «Completata · ricompensa già assegnata», titoli registrati con link',pg.evaluate("()=>{const t=document.getElementById('cenDos-settimanale').innerText;return /Completata/.test(t)&&/già assegnata/.test(t)&&document.querySelectorAll('#cenDos-settimanale .cen-work').length>=3}"),pg.evaluate("()=>JSON.stringify([document.getElementById('cenDos-settimanale').innerText,document.querySelectorAll('#cenDos-settimanale .cen-work').length])"))
    pg.wait_for_timeout(1800); xpA=pg.evaluate("()=>parseInt(document.getElementById('tesseraXpTotale').textContent,10)"); pg.reload(); pg.wait_for_timeout(1200); go(pg); xpB=pg.evaluate("()=>parseInt(document.getElementById('tesseraXpTotale').textContent,10)")
    bank2=json.loads(pg.evaluate("()=>localStorage.getItem('%s')"%BANK))
    ok('X3 dopo reload: XP invariati (%d=%d) e nessuna ricompensa duplicata'%(xpA,xpB),xpA==xpB and bank2['ricompensate']==bank['ricompensate'] and bank2['totale']==bank['totale'],(xpA,xpB))
    tab(pg,'appTabMissioni'); sec(pg,'missioni'); sub(pg,'archivio')
    ok('X4 Archivio: missione settimanale conclusa, +250 XP, senza duplicati',pg.evaluate("()=>{const l=[...document.querySelectorAll('#cenArchive .cen-arch-l li')].map(x=>x.innerText);return l.filter(x=>/3 titoli/.test(x)).length===1&&l.some(x=>/\\+250 XP/.test(x))}"))
    ok('X5 nessun errore JS (funzionale)',not errs,errs[:2]); ctx.close()
    # ============ Timeline: strumenti spostati ============
    ctx,pg,errs=boot(b,390,844,atlas=False); go(pg); tab(pg,'appTabTimeline'); pg.wait_for_timeout(300)
    gone=['resetBtn','resetAllBtn','markAllBtn','exportBtn','importBtn','syncGenBtn','syncCodeInput','modalita-confronto','dashboard','database','dashPicker','badgesGrid','cmpTableWrap']
    ok('L1 Timeline senza strumenti amministrativi/avanzati (nessuno visibile)',not any(vis(pg,'#'+i) for i in gone),[i for i in gone if vis(pg,'#'+i)])
    pg.evaluate("()=>document.querySelector('.advanced-filters').open=true"); pg.wait_for_timeout(200)
    ok('L2 Timeline conserva ricerca, filtri priorità, preferiti, weekend, espandi, filtri avanzati/spoiler, progresso',all(vis(pg,s) for s in ('#searchBox','#filterBtns','#favFilterBtn','#weekendFilterBtn','.expand-all-label','#studioBtns','#typeBtns','.spoiler-mode-picker','#progressPct','#cap0','#cover','#indice','.legend-wrap')))
    ok('L2b nessun backup/sync/dark mode tra i filtri avanzati',pg.evaluate("()=>!document.querySelector('.advanced-filters #exportBtn,.advanced-filters .sync-wrap,.advanced-filters label[for=darkModeToggle]')"))
    ok('L3 serie animate raggiungibili (sezione + voce d\'indice)',vis(pg,'#serieanimate') and pg.evaluate("()=>!!document.querySelector('#indice a[href=\"#serieanimate\"]')"))
    ok('L4 footer/promo non presenti in Timeline',not any(vis(pg,s) for s in ('footer.closing','.foot-mark','.bollettino-box')))
    n=pg.evaluate("()=>({s:document.querySelectorAll('li.card-wrap[id^=\"item-\"]:not([data-variant-of])').length,a:document.querySelectorAll('#serieanimate li, #serieanimate .anim-card').length,c0:document.querySelectorAll('#cap0 details.card').length,sec:document.querySelectorAll('section.part[id]').length})")
    ok('L5 contenuti intatti: schede, Capitolo 0 (5), serie animate presenti',n['c0']==5 and n['s']>=138,n)
    # Timeline Riassuntiva
    ok('C1 Timeline Riassuntiva: un solo indice con 9 checkpoint, collassato',pg.evaluate("()=>document.querySelectorAll('#gtimeline').length===1&&document.querySelectorAll('.tl-row').length===9&&!document.querySelector('#gtimeline details').open"))
    pg.evaluate("()=>{const d=document.querySelector('#gtimeline details');d.open=true}"); pg.wait_for_timeout(200)
    hr=pg.evaluate("()=>[...document.querySelectorAll('#gtimeline .tl-row')].map(a=>a.getAttribute('href'))")
    okc=True; fail=[]
    for i,h in enumerate(hr):
        pg.evaluate("()=>window.scrollTo({top:0,behavior:'instant'})"); pg.wait_for_timeout(120)
        pg.evaluate("(i)=>document.querySelectorAll('#gtimeline .tl-row')[i].click()",i); pg.wait_for_timeout(1400)
        y=pg.evaluate("(h)=>{const e=document.querySelector(h);const r=e.getBoundingClientRect();return [r.top,innerHeight]}",h)
        if not (-60<y[0]<y[1]): okc=False; fail.append((h,y))
    ok('C2 i 9 collegamenti portano alla sezione (visibile nel viewport)',okc and len(hr)==9 and all(pg.evaluate("(h)=>!!document.querySelector(h)",h) for h in hr),fail)
    tab(pg,'appTabMissioni'); ok('C3 Timeline Riassuntiva non compare nella Centrale',not vis(pg,'#gtimeline') and not vis(pg,'.tl-row'))
    ok('C4 la Centrale non mostra capitoli/controlli della Timeline',not any(vis(pg,s) for s in ('#cap0','#parte1','.controlbar','#cover','#indice','.dopo-sw','footer.closing','#database')))
    # unicità id
    dup=pg.evaluate("()=>{const m={};document.querySelectorAll('[id]').forEach(e=>m[e.id]=(m[e.id]||0)+1);return Object.keys(m).filter(k=>m[k]>1)}")
    ok('U1 nessun id duplicato (documento)',not dup,dup[:10])
    cnt=pg.evaluate("()=>['dashHoloPct','dashLastNext','nextWatchCard','stagioneTvaCard','roadToDoomsday','dashMissioni','dashPicker','modalita-confronto','cmpTableWrap','badgesGrid','bollettinoBox','resetBtn','markAllBtn','exportBtn','autoBackupHint'].map(i=>document.querySelectorAll('#'+i).length).join()")
    ok('U2 componenti spostati: una sola copia ciascuno',set(cnt.split(','))=={'1'},cnt)
    ok('U3 nessun errore JS (Timeline)',not errs,errs[:2]); ctx.close()
    # ============ layout multi-viewport ============
    for W,Hh in [(320,568),(375,812),(390,844),(393,852)]:
        ctx,pg,errs=boot(b,W,Hh,atlas=False); go(pg); tab(pg,'appTabMissioni')
        for s in ('panoramica','missioni','strumenti','operazioni'):
            sec(pg,s)
            subs=['attive','stagioni','speciali','archivio'] if s=='missioni' else [None]
            for sb in subs:
                if sb: sub(pg,sb)
                ov=pg.evaluate("()=>document.documentElement.scrollWidth-innerWidth")
                m=pg.evaluate("""()=>{const bad=[];document.querySelectorAll('#dashboard .cen-panel:not([hidden]) :is(button,a,summary,input,label):not([type=hidden])').forEach(e=>{const r=e.getBoundingClientRect();if(r.width<2||r.height<2||getComputedStyle(e).visibility==='hidden'||e.closest('[hidden],.reset-confirm-overlay,details:not([open]) > :not(summary)'))return;if(r.height<43.5&&!e.matches('.us-input-wrap *,.badge-chip,.cmp-toggle-arrow,.tva-chip,input[type=file],.dash-picker-btn,.grp-switch-btn'))bad.push([e.className.toString().slice(0,30),e.textContent.trim().slice(0,20),Math.round(r.height)])});const ex=[...document.querySelectorAll('#dashboard .cen-panel:not([hidden]) *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+1||r.left<-1)&&!e.closest('[hidden]')}).slice(0,4).map(e=>e.className.toString().slice(0,30));return {bad:bad.slice(0,6),ex}}""")
                ok('V%d %s%s: nessun overflow orizzontale (%d), nessun elemento fuori schermo, controlli >=44px'%(W,s,'/'+sb if sb else '',ov),ov<=1 and not m['ex'] and not m['bad'],m)
        # etichette tab non tagliate
        ok('V%d etichette delle 4 sezioni intere'%W,pg.evaluate("()=>[...document.querySelectorAll('.cen-tab-l')].every(l=>l.scrollWidth<=l.clientWidth+1)"))
        ok('V%d barra inferiore non copre i contenuti (ultimo elemento della Centrale sopra la barra)'%W,(lambda: (sec(pg,'operazioni'),pg.evaluate("()=>window.scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'})"),pg.wait_for_timeout(200),pg.evaluate("()=>{const bt=document.getElementById('appTabbar').getBoundingClientRect().top;const l=[...document.querySelectorAll('#cenPan-operazioni .cen-card')].pop().getBoundingClientRect().bottom;return l<=bt+1}"))[-1])())
        # confronto
        sec(pg,'strumenti'); pg.evaluate("()=>document.getElementById('cmpToggleTitle').click()"); pg.wait_for_timeout(300)
        pg.evaluate("()=>{const d=document.querySelector('.variant-cmp-details');d.open=true}"); pg.wait_for_timeout(200)
        pg.evaluate("()=>document.querySelector('.variant-cmp-btn').click()"); pg.wait_for_timeout(500)
        cm=pg.evaluate("""()=>{const w=document.getElementById('cmpTableWrap'),t=w.querySelector('table');if(!t)return null;const r=t.getBoundingClientRect();const inp=[...document.querySelectorAll('#cmpInputA,#cmpInputB')].map(i=>[parseFloat(getComputedStyle(i).fontSize),i.getBoundingClientRect().height,i.getBoundingClientRect().width]);return {scroll:w.scrollWidth-w.clientWidth,right:r.right,iw:innerWidth,inp,rows:t.querySelectorAll('tbody tr').length,ov:document.documentElement.scrollWidth-innerWidth,hint:[...w.querySelectorAll('.cmp-scroll-hint')].some(h=>h.getClientRects().length>0)}}""")
        ok('V%d confronto: tabella senza scroll orizzontale, selettori leggibili (>=16px, >=44px), nessun overflow'%W,cm and cm['scroll']<=1 and cm['right']<=cm['iw']+1 and all(i[0]>=16 and i[1]>=43 for i in cm['inp']) and cm['ov']<=1 and not cm['hint'] and cm['rows']>=8,cm)
        if W in (320,390): pg.screenshot(path='/home/claude/outputs/sprint_blocco2_1/dopo_confronto_%d.png'%W)
        ok('V%d nessun errore JS'%W,not errs,errs[:2]); ctx.close()
    b.close()
done()
