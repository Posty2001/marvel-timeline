const L = require('../lookup.js'); let pass = 0, failN = 0; const ok = (c, m) => { if (c) pass++; else { failN++; console.log('FAIL ' + m); } };
const mem = () => { const o = {}; return { getItem: k => o[k] ?? null, setItem: (k, v) => { o[k] = v; }, removeItem: k => { delete o[k]; }, o }; };
const wp = { query: { pages: [
  { title: 'Spider-Man: Brand New Day', index: 1, extract: 'Spider-Man: Brand New Day is a 2026 American superhero film based on Marvel Comics featuring Spider-Man.', pageprops: { 'wikibase-shortdesc': '2026 American superhero film', wikibase_item: 'Q123' } },
  { title: 'Spider-Man: Brand New Day (comics)', index: 2, extract: 'Brand New Day was a 2008 comic book storyline published by Marvel Comics.', pageprops: { 'wikibase-shortdesc': '2008 Marvel Comics storyline', wikibase_item: 'Q456' } },
  { title: 'Senza descrizione', index: 3 }] } };
let calls = 0, urls = [];
const fetchOk = async (u) => { calls++; urls.push(u); return { ok: true, json: async () => wp }; };
(async () => {
  ok(L.kindOf('2026 American superhero film', '') === 'film' && L.kindOf('2008 Marvel Comics storyline', '') === 'fumetti' && L.kindOf('American television series', '') === 'serie' && L.kindOf('', 'Foo is a person.') === 'altro', 'kindOf');
  const st = mem();
  const r = await L.lookup([{ name: 'Spider-Man: Brand New Day', rel: '2026-07-31' }], { fetch: fetchOk, store: st, today: '2026-11-26' });
  ok(calls === 1 && r.net === 1 && r.facts.length === 3, 'una chiamata, 2 pagine + omonimia: ' + r.facts.length);
  ok(r.facts[0].classe === 'wikipedia' && /film/.test(r.facts[0].testo) && r.facts[0]._url.startsWith('https://en.wikipedia.org/wiki/') && r.facts[0]._wd.endsWith('/Q123'), 'fatto 1: tipo film, url, wikidata');
  ok(/fumetti/.test(r.facts[1].testo) && r.facts[2].testo.startsWith('OMONIMIA'), 'omonimia film/fumetti esplicita');
  ok(!/Senza descrizione/.test(JSON.stringify(r.facts)), 'pagine senza testo scartate');
  ok(/gsrsearch=Spider-Man%3A%20Brand%20New%20Day%20Marvel/.test(urls[0]) && !/question|history/.test(urls[0]) && /origin=\*/.test(urls[0]), 'solo il nome del titolo nella richiesta');
  const r2 = await L.lookup([{ name: 'Spider-Man: Brand New Day', rel: '2026-07-31' }], { fetch: fetchOk, store: st, today: '2026-11-26' });
  ok(calls === 1 && r2.cached === 1 && r2.facts.length === 3, 'cache: nessuna seconda richiesta');
  // TTL
  ok(L.ttlFor('2026-07-31', '2026-11-26') === 6 * 3600e3 && L.ttlFor('2008-05-02', '2026-11-26') === 14 * 86400e3 && L.ttlFor('', '2026-11-26') === 6 * 3600e3, 'TTL differenziato recente/storico');
  // fail-open
  const st2 = mem(); const bad = async () => { throw new Error('rete'); };
  const r3 = await L.lookup([{ name: 'X Y' }], { fetch: bad, store: st2, today: '2026-11-26' });
  ok(r3.facts.length === 0 && r3.failed === 1, 'errore di rete: nessun fatto, nessuna eccezione');
  const r4 = await L.lookup([{ name: 'X Y' }], { fetch: async () => ({ ok: false }), store: st2, today: '2026-11-26' });
  ok(r4.facts.length === 0, 'HTTP errore: nessun fatto');
  // timeout
  const slow = (u, o) => new Promise((_, rej) => o.signal.addEventListener('abort', () => rej(new Error('abort'))));
  const t0 = Date.now(); const r5 = await L.lookup([{ name: 'Slow' }], { fetch: slow, store: mem(), today: '2026-11-26' });
  ok(r5.failed === 1 && Date.now() - t0 < 5000, 'timeout 3,5 s');
  // max 3 nomi
  calls = 0; await L.lookup(['a', 'b', 'c', 'd', 'e'].map(n => ({ name: n })), { fetch: fetchOk, store: mem(), today: '2026-11-26' }); ok(calls === 3, 'massimo 3 ricerche');
  // cache scaduta + rete ko -> dati vecchi
  const st3 = mem(); await L.lookup([{ name: 'Old', rel: '2001-01-01' }], { fetch: fetchOk, store: st3, today: '2026-11-26' });
  const k = Object.keys(st3.o)[0], c = JSON.parse(st3.o[k]); c.old.t = Date.now() - 40 * 86400e3; st3.o[k] = JSON.stringify(c);
  const r6 = await L.lookup([{ name: 'Old', rel: '2001-01-01' }], { fetch: bad, store: st3, today: '2026-11-26' }); ok(r6.facts.length === 3, 'cache scaduta usata se la rete fallisce');
  L.clear(st3); ok(!st3.o[k], 'cache cancellabile');
  console.log(`lookup_test: ${pass} ok, ${failN} falliti`); process.exit(failN ? 1 : 0);
})();
