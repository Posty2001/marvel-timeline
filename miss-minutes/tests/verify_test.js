// Test del verificatore deterministico mm2.0 (nessuna rete).
const V = require('../verify.js'); const fs = require('fs'), path = require('path');
let pass = 0, failN = 0; const ok = (c, m) => { if (c) pass++; else { failN++; console.log('FAIL ' + m); } };
const fatti = JSON.parse(fs.readFileSync(path.join(__dirname, '../knowledge/fatti.json'), 'utf8'));
const titles = [
  { id: 't001', num: 1, title: 'Spider-Man', release: '2002-05-03' },
  { id: 't132', num: 132, title: 'Spider-Man: Brand New Day', release: '2026-07-31' },
  { id: 't136', num: 136, title: 'Avengers: Doomsday', release: '2026-12-18' },
  { id: 't139', num: 139, title: 'Avengers: Secret Wars', release: '2027-12-17' }];
const withSt = a => a.map(t => Object.assign({ stato: t.release && t.release <= '2026-11-26' ? 'released' : (t.release ? 'unreleased' : '') }, t));   // come se TMDB confermasse lo stato
const K = V.build({ titles: withSt(titles), alias_titoli: fatti.alias_titoli, cast: fatti.cast, live: [{ title: 'Avengers: Doomsday', date: '2026-12-16', confidence: 'provisional' }] }, '2026-11-26');
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
// mm2.0-b: contraddizioni di formato/esistenza, anche senza ripetere il titolo (titolo in discussione) - regole GENERALI
const titles2 = titles.concat([{ id: 't100', num: 100, title: 'Captain America: Civil War', release: '2016-04-27', kind: 'film' }, { id: 't117', num: 117, title: 'Fantastic Four: First Steps', release: '2025-07-25', kind: 'film' }]);
const K2 = V.build({ titles: withSt(titles2), alias_titoli: fatti.alias_titoli, cast: fatti.cast, live: [] }, '2026-11-26');
const kk = (q, t, prev) => { V.setFocus(K2, q, prev); const r = V.scan(t, K2, true); return r.viol ? r.viol.kind : null; };
ok(kk('Spider-Man: Brand New Day è già uscito? Di cosa parla?', 'Si tratta di un ciclo fumettistico del 2008.') === 'formato', 'focus: ciclo fumettistico senza titolo nella frase');
ok(kk('Spider-Man: Brand New Day è già uscito?', 'Non risulta essere un film uscito al cinema.') === 'formato', 'focus: negazione del formato');
ok(kk('Spider-Man: Brand New Day è già uscito?', 'Spider-Man: Brand New Day non è un film.') === 'formato', 'titolo nella frase: negazione del formato');
ok(kk('Quando esce Avengers: Doomsday?', 'È un arco narrativo dei fumetti.') === 'formato', 'altro titolo Marvel: stessa regola (Doomsday)');
ok(kk('Parlami di Captain America: Civil War', 'Non esiste alcun film con questo titolo.') === 'esistenza', 'altro titolo: negata esistenza di un titolo già uscito (Civil War)');
ok(kk('Parlami di Fantastic Four: First Steps', 'Questo titolo non è ancora uscito.') === 'tempo', 'altro titolo: non ancora uscito ma uscito nel 2025');
ok(kk('Spider-Man: Brand New Day è già uscito?', 'Esiste anche un ciclo a fumetti omonimo del 2008, da non confondere con il film.') === null, 'omonimia dichiarata: nessuna violazione');
ok(kk('Spider-Man: Brand New Day nei fumetti: com’è il ciclo?', 'Si tratta di un ciclo fumettistico del 2008.') === null, 'domanda sui fumetti: nessuna violazione');
ok(kk('Spider-Man: Brand New Day è già uscito?', 'Il film è uscito il 31 luglio 2026 e vede Tom Holland.') === null, 'risposta corretta: nessuna violazione');
ok(kk('Cosa fa Knull?', 'Non è un film, è un personaggio.') === null, 'nessun titolo in discussione: nessun giudizio');
ok(kk('E quando esce?', 'Non è ancora uscito.', 'Avengers: Doomsday uscita?') === null, 'follow-up su titolo futuro: corretto');
ok(kk('E quando è uscito?', 'Non è ancora uscito.', 'Spider-Man: Brand New Day è già uscito?') === 'tempo', 'follow-up (domanda precedente): contraddizione intercettata');
ok(kk('Parlami di Spider-Man e Doomsday', 'Non è un film uscito al cinema.') === null, 'focus ambiguo (due titoli): nessun giudizio arbitrario');
// C.1: stato di uscita da fonte (non dedotto dalla data), negazioni, riferimenti ad altro, date regionali
const K3 = V.build({ titles: [{ id: 'a', num: 1, title: 'Titolo Senza Stato', release: '2025-07-25', kind: 'film' }, { id: 'b', num: 2, title: 'Film Rimandato', release: '2026-06-01', kind: 'film', stato: 'unreleased' }, { id: 'c', num: 3, title: 'Film Uscito Davvero', release: '2026-07-31', kind: 'film', stato: 'released', dates: ['2026-07-29', '2026-07-31'] }], alias_titoli: {}, cast: [], live: [] }, '2026-11-26');
const k3 = (q, a, prev) => { V.setFocus(K3, q, prev || ''); const r = V.scan(a, K3, true); return r.viol ? r.viol.kind : null; };
ok(k3('Titolo Senza Stato quando è uscito?', 'Titolo Senza Stato non è ancora uscito.') === null, 'data trascorsa senza stato di fonte: nessuna deduzione automatica');
ok(k3('Film Rimandato è uscito?', 'Film Rimandato è uscito nelle sale a giugno.') === 'tempo', 'data trascorsa ma stato TMDB «non uscito»: affermazione di uscita intercettata');
ok(k3('Film Rimandato è uscito?', 'Film Rimandato non è ancora uscito: la data prevista è slittata.') === null, 'slittamento descritto correttamente');
ok(k3('Film Uscito Davvero è uscito?', 'Film Uscito Davvero non è ancora uscito.') === 'tempo', 'stato TMDB uscito ma descritto come non uscito');
ok(k3('Film Uscito Davvero?', 'Il suo seguito non è ancora uscito.') === null, 'frase sul seguito: nessun giudizio sul titolo');
ok(k3('Film Uscito Davvero?', 'Film Uscito Davvero non è uscito prima di luglio.') === null, 'negazione: «non è uscito» non e\' un\'affermazione di uscita futura');
const sn = V.softNotes('Film Uscito Davvero è uscito il 29 luglio 2026 in Italia.', K3); ok(sn.length === 0, 'data regionale documentata (IT): nessun falso avviso');
const sn2 = V.softNotes('Film Uscito Davvero è uscito il 3 agosto 2026.', K3); ok(sn2.length === 1 && /29\/07\/2026/.test(sn2[0]) && !/verifica la fonte/.test(sn2[0]), 'data non documentata: nota naturale con le date note');
// fatti.json
ok(Array.isArray(fatti.cast) && fatti.cast.length >= 40 && fatti.cast.every(c => c.pers && c.attori && c.fonte), 'fatti.json: voci con fonte');
console.log(`verify_test: ${pass} ok, ${failN} falliti`); process.exit(failN ? 1 : 0);
