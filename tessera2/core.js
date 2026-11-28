/* Tessera TVA 3.0 — nucleo puro (testabile in Node): schema additivo `tessera-v2`, validazione, catalogo dei 12 sfondi animati e condizioni di sblocco.
   Nessun accesso al DOM, nessuna rete, nessun XP. Chiavi esistenti MAI toccate: i dati nuovi vivono solo in `marvel-ultimate-timeline-tessera-v2`. */
(function (root) {
  'use strict';
  var KEY = 'marvel-ultimate-timeline-tessera-v2', SLOTS = 6, TITLE_MAX = 40;

  /* Condizioni approvate dall'utente (28/11/2026, 17:23). Solo dati effettivamente registrati nell'app. Sblocchi retroattivi e permanenti; nessun XP. */
  var BGS = [
    { id: 'sacra-linea', n: 'Sacra Linea Temporale', cond: { k: 'free' } },
    { id: 'terminale-tva', n: 'Terminale TVA', cond: { k: 'free' } },
    { id: 'multiverso', n: 'Multiverso', cond: { k: 'free' } },
    { id: 'archivio-dorato', n: 'Archivio Dorato', cond: { k: 'free' } },
    { id: 'yggdrasil', n: 'Yggdrasil', cond: { k: 'level', n: 10 } },
    { id: 'dimensione-specchio', n: 'Dimensione Specchio', cond: { k: 'dossier', n: 50 } },
    { id: 'dimensione-oscura', n: 'Dimensione Oscura', cond: { k: 'level', n: 15 } },
    { id: 'regno-quantico', n: 'Regno Quantico', cond: { k: 'pct', n: 25 } },
    { id: 'bifrost', n: 'Bifrost', cond: { k: 'uni', n: 10 } },
    { id: 'il-vuoto', n: 'Il Vuoto', cond: { k: 'pct', n: 50 } },
    { id: 'spider-verse', n: 'Spider-Verse', cond: { k: 'spider', n: 10 } },
    { id: 'infinito', n: 'Infinito', cond: { k: 'pct', n: 100 } }
  ];
  var BG_BY = {}; BGS.forEach(function (b) { BG_BY[b.id] = b; });
  var CATEGORIES = ['carta', 'identita', 'rango', 'titolo', 'preferiti', 'statistiche', 'emblemi', 'vetrina'];   /* D6: controlli di visibilità (predisposizione, nessuna rete) */

  function isObj(o) { return !!o && typeof o === 'object' && !Array.isArray(o); }
  function defaults() {
    var pv = {}; CATEGORIES.forEach(function (c) { pv[c] = 'p'; });
    return { v: 1, vetrina: null, sfondoAnim: null, anim: 'auto', titolo: { modo: 'ufficiale', testo: '' }, origine: { univ: '', uid: '' }, pref: { univ: '', ch: '' }, privacy: pv, sbloccati: {}, classica: false, ts: 0 };
  }
  /* Titolo personale (D5): ≤ 40 caratteri (punti di codice), senza caratteri di controllo o di direzione, spazi normalizzati; mai HTML (si usa solo textContent). */
  function validTitle(s) {
    if (typeof s !== 'string') return '';
    s = s.replace(/[\u0000-\u001f\u007f-\u009f\u200b-\u200f\u2028-\u202e\u2066-\u2069\ufeff]/g, ' ').replace(/\s+/g, ' ').trim();
    var cp = Array.from(s); if (cp.length > TITLE_MAX) s = cp.slice(0, TITLE_MAX).join('').trim();
    return s;
  }
  var ITEM_ID = /^[a-z0-9][a-z0-9-]{0,47}$/;
  function validItem(it) {
    if (!isObj(it)) return null;
    if (it.t === 'emblema') { var n = Number(String(it.id).replace(/^e/, '')); return isFinite(n) && n >= 0 && n < 56 && Math.floor(n) === n ? { t: 'emblema', id: 'e' + n } : null; }
    if ((it.t === 'badge' || it.t === 'ricompensa') && typeof it.id === 'string' && ITEM_ID.test(it.id)) return { t: it.t, id: it.id };
    return null;
  }
  function cleanName(s) { return validTitle(s).slice(0, 60); }
  function sane(o) {
    var s = defaults(); if (!isObj(o)) return s;
    if (Array.isArray(o.vetrina)) { var seen = {}; s.vetrina = []; for (var i = 0; i < SLOTS; i++) { var it = validItem(o.vetrina[i]); if (it && !seen[it.t + ':' + it.id]) { seen[it.t + ':' + it.id] = 1; s.vetrina.push(it); } else s.vetrina.push(null); } }
    if (typeof o.sfondoAnim === 'string' && BG_BY[o.sfondoAnim]) s.sfondoAnim = o.sfondoAnim;
    if (o.anim === 'statico' || o.anim === 'off' || o.anim === 'auto') s.anim = o.anim;
    if (isObj(o.titolo)) { if (o.titolo.modo === 'personale') s.titolo.modo = 'personale'; s.titolo.testo = validTitle(o.titolo.testo); if (s.titolo.modo === 'personale' && !s.titolo.testo) s.titolo.modo = 'ufficiale'; }
    if (isObj(o.origine)) { s.origine.univ = cleanName(o.origine.univ); s.origine.uid = typeof o.origine.uid === 'string' && ITEM_ID.test(o.origine.uid) ? o.origine.uid : ''; }
    if (isObj(o.pref)) { s.pref.univ = typeof o.pref.univ === 'string' && ITEM_ID.test(o.pref.univ) ? o.pref.univ : ''; s.pref.ch = typeof o.pref.ch === 'string' && ITEM_ID.test(o.pref.ch) ? o.pref.ch : ''; }
    if (isObj(o.privacy)) CATEGORIES.forEach(function (c) { if (o.privacy[c] === 'a') s.privacy[c] = 'a'; });
    if (isObj(o.sbloccati)) Object.keys(o.sbloccati).forEach(function (k) { if (BG_BY[k] && BG_BY[k].cond.k !== 'free' && typeof o.sbloccati[k] === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(o.sbloccati[k])) s.sbloccati[k] = o.sbloccati[k]; });
    s.classica = o.classica === true;
    s.ts = typeof o.ts === 'number' && isFinite(o.ts) && o.ts > 0 ? Math.floor(o.ts) : 0;
    return s;
  }
  /* Vetrina effettiva: se l'utente non l'ha mai configurata, i 3 distintivi già salvati (tessera-look.b) sono i primi tre slot (D3: configurazioni precedenti preservate). */
  function effVetrina(s, lookB) {
    if (Array.isArray(s.vetrina)) return s.vetrina.slice(0, SLOTS);
    var v = []; (Array.isArray(lookB) ? lookB : []).slice(0, 3).forEach(function (b) { var it = validItem({ t: 'badge', id: b }); if (it) v.push(it); });
    while (v.length < SLOTS) v.push(null); return v;
  }

  /* ---- condizioni ---- */
  function evalCond(c, snap) {
    if (c.k === 'free') return { ok: true, have: 1, need: 1, pend: false };
    var have = snap ? snap[c.k] : null;
    if (have === null || have === undefined) return { ok: false, have: null, need: c.n, pend: true };   /* dato non ancora disponibile: né sbloccato né revocato */
    have = Number(have) || 0; return { ok: have >= c.n, have: Math.min(have, c.n * 1000), need: c.n, pend: false };
  }
  function isFree(b) { return b.cond.k === 'free'; }
  function isUnlocked(s, id) { var b = BG_BY[id]; return !!b && (isFree(b) || !!s.sbloccati[id]); }
  /* Valutazione retroattiva e permanente: uno sfondo sbloccato non viene mai richiuso, anche se i dati scendono. Ritorna { state, newly } senza mutare l'input. */
  function evaluate(s, snap, today) {
    var out = JSON.parse(JSON.stringify(s)), newly = [];
    BGS.forEach(function (b) { if (isFree(b) || out.sbloccati[b.id]) return; var r = evalCond(b.cond, snap); if (r.ok) { out.sbloccati[b.id] = today; newly.push(b.id); } });
    return { state: out, newly: newly };
  }
  var LBL = { level: 'Livello', dossier: 'Dossier verificati esplorati', pct: 'Timeline completata', uni: 'Universi verificati esplorati', spider: 'Identità verificate legate a Spider-Man esplorate' };
  function reqText(c) {
    if (c.k === 'free') return 'Disponibile subito';
    if (c.k === 'level') return 'Raggiungi il livello ' + c.n;
    if (c.k === 'pct') return 'Completa il ' + c.n + '% della Timeline';
    if (c.k === 'dossier') return 'Esplora ' + c.n + ' dossier verificati';
    if (c.k === 'uni') return 'Esplora ' + c.n + ' universi verificati';
    if (c.k === 'spider') return 'Esplora ' + c.n + ' identità verificate legate a Spider-Man';
    return '';
  }
  function progText(c, r) { if (c.k === 'free') return ''; if (r.pend) return 'Calcolo in corso…'; return Math.min(r.have, r.need) + ' / ' + r.need + (c.k === 'pct' ? ' %' : ''); }

  /* ---- conteggi Atlas (stessa regola di a5.js `eligible`: solo dossier effettivi e verificati; «fonte singola» e segnaposto esclusi) ---- */
  function eligible(v) { return !!v && v.k !== 'c' && v.t !== 'h' && v.t !== 'm' && !v.s && !v.sv && (!v.db || v.lv === 'A' || v.lv === 'B' || v.lv === 'C'); }
  function canon(id, BY, red) { var r = red && red[id]; return r && BY[r] ? r : id; }
  function atlasCounts(esp, BY, red, spiderIds) {
    var set = {}, c = { dossier: 0, uni: 0, spider: 0 }, sp = {}; (spiderIds || []).forEach(function (i) { sp[i] = 1; });
    Object.keys(esp || {}).forEach(function (id) { var k = canon(id, BY, red); if (eligible(BY[k])) set[k] = 1; });
    Object.keys(set).forEach(function (id) { c.dossier++; if (BY[id].t === 'U') c.uni++; if (sp[id]) c.spider++; });
    return c;
  }

  var Core = { KEY: KEY, SLOTS: SLOTS, TITLE_MAX: TITLE_MAX, BGS: BGS, BG_BY: BG_BY, CATEGORIES: CATEGORIES, LBL: LBL, defaults: defaults, sane: sane, validTitle: validTitle, validItem: validItem, effVetrina: effVetrina,
    evalCond: evalCond, isFree: isFree, isUnlocked: isUnlocked, evaluate: evaluate, reqText: reqText, progText: progText, eligible: eligible, canon: canon, atlasCounts: atlasCounts };
  if (typeof module !== 'undefined' && module.exports) module.exports = Core; else root.tvaT2Core = Core;
})(typeof window !== 'undefined' ? window : this);
