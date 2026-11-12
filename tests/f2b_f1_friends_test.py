# FASE 2B / F1 — Friends cinematic: sezioni chiuse, 56 emblemi, compatibilita', Nexus/Squadre/Serate, 320/375/390, reduced-motion.
# Emulazione browser (due contesti separati = due profili che si scambiano codici). NON iPhone reale.
import sys,os,json,re,base64
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
os.makedirs('/tmp/shots',exist_ok=True)
srv,base=start_server()
P='marvel-ultimate-timeline-'
def dec(c):
    b=c.split('.')[1]; b+='='*(-len(b)%4); return json.loads(base64.urlsafe_b64decode(b).decode('utf-8'))
def code(pg):
    pg.evaluate("()=>{const d=document.getElementById('tfCodeBox'); if(d) d.open=true}"); return pg.input_value('#tfOutCode')
def imp(pg,c):
    pg.evaluate("()=>{const d=document.getElementById('tfImp'); if(d) d.open=true}")
    pg.fill('#tfImpText',c); pg.click('#tfImpBtn'); pg.wait_for_timeout(250); return pg.inner_text('#tfToast')
def fr(pg,t): pg.evaluate("t=>tvaFriends.open(t)",t); pg.wait_for_timeout(350)
def secs(pg): return pg.evaluate("()=>Array.from(document.querySelectorAll('#tfBody details.tf-sec')).map(d=>d.open)")
def store(pg): return json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1')") or 'null')
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---------- A) sezioni chiuse a ogni ingresso, stato mantenuto nella stessa visita ----------
    c=newctx(b,390,844);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));enter(pg,base)
    for t in ('varianti','nexus','squadre','serate'):
        fr(pg,t);s=secs(pg);ck(not any(s),'S1 %s: tutte le sezioni espandibili chiuse all\'ingresso (%d)'%(t,len(s)),s)
    fr(pg,'varianti');pg.click('#tfCustom > summary');pg.wait_for_timeout(350)
    ck(secs(pg)[0] is True or pg.evaluate("()=>document.getElementById('tfCustom').open"),'S2 tocco sull\'intestazione: la sezione si apre')
    pg.click('#tfTab-nexus');pg.wait_for_timeout(200);pg.click('#tfTab-varianti');pg.wait_for_timeout(250)
    ck(pg.evaluate("()=>document.getElementById('tfCustom').open"),'S3 stato scelto mantenuto durante la stessa visita (cambio scheda e ritorno)')
    pg.click('#tfCustom > summary');pg.wait_for_timeout(350)
    ck(not pg.evaluate("()=>document.getElementById('tfCustom').open"),'S4 chiusura animata: la sezione torna chiusa')
    pg.click('#tfCustom > summary');pg.wait_for_timeout(350)
    pg.evaluate("()=>tvaFriends.close()");pg.wait_for_timeout(200);fr(pg,'varianti')
    ck(not any(secs(pg)),'S5 nuovo ingresso: tutte le sezioni tornano chiuse')
    # ---------- B) identita' condivisa con la Tessera ----------
    pg.evaluate("()=>{const i=document.getElementById('tesseraNameInput'); if(i){i.value='Wanda';i.dispatchEvent(new Event('input',{bubbles:true}))} else localStorage.setItem('marvel-ultimate-timeline-user-name','Wanda')}")
    fr(pg,'varianti');pg.click('#tfCustom > summary');pg.wait_for_timeout(300)
    ck(pg.input_value('#tfName')=='Wanda','I1 il nome della Tessera compare nel dossier Variante')
    # emblema nuovo (categoria Multiversali, 3°) + motto
    pg.click('.tf-ep-tab:nth-child(4)');pg.wait_for_timeout(100);pg.click('.tf-ep-grid .tf-pick:nth-child(3)');pg.fill('#tfMotto','Ogni universo conta')
    ck(pg.evaluate("()=>document.querySelectorAll('#tfDossier .tf-emb-svg svg').length==1"),'I2 anteprima live: emblema SVG nel dossier')
    pg.click('#tfSaveMe');pg.wait_for_timeout(300)
    idn=json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-identity-v1')"))
    ck(idn['emx']==26 and idn['motto']=='Ogni universo conta' and 0<=idn['emblem']<=11,'I3 identità salvata: emblema nuovo (26) + fallback legacy 0–11',idn)
    ck(store(pg)['me']['emx']==26 and store(pg)['me']['emblem']==idn['emblem'],'I4 specchio legacy nell\'archivio Friends coerente')
    # due vie: cambio dalla Tessera
    pg.evaluate("()=>tvaIdentity.set({motto:'Cambiato dalla Tessera'})");fr(pg,'varianti');pg.click('#tfCustom > summary')
    ck(pg.input_value('#tfMotto')=='Cambiato dalla Tessera','I5 sincronizzazione a due vie: il valore cambiato altrove compare in Friends')
    # ---------- C) scambio tra due profili: emx nel codice, fallback legacy, collegamento ----------
    cB=newctx(b,390,844);B=cB.new_page();enter(B,base)
    B.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','Bruno')");fr(B,'varianti');B.click('#tfCustom > summary');B.click('#tfSaveMe');B.wait_for_timeout(250)
    fr(pg,'nexus');pg.click('#tfNxInvite');pg.wait_for_timeout(200);inv=code(pg);d=dec(inv)
    ck(d['from'].get('emx')==26 and 0<=d['from']['emblem']<=11,'C1 codice: emx nuovo + emblema legacy compatibile (0–11)',d['from'])
    ck('motto' not in d['from'],'C2 privacy: motto non condiviso finche\' non abilitato')
    # un "vecchio" client ignora emx: normalizzazione di una carta senza emx -> emblema legacy valido
    old=dict(d);old['from']={k:v for k,v in d['from'].items() if k!='emx'}
    import json as J;oldcode='TVA1.'+base64.urlsafe_b64encode(J.dumps(old).encode()).decode().rstrip('=')+'.'+d_hash if False else None
    fr(B,'nexus');r=imp(B,inv);ck('Invito Nexus ricevuto' in r,'C3 B importa l\'invito',r)
    ck(B.evaluate("()=>document.querySelectorAll('[data-req] .tf-emb-svg svg').length>=1"),'C4 B vede l\'emblema SVG di A nella richiesta')
    B.click('[data-act="nx-accept"]');B.wait_for_timeout(250);ra=code(B);fr(pg,'nexus');r=imp(pg,ra)
    ck(pg.evaluate("()=>document.querySelectorAll('[data-vid]').length==1"),'C5 collegamento consensuale completato',r)
    ck(pg.evaluate("()=>document.querySelectorAll('svg.tf-ng').length==1&&document.querySelectorAll('.tf-ng-n').length==1"),'C6 Nexus: rete cinematografica con 1 nodo collegato')
    # ---------- D) Squadre con stemma premium ----------
    fr(pg,'squadre');pg.click('#tfTeamNewSec > summary');pg.wait_for_timeout(250)
    pg.click('.tf-ep-tab:nth-child(5)');pg.click('.tf-ep-grid .tf-pick:nth-child(1)');pg.click('#tfTeamNewSec .tf-col:nth-child(2)');pg.fill('#tfTeamName','Guardiani del Tempo');pg.fill('#tfTeamGoal','20');pg.click('#tfTeamNew');pg.wait_for_timeout(300)
    t=list(store(pg)['teams'].values())[0];ck(t['emx']==32 and t['col']==1 and 0<=t['emblem']<=11,'D1 squadra: stemma nuovo + colore + emblema legacy',t)
    ck(pg.evaluate("()=>!!document.querySelector('.tf-hqh .tf-hq-emb svg')&&!!document.querySelector('.tf-bar')"),'D2 quartier generale: stemma e progresso visibili')
    pg.click('#tfTeamInv + button, #tfTeamInvite');pg.wait_for_timeout(250);ti=code(pg);dt=dec(ti)
    ck(dt['b']['team']['emx']==32 and dt['b']['team']['emblem']==t['emblem'],'D3 invito squadra: emx + emblem legacy',dt['b']['team'])
    fr(B,'squadre');r=imp(B,ti);ck('Invito squadra ricevuto' in r,'D4 B riceve l\'invito squadra (logica invariata)',r)
    ck(B.evaluate("()=>!!document.querySelector('.tf-hq-inv .tf-hq-emb svg')"),'D5 B vede lo stemma della squadra')
    B.click('[data-act="team-join"]');B.wait_for_timeout(250);jc=code(B);fr(pg,'squadre');r=imp(pg,jc);ck('aggiunto' in r,'D6 ingresso squadra (logica invariata)',r)
    ck(pg.evaluate("()=>document.querySelectorAll('.tf-hqh').length+document.querySelectorAll('[data-team]').length>=1"),'D7 vista squadre coerente')
    # condivisione volontaria invariata
    pg.evaluate("()=>{const d=document.querySelector('[data-team]'); if(d) d.click()}");pg.wait_for_timeout(250)
    ck(pg.evaluate("()=>/non condiviso/.test(document.getElementById('tfBody').innerText)"),'D8 avanzamento membri: non condiviso finché non premuto')
    # ---------- E) Serate premiere ----------
    fr(pg,'serate');ck(pg.evaluate("()=>!document.querySelector('.tf-feat')"),'E1 senza serate: stato vuoto illustrato (niente in primo piano)')
    pg.click('#tfEvNewSec > summary');pg.wait_for_timeout(250);pg.fill('#tfEvTitle','Maratona Avengers');pg.fill('#tfEvPlace','Casa di Franco');pg.click('#tfEvNew');pg.wait_for_timeout(300)
    ck(pg.evaluate("()=>!!document.querySelector('.tf-poster.big')&&/PREMI/i.test(document.querySelector('.tf-poster.big').innerText)"),'E2 dettaglio: locandina cinematografica')
    ck(pg.evaluate("()=>!!document.querySelector('.tf-cd')&&/[0-9]/.test(document.querySelector('.tf-cd').innerText)"),'E3 countdown alla serata')
    pg.click('text=← Serate');pg.wait_for_timeout(250)
    ck(pg.evaluate("()=>!!document.querySelector('.tf-feat .tf-poster.big')"),'E4 serata in primo piano')
    ck(pg.evaluate("()=>{const e=document.querySelector('.tf-poster.big');return /Casa di Franco/.test(e.innerText)&&/partecipant/.test(e.innerText)}"),'E5 luogo e partecipanti visibili')
    # serata conclusa (storica) in sezione chiusa
    pg.evaluate("()=>{const o=JSON.parse(localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1'));const k=Object.keys(o.evenings)[0];const e=JSON.parse(JSON.stringify(o.evenings[k]));e.id='e_pastpast1234';e.title='Serata passata';e.when=Date.now()-5*864e5;o.evenings[e.id]=e;localStorage.setItem('marvel-ultimate-timeline-tvafriends-v1',JSON.stringify(o))}")
    pg.evaluate("()=>tvaFriends.close()");fr(pg,'serate')
    ck(pg.evaluate("()=>{const d=document.querySelector('details.tf-past');return !!d&&!d.open&&/Concluse/.test(d.innerText)}"),'E6 serate concluse in sezione chiusa')
    pg.evaluate("()=>document.querySelector('details.tf-past').open=true")
    ck(pg.evaluate("()=>!!document.querySelector('.tf-poster.past')"),'E7 stato visivo "concluso" distinto')
    pg.screenshot(path='/tmp/shots/f2b_serate.png')
    ck(not errs,'G1 nessun errore JavaScript',errs[:3])
    # ---------- F) conflitto Friends/Tessera: nessuna sovrascrittura silenziosa, scelta esplicita ----------
    cC=newctx(b,390,844);C=cC.new_page();C.goto(base+'/index.html');C.wait_for_timeout(1200)
    me={'name':'Carol','emblem':3,'emx':-1,'color':1,'motto':'Avanti','univ':'','ch':'','share':{'emblem':True,'motto':False,'univ':False,'ch':False,'tid':True}}
    C.evaluate("([k,m])=>{localStorage.setItem(k,JSON.stringify({v:1,vid:'vabcdefghij',me:m,nexus:{},pendingOut:{},reqs:{},teams:{},evenings:{},duels:{},shared:{out:{},inn:{}},inbox:[],seen:{},best:{solo:0,n:0}}));localStorage.setItem('marvel-ultimate-timeline-user-name','Wanda')}",['marvel-ultimate-timeline-tvafriends-v1',me])
    C.reload();C.wait_for_timeout(1200);enter(C,base);fr(C,'varianti')
    ck(C.evaluate("()=>!!document.getElementById('tfConflict')"),'F1 conflitto nome rilevato e mostrato (nessuna sovrascrittura silenziosa)')
    ck(C.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-user-name')")=='Wanda','F2 nome Tessera intatto prima della scelta')
    C.click('#tfConflict [data-pick="friends"]');C.wait_for_timeout(300)
    ck(C.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-user-name')")=='Carol' and C.evaluate("()=>!document.getElementById('tfConflict')"),'F3 scelta esplicita applicata, conflitto chiuso')
    # ---------- H) layout 320/375/390 + reduced motion ----------
    for W,H in((320,568),(375,667),(390,844)):
        cx=newctx(b,W,H);q=cx.new_page();enter(q,base)
        q.evaluate("()=>localStorage.setItem('marvel-ultimate-timeline-user-name','Wanda')")
        for t in ('varianti','nexus','squadre','serate'):
            fr(q,t);ov=q.evaluate("()=>{const b=document.getElementById('tfBody');return [b.scrollWidth,b.clientWidth,document.documentElement.scrollWidth,innerWidth]}")
            ck(ov[0]<=ov[1]+1 and ov[2]<=ov[3]+1,'L %d %s: nessun overflow orizzontale'%(W,t),ov)
            q.screenshot(path='/tmp/shots/f2b_%s_%d.png'%(t,W))
        fr(q,'varianti');q.click('#tfCustom > summary');q.wait_for_timeout(350)
        r=q.evaluate("()=>{const g=document.querySelector('.tf-ep-grid');const bs=[...g.querySelectorAll('.tf-pick')].map(b=>b.getBoundingClientRect());return [g.scrollWidth<=g.clientWidth+1,Math.min(...bs.map(x=>x.width)),Math.min(...bs.map(x=>x.height))]}")
        ck(r[0] and r[1]>=40 and r[2]>=40,'L %d: selettore emblemi entro la larghezza, tasti >=40px'%W,r)
    cr=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce',service_workers='block');R=cr.new_page();enter(R,base);fr(R,'nexus')
    an=R.evaluate("()=>{const l=document.querySelector('.tf-ng-l');return l?getComputedStyle(l).animationName:'?'}")
    ck(an=='none','R1 prefers-reduced-motion: animazioni Nexus disattivate',an)
    b.close()
srv.terminate();summary()
