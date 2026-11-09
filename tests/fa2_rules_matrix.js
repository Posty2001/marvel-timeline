'use strict';
/* Matrice di autorizzazione sulle regole PROPOSTE (simulatore, non emulatore Firebase). Esce con codice !=0 se un caso fallisce. */
const path = require('path');
const { SimDB } = require('./fa2_rtdb_sim.js');
const RULES = path.join(__dirname, '..', 'firebase', 'rules.users.proposed.json');
let fails = 0, n = 0;
function T(name, cond, extra) { n++; if (cond) console.log('PASS ' + name); else { fails++; console.log('FAIL ' + name + (extra ? ' ' + JSON.stringify(extra) : '')); } }
const A = { uid: 'uidA', token: { email_verified: true, email: 'a@test.it' } };
const A_UNV = { uid: 'uidA', token: { email_verified: false } };
const B = { uid: 'uidB', token: { email_verified: true } };
const ANON = null;
const TS = { '.sv': 'timestamp' };
const prof = JSON.stringify({ app: 'x', notes: { '001': 'nota segreta di A' } });
const meta = (rev) => ({ schema: 1, rev, updatedAt: TS, device: 'devA1' });
function fresh() { return new SimDB(RULES); }
function seeded() { const d = fresh(); const r = d.write(A, { 'users/uidA': { profile: prof, meta: meta(1) } }); if (!r.ok) throw new Error('seed ' + JSON.stringify(r)); return d; }

let d = fresh();
T('A verificato: primo salvataggio profilo+meta (rev 1)', d.write(A, { 'users/uidA': { profile: prof, meta: meta(1) } }).ok);
T('A legge il proprio profilo', d.read(A, 'users/uidA/profile').ok && d.read(A, 'users/uidA/profile').value === prof);
T('B NON legge il profilo di A', !d.read(B, 'users/uidA/profile').ok);
T('B NON legge il nodo users/uidA', !d.read(B, 'users/uidA').ok);
T('B NON legge i backup di A', !d.read(B, 'users/uidA/backups').ok);
T('anonimo/non autenticato NON legge il profilo di A', !d.read(ANON, 'users/uidA/profile').ok);
T('nessuno legge la radice users (niente enumerazione)', !d.read(A, 'users').ok && !d.read(B, 'users').ok);
T('nessuno legge la radice del database', !d.read(A, '').ok);
T('B NON scrive nel profilo di A', !d.write(B, { 'users/uidA/profile': '{}' }).ok);
T('B NON scrive meta di A', !d.write(B, { 'users/uidA/meta/rev': 2 }).ok);
T('B NON crea backup in uidA', !d.write(B, { 'users/uidA/backups/abcdef1': { at: TS, device: 'x', size: 1, sha256: 'a'.repeat(64), reason: 'x', profile: '{}' } }).ok);
T('B NON cancella i dati di A', !d.write(B, { 'users/uidA': null }).ok);
T('anonimo NON scrive nel profilo di A', !d.write(ANON, { 'users/uidA/profile': '{}' }).ok);
T('A con email NON verificata: lettura negata', !d.read(A_UNV, 'users/uidA/profile').ok);
T('A con email NON verificata: scrittura negata', !fresh().write(A_UNV, { 'users/uidA': { profile: prof, meta: meta(1) } }).ok);
T('A non scrive nel nodo di B', !d.write(A, { 'users/uidB': { profile: prof, meta: meta(1) } }).ok);
/* CAS / integrita' */
d = seeded();
T('A: aggiornamento con rev+1 consentito', d.write(A, { 'users/uidA/profile': '{"v":2}', 'users/uidA/meta/rev': 2, 'users/uidA/meta/updatedAt': TS, 'users/uidA/meta/device': 'devA2', 'users/uidA/meta/schema': 1 }).ok);
T('A: dispositivo obsoleto (rev ripetuto) RIFIUTATO', !d.write(A, { 'users/uidA/profile': '{"v":"obsoleto"}', 'users/uidA/meta/rev': 2 }).ok);
T('A: salto di rev (+2) RIFIUTATO', !d.write(A, { 'users/uidA/profile': '{"v":3}', 'users/uidA/meta/rev': 4 }).ok);
T('A: profilo cambiato SENZA aumentare rev RIFIUTATO', !d.write(A, { 'users/uidA/profile': '{"v":"senza rev"}' }).ok);
T('A: il profilo cloud e\' rimasto quello valido', d.read(A, 'users/uidA/profile').value === '{"v":2}');
T('A: profilo non stringa RIFIUTATO', !d.write(A, { 'users/uidA/profile': { a: 1 }, 'users/uidA/meta/rev': 3 }).ok);
T('A: profilo oltre 5 MB RIFIUTATO', !d.write(A, { 'users/uidA/profile': 'x'.repeat(5242881), 'users/uidA/meta/rev': 3 }).ok);
T('A: campo sconosciuto in users/uidA RIFIUTATO', !d.write(A, { 'users/uidA/public': { nome: 'x' } }).ok);
T('A: campo sconosciuto in meta RIFIUTATO', !d.write(A, { 'users/uidA/meta/extra': 1 }).ok);
T('A: updatedAt falsificato RIFIUTATO', !d.write(A, { 'users/uidA/profile': '{"v":3}', 'users/uidA/meta/rev': 3, 'users/uidA/meta/updatedAt': 123 }).ok);
T('A: schema diverso da 1 RIFIUTATO', !d.write(A, { 'users/uidA/profile': '{"v":3}', 'users/uidA/meta/rev': 3, 'users/uidA/meta/schema': 9 }).ok);
/* backup */
d = seeded();
const bk = (extra) => Object.assign({ at: TS, device: 'devA1', size: 10, sha256: 'a'.repeat(64), reason: 'manuale', profile: prof }, extra || {});
T('A: crea backup valido', d.write(A, { 'users/uidA/backups/abc123xyz': bk() }).ok);
T('A: backup NON sovrascrivibile', !d.write(A, { 'users/uidA/backups/abc123xyz': bk({ reason: 'sovrascritto' }) }).ok);
T('A: backup con id non valido RIFIUTATO', !d.write(A, { 'users/uidA/backups/A/../x': bk() }).ok && !d.write(A, { 'users/uidA/backups/ab': bk() }).ok);
T('A: backup con hash non valido RIFIUTATO', !d.write(A, { 'users/uidA/backups/zzz999abc': bk({ sha256: 'nonhash' }) }).ok);
T('A: backup con campo extra RIFIUTATO', !d.write(A, { 'users/uidA/backups/zzz999abd': bk({ extra: 1 }) }).ok);
T('A: backup senza campo obbligatorio RIFIUTATO', !d.write(A, { 'users/uidA/backups/zzz999abe': { at: TS, device: 'x' } }).ok);
T('A: legge i propri backup', d.read(A, 'users/uidA/backups/abc123xyz').ok);
T('A: puo\' eliminare un proprio backup (potatura)', d.write(A, { 'users/uidA/backups/abc123xyz': null }).ok);
T('A: backup + aggiornamento profilo in un\'unica scrittura', d.write(A, { 'users/uidA/backups/bbb222ccc': bk(), 'users/uidA/profile': '{"v":9}', 'users/uidA/meta/rev': 2, 'users/uidA/meta/updatedAt': TS, 'users/uidA/meta/device': 'x', 'users/uidA/meta/schema': 1 }).ok);
/* altri nodi: restano negati */
T('nessuna scrittura su nodi non previsti (sync/ABC)', !fresh().write(A, { 'sync/ABC': 'x' }).ok);
T('nessuna scrittura su nodi non previsti (rooms/R1) dalle regole PROPOSTE', !fresh().write(A, { 'rooms/R1': { a: 1 } }).ok);
T('A: puo\' eliminare tutti i propri dati (diritto di cancellazione)', seeded().write(A, { 'users/uidA': null }).ok);

