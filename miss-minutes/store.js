/* Miss Minutes — cronologia locale (localStorage). Limiti rigidi per non gonfiare lo spazio; mai inviata altrove. */
(function (root) {
  'use strict';
  var KEY = 'marvel-ultimate-timeline-miss-minutes-v1', MAX_S = 40, MAX_M = 120, MAX_T = 4000;
  function create(storage) {
    var st = { v: 1, sessions: [], active: null, prefs: { online: false, consent: false, spoiler: true, voice: false, local: true, memory: true, cite: true, length: 'normal', speed: 'normal', diag: false, lookup: true } };
    try { var r = JSON.parse(storage.getItem(KEY) || 'null'); if (r && r.v === 1 && Array.isArray(r.sessions)) { st.sessions = r.sessions.filter(function (s) { return s && typeof s.id === 'string' && Array.isArray(s.messages); }).slice(0, MAX_S); st.active = typeof r.active === 'string' ? r.active : null; st.prefs = Object.assign(st.prefs, r.prefs || {}); } } catch (e) {}
    var ok = true;
    function save() {
      /* mm6: nessuna cancellazione silenziosa. Se lo spazio e' pieno si prova a salvare le sole conversazioni piu' recenti
         in una copia di sicurezza separata, ma l'elenco in memoria non viene mai ridotto: l'interfaccia avvisa l'utente. */
      try { storage.setItem(KEY, JSON.stringify(st)); ok = true; return true; } catch (e) { ok = false; return false; }
    }
    function find(id) { for (var i = 0; i < st.sessions.length; i++) if (st.sessions[i].id === id) return st.sessions[i]; return null; }
    return {
      state: st, save: save, usable: function () { return ok; },
      current: function () { return find(st.active); },
      fresh: function (title) { var s = { id: String(Date.now()) + Math.random().toString(36).slice(2, 6), title: String(title || 'Nuova chat').slice(0, 60), at: Date.now(), messages: [], last: [] }; st.sessions.unshift(s); st.sessions = st.sessions.slice(0, MAX_S); st.active = s.id; return s; },
      push: function (s, m) { s.messages.push({ role: m.role, text: String(m.text).slice(0, MAX_T), refs: (m.refs || []).slice(0, 8), tag: m.tag || '', personal: m.personal === true, vf: m.vf || null, srcs: (m.srcs || []).slice(0, 6), flair: m.flair ? String(m.flair).slice(0, 200) : '', at: Date.now() });
        s.at = Date.now(); if (s.messages.length > MAX_M) s.messages = s.messages.slice(-MAX_M); },
      pop: function (s) { return s.messages.pop(); },
      rename: function (id, title) { var s = find(id), t = String(title || '').replace(/\s+/g, ' ').trim().slice(0, 60); if (!s || !t) return false; s.title = t; return true; },
      open: function (id) { if (find(id)) { st.active = id; return true; } return false; },
      remove: function (id) { st.sessions = st.sessions.filter(function (s) { return s.id !== id; }); if (st.active === id) st.active = null; },
      clear: function () { st.sessions = []; st.active = null; },
      key: KEY
    };
  }
  var API = { create: create, KEY: KEY };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.MMStore = API;
})(typeof globalThis !== 'undefined' ? globalThis : this);
