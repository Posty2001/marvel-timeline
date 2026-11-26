/* Miss Minutes 2.0 - caricamento dell'archivio TMDB: pacchetto incluso nella PWA -> copia locale verificata -> aggiornamento remoto (OPZIONALE, spento di default).
   L'aggiornamento remoto e' attivo SOLO se MISS_MINUTES_CONFIG.archivio e' un URL https (vuoto = disattivato, nessuna richiesta di rete).
   Nessun dato personale viene inviato: solo GET di due file pubblici. Qualsiasi errore = si resta sulla versione verificata gia' disponibile (fail-open). */
(function (root) {
  'use strict';
  var KEY = 'marvel-ultimate-timeline-miss-minutes-archivio-v1', STAMP = KEY + '-ctl', EVERY = 12 * 3600 * 1000, MAXB = 1500000, TIMEOUT = 4500;
  function hex(buf) { var a = new Uint8Array(buf), s = ''; for (var i = 0; i < a.length; i++) s += ('0' + a[i].toString(16)).slice(-2); return s; }
  async function sha256(text) { var b = new TextEncoder().encode(text); return hex(await root.crypto.subtle.digest('SHA-256', b)); }
  var ISO = /^\d{4}-\d{2}-\d{2}$/;
  // Regole di validazione (le stesse per il file incluso, la copia locale e il remoto). ref = archivio di riferimento gia' valido.
  function validate(a, ref) {
    var e = [];
    if (!a || typeof a !== 'object') return ['non e\' un oggetto'];
    if (a.versione !== 1 && a.versione !== 2) e.push('versione schema non compatibile');
    if (!a.generato || !ISO.test(String(a.generato).slice(0, 10))) e.push('data di generazione assente');
    var v = a.voci; if (!v || typeof v !== 'object' || Array.isArray(v)) return e.concat(['voci assenti']);
    var ids = Object.keys(v); if (ids.length < 50) e.push('troppe poche voci (' + ids.length + ')');
    var bad = 0;
    ids.forEach(function (k) {
      var x = v[k]; if (!x || typeof x.titolo !== 'string' || !x.tmdb || !x.tmdb.id || !/^(movie|tv)$/.test(x.tmdb.t)) { bad++; return; }
      (x.date || []).forEach(function (d) { if (!d || !ISO.test(String(d.data || ''))) bad++; });
      if (x.sinossi_it != null && typeof x.sinossi_it !== 'string') bad++;
    });
    if (bad) e.push(bad + ' campi/voci malformati');
    if (ref && ref.voci) {
      if (ref.versione && a.versione < ref.versione) e.push('schema piu\' vecchio della versione verificata');
      var rk = Object.keys(ref.voci), keep = rk.filter(function (k) { return v[k]; }).length;
      if (rk.length && keep < 0.9 * rk.length) e.push('perde troppe voci rispetto alla versione verificata (' + keep + '/' + rk.length + ')');
      var lost = rk.filter(function (k) { return v[k] && ref.voci[k].sinossi_it && !v[k].sinossi_it; }).length;
      if (lost > 0.1 * rk.length) e.push('troppe sinossi perse (' + lost + ')');
      if (ref.generato && String(a.generato) < String(ref.generato)) e.push('piu\' vecchio della versione verificata');
    }
    return e;
  }
  function ls() { try { return root.localStorage; } catch (e) { return null; } }
  function readLocal() { var s = ls(); if (!s) return null; try { var o = JSON.parse(s.getItem(KEY) || 'null'); return o && o.archivio ? o : null; } catch (e) { return null; } }
  function writeLocal(arch, sha) { var s = ls(); if (!s) return false; try { s.setItem(KEY, JSON.stringify({ sha: sha, salvato: new Date().toISOString(), archivio: arch })); return true; } catch (e) { return false; } }
  function dropLocal() { var s = ls(); if (s) try { s.removeItem(KEY); } catch (e) { } }
  async function getJSON(f, url, ms) {
    var ctl = typeof AbortController !== 'undefined' ? new AbortController() : null, t = setTimeout(function () { if (ctl) ctl.abort(); }, ms || TIMEOUT);
    try { var r = await f(url, { cache: 'no-cache', credentials: 'omit', signal: ctl ? ctl.signal : undefined }); if (!r.ok) throw new Error('HTTP ' + r.status); var tx = await r.text(); if (tx.length > MAXB) throw new Error('troppo grande'); return tx; } finally { clearTimeout(t); }
  }
  /* load(opts): opts.bundle = archivio incluso (gia' letto), opts.base = URL base remoto o '', opts.fetch, opts.now, opts.force
     Ritorna { archivio, origine: 'incluso'|'copia-locale'|'remoto', note: [...] } */
  async function load(o) {
    o = o || {}; var f = o.fetch || (root.fetch && root.fetch.bind(root)), notes = [], bundle = o.bundle || null, bOk = bundle && !validate(bundle).length;
    var best = bOk ? { archivio: bundle, origine: 'incluso' } : null, ref = best ? best.archivio : null;
    var loc = readLocal();
    if (loc) {
      var p = validate(loc.archivio, ref);   // l'impronta SHA-256 e' verificata al download, sul testo originale
      if (!p.length) { if (!best || String(loc.archivio.generato) > String(best.archivio.generato)) { best = { archivio: loc.archivio, origine: 'copia-locale' }; ref = loc.archivio; } }
      else { dropLocal(); notes.push('copia locale scartata: ' + p.join('; ')); }
    }
    var base = String(o.base || '').replace(/\/+$/, ''), now = o.now || Date.now(), s = ls(), last = 0;
    if (s) try { last = +s.getItem(STAMP) || 0; } catch (e) { }
    if (/^https:\/\//.test(base) && f && (o.force || now - last > EVERY)) {
      try {
        if (s) try { s.setItem(STAMP, String(now)); } catch (e) { }
        var ptr = JSON.parse(await getJSON(f, base + '/pointer.json'));
        if (!ptr || ptr.versione < 1 || !/^[0-9a-f]{64}$/.test(ptr.sha256 || '') || !/^[A-Za-z0-9._-]+\.json$/.test(ptr.file || '')) throw new Error('puntatore non valido');
        if (ref && String(ptr.generato) <= String(ref.generato)) notes.push('archivio gia\' aggiornato');
        else {
          var tx = await getJSON(f, base + '/' + ptr.file), h = await sha256(tx);
          if (h !== ptr.sha256) throw new Error('impronta SHA-256 diversa dal puntatore');
          var cand = JSON.parse(tx), pr = validate(cand, ref); if (pr.length) throw new Error('validazione: ' + pr.join('; '));
          best = { archivio: cand, origine: 'remoto' }; writeLocal(cand, h); notes.push('aggiornato da remoto: ' + cand.generato);
        }
      } catch (e) { notes.push('aggiornamento remoto non riuscito (' + (e && e.message || e) + '): resta ' + (best ? best.origine : 'nessun archivio')); }
    }
    return { archivio: best ? best.archivio : null, origine: best ? best.origine : 'nessuno', note: notes };
  }
  root.MMArchive = { load: load, validate: validate, sha256: sha256, KEY: KEY };
})(typeof window !== 'undefined' ? window : globalThis);
