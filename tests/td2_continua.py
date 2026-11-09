import sys
from playwright.sync_api import sync_playwright
URL='http://localhost:8124/index.html'
ok=True
def chk(n,c):
    global ok; print('PASS' if c else 'FAIL',n); ok&=bool(c)
NOINLINE="[...document.querySelectorAll('.card-wrap[data-item] > details.card')].filter(d=>d.open && !d.parentNode.classList.contains('td-page')).length===0"
NOPAGE="!document.querySelector('.card-wrap.td-page') && !document.documentElement.classList.contains('td-lock')"
def boot(pg):
    pg.goto(URL); pg.wait_for_timeout(2500)
    pg.evaluate("journeyStarted.checked=true;journeyStarted.dispatchEvent(new Event('change'))")
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={'width':390,'height':844},service_workers='block'); pg=c.new_page()
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    boot(pg)
    pg.evaluate("document.getElementById('appTabHome').click()"); pg.wait_for_timeout(1000)
    tid=pg.evaluate("window.marvelHomeNext && ('item-'+window.marvelHomeNext.id)")
    pg.evaluate("document.getElementById('hhsNextRow').click()"); pg.wait_for_timeout(3000)
    chk('Home > Prossimo titolo: pagina NON aperta', pg.evaluate(NOPAGE))
    chk('scheda NON espansa', pg.evaluate(NOINLINE))
    chk('Home nascosta, Timeline visibile', pg.evaluate("document.getElementById('homeHubExited').checked && document.getElementById('homeHub').style.display==='none'"))
    r=pg.evaluate("(id)=>{var e=document.getElementById(id);var r=e.getBoundingClientRect();return [r.top,r.bottom,innerHeight,e.offsetParent!==null]}",tid)
    chk('la scheda %s e\' in vista nella Timeline %s'%(tid,[round(x) for x in r[:3]]), r[3] and r[1]>0 and r[0]<r[2])
    # il tocco sulla testata apre poi la pagina normalmente
    pg.evaluate("document.querySelector('#%s > details.card > summary').click()"%tid); pg.wait_for_timeout(1200)
    chk('tocco sulla testata: apre la pagina', pg.evaluate("!!document.querySelector('.card-wrap.td-page')"))
    pg.evaluate("document.querySelector('.td2-back').click()"); pg.wait_for_timeout(1500)
    chk('Indietro: chiude, scheda chiusa', pg.evaluate(NOPAGE) and pg.evaluate(NOINLINE))
    # Centrale: prossima / ultima visione (se presenti) -> stesso comportamento
    pg.evaluate("document.getElementById('appTabCentrale') && document.getElementById('appTabCentrale').click()"); pg.wait_for_timeout(1500)
    for cid in ['nextWatchCard','lastWatchedCard']:
        v=pg.evaluate("(function(i){var e=document.getElementById(i);return !!e && e.offsetParent!==null})('%s')"%cid)
        if v:
            pg.evaluate("document.getElementById('%s').click()"%cid); pg.wait_for_timeout(2500)
            chk(cid+': pagina NON aperta, scheda chiusa', pg.evaluate(NOPAGE) and pg.evaluate(NOINLINE))
        else: print('SKIP',cid,'non visibile')
    # stampa
    pg.evaluate("window.dispatchEvent(new Event('beforeprint'))"); pg.wait_for_timeout(600)
    n=pg.evaluate("document.querySelectorAll('.card-wrap[data-item] > details.card[open]').length")
    chk('stampa: schede aperte (%d)'%n, n>100)
    chk('nessun errore JS',not errs); print(errs[:3])
    b.close()
sys.exit(0 if ok else 1)
