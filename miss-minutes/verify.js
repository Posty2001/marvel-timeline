/* Miss Minutes 2.0 – verificatore deterministico (nessuna AI, nessuna rete).
   Principi: il testo del modello non viene MAI alterato; i controlli sono per frase e compatibili con lo streaming (una frase si mostra solo dopo il controllo);
   un nome assente dall'archivio NON e' considerato falso (si segnala solo un conflitto con dati documentati); la presenza di una fonte non verifica l'intera risposta. */
(function (root) {
  'use strict';
  function norm(t) { return String(t == null ? '' : t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/['’`]/g, ' ').replace(/[^a-z0-9]+/g, ' ').trim(); }
  function hasWord(n, w) { return w && (' ' + n + ' ').indexOf(' ' + w + ' ') >= 0; }

  /* ---- marcatori [[id]]: si rimuovono dal testo, MAI si inserisce o sostituisce nulla; le citazioni diventano un elenco strutturato ---- */
  function resolveRefs(text, ctx, linkOf) {
    var cited = [], refs = [], markers = 0;
    var out = String(text).replace(/\s*\[\[([^\]]{1,60})\]\]/g, function (m, id) {
      markers++;
      var c = (ctx || []).filter(function (x) { return x.id === id; })[0];
      if (c) { if (cited.indexOf(id) < 0) cited.push(id); var l = linkOf ? linkOf(id) : null; if (l) refs.push({ label: c.title, link: l }); }
      return '';
    });
    out = out.replace(/https?:\/\/\S+/g, '[link rimosso]');   // nessun URL dal modello (le fonti reali sono strutturate)
    return { text: out.replace(/[ \t]+\n/g, '\n').trim(), markers: markers, cited: cited, refs: refs.filter(function (r, i, a) { return a.findIndex(function (z) { return z.link === r.link; }) === i; }).slice(0, 5) };
  }

  /* ---- frasi (senza spezzare Jr., Dr., N°, ecc.) ---- */
  var ABBR = /(?:^|\s)(?:jr|sr|dr|mr|mrs|ms|st|vs|prof|sig|ecc|es|n|no|cap|vol|ep|s|stagg)$/i;
  function sentences(text) {
    var out = [], s = 0, i, c, nx;
    for (i = 0; i < text.length; i++) {
      c = text.charAt(i);
      if (c === '\n') { if (i > s) out.push({ s: s, e: i + 1, done: true }); s = i + 1; continue; }
      if (c === '.' || c === '!' || c === '?') {
        nx = text.charAt(i + 1);
        if (nx !== '' && !/[\s"»”)*]/.test(nx)) continue;            // "3.5", "S.H.I.E.L.D."
        if (c === '.' && ABBR.test(text.slice(Math.max(0, i - 8), i))) continue;
        if (nx === '') { out.push({ s: s, e: i + 1, done: true }); s = i + 1; continue; }
        var rest = text.slice(i + 1).replace(/^[\s"»”)*]+/, '');
        if (rest === '' || /^[A-ZÀ-Ý0-9"«“#*\-•]/.test(rest)) { out.push({ s: s, e: i + 1, done: true }); s = i + 1; }
      }
    }
    if (s < text.length) out.push({ s: s, e: text.length, done: false });
    return out.filter(function (x) { return text.slice(x.s, x.e).trim(); });
  }

  /* ---- conoscenza: titoli (Timeline + alias), calendario Live, cast documentato ---- */
  var DEV = /\b(in sviluppo|in fase di sviluppo|in produzione|in post produzione|in lavorazione|in arrivo|non e ancora (?:uscit[oaie]|stat[oaie]|nelle)|deve ancora uscire|devono ancora uscire|uscira|usciranno|sara (?:rilasciat[oaie]|nelle sale|distribuit[oaie])|prossim[oa] (?:film|uscita)|previst[oa] per|ancora in (?:sviluppo|produzione|lavorazione)|non ancora (?:uscit[oaie]|rilasciat[oaie])|in uscita)\b/;
  var PAST = /\b(e uscit[oa]|sono uscit[ie]|ha incassato|ha debuttato|e stat[oa] (?:rilasciat|distribuit)|nelle sale dal|ha (?:superato|totalizzato|raggiunto) [^.]{0,30}(?:incass|miliard|milion|box office)|incassi? (?:mondial|total)|e gia nelle sale|e uscit)\b/;
  var HEDGE = /\b(inizialmente|all epoca|in origine|prima dell uscita|prima di uscire|era in (?:sviluppo|produzione)|era previst|fu annunciat|fino a|nel (?:20\d\d) era|ai tempi|quando era)\b/;
  var TRIG = /non e |non risulta|non si tratta|ciclo|fumett|interpretat|impersona|doppiat|uscit|usc[ie]r|svilupp|produzion|lavorazion|in arrivo|previst|incass|debutt|rilasciat|sale|sul grande schermo|nelle sale|veste i panni|ruolo di/;
  /* mm2.0-b: contraddizioni di formato/esistenza su un titolo del catalogo (film/serie): generali, valide per qualunque titolo Marvel */
  var FORMAT_DENY = /\bnon (?:e|risulta|sembra|si tratta di|rappresenta|costituisce)(?: essere)? (?:un |uno |il |un )?(?:film|lungometraggio|titolo cinematografico|opera cinematografica|produzione cinematografica|serie tv|serie televisiva|uscit[oa] (?:al cinema|nelle sale)|stat[oa] (?:prodott|realizzat))|\bnon (?:si riferisce|fa riferimento|corrisponde) a(?:d)? (?:un |uno |il )?(?:film|lungometraggio|titolo cinematografico|produzione)/;
  var NOT_EXIST = /\bnon (?:e|risulta|e stat[oa]) (?:mai |ancora |ufficialmente )?(?:uscit|rilasciat|distribuit|prodott|annunciat)|\bnon esiste (?:alcun |nessun |ancora )?(?:film|produzione|titolo)|\bnon e (?:mai )?esistit/;
  var NOT_QUAL = /\bnon e (?:mai |ancora )?(?:uscit|rilasciat|distribuit)\w* (?:prima|dopo|fino|in |nel|a |il |negli|entro|durante|con|ovunque|dappertutto|in tutti)/;   // «non è uscito prima di luglio» e' una precisazione temporale
  var IS_COMIC = /\b(?:e|si tratta di|riguarda|corrisponde a|indica|fa riferimento a|appartiene a|rimanda a) (?:un |uno |una |il |la |l )?(?:ciclo|arco narrativo|storyline|story arc|crossover|evento editoriale|miniserie a fumetti|numero|volume|albo|fumetto|graphic novel|serie a fumetti|trama fumettistica)\b|\bciclo fumettistic/;
  var COMIC_OK = /\banche\b|\bomonim|\bispirat|\bbasat|\btratt[ao] da|\badattament|\bdistint|\bconfond|\bdiverso da|\boltre\b|\binoltre\b|\bnei fumetti\b|\bnon va confus/;
  var Q_COMICS = /fumett|comics|\balbi\b|\balbo\b|graphic novel|storyline|story arc|ciclo|arco narrativo/;
  var VERB_ACT = /\b(interpretat[oa]|impersonat[oa]|portat[oa] sullo schermo|reso vivo|doppiat[oa])\s+(?:dall attore |dalla attrice |dall attrice |da )/;
  var NAME = '([A-ZÀ-Ý][\\p{L}\'’.\\-]+(?:\\s+(?:[A-ZÀ-Ý][\\p{L}\'’.\\-]+|Jr\\.|de|van|von|di|da)){0,3})';
  var RX_PASSIVE = new RegExp('(?:interpretat[oa]|impersonat[oa]|doppiat[oa]|portat[oa] sullo schermo)\\s+(?:dall[\'’]attore |dall[\'’]attrice |dalla attrice |da )' + NAME, 'u');
  var RX_ACTIVE = new RegExp(NAME + '\\s+(?:interpreta|ha interpretato|interpretava|interpretera|veste i panni di|presta (?:il volto|la voce) a|doppia|impersona)\\s+(?:il personaggio di |il ruolo di |la parte di )?' + NAME, 'u');

  /* riferimenti ad ALTRO rispetto al titolo (seguiti, spin-off...): le frasi su di essi non descrivono lo stato del titolo in discussione */
  var SEQ = /\b(seguito|seguiti|sequel|prequel|spin off|spinoff|prossimo capitolo|capitolo successivo|terzo capitolo|quarto capitolo|nuova stagione|stagione successiva|crossover|reboot futuro)\b/;
  /* un'affermazione e' tale solo se non negata poco prima («non e ancora uscito» non e' «e uscito») */
  function affirms(re, n) { var m = re.exec(n); if (!m) return false; var pre = n.slice(Math.max(0, m.index - 22), m.index); return !/\bnon (?:\w+ ){0,2}$/.test(pre) && !/\bmai (?:\w+ )?$/.test(pre); }

  function build(raw, today) {
    var K = { today: today || new Date().toISOString().slice(0, 10), titles: [], cast: [], actors: {} };
    raw = raw || {};
    (raw.titles || []).forEach(function (t) {
      var n = norm(t.title); if (!n) return;
      var al = [n].concat((raw.alias_titoli && raw.alias_titoli[String(t.num || t.id)] || []).map(norm));
      al = al.filter(function (a, i) { return a && al.indexOf(a) === i && (a.split(' ').length >= 2 || (raw.alias_titoli && raw.alias_titoli[String(t.num || t.id)])); });
      if (al.length) K.titles.push({ id: t.id, title: t.title, release: t.release || '', kind: t.kind || '', names: al, stato: t.stato || '', dates: (t.dates || []).filter(Boolean) });
    });
    (raw.cast || []).forEach(function (c) {
      var e = { names: (c.pers || []).map(norm), actors: (c.attori || []).map(norm), cues: (c.cues || []).map(norm), univ: c.univ || '', prod: c.prod || '' };
      K.cast.push(e); e.actors.forEach(function (a) { (K.actors[a] = K.actors[a] || []).push(e); });
    });
    K.live = (raw.live || []).map(function (x) { return { title: x.title, names: [norm(x.title)], date: x.date || '', dateIT: x.dateIT || '', status: x.confidence || x.status || '', official: x.officialDates || [] }; });
    return K;
  }

  function castFor(K, chName) { return K.cast.filter(function (e) { return e.names.indexOf(chName) >= 0; }); }
  function knownChar(K, before) {
    var n = norm(before), best = null, at = -1;
    K.cast.forEach(function (e) { e.names.forEach(function (nm) { if (nm.length < 4) return; var i = (' ' + n + ' ').lastIndexOf(' ' + nm + ' '); if (i >= 0 && i >= at) { at = i; best = nm; } }); });
    return best;
  }
  function pair(K, actorRaw, chName, sentenceNorm, isSelfCheck) {
    var a = norm(actorRaw);
    if (isSelfCheck && a === chName) return { kind: 'attore', msg: 'attore e personaggio coincidono (“' + actorRaw + '”)' };
    var ents = castFor(K, chName); if (!ents.length) return null;                       // personaggio non documentato: nessun giudizio
    var ok = ents.filter(function (e) { return e.actors.indexOf(a) >= 0; });
    if (!ok.length) {
      var other = K.actors[a];                                                           // attore sconosciuto: NON e' falso, solo non verificabile
      if (!other) return null;
      return { kind: 'attore', msg: actorRaw + ' non risulta tra gli interpreti documentati di ' + chName + ' (è documentato per: ' + other.map(function (e) { return e.names[0]; }).filter(function (x, i, z) { return z.indexOf(x) === i; }).slice(0, 3).join(', ') + ')' };
    }
    var cuesOk = [], cuesOther = [];
    ok.forEach(function (e) { cuesOk = cuesOk.concat(e.cues); });
    ents.forEach(function (e) { if (ok.indexOf(e) < 0) cuesOther = cuesOther.concat(e.cues); });
    var hitOther = cuesOther.filter(function (c) { return c && cuesOk.indexOf(c) < 0 && hasWord(sentenceNorm, c); });
    var hitOk = cuesOk.filter(function (c) { return c && hasWord(sentenceNorm, c); });
    if (hitOther.length && !hitOk.length) return { kind: 'continuita', msg: actorRaw + ' interpreta ' + chName + ' in un’altra continuità/produzione rispetto a “' + hitOther[0] + '”' };
    return null;
  }
  /* titoli citati nella frase; se un titolo e' contenuto in un altro piu' specifico (es. «Spider-Man» in «Spider-Man: Brand New Day») resta solo il piu' specifico */
  function titleHits(K, n) {
    var hits = K.titles.map(function (t) { var best = ''; t.names.forEach(function (x) { if (hasWord(n, x) && x.length > best.length) best = x; }); return best ? { t: t, m: best } : null; }).filter(Boolean);
    return hits.filter(function (h) { return !hits.some(function (o) { return o !== h && o.m.length > h.m.length && (' ' + o.m + ' ').indexOf(' ' + h.m + ' ') >= 0; }); }).map(function (h) { return h.t; });
  }
  function dateOf(s) { var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s || ''); return m ? m[0] : ''; }

  function check(sent, K, cur) {
    var v = [], n = norm(sent), m;
    /* attore / personaggio / continuita' */
    if ((m = RX_PASSIVE.exec(sent))) {
      var before = sent.slice(0, m.index), actor = m[1].replace(/[.,;]+$/, '');
      var ch = knownChar(K, before);
      if (!ch) { var run = /([A-ZÀ-Ý][\p{L}'’.\-]+(?:\s+[A-ZÀ-Ý][\p{L}'’.\-]+){0,3})[^A-ZÀ-Ý]*$/u.exec(before); ch = run ? norm(run[1]) : null; }
      if (ch) { var r = pair(K, actor, ch, n, true); if (r) v.push(r); }
    }
    if ((m = RX_ACTIVE.exec(sent))) { var r2 = pair(K, m[1].replace(/[.,;]+$/, ''), norm(m[2].replace(/[.,;]+$/, '')), n, false); if (r2) v.push(r2); }
    /* tempo / formato / esistenza: il soggetto e' il titolo citato nella frase oppure, se la frase non ne cita, quello in discussione (focus/frase precedente) */
    var hits = titleHits(K, n), subj = null, inferred = false;
    if (hits.length === 1) subj = hits[0]; else if (!hits.length && cur && cur.length === 1) { subj = cur[0]; inferred = true; }
    if (subj && !HEDGE.test(n)) {
      var rel = dateOf(subj.release), rtxt = '«' + subj.title + '»' + (inferred ? ' (titolo in discussione)' : ''), st = subj.stato || '';
      /* lo stato di uscita NON si deduce dalla sola data trascorsa: serve una fonte (stato TMDB). Una data futura documentata resta un indizio di «non ancora uscito». */
      if (!SEQ.test(n)) {
        if (DEV.test(n) && ((st === 'released' && (!rel || rel <= K.today)))) v.push({ kind: 'tempo', title: subj.title, msg: rtxt + ' risulta già uscito (' + (rel || 'stato TMDB: uscito') + ') ma è descritto come non ancora uscito' });
        else if (affirms(PAST, n) && (st === 'unreleased' || (!st && rel && rel > K.today))) v.push({ kind: 'tempo', title: subj.title, msg: rtxt + (rel ? ' risulta in uscita il ' + rel : ' risulta non ancora uscito') + ' ma è descritto come già uscito' });
        else if (NOT_EXIST.test(n) && !NOT_QUAL.test(n) && st === 'released') v.push({ kind: 'esistenza', title: subj.title, msg: rtxt + ' è in archivio come già uscito' + (rel ? ' (' + rel + ')' : '') + ' ma ne è negata l’esistenza/uscita' });
      }
      if (!COMIC_OK.test(n)) {
        if (FORMAT_DENY.test(n)) v.push({ kind: 'formato', title: subj.title, msg: rtxt + ' è un' + (subj.kind === 'serie' ? 'a serie' : ' film') + ' del catalogo, ma ne viene negato il formato' });
        else if (IS_COMIC.test(n) && !K.qcomics) v.push({ kind: 'formato', title: subj.title, msg: rtxt + ' è un titolo audiovisivo del catalogo, ma viene descritto come un’opera a fumetti' });
      }
    }
    return v;
  }

  /* scan: restituisce fino a dove il testo puo' essere mostrato (safe) e la prima violazione grave.
     Con stream in corso la frase incompleta viene trattenuta SOLO se contiene parole sensibili (attori, date, stato di uscita): altrimenti scorre libera. */
  function scan(text, K, final) {
    var ss = sentences(text), viol = null, safe = 0, i, s, vs, cur = K.focus || [], hh;
    for (i = 0; i < ss.length; i++) {
      s = ss[i]; var str = text.slice(s.s, s.e);
      if (!s.done && !final) { safe = TRIG.test(norm(str)) ? s.s : text.length; return { safe: safe, viol: viol, sentences: ss.length }; }
      hh = titleHits(K, norm(str)); if (hh.length === 1) cur = [hh[0]];
      vs = check(str, K, cur);
      if (vs.length) { viol = { at: s.s, end: s.e, kind: vs[0].kind, msg: vs[0].msg, title: vs[0].title || '', all: vs }; return { safe: s.s, viol: viol, sentences: ss.length }; }
      safe = s.e;
    }
    return { safe: text.length, viol: null, sentences: ss.length };
  }
  /* note morbide (non bloccanti): date diverse da quelle documentate */
  var MESI = { gennaio: 1, febbraio: 2, marzo: 3, aprile: 4, maggio: 5, giugno: 6, luglio: 7, agosto: 8, settembre: 9, ottobre: 10, novembre: 11, dicembre: 12 };
  function softNotes(text, K) {
    var notes = [];
    sentences(text).forEach(function (s) {
      var str = text.slice(s.s, s.e), n = norm(str), hits = titleHits(K, n);
      if (hits.length !== 1) return;
      var re = /(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})/gi, m;
      while ((m = re.exec(str))) {
        var iso = m[3] + '-' + ('0' + MESI[m[2].toLowerCase()]).slice(-2) + '-' + ('0' + m[1]).slice(-2), known = [dateOf(hits[0].release)].concat((hits[0].dates || []).map(dateOf));
        K.live.forEach(function (l) { if (l.names.some(function (x) { return hasWord(norm(hits[0].title), x); })) { known.push(l.date, l.dateIT); l.official.forEach(function (o) { known.push(o.date); }); } });
        known = known.filter(Boolean);
        if (known.length && known.indexOf(iso) < 0) notes.push('Per «' + hits[0].title + '» in archivio risultano queste date: ' + known.filter(function (x, i, a) { return a.indexOf(x) === i; }).map(function (x) { return x.slice(8, 10) + '/' + x.slice(5, 7) + '/' + x.slice(0, 4); }).join(', ') + '.');
      }
    });
    return notes;
  }
  /* titolo in discussione: quello della domanda, o (domanda di seguito) quello della domanda precedente */
  function setFocus(K, q, prevQ) {
    var h = titleHits(K, norm(q)), pq = Array.isArray(prevQ) ? prevQ : (prevQ ? [prevQ] : []);
    for (var i = 0; !h.length && i < pq.length; i++) h = titleHits(K, norm(pq[i]));      // il soggetto resta quello dell'ultima domanda che nominava un titolo
    K.focus = h.length === 1 ? [h[0]] : []; K.qcomics = Q_COMICS.test(norm(q)); return K.focus;
  }
  var api = { setFocus: setFocus, titleHits: titleHits, norm: norm, resolveRefs: resolveRefs, sentences: sentences, build: build, check: check, scan: scan, softNotes: softNotes };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.MMVerify = api;
})(typeof window !== 'undefined' ? window : this);
