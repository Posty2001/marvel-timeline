# Atlante 2.0 — A3.1 Pilota ritratti: report (25/11/2026)

Stato: **pilota predisposto, in attesa del tuo collaudo da iPhone.** Nessuna estensione alle 295 identità. A4 non avviata. Produzione (`main`), Miss Minutes e dati personali non toccati. Nessuna approvazione implicita: nessuna funzionalità è dichiarata «completata».

## 1. Chiave TMDB: riutilizzabile senza esporla
- La chiave esiste solo come Secret di GitHub Actions (`TMDB_READ_TOKEN` / `TMDB_API_KEY`), già letta lato server dai workflow `tmdb-sync` (TVA Episodes) e TVA Live.
- Ho aggiunto un job `atlante-pilot` **dentro** `tmdb-sync.yml` (sul solo branch `test/tva-archives`; un file di workflow nuovo non risulta avviabile finché non è su `main`, che è congelato). Si avvia a mano con `solo_atlante_pilot=true`.
- Il job usa il Secret, produce **solo metadati** (percorsi CDN, dimensioni, voti) e committa il solo `atlante2/data/pilot/candidati.json` (+ report) su `test/tva-archives`. La chiave non compare in output, repository o frontend (verificato da test: nessun token o `api_key=` nel repository).
- L'app mostra le miniature dal CDN `image.tmdb.org` (immagini pubbliche, nessuna chiave; già consentito dalla CSP).
- **Trasparenza:** durante la prova di avvio via API ho lanciato per errore anche un run di `tmdb-sync` con `solo_episodi=true` (solo lettura, nessun commit, nessun deploy; concluso con successo). Nessun dato è cambiato.

## 2. Candidati del pilota (dati reali da TMDB)
| Identità | Interprete verificato | Titoli verificati | Scene candidate |
|---|---|---|---|
| Iron Man MCU | Robert Downey Jr. | 9/9 | 216 |
| Thor MCU | Chris Hemsworth | 8/8 | 192 |
| Loki MCU | Tom Hiddleston | 5/5 (4 film + serie) | 120 |
| Spider-Man MCU | Tom Holland | 6/6 | 144 |
| Spider-Man Raimi | Tobey Maguire | 4/4 | 96 |
| Spider-Man Garfield | Andrew Garfield | 3/3 | 72 |
| Wolverine Fox | Hugh Jackman | 8/8 | 192 |
| Deadpool | Ryan Reynolds | 3/3 | 72 |
| Wanda Maximoff MCU | Elizabeth Olsen | 5/5 | 120 |
| Thanos MCU | Josh Brolin | 2/2 | 48 |

Fino a 24 scene per titolo (solo larghezza ≥ 1280 px, ordinate per voto TMDB).

## 3. Scoperte importanti
1. **TMDB non etichetta le scene per personaggio, né per attore.** L'endpoint `tagged_images` restituisce solo **locandine** (`poster`), non fotogrammi: 0 scene con interprete segnalato. La scelta resta quindi **visiva e manuale** (tua), con il nome dell'interprete come guida.
2. **8 ID TMDB errati nella mappa locandine esistente** (`data/atlante/blob/tmdbMap.json`): voci Fox 013–018 e 023 (Wolverine) e 024 (Deadpool 2) puntano a film diversi (es. 013 → id di *Days of Future Past*). Il pilota li ha risolti per titolo/anno. **Non li ho corretti** (toccano le locandine dell'app classica): proposta di correzione da approvare.
3. **Identità Wolverine mista:** `id-wolverine` include anche *X-Men '97 S2* (animazione): è una variante diversa. Nel pilota ho usato solo i titoli Fox; la separazione va decisa nella futura revisione identità (non l'ho modificata).
4. ***No Way Home* contiene tre Peter:** è offerto a MCU, Raimi e Garfield con avviso; scegli solo scene con l'interprete giusto.
5. Scene condivise fra identità (es. Thor e Loki nello stesso film): l'app **avvisa** e chiede conferma se la stessa scena è già usata da un'altra identità.

## 4. Cosa è stato realizzato (additivo)
- `atlante2/ritratti.js` (lazy): archivio privato **IndexedDB `tva-atlante-ritratti`**, chiave = ID identità (es. `id-iron-man`).
  - Selettore scene TMDB per titolo, miniature w300 dal CDN.
  - Ritaglio 3:4 (trascina, pizzica, cursore zoom), uscita 480×640 WebP (JPEG se il browser non codifica WebP, caso Safari).
  - **Copia privata** sul dispositivo se il CDN consente la lettura; altrimenti **riferimento** alla scena con ritaglio (nessun pixel copiato).
  - Importa da foto/file, sostituisci, ritaglia di nuovo, rimuovi (con conferma).
  - **Esporta/importa** tutti i ritratti in un unico file `.json` con validazione (formato, ID noti, MIME immagine, dimensione, percorsi); «sovrascrivi» opzionale.
