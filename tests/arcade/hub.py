# Hub Arcade: riapri gioco, dashboard progressi, backup/ripristino reversibile.
import sys, json, tempfile, os, urllib.request
from playwright.sync_api import sync_playwright
ROOT = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8790/'
URL = ROOT + 'arcade/'
RES = []; errs = []
def rec(n, ok, note=''):
    RES.append(bool(ok)); print(('PASS ' if ok else 'FAIL ') + n + ((' — ' + str(note)[:300]) if note else ''), flush=True)
def ev(pg, e): return pg.evaluate(e)
def newctx(br, w=390):
    ctx = br.new_context(viewport={'width': w, 'height': 844}, service_workers='block', accept_downloads=True); pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); return ctx, pg
def day(): 
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo('Europe/Rome')).strftime('%Y-%m-%d')
D = day()
SEED = {
 'tva-who-daily-v1-' + D: json.dumps({'version': 3, 'date': D, 'difficulty': 'agente', 'won': True, 'points': 780, 'answer': 'iron-man'}),
 'tva-crisis-daily-v1:' + D: json.dumps({'v': 1, 'score': 4210, 'hp': 63, 'won': True, 'completed_at': D + 'T10:00:00Z'}),
 'tva-escape-v2:santuario': json.dumps({'v': 2, 'solved': {'ricostruisci-il-simbolo': True, 'decifra-il-manoscritto': True}, 'hints': {'ricostruisci-il-simbolo': 2}, 'room': 'biblioteca-arcana', 'sent': False}),
 'tva-draft-save-v1': json.dumps({'v': 1, 'scenario': 'asgard', 'cpu': 'stratega', 'pool': ['a'] * 16, 'a': [], 'b': [], 'turn': 0, 'assign': {}, 'phase': 'draft', 'result': None}),
 'tva-crisis-best-v1': '5400',
 'tva-arcade-last-visited-v1': json.dumps({'game': 'draft', 'date': D + 'T10:00:00Z'}),
}
XP = {'marvel-ultimate-timeline-missioni-xp-bonus': json.dumps({'totale': 175}), 'marvel-ultimate-timeline-user-name': 'Variante Test'}
def seed(pg, d):
    for k, v in d.items(): pg.evaluate("([k,v])=>localStorage.setItem(k,v)", [k, v])
