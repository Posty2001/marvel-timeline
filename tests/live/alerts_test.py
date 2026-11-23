"""TVA Live - Fase B/C: avvisi con orologio simulato e dati di prova isolati; affidabilita.
Nessun dato reale: il calendario e' una fixture servita da route, le date sono simulate (Playwright clock). Uso: python3 tests/live/alerts_test.py"""
import copy, datetime as dt, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
NS = {'__file__': os.path.join(HERE, 'ui_test.py'), '__name__': 'ui_helpers'}
exec(compile(open(NS['__file__'], encoding='utf-8').read().split('with sync_playwright() as pw:')[0], NS['__file__'], 'exec'), NS)
item, new_ctx, open_page, reload, go_live, txt, jl, ls, ok, STATE, manifest, PK, SK, ROOT = (NS[k] for k in ('item', 'new_ctx', 'open_page', 'reload', 'go_live', 'txt', 'jl', 'ls', 'ok', 'STATE', 'manifest', 'PK', 'SK', 'ROOT'))
sync_playwright = NS['sync_playwright']
SIM0 = dt.datetime(2027, 3, 1, 10, 0, 0)
def sd(n): return (SIM0.date() + dt.timedelta(days=n)).isoformat()
def tr(key, title, relates=None, cat=None): return {'key': 'yt:' + key, 'title': title, 'published': sd(0), 'url': 'https://www.youtube.com/watch?v=' + key, 'channel': 'Marvel Entertainment', 'kind': 'trailer', 'official': True, 'relatesTo': relates, 'category': cat}
def base(): return [item('tmdb:movie:900', 'Reminder Film', sd(7), category='film'), item('tmdb:movie:901', 'Altro Film', sd(7), category='film'), item('tmdb:movie:902', 'Lontano Film', sd(300), category='film')]
def setclock(ctx, day, hour=10): ctx.clock.set_fixed_time(dt.datetime.combine(SIM0.date() + dt.timedelta(days=day), dt.time(hour)))
def setup(b, cal=None, trs=None):
    STATE.update(cal=cal if cal is not None else base(), tr=trs if trs is not None else [], man=manifest(), fail=False)
    ctx = new_ctx(b); ctx.clock.install(time=SIM0); setclock(ctx, 0); pg = open_page(ctx); go_live(pg); return ctx, pg
def visit(ctx, pg, day, sub='avv'):
    setclock(ctx, day); reload(pg); go_live(pg, sub); pg.wait_for_timeout(250)
