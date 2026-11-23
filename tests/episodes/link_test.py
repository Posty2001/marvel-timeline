"""TVA Episodes <-> casella "visto" della Timeline. Uso: python3 tests/episodes/link_test.py"""
import sys, os, json
__file__ = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'ep_test.py')
exec(open(__file__).read().split("with sync_playwright() as p:")[0])
WK = 'marvel-ultimate-timeline-watched'
PUBLISHED = {'on': False}
def route_fixtures(pg, missing_index=False):   # ridefinisce: opzione "episodio futuro ormai uscito"
    def h(r):
        name = r.request.url.rsplit('/', 1)[-1]
        if name in FILES:
            d = json.loads(json.dumps(FILES[name]))
            if PUBLISHED['on'] and name == '61550.json':
                for sn in d['stagioni']:
                    for e in sn['episodi']:
                        if e['d'] == '2999-01-01': e['d'] = '2020-01-01'
            return r.fulfill(status=200, content_type='application/json', body=json.dumps(d))
        r.fulfill(status=404, body='')
    pg.route(re.compile(r'.*/assets/episodes/.*'), h)
    pg.route(re.compile(r'https://posty2001\.github\.io/.*'), lambda r: r.abort('internetdisconnected'))   # Live: endpoint remoto non raggiungibile nei test Episodes
def seed(**kw):
    js = ''
    for k, v in kw.items(): js += "localStorage.setItem('%s', JSON.stringify(%s));" % (k, json.dumps(v))
    return js
def checked(pg, cid): return pg.evaluate("(id)=>document.querySelector('#item-'+id+' input.watch-check').checked", cid)
def watched_ids(pg): return json.loads(ls(pg, WK) or '{}')
def eps_of(pg, cid): return (json.loads(ls(pg, KEY) or '{}')).get(cid, {})
def tick_series(pg, cid):   # tocco sulla casella (label) della scheda
    pg.evaluate("(id)=>document.querySelector('#item-'+id+' .watch-box').click()", cid); pg.wait_for_timeout(700)
def non_ep(pg):
    return pg.evaluate("(k)=>{const o={};for(let i=0;i<localStorage.length;i++){const n=localStorage.key(i);if(n!==k)o[n]=localStorage.getItem(n)}return o}", KEY)
def watch_ep(pg, cid, season, ep):
    se = pg.locator('#item-%s .ep-season' % cid).nth(season); se.evaluate("d=>{d.open=true}")
    b = se.locator('.ep-row').nth(ep).locator('.ep-w'); b.scroll_into_view_if_needed(); b.click(); pg.wait_for_timeout(150)

