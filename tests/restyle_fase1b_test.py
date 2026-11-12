# FASE 1B — barra principale sempre accessibile, nascosta solo nei combattimenti attivi. 320/375/390, emulazione (NON iPhone reale).
import sys,os,json
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
os.makedirs('/tmp/shots',exist_ok=True)
srv,base=start_server()
COVER="""()=>{const tr=document.getElementById('tfRoot');const dlg=(tr&&!tr.hidden&&getComputedStyle(tr).display!='none'?tr:null)||document.querySelector('dialog[open]');const key=e=>(e.id||(e.textContent||'').trim().slice(0,24)||e.tagName);
const els=[...document.querySelectorAll('button,a[href],input,select,summary,textarea')].filter(e=>{if(dlg&&!dlg.contains(e))return false;if(e.disabled||/^Salta al/.test(e.textContent))return false;if(!e.checkVisibility({checkVisibilityCSS:true,contentVisibilityAuto:true}))return false;const r=e.getBoundingClientRect();return r.width>4&&r.height>4});
const hs=el=>{for(let n=el.parentElement;n;n=n.parentElement){const o=getComputedStyle(n).overflowX;if((o=='auto'||o=='scroll')&&n.scrollWidth>n.clientWidth+1)return true}return false};
const res=[];for(const e of els){const r=e.getBoundingClientRect();if(r.right>innerWidth+1||r.left<-1){if(!hs(e))res.push([key(e),'fuori-schermo']);continue}
 if(r.bottom<0||r.top>innerHeight)continue;const x=Math.min(Math.max(r.left+r.width/2,1),innerWidth-1),y=Math.min(Math.max(r.top+r.height/2,1),innerHeight-1);const t=document.elementFromPoint(x,y);
 const cov=!!(t&&t!==e&&!e.contains(t)&&!t.contains(e)&&!t.closest('#tfToast'));res.push([key(e),cov?'coperto da '+(t.id||t.className||t.tagName).toString().slice(0,24):'ok'])}return res}"""
SC="(()=>{const b=document.getElementById('tfBody');const t=document.getElementById('tfRoot');return (t&&!t.hidden&&getComputedStyle(t).display!='none'&&b&&b.scrollHeight>b.clientHeight)?b:document.scrollingElement})"
def scan(pg,label,ctx=None):
    ctx=ctx or pg
    H=ctx.evaluate("()=>("+SC+")().scrollHeight");free={};cov={};y=0
    while y<=H:
        ctx.evaluate("y=>("+SC+")().scrollTo(0,y)",y);pg.wait_for_timeout(50)
        for k,s in ctx.evaluate(COVER):
            if s=='ok': free[k]=1
            else: cov.setdefault(k,s)
        y+=220
    ctx.evaluate("()=>("+SC+")().scrollTo(0,0)")
    bad=[(k,s) for k,s in cov.items() if k not in free];ck(not bad,label,bad[:4])
VIS="""()=>{const vv=[...document.querySelectorAll('.tva-ov-bar')].filter(b=>b.checkVisibility()&&b.getBoundingClientRect().height>10);const real=document.getElementById('appTabbar');const dlg=document.getElementById('tvaArenaDialog');const tr=document.getElementById('tfRoot');const overlay=(dlg&&dlg.open)||(tr&&!tr.hidden&&getComputedStyle(tr).display!='none');
 const b=vv[0]||((!overlay&&real.checkVisibility())?real:null);if(!b)return null;const r=b.getBoundingClientRect();return {top:Math.round(r.top),bottom:Math.round(r.bottom),h:Math.round(r.height),vh:innerHeight,ov:!!vv.length,n:b.querySelectorAll('.app-tab').length,act:[...b.querySelectorAll('.app-tab')].map(t=>t.classList.contains('app-tab-active')||t.classList.contains('ov-on')?(t.querySelector('.app-tab-lbl').textContent.trim()):'').filter(Boolean)}}"""
def bar(pg): return pg.evaluate(VIS)
def bar_ok(pg,lab,act=None):
    r=bar(pg);ok=bool(r) and r['bottom']>=r['vh']-1 and r['n']==7 and r['h']>=44
    if act and ok: ok=act in ' '.join(r['act'])
    ck(ok,lab,r)
