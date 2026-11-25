# MASTER ROADMAP – TVA ARCHIVES

> **Documento permanente e riferimento ufficiale del progetto.** Va consultato **prima** di qualsiasi sviluppo e aggiornato **dopo** ogni intervento.
> Branch: `test/tva-archives` · Creato il 24/11/2026 · Questo file non contiene codice applicativo.
> Gli elementi non ancora decisi o da chiarire sono nella sezione «Punti da chiarire» in fondo: **nessuna decisione è stata presa in autonomia** e nessun requisito è stato eliminato.
> Ultimo aggiornamento: 24/11/2026 (22:00) — integrate le decisioni dell'utente (v. «DECISIONI DELL'UTENTE»).

---

## DECISIONI DELL'UTENTE (24/11/2026)

**Friends**
* Esperienza esclusivamente privata per due persone.
* **Eliminati dalla programmazione:** «Squadre TVA» e gruppi da 2 a 6 persone.
* **TVA Group non è necessario** (non va sviluppato né adattato).
* **Si conserva TVA Live Room**, valutandone l'adattamento alla coppia.
* **Nessuna rimozione dal codice in questa fase** (le eliminazioni riguardano solo la programmazione).

**Tessera:** si usa il nome **Tessera TVA 3.0**, rispettando la numerazione già esistente. Tutti i requisiti concordati rimangono invariati.

**Firebase:** si mantengono **Realtime Database e l'autenticazione esistente**. Nessuna migrazione a Firestore e nessun servizio a pagamento senza autorizzazione esplicita. *(Questa decisione supera l'ipotesi, registrata il 12/11/2026, di usare Firestore con namespace `/f3/test` per Friends 3.0: l'impianto va riprogettato su Realtime Database e Auth esistenti, senza Cloud Functions.)*

**Arena e Arcade:** Multiverse Arena 2.0 è cancellata dalla programmazione. Si preservano tutti i giochi, i progressi e le funzionalità attualmente presenti in TVA Arcade.

**Road to Doomsday (conferma del 24/11/2026, 21:53):** **non si crea una modalità separata** («Modalità Prima di Doomsday» non va programmata). Si mantiene la funzione esistente e se ne programma il **miglioramento attraverso i tre livelli Essenziale, Consigliato e Facoltativo**, preservando missione, 16 opere, progressi, badge e XP (nessuna assegnazione duplicata). Nessuna implementazione ora.

**Area 12 – TVA Arcade e Rankings:** confermata dall'utente (verifica e rifinitura, senza reintrodurre Arena 2.0).

**Principi di rendicontazione**
* I **conteggi storici** (da documenti) sono tenuti **separati** dai conteggi **verificati nel codice** (sezione «CONTEGGI»).
* Una funzionalità **non è considerata completata** solo perché è implementata o perché ha superato i test: serve l'approvazione dell'utente.

---

## 01. Miss Minutes – Intelligence Upgrade

