# Database Expansion — W8 «Qualità e completezza» (build `20261128-2000-db7`, TEST)

Stato: consegnata per collaudo; **non dichiarata «completata»** (serve l'approvazione esplicita dell'utente). Solo `test/tva-archives`, `main` congelato, 0 €, Tessera TVA 2.0 non avviata; motore, gateway e quote di Miss Minutes invariati (solo dati). Progressione, XP, badge, ID esistenti, ritratti privati e dati personali preservati.

> **Obiettivi storici (corretti):** 1.000+ personaggi · 300+ varianti · 200+ artefatti e armi · 100+ universi e dimensioni · **10.000+ relazioni narrative documentate** (non 500). Sono traguardi orientativi: nessun contenuto è stato inventato per raggiungerli.

## 1. Conteggi canonici deduplicati (`python3 tools/db_conteggi.py`)
Totale **6.599 voci** = 452 storiche + 6.147 nuove (698 duplicati d'ID e 37 di QID scartati). Livelli: **A 448 · B 453 · C 5.690** (A/B includono 315 storiche A e le promozioni W8).
| Categoria | Voci | Categoria | Voci |
|---|---|---|---|
| Personaggi/identità | 1.958 | Interpreti | 979 |
| Organizzazioni | 573 | Opere/testate | 1.579 |
| Artefatti e armi | 392 | Luoghi | 395 |
| Universi e dimensioni | 43 | Eventi/saghe | 57 |
| Entità cosmiche | 43 | Specie | 29 |
| Battaglie | 20 | Pianeti | 11 |
| Autori/creatori | 458 | Titoli / hub / mantelli | 49 / 3 / 2 |
Nuove per ondata: W1 1.006 · W2 592 · W3 433 · W4 110 · W5 1.208 · W6 431 · W5c 2.023 · **W8 336** (artefatti 282 prima della deduplicazione per QID, specie 19, eventi 14, entità cosmiche 24, universi 5).

## 2. Obiettivi storici: raggiunti / non raggiunti
| Obiettivo | Esito | Nota |
|---|---|---|
| 1.000+ personaggi | **raggiunto: 1.958** | |
| 300+ varianti | **non raggiunto: 0 verificate** | 2.691 candidate («Nome (Earth-N)» con base nel canon) restano in staging: l'unica fonte è Marvel Database e non esiste una seconda fonte indipendente a costo zero (D12). Richiede una **decisione dell'utente** (eventuale deroga documentata a D12 per le varianti) |
| 200+ artefatti e armi | **raggiunto: 392** | 129 pre-W8 + 263 nuove verificate (Marvel Database + Comic Vine per nome o Wikidata legato a Marvel) |
| 100+ universi e dimensioni | **non raggiunto: 43** | 4.123 pagine «Earth-N» in staging: nessuna seconda fonte indipendente (Comic Vine non ha gli universi Marvel; Wikidata ne copre pochi) |
| 10.000+ relazioni narrative documentate | **non raggiunto: 8.390** (8.145 db + 245 storiche), di cui **993 verificate** | vedi §4 |

## 3. Dossier approfonditi
Compositore riscritto (`tools/db_dossier.py`): fino a 8 sezioni (Sintesi, Origini e identità, Affiliazioni/luoghi/vicende, Poteri e abilità, Equipaggiamento e debolezze, Identità alternative e continuità, Relazioni, Interpreti e apparizioni), sintesi originali in italiano composte **solo** da fatti verificati; relazioni verificate separate da quelle «indicate dalle fonti»; niente testi copiati.
Soglie misurabili (`livelli_w8.json`): **A** ≥6 sezioni, ≥900 caratteri, ≥10 campi-fatto e ≥1 relazione verificata o ≥3 fonti; **B** ≥4 sezioni, ≥450 caratteri, ≥6 campi.
Risultato: 684 dossier; **133 promossi ad A** (media 1.179 caratteri, 15 campi), **235 promossi a B**; 316 restano C (dati insufficienti). Limite dichiarato: senza copiare la prosa delle fonti, biografie narrative estese non sono producibili; i dossier restano composizioni di fatti documentati (non romanzati).

## 4. Relazioni e Nexus
Relazioni narrative db: **8.145** (7.359 «da verificare», 786 verificate) + 245 storiche (207 con **verifica documentale** effettiva dal registro `_verifiche.json`). Fonti: Wikidata, parametri infobox (MCU Wiki/Marvel Database), Comic Vine (solo ID amici/nemici/team di 480 personaggi su 785 richiesti: gli altri hanno restituito errore e sono recuperabili con un nuovo avvio del job `db-w5c`).
Ogni relazione dichiara il **metodo** (`metodo`): *automatica* (Wikidata + riscontro relazionale direzionale Wikipedia: 705; Wikidata + infobox: 81) oppure *nessuna verifica (una sola fonte)* (7.359). Le verifiche automatiche NON sono verifiche documentali. Tipi: rivalità 3.338, alleanza 2.473, appartenenza 1.856, famiglia 330, partner 111, mentorato 37. Collegamenti editoriali (1.027), co-apparizioni e controparti restano separati e fuori dai conteggi.
Le «da verificare» sono mostrate come tali nel Nexus e escluse di default dai percorsi.

## 5. Raccolta mirata (W8)
Marvel Database (CC BY-SA, solo titoli/categorie/parametri-fatto): 12 categorie + 3.848 pagine «Earth-N» + 375 personaggi per le varianti = 33.751 pagine. Seconda fonte indipendente (D12): Wikidata (etichetta esatta + classe «fictional» + legame con Marvel; 119 corrispondenze) oppure Comic Vine (nome esatto in oggetti, origini, concetti, saghe, personaggi, team; 5.086 oggetti, 1.275 concetti, 10 origini, 5.834 luoghi). La sola citazione della «prima apparizione» NON è considerata verifica. Staging W8 + W5c: **13.661** candidati documentati con motivo («una sola fonte»).

## 6. Ritratti e grafica
Pipeline privata invariata (IndexedDB, mai nel repository/ZIP). Preparate **516 identità candidate** con interpreti documentati (`ritratti_candidati.json`, solo metadati locali): l'esecuzione resta **sospesa** perché le condizioni d'uso TMDB per l'archiviazione non sono confermate (nessun nuovo metadato TMDB archiviato). Le voci senza immagine usano l'emblema originale TVA Atlas (monogramma/composizione), mai presentato come ritratto.

## 7. Integrazione globale
Nuove voci native in Atlas, ricerca, Multiverso, Nexus; tipo «Varianti e incarnazioni» predisposto nel catalogo (vuoto finché non verificate); progressione A5 attiva per le voci verificate di livello A/B/C (regole e valori invariati, ricompense mai revocate); archivio Miss Minutes: 6.147 schede verificate (testate come «Nome (testata)»).

## 8. Verifiche automatiche essenziali (tutte superate)
db_test 18 · db_w1 30 · db_w5 12 · **db_w8 18** · db_harvest 30 · db_relverify 10 · a5 46 · atlas_db (Miss Minutes) 6 · engine 42 · a40 · UI: db_ui, a3 32/32, a5_ui 17/17, a41, a7 110/110.

## 9. Attività residue
(1) Decisione sulle varianti (deroga D12) · (2) seconda fonte per universi (nessuna a costo zero) · (3) completare le relazioni Comic Vine dei 305 personaggi mancanti e verificarle documentalmente · (4) ritratti nuove identità (termini TMDB) · (5) saghe/eventi in staging (1.391) · (6) Comics Library futura separata · (7) Safari iOS/iPad reali da collaudare.
