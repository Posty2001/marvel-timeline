"""TVA Live 1.1 Fase 3 - lettura remota da GitHub Pages: aggiornamento, SHA-256, versioni, obsoleti, cache, assenza di rete, avvisi.
Endpoint simulato con route Playwright sull'URL REALE (https://posty2001.github.io/tva-live-scheduler/v1/); dati di prova isolati. Uso: python3 tests/live/remote_test.py"""
import copy, datetime as dt, hashlib, json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
NS = {'__file__': os.path.join(HERE, 'ui_test.py'), '__name__': 'ui_helpers'}
exec(compile(open(NS['__file__'], encoding='utf-8').read().split('with sync_playwright() as pw:')[0], NS['__file__'], 'exec'), NS)
item, new_ctx, open_page, reload, go_live, txt, jl, ls, ok, STATE, manifest, PK, SK, ROOT, CAL, TR = (NS[k] for k in ('item', 'new_ctx', 'open_page', 'reload', 'go_live', 'txt', 'jl', 'ls', 'ok', 'STATE', 'manifest', 'PK', 'SK', 'ROOT', 'CAL', 'TR'))
sync_playwright = NS['sync_playwright']; res = NS['res']
BASE = 'https://posty2001.github.io/tva-live-scheduler/v1/'; KR = 'marvel-ultimate-timeline-live-remote-v1'
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
def G(h): return (NOW + dt.timedelta(hours=h)).isoformat(timespec='seconds')      # h negativo = nel passato
def canon(o): return json.dumps(o, ensure_ascii=False, sort_keys=True, indent=1) + '\n'
def sha(s): return hashlib.sha256(s.encode('utf-8') if isinstance(s, str) else s).hexdigest()
def mk(cal, trl, gen, post=None, pre=None):
    """Bundle come lo pubblica publish_catalog.py. pre(c,t,m) altera gli oggetti PRIMA degli hash; post(files, ptr) DOPO (manomissione)."""
    c = {'schema': 1, 'generated_at': gen, 'items': copy.deepcopy(cal)}; t = {'schema': 1, 'generated_at': gen, 'items': copy.deepcopy(trl)}
    m = manifest(generated_at=gen); m['counts'] = {'calendar': len(c['items']), 'trailers': len(t['items'])}
    if pre: pre(c, t, m)
    tx = {'calendar': canon(c), 'trailers': canon(t), 'manifest': canon(m)}; sh = {n: sha(x) for n, x in tx.items()}
    vid = sha('\n'.join('%s:%s' % (n, sh[n]) for n in ('calendar', 'trailers', 'manifest')))[:16]
    ptr = {'schema': 1, 'version': vid, 'generated_at': gen, 'content_hash': 'x', 'files': {n: {'path': 'c/%s/%s.json' % (vid, n), 'sha256': sh[n], 'bytes': len(tx[n].encode())} for n in tx}}
    files = {ptr['files'][n]['path']: tx[n] for n in tx}
    if post: post(files, ptr)
    return {'ptr': ptr, 'files': files}
REG = {'ptr': None, 'files': {}, 'mode': 'ok', 'hits': []}
def serve(bundle, mode='ok'):
    REG.update(ptr=json.dumps(bundle['ptr']) if bundle else None, files=dict(bundle['files']) if bundle else {}, mode=mode, hits=[], fromcache=False)
def remote_route(pg):
    def h(r):
        u = r.request.url; REG['hits'].append(u); rel = u[len(BASE):] if u.startswith(BASE) else None
        if REG['mode'] == 'offline': return r.abort('internetdisconnected')
        if REG['mode'] == 'hang': return
        if REG['mode'] == '500': return r.fulfill(status=500, body='')
        body = REG['ptr'] if rel == 'current.json' else REG['files'].get(rel)
        hd = {'access-control-allow-origin': '*', 'cache-control': 'max-age=600', 'access-control-expose-headers': 'X-TVA-From-Cache'}
        if REG.get('fromcache') and rel == 'current.json': hd['x-tva-from-cache'] = '1'
        r.fulfill(status=200, content_type='application/json', headers=hd, body=body) if body is not None else r.fulfill(status=404, body='', headers=hd)
    pg.route(re.compile(r'https://posty2001\.github\.io/.*'), h)
