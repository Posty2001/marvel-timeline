/* ---------- interfaccia ---------- */
var UI = { root: null, tab: 'varianti', opener: null, out: null, sub: {}, game: null };
var TABS = [['varianti', '🧬', 'Varianti'], ['nexus', '🔗', 'Nexus'], ['squadre', '🛡️', 'Squadre'], ['serate', '🍿', 'Serate'], ['sfide', '🎯', 'Quiz e Duelli'], ['archivio', '🗂️', 'Archivio'], ['com', '🔔', 'Comunicazioni']];
function add(e, kids) { (kids || []).forEach(function (c) { if (c === null || c === undefined || c === false) return; if (Array.isArray(c)) add(e, c); else e.appendChild(typeof c === 'string' || typeof c === 'number' ? document.createTextNode(String(c)) : c); }); return e; }
function h(tag, a, kids) {
  var e = document.createElement(tag);
  if (a) Object.keys(a).forEach(function (k) { var v = a[k]; if (v === null || v === undefined || v === false) return; if (k === 'class') e.className = v; else if (k.slice(0, 2) === 'on') e.addEventListener(k.slice(2), v); else if (v === true) e.setAttribute(k, ''); else e.setAttribute(k, v); });
  return add(e, kids);
}
function btn(text, fn, cls, attrs) { return h('button', Object.assign({ type: 'button', class: 'reset-btn tf-btn ' + (cls || ''), onclick: fn }, attrs || {}), [text]); }
function toast(msg) { var t = document.getElementById('tfToast'); if (!t) return; t.textContent = msg; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(function () { t.hidden = true; }, 5200); }
function fmtDate(ms) { try { return new Date(ms).toLocaleString('it-IT', { dateStyle: 'medium', timeStyle: 'short' }); } catch (e) { return String(ms); } }
function fmtIn(ms) { var d = ms - now(), a = Math.abs(d), m = Math.round(a / 6e4), t = m < 60 ? m + ' min' : m < 1440 ? Math.round(m / 60) + ' ore' : Math.round(m / 1440) + ' giorni'; return d >= 0 ? 'tra ' + t : t + ' fa'; }
function persist() { if (!save()) { toast('Spazio del browser pieno: modifica NON salvata. Libera spazio ed esporta un backup Friends.'); return false; } return true; }
function emb(i) { return EMBLEMS[(i | 0) % EMBLEMS.length]; }
function cardEl(c, extra) {
  return h('div', { class: 'tf-card', style: '--tfc:' + COLORS[(c.color | 0) % COLORS.length] }, [h('span', { class: 'tf-emb', 'aria-hidden': 'true' }, [emb(c.emblem)]),
    h('div', { class: 'tf-card-b' }, [h('b', {}, [c.name || 'Variante']), c.tid ? h('span', { class: 'tf-sub' }, [c.tid]) : null, c.motto ? h('i', { class: 'tf-sub' }, ['“' + c.motto + '”']) : null, c.univ ? h('span', { class: 'tf-sub' }, ['Universo: ' + c.univ]) : null, c.ch ? h('span', { class: 'tf-sub' }, ['Personaggio: ' + c.ch]) : null, extra || null])]);
}

/* pannello «codice da inviare» */
function showOut(title, msg, hint) {
  var code = encode(msg); UI.out = { title: title, code: code, hint: hint, msg: msg, to: msg.to || '' };
  renderOut();
}
function renderOut() {
  var box = document.getElementById('tfOut'); if (!box) return; box.textContent = '';
  if (!UI.out) { box.hidden = true; return; }
  var o = UI.out; box.hidden = false;
  var ta = h('textarea', { class: 'tf-code', readonly: true, rows: 3, 'aria-label': 'Codice da inviare', id: 'tfOutCode' }); ta.value = o.code;
  add(box, [h('h4', {}, ['📤 ' + o.title]), h('p', { class: 'tf-help' }, [o.hint || 'Invia questo codice alla persona interessata (messaggio, email, AirDrop). Non contiene note, voti, Diario o progressi.']), ta,
    h('div', { class: 'tf-row' }, [btn('Copia', function () { try { navigator.clipboard.writeText(o.code).then(function () { toast('Codice copiato.'); }, function () { ta.select(); toast('Selezionato: copialo a mano.'); }); } catch (e) { ta.select(); toast('Selezionato: copialo a mano.'); } }, '', { id: 'tfCopy' }),
      (navigator.share ? btn('Condividi', function () { navigator.share({ text: o.code }).catch(function () {}); }, '') : null),
      btn('Scarica file', function () { dl('tva-friends-' + o.code.slice(5, 11) + '.tvafriends', o.code, 'text/plain'); }, ''), btn('Chiudi', function () { UI.out = null; renderOut(); }, '')]),
    CLOUD.enabled() ? cloudRow(o) : null]);
}
function cloudRow(o) {
  var to = h('input', { type: 'text', class: 'tf-in', id: 'tfCloudTo', placeholder: 'ID Variante destinataria (v\u2026)', 'aria-label': 'ID Variante destinataria', value: o.to || '' });
  return h('div', { class: 'tf-row', id: 'tfCloudRow' }, [to, btn('Invia via cloud', function () {
    var t = to.value.trim(); if (!VID_RE.test(t)) { toast('ID Variante non valido.'); return; }
    CLOUD.send(o.msg, t).then(function () { toast('Inviato via cloud.'); }, function (e) { toast('Invio cloud NON riuscito (' + ((e && (e.code || e.message)) || 'errore') + '). Puoi usare il codice.'); });
  }, '', { id: 'tfCloudSend' })]);
}
function dl(name, text, type) { try { var b = new Blob([text], { type: type || 'text/plain' }), u = URL.createObjectURL(b), a = h('a', { href: u, download: name }); document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(u); }, 4000); } catch (e) { toast('Download non disponibile su questo browser.'); } }
function ask(q) { try { return window.confirm(q); } catch (e) { return false; } }

