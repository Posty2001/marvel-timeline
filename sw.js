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

const SW_BUILD = '20261125-0100-mm6';
const CACHE_PREFIX = 'marvel-timeline-cache-';   // C26: si cancellano solo le cache di questa app
const CACHE_NAME = 'marvel-timeline-cache-20261125-0100-mm6';
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

/* TVA Arcade (./arcade/...): pagine e script condivisi same-origin in cache per l'uso offline. Stessa regola delle altre shell: HTML di un'altra build non viene salvato. Le immagini sono catturate dal gestore generico alla prima visita. */
const ARCADE_PAGES = ['./arcade/', './arcade/who-am-i/', './arcade/time-crisis/', './arcade/draft/', './arcade/escape/'];
const ARCADE_FILES = ['./arcade/shared/arcade-nav.css', './arcade/shared/arcade-nav.js', './arcade/shared/progress-dashboard.js', './arcade/shared/arcade-backup.js'].concat(["./arcade/assets/draft_portraits/manifest.json", "./arcade/assets/draft_portraits/iron-man.webp", "./arcade/assets/draft_portraits/captain-america.webp", "./arcade/assets/draft_portraits/thor.webp", "./arcade/assets/draft_portraits/hulk.webp", "./arcade/assets/draft_portraits/black-widow.webp", "./arcade/assets/draft_portraits/hawkeye.webp", "./arcade/assets/draft_portraits/scarlet-witch.webp", "./arcade/assets/draft_portraits/vision.webp", "./arcade/assets/draft_portraits/doctor-strange.webp", "./arcade/assets/draft_portraits/captain-marvel.webp", "./arcade/assets/draft_portraits/black-panther.webp", "./arcade/assets/draft_portraits/ant-man.webp", "./arcade/assets/draft_portraits/wasp.webp", "./arcade/assets/draft_portraits/falcon.webp", "./arcade/assets/draft_portraits/war-machine.webp", "./arcade/assets/draft_portraits/spider-man-peter-parker.webp", "./arcade/assets/draft_portraits/spider-man-miles-morales.webp", "./arcade/assets/draft_portraits/spider-gwen.webp", "./arcade/assets/draft_portraits/venom.webp", "./arcade/assets/draft_portraits/carnage.webp", "./arcade/assets/draft_portraits/green-goblin.webp", "./arcade/assets/draft_portraits/doctor-octopus.webp", "./arcade/assets/draft_portraits/mysterio.webp", "./arcade/assets/draft_portraits/black-cat.webp", "./arcade/assets/draft_portraits/knull.webp", "./arcade/assets/draft_portraits/wolverine.webp", "./arcade/assets/draft_portraits/jean-grey.webp", "./arcade/assets/draft_portraits/cyclops.webp", "./arcade/assets/draft_portraits/storm.webp", "./arcade/assets/draft_portraits/magneto.webp", "./arcade/assets/draft_portraits/professor-x.webp", "./arcade/assets/draft_portraits/rogue.webp", "./arcade/assets/draft_portraits/gambit.webp", "./arcade/assets/draft_portraits/nightcrawler.webp", "./arcade/assets/draft_portraits/colossus.webp", "./arcade/assets/draft_portraits/mystique.webp", "./arcade/assets/draft_portraits/deadpool.webp", "./arcade/assets/draft_portraits/cable.webp", "./arcade/assets/draft_portraits/psylocke.webp", "./arcade/assets/draft_portraits/apocalypse.webp", "./arcade/assets/draft_portraits/thanos.webp", "./arcade/assets/draft_portraits/loki.webp", "./arcade/assets/draft_portraits/hela.webp", "./arcade/assets/draft_portraits/doctor-doom.webp", "./arcade/assets/draft_portraits/ultron.webp", "./arcade/assets/draft_portraits/silver-surfer.webp", "./arcade/assets/draft_portraits/galactus.webp", "./arcade/assets/draft_portraits/adam-warlock.webp", "./arcade/assets/draft_portraits/star-lord.webp", "./arcade/assets/draft_portraits/gamora.webp", "./arcade/assets/draft_portraits/rocket-raccoon.webp", "./arcade/assets/draft_portraits/groot.webp", "./arcade/assets/draft_portraits/drax.webp", "./arcade/assets/draft_portraits/nebula.webp", "./arcade/assets/draft_portraits/mantis.webp", "./arcade/assets/draft_portraits/shang-chi.webp", "./arcade/assets/draft_portraits/moon-knight.webp", "./arcade/assets/draft_portraits/ghost-rider.webp", "./arcade/assets/draft_portraits/namor.webp", "./arcade/assets/draft_portraits/sentry.webp", "./arcade/assets/draft_portraits/she-hulk.webp", "./arcade/assets/draft_portraits/luke-cage.webp", "./arcade/assets/draft_portraits/iron-fist.webp", "./arcade/assets/draft_portraits/daredevil.webp", "./arcade/assets/draft_portraits/ms-marvel-kamala-khan.webp", "./arcade/assets/draft_portraits/quicksilver.webp", "./arcade/assets/draft_portraits/hercules.webp", "./arcade/assets/draft_portraits/rune-king-thor.webp", "./arcade/assets/draft_portraits/winter-soldier.webp", "./arcade/assets/draft_portraits/captain-britain.webp", "./arcade/assets/draft_portraits/punisher.webp", "./arcade/assets/draft_portraits/mr-fantastic.webp", "./arcade/assets/draft_portraits/invisible-woman.webp", "./arcade/assets/draft_portraits/human-torch.webp", "./arcade/assets/draft_portraits/the-thing.webp", "./arcade/assets/draft_portraits/phoenix.webp", "./arcade/assets/draft_portraits/beast.webp", "./arcade/assets/draft_portraits/iceman.webp", "./arcade/assets/draft_portraits/archangel.webp", "./arcade/assets/draft_portraits/emma-frost.webp", "./arcade/assets/draft_portraits/jubilee.webp", "./arcade/assets/draft_portraits/bishop.webp", "./arcade/assets/draft_portraits/havok.webp", "./arcade/assets/draft_portraits/sabretooth.webp", "./arcade/assets/draft_portraits/juggernaut.webp", "./arcade/assets/draft_portraits/magik.webp", "./arcade/assets/draft_portraits/x-23.webp", "./arcade/assets/draft_portraits/domino.webp", "./arcade/assets/draft_portraits/cannonball.webp", "./arcade/assets/draft_portraits/legion.webp", "./arcade/assets/draft_portraits/spider-man-2099.webp", "./arcade/assets/draft_portraits/spider-woman-jessica-drew.webp", "./arcade/assets/draft_portraits/scarlet-spider-ben-reilly.webp", "./arcade/assets/draft_portraits/silk.webp", "./arcade/assets/draft_portraits/agent-venom.webp", "./arcade/assets/draft_portraits/anti-venom.webp", "./arcade/assets/draft_portraits/kingpin.webp", "./arcade/assets/draft_portraits/sandman.webp", "./arcade/assets/draft_portraits/electro.webp", "./arcade/assets/draft_portraits/kraven-the-hunter.webp", "./arcade/assets/draft_portraits/zarathos.webp", "./arcade/assets/draft_portraits/nova-richard-rider.webp", "./arcade/assets/draft_portraits/beta-ray-bill.webp", "./arcade/assets/draft_portraits/black-bolt.webp", "./arcade/assets/draft_portraits/ronan-the-accuser.webp", "./arcade/assets/draft_portraits/annihilus.webp", "./arcade/assets/draft_portraits/gladiator-kallark.webp", "./arcade/assets/draft_portraits/hyperion.webp", "./arcade/assets/draft_portraits/odin.webp", "./arcade/assets/draft_portraits/doctor-voodoo.webp", "./arcade/assets/draft_portraits/dormammu.webp", "./arcade/assets/draft_portraits/baron-mordo.webp", "./arcade/assets/draft_portraits/mephisto.webp", "./arcade/assets/draft_portraits/enchantress.webp", "./arcade/assets/draft_portraits/kang-the-conqueror.webp", "./arcade/assets/draft_portraits/red-skull.webp", "./arcade/assets/draft_portraits/surtur.webp", "./arcade/assets/draft_portraits/abomination.webp", "./arcade/assets/draft_portraits/gorr-the-god-butcher.webp", "./arcade/assets/draft_portraits/ikaris.webp"]);
/* Miss Minutes (./miss-minutes/): pagina, script e Knowledge Core same-origin in cache per l'uso offline. Un file mancante non blocca l'installazione. */
const MM_FILES = ['./miss-minutes/index.html', './miss-minutes/mm.css', './miss-minutes/config.js', './miss-minutes/engine.js', './miss-minutes/store.js', './miss-minutes/gateway-client.js', './miss-minutes/app.js', './miss-minutes/knowledge/core.json'];
function precacheMissMinutes(cache) {
  return Promise.all(MM_FILES.map(function (u) { return cache.add(new Request(u, { cache: 'no-cache' })).catch(function () { /* offline o assente */ }); }));
}

