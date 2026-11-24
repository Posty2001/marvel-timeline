#!/usr/bin/env python3
"""TVA Live - aggiornamento automatico del CATALOGO (calendario, trailer, manifest).

Separazione netta: questo script aggiorna solo i dati in assets/live/ (e, nel workflow, li committa sul branch TEST).
NON pubblica nulla su Netlify e NON tocca main, l'app, le preferenze o i dati personali.

Riusa tools/tva_live_build.py. Genera un CANDIDATO, lo confronta col catalogo attuale e decide:
  unchanged  contenuto identico e verifica recente  -> nessuna scrittura (nessun commit)
  heartbeat  contenuto identico ma ultima verifica piu vecchia di N giorni -> aggiorna solo generated_at/status.json
  update     contenuto cambiato e superati i controlli -> scrive i file (atomico) + messaggio di commit
  rejected   fonte non ok, dati anomali o regressioni -> NIENTE scritto in assets/live, candidato in <out>/rejected, exit 1
Exit: 0 unchanged/heartbeat/update; 1 rejected; 2 errore di generazione (nessun file toccato).

Uso: TMDB_READ_TOKEN=... python3 tools/live_update.py [--root .] [--out live-update-out] [--dry-run] [--force]
         [--github-output "$GITHUB_OUTPUT"] [--today YYYY-MM-DD]
"""
import argparse, datetime as dt, json, math, os, shutil, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tva_live_build as B  # noqa: E402

FILES = ('calendar.json', 'trailers.json', 'manifest.json')
STATUS = 'status.json'
DEFAULT_GATE = {'max_removed_abs': 2, 'max_removed_frac': 0.3, 'max_new': 5, 'max_date_changes': 3, 'trailer_drop_frac': 0.5, 'trailer_drop_min': 4, 'max_new_trailers': 10, 'heartbeat_days': 7}


def jdump(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, indent=1) + '\n'


def items_of(doc):
    return sorted((doc or {}).get('items', []) or [], key=lambda i: i.get('key', ''))


def load_live(live_dir):
    d = {n[:-5]: B.load_json(os.path.join(live_dir, n)) for n in FILES}
    d['status'] = B.load_json(os.path.join(live_dir, STATUS))
    return d


def diff(cur_c, new_c, cur_t, new_t):
    cm, nm = {i['key']: i for i in cur_c}, {i['key']: i for i in new_c}
    ct, nt = {i['key']: i for i in cur_t}, {i['key']: i for i in new_t}
    ch = {'added': sorted(set(nm) - set(cm)), 'removed': sorted(set(cm) - set(nm)), 'date': [], 'confidence': [], 'state': [], 'timeline': [], 'other': [],
          'trailers_added': sorted(set(nt) - set(ct)), 'trailers_removed': sorted(set(ct) - set(nt)), 'trailers_changed': []}
    for k in sorted(set(cm) & set(nm)):
        a, b = cm[k], nm[k]
        if a.get('date') != b.get('date'): ch['date'].append((k, a.get('date'), b.get('date')))
        if a.get('confidence') != b.get('confidence'): ch['confidence'].append((k, a.get('confidence'), b.get('confidence')))
        if a.get('state') != b.get('state'): ch['state'].append((k, a.get('state'), b.get('state')))
        if a.get('timelineId') != b.get('timelineId'): ch['timeline'].append((k, a.get('timelineId'), b.get('timelineId')))
        if jdump(a) != jdump(b) and not any(k == x[0] for g in ('date', 'confidence', 'state', 'timeline') for x in ch[g]): ch['other'].append(k)
    ch['trailers_changed'] = [k for k in set(ct) & set(nt) if jdump(ct[k]) != jdump(nt[k])]
    return ch


