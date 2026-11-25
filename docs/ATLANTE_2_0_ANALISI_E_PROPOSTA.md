# Atlante 2.0 — Analisi del database e proposta di progetto

> Branch: `test/tva-archives` · Data: 25/11/2026 · **Solo documentazione: nessun codice applicativo è stato scritto o modificato.**
> Stato: **IMPOSTAZIONE ARCHITETTURALE APPROVATA il 25/11/2026 (v. §10); interfaccia definitiva NON ancora approvata**. Storico: proposta del 25/11 in attesa di approvazione dell'utente (CLAUDE.md: «Atlante 2.0: prima di scrivere codice serve l'approvazione del progetto»).
> Misure eseguite in sola lettura su `index.html` (build `20261125-0030-mm6`) con script Python/BeautifulSoup; nessun dato personale coinvolto.

---

## 1. Requisiti della roadmap (riletti integralmente)

**Area 02 – Atlante 2.0:** restyling grafico completo · navigazione interattiva del Multiverso · dossier dinamici · cronologie individuali dei personaggi · rete delle relazioni · collegamenti con Timeline, fumetti e Miss Minutes · preferiti e collezioni · progressione dell'esplorazione.

**Area 03 – Marvel Database Expansion (obiettivi progressivi, area separata):** 1.000+ personaggi · 300+ varianti · 200+ artefatti e armi · 100+ universi e dimensioni · 150+ organizzazioni · 200+ luoghi e pianeti · 150+ eventi e saghe · 100+ specie ed entità cosmiche. Completare le schede esistenti (immagini, attori, poteri, origini, relazioni, apparizioni, fumetti, continuità). *Evitare duplicati e informazioni inventate.*

**Requisiti recuperati (24/11):** (a) risolvere le **13 decisioni sulle identità**; (b) verificare l'attribuzione TMDB e completare le **7 locandine** mancanti (N°073, 074, 077, 086, 107, 115, 125) + logo TMDB; (c) **correzioni dall'audit del 15/10** (sinossi/continuità N°046, 091–092, 119–120, 134; post-credit 094, 121, 123; schema anno/ambientazione; date e cast 027, 131, 132, 135–139; streaming Italia; prerequisiti) *solo con fonti verificabili*.

**Vincoli:** 0 €/mese · solo `test/tva-archives` · `main` congelato · nessuna perdita di dati personali/progressi/XP/badge/Episodes/Rankings/Friends/Arcade/TVA Live · Miss Minutes 1.0 congelata · nessun dato personale all'AI online · non inventare specifiche mancanti (le segnalo al §9).

---

## 2. Come è fatto oggi l'Atlante

L'Atlante **non ha un database strutturato a runtime**: è HTML scritto a mano dentro `index.html` (~43.000 righe). Ogni voce è `<li class="card-wrap" id="PREFISSO-slug" data-search="…">` con righe `detail-row` (chiave/valore) e collegamenti `mvNavigate('char-thor','char','T')`. Accanto esistono blob JSON a sé stanti:

| Blob | Contenuto | Uso |
|---|---|---|
| `atlasData` (v3) | 304 personaggi con `conta/stato/dubbio/assegnazione`, 5 identità dichiarate, 27 universi, 139 opere, 37 animate | sola lettura, sorgente di migrazione (non usato a runtime) |
| `relationshipGraphData` | 386 nodi, 2.454 archi orientati | grafo Relazioni |
| `mvMapData` | 27 universi con coordinate, 6 famiglie | mappa Multiverso (3B) |
| `tesseraCharIdsData` / `PowersData` / `LevelsData` | 304 / 164 / 159 | Tessera |
| `altTimelineData`, `cmpActorData`, `tmdbMap` | 138 / 45 / 131 | Timeline, Confronto attori, locandine |

Conseguenza: ogni informazione esiste in più copie (scheda HTML, grafo, Tessera, indice di Miss Minutes) e **nessuna è la fonte unica**.

