# TVA Live 1.1 - aggiornamento automatico del catalogo

Due operazioni DIVERSE: (1) **aggiornare i dati nel repository** (questa fase, automatica) e (2) **pubblicare l'app** (Netlify, separata, non automatica).

## Componenti
- `tools/live_update.py`: riusa `tools/tva_live_build.py`, genera un candidato, lo confronta col catalogo in `assets/live/` e decide `unchanged | heartbeat | update | rejected`.
- `tools/live_git_commit.sh`: commit dei soli 4 file di dati (`calendar/trailers/manifest/status.json`), solo se cambiano, solo verso `test/tva-archives` (refspec fisso), rebase+retry se il branch e avanzato.
- `tmdb-sync.yml` (job `live-update`): `solo_live_build=true` + `live_commit=true`, ref `test/tva-archives`. Concorrenza `tva-live-update` (nessuna sovrapposizione), `contents: write` solo in quel job.
- Scheduler: repository separato (modello in `docs/tva-live-scheduler/repo/`), perche i cron girano solo sul branch predefinito (main, congelato).

## Regole di promozione (catalogo valido mai sostituito da dati dubbi)
Bloccano sempre (nemmeno con `live_force`): TMDB non `ok` (stale/partial/error), schema o sicurezza non validi (Confermato senza fonte ufficiale, link non https, budget), chiavi duplicate.
Bloccano salvo `live_force`: >5 nuove uscite o >3 cambi data in un solo run, rimozione anomala di uscite future (>max(2,30%)), perdita di un collegamento Timeline, declassamento da Confermato, calo >50% dei trailer, calendario vuoto. Soglie in `tools/live/config.json` (`update_gate`).
YouTube non ok: calendario aggiornato, **trailer e conferme precedenti mantenuti**, manifest segna `youtube: stale`.
Se rifiutato: nessun file scritto in `assets/live`, run rosso (email di GitHub), candidato bloccato nell'artifact `tva-live-update/rejected`.

## Ultima verifica senza commit quotidiani
Contenuto invariato = nessuna scrittura. Una volta ogni 7 giorni un commit "verifica periodica" aggiorna `generated_at` e `status.json` (`last_check`, `last_change`, `content_hash`). Ogni run registra l'esito esatto nel riepilogo del job. Gli avvisi dell'app non dipendono da `generated_at`.

## Cronologia e ripristino
Ogni cambiamento = un commit con riepilogo (nuove, date, affidabilita, trailer). Ripristino: `git checkout <commit> -- assets/live` e commit; oppure `git revert <commit>`. Artifact 30 giorni.

## Permessi minimi
- `GITHUB_TOKEN` del job `live-update`: solo `contents: write` (nessun `actions`, `workflows`, `pull-requests`...); i suoi push non avviano altri workflow.
- Token fine-grained dello scheduler (da creare): repository **solo** `Posty2001/marvel-timeline`; permessi **Actions: Read and write** (+ Metadata: Read, automatico); **nessun** Contents, Workflows, Secrets, Administration. Scadenza massima 1 anno (promemoria di rinnovo). Salvato come secret `TVA_DISPATCH_TOKEN` nel repository scheduler.

## Avvio manuale
Actions > TMDB sync (manuale) > Run workflow, **Branch: test/tva-archives**, `solo_live_build` + `live_commit` attivi (`live_force` solo per superare le soglie dopo averle ispezionate). Senza `live_commit` resta il comportamento storico (solo artifact, nessun commit).

## Test
`python3 tests/live/update_test.py` (generatore simulato, repository Git temporaneo con remoto locale, app con orologio simulato, controlli statici).


## Scheduler (Fase 1): verifica dell'esito

Il workflow `docs/tva-live-scheduler/repo/.github/workflows/live-scheduler.yml` (da installare nel repository separato `tva-live-scheduler`):

1. controlla token e raggiungibilita, memorizza lo SHA di `main` e del branch TEST;
2. avvia `tmdb-sync.yml` su `test/tva-archives` con `dispatch_id` (nome del run `TVA Live update <id>`: ritrovamento univoco);
3. attende la fine del run (max 15 minuti), scarica l'artifact `tva-live-update` e legge `RESULT.json` (`unchanged | heartbeat | update | rejected`);
4. verifica la coerenza: `main` invariato; esito coerente con la conclusione del run; per `update`/`heartbeat` il branch contiene davvero il `content_hash` validato e `status.json` registra l'esito;
5. scrive il riepilogo; `rejected`, errori e incoerenze rendono rosso lo scheduler (email di GitHub). `verified=true` e un output del job: l'eventuale pubblicazione dei JSON (Fase 2) dipendera **solo** da `verified == 'true'`.

Prova a secco: `workflow_dispatch` con `dry_run=true` esegue tutti i controlli senza scrivere (il branch deve restare allo stesso SHA).
Test: `python3 tests/live/scheduler_test.py` (36 controlli con `gh` simulato).


## Fase 2: endpoint pubblico (GitHub Pages del repository scheduler)

