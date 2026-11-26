# Miss Minutes 2.0 — aggiornamento automatico dell'archivio TMDB (progetto)

**Stato: progettato; il lato app è implementato e testato ma SPENTO (nessuna richiesta di rete). Nessun servizio esterno, workflow di pubblicazione o deploy è stato attivato.** Per accenderlo servono le autorizzazioni elencate in fondo.

## Obiettivi e vincoli
- Archivio sempre fresco (date di uscita, cast, sinossi) **senza un deploy Netlify per ogni aggiornamento** e senza toccare TVA Live / Episodi (nessun file, workflow, segreto o pointer condiviso).
- Copia locale **verificata** per l'uso offline; un aggiornamento difettoso non può mai peggiorare ciò che l'utente ha già.
- Costo 0 € (Actions nei limiti gratuiti, hosting statico gratuito), nessun dato personale in uscita: l'app fa solo due `GET` di file pubblici.

## Cosa si riusa da TVA Live (e cosa no)
Si riusa lo **schema**, non l'istanza: generazione offline con `tools/mm_tmdb.py` tramite `tmdb-sync.yml` (opzione `mm_tmdb`, chiave TMDB solo nei Secret), file immutabili con impronta + puntatore `pointer.json` con `sha256`. Si **evita** di pubblicare sullo stesso sito GitHub Pages di TVA Live: due pubblicatori sullo stesso sito si sovrascrivono a vicenda. Per questo l'archivio usa un **canale separato** con proprio gruppo di concorrenza (`mm-archivio`).

## Architettura
1. **Generazione** (cadenza settimanale + manuale): il workflow del repo scheduler avvia `tmdb-sync.yml` con `mm_tmdb=true`, `mm_tmdb_commit=false` sul branch `test/tva-archives`, scarica l'artefatto `mm-tmdb` (`tmdb_titoli.json`, `tmdb_risolti.json`).
2. **Controllo** (prima di pubblicare, tutte le regole): `python3 tools/mm_tmdb.py --verifica` e le stesse regole del client (`archive.js › validate`): schema, ≥ 50 voci, **nessuna perdita > 10 %** di voci o sinossi rispetto alla versione pubblicata, date ISO, `generato` non retrocesso, dimensione < 1,5 MB. Se qualcosa fallisce: **non si pubblica nulla**, il puntatore resta sulla versione precedente e il job segnala l'errore.
3. **Pubblicazione** solo se i contenuti sono cambiati: file immutabile `tmdb_titoli.<sha8>.json` + `pointer.json` `{versione, generato, sha256, file, n}` nel **canale separato** (repo/sito dedicato `tva-archivio-dati`, branch `gh-pages`). Rollback = riscrivere il puntatore su un file precedente (i file immutabili restano).
4. **Client** (`miss-minutes/archive.js`, già nel pacchetto): ordine pacchetto incluso → copia locale verificata → remoto. Al massimo **un controllo ogni 12 h**, timeout 4,5 s, solo `https`, `credentials: omit`; scarica il file **solo se** `generato` del puntatore è più recente; verifica **SHA-256** sul testo scaricato, poi le regole di validazione; solo allora lo salva come copia locale. Qualsiasi errore = si resta sulla versione verificata già disponibile (fail-open). Copia locale corrotta → scartata, ritorno al pacchetto. Offline: pacchetto o copia locale (se più recente).
5. **Pacchetto incluso** (`knowledge/tmdb_titoli.json`, precache PWA): resta il paracadute; si aggiorna con le normali build.

## Workflow proposto (NON creato, NON attivo — da inserire solo dopo autorizzazione)
```yaml
name: Miss Minutes - archivio TMDB (aggiorna)
on: { schedule: [{ cron: '17 4 * * 1' }], workflow_dispatch: {} }
concurrency: { group: mm-archivio, cancel-in-progress: false }
permissions: { contents: read }
jobs:
  aggiorna:
    runs-on: ubuntu-latest
    steps:
      - # 1) dispatch di tmdb-sync.yml (mm_tmdb=true, mm_tmdb_commit=false) su test/tva-archives e attesa del risultato (stesso meccanismo con dispatch_id usato da TVA Live)
      - # 2) scarica l'artefatto mm-tmdb; esegue tools/mm_tmdb.py --verifica e il controllo di non-regressione contro pointer.json corrente
      - # 3) se valido E cambiato: scrive tmdb_titoli.<sha8>.json + pointer.json nel repo-canale dedicato (token con scope solo su quel repo)
```
Nessun passo tocca `live-scheduler.yml`, `catalog/` o il sito di TVA Live.

## Attivazione (decisioni dell'utente)
1. Creare il repo/sito statico dedicato (o scegliere un altro host gratuito) e un token con scope limitato a quel repo — **servizio esterno: serve la tua autorizzazione**.
2. Inserire il workflow sopra nel repo scheduler (nuovo file, nessuna modifica agli esistenti).
3. Impostare `archivio` in `miss-minutes/config.js` (URL https della cartella) e aggiungere quell'host a `connect-src` nella CSP di `miss-minutes/index.html`: una build TEST, senza altri deploy per i singoli aggiornamenti.

## Verifiche già eseguite
`node miss-minutes/tests/archive_test.js` (18 prove): spento = zero richieste; remoto valido aggiornato e salvato; offline → copia locale; limite 12 h; SHA-256 alterato rifiutato; impronta giusta ma dati peggiori rifiutati; nome file malevolo e `http` rifiutati; copia locale corrotta scartata; pacchetto non valido gestito. La Diagnostica mostra origine, data e numero voci dell'archivio e se l'aggiornamento remoto è spento.

## Limiti dichiarati
- L'endpoint remoto reale non esiste ancora: la rete reale non è stata provata (solo `fetch` simulato).
- TMDB è la fonte: errori TMDB si propagano; le correzioni dell'utente (`tmdb_overrides.json`) vincono sempre e vanno nel generatore, non nel client.