/* importa codice (testo o file) */
function doImport(text) {
  var r = importCode(text); toast(r.text); if (r.ok && r.t === 'nx.accept' && CLOUD.enabled()) CLOUD.link(r.from).then(null, function () {}); renderAll(); return r;
}
function importBar() {
  var ta = h('textarea', { id: 'tfImpText', class: 'tf-code', rows: 2, placeholder: 'Incolla qui un codice TVA Friends (TVA1.…)', 'aria-label': 'Codice da importare' });
  var fi = h('input', { type: 'file', id: 'tfImpFile', accept: '.tvafriends,.txt,text/plain', hidden: true, onchange: function () {
    var f = fi.files && fi.files[0]; if (!f) return; if (f.size > MAXCODE * 2) { toast('File troppo grande.'); return; }
    var rd = new FileReader(); rd.onload = function () { doImport(String(rd.result || '')); fi.value = ''; }; rd.onerror = function () { toast('Impossibile leggere il file.'); }; rd.readAsText(f);
  } });
  return h('details', { class: 'tf-imp', id: 'tfImp' }, [h('summary', {}, ['📥 Importa un codice ricevuto']), ta,
    h('div', { class: 'tf-row' }, [btn('Importa', function () { var r = doImport(ta.value); if (r.ok) ta.value = ''; }, 'tf-primary', { id: 'tfImpBtn' }), btn('Da file…', function () { fi.click(); }, ''),
      btn('Incolla', function () { try { navigator.clipboard.readText().then(function (t) { ta.value = t; }, function () { toast('Incolla a mano: permesso negato.'); }); } catch (e) { toast('Incolla a mano.'); } }, '')]), fi]);
}

/* --- Varianti --- */
function viewVarianti(c) {
  var m = ST.me, sh = m.share, mv = jsonData('mvMapData'), univs = mv && mv.universi ? Object.keys(mv.universi).map(function (k) { return mv.universi[k].nome; }).filter(Boolean).sort() : [], chs = Object.keys(jsonData('tesseraCharLevelsData') || {}).sort();
  var name = h('input', { type: 'text', maxlength: 20, id: 'tfName', class: 'tf-in', value: m.name || (function () { try { return localStorage.getItem('marvel-ultimate-timeline-user-name') || ''; } catch (e) { return ''; } })(), 'aria-label': 'Nome Variante', autocomplete: 'off' });
  var motto = h('input', { type: 'text', maxlength: 60, id: 'tfMotto', class: 'tf-in', value: m.motto, 'aria-label': 'Motto', placeholder: 'Un motto (facoltativo)' });
  var sel = function (id, list, val, label) { var s = h('select', { id: id, class: 'tf-in', 'aria-label': label }, [h('option', { value: '' }, ['— nessuno —'])].concat(list.map(function (x) { return h('option', { value: x }, [x]); }))); s.value = list.indexOf(val) >= 0 ? val : ''; return s; };
  var univ = sel('tfUniv', univs, m.univ, 'Universo preferito'), ch = sel('tfCh', chs, m.ch, 'Personaggio preferito');
  var emblem = m.emblem, color = m.color, prev = h('div', { id: 'tfPrev' });
  var chk = {};
  function mkChk(k, label, disabled) { var i = h('input', { type: 'checkbox', id: 'tfSh-' + k, disabled: disabled, onchange: function () { refreshPrev(); } }); i.checked = !!sh[k]; chk[k] = i; return h('label', { class: 'tf-chk' }, [i, ' ' + label]); }
  function draft() { var d = JSON.parse(JSON.stringify(ST.me)); d.name = clean(name.value, 20); d.motto = clean(motto.value, 60); d.univ = univ.value; d.ch = ch.value; d.emblem = emblem; d.color = color; Object.keys(chk).forEach(function (k) { d.share[k] = chk[k].checked; }); return d; }
  function refreshPrev() {
    var saved = ST.me; ST.me = draft(); var cd = cleanCard(card()); ST.me = saved; prev.textContent = ''; add(prev, [h('p', { class: 'tf-help' }, ['Anteprima: e\' esattamente quello che vedranno le Varianti collegate.']), cardEl(cd)]);
  }
  var em = h('div', { class: 'tf-grid', role: 'radiogroup', 'aria-label': 'Emblema' }, EMBLEMS.map(function (e, i) { return h('button', { type: 'button', class: 'tf-pick' + (i === emblem ? ' on' : ''), role: 'radio', 'aria-checked': i === emblem ? 'true' : 'false', 'aria-label': 'Emblema ' + (i + 1), onclick: function () { emblem = i; em.querySelectorAll('.tf-pick').forEach(function (b, j) { b.classList.toggle('on', j === i); b.setAttribute('aria-checked', j === i ? 'true' : 'false'); }); refreshPrev(); } }, [e]); }));
  var co = h('div', { class: 'tf-grid', role: 'radiogroup', 'aria-label': 'Colore' }, COLORS.map(function (cc, i) { return h('button', { type: 'button', class: 'tf-pick tf-col' + (i === color ? ' on' : ''), style: 'background:' + cc, role: 'radio', 'aria-checked': i === color ? 'true' : 'false', 'aria-label': 'Colore ' + (i + 1), onclick: function () { color = i; co.querySelectorAll('.tf-pick').forEach(function (b, j) { b.classList.toggle('on', j === i); b.setAttribute('aria-checked', j === i ? 'true' : 'false'); }); refreshPrev(); } }); }));
  [name, motto, univ, ch].forEach(function (x) { x.addEventListener('input', refreshPrev); x.addEventListener('change', refreshPrev); });
  var shr = h('fieldset', { class: 'tf-fs' }, [h('legend', {}, ['Cosa puo\' vedere chi e\' collegato a te']), h('p', { class: 'tf-help' }, ['Il nome e l\'emblema sono sempre visibili ai collegati. Il resto e\' facoltativo.']), mkChk('tid', 'Numero Variante (VAR-…)'), mkChk('motto', 'Motto'), mkChk('univ', 'Universo preferito'), mkChk('ch', 'Personaggio preferito'),
    h('p', { class: 'tf-help' }, ['Mai condivisi: Diario TVA, note, voti, preferiti, progressi, XP e badge. Il tuo numero di titoli visti viene inviato solo quando premi “Condividi il mio avanzamento” in una squadra.'])]);
  add(c, [h('h3', {}, ['La tua Variante']), h('label', { class: 'tf-l', for: 'tfName' }, ['Nome Variante']), name, h('span', { class: 'tf-l' }, ['Emblema']), em, h('span', { class: 'tf-l' }, ['Colore']), co,
    h('label', { class: 'tf-l', for: 'tfMotto' }, ['Motto']), motto, h('label', { class: 'tf-l', for: 'tfUniv' }, ['Universo preferito']), univ, h('label', { class: 'tf-l', for: 'tfCh' }, ['Personaggio preferito']), ch, shr, prev,
    h('div', { class: 'tf-row' }, [btn('Salva Variante', function () {
      var d = draft(); if (!d.name) { toast('Scegli un nome per la tua Variante.'); return; }
      ST.me = d; if (persist()) toast('Variante salvata. Le Varianti gia\' collegate vedranno le modifiche ai prossimi scambi.'); renderAll();
    }, 'tf-primary', { id: 'tfSaveMe' })]),
    h('h4', {}, ['Backup dati Friends']), h('p', { class: 'tf-help' }, ['I dati Friends restano su questo dispositivo e NON fanno parte del profilo sincronizzato. Esporta un file per metterli al sicuro.']),
    h('div', { class: 'tf-row' }, [btn('Esporta backup Friends', function () { dl('tva-friends-backup.json', JSON.stringify(ST), 'application/json'); toast('Backup Friends esportato.'); }, '', { id: 'tfExp' }),
      btn('Ripristina backup…', function () { document.getElementById('tfBkFile').click(); }, '', { id: 'tfBkBtn' }),
      h('input', { type: 'file', id: 'tfBkFile', accept: '.json,application/json', hidden: true, onchange: function (ev) {
        var f = ev.target.files && ev.target.files[0]; if (!f) return; if (f.size > 4e6) { toast('File troppo grande.'); return; }
        var rd = new FileReader(); rd.onload = function () {
          var o; try { o = JSON.parse(String(rd.result)); } catch (e) { toast('File non valido.'); return; }
          if (!isObj(o) || o.v !== 1) { toast('Non e\' un backup Friends.'); return; }
          if (!ask('Sostituire TUTTI i dati Friends di questo dispositivo con quelli del file? Non verra\' toccato nient\'altro (profilo, voti, note).')) { toast('Ripristino annullato.'); return; }
          var prevSt = JSON.stringify(ST); ST = normStore(o); if (!ST.vid) ST.vid = rid('v', 10); if (!save()) { ST = JSON.parse(prevSt); toast('Ripristino NON riuscito: spazio pieno.'); } else toast('Backup Friends ripristinato.'); renderAll();
        }; rd.readAsText(f); ev.target.value = '';
      } })]),
    h('h4', {}, ['Cloud']), h('p', { class: 'tf-help', id: 'tfCloudNote' }, [CLOUD_ENABLED ? (CLOUD.enabled() ? 'Cloud attivo. Il tuo ID Variante: ' + ST.vid : 'Cloud pronto: accedi con un account verificato e resta online.') : 'Cloud non attivo: in attesa della verifica delle regole di sicurezza. Gli scambi avvengono con codici o file, e funzionano anche offline.']),
      CLOUD.enabled() ? btn('Pubblica la mia Variante nel cloud', function () { if (!ask('Rendere raggiungibile il tuo ID Variante e la tua carta pubblica (nome, emblema e i campi che hai scelto) dalle altre Varianti?')) return; CLOUD.publish().then(function () { toast('Pubblicata nel cloud.'); }, function (e) { toast('Pubblicazione NON riuscita (' + ((e && (e.code || e.message)) || 'errore') + ').'); }); }, '', { id: 'tfCloudPub' }) : null]);
  refreshPrev();
}

