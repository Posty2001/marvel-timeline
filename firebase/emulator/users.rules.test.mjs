// Test delle regole su EMULATORE UFFICIALE (Realtime Database). Mirror dei casi del simulatore (tests/fa2_rules_matrix.js).
import test, { before, after, beforeEach } from 'node:test';
import fs from 'node:fs';
import { initializeTestEnvironment, assertSucceeds, assertFails } from '@firebase/rules-unit-testing';
import { ref, set, update, get, remove, serverTimestamp } from 'firebase/database';
let env;
const verified = { email_verified: true };
const A = () => env.authenticatedContext('uidA', verified).database();
const A_UNV = () => env.authenticatedContext('uidA', { email_verified: false }).database();
const B = () => env.authenticatedContext('uidB', verified).database();
const ANON = () => env.unauthenticatedContext().database();
const prof = JSON.stringify({ notes: { '001': 'nota segreta di A' } });
const meta = (rev, device = 'devA1') => ({ schema: 1, rev, updatedAt: serverTimestamp(), device });
const bk = (o = {}) => Object.assign({ at: serverTimestamp(), device: 'devA1', size: 2, sha256: 'a'.repeat(64), reason: 'manuale', profile: '{}' }, o);
const upd = (db, profile, rev, device = 'devA1') => update(ref(db, 'users/uidA'), { profile, 'meta/schema': 1, 'meta/rev': rev, 'meta/updatedAt': serverTimestamp(), 'meta/device': device });
before(async () => {
  env = await initializeTestEnvironment({ projectId: 'demo-tva-test', database: { rules: fs.readFileSync(new URL('./database.rules.merged.json', import.meta.url), 'utf8'), host: '127.0.0.1', port: 9000 } });
});
after(async () => { await env.cleanup(); });
beforeEach(async () => { await env.clearDatabase(); await env.withSecurityRulesDisabled(async (c) => { await set(ref(c.database(), 'users/uidA'), { profile: prof, meta: { schema: 1, rev: 1, updatedAt: 1700000000000, device: 'devA1' } }); await set(ref(c.database(), 'rooms/R1/x'), 'r'); await set(ref(c.database(), 'sync/ABCD'), 's'); }); });

test('1 B non legge/scrive i dati di A', async () => {
  await assertFails(get(ref(B(), 'users/uidA/profile'))); await assertFails(get(ref(B(), 'users/uidA')));
  await assertFails(get(ref(B(), 'users/uidA/backups'))); await assertFails(get(ref(B(), 'users')));
  await assertFails(set(ref(B(), 'users/uidA/profile'), '{}')); await assertFails(upd(B(), '{}', 2)); await assertFails(remove(ref(B(), 'users/uidA')));
});
test('2 non autenticato: nessun accesso', async () => {
  await assertFails(get(ref(ANON(), 'users/uidA/profile'))); await assertFails(get(ref(ANON(), 'users'))); await assertFails(set(ref(ANON(), 'users/uidA/profile'), '{}'));
});
test('2b email non verificata: negato anche sul proprio uid', async () => {
  await assertFails(get(ref(A_UNV(), 'users/uidA/profile'))); await assertFails(upd(A_UNV(), '{}', 2));
});
test('3 uid non falsificabile: A non scrive in uidB, nessun campo uid/owner', async () => {
  await assertFails(set(ref(A(), 'users/uidB'), { profile: prof, meta: meta(1) }));
  await assertFails(update(ref(A(), 'users/uidA'), { owner: 'uidB' })); await assertFails(update(ref(B(), 'users/uidA'), { uid: 'uidB' }));
});
test('4 revisione obsoleta / saltata / rewind rifiutate dal database', async () => {
  await assertSucceeds(upd(A(), '{"v":2}', 2));
  await assertFails(upd(A(), '{"v":3}', 2)); await assertFails(upd(A(), '{"v":3}', 4));
  await assertFails(update(ref(A(), 'users/uidA'), { 'meta/rev': 1, 'meta/updatedAt': serverTimestamp() }));
  await assertFails(update(ref(A(), 'users/uidA'), { 'meta/rev': 9, 'meta/updatedAt': serverTimestamp() }));
});
test('5 due dispositivi dalla stessa base: vince uno solo', async () => {
  const r = await Promise.allSettled([upd(A(), '{"w":"d1"}', 2, 'dev1'), upd(A(), '{"w":"d2"}', 2, 'dev2')]);
  const ok = r.filter(x => x.status === 'fulfilled').length;
  if (ok !== 1) throw new Error('attesa 1 scrittura riuscita, trovate ' + ok);
  const s = (await get(ref(A(), 'users/uidA/meta/rev'))).val(); if (s !== 2) throw new Error('rev=' + s);
});
test('7-8 backup: creazione valida, create-only, hash non valido rifiutato', async () => {
  await assertSucceeds(set(ref(A(), 'users/uidA/backups/abc123xyz'), bk()));
  await assertFails(set(ref(A(), 'users/uidA/backups/abc123xyz'), bk({ reason: 'sovrascritto' })));
  await assertFails(set(ref(A(), 'users/uidA/backups/zzz999abc'), bk({ sha256: 'nonhash' })));
  await assertFails(set(ref(B(), 'users/uidA/backups/qqq111www'), bk()));
});
test('limiti: 5 MB, campi sconosciuti, updatedAt falsificato, schema', async () => {
  await assertFails(upd(A(), 'x'.repeat(5242881), 2)); await assertFails(update(ref(A(), 'users/uidA'), { extra: 1 }));
  await assertFails(update(ref(A(), 'users/uidA'), { profile: '{}', 'meta/rev': 2, 'meta/updatedAt': 123 })); await assertFails(update(ref(A(), 'users/uidA'), { profile: '{}', 'meta/rev': 2, 'meta/updatedAt': serverTimestamp(), 'meta/schema': 9 }));
});
test('9 rooms e sync: nodi delle regole identici dopo il merge (nessuna regola esistente alterata)', async () => {
  const prod = JSON.parse(fs.readFileSync(new URL('./current.rules.json', import.meta.url), 'utf8'));
  const merged = JSON.parse(fs.readFileSync(new URL('./database.rules.merged.json', import.meta.url), 'utf8'));
  for (const k of Object.keys(prod.rules)) if (JSON.stringify(prod.rules[k]) !== JSON.stringify(merged.rules[k])) throw new Error('alterato ' + k);
  if (Object.keys(merged.rules).length !== Object.keys(prod.rules).length + 1) throw new Error('il merge deve aggiungere solo users');
});
test('10 senza token (dopo logout) nessun accesso ai dati personali', async () => {
  await assertFails(get(ref(ANON(), 'users/uidA/profile')));
});