- `scripts/publish_catalog.py` (nel repository scheduler, testato da `tests/live/publish_test.py`, 38 controlli): rivalida i tre JSON in modo indipendente (schema, `generated_at` identico nei tre file, `content_hash` e conteggi coerenti, chiavi/duplicati, link solo https su host noti, dimensioni, nessun segreto), registra una **versione immutabile** `catalog/c/<id>/` (id = hash dei tre file; mai riscritta), rifiuta un catalogo piu vecchio del pubblicato e aggiorna `catalog/current.json`.
- Sito: `v1/current.json` + ultime 10 versioni `v1/c/<id>/*.json`. Il puntatore elenca per ogni file percorso, sha256 e byte: chi legge scarica i tre file immutabili e ne verifica l'hash, quindi non esistono letture miste.
- Workflow: `update` -> `publish` (solo se `verified == true`, dati letti dallo SHA verificato) -> `deploy` (Pages) -> `verify-endpoint` (HTTPS, CORS con Origin del sito TEST, cache, sha256, file interni non raggiungibili). Se un passo fallisce, il deploy precedente resta online.
- Impostazione manuale richiesta una tantum: Settings -> Pages -> Source: **GitHub Actions**.

## Fase 3: lettura remota nell'app (TVA Live)

Endpoint: `https://posty2001.github.io/tva-live-scheduler/v1/current.json` (puntatore) + `v1/c/<versione>/{calendar,trailers,manifest}.json` (immutabili).

Regole del caricamento (blocco `tva-live-js` di `index.html`, nessun'altra sezione toccata):
1. Si leggono in parallelo: dati inclusi nell'app, copia locale dell'ultima versione verificata, endpoint remoto (timeout 9 s, `credentials: omit`, nessun referrer).
2. Un catalogo remoto o locale e accettato solo se: dimensioni e SHA-256 dei tre file coincidono col puntatore; l'id di versione e l'hash dei tre hash (nessuna combinazione di versioni diverse); `generated_at` identico nei tre file e nel puntatore, non nel futuro (> 2 giorni); schema 1; conteggi coerenti; ogni voce valida, chiavi uniche, link https verso host noti; percorsi solo `c/<versione>/<nome>.json`. Senza `crypto.subtle` non si accetta nulla di remoto.
3. Tra i candidati validi vince il `generated_at` piu recente (a parita: remoto > copia locale > dati inclusi). Un catalogo piu vecchio non sostituisce mai uno piu recente.
4. Chiave locale `marvel-ultimate-timeline-live-remote-v1`: copia (puntatore + testi, rivalidata a ogni lettura) e soglia `floor` (generated_at piu recente accettato). Non e nel profilo/backup.
5. Se i dati mostrati sono piu vecchi della soglia (copia locale persa, rete assente) non si generano avvisi: niente avvisi "all'indietro".
6. Avvisi, preferenze, titoli seguiti: logica invariata (`computeAlerts` e le chiavi utente non sono stati modificati).
7. Rientro in primo piano dopo 30+ minuti: nuovo controllo dell'endpoint.

CSP: `connect-src` aggiunge solo il prefisso `https://posty2001.github.io/tva-live-scheduler/v1/`. Service worker: invariato (solo build stamp); il gestore generico network-first inoltra gia le GET cross-origin CORS e salva le risposte 200.

Test: `tests/live/remote_test.py` (67), `tests/live/sw_remote_test.py` (6, service worker reale).

### Fase 3.1: indicatore della fonte (correzione dal collaudo iPhone)

Causa: offline il service worker (network-first con ripiego sulla cache) serviva il vecchio `current.json` con stato 200; l'app lo trattava come lettura online (riprodotto in `sw_remote_test.py`). Secondo percorso: app ripresa dalla memoria senza ricaricamento, che manteneva l'etichetta della sessione precedente.
Correzione:
- `sw.js`: i soli `.json` serviti dalla cache portano `X-TVA-From-Cache: 1` (mai navigazioni, redirect, risposte opache; resto invariato).
- App: un puntatore con quella intestazione e una copia verificata ma NON una verifica online (fonte `cache`, motivo "rete non raggiungibile"). "Aggiornamento online verificato" solo se il puntatore e stato letto dalla rete; mostra l'orario. In copia salvata mostra l'ultima verifica online reale (`at`, registrata solo in caso di lettura live).
- Eventi `online`/`offline` e rientro in primo piano ricontrollano la fonte (cambio di connettivita, 30 min, tentativo precedente fallito); con `navigator.onLine === false` e dati in memoria compare l'avviso "ora offline".

## Regola dei mercati e recupero (build 20261124-0240-final)
- **Conferma per mercato** (`tools/tva_live_build.py`): il mercato di un video ufficiale si legge dal TITOLO (UK, USA, Italia, altro paese, non qualificato). Un film e "Confermato" solo con una fonte ufficiale per l'Italia; una serie anche con un video non qualificato per paese; mai con quello di un solo altro paese. La data italiana (`dateIT`) ha priorita (`date`), la data TMDB resta in `dateTMDB`; `dateBasis` = IT|TMDB|GLOBAL; `officialDates` elenca le date ufficiali per mercato (mostrate in "Perche?").
- **Recupero di emergenza**: `tools/live_recover.py` + input `live_recover_from` di `tmdb-sync.yml` + `publish_only` dello scheduler. Procedura completa e rollback: `docs/TVA_LIVE_ROLLBACK.md`.
