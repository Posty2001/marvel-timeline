/* Miss Minutes — client del gateway AI. Nessuna chiave: il dispositivo ottiene un token firmato a scadenza
   dopo una piccola proof-of-work. Nessun retry automatico. UMD: globalThis.MMGateway | module.exports. */
(function (root) {
  'use strict';
  var MSG = {
    disabled: 'L’AI online non è ancora attiva sul gateway.', origin: 'Questo indirizzo non è autorizzato dal gateway.',
    quota: 'Limite giornaliero dell’AI online raggiunto: uso solo il motore locale.', 'provider-quota': 'Il servizio AI gratuito ha raggiunto il suo limite: uso il motore locale.',
    rate: 'Troppe richieste ravvicinate: riprova tra poco.', blocked: 'Troppi tentativi non validi da questa rete: riprova più tardi.',
    auth: 'Sessione non valida: riprovo al prossimo invio.', expired: 'Sessione scaduta: riprovo al prossimo invio.', provider: 'Il servizio AI non risponde: uso il motore locale.',
    empty: 'Risposta AI vuota: uso il motore locale.', size: 'Domanda troppo lunga.', input: 'Domanda non valida.', network: 'Gateway non raggiungibile: uso il motore locale.', timeout: 'Il gateway non ha risposto in tempo: uso il motore locale.'
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

    function err(code) { return { ok: false, code: code, message: MSG[code] || MSG.provider }; }
    function timeout(ms) { if (typeof AbortSignal !== 'undefined' && AbortSignal.timeout) return AbortSignal.timeout(ms); var c = new AbortController(); setTimeout(function () { c.abort(); }, ms); return c.signal; }
    async function req(path, init) {
      try { var r = await f(endpoint + path, Object.assign({ signal: timeout(25000), credentials: 'omit', cache: 'no-store' }, init)); var j = null; try { j = await r.json(); } catch (e) {} return { status: r.status, json: j || {} }; }
      catch (e) { return { status: 0, json: {}, timeout: e && e.name === 'TimeoutError' || e && e.name === 'AbortError' }; }
    }
    async function solve(c) {
      for (var n = 0; n < 5000000; n++) {
        var h = new Uint8Array(await subtle.digest('SHA-256', enc.encode(c.salt + '.' + c.ts + '.' + n)));
        if (lz(h) >= c.bits) return String(n);
        if (n % 4000 === 3999) await new Promise(function (r) { setTimeout(r, 0); });   // lascia respirare l'interfaccia
      }
      return null;
    }
    async function ensureSession() {
      if (token && exp > now() + 60) return { ok: true };
      var ch = await req('/v1/challenge', { method: 'GET' });
      if (ch.status !== 200 || !ch.json.salt) return err(ch.status === 0 ? (ch.timeout ? 'timeout' : 'network') : (ch.json.error || 'provider'));
      var n = await solve(ch.json); if (n === null) return err('provider');
      var s = await req('/v1/session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ salt: ch.json.salt, ts: ch.json.ts, bits: ch.json.bits, sig: ch.json.sig, n: n }) });
      if (s.status !== 200 || !s.json.token) return err(s.status === 0 ? 'network' : (s.json.error || 'provider'));
      token = s.json.token; exp = s.json.exp;
      try { store && store.setItem(SK, JSON.stringify({ token: token, exp: exp })); } catch (e) {}
      return { ok: true };
    }
    async function ask(payload) {
      if (!endpoint) return err('disabled');
      var s = await ensureSession(); if (!s.ok) return s;
      var r = await req('/v1/chat', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token }, body: JSON.stringify(payload) });
      if (r.status === 200 && typeof r.json.answer === 'string') return { ok: true, answer: r.json.answer };
      if (r.status === 401) { token = null; exp = 0; try { store && store.removeItem(SK); } catch (e) {} }
      return r.status === 0 ? err(r.timeout ? 'timeout' : 'network') : err(r.json.error || 'provider');
    }
    async function health() { if (!endpoint) return { ok: false, enabled: false }; var r = await req('/v1/health', { method: 'GET' }); return { ok: r.status === 200, enabled: !!r.json.enabled }; }
    return { ask: ask, health: health, available: function () { return !!endpoint; }, forget: function () { token = null; exp = 0; try { store && store.removeItem(SK); } catch (e) {} } };
  }
  var API = { create: create, MSG: MSG };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.MMGateway = API;
})(typeof globalThis !== 'undefined' ? globalThis : this);
