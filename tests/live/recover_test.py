"""TVA Live - recupero di emergenza (tools/live_recover.py): ripubblica una versione nota con generated_at nuovo. Repository git temporaneo, nessuna rete."""
import json, os, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import live_recover as R
PASS = FAIL = 0
def ok(c, msg, x=''):
    global PASS, FAIL
    if c: PASS += 1; print('PASS', msg)
    else: FAIL += 1; print('FAIL', msg, x)
def sh(d, *a): return subprocess.run(['git', '-C', d] + list(a), capture_output=True, text=True, check=True).stdout.strip()
d = tempfile.mkdtemp(); os.makedirs(d + '/tools/live'); os.makedirs(d + '/assets/live')
shutil.copy(ROOT + '/tools/live/config.json', d + '/tools/live/config.json')
for n in ('calendar', 'trailers', 'manifest', 'status'): shutil.copy(ROOT + '/assets/live/%s.json' % n, d + '/assets/live/%s.json' % n)
sh(d, 'init', '-q', '-b', 'test/tva-archives'); sh(d, 'config', 'user.email', 't@t'); sh(d, 'config', 'user.name', 't')
sh(d, 'add', '-A'); sh(d, 'commit', '-q', '-m', 'good'); good = sh(d, 'rev-parse', 'HEAD')
good_man = json.load(open(d + '/assets/live/manifest.json'))
# versione "cattiva" (valida ma sbagliata) con generated_at piu recente
cal = json.load(open(d + '/assets/live/calendar.json')); man = json.load(open(d + '/assets/live/manifest.json'))
cal['items'][0]['date'] = '2027-01-01'; cal['generated_at'] = man['generated_at'] = '2026-12-01T00:00:00+00:00'
json.dump(cal, open(d + '/assets/live/calendar.json', 'w')); json.dump(man, open(d + '/assets/live/manifest.json', 'w'))
sh(d, 'add', '-A'); sh(d, 'commit', '-q', '-m', 'bad')
NOW = '2026-12-02T10:00:00+00:00'
r = R.recover(d, good[:12], now=NOW, dry=True, out=d + '/o')
ok(json.load(open(d + '/assets/live/calendar.json'))['items'][0]['date'] == '2027-01-01', 'prova a secco: nessun file toccato')
r = R.recover(d, good[:12], now=NOW, out=d + '/o')
c2 = json.load(open(d + '/assets/live/calendar.json')); t2 = json.load(open(d + '/assets/live/trailers.json')); m2 = json.load(open(d + '/assets/live/manifest.json')); st = json.load(open(d + '/assets/live/status.json'))
ok(c2['generated_at'] == t2['generated_at'] == m2['generated_at'] == NOW, 'generated_at nuovo e identico nei tre file (piu recente della versione cattiva)')
ok(m2['content_hash'] == good_man['content_hash'] and c2['items'][0]['date'] != '2027-01-01', 'contenuto = versione buona (stesso content_hash), dato errato rimosso')
ok(st['result'] == 'recovery' and st['content_hash'] == m2['content_hash'] and st['last_change'] == NOW, 'status.json registra il recupero')
ok(m2.get('recovered_from') == good[:12], 'tracciato il commit di origine nel manifest')
# lo stesso pubblicatore dello scheduler accetta il risultato
sys.path.insert(0, ROOT + '/docs/tva-live-scheduler/repo/scripts')
import publish_catalog as P
store = tempfile.mkdtemp(); 
rc = P.main(['--src', d + '/assets/live', '--store', store + '/catalog', '--site', store + '/_site'] ) if os.makedirs(store + '/catalog') is None else 9
ok(rc == 0, 'il pubblicatore indipendente accetta il catalogo recuperato', rc)
# rifiuti
def refuses(sha, msg, root=d):
    try: R.recover(root, sha, now='2026-12-03T00:00:00+00:00'); ok(False, msg)
    except R.RecoverError: ok(True, msg)
refuses('zzzz', 'SHA non valido rifiutato')
refuses('0123456789abcdef', 'commit inesistente rifiutato')
sh(d, 'add', '-A'); sh(d, 'commit', '-q', '-m', 'rec'); sh(d, 'checkout', '-q', '-b', 'altro', good); open(d + '/x.txt', 'w').write('x'); sh(d, 'add', '-A'); sh(d, 'commit', '-q', '-m', 'altro'); other = sh(d, 'rev-parse', 'HEAD'); sh(d, 'checkout', '-q', 'test/tva-archives')
refuses(other, 'commit non antenato del branch rifiutato')
try: R.recover(d, good[:12], now='2026-01-01T00:00:00+00:00'); ok(False, 'generated_at non successivo rifiutato')
except R.RecoverError: ok(True, 'generated_at non successivo rifiutato')
print('\nRISULTATO: %d ok, %d falliti' % (PASS, FAIL)); sys.exit(1 if FAIL else 0)
