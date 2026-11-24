"""TVA Live - test UI mirati (Playwright/Chromium, fixture locali). Uso: python3 tests/live/ui_test.py"""
import copy, datetime as dt, functools, http.server, json, os, re, socketserver, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PK, SK = 'marvel-ultimate-timeline-live-v1', 'marvel-ultimate-timeline-live-state-v1'
T0 = dt.date.today()
def d(n): return (T0 + dt.timedelta(days=n)).isoformat()
def item(key, title, date, kind='movie', conf='provisional', state='upcoming', tl=None, poster='/abc.jpg', prec='day', **kw):
    base = {'key': key, 'kind': kind, 'title': title, 'date': date, 'precision': prec, 'window': None, 'dateIT': None, 'state': state, 'confidence': None if state == 'released' else conf,
            'reason': 'Motivo di test per ' + title, 'timelineId': tl, 'tmdb': None, 'poster': poster, 'signals': ['company'], 'missing': [],
            'sources': [{'name': 'TMDB', 'url': 'https://www.themoviedb.org/movie/1', 'official': False}], 'history': [], 'firstSeen': d(-5), 'updatedAt': d(-5)}
    if conf == 'confirmed' and state != 'released': base['sources'].insert(0, {'name': 'YouTube - Marvel Entertainment', 'url': 'https://www.youtube.com/watch?v=AAAAAAAAAAA', 'official': True})
    base.update(kw); return base
CAL = [item('tmdb:movie:1', 'Known Film', d(200), tl='073', dateIT=d(201)),
       item('tmdb:movie:7', 'Doomsday Test', d(400), conf='confirmed'),
       item('tmdb:tv:61550:S02', 'Known Show - Stagione 2', d(120), kind='season', tl='044'),
       item('tmdb:tv:20:S01', 'Brand New Series', d(300), kind='series', poster=None),
       item('manual:announced-one', 'Announced Without Date', None, state='announced', prec='none', window='2028', poster=None),
       item('tmdb:movie:3', 'Placeholder Saga', d(500)[:4] + '-01-01', prec='year'),
       item('tmdb:movie:8', 'Just Released', d(-3), state='released', conf=None),
       item('tmdb:movie:11', 'Soon Film', d(3))]
TR = [{'key': 'yt:AAAAAAAAAAA', 'title': 'Doomsday Test | Official Trailer', 'published': d(-4), 'url': 'https://www.youtube.com/watch?v=AAAAAAAAAAA', 'channel': 'Marvel Entertainment', 'kind': 'trailer', 'official': True, 'relatesTo': 'tmdb:movie:7'},
      {'key': 'yt:BBBBBBBBBBB', 'title': 'Soon Film | Official Teaser', 'published': d(-6), 'url': 'https://www.youtube.com/watch?v=BBBBBBBBBBB', 'channel': 'Marvel Entertainment', 'kind': 'teaser', 'official': True, 'relatesTo': 'tmdb:movie:11'}]
def manifest(**o):
    m = {'schema': 1, 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'sources': {'tmdb': {'status': 'ok', 'count': len(CAL)}, 'youtube': {'status': 'ok', 'count': 2}, 'news': {'status': 'disabled'}}, 'counts': {}}
    m.update(o); return m