orig_routes = NS['routes']
NS['routes'] = lambda pg: (orig_routes(pg), remote_route(pg))
def base_state(): NS['reset_state'](); STATE['man'] = manifest(generated_at=G(-120))
def boot(b, bundle=None, mode='ok', pre_store=None, ctx=None):
    base_state(); serve(bundle, mode); ctx = ctx or new_ctx(b); pg = open_page(ctx)
    if pre_store is not None: pg.evaluate("(s)=>localStorage.setItem('%s', s)" % KR, pre_store); reload(pg)
    go_live(pg); return ctx, pg
def D(pg): return pg.evaluate("()=>{const d=window.tvaLive.data();return {s:d.source,e:d.remoteErr,rej:d.remoteRejected,v:d.version,old:d.olderThanSeen,cal:d.calendar.map(i=>i.key),trl:d.trailers.map(i=>i.key),gen:d.manifest&&d.manifest.generated_at,rf:d.refreshFailed}}")
def store(pg): v = ls(pg, KR); return json.loads(v) if v else None
def ind(pg): return pg.evaluate("()=>window.tvaLive.prefs().inbox.map(a=>a.t+':'+a.k)")
NEWI = lambda: item('tmdb:movie:5000', 'Solo Remoto', G(0)[:10] if False else (NOW + dt.timedelta(days=90)).date().isoformat(), category='film')
CALN = copy.deepcopy(CAL) + [NEWI()]
def B1(**kw): return mk(CALN, TR, G(-24), **kw)           # catalogo remoto valido e piu recente di quello incluso (-120h)
def refused(b, name, bundle, why, mode='ok'):
    ctx, pg = boot(b, bundle, mode); d = D(pg)
    ok('%s: rifiutato (%s), si usano i dati inclusi, niente dati remoti' % (name, why), d['s'] == 'bundled' and d['rej'] is True and why.lower() in (d['e'] or '').lower() and 'tmdb:movie:5000' not in d['cal'] and store(pg) is None, d)
    ok('%s: il motivo e il ripiego sono visibili nello stato dati' % name, 'rifiutato' in txt(pg, '.tvl-status').lower() and 'dati inclusi' in txt(pg, '.tvl-status').lower())
    ctx.close()

