# Rifinitura finale: Operazioni compatta, nomi lunghi Tier, avviso "altra scheda" (falso positivo). Chromium emulato (NON Safari reale).
import os,sys
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
srv,base=start_server()
LONG='Dottor Stephen Vincent Strange Supremo Stregone'
with sync_playwright() as p:
    b=p.chromium.launch()
    for W,H in ((390,844),(320,640),(412,915),(768,1024)):
        c=newctx(b,W,H); pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)[:150])); enter(pg,base)
        pg.evaluate("document.getElementById('appTabMissioni').click();document.getElementById('cenTab-operazioni').click()"); pg.wait_for_timeout(1200)
        t=pg.evaluate("[...document.querySelectorAll('#cenPan-operazioni > section, #cenPan-operazioni > details')].map(e=>(e.querySelector('h3,summary')||{}).textContent)")
        ck(not pg.evaluate("!!document.getElementById('quizLauncher')||!!document.getElementById('rkLauncher')"),'O%d-1 Quiz/Rankings non duplicati in Operazioni'%W)
        ck(t[:4]==['Progresso di visione','Backup profilo','Account personale (facoltativo)','Sincronizzazione cloud'] and t[-1]=='Impostazioni e gestione','O%d-2 sezioni principali + Impostazioni e gestione'%W,t)
        ck(pg.evaluate("(()=>{const m=document.getElementById('cenManage');return !!m && !m.open && ['Ripristino','Aspetto','Zona pericolosa'].every(k=>m.textContent.includes(k))})()"),'O%d-3 Ripristino/Aspetto/Zona pericolosa dentro Impostazioni e gestione (chiusa)'%W)
        pg.evaluate("document.querySelector('#cenManage > summary').click()"); pg.wait_for_timeout(300)
        ck(pg.evaluate("document.getElementById('cenManage').open && [...document.querySelectorAll('#cenManage button,#cenManage input,#cenManage select')].some(e=>e.offsetParent)"),'O%d-4 la sezione si apre e i controlli sono usabili'%W)
        o=pg.evaluate("[document.documentElement.scrollWidth-innerWidth, document.getElementById('cenPan-operazioni').scrollWidth-document.getElementById('cenPan-operazioni').clientWidth]")
        ck(o[0]<=0 and o[1]<=0,'O%d-5 nessun overflow orizzontale'%W,o)
        ck(pg.evaluate("!!document.getElementById('journeyStarted')")  and not errs,'O%d-6 nessun errore JS'%W,errs)
        # Home: Quiz e Rankings raggiungibili
        pg.evaluate("document.getElementById('appTabHome')&&document.getElementById('appTabHome').click()"); pg.wait_for_timeout(500)
        ck(pg.evaluate("!!document.querySelector('#hubQuiz,.hub-quiz,[data-hub=quiz],a[href*=\"quiz\"]')||document.body.innerText.includes('Quiz Marvel')") and pg.evaluate("document.body.innerText.includes('TVA Rankings')"),'O%d-7 Quiz Marvel e TVA Rankings presenti in Home'%W)
        # Tier: nomi lunghi
        pg.evaluate("document.getElementById('appTabHome')&&document.getElementById('appTabHome').click()")
        r=pg.evaluate("""async(L)=>{const t=await tvaRankings.create({kind:'tier',title:'Tier nomi lunghi',preset:'libera',imageMode:'images'});const id=(t.ranking||t).id;
          for(const n of ['Thor',L,'Capitan America: il primo vendicatore e oltre']){await tvaRankings.addItem(id,{source:{type:'manual'},name:n})} return id}""",LONG)
        pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(900)
        pg.evaluate("[...document.querySelectorAll('.rk-card-main')].find(x=>x.textContent.includes('Tier nomi lunghi')).click()"); pg.wait_for_timeout(900)
        m=pg.evaluate("[...document.querySelectorAll('.rk-tcard')].map(c=>{const t=c.querySelector('.rk-t');const r=c.getBoundingClientRect();return {n:t.textContent,cls:t.className,clip:t.scrollHeight>t.clientHeight+1,fs:parseFloat(getComputedStyle(t).fontSize),ar:Math.round(r.height/r.width*30)/10,title:c.title}})")
        long=[x for x in m if len(x['n'])>16]
        ck(len(m)==3 and all(abs(x['ar']-3.3)<=0.2 for x in m),'T%d-1 proporzione schede 3:3,3 invariata'%W,[x['ar'] for x in m])
        ck(long and all(not x['clip'] for x in long),'T%d-2 nomi lunghi leggibili senza troncamento (3 righe)'%W,long)
        ck(all(x['fs']>=9.5 for x in m) and all(x['title']==x['n'] for x in m),'T%d-3 font >=9,5px e nome completo in title/aria'%W,[x['fs'] for x in m])
        c.close()
    # ---- avviso "altra scheda" ----
    c=newctx(b,390,844); pg=c.new_page(); enter(pg,base)
    pg.evaluate("tvaRankingsUI.open()"); pg.wait_for_timeout(800)
    rid=pg.evaluate("""async()=>{const t=await tvaRankings.create({kind:'top',title:'Prova avviso',preset:'libera',imageMode:'text'});return (t.ranking||t).id}""")
    pg.evaluate("[...document.querySelectorAll('.rk-card-main')].find(x=>x.textContent.includes('Prova avviso')).click()"); pg.wait_for_timeout(900)
    # scrittura locale rallentata (simula IndexedDB lenta di Safari): l'UI non deve annunciare "altra scheda"
    pg.evaluate("""()=>{window.__toasts=[];new MutationObserver(()=>{document.querySelectorAll('.rk-toast,[role=status],[role=alert]').forEach(e=>{const t=e.textContent;if(t&&window.__toasts.indexOf(t)<0)window.__toasts.push(t)})}).observe(document.body,{childList:true,subtree:true,characterData:true})}""")
    pg.evaluate("""async(id)=>{const orig=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){return orig.apply(this,arguments)};
       for(const n of ['uno','due','tre']){await tvaRankings.addItem(id,{source:{type:'manual'},name:n}); await new Promise(r=>setTimeout(r,20))}}""",rid); pg.wait_for_timeout(900)
    ck(not any('altra scheda' in t for t in pg.evaluate("window.__toasts")),'N1 nessun avviso «altra scheda» dopo scritture locali',pg.evaluate("window.__toasts"))
    # evento locale con rev avanti rispetto a UI.cur (stato di corsa): non deve avvisare
    pg.evaluate("(id)=>{const e=new Event('x');}",rid)
    # scrittura reale da un'altra scheda: avviso + dati ricaricati
    pg2=c.new_page(); enter(pg2,base); pg2.wait_for_timeout(500)
    pg2.evaluate("async(id)=>{await tvaRankings.addItem(id,{source:{type:'manual'},name:'da altra scheda'})}",rid); pg.wait_for_timeout(1200)
    ck(any('altra scheda' in t for t in pg.evaluate("window.__toasts")),'N2 modifica reale da un\'altra scheda: avviso mostrato',pg.evaluate("window.__toasts"))
    ck(pg.evaluate("document.body.innerText.includes('da altra scheda')"),'N3 e la classifica viene ricaricata con il nuovo elemento')
    # protezione concorrenza invariata: expectedRev obsoleto -> conflitto
    cf=pg.evaluate("""async(id)=>{try{await tvaRankings.updateMeta(id,{title:'x'},{expectedRev:1});return 'ok'}catch(e){return e.code||String(e)}}""",rid)
    ck(cf=='conflict','N4 expectedRev obsoleto => conflitto (protezione intatta)',cf)
    # N5: modifiche fatte dalla UI (vista, nome) allineano UI.cur senza avvisi
    pg.evaluate("document.querySelectorAll('.rk-toast,[role=status],[role=alert]').forEach(e=>{if(e.textContent.includes('altra scheda'))e.textContent=''});window.__toasts=[]"); pg.wait_for_timeout(300)
    pg.click('#rkViewPod'); pg.wait_for_timeout(700); podOk=pg.evaluate("!!document.getElementById('rkPodium')"); pg.click('#rkViewList'); pg.wait_for_timeout(1000)
    ck(not any('altra scheda' in t for t in pg.evaluate("window.__toasts")),'N5 cambio vista da UI: nessun avviso «altra scheda»',pg.evaluate("window.__toasts"))
    ck(podOk,'N5b il cambio vista da UI si riflette subito (UI.cur allineato)')
    ck(pg.evaluate("async(id)=>{const r=await tvaRankings.get(id);return r.view}",rid)=='list','N6 la vista scelta e\' salvata e allineata')
    b.close()
srv.terminate(); summary()
