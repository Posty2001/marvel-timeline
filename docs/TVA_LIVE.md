# TVA Live 1.0 (solo TEST)

Sezione **Live** della Centrale TVA (5ª scheda): calendario uscite, trailer, avvisi interni, preferenze. Nessuna settima voce nella barra principale.

## Dati (JSON statici)
`assets/live/manifest.json`, `calendar.json`, `trailers.json` (stesso dominio, CSP invariata). Il browser non chiama mai TMDB/YouTube.
Generati da `tools/tva_live_build.py` (solo libreria standard, token TMDB solo da ambiente). Configurazione: `tools/live/config.json`; lista manuale verificabile: `tools/live/manual.json`.

### Come aggiornare (manuale, nessun cron, nessun commit automatico)
GitHub > Actions > **TMDB sync (manuale)** > Run workflow > branch `test/tva-archives` > attiva **solo_live_build** > scarica l'artifact **tva-live-data** (`calendar.json`, `trailers.json`, `manifest.json`, `REPORT.md`) e consegnalo per l'integrazione in `assets/live/`.
Test locali: `python3 tests/live/build_test.py` (generatore, fixture) e `python3 tests/live/ui_test.py` (interfaccia, Playwright).

### Regole di classificazione
- **Confermato**: solo con fonte ufficiale verificabile (video del canale ufficiale che riporta la stessa data, oppure voce manuale con `source_url` https ufficiale e data). Una data TMDB, anche invariata da tempo, resta **Provvisorio**. Il validatore rifiuta un "confermato" senza fonte ufficiale.
- **Provvisorio**: data TMDB non corroborata, data segnaposto (01-01 / 12-31 = solo anno), data passata con stato non aggiornato.
- **Annunciato**: nessuna data; mostra solo la finestra dichiarata dalla fonte (`window`), mai date inventate.
- **Uscito**: titoli usciti negli ultimi 14 giorni, senza etichetta di confidenza.
- **Nessuna indiscrezione** in 1.0 (stato TMDB Rumored/Canceled escluso).
- Esclusi (con motivo nel REPORT): podcast/extra, generi talk/news/reality/documentario, titoli senza societa Marvel (solo keyword), esclusioni manuali.
- YouTube: solo `@marvel` (UCvC4D8onUfXzvjTOM-dBfEA), pubblicato solo se l'identita risulta verificata (handle→channel_id e autore del feed). `@MarvelHQ` disabilitato (valutazione separata). Nessun canale diverso.
- Notizie: **non sviluppate** (nessun feed ufficiale accessibile).

### Timeline senza duplicati
Aggancio per TMDB id tramite `tmdb_map.json`/`tmdb_overrides.json` (film→scheda; serie→scheda della stagione, altrimenti scheda "intera serie"). Le voci non agganciate restano solo in Live ("Solo in Live"): nessuna scheda viene creata. Una scheda Timeline non puo essere agganciata a due voci film/serie.

### Lista manuale (`tools/live/manual.json`)
Per produzioni annunciate senza data o assenti in TMDB. Campi obbligatori: `key` (`manual:slug`), `title`, `source_name`, `source_url` (https), `verified_on`. Facoltativi: `window`, `date` (solo se la fonte la riporta), `kind`, `tmdb {type,id}`. Se `tmdb` coincide con una voce TMDB, la fonte ufficiale si fonde con quella voce (e la conferma scatta solo se la data coincide). Inizialmente vuota: nessuna informazione non verificata.

## App
- Preferenze: chiave `marvel-ultimate-timeline-live-v1` (categorie, anticipi, titoli seguiti/silenziati, nascondi gia visti), inclusa in `PROFILE_OBJ_KEYS` + validatore `NORM.live` (backup/ripristino/sync). Profili senza il campo conservano i dati locali.
- Stato per dispositivo (avvisi, visti, inbox): chiave `marvel-ultimate-timeline-live-state-v1`, **non** nel profilo (evita conflitti di sync a ogni visita).
- Avvisi (solo ad app aperta, nessuna notifica di sistema/push): nuova uscita, cambio data, passaggio a confermato, nuovo trailer, promemoria dei titoli seguiti (7/3/1/0 giorni). Primo avvio: nessun avviso (si inizializza lo stato). Deduplica per id; badge sulla scheda Centrale TVA, scheda Live e sotto-scheda Avvisi.
- Trailer: link esterni a YouTube (nessun iframe, nessuna miniatura scaricata; CSP invariata).
- Credito TMDB nella sezione (logo + frase di non-endorsement).
