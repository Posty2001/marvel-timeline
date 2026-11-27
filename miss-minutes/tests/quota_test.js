// mm2e.2 - quote: testi (gateway/Google, tipo, orario), valutazione sospesa e riprendibile.
const G = require('../gateway-client.js'); require('../eval.js'); const E = globalThis.MMEval;
let p = 0, f = 0; const ok = (c, m) => { if (c) p++; else { f++; console.log('FAIL', m); } };
const now = Date.UTC(2026, 10, 27, 15, 0, 0) / 1000;   // 27/11/2026 16:00 ora italiana
const dev = G.describeQuota({ source: 'gateway', scope: 'dispositivo-giorno', kind: 'giornaliero', limit: 100, used: 100, resetAt: Date.UTC(2026, 10, 28, 0, 0, 0) / 1000 }, now, 'Europe/Rome');
ok(/non di Google/.test(dev) && /limite giornaliero di questo dispositivo \(100 richieste\)/.test(dev) && /domani alle 01:00 \(ora italiana\)/.test(dev), 'dispositivo: ' + dev);
const gg = G.describeQuota({ source: 'gemini', kind: 'giornaliero', resetAt: Date.UTC(2026, 10, 28, 8, 0, 0) / 1000 }, now, 'Europe/Rome');
ok(/Limite di Google, non di Miss Minutes/.test(gg) && /quota giornaliera gratuita di Google/.test(gg) && /domani alle 09:00/.test(gg), 'google giornaliero: ' + gg);
const mn = G.describeQuota({ source: 'gateway', scope: 'rete-minuto', kind: 'temporaneo', limit: 6, resetAt: now + 37 }, now, 'Europe/Rome');
ok(/Riprova tra 37 secondi/.test(mn) && /al minuto/.test(mn), 'minuto: ' + mn);
const mm = G.describeQuota({ source: 'gateway', scope: 'globale-mese', kind: 'mensile', limit: 12000, resetAt: Date.UTC(2026, 11, 1, 0, 0, 0) / 1000 }, now, 'Europe/Rome');
ok(/mensile/.test(mm) && /il 1 dicembre alle 01:00/.test(mm), 'mese: ' + mm);
ok(/tipo non indicato/.test(G.describeQuota({ source: 'gemini', kind: 'sconosciuto', retryAfter: 60 }, now)), 'tipo sconosciuto dichiarato come tale');
// il client conserva i campi del 429
const mk = (status, body) => async (u) => ({ status, headers: { get: () => 'application/json' }, json: async () => body, text: async () => JSON.stringify(body) });
(async () => {
  const body = { error: 'quota', scope: 'globale-giorno', kind: 'giornaliero', source: 'gateway', limit: 450, used: 450, resetAt: now + 9000, retryAfter: 9000 };
  const sub = { digest: async () => new Uint8Array(32) };
  let calls = [];
  const fe = async (u, i) => { calls.push(String(u)); if (/challenge/.test(u)) return { status: 200, json: async () => ({ salt: 's', ts: 1, bits: 0, sig: 'x' }) }; if (/session/.test(u)) return { status: 200, json: async () => ({ token: 'a.b.c', exp: now + 9999 }) }; return { status: 429, headers: { get: () => 'application/json' }, json: async () => body }; };
  const gw = G.create({ endpoint: 'https://g.test', fetch: fe, subtle: sub, now: () => now });
  const r = await gw.ask({ question: 'x' });
  ok(!r.ok && r.code === 'quota' && r.stage === 'gateway' && r.quota && r.quota.scope === 'globale-giorno' && r.quota.limit === 450 && r.quota.resetAt === now + 9000, 'client: 429 conserva ambito/limite/ripristino ' + JSON.stringify(r.quota));
  ok(gw.retriable(r) === false, 'quota mai ritentata automaticamente');
  const rs = await gw.askStream({ question: 'x' }); ok(rs.quota && rs.quota.kind === 'giornaliero', 'client streaming: 429 conserva i campi');
  const fq = async (u) => /challenge/.test(u) ? { status: 200, json: async () => ({ salt: 's', ts: 1, bits: 0, sig: 'x' }) } : /session/.test(u) ? { status: 200, json: async () => ({ token: 'a.b.c', exp: now + 9999 }) } : { status: 200, json: async () => ({ now, disponibili: 37, limitante: 'dispositivo-giorno', ripristino: now + 100, limiti: [{ scope: 'dispositivo-giorno', kind: 'giornaliero', limit: 100, used: 63, remaining: 37, resetAt: now + 100 }] }) };
  const q = await G.create({ endpoint: 'https://g.test', fetch: fq, subtle: sub, now: () => now }).quota(); ok(q.ok && q.disponibili === 37 && q.limiti[0].remaining === 37, 'client.quota(): residuo');

  // valutazione: sospensione a quota giornaliera e ripresa senza ripetere
  const dom = [{ id: 'a1', q: 'Q1', cat: 'x' }, { id: 'a2', q: 'Q2', cat: 'x', dopo: 'a1' }, { id: 'a3', q: 'Q3', cat: 'x' }, { id: 'a4', q: 'Q4', cat: 'x', dopo: 'a3' }, { id: 'a5', q: 'Q5', cat: 'x' }];
  let msgs = [], asked = [], seeded = [], mode = 'ok', quotaAt = 'Q4', diag = null;
  const hooks = { newChat: () => { msgs = []; }, count: () => msgs.length, ask: async (q) => { asked.push(q); msgs.push({ role: 'user' }); if (q === quotaAt && mode === 'quota') { diag = { code: 'quota', quota: { kind: 'giornaliero', source: 'gateway', scope: 'dispositivo-giorno', limit: 100, resetAt: now + 5000 } }; return; } diag = { ok: true }; msgs.push({ role: 'assistant', text: 'R-' + q, tag: 'online · AI' }); }, last: () => msgs[msgs.length - 1], diag: () => diag, seed: (r) => seeded.push(r.map(x => x.id)) };
  mode = 'quota'; const snaps = [];
  const o1 = await E.run(hooks, dom, { gap: 0, checkpoint: s => snaps.push(s.risultati.length) }, null, null);
  ok(o1.sospesa && o1.sospesa.kind === 'giornaliero' && o1.quota === true, 'sospesa a quota giornaliera');
  ok(o1.risultati.length === 3 && o1.risultati.every(r => r.ok), 'solo le 3 risposte completate sono salvate (nessun record fallito) ' + o1.risultati.map(r => r.id));
  ok(asked.join() === 'Q1,Q2,Q3,Q4', 'nessun tentativo ripetuto dopo la quota (Q4 una sola volta): ' + asked.join()); ok(snaps.join() === '1,2,3', 'checkpoint dopo ogni risposta');
  asked = []; mode = 'ok';
  const o2 = await E.run(hooks, dom, { gap: 0, prev: o1.risultati }, null, null);
  ok(asked.join() === 'Q4,Q5', 'ripresa: solo le domande mancanti ' + asked.join());
  ok(seeded.length === 1 && seeded[0].join() === 'a3', 'ripresa: il seguito Q4 riceve il contesto della domanda già completata (a3)');
  ok(!o2.sospesa && o2.risultati.length === 5 && o2.risultati.every(r => r.ok) && o2.risultati.map(r => r.id).join() === 'a1,a2,a3,a4,a5', 'ripresa: serie completa, ordine originale');
  // limite temporaneo: attesa del ripristino indicato e un solo nuovo tentativo
  let n = 0; const h2 = { ...hooks, ask: async (q) => { n++; msgs.push({ role: 'user' }); if (n === 1) { diag = { code: 'quota', quota: { kind: 'temporaneo', retryAfter: 1, resetAt: Math.floor(Date.now() / 1000) + 1 } }; return; } diag = { ok: true }; msgs.push({ role: 'assistant', text: 'ok', tag: 'online · AI' }); } };
  const t0 = Date.now(), o3 = await E.run(h2, [{ id: 'z1', q: 'Z', cat: 'x' }], { gap: 0 }, null, null);
  ok(n === 2 && !o3.sospesa && o3.risultati[0].ok && Date.now() - t0 >= 2500 && Date.now() - t0 < 8000, 'limite al minuto: attesa del ripristino e un solo nuovo tentativo (' + (Date.now() - t0) + ' ms)');
  console.log(`quota_test: ${p} ok, ${f} falliti`); process.exit(f ? 1 : 0);
})();
