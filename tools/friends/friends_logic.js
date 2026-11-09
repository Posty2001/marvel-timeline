/* ---------- logica dei moduli (nessuna UI) ---------- */
function note(k, text, ref) {
  ST.inbox.push({ id: rid('n_', 10), k: k, ts: now(), read: false, text: clean(text, 220), ref: ref || null });
  if (ST.inbox.length > 200) ST.inbox = ST.inbox.slice(-200);
}
function linked(vid) { return own(ST.nexus, vid) && ST.nexus[vid].status === 'linked'; }
function linkedList() { return Object.keys(ST.nexus).filter(linked).map(function (k) { return ST.nexus[k]; }).sort(function (a, b) { return a.name < b.name ? -1 : 1; }); }
function unreadCount() { return ST.inbox.filter(function (n) { return !n.read; }).length + Object.keys(ST.reqs).length; }
function purgeExpired() {
  var t = now(), ch = false;
  Object.keys(ST.pendingOut).forEach(function (k) { if (t - ST.pendingOut[k].ts > INV_TTL) { delete ST.pendingOut[k]; ch = true; } });
  Object.keys(ST.reqs).forEach(function (k) { if (t - ST.reqs[k].ts > INV_TTL) { delete ST.reqs[k]; ch = true; } });
  if (ch) save();
}

/* --- Legame Nexus (doppio consenso) --- */
function nxInvite() { var nonce = rid('', 16); ST.pendingOut[nonce] = { ts: now() }; save(); return mkMsg('nx.invite', { nonce: nonce }); }
function nxCancel(nonce) { if (own(ST.pendingOut, nonce)) { delete ST.pendingOut[nonce]; save(); } }
function nxAccept(reqId) {
  var r = ST.reqs[reqId]; if (!r || r.kind !== 'nx.invite') return null;
  ST.nexus[r.from.vid] = { vid: r.from.vid, name: r.from.name, emblem: r.from.emblem, color: r.from.color, motto: r.from.motto || '', since: now(), status: 'linked' };
  delete ST.reqs[reqId]; note('nexus', 'Legame Nexus attivo con ' + r.from.name + '.', { tab: 'nexus' }); save();
  return mkMsg('nx.accept', { nonce: r.nonce }, r.from.vid);
}
function nxDecline(reqId) { if (own(ST.reqs, reqId)) { delete ST.reqs[reqId]; save(); } }
function nxUnlink(vid) {
  if (!own(ST.nexus, vid)) return null; var n = ST.nexus[vid].name; delete ST.nexus[vid];
  Object.keys(ST.teams).forEach(function (id) { var t = ST.teams[id]; if (t.members && own(t.members, vid) && t.owner === ST.vid) delete t.members[vid]; });
  note('nexus', 'Legame con ' + n + ' rimosso.', { tab: 'nexus' }); save(); return mkMsg('nx.unlink', {}, vid);
}
function nxBlock(vid) { var n = own(ST.nexus, vid) ? ST.nexus[vid].name : 'Variante'; ST.nexus[vid] = { vid: vid, name: n, emblem: 0, color: 0, since: now(), status: 'blocked' }; save(); }
function nxUnblock(vid) { if (own(ST.nexus, vid) && ST.nexus[vid].status === 'blocked') { delete ST.nexus[vid]; save(); } }