---

## 3. Misure effettive (verificate nel codice, 25/11/2026)

| Tipologia | Conteggio verificato | Note |
|---|---|---|
| **Personaggi** (`char-`) | **304 schede** (300 «contano», 4 segnaposto da escludere) | 72 hanno «/» nel nome (alias o voci aggregate) |
| **Varianti** | **14 dossier `var-`** + 4 archi «variante» nel grafo + voci aggregate (es. «Peter Parker (Holland/Maguire/Garfield)», «Xavier (giovane e anziano)») | nessun tipo «variante» strutturato: 2 sole schede lo dichiarano |
| **Universi** (`uni-`) | **27 schede** = 27 nodi mappa | 16 «universi» nel grafo sono etichette testuali **senza scheda** |
| **Eventi** (`evt-`) | **3** | + 11 sezioni saghe (`sec-1a…1k`), 7 pannelli cronologici, 4 battaglie (`bat-`) |
| **Organizzazioni** (`org-`) | **17** | 6 campi ciascuna (fondata, leader, membri, scopo…) |
| **Oggetti/artefatti** (`art-`) | **16** | solo descrizione + «compare in» |
| **Luoghi / pianeti** (`luo-`, `pia-`) | **9 + 7 = 16** | |
| **Attori** (`att-`) | **49** | campo unico «RUOLI» |
| **Opere** (`item-`) / animate | **139** (138 Timeline) / **37** | |
| **Relazioni** | **2.454 archi orientati** (≈1,2k coppie): co-apparizione 1.522 · universo 692 · attore 106 · organizzazione 98 · **famiglia 28** · variante 4 · relazione 4 | solo 14 schede hanno il campo RELAZIONI |
| **Link interni** `mvNavigate` | **1.065, 0 rotti** | integrità buona |

**Distanza dagli obiettivi dell'area 03** (stato oggi → obiettivo): personaggi 304 → 1.000+ (30 %) · varianti 14 → 300+ (5 %) · artefatti 16 → 200+ (8 %) · universi 27 → 100+ (27 %) · organizzazioni 17 → 150+ (11 %) · luoghi/pianeti 16 → 200+ (8 %) · eventi 3 (+11 saghe) → 150+ (≈9 %) · specie/entità: **pagine aggregate già presenti** (Entità Cosmiche 26 — 6 sullo schermo, 20 mai apparse; Specie e Civiltà 8; Arti Mistiche 3) ma **senza schede individuali** collegate al registro. L'espansione richiede **fonti e contenuti**: non può essere generata senza rischio di invenzione (v. §9).

---

## 4. Duplicati, incongruenze, lacune, errori di collegamento

**Duplicati/identità.** Nessun titolo di scheda duplicato dopo normalizzazione; i duplicati reali sono **identità spezzate su più pagine** → i 13 gruppi del §5 (es. Mary Jane / Mary Jane Watson / MJ; Charles Xavier / Xavier / Xavier giovane e anziano).

**Incongruenze.**
- **Tre vocabolari diversi per gli universi:** il campo UNIVERSI dei personaggi è testo libero con **56 stringhe distinte** («MCU», «Fox-Verse · MCU + Fox-Verse», «isolato · MCU (Netflix)», «Legacy · MCU + Fox-Verse»…) contro 27 schede `uni-`: **nessuna chiave di collegamento** personaggio→universo; i 16 nodi-universo del grafo non puntano a schede.
- **Conteggi non allineati:** 304 pagine · 300 «contano» · 305 storico · 302 nodi grafo (storico) · 307 voci personaggio nell'indice di Miss Minutes (include schede curate) · 164 poteri (blob) vs 163 righe POTERI nelle schede · 159 livelli.
- **Relazioni di famiglia:** solo 28 archi, direzione ambigua («Padre» in entrambi i versi, già nota da `REPORT_relazioni_alberi_arti.md`); archi «variante» sospetti (Loki ↔ Jane Foster/Mighty Thor, Wanda ↔ Visione, Reed ↔ Sue); **6 archi non reciproci**.
- **Alberi genealogici:** solo MCU (FF, Asgard, Wakanda, Stark); Legacy/continuità alternative assenti.

