#!/usr/bin/env python3
"""Patch F-A2 + F-A3 (idempotente, dopo patch_td2): profilo per-account su Firebase Auth + sincronizzazione cloud.
Riusa il motore di sync 4.0C/4.0E (stati reali, barriera di init, confronto stabile, retry, conflitto con scelta esplicita,
ripristino transazionale con copia di sicurezza). Cambiano: percorso (users/<uid>/profile), scrittura con controllo di
concorrenza (meta/rev), proprieta' locale del profilo, backup cloud verificabili, UI nella scheda Account.
NESSUN cambiamento a: rooms/*, sync/* (codice storico, invariato), chiavi del profilo, formato export/import, TD2."""
import re
P = '/home/claude/work/index.html'; SW = '/home/claude/work/sw.js'
BUILD = '20261109-1730-fa2'
s = open(P, encoding='utf-8').read()


def rep(old, new, marker):
    global s
    if marker in s:
        return
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new)


# ---------------------------------------------------------------- 1) motore: punti di aggancio minimi
rep("      if (syncDisconnectBtn) syncDisconnectBtn.hidden = (stato === 'off' && !syncCode);\n      if (stato !== 'conflict') syncHideConflict();",
    "      if (syncMode === 'account') { if (syncDisconnectBtn) syncDisconnectBtn.hidden = true; }\n"
    "      else if (syncDisconnectBtn) syncDisconnectBtn.hidden = (stato === 'off' && !syncCode);\n"
    "      if (stato !== 'conflict' && stato !== 'update' && stato !== 'foreign') syncHideConflict();\n"
    "      if (typeof acctRender === 'function') acctRender(); /* FA2 */",
    '/* FA2 */')
rep("      var l = SYNC_LABELS[stato] || SYNC_LABELS.off;",
    "      var l = (syncMode === 'account' && SYNC_LABELS_ACCT[stato]) || SYNC_LABELS[stato] || SYNC_LABELS.off; /* FA2 */",
    'SYNC_LABELS_ACCT[stato]')
rep("      var tipo = syncClassificaErrore(err);\n      syncPushing = false;\n      if (tipo === 'auth') {",
    "      var tipo = syncClassificaErrore(err);\n      syncPushing = false;\n"
    "      if (syncMode === 'account' && ctx === 'push' && tipo === 'auth') { acctCasRecheck(gen); return; } /* FA2: rifiuto per rev obsoleto != errore di autorizzazione */\n"
    "      if (tipo === 'auth') {",
    'acctCasRecheck(gen)')
rep("        else syncConnect(syncCode, { retry: true });", "        else syncReconnect(true);", 'syncReconnect(true)')
rep("syncRetryCount = 0; syncConnect(syncCode, {}); });", "syncRetryCount = 0; syncReconnect(false); });", 'syncReconnect(false)')
rep("      syncTimeout(ref.set(str)).then(function() {", "      syncTimeout(syncWriteRemote(ref, str)).then(function() {", 'syncWriteRemote(ref, str)')
rep("      try { localStorage.setItem(SYNC_CODE_KEY, syncCode); } catch(eSv) {}\n      syncSetState('synced');",
    "      syncPersistLink();\n      syncSetState('synced');", 'syncPersistLink();\n      syncSetState')
rep("      try { localStorage.setItem(SYNC_CODE_KEY, syncCode); } catch(eC) {}\n      showToast('Profilo ripristinato dal cloud.",
    "      syncPersistLink();\n      showToast('Profilo ripristinato dal cloud.", 'syncPersistLink();\n      showToast')
rep("    function syncConnect(code, opts) {\n      opts = opts || {};",
    "    function syncConnect(code, opts) {\n      opts = opts || {};\n      if (syncMode === 'account') { acctClearFlag(); } syncMode = 'code'; syncUseEl(); /* FA2: sync con codice e sync account sono mutuamente esclusive */",
    'sync con codice e sync account sono mutuamente')
rep("      try { localStorage.removeItem(SYNC_CODE_KEY); } catch(eRm) {}\n      syncSetState('off');\n      syncSetStatus('Dati locali mantenuti.",
    "      try { localStorage.removeItem(SYNC_CODE_KEY); } catch(eRm) {}\n      acctClearFlag();\n      syncSetState('off');\n      syncSetStatus('Dati locali mantenuti.", 'acctClearFlag();\n      syncSetState')
rep("      if (syncConflictBox || !syncStatusEl || !syncStatusEl.parentNode) return syncConflictBox;",
    "      if (syncConflictBox && syncStatusEl && syncStatusEl.parentNode && syncConflictBox.previousSibling !== syncStatusEl) syncStatusEl.parentNode.insertBefore(syncConflictBox, syncStatusEl.nextSibling); /* FA2 */\n"
    "      if (syncConflictBox || !syncStatusEl || !syncStatusEl.parentNode) return syncConflictBox;", 'syncConflictBox.previousSibling !== syncStatusEl')
