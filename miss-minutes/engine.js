/* Miss Minutes — motore locale (offline). Nessuna rete, nessuno storage, nessun accesso al DOM.
   Riceve dati gia' presenti nell'app (sola lettura) e le schede del Knowledge Core; restituisce risposte testuali
   con riferimenti (link interni) e marcatori fatto/ipotesi. UMD: globalThis.MMEngine | module.exports. */
(function (root) {
  'use strict';

  var norm = function (t) {
    return String(t == null ? '' : t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/['’`]/g, ' ').replace(/[^a-z0-9]+/g, ' ').trim();
  };
  var pad3 = function (n) { return ('00' + n).slice(-3); };
  var uniq = function (a) { return a.filter(function (x, i) { return x && a.indexOf(x) === i; }); };
  var hash = function (s) { var h = 5381; for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return Math.abs(h); };
  var pick = function (arr, seed) { return arr[hash(String(seed)) % arr.length]; };
  var fmtDate = function (iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || ''); if (!m) return iso || '';
    var M = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'];
    return Number(m[3]) + ' ' + M[Number(m[2]) - 1] + ' ' + m[1];
  };

  /* ---------- indice ---------- */
  function aliasesOf(name) {
    var out = [name];
    String(name).split(/[\/()]/).forEach(function (p) { p = p.trim(); if (p.length >= 3) out.push(p); });
    return uniq(out.map(norm).filter(function (a) { return a.length >= 3; }));
  }

  function build(opts) {
    var d = opts.data || {};
    var entries = [], byId = {}, aliasMap = {};
    function add(e) {
      if (byId[e.id]) return byId[e.id];
      e.aliases = uniq(e.aliases.map(norm).filter(function (a) { return a.length >= 2; }));
      entries.push(e); byId[e.id] = e;
      e.aliases.forEach(function (a) { (aliasMap[a] = aliasMap[a] || []).push(e); });
      return e;
    }
    // 1) Knowledge Core (schede curate)
    (opts.knowledge || []).forEach(function (r) {
      if (!r || !r.id || !r.name) return;
      add({ id: 'kc:' + r.id, kind: r.category || 'lore', name: r.name, aliases: [r.name].concat(r.aliases || []), universe: r.universe || '', text: r.text || '', source: r.source || '',
        spoiler: r.spoiler === true, verification: r.verification || 'da verificare', curated: true, link: null });
    });
    // 2) personaggi dell'app (grafo relazioni + poteri + livelli): fusione con le schede curate se hanno un alias in comune
    var graph = d.graph || {}, powers = d.powers || {}, levels = d.levels || {}, lvNames = d.levelNames || {};
    var charIds = d.charIds || {};
    var nameToChar = {};
    Object.keys(graph).forEach(function (cid) {
      var g = graph[cid]; if (!g || g.type !== 'char') return;
      var nm = g.name || cid;
      var al = aliasesOf(nm);
      var merged = null;
      for (var i = 0; i < al.length && !merged; i++) { (aliasMap[al[i]] || []).forEach(function (e) { if (e.curated && e.kind === 'personaggio' && !e.host) merged = e; }); }
      var lv = levels[nm];
      var host = { id: cid, name: nm, level: lv != null ? lv : null, levelName: lv != null ? (lvNames[String(lv)] || '') : '', power: powers[nm] || '', conns: g.conns || [] };
      if (merged) {
        merged.host = host; merged.link = 'char:' + cid; merged.aliases = uniq(merged.aliases.concat(al));
        al.forEach(function (a) { (aliasMap[a] = aliasMap[a] || []).indexOf(merged) < 0 && aliasMap[a].push(merged); });
        nameToChar[norm(nm)] = merged;
      } else {
        var e = add({ id: 'ch:' + cid, kind: 'personaggio', name: nm, aliases: al, universe: '', text: '', source: '', spoiler: false, verification: 'dati dell’app', curated: false, link: 'char:' + cid, host: host });
        nameToChar[norm(nm)] = e;
      }
    });
    // nomi con personaggi presenti solo in poteri/livelli
    Object.keys(powers).forEach(function (nm) {
      if (nameToChar[norm(nm)]) return;
      var cid = charIds[nm] || null;
      var e = add({ id: 'ch:' + (cid || norm(nm).replace(/ /g, '-')), kind: 'personaggio', name: nm, aliases: aliasesOf(nm), universe: '', text: '', source: '', spoiler: false, verification: 'dati dell’app', curated: false,
        link: cid ? 'char:' + cid : null, host: { id: cid, name: nm, level: levels[nm] != null ? levels[nm] : null, levelName: levels[nm] != null ? (lvNames[String(levels[nm])] || '') : '', power: powers[nm] || '', conns: [] } });
      nameToChar[norm(nm)] = e;
    });
    // 3) universi (mvMapData)
    var uni = (d.mv && d.mv.universi) || {};
    Object.keys(uni).forEach(function (uid) {
      var u = uni[uid], nm = u.nome || uid;
      var short = nm.split('—')[0].trim();
      add({ id: 'un:' + uid, kind: 'universo', name: nm, aliases: [nm, short, short.replace(/earth[- ]/i, 'terra ')], universe: '', text: nm + ': ' + (u.titoli || 0) + ' titoli (' + (u.film || 0) + ' film, ' + (u.serie || 0) + ' serie), ' + (u.personaggi || 0) + ' personaggi.' + ((u.personaggiPrincipali || []).length ? ' Tra i principali: ' + u.personaggiPrincipali.slice(0, 5).join(', ') + '.' : ''), source: '', spoiler: false, verification: 'dati dell’app', curated: false, link: 'uni:' + uid, uid: uid });
    });
    // 4) titoli della timeline
    var titles = (d.titles || []).map(function (t) { return t; });
    titles.forEach(function (t) {
      add({ id: 'ti:' + t.id, kind: 'titolo', name: t.title, aliases: [t.title], universe: t.saga || '', text: '', source: '', spoiler: false, verification: 'dati dell’app', curated: false, link: 'item:' + t.id, title: t });
    });
    return { entries: entries, byId: byId, aliasMap: aliasMap, titles: titles, nameToChar: nameToChar };
  }

  /* ---------- ricerca entita' ---------- */
  function findEntities(ix, q, limit, kinds) {
    var n = ' ' + norm(q) + ' ', hits = {};
    Object.keys(ix.aliasMap).forEach(function (a) {
      if (n.indexOf(' ' + a + ' ') < 0) return;
      ix.aliasMap[a].forEach(function (e) {
        if (kinds && kinds.indexOf(e.kind) < 0) return;
        var sc = a.length + (e.curated ? 4 : 0) + (e.kind === 'titolo' ? 0 : 1);
        if (!hits[e.id] || hits[e.id].sc < sc) hits[e.id] = { e: e, sc: sc, a: a };
      });
    });
    var arr = Object.keys(hits).map(function (k) { return hits[k]; }).sort(function (x, y) { return y.sc - x.sc; });
    // scarta alias contenuti in match piu' lunghi gia' presi (es. "man" in "spider man")
    var out = [];
    arr.forEach(function (h) { if (!out.some(function (o) { return o.a.indexOf(h.a) >= 0 && o.e !== h.e && o.a.length > h.a.length && h.e.kind !== o.e.kind; })) out.push(h); });
    return out.slice(0, limit || 5).map(function (h) { return h.e; });
  }

  /* ---------- composizione ---------- */
  var TONE = {
    open: [],
    empty: ['Su questo non trovo nulla di affidabile nell’archivio locale.', 'Nell’archivio locale non ho informazioni affidabili su questo.'],
    close: []
  };


  function lvLine(h) {
    if (!h) return '';
    var parts = [];
    if (h.levelName) parts.push('Livello poteri ' + h.level + ' (' + h.levelName + ')');
    return parts.join(' · ');
  }

  /* aspetto richiesto dalla domanda: la risposta locale contiene SOLO cio' che e' stato chiesto (mai l'intero dossier) */
  function aspectOf(n) {
    if (/\b(poteri|poter\w+|abilit\w+|capacit\w+|superpoter\w+|livello|scala dei poteri|quanto e forte|forza)\b/.test(n)) return 'poteri';
    if (/\b(legami|legat\w+|parenti|famiglia|alleat\w+|nemic\w+|relazion\w+|collegat\w+)\b/.test(n)) return 'legami';
    if (/\b(universo|terra|multiverso|continuita|che universo|di quale universo)\b/.test(n)) return 'universo';
    if (/\b(quando e uscit\w*|data di uscita|uscita|quando esce|che anno)\b/.test(n)) return 'uscita';
    if (/\b(saga|scheda n|numero della scheda|in che posizione|ordine)\b/.test(n)) return 'posizione';
    return 'generale';
  }
  function describe(e, ctx, aspect) {
    var L = [], refs = [], miss = false; aspect = aspect || 'generale';
    var h = e.host, who = e.name + (e.universe ? ' (' + e.universe + ')' : '');
    if (aspect === 'poteri') {
      if (h && h.power) { L.push('Poteri e capacità di ' + who + ' secondo la guida dell’app: ' + h.power); var lv = lvLine(h); if (lv) L.push(lv + ' — scala interna dell’app, non dei fumetti.'); }
      else miss = true;
      if (miss) L.push('Per ' + e.name + ' nella guida dell’app non ci sono dati sui poteri.');
    } else if (aspect === 'legami') {
      var rel = relationsOf(ctx.ix, e, 8);
      if (rel.length) L.push('Legami di ' + who + ' nella guida dell’app: ' + rel.map(function (r) { return r.name + ' (' + r.label.toLowerCase() + ')'; }).join('; ') + '.'); else { miss = true; L.push('Per ' + e.name + ' nella guida dell’app non ci sono legami registrati.'); }
    } else if (aspect === 'universo') {
      if (e.universe) L.push(e.name + ' appartiene a: ' + e.universe + '.'); else { miss = true; L.push('Per ' + e.name + ' nella guida non è indicato l’universo.'); }
    } else if (e.title && (aspect === 'uscita' || aspect === 'posizione')) {
      var t0 = e.title;
      if (aspect === 'uscita') { if (t0.release) L.push(e.name + ': uscita ' + fmtDate(t0.release) + ' (data della Timeline).'); else { miss = true; L.push('Per ' + e.name + ' la Timeline non riporta una data di uscita.'); } }
      else L.push(e.name + ' è la scheda N°' + t0.id + (t0.saga ? ', ' + t0.saga : '') + '.');
    } else if (aspect === 'uscita' || aspect === 'posizione') {
      miss = true; L.push('Per ' + e.name + ' nella guida non ho questo dato.');
    } else {
      L.push(e.name + (e.universe ? ' — ' + e.universe : ''));
      if (e.text) { L.push(e.text); if (e.source) L.push('Riferimento nei fumetti: ' + e.source + '.'); }
      else if (e.title) L.push('Scheda N°' + e.title.id + (e.title.saga ? ' · ' + e.title.saga : '') + (e.title.release ? ' · uscita ' + fmtDate(e.title.release) : ''));
      else if (h && h.power) L.push('Poteri e capacità (dati dell’app): ' + h.power);
    }
    if (e.link) refs.push({ label: e.name, link: e.link });
    return { text: L.filter(Boolean).join('\n'), refs: refs, missing: miss };
  }

  function relationsOf(ix, e, max) {
    var out = [], seen = {};
    ((e.host && e.host.conns) || []).forEach(function (c) {
      if (c.rtype === 'titolo' || !c.name || seen[c.id]) return;
      seen[c.id] = 1; out.push({ id: c.id, name: c.name, label: c.label || c.rtype || 'collegato', rtype: c.rtype });
    });
    return out.slice(0, max || 8);
  }

  /* ---------- intenti ---------- */
  function has(n, re) { return re.test(n); }

  /* Un'intenzione PERSONALE richiede un riferimento a chi parla o all'app (ho/mi/mio..., Timeline, Tessera, TVA Live...):
     «Quanti film compongono la Saga dell'Infinito?» o «Quali sono le prossime uscite Marvel?» sono domande generali sul Marvel Universe. */
  var SELF = /\b(mi|ho|hai|mio|mia|miei|mie|me|sono|sto|stiamo|nostr[oa]|nostri|mancano)\b|\b(tva archives|nella timeline|la timeline|tessera|profilo|tva live|calendario dell app|missioni|friends)\b/;
  function personalIntent(n) {
    var self = SELF.test(n) || n.split(' ').length <= 3;   // comandi brevi dell'app («Cosa guardo?», «Prossime uscite»)
    if (has(n, /\b(mi manc[ao]|mi mancano|non ho (ancora )?visto|da recuperare)\b/)) return 'missing';
    if (!self) return null;
    if (has(n, /\b(cosa|che cosa|che)\b.*\b(guard|vedere|vedo)|\bprossim[oi] (da|titolo|film|serie)|consigli|cosa mi consigli|da vedere/)) return 'advice';
    if (has(n, /\b(ho visto|quanti|quanto ho|progresso|percentuale|a che punto)\b/)) return 'progress';
    if (has(n, /\b(miei voti|mie valutazioni|i miei voti|voti piu alti|migliori per me|classifica|classifiche|preferiti)\b/)) return 'ratings';
    if (has(n, /\b(prossime uscite|nuove uscite|in uscita|trailer|novita|live|calendario)\b/)) return 'live';
    if (has(n, /\b(tessera|mio rango|rango|mio livello|livello agente)\b/)) return 'card';
    if (has(n, /\b(amici|friends|compagni)\b/)) return 'friends';
    if (has(n, /\b(arcade|giocare|giochi|quiz)\b/)) return 'play';
    if (has(n, /\b(episodi|episodio)\b/)) return 'episodes';
    if (has(n, /\b(missioni|missione)\b/)) return 'missions';
    return null;
  }

  function seenState(t, spoilerMode) { return t.seen === true; }

  function answerPersonal(kind, q, ctx) {
    var T = ctx.ix.titles, seenN = T.filter(function (t) { return t.seen === true; }).length, tot = T.length;
    var refs = [], L = [];
    if (!tot) return { text: 'Non riesco a leggere la tua timeline in questo momento: apri Miss Minutes dall’app per consultare i tuoi dati.', refs: [], personal: true };
    var unseen = T.filter(function (t) { return t.seen !== true; }).sort(function (a, b) { return a.num - b.num; });
    if (kind === 'advice') {
      var nxt = unseen.slice(0, 3);
      if (!nxt.length) return { text: 'Hai visto tutti i ' + tot + ' titoli. Non resta nulla da recuperare nella Timeline.', refs: [{ label: 'Arcade', link: 'page:arcade' }], personal: true };
      L.push('Seguendo l’ordine della guida, i prossimi per te sono:');
      nxt.forEach(function (t, i) { L.push((i + 1) + '. ' + t.title + ' (N°' + t.id + (t.saga ? ' · ' + t.saga : '') + ')'); refs.push({ label: t.title, link: 'item:' + t.id }); });
      L.push('Sto solo guardando cosa ti manca e l’ordine, non i tuoi gusti: nessuno spoiler, promesso.');
      return { text: L.join('\n'), refs: refs, personal: true };
    }
    if (kind === 'progress') {
      var pct = Math.round(seenN * 1000 / tot) / 10;
      return { text: 'Hai segnato come visti ' + seenN + ' titoli su ' + tot + ' (' + String(pct).replace('.', ',') + '%).', refs: [{ label: 'Timeline', link: 'tab:timeline' }], personal: true };
    }
    if (kind === 'missing') {
      var f = findEntities(ctx.ix, q, 3, ['titolo', 'universo']);
      var sub = unseen;
      var nq = norm(q);
      var saga = T.filter(function (t) { return t.saga && nq.indexOf(norm(t.saga.replace(/^\d+[A-Z]?\s*·\s*/, ''))) >= 0; });
      if (saga.length) sub = unseen.filter(function (t) { return saga.some(function (s) { return s.saga === t.saga; }); });
      else if (/\bfilm\b/.test(nq)) sub = unseen.filter(function (t) { return /film/.test(t.kind || ''); }).length ? unseen.filter(function (t) { return /film/.test(t.kind || ''); }) : unseen;
      L.push('Ti mancano ' + sub.length + ' titoli' + (sub.length !== unseen.length ? ' (su ' + unseen.length + ' non visti in totale)' : '') + '.');
      sub.slice(0, 10).forEach(function (t) { L.push('• ' + t.title + ' (N°' + t.id + ')'); refs.push({ label: t.title, link: 'item:' + t.id }); });
      if (sub.length > 10) L.push('…e altri ' + (sub.length - 10) + ': li trovi nella Timeline.');
      return { text: L.join('\n'), refs: refs, personal: true };
    }
    if (kind === 'ratings') {
      var rated = T.filter(function (t) { return t.rating > 0; }).sort(function (a, b) { return b.rating - a.rating || a.num - b.num; });
      if (!rated.length) return { text: 'Non hai ancora assegnato voti. Valuta un titolo dalla sua scheda e lo troverò qui.', refs: [{ label: 'Classifiche', link: 'page:rankings' }], personal: true };
      L.push('I tuoi titoli meglio votati:');
      rated.slice(0, 8).forEach(function (t) { L.push('• ' + t.title + ' — ' + String(t.rating).replace('.', ',') + '/5'); refs.push({ label: t.title, link: 'item:' + t.id }); });
      refs.push({ label: 'Classifiche', link: 'page:rankings' });
      return { text: L.join('\n'), refs: refs, personal: true };
    }
    if (kind === 'live') {
      var lv = ctx.live || [];
      if (!lv.length) return { text: 'Non ho uscite da mostrarti adesso: apri TVA Live per aggiornare il calendario.', refs: [{ label: 'TVA Live', link: 'cen:live' }], personal: true };
      L.push('Dal calendario TVA Live (' + (ctx.liveNote || 'dati locali') + '):');
      lv.slice(0, 6).forEach(function (x) { L.push('• ' + x.title + (x.date ? ' — ' + fmtDate(x.date) : '') + (x.status ? ' (' + x.status + ')' : '')); });
      L.push('Le date “provvisorie” non sono confermate per l’Italia.');
      return { text: L.join('\n'), refs: [{ label: 'TVA Live', link: 'cen:live' }], personal: true };
    }
    if (kind === 'card') {
      var p = Math.round(seenN * 1000 / tot) / 10;
      return { text: 'La tua Tessera TVA riflette ' + seenN + '/' + tot + ' titoli visti (' + String(p).replace('.', ',') + '%). Rango, distintivi e cornici li vedi nella Tessera.', refs: [{ label: 'Tessera TVA', link: 'tab:tessera' }], personal: true };
    }
    if (kind === 'friends') return { text: 'Gli amici si gestiscono dalla sezione Friends. Per ora non leggo i loro dati: il confronto con gli amici arriverà con Friends 3.0.', refs: [{ label: 'Friends', link: 'tab:friends' }], personal: true };
    if (kind === 'play') return { text: 'Vuoi allenare la memoria? Arcade e Quiz ti aspettano.', refs: [{ label: 'Arcade', link: 'page:arcade' }, { label: 'Quiz', link: 'page:quiz' }], personal: true };
    if (kind === 'episodes') return { text: 'Gli episodi con i tuoi voti e visti sono nella scheda della serie. Non leggo ancora i singoli episodi: apri Episodes per consultarli.', refs: [{ label: 'Timeline', link: 'tab:timeline' }], personal: true };
    if (kind === 'missions') return { text: 'Missioni e Stagioni sono nella Centrale TVA.', refs: [{ label: 'Centrale TVA', link: 'cen:missioni' }], personal: true };
    return null;
  }

  function compare(ctx, q) {
    var n = norm(q), m = /(?:differenza|differenze|confronta|confronto|paragona)\s+(?:tra|fra|di)?\s*(.+?)\s+(?:e|con|vs|o)\s+(.+)$/.exec(n) || /(.+?)\s+(?:vs|contro|o)\s+(.+)$/.exec(n);
    var ents = [];
    if (m) { [m[1], m[2]].forEach(function (s) { var f = findEntities(ctx.ix, s, 1); if (f[0]) ents.push(f[0]); }); }
    if (ents.length < 2) ents = findEntities(ctx.ix, q, 4).filter(function (e) { return e.kind !== 'titolo'; }).slice(0, 2);
    if (ents.length < 2 || ents[0] === ents[1]) return null;
    var L = ['Confronto: ' + ents[0].name + ' ↔ ' + ents[1].name], refs = [];
    ents.forEach(function (e) {
      var part = ['• ' + e.name];
      if (e.universe) part.push(e.universe);
      if (e.host && e.host.levelName) part.push('livello ' + e.host.level + ' (' + e.host.levelName + ')');
      if (e.text) part.push(e.text);
      else if (e.host && e.host.power) part.push(e.host.power);
      if (e.source) part.push('rif. ' + e.source);
      L.push(part.join(' — '));
      if (e.link) refs.push({ label: e.name, link: e.link });
    });
    var a = ents[0], b = ents[1];
    var link = a.host && (a.host.conns || []).filter(function (c) { return b.host && c.id === b.host.id && c.rtype !== 'titolo'; })[0];
    if (link) L.push('Legame diretto (dati dell’app): ' + String(link.label).toLowerCase() + ' — da ' + a.name + ' verso ' + b.name + '.');
    if (a.host && b.host && a.host.level != null && b.host.level != null && a.host.level !== b.host.level) {
      L.push('Sul piano dei poteri (scala dell’app, non dei fumetti) ' + (a.host.level > b.host.level ? a.name : b.name) + ' ha un livello più alto: è una scala interna della guida, non un verdetto.');
    }
    L.push('Ipotesi: chi vincerebbe dipende dalla storia e dall’autore; qui ti do solo i fatti disponibili.');
    var uniq0 = (a.universe || '') !== (b.universe || '');
    if (uniq0 && a.universe && b.universe) L.push('Attenzione: provengono da continuità diverse (' + a.universe + ' / ' + b.universe + ').');
    return { text: L.join('\n'), refs: refs, entities: ents };
  }

  /* ---------- API ---------- */
  function create(opts) {
    var ix = build(opts);
    var spoilerOn = true;

    function ask(question, state) {
      state = state || {};
      var q = String(question || '').trim().slice(0, 1000);
      var n = norm(q);
      var ctx = { ix: ix, live: state.live || [], liveNote: state.liveNote };
      var out = { text: '', refs: [], tag: 'locale', personal: false, entities: [], withheld: [], intent: 'sconosciuto', confidence: 0 };
      if (!n) { out.text = 'Dimmi pure cosa vuoi sapere.'; return out; }

      if (/^(ciao|salve|hey|buongiorno|buonasera|ehi)\b/.test(n) && n.split(' ').length <= 3) {
        out.text = 'Ciao, sono Miss Minutes. Chiedimi di personaggi, universi, fumetti, di cosa guardare o dei tuoi progressi.';
        out.intent = 'saluto'; out.confidence = 1; return out;
      }
      var pk = personalIntent(n);
      var ents0 = findEntities(ix, q, 4);
      // una domanda con un'entita' esplicita e un verbo di conoscenza ("chi e", "parlami") resta lore anche se contiene parole ambigue
      var loreCue = /\b(chi e|chi sono|cos e|che cos e|parlami|spiegami|raccontami|origine|poteri|storia di)\b/.test(n);
      if (pk && !(loreCue && ents0.length && pk !== 'missing' && pk !== 'progress')) {
        var pa = answerPersonal(pk, q, ctx);
        if (pa) { pa.intent = 'personale:' + pk; pa.confidence = 1; pa.tag = 'locale'; pa.entities = []; pa.withheld = []; return pa; }
      }
      if (/\b(differenza|differenze|confronta\w*|confronto|paragona\w*|vs|contro)\b/.test(n) || /\be\b.*\bo\b/.test(n) && /\bmeglio|piu forte\b/.test(n)) {
        var c = compare(ctx, q);
        // "confrontali", "qual e la differenza?": senza nomi espliciti si usano le ultime due entita' della conversazione
        if (!c && !ents0.length && state.lastEntities && state.lastEntities.length >= 2) {
          var pv = state.lastEntities.map(function (id) { return ix.byId[id]; }).filter(function (e) { return e && e.kind !== 'titolo'; }).slice(0, 2);
          if (pv.length === 2) c = compare(ctx, pv[0].name + ' vs ' + pv[1].name);
        }
        if (c) { c.intent = 'confronto'; c.confidence = 0.8; c.tag = 'locale'; c.withheld = []; return finalize(c, state); }
      }
      var ents = ents0;
      // domande di continuita' sull'ultimo soggetto
      var nW = n.split(' ').filter(Boolean).length;
      var refersBack = /^(e |ma |approfondisci|dimmi di piu|piu dettagli|e lui|e lei|e suo|e sua|e i suoi|e le sue)/.test(n) ||
        (nW <= 8 && /\b(lui|lei|loro|suo|sua|suoi|sue|quello|quella|quelli|quelle|costui|poteri|origini?|debolezz\w+|alleat\w+|nemic\w+|famiglia|parenti|storia|motivo|perche)\b/.test(n));
      if (!ents.length && refersBack && state.lastEntities && state.lastEntities.length) {
        var prev = state.lastEntities.map(function (id) { return ix.byId[id]; }).filter(Boolean);
        if (prev.length) { ents = prev.slice(0, 1); out.followUp = true; }
      }
      if (/\b(parenti|famiglia|fratell|sorell|padre|madre|figli|alleat|nemic|legat|relazion|collegat)/.test(n) && ents.length) {
        var e0 = ents[0], rel = relationsOf(ix, e0, 10);
        if (rel.length) {
          out.intent = 'relazioni'; out.confidence = 0.8; out.entities = [e0.id];
          out.text = 'Legami di ' + e0.name + ' (dati dell’app):\n' + rel.map(function (r) { return '• ' + r.name + ' — ' + r.label; }).join('\n');
          out.refs = [{ label: e0.name, link: e0.link }].concat(rel.slice(0, 6).map(function (r) { return { label: r.name, link: 'char:' + r.id }; })).filter(function (r) { return r.link && r.link !== 'null'; });
          return finalize(out, state);
        }
      }
      if (!ents.length) {
        out.intent = 'sconosciuto'; out.confidence = 0; out.needsOnline = true;
        out.text = pick(TONE.empty, n) + '\nProva con il nome di un personaggio, di un universo (es. Terra-616), di un evento o di un titolo.';
        return out;
      }
      // dal piu' pertinente: se compare un titolo e un personaggio privilegia i non-titolo salvo domanda esplicita
      var main = ents.filter(function (e) { return e.kind !== 'titolo'; })[0] || ents[0];
      var others = ents.filter(function (e) { return e !== main; }).slice(0, 2);
      out.intent = 'scheda'; out.confidence = main.curated || main.host || main.title || main.kind === 'universo' ? 0.9 : 0.5;
      out.entities = [main.id];
      if (main.spoiler && spoilerOn && !state.reveal) {
        out.withheld = [main.id];
        out.text = main.name + ': la scheda contiene spoiler su eventi o finali. Tocca “Mostra comunque” per leggerla.';
        out.refs = main.link ? [{ label: main.name, link: main.link }] : [];
        return out;
      }
      var asp = aspectOf(n); var d = describe(main, ctx, asp); out.text = d.text; out.refs = d.refs; out.aspect = asp; if (d.missing) { out.needsOnline = true; out.confidence = 0.4; }
      if (!main.curated && !main.host && !main.title && main.kind !== 'universo') out.text += '\nHo poche informazioni affidabili su questo.';
      if (others.length && asp === 'generale') { out.text += '\nVedi anche: ' + others.map(function (e) { return e.name; }).join(', ') + '.'; others.forEach(function (e) { if (e.link) out.refs.push({ label: e.name, link: e.link }); }); }
      if (main.spoiler) out.text = '⚠ Contiene spoiler.\n' + out.text;
      return finalize(out, state);
    }

    function finalize(out, state) {
      out.tag = out.tag || 'locale';
      
      return out;
    }

    // schede da inviare al gateway: solo archivio pubblico, MAI dati personali; le schede spoiler sono escluse
    function contextFor(question, state) {
      // solo archivio pubblico, MAI dati personali; le schede spoiler restano escluse se la protezione e' attiva
      var guard = !(state && state.spoilerOff);
      var ok = function (e) { return e && (!guard || !e.spoiler) && e.kind !== 'titolo'; };
      var ents = findEntities(ix, question, 6).filter(ok);
      // domande di seguito ("e lui?", "confrontali"): si aggiungono le entita' dell'ultimo turno
      var last = ((state && state.lastEntities) || []).map(function (id) { return ix.byId[id]; }).filter(ok);
      last.forEach(function (e) { if (ents.indexOf(e) < 0) ents.push(e); });
      return ents.slice(0, 5).map(function (e) {
        var txt = (e.text || '') + (e.host && e.host.power ? ' Poteri: ' + e.host.power : '') + (e.universe ? ' Universo: ' + e.universe : '') + (e.source ? ' Rif.: ' + e.source : '');
        return { id: e.id, title: e.name, text: txt.trim().slice(0, 700) };
      });
    }
    function isPersonal(question) {
      var n = norm(question); var pk = personalIntent(n);
      if (!pk) return false; var ents = findEntities(ix, question, 3);
      var loreCue = /\b(chi e|chi sono|cos e|che cos e|parlami|spiegami|raccontami|origine|poteri|storia di)\b/.test(n);
      return !(loreCue && ents.length && pk !== 'missing' && pk !== 'progress');
    }
    return {
      ask: ask, contextFor: contextFor, isPersonal: isPersonal, norm: norm,
      entity: function (id) { return ix.byId[id] || null; },
      find: function (q, k) { return findEntities(ix, q, k || 5); },
      stats: function () { var k = {}; ix.entries.forEach(function (e) { k[e.kind] = (k[e.kind] || 0) + 1; }); return { entries: ix.entries.length, byKind: k, curated: ix.entries.filter(function (e) { return e.curated; }).length }; },
      setSpoilerProtection: function (on) { spoilerOn = on !== false; },
      linkOf: function (id) { var e = ix.byId[id]; return e ? e.link : null; }
    };
  }

  var API = { create: create, norm: norm, fmtDate: fmtDate };
  if (typeof module !== 'undefined' && module.exports) module.exports = API; else root.MMEngine = API;
})(typeof globalThis !== 'undefined' ? globalThis : this);
