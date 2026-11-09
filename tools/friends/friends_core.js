/* TVA Friends — nucleo: archivio locale, codec dei messaggi, regole di ricezione, generatore di quiz. Nessun accesso a profilo, note, voti, progressi (solo LETTURA del conteggio titoli visti, su azione esplicita). */
var KEY = 'marvel-ultimate-timeline-tvafriends-v1';
var CLOUD_ENABLED = false;            /* costante di build: il cloud resta DISATTIVATO finche' le regole Firebase non sono verificate */
var MAXCODE = 24000, INV_TTL = 14 * 864e5;
var EMBLEMS = ['🛡️', '⚡', '🕷️', '🔨', '🌀', '🪐', '🧬', '⏳', '🔮', '🦅', '🐆', '⭐'];
var COLORS = ['#c22528', '#2a5c7a', '#3e6b4f', '#6a3d9a', '#c8600c', '#a9791e'];
var VID_RE = /^v[a-z0-9]{8,12}$/, ID_RE = /^[a-z]{1,3}_[a-z0-9]{8,16}$/;
var TYPES = { 'nx.invite': 1, 'nx.accept': 1, 'nx.unlink': 1, 'team.invite': 1, 'team.join': 1, 'team.state': 1, 'ev.invite': 1, 'ev.rsvp': 1, 'ev.cancel': 1, 'duel.challenge': 1, 'duel.result': 1, 'share.pkg': 1 };

var CTRL_RE = new RegExp('[' + String.fromCharCode(0) + '-' + String.fromCharCode(31) + String.fromCharCode(127) + String.fromCharCode(0x2028) + String.fromCharCode(0x2029) + String.fromCharCode(0x202a) + '-' + String.fromCharCode(0x202e) + String.fromCharCode(0x2066) + '-' + String.fromCharCode(0x2069) + ']', 'g');
function now() { return Date.now(); }
function rid(p, n) {
  var s = '', b = new Uint8Array(n || 10);
  try { crypto.getRandomValues(b); } catch (e) { for (var i = 0; i < b.length; i++) b[i] = Math.floor(Math.random() * 256); }
  for (var j = 0; j < b.length; j++) s += (b[j] % 36).toString(36);
  return p + s;
}
function clean(s, max) { return typeof s === 'string' ? s.replace(CTRL_RE, ' ').replace(/\s+/g, ' ').trim().slice(0, max) : ''; }
function isObj(o) { return o !== null && typeof o === 'object' && !Array.isArray(o); }
function own(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
function fnv(str) { var h = 2166136261; for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } return ('00000000' + h.toString(16)).slice(-8); }