def inbox(pg): return pg.evaluate("()=>window.tvaLive.prefs().inbox")
def kinds(pg, t): return [a for a in inbox(pg) if a['t'] == t]
def setprefs(pg, **kw):
    p = pg.evaluate("()=>window.tvaLive.prefs()"); keep = {k: p[k] for k in ('v', 'cats', 'lead', 'followed', 'muted', 'onlyUnwatched')}; keep.update(kw)
    pg.evaluate("(o)=>localStorage.setItem('marvel-ultimate-timeline-live-v1', JSON.stringify(o))", keep)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    # ---- B1 nuova uscita: un solo avviso, nessun duplicato alla riapertura
    ctx, pg = setup(b)
    ok('B1 primo avvio: nessun avviso, stato inizializzato', len(inbox(pg)) == 0 and jl(pg, SK)['init'] is True)
    STATE['cal'] = base() + [item('tmdb:movie:910', 'Nuova Uscita', sd(120), category='film')]
    visit(ctx, pg, 1)
    ok('B1 nuova uscita: un solo avviso', len(kinds(pg, 'new')) == 1 and 'Nuova uscita in calendario: Nuova Uscita' in txt(pg))
    visit(ctx, pg, 1); visit(ctx, pg, 2)
    ok('B1 riapertura (anche giorni dopo): nessun avviso duplicato', len(kinds(pg, 'new')) == 1 and len(inbox(pg)) == 1)
    # ---- B2 cambio data: vecchia e nuova data nel testo
    STATE['cal'][2]['date'] = sd(310)
    visit(ctx, pg, 3)
    t = txt(pg); old, nw = [int(x) for x in (sd(300)[8:], sd(310)[8:])]
    ok('B2 cambio data: avviso con vecchia e nuova data', len(kinds(pg, 'date')) == 1 and 'Data cambiata per Lontano Film' in t and ' → ' in t and ('%d ' % old) in t.split('Data cambiata per Lontano Film')[1] and ('%d ' % nw) in t.split('→')[1], t[:200])
    visit(ctx, pg, 3); ok('B2 stesso dato: nessun secondo avviso', len(kinds(pg, 'date')) == 1)
    # ---- B3 provvisorio -> confermato
    STATE['cal'][1]['confidence'] = 'confirmed'; STATE['cal'][1]['sources'].insert(0, {'name': 'YouTube - Marvel Entertainment', 'url': 'https://www.youtube.com/watch?v=AAAAAAAAAAA', 'official': True})
    visit(ctx, pg, 4)
    ok('B3 provvisorio -> confermato: un avviso', len(kinds(pg, 'confirmed')) == 1 and 'Ora confermato da fonte ufficiale: Altro Film' in txt(pg))
    visit(ctx, pg, 4); ok('B3 nessun duplicato', len(kinds(pg, 'confirmed')) == 1)
    # ---- B4 nuovo trailer
    STATE['tr'] = [tr('EEEEEEEEEEE', 'Nuovo Teaser Ufficiale')]
    visit(ctx, pg, 5); ok('B4 nuovo trailer: un avviso', len(kinds(pg, 'trailer')) == 1 and 'Nuovo video ufficiale: Nuovo Teaser Ufficiale' in txt(pg))
    visit(ctx, pg, 5); ok('B4 nessun duplicato alla riapertura', len(kinds(pg, 'trailer')) == 1)
    ctx.close()

    # ---- B5 promemoria 7/3/1/0: solo se seguito e anticipo abilitato
    ctx, pg = setup(b)
    setprefs(pg, followed=['tmdb:movie:900'], lead=[7, 3, 1, 0])
    for day, exp in ((0, 'tra 7 giorni'), (4, 'tra 3 giorni'), (6, 'domani'), (7, 'oggi')):
        visit(ctx, pg, day)
        s = [a for a in kinds(pg, 'soon') if a['k'] == 'tmdb:movie:900']
        ok('B5 giorno %d: promemoria "%s" (totale %d)' % (day, exp, len(s)), s and exp in txt(pg) and len(s) == {0: 1, 4: 2, 6: 3, 7: 4}[day], [x['m']['days'] for x in s])
    visit(ctx, pg, 7); visit(ctx, pg, 7)
    ok('B5 riaperture nello stesso giorno: sempre 4 promemoria, nessuno duplicato', len(kinds(pg, 'soon')) == 4)
    ok('B5 titolo NON seguito: nessun promemoria', not [a for a in kinds(pg, 'soon') if a['k'] == 'tmdb:movie:901'])
    ctx.close()
    ctx, pg = setup(b); setprefs(pg, followed=['tmdb:movie:900'], lead=[1, 0])
    visit(ctx, pg, 0); visit(ctx, pg, 4); ok('B5 anticipi 7 e 3 disabilitati: nessun promemoria a 7 e 3 giorni', len(kinds(pg, 'soon')) == 0)
    visit(ctx, pg, 6); ok('B5 anticipo 1 giorno abilitato: un promemoria', len(kinds(pg, 'soon')) == 1)
    ctx.close()
    ctx, pg = setup(b); setprefs(pg, followed=['tmdb:movie:900'], lead=[])
    for day in (0, 4, 6, 7): visit(ctx, pg, day)
    ok('B5 nessun anticipo abilitato: nessun promemoria', len(kinds(pg, 'soon')) == 0)
    ctx.close()
    ctx, pg = setup(b); setprefs(pg, followed=['tmdb:movie:900'], lead=[7, 3, 1, 0], muted=['tmdb:movie:900'])
    for day in (0, 4, 7): visit(ctx, pg, day)
    ok('B5 titolo silenziato: nessun promemoria', len(kinds(pg, 'soon')) == 0)
    ctx.close()
    # promemoria rifatti se la data cambia (nuova data = nuova scadenza)
    ctx, pg = setup(b); setprefs(pg, followed=['tmdb:movie:900'], lead=[7, 3, 1, 0]); visit(ctx, pg, 0)
    STATE['cal'][0]['date'] = sd(12); visit(ctx, pg, 5)
    ok('B5 data spostata: promemoria coerente con la nuova data (tra 7 giorni dal 12)', any(a['m']['to'] == sd(12) and a['m']['days'] == 7 for a in kinds(pg, 'soon')) and len(kinds(pg, 'date')) == 1)
    ctx.close()

    # ---- B9 rigenerazione con catalogo invariato (cambiano solo generated_at / updatedAt / content_hash): nessun falso avviso
    cal0 = base() + [item('tmdb:tv:950:S01', 'Serie Animata S1', sd(90), kind='season', category='animazione')]
    ctx, pg = setup(b, cal=copy.deepcopy(cal0), trs=[tr('JJJJJJJJJJJ', 'Trailer Stabile')]); setprefs(pg, followed=['tmdb:movie:902'])
    visit(ctx, pg, 1); n_before = len(inbox(pg)); fol = pg.evaluate("()=>window.tvaLive.prefs().followed")
    cal1 = copy.deepcopy(cal0)
    for i in cal1: i['updatedAt'] = sd(2); i['firstSeen'] = sd(-30)
    STATE['cal'] = cal1; STATE['man'] = manifest(generated_at=(SIM0 + dt.timedelta(days=2)).isoformat() + '+00:00', content_hash='ffffffffffffffff')
    for day in (2, 2, 3): visit(ctx, pg, day)
    ok('B9 stesso catalogo rigenerato: nessun nuovo avviso (updatedAt/generated_at non sono segnali di cambiamento)', len(inbox(pg)) == n_before == 0, inbox(pg))
    ok('B9 rigenerazione: titoli seguiti e preferenze invariati', pg.evaluate("()=>window.tvaLive.prefs().followed") == fol == ['tmdb:movie:902'])
    ctx.close()

    # ---- B6 preferenze disabilitate -> nessun avviso indesiderato
    ctx, pg = setup(b)
    cats = {'film': False, 'serie': True, 'animazione': True, 'game': True, 'trailer': False}
    setprefs(pg, cats=cats)
    STATE['cal'] = base() + [item('tmdb:movie:911', 'Film Nascosto', sd(100), category='film')]; STATE['cal'][1]['date'] = sd(9)
    STATE['tr'] = [tr('FFFFFFFFFFF', 'Trailer Disattivato')]
    visit(ctx, pg, 1)
    ok('B6 categoria Film e Trailer disattivati: nessun avviso (nuova uscita, cambio data, trailer)', len(inbox(pg)) == 0, inbox(pg))
    setprefs(pg, cats={'film': True, 'serie': True, 'animazione': True, 'game': True, 'trailer': True}); STATE['tr'] = [tr('GGGGGGGGGGG', 'Videogioco DLC', cat='videogioco')]
    setprefs(pg, cats={'film': True, 'serie': True, 'animazione': True, 'game': False, 'trailer': True}); visit(ctx, pg, 2)
    ok('B6 categoria Videogiochi disattivata: nessun avviso per trailer videogioco', len(kinds(pg, 'trailer')) == 0)
    ctx.close()

    # ---- B8 aggiornamento catalogo: nessuna modifica ai dati personali
    ctx, pg = setup(b)
    pg.evaluate("""()=>{localStorage.setItem('marvel-ultimate-timeline-watched', JSON.stringify({'073':true}));localStorage.setItem('tva-xp-sentinel','{"xp":1234}');localStorage.setItem('tva-ratings-sentinel','{"039":4.5}');localStorage.setItem('tva-missions-sentinel','{"m1":true}')}""")
    def personal(): return pg.evaluate("(ks)=>{const o={};for(let i=0;i<localStorage.length;i++){const n=localStorage.key(i);if(!ks.includes(n))o[n]=localStorage.getItem(n)}return o}", [PK, SK])
    before = personal(); cards = pg.evaluate("()=>document.querySelectorAll('li.card-wrap').length"); chk = pg.evaluate("()=>[...document.querySelectorAll('.watch-check:checked')].length")
    STATE['cal'] = base() + [item('tmdb:movie:920', 'Aggiunto', sd(50), category='film')]; STATE['cal'][0]['date'] = sd(20); STATE['tr'] = [tr('HHHHHHHHHHH', 'Altro Trailer')]
    pg.evaluate("()=>window.tvaLive.load(true)"); pg.wait_for_timeout(500)
    ok('B8 aggiornamento catalogo: nuovi avvisi ma nessuna chiave personale modificata (XP, voti, missioni, visti, ecc.)', len(inbox(pg)) >= 3 and personal() == before)
    ok('B8 nessuna scheda Timeline creata/rimossa e visti invariati', pg.evaluate("()=>document.querySelectorAll('li.card-wrap').length") == cards and pg.evaluate("()=>[...document.querySelectorAll('.watch-check:checked')].length") == chk)
    ctx.close()

    # ---- C1 errore TMDB/YouTube dopo un catalogo valido: ultimo catalogo valido conservato e visibile
    ctx, pg = setup(b, trs=[tr('IIIIIIIIIII', 'Trailer Valido')]); n0 = len(base())
    STATE['fail'] = True; pg.evaluate("()=>window.tvaLive.load(true)"); pg.wait_for_function("()=>window.tvaLive.data().refreshFailed===true", timeout=10000); pg.evaluate("()=>window.tvaLive.render()")
    d = pg.evaluate("()=>{const x=window.tvaLive.data();return {s:x.status,c:x.calendar.length,t:x.trailers.length,f:x.refreshFailed}}")
    ok('C1 aggiornamento fallito: calendario e trailer validi conservati in memoria', d['c'] == n0 and d['t'] == 1 and d['f'] is True, d)
    pg.evaluate("()=>document.getElementById('tvlSub-cal').click()"); pg.wait_for_timeout(150)
    ok('C1 aggiornamento fallito: il calendario resta visibile con avviso', pg.locator('.tvl-row').count() == n0 and 'Aggiornamento non riuscito' in txt(pg, '.tvl-status'))
    ok('C1 aggiornamento fallito: nessun avviso generato e inbox intatta', len(inbox(pg)) == 0)
    STATE['fail'] = False; pg.evaluate("()=>window.tvaLive.load(true)"); pg.wait_for_function("()=>window.tvaLive.data().refreshFailed===false", timeout=10000); pg.evaluate("()=>window.tvaLive.render()")
    ok('C1 ripristino della rete: avviso di errore sparito', 'Aggiornamento non riuscito' not in txt(pg, '.tvl-status'))
    ctx.close()
    # ---- C2 dati obsoleti riconoscibili (stato fonte e anzianita)
    STATE.update(cal=base(), tr=[], man=manifest(generated_at=(SIM0 - dt.timedelta(days=41)).isoformat() + '+00:00'), fail=False)
    ctx = new_ctx(b); ctx.clock.install(time=SIM0); setclock(ctx, 0); pg = open_page(ctx); go_live(pg)
    ok('C2 catalogo vecchio di 40 giorni: avviso di dati non aggiornati', 'non aggiornati da 40 giorni' in txt(pg, '.tvl-status') or 'non aggiornati da 41 giorni' in txt(pg, '.tvl-status') and pg.locator('.tvl-status.tvl-warn').count() == 1, txt(pg, '.tvl-status'))
    ctx.close()
    STATE.update(man=manifest(generated_at=SIM0.isoformat() + '+00:00'))
    ctx = new_ctx(b); ctx.clock.install(time=SIM0); setclock(ctx, 0); pg = open_page(ctx); go_live(pg)
    ok('C2 catalogo fresco: nessun avviso di obsolescenza', 'non aggiornati da' not in txt(pg, '.tvl-status'))
    ctx.close()
    # ---- C6 gli avvisi restano interni all'app
    go = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read(); js = go.split('<script id="tva-live-js">')[1].split('</script>')[0]
    ok('C6 nessuna API di notifica/push nel modulo Live', not re.search(r'Notification|PushManager|showNotification|serviceWorker|\.subscribe\(', js))
    ok('C6 testo UI: avvisi solo all\'apertura, nessuna notifica in background', 'l’app non invia notifiche in background' in js and not re.search(r'riceverai (una )?notifica|ti avvis(iamo|eremo) anche', js, re.I))
    b.close()