with sync_playwright() as p:
    b = p.chromium.launch()
    # 1-2: completamento automatico e deselezione
    pg = new_page(b); open_eps(pg, '043')
    for i in range(2): watch_ep(pg, '043', 0, i)
    ok('2/3 episodi visti: scheda NON completata', not checked(pg, '043'))
    watch_ep(pg, '043', 0, 2); pg.wait_for_timeout(500)
    ok('3/3 episodi visti -> scheda completata (casella + salvataggio)', checked(pg, '043') and '043' in watched_ids(pg))
    ok('altre schede della stessa serie (044) intatte', '044' not in json.loads(ls(pg, KEY)) and not checked(pg, '044'))
    watch_ep(pg, '043', 0, 1); pg.wait_for_timeout(500)
    ok('episodio deselezionato -> scheda non completata', not checked(pg, '043') and '043' not in watched_ids(pg))
    ok('deselezione: gli altri episodi restano visti', sum(1 for e in eps_of(pg, '043').values() if e.get('w')) == 2)
    watch_ep(pg, '043', 0, 1); pg.wait_for_timeout(500)
    ok('ri-selezione -> di nuovo completata', checked(pg, '043'))
    pg.reload(); pg.wait_for_selector('#item-043', state='attached'); pg.wait_for_timeout(500)
    ok('persistenza dopo ricarica: scheda completata + episodi visti', checked(pg, '043') and len([1 for e in eps_of(pg, '043').values() if e.get('w')]) == 3)
    ok('nessun errore JS', not pg.errs, str(pg.errs)); pg.close()
    # 3: completamento manuale dalla Timeline (pannello mai aperto), voti e recensioni intatti
    pg = new_page(b, init=seed(**{KEY: {'043': {'S01E01': {'r': 7, 'n': 'Rec', 't': 1}}, '039': {'S01E01': {'r': 9}}}}))
    tick_series(pg, '043')
    e = eps_of(pg, '043')
    ok('manuale: tutti gli episodi usciti della scheda risultano visti', all(e.get('S01E0%d' % i, {}).get('w') == 1 for i in (1, 2, 3)))
    ok('manuale: voto e recensione esistenti intatti', e['S01E01']['r'] == 7 and e['S01E01']['n'] == 'Rec')
    ok('manuale: altra serie (039) non toccata', json.loads(ls(pg, KEY))['039'] == {'S01E01': {'r': 9}} and '044' not in json.loads(ls(pg, KEY)))
    tick_series(pg, '043')
    e = eps_of(pg, '043')
    ok('manuale: scheda tolta con tutto visto -> visti azzerati, voti/recensioni intatti', not any(x.get('w') for x in e.values()) and e['S01E01']['r'] == 7 and e['S01E01']['n'] == 'Rec' and not checked(pg, '043'))
    ok('badge media episodi invariato dopo i cicli', '7,0' in (badge(pg, '043') or ''))
    pg.close()
    # 4: scheda tolta con progresso parziale (stato legacy): nessuna perdita
    pg = new_page(b, init=seed(**{KEY: {'043': {'S01E01': {'w': 1}}}, WK: {'043': True}}))
    tick_series(pg, '043')
    ok('scheda tolta con visti parziali: i visti restano (nessuna perdita)', eps_of(pg, '043').get('S01E01', {}).get('w') == 1); pg.close()
    # 5: stagioni separate (043 = S1, 044 = S2 della stessa serie)
    pg = new_page(b); tick_series(pg, '044'); k = json.loads(ls(pg, KEY))
    ok('stagioni separate: 044 modifica solo S02, 043 intatta', set(k.get('044', {}).keys()) == {'S02E01', 'S02E02', 'S02E03'} and '043' not in k and not checked(pg, '043'))
    ok('episodio futuro (S02E04) non segnato visto dalla completazione manuale', 'S02E04' not in k['044'] and checked(pg, '044')); pg.close()
    # 6: futuri: non impediscono il completamento
    pg = new_page(b); open_eps(pg, '044')
    for i in range(3): watch_ep(pg, '044', 0, i)
    pg.wait_for_timeout(500)
    ok('episodi futuri non impediscono il completamento (3 usciti visti)', checked(pg, '044')); pg.close()
    # 7: episodio pubblicato dopo il completamento: non annulla (apertura pannello)
    PUBLISHED['on'] = True
    pg = new_page(b, init=seed(**{KEY: {'044': {'S02E01': {'w': 1}, 'S02E02': {'w': 1}, 'S02E03': {'w': 1}}}, WK: {'044': True}}))
    open_eps(pg, '044'); pg.wait_for_timeout(400)
    ok('episodio pubblicato dopo il completamento: scheda resta completata e il nuovo non e\' marcato visto', checked(pg, '044') and 'S02E04' not in json.loads(ls(pg, KEY))['044'])
    pg.close(); PUBLISHED['on'] = False
    # 8: migrazione dati esistenti
    pg = new_page(b, init=seed(**{WK: {'043': True}})); open_eps(pg, '043'); pg.wait_for_timeout(400)
    ok('migrazione: scheda gia\' completata senza episodi -> episodi segnati visti', all(eps_of(pg, '043').get('S01E0%d' % i, {}).get('w') == 1 for i in (1, 2, 3)) and checked(pg, '043')); pg.close()
    pg = new_page(b, init=seed(**{KEY: {'043': {'S01E01': {'w': 1, 'r': 8}, 'S01E02': {'w': 1}, 'S01E03': {'w': 1}}}}))
    open_eps(pg, '043'); pg.wait_for_timeout(400)
    ok('migrazione (caso Moon Knight): 3/3 visti e scheda vuota -> scheda completata, voto intatto', checked(pg, '043') and eps_of(pg, '043')['S01E01']['r'] == 8); pg.close()
    pg = new_page(b, init=seed(**{KEY: {'043': {'S01E01': {'w': 1, 'r': 8}}}, WK: {'043': True}}))
    open_eps(pg, '043'); pg.wait_for_timeout(400)
    ok('migrazione: completata con visti parziali -> nessuna modifica automatica', checked(pg, '043') and sum(1 for e in eps_of(pg, '043').values() if e.get('w')) == 1); pg.close()
    # 9: nessuna ricompensa duplicata / nessun ciclo: stesso stato finale e stesso numero di eventi che con il tocco manuale
    def run(mode):
        pg = new_page(b); pg.evaluate("()=>{window.__c=0;document.querySelector('#item-043 input.watch-check').addEventListener('change',()=>window.__c++)}")
        if mode == 'manual': tick_series(pg, '043')
        else:
            open_eps(pg, '043')
            for i in range(3): watch_ep(pg, '043', 0, i)
            pg.wait_for_timeout(800)
        pg.wait_for_timeout(600); n = pg.evaluate("()=>window.__c"); st = non_ep(pg); pg.close(); return n, st
    n1, s1 = run('manual'); n2, s2 = run('episodes')
    vol = lambda d: {k: v for k, v in d.items() if not any(t in k.lower() for t in ('time', 'date', 'last', 'ts', 'session', 'visit'))}
    diff = [k for k in set(vol(s1)) | set(vol(s2)) if vol(s1).get(k) != vol(s2).get(k)]
    ok('un solo evento di cambio casella per completamento (nessun ciclo)', n1 == 1 and n2 == 1, '%s/%s' % (n1, n2))
    ok('stato finale (visti, XP, missioni, badge...) identico tra tocco manuale e completamento da episodi', not diff, str(diff))
    ok('nessuna ricompensa duplicata: chiavi badge/missioni/XP uguali', all(vol(s1).get(k) == vol(s2).get(k) for k in vol(s1) if re.search(r'badge|mission|xp|reward', k, re.I)))
    b.close()
bad = [n for n, c in res if not c]
print('\n%d/%d test superati' % (len(res) - len(bad), len(res)))
if bad: print('FALLITI:', bad); sys.exit(1)