def evaluate(cand, cur, cfg, today, force=False, gate=None):
    """Ritorna dict(result, reasons, blocking, warnings, changes). Nessun I/O."""
    g = dict(DEFAULT_GATE); g.update((cfg or {}).get('update_gate') or {}); g.update(gate or {})
    cal, trl, man = cand['calendar'], cand['trailers'], cand['manifest']
    reasons, anomalies, warns = [], [], []                 # reasons = bloccanti non superabili; anomalies = superabili con force
    src = man.get('sources', {})
    ts = (src.get('tmdb') or {}).get('status')
    if ts != 'ok': reasons.append('TMDB non ok (stato: %s): il catalogo valido resta invariato' % ts)
    ys = (src.get('youtube') or {}).get('status')
    if ys != 'ok': warns.append('YouTube non ok (stato: %s): trailer validi precedenti mantenuti, calendario aggiornato' % ys)
    try:
        B.validate(cal, trl, man, cfg)
    except Exception as e:                                  # noqa: BLE001
        reasons.append('Validazione schema/sicurezza fallita: %s' % B.scrub(e))
    ci, ti = items_of(cal), items_of(trl)
    keys = [i['key'] for i in ci]
    if len(keys) != len(set(keys)): reasons.append('Chiavi duplicate nel calendario')
    tk = [i['key'] for i in ti]
    if len(tk) != len(set(tk)): reasons.append('Chiavi duplicate nei trailer')
    for i in ci:
        for s in (i.get('sources') or []):
            if not str(s.get('url', '')).startswith('https://'): reasons.append('Link non https in %s' % i['key'])
    for t in ti:
        if not str(t.get('url', '')).startswith('https://www.youtube.com/watch?v='): reasons.append('Link trailer non valido in %s' % t['key'])
    cur_ok = bool(cur.get('calendar') and cur.get('manifest') and not (cur['manifest'] or {}).get('seed'))
    cc, ct = items_of(cur.get('calendar')), items_of(cur.get('trailers'))
    ch = diff(cc, ci, ct, ti) if cur_ok else {k: [] for k in ('added', 'removed', 'date', 'confidence', 'state', 'timeline', 'other', 'trailers_added', 'trailers_removed', 'trailers_changed')}
    if cur_ok:
        if cc and not ci: anomalies.append('Il nuovo calendario e vuoto (prima: %d voci)' % len(cc))
        unexpected = [k for k in ch['removed'] if not (next(i for i in cc if i['key'] == k).get('date') or '9999') < today]
        cap = max(g['max_removed_abs'], math.ceil(g['max_removed_frac'] * len(cc)))
        if len(unexpected) > cap: anomalies.append('Rimosse %d voci non ancora uscite (limite %d): %s' % (len(unexpected), cap, ', '.join(unexpected[:5])))
        if len(ch['added']) > g['max_new']: anomalies.append('Troppe nuove voci in un solo aggiornamento: %d (limite %d)' % (len(ch['added']), g['max_new']))
        if len(ch['date']) > g['max_date_changes']: anomalies.append('Troppi cambi data in un solo aggiornamento: %d (limite %d)' % (len(ch['date']), g['max_date_changes']))
        for k, a, b in ch['timeline']:
            if a and not b: anomalies.append('Perso il collegamento Timeline di %s (%s -> nessuno)' % (k, a))
        for k, a, b in ch['confidence']:
            if a == 'confirmed' and b != 'confirmed': anomalies.append('Declassato da Confermato: %s (la fonte ufficiale potrebbe non essere piu nel feed)' % k)
        if len(ct) >= g['trailer_drop_min'] and len(ti) < (1 - g['trailer_drop_frac']) * len(ct): anomalies.append('Trailer scesi da %d a %d' % (len(ct), len(ti)))
        if len(ch['trailers_added']) > g['max_new_trailers']: anomalies.append('Troppi nuovi trailer: %d' % len(ch['trailers_added']))
    blocking = list(reasons)
    if anomalies and not force: blocking += anomalies
    elif anomalies: warns += ['(forzato) ' + a for a in anomalies]
    content_changed = (not cur_ok) or jdump(ci) != jdump(cc) or jdump(ti) != jdump(ct)
    st = cur.get('status') or {}
    last = (st.get('last_check') or ((cur.get('manifest') or {}).get('generated_at')) or '1970-01-01')[:10]
    try: age = (dt.date.fromisoformat(today) - dt.date.fromisoformat(last)).days
    except ValueError: age = 10 ** 6
    if blocking: result = 'rejected'
    elif content_changed: result = 'update'
    elif age >= g['heartbeat_days'] or not st: result = 'heartbeat'
    else: result = 'unchanged'
    return {'result': result, 'blocking': blocking, 'warnings': warns, 'changes': ch, 'age_days': age, 'content_changed': content_changed}


