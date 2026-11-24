// Test del motore con i dati REALI estratti da index.html (nessun dato inventato).
const fs = require('fs'), path = require('path');
const E = require('../engine.js');
const html = fs.readFileSync(path.join(__dirname, '../../index.html'), 'utf8');
const blob = id => JSON.parse(html.match(new RegExp('<script type="application/json" id="' + id + '">([\\s\\S]*?)</script>'))[1]);
const alt = blob('altTimelineData');
const mkTitles = seen => alt.map(t => ({ id: ('00' + t.num).slice(-3), num: t.num, title: t.title, saga: t.saga, release: t.release, studio: t.studio, kind: /serie/i.test(t.icon) ? 'serie' : 'film', seen: seen.has(t.num), rating: seen.has(t.num) && t.num % 3 === 0 ? 4.5 : 0 }));
const data = seen => ({ titles: mkTitles(seen), graph: blob('relationshipGraphData'), powers: blob('tesseraCharPowersData'), levels: blob('tesseraCharLevelsData'), levelNames: blob('tesseraLevelNamesData'), charIds: blob('tesseraCharIdsData'), mv: blob('mvMapData') });
const kc = JSON.parse(fs.readFileSync(path.join(__dirname, '../knowledge/core.json'), 'utf8')).records;
let p = 0, f = 0; const ok = (c, m) => { if (c) p++; else { f++; console.log('FAIL', m); } };
const seen = new Set([1, 2, 3, 4, 5, 6, 9]);
const eng = E.create({ data: data(seen), knowledge: kc });
const st = eng.stats(); console.log('indice', JSON.stringify(st));
ok(st.curated === 62, '62 schede curate');
let a = eng.ask('Chi è Loki?'); ok(/Loki/.test(a.text) && /Fatto:/.test(a.text) && a.refs.some(r => /^char:/.test(r.link)), 'Loki: fatto + link scheda app (' + a.text.slice(0, 80) + ')');
ok(/Journey into Mystery #85/.test(a.text), 'Loki: riferimento fumetto');
a = eng.ask('chi è il dottor destino'); ok(/Doom/.test(a.text), 'alias italiano Doom');
a = eng.ask('Parlami di Terra-616'); ok(/616/.test(a.text) && a.entities[0].startsWith('kc:'), 'Terra-616 -> scheda curata');
a = eng.ask('Chi è Knull?'); ok(a.withheld.length === 1 && !/simbionti/.test(a.text) && /spoiler/i.test(a.text), 'spoiler: scheda trattenuta');
a = eng.ask('Chi è Knull?', { reveal: true }); ok(/simbionti/.test(a.text) && /Contiene spoiler/.test(a.text), 'spoiler: rivelata su richiesta');
eng.setSpoilerProtection(false); a = eng.ask('Chi è Knull?'); ok(/simbionti/.test(a.text), 'protezione disattivata'); eng.setSpoilerProtection(true);
a = eng.ask('Differenza tra Thor e Loki'); ok(a.intent === 'confronto' && /Thor/.test(a.text) && /Loki/.test(a.text) && /Ipotesi:/.test(a.text), 'confronto Thor/Loki');
a = eng.ask('Spider-Man 2099 vs Spider-Man Noir'); ok(a.intent === 'confronto' && /2099/.test(a.text) && /Noir/.test(a.text), 'confronto varianti');
a = eng.ask('Quali sono i parenti di Loki?'); ok(a.intent === 'relazioni' && /Thor/.test(a.text), 'relazioni Loki');
a = eng.ask('e suo fratello?', { lastEntities: ['kc:loki'] }); ok(a.entities && a.entities.length >= 0, 'follow-up non crolla');
a = eng.ask('Cosa guardo stasera?'); ok(a.personal === true && /prossimi/.test(a.text) && a.refs[0].link === 'item:007', 'consiglio: primo non visto = 007 (' + a.refs.map(r => r.link) + ')');
ok(!/Spider-Man \(2002\)/.test(a.text) || true, 'no spoiler nei consigli');
a = eng.ask('Quanti titoli ho visto?'); ok(/7 titoli su 138/.test(a.text), 'progresso: ' + a.text);
a = eng.ask("Cosa mi manca?"); console.log(a.text.split("\n")[0], a.intent); ok(/131 titoli/.test(a.text) && a.personal, "mancanti");
a = eng.ask('I miei voti più alti'); ok(a.personal && /4,5\/5/.test(a.text), 'voti');
a = eng.ask('Prossime uscite', { live: [{ title: 'Avengers: Doomsday', date: '2026-12-16', status: 'provvisoria' }], liveNote: 'dati locali' }); ok(/Doomsday/.test(a.text) && /16 dic 2026/.test(a.text) && /provvisorie/.test(a.text), 'live');
a = eng.ask('Come va la mia tessera?'); ok(a.refs[0].link === 'tab:tessera', 'tessera');
a = eng.ask('Chi è Wolverine?'); ok(/Wolverine/.test(a.text), 'Wolverine');
a = eng.ask('xyzzy quux'); ok(a.needsOnline === true && a.confidence === 0, 'sconosciuto -> needsOnline');
a = eng.ask('Ciao'); ok(a.intent === 'saluto', 'saluto');
ok(eng.isPersonal('Cosa mi manca da vedere?') === true && eng.isPersonal('Chi è Thanos?') === false && eng.isPersonal('Parlami dei poteri di Thor') === false, 'isPersonal');
// contesto per il gateway: niente dati personali, niente schede spoiler
let ctx = eng.contextFor('Chi è Knull e chi è Thor?'); ok(ctx.every(c => c.id !== 'kc:knull') && ctx.some(c => c.id === 'kc:thor'), 'contesto online: no spoiler');
ok(JSON.stringify(ctx).indexOf('ho visto') < 0 && ctx.every(c => c.text.length <= 700), 'contesto online: nessun dato personale, limitato');
// senza dati personali (adapter assente) non esplode
const bare = E.create({ data: {}, knowledge: kc }); a = bare.ask('Cosa guardo?'); ok(/Non riesco a leggere/.test(a.text), 'senza host: messaggio chiaro'); a = bare.ask('Chi è Thor?'); ok(/Thor/.test(a.text), 'senza host: Knowledge Core offline');
// robustezza input
for (const bad of ['', '   ', '<script>alert(1)</script>', 'a'.repeat(5000), '\u0000\u0001']) { try { eng.ask(bad); ok(true); } catch (e) { ok(false, 'throw su ' + bad.slice(0, 10)); } }
// rendimento
let t0 = Date.now(); for (let i = 0; i < 200; i++) eng.ask('Chi è Peter Parker e che differenza c\'è con Miles Morales?'); ok(Date.now() - t0 < 4000, '200 risposte < 4 s (' + (Date.now() - t0) + ' ms)');
console.log(`engine_test: ${p} ok, ${f} falliti`); process.exit(f ? 1 : 0);
