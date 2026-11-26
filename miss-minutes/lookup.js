/* Miss Minutes 2.0-b – ricerca di fonti aggiornate (Wikipedia/Wikidata), gratuita e senza chiave.
   Privacy: si inviano SOLO nomi di titoli/personaggi Marvel (mai la domanda, la cronologia o dati personali). Il contenuto ricevuto e' trattato come DATO.
   Gerarchia (in ordine di autorevolezza): ufficiale > archivio-app > tmdb > wikipedia/wikidata > modello. Wikipedia NON e' una conferma ufficiale.
   Fallimento = nessun fatto (mai bloccare la risposta). Cache con TTL differenziato: titoli recenti/futuri 6 h, storici 14 giorni. Testi Wikipedia: CC BY-SA 4.0. */
(function (root) {
  'use strict';
  var KEY = 'marvel-ultimate-timeline-miss-minutes-lookup-v1', TTL_RECENT = 6 * 3600e3, TTL_OLD = 14 * 86400e3, MAXC = 40, TIMEOUT = 3500;
  var HOSTS = { en: 'https://en.wikipedia.org', it: 'https://it.wikipedia.org' };
  function ttlFor(rel, today) {
    if (!rel) return TTL_RECENT;
    var d = (Date.parse(rel.slice(0, 10)) - Date.parse(today)) / 86400e3; return isFinite(d) && d > -180 && d < 400 ? TTL_RECENT : TTL_OLD;
  }
  function load(store) { try { var o = JSON.parse(store.getItem(KEY) || '{}'); return o && typeof o === 'object' ? o : {}; } catch (e) { return {}; } }
  function save(store, o) {
    try { var ks = Object.keys(o).sort(function (a, b) { return o[b].t - o[a].t; }).slice(0, MAXC), n = {}; ks.forEach(function (k) { n[k] = o[k]; }); store.setItem(KEY, JSON.stringify(n)); } catch (e) { /* cache non disponibile */ }
  }
  /* tipo dell'opera dalla descrizione breve di Wikidata/Wikipedia (non da conoscenza interna) */
  function kindOf(desc, ext) {
    var d = String(desc || '').toLowerCase(), e = String(ext || '').toLowerCase().slice(0, 220);
    if (/comic|comics|storyline|story arc|graphic novel|crossover|limited series.*comic|fumett/.test(d)) return 'fumetti';
    if (/film|movie|television series|tv series|web series|miniseries|streaming series|serie televisiva/.test(d)) return /series|serie/.test(d) && !/film/.test(d) ? 'serie' : 'film';
    if (/is an american superhero film|is a (?:\\d{4} )?american (?:superhero )?film|\\bfilm\\b/.test(e) && !/comic/.test(e)) return 'film';
    if (/comic|storyline|story arc|graphic novel/.test(e)) return 'fumetti';
    return 'altro';
  }
  function clip(t, n) { t = String(t || '').replace(/\s+/g, ' ').trim(); return t.length > n ? t.slice(0, n - 1).replace(/\s+\S*$/, '') + '…' : t; }
  function parse(json, name, lang, whenISO) {
    var pages = json && json.query && json.query.pages; if (!Array.isArray(pages)) return [];
    return pages.slice().sort(function (a, b) { return (a.index || 99) - (b.index || 99); }).slice(0, 4).map(function (p) {
      var pp = p.pageprops || {}, desc = pp['wikibase-shortdesc'] || '', q = pp.wikibase_item || '', k = kindOf(desc, p.extract);
      if (!p.title || !(p.extract || desc)) return null;
      return { title: String(p.title), kind: k, desc: clip(desc, 110), extract: clip(p.extract, 260), url: 'https://' + lang + '.wikipedia.org/wiki/' + encodeURIComponent(String(p.title).replace(/ /g, '_')), qid: /^Q\d+$/.test(q) ? q : '', when: whenISO };
    }).filter(Boolean);
  }
  /* trasforma le pagine in fatti per il modello: ogni fatto dichiara fonte, classe e tipo; omonimie esplicite */
  function toFacts(name, pages, lang) {
    var out = [], kinds = {};
    pages.forEach(function (p) { kinds[p.kind] = (kinds[p.kind] || 0) + 1; });
    pages.slice(0, 3).forEach(function (p, i) {
      var tipo = p.kind === 'film' ? 'film' : p.kind === 'serie' ? 'serie TV' : p.kind === 'fumetti' ? 'opera a fumetti' : 'altro';
      out.push({ id: 'f:wp:' + p.qid + ':' + i, testo: '«' + p.title + '» (' + tipo + (p.desc ? ': ' + p.desc : '') + '). ' + p.extract, classe: 'wikipedia', fonte: 'Wikipedia (' + lang + ') ' + p.when.slice(0, 10),
        _url: p.url, _wd: p.qid ? 'https://www.wikidata.org/wiki/' + p.qid : '', _kw: [name, p.title], _when: p.when });
    });
    if (kinds.fumetti && (kinds.film || kinds.serie)) out.push({ id: 'f:wp:omonimia:' + name.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 24), testo: 'OMONIMIA su «' + name + '»: esistono sia un’opera audiovisiva (film/serie) sia un’opera a fumetti con questo nome. Distingui sempre quale; non attribuire all’una dati dell’altra.', classe: 'wikipedia', fonte: 'Wikipedia (' + lang + ') confronto risultati', _kw: [name], _when: pages[0].when });
    return out;
  }
  /* ricerca di un nome: cache -> rete (timeout) -> fatti. deps: {fetch, store, today, rel, signal} */
  async function one(name, deps) {
    var cache = load(deps.store), k = name.toLowerCase(), now = Date.now(), hit = cache[k], ttl = ttlFor(deps.rel, deps.today);
    if (hit && now - hit.t < ttl) return { facts: toFacts(name, hit.pages, hit.lang), cached: true };
    var lang = 'en', url = HOSTS.en + '/w/api.php?action=query&generator=search&gsrsearch=' + encodeURIComponent(name + ' Marvel') + '&gsrlimit=4&prop=extracts|pageprops&exintro=1&explaintext=1&exsentences=3&exlimit=max&ppprop=wikibase-shortdesc|wikibase_item&format=json&formatversion=2&origin=*';
    var ctl = new AbortController(), tm = setTimeout(function () { try { ctl.abort(); } catch (e) { /* ok */ } }, TIMEOUT);
    if (deps.signal) { if (deps.signal.aborted) ctl.abort(); else deps.signal.addEventListener('abort', function () { try { ctl.abort(); } catch (e) { /* ok */ } }, { once: true }); }
    try {
      var r = await deps.fetch(url, { signal: ctl.signal, credentials: 'omit', referrerPolicy: 'no-referrer', headers: { 'Accept': 'application/json' } });
      if (!r.ok) throw new Error('http');
      var pages = parse(await r.json(), name, lang, new Date().toISOString());
      cache = load(deps.store); cache[k] = { t: now, lang: lang, pages: pages }; save(deps.store, cache);
      return { facts: toFacts(name, pages, lang), cached: false };
    } catch (e) { return hit ? { facts: toFacts(name, hit.pages, hit.lang), cached: true, stale: true } : { facts: [], failed: true }; }   // cache scaduta meglio di niente, mai errore
    finally { clearTimeout(tm); }
  }
  /* names: [{name, rel}] (max 3) */
  async function lookup(names, deps) {
    var res = await Promise.all(names.slice(0, 3).map(function (n) { return one(n.name, Object.assign({}, deps, { rel: n.rel || '' })); }));
    return { facts: [].concat.apply([], res.map(function (r) { return r.facts; })), net: res.filter(function (r) { return !r.cached && !r.failed; }).length, failed: res.filter(function (r) { return r.failed; }).length, cached: res.filter(function (r) { return r.cached; }).length };
  }
  function clear(store) { try { store.removeItem(KEY); } catch (e) { /* ok */ } }
  var api = { lookup: lookup, parse: parse, toFacts: toFacts, kindOf: kindOf, ttlFor: ttlFor, clear: clear, KEY: KEY };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.MMLookup = api;
})(typeof window !== 'undefined' ? window : globalThis);