/* --- Nexus --- */
function viewNexus(c) {
  var reqs = Object.keys(ST.reqs).filter(function (k) { return ST.reqs[k].kind === 'nx.invite'; });
  add(c, [h('h3', {}, ['Legame Nexus']), h('p', { class: 'tf-help' }, ['Il collegamento e\' consensuale: serve l\'accettazione di entrambi. Fino ad allora nessun dato viene condiviso.']),
    btn('Crea invito Nexus', function () { if (!ST.me.name) { toast('Prima salva il nome della tua Variante.'); UI.tab = 'varianti'; renderAll(); return; } showOut('Invito Nexus', nxInvite(), 'Invia questo invito alla persona che vuoi collegare. Quando lo accetta ti restituira\' un codice di risposta da importare qui.'); renderAll(); }, 'tf-primary', { id: 'tfNxInvite' })]);
  if (reqs.length) add(c, [h('h4', {}, ['Richieste ricevute']), reqs.map(function (k) { var r = ST.reqs[k]; return h('div', { class: 'tf-item', 'data-req': k }, [cardEl(r.from), h('div', { class: 'tf-row' }, [
    btn('Accetta', function () { var m = nxAccept(k); if (m && CLOUD.enabled()) CLOUD.link(r.from.vid).then(null, function () {}); if (m) { showOut('Risposta Nexus', m, 'Invia questa risposta a ' + r.from.name + ' per completare il collegamento.'); } renderAll(); }, 'tf-primary', { 'data-act': 'nx-accept' }),
    btn('Rifiuta', function () { nxDecline(k); toast('Richiesta rifiutata. Nessun dato condiviso.'); renderAll(); }, ''), btn('Blocca', function () { if (ask('Bloccare ' + r.from.name + '? I suoi codici verranno ignorati.')) { nxDecline(k); nxBlock(r.from.vid); renderAll(); } }, '')])]); })]);
  var out = Object.keys(ST.pendingOut);
  if (out.length) add(c, [h('h4', {}, ['Inviti in attesa di risposta']), out.map(function (k) { return h('div', { class: 'tf-item' }, [h('span', {}, ['Invito creato ' + fmtDate(ST.pendingOut[k].ts) + ' — scade tra ' + Math.max(0, Math.round((INV_TTL - (now() - ST.pendingOut[k].ts)) / 864e5)) + ' giorni']), btn('Annulla', function () { nxCancel(k); renderAll(); }, '')]); })]);
  var L = linkedList();
  add(c, [h('h4', {}, ['Varianti collegate (' + L.length + ')']), L.length ? L.map(function (n) { return h('div', { class: 'tf-item', 'data-vid': n.vid }, [cardEl(n, h('span', { class: 'tf-sub' }, ['Collegati dal ' + fmtDate(n.since)])), h('div', { class: 'tf-row' }, [
    btn('Scollega', function () { if (ask('Scollegare ' + n.name + '? Gli scambi futuri verranno rifiutati.')) { var m = nxUnlink(n.vid); if (m) showOut('Avviso di scollegamento', m, 'Facoltativo: invia questo codice a ' + n.name + ' perche\' rimuova il legame anche dal suo lato.'); renderAll(); } }, ''),
    btn('Blocca', function () { if (ask('Bloccare ' + n.name + '?')) { nxBlock(n.vid); renderAll(); } }, '')])]); }) : h('p', { class: 'tf-empty' }, ['Nessun collegamento. Crea un invito o importa quello di un amico.'])]);
  var bl = Object.keys(ST.nexus).filter(function (k) { return ST.nexus[k].status === 'blocked'; });
  if (bl.length) add(c, [h('h4', {}, ['Bloccati']), bl.map(function (k) { return h('div', { class: 'tf-item' }, [h('span', {}, [ST.nexus[k].name]), btn('Sblocca', function () { nxUnblock(k); renderAll(); }, '')]); })]);
}

