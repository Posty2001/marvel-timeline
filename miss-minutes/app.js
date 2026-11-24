/* Miss Minutes — pagina (controller UI). Nessun innerHTML: tutto il testo passa da textContent.
   Dati dell'app solo in lettura tramite window.parent.tvaMissMinutesHost (stessa origine). */
(function () {
  'use strict';
  var D = document, $ = function (id) { return D.getElementById(id); };
  var host = null; try { host = window.parent !== window && window.parent.tvaMissMinutesHost && window.parent.tvaMissMinutesHost.version === 1 ? window.parent.tvaMissMinutesHost : null; } catch (e) { host = null; }
  var store, eng, gw, busy = false, lastCtx = [];
  var CFG = window.MISS_MINUTES_CONFIG || { endpoint: '' };
  var EP_RE = /^https:\/\/[a-z0-9-]+(\.[a-z0-9-]+)?\.workers\.dev$/;
  function endpointNow() { var e = CFG.endpoint || (store && store.state.prefs.endpoint) || ''; return EP_RE.test(e) ? e : ''; }
  function makeGw() { return window.MMGateway.create({ endpoint: endpointNow(), storage: window.sessionStorage }); }

  /* ---------- mascotte ---------- */
  var SVG = 'http://www.w3.org/2000/svg';
  function mk(tag, attrs, parent) { var n = D.createElementNS(SVG, tag); for (var k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; }
  function drawMascot() {
    var s = mk('svg', { viewBox: '0 0 100 100', 'aria-hidden': 'true' });
    mk('circle', { cx: 50, cy: 50, r: 45, fill: '#f4a43c', stroke: '#ffda8b', 'stroke-width': 3 }, s);
    var g = mk('g', { stroke: '#583519', 'stroke-width': 3, 'stroke-linecap': 'round' }, s);
    mk('path', { d: 'M50 9v8M50 83v8M9 50h8M83 50h8' }, g);
    var h = mk('path', { d: 'M50 50V22', class: 'hand-m' }, g); h.setAttribute('stroke-width', 3);
    mk('path', { d: 'M50 50l18 9' }, g);
    mk('ellipse', { cx: 36, cy: 40, rx: 4.5, ry: 7.5, fill: '#362819', class: 'eye' }, s);
    mk('ellipse', { cx: 64, cy: 40, rx: 4.5, ry: 7.5, fill: '#362819', class: 'eye' }, s);
    mk('path', { d: 'M34 62Q50 77 66 62', fill: 'none', stroke: '#362819', 'stroke-width': 4, 'stroke-linecap': 'round', class: 'mouth' }, s);
    $('mmMascot').appendChild(s);
  }
  function mood(m) { $('mmMascot').setAttribute('data-state', m); }

  /* ---------- utilita' ---------- */
  function el(tag, cls, txt) { var n = D.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; return n; }
  function banner(t) { var b = $('mmBanner'); b.hidden = !t; b.textContent = t || ''; }
  function scrollEnd() { var c = $('mmChat'); c.scrollTop = c.scrollHeight; }
  function speak(t) { try { if (!store.state.prefs.voice || !window.speechSynthesis) return; window.speechSynthesis.cancel(); var u = new SpeechSynthesisUtterance(t.replace(/\[[^\]]*\]/g, '').slice(0, 600)); u.lang = 'it-IT'; window.speechSynthesis.speak(u); } catch (e) {} }

  /* ---------- rendering ---------- */
  function renderMsg(m, idx) {
    var d = el('div', 'mm-msg ' + (m.role === 'user' ? 'user' : 'assistant'));
    if (m.role !== 'user' && m.tag) d.appendChild(el('div', 'mm-tag' + (m.tag.indexOf('online') === 0 ? ' online' : ''), m.tag));
    d.appendChild(el('div', '', m.text));
    if (m.refs && m.refs.length) {
      var r = el('div', 'mm-refs');
      m.refs.forEach(function (x) { var b = el('button', 'mm-chip', x.label); b.type = 'button'; b.onclick = function () { open(x.link); }; r.appendChild(b); });
      d.appendChild(r);
    }
    if (m.flair) d.appendChild(el('div', 'mm-flair', m.flair));
    if (m.action) {
      var a = el('button', 'mm-act', m.action.label); a.type = 'button'; a.onclick = function () { a.disabled = true; m.action.run(); }; var w = el('div', 'mm-refs'); w.appendChild(a); d.appendChild(w);
    }
    return d;
  }
  function render() {
    var c = $('mmChat'); while (c.firstChild) c.removeChild(c.firstChild);
    var s = store.current(); var msgs = s ? s.messages : [];
    $('mmWelcome').hidden = msgs.length > 0;
    msgs.forEach(function (m) { c.appendChild(renderMsg(m)); });
    scrollEnd();
  }
  function appendLive(m) { var d = renderMsg(m); $('mmChat').appendChild(d); $('mmWelcome').hidden = true; scrollEnd(); return d; }

  function open(link) {
    if (!host) { banner('Per aprire le schede usa Miss Minutes dall’app TVA Archives.'); return; }
    try { host.open(link); } catch (e) { banner('Collegamento non disponibile.'); }
  }

  /* ---------- risposta ---------- */
  function liveState() { try { return host ? host.live() : { items: [], note: '' }; } catch (e) { return { items: [], note: '' }; } }
  function convState(s) { return { live: liveState().items, liveNote: liveState().note, lastEntities: (s && s.last) || [] }; }
  function onlineOK() { var p = store.state.prefs; return !!(p.online && p.consent && gw.available()); }
  function resolveRefs(text, ctx) {
    var refs = [];
    var out = text.replace(/\[\[([^\]]{1,60})\]\]/g, function (_, id) {
      var c = ctx.filter(function (x) { return x.id === id; })[0]; if (!c) return '';
      var l = eng.linkOf(id); if (l) refs.push({ label: c.title, link: l }); return c.title;
    }).replace(/https?:\/\/\S+/g, '[link rimosso]');
    return { text: out.trim(), refs: refs.filter(function (r, i, a) { return a.findIndex(function (z) { return z.link === r.link; }) === i; }).slice(0, 5) };
  }

  async function askOnline(q, s, local) {
    var ctx = eng.contextFor(q, convState(s)); lastCtx = ctx;
    var hist = s.messages.slice(-9, -1).filter(function (m) { return (m.role === 'user' || m.role === 'assistant') && !m.personal; }).slice(-6).map(function (m) { return { role: m.role, text: m.text.slice(0, 800) }; });
    var r = await gw.ask({ question: q, history: hist, context: ctx, spoiler: store.state.prefs.spoiler ? 'avoid' : 'off' });
    if (!r.ok) return { ok: false, message: r.message };
    var rr = resolveRefs(r.answer, ctx);
    return { ok: true, text: rr.text, refs: rr.refs };
  }

  async function submit(q, opts) {
    q = String(q || '').trim(); if (!q || busy) return; opts = opts || {};
    busy = true; $('mmSend').disabled = true; banner('');
    var s = store.current() || store.fresh(q);
    if (!s.messages.length) s.title = q.slice(0, 60);
    var isPers = eng.isPersonal(q);
    store.push(s, { role: 'user', text: q, personal: isPers }); appendLive({ role: 'user', text: q }); $('mmQ').value = '';
    mood('think');
    var ans;
    try { ans = eng.ask(q, Object.assign(convState(s), { reveal: !!opts.reveal })); } catch (e) { ans = { text: 'Qualcosa si è inceppato negli archivi. Riprova.', refs: [], tag: 'locale', confidence: 0 }; }
    var wantOnline = !opts.forceLocal && onlineOK() && !eng.isPersonal(q) && (opts.forceOnline || ans.needsOnline || ans.confidence < 0.6);
    var msg = { role: 'assistant', text: ans.text, refs: ans.refs || [], tag: ans.personal ? 'dati locali' : 'archivio locale', flair: ans.flair };
    if (wantOnline) {
      $('mmSub').textContent = 'consulto l’AI online…';
      var o = await askOnline(q, s, ans);
      $('mmSub').textContent = subtitle();
      if (o.ok) { msg = { role: 'assistant', text: o.text, refs: o.refs, tag: 'online · AI · non verificato' + (store.state.prefs.spoiler ? ' · spoiler non garantiti' : '') }; }
      else { banner(o.message); msg.tag = 'archivio locale (AI non disponibile)'; }
    } else if (ans.needsOnline && !onlineOK()) {
      msg.text += '\n(L’AI online è disattiva: puoi attivarla dalle impostazioni.)';
    }
    if (ans.withheld && ans.withheld.length) {
      msg.action = { label: 'Mostra comunque', run: function () { busy = false; submit(q, { reveal: true }); } };
    } else if (!wantOnline && onlineOK() && !ans.personal && ans.intent !== 'saluto') {
      msg.action = { label: 'Chiedi all’AI online', run: function () { busy = false; submit(q, { forceOnline: true }); } };
    }
    if (ans.entities && ans.entities.length) s.last = ans.entities.slice(0, 2);
    msg.personal = !!ans.personal; store.push(s, msg); if (!store.save()) banner('Memoria locale piena o non disponibile: la cronologia potrebbe non essere salvata.');
    appendLive(msg); speak(msg.text); mood('talk'); setTimeout(function () { mood('idle'); }, Math.min(4000, 600 + msg.text.length * 12));
    busy = false; $('mmSend').disabled = false;
  }

  /* ---------- dialoghi ---------- */
  function dlg(title, build) { var b = $('mmDlgBody'); while (b.firstChild) b.removeChild(b.firstChild); b.appendChild(el('h2', '', title)); build(b); var d = $('mmDlg'); if (!d.open) { if (d.showModal) d.showModal(); else d.setAttribute('open', ''); } }
  function toggleRow(b, label, key, onChange, note) {
    var r = el('div', 'row'); var l = el('label', '', label); l.setAttribute('for', 'set-' + key); var i = el('input'); i.type = 'checkbox'; i.id = 'set-' + key; i.checked = !!store.state.prefs[key];
    i.onchange = function () { onChange(i.checked, i); }; r.appendChild(l); r.appendChild(i); b.appendChild(r); if (note) b.appendChild(el('p', 'mm-small', note));
  }
  function settings() {
    dlg('Impostazioni', function (b) {
      toggleRow(b, 'Protezione spoiler', 'spoiler', function (v) { store.state.prefs.spoiler = v; eng.setSpoilerProtection(v); store.save(); },
        'Nasconde le schede segnalate come spoiler finché non le sblocchi. È un aiuto, non una garanzia: non conosco cosa hai visto davvero e le risposte dell’AI online possono rivelare dettagli.');
      toggleRow(b, 'AI online (Gemini, gratuita)', 'online', function (v, inp) {
        if (!v) { store.state.prefs.online = false; store.save(); return; }
        if (!gw.available()) { inp.checked = false; banner('Il gateway non è ancora configurato (vedi DEPLOY.md).'); return; }
        if (!store.state.prefs.consent) { inp.checked = false; consent(); return; }
        store.state.prefs.online = true; store.save();
      }, gw.available() ? 'Quando la domanda non è coperta dall’archivio locale, la domanda, fino a 4 schede pubbliche e gli ultimi messaggi vengono inviati al servizio AI. I tuoi dati personali (visti, voti, note, amici) non vengono mai inviati.' : 'Gateway non configurato: funziona solo il motore locale.');
      if (!CFG.endpoint) {
        var r = el('div', 'row'); var inp = el('input'); inp.type = 'url'; inp.id = 'set-endpoint'; inp.placeholder = 'https://miss-minutes-api.….workers.dev'; inp.value = store.state.prefs.endpoint || ''; inp.setAttribute('aria-label', 'Indirizzo del gateway'); inp.autocapitalize = 'off'; inp.spellcheck = false; inp.style.cssText = 'flex:1;min-width:0;background:#262f23;color:inherit;border:1px solid #5a4a2e;border-radius:10px;padding:8px';
        var sv = el('button', '', 'Salva'); sv.type = 'button'; var msg = el('p', 'mm-small', 'Indirizzo del gateway AI (non è un segreto). Vuoto = solo motore locale.');
        sv.onclick = async function () {
          var v = inp.value.trim().replace(/\/+$/, '');
          if (v && !EP_RE.test(v)) { msg.textContent = 'Indirizzo non valido: deve essere https://…workers.dev'; return; }
          store.state.prefs.endpoint = v; if (!v) { store.state.prefs.online = false; } store.save(); gw = makeGw();
          if (!v) { msg.textContent = 'Gateway rimosso: solo motore locale.'; return; }
          msg.textContent = 'Verifico…'; var h = await gw.health();
          msg.textContent = !h.ok ? 'Gateway non raggiungibile o origine non autorizzata.' : h.enabled ? 'Gateway raggiungibile, AI attiva.' : 'Gateway raggiungibile, AI ancora spenta (attivazione da fare lato Cloudflare).';
          $('mmSub').textContent = subtitle();
        };
        r.appendChild(inp); r.appendChild(sv); b.appendChild(r); b.appendChild(msg);
      }
      toggleRow(b, 'Leggi le risposte ad alta voce', 'voice', function (v) { store.state.prefs.voice = v; store.save(); if (!v) try { speechSynthesis.cancel(); } catch (e) {} });
      var st = eng.stats(); b.appendChild(el('p', 'mm-small', 'Archivio locale: ' + st.entries + ' voci (' + st.curated + ' schede curate, riferimenti da verificare su fonti primarie). Dati dell’app: ' + (host ? 'collegati in sola lettura' : 'non collegati') + '.'));
    });
  }
  function consent() {
    dlg('Attivare l’AI online?', function (b) {
      b.appendChild(el('p', '', 'Per rispondere a domande aperte, Miss Minutes invia a un servizio AI di Google (Gemini, piano gratuito) la tua domanda, fino a 4 schede pubbliche dell’archivio e gli ultimi messaggi della chat.'));
      b.appendChild(el('p', '', 'Non vengono inviati titoli visti, voti, note, amici o altri dati personali. Nel piano gratuito Google può usare i contenuti inviati per migliorare i propri prodotti: non scrivere informazioni private.'));
      b.appendChild(el('p', '', 'Se il servizio non è disponibile o il limite gratuito è finito, risponde il motore locale.'));
      var a = el('button', '', 'Acconsento e attivo'); a.type = 'button'; a.onclick = function () { store.state.prefs.consent = true; store.state.prefs.online = true; store.save(); $('mmDlg').close(); banner('AI online attivata.'); };
      var n = el('button', '', 'No, solo locale'); n.type = 'button'; n.onclick = function () { $('mmDlg').close(); };
      var w = el('div', 'mm-dlg-actions'); w.appendChild(n); w.appendChild(a); b.appendChild(w);
    });
  }
  function showHistory() {
    dlg('Cronologia', function (b) {
      var ss = store.state.sessions; if (!ss.length) b.appendChild(el('p', 'mm-small', 'Nessuna conversazione salvata.'));
      ss.forEach(function (s) {
        var r = el('div', 'row'); var o = el('button', 'hist', s.title + ' · ' + new Date(s.at).toLocaleDateString('it-IT')); o.type = 'button'; o.onclick = function () { store.open(s.id); store.save(); $('mmDlg').close(); render(); };
        var x = el('button', '', '🗑'); x.type = 'button'; x.setAttribute('aria-label', 'Elimina conversazione'); x.onclick = function () { store.remove(s.id); store.save(); showHistory(); render(); };
        r.appendChild(o); r.appendChild(x); b.appendChild(r);
      });
      if (ss.length) { var c = el('button', '', 'Cancella tutta la cronologia'); c.type = 'button'; c.onclick = function () { store.clear(); store.save(); $('mmDlg').close(); render(); }; b.appendChild(c); }
      b.appendChild(el('p', 'mm-small', 'La cronologia resta su questo dispositivo e non viene inviata a nessuno.'));
    });
  }

  /* ---------- voce ---------- */
  function setupVoice() {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition; if (!SR) return;
    var mic = $('mmMic'); mic.hidden = false; var rec = null;
    mic.onclick = function () {
      if (rec) { try { rec.stop(); } catch (e) {} return; }
      try {
        rec = new SR(); rec.lang = 'it-IT'; rec.interimResults = false; rec.maxAlternatives = 1;
        rec.onresult = function (ev) { var t = ev.results[0] && ev.results[0][0] && ev.results[0][0].transcript; if (t) { $('mmQ').value = t.slice(0, 600); } };
        rec.onerror = function () { banner('Dettatura non disponibile (permesso negato o rete assente).'); };
        rec.onend = function () { rec = null; mic.textContent = '🎤'; };
        mic.textContent = '⏹'; rec.start();
      } catch (e) { rec = null; banner('Dettatura non supportata su questo dispositivo.'); }
    };
  }

  function subtitle() { return onlineOK() ? 'TVA · archivio locale + AI online' : 'TVA · archivio locale'; }

  /* ---------- avvio ---------- */
  async function init() {
    drawMascot(); setupVoice();
    store = window.MMStore.create(window.localStorage);
    gw = makeGw();
    var kc = []; try { var r = await fetch('knowledge/core.json'); kc = (await r.json()).records || []; } catch (e) { banner('Archivio locale non caricato: riapri Miss Minutes.'); }
    var data = {};
    if (host) {
      try {
        data.titles = host.titles();
        ['graph:relationshipGraphData', 'powers:tesseraCharPowersData', 'levels:tesseraCharLevelsData', 'levelNames:tesseraLevelNamesData', 'charIds:tesseraCharIdsData', 'mv:mvMapData'].forEach(function (p) { var kv = p.split(':'); try { var t = host.blob(kv[1]); if (t) data[kv[0]] = JSON.parse(t); } catch (e) {} });
      } catch (e) { data = {}; }
    }
    eng = window.MMEngine.create({ data: data, knowledge: kc }); eng.setSpoilerProtection(store.state.prefs.spoiler);
    $('mmSub').textContent = subtitle();
    $('mmMode').textContent = (onlineOK() ? 'AI online attiva · ' : 'Modalità locale · ') + (host ? 'dati dell’app collegati in sola lettura' : 'dati personali non collegati (apri Miss Minutes dall’app)');
    ['Chi è Loki?', 'Terra-616 e Terra-1610', 'Differenza tra Thor e Loki', 'Cosa guardo stasera?', 'Quanti titoli ho visto?', 'Prossime uscite'].forEach(function (q) { var b = el('button', '', q); b.type = 'button'; b.onclick = function () { submit(q); }; $('mmTopics').appendChild(b); });
    $('mmForm').onsubmit = function (e) { e.preventDefault(); submit($('mmQ').value); };
    $('mmNew').onclick = function () { store.state.active = null; store.save(); render(); $('mmQ').focus(); };
    $('mmHist').onclick = showHistory; $('mmSet').onclick = settings;
    $('mmDlgClose').onclick = function () { $('mmDlg').close(); };
    $('mmClose').onclick = function () { try { if (host) host.close(); else history.back(); } catch (e) {} };
    D.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !$('mmDlg').open) { try { host && host.close(); } catch (x) {} } });
    if (!store.usable()) banner('Memoria locale non disponibile: la cronologia non sarà salvata.');
    render();
    try { window.__mm = { ask: submit, engine: eng, store: store }; } catch (e) {}
  }
  init();
})();