STATE = {}
def reset_state(): STATE.update(cal=copy.deepcopy(CAL), tr=copy.deepcopy(TR), man=manifest(), fail=False)
reset_state()
res = []
def ok(n, c, x=''): res.append((n, bool(c))); print('PASS' if c else 'FAIL', n, x)

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(H, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:%d/index.html' % srv.server_address[1]

def routes(pg):
    def h(r):
        if STATE['fail']: return r.fulfill(status=500, body='')
        n = r.request.url.rsplit('/', 1)[-1].split('?')[0]
        body = {'manifest.json': STATE['man'], 'calendar.json': {'schema': 1, 'items': STATE['cal']}, 'trailers.json': {'schema': 1, 'items': STATE['tr']}}.get(n)
        r.fulfill(status=200, content_type='application/json', body=json.dumps(body)) if body is not None else r.fulfill(status=404, body='')
    pg.route(re.compile(r'.*/assets/live/.*'), h)
    pg.route(re.compile(r'https://posty2001\.github\.io/.*'), lambda r: r.abort('internetdisconnected'))   # endpoint remoto: nei test esistenti non raggiungibile (ripiego sui dati inclusi); i test remoti sono in remote_test.py
    pg.route(re.compile(r'https://image\.tmdb\.org/.*'), lambda r: r.fulfill(status=200, content_type='image/svg+xml', body='<svg xmlns="http://www.w3.org/2000/svg" width="2" height="3"/>'))

def new_ctx(b, w=390):
    return b.new_context(viewport={'width': w, 'height': 820}, accept_downloads=True, service_workers='block')
def open_page(ctx, w=None):
    pg = ctx.new_page(); pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e))); routes(pg)
    pg.goto(URL); pg.wait_for_selector('#item-073', state='attached'); pg.wait_for_timeout(700)
    pg.evaluate("()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(400)
    return pg
def reload(pg):
    pg.reload(); pg.wait_for_selector('#item-073', state='attached'); pg.wait_for_timeout(500)
    pg.evaluate("()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(400)
def go_live(pg, sub=None):
    pg.evaluate("()=>document.getElementById('appTabMissioni').click()"); pg.wait_for_timeout(300)
    pg.evaluate("()=>document.getElementById('cenTab-live').click()"); pg.wait_for_selector('#cenPan-live:not([hidden]) .tvl-sub', state='attached')
    pg.wait_for_function("()=>window.tvaLive && window.tvaLive.data().status==='ok'"); pg.wait_for_timeout(250)
    if sub: pg.evaluate("(s)=>document.getElementById('tvlSub-'+s).click()", sub); pg.wait_for_timeout(150)
def txt(pg, sel='#cenPan-live'): return pg.locator(sel).inner_text()
def overflow(pg): return pg.evaluate("()=>document.documentElement.scrollWidth-window.innerWidth")
def ls(pg, k): return pg.evaluate("(k)=>localStorage.getItem(k)", k)
def jl(pg, k): v = ls(pg, k); return json.loads(v) if v else None

with sync_playwright() as pw:
    b = pw.chromium.launch()
    # ---------- 1. navigazione e struttura ----------
    reset_state(); ctx = new_ctx(b); pg = open_page(ctx)
    ok('nav: nessuna settima voce nella barra principale', pg.locator('#appTabbar .app-tab').count() == 6)
    go_live(pg)
    ok('nav: sezione Live dentro Centrale TVA (5 schede)', pg.locator('.cen-nav .cen-tab').count() == 5 and pg.locator('#cenTab-live').get_attribute('aria-selected') == 'true')
    ok('nav: altre sezioni nascoste, Live visibile', pg.evaluate("()=>[...document.querySelectorAll('.cen-panel')].filter(p=>!p.hidden).map(p=>p.id).join()") == 'cenPan-live')
    pg.evaluate("()=>document.getElementById('cenTab-panoramica').click()"); pg.wait_for_timeout(200)
    ok('nav: tornando a Panoramica Live si nasconde e Panoramica funziona', pg.locator('#cenPan-live').is_hidden() and pg.locator('#cenPan-panoramica').is_visible())
    pg.goto(URL + '#cen-live'); pg.wait_for_timeout(1200)
    pg.evaluate("()=>{try{journeyStarted.checked=true;homeHubExited.checked=true;journeyStarted.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}}"); pg.wait_for_timeout(400)
    ok('nav: ancora #cen-live apre Live', pg.locator('#cenPan-live').is_visible())
    go_live(pg)
    ok('ui: 4 sotto-schede', pg.locator('.tvl-stab').count() == 4)
    ok('ui: stato dati mostra data di aggiornamento', 'aggiornato' in txt(pg, '.tvl-status').lower())
    for w in (320, 340, 360, 375, 414):
        pg.set_viewport_size({'width': w, 'height': 800}); pg.wait_for_timeout(250)
        ok('mobile %dpx: nessun overflow orizzontale (calendario)' % w, overflow(pg) <= 0, overflow(pg))
        for s in ('trl', 'avv', 'pref', 'cal'):
            pg.evaluate("(s)=>document.getElementById('tvlSub-'+s).click()", s); pg.wait_for_timeout(120)
            if overflow(pg) > 0: ok('mobile %dpx: overflow in %s' % (w, s), False, overflow(pg))
        ok('mobile %dpx: schede Centrale a 5 colonne senza overflow' % w, pg.evaluate("()=>[...document.querySelectorAll('.cen-nav .cen-tab')].every(b=>b.getBoundingClientRect().right<=window.innerWidth+0.5)"))
        ok('mobile %dpx: nessuna etichetta delle 5 schede Centrale troncata (Osservatorio intera)' % w, pg.evaluate("()=>[...document.querySelectorAll('.cen-nav .cen-tab-l')].every(l=>l.scrollWidth<=l.clientWidth)"))
        ok('mobile %dpx: tap target sotto-schede >= 44px' % w, pg.evaluate("()=>[...document.querySelectorAll('.tvl-stab')].every(b=>b.getBoundingClientRect().height>=43)"))
    pg.set_viewport_size({'width': 390, 'height': 820})
    # ---------- 2. calendario ----------
    T = txt(pg)
    ok('calendario: prossima uscita con conto alla rovescia', pg.locator('.tvl-hero').count() == 1 and 'tra 3 giorni' in txt(pg, '.tvl-hero') and 'Soon Film' in txt(pg, '.tvl-hero'))
    rows = pg.locator('.tvl-row'); ok('calendario: righe presenti (7 upcoming/annunciati/usciti)', rows.count() >= 7, rows.count())
    ok('calendario: "Confermato" solo con fonte ufficiale', pg.locator('.tvl-row[data-key="tmdb:movie:7"] .tvl-t-conf').count() == 1 and pg.locator('.tvl-row .tvl-t-conf').count() == 1)
    ok('calendario: TMDB-only resta Provvisorio', 'provvisorio' in txt(pg, '.tvl-row[data-key="tmdb:movie:1"]').lower() and 'confermato' not in txt(pg, '.tvl-row[data-key="tmdb:movie:1"]'))
    ok('calendario: data IT mostrata', 'Italia:' in txt(pg, '.tvl-row[data-key="tmdb:movie:1"]'))
    ok('calendario: segnaposto anno -> solo anno indicativo', 'solo anno indicativo' in T or 'data indicativa' in T)
    ok('calendario: annunciato senza data non inventa date', 'annunciati senza data' in T.lower())
    pg.evaluate("()=>document.querySelectorAll('.tvl-grp').forEach(g=>g.open=true)"); pg.wait_for_timeout(100)
    ok('calendario: annunciato mostra finestra dichiarata, mai una data', 'Finestra dichiarata: 2028' in txt(pg, '.tvl-row[data-key="manual:announced-one"]'))
    ok('calendario: usciti di recente separati, senza confidenza', 'uscito' in txt(pg, '.tvl-row[data-key="tmdb:movie:8"]').lower() and 'provvisorio' not in txt(pg, '.tvl-row[data-key="tmdb:movie:8"]').lower())
    ok('calendario: nessuna etichetta "indiscrezione/rumor"', not re.search(r'indiscrezion|rumor', txt(pg, '#cenPan-live .tvl-body').replace('Le indiscrezioni non sono incluse', ''), re.I))
    ok('calendario: titolo senza poster -> segnaposto', pg.locator('.tvl-row[data-key="tmdb:tv:20:S01"] .tvl-ph').count() == 1 and pg.locator('.tvl-row[data-key="tmdb:movie:1"] img.tvl-poster').count() == 1)
    pg.locator('.tvl-row[data-key="tmdb:movie:7"] button:has-text("Perché")').click(); pg.wait_for_timeout(150)
    ok('dettagli: motivo e fonte ufficiale (link https, rel noopener)', 'fonte ufficiale' in txt(pg, '.tvl-row[data-key="tmdb:movie:7"]').lower() and pg.locator('.tvl-row[data-key="tmdb:movie:7"] .tvl-det a[rel="noopener noreferrer"][target="_blank"]').count() >= 1)
    chip = lambda n: pg.locator('.tvl-chip:has-text("%s")' % n).click()
    chip('Film'); pg.wait_for_timeout(100); ok('filtro Film: nessuna serie', pg.locator('.tvl-row[data-key^="tmdb:tv"]').count() == 0 and pg.locator('.tvl-row[data-key="tmdb:movie:1"]').count() == 1)
    chip('Confermati'); pg.wait_for_timeout(100); ok('filtro Confermati: solo confermati', pg.locator('.tvl-row').count() == 1)
    chip('Tutti')
    # ---------- 3. collegamento Timeline ----------
    ok('timeline: voce agganciata mostra "In Timeline", altre "Solo in Live"', 'in timeline' in txt(pg, '.tvl-row[data-key="tmdb:movie:1"]').lower() and 'solo in live' in txt(pg, '.tvl-row[data-key="tmdb:movie:7"]').lower())
    n_cards = pg.evaluate("()=>document.querySelectorAll('li.card-wrap').length")
    pg.locator('.tvl-row[data-key="tmdb:movie:1"] button:has-text("Apri in Timeline")').click(); pg.wait_for_timeout(800)
    ok('timeline: "Apri in Timeline" apre la scheda esistente 073', pg.evaluate("()=>!!document.querySelector('#item-073.td-page, .td2-back')") or pg.evaluate("()=>document.documentElement.getAttribute('data-tva-view')") == 'timeline')
    ok('timeline: nessuna scheda creata o duplicata da Live', pg.evaluate("()=>document.querySelectorAll('li.card-wrap').length") == n_cards and pg.evaluate("()=>document.querySelectorAll('#item-073').length") == 1)
    pg.evaluate("()=>{const t=document.querySelector('.td2-back');if(t)t.click()}"); pg.wait_for_timeout(300)
    # visto
    before_w = ls(pg, 'marvel-ultimate-timeline-watched')
    go_live(pg)
    ok('timeline: lettura dello stato "visto" senza scrivere', ls(pg, 'marvel-ultimate-timeline-watched') == before_w)
    pg.evaluate("()=>{const c=document.querySelector('.watch-check[data-item=\"073\"]');c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}))}"); pg.wait_for_timeout(300)
    go_live(pg); pg.evaluate("()=>window.tvaLive.render()")
    ok('timeline: titolo visto mostrato come visto', 'visto' in txt(pg, '.tvl-row[data-key="tmdb:movie:1"]').lower())
    pg.evaluate("()=>document.getElementById('tvlSub-pref').click()"); pg.wait_for_timeout(100)
    pg.locator('label:has-text("Nascondi i titoli già visti") input').check(); pg.wait_for_timeout(100)
    pg.evaluate("()=>document.getElementById('tvlSub-cal').click()"); pg.wait_for_timeout(100)
    ok('preferenze: "nascondi già visti" nasconde 073', pg.locator('.tvl-row[data-key="tmdb:movie:1"]').count() == 0 and pg.locator('.tvl-row[data-key="tmdb:movie:7"]').count() == 1)
    pg.evaluate("()=>document.getElementById('tvlSub-pref').click()"); pg.locator('label:has-text("Nascondi i titoli già visti") input').uncheck()
    pg.evaluate("()=>{const c=document.querySelector('.watch-check[data-item=\"073\"]');c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}))}")
    ok('errori JS: nessuno finora', not pg.errs, pg.errs)
    ctx.close()

    # ---------- 4. avvisi e preferenze (persistenza) ----------
    reset_state(); ctx = new_ctx(b); pg = open_page(ctx); go_live(pg)
    ok('avvisi: primo avvio senza avvisi (nessun diluvio iniziale)', pg.evaluate("()=>window.tvaLive.unread()") == 0 and jl(pg, SK)['init'] is True and len(jl(pg, SK)['seen']) == len(CAL))
    ok('avvisi: nessun badge al primo avvio', pg.locator('.tvl-badge').count() == 0)
    pg.evaluate("()=>document.getElementById('tvlSub-cal').click()")
    pg.locator('.tvl-row[data-key="tmdb:movie:11"] button:has-text("Segui")').click(); pg.wait_for_timeout(150)
    ok('segui: salvato nelle preferenze (chiave profilo)', jl(pg, PK) and 'tmdb:movie:11' in jl(pg, PK)['followed'])
    ok('segui: lo stato volatile NON finisce nella chiave del profilo', set(jl(pg, PK)) <= {'v', 'cats', 'lead', 'followed', 'muted', 'onlyUnwatched'})
    # nuovo ciclo dati: nuova uscita, cambio data, conferma, nuovo trailer
    STATE['cal'] = copy.deepcopy(CAL)
    STATE['cal'].append(item('tmdb:movie:99', 'Nuova Uscita', d(250)))
    for i in STATE['cal']:
        if i['key'] == 'tmdb:movie:1': i['date'] = d(210)
        if i['key'] == 'tmdb:tv:61550:S02': i['confidence'] = 'confirmed'; i['sources'].insert(0, {'name': 'YouTube', 'url': 'https://www.youtube.com/watch?v=CCCCCCCCCCC', 'official': True})
    STATE['tr'] = copy.deepcopy(TR) + [{'key': 'yt:DDDDDDDDDDD', 'title': 'Nuovo Trailer Ufficiale', 'published': d(0), 'url': 'https://www.youtube.com/watch?v=DDDDDDDDDDD', 'channel': 'Marvel Entertainment', 'kind': 'trailer', 'official': True, 'relatesTo': None}]
    reload(pg); go_live(pg, 'avv'); pg.wait_for_timeout(300)
    A = txt(pg)
    ok('avvisi: nuova uscita', 'Nuova uscita in calendario: Nuova Uscita' in A)
    ok('avvisi: cambio data (da -> a)', 'Data cambiata per Known Film' in A)
    ok('avvisi: provvisorio -> confermato', 'Ora confermato da fonte ufficiale: Known Show' in A)
    ok('avvisi: nuovo trailer', 'Nuovo video ufficiale: Nuovo Trailer Ufficiale' in A)
    ok('avvisi: promemoria titolo seguito (tra 3 giorni)', 'Soon Film esce tra 3 giorni' in A)
    n = pg.locator('.tvl-alert').count(); ok('avvisi: 5 avvisi, tutti non letti', n == 5 and pg.locator('.tvl-unread').count() == 5, n)
    ok('badge: contatore su Centrale TVA, scheda Live e sotto-scheda', all(pg.locator(s + ' .tvl-badge').count() == 1 for s in ('#appTabMissioni', '#cenTab-live', '#tvlSub-avv')) and pg.locator('#cenTab-live .tvl-badge').inner_text() == '5')
    reload(pg); go_live(pg, 'avv')
    ok('avvisi: nessun duplicato dopo ricarica (stessi dati)', pg.locator('.tvl-alert').count() == 5)
    pg.evaluate("()=>window.tvaLive.load(true)"); pg.wait_for_timeout(500)
    ok('avvisi: il promemoria non si ripete', pg.evaluate("()=>window.tvaLive.prefs().inbox.filter(a=>a.t==='soon').length") == 1)
    pg.locator('button:has-text("Segna tutto come letto")').click(); pg.wait_for_timeout(200)
    ok('avvisi: segna tutto come letto azzera i badge', pg.locator('.tvl-badge').count() == 0 and pg.evaluate("()=>window.tvaLive.unread()") == 0)
    pg.locator('.tvl-alert:has-text("Nuova uscita")').first.locator('button:has-text("Vai al calendario")').click(); pg.wait_for_timeout(300)
    ok('avvisi: "Vai al calendario" apre le righe del calendario', pg.locator('#tvlSub-cal.tvl-on').count() == 1)
    pg.evaluate("()=>document.getElementById('tvlSub-avv').click()"); pg.locator('button:has-text("Svuota")').click(); pg.wait_for_timeout(100)
    ok('avvisi: svuota', pg.locator('.tvl-alert').count() == 0 and 'Nessun avviso' in txt(pg))
    # categorie
    pg.evaluate("()=>document.getElementById('tvlSub-pref').click()"); pg.locator('label:has-text("Film") input').first.uncheck(); pg.wait_for_timeout(100)
    pg.evaluate("()=>document.getElementById('tvlSub-cal').click()")
    ok('preferenze: categoria Film disattivata nasconde i film', pg.locator('.tvl-row[data-key^="tmdb:movie"]').count() == 0 and pg.locator('.tvl-row[data-key^="tmdb:tv"]').count() >= 1)
    STATE['cal'].append(item('tmdb:movie:123', 'Film Silenziato', d(260))); pg.evaluate("()=>window.tvaLive.load(true)"); pg.wait_for_timeout(500)
    ok('preferenze: nessun avviso per categorie disattivate', pg.evaluate("()=>window.tvaLive.prefs().inbox.length") == 0)
    # promemoria: lead
    pg.evaluate("()=>document.getElementById('tvlSub-pref').click()"); pg.locator('label:has-text("Film") input').first.check()
    pg.locator('label:has-text("7 giorni prima") input').uncheck(); pg.wait_for_timeout(100)
    ok('preferenze: anticipi salvati', jl(pg, PK)['lead'] == [1, 0])
    ctx.close()

    # ---------- 5. robustezza dati ----------
    reset_state(); STATE['fail'] = True; ctx = new_ctx(b); pg = open_page(ctx)
    pg.evaluate("()=>document.getElementById('appTabMissioni').click()"); pg.evaluate("()=>document.getElementById('cenTab-live').click()"); pg.wait_for_function("()=>window.tvaLive.data().status==='error'"); pg.wait_for_timeout(200)
    ok('errore rete/HTTP: messaggio chiaro, nessun crash, resto dell\'app funziona', 'dati non disponibili' in txt(pg).lower() and not pg.errs and pg.evaluate("()=>document.querySelectorAll('li.card-wrap').length") > 100, pg.errs)
    ok('errore rete: preferenze ancora accessibili', pg.evaluate("()=>document.getElementById('tvlSub-pref').click()") is None and 'categorie' in txt(pg).lower())
    ctx.close()
    reset_state(); STATE['cal'] = [dict(CAL[0], date='non-una-data'), {'key': 'evil', 'title': '<img src=x onerror=alert(1)>'}, dict(CAL[1], title='<img src=x onerror=window.__xss=1>X', poster='/../../evil.jpg', sources=[{'name': 'x', 'url': 'javascript:alert(1)', 'official': True}])]
    STATE['tr'] = [dict(TR[0], url='javascript:alert(1)'), TR[1]]
    ctx = new_ctx(b); pg = open_page(ctx); go_live(pg)
    ok('dati malformati: voci non valide scartate, nessun crash', pg.locator('.tvl-row').count() == 1 and not pg.errs, pg.errs)
    ok('sicurezza: titolo con HTML mostrato come testo, nessuno script eseguito', pg.evaluate("()=>!window.__xss") and pg.locator('.tvl img[src=x]').count() == 0)
    ok('sicurezza: poster con percorso anomalo scartato, URL javascript: non linkato', pg.locator('.tvl-row img.tvl-poster').count() == 0 and pg.locator('.tvl a[href^="javascript"]').count() == 0)
    pg.evaluate("()=>document.getElementById('tvlSub-trl').click()"); pg.wait_for_timeout(100)
    ok('sicurezza: trailer con URL non YouTube scartato', pg.locator('.tvl-row').count() == 1)
    ok('sicurezza: link esterni tutti con rel noopener', pg.evaluate("()=>[...document.querySelectorAll('.tvl a[target=_blank]')].every(a=>/noopener/.test(a.rel))"))
    ctx.close()
    reset_state(); STATE['man'] = manifest(sources={'tmdb': {'status': 'stale'}, 'youtube': {'status': 'unverified'}, 'news': {'status': 'disabled'}})
    ctx = new_ctx(b); pg = open_page(ctx); go_live(pg)
    ok('dati vecchi (stale/unverified): avviso visibile all\'utente', 'non aggiornato' in txt(pg, '.tvl-status') and pg.locator('.tvl-status.tvl-warn').count() == 1)
    ctx.close()
    reset_state(); STATE['man'] = {'schema': 1, 'seed': True, 'generated_at': None, 'sources': {}}; STATE['cal'] = []; STATE['tr'] = []
    ctx = new_ctx(b); pg = open_page(ctx); go_live(pg)
    ok('seed (nessun dato ancora generato): messaggio dedicato', 'in attesa dei primi dati' in txt(pg).lower() and 'vuoto' in txt(pg) and pg.locator('.tvl-badge').count() == 0)
    ctx.close()
    # Trailer
    reset_state(); ctx = new_ctx(b); pg = open_page(ctx); go_live(pg, 'trl')
    ok('trailer: link esterni a YouTube, nessun iframe/embed', pg.locator('.tvl-row a[href^="https://www.youtube.com/watch?v="]').count() == 2 and pg.locator('#cenPan-live :is(iframe, embed, object, video)').count() == 0)
    ok('trailer: canale ufficiale indicato e collegamento al titolo', 'canale ufficiale' in txt(pg).lower() and 'Doomsday Test' in txt(pg, '#cenPan-live .tvl-row >> nth=0'))
    ok('trailer: credito TMDB con logo', pg.locator('.tvl-credit').count() == 1 and 'not endorsed or certified by TMDB' in txt(pg, '.tvl-credit'))
    ctx.close()

    # ---------- 6. backup / ripristino profilo ----------
    reset_state(); ctx = new_ctx(b); pg = open_page(ctx); go_live(pg)
    pg.evaluate("()=>document.getElementById('tvlSub-cal').click()"); pg.locator('.tvl-row[data-key="tmdb:movie:11"] button:has-text("Segui")').click(); pg.wait_for_timeout(100)
    pg.evaluate("()=>document.getElementById('tvlSub-pref').click()"); pg.locator('label:has-text("Serie e stagioni") input').uncheck(); pg.wait_for_timeout(100)
    saved = jl(pg, PK); ok('backup: preferenze presenti in locale', saved['followed'] == ['tmdb:movie:11'] and saved['cats']['serie'] is False)
    with pg.expect_download() as dl: pg.evaluate("()=>document.getElementById('exportBtn').click()")
    path = dl.value.path(); prof = json.load(open(path))
    ok('backup: campo "live" nel profilo = preferenze (senza stato volatile)', prof.get('live') == saved and 'inbox' not in prof['live'] and 'seen' not in prof['live'], prof.get('live'))
    pg.evaluate("(k)=>{localStorage.removeItem(k)}", PK)
    pg.on('dialog', lambda dd: dd.accept())
    with pg.expect_navigation(): pg.set_input_files('#importFile', path)
    pg.wait_for_selector('#item-073', state='attached'); pg.wait_for_timeout(500)
    ok('ripristino: preferenze Live ripristinate identiche', jl(pg, PK) == saved, jl(pg, PK))
    ok('ripristino: stato locale degli avvisi non toccato', jl(pg, SK) is not None and jl(pg, SK)['init'] is True)
    old = json.loads(json.dumps(prof)); del old['live']; open('/tmp/live_old.json', 'w').write(json.dumps(old))
    with pg.expect_navigation(): pg.set_input_files('#importFile', '/tmp/live_old.json')
    pg.wait_for_selector('#item-073', state='attached'); pg.wait_for_timeout(500)
    ok('profilo precedente senza "live": preferenze locali conservate', jl(pg, PK) == saved)
    before = ls(pg, PK)
    for bad, nm in (({'cats': {'film': 'si'}}, 'cats non booleano'), ({'lead': [5]}, 'lead fuori elenco'), ({'followed': ['evil']}, 'chiave titolo non valida'), ({'inbox': [{'id': 'x'}]}, 'avviso malformato'), ('stringa', 'tipo errato')):
        x = json.loads(json.dumps(prof)); x['live'] = bad; open('/tmp/live_bad.json', 'w').write(json.dumps(x))
        pg.set_input_files('#importFile', '/tmp/live_bad.json'); pg.wait_for_timeout(1200)
        ok('import non valido (%s): rifiutato, dati intatti' % nm, ls(pg, PK) == before)
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    ok('sync: chiave Live registrata in PROFILE_OBJ_KEYS (stessi costruttori di profilo)', "live: 'marvel-ultimate-timeline-live-v1'" in src and src.count('for (var ok in PROFILE_OBJ_KEYS) { profile[ok] = safeGetObj') >= 3)
    ok('isolamento: la chiave dello stato volatile NON e nel profilo', 'live-state-v1' not in src.split('PROFILE_OBJ_KEYS = {')[1].split('};')[0])
    # --- categorie (film/serie/animazione/videogiochi), avvisi "da verificare", trailer game
    reset_state()
    STATE['cal'] = copy.deepcopy(CAL) + [item('tmdb:movie:60', 'Film Animato', d(220), category='animazione'), item('tmdb:tv:61', 'Serie Cancellata Con Data', d(230), kind='season', category='serie', warnings=['tmdb_canceled'])]
    for i in STATE['cal'][:len(CAL)]: i.setdefault('category', None)
    STATE['tr'] = copy.deepcopy(TR) + [{'key': 'yt:GGGGGGGGGGG', 'title': 'Marvel Cosmic Invasion DLC | Launch Trailer', 'published': d(-2), 'url': 'https://www.youtube.com/watch?v=GGGGGGGGGGG', 'channel': 'Marvel Entertainment', 'kind': 'trailer', 'official': True, 'relatesTo': None, 'category': 'videogioco'}]
    ctx = new_ctx(b); pg = open_page(ctx); go_live(pg)
    def chipc(n): pg.locator('.tvl-chip', has_text=n).first.click(); pg.wait_for_timeout(100)
    chipc('Animazione'); ok('categorie: filtro Animazione mostra solo animati', pg.locator('.tvl-row').count() == 1 and pg.locator('.tvl-row[data-key="tmdb:movie:60"]').count() == 1)
    chipc('Serie'); ok('categorie: filtro Serie non include animati', pg.locator('.tvl-row[data-key="tmdb:movie:60"]').count() == 0 and pg.locator('.tvl-row[data-key="tmdb:tv:61"]').count() == 1)
    chipc('Tutti'); ok('avviso: serie con stato TMDB cancellato mostra "Da verificare"', 'da verificare' in txt(pg, '.tvl-row[data-key="tmdb:tv:61"]').lower())
    ok('avviso: nessuna etichetta Confermato aggiunta', pg.locator('.tvl-row .tvl-t-conf').count() == 1)
    go_live(pg, 'trl')
    ok('trailer: DLC classificato Videogioco', 'videogioc' in txt(pg, '.tvl-row[data-key="yt:GGGGGGGGGGG"]').lower())
    ok('trailer: senza categoria dimostrata -> Non classificato', 'non classificato' in txt(pg, '.tvl-row[data-key="yt:AAAAAAAAAAA"]').lower() or 'film' in txt(pg, '.tvl-row[data-key="yt:AAAAAAAAAAA"]').lower())
    chipc('Videogiochi'); ok('trailer: filtro Videogiochi isola il DLC', pg.locator('.tvl-row').count() == 1 and pg.locator('.tvl-row[data-key="yt:GGGGGGGGGGG"]').count() == 1)
    ok('errori JS categorie', not pg.errs, pg.errs)
    ctx.close()
    # --- rifiniture: schede compatte, locandine proporzionali, filtri su una riga, icona Segui
    reset_state(); ctx = new_ctx(b, 390); pg = open_page(ctx); go_live(pg)
    r = pg.locator('.tvl-row[data-key="tmdb:movie:1"]')
    H = r.bounding_box()['height']; print('altezza riga', H)
    ok('compatte: riga sotto 150px a 390px con tutti i comandi', H < 150 and r.locator('button').count() >= 3, H)
    ok('compatte: comandi Segui / Apri in Timeline / Perche presenti', r.locator('button.tvl-follow').count() == 1 and r.locator('button:has-text("Apri in Timeline")').count() == 1 and r.locator('button:has-text("Perché")').count() == 1)
    ok('compatte: tap target >= 36px', pg.evaluate("()=>[...document.querySelectorAll('.tvl-row .tvl-btn')].every(b=>b.getBoundingClientRect().height>=35.5)"))
    ok('locandine: proporzioni naturali (height auto, contain, nessun aspect-ratio forzato)', pg.evaluate("()=>{const i=document.querySelector('img.tvl-poster');const c=getComputedStyle(i);return c.objectFit==='contain'&&i.style.height==='auto'&&c.aspectRatio.indexOf('auto')===0}"))
    ok('locandine: rapporto renderizzato ~2:3 (nessun ritaglio)', pg.evaluate("()=>{const i=document.querySelector('img.tvl-poster');if(!i.naturalWidth)return true;const b=i.getBoundingClientRect();return Math.abs(b.width/b.height-i.naturalWidth/i.naturalHeight)<0.03}"))
    ch = pg.locator('.tvl-chips').bounding_box()
    ok('filtri: una sola riga (<= 40px) a 390px', ch['height'] <= 40, ch['height'])
    ok('filtri: scorrimento orizzontale interno, nessun overflow di pagina', overflow(pg) <= 0)
    ok('filtri: tap target >= 32px', pg.evaluate("()=>[...document.querySelectorAll('.tvl-chip')].every(b=>b.getBoundingClientRect().height>=31.5)"))
    fb = pg.locator('.tvl-row[data-key="tmdb:movie:1"] button.tvl-follow')
    ok('segui: icona SVG (non campanella), contorno quando non seguito', fb.locator('svg path[fill="none"]').count() == 1 and fb.get_attribute('aria-pressed') == 'false' and 'Segui' in fb.inner_text() and '🔕' not in fb.inner_text() and '🔔' not in fb.inner_text())
    fb.click(); pg.wait_for_timeout(150); fb = pg.locator('.tvl-row[data-key="tmdb:movie:1"] button.tvl-follow')
    if os.environ.get('SHOT'): pg.screenshot(path=os.environ['SHOT'])
    ok('segui: stella piena e "Seguito" quando seguito, aria-pressed true', fb.locator('svg path[fill="currentColor"]').count() == 1 and fb.get_attribute('aria-pressed') == 'true' and 'Seguito' in fb.inner_text())
    pg.reload(); pg.wait_for_selector('#item-073', state='attached'); pg.wait_for_timeout(400)
    ok('segui: persistenza invariata dopo ricarica', 'tmdb:movie:1' in (jl(pg, PK) or {}).get('followed', []))
    ok('rifiniture: nessun errore JS', not pg.errs, pg.errs)
    ctx.close()
    # ---------- mercati: la data italiana ha priorita, le date ufficiali degli altri mercati stanno nei dettagli ----------
    reset_state()
    for i in STATE['cal']:
        if i['key'] == 'tmdb:movie:7':
            i.update(dateBasis='IT', dateTMDB=d(400), officialDates=[
                {'market': 'UK', 'date': d(400), 'channel': 'Marvel Entertainment', 'url': 'https://www.youtube.com/watch?v=AAAAAAAAAAA', 'title': 'x'},
                {'market': 'US', 'date': d(402), 'channel': 'Marvel Entertainment', 'url': 'javascript:alert(1)', 'title': 'y'},
                {'market': 'ZZ', 'date': d(403), 'url': 'https://evil.example/', 'title': 'z'}], confidence='provisional')
            i['sources'] = [i['sources'][-1]]
    ctx = new_ctx(b); pg = open_page(ctx); go_live(pg)
    r = pg.locator('.tvl-row[data-key="tmdb:movie:7"]')
    ok('mercati: badge Provvisorio e etichetta data italiana', r.locator('.tvl-t-prov').count() == 1 and r.locator('.tvl-mk').inner_text() == 'Italia')
    r.locator('button:has-text("Perché")').click(); pg.wait_for_timeout(150)
    t = r.inner_text()
    ok('mercati: dettagli con date ufficiali per mercato (UK, USA), mercato sconosciuto scartato', 'Regno Unito' in t and 'USA' in t and 'ZZ' not in t)
    ok('mercati: avviso "non conferma la data italiana"', 'non conferma la data italiana' in t)
    hrefs = r.locator('.tvl-det a').evaluate_all("els=>els.map(e=>e.href)")
    ok('mercati: solo link https verso host noti (niente javascript:)', all(h.startswith('https://www.youtube.com/') or h.startswith('https://www.themoviedb.org/') for h in hrefs) and not any('javascript' in h or 'evil' in h for h in hrefs), hrefs)
    STATE['cal'][1].update(dateBasis='TMDB')
    ok('mercati: nessun errore JS', not pg.errs, pg.errs)
    ctx.close()
    ctx.close(); b.close()
bad = [n for n, c in res if not c]
print('\nRISULTATO: %d ok, %d falliti' % (len(res) - len(bad), len(bad)))
for n in bad: print(' FAIL:', n)
raise SystemExit(1 if bad else 0)
