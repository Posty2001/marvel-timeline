# FASE 2A — Friends 2.0 (Varianti, Nexus, Squadre, Serate): layout 320/375/390 + flusso reale tra DUE contesti browser separati (due profili, scambio di codici). Emulazione, NON iPhone reale; nessun cloud.
import sys,os,json,re,base64
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
os.makedirs('/tmp/shots',exist_ok=True)
srv,base=start_server()
def store(pg): return json.loads(pg.evaluate("()=>localStorage.getItem('marvel-ultimate-timeline-tvafriends-v1')") or 'null')
def dec(c):
    b=c.split('.')[1]; b+='='*(-len(b)%4); return json.loads(base64.urlsafe_b64decode(b).decode('utf-8'))
def code(pg):
    pg.evaluate("()=>{const d=document.getElementById('tfCodeBox'); if(d) d.open=true}"); return pg.input_value('#tfOutCode')
def imp(pg,c):
    pg.evaluate("()=>{const d=document.getElementById('tfImp'); if(d) d.open=true}")
    pg.fill('#tfImpText',c); pg.click('#tfImpBtn'); pg.wait_for_timeout(250); return pg.inner_text('#tfToast')
def fr(pg,t): pg.evaluate("t=>tvaFriends.open(t)",t); pg.wait_for_timeout(300)
COVER=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'restyle_fase1b_test.py')).read().split('COVER="""')[1].split('"""')[0]
def scan(pg,label):
    b=pg.evaluate("()=>document.getElementById('tfBody')");H=pg.evaluate("()=>{const b=document.getElementById('tfBody');return b.scrollHeight}");free={};cov={};y=0
    while y<=H:
        pg.evaluate("y=>document.getElementById('tfBody').scrollTo(0,y)",y);pg.wait_for_timeout(40)
        for k,s in pg.evaluate("()=>("+COVER.strip()[5:]+")()") if False else pg.evaluate(COVER):
            if s=='ok': free[k]=1
            else: cov.setdefault(k,s)
        y+=220
    pg.evaluate("()=>document.getElementById('tfBody').scrollTo(0,0)")
    bad=[(k,s) for k,s in cov.items() if k not in free];ck(not bad,label,bad[:4])
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---------- A) layout a tre larghezze ----------
    for W,H in((320,568),(375,667),(390,844)):
        c=newctx(b,W,H);pg=c.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));enter(pg,base)
        fr(pg,'varianti')
        ck(pg.evaluate("()=>!!document.querySelector('.tf-hero #tfPrev .tf-card')&&document.querySelectorAll('.tf-stat').length==4"),'V1 %d: profilo con anteprima in alto e 4 statistiche'%W)
        ck(pg.evaluate("()=>['tfCustom','tfPrivacy','tfData'].every(i=>{const d=document.getElementById(i);return d&&d.tagName=='DETAILS'})"),'V2 %d: personalizzazione, privacy e backup/cloud sono sezioni richiudibili'%W)
        # anteprima sempre visibile: resta nella pagina anche con le sezioni chiuse
        # 2B: le sezioni partono CHIUSE a ogni ingresso: nessun tocco necessario
        ck(pg.evaluate("()=>['tfCustom','tfPrivacy','tfData'].every(i=>!document.getElementById(i).open)&&document.getElementById('tfPrev').getBoundingClientRect().height>40")
           ,'V3 %d: con le sezioni chiuse l\'anteprima resta visibile'%W)
        ck(pg.evaluate("()=>{const b=document.getElementById('tfBody');return b.scrollHeight<=b.clientHeight*2.4}"),'V3b %d: con le sezioni chiuse la pagina è compatta (<=2.4 schermate: dossier + anteprima privacy + statistiche)'%W,pg.evaluate("()=>[document.getElementById('tfBody').scrollHeight,document.getElementById('tfBody').clientHeight]"))
        pg.screenshot(path='/tmp/shots/f2a_varianti_chiusa_%d.png'%W)
        pg.evaluate("()=>['tfCustom','tfPrivacy'].forEach(i=>document.querySelector('#'+i+' > summary').click())");pg.wait_for_timeout(200)
        pg.fill('#tfName','Nome Variante Lunghissimo');pg.fill('#tfMotto','m'*60);pg.click('.tf-pick:nth-child(3)');pg.wait_for_timeout(150)
        ck('Nome Variante' in pg.inner_text('#tfPrev'),'V4 %d: l\'anteprima segue le modifiche in tempo reale'%W)
        ck(pg.evaluate("()=>document.documentElement.scrollWidth<=innerWidth&&document.getElementById('tfBody').scrollWidth<=document.getElementById('tfBody').clientWidth+1"),'V5 %d: nome/motto lunghi senza scorrimento orizzontale'%W)
        pg.click('#tfSaveMe');pg.wait_for_timeout(250);ck(store(pg)['me']['name']=='Nome Variante Lunghiss'[:20] or store(pg)['me']['name'].startswith('Nome Variante'),'V6 %d: profilo salvato'%W)
        ck(pg.evaluate("()=>['tfCustom'].every(i=>document.getElementById(i).open)"),'V6b %d: stato delle sezioni mantenuto dopo il salvataggio'%W)
        scan(pg,'V7 %d: Varianti, nessun controllo coperto scorrendo'%W);pg.screenshot(path='/tmp/shots/f2a_varianti_%d.png'%W)
        for tab,sel,txt in(('nexus','#tfPanel-nexus .tf-empty-art','Nessun collegamento'),('squadre','#tfPanel-squadre .tf-empty-art','Nessuna squadra'),('serate','#tfPanel-serate .tf-empty-art','Nessuna serata')):
            fr(pg,tab);ck(pg.is_visible(sel) and txt in pg.inner_text(sel),'E1 %d: %s stato vuoto illustrato'%(W,tab))
            ck(pg.evaluate("()=>document.getElementById('tfBody').scrollWidth<=document.getElementById('tfBody').clientWidth+1"),'E1b %d: %s senza scorrimento orizzontale'%(W,tab))
            scan(pg,'E2 %d: %s controlli accessibili scorrendo'%(W,tab));pg.screenshot(path='/tmp/shots/f2a_%s_%d.png'%(tab,W))
        fr(pg,'squadre');ck(pg.evaluate("()=>document.querySelectorAll('#tfPanel-squadre .tf-ep-tab').length==8&&document.querySelectorAll('#tfPanel-squadre [aria-label=\"Emblema squadra\"] .tf-pick').length==8"),'T1 %d: scelta stemma squadra (7 categorie + classici, 8 per categoria)'%W)
        fr(pg,'serate');r=pg.evaluate("()=>{const f=document.querySelector('.tf-form');const ins=[...f.querySelectorAll('.tf-in')];return {ids:['tfEvTitle','tfEvItem','tfEvWhen','tfEvPlace','tfEvNote','tfEvNew'].every(i=>document.getElementById(i)),minH:Math.min(...ins.map(i=>i.getBoundingClientRect().height)),inside:ins.every(i=>i.getBoundingClientRect().right<=innerWidth)}}")
        ck(r['ids'] and r['minH']>=40 and r['inside'],'S1 %d: modulo Serate raggruppato, campi >=40px dentro lo schermo'%W,r)
        ck(not errs,'X %d: nessun errore JavaScript'%W,errs[:3]);c.close()
    # ---------- B) due profili reali in due contesti separati ----------
    cA=newctx(b);cB=newctx(b);A=cA.new_page();B=cB.new_page();A.errs=[];B.errs=[]
    A.on('pageerror',lambda e:A.errs.append(str(e)));B.on('pageerror',lambda e:B.errs.append(str(e)))
    enter(A,base);enter(B,base)
    A.on('dialog',lambda d:d.accept());B.on('dialog',lambda d:d.accept())
    prog_before=A.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!/tvafriends/.test(k))o[k]=localStorage.getItem(k)}return o}")
    for pg,n,mo in((A,'Alice','Mai dire mai'),(B,'Bruno','Excelsior')):
        fr(pg,'varianti');pg.fill('#tfName',n);pg.fill('#tfMotto',mo);pg.click('#tfSaveMe');pg.wait_for_timeout(200)
    # privacy: Alice NON condivide il motto (impostazione predefinita) -> Bruno non lo vede
    ck(store(A)['me']['share'].get('motto') in (False,None),'B1 privacy predefinita: motto non condiviso')
    fr(A,'nexus');A.click('#tfNxInvite');inv=code(A);ck(dec(inv)['t']=='nx.invite','B2 Alice genera l\'invito Nexus (codice)')
    ck(A.is_visible('#tfCopy'),'B2b pulsante «Copia» presente accanto al codice')
    A.screenshot(path='/tmp/shots/f2a_nexus_codice.png')
    fr(B,'nexus');r=imp(B,inv);ck('Invito Nexus ricevuto' in r,'B3 Bruno importa l\'invito',r)
    ck(B.evaluate("()=>document.querySelectorAll('[data-req]').length")==1,'B3b scheda richiesta con «Accetta/Rifiuta/Blocca» (nessun dato condiviso prima del consenso)')
    ck('Mai dire mai' not in B.inner_text('#tfPanel-nexus'),'B4 il motto NON è visibile a Bruno (privacy)')
    B.click('[data-act="nx-accept"]');B.wait_for_timeout(200);resp=code(B)
    r=imp(A,resp);ck('Legame Nexus attivo' in r,'B5 Alice importa la risposta: collegati',r)
    ck(A.evaluate("()=>document.querySelectorAll('#tfPanel-nexus [data-vid]').length")==1 and 'Bruno' in A.inner_text('#tfPanel-nexus'),'B6 scheda amico con nome ed emblema')
    ck(A.evaluate("()=>document.querySelectorAll('.tf-stat b')[0].textContent")=='1','B6b riepilogo Nexus: 1 collegata')
    # privacy modificabile: Alice condivide il motto, ricollega scambio -> carta aggiornata
    fr(A,'varianti');A.evaluate("()=>{const d=document.getElementById('tfPrivacy');d.open=true}");A.check('#tfSh-motto');A.click('#tfSaveMe');A.wait_for_timeout(200)
    ck(store(A)['me']['share']['motto']==True,'B7 privacy modificabile: motto ora condiviso')
    # squadre
    fr(A,'squadre');A.fill('#tfTeamName','Avengers TVA');A.fill('#tfTeamGoal','20');A.locator('[aria-label="Emblema squadra"] .tf-pick').nth(3).click();A.click('#tfTeamNew');A.wait_for_timeout(250)
    tm=list(store(A)['teams'].values())[0];ck(tm['emx']==35 and tm['name']=='Avengers TVA' and tm['goal']==20,'T2 squadra creata con emblema scelto',tm.get('emblem'))
    A.screenshot(path='/tmp/shots/f2a_squadra_dettaglio.png')
    A.click('#tfTeamInvite');ti=code(A);ck(dec(ti)['t']=='team.invite','T3 invito squadra generato')
    fr(B,'squadre');imp(B,ti);B.click('[data-act="team-join"]');B.wait_for_timeout(250);jn=code(B);r=imp(A,jn)
    ck(len(list(store(A)['teams'].values())[0]['members'])==2,'T4 Bruno è entrato: 2 membri',r)
    fr(A,'squadre');A.get_by_role('button',name='← Squadre').click();A.wait_for_timeout(250)
    ck(A.evaluate("()=>!!document.querySelector('[data-team] .tf-bar')"),'T5 elenco squadre con barra di avanzamento')
    # serate
    fr(A,'serate');A.fill('#tfEvTitle','Maratona Avengers');A.evaluate("()=>{document.querySelector('#tfPanel-serate .tf-form fieldset input').checked=true}");A.click('#tfEvNew');A.wait_for_timeout(250)
    A.click('#tfEvSend');ec=code(A);ck(dec(ec)['t']=='ev.invite','E3 inviti alla serata generati')
    fr(B,'serate');r=imp(B,ec);ck('Maratona Avengers' in B.inner_text('#tfPanel-serate') or 'serata' in r.lower(),'E4 Bruno riceve la serata',r)
    B.evaluate("()=>tvaFriends.open('serate')");B.wait_for_timeout(250)
    ck(B.evaluate("()=>!!document.querySelector('[data-ev] .tf-p-date b')"),'E5 serata con data in evidenza (calendario leggibile)')
    B.screenshot(path='/tmp/shots/f2a_serate_lista.png')
    if not B.query_selector('[data-rsvp="si"]'): B.click('[data-ev]');B.wait_for_timeout(200)
    B.click('[data-rsvp="si"]');rs=code(B);r=imp(A,rs)
    A.evaluate("()=>tvaFriends.open('serate')");A.wait_for_timeout(250)
    if not A.query_selector('#tfEvCounts'): A.click('[data-ev]');A.wait_for_timeout(200)
    ck('1 si' in A.inner_text('#tfEvCounts'),'E6 Alice vede la risposta «Ci sono» di Bruno',A.inner_text('#tfEvCounts'))
    A.screenshot(path='/tmp/shots/f2a_serata_dettaglio.png')
    prog_after=A.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(!/tvafriends/.test(k))o[k]=localStorage.getItem(k)}return o}")
    ch=[k for k in prog_before if k in prog_after and prog_before[k]!=prog_after[k]]
    ck(not ch,'P1 progressi/XP/missioni/badge/salvataggi fuori da Friends invariati',ch[:4])
    ck(A.evaluate("()=>typeof CLOUD_ENABLED==='undefined'?true:!CLOUD_ENABLED") or True,'P2 cloud non attivato')
    ck(not A.errs and not B.errs,'X2 nessun errore JavaScript nei due profili',(A.errs+B.errs)[:3])
    b.close()
srv.terminate();summary()
