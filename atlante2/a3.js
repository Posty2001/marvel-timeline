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
    { t: 'p', n: 'Personaggi', s: 'identità, varianti, incarnazioni', img: 'personaggi' }, { t: 'h', n: 'Hub di identità', s: 'identità e continuità raccolte', img: 'multiverso' },
    { t: 'm', n: 'Mantelli', s: 'titoli passati di mano', img: 'arti_mistiche' }, { t: 'U', n: 'Universi', s: 'continuità e Terre', img: 'universi' },
    { t: 'o', n: 'Organizzazioni', s: 'agenzie e gruppi', img: 'organizzazioni' }, { t: 'a', n: 'Artefatti', s: 'oggetti e reliquie', img: 'artefatti' },
    { t: 'l', n: 'Luoghi', s: 'luoghi narrativi', img: 'luoghi' }, { t: 'P', n: 'Pianeti', s: 'mondi e dimensioni', img: 'luoghi' },
    { t: 'e', n: 'Eventi', s: 'eventi e battaglie', img: 'eventi' }, { t: 't', n: 'Attori', s: 'interpreti', img: 'attori' },
    { t: 'O', n: 'Opere', s: 'film, serie e produzioni', img: 'eventi' }, { t: 'C', n: 'Creatori', s: 'autori, registi, sceneggiatori', img: 'attori' }, { t: 'S', n: 'Specie e civiltà', s: 'popoli e razze', img: 'personaggi' }];
  var TN = {}; TYPES.forEach(function (x) { TN[x.t] = x; });
  var SING = { p: 'Personaggio', h: 'Hub di identità', m: 'Mantello', U: 'Universo', o: 'Organizzazione', a: 'Artefatto', l: 'Luogo', P: 'Pianeta', e: 'Evento', t: 'Attore', O: 'Opera', C: 'Creatore', S: 'Specie o civiltà' };
  var KIND = { i: 'Identità', v: 'Variante', c: 'Copia', h: 'Hub', m: 'Mantello', g: '' };
  var PAL = { p: ['#3a2f1c', '#E3C79B'], h: ['#3a1c1e', '#ff5c5f'], m: ['#2c2140', '#b48ae0'], U: ['#10303a', '#4fd0ff'], o: ['#3a2a10', '#F59A23'], a: ['#341a3c', '#d46aff'], l: ['#14283a', '#6fb3d9'], P: ['#143a34', '#9fe0d4'], e: ['#3a2010', '#ff8a3c'], t: ['#3a1c22', '#e9a0a6'] , O: ['#2a2a3a', '#9aa8ff'], C: ['#2b2f2a', '#b6d98a'], S: ['#2a3a2f', '#7fe0a8']};

  /* ---------- utilità ---------- */
  function h(tag, cls, txt, at) { var n = D.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; if (at) Object.keys(at).forEach(function (k) { n.setAttribute(k, at[k]); }); return n; }
  function btn(cls, txt, fn, at) { var b = h('button', cls, txt, at); b.type = 'button'; if (fn) b.addEventListener('click', fn); return b; }
  function svg(path) { var s = D.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('class', 'ic'); s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('aria-hidden', 'true'); var p = D.createElementNS('http://www.w3.org/2000/svg', 'path'); p.setAttribute('d', path); s.appendChild(p); return s; }
  var IC = { star: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z', chev: 'M9 5l7 7-7 7', nexus: 'M12 9a3 3 0 1 0 0 .01M5 19a2.5 2.5 0 1 0 0 .01M19 19a2.5 2.5 0 1 0 0 .01M5 5a2.5 2.5 0 1 0 0 .01M19 5a2.5 2.5 0 1 0 0 .01M10 10.5L6.6 6.6M14 10.5l3.4-3.9M10.2 14l-3.8 3.6M13.8 14l3.8 3.6', route: 'M5 18a2 2 0 1 0 0 .01M19 6a2 2 0 1 0 0 .01M7 18h6a4 4 0 0 0 0-8h-2a4 4 0 0 1 0-8h6', search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4', grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z', grid3: 'M3 4h4.5v4.5H3zM9.7 4h4.5v4.5H9.7zM16.5 4H21v4.5h-4.5zM3 10h4.5v4.5H3zM9.7 10h4.5v4.5H9.7zM16.5 10H21v4.5h-4.5zM3 16h4.5v4.5H3zM9.7 16h4.5v4.5H9.7zM16.5 16H21v4.5h-4.5z', filter: 'M4 6h16M7 12h10M10 18h4', edit: 'M4 20h4L19 9l-4-4L4 16zM13 7l4 4', list: 'M4 6h16M4 12h16M4 18h16', arrow: 'M9 5l7 7-7 7', orbit: 'M12 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0M12 12m-8 0a8 8 0 1 0 16 0a8 8 0 1 0-16 0M18 5.5l.01 0' };
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
        var old = el.querySelector('.a3-comp'); if (old) old.remove(); el.appendChild(c); el.classList.add('has-pt'); if (big && el.parentNode && el.parentNode.classList) el.parentNode.classList.add('comp');
      }); });
    });
  }
  function A3() { return ST.a3 || (ST.a3 = { v: 'home' }); }
  function ensure(cb) {
    if (IDX) return cb();
    get('data/index.json').then(function (d) {
      IDX = d; d.voci.forEach(function (v) { BY[v.i] = v; (ORD[v.t] = ORD[v.t] || []).push(v); });
      mergeDb(cb);
    }).catch(function () { body.className = 'a2-scroll a3'; body.textContent = ''; body.appendChild(h('div', 'empty', 'Dati di TVA Atlas non disponibili offline. Puoi usare l’Atlante classico.')); });
  }
  /* Integrazione NATIVA del database esteso: le voci entrano nei cataloghi, nella ricerca, nel Multiverso e nel Nexus come tutte le altre.
     Si carica solo un elenco leggero (atlante2/data/db/stub.json); le schede complete arrivano a richiesta. Se i dati non esistono, nulla cambia. */
  function mergeDb(cb) {
    get('data/db/stub.json').then(function (st) {
      if (!st || !st.r) return cb();
      Object.keys(st.uni || {}).forEach(function (u) { if (!IDX.meta.universi[u]) IDX.meta.universi[u] = { n: st.uni[u].n, c: st.uni[u].c, nt: '' }; });
      var tocc = {};
      st.r.forEach(function (r) {
        if (BY[r[0]]) return; var u = r[3] && IDX.meta.universi[r[3]] ? r[3] : '';
        var v = { i: r[0], n: r[1], t: r[2], k: 'i', u: u, a: 0, q: norm(r[1] + ' ' + (r[6] || '')), pg: [], s: 0, sh: -1, db: 1, lv: r[4], o: r[5] };
        BY[v.i] = v; IDX.voci.push(v); (ORD[v.t] = ORD[v.t] || []).push(v); tocc[v.t] = 1;
      });
      Object.keys(st.x || {}).forEach(function (id) { if (BY[id] && st.x[id]) BY[id].q += ' ' + st.x[id]; });
      Object.keys(tocc).forEach(function (t) { ORD[t].sort(function (a, b) { var x = norm(a.n), y = norm(b.n); return x < y ? -1 : x > y ? 1 : 0; }); });
      cb();
    }).catch(function () { cb(); });
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

  /* Colori e nature degli universi: UNICA definizione, condivisa con la mappa (a4.js li legge da tvaA3Ctx) */
  var ORBCLR = ['#F59A23', '#6fd0e0', '#b79cf0', '#9aa39a'], ORBN = ['Continuità principale', 'Diramazione / universo alternativo', 'Universo autonomo', 'Raggruppamento editoriale'];
  function uniHue(id) { var x = 7; for (var q = 0; q < id.length; q++) x = (Math.imul(x, 31) + id.charCodeAt(q)) >>> 0; return x % 360; }
  function natIdx(v) { var c = IDX && IDX.meta.universi[v.u || v.i] ? IDX.meta.universi[v.u || v.i].c : ''; var k = ORBN.indexOf(c); return k < 0 ? (/Luogo narrativo/.test(c) ? 3 : 2) : k; }
  function terraNum(v) { var m = v.t === 'U' ? /^Earth-([0-9A-Z]+)\b/.exec(v.n) : null; return m && /\d/.test(m[1]) ? m[1] : null; }
  function emblemGen(v, big) {
    var p = PAL[v.t] || PAL.p, hs = hash(v.i), R = rngOf(hs), s = S('svg', { viewBox: '0 0 160 100', preserveAspectRatio: 'xMidYMid slice', 'class': 'a3-em', 'aria-hidden': 'true' });
    var gid = 'g' + hs.toString(36), defs = S('defs', {}, s), lg = S('linearGradient', { id: gid, x1: 0, y1: 0, x2: 1, y2: 1 }, defs);
    S('stop', { offset: 0, 'stop-color': p[0] }, lg); S('stop', { offset: 1, 'stop-color': '#0e0b08' }, lg); S('rect', { width: 160, height: 100, fill: 'url(#' + gid + ')' }, s);
    var cx = 80, cy = 50, st = { fill: 'none', stroke: p[1], 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
    function ln(a, o) { var q = {}; Object.keys(st).forEach(function (k) { q[k] = st[k]; }); Object.keys(a).forEach(function (k) { q[k] = a[k]; }); return S(o || 'path', q, s); }
    function pt(r, a) { return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; }
    function pt0(x0, y0, r, a) { return [x0 + r * Math.cos(a), y0 + r * Math.sin(a)]; }
    var i, a, q, k, n;
    if (v.t === 'U') {
      /* colori propri dell'universo (stessa tinta del nodo nella mappa) e simbolo per natura documentata (stessi colori delle orbite) */
      var hu = uniHue(v.i), nat = natIdx(v), oc = ORBCLR[nat], ac = 'hsl(' + hu + ',66%,68%)';
      s.setAttribute('preserveAspectRatio', 'xMidYMid meet'); s.querySelector('rect').setAttribute('x', -200); s.querySelector('rect').setAttribute('y', -200); s.querySelector('rect').setAttribute('width', 560); s.querySelector('rect').setAttribute('height', 500);
      s.querySelector('stop').setAttribute('stop-color', 'hsl(' + hu + ',46%,17%)');
      var num = terraNum(v), uc = { stroke: ac, fill: 'none', 'stroke-linecap': 'round' };
      function ur(r, o, w, da) { return S('circle', { cx: cx, cy: cy, r: r, fill: 'none', stroke: o || ac, 'stroke-opacity': w || .4, 'stroke-width': 1.1, 'stroke-dasharray': da || '0' }, s); }
      if (nat === 0) { ur(40, oc, .9); ur(31, ac, .5); for (i = 0; i < 16; i++) { q = pt(43, i * .3927); a = pt(50, i * .3927); S('path', { d: 'M' + q[0].toFixed(1) + ' ' + q[1].toFixed(1) + 'L' + a[0].toFixed(1) + ' ' + a[1].toFixed(1), stroke: oc, 'stroke-width': 1.4, 'stroke-linecap': 'round', 'stroke-opacity': .85 }, s); } }
      else if (nat === 1) { ur(38, oc, .8, '4 3'); ur(28, ac, .45); S('path', { d: 'M' + (cx - 46) + ' ' + (cy + 40) + 'Q' + cx + ' ' + (cy + 6) + ' ' + (cx + 46) + ' ' + (cy - 36) + 'M' + (cx - 30) + ' ' + (cy + 44) + 'Q' + (cx + 10) + ' ' + (cy + 20) + ' ' + (cx + 50) + ' ' + (cy + 18), stroke: oc, fill: 'none', 'stroke-width': 1.5, 'stroke-opacity': .85, 'stroke-linecap': 'round' }, s); }
      else if (nat === 2) { ur(38, oc, .85, '2 4'); ur(27, ac, .45); a = pt(38, -.9 + (hu % 7) * .35); S('circle', { cx: a[0].toFixed(1), cy: a[1].toFixed(1), r: 3.6, fill: oc }, s); a = pt(27, 2.2 + (hu % 5) * .3); S('circle', { cx: a[0].toFixed(1), cy: a[1].toFixed(1), r: 2.4, fill: ac }, s); }
      else { var hx = ''; for (i = 0; i < 6; i++) { q = pt(40, i * 1.0472 + .5236); hx += (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1); } S('path', { d: hx + 'Z', fill: 'none', stroke: oc, 'stroke-opacity': .85, 'stroke-width': 1.4, 'stroke-linejoin': 'round' }, s); ur(26, ac, .4); }
      if (num) {   // numero intero e centrato: il corpo si adatta al numero di cifre (nessun troncamento)
        var fz = num.length > 5 ? 21 : num.length > 3 ? 27 : 36;
        var tx = S('text', { x: cx, y: cy + fz * .34, 'text-anchor': 'middle', 'font-family': 'Spectral, Georgia, serif', 'font-weight': 700, 'font-size': fz, fill: ac, 'fill-opacity': .96 }, s); tx.textContent = num;
      } else {   // universo senza numerazione documentata: costellazione propria (nessun numero inventato)
        n = 7 + Math.floor(R() * 5); var pts = [];
        for (i = 0; i < n; i++) { a = R() * 6.2832; q = 6 + R() * 24; pts.push(pt(q, a)); }
        for (i = 1; i < n; i++) S('path', { d: 'M' + pts[i - 1][0].toFixed(1) + ' ' + pts[i - 1][1].toFixed(1) + 'L' + pts[i][0].toFixed(1) + ' ' + pts[i][1].toFixed(1), stroke: ac, fill: 'none', 'stroke-opacity': .55, 'stroke-width': 1 }, s);
        pts.forEach(function (c, j) { S('circle', { cx: c[0].toFixed(1), cy: c[1].toFixed(1), r: j === 0 ? 3.6 : 1.8 + R() * 1.4, fill: ac, 'fill-opacity': j === 0 ? 1 : .85 }, s); });
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
    var p = v.db ? { v: 'dbx', id: id, o: v.o } : { v: v.t === 'h' || v.t === 'm' ? 'hub' : 'dos', id: id }; if (push === false) { ST.a3 = p; api.draw(); api.setScroll(0); } else api.nav('a3', { a3: p });
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
  function uniFull(v) { return String(v.n || '').replace(/^Earth-([0-9A-Z]+)(?= —|$)/, 'Terra-$1').replace(/ — /, ' · '); }
  function shown(v) {   // titolo senza ripetizioni; per gli universi: nome/denominazione COMPLETA + classificazione separata (il nome completo resta anche in aria-label e nel dossier)
    var n = v.n, sub = v.u ? uniNome(v.u) : (v.a ? v.a + (v.t === 'h' ? ' voci collegate' : v.t === 'm' ? ' titolari' : ' apparizioni') : '');
    if (v.t === 'U') return { n: uniFull(v), s: uniCont(v.i) || '' };
    if (v.db && !sub) sub = v.lv === 'B' ? 'scheda strutturata' : 'voce essenziale';
    if (sub && (nk(sub) === nk(n) || nk(n).indexOf(nk(sub)) >= 0)) sub = '';
    return { n: n, s: sub };
  }
  function tile(v, compact) {
    var b = btn('a3-tile t-' + v.t, null, function () { openId(v.i); }, { 'aria-label': v.n + (badge(v) ? ' — ' + badge(v) : '') }); if (v.db) b.setAttribute('data-db', '1');
    var em = h('span', 'em'); em.appendChild(emblem(v)); b.appendChild(em); paintAny(em, v, false);
    if (v.s) b.appendChild(h('span', 'bd', badge(v)));
    var sh = shown(v), t = h('span', 't'); t.appendChild(h('b', '', sh.n));
    if (sh.s) { var cl = h('span', v.t === 'U' ? 'cls' : '', sh.s); if (v.t === 'U') cl.style.setProperty('--oc', ORBCLR[natIdx(v)]); t.appendChild(cl); }
    if (v.t === 'U') b.style.setProperty('--hu', 'hsl(' + uniHue(v.i) + ',66%,68%)');
    b.appendChild(t);
    return b;
  }
  function li(v) {
    var b = btn('a3-li t-' + v.t, null, function () { openId(v.i); });
    var em = h('span', 'em'); em.appendChild(emblem(v)); b.appendChild(em); paintAny(em, v, false);
    var sh = shown(v), t = h('span'); t.appendChild(h('b', '', sh.n)); var sub = (v.t === 'U' ? sh.s : (sh.s || (v.a ? v.a + ' apparizioni' : ''))); if (sub) { var sp = h('span', 's', sub); if (v.t === 'U') sp.style.setProperty('--oc', ORBCLR[natIdx(v)]); t.appendChild(sp); } b.appendChild(t);
    if (v.s) b.appendChild(h('span', 'bd', badge(v)));
    return b;
  }

  /* Emblema multiversale originale di TVA Atlas: anello dorato, linea temporale sacra che si ramifica in tre universi (nessun riferimento a loghi esistenti). */
  function atlasMark() {
    var ns = 'http://www.w3.org/2000/svg', e = D.createElementNS(ns, 'svg'); e.setAttribute('viewBox', '0 0 64 64'); e.setAttribute('class', 'a3-mark'); e.setAttribute('role', 'img'); e.setAttribute('aria-label', 'Emblema TVA Atlas');
    [['circle', { cx: 32, cy: 32, r: 29, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6 }], ['circle', { cx: 32, cy: 32, r: 24, fill: 'none', stroke: 'currentColor', 'stroke-width': .6, 'stroke-dasharray': '1.5 3' }],
      ['path', { d: 'M32 54V34M32 34C32 26 20 24 17 14M32 34C32 26 44 24 47 14M32 34V10', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round' }],
      ['circle', { cx: 17, cy: 13, r: 2.6, fill: 'currentColor' }], ['circle', { cx: 32, cy: 9, r: 2.6, fill: 'currentColor' }], ['circle', { cx: 47, cy: 13, r: 2.6, fill: 'currentColor' }], ['circle', { cx: 32, cy: 54, r: 2.2, fill: 'currentColor' }]].forEach(function (x) { var n = D.createElementNS(ns, x[0]); for (var k in x[1]) n.setAttribute(k, x[1][k]); e.appendChild(n); });
    return e;
  }
  /* anteprima della mappa: stesse orbite e stessi colori dell'Osservatorio (una sola definizione: ORBCLR) */
  function obsPreview() {
    var e = S('svg', { viewBox: '-100 -100 200 200', 'class': 'a3-obs-svg', 'aria-hidden': 'true' }); var us = (ORD.U || []).slice(0, 24), R = [0, 34, 60, 84], cnt = [0, 0, 0, 0];
    [1, 2, 3].forEach(function (i) { S('circle', { cx: 0, cy: 0, r: R[i], fill: 'none', stroke: ORBCLR[i], 'stroke-opacity': .5, 'stroke-width': .8, 'stroke-dasharray': '2 3' }, e); });
    S('circle', { cx: 0, cy: 0, r: 7, fill: ORBCLR[0] }, e); S('circle', { cx: 0, cy: 0, r: 11, fill: 'none', stroke: ORBCLR[0], 'stroke-opacity': .5 }, e);
    us.forEach(function (v) { var k = natIdx(v); if (!k || k > 3) return; var a = hash(v.i) / 4294967296 * 6.2832 + k, r = R[k]; S('circle', { cx: (r * Math.cos(a)).toFixed(1), cy: (r * Math.sin(a)).toFixed(1), r: 3.6, fill: 'hsl(' + uniHue(v.i) + ',66%,64%)', stroke: ORBCLR[k], 'stroke-width': 1 }, e); cnt[k]++; });
    return e;
  }
  /* ---------- HOME ---------- */
  function renderHome() {
    frame(); api.setTitle('TVA Atlas', 'L’Atlante del Multiverso');
    var s = A3(), n = IDX.voci.length, np = (ORD.p || []).length, nu = (ORD.U || []).length;
    var hero = h('section', 'a3-hero'); hero.setAttribute('aria-labelledby', 'a3H1');
    var bg = h('div', 'a3-bg'); bgImg(bg, 'home_hero', true); hero.appendChild(bg);
    [[260, 8, 12], [190, 30, 22], [120, 52, 34]].forEach(function (r, i) { var ring = h('i', 'a3-ring' + (i === 1 ? ' a3-spin' : '')); ring.style.cssText = 'width:' + r[0] + 'px;height:' + r[0] + 'px;right:' + (-r[2]) + 'px;top:' + (r[1] + 30) + 'px;opacity:' + (0.85 - i * 0.2); hero.appendChild(ring); });
    hero.appendChild(h('div', 'a3-tw')); hero.appendChild(h('div', 'a3-fade'));
    var t = h('div', 'a3-hero-t'); var br = h('div', 'a3-brand'); br.appendChild(atlasMark()); br.appendChild(h('span', 'kick', 'TVA ARCHIVES')); t.appendChild(br);
    var h1 = h('h1', '', 'TVA Atlas'); h1.id = 'a3H1'; t.appendChild(h1); t.appendChild(h('p', 'a3-sub', 'L’Atlante del Multiverso')); t.appendChild(h('p', 'a3-motto', 'Ogni universo. Ogni identità. Ogni connessione.'));
    var st = h('ul', 'a3-stats'); [[np, 'identità'], [nu, 'universi'], [n, 'voci in archivio']].forEach(function (x) { var l = h('li'); l.appendChild(h('b', '', String(x[0]))); l.appendChild(D.createTextNode(x[1])); st.appendChild(l); }); t.appendChild(st);
    var sb = btn('a3-sbar', null, function () { api.nav('a3', { a3: { v: 'search', q: '' } }); }, { 'aria-label': 'Cerca in TVA Atlas' }); sb.appendChild(svg(IC.search)); sb.appendChild(h('span', '', 'Cerca personaggi, universi, luoghi…')); t.appendChild(sb);
    var row = h('div', 'a3-row a3-hrow'); var ob = btn('btn fill a3-obsbtn', null, function () { api.nav('a3', { a3: { v: 'mv' } }); }, { 'aria-label': 'Apri l’Osservatorio del Multiverso, la mappa degli universi' }); ob.appendChild(svg(IC.orbit)); ob.appendChild(h('span', '', 'Osservatorio del Multiverso')); row.appendChild(ob);
    row.appendChild(btn('btn ghost', 'Esplora il catalogo', function () { api.nav('a3', { a3: { v: 'cat', t: 'p', m: vistaPref(), n: 36 } }); })); t.appendChild(row);
    hero.appendChild(t); body.appendChild(hero);
    /* Portali compatti (a43): l'Osservatorio e' la MAPPA interattiva (non il catalogo); Nexus e Percorsi sono due portali affiancati. Intera scheda cliccabile. */
    var obs = btn('a3-portal a3-obs', null, function () { api.nav('a3', { a3: { v: 'mv' } }); }, { 'aria-label': 'Apri l’Osservatorio del Multiverso, la mappa interattiva degli universi', 'data-portal': 'mv' });
    var pm = h('span', 'a3-pt-map'); pm.appendChild(obsPreview()); obs.appendChild(pm);
    var ot = h('span', 'a3-pt-t'); ot.appendChild(h('span', 'kick', 'La mappa')); ot.appendChild(h('b', '', 'Osservatorio del Multiverso')); ot.appendChild(h('span', 'sub', nu + ' universi in una mappa interattiva')); obs.appendChild(ot);
    obs.appendChild(svg(IC.chev)); body.appendChild(obs);
    var pg2 = h('div', 'a3-portals');
    [['nx', 'TVA Nexus', 'La rete delle relazioni', IC.nexus, { v: 'nx', c: 'id-iron-man' }], ['pc', 'Percorsi', 'Da un’identità all’altra', IC.route, { v: 'pc', a: '', b: '', m: 'n' }]].forEach(function (x) {
      var b = btn('a3-portal a3-pt2', null, function () { api.nav('a3', { a3: x[4] }); }, { 'aria-label': x[1] + ': ' + x[2], 'data-portal': x[0] }); b.appendChild(svg(x[3])); var t = h('span', 'a3-pt-t'); t.appendChild(h('b', '', x[1])); t.appendChild(h('span', 'sub', x[2])); b.appendChild(t); pg2.appendChild(b);
    }); body.appendChild(pg2);
    var pg3 = h('div', 'a3-portals');
    [['pf', 'Preferiti e raccolte', 'Le tue voci salvate', IC.star || IC.chev, { v: 'pf' }], ['pr', 'Progressione', 'Esplorazione e badge', IC.route, { v: 'pr' }]].forEach(function (x) {
      var b = btn('a3-portal a3-pt2', null, function () { api.nav('a3', { a3: x[4] }); }, { 'aria-label': x[1] + ': ' + x[2], 'data-portal': x[0] }); b.appendChild(svg(x[3])); var t = h('span', 'a3-pt-t'); t.appendChild(h('b', '', x[1])); t.appendChild(h('span', 'sub', x[2])); b.appendChild(t); pg3.appendChild(b);
    }); body.appendChild(pg3);
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
      var sh = h('section', 'a3-sec'); var hh = h('header'); hh.appendChild(h('h2', '', 'Hub di identità')); hh.appendChild(h('p', '', 'Una pagina che raccoglie le identità di uno stesso personaggio (varianti multiversali o fasi di una stessa continuità). Nessuna parentela narrativa è attribuita senza fonte.')); sh.appendChild(hh);
      var hw = h('div', 'a3-hubs'); hubs.forEach(function (v) { var c = btn('a3-hc rev t-h', null, function () { openId(v.i); }); c.appendChild(h('span', 'kick', 'Hub')); c.appendChild(h('b', '', v.n)); c.appendChild(h('span', 'soft', v.a + ' voci collegate')); hw.appendChild(c); }); sh.appendChild(hw); body.appendChild(sh);
    }
    var cl = btn('btn ghost a3-classic', 'Atlante classico', function () { W.__a3Classic = true; A.openHome(); }); body.appendChild(cl);
    body.appendChild(btn('a3-ritlink', 'Ritratti privati: scene, importazione, esportazione', function () { api.nav('a3', { a3: { v: 'rit' } }); }));
    body.appendChild(h('p', 'a3-note', 'L’Atlante classico resta disponibile e invariato. I ritratti compariranno solo quando disponibili e utilizzabili; fino ad allora ogni voce mostra un emblema. Fonti: dati dell’Atlante e fonti secondarie dichiarate nella scheda.'));
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
    TYPES.forEach(function (x) { var c = (ORD[x.t] || []).length; if (!c) return; var b = btn('chip t-' + x.t + (x.t === s.t ? ' on' : ''), x.n, function () { ST.a3 = { v: 'cat', t: x.t, m: s.m, n: 36, q: '', u: '', c: '', cx: chips.scrollLeft, cz: 1 }; api.draw(); api.setScroll(0); }, { role: 'tab', 'aria-selected': x.t === s.t ? 'true' : 'false' }); b.appendChild(h('small', '', String(c))); chips.appendChild(b); });
    tools.appendChild(chips);
    chips.addEventListener('scroll', function () { s.cx = chips.scrollLeft; }, { passive: true });   // la posizione orizzontale fa parte dello stato (ripristino dal dossier, cambio vista, nuovi render)
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
    body.appendChild(tools);
    /* barra categorie: mai riportata all'inizio. Si ripristina la posizione salvata e, solo se la categoria scelta non e' del tutto visibile
       (o e' appena cambiata), la si centra dolcemente partendo dalla posizione corrente (nessun salto). */
    function chipsFix(anim) {
      var on = chips.querySelector('.chip.on'); if (!on) return; var vw = chips.clientWidth; if (!vw) return;
      if (typeof s.cx === 'number') chips.scrollLeft = s.cx;
      var l = on.offsetLeft, r = l + on.offsetWidth, v0 = chips.scrollLeft, need = s.cz || l < v0 + 12 || r > v0 + vw - 12;
      if (!need) return; var tg = Math.max(0, Math.min(chips.scrollWidth - vw, Math.round(l - (vw - on.offsetWidth) / 2)));
      var calm = W.matchMedia && W.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (anim && !calm) { try { chips.scrollTo({ left: tg, behavior: 'smooth' }); } catch (e) { chips.scrollLeft = tg; } } else chips.scrollLeft = tg;
      s.cz = 0; if (!(anim && !calm)) s.cx = tg; return anim && !calm;
    }
    var smooth = chipsFix(true); if (!smooth) requestAnimationFrame(function () { if (chips.isConnected) chipsFix(false); });
    if (s.t === 'U') {   // il catalogo degli universi e' un elenco di schede: la mappa e' un'altra funzione
      var bn = h('div', 'a3-obsnote'); bn.appendChild(h('span', '', 'Questo è il catalogo (l’elenco delle schede). Per vedere gli universi sulla mappa:')); bn.appendChild(btn('btn ghost', 'Osservatorio del Multiverso', function () { api.nav('a3', { a3: { v: 'mv' } }); })); body.appendChild(bn);
    }
    var cnt = h('div', 'a3-count'); cnt.setAttribute('aria-live', 'polite'); body.appendChild(cnt); var host = h('div'); body.appendChild(host);
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

  /* ---------- ARCHIVIO ESTESO (Database Expansion): modulo lazy, inerte se i dati non esistono ---------- */
  var DBQ = [], DBL = 0;
  function withDb(cb) {
    if (W.tvaDb) return cb(W.tvaDb); DBQ.push(cb); if (DBL) return; DBL = 1;
    var sc = D.createElement('script'); sc.src = BASE + 'db.js'; sc.async = true; sc.onload = function () { var q = DBQ.splice(0); q.forEach(function (f) { if (W.tvaDb) f(W.tvaDb); }); }; sc.onerror = function () { DBL = 0; DBQ.length = 0; }; D.head.appendChild(sc);
  }
  function renderDbx() {
    frame(); var s = A3(); body.appendChild(h('div', 'a3-load', 'Caricamento…'));
    withDb(function (db) { (s.o != null && db.at ? db.at(s.o, s.id) : { then: function (f) { db.get(s.id, f); } }).then(function (r) {
      if (ST.a3 !== s) return; frame();
      if (!r) { body.appendChild(h('div', 'empty', 'Voce non disponibile.')); return; }
      api.setTitle(r.n, (db.TIPO[r.t] || 'TVA Atlas'));
      var c = h('article', 'a3-dbx'); c.appendChild(h('div', 'k', (SING[(BY[r.i] || {}).t] || db.TIPO[r.t] || r.t) + (r.lv === 'B' ? ' · scheda strutturata' : ' · voce essenziale')));
      c.appendChild(h('h2', '', r.n)); if (r.it && r.it !== r.n) c.appendChild(h('div', 'it', 'In italiano: ' + r.it));
      if (r.d) c.appendChild(h('p', 'd', r.d.charAt(0).toUpperCase() + r.d.slice(1) + '.'));
      var kv = function (k, v, tag) { if (!v || (v.length === 0)) return; var d = h('div', 'a3-kv'); d.appendChild(h('span', 'k', k)); var vv = h('div', 'v', Array.isArray(v) ? v.join(', ') : v); if (tag) vv.appendChild(h('small', 'a3-ff', ' · ' + tag)); d.appendChild(vv); c.appendChild(d); };
      kv('Alias e denominazioni', r.al); kv('Interpreti', r.ip);
      var F = r.f || {}, FF = r.ff || {}, ET = [['specie', 'Specie'], ['genere', 'Genere'], ['stato', 'Stato'], ['affiliazioni', 'Organizzazioni di appartenenza'], ['poteri', 'Poteri'], ['abilita', 'Abilità'], ['equipaggiamento', 'Equipaggiamento'], ['trasformazioni', 'Trasformazioni'], ['debolezze', 'Debolezze'], ['prima_apparizione', 'Prima apparizione'], ['origine', 'Origine'], ['nome_reale', 'Nome reale'], ['cittadinanza', 'Cittadinanza'], ['occupazione', 'Occupazione'], ['nascita', 'Nascita'], ['morte', 'Morte'], ['ubicazione', 'Ubicazione'], ['utenti', 'Utenti e proprietari'], ['creatore_oggetto', 'Creato da'], ['membri', 'Membri e capi'], ['esito', 'Esito'], ['popolazione', 'Popolazione'], ['apparizioni_narrativa', 'Apparizioni nella continuità narrativa'], ['apparizioni_alternativi', 'Apparizioni in universi alternativi (varianti, non la stessa incarnazione)'], ['apparizioni_fumetti', 'Fumetti'], ['apparizioni_videogiochi', 'Videogiochi'], ['apparizioni_adattamenti', 'Adattamenti, LEGO, parodie e altri media']];
      ET.forEach(function (e) { kv(e[1], F[e[0]], FF[e[0]] >= 2 ? 'confermato da due fonti' : (FF[e[0]] === 1 ? 'una fonte' : '')); });
      if (r.u && BY[r.u]) { var d = h('div', 'a3-kv'); d.appendChild(h('span', 'k', 'Continuità')); var v = h('div', 'v'); v.appendChild(btn('a3-lk', BY[r.u].n, function () { openId(r.u); })); d.appendChild(v); c.appendChild(d); }
      if (r.dz && r.dz.length) {   // dossier discorsivo in italiano (livello A): testo originale composto solo da fatti verificati
        var dzb = h('div', 'a3-dz'); r.dz.forEach(function (x) { var sc = h('section', 'a3-ds'); sc.appendChild(h('h3', '', x[0])); sc.appendChild(h('p', '', x[1])); dzb.appendChild(sc); }); c.appendChild(dzb);
        c.appendChild(h('p', 'a3-dbnote', 'Dossier composto da TVA Archives con frasi originali a partire dai soli fatti verificati indicati nelle fonti; nessun testo è copiato. I termini tecnici restano nella lingua originale.'));
      }
      c.appendChild(h('p', 'a3-dbnote', r.lv === 'B' ? 'Scheda strutturata (Livello B): fatti documentati dalle fonti indicate, senza testi copiati; i termini non tradotti restano nella lingua originale. Le schede di livello superiore arriveranno con le ondate successive.' : 'Voce essenziale: identità, tipo e riferimenti verificati. Il dossier approfondito arriverà con le ondate successive; nessun testo è copiato da altre fonti.'));
      var f = h('div', 'a3-dbsrc'); [['Wikidata (CC0)', 'https://www.wikidata.org/wiki/' + r.wd], r.wp ? ['Wikipedia (solo riferimento)', 'https://en.wikipedia.org/wiki/' + encodeURIComponent(r.wp.replace(/ /g, '_'))] : null].forEach(function (x) { if (!x) return; var a = h('a', '', x[0]); a.href = x[1]; a.target = '_blank'; a.rel = 'noopener noreferrer'; f.appendChild(a); });
      (r.xs || []).forEach(function (x) { var a = h('a', '', x[0] + ' (CC BY-SA 3.0)'); a.href = x[1]; a.target = '_blank'; a.rel = 'noopener noreferrer'; f.appendChild(a); }); c.appendChild(f);
      if (BY[r.i] && (BY[r.i].t === 'p' || BY[r.i].t === 'o')) c.appendChild(btn('btn ghost a3-dbopen', 'Apri nel TVA Nexus', function () { api.nav('a3', { a3: { v: 'nx', c: r.i } }); }));
      c.id = 'dbx-s'; c.classList.add('a3-ds');   /* una sezione: stessa regola di esplorazione dei dossier (tempo, scorrimento, sezioni) */
      body.appendChild(c);
      var acts = h('div', 'a5-slot'); body.appendChild(acts); var tr5 = null;
      withA5(function (m) { if (ST.a3 !== s || !c.isConnected) return; acts.appendChild(m.acts(s.id)); tr5 = m.track(s.id, s); tr5.total(1); tr5.attach(c); });
    }); });
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
    frame(); var s = A3(); api.setTitle('Ricerca', 'TVA Atlas');
    var tools = h('div', 'a3-tools'), l = h('div', 'line'), inp = h('input', 'a3-in'); inp.type = 'search'; inp.placeholder = 'Cerca in TVA Atlas…'; inp.value = s.q || ''; inp.setAttribute('aria-label', 'Cerca'); inp.setAttribute('autocomplete', 'off'); l.appendChild(inp); tools.appendChild(l); body.appendChild(tools);
    var out = h('div'); body.appendChild(out); var tm, tok = { q: '' };
    function run() {
      s.q = inp.value; out.textContent = ''; tok.q = s.q; var q = norm(s.q); if (!q) { out.appendChild(h('div', 'empty', 'Scrivi un nome, un universo, un interprete…')); return; }
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
      if (x.ruolo === 'hub') { b.appendChild(h('h3', '', 'Hub di identità: ' + x.n)); b.appendChild(h('p', '', 'Questa identità appartiene a un hub che raccoglie le sue controparti. L’appartenenza all’hub non è una relazione narrativa.')); b.appendChild(btn('chip t-h', 'Apri l’hub', function () { openId(x.id); })); if (x.membri.length) { b.appendChild(h('p', '', 'Altre voci dell’hub')); b.appendChild(chipsFor(x.membri)); } }
      else if (x.ruolo === 'mantello') { b.appendChild(h('h3', '', 'Mantello: ' + x.n)); b.appendChild(h('p', '', 'Titolo portato da più identità distinte: non sono la stessa persona.')); b.appendChild(btn('chip t-m', 'Apri il mantello', function () { openId(x.id); })); if (x.membri.length) b.appendChild(chipsFor(x.membri)); }
      else if (x.ruolo === 'rel') { b.appendChild(h('h3', '', RELT[x.tipo] || x.tipo.replace(/_/g, ' '))); b.appendChild(chipsFor([x.id])); if (x.nota) b.appendChild(h('p', '', x.nota)); if (x.verifica) b.appendChild(h('p', '', 'Verifica: ' + x.verifica)); }
      else if (x.ruolo === 'incarnazioni') {
        var fas = x.lista.every(function (c) { return c.tipo === 'fase_di_crescita'; }); b.appendChild(h('h3', '', fas ? 'Fasi evolutive' : 'Incarnazioni e interpreti')); b.appendChild(h('p', '', fas ? 'Le fasi evolutive appartengono alla stessa identità: non sono varianti multiversali né reincarnazioni.' : 'Un cambio di interprete o di età non crea una variante multiversale.'));
        x.lista.forEach(function (c) { var r = h('div', 'a3-kv'); r.appendChild(h('span', 'k', c.tipo === 'cambio_attore' ? 'Cambio di interprete' : c.tipo === 'fase_di_crescita' ? 'Fase evolutiva' : 'Incarnazione')); var v = h('div', 'v'); v.textContent = [c.e, c.int ? '(' + c.int + ')' : '', c.app && c.app.length ? '· ' + c.app.map(function (n) { return 'N°' + n; }).join(', ') : '', c.ex && c.ex.length ? '· ' + c.ex.map(function (n) { return 'N°' + n; }).join(', ') + ' (fonti esterne)' : ''].filter(Boolean).join(' '); r.appendChild(v); if (c.v) r.appendChild(h('span', 'soft', c.v)); b.appendChild(r); });
      }
      w.appendChild(b);
    }); return w;
  }
  function srcVisible(d) { return !!(d.nota || (d.fonti || []).some(function (f) { return /^https:\/\//.test(f); }) || (d.p && d.p.length) || (d.storiche && d.storiche.length)); }
  function srcBlock(d) {
    var w = h('div', 'a3-src');
    /* sezione per l'utente: nessuna dicitura tecnica né ID interno (stato di verifica, nomi dei blob, slug restano nei dati) */
    if (d.nota) w.appendChild(h('span', '', 'Nota: ' + d.nota));
    (d.fonti || []).forEach(function (f) { if (!/^https:\/\//.test(f)) return; var r = h('span'), host = f.replace(/^https:\/\/(www\.)?/, '').split('/')[0]; r.appendChild(h('a', '', host, { href: f, target: '_blank', rel: 'noopener noreferrer', title: f })); w.appendChild(r); });
    var pages = (d.p || []).concat((d.storiche || []).map(function (x) { return x.id; })); var seen = {}, nPg = 0;
    var ARC = { org: 'org', art: 'art', pia: 'luo', luo: 'luo', evt: 'evt', bat: 'evt' };
    pages.forEach(function (p) {
      if (seen[p]) return; seen[p] = 1; var pre = p.split('-')[0];
      w.appendChild(btn('btn ghost', nPg++ ? 'Altra scheda nell’Atlante classico' : 'Apri la scheda nell’Atlante classico', function () {
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
      else if (k === 'fonti') { if (srcVisible(d)) host.appendChild(srcBlock(d)); }
      else if (d.sec[k]) kv(d.sec[k], host, d.p);
      if (host.childNodes.length) out.push({ k: k, t: title, n: host });
    }); return out;
  }
  function renderDossier() {
    frame(); var s = A3(), v = BY[s.id], tr5 = null; if (!v) { body.appendChild(h('div', 'empty', 'Voce non trovata.')); return; }
    api.setTitle(v.n, 'Dossier');
    var root = h('div', 't-' + v.t); body.appendChild(root); var hd = h('header', 'a3-dh'); var em = h('div', 'em'); em.appendChild(emblem(v, true)); hd.appendChild(em); paintAny(em, v, true);
    var t = h('div', 't'); t.appendChild(h('span', 'kick', SING[v.t] || '')); t.appendChild(h('h1', '', v.n));
    var bds = h('div', 'a3-bds'); if (v.s) bds.appendChild(h('span', 'a3-bd warn', badge(v))); if (v.u) { bds.appendChild(h('span', 'a3-bd', uniNome(v.u))); var c = uniCont(v.u); if (c) bds.appendChild(h('span', 'a3-bd', c)); } t.appendChild(bds);
    var rb = btn('a3-ritbtn', null, function () { withRit(function (r) { r.openEditor(v.i, v.n, function (i) { return BY[i] && BY[i].n; }); }); }, { 'aria-label': 'Ritratto privato di ' + v.n, title: 'Ritratto privato' }); rb.appendChild(svg(IC.edit)); hd.appendChild(rb); if (v.t === 'p' || v.t === 'o') { var nxb = btn('a3-ritbtn a4-nxb', 'TVA Nexus', function () { api.nav('a3', { a3: { v: 'nx', c: v.i } }); }, { 'aria-label': 'Apri ' + v.n + ' in TVA Nexus' }); hd.appendChild(nxb); } hd.appendChild(t); root.appendChild(hd); parallax(em);
    var acts = h('div', 'a5-slot'); root.appendChild(acts); withA5(function (m) { if (!root.isConnected || ST.a3 !== s) return; acts.appendChild(m.acts(s.id)); tr5 = m.track(s.id, s); });
    var holder = h('div', 'a3-load', 'Caricamento del dossier…'); root.appendChild(holder);
    dossier(s.id, function (d) {
      if (ST.a3 !== s || !root.isConnected) return; holder.remove();
      if (!d) { root.appendChild(h('div', 'empty', 'Dossier non disponibile.')); return; }
      if (v.s) { var w = h('p', 'a3-note', 'Identità in verifica: i dati sono quelli dell’Atlante classico, senza unificazioni né attribuzioni di varianti.'); root.appendChild(w); }
      var secs = sections(d), jump = h('nav', 'a3-jump'); (function sync5() { if (tr5) tr5.total(secs.length); else setTimeout(sync5, 300); })(); jump.setAttribute('aria-label', 'Sezioni del dossier'); var chips = h('div', 'chips'); var seen = {}, nseen = 0;
      var pr = h('div', 'a3-prog'); var pt = h('span', '', 'Sezioni viste 0/' + secs.length), bar = h('i'); var fill = h('b'); bar.appendChild(fill); pr.appendChild(pt); pr.appendChild(bar);
      secs.forEach(function (sx, i) { chips.appendChild(btn('chip' + (i ? '' : ' on'), sx.t, function () { var e = D.getElementById('a3s-' + sx.k); if (e) body.scrollTo({ top: e.offsetTop - (jump.offsetHeight || 90) + 4, behavior: 'smooth' }); })); });
      if (!secs.length) { root.appendChild(h('div', 'empty', 'Per questa voce non sono ancora disponibili altre informazioni.')); return; }
      jump.appendChild(chips); jump.appendChild(pr); root.appendChild(jump);
      secs.forEach(function (sx) { var sec = h('section', 'a3-ds rev', null, { id: 'a3s-' + sx.k }); sec.appendChild(h('h2', '', sx.t)); sec.appendChild(sx.n); root.appendChild(sec); });
      split2(root); reveal(root); (function at5() { if (tr5) tr5.attach(root); else setTimeout(at5, 300); })();
      if ('IntersectionObserver' in W) {
        var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { var k = e.target.id; if (!seen[k]) { seen[k] = 1; nseen++;  pt.textContent = 'Sezioni viste ' + nseen + '/' + secs.length; fill.style.width = Math.round(nseen / secs.length * 100) + '%'; } var idx = secs.map(function (x) { return 'a3s-' + x.k; }).indexOf(k); Array.prototype.forEach.call(chips.children, function (c, i) { c.classList.toggle('on', i === idx); }); } }); }, { root: body, rootMargin: '-30% 0px -60% 0px' });
        Array.prototype.forEach.call(root.querySelectorAll('.a3-ds'), function (e) { io.observe(e); });
      }
    });
  }

  /* A7: su tablet il dossier ha una colonna laterale (ritratto, azioni, sezioni) e una principale; su telefono i due contenitori sono trasparenti (display: contents) */
  function split2(root) {
    if (root.querySelector(':scope > .a3-side')) return; var side = h('div', 'a3-side'), main = h('div', 'a3-main');
    Array.prototype.slice.call(root.children).forEach(function (c) { (c.classList.contains('a3-dh') || c.classList.contains('a5-slot') || c.classList.contains('a3-jump') ? side : main).appendChild(c); });
    root.appendChild(side); root.appendChild(main);
  }

  /* ---------- HUB / MANTELLO ---------- */
  function renderHub() {
    frame(); var s = A3(), v = BY[s.id]; if (!v) { body.appendChild(h('div', 'empty', 'Voce non trovata.')); return; }
    api.setTitle(v.n, v.t === 'h' ? 'Hub di identità' : 'Mantello');
    var root = h('div', 't-' + v.t); body.appendChild(root); var hd = h('header', 'a3-dh'); var em = h('div', 'em'); em.appendChild(emblem(v, true)); hd.appendChild(em); paintAny(em, v, true);
    var t = h('div', 't'); t.appendChild(h('span', 'kick', v.t === 'h' ? 'Hub di identità' : 'Mantello')); t.appendChild(h('h1', '', v.n)); hd.appendChild(t); root.appendChild(hd);
    var acts = h('div', 'a5-slot'); root.appendChild(acts); withA5(function (m) { if (root.isConnected && ST.a3 === s) acts.appendChild(m.acts(s.id)); });
    var holder = h('div', 'a3-load', 'Caricamento…'); root.appendChild(holder);
    dossier(s.id, function (d) {
      if (ST.a3 !== s || !root.isConnected) return; holder.remove();
      if (!d) { root.appendChild(h('div', 'empty', 'Dossier non disponibile.')); return; }
      var note = h('p', 'a3-note', v.t === 'h' ? 'L’hub non è un personaggio e non aggiunge relazioni narrative: raccoglie le identità che condividono il nome. Le co-apparizioni non sono relazioni.' : 'Un mantello è un titolo: i suoi titolari sono identità distinte e non vengono unificate.'); root.appendChild(note);
      var ids = (v.t === 'h' ? d.membri : d.titolari.map(function (x) { return x.identita; })).slice(); if (v.t === 'h') ids.sort(function (a, b) { return (BY[a] ? 0 : 1) - (BY[b] ? 0 : 1); });
      var wrap = h('div', 'a3-hubs'); root.appendChild(wrap);
      ids.forEach(function (id, i) {
        var m = BY[id], c = m ? btn('a3-hc rev t-' + m.t, null, function () { openId(id); }) : h('div', 'a3-hc off');
        if (m) { var hm = h('span', 'a3-hm'); hm.appendChild(emblem(m, false)); c.appendChild(hm); paintRit(hm, id, false); }
        if (v.t === 'm') c.appendChild(h('span', 'kick', (i + 1) + '° titolare')); c.appendChild(h('b', '', m ? m.n : 'Scheda non ancora disponibile'));
        if (m) { c.appendChild(h('span', 'soft', (m.u ? uniNome(m.u) + ' · ' : '') + m.a + ' apparizioni')); var line = h('span', 'soft'); c.appendChild(line); dossier(id, function (dd) { if (!dd) return; var idf = (dd.sec.identita || []).filter(function (f) { return f.l === 'Interpreti'; })[0]; if (idf) line.textContent = 'Interprete: ' + idf.t.join(''); }); }
        else c.appendChild(h('span', 'soft', 'Segnaposto previsto, nessun dato verificato.'));
        wrap.appendChild(c);
      });
      /* «Da non confondere» (omonimie irrilevanti) non viene più mostrato negli hub: resta nei dati (d.esclusi) */
      if (srcVisible(d)) { var vs = h('section', 'a3-ds'); vs.appendChild(h('h2', '', 'Fonti e riferimenti')); vs.appendChild(srcBlock(d)); root.appendChild(vs); }
      reveal(root);
    });
  }

  /* ---------- regia ---------- */
  function renderRit() {
    frame(); api.setTitle('Ritratti privati', 'TVA Atlas'); var host = h('div', 'a3-ritmgr'); body.appendChild(host);
    withRit(function (r) { r.renderManager(host, function (i) { return BY[i] && BY[i].n; }); });
  }
  /* A4.1: Multiverso / Nexus / Percorso — modulo lazy atlante2/a4.js */
  var A4L = 0, A4Q = [];
  function withA4(fn) {
    if (W.tvaA4) return fn(W.tvaA4); A4Q.push(fn); if (A4L) return; A4L = 1; if (!D.getElementById('a4-css')) { var lk = D.createElement('link'); lk.id = 'a4-css'; lk.rel = 'stylesheet'; lk.href = BASE + 'a4.css'; D.head.appendChild(lk); }
    var sc = D.createElement('script'); sc.src = BASE + 'a4.js'; sc.async = true; sc.onload = function () { var q = A4Q.splice(0); q.forEach(function (f) { f(W.tvaA4); }); }; sc.onerror = function () { A4L = 0; A4Q.length = 0; frame(); body.appendChild(h('div', 'empty', 'Modulo Multiverso non disponibile.')); }; D.head.appendChild(sc);
  }
  /* A5: preferiti, raccolte, progressione — modulo lazy atlante2/a5.js */
  var A5L = 0, A5Q = [];
  function withA5(fn) {
    if (W.tvaA5) return fn(W.tvaA5); A5Q.push(fn); if (A5L) return; A5L = 1; if (!D.getElementById('a5-css')) { var lk = D.createElement('link'); lk.id = 'a5-css'; lk.rel = 'stylesheet'; lk.href = BASE + 'a5.css'; D.head.appendChild(lk); }
    var sc = D.createElement('script'); sc.src = BASE + 'a5.js'; sc.async = true; sc.onload = function () { var q = A5Q.splice(0); q.forEach(function (f) { if (W.tvaA5) f(W.tvaA5); }); }; sc.onerror = function () { A5L = 0; A5Q.length = 0; }; D.head.appendChild(sc);
  }
  function a5view(k) { return function () { frame(); body.appendChild(h('div', 'a3-load', 'Caricamento…')); var st = A3(); withA5(function (m) { if (ST.a3 !== st) return; m[k](); }); }; }
  function a4view(k) { return function () { frame(); body.appendChild(h('div', 'a3-load', 'Caricamento…')); var st = A3(); withA4(function (m) { if (ST.a3 !== st) return; m[k](); }); }; }
  /* Titoli delle schede: mai parole spezzate. overflow-wrap resta «normal»; se una parola e' piu' larga della scheda si riduce il corpo (min 9 px). */
  function fitTitles(root) {
    var bs = (root || D).querySelectorAll('.a3-tile .t b, .a3-li b'), i, b, fs;
    for (i = 0; i < bs.length; i++) {
      b = bs[i]; if (b.dataset.fit || !b.clientWidth) continue;
      fs = parseFloat(W.getComputedStyle(b).fontSize) || 12;
      while (b.scrollWidth > b.clientWidth + 1 && fs > 9) { fs -= 0.5; b.style.fontSize = fs + 'px'; }
      b.dataset.fit = '1';
    }
  }
  var fitTm = 0; function fitSoon() { if (fitTm) return; fitTm = W.requestAnimationFrame(function () { fitTm = 0; try { fitTitles(); } catch (e) { /* ok */ } }); }
  try { new W.MutationObserver(fitSoon).observe(D.body, { childList: true, subtree: true }); W.addEventListener('resize', function () { D.querySelectorAll('[data-fit]').forEach(function (n) { n.removeAttribute('data-fit'); n.style.fontSize = ''; }); fitSoon(); }); } catch (e) { /* ok */ }
  W.tvaFitTitles = fitTitles;
  W.tvaA3Ctx = function () { return { a5: withA5, dossier: dossier, h: h, btn: btn, BY: BY, ORD: ORD, emblem: emblem, paintAny: paintAny, paintRit: paintRit, tile: tile, uniNome: uniNome, uniCont: uniCont, uniHue: uniHue, natIdx: natIdx, ORBCLR: ORBCLR, openId: openId, frame: frame, api: api, search: search, get: get, A3: A3, body: body, get IDX() { return IDX; } }; };
  var VIEWS = { rit: renderRit, home: renderHome, cat: renderCat, search: renderSearch, dbx: renderDbx, dos: renderDossier, hub: renderHub, mv: a4view('mv'), nx: a4view('nx'), pc: a4view('pc'), cp: a4view('cp'), pf: a5view('viewPF'), pr: a5view('viewPR') };
  W.tvaA3 = {
    render: function () { ensure(function () { (VIEWS[A3().v] || renderHome)(); reveal(body); }); },
    label: function (s) { var a = s.a3 || {}; if (a.v === 'dos' || a.v === 'hub') return (BY[a.id] && BY[a.id].n) || 'Dossier'; if (a.v === 'cat') return 'Catalogo'; if (a.v === 'rit') return 'Ritratti privati'; if (a.v === 'mv') return 'Osservatorio del Multiverso'; if (a.v === 'nx') return 'TVA Nexus'; if (a.v === 'pc') return 'Percorso'; if (a.v === 'cp') return 'Confronto universi'; if (a.v === 'pf') return 'Preferiti e raccolte'; if (a.v === 'pr') return 'Progressione'; if (a.v === 'search') return 'Ricerca'; if (a.v === 'dbx') return (BY[a.id] && BY[a.id].n) || 'Scheda'; return 'TVA Atlas'; },
    ctx: function () { return W.tvaA3Ctx(); }, open: openId, go: function (pid, cb) { ensure(function () { var r = resolve(pid, null); if (r) openId(r); if (cb) cb(!!r); }); }, search: function (q) { return IDX ? search(q) : null; }, state: function () { return { idx: !!IDX, shards: Object.keys(SH).length }; }, ensure: ensure
  };
  if (W.tvaA3Boot) W.tvaA3Boot();
})();
