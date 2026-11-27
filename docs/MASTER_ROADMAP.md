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
| 02 | Atlante 2.0 | **A4.1 (Multiverso, Nexus, Percorso) in collaudo — build a37 (26/11/2026)**; A3/A3.2 concluse. Precedente: **A3 in collaudo su iPhone** (25/11/2026; A0–A2 approvate, A4 non avviata). Stato precedente: **In progettazione** (25/11/2026): impostazione architetturale **approvata** con integrazioni; **interfaccia definitiva non approvata** (anteprime grafiche da preparare); 13 decisioni identità: 8 approvate, 3 modificate (1 Peter Parker hub, 2 Xavier, 11 Fisk hub), 2 rimandate (9 Bishop, 10 Janet), nessuna applicata; modello generale delle identità specificato; **Revisione 2 delle 14 anteprime APPROVATA dall'utente (25/11/2026) come riferimento grafico definitivo**; **A0 e A1 APPROVATE (25/11/2026); A2 (identità) eseguita a livello registro — in attesa di approvazione**; condizioni di implementazione: nessuna perdita di funzioni/informazioni/collegamenti, ritratti specifici solo se legittimi, dossier approfonditi, Multiverso con mappa+ricerca+filtri+elenco, Nexus scalabile oltre 10.000 relazioni, animazioni ottimizzate iPhone, nessun dato inventato, nessuna regressione; Bishop e Janet sospese; regole XP/badge aggiornate con i valori approvati; nessun codice dell'app scritto | — | — | — | Proposta in `docs/ATLANTE_2_0_ANALISI_E_PROPOSTA.md`; 13 decisioni sulle identità tutte aperte; correzioni audit da riconciliare con fonti; decisioni D1–D8 richieste all'utente | No |
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
| 25/11/2026 | Atlante 2.0 **A3.1 – seconda valutazione** (solo analisi): scene TMDB per personaggio (nessun diritto concesso da TMDB, selezione visiva necessaria, ritaglio 3:4) e illustrazioni AI (rischio giuridico da opere derivate, tier gratuito Gemini senza immagini, ~0,04–0,07 $/immagine); proposta pilota di 10 identità e modalità «immagini private»; archetipi condivisi e locandine esclusi per tua decisione; nessuna implementazione, A4 non avviata | `docs/ATLANTE_2_0_A31_ANALISI_ASSET_VISIVI.md` §6–10 |
| 25/11/2026 | Atlante 2.0 **A3.1 – Pilota ritratti (10 identità)**, approvato dall'utente (ibrido, immagini private, budget 0 €): chiave TMDB dei Secret riusata solo lato server (job `atlante-pilot` in `tmdb-sync.yml`, solo metadati); candidati reali per 10 identità; archivio privato IndexedDB `tva-atlante-ritratti` (selettore scene, ritaglio 3:4, WebP/JPEG, sostituisci/rimuovi, esporta/importa); registro `data/atlante/assets.json`; test `tests/a31_test.py`; scoperte: `tagged_images` solo locandine, 8 ID errati in tmdbMap (non corretti), Wolverine misto con X-Men '97; a31_test 40/40, a3_test 30/30, regressione 66 suite senza nuove rotture (banner A3 a 11 px: fix ui_audit; b40c_test instabile); **in attesa del collaudo iPhone, nessuna estensione alle 295 identità, A4 non avviata** | `atlante2/ritratti.js`, `atlante2/a3.*`, `tools/atlante_pilot_tmdb.py`, `tools/atlante_assets.py`, `data/atlante/assets.json`, `docs/ATLANTE_2_0_A31_PILOTA_REPORT.md`, ZIP `NETLIFY_TEST_a31.zip` |
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
| 25/11/2026 | **A3.1 – correzioni autorizzate**: verifica mappa tmdbMap contro TMDB (131 voci: 112 ok, 19 solo prefisso «Marvel's», **nessuna sostituzione necessaria**; i «8 ID errati» erano confusione tra numero visibile e id interno); Wolverine Fox separato da X-Men '97 (ID, apparizioni e link preservati); instabilità ripristino cloud documentata (`docs/ATLANTE_2_0_RIPRISTINO_CLOUD_INSTABILITA.md`, KNOWN_FAILS `b40c_test`, **problema aperto**); A4 non avviata, pilota non esteso | `tools/tmdb_verifica_mappa.py`, `data/atlante/tmdb_verifica_mappa.json`, `docs/ATLANTE_2_0_TMDB_VERIFICA_MAPPA.md` |
| 25/11/2026 | **A3 – revisione densità + A3.2 Visual Asset Engine (prototipo)**, approvate dall'utente dopo anteprima 390 px: 3 viste catalogo (compatta predefinita, grande, elenco; preferenza `tva-a3-vista`), 3 colonne personaggi/artefatti, 2 colonne le altre, filtri richiudibili, hero –25 %, dossier compatti, icona ritratto, numero Terra completo, dossier senza ridondanze (dati originali intatti), linguetta launcher Miss Minutes solo in Atlante (solo CSS, Miss Minutes non modificata); **A3.2**: motore di preselezione su GitHub Actions (CLIP e SigLIP, 0 €) sulle 10 identità del pilota: 1272 candidati → 44 proposte (3–5 per identità, ritaglio 3:4 suggerito), CLIP 6,3 min / 1,8 GB, SigLIP 13,4 min / 2,2 GB, accordo sui titoli alto e sulle immagini 41 %; approvazione rapida (✓) nell'editor; **precisione visiva NON misurabile dalla sandbox: serve il tuo collaudo** (protocollo in `docs/ATLANTE_2_0_A32_VISUAL_ASSET_ENGINE.md` §6); **causa dell'instabilità del ripristino cloud trovata nel test** (race di inizializzazione TVA Live; `b40c_test` 42/42 su 4 esecuzioni; nessun ripristino su dati reali); test: a3 30/30, a31 40/40, a32 21/21, a32e 7/7; ZIP `NETLIFY_TEST_a32.zip`; **nessuna estensione alle 296 identità, A4 non avviata, produzione non toccata, in attesa di approvazione** | `atlante2/a3.*`, `atlante2/ritratti.js`, `tools/atlante_engine*.py`, `data/atlante/engine/`, `docs/ATLANTE_2_0_A32_VISUAL_ASSET_ENGINE.md`, `docs/ATLANTE_2_0_A3_DENSITA_REVISIONE.md`, `docs/ATLANTE_2_0_RIPRISTINO_CLOUD_INSTABILITA.md`, `tests/a32_test.py`, `tests/a32e_test.py` |
| 25/11/2026 | **A3.2 v2 (dopo collaudo A3.2)**: correzioni grafiche (numeri Terra interi, titoli senza ridondanze, barra filtri opaca, schede invariate); emblemi originali per 8 categorie; **Motore 2.0** su 40 identità (20,5 min, 3,1 GB, 0 €): 202 proposte, confidenza alta 32 / bassa 8 (fino a 10 proposte); candidati lazy per identità; **revisione rapida consecutiva** (mai sovrascrive ritratti salvati; scene già usate escluse); export valutazioni solo-metadati; precisione da misurare con le tue approvazioni (`scena.rk`); test: a3 30/30, a31 40/40, a32 21/21, a32e 7/7, a33 12/12; build `20261125-1500-a33`, ZIP `NETLIFY_TEST_a33.zip`; **nessuna estensione alle 296 identità, A4 non avviata, produzione non toccata; in attesa di collaudo/approvazione** | `atlante2/ritratti.js`, `tools/atlante_engine2*.py`, `tools/atlante_w.py`, `data/atlante/engine/*2_w1.json`, `tests/a33_test.py` |
| 25/11/2026 | **A3.2 v3 – estensione a 296 identità** (autorizzata dopo collaudo: 38 valutazioni, 89,5 % da proposta, 78,9 % entro la 3ª, 83,9 % su alta confidenza): filtro di continuità per universo principale; **Harry Osborn** ricalcolato (solo Raimi, 5 proposte, alta); candidati TMDB e motore a **blocchi riprendibili** (9 blocchi, 93 min CPU, 0 €); 279 identità con proposte (alta 90, bassa 189 fino a 10), 17 senza; prompt descrittivi per 174 identità, soglia prudente (non calibrata) per 82; **contatore completati/mancanti**, filtro «senza ritratto», revisione rapida su tutte le identità (mai sovrascrive), **composizioni hub/mantelli** dai ritratti delle varianti; spiegazione 38 vs 39 (ritratti da file locale esclusi dall'export v1; export v2 elenca tutti); test: a3 30/30, a31 40/40, a32 21/21, a32e 7/7, a33 12/12, a34 9/9; build `20261125-2000-a34`, ZIP `NETLIFY_TEST_a34.zip`; **A4 non avviata, produzione non toccata, in attesa di collaudo/approvazione** | `atlante2/a3.*`, `atlante2/ritratti.js`, `tools/atlante_w.py`, `tools/atlante_prompt.py`, `tools/atlante_engine2*.py`, `data/atlante/engine/{waveall.json,blocchi/}`, `tests/a34_test.py` |
| 25/11/2026 | **A3/A3.2 CONCLUSE dall'utente (collaudo A34 approvato; resta aperta la compilazione progressiva dei ritratti) + rifiniture a35**: miniature ritratto nelle varianti degli hub, composizione hub più grande, niente sillabazione automatica dei titoli, diciture tecniche/ID nascosti nelle sezioni utente (restano nei dati), Peter (X-Force) prima apparizione Deadpool 2 (2018), omonimie rimosse dagli hub, **Harry Osborn diviso in Raimi e Webb** (ID, riferimenti, dati personali e ritratti preservati; N°005 → Webb; N°120 lasciato su Raimi in attesa di decisione), contrasto badge «Documentato» corretto (ui_audit 0 fallimenti), identità 297. Test a3/a31/a32/a32e/a33/a34/a2 verdi, verifiche registro OK; baseline A0 rigenerata (solo build+hash). Webb senza candidati ritratto: da generare (`atlante_w.py --meta-all` eseguito, poi Actions `tutti_candidati`/`engine2-tutte`). **A4 AUTORIZZATA ma solo PROPOSTA + anteprima interattiva** (`docs/ATLANTE_2_0_A4_PROPOSTA.md`, `docs/atlante2/a4/`): nessun codice A4 finché non approvi. Build a35. Stato: in attesa di collaudo/approvazione. |
| 25/11/2026 (sera) | **A4.0 autorizzata (solo dati/analisi/correzioni identità) + anteprima grafica v2 di Multiverso, Nexus, Percorso**: registro relazioni tipizzate (`tools/atlante_relazioni.py`, `data/atlante/relazioni.json`: 940 relazioni = 66 narrative + 2 controparti + 872 editoriali; 93 voci ambigue/errate in coda non importate; co-apparizioni escluse dai conteggi; processo di intake scalabile in `docs/ATLANTE_2_0_A4_RELAZIONI.md`); Harry Osborn YFNSM separato da Raimi e Webb (3 identità, ID/riferimenti/ritratti preservati; 298 identità); Peter (Deadpool) assegnato a Fox-Verse dopo verifica fonti; candidati ritratto e proposte generati per le nuove identità (Actions, 0 €); documento dei 34 link ambigui consegnato, NON risolti; rimossi 3 screenshot di test tracciati per errore. Anteprima `docs/atlante2/a4/anteprima_v2.html` + test (25 controlli). Build a36. **A4.1 NON avviata**: attende approvazione dell'anteprima. Stato: in attesa di approvazione. |
| 26/11/2026 | **A4.1 autorizzata dall'utente (direzione anteprima rev.2 approvata) – build a37, in attesa di collaudo**: (1) *Registro relazioni*: lotto editoriale 01 (`data/atlante/relazioni_lotti/lotto_01.rel`, ~185 affermazioni su MCU, Spider-Man, X-Men, Deadpool, Wolverine, FF, Defenders), verifica documentale registrata a parte (`_verifiche.json`, distinta dall'approvazione umana: campi `approvazione`, `controversa`, `esito_verifica`); registro: 1168 relazioni (227 narrative, 5 controparti, 936 editoriali), **28 narrative verificate su fonte consultata (Wikipedia: Thor, Iron Man 2, Civil War, Avengers, Homecoming, Ragnarok), 138 ancora «da verificare»** (verifica non ancora eseguita sulle altre fonti del lotto); obiettivo interno 500 narrative documentate: **non raggiunto** (227 narrative totali, 28 verificate), prosecuzione a lotti; nessun caso controverso in attesa. (2) *Correzioni*: Howard Stark → Tony (padre, fonte consultata); eliminate le «Varianti» errate di Jane Foster (Loki/Thor) dalle schede e dal grafo classico; dossier autonomo di Laufey (padre biologico di Loki, fonte consultata); coda identità multiple 93 → 19; i 34 link ambigui restano separati e non decisi. (3) *Modulo A4.1* additivo e lazy (`atlante2/a4.js`, `a4.css`, dati `atlante2/data/nexus/g.json` da `python3 tools/atlante_a4.py --scrivi|--verifica`): **Multiverso** (orbite per natura documentata, TVA separata, zoom/trascinamento/pinch/ricentra/schermo intero, scheda universo con ritratti privati già salvati, confronto con controparti documentate), **Nexus** (tutte le identità e organizzazioni, ricerca, ricentra/indietro, legenda solo dei tipi presenti, tipi vuoti nascosti, editoriali e co-apparizioni escluse di default con soglia 1/2/3/4+, tetto nodi 12/20/30, stato di verifica sempre visibile), **Percorso** (narrativo/co-apparizioni/misto, fino a 3 alternative, esclusi editoriali e non verificate di default). Test: `tests/a41_test.py` (390/430 px) + a3/a31/a32/a32e/a33/a34/a40/a2/ui_audit verdi; test a34/a40 aggiornati a 299 identità. Nessuna modifica a XP/badge, Miss Minutes invariata, produzione congelata, 0 €. **Aperti**: Matt Murdock (MCU) privo di identità distinta (relazioni Netflix/Echo non importate); 19 voci in coda; 34 link ambigui; mm6.1 in attesa di collaudo; N°120 su Raimi (decisione pendente). **A4.2+ non avviata.** |
| 26/11/2026 (notte) | **a38 – espansione editoriale relazioni (autorizzata durante collaudo a37)**: (1) Harry Osborn N°120: nessuna regressione, i dati erano già su YFNSM; errore nel resoconto a36/a37, corretto. (2) Matt Murdock separato: `id-matt-murdock-daredevil` (Affleck, 2003, N°035; ID/ritratti/riferimenti conservati) e nuova `id-matt-murdock-mcu` (Cox, N°060-128), relazione `stessa_scheda_atlante`; 300 identità. Candidati ritratto per Matt MCU da generare (Actions). (3) Coda relazioni 22→0 con regole su evidenze documentate; pagine aggregate → respinte (10). (4) Lotto 02 (7 relazioni). (5) Verifica documentale da Wikipedia: 93 narrative verificate / 90 da verificare (testo non chiaro = «non confermata», mai respinta); 1 controversa per l'utente (Nakia/T'Challa: «ex-lover» vs figlio in Wakanda Forever). Totale narrative 233: **obiettivo 500 non raggiunto**. Test a3/a31/a32/a32e/a33/a34/a40/a41 OK. Non avviati A4.2/A5. In attesa: collaudo a37/a38, mm6.1, 34 link ambigui. |
| 26/11/2026 (notte) | **Rinomina ufficiale (decisione utente)**: Atlante 2.0 → **TVA Atlas** («L'Atlante del Multiverso»; motto «Ogni universo. Ogni identità. Ogni connessione.»); relazioni → **TVA Nexus**; «Atlante» resta nella barra di navigazione. Applicata alle intestazioni dell'interfaccia (hero con emblema multiversale originale oro su nero, Spectral; titoli di Home/Ricerca/Nexus/pulsanti), a CLAUDE.md e alla roadmap; invariati ID, chiavi di salvataggio, percorsi tecnici e riferimenti interni. Nessun ZIP dedicato: confluisce nella prossima build TEST. Test a3/a31/a32/a41 OK. |
| 26/11/2026 (notte) | **Decisioni utente su Nakia/T'Challa/Toussaint applicate**: relazione sentimentale canonica «partner sentimentali e genitori di un figlio» (non coniugi), fasi documentate (Black Panther: ex-amanti; Wakanda Forever: figlio Toussaint/T'Challa II), Toussaint collegato a entrambi come figlio. **Verifica relazioni su fonti non-Wikipedia** (MCU Wiki, Marvel Database, Marvel.com): narrative 243 totali = 148 verificate documentalmente + 46 da verificare (fra cui «non confermata», mai respinta) + 49 «guida» (provenienti dalle schede dell'app, non ancora verificate su fonti esterne: sono le «altre 50» richieste; 197 = verificate+guida visibili come tali). Lotto 03 (11 relazioni da MCU Wiki). Obiettivo 500 non raggiunto. Candidati ritratto Matt MCU: workflow `tutti_candidati` avviato. |
| 26/11/2026 (notte) | **Build a39 TEST (grouppo: relazioni + rinomina + riassegnazione ritratti)**: TVA Atlas/TVA Nexus nelle intestazioni (hero con emblema multiversale originale, sottotitolo e motto); candidati ritratto di Matt Murdock MCU generati (workflow `tutti_candidati`, solo metadati; file `atlante2/data/pilot/c/id-matt-murdock-mcu.json`); **riassegnazione sicura dei ritratti privati** tra identità gemelle (Matt 2003 ⇄ MCU) con «Sposta»/«Copia»: mai sovrascrive un ritratto già salvato, l'origine è cancellata solo dopo la scrittura riuscita (`tests/a35_test.py` 5/5). Test a2/a3/a31/a32/a34/a35/a40/a41 OK. In attesa: collaudo a37–a39, mm6.1, 34 link ambigui. A4.2/A5 non avviati. |
| 26/11/2026 (sera) | **Build consolidata a40 TEST (ciclo dati completo, unica build dopo a39)**. **Link ambigui**: dei 34 collegamenti esaminati (24 coppie univoche) 17 risolti con regola R1 (stesso universo di una sola identità candidata), 3 con R2 (scheda interprete → variante interpretata: Tobey→Raimi, Garfield→Garfield, Holland→MCU), 1 con R3 (Ronan → Groot originale, unica apparizione in comune), 3 pagine-universo non registrate/multiversali restano sull'hub (R4). **Realmente controverso: una sola decisione** — Groot originale vs successore per Drax, Gamora, Quill, Rocket, Nebula e universo MCU (6 link; provvisoriamente scheda storica, nessuna relazione narrativa attribuita). Tabella in `docs/ATLANTE_2_0_A3_LINK_AMBIGUI.md` (2a risolti / 2b da decidere), `tools/atlante_a3.py` (`decidi()`). **Relazioni**: Nakia/T'Challa registrati come «relazione sentimentale (ex-amanti)» documentata solo in Black Panther; la genitorialità di Toussaint NON prova la prosecuzione della relazione sentimentale. Verifica del 26/11 su MCU Wiki / Marvel Database / Marvel.com / Wikipedia (trame): ledger applicato anche alle relazioni «guida» (guida 49→6), lotto 04 (Matt Murdock MCU/Stick, Karen Page, Vanessa/Fisk, Raimi Doc Ock/Sandman). **Stato finale registro**: narrative 246 = 206 verificate documentalmente + 34 da verificare (non_verificata/non_confermata, mai «respinta») + 6 guida; 0 controverse in attesa; obiettivo 500 NON raggiunto (nessuna forzatura: solo relazioni con fonte). **Lacune residue**: 34 da verificare (soprattutto Fox/Sony/Netflix: Deadpool, Wolverine/Jean·Mariko·Viper, Beast, Xavier→Rogue/Wolverine/Beast, Defenders, Iron Fist/Colleen, Cottonmouth/Mariah/Cage, Tony/Steve, Strange/Wong, Mysterio, TASM2 Harry/Electro, Daredevil 2003, Venom/Anne), 6 guida (Elektra/Mano, Howard/SSR, Groot successore, Johnny/Sue, Bob Sentry ×2), completamento relazioni Harry Raimi/Webb/YFNSM e Wolverine, decisione Groot. Test a2/a3/a31/a32/a32e/a33/a34/a35/a40/a41/ui_audit OK. In attesa: collaudo a37–a40, mm6.1, decisione Groot. A4.2/A5 NON avviati. |
| 26/11/2026 (notte) | **Decisione utente su Groot applicata (nessun ZIP dedicato: confluisce nella prossima build)**: nuovo **hub Groot** (`hub-groot`, tipo `hub_continuita`, non multiversale, non conta come personaggio) con due identità distinte, `id-groot-originale` e `id-groot-successore`; discendenza (successore → originale) mantenuta e ora verificata (dichiarazione d'autore Gunn + Wikipedia). Le fasi **Baby Groot, adolescente, adulto** sono incarnazioni del successore (`inc-groot-piccolo` conserva l'ID; `inc-groot-adolescente` = N°084; `inc-groot-adulto` senza apparizioni registrate: «da verificare», non attribuita). Link: i riferimenti generici a Groot (Drax, Gamora, Quill, Rocket, Nebula, pagina Universo MCU) puntano all'hub (regola R5); Ronan resta sull'originale (R3, unica apparizione in comune). Relazioni specifiche attribuite alle identità: Rocket → Groot successore (padre adottivo, confermata), Rocket/Quill ↔ Groot originale invariati. **Chiarimento link**: i 34 «collegamenti ambigui» sono 34 righe ma 24 coppie origine→destinazione, perché 10 righe sono duplicati (stesso link da più sezioni); le 34 righe = 24 risolte (R1–R4, compresi i duplicati) + 10 righe Groot (6 coppie uniche + 4 duplicati: Drax, Gamora, Quill, Rocket elencati due volte); ora 34/34 risolte (R1 17, R2 3, R4 3, R5 11), nessuna decisione pendente. Registro: 247 narrative = 208 verificate + 34 da verificare + 5 guida. Obiettivo 500 non è prerequisito delle fasi successive. ID, riferimenti e ritratti privati invariati. Test a2/a3 (32/32)/a31/a32/a32e/a33/a34/a35/a40/a41/ui_audit OK. In attesa: collaudo a40; A4.2/A5 non avviati. |
| 26/11/2026 (mattina) | **Build a41 TEST (unica build consolidata dopo a40; correzioni dal collaudo reale a40, senza attendere l'approvazione della a40)**. **Atlas/Nexus** (`atlante2/a4.js`, `a4.css`; test `tests/a42_test.py`, 31 controlli a 390/430 px): (1) tap sugli universi non funzionante → causa: `setPointerCapture` al pointerdown reindirizzava il click sul riquadro; ora la cattura parte solo al vero trascinamento (>8 px) e il tap raggiunge il nodo; (2) nodi duplicati nel TVA Nexus → un solo nodo per identità (relazioni multiple unite: «anche: …»), mai il nodo centrale tra i vicini; (3) leggibilità/inquadratura/disposizione: raggi delle orbite e degli anelli calcolati sul numero di nodi (nessuna sovrapposizione), inquadratura automatica `fit` di tutti i nodi sia in Multiverso sia in Nexus, ricentra con ◎; (4) universi differenziati: tinta propria per universo (da hash dell'ID), colore e stile dell'orbita per natura (principale/diramazione/autonomo/raggruppamento) con legenda; (5) filtri compatti: pulsante «Filtri · n» richiudibile in Nexus e Percorso (chiusi di default); (6) controlli mappa spostati a sinistra e spostati automaticamente sul lato opposto se la linguetta di Miss Minutes (trascinabile) li copre. **Groot** (richiesta 26/11): verificati su MCU Wiki/Wikipedia/Marvel.com Holiday Special (N°107, più massiccio, in crescita verso la taglia adulta) e Guardians Vol. 3 (N°110, «giovane adulto»); la fase «adulto» è registrata come `apparizioni_esterne` [107, 110] perché le due schede dell'app non elencano Groot (lacuna dei dati dell'app, NON modificata; il sottoinsieme delle pagine resta verificato). Nell'interfaccia: «Fasi evolutive» / «Fase evolutiva» (architettura tecnica invariata: `tipo = fase_di_crescita`). **Miss Minutes – streaming progressivo (richiesto esplicitamente dall'utente; fuori dal congelamento mm6, non è mm7; versione indicata mm6.2 nello storico)**: gateway `miss-minutes/gateway/worker.ts` con `stream:true` → Gemini `streamGenerateContent?alt=sse` ri-emesso come SSE semplificato (`{"t":…}`, `{"done":true}`, `{"e":codice}`), stesse quote/validazioni/CORS, parti «thought» escluse, tetto 4000 caratteri, errori prima dell'inizio ancora in JSON; client `gateway-client.js` `askStream` (lettura incrementale, timeout di inattività, testo parziale in `partial`); app: bolla che si riempie in tempo reale con cursore, nessuno scorrimento forzato (vista all'inizio del messaggio come mm6.1), marcatori `[[id]]` mai visibili, Interrompi sempre disponibile e testo già ricevuto conservato in cronologia con Riprova, nessun nuovo tentativo automatico dopo testo parziale, diagnostica «Streaming: reale/simulato · primo testo dopo X ms»; con gateway non ancora aggiornato o browser senza stream: rivelazione progressiva simulata interrompibile (diagnostica «simulato»). **Il gateway deve essere ridistribuito dall'utente** (workflow `Miss Minutes - gateway` nel repo `tva-live-scheduler`, che usa la propria copia di `worker.ts`: serve aggiornarla; non fatto da Claude senza autorizzazione, nessuna modifica a Cloudflare). Test: `gateway_test.mjs` 51/51, `ui_stream_test.py` 16/16 (gateway HTTPS locale con chunk reali, richiede porta 443/root), `ui_test` 67/67, `ui_mm6` 35/35, `ui_mm61` 10/10, `engine_test` 37/37, `e2e_gateway` 8/8; a2/a3 (32)/a31/a32/a32e/a33/a34/a35/a40/a41/a42/ui_audit OK. Requisiti dello streaming «comunicati in precedenza»: non reperibili nel repository né nella documentazione; applicati quelli standard e documentati qui — da integrare se l'utente ne indica altri. Stato: in attesa del collaudo a41; A4.2/A5 NON avviati. |
| 26/11/2026 (mezzogiorno) | **Gateway Miss Minutes aggiornato nel repo `Posty2001/tva-live-scheduler` (autorizzato dall'utente alle 11:11)**. Backup del gateway funzionante: branch `backup/gateway-pre-streaming-20261126` (= commit `86262a9`, mm6). Aggiornamento: commit `9bc2ed5` su `main` (e branch `gateway/streaming-mm62`), UNICO file modificato `miss-minutes-gateway/worker.ts` (+51/−4: parametro `stream`, SSE, URL `streamGenerateContent?alt=sse`, timeout 45 s in streaming). Invariati: segreti, autenticazione/PoW, limiter, modello (`GEMINI_MODEL`), quote, `wrangler.toml`, workflow TVA Live e workflow gateway. Compatibilità: senza `stream` percorso JSON identico (app precedenti); app nuova con gateway vecchio → rivelazione simulata. Annullamento a monte: la chiusura del client chiama `cancel()` → `reader.cancel()` sul corpo Gemini (test: 1 sola chiamata, upstream annullato); al tetto di 4000 caratteri la richiesta a monte viene annullata. Nessun retry lato gateway; il client non ritenta dopo testo parziale. `gateway_test.mjs` 53/53. Deploy NON eseguito da Claude: da avviare dall'utente (workflow `Miss Minutes - gateway`). Rollback: rieseguire il workflow dopo aver ripristinato `worker.ts` dal branch di backup. |
| 26/11/2026 (pomeriggio) | **Build a42 TEST (unica build consolidata dopo il collaudo a41; A4.2)** – report completo in `docs/ATLANTE_2_0_A42_REPORT.md`. (1) **Streaming Miss Minutes**: causa misurata sul gateway reale con sonda (Cloudflare invia 25 chunk veri; Gemini li consegna a raffiche con pause di 4 s → effetto «tutto insieme»); corretto con pacer di visualizzazione lato app (ritmo costante, Interrompi/parziali/niente scroll forzato) + prologo anti-buffering e `no-transform`/`nosniff` nel gateway (commit `b41b01a` su `tva-live-scheduler`, backup `backup/gateway-streaming-v1-9bc2ed5`; da ridistribuire con il workflow). Safari iOS reale NON verificabile qui. (2) **Osservatorio del Multiverso** in primo piano nella Home (pulsante nella hero + scheda con anteprima), distinto dal catalogo. (3) **Catalogo universi**: numeri non tagliati, nome completo + classificazione separata, tinte/emblemi per universo coerenti con la mappa, «Hub di identità». (4) **TVA Nexus**: nomi brevi, alias distinti, relazioni multiple mostrate tutte (Iron Man–Steve: amicizia + rivalità). (5) **A4.2**: trail, filtri per tipo, relazioni multiple. (6) **Barra categorie**: posizione orizzontale mantenuta/ripristinata, centratura dolce. Test: a43 71/71 (nuovo), a3/a31–a35/a40/a41/ui_audit/c3/c4 e suite Miss Minutes verdi. Build id `20261126-1334-a42`; ZIP `NETLIFY_TEST_a42.zip`. Stato: in attesa del collaudo iPhone; **A5 NON avviata**; Miss Minutes: eccezione streaming mm6.2 (nessun altro intervento). |
| 26/11/2026 (sera) | **Build a43 TEST (unica build consolidata dopo il collaudo a42; A4.3 Percorsi e confronti)** – report in `docs/ATLANTE_2_0_A43_REPORT.md`. (1) Home: portale Osservatorio compatto (~140 px, miniatura animata a sinistra) + portali TVA Nexus/Percorsi affiancati. (2) Miss Minutes: preferenza locale «Velocità di lettura» (Lenta 25 / Normale 45 predefinita / Rapida 80 car/s, valori da calibrare), pacer quasi costante con recupero ≤1,25×; gateway invariato. (3) Dati: Fantastici Quattro divisi per continuità (1994, Story, Trank, First Steps/Terra-828, Reed Illuminati/Terra-838) senza unificazioni, 315 identità; discrepanza Johnny N°117 (Marvel Wiki Earth-121698 vs mappa Fox-Verse) segnalata, non risolta; nessuna relazione nuova inventata. (4) Parole spezzate nelle schede corrette (`fitTitles`). (5) A4.3: Percorsi con Inverti/passi con universo/«Apri nel Nexus» + Confronto tra universi (titoli in comune, controparti, identità esclusive). Test: a43_percorsi 33/33, a43 73/73, suite a3–a42, Miss Minutes 26/26 stream, gateway 53. Safari iOS non verificato. **In attesa di collaudo; A5 NON avviata; nessuna funzionalità dichiarata completata.** |
| 26/11/2026 (sera) | **Miss Minutes 2.0 – Affidabilità e conoscenza aggiornata: SOLO ANALISI (nessun codice)** – `docs/MISS_MINUTES_2_0_ANALISI.md`. Cause verificate: (1) «Peter Parker interpretato da Peter Parker» riprodotto: `resolveRefs` sostituisce i marcatori `[[id]]` con il titolo della scheda dopo parole funzionali (da, di, con…); (2) «Spider-Man 4 in sviluppo»: il modello non riceve data corrente né Timeline/TVA Live/Nexus (`contextFor` scarta i titoli) e il prompt dice «non hai accesso a internet» (Brand New Day è uscito il 31/07/2026). Grounding Gemini: non disponibile gratis per Gemini 3+ (richiede fatturazione) → escluso salvo sonda. Soluzione consigliata: pacchetto di fatti (interni + TMDB/Wikipedia) con provenienza e classi, marcatori strutturati, verificatore deterministico, fonti realmente consultate, suite ≥50 domande. **In attesa di approvazione; 4 decisioni richieste; mm6 resta congelata; A5 NON avviata.** |
| 26/11/2026 (sera) | **Miss Minutes 2.0 – fase a (verificatore, data odierna, fatti interni, rigenerazione unica)** – architettura approvata e sviluppo autorizzato dall'utente (16:43). Implementati `miss-minutes/verify.js`, `knowledge/fatti.json` (45 voci cast con fonte), integrazione in `app.js` (controllo frase-per-frase prima della visualizzazione, una sola ripresa dal prefisso verificato, altrimenti nota di incertezza), gateway `worker.ts` (data Europe/Rome, `fatti` sanificati, `riprendi`, prompt aggiornato; commit nello scheduler repo da ridistribuire dall'utente). Bug reale trovato dal test UI e corretto (titoli sovrapposti). Test: verify 23, gateway 58, e2e 8, ui_mm2 13 + suite esistenti. **Stato: in collaudo, NON completata.** Fase b (TMDB/Wikipedia/Wikidata, fonti ufficiali, limiti gratuiti Cloudflare/TMDB/Wikimedia) e fase c (≥50 domande documentate) da eseguire; sonda grounding non eseguita (serve conferma utente che la fatturazione sia disattivata). Produzione e A5 non toccati. |
| 27/11/2026 | **Miss Minutes 2.0 – fase b (fonti aggiornate, gerarchia, formato/omonimie, cronologia pulita, fonti reali, autoscroll)** – dopo il collaudo mm2a (BND descritto come ciclo fumettistico: causa = fatti senza tipo/sinossi, verificatore limitato alle frasi con titolo e ai soli pattern «già uscito/in sviluppo», cronologia non ripulita). Implementati: titolo in discussione + controlli `formato`/`esistenza`/`tempo` generali (corretto anche il pattern «non è ancora uscito»), `lookup.js` (Wikipedia/Wikidata solo nomi, cache TTL 6 h/14 gg, fail-open, impostazione + svuota cache), classi/gerarchia fonti nei fatti e nel prompt, fatto «lacuna» e omonimia, cronologia ripulita, «Fonti consultate» con link reali, `tools/mm_tmdb.py` + opzione `mm_tmdb` nel workflow esistente «TMDB sync (manuale)» da lanciare con ref test/tva-archives (il workflow separato non compariva nelle Actions perché presente solo sul branch TEST; rimosso; archivio non ancora generato), autoscroll intelligente (3 velocità invariate), CSP `connect-src` + en.wikipedia.org, attribuzioni. Gateway da ridistribuire (nessun deploy fatto). Report: `docs/MISS_MINUTES_2_0_FASE_B_REPORT.md`. **Stato: in collaudo, NON completata.** Endpoint Wikipedia non verificabile da questo ambiente (prima verifica = iPhone). Fase c (≥50 domande) e sonda grounding non eseguite (serve conferma utente della fatturazione disattivata). Produzione e A5 non toccati. |
| 27/11/2026 | **Miss Minutes 2.0 – fase b.1 (archivio TMDB)** – workflow «TMDB sync (manuale)» #50 (`mm_tmdb`+`mm_tmdb_commit`) → commit `5e18986`, `tmdb_titoli.json` 131/138 titoli (sinossi 131, cast 127, date film IT 78/US 84). Limiti trovati e gestiti: serie = dati della serie non della stagione; date con anteprime (generatore corretto, archivio da rigenerare); sinossi troncate; 7 titoli senza voce (N°125 FF First Steps mancante nella mappa). App: etichette serie/stagione, «DISCORDANZA» con la Timeline, precache PWA verificata offline, test `ui_tmdb_test.py`. Report: `docs/MISS_MINUTES_2_0_TMDB_COPERTURA.md`. ZIP `NETLIFY_TEST_mm2b.1.zip`. **In collaudo, NON completata.** |
| 27/11/2026 | **Miss Minutes 2.0 – fase b.2 + fase C (strumenti) + progetto aggiornamento archivio** – direzione B.1 approvata dall'utente (23:40), consolidamento richiesto. b.2: generatore `tools/mm_tmdb.py` v2 (override verificati dall'utente `tmdb_overrides.json`, risoluzione stringente dei 7 mancanti → `tmdb_risolti.json`, dati per stagione/serie), app compatibile (commit `1a84e48`); **l'archivio v2 va ancora rigenerato dall'utente** (workflow «TMDB sync (manuale)» con `mm_tmdb`+`mm_tmdb_commit`, «Use workflow from» = `test/tva-archives`): l'archivio attuale (commit `49f0767`) è versione 1 (131 voci, nessuna stagione). Fase C: set di **81 domande** documentato (`miss-minutes/eval/domande.json`, generato da `tools/mm_eval_build.py`; 11 categorie incl. MCU, Sony, Fox, fumetti, multiverso, attori, cronologia, novità, teorie, false premesse, 18 seguiti in 6 catene), runner in-app «Impostazioni → Valutazione risposte (fase C)» che interroga il **Gemini reale** tramite il gateway dell'utente (`miss-minutes/eval.js`, ritmo 11,5 s/richiesta, 1 conversazione per catena, forzato online), report `python3 tools/mm_eval_report.py --md docs/MISS_MINUTES_2_0_FASE_C_RISULTATI.md` (accuratezza, freschezza, fonti, allucinazioni sospette, latenza, incertezza). **Le risposte reali NON sono ancora state raccolte** (la sandbox non raggiunge Gemini/gateway): serve l'esecuzione dell'utente da iPhone; nessun risultato è stato inventato. Aggiornamento automatico archivio: progetto `docs/MISS_MINUTES_2_0_AGGIORNAMENTO_ARCHIVIO.md`; lato app `miss-minutes/archive.js` (pacchetto → copia locale verificata → remoto SHA-256 + validazione, SPENTO di default, `config.archivio` vuoto), test `archive_test.js` 18/18; **nessun servizio esterno o workflow di pubblicazione attivato**, TVA Live non toccata. Nessuna sonda grounding. Build `20261127-0200-mm2d`, ZIP `NETLIFY_TEST_mm2d.zip`, ZIP `NETLIFY_TEST_mm2c.zip`; regressioni: verify 37, lookup 14, archive 18, engine 37, ui_tmdb 12, ui_eval 13, ui_scroll 11, ui_stream 26, ui_test 67, ui_mm61 9, gateway 58+8 (gateway invariato, nessuna ridistribuzione). **In collaudo, NON completata.** |
| 27/11/2026 | **Miss Minutes 2.0 – fase C.1 (consolidamento intelligenza/affidabilità + UI pulita)** – richiesta dell'utente dopo la valutazione reale (74/2/5 su 81, 91,4 %). **Il JSON integrale NON è arrivato in sessione: punto 1 (revisione delle 81 risposte) NON eseguito, confronto prima/dopo con dati reali NON producibile** (nessun dato inventato). Interventi generali (nessuna eccezione per titolo): stato di uscita dallo stato TMDB e mai dalla data trascorsa; date regionali IT/US/altre nei fatti e nel verificatore; negazioni/seguiti/spin-off; intenti personali solo con riferimento a sé/app (mcu07); spoiler solo se richiesti esplicitamente (per quella domanda); soggetto dei seguiti su 4 domande; correzione naturale al posto della nota «non lo riporto»; fonti solo se supportano la risposta; prompt di naturalezza e date nel gateway (`worker.ts`, commit scheduler `1846ea0`, **da ridistribuire dall'utente**); UI: tolte etichetta tecnica, elenco fonti, date di consultazione, Wikidata; pulsante «Fonti» accanto a Copia/Ascolta. Valutatore v2 (dimensioni, fal03 corretto) + 42 domande nuove (set V, 123 totali) + `--confronta`. Report `docs/MISS_MINUTES_2_0_FASE_C1_REPORT.md`. Build `20261127-1200-mm2e`, ZIP `NETLIFY_TEST_mm2e.zip`. Obiettivo ≥95 % NON dimostrato. N°077/N°125 ancora senza voce TMDB. A5 sospesa. **In collaudo, NON completata.** |
| 27/11/2026 | **Miss Minutes 2.0 – hotfix mm2e.1** (richiesto dopo il collaudo mm2e; pulizia grafica risposte APPROVATA dall'utente): (1) viewport iOS – overlay sempre a tutto il viewport di layout con sfondo opaco, solo l'iframe segue il `visualViewport` (coalescenza rAF + riassestamenti), pagina ospite e documento dell'assistente non scorrevoli, scroll di pagina e conversazione preservati; screenshot IMG_2741 NON ricevuti, causa dedotta dal codice; (2) fallback locale: risposta limitata all'aspetto chiesto (poteri/legami/universo/uscita), niente dossier completo né riferimenti tecnici, dato mancante dichiarato e passaggio all'AI; (3) niente battute/flair fissi nel motore locale; (4) `ui_viewport_test.py` 18 controlli. Report `docs/MISS_MINUTES_2_0_HOTFIX_MM2E1.md`; build `20261127-1500-mm2e1`, ZIP `NETLIFY_TEST_mm2e.1.zip`. Valutazione completa (123 domande) e ridistribuzione gateway ancora da fare dall'utente. A5 sospesa. **In collaudo, NON completata.** |
| 27/11/2026 | **Miss Minutes 2.0 – mm2e.2: diagnosi 429 e gestione quote** – il 429 del collaudo era del **gateway** (non di Google; scope non registrato: probabile tetto dispositivo 100/giorno, inferenza); gateway: 429 con ambito/tipo/origine/limite/usate/ripristino, `GET /v1/quota` (residuo senza consumo), parsing dei 429 di Google; app: messaggi con orario in ora italiana, blocco locale senza richieste inutili, pulsante «Richieste disponibili», valutazione sospendibile/riprendibile senza ripetere le completate. **Limiti NON modificati**: i valori gratuiti di Gemini non sono pubblicati (solo AI Studio) e i documenti si contraddicono (10 RPM/20 RPD letti dall'utente vs ipotesi 15/500): serve la lettura di AI Studio prima di valutare 100→200. Gateway da ridistribuire (scheduler). Report `docs/MISS_MINUTES_2_0_QUOTE_MM2E2.md`; build `20261127-1700-mm2e2`, ZIP `NETLIFY_TEST_mm2e.2.zip`. **In collaudo, NON completata.** |
| 27/11/2026 (notte) | **Miss Minutes 2.0 – aggiornamento automatico archivio IMPLEMENTATO (autorizzato dall'utente alle 01:25) + archivio v2 verificato + export JSON da iPhone** – archivio rigenerato dall'utente (commit `7ea1d4b`): **136/138 titoli** (film 86, serie 50; sinossi 136, cast 132, regia film 86/86, date IT film 79/86, stagioni 32; override utente 10, automatiche 2 da confermare: N°107, N°115); **mancano N°077 (ambiguo) e N°125 (nessun candidato: ID non inventato, serve override)**; dettaglio `docs/MISS_MINUTES_2_0_TMDB_COPERTURA.md`. Canale dati nel repo scheduler (commit `080fb7f`): workflow `miss-minutes-archivio.yml` (lunedì + manuale, prova a secco), `scripts/mm_archivio.py` (validazione, SHA-256, anti-regressione ≤10 %, ultima versione valida conservata, 8 versioni), pubblicazione SOLO sul branch `mm-archivio` (raw.githubusercontent.com, CORS verificato dal workflow), niente Pages/Netlify, nessuna modifica a TVA Live; `tmdb-sync.yml`: solo `run-name` per `dispatch_id` `mm-…`. App: `archive.js` acceso (`config.archivio`), CSP limitata al percorso, SW non intercetta l'host. **Primo avvio reale del workflow NON eseguito** (token gh della sandbox non valido): da lanciare dall'utente (prima va pubblicato `tmdb-sync.yml` su `test/tva-archives`). Export iPhone: Impostazioni → Valutazione risposte → «Salva il file JSON» (foglio di condivisione «Salva su File» / download), riepilogo calcolato sul dispositivo (`MMEval.summarize`), report Python opzionale (`mm_eval_report.py` legge il file più recente). Test: `scripts/test_mm_archivio.py` 15/15 (scheduler), `eval_grade_test.js` 12/12, `ui_eval_test.py` 16/16. **In collaudo, NON completata.** Produzione congelata, A5 sospesa. |
