/* Miss Minutes — client del gateway AI. Nessuna chiave: il dispositivo ottiene un token firmato a scadenza
   dopo una piccola proof-of-work. Nessun retry qui: un solo tentativo automatico, limitato agli errori temporanei, e' deciso dall'app (ogni tentativo passa dalle stesse quote del gateway). UMD: globalThis.MMGateway | module.exports. */
(function (root) {
  'use strict';
  var MSG = {
    disabled: 'L’AI online non è ancora attiva sul gateway.', origin: 'Questo indirizzo non è autorizzato dal gateway.',
    quota: 'Limite giornaliero dell’AI online raggiunto: uso solo il motore locale.', 'provider-quota': 'Il servizio AI gratuito ha raggiunto il suo limite: uso il motore locale.',
    rate: 'Troppe richieste ravvicinate: riprova tra poco.', blocked: 'Troppi tentativi non validi da questa rete: riprova più tardi.',
    auth: 'Sessione non valida: riprovo al prossimo invio.', expired: 'Sessione scaduta: riprovo al prossimo invio.', provider: 'Il servizio AI non risponde: uso il motore locale.',
    'provider-request': 'Google ha rifiutato la richiesta (formato non valido): uso il motore locale.', 'provider-auth': 'Google ha rifiutato la chiave AI (non valida o senza permessi): uso il motore locale.',
    'provider-model': 'Il modello AI configurato non esiste o non è disponibile: uso il motore locale.', 'provider-timeout': 'Google non ha risposto in tempo: uso il motore locale.', 'provider-network': 'Il gateway non riesce a raggiungere Google: uso il motore locale.',
    empty: 'Risposta AI vuota: uso il motore locale.', aborted: 'Attesa interrotta.', size: 'Domanda troppo lunga.', input: 'Domanda non valida.', network: 'Gateway non raggiungibile: uso il motore locale.', timeout: 'Il gateway non ha risposto in tempo: uso il motore locale.'
  };
  function lz(bytes) { var n = 0; for (var i = 0; i < bytes.length; i++) { var b = bytes[i]; if (b === 0) { n += 8; continue; } n += Math.clz32(b) - 24; break; } return n; }

  function create(o) {
    var endpoint = String(o.endpoint || '').replace(/\/+$/, '');
    var f = o.fetch || (typeof fetch === 'function' ? fetch.bind(root) : null);
    var subtle = o.subtle || (root.crypto && root.crypto.subtle);
    var store = o.storage || null, SK = o.storageKey || 'marvel-ultimate-timeline-miss-minutes-session';
    var now = o.now || function () { return Math.floor(Date.now() / 1000); };
    var token = null, exp = 0, enc = new TextEncoder();
    try { var raw = store && JSON.parse(store.getItem(SK) || 'null'); if (raw && raw.exp > now() + 60 && typeof raw.token === 'string') { token = raw.token; exp = raw.exp; } } catch (e) {}

    function err(code, stage, up, http) { var d = up ? 'HTTP ' + up.http + (up.status ? ' ' + up.status : '') + (up.message ? ': ' + up.message : '') : (http ? 'HTTP ' + http : ''); return { ok: false, code: code, stage: stage || 'chat', http: http || (up && up.http) || 0, detail: d, message: MSG[code] || MSG.provider }; }
    // segnale unico: scadenza + eventuale interruzione dell'utente (AbortSignal.any non e' disponibile su tutti i Safari)
    function timeout(ms, user) {
      var c = new AbortController(), t = setTimeout(function () { c.__timeout = true; c.abort(); }, ms);
      if (user) { if (user.aborted) c.abort(); else user.addEventListener('abort', function () { c.abort(); }, { once: true }); }
      c.signal.addEventListener('abort', function () { clearTimeout(t); }, { once: true });
      return { signal: c.signal, timedOut: function () { return !!c.__timeout; } };
    }
    async function req(path, init, user) {
      var tm = timeout(25000, user);
      try { var r = await f(endpoint + path, Object.assign({ signal: tm.signal, credentials: 'omit', cache: 'no-store' }, init)); var j = null; try { j = await r.json(); } catch (e) {} return { status: r.status, json: j || {} }; }
      catch (e) { var abortedByUser = !!(user && user.aborted); return { status: 0, json: {}, aborted: abortedByUser, timeout: !abortedByUser && (tm.timedOut() || (e && (e.name === 'TimeoutError' || e.name === 'AbortError'))) }; }
    }
    async function solve(c) {
      for (var n = 0; n < 5000000; n++) {
        var h = new Uint8Array(await subtle.digest('SHA-256', enc.encode(c.salt + '.' + c.ts + '.' + n)));
        if (lz(h) >= c.bits) return String(n);
        if (n % 4000 === 3999) await new Promise(function (r) { setTimeout(r, 0); });   // lascia respirare l'interfaccia
      }
      return null;
    }
    async function ensureSession(user) {
      if (token && exp > now() + 60) return { ok: true };
      var ch = await req('/v1/challenge', { method: 'GET' }, user);
      if (ch.aborted) return err('aborted', 'sfida');
      if (ch.status !== 200 || !ch.json.salt) return err(ch.status === 0 ? (ch.timeout ? 'timeout' : 'network') : (ch.json.error || 'provider'), 'sfida', null, ch.status);
      var n = await solve(ch.json); if (n === null) return err('provider', 'sfida');
      if (user && user.aborted) return err('aborted', 'sfida');
      var s = await req('/v1/session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ salt: ch.json.salt, ts: ch.json.ts, bits: ch.json.bits, sig: ch.json.sig, n: n }) }, user);
      if (s.aborted) return err('aborted', 'sessione');
      if (s.status !== 200 || !s.json.token) return err(s.status === 0 ? 'network' : (s.json.error || 'provider'), 'sessione', null, s.status);
      token = s.json.token; exp = s.json.exp;
      try { store && store.setItem(SK, JSON.stringify({ token: token, exp: exp })); } catch (e) {}
      return { ok: true };
    }
    async function ask(payload, opts) {
      if (!endpoint) return err('disabled');
      var user = opts && opts.signal || null, t0 = Date.now();
      var s = await ensureSession(user); if (!s.ok) { s.ms = Date.now() - t0; return s; }
      var r = await req('/v1/chat', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token }, body: JSON.stringify(payload) }, user);
      if (r.aborted) { var ab = err('aborted', 'chat'); ab.ms = Date.now() - t0; return ab; }
      if (r.status === 200 && typeof r.json.answer === 'string') return { ok: true, answer: r.json.answer, ms: Date.now() - t0 };
      if (r.status === 401) { token = null; exp = 0; try { store && store.removeItem(SK); } catch (e) {} }
      var e2 = r.status === 0 ? err(r.timeout ? 'timeout' : 'network', 'chat') : err(r.json.error || 'provider', r.json.error && /^provider/.test(r.json.error) ? 'gemini' : 'gateway', r.json.upstream, r.status); e2.ms = Date.now() - t0; return e2;
    }
    // Streaming reale (SSE): onDelta(testoCumulativo) a ogni frammento. Se il gateway non supporta lo streaming (risposta JSON) o il
    // browser non espone lo stream, ricade sulla risposta intera (streamed:false). Un'interruzione a meta' restituisce il testo gia' ricevuto in `partial`.
    async function askStream(payload, opts) {
      if (!endpoint) return err('disabled');
      opts = opts || {}; var user = opts.signal || null, onDelta = typeof opts.onDelta === 'function' ? opts.onDelta : function () {}, t0 = Date.now();
      var s = await ensureSession(user); if (!s.ok) { s.ms = Date.now() - t0; return s; }
      var c = new AbortController(), idle = null, timedOut = false, first = true;
      function arm(ms) { clearTimeout(idle); idle = setTimeout(function () { timedOut = true; c.abort(); }, ms); }
      if (user) { if (user.aborted) c.abort(); else user.addEventListener('abort', function () { c.abort(); }, { once: true }); }
      arm(25000);
      var r, acc = '', ttfb = 0;
      try {
        r = await f(endpoint + '/v1/chat', { method: 'POST', signal: c.signal, credentials: 'omit', cache: 'no-store', headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream', Authorization: 'Bearer ' + token }, body: JSON.stringify(Object.assign({}, payload, { stream: true })) });
      } catch (e) { clearTimeout(idle); var ab = !!(user && user.aborted); var x = ab ? err('aborted', 'chat') : err(timedOut ? 'timeout' : 'network', 'chat'); x.ms = Date.now() - t0; return x; }
      var ct = String(r.headers && r.headers.get && r.headers.get('content-type') || '');
      if (r.status !== 200 || ct.indexOf('text/event-stream') < 0) {
        clearTimeout(idle); var j = null; try { j = await r.json(); } catch (e) {}
        j = j || {};
        if (r.status === 200 && typeof j.answer === 'string') return { ok: true, answer: j.answer, ms: Date.now() - t0, streamed: false };
        if (r.status === 401) { token = null; exp = 0; try { store && store.removeItem(SK); } catch (e) {} }
        var e2 = err(j.error || 'provider', j.error && /^provider/.test(j.error) ? 'gemini' : 'gateway', j.upstream, r.status); e2.ms = Date.now() - t0; return e2;
      }
      if (!r.body || !r.body.getReader || typeof TextDecoder === 'undefined') {   // browser senza stream: testo intero
        var all = ''; try { all = await r.text(); } catch (e) {} clearTimeout(idle);
        var parsed = parseSSE(all + '\n\n'); var txt = parsed.text; if (parsed.err) { var e3 = err(parsed.err, 'gemini'); e3.partial = txt; e3.ms = Date.now() - t0; return e3; }
        return txt ? { ok: true, answer: txt, ms: Date.now() - t0, streamed: false } : err('empty', 'gemini');
      }
      var rd = r.body.getReader(), dec = new TextDecoder(), buf = '', done = false, serr = '';
      try {
        for (;;) {
          var chunk = await rd.read(); if (chunk.done) break; arm(20000);
          buf += dec.decode(chunk.value, { stream: true }).replace(/\r\n/g, '\n'); var i;
          while ((i = buf.indexOf('\n\n')) >= 0) {
            var ev = buf.slice(0, i); buf = buf.slice(i + 2); var o = parseEvent(ev); if (!o) continue;
            if (typeof o.t === 'string' && o.t) { if (first) { first = false; ttfb = Date.now() - t0; } acc += o.t; try { onDelta(acc, ttfb); } catch (e) {} }
            else if (o.done) done = true; else if (o.e) serr = String(o.e).slice(0, 40);
          }
        }
      } catch (e) {
        clearTimeout(idle); try { rd.cancel().catch(function () {}); } catch (x) {}
        if (user && user.aborted) { var a2 = err('aborted', 'chat'); a2.partial = acc; a2.ms = Date.now() - t0; return a2; }
        var e4 = err(timedOut ? 'timeout' : 'provider-network', 'chat'); e4.partial = acc; e4.ms = Date.now() - t0; return e4;
      }
      clearTimeout(idle);
      if (serr) { var e5 = err(serr, 'gemini'); e5.partial = acc; e5.ms = Date.now() - t0; return e5; }
      if (!acc) { var e6 = err('empty', 'gemini'); e6.ms = Date.now() - t0; return e6; }
      if (!done) { var e7 = err('provider-network', 'chat'); e7.partial = acc; e7.ms = Date.now() - t0; return e7; }
      return { ok: true, answer: acc, ms: Date.now() - t0, streamed: true, ttfb: ttfb };
    }
    function parseEvent(ev) { var l = ev.split('\n').filter(function (x) { return x.indexOf('data:') === 0; })[0]; if (!l) return null; try { return JSON.parse(l.slice(5)); } catch (e) { return null; } }
    function parseSSE(t) { var text = '', er = '', p = t.replace(/\r\n/g, '\n').split('\n\n'); p.forEach(function (x) { var o = parseEvent(x); if (!o) return; if (typeof o.t === 'string') text += o.t; else if (o.e) er = String(o.e).slice(0, 40); }); return { text: text, err: er }; }
    // errori temporanei per cui vale un solo nuovo tentativo (sovraccarico/rete); mai quote, auth, modello, richiesta, timeout
    function retriable(e) { return !!e && !e.ok && ((e.code === 'provider' && (e.http === 500 || e.http === 502 || e.http === 503 || e.http === 504 || e.http === 529)) || e.code === 'provider-network'); }
    async function health() { if (!endpoint) return { ok: false, enabled: false }; var r = await req('/v1/health', { method: 'GET' }); return { ok: r.status === 200, enabled: !!r.json.enabled, missing: Array.isArray(r.json.missing) ? r.json.missing.slice(0, 6).map(String) : [] }; }
    return { ask: ask, askStream: askStream, health: health, retriable: retriable, available: function () { return !!endpoint; }, forget: function () { token = null; exp = 0; try { store && store.removeItem(SK); } catch (e) {} } };
  }
  var API = { create: create, MSG: MSG };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.MMGateway = API;
})(typeof globalThis !== 'undefined' ? globalThis : this);