/* ---------- archivio locale ---------- */
function emptyStore() {
  return { v: 1, vid: null, me: { name: '', emblem: 0, color: 0, motto: '', univ: '', ch: '', share: { emblem: true, motto: false, univ: false, ch: false, tid: true } },
    nexus: {}, pendingOut: {}, reqs: {}, teams: {}, evenings: {}, duels: {}, shared: { out: {}, inn: {} }, inbox: [], seen: {}, best: { solo: 0, n: 0 } };
}
function num(v, lo, hi, d) { return typeof v === 'number' && isFinite(v) && v >= lo && v <= hi ? Math.floor(v) : d; }
function eachKey(m, re, fn, max) { if (!isObj(m)) return; var n = 0; Object.keys(m).forEach(function (k) { if (n < max && re.test(k) && isObj(m[k])) { fn(k, m[k]); n++; } }); }
function nIdx(v, len) { return (typeof v === 'number' && v >= 0 && v < len) ? Math.floor(v) : 0; }
function nCard(c) { return cleanCard(c); }
function nTeam(t) { return { id: t.id, name: clean(t.name, 30), emblem: nIdx(t.emblem, EMBLEMS.length), goal: num(t.goal, 5, 1000, 50), owner: t.owner }; }
function normStore(o) {
  var s = emptyStore();
  if (!isObj(o) || o.v !== 1) return s;
  if (typeof o.vid === 'string' && VID_RE.test(o.vid)) s.vid = o.vid;
  if (isObj(o.me)) {
    s.me.name = clean(o.me.name, 20); s.me.motto = clean(o.me.motto, 60); s.me.univ = clean(o.me.univ, 60); s.me.ch = clean(o.me.ch, 60);
    s.me.emblem = nIdx(o.me.emblem, EMBLEMS.length); s.me.color = nIdx(o.me.color, COLORS.length);
    if (isObj(o.me.share)) Object.keys(s.me.share).forEach(function (k) { if (typeof o.me.share[k] === 'boolean') s.me.share[k] = o.me.share[k]; });
  }
  eachKey(o.nexus, VID_RE, function (k, n) { if (n.status !== 'linked' && n.status !== 'blocked') return; s.nexus[k] = { vid: k, name: clean(n.name, 20) || 'Variante', emblem: nIdx(n.emblem, EMBLEMS.length), color: nIdx(n.color, COLORS.length), motto: clean(n.motto, 60), since: num(n.since, 0, 4e12, 0), status: n.status }; }, 500);
  eachKey(o.pendingOut, /^[a-z0-9]{16}$/, function (k, n) { s.pendingOut[k] = { ts: num(n.ts, 0, 4e12, 0) }; }, 100);
  eachKey(o.reqs, ID_RE, function (k, r) {
    var f = nCard(r.from); if (!f || (r.kind !== 'nx.invite' && r.kind !== 'team.invite')) return;
    var q = { kind: r.kind, from: f, ts: num(r.ts, 0, 4e12, 0) };
    if (r.kind === 'nx.invite') { if (typeof r.nonce !== 'string' || !/^[a-z0-9]{16}$/.test(r.nonce)) return; q.nonce = r.nonce; }
    else { if (!isObj(r.team) || !ID_RE.test(r.team.id || '') || !VID_RE.test(r.team.owner || '')) return; q.team = nTeam(r.team); }
    s.reqs[k] = q;
  }, 200);
  eachKey(o.teams, ID_RE, function (k, t) {
    if (!VID_RE.test(t.owner || '') || t.id !== k) return; var T = nTeam(t); T.created = num(t.created, 0, 4e12, 0); T.members = {}; T.log = [];
    eachKey(t.members, VID_RE, function (v, m) { T.members[v] = { name: clean(m.name, 20) || 'Variante', seen: m.seen === null ? null : num(m.seen, 0, 1000, null), ts: num(m.ts, 0, 4e12, 0) }; }, 100);
    if (Array.isArray(t.log)) t.log.slice(-30).forEach(function (l) { if (isObj(l)) T.log.push({ ts: num(l.ts, 0, 4e12, 0), text: clean(l.text, 120) }); });
    s.teams[k] = T;
  }, 100);
  eachKey(o.evenings, ID_RE, function (k, e) {
    if (e.id !== k || !VID_RE.test(e.host || '') || typeof e.when !== 'number' || !isFinite(e.when) || !clean(e.title, 60)) return;
    var E = { id: k, title: clean(e.title, 60), item: /^[0-9]{3}$/.test(e.item || '') ? e.item : '', when: Math.floor(e.when), place: clean(e.place, 60), note: clean(e.note, 200), host: e.host, hostName: clean(e.hostName, 20) || 'Variante', guests: {}, mine: ['si', 'forse', 'no', 'in attesa'].indexOf(e.mine) >= 0 ? e.mine : 'in attesa', cancelled: e.cancelled === true };
    eachKey(e.guests, VID_RE, function (v, g) { E.guests[v] = { name: clean(g.name, 20) || 'Variante', rsvp: ['si', 'forse', 'no', 'in attesa'].indexOf(g.rsvp) >= 0 ? g.rsvp : 'in attesa', ts: num(g.ts, 0, 4e12, 0) }; }, 100);
    s.evenings[k] = E;
  }, 300);
  eachKey(o.duels, ID_RE, function (k, d) {
    if (d.id !== k || !VID_RE.test(d.by || '') || [5, 10, 15].indexOf(d.n) < 0 || typeof d.qh !== 'string' || !/^[0-9a-f]{8}$/.test(d.qh)) return;
    var seed = num(d.seed, 1, 4294967295, 0); if (!seed) return;
    var D = { id: k, seed: seed, n: d.n, qh: d.qh, by: d.by, byName: clean(d.byName, 20) || 'Variante', created: num(d.created, 0, 4e12, 0), scores: {}, played: d.played === true };
    eachKey(d.scores, VID_RE, function (v, c) { var tot = num(c.total, 1, 15, 0); if (tot) D.scores[v] = { name: clean(c.name, 20) || 'Variante', score: num(c.score, 0, tot, 0), total: tot, ms: num(c.ms, 0, 36e5, 0), ts: num(c.ts, 0, 4e12, 0) }; }, 50);
    s.duels[k] = D;
  }, 300);
  function pkgs(src, dst, inn) {
    eachKey(src, ID_RE, function (k, p) {
      if (p.id !== k || (p.kind !== 'picks' && p.kind !== 'order')) return; var items = Array.isArray(p.items) ? p.items.filter(function (x) { return typeof x === 'string' && /^[0-9]{3}$/.test(x); }).slice(0, p.kind === 'order' ? 200 : 12) : []; if (!items.length) return;
      var P = { id: k, kind: p.kind, title: clean(p.title, 40), desc: clean(p.desc, 120), items: items, ts: num(p.ts, 0, 4e12, 0) };
      if (inn) { if (!VID_RE.test(p.from || '')) return; P.from = p.from; P.fromName = clean(p.fromName, 20) || 'Variante'; } dst[k] = P;
    }, 200);
  }
  if (isObj(o.shared)) { pkgs(o.shared.out, s.shared.out, false); pkgs(o.shared.inn, s.shared.inn, true); }
  if (Array.isArray(o.inbox)) o.inbox.slice(-200).forEach(function (n) {
    if (!isObj(n) || typeof n.id !== 'string' || !/^n_[a-z0-9]{6,16}$/.test(n.id)) return; var k = ['nexus', 'team', 'ev', 'duel', 'share', 'sys'].indexOf(n.k) >= 0 ? n.k : 'sys';
    var ref = null; if (isObj(n.ref) && ['varianti', 'nexus', 'squadre', 'serate', 'sfide', 'archivio', 'com'].indexOf(n.ref.tab) >= 0) { ref = { tab: n.ref.tab }; if (typeof n.ref.id === 'string' && ID_RE.test(n.ref.id)) ref.id = n.ref.id; }
    s.inbox.push({ id: n.id, k: k, ts: num(n.ts, 0, 4e12, 0), read: n.read === true, text: clean(n.text, 220), ref: ref });
  });
  eachKey({ x: o.seen }, /^x$/, function (k, m) { var n = 0; Object.keys(m).forEach(function (id) { if (n < 500 && ID_RE.test(id) && typeof m[id] === 'number') { s.seen[id] = num(m[id], 0, 4e12, 0); n++; } }); }, 1);
  if (isObj(o.best)) s.best = { solo: num(o.best.solo, 0, 15, 0), n: [0, 5, 10, 15].indexOf(o.best.n) >= 0 ? o.best.n : 0 };
  return s;
}
var ST = null, storeOk = true;
function load() { try { ST = normStore(JSON.parse(localStorage.getItem(KEY) || 'null')); } catch (e) { ST = emptyStore(); } if (!ST.vid) ST.vid = rid('v', 10); return ST; }
function save() { try { localStorage.setItem(KEY, JSON.stringify(ST)); storeOk = true; } catch (e) { storeOk = false; } return storeOk; }

