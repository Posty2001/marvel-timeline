// Test del verificatore deterministico mm2.0 (nessuna rete).
const V = require('../verify.js'); const fs = require('fs'), path = require('path');
let pass = 0, failN = 0; const ok = (c, m) => { if (c) pass++; else { failN++; console.log('FAIL ' + m); } };
const fatti = JSON.parse(fs.readFileSync(path.join(__dirname, '../knowledge/fatti.json'), 'utf8'));
const titles = [
  { id: 't001', num: 1, title: 'Spider-Man', release: '2002-05-03' },
  { id: 't132', num: 132, title: 'Spider-Man: Brand New Day', release: '2026-07-31' },
  { id: 't136', num: 136, title: 'Avengers: Doomsday', release: '2026-12-18' },
  { id: 't139', num: 139, title: 'Avengers: Secret Wars', release: '2027-12-17' }];
const K = V.build({ titles, alias_titoli: fatti.alias_titoli, cast: fatti.cast, live: [{ title: 'Avengers: Doomsday', date: '2026-12-16', confidence: 'provisional' }] }, '2026-11-26');
const kinds = t => V.scan(t, K, true).viol && V.scan(t, K, true).viol.kind;

// resolveRefs: mai inserimento di testo
const ctx = [{ id: 'id-peter-parker-mcu', title: 'Peter Parker' }];
const r = V.resolveRefs('Il personaggio è interpretato da [[id-peter-parker-mcu]] nel film.', ctx, id => '#/' + id);
ok(r.text === 'Il personaggio è interpretato da nel film.' || !/Peter Parker/.test(r.text), 'resolveRefs non inserisce titoli');
ok(r.cited.length === 1 && r.refs.length === 1 && r.markers === 1, 'resolveRefs: citazioni strutturate');
ok(V.resolveRefs('Testo [[inesistente]] ok', ctx).text === 'Testo ok' && V.resolveRefs('Nessun marcatore', ctx).text === 'Nessun marcatore', 'resolveRefs: id ignoto / nessun marcatore');

ok(V.resolveRefs('Vedi https://evil.example/x ok', ctx).text === 'Vedi [link rimosso] ok', 'resolveRefs: URL rimossi');
// attore/personaggio
ok(kinds('Peter Parker è interpretato da Peter Parker.') === 'attore', 'attore = personaggio');
ok(kinds('Peter Parker è interpretato da Tom Holland nel MCU.') === null, 'Holland ok');
ok(kinds('Peter Parker è interpretato da Robert Downey Jr.') === 'attore', 'RDJ non è Peter');
ok(kinds('Peter Parker è interpretato da Hudson Thames.') === null, 'attore sconosciuto non è falso');
ok(kinds('Tobey Maguire interpreta Peter Parker nella trilogia di Raimi.') === null, 'Maguire/Raimi ok');
ok(kinds('Tobey Maguire interpreta Peter Parker nel MCU.') === 'continuita', 'Maguire/MCU -> continuita');
// tempo
ok(kinds('Spider-Man: Brand New Day è ancora in sviluppo.') === 'tempo', 'BND uscito ma in sviluppo');
ok(kinds('Spider-Man: Brand New Day è uscito il 31 luglio 2026.') === null, 'BND uscito ok');
ok(kinds('Avengers: Doomsday è uscito nelle sale.') === 'tempo', 'Doomsday futuro descritto come uscito');
ok(kinds('Avengers: Doomsday è in arrivo a dicembre 2026.') === null, 'Doomsday in arrivo ok');
ok(kinds('Spider-Man: Brand New Day era in sviluppo prima dell’uscita.') === null, 'hedge storico ok');
// nessun falso positivo su testo neutro e senza nomi
ok(kinds('Knull è il dio dei simbionti nei fumetti.') === null, 'testo neutro');
// scan streaming: frase incompleta senza trigger scorre, con trigger trattenuta
const s1 = V.scan('Knull è un personaggio dei fumetti. Poi appare nel', K, false);
ok(s1.safe === 'Knull è un personaggio dei fumetti. Poi appare nel'.length && !s1.viol, 'streaming: coda neutra libera');
const t2 = 'Un fatto. Peter Parker è interpretato da';
const s2 = V.scan(t2, K, false); ok(s2.safe === 'Un fatto.'.length, 'streaming: coda con trigger trattenuta');
// la violazione blocca prima della frase
const t3 = 'Ciao a tutti. Peter Parker è interpretato da Peter Parker. Altro.';
const s3 = V.scan(t3, K, true); ok(s3.viol && s3.safe === 'Ciao a tutti.'.length, 'scan: safe si ferma prima della frase errata');
// frasi: abbreviazioni
ok(V.sentences('Robert Downey Jr. è Doom. Ok.').length === 2, 'sentences: Jr. non spezza');
ok(V.sentences('Il film N° 132 esce. Sì.').length === 2, 'sentences: N°');
// soft notes
ok(V.softNotes('Spider-Man: Brand New Day esce il 15 agosto 2026.', K).length === 1, 'softNotes: data diversa');
ok(V.softNotes('Spider-Man: Brand New Day è uscito il 31 luglio 2026.', K).length === 0, 'softNotes: data coincidente');
// fatti.json
ok(Array.isArray(fatti.cast) && fatti.cast.length >= 40 && fatti.cast.every(c => c.pers && c.attori && c.fonte), 'fatti.json: voci con fonte');
console.log(`verify_test: ${pass} ok, ${failN} falliti`); process.exit(failN ? 1 : 0);