rep("'<button type=\"button\" class=\"reset-btn\" id=\"syncRestoreBtn\">Ripristina dal cloud</button>' +",
    "'<button type=\"button\" class=\"reset-btn\" id=\"syncRestoreBtn\">Ripristina dal cloud</button>' +\n        '<button type=\"button\" class=\"reset-btn\" id=\"syncUseLocalBtn\" hidden>Usa questo dispositivo (sostituisce il cloud)</button>' +",
    'id="syncUseLocalBtn"')
rep("      document.getElementById('syncRestoreBtn').addEventListener('click', syncRestoreFromCloud);",
    "      document.getElementById('syncRestoreBtn').addEventListener('click', syncRestoreFromCloud);\n      document.getElementById('syncUseLocalBtn').addEventListener('click', function() { acctUseLocal(); });",
    'acctUseLocal(); });')

# ---------------------------------------------------------------- 2) modulo account-sync (dentro la chiusura del motore)
ACCT_JS = r"""
    /* FA2-BEGIN — F-A2/F-A3: profilo personale (Firebase Auth) + sincronizzazione cloud per account */
    var ACCT_FLAG_KEY = 'marvel-ultimate-timeline-acct-sync';
    var ACCT_OWNER_KEY = 'marvel-ultimate-timeline-profile-owner';
    var ACCT_DEV_KEY = 'marvel-ultimate-timeline-device-id';
    var ACCT_BASE_KEY = 'marvel-ultimate-timeline-acct-base';
    var ACCT_SYNC_ENABLED = false;   /* costante di build: F-A2/F-A3 NON attivate finche' regole e verifiche non sono approvate */
    var ACCT_BACKUP_MAX = 5;
    var syncMode = 'code';
    var acct = { uid: null, rev: 0, userRef: null, foreign: false, migrating: false };
    var syncStatusElCode = syncStatusEl;
    var SYNC_LABELS_ACCT = {
      off: ['Sincronizzazione account non attiva su questo dispositivo.', 'err'],
      auth: ['⛔ Accesso al tuo spazio cloud non autorizzato (accedi di nuovo e verifica l’email). Sincronizzazione sospesa; i dati locali non sono stati toccati e NON risultano sincronizzati.', 'err']
    };
    SYNC_LABELS.update = ['🔄 Un altro dispositivo ha aggiornato il tuo profilo. Questo dispositivo non ha modifiche non sincronizzate: puoi applicare l’aggiornamento. Nulla è stato modificato.', 'busy'];
    SYNC_LABELS.foreign = ['🔒 Questo dispositivo contiene i dati di un altro account: per proteggerli non vengono caricati nel tuo. Nulla è stato modificato.', 'err'];

    function acctEl(id) { return document.getElementById(id); }
    function syncUseEl() { var a = acctEl('faSyncStatus'); syncStatusEl = (syncMode === 'account' && a) ? a : syncStatusElCode; }
    function acctUser() { try { var a = firebase.auth && firebase.auth(); var u = a && a.currentUser; return (u && u.emailVerified) ? u : null; } catch (e) { return null; } }
    function acctFlag() { try { var f = JSON.parse(localStorage.getItem(ACCT_FLAG_KEY) || 'null'); return (f && typeof f.uid === 'string' && f.on) ? f : null; } catch (e) { return null; } }
    function acctSetFlag(uid) { try { localStorage.setItem(ACCT_FLAG_KEY, JSON.stringify({ uid: uid, on: true })); } catch (e) {} }
    function acctClearFlag() { try { localStorage.removeItem(ACCT_FLAG_KEY); localStorage.removeItem(ACCT_BASE_KEY); } catch (e) {} }
    function acctSetBase() { try { localStorage.setItem(ACCT_BASE_KEY, JSON.stringify({ uid: acct.uid, rev: acct.rev })); } catch (e) {} }
    function acctBaseOk() { try { var b = JSON.parse(localStorage.getItem(ACCT_BASE_KEY) || 'null'); return !!(b && b.uid === acct.uid && b.rev === acct.rev && acct.rev > 0); } catch (e) { return false; } }
    function acctOwner() { try { return localStorage.getItem(ACCT_OWNER_KEY) || ''; } catch (e) { return ''; } }
    function acctSetOwner(uid) { try { localStorage.setItem(ACCT_OWNER_KEY, uid); } catch (e) {} }
    function acctDevId() {
      var d = ''; try { d = localStorage.getItem(ACCT_DEV_KEY) || ''; } catch (e) {}
      if (!/^[a-z0-9]{6,24}$/.test(d)) {
        d = ''; var cr = window.crypto, b = new Uint8Array(8);
        if (cr && cr.getRandomValues) cr.getRandomValues(b); else for (var i = 0; i < 8; i++) b[i] = Math.floor(Math.random() * 256);
        for (var j = 0; j < 8; j++) d += (b[j] % 36).toString(36);
        try { localStorage.setItem(ACCT_DEV_KEY, d); } catch (e2) {}
      }
      return d;
    }
    function syncReconnect(retry) {
      if (syncMode === 'account') acctConnect({ retry: !!retry });
      else syncConnect(syncCode, retry ? { retry: true } : {});
    }
    function syncPersistLink() {
      if (syncMode === 'account') {
        if (acct.uid) { acctSetFlag(acct.uid); acctSetOwner(acct.uid); acctSetBase(); }
        if (acct.migrating) { acct.migrating = false; acctBackupCreate(syncLastPushedStr || JSON.stringify(syncGetFullProfile()), 'migrazione').then(null, function() {}); }
      } else { try { localStorage.setItem(SYNC_CODE_KEY, syncCode); } catch (eSv) {} }
    }
    /* scrittura con controllo di concorrenza: il server accetta solo meta/rev = precedente + 1 */
    function syncWriteRemote(ref, str) {
      if (syncMode !== 'account') return ref.set(str);
      var rev = acct.rev + 1, up = {};
      up['profile'] = str; up['meta/schema'] = 1; up['meta/rev'] = rev;
      up['meta/updatedAt'] = firebase.database.ServerValue.TIMESTAMP; up['meta/device'] = acctDevId();
      return acct.userRef.update(up).then(function() { acct.rev = rev; acctSetBase(); });
    }

    function acctConnect(opts) {
      if (!ACCT_SYNC_ENABLED) return;
      opts = opts || {};
      var u = acctUser();
      if (!u) { syncMode = 'account'; syncUseEl(); syncSetStatus('⚠️ Accedi e verifica l’email per sincronizzare.', 'err'); return; }
      if (!syncConfigured()) { syncMode = 'account'; syncUseEl(); syncSetStatus('⚠️ Sincronizzazione non ancora configurata su questo file.', 'err'); return; }
      if (!opts.retry && syncMode === 'account' && syncState === 'connecting' && acct.uid === u.uid) return;
      var rc = opts.retry ? syncRetryCount : 0;
      syncDetach();
      syncRetryCount = rc; syncMode = 'account'; acct.uid = u.uid; syncCode = 'ACCOUNT'; syncUseEl();
      var gen = syncGen;
      syncSetState('connecting', syncInitOk ? '' : '(preparazione del profilo locale)');
      syncInitBarrier().then(function(init) {
        if (gen !== syncGen) return;
        if (!init.ok) { syncDetach(); syncCode = 'ACCOUNT'; syncSetState('initfail'); return; }
        syncSetState('connecting');
        acctAvvia(gen, u);
      });
    }
    function acctAvvia(gen, u) {
      try {
        if (!firebase.apps || !firebase.apps.length) firebase.initializeApp(FIREBASE_CONFIG);
        acct.userRef = firebase.database().ref('users/' + u.uid);
        syncRef = acct.userRef.child('profile');
      } catch (e) { syncSetStatus('⚠️ Errore di configurazione Firebase.', 'err'); syncState = 'offline'; return; }
      acct.foreign = !!acctOwner() && acctOwner() !== u.uid;
      /* il token deve contenere email_verified: lo aggiorno prima di toccare il database */
      u.getIdToken(true).then(function() {
        if (gen !== syncGen) return;
        return syncTimeout(acct.userRef.child('meta/rev').once('value')).then(function(ms) {
          if (gen !== syncGen) return;
          acct.rev = Number(ms.val()) || 0;
          return syncTimeout(syncRef.once('value')).then(function(snap) { if (gen === syncGen) acctAvviaDati(snap.val(), gen); });
        });
      }).catch(function(err) { syncHandleError(err, 'connect', gen); });
    }
    function acctAvviaDati(raw, gen) {
      if (raw === null || raw === undefined) {
        if (acct.foreign) {
          syncDetach(); syncCode = 'ACCOUNT'; syncSetState('foreign');
          var b = syncEnsureBox(); if (b) { b.hidden = false; acctBoxButtons({ keep: 'Annulla' }); acctEl('syncConflictMsg').textContent = 'Questo dispositivo contiene i dati di un altro account e il tuo spazio cloud è vuoto: per non copiare dati altrui nel tuo account non carico nulla. Per iniziare con un profilo tuo usa “Resetta tutto” (resta una copia di sicurezza) oppure importa un tuo backup, poi riattiva la sincronizzazione.'; acctEl('syncConflictDiff').hidden = true; }
          return;
        }
        var loc = null; try { loc = costruisciProfiloCompleto(); } catch (e) {}
        if (loc && profiloHaDati(loc)) {
          var testo = 'Caricare nel tuo account i dati di questo dispositivo (' + riassuntoProfiloAttuale() + ' titoli visti, note, voti, preferiti e impostazioni)?\n\nI dati locali non vengono modificati né cancellati.';
          if (!window.confirm(testo)) {
            syncDetach(); acctClearFlag(); syncCode = null; syncSetState('off');
            syncSetStatus('Sincronizzazione non attivata. Nulla è stato inviato e i dati locali non sono stati modificati.', 'err');
            return;
          }
          acct.migrating = true;
        }
        syncSetState('connecting'); syncPushNow(true, gen); return;
      }
      syncConfrontaStabile(raw, gen, function(cmp) {
        if (gen !== syncGen) return;
        if (cmp.tipo === 'uguale') { syncLastPushedStr = JSON.stringify(syncGetFullProfile()); syncActivate(raw, gen); return; }
        /* il cloud non e' cambiato dall'ultima sincronizzazione di QUESTO dispositivo (stessa rev): le differenze sono modifiche locali -> invio protetto da CAS */
        if (cmp.tipo === 'diverso' && !acct.foreign && acctBaseOk()) { syncSetState('connecting'); syncLastRemoteRaw = raw; syncPushNow(true, gen); return; }
        syncEnterConflict(raw, cmp);
      });
    }
    /* rifiuto del server su una scrittura: rev obsoleta (altro dispositivo) oppure vera negazione di autorizzazione */
    function acctCasRecheck(gen) {
      var ref = acct.userRef; if (!ref) { syncHandleError({ code: 'transient' }, 'connect', gen); return; }
      syncTimeout(ref.child('meta/rev').once('value')).then(function(ms) {
        if (gen !== syncGen) return;
        var r = Number(ms.val()) || 0;
        if (r === acct.rev) { var c = syncCode; syncDetach(); syncCode = c; syncSetState('auth'); return; }
        acct.rev = r;
        return syncTimeout(ref.child('profile').once('value')).then(function(ps) {
          if (gen !== syncGen) return;
          var raw = ps.val();
          syncConfrontaStabile(raw, gen, function(cmp) {
            if (gen !== syncGen) return;
            if (cmp.tipo === 'uguale') { syncLastRemoteRaw = raw; syncLastPushedStr = JSON.stringify(syncGetFullProfile()); syncSetState('synced'); return; }
            syncEnterConflict(raw, cmp);
          });
        });
      }).catch(function(err) { syncHandleError({ code: (err && err.code) || 'transient', message: err && err.message, _x: 1 }, 'connect', gen); });
    }

    /* ---- conflitto: etichette e scelte per modalita' ---- */
    function acctBoxButtons(o) {
      var set = function(id, txt, show) { var e = acctEl(id); if (!e) return; if (txt) e.textContent = txt; e.hidden = !show; };
      set('syncKeepLocalBtn', o.keep || 'Mantieni dati locali', o.keep !== false);
      set('syncShowDiffBtn', null, o.diff !== false);
      set('syncRestoreBtn', o.restore || 'Ripristina dal cloud', o.restore !== false);
      set('syncUseLocalBtn', null, !!o.useLocal);
      var rt = acctEl('syncRetryBtn'); if (rt) rt.hidden = true;
    }
    var syncEnterConflictBase = syncEnterConflict;
    syncEnterConflict = function(raw, cmp) {
      syncEnterConflictBase(raw, cmp);
      var rb0 = acctEl('syncRestoreBtn'); if (rb0) rb0.disabled = (cmp.tipo === 'invalido');
      if (syncMode !== 'account') { acctBoxButtons({}); return; }
      var msg = acctEl('syncConflictMsg');
      if (acct.foreign) {
        syncSetState('foreign');
        acctBoxButtons({ keep: 'Annulla', restore: cmp.tipo === 'invalido' ? false : 'Sostituisci con i dati del mio account' });
        msg.textContent = 'Questo dispositivo contiene i dati di un altro account: non vengono mai caricati nel tuo. Puoi sostituire i dati di questo dispositivo con quelli del tuo account (resta una copia di sicurezza locale recuperabile) oppure annullare.';
        return;
      }
      var invariato = false; try { invariato = JSON.stringify(syncGetFullProfile()) === syncLastPushedStr; } catch (e) {}
      if (cmp.tipo !== 'invalido' && invariato) {
        syncSetState('update');
        acctBoxButtons({ keep: 'Più tardi', restore: 'Applica aggiornamento' });
        msg.textContent = 'Un altro dispositivo ha aggiornato il tuo profilo e questo dispositivo non ha modifiche non sincronizzate. Prima di applicare viene salvata una copia di sicurezza locale.';
        return;
      }
      acctBoxButtons({ useLocal: true });
      msg.textContent = cmp.tipo === 'invalido'
        ? 'Il profilo nel cloud non è valido (' + cmp.motivo + ') e non può essere ripristinato. I tuoi dati locali restano intatti: puoi sostituire il cloud con questo dispositivo.'
        : 'Il profilo nel cloud e quello di questo dispositivo sono diversi. Nessun dato è stato modificato né inviato: scegli cosa fare. “Usa questo dispositivo” salva prima una copia di sicurezza del cloud.';
    };
    function acctUseLocal() {
      if (!ACCT_SYNC_ENABLED) return;
      var u = acctUser(); if (!u || syncMode !== 'account') return;
      if (acct.foreign) { showToast('Operazione non consentita: questo dispositivo contiene i dati di un altro account.', 7000); return; }
      var raw = syncConflictRaw;
      if (!window.confirm('Sostituire il profilo nel cloud con quello di questo dispositivo (' + riassuntoProfiloAttuale() + ' titoli visti)?\n\nPrima viene salvata nel tuo spazio cloud una copia di sicurezza del profilo cloud attuale, ripristinabile dall’elenco backup.')) { showToast('Operazione annullata. Nulla è stato modificato.'); return; }
      var str = JSON.stringify(syncGetFullProfile());
      var bk = (typeof raw === 'string' && raw) ? acctBackupCreate(raw, 'prima-sostituzione') : Promise.resolve(null);
      bk.then(function() { return acctPushDirect(str); }).then(function() {
        showToast('Cloud aggiornato con i dati di questo dispositivo. La copia precedente è nei backup.', 6000);
        acctConnect({});
      }).catch(function(e) { showToast('Operazione NON riuscita (' + ((e && (e.code || e.message)) || 'errore') + '). Nulla è stato perso; riprova.', 8000); });
    }
    function acctPushDirect(str) {
      var u = acctUser(); if (!u) return Promise.reject(new Error('no-user'));
      var ref = firebase.database().ref('users/' + u.uid);
      return syncTimeout(ref.child('meta/rev').once('value')).then(function(s2) {
        var rev = (Number(s2.val()) || 0) + 1, up = {};
        up['profile'] = str; up['meta/schema'] = 1; up['meta/rev'] = rev;
        up['meta/updatedAt'] = firebase.database.ServerValue.TIMESTAMP; up['meta/device'] = acctDevId();
        return syncTimeout(ref.update(up)).then(function() { acct.rev = rev; return rev; });
      });
    }

    /* ---- backup cloud verificabili ---- */
    function acctFnv(str) { var h = 2166136261; for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; } return ('00000000' + h.toString(16)).slice(-8); }
    function acctSha(str) {
      try {
        if (window.crypto && crypto.subtle && window.TextEncoder) {
          return crypto.subtle.digest('SHA-256', new TextEncoder().encode(str)).then(function(buf) {
            var a = new Uint8Array(buf), h = ''; for (var i = 0; i < a.length; i++) h += ('0' + a[i].toString(16)).slice(-2); return h;
          });
        }
      } catch (e) {}
      return Promise.resolve('weak-' + acctFnv(str));
    }
    function acctBackupId() { var d = acctDevId(); return (Date.now().toString(36) + d).slice(0, 32); }
    function acctBackupCreate(str, reason) {
      var u = acctUser(); if (!u) return Promise.reject(new Error('no-user'));
      if (typeof str !== 'string' || !str) return Promise.reject(new Error('empty'));
      var ref = firebase.database().ref('users/' + u.uid + '/backups');
      return acctSha(str).then(function(h) {
        var id = acctBackupId();
        return syncTimeout(ref.child(id).set({ at: firebase.database.ServerValue.TIMESTAMP, device: acctDevId(), size: str.length, sha256: h, reason: String(reason || 'manuale').slice(0, 40), profile: str }))
          .then(function() { return acctBackupTrim(ref); }).then(function() { return id; });
      });
    }
    function acctBackupRead(ref) {
      return syncTimeout(ref.once('value')).then(function(s2) {
        var v = s2.val() || {}, out = [];
        Object.keys(v).forEach(function(k) { var e = v[k]; if (e && typeof e === 'object') out.push({ id: k, at: Number(e.at) || 0, size: e.size, sha256: e.sha256, reason: e.reason, device: e.device, profile: e.profile }); });
        out.sort(function(a, b) { return b.at - a.at; });
        return out;
      });
    }
    function acctBackupTrim(ref) {
      return acctBackupRead(ref).then(function(list) {
        if (list.length <= ACCT_BACKUP_MAX) return;
        var up = {}; list.slice(ACCT_BACKUP_MAX).forEach(function(e) { up[e.id] = null; });
        return syncTimeout(ref.update(up));
      });
    }
    function acctBackupsRef() { var u = acctUser(); return u ? firebase.database().ref('users/' + u.uid + '/backups') : null; }
    function acctBackupVerify(entry) {
      if (!entry || typeof entry.profile !== 'string') return Promise.resolve({ ok: false, motivo: 'backup vuoto o illeggibile' });
      if (entry.size !== entry.profile.length) return Promise.resolve({ ok: false, motivo: 'dimensione non coerente' });
      return acctSha(entry.profile).then(function(h) {
        if (h !== entry.sha256) return { ok: false, motivo: 'impronta SHA-256 diversa: il backup è stato alterato o danneggiato' };
        var rem = syncValidaRemoto(entry.profile);
        if (!rem.ok) return { ok: false, motivo: rem.motivo };
        return { ok: true, rem: rem };
      });
    }
    function acctBackupNow() {
      if (!ACCT_SYNC_ENABLED) return;
      var str = JSON.stringify(syncGetFullProfile());
      var ref = acctBackupsRef(); if (!ref) { showToast('Accedi con un account verificato per creare un backup cloud.', 5000); return; }
      acctUserHasProfile().then(function(has) {
        if (!has) { showToast('Attiva prima la sincronizzazione: il backup si salva nel tuo spazio cloud dopo il primo caricamento.', 7000); return; }
        return acctBackupCreate(str, 'manuale').then(function() { showToast('Backup cloud creato e verificabile.', 4000); acctListBackups(); });
      }).catch(function(e) { showToast('Backup NON riuscito (' + ((e && (e.code || e.message)) || 'errore') + '). Nessun dato è stato modificato.', 7000); });
    }
    function acctUserHasProfile() {
      var u = acctUser(); if (!u) return Promise.resolve(false);
      return syncTimeout(firebase.database().ref('users/' + u.uid + '/meta/rev').once('value')).then(function(s2) { return s2.val() !== null; });
    }
    function acctFmtDate(ms) { try { return new Date(ms).toLocaleString('it-IT', { dateStyle: 'short', timeStyle: 'short' }); } catch (e) { return String(ms); } }
    function acctListBackups() {
      if (!ACCT_SYNC_ENABLED) return;
      var ul = acctEl('faBackupList'), ref = acctBackupsRef(); if (!ul) return;
      if (!ref) { ul.textContent = ''; return; }
      ul.textContent = 'Lettura dei backup…';
      acctBackupRead(ref).then(function(list) {
        ul.textContent = '';
        if (!list.length) { var li0 = document.createElement('li'); li0.textContent = 'Nessun backup cloud.'; ul.appendChild(li0); return; }
        list.forEach(function(e) {
          var li = document.createElement('li'); li.setAttribute('data-bk', e.id);
          li.appendChild(document.createTextNode(acctFmtDate(e.at) + ' · ' + (e.reason || 'manuale') + ' · ' + Math.round((e.size || 0) / 1024) + ' KB · ' + String(e.sha256 || '').slice(0, 8) + ' '));
          [['verify', 'Verifica'], ['restore', 'Ripristina']].forEach(function(p) { var b = document.createElement('button'); b.type = 'button'; b.className = 'reset-btn'; b.setAttribute('data-bk-act', p[0]); b.textContent = p[1]; li.appendChild(b); });
          ul.appendChild(li);
        });
      }, function() { ul.textContent = 'Impossibile leggere i backup in questo momento (offline o non autorizzato).'; });
    }
    function acctBackupAction(id, act) {
      if (!ACCT_SYNC_ENABLED) return;
      var ref = acctBackupsRef(); if (!ref) return;
      syncTimeout(ref.child(id).once('value')).then(function(s2) {
        var e = s2.val(); if (e) e.id = id;
        return acctBackupVerify(e).then(function(v) {
          if (act === 'verify') { showToast(v.ok ? 'Backup verificato: impronta SHA-256, dimensione e formato del profilo corretti.' : 'Backup NON valido: ' + v.motivo + '.', 7000); return; }
          if (!v.ok) { showToast('Ripristino annullato: ' + v.motivo + '. Nulla è stato modificato.', 8000); return; }
          if (!syncInitOk) { showToast('Ripristino non disponibile: il profilo locale non è ancora inizializzato.', 6000); return; }
          if (!window.confirm('Ripristinare il backup del ' + acctFmtDate(e.at) + '?\n\nSostituirà TUTTO il profilo di questo dispositivo (' + riassuntoProfiloAttuale() + ' titoli visti) con quello del backup (' + v.rem.titoliVisti + ' titoli visti). Resta una copia di sicurezza locale e il cloud attuale viene salvato come backup.')) { showToast('Ripristino annullato. Nessun dato è stato modificato.'); return; }
          var cur = syncLastRemoteRaw; var pre = (typeof cur === 'string' && cur) ? acctBackupCreate(cur, 'prima-ripristino') : Promise.resolve(null);
          return pre.then(function() {
            var ris = sostituisciProfilo(v.rem, true);
            if (!ris.ok) { showToast('Ripristino NON riuscito: ' + ris.motivo + (ris.ripristinato ? ' Il profilo precedente è stato ripristinato.' : ''), 8000); return; }
            return acctPushDirect(JSON.stringify(syncGetFullProfile())).then(function() { acctSetOwner(acctUser().uid); showToast('Backup ripristinato e sincronizzato. Ricarico…'); setTimeout(function() { location.reload(); }, 1200); },
              function() { showToast('Backup ripristinato in locale, ma il cloud non è stato aggiornato (offline?). Riattiva la sincronizzazione per riallineare.', 9000); });
          });
        });
      }).catch(function(err) { showToast('Operazione NON riuscita (' + ((err && (err.code || err.message)) || 'errore') + '). Nulla è stato modificato.', 7000); });
    }

    /* ---- UI account ---- */
    function acctRender() {
      if (!ACCT_SYNC_ENABLED) return;
      var sec = acctEl('faSync'); if (!sec) return;
      sec.hidden = false;
      var u = acctUser(), f = acctFlag(), on = !!(u && f && f.uid === u.uid);
      var onBtn = acctEl('faSyncOn'), nowBtn = acctEl('faSyncNow'), offBtn = acctEl('faSyncOff'), note = acctEl('faSyncNote'), dirty = acctEl('faSyncDirty'), bk = acctEl('faBackups');
      if (onBtn) onBtn.hidden = !u || on;
      if (nowBtn) nowBtn.hidden = !on;
      if (offBtn) offBtn.hidden = !on;
      if (bk) bk.hidden = !u;
      if (note) note.textContent = on ? 'Sincronizzazione account attiva su questo dispositivo: i dati restano anche qui e funzionano offline; le modifiche si inviano appena possibile.' : 'La sincronizzazione con l’account è disattivata: i dati restano solo su questo dispositivo, invariati. Attivandola scegli tu cosa caricare.';
      var sd = false; if (on && syncMode === 'account' && syncState !== 'synced') sd = true;
      if (on && syncMode === 'account' && syncState === 'synced') { try { sd = JSON.stringify(syncGetFullProfile()) !== syncLastPushedStr; } catch (e) {} }
      if (dirty) { dirty.hidden = !sd; dirty.textContent = sd ? 'Alcune modifiche non sono ancora sincronizzate (restano al sicuro su questo dispositivo).' : ''; }
    }
    function acctEnable() {
      if (!ACCT_SYNC_ENABLED) return;
      var u = acctUser(); if (!u) { showToast('Accedi e verifica l’email per attivare la sincronizzazione.', 5000); return; }
      var saved = null; try { saved = localStorage.getItem(SYNC_CODE_KEY); } catch (e) {}
      if (saved && !window.confirm('Su questo dispositivo è attiva la sincronizzazione con codice. Attivando quella dell’account, la sincronizzazione con codice verrà disattivata qui (il codice e i dati nel cloud non vengono toccati). Continuare?')) return;
      if (saved) { try { localStorage.removeItem(SYNC_CODE_KEY); } catch (e2) {} }
      acctSetFlag(u.uid); acctConnect({});
    }
    function acctDisable() {
      if (!ACCT_SYNC_ENABLED) return;
      syncDetach(); acctClearFlag(); syncCode = null; syncMode = 'account'; syncUseEl();
      syncSetState('off'); syncSetStatus('Sincronizzazione account disattivata su questo dispositivo. I dati locali e quelli nel cloud non sono stati modificati.', 'err');
    }
    function acctOnAuth(view) {
      if (!ACCT_SYNC_ENABLED) return;
      var u = acctUser();
      if (view === 'in' && u) {
        var f = acctFlag();
        if (f && f.uid === u.uid && !(syncMode === 'account' && acct.uid === u.uid && (syncState === 'connecting' || syncState === 'synced' || syncState === 'conflict' || syncState === 'update' || syncState === 'foreign'))) acctConnect({});
        else acctRender();
        return;
      }
      if (syncMode === 'account' && acct.uid) {
        syncDetach(); syncCode = null; syncSetState('off'); syncSetStatus('Sincronizzazione sospesa: non sei collegato all’account. I dati restano su questo dispositivo, invariati.', 'err');
      }
      acctRender();
    }
    document.addEventListener('tva-auth', function(ev) { try { acctOnAuth(ev && ev.detail && ev.detail.view); } catch (e) { if (window.console) console.error('Marvel guide - account sync:', e); } });
    function acctResume() { if (syncMode === 'account' && syncState === 'offline' && acctUser() && acctFlag()) { syncRetryCount = 0; acctConnect({}); } }
    window.addEventListener('online', acctResume);
    document.addEventListener('visibilitychange', function() { if (!document.hidden) acctResume(); });
    setInterval(function() { if (typeof acctRender === 'function') acctRender(); }, 3000);
    (function acctWire() {
      var on = acctEl('faSyncOn'), nw = acctEl('faSyncNow'), off = acctEl('faSyncOff'), bn = acctEl('faBackupNow'), bl = acctEl('faBackupRefresh'), ul = acctEl('faBackupList');
      if (on) on.addEventListener('click', acctEnable);
      if (off) off.addEventListener('click', acctDisable);
      if (nw) nw.addEventListener('click', function() { if (syncMode === 'account' && syncState === 'synced') { syncRetryCount = 0; syncPushNow(false, syncGen, true); } else acctConnect({}); });
      if (bn) bn.addEventListener('click', acctBackupNow);
      if (bl) bl.addEventListener('click', acctListBackups);
      if (ul) ul.addEventListener('click', function(ev) { var b = ev.target.closest ? ev.target.closest('[data-bk-act]') : null; if (!b) return; var li = b.closest('li'); if (li) acctBackupAction(li.getAttribute('data-bk'), b.getAttribute('data-bk-act')); });
    })();
    try { Object.defineProperty(window, 'tvaAccountSync', { value: Object.freeze({ state: function() { return { mode: syncMode, state: syncState, uid: acct.uid, rev: acct.rev, foreign: acct.foreign }; }, connect: function() { acctConnect({}); }, backupNow: acctBackupNow }), configurable: false }); } catch (e) {}
    /* FA2-END */
"""
rep("    // Riconnessione automatica: mostra «Connessione in corso»", ACCT_JS + "\n    // Riconnessione automatica: mostra «Connessione in corso»", '/* FA2-BEGIN')

