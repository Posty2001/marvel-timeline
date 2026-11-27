// A5 — nucleo puro (preferiti, raccolte, tetto XP, badge, dossier esplorato). Uso: node tests/a5_test.js
const C = require('../atlante2/a5.js'); let p = 0, f = 0; const ok = (c, m) => { if (c) p++; else { f++; console.log('FAIL', m); } };
const BY = {}; for (let i = 0; i < 30; i++) BY['p' + i] = { t: 'p', k: 'i', n: 'P' + i }; BY.copia = { t: 'p', k: 'c' }; BY.hub = { t: 'h', k: 'h' }; BY.man = { t: 'm', k: 'm' };
for (let i = 0; i < 3; i++) BY['a' + i] = { t: 'a', k: 'i' };
const day = '2026-11-27', t0 = new Date(2026, 10, 27, 12).getTime();
// esplorato: soglie
ok(!C.isExplored({ ms: 9999, scroll: 1, sec: 5 }), '10 s minimi'); ok(!C.isExplored({ ms: 12000, scroll: 0.59, sec: 5 }), 'scroll 60%'); ok(!C.isExplored({ ms: 12000, scroll: 1, sec: 1 }), '2 sezioni'); ok(C.isExplored({ ms: 10000, scroll: 0.6, sec: 2 }), 'soglie esatte');
ok(C.isExplored({ ms: 10000, scroll: 0.6, sec: 1 }, 1) && !C.isExplored({ ms: 10000, scroll: 0.6, sec: 1 }, 3) && !C.isExplored({ ms: 99999, scroll: 1, sec: 0 }, 0), 'meno di 2 sezioni: tutte; 0 sezioni: mai');
// una volta sola, esclusioni
const st = C.empty();
ok(C.markExplored(st, 'p0', BY, t0).ok && !C.markExplored(st, 'p0', BY, t0).ok, 'una sola volta per id');
ok(!C.markExplored(st, 'copia', BY, t0).ok && !C.markExplored(st, 'hub', BY, t0).ok && !C.markExplored(st, 'man', BY, t0).ok && !C.markExplored(st, 'sconosciuto', BY, t0).ok, 'copie/hub/mantelli/ignoti non contano');
ok(C.counts(st, BY).tot === 1, 'conteggio = 1');
// niente XP per dossier (valore non specificato)
ok(C.XP_DOSSIER === 0 && Object.keys(st.xp).length === 0, 'nessun XP per singolo dossier finche\' non deciso');
// badge Esploratore a 25, 40 XP, tetto 30/giorno con coda
let got = [];
for (let i = 1; i < 25; i++) { const r = C.markExplored(st, 'p' + i, BY, t0); got = got.concat(r.badges); }
ok(got.length === 1 && got[0].k === 'esploratore', 'Esploratore al 25° dossier'); ok(C.counts(st, BY).tot === 25, '25 esplorati');
ok(st.xp[day] === 30 && st.xp['2026-11-28'] === 10, 'badge 40 XP: 30 oggi + 10 domani (coda)');
ok(C.creditedUntil(st, day) === 30 && C.pendingAfter(st, day) === 10 && C.creditedUntil(st, '2026-11-28') === 40, 'accredito e coda corretti');
ok(!C.evaluate(st, BY, t0).length, 'badge mai riassegnato'); ok(!C.award(st, 'badge:esploratore', 40, t0), 'ricompensa unica per chiave');
// badge non ottenibili spiegati; mai revocati
const bs = C.badgeStatus(st, BY).reduce((o, b) => (o[b.k] = b, o), {});
ok(!bs.cartografo.avail && /Manca/.test(bs.cartografo.why) && !bs.cacciatore.avail && !bs.maestro_nexus.avail, 'Cartografo/Cacciatore/Maestro: non ancora ottenibili con motivo');
ok(!bs.custode_artefatti.avail && /3 voci/.test(bs.custode_artefatti.why), 'Custode artefatti: registro < 25'); ok(!bs.custode_multiverso.avail && !bs.archivista.got && bs.archivista.avail, 'Archivista ottenibile, Custode del Multiverso no');
const BY2 = Object.assign({}, BY); for (let i = 30; i < 600; i++) BY2['q' + i] = { t: 'p', k: 'i' }; ok(C.badgeStatus(st, BY2).find(b => b.k === 'custode_multiverso').avail, 'il registro cresce → diventa ottenibile'); ok(C.badgeStatus(st, BY).find(b => b.k === 'esploratore').got, 'traguardo non revocato');
// tetto giornaliero: 3 badge nello stesso giorno → mai > 30 al giorno
const s2 = C.empty(); for (let i = 0; i < 5; i++) C.award(s2, 'k' + i, 40, t0); ok(Object.values(s2.xp).every(v => v <= 30) && Object.values(s2.xp).reduce((a, b) => a + b, 0) === 200, 'tetto 30/giorno, nessun XP perso (200 totali)');
ok(C.creditedUntil(s2, day) === 30 && C.creditedUntil(s2, '2026-12-31') === 200, 'accredito progressivo fino a 200');
ok(C.creditedUntil({ xp: { '2026-11-27': 9999 } }, day) === 30, 'lettura con clamp 30/giorno');
// preferiti e raccolte
const s3 = C.empty(); ok(C.toggleFav(s3, 'p1', 1) === true && C.toggleFav(s3, 'p1', 2) === false, 'preferito on/off');
const cid = C.newCol(s3, '  Miei  ', 5); ok(cid && s3.col[cid].n === 'Miei', 'nuova raccolta (trim)'); ok(C.newCol(s3, '   ', 5) === null, 'nome vuoto rifiutato');
ok(C.colToggle(s3, cid, 'p1') && C.colHas(s3, cid, 'p1') && !C.colToggle(s3, cid, 'p1'), 'aggiungi/rimuovi voce'); ok(C.renameCol(s3, cid, 'Altro') && s3.col[cid].n === 'Altro', 'rinomina'); ok(C.delCol(s3, cid) && !s3.col[cid], 'elimina');
ok(JSON.stringify(C.sane('x')) === JSON.stringify(C.empty()) && C.sane({ fav: [] }).fav && !Array.isArray(C.sane({ fav: [] }).fav), 'stato corrotto → vuoto, senza eccezioni');
ok(C.addDays('2026-12-31', 1) === '2027-01-01', 'addDays a cavallo d\'anno');
console.log('a5_test: ' + p + ' ok, ' + f + ' falliti'); process.exit(f ? 1 : 0);
