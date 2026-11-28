# Tessera TVA 2.0 — Analisi e progetto (macro-fase 4)

Stato: **SOLO ANALISI E PROGETTAZIONE** (28/11/2026). Nessuna implementazione; nessun file dell'app modificato. In attesa di approvazione dell'utente.
Nome: la macro-fase 4 si chiama «Tessera TVA 2.0», ma il **nome ufficiale visibile resta «Tessera TVA 3.0»** (decisione del 24/11, in continuità con la numerazione già pubblicata). Nel progetto: «Tessera 2.0» = la macro-fase; «Tessera TVA 3.0» = il prodotto.
Vincoli: produzione congelata (`main` = 82a73c7), solo `test/tva-archives`, 0 €, dati personali preservati, regole XP invariate, Missioni/Evolution e Friends 3.0 NON anticipati (solo predisposizioni), roadmap a 13 macro-fasi invariata.

---

## 1. Decisioni già approvate (recuperate)

**Tessera / identità**
- 12/11: Friends 2.0 + **Tessera 3.0** integrate e pubblicate (build `20261112-1905-rifinitura`); Sala storica raggiungibile dalla Tessera e da Friends → Archivio; backup JSON verificato obbligatorio prima di ogni migrazione di identità.
- 24/11: nome ufficiale **Tessera TVA 3.0**; «tutti i requisiti concordati restano invariati». Base da preservare: avatar, cornici, temi, effetti, layout, editor, esportazione PNG, **Variant ID** (da non perdere).
- Requisiti (roadmap §04): correzione delle sovrapposizioni grafiche; ottimizzazione responsive; sfondi statici e animati; cornici e rarità; avatar; titoli personalizzabili; emblemi; universo di appartenenza; personaggio preferito; temi cromatici; badge e trofei esponibili; statistiche personali; personalizzazioni sbloccabili; identità unica collegata a Friends.
- Nessuna funzionalità è «completata» senza approvazione esplicita; anteprime da approvare prima dell'implementazione; una funzionalità alla volta.

**Ranghi, XP, progressione**
- Rango (8 gradi a percentuale), livello XP, 14 distintivi e Stagioni TVA esistenti vanno **preservati** (v. roadmap §05 e area 12). «Non modificare le regole XP già approvate» (28/11).
- Atlas: XP di esplorazione approvati e già integrati (+2 dossier, +15 hub, +25 universo, +5 confronto, +5 raccolta, +40 badge, +1 Nexus; tetto 30/giorno; registro permanente, ricompense mai revocate; le voci «fonte singola» non danno XP).
- Road to Doomsday: nessuna modalità separata; miglioramento a tre livelli (Essenziale/Consigliato/Facoltativo) rinviato alla fase Missioni.

**Variante e Friends**
- Friends 3.0 = esperienza **privata per due persone**; eliminate Squadre TVA, gruppi 2–6, TVA Group; **TVA Live Room conservata** (da valutare per la coppia); nessuna rimozione dal codice in questa fase.
- «Identità Variante collegata alla Tessera» e «Legame Nexus permanente» (roadmap §07); un'**identità unica** Tessera↔Variante.
- **Firebase = Realtime Database + Auth esistenti**; niente Firestore, niente servizi a pagamento (la decisione supera il vecchio piano Firestore `/f3/test`).
- Dati personali mai all'AI online; l'app deve restare usabile senza login.

**Altre**: Arena 2.0 cancellata (Arcade preservata); budget 0 €; Missioni, Quiz, Friends hanno fasi proprie successive.

---

## 2. Analisi dello stato attuale (verificato nel codice di `index.html`)

