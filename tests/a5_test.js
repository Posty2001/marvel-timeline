// A5 — nucleo puro: soglie, XP approvati (+2/+15/+25/+5/+5/+1/+40), tetto 30 con coda, badge, completamenti, relazioni, preferiti/raccolte. Uso: node tests/a5_test.js
const C = require('../atlante2/a5.js'); let p = 0, f = 0; const ok = (c, m) => { if (c) p++; else { f++; console.log('FAIL', m); } };
const BY = {}; for (let i = 0; i < 30; i++) BY['p' + i] = { t: 'p', k: 'i', n: 'P' + i, u: i < 4 ? 'U1' : 'U2' }; BY.U1 = { t: 'U', k: 'i' }; BY.U2 = { t: 'U', k: 'i' };
BY.copia = { t: 'p', k: 'c', u: 'U1' }; BY.hub = { t: 'h', k: 'h' }; BY.man = { t: 'm', k: 'm' }; BY.ver = { t: 'p', k: 'i', s: 1, u: 'U1' };
for (let i = 0; i < 3; i++) BY['a' + i] = { t: 'a', k: 'i' };
const t0 = new Date(2026, 10, 27, 12).getTime(), day = '2026-11-27';
ok(C.REW.dossier === 2 && C.REW.hub === 15 && C.REW.uni === 25 && C.REW.confronto === 5 && C.REW.raccolta === 5 && C.BADGE_XP === 40 && C.CAP === 30, 'valori XP approvati');
ok(!C.isExplored({ ms: 9999, scroll: 1, sec: 5 }) && !C.isExplored({ ms: 12000, scroll: 0.59, sec: 5 }) && !C.isExplored({ ms: 12000, scroll: 1, sec: 1 }) && C.isExplored({ ms: 10000, scroll: 0.6, sec: 2 }), 'soglie dossier esplorato');
ok(C.isExplored({ ms: 10000, scroll: 0.6, sec: 1 }, 1) && !C.isExplored({ ms: 99999, scroll: 1, sec: 0 }, 0), 'meno di 2 sezioni / 0 sezioni');
// dossier +2, una sola volta; esclusioni
let st = C.empty(); const ex = { hubMap: {}, red: {} };
ok(C.markExplored(st, 'p0', BY, t0, ex).ok && st.xp[day] === 2 && !C.markExplored(st, 'p0', BY, t0, ex).ok && st.xp[day] === 2, 'dossier +2 una sola volta');
['copia', 'hub', 'man', 'ver', 'nonesiste'].forEach(id => ok(!C.markExplored(st, id, BY, t0, ex).ok, 'nessuna ricompensa: ' + id));
// alias: id storico redirect → canonico, nessun doppio premio
ok(!C.markExplored(st, 'vecchio', BY, t0, { red: { vecchio: 'p0' }, hubMap: {} }).ok && C.counts(st, BY, { vecchio: 'p0' }).tot === 1, 'alias non premiato due volte');
const stA = C.empty(); C.markExplored(stA, 'p5', BY, t0, ex); ok(C.counts(Object.assign(C.empty(), { esp: { p5: {}, vecchio5: {} } }), Object.assign({}, BY), { vecchio5: 'p5' }).tot === 1, 'id storico + canonico contano una volta');
// universo completato +25 (U1: p0..p3), non conta la voce in verifica/copia
['p1', 'p2'].forEach(i => C.markExplored(st, i, BY, t0, ex)); ok(!st.uni.U1, 'universo non ancora completo');
const r3 = C.markExplored(st, 'p3', BY, t0, ex); ok(st.uni.U1 && r3.done.some(d => d.k === 'uni' && d.id === 'U1' && d.xp === 25) && st.ric['uni:U1'].xp === 25, 'universo completato +25');
ok(!C.markExplored(st, 'p3', BY, t0, ex).ok && Object.keys(st.ric).filter(k => k === 'uni:U1').length === 1, 'universo premiato una sola volta');
// hub completato +15: solo membri effettivi, hub con >= 2
const hubMap = { H1: ['p10', 'p11', 'ver', 'mancante'], H2: ['p12'] }; const exh = { hubMap, red: {} }; ['p10'].forEach(i => C.markExplored(st, i, BY, t0, exh)); ok(!st.hub.H1, 'hub incompleto');
const rh = C.markExplored(st, 'p11', BY, t0, exh); ok(st.hub.H1 && rh.done.some(d => d.k === 'hub' && d.xp === 15), 'hub completato +15 (membri effettivi, esclusi in verifica/mancanti)');
C.markExplored(st, 'p12', BY, t0, exh); ok(!st.hub.H2, 'hub con 1 solo membro non conta');
// primo confronto +5, prima raccolta +5 (>=3 schede), una volta
const s2 = C.empty(); ok(C.onConfronto(s2, t0, ex, BY).ok && !C.onConfronto(s2, t0, ex, BY).ok && s2.ric['primo-confronto'].xp === 5, 'primo confronto +5 una volta');
const s3 = C.empty(); const cid = C.newCol(s3, 'X', 1); C.colToggle(s3, cid, 'p1'); C.colToggle(s3, cid, 'p2'); ok(!C.checkCollection(s3, t0), 'raccolta con 2 schede: no'); C.colToggle(s3, cid, 'p3'); ok(C.checkCollection(s3, t0) && !C.checkCollection(s3, t0) && s3.ric['prima-raccolta'].xp === 5, 'prima raccolta +5 con 3 schede, una volta');
C.delCol(s3, cid); ok(s3.ric['prima-raccolta'], 'la ricompensa resta dopo aver eliminato la raccolta');
// relazioni: chiavi, filtri, inverse, +1 max 10/giorno
const R = (a, b, t, cl, v) => [a, b, t, cl, v];
ok(C.relKey(R('a', 'b', 'alleanza', 'n', 2)) === C.relKey(R('b', 'a', 'alleanza', 'n', 2)), 'simmetrica: chiave identica');
ok(C.relKey(R('a', 'b', 'famiglia_genitore', 'n', 2)) === C.relKey(R('b', 'a', 'famiglia_discendente', 'n', 2)), 'genitore/discendente: nessuna duplicazione inversa');
ok(C.relKey(R('a', 'b', 'alleanza', 'a', 2)) === null && C.relKey(R('a', 'b', 'alleanza', 'e', 2)) === null && C.relKey(R('a', 'b', 'alleanza', 'n', 0)) === null && C.relKey(R('a', 'b', 'copia', 'n', 2)) === null && C.relKey(R('a', 'a', 'alleanza', 'n', 2)) === null, 'escluse co-apparizioni, editoriali, da verificare, copie, auto-relazioni');
ok(C.relKey(R('a', 'b', 'alleanza', 'n', 2)) !== C.relKey(R('a', 'b', 'rivalita', 'n', 2)), 'tipi diversi = relazioni distinte');
const s4 = C.empty(); for (let i = 0; i < 12; i++) C.onRelation(s4, [R('x', 'y' + i, 'amicizia', 'n', 2)], BY, t0, ex);
ok(Object.keys(s4.rel).length === 12 && Object.keys(s4.ric).filter(k => k.startsWith('rel:')).length === 10 && s4.xp[day] === 10, '12 relazioni distinte contate, XP solo per le prime 10 del giorno');
ok(C.onRelation(s4, [R('y0', 'x', 'amicizia', 'n', 2)], BY, t0, ex).added === 0, 'stessa relazione al contrario: non ricontata');
ok(C.relTotal({ tipi: ['alleanza', 'copia'], r: [['a', 'b', 0, 'n', 2], ['b', 'a', 0, 'n', 2], ['a', 'c', 1, 'n', 2], ['a', 'd', 0, 'e', 2]] }) === 1, 'relTotal: solo narrative documentate distinte');
// badge: Esploratore a 25 con +40, coda 30/giorno
const s5 = C.empty(); let got = []; for (let i = 0; i < 25; i++) got = got.concat(C.markExplored(s5, 'p' + i, BY, t0, ex).badges); ok(got.length === 1 && got[0].k === 'esploratore', 'Esploratore al 25°');
const tot5 = Object.values(s5.xp).reduce((a, b) => a + b, 0); ok(tot5 === 25 * 2 + 40 + 25 + 0 && Object.values(s5.xp).every(v => v <= 30), 'XP totali = 25×2 + badge 40 + universo 25, mai > 30/giorno (' + tot5 + ')');
ok(C.creditedUntil(s5, day) === 30 && C.pendingAfter(s5, day) === tot5 - 30 && C.creditedUntil(s5, '2027-12-31') === tot5, 'accredito differito, nulla si perde');
ok(!C.evaluate(s5, BY, t0, ex).length && !C.award(s5, 'badge:esploratore', 40, t0), 'badge mai riassegnato');
// disponibilità e motivi; mai revocati
const bs = C.badgeStatus(s5, BY, { red: {}, hubMap, relTot: 20 }).reduce((o, b) => (o[b.k] = b, o), {});
ok(!bs.cartografo.avail && /universi/.test(bs.cartografo.why) && !bs.cacciatore.avail && /hub/.test(bs.cacciatore.why) && !bs.maestro_nexus.avail && /20/.test(bs.maestro_nexus.why), 'Cartografo/Cacciatore/Maestro: non ottenibili con motivo');
ok(!bs.custode_artefatti.avail && /3 voci/.test(bs.custode_artefatti.why) && !bs.custode_multiverso.avail && bs.archivista.avail, 'artefatti/multiverso: motivo; archivista ottenibile');
const BY2 = Object.assign({}, BY); for (let i = 100; i < 700; i++) BY2['q' + i] = { t: 'p', k: 'i' }; ok(C.badgeStatus(s5, BY2, { relTot: 500, hubMap }).find(b => b.k === 'custode_multiverso').avail && C.badgeStatus(s5, BY, {}).find(b => b.k === 'esploratore').got, 'registro cresciuto → ottenibile; traguardo non revocato');
ok(C.badgeStatus(s5, {}, {}).find(b => b.k === 'esploratore').got, 'traguardo ottenuto resta anche se il registro cambia');
// tetto globale con più ricompense
const s6 = C.empty(); for (let i = 0; i < 5; i++) C.award(s6, 'k' + i, 40, t0); ok(Object.values(s6.xp).every(v => v <= 30) && Object.values(s6.xp).reduce((a, b) => a + b, 0) === 200, 'tetto 30/giorno, 200 XP totali');
ok(C.creditedUntil({ xp: { '2026-11-27': 9999 } }, day) === 30, 'lettura con clamp 30');
// preferiti e raccolte, stato corrotto
const s7 = C.empty(); ok(C.toggleFav(s7, 'p1', 1) === true && C.toggleFav(s7, 'p1', 2) === false && Object.keys(s7.ric).length === 0, 'preferiti: nessuna ricompensa A5 (resta il +3 esistente)');
const c7 = C.newCol(s7, '  Miei  ', 5); ok(c7 && s7.col[c7].n === 'Miei' && C.newCol(s7, '  ', 5) === null && C.colToggle(s7, c7, 'p1') && !C.colToggle(s7, c7, 'p1') && C.renameCol(s7, c7, 'Altro') && C.delCol(s7, c7), 'raccolte: crea/aggiungi/rinomina/elimina');
ok(JSON.stringify(C.sane('x')) === JSON.stringify(C.empty()) && !Array.isArray(C.sane({ fav: [] }).fav) && C.sane({ v: 1 }).hub && C.sane({ v: 1 }).rel, 'stato corrotto/vecchio → struttura completa');
ok(C.addDays('2026-12-31', 1) === '2027-01-01', 'addDays a cavallo d\'anno');
console.log('a5_test: ' + p + ' ok, ' + f + ' falliti'); process.exit(f ? 1 : 0);
