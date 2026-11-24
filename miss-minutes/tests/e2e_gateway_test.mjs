// Client reale + worker reale (DO simulato) collegati senza rete: verifica il flusso sfida -> sessione -> chat.
import { DatabaseSync } from 'node:sqlite';
import { createRequire } from 'node:module';
import worker, { Limiter } from '../gateway/worker.ts';
const require = createRequire(import.meta.url); const G = require('../gateway-client.js');
const db = new DatabaseSync(':memory:');
const sql = { exec(q, ...b) { const st = db.prepare(q); const sel = /^\s*select/i.test(q); const rows = sel ? st.all(...b) : (st.run(...b), []); return { toArray: () => rows, one: () => rows[0] }; } };
const lim = new Limiter({ storage: { sql } });
const env = { LIMITER: { idFromName: n => n, get: () => ({ fetch: (u, i) => lim.fetch(new Request(u, i)) }) }, GEMINI_KEY: 'k', GEMINI_MODEL: 'm', SESSION_SECRET: 's'.repeat(32), APP_ORIGINS: 'https://app.test', FREE_TIER_VERIFIED: 'yes', POW_BITS: '12', DAILY_CAP: '2' };
let providerCalls = 0;
const fakeFetch = async (url, init) => { url = String(url);
  if (url.includes('generativelanguage')) { providerCalls++; return new Response(JSON.stringify({ candidates: [{ content: { parts: [{ text: 'Risposta [[kc:loki]]' }] } }] })); }
  const u = new URL(url); return worker.fetch(new Request('https://gw' + u.pathname, { ...init, headers: { ...(init.headers || {}), Origin: 'https://app.test', 'CF-Connecting-IP': '3.3.3.3' } }), env); };
const mem = {}; const storage = { getItem: k => mem[k] ?? null, setItem: (k, v) => { mem[k] = v; }, removeItem: k => { delete mem[k]; } };
let p = 0, f = 0; const ok = (c, m) => { if (c) p++; else { f++; console.log('FAIL', m); } };
const orig = globalThis.fetch; globalThis.fetch = fakeFetch;   // il worker chiama il "provider" tramite fetch globale
const c = G.create({ endpoint: 'https://gw', fetch: fakeFetch, storage });
const t0 = Date.now(); let r = await c.ask({ question: 'Chi è Loki?', history: [], context: [], spoiler: 'avoid' });
ok(r.ok && /Risposta/.test(r.answer), 'primo giro: sfida+sessione+chat (' + JSON.stringify(r) + ')'); console.log('PoW 12 bit + chat in', Date.now() - t0, 'ms');
ok(!!mem['marvel-ultimate-timeline-miss-minutes-session'], 'token salvato (solo token firmato, nessuna chiave)');
r = await c.ask({ question: 'e Thor?' }); ok(r.ok, 'secondo giro riusa la sessione'); ok(providerCalls === 2, 'provider chiamato 2 volte');
r = await c.ask({ question: 'terza' }); ok(!r.ok && r.code === 'quota' && /locale/.test(r.message), 'cap giornaliero -> errore esplicito (fallback locale)'); ok(providerCalls === 2, 'nessuna chiamata oltre il cap');
const bad = G.create({ endpoint: '', fetch: fakeFetch }); r = await bad.ask({ question: 'x' }); ok(!r.ok && r.code === 'disabled', 'senza endpoint: disabled');
const off = G.create({ endpoint: 'https://gw', fetch: async () => { throw new TypeError('x'); } }); r = await off.ask({ question: 'x' }); ok(!r.ok && r.code === 'network', 'rete assente -> network');
console.log(`e2e_gateway_test: ${p} ok, ${f} falliti`); process.exit(f ? 1 : 0);