/* --- Squadre TVA --- */
function teamNew(name, emblem, goal) {
  var id = rid('t_', 10); name = clean(name, 30); goal = Math.max(5, Math.min(1000, goal | 0));
  if (!name) return null;
  ST.teams[id] = { id: id, name: name, emblem: emblem | 0, goal: goal, owner: ST.vid, created: now(), members: {}, log: [] };
  ST.teams[id].members[ST.vid] = { name: ST.me.name || 'Variante', seen: null, ts: 0 };
  teamLog(id, 'Squadra creata.'); save(); return ST.teams[id];
}
function teamLog(id, text) { var t = ST.teams[id]; if (!t) return; t.log.push({ ts: now(), text: clean(text, 120) }); if (t.log.length > 30) t.log = t.log.slice(-30); }
function teamInvite(id, vid) { var t = ST.teams[id]; if (!t || t.owner !== ST.vid || !linked(vid)) return null; return mkMsg('team.invite', { team: { id: t.id, name: t.name, emblem: t.emblem, goal: t.goal, owner: t.owner } }, vid); }
function teamJoin(reqId) {
  var r = ST.reqs[reqId]; if (!r || r.kind !== 'team.invite') return null; var tm = r.team;
  if (!own(ST.teams, tm.id)) { ST.teams[tm.id] = { id: tm.id, name: tm.name, emblem: tm.emblem, goal: tm.goal, owner: tm.owner, created: now(), members: {}, log: [] }; }
  ST.teams[tm.id].members[ST.vid] = { name: ST.me.name || 'Variante', seen: null, ts: 0 };
  teamLog(tm.id, 'Sei entrato nella squadra.'); delete ST.reqs[reqId]; save();
  return mkMsg('team.join', { teamId: tm.id }, tm.owner);
}
function teamState(id, shareProgress) {
  var t = ST.teams[id]; if (!t || !own(t.members, ST.vid)) return null;
  if (shareProgress) { t.members[ST.vid].seen = watchedCount(); t.members[ST.vid].ts = now(); t.members[ST.vid].name = ST.me.name || 'Variante'; teamLog(id, 'Hai condiviso il tuo avanzamento.'); }
  var mem = {}; Object.keys(t.members).forEach(function (v) { mem[v] = { name: t.members[v].name, seen: t.members[v].seen, ts: t.members[v].ts }; });
  save(); return mkMsg('team.state', { team: { id: t.id, name: t.name, emblem: t.emblem, goal: t.goal, owner: t.owner }, members: mem });
}
function teamLeave(id) { var t = ST.teams[id]; if (!t) return; delete ST.teams[id]; save(); }
function teamKick(id, vid) { var t = ST.teams[id]; if (!t || t.owner !== ST.vid || vid === ST.vid || !own(t.members, vid)) return; var n = t.members[vid].name; delete t.members[vid]; teamLog(id, n + ' rimosso dalla squadra.'); save(); }
function teamProgress(t) { var tot = 0, k = 0; Object.keys(t.members).forEach(function (v) { if (typeof t.members[v].seen === 'number') { tot += t.members[v].seen; k++; } }); return { total: tot, reporting: k, pct: Math.min(100, Math.round(100 * tot / Math.max(1, t.goal))) }; }

/* --- Serate Marvel --- */
function evNew(o) {
  var when = Date.parse(o.when); if (!clean(o.title, 60) || isNaN(when)) return null;
  var id = rid('e_', 10), guests = {};
  (o.guests || []).forEach(function (v) { if (linked(v)) guests[v] = { name: ST.nexus[v].name, rsvp: 'in attesa', ts: 0 }; });
  ST.evenings[id] = { id: id, title: clean(o.title, 60), item: /^[0-9]{3}$/.test(o.item || '') ? o.item : '', when: when, place: clean(o.place, 60), note: clean(o.note, 200), host: ST.vid, hostName: ST.me.name || 'Variante', guests: guests, mine: 'si', cancelled: false };
  save(); return ST.evenings[id];
}
function evInviteMsg(id) { var e = ST.evenings[id]; if (!e || e.host !== ST.vid) return null; return mkMsg('ev.invite', { ev: { id: e.id, title: e.title, item: e.item, when: e.when, place: e.place, note: e.note, host: e.host, guests: Object.keys(e.guests) } }); }
function evRsvp(id, rsvp) {
  var e = ST.evenings[id]; if (!e || e.host === ST.vid || ['si', 'forse', 'no'].indexOf(rsvp) < 0) return null; e.mine = rsvp; save();
  return mkMsg('ev.rsvp', { id: id, rsvp: rsvp }, e.host);
}
function evCancel(id) { var e = ST.evenings[id]; if (!e || e.host !== ST.vid) return null; e.cancelled = true; save(); return mkMsg('ev.cancel', { id: id }); }
function evDelete(id) { delete ST.evenings[id]; save(); }
function icsEscape(s) { return String(s).replace(/\\/g, '\\\\').replace(/;/g, '\;').replace(/,/g, '\\,').replace(/\n/g, '\\n'); }
function icsDate(ms) { return new Date(ms).toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, ''); }
function evIcs(id) {
  var e = ST.evenings[id]; if (!e) return null;
  return ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//TVA Archives//Friends//IT', 'BEGIN:VEVENT', 'UID:' + e.id + '@tva-archives', 'DTSTAMP:' + icsDate(now()), 'DTSTART:' + icsDate(e.when), 'DTEND:' + icsDate(e.when + 3 * 36e5),
    'SUMMARY:' + icsEscape('Serata Marvel: ' + e.title), e.place ? 'LOCATION:' + icsEscape(e.place) : null, e.note ? 'DESCRIPTION:' + icsEscape(e.note) : null, 'END:VEVENT', 'END:VCALENDAR'].filter(Boolean).join('\r\n');
}

