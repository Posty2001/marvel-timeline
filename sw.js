// Service Worker per Marvel Multiverse — TVA Archive.
// Strategia principale: network-first con fallback su cache. Quando sei online, ricevi sempre
// la versione più recente del file (utile dato che il progetto viene aggiornato spesso);
// quando sei offline, ricevi l'ultima versione che il browser è riuscito a scaricare.
// Non pre-carica nulla per nome file esplicito: cattura dinamicamente ogni richiesta GET
// alla prima visita online, così funziona qualunque sia il nome con cui l'HTML viene caricato.
//
// Font Google: la registrazione di questo SW avviene DOPO che la pagina ha già finito di
// caricarsi (window.onload), quindi il fetch handler generico sotto non farebbe mai in tempo a
// intercettare le richieste font della primissima visita — solo dalla seconda visita online in
// poi. Per risolverlo, durante "install" questo SW scarica DIRETTAMENTE il CSS di Google Fonts
// (qui gira nel browser reale, non ha i limiti di un tool esterno), lo analizza per trovare gli
// URL dei file .woff2 referenziati, e li mette in cache esplicitamente — indipendentemente da
// quando/come la pagina stessa li carica.

const SW_BUILD = '20261112-1000-integrazione';
const CACHE_PREFIX = 'marvel-timeline-cache-';   // C26: si cancellano solo le cache di questa app
const CACHE_NAME = 'marvel-timeline-cache-20261112-1000-integrazione';
const FONT_CSS_URL = 'https://fonts.googleapis.com/css2?family=Special+Elite&family=Spectral:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap';

/* 3.2.4: ritratti avatar approvati, precaricati per l'uso offline (Tessera, editor, esportazione PNG). */
const AVATAR_ASSETS = ['agente', 'variante', 'esploratore', 'tecnologico', 'mistico', 'astratto', 'cronista', 'sentinella'].map(function (n) { return 'assets/avatars/' + n + '.webp'; });
function precacheAvatars(cache) {
  return Promise.all(AVATAR_ASSETS.map(function (u) { return cache.add(u).catch(function () { /* un asset mancante non blocca l'installazione */ }); }));
}

/* C26: la pagina della build corrente entra subito in cache: dopo un aggiornamento la guida resta apribile offline anche prima della prima navigazione. */
function precacheShell(cache) {
  return Promise.all(['./', './index.html'].map(function (u) {
    return fetch(new Request(u, { cache: 'no-cache' })).then(function (r) {
      if (!r || r.status !== 200) return;
      // C26b: non si salva HTML di una build diversa da SW_BUILD (es. deploy a meta': sw.js nuovo, index.html ancora vecchio)
      return r.clone().text().then(function (t) {
        var m = /name="tva-build"\s+content="([^"]+)"/.exec(t.slice(0, 8192));
        if (m && m[1] === SW_BUILD) return cache.put(u, r);
      });
    }).catch(function () { /* offline: nessun errore fatale */ });
  }));
}

/* Quiz Marvel (./quiz/): pagina della stessa origine, in cache per l'uso offline. Solo risorse same-origin; stessa regola di precacheShell (HTML di un'altra build non viene salvato). Le immagini TMDB del Quiz non vengono mai messe in cache da qui. */
function precacheQuiz(cache) {
  return Promise.all(['./quiz/', './quiz/index.html'].map(function (u) {
    return fetch(new Request(u, { cache: 'no-cache' })).then(function (r) {
      if (!r || r.status !== 200) return;
      return r.clone().text().then(function (x) {
        var m = /name="tva-build"\s+content="([^"]+)"/.exec(x.slice(0, 8192));
        if (m && m[1] === SW_BUILD) return cache.put(u, r);
      });
    }).catch(function () { /* offline o assente: non blocca l'installazione */ });
  }));
}

function precacheFonts(cache) {
  return fetch(FONT_CSS_URL, { mode: 'cors' })
    .then(function (cssResponse) {
      var cssForCache = cssResponse.clone();
      return cssResponse.text().then(function (cssText) {
        var matches = cssText.match(/url\(([^)]+)\)/g) || [];
        var fontUrls = matches.map(function (m) {
          return m.replace(/^url\(/, '').replace(/\)$/, '').replace(/["']/g, '');
        });
        var cachePromises = fontUrls.map(function (fontUrl) {
          return fetch(fontUrl, { mode: 'cors' })
            .then(function (fontResponse) { return cache.put(fontUrl, fontResponse); })
            .catch(function () { /* un singolo peso mancante non blocca gli altri */ });
        });
        cachePromises.push(cache.put(FONT_CSS_URL, cssForCache));
        return Promise.all(cachePromises);
      });
    })
    .catch(function () { /* offline già alla prima installazione: nessun font da pre-caricare, non è un errore fatale */ });
}

self.addEventListener('install', function (event) {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) { return Promise.all([precacheFonts(cache), precacheAvatars(cache), precacheShell(cache), precacheQuiz(cache)]); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(
          keys.filter(function (k) { return k.indexOf(CACHE_PREFIX) === 0 && k !== CACHE_NAME; })
            .map(function (k) { return caches.delete(k); })
        );
      })
      .then(function () { return self.clients.claim(); })
  );
});

// Versione leggibile dalla pagina (diagnostica ?debugLayout=1 e verifica build). Non tocca dati utente.
self.addEventListener('message', function (event) {
  var d = event.data;
  if (d && d.type === 'tva-get-version' && event.ports && event.ports[0]) {
    event.ports[0].postMessage({ swBuild: SW_BUILD, cache: CACHE_NAME });
  }
});

self.addEventListener('fetch', function (event) {
  var req = event.request;
  if (req.method !== 'GET') return;

  // Navigazione (l'HTML): rivalida sempre con il server, senza passare dalla cache HTTP del WebView
  // (una copia "fresca" li' darebbe una versione precedente anche con rete presente). Se la costruzione
  // della richiesta non e' supportata, si ricade sul comportamento precedente.
  var netReq = req;
  if (req.mode === 'navigate') {
    try { netReq = new Request(req, { cache: 'no-cache' }); } catch (e) { netReq = req; }
  }

  event.respondWith(
    fetch(netReq)
      .then(function (networkResponse) {
        // Solo risposte complete (200): niente 206 parziali (verifica build via Range) ne' errori in cache.
        if (networkResponse && networkResponse.status === 200 && !req.headers.get('Range')) {
          var responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            return cache.put(req, responseClone);
          }).catch(function () {});
        }
        return networkResponse;
      })
      .catch(function () {
        return caches.match(req, { ignoreSearch: req.mode === 'navigate' }).then(function (cached) {   // C26: la navigazione ignora la query
          if (cached) return cached;
          return new Response(
            'Contenuto non disponibile offline. Apri la guida almeno una volta con connessione attiva.',
            { status: 503, statusText: 'Offline', headers: { 'Content-Type': 'text/plain; charset=utf-8' } }
          );
        });
      })
  );
});
