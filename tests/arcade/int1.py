# Integrazione TVA Arcade nell'app TEST — blocco 1 (struttura, home, hub, quiz, SW). Chromium reale su HTTP.
import json, sys, re, time
from playwright.sync_api import sync_playwright
import urllib.request
ROOT = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8790/'
RES = []
def wf(pg, expr, timeout=60000):
    t = time.time()
    while time.time() - t < timeout / 1000:
        try:
            if pg.evaluate('(()=>!!(' + expr + '))()'): return True
        except Exception: pass
        pg.wait_for_timeout(250)
    raise TimeoutError(expr)
def rec(n, ok, note=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + n + ((' — ' + str(note)[:300]) if note else ''), flush=True)
def status(u):
    try: return urllib.request.urlopen(u).status
    except Exception as e: return getattr(e, 'code', 0)
SEED = {
 'marvel-ultimate-timeline-missioni-xp-bonus': json.dumps({'totale': 175, 'ricompensate': ['a', 'b', 'c']}),
 'marvel-ultimate-timeline-watched': json.dumps({'x': True}),
 'marvel-ultimate-timeline-user-name': 'Variante Test',
}
def snap(pg): return pg.evaluate("(()=>{var o={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o})()")
with sync_playwright() as p:
    br = p.chromium.launch()
    ctx = br.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); pg = ctx.new_page(); errs = []; fails = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('response', lambda r: fails.append(r.url) if r.status >= 400 else None)
    pg.add_init_script("(()=>{var S=%s;try{if(!sessionStorage.getItem('__seeded')){for(var k in S)localStorage.setItem(k,S[k]);sessionStorage.setItem('__seeded','1');sessionStorage.setItem('tva-return-home','1')}}catch(e){}})()" % json.dumps(SEED))
    pg.goto(ROOT, wait_until='domcontentloaded'); wf(pg, "typeof window.tvaFriends!=='undefined'", 60000); pg.wait_for_timeout(2500)
    # I1 home
    h = pg.evaluate("""(()=>{var a=document.getElementById('hhPlayArcade');return {arc:!!a, href:a&&a.getAttribute('href'), txt:a&&a.textContent.replace(/\\s+/g,' ').trim(), quiz:!!document.getElementById('hhPlayQuiz'), atl:!!document.getElementById('m34Atl'), tes:!!document.getElementById('m34Tes'), rank:!!document.getElementById('hhPlayRank'),
      tabs:['appTabAtlante','appTabTessera','appTabMissioni'].map(i=>!!document.getElementById(i)), a2:!!document.getElementById('a2Entry'), navHidden:getComputedStyle(document.querySelector('.home-hub-nav')).display, h:Math.round(a.getBoundingClientRect().height), vis:a.getBoundingClientRect().width>0}})()""")
    rec('I1 home: «TVA Arcade» sostituisce la scorciatoia Quiz; Atlante/Tessera rimosse; Rankings, Atlante 2 e tabbar intatti', h['arc'] and h['href'] == './arcade/' and 'TVA Arcade' in h['txt'] and not h['quiz'] and not h['atl'] and not h['tes'] and h['rank'] and all(h['tabs']) and h['a2'] and h['navHidden'] == 'none' and h['h'] >= 44 and not errs, (h, errs[:2]))
    pg.screenshot(path='/home/claude/arc/home_int1.png')
    base = snap(pg)
    # I2 navigazione
    pg.click('#hhPlayArcade'); pg.wait_for_url('**/arcade/', timeout=10000); pg.wait_for_selector('a.game', timeout=10000)
    cards = pg.evaluate("[...document.querySelectorAll('nav.games a.game')].map(a=>[a.getAttribute('href'), a.querySelector('.game-name').textContent])")
    rec('I2 hub: cinque card (Quiz, Who Am I?, Time Crisis, Draft, Escape) con i link corretti', [c[1] for c in cards] == ['Quiz Marvel', 'Who Am I?', 'Time Crisis', 'Secret Wars Draft', 'Multiverse Escape'] and [c[0] for c in cards] == ['../quiz/?from=arcade', 'who-am-i/', 'time-crisis/', 'draft/', 'escape/'], cards)
    allok = True; det = []
    for href, name in cards:
        pg.goto(ROOT + 'arcade/' + href, wait_until='domcontentloaded'); pg.wait_for_timeout(900)
        nav = pg.evaluate("(()=>{var a=document.querySelector('#tva-arcade-nav a, #tvaBackApp, .tvaexit a');return a?[a.textContent.trim(),a.getAttribute('href'),Math.round(a.getBoundingClientRect().height)]:null})()")
        vp = pg.evaluate("!!document.querySelector('head meta[name=viewport]')")
        ov = pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth")
        ok = bool(nav) and ov and (vp or 'quiz' in href); allok &= ok; det.append((name, nav, vp, ov))
    rec('I2b ogni pagina: carica, link di ritorno presente, viewport nel <head>, nessun overflow orizzontale', allok, det)
    # ritorno dai giochi
    for href in ['who-am-i/', 'time-crisis/', 'draft/', 'escape/']:
        pg.goto(ROOT + 'arcade/' + href, wait_until='domcontentloaded'); pg.wait_for_timeout(500); pg.click('#tva-arcade-nav a'); pg.wait_for_url('**/arcade/', timeout=8000)
    rec('I2c ritorno all\'hub da tutti e 4 i giochi', pg.url.endswith('/arcade/'))
    pg.click('#arcade-to-app'); wf(pg, "typeof window.tvaFriends!=='undefined'", 60000); pg.wait_for_timeout(1500)
    rec('I2d hub → «TVA Archives» riporta alla app', pg.url.rstrip('/') == ROOT.rstrip('/') or pg.url.startswith(ROOT) and '/arcade' not in pg.url, pg.url)
    # I3 quiz
    pg.goto(ROOT + 'quiz/?from=arcade', wait_until='domcontentloaded'); pg.wait_for_selector('#tvaBackApp', timeout=15000)
    b = pg.evaluate("(()=>{var a=document.getElementById('tvaBackApp');return [a.getAttribute('href'),a.textContent.trim()]})()")
    pg.click('#tvaBackApp'); pg.wait_for_url('**/arcade/', timeout=8000)
    pg.goto(ROOT + 'quiz/', wait_until='domcontentloaded'); pg.wait_for_selector('#tvaBackApp', timeout=15000)
    b2 = pg.evaluate("(()=>{var a=document.getElementById('tvaBackApp');return [a.getAttribute('href'),a.textContent.trim()]})()")
    src = urllib.request.urlopen(ROOT + 'quiz/').read().decode('utf8')
    rec('I3 Quiz: da Arcade il ritorno va all\'hub; da /quiz/ diretto resta «Torna a TVA Archives» (../); timer 30 s (2 occorrenze + etichetta)', b[0] == '../arcade/' and 'TVA Arcade' in b[1] and b2[0] == '../' and 'Archives' in b2[1] and src.count('tLeft = 30') == 2 and 'tLeft = 20' not in src and 'Timer di 30 secondi' in src and 'Timer di 20' not in src, (b, b2))
    # I4 regressione dati
    pg.goto(ROOT, wait_until='domcontentloaded'); wf(pg, "typeof window.tvaFriends!=='undefined'", 60000); pg.wait_for_timeout(2000)
    after = snap(pg)
    chg = [k for k in base if base[k] != after.get(k) and not re.search(r'(last-visited|tva-arcade|tva-return|sessionstorage)', k)]
    chg_prot = [k for k in chg if re.search(r'(xp|watched|missioni|badge|rank|user-name|tessera|friends)', k)]
    rec('I4 profilo popolato: XP/missioni/watched/nome/Tessera/Friends/Rankings invariati dopo home→Arcade→giochi→Quiz→home', not chg_prot and after['marvel-ultimate-timeline-missioni-xp-bonus'] == SEED['marvel-ultimate-timeline-missioni-xp-bonus'], (chg_prot, chg[:5]))
    rec('I4b nessun errore di pagina durante tutto il percorso', not errs, errs[:3])
    # I5 404 sui file referenziati
    PRE = ['assets/images/tmdb-logo.svg']   # 404 GIA' PRESENTE nella build TEST di partenza (non introdotto da Arcade): segnalato nei problemi aperti
    bad = [u for u in fails if u.startswith(ROOT) and not u.endswith('favicon.ico') and not any(u.endswith(x) for x in PRE)]
    rec('I5 nessuna risorsa locale 404 / fallita', not bad, bad[:5])
    ctx.close()
    # I6 offline con service worker
    ctx = br.new_context(viewport={'width': 390, 'height': 844}); pg = ctx.new_page(); e2 = []; pg.on('pageerror', lambda e: e2.append(str(e)))
    pg.goto(ROOT, wait_until='domcontentloaded'); wf(pg, "typeof window.tvaFriends!=='undefined'", 60000)
    pg.evaluate("navigator.serviceWorker.ready.then(()=>1)"); pg.wait_for_timeout(500)
    ok_sw = False
    for _ in range(40):
        c = pg.evaluate("(async()=>{try{var ks=await caches.keys();var k=ks.find(x=>/marvel-timeline-cache/.test(x));if(!k)return [];var c=await caches.open(k);return (await c.keys()).map(r=>new URL(r.url).pathname)}catch(e){return []}})()")
        if any(x.endswith('/arcade/') for x in c): ok_sw = True; break
        pg.wait_for_timeout(500)
    cached = [x for x in c if '/arcade' in x]
    rec('I6 service worker: shell Arcade in cache (hub + 4 giochi + script condivisi)', ok_sw and all(any(x.endswith(s) for x in c) for s in ['/arcade/', '/arcade/who-am-i/', '/arcade/time-crisis/', '/arcade/draft/', '/arcade/escape/', '/arcade/shared/arcade-nav.js']), cached)
    ctx.set_offline(True)
    off = {}
    for pth in ['arcade/', 'arcade/who-am-i/', 'arcade/time-crisis/']:
        try:
            pg.goto(ROOT + pth, wait_until='domcontentloaded', timeout=15000); off[pth] = pg.evaluate("document.title") 
        except Exception as e: off[pth] = 'ERR ' + str(e)[:60]
    rec('I6b offline: hub e giochi si aprono dalla cache', all(not v.startswith('ERR') and v for v in off.values()), off)
    ctx.close()
    # I7 overflow su 320/390/430 (hub)
    ov = {}
    for w in (320, 390, 430):
        c = br.new_context(viewport={'width': w, 'height': 800}, service_workers='block'); q = c.new_page(); q.goto(ROOT + 'arcade/', wait_until='domcontentloaded'); q.wait_for_timeout(600)
        ov[w] = q.evaluate("[document.documentElement.scrollWidth, window.innerWidth]"); c.close()
    rec('I7 hub senza scroll orizzontale a 320/390/430', all(a <= b for a, b in ov.values()), ov)
    br.close()
bad = RES.count(False); print('\nTOTALE %d test, %d PASS, %d FAIL' % (len(RES), len(RES) - bad, bad)); sys.exit(1 if bad else 0)