with sync_playwright() as p:
    br = p.chromium.launch()
    for w in (320, 390, 430):
        ctx, pg = newctx(br, w); pg.goto(URL); pg.wait_for_selector('a.game'); ev(pg, "document.querySelectorAll('.sec2').forEach(d=>d.open=true)")
        o = ev(pg, "({sw:document.documentElement.scrollWidth,iw:innerWidth,t:document.body.innerText})")
        small = ev(pg, "[...document.querySelectorAll('a,button,label.backup-import')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height<44).map(e=>(e.id||e.textContent).slice(0,20))")
        rec('H1 %dpx: hub senza overflow orizzontale di pagina, senza «prototipo/Lab», link/pulsanti ≥44px' % w, o['sw'] <= o['iw'] and 'prototip' not in o['t'].lower() and 'quiz lab' not in o['t'].lower() and not small, (o['sw'], o['iw'], small)); ctx.close()
    ctx, pg = newctx(br); pg.goto(URL); seed(pg, {**SEED, **XP}); pg.reload(); pg.wait_for_selector('a.game'); ev(pg, "document.querySelectorAll('.sec2').forEach(d=>d.open=true)")
    href = ev(pg, "document.getElementById('tva-resume-link').getAttribute('href')"); full = ev(pg, "document.getElementById('tva-resume-link').href")
    st = urllib.request.urlopen(full).status
    ok = []
    for g, h in {'quiz': '../quiz/?from=arcade', 'who': 'who-am-i/', 'time': 'time-crisis/', 'draft': 'draft/', 'escape': 'escape/'}.items():
        ev(pg, "localStorage.setItem('tva-arcade-last-visited-v1',JSON.stringify({game:'%s',date:new Date().toISOString()}))" % g); pg.reload(); pg.wait_for_selector('a.game'); ev(pg, "document.querySelectorAll('.sec2').forEach(d=>d.open=true)")
        u = ev(pg, "document.getElementById('tva-resume-link').href"); ok.append(urllib.request.urlopen(u).status == 200)
    rec('H2 «Riapri gioco» punta ai percorsi reali (5/5 raggiungibili, nessun 404)', all(ok) and st == 200, (href, ok))
    d = ev(pg, "({who:document.getElementById('p-who').textContent+' | '+document.getElementById('p-who-detail').textContent,t:document.getElementById('p-time').textContent+' | '+document.getElementById('p-time-detail').textContent,e:document.getElementById('p-escape').textContent+' | '+document.getElementById('p-escape-detail').textContent})")
    rec('H3 dashboard legge Who Am I (780), Time Crisis (4.210 pt) ed Escape v2 (2 enigmi)', '780' in d['who'] and '4' in d['t'] and '210' in d['t'] and '2' in d['e'], d)
    ev(pg, "localStorage.removeItem('tva-who-daily-v1-%s');localStorage.setItem('tva-who-progress-v1-%s',JSON.stringify({version:3,date:'%s',answerId:'iron-man',difficulty:'agente',credits:2,tries:5,used:1,hints:[],history:[],guessedIds:[]}))" % (D, D, D)); pg.click('#refresh-progress')
    rec('H4 Who Am I in corso (salvataggio v3) riconosciuto dalla dashboard', 'In corso' in pg.inner_text('#p-who'), pg.inner_text('#p-who'))
    # backup
    before = ev(pg, "(()=>{var o={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o})()")
    with pg.expect_download() as dl: pg.click('#backup-export')
    path = tempfile.mktemp(suffix='.json'); dl.value.save_as(path); bk = json.load(open(path))
    rec('H5 export: formato tva-arcade-local-backup, include solo chiavi Arcade (nessun XP/account)', bk['format'] == 'tva-arcade-local-backup' and all(k.startswith(('tva-', )) for k in bk['records']) and not any('marvel-ultimate' in k for k in bk['records']) and 'tva-escape-v2:santuario' in bk['records'] and 'tva-draft-save-v1' in bk['records'], list(bk['records'])[:8])
    ctx.close()
    # ripristino su profilo nuovo con XP presente e un dato preesistente diverso
    ctx, pg = newctx(br); pg.goto(URL); seed(pg, XP); seed(pg, {'tva-crisis-best-v1': '999'}); pg.reload(); pg.wait_for_selector('a.game'); ev(pg, "document.querySelectorAll('.sec2').forEach(d=>d.open=true)")
    pg.set_input_files('#backup-import', path); pg.wait_for_timeout(500); msg = pg.inner_text('#backup-status')
    after = ev(pg, "(()=>{var o={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o})()")
    rec('H6 import: ripristina i salvataggi mancanti, NON sovrascrive quelli presenti, XP intatto', 'tva-escape-v2:santuario' in after and after['tva-crisis-best-v1'] == '999' and after['marvel-ultimate-timeline-missioni-xp-bonus'] == XP['marvel-ultimate-timeline-missioni-xp-bonus'], msg)
    rec('H6b import compatibile con salvataggio Who v3 e Escape v2 (nessun rifiuto)', 'annullata' not in msg.lower() and 'Importati' in msg, msg)
    pg.click('#backup-undo'); post = ev(pg, "(()=>{var o={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o})()")
    expect = {'tva-crisis-best-v1': '999', **XP}
    rec('H7 «Annulla ultima importazione»: il profilo torna esattamente allo stato precedente (reversibile)', {k: v for k, v in post.items() if k != 'tva-arcade-last-import-v1'} == expect and 'tva-arcade-last-import-v1' not in post, sorted(post)[:6])
    # file non valido: nessuna scrittura
    bad = tempfile.mktemp(suffix='.json'); json.dump({'format': 'tva-arcade-local-backup', 'version': 1, 'records': {'tva-escape-v2:santuario': {'v': 2, 'solved': {'x': 'no'}}, 'tva-draft-save-v1': {'v': 1}}}, open(bad, 'w'))
    pg.set_input_files('#backup-import', bad); pg.wait_for_timeout(400); a2 = ev(pg, "Object.keys(localStorage).filter(k=>k.startsWith('tva-escape')||k.startsWith('tva-draft')).length")
    rec('H8 backup con record non valido: importazione annullata, nessuna scrittura parziale', 'annullata' in pg.inner_text('#backup-status').lower() and a2 == 0, pg.inner_text('#backup-status'))
    junk = tempfile.mktemp(suffix='.json'); open(junk, 'w').write('{{non json'); pg.set_input_files('#backup-import', junk); pg.wait_for_timeout(300)
    rec('H8b file non-JSON: errore gestito, nessun crash', 'annullata' in pg.inner_text('#backup-status').lower())
    rec('H9 nessun errore JS', not errs, errs[:3]); ctx.close(); br.close()
print('TOTALE %d test, %d PASS, %d FAIL' % (len(RES), sum(RES), len(RES) - sum(RES)))