/* --- Quiz e Duelli --- */
function duelNew(n) {
  var seed = (Math.floor(Math.random() * 4294967295) >>> 0) || 1, qs = genQuiz(seed, n); if (qs.length < n) return null;
  var id = rid('d_', 10); ST.duels[id] = { id: id, seed: seed, n: n, qh: quizHash(qs), by: ST.vid, byName: ST.me.name || 'Variante', created: now(), scores: {}, played: false };
  save(); return ST.duels[id];
}
function duelChallengeMsg(id) { var d = ST.duels[id]; if (!d) return null; return mkMsg('duel.challenge', { id: d.id, seed: d.seed, n: d.n, qh: d.qh }); }
function duelRecord(id, score, total, ms) {
  var d = ST.duels[id]; if (!d) return null; d.scores[ST.vid] = { name: ST.me.name || 'Variante', score: score, total: total, ms: ms, ts: now() }; d.played = true;
  note('duel', 'Duello completato: ' + score + '/' + total + '.', { tab: 'sfide', id: id }); save();
  return mkMsg('duel.result', { id: id, score: score, total: total, ms: ms });
}
function duelBoard(d) { return Object.keys(d.scores).map(function (v) { return Object.assign({ vid: v }, d.scores[v]); }).sort(function (a, b) { return b.score - a.score || a.ms - b.ms; }); }
function soloRecord(score, total) { if (total >= ST.best.n && score / total >= (ST.best.n ? ST.best.solo / ST.best.n : 0)) { ST.best = { solo: score, n: total }; } save(); }

/* --- Archivio condiviso: whitelist rigida, nessun dato personale --- */
function pkgPicks(title, desc, ids) {
  ids = (ids || []).filter(function (i) { return /^[0-9]{3}$/.test(i); }).filter(function (v, i, a) { return a.indexOf(v) === i; }).slice(0, 12);
  title = clean(title, 40); if (!title || !ids.length) return null;
  var id = rid('p_', 10), p = { id: id, kind: 'picks', title: title, desc: clean(desc, 120), items: ids, ts: now() }; ST.shared.out[id] = p; save(); return p;
}
function customOrderIds() { try { var o = JSON.parse(localStorage.getItem('marvelGuideCustomTimelineOrder') || 'null'); if (Array.isArray(o)) return o.map(function (x) { return String(x).padStart(3, '0'); }).filter(function (x) { return /^[0-9]{3}$/.test(x); }).slice(0, 200); } catch (e) {} return []; }
function pkgOrder(title) {
  var ids = customOrderIds(); title = clean(title, 40) || 'Il mio ordine Timeline'; if (!ids.length) return null;
  var id = rid('p_', 10), p = { id: id, kind: 'order', title: title, desc: '', items: ids, ts: now() }; ST.shared.out[id] = p; save(); return p;
}
function pkgMsg(id) { var p = ST.shared.out[id]; if (!p) return null; return mkMsg('share.pkg', { id: p.id, kind: p.kind, title: p.title, desc: p.desc, items: p.items }); }

