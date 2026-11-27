/* Miss Minutes 2.0 - fase C: esecuzione guidata del set di valutazione sulle risposte REALI del gateway/Gemini.
   Nessuna logica di risposta qui: solo orchestrazione (conversazioni, ritmo compatibile con le quote del gateway, raccolta metadati). */
(function (root) {
  'use strict';
  var GAP = 11500;   // ms minimi tra due richieste online (gateway: 6/min per IP)
  function sleep(ms, sig) { return new Promise(function (res) { var t = setTimeout(res, ms); if (sig) sig.addEventListener('abort', function () { clearTimeout(t); res(); }); }); }
  function pick(qs, o) {
    o = o || {}; var cats = o.cats && o.cats.length ? o.cats : null, lim = o.max || 0, out = [];
    qs.forEach(function (x) { if ((!cats || cats.indexOf(x.cat) >= 0) && (!o.set || (x.set || 'S') === o.set)) out.push(x); });
    // una catena di seguiti resta intera: se manca l'antecedente lo si aggiunge
    var ids = {}; out.forEach(function (x) { ids[x.id] = 1; });
    qs.forEach(function (x) { if (ids[x.id]) { var p = x.dopo; while (p && !ids[p]) { ids[p] = 1; p = (qs.filter(function (y) { return y.id === p; })[0] || {}).dopo; } } });
    out = qs.filter(function (x) { return ids[x.id]; });
    return lim ? out.slice(0, lim) : out;
  }
  // hooks: { newChat(), ask(q) -> Promise, last() -> {text,srcs,vf,tag,flair,refs}|null, diag() -> object|null }
  /* Esecuzione riprendibile: o.prev = risultati gia' completati (non si ripetono); a quota esaurita la serie si SOSPENDE (nessun tentativo inutile),
     il record fallito non viene salvato come «fatto» e o.checkpoint riceve lo stato dopo ogni risposta. */
  async function run(hooks, qs, o, progress, sig) {
    o = o || {}; var res = [], lastStart = 0, prevId = null, quota = false, qinfo = null, chatOpen = false, byId = {}, done = {};
    (o.prev || []).forEach(function (r) { if (r && r.ok && r.id) { done[r.id] = r; } });
    qs.forEach(function (x) { byId[x.id] = x; });
    function snap(sus) { var all = res.slice(); return { versione: 1, set: o.set || '', avvio: o.avvio || new Date().toISOString(), fine: new Date().toISOString(), quota: quota, sospesa: sus ? (qinfo || true) : null, risultati: all }; }
    function chainOf(x) { var ch = [], p = x.dopo, g = 0; while (p && g++ < 20) { ch.unshift(p); p = (byId[p] || {}).dopo; } return ch; }
    for (var i = 0; i < qs.length; i++) {
      if (sig && sig.aborted) break;
      var x = qs[i];
      if (done[x.id]) { res.push(done[x.id]); prevId = x.id; chatOpen = false; if (progress) progress({ i: i + 1, n: qs.length, id: x.id, nota: 'già completata: salto', skip: true }); continue; }
      if (!x.dopo || x.dopo !== prevId || !chatOpen) {
        hooks.newChat(); chatOpen = true;
        if (x.dopo && hooks.seed) { var ctxRecs = chainOf(x).map(function (id) { return done[id] || res.filter(function (r) { return r.id === id && r.ok; })[0]; }).filter(Boolean); if (ctxRecs.length) hooks.seed(ctxRecs); }
      }
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
          var code = d.code || 'sconosciuto', qq = d.quota || null;
          if (code === 'quota' || code === 'provider-quota') {
            if (qq && qq.kind === 'temporaneo' && att === 0 && (qq.retryAfter || 60) <= 120) {   // limite al minuto: si attende il ripristino indicato e si riprova una volta
              var w = Math.max(2, (qq.resetAt ? qq.resetAt - Math.floor(Date.now() / 1000) : (qq.retryAfter || 60)) + 2);
              if (progress) progress({ i: i, n: qs.length, id: x.id, nota: 'limite al minuto: attendo ' + w + ' s' }); await sleep(w * 1000, sig); if (sig && sig.aborted) break; continue;
            }
            quota = true; qinfo = qq || { kind: 'sconosciuto', source: code === 'provider-quota' ? 'gemini' : 'gateway' }; break;   // giornaliero/mensile/sconosciuto: sospendi, non ritentare
          }
          else if (att === 0 && /rate|blocked|busy|timeout|network|provider|empty/.test(code)) { if (progress) progress({ i: i, n: qs.length, id: x.id, nota: 'riprovo tra 65 s (' + code + ')' }); await sleep(65000, sig); if (sig && sig.aborted) break; }
          else rec = { id: x.id, q: x.q, dopo: x.dopo || null, cat: x.cat, ok: false, code: code, ms: Date.now() - t0 };
        }
      }
      if (quota) break;
      if (!rec) break;
      res.push(rec); prevId = x.id; if (progress) progress({ i: i + 1, n: qs.length, id: x.id, rec: rec });
      if (o.checkpoint) { try { o.checkpoint(snap(false)); } catch (e) { } }
    }
    return snap(quota);
  }

  /* ---- valutazione automatica (stessi criteri di tools/mm_eval_report.py; INDICATIVA: il giudizio finale e' dell'utente) ---- */
  var HEDGE; try { HEDGE = new RegExp("non (è|sono|risulta|posso|so|ho|abbiamo|mi risulta|ci sono|esiste)\\b.{0,60}?(confermat|ufficial|sicur|certo|noto|verificat|disponibil|annunciat|informazion|dati|prove|esist)|non lo so|non (ne )?ho (informazioni|dati|certezz)|non posso (confermare|verificare)|ipotes|speculaz|teori|\\bvoci\\b|rumor|potrebbe|potrebbero|incert|non (risulta|esiste)|non ancora|non sono riuscit", 'i'); } catch (e) { HEDGE = /non (è|risulta|posso|so|ho)|ipotes|teori|rumor|potrebbe|incert|non ancora/i; }
  var DENY; try { DENY = new RegExp("\\bnon (?:ha|hanno|è|e'|era|sono|compare|compaiono|appare|recita|risulta|figura|c'è|esiste|esistono|partecipa|prende parte|interpreta|fa parte)\\b|\\bnessun\\w*|\\bin realtà\\b|\\bnon (?:è|e') (?:mai )?(?:stato|apparso)|\\bmai (?:stato|apparso|esistit|uscit|recitat)|\\bfals[oa]\\b|\\berrat[oa]\\b|\\bpremessa\\b|\\bconfond|\\bsmentit", 'i'); } catch (e) { DENY = /\bnon (ha|è|risulta|compare)|\bnessun|\bin realtà/i; }
  var TECH = /\[link rimosso\]|\[\[|controlli automatici|non è una conferma ufficiale|secondo (?:i miei |i )?(?:fatti|dati forniti)|fatti forniti|\bverifica non superata|⚠|Non sono riuscit[ao] a verificare|\(TMDB|archivio TMDB|fonti consultate/i;
  function rx(l) { var o = []; (l || []).forEach(function (s) { try { o.push(new RegExp(String(s).replace(/^\(\?i\)/, ''), 'i')); } catch (e) { } }); return o; }
  function grade(d, r) {
    if (!r || !r.ok) return { e: 'assente', sus: false };
    var t = r.text || '', hedge = HEDGE.test(t), sus = rx(d.no).some(function (x) { return x.test(t); });
    var anyok = !d.ok || rx(d.ok).some(function (x) { return x.test(t); }), allok = rx(d.tutti).every(function (x) { return x.test(t); });
    var vfok = !r.vf || r.vf.ok !== false;
    if (d.nopers && /^dati locali/.test(r.tag || '')) return { e: 'sbagliata', sus: false };
    if (d.tipo === 'incerto') return hedge ? { e: 'corretta', sus: false } : { e: 'sbagliata', sus: true };
    if (sus) return { e: 'sbagliata', sus: true };
    if (anyok && allok) return { e: 'corretta', sus: false };
    if (hedge && d.hedge) return { e: 'incerta', sus: false };
    if (d.tipo === 'falsa') return DENY.test(t) && (allok || !d.tutti) ? { e: 'corretta', sus: false } : { e: 'sbagliata', sus: true };
    if (!vfok && hedge) return { e: 'incerta', sus: false };
    return { e: 'sbagliata', sus: false };
  }
  function med(v) { if (!v.length) return 0; v = v.slice().sort(function (a, b) { return a - b; }); return v[Math.floor((v.length - 1) / 2)]; }
  function p90(v) { if (!v.length) return 0; v = v.slice().sort(function (a, b) { return a - b; }); return v[Math.min(v.length - 1, Math.round(0.9 * (v.length - 1)))]; }
  function summarize(dom, recs) {
    var by = {}; recs.forEach(function (r) { by[r.id] = r; });
    var rows = dom.map(function (d) { var g = grade(d, by[d.id]); return { d: d, r: by[d.id], e: g.e, sus: g.sus }; }).filter(function (x) { return x.e !== 'assente'; });
    var n = rows.length, c = function (s) { return rows.filter(function (x) { return x.e === s; }).length; };
    var fact = rows.filter(function (x) { return x.d.tipo === 'fatto' || x.d.tipo === 'fresco'; }), fr = rows.filter(function (x) { return x.d.tipo === 'fresco'; }), inc = rows.filter(function (x) { return x.d.tipo === 'incerto' || x.d.tipo === 'falsa'; });
    var good = function (a) { return a.filter(function (x) { return x.e === 'corretta' || x.e === 'incerta'; }).length; };
    var ms = rows.map(function (x) { return x.r.ms; }), tt = rows.map(function (x) { return x.r.ttfb; }).filter(Boolean);
    var cats = {}; rows.forEach(function (x) { var k = cats[x.d.cat] = cats[x.d.cat] || { n: 0, corrette: 0, incerte: 0, sbagliate: 0 }; k.n++; if (x.e === 'corretta') k.corrette++; else if (x.e === 'incerta') k.incerte++; else k.sbagliate++; });
    return { eseguite: n, totale: dom.length, corrette: c('corretta'), incerte: c('incerta'), sbagliate: c('sbagliata'), sospette_allucinazioni: rows.filter(function (x) { return x.sus; }).length,
      errori_su_fatti: fact.filter(function (x) { return x.e === 'sbagliata'; }).length, fatti: fact.length, freschezza_ok: good(fr), freschezza_n: fr.length, incertezza_ok: good(inc), incertezza_n: inc.length,
      con_fonte: fact.filter(function (x) { return x.r.srcs && x.r.srcs.length; }).length, verifica_omessa: rows.filter(function (x) { return x.r.vf && x.r.vf.ok === false; }).length, rigenerate: rows.filter(function (x) { return x.r.vf && x.r.vf.retried; }).length,
      tecnici: rows.filter(function (x) { return TECH.test(x.r.text || ''); }).length, nuove: rows.filter(function (x) { return x.d.set === 'V'; }).length, nuove_ok: rows.filter(function (x) { return x.d.set === 'V' && (x.e === 'corretta' || x.e === 'incerta'); }).length,
      lat_mediana_ms: med(ms), lat_p90_ms: p90(ms), ttfb_mediana_ms: med(tt), non_online: rows.filter(function (x) { return !x.r.online; }).length, categorie: cats,
      da_rivedere: rows.filter(function (x) { return x.e === 'sbagliata'; }).map(function (x) { return x.d.id; }) };
  }
  function riepilogoTesto(s) {
    var p = function (a, b) { return b ? Math.round(100 * a / b) + '%' : 'n/d'; };
    return ['Eseguite ' + s.eseguite + '/' + s.totale,
      'Corrette ' + s.corrette + ' (' + p(s.corrette, s.eseguite) + ') · incertezza dichiarata ' + s.incerte + ' · sbagliate ' + s.sbagliate + ' (' + p(s.sbagliate, s.eseguite) + ')',
      'Sospette allucinazioni (da confermare): ' + s.sospette_allucinazioni,
      'Freschezza: ' + s.freschezza_ok + '/' + s.freschezza_n + ' · Incertezza/false premesse: ' + s.incertezza_ok + '/' + s.incertezza_n,
      'Naturalezza: ' + s.tecnici + ' risposte con marcatori tecnici' + (s.nuove ? ' · domande nuove ' + s.nuove_ok + '/' + s.nuove : ''),
      'Con fonte mostrata: ' + s.con_fonte + '/' + s.fatti + ' · verificatore: ' + s.verifica_omessa + ' omessi, ' + s.rigenerate + ' rigenerati',
      'Latenza mediana ' + s.lat_mediana_ms + ' ms · p90 ' + s.lat_p90_ms + ' ms · primo testo ' + s.ttfb_mediana_ms + ' ms'].join('\n');
  }
  root.MMEval = { run: run, pick: pick, GAP: GAP, grade: grade, summarize: summarize, riepilogoTesto: riepilogoTesto };
})(typeof window !== 'undefined' ? window : globalThis);