with sync_playwright() as pw:
    b = pw.chromium.launch()
    # ---- R1 aggiornamento remoto valido
    ctx, pg = boot(b, B1()); d = D(pg); st = store(pg)
    ok('R1 aggiornamento remoto verificato: fonte remota, versione del puntatore, dati nuovi presenti', d['s'] == 'remote' and d['e'] is None and d['v'] == json.loads(REG['ptr'])['version'] and 'tmdb:movie:5000' in d['cal'], d)
    ok('R1 la copia locale e la soglia sono salvate (puntatore + testi + generated_at piu recente)', st and st['ptr']['version'] == d['v'] and set(st['tx']) == {'calendar', 'trailers', 'manifest'} and st['floor'] == int(dt.datetime.fromisoformat(G(-24)).timestamp() * 1000), st and list(st))
    ok('R1 stato dati: fonte "aggiornamento online verificato" e versione', 'aggiornamento online verificato' in txt(pg, '.tvl-status') and d['v'][:8] in txt(pg, '.tvl-status'))
    ok('R1 richieste solo al prefisso consentito: puntatore + 3 file immutabili, nessun altro host', len(REG['hits']) == 4 and all(u.startswith(BASE) for u in REG['hits']) and REG['hits'][0].endswith('current.json'), REG['hits'])
    ok('R1 il calendario mostra la voce arrivata solo dal remoto', pg.locator('.tvl-row[data-key="tmdb:movie:5000"]').count() == 1 or 'Solo Remoto' in pg.evaluate("()=>document.getElementById('cenPan-live').textContent"))
    # ---- R2 riapertura con rete assente: copia locale
    serve(None, 'offline'); reload(pg); go_live(pg); d = D(pg)
    ok('R2 rete assente dopo un aggiornamento: ultima versione valida dalla copia locale (non i dati inclusi piu vecchi)', d['s'] == 'cache' and 'tmdb:movie:5000' in d['cal'] and 'rete non raggiungibile' in (d['e'] or ''), d)
    ok('R2 stato dati: "copia salvata sul dispositivo" e motivo', 'copia salvata' in txt(pg, '.tvl-status') and 'non disponibile' in txt(pg, '.tvl-status'))
    # ---- R3 cache locale manomessa: rivalidata, scartata
    st = store(pg); st['tx']['calendar'] = st['tx']['calendar'].replace('Solo Remoto', 'Solo RemotX'); pg.evaluate("(s)=>localStorage.setItem('%s', s)" % KR, json.dumps(st)); reload(pg); go_live(pg); d = D(pg)
    ok('R3 copia locale alterata (hash diverso): scartata, ripiego sui dati inclusi', d['s'] == 'bundled' and 'tmdb:movie:5000' not in d['cal'], d)
    ok('R3 la soglia (floor) resta: i dati inclusi sono piu vecchi di quelli gia visti -> nessun nuovo avviso e avviso a schermo', d['old'] is True and 'più vecchi' in txt(pg, '.tvl-status'))
    ctx.close()
    # ---- R4 cataloghi obsoleti
    ctx, pg = boot(b, mk(CALN, TR, G(-240))); d = D(pg)
    ok('R4 catalogo remoto piu vecchio di quello incluso: ignorato (anti-regressione)', d['s'] == 'bundled' and 'tmdb:movie:5000' not in d['cal'] and d['e'] is None, d); ctx.close()
    ctx, pg = boot(b, B1()); serve(mk(CALN[:-1], TR, G(-48)), 'ok'); reload(pg); go_live(pg); d = D(pg)
    ok('R4 dopo un catalogo accettato, uno remoto piu vecchio (anche valido) non lo sostituisce: resta la copia locale', d['s'] == 'cache' and 'tmdb:movie:5000' in d['cal'] and d['gen'] == G(-24), d)
    serve(mk(CALN + [item('tmdb:movie:5001', 'Ancora Piu Nuovo', (NOW + dt.timedelta(days=95)).date().isoformat(), category='film')], TR, G(-1))); reload(pg); go_live(pg); d = D(pg)
    ok('R4 un catalogo remoto piu recente sostituisce la copia locale e aggiorna la soglia', d['s'] == 'remote' and 'tmdb:movie:5001' in d['cal'] and store(pg)['floor'] == int(dt.datetime.fromisoformat(G(-1)).timestamp() * 1000), d)
    ctx.close()
    # ---- R5 hash errato, versioni miste, puntatore incoerente
    def bad_hash(files, ptr):
        p = ptr['files']['calendar']['path']; files[p] = files[p].replace('Solo Remoto', 'Solo RemotX')      # stessa lunghezza, contenuto diverso
    refused(b, 'R5 hash SHA-256 errato (contenuto alterato a pari lunghezza)', B1(post=bad_hash), 'hash SHA-256 errato')
    def bad_size(files, ptr): p = ptr['files']['trailers']['path']; files[p] = files[p] + ' '
    refused(b, 'R5 file piu lungo di quanto dichiarato', B1(post=bad_size), 'dimensione')
    def mixed_old(files, ptr):          # il puntatore nuovo indica un calendario di un'altra versione (stessa forma, altro contenuto)
        other = mk(CAL, TR, G(-30)); p = ptr['files']['calendar']['path']; files[p] = other['files'][other['ptr']['files']['calendar']['path']]
    refused(b, 'R5 calendario di una versione diversa nel bundle', B1(post=mixed_old), 'errat')
    def mixed_gen(c, t, m): t['generated_at'] = G(-23)          # hash coerenti, ma generated_at diverso tra i file
    refused(b, 'R5 versioni miste (generated_at diverso, hash tutti validi)', B1(pre=mixed_gen), 'versioni miste')
    def bad_ver(files, ptr): ptr['version'] = '0123456789abcdef'; [f.update(path='c/0123456789abcdef/%s.json' % n) for n, f in ptr['files'].items()]; files.update({'c/0123456789abcdef/%s.json' % n: files[[x for x in files if x.endswith('/%s.json' % n)][0]] for n in ('calendar', 'trailers', 'manifest')})
    refused(b, 'R5 id di versione non derivato dai file', B1(post=bad_ver), 'versione non coerente')
    def trav(files, ptr): ptr['files']['calendar']['path'] = 'c/../../x/calendar.json'
    refused(b, 'R5 percorso del puntatore fuori dalla versione (path traversal)', B1(post=trav), 'percorso non valido')
    def sch2(files, ptr): ptr['schema'] = 2
    refused(b, 'R5 puntatore con schema diverso', B1(post=sch2), 'puntatore non valido')
    def big(files, ptr): ptr['files']['trailers']['bytes'] = 99999
    refused(b, 'R5 dimensione dichiarata oltre il limite', B1(post=big), 'puntatore non valido')
    # ---- R6 contenuti non validi (hash coerenti: il rifiuto e dovuto ai controlli di validita)
    def evil(c, t, m): c['items'][0]['sources'].append({'name': 'x', 'official': False, 'url': 'https://evil.example.com/x'})
    refused(b, 'R6 link verso host non ammesso', B1(pre=evil), 'link non ammesso')
    def js(c, t, m): c['items'][0]['sources'][0]['url'] = 'javascript:alert(1)'
    refused(b, 'R6 link javascript:', B1(pre=js), 'link non ammesso')
    def dupk(c, t, m): c['items'].append(copy.deepcopy(c['items'][0])); m['counts']['calendar'] = len(c['items'])
    refused(b, 'R6 chiave duplicata', B1(pre=dupk), 'voce non valida')
    def badit(c, t, m): c['items'][0]['kind'] = 'boh'
    refused(b, 'R6 voce con tipo non valido', B1(pre=badit), 'voce non valida')
    def empty(c, t, m): c['items'] = []; m['counts']['calendar'] = 0
    refused(b, 'R6 calendario vuoto', B1(pre=empty), 'catalogo vuoto')
    def fut(c, t, m): pass
    refused(b, 'R6 data di generazione nel futuro (blocco degli aggiornamenti successivi)', mk(CALN, TR, G(24 * 5)), 'futuro')
    def cnt(c, t, m): m['counts']['trailers'] = 77
    refused(b, 'R6 conteggi del manifest incoerenti', B1(pre=cnt), 'conteggi')
    def badtr(c, t, m): t['items'][0]['url'] = 'https://evil.example.com/watch?v=AAAAAAAAAAA'
    refused(b, 'R6 trailer con URL non YouTube', B1(pre=badtr), 'trailer non valido')
    # ---- R7 guasti di rete
    for mode, why in (('offline', 'rete non raggiungibile'), ('500', 'HTTP 500')):
        ctx, pg = boot(b, B1(), mode); d = D(pg)
        ok('R7 endpoint %s: dati inclusi, nessun errore bloccante, motivo mostrato' % mode, d['s'] == 'bundled' and why in (d['e'] or '') and d['rej'] is False and 'DATI NON DISPONIBILI' not in txt(pg, '.tvl-status') and not pg.errs, (d, pg.errs)); ctx.close()
    ctx, pg = boot(b, None, 'ok'); d = D(pg)
    ok('R7 puntatore assente (404): dati inclusi', d['s'] == 'bundled' and 'HTTP 404' in (d['e'] or ''), d); ctx.close()
    ctx = new_ctx(b); base_state(); serve(B1(), 'hang'); pg = open_page(ctx); go_live(pg)
    pg.wait_for_function("()=>window.tvaLive.data().remoteErr", timeout=20000); d = D(pg)
    ok('R7 endpoint che non risponde: timeout (9 s) e ripiego sui dati inclusi', d['s'] == 'bundled' and 'timeout' in (d['e'] or ''), d); ctx.close()
    ctx = new_ctx(b); ctx.add_init_script("Object.defineProperty(window.crypto,'subtle',{value:undefined,configurable:true})"); base_state(); serve(B1()); pg = open_page(ctx); go_live(pg); d = D(pg)
    ok('R7 SHA-256 non disponibile: i dati remoti NON si accettano senza verifica', d['s'] == 'bundled' and 'sha-256 non disponibile' in (d['e'] or '').lower() and 'tmdb:movie:5000' not in d['cal'], d); ctx.close()
    # ---- R8 avvisi
    ctx, pg = boot(b, None, 'offline'); ok('R8 primo avvio (dati inclusi): nessun avviso', ind(pg) == [] and jl(pg, SK)['init'] is True)
    serve(B1()); reload(pg); go_live(pg, 'avv')
    ok('R8 aggiornamento remoto con una nuova uscita: un solo avviso "nuova"', ind(pg) == ['new:tmdb:movie:5000'], ind(pg))
    for i in range(3): reload(pg); go_live(pg)
    ok('R8 riaperture ripetute (remoto, poi copia, poi dati inclusi): nessun avviso duplicato', ind(pg) == ['new:tmdb:movie:5000'], ind(pg))
    serve(None, 'offline'); reload(pg); go_live(pg); ok('R8 rete assente (copia locale): nessun avviso duplicato', D(pg)['s'] == 'cache' and ind(pg) == ['new:tmdb:movie:5000'])
    nc = copy.deepcopy(CALN); nc[2]['date'] = (NOW + dt.timedelta(days=210)).date().isoformat(); nc[0]['confidence'] = 'confirmed'; nc[0]['sources'].insert(0, {'name': 'YouTube - Marvel Entertainment', 'url': 'https://www.youtube.com/watch?v=AAAAAAAAAAA', 'official': True})
    serve(mk(nc, TR + [{'key': 'yt:CCCCCCCCCCC', 'title': 'Nuovo Teaser', 'published': NOW.date().isoformat(), 'url': 'https://www.youtube.com/watch?v=CCCCCCCCCCC', 'channel': 'Marvel Entertainment', 'kind': 'trailer', 'official': True, 'relatesTo': None}], G(-2))); reload(pg); go_live(pg)
    k = ind(pg); ok('R8 remoto con cambio data + conferma + nuovo trailer: un avviso per tipo, ciascuno una volta', sorted(x.split(':')[0] for x in k) == ['confirmed', 'date', 'new', 'trailer'] and len(k) == 4, k)
    reload(pg); go_live(pg); ok('R8 stessa versione riaperta: ancora 4 avvisi', len(ind(pg)) == 4)
    # remoto di nuovo piu vecchio e valido (CDN che serve una copia vecchia): nessun avviso "all'indietro"
    serve(mk(CALN, TR, G(-30))); reload(pg); go_live(pg); d = D(pg)
    ok('R8 copia vecchia servita dalla CDN: ignorata, nessun avviso di ritorno al vecchio valore', d['s'] == 'cache' and len(ind(pg)) == 4 and not any(a.startswith('date:') and a.count('|') for a in ind(pg)), (d['s'], ind(pg)))
    # perdita della copia locale (es. pulizia di Safari) ma non della soglia: dati inclusi piu vecchi -> nessun avviso
    st = store(pg); pg.evaluate("(s)=>localStorage.setItem('%s', s)" % KR, json.dumps({'floor': st['floor']})); serve(None, 'offline'); reload(pg); go_live(pg); d = D(pg)
    ok('R8 senza copia locale e rete: dati inclusi piu vecchi della soglia -> nessun avviso nuovo/"indietro"', d['s'] == 'bundled' and d['old'] is True and len(ind(pg)) == 4, (d, ind(pg)))
    ctx.close()
    # ---- R9 preferenze, titoli seguiti, stato avvisi intatti
    ctx, pg = boot(b, None, 'offline')
    pg.evaluate("(o)=>localStorage.setItem('marvel-ultimate-timeline-live-v1', JSON.stringify(o))", {'v': 1, 'cats': {'film': True, 'serie': False, 'animazione': True, 'game': True, 'trailer': True}, 'lead': [3, 0], 'followed': ['tmdb:movie:1', 'tmdb:movie:5000'], 'muted': ['tmdb:movie:3'], 'onlyUnwatched': True})
    reload(pg); go_live(pg); p0 = pg.evaluate("()=>window.tvaLive.prefs()"); k0 = ls(pg, PK)
    serve(B1()); reload(pg); go_live(pg); p1 = pg.evaluate("()=>window.tvaLive.prefs()")
    ok('R9 preferenze, seguiti, silenziati, anticipi e filtri identici dopo l\'aggiornamento remoto', all(p0[f] == p1[f] for f in ('cats', 'lead', 'followed', 'muted', 'onlyUnwatched')) and ls(pg, PK) == k0, (p0, p1))
    serve(None, 'offline'); reload(pg); go_live(pg); p2 = pg.evaluate("()=>window.tvaLive.prefs()")
    ok('R9 stesso risultato con rete assente', all(p0[f] == p2[f] for f in ('cats', 'lead', 'followed', 'muted', 'onlyUnwatched')))
    ok('R9 la cache remota NON e nel profilo/backup (chiave separata, fuori da PROFILE_OBJ_KEYS)', KR not in open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read().split('PROFILE_OBJ_KEYS = {')[1].split('};')[0])
    ctx.close()
    # ---- R10 dati reali del repository, pubblicati con lo stesso formato del publisher
    real = {n: json.load(open(os.path.join(ROOT, 'assets/live', n + '.json'), encoding='utf-8')) for n in ('calendar', 'trailers', 'manifest')}
    tx = {n: canon(real[n]) for n in real}
    assert tx == {n: open(os.path.join(ROOT, 'assets/live', n + '.json'), encoding='utf-8').read() for n in real}
    sh = {n: sha(tx[n]) for n in tx}; vid = sha('\n'.join('%s:%s' % (n, sh[n]) for n in ('calendar', 'trailers', 'manifest')))[:16]
    rb = {'ptr': {'schema': 1, 'version': vid, 'generated_at': real['manifest']['generated_at'], 'content_hash': real['manifest']['content_hash'], 'files': {n: {'path': 'c/%s/%s.json' % (vid, n), 'sha256': sh[n], 'bytes': len(tx[n].encode())} for n in tx}}, 'files': {'c/%s/%s.json' % (vid, n): tx[n] for n in tx}}
    base_state(); STATE['man'] = manifest(generated_at='2020-01-01T00:00:00+00:00'); serve(rb); ctx = new_ctx(b); pg = open_page(ctx); go_live(pg); d = D(pg)
    ok('R10 il catalogo REALE del repository (stesso formato del publisher) supera tutti i controlli ed e accettato', d['s'] == 'remote' and len(d['cal']) == len(real['calendar']['items']) and d['e'] is None, d)
    ctx.close()
    # ---- R11 rientro in primo piano
    ctx, pg = boot(b, None, 'offline'); serve(B1()); pg.evaluate("()=>{const o=Date.now.bind(Date); Date.now=()=>o()+31*60000; document.dispatchEvent(new Event('visibilitychange'))}")
    pg.wait_for_function("()=>window.tvaLive.data().source==='remote'", timeout=8000); ok('R11 app aperta a lungo: al rientro in primo piano (dopo 30+ min) ricontrolla e applica la nuova versione', 'tmdb:movie:5000' in D(pg)['cal'])
    n = len(REG['hits']); pg.evaluate("()=>document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(600)
    ok('R11 rientri ravvicinati non rifanno richieste (limite 30 minuti)', len(REG['hits']) == n, REG['hits'][n:]); ctx.close()
    # ---- R13 app ripresa dalla memoria: l indicatore segue la fonte realmente usata, mai "online" se non e avvenuto
    ctx, pg = boot(b, B1()); k0 = ind(pg); p0 = pg.evaluate("()=>window.tvaLive.prefs()"); t0 = txt(pg, '.tvl-status')
    ok('R13 online: "aggiornamento online verificato alle HH:MM" con orario della verifica e versione', re.search(r'aggiornamento online verificato (alle \d\d:\d\d|il )', t0) and D(pg)['s'] == 'remote', t0)
    ok('R13 la verifica online e registrata nella copia locale (data/ora)', isinstance(store(pg).get('at'), int) and abs(store(pg)['at'] - pg.evaluate("()=>Date.now()")) < 60000)
    at0 = store(pg)['at']; REG['mode'] = 'offline'; pg.wait_for_timeout(2300); ctx.set_offline(True)          # NESSUN ricaricamento: l'app resta in memoria e riceve l'evento offline
    pg.wait_for_function("()=>window.tvaLive.data().source==='cache'", timeout=8000); pg.evaluate("()=>window.tvaLive.render()"); t1 = txt(pg, '.tvl-status')
    ok('R13 offline senza ricaricare: la fonte diventa "copia salvata", non resta "online verificato"', 'copia salvata sul dispositivo' in t1 and 'aggiornamento online verificato' not in t1 and 'ultima verifica online' in t1, t1)
    ok('R13 la copia salvata conserva l ora dell ultima verifica online reale (non la rinnova)', store(pg)['at'] == at0)
    ok('R13 offline: motivo mostrato, nessun avviso nuovo/duplicato, preferenze invariate', 'rete non raggiungibile' in t1 and ind(pg) == k0 and all(pg.evaluate("()=>window.tvaLive.prefs()")[f] == p0[f] for f in ('cats', 'lead', 'followed', 'muted', 'onlyUnwatched')))
    ctx.set_offline(False); REG['mode'] = 'ok'; pg.wait_for_timeout(5200); pg.evaluate("()=>window.dispatchEvent(new Event('online'))")
    pg.wait_for_function("()=>window.tvaLive.data().source==='remote'", timeout=8000); pg.evaluate("()=>window.tvaLive.render()"); t2 = txt(pg, '.tvl-status')
    ok('R13 ritorno online senza ricaricare: nuova verifica e fonte di nuovo "online verificato" con orario aggiornato', 'aggiornamento online verificato' in t2 and store(pg)['at'] > at0 and ind(pg) == k0, t2)
    # app aperta (stato "remoto") quando il sistema va offline ma l'evento non arriva: l'indicatore non mente sul presente
    pg.evaluate("()=>{Object.defineProperty(navigator,'onLine',{get:()=>false,configurable:true}); window.tvaLive.render()}"); t3 = txt(pg, '.tvl-status')
    ok('R13 offline noto al browser ma dati ancora in memoria: avviso esplicito "ora offline, dati dell ultimo controllo"', 'offline' in t3 and 'ultimo controllo online' in t3, t3)
    ctx.close()
    # ---- R14 puntatore servito dalla cache del service worker (rete assente): dati verificati ma NON "online"
    base_state(); serve(B1()); ctx = new_ctx(b); pg = open_page(ctx); go_live(pg); REG['fromcache'] = True; reload(pg); go_live(pg); d = D(pg); t = txt(pg, '.tvl-status')
    ok('R14 puntatore dalla cache del SW: fonte "copia salvata", motivo "rete non raggiungibile", mai "online verificato"', d['s'] == 'cache' and 'rete non raggiungibile' in (d['e'] or '') and 'aggiornamento online verificato' not in t and 'copia salvata' in t, (d, t))
    ok('R14 la verifica online registrata resta quella reale precedente (il puntatore dalla cache non la rinnova)', store(pg)['at'] <= pg.evaluate("()=>Date.now()") - 1 and d['v'] == json.loads(REG['ptr'])['version'])
    ctx.close()
    # ---- R12 statici: perimetro delle modifiche
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read(); csp = re.search(r'Content-Security-Policy" content="([^"]+)"', src).group(1)
    cs = [x for x in csp.split(';') if x.strip().startswith('connect-src')][0]
    ok('R12 CSP: connect-src ammette il SOLO prefisso dell endpoint (non l intero dominio); nessun unsafe-eval', 'https://posty2001.github.io/tva-live-scheduler/v1/' in cs and not re.search(r'https://posty2001\.github\.io[ ;]', cs + ' ') and 'unsafe-eval' not in csp and "default-src 'self'" in csp)
    REF = '415f5a9'      # ultimo commit prima della Fase 3 (lettura remota)
    def hunks(path):
        dd = subprocess.run(['git', 'diff', '-U0', REF, '--', path], cwd=ROOT, capture_output=True, text=True).stdout
        return [(int(m.group(3)), int(m.group(4) or 1)) for m in re.finditer(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', dd, re.M)], dd
    lines = src.split('\n'); lo = next(i for i, l in enumerate(lines, 1) if 'LIVE-JS-BEGIN' in l); hi = next(i for i, l in enumerate(lines, 1) if 'LIVE-JS-END' in l); bad = []
    m0 = next(i for i, l in enumerate(lines, 1) if l.strip() == '<script id="mm-host">'); m1 = next(i for i, l in enumerate(lines, 1) if 'MM-HOST-END' in l) + 1   # Miss Minutes 1.0: blocco di integrazione approvato
    for s0, n0 in hunks('index.html')[0]:
        for ln in range(s0, s0 + max(n0, 1)):
            t = lines[ln - 1] if ln - 1 < len(lines) else ''
            if not (lo <= ln <= hi or m0 <= ln <= m1 or 'Content-Security-Policy' in t or 'tva-build' in t or 'Progetto fan non ufficiale' in t): bad.append(ln)   # ultima: patch disclaimer approvata
    ok('R12 index.html (rispetto a prima della Fase 3): modificate solo le righe del blocco TVA Live, la CSP e il build stamp (nessun\'altra sezione)', not bad, bad[:10])
    swl = open(os.path.join(ROOT, 'sw.js'), encoding='utf-8').read().split('\n'); f0 = next(i for i, l in enumerate(swl, 1) if l.startswith('/* F3b')); f1 = next(i for i in range(f0, len(swl)) if swl[i - 1] == '}')
    badsw = [ln for s0, n0 in hunks('sw.js')[0] for ln in range(s0, s0 + max(n0, 1)) if not (f0 <= ln <= f1 or 'F3b' in swl[ln - 1] or re.search(r'20261124-\d{4}-(live5|final|mm\d)', swl[ln - 1]) or 'MM_FILES' in swl[ln - 1] or 'precacheMissMinutes' in swl[ln - 1] or 'Miss Minutes' in swl[ln - 1] or 'workers' in swl[ln - 1] or ('Gateway Miss Minutes' in swl[ln - 1]) or (ln >= 2 and 'precacheMissMinutes' in ' '.join(swl[max(0, ln - 4):ln + 2])) or not swl[ln - 1].strip())]
    ok('R12 sw.js: solo build stamp e la marcatura F3b dei JSON serviti dalla cache (resto del service worker identico)', not badsw and len(hunks('sw.js')[0]) >= 3, badsw[:5])
    qa = subprocess.run(['git', 'diff', '-U0', REF, '--', 'quiz', 'arcade'], cwd=ROOT, capture_output=True, text=True).stdout
    chg = [l for l in qa.splitlines() if re.match(r'^[+-](?![+-]{2})', l)]
    ARC_OK = ('100svh', 'dvh - 400px', '.th .nm{font-size')   # correzioni Arcade approvate: fallback vh per iOS vecchi, nome tagliato a 320px
    ok('R12 Quiz e Arcade: cambia solo il build stamp (e le 3 correzioni Arcade approvate)', chg and all(('20261124-' in l and ('live' in l or 'final' in l or 'mm5' in l or 'mm4' in l)) or '20261123-' in l or any(k in l for k in ARC_OK) for l in chg), [l[:80] for l in chg if '20261124-' not in l and '20261123-' not in l][:3])
    sw = open(os.path.join(ROOT, 'sw.js'), encoding='utf-8').read()
    ok('R12 service worker: gestore generico network-first per ogni GET (anche cross-origin CORS), in cache solo risposte 200', "req.method !== 'GET'" in sw and 'networkResponse.status === 200' in sw and 'cache.put(req' in sw)
    ok('R12 marcatura F3b: solo file .json con risposta leggibile, mai navigazioni/redirect/opachi', "/\\.json$/.test(" in sw and "req.mode === 'navigate'" in sw and 'cached.redirected' in sw and "cached.type !== 'basic' && cached.type !== 'cors'" in sw)
    ls_ = open(os.path.join(ROOT, 'tests/live/remote_test.py')).read()
    b.close()
bad = [n for n, c in res if not c]; rem = [(n, c) for n, c in res]
print('\n%d/%d PASS' % (len(res) - len(bad), len(res)))
for n in bad: print('FAIL: ' + n)
raise SystemExit(1 if bad else 0)
