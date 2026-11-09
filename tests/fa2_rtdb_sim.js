'use strict';
/* Simulatore MINIMO del Realtime Database con valutazione delle regole di sicurezza (sottoinsieme usato da
   firebase/rules.users.proposed.json). NON e' l'emulatore Firebase: serve a provare la logica delle regole e i client. */
const fs = require('fs');
const SERVER_TS = { '.sv': 'timestamp' };
function clone(v) { return v === undefined ? null : JSON.parse(JSON.stringify(v)); }
function getPath(o, parts) { let c = o; for (const p of parts) { if (c === null || typeof c !== 'object' || !(p in c)) return null; c = c[p]; } return c === undefined ? null : c; }
function setPath(root, parts, val) {
  if (!parts.length) return clone(val);
  root = (root !== null && typeof root === 'object') ? root : {};
  const k = parts[0];
  const child = setPath(root[k] === undefined ? null : root[k], parts.slice(1), val);
  if (child === null) delete root[k]; else root[k] = child;
  return Object.keys(root).length ? root : null;
}
class Snap {
  constructor(val) { this.v = val === undefined ? null : val; }
  exists() { return this.v !== null; }
  val() { return this.v === null ? null : (typeof this.v === 'object' ? clone(this.v) : this.v); }
  child(p) { return new Snap(getPath(this.v, String(p).split('/').filter(Boolean))); }
  hasChild(p) { return this.child(p).exists(); }
  hasChildren(a) { if (this.v === null || typeof this.v !== 'object') return false; return a ? a.every(k => k in this.v) : Object.keys(this.v).length > 0; }
  isString() { return typeof this.v === 'string'; }
  isNumber() { return typeof this.v === 'number'; }
  isBoolean() { return typeof this.v === 'boolean'; }
}
const compiled = new Map();
function ev(expr, ctx, vars) {
  if (typeof expr === 'boolean') return expr;
  const names = Object.keys(vars);
  const key = expr + '|' + names.join(',');
  let fn = compiled.get(key);
  if (!fn) { fn = new Function('auth', 'data', 'newData', 'root', 'now', ...names, '"use strict"; return (' + expr + ');'); compiled.set(key, fn); }
  try { return !!fn(ctx.auth, ctx.data, ctx.newData, ctx.root, ctx.now, ...names.map(n => vars[n])); } catch (e) { return false; }
}
String.prototype.matches = function (re) { return re.test(this); };

class SimDB {
  constructor(rulesPath, opts) {
    this.rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8')).rules;
    this.data = null; this.clock = 1700000000000; this.opts = opts || {};
  }
  now() { return (this.clock += 1000); }
  /* applica i sentinelle server */
  _resolve(v, ts) { if (v && typeof v === 'object') { if (v['.sv'] === 'timestamp') return ts; const o = {}; Object.keys(v).forEach(k => { const r = this._resolve(v[k], ts); if (r !== null) o[k] = r; }); return Object.keys(o).length ? o : null; } return v; }
  _ruleChild(node, key) { if (!node) return [null, {}]; if (node[key] !== undefined && key[0] !== '.' && key[0] !== '$') return [node[key], {}]; const w = Object.keys(node).find(k => k[0] === '$'); if (w) return [node[w], { [w]: key }]; return [null, {}]; }
  /* regole di lettura: basta un antenato (o il nodo) con .read true */
  canRead(auth, path) {
    const parts = path.split('/').filter(Boolean); let node = this.rules, vars = {};
    const ctx = { auth, root: new Snap(this.data), now: this.clock };
    for (let i = 0; i <= parts.length; i++) {
      if (node && node['.read'] !== undefined) { ctx.data = new Snap(getPath(this.data, parts.slice(0, i))); ctx.newData = ctx.data; if (ev(node['.read'], ctx, vars)) return true; }
      if (i === parts.length) break;
      const [n, v] = this._ruleChild(node, parts[i]); node = n; Object.assign(vars, v);
      if (!node) return false;
    }
    return false;
  }
  /* writes: {path: value|null} atomiche */
  write(auth, updates) {
    const ts = this.now(); let newRoot = clone(this.data); const paths = Object.keys(updates);
    const norm = paths.map(p => p.split('/').filter(Boolean));
    for (let i = 0; i < paths.length; i++) newRoot = setPath(newRoot, norm[i], this._resolve(clone(updates[paths[i]]), ts));
    const oldSnap = new Snap(this.data), newSnap = new Snap(newRoot);
    const base = { auth, root: oldSnap, now: ts };
    /* .write: per ogni percorso scritto serve un antenato/il nodo con .write true */
    for (const parts of norm) {
      let node = this.rules, vars = {}, ok = false;
      for (let i = 0; i <= parts.length; i++) {
        if (node && node['.write'] !== undefined) { const c = Object.assign({}, base, { data: new Snap(getPath(this.data, parts.slice(0, i))), newData: new Snap(getPath(newRoot, parts.slice(0, i))) }); if (ev(node['.write'], c, vars)) { ok = true; break; } }
        if (i === parts.length) break;
        const [n, v] = this._ruleChild(node, parts[i]); node = n; Object.assign(vars, v);
        if (!node) break;
      }
      if (!ok) return { ok: false, error: 'PERMISSION_DENIED', why: 'write' };
    }
    /* .validate: lungo i percorsi scritti e su tutti i discendenti presenti in newData (e sui nodi con regola figli mancanti) */
    const self = this; let bad = null;
    function visit(node, parts, vars) {
      const c = Object.assign({}, base, { data: new Snap(getPath(self.data, parts)), newData: new Snap(getPath(newRoot, parts)) });
      if (c.newData.exists() && node && node['.validate'] !== undefined && !ev(node['.validate'], c, vars)) { bad = '/' + parts.join('/'); return false; }
      const nv = c.newData.v;
      if (nv !== null && typeof nv === 'object') {
        for (const k of Object.keys(nv)) {
          const [n, v] = self._ruleChild(node, k);
          if (n) { if (!visit(n, parts.concat(k), Object.assign({}, vars, v))) return false; }
          else if (node && Object.keys(node).some(x => x[0] === '$')) { /* gestito da _ruleChild */ }
        }
      }
      return true;
    }
    for (const parts of norm) {
      /* antenati: validate sul percorso fino al nodo scritto, poi discendenti */
      let node = this.rules, vars = {};
      for (let i = 0; i < parts.length; i++) {
        const c = Object.assign({}, base, { data: new Snap(getPath(this.data, parts.slice(0, i))), newData: new Snap(getPath(newRoot, parts.slice(0, i))) });
        if (c.newData.exists() && node['.validate'] !== undefined && !ev(node['.validate'], c, vars)) return { ok: false, error: 'PERMISSION_DENIED', why: 'validate ' + '/' + parts.slice(0, i).join('/') };
        const [n, v] = this._ruleChild(node, parts[i]); node = n; Object.assign(vars, v); if (!node) { node = null; break; }
      }
      if (node && !visit(node, parts, vars)) return { ok: false, error: 'PERMISSION_DENIED', why: 'validate ' + bad };
    }
    this.data = newRoot; return { ok: true };
  }
  read(auth, path) {
    if (!this.canRead(auth, path)) return { ok: false, error: 'PERMISSION_DENIED', why: 'read' };
    return { ok: true, value: clone(getPath(this.data, path.split('/').filter(Boolean))) };
  }
}
module.exports = { SimDB, SERVER_TS };
