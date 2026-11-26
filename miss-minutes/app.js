/* Miss Minutes mm5 — pagina (controller UI). Nessun innerHTML: tutto il testo passa da textContent / nodi DOM.
   Dati dell'app solo in lettura tramite window.parent.tvaMissMinutesHost (stessa origine). */
(function () {
  'use strict';
  var D = document, $ = function (id) { return D.getElementById(id); };
  var host = null; try { host = window.parent !== window && window.parent.tvaMissMinutesHost && window.parent.tvaMissMinutesHost.version === 1 ? window.parent.tvaMissMinutesHost : null; } catch (e) { host = null; }
  var store, eng, gw, busy = false, lastCtx = [], waitCtl = null, waitNode = null, errNode = null, heroSvg = null, speakingNode = null;
  var diag = { last: null }, extra = null, prevView = 'home', maxH = 0;
  /* Stato dell'interfaccia (schermata, bozza, scorrimento) e registro del ciclo di vita della pagina. Chiave separata dalla
     cronologia: nessuna migrazione, nessuna scrittura sulle conversazioni. Nessun testo delle conversazioni, solo UI. */
  var UIK = 'marvel-ultimate-timeline-miss-minutes-ui-v1', ui = { view: 'home', prev: 'home', draft: '', scroll: {}, stick: {}, sid: null, life: [], boots: 0, restored: false };
  function uiLoad() { try { var r = JSON.parse(localStorage.getItem(UIK) || 'null'); if (r && typeof r === 'object') ui = Object.assign(ui, r); } catch (e) {} if (!Array.isArray(ui.life)) ui.life = []; if (!ui.scroll || typeof ui.scroll !== 'object') ui.scroll = {}; if (!ui.stick || typeof ui.stick !== 'object') ui.stick = {}; }
  function uiSave() { try { ui.t = Date.now(); localStorage.setItem(UIK, JSON.stringify(ui)); } catch (e) {} }
  function life(ev) { ui.life.push({ e: ev, t: Date.now() }); if (ui.life.length > 14) ui.life = ui.life.slice(-14); uiSave(); }
  function wipeUi() { ui.draft = ''; ui.scroll = {}; ui.stick = {}; ui.sid = null; try { $('mmQ').value = ''; } catch (e) {} uiSave(); }
  var SCR = { home: 'vHome', chat: 'mmChat', hist: 'vHist', set: 'vSet' };
  function capture() { try { var n = $(SCR[view]); if (n) { ui.scroll[view] = n.scrollTop; ui.stick[view] = n.scrollHeight - n.scrollTop - n.clientHeight < 48; } ui.draft = $('mmQ').value; ui.view = view; ui.prev = prevView; ui.sid = store ? store.state.active : null; } catch (e) {} }
  function flushUi(ev) { capture(); if (ev) life(ev); else uiSave(); }
  function restoreScroll(v) {
    var n = $(SCR[v]); if (!n) return; var go = function () { if (ui.stick[v] && v === 'chat') n.scrollTop = n.scrollHeight; else if (typeof ui.scroll[v] === 'number') n.scrollTop = ui.scroll[v]; };
    go(); requestAnimationFrame(function () { go(); setTimeout(go, 200); });
  }

  var CFG = window.MISS_MINUTES_CONFIG || { endpoint: '' };
  var EP_RE = /^https:\/\/[a-z0-9-]+(\.[a-z0-9-]+)?\.workers\.dev$/;
  function endpointNow() { var e = CFG.endpoint || (store && store.state.prefs.endpoint) || ''; return EP_RE.test(e) ? e : ''; }
  function makeGw() { return window.MMGateway.create({ endpoint: endpointNow(), storage: window.sessionStorage }); }
  var VERSION = 'mm6.1';

  /* ---------- utilita' ---------- */
  function el(tag, cls, txt) { var n = D.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; return n; }
  function btn(cls, label) { var b = el('button', cls); b.type = 'button'; if (label) b.setAttribute('aria-label', label); return b; }
  function banner(t) { var b = $('mmBanner'); b.hidden = !t; b.textContent = t || ''; }
  function scrollEnd() { var c = $('mmChat'); c.scrollTop = c.scrollHeight; }
  var toastT = null;
  function toast(t) { var old = D.querySelector('.mm-toast'); if (old) old.remove(); var n = el('div', 'mm-toast', t); n.setAttribute('role', 'status'); $('mmRoot').appendChild(n); clearTimeout(toastT); toastT = setTimeout(function () { n.remove(); }, 1800); }

  /* ---------- icone (SVG di linea, nessuna emoji) ---------- */
  var SVG = 'http://www.w3.org/2000/svg';
  function mk(tag, attrs, parent) { var n = D.createElementNS(SVG, tag); for (var k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; }
  var IC = {
    chat: 'M4 5h16a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H10l-4 3.5V16H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z M8 10h8 M8 13h5',
    history: 'M12 3a9 9 0 1 1-8.5 6 M3 4v5h5 M12 7.5V12l3 2',
    book: 'M4 5.5C6.5 4.5 9.5 4.5 12 6c2.5-1.5 5.5-1.5 8-.5V19c-2.5-1-5.5-1-8 .5-2.5-1.5-5.5-1.5-8-.5z M12 6v13.5',
    send: 'M21 3L3 10.5l7 2.5 2.5 7z M10 13l11-10',
    plus: 'M12 5v14M5 12h14',
    mic: 'M12 3a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V6a3 3 0 0 1 3-3z M5 11a7 7 0 0 0 14 0 M12 18v3',
    stop: 'M7 7h10v10H7z',
    copy: 'M9 9h11v11H9z M5 15V4h11',
    refresh: 'M20 12a8 8 0 1 1-2.6-5.9 M20 4v5h-5',
    volume: 'M4 9.5h3.5L12 6v12l-4.5-3.5H4z M15.5 9a4 4 0 0 1 0 6 M18 6.5a8 8 0 0 1 0 11',
    more: 'M12 5v.01 M12 12v.01 M12 19v.01',
    back: 'M15 5l-7 7 7 7',
    down: 'M6 9l6 6 6-6',
    right: 'M9 5l7 7-7 7',
    search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z M16 16l5 5',
    trash: 'M4 7h16 M9 7V4h6v3 M6 7l1 13h10l1-13 M10 11v6 M14 11v6',
    edit: 'M4 20l1-4L16 5l3 3L8 19z M14 7l3 3',
    gear: 'M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7z M19.4 13a7.5 7.5 0 0 0 0-2l2-1.5-2-3.5-2.3.9a7.5 7.5 0 0 0-1.7-1L15 3h-4l-.4 2.9a7.5 7.5 0 0 0-1.7 1L6.6 6 4.6 9.5l2 1.5a7.5 7.5 0 0 0 0 2l-2 1.5 2 3.5 2.3-.9c.5.4 1.1.7 1.7 1L11 21h4l.4-2.9c.6-.3 1.2-.6 1.7-1l2.3.9 2-3.5z',
    warn: 'M12 3l10 18H2z M12 10v5 M12 18v.01',
    layers: 'M12 3l9 5-9 5-9-5z M3 12.5l9 5 9-5 M3 17l9 5 9-5',
    scales: 'M12 4v16 M7 20h10 M5 7h14 M5 7l-3 7a3 3 0 0 0 6 0z M19 7l-3 7a3 3 0 0 0 6 0z',
    spark: 'M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z',
    archive: 'M3 5h18v4H3z M5 9v10h14V9 M10 13h4',
    brain: 'M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-2 3 3 3 0 0 0 1.5 2.6A3 3 0 0 0 9 19z M15 4a3 3 0 0 1 3 3v1a3 3 0 0 1 2 3 3 3 0 0 1-1.5 2.6A3 3 0 0 1 15 19z',
    shield: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z M9 12l2 2 4-4',
    lines: 'M4 6h16 M4 12h12 M4 18h8',
    info: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 11v5 M12 8v.01',
    wrench: 'M14.5 6.5a4 4 0 0 0-5 5L3 18l3 3 6.5-6.5a4 4 0 0 0 5-5l-2.5 2.5-2.5-.5-.5-2.5z',
    eye: 'M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z',
    close: 'M6 6l12 12M18 6L6 18',
    check: 'M5 12l4 4 10-10',
    link: 'M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1 M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1'
  };
  function ic(name) { var s = mk('svg', { viewBox: '0 0 24 24', class: 'ic', 'aria-hidden': 'true', focusable: 'false' }); var d = IC[name] || IC.info; if (name === 'stop') mk('path', { d: d, class: 'fill' }, s); else mk('path', { d: d }, s); return s; }
  function hydrate(root) {
    [].forEach.call(root.querySelectorAll('[data-ic]'), function (n) { n.appendChild(ic(n.getAttribute('data-ic'))); if (n.getAttribute('data-label')) n.appendChild(el('span', '', n.getAttribute('data-label'))); n.removeAttribute('data-ic'); });
  }
  function iconBtn(name, label, cls) { var b = btn(cls || '', label); b.title = label; b.appendChild(ic(name)); return b; }

  /* ---------- mascotte olografica originale ---------- */
  var uid = 0, ART = null;
  // Cuore del design: un cronografo-ologramma di vetro scuro e ambra, con "visiera" luminosa che cambia espressione.
  // Opzionale: se esiste mascot/manifest.json (immagini fornite dall'utente) vengono usate al posto del disegno.
  function holo(o) {
    o = o || {}; var id = 'h' + (++uid), head = !!o.head;
    var s = mk('svg', { viewBox: head ? '36 46 128 128' : '0 0 200 260', 'aria-hidden': 'true', focusable: 'false' });
    s.setAttribute('data-state', o.state || 'idle');
    var df = mk('defs', {}, s);
    var rb = mk('radialGradient', { id: id + 'b', cx: '.5', cy: '.38', r: '.7' }, df); mk('stop', { offset: 0, 'stop-color': '#3b2008' }, rb); mk('stop', { offset: 1, 'stop-color': '#0c0602' }, rb);
    var lr = mk('linearGradient', { id: id + 'r', x1: 0, y1: 0, x2: 1, y2: 1 }, df); mk('stop', { offset: 0, 'stop-color': '#ffd98a' }, lr); mk('stop', { offset: .55, 'stop-color': '#f59a23' }, lr); mk('stop', { offset: 1, 'stop-color': '#b4560a' }, lr);
    var lm = mk('linearGradient', { id: id + 'm', x1: 0, y1: 1, x2: 0, y2: 0 }, df); mk('stop', { offset: 0, 'stop-color': '#ff9f1c', 'stop-opacity': .34 }, lm); mk('stop', { offset: 1, 'stop-color': '#ff9f1c', 'stop-opacity': 0 }, lm);
    var lw = mk('linearGradient', { id: id + 'w', x1: 0, y1: 0, x2: 0, y2: 1 }, df); mk('stop', { offset: 0, 'stop-color': '#ffe2a8', 'stop-opacity': 0 }, lw); mk('stop', { offset: .5, 'stop-color': '#ffe2a8', 'stop-opacity': .32 }, lw); mk('stop', { offset: 1, 'stop-color': '#ffe2a8', 'stop-opacity': 0 }, lw);
    var pt = mk('pattern', { id: id + 'p', width: 4, height: 4, patternUnits: 'userSpaceOnUse' }, df); mk('rect', { x: 0, y: 0, width: 4, height: 1.3, fill: '#000', 'fill-opacity': .38 }, pt);
    var cp = mk('clipPath', { id: id + 'c' }, df); mk('circle', { cx: 100, cy: 110, r: 56 }, cp);
    if (!head) {
      mk('polygon', { points: '62,238 138,238 122,150 78,150', fill: 'url(#' + id + 'm)' }, s);
      mk('ellipse', { cx: 100, cy: 240, rx: 70, ry: 11, fill: 'rgba(255,150,30,.14)', stroke: '#f59a23', 'stroke-width': 2, class: 'holo-ring' }, s);
      mk('ellipse', { cx: 100, cy: 240, rx: 48, ry: 7, fill: 'none', stroke: '#ffc766', 'stroke-width': 1.4, 'stroke-opacity': .8, class: 'holo-ring2' }, s);
    }
    var g = mk('g', { class: head ? '' : 'holo-float' }, s);
    if (!head) {
      // Personaggio originale: orologio retro-cartoon con braccia, guanti, gambe e scarpe (non riproduce personaggi esistenti)
      var LIMB = { fill: 'none', stroke: '#ffb347', 'stroke-width': 5.5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' };
      function glove(parent, cx, cy, flip) {
        var gg = mk('g', {}, parent), k = flip ? -1 : 1;
        mk('rect', { x: cx - 7, y: cy - 13, width: 14, height: 8, rx: 3, fill: '#ffe7b8', stroke: '#b4560a', 'stroke-width': 1.4 }, gg);
        mk('ellipse', { cx: cx, cy: cy, rx: 9.5, ry: 9, fill: '#fff4dc', stroke: '#b4560a', 'stroke-width': 1.5 }, gg);
        mk('ellipse', { cx: cx + 8.5 * k, cy: cy - 1, rx: 3.6, ry: 6, fill: '#fff4dc', stroke: '#b4560a', 'stroke-width': 1.3, transform: 'rotate(' + (22 * k) + ' ' + (cx + 8.5 * k) + ' ' + (cy - 1) + ')' }, gg);
        mk('path', { d: 'M' + (cx - 3) + ' ' + (cy + 2) + 'v6 M' + (cx + 2) + ' ' + (cy + 2) + 'v7', stroke: '#b4560a', 'stroke-width': 1.1, 'stroke-linecap': 'round', fill: 'none' }, gg);
      }
      var legL = mk('g', { class: 'm-leg m-leg-l' }, g), legR = mk('g', { class: 'm-leg m-leg-r' }, g);
      mk('path', Object.assign({ d: 'M88 148L84 212' }, LIMB), legL); mk('ellipse', { cx: 77, cy: 221, rx: 15, ry: 8, fill: '#ffe7b8', stroke: '#b4560a', 'stroke-width': 1.6 }, legL); mk('path', { d: 'M70 217q7-4 14 0', fill: 'none', stroke: '#b4560a', 'stroke-width': 1.2 }, legL);
      mk('path', Object.assign({ d: 'M112 148L116 212' }, LIMB), legR); mk('ellipse', { cx: 123, cy: 221, rx: 15, ry: 8, fill: '#ffe7b8', stroke: '#b4560a', 'stroke-width': 1.6 }, legR); mk('path', { d: 'M116 217q7-4 14 0', fill: 'none', stroke: '#b4560a', 'stroke-width': 1.2 }, legR);
      var armL = mk('g', { class: 'm-arm m-arm-l' }, g); mk('path', Object.assign({ d: 'M46 96Q22 100 24 126' }, LIMB), armL); glove(armL, 24, 134, true);
      var armR = mk('g', { class: 'm-arm m-arm-r' }, g); mk('path', Object.assign({ d: 'M154 96Q180 92 178 66' }, LIMB), armR); glove(armR, 178, 58, false);
      mk('rect', { x: 91, y: 24, width: 18, height: 11, rx: 3.5, fill: '#2a1608', stroke: '#f59a23', 'stroke-width': 2.4 }, g);
    }
    var f = mk('g', { class: head ? '' : 'holo-flick', transform: head ? '' : 'translate(0,-18)' }, g);
    mk('circle', { cx: 100, cy: 110, r: 58, fill: 'url(#' + id + 'b)' }, f);
    mk('circle', { cx: 100, cy: 110, r: 58, fill: 'none', stroke: 'url(#' + id + 'r)', 'stroke-width': 5 }, f);
    mk('circle', { cx: 100, cy: 110, r: 49, fill: 'none', stroke: '#ffc766', 'stroke-opacity': .3, 'stroke-width': 1 }, f);
    var tk = mk('g', { stroke: '#ffc766', 'stroke-linecap': 'round', 'stroke-opacity': .75 }, f);
    for (var i = 0; i < 12; i++) { var a = i * Math.PI / 6, r1 = i % 3 ? 44 : 41, r2 = 48; mk('line', { x1: 100 + Math.sin(a) * r1, y1: 110 - Math.cos(a) * r1, x2: 100 + Math.sin(a) * r2, y2: 110 - Math.cos(a) * r2, 'stroke-width': i % 3 ? 1.4 : 2.6 }, tk); }
    if (!head) {
      var ob = mk('g', { class: 'o-orbit' }, f);
      mk('circle', { cx: 100, cy: 36, r: 3.6, fill: '#ffd98a' }, ob); mk('circle', { cx: 100, cy: 184, r: 2.6, fill: '#f59a23' }, ob);
      mk('circle', { cx: 100, cy: 110, r: 70, fill: 'none', stroke: '#f59a23', 'stroke-opacity': .22, 'stroke-dasharray': '2 6' }, ob);
      var hh = mk('g', { class: 'o-hand-h' }, f); mk('line', { x1: 100, y1: 110, x2: 100, y2: 93, stroke: '#ffc766', 'stroke-width': 3.2, 'stroke-linecap': 'round' }, hh);
      var hm = mk('g', { class: 'o-hand-m' }, f); mk('line', { x1: 100, y1: 110, x2: 100, y2: 80, stroke: '#ffd98a', 'stroke-width': 2.2, 'stroke-linecap': 'round' }, hm);
    }
    mk('circle', { cx: 100, cy: 110, r: 3.4, fill: '#ffd98a' }, f);
    var ey = mk('g', { fill: '#ffd98a' }, f);
    mk('ellipse', { cx: 80, cy: 128, rx: 9.5, ry: 5.5, class: 'o-eye o-eye-l' }, ey); mk('ellipse', { cx: 120, cy: 128, rx: 9.5, ry: 5.5, class: 'o-eye o-eye-r' }, ey);
    var mo = { fill: 'none', stroke: '#ffd98a', 'stroke-width': 3, 'stroke-linecap': 'round' };
    mk('path', Object.assign({ d: 'M82 144Q100 157 118 144', class: 'o-smile' }, mo), f);
    mk('ellipse', { cx: 100, cy: 148, rx: 11, ry: 7, fill: '#ffd98a', class: 'o-open' }, f);
    mk('path', Object.assign({ d: 'M84 152Q100 138 116 152', class: 'o-frown' }, mo), f);
    mk('path', Object.assign({ d: 'M86 147H114', class: 'o-flat' }, mo), f);
    mk('path', Object.assign({ d: 'M86 147q7-6 14 0t14 0', class: 'o-wavy' }, mo), f);
    if (!head) {
      var gl = { 'font-size': 30, 'font-weight': 800, fill: '#ffd98a', 'text-anchor': 'middle', 'font-family': 'system-ui,sans-serif' };
      [['!', 'g-err'], ['?', 'g-q'], ['zZ', 'g-z']].forEach(function (p) { var t = mk('text', Object.assign({ x: 164, y: 40, class: 'o-glyph ' + p[1] }, gl), g); t.textContent = p[0]; });
    }
    mk('circle', { cx: 100, cy: 110, r: 56, fill: 'url(#' + id + 'p)' }, f);
    if (!head) { var sw = mk('g', { 'clip-path': 'url(#' + id + 'c)' }, f); mk('rect', { x: 40, y: 40, width: 120, height: 44, fill: 'url(#' + id + 'w)', class: 'holo-sweep' }, sw); }
    return s;
  }
  function artImg(state) {
    if (!ART) return null; var f = ART[state] || ART.idle; if (!f || !/^[\w.\-]+\.(png|webp|svg|jpg|jpeg)$/i.test(f)) return null;
    var w = el('div', 'holo-art holo-float'); var i = el('img'); i.alt = ''; i.src = 'mascot/' + f; i.decoding = 'async'; w.appendChild(i); w.setAttribute('data-state', state || 'idle'); return w;
  }
  function bigMascot(state) { return artImg(state) || holo({ state: state }); }
  function setMood(node, m) { if (node) node.setAttribute('data-state', m); }
  function mood(m) { setMood(heroSvg, m); }
  // avatar piccolo: simbolo condiviso (una sola definizione, riusata con <use>)
  // avatar: <use> di un simbolo condiviso. Il viewBox esterno parte da 0,0 (l'offset di mm5 lo faceva apparire decentrato).
  function avatar(state) {
    var w = el('div', 'mm-av'); w.setAttribute('aria-hidden', 'true');
    if (state) { w.appendChild(holo({ head: true, state: state })); return w; }
    var s = mk('svg', { viewBox: '0 0 128 128', focusable: 'false' }, w); var u = mk('use', { href: '#mm-head', width: 128, height: 128 }, s); u.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', '#mm-head'); return w;
  }
  function installHeadSymbol() { var hs = holo({ head: true }); var sp = mk('svg', { width: 0, height: 0, style: 'position:absolute', 'aria-hidden': 'true' }); var sy = mk('symbol', { id: 'mm-head', viewBox: '36 46 128 128' }, sp); [].slice.call(hs.childNodes).forEach(function (n) { sy.appendChild(n); }); D.body.appendChild(sp); }
  function drawBackground() {
    var s = mk('svg', { viewBox: '0 0 400 380', preserveAspectRatio: 'xMidYMin slice' }); var seed = 7; function rnd() { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; }
    var g = mk('linearGradient', { id: 'bgsky', x1: 0, y1: 0, x2: 0, y2: 1 }, mk('defs', {}, s)); mk('stop', { offset: 0, 'stop-color': '#2a1507' }, g); mk('stop', { offset: 1, 'stop-color': '#070402' }, g);
    mk('rect', { width: 400, height: 380, fill: 'url(#bgsky)' }, s);
    for (var i = 0, x = -10; x < 410; i++) { var w = 22 + rnd() * 38, h = 70 + rnd() * 190, y = 330 - h; mk('rect', { x: x, y: y, width: w, height: h, fill: '#0f0905', stroke: 'rgba(245,154,35,.18)' }, s); for (var wy = y + 8; wy < 322; wy += 11) for (var wx = x + 5; wx < x + w - 5; wx += 8) if (rnd() > .72) mk('rect', { x: wx, y: wy, width: 3, height: 4, fill: '#f59a23', opacity: (.25 + rnd() * .55).toFixed(2) }, s); x += w + 3; }
    mk('rect', { y: 322, width: 400, height: 58, fill: '#070402' }, s);
    $('mmBg').appendChild(s);
  }

  /* ---------- rendering testo (solo DOM) ---------- */
  function inline(parent, t) {
    t = String(t).replace(/`/g, '');
    t.split(/(\*\*[^*]+\*\*)/).forEach(function (p) {
      if (!p) return;
      if (/^\*\*[^*]+\*\*$/.test(p)) parent.appendChild(el('strong', '', p.slice(2, -2))); else parent.appendChild(D.createTextNode(p.replace(/\*/g, '')));
    });
  }
  function rich(text, lines) {
    var root = el('div', 'mm-rich'), list = null, para = [];
    function flush() { if (para.length) { var p = el('p'); inline(p, para.join(' ')); root.appendChild(p); para = []; } }
    String(text).split(/\r?\n/).forEach(function (ln) {
      var t = ln.trim(), m;
      if (!t) { flush(); list = null; return; }
      if ((m = /^#{1,4}\s+(.+)$/.exec(t))) { flush(); list = null; var h = el('div', 'mm-h'); inline(h, m[1]); root.appendChild(h); return; }
      if ((m = /^(?:[-*•]|\d+[.)])\s+(.+)$/.exec(t))) {
        flush(); var ord = /^\d/.test(t);
        if (!list || list.tagName !== (ord ? 'OL' : 'UL')) { list = el(ord ? 'ol' : 'ul'); root.appendChild(list); }
        var li = el('li'); inline(li, m[1]); list.appendChild(li); return;
      }
      list = null; para.push(t); if (lines) flush();
    });
    flush(); return root;
  }

  /* ---------- voce (ascolto) ---------- */
  function stripForSpeech(t) { return String(t).replace(/\[[^\]]*\]/g, '').replace(/[*#`]/g, '').slice(0, 900); }
  function stopSpeaking() { try { window.speechSynthesis && window.speechSynthesis.cancel(); } catch (e) {} $('mmRoot').classList.remove('speaking'); if (speakingNode) { speakingNode.setAttribute('aria-pressed', 'false'); speakingNode = null; } mood('idle'); }
  function speak(text, node) {
    try {
      if (!window.speechSynthesis) { toast('Lettura vocale non supportata su questo dispositivo.'); return; }
      var same = node && speakingNode === node; stopSpeaking(); if (same) return;
      var u = new SpeechSynthesisUtterance(stripForSpeech(text)); u.lang = 'it-IT';
      u.onend = u.onerror = function () { if (speakingNode === node || !node) stopSpeaking(); };
      speakingNode = node || null; if (node) node.setAttribute('aria-pressed', 'true'); $('mmRoot').classList.add('speaking'); mood('talk'); window.speechSynthesis.speak(u);
    } catch (e) { stopSpeaking(); }
  }
  function copyText(t) {
    var done = function () { toast('Copiato negli appunti'); };
    function fallback() { try { var ta = el('textarea'); ta.value = t; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;opacity:0;top:0'; D.body.appendChild(ta); ta.select(); var ok = D.execCommand && D.execCommand('copy'); ta.remove(); ok ? done() : toast('Copia non riuscita: seleziona il testo a mano.'); } catch (e) { toast('Copia non riuscita.'); } }
    try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(done, fallback); else fallback(); } catch (e) { fallback(); }
  }

  /* ---------- schermate e navigazione ---------- */
  var view = 'home';
  function setView(v, o) {
    if (v !== view) { capture(); if (!(o && o.noPush)) prevView = view; }
    view = v; $('mmRoot').setAttribute('data-view', v); closeMenu();
    $('navChat').setAttribute('aria-current', v === 'home' || v === 'chat' ? 'page' : 'false'); $('navHist').setAttribute('aria-current', v === 'hist' ? 'page' : 'false'); $('navAtl').setAttribute('aria-current', 'false');
    if (v === 'home') renderHome(); if (v === 'chat') render(); if (v === 'hist') renderHistory(); if (v === 'set') renderSettings();
    var vw = SCR[v]; if (v !== 'chat') $(vw).scrollTop = 0;
    ui.view = v; ui.prev = prevView; uiSave(); updateDown();
  }
  // Indietro: torna alla schermata da cui si proveniva (non chiude l'assistente)
  function goBack() { stopSpeaking(); var t = prevView; if (t === view || ['home', 'chat', 'hist', 'set'].indexOf(t) < 0 || (t === 'chat' && !hasChat())) t = hasChat() && view !== 'chat' ? 'chat' : 'home'; prevView = 'home'; setView(t, { noPush: true }); }
  function hasChat() { var s = store.current(); return !!(s && s.messages.length); }
  function openLink(link) {
    if (!host) { banner('Per aprire le schede usa Miss Minutes dall’app TVA Archives.'); return; }
    try { host.open(link); } catch (e) { banner('Collegamento non disponibile.'); }
  }
  function closeApp() { try { if (host) host.close(); else history.back(); } catch (e) {} }

  /* menu a comparsa */
  function openMenu(anchor, items) {
    var box = $('mmMenuBox'); while (box.firstChild) box.removeChild(box.firstChild);
    items.forEach(function (it) { var b = btn('', null); b.setAttribute('role', 'menuitem'); b.appendChild(ic(it.icon)); b.appendChild(el('span', '', it.label)); b.onclick = function () { closeMenu(); it.run(); }; box.appendChild(b); });
    box.hidden = false; anchor.setAttribute('aria-expanded', 'true'); box._anchor = anchor; var f = box.querySelector('button'); if (f) f.focus();
  }
  function closeMenu() { var box = $('mmMenuBox'); if (box.hidden) return; box.hidden = true; if (box._anchor) { box._anchor.setAttribute('aria-expanded', 'false'); } }

  /* ---------- home ---------- */
  var TOPICS = [
    { icon: 'chat', label: 'La storia di un personaggio', qs: ['Chi è Loki?', 'Raccontami le origini di Thor', 'Chi è Kang il Conquistatore?'] },
    { icon: 'layers', label: 'L’ordine di visione di un evento', qs: ['In che ordine guardo la Infinity Saga?', 'Cosa devo vedere prima di Avengers: Doomsday?', 'Da dove inizio con il multiverso?'] },
    { icon: 'book', label: 'I fumetti da leggere', qs: ['Quali fumetti leggo per conoscere Knull?', 'Ordine di lettura di Secret Wars', 'Fumetti essenziali su Spider-Man'] },
    { icon: 'scales', label: 'Un confronto tra personaggi', qs: ['Differenza tra Thor e Loki', 'Terra-616 e Terra-1610', 'Chi è più potente tra Thanos e Galactus?'] }
  ];
  function greet() { var h = new Date().getHours(); return (h < 6 ? 'Buonanotte' : h < 13 ? 'Buongiorno' : h < 18 ? 'Buon pomeriggio' : 'Buonasera') + ', Agente!'; }
  function buildHome() {
    $('mmMascot').appendChild(heroSvg = bigMascot('idle'));
    var w = $('mmWave'); for (var i = 0; i < 26; i++) { var b = el('i'); b.style.height = (4 + Math.round(Math.abs(Math.sin(i * 0.9)) * 14 + (i % 3) * 2)) + 'px'; b.style.animationDelay = (i * 0.07).toFixed(2) + 's'; w.appendChild(b); }
    var host2 = $('mmTopics');
    TOPICS.forEach(function (t, k) {
      var box = el('div', 'mm-topic'); box.setAttribute('data-open', 'false');
      var b = btn('', null); b.setAttribute('aria-expanded', 'false'); b.appendChild(ic(t.icon)); b.appendChild(el('span', '', t.label)); var ch = ic('right'); ch.setAttribute('class', 'ic chev'); b.appendChild(ch);
      var ul = el('ul'); ul.id = 'tp' + k; b.setAttribute('aria-controls', ul.id);
      t.qs.forEach(function (q) { var li = el('li'); var qb = btn('', null); qb.textContent = q; qb.onclick = function () { submit(q); }; li.appendChild(qb); ul.appendChild(li); });
      b.onclick = function () { var open = box.getAttribute('data-open') !== 'true'; [].forEach.call(host2.children, function (x) { x.setAttribute('data-open', 'false'); x.firstChild.setAttribute('aria-expanded', 'false'); }); box.setAttribute('data-open', open ? 'true' : 'false'); b.setAttribute('aria-expanded', open ? 'true' : 'false'); };
      box.appendChild(b); box.appendChild(ul); host2.appendChild(box);
    });
  }
  function renderHome() {
    $('mmGreet').textContent = greet();
    var r = $('mmResume'), s = store.current();
    if (s && s.messages.length) { r.hidden = false; while (r.firstChild) r.removeChild(r.firstChild); r.appendChild(ic('history')); r.appendChild(el('span', '', 'Riprendi: ' + s.title)); r.appendChild(ic('right')); r.onclick = function () { setView('chat'); }; } else r.hidden = true;
    $('mmMode').textContent = (onlineOK() ? 'AI online attiva · ' : 'Modalità locale · ') + (host ? 'dati dell’app collegati in sola lettura' : 'dati personali non collegati (apri Miss Minutes dall’app)');
  }

  /* ---------- conversazione ---------- */
  function renderMsg(m, isLast, canRegen) {
    var d = el('div', 'mm-msg ' + (m.role === 'user' ? 'user' : 'assistant'));
    if (m.role === 'user') { d.textContent = m.text; return d; }
    d.appendChild(avatar());
    var body = el('div', 'mm-body'); d.appendChild(body);
    body.appendChild(rich(m.text, !(m.tag && m.tag.indexOf('online') === 0)));
    if (m.refs && m.refs.length) {
      var r = el('div', 'mm-refs');
      m.refs.forEach(function (x) { var b = btn('mm-chip', null); b.appendChild(ic('book')); b.appendChild(el('span', '', x.label)); b.onclick = function () { openLink(x.link); }; r.appendChild(b); });
      body.appendChild(r);
    }
    if (m.flair) body.appendChild(el('div', 'mm-flair', m.flair));
    if (m.action) {
      var a = btn('mm-act', null); a.textContent = m.action.label; a.onclick = function () { a.disabled = true; m.action.run(); }; var w = el('div', 'mm-refs'); w.appendChild(a); body.appendChild(w);
    }
    var meta = el('div', 'mm-meta');
    if (m.tag) meta.appendChild(el('span', 'mm-tag' + (m.tag.indexOf('online') === 0 ? ' online' : ''), m.tag));
    var acts = el('div', 'mm-acts');
    var c = iconBtn('copy', 'Copia la risposta'); c.onclick = function () { copyText(m.text); }; acts.appendChild(c);
    if (isLast && canRegen) { var rg = iconBtn('refresh', 'Rigenera la risposta'); rg.onclick = regenerate; acts.appendChild(rg); }
    var l = iconBtn('volume', 'Ascolta la risposta'); l.setAttribute('aria-pressed', 'false'); l.onclick = function () { speak(m.text, l); }; acts.appendChild(l);
    meta.appendChild(acts); body.appendChild(meta);
    return d;
  }
  // mm6.1: dopo una risposta la vista parte dall'INIZIO del nuovo messaggio (come ChatGPT), senza scorrere in fondo
  var focusNext = false;
  function scrollToAnswerTop() {
    var c = $('mmChat'), a = c.querySelectorAll('.mm-msg.assistant'); if (!a.length) { scrollEnd(); return; }
    var n = a[a.length - 1]; c.scrollTop = Math.max(0, n.offsetTop - 8);
  }
  function updateDown() {
    var b = $('mmDown'), c = $('mmChat'); if (!b || !c) return;
    var far = view === 'chat' && c.scrollHeight - c.scrollTop - c.clientHeight > 120; b.hidden = !far;
  }
  function render(mode) {
    var c = $('mmChat'); while (c.firstChild) c.removeChild(c.firstChild); waitNode = null; errNode = null;
    var s = store.current(); var msgs = s ? s.messages : [];
    msgs.forEach(function (m, i) { if (extra && s && extra.sid === s.id && extra.i === i) m = Object.assign({}, m, { action: extra.action, flair: extra.flair }); c.appendChild(renderMsg(m, i === msgs.length - 1, i > 0 && msgs[i - 1].role === 'user' && !busy)); });
    if (msgs.length && msgs[msgs.length - 1].role === 'user' && !busy) showError({ code: 'pending' }, msgs[msgs.length - 1].text);
    if ((mode === 'answer' || focusNext) && !(msgs.length && msgs[msgs.length - 1].role === 'user')) {
      if (view === 'chat' && c.clientHeight) { focusNext = false; scrollToAnswerTop(); } else focusNext = true;
    } else scrollEnd();
    updateDown();
  }
  function appendLive(m, last) { var d = renderMsg(m, !!last, !!last); $('mmChat').appendChild(d); scrollEnd(); return d; }
  function dropRegenButtons() { [].forEach.call($('mmChat').querySelectorAll('.mm-acts button[aria-label="Rigenera la risposta"]'), function (b) { b.remove(); }); }

  /* ---------- risposta ---------- */
  function liveState() { try { return host ? host.live() : { items: [], note: '' }; } catch (e) { return { items: [], note: '' }; } }
  function convState(s) { var lv = liveState(); return { live: lv.items, liveNote: lv.note, lastEntities: store.state.prefs.memory ? ((s && s.last) || []) : [] }; }
  function onlineOK() { var p = store.state.prefs; return !!(p.online && p.consent && gw.available()); }
  var FUNC = /(?:^|[\s(])(?:il|lo|la|le|gli|i|un|uno|una|di|del|dello|della|dei|degli|delle|da|dal|dallo|dalla|con|e|ed|a|al|allo|alla|ai|che|contro|tra|fra|per|su|come|sia|o|ma|se)\s*$/i;
  function dupCount(t) { var m = String(t).match(/(^|[^A-Za-zÀ-ÿ'])([A-Za-zÀ-ÿ']{3,})\s+\2(?![A-Za-zÀ-ÿ'])/gi); return m ? m.length : 0; }
  // I marcatori [[id]] sono CITAZIONI: non sostituiscono mai il testo. Se il modello li usa al posto di un nome
  // (dopo articolo/preposizione) si inserisce il titolo; altrimenti il marcatore sparisce e resta solo il collegamento.
  function resolveRefs(text, ctx) {
    var refs = [], cited = [], markers = 0;
    var out = text.replace(/\s*\[\[([^\]]{1,60})\]\]/g, function (m, id, off, str) {
      markers++;
      var c = ctx.filter(function (x) { return x.id === id; })[0]; if (!c) return '';
      var l = eng.linkOf(id); if (l) refs.push({ label: c.title, link: l }); if (cited.indexOf(id) < 0) cited.push(id);
      return FUNC.test(str.slice(0, off)) ? ' ' + c.title : '';
    }).replace(/https?:\/\/\S+/g, '[link rimosso]');
    return { text: out.trim(), markers: markers, cited: cited, refs: refs.filter(function (r, i, a) { return a.findIndex(function (z) { return z.link === r.link; }) === i; }).slice(0, 5) };
  }

  // Decide se la domanda merita l'AI online (spiegazioni, confronti, ragionamenti, seguiti) o basta il motore locale
  var APP_INTENTS = /^(avanzamento|mancanti|progress|missing|live|classifiche|ratings|amici|friends|gioca|play|episodi|episodes|missioni|missions|saluto|personale|consigli|advice|scheda-?utente)/;
  // Con l'AI online attiva l'archivio locale risponde solo alle richieste semplici (scheda anagrafica, dato puntuale, dati dell'app);
  // domande teoriche, comparative, ipotetiche, sul futuro o contestuali vanno a Gemini con l'archivio come contesto.
  var COMPLEX = /\b(perche|come mai|come funziona|differenz\w*|confront\w*|parago\w*|contro|vs|versus|vinc\w+|batt\w+|sconfigg\w+|perd\w+|piu forte|piu potente|piu veloce|spiega\w*|raccont\w+|riassum\w+|teori\w*|ipotes\w*|indiscrezion\w*|rumor\w*|leak\w*|secondo te|pensi|credi|cosa succede\w*|cosa accad\w*|succeder\w*|accader\w*|sara|saranno|diventer\w*|torner\w*|morir\w*|apparir\w*|potrebbe|potrebbero|futuro|retcon|saga|evento|fumett\w+|easter egg|riferiment\w+|collegament\w+|connession\w+|ordine|da dove|conviene|canon\w*|origine|origini|storia|trama|significa\w*|ruolo|importanza|dopo|prima di|doomsday|secret wars)\b/;
  var SIMPLE = /^(chi e|chi sono|chi era|cos e|cosa e|che cos e|cosa sono|che poteri|quali poteri|poteri di|scheda|mostra|apri|dimmi di|parlami di|dove si trova|quando e uscit\w*|chi ha interpretato|chi interpreta|chi ha creato|quanti|quante|quali sono i miei)\b/;
  function needsDepth(q, ans, s) {
    if (ans.needsOnline) return true;
    if (ans.personal || APP_INTENTS.test(String(ans.intent || ''))) return false;
    var n = eng.norm(q), words = n.split(' ').filter(Boolean).length;
    if (ans.intent === 'confronto' || COMPLEX.test(n)) return true;
    var prev = s && s.messages ? s.messages.slice(-3, -1) : [];
    var follow = prev.some(function (m) { return m.role === 'assistant' && m.tag && m.tag.indexOf('online') === 0; });
    var refer = /\b(lui|lei|loro|lo|la|li|le|quello|quella|quelli|questo|questa|invece|anche|ancora|poi|altrimenti|confrontali|confrontalo|e se|e lui|e lei|prima)\b/.test(n);
    if (follow && words <= 12 && (refer || !eng.find(q, 1).length)) return true;
    if (ans.confidence < 0.75) return true;
    if (SIMPLE.test(n) && words <= 6) return false;
    return words >= 5;
  }

  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  /* streaming: la bolla della risposta si riempie man mano; nessuno scorrimento forzato (mm6.1: la vista parte dall'inizio del messaggio) */
  var live = null;
  function paintLive() {
    if (!live) return; live.raf = 0;
    var t = String(live.text).replace(/\s*\[\[[^\]]*$/, ''), rr = t; try { rr = resolveRefs(t, lastCtx).text; } catch (e) { /* testo grezzo */ }
    while (live.body.firstChild) live.body.removeChild(live.body.firstChild);
    var rc = rich(rr, false); live.body.appendChild(rc); var last = rc.lastElementChild || rc; last.appendChild(el('span', 'mm-caret')); updateDown();
  }
  function liveDelta(acc) {
    if (!live) {
      clearTransient(); var d = el('div', 'mm-msg assistant streaming'); d.setAttribute('aria-busy', 'true'); d.appendChild(avatar('talk'));
      var body = el('div', 'mm-body'); d.appendChild(body); $('mmChat').appendChild(d); live = { node: d, body: body, text: '', raf: 0 };
      mood('talk'); var c = $('mmChat'); c.scrollTop = Math.max(0, d.offsetTop - 8);
    }
    live.text = acc; if (!live.raf) live.raf = requestAnimationFrame(paintLive);
  }
  function endLive() { if (!live) return; if (live.raf) cancelAnimationFrame(live.raf); if (live.node.parentNode) live.node.parentNode.removeChild(live.node); live = null; }
  async function simulateReveal(text, signal) {
    var n = text.length, step = Math.max(24, Math.ceil(n / 50)), i = 0;
    while (i < n && !(signal && signal.aborted)) { i = Math.min(n, i + step); liveDelta(text.slice(0, i)); await sleep(30); }
  }
  async function askOnline(q, s) {
    var p = store.state.prefs;
    var ctx = p.local ? eng.contextFor(q, Object.assign(convState(s), { spoilerOff: !p.spoiler })) : []; lastCtx = ctx;
    var hist = p.memory ? s.messages.slice(-9, -1).filter(function (m) { return (m.role === 'user' || m.role === 'assistant') && !m.personal; }).slice(-6).map(function (m) { return { role: m.role, text: m.text.slice(0, 1200) }; }) : [];
    var payload = { question: q, history: hist, context: ctx, spoiler: p.spoiler ? 'avoid' : 'off', length: p.length || 'normal', cite: p.cite !== false };
    waitCtl = new AbortController();
    var attempts = 0, r, tot0 = Date.now();
    for (;;) {
      attempts++;
      r = await gw.askStream(payload, { signal: waitCtl.signal, onDelta: liveDelta });
      // mai un nuovo tentativo se una parte della risposta e' gia' stata mostrata
      if (r.ok || r.code === 'aborted' || attempts >= 2 || live || r.partial || !gw.retriable(r)) break;
      // un solo nuovo tentativo, solo per errori temporanei, ogni tentativo passa dalle stesse quote del gateway
      if (waitNode) { var wt = waitNode.querySelector('.wt'); if (wt) wt.textContent = 'Il servizio è occupato: riprovo una volta…'; }
      await sleep(1500 + Math.floor(Math.random() * 600)); if (waitCtl.signal.aborted) { r = { ok: false, code: 'aborted', stage: 'chat', http: 0, detail: '', message: 'Attesa interrotta.' }; break; }
    }
    // gateway non ancora aggiornato (o browser senza stream): la risposta intera viene rivelata progressivamente, in modo interrompibile
    if (r.ok && r.streamed === false && r.answer) await simulateReveal(r.answer, waitCtl.signal);
    var partial = live ? live.text : (r.partial || ''); endLive();
    waitCtl = null;
    var d = { at: Date.now(), ok: !!r.ok, stream: r.ok ? (r.streamed === false ? 'simulato' : 'reale') : (partial ? 'parziale' : ''), ttfb: r.ttfb || 0, partialChars: partial.length, attempts: attempts, ms: Date.now() - tot0, code: r.ok ? 'ok' : r.code, stage: r.ok ? '' : r.stage, http: r.ok ? 200 : r.http, detail: r.ok ? '' : (r.detail || ''), length: p.length || 'normal' };
    if (!r.ok) { diag.last = d; return { ok: false, code: r.code, stage: r.stage, http: r.http, detail: r.detail, message: r.message, partial: partial }; }
    var rr = resolveRefs(r.answer, ctx);
    d.markers = rr.markers; d.dupRaw = dupCount(r.answer); d.dupShown = dupCount(rr.text); diag.last = d;
    return { ok: true, text: rr.text, refs: rr.refs, cited: rr.cited };
  }

  /* attesa e anomalie */
  function clearTransient() { if (waitNode) { waitNode.remove(); waitNode = null; } if (errNode) { errNode.remove(); errNode = null; } }
  function abortWait() { if (waitCtl) waitCtl.abort(); }
  // Attesa compatta dentro la conversazione: i messaggi precedenti restano visibili; Interrompi anche nella barra di input
  function showWait(online) {
    clearTransient();
    var w = el('div', 'mm-think'); w.setAttribute('role', 'status'); w.setAttribute('aria-live', 'polite');
    w.appendChild(avatar('think'));
    var tx = el('div', 'tx'); tx.appendChild(el('b', 'wt', 'Consulto gli archivi del Multiverso…')); tx.appendChild(el('small', '', online ? 'Attendo la risposta dell’AI online.' : 'Cerco nell’archivio locale.'));
    var bar = el('div', 'mm-bar-ind'); bar.setAttribute('role', 'progressbar'); bar.setAttribute('aria-label', 'Elaborazione in corso'); bar.appendChild(el('i')); tx.appendChild(bar); w.appendChild(tx);
    var st = btn('stopmini', 'Interrompi la risposta'); st.appendChild(ic('stop')); st.appendChild(el('span', '', 'Interrompi')); st.onclick = abortWait; w.appendChild(st);
    $('mmChat').appendChild(w); waitNode = w; scrollEnd();
  }
  var ERR = {
    busy: { mood: 'err', title: 'Anomalia temporanea', text: 'I sistemi della TVA sono momentaneamente sovraccarichi. La tua domanda è al sicuro e verrà mantenuta in attesa.' },
    slow: { mood: 'err', title: 'Risposta in ritardo', text: 'La risposta sta impiegando troppo tempo. La tua domanda è al sicuro: puoi riprovare o consultare l’archivio locale.' },
    limit: { mood: 'tired', title: 'Energia temporale esaurita', text: 'Il limite gratuito dell’AI online è stato raggiunto per ora. La tua domanda è al sicuro: l’archivio locale resta a disposizione.' },
    rate: { mood: 'tired', title: 'Troppe richieste ravvicinate', text: 'Attendi qualche istante e riprova. La tua domanda è al sicuro.' },
    config: { mood: 'puzzled', title: 'Qualcosa non quadra', text: 'Il servizio AI non è disponibile o ha rifiutato la richiesta. Puoi consultare l’archivio locale; i dettagli sono nella Diagnostica.' },
    pending: { mood: 'puzzled', title: 'Domanda in attesa', text: 'Questa domanda non ha ancora una risposta. Puoi riprovare o consultare l’archivio locale.' }
  };
  function errKind(e) {
    var c = e.code;
    if (c === 'pending') return 'pending';
    if (c === 'quota' || c === 'provider-quota') return 'limit';
    if (c === 'rate' || c === 'blocked') return 'rate';
    if (c === 'timeout' || c === 'provider-timeout') return 'slow';
    if (c === 'network' || c === 'provider-network' || (c === 'provider' && e.http >= 500) || c === 'empty') return 'busy';
    return 'config';
  }
  function showError(e, q) {
    clearTransient();
    var k = ERR[errKind(e)], w = el('div', 'mm-state err'); w.setAttribute('role', 'alert');
    var m = el('div', 'mm-mascot-big'); m.appendChild(bigMascot(k.mood)); w.appendChild(m);
    w.appendChild(el('h3', '', k.title)); w.appendChild(el('p', '', k.text));
    var ok = onlineOK(), retry = btn('mm-bigbtn' + (errKind(e) === 'limit' || errKind(e) === 'config' ? ' sub' : ' primary'), null); retry.appendChild(ic('refresh')); retry.appendChild(el('span', '', 'Riprova'));
    retry.onclick = function () { var s = store.current(); if (s) answer(q, s, { forceOnline: ok }); };
    var loc = btn('mm-bigbtn sub', null); loc.appendChild(ic('book')); var t = el('span', '', 'Consulta l’archivio locale'); var sm = el('small', '', 'modalità offline'); t.appendChild(sm); loc.appendChild(t);
    loc.onclick = function () { var s = store.current(); if (s) answer(q, s, { forceLocal: true }); };
    w.appendChild(retry); w.appendChild(loc);
    if (e.code !== 'pending') { var dg = btn('mm-link', null); dg.textContent = 'Dettagli tecnici nella Diagnostica'; dg.onclick = function () { setView('set'); diagnostics(); }; w.appendChild(dg); }
    $('mmChat').appendChild(w); errNode = w; scrollEnd();
  }
  function setBusy(b) { busy = b; $('mmSend').disabled = b; $('mmSend').hidden = b; $('mmStop').hidden = !b; $('mmRoot').classList.toggle('busy', b); }

  function makeTitle(q) { var t = String(q).replace(/\s+/g, ' ').trim().replace(/[?!.]+$/, ''); t = t.charAt(0).toUpperCase() + t.slice(1); if (t.length > 48) { t = t.slice(0, 48); t = t.replace(/\s+\S*$/, '') + '…'; } return t || 'Nuova conversazione'; }

  // Nuova domanda dall'utente: il messaggio viene salvato UNA volta; tentativi e "Riprova" non lo duplicano.
  async function submit(q, opts) {
    q = String(q || '').trim(); if (!q || busy) return; opts = opts || {};
    var s = store.current() || store.fresh(q);
    if (!s.messages.length) s.title = makeTitle(q);
    store.push(s, { role: 'user', text: q, personal: eng.isPersonal(q) }); store.save();
    $('mmQ').value = ''; ui.draft = ''; stopSpeaking();
    if (view !== 'chat') setView('chat'); else { dropRegenButtons(); appendLive({ role: 'user', text: q }); }
    return answer(q, s, opts);
  }
  async function answer(q, s, opts) {
    if (busy) return; opts = opts || {};
    setBusy(true); banner(''); clearTransient(); dropRegenButtons(); extra = null;
    var msg, ans;
    try { ans = eng.ask(q, Object.assign(convState(s), { reveal: !!opts.reveal })); } catch (e) { ans = { text: 'Qualcosa si è inceppato negli archivi. Riprova.', refs: [], tag: 'locale', confidence: 0, entities: [] }; }
    var p = store.state.prefs, personal = eng.isPersonal(q);
    var wantOnline = !opts.forceLocal && onlineOK() && !personal && (opts.forceOnline || needsDepth(q, ans, s) || !p.local);
    msg = { role: 'assistant', text: ans.text, refs: ans.refs || [], tag: ans.personal ? 'dati locali' : 'archivio locale', flair: ans.flair };
    var cited = [];
    if (wantOnline) {
      mood('think'); showWait(true);
      var o = await askOnline(q, s);
      clearTransient();
      if (o.ok) { cited = o.cited; msg = { role: 'assistant', text: o.text, refs: o.refs, tag: 'online · AI · non verificato' + (p.spoiler ? ' · spoiler non garantiti' : '') }; }
      else if (o.partial && o.partial.trim().length >= 1 && (o.code === 'aborted' || o.code === 'timeout' || /network|timeout|provider/.test(o.code || ''))) {
        // il testo gia' ricevuto non va perso: resta in cronologia, con Riprova
        var pr = resolveRefs(o.partial, lastCtx); cited = pr.cited;
        msg = { role: 'assistant', text: pr.text, refs: pr.refs, tag: 'online · AI · ' + (o.code === 'aborted' ? 'interrotta dall’utente' : 'risposta parziale (connessione interrotta)'), action: { label: 'Riprova con l’AI online', run: function () { retryOnline(q); } } };
        banner(o.code === 'aborted' ? 'Risposta interrotta: il testo ricevuto è stato conservato.' : 'Connessione interrotta: conservo la parte di risposta già ricevuta.');
      }
      else if (o.code === 'aborted') { msg.tag = 'archivio locale (attesa interrotta)'; msg.action = { label: 'Riprova con l’AI online', run: function () { retryOnline(q); } }; banner('Attesa interrotta: ecco l’archivio locale.'); }
      else { setBusy(false); mood('idle'); render(); showError(o, q); return; }
    } else if (ans.needsOnline && !onlineOK()) {
      msg.text += '\n(L’AI online è disattiva: puoi attivarla dalle impostazioni.)';
    }
    if (opts.forceLocal && ans.needsOnline) msg.tag = 'archivio locale (modalità offline)';
    if (ans.withheld && ans.withheld.length) {
      msg.action = { label: 'Mostra comunque', run: function () { retryLocalReveal(q); } };
    } else if (!wantOnline && onlineOK() && !ans.personal && ans.intent !== 'saluto' && !msg.action) {
      msg.action = { label: 'Chiedi all’AI online', run: function () { retryOnline(q); } };
    }
    // memoria dei soggetti: entita' trovate dal motore locale + schede citate dall'AI (per i seguiti, anche offline)
    if (p.memory) { var ids = (ans.entities || []).slice(0, 2).concat(cited); var prev = s.last || []; s.last = ids.concat(prev).filter(function (x, i, a) { return x && a.indexOf(x) === i; }).slice(0, 4); }
    msg.personal = !!ans.personal; store.push(s, msg); extra = { sid: s.id, i: s.messages.length - 1, action: msg.action, flair: msg.flair }; if (!store.save()) banner('Memoria locale piena o non disponibile: la cronologia potrebbe non essere salvata.');
    setBusy(false); render('answer');
    if (p.voice) speak(msg.text, null);
    mood('talk'); setTimeout(function () { mood('idle'); }, Math.min(4000, 600 + msg.text.length * 12));
  }
  // Azioni che rielaborano la stessa domanda senza duplicarla nella cronologia
  function dropLastAssistant(s) { if (s.messages.length && s.messages[s.messages.length - 1].role === 'assistant') store.pop(s); }
  function retryOnline(q) { var s = store.current(); if (!s || busy) return; dropLastAssistant(s); answer(q, s, { forceOnline: true }); }
  function retryLocalReveal(q) { var s = store.current(); if (!s || busy) return; dropLastAssistant(s); answer(q, s, { reveal: true }); }
  function regenerate() {
    var s = store.current(); if (!s || busy || s.messages.length < 2) return;
    var last = s.messages[s.messages.length - 1], prev = s.messages[s.messages.length - 2]; if (last.role !== 'assistant' || prev.role !== 'user') return;
    store.pop(s); answer(prev.text, s, { forceOnline: onlineOK() && !prev.personal });
  }

  /* ---------- cronologia ---------- */
  function dayStart(t) { var d = new Date(t); d.setHours(0, 0, 0, 0); return d.getTime(); }
  function groupLabel(at) { var t0 = dayStart(Date.now()), d = dayStart(at); if (d >= t0) return 'Oggi'; if (d >= t0 - 86400000) return 'Ieri'; if (d >= t0 - 7 * 86400000) return 'Settimana scorsa'; return 'Più vecchie'; }
  function renderHistory() {
    var box = $('mmHistList'); while (box.firstChild) box.removeChild(box.firstChild);
    var qs = String($('mmSearch').value || '').toLowerCase().trim();
    var ss = store.state.sessions.filter(function (s) { return s.messages.length || s.id === store.state.active; }).slice().sort(function (a, b) { return b.at - a.at; });
    if (qs) ss = ss.filter(function (s) { return s.title.toLowerCase().indexOf(qs) >= 0 || s.messages.some(function (m) { return m.text.toLowerCase().indexOf(qs) >= 0; }); });
    if (!ss.length) { box.appendChild(el('p', 'mm-empty', qs ? 'Nessuna conversazione trovata.' : 'Nessuna conversazione salvata.')); }
    var nb = btn('mm-bigbtn primary', null); nb.style.margin = '12px auto'; nb.appendChild(ic('plus')); nb.appendChild(el('span', '', 'Nuova conversazione')); nb.onclick = newChat; box.appendChild(nb);
    var cur = null, list = null;
    ss.forEach(function (s) {
      var gl = groupLabel(s.at); if (gl !== cur) { cur = gl; box.appendChild(el('div', 'mm-group', gl)); list = el('div', 'mm-list'); box.appendChild(list); }
      var r = el('div', 'mm-row' + (s.id === store.state.active ? ' current' : ''));
      var o = btn('open', null); o.appendChild(ic('chat')); o.appendChild(el('span', '', s.title)); o.appendChild(ic('right')); o.onclick = function () { store.open(s.id); store.save(); setView('chat'); };
      var ed = iconBtn('edit', 'Rinomina conversazione', 'mini'); ed.onclick = function () { rename(r, s); };
      var x = iconBtn('trash', 'Elimina conversazione', 'mini danger'); x.onclick = function () {
        if (x.getAttribute('data-arm') === 'true') { store.remove(s.id); store.save(); renderHistory(); toast('Conversazione eliminata'); return; }
        x.setAttribute('data-arm', 'true'); x.setAttribute('aria-label', 'Conferma eliminazione'); toast('Tocca di nuovo per eliminare'); setTimeout(function () { x.removeAttribute('data-arm'); x.setAttribute('aria-label', 'Elimina conversazione'); }, 3000);
      };
      r.appendChild(o); r.appendChild(ed); r.appendChild(x); list.appendChild(r);
    });
    box.appendChild(el('p', 'mm-note', 'L’archivio completo delle conversazioni resta su questo dispositivo. Con AI online e memoria contestuale attive, i messaggi più recenti (fino a 6, esclusi quelli sui tuoi dati personali) e le schede pertinenti possono essere inviati a Gemini per rispondere.'));
  }
  function rename(row, s) {
    while (row.firstChild) row.removeChild(row.firstChild);
    var i = el('input', 'ren'); i.type = 'text'; i.maxLength = 60; i.value = s.title; i.setAttribute('aria-label', 'Nuovo titolo'); row.appendChild(i);
    var ok = iconBtn('check', 'Salva il titolo', 'mini'); var no = iconBtn('close', 'Annulla', 'mini');
    function save() { if (store.rename(s.id, i.value)) store.save(); renderHistory(); }
    ok.onclick = save; no.onclick = renderHistory; i.onkeydown = function (e) { if (e.key === 'Enter') { e.preventDefault(); save(); } else if (e.key === 'Escape') renderHistory(); };
    row.appendChild(ok); row.appendChild(no); i.focus(); i.select();
  }
  function newChat() { stopSpeaking(); store.state.active = null; store.save(); setView('home'); $('mmQ').focus(); }

  /* ---------- impostazioni ---------- */
  function dlg(title, build) { var b = $('mmDlgBody'); while (b.firstChild) b.removeChild(b.firstChild); b.appendChild(el('h2', '', title)); build(b); var d = $('mmDlg'); if (!d.open) { if (d.showModal) d.showModal(); else d.setAttribute('open', ''); } }
  function toggleRow(parent, o) {
    var r = el('label', 'mm-srow'); r.appendChild(ic(o.icon)); var t = el('div', 't'); t.appendChild(el('b', '', o.title)); if (o.sub) t.appendChild(el('small', '', o.sub)); r.appendChild(t);
    var sw = el('span', 'sw'); var i = el('input'); i.type = 'checkbox'; i.id = 'set-' + o.key; i.checked = !!store.state.prefs[o.key]; i.setAttribute('role', 'switch'); i.setAttribute('aria-label', o.title);
    i.onchange = function () { o.onChange(i.checked, i); }; sw.appendChild(i); sw.appendChild(el('i')); r.appendChild(sw); parent.appendChild(r); return r;
  }
  function linkRow(parent, icon, title, sub, run) { var b = btn('mm-srow', null); b.appendChild(ic(icon)); var t = el('div', 't'); t.appendChild(el('b', '', title)); if (sub) t.appendChild(el('small', '', sub)); b.appendChild(t); var c = ic('right'); c.setAttribute('class', 'ic chev'); b.appendChild(c); b.onclick = run; parent.appendChild(b); return b; }
  function renderSettings() {
    var b = $('mmSetBody'); while (b.firstChild) b.removeChild(b.firstChild); var p = store.state.prefs;
    var pr = el('div', 'mm-prof'); pr.appendChild(avatar()); var pt = el('div'); pt.appendChild(el('b', '', 'Miss Minutes')); pt.appendChild(el('small', '', 'Holographic Intelligence · ' + VERSION + ' (TEST)')); pr.appendChild(pt); pr.appendChild(el('span', 'logo', 'TVA')); b.appendChild(pr);
    var g1 = el('div', 'mm-set');
    toggleRow(g1, { key: 'online', icon: 'spark', title: 'AI online', sub: gw.available() ? 'Gemini (gratuito) · serve il consenso' : 'Gateway non configurato: solo motore locale', onChange: function (v, inp) {
      if (!v) { store.state.prefs.online = false; store.save(); updateSub(); return; }
      if (!gw.available()) { inp.checked = false; banner('Il gateway non è ancora configurato (vedi Diagnostica).'); return; }
      if (!store.state.prefs.consent) { inp.checked = false; consent(); return; }
      store.state.prefs.online = true; store.save(); updateSub();
    } });
    toggleRow(g1, { key: 'local', icon: 'archive', title: 'Archivio locale', sub: 'Risposte rapide offline e schede come contesto per l’AI. Spento: l’AI non riceve schede.', onChange: function (v) { p.local = v; store.save(); } });
    toggleRow(g1, { key: 'memory', icon: 'brain', title: 'Memoria contestuale', sub: 'Ricorda i messaggi recenti per i seguiti («e lui?», «confrontali»).', onChange: function (v) { p.memory = v; store.save(); } });
    b.appendChild(g1);
    var g2 = el('div', 'mm-set');
    toggleRow(g2, { key: 'voice', icon: 'volume', title: 'Lettura vocale', sub: 'Legge ad alta voce ogni risposta; i pulsanti di ascolto funzionano comunque.', onChange: function (v) { p.voice = v; store.save(); if (!v) stopSpeaking(); } });
    var lr = el('div', 'mm-srow'); lr.appendChild(ic('lines')); var lt = el('div', 't'); lt.appendChild(el('b', '', 'Lunghezza delle risposte')); lt.appendChild(el('small', '', 'Vale per le risposte dell’AI online.')); lr.appendChild(lt);
    var sg = el('div', 'seg'); sg.setAttribute('role', 'group'); sg.setAttribute('aria-label', 'Lunghezza delle risposte');
    [['short', 'Brevi'], ['normal', 'Medie'], ['long', 'Lunghe']].forEach(function (o) { var x = btn('', null); x.textContent = o[1]; x.setAttribute('aria-pressed', String((p.length || 'normal') === o[0])); x.onclick = function () { p.length = o[0]; store.save(); [].forEach.call(sg.children, function (y) { y.setAttribute('aria-pressed', 'false'); }); x.setAttribute('aria-pressed', 'true'); }; sg.appendChild(x); });
    lr.appendChild(sg); g2.appendChild(lr);
    toggleRow(g2, { key: 'cite', icon: 'book', title: 'Riferimenti bibliografici', sub: 'Chiede all’AI di indicare opere e cicli di riferimento solo quando attendibili.', onChange: function (v) { p.cite = v; store.save(); } });
    toggleRow(g2, { key: 'spoiler', icon: 'eye', title: 'Protezione spoiler', sub: 'Aiuto, non garanzia (v. sotto).', onChange: function (v) { p.spoiler = v; eng.setSpoilerProtection(v); store.save(); } });
    b.appendChild(g2);
    b.appendChild(el('p', 'mm-note', 'La protezione spoiler nasconde le schede segnalate come spoiler finché non le sblocchi. Non conosco cosa hai visto davvero e le risposte dell’AI online possono rivelare dettagli: non è una garanzia.'));
    var g3 = el('div', 'mm-set');
    linkRow(g3, 'shield', 'Privacy e consenso', p.consent ? 'Consenso AI online dato' : 'Nessun consenso dato', privacy);
    linkRow(g3, 'wrench', 'Diagnostica', 'Gateway, prova AI, ultima richiesta', diagnostics);
    linkRow(g3, 'info', 'Informazioni e crediti', VERSION + ' · Holographic Intelligence', about);
    b.appendChild(g3);
  }
  function updateSub() { var on = onlineOK(); $('mmRoot').setAttribute('data-ai', on ? 'on' : 'off'); var t = 'Assistente del Multiverso'; $('mmSub').textContent = t; $('mmSubChat').textContent = t; var lab = on ? 'AI online attiva' : 'Modalità locale'; $('mmSub').title = lab; $('mmSubChat').title = lab; if (view === 'home') renderHome(); }
  function subtitle() { return 'Assistente del Multiverso'; }
  function consent() {
    dlg('Attivare l’AI online?', function (b) {
      b.appendChild(el('p', '', 'Per rispondere a domande aperte, Miss Minutes invia a un servizio AI di Google (Gemini, piano gratuito) la tua domanda, fino a 5 schede pubbliche dell’archivio e gli ultimi messaggi della chat.'));
      b.appendChild(el('p', '', 'Non vengono inviati titoli visti, voti, note, amici o altri dati personali. Nel piano gratuito Google può usare i contenuti inviati per migliorare i propri prodotti: non scrivere informazioni private.'));
      b.appendChild(el('p', '', 'Se il servizio non è disponibile o il limite gratuito è finito, puoi riprovare o consultare l’archivio locale.'));
      var a = btn('', null); a.textContent = 'Acconsento e attivo'; a.onclick = function () { store.state.prefs.consent = true; store.state.prefs.online = true; store.save(); $('mmDlg').close(); banner('AI online attivata.'); updateSub(); if (view === 'set') renderSettings(); };
      var n = btn('', null); n.textContent = 'No, solo locale'; n.onclick = function () { $('mmDlg').close(); };
      var w = el('div', 'mm-dlg-actions'); w.appendChild(n); w.appendChild(a); b.appendChild(w);
    });
  }
  function privacy() {
    dlg('Privacy e consenso', function (b) {
      b.appendChild(el('p', '', 'Con l’AI online attiva, a Google (Gemini, piano gratuito) vengono inviati: la tua domanda, fino a 5 schede pubbliche dell’archivio e gli ultimi messaggi della chat non personali.'));
      b.appendChild(el('p', '', 'Non vengono mai inviati titoli visti, voti, note, amici, progressi o altri dati personali. Le domande sui tuoi dati restano sempre sul dispositivo.'));
      b.appendChild(el('p', 'mm-small', 'Nel piano gratuito Google può usare i contenuti inviati per migliorare i propri prodotti: non scrivere informazioni private. L’archivio completo delle conversazioni resta in questo browser; a Gemini arrivano solo i messaggi recenti quando AI online e memoria contestuale sono attive.'));
      var w = el('div', 'mm-dlg-actions');
      if (store.state.prefs.consent) { var rv = btn('', null); rv.textContent = 'Revoca il consenso'; rv.onclick = function () { store.state.prefs.consent = false; store.state.prefs.online = false; store.save(); $('mmDlg').close(); banner('Consenso revocato: AI online disattivata.'); updateSub(); renderSettings(); }; w.appendChild(rv); }
      var cl = btn('', null); cl.textContent = 'Cancella cronologia'; cl.onclick = function () { if (cl.getAttribute('data-arm') === 'true') { store.clear(); store.save(); wipeUi(); $('mmDlg').close(); toast('Cronologia cancellata'); return; } cl.setAttribute('data-arm', 'true'); cl.textContent = 'Tocca di nuovo per confermare'; };
      w.appendChild(cl); b.appendChild(w);
    });
  }
  function about() {
    dlg('Informazioni e crediti', function (b) {
      var st = eng.stats();
      b.appendChild(el('p', '', 'Miss Minutes · Holographic Intelligence · ' + VERSION + ' (TEST). Assistente del Multiverso Marvel dentro TVA Archives.'));
      b.appendChild(el('p', 'mm-small', 'Archivio locale: ' + st.entries + ' voci (' + st.curated + ' schede curate, riferimenti da verificare su fonti primarie). Dati dell’app: ' + (host ? 'collegati in sola lettura' : 'non collegati') + '.'));
      b.appendChild(el('p', 'mm-small', 'Risposte generate con Google Gemini tramite un gateway gratuito: possono contenere errori, verifica le informazioni importanti. Progetto fan non ufficiale, non affiliato né approvato da Marvel o Disney.'));
      b.appendChild(el('p', 'mm-small', 'Interfaccia e mascotte olografica: disegni originali per TVA Archives.'));
    });
  }
  function diagText() {
    var d = diag.last, L = ['Miss Minutes ' + VERSION, 'Gateway: ' + (gw.available() ? 'configurato' : 'non configurato'), 'AI online: ' + (onlineOK() ? 'attiva' : 'spenta')];
    if (!d) L.push('Ultima richiesta AI: nessuna in questa sessione.');
    else {
      L.push('Ultima richiesta AI: ' + (d.ok ? 'riuscita' : 'FALLITA'), 'Tentativi: ' + d.attempts + ' · durata: ' + d.ms + ' ms', 'Lunghezza richiesta: ' + d.length);
      if (d.stream) L.push('Streaming: ' + d.stream + (d.ttfb ? ' · primo testo dopo ' + d.ttfb + ' ms' : '') + (d.partialChars ? ' · testo parziale: ' + d.partialChars + ' caratteri' : ''));
      if (!d.ok) L.push('Codice: ' + d.code + ' · stadio: ' + (d.stage || '-') + ' · HTTP: ' + (d.http || '-') + (d.detail ? ' · ' + d.detail : ''));
      else L.push('Marcatori scheda nella risposta grezza: ' + d.markers, 'Parole ripetute adiacenti — risposta grezza: ' + d.dupRaw + ' · testo mostrato: ' + d.dupShown);
    }
    L.push('Avvii della pagina: ' + ui.boots + ' · ripristino schermata: ' + (ui.restored ? 'sì' : 'no'));
    var ev = ui.life.slice(-6).map(function (x) { var d = new Date(x.t); return x.e + '@' + ('0' + d.getHours()).slice(-2) + ':' + ('0' + d.getMinutes()).slice(-2) + ':' + ('0' + d.getSeconds()).slice(-2); });
    L.push('Ultimi eventi: ' + (ev.join(', ') || '-'));
    return L.join('\n');
  }
  function diagnostics() {
    dlg('Diagnostica', function (b) {
      if (!CFG.endpoint) {
        var r = el('div', 'row'); var inp = el('input'); inp.type = 'url'; inp.id = 'set-endpoint'; inp.placeholder = 'https://miss-minutes-api.….workers.dev'; inp.value = store.state.prefs.endpoint || ''; inp.setAttribute('aria-label', 'Indirizzo del gateway'); inp.autocapitalize = 'off'; inp.spellcheck = false;
        var sv = btn('', null); sv.textContent = 'Salva'; var msg = el('p', 'mm-small', 'Indirizzo del gateway AI (non è un segreto). Vuoto = solo motore locale.');
        sv.onclick = async function () {
          var v = inp.value.trim().replace(/\/+$/, '');
          if (v && !EP_RE.test(v)) { msg.textContent = 'Indirizzo non valido: deve essere https://…workers.dev'; return; }
          store.state.prefs.endpoint = v; if (!v) { store.state.prefs.online = false; } store.save(); gw = makeGw();
          if (!v) { msg.textContent = 'Gateway rimosso: solo motore locale.'; updateSub(); return; }
          msg.textContent = 'Verifico…'; var h = await gw.health();
          msg.textContent = !h.ok ? 'Gateway non raggiungibile o origine non autorizzata.' : h.enabled ? 'Gateway raggiungibile, AI attiva.' : 'Gateway raggiungibile, AI ancora spenta (attivazione da fare lato Cloudflare).';
          updateSub();
        };
        r.appendChild(inp); r.appendChild(sv); b.appendChild(r); b.appendChild(msg);
      }
      if (gw.available()) {
        var dg = btn('', null); dg.textContent = 'Prova AI online (usa 1 richiesta)'; var dm = el('p', 'mm-small', 'Controlla gateway, sessione e risposta reale di Gemini.');
        dg.onclick = async function () {
          dg.disabled = true; dm.textContent = '1/2 gateway…'; var h = await gw.health();
          if (!h.ok) { dm.textContent = 'Gateway: non raggiungibile o origine non autorizzata (CORS).'; dg.disabled = false; return; }
          if (!h.enabled) { dm.textContent = 'Gateway raggiungibile ma AI spenta lato Cloudflare' + (h.missing && h.missing.length ? ' (manca: ' + h.missing.join(', ') + ')' : '') + '.'; dg.disabled = false; return; }
          dm.textContent = '2/2 sessione e Gemini…'; var r = await gw.ask({ question: 'Rispondi solo con la parola OK.', history: [], context: [], spoiler: 'avoid' });
          dm.textContent = r.ok ? 'Tutto funziona. Gemini ha risposto: «' + r.answer.slice(0, 60) + '»' : 'Fallito allo stadio «' + r.stage + '»: ' + r.message + (r.detail ? ' [' + r.detail + ']' : ''); dg.disabled = false;
        };
        b.appendChild(dg); b.appendChild(dm);
      }
      var kv = el('div', 'mm-kv', diagText()); kv.id = 'mmDiag'; b.appendChild(kv);
      var cp = btn('', null); cp.textContent = 'Copia diagnostica'; cp.onclick = function () { copyText(diagText()); }; b.appendChild(cp);
      b.appendChild(el('p', 'mm-small', 'La diagnostica non contiene domande, risposte, chiavi o dati personali.'));
    });
  }

  /* ---------- dettatura ---------- */
  function setupVoice() {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition; if (!SR) return;
    var mic = $('mmMic'); mic.hidden = false; var rec = null;
    mic.onclick = function () {
      if (rec) { try { rec.stop(); } catch (e) {} return; }
      try {
        rec = new SR(); rec.lang = 'it-IT'; rec.interimResults = false; rec.maxAlternatives = 1;
        rec.onresult = function (ev) { var t = ev.results[0] && ev.results[0][0] && ev.results[0][0].transcript; if (t) { $('mmQ').value = t.slice(0, 600); } };
        rec.onerror = function () { banner('Dettatura non disponibile (permesso negato o rete assente).'); };
        rec.onend = function () { rec = null; mic.setAttribute('aria-pressed', 'false'); };
        mic.setAttribute('aria-pressed', 'true'); rec.start();
      } catch (e) { rec = null; banner('Dettatura non supportata su questo dispositivo.'); }
    };
  }

  /* ---------- avvio ---------- */
  async function init() {
    hydrate(D); installHeadSymbol(); drawBackground(); setupVoice();
    $('mmAvChat').appendChild(avatar().firstChild);
    store = window.MMStore.create(window.localStorage);
    gw = makeGw();
    uiLoad(); ui.boots = (ui.boots || 0) + 1; var navT = ''; try { var ne = performance.getEntriesByType('navigation')[0]; navT = ne ? ne.type : ''; } catch (e) {}
    var hadState = !!ui.t; life('avvio:' + (navT || '?') + (hadState ? ':con-stato' : ':nuovo'));
    // ciclo di vita: il salvataggio avviene a ogni uscita dal primo piano (iOS puo' scartare la pagina senza altri avvisi)
    D.addEventListener('visibilitychange', function () { flushUi('visibilita:' + D.visibilityState); });
    window.addEventListener('pagehide', function (e) { flushUi('pagehide' + (e.persisted ? ':bfcache' : '')); });
    window.addEventListener('pageshow', function (e) { life('pageshow' + (e.persisted ? ':bfcache' : '')); });
    window.addEventListener('blur', function () { flushUi('blur'); }); window.addEventListener('focus', function () { life('focus'); });
    D.addEventListener('freeze', function () { flushUi('freeze'); }); D.addEventListener('resume', function () { life('resume'); });
    var tmr = null; function later(f) { clearTimeout(tmr); tmr = setTimeout(f, 250); }
    ['vHome', 'mmChat', 'vHist', 'vSet'].forEach(function (id) { $(id).addEventListener('scroll', function () { updateDown(); later(function () { flushUi(); }); }, { passive: true }); });
    $('mmDown').onclick = function () { var c = $('mmChat'); try { c.scrollTo({ top: c.scrollHeight, behavior: 'smooth' }); } catch (e) { c.scrollTop = c.scrollHeight; } };
    $('mmQ').addEventListener('input', function () { later(function () { flushUi(); }); });
    // tastiera iOS: la barra inferiore cede spazio mentre si scrive
    maxH = window.innerHeight;
    function kbCheck() { var f = D.activeElement, typing = f && (f.id === 'mmQ' || f.id === 'mmSearch' || (f.tagName === 'INPUT' && f.type !== 'checkbox')); maxH = Math.max(maxH, window.innerHeight); var small = window.innerHeight < maxH - 120; $('mmRoot').classList.toggle('kb', !!(typing && small)); if (typing && small && view === 'chat') scrollEnd(); }
    window.addEventListener('resize', kbCheck); D.addEventListener('focusin', function () { setTimeout(kbCheck, 250); }); D.addEventListener('focusout', function () { setTimeout(kbCheck, 120); });
    window.addEventListener('orientationchange', function () { setTimeout(function () { maxH = window.innerHeight; kbCheck(); }, 400); });
    try { var ar = await fetch('mascot/manifest.json', { cache: 'no-store' }); if (ar.ok) { var aj = await ar.json(); if (aj && typeof aj === 'object' && aj.idle) ART = aj; } } catch (e) { ART = null; }
    buildHome();
    var kc = []; try { var r = await fetch('knowledge/core.json'); kc = (await r.json()).records || []; } catch (e) { banner('Archivio locale non caricato: riapri Miss Minutes.'); }
    var data = {};
    if (host) {
      try {
        data.titles = host.titles();
        ['graph:relationshipGraphData', 'powers:tesseraCharPowersData', 'levels:tesseraCharLevelsData', 'levelNames:tesseraLevelNamesData', 'charIds:tesseraCharIdsData', 'mv:mvMapData'].forEach(function (p2) { var kv = p2.split(':'); try { var t = host.blob(kv[1]); if (t) data[kv[0]] = JSON.parse(t); } catch (e) {} });
      } catch (e) { data = {}; }
    }
    eng = window.MMEngine.create({ data: data, knowledge: kc }); eng.setSpoilerProtection(store.state.prefs.spoiler);
    updateSub();
    $('mmForm').onsubmit = function (e) { e.preventDefault(); submit($('mmQ').value); };
    $('mmPlus').onclick = newChat;
    $('mmHist').onclick = function () { setView('hist'); }; $('mmSet').onclick = function () { setView('set'); };
    $('navChat').onclick = function () { setView(hasChat() ? 'chat' : 'home'); }; $('navHist').onclick = function () { setView('hist'); };
    $('navAtl').onclick = function () { openLink('tab:atlante'); };
    ['mmBack', 'mmBackHist', 'mmBackSet'].forEach(function (id) { $(id).onclick = goBack; });
    ['mmClose', 'mmCloseChat', 'mmCloseHist', 'mmSetClose'].forEach(function (id) { $(id).onclick = function () { stopSpeaking(); flushUi('chiusura'); closeApp(); }; });
    $('mmStop').onclick = abortWait;
    $('mmMenu').onclick = function () { if (!$('mmMenuBox').hidden) return closeMenu(); openMenu($('mmMenu'), [
      { icon: 'plus', label: 'Nuova conversazione', run: newChat }, { icon: 'history', label: 'Cronologia', run: function () { setView('hist'); } },
      { icon: 'gear', label: 'Impostazioni', run: function () { setView('set'); } }, { icon: 'close', label: 'Chiudi Miss Minutes', run: closeApp }]); };
    $('mmHistMenu').onclick = function () { if (!$('mmMenuBox').hidden) return closeMenu(); openMenu($('mmHistMenu'), [
      { icon: 'plus', label: 'Nuova conversazione', run: newChat },
      { icon: 'trash', label: 'Cancella tutta la cronologia', run: function () { dlg('Cancellare la cronologia?', function (b) { b.appendChild(el('p', '', 'Tutte le conversazioni salvate su questo dispositivo verranno eliminate. L’operazione non si può annullare.')); var y = btn('', null); y.textContent = 'Cancella tutto'; y.onclick = function () { store.clear(); store.save(); wipeUi(); $('mmDlg').close(); renderHistory(); toast('Cronologia cancellata'); }; var w = el('div', 'mm-dlg-actions'); w.appendChild(y); b.appendChild(w); }); } },
      { icon: 'close', label: 'Chiudi Miss Minutes', run: closeApp }]); };
    $('mmSearch').oninput = renderHistory;
    $('mmDlgClose').onclick = function () { $('mmDlg').close(); };
    D.addEventListener('click', function (e) { var box = $('mmMenuBox'); if (!box.hidden && !box.contains(e.target) && !(box._anchor && box._anchor.contains(e.target))) closeMenu(); });
    D.addEventListener('keydown', function (e) { if (e.key !== 'Escape') return; if (!$('mmMenuBox').hidden) { closeMenu(); return; } if (!$('mmDlg').open) { try { host && host.close(); } catch (x) {} } });
    if (!store.usable()) banner('Memoria locale non disponibile: la cronologia non sarà salvata.');
    // ripristino: schermata, bozza e scorrimento (mai una nuova chat senza richiesta esplicita)
    var start = ['home', 'chat', 'hist', 'set'].indexOf(ui.view) >= 0 ? ui.view : 'home'; if (start === 'chat' && !hasChat()) start = 'home';
    prevView = ['home', 'chat', 'hist', 'set'].indexOf(ui.prev) >= 0 ? ui.prev : 'home';
    if (ui.draft) $('mmQ').value = String(ui.draft).slice(0, 600);
    ui.restored = !!(hadState && (start !== 'home' || ui.draft));
    setView(start, { noPush: true }); if (ui.restored) restoreScroll(start);
    try { window.__mm = { ask: submit, engine: eng, store: store, view: function () { return view; }, diag: function () { return diag.last; }, resolveRefs: resolveRefs, go: function (v) { setView(v); }, ui: function () { return ui; }, back: goBack }; } catch (e) {}
  }
  init();
})();