### 2.1 Moduli esistenti (tutti già presenti)
| Modulo (script id) | Ruolo | Note |
|---|---|---|
| `tc-js` (≈39317) | Tessera: carta, editor «Personalizza» (6 schede: Avatar, Stile, Titoli, Cornici, Temi, Effetti), foto locale, esportazione PNG, sezioni **Carriera TVA** e **Collezione** | 3 distintivi esponibili; layout wide/compact/vertical |
| `tc-art-js` (≈38251) | motore grafico SVG puro: 8 avatar originali, 12 cornici, 10 temi, 6 effetti | nessuna immagine esterna |
| `tva-tessera3` (≈38958) | stile personalizzabile 3.0: font (4), sfondi (9), texture (6), cornici, decorazioni (6), effetti, retro, preset gratuiti | «segue il premio equipaggiato» di default |
| `tva-emblems` | 56 emblemi originali (7 categorie × 8), SVG procedurali | senza marchi protetti |
| `tva-identity` | identità condivisa Tessera↔Variante: nome, VAR-ID, emblema, motto, universo e personaggio preferiti; migrazione non distruttiva con copia di sicurezza | conflitti conservati, mai sovrascritti |
| `rw-js` (≈37721) | **48 ricompense cosmetiche** (20 titoli, 12 cornici, 10 temi, 6 effetti), 5 rarità, 4 tier; stato di sblocco persistente; nessun XP/valuta nuovi | condizioni verificabili (`titles`, `level`, `badge`, `seasons`, `missions`, `anim`…) |
| `updateTessera` (≈24771) | calcolo di rango, XP, livello, statistiche (ore viste, studi, serie, voto medio) | espone `marvelXpInfo` in sola lettura |
| `friends3-js` (≈41338) | collegamento UID↔Tessera↔Variante (Fase 2, solo TEST) | **ancora basato su Firestore**: da riprogettare su Realtime Database (decisione 24/11) |