# ---------------------------------------------------------------- 3) HTML account
old_in = """        <p class="fa-note">Sei collegato. I tuoi dati restano su questo dispositivo e <strong>non sono ancora sincronizzati con l'account</strong>: progressi, voti, XP, badge e Timeline non vengono letti n&eacute; modificati.</p>
        <div class="fa-actions"><button type="button" class="reset-btn" id="faLogoutBtn">Esci</button></div>"""
new_in = """        <p class="fa-note" id="faSyncNote">Sei collegato. I tuoi dati restano su questo dispositivo e <strong>non sono ancora sincronizzati con l'account</strong>: progressi, voti, XP, badge e Timeline non vengono letti n&eacute; modificati.</p>
        <div class="fa-sync" id="faSync" hidden>
          <p class="sync-status" id="faSyncStatus" hidden></p>
          <p class="fa-hint" id="faSyncDirty" hidden></p>
          <div class="fa-actions">
            <button type="button" class="reset-btn reset-btn-info" id="faSyncOn">Attiva sincronizzazione</button>
            <button type="button" class="reset-btn" id="faSyncNow" hidden>Sincronizza ora</button>
            <button type="button" class="reset-btn" id="faSyncOff" hidden>Disattiva su questo dispositivo</button>
          </div>
          <details class="fa-bk" id="faBackups" hidden>
            <summary>Backup cloud</summary>
            <p class="fa-hint">Copie del profilo nel tuo spazio cloud (ultime 5), con impronta SHA-256 verificabile prima di ogni ripristino. Il file di backup locale (Esporta profilo) resta disponibile.</p>
            <div class="fa-actions"><button type="button" class="reset-btn" id="faBackupNow">Crea backup ora</button><button type="button" class="reset-btn" id="faBackupRefresh">Aggiorna elenco</button></div>
            <ul class="fa-bk-list" id="faBackupList"></ul>
          </details>
        </div>
        <div class="fa-actions"><button type="button" class="reset-btn" id="faLogoutBtn">Esci</button></div>"""