/* --- Squadre --- */
function viewSquadre(c) {
  var tid = UI.sub.team && own(ST.teams, UI.sub.team) ? UI.sub.team : null;
  if (tid) return teamDetail(c, ST.teams[tid]);
  var inv = Object.keys(ST.reqs).filter(function (k) { return ST.reqs[k].kind === 'team.invite'; });
  var name = h('input', { type: 'text', maxlength: 30, id: 'tfTeamName', class: 'tf-in', placeholder: 'Nome squadra', 'aria-label': 'Nome squadra' }), goal = h('input', { type: 'number', min: 5, max: 1000, value: 50, id: 'tfTeamGoal', class: 'tf-in', 'aria-label': 'Obiettivo: titoli visti insieme' });
  add(c, [h('h3', {}, ['Squadre TVA']), h('p', { class: 'tf-help' }, ['Uno spazio condiviso con le Varianti collegate: obiettivo comune, avanzamento di squadra e attivita\'. Condividi il tuo avanzamento solo quando premi il pulsante.'])]);
  if (inv.length) add(c, [h('h4', {}, ['Inviti ricevuti']), inv.map(function (k) { var r = ST.reqs[k]; return h('div', { class: 'tf-item' }, [h('b', {}, [emb(r.team.emblem) + ' ' + r.team.name]), h('span', { class: 'tf-sub' }, ['Da ' + r.from.name + ' — obiettivo ' + r.team.goal + ' titoli']), h('div', { class: 'tf-row' }, [
    btn('Entra', function () { var m = teamJoin(k); if (m) showOut('Conferma di ingresso', m, 'Invia questo codice a ' + r.from.name + ' (capo squadra) per essere aggiunto.'); UI.sub.team = r.team.id; renderAll(); }, 'tf-primary', { 'data-act': 'team-join' }), btn('Rifiuta', function () { delete ST.reqs[k]; persist(); renderAll(); }, '')])]); })]);
  var ts = Object.keys(ST.teams).map(function (k) { return ST.teams[k]; });
  add(c, [h('h4', {}, ['Le tue squadre (' + ts.length + ')']), ts.length ? ts.map(function (t) { var p = teamProgress(t); return h('button', { type: 'button', class: 'tf-item tf-link', 'data-team': t.id, onclick: function () { UI.sub.team = t.id; renderAll(); } }, [h('b', {}, [emb(t.emblem) + ' ' + t.name]), h('span', { class: 'tf-sub' }, [Object.keys(t.members).length + ' membri — ' + p.total + '/' + t.goal + ' titoli (' + p.pct + '%)'])]); }) : h('p', { class: 'tf-empty' }, ['Nessuna squadra.']),
    h('h4', {}, ['Nuova squadra']), h('label', { class: 'tf-l', for: 'tfTeamName' }, ['Nome']), name, h('label', { class: 'tf-l', for: 'tfTeamGoal' }, ['Obiettivo (titoli visti insieme)']), goal,
    btn('Crea squadra', function () { if (!ST.me.name) { toast('Prima salva il nome della tua Variante.'); return; } var t = teamNew(name.value, 0, parseInt(goal.value, 10) || 50); if (!t) { toast('Scrivi un nome per la squadra.'); return; } UI.sub.team = t.id; renderAll(); }, 'tf-primary', { id: 'tfTeamNew' })]);
}
function teamDetail(c, t) {
  var p = teamProgress(t), isOwner = t.owner === ST.vid, L = linkedList().filter(function (n) { return !own(t.members, n.vid); });
  var sel = h('select', { id: 'tfTeamInv', class: 'tf-in', 'aria-label': 'Invita una Variante collegata' }, L.map(function (n) { return h('option', { value: n.vid }, [n.name]); }));
  add(c, [btn('← Squadre', function () { UI.sub.team = null; renderAll(); }, ''), h('h3', {}, [emb(t.emblem) + ' ' + t.name]), h('div', { class: 'tf-bar', role: 'progressbar', 'aria-valuemin': 0, 'aria-valuemax': 100, 'aria-valuenow': p.pct, 'aria-label': 'Obiettivo squadra' }, [h('span', { style: 'width:' + p.pct + '%' })]),
    h('p', { class: 'tf-help', id: 'tfTeamProg' }, ['Obiettivo: ' + p.total + ' / ' + t.goal + ' titoli visti insieme (' + p.reporting + ' membri hanno condiviso il proprio avanzamento).']),
    h('h4', {}, ['Membri']), Object.keys(t.members).map(function (v) { var m = t.members[v]; return h('div', { class: 'tf-item' }, [h('b', {}, [(v === t.owner ? '👑 ' : '') + m.name + (v === ST.vid ? ' (tu)' : '')]), h('span', { class: 'tf-sub' }, [typeof m.seen === 'number' ? m.seen + ' titoli visti — aggiornato ' + fmtDate(m.ts) : 'avanzamento non condiviso']),
      isOwner && v !== ST.vid ? btn('Rimuovi', function () { if (ask('Rimuovere ' + m.name + ' dalla squadra?')) { teamKick(t.id, v); renderAll(); } }, '') : null]); }),
    h('h4', {}, ['Azioni']),
    h('p', { class: 'tf-help' }, ['“Condividi il mio avanzamento” invia SOLO il numero dei tuoi titoli visti (adesso: ' + watchedCount() + '), non quali ne' + ' voti o note.']),
    h('div', { class: 'tf-row' }, [btn('Condividi il mio avanzamento', function () { if (!ask('Condividere con la squadra il numero dei tuoi titoli visti (' + watchedCount() + ')? Nient\'altro verra\' inviato.')) return; var m = teamState(t.id, true); if (m) showOut('Aggiornamento squadra', m, 'Invia questo codice ai membri della squadra: importandolo vedranno il tuo avanzamento.'); renderAll(); }, 'tf-primary', { id: 'tfTeamShare' }),
      btn('Aggiornamento senza avanzamento', function () { var m = teamState(t.id, false); if (m) showOut('Aggiornamento squadra', m); }, '', { id: 'tfTeamSync' })]),
    isOwner ? (L.length ? h('div', { class: 'tf-row' }, [sel, btn('Invita', function () { var m = teamInvite(t.id, sel.value); if (m) showOut('Invito squadra', m, 'Invia questo invito alla Variante scelta.'); }, '', { id: 'tfTeamInvite' })]) : h('p', { class: 'tf-empty' }, ['Nessuna Variante collegata da invitare (serve prima il Legame Nexus).'])) : null,
    h('h4', {}, ['Attivita\' recente']), h('ul', { class: 'tf-log' }, t.log.slice(-10).reverse().map(function (l) { return h('li', {}, [fmtDate(l.ts) + ' — ' + l.text]); })),
    btn(isOwner ? 'Elimina squadra (solo da questo dispositivo)' : 'Lascia squadra', function () { if (ask((isOwner ? 'Eliminare la squadra da questo dispositivo?' : 'Lasciare la squadra?') + ' I tuoi dati personali non vengono toccati.')) { teamLeave(t.id); UI.sub.team = null; renderAll(); } }, 'tf-danger')]);
}

