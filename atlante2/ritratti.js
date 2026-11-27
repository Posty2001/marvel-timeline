/* Atlante 2.0 — A3.1: Ritratti PRIVATI. Archivio locale (IndexedDB «tva-atlante-ritratti») + selettore scene TMDB + ritaglio 3:4 + esporta/importa.
   Principi: nessuna immagine protetta nel repository/ZIP/deploy; nessuna chiave API nel frontend (i candidati sono metadati generati lato server);
   nessuna scrittura in localStorage né nei dati di backup/sincronizzazione esistenti (database separato, chiave = ID identità).
   Nessun HTML dai dati: solo textContent/attributi. Le immagini TMDB si caricano dal CDN già consentito dalla CSP (img-src). */
(function () {
  'use strict';
  var W = window, D = document;
  if (W.tvaRit) return;
  var DB = 'tva-atlante-ritratti', STORE = 'ritratti', VER = 1, OUT_W = 480, OUT_H = 640, MAX_IMPORT = 3 * 1024 * 1024;
  var TM = 'https://image.tmdb.org/t/p/', PATH_RX = /^\/[A-Za-z0-9_-]{5,60}\.(jpg|png)$/;
  var ATTR = 'Scene: indice e immagini via TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB. I fotogrammi sono di proprietà degli studi titolari: uso personale, non commerciale.';
  var MEM = {}, DBP = null, USING_MEM = false, KEYS = null, URLS = {}, WAIT = [];

  function h(tag, cls, txt, at) { var n = D.createElement(tag); if (cls) n.className = cls; if (txt != null) n.textContent = txt; if (at) Object.keys(at).forEach(function (k) { n.setAttribute(k, at[k]); }); return n; }
  function btn(cls, txt, fn) { var b = h('button', cls, txt); b.type = 'button'; if (fn) b.addEventListener('click', fn); return b; }

  /* ---------- archivio ---------- */
  var SIBLINGS = { 'id-matt-murdock-daredevil': ['id-matt-murdock-mcu'], 'id-matt-murdock-mcu': ['id-matt-murdock-daredevil'] };
  function open() {
    if (DBP) return DBP;
    DBP = new Promise(function (res) {
      function mem() { USING_MEM = true; res(null); }
      try {
        if (!W.indexedDB) return mem();
        var rq = W.indexedDB.open(DB, VER);
        rq.onupgradeneeded = function () { var d = rq.result; if (!d.objectStoreNames.contains(STORE)) d.createObjectStore(STORE, { keyPath: 'id' }); };
        rq.onsuccess = function () { res(rq.result); }; rq.onerror = mem; rq.onblocked = mem;
      } catch (e) { mem(); }
    });
    return DBP;
  }
  function run(mode, fn) {
    return open().then(function (db) {
      if (!db) return fn(null);
      return new Promise(function (res, rej) { var t = db.transaction(STORE, mode), os = t.objectStore(STORE), out = fn(os); t.oncomplete = function () { res(out && typeof out === 'object' && 'readyState' in out ? (out.result === undefined ? null : out.result) : out); }; t.onerror = t.onabort = function () { rej(t.error || new Error('archivio')); }; });
    });
  }
  function all() { return run('readonly', function (os) { if (!os) return Object.keys(MEM).map(function (k) { return MEM[k]; }); return os.getAll(); }).then(function (r) { return r || []; }); }
  function getRec(id) { return run('readonly', function (os) { if (!os) return MEM[id] || null; return os.get(id); }).then(function (r) { return r || null; }); }
  function putRec(rec) { return run('readwrite', function (os) { if (!os) { MEM[rec.id] = rec; return null; } return os.put(rec); }).then(function () { if (KEYS) KEYS[rec.id] = 1; drop(rec.id); changed(rec.id); persist(); }); }
  function delRec(id) { return run('readwrite', function (os) { if (!os) { delete MEM[id]; return null; } return os.delete(id); }).then(function () { if (KEYS) delete KEYS[id]; drop(id); changed(id); }); }
  function drop(id) { if (URLS[id]) { try { URL.revokeObjectURL(URLS[id]); } catch (e) { /* nulla */ } delete URLS[id]; } }
  function ids() { if (KEYS) return Promise.resolve(KEYS); return all().then(function (l) { KEYS = {}; l.forEach(function (r) { KEYS[r.id] = 1; }); return KEYS; }); }
  function changed(id) { WAIT.forEach(function (f) { try { f(id); } catch (e) { /* nulla */ } }); }
  function persist() { try { if (W.navigator.storage && W.navigator.storage.persist) return W.navigator.storage.persist(); } catch (e) { /* nulla */ } return Promise.resolve(false); }
  function persisted() { try { if (W.navigator.storage && W.navigator.storage.persisted) return W.navigator.storage.persisted(); } catch (e) { /* nulla */ } return Promise.resolve(null); }

  /* ---------- rendering di un ritratto ---------- */
  function refStyle(rec) {
    var s = rec.scena || {}, c = rec.crop || { z: 1, cx: .5, cy: .5 }, ar = (s.w && s.h) ? s.w / s.h : 16 / 9, fw = 0.75, wd = c.z * ar;
    var px = (fw / 2 - c.cx * wd) / (fw - wd), py = (0.5 - c.cy * c.z) / (1 - c.z);
    return { size: (wd / fw * 100).toFixed(2) + '% ' + (c.z * 100).toFixed(2) + '%', pos: (isFinite(px) ? px * 100 : 50).toFixed(2) + '% ' + (isFinite(py) ? py * 100 : 50).toFixed(2) + '%' };
  }
  function node(rec, big) {
    if (rec.kind === 'copy' && rec.blob) { var im = h('img', 'a3-pt', null, { alt: '', decoding: 'async', loading: 'lazy' }); URLS[rec.id] = URLS[rec.id] || URL.createObjectURL(rec.blob); im.src = URLS[rec.id]; return im; }
    if (rec.kind === 'ref' && rec.scena && PATH_RX.test(rec.scena.p)) { var d = h('div', 'a3-pt a3-ptr', null, { role: 'img', 'aria-label': rec.titolo || '' }), st = refStyle(rec); d.style.backgroundImage = 'url("' + TM + (big ? 'w1280' : 'w780') + rec.scena.p + '")'; d.style.backgroundSize = st.size; d.style.backgroundPosition = st.pos; return d; }
    return null;
  }
  /** Applica (se esiste) il ritratto privato dentro `el`, sopra l'emblema. Nessun effetto se assente. */
  function paint(el, id, big) {
    return ids().then(function (k) {
      if (!k[id] || !el.isConnected) return; return getRec(id).then(function (rec) {
        if (!rec || !el.isConnected) return; var old = el.querySelector('.a3-pt'); if (old) old.remove(); var n = node(rec, big); if (n) { el.appendChild(n); el.classList.add('has-pt'); }
      });
    }).catch(function () { /* ritratto non disponibile: resta l'emblema */ });
  }

  /* ---------- immagini / codifica ---------- */
  function loadImg(src, cors) { return new Promise(function (res, rej) { var im = new Image(); if (cors) im.crossOrigin = 'anonymous'; im.onload = function () { res(im); }; im.onerror = function () { rej(new Error('img')); }; im.decoding = 'async'; im.src = src; }); }
  function encode(cv) {
    return new Promise(function (res, rej) {
      function jpg() { cv.toBlob(function (b) { b ? res(b) : rej(new Error('codifica')); }, 'image/jpeg', 0.86); }
      try { cv.toBlob(function (b) { if (b && b.type === 'image/webp') res(b); else jpg(); }, 'image/webp', 0.82); } catch (e) { rej(e); }
    });
  }
  function cropBlob(im, c) {
    var iw = im.naturalWidth, ih = im.naturalHeight, ar = iw / ih, vw = .75 / (c.z * ar), vh = 1 / c.z, cv = D.createElement('canvas'); cv.width = OUT_W; cv.height = OUT_H;
    var ctx = cv.getContext('2d'); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(im, (c.cx - vw / 2) * iw, (c.cy - vh / 2) * ih, vw * iw, vh * ih, 0, 0, OUT_W, OUT_H); return encode(cv);
  }
  function clamp(c, ar) { var vw = .75 / (c.z * ar), vh = 1 / c.z; c.z = Math.max(1, Math.min(4, c.z)); vw = .75 / (c.z * ar); vh = 1 / c.z; c.cx = Math.max(vw / 2, Math.min(1 - vw / 2, c.cx)); c.cy = Math.max(vh / 2, Math.min(1 - vh / 2, c.cy)); return c; }

  /* ---------- ritagliatore 3:4 (trascina, pizzica, cursore) ---------- */
  function cropper(host, im, ar, init) {
    var fwPx = Math.min(300, Math.max(180, (W.innerWidth || 360) - 64)), fhPx = Math.round(fwPx * 4 / 3), c = clamp({ z: (init && init.z) || 1, cx: (init && init.cx) || .5, cy: (init && init.cy) || .5 }, ar);
    var fr = h('div', 'a3r-frame'); fr.style.width = fwPx + 'px'; fr.style.height = fhPx + 'px'; var pic = im.cloneNode(); pic.className = 'a3r-pic'; pic.draggable = false; pic.style.position = 'absolute'; pic.style.maxWidth = 'none'; fr.appendChild(pic);
    var sl = h('input', 'a3r-zoom', null, { type: 'range', min: '1', max: '4', step: '0.01', 'aria-label': 'Zoom' }); sl.value = String(c.z);
    function draw() { var hd = fhPx * c.z, wd = hd * ar; pic.style.width = wd + 'px'; pic.style.height = hd + 'px'; pic.style.left = (fwPx / 2 - c.cx * wd) + 'px'; pic.style.top = (fhPx / 2 - c.cy * hd) + 'px'; sl.value = String(c.z); }
    var P = {}, last = null;
    fr.addEventListener('pointerdown', function (e) { fr.setPointerCapture(e.pointerId); P[e.pointerId] = { x: e.clientX, y: e.clientY }; last = null; });
    fr.addEventListener('pointermove', function (e) {
      if (!P[e.pointerId]) return; var k = Object.keys(P), o = P[e.pointerId], hd = fhPx * c.z, wd = hd * ar;
      if (k.length >= 2) { var a = P[k[0]], b = P[k[1]]; var d0 = Math.hypot(a.x - b.x, a.y - b.y); P[e.pointerId] = { x: e.clientX, y: e.clientY }; var a2 = P[k[0]], b2 = P[k[1]], d1 = Math.hypot(a2.x - b2.x, a2.y - b2.y); if (d0 > 0) c.z *= d1 / d0; }
      else { c.cx -= (e.clientX - o.x) / wd; c.cy -= (e.clientY - o.y) / hd; P[e.pointerId] = { x: e.clientX, y: e.clientY }; }
      clamp(c, ar); draw(); e.preventDefault();
    });
    function up(e) { delete P[e.pointerId]; } fr.addEventListener('pointerup', up); fr.addEventListener('pointercancel', up);
    fr.addEventListener('wheel', function (e) { c.z *= e.deltaY < 0 ? 1.06 : 0.94; clamp(c, ar); draw(); e.preventDefault(); }, { passive: false });
    sl.addEventListener('input', function () { c.z = parseFloat(sl.value); clamp(c, ar); draw(); });
    host.appendChild(fr); host.appendChild(h('label', 'a3r-lbl', 'Zoom')); host.appendChild(sl); draw();
    return { get: function () { return { z: +c.z.toFixed(4), cx: +c.cx.toFixed(4), cy: +c.cy.toFixed(4) }; } };
  }

  /* ---------- editor (overlay a schermo intero) ---------- */
  var CANDS = null;
  var CIDX = null, CID = {};
  function getJson(u) { return fetch(u, { credentials: 'same-origin' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }); }
  /* indice delle identità con candidati (ondata corrente); ripiega sul file del pilota */
  function indice() {
    if (CIDX) return Promise.resolve(CIDX);
    return Promise.all([candidati(), getJson('atlante2/data/pilot/c/_indice.json').catch(function () { return { identita: [] }; })]).then(function (z) {
      var out = (z[0].identita || []).map(function (q) { return q.id; }); (z[1].identita || []).forEach(function (i) { if (typeof i === 'string' && /^[a-z0-9-]{3,80}$/.test(i) && out.indexOf(i) < 0) out.push(i); });   // prima le 10 del pilota, poi le nuove
      CIDX = out; return out;
    });
  }
  /* candidati di UNA identità (file lazy c/<id>.json, con ripiego sul vecchio file unico) */
  function candId(id) {
    if (CID[id]) return CID[id];
    var safe = /^[a-z0-9-]{3,80}$/.test(id) ? id : null;
    CID[id] = (safe ? getJson('atlante2/data/pilot/c/' + safe + '.json') : Promise.reject(0)).catch(function () { return candidati().then(function (j) { return infoId(j, id); }); }).then(function (r) { if (r && !r.attore) r.attore = { nome: 'interprete non indicato' }; return r || null; });
    return CID[id];
  }
  function candidati() { if (CANDS) return Promise.resolve(CANDS); return getJson('atlante2/data/pilot/candidati.json').then(function (j) { CANDS = j; return j; }).catch(function () { CANDS = { identita: [] }; return CANDS; }); }
  var PROP = null;   // proposte del motore A3.2 (metadati: percorsi CDN, punteggi, ritaglio suggerito); l'utente decide sempre
  function proposte() {
    if (PROP) return Promise.resolve(PROP);
    return Promise.all([getJson('atlante2/data/pilot/proposte.json').catch(function () { return { identita: [] }; }), getJson('atlante2/data/pilot/proposte2.json').catch(function () { return { identita: [] }; })]).then(function (a) {
      var m = {}; (a[0].identita || []).forEach(function (z) { m[z.id] = z; }); (a[1].identita || []).forEach(function (z) { if (z && z.proposte && z.proposte.length) m[z.id] = z; });   // il motore 2.0 prevale sul prototipo
      PROP = { identita: Object.keys(m).map(function (k) { return m[k]; }) }; return PROP;
    });
  }
  function propId(id) { return proposte().then(function (pj) { return (pj.identita || []).filter(function (z) { return z.id === id; })[0] || null; }); }
  function infoId(j, id) { for (var i = 0; i < j.identita.length; i++) if (j.identita[i].id === id) return j.identita[i]; return null; }

  function openEditor(id, nome, known) {
    var ov = h('div', 'a3r'); ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'Ritratto privato — ' + nome);
    var top = h('header', 'a3r-top'); top.appendChild(btn('a3r-x', 'Chiudi', close)); top.appendChild(h('b', '', nome)); ov.appendChild(top);
    var main = h('div', 'a3r-main'); ov.appendChild(main); (D.getElementById('atlas2') || D.body).appendChild(ov);
    function close() { ov.remove(); D.removeEventListener('keydown', esc); } function esc(e) { if (e.key === 'Escape') close(); } D.addEventListener('keydown', esc);
    function msg(t, bad) { var m = main.querySelector('.a3r-msg'); if (!m) { m = h('p', 'a3r-msg'); main.insertBefore(m, main.firstChild); } m.textContent = t; m.classList.toggle('bad', !!bad); }
    function clear() { main.textContent = ''; }

    function home() {
      clear(); getRec(id).then(function (rec) {
        var pv = h('div', 'a3r-prev'); var n = rec && node(rec, true); if (n) pv.appendChild(n); else pv.appendChild(h('span', 'a3r-none', 'Nessun ritratto')); main.appendChild(pv);
        main.appendChild(h('p', 'a3r-info', rec ? (rec.kind === 'copy' ? 'Copia privata su questo dispositivo' : 'Riferimento a scena TMDB') + (rec.titolo ? ' · ' + rec.titolo : '') + ' · ' + (rec.fonte === 'tmdb-scena' ? 'fotogramma © studio titolare, via TMDB' : 'importata da te') : 'Questo ritratto resta solo sul tuo dispositivo: non è nel repository, nello ZIP né sul sito.'));
        var row = h('div', 'a3r-row');
        row.appendChild(btn('a3r-b pri', rec ? 'Sostituisci con una scena TMDB' : 'Scegli una scena TMDB', scene));
        row.appendChild(btn('a3r-b', 'Importa da foto o file', pick));
        if (rec && rec.kind === 'copy') row.appendChild(btn('a3r-b', 'Ritaglia di nuovo', function () { recrop(rec); }));
        if (rec && rec.kind === 'ref') row.appendChild(btn('a3r-b', 'Ritaglia di nuovo', function () { recropRef(rec); }));
        if (rec) row.appendChild(btn('a3r-b warn', 'Rimuovi', function () { confirmDel(); }));
        main.appendChild(row);
        /* Riassegnazione sicura tra identità gemelle (es. Matt Murdock 2003 / MCU): mai sovrascrive un ritratto già salvato; lo spostamento cancella l'origine solo dopo la scrittura riuscita */
        var sib = (SIBLINGS[id] || []).filter(function (t) { return t !== id; });
        if (rec && sib.length) sib.forEach(function (t) {
          var nm = (known && known(t)) || t, r2 = h('div', 'a3r-row');
          function esegui(sposta) {
            getRec(t).then(function (ex) {
              if (ex) { msg('«' + nm + '» ha già un ritratto: non viene sovrascritto. Rimuovilo prima se vuoi sostituirlo.', true); return; }
              var cp = {}; Object.keys(rec).forEach(function (k) { cp[k] = rec[k]; }); cp.id = t; cp.riassegnato_da = id;
              return putRec(cp).then(function () { return sposta ? delRec(id).then(function () { drop(id); changed(id); }) : null; }).then(function () { changed(t); home(); setTimeout(function () { msg(sposta ? 'Ritratto spostato su «' + nm + '».' : 'Ritratto copiato su «' + nm + '».'); }, 80); });
            }).catch(function () { msg('Operazione non riuscita: nessun ritratto è stato perso.', true); });
          }
          r2.appendChild(btn('a3r-b', 'Sposta su ' + nm, function () { esegui(true); })); r2.appendChild(btn('a3r-b', 'Copia su ' + nm, function () { esegui(false); })); main.appendChild(r2);
        }); main.appendChild(h('p', 'a3r-fine', 'Archivio, esportazione e importazione di tutti i ritratti: voce «Ritratti privati» nella Home di TVA Atlas.'));
      });
    }
    function confirmDel() { var m = h('div', 'a3r-conf'); m.appendChild(h('p', '', 'Rimuovere il ritratto di «' + nome + '»? L’emblema tornerà come segnaposto. Non è annullabile, salvo reimportazione da un’esportazione.')); m.appendChild(btn('a3r-b warn', 'Rimuovi', function () { delRec(id).then(home); })); m.appendChild(btn('a3r-b', 'Annulla', home)); clear(); main.appendChild(m); }
    function pick() {
      var f = h('input', '', null, { type: 'file', accept: 'image/*' }); f.addEventListener('change', function () { var file = f.files && f.files[0]; if (!file) return; if (file.size > 25 * 1024 * 1024) { msg('File troppo grande (max 25 MB).', true); return; } var u = URL.createObjectURL(file); loadImg(u, false).then(function (im) { crop(im, null, { fonte: 'import-locale', titolo: file.name.slice(0, 60) }, u); }).catch(function () { URL.revokeObjectURL(u); msg('Immagine non leggibile.', true); }); }); f.click();
    }
    function recrop(rec) { var u = URL.createObjectURL(rec.blob); loadImg(u, false).then(function (im) { crop(im, null, { fonte: rec.fonte, titolo: rec.titolo, scena: rec.scena }, u); }); }
    function recropRef(rec) { loadImg(TM + 'w780' + rec.scena.p, false).then(function (im) { crop(im, rec.crop, { fonte: rec.fonte, titolo: rec.titolo, scena: rec.scena, soloRef: true }, null, rec.scena.w / rec.scena.h); }).catch(function () { msg('Scena non raggiungibile.', true); }); }
    function crop(im, init, meta, objUrl, arOverride) {
      clear(); var ar = arOverride || (im.naturalWidth / im.naturalHeight), box = h('div', 'a3r-crop'); main.appendChild(box); main.appendChild(h('p', 'a3r-info', 'Trascina per spostare, pizzica o usa il cursore per ingrandire. Il riquadro è il formato verticale 3:4 del ritratto.'));
      var cr = cropper(box, im, ar, init), row = h('div', 'a3r-row');
      row.appendChild(btn('a3r-b pri', 'Salva ritratto', function () { salva(); })); row.appendChild(btn('a3r-b', 'Annulla', function () { if (objUrl) URL.revokeObjectURL(objUrl); home(); })); main.appendChild(row);
      function salva() {
        var c = cr.get(), base = { id: id, fonte: meta.fonte, titolo: meta.titolo || '', scena: meta.scena || null, crop: c, ts: Date.now(), v: 1 };
        var chk = Promise.resolve(null);
        if (meta.scena) chk = all().then(function (l) { var o = l.filter(function (r) { return r.id !== id && r.scena && r.scena.p === meta.scena.p; })[0]; return o ? o.id : null; });
        chk.then(function (dup) {
          if (dup && !meta.conferma) { var nm = (known && known(dup)) || dup; var m = h('div', 'a3r-conf'); m.appendChild(h('p', '', 'Questa stessa scena è già usata per «' + nm + '». Le varianti devono avere ritratti distinti: vuoi usarla comunque?')); m.appendChild(btn('a3r-b warn', 'Usa comunque', function () { meta.conferma = 1; salva(); })); m.appendChild(btn('a3r-b', 'Torna al ritaglio', function () { crop(im, c, meta, objUrl, ar); })); clear(); main.appendChild(m); return; }
          if (meta.soloRef) { base.kind = 'ref'; return putRec(base).then(function () { msg('Ritaglio aggiornato.'); home(); }); }
          return cropBlob(im, c).then(function (b) { base.kind = 'copy'; base.blob = b; base.mime = b.type; base.w = OUT_W; base.h = OUT_H; return putRec(base); }).catch(function () {
            if (meta.scena) { base.kind = 'ref'; return putRec(base).then(function () { home(); msg('Copia locale non possibile da questa fonte: salvato come riferimento alla scena.'); }); }
            msg('Salvataggio non riuscito.', true);
          }).then(function () { if (objUrl) URL.revokeObjectURL(objUrl); if (main.querySelector('.a3r-crop')) home(); });
        });
      }
      if (meta.auto) { meta.auto = 0; salva(); }
    }
    function scene() {
      clear(); main.appendChild(h('p', 'a3r-info', 'Caricamento delle scene candidate…')); candId(id).then(function (inf) {
        clear();
        if (!inf || !inf.immagini.length) { main.appendChild(h('p', 'a3r-info', 'Per questa identità non ci sono ancora scene candidate. Puoi importare una tua immagine.')); main.appendChild(btn('a3r-b', 'Indietro', home)); return; }
        main.appendChild(btn('a3r-b', 'Indietro', home));
        main.appendChild(h('p', 'a3r-info', 'Interprete: ' + inf.attore.nome + '. ' + (inf.nota || 'Scegli una scena in cui il personaggio è chiaramente riconoscibile in questa continuità.')));
        var tabs = h('div', 'a3r-tabs'), grid = h('div', 'a3r-grid'), nums = []; inf.titoli.forEach(function (t) { if (t.verificato) nums.push(t); });
        var shown = nums[0] ? nums[0].num : null;
        function fill() {
          grid.textContent = ''; Array.prototype.forEach.call(tabs.children, function (b) { b.classList.toggle('on', b.getAttribute('data-n') === shown); });
          inf.immagini.filter(function (x) { return x.num === shown; }).forEach(function (x) {
            if (!PATH_RX.test(x.p)) return; var b = btn('a3r-th', null, function () { scegli(x); }); b.setAttribute('aria-label', 'Scena ' + (x.tag ? '(con interprete segnalato) ' : '') + x.w + ' per ' + x.h);
            var im = h('img', '', null, { alt: '', loading: 'lazy', decoding: 'async', src: TM + 'w300' + x.p }); b.appendChild(im); if (x.tag) b.appendChild(h('i', 'tg', '★')); grid.appendChild(b);
          });
        }
        nums.forEach(function (t) { var b = btn('a3r-tab', t.titolo_tmdb, function () { shown = t.num; fill(); }); b.setAttribute('data-n', t.num); tabs.appendChild(b); });
        propId(id).then(function (pi) {
          if (!pi || !pi.proposte || !pi.proposte.length) return;
          var box = h('section', 'a3r-prop'); box.appendChild(h('h3', '', 'Proposte automatiche (' + pi.proposte.length + ')'));
          box.appendChild(h('p', 'a3r-info', (pi.conf === 'bassa' ? 'Confidenza BASSA: il motore non ha trovato scene sicure, quindi ne propone di più (fino a 10). ' : '') + 'Selezionate dal motore tra le scene della continuità, con ritaglio suggerito. ★ = scena confermata da entrambi i modelli. Tocca ✓ per approvare subito, o la scena per rivedere il ritaglio. La scelta resta tua.'));
          var g = h('div', 'a3r-pg'); pi.proposte.forEach(function (x) {
            var t = inf.titoli.filter(function (y) { return y.num === x.num; })[0]; var st = refStyle({ scena: { w: x.w, h: x.h }, crop: x.crop });
            var c = h('div', 'a3r-pc'); var pv = btn('a3r-pv', null, function () { scegli(x, x.crop, false); }); pv.setAttribute('aria-label', 'Proposta ' + x.rk + ', rivedi il ritaglio');
            pv.style.backgroundImage = 'url("' + TM + 'w780' + x.p + '")'; pv.style.backgroundSize = st.size; pv.style.backgroundPosition = st.pos; pv.appendChild(h('i', 'rk', '#' + x.rk + (x.ck ? ' ★' : '')));
            var ok = btn('a3r-ok', '✓ Approva', function () { scegli(x, x.crop, true); }); ok.setAttribute('aria-label', 'Approva la proposta ' + x.rk + ' con il ritaglio suggerito'); c.appendChild(pv); c.appendChild(ok); g.appendChild(c);
          }); box.appendChild(g); main.insertBefore(box, tabs);
        });
        main.appendChild(tabs); main.appendChild(grid); main.appendChild(h('p', 'a3r-fine', ATTR)); fill();
        function scegli(x, ini, auto) {
          var t = inf.titoli.filter(function (y) { return y.num === x.num; })[0]; clear(); main.appendChild(h('p', 'a3r-info', 'Caricamento della scena…'));
          var meta = { fonte: 'tmdb-scena', titolo: t ? t.titolo_tmdb : '', auto: auto ? 1 : 0, scena: { p: x.p, w: x.w, h: x.h, tid: t ? t.tmdb_id : null, num: x.num } }; if (x.rk) { meta.scena.rk = x.rk; meta.scena.sc = x.sc; }
          loadImg(TM + 'w1280' + x.p, true).then(function (im) { crop(im, ini || null, meta, null); }).catch(function () {
            loadImg(TM + 'w1280' + x.p, false).then(function (im) { meta.soloRef = true; crop(im, ini || null, meta, null); main.insertBefore(h('p', 'a3r-msg', 'Il sito non consente la copia locale: il ritratto verrà salvato come riferimento alla scena (serve la rete per vederlo).'), main.firstChild); }).catch(function () { clear(); main.appendChild(h('p', 'a3r-msg bad', 'Scena non raggiungibile (rete assente o immagine rimossa).')); main.appendChild(btn('a3r-b', 'Indietro', scene)); });
          });
        }
      });
    }
    home();
  }

  /* ---------- esporta / importa (file .json, solo sul tuo dispositivo) ---------- */
  function b64(blob) { return new Promise(function (res, rej) { var r = new FileReader(); r.onload = function () { res(r.result); }; r.onerror = rej; r.readAsDataURL(blob); }); }
  function exportAll() {
    return all().then(function (l) {
      return Promise.all(l.map(function (r) {
        var o = { id: r.id, kind: r.kind, fonte: r.fonte, titolo: r.titolo || '', scena: r.scena || null, crop: r.crop || null, ts: r.ts, v: 1 };
        if (r.kind === 'copy' && r.blob) return b64(r.blob).then(function (d) { o.dati = d; return o; }); return o;
      }));
    }).then(function (voci) { return { formato: 'tva-ritratti', versione: 1, creato: new Date().toISOString(), nota: 'Contiene immagini protette da copyright degli studi: uso personale e non commerciale, non condividere.', voci: voci }; });
  }
  function downloadExport() {
    return exportAll().then(function (o) {
      var blob = new Blob([JSON.stringify(o)], { type: 'application/json' }), name = 'tva-ritratti-' + new Date().toISOString().slice(0, 10) + '.json', file = null;
      try { file = new File([blob], name, { type: 'application/json' }); } catch (e) { /* nulla */ }
      if (file && W.navigator.canShare && W.navigator.canShare({ files: [file] })) return W.navigator.share({ files: [file], title: 'Ritratti privati TVA Archives' }).then(function () { return o.voci.length; }, function (e) { if (e && e.name === 'AbortError') return o.voci.length; throw e; });
      var a = h('a', '', null, { href: URL.createObjectURL(blob), download: name }); D.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 2000); return o.voci.length;
    });
  }
  /** Valida e importa. opts: {known(id)->bool, sovrascrivi:boolean}. Ritorna {ok, saltati, errori:[]} */
  function importJson(txt, opts) {
    var rep = { importati: 0, saltati: 0, errori: [] }, o; opts = opts || {};
    try { o = JSON.parse(txt); } catch (e) { rep.errori.push('File non valido (JSON).'); return Promise.resolve(rep); }
    if (!o || o.formato !== 'tva-ritratti' || o.versione !== 1 || !Array.isArray(o.voci) || o.voci.length > 1000) { rep.errori.push('Formato non riconosciuto.'); return Promise.resolve(rep); }
    return ids().then(function (k) {
      return o.voci.reduce(function (p, v) {
        return p.then(function () {
          if (!v || typeof v.id !== 'string' || (opts.known && !opts.known(v.id))) { rep.saltati++; rep.errori.push('Identità sconosciuta: ' + String(v && v.id).slice(0, 60)); return; }
          if (k[v.id] && !opts.sovrascrivi) { rep.saltati++; return; }
          var rec = { id: v.id, kind: v.kind, fonte: v.fonte === 'tmdb-scena' ? 'tmdb-scena' : 'import-locale', titolo: String(v.titolo || '').slice(0, 80), ts: +v.ts || Date.now(), v: 1, crop: null, scena: null };
          if (v.crop && [v.crop.z, v.crop.cx, v.crop.cy].every(function (n) { return typeof n === 'number' && isFinite(n); })) rec.crop = { z: v.crop.z, cx: v.crop.cx, cy: v.crop.cy };
          if (v.scena && PATH_RX.test(v.scena.p || '')) rec.scena = { p: v.scena.p, w: +v.scena.w || 1920, h: +v.scena.h || 1080, tid: +v.scena.tid || null, num: String(v.scena.num || '').slice(0, 4) };
          if (v.kind === 'ref') { if (!rec.scena || !rec.crop) { rep.saltati++; rep.errori.push('Riferimento incompleto: ' + v.id); return; } return putRec(rec).then(function () { rep.importati++; }); }
          var m = /^data:(image\/(?:webp|jpeg|png));base64,([A-Za-z0-9+\/=]+)$/.exec(v.dati || '');
          if (v.kind !== 'copy' || !m || m[2].length * 0.75 > MAX_IMPORT) { rep.saltati++; rep.errori.push('Immagine non valida: ' + v.id); return; }
          var bin = atob(m[2]), u8 = new Uint8Array(bin.length); for (var i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i); var blob = new Blob([u8], { type: m[1] }), u = URL.createObjectURL(blob);
          return loadImg(u, false).then(function () { URL.revokeObjectURL(u); rec.kind = 'copy'; rec.blob = blob; rec.mime = m[1]; rec.w = OUT_W; rec.h = OUT_H; return putRec(rec).then(function () { rep.importati++; }); }, function () { URL.revokeObjectURL(u); rep.saltati++; rep.errori.push('Immagine non decodificabile: ' + v.id); });
        });
      }, Promise.resolve());
    }).then(function () { return rep; });
  }

  /* ---------- revisione rapida consecutiva (A3.2 v2) ---------- */
  function downloadJson(name, obj) {
    var blob = new Blob([JSON.stringify(obj, null, 1)], { type: 'application/json' }), a = h('a', '', null, { href: URL.createObjectURL(blob), download: name });
    D.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 2000);
  }
  /** Solo METADATI delle scelte (nessuna immagine): serve a misurare la precisione del motore (posizione della proposta scelta). */
  function valutazioni() {
    return all().then(function (l) {
      var voci = l.map(function (r) { return { id: r.id, kind: r.kind, fonte: r.fonte, num: r.scena ? (r.scena.num || null) : null, rk: r.scena && r.scena.rk ? r.scena.rk : null, sc: r.scena && r.scena.sc != null ? r.scena.sc : null, origine: r.scena ? (r.scena.rk ? 'proposta' : 'scena-manuale') : 'file-locale' }; });
      var con = voci.filter(function (v) { return v.rk; }), at = function (k) { return con.filter(function (v) { return v.rk <= k; }).length; };
      return { formato: 'tva-valutazioni', versione: 2, creato: new Date().toISOString(), totale: voci.length, da_proposta: con.length, scene_manuali: voci.filter(function (v) { return v.origine === 'scena-manuale'; }).length, file_locali: voci.filter(function (v) { return v.origine === 'file-locale'; }).length, rk1: at(1), rk3: at(3), rk5: at(5), rk10: at(10), voci: voci };
    });
  }
  /** Contatori sul totale delle identità dell'indice: completati / mancanti. */
  function conteggio() { return Promise.all([indice(), ids()]).then(function (a) { var f = a[0].filter(function (i) { return a[1][i]; }).length; return { totale: a[0].length, fatti: f, mancanti: a[0].length - f }; }); }
  function revisione(known) {
    var ov = h('div', 'a3r'); ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('aria-label', 'Revisione rapida dei ritratti');
    var top = h('header', 'a3r-top'); top.appendChild(btn('a3r-x', 'Chiudi', close)); top.appendChild(h('b', '', 'Revisione rapida')); ov.appendChild(top);
    var main = h('div', 'a3r-main'); ov.appendChild(main); (D.getElementById('atlas2') || D.body).appendChild(ov);
    function close() { ov.remove(); D.removeEventListener('keydown', esc); } function esc(e) { if (e.key === 'Escape') close(); } D.addEventListener('keydown', esc);
    var Q = [], qi = 0, pi = 0, saved = 0, skipped = 0, busy = false, note = '';
    main.appendChild(h('p', 'a3r-info', 'Preparazione della coda…'));
    Promise.all([indice(), ids(), proposte()]).then(function (a) {
      var props = {}; (a[2].identita || []).forEach(function (z) { if (z.proposte && z.proposte.length) props[z.id] = 1; });
      Q = a[0].filter(function (id) { return !a[1][id] && props[id]; }); show();
    });
    function done() { main.textContent = ''; main.appendChild(h('p', 'a3r-info', 'Revisione terminata: ' + saved + ' ritratti salvati, ' + skipped + ' identità saltate (restano senza ritratto, nulla è stato sovrascritto).')); main.appendChild(btn('a3r-b pri', 'Chiudi', close)); }
    function show() {
      main.textContent = ''; busy = false; pi = 0;
      if (qi >= Q.length) { done(); return; }
      var id = Q[qi];
      Promise.all([candId(id), propId(id), getRec(id)]).then(function (a) {
        var inf = a[0], pr = a[1], rec = a[2];
        if (rec || !inf || !pr || !pr.proposte.length) { qi++; show(); return; }   // già presente (mai sovrascritto) o senza proposte
        draw(id, inf, pr);
      }).catch(function () { qi++; show(); });
    }
    function draw(id, inf, pr) {
      main.textContent = ''; var P = pr.proposte, x = P[pi], t = inf.titoli.filter(function (y) { return y.num === x.num; })[0];
      var cn = h('p', 'a3r-info', (qi + 1) + ' / ' + Q.length + ' · salvati ' + saved); main.appendChild(cn); conteggio().then(function (c) { cn.textContent += ' · completati ' + c.fatti + ' di ' + c.totale + ', mancanti ' + c.mancanti; });
      main.appendChild(h('h3', '', inf.nome || id));
      main.appendChild(h('p', 'a3r-info', 'Interprete: ' + (inf.attore ? inf.attore.nome : '—') + ' · ' + (t ? t.titolo_tmdb : '') + ' · proposta ' + (pi + 1) + ' di ' + P.length + (pr.conf === 'bassa' ? ' · confidenza BASSA' : '') + (x.ck ? ' · ★' : '')));
      if (note) { main.appendChild(h('p', 'a3r-msg', note)); note = ''; }
      var st = refStyle({ scena: { w: x.w, h: x.h }, crop: x.crop }), pv = h('div', 'a3r-big'); pv.style.backgroundImage = 'url("' + TM + 'w780' + x.p + '")'; pv.style.backgroundSize = st.size; pv.style.backgroundPosition = st.pos; pv.setAttribute('role', 'img'); pv.setAttribute('aria-label', 'Anteprima della proposta ' + (pi + 1)); main.appendChild(pv);
      var r1 = h('div', 'a3r-row'); r1.appendChild(btn('a3r-b pri', '✓ Approva', function () { approva(id, inf, x); })); main.appendChild(r1);
      var r2 = h('div', 'a3r-row'), nx = btn('a3r-b', 'Altra proposta', function () { if (pi + 1 < P.length) { pi++; draw(id, inf, pr); } }); if (pi + 1 >= P.length) { nx.disabled = true; nx.textContent = 'Nessuna altra proposta'; } r2.appendChild(nx);
      r2.appendChild(btn('a3r-b', 'Salta', function () { skipped++; qi++; show(); })); r2.appendChild(btn('a3r-b', 'Editor', function () { openEditor(id, inf.nome || id, known); })); main.appendChild(r2);
      main.appendChild(h('p', 'a3r-fine', ATTR));
    }
    function approva(id, inf, x) {
      if (busy) return; busy = true;
      var t = inf.titoli.filter(function (y) { return y.num === x.num; })[0], scena = { p: x.p, w: x.w, h: x.h, tid: t ? t.tmdb_id : null, num: x.num }; if (x.rk) { scena.rk = x.rk; scena.sc = x.sc; }
      var base = { id: id, fonte: 'tmdb-scena', titolo: t ? t.titolo_tmdb : '', scena: scena, crop: { z: x.crop.z, cx: x.crop.cx, cy: x.crop.cy }, ts: Date.now(), v: 1 };
      Promise.all([getRec(id), all()]).then(function (a) {
        if (a[0]) { note = 'Ritratto già presente: non sovrascritto.'; qi++; show(); return null; }
        var dup = a[1].filter(function (r) { return r.id !== id && r.scena && r.scena.p === x.p; })[0];
        if (dup) { busy = false; var prm = propId(id); note = 'Questa scena è già usata per un’altra identità: scegli un’altra proposta.'; return prm.then(function (pr) { if (pi + 1 < pr.proposte.length) pi++; draw(id, inf, pr); }); }
        function fin(rec) { return getRec(id).then(function (again) { if (again) { note = 'Ritratto comparso nel frattempo: non sovrascritto.'; qi++; show(); return; } return putRec(rec).then(function () { saved++; qi++; show(); }); }); }
        return loadImg(TM + 'w1280' + x.p, true).then(function (im) { return cropBlob(im, base.crop); }).then(function (b) { base.kind = 'copy'; base.blob = b; base.mime = b.type; base.w = OUT_W; base.h = OUT_H; return fin(base); }).catch(function () { base.kind = 'ref'; return fin(base); });
      }).catch(function () { busy = false; note = 'Salvataggio non riuscito: riprova o salta.'; propId(id).then(function (pr) { draw(id, inf, pr); }); });
    }
  }

  /* ---------- gestione (elenco del pilota + esporta/importa) ---------- */
  function renderManager(host, known) {
    host.textContent = ''; var root = h('div', 'a3r-mgr'); host.appendChild(root);
    root.appendChild(h('p', 'a3r-info', 'Ritratti privati: restano solo su questo dispositivo (archivio separato dai backup e dalla sincronizzazione). Nessuna immagine protetta è nel repository, nello ZIP o sul sito.'));
    var st = h('p', 'a3r-info', 'Stato archivio…'); root.appendChild(st);
    Promise.all([ids(), persisted(), (W.navigator.storage && W.navigator.storage.estimate) ? W.navigator.storage.estimate().catch(function () { return null; }) : null]).then(function (a) {
      var n = Object.keys(a[0]).length, mb = a[2] && a[2].usage ? (a[2].usage / 1048576).toFixed(1) + ' MB usati dall’app · ' : '';
      st.textContent = n + ' ritratti · ' + mb + (USING_MEM ? 'ATTENZIONE: archivio non disponibile (navigazione privata?), i ritratti non verranno conservati.' : (a[1] === true ? 'archivio persistente' : 'archivio non ancora marcato persistente (si attiva al primo salvataggio)'));
    });
    var row = h('div', 'a3r-row'), res = h('p', 'a3r-msg'); res.hidden = true;
    row.appendChild(btn('a3r-b pri', 'Esporta ritratti', function () { downloadExport().then(function (n) { res.hidden = false; res.className = 'a3r-msg'; res.textContent = 'Esportati ' + n + ' ritratti.'; }, function () { res.hidden = false; res.className = 'a3r-msg bad'; res.textContent = 'Esportazione non riuscita.'; }); }));
    var ow = h('label', 'a3r-ck'); var cb = h('input', '', null, { type: 'checkbox' }); ow.appendChild(cb); ow.appendChild(D.createTextNode(' sovrascrivi quelli già presenti'));
    row.appendChild(btn('a3r-b', 'Importa da file', function () { var f = h('input', '', null, { type: 'file', accept: 'application/json,.json' }); f.addEventListener('change', function () { var file = f.files && f.files[0]; if (!file) return; file.text().then(function (t) { return importJson(t, { known: function (id) { return !!(known && known(id)); }, sovrascrivi: cb.checked }); }).then(function (r) { res.hidden = false; res.className = 'a3r-msg' + (r.errori.length && !r.importati ? ' bad' : ''); res.textContent = 'Importati ' + r.importati + ', saltati ' + r.saltati + (r.errori.length ? ' — ' + r.errori.slice(0, 3).join('; ') : '') + '.'; list(); }); }); f.click(); }));
    row.appendChild(btn('a3r-b', 'Esporta valutazioni (solo metadati)', function () { valutazioni().then(function (o) { downloadJson('tva-valutazioni-' + new Date().toISOString().slice(0, 10) + '.json', o); res.hidden = false; res.className = 'a3r-msg'; res.textContent = 'Valutazioni esportate: ' + o.totale + ' ritratti (' + o.da_proposta + ' da proposta, prima: ' + o.rk1 + ', entro la 3ª: ' + o.rk3 + '; ' + o.scene_manuali + ' scene manuali; ' + o.file_locali + ' da file locale).'; }); }));
    var rv = btn('a3r-b pri', 'Revisione rapida…', function () { revisione(known); }); row.appendChild(rv);
    root.appendChild(row); root.appendChild(ow); root.appendChild(res);
    var cnt = h('p', 'a3r-info a3r-cnt'); var sol = h('label', 'a3r-ck'); var cb2 = h('input', '', null, { type: 'checkbox' }); sol.appendChild(cb2); sol.appendChild(D.createTextNode(' solo identità senza ritratto')); cb2.addEventListener('change', function () { list(); }); root.appendChild(cnt); root.appendChild(sol);
    var lh = h('div', 'a3r-list'); root.appendChild(lh); root.appendChild(h('p', 'a3r-fine', ATTR));
    function list() {
      lh.textContent = ''; conteggio().then(function (c) { cnt.textContent = 'Completati ' + c.fatti + ' di ' + c.totale + ' · mancanti ' + c.mancanti; }); Promise.all([indice(), ids()]).then(function (z) {
        var arr = cb2.checked ? z[0].filter(function (i) { return !z[1][i]; }) : z[0];
        if (!arr.length) { lh.appendChild(h('p', 'a3r-info', 'Candidati non ancora disponibili.')); return; }
        arr.forEach(function (id) {
          var r = btn('a3r-item', null, null), th = h('span', 'a3r-mini'); r.appendChild(th); var t = h('span'), kn = known && known(id), nm = h('b', '', typeof kn === 'string' && kn ? kn : id.replace(/^id-/, '').replace(/-/g, ' ')); t.appendChild(nm); var s = h('span', 's', 'Verifica in corso…'); t.appendChild(s); r.appendChild(t);
          var nome = nm.textContent; r.addEventListener('click', function () { openEditor(id, nome, known); }); lh.appendChild(r);
          Promise.all([getRec(id), candId(id)]).then(function (a) { var rec = a[0], inf = a[1]; if (inf && inf.nome) { nome = inf.nome; nm.textContent = nome; } s.textContent = rec ? (rec.kind === 'copy' ? 'Copia privata' : 'Riferimento a scena') + (rec.titolo ? ' · ' + rec.titolo : '') : (inf ? inf.immagini.length + ' scene candidate · nessun ritratto' : 'nessuna scena candidata · nessun ritratto'); var n = rec && node(rec, false); if (n) th.appendChild(n); });
        });
      });
    }
    list(); WAIT.push(function () { /* aggiornamento dell'elenco alla modifica */ if (root.isConnected) list(); });
  }

  W.tvaRit = { conteggio: conteggio, revisione: revisione, valutazioni: valutazioni, paint: paint, ids: ids, get: getRec, put: putRec, del: delRec, all: all, openEditor: openEditor, renderManager: renderManager, exportAll: exportAll, importJson: importJson, refStyle: refStyle, clamp: clamp, cropBlob: cropBlob, persisted: persisted, usingMemory: function () { return USING_MEM; }, _v: 1 };
})();
