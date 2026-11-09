'use strict';
/* Server HTTP di test: espone il simulatore RTDB (regole PROPOSTE) ai client mock. Solo test, solo localhost. */
const http = require('http'); const path = require('path');
const { SimDB } = require('./fa2_rtdb_sim.js');
const db = new SimDB(process.argv[3] || path.join(__dirname, '..', 'firebase', 'rules.users.proposed.json'));
const get = (o, p) => p.split('/').filter(Boolean).reduce((c, k) => (c && typeof c === 'object' && k in c) ? c[k] : null, o);
http.createServer((req, res) => {
  let b = ''; req.on('data', d => b += d); req.on('end', () => {
    let q = {}; try { q = JSON.parse(b || '{}'); } catch (e) {}
    let out;
    if (q.op === 'once') out = db.read(q.auth, q.path);
    else if (q.op === 'write') out = db.write(q.auth, q.updates);
    else if (q.op === 'dump') out = { ok: true, value: get(db.data, q.path || '') };
    else if (q.op === 'raw') { const r = JSON.parse(JSON.stringify(db.data || {})); const parts = q.path.split('/').filter(Boolean); let c = r; for (const k of parts.slice(0, -1)) c = c[k]; c[parts[parts.length - 1]] = q.value; db.data = r; out = { ok: true }; }
    else out = { ok: false, error: 'bad-op' };
    res.setHeader('content-type', 'application/json'); res.end(JSON.stringify(out));
  });
}).listen(+process.argv[2], '127.0.0.1');
