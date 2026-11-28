// Archivio esteso (Database Expansion) in Miss Minutes: motore INVARIATO, solo dati. Uso: node miss-minutes/tests/atlas_db_test.js
const fs = require('fs'), path = require('path'), E = require('../engine.js');
const html = fs.readFileSync(path.join(__dirname, '../../index.html'), 'utf8');
const blob = id => JSON.parse(html.match(new RegExp('<script type="application/json" id="' + id + '">([\\s\\S]*?)</script>'))[1]);
const core = JSON.parse(fs.readFileSync(path.join(__dirname, '../knowledge/core.json'), 'utf8')).records;
const db = JSON.parse(fs.readFileSync(path.join(__dirname, '../knowledge/atlas_db.json'), 'utf8')).records;
let p = 0, f = 0; const ok = (c, m) => { if (c) p++; else { f++; console.log('FAIL', m); } };
ok(db.length > 3000 && new Set(db.map(r => r.id)).size === db.length, 'record unici (' + db.length + ')');
ok(db.every(r => r.category === 'scheda' && r.verification === 'verificata' && r.text && r.id.indexOf('db:') === 0), 'schema: solo schede verificate, kind scheda (nessuna fusione con i personaggi dell\'app)');
const data = { titles: [], graph: blob('relationshipGraphData'), powers: blob('tesseraCharPowersData'), levels: blob('tesseraCharLevelsData'), levelNames: blob('tesseraLevelNamesData'), charIds: {} };
const base = E.create({ data, knowledge: core }), est = E.create({ data, knowledge: core.concat(db) });
ok(est.stats().entries > base.stats().entries + 3000, 'indice esteso: +' + (est.stats().entries - base.stats().entries) + ' voci');
ok(est.stats().curated >= 62, 'schede curate invariate');
const z = db.find(r => r.name === 'Zeke Stane'); if (z) { const a = est.ask('Chi è Zeke Stane?'); ok(/Stane/.test(a.text), 'risponde su una voce del canon: ' + a.text.slice(0, 60)); }
const a0 = base.ask('Chi è Loki?').text, a1 = est.ask('Chi è Loki?').text; ok(a0 === a1, 'risposta su Loki identica con e senza archivio esteso');
console.log('atlas_db_test: ' + p + ' ok, ' + f + ' falliti'); process.exit(f ? 1 : 0);
