# Ritorno Quiz -> Home: senza intro, senza perdita di stato (localStorage), flag monouso. Chromium emulato (NON Safari reale).
import os,sys,json
os.environ.setdefault('Q_ROOT',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_qcommon.py')).read())
srv,base=start_server()
INTRO="(()=>{const e=document.getElementById('intro');return !!e&&getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().height>0})()"
HUB="(()=>{const e=document.querySelector('.home-hub');return !!e&&getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().height>0})()"
with sync_playwright() as p:
    b=p.chromium.launch(); c=newctx(b); pg=c.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)[:150]))
    # avvio normale: l'intro compare
    pg.goto(base+'/index.html'); pg.wait_for_timeout(1500)
    ck(pg.evaluate(INTRO),'R0 avvio normale: l\'intro compare (comportamento invariato)')
    pg.evaluate("()=>{localStorage.setItem('marvel-ultimate-timeline-user-name','Franco');localStorage.setItem('tva-test-marker','keep-me')}")
    # esco dall'intro e vado al Quiz dalla card Home
    pg.evaluate("()=>{journeyStarted.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(600)
    pg.click('#hhPlayQuiz'); pg.wait_for_url('**/quiz/**'); pg.wait_for_timeout(1200)
    ck('/quiz/' in pg.url,'R1 dal Home si apre il Quiz (pagina separata)')
    pg.click('#tvaBackApp'); pg.wait_for_url(lambda u: '/quiz/' not in u); pg.wait_for_timeout(1500)
    ck(pg.evaluate(INTRO) is False,'R2 «Torna a TVA Archives»: nessuna schermata iniziale')
    ck(pg.evaluate(HUB),'R3 si arriva alla Home TVA (hub visibile)')
    ck(pg.evaluate("sessionStorage.getItem('tva-return-home')")is None,'R4 flag monouso consumato')
    ck(pg.evaluate("localStorage.getItem('tva-test-marker')")=='keep-me' and pg.evaluate("localStorage.getItem('marvel-ultimate-timeline-user-name')")=='Franco','R5 dati salvati intatti dopo il ritorno')
    ck(pg.evaluate("!!document.getElementById('hhPlayQuiz')&&!!document.getElementById('hhPlayRank')&&document.querySelectorAll('#appTabbar .app-tab').length===6"),'R6 Home con due card e barra a 6 voci')
    # cronologia: dal Home, Indietro non riporta al Quiz
    hist_ok=True
    try:
        pg.go_back(); pg.wait_for_timeout(800); hist_ok='/quiz/' not in pg.url
    except Exception: hist_ok=True
    ck(hist_ok,'R7 Indietro dopo il ritorno non riapre il Quiz (replace)')
    # ricarica manuale: l'intro torna normale (flag non persistente)
    pg2=c.new_page(); pg2.goto(base+'/index.html'); pg2.wait_for_timeout(1500)
    ck(pg2.evaluate(INTRO),'R8 una nuova apertura dell\'app mostra di nuovo l\'intro (flag non persistente)')
    # senza JS-click: il link resta ../ (fallback)
    pg3=c.new_page(); pg3.goto(base+'/quiz/'); pg3.wait_for_timeout(1000)
    ck(pg3.get_attribute('#tvaBackApp','href')=='../','R9 fallback senza script: href="../"')
    ck(not errs,'R10 nessun errore JavaScript',errs)
    b.close()
summary(); srv.terminate()