/* --- Serate --- */
function evEl(e) {
  var inP = e.when > now() - 3 * 36e5, mine = e.host === ST.vid ? 'Organizzi tu' : 'Organizza ' + e.hostName;
  return h('button', { type: 'button', class: 'tf-item tf-link' + (e.cancelled ? ' tf-cancelled' : ''), 'data-ev': e.id, onclick: function () { UI.sub.ev = e.id; renderAll(); } }, [h('b', {}, ['🍿 ' + e.title + (e.cancelled ? ' (annullata)' : '')]), h('span', { class: 'tf-sub' }, [fmtDate(e.when) + ' — ' + fmtIn(e.when) + ' — ' + mine])]);
}
function viewSerate(c) {
  var id = UI.sub.ev && own(ST.evenings, UI.sub.ev) ? UI.sub.ev : null; if (id) return evDetail(c, ST.evenings[id]);
  var all = Object.keys(ST.evenings).map(function (k) { return ST.evenings[k]; }).sort(function (a, b) { return a.when - b.when; });
  var up = all.filter(function (e) { return e.when > now() - 3 * 36e5; }), past = all.filter(function (e) { return e.when <= now() - 3 * 36e5; }).reverse();
  var ti = h('input', { type: 'text', maxlength: 60, id: 'tfEvTitle', class: 'tf-in', placeholder: 'Titolo della serata', 'aria-label': 'Titolo' });
  var it = h('select', { id: 'tfEvItem', class: 'tf-in', 'aria-label': 'Titolo da guardare' }, [h('option', { value: '' }, ['— da decidere —'])].concat(titles().map(function (t) { return h('option', { value: t.id }, ['N°' + t.id + ' ' + t.name]); })));
  var d = new Date(now() + 864e5 * 2); d.setHours(21, 0, 0, 0); var pad = function (n) { return ('0' + n).slice(-2); };
  var wh = h('input', { type: 'datetime-local', id: 'tfEvWhen', class: 'tf-in', value: d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + 'T21:00', 'aria-label': 'Data e ora' });
  var pl = h('input', { type: 'text', maxlength: 60, id: 'tfEvPlace', class: 'tf-in', placeholder: 'Luogo (facoltativo)', 'aria-label': 'Luogo' }), nt = h('input', { type: 'text', maxlength: 200, id: 'tfEvNote', class: 'tf-in', placeholder: 'Nota (facoltativa)', 'aria-label': 'Nota' });
  var L = linkedList(), chks = L.map(function (n) { var i = h('input', { type: 'checkbox', value: n.vid }); return h('label', { class: 'tf-chk' }, [i, ' ' + n.name]); });
  add(c, [h('h3', {}, ['Serate Marvel']), h('p', { class: 'tf-help' }, ['Organizza una visione insieme: data, titolo, invitati e risposte. Funziona anche offline.']), h('h4', {}, ['In programma (' + up.length + ')']), up.length ? up.map(evEl) : h('p', { class: 'tf-empty' }, ['Nessuna serata in programma.']),
    past.length ? h('details', {}, [h('summary', {}, ['Passate (' + past.length + ')']), past.map(evEl)]) : null,
    h('h4', {}, ['Nuova serata']), ti, it, wh, pl, nt, h('fieldset', { class: 'tf-fs' }, [h('legend', {}, ['Invitati (Varianti collegate)']), L.length ? chks : h('p', { class: 'tf-empty' }, ['Nessuna Variante collegata: puoi creare la serata e invitare piu\' tardi.'])]),
    btn('Crea serata', function () {
      if (!ST.me.name) { toast('Prima salva il nome della tua Variante.'); return; }
      var tt = ti.value || (it.value ? titleName(it.value) : ''); var e = evNew({ title: tt, item: it.value, when: wh.value, place: pl.value, note: nt.value, guests: chks.map(function (l) { return l.firstChild; }).filter(function (i) { return i.checked; }).map(function (i) { return i.value; }) });
      if (!e) { toast('Servono un titolo e una data valida.'); return; } UI.sub.ev = e.id; renderAll();
    }, 'tf-primary', { id: 'tfEvNew' })]);
}
function evDetail(c, e) {
  var host = e.host === ST.vid, g = Object.keys(e.guests).map(function (v) { return [v, e.guests[v]]; }), cnt = { si: 0, forse: 0, no: 0, 'in attesa': 0 }; g.forEach(function (x) { cnt[x[1].rsvp] = (cnt[x[1].rsvp] || 0) + 1; });
  add(c, [btn('← Serate', function () { UI.sub.ev = null; renderAll(); }, ''), h('h3', {}, ['🍿 ' + e.title]), h('p', {}, [fmtDate(e.when) + ' — ' + (e.cancelled ? 'ANNULLATA' : fmtIn(e.when))]), e.item ? h('p', {}, ['Si guarda: N°' + e.item + ' ' + titleName(e.item)]) : null, e.place ? h('p', {}, ['📍 ' + e.place]) : null, e.note ? h('p', { class: 'tf-sub' }, [e.note]) : null, h('p', { class: 'tf-sub' }, [host ? 'Organizzi tu' : 'Organizzata da ' + e.hostName])]);
  if (host) add(c, [h('p', { id: 'tfEvCounts' }, ['Risposte: ' + cnt.si + ' si\', ' + cnt.forse + ' forse, ' + cnt.no + ' no, ' + cnt['in attesa'] + ' in attesa.']), g.map(function (x) { return h('div', { class: 'tf-item' }, [h('b', {}, [x[1].name]), h('span', { class: 'tf-sub' }, [x[1].rsvp])]); }),
    h('div', { class: 'tf-row' }, [e.cancelled ? null : btn('Invia inviti', function () { var m = evInviteMsg(e.id); if (m) showOut('Invito alla serata', m, 'Invia questo codice agli invitati. Importandolo, potranno rispondere.'); }, 'tf-primary', { id: 'tfEvSend' }), e.cancelled ? null : btn('Annulla serata', function () { if (ask('Annullare la serata? Gli invitati verranno avvisati con un codice.')) { var m = evCancel(e.id); if (m) showOut('Annullamento serata', m); renderAll(); } }, 'tf-danger')])]);
  else add(c, [h('p', { id: 'tfEvMine' }, ['La tua risposta: ' + e.mine]), e.cancelled ? null : h('div', { class: 'tf-row' }, [['si', 'Ci sono'], ['forse', 'Forse'], ['no', 'Non posso']].map(function (r) { return btn(r[1], function () { var m = evRsvp(e.id, r[0]); if (m) showOut('Risposta alla serata', m, 'Invia questo codice a ' + e.hostName + ' per comunicare la tua risposta.'); renderAll(); }, e.mine === r[0] ? 'tf-primary' : '', { 'data-rsvp': r[0] }); }))]);
  add(c, [h('div', { class: 'tf-row' }, [btn('Aggiungi al calendario (.ics)', function () { var t = evIcs(e.id); if (t) dl('serata-marvel.ics', t, 'text/calendar'); }, '', { id: 'tfEvIcs' }), btn('Elimina dal dispositivo', function () { if (ask('Eliminare la serata da questo dispositivo?')) { evDelete(e.id); UI.sub.ev = null; renderAll(); } }, 'tf-danger')])]);
}

