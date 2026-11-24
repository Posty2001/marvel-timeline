# MASTER ROADMAP – TVA ARCHIVES

> **Documento permanente e riferimento ufficiale del progetto.** Va consultato **prima** di qualsiasi sviluppo e aggiornato **dopo** ogni intervento.
> Branch: `test/tva-archives` · Creato il 24/11/2026 · Questo file non contiene codice applicativo.
> Gli elementi non ancora decisi o da chiarire sono nella sezione «Punti da chiarire» in fondo: **nessuna decisione è stata presa in autonomia** e nessun requisito è stato eliminato.
> Ultimo aggiornamento: 24/11/2026 (21:01) — integrate le decisioni dell'utente (v. «DECISIONI DELL'UTENTE»).

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
* Stato: in collaudo, versione mm4.

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
* **Risoluzione delle 13 decisioni sulle identità dei personaggi** (`docs/CANDIDATI_IDENTITA_D3.md`): nessuna unificazione eseguita finora; ogni caso richiede la decisione dell'utente.
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

### Requisito recuperato: «Modalità Prima di Doomsday» (NON da implementare ora)

*Stato: Da sviluppare — solo specifica, nessuna implementazione. Si attende la conferma dell'utente.*

**Ricerca delle specifiche originali (24/11/2026):** il nome «Modalità Prima di Doomsday» **non compare** nel codice né nei documenti del repository (0 occorrenze, v. `docs/REGISTRO_MASTER_TVA_ARCHIVES.md`), nei file di prompt e audit caricati, né nelle conversazioni archiviate consultate. **Non esiste quindi una specifica originale con questo nome: non ne è stata inventata alcuna.** Le uniche specifiche documentate sul tema, che potrebbero coincidere o essere correlate (da confermare), sono:

1. **Road to Doomsday (esistente nel codice):** missione speciale «Operazione Incursione», 16 schede (N°015, 016, 041, 051, 084, 089, 095, 097, 099, 102, 108, 112, 117, 121, 123, 125), +300 XP, distinzione tra watchlist ufficiale «Countdown to Avengers: Doomsday» di Marvel/Disney+ (un consiglio, non un obbligo) e classificazioni editoriali TVA Archives (`docs/REPORT_BLOCCO2.md`).
2. **Specifica di revisione del percorso (prompt di ottobre 2026):** riorganizzare la preparazione ad *Avengers: Doomsday* (N°136) su tre livelli — *Essenziale* (necessario per capire personaggi e sviluppi già documentati), *Consigliato*, *Facoltativo*; non classificare un titolo come essenziale solo perché si ipotizza la presenza di un personaggio; distinguere collegamenti ufficialmente confermati, collegamenti narrativi dimostrabili e ipotesi editoriali; mantenere coerenti missione, 16 opere, progressi, badge e XP, preservando i premi già ottenuti ed evitando assegnazioni duplicate.
3. **Audit del 15/10/2026:** il percorso di 16 schede omette 16 titoli distinti che le sue stesse tappe dichiarano essenziali (aggiungerli porterebbe a 32 schede, 35 con Civil War); possibili soluzioni indicate: dichiarare la selezione «ripasso per chi conosce già gli antecedenti» oppure estenderla. Le mappe N°136 e N°139 vanno trattate come preparazione editoriale, non come prerequisiti ufficiali.
4. **Data di uscita (TVA Live):** per Doomsday lo stato «Confermato» è valutato per mercato; la data italiana ha priorità nell'interfaccia, quelle UK/USA stanno nei dettagli.

**Domanda aperta per l'utente:** la «Modalità Prima di Doomsday» coincide con Road to Doomsday (eventualmente rivista come sopra) o è una modalità autonoma (es. Timeline limitata ai titoli utili prima di Doomsday)? Finché non è chiarito non si implementa nulla.

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

## 12. TVA Arcade e TVA Rankings – Preservazione, verifica e rifinitura *(area recuperata, 24/11/2026)*

* **Preservare tutti i giochi, i progressi e le funzionalità attualmente presenti in TVA Arcade** (Quiz Marvel, Who Am I?, Time Crisis, Secret Wars Draft, Multiverse Escape), compresi XP, missioni, ranghi e badge collegati.
* **Verifica e rifinitura di TVA Arcade e di TVA Rankings** (Rankings: classifiche personali Top numerate, Podio, Tier List, modelli per categoria, backup ZIP). Nessuna modifica senza anteprima approvata.
* **Verifica dei diritti d'uso dei 120 ritratti del Draft:** oggi 0/120 con diritti verificati; sono segnaposto/asset stilizzati di test (`docs/arcade/REPORT_RITRATTI.md`, `docs/arcade/PROBLEMI_APERTI.md`). Nessuna immagine Marvel senza i diritti necessari; applicazione della patch disclaimer («Progetto fan non ufficiale…») solo su indicazione dell'utente.
* Bilanciamento dei cosmici di vertice da osservare nel collaudo; verifica su iPhone reale (safe area, scroll, tocchi, prestazioni).
* **Multiverse Arena 2.0: cancellata** (v. sotto). Preservare l'Arena attualmente funzionante.

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

