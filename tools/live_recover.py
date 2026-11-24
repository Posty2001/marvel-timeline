#!/usr/bin/env python3
"""TVA Live - RECUPERO di emergenza: ripristina sul branch TEST un catalogo noto e valido preso da un commit precedente.

Perche serve: un catalogo gia pubblicato non si "ritira" fermando lo scheduler, e l app rifiuta qualunque catalogo con generated_at piu vecchio di quello che ha gia visto.
Quindi il recupero NON riporta indietro il tempo: ripubblica il CONTENUTO di una versione buona con un generated_at NUOVO (stessi dati, stesso content_hash).
Garanzie: il commit di partenza deve essere un antenato del branch; i tre file vengono rivalidati dal generatore; scrittura atomica; solo i 4 file di assets/live.
Uso: python3 tools/live_recover.py --from <sha> [--root .] [--dry-run] [--out live-recover-out] [--now ISO]"""
import argparse, datetime as dt, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tva_live_build as B       # noqa: E402
import live_update as U          # noqa: E402

SHA_RE = re.compile(r'^[0-9a-f]{7,40}$')
FILES = ('calendar', 'trailers', 'manifest')


class RecoverError(Exception):
    pass


def git(root, *a):
    p = subprocess.run(['git', '-C', root] + list(a), capture_output=True, text=True)
    if p.returncode != 0:
        raise RecoverError('git %s: %s' % (a[0], (p.stderr or p.stdout).strip()[:200]))
    return p.stdout


def recover(root, sha, now=None, dry=False, out=None):
    if not SHA_RE.match(sha or ''):
        raise RecoverError('SHA non valido')
    full = git(root, 'rev-parse', '--verify', sha + '^{commit}').strip()
    p = subprocess.run(['git', '-C', root, 'merge-base', '--is-ancestor', full, 'HEAD'])
    if p.returncode != 0:
        raise RecoverError('il commit %s non e un antenato del branch corrente: rifiutato' % sha)
    docs = {n: json.loads(git(root, 'show', '%s:assets/live/%s.json' % (full, n))) for n in FILES}
    cfg = B.load_json(os.path.join(root, 'tools/live/config.json'))
    try:
        B.validate(docs['calendar'], docs['trailers'], docs['manifest'], cfg)
    except Exception as e:      # noqa: BLE001
        raise RecoverError('la versione di partenza non supera la validazione: %s' % B.scrub(e))
    old_gen = docs['manifest']['generated_at']
    now = now or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    if dt.datetime.fromisoformat(now) <= dt.datetime.fromisoformat(old_gen):
        raise RecoverError('il nuovo generated_at non e successivo a quello di partenza')
    for n in FILES:
        docs[n]['generated_at'] = now
    docs['manifest']['recovered_from'] = full[:12]
    h = B.hashlib.sha256((B.canon(docs['calendar']['items']) + B.canon(docs['trailers']['items'])).encode()).hexdigest()[:16]
    if h != docs['manifest']['content_hash']:
        raise RecoverError('content_hash incoerente con i dati della versione di partenza')
    live_dir = os.path.join(root, 'assets/live')
    cur = U.load_live(live_dir)
    same = bool(cur.get('manifest')) and cur['manifest'].get('content_hash') == h
    st = {'schema': 1, 'last_check': now, 'last_change': now, 'content_hash': h, 'result': 'recovery'}
    res = {'schema': 1, 'result': 'recovery', 'dry_run': bool(dry), 'forced': True, 'content_changed': not same, 'generated_at': now, 'content_hash': h, 'blocking': [],
           'warnings': ['Ripristinato il contenuto del commit %s con generated_at %s' % (full[:12], now)] + (['Il contenuto era gia quello corrente: aggiornata solo la data'] if same else [])}
    if out:
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, 'RESULT.json'), 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=2) + '\n')
        open(os.path.join(out, 'COMMIT_MSG.txt'), 'w', encoding='utf-8').write('TVA Live: RECUPERO del catalogo dal commit %s\n\nContenuto della versione nota e valida (hash %s) con generated_at %s, cosi da sostituire un catalogo gia pubblicato.\n' % (full[:12], h, now))
    if not dry:
        U.write_atomic(live_dir, {'calendar.json': B.scrub(B.canon(docs['calendar'])), 'trailers.json': B.scrub(B.canon(docs['trailers'])),
                                  'manifest.json': B.scrub(B.canon(docs['manifest'])), U.STATUS: U.jdump(st)})
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='sha', required=True); ap.add_argument('--root', default=os.path.dirname(HERE))
    ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--out', default='live-recover-out'); ap.add_argument('--now', default=None)
    ap.add_argument('--github-output', default=None)
    a = ap.parse_args(argv)
    try:
        r = recover(os.path.abspath(a.root), a.sha, a.now, a.dry_run, a.out)
    except RecoverError as e:
        print('RECUPERO RIFIUTATO: %s' % e, file=sys.stderr); return 1
    print('Esito: recovery | hash %s | generated_at %s%s' % (r['content_hash'], r['generated_at'], ' (prova a secco)' if a.dry_run else ''))
    if a.github_output:
        with open(a.github_output, 'a', encoding='utf-8') as f: f.write('result=recovery\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