**Informazioni mancanti (sulle 304 schede personaggio).** UNIVERSI assente in 5 · CORRELATI in 8 · POTERI in **141** · «NEI FUMETTI» in 73 · RELAZIONI in **290** · COLLEGAMENTI in 247 · DA LEGGERE in 261 · **192 personaggi (63 %) hanno una sola apparizione** · **nessun ritratto dedicato nelle schede personaggio** (solo 8 avatar generici in `assets/avatars`; 2 schede su 304 citano un'immagine) · 5 nodi isolati nel grafo (Firestar, A-Bomb, Skaar, James Rogers, Torunn) · 10 attori non collegati da alcuna scheda.
Altre tipologie: oggetti e luoghi hanno soltanto «descrizione» + «compare in»; eventi 3 campi; nessun campo di provenienza/fonte né di livello di verifica nelle schede HTML.

**Errori di collegamento.** 0 link `mvNavigate` rotti; 0 riferimenti N° inesistenti; 0 archi con destinazione inesistente; 0 id Tessera orfani. Problemi di *struttura*, non di integrità: **universi/oggetti/luoghi/eventi/battaglie non sono raggiunti da alcun link `mvNavigate` o dal grafo** (si arriva solo dai tab) · 16 nodi-universo senza scheda · `tmdbMap` 131 vs 138 titoli (7 locandine, già noto) · logo TMDB mancante.

**Test:** 7 suite FAIL preesistenti documentate in `PROBLEMI_PREESISTENTI.md`; non toccano l'Atlante ma la baseline va ripulita prima di una migrazione (§8, fase A0).

---

## 5. Le 13 decisioni sulle identità (da `docs/CANDIDATI_IDENTITA_D3.md`)

**Stato: tutte aperte; nessuna unificazione è mai stata eseguita.** Uniche identità già dichiarate in `atlasData.identita`: Charles Xavier (3 pagine, verificata), Peter Parker MCU/Raimi/Garfield (+ 5 totali nel blob).

| # | Gruppo | Pagine | Evidenza del documento | Opzione che propongo (a tua scelta) |
|---|---|---|---|---|
| 1 | Peter | `peter`, `peter-b-parker`, `peter-parker`, `peter-parker-holland-maguire-garfield`, `peter-quill-star-lord` | Parker ↔ Parker (H/M/G): **dichiarata**; il resto «debole»; Quill è altra persona | Parker ↔ aggregata = stessa identità con 3 incarnazioni; Peter B. Parker distinto; Quill distinto |
| 2 | Charles Xavier | `charles-xavier`, `xavier`, `xavier-giovane-e-anziano` | **dichiarata dalla guida** (verificata) | Un'identità, 3 pagine → una canonica + alias |
| 3 | Coulson | `coulson`, `coulson-lmd`, `phil-coulson` | Coulson ↔ LMD «possibile» | Coulson e Phil Coulson candidati a unione; LMD = **variante** |
| 4 | Groot | `groot`, `groot-piccolo` | «possibile» | Groot piccolo = incarnazione/variante di Groot |
| 5 | Capitan America | `sam-wilson-…`, `steve-rogers-…` | solo alias in comune; interpreti diversi | **Persone distinte** (alias «Capitan America» condiviso) |
| 6 | Ross | `everett-ross`, `generale-ross`, `generale-thaddeus-ross`, `thaddeus-ross` | Everett distinto; generale Ross / Thaddeus «debole» (universi diversi senza sovrapposizione) | Everett distinto; Thaddeus Ross va verificato per universo prima di unire |
| 7 | Ghost Rider | `ghost`, `johnny-blaze-…`, `robbie-reyes-…` | «debole» | **Persone distinte**; Ghost (altro personaggio) |
| 8 | Mary Jane | `mary-jane`, `mary-jane-watson`, `mj` | duplicato noto già nel report del 18/10 | Da decidere per universo (MJ MCU vs Raimi) |
| 9 | Bishop | `bishop`, `kate-bishop` | — | Probabilmente distinti (non verificato) |
| 10 | Janet | `janet`, `janet-van-dyne` | — | Da verificare |
| 11 | Kingpin | `kingpin` (Spider-Verse), `wilson-fisk-kingpin` | — | Da verificare (universi diversi) |
| 12 | Miles Morales | `miles-morales`, `miles-morales-e-altri` | voce aggregata | Aggregata = incarnazioni di Miles |
| 13 | Ravonna | `ravonna-renslayer`, `renslayer` | — | Da verificare |

*Per i gruppi 8–13 il documento D3 non riporta ancora prove sufficienti: non propongo un esito che non so sostenere. Serve la tua decisione, caso per caso.*

**Modello di risoluzione proposto (non distruttivo):** ogni decisione crea un'**identità** (entità canonica) con `incarnazioni/varianti` e una tabella di **alias/redirect** che mantiene valide **tutte le vecchie pagine e id** (`char-xavier` → apre l'identità `charles-xavier`). Nessun id viene eliminato, così preferiti, progressi, Tessera (`tesseraCharIdsData`), Variant ID, link di Miss Minutes e riferimenti Friends restano validi.

