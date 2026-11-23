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