function precacheArcade(cache) {
  var pages = ARCADE_PAGES.map(function (u) {
    return fetch(new Request(u, { cache: 'no-cache' })).then(function (r) {
      if (!r || r.status !== 200) return;
      return r.clone().text().then(function (x) {
        var m = /name="tva-build"\s+content="([^"]+)"/.exec(x.slice(0, 8192));
        if (m && m[1] === SW_BUILD) return cache.put(u, r);
      });
    }).catch(function () { /* offline o assente: non blocca l'installazione */ });
  });
  var files = ARCADE_FILES.map(function (u) { return cache.add(u).catch(function () {}); });
  return Promise.all(pages.concat(files));
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
    caches.open(CACHE_NAME).then(function (cache) { return Promise.all([precacheFonts(cache), precacheAvatars(cache), precacheShell(cache), precacheQuiz(cache), precacheArcade(cache), precacheMissMinutes(cache)]); })
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

/* F3b: un JSON servito dalla CACHE (rete assente) porta l'intestazione X-TVA-From-Cache: la pagina (TVA Live) cosi' non scambia una copia salvata per una lettura online. Solo .json same/cross-origin con risposta leggibile; ogni altro contenuto resta identico. */
function markFromCache(req, cached) {
  try {
    if (req.mode === 'navigate' || cached.redirected || (cached.type !== 'basic' && cached.type !== 'cors') || !/\.json$/.test(new URL(req.url).pathname)) return cached;
    var h = new Headers(cached.headers); h.set('X-TVA-From-Cache', '1');
    return new Response(cached.body, { status: cached.status, statusText: cached.statusText, headers: h });
  } catch (e) { return cached; }
}

self.addEventListener('fetch', function (event) {
  var req = event.request;
  if (req.method !== 'GET') return;
  // Gateway Miss Minutes (Cloudflare Workers): mai intercettato ne' messo in cache (sfide e sessioni sono monouso)
  try { if (/\.workers\.dev$/.test(new URL(req.url).hostname)) return; } catch (e) { /* URL non valido: prosegue */ }

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
          if (cached) return markFromCache(req, cached);   // F3b
          return new Response(
            'Contenuto non disponibile offline. Apri la guida almeno una volta con connessione attiva.',
            { status: 503, statusText: 'Offline', headers: { 'Content-Type': 'text/plain; charset=utf-8' } }
          );
        });
      })
  );
});
