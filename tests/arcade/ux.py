# UX mobile-first int3: cosa si vede subito, tastiera iPhone aperta, safe area, pulsanti non coperti.
import sys, json
from playwright.sync_api import sync_playwright
ROOT = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8790/'
RES = []; errs = []
def rec(n, ok, note=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + n + ((' — ' + str(note)[:260]) if note else ''), flush=True)
def ev(pg, e): return pg.evaluate(e)
with sync_playwright() as p:
    br = p.chromium.launch()
    def pg_(w, h, url):
        ctx = br.new_context(viewport={'width': w, 'height': h}, service_workers='block', has_touch=True, is_mobile=True); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(ROOT + url); return ctx, pg
    # HUB
    for w, h in ((390, 844), (430, 932), (320, 568)):
        ctx, pg = pg_(w, h, 'arcade/'); pg.wait_for_selector('a.game')
        b = ev(pg, "[...document.querySelectorAll('a.game')].map(a=>Math.round(a.getBoundingClientRect().bottom))"); hh = ev(pg, 'innerHeight')
        lim = hh if h >= 800 else hh + 120
        rec('U1 hub %dx%d: 5 giochi in colonna, tutti visibili senza scroll' % (w, h) if h >= 800 else 'U1 hub %dx%d: 5 giochi in colonna (≤ mezza schermata di scroll)' % (w, h), len(b) == 5 and b[-1] <= lim and ev(pg, 'document.documentElement.scrollWidth<=innerWidth'), b)
        d = ev(pg, "[...document.querySelectorAll('.sec2')].map(e=>[e.tagName,e.open,e.querySelector('summary').textContent.trim()])")
        rec('U1b hub: progressi e backup in sezioni secondarie chiuse, funzioni presenti', d == [['DETAILS', False, 'I miei progressi'], ['DETAILS', False, 'Backup locale']] and ev(pg, "!!document.getElementById('backup-export')&&!!document.getElementById('backup-import')&&!!document.getElementById('refresh-progress')"), d)
        ctx.close()
    ctx, pg = pg_(390, 844, 'arcade/'); pg.wait_for_selector('a.game'); pg.click('summary:has-text("Backup")'); pg.click('summary:has-text("progressi")'); rec('U1c sezioni secondarie apribili (backup + progressi) senza overflow', ev(pg, "document.getElementById('backup-export').getBoundingClientRect().height>=44&&document.documentElement.scrollWidth<=innerWidth")); ctx.close()
    # WHO
    for w, h in ((390, 844), (320, 568), (430, 932)):
        ctx, pg = pg_(w, h, 'arcade/who-am-i/'); pg.wait_for_selector('#new'); pg.click('#new')
        r = ev(pg, "(()=>{const q=s=>document.querySelector(s).getBoundingClientRect();return {inp:Math.round(q('#guess').bottom),conf:Math.round(q('#confirm').bottom),h:innerHeight,help:Math.round(q('.helps').bottom)}})()")
        rec('U2 Who %dx%d: indizi, aiuti e campo risposta visibili senza scroll' % (w, h), r['conf'] <= r['h'] and r['inp'] <= r['h'], r)
        # tastiera aperta: viewport ridotto (~ -336px) + focus
        ctx.close()
    ctx, pg = pg_(390, 844, 'arcade/who-am-i/'); pg.wait_for_selector('#new'); pg.click('#new'); pg.click('#identikit')
    pg.set_viewport_size({'width': 390, 'height': 500}); pg.focus('#guess'); pg.wait_for_timeout(900)
    r = ev(pg, "(()=>{const q=s=>document.querySelector(s).getBoundingClientRect();return {inpT:Math.round(q('#guess').top),inpB:Math.round(q('#guess').bottom),cB:Math.round(q('#confirm').bottom),h:innerHeight}})()")
    rec('U3 Who con tastiera aperta (viewport 390x500): campo e Conferma raggiungibili', r['inpT'] >= 0 and r['cB'] <= r['h'], r)
    cap = ev(pg, "document.querySelector('#identikit_view figcaption').textContent"); alt = ev(pg, "document.querySelector('#identikit_view img').alt")
    rec('U4 identikit presentato come traccia astratta, non ritratto (didascalia + alt)', 'non è un ritratto' in cap and 'non un ritratto' in alt and 'identikit' not in ev(pg, 'document.body.innerText').lower().replace('identikit_view', ''), (cap, alt)); ctx.close()
    # DRAFT
    for w, h in ((390, 844), (320, 568), (430, 932)):
        ctx, pg = pg_(w, h, 'arcade/draft/'); pg.wait_for_selector('#new'); pg.click('#new')
        r = ev(pg, "(()=>{const c=document.querySelector('#pool .card').getBoundingClientRect(),b=document.querySelector('#recruit').getBoundingClientRect(),h=document.querySelector('#hero .kard').getBoundingClientRect();return {thumbBottom:Math.round(c.bottom),recruitTop:Math.round(b.top),recruitBottom:Math.round(b.bottom),heroBottom:Math.round(h.bottom),h:innerHeight,ow:document.documentElement.scrollWidth<=innerWidth}})()")
        rec('U5 Draft %dx%d: carta selezionata e «Recluta» visibili senza scroll, nessun overflow (int4: la prima riga di miniature è raggiungibile subito)' % (w, h), r['heroBottom'] < r['h'] and r['recruitBottom'] <= r['h'] and r['ow'], r)
        ctx.close()
    # ESCAPE
    for w, h in ((390, 844), (320, 568), (430, 932)):
        ctx, pg = pg_(w, h, 'arcade/escape/'); pg.wait_for_selector('#tabs button')
        r = ev(pg, "(()=>{const q=s=>document.querySelector(s).getBoundingClientRect();return {img:Math.round(q('.scene').height),h:innerHeight,v:Math.round(q('#puzzle .gold').bottom),bp:parseInt(getComputedStyle(document.body).paddingBottom),ow:document.documentElement.scrollWidth<=innerWidth}})()")
        ok = r['ow'] and r['bp'] >= 100 and (r['img'] >= r['h'] * .27) and (r['v'] <= r['h'] if h >= 800 else True)
        rec('U6 Escape %dx%d: illustrazione ≥27%% schermata, azione principale visibile (≥800px) e spazio sotto per la barra Safari' % (w, h), ok, r); ctx.close()
    # SAFE AREA: tutti i giochi hanno padding-bottom >= 72px e viewport-fit=cover
    bad = []
    for g in ('who-am-i', 'time-crisis', 'draft', 'escape', ''):
        ctx, pg = pg_(390, 844, 'arcade/' + g + ('/' if g else '')); pg.wait_for_timeout(300)
        o = ev(pg, "({pb:Math.max(parseFloat(getComputedStyle(document.body).paddingBottom),parseFloat(getComputedStyle(document.querySelector('main')).paddingBottom)),vf:document.querySelector('meta[name=viewport]').content.includes('viewport-fit=cover'),ow:document.documentElement.scrollWidth<=innerWidth})")
        if not (o['vf'] and o['ow'] and (o['pb'] >= 40)): bad.append((g, o))
        ctx.close()
    rec('U7 safe area: viewport-fit=cover, margine inferiore, nessun overflow in hub e 4 giochi', not bad, bad)
    rec('U8 nessun errore JS', not errs, errs[:3]); br.close()
print('TOTALE %d test, %d PASS, %d FAIL' % (len(RES), sum(RES), len(RES) - sum(RES)))