/* --- Quiz e Duelli --- */
function runGame(g, box) {
  var i = 0, ok = 0, t0 = now(), qs = g.qs;
  function step() {
    box.textContent = '';
    if (i >= qs.length) {
      var ms = now() - t0; g.done(ok, qs.length, ms);
      add(box, [h('h3', {}, ['Risultato: ' + ok + ' / ' + qs.length]), h('p', {}, ['Tempo: ' + Math.round(ms / 1000) + ' s']), btn('Chiudi', function () { UI.game = null; renderAll(); }, 'tf-primary', { id: 'tfGameEnd' })]); return;
    }
    var q = qs[i], fb = h('p', { class: 'tf-fb', 'aria-live': 'polite', id: 'tfFb' });
    add(box, [h('p', { class: 'tf-sub' }, ['Domanda ' + (i + 1) + ' di ' + qs.length]), h('p', { class: 'tf-q', id: 'tfQ' }, [q.text]), h('div', { class: 'tf-opts' }, q.opts.map(function (o, k) {
      return h('button', { type: 'button', class: 'reset-btn tf-btn tf-opt', 'data-k': k, onclick: function (ev) {
        var bs = box.querySelectorAll('.tf-opt'); bs.forEach(function (b) { b.disabled = true; }); var good = k === q.ans; if (good) ok++;
        bs[q.ans].classList.add('tf-good'); if (!good) bs[k].classList.add('tf-bad'); fb.textContent = (good ? 'Esatto! ' : 'Non proprio. ') + q.ex;
        add(box, [btn(i + 1 < qs.length ? 'Avanti' : 'Vedi il risultato', function () { i++; step(); }, 'tf-primary', { id: 'tfNext' })]); document.getElementById('tfNext').focus();
      } }, [o]);
    })), fb]);
  }
  step();
}
function viewSfide(c) {
  if (UI.game) { var box = h('div', { id: 'tfGame' }); add(c, [box]); runGame(UI.game, box); return; }
  var mk = function (label, n, fn, id) { return btn(label, function () { var qs = genQuiz((Math.floor(Math.random() * 4294967295) >>> 0) || 1, n); if (qs.length < n) { toast('Dati del catalogo insufficienti per il quiz.'); return; } fn(qs); }, '', { id: id }); };
  var ds = Object.keys(ST.duels).map(function (k) { return ST.duels[k]; }).sort(function (a, b) { return b.created - a.created; });
  add(c, [h('h3', {}, ['Quiz e Duelli']), h('p', { class: 'tf-help' }, ['Domande generate dal catalogo dell\'app (anni di uscita, interpreti, livelli di potere, curiosita\'). Il quiz non cambia XP, badge o progressi.']),
    h('h4', {}, ['Quiz singolo']), ST.best.n ? h('p', { class: 'tf-sub', id: 'tfBest' }, ['Miglior risultato: ' + ST.best.solo + ' / ' + ST.best.n]) : null,
    h('div', { class: 'tf-row' }, [5, 10, 15].map(function (n) { return mk(n + ' domande', n, function (qs) { UI.game = { qs: qs, done: function (ok, tot) { soloRecord(ok, tot); } }; renderAll(); }, 'tfSolo' + n); })),
    h('h4', {}, ['Duelli']), h('p', { class: 'tf-help' }, ['Lancia una sfida: tu e il tuo avversario rispondete alle stesse domande, anche in momenti diversi. Vince chi fa piu\' punti, a parita\' chi e\' piu\' veloce.']),
    btn('Lancia un duello (10 domande)', function () { if (!ST.me.name) { toast('Prima salva il nome della tua Variante.'); return; } var d = duelNew(10); if (!d) { toast('Dati del catalogo insufficienti.'); return; } showOut('Sfida a duello', duelChallengeMsg(d.id), 'Invia la sfida a una Variante collegata. Gioca anche tu: poi invia il tuo risultato.'); renderAll(); }, 'tf-primary', { id: 'tfDuelNew' }),
    ds.length ? ds.map(function (d) {
      var b = duelBoard(d), mine = d.scores[ST.vid];
      return h('div', { class: 'tf-item', 'data-duel': d.id }, [h('b', {}, ['Duello di ' + (d.by === ST.vid ? 'te' : d.byName) + ' — ' + d.n + ' domande']), h('span', { class: 'tf-sub' }, [fmtDate(d.created)]),
        b.length ? h('ol', { class: 'tf-board' }, b.map(function (x) { return h('li', {}, [x.name + (x.vid === ST.vid ? ' (tu)' : '') + ': ' + x.score + '/' + x.total + ' in ' + Math.round(x.ms / 1000) + ' s']); })) : h('span', { class: 'tf-sub' }, ['Nessun risultato ancora.']),
        h('div', { class: 'tf-row' }, [!mine ? btn('Gioca', function () { var qs = genQuiz(d.seed | 0, d.n); if (quizHash(qs) !== d.qh) { toast('Versione dell\'app diversa: duello non giocabile.'); return; } UI.game = { qs: qs, done: function (ok, tot, ms) { var m = duelRecord(d.id, ok, tot, ms); if (m) setTimeout(function () { showOut('Il tuo risultato', m, 'Invia questo codice a ' + (d.by === ST.vid ? 'chi hai sfidato' : d.byName) + ' per registrare il tuo punteggio.'); }, 0); } }; renderAll(); }, 'tf-primary', { 'data-act': 'duel-play' }) : null,
          mine ? btn('Rigenera codice risultato', function () { var m = mkMsg('duel.result', { id: d.id, score: mine.score, total: mine.total, ms: mine.ms }); showOut('Il tuo risultato', m); }, '', { 'data-act': 'duel-res' }) : null,
          d.by === ST.vid ? btn('Rigenera sfida', function () { showOut('Sfida a duello', duelChallengeMsg(d.id)); }, '') : null,
          btn('Elimina', function () { if (ask('Eliminare il duello da questo dispositivo?')) { delete ST.duels[d.id]; persist(); renderAll(); } }, '')])]);
    }) : h('p', { class: 'tf-empty' }, ['Nessun duello.'])]);
}