---

## 6. Audit del 15/10: correzioni già previste

Registro Master: la voce «Correzioni di dati certi» è **DA VERIFICARE** (solo X-Men chiuso, categoria `xmen` su 016/020/021); «Dati da aggiornare con fonte» **DA SVILUPPARE** (12 titoli «Prevista», 6 da verificare). Elenco da riconciliare con la build attuale, **solo con fonti datate**:

| Ambito | Titoli | Tipo |
|---|---|---|
| Sinossi/continuità | N°046, 091–092, 119–120, 134 | testo |
| Post-credit | N°094, 121, 123 | testo |
| Schema anno/ambientazione | trasversale | struttura dati |
| Date di uscita / cast | 027, 131, 132, 135–139 | dati con fonte |
| Streaming Italia | trasversale | dati con fonte |
| Prerequisiti incoerenti / Dependency Map | trasversale | logica |
| Locandine TMDB + logo | 073, 074, 077, 086, 107, 115, 125 | asset + diritti |

Queste correzioni sono nel perimetro Atlante (requisiti recuperati) ma **non sono implementabili senza che tu fornisca o approvi le fonti**: le inserisco in un registro «da verificare» con stato e fonte, mai come dato certo.

---

## 7. Proposta: architettura

**Principio:** passare da «HTML scritto a mano + blob duplicati» a **un registro dati unico, versionato, statico**, da cui l'interfaccia genera schede, grafo, mappa e indice. Costo 0 €: solo file JSON statici serviti da Netlify TEST e cache del Service Worker; **nessun nuovo servizio, nessun database esterno, nessuna AI a pagamento.**