def carry_trailers(cand, cur):
    """Se YouTube non e ok (errore o canale non verificato) i trailer del catalogo valido restano; il resto del candidato e valido (TMDB ok)."""
    ys = (cand['manifest'].get('sources', {}).get('youtube') or {}).get('status')
    if ys == 'ok': return cand
    keep = items_of(cur.get('trailers')) if cur.get('trailers') else []
    cand['trailers'] = dict(cand['trailers'], items=keep)
    cm = {i['key']: i for i in items_of(cur.get('calendar'))}
    items = cand['calendar']['items']
    for n, i in enumerate(items):          # senza il feed ufficiale le conferme precedenti (stessa data) non vengono declassate
        o = cm.get(i['key'])
        if o and o.get('confidence') == 'confirmed' and i.get('confidence') != 'confirmed' and o.get('date') == i.get('date'): items[n] = o
        elif o and o.get('date') == i.get('date') and o.get('confidence') == i.get('confidence') and o.get('officialDates') and not i.get('officialDates'):
            items[n] = dict(i, officialDates=o['officialDates'], reason=o.get('reason') or i.get('reason'), sources=o.get('sources') or i.get('sources'))   # senza il feed le date ufficiali per mercato gia note non spariscono
    m = cand['manifest']; m['sources']['youtube'] = dict(m['sources'].get('youtube') or {}, status='stale', count=len(keep))
    m['counts']['trailers'] = len(keep)
    m['counts']['trailers_by_category'] = {str(c): sum(1 for t in keep if t.get('category') == c) for c in B.CATEGORIES + (None,)}
    m['content_hash'] = B.hashlib.sha256((B.canon(cand['calendar']['items']) + B.canon(keep)).encode()).hexdigest()[:16]
    return cand


def commit_message(res, cand):
    c, ch = res['result'], res['changes']
    if c == 'heartbeat': return 'TVA Live: verifica periodica riuscita (catalogo invariato)\n\nSolo generated_at e status.json. Nessuna modifica ai contenuti.\n'
    parts = []
    if ch['added']: parts.append('+%d uscite' % len(ch['added']))
    if ch['removed']: parts.append('-%d uscite' % len(ch['removed']))
    if ch['date']: parts.append('%d date cambiate' % len(ch['date']))
    if ch['confidence']: parts.append('%d affidabilita' % len(ch['confidence']))
    if ch['trailers_added']: parts.append('+%d trailer' % len(ch['trailers_added']))
    if ch['trailers_removed']: parts.append('-%d trailer' % len(ch['trailers_removed']))
    if not parts: parts.append('aggiornamento dati')
    L = ['TVA Live: aggiornamento catalogo (%s)' % ', '.join(parts), '']
    L += ['- nuova: %s' % k for k in ch['added']] + ['- rimossa: %s' % k for k in ch['removed']]
    L += ['- data %s: %s -> %s' % x for x in ch['date']] + ['- affidabilita %s: %s -> %s' % x for x in ch['confidence']] + ['- stato %s: %s -> %s' % x for x in ch['state']]
    L += ['- timeline %s: %s -> %s' % x for x in ch['timeline']] + ['- modificata: %s' % k for k in ch['other']]
    L += ['- trailer nuovo: %s' % k for k in ch['trailers_added']] + ['- trailer rimosso: %s' % k for k in ch['trailers_removed']]
    L += ['', 'Hash contenuto: %s' % cand['manifest'].get('content_hash')]
    return '\n'.join(L) + '\n'


def summary_md(res, cand, dry):
    r, ch = res, res['changes']
    L = ['## TVA Live - aggiornamento catalogo', '', '**Esito: %s**%s' % (r['result'].upper(), ' (prova a secco: nulla scritto)' if dry else ''), '']
    if r['blocking']: L += ['### Motivi del blocco (il catalogo valido resta invariato)'] + ['- ' + b for b in r['blocking']] + ['']
    if r['warnings']: L += ['### Avvisi'] + ['- ' + w for w in r['warnings']] + ['']
    L += ['### Modifiche', '- nuove: %s' % (', '.join(ch['added']) or '-'), '- rimosse: %s' % (', '.join(ch['removed']) or '-'),
          '- date: %s' % ('; '.join('%s %s->%s' % x for x in ch['date']) or '-'), '- affidabilita: %s' % ('; '.join('%s %s->%s' % x for x in ch['confidence']) or '-'),
          '- altre: %s' % (', '.join(ch['other']) or '-'), '- trailer: +%d / -%d' % (len(ch['trailers_added']), len(ch['trailers_removed'])), '',
          '### Fonti', json.dumps({k: v.get('status') for k, v in cand['manifest'].get('sources', {}).items()}), '',
          'Ultima verifica precedente: %s giorni fa. Questa operazione aggiorna solo i dati nel repository; la pubblicazione su Netlify e separata.' % r['age_days']]
    return '\n'.join(L) + '\n'