/* ---------- codec dei messaggi (manuale: copia/incolla, file, condividi) ---------- */
function toB64(str) { var u = new TextEncoder().encode(str), s = ''; for (var i = 0; i < u.length; i++) s += String.fromCharCode(u[i]); return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
function fromB64(b) { b = b.replace(/-/g, '+').replace(/_/g, '/'); while (b.length % 4) b += '='; var s = atob(b), u = new Uint8Array(s.length); for (var i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return new TextDecoder('utf-8', { fatal: true }).decode(u); }
function card() {
  var m = ST.me, sh = m.share, c = { vid: ST.vid, name: m.name || 'Variante', emblem: m.emblem, color: m.color };
  if (sh.motto && m.motto) c.motto = m.motto; if (sh.univ && m.univ) c.univ = m.univ; if (sh.ch && m.ch) c.ch = m.ch;
  if (sh.tid) { try { var t = localStorage.getItem('marvel-ultimate-timeline-tessera-id'); if (t && /^VAR-[0-9]{6}$/.test(t)) c.tid = t; } catch (e) {} }
  return c;
}
function cleanCard(c) {
  if (!isObj(c) || typeof c.vid !== 'string' || !VID_RE.test(c.vid)) return null;
  var o = { vid: c.vid, name: clean(c.name, 20) || 'Variante', emblem: (c.emblem | 0) >= 0 && (c.emblem | 0) < EMBLEMS.length ? c.emblem | 0 : 0, color: (c.color | 0) >= 0 && (c.color | 0) < COLORS.length ? c.color | 0 : 0 };
  if (c.motto) o.motto = clean(c.motto, 60); if (c.univ) o.univ = clean(c.univ, 60); if (c.ch) o.ch = clean(c.ch, 60);
  if (typeof c.tid === 'string' && /^VAR-[0-9]{6}$/.test(c.tid)) o.tid = c.tid;
  return o;
}
function mkMsg(t, b, to) { var m = { v: 1, id: rid('m_', 12), t: t, ts: now(), from: card(), b: b || {} }; if (to) m.to = to; return m; }
function encode(msg) { var j = JSON.stringify(msg); return 'TVA1.' + toB64(j) + '.' + fnv(j); }
function decode(code) {
  if (typeof code !== 'string') throw new Error('Codice vuoto.');
  code = code.replace(/\s+/g, '');
  if (!code) throw new Error('Incolla un codice TVA Friends.');
  if (code.length > MAXCODE) throw new Error('Codice troppo lungo.');
  var m = /^TVA1\.([A-Za-z0-9_-]+)\.([0-9a-f]{8})$/.exec(code);
  if (!m) throw new Error('Non e\' un codice TVA Friends valido.');
  var j; try { j = fromB64(m[1]); } catch (e) { throw new Error('Codice danneggiato.'); }
  if (fnv(j) !== m[2]) throw new Error('Codice incompleto o trascritto male (controllo di integrita\' non superato).');
  var o; try { o = JSON.parse(j); } catch (e2) { throw new Error('Codice danneggiato.'); }
  if (!isObj(o) || o.v !== 1 || !own(TYPES, o.t) || typeof o.id !== 'string' || !ID_RE.test(o.id) || typeof o.ts !== 'number') throw new Error('Messaggio non riconosciuto (versione diversa?).');
  var f = cleanCard(o.from); if (!f) throw new Error('Mittente non valido.');
  return { v: 1, id: o.id, t: o.t, ts: o.ts, from: f, to: (typeof o.to === 'string' && VID_RE.test(o.to)) ? o.to : null, b: isObj(o.b) ? o.b : {} };
}

/* ---------- titoli del catalogo (dal DOM esistente, in sola lettura) e generatore di quiz ---------- */
var TT = null;
function jsonData(id) { try { return JSON.parse(document.getElementById(id).textContent); } catch (e) { return null; } }
function titles() {
  if (TT) return TT; TT = []; var yr = jsonData('cmpYearData') || {};
  var li = document.querySelectorAll('li.card-wrap[id^="item-"]');
  for (var i = 0; i < li.length; i++) {
    var id = li[i].id.slice(5), t = li[i].querySelector('.title');
    if (/^[0-9]{3}$/.test(id) && t) TT.push({ id: id, name: clean(t.textContent, 80), year: yr['item-' + id] && /^[0-9]{4}$/.test(yr['item-' + id]) ? yr['item-' + id] : null });
  }
  TT.sort(function (a, b) { return a.id < b.id ? -1 : 1; }); return TT;
}
function titleName(id) { var t = titles(); for (var i = 0; i < t.length; i++) if (t[i].id === id) return t[i].name; return 'Scheda ' + id; }
function rng(seed) { var a = seed >>> 0; return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function shuffle(r, a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(r() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
function pick(r, a) { return a[Math.floor(r() * a.length)]; }
function pools() {
  var act = jsonData('cmpActorData') || {}, lv = jsonData('tesseraCharLevelsData') || {}, ln = jsonData('tesseraLevelNamesData') || {}, bp = jsonData('bollettinoPool') || [];
  return {
    ty: titles().filter(function (t) { return t.year; }), actors: Object.keys(act).sort().map(function (k) { return [k, act[k]]; }),
    levels: Object.keys(lv).sort().map(function (k) { return [k, lv[k]]; }), lname: ln,
    curio: (Array.isArray(bp) ? bp : []).filter(function (c) { return c && c.titolo && c.testo && c.testo.toLowerCase().indexOf(String(c.titolo).toLowerCase()) < 0; })
  };
}
var MK = {
  year: function (r, P, u) {
    if (P.ty.length < 8) return null; var t = pick(r, P.ty); if (u['y' + t.id]) return null; u['y' + t.id] = 1;
    var ys = {}; P.ty.forEach(function (x) { if (x.year !== t.year) ys[x.year] = 1; }); var cand = Object.keys(ys).sort(function (a, b) { return Math.abs(a - t.year) - Math.abs(b - t.year) || a - b; }).slice(0, 8);
    var o = shuffle(r, cand).slice(0, 3).concat([t.year]); o = shuffle(r, o);
    return { k: 'year', text: 'In che anno e\' uscito «' + t.name + '»?', opts: o, ans: o.indexOf(t.year), ex: '«' + t.name + '» e\' del ' + t.year + '.' };
  },
  first: function (r, P, u) {
    if (P.ty.length < 8) return null; var s = shuffle(r, P.ty), sel = [], ys = {};
    for (var i = 0; i < s.length && sel.length < 4; i++) if (!ys[s[i].year]) { ys[s[i].year] = 1; sel.push(s[i]); }
    if (sel.length < 4) return null; var key = 'f' + sel.map(function (x) { return x.id; }).sort().join(''); if (u[key]) return null; u[key] = 1;
    var min = sel.reduce(function (a, b) { return a.year < b.year ? a : b; });
    return { k: 'first', text: 'Quale di questi titoli e\' uscito per primo?', opts: sel.map(function (x) { return x.name; }), ans: sel.indexOf(min), ex: '«' + min.name + '» e\' del ' + min.year + '.' };
  },
  actor: function (r, P, u) {
    if (P.actors.length < 6) return null; var a = pick(r, P.actors); if (u['a' + a[0]]) return null; u['a' + a[0]] = 1;
    var others = shuffle(r, P.actors.filter(function (x) { return x[1] !== a[1]; })), seen = {}, o = [];
    for (var i = 0; i < others.length && o.length < 3; i++) if (!seen[others[i][1]]) { seen[others[i][1]] = 1; o.push(others[i][1]); }
    if (o.length < 3) return null; o.push(a[1]); o = shuffle(r, o);
    return { k: 'actor', text: 'Chi interpreta «' + a[0] + '»?', opts: o, ans: o.indexOf(a[1]), ex: a[0] + ': ' + a[1] + '.' };
  },
  level: function (r, P, u) {
    if (P.levels.length < 6) return null; var c = pick(r, P.levels), nm = P.lname[String(c[1])]; if (!nm || u['l' + c[0]]) return null; u['l' + c[0]] = 1;
    var all = Object.keys(P.lname).filter(function (k) { return k !== String(c[1]); }), o = shuffle(r, all).slice(0, 3).map(function (k) { return P.lname[k]; }); o.push(nm); o = shuffle(r, o);
    return { k: 'level', text: 'Che livello di potere ha «' + c[0] + '» nella scala della Tessera TVA?', opts: o, ans: o.indexOf(nm), ex: c[0] + ': ' + nm + '.' };
  },
  curio: function (r, P, u) {
    if (P.curio.length < 8) return null; var c = pick(r, P.curio), k = 'c' + fnv(c.testo); if (u[k]) return null; u[k] = 1;
    var seen = {}; seen[c.titolo] = 1; var o = [], pool = shuffle(r, P.curio);
    for (var i = 0; i < pool.length && o.length < 3; i++) if (!seen[pool[i].titolo]) { seen[pool[i].titolo] = 1; o.push(pool[i].titolo); }
    if (o.length < 3) return null; o.push(c.titolo); o = shuffle(r, o);
    return { k: 'curio', text: 'Di quale titolo parla questa curiosita\'? «' + clean(c.testo, 220) + '»', opts: o, ans: o.indexOf(c.titolo), ex: 'Si tratta di «' + c.titolo + '».' };
  }
};
function genQuiz(seed, n) {
  var r = rng(seed), P = pools(), kinds = Object.keys(MK), qs = [], u = {}, g = 0;
  while (qs.length < n && g++ < 600) { var q = MK[pick(r, kinds)](r, P, u); if (q && !u['t:' + q.text]) { u['t:' + q.text] = 1; qs.push(q); } }
  return qs;
}
function quizHash(qs) { return fnv(JSON.stringify(qs.map(function (q) { return [q.text, q.opts, q.ans]; }))); }
function watchedCount() { try { var w = JSON.parse(localStorage.getItem('marvel-ultimate-timeline-watched') || '{}'); return Object.keys(w).filter(function (k) { return w[k] === true; }).length; } catch (e) { return 0; } }
