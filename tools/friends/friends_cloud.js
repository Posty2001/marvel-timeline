/* ---------- trasporto cloud (PRONTO MA DISATTIVATO: CLOUD_ENABLED === false) ----------
   Stessi messaggi/codici del trasporto manuale, recapitati in inbox/{uid}/{id}. Rubrica: handles/{vid} -> uid. Regole: firebase/rules.friends.proposed.json (NON applicate). */
var CLOUD = {
  user: function () { try { var u = firebase.auth().currentUser; return u && u.emailVerified ? u : null; } catch (e) { return null; } },
  enabled: function () { return CLOUD_ENABLED === true && !!CLOUD.user() && typeof firebase !== 'undefined' && !!firebase.database && navigator.onLine !== false; },
  db: function () { return firebase.database(); },
  publish: function () {
    var u = CLOUD.user(); if (!CLOUD.enabled()) return Promise.reject(new Error('cloud-disattivato'));
    return CLOUD.db().ref('handles/' + ST.vid).set({ uid: u.uid, ts: firebase.database.ServerValue.TIMESTAMP }).then(function () { return CLOUD.db().ref('profiles/' + u.uid).set({ vid: ST.vid, card: JSON.stringify(card()), ts: firebase.database.ServerValue.TIMESTAMP }); });
  },
  send: function (msg, toVid) {
    var u = CLOUD.user(); if (!CLOUD.enabled()) return Promise.reject(new Error('cloud-disattivato')); if (!VID_RE.test(toVid || '')) return Promise.reject(new Error('Variante destinataria non valida.'));
    return CLOUD.db().ref('handles/' + toVid).once('value').then(function (s) {
      var h2 = s.val(); if (!h2 || typeof h2.uid !== 'string') throw new Error('Variante non trovata nel cloud.');
      return CLOUD.db().ref('inbox/' + h2.uid + '/' + msg.id).set({ code: encode(msg), from: u.uid, inv: msg.t === 'nx.invite' || msg.t === 'nx.accept', ts: firebase.database.ServerValue.TIMESTAMP });
    });
  },
  poll: function () {
    var u = CLOUD.user(); if (!CLOUD.enabled()) return Promise.reject(new Error('cloud-disattivato'));
    var ref = CLOUD.db().ref('inbox/' + u.uid);
    return ref.once('value').then(function (s) {
      var v = s.val() || {}, ids = Object.keys(v).slice(0, 50), res = [];
      ids.forEach(function (id) { var e = v[id]; if (e && typeof e.code === 'string') res.push(importCode(e.code)); });
      var links = res.filter(function (r) { return r.ok && r.t === 'nx.accept'; }).map(function (r) { return CLOUD.link(r.from).then(null, function () {}); });
      return Promise.all(links.concat(ids.map(function (id) { return ref.child(id).remove(); }))).then(function () { return res; });
    });
  },
  uidOf: function (vid) { return CLOUD.db().ref('handles/' + vid).once('value').then(function (s) { var v = s.val(); return v && typeof v.uid === 'string' ? v.uid : null; }); },
  link: function (vid) { var u = CLOUD.user(); if (!CLOUD.enabled()) return Promise.resolve(false); return CLOUD.uidOf(vid).then(function (uid) { if (!uid) return false; return CLOUD.db().ref('links/' + u.uid + '/' + uid).set(true).then(function () { return true; }); }); },
  unlink: function (vid, block) { var u = CLOUD.user(); if (!CLOUD.enabled()) return Promise.resolve(false); return CLOUD.uidOf(vid).then(function (uid) { if (!uid) return false; var p = [CLOUD.db().ref('links/' + u.uid + '/' + uid).remove()]; if (block) p.push(CLOUD.db().ref('blocked/' + u.uid + '/' + uid).set(true)); return Promise.all(p).then(function () { return true; }); }); }
};
