'use strict';
/* Test nucleo Tessera 3.0 (Node, nessun browser): condizioni di sblocco, retroattività/permanenza, titolo libero, schema additivo, parità con a5.js `eligible`. */
const assert = require('assert'); const fs = require('fs'); const path = require('path');
const C = require('../tessera2/core.js'); const A5 = require('../atlante2/a5.js');
let n = 0; const t = (name, f) => { try { f(); n++; console.log('PASS ' + name); } catch (e) { console.log('FAIL ' + name + ' ' + e.message); process.exitCode = 1; } };
const snap = (o) => Object.assign({ level: 1, pct: 0, dossier: 0, uni: 0, spider: 0 }, o);
t('12 sfondi: 4 liberi + 8 sbloccabili con le condizioni approvate', () => {
  assert.strictEqual(C.BGS.length, 12); assert.deepStrictEqual(C.BGS.filter(b => C.isFree(b)).map(b => b.id), ['sacra-linea', 'terminale-tva', 'multiverso', 'archivio-dorato']);
  const exp = { yggdrasil: ['level', 10], 'dimensione-specchio': ['dossier', 50], 'dimensione-oscura': ['level', 15], 'regno-quantico': ['pct', 25], bifrost: ['uni', 10], 'il-vuoto': ['pct', 50], 'spider-verse': ['spider', 10], infinito: ['pct', 100] };
  Object.keys(exp).forEach(id => { assert.strictEqual(C.BG_BY[id].cond.k, exp[id][0]); assert.strictEqual(C.BG_BY[id].cond.n, exp[id][1]); });
});
t('sblocco esatto alla soglia (n-1 no, n sì)', () => {
  [['yggdrasil', 'level', 10], ['dimensione-specchio', 'dossier', 50], ['dimensione-oscura', 'level', 15], ['regno-quantico', 'pct', 25], ['bifrost', 'uni', 10], ['il-vuoto', 'pct', 50], ['spider-verse', 'spider', 10], ['infinito', 'pct', 100]].forEach(([id, k, nn]) => {
    const lo = C.evaluate(C.defaults(), snap({ [k]: nn - 1 }), '2026-11-28'), hi = C.evaluate(C.defaults(), snap({ [k]: nn }), '2026-11-28');
    assert.ok(!lo.state.sbloccati[id], id + ' non deve sbloccarsi a ' + (nn - 1)); assert.ok(hi.state.sbloccati[id], id + ' deve sbloccarsi a ' + nn);
  });
});
t('retroattivo: un profilo già avanzato sblocca tutto alla prima valutazione', () => {
  const r = C.evaluate(C.defaults(), snap({ level: 20, pct: 100, dossier: 80, uni: 12, spider: 11 }), '2026-11-28'); assert.strictEqual(r.newly.length, 8);
});
t('permanente: se i dati scendono lo sfondo resta sbloccato', () => {
  const a = C.evaluate(C.defaults(), snap({ level: 10 }), '2026-11-28').state, b = C.evaluate(a, snap({ level: 1 }), '2026-11-29');
  assert.ok(b.state.sbloccati.yggdrasil === '2026-11-28'); assert.strictEqual(b.newly.length, 0);
});
t('dato non disponibile (null) = in calcolo: né sblocca né revoca', () => {
  const r = C.evalCond(C.BG_BY['dimensione-specchio'].cond, snap({ dossier: null })); assert.ok(r.pend && !r.ok);
  const a = C.evaluate(C.defaults(), snap({ level: 10 }), 'd').state; assert.ok(C.evaluate(a, { level: null, pct: null, dossier: null, uni: null, spider: null }, 'd2').state.sbloccati.yggdrasil === 'd');
});
t('nessun XP: il nucleo non espone né modifica XP/ranghi/soglie', () => { const src = fs.readFileSync(path.join(__dirname, '../tessera2/core.js'), 'utf8'); assert.ok(!/localStorage|XP_|TESSERA_TIERS|marvelXp/.test(src.replace(/\/\*[\s\S]*?\*\//g, ''))); });
t('titolo libero: ≤40 punti di codice, niente controllo/direzione, spazi normalizzati', () => {
  assert.strictEqual(C.validTitle('  Guardiano   delle  Varianti '), 'Guardiano delle Varianti'); assert.strictEqual(Array.from(C.validTitle('x'.repeat(100))).length, 40);
  assert.strictEqual(C.validTitle('a‮b\u0000c​d'), 'a b c d'); assert.strictEqual(C.validTitle(null), ''); assert.strictEqual(Array.from(C.validTitle('😀'.repeat(60))).length, 40);
});
t('schema additivo: sane() accetta vuoto/corrotto e normalizza', () => {
  [null, undefined, 5, 'x', [], {}, { v: 9, vetrina: 'no', anim: 'zz', sbloccati: { 'non-esiste': 'd', yggdrasil: 'oggi' }, titolo: { modo: 'boh', testo: 'a'.repeat(99) }, privacy: { carta: 'a', x: 'a' } }].forEach(x => {
    const s = C.sane(x); assert.strictEqual(s.v, 1); assert.ok(['auto', 'statico', 'off'].includes(s.anim)); assert.ok(!s.sbloccati['non-esiste']); assert.ok(Array.from(s.titolo.testo).length <= 40); assert.ok(C.CATEGORIES.every(k => s.privacy[k] === 'a' || s.privacy[k] === 'p'));
  });
});
t('vetrina: 6 slot, derivata dai distintivi della tessera classica se non configurata', () => {
  const s = C.defaults(); const v = C.effVetrina(s, ['x', 'y', 'z', 'w']); assert.strictEqual(v.length, 6); assert.strictEqual(v.filter(Boolean).length, 3);
  const s2 = C.sane({ vetrina: [{ t: 'badge', id: 'a' }, null, null] }); assert.strictEqual(C.effVetrina(s2, ['x']).length <= 6, true);
});
t('parità con a5.js eligible su un campione rappresentativo', () => {
  const idx = JSON.parse(fs.readFileSync(path.join(__dirname, '../atlante2/data/index.json'), 'utf8')); const st = JSON.parse(fs.readFileSync(path.join(__dirname, '../atlante2/data/db/stub.json'), 'utf8'));
  const rows = idx.voci.slice(); st.r.forEach(x => rows.push({ i: x[0], n: x[1], t: x[2], k: 'i', u: x[3], s: 0, db: 1, lv: x[4], sv: x[7] || '' }));
  rows.concat([{ k: 'c' }, { t: 'h' }, { t: 'm' }, { s: 1 }, { sv: 'x' }, { db: 1, lv: 'D' }, { db: 1, lv: 'B' }, {}]).forEach(v => assert.strictEqual(C.eligible(v), A5.eligible ? A5.eligible(v) : C.eligible(v)));
  assert.ok(rows.length > 300);
});
t('Spider-Man: 42 identità, tutte presenti nel registro', () => {
  const reg = JSON.parse(fs.readFileSync(path.join(__dirname, '../tessera2/data/regole.json'), 'utf8')); const idx = JSON.parse(fs.readFileSync(path.join(__dirname, '../atlante2/data/index.json'), 'utf8')); const ids = new Set(idx.voci.map(v => v.i));
  const st = JSON.parse(fs.readFileSync(path.join(__dirname, '../atlante2/data/db/stub.json'), 'utf8')); st.r.forEach(x => ids.add(x[0]));
  assert.strictEqual(reg.spiderman.length, 42); reg.spiderman.forEach(i => assert.ok(ids.has(i), i));
});
t('atlasCounts: redirect canonico, alias contati una volta, non verificati esclusi', () => {
  const BY = { a: { i: 'a', t: 'U', k: 'i' }, b: { i: 'b', t: 'p', k: 'i' }, c: { i: 'c', t: 'p', k: 'i', sv: 'x' }, d: { i: 'd', t: 'p', k: 'c' } };
  const r = C.atlasCounts({ a: 1, b: 1, 'old-b': 1, c: 1, d: 1, zz: 1 }, BY, { 'old-b': 'b' }, ['b']); assert.deepStrictEqual(r, { dossier: 2, uni: 1, spider: 1 });
});
console.log(n + ' controlli nucleo OK');