1. **Registro `data/atlante/*.json`** (caricamento pigro per tipologia: `personaggi`, `varianti`, `universi`, `eventi`, `organizzazioni`, `oggetti`, `luoghi`, `specie`, `attori`, `relazioni`). Ogni entità ha: `id` **stabile e identico a quello attuale** (`char-thor`…), `tipo`, `nome`, `alias[]`, `identita` (canonica) / `incarnazioni[]`, `universi[]` (chiavi verso `uni-`, non testo libero), `apparizioni[]` (N° opera + ruolo), `relazioni[]` tipizzate e orientate, `fumetti[]`, `immagine` + `diritti`, **`fonte` e `verifica` (verificata / da verificare / ipotesi / voce)** per distinguere canone, ipotesi e voci (stessa regola di Miss Minutes).
2. **Migrazione «strangler», non big bang:** uno script `tools/atlante_estrai.py` estrae l'HTML attuale nei JSON con **test di round-trip** (stessi id, stessi conteggi 304/14/27/17/16/9/7/3/4/49, stessi 1.065 link). L'HTML esistente resta come **fallback** finché ogni tipologia migrata non è approvata.
3. **Relazioni:** una sola tabella di archi con direzione, tipo (famiglia, alleanza, rivalità, mentore, identità/variante…) e **fonte**; i 1.522 archi di co-apparizione e 692 di universo vengono **derivati** (non memorizzati), le 28 relazioni familiari e le 8 «variante/relazione» vengono riviste una a una.
4. **Dati dell'utente (protezione assoluta):** preferiti, collezioni, progressione esplorazione in **nuova chiave localStorage** `tva-atlante-v2` (additiva); nessuna chiave esistente viene letta-riscritta o rinominata; l'estensione dell'esportazione/backup profilo (`normalizzaProfilo`) è **solo additiva** con test «profilo vecchio importato = identico». Nessun dato di Atlante passa da Firebase.
5. **Integrazione con Miss Minutes (congelata):** oggi Miss Minutes legge Atlante tramite `tvaMissMinutesHost` con una **whitelist di 6 blob**. Per non toccarla, la nuova pipeline **continuerà a produrre i blob attuali** (stesso formato, generati dal registro) e la grammatica di link `char:/uni:/arc:/att:/item:/tab:/cen:/page:` resta identica; i nuovi tipi (luoghi, specie, varianti) saranno raggiungibili solo se tu autorizzi una modifica minima alla whitelist (v. decisione D7).
6. **Prestazioni su iPhone:** liste virtualizzate/paginate, immagini lazy in `webp`, rendering della scheda solo all'apertura; l'`index.html` si alleggerisce. Nessun `filter`/`backdrop-filter` sulla mappa (vincolo già rispettato in 3B).

---

## 8. Funzionalità, organizzazione grafica, piano

### Funzionalità (corrispondenti ai requisiti dell'area 02)
- **Home Atlante** con ingressi per tipologia, ricerca globale (nome, alias, universo, attore) e «Continua l'esplorazione».
- **Dossier dinamico** unico per tutte le tipologie: intestazione (immagine, tipo, universo, stato di verifica), blocchi (Identità e incarnazioni · Apparizioni · Cronologia individuale · Relazioni · Fumetti · Poteri · Collegati), con i campi vuoti **nascosti o dichiarati «dati non ancora disponibili»**, mai riempiti a caso.
- **Multiverso interattivo:** la mappa 3B (27 nodi, pan/pinch già testati) collegata ai personaggi di ogni universo tramite la chiave `universi[]`.
- **Cronologia individuale** per personaggio (apparizioni ordinate per uscita e per cronologia interna, con le due viste già presenti in Timeline).
- **Rete delle relazioni** esplorabile dal dossier (vicinato a 1–2 salti, filtri per tipo, nessun anello unico da centinaia di nodi: si usa il vicinato).
- **Collegamenti:** Timeline (opere), fumetti (letture già presenti, «DA LEGGERE»), Miss Minutes (apri la scheda in chat / chiedi a Miss Minutes dal dossier, senza modificarla).
- **Preferiti e collezioni** (locali) e **progressione dell'esplorazione** (schede viste per tipologia/universo; nessun XP né badge nuovo senza tua decisione D6).
- **Pannello «Qualità dati»** (strumento interno): identità da risolvere, schede senza fonte, 7 locandine, correzioni audit.

