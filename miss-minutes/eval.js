/* Miss Minutes 2.0 - fase C: esecuzione guidata del set di valutazione sulle risposte REALI del gateway/Gemini.
   Nessuna logica di risposta qui: solo orchestrazione (conversazioni, ritmo compatibile con le quote del gateway, raccolta metadati). */
(function (root) {
  'use strict';
  var GAP = 11500;   // ms minimi tra due richieste online (gateway: 6/min per IP)
  function sleep(ms, sig) { return new Promise(function (res) { var t = setTimeout(res, ms); if (sig) sig.addEventListener('abort', function () { clearTimeout(t); res(); }); }); }
  function pick(qs, o) {
    o = o || {}; var cats = o.cats && o.cats.length ? o.cats : null, lim = o.max || 0, out = [];
    qs.forEach(function (x) { if (!cats || cats.indexOf(x.cat) >= 0) out.push(x); });
    // una catena di seguiti resta intera: se manca l'antecedente lo si aggiunge
    var ids = {}; out.forEach(function (x) { ids[x.id] = 1; });
    qs.forEach(function (x) { if (ids[x.id]) { var p = x.dopo; while (p && !ids[p]) { ids[p] = 1; p = (qs.filter(function (y) { return y.id === p; })[0] || {}).dopo; } } });
    out = qs.filter(function (x) { return ids[x.id]; });
    return lim ? out.slice(0, lim) : out;
  }
  // hooks: { newChat(), ask(q) -> Promise, last() -> {text,srcs,vf,tag,flair,refs}|null, diag() -> object|null }
  async function run(hooks, qs, o, progress, sig) {
    o = o || {}; var res = [], lastStart = 0, prevId = null, quota = false;
    for (var i = 0; i < qs.length; i++) {
      if (sig && sig.aborted) break;
      var x = qs[i];
      if (!x.dopo || x.dopo !== prevId) hooks.newChat();
      var wait = Math.max(0, (o.gap == null ? GAP : o.gap) - (Date.now() - lastStart)); if (wait) await sleep(wait, sig);
      if (sig && sig.aborted) break;
      var rec = null;
      for (var att = 0; att < 2 && !rec; att++) {
        lastStart = Date.now(); var t0 = lastStart, before = hooks.count();
        try { await hooks.ask(x.q); } catch (e) { }
        var m = hooks.last(), d = hooks.diag() || {};
        var got = hooks.count() > before + 1 && m && m.text;   // domanda + risposta aggiunte
        if (got) rec = { id: x.id, q: x.q, dopo: x.dopo || null, cat: x.cat, ok: true, ms: Date.now() - t0, text: m.text, tag: m.tag || '', online: /^online/.test(m.tag || ''), vf: m.vf || null, srcs: (m.srcs || []).map(function (s) { return { label: s.label, url: s.url, classe: s.classe }; }), flair: m.flair || '', ttfb: d.ttfb || 0, attempts: d.attempts || 0, stream: d.stream || '', fatti: d.fatti || 0, fonti: d.fonti || 0, lk: d.lk || null, verifica: d.verifica || null };
        else {
          var code = d.code || 'sconosciuto';
          if ((code === 'quota' || code === 'provider-quota') ) { quota = true; rec = { id: x.id, q: x.q, dopo: x.dopo || null, cat: x.cat, ok: false, code: code, ms: Date.now() - t0 }; }
          else if (att === 0 && /rate|blocked|busy|timeout|network|provider|empty/.test(code)) { if (progress) progress({ i: i, n: qs.length, id: x.id, nota: 'riprovo tra 65 s (' + code + ')' }); await sleep(65000, sig); if (sig && sig.aborted) break; }
          else rec = { id: x.id, q: x.q, dopo: x.dopo || null, cat: x.cat, ok: false, code: code, ms: Date.now() - t0 };
        }
      }
      if (!rec) break;
      res.push(rec); prevId = x.id; if (progress) progress({ i: i + 1, n: qs.length, id: x.id, rec: rec });
      if (quota) break;
    }
    return { versione: 1, avvio: o.avvio || new Date().toISOString(), fine: new Date().toISOString(), quota: quota, risultati: res };
  }
  root.MMEval = { run: run, pick: pick, GAP: GAP };
})(typeof window !== 'undefined' ? window : globalThis);
