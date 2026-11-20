# Offline: ogni gioco giocabile senza rete dopo una prima visita (SW attivo).
import sys, json
from playwright.sync_api import sync_playwright
ROOT = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8790/'
RES = []; errs = []
def rec(n, ok, note=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + n + ((' — ' + str(note)[:300]) if note else ''), flush=True)
def ev(pg, e): return pg.evaluate(e)
with sync_playwright() as p:
    br = p.chromium.launch(); ctx = br.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.add_init_script("try{sessionStorage.setItem('tva-return-home','1')}catch(e){}")
    pg.goto(ROOT, wait_until='domcontentloaded')
    t = 0
    while t < 60:
        if ev(pg, "navigator.serviceWorker&&navigator.serviceWorker.controller?true:false"): break
        pg.wait_for_timeout(500); t += 1
        if t == 20: pg.reload()
    rec('O0 service worker attivo e in controllo', ev(pg, "!!navigator.serviceWorker.controller"))
    for g in ('', 'who-am-i/', 'time-crisis/', 'draft/', 'escape/'):
        pg.goto(ROOT + 'arcade/' + g); pg.wait_for_timeout(5000)
    pg.goto(ROOT + 'arcade/who-am-i/'); pg.wait_for_selector('#new'); pg.click('#new'); pg.click('#identikit'); pg.fill('#guess', ev(pg, 'state.answer.name')); pg.click('#confirm'); pg.wait_for_timeout(1500)
    ctx.set_offline(True)
    for g, sel, name in (('', 'a.game', 'hub'), ('who-am-i/', '#new', 'Who Am I?'), ('time-crisis/', '#start', 'Time Crisis'), ('draft/', '#new', 'Draft'), ('escape/', '#tabs button', 'Escape')):
        try:
            pg.goto(ROOT + 'arcade/' + g, wait_until='domcontentloaded'); pg.wait_for_selector(sel, timeout=8000); ok = True
        except Exception as e: ok = False
        rec('O1 offline: %s si apre' % name, ok)
    # giocabile offline: Draft con immagini della cinematica, Escape con scene
    pg.goto(ROOT + 'arcade/draft/'); pg.wait_for_selector('#new'); pg.click('#new')
    while ev(pg, "phase==='draft'"):
        if ev(pg, "ORDER[turn]==='A'"): pg.locator('#pool .card').first.click(); pg.click('#recruit'); pg.wait_for_function('!recruiting', timeout=8000)
        else: pg.wait_for_timeout(100)
    pg.click('#auto'); pg.click('#go'); pg.wait_for_timeout(600)
    pg.wait_for_timeout(1500)
    cards = ev(pg, "[...document.querySelectorAll('#stage .fcw .kard .art')].filter(a=>a.querySelector('svg')||(a.querySelector('img')&&a.querySelector('img').complete&&a.querySelector('img').naturalWidth>0)).length")
    rec('O2 Draft offline: partita completa fino alla battaglia con le carte illustrate (ritratti di test da cache o segnaposto SVG)', cards == 2, cards)
    pg.goto(ROOT + 'arcade/escape/'); pg.wait_for_selector('#tabs button'); allimg = []
    for ep in ('santuario', 'ultron', 'simbionte'):
        ev(pg, "loadEp('%s');render()" % ep)
        for r in ev(pg, 'cur().rooms.map(r=>r.id)'):
            ev(pg, "roomId='%s';render()" % r); pg.wait_for_timeout(80); allimg.append(ev(pg, "document.querySelector('.scene img').complete&&document.querySelector('.scene img').naturalWidth>0"))
    rec('O3 Escape offline: tutte le 13 scene visibili', all(allimg) and len(allimg) == 13, allimg)
    pg.goto(ROOT + 'arcade/who-am-i/'); pg.wait_for_selector('#new'); pg.click('#new'); pg.click('#identikit'); pg.wait_for_timeout(400)
    rec('O4 Who Am I offline: identikit caricato', ev(pg, "(()=>{const i=document.querySelector('#identikit_view img');return !!i&&i.complete&&i.naturalWidth>0})()"))
    rec('O5 nessun errore JS offline', not errs, errs[:3]); br.close()
print('TOTALE %d test, %d PASS, %d FAIL' % (len(RES), sum(RES), len(RES) - sum(RES)))