### Organizzazione grafica
Stessa identità TVA già presente (nero/ambra dell'app, ma senza ridisegnare Home, Tessera o Miss Minutes). Schermate: **Home Atlante** (griglia di 8 tipologie con contatori reali) → **Elenco** (filtri a chip, ricerca, ordinamenti) → **Dossier** (scheda a blocchi comprimibili, barra azioni sticky) → **Mappa/Rete** (a schermo intero con anteprima in basso). Mobile-first 390 px, bersagli ≥44 px, safe area iOS, `prefers-reduced-motion`, contrasti misurati sui pixel come in E3. Mockup su 4 schermate da approvare **prima** dell'implementazione grafica.

### Piano per fasi (ognuna con verifica e tua approvazione prima della successiva)
| Fase | Contenuto | Esito atteso | Gate |
|---|---|---|---|
| **A0 – Baseline** | Congelo stato attuale (snapshot ZIP/branch), misure ufficiali in roadmap, suite essenziale verde per l'Atlante | numeri di riferimento immutabili | tuo OK al progetto |
| **A1 – Registro dati** | Script di estrazione + JSON + test round-trip; generazione dei blob attuali identici | 0 differenze funzionali, 0 id persi | tuo OK |
| **A2 – Identità** | Applicazione delle **13 decisioni** (alias/redirect, incarnazioni) | nessun id rotto, Tessera invariata | le tue 13 decisioni |
| **A3 – Dossier e navigazione** | Nuovo dossier unico, Home Atlante, elenchi, ricerca, back/X coerenti | tutte le tipologie apribili | collaudo iPhone |
| **A4 – Multiverso e relazioni** | Mappa↔personaggi, cronologie individuali, rete locale | link universo reali | collaudo iPhone |
| **A5 – Preferiti, collezioni, progressione** | `tva-atlante-v2`, backup additivo | profilo vecchio importato identico | collaudo iPhone |
| **A6 – Collegamenti e Miss Minutes** | Pulsanti dal dossier, blob invariati | nessuna modifica a MM salvo D7 | tuo OK |
| **A7 – Rifinitura e correzioni audit** | Dati con fonte, 7 locandine, attribuzione TMDB | registro «da verificare» azzerato dove possibile | approvazione finale |

L'**espansione numerica (area 03)** parte **dopo A2–A3**, per lotti (es. 50 voci per tipologia), ognuno con fonte dichiarata e verifica: la struttura 2.0 serve proprio a poterla fare senza duplicati.

### Rischi e mitigazioni
| Rischio | Mitigazione |
|---|---|
| Perdita/rottura di id e progressi | id invariati + alias; test round-trip; nessuna scrittura su chiavi esistenti |
| Regressioni su Miss Minutes/Tessera | blob generati identici; suite engine/UI esistenti rieseguite |
| Contenuti inventati | campo `fonte`/`verifica` obbligatorio; niente testo generato da AI senza tua revisione |
| Diritti immagini | nessuna immagine senza licenza dichiarata; ripiego = emblema (come oggi) |
| Peso/prestazioni su iPhone | caricamento pigro, paginazione, test su 4× CPU |
| 7 suite FAIL preesistenti | restano classificate; non si «aggiustano i test per far passare» |

---

## 9. Decisioni e informazioni che mi servono (non invento specifiche)

- **D1 – Progetto:** approvi architettura (§7), funzionalità (§8) e piano A0–A7 così come sono, o con modifiche?
- **D2 – Identità:** le 13 decisioni (§5), anche a gruppi; le mie opzioni sono proposte, i gruppi 8–13 non hanno ancora prove sufficienti.
- **D3 – Ordine delle fasi:** prima identità (A2) o prima nuova interfaccia (A3)?
- **D4 – Fonti per i dati:** quali fonti consenti per l'espansione e le correzioni audit (e per quali tipologie)? Senza fonti non inserisco dati nuovi. Le licenze di eventuali database esterni vanno verificate prima.
- **D5 – Immagini:** dove reperire ritratti/locandine con diritti verificati (oggi 0 ritratti nelle schede e 7 locandine mancanti)?
- **D6 – Progressione:** l'esplorazione deve dare XP/badge (tocca il sistema Missioni, protetto) oppure essere solo un indicatore locale?
- **D7 – Miss Minutes:** autorizzi, se serve, **una sola modifica minima** alla whitelist dell'host per esporre i nuovi tipi (luoghi, specie, varianti)? Senza, resta com'è.
- **D8 – Specie ed entità cosmiche:** tipologia da strutturare (oggi esistono solo pagine aggregate: Entità Cosmiche 26, Specie e Civiltà 8, Arti Mistiche 3): la creo come tipo a sé o dentro «personaggi»?

**Cosa NON farò senza tuo ordine:** scrivere codice Atlante, modificare `main`, pubblicare, attivare servizi esterni, toccare Miss Minutes mm6, rimuovere funzionalità, dichiarare «completata» l'area 02.

---

## 10. Approvazione dell'utente del 25/11/2026 e integrazioni (recepite)

**Approvato:** impostazione architetturale generale (registro JSON statico, ID conservati, alias, migrazione non distruttiva). **Non approvata:** interfaccia definitiva (si procede con anteprime grafiche prima dell'implementazione). Nessun codice ancora scritto.

**Visione:** enciclopedia interattiva dell'intero universo Marvel — MCU, fumetti, universi Sony e Fox, animazione, videogiochi, continuità alternative — **non limitata alle opere della Timeline**; continuità narrative sempre distinte.

**Obiettivi progressivi (sostituiscono, per l'Atlante, quelli del §1; non autorizzano dati inventati né conteggi gonfiati):** 1.000+ personaggi · 300+ varianti · 100+ universi · 100+ organizzazioni · 150+ artefatti e armi · 150+ luoghi e pianeti · 100+ eventi · 100+ battaglie · **10.000+ relazioni significative** · categorie dedicate a specie ed entità cosmiche. *(Valori verificati oggi: 304 · 14 · 27 · 17 · 16 · 16 · 3 (+11 saghe) · 4 · 2.454 archi orientati, di cui solo ~1,2k coppie e in gran parte derivati da co-apparizioni: le relazioni «significative» tipizzate sono oggi poche decine.)*

**Schema esteso:** campi per tipologia — identità, biografia, origini, storia, poteri, debolezze, equipaggiamento, affiliazioni, relazioni, varianti, apparizioni, eventi, riferimenti bibliografici, fonti; identificatori stabili; relazioni tipizzate; `fonte` e `verifica` per ogni dato. **Una sola scheda per entità con più categorie** (`categorie[]`): un'entità cosmica può essere anche «personaggio» senza duplicati.

**Fonti autorizzate:** Marvel.com, pubblicazioni Marvel, Marvel Database, TMDB e altre fonti attendibili e pertinenti, **nel rispetto di licenze, condizioni d'uso e limiti API**; testi **sempre originali**, nessuna copia integrale di descrizioni protette; per immagini e locandine il diritto d'uso si verifica a parte e si mantengono i segnaposto.

**Interfaccia da progettare insieme (anteprime prima del codice):** Home Atlante · Esplorazione del Multiverso · Catalogo personaggi · Dossier · Confronto personaggi/varianti · Nexus interattivo delle relazioni · Eventi e saghe · Artefatti, organizzazioni, specie ed entità cosmiche · Ricerca globale, filtri, collegamenti · Preferiti e collezioni. Identità grafica premium TVA Archives.

**Progressione:** XP e badge legati all'esplorazione, integrati nel sistema esistente, **senza azzerare/duplicare progressi e senza XP ripetibili con la stessa azione**. **Le regole di assegnazione vanno presentate a te prima di qualsiasi implementazione.** Risposta a D6.

**Miss Minutes:** autorizzate solo modifiche minime per consultare nuovi tipi e relazioni; nessuna modifica a interfaccia, comportamento o gateway senza necessità documentata. Risposta a D7.

**Fasi:** A0 e A1 invariate; **A2** usa `docs/ATLANTE_2_0_DECISIONI_IDENTITA.md`; prima di A3 si preparano le **anteprime grafiche** da approvare.