- Integrazione A3: ritratto al posto dell'emblema in tile, elenchi e dossier (scheda 3:4 intera); pulsante «Ritratto privato» in ogni dossier; voce «Ritratti privati — pilota A3.1» nella Home Atlante 2.0 con l'elenco delle 10 identità.
- `tools/atlante_pilot_tmdb.py`, `tools/atlante_assets.py`, **registro asset** `data/atlante/assets.json` (ID, entità, continuità, fonte, attribuzione, condizioni d'uso, formato, stato di verifica; solo metadati), regole su unicità e foto attori.
- Nessuna immagine protetta, nessuna chiave nel repository o nello ZIP.

## 5. Persistenza e backup
- Database separato da `localStorage`, dal profilo di sincronizzazione e dai backup cloud: test verificano che chiavi `localStorage` e profilo di sync restano identici e che i dati dei ritratti non vi compaiono.
- Sopravvive a ricarica e ad aggiornamenti dell'app (l'aggiornamento cambia solo cache e codice, non il database).
- All'ingresso del primo ritratto l'app richiede lo storage persistente (`navigator.storage.persist`). **Limite iOS:** Safari può comunque eliminare i dati di un sito non usato per molto tempo; installata in Home l'app è più protetta, ma **l'unica garanzia è l'esportazione**: consigliato esportare dopo il collaudo.
- I ritratti **non** entrano nei backup esistenti (scelta voluta: restano privati); si salvano con «Esporta ritratti».

## 6. Condizioni d'uso verificate
- API TMDB: uso non commerciale con attribuzione; TMDB non concede diritti sulle immagini, che restano degli studi (staff TMDB: nessun documento di copyright per gli utenti API). Per questo le immagini sono private e fuori dal repository.
- Il testo di attribuzione TMDB è già nei Crediti dell'app; ogni ritratto registra titolo e fonte.
- Non è un parere legale; il rischio residuo (fotogrammi di terzi per uso personale) è tuo da accettare o rifiutare.

## 6b. Verifiche
- `tests/a31_test.py`: **40/40** (archivio isolato, ritaglio sui pixel, WebP/JPEG, riferimento senza CORS, duplicati, import/export con input malevoli, persistenza, nessuna chiave/immagine protetta nel repository, richieste solo a host già in CSP). `tests/a3_test.py`: 30/30.
- Regressione completa (66 suite, build `20261125-1300-a31`): stessi FAIL/BLOCKED/NOT RUN del confronto precedente (dipendenze esterne assenti, collisioni su /tmp in parallelo, FAIL storici documentati). Due differenze indagate: `ui_audit` (testo 10 px nel banner di ingresso dell'A3: **difetto mio dell'A3, corretto a 11 px**; ora 135/1 come prima, con l'unico FAIL documentato) e `b40c_test` (test di ripristino cloud, **instabile**: 33–38 pass su codice invariato, con insiemi di FAIL diversi a ogni esecuzione, anche sul commit precedente).

## 7. Cosa devi fare tu (collaudo, iPhone)
1. Aggiorna l'app con `NETLIFY_TEST_a31.zip` (TEST).
2. Atlante 2.0 → «Ritratti privati» → scegli un'identità → «Scegli una scena TMDB» → scheda del titolo → tocca una scena → inquadra il volto → «Salva ritratto».
3. Ripeti per le 10 identità e confronta **riconoscibilità** e **distinzione fra Peter MCU/Raimi/Garfield**.
4. Prova «Esporta ritratti», svuota un ritratto e «Importa da file».

## 8. Limiti del pilota (dichiarati)
- Non posso vedere le scene dalla sandbox: **la riconoscibilità la giudichi tu**. Nei test le immagini sono sintetiche.
- La scelta è manuale: con 295 identità servono ~295 scelte; stima non verificabile finché non vedi quante scene utili offre TMDB.
- La copia locale dipende da CORS del CDN TMDB (non verificabile dalla sandbox): se rifiutata, il ritratto è un riferimento (richiede rete).
- Illustrazioni originali per universi, luoghi, artefatti, eventi: **non avviate** (restano nel piano).

## 9. Decisioni richieste
1. Esito del collaudo: approvi l'estensione ad altre identità (con quale criterio di priorità) o modifichi il metodo?
2. Correggo i 8 ID errati nella mappa locandine (impatta le locandine dell'app classica)?
3. Separo la variante animata di Wolverine (X-Men '97) dall'identità Fox?
