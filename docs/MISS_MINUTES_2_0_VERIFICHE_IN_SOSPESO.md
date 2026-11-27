# Miss Minutes 2.0 — verifiche in sospeso (non bloccanti)

Sviluppo chiuso alla build `20261127-1700-mm2e2` (commit `c1e5046`) su decisione dell'utente del 27/11/2026. Nessuna delle voci seguente impedisce l'uso; si correggono durante il normale utilizzo.

| # | Verifica non eseguita | Perché è rimasta aperta | Rischio / cosa osservare |
|---|---|---|---|
| 1 | Valutazione reale delle 123 domande sulla build mm2e.x (set V di 42 nuove incluso) | decisione dell'utente di non completarla | accuratezza ≥ 95 % **non dimostrata** (91,4 % automatico sulla vecchia build, non verificato a mano) |
| 2 | Revisione integrale delle 81 risposte originali e confronto prima/dopo | il JSON della valutazione non è mai arrivato in sessione | difetti non nominati dall'utente possono essere ancora presenti |
| 3 | Gateway ridistribuito (prompt di naturalezza/date, 429 dettagliati, `GET /v1/quota`) | deploy riservato all'utente (scheduler `96c08e5`) | finché non è ridistribuito l'app non vede i nuovi dettagli quota e il prompt nuovo |
| 4 | Limite 100→200 richieste/giorno | limiti gratuiti Gemini non pubblicati (solo AI Studio), documenti contraddittori | invariato a 100; alzarlo solo con RPD gratuita ≥ 200 verificata |
| 5 | Formato reale dei 429 di Google (`details`/`retryDelay`) | non riproducibile dalla sandbox | tipo/orario di ripristino potrebbero risultare «sconosciuti» |
| 6 | Viewport iOS (mm2e.1) su Safari reale; orari quota su iOS | sandbox senza Safari; screenshot IMG_2741 mai arrivati | possibile residuo di spostamento con tastiera |
| 7 | Primo avvio reale del workflow `miss-minutes-archivio.yml` (aggiornamento archivio TMDB) e canale `mm-archivio` | gh non utilizzabile dalla sandbox | archivio attuale = copia nel pacchetto (136/138) |
| 8 | N°077 e N°125 senza voce TMDB | servono override dell'utente in `assets/images/catalog/tmdb_overrides.json` (ID non inventati) | per questi titoli nessuna data/stato TMDB: stato di uscita non dedotto |
| 9 | Sonda grounding Gemini | non autorizzata (richiede conferma fatturazione disattivata) | non eseguita, nessun piano a pagamento |

Strumenti già pronti per ogni ripresa futura: runner in-app «Valutazione risposte» (sospendibile/riprendibile), `python3 tools/mm_eval_report.py --confronta PRIMA.json DOPO.json`.
