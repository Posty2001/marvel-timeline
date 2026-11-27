# Database Expansion – W1 «Espansione MCU» (27–28/11/2026) — REPORT

Stato: **pipeline e integrazione consegnate e collaudate su fixture; contenuti reali NON ancora aggiunti** (la raccolta richiede la rete: va eseguita una volta in GitHub Actions). Non dichiarata completata. Build TEST `20261128-0100-db1`. 0 €, produzione congelata.

## 1. Correzioni al censimento (richieste dell'utente)
| Problema | Causa | Correzione |
|---|---|---|
| Q1235940 = Kilmogue Portal Tomb | QID scritto a mano e mai verificato | nessun QID a mano: si risolvono per **etichetta esatta** (`Marvel Cinematic Universe`) e il censimento stampa i candidati per la verifica umana |
| Query Wikidata: solo 9 elementi / 5 personaggi | QID universo errato (Q931597) e classe troppo stretta | elenco **di tutti gli universi con «Marvel» nell'etichetta** con conteggio P1080; personaggi per P1080 e per editore (P123); MCU per classe P31; sottoclassi incluse |
| `titoli_timeline` = 49 | contava le voci d'indice di tipo «titolo» (titoli con scheda Atlas) | ora `titoli_timeline_numerata` = **138** (da `altTimelineData`, la Timeline numerata) e `titoli_con_voce_atlas` = 49, separati |
| Relazioni mescolate | 1.277 = somma di classi diverse | `relazioni_per_classe`: **narrativa 245, editoriale 1.027, controparte 5, co-apparizione 0** (per regola mai nel registro); narrative per verifica: 207 verificate, 34 da verificare, 4 guida |
Dati dell'esecuzione dell'utente (19 s): 104 film e 39 serie Marvel Studios, 20 serie Marvel Animation (TMDB), 1.197 elementi MCU (Wikidata) — usati solo come ordine di grandezza; nessun metadato TMDB archiviato.

## 2. Pipeline W1 (tutto in repository, riproducibile)
1. **Raccolta** `tools/db_w1_harvest.py` (modalità `db_w1` di «TMDB sync (manuale)», ref `test/tva-archives`): SPARQL leggero per i QID di 4 gruppi (universo MCU P1080; opere MCU via franchise/parte-di; interpreti = cast delle opere MCU; creatori = regia/sceneggiatura/creatori dei personaggi MCU) → `wbgetentities` a blocchi (etichette/alias/descrizioni en+it, sitelink, dichiarazioni). Solo **Wikidata CC0**, User-Agent dichiarato, pause. Scrive **solo sul branch dati `db-raw`** (mai `main`, mai il branch TEST). Nessun Secret.
2. **Costruzione offline** `tools/db_w1_build.py`: classifica per classe P31 → risolve contro le 452 voci storiche → valida (D12) → `canon/w1_mcu.jsonl` (Livello C, verificate), `canon/w1_arricchimenti.jsonl`, `staging/w1_staging.jsonl`, `review/w1_coda.json`, registro ID append-only aggiornato, indice runtime a shard `atlante2/data/db/`.
3. **Regole anti-duplicazione e anti-invenzione**: nome/alias esatto → *arricchimento* della voce storica (ID invariato, aggiunge alias/interpreti, mai riscrittura); corrispondenza parziale/multipla → **coda di revisione e voce trattenuta** (mai importata); omonimi con QID diversi **mai fusi** (ID con suffisso QID); nuova voce → **verificata solo con dichiarazione Wikidata + articolo Wikipedia indipendente** (D12), altrimenti staging; episodi e classi non riconosciute fuori dal runtime; nessun testo narrativo (descrizione breve Wikidata CC0 + campi strutturati); mai co-apparizioni come relazioni.
4. **Categorie coperte**: personaggi, entità cosmiche, organizzazioni, artefatti/armi, luoghi, pianeti, universi/dimensioni, specie, civiltà, eventi, battaglie, **opere** (film/serie MCU), **interpreti**, **creatori**.

## 3. Integrazione con TVA Atlas
- **Ricerca globale**: nuovo modulo lazy `atlante2/db.js` (non caricato né scaricato finché non si cerca); ricerca per alias, nome italiano e originale, nomi parziali/infissi, accenti/maiuscole, interpreti. Gruppo «Archivio esteso» sotto i risultati storici; un alias di una voce storica apre la **scheda storica esistente**.
- **Scheda essenziale (Livello C)** `v:'dbx'`: tipo, nome, nome italiano, descrizione breve, alias, interpreti, continuità (link all'hub/universo esistente), fonti con licenza; dichiara che il dossier approfondito arriverà dopo.
- **Invariati**: ID storici, continuità, ritratti privati, XP, badge, preferiti, raccolte, Multiverso, Nexus (nessuna relazione nuova senza verifica D12: le relazioni narrative restano a W6), Miss Minutes (D14: integrazione dei nuovi dati nell'archivio consultabile rimandata a W7, motore/gateway/interfaccia/quote intoccati). Banner/ID di build: solo `20261128-0100-db1`.
- Scala: indice runtime = trigrammi a 16 shard + chunk da 500 record (prototipo W0: 1,14 MB gz a 50.000 record).

## 4. Verifiche automatiche
`tests/db_w1_test.py` 13/13 (idempotenza ID, nessuna collisione con gli ID storici, omonimi non fusi, solo Livello C verificato, staging/coda corretti, ricerca JS); `tests/db_ui_test.py` 10/10 (lazy, omonimi, scheda, link sicuri, alias→scheda esistente, ricerca storica invariata, nessun overflow, nessun errore JS); `tests/db_test.py` (W0 + W1); regressioni Atlas v. roadmap. Le fixture sono **sintetiche e non finiscono nel runtime**.

## 5. Contenuti aggiunti: **0 reali, in attesa della raccolta**
Il sandbox non raggiunge Wikidata. Conteggi reali per tipo, arricchimenti, staging e coda verranno prodotti da `python3 tools/db_w1_build.py <raw> --scrivi` subito dopo la raccolta e riportati qui. Atteso (ordine di grandezza, non verificato): ~1.200 elementi MCU + opere + interpreti/creatori, di cui solo una parte promossa.

## 6. Azione richiesta (una sola)
Actions → **TMDB sync (manuale)** → Run workflow, ref `test/tva-archives`, spunta **`db_w1`** (l'altra casella `db_censimento` spenta). Esito atteso: artifact `db-w1` + branch `db-raw` con `w1_wikidata.json`. Poi scrivimi «raccolta fatta»: costruisco canon, indice, test e report con i numeri reali.