### 2.2 XP, livelli, ranghi, badge (regole in vigore — non toccate)
- **XP totale** = titoli visti per priorità (verde 30, blu 20, giallo 15, rosso 10) + serie animate viste ×8 + voti ×5 + note ×10 + preferiti ×3 + distintivi ×40 + banca XP missioni + XP Atlas (`leggiXpAtlante`, tetto 30/giorno).
- **Livello**: curva lineare, XP per livello = 100 + (n−1)×30.
- **Rango** (8, a percentuale di guida completata): Recluta 0 · Analista Junior 1 · Analista TVA 15 · Agente Junior 30 · Agente Specializzato 50 · Cacciatore di Varianti 70 · Veterano del Multiverso 90 · Quasi Leggendario 100; «Custode Supremo del Multiverso» = completamento assoluto (rivelazione finale).
- **14 distintivi** (Primo Passo, Guardiano della Linea Sacra, Cacciatore di Varianti, Archivista TVA, Solo l'Essenziale, Nessuna Divergenza Rilevata, Cinefilo TVA, Maratoneta di Serie, Collezionista di Rarità, Weekend Guerriero, A Metà Strada, Critico Ufficiale, Nella Lista dei Preferiti, Cronista TVA).
- Osservazione: i **ranghi** (percentuale) e i **livelli** (XP) sono due scale parallele; la Tessera le mostra entrambe. Il progetto le **unifica solo nella presentazione** («Passaporto di carriera»), senza cambiare soglie né calcoli.

### 2.3 Dati personali e chiavi di salvataggio (prefisso `marvel-ultimate-timeline-`)
| Gruppo | Chiavi | Nel backup/sync |
|---|---|---|
| Identità | `user-name`, `tessera-id` (VAR-NNNNNN), `identity-v1`, `identity-premigration-v1` (copia di sicurezza), `fav-char` | sì (profilo) |
| Aspetto | `tessera-look` (avatar + 3 distintivi), `tessera-style-v1`, `rewards` (sblocchi + equipaggiato) | sì |
| Foto | `tessera-photo` (data-URL ≤ 600 KB, **solo locale**; rimossa al reset) | da verificare se inclusa nell'export |
| Progresso | `watched`, `watched-anim`, `ratings`, `notes`, `favorites`, `badges-earned`, `titoli-stagione`, `missioni-xp-bonus`, `missione-settimana/snapshot`, `road-to-doomsday`, `watch-days`, `episodes-v1` | sì |
| Atlas | `tva-atlante-v2` (registro XP/raccolte), `tva-atlante-ritratti` (IndexedDB, **privato**) | registro sì; ritratti solo export dedicato |
| Altri | `tva-rankings-v1` (+ backup), `tvafriends-v1`, `friends3-link-v1`, `sync-code`, `tva-live-v1` | per modulo |
Principi: nessuna chiave rinominata; ogni nuova chiave è **additiva**; migrazioni non distruttive con copia verificata (schema `premigration` già esistente); il reset («cancella tutto») resta l'unico punto che rimuove la Tessera.

### 2.4 Collegamenti con le altre sezioni
| Sezione | Collegamento attuale con la Tessera | Gap |
|---|---|---|
| **Timeline** | fonte principale: titoli visti → percentuale, rango, XP, statistiche | ok |
| **Atlas** | XP di esplorazione (+ badge Atlas) confluiscono nell'XP; nessuna vista Atlas nella Tessera | mostrare progressione Atlante in Carriera (sola lettura) |
| **Episodes** | voti/visti per episodio (`episodes-v1`); nessun XP | statistiche episodi in Carriera, nessuna regola XP nuova |
| **Rankings** | motore autonomo; nome utente condiviso; nessun legame con rango/XP | vetrina: «classifica in evidenza» opzionale (predisposta) |
| **Quiz** | 1 categoria «Universo TVA» sulle regole della Tessera; progressi quiz separati | statistiche quiz in Carriera (sola lettura, se esposte) |
| **Arcade** | ponte `arcade-reward-bridge`: solo **eventi candidati**, nessun XP/account | trofei Arcade espone­bili in vetrina (predisposto) |
| **Miss Minutes** | legge Tessera in sola lettura via `tvaMissMinutesHost` | invariata |
| **Friends** | `friends3-js` (Firestore, solo TEST), identità in `tva-identity` | riallineare a Realtime DB in macro-fase 8 |

### 2.5 Problemi noti da risolvere (requisiti utente)
- Sovrapposizioni grafiche e responsive della carta (320–430 px; iPad); editor Personalizza lungo e poco immersivo; sfondi animati assenti (oggi solo effetti); badge esponibili limitati a 3; nessuna «vetrina» con statistiche/trofei; stile 3.0 e ricompense separati ma poco leggibili come percorso; funzioni di identità Variante non ancora visibili come «Passaporto».

---

## 3. Progetto Tessera TVA 2.0 (nome visibile: Tessera TVA 3.0)

### 3.1 Principi
1. **Additivo, mai distruttivo**: nessuna regola XP, soglia, badge o chiave esistente viene modificata.
2. **Un'unica fonte** per ogni dato (identità in `tva-identity`, ricompense in `tvaRewards`, XP da `marvelXpInfo`).
3. **Cosmetico ≠ progresso**: le personalizzazioni si sbloccano con condizioni già esistenti; le nuove personalizzazioni usano le stesse condizioni (nessun XP, valuta o contatore nuovi).
4. **Predisposizioni, non anticipi**: slot e contratti dati per Missioni e Friends, disattivati e senza logica.
5. **0 €, offline-first**, nessun dato personale a servizi esterni, nessuna immagine con diritti incerti (solo grafica originale SVG).

### 3.2 Architettura dell'interfaccia (immersiva stile TVA)
**Hub «La mia Tessera»** a schermo intero con intestazione TVA (Indietro · titolo), carta 3D (fronte/retro con flip, effetto olografico, parallasse leggera con giroscopio opzionale e rispetto di *reduce motion*) e cinque schede inferiori:
1. **Tessera** — carta, nome, VAR-ID, rango, livello, barra XP, emblema, titolo equipaggiato, 3→6 distintivi in vetrina.
2. **Carriera** — Passaporto di carriera: rango e livello affiancati (stesse regole), prossimo traguardo, registro XP per fonte (Timeline, serie animate, voti, note, preferiti, distintivi, missioni, Atlas), 14 distintivi, Stagioni, statistiche personali (ore viste, studi, serie, voto medio, giorni attivi, esplorazione Atlas, episodi).
3. **Atelier** — personalizzazione guidata (sostituisce le 6 schede lunghe con un flusso a anteprima viva): Avatar · Sfondo (statico/animato) · Cornice · Tema · Titolo · Emblema · Effetti · Universo di appartenenza · Personaggio preferito · Layout. Ogni voce mostra rarità e condizione di sblocco; le bloccate sono visibili con requisito.
4. **Collezione** — le 48 ricompense (e le nuove) per categoria e rarità, % di completamento, «prossime da sbloccare».
5. **Identità** — Passaporto Variante: VAR-ID, universo di appartenenza, motto, personaggio preferito, backup/ripristino identità; sezione **Legame Nexus** (predisposta, disattivata) e **Vetrina condivisibile** (esportazione PNG).

### 3.3 Funzionalità per requisito
| Requisito utente | Progetto | Nota |
|---|---|---|
| Correzione sovrapposizioni / responsive | griglia fluida della carta con misure in `cqw`, test a 320/375/390/430 px e iPad portrait/landscape; nessun testo troncato | priorità T1 |
| Sfondi statici e animati | 9 sfondi statici esistenti + nuovi **sfondi animati leggeri** (CSS/SVG: portale temporale, nebulosa, griglia TVA, pioggia di glifi), disattivati con *reduce motion* e in risparmio energetico; anteprima in Atelier | sbloccabili per rarità |
| Cornici e rarità | 12 cornici esistenti con bordo di rarità (comune → leggendario) visibile ovunque | estensione catalogo opzionale |
| Avatar | 8 avatar originali conservati; opzione foto locale conservata | nessuna foto caricata altrove |
| Titoli personalizzabili | 20 titoli esistenti + **titolo libero** (≤24 caratteri, validato) accanto al titolo equipaggiato | il titolo libero non sostituisce quelli di rango |
| Emblemi | 56 emblemi esistenti con selettore per categoria e finitura | |
| Universo di appartenenza | scelta dal catalogo universi di Atlas (voci verificate) | usa `identity-v1`, già predisposto |
| Personaggio preferito | scelta tramite ricerca Atlas (anche voci del database esteso); salva ID stabile oltre al nome | retrocompatibile con `fav-char` |
| Temi cromatici | 10 temi + palette accento libera (da preset) | |
| Badge e trofei esponibili | da 3 a **6 slot** in vetrina: distintivi, trofei Arcade/Quiz/Rankings (predisposti), traguardi Atlas | gli slot Arcade/Quiz/Rankings restano vuoti finché le sezioni non espongono i dati |
| Statistiche personali | 4 statistiche scelte dall'utente nella carta; elenco completo in Carriera | sola lettura |
| Personalizzazioni sbloccabili | catalogo esteso, stesse condizioni verificabili del sistema attuale | nessun XP nuovo |
| Identità unica collegata a Friends | contratto dati «identità pubblica» (nome, VAR-ID, emblema, motto, universo, preferito, look) per la futura proiezione, **senza** rete in questa fase | su Realtime DB + Auth (v. 3.5) |

### 3.4 Dati e chiavi (proposta)
- Nuova chiave additiva `marvel-ultimate-timeline-tessera-v2` per le sole impostazioni di vetrina (slot, sfondo animato, titolo libero, statistiche scelte); schema versionato, validazione rigorosa, valori di ripiego, incluso nel profilo esportato.
- Nessuna modifica a `tessera-id`, `identity-v1`, `rewards`, `tessera-look`, `tessera-style-v1`; lettura compatibile con le versioni precedenti; copia di sicurezza (`premigration`) prima di qualunque conversione; rollback documentato.
- Foto: resta locale; esclusa da sync e da qualsiasi invio.

### 3.5 Predisposizioni (senza sviluppo)
- **Missioni ed Evolution (macro-fase 5)**: slot «ricompense cosmetiche di missione» nel catalogo (condizione tipo `mission-reward` non attiva); punto di lettura della banca XP già esistente; nessuna missione nuova.
- **Friends 3.0 (macro-fase 8)**: «identità pubblica v1» (campi e limiti di lunghezza), stato `legame: nessuno|in-attesa|attivo` (sempre `nessuno`), pagina «Legame Nexus» disattivata; il modulo `friends3-js` basato su Firestore **non viene toccato** ma segnalato per il riallineamento a Realtime Database + Auth.
- **Arcade/Quiz/Rankings**: interfaccia di lettura `tvaTrophies.list()` (vuota di default) per trofei esponibili; nessun XP.
- **Miss Minutes**: solo lettura; nessuna modifica al motore.

### 3.6 iPhone e iPad
- iPhone: carta verticale a tutta larghezza, schede inferiori con aree di tocco ≥ 44 px, *safe area* (Dynamic Island, barra Safari), nessun hover, scorrimento senza overflow orizzontale, test a 320 px.
- iPad (≥ 768 px, portrait e landscape): due colonne — carta sticky a sinistra, pannello a destra; Atelier con anteprima grande e griglia di scelta; riuso di `assets/tablet.css` e dei criteri A7.
- Prestazioni: animazioni CSS/SVG leggere, sospese in background e con *reduce motion*; nessun asset pesante; nessuna libreria esterna.
- Accessibilità: contrasto verificato nei due temi, etichette ARIA, ordine di focus, alternative testuali per le carte.

### 3.7 Sicurezza e privacy
Input validati (lunghezza, charset, schema), nessun HTML da dati utente (solo `textContent`/SVG costruito), esportazione PNG locale, nessuna chiamata di rete aggiunta, nessun dato personale all'AI, niente cookie/terze parti.

---

## 4. Fasi operative proposte (una per volta, ciascuna con approvazione)
| Fase | Contenuto | Uscita | Test essenziali |
|---|---|---|---|
| **T0 Fondamenta** | inventario chiavi, copia di sicurezza verificata, schema `tessera-v2` (solo lettura/scrittura isolata), test di regressione XP/rango/badge | doc + test, nessun cambio visibile | regressione XP, backup/ripristino |
| **T1 Hub immersivo** | nuova schermata «La mia Tessera», carta fronte/retro, correzione sovrapposizioni, responsive iPhone | build in collaudo | layout 320–430 px, nessun overflow |
| **T2 Carriera** | Passaporto di carriera, registro XP per fonte, statistiche, badge | build in collaudo | coerenza con i calcoli esistenti |
| **T3 Atelier** | personalizzazione guidata, sfondi animati, titolo libero, rarità | build in collaudo | validazione input, reduce-motion |
| **T4 Vetrina e Collezione** | 6 slot, statistiche scelte, esportazione PNG, Collezione estesa | build in collaudo | export PNG, sblocchi |
| **T5 Identità Variante** | Passaporto Variante, universo/preferito da Atlas, backup identità, predisposizioni Friends | build in collaudo | migrazione non distruttiva |
| **T6 Predisposizioni** | `tvaTrophies`, slot Missioni, contratto identità pubblica | solo hook disattivati | nessun effetto XP |
| **T7 iPad e rifinitura** | layout iPad, performance, accessibilità, report, ZIP | build finale | suite essenziale + collaudo reale |
Ordine consigliato: T0 → T1 → T2 → T3 → T4 → T5 → T6 → T7 (T1 e T2 sono i più visibili). Nessuna fase viene avviata senza la tua approvazione dell'anteprima e della fase precedente.

## 5. Rischi e mitigazioni
- Regressione su XP/rango → test di regressione T0 e confronto prima/dopo su profili campione.
- Perdita dati → copia di sicurezza verificata + chiavi additive + nessuna cancellazione.
- Peso di `index.html` (43.000 righe) → il nuovo hub è un modulo lazy separato (`tessera2/`), come per Atlas.
- Animazioni su iPhone datati → opzione «Effetti ridotti» e rispetto di *reduce motion*.
- Friends su Firestore nel codice → non toccato; riallineamento rimandato.

## 6. Decisioni richieste all'utente (non assumo specifiche mancanti)
1. **Nome**: confermare «Tessera TVA 3.0» come nome visibile.
2. **Livelli oltre il 18** e nomi dei livelli: oggi non specificati (la curva è aperta); mantenere solo il numero?
3. **Slot vetrina**: 6 va bene (oggi 3)?
4. **Sfondi animati**: quanti e con quale rarità; sono tutti gratuiti o legati a sblocchi?
5. **Titolo libero**: ammesso? (testo libero ≤ 24 caratteri, solo locale; in Friends visibile solo se lo consenti).
6. **Cosa sarà visibile al partner** in Friends (nome, VAR-ID, emblema, motto, universo, preferito, aspetto, rango/livello?). Predisposto ma da decidere prima della macro-fase 8.
7. **Foto locale**: confermare che resti esclusa da sync e backup condivisi.
8. **Trofei Arcade/Quiz/Rankings** in vetrina: confermare solo come predisposizione.
9. Anteprime: approvare la direzione grafica (nero e oro, SVG originale) prima di T1.

## 7. Anteprime grafiche
`docs/tessera2/anteprima.html` (statica, navigabile, nessun codice dell'app): carta fronte/retro, Hub iPhone (5 schede), Carriera, Atelier, Collezione, Identità con slot Missioni/Friends predisposti, layout iPad. Sono mockup di progetto, non l'implementazione.