def write_atomic(live_dir, files):
    """Scrive tutti i file o nessuno: temporanei nello stesso volume, poi replace; in caso di errore ripristina."""
    os.makedirs(live_dir, exist_ok=True)
    tmp, backup = {}, {}
    try:
        for name, text in files.items():
            t = os.path.join(live_dir, '.' + name + '.tmp'); open(t, 'w', encoding='utf-8').write(text); tmp[name] = t
        for name in files:
            p = os.path.join(live_dir, name)
            backup[name] = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        for name in files: os.replace(tmp[name], os.path.join(live_dir, name))
    except Exception:
        for name, old in backup.items():
            p = os.path.join(live_dir, name)
            if old is None:
                if os.path.exists(p): os.remove(p)
            else: open(p, 'w', encoding='utf-8').write(old)
        raise
    finally:
        for t in tmp.values():
            if os.path.exists(t): os.remove(t)


def main(argv=None, fetch=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.dirname(HERE))
    ap.add_argument('--out', default='live-update-out')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--force', action='store_true', help='supera SOLO le soglie anti-anomalia, mai fonte/schema/sicurezza')
    ap.add_argument('--github-output', default=None)
    ap.add_argument('--today', default=None)
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root); live_dir = os.path.join(root, 'assets/live')
    today = a.today or dt.datetime.now(dt.timezone.utc).date().isoformat()
    cfg = B.load_json(os.path.join(root, 'tools/live/config.json'))
    cur = load_live(live_dir)
    try:
        cal, trl, man, excl, log = B.run(types.SimpleNamespace(today=a.today, prev=live_dir), fetch=fetch or B.http, root=root)
    except Exception as e:                                  # noqa: BLE001 - nessun file toccato
        print('Generazione fallita, nessun file toccato: ' + B.scrub(e), file=sys.stderr)
        return 2
    cand = {'calendar': cal, 'trailers': trl, 'manifest': man}
    cand = carry_trailers(cand, cur); cal, trl, man = cand['calendar'], cand['trailers'], cand['manifest']
    res = evaluate(cand, cur, cfg, today, force=a.force)
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, 'SUMMARY.md'), 'w', encoding='utf-8').write(B.scrub(summary_md(res, cand, a.dry_run)))
    cand_dir = os.path.join(a.out, 'rejected' if res['result'] == 'rejected' else 'candidate')
    B.write_all(cand_dir, cal, trl, man, excl, log)
    if res['result'] in ('update', 'heartbeat'):
        open(os.path.join(a.out, 'COMMIT_MSG.txt'), 'w', encoding='utf-8').write(B.scrub(commit_message(res, cand)))
        if not a.dry_run:
            now = man['generated_at']
            st = {'schema': 1, 'last_check': now, 'last_change': now if res['content_changed'] else ((cur.get('status') or {}).get('last_change') or now), 'content_hash': man['content_hash'], 'result': res['result']}
            write_atomic(live_dir, {'calendar.json': B.scrub(B.canon(cal)), 'trailers.json': B.scrub(B.canon(trl)), 'manifest.json': B.scrub(B.canon(man)), STATUS: jdump(st)})
    print('Esito: %s%s' % (res['result'], ' | ' + ' | '.join(res['blocking']) if res['blocking'] else ''))
    # RESULT.json: esito leggibile da macchina (lo scheduler lo confronta con il branch). Solo campi sintetici, gia ripuliti.
    rj = {'schema': 1, 'result': res['result'], 'dry_run': bool(a.dry_run), 'forced': bool(a.force), 'content_changed': bool(res['content_changed']),
          'generated_at': man.get('generated_at'), 'content_hash': man.get('content_hash'), 'blocking': res['blocking'], 'warnings': res['warnings']}
    open(os.path.join(a.out, 'RESULT.json'), 'w', encoding='utf-8').write(B.scrub(json.dumps(rj, ensure_ascii=False, indent=2)) + '\n')
    if a.github_output:
        with open(a.github_output, 'a', encoding='utf-8') as f: f.write('result=%s\n' % res['result'])
    return 1 if res['result'] == 'rejected' else 0


if __name__ == '__main__':
    sys.exit(main())
