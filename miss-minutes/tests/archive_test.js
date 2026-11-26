// Miss Minutes 2.0 - caricamento/validazione dell'archivio TMDB (pacchetto -> copia locale -> remoto). Uso: node miss-minutes/tests/archive_test.js
const fs = require('fs'), path = require('path'), crypto = require('crypto');
global.window = globalThis; const store = {};
globalThis.localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
require('../archive.js'); const A = globalThis.MMArchive;
let n = 0, bad = 0; const ok = (t, c, x) => { n++; if (!c) bad++; console.log((c ? 'PASS ' : 'FAIL ') + t + (x ? ' ' + x : '')); };
const real = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'knowledge', 'tmdb_titoli.json'), 'utf8'));
const mk = (gen, extra) => { const o = JSON.parse(JSON.stringify(real)); o.versione = 2; o.generato = gen; Object.assign(o.voci, extra || {}); return o; };
const sha = t => crypto.createHash('sha256').update(t).digest('hex');
const mkFetch = (files, log) => async (u) => { log.push(u); const k = u.replace(/^https:\/\/ex\.test\/a\//, ''); if (!(k in files)) return { ok: false, status: 404, text: async () => '' }; return { ok: true, status: 200, text: async () => files[k] }; };
(async () => {
  ok('archivio incluso valido', A.validate(real).length === 0, A.validate(real).join(';'));
  ok('scarta schema sconosciuto', A.validate({ versione: 9, generato: '2026-11-27', voci: real.voci }).length > 0);
  ok('scarta archivio quasi vuoto', A.validate({ versione: 2, generato: '2026-11-27', voci: { '001': real.voci['001'] } }).length > 0);
  const lost = mk('2026-12-01'); Object.keys(lost.voci).slice(0, 40).forEach(k => delete lost.voci[k]);
  ok('scarta se perde >10% delle voci', A.validate(lost, real).some(x => /perde/.test(x)));
  const nosyn = mk('2026-12-01'); Object.keys(nosyn.voci).slice(0, 30).forEach(k => { delete nosyn.voci[k].sinossi_it; });
  ok('scarta se perde molte sinossi', A.validate(nosyn, real).some(x => /sinossi/.test(x)));
  const baddate = mk('2026-12-01'); baddate.voci['001'].date = [{ paese: 'IT', data: '07/06/2002' }];
  ok('scarta date non ISO', A.validate(baddate, real).length > 0);
  ok('scarta archivio piu\' vecchio', A.validate(mk('2020-01-01'), real).some(x => /vecchio/.test(x)));

  // 1) remoto spento: nessuna richiesta di rete
  let log = []; let r = await A.load({ bundle: real, base: '', fetch: mkFetch({}, log) });
  ok('spento di default: nessuna richiesta', log.length === 0 && r.origine === 'incluso');
  // 2) remoto valido piu' recente -> usato, salvato come copia locale verificata
  const next = mk('2026-12-05'); const tx = JSON.stringify(next), h = sha(tx), ptr = { versione: 2, generato: '2026-12-05', sha256: h, file: 'tmdb_titoli.' + h.slice(0, 8) + '.json', n: Object.keys(next.voci).length };
  const files = { 'pointer.json': JSON.stringify(ptr), [ptr.file]: tx }; log = [];
  r = await A.load({ bundle: real, base: 'https://ex.test/a', fetch: mkFetch(files, log), now: 1e12, force: true });
  ok('remoto valido: aggiornato', r.origine === 'remoto' && r.archivio.generato === '2026-12-05', r.note.join('|'));
  ok('copia locale salvata', !!store[A.KEY]);
  // 3) offline dopo l'aggiornamento: usa la copia locale verificata
  log = []; r = await A.load({ bundle: real, base: 'https://ex.test/a', fetch: async () => { throw new Error('offline'); }, now: 1e12 + 13 * 3600e3 });
  ok('offline: usa la copia locale verificata', r.origine === 'copia-locale' && r.archivio.generato === '2026-12-05', r.origine + ' ' + r.note.join('|'));
  // 4) limite di frequenza: nessuna nuova richiesta entro 12 h
  log = []; r = await A.load({ bundle: real, base: 'https://ex.test/a', fetch: mkFetch(files, log), now: 1e12 + 13 * 3600e3 + 1000 });
  ok('al piu\' un controllo ogni 12 h', log.length === 0);
  // 5) impronta alterata -> scartato, resta la copia
  const evil = Object.assign({}, ptr, { generato: '2026-12-09', sha256: '0'.repeat(64) }); const nx = JSON.stringify(mk('2026-12-09'));
  log = []; r = await A.load({ bundle: real, base: 'https://ex.test/a', fetch: mkFetch({ 'pointer.json': JSON.stringify(evil), [ptr.file]: nx, ['x.json']: nx }, log), now: 1e12 + 99 * 3600e3, force: true });
  ok('SHA-256 diverso: rifiutato, resta la copia verificata', r.origine === 'copia-locale' && /SHA-256/.test(r.note.join('')), r.note.join('|'));
  // 6) contenuto valido per impronta ma che non supera la validazione
  const lost2 = mk('2026-12-10'); Object.keys(lost2.voci).slice(0, 60).forEach(k => delete lost2.voci[k]); const tl = JSON.stringify(lost2), hl = sha(tl);
  r = await A.load({ bundle: real, base: 'https://ex.test/a', fetch: mkFetch({ 'pointer.json': JSON.stringify({ versione: 2, generato: '2026-12-10', sha256: hl, file: 'l.json' }), 'l.json': tl }, []), now: 1e12 + 120 * 3600e3, force: true });
  ok('impronta corretta ma dati peggiori: rifiutato', r.origine === 'copia-locale' && /validazione/.test(r.note.join('')), r.note.join('|'));
  // 7) puntatore con nome file malevolo / rete giu'
  r = await A.load({ bundle: real, base: 'https://ex.test/a', fetch: mkFetch({ 'pointer.json': JSON.stringify({ versione: 2, generato: '2027-01-01', sha256: h, file: '../../etc/x.json' }) }, []), now: 1e12 + 150 * 3600e3, force: true });
  ok('nome file non consentito: rifiutato', /puntatore non valido/.test(r.note.join('')));
  r = await A.load({ bundle: real, base: 'http://ex.test/a', fetch: mkFetch(files, []), now: 1e12 + 200 * 3600e3, force: true });
  ok('solo https', !/aggiornato da remoto/.test(r.note.join('')));
  // 8) copia locale corrotta -> scartata, si torna al pacchetto
  store[A.KEY] = JSON.stringify({ sha: 'x', archivio: { versione: 2, generato: '2027-01-01', voci: { a: 1 } } });
  r = await A.load({ bundle: real, base: '', fetch: mkFetch({}, []) });
  ok('copia locale corrotta scartata', r.origine === 'incluso' && !store[A.KEY] && /scartata/.test(r.note.join('')));
  // 9) pacchetto non valido e nessun remoto: nessun archivio (l'app tiene il proprio)
  r = await A.load({ bundle: { versione: 9 }, base: '' }); ok('pacchetto non valido: nessun archivio', r.archivio === null);
  console.log('\n' + (n - bad) + '/' + n); process.exit(bad ? 1 : 0);
})();