/* --- Archivio condiviso --- */
function viewArchivio(c) {
  var out = Object.keys(ST.shared.out).map(function (k) { return ST.shared.out[k]; }).sort(function (a, b) { return b.ts - a.ts; }), inn = Object.keys(ST.shared.inn).map(function (k) { return ST.shared.inn[k]; }).sort(function (a, b) { return b.ts - a.ts; });
  var ti = h('input', { type: 'text', maxlength: 40, id: 'tfPkTitle', class: 'tf-in', placeholder: 'Titolo del pacchetto', 'aria-label': 'Titolo del pacchetto' }), de = h('input', { type: 'text', maxlength: 120, id: 'tfPkDesc', class: 'tf-in', placeholder: 'Descrizione (facoltativa)', 'aria-label': 'Descrizione' });
  var list = titles().map(function (t) { var i = h('input', { type: 'checkbox', value: t.id }); return h('label', { class: 'tf-chk' }, [i, ' N°' + t.id + ' ' + t.name]); });
  var seenMap = {}; try { seenMap = JSON.parse(localStorage.getItem('marvel-ultimate-timeline-watched') || '{}'); } catch (e) {}
  add(c, [h('h3', {}, ['Archivio condiviso']), h('p', { class: 'tf-help' }, ['Condividi selezioni che scegli tu. Non vengono mai condivisi Diario TVA, note, voti, preferiti o progressi: un pacchetto contiene solo i numeri dei titoli e il testo che scrivi qui.']),
    h('h4', {}, ['Crea un pacchetto']), ti, de, h('details', {}, [h('summary', {}, ['Scegli i titoli (max 12)']), h('div', { class: 'tf-scroll', id: 'tfPkList' }, list)]),
    h('div', { class: 'tf-row' }, [btn('Condividi selezione', function () {
      var ids = list.map(function (l) { return l.firstChild; }).filter(function (i) { return i.checked; }).map(function (i) { return i.value; });
      if (ids.length > 12) { toast('Massimo 12 titoli.'); return; } var p = pkgPicks(ti.value, de.value, ids); if (!p) { toast('Servono un titolo e almeno un titolo selezionato.'); return; } showOut('Pacchetto «' + p.title + '»', pkgMsg(p.id)); renderAll();
    }, 'tf-primary', { id: 'tfPkMake' }), btn('Condividi il mio ordine Timeline', function () {
      if (!customOrderIds().length) { toast('Non hai un ordine Timeline personalizzato da condividere.'); return; } if (!ask('Condividere l\'elenco dei titoli del tuo ordine Timeline personalizzato (solo i numeri, in ordine)?')) return; var p = pkgOrder(ti.value); if (p) { showOut('Pacchetto «' + p.title + '»', pkgMsg(p.id)); renderAll(); }
    }, '', { id: 'tfPkOrder' })]),
    out.length ? h('details', {}, [h('summary', {}, ['Pacchetti che hai creato (' + out.length + ')']), out.map(function (p) { return h('div', { class: 'tf-item' }, [h('b', {}, [p.title]), h('span', { class: 'tf-sub' }, [p.items.length + ' titoli — ' + (p.kind === 'order' ? 'ordine Timeline' : 'selezione')]), h('div', { class: 'tf-row' }, [btn('Rigenera codice', function () { showOut('Pacchetto «' + p.title + '»', pkgMsg(p.id)); }, ''), btn('Elimina', function () { delete ST.shared.out[p.id]; persist(); renderAll(); }, '')])]); })]) : null,
    h('h4', {}, ['Ricevuti (' + inn.length + ')']), inn.length ? inn.map(function (p) {
      return h('details', { class: 'tf-item', 'data-pkg': p.id }, [h('summary', {}, [p.title + ' — da ' + p.fromName]), p.desc ? h('p', { class: 'tf-sub' }, [p.desc]) : null,
        h('ol', { class: 'tf-pk' }, p.items.map(function (id) { return h('li', {}, ['N°' + id + ' ' + titleName(id) + (seenMap[id] === true ? ' ✓ gia\' visto' : '')]); })), btn('Rimuovi', function () { delete ST.shared.inn[p.id]; persist(); renderAll(); }, '')]);
    }) : h('p', { class: 'tf-empty' }, ['Nessun pacchetto ricevuto. I pacchetti arrivano da Varianti collegate e non modificano i tuoi dati.'])]);
}

/* --- Centro Comunicazioni --- */
var KICON = { nexus: '🔗', team: '🛡️', ev: '🍿', duel: '🎯', share: '🗂️', sys: 'ℹ️' };
function reminders() {
  var r = [], t = now(); Object.keys(ST.evenings).forEach(function (k) { var e = ST.evenings[k]; if (!e.cancelled && e.when > t && e.when - t < 864e5) r.push({ id: 'r_' + e.id, k: 'ev', ts: e.when, read: true, rem: true, text: 'Promemoria: serata «' + e.title + '» ' + fmtIn(e.when) + '.', ref: { tab: 'serate', id: e.id } }); });
  return r;
}
function viewCom(c) {
  var f = UI.sub.filter || '', all = reminders().concat(ST.inbox.slice().reverse()).filter(function (n) { return !f || n.k === f; });
  var fs = h('select', { id: 'tfFilter', class: 'tf-in', 'aria-label': 'Filtra', onchange: function () { UI.sub.filter = fs.value; renderAll(); } }, [h('option', { value: '' }, ['Tutte'])].concat(Object.keys(KICON).map(function (k) { return h('option', { value: k }, [k]); }))); fs.value = f;
  add(c, [h('h3', {}, ['Centro Comunicazioni']), h('p', { class: 'tf-help' }, ['Notifiche e attivita\' condivise, solo dentro l\'app: nessuna notifica push e nessun invio automatico.']), fs,
    CLOUD.enabled() ? btn('Controlla nuovi messaggi (cloud)', function () { CLOUD.poll().then(function (res) { toast(res.length ? res.length + ' messaggi elaborati.' : 'Nessun nuovo messaggio.'); renderAll(); }, function (e) { toast('Controllo cloud NON riuscito (' + ((e && (e.code || e.message)) || 'errore') + ').'); }); }, '', { id: 'tfCloudPoll' }) : null,
    h('div', { class: 'tf-row' }, [btn('Segna tutto come letto', function () { ST.inbox.forEach(function (n) { n.read = true; }); persist(); renderAll(); }, '', { id: 'tfReadAll' }), btn('Svuota', function () { if (ask('Eliminare tutte le comunicazioni? Le richieste in sospeso restano.')) { ST.inbox = []; persist(); renderAll(); } }, '')]),
    all.length ? all.map(function (n) {
      return h('div', { class: 'tf-item tf-note' + (n.read ? '' : ' tf-unread'), 'data-note': n.id }, [h('span', {}, [(KICON[n.k] || '') + ' ' + n.text]), h('span', { class: 'tf-sub' }, [fmtDate(n.ts)]),
        h('div', { class: 'tf-row' }, [n.ref && n.ref.tab ? btn('Apri', function () { n.read = true; persist(); UI.tab = n.ref.tab; if (n.ref.tab === 'squadre') UI.sub.team = n.ref.id || null; if (n.ref.tab === 'serate') UI.sub.ev = n.ref.id || null; renderAll(); }, '') : null, !n.rem && !n.read ? btn('Letto', function () { n.read = true; persist(); renderAll(); }, '') : null, !n.rem ? btn('Elimina', function () { ST.inbox = ST.inbox.filter(function (x) { return x.id !== n.id; }); persist(); renderAll(); }, '') : null])]);
    }) : h('p', { class: 'tf-empty' }, ['Nessuna comunicazione.'])]);
}

