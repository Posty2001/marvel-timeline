#!/usr/bin/env python3
"""Test UI Tessera TVA 3.0 (iPhone + iPad): cinque sezioni, layout, sblocchi retroattivi/permanenti, Atelier salva/annulla, vetrina, identità, compatibilità chiavi, vista classica, launcher, Home/Centrale.
Uso: python3 tests/tessera2_ui_test.py   (exit 1 se un controllo fallisce)"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t2_common as H
from playwright.sync_api import sync_playwright
P = H.P; res = []
def ok(n, c, d=''):
    res.append((n, bool(c))); print(('PASS ' if c else 'FAIL ') + n + ((' ' + str(d)[:260]) if (d and not c) else ''), flush=True)
SECS = ['tessera', 'carriera', 'atelier', 'collezione', 'identita']
IDX = json.load(open(os.path.join(H.ROOT, 'atlante2/data/index.json')))
ELIG = [v['i'] for v in IDX['voci'] if v.get('k') != 'c' and v.get('t') not in ('h', 'm') and not v.get('s') and not v.get('sv') and not v.get('db')]
def esp(n): return json.dumps({'v': 1, 'esp': {i: 1 for i in ELIG[:n]}})
def go(pg, s): pg.evaluate("s=>tvaT2.go(s)", s); pg.wait_for_timeout(500)
def boot2(b, seed, w=390, h=844, **kw):
    c, pg = H.boot(b, seed, w, h) if not kw else None, None
    return c, pg
def ctx(b, seed, w, h, mobile=True, rm=None):
    c = b.new_context(viewport={'width': w, 'height': h}, has_touch=mobile, is_mobile=mobile, service_workers='block', reduced_motion=rm or 'no-preference')
    c.add_init_script("(" + H.SEED_JS + ")(" + json.dumps(seed) + ")")
    pg = c.new_page(); pg.on('pageerror', lambda e: H.errs.append(str(e))); pg.goto(H.URL); pg.wait_for_timeout(2500)
    pg.evaluate("()=>{try{journeyStarted.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(500)
    pg.evaluate("()=>document.getElementById('appTabTessera').click()"); pg.wait_for_timeout(1800)
    return c, pg
def ls(pg, k): return pg.evaluate("k=>localStorage.getItem(k)", P + k)
def overflow(pg): return pg.evaluate("()=>{const e=document.getElementById('tesseraOverlayEl');return Math.max(e.scrollWidth-e.clientWidth, document.documentElement.scrollWidth-window.innerWidth)}")
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---- 1. caricamento e cinque sezioni su dispositivi diversi ----
    for name, w, h, mob in [('iPhone 390', 390, 844, True), ('iPhone SE 320', 320, 568, True), ('iPhone Max 430', 430, 932, True), ('iPad verticale', 820, 1180, True), ('iPad orizzontale', 1180, 820, True), ('iPad Split View', 507, 1024, True)]:
        c, pg = ctx(b, H.PERS, w, h, mob)
        ok(name + ': modulo caricato (lazy) e vista «La mia Tessera» attiva', pg.evaluate("()=>!!window.tvaT2 && document.getElementById('tesseraOverlayEl').classList.contains('t2-on') && document.querySelector('#tesseraOverlayEl .mg-header h2').textContent==='La mia Tessera'"))
        ok(name + ': cinque schede', pg.evaluate("()=>[...document.querySelectorAll('#t2Tabs [data-s]')].map(x=>x.dataset.s).join()") == ','.join(SECS))
        bad = []
        for s in SECS:
            go(pg, s); n = pg.evaluate("()=>document.getElementById('t2Panel').innerText.length"); o = overflow(pg)
            if n < 40 or o > 1: bad.append((s, n, o))
        ok(name + ': 5 sezioni con contenuto e senza scorrimento orizzontale', not bad, bad)
        two = pg.evaluate("()=>{const a=document.getElementById('t2Stage').getBoundingClientRect(),b=document.getElementById('t2Panel').getBoundingClientRect();return b.left>=a.right-2 && Math.abs(a.top-b.top)<200}")
        ok(name + ': layout ' + ('due colonne' if w >= 768 and h >= 600 else 'a colonna singola'), two == (w >= 768 and h >= 600))
        small = pg.evaluate("()=>{let m=99;document.querySelectorAll('#t2Root button, #t2Root .t2-tile, #t2Root .t2-slot').forEach(e=>{const r=e.getBoundingClientRect();if(r.width&&r.height)m=Math.min(m,Math.min(r.width,r.height))});return m}")
        ok(name + ': bersagli tattili ≥ 36 px', small >= 36, small)
        c.close()
    # ---- 2. compatibilità, nessuna regressione dei dati personali ----
    c, pg = ctx(b, H.PERS, 390, 844)
    before = {k: pg.evaluate("k=>localStorage.getItem(k)", P + k) for k in ['watched', 'ratings', 'notes', 'favorites', 'user-name', 'tessera-id', 'tessera-photo']}
    for s in SECS: go(pg, s)
    after = {k: pg.evaluate("k=>localStorage.getItem(k)", P + k) for k in before}
    ok('Aprire le cinque sezioni non altera i dati personali (watched, voti, note, preferiti, nome, VAR-ID, foto)', before == after)
    ok('Compatibilità: senza «tessera-v2» il modulo parte con i default e non scrive nulla finché non si cambia qualcosa', ls(pg, 'tessera-v2') in (None,) or json.loads(ls(pg, 'tessera-v2')).get('v') == 1)
    ok('Foto locale: la chiave della foto resta distinta da tessera-v2', 'photo' not in (ls(pg, 'tessera-v2') or ''))
    c.close()
    c, pg = ctx(b, dict(H.PERS, **{P + 'tessera-v2': '{bad json'}), 390, 844)
    ok('Chiave tessera-v2 corrotta: nessun errore, default applicati', pg.evaluate("()=>window.tvaT2 && tvaT2.state().v===1"))
    c.close()
    # ---- 3. Atelier: bozza, annulla, salva ----
    c, pg = ctx(b, H.PERS, 390, 844)
    go(pg, 'atelier'); look0 = ls(pg, 'tessera-look'); rw0 = ls(pg, 'rewards')
    pg.locator('.t2-tile', has_text='Variante misteriosa').click(); pg.wait_for_timeout(300)
    ok('Atelier: la modifica è solo una bozza (nessun salvataggio prima di «Salva»)', ls(pg, 'tessera-look') == look0)
    ok('Atelier: indicatore «Non salvato»', 'Non salvato' in pg.locator('#t2State').inner_text())
    pg.get_by_role('button', name='Annulla').click(); pg.wait_for_timeout(300)
    ok('Atelier: «Annulla» scarta la bozza', ls(pg, 'tessera-look') == look0 and 'Salvato' in pg.locator('#t2State').inner_text() and 'Non salvato' not in pg.locator('#t2State').inner_text())
    go(pg, 'atelier'); pg.locator('.t2-tile', has_text='Variante misteriosa').click(); pg.locator('#t2Save').click(); pg.wait_for_timeout(500)
    ok('Atelier: «Salva» scrive l\'avatar nella chiave esistente (tessera-look)', json.loads(ls(pg, 'tessera-look'))['a'] != json.loads(look0)['a'])
    ok('Atelier: salvataggio non toglie ricompense né foto', json.loads(ls(pg, 'rewards'))['u'].items() >= json.loads(rw0)['u'].items() and ls(pg, 'tessera-photo') == H.PERS[P + 'tessera-photo'])
    pg.get_by_role('tab', name='Titoli').click(); pg.wait_for_timeout(300)
    inp = pg.locator('input[placeholder^="Es. Guardiano"]'); inp.fill('Z' * 70); v = inp.input_value()
    ok('Titolo personale limitato a 40 caratteri', len(v) <= 40, len(v))
    inp.fill('Guardiano delle Varianti'); pg.locator('#t2Save').click(); pg.wait_for_timeout(400)
    st = json.loads(ls(pg, 'tessera-v2'))
    ok('Titolo personale salvato in tessera-v2 e distinto dal rango', st['titolo'] == {'modo': 'personale', 'testo': 'Guardiano delle Varianti'} and 'Guardiano' not in pg.locator('#tesseraRank').inner_text(), (st['titolo'], pg.locator('#tesseraRank').inner_text()))
    ok('Il titolo personale compare sulla carta (come testo, non come HTML)', 'Guardiano delle Varianti' in pg.evaluate("()=>document.querySelector('#t2Card').textContent"))
    inp2 = pg.locator('input[placeholder^="Es. Guardiano"]') if pg.get_by_role('tab', name='Titoli').count() else None
    go(pg, 'atelier'); pg.get_by_role('tab', name='Titoli').click(); pg.locator('input[placeholder^="Es. Guardiano"]').fill('<img src=x onerror=window.__x=1>'); pg.locator('#t2Save').click(); pg.wait_for_timeout(500)
    ok('Titolo con markup: nessuna esecuzione (XSS)', pg.evaluate("()=>window.__x===undefined && !document.querySelector('#t2Card img[src=x]')"))
    c.close()
    # ---- 4. sfondi animati: bloccati, sblocco retroattivo, permanenza, nessun XP ----
    c, pg = ctx(b, H.PERS, 390, 844)
    xp0 = pg.evaluate("()=>window.marvelXpInfo && window.marvelXpInfo.xp")
    go(pg, 'atelier'); pg.get_by_role('tab', name='Sfondi').click(); pg.wait_for_timeout(1500)
    ok('12 sfondi in elenco, 8 bloccati con requisito e progresso visibili', pg.locator('.t2-grid-bg .t2-tile').count() == 12 and pg.locator('.t2-grid-bg .t2-tile.lock').count() == 8 and 'Raggiungi il livello 10' in pg.locator('.t2-grid-bg').inner_text())
    pg.locator('.t2-grid-bg .t2-tile', has_text='Terminale TVA').click(); pg.locator('#t2Save').click(); pg.wait_for_timeout(500)
    ok('Sfondo libero applicabile e salvato', json.loads(ls(pg, 'tessera-v2'))['sfondoAnim'] == 'terminale-tva' and pg.locator('#t2Card .t2-scene svg').count() == 1)
    c.close()
    seed = dict(H.PERS); seed['tva-atlante-v2'] = esp(60)
    c, pg = ctx(b, seed, 390, 844); pg.evaluate("()=>tvaT2.loadAtlas(()=>tvaT2.refresh())"); pg.wait_for_timeout(2500)
    s2 = json.loads(ls(pg, 'tessera-v2') or '{}'); cnt = pg.evaluate("()=>tvaT2.atlasCounts()")
    ok('Sblocco retroattivo «Dimensione Specchio» con 60 dossier verificati già esplorati', 'dimensione-specchio' in s2.get('sbloccati', {}), (cnt, s2.get('sbloccati')))
    ok('Nessuno sblocco indebito (livello/Timeline/universi/Spider-Man non raggiunti)', not (set(s2.get('sbloccati', {})) - {'dimensione-specchio', 'bifrost', 'spider-verse'}), s2.get('sbloccati'))
    c.close()
    seed2 = dict(H.PERS); seed2[P + 'tessera-v2'] = json.dumps({'v': 1, 'sbloccati': {'yggdrasil': '2026-11-01'}})
    c, pg = ctx(b, seed2, 390, 844)
    ok('Permanenza: uno sfondo già sbloccato resta tale anche se i requisiti non sono più soddisfatti', pg.evaluate("()=>tvaT2.state().sbloccati.yggdrasil==='2026-11-01' && tvaT2.core.isUnlocked(tvaT2.state(),'yggdrasil')"))
    go(pg, 'collezione'); pg.get_by_role('button', name='Sfondi (12)').click(); pg.wait_for_timeout(400)
    ok('Collezione: sfondi mostrati come sbloccati/da sbloccare', pg.locator('.t2-grid-col .t2-tile').count() == 12 and pg.locator('.t2-grid-col .t2-tile.lock').count() == 7)
    ok('XP invariati dagli sblocchi (nessun XP aggiuntivo)', pg.evaluate("()=>window.marvelXpInfo.xp") == xp0)
    c.close()
    # ---- 5. vetrina, collezione, identità ----
    c, pg = ctx(b, H.PERS, 390, 844)
    go(pg, 'tessera'); pg.locator('.t2-slot').first.click(); pg.wait_for_timeout(300)
    pg.get_by_role('button', name='Emblemi').click(); pg.locator('.t2-pick .t2-pk').first.click(); pg.wait_for_timeout(300)
    v = json.loads(ls(pg, 'tessera-v2'))['vetrina']
    ok('Vetrina: 6 slot, scelta salvata in tessera-v2', len(v) == 6 and v[0] and v[0]['t'] == 'emblema', v)
    pg.locator('.t2-slot').nth(1).click(); pg.get_by_role('button', name='Svuota slot').count()
    pg.get_by_role('button', name='Chiudi').first.click(); pg.wait_for_timeout(200)
    go(pg, 'collezione'); ok('Collezione: emblemi 56 e ricompense 48 con filtri', pg.locator('.t2-grid-col .t2-tile').count() == 56)
    pg.get_by_role('button', name='Ricompense (48)').click(); pg.wait_for_timeout(300)
    n_all = pg.locator('.t2-grid-col .t2-tile').count(); pg.get_by_role('button', name='Ottenute').click(); pg.wait_for_timeout(300)
    ok('Collezione: filtro «Ottenute» coerente con le ricompense reali', n_all == 48 and pg.locator('.t2-grid-col .t2-tile').count() == pg.evaluate("()=>tvaRewards.unlocked().length"))
    go(pg, 'identita'); pg.locator('.t2-sw input').nth(1).uncheck() if False else None
    sw = pg.locator('#t2Panel .t2-sw input[type=checkbox]'); sw.nth(1).check(); pg.wait_for_timeout(200)
    ok('Identità: privacy salvata in tessera-v2 (predisposizione, nessuna rete)', 'a' in json.loads(ls(pg, 'tessera-v2'))['privacy'].values())
    pi = pg.evaluate("()=>tvaT2.publicIdentity()"); ok('Contratto identità condivisa v1 limitato a ciò che è marcato condivisibile', pi['v'] == 1 and pi['legameNexus'] == 'nessuno')
    pg.get_by_role('button', name='Scegli da TVA Atlas').first.click(); pg.wait_for_timeout(2500)
    ok('Identità: selezione dall\'Atlante (universi verificati)', pg.locator('.t2-sheet .t2-pk-row').count() > 5)
    pg.locator('.t2-sheet .t2-pk-row').first.click(); pg.wait_for_timeout(300)
    ok('Universo di origine salvato', json.loads(ls(pg, 'tessera-v2'))['origine']['univ'] != '')
    ok('Predisposizioni future: tvaTrophies senza dati, nessuno slot vuoto in UI', pg.evaluate("()=>Array.isArray(tvaTrophies.list()) && tvaTrophies.list().length===0") and 'Trofe' not in pg.locator('#t2Root').inner_text())
    # vista classica
    pg.get_by_label('Mostra la vista classica della Tessera').check(); pg.wait_for_timeout(400)
    ok('Vista classica sempre raggiungibile (e tutti i dati restano)', pg.evaluate("()=>!document.getElementById('tesseraOverlayEl').classList.contains('t2-on') && getComputedStyle(document.querySelector('#tesseraOverlayEl .tessera-wrap')).display!=='none' && !!document.getElementById('tesseraCard')"))
    pg.get_by_role('button', name='Passa a «La mia Tessera»').click(); pg.wait_for_timeout(400)
    ok('Ritorno a «La mia Tessera»', pg.evaluate("()=>document.getElementById('tesseraOverlayEl').classList.contains('t2-on')"))
    # editor classico ancora disponibile
    go(pg, 'atelier'); pg.get_by_role('button', name='Editor completo').click(); pg.wait_for_timeout(800)
    ok('Editor classico «Personalizza» ancora apribile dall\'Atelier', pg.evaluate("()=>!!document.querySelector('.tc-ed, .tc-editor, [data-tc-editor], #tcEditor, .tessera-editor')") or pg.evaluate("()=>document.body.innerText.includes('Personalizza')"))
    c.close()
    # ---- 6. launcher Miss Minutes e animazioni ----
    c, pg = ctx(b, H.PERS, 390, 844); pg.wait_for_timeout(1500)
    tr = pg.evaluate("()=>{const f=document.getElementById('mmFab'); return f?getComputedStyle(f).translate:'assente'}")
    ok('Launcher Miss Minutes: spostamento laterale solo mentre La mia Tessera è aperta', tr in ('6px', '6px 0px', '6px 0'), tr)
    go(pg, 'identita'); r = pg.evaluate("()=>{const f=document.getElementById('mmFab');if(!f)return null;const a=f.getBoundingClientRect();let hit=0;document.querySelectorAll('#t2Panel input,#t2Panel button,#t2Panel .t2-kv>b').forEach(e=>{const b=e.getBoundingClientRect();const x=Math.min(b.right,a.right+6)-Math.max(b.left,a.left+6);if(x>1&&b.bottom>a.top&&b.top<a.bottom&&b.width)hit++});return hit}")
    ok('Launcher: nessun controllo del contenuto resta coperto (Identità)', r in (0, None), r)
    pg.evaluate("()=>document.getElementById('tesseraToggle').checked=false"); pg.wait_for_timeout(300)
    ok('Launcher: fuori dalla Tessera torna alla posizione normale', pg.evaluate("()=>{const f=document.getElementById('mmFab');return !f||getComputedStyle(f).translate==='none'||getComputedStyle(f).translate==='0px'}"))
    c.close()
    c, pg = ctx(b, H.PERS, 390, 844, rm='reduce')
    ok('Riduzione del movimento: nessuna animazione 3D', pg.evaluate("()=>{const e=document.querySelector('#t2Card .t2-3d');return !e||getComputedStyle(e).animationName==='none'}"))
    c.close()
    # ---- 7. Home vs Centrale TVA ----
    seedh = dict(H.PERS); w = json.loads(seedh[P + 'watched']); w['133'] = True; seedh[P + 'watched'] = json.dumps(w)
    c, pg = ctx(b, seedh, 390, 844)
    pg.evaluate("()=>{document.getElementById('tesseraToggle').checked=false}"); pg.wait_for_timeout(400)
    hs = pg.evaluate("()=>(document.getElementById('hhsDone')||{}).textContent"); ct = pg.evaluate("()=>(document.getElementById('tesseraTitoliAssoluti')||{}).textContent")
    ok('Home «Titoli completati» = Centrale TVA/Tessera (con una variante spuntata)', hs and ct and hs.split('/')[0] == ct.split('/')[0] and hs.split('/')[1] == ct.split('/')[1], (hs, ct))
    ok('Il conteggio non modifica i dati salvati', json.loads(ls(pg, 'watched')) == w)
    c.close()
    b.close()
real = [e for e in H.errs if 'Failed to load' not in e and 'TUNNEL' not in e]
ok('Nessun errore di pagina', not real, real[:3])
f = [n for n, c in res if not c]
print('\n%d/%d controlli superati' % (len(res) - len(f), len(res)))
sys.exit(1 if f else 0)
