# Miss Minutes 2.0 — aggiornamento automatico dell'archivio TMDB

**Stato (27/11/2026): IMPLEMENTATO su autorizzazione dell'utente (01:25), in attesa del primo avvio reale.** Costo 0 €. Nessun Netlify, nessun GitHub Pages, nessuna modifica a TVA Live / Episodi.

## Come funziona (implementato)
- **Repo scheduler** (`Posty2001/tva-live-scheduler`, commit `080fb7f`): workflow `.github/workflows/miss-minutes-archivio.yml` — **ogni lunedì 03:41 UTC** + avvio manuale (`Run workflow`, opzione *Prova a secco*). Gruppo di concorrenza proprio `mm-archivio`; non tocca `live-scheduler.yml`, `catalog/`, il sito Pages.
- **Generazione:** il workflow avvia `tmdb-sync.yml` di marvel-timeline su `test/tva-archives` con `mm_tmdb=true`, `mm_tmdb_commit=false` (il run si ritrova da `dispatch_id` = `mm-<run>-<tentativo>`; il `run-name` di `tmdb-sync.yml` è stato esteso, il comportamento di TVA Live è invariato). Accetta solo un run **riuscito** (l'artifact viene caricato anche in caso di errore e conterrebbe il file vecchio), verifica che `main` non sia cambiato, scarica l'artifact `mm-tmdb`. Riusa il secret già esistente `TVA_DISPATCH_TOKEN`.
- **Validazione e anti-regressione** (`scripts/mm_archivio.py`, 15 prove + archivio reale accettato): schema, ≥ 50 voci, campi ben formati, date ISO, file < 1,5 MB, **nessuna perdita > 10 % di voci / sinossi / cast** rispetto all'ultima versione pubblicata, `generato` non retrocesso, schema non più vecchio. Se non passa: **nulla viene scritto**, il workflow diventa rosso e resta l'ultima versione valida.
- **SHA-256:** calcolato sui byte del file; `pointer.json` = `{versione, generato, sha256, file, n, pubblicato, precedente}`; il file è immutabile `tmdb_titoli.<sha8>.json`. Il puntatore si scrive per ultimo. Ultime 8 versioni conservate in `storico.json` (ripristino = riportare il puntatore a una versione precedente).
- **Canale indipendente:** branch dati dedicato **`mm-archivio`** dello stesso repo (orfano, creato al primo avvio), servito da `https://raw.githubusercontent.com/Posty2001/tva-live-scheduler/mm-archivio/` (HTTPS, CORS `*`). Un push su quel branch non attiva né sostituisce il sito Pages di TVA Live. Dopo la pubblicazione il workflow **verifica l'endpoint pubblico reale** (puntatore, CORS, SHA-256 del file) e diventa rosso se qualcosa non torna.
- **App** (`miss-minutes/archive.js`, già nel pacchetto, **acceso** con `config.archivio` = URL del canale; CSP `connect-src` limitata a quel percorso): pacchetto incluso → copia locale verificata → remoto. Un controllo ogni 12 h, timeout 4,5 s, solo https, scarica solo se `generato` è più recente, verifica SHA-256 e le stesse regole prima di salvare la copia locale; errore = si resta sulla versione verificata. **Offline:** pacchetto o copia locale. La Diagnostica mostra origine, data e voci dell'archivio. Nessun deploy Netlify per gli aggiornamenti dei dati.
- Il pacchetto incluso nell'app resta il paracadute (precache PWA).

## Limiti dichiarati
- **Non è stato eseguito alcun avvio reale** del workflow (il token `gh` della sandbox non è valido e non raggiungo GitHub Actions): logica provata in locale (simulazione del branch orfano, aggiornamento, invariato, rifiuto per regressione) ma il primo giro va lanciato dall'utente (Actions → «Miss Minutes - archivio TMDB» → Run workflow, con *Prova a secco* se vuole). Prima serve che `tmdb-sync.yml` modificato sia su `test/tva-archives` (pubblicato).
- Cache di raw.githubusercontent.com: fino a ~5 minuti di ritardo sul puntatore.
- L'endpoint reale dal browser dell'iPhone non è provato.
- TMDB è la fonte: errori TMDB si propagano; le correzioni dell'utente (`tmdb_overrides.json`) vincono sempre e vanno nel generatore.

## Cronologia della progettazione (storica)
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