*Nota sui commit: i commit dell'app citati (es. `0b71861`) sono presenti nel repository locale ma, al 24/11/2026, **non sono stati pubblicati** sul branch remoto `test/tva-archives`: sul remoto sono stati pubblicati solo i documenti.*

| N. | Funzionalità | Stato | Versione | Commit | ZIP | Problemi aperti | Approvazione utente |
|---|---|---|---|---|---|---|---|
| 01 | Miss Minutes – Intelligence Upgrade | In collaudo | mm4 (`20261124-1930-mm4`) | `0b71861` (app); gateway repo `tva-live-scheduler` `000799e` | `NETLIFY_TEST_mm4.zip` | Collaudo reale di mm4 su Gemini (workflow gateway da rilanciare + ZIP da caricare); qualità risposte su Knull/continuità da riverificare | No |
| 02 | Atlante 2.0 | Da sviluppare | — | — | — | Esistono già Atlante, dossier, mappa, cronologie, grafo relazioni (v. «Punti da chiarire») | No |
| 03 | Marvel Database Expansion | Da sviluppare | — | — | — | Consistenza attuale del database da misurare prima di fissare la baseline | No |
| 04 | Tessera TVA 3.0 | Da sviluppare (requisiti nuovi); base esistente da preservare | — | — | — | Verificare quali requisiti sono già coperti dal codice (nessuno considerato completato) | No |
| 05 | Missioni TVA 2.0 / Evolution | Da sviluppare | — | — | — | Missioni, XP, ranghi e badge esistenti da preservare | No |
| 06 | Quiz Marvel Expansion | Da sviluppare | — | — | — | Consistenza attuale del banco domande da misurare | No |
| 07 | TVA Friends 3.0 | In progettazione (da riprogettare su Realtime Database + Auth esistenti, solo coppia) | — | — | — | TVA Live Room da valutare per la coppia; SRI e regole F-A2 aperte (v. 11) | No |
| 08 | TVA Comics Library | Da sviluppare | — | — | — | — | No |
| 09 | Timeline Immersive | Da sviluppare | — | — | — | TVA Episodes già presente | No |
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
5. **«Modalità Prima di Doomsday»:** specifiche originali non reperite; coincide con Road to Doomsday o è autonoma? (v. area 09).
6. **Tessera 3.0:** stabilire, requisito per requisito, cosa è già coperto dal codice e cosa no, senza dare nulla per completato.
7. **TVA Live Room nella coppia:** definire come adattarla (accesso, privacy) prima di qualunque sviluppo.
8. **Altri requisiti storici da decidere:** quiz «da dove inizio» (riesporlo o no), `preferredMode` come default iniziale, locandine per titolo, peso contestuale di N°069/073/094 nel percorso Doomsday.
9. **Infrastruttura Miss Minutes:** gateway Cloudflare Worker (`miss-minutes-api`) con Gemini 3.5 Flash Lite, deploy via GitHub Actions nel repo `tva-live-scheduler`, quote 12/min, 450/giorno, 12.000/mese: rientra nel tetto di costo; da monitorare.
10. **Pubblicazione del codice TEST non ancora sul remoto:** i commit di Miss Minutes (mm4 e precedenti) sono solo locali; il push richiede autorizzazione separata.

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

**Da misurare prima di avviare le aree 03 e 06:** consistenza del database Atlante per tipologia (personaggi, varianti, artefatti, universi, organizzazioni, luoghi, eventi, specie ed entità) e dimensione effettiva del pool del quiz (domande per categoria dopo deduplicazione e controllo di correttezza).

---

## STORICO AGGIORNAMENTI

| Data | Intervento | Commit |
|---|---|---|
| 24/11/2026 | Creazione del documento; nessuna modifica al codice applicativo | `d99d7fd` |
| 24/11/2026 | Integrate le decisioni dell'utente (Friends, Tessera 3.0, Firebase, Arcade/Arena), i requisiti recuperati, l'area 12 e la sezione Conteggi; solo documentazione | v. `git log -- docs/MASTER_ROADMAP.md` |
