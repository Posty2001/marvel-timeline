# Database Expansion — Preparazione (NON AVVIATA)

Data: 27/11/2026 · Stato: **solo pianificazione**. Nessun dato è stato aggiunto, nessun codice di espansione scritto.
Documento gemello: `docs/DATABASE_EXPANSION_PROPOSTA.md` (proposta operativa). Base: build **a70** (TVA Atlas congelato).

Vincoli permanenti: sviluppo solo su `test/tva-archives`; produzione (`main`) congelata; costo 0 €; nessun dato personale perso o inviato all'AI online; nessuna pubblicazione/deploy/attivazione di servizi esterni senza autorizzazione esplicita; nessun dato inventato; Miss Minutes congelata.

---

## 1. Stato di partenza VERIFICATO nel codice (27/11/2026)

> Conteggi verificati leggendo i file; i conteggi storici dei documenti restano separati nella Master Roadmap.

### 1.1 Registro sorgente (`data/atlante/`)
| File | Voci | Note |
|---|---|---|
| `personaggi.json` | 304 | pagine «char-*» estratte da `index.html` |
| `attori.json` | 49 | «att-*» |
| `universi.json` | 27 | «uni-*» |
| `organizzazioni.json` | 17 | «org-*» |
| `artefatti.json` | 16 | «art-*» |
| `luoghi.json` | 9 | «luo-*» |
| `pianeti.json` | 7 | «pia-*» |
| `eventi.json` | 3 | «evt-*» |
| `battaglie.json` | 4 | «bat-*» |
| `identita.json` | 315 identità, 3 hub, 2 mantelli, 7 segnaposto, 304 redirect pagina→identità | modello A2 («id-*», «hub-*», «man-*») |
| `relazioni.json` + `relazioni_lotti/` + `_verifiche.json` | 1276 record nel runtime | v. 1.3 |
| `assets.json`, `engine/` | registro ritratti (solo metadati) | immagini PRIVATE, mai nel repository |

**Fatto architetturale chiave:** il registro `data/atlante/*.json` è oggi *estratto* dall'`index.html` (`tools/atlante_estrai.py`, «sorgente di migrazione», strangler). Le schede nuove NON possono vivere nell'HTML: serve una **sorgente canonica nuova** (v. proposta §4). `identita.json` e le relazioni sono invece già dati canonici editati a parte.

### 1.2 Runtime (`atlante2/data/`, generato da `tools/atlante_a3.py` / `atlante_a4.py`)
- `index.json`: **452 voci** (315 identità, 49 attori, 27 universi, 17 organizzazioni, 16 artefatti, 9 luoghi, 7 pianeti, 7 eventi [3 + 4 battaglie], 3 hub, 2 mantelli); 99 140 byte (~19 KB gzip) → ~220 byte/voce non compressa.
- `d/NNN.json`: shard di 24 dossier, caricati solo all'apertura. `nexus/g.json` (81 KB): 1276 record relazione.
- Tutto lazy: nessun dato Atlas viene caricato prima dell'ingresso (test `a3_test`).
- **Implicazione di scala:** estrapolando linearmente, 20 000 voci ≈ 4,4 MB di indice non compresso (~0,85 MB gzip): l'indice monolitico NON regge; serve indice a livelli + ricerca per prefisso (proposta §7). È un'estrapolazione, da misurare.

### 1.3 Relazioni (nel runtime)
1276 record = 245 narrative (207 con fonte, 4 «guida», 34 «da verificare») + 1026 editoriali + 5 controparti. Regola: co-apparizioni ≠ relazioni narrative; «da verificare» mai presentata come verificata. Obiettivo storico 500 narrative: NON raggiunto, non prerequisito.

### 1.4 Titoli e altri registri collegati (fuori dal perimetro Atlas, da NON toccare senza decisione)
- Timeline/guida: **138 titoli** numerati N°001–N°138 (ordine di visione, Tessera, Missioni, progressi personali). 7 senza locandina TMDB (073, 074, 077, 086, 107, 115, 125).
- Archivio Miss Minutes: 136/138 (mancano N°077 e N°125; nessun ID inventato). TVA Episodes: catalogo generato da TMDB (`tmdb-sync.yml`).
- 27 universi/continuity oggi coperti: MCU (Earth-199999), Raimi, Garfield, SSU, Fox, Fantastici Quattro 1994, Earth-121698, Earth-TRN123, Blade, Daredevil/Elektra, Ghost Rider, Spider-Noir, Hulk 2003, Earth-828, Earth-838, TVA, What If…?, X-Men '97, Your Friendly Neighborhood Spider-Man, Marvel Productions (due raggruppamenti), Marvel Animation Universe, continuity animate minori, Spider-Verse Sony, Legion, The Gifted, Marvel Zombies.

### 1.5 Integrazioni e dati personali da preservare (inventario)
| Elemento | Chiave/legame | Rischio dall'espansione |
|---|---|---|
| ID esistenti (`id-*`, `char-*`, `uni-*`, …) | immutabili; `baseline_A0.json` (`ids_sha256`) | rinomina/ri-slug involontari |
| Ritratti privati | IndexedDB `tva-atlante-ritratti`, chiave = ID identità + continuità | cambio ID o unificazioni |
| Progressione A5 | `tva-atlante-v2` (`esp`, `ric`, `xp`, `badge`, `hub`, `uni`, `rel`, `fav`, `col`) + backup `-bak` | totali che crescono; ID spariti |
| XP Tessera | riga additiva `leggiXpAtlante()` (tetto 30/giorno) | duplicare ricompense |
| Preferiti/raccolte | per ID | ID orfani |
| Link Miss Minutes | `atl:<id>`, `tvaA3.go(pageId)` via `redirect`/`lnk` | pagine rimosse |
| Percorsi/Nexus | nodi solo via ID | relazioni verso voci cambiate |
| Redirect | `index.json.redirect` (304 pagine→identità) | collisioni |