/* --- guscio --- */
var VIEWS = { varianti: viewVarianti, nexus: viewNexus, squadre: viewSquadre, serate: viewSerate, sfide: viewSfide, archivio: viewArchivio, com: viewCom };
function updateBadges() {
  var u = unreadCount(); var b = document.getElementById('tfBadge'); if (b) { b.textContent = u ? String(u) : ''; b.hidden = !u; }
  var tb = document.getElementById('tfTab-com'); if (tb) { var s = tb.querySelector('.tf-n'); if (s) { s.textContent = u ? String(u) : ''; s.hidden = !u; } }
  var tn = document.getElementById('tfTab-nexus'); if (tn) { var s2 = tn.querySelector('.tf-n'); if (s2) { var q = Object.keys(ST.reqs).filter(function (k) { return ST.reqs[k].kind === 'nx.invite'; }).length; s2.textContent = q ? String(q) : ''; s2.hidden = !q; } }
}
function renderAll() {
  if (!UI.root || UI.root.hidden) { updateBadges(); return; }
  var c = document.getElementById('tfBody'), y = c.scrollTop; var focusId = document.activeElement && document.activeElement.id; c.textContent = '';
  var open = document.getElementById('tfImp') ? document.getElementById('tfImp').open : false, txt = document.getElementById('tfImpText') ? document.getElementById('tfImpText').value : '';
  UI.root.querySelectorAll('.tf-tab').forEach(function (b) { var on = b.getAttribute('data-tab') === UI.tab; b.setAttribute('aria-selected', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; });
  var imp = importBar(); imp.open = open; imp.querySelector('textarea').value = txt; c.appendChild(imp);
  var sec = h('section', { id: 'tfPanel-' + UI.tab, role: 'tabpanel', 'aria-labelledby': 'tfTab-' + UI.tab }); c.appendChild(sec);
  try { VIEWS[UI.tab](sec); } catch (e) { sec.textContent = 'Errore di visualizzazione: i dati non sono stati toccati.'; if (window.console) console.error('TVA Friends:', e); }
  renderOut(); updateBadges(); c.scrollTop = y;
  if (!storeOk) toast('Spazio del browser pieno: le ultime modifiche Friends NON sono salvate. Esporta un backup e libera spazio.');
  if (focusId) { var f = document.getElementById(focusId); if (f && f.focus) try { f.focus({ preventScroll: true }); } catch (e2) {} }
}
function build() {
  var tabs = h('div', { class: 'tf-tabs', role: 'tablist', 'aria-label': 'Moduli TVA Friends' }, TABS.map(function (t) { return h('button', { type: 'button', role: 'tab', class: 'tf-tab', id: 'tfTab-' + t[0], 'data-tab': t[0], 'aria-controls': 'tfPanel-' + t[0], onclick: function () { UI.tab = t[0]; UI.game = null; renderAll(); } }, [h('span', { 'aria-hidden': 'true' }, [t[1]]), h('span', { class: 'tf-tl' }, [t[2]]), h('span', { class: 'tf-n', hidden: true })]); }));
  tabs.addEventListener('keydown', function (ev) { var k = ev.key; if (k !== 'ArrowRight' && k !== 'ArrowLeft') return; var i = TABS.map(function (t) { return t[0]; }).indexOf(UI.tab); i = (i + (k === 'ArrowRight' ? 1 : TABS.length - 1)) % TABS.length; UI.tab = TABS[i][0]; UI.game = null; renderAll(); document.getElementById('tfTab-' + UI.tab).focus(); ev.preventDefault(); });
  UI.root = h('div', { id: 'tfRoot', class: 'tf-root', role: 'dialog', 'aria-modal': 'true', 'aria-label': 'TVA Friends', hidden: true }, [
    h('div', { class: 'tf-head' }, [h('b', {}, ['👥 TVA Friends']), h('span', { class: 'tf-off', id: 'tfNet', hidden: true }, ['offline']), btn('Chiudi', closeUI, '', { id: 'tfClose', 'aria-label': 'Chiudi TVA Friends' })]), tabs,
    h('div', { id: 'tfBody', class: 'tf-body' }), h('div', { id: 'tfOut', class: 'tf-out', hidden: true }), h('p', { id: 'tfToast', class: 'tf-toast', role: 'status', 'aria-live': 'polite', hidden: true })]);
  document.body.appendChild(UI.root);
  UI.root.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') { closeUI(); ev.stopPropagation(); } });
  function net() { var n = document.getElementById('tfNet'); if (n) n.hidden = navigator.onLine !== false; } window.addEventListener('online', net); window.addEventListener('offline', net); net();
}
function openUI(tab) {
  load(); purgeExpired(); if (!UI.root) build(); if (tab && VIEWS[tab]) UI.tab = tab; UI.opener = document.activeElement; UI.root.hidden = false; document.documentElement.classList.add('tf-lock'); renderAll(); document.getElementById('tfClose').focus();
}
function closeUI() { if (!UI.root) return; UI.root.hidden = true; UI.game = null; document.documentElement.classList.remove('tf-lock'); updateBadges(); if (UI.opener && UI.opener.focus) try { UI.opener.focus(); } catch (e) {} }
