/* Atlante 2.0 — A4.1: Multiverso, Nexus, Percorso. Caricato in lazy da a3.js (W.tvaA3.ctx). Dati: atlante2/data/nexus/g.json (+ index A3).
   Nessun HTML dai dati (solo textContent). Co-apparizioni calcolate qui dalle apparizioni: NON sono relazioni. Ritratti: solo quelli già salvati dall'utente (tvaRit). */
(function () {
  'use strict';
  var W = window, D = document, T = W.tvaA3, C = T && T.ctx && T.ctx();
  if (!C || W.tvaA4) return;
  if (!D.getElementById('a4-css')) { var lk = D.createElement('link'); lk.id = 'a4-css'; lk.rel = 'stylesheet'; lk.href = 'atlante2/a4.css'; D.head.appendChild(lk); }
  var h = C.h, btn = C.btn, BY = C.BY, NS = 'http://www.w3.org/2000/svg';
  var G = null, ADJ = null, CO = null, ST4 = C.api.ST, LBL = {};
  var TL = { famiglia_genitore: 'Genitorialità', famiglia_fratelli: 'Fratelli', famiglia_coniugi: 'Coniugi', partner: 'Relazione sentimentale', famiglia_discendente: 'Discendenza', alleanza: 'Alleanza', amicizia: 'Amicizia', rivalita: 'Rivalità', mentorato: 'Mentorato', appartenenza: 'Appartenenza', successione: 'Successione', tradimento: 'Tradimento', copia: 'Copia', controparte: 'Controparte multiversale', ispirato_a: 'Ispirazione', correlato: 'Associazione editoriale', stessa_scheda: 'Scheda condivisa', segnaposto: 'Segnaposto' };
  var TC = { famiglia_genitore: '#e3c79b', famiglia_fratelli: '#e3c79b', famiglia_coniugi: '#f08fb0', partner: '#f08fb0', famiglia_discendente: '#e3c79b', alleanza: '#6fd08c', amicizia: '#7fd0ff', rivalita: '#ff6a5c', mentorato: '#f5c04a', appartenenza: '#b48ae0', successione: '#f59a23', tradimento: '#ff4fa0', copia: '#9fe0d4', controparte: '#4fd0ff' };
  var VL = ['Da verificare', 'Guida classica', 'Fonte consultata'];
  function sv(n, a, p) { var e = D.createElementNS(NS, n); Object.keys(a || {}).forEach(function (k) { e.setAttribute(k, String(a[k])); }); if (p) p.appendChild(e); return e; }
  function load(cb) {
    if (G) return cb(); C.get('data/nexus/g.json').then(function (d) { G = d; return C.get('data/db/rel.json').catch(function () { return null; }).then(function (x) { mergeRel(x); build(); cb(); }); }).catch(function () { C.body.textContent = ''; C.body.appendChild(h('div', 'empty', 'Dati di TVA Nexus non disponibili offline.')); });
  }
  /* relazioni narrative documentate dal database esteso (stesso formato, stesse regole: verifica, classe, nessuna co-apparizione); si uniscono solo se entrambi i nodi esistono */
  function mergeRel(x) {
    if (!x || !x.r) return;
    x.r.forEach(function (r) {
      if (!BY[r[0]] || !BY[r[1]]) return; var t = x.tipi[r[2]], gi = G.tipi.indexOf(t); if (gi < 0) { G.tipi.push(t); gi = G.tipi.length - 1; }
      G.r.push([r[0], r[1], gi, r[3], r[4], r[5], r[6]]);
    });
  }
  function build() {
    G.coT = 2; ADJ = {}; G.r.forEach(function (r, i) { (ADJ[r[0]] = ADJ[r[0]] || []).push([i, r[1]]); (ADJ[r[1]] = ADJ[r[1]] || []).push([i, r[0]]); });
    var inv = {}; Object.keys(G.app).forEach(function (id) { G.app[id].forEach(function (n) { (inv[n] = inv[n] || []).push(id); }); });
    CO = {}; Object.keys(inv).forEach(function (n) { var a = inv[n]; if (a.length > 60) return; for (var i = 0; i < a.length; i++) for (var j = i + 1; j < a.length; j++) { var k = a[i] < a[j] ? a[i] + '|' + a[j] : a[j] + '|' + a[i]; CO[k] = (CO[k] || 0) + 1; } });
    G.coN = {}; Object.keys(CO).forEach(function (k) { var p = k.split('|'); (G.coN[p[0]] = G.coN[p[0]] || []).push([p[1], CO[k]]); (G.coN[p[1]] = G.coN[p[1]] || []).push([p[0], CO[k]]); });
    G.cnt = {}; G.r.forEach(function (r) { var t = G.tipi[r[2]]; G.cnt[t] = (G.cnt[t] || 0) + 1; });
  }
  function nm(id) { return BY[id] ? BY[id].n : id; }
  function co(a, b) { return CO[a < b ? a + '|' + b : b + '|' + a] || 0; }
  /* ---------- pan / zoom (pointer events, pinch, rotella) ---------- */
  function panzoom(vp, world, o) {
    o = o || {}; var s = { x: 0, y: 0, k: o.k || 1 }, pts = {}, d0 = 0, k0 = 1, lastTap = 0, mv = false, raf = 0;
    function ap() { raf = 0; world.style.transform = 'translate3d(' + s.x.toFixed(1) + 'px,' + s.y.toFixed(1) + 'px,0) scale(' + s.k.toFixed(3) + ')'; if (o.onChange) o.onChange(s); }
    function ask() { if (!raf) raf = requestAnimationFrame(ap); }
    function zoomAt(f, cx, cy) { var nk = Math.max(o.min || .3, Math.min(o.max || 3, s.k * f)); f = nk / s.k; s.x = cx - (cx - s.x) * f; s.y = cy - (cy - s.y) * f; s.k = nk; ask(); }
    function center() { var r = vp.getBoundingClientRect(); return [r.width / 2, r.height / 2]; }
    vp.addEventListener('pointerdown', function (e) { if (e.target.closest && e.target.closest('.a4-ctl')) return; pts[e.pointerId] = [e.clientX, e.clientY]; mv = false; var ks = Object.keys(pts); if (ks.length === 2) { d0 = Math.hypot(pts[ks[0]][0] - pts[ks[1]][0], pts[ks[0]][1] - pts[ks[1]][1]); k0 = s.k; } });
    vp.addEventListener('pointermove', function (e) {
      var p = pts[e.pointerId]; if (!p) return; var ks = Object.keys(pts);
      if (ks.length === 2) { var a = pts[ks[0]], b = pts[ks[1]]; pts[e.pointerId] = [e.clientX, e.clientY]; a = pts[ks[0]]; b = pts[ks[1]]; var d = Math.hypot(a[0] - b[0], a[1] - b[1]), r = vp.getBoundingClientRect(); if (!mv) { try { vp.setPointerCapture(e.pointerId); } catch (x) { /* ok */ } } if (d0 > 0) { var tk = Math.max(o.min || .3, Math.min(o.max || 3, k0 * d / d0)); zoomAt(tk / s.k, (a[0] + b[0]) / 2 - r.left, (a[1] + b[1]) / 2 - r.top); } mv = true; return; }
      var dx = e.clientX - p[0], dy = e.clientY - p[1]; if (!mv && Math.abs(dx) + Math.abs(dy) < 8) return; if (!mv) { try { vp.setPointerCapture(e.pointerId); } catch (x) { /* ok */ } } mv = true; s.x += dx; s.y += dy; pts[e.pointerId] = [e.clientX, e.clientY]; ask();
    });
    function up(e) { delete pts[e.pointerId]; if (mv) vp.dataset.drag = '1'; setTimeout(function () { delete vp.dataset.drag; }, 60); }
    vp.addEventListener('pointerup', up); vp.addEventListener('pointercancel', up);
    vp.addEventListener('wheel', function (e) { e.preventDefault(); var r = vp.getBoundingClientRect(); zoomAt(e.deltaY < 0 ? 1.15 : 1 / 1.15, e.clientX - r.left, e.clientY - r.top); }, { passive: false });
    function fit(w, hh, pad) { var r = vp.getBoundingClientRect(); pad = pad || 24; var k = Math.max(o.min || .3, Math.min(o.max || 3, Math.min((r.width - pad) / w, (r.height - pad) / hh))); return k; }
    return { s: s, fit: fit, zoom: function (f) { var c = center(); zoomAt(f, c[0], c[1]); }, reset: function (x, y, k) { var c = center(); s.k = k || o.k || 1; s.x = c[0] - (x || 0) * s.k; s.y = c[1] - (y || 0) * s.k; ask(); } };
  }
  function controls(host, pz, onRe, vp) {
    var c = h('div', 'a4-ctl'); c.appendChild(btn('', '+', function () { pz.zoom(1.3); }, { 'aria-label': 'Ingrandisci' })); c.appendChild(btn('', '−', function () { pz.zoom(1 / 1.3); }, { 'aria-label': 'Riduci' })); c.appendChild(btn('', '◎', function () { onRe(); }, { 'aria-label': 'Ricentra' }));
    var fs = btn('', '⛶', function () { var on = host.classList.toggle('a4-full'); fs.setAttribute('aria-pressed', on ? 'true' : 'false'); try { if (on && host.requestFullscreen) host.requestFullscreen().catch(function () {}); else if (!on && D.fullscreenElement) D.exitFullscreen(); } catch (e) { /* ok */ } setTimeout(onRe, 80); }, { 'aria-label': 'Schermo intero', 'aria-pressed': 'false' }); c.appendChild(fs); host.appendChild(c); avoidFab(c); setTimeout(function () { avoidFab(c); }, 300);
  }
  function avoidFab(c) {
    function chk() { var f = D.getElementById('mmFab'); if (!f || !c.isConnected) return; c.classList.remove('r'); var a = c.getBoundingClientRect(), b = f.getBoundingClientRect(); if (!(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom)) c.classList.add('r'); var a2 = c.getBoundingClientRect(); if (!(a2.right < b.left || a2.left > b.right || a2.bottom < b.top || a2.top > b.bottom)) c.classList.remove('r'); }
    chk(); if (!c.dataset.fabw) { c.dataset.fabw = '1'; ['pointerup', 'scroll', 'resize', 'orientationchange'].forEach(function (ev) { W.addEventListener(ev, function () { setTimeout(chk, 60); }, true); }); }
  }
  function bgStars(el) { var s = ''; for (var i = 0, x = 12345; i < 46; i++) { x = (Math.imul(x, 1103515245) + 12345) >>> 0; var a = x % 100, b = (x >>> 8) % 100; s += (i ? ',' : '') + 'radial-gradient(1px 1px at ' + a + '% ' + b + '%,rgba(255,240,210,.7),transparent)'; } el.style.backgroundImage = s + ',radial-gradient(circle at 50% 50%,rgba(245,154,35,.10),transparent 55%)'; }
  function nodeEl(id, cls, big) {
    var v = BY[id], n = h('button', 'a4-n ' + (cls || '') + ' t-' + (v ? v.t : 'p')); n.type = 'button'; n.dataset.id = id; n.setAttribute('aria-label', nm(id));
    var em = h('span', 'em'); if (v) { em.appendChild(C.emblem(v, false)); C.paintAny(em, v, false); } n.appendChild(em); var L = LBL[id] || labels([id])[id], lb = h('span', 'lb', L[0]); if (L[1]) lb.appendChild(h('small', '', L[1])); n.appendChild(lb); n.title = nm(id); return n;
  }
  /* ---------- MULTIVERSO ---------- */
  var ORB = [['Continuità principale', 0], ['Diramazione / universo alternativo', 1], ['Universo autonomo', 2], ['Raggruppamento editoriale', 3]];
  function renderMv() {
    C.frame(); C.api.setTitle('Osservatorio del Multiverso', 'La mappa degli universi'); var s = C.A3(), root = h('div', 'a4-root'); C.body.appendChild(root);
    root.appendChild(h('p', 'a3-note', 'Le orbite raggruppano gli universi per natura documentata. Le distanze non indicano parentele né gerarchie; la TVA non è un universo.'));
    var host = h('div', 'a4-vp'), world = h('div', 'a4-world'); bgStars(host); host.appendChild(world); root.appendChild(host);
    var sheet = h('div', 'a4-sheet'); sheet.hidden = true; root.appendChild(sheet);
    var U = (C.ORD.U || []).slice(), by = {}, tva = [], R0 = 150, ST = 120;
    LBL = labels(U.map(function (v) { return v.i; }));
    U.forEach(function (v) { var c = C.uniCont(v.i); if (/Luogo narrativo/.test(c)) { tva.push(v); return; } var o = ORB.filter(function (x) { return x[0] === c; })[0]; (by[o ? o[1] : 2] = by[o ? o[1] : 2] || []).push(v); });
    // layout adattivo: raggio dell'orbita in funzione del numero di universi (nessuna sovrapposizione di etichette)
    var CLR = C.ORBCLR, cnt = [1, 2, 3].map(function (i) { return (by[i] || []).length; }), RAD = [], prev = 120;
    [1, 2, 3].forEach(function (i) { var need = Math.ceil(cnt[i - 1] * 96 / 6.283); prev = cnt[i - 1] ? Math.max(prev + 135, need) : prev; RAD[i] = prev; });
    var RM = Math.max(RAD[1], RAD[2], RAD[3], 200), WS = Math.ceil((RM + 110) * 2), HC = WS / 2; s.WS = WS;
    var svg = sv('svg', { 'class': 'a4-orb', width: WS, height: WS, viewBox: (-HC) + ' ' + (-HC) + ' ' + WS + ' ' + WS }, world);
    [1, 2, 3].forEach(function (i) { if (cnt[i - 1]) sv('circle', { cx: 0, cy: 0, r: RAD[i], fill: 'none', stroke: CLR[i], 'stroke-opacity': .42, 'stroke-width': 1.4, 'stroke-dasharray': '3 6' }, svg); });
    var hue = C.uniHue;
    var pos = {}; function put(v, r, a, cls, oi) { var x = r * Math.cos(a), y = r * Math.sin(a), n = nodeEl(v.i, cls); n.style.left = (HC + x) + 'px'; n.style.top = (HC + y) + 'px'; n.style.setProperty('--oc', CLR[oi]); n.style.setProperty('--hu', 'hsl(' + hue(v.i) + ',66%,68%)'); n.addEventListener('click', function () { if (host.dataset.drag) return; pick(v.i); }); world.appendChild(n); pos[v.i] = n; }
    (by[0] || []).forEach(function (v) { put(v, 0, 0, 'sun', 0); });
    [1, 2, 3].forEach(function (i) { var arr = (by[i] || []).sort(function (a, b) { return a.n < b.n ? -1 : 1; }); arr.forEach(function (v, j) { put(v, RAD[i], -Math.PI / 2 + j * 2 * Math.PI / arr.length + i * .4, 'o' + i, i); }); });
    tva.forEach(function (v) { put(v, 0, 0, 'tva', 3); pos[v.i].style.left = (HC + RM - 20) + 'px'; pos[v.i].style.top = (HC + RM - 20) + 'px'; pos[v.i].title = 'Separata dagli universi'; });
    world.style.width = WS + 'px'; world.style.height = WS + 'px';
    var leg = h('div', 'a4-leg'); ORB.forEach(function (o, i) { if (i === 0 || cnt[i - 1]) { var l = h('span', 'a4-lg'); var sw = h('i'); sw.style.background = CLR[i]; l.appendChild(sw); l.appendChild(D.createTextNode(o[0])); leg.appendChild(l); } }); root.insertBefore(leg, sheet);
    var pz = panzoom(host, world, { min: .2, max: 2.6, k: .6 }); function re() { pz.reset(HC, HC, pz.fit(WS - 40, WS - 40, 12)); } re(); setTimeout(re, 120); setTimeout(re, 450); controls(host, pz, re);
    var cmp = s.cmp || '';
    function nCount(u) { return (C.ORD.p || []).filter(function (v) { return v.u === u; }).length; }
    function pick(u) {
      sheet.hidden = false; sheet.textContent = ''; var v = BY[u], x = C.IDX.meta.universi[u] || {};
      if (cmp && cmp !== u) { compare(cmp, u); return; }
      sheet.appendChild(h('span', 'kick', 'Universo')); sheet.appendChild(h('h2', '', C.uniNome(u) || v.n)); if (x.c) sheet.appendChild(h('p', 'a3-note', x.c + (x.nt ? ' — ' + x.nt : '')));
      var ids = (C.ORD.p || []).filter(function (q) { return q.u === u; }); sheet.appendChild(h('p', '', ids.length + ' identità catalogate in questo universo.'));
      var g = h('div', 'a3-grid c3'); ids.slice(0, 18).forEach(function (q) { g.appendChild(C.tile(q, true)); }); sheet.appendChild(g);
      var row = h('div', 'a3-row'); row.appendChild(btn('btn fill', 'Apri la scheda', function () { C.openId(u); })); row.appendChild(btn('btn ghost', 'Catalogo dell’universo', function () { C.api.nav('a3', { a3: { v: 'cat', t: 'p', m: 'c', n: 36, u: u } }); }));
      row.appendChild(btn('btn ghost', 'Confronta con un altro universo', function () { cmp = u; s.cmp = u; sheet.appendChild(h('p', 'a3-note', 'Tocca un secondo universo nell’osservatorio.')); })); sheet.appendChild(row);
      if (!G) return; try { sheet.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); } catch (e) { /* ok */ }
    }
    function compare(a, b) {
      sheet.appendChild(h('span', 'kick', 'Confronto')); sheet.appendChild(h('h2', '', (C.uniNome(a) || nm(a)) + ' ↔ ' + (C.uniNome(b) || nm(b))));
      sheet.appendChild(h('p', '', nCount(a) + ' identità contro ' + nCount(b) + '. Sono mostrate solo le controparti documentate; nessuna distanza è inventata.'));
      var ps = G.r.filter(function (r) { return r[3] === 'c' && BY[r[0]] && BY[r[1]] && ((BY[r[0]].u === a && BY[r[1]].u === b) || (BY[r[0]].u === b && BY[r[1]].u === a)); });
      if (!ps.length) sheet.appendChild(h('p', 'empty', 'Nessuna controparte documentata tra questi due universi.'));
      ps.forEach(function (r) { var d = h('div', 'a4-pair'); d.appendChild(btn('chip', nm(r[0]), function () { C.openId(r[0]); })); d.appendChild(h('span', 'soft', '↔')); d.appendChild(btn('chip', nm(r[1]), function () { C.openId(r[1]); })); d.appendChild(h('small', '', VL[r[4]])); sheet.appendChild(d); });
      sheet.appendChild(btn('btn fill', 'Confronto dettagliato', function () { C.api.nav('a3', { a3: { v: 'cp', ua: a, ub: b } }); }));
      sheet.appendChild(btn('btn ghost', 'Chiudi il confronto', function () { cmp = ''; s.cmp = ''; sheet.hidden = true; }));
    }
    load(function () { /* dati controparti pronti per il confronto */ });
  }
  /* ---------- NEXUS ---------- */
  /* Una sola voce per nodo vicino, ma con TUTTE le relazioni documentate della classe migliore (rels): nessuna viene nascosta o presentata come unica.
     Es.: Iron Man e Steve Rogers → amicizia + rivalità (non «solo rivali»). Le classi inferiori (editoriali/co-apparizioni) restano in `more`. */
  function edgesOf(id, S) {
    var by = {}, order = [], rank = { n: 0, c: 1, e: 2, a: 3 };
    (ADJ[id] || []).forEach(function (e) {
      var r = G.r[e[0]], t = G.tipi[r[2]], cl = r[3]; if (cl === 'e' && !S.ed) return; if (S.tp[t] === false) return; if (r[4] === 0 && !S.un) return; if (e[1] === id) return;
      var x = by[e[1]]; if (!x) { x = by[e[1]] = []; order.push(e[1]); } x.push({ cl: cl, t: t, v: r[4], q: r[5], d: r[0] === id, c: r[6] });
    });
    var out = order.map(function (nid) {
      var arr = by[nid], best = Math.min.apply(null, arr.map(function (z) { return rank[z.cl]; })), top = arr.filter(function (z) { return rank[z.cl] === best; }).sort(function (a, b) { return (b.v - a.v) || (a.t < b.t ? -1 : 1); }), seenT = {}, rels = [];
      top.forEach(function (z) { var k = z.t + '|' + z.q + '|' + z.d; if (!seenT[k]) { seenT[k] = 1; rels.push(z); } });
      var more = []; arr.forEach(function (z) { if (rank[z.cl] > best && more.indexOf(z.t) < 0 && !rels.some(function (y) { return y.t === z.t; })) more.push(z.t); });
      var z0 = rels[0]; return { id: nid, cl: z0.cl, t: z0.t, v: Math.max.apply(null, rels.map(function (y) { return y.v; })), q: z0.q, d: z0.d, c: z0.c, rels: rels, more: more };
    });
    if (S.co > 0) (G.coN[id] || []).forEach(function (c) { if (c[0] !== id && c[1] >= S.co && !out.some(function (o) { return o.id === c[0]; })) out.push({ id: c[0], cl: 'a', t: 'co_apparizione', v: 1, n: c[1], rels: [{ cl: 'a', t: 'co_apparizione', v: 1, n: c[1] }], more: [] }); });
    out.sort(function (a, b) { return rank[a.cl] - rank[b.cl] || (b.v - a.v) || (b.n || 0) - (a.n || 0) || (b.rels.length - a.rels.length) || (nm(a.id) < nm(b.id) ? -1 : 1); });
    return out;
  }
  /* Etichette dei nodi: nome breve e riconoscibile (il nome completo resta in aria-label, nell'elenco e nel dossier). Le identità che
     condividono lo stesso nome breve vengono distinte (nome civile e/o qualificatore: universo o produzione). */
  function parts(id) {
    var v = BY[id], n = (v && v.n) || id, m = /\s*\(([^)]*)\)\s*$/.exec(n), qual = m ? m[1] : '', base = m ? n.slice(0, m.index) : n, sp = base.split(/\s*\/\s*/);
    if (v && v.t === 'U') { var em = /^Earth-([0-9A-Z]+)\s+—\s+(.+)$/.exec(n); if (em) return { short: em[2], civil: em[2], qual: 'Terra-' + em[1] }; var e2 = /^Earth-([0-9A-Z]+)$/.exec(n); if (e2) return { short: 'Terra-' + e2[1], civil: 'Terra-' + e2[1], qual: '' }; return { short: base, civil: base, qual: qual }; }
    return { short: sp[1] || sp[0], civil: sp[0], qual: qual };
  }
  function qshort(q) { return String(q || '').replace(/Your Friendly Neighborhood Spider-Man/i, 'YFNSM').replace(/-?verse/i, '').replace(/^franchise\s+/i, '').replace(/,.*$/, '').trim().slice(0, 18); }
  function labels(ids) {
    var P = {}, g = {}, out = {}; ids.forEach(function (id) { P[id] = parts(id); (g[P[id].short] = g[P[id].short] || []).push(id); });
    ids.forEach(function (id) {
      var p = P[id], dup = g[p.short].length > 1, l1 = p.short, l2 = '';
      if (dup) {
        l1 = p.civil || p.short; var same = ids.filter(function (o) { return P[o].short === p.short && P[o].civil === p.civil; }).length > 1;
        var u = BY[id] && BY[id].u && C.IDX.meta.universi[BY[id].u] ? C.IDX.meta.universi[BY[id].u].n.replace(/^Earth-[0-9A-Z]+ — /, '') : ''; var q = qshort(p.qual) || qshort(u);
        if (same || P[id].civil === P[id].short) l2 = q; else if (q && ids.some(function (o) { return o !== id && P[o].civil === p.civil; })) l2 = q;
        if (!l2 && p.civil !== p.short) l2 = p.short;
      } else if (BY[id] && BY[id].t === 'U') l2 = p.qual;
      out[id] = [l1, l2];
    }); return out;
  }
  function pickList(host, onPick, ph) {
    var w = h('div', 'a4-pick'), inp = h('input', 'a3-in'); inp.type = 'search'; inp.placeholder = ph; inp.setAttribute('autocomplete', 'off'); inp.setAttribute('aria-label', ph); w.appendChild(inp); var ul = h('div', 'a4-sug'); ul.hidden = true; w.appendChild(ul); var tm;
    inp.addEventListener('input', function () { clearTimeout(tm); tm = setTimeout(function () { ul.textContent = ''; var q = inp.value; if (!q.trim()) { ul.hidden = true; return; } var r = C.search(q) || {}, arr = []; ['p', 'o', 'U', 'h', 'm', 'a', 'l', 'P', 'e'].forEach(function (t) { (r[t] || []).slice(0, 5).forEach(function (e) { if (G && ADJ && (ADJ[e[1].i] || (G.coN[e[1].i]))) arr.push(e[1]); }); }); arr.slice(0, 8).forEach(function (v) { ul.appendChild(btn('a4-s', v.n, function () { inp.value = v.n; ul.hidden = true; onPick(v.i); })); }); if (!arr.length) ul.appendChild(h('span', 'soft', 'Nessuna voce collegata trovata.')); ul.hidden = false; }, 120); }); host.appendChild(w); return inp;
  }
  function renderNx() {
    C.frame(); var s = C.A3(); s.c = s.c || 'id-iron-man'; if (!BY[s.c]) s.c = (C.ORD.p[0] || {}).i; var S = s.S = s.S || { co: 0, cap: 20, ed: false, un: true, tp: {} }; s.hist = s.hist || [];
    C.api.setTitle('TVA Nexus', nm(s.c)); var root = h('div', 'a4-root'); C.body.appendChild(root);
    pickList(root, function (id) { go(id); }, 'Cerca un’identità, un’organizzazione…');
    var bar = h('div', 'a4-bar'), tools = h('div', 'a4-tools'), trail = h('div', 'a4-trail'); trail.setAttribute('aria-label', 'Percorso esplorato'); root.appendChild(bar); root.appendChild(trail); root.appendChild(tools);
    var host = h('div', 'a4-vp a4-nx'), world = h('div', 'a4-world'); bgStars(host); host.appendChild(world); root.appendChild(host);
    var leg = h('div', 'a4-leg'); root.appendChild(leg); var list = h('div', 'a4-rl'); root.appendChild(list);
    var pz = panzoom(host, world, { min: .4, max: 3, k: 1 }); controls(host, pz, function () { lay(); }); function lay() { var W0 = s.WS || 1000; pz.reset(W0 / 2, W0 / 2, pz.fit(W0 - 60, W0 - 60, 16)); } setTimeout(lay, 120); setTimeout(lay, 450);
    function trackRel(a, b) { try { var recs = []; (ADJ[a] || []).forEach(function (e) { if (e[1] === b) { var r = G.r[e[0]]; recs.push([r[0], r[1], G.tipi[r[2]], r[3], r[4]]); } }); if (recs.length && C.a5) C.a5(function (m) { m.onRelation(recs); }); } catch (e) { /* ok */ } }
    function go(id, back) { if (!back && s.c && s.c !== id) trackRel(s.c, id); if (!back && s.c !== id) s.hist.push(s.c); s.c = id; C.api.setTitle('TVA Nexus', nm(id)); draw(); }
    function chipT(txt, on, fn, title) { var b = btn('chip' + (on ? ' on' : ''), txt, fn, { 'aria-pressed': on ? 'true' : 'false' }); if (title) b.title = title; return b; }
    function toolbar() {
      tools.textContent = ''; bar.textContent = ''; bar.appendChild(btn('btn ghost', '← Indietro', function () { var p = s.hist.pop(); if (p) go(p, true); }, s.hist.length ? {} : { disabled: 'disabled' })); bar.appendChild(btn('btn ghost', 'Apri il dossier', function () { C.openId(s.c); })); bar.appendChild(btn('btn ghost', 'Percorso da qui', function () { C.api.nav('a3', { a3: { v: 'pc', a: s.c, b: '', m: 'mix' } }); }));
      var nAct = (S.cap !== 20 ? 1 : 0) + (S.co > 0 ? 1 : 0) + (S.ed ? 1 : 0) + (S.un ? 0 : 1) + Object.keys(S.tp).filter(function (t) { return S.tp[t] === false; }).length, fb = btn('chip a4-fbtn' + (nAct ? ' on' : ''), 'Filtri' + (nAct ? ' · ' + nAct : '') + (s.fo ? ' ▴' : ' ▾'), function () { s.fo = !s.fo; toolbar(); }, { 'aria-expanded': s.fo ? 'true' : 'false' }); bar.appendChild(fb); tools.hidden = !s.fo;
      tools.appendChild(h('span', 'soft', 'Nodi')); [12, 20, 30].forEach(function (n) { tools.appendChild(chipT(String(n), S.cap === n, function () { S.cap = n; draw(); })); });
      tools.appendChild(h('span', 'soft', 'Co-apparizioni')); [[0, 'No'], [1, '1+'], [2, '2+'], [3, '3+'], [4, '4+']].forEach(function (x) { tools.appendChild(chipT(x[1], S.co === x[0], function () { S.co = x[0]; draw(); }, 'Soglia di apparizioni in comune (non sono relazioni narrative)')); });
      var tcn = {}; (ADJ[s.c] || []).forEach(function (e) { var r = G.r[e[0]]; if (r[3] === 'n' || r[3] === 'c' || (r[3] === 'e' && S.ed)) { var t = G.tipi[r[2]]; tcn[t] = (tcn[t] || 0) + 1; } });
      var tk = Object.keys(tcn).sort(function (a, b) { return tcn[b] - tcn[a] || (a < b ? -1 : 1); });
      if (tk.length > 1) { tools.appendChild(h('span', 'soft', 'Tipi di relazione')); tk.forEach(function (t) { tools.appendChild(chipT((TL[t] || t) + ' · ' + tcn[t], S.tp[t] !== false, function () { S.tp[t] = S.tp[t] === false; draw(); }, 'Mostra o nascondi questo tipo di relazione')); }); }
      tools.appendChild(chipT('Editoriali', S.ed, function () { S.ed = !S.ed; draw(); }, 'Associazioni dalla scheda, non relazioni narrative')); tools.appendChild(chipT('Da verificare', S.un, function () { S.un = !S.un; draw(); }, 'Mostra le relazioni non ancora verificate'));
    }
    function pos(i, n, ring) { var R = ring === 0 ? Math.max(170, n * 92 / 6.283) : Math.max(330, 170 + 150, n * 92 / 6.283), a = -Math.PI / 2 + i * 2 * Math.PI / Math.max(n, 1) + (ring ? Math.PI / Math.max(n, 1) : 0); return [R * Math.cos(a), R * Math.sin(a)]; }
    function draw() {
      toolbar(); world.textContent = ''; list.textContent = ''; leg.textContent = ''; trail.textContent = ''; trail.hidden = !s.hist.length;
      if (s.hist.length) {   // traccia dell'esplorazione: ogni tappa e' toccabile e riporta a quel punto
        trail.appendChild(h('span', 'soft', 'Percorso')); var th = s.hist.slice(-4), off = s.hist.length - th.length; if (off) trail.appendChild(h('span', 'soft', '…'));
        th.forEach(function (id, i) { trail.appendChild(btn('chip', parts(id).short, function () { s.hist = s.hist.slice(0, off + i); go(id, true); }, { title: nm(id) })); trail.appendChild(h('span', 'soft', '›')); });
        trail.appendChild(h('b', 'a4-here', parts(s.c).short));
      }
      var all = edgesOf(s.c, S), nar = all.filter(function (e) { return e.cl === 'n' || e.cl === 'c'; }), oth = all.filter(function (e) { return e.cl !== 'n' && e.cl !== 'c'; });
      var sel = nar.slice(0, S.cap); var left = S.cap - sel.length; if (left > 0) sel = sel.concat(oth.slice(0, left));
      LBL = labels([s.c].concat(sel.map(function (e) { return e.id; })));
      var N = sel.length, n1 = Math.min(N, 10), n2 = N - n1, RM = n2 ? Math.max(330, n2 * 92 / 6.283) : Math.max(170, n1 * 92 / 6.283), WS = Math.ceil((RM + 90) * 2); WS = Math.max(WS, 600); var HC = WS / 2; world.style.width = WS + 'px'; world.style.height = WS + 'px'; s.WS = WS; s.RM = RM;
      var svg = sv('svg', { 'class': 'a4-edges', width: WS, height: WS, viewBox: (-HC) + ' ' + (-HC) + ' ' + WS + ' ' + WS }, world);
      var c0 = nodeEl(s.c, 'sun'); c0.style.left = HC + 'px'; c0.style.top = HC + 'px'; var used = {};
      sel.forEach(function (e, i) {
        var n1 = Math.min(N, 10), ring = i < n1 ? 0 : 1, idx = ring ? i - n1 : i, cnt = ring ? N - n1 : n1, p = pos(idx, cnt, ring);
        var rl = (e.rels || [e]).slice(0, 4), nr = rl.length, dl = Math.hypot(p[0], p[1]) || 1, ox = -p[1] / dl, oy = p[0] / dl;
        rl.forEach(function (z, k) {
          var col = z.cl === 'a' ? 'rgba(255,240,210,.5)' : z.cl === 'e' ? 'rgba(200,190,170,.55)' : (TC[z.t] || '#e3c79b'); used[z.t] = [col, z.cl];
          var of = (k - (nr - 1) / 2) * 6;   // più relazioni documentate = più tratti paralleli, ciascuno con il proprio colore (nessuna prevale)
          sv('line', { x1: (ox * of).toFixed(1), y1: (oy * of).toFixed(1), x2: (p[0] + ox * of).toFixed(1), y2: (p[1] + oy * of).toFixed(1), stroke: col, 'stroke-width': z.cl === 'n' ? 2.4 : z.cl === 'c' ? 2 : 1.2, 'stroke-dasharray': z.cl === 'c' ? '8 4' : z.cl === 'e' ? '2 5' : z.cl === 'a' ? '6 3 1 3' : (z.v === 0 ? '5 5' : '0'), 'stroke-opacity': z.v === 0 && z.cl === 'n' ? .55 : .95 }, svg);
        });
        var n = nodeEl(e.id, e.cl === 'e' ? 'ed' : e.cl === 'a' ? 'ca' : ''); n.style.left = (HC + p[0]) + 'px'; n.style.top = (HC + p[1]) + 'px'; n.addEventListener('click', function () { if (host.dataset.drag) return; go(e.id); }); world.appendChild(n);
      });
      world.appendChild(c0); lay();
      Object.keys(used).forEach(function (t) { var l = h('span', 'a4-lg'); var sw = h('i'); sw.style.background = used[t][0]; l.appendChild(sw); l.appendChild(D.createTextNode(TL[t] || 'Co-apparizioni in comune')); leg.appendChild(l); });
      if (!N) leg.appendChild(h('p', 'empty', 'Nessuna relazione da mostrare con i filtri attuali. Prova ad attivare le co-apparizioni o le associazioni editoriali.'));
      var shownN = sel.length; list.appendChild(h('p', 'a3-note', shownN + ' collegamenti mostrati su ' + all.length + ' disponibili. Le co-apparizioni (apparizioni condivise) non sono relazioni narrative; le associazioni editoriali non sono considerate nei percorsi narrativi.'));
      sel.forEach(function (e) {
        var r = h('div', 'a4-r'); r.appendChild(btn('chip', nm(e.id), function () { go(e.id); })); var ls = h('div', 'a4-rls');
        e.rels.forEach(function (z) {
          var row = h('div', 'a4-rl1'), lab = z.cl === 'a' ? 'Co-apparizioni: ' + z.n + ' apparizioni in comune' : (TL[z.t] || z.t) + (z.q ? ' · ' + z.q : '') + (z.cl === 'n' && z.t === 'famiglia_genitore' ? (z.d ? ' (verso il figlio)' : ' (dal genitore)') : '');
          row.appendChild(h('span', 's', lab)); row.appendChild(h('small', 'a4-v v' + z.v, z.cl === 'a' ? 'Calcolata' : VL[z.v])); ls.appendChild(row);
        });
        if (e.more && e.more.length) ls.appendChild(h('div', 'a4-more', 'Anche (non narrative): ' + e.more.map(function (t) { return TL[t] || t; }).join(', ')));
        r.appendChild(ls); list.appendChild(r);
      });
    }
    load(draw);
  }
  /* ---------- PERCORSO ---------- */
  function bfs(a, b, M, V, block) {
    var q = [a], prev = {}; prev[a] = null; var cof = M !== 'n';
    while (q.length) {
      var u = q.shift(); if (u === b) break;
      var nb = [];
      (ADJ[u] || []).forEach(function (e) { var r = G.r[e[0]]; if (r[3] === 'e' || (M === 'a')) return; if (r[4] < V) return; nb.push([e[1], { i: e[0], k: 'r' }]); });
      if (cof && G.coN[u]) G.coN[u].forEach(function (c) { if (c[1] >= (G.coT || 1)) nb.push([c[0], { k: 'a', n: c[1] }]); });
      nb.forEach(function (x) { if (x[0] in prev) return; var ek = u < x[0] ? u + '|' + x[0] : x[0] + '|' + u; if (block && block[ek]) return; prev[x[0]] = [u, x[1]]; q.push(x[0]); });
    }
    if (!(b in prev)) return null; var path = [], cur = b; while (prev[cur]) { path.unshift({ id: cur, e: prev[cur][1], from: prev[cur][0] }); cur = prev[cur][0]; } path.unshift({ id: a }); return path;
  }
  function renderPc() {
    C.frame(); var s = C.A3(); s.m = s.m || 'n'; if (s.doc === undefined) s.doc = 1; C.api.setTitle('Percorso', 'tra due identità'); var root = h('div', 'a4-root'); C.body.appendChild(root);
    root.appendChild(tabsPc('pc'));
    root.appendChild(h('p', 'a3-note', 'Il percorso usa solo collegamenti presenti nel registro. Narrativo: relazioni e controparti documentate; nessuna associazione editoriale. Per impostazione predefinita le relazioni non verificate sono escluse.'));
    var fa = h('div', 'a4-ab'), fb = h('div', 'a4-ab'); root.appendChild(h('label', 'soft', 'Da')); root.appendChild(fa); root.appendChild(h('label', 'soft', 'A')); root.appendChild(fb);
    var la = h('p', 'a4-sel', s.a ? nm(s.a) : 'Nessuna selezione'), lb = h('p', 'a4-sel', s.b ? nm(s.b) : 'Nessuna selezione');
    var ia = pickList(fa, function (i) { s.a = i; la.textContent = nm(i); run(); }, 'Identità di partenza'), ib = pickList(fb, function (i) { s.b = i; lb.textContent = nm(i); run(); }, 'Identità di arrivo'); fa.appendChild(la); fb.appendChild(lb);
    var sw = btn('chip a4-swap', '⇅ Inverti partenza e arrivo', function () { var t = s.a; s.a = s.b; s.b = t; renderPc(); }, { 'aria-label': 'Inverti partenza e arrivo' }); sw.disabled = !(s.a || s.b); root.appendChild(sw);
    var md = h('div', 'a4-tools'); [['n', 'Narrativo'], ['a', 'Co-apparizioni'], ['x', 'Misto']].forEach(function (x) { var k = x[0] === 'a' ? 'c' : x[0]; md.appendChild(btn('chip' + (s.m === x[0] || (x[0] === 'x' && s.m === 'mix') ? ' on' : ''), x[1], function () { s.m = x[0] === 'x' ? 'mix' : x[0] === 'a' ? 'co' : 'n'; renderPc(); })); });
    md.appendChild(btn('chip' + (s.doc ? '' : ' on'), 'Includi non verificate', function () { s.doc = s.doc ? 0 : 1; renderPc(); }, { title: 'Di default sono escluse' }));
    var nA = (s.m !== 'n' ? 1 : 0) + (s.doc ? 0 : 1), fbp = btn('chip a4-fbtn' + (nA ? ' on' : ''), 'Filtri' + (nA ? ' · ' + nA : '') + (s.fo ? ' ▴' : ' ▾'), function () { s.fo = !s.fo; md.hidden = !s.fo; fbp.textContent = 'Filtri' + (nA ? ' · ' + nA : '') + (s.fo ? ' ▴' : ' ▾'); fbp.setAttribute('aria-expanded', s.fo ? 'true' : 'false'); }, { 'aria-expanded': s.fo ? 'true' : 'false' }); md.hidden = !s.fo; root.appendChild(fbp); root.appendChild(md);
    var out = h('div', 'a4-out'); root.appendChild(out);
    function step(p) {
      var d = h('div', 'a4-step'); var un = BY[p.id] && BY[p.id].u ? C.uniNome(BY[p.id].u) : ''; var ch = btn('chip', nm(p.id), function () { s.c = p.id; C.api.nav('a3', { a3: { v: 'nx', c: p.id } }); }, { 'aria-label': nm(p.id) + (un ? ', ' + un : '') + ': apri nel TVA Nexus' }); d.appendChild(ch); if (un) d.appendChild(h('small', 'soft a4-un', un));
      if (p.e) { var r = p.e.k === 'r' ? G.r[p.e.i] : null; var txt = p.e.k === 'a' ? 'Co-apparizioni: ' + p.e.n + ' apparizioni in comune (non è una relazione narrativa)' : (TL[G.tipi[r[2]]] || '') + ' · ' + VL[r[4]]; d.insertBefore(h('span', 'a4-e' + (p.e.k === 'a' ? ' ca' : ''), '↓ ' + txt + (p.e.k === 'r' && r[0] === p.from ? ' (' + nm(p.from) + ' → ' + nm(p.id) + ')' : '')), d.firstChild); }
      return d;
    }
    function run() {
      out.textContent = ''; if (!G) return; if (!s.a || !s.b) { out.appendChild(h('p', 'empty', 'Scegli due voci per vedere il percorso.')); return; } if (s.a === s.b) { out.appendChild(h('p', 'empty', 'Partenza e arrivo coincidono.')); return; }
      var M = s.m === 'co' ? 'a' : s.m === 'mix' ? 'x' : 'n', V = s.doc ? 1 : 0, mode = M === 'a' ? 'co' : M === 'x' ? 'mix' : 'n';
      function search(block) { if (mode === 'co') { var q = [s.a], pr = {}; pr[s.a] = null; while (q.length) { var u = q.shift(); if (u === s.b) break; (G.coN[u] || []).forEach(function (c) { var ek = u < c[0] ? u + '|' + c[0] : c[0] + '|' + u; if (c[0] in pr || (block && block[ek])) return; pr[c[0]] = [u, { k: 'a', n: c[1] }]; q.push(c[0]); }); } if (!(s.b in pr)) return null; var p = [], cur = s.b; while (pr[cur]) { p.unshift({ id: cur, e: pr[cur][1], from: pr[cur][0] }); cur = pr[cur][0]; } p.unshift({ id: s.a }); return p; } return bfs(s.a, s.b, mode === 'mix' ? 'x' : 'n', V, block); }
      var first = search(null); if (!first) { out.appendChild(h('p', 'empty', 'Nessun percorso documentato' + (V ? '' : '') + ' tra «' + nm(s.a) + '» e «' + nm(s.b) + '» con le regole scelte. Nessun collegamento viene inventato.' + (V ? ' Puoi includere le relazioni non verificate.' : ''))); return; }
      var paths = [first], sigs = {}; sigs[first.map(function (x) { return x.id; }).join('>')] = 1;
      for (var i = 1; i < first.length && paths.length < 3; i++) { var bl = {}, a1 = first[i - 1].id, b1 = first[i].id; bl[a1 < b1 ? a1 + '|' + b1 : b1 + '|' + a1] = 1; var alt = search(bl); if (alt) { var sg = alt.map(function (x) { return x.id; }).join('>'); if (!sigs[sg]) { sigs[sg] = 1; paths.push(alt); } } }
      paths.forEach(function (p, k) { var card = h('section', 'a4-path'); card.appendChild(h('h3', '', (k ? 'Alternativa ' + k : 'Percorso più breve') + ' · ' + (p.length - 1) + (p.length === 2 ? ' passo' : ' passi'))); p.forEach(function (x) { card.appendChild(step(x)); }); card.appendChild(btn('btn ghost a4-opn', 'Apri nel TVA Nexus', function () { C.api.nav('a3', { a3: { v: 'nx', c: p[0].id } }); })); out.appendChild(card); });
    }
    load(run);
  }

  /* ---------- CONFRONTO TRA UNIVERSI (A4.3) ---------- */
  function tabsPc(cur) {
    var t = h('div', 'a4-tabs'); t.setAttribute('role', 'tablist');
    [['pc', 'Percorso tra identità'], ['cp', 'Confronto tra universi']].forEach(function (x) {
      var b = btn('chip' + (cur === x[0] ? ' on' : ''), x[1], function () { if (cur !== x[0]) C.api.nav('a3', { a3: x[0] === 'cp' ? { v: 'cp', ua: C.A3().ua || '', ub: C.A3().ub || '' } : { v: 'pc', a: C.A3().a || '', b: C.A3().b || '', m: 'n' } }); }, { role: 'tab', 'aria-selected': cur === x[0] ? 'true' : 'false' }); t.appendChild(b);
    }); return t;
  }
  function titName(n) { var FV = W.marvelIdDaNumeroVisibile, e = W.tvaIdx && W.tvaIdx.titoli && W.tvaIdx.titoli['item-' + (FV ? FV(n) : n)]; return (e && e.title) || ''; }
  function renderCp() {
    C.frame(); var s = C.A3(); C.api.setTitle('Confronto', 'tra due universi'); var root = h('div', 'a4-root'); C.body.appendChild(root); root.appendChild(tabsPc('cp'));
    root.appendChild(h('p', 'a3-note', 'Il confronto usa solo dati del registro: titoli in comune dalla mappa, controparti dichiarate dalle relazioni documentate e identità catalogate in ciascun universo. Nessuna distanza o parentela è inventata; incarnazioni diverse restano distinte.'));
    var us = (C.ORD.U || []).filter(function (v) { return v.k !== 'h'; }), out = h('div', 'a4-out');
    function sel(key, lab) {
      var w = h('label', 'a4-usel'); w.appendChild(h('span', 'soft', lab)); var el = h('select', 'a3-in'); el.setAttribute('aria-label', lab); var o0 = h('option', '', 'Scegli un universo…'); o0.value = ''; el.appendChild(o0);
      us.slice().sort(function (x, y) { return (C.uniNome(x.i) || x.n).localeCompare(C.uniNome(y.i) || y.n, 'it'); }).forEach(function (v) { var o = h('option', '', C.uniNome(v.i) || v.n); o.value = v.i; if (s[key] === v.i) o.selected = true; el.appendChild(o); });
      el.addEventListener('change', function () { s[key] = el.value; run(); }); w.appendChild(el); return w;
    }
    root.appendChild(sel('ua', 'Universo A')); root.appendChild(sel('ub', 'Universo B'));
    root.appendChild(btn('chip a4-swap', '⇅ Inverti A e B', function () { var t = s.ua; s.ua = s.ub; s.ub = t; renderCp(); })); root.appendChild(out);
    function ids(u) { return (C.ORD.p || []).filter(function (v) { return v.u === u; }); }
    function sec(t, n) { var d = h('section', 'a4-path'); d.appendChild(h('h3', '', t + ' · ' + n)); out.appendChild(d); return d; }
    function run() {
      out.textContent = ''; var a = s.ua, b = s.ub; if (!a || !b) { out.appendChild(h('p', 'empty', 'Scegli due universi per confrontarli.')); return; } if (a === b) { out.appendChild(h('p', 'empty', 'Hai scelto lo stesso universo due volte.')); return; }
      if (C.a5) C.a5(function (m) { m.onConfronto(); });
      var ta = G.ut[a] || [], tb = G.ut[b] || [], sh = ta.filter(function (n) { return tb.indexOf(n) >= 0; });
      var ia = ids(a), ib = ids(b), setA = {}, setB = {}; ia.forEach(function (v) { setA[v.i] = 1; }); ib.forEach(function (v) { setB[v.i] = 1; });
      var pairs = G.r.filter(function (r) { return r[3] === 'c' && ((setA[r[0]] && setB[r[1]]) || (setB[r[0]] && setA[r[1]])); }), inPair = {}; pairs.forEach(function (r) { inPair[r[0]] = 1; inPair[r[1]] = 1; });
      var h0 = h('p', 'a3-note', (C.uniNome(a) || nm(a)) + ': ' + ia.length + ' identità · ' + ta.length + ' titoli — ' + (C.uniNome(b) || nm(b)) + ': ' + ib.length + ' identità · ' + tb.length + ' titoli.'); out.appendChild(h0);
      var c1 = sec('Titoli in comune', sh.length); if (!sh.length) c1.appendChild(h('p', 'empty', 'Nessun titolo condiviso nei dati della mappa.')); sh.forEach(function (n) { c1.appendChild(h('div', 'a4-cmpt', 'N°' + n + (titName(n) ? ' · ' + titName(n) : ''))); });
      var c2 = sec('Controparti dichiarate', pairs.length); if (!pairs.length) c2.appendChild(h('p', 'empty', 'Nessuna controparte documentata tra questi due universi.'));
      pairs.forEach(function (r) { var x = setA[r[0]] ? r : [r[1], r[0], r[2], r[3], r[4]]; var d = h('div', 'a4-pair'); d.appendChild(btn('chip', nm(x[0]), function () { C.openId(x[0]); })); d.appendChild(h('span', 'soft', '↔')); d.appendChild(btn('chip', nm(x[1]), function () { C.openId(x[1]); })); d.appendChild(h('small', '', VL[r[4]])); c2.appendChild(d); });
      [[a, ia, 'Solo in '], [b, ib, 'Solo in ']].forEach(function (z) {
        var rest = z[1].filter(function (v) { return !inPair[v.i]; }), c = sec(z[2] + (C.uniNome(z[0]) || nm(z[0])), rest.length); if (!rest.length) c.appendChild(h('p', 'empty', 'Ogni identità ha una controparte documentata.'));
        var g = h('div', 'a3-grid c3'); rest.slice(0, 18).forEach(function (v) { g.appendChild(C.tile(v, true)); }); if (rest.length) c.appendChild(g); if (rest.length > 18) c.appendChild(btn('btn ghost', 'Catalogo dell’universo (' + rest.length + ')', function () { C.api.nav('a3', { a3: { v: 'cat', t: 'p', m: 'c', n: 36, u: z[0] } }); }));
      });
    }
    load(run);
  }
  W.tvaA4 = { mv: renderMv, nx: renderNx, pc: renderPc, cp: renderCp, state: function () { return { g: !!G, rel: G ? G.r.length : 0 }; }, data: function () { return G; } };
  if (W.tvaA4Boot) W.tvaA4Boot();
})();