def gone(pg,lab):
    r=bar(pg);ck(r is None,lab,r)
def arena_open(pg,mode='pve'):
    pg.tap('#appTabArena');pg.wait_for_timeout(450)
    if mode=='pve': pg.tap('#tvaArenaPve');pg.wait_for_timeout(1700);return [f for f in pg.frames if 'multiverse-arena' in f.url][0]
def prog(pg): return pg.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(/watched|xp|rank|badge|mission|progress|tva_arena_(campaign|quiz)/i.test(k))o[k]=localStorage.getItem(k)}return o}")
with sync_playwright() as p:
    b=p.chromium.launch()
    for W,H in((320,568),(375,667),(390,844)):
        c=newctx(b,W,H);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));enter(pg,base)
        pg.on('dialog',lambda d:(setattr(pg,'last_dialog',d.message),d.accept() if getattr(pg,'accept',True) else d.dismiss()))
        # --- 1 barra principale nelle sezioni
        before=prog(pg)
        ck(pg.evaluate("()=>[...document.querySelectorAll('#appTabbar .app-tab-lbl')].map(l=>l.textContent.trim()).join('|')")=='HOME|TIMELINE|ATLANTE|CENTRALE TVA|TESSERA|FRIENDS|ARENA','N1 %d: sette voci nell\'ordine richiesto'%W)
        ck(pg.evaluate("()=>[...document.querySelectorAll('#appTabbar .app-tab-lbl')].every(l=>l.scrollWidth<=l.clientWidth+1)"),'N2 %d: etichette della barra senza collisioni'%W,pg.evaluate("()=>[...document.querySelectorAll('#appTabbar .app-tab-lbl')].map(l=>[l.textContent.trim(),l.scrollWidth,l.clientWidth])"))
        for tid,lab in(('appTabHome','HOME'),('appTabTimeline','TIMELINE'),('appTabAtlante','ATLANTE'),('appTabMissioni','CENTRALE'),('appTabTessera','TESSERA')):
            pg.tap('#'+tid);pg.wait_for_timeout(450)
            if tid=='appTabAtlante':   # Fase 2B: barra nascosta in Atlante
                ck(pg.evaluate("()=>getComputedStyle(document.getElementById('appTabbar')).display==='none'"),'N3 %d: ATLANTE — barra principale nascosta (Fase 2B)'%W)
                pg.evaluate("()=>{const t=document.getElementById('atlas2Toggle');t.checked=false;t.dispatchEvent(new Event('change',{bubbles:true}))}");pg.wait_for_timeout(300);continue
            bar_ok(pg,'N3 %d: %s — barra fissa in basso, 7 voci, voce attiva evidenziata'%(W,lab),lab)
            ck(pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth"),'N3b %d: %s senza scorrimento orizzontale'%(W,lab))
        ck(pg.evaluate("()=>{const a=document.querySelector('#appTabbar .app-tab-active');const cs=getComputedStyle(a);return /210, 177, 132/.test(cs.backgroundColor)}"),'N4 %d: voce attiva beige/oro'%W)
        _h=open(os.path.join(os.environ['Q_ROOT'],'index.html'),encoding='utf-8').read()
        ck('--sab:env(safe-area-inset-bottom' in _h.replace(' ','') and 'padding: 0 var(--sar) var(--sab) var(--sal)' in _h,'N5 %d: la barra rispetta la safe area (padding var(--sab)=env(safe-area-inset-bottom)) — verificato sul CSS, non su dispositivo'%W)
        # --- 2 Arena: hub, menu, preparazioni, salvataggi
        pg.tap('#appTabArena');pg.wait_for_timeout(500)
        ck(pg.evaluate("()=>[...document.querySelectorAll('.tva-ov-bar .app-tab-lbl')].every(l=>l.scrollWidth<=l.clientWidth+1)"),'N2b %d: etichette della barra dentro Arena senza collisioni'%W,pg.evaluate("()=>[...document.querySelectorAll('.tva-ov-bar .app-tab-lbl')].map(l=>[l.textContent.trim(),l.scrollWidth,l.clientWidth])"))
        bar_ok(pg,'A1 %d: hub Arena — barra visibile, Arena attiva'%W,'ARENA');scan(pg,'A1b %d: hub, nessun controllo coperto'%W)
        pg.screenshot(path='/tmp/shots/b1_hub_%d.png'%W)
        pg.tap('#tvaArenaPve');pg.wait_for_timeout(1700);F=[f for f in pg.frames if 'multiverse-arena' in f.url][0]
        bar_ok(pg,'A2 %d: Arena menu principale — barra visibile'%W,'ARENA')
        r=pg.evaluate("()=>{const f=document.getElementById('tvaArenaFrame').getBoundingClientRect(),b=document.querySelector('.tva-ov-bar').getBoundingClientRect();return [Math.round(f.bottom),Math.round(b.top)]}")
        ck(r[0]<=r[1]+1,'A3 %d: l\'iframe Arena finisce sopra la barra (nessuna sovrapposizione)'%W,r)
        scan(pg,'A4 %d: menu Arena (selezione, preparazione duello/campagna, salvataggi) — controlli accessibili scorrendo'%W,F)
        F.evaluate("()=>window.scrollTo({top:document.scrollingElement.scrollHeight,behavior:'instant'})");pg.wait_for_timeout(300)
        ck(F.evaluate("()=>{const a=[...document.querySelectorAll('.arena-footnav a')].pop().getBoundingClientRect();return a.bottom<=innerHeight+1}"),'A5 %d: in fondo alla pagina l\'ultimo comando resta sopra la barra'%W)
        pg.screenshot(path='/tmp/shots/b2_arenamenu_%d.png'%W)
        ck(F.evaluate("()=>{const q=document.querySelector('.quicknav');const cs=getComputedStyle(q);return (cs.overflowX=='auto'||cs.overflowX=='scroll')&&q.scrollWidth>=q.clientWidth}"),'A6 %d: barra rapida interna con scorrimento orizzontale'%W)
        # --- 3 duello libero
        F.evaluate("()=>{[...document.querySelectorAll('button')].find(b=>/Inizia duello/.test(b.textContent)).click()}");pg.wait_for_timeout(1300)
        gone(pg,'D1 %d: duello PvE attivo — barra nascosta'%W)
        ck(F.is_visible('#mobileFightMenuBtn'),'D2 %d: «Menu Arena» (pausa) raggiungibile nel duello'%W)
        pg.screenshot(path='/tmp/shots/b3_duel_%d.png'%W)
        F.locator('#mobileFightMenuBtn').tap();pg.wait_for_timeout(500)
        bar_ok(pg,'D3 %d: duello in pausa (menu) — barra visibile'%W,'ARENA')
        # uscita con duello in corso: conferma
        pg.accept=False;pg.last_dialog=None;pg.tap('.tva-ov-bar [data-ov="appTabHome"]');pg.wait_for_timeout(500)
        ck(bool(pg.last_dialog) and 'duello' in pg.last_dialog and pg.evaluate("()=>document.getElementById('tvaArenaDialog').open"),'D4 %d: uscire dalla barra con duello in pausa chiede conferma; «Annulla» resta in Arena'%W,pg.last_dialog)
        pg.last_dialog=None;pg.tap('#tvaArenaClose');pg.wait_for_timeout(400)
        ck(bool(pg.last_dialog) and pg.evaluate("()=>document.getElementById('tvaArenaDialog').open"),'D5 %d: «Chiudi Arena» con duello in corso chiede conferma; «Annulla» resta'%W,pg.last_dialog)
        pg.accept=True
        F.locator('#mobileFightBackBtn').tap();pg.wait_for_timeout(500);gone(pg,'D6 %d: ripresa del duello — barra di nuovo nascosta'%W)
        F.evaluate("()=>{game.c.hp=1;game.c.shield=0;game.c.evadeReady=false;game.p.powerBonus=500;game.p.stun=0;game.p.energy=100;game.p.hp=game.p.maxHP}")
        F.locator('#moves button:not(:disabled)').first.tap();pg.wait_for_timeout(1500)
        bar_ok(pg,'D7 %d: fine duello — la barra riappare'%W,'ARENA');pg.screenshot(path='/tmp/shots/b4_duelend_%d.png'%W)
        # --- 4 campagna
        F.evaluate("()=>{document.getElementById('campaignHero').value='ironman';document.getElementById('campaignStart').click()}");pg.wait_for_timeout(1400)
        gone(pg,'K1 %d: scontro con il boss — barra nascosta'%W)
        F.locator('#mobileFightMenuBtn').tap();pg.wait_for_timeout(500)
        bar_ok(pg,'K2 %d: Pausa campagna — barra visibile; «Riprendi campagna» presente'%W,'ARENA')
        ck(F.is_visible('#mobileFightBackBtn'),'K2b %d: «Riprendi campagna» visibile'%W)
        pg.accept=False;pg.last_dialog=None;pg.tap('.tva-ov-bar [data-ov="appTabHome"]');pg.wait_for_timeout(500)
        ck(not pg.last_dialog and not pg.evaluate("()=>document.getElementById('tvaArenaDialog').open"),'K3 %d: uscire dalla campagna non chiede conferma (salvata) e porta alla Home'%W,pg.last_dialog)
        pg.accept=True
        st=pg.evaluate("()=>JSON.parse(localStorage.getItem('tva_arena_pve_save_v34')||'null')");ck(bool(st and st.get('campaign')),'K4 %d: campagna salvata all\'uscita (nessuna perdita)'%W)
        F=arena_open(pg);pg.wait_for_timeout(300)
        # ripresa e vittoria boss
        if F.evaluate("()=>document.body.dataset.campaignView")=='menu': F.locator('#mobileFightBackBtn').tap();pg.wait_for_timeout(300)
        gone(pg,'K5 %d: ripresa dopo il rientro — barra nascosta'%W)
        F.evaluate("()=>{game.c.hp=1;game.c.shield=0;game.c.evadeReady=false;game.p.powerBonus=500;game.p.stun=0;game.p.energy=100;game.p.hp=game.p.maxHP}")
        F.locator('#moves button:not(:disabled)').first.tap();pg.wait_for_timeout(700)
        ck(F.evaluate("()=>document.body.dataset.campaignView")=='break','K6 %d: schermata di passaggio'%W)
        bar_ok(pg,'K7 %d: passaggio/riepilogo — barra riappare'%W,'ARENA');scan(pg,'K7b %d: passaggio, controlli accessibili'%W,F)
        pg.screenshot(path='/tmp/shots/b5_break_%d.png'%W)
        # --- 5 Quiz
        pg.tap('.tva-ov-bar [data-ov="appTabArena"]');pg.wait_for_timeout(300)
        pg.evaluate("()=>{const d=document.getElementById('tvaArenaDialog');if(d.open)d.close()}");pg.wait_for_timeout(300)
        pg.tap('#appTabArena');pg.wait_for_timeout(400);pg.tap('#tvaArenaQuiz');pg.wait_for_timeout(500)
        bar_ok(pg,'Q1 %d: Quiz (scelta) — barra visibile, Arena attiva'%W,'ARENA');scan(pg,'Q1b %d: Quiz scelta, controlli accessibili'%W)
        pg.tap('#tfSolo5');pg.wait_for_timeout(400);bar_ok(pg,'Q2 %d: Quiz, domanda — barra visibile'%W,'ARENA')
        pg.screenshot(path='/tmp/shots/b6_quiz_%d.png'%W)
        for _ in range(5):
            pg.locator('.tf-opt').first.tap();pg.wait_for_timeout(120);pg.locator('#tfNext').tap();pg.wait_for_timeout(200)
        ck(pg.evaluate("()=>!!document.querySelector('.tf-result')"),'Q3 %d: risultato del quiz mostrato'%W)
        bar_ok(pg,'Q4 %d: Quiz, risultato — barra visibile'%W,'ARENA');scan(pg,'Q4b %d: risultato, controlli accessibili'%W)
        # da Friends/Arena verso altre sezioni
        pg.tap('.tva-ov-bar [data-ov="appTabTimeline"]');pg.wait_for_timeout(500);bar_ok(pg,'Q5 %d: dalla barra del Quiz si passa alla Timeline'%W,'TIMELINE')
        # --- integrità
        after=prog(pg);keep=[k for k in before if k in after and before[k]!=after[k] and not k.startswith('tva_arena')]
        ck(not keep and all(k in after for k in before),'S1 %d: progressi/XP/missioni/badge non alterati dalla navigazione'%W,keep)
        ck(not errs,'E %d: nessun errore JavaScript'%W,errs[:3]);c.close()
    b.close()
srv.terminate();summary()