* Precisione delle risposte.
* Personalità e naturalezza.
* Memoria contestuale.
* Integrazione con Atlante.
* Protezione spoiler.
* Collaudo reale Gemini.
* Restyling «Holographic Intelligence» (mm5): sei schermate (Home, Conversazione, Elaborazione AI, Cronologia, Impostazioni, Gestione anomalie), mascotte olografica animata disegnata in SVG, icone vettoriali, nessuna emoji.
* Affidabilità: un solo nuovo tentativo automatico per errori temporanei del provider (500/502/503/504/529), pulsante Riprova, interruzione dell'attesa, archivio locale come alternativa, memoria locale dei soggetti per i seguiti, nessuna domanda duplicata in cronologia.
* Qualità: corretta la causa dei termini duplicati (i marcatori `[[id]]` sostituivano le parole), prompt con regole su precisione narrativa, fonti, confronti e ordini di lettura; preferenze lunghezza risposte e riferimenti bibliografici.
* mm6 (consolidamento dopo il collaudo su iPhone): componente globale visibile in tutte le sezioni dell'app (era nascosto in Home, Tessera, Friends, Classifiche da una regola CSS dell'app), X sempre visibile e distinta dalla freccia Indietro con ripristino di sezione e scorrimento, persistenza di schermata/bozza/scorrimento e registro del ciclo di vita in Diagnostica, attesa AI compatta nella chat con Interrompi sempre accessibile, instradamento verso Gemini delle domande teoriche/comparative/contestuali, prompt su confermato/ipotesi/indiscrezioni, rifiniture grafiche e correzione della dicitura sulla cronologia.
* Non incluso in mm6: Quiz e Arcade (documenti separati con timer in tempo reale) non montano il componente; la mascotte è un personaggio originale (orologio retro-cartoon con braccia, guanti e gambe), non una riproduzione del personaggio della serie; si possono fornire illustrazioni proprie in `miss-minutes/mascot/` con `manifest.json`.
* Stato: **COMPLETATA E APPROVATA** (25/11/2026), versione definitiva **mm6**. Collaudo reale su iPhone/Safari superato dall'utente. **Funzionalità congelata**: nessuno sviluppo mm7 previsto; ogni modifica futura richiede una richiesta esplicita dell'utente. Riferimento Git stabile: branch remoto `release/miss-minutes-1.0-mm6` fissato al commit app `8330576` (il proxy dell'ambiente rifiuta il push dei tag; il tag annotato `miss-minutes-1.0-mm6` esiste solo nel clone locale). ZIP approvato: `MISS_MINUTES_1.0_APPROVATA_mm6.zip` (identico a `NETLIFY_TEST_mm6.zip`, SHA-256 86e52669c2e794e1c5029a1a75d01df60bfb27c876ca73f7f9e916ba6e8a4bab).
* **Hotfix mm6.1 (25/11/2026, richiesto dall'utente prima del congelamento definitivo):** solo scorrimento della chat — la risposta si posiziona all'inizio del nuovo messaggio, nessuno scorrimento forzato in fondo, freccia verso il basso visibile solo quando serve, persistenza dello scorrimento di mm6 invariata. Nessuna modifica a grafica, gateway (nessun redeploy), prompt o altre funzioni. Test: `ui_mm61_test.py` 10/10, `ui_mm6_test.py` 35/35, `ui_test.py` 67/67, `engine_test.js` 37/37, `remote_test.py` 78/78. Stato: **in attesa di collaudo e approvazione dell'utente** (la versione approvata mm6 resta quella del riferimento `release/miss-minutes-1.0-mm6`).
* Cronologia stato precedente: in rifinitura, versione mm6 (storico: in rifinitura fino all'approvazione del 25/11/2026).

## 02. Atlante 2.0

* Restyling grafico completo.
* Navigazione interattiva del Multiverso.
* Dossier dinamici.
* Cronologie individuali dei personaggi.
* Rete delle relazioni.
* Collegamenti con Timeline, fumetti e Miss Minutes.
* Preferiti e collezioni.
* Progressione dell’esplorazione.

## 03. Marvel Database Expansion

Obiettivi progressivi:

* 1.000+ personaggi.
* 300+ varianti.
* 200+ artefatti e armi.
* 100+ universi e dimensioni.
* 150+ organizzazioni e squadre.
* 200+ luoghi e pianeti.
* 150+ eventi e saghe.
* 100+ specie ed entità cosmiche.

Completare anche le schede esistenti: immagini, attori, poteri, origini, relazioni, apparizioni, riferimenti ai fumetti e continuità narrative. Evitare duplicati e informazioni inventate.

*Requisiti recuperati (24/11/2026):*
* **Risoluzione delle 13 decisioni sulle identità dei personaggi** (`docs/CANDIDATI_IDENTITA_D3.md`; schede numerate con proposta in `docs/ATLANTE_2_0_DECISIONI_IDENTITA.md`, 25/11/2026): nessuna unificazione eseguita finora; ogni caso richiede la decisione dell'utente.
* **Verifica dell'attribuzione TMDB e completamento delle 7 locandine mancanti:** titoli 073, 074, 077, 086, 107, 115, 125 (oggi con emblema di ripiego); logo ufficiale TMDB mancante (`assets/images/tmdb-logo.svg`). Verificare i diritti d'uso di ogni immagine.
* **Correzioni ai dati emerse dall'audit del 15/10/2026:** sinossi/continuità di alcune schede (es. N°046, 091–092, 119–120, 134), post-credit (N°094, 121, 123), schema anno/ambientazione, date di uscita e cast (027, 131, 132, 135–139), streaming in Italia, prerequisiti incoerenti. Da riconciliare con la build attuale, solo con fonti verificabili.

## 04. Tessera TVA 3.0 (ex «Tessera TVA 2.0»)

*Nome ufficiale: Tessera TVA 3.0, in continuità con la numerazione già esistente. Tutti i requisiti sotto restano invariati. Base già presente nel codice: avatar, cornici, temi, effetti, layout, editor, esportazione PNG, Variant ID (da non perdere).*

* Correzione delle sovrapposizioni grafiche.
* Ottimizzazione responsive.
* Sfondi statici e animati.
* Cornici e rarità.
* Avatar.
* Titoli personalizzabili.
* Emblemi.
* Universo di appartenenza.
* Personaggio preferito.
* Temi cromatici.
* Badge e trofei esponibili.
* Statistiche personali.
* Personalizzazioni sbloccabili.
* Identità unica collegata a Friends.

## 05. Missioni TVA 2.0 / Evolution

* Missioni giornaliere.
* Missioni settimanali.
* Missioni multiversali.
* Missioni leggendarie.
* Missioni segrete.
* Ricompense XP e personalizzazioni esclusive.
* Integrazione con tutte le sezioni.
* Conservazione delle missioni, degli XP, dei ranghi e dei badge esistenti.

## 06. Quiz Marvel Expansion

Obiettivo progressivo: 5.000+ domande.

* MCU: 1.000.
* Fumetti: 1.500.
* Spider-Verse: 500.
* X-Men e mutanti: 500.
* Entità cosmiche: 400.
* Multiverso: 400.
* Artefatti e poteri: 400.
* Easter egg e curiosità: 300.

Preservare e ampliare ruota, campagne dei 9 mondi, Prove Supreme, boss, combo, difficoltà e timer da 30 secondi.

Controllare correttezza, ambiguità e duplicati delle domande.

## 07. TVA Friends 3.0

Esperienza privata esclusivamente per due persone.

* Account personali.
* Identità Variante collegata alla Tessera.
* Legame Nexus permanente.
* Chat in tempo reale.
* Confronto TVA Rankings.
* Quiz e duelli 1 vs 1.
* Organizzazione serate Marvel.
* Match sui film da vedere insieme.
* Archivio privato condiviso.
* Centro comunicazioni.
* Sincronizzazione cloud.

Recuperare e migliorare i moduli eventualmente già sviluppati.

Le Squadre Marvel sono escluse da Friends.

*Decisioni del 24/11/2026:*
* Esperienza esclusivamente per due persone. **Squadre TVA e gruppi da 2 a 6 persone sono eliminati dalla programmazione. TVA Group non è necessario.**
* **TVA Live Room si conserva:** valutarne l'adattamento alla coppia (nessuna rimozione dal codice in questa fase).
* Tecnologia: **Realtime Database + Authentication esistenti**; nessuna migrazione a Firestore né servizi a pagamento senza autorizzazione.
* *Requisito recuperato (v. area 11):* verifica SRI di Firebase e regole di sicurezza per utente F-A2 sono prerequisiti della sincronizzazione cloud.

## 08. TVA Comics Library

* Catalogo fumetti, con attenzione alle edizioni italiane.
* Ordini di lettura.
* Saghe ed eventi.
* Universi fumettistici.
* Collezione personale.
* Fumetti posseduti, letti e da acquistare.
* Progressi di lettura.
* Collegamenti con Atlante.

## 09. Timeline Immersive

* Schede avanzate di film e serie.
* Personaggi e attori.
* Curiosità ed easter egg.
* Scene post-credit.
* Riferimenti ai fumetti.
* Collegamenti narrativi.
* Integrazione Atlante ed Episodes.
* Protezione intelligente dagli spoiler.

### Road to Doomsday – miglioramento della funzione esistente (decisione del 24/11/2026)

*Stato: Da sviluppare — solo programmazione, nessuna implementazione. **Nessuna modalità separata** («Modalità Prima di Doomsday» non verrà creata): si migliora la funzione esistente.*

**Funzione esistente da mantenere:** missione speciale «Road to Doomsday — Operazione Incursione», 16 schede (N°015, 016, 041, 051, 084, 089, 095, 097, 099, 102, 108, 112, 117, 121, 123, 125), +300 XP, distinzione tra watchlist ufficiale «Countdown to Avengers: Doomsday» di Marvel/Disney+ (un consiglio, non un obbligo) e classificazioni editoriali TVA Archives (`docs/REPORT_BLOCCO2.md`).

**Miglioramento programmato — tre livelli:**
* **Essenziale:** necessario per comprendere personaggi e sviluppi già documentati.
* **Consigliato:** approfondisce vicende, personaggi e universi potenzialmente rilevanti.
* **Facoltativo:** contesto aggiuntivo o collegamenti tematici.

**Regole:** non classificare un titolo come essenziale solo perché si ipotizza la presenza di un personaggio in *Avengers: Doomsday* (N°136); distinguere collegamenti ufficialmente confermati, collegamenti narrativi dimostrabili e ipotesi editoriali; mantenere coerenti missione, 16 opere, progressi, badge e XP, preservando i premi già ottenuti ed evitando assegnazioni duplicate se una classificazione cambia.

**Punti emersi dall'audit del 15/10/2026 da risolvere in fase di progetto (decisioni dell'utente):** il percorso di 16 schede omette 16 titoli che le sue stesse tappe dichiarano essenziali (estenderlo porterebbe a 32 schede, 35 con Civil War): scegliere se dichiarare la selezione «ripasso per chi conosce già gli antecedenti» o estenderla; le mappe N°136 e N°139 sono preparazione editoriale, non prerequisiti ufficiali; peso contestuale di N°069/073/094. Date di Doomsday: «Confermato» valutato per mercato, data italiana prioritaria nell'interfaccia (v. TVA Live).

## 10. TVA Live – Completamento

* Verifica scheduler automatico.
* Calendario uscite.
* Trailer ufficiali.
* Avvisi e promemoria.
* TVA News solo se disponibile una fonte adeguata.
* Notifiche push da valutare, senza introdurre costi.

## 11. Rifinitura globale e pubblicazione

* Coerenza grafica generale.
* Home e Centrale TVA.
* Firebase e Firestore.
* Sicurezza degli account.
* Sincronizzazione cloud.
* Backup e ripristino.
* Prestazioni.
* Compatibilità Safari e iPhone.
* Installazione e aggiornamenti PWA.
* Collaudo generale.
* Pubblicazione stabile solo dopo approvazione.

*Requisiti recuperati (24/11/2026):*
* **Verifica SRI di Firebase** (hash dei due script `firebase-*-compat.js` 10.13.0 non ancora calcolati; script pronti in `tools/sri_firebase.*`, `tools/apply_sri.py`) e **regole di sicurezza per utente F-A2** (`users/{uid}`); connessa a F-A1 (autenticazione email/password), non dichiarata completamente chiusa. Includere unicità dei Variant ID e App Check, se compatibili con costo 0 €.
* **Prove su iPhone reale** per tutte le build non ancora verificate (Safari, PWA offline/installazione, safe area, VoiceOver): da eseguire dall'utente; nessun esito è considerato superato finché non lo riferisce.
* **Risoluzione dei test BLOCKED o NOT RUN** (8 BLOCKED e 10 NOT RUN nell'ultimo esito documentato `tests/RESULTS_C26.md`; FAIL preesistenti in `docs/PROBLEMI_PREESISTENTI.md`): riscrivere o ritirare in modo documentato, senza alterare i risultati per ottenere PASS.

## 12. TVA Arcade e TVA Rankings – Preservazione, verifica e rifinitura *(area confermata, 24/11/2026)*

* **Preservare tutti i giochi, i progressi e le funzionalità attualmente presenti in TVA Arcade** (Quiz Marvel, Who Am I?, Time Crisis, Secret Wars Draft, Multiverse Escape), compresi XP, missioni, ranghi e badge collegati.
* **Verifica e rifinitura di TVA Arcade e di TVA Rankings** (Rankings: classifiche personali Top numerate, Podio, Tier List, modelli per categoria, backup ZIP). Nessuna modifica senza anteprima approvata.
* **Verifica dei diritti d'uso dei 120 ritratti del Draft:** oggi 0/120 con diritti verificati; sono segnaposto/asset stilizzati di test (`docs/arcade/REPORT_RITRATTI.md`, `docs/arcade/PROBLEMI_APERTI.md`). Nessuna immagine Marvel senza i diritti necessari; applicazione della patch disclaimer («Progetto fan non ufficiale…») solo su indicazione dell'utente.
* Bilanciamento dei cosmici di vertice da osservare nel collaudo; verifica su iPhone reale (safe area, scroll, tocchi, prestazioni).
* **Multiverse Arena 2.0: cancellata** (v. sotto), senza reintrodurla. Preservare l'Arena attualmente funzionante.
* *Area confermata dall'utente il 24/11/2026.*

---

## FUNZIONALITÀ CANCELLATE

* Multiverse Arena 2.0.
* Squadre Marvel all’interno di Friends.
* Squadre TVA e gruppi da 2 a 6 persone in Friends; TVA Group (decisione del 24/11/2026; nessuna rimozione dal codice in questa fase).

Non reinserirle nella roadmap senza esplicita richiesta dell’utente. Preservare l’Arena attualmente funzionante.

## REGOLE INDEROGABILI

1. Sviluppo esclusivamente su TEST.
2. Produzione stabile congelata.
3. Costo operativo di 0 €.
4. Nessuna perdita dei dati personali.
5. Preservare tutti i moduli funzionanti.
6. Consultare la roadmap prima di ogni intervento.
7. Verificare i requisiti precedenti e confrontarli con il codice effettivo.
8. Progettare e approvare le anteprime prima dell’implementazione.
9. Sviluppare una funzionalità alla volta.
10. Consentire all’utente di provare ogni funzionalità nell’app reale.
11. Rifinire estetica, contenuti, animazioni, usabilità e comportamento finché l’utente non è completamente soddisfatto.
12. Il superamento dei test non equivale all’approvazione dell’utente.
13. Non passare alla fase successiva senza l’autorizzazione dell’utente.
14. Evitare test ridondanti, mantenendo quelli essenziali contro regressioni e perdita dei dati.
15. Aggiornare la roadmap senza eliminare requisiti futuri.

## STATI DI AVANZAMENTO

Ogni funzionalità ha uno di questi stati:

* Da sviluppare.
* In progettazione.
* In sviluppo.
* In collaudo.
* In rifinitura.
* Completata e approvata dall’utente.
* Cancellata.

Si registrano inoltre versione, commit, eventuale ZIP, problemi aperti e approvazione dell’utente.

---

## REGISTRO DI AVANZAMENTO

*Aggiornare questa tabella dopo ogni intervento. «Completata e approvata» solo dopo approvazione esplicita dell’utente (regola 12): implementazione e test superati non bastano. Ultimo aggiornamento: 24/11/2026.*

*Nota sui commit: i commit dell'app sono pubblicati sul branch `test/tva-archives` dal riallineamento del 24/11/2026. `NETLIFY_TEST_mm4.zip` è stato confrontato con l'albero risultante: i file dell'app coincidono (nessun ZIP aggiornato necessario). Il caricamento su Netlify TEST resta un'operazione manuale dell'utente.*

| N. | Funzionalità | Stato | Versione | Commit | ZIP | Problemi aperti | Approvazione utente |
|---|---|---|---|---|---|---|---|
| 01 | Miss Minutes 1.0 | **Completata e approvata** (25/11/2026, collaudo reale iPhone/Safari superato) — **congelata** | mm6 definitiva (`20261125-0030-mm6`), nessun mm7 previsto | `8330576` (app, riferimento Git stabile: branch `release/miss-minutes-1.0-mm6`; il tag locale non è pubblicabile dal proxy); gateway `tva-live-scheduler` `86262a9` | `MISS_MINUTES_1.0_APPROVATA_mm6.zip` (SHA-256 86e52669c2e794e1c5029a1a75d01df60bfb27c876ca73f7f9e916ba6e8a4bab) | Nessuno. Quiz/Arcade non montano il componente (decisione aperta, non bloccante). Il gateway deve restare quello distribuito con il prompt mm6 | **Sì** (25/11/2026) |
| 02 | Atlante 2.0 | **A3 in collaudo su iPhone** (25/11/2026; A0–A2 approvate, A4 non avviata). Stato precedente: **In progettazione** (25/11/2026): impostazione architetturale **approvata** con integrazioni; **interfaccia definitiva non approvata** (anteprime grafiche da preparare); 13 decisioni identità: 8 approvate, 3 modificate (1 Peter Parker hub, 2 Xavier, 11 Fisk hub), 2 rimandate (9 Bishop, 10 Janet), nessuna applicata; modello generale delle identità specificato; **Revisione 2 delle 14 anteprime APPROVATA dall'utente (25/11/2026) come riferimento grafico definitivo**; **A0 e A1 APPROVATE (25/11/2026); A2 (identità) eseguita a livello registro — in attesa di approvazione**; condizioni di implementazione: nessuna perdita di funzioni/informazioni/collegamenti, ritratti specifici solo se legittimi, dossier approfonditi, Multiverso con mappa+ricerca+filtri+elenco, Nexus scalabile oltre 10.000 relazioni, animazioni ottimizzate iPhone, nessun dato inventato, nessuna regressione; Bishop e Janet sospese; regole XP/badge aggiornate con i valori approvati; nessun codice dell'app scritto | — | — | — | Proposta in `docs/ATLANTE_2_0_ANALISI_E_PROPOSTA.md`; 13 decisioni sulle identità tutte aperte; correzioni audit da riconciliare con fonti; decisioni D1–D8 richieste all'utente | No |
| 03 | Marvel Database Expansion | Da sviluppare | — | — | — | Consistenza attuale del database da misurare prima di fissare la baseline | No |
| 04 | Tessera TVA 3.0 | Da sviluppare (requisiti nuovi); base esistente da preservare | — | — | — | Verificare quali requisiti sono già coperti dal codice (nessuno considerato completato) | No |
| 05 | Missioni TVA 2.0 / Evolution | Da sviluppare | — | — | — | Missioni, XP, ranghi e badge esistenti da preservare. Road to Doomsday: miglioramento a tre livelli programmato (v. 09), nessuna modalità separata | No |
| 06 | Quiz Marvel Expansion | Da sviluppare | — | — | — | Consistenza attuale del banco domande da misurare | No |
| 07 | TVA Friends 3.0 | In progettazione (da riprogettare su Realtime Database + Auth esistenti, solo coppia) | — | — | — | TVA Live Room da valutare per la coppia; SRI e regole F-A2 aperte (v. 11) | No |
| 08 | TVA Comics Library | Da sviluppare | — | — | — | — | No |
| 09 | Timeline Immersive (incl. miglioramento Road to Doomsday) | Da sviluppare | — | — | — | TVA Episodes già presente; Road to Doomsday esistente da migliorare con Essenziale/Consigliato/Facoltativo | No |
| 10 | TVA Live – Completamento | In collaudo | v. `docs/TVA_LIVE.md` | — | — | Il primo cron del 24/11 (05:17 UTC) non risulta eseguito: ricontrollare dopo il 25/11 05:17 UTC distinguendo evento `schedule` da avvio manuale | No |
| 11 | Rifinitura globale e pubblicazione | Da sviluppare | — | — | — | SRI, regole F-A2, prove iPhone reale, test BLOCKED/NOT RUN. Produzione ferma a `main` = `82a73c7`; verdetto precedente NO-GO | No |
| 12 | TVA Arcade e TVA Rankings (preservazione, verifica, rifinitura) | In collaudo (implementati, non approvati) | build TEST `mm4` (Arcade invariato) | — | — | Ritratti Draft 0/120 con diritti verificati; disclaimer non applicato; iPhone reale da verificare | No |
| — | Multiverse Arena 2.0 | Cancellata | — | — | — | — | — |
| — | Squadre Marvel in Friends | Cancellata | — | — | — | — | — |
| — | Squadre TVA, gruppi 2–6, TVA Group | Cancellata dalla programmazione (codice non rimosso) | — | — | — | — | — |

---

## PUNTI DA CHIARIRE

*Aggiornati il 24/11/2026. I punti risolti restano come traccia; nessun requisito è stato eliminato.*

### Risolti dalle decisioni dell'utente (24/11/2026)
1. ~~Friends: due persone vs gruppi~~ → solo coppia; Squadre TVA, gruppi 2–6 e TVA Group eliminati dalla programmazione; TVA Live Room conservata (adattamento da valutare); nessuna rimozione dal codice ora.
2. ~~Tessera 2.0 vs 3.0~~ → nome ufficiale **Tessera TVA 3.0**.
3. ~~Firebase/Firestore~~ → Realtime Database + Auth esistenti; niente Firestore o servizi a pagamento senza autorizzazione.
4. ~~Arena~~ → Multiverse Arena 2.0 cancellata; si preserva tutto TVA Arcade.

### Ancora aperti
5. ~~«Modalità Prima di Doomsday»~~ → risolto: nessuna modalità separata; si migliora Road to Doomsday con i tre livelli (v. area 09).
6. **Tessera 3.0:** stabilire, requisito per requisito, cosa è già coperto dal codice e cosa no, senza dare nulla per completato.
7. **TVA Live Room nella coppia:** definire come adattarla (accesso, privacy) prima di qualunque sviluppo.
8. **Altri requisiti storici da decidere:** quiz «da dove inizio» (riesporlo o no), `preferredMode` come default iniziale, locandine per titolo, peso contestuale di N°069/073/094 nel percorso Doomsday.
9. **Infrastruttura Miss Minutes:** gateway Cloudflare Worker (`miss-minutes-api`) con Gemini 3.5 Flash Lite, deploy via GitHub Actions nel repo `tva-live-scheduler`, quote 12/min, 450/giorno, 12.000/mese: rientra nel tetto di costo; da monitorare.
10. ~~Pubblicazione del codice TEST~~ → risolto il 24/11/2026: branch locale riallineato al remoto (merge, senza force push) e commit di Miss Minutes pubblicati su `test/tva-archives`.

---

## CONTEGGI

*I conteggi **storici** provengono da documenti e non sono stati riverificati nel codice. I conteggi **verificati** sono stati misurati il 24/11/2026 caricando l'app TEST (build mm4) e leggendo i dati; indicano la baseline per le aree 03 e 06. Nessun obiettivo della roadmap è considerato raggiunto.*

### Conteggi storici (da documenti, non verificati oggi)
| Elemento | Valore storico | Fonte |
|---|---|---|
| Titoli in Timeline | 138 (poi 139 con extra; 176 con 37 animati) | Registro Master; log di agosto |
| Universi | 27 | Registro Master / intro |
| Personaggi | 305 (agosto), 302 nodi nel grafo relazioni | log di agosto; Registro Master |
| Dossier archivio | 93; attori 49; cronologie 15 voci | Registro Master |
| Carte Secret Wars Draft | 120 | `docs/TEST_BRANCH.md` |
| Ritratti Draft con diritti verificati | 0/120 | `docs/arcade/PROBLEMI_APERTI.md` |
| Serie/episodi TVA Episodes | 47 serie, 496 episodi + 2 speciali | `docs/TEST_BRANCH.md` |
| Titoli senza locandina TMDB | 7 | Registro Master |
| Suite di test | 57: 33 PASS, 6 FAIL, 8 BLOCKED, 10 NOT RUN | `tests/RESULTS_C26.md` |

### Conteggi verificati nel codice (24/11/2026)
| Elemento | Valore verificato | Come |
|---|---|---|
| Titoli in Timeline | **138** | adattatore dati dell'app |
| Voci dell'indice di Miss Minutes | **502** (app + 62 schede curate del Knowledge Core): 307 personaggi, 33 universi, 6 organizzazioni, 6 eventi, 3 luoghi, 3 artefatti, 2 varianti, 1 entità, 1 dimensione, 1 fumetto, 1 adattamento, 138 titoli | statistiche del motore; **non è un conteggio del database Atlante** (mescola dati app e schede curate) |
| Schede curate Knowledge Core | **62** (verification «da verificare») | `miss-minutes/knowledge/core.json` |
| Domande del quiz (banco statico) | **216** in 9 categorie (mcu 27, fumetti 27, xmen 27, animazione 27, spider 26, avengers 26, multiverso 26, nonmcu 26, tva 4), 0 id duplicati | `quiz/index.html`; il pool effettivo include anche domande generate da catalogo e «fatti» (non misurate qui) |
| Voci catalogo episodi | **49** (`assets/episodes/index.json`) | file JSON |

### Conteggi verificati nel codice – Atlante (25/11/2026)
Misurati in sola lettura su `index.html` (build `20261125-0030-mm6`); dettaglio e anomalie in `docs/ATLANTE_2_0_ANALISI_E_PROPOSTA.md`.
| Elemento | Valore verificato |
|---|---|
| Schede totali (`card-wrap`) | **622**: char 304 (300 «contano»), item 139, att 49, anim 37, uni 27, org 17, art 16, p4 10, luo 9, pia 7, bat 4, evt 3 |
| Varianti | **14** dossier `var-` + 4 archi «variante» nel grafo (nessun tipo strutturato) |
| Relazioni | grafo 386 nodi (304 char, 49 attori, 17 org, 16 universi senza scheda), **2.454 archi orientati**: titolo 1.522, universo 692, attore 106, org 98, famiglia 28, variante 4, relazione 4; 6 non reciproci; 5 nodi isolati |
| Integrità link | `mvNavigate` 1.065, **0 rotti**; 0 riferimenti N° inesistenti |
| Lacune sui 304 personaggi | UNIVERSI assente 5 · CORRELATI 8 · POTERI 141 · NEI FUMETTI 73 · RELAZIONI 290 · 192 con una sola apparizione · campo UNIVERSI = testo libero (56 stringhe vs 27 schede `uni-`) |
| Identità | 13 gruppi candidati, **0 risolti** (5 identità dichiarate in `atlasData.identita`) |

**Da misurare prima di avviare le aree 03 e 06:** consistenza del database Atlante per tipologia (personaggi, varianti, artefatti, universi, organizzazioni, luoghi, eventi, specie ed entità) e dimensione effettiva del pool del quiz (domande per categoria dopo deduplicazione e controllo di correttezza).

---

## STORICO AGGIORNAMENTI

| Data | Intervento | Commit |
|---|---|---|
| 24/11/2026 | Creazione del documento; nessuna modifica al codice applicativo | `d99d7fd` |
| 24/11/2026 | Riallineamento branch locale/remoto (merge, no force push), pubblicazione commit Miss Minutes, verifica ZIP mm4, decisione Road to Doomsday, conferma area 12 | v. `git log` |
| 25/11/2026 | Atlante 2.0 **A3.1 – Atlante Visual Assets** (solo analisi, nessuna implementazione): analisi di TMDB, Marvel.com/API (ritirata), Marvel Database, Wikipedia/Commons, altre fonti; nessuna fonte gratuita offre ritratti Marvel riutilizzabili (L1 0 %; L2 locandine TMDB 282/295; L3 illustrazioni originali archetipiche 100 %); anteprima di 21 identità con limite dichiarato (soggetti condivisi); 5 decisioni richieste; A4 non avviata | `docs/ATLANTE_2_0_A31_ANALISI_ASSET_VISIVI.md`, `docs/atlante2/a31/` |
| 25/11/2026 | Atlante 2.0 **A3 – Dossier e navigazione** (interfaccia, **in attesa di collaudo su iPhone**; A4 non avviata): modulo additivo e lazy `atlante2/` (`a3.js`, `a3.css`, indice leggero 94 KB + 18 shard dossier ~30 KB caricati uno alla volta, immagini lazy) agganciato con tre hook minimi in `index.html` (`EXT.over` in `draw()`, stato `a3` in getState/setState, blocco `tva-a3-boot`); Home immersiva, catalogo illustrato griglia/elenco con filtri universo/continuità/tipo e rendering progressivo, ricerca globale per categoria, dossier a sezioni (solo sezioni con dati), hub e mantelli, navigazione identità/varianti/incarnazioni, apparizioni → scheda/Timeline, Indietro/X e scorrimento ripristinati; Atlante classico **invariato e fallback** (Home classica di default con banner «Atlante 2.0»; preferenza `tva-atlante-ui=v2` per avviare dalla nuova Home); generatore `tools/atlante_a3.py` (`--scrivi`/`--verifica`); verifica delle 44 classificazioni automatiche (42 confermate, 2 passate agli ambigui) e tabella numerata dei **34** collegamenti ambigui in `docs/ATLANTE_2_0_A3_LINK_AMBIGUI.md` (collegamenti originali conservati; nella nuova UI link all'hub dove la variante non è dimostrata); build `20261125-1200-a3`; test `tests/a3_test.py` 30/30; ritratti: nessuno disponibile/legittimo → emblemi; sezioni Debolezze/Trasformazioni/Equipaggiamento previste ma senza dati nel registro (non mostrate); XP/badge **non** inclusi (A5); ZIP `NETLIFY_TEST_a3.zip` (SHA-256 5979f41a7c055206e9907e509f677d47d33b589d55ad325339a233e13bb3fc7c); regressione: suite storiche invariate rispetto al commit precedente (stessi FAIL/BLOCKED/NOT RUN; `fa2_test` documentato in KNOWN_FAILS.json, identico su 8b6e667) | v. `git log`, `docs/ATLANTE_2_0_A3_REPORT.md` |
| 25/11/2026 | Atlante 2.0 **A2 – Identità** (livello registro, nessuna modifica UI/runtime): `data/atlante/identita.json` + `tools/atlante_identita.py`; 5 unificazioni (Coulson, Xavier, Ross, Mary Jane, Ravonna) con pagine come alias, hub Peter Parker e Wilson Fisk (non contati), mantelli Capitan America e Ghost Rider, Groot originale/successore, Coulson LMD, segnaposto; identità che contano 300 → 295; 76 link entranti verso pagine divise (44 proposti, 32 da decidere); Bishop e Janet sospese; verifiche PASS; fonti secondarie dichiarate | `docs/ATLANTE_2_0_A2_REPORT.md`, `data/atlante/identita.json`, `tools/atlante_identita.py` |
| 25/11/2026 | Atlante 2.0 **A0 + A1**: baseline congelata (branch `release/atlante-baseline-a0`, misure in `data/atlante/baseline_A0.json`: 304 personaggi · 27 universi · 17 organizzazioni · 16 artefatti · 9 luoghi · 7 pianeti · 3 eventi · 4 battaglie · 49 attori · 11 sezioni saghe · 1.065 link mvNavigate · 0 rotti); estrattore `tools/atlante_estrai.py` → `data/atlante/*.json` + 9 blob identici al byte; test di round-trip (`--verifica`, 31 controlli, tutti PASS) ; **nessuna modifica a index.html, sw.js, Miss Minutes**; suite essenziali Atlante: 7 PASS, 4 FAIL per la chiave `live-state-v1` di TVA Live (non causati da Atlante, documentati in `tests/KNOWN_FAILS.json`), 2 BLOCKED (`nav_test`, `uf_test`, ambiente), 1 NOT RUN (`data_test`, dipendenza esterna) | `data/atlante/`, `tools/atlante_estrai.py`, `tests/KNOWN_FAILS.json` |
| 25/11/2026 | Atlante 2.0 **Revisione 2**: analisi della UI esistente (`docs/ATLANTE_2_0_ANALISI_UI_ATTUALE.md`), 14 anteprime rifatte sulla shell reale con immagini e dati reali (universi, relazioni e apparizioni di Loki dal registro), confronto prima/dopo, correzioni (hub Peter 6/6, nessun «Missioni», Thanos resta personaggio, relazione sospetta esclusa, nessun obiettivo numerico nella UI), regole XP/badge con valori e condizioni approvati; corretto il conteggio specie/entità (pagine già presenti); solo documentazione | `docs/atlante2/revisione2/`, `docs/ATLANTE_2_0_ANALISI_UI_ATTUALE.md`, `docs/ATLANTE_2_0_REGOLE_XP_BADGE.md` |
| 25/11/2026 | Atlante 2.0: registrate le risposte alle 13 decisioni; modello generale delle identità (identità, variante, incarnazione, mantello, alias, hub, copie, cambio attore; co-apparizioni separate dalle relazioni); **14 anteprime grafiche** (canvas, sorgenti in `docs/atlante2/anteprime/`); regole XP/badge proposte; solo documentazione | `docs/ATLANTE_2_0_DECISIONI_IDENTITA.md` (Esito), `docs/ATLANTE_2_0_MODELLO_IDENTITA.md`, `docs/ATLANTE_2_0_REGOLE_XP_BADGE.md` |
| 25/11/2026 | Atlante 2.0: l'utente approva l'impostazione architetturale con integrazioni (visione enciclopedica, nuovi obiettivi, fonti autorizzate, XP/badge da concordare, Miss Minutes solo modifiche minime); presentate le 13 decisioni identità numerate; solo documentazione | `docs/ATLANTE_2_0_DECISIONI_IDENTITA.md`, `docs/ATLANTE_2_0_ANALISI_E_PROPOSTA.md` §10 |
| 25/11/2026 | Hotfix Miss Minutes mm6.1 (scorrimento chat: risposta dall'inizio, freccia verso il fondo, nessun scorrimento forzato); build `20261125-0100-mm6`; ZIP `NETLIFY_TEST_mm6.1.zip` (SHA-256 ff4f2f1b2e97fc6e9bee55c6789ebbecc8b5f29f0e0129d96279cb2ee2816b93); gateway invariato; in attesa di collaudo | v. `git log` |
| 25/11/2026 | Atlante 2.0: analisi del database (misure verificate, duplicati, incongruenze, lacune), recupero delle 13 decisioni identità e delle correzioni audit, proposta di architettura/funzionalità/grafica/piano A0–A7; **solo documentazione, nessun codice**; area 02 «In progettazione» in attesa di approvazione | `docs/ATLANTE_2_0_ANALISI_E_PROPOSTA.md` |
| 25/11/2026 | Approvazione ufficiale di Miss Minutes 1.0 (mm6) dopo collaudo reale; funzionalità congelata, nessun mm7; tag Git `miss-minutes-1.0-mm6`, ZIP approvato conservato; si passa all'analisi di Atlante 2.0 (nessun codice) | tag `miss-minutes-1.0-mm6` |
| 25/11/2026 | Miss Minutes mm6: componente globale, X/Indietro, persistenza e ciclo di vita, attesa compatta, instradamento Gemini, rifiniture UI, dicitura cronologia; ZIP `NETLIFY_TEST_mm6.zip`; stato «in rifinitura»; Atlante 2.0 non avviato | `8330576` |
| 24/11/2026 | Miss Minutes mm5 «Holographic Intelligence»: nuova interfaccia a sei schermate, affidabilità (retry limitato, Riprova, interruzione), fix duplicati, prompt di precisione, ZIP `NETLIFY_TEST_mm5.zip`; stato «in rifinitura»; Atlante 2.0 non avviato | `87879c5` |
| 24/11/2026 | Integrate le decisioni dell'utente (Friends, Tessera 3.0, Firebase, Arcade/Arena), i requisiti recuperati, l'area 12 e la sezione Conteggi; solo documentazione | v. `git log -- docs/MASTER_ROADMAP.md` |
