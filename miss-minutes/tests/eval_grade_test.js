// eval.js (valutazione sul dispositivo) deve classificare come tools/mm_eval_report.py. Uso: node miss-minutes/tests/eval_grade_test.js
const fs = require('fs'), path = require('path'); require('../eval.js'); const E = globalThis.MMEval;
const dom = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'eval', 'domande.json'), 'utf8')).domande, D = id => dom.find(d => d.id === id);
const rec = (id, text, o) => Object.assign({ id, ok: true, text, ms: 3000, ttfb: 900, online: true, vf: { ok: true }, srcs: [{ label: 'TMDB' }] }, o || {});
const cases = [['mcu01', 'Tony Stark è interpretato da Robert Downey Jr.', 'corretta'], ['mcu02', 'Uscì nel 2009.', 'sbagliata'], ['teo01', 'Non è confermato: sono solo teorie e ipotesi.', 'corretta'], ['teo02', 'Sì, sarà sicuramente in Secret Wars.', 'sbagliata'],
  ['fal01', 'Iron Man 7 non esiste: non risulta alcun film con questo titolo.', 'corretta'], ['nov03', 'Avengers: Doomsday non è ancora uscito, uscirà a dicembre 2026.', 'corretta'], ['nov02', 'Avengers: Doomsday è già uscito.', 'sbagliata'],
  ['fum03', 'Nei fumetti Brand New Day è un ciclo di storie del 2008.', 'corretta'], ['nov01', 'Il film Brand New Day è uscito il 29 luglio 2026.', 'corretta']];
let n = 0, bad = 0; for (const [id, t, e] of cases) { n++; const g = E.grade(D(id), rec(id, t)).e; if (g !== e) { bad++; console.log('FAIL', id, g, '!=', e); } else console.log('PASS', id); }
n++; if (E.grade(D('mcu03'), { id: 'mcu03', ok: false }).e !== 'assente') { bad++; console.log('FAIL assente'); }
const s = E.summarize(dom, cases.map(c => rec(c[0], c[1]))); n++; if (!(s.eseguite === 9 && s.corrette === 6 && s.sbagliate === 3 && s.lat_mediana_ms === 3000)) { bad++; console.log('FAIL summarize', JSON.stringify(s).slice(0, 200)); } else console.log('PASS riepilogo');
n++; if (!/Eseguite 9\/123/.test(E.riepilogoTesto(s))) { bad++; console.log('FAIL testo'); } else console.log('PASS testo');
console.log(`${n - bad}/${n}`); process.exit(bad ? 1 : 0);
