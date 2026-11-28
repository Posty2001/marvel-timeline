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
    if (d) { v.titolo = d.titolo; v.cornice = d.cornice; v.tema = d.tema; v.effetto = d.effetto; v.st = d.st; if (d.avatar === 'photo') { if (c.photo) v.avatar = { kind: 'photo', id: c.avatar.id }; } else v.avatar = { kind: 'preset', id: d.avatar }; }
    return v;
  }
  function modelOf(v, d) {
    var m = T.model(v), modo = d ? d.tmodo : S2.titolo.modo, tx = d ? d.ttesto : S2.titolo.testo;
    if (modo === 'personale' && tx) m.title = tx;   /* titolo personale: campo distinto dal rango ufficiale */
    return m;
  }

  /* ---------- stage: carta 3D + sfondo animato + controlli ---------- */
  var stage, side = 'front', draft = null, draftBase = null, rq = 0;
  function animMode() { var m = draft ? draft.anim : S2.anim; return m === 'auto' ? (T3.reduced() ? 'statico' : 'auto') : m; }
  function activeBg() { var id = draft ? draft.bg : S2.sfondoAnim; return id && C.isUnlocked(S2, id) ? id : null; }
  function buildStage() {
    var v = draftView(draft), m = modelOf(v, draft), box = $('t2Card'); if (!box) return;
    var w = box.clientWidth || 340, layout = w >= 520 ? 'wide' : 'compact', f, b;
    try { f = T3.render(m, v.st, v.id, layout, 't2f', 'front'); b = T3.render(m, v.st, v.id, layout, 't2b', 'back'); } catch (e) { return; }
    var key = f + '\u0001' + b + '\u0001' + activeBg() + '\u0001' + animMode() + '\u0001' + side; if (box.getAttribute('data-k') === key) return; box.setAttribute('data-k', key);
    var mode = animMode(), bg = activeBg(), rot = (draft ? draft.st.rot : T3.styleNow().rot) !== false && mode !== 'off' && !T3.reduced();
    stage.className = 't2-stage' + (mode === 'statico' ? ' t2-static' : '') + (mode === 'off' ? ' t2-noanim' : '') + (rot ? ' t2-rot' : '') + (side === 'back' ? ' t2-back' : '');
    box.textContent = '';
    if (bg && mode !== 'off') { var sc = el('div', 't2-scene'); sc.innerHTML = SC.scene(bg, 'a'); box.appendChild(sc); }
    var c3 = el('div', 't2-3d'), ff = el('div', 't2-face t2-front'), fb = el('div', 't2-face t2-bk'); ff.innerHTML = f; fb.innerHTML = b;
    if (bg && mode !== 'off') { var fx = el('div', 't2-fx'); fx.innerHTML = SC.scene(bg, 'b'); ff.appendChild(fx); }
    c3.appendChild(ff); c3.appendChild(fb); box.appendChild(c3);
    ff.setAttribute('aria-hidden', side === 'back' ? 'true' : 'false'); fb.setAttribute('aria-hidden', side === 'back' ? 'false' : 'true');
    var fl = $('t2Flip'); if (fl) fl.setAttribute('aria-pressed', side === 'back' ? 'true' : 'false');
  }
  function stageLater() { if (rq) return; rq = W.requestAnimationFrame(function () { rq = 0; buildStage(); renderVetrina(); }); }
  function flip() { side = side === 'back' ? 'front' : 'back'; var box = $('t2Card'); if (box) { box.removeAttribute('data-k'); } stageLater(); }
  function rotToggle(on) { var st = Object.assign({}, T3.styleNow(), { rot: !!on }); ID.styleSave(st); if (draft) draft.st.rot = !!on; var box = $('t2Card'); if (box) box.removeAttribute('data-k'); stageLater(); try { T.render(); } catch (e) {} }

  /* ---------- vetrina (6 slot) ---------- */
  var BADGES = function () { var out = []; Array.prototype.forEach.call(D.querySelectorAll('.badge-chip'), function (c) { var id = (c.id || '').replace(/^badge-/, ''); if (id) out.push({ id: id, name: c.getAttribute('data-name') || id, desc: c.getAttribute('data-desc') || '', got: c.classList.contains('badge-unlocked'), glyph: c.textContent.trim() }); }); return out; };
  function vet() { var lk = {}; try { lk = T.lookLoad(); } catch (e) {} return C.effVetrina(S2, lk.b); }
  function itemInfo(it) {
    if (!it) return null;
    if (it.t === 'badge') { var b = BADGES().filter(function (x) { return x.id === it.id; })[0]; return b ? { name: b.name, ok: b.got, html: '<svg viewBox="-24 -24 48 48" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" transform="scale(1.5)">' + A.glyph(b.id) + '</g></svg>' } : null; }
    if (it.t === 'emblema') { var n = +it.id.slice(1); return { name: 'Emblema · ' + (EM.names[n] || n), ok: true, html: EM.svg(n, { p: '#2a1519', s: '#e3c79b' }) }; }
    if (it.t === 'ricompensa') { var r = RW.catalog.filter(function (x) { return x.id === it.id; })[0]; return r ? { name: r.nome, ok: RW.isUnlocked(r.id), rar: r.rar, html: '' } : null; }
    return null;
  }
  function slotNode(it, i, onTap) {
    var inf = itemInfo(it), b = el('button', 't2-slot' + (inf ? ' on' : '')); b.type = 'button'; b.setAttribute('data-slot', i);
    if (inf && inf.ok) {
      b.setAttribute('aria-label', 'Slot ' + (i + 1) + ': ' + inf.name); b.title = inf.name;
      if (inf.html) b.appendChild(fromHtml(inf.html, 't2-slot-art')); else { var g = el('span', 't2-slot-rw r-' + (inf.rar || 'c'), '✦'); b.appendChild(g); }
    } else { b.setAttribute('aria-label', 'Slot ' + (i + 1) + ': vuoto, tocca per scegliere'); b.appendChild(ic('plus')); }
    b.addEventListener('click', function () { onTap(i); }); return b;
  }
  function renderVetrina() {
    var box = $('t2Vet'); if (!box) return; box.textContent = ''; var v = vet(), filled = v.filter(Boolean).length;
    var h = el('div', 't2-vet-h'); h.appendChild(el('b', '', 'Vetrina')); h.appendChild(el('span', 't2-dim', filled + '/' + C.SLOTS)); box.appendChild(h);
    var row = el('div', 't2-vet-row'); v.forEach(function (it, i) { row.appendChild(slotNode(it, i, slotSheet)); }); box.appendChild(row);
  }
  function setSlot(i, it) { var v = vet(); v[i] = it ? C.validItem(it) : null; var seen = {}; v = v.map(function (x) { if (!x) return null; var k = x.t + ':' + x.id; if (seen[k]) return null; seen[k] = 1; return x; }); S2.vetrina = v; saveS2(); renderVetrina(); renderPanel(); }
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
    var body = openSheet(kind === 'uni' ? 'Scegli un universo (TVA Atlas)' : 'Scegli un personaggio (TVA Atlas)'), inp = el('input', 't2-in'), list = el('div', 't2-pick t2-list'), msg = el('p', 't2-dim', 'Caricamento di TVA Atlas…');
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
    loadAtlas(function (ok) { if (!sheetEl) return; if (!ok) { msg.textContent = 'Dati di TVA Atlas non disponibili offline: puoi scrivere il nome a mano nei campi dell’identità.'; return; } msg.remove(); draw(); inp.addEventListener('input', draw); inp.focus(); });
  }

  /* ---------- sezioni ---------- */
  var SECS = [['tessera', 'Tessera'], ['carriera', 'Carriera'], ['atelier', 'Atelier'], ['collezione', 'Collezione'], ['identita', 'Identità']], sec = 'tessera', panel;
  function head(t, s) { var h = el('div', 't2-ph'); h.appendChild(el('h3', '', t)); if (s) h.appendChild(el('p', 't2-dim', s)); return h; }
  function card(title) { var c = el('section', 't2-card-p'); if (title) c.appendChild(el('h4', '', title)); return c; }
  function kv(box, k, v) { var r = el('div', 't2-kv'); r.appendChild(el('span', '', k)); r.appendChild(el('b', '', v)); box.appendChild(r); return r; }

  function secTessera(b) {
    var v = cur(), c = card();
    c.appendChild(el('div', 't2-eyebrow', 'AGENTE TVA')); c.appendChild(el('div', 't2-name', v.name || 'Variante'));
    var m = modelOf(draftView(null), null); c.appendChild(el('div', 't2-sub', m.title)); c.appendChild(el('div', 't2-varid', txt('tesseraId') || 'VAR-000000'));
    var r = el('div', 't2-two'); kv(r, 'Rango', txt('tesseraRank')); kv(r, 'Livello', 'LV ' + txt('tesseraLivello') + ' · ' + txt('tesseraXpTotale') + ' XP'); c.appendChild(r);
    b.appendChild(c);
    var act = el('div', 't2-row');
    act.appendChild(button('Personalizza', 't2-primary', function () { go('atelier'); }, 'atelier')); act.appendChild(button('Condividi', '', function () { try { T.share(side); } catch (e) {} }, 'share')); b.appendChild(act);
    b.appendChild(el('p', 't2-dim t2-note', 'Tocca uno slot della vetrina per sceglierne il contenuto: puoi lasciarne di vuoti, spostarli e cambiarli quando vuoi.'));
  }

  function secCarriera(b) {
    b.appendChild(head('Passaporto di carriera', 'Rango e livello sono due scale distinte, con le regole di sempre.'));
    var c = card(), row = el('div', 't2-pass'), lv = el('div', 't2-lv');
    var sub = txt('tesseraXpSub'), mm = sub.match(/(\d+)\s*\/\s*(\d+)/), frac = mm ? Math.min(1, (+mm[1]) / Math.max(1, +mm[2])) : 0, R = 34, L = 2 * Math.PI * R;
    lv.innerHTML = '<svg viewBox="0 0 84 84" aria-hidden="true"><circle cx="42" cy="42" r="' + R + '" fill="none" stroke="rgba(227,199,155,.2)" stroke-width="6"/><circle cx="42" cy="42" r="' + R + '" fill="none" stroke="#E3C79B" stroke-width="6" stroke-linecap="round" stroke-dasharray="' + (L * frac).toFixed(1) + ' ' + L.toFixed(1) + '" transform="rotate(-90 42 42)"/></svg>';
    var n = el('div', 't2-lv-n'); n.appendChild(el('small', '', 'Livello')); n.appendChild(el('b', '', txt('tesseraLivello') || '1')); lv.appendChild(n); row.appendChild(lv);
    var rk = el('div', 't2-rk'); rk.appendChild(el('small', '', 'Rango TVA')); rk.appendChild(el('b', '', txt('tesseraRank') || 'Recluta')); rk.appendChild(el('span', 't2-dim', 'Guida completata: ' + (txt('tesseraPct') || '0%'))); row.appendChild(rk);
    c.appendChild(row); kv(c, 'XP totale', (txt('tesseraXpTotale') || '0') + ' XP'); kv(c, 'Prossimo livello', sub); b.appendChild(c);
    var pr = card('Progressione'); var p = txt('tesseraProssimo'); if (p) pr.appendChild(el('p', '', p));
    var bar = el('div', 't2-bar'); var fill = el('i'); fill.style.width = Math.round(frac * 100) + '%'; bar.appendChild(fill); pr.appendChild(bar);
    var nx = C.BGS.filter(function (g) { return !C.isUnlocked(S2, g.id); }).map(function (g) { var r = C.evalCond(g.cond, snap()); return { g: g, r: r }; }).filter(function (x) { return !x.r.pend; }).sort(function (a, b2) { return (b2.r.have / b2.r.need) - (a.r.have / a.r.need); })[0];
    if (nx) pr.appendChild(el('p', 't2-dim', 'Prossimo sfondo: ' + nx.g.n + ' — ' + C.reqText(nx.g.cond) + ' (' + C.progText(nx.g.cond, nx.r) + ')'));
    b.appendChild(pr);
    var st = card('Statistiche di servizio');
    kv(st, 'Titoli visti', txt('tesseraTitoliAssoluti')); kv(st, 'Ore viste', txt('tesseraOre')); kv(st, 'Voto medio', txt('tesseraVoto')); kv(st, 'Serie consecutive (giorni)', txt('tesseraStreak'));
    kv(st, 'Universi visitati', txt('tesseraUniversi')); kv(st, 'Studi', txt('tesseraStudi')); kv(st, 'Distintivi', txt('tesseraBadges'));
    kv(st, 'Ricompense ottenute', RW.unlocked().length + ' / ' + RW.catalog.length);
    var ex = Object.keys(espNow()).length; var kx = kv(st, 'Dossier Atlas esplorati', String(ex)); if (atCounts) kv(st, 'di cui verificati', String(atCounts.dossier)); b.appendChild(st);
    var rc = card('Riconoscimenti ottenuti'), got = BADGES().filter(function (x) { return x.got; });
    if (!got.length) rc.appendChild(el('p', 't2-dim', 'Nessun distintivo ancora: i prossimi arrivano con la visione.')); else { var g = el('div', 't2-badges'); got.forEach(function (x) { var s = el('span', 't2-bd'); s.appendChild(fromHtml('<svg viewBox="-24 -24 48 48" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" transform="scale(1.5)">' + A.glyph(x.id) + '</g></svg>', 't2-bd-ic')); s.appendChild(el('span', '', x.name)); g.appendChild(s); }); rc.appendChild(g); }
    b.appendChild(rc);
    if (!atCounts) loadAtlas(function (ok) { if (ok && sec === 'carriera') renderPanel(); });
  }

  /* ---- Atelier ---- */
  var atTab = 'avatar';
  function ensureDraft() {
    if (draft) return; var c = cur(); draft = { avatar: c.avatar.kind === 'photo' ? 'photo' : c.avatar.id, titolo: c.titolo, cornice: c.cornice, tema: c.tema, effetto: c.effetto, st: clone(c.st || { v: 1 }), bg: S2.sfondoAnim, anim: S2.anim, tmodo: S2.titolo.modo, ttesto: S2.titolo.testo };
    draftBase = clone(draft);
  }
  function dirtyN() { if (!draft) return 0; var n = 0; ['avatar', 'titolo', 'cornice', 'tema', 'effetto', 'bg', 'anim', 'tmodo', 'ttesto'].forEach(function (k) { if (draft[k] !== draftBase[k]) n++; }); if (JSON.stringify(draft.st) !== JSON.stringify(draftBase.st)) n++; return n; }
  function dirtyUI() { var n = dirtyN(), s = $('t2Save'), t = $('t2State'); if (s) { s.textContent = n ? 'Salva · ' + n : 'Salva'; s.classList.toggle('t2-idle', !n); } if (t) { t.textContent = n ? '● Non salvato' : '✓ Salvato'; t.classList.toggle('dirty', !!n); } }
  function dchg() { var box = $('t2Card'); if (box) box.removeAttribute('data-k'); stageLater(); dirtyUI(); }
  function setSt(patch) { var o = Object.assign({}, draft.st); Object.keys(patch).forEach(function (k) { if (patch[k] === null) delete o[k]; else o[k] = patch[k]; }); if (patch.pr === undefined && Object.keys(patch).some(function (k) { return ['bg', 'tx', 'fr', 'fx', 'ic', 'ty', 'fi', 'pc', 'sc', 'dc', 'ac'].indexOf(k) >= 0; })) delete o.pr; draft.st = ID.styleSanitize(o); dchg(); }
  function discard() { draft = null; draftBase = null; var box = $('t2Card'); if (box) box.removeAttribute('data-k'); stageLater(); renderPanel(); }
  function saveDraft() {
    if (!draft) return; var c = cur(), bad = '';
    ['titolo', 'cornice', 'tema', 'effetto'].forEach(function (s) { if (draft[s] !== draftBase[s]) { var r = RW.equip(s, draft[s]); if (!r.ok) bad = s; } });
    if (bad) { toast('Impossibile salvare «' + bad + '»: non è sbloccato.'); return; }
    if (JSON.stringify(draft.st) !== JSON.stringify(draftBase.st)) { var o = Object.assign({}, draft.st); delete o.ts; var keep = Object.keys(o).filter(function (k) { return k !== 'v' && k !== 'rot'; }).length; if (!keep && o.rot === undefined) ID.styleReset(); else ID.styleSave(o); }
    if (draft.avatar !== draftBase.avatar) { var lk = T.lookLoad(); try { W.localStorage.setItem(T.keys.look, JSON.stringify(T.sanitizeLook({ v: 1, a: draft.avatar, b: lk.b, ts: Date.now() }))); D.dispatchEvent(new W.CustomEvent('tva:look', { detail: { saved: true } })); } catch (e) {} }
    if (draft.bg !== draftBase.bg) S2.sfondoAnim = draft.bg && C.isUnlocked(S2, draft.bg) ? draft.bg : null;
    S2.anim = draft.anim; S2.titolo.modo = draft.tmodo; S2.titolo.testo = C.validTitle(draft.ttesto); if (S2.titolo.modo === 'personale' && !S2.titolo.testo) S2.titolo.modo = 'ufficiale';
    S2 = C.sane(S2); saveS2(); draft = null; draftBase = null; try { T.render(); } catch (e) {} var box = $('t2Card'); if (box) box.removeAttribute('data-k'); toast('Salvato'); stageLater(); renderPanel();
  }
  function tile(sel, locked, label, thumbHtml, sub, fn) {
    var b = el('button', 't2-tile' + (sel ? ' sel' : '') + (locked ? ' lock' : '')); b.type = 'button'; b.setAttribute('aria-pressed', sel ? 'true' : 'false'); if (locked) b.setAttribute('aria-disabled', 'true');
    if (thumbHtml) b.appendChild(fromHtml(thumbHtml, 't2-tile-th')); b.appendChild(el('span', 't2-tile-n', label)); if (sub) b.appendChild(el('span', 't2-tile-s', sub)); if (locked) b.appendChild(ic('lock', 't2-lk')); b.addEventListener('click', fn); return b;
  }
  function rewardTiles(cat, wrap, msg) {
    var grid = el('div', 't2-grid');
    RW.catalog.filter(function (r) { return r.cat === cat; }).forEach(function (r, i) {
      var un = RW.isUnlocked(r.id), th = cat === 'titolo' ? '' : A.thumb(cat, r.id, 'q' + cat + i, { theme: draft.tema, frame: draft.cornice }), pg = RW.progress(r.id);
      var sub = un ? RW.rarities[r.rar] : RW.rarities[r.rar] + ' · ' + r.desc + (pg && !pg.ok && pg.tot > 1 ? ' (' + pg.cur + '/' + pg.tot + ')' : '');
      grid.appendChild(tile(draft[cat] === r.id, !un, r.nome, th, sub, function () { if (!un) { msg.textContent = 'Bloccata: ' + r.desc; return; } msg.textContent = ''; draft[cat] = r.id; if (cat === 'titolo') draft.tmodo = 'ufficiale'; dchg(); renderPanel(); }));
    });
    if (cat === 'effetto') grid.insertBefore(tile(draft.effetto === null, false, 'Nessun effetto', '', '', function () { draft.effetto = null; dchg(); renderPanel(); }), grid.firstChild);
    wrap.appendChild(grid);
  }
  function chipsFor(map, key, label, wrap, multi) {
    var f = el('div', 't2-fld'); f.appendChild(el('span', 't2-lab', label)); var row = el('div', 't2-chips');
    Object.keys(map).forEach(function (k) {
      var nm = Array.isArray(map[k]) ? map[k][0] : map[k], on = multi ? (draft.st.dc || []).indexOf(k) >= 0 : (draft.st[key] !== undefined ? draft.st[key] : T3.DEFAULTS[key]) === k;
      var c = el('button', 't2-chip' + (on ? ' on' : ''), nm); c.type = 'button'; c.setAttribute('aria-pressed', on ? 'true' : 'false');
      c.addEventListener('click', function () { if (multi) { var l = (draft.st.dc || []).slice(), i = l.indexOf(k); if (i >= 0) l.splice(i, 1); else if (l.length < 4) l.push(k); setSt({ dc: l.length ? l : null }); } else setSt(Object.fromEntries([[key, k]])); renderPanel(); });
      row.appendChild(c);
    }); f.appendChild(row); wrap.appendChild(f);
  }
  function secAtelier(b) {
    ensureDraft(); var msg = el('p', 't2-note t2-dim', ''); msg.setAttribute('role', 'status'); msg.setAttribute('aria-live', 'polite');
    var bar = el('div', 't2-atbar'); bar.appendChild(button('Annulla', 't2-ghost', discard));
    var mid = el('div', 't2-atmid'); mid.appendChild(el('b', '', 'Atelier')); var stt = el('small', '', ''); stt.id = 't2State'; stt.setAttribute('role', 'status'); mid.appendChild(stt); bar.appendChild(mid);
    var sv = button('Salva', 't2-primary', saveDraft); sv.id = 't2Save'; bar.appendChild(sv); b.appendChild(bar);
    var tabs = el('div', 't2-subtabs'); tabs.setAttribute('role', 'tablist');
    [['avatar', 'Avatar'], ['stile', 'Stile'], ['titolo', 'Titoli'], ['cornice', 'Cornici'], ['tema', 'Temi'], ['effetto', 'Effetti'], ['sfondo', 'Sfondi']].forEach(function (t) { var x = el('button', 't2-subtab' + (atTab === t[0] ? ' on' : ''), t[1]); x.type = 'button'; x.setAttribute('role', 'tab'); x.setAttribute('aria-selected', atTab === t[0] ? 'true' : 'false'); x.addEventListener('click', function () { atTab = t[0]; renderPanel(); }); tabs.appendChild(x); });
    b.appendChild(tabs); var body = el('div', 't2-atbody');
    if (atTab === 'avatar') {
      body.appendChild(el('p', 't2-dim t2-note', 'Otto avatar originali. La tua foto resta sul dispositivo (mai sincronizzata): per cambiarla apri l’editor completo.'));
      var g = el('div', 't2-grid t2-grid-av'); A.avatars.forEach(function (a, i) { g.appendChild(tile(draft.avatar === a.id, false, a.nome, A.avatarThumb({ avatar: { kind: 'preset', id: a.id } }, 'qa' + i), '', function () { draft.avatar = a.id; dchg(); renderPanel(); })); });
      if (cur().photo) g.appendChild(tile(draft.avatar === 'photo', false, 'La tua foto', A.avatarThumb({ avatar: { kind: 'photo', url: cur().photo } }, 'qap'), '', function () { draft.avatar = 'photo'; dchg(); renderPanel(); }));
      body.appendChild(g);
    } else if (atTab === 'stile') {
      body.appendChild(el('p', 't2-dim t2-note', 'I preset usano solo elementi liberi: non sbloccano né sostituiscono cornici, temi o effetti legati ai gradi.'));
      var pg = el('div', 't2-grid t2-grid-pr'); T3.PRESETS.forEach(function (p) { pg.appendChild(tile(draft.st.pr === p.id, false, p.name, '', '', function () { draft.st = T3.applyPreset(draft.st, p.id); dchg(); renderPanel(); })); }); body.appendChild(pg);
      chipsFor(T3.TYPO, 'ty', 'Carattere', body); chipsFor(T3.BGS, 'bg', 'Sfondo (statico)', body); chipsFor(T3.TEXS, 'tx', 'Texture', body); chipsFor(T3.FRS, 'fr', 'Cornice di stile', body); chipsFor(T3.DECS, 'dc', 'Decorazioni (fino a 4)', body, true); chipsFor(T3.FXS, 'fx', 'Effetto di stile', body); chipsFor(T3.ICS, 'ic', 'Codice', body); chipsFor(T3.LYS, 'ly', 'Layout', body);
      var fin = {}; EM.finishKeys.forEach(function (k) { fin[k] = k.charAt(0).toUpperCase() + k.slice(1); }); chipsFor(fin, 'fi', 'Finitura', body);
      [['pc', 'Colore primario'], ['sc', 'Colore secondario']].forEach(function (q) { var f = el('label', 't2-fld'); f.appendChild(el('span', 't2-lab', q[1])); var i = el('input'); i.type = 'color'; i.value = draft.st[q[0]] || T3.DEFAULTS[q[0]]; i.addEventListener('input', function () { setSt(Object.fromEntries([[q[0], i.value]])); }); f.appendChild(i); body.appendChild(f); });
      var rf = el('label', 't2-fld'), rl = el('span', 't2-lab', 'Intensità effetto ' + (draft.st.fxi !== undefined ? draft.st.fxi : T3.DEFAULTS.fxi) + '%'), ri = el('input'); ri.type = 'range'; ri.min = 0; ri.max = 100; ri.step = 5; ri.value = draft.st.fxi !== undefined ? draft.st.fxi : T3.DEFAULTS.fxi; ri.addEventListener('input', function () { rl.textContent = 'Intensità effetto ' + ri.value + '%'; setSt({ fxi: +ri.value }); }); rf.appendChild(rl); rf.appendChild(ri); body.appendChild(rf);
    } else if (atTab === 'titolo') {
      var pf = el('div', 't2-fld'); pf.appendChild(el('span', 't2-lab', 'Titolo personale (max ' + C.TITLE_MAX + ' caratteri) — distinto dal rango'));
      var ti = el('input', 't2-in'); ti.type = 'text'; ti.maxLength = C.TITLE_MAX; ti.value = draft.ttesto; ti.placeholder = 'Es. Guardiano delle Varianti'; var cnt = el('small', 't2-dim', Array.from(draft.ttesto).length + '/' + C.TITLE_MAX);
      ti.addEventListener('input', function () { draft.ttesto = C.validTitle(ti.value.slice(0, 80)); if (draft.ttesto) draft.tmodo = 'personale'; else draft.tmodo = 'ufficiale'; cnt.textContent = Array.from(draft.ttesto).length + '/' + C.TITLE_MAX; dchg(); });
      pf.appendChild(ti); pf.appendChild(cnt); var use = el('div', 't2-chips'); [['ufficiale', 'Usa un titolo ufficiale'], ['personale', 'Usa il titolo personale']].forEach(function (m) { var c = el('button', 't2-chip' + (draft.tmodo === m[0] ? ' on' : ''), m[1]); c.type = 'button'; c.setAttribute('aria-pressed', draft.tmodo === m[0] ? 'true' : 'false'); c.addEventListener('click', function () { if (m[0] === 'personale' && !draft.ttesto) { msg.textContent = 'Scrivi prima il titolo personale.'; return; } draft.tmodo = m[0]; dchg(); renderPanel(); }); use.appendChild(c); }); pf.appendChild(use); body.appendChild(pf);
      body.appendChild(el('h4', 't2-h4', 'Titoli ufficiali (ottenuti con la progressione)')); rewardTiles('titolo', body, msg);
    } else if (atTab === 'sfondo') {
      var sn = snap(); body.appendChild(el('h4', 't2-h4', 'Sfondi animati (12)'));
      var ag = el('div', 't2-grid t2-grid-bg'); C.BGS.forEach(function (bg) {
        var un = C.isUnlocked(S2, bg.id), r = C.evalCond(bg.cond, sn), th = '<span class="t2-bgth">' + (un ? SC.scene(bg.id, 'th' + bg.id.length) : '<span class="t2-bgph"></span>') + '</span>';
        ag.appendChild(tile(draft.bg === bg.id, !un, bg.n, th, un ? (C.isFree(bg) ? 'Disponibile' : 'Sbloccato') : C.reqText(bg.cond) + ' · ' + C.progText(bg.cond, r), function () { if (!un) { msg.textContent = C.reqText(bg.cond) + ' — ' + C.progText(bg.cond, r); if (r.pend) loadAtlas(function () { refreshUnlocks(); renderPanel(); }); return; } msg.textContent = ''; draft.bg = draft.bg === bg.id ? null : bg.id; dchg(); renderPanel(); }));
      }); body.appendChild(ag);
      body.appendChild(el('h4', 't2-h4', 'Animazioni')); var ar = el('div', 't2-chips'); [['auto', 'Automatiche'], ['statico', 'Statico'], ['off', 'Nessuno sfondo animato']].forEach(function (m) { var c = el('button', 't2-chip' + (draft.anim === m[0] ? ' on' : ''), m[1]); c.type = 'button'; c.setAttribute('aria-pressed', draft.anim === m[0] ? 'true' : 'false'); c.addEventListener('click', function () { draft.anim = m[0]; dchg(); renderPanel(); }); ar.appendChild(c); }); body.appendChild(ar);
      body.appendChild(el('p', 't2-dim t2-note', 'Le animazioni sono leggere e si fermano con «Statico» o con la riduzione del movimento del sistema. Gli sfondi si aggiungono a quelli statici dello stile.'));
      var sg = el('div', 't2-fld'); sg.appendChild(el('span', 't2-lab', 'Sfondi statici esistenti: scheda Stile → «Sfondo (statico)».')); body.appendChild(sg);
      if (sn.dossier === null || sn.uni === null) loadAtlas(function (ok) { if (ok) { var n0 = Object.keys(S2.sbloccati).length; refreshUnlocks(); if (Object.keys(S2.sbloccati).length !== n0 || atTab === 'sfondo') renderPanel(); } });
    } else { rewardTiles(atTab, body, msg); }
    b.appendChild(body); b.appendChild(msg);
    var ec = el('div', 't2-row'); ec.appendChild(button('Editor completo', 't2-ghost', function () { try { T.open(atTab === 'avatar' ? 'avatar' : atTab === 'stile' ? 'stile' : atTab === 'sfondo' ? 'stile' : atTab); } catch (e) {} })); b.appendChild(ec);
    dirtyUI();
  }

  /* ---- Collezione ---- */
  var colTab = 'emblemi', colF = { cat: 'tutte', rar: 'tutte', stato: 'tutti' }, colSel = null;
  function chipRow(opts, val, fn) { var row = el('div', 't2-chips'); opts.forEach(function (o) { var c = el('button', 't2-chip' + (val === o[0] ? ' on' : ''), o[1]); c.type = 'button'; c.setAttribute('aria-pressed', val === o[0] ? 'true' : 'false'); c.addEventListener('click', function () { fn(o[0]); }); row.appendChild(c); }); return row; }
  function detail(box, o) {
    var d = card(o.title); if (o.sub) d.appendChild(el('p', 't2-dim', o.sub)); if (o.desc) d.appendChild(el('p', '', o.desc)); if (o.req) d.appendChild(el('p', 't2-req', o.req));
    var row = el('div', 't2-row'); (o.acts || []).forEach(function (a) { row.appendChild(button(a[0], a[2] || '', a[1])); }); if (row.childNodes.length) d.appendChild(row); box.appendChild(d);
  }
  function addToVetrina(it) { return function () { var v = vet(), i = v.findIndex(function (x) { return x && x.t === it.t && x.id === it.id; }); if (i >= 0) { toast('È già nella vetrina'); return; } var e = v.findIndex(function (x) { return !x; }); if (e < 0) { toast('Vetrina piena: libera uno slot dalla scheda Tessera.'); return; } setSlot(e, it); toast('Aggiunto alla vetrina'); }; }
  function secCollezione(b) {
    b.appendChild(head('Collezione', 'Emblemi, ricompense, distintivi e sfondi: ottenuti e ancora da sbloccare.'));
    b.appendChild(chipRow([['emblemi', 'Emblemi (56)'], ['ricompense', 'Ricompense (' + RW.catalog.length + ')'], ['badge', 'Distintivi'], ['sfondi', 'Sfondi (12)']], colTab, function (t) { colTab = t; colSel = null; renderPanel(); }));
    var g = el('div', 't2-grid t2-grid-col'), det = el('div', 't2-det');
    if (colTab === 'emblemi') {
      b.appendChild(chipRow([['tutte', 'Tutte']].concat(EM.cats.map(function (c, i) { return [String(i), c]; })), colF.cat, function (v) { colF.cat = v; renderPanel(); }));
      var inUse = ID.get().emx;
      for (var n = 0; n < 56; n++) (function (n) {
        if (colF.cat !== 'tutte' && Math.floor(n / 8) !== +colF.cat) return;
        var t = tile(colSel === 'e' + n, false, EM.names[n] || ('Emblema ' + n), EM.svg(n, { p: '#2a1519', s: '#e3c79b' }), inUse === n ? 'In uso' : '', function () { colSel = 'e' + n; renderPanel(); }); g.appendChild(t);
      })(n);
      if (colSel && colSel[0] === 'e') { var k = +colSel.slice(1); detail(det, { title: EM.names[k], sub: 'Categoria: ' + EM.cats[Math.floor(k / 8)], acts: [[inUse === k ? 'In uso' : 'Usa come emblema', function () { ID.set({ emx: k }, { fromTessera: true }); try { T.render(); } catch (e) {} var bx = $('t2Card'); if (bx) bx.removeAttribute('data-k'); stageLater(); renderPanel(); }, 't2-primary'], ['Aggiungi alla vetrina', addToVetrina({ t: 'emblema', id: 'e' + k })]] }); }
    } else if (colTab === 'ricompense') {
      b.appendChild(chipRow([['tutte', 'Tutte'], ['titolo', 'Titoli'], ['cornice', 'Cornici'], ['tema', 'Temi'], ['effetto', 'Effetti']], colF.cat, function (v) { colF.cat = v; renderPanel(); }));
      b.appendChild(chipRow([['tutte', 'Tutte le rarità']].concat(Object.keys(RW.rarities).map(function (k) { return [k, RW.rarities[k]]; })), colF.rar, function (v) { colF.rar = v; renderPanel(); }));
      b.appendChild(chipRow([['tutti', 'Tutte'], ['ottenute', 'Ottenute'], ['bloccate', 'Da sbloccare']], colF.stato, function (v) { colF.stato = v; renderPanel(); }));
      var n2 = 0; RW.catalog.forEach(function (r, i) {
        if ((colF.cat !== 'tutte' && r.cat !== colF.cat) || (colF.rar !== 'tutte' && r.rar !== colF.rar)) return; var un = RW.isUnlocked(r.id); if ((colF.stato === 'ottenute' && !un) || (colF.stato === 'bloccate' && un)) return; n2++;
        g.appendChild(tile(colSel === r.id, !un, r.nome, r.cat === 'titolo' ? '' : A.thumb(r.cat, r.id, 'qc' + i, {}), RW.rarities[r.rar], function () { colSel = r.id; renderPanel(); }));
      });
      if (!n2) g.appendChild(el('p', 't2-dim', 'Nessuna ricompensa con questi filtri.'));
      var rr = colSel && RW.catalog.filter(function (x) { return x.id === colSel; })[0];
      if (rr) { var un2 = RW.isUnlocked(rr.id), pg2 = RW.progress(rr.id), eq = RW.equipped()[rr.cat] === rr.id; detail(det, { title: rr.nome, sub: RW.rarities[rr.rar] + ' · ' + ({ titolo: 'Titolo', cornice: 'Cornice', tema: 'Tema', effetto: 'Effetto' })[rr.cat], desc: rr.desc, req: un2 ? 'Ottenuta' : 'Da sbloccare' + (pg2 && pg2.tot > 1 ? ' (' + pg2.cur + '/' + pg2.tot + ')' : ''), acts: un2 ? [[eq ? 'Equipaggiata' : 'Equipaggia', function () { RW.equip(rr.cat, rr.id); try { T.render(); } catch (e) {} var bx = $('t2Card'); if (bx) bx.removeAttribute('data-k'); stageLater(); renderPanel(); }, 't2-primary'], ['Aggiungi alla vetrina', addToVetrina({ t: 'ricompensa', id: rr.id })]] : [] }); }
    } else if (colTab === 'badge') {
      BADGES().forEach(function (x) { var t = tile(colSel === x.id, !x.got, x.name, '<svg viewBox="-24 -24 48 48" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" transform="scale(1.5)">' + A.glyph(x.id) + '</g></svg>', x.got ? 'Ottenuto' : 'Da ottenere', function () { colSel = x.id; renderPanel(); }); g.appendChild(t); });
      var bb = colSel && BADGES().filter(function (x) { return x.id === colSel; })[0]; if (bb) detail(det, { title: bb.name, desc: bb.desc, req: bb.got ? 'Ottenuto' : 'Da ottenere', acts: bb.got ? [['Aggiungi alla vetrina', addToVetrina({ t: 'badge', id: bb.id })]] : [] });
    } else {
      var sn2 = snap(); C.BGS.forEach(function (bg) { var un = C.isUnlocked(S2, bg.id), r = C.evalCond(bg.cond, sn2); g.appendChild(tile(colSel === bg.id, !un, bg.n, '<span class="t2-bgth">' + (un ? SC.scene(bg.id, 'cc' + bg.id.length) : '<span class="t2-bgph"></span>') + '</span>', un ? (C.isFree(bg) ? 'Disponibile' : 'Sbloccato') : C.progText(bg.cond, r), function () { colSel = bg.id; renderPanel(); })); });
      var gg = colSel && C.BG_BY[colSel]; if (gg) { var un3 = C.isUnlocked(S2, gg.id), r3 = C.evalCond(gg.cond, sn2); detail(det, { title: gg.n, req: un3 ? (C.isFree(gg) ? 'Disponibile subito' : 'Sbloccato (permanente)') : C.reqText(gg.cond) + ' — ' + C.progText(gg.cond, r3), acts: un3 ? [['Usa come sfondo', function () { S2.sfondoAnim = gg.id; saveS2(); if (draft) draft.bg = gg.id; var bx = $('t2Card'); if (bx) bx.removeAttribute('data-k'); stageLater(); toast('Sfondo applicato'); renderPanel(); }, 't2-primary']] : [] }); }
      if (sn2.dossier === null) loadAtlas(function (ok) { if (ok) { refreshUnlocks(); if (sec === 'collezione' && colTab === 'sfondi') renderPanel(); } });
    }
    b.appendChild(g); b.appendChild(det);
  }

  /* ---- Identità ---- */
  function secIdentita(b) {
    b.appendChild(head('Passaporto Variante', 'La tua identità, condivisa con Tessera e (in futuro) con Friends: nessun profilo duplicato.'));
    var idt = ID.get(), c = card(); kv(c, 'VAR-ID', txt('tesseraId') || 'VAR-000000');
    var nf = el('label', 't2-fld'); nf.appendChild(el('span', 't2-lab', 'Nome')); var ni = el('input', 't2-in'); ni.type = 'text'; ni.maxLength = 20; ni.value = (cur().name || ''); ni.addEventListener('change', function () { var src = $('tesseraNameInput'); var val = C.validTitle(ni.value).slice(0, 20); if (src) { src.value = val; src.dispatchEvent(new W.Event('input', { bubbles: true })); } else { try { W.localStorage.setItem(P + 'user-name', val); } catch (e) {} } stageLater(); toast('Nome aggiornato'); }); nf.appendChild(ni); c.appendChild(nf);
    var mf = el('label', 't2-fld'); mf.appendChild(el('span', 't2-lab', 'Motto')); var mi = el('input', 't2-in'); mi.type = 'text'; mi.maxLength = 60; mi.value = idt.motto || ''; mi.addEventListener('change', function () { ID.set({ motto: C.validTitle(mi.value).slice(0, 60) }, { fromTessera: true }); var bx = $('t2Card'); if (bx) bx.removeAttribute('data-k'); stageLater(); toast('Motto salvato'); }); mf.appendChild(mi); c.appendChild(mf);
    function pickRow(label, val, kind, onPick, onClear) { var r = el('div', 't2-kv'); r.appendChild(el('span', '', label)); var bt = button(val || 'Scegli da TVA Atlas', 't2-ghost t2-pickbtn', function () { atlasPicker(kind, onPick); }); r.appendChild(bt); if (val) { var x = button('Rimuovi', 't2-ghost t2-x', onClear); x.setAttribute('aria-label', 'Rimuovi ' + label); r.appendChild(x); } c.appendChild(r); }
    pickRow('Universo di origine', S2.origine.univ, 'uni', function (v) { S2.origine = { univ: v.n.slice(0, 60), uid: v.i.slice(0, 48) }; saveS2(); renderPanel(); }, function () { S2.origine = { univ: '', uid: '' }; saveS2(); renderPanel(); });
    pickRow('Universo preferito', idt.univ, 'uni', function (v) { ID.set({ univ: v.n.slice(0, 60) }, { fromTessera: true }); S2.pref.univ = v.i; saveS2(); stageLater(); renderPanel(); }, function () { ID.set({ univ: '' }, { fromTessera: true }); S2.pref.univ = ''; saveS2(); stageLater(); renderPanel(); });
    pickRow('Personaggio preferito', idt.ch, 'ch', function (v) { ID.set({ ch: v.n.slice(0, 60) }, { fromTessera: true }); S2.pref.ch = v.i; saveS2(); stageLater(); renderPanel(); }, function () { ID.set({ ch: '' }, { fromTessera: true }); S2.pref.ch = ''; saveS2(); stageLater(); renderPanel(); });
    var m = modelOf(draftView(null), null); kv(c, 'Titolo', m.title + (S2.titolo.modo === 'personale' ? ' (personale)' : ' (ufficiale)')); b.appendChild(c);
    var inf = card('Impostazioni identità'), bi = {}; try { bi = ID.backupInfo(); } catch (e) {}
    kv(inf, 'Copia di sicurezza dell’identità', bi && bi.exists ? (bi.valid ? 'Presente e valida' : 'Presente, da verificare') : 'Non necessaria'); kv(inf, 'Foto personale', 'Solo su questo dispositivo');
    var vc = el('label', 't2-sw'); var cb = el('input'); cb.type = 'checkbox'; cb.checked = !!S2.classica; cb.addEventListener('change', function () { S2.classica = cb.checked; saveS2(); applyMode(); }); vc.appendChild(cb); vc.appendChild(el('span', '', 'Mostra la vista classica della Tessera')); inf.appendChild(vc); b.appendChild(inf);
    var pv = card('Privacy e condivisione'); pv.appendChild(el('p', 't2-dim', 'Predisposizione per la futura condivisione con il tuo partner (Friends 3.0). Oggi nulla viene condiviso o inviato: queste scelte restano sul dispositivo.'));
    var NAMES = { carta: 'Tessera (fronte e retro)', identita: 'VAR-ID e identità Variante', rango: 'Rango e livello', titolo: 'Titolo personale', preferiti: 'Universo e personaggio preferito', statistiche: 'Statistiche di carriera', emblemi: 'Emblemi e ricompense', vetrina: 'Vetrina personale' };
    C.CATEGORIES.forEach(function (k) { var r = el('label', 't2-sw'); var i = el('input'); i.type = 'checkbox'; i.checked = S2.privacy[k] === 'a'; i.addEventListener('change', function () { S2.privacy[k] = i.checked ? 'a' : 'p'; saveS2(); }); r.appendChild(i); r.appendChild(el('span', '', NAMES[k] + ' — ' + (i.checked ? 'condivisibile' : 'privato'))); i.addEventListener('change', function () { r.lastChild.textContent = NAMES[k] + ' — ' + (i.checked ? 'condivisibile' : 'privato'); }); pv.appendChild(r); });
    b.appendChild(pv);
  }

  /* ---------- struttura ---------- */
  function go(s) { sec = s; closeSheet(); renderTabs(); renderPanel(); if (panel && panel.scrollIntoView) { try { OV.scrollTo({ top: 0 }); } catch (e) { OV.scrollTop = 0; } } }
  function renderTabs() { var bar = $('t2Tabs'); if (!bar) return; Array.prototype.forEach.call(bar.children, function (b) { var on = b.getAttribute('data-s') === sec; b.classList.toggle('on', on); b.setAttribute('aria-selected', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; }); var r = $('t2Body'); if (r) r.setAttribute('data-sec', sec); }
  function renderPanel() {
    if (!panel) return; panel.textContent = ''; var b = el('div', 't2-sec'); panel.appendChild(b);
    try { ({ tessera: secTessera, carriera: secCarriera, atelier: secAtelier, collezione: secCollezione, identita: secIdentita })[sec](b); } catch (e) { b.appendChild(el('p', 't2-dim', 'Sezione momentaneamente non disponibile.')); if (W.console) W.console.error('Tessera TVA 3.0:', e); }
  }
  var origTitle = null;
  function applyMode() {
    var h2 = OV.querySelector('.mg-header h2'), sub = OV.querySelector('.mg-header .mg-sub');
    if (origTitle === null && h2) origTitle = [h2.innerHTML, sub ? sub.innerHTML : ''];
    var on = !S2.classica; OV.classList.toggle('t2-on', on);
    if (h2) { if (on) h2.textContent = 'La mia Tessera'; else if (origTitle) h2.innerHTML = origTitle[0]; }
    if (sub) { if (on) sub.textContent = 'La tua identità ufficiale negli Archivi Temporali.'; else if (origTitle) sub.innerHTML = origTitle[1]; }
    var back = $('t2Back'); if (!on) { if (!back) { var wrap = OV.querySelector('.tessera-wrap'); if (wrap) { var bb = button('Passa a «La mia Tessera»', 't2-primary t2-ret', function () { S2.classica = false; saveS2(); applyMode(); renderPanel(); }); bb.id = 't2Back'; wrap.parentNode.insertBefore(bb, wrap); } } } else if (back) back.remove();
    if (on) { stageLater(); renderPanel(); }
  }
  function build() {
    var root = el('div', 't2'); root.id = 't2Root';
    var tabs = el('div', 't2-tabs'); tabs.id = 't2Tabs'; tabs.setAttribute('role', 'tablist'); tabs.setAttribute('aria-label', 'Sezioni di La mia Tessera');
    SECS.forEach(function (s) { var t = el('button', 't2-tab'); t.type = 'button'; t.setAttribute('role', 'tab'); t.setAttribute('data-s', s[0]); t.appendChild(ic(s[0])); t.appendChild(el('span', '', s[1])); t.addEventListener('click', function () { go(s[0]); }); t.addEventListener('keydown', function (e) { var i = SECS.findIndex(function (x) { return x[0] === sec; }); if (e.key === 'ArrowRight') { go(SECS[(i + 1) % 5][0]); tabs.children[(i + 1) % 5].focus(); } else if (e.key === 'ArrowLeft') { go(SECS[(i + 4) % 5][0]); tabs.children[(i + 4) % 5].focus(); } }); tabs.appendChild(t); });
    root.appendChild(tabs);
    var body = el('div', 't2-body'); body.id = 't2Body'; stage = el('div', 't2-stage'); stage.id = 't2Stage';
    var cb = el('div', 't2-card'); cb.id = 't2Card'; stage.appendChild(cb);
    var ctr = el('div', 't2-ctr'); var fl = button('Gira la carta', 't2-ghost', flip, 'flip'); fl.id = 't2Flip'; fl.setAttribute('aria-pressed', 'false'); ctr.appendChild(fl);
    var rl = el('label', 't2-sw t2-rot'); var ri = el('input'); ri.type = 'checkbox'; ri.checked = T3.styleNow().rot !== false; ri.addEventListener('change', function () { rotToggle(ri.checked); }); rl.appendChild(ri); rl.appendChild(el('span', '', 'Rotazione 3D')); ctr.appendChild(rl); stage.appendChild(ctr);
    var vt = el('div', 't2-vet'); vt.id = 't2Vet'; stage.appendChild(vt); body.appendChild(stage); panel = el('div', 't2-panel'); panel.id = 't2Panel'; body.appendChild(panel); root.appendChild(body);
    var ts = el('div', 't2-toast'); ts.id = 't2Toast'; ts.setAttribute('role', 'status'); ts.setAttribute('aria-live', 'polite'); root.appendChild(ts);
    var h = OV.querySelector('.mg-header'); if (h && h.nextSibling) OV.insertBefore(root, h.nextSibling); else OV.appendChild(root);
    renderTabs();
  }
  var opened = false;
  function onOpen() {
    refreshUnlocks(); recompute(); if (!atCounts) loadAtlas(function (ok) { if (ok) { refreshUnlocks(); if (sec === 'atelier' || sec === 'collezione' || sec === 'carriera') renderPanel(); } });
    if (!S2.classica) { var box = $('t2Card'); if (box) box.removeAttribute('data-k'); stageLater(); renderPanel(); }
  }
  /* Rivalutazione quando i dati reali cambiano (retroattiva): XP/livello e progresso Timeline */
  var obs = 0; function watch() { var x = $('tesseraXpTotale'); if (x && W.MutationObserver) new W.MutationObserver(function () { W.clearTimeout(obs); obs = W.setTimeout(function () { refreshUnlocks(); }, 300); }).observe(x, { childList: true, characterData: true, subtree: true }); }
  D.addEventListener('visibilitychange', function () { if (stage) stage.classList.toggle('t2-paused', D.hidden); });
  W.addEventListener('resize', function () { if (OV.classList.contains('t2-on')) { var box = $('t2Card'); if (box) box.removeAttribute('data-k'); stageLater(); } });
  D.addEventListener('tva:look', function () { if (OV.classList.contains('t2-on') && !draft) { var box = $('t2Card'); if (box) box.removeAttribute('data-k'); stageLater(); renderPanel(); } });

  /* ---------- API pubblica e predisposizioni (nessuna rete, nessun XP) ---------- */
  function publicIdentity() {   /* contratto «identità condivisa v1» per Friends 3.0: solo ciò che l'utente ha marcato «condivisibile»; oggi non è inviato a nessuno */
    var p = S2.privacy, idt = ID.get(), o = { v: 1, legameNexus: 'nessuno' };
    if (p.identita === 'a') { o.varId = txt('tesseraId'); o.nome = cur().name; }
    if (p.rango === 'a') { o.rango = txt('tesseraRank'); o.livello = +txt('tesseraLivello') || 1; }
    if (p.titolo === 'a' && S2.titolo.modo === 'personale') o.titoloPersonale = S2.titolo.testo;
    if (p.preferiti === 'a') { o.universoPreferito = idt.univ; o.personaggioPreferito = idt.ch; }
    return o;
  }
  W.tvaT2 = { version: 1, core: C, state: function () { return clone(S2); }, snapshot: snap, refresh: onOpen, go: go, section: function () { return sec; }, publicIdentity: publicIdentity, loadAtlas: loadAtlas, atlasCounts: function () { return atCounts && clone(atCounts); }, draft: function () { return draft && clone(draft); } };
  if (!W.tvaTrophies) W.tvaTrophies = { v: 1, list: function () { return []; } };   /* predisposizione: Arcade, Quiz, Rankings (nessun dato oggi) */

  build(); watch(); applyMode(); onOpen();
})(window);
