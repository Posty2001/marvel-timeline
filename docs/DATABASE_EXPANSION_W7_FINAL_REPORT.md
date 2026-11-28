# DATABASE EXPANSION — W7 Final: report di consolidamento (build `20261128-2300-db8`, TEST)

Stato: **in attesa di approvazione dell'utente; non dichiarata «completata»**. Tessera TVA 2.0 NON avviata. Produzione congelata, solo TEST, 0 €.
Engine, gateway, quote e verificatore di Miss Minutes, regole XP (`a5.js`) e dati personali: **invariati** (verificato da `tests/db_integrazione_test.py` contro il commit db7).

## 1. Conteggi canonici (deduplicati per ID e QID; `python3 tools/db_conteggi.py`)
Voci canoniche deduplicate: **6.591** (6.599 ID registrati nei canon, di cui 8 scartati perché duplicati per QID Wikidata; i report precedenti citavano 6.599). Per categoria × livello:

| Categoria | A | B | C | Totale |
|---|---|---|---|---|
| Identità (personaggi) | 448 | 248 | 1.262 | 1.958 |
| Entità cosmiche/sovrannaturali | 4 | 16 | 23 | 43 |
| Artefatti e armi | 0 | 17 | 375 | 392 |
| Specie e civiltà | 0 | 6 | 23 | 29 |
| Universi e dimensioni | 0 | 27 | 16 | 43 |
| Eventi e saghe | 0 | 7 | 50 | 57 |
| Organizzazioni | 0 | 81 | 492 | 573 |
| Luoghi | 0 | 16 | 379 | 395 |
| Pianeti / Battaglie | 0 | 0 | 31 | 31 |
| Hub / Mantelli | 0 | 5 | 0 | 5 |
| Titoli (storico) | 0 | 49 | 0 | 49 |
| Opere / Attori / Creatori | 0 | 0 | 3.016 | 3.016 |
| **Totale** | **452** | **472** | **5.667** | **6.591** |

## 2. Conteggi separati (definiti dai dati)
- **Personaggi** distinti (identità che contano come personaggio): **1.958**.
- **Identità** canoniche: 1.958 (coincidono: ogni identità canonica è un personaggio distinto; omonimi in continuità diverse restano voci separate, mai fuse).
- **Varianti** verificate come voce autonoma: **0**; marcate come variante nel registro storico (`variante_multiversale`, `copia_artificiale`): 4; in staging (una sola fonte, D12): 2.691.
- **Incarnazioni** documentate (fasi/interpreti della stessa identità): **7** su 3 identità.
- **Mantelli**: 2. **Hub**: 3 (non contano come personaggi).

## 3. Confronto con gli obiettivi storici (orientativi, nessun dato inventato)
| Obiettivo | Valore attuale | Esito |
|---|---|---|
| 1.000+ personaggi | 1.958 | raggiunto |
| 300+ varianti | 0 verificate (+4 storiche, 2.691 in staging) | **non raggiunto** (serve decisione sulla deroga D12) |
| 200+ artefatti e armi | 392 | raggiunto |
| 100+ universi e dimensioni | 43 (4.123 pagine «Earth-N» in staging) | **non raggiunto** (manca una seconda fonte gratuita indipendente) |
| 10.000+ relazioni narrative documentate | 8.390 (8.145 database + 245 storiche), di cui 993 verificate | **non raggiunto** |
Le relazioni verificate automaticamente (campo `metodo`) restano distinte da quelle verificate documentalmente; co-apparizioni, collegamenti editoriali e controparti non entrano nei conteggi.

## 4. Dossier approfonditi (W7 Final)
Il compositore (`tools/db_dossier.py`) ora copre anche entità cosmiche, artefatti/armi e specie (solo fatti verificati del canon, nessun testo copiato; tipo dichiarato come «classificazione editoriale», non come tesi sulla natura del personaggio). Dossier totali: **828** (A 137, B 257, C 434; soglia minima 3 sezioni e 200 caratteri). Promozioni A/B registrate in `livelli_w8.json`: 394. I dossier A/B sono visibili in Atlas, ricerca e archivio di Miss Minutes.
Limite: la profondità dipende dai fatti presenti nelle fonti consultate; dove mancano sezioni (storia, trasformazioni, equipaggiamento) non vengono inventate.

## 5. Integrazione globale
`tests/db_integrazione_test.py` (17 verifiche): ricerca per nome su 400 voci campionate, relazioni del Nexus con ID esistenti, universi del Multiverso, livello A/B/C per la progressione, 6.147 schede nell'archivio di Miss Minutes, dossier collegati, XP e motore AI invariati. Altre suite: db_test 18, db_w1 30, db_w5 12, db_harvest 30, db_relverify 10, db_w8 18, a5 46, db_ui: tutte superate.

## 6. Sistema incrementale e ritratti
`python3 tools/db_ricostruisci.py` (ordine fisso, guardia sul registro ID) + runbook in `docs/DATABASE_EXPANSION_INCREMENTALE.md`. Ritratti: archivio privato e import da file già disponibili per ogni identità; l'automazione sulle nuove identità è sospesa per i termini TMDB non confermati (516 candidati, solo metadati); nessuna immagine non autorizzata distribuita.

## 7. Attività residue
1. Decisione utente sulla deroga D12 per le varianti (2.691 in staging).
2. Seconda fonte gratuita per universi/dimensioni ed eventi (4.123 + 1.391 in staging).
3. Rilancio `db-w5c` per i 305 personaggi di relazioni Comic Vine mancanti; ulteriore verifica documentale delle relazioni (7.359 «da verificare»).
4. Ritratti nuove identità: import privato o conferma dei termini TMDB.
5. Collaudo reale su iPhone/iPad (nessun collaudo manuale richiesto in questa fase).
6. Anomalia nota: alcune voci di ondate precedenti di tipo «entità cosmica» sono personaggi (es. Doctor Doom, Mephisto): la classificazione è dichiarata come editoriale; riclassificazione da decidere.
