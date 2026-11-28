#!/usr/bin/env python3
"""Censimento runtime delle personalizzazioni della Tessera (T0, solo lettura).

Carica l'app reale in un browser headless ed estrae il catalogo VIVO dalle API già
esposte (tvaCardArt, tvaTessera3, tvaEmblems, tvaRewards, tvaIdentity). Nessun
file dell'app viene modificato.

Uso:
  python3 tools/tessera_censimento.py --scrivi     # scrive docs/tessera2/censimento_runtime_T0.json
  python3 tools/tessera_censimento.py --verifica   # confronta con lo snapshot congelato (exit 1 se manca qualcosa)
"""
import functools, http.server, json, os, socket, sys, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, 'docs', 'tessera2', 'inventario_personalizzazioni_28112026.json')
OUT = os.path.join(ROOT, 'docs', 'tessera2', 'censimento_runtime_T0.json')

JS = """() => {
  const A = window.tvaCardArt, T = window.tvaTessera3, E = window.tvaEmblems, R = window.tvaRewards, I = window.tvaIdentity;
  const keys = o => Object.keys(o || {});
  return {
    avatar: A.avatars.map(a => (typeof a === 'string' ? a : a.id)),
    cornici_arte: A.frames.slice(), temi_arte: A.themes.slice(), effetti_arte: A.fx.slice(),
    font: keys(T.TYPO), sfondi: keys(T.BGS), texture: keys(T.TEXS), cornici_stile: keys(T.FRS),
    decorazioni: keys(T.DECS), effetti_stile: keys(T.FXS), icone: keys(T.ICS), layout: keys(T.LYS),
    preset: Array.isArray(T.PRESETS) ? T.PRESETS.map(p => p.id || p.k) : keys(T.PRESETS), preset_campi: T.PRESET_KEYS.slice(), preset_valori: JSON.parse(JSON.stringify(T.PRESETS)),
    ricompense_default: JSON.parse(JSON.stringify(R.defaults)), stile_default: JSON.parse(JSON.stringify(T.DEFAULTS)),
    emblemi_count: E.count, emblemi_categorie: E.cats.slice(), emblemi_nomi: E.names.slice(), emblemi_finiture: E.finishKeys.slice(),
    ricompense: R.catalog.map(r => ({ id: r.id, cat: r.cat, nome: r.nome, rar: r.rar, cond: r.cond })),
    ricompense_categorie: R.categories.slice(), rarita: keys(R.rarities),
    storageKey: R.storageKey,
    chiavi_identita: { IDK: I.IDK, STYK: I.STYK, BAKK: I.BAKK }
  };
}"""


def _server():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def handle(self):
            try: super().handle()
            except Exception: pass
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, 'http://127.0.0.1:%d/index.html' % port


def censimento():
    from playwright.sync_api import sync_playwright
    srv, url = _server()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            c = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
            pg = c.new_page(); pg.goto(url); pg.wait_for_timeout(3500)
            data = pg.evaluate(JS)
            b.close()
        return data
    finally:
        srv.shutdown()


def confronta(vivo, snap):
    """Ritorna l'elenco dei problemi: ogni elemento dello snapshot deve esistere ancora (additivo: i nuovi sono ammessi)."""
    pb = []
    for fam, v in snap.items():
        w = vivo.get(fam)
        if fam == 'ricompense':
            vm = {r['id']: r for r in (w or [])}
            for r in v:
                x = vm.get(r['id'])
                if not x: pb.append('ricompensa mancante: %s' % r['id']); continue
                for k in ('nome', 'rar', 'cat', 'cond'):
                    if x.get(k) != r.get(k): pb.append('ricompensa %s: %s cambiato (%r -> %r)' % (r['id'], k, r.get(k), x.get(k)))
        elif isinstance(v, list):
            for e in v:
                if e not in (w or []): pb.append('%s: manca %r' % (fam, e))
            if fam == 'emblemi_nomi' and w and len(w) < len(v): pb.append('emblemi_nomi: conteggio ridotto')
        elif isinstance(v, int):
            if (w or 0) < v: pb.append('%s: %s < %s' % (fam, w, v))
        elif w != v:
            pb.append('%s: %r -> %r' % (fam, v, w))
    return pb


def main():
    a = sys.argv[1:]
    vivo = censimento()
    if '--scrivi' in a:
        with open(OUT, 'w') as f: json.dump(vivo, f, ensure_ascii=False, indent=1, sort_keys=True)
        print('scritto', os.path.relpath(OUT, ROOT))
    if '--verifica' in a or not a:
        snap = json.load(open(SNAP))
        pb = confronta(vivo, snap)
        for p_ in pb: print('FAIL', p_)
        tot = {k: (len(v) if isinstance(v, list) else v) for k, v in vivo.items() if k not in ('chiavi_identita',)}
        print('conteggi vivi:', json.dumps(tot, ensure_ascii=False))
        print('OK catalogo congelato rispettato' if not pb else 'ERRORI: %d' % len(pb))
        sys.exit(1 if pb else 0)


if __name__ == '__main__':
    main()