rep(old_in, new_in, 'id="faSyncNote"')

# CSS
css = """<style id="fa2-css">
.fa-sync { margin: .5rem 0; }
.fa-bk { margin-top: .6rem; }
.fa-bk summary { cursor: pointer; font-weight: 600; min-height: 44px; display: flex; align-items: center; }
.fa-bk-list { list-style: none; margin: .4rem 0 0; padding: 0; }
.fa-bk-list li { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; padding: .35rem 0; border-top: 1px solid rgba(128,128,128,.25); font-size: .86rem; }
.fa-bk-list .reset-btn { min-height: 44px; }
#syncUseLocalBtn { border-color: rgba(200,140,0,.6); }
</style>
"""
rep('<style id="fa1-css">', css + '<style id="fa1-css">', 'id="fa2-css"')

# ---------------------------------------------------------------- 4) F-A1: evento di cambio stato account
rep("    status = view; root.setAttribute('data-fa-state', view);",
    "    status = view; root.setAttribute('data-fa-state', view);\n    try { document.dispatchEvent(new CustomEvent('tva-auth', { detail: { view: view } })); } catch (eEv) {} /* FA2 */",
    "new CustomEvent('tva-auth'")

# ---------------------------------------------------------------- 5) build
s = re.sub(r'(<meta name="tva-build" content=")[^"]*(")', r'\g<1>' + BUILD + r'\2', s)
open(P, 'w', encoding='utf-8').write(s)
sw = open(SW, encoding='utf-8').read()
sw = re.sub(r"(const SW_BUILD = ')[^']*(')", r'\g<1>' + BUILD + r'\2', sw)
sw = re.sub(r"(const CACHE_NAME = 'marvel-timeline-cache-)[^']*(')", r'\g<1>' + BUILD + r'\2', sw)
open(SW, 'w', encoding='utf-8').write(sw)
print('ok', BUILD)
