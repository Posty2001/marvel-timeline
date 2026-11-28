/* TVA Atlas — Archivio esteso (Database Expansion). Caricato SOLO quando si usa la ricerca; dati lazy in atlante2/data/db/ (assenti = modulo inerte).
   Ricerca a shard: trigrammi (infix, alias, nomi italiani/originali, accenti) + indice prefissi per query corte. Nessuna dipendenza, nessun dato personale. */
(function () {
  'use strict';
  var W = window, SRC = (document.currentScript && document.currentScript.src) || '', BASE = SRC ? SRC.replace(/db\.js(\?.*)?$/, 'data/db/') : 'atlante2/data/db/';
  var META = null, C = {}, TIPO = { identita: 'Personaggi', organizzazione: 'Organizzazioni', artefatto: 'Artefatti', luogo: 'Luoghi', pianeta: 'Pianeti', evento: 'Eventi', battaglia: 'Battaglie', specie: 'Specie', civilta: 'Civiltà', opera: 'Opere', attore: 'Interpreti', creatore: 'Creatori', universo: 'Universi', 'entita-cosmica': 'Entità cosmiche' };
  function norm(s) { return String(s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim(); }
  var T = null; function crc(s) {
    if (!T) { T = []; for (var n = 0, c; n < 256; n++) { c = n; for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; T[n] = c >>> 0; } }
    var b = unescape(encodeURIComponent(s)), r = 0xFFFFFFFF; for (var i = 0; i < b.length; i++) r = T[(r ^ b.charCodeAt(i)) & 255] ^ (r >>> 8); return (r ^ 0xFFFFFFFF) >>> 0;
  }
  function load(p) { if (C[p]) return C[p]; return (C[p] = fetch(BASE + p).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).catch(function () { delete C[p]; return null; })); }
  function meta() { return META ? Promise.resolve(META) : load('meta.json').then(function (m) { return (META = m); }); }
  function rec(o) { return meta().then(function (m) { return m ? load('n/' + Math.floor(o / m.CH) + '.json').then(function (c) { return c ? c[o % m.CH] : null; }) : null; }); }
  function keysOf(r) { return r.t === 'x' ? r.al : [r.n, r.it || ''].concat(r.al || [], r.ip || []); }
  function score(r, nq, ws) {
    var best = 0; keysOf(r).forEach(function (k) { var nk = norm(k), s = 0; if (!nk) return;
      if (nk === nq) s = 100; else if (nk.indexOf(nq) === 0) s = 80; else if (nk.split(' ').some(function (x) { return x.indexOf(nq) === 0; })) s = 60; else if (ws.every(function (x) { return nk.indexOf(x) >= 0; })) s = 40;
      if (s > best) best = s; }); return best;
  }
  function search(q, cb) {
    var nq = norm(q); if (!nq) return cb([]);
    meta().then(function (m) {
      if (!m) return cb([]);
      var ws = nq.split(' '), w = ws.reduce(function (a, b) { return b.length > a.length ? b : a; }, ''), cand;
      var done = function (ids) {
        Promise.all(ids.slice(0, 400).map(function (o) { return rec(o).then(function (r) { return r ? [o, r] : null; }); })).then(function (rs) {
          var out = []; rs.forEach(function (x) { if (!x) return; var s = score(x[1], nq, ws); if (s) out.push([s, x[1]]); });
          out.sort(function (a, b) { return b[0] - a[0] || (a[1].n < b[1].n ? -1 : 1); }); cb(out.slice(0, 40).map(function (x) { return x[1]; }));
        });
      };
      if (w.length < 3) { load('pre.json').then(function (p) { done((p && p[w.slice(0, 2).length < 2 ? w + '_' : w.slice(0, 2)]) || []); }); return; }
      var ts = []; for (var i = 0; i < w.length - 2; i++) ts.push(w.substr(i, 3));
      Promise.all(ts.map(function (t) { return load('t/' + (crc(t) % m.SH) + '.json').then(function (d) { var a = 0; return d && d[t] ? d[t].map(function (x) { return (a += x); }) : []; }); })).then(function (sets) {
        sets.sort(function (a, b) { return a.length - b.length; }); var r = sets[0] || [];
        sets.slice(1).forEach(function (s) { var S = {}; s.forEach(function (x) { S[x] = 1; }); r = r.filter(function (x) { return S[x]; }); }); done(r);
      });
    });
  }
  function get(id, cb) {
    meta().then(function (m) { if (!m) return cb(null); var n = Math.ceil(m.N / m.CH), i = 0;
      (function next() { if (i >= n) return cb(null); load('n/' + (i++) + '.json').then(function (c) { var f = c && c.filter(function (r) { return r.i === id && r.t !== 'x'; })[0]; f ? cb(f) : next(); }); })(); });
  }
  function lista(t, cb) {   // tutte le voci di un tipo (catalogo esteso), ordinate per nome
    meta().then(function (m) { if (!m) return cb([]); var n = Math.ceil(m.N / m.CH), out = [], i = 0;
      (function next() { if (i >= n) return cb(out.sort(function (a, b) { return a.n < b.n ? -1 : a.n > b.n ? 1 : 0; })); load('n/' + (i++) + '.json').then(function (c) { (c || []).forEach(function (r) { if (r.t === t) out.push(r); }); next(); }); })(); });
  }
  function at(o, id) { return rec(o).then(function (r) { return r && (!id || r.i === id) ? r : null; }); }
  W.tvaDb = { at: at, lista: lista, tipi: function (cb) { meta().then(function (m) { cb(m ? m.tipi || {} : {}); }); }, search: search, get: get, norm: norm, TIPO: TIPO, available: function (cb) { meta().then(function (m) { cb(!!m); }); } };
})();