# ---- C: controlli statici (nessun servizio a pagamento, nessuna scrittura sul repo, link sicuri)
wf = open(os.path.join(ROOT, '.github/workflows/tmdb-sync.yml'), encoding='utf-8').read()
gen = open(os.path.join(ROOT, 'tools/tva_live_build.py'), encoding='utf-8').read()
cfg = json.load(open(os.path.join(ROOT, 'tools/live/config.json'), encoding='utf-8'))
ok('C workflow: permessi in sola lettura, nessun push/commit, trigger solo manuale', 'contents: read' in wf and not re.search(r'git (push|commit)|contents: write|^\s*schedule:|^\s*push:', wf, re.M) and 'workflow_dispatch' in wf)
ok('C generatore: solo libreria standard (nessun pacchetto a pagamento/esterno)', not re.search(r'^\s*(import|from)\s+(requests|googleapiclient|openai|anthropic|boto3|feedparser)', gen, re.M))
ok('C generatore: non scrive index.html, schede Timeline o cataloghi esistenti', not re.search(r"open\([^)]*(index\.html|tmdb_map|tmdb_overrides|timeline)[^)]*['\"]w", gen))
ok('C fonti: nessun endpoint a pagamento, YouTube solo feed pubblico e canale @marvel', all(h in ('api.themoviedb.org', 'www.youtube.com') for h in set(re.findall(r'https://([\w.]+)/', json.dumps(cfg)) + re.findall(r"https://(api\.themoviedb\.org|www\.youtube\.com)", gen))) and 'googleapis.com/youtube' not in gen)
ok('C link esterni: ogni target=_blank ha rel noopener noreferrer', all('noopener noreferrer' in l for l in js.split('\n') if "target = '_blank'" in l) and js.count("target = '_blank'") >= 2)
ok('C link esterni: solo https validati (fonti e YouTube)', "/^https:\\/\\//.test(s.url" in js and 'youtube\\.com\\/watch' in js)
bad = [n for n, c in NS['res'] if not c]
print('\nRISULTATO: %d ok, %d falliti' % (len(NS['res']) - len(bad), len(bad)))
for n in bad: print(' FAIL:', n)
raise SystemExit(1 if bad else 0)