/* ---- verifica finale: revisione applicata dal DATABASE (non solo dal client) ---- */
{
  const d1 = seeded();
  const d2 = seeded(); d2.write(A, { 'users/uidA/profile': '{"v":2}', 'users/uidA/meta/rev': 2, 'users/uidA/meta/updatedAt': TS });
  T('REV: rev riportata a 1 con profilo invariato RIFIUTATA', !d2.write(A, { 'users/uidA/meta/rev': 1, 'users/uidA/meta/updatedAt': TS }).ok);
  T('REV: rev saltata (+5) con profilo invariato RIFIUTATA', !d2.write(A, { 'users/uidA/meta/rev': 7, 'users/uidA/meta/updatedAt': TS }).ok);
  T('REV: stessa rev + stesso profilo (solo device) consentito', d2.write(A, { 'users/uidA/meta/device': 'devZ', 'users/uidA/meta/updatedAt': TS }).ok);
  const d3 = seeded();
  const r1 = d3.write(A, { 'users/uidA/profile': '{"w":"primo"}', 'users/uidA/meta/rev': 2, 'users/uidA/meta/updatedAt': TS, 'users/uidA/meta/device': 'dev1' });
  const r2 = d3.write(A, { 'users/uidA/profile': '{"w":"secondo"}', 'users/uidA/meta/rev': 2, 'users/uidA/meta/updatedAt': TS, 'users/uidA/meta/device': 'dev2' });
  T('CONCORRENZA: due scritture dalla stessa base: vince una sola, l\'altra rifiutata dal DB', r1.ok && !r2.ok && d3.read(A, 'users/uidA/profile').value === '{"w":"primo"}');
  T('ATOMICITA\': profilo cambiato con rev invariata in un\'unica update RIFIUTATO e nulla scritto', (() => { const d = seeded(); const r = d.write(A, { 'users/uidA/profile': '{"x":1}', 'users/uidA/meta/updatedAt': TS }); return !r.ok && d.read(A, 'users/uidA/profile').value === prof; })());
  T('ATOMICITA\': update multi-percorso con un percorso non valido non scrive nessuno dei percorsi', (() => { const d = seeded(); const r = d.write(A, { 'users/uidA/profile': '{"x":2}', 'users/uidA/meta/rev': 2, 'users/uidA/meta/updatedAt': TS, 'users/uidA/meta/schema': 9 }); return !r.ok && d.read(A, 'users/uidA/profile').value === prof; })());
}
/* ---- falsificazione dell'uid del proprietario ---- */
{
  const d = seeded();
  T('UID: B non puo\' scrivere in users/uidA dichiarandosi A nel payload', !d.write(B, { 'users/uidA/uid': 'uidB' }).ok && !d.write(B, { 'users/uidA': { profile: prof, meta: meta(2), uid: 'uidB' } }).ok);
  T('UID: campo «uid/owner» nel nodo proprio RIFIUTATO (il proprietario e\' la chiave, non un dato)', !d.write(A, { 'users/uidA/owner': 'uidB' }).ok && !d.write(A, { 'users/uidA/uid': 'uidB' }).ok);
  T('UID: A non puo\' creare users/uidB con il proprio token', !fresh().write(A, { 'users/uidB': { profile: prof, meta: meta(1) } }).ok);
  T('UID: uid vuoto/null nel token: tutto negato', !fresh().write({ uid: null, token: { email_verified: true } }, { 'users/uidA': { profile: prof, meta: meta(1) } }).ok);
  T('NON AUTENTICATO: nessuna lettura di users/*, profilo, meta, backups', ['users', 'users/uidA', 'users/uidA/profile', 'users/uidA/meta', 'users/uidA/backups'].every(p => !d.read(null, p).ok));
  T('NON AUTENTICATO: nessuna scrittura (profilo, meta, backup, creazione)', !d.write(null, { 'users/uidA/profile': '{}' }).ok && !fresh().write(null, { 'users/uidZ': { profile: prof, meta: meta(1) } }).ok && !d.write(null, { 'users/uidA/backups/abcdef1': { at: TS, device: 'x', size: 1, sha256: 'a'.repeat(64), reason: 'x', profile: '{}' } }).ok);
}
/* ---- le regole users NON alterano rooms e sync (test differenziale su regole segnaposto) ---- */
{
  const fs = require('fs'), os = require('os');
  const users = JSON.parse(fs.readFileSync(RULES, 'utf8')).rules;
  const existing = { rooms: { $code: { '.read': 'auth != null', '.write': 'auth != null', members: { $m: { '.validate': 'newData.isString()' } } } }, sync: { $c: { '.read': true, '.write': 'newData.isString() && newData.val().length < 100' } } };
  const wr = (rules, name) => { const f = os.tmpdir() + '/fa2_' + name + '_' + process.pid + '.json'; fs.writeFileSync(f, JSON.stringify({ rules })); return f; };
  const fOld = wr(existing, 'old'), fNew = wr(Object.assign({}, existing, users), 'new');
  const { SimDB: S2 } = require('./fa2_rtdb_sim.js');
  const ops = [
    ['w', A, { 'rooms/R1/members/m1': 'x' }], ['w', null, { 'rooms/R1/members/m1': 'x' }], ['w', B, { 'rooms/R1/members/m2': 5 }],
    ['w', A, { 'sync/ABCD': 'dati' }], ['w', null, { 'sync/ABCD': 'x'.repeat(200) }], ['w', null, { 'sync/ZZZZ': 'ok' }],
    ['r', A, 'rooms/R1'], ['r', null, 'rooms/R1'], ['r', null, 'sync/ABCD'], ['r', B, 'sync/ZZZZ'], ['r', A, 'rooms'], ['r', null, '']
  ];
  const run = (f) => { const db = new S2(f); return ops.map(o => o[0] === 'w' ? db.write(o[1], o[2]).ok : db.read(o[1], o[2]).ok); };
  const a = run(fOld), b2 = run(fNew);
  T('ROOMS/SYNC: stesse decisioni con e senza il nodo users (' + ops.length + ' operazioni)', JSON.stringify(a) === JSON.stringify(b2), { a, b2 });
  T('ROOMS/SYNC: il merge non rimuove ne\' modifica rooms/sync', JSON.stringify(Object.assign({}, existing, users).rooms) === JSON.stringify(existing.rooms) && JSON.stringify(Object.assign({}, existing, users).sync) === JSON.stringify(existing.sync));
  const dn = new S2(fNew);
  T('ROOMS/SYNC: users non e\' raggiungibile da regole di rooms/sync (nessuna lettura di users via antenati)', !dn.read(B, 'users/uidA/profile').ok && !dn.read(null, 'users').ok);
}

console.log('TOTALE ' + n + ' | FAIL ' + fails);
process.exit(fails ? 1 : 0);
