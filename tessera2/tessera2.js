/* Tessera TVA 3.0 — «La mia Tessera»: modulo lazy e ADDITIVO (cinque sezioni: Tessera · Carriera · Atelier · Collezione · Identità).
   Non sostituisce nulla: la Tessera classica, l'editor «Personalizza», la condivisione e tutte le chiavi di salvataggio restano intatti (vista classica sempre raggiungibile).
   Dati nuovi SOLO in `tessera-v2` (v. core.js). Nessuna rete verso terzi; nessun XP; nessun HTML dai dati dell'utente (solo textContent). */
(function (W) {
  'use strict';
  var D = W.document, C = W.tvaT2Core, T = W.tvaTessera, T3 = W.tvaTessera3, RW = W.tvaRewards, ID = W.tvaIdentity, EM = W.tvaEmblems, A = W.tvaCardArt, SC = W.tvaT2Scenes;
  if (!C || !T || !T3 || !RW || !ID || !EM || !A || !SC || W.tvaT2) return;
  var OV = D.getElementById('tesseraOverlayEl'); if (!OV) return;
  var P = 'marvel-ultimate-timeline-';

  /* ---------- utilità ---------- */
  function el(tag, cls, txt) { var e = D.createElement(tag); if (cls) e.className = cls; if (txt !== undefined) e.textContent = txt; return e; }
  function $(id) { return D.getElementById(id); }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function today() { var d = new Date(), p = function (n) { return (n < 10 ? '0' : '') + n; }; return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()); }
  function txt(id) { var e = $(id); return e ? (e.textContent || '').trim() : ''; }
  var ICON = {
    tessera: '<rect x="3" y="5" width="18" height="14" rx="2.5"/><circle cx="9" cy="11" r="2.2"/><path d="M6 16c.6-1.6 2-2.4 3-2.4s2.4.8 3 2.4M14 10h4M14 13h3"/>',
    carriera: '<path d="M4 20V9M10 20V4M16 20v-8M22 20H2"/>',
    atelier: '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2.2"/><circle cx="8" cy="17" r="2.2"/>',
    collezione: '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9L12 3z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
    identita: '<circle cx="12" cy="8" r="3.6"/><path d="M5 20c.8-4 3.6-6 7-6s6.2 2 7 6"/>',
    lock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    plus: '<path d="M12 5v14M5 12h14"/>', left: '<path d="M15 5l-7 7 7 7"/>', right: '<path d="M9 5l7 7-7 7"/>', x: '<path d="M6 6l12 12M18 6L6 18"/>', check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    flip: '<path d="M4 12a8 8 0 0 1 14-5.3M20 4v4h-4M20 12a8 8 0 0 1-14 5.3M4 20v-4h4"/>', share: '<path d="M12 15V4M8 8l4-4 4 4M5 13v6h14v-6"/>'
  };
  function ic(n, cls) { var s = D.createElementNS('http://www.w3.org/2000/svg', 'svg'); s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('class', 't2-ic' + (cls ? ' ' + cls : '')); s.setAttribute('aria-hidden', 'true'); s.setAttribute('focusable', 'false'); s.innerHTML = ICON[n] || ''; return s; }
  function button(label, cls, fn, icon) { var b = el('button', 't2-btn ' + (cls || '')); b.type = 'button'; if (icon) b.appendChild(ic(icon)); b.appendChild(D.createTextNode(label)); if (fn) b.addEventListener('click', fn); return b; }
  function fromHtml(html, cls) { var s = el('span', cls || ''); s.innerHTML = html; return s; }   /* solo markup generato dall'app (miniature SVG), mai dati dell'utente */

  /* ---------- stato tessera-v2 ---------- */
  var S2 = loadS2();
  function loadS2() { try { return C.sane(JSON.parse(W.localStorage.getItem(C.KEY) || 'null')); } catch (e) { return C.defaults(); } }
  function saveS2() { S2.ts = Date.now(); try { W.localStorage.setItem(C.KEY, JSON.stringify(S2)); return true; } catch (e) { return false; } }

  /* ---------- dati reali (sola lettura) ---------- */
  var AT = null, atCounts = null, atWait = null;
  function espNow() { try { var s = JSON.parse(W.localStorage.getItem('tva-atlante-v2') || 'null'); return s && s.esp && typeof s.esp === 'object' ? s.esp : {}; } catch (e) { return {}; } }
  function jget(u) { return W.fetch(u, { credentials: 'same-origin' }).then(function (r) { if (!r.ok) throw new Error(u); return r.json(); }); }
  function loadAtlas(cb) {
    if (AT) return cb(true); if (atWait) { atWait.push(cb); return; } atWait = [cb];
    Promise.all([jget('atlante2/data/index.json'), jget('atlante2/data/db/stub.json').catch(function () { return null; }), jget('tessera2/data/regole.json').catch(function () { return { spiderman: [] }; })]).then(function (r) {
      var idx = r[0], st = r[1], BY = {}; idx.voci.forEach(function (v) { BY[v.i] = v; });
      if (st && st.r) st.r.forEach(function (x) { if (BY[x[0]]) return; BY[x[0]] = { i: x[0], n: x[1], t: x[2], k: 'i', u: x[3] && idx.meta.universi[x[3]] ? x[3] : '', s: 0, db: 1, lv: x[4], sv: x[7] || '' }; });
      AT = { BY: BY, red: idx.redirect || {}, spider: (r[2] && r[2].spiderman) || [], uni: idx.meta.universi || {} }; recompute(); var f = atWait; atWait = null; f.forEach(function (c) { c(true); });
    }).catch(function () { var f = atWait; atWait = null; f.forEach(function (c) { c(false); }); });
  }
  function recompute() { if (AT) atCounts = C.atlasCounts(espNow(), AT.BY, AT.red, AT.spider); }
  function snap() {
    var x = W.marvelXpInfo || {}, all = D.querySelectorAll('.watch-check'), done = D.querySelectorAll('.watch-check:checked').length;
    return { level: typeof x.livello === 'number' ? x.livello : null, pct: all.length ? Math.round(done / all.length * 100) : null, dossier: atCounts ? atCounts.dossier : null, uni: atCounts ? atCounts.uni : null, spider: atCounts ? atCounts.spider : null };
  }
  var toastT = 0;
  function toast(msg) { var t = $('t2Toast'); if (!t) return; t.textContent = msg; t.classList.add('on'); W.clearTimeout(toastT); toastT = W.setTimeout(function () { t.classList.remove('on'); }, 3800); }
  function refreshUnlocks() {   /* retroattivo e permanente: ogni apertura valuta i dati reali; ciò che si è sbloccato non si richiude */
    var r = C.evaluate(S2, snap(), today());
    if (r.newly.length) { S2 = r.state; saveS2(); r.newly.forEach(function (id) { toast('Sfondo sbloccato: ' + C.BG_BY[id].n); }); }
  }

  /* ---------- vista corrente della carta ---------- */
  function cur() { return T.current(); }
  function draftView(d) {
    var c = cur(), v = { name: c.name, avatar: c.avatar, badges: c.badges, titolo: c.titolo, cornice: c.cornice, tema: c.tema, effetto: c.effetto, photo: c.photo, st: c.st, id: c.id };
    if (d) {
      v.titolo = d.titolo; v.cornice = d.cornice; v.tema = d.tema; v.effetto = d.effetto; v.st = d.st; v.name = d.name; v.photo = d.photo; v.badges = d.badges;
      v.id = Object.assign({}, c.id, d.id);
      if (d.avatar === 'photo' && d.photo) v.avatar = { kind: 'photo', id: (c.avatar && c.avatar.id) || 'agente' }; else v.avatar = { kind: 'preset', id: d.avatar === 'photo' ? 'agente' : d.avatar };
    }
    return v;
  }
  function modelOf(v, d) {
    var m = T.model(v), modo = d ? d.tmodo : S2.titolo.modo, tx = d ? d.ttesto : S2.titolo.testo;
    if (modo === 'personale' && tx) m.title = tx;   /* titolo personale: campo distinto dal rango ufficiale */
    return m;
  }

  /* ---------- stage: carta 3D + sfondo animato + controlli ---------- */
  var stage, side = 'front', draft = null, draftBase = null, rq = 0, shim = null;
  function animMode() { var m = draft ? draft.anim : S2.anim; return m === 'auto' ? (T3.reduced() ? 'statico' : 'auto') : m; }
  function activeBg() { var id = draft ? draft.bg : S2.sfondoAnim; return id && C.isUnlocked(S2, id) ? id : null; }
  function tiltOn() { var st = draft ? draft.st : T3.styleNow(); return st.rot !== false && animMode() !== 'off' && !T3.reduced(); }
  function buildStage() {
    var v = draftView(draft), m = modelOf(v, draft), box = $('t2Card'); if (!box) return;
    var w = box.clientWidth || 340, layout = w >= 520 ? 'wide' : 'compact', f, b;
    try { f = T3.render(m, v.st, v.id, layout, 't2f', 'front'); b = T3.render(m, v.st, v.id, layout, 't2b', 'back'); } catch (e) { return; }
    var key = f + '\u0001' + b + '\u0001' + activeBg() + '\u0001' + animMode() + '\u0001' + side; if (box.getAttribute('data-k') === key) return; box.setAttribute('data-k', key);
    var mode = animMode(), bg = activeBg();
    stage.className = 't2-stage' + (mode === 'statico' ? ' t2-static' : '') + (mode === 'off' ? ' t2-noanim' : '') + (side === 'back' ? ' t2-back' : '');
    box.textContent = '';
    if (bg && mode !== 'off') { var sc = el('div', 't2-scene'); sc.innerHTML = SC.scene(bg, 'a'); box.appendChild(sc); }
    var c3 = el('div', 't2-3d'), ff = el('div', 't2-face t2-front'), fb = el('div', 't2-face t2-bk'); ff.innerHTML = f; fb.innerHTML = b;
    c3.appendChild(ff); c3.appendChild(fb); box.appendChild(c3);
    ff.setAttribute('aria-hidden', side === 'back' ? 'true' : 'false'); fb.setAttribute('aria-hidden', side === 'back' ? 'false' : 'true');
    var fl = $('t2Flip'); if (fl) fl.setAttribute('aria-pressed', side === 'back' ? 'true' : 'false');
    lastFront = f; var mn = $('t2Mini'); if (mn) mn.innerHTML = f;
  }
  var lastFront = '';
  function stageLater() { if (rq) return; rq = W.requestAnimationFrame(function () { rq = 0; buildStage(); renderVetrina(); }); }
  function reStage() { var box = $('t2Card'); if (box) box.removeAttribute('data-k'); stageLater(); }
  function flip() { side = side === 'back' ? 'front' : 'back'; reStage(); }
  /* Inclinazione 3D solo a contatto (dito/mouse): a riposo la carta resta piana e nitida su display Retina */
  function bindTilt(box) {
    if (box._tl) return; box._tl = 1; var down = null, moved = false;
    function c3() { return box.querySelector('.t2-3d'); }
    function tilt(e) { var c = c3(); if (!c || side !== 'front' || !tiltOn()) return; var r = box.getBoundingClientRect(); c.style.transform = 'rotateX(' + ((((e.clientY - r.top) / r.height) - .5) * -9).toFixed(1) + 'deg) rotateY(' + ((((e.clientX - r.left) / r.width) - .5) * 12).toFixed(1) + 'deg)'; }
    function rest() { var c = c3(); if (c) c.style.transform = ''; }
    box.addEventListener('pointerdown', function (e) { down = { x: e.clientX, y: e.clientY }; moved = false; tilt(e); });
    box.addEventListener('pointermove', function (e) { if (down && (Math.abs(e.clientX - down.x) > 6 || Math.abs(e.clientY - down.y) > 6)) moved = true; if (down || e.pointerType === 'mouse') tilt(e); });
    box.addEventListener('pointerup', function () { var tap = down && !moved; down = null; rest(); if (tap) flip(); });
    box.addEventListener('pointercancel', function () { down = null; rest(); }); box.addEventListener('pointerleave', function () { if (!down) rest(); });
    box.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); flip(); } });
  }
  function rotToggle(on) { var st = Object.assign({}, T3.styleNow(), { rot: !!on }); ID.styleSave(st); if (draft) draft.st.rot = !!on; reStage(); try { T.render(); } catch (e) {} }

  /* ---------- vetrina (6 slot) ---------- */
  var BADGES = function () { var out = []; Array.prototype.forEach.call(D.querySelectorAll('.badge-chip'), function (c) { var id = (c.id || '').replace(/^badge-/, ''); if (id) out.push({ id: id, name: c.getAttribute('data-name') || id, desc: c.getAttribute('data-desc') || '', got: c.classList.contains('badge-unlocked'), glyph: c.textContent.trim() }); }); return out; };
  var GLY = function (id) { return '<svg viewBox="-24 -24 48 48" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" transform="scale(1.5)">' + A.glyph(id) + '</g></svg>'; };
  function vet() { var lk = {}; try { lk = T.lookLoad(); } catch (e) {} return C.effVetrina(S2, lk.b); }
  function itemInfo(it) {
    if (!it) return null;
    if (it.t === 'badge') { var b = BADGES().filter(function (x) { return x.id === it.id; })[0]; return b ? { name: b.name, ok: b.got, html: GLY(b.id) } : null; }
    if (it.t === 'emblema') { var n = +it.id.slice(1); return { name: 'Emblema · ' + (EM.names[n] || n), ok: true, html: EM.svg(n, { p: '#2a1519', s: '#e3c79b' }) }; }
    if (it.t === 'ricompensa') { var r = RW.catalog.filter(function (x) { return x.id === it.id; })[0]; return r ? { name: r.nome, ok: RW.isUnlocked(r.id), rar: r.rar, html: '' } : null; }
    return null;
  }
  function slotNode(it, i, onTap) {
    var inf = itemInfo(it), b = el('button', 't2-slot' + (inf ? ' on' : '')); b.type = 'button'; b.setAttribute('data-slot', i);
    if (inf && inf.ok) {
      b.setAttribute('aria-label', 'Slot ' + (i + 1) + ': ' + inf.name); b.title = inf.name;
      if (inf.html) b.appendChild(fromHtml(inf.html, 't2-slot-art')); else b.appendChild(el('span', 't2-slot-rw r-' + (inf.rar || 'c'), '✦'));
    } else { b.setAttribute('aria-label', 'Slot ' + (i + 1) + ': vuoto, tocca per scegliere'); b.appendChild(ic('plus')); }
    b.addEventListener('click', function () { onTap(i); }); return b;
  }
  function renderVetrina() {
    var box = $('t2Vet'); if (!box) return; box.textContent = ''; var v = vet(), filled = v.filter(Boolean).length;
    var h = el('div', 't2-vet-h'); h.appendChild(el('b', '', 'Vetrina')); h.appendChild(el('span', 't2-dim', filled + '/' + C.SLOTS)); box.appendChild(h);
    var row = el('div', 't2-vet-row'); v.forEach(function (it, i) { row.appendChild(slotNode(it, i, slotSheet)); }); box.appendChild(row);
  }
  function setSlot(i, it) { var v = vet(); v[i] = it ? C.validItem(it) : null; var seen = {}; v = v.map(function (x) { if (!x) return null; var k = x.t + ':' + x.id; if (seen[k]) return null; seen[k] = 1; return x; }); S2.vetrina = v; saveS2(); renderVetrina(); if (sec !== 'atelier') renderPanel(); }
  function moveSlot(i, d) { var v = vet(), j = i + d; if (j < 0 || j >= v.length) return; var t = v[i]; v[i] = v[j]; v[j] = t; S2.vetrina = v; saveS2(); renderVetrina(); }

  /* ---------- finestre (sheet) ---------- */
  var sheetEl = null, sheetOpener = null;
  function closeSheet() { if (!sheetEl) return; sheetEl.remove(); sheetEl = null; var o = sheetOpener; sheetOpener = null; try { if (o && o.focus && D.contains(o)) o.focus(); } catch (e) {} }
  function openSheet(title) {
    closeSheet(); sheetOpener = D.activeElement;
    var back = el('div', 't2-sheet-back'), s = el('div', 't2-sheet'); s.setAttribute('role', 'dialog'); s.setAttribute('aria-modal', 'true'); s.setAttribute('aria-label', title);
    var h = el('div', 't2-sheet-h'); h.appendChild(el('b', '', title)); var x = button('Chiudi', 't2-ghost', closeSheet); h.appendChild(x); s.appendChild(h);
    var body = el('div', 't2-sheet-b'); s.appendChild(body); back.appendChild(s);
    back.addEventListener('click', function (e) { if (e.target === back) closeSheet(); }); s.addEventListener('keydown', function (e) { if (e.key === 'Escape') { e.stopPropagation(); closeSheet(); } });
    $('t2Root').appendChild(back); sheetEl = back; x.focus(); return body;
  }
  function slotSheet(i) {
    var v = vet(), it = v[i], body = openSheet('Slot ' + (i + 1) + ' della vetrina'), tab = 'badge';
    var bar = el('div', 't2-chips'), list = el('div', 't2-pick');
    function draw() {
      list.textContent = ''; Array.prototype.forEach.call(bar.children, function (c) { c.classList.toggle('on', c.getAttribute('data-t') === tab); c.setAttribute('aria-pressed', c.getAttribute('data-t') === tab ? 'true' : 'false'); });
      var items = [];
      if (tab === 'badge') BADGES().filter(function (b) { return b.got; }).forEach(function (b) { items.push({ t: 'badge', id: b.id }); });
      else if (tab === 'emblema') for (var n = 0; n < 56; n++) items.push({ t: 'emblema', id: 'e' + n });
      else RW.catalog.filter(function (r) { return RW.isUnlocked(r.id); }).forEach(function (r) { items.push({ t: 'ricompensa', id: r.id }); });
      if (!items.length) list.appendChild(el('p', 't2-dim', tab === 'badge' ? 'Non hai ancora ottenuto distintivi.' : 'Nessun elemento disponibile.'));
      items.forEach(function (q) {
        var inf = itemInfo(q); if (!inf) return; var b = el('button', 't2-pk'); b.type = 'button';
        if (inf.html) b.appendChild(fromHtml(inf.html, 't2-pk-art')); else b.appendChild(el('span', 't2-pk-art t2-slot-rw r-' + (inf.rar || 'c'), '✦'));
        b.appendChild(el('span', 't2-pk-n', inf.name)); b.addEventListener('click', function () { setSlot(i, q); closeSheet(); }); list.appendChild(b);
      });
    }
    [['badge', 'Distintivi'], ['emblema', 'Emblemi'], ['ricompensa', 'Ricompense']].forEach(function (t) { var c = el('button', 't2-chip', t[1]); c.type = 'button'; c.setAttribute('data-t', t[0]); c.addEventListener('click', function () { tab = t[0]; draw(); }); bar.appendChild(c); });
    body.appendChild(bar); body.appendChild(list);
    var act = el('div', 't2-row');
    act.appendChild(button('Sposta a sinistra', 't2-ghost', function () { moveSlot(i, -1); closeSheet(); }, 'left')); act.appendChild(button('Sposta a destra', 't2-ghost', function () { moveSlot(i, 1); closeSheet(); }, 'right'));
    if (it) act.appendChild(button('Svuota slot', 't2-ghost', function () { setSlot(i, null); closeSheet(); }, 'x'));
    body.appendChild(act); draw();
  }

  /* ---------- Atlas picker (universo / personaggio) ---------- */
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function atlasPicker(kind, onPick) {
    var body = openSheet(kind === 'uni' ? 'Scegli un universo' : 'Scegli un personaggio'), inp = el('input', 't2-in'), list = el('div', 't2-pick t2-list'), msg = el('p', 't2-dim', 'Apro TVA Atlas…');
    inp.type = 'search'; inp.placeholder = 'Cerca…'; inp.setAttribute('aria-label', 'Cerca'); inp.maxLength = 40; body.appendChild(inp); body.appendChild(msg); body.appendChild(list);
    function draw() {
      list.textContent = ''; var q = norm(inp.value.trim()), out = [];
      Object.keys(AT.BY).forEach(function (id) {
        var v = AT.BY[id]; if (out.length >= 60) return; if (!C.eligible(v)) return;
        if (kind === 'uni' ? v.t !== 'U' : !(v.t === 'p' && v.k === 'i')) return; if (q && norm(v.n).indexOf(q) < 0) return; out.push(v);
      });
      out.sort(function (a, b) { return a.n < b.n ? -1 : 1; });
      if (!out.length) list.appendChild(el('p', 't2-dim', 'Nessun risultato.'));
      out.forEach(function (v) { var b = el('button', 't2-pk t2-pk-row'); b.type = 'button'; b.appendChild(el('span', 't2-pk-n', v.n)); if (kind === 'ch' && v.u && AT.uni[v.u]) b.appendChild(el('span', 't2-dim', AT.uni[v.u].n)); b.addEventListener('click', function () { onPick(v); closeSheet(); }); list.appendChild(b); });
    }
    loadAtlas(function (ok) { if (!sheetEl) return; if (!ok) { msg.textContent = 'TVA Atlas non è raggiungibile offline: riprova più tardi.'; return; } msg.remove(); draw(); inp.addEventListener('input', draw); inp.focus(); });
  }

  /* ---------- sezioni ---------- */
  var SECS = [['tessera', 'Tessera'], ['carriera', 'Carriera'], ['atelier', 'Atelier'], ['collezione', 'Collezione'], ['identita', 'Identità']], sec = 'tessera', panel;
  function head(t, s) { var h = el('div', 't2-ph'); h.appendChild(el('h3', '', t)); if (s) h.appendChild(el('p', 't2-dim', s)); return h; }
  function card(title) { var c = el('section', 't2-card-p'); if (title) c.appendChild(el('h4', '', title)); return c; }
  function kv(box, k, v) { var r = el('div', 't2-kv'); r.appendChild(el('span', '', k)); r.appendChild(el('b', '', v)); box.appendChild(r); return r; }
  function num(id) { var m = txt(id).match(/\d+/); return m ? +m[0] : 0; }
  function xpParts() { var m = txt('tesseraXpSub').match(/(\d+)\s*\/\s*(\d+)/); return m ? { cur: +m[1], tot: +m[2] } : { cur: 0, tot: 100 }; }

  function secTessera(b) {
    var v = cur(), c = card('Riepilogo'), m = modelOf(draftView(null), null), xp = xpParts();
    var top = el('div', 't2-sum'); var l = el('div', 't2-sum-l'); l.appendChild(el('div', 't2-name', v.name || 'Variante')); l.appendChild(el('div', 't2-sub', m.title)); l.appendChild(el('div', 't2-varid', txt('tesseraId') || 'VAR-000000')); top.appendChild(l);
    var r = el('div', 't2-sum-r'); r.appendChild(el('small', '', 'Livello')); r.appendChild(el('b', '', txt('tesseraLivello') || '1')); top.appendChild(r); c.appendChild(top);
    var bar = el('div', 't2-bar'); var fill = el('i'); fill.style.width = Math.round(Math.min(1, xp.cur / Math.max(1, xp.tot)) * 100) + '%'; bar.appendChild(fill); c.appendChild(bar);
    var two = el('div', 't2-two'); kv(two, 'Rango TVA', txt('tesseraRank')); kv(two, 'Esperienza', (txt('tesseraXpTotale') || '0') + ' XP'); c.appendChild(two); b.appendChild(c);
    var nx = nextBg(); if (nx) { var n = card('Prossimo sfondo da sbloccare'); n.appendChild(el('p', '', nx.g.n)); n.appendChild(el('p', 't2-dim', C.reqText(nx.g.cond) + ' · ' + C.progText(nx.g.cond, nx.r))); b.appendChild(n); }
  }
  function nextBg() { return C.BGS.filter(function (g) { return !C.isUnlocked(S2, g.id); }).map(function (g) { return { g: g, r: C.evalCond(g.cond, snap()) }; }).filter(function (x) { return !x.r.pend; }).sort(function (a, b2) { return (b2.r.have / b2.r.need) - (a.r.have / a.r.need); })[0]; }

  function secCarriera(b) {
    var xp = xpParts(), frac = Math.min(1, xp.cur / Math.max(1, xp.tot)), R = 52, L = 2 * Math.PI * R, lvl = txt('tesseraLivello') || '1';
    var hero = el('section', 't2-hero');
    var lv = el('div', 't2-lv'); lv.innerHTML = '<svg viewBox="0 0 124 124" aria-hidden="true"><circle cx="62" cy="62" r="' + R + '" fill="none" stroke="rgba(227,199,155,.16)" stroke-width="8"/><circle cx="62" cy="62" r="' + R + '" fill="none" stroke="url(#t2lg)" stroke-width="8" stroke-linecap="round" stroke-dasharray="' + (L * frac).toFixed(1) + ' ' + L.toFixed(1) + '" transform="rotate(-90 62 62)"/><defs><linearGradient id="t2lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F59A23"/><stop offset="1" stop-color="#F6DCA8"/></linearGradient></defs></svg>';
    var n = el('div', 't2-lv-n'); n.appendChild(el('small', '', 'Livello')); n.appendChild(el('b', '', lvl)); lv.appendChild(n); hero.appendChild(lv);
    var rk = el('div', 't2-hero-r'); rk.appendChild(el('small', '', 'Il tuo rango')); rk.appendChild(el('b', 't2-rank', txt('tesseraRank') || 'Recluta')); rk.appendChild(el('span', 't2-xpbig', (txt('tesseraXpTotale') || '0') + ' XP'));
    rk.appendChild(el('span', 't2-dim', 'Ti mancano ' + Math.max(0, xp.tot - xp.cur) + ' XP per il livello ' + ((+lvl || 1) + 1) + '.')); hero.appendChild(rk); b.appendChild(hero);
    var bar = el('div', 't2-bar t2-bar-lg'); var fill = el('i'); fill.style.width = Math.round(frac * 100) + '%'; bar.appendChild(fill); b.appendChild(bar);
    var pr = card('Il cammino'); pr.appendChild(el('p', 't2-dim', 'Il rango racconta quanta parte della Sacra Linea Temporale hai percorso. Il livello cresce con ogni XP guadagnato: sono due strade diverse, e procedono in parallelo.'));
    kv(pr, 'Guida percorsa', txt('tesseraPct') || '0%'); var p = txt('tesseraProssimo'); if (p) pr.appendChild(el('p', 't2-next', p));
    var nx = nextBg(); if (nx) pr.appendChild(el('p', 't2-dim', 'Sulla strada verso lo sfondo «' + nx.g.n + '»: ' + C.reqText(nx.g.cond).toLowerCase() + ' (' + C.progText(nx.g.cond, nx.r) + ').')); b.appendChild(pr);
    var st = card('Registro di servizio'), g = el('div', 't2-stats');
    [['Titoli visti', txt('tesseraTitoliAssoluti')], ['Ore negli Archivi', txt('tesseraOre')], ['Voto medio', txt('tesseraVoto')], ['Giorni di fila', txt('tesseraStreak')], ['Universi visitati', txt('tesseraUniversi')], ['Studi esplorati', txt('tesseraStudi')], ['Distintivi', txt('tesseraBadges')], ['Ricompense', RW.unlocked().length + '/' + RW.catalog.length], ['Dossier Atlas', String(Object.keys(espNow()).length)]].forEach(function (x) { var t = el('div', 't2-stat'); t.appendChild(el('b', '', x[1] || '—')); t.appendChild(el('span', '', x[0])); g.appendChild(t); });
    st.appendChild(g); b.appendChild(st);
    var rc = card('Riconoscimenti'), got = BADGES().filter(function (x) { return x.got; });
    if (!got.length) rc.appendChild(el('p', 't2-dim', 'Nessun distintivo ancora: arriveranno con le tue visioni.')); else { var gb = el('div', 't2-badges'); got.forEach(function (x) { var s = el('span', 't2-bd'); s.appendChild(fromHtml(GLY(x.id), 't2-bd-ic')); s.appendChild(el('span', '', x.name)); gb.appendChild(s); }); rc.appendChild(gb); }
    b.appendChild(rc);
    if (!atCounts) loadAtlas(function (ok) { if (ok && sec === 'carriera') renderPanel(); });
  }

  /* ---- Atelier ---- */
  var atTab = 'avatar', DIRTY_KEYS = ['avatar', 'titolo', 'cornice', 'tema', 'effetto', 'bg', 'anim', 'tmodo', 'ttesto', 'name', 'photo'];
  function ensureDraft() {
    if (draft) return; var c = cur(), id0 = ID.get();
    draft = { avatar: c.avatar.kind === 'photo' ? 'photo' : c.avatar.id, titolo: c.titolo, cornice: c.cornice, tema: c.tema, effetto: c.effetto, st: clone(c.st || { v: 1 }), bg: S2.sfondoAnim, anim: S2.anim, tmodo: S2.titolo.modo, ttesto: S2.titolo.testo,
      name: c.name || '', photo: c.photo || null, badges: (c.badges || []).slice(0, 3), id: { emx: id0.emx, motto: id0.motto || '', univ: id0.univ || '', ch: id0.ch || '' } };
    draftBase = clone(draft); shim = { get draft() { return draft; }, undo: [], side: 'front', focusKey: '' };
  }
  function dirtyN() { if (!draft) return 0; var n = 0; DIRTY_KEYS.forEach(function (k) { if (draft[k] !== draftBase[k]) n++; }); ['st', 'badges', 'id'].forEach(function (k) { if (JSON.stringify(draft[k]) !== JSON.stringify(draftBase[k])) n++; }); return n; }
  function dirtyUI() { var n = dirtyN(), s = $('t2Save'), t = $('t2State'); if (s) { s.textContent = n ? 'Salva · ' + n : 'Salva'; s.classList.toggle('t2-idle', !n); } if (t) { t.textContent = n ? '● Modifiche non salvate' : '✓ Tutto salvato'; t.classList.toggle('dirty', !!n); } }
  function dchg() { reStage(); dirtyUI(); }
  function discard() { draft = null; draftBase = null; shim = null; reStage(); renderPanel(); }
  function setNameValue(val) { var src = $('tesseraNameInput'); if (src) { src.value = val; src.dispatchEvent(new W.Event('input', { bubbles: true })); } else { try { W.localStorage.setItem(P + 'user-name', val); } catch (e) {} } }
  function saveDraft() {
    if (!draft) return; var bad = '';
    ['titolo', 'cornice', 'tema', 'effetto'].forEach(function (s) { if (draft[s] !== draftBase[s]) { var r = RW.equip(s, draft[s]); if (!r.ok) bad = s; } });
    if (bad) { toast('Impossibile salvare «' + bad + '»: non è sbloccato.'); return; }
    if (draft.photo !== draftBase.photo) { try { if (draft.photo) W.localStorage.setItem(T.keys.photo, draft.photo); else W.localStorage.removeItem(T.keys.photo); } catch (e) { toast('Spazio insufficiente: la foto non è stata salvata. Nessuna modifica applicata.'); return; } }
    if (JSON.stringify(draft.st) !== JSON.stringify(draftBase.st)) { var o = Object.assign({}, draft.st); delete o.ts; var keep = Object.keys(o).filter(function (k) { return k !== 'v' && k !== 'rot'; }).length; if (!keep && o.rot === undefined) ID.styleReset(); else ID.styleSave(o); }
    var idp = {}; ['emx', 'motto', 'univ', 'ch'].forEach(function (k) { if (draft.id[k] !== draftBase.id[k]) idp[k] = draft.id[k]; }); if (Object.keys(idp).length) ID.set(idp, { fromTessera: true });
    if (draft.name !== draftBase.name) setNameValue(C.validTitle(draft.name).slice(0, 20));
    var av = draft.avatar === 'photo' && draft.photo ? 'photo' : (draft.avatar === 'photo' ? 'agente' : draft.avatar);
    if (draft.avatar !== draftBase.avatar || draft.photo !== draftBase.photo || JSON.stringify(draft.badges) !== JSON.stringify(draftBase.badges)) { var lk = T.lookLoad(); try { W.localStorage.setItem(T.keys.look, JSON.stringify(T.sanitizeLook({ v: 1, a: av, b: draft.badges.slice(0, 3), ts: Date.now() }))); D.dispatchEvent(new W.CustomEvent('tva:look', { detail: { saved: true } })); } catch (e) {} }
    if (draft.bg !== draftBase.bg) S2.sfondoAnim = draft.bg && C.isUnlocked(S2, draft.bg) ? draft.bg : null;
    S2.anim = draft.anim; S2.titolo.modo = draft.tmodo; S2.titolo.testo = C.validTitle(draft.ttesto); if (S2.titolo.modo === 'personale' && !S2.titolo.testo) S2.titolo.modo = 'ufficiale';
    S2 = C.sane(S2); saveS2(); draft = null; draftBase = null; shim = null; try { T.render(); } catch (e) {} toast('Salvato'); reStage(); renderPanel();
  }
  function tile(sel, locked, label, thumbHtml, sub, fn) {
    var b = el('button', 't2-tile' + (sel ? ' sel' : '') + (locked ? ' lock' : '')); b.type = 'button'; b.setAttribute('aria-pressed', sel ? 'true' : 'false'); if (locked) b.setAttribute('aria-disabled', 'true');
    if (thumbHtml) b.appendChild(fromHtml(thumbHtml, 't2-tile-th')); b.appendChild(el('span', 't2-tile-n', label)); if (sub) b.appendChild(el('span', 't2-tile-s', sub));
    if (locked) b.appendChild(ic('lock', 't2-lk')); else if (sel) b.appendChild(ic('check', 't2-ck')); b.addEventListener('click', fn); return b;
  }
  function rewardTiles(cat, wrap, msg) {
    var grid = el('div', 't2-grid');
    RW.catalog.filter(function (r) { return r.cat === cat; }).forEach(function (r, i) {
      var un = RW.isUnlocked(r.id), th = cat === 'titolo' ? '' : A.thumb(cat, r.id, 'q' + cat + i, { theme: draft.tema, frame: draft.cornice }), pg = RW.progress(r.id);
      var sub = un ? RW.rarities[r.rar] : RW.rarities[r.rar] + ' · ' + r.desc + (pg && !pg.ok && pg.tot > 1 ? ' (' + pg.cur + '/' + pg.tot + ')' : '');
      grid.appendChild(tile(draft[cat] === r.id, !un, r.nome, th, sub, function () { if (!un) { msg.textContent = 'Ancora bloccata: ' + r.desc; return; } msg.textContent = ''; draft[cat] = r.id; if (cat === 'titolo') draft.tmodo = 'ufficiale'; dchg(); renderPanel(); }));
    });
    if (cat === 'effetto') grid.insertBefore(tile(draft.effetto === null, false, 'Nessun effetto', '', '', function () { draft.effetto = null; dchg(); renderPanel(); }), grid.firstChild);
    wrap.appendChild(grid);
  }
  function startPhoto(file, dataUrl, msg) {
    var ok = T.photoFlow($('t2Root'), draft.avatar === 'photo' ? { kind: 'photo', id: 'agente' } : { kind: 'preset', id: draft.avatar }, file, dataUrl, function (dr, err) { if (dr && dr.photo) { draft.photo = dr.photo; draft.avatar = 'photo'; dchg(); renderPanel(); } else if (err) msg.textContent = err; });
    if (!ok) msg.textContent = 'Chiudi prima l’editor classico.';
  }
  function backupCard(body, msg) {
    var c = card('Copie di sicurezza'); body.appendChild(c); var info = {}; try { info = ID.backupInfo(); } catch (e) {}
    c.appendChild(el('p', 't2-dim', info && info.valid ? 'Esiste una copia verificata dei dati d’identità e Friends, creata prima dell’aggiornamento dell’identità. Conservane un file.' : 'Non serve nessuna copia: non c’erano dati da proteggere.'));
    if (info && info.valid) {
      var row = el('div', 't2-row');
      row.appendChild(button('Scarica copia', 't2-primary', function () { var t = ID.backupText(); if (!t) { msg.textContent = 'Copia non disponibile.'; return; } var a = D.createElement('a'); a.href = W.URL.createObjectURL(new W.Blob([t], { type: 'application/json' })); a.download = 'tva-backup-identita-' + today() + '.json'; D.body.appendChild(a); a.click(); a.remove(); W.setTimeout(function () { W.URL.revokeObjectURL(a.href); }, 4000); }, 'share'));
      var conf = el('div', 't2-conf'); conf.hidden = true; conf.appendChild(el('p', '', 'Il ripristino sostituisce i dati Friends e d’identità attuali con quelli della copia: ciò che è arrivato dopo andrà perso. Continuare?'));
      var cr = el('div', 't2-row'); cr.appendChild(button('Sì, ripristina', 't2-primary', function () { var r = ID.restoreFull(null); msg.textContent = r && r.ok ? 'Copia ripristinata.' : ((r && r.reason) || 'Ripristino non riuscito.'); conf.hidden = true; if (r && r.ok) { reStage(); } })); cr.appendChild(button('Annulla', 't2-ghost', function () { conf.hidden = true; })); conf.appendChild(cr);
      row.appendChild(button('Ripristina dalla copia…', 't2-ghost', function () { conf.hidden = false; })); c.appendChild(row); c.appendChild(conf);
    }
    if (ID.backupParse) {
      var f = el('label', 't2-fld'); f.appendChild(el('span', 't2-lab', 'Ripristina da un file di copia')); var fi = el('input'); fi.type = 'file'; fi.accept = 'application/json,.json'; fi.setAttribute('aria-label', 'Ripristina da file di copia');
      fi.addEventListener('change', function () { var fl = fi.files && fi.files[0]; if (!fl) return; if (fl.size > 6 * 1024 * 1024) { msg.textContent = 'File troppo grande.'; return; } var rd = new W.FileReader(); rd.onload = function () { var bk = ID.backupParse(String(rd.result)); fi.value = ''; if (!bk) { msg.textContent = 'File non valido: nessuna modifica.'; return; } var r = ID.restoreFull(bk); msg.textContent = r && r.ok ? 'Copia ripristinata dal file.' : ((r && r.reason) || 'Ripristino non riuscito.'); }; rd.readAsText(fl); });
      f.appendChild(fi); c.appendChild(f);
    }
    c.appendChild(el('p', 't2-dim', 'La foto personale resta solo su questo dispositivo e non è inclusa nelle copie.'));
  }
  var AT_CATS = [['avatar', 'Avatar'], ['stile', 'Stile'], ['titolo', 'Titoli'], ['cornice', 'Cornici'], ['tema', 'Temi'], ['effetto', 'Effetti'], ['sfondo', 'Sfondi'], ['dati', 'Copie']];
  function secAtelier(b) {
    ensureDraft(); var msg = el('p', 't2-note t2-dim', ''); msg.setAttribute('role', 'status'); msg.setAttribute('aria-live', 'polite');
    var bar = el('div', 't2-atbar'); bar.appendChild(button('Annulla', 't2-ghost', discard));
    var mid = el('div', 't2-atmid'); var mini = el('div', 't2-mini'); mini.id = 't2Mini'; mini.setAttribute('aria-hidden', 'true'); mini.innerHTML = lastFront; mid.appendChild(mini); var stt = el('small', '', ''); stt.id = 't2State'; stt.setAttribute('role', 'status'); mid.appendChild(stt); bar.appendChild(mid);
    var sv = button('Salva', 't2-primary', saveDraft); sv.id = 't2Save'; bar.appendChild(sv); b.appendChild(bar);
    var tabs = el('div', 't2-cats'); tabs.setAttribute('role', 'tablist');
    AT_CATS.forEach(function (t) { var x = el('button', 't2-cat' + (atTab === t[0] ? ' on' : ''), t[1]); x.type = 'button'; x.setAttribute('role', 'tab'); x.setAttribute('aria-selected', atTab === t[0] ? 'true' : 'false'); x.addEventListener('click', function () { atTab = t[0]; renderPanel(); }); tabs.appendChild(x); });
    b.appendChild(tabs); var cur_ = AT_CATS.filter(function (t) { return t[0] === atTab; })[0]; b.appendChild(el('h4', 't2-curcat', 'Stai modificando: ' + (cur_ ? cur_[1] : ''))); var body = el('div', 't2-atbody');
    if (atTab === 'avatar') {
      var nf = el('label', 't2-fld'); nf.appendChild(el('span', 't2-lab', 'Nome agente')); var ni = el('input', 't2-in'); ni.type = 'text'; ni.maxLength = 20; ni.value = draft.name; ni.placeholder = 'Il tuo nome…'; ni.addEventListener('input', function () { draft.name = ni.value.slice(0, 20); dchg(); }); nf.appendChild(ni); body.appendChild(nf);
      var g = el('div', 't2-grid t2-grid-av'); A.avatars.forEach(function (a, i) { g.appendChild(tile(draft.avatar === a.id, false, a.nome, A.avatarThumb({ avatar: { kind: 'preset', id: a.id } }, 'qa' + i), '', function () { draft.avatar = a.id; dchg(); renderPanel(); })); });
      if (draft.photo) g.appendChild(tile(draft.avatar === 'photo', false, 'La tua foto', A.avatarThumb({ avatar: { kind: 'photo', url: draft.photo } }, 'qap'), '', function () { draft.avatar = 'photo'; dchg(); renderPanel(); }));
      body.appendChild(g); body.appendChild(el('h4', 't2-h4', 'Foto personale'));
      var pr = el('div', 't2-row'), file = el('input'); file.type = 'file'; file.accept = 'image/*'; file.hidden = true; file.setAttribute('aria-label', 'Scegli una foto'); file.addEventListener('change', function () { if (file.files && file.files[0]) startPhoto(file.files[0], null, msg); });
      pr.appendChild(button(draft.photo ? 'Cambia foto' : 'Carica foto', 't2-primary', function () { file.value = ''; file.click(); })); pr.appendChild(file);
      if (draft.photo) { pr.appendChild(button('Modifica ritaglio', 't2-ghost', function () { startPhoto(null, draft.photo, msg); })); pr.appendChild(button('Rimuovi', 't2-ghost', function () { draft.photo = null; if (draft.avatar === 'photo') draft.avatar = 'agente'; msg.textContent = 'Foto rimossa (si applica al salvataggio).'; dchg(); renderPanel(); })); }
      body.appendChild(pr); body.appendChild(el('p', 't2-dim', 'La foto resta solo su questo dispositivo: non viene caricata online né sincronizzata, e non è inclusa nelle copie.'));
      var got = BADGES().filter(function (x) { return x.got; }); body.appendChild(el('h4', 't2-h4', 'Distintivi in evidenza · ' + draft.badges.length + '/3'));
      if (!got.length) body.appendChild(el('p', 't2-dim', 'Non hai ancora distintivi: appariranno qui appena ne otterrai uno.')); else { var bl = el('div', 't2-chips'); got.forEach(function (x) { var on = draft.badges.indexOf(x.id) >= 0, c = el('button', 't2-chip t2-chip-b' + (on ? ' on' : '')); c.type = 'button'; c.setAttribute('aria-pressed', on ? 'true' : 'false'); c.appendChild(fromHtml(GLY(x.id), 't2-chip-ic')); c.appendChild(D.createTextNode(x.name)); c.addEventListener('click', function () { var i = draft.badges.indexOf(x.id); if (i >= 0) draft.badges.splice(i, 1); else if (draft.badges.length >= 3) { msg.textContent = 'Puoi esporne al massimo tre: toglierne uno per sceglierne un altro.'; return; } else draft.badges.push(x.id); msg.textContent = ''; dchg(); renderPanel(); }); bl.appendChild(c); }); body.appendChild(bl); }
    } else if (atTab === 'stile') {
      T3.panel(body, shim, { el: el, flash: toast, refresh: function () { if (shim.side && shim.side !== side) side = shim.side; dchg(); renderPanel(); }, soft: function () { dchg(); } });
    } else if (atTab === 'titolo') {
      var pf = el('div', 't2-fld'); pf.appendChild(el('span', 't2-lab', 'Titolo personale (max ' + C.TITLE_MAX + ' caratteri) — distinto dal rango'));
      var ti = el('input', 't2-in'); ti.type = 'text'; ti.maxLength = C.TITLE_MAX; ti.value = draft.ttesto; ti.placeholder = 'Es. Guardiano delle Varianti'; var cnt = el('small', 't2-dim', Array.from(draft.ttesto).length + '/' + C.TITLE_MAX);
      ti.addEventListener('input', function () { draft.ttesto = C.validTitle(ti.value.slice(0, 80)); draft.tmodo = draft.ttesto ? 'personale' : 'ufficiale'; cnt.textContent = Array.from(draft.ttesto).length + '/' + C.TITLE_MAX; dchg(); });
      pf.appendChild(ti); pf.appendChild(cnt); var use = el('div', 't2-chips'); [['ufficiale', 'Usa un titolo ufficiale'], ['personale', 'Usa il titolo personale']].forEach(function (m) { var c = el('button', 't2-chip' + (draft.tmodo === m[0] ? ' on' : ''), m[1]); c.type = 'button'; c.setAttribute('aria-pressed', draft.tmodo === m[0] ? 'true' : 'false'); c.addEventListener('click', function () { if (m[0] === 'personale' && !draft.ttesto) { msg.textContent = 'Scrivi prima il titolo personale.'; return; } draft.tmodo = m[0]; dchg(); renderPanel(); }); use.appendChild(c); }); pf.appendChild(use); body.appendChild(pf);
      body.appendChild(el('h4', 't2-h4', 'Titoli ufficiali (ottenuti con la progressione)')); rewardTiles('titolo', body, msg);
    } else if (atTab === 'sfondo') {
      var sn = snap(); var ag = el('div', 't2-grid t2-grid-bg'); C.BGS.forEach(function (bg) {
        var un = C.isUnlocked(S2, bg.id), r = C.evalCond(bg.cond, sn), th = '<span class="t2-bgth' + (un ? '' : ' t2-bgl') + '">' + SC.scene(bg.id, 'th' + bg.id.length) + '</span>';
        ag.appendChild(tile(draft.bg === bg.id, !un, bg.n, th, un ? (C.isFree(bg) ? 'Disponibile' : 'Sbloccato') : C.reqText(bg.cond) + ' · ' + C.progText(bg.cond, r), function () { if (!un) { msg.textContent = C.reqText(bg.cond) + ' — ' + C.progText(bg.cond, r); if (r.pend) loadAtlas(function () { refreshUnlocks(); renderPanel(); }); return; } msg.textContent = ''; draft.bg = draft.bg === bg.id ? null : bg.id; dchg(); renderPanel(); }));
      }); body.appendChild(ag);
      body.appendChild(el('h4', 't2-h4', 'Animazioni')); var ar = el('div', 't2-chips'); [['auto', 'Automatiche'], ['statico', 'Statico'], ['off', 'Nessuno sfondo animato']].forEach(function (m) { var c = el('button', 't2-chip' + (draft.anim === m[0] ? ' on' : ''), m[1]); c.type = 'button'; c.setAttribute('aria-pressed', draft.anim === m[0] ? 'true' : 'false'); c.addEventListener('click', function () { draft.anim = m[0]; dchg(); renderPanel(); }); ar.appendChild(c); }); body.appendChild(ar);
      body.appendChild(el('p', 't2-dim t2-note', 'Gli sfondi animati si aggiungono a quelli statici dello stile (scheda Stile). Le animazioni sono leggere e si fermano con «Statico» o con la riduzione del movimento del sistema.'));
      if (sn.dossier === null || sn.uni === null) loadAtlas(function (ok) { if (ok) { var n0 = Object.keys(S2.sbloccati).length; refreshUnlocks(); if (Object.keys(S2.sbloccati).length !== n0 && atTab === 'sfondo' && sec === 'atelier') renderPanel(); } });
    } else if (atTab === 'dati') { backupCard(body, msg); }
    else rewardTiles(atTab, body, msg);
    b.appendChild(body); b.appendChild(msg);
    var ec = el('div', 't2-row'); ec.appendChild(button('Apri l’editor classico', 't2-ghost', function () { try { T.open(atTab === 'avatar' ? 'avatar' : atTab === 'stile' ? 'stile' : ['titolo', 'cornice', 'tema', 'effetto'].indexOf(atTab) >= 0 ? atTab : 'stile'); } catch (e) {} })); b.appendChild(ec);
    dirtyUI();
  }

  /* ---- Collezione ---- */
  var colTab = 'emblemi', colF = { cat: 'tutte', rar: 'tutte', stato: 'tutti' }, colSel = null;
  function select(label, opts, val, fn) { var s = el('select', 't2-sel'); s.setAttribute('aria-label', label); opts.forEach(function (o) { var op = el('option', '', o[1]); op.value = o[0]; if (val === o[0]) op.selected = true; s.appendChild(op); }); s.addEventListener('change', function () { fn(s.value); }); return s; }
  function detail(box, o) {
    var d = card(o.title); d.classList.add('t2-detc'); if (o.sub) d.appendChild(el('p', 't2-dim', o.sub)); if (o.desc) d.appendChild(el('p', '', o.desc)); if (o.req) d.appendChild(el('p', 't2-req', o.req));
    var row = el('div', 't2-row'); (o.acts || []).forEach(function (a) { row.appendChild(button(a[0], a[2] || '', a[1])); }); if (row.childNodes.length) d.appendChild(row); box.appendChild(d);
  }
  function addToVetrina(it) { return function () { var v = vet(), i = v.findIndex(function (x) { return x && x.t === it.t && x.id === it.id; }); if (i >= 0) { toast('È già nella vetrina'); return; } var e = v.findIndex(function (x) { return !x; }); if (e < 0) { toast('Vetrina piena: libera uno slot dalla scheda Tessera.'); return; } setSlot(e, it); toast('Aggiunto alla vetrina'); }; }
  function secCollezione(b) {
    var seg = el('div', 't2-seg'); [['emblemi', 'Emblemi'], ['ricompense', 'Ricompense'], ['badge', 'Distintivi'], ['sfondi', 'Sfondi']].forEach(function (t) { var x = el('button', 't2-segb' + (colTab === t[0] ? ' on' : ''), t[1]); x.type = 'button'; x.setAttribute('aria-pressed', colTab === t[0] ? 'true' : 'false'); x.addEventListener('click', function () { colTab = t[0]; colSel = null; renderPanel(); }); seg.appendChild(x); }); b.appendChild(seg);
    var g = el('div', 't2-grid t2-grid-col'), det = el('div', 't2-det'), fl = el('div', 't2-filters');
    if (colTab === 'emblemi') {
      var inUse = ID.get().emx; fl.appendChild(select('Categoria di emblemi', [['tutte', 'Tutte le categorie']].concat(EM.cats.map(function (c, i) { return [String(i), c]; })), colF.cat, function (v) { colF.cat = v; renderPanel(); })); b.appendChild(fl);
      for (var n = 0; n < 56; n++) (function (n) {
        if (colF.cat !== 'tutte' && Math.floor(n / 8) !== +colF.cat) return;
        g.appendChild(tile(colSel === 'e' + n, false, EM.names[n] || ('Emblema ' + n), EM.svg(n, { p: '#2a1519', s: '#e3c79b' }), inUse === n ? 'In uso' : '', function () { colSel = 'e' + n; renderPanel(); }));
      })(n);
      if (colSel && colSel[0] === 'e') { var k = +colSel.slice(1); detail(det, { title: EM.names[k], sub: 'Categoria: ' + EM.cats[Math.floor(k / 8)], acts: [[inUse === k ? 'In uso' : 'Usa come emblema', function () { ID.set({ emx: k }, { fromTessera: true }); try { T.render(); } catch (e) {} reStage(); renderPanel(); }, 't2-primary'], ['Aggiungi alla vetrina', addToVetrina({ t: 'emblema', id: 'e' + k })]] }); }
    } else if (colTab === 'ricompense') {
      fl.appendChild(select('Tipo di ricompensa', [['tutte', 'Tutti i tipi'], ['titolo', 'Titoli'], ['cornice', 'Cornici'], ['tema', 'Temi'], ['effetto', 'Effetti']], colF.cat, function (v) { colF.cat = v; renderPanel(); }));
      fl.appendChild(select('Rarità', [['tutte', 'Tutte le rarità']].concat(Object.keys(RW.rarities).map(function (k) { return [k, RW.rarities[k]]; })), colF.rar, function (v) { colF.rar = v; renderPanel(); }));
      fl.appendChild(select('Stato', [['tutti', 'Tutte'], ['ottenute', 'Ottenute'], ['bloccate', 'Da sbloccare']], colF.stato, function (v) { colF.stato = v; renderPanel(); })); b.appendChild(fl);
      var n2 = 0, got = 0; RW.catalog.forEach(function (r, i) {
        if ((colF.cat !== 'tutte' && r.cat !== colF.cat) || (colF.rar !== 'tutte' && r.rar !== colF.rar)) return; var un = RW.isUnlocked(r.id); if ((colF.stato === 'ottenute' && !un) || (colF.stato === 'bloccate' && un)) return; n2++; if (un) got++;
        g.appendChild(tile(colSel === r.id, !un, r.nome, r.cat === 'titolo' ? '' : A.thumb(r.cat, r.id, 'qc' + i, {}), RW.rarities[r.rar] + (un ? ' · ottenuta' : ''), function () { colSel = r.id; renderPanel(); }));
      });
      if (!n2) g.appendChild(el('p', 't2-dim', 'Nessuna ricompensa con questi filtri.'));
      var rr = colSel && RW.catalog.filter(function (x) { return x.id === colSel; })[0];
      if (rr) { var un2 = RW.isUnlocked(rr.id), pg2 = RW.progress(rr.id), eq = RW.equipped()[rr.cat] === rr.id; detail(det, { title: rr.nome, sub: RW.rarities[rr.rar] + ' · ' + ({ titolo: 'Titolo', cornice: 'Cornice', tema: 'Tema', effetto: 'Effetto' })[rr.cat], desc: rr.desc, req: un2 ? 'Ottenuta' : 'Da sbloccare' + (pg2 && pg2.tot > 1 ? ' (' + pg2.cur + '/' + pg2.tot + ')' : ''), acts: un2 ? [[eq ? 'Equipaggiata' : 'Equipaggia', function () { RW.equip(rr.cat, rr.id); try { T.render(); } catch (e) {} reStage(); renderPanel(); }, 't2-primary'], ['Aggiungi alla vetrina', addToVetrina({ t: 'ricompensa', id: rr.id })]] : [] }); }
    } else if (colTab === 'badge') {
      BADGES().forEach(function (x) { g.appendChild(tile(colSel === x.id, !x.got, x.name, GLY(x.id), x.got ? 'Ottenuto' : 'Da ottenere', function () { colSel = x.id; renderPanel(); })); });
      var bb = colSel && BADGES().filter(function (x) { return x.id === colSel; })[0]; if (bb) detail(det, { title: bb.name, desc: bb.desc, req: bb.got ? 'Ottenuto' : 'Da ottenere', acts: bb.got ? [['Aggiungi alla vetrina', addToVetrina({ t: 'badge', id: bb.id })]] : [] });
    } else {
      var sn2 = snap(); C.BGS.forEach(function (bg) { var un = C.isUnlocked(S2, bg.id), r = C.evalCond(bg.cond, sn2); g.appendChild(tile(colSel === bg.id, !un, bg.n, '<span class="t2-bgth' + (un ? '' : ' t2-bgl') + '">' + SC.scene(bg.id, 'cc' + bg.id.length) + '</span>', un ? (C.isFree(bg) ? 'Disponibile' : 'Sbloccato') : C.progText(bg.cond, r), function () { colSel = bg.id; renderPanel(); })); });
      var gg = colSel && C.BG_BY[colSel]; if (gg) { var un3 = C.isUnlocked(S2, gg.id), r3 = C.evalCond(gg.cond, sn2); detail(det, { title: gg.n, req: un3 ? (C.isFree(gg) ? 'Disponibile subito' : 'Sbloccato (permanente)') : C.reqText(gg.cond) + ' — ' + C.progText(gg.cond, r3), acts: un3 ? [['Usa come sfondo', function () { S2.sfondoAnim = gg.id; saveS2(); if (draft) draft.bg = gg.id; reStage(); toast('Sfondo applicato'); renderPanel(); }, 't2-primary']] : [] }); }
      if (sn2.dossier === null) loadAtlas(function (ok) { if (ok) { refreshUnlocks(); if (sec === 'collezione' && colTab === 'sfondi') renderPanel(); } });
    }
    b.appendChild(g); b.appendChild(det);
  }

  /* ---- Identità ---- */
  function secIdentita(b) {
    var idt = ID.get(), c = el('section', 't2-pass-card'), v = cur(), m = modelOf(draftView(null), null);
    var hd = el('div', 't2-pass-h'); hd.appendChild(el('span', '', 'PASSAPORTO VARIANTE')); hd.appendChild(el('span', '', 'TIME VARIANCE AUTHORITY')); c.appendChild(hd);
    var mid = el('div', 't2-pass-m'); var em = el('div', 't2-pass-em'); em.innerHTML = EM.svg(typeof idt.emx === 'number' ? idt.emx : 0, { p: '#2a1519', s: '#e3c79b' }); mid.appendChild(em);
    var tx = el('div', 't2-pass-t'); tx.appendChild(el('div', 't2-varid-lg', txt('tesseraId') || 'VAR-000000')); tx.appendChild(el('div', 't2-name', v.name || 'Variante')); tx.appendChild(el('div', 't2-sub', m.title)); if (idt.motto) tx.appendChild(el('div', 't2-motto', '«' + idt.motto + '»')); mid.appendChild(tx); c.appendChild(mid);
    function stamp(label, val, kind, onPick, onClear) { var r = el('div', 't2-stamp'); var bt = el('button', 't2-stamp-b'); bt.type = 'button'; bt.appendChild(el('small', '', label)); bt.appendChild(el('b', val ? '' : 't2-empty', val || 'Non ancora scelto')); bt.appendChild(ic('right', 't2-chev')); bt.setAttribute('aria-label', label + ': ' + (val || 'non ancora scelto') + '. Cambia'); bt.addEventListener('click', function () { atlasPicker(kind, onPick); }); r.appendChild(bt); if (val) { var x = button('Rimuovi', 't2-ghost t2-x', onClear); x.setAttribute('aria-label', 'Rimuovi ' + label); r.appendChild(x); } c.appendChild(r); }
    stamp('Universo di origine', S2.origine.univ, 'uni', function (q) { S2.origine = { univ: q.n.slice(0, 60), uid: q.i.slice(0, 48) }; saveS2(); renderPanel(); }, function () { S2.origine = { univ: '', uid: '' }; saveS2(); renderPanel(); });
    stamp('Universo preferito', idt.univ, 'uni', function (q) { ID.set({ univ: q.n.slice(0, 60) }, { fromTessera: true }); S2.pref.univ = q.i; saveS2(); reStage(); renderPanel(); }, function () { ID.set({ univ: '' }, { fromTessera: true }); S2.pref.univ = ''; saveS2(); reStage(); renderPanel(); });
    stamp('Personaggio preferito', idt.ch, 'ch', function (q) { ID.set({ ch: q.n.slice(0, 60) }, { fromTessera: true }); S2.pref.ch = q.i; saveS2(); reStage(); renderPanel(); }, function () { ID.set({ ch: '' }, { fromTessera: true }); S2.pref.ch = ''; saveS2(); reStage(); renderPanel(); });
    b.appendChild(c);
    var dt = el('details', 't2-det-x'); dt.appendChild(el('summary', '', 'Nome e motto'));
    var nf = el('label', 't2-fld'); nf.appendChild(el('span', 't2-lab', 'Nome')); var ni = el('input', 't2-in'); ni.type = 'text'; ni.maxLength = 20; ni.value = (cur().name || ''); ni.addEventListener('change', function () { setNameValue(C.validTitle(ni.value).slice(0, 20)); reStage(); renderPanel(); toast('Nome aggiornato'); }); nf.appendChild(ni); dt.appendChild(nf);
    var mf = el('label', 't2-fld'); mf.appendChild(el('span', 't2-lab', 'Motto')); var mi = el('input', 't2-in'); mi.type = 'text'; mi.maxLength = 60; mi.value = idt.motto || ''; mi.addEventListener('change', function () { ID.set({ motto: C.validTitle(mi.value).slice(0, 60) }, { fromTessera: true }); reStage(); renderPanel(); toast('Motto salvato'); }); mf.appendChild(mi); dt.appendChild(mf); b.appendChild(dt);
    var pv = card('Cosa può vedere un amico'); pv.appendChild(el('p', 't2-dim', 'Quando potrai condividere la tua Tessera con un amico, vedrà solo ciò che scegli qui. Per ora non viene condiviso nulla: queste scelte restano sul tuo dispositivo.'));
    var NAMES = { carta: 'La Tessera (fronte e retro)', identita: 'VAR-ID e nome', rango: 'Rango e livello', titolo: 'Titolo personale', preferiti: 'Universo e personaggio preferiti', statistiche: 'Registro di servizio', emblemi: 'Emblemi e ricompense', vetrina: 'La vetrina' };
    C.CATEGORIES.forEach(function (k) { var r = el('label', 't2-sw'); var i = el('input'); i.type = 'checkbox'; i.checked = S2.privacy[k] === 'a'; var lab = el('span', '', NAMES[k] + ' — ' + (i.checked ? 'visibile' : 'privato')); i.addEventListener('change', function () { S2.privacy[k] = i.checked ? 'a' : 'p'; saveS2(); lab.textContent = NAMES[k] + ' — ' + (i.checked ? 'visibile' : 'privato'); }); r.appendChild(i); r.appendChild(lab); pv.appendChild(r); });
    b.appendChild(pv);
    var al = el('details', 't2-det-x'); al.appendChild(el('summary', '', 'Altro')); var vc = el('label', 't2-sw'); var cb = el('input'); cb.type = 'checkbox'; cb.checked = !!S2.classica; cb.addEventListener('change', function () { S2.classica = cb.checked; saveS2(); applyMode(); }); vc.appendChild(cb); vc.appendChild(el('span', '', 'Mostra la vista classica della Tessera')); al.appendChild(vc); b.appendChild(al);
  }

  /* ---------- struttura ---------- */
  function go(s) { sec = s; closeSheet(); renderTabs(); renderPanel(); try { OV.scrollTo({ top: 0 }); } catch (e) { OV.scrollTop = 0; } }
  function renderTabs() { var bar = $('t2Tabs'); if (!bar) return; Array.prototype.forEach.call(bar.children, function (b) { var on = b.getAttribute('data-s') === sec; b.classList.toggle('on', on); b.setAttribute('aria-selected', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; }); var r = $('t2Body'); if (r) r.setAttribute('data-sec', sec); }
  function renderPanel() {
    if (!panel) return; var keep = OV.scrollTop; panel.textContent = ''; var b = el('div', 't2-sec'); panel.appendChild(b);
    try { ({ tessera: secTessera, carriera: secCarriera, atelier: secAtelier, collezione: secCollezione, identita: secIdentita })[sec](b); } catch (e) { b.appendChild(el('p', 't2-dim', 'Sezione momentaneamente non disponibile.')); if (W.console) W.console.error('Tessera TVA 3.0:', e); }
    if (sec !== 'tessera') { try { OV.scrollTop = keep; } catch (e) {} }
  }
  function applyMode() {
    var on = !S2.classica; OV.classList.toggle('t2-on', on);
    var back = $('t2Back'); if (!on) { if (!back) { var wrap = OV.querySelector('.tessera-wrap'); if (wrap) { var bb = button('Passa a «La mia Tessera»', 't2-primary t2-ret', function () { S2.classica = false; saveS2(); applyMode(); renderPanel(); }); bb.id = 't2Back'; wrap.parentNode.insertBefore(bb, wrap); } } } else if (back) back.remove();
    if (on) { stageLater(); renderPanel(); }
  }
  function build() {
    var root = el('div', 't2'); root.id = 't2Root';
    var top = el('div', 't2-top'); var bk = el('label', 't2-back'); bk.setAttribute('for', 'tesseraToggle'); bk.setAttribute('role', 'button'); bk.tabIndex = 0; bk.setAttribute('aria-label', 'Torna alla guida'); bk.appendChild(ic('left')); bk.appendChild(el('span', '', 'Guida'));
    bk.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); bk.click(); } }); top.appendChild(bk); top.appendChild(el('h2', 't2-title', 'La mia Tessera')); root.appendChild(top);
    var tabs = el('div', 't2-tabs'); tabs.id = 't2Tabs'; tabs.setAttribute('role', 'tablist'); tabs.setAttribute('aria-label', 'Sezioni di La mia Tessera');
    SECS.forEach(function (s) { var t = el('button', 't2-tab'); t.type = 'button'; t.setAttribute('role', 'tab'); t.setAttribute('data-s', s[0]); t.appendChild(ic(s[0])); t.appendChild(el('span', '', s[1])); t.addEventListener('click', function () { go(s[0]); }); t.addEventListener('keydown', function (e) { var i = SECS.findIndex(function (x) { return x[0] === sec; }); if (e.key === 'ArrowRight') { go(SECS[(i + 1) % 5][0]); tabs.children[(i + 1) % 5].focus(); } else if (e.key === 'ArrowLeft') { go(SECS[(i + 4) % 5][0]); tabs.children[(i + 4) % 5].focus(); } }); tabs.appendChild(t); });
    root.appendChild(tabs);
    var body = el('div', 't2-body'); body.id = 't2Body'; stage = el('div', 't2-stage'); stage.id = 't2Stage';
    var cb = el('div', 't2-card'); cb.id = 't2Card'; cb.tabIndex = 0; cb.setAttribute('role', 'button'); cb.setAttribute('aria-label', 'Tessera TVA: tocca per girare la carta'); stage.appendChild(cb); bindTilt(cb);
    var ctr = el('div', 't2-ctr'); var fl = button('Gira la carta', 't2-ghost', flip, 'flip'); fl.id = 't2Flip'; fl.setAttribute('aria-pressed', 'false'); ctr.appendChild(fl);
    var rl = el('label', 't2-sw t2-rot'); var ri = el('input'); ri.type = 'checkbox'; ri.checked = T3.styleNow().rot !== false; ri.addEventListener('change', function () { rotToggle(ri.checked); }); rl.appendChild(ri); rl.appendChild(el('span', '', 'Rotazione 3D')); ctr.appendChild(rl); stage.appendChild(ctr);
    var acts = el('div', 't2-acts'); acts.appendChild(button('Personalizza', 't2-primary', function () { go('atelier'); }, 'atelier')); acts.appendChild(button('Condividi', '', function () { try { T.share(side); } catch (e) {} }, 'share')); stage.appendChild(acts);
    var vt = el('div', 't2-vet'); vt.id = 't2Vet'; stage.appendChild(vt); body.appendChild(stage); panel = el('div', 't2-panel'); panel.id = 't2Panel'; body.appendChild(panel); root.appendChild(body);
    var ts = el('div', 't2-toast'); ts.id = 't2Toast'; ts.setAttribute('role', 'status'); ts.setAttribute('aria-live', 'polite'); root.appendChild(ts);
    var h = OV.querySelector('.mg-header'); if (h && h.nextSibling) OV.insertBefore(root, h.nextSibling); else OV.appendChild(root);
    renderTabs();
  }
  function onOpen() {
    refreshUnlocks(); recompute(); if (!atCounts) loadAtlas(function (ok) { if (ok) { refreshUnlocks(); if (sec === 'atelier' || sec === 'collezione' || sec === 'carriera' || sec === 'tessera') renderPanel(); } });
    if (!S2.classica) { reStage(); renderPanel(); }
  }
  var obs = 0; function watch() { var x = $('tesseraXpTotale'); if (x && W.MutationObserver) new W.MutationObserver(function () { W.clearTimeout(obs); obs = W.setTimeout(function () { refreshUnlocks(); }, 300); }).observe(x, { childList: true, characterData: true, subtree: true }); }
  D.addEventListener('visibilitychange', function () { if (stage) stage.classList.toggle('t2-paused', D.hidden); });
  W.addEventListener('resize', function () { if (OV.classList.contains('t2-on')) reStage(); });
  D.addEventListener('tva:look', function () { if (OV.classList.contains('t2-on') && !draft) { reStage(); renderPanel(); } });

  /* ---------- API pubblica e predisposizioni (nessuna rete, nessun XP) ---------- */
  function publicIdentity() {   /* contratto «identità condivisa v1»: solo ciò che l'utente ha marcato visibile; oggi non è inviato a nessuno */
    var p = S2.privacy, idt = ID.get(), o = { v: 1, legameNexus: 'nessuno' };
    if (p.identita === 'a') { o.varId = txt('tesseraId'); o.nome = cur().name; }
    if (p.rango === 'a') { o.rango = txt('tesseraRank'); o.livello = +txt('tesseraLivello') || 1; }
    if (p.titolo === 'a' && S2.titolo.modo === 'personale') o.titoloPersonale = S2.titolo.testo;
    if (p.preferiti === 'a') { o.universoPreferito = idt.univ; o.personaggioPreferito = idt.ch; }
    return o;
  }
  W.tvaT2 = { version: 2, core: C, state: function () { return clone(S2); }, snapshot: snap, refresh: onOpen, go: go, section: function () { return sec; }, publicIdentity: publicIdentity, loadAtlas: loadAtlas, atlasCounts: function () { return atCounts && clone(atCounts); }, draft: function () { return draft && clone(draft); } };
  if (!W.tvaTrophies) W.tvaTrophies = { v: 1, list: function () { return []; } };

  build(); watch(); applyMode(); onOpen();
})(window);