Regole A5 da rispettare (approvate): Dossier esplorato +2, Hub completato +15, Universo completato +25, Primo confronto +5, Prima raccolta +5, Badge +40, Nexus +1 per relazione narrativa distinta (max 10/giorno), tetto Atlante 30 XP/giorno con eccedenze differite, registro ricompense permanente, **badge mai revocati**. Esplorabile = identità effettiva e documentata (esclusi segnaposto, alias, voci in verifica).

## 2. Cosa significa «database estremamente completo» — dimensioni del problema
Il perimetro richiesto è: MCU, universi cinematografici precedenti, serie TV, animazione, fumetti; tutte le categorie dell'Atlante. Le categorie attuali sono 9 (personaggi, attori, universi, organizzazioni, artefatti, luoghi, pianeti, eventi, battaglie). Per includere *opere* e *fumetti* servono con ogni probabilità **nuove categorie** (v. proposta §3): sono decisioni dell'utente, non assunte qui.
Le dimensioni reali del perimetro (soprattutto fumetti) non sono state misurate: il piano prevede un **censimento (W0)** con dati pubblici prima di fissare obiettivi numerici. Non sono state inventate stime di quantità.

## 3. Fonti candidate a costo zero (licenze verificate il 27/11/2026)
| Fonte | Uso | Condizioni rilevate |
|---|---|---|
| **TMDB API** | film/serie/animazione, cast, date, immagini (già in uso, chiave nei Secret) | gratuita per uso non commerciale con attribuzione (testo/logo nella sezione «Informazioni/Crediti»); il limite storico di 40 richieste/10 s è stato disattivato nel 2019 (da riconfermare); uso commerciale richiede accordo |
| **Comic Vine API** | fumetti (personaggi, volumi, numeri, team, luoghi, oggetti) | solo uso non commerciale; chiave gratuita; 200 richieste/risorsa/ora; link a Comic Vine dove si usano i dati; niente CORS (solo lato server/Actions); una sola chiave alla volta (blocco 24 h se più chiavi) |
| **Grand Comics Database (GCD)** | metadati di albi, storie, credits, apparizioni di personaggi | contenuti sotto CC BY-SA 4.0; esportazioni CSV/JSON e dump pubblicati |
| **Wikidata** | identificatori, relazioni strutturate, date | dati strutturati a licenza libera (CC0, noto: riconfermare nei termini prima dell'uso) |
| **Wikipedia / Fandom (Marvel Database, MCU Wiki, ecc.)** | verifica incrociata e link | testo CC BY-SA 3.0: attribuzione + share-alike; **si estraggono fatti, non prosa**; testi riscritti in italiano con fonte dichiarata |
| **Marvel.com / Marvel API** | — | API ritirata (v. roadmap A3.1); solo link/verifica manuale, nessuna copia di testi |
| Immagini | — | nessun diritto concesso: restano ritratti **privati** sul dispositivo (decisione A3.1), nessuna immagine nel repository |

Nota legale: non è consulenza legale. Le condizioni CC BY-SA (share-alike) e «non commerciale» valgono finché l'app resta personale/gratuita; un'eventuale distribuzione pubblica richiede una revisione di conformità prima.

## 4. Vincoli tecnici e di sostenibilità a 0 €
- **Esecuzione**: GitHub Actions già usato (`tmdb-sync.yml`, job a blocchi riprendibili). Il limite di minuti gratuiti dipende dal piano/visibilità del repository: **da verificare** prima di pianificare carichi (non assunto).
- **Dimensione repository**: `.git` ≈ 122 MB, working tree ≈ 66 MB. Il dato grezzo scaricato NON va nel branch di sviluppo: canale dedicato (branch dati tipo `mm-archivio`) o artefatti Actions; nel repository solo dati normalizzati e compressi.
- **Chiavi**: solo nei Secret (TMDB esiste; Comic Vine richiede chiave gratuita personale — attivazione = decisione dell'utente).
- **Deploy**: lo ZIP lo pubblica l'utente (Netlify); nessun servizio nuovo.
- **iPhone**: budget di memoria/rete da definire e misurare (proposta §7).

## 5. Decisioni aperte (da risolvere prima di avviare)
Rinviano alla numerazione D1–D14 della proposta. In sintesi: nuove categorie (opere, fumetti, creatori?); profondità per i soli-fumetto; ordine delle ondate; rapporto con i 138 titoli numerati (nessun cambio di N°/percentuali); regola su completamento universi/hub quando la banca dati cresce; obiettivo relazioni; attivazione Comic Vine; testi in italiano (modello/traduzione/modelli di frase); N°077 e N°125; Johnny Storm N°117; 34 relazioni «da verificare»; compilazione ritratti.

## 6. Punti aperti ereditati
1. N°077 e N°125: fonte per l'archivio Miss Minutes (nessun ID inventato).
2. Discrepanza Johnny Storm N°117 (a43).
3. 34 relazioni narrative «da verificare»: criterio di promozione/scarto.
4. Compilazione ritratti privati (aperta).
5. `tests/cons_test.py` «Back 2» (8 px, preesistente).
6. Verifiche su dispositivi Apple reali (non bloccanti): `docs/ATLANTE_2_0_VERIFICHE_IN_SOSPESO.md`.

## 7. Criteri di avvio
La fase parte solo dopo: (a) approvazione esplicita del piano, (b) risposta alle decisioni D1–D14 (o conferma dei default proposti), (c) autorizzazione per eventuali nuove chiavi/servizi gratuiti. Primo passo operativo previsto: Ondata 0 (architettura + censimento, nessun contenuto pubblicato).
