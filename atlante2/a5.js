/* Atlante 2.0 — A5: Preferiti, raccolte, progressione dell'esplorazione. Modulo lazy, additivo.
   Dati dell'utente SOLO in `tva-atlante-v2` (nuova chiave; nessuna chiave esistente viene letta-riscritta). Regole: docs/ATLANTE_2_0_REGOLE_XP_BADGE.md (approvate).
   Il nucleo (Core) e' puro e testabile in Node; l'interfaccia usa tvaA3Ctx. Nessun HTML dai dati: solo textContent. */
(function (root) {
  'use strict';
  var KEY = 'tva-atlante-v2', BAK = 'tva-atlante-v2-bak', CAP = 30, BADGE_XP = 40;
  /* XP per singolo dossier esplorato: NON specificato nei documenti approvati → 0 finche' l'utente non decide (nessun valore inventato). */
  var XP_DOSSIER = 0;
  var THR = { dossier: { s: 10000, scroll: 0.6, sez: 2 } };
  var BADGES = [
    { k: 'esploratore', n: 'Esploratore', r: '25 dossier esplorati', need: 25, cnt: 'tot' },
    { k: 'archivista', n: 'Archivista', r: '100 dossier esplorati', need: 100, cnt: 'tot' },
    { k: 'cartografo', n: 'Cartografo', r: '10 universi completati', need: 10, cnt: null, nope: 'Manca il collegamento personaggio→universo e la definizione di «universo completato».' },
    { k: 'cacciatore', n: 'Cacciatore di varianti', r: '3 hub completati', need: 3, cnt: null, nope: 'Gli hub confermati sono pochi e «hub completato» non è ancora definito.' },
    { k: 'custode_artefatti', n: 'Custode degli artefatti', r: '25 artefatti esplorati', need: 25, cnt: 'a', reg: 'a' },
    { k: 'storico', n: 'Storico del Multiverso', r: '25 eventi esplorati', need: 25, cnt: 'e', reg: 'e' },
    { k: 'maestro_nexus', n: 'Maestro del Nexus', r: '100 relazioni narrative distinte', need: 100, cnt: null, nope: 'Le relazioni narrative verificate sono ancora poche e il criterio di «distinta» non è definito.' },
    { k: 'custode_multiverso', n: 'Custode del Multiverso', r: '500 dossier esplorati', need: 500, cnt: 'tot', reg: 'tot' }
  ];
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function dayStr(ms) { var d = new Date(ms); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function addDays(ds, n) { var p = ds.split('-'); var d = new Date(+p[0], +p[1] - 1, +p[2] + n, 12); return dayStr(d.getTime()); }
  function empty() { return { v: 1, fav: {}, col: {}, esp: {}, ric: {}, xp: {}, badge: {} }; }
  function sane(s) {
    var o = empty(); if (!s || typeof s !== 'object') return o;
    ['fav', 'col', 'esp', 'ric', 'xp', 'badge'].forEach(function (k) { if (s[k] && typeof s[k] === 'object' && !Array.isArray(s[k])) o[k] = s[k]; });
    return o;
  }
  /* ---- XP: accredito programmato giorno per giorno (tetto 30/giorno, eccedenza in coda, nulla si perde). Pura lettura: la Tessera somma xp[d] con d <= oggi. ---- */
  function schedule(st, amount, today) {
    var left = amount, d = today, guard = 0;
    while (left > 0 && guard++ < 4000) { var used = Number(st.xp[d]) || 0, room = Math.max(0, CAP - used), put = Math.min(room, left); if (put > 0) { st.xp[d] = used + put; left -= put; } d = addDays(d, 1); }
  }
  function creditedUntil(st, today) { var t = 0; Object.keys(st.xp).forEach(function (d) { if (d <= today) { var n = Number(st.xp[d]); if (isFinite(n) && n > 0) t += Math.min(n, CAP); } }); return t; }
  function pendingAfter(st, today) { var t = 0; Object.keys(st.xp).forEach(function (d) { if (d > today) { var n = Number(st.xp[d]); if (isFinite(n) && n > 0) t += Math.min(n, CAP); } }); return t; }
  function award(st, key, xp, now) {   // ricompensa unica e permanente: una chiave, una sola volta
    if (st.ric[key]) return false; var today = dayStr(now); st.ric[key] = { xp: xp, ts: now, d: today }; if (xp > 0) schedule(st, xp, today); return true;
  }
  /* ---- conteggi: solo dossier reali (esclusi copie, hub e mantelli; alias risolti a monte) ---- */
  function eligible(v) { return !!v && v.k !== 'c' && v.t !== 'h' && v.t !== 'm'; }
  function counts(st, BY) {
    var c = { tot: 0, byT: {} };
    Object.keys(st.esp).forEach(function (id) { var v = BY[id]; if (!eligible(v)) return; c.tot++; c.byT[v.t] = (c.byT[v.t] || 0) + 1; });
    return c;
  }
  function regCounts(BY) { var c = { tot: 0, byT: {} }; Object.keys(BY).forEach(function (id) { var v = BY[id]; if (!eligible(v)) return; c.tot++; c.byT[v.t] = (c.byT[v.t] || 0) + 1; }); return c; }
  function badgeStatus(st, BY) {
    var c = counts(st, BY), rg = regCounts(BY);
    return BADGES.map(function (b) {
      var got = !!st.badge[b.k], have = b.cnt === 'tot' ? c.tot : b.cnt ? (c.byT[b.cnt] || 0) : 0, avail = true, why = '';
      if (!b.cnt) { avail = false; why = b.nope; }
      else if (b.reg) { var tot = b.reg === 'tot' ? rg.tot : (rg.byT[b.reg] || 0); if (tot < b.need) { avail = false; why = 'Nel registro ci sono ' + tot + ' voci di questo tipo: ne servono ' + b.need + '.'; } }
      return { k: b.k, n: b.n, r: b.r, need: b.need, have: have, got: got, avail: avail, why: why, xp: BADGE_XP };
    });
  }
  /* traguardi: assegnati una sola volta, mai revocati */
  function evaluate(st, BY, now) {
    var out = []; badgeStatus(st, BY).forEach(function (b) {
      if (b.got || !b.avail || b.have < b.need) return;
      st.badge[b.k] = now; award(st, 'badge:' + b.k, BADGE_XP, now); out.push(b);
    }); return out;
  }
  /* ---- dossier esplorato: una sola volta per id canonico ---- */
  function markExplored(st, id, BY, now) {
    var v = BY[id]; if (!eligible(v) || st.esp[id]) return { ok: false, badges: [] };
    st.esp[id] = { ts: now, t: v.t };
    if (XP_DOSSIER > 0) award(st, 'dossier:' + id, XP_DOSSIER, now);
    return { ok: true, badges: evaluate(st, BY, now) };
  }
  /* total = sezioni del dossier: con meno di 2 sezioni il requisito diventa «tutte le sezioni» (altrimenti sarebbe irraggiungibile); 0 sezioni = non esplorabile */
  function isExplored(m, total) { var T = THR.dossier, need = total == null ? T.sez : Math.min(T.sez, total); return need >= 1 && m.ms >= T.s && m.scroll >= T.scroll && m.sec >= need; }
  /* ---- preferiti e raccolte ---- */
  function toggleFav(st, id, now) { if (st.fav[id]) { delete st.fav[id]; return false; } st.fav[id] = now; return true; }
  function newCol(st, name, now) { name = String(name || '').trim().slice(0, 40); if (!name) return null; var id = 'c' + now.toString(36) + Math.floor(Math.random() * 1e4).toString(36); st.col[id] = { n: name, ids: [], ts: now }; return id; }
  function renameCol(st, id, name) { name = String(name || '').trim().slice(0, 40); if (!st.col[id] || !name) return false; st.col[id].n = name; return true; }
  function delCol(st, id) { if (!st.col[id]) return false; delete st.col[id]; return true; }
  function colHas(st, cid, id) { return !!(st.col[cid] && st.col[cid].ids.indexOf(id) >= 0); }
  function colToggle(st, cid, id) { var c = st.col[cid]; if (!c) return false; var i = c.ids.indexOf(id); if (i >= 0) { c.ids.splice(i, 1); return false; } c.ids.push(id); return true; }
  var Core = { KEY: KEY, CAP: CAP, BADGE_XP: BADGE_XP, XP_DOSSIER: XP_DOSSIER, BADGES: BADGES, THR: THR, empty: empty, sane: sane, dayStr: dayStr, addDays: addDays, schedule: schedule, creditedUntil: creditedUntil, pendingAfter: pendingAfter, award: award,
    eligible: eligible, counts: counts, regCounts: regCounts, badgeStatus: badgeStatus, evaluate: evaluate, markExplored: markExplored, isExplored: isExplored, toggleFav: toggleFav, newCol: newCol, renameCol: renameCol, delCol: delCol, colHas: colHas, colToggle: colToggle };
  if (typeof module !== 'undefined' && module.exports) { module.exports = Core; return; }

  /* ================= interfaccia ================= */
  var W = window, D = document; if (W.tvaA5 || !W.tvaA3Ctx) return;
  var C = W.tvaA3Ctx(), h = C.h, btn = C.btn, BY = C.BY, api = C.api, ST = api.ST, body = C.body;
  function read() { try { return sane(JSON.parse(W.localStorage.getItem(KEY) || 'null')); } catch (e) { return empty(); } }
  var S = read(), memOnly = false;
  function write() {
    try { var now = Date.now(), prev = W.localStorage.getItem(KEY); var bd = W.localStorage.getItem(BAK + '-d'); if (prev && bd !== dayStr(now)) { W.localStorage.setItem(BAK, prev); W.localStorage.setItem(BAK + '-d', dayStr(now)); }
      W.localStorage.setItem(KEY, JSON.stringify(S)); return true; } catch (e) { memOnly = true; return false; }
  }
  function toast(msg) { var t = h('div', 'a5-toast', msg, { role: 'status' }); (D.documentElement || D.body).appendChild(t); setTimeout(function () { t.classList.add('on'); }, 20); setTimeout(function () { t.classList.remove('on'); setTimeout(function () { t.remove(); }, 400); }, 4200); }
  function announce(bs) { bs.forEach(function (b) { toast('Traguardo ottenuto: ' + b.n + ' (+' + b.xp + ' XP, accreditati con il tetto giornaliero)'); }); }
  function canonical(id) { var r = C.IDX && C.IDX.redirect && C.IDX.redirect[id]; return r && BY[r] ? r : id; }

  /* tracker del dossier: stessa apertura, tempo visibile attivo + scorrimento + sezioni consultate */
  function track(id, stRef) {
    id = canonical(id); var m = { ms: 0, scroll: 0, sec: 0 }, secs = {}, total = null, last = Date.now(), done = !!S.esp[id] || !Core.eligible(BY[id]), iv = 0;
    function scr() { var b = body, sh = b.scrollHeight, ch = b.clientHeight; if (!sh) return; m.scroll = Math.max(m.scroll, sh <= ch + 4 ? 1 : (b.scrollTop + ch) / sh); }
    var stop = function () { if (iv) { clearInterval(iv); iv = 0; } body.removeEventListener('scroll', scr); };
    if (done) return { sec: function () {}, total: function () {}, attach: function () {}, stop: stop };
    body.addEventListener('scroll', scr, { passive: true });
    iv = setInterval(function () {
      var now = Date.now(), dt = Math.min(1500, now - last); last = now;
      if (ST.a3 !== stRef || !body.isConnected) { stop(); return; }
      if (D.visibilityState === 'visible') m.ms += dt; scr();
      if (Core.isExplored(m, total)) { stop(); S = read(); var r = Core.markExplored(S, id, BY, Date.now()); if (r.ok) { write(); announce(r.badges); } }
    }, 500);
    var tk = { sec: function (k) { if (!secs[k]) { secs[k] = 1; m.sec++; } }, total: function (n) { total = n; },
      attach: function (rootEl) { try { var io = new W.IntersectionObserver(function (es) { es.forEach(function (e) { var need = Math.min(e.boundingClientRect.height * 0.5, body.clientHeight * 0.35); if (e.isIntersecting && e.intersectionRect.height >= need - 1) { var k = e.target.id; if (!secs[k]) { secs[k] = 1; m.sec++; } } }); }, { root: body, threshold: [0.1, 0.25, 0.5, 0.75, 1] }); Array.prototype.forEach.call(rootEl.querySelectorAll('.a3-ds'), function (x) { io.observe(x); }); var st0 = stop; stop = function () { io.disconnect(); st0(); }; } catch (e) { /* ok */ } }, metrics: function () { return { ms: m.ms, scroll: m.scroll, sec: m.sec, total: total, done: !!S.esp[id] }; }, stop: stop }; W.tvaA5 && (W.tvaA5.last = tk); return tk;
  }
  function acts(id) { var r = h('div', 'a5-acts'); r.appendChild(favBtn(id)); r.appendChild(colBtn(id)); return r; }
  function favBtn(id) {
    var b = btn('a5-act a5-fav', null, null, { 'aria-label': 'Preferito', 'aria-pressed': 'false' });
    function paint() { var on = !!S.fav[id]; b.setAttribute('aria-pressed', on ? 'true' : 'false'); b.setAttribute('aria-label', on ? 'Rimuovi dai preferiti' : 'Aggiungi ai preferiti'); b.title = b.getAttribute('aria-label'); b.textContent = on ? '★ Preferito' : '☆ Preferito'; b.classList.toggle('on', on); }
    b.addEventListener('click', function () { S = read(); var on = Core.toggleFav(S, id, Date.now()); write(); paint(); toast(on ? 'Aggiunto ai preferiti' : 'Rimosso dai preferiti'); }); paint(); return b;
  }
  function colBtn(id) {
    return btn('a5-act a5-col', '▤ Raccolte', function () { sheet(id); }, { 'aria-label': 'Aggiungi a una raccolta', title: 'Raccolte' });
  }
  function sheet(id) {
    var ov = h('div', 'a5-ov', null, { role: 'dialog', 'aria-modal': 'true', 'aria-label': 'Raccolte' }), box = h('div', 'a5-sheet'); ov.appendChild(box);
    function close() { ov.remove(); }
    function draw() {
      S = read(); box.textContent = ''; box.appendChild(h('h2', '', 'Raccolte'));
      var ids = Object.keys(S.col); if (!ids.length) box.appendChild(h('p', 'soft', 'Non hai ancora raccolte: creane una qui sotto.'));
      ids.forEach(function (cid) { var row = btn('a5-row', null, function () { S = read(); Core.colToggle(S, cid, id); write(); draw(); }, { role: 'checkbox', 'aria-checked': Core.colHas(S, cid, id) ? 'true' : 'false' }); row.appendChild(h('span', 'a5-chk', Core.colHas(S, cid, id) ? '✓' : '')); row.appendChild(h('span', '', S.col[cid].n + ' (' + S.col[cid].ids.length + ')')); box.appendChild(row); });
      var inp = h('input', 'a5-inp', null, { type: 'text', maxlength: '40', placeholder: 'Nome della nuova raccolta', 'aria-label': 'Nome della nuova raccolta' });
      var add = btn('btn fill', 'Crea e aggiungi', function () { S = read(); var cid = Core.newCol(S, inp.value, Date.now()); if (!cid) { inp.focus(); return; } Core.colToggle(S, cid, id); write(); draw(); });
      var cl = btn('btn ghost', 'Chiudi', close); box.appendChild(inp); var r2 = h('div', 'a5-btns'); r2.appendChild(add); r2.appendChild(cl); box.appendChild(r2);
    }
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); }); draw(); (D.documentElement || D.body).appendChild(ov);
  }
  function listOf(ids) {
    var u = h('div', 'a5-list'); ids.forEach(function (id) { var v = BY[id]; if (!v) return; var b = btn('a5-item', null, function () { C.openId(id); }); b.appendChild(h('b', '', v.n)); b.appendChild(h('small', '', (C.uniNome && v.u ? C.uniNome(v.u) : ''))); u.appendChild(b); }); return u;
  }
  function viewPF() {
    C.frame(); api.setTitle('Preferiti e raccolte', 'TVA Atlas'); S = read();
    var root = h('div', 'pad a5-root'); body.appendChild(root); root.appendChild(h('h1', '', 'Preferiti e raccolte'));
    root.appendChild(h('p', 'soft', 'Salvati solo su questo dispositivo, in una chiave separata: non toccano la Tessera né gli altri progressi.'));
    var favs = Object.keys(S.fav).sort(function (a, b) { return S.fav[b] - S.fav[a]; }).filter(function (i) { return BY[i]; });
    root.appendChild(h('h2', '', 'Preferiti (' + favs.length + ')')); root.appendChild(favs.length ? listOf(favs) : h('p', 'soft', 'Tocca ☆ in un dossier per salvarlo qui.'));
    var cids = Object.keys(S.col); root.appendChild(h('h2', '', 'Raccolte (' + cids.length + ')'));
    cids.forEach(function (cid) {
      var c = S.col[cid], card = h('section', 'a5-colcard'), hd = h('div', 'a5-colhd'); hd.appendChild(h('b', '', c.n + ' · ' + c.ids.filter(function (i) { return BY[i]; }).length));
      hd.appendChild(btn('a5-mini', 'Rinomina', function () { var inp = h('input', 'a5-inp', null, { type: 'text', maxlength: '40', value: c.n, 'aria-label': 'Nuovo nome' }); var ok = btn('a5-mini', 'Salva', function () { S = read(); if (Core.renameCol(S, cid, inp.value)) { write(); viewPF(); } }); hd.textContent = ''; hd.appendChild(inp); hd.appendChild(ok); inp.focus(); }));
      var del = btn('a5-mini warn', 'Elimina', function () { del.textContent = 'Conferma eliminazione'; del.classList.add('arm'); del.onclick = function () { S = read(); Core.delCol(S, cid); write(); viewPF(); }; setTimeout(function () { if (del.isConnected) { del.textContent = 'Elimina'; del.classList.remove('arm'); del.onclick = null; } }, 4000); }); hd.appendChild(del);
      card.appendChild(hd); card.appendChild(c.ids.length ? listOf(c.ids) : h('p', 'soft', 'Raccolta vuota: aggiungi voci dal pulsante ▤ di un dossier.')); root.appendChild(card);
    });
    var inp = h('input', 'a5-inp', null, { type: 'text', maxlength: '40', placeholder: 'Nuova raccolta', 'aria-label': 'Nome della nuova raccolta' });
    var mk = btn('btn fill', 'Crea raccolta', function () { S = read(); if (Core.newCol(S, inp.value, Date.now())) { write(); viewPF(); } else inp.focus(); }); var row = h('div', 'a5-btns'); row.appendChild(inp); row.appendChild(mk); root.appendChild(row);
    if (memOnly) root.appendChild(h('p', 'a3-note', 'Memoria locale piena o non disponibile: le modifiche potrebbero non essere salvate.'));
  }
  var TNAME = { p: 'Personaggi', U: 'Universi', o: 'Organizzazioni', a: 'Artefatti', l: 'Luoghi', P: 'Pianeti', e: 'Eventi', t: 'Attori' };
  function viewPR() {
    C.frame(); api.setTitle('Progressione', 'TVA Atlas'); S = read(); var now = Date.now(), today = dayStr(now);
    var root = h('div', 'pad a5-root'); body.appendChild(root); root.appendChild(h('h1', '', 'Progressione dell’esplorazione'));
    var used = Number(S.xp[today]) || 0, pend = Core.pendingAfter(S, today), c = Core.counts(S, BY), rg = Core.regCounts(BY);
    var card = h('div', 'a5-colcard'); card.appendChild(h('span', 'kick', 'Esplorazione di oggi')); card.appendChild(h('b', 'a5-big', Math.min(CAP, used) + ' / ' + CAP + ' XP'));
    card.appendChild(h('p', 'soft', pend ? pend + ' XP in coda: vengono accreditati nei giorni successivi (tetto ' + CAP + ' al giorno, nessuna perdita).' : 'Gli XP oltre il tetto giornaliero restano in coda e vengono accreditati nei giorni successivi.')); root.appendChild(card);
    var how = h('div', 'a5-colcard'); how.appendChild(h('span', 'kick', 'Quando un dossier è «esplorato»')); how.appendChild(h('p', 'soft', 'Resti almeno 10 secondi, scorri almeno il 60% e consulti almeno 2 sezioni, nella stessa apertura. Una sola volta per scheda; copie, hub e mantelli non contano.')); root.appendChild(how);
    root.appendChild(h('h2', '', 'Dossier esplorati: ' + c.tot + ' su ' + rg.tot));
    var ul = h('ul', 'a5-bytype'); Object.keys(TNAME).forEach(function (t) { if (!rg.byT[t]) return; var li = h('li'); li.appendChild(h('span', '', TNAME[t])); li.appendChild(h('b', '', (c.byT[t] || 0) + ' / ' + rg.byT[t])); ul.appendChild(li); }); root.appendChild(ul);
    root.appendChild(h('h2', '', 'Badge di esplorazione'));
    Core.badgeStatus(S, BY).forEach(function (b) {
      var k = h('div', 'a5-badge' + (b.got ? ' got' : b.avail ? '' : ' lock')); var t = h('div', 'a5-bt'); t.appendChild(h('b', '', b.n)); t.appendChild(h('small', '', b.r));
      if (b.got) t.appendChild(h('small', 'ok', 'Ottenuto')); else if (!b.avail) t.appendChild(h('small', 'why', 'Non ancora ottenibile: ' + b.why)); else t.appendChild(h('small', '', b.have + ' / ' + b.need));
      k.appendChild(t); k.appendChild(h('span', 'a5-xp', '+' + b.xp + ' XP')); root.appendChild(k);
    });
    root.appendChild(h('p', 'soft', 'I traguardi ottenuti non vengono mai revocati quando il registro cresce. Gli XP di esplorazione entrano nel totale della Tessera con una sola riga additiva; non compaiono nelle classifiche dei contenuti né nei punteggi dell’Arcade.'));
  }
  W.tvaA5 = { Core: Core, track: track, acts: acts, viewPF: viewPF, viewPR: viewPR, state: function () { return read(); }, summary: function () { S = read(); var t = dayStr(Date.now()); return { fav: Object.keys(S.fav).length, col: Object.keys(S.col).length, esp: Object.keys(S.esp).length, xpOggi: Number(S.xp[t]) || 0 }; } };
})(typeof window !== 'undefined' ? window : globalThis);
