/* Atlante 2.0 — A3: Home immersiva, catalogo, ricerca, dossier, hub, mantelli. Caricato SOLO all'ingresso (lazy) dal bootstrap `tva-a3-boot`.
   Dati: atlante2/data/index.json (indice leggero) + atlante2/data/d/NNN.json (shard dei dossier, uno alla volta).
   Nessun HTML dai dati: tutto testo (textContent). Navigazione: stack/Indietro/X e scroll dell'Atlante esistente (stato in ST.a3). */
(function () {
  'use strict';
  var W = window, D = document, A = W.tvaAtlas2, X = A && A.ext, api = X && X.api;
  if (!api || W.tvaA3) return;
  var ST = api.ST, body = api.body, BASE = 'atlante2/';
  /** @type {{voci:Array<Object>,meta:Object,redirect:Object,lnk:Object}|null} */
  var IDX = null, BY = {}, ORD = {}, SH = {}, LASTKEY = 'tva-a3-last', VKEY = 'tva-a3-vista';
  function vistaPref() { try { var x = W.localStorage.getItem(VKEY); return x === 'g' || x === 'l' ? x : 'c'; } catch (e) { return 'c'; } }
  function vistaSalva(m) { try { W.localStorage.setItem(VKEY, m); } catch (e) {} }
  var COL3 = { p: 1, a: 1 };
  var TYPES = [
    { t: 'p', n: 'Personaggi', s: 'identità, varianti, incarnazioni', img: 'personaggi' }, { t: 'h', n: 'Hub multiversali', s: 'varianti raccolte', img: 'multiverso' },
    { t: 'm', n: 'Mantelli', s: 'titoli passati di mano', img: 'arti_mistiche' }, { t: 'U', n: 'Universi', s: 'continuità e Terre', img: 'universi' },
    { t: 'o', n: 'Organizzazioni', s: 'agenzie e gruppi', img: 'organizzazioni' }, { t: 'a', n: 'Artefatti', s: 'oggetti e reliquie', img: 'artefatti' },
    { t: 'l', n: 'Luoghi', s: 'luoghi narrativi', img: 'luoghi' }, { t: 'P', n: 'Pianeti', s: 'mondi e dimensioni', img: 'luoghi' },
    { t: 'e', n: 'Eventi', s: 'eventi e battaglie', img: 'eventi' }, { t: 't', n: 'Attori', s: 'interpreti', img: 'attori' }];
  var TN = {}; TYPES.forEach(function (x) { TN[x.t] = x; });
  var SING = { p: 'Personaggio', h: 'Hub multiversale', m: 'Mantello', U: 'Universo', o: 'Organizzazione', a: 'Artefatto', l: 'Luogo', P: 'Pianeta', e: 'Evento', t: 'Attore' };
  var KIND = { i: 'Identità', v: 'Variante', c: 'Copia', h: 'Hub', m: 'Mantello', g: '' };
  var PAL = { p: ['#3a2f1c', '#E3C79B'], h: ['#3a1c1e', '#ff5c5f'], m: ['#2c2140', '#b48ae0'], U: ['#10303a', '#4fd0ff'], o: ['#3a2a10', '#F59A23'], a: ['#341a3c', '#d46aff'], l: ['#14283a', '#6fb3d9'], P: ['#143a34', '#9fe0d4'], e: ['#3a2010', '#ff8a3c'], t: ['#3a1c22', '#e9a0a6'] };

  /* ---------- utilità ---------- */
  function h(tag, cls, txt, at) { var n = D.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; if (at) Object.keys(at).forEach(function (k) { n.setAttribute(k, at[k]); }); return n; }
  function btn(cls, txt, fn, at) { var b = h('button', cls, txt, at); b.type = 'button'; if (fn) b.addEventListener('click', fn); return b; }
  function svg(path) { var s = D.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('class', 'ic'); s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('aria-hidden', 'true'); var p = D.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('d', path); s.appendChild(p); return s; }
  var IC = { search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4', grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z', grid3: 'M3 4h4.5v4.5H3zM9.7 4h4.5v4.5H9.7zM16.5 4H21v4.5h-4.5zM3 10h4.5v4.5H3zM9.7 10h4.5v4.5H9.7zM16.5 10H21v4.5h-4.5zM3 16h4.5v4.5H3zM9.7 16h4.5v4.5H9.7zM16.5 16H21v4.5h-4.5z', filter: 'M4 6h16M7 12h10M10 18h4', edit: 'M4 20h4L19 9l-4-4L4 16zM13 7l4 4', list: 'M4 6h16M4 12h16M4 18h16', arrow: 'M9 5l7 7-7 7' };
  function norm(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9 ]+/g, ' ').replace(/\s+/g, ' ').trim(); }
  function hash(s) { var x = 2166136261; for (var i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619); } return x >>> 0; }
  function get(path) { return fetch(BASE + path, { credentials: 'same-origin' }).then(function (r) { if (!r.ok) throw new Error(path + ' ' + r.status); return r.json(); }); }
  function save(k, v) { try { W.localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage non disponibile: nessun effetto */ } }
  function load(k) { try { return JSON.parse(W.localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  /* ritratti privati (A3.1): modulo lazy, archivio locale; nessun effetto se non ci sono ritratti */
  var RITQ = [], RITL = 0;
  function withRit(fn) {
    if (W.tvaRit) return fn(W.tvaRit); RITQ.push(fn); if (RITL) return; RITL = 1;
    var s = D.createElement('script'); s.src = BASE + 'ritratti.js'; s.async = true; s.onload = function () { var q = RITQ.splice(0); q.forEach(function (f) { f(W.tvaRit); }); }; s.onerror = function () { RITL = 0; RITQ.length = 0; }; D.head.appendChild(s);
  }
  function paintRit(el, id, big) { withRit(function (r) { r.paint(el, id, big); }); }
  var PK = null;   // chiavi dei ritratti salvati (id identità), per filtro e contatore
  function loadKeys(cb) { withRit(function (r) { r.ids().then(function (k) { PK = k; cb(k); }, function () { PK = {}; cb(PK); }); }); }
  /* hub e mantelli: composizione dei ritratti delle rispettive varianti/titolari (nessuna immagine nuova: solo i ritratti già salvati dall'utente) */
  function paintAny(el, v, big) {
    if (v.t !== 'h' && v.t !== 'm') return paintRit(el, v.i, big);
    dossier(v.i, function (d) {
      if (!d) return; var mem = (d.membri || []).filter(function (m) { return /^id-/.test(m); }).concat((d.titolari || []).map(function (t) { return t.identita; })).filter(function (m, i, a) { return m && a.indexOf(m) === i; });
      if (!mem.length) return;
      withRit(function (r) { r.ids().then(function (k) {
        var have = mem.filter(function (m) { return k[m]; }).slice(0, 4); if (!have.length || !el.isConnected) return;
        var c = h('div', 'a3-comp n' + have.length); have.forEach(function (m) { var cell = h('span', 'a3-cell'); c.appendChild(cell); r.paint(cell, m, big); });
        var old = el.querySelector('.a3-comp'); if (old) old.remove(); el.appendChild(c); el.classList.add('has-pt');
      }); });
    });
  }
  function A3() { return ST.a3 || (ST.a3 = { v: 'home' }); }
  function ensure(cb) {
    if (IDX) return cb();
    get('data/index.json').then(function (d) {
      IDX = d; d.voci.forEach(function (v) { BY[v.i] = v; (ORD[v.t] = ORD[v.t] || []).push(v); });
      cb();
    }).catch(function () { body.className = 'a2-scroll a3'; body.textContent = ''; body.appendChild(h('div', 'empty', 'Dati dell’Atlante 2.0 non disponibili offline. Puoi usare l’Atlante classico.')); });
  }
  function dossier(id, cb) {
    var v = BY[id]; if (!v) return cb(null);
    if (SH[v.sh]) return cb(SH[v.sh][id] || null);
    get('data/d/' + ('00' + v.sh).slice(-3) + '.json').then(function (b) { SH[v.sh] = b; cb(b[id] || null); }).catch(function () { cb(null); });
  }
  function initials(n) { var w = (n || '').replace(/\(.*?\)/g, ' ').split(/[\s\/\-]+/).map(function (x) { return (x.match(/[A-Za-z0-9À-ÿ]/) || [''])[0]; }).filter(Boolean); var r = w.length > 1 ? w[0] + w[1] : (w[0] || '·'); return r.toUpperCase(); }

  /* ---------- Emblemi originali per le categorie senza ritratto (nessuna iniziale): grafica procedurale deterministica, unica per ogni voce ---------- */
  var NSV = 'http://www.w3.org/2000/svg';
  function S(n, a, par) { var e = D.createElementNS(NSV, n); Object.keys(a || {}).forEach(function (k) { e.setAttribute(k, String(a[k])); }); if (par) par.appendChild(e); return e; }
  function rngOf(seed) { var s = seed >>> 0; return function () { s = (s + 0x6D2B79F5) >>> 0; var x = s; x = Math.imul(x ^ (x >>> 15), x | 1); x ^= x + Math.imul(x ^ (x >>> 7), x | 61); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; }
  function terraNum(v) { var m = v.t === 'U' ? /^Earth-([0-9A-Z]+)\b/.exec(v.n) : null; return m && /\d/.test(m[1]) ? m[1] : null; }
  function emblemGen(v, big) {
    var p = PAL[v.t] || PAL.p, hs = hash(v.i), R = rngOf(hs), s = S('svg', { viewBox: '0 0 160 100', preserveAspectRatio: 'xMidYMid slice', 'class': 'a3-em', 'aria-hidden': 'true' });
    var gid = 'g' + hs.toString(36), defs = S('defs', {}, s), lg = S('linearGradient', { id: gid, x1: 0, y1: 0, x2: 1, y2: 1 }, defs);
    S('stop', { offset: 0, 'stop-color': p[0] }, lg); S('stop', { offset: 1, 'stop-color': '#0e0b08' }, lg); S('rect', { width: 160, height: 100, fill: 'url(#' + gid + ')' }, s);
    var cx = 80, cy = 44, st = { fill: 'none', stroke: p[1], 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
    function ln(a, o) { var q = {}; Object.keys(st).forEach(function (k) { q[k] = st[k]; }); Object.keys(a).forEach(function (k) { q[k] = a[k]; }); return S(o || 'path', q, s); }
    function pt(r, a) { return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    function pt0(x0, y0, r, a) { return [x0 + r * Math.cos(a), y0 + r * Math.sin(a)]; }
    var i, a, q, k, n;
    if (v.t === 'U') {
      var num = terraNum(v);
      for (i = 0; i < 4; i++) ln({ cx: cx, cy: cy, r: 12 + i * 8, 'stroke-opacity': .5 - i * .1, 'stroke-width': 1 }, 'circle');
      if (num) {
        var tx = S('text', { x: cx, y: cy + (num.length > 5 ? 8 : 12), 'text-anchor': 'middle', 'font-family': 'Spectral, Georgia, serif', 'font-weight': 700, 'font-size': num.length > 5 ? 26 : num.length > 3 ? 32 : 40, fill: p[1], 'fill-opacity': .92 }, s); tx.textContent = num;
      } else {   // universo senza numerazione documentata: costellazione unica (nessun numero inventato)
        n = 7 + Math.floor(R() * 5); var pts = [];
        for (i = 0; i < n; i++) { a = R() * 6.2832; q = 8 + R() * 28; pts.push(pt(q, a)); }
        for (i = 1; i < n; i++) ln({ d: 'M' + pts[i - 1][0].toFixed(1) + ' ' + pts[i - 1][1].toFixed(1) + 'L' + pts[i][0].toFixed(1) + ' ' + pts[i][1].toFixed(1), 'stroke-opacity': .5, 'stroke-width': 1 });
        pts.forEach(function (c, j) { S('circle', { cx: c[0].toFixed(1), cy: c[1].toFixed(1), r: j === 0 ? 3.6 : 1.8 + R() * 1.4, fill: p[1], 'fill-opacity': j === 0 ? 1 : .8 }, s); });
      }
    } else if (v.t === 'h') {   // hub: una ramificazione con tanti rami quante sono le voci collegate
      n = Math.max(2, Math.min(8, v.a || 3)); var off = R() * 6.28;
      for (i = 0; i < n; i++) { a = off + i * 6.2832 / n; var e1 = pt(30, a), mid = pt(15, a + .35); ln({ d: 'M' + cx + ' ' + cy + 'Q' + mid[0].toFixed(1) + ' ' + mid[1].toFixed(1) + ' ' + e1[0].toFixed(1) + ' ' + e1[1].toFixed(1), 'stroke-width': 1.4 }); S('circle', { cx: e1[0].toFixed(1), cy: e1[1].toFixed(1), r: 3.4, fill: p[1] }, s); }
      S('circle', { cx: cx, cy: cy, r: 6, fill: p[1] }, s); ln({ cx: cx, cy: cy, r: 11, 'stroke-opacity': .6 }, 'circle');
    } else if (v.t === 'm') {   // mantello: mantelli sovrapposti e fermaglio
      var w0 = 20 + R() * 8;
      for (i = 0; i < 3; i++) { var w = w0 + i * 7, hh = 22 + i * 6; ln({ d: 'M' + (cx - w) + ' ' + (cy - hh + 4) + 'Q' + cx + ' ' + (cy - hh - 10 + i * 2) + ' ' + (cx + w) + ' ' + (cy - hh + 4) + 'L' + (cx + w * .8) + ' ' + (cy + hh) + 'Q' + cx + ' ' + (cy + hh - 8) + ' ' + (cx - w * .8) + ' ' + (cy + hh) + 'Z', 'stroke-opacity': .85 - i * .22, 'stroke-width': 1.3 }); }
      S('circle', { cx: cx, cy: cy - 22, r: 4, fill: p[1] }, s);
    } else if (v.t === 'a') {   // artefatto: sigillo unico (poligono stellato ruotato, anello, cuore interno, tacche)
      n = 5 + Math.floor(R() * 5); k = 2 + Math.floor(R() * Math.max(1, (n - 3) / 2)); if (n % k === 0) k = (k % 2) ? 2 : 3; if (n % k === 0) k = 1; var rot = R() * 6.2832, d = '', n2 = 3 + Math.floor(R() * 4), r2 = 8 + R() * 8, dash = R() > .55;
      for (i = 0; i <= n; i++) { q = pt(30 - R() * 2, rot + (i * k % n) * 6.2832 / n); d += (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1); }
      ln({ d: d + 'Z', 'stroke-width': 1.2 + R() * .8 }); ln({ cx: cx, cy: cy, r: 33, 'stroke-opacity': .6, 'stroke-dasharray': dash ? '2 3' : '0' }, 'circle');
      d = ''; for (i = 0; i <= n2; i++) { q = pt(r2, rot * 2 + i * 6.2832 / n2); d += (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1); } ln({ d: d + 'Z', 'stroke-opacity': .8 });
      var tk = 6 + Math.floor(R() * 14); for (i = 0; i < tk; i++) { var q0 = pt(33, i * 6.2832 / tk), q1 = pt(33 + 3 + R() * 3, i * 6.2832 / tk); ln({ d: 'M' + q0[0].toFixed(1) + ' ' + q0[1].toFixed(1) + 'L' + q1[0].toFixed(1) + ' ' + q1[1].toFixed(1), 'stroke-opacity': .7 }); }
      S('circle', { cx: cx, cy: cy, r: 1.8 + R() * 1.6, fill: p[1] }, s);
    } else if (v.t === 'o') {   // organizzazione: scudo (4 sagome) con partizione (6) e figura (5) uniche
      var sw = 22 + R() * 6, sk = Math.floor(R() * 3), top = cy - 30, bot = cy + 34, sh;
      if (sk === 0) sh = 'M' + (cx - sw) + ' ' + top + 'H' + (cx + sw) + 'V' + (cy + 4) + 'Q' + (cx + sw) + ' ' + (cy + 24) + ' ' + cx + ' ' + bot + 'Q' + (cx - sw) + ' ' + (cy + 24) + ' ' + (cx - sw) + ' ' + (cy + 4) + 'Z';
      else if (sk === 1) sh = 'M' + (cx - sw) + ' ' + (top + 4) + 'Q' + cx + ' ' + (top - 6) + ' ' + (cx + sw) + ' ' + (top + 4) + 'V' + (cy + 8) + 'L' + cx + ' ' + bot + 'L' + (cx - sw) + ' ' + (cy + 8) + 'Z';
      else sh = 'M' + (cx - sw) + ' ' + top + 'H' + (cx + sw) + 'V' + (cy + 10) + 'Q' + (cx + sw) + ' ' + (bot) + ' ' + cx + ' ' + bot + 'Q' + (cx - sw) + ' ' + (bot) + ' ' + (cx - sw) + ' ' + (cy + 10) + 'Z';
      ln({ d: sh, 'stroke-width': 1.8 }); k = Math.floor(R() * 6); var X0 = cx - sw, X1 = cx + sw;
      if (k === 0) ln({ d: 'M' + cx + ' ' + top + 'V' + bot + 'M' + X0 + ' ' + (cy - 6) + 'H' + X1 }); else if (k === 1) ln({ d: 'M' + X0 + ' ' + (cy - 14) + 'L' + cx + ' ' + (cy + 4) + 'L' + X1 + ' ' + (cy - 14) }); else if (k === 2) ln({ d: 'M' + X0 + ' ' + top + 'L' + X1 + ' ' + (cy + 12) }); else if (k === 3) ln({ d: 'M' + X0 + ' ' + (cy - 8) + 'H' + X1 }); else if (k === 4) ln({ d: 'M' + X0 + ' ' + (cy + 12) + 'L' + cx + ' ' + (cy - 10) + 'L' + X1 + ' ' + (cy + 12) }); else ln({ d: 'M' + (cx - sw / 3) + ' ' + top + 'V' + bot + 'M' + (cx + sw / 3) + ' ' + top + 'V' + bot });
      var ch = Math.floor(R() * 5), my = cy - 4 + R() * 6;
      if (ch === 0) S('circle', { cx: cx, cy: my, r: 6, fill: p[1], 'fill-opacity': .85 }, s);
      else if (ch === 1) { var dd = ''; for (i = 0; i < 10; i++) { q = pt0(cx, my, i % 2 ? 3 : 7, -1.5708 + i * .6283); dd += (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1); } S('path', { d: dd + 'Z', fill: p[1], 'fill-opacity': .85 }, s); }
      else if (ch === 2) S('path', { d: 'M' + cx + ' ' + (my - 7) + 'L' + (cx + 6) + ' ' + my + 'L' + cx + ' ' + (my + 7) + 'L' + (cx - 6) + ' ' + my + 'Z', fill: p[1], 'fill-opacity': .85 }, s);
      else if (ch === 3) S('path', { d: 'M' + cx + ' ' + (my - 7) + 'L' + (cx + 7) + ' ' + (my + 6) + 'H' + (cx - 7) + 'Z', fill: p[1], 'fill-opacity': .85 }, s);
      else { ln({ cx: cx, cy: my, r: 7 }, 'circle'); S('circle', { cx: cx, cy: my, r: 2.6, fill: p[1] }, s); }
    } else if (v.t === 'l') {   // luogo: curve di livello uniche
      n = 5; var ph = [R() * 6.28, R() * 6.28, R() * 6.28], am = [.12 + R() * .1, .08 + R() * .08, .05 + R() * .05];
      for (i = 0; i < n; i++) { var rr = 8 + i * 6.5, dd = ''; for (var j = 0; j <= 48; j++) { a = j * 6.2832 / 48; var w2 = rr * (1 + am[0] * Math.sin(2 * a + ph[0]) + am[1] * Math.sin(3 * a + ph[1]) + am[2] * Math.sin(5 * a + ph[2])); q = pt(w2, a); dd += (j ? 'L' : 'M') + q[0].toFixed(1) + ' ' + (cy + (q[1] - cy) * .85).toFixed(1); } ln({ d: dd + 'Z', 'stroke-opacity': .85 - i * .12, 'stroke-width': 1.2 }); }
      S('circle', { cx: cx + (R() - .5) * 8, cy: cy + (R() - .5) * 6, r: 2.4, fill: p[1] }, s);
    } else if (v.t === 'P') {   // pianeta: sfera con fasce e, a volte, anello e luna
      var cp = S('clipPath', { id: gid + 'c' }, defs); S('circle', { cx: cx, cy: cy, r: 26 }, cp); S('circle', { cx: cx, cy: cy, r: 26, fill: p[1], 'fill-opacity': .22 }, s);
      var g2 = S('g', { 'clip-path': 'url(#' + gid + 'c)' }, s); n = 3 + Math.floor(R() * 3);
      for (i = 0; i < n; i++) { var by = cy - 20 + R() * 40; S('path', { d: 'M' + (cx - 30) + ' ' + by.toFixed(1) + 'Q' + cx + ' ' + (by + 4 + R() * 6).toFixed(1) + ' ' + (cx + 30) + ' ' + by.toFixed(1), fill: 'none', stroke: p[1], 'stroke-opacity': .35 + R() * .4, 'stroke-width': 2 + R() * 3 }, g2); }
      S('circle', { cx: cx - 8, cy: cy - 8, r: 26, fill: 'none', stroke: '#0e0b08', 'stroke-opacity': .0 }, s); ln({ cx: cx, cy: cy, r: 26, 'stroke-width': 1.4 }, 'circle');
      if (R() > .4) ln({ d: 'M' + (cx - 42) + ' ' + (cy + 6) + 'Q' + cx + ' ' + (cy + 20) + ' ' + (cx + 42) + ' ' + (cy - 6), 'stroke-opacity': .7, 'stroke-width': 1.6 });
      q = pt(36, R() * 6.28); S('circle', { cx: q[0].toFixed(1), cy: q[1].toFixed(1), r: 3, fill: p[1] }, s);
    } else if (v.t === 'e') {   // evento: esplosione di raggi
      n = 14 + Math.floor(R() * 8); for (i = 0; i < n; i++) { a = i * 6.2832 / n + R() * .1; var r0 = 9 + R() * 4, r1 = 20 + R() * 20, p0 = pt(r0, a), p1 = pt(r1, a); ln({ d: 'M' + p0[0].toFixed(1) + ' ' + p0[1].toFixed(1) + 'L' + p1[0].toFixed(1) + ' ' + p1[1].toFixed(1), 'stroke-width': 1 + R() * 1.4, 'stroke-opacity': .9 - R() * .4 }); }
      S('circle', { cx: cx, cy: cy, r: 5, fill: p[1] }, s); ln({ cx: cx, cy: cy, r: 8, 'stroke-opacity': .6 }, 'circle');
    }
    return s;
  }
  function emblem(v, big) {
    if (v.t !== 'p' && v.t !== 't') return emblemGen(v, big);
    var p = PAL[v.t] || PAL.p, hs = hash(v.i), a = hs % 360, ini = initials(v.n);
    var ns = 'http://www.w3.org/2000/svg', s = D.createElementNS(ns, 'svg'); s.setAttribute('viewBox', '0 0 120 160'); s.setAttribute('preserveAspectRatio', 'xMidYMid slice'); s.setAttribute('class', 'a3-em'); s.setAttribute('aria-hidden', 'true');
    var gid = 'g' + hs.toString(36), defs = D.createElementNS(ns, 'defs'), lg = D.createElementNS(ns, 'linearGradient'); lg.setAttribute('id', gid); lg.setAttribute('x1', '0'); lg.setAttribute('y1', '0'); lg.setAttribute('x2', '1'); lg.setAttribute('y2', '1');
    [['0', p[0]], ['1', '#0e0b08']].forEach(function (st) { var e = D.createElementNS(ns, 'stop'); e.setAttribute('offset', st[0]); e.setAttribute('stop-color', st[1]); lg.appendChild(e); }); defs.appendChild(lg); s.appendChild(defs);
    var r = D.createElementNS(ns, 'rect'); r.setAttribute('width', '120'); r.setAttribute('height', '160'); r.setAttribute('fill', 'url(#' + gid + ')'); s.appendChild(r);
    for (var i = 0; i < 3; i++) { var c = D.createElementNS(ns, 'circle'); c.setAttribute('cx', String(30 + (hs >> (i * 3)) % 60)); c.setAttribute('cy', String(40 + (hs >> (i * 2 + 1)) % 50)); c.setAttribute('r', String(22 + i * 16)); c.setAttribute('fill', 'none'); c.setAttribute('stroke', p[1]); c.setAttribute('stroke-opacity', String(0.45 - i * 0.12)); s.appendChild(c); }
    var tx = D.createElementNS(ns, 'text'); tx.setAttribute('x', '60'); tx.setAttribute('y', big ? '84' : '78'); tx.setAttribute('text-anchor', 'middle'); tx.setAttribute('font-family', 'Spectral, Georgia, serif'); tx.setAttribute('font-size', '38'); tx.setAttribute('font-weight', '700'); tx.setAttribute('fill', p[1]); tx.setAttribute('fill-opacity', '.85'); tx.textContent = ini; s.appendChild(tx);
    return s;
  }
  function bgImg(el, name, kb) { var im = new Image(); im.onload = function () { el.style.backgroundImage = 'url("' + im.src + '")'; el.classList.add('ld'); }; im.decoding = 'async'; im.src = BASE + 'img/' + name + '.webp'; if (kb) el.classList.add('a3-kb'); }
  function reveal(root) {
    var els = root.querySelectorAll('.rev'); if (!els.length) return;
    if (!('IntersectionObserver' in W)) { Array.prototype.forEach.call(els, function (e) { e.classList.add('in'); }); return; }
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { root: body, rootMargin: '0px 0px -8% 0px' });
    Array.prototype.forEach.call(els, function (e) { io.observe(e); });
  }
  function frame() { body.className = 'a2-scroll a3'; body.textContent = ''; }
  function uniNome(u) { var x = IDX.meta.universi[u]; return x ? x.n.replace(/^Earth-(\w+) — /, 'Terra-$1 · ') : ''; }
  function uniCont(u) { var x = IDX.meta.universi[u]; return x ? x.c : ''; }
  function openId(id, push) {
    var v = BY[id]; if (!v) return false;
    save(LASTKEY, { id: id, n: v.n, t: v.t });
    var p = { v: v.t === 'h' || v.t === 'm' ? 'hub' : 'dos', id: id }; if (push === false) { ST.a3 = p; api.draw(); api.setScroll(0); } else api.nav('a3', { a3: p });
    return true;
  }
  W.tvaA3 = {};
  function resolve(pageId, fromPages) {
    if (!IDX) return null;
    if (fromPages) for (var i = 0; i < fromPages.length; i++) { var k = IDX.lnk[fromPages[i] + '>' + pageId]; if (k && BY[k]) return k; }
    var r = IDX.redirect[pageId]; if (r && BY[r]) return r; return BY[pageId] ? pageId : null;
  }
  function badge(v) { return v.s ? 'In verifica' : (KIND[v.k] || ''); }

  /* ---------- tile / riga ---------- */
  function nk(s) { return norm(String(s || '').replace(/^Earth-/i, 'Terra ')); }
  function shown(v) {   // titolo e sottotitolo senza ripetizioni (il nome completo resta in aria-label e nel dossier)
    var n = v.n, sub = v.u ? uniNome(v.u) : (v.a ? v.a + (v.t === 'h' ? ' voci collegate' : v.t === 'm' ? ' titolari' : ' apparizioni') : '');
    if (v.t === 'U') { var m = /^Earth-[0-9A-Z]+ — (.+)$/.exec(v.n); if (terraNum(v)) { if (m) { n = m[1]; sub = uniCont(v.i) && nk(uniCont(v.i)) !== nk(n) ? uniCont(v.i) : ''; } else { n = uniCont(v.i) || 'Terra ' + terraNum(v); sub = ''; } } else sub = uniCont(v.i) && nk(uniCont(v.i)) !== nk(n) ? uniCont(v.i) : ''; }
    else if (sub && (nk(sub) === nk(n) || nk(n).indexOf(nk(sub)) >= 0)) sub = '';
    return { n: n, s: sub };
  }
  function tile(v, compact) {
    var b = btn('a3-tile t-' + v.t, null, function () { openId(v.i); }, { 'aria-label': v.n + (badge(v) ? ' — ' + badge(v) : '') });
    var em = h('span', 'em'); em.appendChild(emblem(v)); b.appendChild(em); paintAny(em, v, false);
    if (v.s) b.appendChild(h('span', 'bd', badge(v)));
    var sh = shown(v), t = h('span', 't'); t.appendChild(h('b', '', sh.n)); if (sh.s) t.appendChild(h('span', '', sh.s)); b.appendChild(t);
    return b;
  }
  function li(v) {
    var b = btn('a3-li t-' + v.t, null, function () { openId(v.i); });
    var em = h('span', 'em'); em.appendChild(emblem(v)); b.appendChild(em); paintAny(em, v, false);
    var sh = shown(v), t = h('span'); t.appendChild(h('b', '', sh.n)); var sub = (v.t === 'U' ? sh.s : (sh.s || (v.a ? v.a + ' apparizioni' : ''))); if (sub) t.appendChild(h('span', 's', sub)); b.appendChild(t);
    if (v.s) b.appendChild(h('span', 'bd', badge(v)));
    return b;
  }

  /* ---------- HOME ---------- */
  function renderHome() {
    frame(); api.setTitle('Atlante 2.0', 'Anteprima A3');
    var s = A3(), n = IDX.voci.length, np = (ORD.p || []).length, nu = (ORD.U || []).length;
    var hero = h('section', 'a3-hero'); hero.setAttribute('aria-labelledby', 'a3H1');
    var bg = h('div', 'a3-bg'); bgImg(bg, 'home_hero', true); hero.appendChild(bg);
    [[260, 8, 12], [190, 30, 22], [120, 52, 34]].forEach(function (r, i) { var ring = h('i', 'a3-ring' + (i === 1 ? ' a3-spin' : '')); ring.style.cssText = 'width:' + r[0] + 'px;height:' + r[0] + 'px;right:' + (-r[2]) + 'px;top:' + (r[1] + 30) + 'px;opacity:' + (0.85 - i * 0.2); hero.appendChild(ring); });
    hero.appendChild(h('div', 'a3-tw')); hero.appendChild(h('div', 'a3-fade'));
    var t = h('div', 'a3-hero-t'); t.appendChild(h('span', 'kick', 'TVA ARCHIVES · ATLANTE 2.0'));
    var h1 = h('h1', '', 'L’Atlante del Multiverso'); h1.id = 'a3H1'; t.appendChild(h1);
    t.appendChild(h('p', '', 'Identità, varianti e incarnazioni catalogate dalla TVA. Ogni scheda mostra solo ciò che è documentato.'));
    var st = h('ul', 'a3-stats'); [[np, 'identità'], [nu, 'universi'], [n, 'voci in archivio']].forEach(function (x) { var l = h('li'); l.appendChild(h('b', '', String(x[0]))); l.appendChild(D.createTextNode(x[1])); st.appendChild(l); }); t.appendChild(st);
    var sb = btn('a3-sbar', null, function () { api.nav('a3', { a3: { v: 'search', q: '' } }); }, { 'aria-label': 'Cerca nell’Atlante' }); sb.appendChild(svg(IC.search)); sb.appendChild(h('span', '', 'Cerca personaggi, universi, luoghi…')); t.appendChild(sb);
    var row = h('div', 'a3-row'); row.appendChild(btn('btn fill', 'Esplora il catalogo', function () { api.nav('a3', { a3: { v: 'cat', t: 'p', m: vistaPref(), n: 36 } }); }));
    row.appendChild(btn('btn ghost', 'Atlante classico', function () { W.__a3Classic = true; A.openHome(); })); t.appendChild(row);
    hero.appendChild(t); body.appendChild(hero);
    var last = load(LASTKEY);
    if (last && BY[last.id]) { var rs = btn('a3-resume rev t-' + last.t, null, function () { openId(last.id); }); var em = h('span', 'em'); em.style.cssText = 'width:48px;height:48px;border-radius:12px;overflow:hidden;flex:none'; em.appendChild(emblem(BY[last.id])); rs.appendChild(em); var tx = h('span'); tx.appendChild(h('small', 'kick', 'Riprendi da dove eri')); tx.appendChild(h('b', '', BY[last.id].n)); rs.appendChild(tx); body.appendChild(rs); }
    // dossier in evidenza: sceglie tra le identità con più apparizioni, a rotazione giornaliera (nessun contenuto inventato)
    var top = (ORD.p || []).filter(function (v) { return !v.s; }).sort(function (a, b) { return b.a - a.a || (a.i < b.i ? -1 : 1); }).slice(0, 24);
    if (top.length) {
      var f = top[Math.floor(Date.now() / 86400000) % top.length], sec = h('section', 'a3-sec'); var hd = h('header'); hd.appendChild(h('h2', '', 'Dossier in evidenza')); hd.appendChild(h('p', '', 'A rotazione tra le identità con più apparizioni.')); sec.appendChild(hd);
      var fb = btn('a3-feat rev t-' + f.t, null, function () { openId(f.i); }); var fe = h('span', 'em'); fe.appendChild(emblem(f)); fb.appendChild(fe); fb.appendChild(h('span', 'kick', badge(f) || 'Identità')); fb.appendChild(h('h3', '', f.n)); fb.appendChild(h('p', '', (f.u ? uniNome(f.u) + ' · ' : '') + f.a + ' apparizioni')); sec.appendChild(fb); body.appendChild(sec);
    }
    var sc = h('section', 'a3-sec'); var hc = h('header'); hc.appendChild(h('h2', '', 'Categorie')); hc.appendChild(h('p', '', 'Un archivio, dieci modi di entrarci.')); sc.appendChild(hc);
    var rail = h('div', 'a3-rail'); TYPES.forEach(function (x) {
      var cnt = (ORD[x.t] || []).length; if (!cnt) return; var c = btn('a3-cat rev t-' + x.t, null, function () { api.nav('a3', { a3: { v: 'cat', t: x.t, m: vistaPref(), n: 36 } }); }, { 'aria-label': x.n + ', ' + cnt });
      bgImg(c, x.img, false); var tt = h('span', 't'); tt.appendChild(h('b', '', x.n)); tt.appendChild(h('span', '', cnt + ' · ' + x.s)); c.appendChild(tt); rail.appendChild(c);
    }); sc.appendChild(rail); body.appendChild(sc);
    var hubs = (ORD.h || []); if (hubs.length) {
      var sh = h('section', 'a3-sec'); var hh = h('header'); hh.appendChild(h('h2', '', 'Hub multiversali')); hh.appendChild(h('p', '', 'Una pagina per ogni personaggio che vive in più continuità. Nessuna parentela narrativa è attribuita senza fonte.')); sh.appendChild(hh);
      var hw = h('div', 'a3-hubs'); hubs.forEach(function (v) { var c = btn('a3-hc rev t-h', null, function () { openId(v.i); }); c.appendChild(h('span', 'kick', 'Hub')); c.appendChild(h('b', '', v.n)); c.appendChild(h('span', 'soft', v.a + ' voci collegate')); hw.appendChild(c); }); sh.appendChild(hw); body.appendChild(sh);
    }
    body.appendChild(btn('a3-ritlink', 'Ritratti privati — pilota A3.1: scene, importazione, esportazione', function () { api.nav('a3', { a3: { v: 'rit' } }); }));
    body.appendChild(h('p', 'a3-note', 'Anteprima A3 in collaudo: l’Atlante classico resta disponibile e invariato. I ritratti specifici compariranno solo quando disponibili e utilizzabili; fino ad allora ogni voce mostra un emblema. Fonti: registro dati dell’Atlante e fonti secondarie dichiarate nella scheda.'));
    reveal(body); parallax(bg);
  }
  function parallax(el) {
    if (!el || (W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches)) return; var tk = false;
    body.onscroll = function () { if (tk) return; tk = true; requestAnimationFrame(function () { tk = false; var y = body.scrollTop; if (y < 600) el.style.translate = '0 ' + Math.round(y * 0.25) + 'px'; }); };
  }

  /* ---------- CATALOGO ---------- */
  function filtered(s) {
    var q = norm(s.q || ''), toks = q ? q.split(' ') : [];
    return (ORD[s.t] || []).filter(function (v) {
      if (s.u && v.u !== s.u) return false; if (s.c && uniCont(v.u) !== s.c) return false; if (s.r && PK && PK[v.i]) return false;
      for (var i = 0; i < toks.length; i++) if (v.q.indexOf(toks[i]) < 0) return false; return true;
    });
  }
  function renderCat() {
    frame(); var s = A3(); s.t = s.t || 'p'; s.m = s.m && s.m !== 'g0' ? s.m : vistaPref(); s.n = s.n || 36; api.setTitle('Catalogo', TN[s.t].n);
    var tools = h('div', 'a3-tools'); var chips = h('div', 'chips'); chips.setAttribute('role', 'tablist');
    TYPES.forEach(function (x) { var c = (ORD[x.t] || []).length; if (!c) return; var b = btn('chip t-' + x.t + (x.t === s.t ? ' on' : ''), x.n, function () { ST.a3 = { v: 'cat', t: x.t, m: s.m, n: 36, q: '', u: '', c: '' }; api.draw(); api.setScroll(0); }, { role: 'tab', 'aria-selected': x.t === s.t ? 'true' : 'false' }); b.appendChild(h('small', '', String(c))); chips.appendChild(b); });
    tools.appendChild(chips);
    var l1 = h('div', 'line'); var inp = h('input', 'a3-in'); inp.type = 'search'; inp.placeholder = 'Filtra in ' + TN[s.t].n.toLowerCase(); inp.value = s.q || ''; inp.setAttribute('aria-label', 'Filtra'); inp.setAttribute('autocomplete', 'off');
    var tm; inp.addEventListener('input', function () { clearTimeout(tm); tm = setTimeout(function () { s.q = inp.value; s.n = 36; listOnly(); }, 120); });
    l1.appendChild(inp);
    var base = (ORD[s.t] || []), us = {}, cs = {}; base.forEach(function (v) { if (v.u) { us[v.u] = (us[v.u] || 0) + 1; var c = uniCont(v.u); if (c) cs[c] = (cs[c] || 0) + 1; } });
    var hasF = Object.keys(us).length > 1 || s.t === 'p', fp = null, fb = null;
    function nF() { return (s.u ? 1 : 0) + (s.c ? 1 : 0) + (s.r ? 1 : 0); }
    function fbLabel() { fb.textContent = ''; fb.appendChild(svg(IC.filter)); if (nF()) fb.appendChild(h('i', 'a3-fn', String(nF()))); }
    if (hasF) { fb = btn('a3-fbtn' + (nF() ? ' on' : ''), null, function () { var o = fp.hidden; fp.hidden = !o; fb.setAttribute('aria-expanded', o ? 'true' : 'false'); }, { 'aria-label': 'Filtri', 'aria-expanded': nF() ? 'true' : 'false' }); fbLabel(); l1.appendChild(fb); }
    var seg = h('div', 'a3-seg'); [['c', IC.grid3, 'Griglia compatta'], ['g', IC.grid, 'Griglia grande'], ['l', IC.list, 'Elenco']].forEach(function (m) { var b = btn(s.m === m[0] ? 'on' : '', null, function () { s.m = m[0]; vistaSalva(m[0]); Array.prototype.forEach.call(seg.children, function (x) { x.classList.remove('on'); x.setAttribute('aria-pressed', 'false'); }); b.classList.add('on'); b.setAttribute('aria-pressed', 'true'); listOnly(); }, { 'aria-label': m[2], 'aria-pressed': s.m === m[0] ? 'true' : 'false' }); b.appendChild(svg(m[1])); seg.appendChild(b); }); l1.appendChild(seg); tools.appendChild(l1);
    if (hasF) {
      fp = h('div', 'a3-fpanel'); fp.hidden = !nF(); var su = h('select', 'a3-sel'); su.setAttribute('aria-label', 'Filtra per universo'); su.appendChild(new Option('Tutti gli universi', ''));
      Object.keys(us).sort(function (a, b) { return uniNome(a) < uniNome(b) ? -1 : 1; }).forEach(function (u) { su.appendChild(new Option(uniNome(u) + ' (' + us[u] + ')', u)); }); su.value = s.u || '';
      su.addEventListener('change', function () { s.u = su.value; s.n = 36; fb.classList.toggle('on', !!nF()); fbLabel(); listOnly(); });
      var sc = h('select', 'a3-sel'); sc.setAttribute('aria-label', 'Filtra per continuità'); sc.appendChild(new Option('Tutte le continuità', '')); Object.keys(cs).sort().forEach(function (c) { sc.appendChild(new Option(c + ' (' + cs[c] + ')', c)); }); sc.value = s.c || '';
      sc.addEventListener('change', function () { s.c = sc.value; s.n = 36; fb.classList.toggle('on', !!nF()); fbLabel(); listOnly(); }); if (Object.keys(us).length > 1) { fp.appendChild(su); fp.appendChild(sc); }
      if (s.t === 'p') {
        var rb = btn('a3-seno' + (s.r ? ' on' : ''), 'Solo senza ritratto', function () { s.r = s.r ? '' : 'no'; rb.classList.toggle('on', !!s.r); rb.setAttribute('aria-pressed', s.r ? 'true' : 'false'); s.n = 36; fb.classList.toggle('on', !!nF()); fbLabel(); loadKeys(function () { listOnly(); }); }, { 'aria-pressed': s.r ? 'true' : 'false' }); fp.appendChild(rb);
      }
      tools.appendChild(fp);
    }
    body.appendChild(tools); var cnt = h('div', 'a3-count'); cnt.setAttribute('aria-live', 'polite'); body.appendChild(cnt); var host = h('div'); body.appendChild(host);
    var sent = h('div', 'a3-sent'), io = null;
    function listOnly() {
      var arr = filtered(s), shown = Math.min(s.n, arr.length); host.textContent = '';
      cnt.textContent = arr.length + (arr.length === 1 ? ' voce' : ' voci') + (arr.length !== base.length ? ' su ' + base.length : '') + (s.t === 'p' && PK ? ' · ritratti ' + base.filter(function (v) { return PK[v.i]; }).length + '/' + base.length + ' completati, ' + base.filter(function (v) { return !PK[v.i]; }).length + ' mancanti' : '');
      if (!arr.length) { host.appendChild(h('div', 'empty', 'Nessuna voce corrisponde ai filtri.')); return; }
      var wrap = h('div', s.m === 'l' ? 'a3-list' : 'a3-grid ' + (s.m === 'c' ? (COL3[s.t] ? 'c3' : 'c2') : 'big')); host.appendChild(wrap); fill(wrap, arr, 0, shown);
      if (io) io.disconnect(); if (shown < arr.length) { host.appendChild(sent); observe(wrap, arr); }
    }
    function fill(wrap, arr, a, b) { for (var i = a; i < b; i++) wrap.appendChild(s.m === 'l' ? li(arr[i]) : tile(arr[i], s.m === 'c')); }
    function observe(wrap, arr) {
      function more() { var from = wrap.childElementCount, to = Math.min(from + 36, arr.length); fill(wrap, arr, from, to); s.n = to; if (to >= arr.length) { if (io) io.disconnect(); sent.remove(); } }
      if ('IntersectionObserver' in W) { io = new IntersectionObserver(function (es) { if (es[0].isIntersecting) more(); }, { root: body, rootMargin: '600px' }); io.observe(sent); }
      else { var mb = btn('btn ghost a3-more', 'Mostra altre voci', more); host.appendChild(mb); }
    }
    listOnly(); if (s.t === 'p') loadKeys(function () { listOnly(); });
  }

  /* ---------- RICERCA ---------- */
  function search(q) {
    var toks = norm(q).split(' ').filter(Boolean), res = {}; if (!toks.length) return res;
    IDX.voci.forEach(function (v) {
      var sc = 0; for (var i = 0; i < toks.length; i++) { var p = v.q.indexOf(toks[i]); if (p < 0) { sc = -1; break; } sc += p === 0 ? 3 : (v.q.charAt(p - 1) === ' ' ? 2 : 1); }
      if (sc > 0) (res[v.t] = res[v.t] || []).push([sc, v]);
    });
    Object.keys(res).forEach(function (t) { res[t].sort(function (a, b) { return b[0] - a[0] || (a[1].n < b[1].n ? -1 : 1); }); });
    return res;
  }
  function renderSearch() {
    frame(); var s = A3(); api.setTitle('Ricerca', 'Atlante 2.0');
    var tools = h('div', 'a3-tools'), l = h('div', 'line'), inp = h('input', 'a3-in'); inp.type = 'search'; inp.placeholder = 'Cerca nell’Atlante…'; inp.value = s.q || ''; inp.setAttribute('aria-label', 'Cerca'); inp.setAttribute('autocomplete', 'off'); l.appendChild(inp); tools.appendChild(l); body.appendChild(tools);
    var out = h('div'); body.appendChild(out); var tm;
    function run() {
      s.q = inp.value; out.textContent = ''; var q = norm(s.q); if (!q) { out.appendChild(h('div', 'empty', 'Scrivi un nome, un universo, un interprete…')); return; }
      var r = search(s.q), any = false;
      TYPES.forEach(function (x) {
        var a = r[x.t]; if (!a) return; any = true; var g = h('section', 'a3-sgroup t-' + x.t), hd = h('h3', '', x.n); hd.appendChild(h('small', '', a.length + (a.length === 1 ? ' risultato' : ' risultati'))); g.appendChild(hd);
        var ls = h('div', 'a3-list'); a.slice(0, 5).forEach(function (e) { ls.appendChild(li(e[1])); }); g.appendChild(ls);
        if (a.length > 5) { var m = btn('btn ghost a3-more', 'Mostra tutti (' + a.length + ')', function () { api.nav('a3', { a3: { v: 'cat', t: x.t, m: 'l', n: 36, q: s.q } }); }); g.appendChild(m); } out.appendChild(g);
      });
      if (!any) out.appendChild(h('div', 'empty', 'Nessun risultato per «' + s.q + '».'));
    }
    inp.addEventListener('input', function () { clearTimeout(tm); tm = setTimeout(run, 100); }); run();
    if (!s.q) setTimeout(function () { try { inp.focus(); } catch (e) { /* focus non consentito */ } }, 50);
  }

  /* ---------- DOSSIER ---------- */
  function tokens(host, arr, pages) {
    arr.forEach(function (x) {
      if (typeof x === 'string') { host.appendChild(D.createTextNode(x)); return; }
      var tgt = resolve(x[0], pages), lb = x[2] || x[0];
      if (tgt) host.appendChild(btn('a3-lk', lb, function () { openId(tgt); }, { 'aria-label': 'Apri ' + (BY[tgt] ? BY[tgt].n : lb) })); else host.appendChild(D.createTextNode(lb));
    });
  }
  function ridondanti(sec) {
    var tx = sec.map(function (f) { return norm((f.t || []).map(function (x) { return typeof x === 'string' ? x : ''; }).join(' ')); });
    return sec.filter(function (f, i) { return !tx.some(function (o, j) { return j !== i && tx[i] && (o.length > tx[i].length || (o.length === tx[i].length && j < i)) && o.indexOf(tx[i]) >= 0; }); });
  }
  function kv(sec, host, pages) { ridondanti(sec).forEach(function (f) { var d = h('div', 'a3-kv'); d.appendChild(h('span', 'k', f.l)); var v = h('div', 'v'); tokens(v, f.t, pages); d.appendChild(v); host.appendChild(d); }); }
  function nBtn(n, label, opt) {
    var FV = W.marvelIdDaNumeroVisibile, id = 'item-' + (FV ? FV(n) : n); var ok = !!(W.tvaIdx && W.tvaIdx.titoli && W.tvaIdx.titoli[id]);
    return { id: id, ok: ok };
  }
  function appsBlock(d) {
    var w = h('div', 'a3-apps'); d.app.forEach(function (a) {
      var r = nBtn(a[0]), row = h('div', 'a3-app'); row.appendChild(h('span', 'n', 'N°' + a[0])); row.appendChild(h('span', 'tt', a[1] || 'Titolo non indicato nella scheda'));
      if (r.ok) { row.appendChild(btn('', 'Scheda', function () { W.tvaGo('item', r.id); }, { 'aria-label': 'Apri la scheda di ' + (a[1] || a[0]) })); row.appendChild(btn('', 'Timeline', function () { W.tvaGo('item', r.id, { scheda: true }); }, { 'aria-label': 'Mostra nella Timeline: ' + (a[1] || a[0]) })); }
      w.appendChild(row);
    }); return w;
  }
  function chipsFor(ids, pages) {
    var w = h('div', 'a3-vl'); ids.forEach(function (id) { var v = BY[id]; if (v) w.appendChild(btn('chip t-' + v.t, v.n, function () { openId(id); })); else w.appendChild(h('span', 'chip', 'scheda non ancora disponibile')); }); return w;
  }
  var RELT = { controparte_altra_continuita: 'Controparte in un’altra continuità', variante: 'Variante', alias: 'Alias', clone: 'Clone', copia: 'Copia' };
  function varBlock(d) {
    var w = h('div');
    d.var.forEach(function (x) {
      var b = h('div', 'a3-vb');
      if (x.ruolo === 'hub') { b.appendChild(h('h3', '', 'Hub multiversale: ' + x.n)); b.appendChild(h('p', '', 'Questa identità appartiene a un hub che raccoglie le sue controparti. L’appartenenza all’hub non è una relazione narrativa.')); b.appendChild(btn('chip t-h', 'Apri l’hub', function () { openId(x.id); })); if (x.membri.length) { b.appendChild(h('p', '', 'Altre voci dell’hub')); b.appendChild(chipsFor(x.membri)); } }
      else if (x.ruolo === 'mantello') { b.appendChild(h('h3', '', 'Mantello: ' + x.n)); b.appendChild(h('p', '', 'Titolo portato da più identità distinte: non sono la stessa persona.')); b.appendChild(btn('chip t-m', 'Apri il mantello', function () { openId(x.id); })); if (x.membri.length) b.appendChild(chipsFor(x.membri)); }
      else if (x.ruolo === 'rel') { b.appendChild(h('h3', '', RELT[x.tipo] || x.tipo.replace(/_/g, ' '))); b.appendChild(chipsFor([x.id])); if (x.nota) b.appendChild(h('p', '', x.nota)); if (x.verifica) b.appendChild(h('p', '', 'Verifica: ' + x.verifica)); }
      else if (x.ruolo === 'incarnazioni') {
        b.appendChild(h('h3', '', 'Incarnazioni e interpreti')); b.appendChild(h('p', '', 'Un cambio di interprete o di età non crea una variante multiversale.'));
        x.lista.forEach(function (c) { var r = h('div', 'a3-kv'); r.appendChild(h('span', 'k', c.tipo === 'cambio_attore' ? 'Cambio di interprete' : 'Incarnazione')); var v = h('div', 'v'); v.textContent = [c.e, c.int ? '(' + c.int + ')' : '', c.app && c.app.length ? '· ' + c.app.map(function (n) { return 'N°' + n; }).join(', ') : ''].filter(Boolean).join(' '); r.appendChild(v); if (c.v) r.appendChild(h('span', 'soft', c.v)); b.appendChild(r); });
      }
      w.appendChild(b);
    }); return w;
  }
  function srcBlock(d) {
    var w = h('div', 'a3-src');
    if (d.nota) w.appendChild(h('span', '', 'Nota di catalogo: ' + d.nota));
    if (d.ver) w.appendChild(h('span', '', 'Stato di verifica: ' + d.ver));
    (d.fonti || []).forEach(function (f) { var r = h('span'); if (/^https:\/\//.test(f)) { var a = h('a', '', f, { href: f, target: '_blank', rel: 'noopener noreferrer' }); r.appendChild(a); } else r.textContent = f; w.appendChild(r); });
    var pages = (d.p || []).concat((d.storiche || []).map(function (x) { return x.id; })); var seen = {};
    var ARC = { org: 'org', art: 'art', pia: 'luo', luo: 'luo', evt: 'evt', bat: 'evt' };
    pages.forEach(function (p) {
      if (seen[p]) return; seen[p] = 1; var pre = p.split('-')[0];
      w.appendChild(btn('btn ghost', 'Scheda originale (Atlante classico): ' + p.replace(/^[a-z]+-/, ''), function () {
        if (!W.tvaGo) return; if (pre === 'char' || pre === 'uni' || pre === 'att') W.tvaGo(pre, p); else if (ARC[pre]) W.tvaGo('arc', ARC[pre] + ':' + p);
      }));
    });
    return w;
  }
  function sections(d) {
    var out = [], S = IDX.meta.sezioni;
    S.forEach(function (sd) {
      var k = sd[0], title = sd[1], node = null, host = h('div');
      if (k === 'apparizioni') { if (d.app && d.app.length) host.appendChild(appsBlock(d)); if (d.sec.apparizioni) kv(d.sec.apparizioni, host, d.p); }
      else if (k === 'varianti') { if (d.var) host.appendChild(varBlock(d)); if (d.storiche && d.storiche.length) { var hb = h('div', 'a3-vb'); hb.appendChild(h('h3', '', 'Pagina storica multi-continuità')); hb.appendChild(h('p', '', 'Nell’Atlante classico questa identità compare in una scheda aggregata: i suoi dati non vengono attribuiti a una sola continuità.')); host.appendChild(hb); } }
      else if (k === 'fonti') { if (d.fonti || d.ver || d.nota || (d.p && d.p.length) || (d.storiche && d.storiche.length)) host.appendChild(srcBlock(d)); }
      else if (d.sec[k]) kv(d.sec[k], host, d.p);
      if (host.childNodes.length) out.push({ k: k, t: title, n: host });
    }); return out;
  }
  function renderDossier() {
    frame(); var s = A3(), v = BY[s.id]; if (!v) { body.appendChild(h('div', 'empty', 'Voce non trovata.')); return; }
    api.setTitle(v.n, 'Dossier');
    var root = h('div', 't-' + v.t); body.appendChild(root); var hd = h('header', 'a3-dh'); var em = h('div', 'em'); em.appendChild(emblem(v, true)); hd.appendChild(em); paintAny(em, v, true);
    var t = h('div', 't'); t.appendChild(h('span', 'kick', SING[v.t] || '')); t.appendChild(h('h1', '', v.n));
    var bds = h('div', 'a3-bds'); if (v.s) bds.appendChild(h('span', 'a3-bd warn', badge(v))); if (v.u) { bds.appendChild(h('span', 'a3-bd', uniNome(v.u))); var c = uniCont(v.u); if (c) bds.appendChild(h('span', 'a3-bd', c)); } t.appendChild(bds);
    var rb = btn('a3-ritbtn', null, function () { withRit(function (r) { r.openEditor(v.i, v.n, function (i) { return BY[i] && BY[i].n; }); }); }, { 'aria-label': 'Ritratto privato di ' + v.n, title: 'Ritratto privato' }); rb.appendChild(svg(IC.edit)); hd.appendChild(rb); hd.appendChild(t); root.appendChild(hd); parallax(em);
    var holder = h('div', 'a3-load', 'Caricamento del dossier…'); root.appendChild(holder);
    dossier(s.id, function (d) {
      if (ST.a3 !== s || !root.isConnected) return; holder.remove();
      if (!d) { root.appendChild(h('div', 'empty', 'Dossier non disponibile.')); return; }
      if (v.s) { var w = h('p', 'a3-note', 'Identità in verifica: i dati sono quelli dell’Atlante classico, senza unificazioni né attribuzioni di varianti.'); root.appendChild(w); }
      var secs = sections(d), jump = h('nav', 'a3-jump'); jump.setAttribute('aria-label', 'Sezioni del dossier'); var chips = h('div', 'chips'); var seen = {}, nseen = 0;
      var pr = h('div', 'a3-prog'); var pt = h('span', '', 'Sezioni viste 0/' + secs.length), bar = h('i'); var fill = h('b'); bar.appendChild(fill); pr.appendChild(pt); pr.appendChild(bar);
      secs.forEach(function (sx, i) { chips.appendChild(btn('chip' + (i ? '' : ' on'), sx.t, function () { var e = D.getElementById('a3s-' + sx.k); if (e) body.scrollTo({ top: e.offsetTop - (jump.offsetHeight || 90) + 4, behavior: 'smooth' }); })); });
      if (!secs.length) { root.appendChild(h('div', 'empty', 'Per questa voce non sono ancora disponibili altre informazioni.')); return; }
      jump.appendChild(chips); jump.appendChild(pr); root.appendChild(jump);
      secs.forEach(function (sx) { var sec = h('section', 'a3-ds rev', null, { id: 'a3s-' + sx.k }); sec.appendChild(h('h2', '', sx.t)); sec.appendChild(sx.n); root.appendChild(sec); });
      reveal(root);
      if ('IntersectionObserver' in W) {
        var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { var k = e.target.id; if (!seen[k]) { seen[k] = 1; nseen++; pt.textContent = 'Sezioni viste ' + nseen + '/' + secs.length; fill.style.width = Math.round(nseen / secs.length * 100) + '%'; } var idx = secs.map(function (x) { return 'a3s-' + x.k; }).indexOf(k); Array.prototype.forEach.call(chips.children, function (c, i) { c.classList.toggle('on', i === idx); }); } }); }, { root: body, rootMargin: '-30% 0px -60% 0px' });
        Array.prototype.forEach.call(root.querySelectorAll('.a3-ds'), function (e) { io.observe(e); });
      }
    });
  }

  /* ---------- HUB / MANTELLO ---------- */
  function renderHub() {
    frame(); var s = A3(), v = BY[s.id]; if (!v) { body.appendChild(h('div', 'empty', 'Voce non trovata.')); return; }
    api.setTitle(v.n, v.t === 'h' ? 'Hub multiversale' : 'Mantello');
    var root = h('div', 't-' + v.t); body.appendChild(root); var hd = h('header', 'a3-dh'); var em = h('div', 'em'); em.appendChild(emblem(v, true)); hd.appendChild(em); paintAny(em, v, true);
    var t = h('div', 't'); t.appendChild(h('span', 'kick', v.t === 'h' ? 'Hub multiversale' : 'Mantello')); t.appendChild(h('h1', '', v.n)); hd.appendChild(t); root.appendChild(hd);
    var holder = h('div', 'a3-load', 'Caricamento…'); root.appendChild(holder);
    dossier(s.id, function (d) {
      if (ST.a3 !== s || !root.isConnected) return; holder.remove();
      if (!d) { root.appendChild(h('div', 'empty', 'Dossier non disponibile.')); return; }
      var note = h('p', 'a3-note', v.t === 'h' ? 'L’hub non è un personaggio e non aggiunge relazioni narrative: raccoglie le identità che condividono il nome. Le co-apparizioni non sono relazioni.' : 'Un mantello è un titolo: i suoi titolari sono identità distinte e non vengono unificate.'); root.appendChild(note);
      var ids = (v.t === 'h' ? d.membri : d.titolari.map(function (x) { return x.identita; })).slice(); if (v.t === 'h') ids.sort(function (a, b) { return (BY[a] ? 0 : 1) - (BY[b] ? 0 : 1); });
      var wrap = h('div', 'a3-hubs'); root.appendChild(wrap);
      ids.forEach(function (id, i) {
        var m = BY[id], c = m ? btn('a3-hc rev t-' + m.t, null, function () { openId(id); }) : h('div', 'a3-hc off');
        if (v.t === 'm') c.appendChild(h('span', 'kick', (i + 1) + '° titolare')); c.appendChild(h('b', '', m ? m.n : 'Scheda non ancora disponibile'));
        if (m) { c.appendChild(h('span', 'soft', (m.u ? uniNome(m.u) + ' · ' : '') + m.a + ' apparizioni')); var line = h('span', 'soft'); c.appendChild(line); dossier(id, function (dd) { if (!dd) return; var idf = (dd.sec.identita || []).filter(function (f) { return f.l === 'Interpreti'; })[0]; if (idf) line.textContent = 'Interprete: ' + idf.t.join(''); }); }
        else c.appendChild(h('span', 'soft', 'Segnaposto previsto, nessun dato verificato.'));
        wrap.appendChild(c);
      });
      if (d.esclusi && Object.keys(d.esclusi).length) { var ex = h('section', 'a3-ds'); ex.appendChild(h('h2', '', 'Da non confondere')); Object.keys(d.esclusi).forEach(function (k) { var kvd = h('div', 'a3-kv'); kvd.appendChild(h('span', 'k', k.replace(/^char-/, '').replace(/-/g, ' '))); kvd.appendChild(h('div', 'v', d.esclusi[k])); ex.appendChild(kvd); }); root.appendChild(ex); }
      if (d.ver) { var vs = h('section', 'a3-ds'); vs.appendChild(h('h2', '', 'Fonti e riferimenti')); vs.appendChild(srcBlock(d)); root.appendChild(vs); }
      else if (d.fonti && d.fonti.length) { var fs = h('section', 'a3-ds'); fs.appendChild(h('h2', '', 'Fonti e riferimenti')); fs.appendChild(srcBlock(d)); root.appendChild(fs); }
      reveal(root);
    });
  }

  /* ---------- regia ---------- */
  function renderRit() {
    frame(); api.setTitle('Ritratti privati', 'Pilota A3.1'); var host = h('div', 'a3-ritmgr'); body.appendChild(host);
    withRit(function (r) { r.renderManager(host, function (i) { return BY[i] && BY[i].n; }); });
  }
  var VIEWS = { rit: renderRit, home: renderHome, cat: renderCat, search: renderSearch, dos: renderDossier, hub: renderHub };
  W.tvaA3 = {
    render: function () { ensure(function () { (VIEWS[A3().v] || renderHome)(); reveal(body); }); },
    label: function (s) { var a = s.a3 || {}; if (a.v === 'dos' || a.v === 'hub') return (BY[a.id] && BY[a.id].n) || 'Dossier'; if (a.v === 'cat') return 'Catalogo'; if (a.v === 'rit') return 'Ritratti privati'; if (a.v === 'search') return 'Ricerca'; return 'Atlante 2.0'; },
    open: openId, search: function (q) { return IDX ? search(q) : null; }, state: function () { return { idx: !!IDX, shards: Object.keys(SH).length }; }, ensure: ensure
  };
  if (W.tvaA3Boot) W.tvaA3Boot();
})();
