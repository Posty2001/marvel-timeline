/* Tessera TVA 3.0 — 12 sfondi animati ORIGINALI (SVG + CSS, nessuna immagine, nessuna risorsa esterna).
   Ogni scena è una stringa SVG (viewBox 320×200) costruita da forme semplici; le animazioni sono solo transform/opacity (classi in tessera2.css) e si fermano con
   «statico»/«off» o con prefers-reduced-motion. Nessun dato utente entra nel markup. */
(function (W) {
  'use strict';
  function rng(seed) { var s = seed >>> 0; return function () { s = (s + 0x6D2B79F5) >>> 0; var x = s; x = Math.imul(x ^ (x >>> 15), x | 1); x ^= x + Math.imul(x ^ (x >>> 7), x | 61); return ((x ^ (x >>> 14)) >>> 0) / 4294967296; }; }
  function n1(x) { return Math.round(x * 10) / 10; }
  function an(cls, dur, delay, origin) { return ' class="' + cls + '" style="animation-duration:' + dur + 's;animation-delay:' + n1(delay) + 's' + (origin ? ';transform-origin:' + origin : '') + '"'; }
  function svg(uid, defs, body) { return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false"><defs>' + defs + '</defs>' + body + '</svg>'; }
  function grad(id, a, b, c, dir) { return '<linearGradient id="' + id + '" ' + (dir || 'x1="0" y1="0" x2="0" y2="1"') + '><stop offset="0" stop-color="' + a + '"/>' + (c ? '<stop offset=".55" stop-color="' + b + '"/><stop offset="1" stop-color="' + c + '"/>' : '<stop offset="1" stop-color="' + b + '"/>') + '</linearGradient>'; }
  function rad(id, a, b, cx, cy, r) { return '<radialGradient id="' + id + '" cx="' + (cx || .5) + '" cy="' + (cy || .5) + '" r="' + (r || .6) + '"><stop offset="0" stop-color="' + a + '"/><stop offset="1" stop-color="' + b + '" stop-opacity="0"/></radialGradient>'; }
  function dots(R, n, y0, y1, cols, rmax, cls, durMin, durMax) {
    var o = ''; for (var i = 0; i < n; i++) { var x = n1(R() * 320), y = n1(y0 + R() * (y1 - y0)), r = n1(.5 + R() * rmax); o += '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="' + cols[i % cols.length] + '"' + an(cls, n1(durMin + R() * (durMax - durMin)), R() * 4) + '/>'; }
    return o;
  }

  var S = {
    'sacra-linea': function (u) {
      var R = rng(11), o = '';
      for (var i = 0; i < 5; i++) { var y = 40 + i * 28; o += '<path d="M-10 ' + y + ' C80 ' + (y - 14 + i * 6) + ' 200 ' + (y + 16 - i * 5) + ' 330 ' + (y - 6) + '" stroke="#E3C79B" stroke-opacity=".10" stroke-width="1" fill="none"/>'; }
      o += '<path d="M-10 100 C90 84 210 118 330 98" stroke="url(#' + u + 'g)" stroke-width="3.2" fill="none" stroke-linecap="round"/>';
      o += '<path d="M-10 100 C90 84 210 118 330 98" stroke="#fff6dc" stroke-opacity=".8" stroke-width="1" fill="none" stroke-dasharray="14 120"' + an('t2a-dash', 6, 0) + '/>';
      [[40, 94], [110, 90], [190, 108], [262, 102]].forEach(function (p, i) { o += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="4.5" fill="#F59A23"' + an('t2a-pulse', 3 + i * .6, i * .5, 'center') + '/><circle cx="' + p[0] + '" cy="' + p[1] + '" r="9" fill="none" stroke="#F59A23" stroke-opacity=".35"/>'; });
      o += dots(R, 14, 20, 180, ['#E3C79B', '#F59A23'], 1, 't2a-twinkle', 3, 6);
      return svg(u, grad(u + 'bg', '#1b1208', '#0d0a07') + '<linearGradient id="' + u + 'g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F59A23" stop-opacity="0"/><stop offset=".5" stop-color="#F6C86A"/><stop offset="1" stop-color="#F59A23" stop-opacity="0"/></linearGradient>', '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'terminale-tva': function (u) {
      var o = '', R = rng(7);
      for (var i = 0; i < 9; i++) { var w = 40 + R() * 150; o += '<rect x="18" y="' + (24 + i * 16) + '" width="' + n1(w) + '" height="4" rx="2" fill="#F59A23" fill-opacity="' + n1(.25 + R() * .5) + '"' + an('t2a-blink', 3 + R() * 3, R() * 3) + '/>'; }
      o += '<rect x="18" y="170" width="8" height="12" fill="#F6C86A"' + an('t2a-blink-hard', 1.1, 0) + '/>';
      o += '<g stroke="#2a6b6f" stroke-opacity=".35">' + [0, 1, 2, 3, 4, 5, 6, 7].map(function (i) { return '<path d="M' + (200 + i * 16) + ' 20V180"/>'; }).join('') + '</g>';
      o += '<rect x="0" y="-30" width="320" height="30" fill="url(#' + u + 'sc)"' + an('t2a-scan', 5.5, 0) + '/>';
      return svg(u, grad(u + 'bg', '#0b1618', '#070b0c') + '<linearGradient id="' + u + 'sc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6fe0d0" stop-opacity="0"/><stop offset="1" stop-color="#6fe0d0" stop-opacity=".35"/></linearGradient>', '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'multiverso': function (u) {
      var R = rng(23), o = '';
      [[160, 100, 34, 22], [160, 100, 62, 44], [160, 100, 96, 70], [160, 100, 140, 100]].forEach(function (c, i) {
        o += '<g' + an(i % 2 ? 't2a-spin-r' : 't2a-spin', 40 + i * 25, 0, '160px 100px') + '><ellipse cx="' + c[0] + '" cy="' + c[1] + '" rx="' + c[2] + '" ry="' + c[3] + '" fill="none" stroke="#b79cf0" stroke-opacity="' + n1(.5 - i * .08) + '" stroke-dasharray="' + (3 + i * 3) + ' ' + (6 + i * 4) + '"/><circle cx="' + (c[0] + c[2]) + '" cy="' + c[1] + '" r="' + (3 + i) + '" fill="' + ['#F59A23', '#6fd0e0', '#e88bd0', '#9aa39a'][i] + '"/></g>';
      });
      o += '<circle cx="160" cy="100" r="16" fill="url(#' + u + 'c)"' + an('t2a-pulse', 4, 0, 'center') + '/>' + dots(R, 22, 6, 194, ['#fff', '#b79cf0', '#6fd0e0'], 1, 't2a-twinkle', 3, 7);
      return svg(u, rad(u + 'bg', '#2b1a52', '#06040d', .5, .5, .8) + rad(u + 'c', '#fff1c8', '#F59A23'), '<rect width="320" height="200" fill="#07050f"/><rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'archivio-dorato': function (u) {
      var R = rng(5), o = '';
      for (var i = 0; i < 6; i++) { var x = 18 + i * 52; o += '<rect x="' + x + '" y="30" width="22" height="150" fill="#2a1d0c" stroke="#E3C79B" stroke-opacity=".25"/><rect x="' + (x - 3) + '" y="24" width="28" height="8" fill="#3a2810" stroke="#E3C79B" stroke-opacity=".3"/>'; for (var j = 0; j < 4; j++) o += '<rect x="' + (x + 4) + '" y="' + (44 + j * 32) + '" width="14" height="2" fill="#E3C79B" fill-opacity=".25"/>'; }
      o += '<ellipse cx="160" cy="110" rx="120" ry="70" fill="url(#' + u + 'l)"' + an('t2a-pulse', 6, 0, 'center') + '/>';
      o += dots(R, 26, 40, 190, ['#F6C86A', '#E3C79B'], 1.3, 't2a-rise', 7, 13);
      return svg(u, grad(u + 'bg', '#20150a', '#0b0805') + rad(u + 'l', '#f6c86a', '#f6c86a', .5, .5, .6).replace('stop-opacity="0"', 'stop-opacity=".0"'), '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'yggdrasil': function (u) {
      var R = rng(31), o = '';
      o += '<path d="M160 200 C158 160 150 140 146 118 C140 96 120 84 96 74 M160 200 C162 160 170 140 176 116 C184 94 206 82 232 70 M154 130 C150 104 156 80 160 52 M168 128 C174 104 168 76 164 48 M146 118 C128 120 108 112 84 118 M176 116 C198 120 214 112 240 118" stroke="#6b4a1e" stroke-width="5" stroke-linecap="round" fill="none"/>';
      o += '<path d="M160 200 C158 160 150 140 146 118 C140 96 120 84 96 74" stroke="#E3C79B" stroke-opacity=".35" stroke-width="1" fill="none"/>';
      for (var i = 0; i < 34; i++) { var x = n1(70 + R() * 180), y = n1(30 + R() * 110); o += '<circle cx="' + x + '" cy="' + y + '" r="' + n1(1 + R() * 2.2) + '" fill="' + (i % 3 ? '#8fcf7a' : '#F6C86A') + '" fill-opacity=".85"' + an('t2a-drift', 5 + R() * 6, R() * 5) + '/>'; }
      o += '<circle cx="160" cy="74" r="26" fill="url(#' + u + 'g)"' + an('t2a-pulse', 5, 0, 'center') + '/>';
      return svg(u, grad(u + 'bg', '#0f1d14', '#070d09') + rad(u + 'g', '#c9f0a8', '#4a8f3a'), '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'dimensione-specchio': function (u) {
      var o = '', R = rng(13);
      for (var i = 0; i < 8; i++) { var a = i * 45; o += '<g transform="rotate(' + a + ' 160 100)"><polygon points="160,100 ' + n1(190 + R() * 30) + ',' + n1(36 + R() * 20) + ' ' + n1(214 + R() * 20) + ',' + n1(70 + R() * 20) + '" fill="url(#' + u + 'f)" fill-opacity="' + n1(.25 + R() * .35) + '" stroke="#cfd8ff" stroke-opacity=".35"/></g>'; }
      o = '<g' + an('t2a-spin', 90, 0, '160px 100px') + '>' + o + '</g><g' + an('t2a-spin-r', 60, 0, '160px 100px') + '><polygon points="160,60 200,100 160,140 120,100" fill="none" stroke="#fff" stroke-opacity=".5"/></g>';
      o += '<rect x="-40" y="0" width="30" height="200" fill="#fff" fill-opacity=".10" transform="skewX(-18)"' + an('t2a-sweep', 7, 0) + '/>';
      return svg(u, grad(u + 'bg', '#141a33', '#07091a') + '<linearGradient id="' + u + 'f" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8fa8ff"/><stop offset="1" stop-color="#e8c7ff"/></linearGradient>', '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'dimensione-oscura': function (u) {
      var o = '', R = rng(41);
      for (var i = 0; i < 6; i++) o += '<path d="M160 100 m' + (-14 - i * 14) + ' 0 a' + (14 + i * 14) + ' ' + (10 + i * 10) + ' 0 1 1 ' + (28 + i * 28) + ' 0" fill="none" stroke="' + (i % 2 ? '#b0173f' : '#7a3fd0') + '" stroke-opacity="' + n1(.65 - i * .08) + '" stroke-width="' + n1(2.2 - i * .2) + '" transform="rotate(' + i * 52 + ' 160 100)"/>';
      o = '<g' + an('t2a-spin', 50, 0, '160px 100px') + '>' + o + '</g><circle cx="160" cy="100" r="22" fill="#05020a" stroke="#b0173f" stroke-opacity=".7"' + an('t2a-pulse', 5, 0, 'center') + '/>';
      o += dots(R, 20, 8, 192, ['#d6335f', '#9b6bff'], 1, 't2a-twinkle', 3, 6);
      return svg(u, rad(u + 'bg', '#2a0f3d', '#05020a', .5, .5, .85), '<rect width="320" height="200" fill="#05020a"/><rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'regno-quantico': function (u) {
      var R = rng(17), o = '';
      for (var i = 0; i < 8; i++) o += '<path d="M0 ' + (28 + i * 20) + ' Q80 ' + (8 + i * 20) + ' 160 ' + (28 + i * 20) + ' T320 ' + (28 + i * 20) + '" fill="none" stroke="#6fe8ff" stroke-opacity=".16"' + an('t2a-wave', 6 + i * .7, i * .3) + '/>';
      for (var j = 0; j < 42; j++) { var x = n1(R() * 320), y = n1(R() * 200); o += '<circle cx="' + x + '" cy="' + y + '" r="' + n1(.8 + R() * 1.8) + '" fill="' + (j % 4 ? '#bff6ff' : '#fff') + '"' + an('t2a-twinkle', 2 + R() * 4, R() * 4) + '/>'; }
      o += '<circle cx="160" cy="100" r="40" fill="none" stroke="#6fe8ff" stroke-opacity=".5" stroke-dasharray="2 6"' + an('t2a-spin', 30, 0, '160px 100px') + '/><circle cx="160" cy="100" r="6" fill="#fff"' + an('t2a-pulse', 2.6, 0, 'center') + '/>';
      return svg(u, grad(u + 'bg', '#06222c', '#030d12'), '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'bifrost': function (u) {
      var cols = ['#ff5a5f', '#ffa24a', '#ffe066', '#6fe0a0', '#58b9ff', '#9d7bff'], o = '', R = rng(3);
      cols.forEach(function (c, i) { o += '<path d="M-20 ' + (170 - i * 5) + ' Q160 ' + (-30 - i * 5) + ' 340 ' + (170 - i * 5) + '" fill="none" stroke="' + c + '" stroke-width="4.2" stroke-opacity=".72"' + an('t2a-shimmer', 3.5 + i * .4, i * .25) + '/>'; });
      o += dots(R, 34, 4, 120, ['#fff', '#cfe6ff'], 1, 't2a-twinkle', 2, 6);
      return svg(u, grad(u + 'bg', '#0a1030', '#050816'), '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'il-vuoto': function (u) {
      var R = rng(29), o = '<circle cx="160" cy="100" r="46" fill="#000" stroke="#E3C79B" stroke-opacity=".7" stroke-width="1.4"' + an('t2a-pulse', 8, 0, 'center') + '/><circle cx="160" cy="100" r="58" fill="none" stroke="#E3C79B" stroke-opacity=".18"/>';
      o += '<circle cx="160" cy="100" r="64" fill="url(#' + u + 'h)"/>' + dots(R, 24, 6, 194, ['#8d8472', '#5b5547'], 1, 't2a-drift', 8, 14);
      return svg(u, rad(u + 'h', '#E3C79B', '#E3C79B', .5, .5, .5).replace('stop-opacity="0"', 'stop-opacity="0"'), '<rect width="320" height="200" fill="#030303"/>' + o);
    },
    'spider-verse': function (u) {
      var o = '', R = rng(37);
      for (var i = 0; i < 16; i++) { var a = (i / 16) * Math.PI * 2; o += '<path d="M160 100 L' + n1(160 + Math.cos(a) * 240) + ' ' + n1(100 + Math.sin(a) * 240) + '" stroke="#fff" stroke-opacity=".16"/>'; }
      for (var r = 1; r < 6; r++) { var p = ''; for (var k = 0; k < 16; k++) { var b = (k / 16) * Math.PI * 2, rr = r * 26 + (k % 2 ? -3 : 0); p += (k ? 'L' : 'M') + n1(160 + Math.cos(b) * rr) + ' ' + n1(100 + Math.sin(b) * rr * .8); } o += '<path d="' + p + 'Z" fill="none" stroke="#fff" stroke-opacity=".18"/>'; }
      for (var j = 0; j < 40; j++) o += '<circle cx="' + n1(R() * 320) + '" cy="' + n1(R() * 200) + '" r="1.6" fill="#ff2f64" fill-opacity=".5"/>';
      o = '<g' + an('t2a-glitch', 4, 0) + '>' + o + '</g><path d="M60 200 L110 120 L90 120 L140 50" stroke="#2fb5ff" stroke-width="3" fill="none" stroke-opacity=".7"' + an('t2a-flick', 3.2, 0) + '/>';
      return svg(u, grad(u + 'bg', '#1a0b2a', '#070312', '#0a1840'), '<rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    },
    'infinito': function (u) {
      var o = '', cols = ['#a66bff', '#4aa8ff', '#ff4a5a', '#ffc94a', '#4ad98a', '#ff8a2a'];
      o += '<path id="' + u + 'p" d="M160 100 C200 40 270 40 270 100 C270 160 200 160 160 100 C120 40 50 40 50 100 C50 160 120 160 160 100Z" fill="none" stroke="url(#' + u + 'g)" stroke-width="5" stroke-linecap="round"/>';
      o += '<path d="M160 100 C200 40 270 40 270 100 C270 160 200 160 160 100 C120 40 50 40 50 100 C50 160 120 160 160 100Z" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1.2" stroke-dasharray="10 160"' + an('t2a-dash', 7, 0) + '/>';
      cols.forEach(function (c, i) { o += '<circle cx="' + (85 + i * 30) + '" cy="' + (i % 2 ? 150 : 52) + '" r="7" fill="' + c + '"' + an('t2a-pulse', 3 + i * .5, i * .4, 'center') + '/><circle cx="' + (85 + i * 30) + '" cy="' + (i % 2 ? 150 : 52) + '" r="12" fill="' + c + '" fill-opacity=".18"/>'; });
      return svg(u, '<linearGradient id="' + u + 'g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#a66bff"/><stop offset=".5" stop-color="#ffc94a"/><stop offset="1" stop-color="#4aa8ff"/></linearGradient>' + rad(u + 'bg', '#2a1a40', '#050308', .5, .5, .8), '<rect width="320" height="200" fill="#050308"/><rect width="320" height="200" fill="url(#' + u + 'bg)"/>' + o);
    }
  };
  /* Rifinitura grafica t4: strati aggiuntivi per rendere ogni sfondo riconoscibile a colpo d'occhio (solo forme originali, animazioni transform/opacity) */
  var X = {
    'sacra-linea': function (u) {
      return '<path d="M96 92 C130 60 190 56 250 40" stroke="#b86bff" stroke-opacity=".55" stroke-width="1.6" fill="none"/><path d="M178 106 C210 140 250 150 318 160" stroke="#ff5a6e" stroke-opacity=".5" stroke-width="1.6" fill="none"/>' +
        '<circle cx="250" cy="40" r="3" fill="#b86bff"' + an('t2a-pulse', 3.4, .3, 'center') + '/><circle cx="300" cy="158" r="3" fill="#ff5a6e"' + an('t2a-pulse', 3.8, .9, 'center') + '/>' +
        '<ellipse cx="150" cy="96" rx="46" ry="9" fill="#F6C86A" fill-opacity=".10"' + an('t2a-pulse', 5, 0, 'center') + '/>';
    },
    'terminale-tva': function (u) {
      var o = '<path d="M8 8h22M8 8v22M312 8h-22M312 8v22M8 192h22M8 192v-22M312 192h-22M312 192v-22" stroke="#6fe0d0" stroke-opacity=".6" stroke-width="1.4" fill="none"/>';
      for (var i = 0; i < 8; i++) o += '<rect x="' + (214 + i * 12) + '" y="' + (150 - (i % 4) * 8) + '" width="7" height="' + (14 + (i % 4) * 8) + '" fill="#6fe0d0" fill-opacity=".35"' + an('t2a-wave', 2.2 + i * .25, i * .2) + '/>';
      return o + '<text x="214" y="30" font-family="monospace" font-size="9" fill="#6fe0d0" fill-opacity=".7">TVA // SYS.OK</text>';
    },
    'dimensione-specchio': function (u) {
      return '<line x1="0" y1="100" x2="320" y2="100" stroke="#cfd8ff" stroke-opacity=".5" stroke-width="1"/><rect x="0" y="100" width="320" height="100" fill="#0a0d20" fill-opacity=".35"/>' +
        '<g stroke="#8fa8ff" stroke-opacity=".18">' + [40, 80, 120, 160, 200, 240, 280].map(function (x) { return '<path d="M' + x + ' 0V200"/>'; }).join('') + '</g>';
    },
    'dimensione-oscura': function (u) {
      return '<circle cx="160" cy="100" r="30" fill="none" stroke="#ff2e63" stroke-opacity=".5" stroke-width="2"' + an('t2a-pulse', 6, 0, 'center') + '/><path d="M0 200 Q160 120 320 200" stroke="#7a3fd0" stroke-opacity=".25" fill="none"/>';
    },
    'il-vuoto': function (u) {
      var o = ''; for (var i = 0; i < 5; i++) o += '<circle cx="160" cy="100" r="' + (74 + i * 22) + '" fill="none" stroke="#E3C79B" stroke-opacity="' + n1(.12 - i * .02) + '" stroke-dasharray="3 9"' + an(i % 2 ? 't2a-spin' : 't2a-spin-r', 120 + i * 30, 0, '160px 100px') + '/>';
      return o + '<path d="M160 100L40 20M160 100L300 40M160 100L280 190M160 100L30 170" stroke="#E3C79B" stroke-opacity=".08"/>';
    },
    'regno-quantico': function (u) {
      var o = '', pts = []; for (var i = 0; i < 6; i++) for (var j = 0; j < 4; j++) pts.push([30 + i * 52, 30 + j * 46]);
      pts.forEach(function (p, k) { var q = pts[(k + 5) % pts.length]; o += '<path d="M' + p[0] + ' ' + p[1] + 'L' + q[0] + ' ' + q[1] + '" stroke="#6fe8ff" stroke-opacity=".12"/>'; });
      pts.forEach(function (p, k) { if (k % 3 === 0) o += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="2.4" fill="#bff6ff"' + an('t2a-twinkle', 2 + (k % 5) * .4, k * .1) + '/>'; });
      return o;
    }
  };
  W.tvaT2Scenes = { scene: function (id, uid) { var f = S[id]; if (!f) return ''; var u = 't2s' + (uid || '') + id.replace(/[^a-z]/g, '').slice(0, 6), r = f(u); return X[id] ? r.replace(/<\/svg>$/, X[id](u) + '</svg>') : r; }, ids: Object.keys(S) };
})(window);