/* --- Ricezione: unica porta d'ingresso per codici manuali e (in futuro) cloud --- */
function cleanIds(a, max) { return Array.isArray(a) ? a.filter(function (x) { return typeof x === 'string' && /^[0-9]{3}$/.test(x); }).slice(0, max) : []; }
function receive(msg) {
  if (own(ST.seen, msg.id)) return { ok: false, text: 'Questo codice e\' gia\' stato importato.' };
  if (msg.from.vid === ST.vid) return { ok: false, text: 'Questo codice e\' stato creato da te.' };
  if (own(ST.nexus, msg.from.vid) && ST.nexus[msg.from.vid].status === 'blocked') return { ok: false, text: 'Mittente bloccato: codice ignorato.' };
  if (msg.to && msg.to !== ST.vid) return { ok: false, text: 'Questo codice e\' destinato a un\'altra Variante.' };
  if (now() - msg.ts > INV_TTL * 4 && msg.t.indexOf('nx.') === 0) return { ok: false, text: 'Codice scaduto: chiedi un nuovo invito.' };
  var f = msg.from, b = msg.b, t = msg.t, out;
  function done(text) { ST.seen[msg.id] = now(); var ks = Object.keys(ST.seen); if (ks.length > 500) ks.sort(function (a, c) { return ST.seen[a] - ST.seen[c]; }).slice(0, ks.length - 500).forEach(function (k) { delete ST.seen[k]; }); save(); return { ok: true, text: text, t: msg.t, from: msg.from.vid }; }
  if (t === 'nx.invite') {
    if (typeof b.nonce !== 'string' || !/^[a-z0-9]{16}$/.test(b.nonce)) return { ok: false, text: 'Invito non valido.' };
    if (linked(f.vid)) return { ok: false, text: 'Sei gia\' collegato a ' + f.name + '.' };
    ST.reqs[msg.id] = { kind: 'nx.invite', from: f, nonce: b.nonce, ts: now() }; note('nexus', f.name + ' vuole collegarsi a te (Legame Nexus). Accetta o rifiuta.', { tab: 'nexus' });
    return done('Invito Nexus ricevuto da ' + f.name + '. Vai su Nexus per accettare o rifiutare: nulla e\' collegato finche\' non accetti.');
  }
  if (t === 'nx.accept') {
    if (typeof b.nonce !== 'string' || !own(ST.pendingOut, b.nonce)) return { ok: false, text: 'Risposta non attesa: non hai un invito aperto corrispondente (o e\' scaduto).' };
    if (msg.to !== ST.vid) return { ok: false, text: 'Risposta non destinata a te.' };
    delete ST.pendingOut[b.nonce]; ST.nexus[f.vid] = { vid: f.vid, name: f.name, emblem: f.emblem, color: f.color, motto: f.motto || '', since: now(), status: 'linked' };
    note('nexus', 'Legame Nexus attivo con ' + f.name + '.', { tab: 'nexus' }); return done('Legame Nexus attivo con ' + f.name + '.');
  }
  if (!linked(f.vid)) return { ok: false, text: 'Mittente non collegato: serve prima il Legame Nexus (consenso di entrambi).' };
  ST.nexus[f.vid].name = f.name; ST.nexus[f.vid].emblem = f.emblem; ST.nexus[f.vid].color = f.color;
  if (t === 'nx.unlink') { delete ST.nexus[f.vid]; note('nexus', f.name + ' ha rimosso il Legame Nexus.', { tab: 'nexus' }); return done(f.name + ' ha rimosso il collegamento.'); }
  if (t === 'team.invite') {
    var tm = isObj(b.team) ? b.team : null; if (!tm || !ID_RE.test(tm.id || '') || tm.owner !== f.vid || clean(tm.name, 30) === '') return { ok: false, text: 'Invito squadra non valido.' };
    ST.reqs[msg.id] = { kind: 'team.invite', from: f, ts: now(), team: { id: tm.id, name: clean(tm.name, 30), emblem: (tm.emblem | 0) % EMBLEMS.length, goal: Math.max(5, Math.min(1000, tm.goal | 0)), owner: tm.owner } };
    note('team', f.name + ' ti invita nella squadra \u00AB' + clean(tm.name, 30) + '\u00BB.', { tab: 'squadre' }); return done('Invito squadra ricevuto: accettalo dalla scheda Squadre.');
  }
  if (t === 'team.join') {
    var tj = own(ST.teams, b.teamId) ? ST.teams[b.teamId] : null; if (!tj || tj.owner !== ST.vid) return { ok: false, text: 'Squadra non trovata o non sei il capo squadra.' };
    tj.members[f.vid] = { name: f.name, seen: null, ts: 0 }; teamLog(tj.id, f.name + ' e\' entrato nella squadra.'); note('team', f.name + ' e\' entrato in \u00AB' + tj.name + '\u00BB.', { tab: 'squadre', id: tj.id });
    return done(f.name + ' aggiunto alla squadra. Invia un aggiornamento squadra per farlo vedere a tutti.');
  }
  if (t === 'team.state') {
    var ts = isObj(b.team) ? b.team : null; if (!ts || !own(ST.teams, ts.id)) return { ok: false, text: 'Non fai parte di questa squadra.' };
    var T = ST.teams[ts.id]; if (!own(T.members, ST.vid)) return { ok: false, text: 'Non fai parte di questa squadra.' };
    if (ts.owner !== T.owner) return { ok: false, text: 'Squadra non coerente.' };
    var mem = isObj(b.members) ? b.members : {}, isOwner = f.vid === T.owner;
    if (isOwner) { T.name = clean(ts.name, 30) || T.name; T.goal = Math.max(5, Math.min(1000, ts.goal | 0)); T.emblem = (ts.emblem | 0) % EMBLEMS.length; }
    Object.keys(mem).forEach(function (v) {
      if (!VID_RE.test(v) || v === ST.vid || !isObj(mem[v])) return;
      var me = mem[v];
      if (v === f.vid || isOwner) {            /* ognuno aggiorna solo se stesso; il capo puo' aggiornare e aggiungere membri */
        var cur = own(T.members, v) ? T.members[v] : { name: '', seen: null, ts: 0 };
        var seen = (typeof me.seen === 'number' && me.seen >= 0 && me.seen <= 1000) ? Math.floor(me.seen) : null, tsm = typeof me.ts === 'number' ? me.ts : 0;
        if (!own(T.members, v) || tsm >= cur.ts) T.members[v] = { name: clean(me.name, 20) || cur.name || 'Variante', seen: seen, ts: tsm };
      }
    });
    if (isOwner) Object.keys(T.members).forEach(function (v) { if (v !== ST.vid && !own(mem, v)) delete T.members[v]; });
    teamLog(T.id, 'Aggiornamento da ' + f.name + '.'); note('team', 'Aggiornamento squadra \u00AB' + T.name + '\u00BB da ' + f.name + '.', { tab: 'squadre', id: T.id });
    return done('Squadra \u00AB' + T.name + '\u00BB aggiornata.');
  }
  if (t === 'ev.invite') {
    var ev = isObj(b.ev) ? b.ev : null; if (!ev || !ID_RE.test(ev.id || '') || ev.host !== f.vid || typeof ev.when !== 'number' || !clean(ev.title, 60)) return { ok: false, text: 'Invito serata non valido.' };
    if (!Array.isArray(ev.guests) || ev.guests.indexOf(ST.vid) < 0) return { ok: false, text: 'Non sei tra gli invitati a questa serata.' };
    var old = own(ST.evenings, ev.id) ? ST.evenings[ev.id] : null;
    ST.evenings[ev.id] = { id: ev.id, title: clean(ev.title, 60), item: /^[0-9]{3}$/.test(ev.item || '') ? ev.item : '', when: ev.when, place: clean(ev.place, 60), note: clean(ev.note, 200), host: f.vid, hostName: f.name, guests: {}, mine: old ? old.mine : 'in attesa', cancelled: false };
    note('ev', f.name + ' ti invita alla serata \u00AB' + clean(ev.title, 60) + '\u00BB.', { tab: 'serate', id: ev.id }); return done('Invito alla serata \u00AB' + clean(ev.title, 60) + '\u00BB ricevuto.');
  }
  if (t === 'ev.rsvp') {
    var E = own(ST.evenings, b.id) ? ST.evenings[b.id] : null; if (!E || E.host !== ST.vid) return { ok: false, text: 'Serata non trovata.' };
    if (!own(E.guests, f.vid) || ['si', 'forse', 'no'].indexOf(b.rsvp) < 0) return { ok: false, text: 'Risposta non valida.' };
    E.guests[f.vid].rsvp = b.rsvp; E.guests[f.vid].ts = now(); note('ev', f.name + ' risponde \u00AB' + b.rsvp + '\u00BB a \u00AB' + E.title + '\u00BB.', { tab: 'serate', id: E.id }); return done('Risposta di ' + f.name + ': ' + b.rsvp + '.');
  }
  if (t === 'ev.cancel') {
    var E2 = own(ST.evenings, b.id) ? ST.evenings[b.id] : null; if (!E2 || E2.host !== f.vid) return { ok: false, text: 'Serata non trovata.' };
    E2.cancelled = true; note('ev', 'Serata \u00AB' + E2.title + '\u00BB annullata da ' + f.name + '.', { tab: 'serate', id: E2.id }); return done('Serata annullata dall\'organizzatore.');
  }
  if (t === 'duel.challenge') {
    if (typeof b.id !== 'string' || !ID_RE.test(b.id) || typeof b.seed !== 'number' || b.seed < 1 || b.seed > 4294967295 || [5, 10, 15].indexOf(b.n) < 0 || typeof b.qh !== 'string' || !/^[0-9a-f]{8}$/.test(b.qh)) return { ok: false, text: 'Sfida non valida.' };
    if (own(ST.duels, b.id)) return { ok: false, text: 'Sfida gia\' presente.' };
    var qs = genQuiz(b.seed | 0, b.n); if (qs.length < b.n || quizHash(qs) !== b.qh) return { ok: false, text: 'Questa sfida e\' stata creata con una versione diversa dell\'app: aggiorna entrambi i dispositivi.' };
    ST.duels[b.id] = { id: b.id, seed: b.seed, n: b.n, qh: b.qh, by: f.vid, byName: f.name, created: now(), scores: {}, played: false };
    note('duel', f.name + ' ti sfida a un duello Marvel (' + b.n + ' domande).', { tab: 'sfide', id: b.id }); return done('Sfida di ' + f.name + ' ricevuta: la trovi in Quiz e Duelli.');
  }
  if (t === 'duel.result') {
    var D = own(ST.duels, b.id) ? ST.duels[b.id] : null; if (!D) return { ok: false, text: 'Duello non trovato: importa prima la sfida.' };
    if (typeof b.score !== 'number' || typeof b.total !== 'number' || b.total !== D.n || b.score < 0 || b.score > b.total || typeof b.ms !== 'number' || b.ms < 0 || b.ms > 36e5) return { ok: false, text: 'Risultato non valido.' };
    D.scores[f.vid] = { name: f.name, score: Math.floor(b.score), total: b.total, ms: Math.floor(b.ms), ts: now() };
    note('duel', f.name + ' ha chiuso il duello: ' + Math.floor(b.score) + '/' + b.total + '.', { tab: 'sfide', id: D.id }); return done('Risultato di ' + f.name + ': ' + Math.floor(b.score) + '/' + b.total + '.');
  }
  if (t === 'share.pkg') {
    if (typeof b.id !== 'string' || !ID_RE.test(b.id) || ['picks', 'order'].indexOf(b.kind) < 0) return { ok: false, text: 'Pacchetto non valido.' };
    var items = cleanIds(b.items, b.kind === 'order' ? 200 : 12); if (!items.length) return { ok: false, text: 'Pacchetto vuoto.' };
    ST.shared.inn[b.id] = { id: b.id, from: f.vid, fromName: f.name, kind: b.kind, title: clean(b.title, 40), desc: clean(b.desc, 120), items: items, ts: now() };
    note('share', f.name + ' ha condiviso \u00AB' + clean(b.title, 40) + '\u00BB.', { tab: 'archivio' }); return done('Pacchetto \u00AB' + clean(b.title, 40) + '\u00BB aggiunto all\'Archivio condiviso.');
  }
  return { ok: false, text: 'Messaggio non gestito.' };
}
function importCode(code) { var m; try { m = decode(code); } catch (e) { return { ok: false, text: e.message }; } return receive(m); }
